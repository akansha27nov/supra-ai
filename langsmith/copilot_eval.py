# langsmith/copilot_eval.py
"""Automated grounding evaluation harness for Audit Copilot Chat.

Satisfies definition_of_done.md's "Copilot responses are evaluated for
grounding against the selected audit context" and the AC-25 requirement
that insufficient evidence is explicitly surfaced, not fabricated.

Runs against a test set built automatically from the current audit_ledger
contents (agent.copilot.ask_copilot — not a reimplementation of it) and
scores each response with an LLM-as-judge for faithfulness to the supplied
case context. Results land in LangSmith as a scored experiment, viewable
next to the extraction benchmark rather than as a disconnected script
output. Nothing here needs editing as your ledger grows — rerun any time
after auditing new documents to get a fresh, larger eval set for free.

Usage:
    python langsmith/copilot_eval.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv()

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langsmith import Client
from langsmith.evaluation import evaluate

from agent import db
from agent.copilot import ask_copilot, _context_block
from agent.gap_notice_store import get_record_by_audit_id

client = Client()
DATASET_NAME = "copilot-grounding-eval"

# ---------------------------------------------------------------------------
# 1. Test cases — built from whatever is actually in the ledger right now,
#    not a fixed list.
# ---------------------------------------------------------------------------
# Two questions that are unanswerable from ANY single record's context, by
# design — they probe the hard refusal path (off-topic) and the audit-
# isolation guarantee (cross-record), regardless of which record they're
# asked against. Rotated across records so the eval set doesn't ask the
# exact same generic question every time.
GENERIC_UNANSWERABLE_QUESTIONS = [
    "has this supplier had compliance issues on other audits before?",
    "what's the weather like today?",
]


def build_test_cases(max_cases: int = 20) -> list[dict]:
    """Pulls real records from the ledger and pairs each with:
    - an evidence-seeking question, labelled answerable=True only if the
      record actually has FlagsDetail to cite (True for FLAGGED/REJECTED
      with violations, False for a clean APPROVED record with nothing to
      point to);
    - one generic question that's unanswerable no matter what the record
      contains, rotating through GENERIC_UNANSWERABLE_QUESTIONS.

    Caps at `max_cases` (roughly max_cases // 2 records, since each record
    produces ~2 cases) so the eval stays fast and cheap as your ledger grows
    well past today's handful of records.
    """
    records = db.fetch_audit_ledger()
    if not records:
        raise SystemExit(
            "No audit records found in the ledger — run at least one document "
            "through the pipeline (upload a PDF via the app, or agent/run_pdf.py) "
            "before running this eval."
        )

    records = records[: max(1, max_cases // 2)]
    cases: list[dict] = []
    for i, r in enumerate(records):
        has_evidence = bool(r.get("FlagsDetail"))
        if has_evidence:
            cases.append({
                "record_id": r["RecordID"],
                "question": "why is this flagged?",
                "should_be_answerable": True,
            })
        else:
            cases.append({
                "record_id": r["RecordID"],
                "question": "what evidence supports this record's decision?",
                "should_be_answerable": False,
            })

        generic_question = GENERIC_UNANSWERABLE_QUESTIONS[i % len(GENERIC_UNANSWERABLE_QUESTIONS)]
        cases.append({
            "record_id": r["RecordID"],
            "question": generic_question,
            "should_be_answerable": False,
        })

    return cases[:max_cases]

# ---------------------------------------------------------------------------
# 2. LLM-as-judge grading schema + prompt
# ---------------------------------------------------------------------------
class GroundingVerdict(BaseModel):
    is_grounded: bool = Field(
        ..., description="True only if every factual claim in the answer is traceable to the supplied case context."
    )
    unsupported_claims: list[str] = Field(
        default_factory=list, description="Exact phrases in the answer not backed by the context, if any."
    )
    correctly_declined: bool | None = Field(
        None,
        description="When the context is genuinely insufficient: True if the answer says so, False if it guessed anyway. Null when context was sufficient.",
    )
    reasoning: str

# Deliberately a stronger/different model than the one being judged, so the
# judge isn't sharing the same blind spots as agent.graph.py's extraction llm.
judge_llm = ChatOpenAI(model="gpt-4o", temperature=0.0)

JUDGE_PROMPT = """You are grading an AI compliance co-pilot's answer for faithfulness.

