import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.analyses import compute_address_popularity
from src.config import PROCESSED_DIR


def load_bet_transactions():
    return pd.read_csv(
        PROCESSED_DIR / "bet_transactions.csv.gz",
        usecols=[
            "txId",
            "addressId",
            "satoshiAddress",
            "diceName",
            "betAmountBtc",
        ],
        dtype={
            "txId": "int64",
            "addressId": "int64",
            "satoshiAddress": "string",
            "diceName": "string",
            "betAmountBtc": "float64",
        },
    )


def main():
    print("Loading processed bet transactions...", flush=True)
    bet_transactions = load_bet_transactions()

    print("Loading SatoshiDice address lookup...", flush=True)
    satoshi_addresses = pd.read_csv(PROCESSED_DIR / "satoshi_addresses.csv")

    print("Computing address popularity...", flush=True)
    popularity = compute_address_popularity(bet_transactions, satoshi_addresses)

    output_path = PROCESSED_DIR / "address_popularity.csv"
    print(f"Saving {output_path}...", flush=True)
    popularity.to_csv(output_path, index=False)

    print(f"Saved {len(popularity)} address rows.", flush=True)


if __name__ == "__main__":
    main()
