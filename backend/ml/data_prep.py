"""Shared HMDA cleaning / feature engineering used by both training and live inference.

Keeping this in one module guarantees the feature vector built for a live loan
application at request time is identical in shape/encoding to what the models
were trained on.
"""
import numpy as np
import pandas as pd

RAW_HMDA_PATH = "data/raw/hmda_2023_multistate.csv"

# Columns the trained models are allowed to see. Race, ethnicity and sex are
# deliberately excluded from the model inputs (fair-lending best practice) but
# are kept alongside the dataset for the bias-audit module to test the model's
# *outcomes* against.
NUMERIC_FEATURES = [
    "loan_amount",
    "loan_to_value_ratio",
    "income",
    "debt_to_income_ratio",
    "property_value",
    "loan_term",
    "applicant_age_numeric",
    "total_units_numeric",
]

CATEGORICAL_FEATURES = [
    "loan_type",
    "loan_purpose",
    "lien_status",
    "occupancy_type",
    "derived_dwelling_category",
    "applicant_credit_score_type",
    "construction_method",
    "state_code",
]

ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

PROTECTED_COLUMNS = ["derived_race", "derived_sex", "derived_ethnicity"]

_DTI_BUCKETS = {
    "<20%": 15.0,
    "20%-<30%": 25.0,
    "30%-<36%": 33.0,
    "50%-60%": 55.0,
    ">60%": 65.0,
}

_AGE_BUCKETS = {
    "<25": 22.0,
    "25-34": 29.5,
    "35-44": 39.5,
    "45-54": 49.5,
    "55-64": 59.5,
    "65-74": 69.5,
    ">74": 78.0,
}

_UNITS_BUCKETS = {
    "5-24": 14.5,
    "25-49": 37.0,
    "50-99": 74.5,
    "100-149": 124.5,
    ">149": 160.0,
}


def _parse_dti(value):
    if pd.isna(value):
        return np.nan
    value = str(value).strip()
    if value in _DTI_BUCKETS:
        return _DTI_BUCKETS[value]
    try:
        return float(value)
    except ValueError:
        return np.nan


def _parse_age(value):
    if pd.isna(value):
        return np.nan
    value = str(value).strip()
    if value in _AGE_BUCKETS:
        return _AGE_BUCKETS[value]
    return np.nan


def _parse_units(value):
    if pd.isna(value):
        return np.nan
    value = str(value).strip()
    if value in _UNITS_BUCKETS:
        return _UNITS_BUCKETS[value]
    try:
        return float(value)
    except ValueError:
        return np.nan


def _to_numeric(series):
    return pd.to_numeric(series, errors="coerce")


def load_raw_hmda(path: str = RAW_HMDA_PATH) -> pd.DataFrame:
    return pd.read_csv(path, low_memory=False)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Adds cleaned/derived columns in place and returns the same frame."""
    df = df.copy()
    df["debt_to_income_ratio"] = df["debt_to_income_ratio"].apply(_parse_dti)
    df["applicant_age_numeric"] = df["applicant_age"].apply(_parse_age)
    df["total_units_numeric"] = df["total_units"].apply(_parse_units)

    for col in ["loan_amount", "loan_to_value_ratio", "income", "property_value", "loan_term"]:
        df[col] = _to_numeric(df[col])

    df["interest_rate_numeric"] = _to_numeric(df["interest_rate"])

    for col in CATEGORICAL_FEATURES:
        df[col] = df[col].astype("string").fillna("Unknown").astype("category")

    return df


def build_feature_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Returns just the model-input columns, correctly typed for XGBoost
    (numeric floats + pandas 'category' dtype for categoricals)."""
    X = df[ALL_FEATURES].copy()
    for col in NUMERIC_FEATURES:
        X[col] = pd.to_numeric(X[col], errors="coerce")
    for col in CATEGORICAL_FEATURES:
        X[col] = X[col].astype("string").fillna("Unknown").astype("category")
    return X


def approval_label(df: pd.DataFrame) -> pd.Series:
    """1 = loan originated or approved-but-not-accepted, 0 = denied.
    Withdrawn (4) / incomplete (5) applications are excluded upstream since
    they reflect no lender credit decision."""
    return df["action_taken"].isin([1, 2]).astype(int)
