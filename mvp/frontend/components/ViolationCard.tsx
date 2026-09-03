"use client";

import { useState } from 'react';
import { Quote, Hash, BookOpen } from 'lucide-react';
import { RuleViolationDetail } from '@/lib/api';

/**
 * Renders one rule violation as a card, with an expandable evidence block
 * (exact quote, page, section) when evidence was recorded for it. Shared
 * between the audit detail page and the "Run Compliance Audit" upload
 * modal — both display the same RuleViolationDetail[] shape and should
 * not diverge into two separately-maintained renderings (one used to be a
 * raw JSON.stringify dump; this replaces that).
 *
 * showEvidence (default true) controls whether the expand/"Show evidence"
 * affordance renders at all. The upload modal is a fast post-upload
 * summary, not a review workspace, so it passes showEvidence={false} to
 * render a plain static card — full evidence drill-down stays exclusive
 * to the audit detail page, where a reviewer is actually investigating.
 */
export default function ViolationCard({
  violation,
  showEvidence = true,
}: {
  violation: RuleViolationDetail;
  showEvidence?: boolean;
}) {
  const [expanded, setExpanded] = useState(false);
  const hasEvidence = showEvidence && Boolean(violation.evidence?.exact_quote);

  const severityStyle =
    violation.severity_score >= 75
      ? 'bg-error/10 text-error'
      : violation.severity_score >= 50
      ? 'bg-amber-100 text-amber-800'
      : 'bg-surface-container-highest text-on-surface-variant';

  return (
    <div className="bg-surface-container-lowest rounded-lg border border-outline-variant overflow-hidden">
      <button
        type="button"
        onClick={() => hasEvidence && setExpanded((prev) => !prev)}
        disabled={!hasEvidence}
        className={`w-full flex items-start justify-between gap-3 p-3 text-left ${hasEvidence ? 'cursor-pointer hover:bg-surface-container' : 'cursor-default'}`}
      >
        <div className="flex flex-col gap-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-mono text-xs font-semibold text-on-surface">{violation.code}</span>
            <span className={`px-2 py-0.5 rounded text-xs font-bold ${severityStyle}`}>
              {violation.severity_score}
            </span>
          </div>
          <span className="text-sm text-on-surface-variant leading-snug">{violation.message}</span>
        </div>
        {hasEvidence && (
          <span className="text-xs text-primary font-medium whitespace-nowrap pt-0.5">
            {expanded ? 'Hide evidence' : 'Show evidence'}
          </span>
        )}
      </button>

      {expanded && hasEvidence && (
        <div className="px-3 pb-3 flex flex-col gap-2 border-t border-outline-variant pt-3 bg-surface-container/40">
          <div className="flex items-start gap-2">
            <Quote size={14} className="text-primary mt-0.5 flex-shrink-0" />
            <p className="text-sm text-on-surface italic leading-relaxed">
              "{violation.evidence!.exact_quote}"
            </p>
          </div>
          <div className="flex items-center gap-4 text-xs text-on-surface-variant pl-6">
            {violation.evidence!.page_number != null && (
              <span className="flex items-center gap-1">
                <Hash size={12} /> Page {violation.evidence!.page_number}
              </span>
            )}
            {violation.evidence!.section && (
              <span className="flex items-center gap-1">
                <BookOpen size={12} /> {violation.evidence!.section}
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
