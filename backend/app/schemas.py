from typing import Literal, Optional

from pydantic import BaseModel, Field

LoanPurpose = Literal["home_purchase", "home_improvement", "refinance", "cash_out_refinance", "other"]
LoanType = Literal["conventional", "fha", "va", "usda"]
OccupancyType = Literal["principal_residence", "second_residence", "investment_property"]
DwellingType = Literal["single_family", "multifamily"]
ConstructionMethod = Literal["site_built", "manufactured"]

LOAN_PURPOSE_CODE = {
    "home_purchase": "1",
    "home_improvement": "2",
    "refinance": "31",
    "cash_out_refinance": "32",
    "other": "4",
}
LOAN_TYPE_CODE = {"conventional": "1", "fha": "2", "va": "3", "usda": "4"}
OCCUPANCY_CODE = {"principal_residence": "1", "second_residence": "2", "investment_property": "3"}
CONSTRUCTION_CODE = {"site_built": "1", "manufactured": "2"}


def dwelling_category(dwelling: DwellingType, construction: ConstructionMethod) -> str:
    base = "Single Family (1-4 Units)" if dwelling == "single_family" else "Multifamily"
    build = "Site-Built" if construction == "site_built" else "Manufactured"
    return f"{base}:{build}"


class LoanApplicationRequest(BaseModel):
    applicant_name: str = Field(..., min_length=1)
    applicant_email: str

    state_code: str = Field(..., min_length=2, max_length=2)
    applicant_age: int = Field(..., ge=18, le=100)

    annual_income: float = Field(..., gt=0, description="Gross annual income in USD")
    monthly_debt_payments: float = Field(0, ge=0, description="Existing monthly debt obligations in USD")

    loan_amount: float = Field(..., gt=0)
    property_value: float = Field(..., gt=0)
    loan_term_months: int = Field(360, description="360 = 30yr, 180 = 15yr")

    loan_purpose: LoanPurpose
    loan_type: LoanType
    occupancy_type: OccupancyType
    dwelling_type: DwellingType = "single_family"
    construction_method: ConstructionMethod = "site_built"
    total_units: int = Field(1, ge=1, le=149)


class FeatureContribution(BaseModel):
    feature: str
    value: str
    impact: float
    direction: str


class LenderOffer(BaseModel):
    lender_id: str
    lender_name: str
    offered_interest_rate: float
    lender_confidence: float
    processing_tier: str
    est_monthly_payment_360m: float
    marketplace_commission_bps: int


class CreditReport(BaseModel):
    bureau: str
    score: int
    score_range: str
    hard_inquiries_last_12mo: int
    open_tradelines: int
    revolving_utilization_pct: float
    factors: list[str]
    pulled_via: str


class FraudScreeningResult(BaseModel):
    transactions_screened: int
    max_fraud_probability: float
    flagged_count: int
    mean_fraud_probability: float
    risk_level: str


class AIIntelligenceLayer(BaseModel):
    """The 5 modules, in the order requested in review feedback (c):
    fraud detection first, then approval, interest rate, recommendation,
    and the bias/fairness check."""
    fraud_detection: FraudScreeningResult
    loan_approval: dict
    interest_rate_prediction: dict
    recommendation_system: list[LenderOffer]
    bias_fairness_check: dict


class LoanApplicationResponse(BaseModel):
    application_id: str
    approved: bool
    approval_probability: float
    approval_explanation: list[FeatureContribution]
    predicted_base_interest_rate: float
    interest_rate_explanation: list[FeatureContribution]
    credit_report: CreditReport
    ai_intelligence_layer: AIIntelligenceLayer
    offers: list[LenderOffer]
