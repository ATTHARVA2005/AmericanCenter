"""Fairness audit of the loan-approval model's predictions across HMDA's
race/ethnicity/sex fields, using fairlearn. This runs the audit on the model's
own held-out test set and caches a JSON report the API serves as-is (an audit
of a fixed model doesn't need to be re-run per request).

Run from backend/:  .venv/Scripts/python.exe -m ml.bias_audit
"""
import json

import pandas as pd
from fairlearn.metrics import (
    MetricFrame,
    demographic_parity_difference,
    equalized_odds_difference,
    false_negative_rate,
    selection_rate,
)
from sklearn.metrics import accuracy_score

TEST_SET_PATH = "data/processed/approval_test_with_groups.parquet"
REPORT_PATH = "models/bias_report.json"

GROUP_COLUMNS = {
    "race": "derived_race",
    "sex": "derived_sex",
    "ethnicity": "derived_ethnicity",
}

# Groups with too few test examples produce noisy/unreliable rates.
MIN_GROUP_SIZE = 30


def audit_one(df: pd.DataFrame, group_col: str) -> dict:
    counts = df[group_col].value_counts()
    keep_groups = counts[counts >= MIN_GROUP_SIZE].index
    sub = df[df[group_col].isin(keep_groups)]

    mf = MetricFrame(
        metrics={
            "selection_rate": selection_rate,
            "accuracy": accuracy_score,
            "false_negative_rate": false_negative_rate,
        },
        y_true=sub["y_true"],
        y_pred=sub["y_pred"],
        sensitive_features=sub[group_col],
    )

    dp_diff = demographic_parity_difference(
        sub["y_true"], sub["y_pred"], sensitive_features=sub[group_col]
    )
    eo_diff = equalized_odds_difference(
        sub["y_true"], sub["y_pred"], sensitive_features=sub[group_col]
    )

    by_group = mf.by_group.reset_index().rename(columns={group_col: "group"})
    by_group["n"] = sub.groupby(group_col).size().reindex(by_group["group"]).values

    return {
        "attribute": group_col,
        "demographic_parity_difference": float(dp_diff),
        "equalized_odds_difference": float(eo_diff),
        "overall_selection_rate": float(mf.overall["selection_rate"]),
        "overall_accuracy": float(mf.overall["accuracy"]),
        "by_group": by_group.to_dict(orient="records"),
        "flag": "review" if abs(dp_diff) > 0.10 else "ok",
    }


def main():
    df = pd.read_parquet(TEST_SET_PATH)
    report = {"n_test_samples": len(df), "audits": []}
    for label, col in GROUP_COLUMNS.items():
        print(f"Auditing fairness across: {label} ({col})")
        result = audit_one(df, col)
        print(
            f"  demographic_parity_diff={result['demographic_parity_difference']:.4f}"
            f"  equalized_odds_diff={result['equalized_odds_difference']:.4f}"
            f"  flag={result['flag']}"
        )
        report["audits"].append(result)

    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Saved bias report -> {REPORT_PATH}")


if __name__ == "__main__":
    main()
