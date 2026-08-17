"use client";

import { useState } from "react";
import type { LoanApplicationInput } from "@/lib/api";

const STATE_OPTIONS = ["VT", "DE", "WY", "ND", "SD", "MT", "RI", "AK", "DC"];

const DEFAULTS: LoanApplicationInput = {
  applicant_name: "",
  applicant_email: "",
  state_code: "VT",
  applicant_age: 35,
  annual_income: 95000,
  monthly_debt_payments: 800,
  loan_amount: 280000,
  property_value: 350000,
  loan_term_months: 360,
  loan_purpose: "home_purchase",
  loan_type: "conventional",
  occupancy_type: "principal_residence",
  dwelling_type: "single_family",
  construction_method: "site_built",
  total_units: 1,
};

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="flex flex-col gap-1 text-sm">
      <span style={{ color: "var(--text-secondary)" }}>{label}</span>
      {children}
    </label>
  );
}

const inputClass =
  "rounded-md border px-3 py-2 text-sm bg-transparent focus:outline-none focus:ring-2";

export default function LoanForm({
  onSubmit,
  submitting,
}: {
  onSubmit: (input: LoanApplicationInput) => void;
  submitting: boolean;
}) {
  const [form, setForm] = useState<LoanApplicationInput>(DEFAULTS);

  function update<K extends keyof LoanApplicationInput>(key: K, value: LoanApplicationInput[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit(form);
      }}
      className="card p-6 flex flex-col gap-5"
    >
      <div>
        <h2 className="text-lg font-semibold">Loan Application</h2>
        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
          Real-time fraud screening, approval prediction, interest-rate pricing, and a ranked
          lender panel — all from one application.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Field label="Full name">
          <input
            required
            className={inputClass}
            style={{ borderColor: "var(--border)" }}
            value={form.applicant_name}
            onChange={(e) => update("applicant_name", e.target.value)}
          />
        </Field>
        <Field label="Email">
          <input
            required
            type="email"
            className={inputClass}
            style={{ borderColor: "var(--border)" }}
            value={form.applicant_email}
            onChange={(e) => update("applicant_email", e.target.value)}
          />
        </Field>

        <Field label="State">
          <select
            className={inputClass}
            style={{ borderColor: "var(--border)" }}
            value={form.state_code}
            onChange={(e) => update("state_code", e.target.value)}
          >
            {STATE_OPTIONS.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Applicant age">
          <input
            required
            type="number"
            min={18}
            max={100}
            className={inputClass}
            style={{ borderColor: "var(--border)" }}
            value={form.applicant_age}
            onChange={(e) => update("applicant_age", Number(e.target.value))}
          />
        </Field>

        <Field label="Annual income (USD)">
          <input
            required
            type="number"
            min={1}
            className={inputClass}
            style={{ borderColor: "var(--border)" }}
            value={form.annual_income}
            onChange={(e) => update("annual_income", Number(e.target.value))}
          />
        </Field>
        <Field label="Existing monthly debt payments (USD)">
          <input
            required
            type="number"
            min={0}
            className={inputClass}
            style={{ borderColor: "var(--border)" }}
            value={form.monthly_debt_payments}
            onChange={(e) => update("monthly_debt_payments", Number(e.target.value))}
          />
        </Field>

        <Field label="Requested loan amount (USD)">
          <input
            required
            type="number"
            min={1}
            className={inputClass}
            style={{ borderColor: "var(--border)" }}
            value={form.loan_amount}
            onChange={(e) => update("loan_amount", Number(e.target.value))}
          />
        </Field>
        <Field label="Property value (USD)">
          <input
            required
            type="number"
            min={1}
            className={inputClass}
            style={{ borderColor: "var(--border)" }}
            value={form.property_value}
            onChange={(e) => update("property_value", Number(e.target.value))}
          />
        </Field>

        <Field label="Loan term">
          <select
            className={inputClass}
            style={{ borderColor: "var(--border)" }}
            value={form.loan_term_months}
            onChange={(e) => update("loan_term_months", Number(e.target.value))}
          >
            <option value={360}>30-year (360mo)</option>
            <option value={180}>15-year (180mo)</option>
          </select>
        </Field>
        <Field label="Loan purpose">
          <select
            className={inputClass}
            style={{ borderColor: "var(--border)" }}
            value={form.loan_purpose}
            onChange={(e) => update("loan_purpose", e.target.value)}
          >
            <option value="home_purchase">Home purchase</option>
            <option value="home_improvement">Home improvement</option>
            <option value="refinance">Refinancing</option>
            <option value="cash_out_refinance">Cash-out refinancing</option>
            <option value="other">Other</option>
          </select>
        </Field>

        <Field label="Loan type">
          <select
            className={inputClass}
            style={{ borderColor: "var(--border)" }}
            value={form.loan_type}
            onChange={(e) => update("loan_type", e.target.value)}
          >
            <option value="conventional">Conventional</option>
            <option value="fha">FHA insured</option>
            <option value="va">VA guaranteed</option>
            <option value="usda">USDA/RHS</option>
          </select>
        </Field>
        <Field label="Occupancy">
          <select
            className={inputClass}
            style={{ borderColor: "var(--border)" }}
            value={form.occupancy_type}
            onChange={(e) => update("occupancy_type", e.target.value)}
          >
            <option value="principal_residence">Principal residence</option>
            <option value="second_residence">Second residence</option>
            <option value="investment_property">Investment property</option>
          </select>
        </Field>

        <Field label="Dwelling">
          <select
            className={inputClass}
            style={{ borderColor: "var(--border)" }}
            value={form.dwelling_type}
            onChange={(e) => update("dwelling_type", e.target.value)}
          >
            <option value="single_family">Single family (1-4 units)</option>
            <option value="multifamily">Multifamily</option>
          </select>
        </Field>
        <Field label="Construction method">
          <select
            className={inputClass}
            style={{ borderColor: "var(--border)" }}
            value={form.construction_method}
            onChange={(e) => update("construction_method", e.target.value)}
          >
            <option value="site_built">Site-built</option>
            <option value="manufactured">Manufactured</option>
          </select>
        </Field>
      </div>

      <button
        type="submit"
        disabled={submitting}
        className="rounded-md px-4 py-2.5 text-sm font-medium text-white disabled:opacity-60 transition"
        style={{ background: "var(--series-1)" }}
      >
        {submitting ? "Running AI intelligence layer…" : "Submit application"}
      </button>
    </form>
  );
}
