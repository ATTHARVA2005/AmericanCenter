import type { CreditReport } from "@/lib/api";

export default function CreditReportCard({ report }: { report: CreditReport }) {
  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">Credit Report — {report.bureau}</h3>
        <span className="text-xs" style={{ color: "var(--text-muted)" }}>
          {report.pulled_via}
        </span>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
        <div>
          <div style={{ color: "var(--text-muted)" }}>Score</div>
          <div className="text-lg font-semibold" style={{ color: "var(--series-1)" }}>
            {report.score}
          </div>
          <div className="text-xs" style={{ color: "var(--text-muted)" }}>
            {report.score_range}
          </div>
        </div>
        <div>
          <div style={{ color: "var(--text-muted)" }}>Hard inquiries (12mo)</div>
          <div className="text-lg font-semibold">{report.hard_inquiries_last_12mo}</div>
        </div>
        <div>
          <div style={{ color: "var(--text-muted)" }}>Open tradelines</div>
          <div className="text-lg font-semibold">{report.open_tradelines}</div>
        </div>
        <div>
          <div style={{ color: "var(--text-muted)" }}>Revolving utilization</div>
          <div className="text-lg font-semibold">{report.revolving_utilization_pct}%</div>
        </div>
      </div>
      <ul className="mt-3 text-sm list-disc list-inside" style={{ color: "var(--text-secondary)" }}>
        {report.factors.map((f) => (
          <li key={f}>{f}</li>
        ))}
      </ul>
    </div>
  );
}
