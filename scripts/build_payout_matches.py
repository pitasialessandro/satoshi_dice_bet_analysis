import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import PROCESSED_DIR
from src.load_data import load_inputs, load_transactions
from src.payouts import build_payout_distance_summary, match_payout_transactions


def load_bet_transactions():
    return pd.read_csv(
        PROCESSED_DIR / "bet_transactions.csv.gz",
        usecols=[
            "txId",
            "position",
            "blockId",
        ],
        dtype={
            "txId": "int64",
            "position": "int16",
            "blockId": "int32",
        },
    )


def main():
    print("Loading inputs...", flush=True)
    inputs = load_inputs()

    print("Loading transactions...", flush=True)
    transactions = load_transactions()

    print("Loading processed bet transactions...", flush=True)
    bet_transactions = load_bet_transactions()

    print("Matching payout transactions via UTXO spends...", flush=True)
    payout_matches = match_payout_transactions(inputs, bet_transactions, transactions)

    print("Building payout distance summary...", flush=True)
    summary = build_payout_distance_summary(
        payout_matches,
        total_bet_transactions=bet_transactions["txId"].nunique(),
    )

    payout_matches_path = PROCESSED_DIR / "payout_matches.csv.gz"
    summary_path = PROCESSED_DIR / "payout_distance_summary.csv"

    print(f"Saving {payout_matches_path}...", flush=True)
    payout_matches.to_csv(payout_matches_path, index=False, compression="gzip")

    print(f"Saving {summary_path}...", flush=True)
    summary.to_csv(summary_path, index=False)

    print(f"Saved {len(payout_matches)} payout links.", flush=True)


if __name__ == "__main__":
    main()
