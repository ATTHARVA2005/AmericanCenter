#!/usr/bin/env bash
# Re-fetches the two real datasets the models are trained on. Not needed if
# data/raw/ already has them (they're gitignored for size, ~145MB combined).
set -e
mkdir -p data/raw

echo "Fetching CFPB/HMDA 2023 loan-level data (9 small states)..."
curl -sL --compressed \
  "https://ffiec.cfpb.gov/v2/data-browser-api/view/csv?states=VT,DE,WY,ND,SD,MT,RI,AK,DC&years=2023&actions_taken=1,2,3,4,5" \
  --http1.1 --max-time 300 -o data/raw/hmda_2023_multistate.csv

echo "Fetching ULB/Worldline credit card fraud dataset (via OpenML)..."
curl -sL "https://data.openml.org/datasets/0000/1597/dataset_1597.pq" \
  --max-time 300 -o data/raw/creditcard_fraud.parquet

echo "Done. Run the training scripts next:"
echo "  python -m ml.train_approval && python -m ml.train_interest && python -m ml.train_fraud && python -m ml.bias_audit"
