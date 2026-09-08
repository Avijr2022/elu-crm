"use client";

import { useMemo, useState } from "react";
import type { OppStage } from "./OpportunityMobileCard";

export type OpportunityStatus =
  | "OPEN"
  | "ON_HOLD"
  | "CLOSED_WON"
  | "CLOSED_LOST"
  | "REOPENED";

export interface OpportunityDetailModel {
  opportunityId: string;
  opportunityNumber: string;
  clientName: string;
  dealName: string;
  stage: OppStage;
  status: OpportunityStatus;
  dealValue: number;
  currencyCode: string;
  winProbability: number;
  weightedValue: number;
  targetCloseDate?: string | null;
  ownerName?: string | null;
  sourceLeadId?: string | null;
  notes?: string | null;
  lossReason?: string | null;
  createdOn: string;
  modifiedOn?: string | null;
}

export interface ActivityLedgerItem {
  id: string;
  eventType: string;
  title: string;
  detail?: string | null;
  actorName?: string | null;
  occurredAt: string;
}

export interface OpportunityDetailProps {
  opportunity: OpportunityDetailModel;
  activities: readonly ActivityLedgerItem[];
  loading?: boolean;
  error?: string | null;
}

type TabKey = "overview" | "activity";

const PIPELINE: readonly OppStage[] = [
  "QUALIFICATION",
  "TECHNICAL_EVAL",
  "BUDGET_VALIDATION",
  "PROPOSAL",
  "QUOTATION_ISSUED",
  "NEGOTIATION",
  "CLOSED_WON",
] as const;

const STAGE_BADGE: Record<OppStage, string> = {
  QUALIFICATION: "bg-blue-100 text-blue-800",
  TECHNICAL_EVAL: "bg-blue-100 text-blue-800",
  BUDGET_VALIDATION: "bg-yellow-100 text-yellow-900",
  PROPOSAL: "bg-yellow-100 text-yellow-900",
  QUOTATION_ISSUED: "bg-yellow-100 text-yellow-900",
  NEGOTIATION: "bg-green-100 text-green-900",
  CLOSED_WON: "bg-green-600 text-white",
  CLOSED_LOST: "bg-red-600 text-white",
};

const STAGE_BAR: Record<OppStage, string> = {
  QUALIFICATION: "bg-blue-500",
  TECHNICAL_EVAL: "bg-blue-500",
  BUDGET_VALIDATION: "bg-yellow-500",
  PROPOSAL: "bg-yellow-500",
  QUOTATION_ISSUED: "bg-yellow-500",
  NEGOTIATION: "bg-green-500",
  CLOSED_WON: "bg-green-700",
  CLOSED_LOST: "bg-red-600",
};

const fmtMoney = (v: number, c: string) =>
  new Intl.NumberFormat("en-IN", { style: "currency", currency: c }).format(v);

const fmtDate = (iso?: string | null) =>
  iso ? new Date(iso).toLocaleDateString("en-IN", { dateStyle: "medium" }) : "—";

const lbl = (s: string) => s.replaceAll("_", " ");

function stageIndex(stage: OppStage): number {
  const i = PIPELINE.indexOf(stage);
  if (i >= 0) return i;
  if (stage === "CLOSED_LOST") return PIPELINE.length - 1;
  return 0;
}

function PipelineChevron({ current }: { current: OppStage }) {
  const idx = stageIndex(current);
  return (
    <ol className="grid grid-cols-2 gap-2 md:grid-cols-4 xl:grid-cols-7">
      {PIPELINE.map((stage, i) => {
        const done = i <= idx;
        return (
          <li key={stage} className="relative">
            <div
              className={`flex min-h-9 items-center justify-center rounded-md px-2 text-center text-[10px] font-semibold uppercase md:text-xs ${
                done ? `${STAGE_BAR[stage]} text-white` : "bg-slate-200 text-slate-500"
              }`}
            >
              {lbl(stage)}
            </div>
          </li>
        );
      })}
    </ol>
  );
}

