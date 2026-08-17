"use client";

import type { LoanApplicationResponse } from "@/lib/api";

function riskColor(level: string) {
  if (level === "high") return "var(--status-critical)";
  if (level === "medium") return "var(--status-warning)";
  return "var(--status-good)";
}

function Module({
  index,
  title,
  headline,
  detail,
  accent,
}: {
  index: number;
  title: string;
  headline: React.ReactNode;
  detail: string;
  accent?: string;
}) {
  return (
    <div className="card p-4 flex flex-col gap-2 min-w-0">
      <div className="flex items-center gap-2 text-xs" style={{ color: "var(--text-muted)" }}>
        <span
          className="w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-semibold text-white"
          style={{ background: "var(--series-1)" }}
        >
          {index}
        </span>
        {title}
      </div>
      <div className="text-xl font-semibold" style={{ color: accent }}>
        {headline}
      </div>
      <div className="text-xs" style={{ color: "var(--text-secondary)" }}>
        {detail}
      </div>
    </div>
  );
}

export default function AIIntelligenceLayer({ result }: { result: LoanApplicationResponse }) {
  const layer = result.ai_intelligence_layer;
  const fraud = layer.fraud_detection;
  const bias = layer.bias_fairness_check;

  return (
    <div>
      <h3 className="text-sm font-semibold mb-3" style={{ color: "var(--text-secondary)" }}>
        AI Intelligence Layer
      </h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        <Module
          index={1}
          title="Fraud Detection"
          headline={fraud.risk_level.toUpperCase()}
          accent={riskColor(fraud.risk_level)}
          detail={`${fraud.transactions_screened} linked transactions screened, ${fraud.flagged_count} flagged (max score ${fraud.max_fraud_probability.toFixed(3)})`}
        />
        <Module
          index={2}
          title="Loan Approval"
          headline={`${(result.approval_probability * 100).toFixed(1)}%`}
          accent={result.approved ? "var(--status-good)" : "var(--status-critical)"}
          detail={result.approved ? "Predicted approval" : "Predicted denial"}
        />
        <Module
          index={3}
          title="Interest Rate Prediction"
          headline={`${result.predicted_base_interest_rate.toFixed(2)}%`}
          detail="Market base rate before lender-specific pricing"
        />
        <Module
          index={4}
          title="Recommendation System"
          headline={`${result.offers.length} lender${result.offers.length === 1 ? "" : "s"}`}
          detail={
            result.offers.length
              ? `Best offer: ${result.offers[0].lender_name} at ${result.offers[0].offered_interest_rate}%`
              : "No lenders in panel clear this applicant's risk profile"
          }
        />
        <Module
          index={5}
          title="Bias / Fairness Check"
          headline={bias.flags.length ? `${bias.flags.length} flagged` : "Clear"}
          accent={bias.flags.length ? "var(--status-warning)" : "var(--status-good)"}
          detail={
            bias.flags.length
              ? `Model-level disparity review needed on: ${bias.flags.join(", ")}`
              : "No demographic-parity disparities above threshold"
          }
        />
      </div>
    </div>
  );
}
