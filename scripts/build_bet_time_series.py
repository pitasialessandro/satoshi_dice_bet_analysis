import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.analyses import compute_bet_percentages_for_default_periods
from src.config import PROCESSED_DIR
from src.load_data import load_transactions


def parse_args():
    parser = argparse.ArgumentParser(
        description="Build bet percentage time series by day, week, and month."
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=None,
        help="Read only the first N rows from transactions and use processed sample bets.",
    )
    return parser.parse_args()


def load_bet_transactions(output_dir):
    return pd.read_csv(
        output_dir / "bet_transactions.csv.gz",
        usecols=["txId", "timestamp"],
        dtype={"txId": "int64", "timestamp": "int64"},
    )


def save_time_series(results, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    for period_name, df in results.items():
        df.to_csv(output_dir / f"bet_percentage_by_{period_name}.csv", index=False)


def main():
    args = parse_args()
    output_dir = PROCESSED_DIR / "sample" if args.sample is not None else PROCESSED_DIR

    if args.sample is None:
        print("Running on complete transactions and processed bets.", flush=True)
    else:
        print(
            f"Running in sample mode with first {args.sample} transactions rows.",
            flush=True,
        )

    print("Loading transactions...", flush=True)
    transactions = load_transactions(nrows=args.sample)

    print("Loading processed bet transactions...", flush=True)
    bet_transactions = load_bet_transactions(output_dir)

    print("Computing bet percentages by period...", flush=True)
    results = compute_bet_percentages_for_default_periods(transactions, bet_transactions)

    print("Saving time series CSV files...", flush=True)
    save_time_series(results, output_dir)

    for period_name, df in results.items():
        print(f"{period_name}: {len(df)} periods", flush=True)

    print(f"Saved files in: {output_dir}", flush=True)


if __name__ == "__main__":
    main()