function DetailHeader({ opp }: { opp: OpportunityDetailModel }) {
  return (
    <header className="grid gap-3 rounded-xl border border-slate-200 bg-white p-4 md:grid-cols-4">
      <div className="md:col-span-2">
        <p className="text-xs font-semibold uppercase text-slate-500">Client</p>
        <h1 className="text-xl font-bold text-slate-900">{opp.clientName}</h1>
        <p className="text-sm text-slate-500">
          {opp.dealName} · {opp.opportunityNumber}
        </p>
      </div>
      <div>
        <p className="text-xs font-semibold uppercase text-slate-500">Expected Deal Value</p>
        <p className="text-2xl font-bold text-slate-900">{fmtMoney(opp.dealValue, opp.currencyCode)}</p>
        <p className="text-xs text-slate-500">
          Weighted {fmtMoney(opp.weightedValue, opp.currencyCode)} ({opp.winProbability}%)
        </p>
      </div>
      <div className="space-y-2">
        <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-bold uppercase ${STAGE_BADGE[opp.stage]}`}>
          {lbl(opp.stage)}
        </span>
        <div>
          <p className="text-xs font-semibold uppercase text-slate-500">Target Close</p>
          <p className="text-sm font-semibold text-slate-900">{fmtDate(opp.targetCloseDate)}</p>
        </div>
      </div>
    </header>
  );
}

function OverviewTab({ opp }: { opp: OpportunityDetailModel }) {
  const rows: Array<[string, string]> = [
    ["Status", lbl(opp.status)],
    ["Win Probability", `${opp.winProbability}%`],
    ["Owner", opp.ownerName ?? "—"],
    ["Source Lead", opp.sourceLeadId ?? "—"],
    ["Created", fmtDate(opp.createdOn)],
    ["Modified", fmtDate(opp.modifiedOn)],
  ];
  return (
    <div className="space-y-3 rounded-xl border border-slate-200 bg-white p-4">
      <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {rows.map(([k, v]) => (
          <div key={k} className="rounded-lg border border-slate-100 p-3">
            <dt className="text-xs text-slate-500">{k}</dt>
            <dd className="text-sm font-semibold text-slate-900">{v}</dd>
          </div>
        ))}
      </dl>
      <div className="rounded-lg border border-slate-100 p-3">
        <p className="text-xs text-slate-500">Deal Health Notes</p>
        <p className="mt-1 text-sm text-slate-800">{opp.notes?.trim() || "No notes recorded."}</p>
      </div>
      {opp.lossReason && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-3">
          <p className="text-xs font-semibold text-red-700">Loss Reason</p>
          <p className="text-sm text-red-900">{opp.lossReason}</p>
        </div>
      )}
    </div>
  );
}

function ActivityTimelineTab({ items }: { items: readonly ActivityLedgerItem[] }) {
  if (!items.length) {
    return <p className="rounded-xl border border-slate-200 bg-white p-6 text-center text-sm text-slate-500">No audit activity.</p>;
  }
  return (
    <ol className="space-y-4 rounded-xl border border-slate-200 bg-white p-4">
      {items.map((a) => (
        <li key={a.id} className="relative border-l-2 border-slate-200 pl-4">
          <span className="absolute -left-[5px] top-1 h-2 w-2 rounded-full bg-slate-900" />
          <p className="text-xs text-slate-500">
            {fmtDate(a.occurredAt)} · {lbl(a.eventType)}
          </p>
          <p className="text-sm font-semibold text-slate-900">{a.title}</p>
          {a.detail && <p className="text-sm text-slate-600">{a.detail}</p>}
          {a.actorName && <p className="text-xs text-slate-500">By {a.actorName}</p>}
        </li>
      ))}
    </ol>
  );
}

export function OpportunityDetail({
  opportunity,
  activities,
  loading = false,
  error = null,
}: OpportunityDetailProps) {
  const [tab, setTab] = useState<TabKey>("overview");
  const tabs = useMemo(
    () =>
      [
        { key: "overview" as const, label: "Overview" },
        { key: "activity" as const, label: "Activity Timeline" },
      ] as const,
    []
  );

  if (loading) return <div className="h-48 animate-pulse rounded-xl bg-slate-200" />;
  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">{error}</div>
    );
  }

  return (
    <section className="space-y-4">
      <DetailHeader opp={opportunity} />
      <div className="rounded-xl border border-slate-200 bg-white p-4">
        <p className="mb-2 text-xs font-semibold uppercase text-slate-500">Pipeline Progress</p>
        <PipelineChevron current={opportunity.stage} />
      </div>
      <nav className="flex gap-2 border-b border-slate-200">
        {tabs.map((t) => (
          <button
            key={t.key}
            type="button"
            onClick={() => setTab(t.key)}
            className={`min-h-11 px-4 text-sm font-medium ${
              tab === t.key
                ? "border-b-2 border-slate-900 text-slate-900"
                : "text-slate-500 hover:text-slate-700"
            }`}
          >
            {t.label}
          </button>
        ))}
      </nav>
      {tab === "overview" && <OverviewTab opp={opportunity} />}
      {tab === "activity" && <ActivityTimelineTab items={activities} />}
    </section>
  );
}
