"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { BiasAudit } from "@/lib/api";

const ATTRIBUTE_LABELS: Record<string, string> = {
  derived_race: "Race",
  derived_sex: "Sex",
  derived_ethnicity: "Ethnicity",
};

export default function FairnessChart({ audit }: { audit: BiasAudit }) {
  const data = [...audit.by_group]
    .sort((a, b) => b.selection_rate - a.selection_rate)
    .map((g) => ({ ...g, selection_rate_pct: Number((g.selection_rate * 100).toFixed(1)) }));

  return (
    <div className="card p-5">
      <div className="flex items-start justify-between mb-1">
        <div>
          <h3 className="font-semibold">{ATTRIBUTE_LABELS[audit.attribute] ?? audit.attribute}</h3>
          <p className="text-xs" style={{ color: "var(--text-muted)" }}>
            Approval (selection) rate by group, held-out test set
          </p>
        </div>
        <span
          className="text-xs px-2 py-1 rounded-full text-white font-medium"
          style={{ background: audit.flag === "review" ? "var(--status-warning)" : "var(--status-good)" }}
        >
          {audit.flag === "review" ? "Review" : "OK"}
        </span>
      </div>
      <p className="text-xs mb-3" style={{ color: "var(--text-secondary)" }}>
        Demographic parity difference:{" "}
        <strong>{(audit.demographic_parity_difference * 100).toFixed(1)} pts</strong> · Equalized odds
        difference: <strong>{(audit.equalized_odds_difference * 100).toFixed(1)} pts</strong>
      </p>
      <ResponsiveContainer width="100%" height={Math.max(160, data.length * 34)}>
        <BarChart data={data} layout="vertical" margin={{ left: 8, right: 32, top: 4, bottom: 4 }}>
          <CartesianGrid horizontal={false} stroke="var(--gridline)" />
          <XAxis
            type="number"
            domain={[0, 100]}
            unit="%"
            tick={{ fill: "var(--text-muted)", fontSize: 11 }}
            stroke="var(--baseline)"
          />
          <YAxis
            type="category"
            dataKey="group"
            width={190}
            tick={{ fill: "var(--text-secondary)", fontSize: 12 }}
            stroke="var(--baseline)"
          />
          <ReferenceLine
            x={Number((audit.overall_selection_rate * 100).toFixed(1))}
            stroke="var(--text-muted)"
            strokeDasharray="4 4"
            label={{ value: "overall", position: "insideTopRight", fill: "var(--text-muted)", fontSize: 10 }}
          />
          <Tooltip
            contentStyle={{
              background: "var(--surface-1)",
              border: "1px solid var(--border)",
              borderRadius: 8,
              fontSize: 12,
              color: "var(--text-primary)",
            }}
            formatter={(value, _n, props) => [`${value}% (n=${props.payload.n})`, "Selection rate"]}
          />
          <Bar dataKey="selection_rate_pct" fill="var(--series-1)" radius={4} maxBarSize={18} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
