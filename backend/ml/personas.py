"""Simulated lender panel for the marketplace.

We have one real, HMDA-trained risk core (the approval-probability and
base-interest-rate models). Individual banks' internal underwriting models
are proprietary and not publicly available, so — the same way a real loan
marketplace (Even, LendingTree, Credible) layers partner-specific business
rules on top of a shared risk score — each persona below re-prices and
re-thresholds the shared model output according to its own risk appetite,
fee structure and processing tier. This is what turns one prediction into a
ranked, multi-bank marketplace instead of a single yes/no.
"""

LENDER_PERSONAS = [
    {
        "id": "north_star_bank",
        "name": "North Star National Bank",
        "risk_appetite": "conservative",
        "min_approval_proba": 0.65,
        "rate_margin": -0.15,   # prices slightly below the market base rate
        "max_loan_amount": 750_000,
        "commission_bps": 90,   # commission the marketplace earns per closed loan
        "processing_tier": "standard (5-7 business days)",
    },
    {
        "id": "meridian_credit_union",
        "name": "Meridian Credit Union",
        "risk_appetite": "conservative",
        "min_approval_proba": 0.60,
        "rate_margin": -0.35,
        "max_loan_amount": 500_000,
        "commission_bps": 60,
        "processing_tier": "standard (5-7 business days)",
    },
    {
        "id": "harbor_point_financial",
        "name": "Harbor Point Financial",
        "risk_appetite": "balanced",
        "min_approval_proba": 0.45,
        "rate_margin": 0.10,
        "max_loan_amount": 1_000_000,
        "commission_bps": 110,
        "processing_tier": "expedited (2-3 business days)",
    },
    {
        "id": "summit_direct_lending",
        "name": "Summit Direct Lending",
        "risk_appetite": "growth",
        "min_approval_proba": 0.30,
        "rate_margin": 0.55,
        "max_loan_amount": 400_000,
        "commission_bps": 140,
        "processing_tier": "expedited (2-3 business days)",
    },
    {
        "id": "beacon_nbfc_partners",
        "name": "Beacon NBFC Partners",
        "risk_appetite": "growth",
        "min_approval_proba": 0.20,
        "rate_margin": 1.10,
        "max_loan_amount": 250_000,
        "commission_bps": 175,
        "processing_tier": "same-day pre-qualification",
    },
]


def build_offers(approval_proba: float, base_rate: float, loan_amount: float) -> list[dict]:
    """Ranks the lender panel for one applicant given the shared risk model's
    output. Returns only lenders this applicant would plausibly clear, sorted
    by lowest offered rate first."""
    offers = []
    for lender in LENDER_PERSONAS:
        if loan_amount > lender["max_loan_amount"]:
            continue
        if approval_proba < lender["min_approval_proba"]:
            continue

        offered_rate = round(max(base_rate + lender["rate_margin"], 1.0), 3)
        # A lender's own comfort with this applicant, given how far above its
        # bar the applicant's approval probability sits.
        headroom = min(1.0, (approval_proba - lender["min_approval_proba"]) / (1 - lender["min_approval_proba"] + 1e-6))
        lender_confidence = round(0.5 + 0.5 * headroom, 3)

        offers.append(
            {
                "lender_id": lender["id"],
                "lender_name": lender["name"],
                "offered_interest_rate": offered_rate,
                "lender_confidence": lender_confidence,
                "processing_tier": lender["processing_tier"],
                "est_monthly_payment_360m": _monthly_payment(loan_amount, offered_rate, 360),
                "marketplace_commission_bps": lender["commission_bps"],
            }
        )

    offers.sort(key=lambda o: o["offered_interest_rate"])
    return offers


def _monthly_payment(principal: float, annual_rate_pct: float, term_months: int) -> float:
    if principal is None or principal <= 0:
        return 0.0
    r = (annual_rate_pct / 100) / 12
    if r == 0:
        return round(principal / term_months, 2)
    payment = principal * (r * (1 + r) ** term_months) / ((1 + r) ** term_months - 1)
    return round(payment, 2)
