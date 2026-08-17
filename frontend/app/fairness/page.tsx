"use client";

import { useEffect, useState } from "react";
import FairnessChart from "@/components/FairnessChart";
import { fetchBiasReport, type BiasReport } from "@/lib/api";

export default function FairnessPage() {
  const [report, setReport] = useState<BiasReport | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchBiasReport()
      .then(setReport)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load"));
  }, []);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold mb-1">Bias &amp; Fairness Dashboard</h1>
        <p className="text-sm max-w-2xl" style={{ color: "var(--text-secondary)" }}>
          A fairlearn audit of the loan-approval model&apos;s outcomes across HMDA&apos;s disclosed race,
          ethnicity and sex fields, computed once on the model&apos;s held-out test set (
          {report ? report.n_test_samples.toLocaleString() : "…"} applications). Race and ethnicity are
          <em> not</em> used as model inputs — this checks the model&apos;s outcomes for disparate impact,
          not its inputs.
        </p>
      </div>

      {error && (
        <div className="card p-4 text-sm" style={{ color: "var(--status-critical)" }}>
          {error}
        </div>
      )}

      {!report && !error && (
        <div className="text-sm" style={{ color: "var(--text-muted)" }}>
          Loading fairness report…
        </div>
      )}

      {report && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {report.audits.map((audit) => (
            <FairnessChart key={audit.attribute} audit={audit} />
          ))}
        </div>
      )}
    </div>
  );
}
