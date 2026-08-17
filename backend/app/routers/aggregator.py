from fastapi import APIRouter

from app import aggregator_mock

router = APIRouter(prefix="/api/aggregator", tags=["aggregator"])


@router.post("/consent")
def issue_consent(applicant_id: str):
    """Mock CFPB Section 1033 consent grant. Real aggregators (Plaid,
    MeridianLink, Finicity) return the same shape: a scoped, expiring token."""
    return aggregator_mock.issue_consent_token(applicant_id)


@router.get("/credit-report")
def credit_report(applicant_id: str, income_thousands: float, requested_loan_amount: float):
    return aggregator_mock.pull_credit_report(applicant_id, income_thousands, requested_loan_amount)


@router.get("/transactions")
def transactions(applicant_id: str, n: int = 25):
    df = aggregator_mock.pull_bank_transactions(applicant_id, n)
    return df.drop(columns=["Class"]).to_dict(orient="records")
