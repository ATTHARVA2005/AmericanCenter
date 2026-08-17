import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "app.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS applications (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    applicant_name TEXT NOT NULL,
    applicant_email TEXT NOT NULL,
    state_code TEXT NOT NULL,
    loan_amount REAL NOT NULL,
    property_value REAL NOT NULL,
    annual_income REAL NOT NULL,
    approved INTEGER NOT NULL,
    approval_probability REAL NOT NULL,
    predicted_base_interest_rate REAL NOT NULL,
    fraud_risk_level TEXT NOT NULL,
    bureau TEXT NOT NULL,
    credit_score INTEGER NOT NULL,
    offers_count INTEGER NOT NULL,
    response_json TEXT NOT NULL
);
"""


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute(SCHEMA)


def insert_application(application_id: str, created_at: str, request, response: dict):
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO applications
               (id, created_at, applicant_name, applicant_email, state_code, loan_amount,
                property_value, annual_income, approved, approval_probability,
                predicted_base_interest_rate, fraud_risk_level, bureau, credit_score,
                offers_count, response_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                application_id,
                created_at,
                request.applicant_name,
                request.applicant_email,
                request.state_code,
                request.loan_amount,
                request.property_value,
                request.annual_income,
                int(response["approved"]),
                response["approval_probability"],
                response["predicted_base_interest_rate"],
                response["ai_intelligence_layer"]["fraud_detection"]["risk_level"],
                response["credit_report"]["bureau"],
                response["credit_report"]["score"],
                len(response["offers"]),
                json.dumps(response),
            ),
        )


def get_application(application_id: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute("SELECT response_json FROM applications WHERE id = ?", (application_id,)).fetchone()
    return json.loads(row["response_json"]) if row else None


def list_applications(limit: int = 25) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT id, created_at, applicant_name, state_code, loan_amount, approved,
                      approval_probability, predicted_base_interest_rate, fraud_risk_level,
                      bureau, credit_score, offers_count
               FROM applications ORDER BY created_at DESC LIMIT ?""",
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]
