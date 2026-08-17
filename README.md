# CapitalMind AI — Loan Marketplace MVP

An AI marketplace for personalized loan offers: fraud screening, approval
prediction, interest-rate pricing, multi-lender recommendation, and bias
auditing — trained on real public data, not synthetic placeholders.

- **Backend**: Python (FastAPI) + XGBoost + SHAP + fairlearn, SQLite storage
- **Frontend**: Next.js 16 (App Router, TypeScript, Tailwind, Recharts)

## Real data used

| Dataset | Source | Size | Used for |
|---|---|---|---|
| HMDA 2023 loan-level data | CFPB / FFIEC Data Browser API (9 small states: VT, DE, WY, ND, SD, MT, RI, AK, DC) | 206,810 applications | Loan approval + interest-rate models |
| Credit card transactions | ULB/Worldline (via OpenML), the standard Kaggle fraud benchmark | 284,807 transactions, 492 confirmed frauds | Fraud detection model |

Both are re-fetchable via `backend/download_data.sh` (gitignored for size, ~145MB combined).

## Model performance (held-out test sets)

| Model | Metric | Value |
|---|---|---|
| Loan approval (XGBoost classifier) | ROC-AUC | 0.897 |
| Loan approval | Accuracy | 0.887 |
| Interest rate (XGBoost regressor) | MAE | 0.69 points |
| Interest rate | R² | 0.548 |
| Fraud detection (XGBoost classifier) | ROC-AUC | 0.983 |
| Fraud detection | Average precision | 0.866 |

## How this maps to the review feedback

- **(a) Market sizing / competitors** — not a code deliverable; belongs in the
  pitch narrative (LendingTree, Even Financial, Credible are the closest
  comparable US marketplaces — worth researching current TAM figures for the deck).
- **(b) CFPB Section 1033 / aggregator security** — `app/aggregator_mock.py`
  simulates a scoped-consent, 1033-shaped aggregator (issue token → pull
  accounts/credit report). It's a mock (real aggregators like Plaid/Finicity
  require paid contracts), built so swapping in a real one is a drop-in
  replacement, not a redesign.
- **(c) AI Intelligence Layer, fraud first, 1×5** — `AIIntelligenceLayer.tsx`
  renders exactly that: Fraud Detection → Loan Approval → Interest Rate
  Prediction → Recommendation System → Bias/Fairness Check.
- **(d) Credit bureau integration** — the mock aggregator picks one of
  Experian/TransUnion/Equifax per applicant and returns a bureau-shaped report
  (score, inquiries, tradelines, utilization, factors).
- **(e) Bias testing at approval stage** — `ml/bias_audit.py` runs a fairlearn
  audit (demographic parity + equalized odds) across HMDA's disclosed race,
  ethnicity and sex fields. **This surfaced a real finding**: the approval
  model shows a 20.3-point demographic parity gap by race and 14.2 points by
  ethnicity on real 2023 HMDA outcomes — flagged "review" in `/fairness`. This
  reflects disparities in the underlying historical lending data, which is
  itself the point of shipping a bias-audit module.
- **(f) Revenue model** — `ml/personas.py` gives each lender a
  `commission_bps` (revenue point i). Points ii–iv (SaaS licensing, free/premium
  tiers, cross-sell) are business-model decisions for the pitch deck, not
  something an MVP demo needs to render as UI.

## Design choices worth knowing before you present

- **Race/ethnicity/sex are excluded from model inputs** (fair-lending best
  practice) but kept alongside predictions for the bias audit to test
  *outcomes* against — this is why the audit is meaningful rather than circular.
- **The "5 banks" are simulated personas**, not 5 separately trained models.
  Real banks' internal underwriting models aren't public. One shared,
  HMDA-trained risk core gets re-priced and re-thresholded per lender
  (risk appetite, margin, loan cap, processing tier) — the same pattern real
  marketplaces (Even, LendingTree) use over partner banks whose models they
  don't own.
- **HMDA doesn't publish raw FICO scores** (by design, for privacy) — only
  which scoring model was used. The mock bureau's numeric score is informational
  context for the applicant, not a trained model input; the trained models
  only consume what HMDA actually discloses.
- **Training data covers 9 small-population states** (kept the dataset light
  for a local demo). A state outside that set (e.g. CA, NY, TX) still works —
  it just falls through to XGBoost's native missing-value handling for that
  one feature — but accuracy is best validated on the trained states.

## Running it locally

### Backend (port 8000)

```bash
cd backend
python -m venv .venv
./.venv/Scripts/pip install -r requirements.txt   # .venv/bin/pip on macOS/Linux
./download_data.sh                                 # fetches the two real datasets
./.venv/Scripts/python -m ml.train_approval
./.venv/Scripts/python -m ml.train_interest
./.venv/Scripts/python -m ml.train_fraud
./.venv/Scripts/python -m ml.bias_audit
./.venv/Scripts/python -m uvicorn app.main:app --port 8000
```

### Frontend (port 3000)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 — Apply, Application History, and Fairness Dashboard
are all in the nav. The frontend expects the backend at
`http://localhost:8000` (see `frontend/.env.local`).

## Project layout

```
backend/
  ml/                 data_prep, training scripts, personas, SHAP, bias audit
  app/                FastAPI app: inference, aggregator mock, db, routers
  models/             trained model artifacts (committed — small, ~3.5MB)
  data/raw/            gitignored — re-fetch with download_data.sh
frontend/
  app/                /, /history, /fairness
  components/         LoanForm, ResultPanel, AIIntelligenceLayer, charts
  lib/api.ts          typed fetch client for the backend
```
