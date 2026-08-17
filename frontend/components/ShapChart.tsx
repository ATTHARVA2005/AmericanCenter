"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { FeatureContribution } from "@/lib/api";

export default function ShapChart({
  data,
  positiveLabel,
  negativeLabel,
}: {
  data: FeatureContribution[];
  positiveLabel: string;
  negativeLabel: string;
}) {
  const chartData = [...data].sort((a, b) => a.impact - b.impact);

  return (
    <div>
      <ResponsiveContainer width="100%" height={Math.max(160, chartData.length * 38)}>
        <BarChart data={chartData} layout="vertical" margin={{ left: 8, right: 24, top: 4, bottom: 4 }}>
          <CartesianGrid horizontal={false} stroke="var(--gridline)" />
          <XAxis type="number" tick={{ fill: "var(--text-muted)", fontSize: 11 }} stroke="var(--baseline)" />
          <YAxis
            type="category"
            dataKey="feature"
            width={160}
            tick={{ fill: "var(--text-secondary)", fontSize: 12 }}
            stroke="var(--baseline)"
          />
          <ReferenceLine x={0} stroke="var(--baseline)" />
          <Tooltip
            contentStyle={{
              background: "var(--surface-1)",
              border: "1px solid var(--border)",
              borderRadius: 8,
              fontSize: 12,
              color: "var(--text-primary)",
            }}
            formatter={(value, _name, props) => {
              const impact = Number(value);
              return [
                `${impact > 0 ? "+" : ""}${impact.toFixed(3)} (value: ${props.payload.value})`,
                impact > 0 ? positiveLabel : negativeLabel,
              ];
            }}
          />
          <Bar dataKey="impact" radius={4} maxBarSize={18}>
            {chartData.map((entry, i) => (
              <Cell key={i} fill={entry.impact >= 0 ? "var(--series-1)" : "var(--series-8)"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div className="flex gap-4 text-xs mt-1" style={{ color: "var(--text-secondary)" }}>
        <span className="flex items-center gap-1.5">
          <span className="inline-block w-2.5 h-2.5 rounded-full" style={{ background: "var(--series-1)" }} />
          {positiveLabel}
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block w-2.5 h-2.5 rounded-full" style={{ background: "var(--series-8)" }} />
          {negativeLabel}
        </span>
      </div>
    </div>
  );
}
