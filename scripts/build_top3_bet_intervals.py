import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.analyses import compute_top3_bet_interval_summary, compute_top3_bet_intervals
from src.config import PROCESSED_DIR


def load_bet_transactions():
    return pd.read_csv(
        PROCESSED_DIR / "bet_transactions.csv.gz",
        usecols=["txId", "timestamp", "addressId", "satoshiAddress", "diceName"],
        dtype={
            "txId": "int64",
            "timestamp": "int64",
            "addressId": "int64",
            "satoshiAddress": "string",
            "diceName": "string",
        },
    )


def main():
    print("Loading processed bet transactions...", flush=True)
    bet_transactions = load_bet_transactions()

    print("Loading address popularity data...", flush=True)
    address_popularity = pd.read_csv(PROCESSED_DIR / "address_popularity.csv")

    print("Computing top-3 bet intervals...", flush=True)
    bet_intervals = compute_top3_bet_intervals(bet_transactions, address_popularity)

    print("Building top-3 bet interval summary...", flush=True)
    summary = compute_top3_bet_interval_summary(bet_intervals)

    intervals_path = PROCESSED_DIR / "top3_bet_intervals.csv.gz"
    summary_path = PROCESSED_DIR / "top3_bet_interval_summary.csv"

    print(f"Saving {intervals_path}...", flush=True)
    bet_intervals.to_csv(intervals_path, index=False, compression="gzip")

    print(f"Saving {summary_path}...", flush=True)
    summary.to_csv(summary_path, index=False)

    print(f"Saved {len(bet_intervals)} top-3 bet interval rows.", flush=True)


if __name__ == "__main__":
    main()
