"use client";

import { memo, useCallback } from "react";

export type OppStage =
  | "QUALIFICATION"
  | "TECHNICAL_EVAL"
  | "BUDGET_VALIDATION"
  | "PROPOSAL"
  | "QUOTATION_ISSUED"
  | "NEGOTIATION"
  | "CLOSED_WON"
  | "CLOSED_LOST";

export interface OpportunityMobileCardProps {
  id: string;
  companyName: string;
  dealName?: string;
  value: number;
  currencyCode?: string;
  stage: OppStage;
  onOpen?: (id: string) => void;
  onAdvance?: (id: string) => void;
}

const STAGE_PILL: Record<OppStage, string> = {
  QUALIFICATION: "bg-blue-100 text-blue-800",
  TECHNICAL_EVAL: "bg-blue-100 text-blue-800",
  BUDGET_VALIDATION: "bg-yellow-100 text-yellow-900",
  PROPOSAL: "bg-yellow-100 text-yellow-900",
  QUOTATION_ISSUED: "bg-yellow-100 text-yellow-900",
  NEGOTIATION: "bg-green-100 text-green-900",
  CLOSED_WON: "bg-green-600 text-white",
  CLOSED_LOST: "bg-red-600 text-white",
};

const fmt = (v: number, c = "INR") =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: c,
    maximumFractionDigits: 0,
  }).format(v);

const lbl = (s: string) => s.replaceAll("_", " ");

export const OpportunityMobileCard = memo(function OpportunityMobileCard({
  id,
  companyName,
  dealName,
  value,
  currencyCode = "INR",
  stage,
  onOpen,
  onAdvance,
}: OpportunityMobileCardProps) {
  const open = useCallback(() => onOpen?.(id), [id, onOpen]);
  const advance = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      onAdvance?.(id);
    },
    [id, onAdvance]
  );

  return (
    <article
      onClick={open}
      className="max-w-[640px] rounded-xl border border-slate-200 bg-white p-3 shadow-sm active:scale-[0.99]"
      role="button"
      tabIndex={0}
      onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && open()}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold text-slate-900">{companyName}</p>
          {dealName && <p className="truncate text-xs text-slate-500">{dealName}</p>}
        </div>
        <span
          className={`shrink-0 rounded-full px-2 py-1 text-[10px] font-bold uppercase ${STAGE_PILL[stage]}`}
        >
          {lbl(stage)}
        </span>
      </div>

      <p className="mt-2 text-lg font-bold leading-none text-slate-900">
        {fmt(value, currencyCode)}
      </p>

      <div className="mt-3 grid grid-cols-2 gap-2">
        <button
          type="button"
          onClick={open}
          className="min-h-11 rounded-lg border border-slate-200 px-3 text-sm font-medium text-slate-800"
        >
          Open
        </button>
        {onAdvance && (
          <button
            type="button"
            onClick={advance}
            className="min-h-11 rounded-lg bg-slate-900 px-3 text-sm font-medium text-white"
          >
            Advance
          </button>
        )}
      </div>
    </article>
  );
});
