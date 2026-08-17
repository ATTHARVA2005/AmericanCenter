"use client";

import { useEffect, useState } from "react";
import { fetchRecentApplications, type RecentApplication } from "@/lib/api";

function riskColor(level: string) {
  if (level === "high") return "var(--status-critical)";
  if (level === "medium") return "var(--status-warning)";
  return "var(--status-good)";
}

export default function HistoryPage() {
  const [rows, setRows] = useState<RecentApplication[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchRecentApplications()
      .then(setRows)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load"));
  }, []);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold mb-1">Application History</h1>
        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
          Recent applications processed by the AI intelligence layer, most recent first.
        </p>
      </div>

      {error && (
        <div className="card p-4 text-sm" style={{ color: "var(--status-critical)" }}>
          {error}
        </div>
      )}

      {rows && rows.length === 0 && (
        <div className="text-sm" style={{ color: "var(--text-muted)" }}>
          No applications yet — submit one from the Apply page.
        </div>
      )}

      {rows && rows.length > 0 && (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr
                  className="text-left"
                  style={{ color: "var(--text-muted)", borderBottom: "1px solid var(--border)" }}
                >
                  <th className="px-4 py-3 font-medium">Applicant</th>
                  <th className="px-4 py-3 font-medium">State</th>
                  <th className="px-4 py-3 font-medium">Loan amount</th>
                  <th className="px-4 py-3 font-medium">Decision</th>
                  <th className="px-4 py-3 font-medium">Base rate</th>
                  <th className="px-4 py-3 font-medium">Fraud risk</th>
                  <th className="px-4 py-3 font-medium">Credit score</th>
                  <th className="px-4 py-3 font-medium">Offers</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row, i) => (
                  <tr key={row.id} style={{ borderTop: i === 0 ? undefined : "1px solid var(--gridline)" }}>
                    <td className="px-4 py-3 font-medium">{row.applicant_name}</td>
                    <td className="px-4 py-3">{row.state_code}</td>
                    <td className="px-4 py-3">${row.loan_amount.toLocaleString()}</td>
                    <td className="px-4 py-3">
                      <span style={{ color: row.approved ? "var(--status-good)" : "var(--status-critical)" }}>
                        {row.approved ? "Approved" : "Denied"}
                      </span>{" "}
                      <span style={{ color: "var(--text-muted)" }}>
                        ({(row.approval_probability * 100).toFixed(0)}%)
                      </span>
                    </td>
                    <td className="px-4 py-3">{row.predicted_base_interest_rate.toFixed(2)}%</td>
                    <td className="px-4 py-3">
                      <span style={{ color: riskColor(row.fraud_risk_level) }}>
                        {row.fraud_risk_level.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {row.credit_score} ({row.bureau})
                    </td>
                    <td className="px-4 py-3">{row.offers_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
