"""Trains the loan-approval XGBoost classifier on real CFPB/HMDA 2023 data.

Run from backend/:  .venv/Scripts/python.exe -m ml.train_approval
"""
import json

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from sklearn.model_selection import train_test_split

from ml.data_prep import (
    ALL_FEATURES,
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    PROTECTED_COLUMNS,
    approval_label,
    build_feature_frame,
    engineer_features,
    load_raw_hmda,
)

MODEL_PATH = "models/approval_model.json"
META_PATH = "models/approval_meta.joblib"
TEST_SET_PATH = "data/processed/approval_test_with_groups.parquet"


def main():
    print("Loading raw HMDA data...")
    raw = load_raw_hmda()
    raw = raw[raw["action_taken"].isin([1, 2, 3])].copy()
    print(f"Decisioned applications (originated/approved/denied): {len(raw)}")

    df = engineer_features(raw)
    X = build_feature_frame(df)
    y = approval_label(df)
    groups = df[PROTECTED_COLUMNS].reset_index(drop=True)

    categories = {col: X[col].cat.categories.tolist() for col in CATEGORICAL_FEATURES}

    X_train, X_test, y_train, y_test, groups_train, groups_test = train_test_split(
        X, y, groups, test_size=0.2, random_state=42, stratify=y
    )

    model = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="auc",
        enable_categorical=True,
        random_state=42,
    )
    model.fit(X_train, y_train)

    proba = model.predict_proba(X_test)[:, 1]
    pred = (proba >= 0.5).astype(int)
    auc = roc_auc_score(y_test, proba)
    acc = accuracy_score(y_test, pred)
    print(f"Test AUC: {auc:.4f}  Accuracy: {acc:.4f}")
    print(classification_report(y_test, pred, target_names=["Denied", "Approved"]))

    model.save_model(MODEL_PATH)
    joblib.dump(
        {
            "numeric_features": NUMERIC_FEATURES,
            "categorical_features": CATEGORICAL_FEATURES,
            "all_features": ALL_FEATURES,
            "categories": categories,
            "test_auc": auc,
            "test_accuracy": acc,
        },
        META_PATH,
    )

    test_out = X_test.copy()
    for col in CATEGORICAL_FEATURES:
        test_out[col] = test_out[col].astype(str)
    test_out["y_true"] = y_test.values
    test_out["y_pred"] = pred
    test_out["y_proba"] = proba
    test_out = pd.concat([test_out.reset_index(drop=True), groups_test.reset_index(drop=True)], axis=1)
    test_out.to_parquet(TEST_SET_PATH, index=False)

    print(f"Saved model -> {MODEL_PATH}")
    print(f"Saved metadata -> {META_PATH}")
    print(f"Saved test set (with protected attrs, for bias audit) -> {TEST_SET_PATH}")


if __name__ == "__main__":
    main()
