import type { LenderOffer } from "@/lib/api";

export default function OffersList({ offers }: { offers: LenderOffer[] }) {
  if (!offers.length) {
    return (
      <div className="card p-5 text-sm" style={{ color: "var(--text-secondary)" }}>
        No lender in the current panel clears this applicant&apos;s risk profile or requested loan
        amount.
      </div>
    );
  }

  return (
    <div className="card overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left" style={{ color: "var(--text-muted)", borderBottom: "1px solid var(--border)" }}>
              <th className="px-4 py-3 font-medium">Lender</th>
              <th className="px-4 py-3 font-medium">Rate</th>
              <th className="px-4 py-3 font-medium">Est. monthly payment</th>
              <th className="px-4 py-3 font-medium">Confidence</th>
              <th className="px-4 py-3 font-medium">Processing</th>
            </tr>
          </thead>
          <tbody>
            {offers.map((offer, i) => (
              <tr key={offer.lender_id} style={{ borderTop: i === 0 ? undefined : "1px solid var(--gridline)" }}>
                <td className="px-4 py-3 font-medium">
                  {offer.lender_name}
                  {i === 0 && (
                    <span
                      className="ml-2 text-[10px] px-1.5 py-0.5 rounded-full text-white"
                      style={{ background: "var(--status-good)" }}
                    >
                      BEST RATE
                    </span>
                  )}
                </td>
                <td className="px-4 py-3" style={{ color: "var(--series-1)", fontWeight: 600 }}>
                  {offer.offered_interest_rate}%
                </td>
                <td className="px-4 py-3">${offer.est_monthly_payment_360m.toLocaleString()}</td>
                <td className="px-4 py-3">{Math.round(offer.lender_confidence * 100)}%</td>
                <td className="px-4 py-3" style={{ color: "var(--text-secondary)" }}>
                  {offer.processing_tier}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
