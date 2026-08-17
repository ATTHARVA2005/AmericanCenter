"""Trains the interest-rate XGBoost regressor on originated HMDA 2023 loans
that report a numeric interest rate (excludes 'Exempt'/blank rows).

Run from backend/:  .venv/Scripts/python.exe -m ml.train_interest
"""
import joblib
import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

from ml.data_prep import (
    ALL_FEATURES,
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    build_feature_frame,
    engineer_features,
    load_raw_hmda,
)

MODEL_PATH = "models/interest_model.json"
META_PATH = "models/interest_meta.joblib"


def main():
    print("Loading raw HMDA data...")
    raw = load_raw_hmda()
    raw = raw[raw["action_taken"] == 1].copy()  # originated loans only
    df = engineer_features(raw)
    df = df[df["interest_rate_numeric"].notna()]
    df = df[(df["interest_rate_numeric"] > 0) & (df["interest_rate_numeric"] < 20)]
    print(f"Originated loans with a usable interest rate: {len(df)}")

    X = build_feature_frame(df)
    y = df["interest_rate_numeric"]

    categories = {col: X[col].cat.categories.tolist() for col in CATEGORICAL_FEATURES}

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = xgb.XGBRegressor(
        n_estimators=400,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        enable_categorical=True,
        random_state=42,
    )
    model.fit(X_train, y_train)

    pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, pred)
    r2 = r2_score(y_test, pred)
    print(f"Test MAE: {mae:.4f} pts   R2: {r2:.4f}")

    model.save_model(MODEL_PATH)
    joblib.dump(
        {
            "numeric_features": NUMERIC_FEATURES,
            "categorical_features": CATEGORICAL_FEATURES,
            "all_features": ALL_FEATURES,
            "categories": categories,
            "test_mae": mae,
            "test_r2": r2,
        },
        META_PATH,
    )
    print(f"Saved model -> {MODEL_PATH}")
    print(f"Saved metadata -> {META_PATH}")


if __name__ == "__main__":
    main()