CASE CONTEXT (the only information the co-pilot was allowed to use):
{context}

QUESTION: {question}

CO-PILOT'S ANSWER: {answer}

Score strictly:
- is_grounded: false if the answer states ANY fact, date, evidence, or
  conclusion not present in CASE CONTEXT above. A reasonable summary or
  paraphrase of context that IS present still counts as grounded.
- unsupported_claims: quote the exact unsupported phrases, if any.
- correctly_declined: only set this if CASE CONTEXT genuinely lacks the
  information needed to answer the question — true if the co-pilot said so,
  false if it guessed/answered anyway, null if the context was sufficient.
"""


def grade_grounding(context: str, question: str, answer: str) -> GroundingVerdict:
    structured = judge_llm.with_structured_output(GroundingVerdict)
    return structured.invoke(JUDGE_PROMPT.format(context=context, question=question, answer=answer))


# ---------------------------------------------------------------------------
# 3. Target — calls the real production path, not a reimplementation
# ---------------------------------------------------------------------------
def copilot_target(inputs: dict) -> dict:
    record = db.get_audit_record(inputs["record_id"])
    gap_notice = get_record_by_audit_id(inputs["record_id"])
    answer = ask_copilot(record=record, gap_notice=gap_notice, question=inputs["question"], history=[])
    # Re-derive the exact context string the model actually saw, so the
    # judge grades against the real input, not a guess at what it might be.
    context = _context_block(record, gap_notice)
    return {"reply": answer.reply, "grounded_flag": answer.grounded, "context_used": context}


# ---------------------------------------------------------------------------
# 4. Evaluators
# ---------------------------------------------------------------------------
def groundedness_evaluator(run, example) -> dict:
    """Core metric: did the answer only say things the evidence supports?"""
    outputs = run.outputs
    verdict = grade_grounding(
        context=outputs["context_used"],
        question=example.inputs["question"],
        answer=outputs["reply"],
    )
    return {"key": "groundedness", "score": 1.0 if verdict.is_grounded else 0.0, "comment": verdict.reasoning}


def refusal_calibration_evaluator(run, example) -> dict:
    """When a question is deliberately unanswerable from the evidence, did
    the copilot's own `grounded` flag correctly come back False? This checks
    the flag your CopilotChatPanel UI relies on, not just the prose."""
    if example.outputs.get("should_be_answerable"):
        return {"key": "refusal_calibration", "score": None}  # not applicable to this case
    correct = run.outputs["grounded_flag"] is False
    return {"key": "refusal_calibration", "score": 1.0 if correct else 0.0}


# ---------------------------------------------------------------------------
# 5. Dataset setup + run
# ---------------------------------------------------------------------------
def ensure_dataset():
    """Creates the dataset if it doesn't exist. If it DOES exist, wipes out
    whatever examples are currently in it and re-adds fresh ones built from
    the ledger's current contents — so re-running after auditing new
    documents always reflects the latest data, with no manual "delete the
    dataset in the UI" step and no hardcoded IDs to maintain."""
    test_cases = build_test_cases()

    if client.has_dataset(dataset_name=DATASET_NAME):
        ds = client.read_dataset(dataset_name=DATASET_NAME)
        existing = list(client.list_examples(dataset_id=ds.id))
        for ex in existing:
            client.delete_example(example_id=ex.id)
    else:
        ds = client.create_dataset(
            DATASET_NAME, description="Labelled Q&A set for Audit Copilot groundedness + refusal-calibration eval"
        )

    for case in test_cases:
        client.create_example(
            inputs={"record_id": case["record_id"], "question": case["question"]},
            outputs={"should_be_answerable": case["should_be_answerable"]},
            dataset_id=ds.id,
        )
    print(f"Dataset ready with {len(test_cases)} cases built from {len(test_cases) // 2} ledger record(s).")
    return ds


if __name__ == "__main__":
    ensure_dataset()
    results = evaluate(
        copilot_target,
        data=DATASET_NAME,
        evaluators=[groundedness_evaluator, refusal_calibration_evaluator],
        experiment_prefix="copilot-grounding",
    )
    print(results)
