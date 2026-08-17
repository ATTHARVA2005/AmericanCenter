import type { LoanApplicationResponse } from "@/lib/api";
import AIIntelligenceLayer from "@/components/AIIntelligenceLayer";
import CreditReportCard from "@/components/CreditReportCard";
import OffersList from "@/components/OffersList";
import ShapChart from "@/components/ShapChart";

export default function ResultPanel({ result }: { result: LoanApplicationResponse }) {
  return (
    <div className="flex flex-col gap-6">
      <AIIntelligenceLayer result={result} />

      <CreditReportCard report={result.credit_report} />

      <div>
        <h3 className="text-sm font-semibold mb-3" style={{ color: "var(--text-secondary)" }}>
          Ranked lender offers
        </h3>
        <OffersList offers={result.offers} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-5">
          <h3 className="font-semibold mb-1">Why this approval decision</h3>
          <p className="text-xs mb-3" style={{ color: "var(--text-muted)" }}>
            Top SHAP feature contributions to the approval-probability model
          </p>
          <ShapChart
            data={result.approval_explanation}
            positiveLabel="Increases approval likelihood"
            negativeLabel="Decreases approval likelihood"
          />
        </div>
        <div className="card p-5">
          <h3 className="font-semibold mb-1">Why this interest rate</h3>
          <p className="text-xs mb-3" style={{ color: "var(--text-muted)" }}>
            Top SHAP feature contributions to the base interest-rate model
          </p>
          <ShapChart
            data={result.interest_rate_explanation}
            positiveLabel="Increases predicted rate"
            negativeLabel="Decreases predicted rate"
          />
        </div>
      </div>
    </div>
  );
}
