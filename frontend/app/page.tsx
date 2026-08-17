"use client";

import { useState } from "react";
import LoanForm from "@/components/LoanForm";
import ResultPanel from "@/components/ResultPanel";
import { submitLoanApplication, type LoanApplicationInput, type LoanApplicationResponse } from "@/lib/api";

export default function Home() {
  const [result, setResult] = useState<LoanApplicationResponse | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(input: LoanApplicationInput) {
    setSubmitting(true);
    setError(null);
    try {
      const response = await submitLoanApplication(input);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex flex-col gap-8">
      {!result && (
        <div className="max-w-2xl">
          <h1 className="text-2xl font-semibold mb-1">AI Marketplace for Personalized Loan Offers</h1>
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
            Submit one application and get fraud screening, an approval prediction, an interest-rate
            estimate, and a ranked panel of lender offers — powered by XGBoost models trained on real
            CFPB/HMDA mortgage data and ULB/Worldline transaction data.
          </p>
        </div>
      )}

      <div className={result ? "grid grid-cols-1 xl:grid-cols-[380px_1fr] gap-6 items-start" : "max-w-xl"}>
        <LoanForm onSubmit={handleSubmit} submitting={submitting} />

        {error && (
          <div
            className="card p-4 text-sm xl:col-span-2"
            style={{ color: "var(--status-critical)", borderColor: "var(--status-critical)" }}
          >
            {error}
          </div>
        )}

        {result && <ResultPanel result={result} />}
      </div>
    </div>
  );
}
