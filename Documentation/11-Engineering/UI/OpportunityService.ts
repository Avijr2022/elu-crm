import type { OppStage } from "./OpportunityMobileCard";

export type OpportunityStatus =
  | "OPEN"
  | "ON_HOLD"
  | "CLOSED_WON"
  | "CLOSED_LOST"
  | "REOPENED";

export interface OpportunityRecord {
  opportunity_id: string;
  tenant_id: string;
  opportunity_number: string;
  name: string;
  company_name: string | null;
  stage: OppStage;
  status: OpportunityStatus;
  opportunity_value: number;
  currency_code: string;
  probability: number;
  expected_close_date: string | null;
  source_lead_id: string | null;
  owner_id: string | null;
  loss_reason: string | null;
  notes: string | null;
  created_on: string;
  modified_on: string | null;
  weighted_value: number;
}

export interface OpportunityListResult {
  items: OpportunityRecord[];
  total: number;
  page: number;
  page_size: number;
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";
const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK_OPPORTUNITIES === "true";

const PIPELINE: OppStage[] = [
  "QUALIFICATION",
  "TECHNICAL_EVAL",
  "BUDGET_VALIDATION",
  "PROPOSAL",
  "QUOTATION_ISSUED",
  "NEGOTIATION",
];

const STAGE_PROBABILITY: Record<string, number> = {
  QUALIFICATION: 10,
  TECHNICAL_EVAL: 25,
  BUDGET_VALIDATION: 40,
  PROPOSAL: 60,
  QUOTATION_ISSUED: 75,
  NEGOTIATION: 90,
};

const MOCK_OPPORTUNITIES: OpportunityRecord[] = [
  {
    opportunity_id: "a1111111-1111-1111-1111-111111111101",
    tenant_id: "t1111111-1111-1111-1111-111111111111",
    opportunity_number: "EUP-OPP-2026-0042",
    name: "Acme ERP Rollout",
    company_name: "Acme Manufacturing",
    stage: "QUALIFICATION",
    status: "OPEN",
    opportunity_value: 1800000,
    currency_code: "INR",
    probability: 10,
    expected_close_date: "2026-09-30",
    source_lead_id: "b1111111-1111-1111-1111-111111111101",
    owner_id: "u1111111-1111-1111-1111-111111111101",
    loss_reason: null,
    notes: "Inbound from qualified lead.",
    created_on: "2026-08-01T10:00:00Z",
    modified_on: "2026-08-15T12:00:00Z",
    weighted_value: 180000,
  },
  {
    opportunity_id: "a1111111-1111-1111-1111-111111111102",
    tenant_id: "t1111111-1111-1111-1111-111111111111",
    opportunity_number: "EUP-OPP-2026-0043",
    name: "Zenith Cloud Migration",
    company_name: "Zenith Logistics",
    stage: "PROPOSAL",
    status: "OPEN",
    opportunity_value: 950000,
    currency_code: "INR",
    probability: 60,
    expected_close_date: "2026-10-15",
    source_lead_id: null,
    owner_id: "u1111111-1111-1111-1111-111111111102",
    loss_reason: null,
    notes: "Proposal shared with procurement.",
    created_on: "2026-07-20T09:30:00Z",
    modified_on: "2026-08-10T16:45:00Z",
    weighted_value: 570000,
  },
  {
    opportunity_id: "a1111111-1111-1111-1111-111111111103",
    tenant_id: "t2222222-2222-2222-2222-222222222222",
    opportunity_number: "EUP-OPP-2026-0044",
    name: "Nova Retail POS",
    company_name: "Nova Retail",
    stage: "NEGOTIATION",
    status: "OPEN",
    opportunity_value: 420000,
    currency_code: "INR",
    probability: 90,
    expected_close_date: "2026-08-28",
    source_lead_id: "b2222222-2222-2222-2222-222222222222",
    owner_id: "u2222222-2222-2222-2222-222222222222",
    loss_reason: null,
    notes: "Final commercial terms under review.",
    created_on: "2026-06-05T11:00:00Z",
    modified_on: "2026-08-18T08:20:00Z",
    weighted_value: 378000,
  },
];

function authHeaders(): HeadersInit {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
  return {
    Accept: "application/json",
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

function nextStage(current: string): OppStage | null {
  const idx = PIPELINE.indexOf(current as OppStage);
  if (idx < 0 || idx >= PIPELINE.length - 1) return null;
  return PIPELINE[idx + 1];
}

function mockList(tenantId: string): OpportunityListResult {
  const items = MOCK_OPPORTUNITIES.filter((o) => o.tenant_id === tenantId);
  return { items, total: items.length, page: 1, page_size: 25 };
}

function mockAdvance(id: string, currentStage: string): OpportunityRecord {
  const row = MOCK_OPPORTUNITIES.find((o) => o.opportunity_id === id);
  if (!row) throw new Error("Opportunity not found");
  const target = nextStage(currentStage);
  if (!target) throw new Error("Cannot advance stage");
  const probability = STAGE_PROBABILITY[target] ?? row.probability;
  const weighted = (row.opportunity_value * probability) / 100;
  return {
    ...row,
    stage: target,
    probability,
    weighted_value: weighted,
    modified_on: new Date().toISOString(),
  };
}

export async function fetchOpportunities(
  tenantId: string
): Promise<OpportunityListResult> {
  if (USE_MOCK) return mockList(tenantId);

  try {
    const res = await fetch(`${API_BASE}/api/v1/crm/opportunities?page=1&page_size=100`, {
      method: "GET",
      headers: authHeaders(),
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = (await res.json()) as OpportunityListResult;
    return {
      ...data,
      items: data.items.filter((o) => o.tenant_id === tenantId),
      total: data.items.filter((o) => o.tenant_id === tenantId).length,
    };
  } catch {
    return mockList(tenantId);
  }
}

export async function advanceOpportunityStage(
  id: string,
  currentStage: string
): Promise<OpportunityRecord> {
  if (USE_MOCK) return mockAdvance(id, currentStage);

  try {
    const res = await fetch(`${API_BASE}/api/v1/crm/opportunities/advance`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ opportunity_id: id, current_stage: currentStage }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return (await res.json()) as OpportunityRecord;
  } catch {
    const target = nextStage(currentStage);
    if (!target) throw new Error("Cannot advance stage");
    const patch = await fetch(`${API_BASE}/api/v1/crm/opportunities/${id}/stage`, {
      method: "PATCH",
      headers: authHeaders(),
      body: JSON.stringify({ stage: target }),
    });
    if (!patch.ok) return mockAdvance(id, currentStage);
    return (await patch.json()) as OpportunityRecord;
  }
}
