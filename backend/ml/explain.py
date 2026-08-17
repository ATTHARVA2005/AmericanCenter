"""SHAP-based explainability for the tree models. Wraps shap.TreeExplainer so
routers can ask "why" a prediction came out the way it did and get back a
ranked, human-readable list of feature contributions instead of raw arrays.
"""
import shap
import pandas as pd

FRIENDLY_NAMES = {
    "loan_amount": "Requested loan amount",
    "loan_to_value_ratio": "Loan-to-value ratio",
    "income": "Annual income",
    "debt_to_income_ratio": "Debt-to-income ratio",
    "property_value": "Property value",
    "loan_term": "Loan term",
    "applicant_age_numeric": "Applicant age",
    "total_units_numeric": "Property units",
    "loan_type": "Loan type",
    "loan_purpose": "Loan purpose",
    "lien_status": "Lien status",
    "occupancy_type": "Occupancy type",
    "derived_dwelling_category": "Dwelling category",
    "applicant_credit_score_type": "Credit score model reported",
    "construction_method": "Construction method",
    "state_code": "State",
}


class TreeExplainer:
    def __init__(self, xgb_model):
        self._explainer = shap.TreeExplainer(xgb_model)

    def explain_row(self, X_row: pd.DataFrame, top_k: int = 5) -> list[dict]:
        shap_values = self._explainer.shap_values(X_row)
        row_values = shap_values[0]
        contributions = []
        for feature, value, shap_val in zip(X_row.columns, X_row.iloc[0], row_values):
            contributions.append(
                {
                    "feature": FRIENDLY_NAMES.get(feature, feature),
                    "value": str(value),
                    "impact": round(float(shap_val), 4),
                    "direction": "increases" if shap_val > 0 else "decreases",
                }
            )
        contributions.sort(key=lambda c: abs(c["impact"]), reverse=True)
        return contributions[:top_k]
