# agent/copilot.py
from __future__ import annotations
from typing import Any
from pydantic import BaseModel
from agent.graph import llm  
from agent.llm_reliability import invoke_with_retry

class CopilotAnswer(BaseModel):
    reply: str
    grounded: bool  # False when the model had to go outside the supplied evidence


SYSTEM_PROMPT = """You are a compliance co-pilot helping a reviewer understand ONE flagged audit record.

Rules:
- Answer only from the CASE CONTEXT below. No outside knowledge of regulations or suppliers.
- If the question isn't answerable from CASE CONTEXT, set grounded=false and say the evidence isn't in this record.
- You never make or change the compliance decision — only describe what the rule engine found.
  Never say a case is "approved," "compliant," or "fine."
- Quote evidence.exact_quote when citing findings; don't invent new findings.
"""


def _context_block(record: dict[str, Any], gap_notice: dict[str, Any] | None) -> str:
    lines = [
        f"File: {record.get('File Name')}  Supplier: {record.get('Supplier')}",
        f"SKU: {record.get('SKU')} ({record.get('SKU Match Status')})",
        f"Decision: {record.get('Decision')}  Score: {record.get('Score')}",
        "", "Rule violations:",
    ]
    for f in record.get("FlagsDetail") or []:
        lines.append(f"  - [{f.get('code')}] severity={f.get('severity_score')}: {f.get('message')}")
        ev = f.get("evidence")
        if ev:
            lines.append(f'      evidence: "{ev.get("exact_quote")}" (p.{ev.get("page_number")}, {ev.get("section")})')
    if gap_notice:
        lines += [
            "", "Gap notice on file:",
            f"  Status: {gap_notice.get('status')}",
            f"  Failed rules: {', '.join(gap_notice.get('failed_rules', []))}",
            f"  Corrective action: {gap_notice.get('corrective_action')}",
        ]
    return "\n".join(lines)


def ask_copilot(record, gap_notice, question, history) -> CopilotAnswer:
    context = _context_block(record, gap_notice)
    messages = [{"role": "system", "content": SYSTEM_PROMPT + "\n\nCASE CONTEXT:\n" + context}]
    messages += history
    messages.append({"role": "user", "content": question})

    structured_llm = llm.with_structured_output(CopilotAnswer)
    return invoke_with_retry(
        lambda: structured_llm.invoke(
            messages,
            config={"tags": ["copilot_chat"], "metadata": {"record_id": record.get("RecordID")}},
        ),
        step="copilot_chat",
    )