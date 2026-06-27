import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.analyses import (
    compute_top3_fee_amount_correlation,
    compute_top3_fee_amount_points,
)
from src.config import PROCESSED_DIR


def load_bet_transactions():
    return pd.read_csv(
        PROCESSED_DIR / "bet_transactions.csv.gz",
        usecols=[
            "txId",
            "addressId",
            "diceName",
            "betAmountBtc",
            "feeBtc",
        ],
        dtype={
            "txId": "int64",
            "addressId": "int64",
            "diceName": "string",
            "betAmountBtc": "float64",
            "feeBtc": "float64",
        },
    )


def main():
    print("Loading processed bet transactions...", flush=True)
    bet_transactions = load_bet_transactions()

    print("Loading address popularity data...", flush=True)
    address_popularity = pd.read_csv(PROCESSED_DIR / "address_popularity.csv")

    print("Building top-3 fee/amount points...", flush=True)
    points = compute_top3_fee_amount_points(bet_transactions, address_popularity)

    print("Computing fee/amount correlations...", flush=True)
    summary = compute_top3_fee_amount_correlation(points)

    points_path = PROCESSED_DIR / "top3_fee_amount_points.csv.gz"
    summary_path = PROCESSED_DIR / "top3_fee_amount_correlation.csv"

    print(f"Saving {points_path}...", flush=True)
    points.to_csv(points_path, index=False, compression="gzip")

    print(f"Saving {summary_path}...", flush=True)
    summary.to_csv(summary_path, index=False)

    print(f"Saved {len(points)} top-3 fee/amount points.", flush=True)


if __name__ == "__main__":
    main()
