from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import db, inference
from app.routers import aggregator, bias, loans

app = FastAPI(
    title="CapitalMind AI — Loan Marketplace API",
    description="AI marketplace for personalized loan offers: fraud screening, "
    "approval prediction, interest-rate prediction, multi-lender recommendation, "
    "and bias/fairness auditing, all trained on real CFPB/HMDA and ULB transaction data.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(loans.router)
app.include_router(aggregator.router)
app.include_router(bias.router)


@app.on_event("startup")
def on_startup():
    db.init_db()


@app.get("/api/health")
def health():
    return {"status": "ok", "models": inference.model_health()}
