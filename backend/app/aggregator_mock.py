"""Mock open-banking / credit-bureau aggregator.

Real bank-account linking (Plaid-style) and bureau pulls (Experian,
TransUnion, Equifax) require paid enterprise contracts that aren't available
for a student MVP. This module stands in for that layer, but is built to the
shape a real CFPB Section 1033-compliant aggregator would return: a scoped
consent token, a bank-linked transaction feed, and a bureau credit report —
so swapping in a real aggregator (e.g. Plaid, MeridianLink, Finicity) later is
a drop-in replacement of this module, not a redesign of the API.

Everything here is deterministic per-applicant (seeded from their submitted
identity fields) so a demo re-run for the same applicant is reproducible, and
the sampled transactions are drawn from the real ULB/Worldline anonymized
transaction dataset rather than fabricated numbers.
"""
import hashlib
import time
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
_FRAUD_COLS = [f"V{i}" for i in range(1, 29)] + ["Amount", "Time", "Class"]
_transaction_pool = pd.read_parquet(BASE_DIR / "data" / "raw" / "creditcard_fraud.parquet", columns=_FRAUD_COLS)

CREDIT_BUREAUS = ["Experian", "TransUnion", "Equifax"]

# HMDA's applicant_credit_score_type codes only disclose which scoring model
# was used, not the numeric score itself (HMDA does not publish raw FICO
# scores, by design, for consumer privacy). We map each mock bureau pull to
# the closest matching HMDA code so the trained approval/interest models —
# which were fit on that field — receive a value consistent with training.
BUREAU_TO_SCORE_TYPE_CODE = {
    "Equifax": "1",     # Equifax Beacon 5.0
    "Experian": "2",    # Experian Fair Isaac
    "TransUnion": "6",  # VantageScore 3.0 (tri-bureau model TransUnion commonly reports)
}


def _seed_from(identifier: str) -> int:
    digest = hashlib.sha256(identifier.encode()).hexdigest()
    return int(digest[:8], 16)


def issue_consent_token(applicant_id: str) -> dict:
    """Simulates the OAuth-style consent grant a 1033-compliant aggregator
    issues before any account data can be pulled."""
    seed = _seed_from(applicant_id)
    token = hashlib.sha256(f"{applicant_id}-{seed}".encode()).hexdigest()[:32]
    return {
        "applicant_id": applicant_id,
        "consent_token": token,
        "scope": ["accounts:read", "transactions:read", "credit_report:read"],
        "issued_at": int(time.time()),
        "expires_in_seconds": 3600,
        "standard": "CFPB Section 1033 personal financial data rights",
    }


def pull_bank_transactions(applicant_id: str, n: int = 25) -> pd.DataFrame:
    seed = _seed_from(applicant_id)
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(_transaction_pool), size=n, replace=False)
    sample = _transaction_pool.iloc[idx].reset_index(drop=True)
    return sample


def pull_credit_report(applicant_id: str, income_thousands: float, requested_loan_amount: float) -> dict:
    seed = _seed_from(applicant_id)
    rng = np.random.default_rng(seed)
    bureau = CREDIT_BUREAUS[seed % 3]

    # A deterministic-but-plausible score: modestly correlated with income
    # relative to requested loan size, plus per-applicant noise so it isn't
    # just a formula the audience can reverse-engineer live.
    income = max(income_thousands or 0, 1)
    leverage = min((requested_loan_amount or 0) / (income * 1000 + 1), 10)
    base = 680 + 25 * np.log1p(income / 50) - 18 * leverage
    noise = rng.normal(0, 35)
    score = int(np.clip(base + noise, 300, 850))

    inquiries = int(rng.integers(0, 6))
    tradelines = int(rng.integers(3, 18))
    utilization = round(float(rng.uniform(5, 85)), 1)

    return {
        "bureau": bureau,
        "score": score,
        "score_range": "300-850",
        "hmda_score_type_code": BUREAU_TO_SCORE_TYPE_CODE[bureau],
        "hard_inquiries_last_12mo": inquiries,
        "open_tradelines": tradelines,
        "revolving_utilization_pct": utilization,
        "factors": _score_factors(score, utilization, inquiries),
        "pulled_via": "Mock 1033-compliant aggregator (sandbox — not a live bureau connection)",
    }


def _score_factors(score: int, utilization: float, inquiries: int) -> list[str]:
    factors = []
    if utilization > 50:
        factors.append("High revolving credit utilization")
    if inquiries >= 4:
        factors.append("Multiple recent hard inquiries")
    if score < 620:
        factors.append("Limited or adverse credit history")
    if not factors:
        factors.append("Stable credit history, low utilization")
    return factors
