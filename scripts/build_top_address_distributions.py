import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.analyses import compute_top_address_bet_distributions
from src.config import PROCESSED_DIR


def load_bet_transactions():
    return pd.read_csv(
        PROCESSED_DIR / "bet_transactions.csv.gz",
        usecols=["txId", "timestamp", "addressId", "diceName"],
        dtype={
            "txId": "int64",
            "timestamp": "int64",
            "addressId": "int64",
            "diceName": "string",
        },
    )


def main():
    print("Loading processed bet transactions...", flush=True)
    bet_transactions = load_bet_transactions()

    print("Loading address popularity data...", flush=True)
    address_popularity = pd.read_csv(PROCESSED_DIR / "address_popularity.csv")

    print("Computing top-3 address bet distributions...", flush=True)
    distributions = compute_top_address_bet_distributions(
        bet_transactions, address_popularity, n=3
    )

    for period_name, df in distributions.items():
        output_path = PROCESSED_DIR / f"top3_bet_distribution_by_{period_name}.csv"
        print(f"Saving {output_path}...", flush=True)
        df.to_csv(output_path, index=False)

    print("Saved top-3 address distribution files.", flush=True)


if __name__ == "__main__":
    main()
