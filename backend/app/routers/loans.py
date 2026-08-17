import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app import aggregator_mock, db, inference
from app.schemas import (
    CONSTRUCTION_CODE,
    LOAN_PURPOSE_CODE,
    LOAN_TYPE_CODE,
    OCCUPANCY_CODE,
    LoanApplicationRequest,
    dwelling_category,
)
from ml.personas import build_offers

router = APIRouter(prefix="/api/loans", tags=["loans"])


@router.post("/apply")
def apply(request: LoanApplicationRequest):
    applicant_id = request.applicant_email.strip().lower()

    # --- Step 0: mock 1033-compliant aggregator pull -----------------------
    aggregator_mock.issue_consent_token(applicant_id)
    credit_report = aggregator_mock.pull_credit_report(
        applicant_id, request.annual_income / 1000, request.loan_amount
    )
    transactions = aggregator_mock.pull_bank_transactions(applicant_id)

    # --- AI Intelligence Layer, column 1: fraud detection -------------------
    fraud_result = inference.predict_fraud(transactions)

    # --- Build the shared feature row for the HMDA-trained models ----------
    dti = (request.monthly_debt_payments * 12) / request.annual_income * 100 if request.annual_income else 0
    ltv = request.loan_amount / request.property_value * 100 if request.property_value else 0

    feature_payload = {
        "loan_amount": request.loan_amount,
        "loan_to_value_ratio": ltv,
        "income": request.annual_income / 1000,  # HMDA reports income in thousands
        "debt_to_income_ratio": dti,
        "property_value": request.property_value,
        "loan_term": request.loan_term_months,
        "applicant_age_numeric": request.applicant_age,
        "total_units_numeric": request.total_units,
        "loan_type": LOAN_TYPE_CODE[request.loan_type],
        "loan_purpose": LOAN_PURPOSE_CODE[request.loan_purpose],
        "lien_status": "1",
        "occupancy_type": OCCUPANCY_CODE[request.occupancy_type],
        "derived_dwelling_category": dwelling_category(request.dwelling_type, request.construction_method),
        "applicant_credit_score_type": credit_report["hmda_score_type_code"],
        "construction_method": CONSTRUCTION_CODE[request.construction_method],
        "state_code": request.state_code.upper(),
    }
    row = inference.build_feature_row(feature_payload)

    # --- AI Intelligence Layer, column 2: loan approval ---------------------
    approval_proba, approval_explanation = inference.predict_approval(row)
    approved = approval_proba >= 0.5

    # --- AI Intelligence Layer, column 3: interest rate ---------------------
    base_rate, rate_explanation = inference.predict_interest_rate(row)

    # --- AI Intelligence Layer, column 4: recommendation system -------------
    offers = build_offers(approval_proba, base_rate, request.loan_amount)

    # --- AI Intelligence Layer, column 5: bias / fairness check -------------
    bias_summary = inference.get_bias_report()

    application_id = str(uuid.uuid4())
    response = {
        "application_id": application_id,
        "approved": approved,
        "approval_probability": round(approval_proba, 4),
        "approval_explanation": approval_explanation,
        "predicted_base_interest_rate": base_rate,
        "interest_rate_explanation": rate_explanation,
        "credit_report": {k: v for k, v in credit_report.items() if k != "hmda_score_type_code"},
        "ai_intelligence_layer": {
            "fraud_detection": fraud_result,
            "loan_approval": {"approved": approved, "approval_probability": round(approval_proba, 4)},
            "interest_rate_prediction": {"predicted_base_interest_rate": base_rate},
            "recommendation_system": offers,
            "bias_fairness_check": {
                "note": "Model-level audit (not per-applicant). See /api/bias/report for full detail.",
                "flags": [a["attribute"] for a in bias_summary["audits"] if a["flag"] == "review"],
            },
        },
        "offers": offers,
    }

    db.insert_application(
        application_id,
        datetime.now(timezone.utc).isoformat(),
        request,
        response,
    )
    return response


@router.get("/apply/{application_id}")
def get_application(application_id: str):
    result = db.get_application(application_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return result


@router.get("/recent")
def recent_applications(limit: int = 25):
    return db.list_applications(limit)
