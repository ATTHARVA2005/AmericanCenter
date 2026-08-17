"""Trains the fraud-detection XGBoost classifier on the real ULB/Worldline
credit-card transactions dataset (284,807 transactions, 492 confirmed frauds).

Run from backend/:  .venv/Scripts/python.exe -m ml.train_fraud
"""
import joblib
import pandas as pd
import xgboost as xgb
from sklearn.metrics import average_precision_score, classification_report, roc_auc_score
from sklearn.model_selection import train_test_split

RAW_PATH = "data/raw/creditcard_fraud.parquet"
MODEL_PATH = "models/fraud_model.json"
META_PATH = "models/fraud_meta.joblib"

FEATURES = [f"V{i}" for i in range(1, 29)] + ["Amount", "Time"]


def main():
    print("Loading credit card transactions...")
    df = pd.read_parquet(RAW_PATH)
    X = df[FEATURES]
    y = df["Class"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()

    model = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="aucpr",
        scale_pos_weight=scale_pos_weight,
        random_state=42,
    )
    model.fit(X_train, y_train)

    proba = model.predict_proba(X_test)[:, 1]
    pred = (proba >= 0.5).astype(int)
    auc = roc_auc_score(y_test, proba)
    ap = average_precision_score(y_test, proba)
    print(f"Test ROC-AUC: {auc:.4f}   Average Precision: {ap:.4f}")
    print(classification_report(y_test, pred, target_names=["Legit", "Fraud"]))

    model.save_model(MODEL_PATH)
    joblib.dump(
        {
            "features": FEATURES,
            "test_auc": auc,
            "test_avg_precision": ap,
            "scale_pos_weight": scale_pos_weight,
        },
        META_PATH,
    )
    print(f"Saved model -> {MODEL_PATH}")


if __name__ == "__main__":
    main()
