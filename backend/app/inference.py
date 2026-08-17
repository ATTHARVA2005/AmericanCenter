"""Loads the three trained XGBoost models once at process start and exposes
plain prediction/explanation functions the routers call. Keeping model
loading here (rather than per-request) is what makes the API fast enough to
demo live.
"""
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb

from ml.data_prep import CATEGORICAL_FEATURES, NUMERIC_FEATURES, ALL_FEATURES
from ml.explain import TreeExplainer

BASE_DIR = Path(__file__).resolve().parent.parent

_approval_model = xgb.XGBClassifier()
_approval_model.load_model(BASE_DIR / "models" / "approval_model.json")
_approval_meta = joblib.load(BASE_DIR / "models" / "approval_meta.joblib")
_approval_explainer = TreeExplainer(_approval_model)

_interest_model = xgb.XGBRegressor()
_interest_model.load_model(BASE_DIR / "models" / "interest_model.json")
_interest_meta = joblib.load(BASE_DIR / "models" / "interest_meta.joblib")
_interest_explainer = TreeExplainer(_interest_model)

_fraud_model = xgb.XGBClassifier()
_fraud_model.load_model(BASE_DIR / "models" / "fraud_model.json")
_fraud_meta = joblib.load(BASE_DIR / "models" / "fraud_meta.joblib")

with open(BASE_DIR / "models" / "bias_report.json") as f:
    _bias_report = json.load(f)


def _coerce_categorical(series: pd.Series, allowed_categories: list[str]) -> pd.Series:
    """Casts to the exact category set seen at training time. XGBoost's
    native categorical support validates the *declared* category list against
    training, so we can't introduce a new 'Unknown' category — instead, any
    value the model never saw in training (e.g. a state outside our 9-state
    HMDA sample) falls through to NaN, which XGBoost natively treats as
    missing and routes down the tree's learned default branch."""
    values = series.astype(str)
    return pd.Categorical(values, categories=allowed_categories)


def build_feature_row(payload: dict) -> pd.DataFrame:
    """payload keys must match ml.data_prep.ALL_FEATURES."""
    row = {k: [payload.get(k)] for k in ALL_FEATURES}
    df = pd.DataFrame(row)
    for col in NUMERIC_FEATURES:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in CATEGORICAL_FEATURES:
        df[col] = _coerce_categorical(df[col], _approval_meta["categories"][col])
    return df


def predict_approval(row: pd.DataFrame):
    proba = float(_approval_model.predict_proba(row)[0, 1])
    explanation = _approval_explainer.explain_row(row)
    return proba, explanation


def predict_interest_rate(row: pd.DataFrame):
    rate = float(_interest_model.predict(row)[0])
    explanation = _interest_explainer.explain_row(row)
    return round(rate, 3), explanation


def predict_fraud(transactions: pd.DataFrame):
    """transactions must have columns matching ml.train_fraud.FEATURES
    (V1..V28, Amount, Time)."""
    features = _fraud_meta["features"]
    X = transactions[features]
    probs = _fraud_model.predict_proba(X)[:, 1]
    max_idx = int(np.argmax(probs))
    return {
        "transactions_screened": len(transactions),
        "max_fraud_probability": float(probs[max_idx]),
        "flagged_count": int((probs >= 0.5).sum()),
        "mean_fraud_probability": float(probs.mean()),
        "risk_level": _fraud_risk_level(float(probs.max())),
    }


def _fraud_risk_level(max_proba: float) -> str:
    if max_proba >= 0.75:
        return "high"
    if max_proba >= 0.35:
        return "medium"
    return "low"


def get_bias_report() -> dict:
    return _bias_report


def model_health() -> dict:
    return {
        "approval_model": {"test_auc": _approval_meta["test_auc"], "test_accuracy": _approval_meta["test_accuracy"]},
        "interest_model": {"test_mae": _interest_meta["test_mae"], "test_r2": _interest_meta["test_r2"]},
        "fraud_model": {"test_auc": _fraud_meta["test_auc"], "test_avg_precision": _fraud_meta["test_avg_precision"]},
    }
