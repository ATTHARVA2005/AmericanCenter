const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export type LoanApplicationInput = {
  applicant_name: string;
  applicant_email: string;
  state_code: string;
  applicant_age: number;
  annual_income: number;
  monthly_debt_payments: number;
  loan_amount: number;
  property_value: number;
  loan_term_months: number;
  loan_purpose: string;
  loan_type: string;
  occupancy_type: string;
  dwelling_type: string;
  construction_method: string;
  total_units: number;
};

export type FeatureContribution = {
  feature: string;
  value: string;
  impact: number;
  direction: "increases" | "decreases";
};

export type LenderOffer = {
  lender_id: string;
  lender_name: string;
  offered_interest_rate: number;
  lender_confidence: number;
  processing_tier: string;
  est_monthly_payment_360m: number;
  marketplace_commission_bps: number;
};

export type CreditReport = {
  bureau: string;
  score: number;
  score_range: string;
  hard_inquiries_last_12mo: number;
  open_tradelines: number;
  revolving_utilization_pct: number;
  factors: string[];
  pulled_via: string;
};

export type FraudScreeningResult = {
  transactions_screened: number;
  max_fraud_probability: number;
  flagged_count: number;
  mean_fraud_probability: number;
  risk_level: "low" | "medium" | "high";
};

export type LoanApplicationResponse = {
  application_id: string;
  approved: boolean;
  approval_probability: number;
  approval_explanation: FeatureContribution[];
  predicted_base_interest_rate: number;
  interest_rate_explanation: FeatureContribution[];
  credit_report: CreditReport;
  ai_intelligence_layer: {
    fraud_detection: FraudScreeningResult;
    loan_approval: { approved: boolean; approval_probability: number };
    interest_rate_prediction: { predicted_base_interest_rate: number };
    recommendation_system: LenderOffer[];
    bias_fairness_check: { note: string; flags: string[] };
  };
  offers: LenderOffer[];
};

export type BiasGroupRow = {
  group: string;
  selection_rate: number;
  accuracy: number;
  false_negative_rate: number;
  n: number;
};

export type BiasAudit = {
  attribute: string;
  demographic_parity_difference: number;
  equalized_odds_difference: number;
  overall_selection_rate: number;
  overall_accuracy: number;
  by_group: BiasGroupRow[];
  flag: "ok" | "review";
};

export type BiasReport = {
  n_test_samples: number;
  audits: BiasAudit[];
};

export type RecentApplication = {
  id: string;
  created_at: string;
  applicant_name: string;
  state_code: string;
  loan_amount: number;
  approved: number;
  approval_probability: number;
  predicted_base_interest_rate: number;
  fraud_risk_level: string;
  bureau: string;
  credit_score: number;
  offers_count: number;
};

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${body}`);
  }
  return res.json();
}

export function submitLoanApplication(input: LoanApplicationInput) {
  return request<LoanApplicationResponse>("/api/loans/apply", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function fetchBiasReport() {
  return request<BiasReport>("/api/bias/report");
}

export function fetchRecentApplications() {
  return request<RecentApplication[]>("/api/loans/recent");
}

export function fetchHealth() {
  return request<{ status: string; models: Record<string, Record<string, number>> }>("/api/health");
}
