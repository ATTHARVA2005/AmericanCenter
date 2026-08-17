from fastapi import APIRouter

from app import inference

router = APIRouter(prefix="/api/bias", tags=["bias"])


@router.get("/report")
def bias_report():
    """Fairlearn fairness audit of the loan-approval model across HMDA's
    disclosed race/ethnicity/sex fields, computed once on the held-out test
    set (ml/bias_audit.py) and served here for the compliance dashboard."""
    return inference.get_bias_report()
