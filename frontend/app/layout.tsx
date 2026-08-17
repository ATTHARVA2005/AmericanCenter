import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "CapitalMind AI — Loan Marketplace",
  description: "AI marketplace for personalized loan offers",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className="h-full">
      <body className="min-h-full flex flex-col">
        <header
          className="border-b sticky top-0 z-10"
          style={{ background: "var(--surface-1)", borderColor: "var(--border)" }}
        >
          <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
            <Link href="/" className="font-semibold tracking-tight">
              CapitalMind <span style={{ color: "var(--series-1)" }}>AI</span>
            </Link>
            <nav className="flex gap-6 text-sm" style={{ color: "var(--text-secondary)" }}>
              <Link href="/" className="hover:underline">
                Apply
              </Link>
              <Link href="/history" className="hover:underline">
                Application History
              </Link>
              <Link href="/fairness" className="hover:underline">
                Fairness Dashboard
              </Link>
            </nav>
          </div>
        </header>
        <main className="flex-1 max-w-6xl w-full mx-auto px-6 py-8">{children}</main>
        <footer
          className="border-t text-xs py-6 text-center"
          style={{ borderColor: "var(--border)", color: "var(--text-muted)" }}
        >
          CapitalMind AI — MVP demo. Trained on real CFPB/HMDA 2023 mortgage data and the ULB/Worldline
          credit-card transaction dataset. Bureau and bank-account data shown are simulated via a mock
          1033-style aggregator.
        </footer>
      </body>
    </html>
  );
}
