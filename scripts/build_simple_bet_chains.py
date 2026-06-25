import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import PROCESSED_DIR
from src.load_data import load_inputs, load_outputs
from src.simple_bet_chains import (
    build_chain_length_distribution,
    build_simple_bet_chain_summaries,
    build_simple_bet_chain_summary,
    build_simple_bet_edges,
    build_simple_bets,
    get_most_popular_satoshi_address,
)


def load_bet_transactions():
    return pd.read_csv(
        PROCESSED_DIR / "bet_transactions.csv.gz",
        usecols=[
            "txId",
            "timestamp",
            "datetime",
            "blockId",
            "fee",
            "feeBtc",
            "position",
            "addressId",
            "satoshiAddress",
            "diceName",
            "betAmount",
            "betAmountBtc",
        ],
        dtype={
            "txId": "int64",
            "timestamp": "int64",
            "datetime": "string",
            "blockId": "int32",
            "fee": "int64",
            "feeBtc": "float64",
            "position": "int16",
            "addressId": "int64",
            "satoshiAddress": "string",
            "diceName": "string",
            "betAmount": "int64",
            "betAmountBtc": "float64",
        },
    )


def main():
    print("Loading address popularity data...", flush=True)
    address_popularity = pd.read_csv(PROCESSED_DIR / "address_popularity.csv")
    top_address = get_most_popular_satoshi_address(address_popularity)
    print(
        f"Using most popular SatoshiDice address: {top_address['diceName']} "
        f"({top_address['satoshiAddress']})",
        flush=True,
    )

    print("Loading processed bet transactions...", flush=True)
    bet_transactions = load_bet_transactions()

    print("Loading inputs...", flush=True)
    inputs = load_inputs()

    print("Loading outputs...", flush=True)
    outputs = load_outputs()

    print("Building simple bets...", flush=True)
    simple_bets = build_simple_bets(
        inputs,
        outputs,
        bet_transactions,
        address_popularity,
    )

    print("Building simple-bet chain edges...", flush=True)
    edges = build_simple_bet_edges(simple_bets)

    print("Building simple-bet chain summaries...", flush=True)
    chain_summaries = build_simple_bet_chain_summaries(simple_bets, edges)
    length_distribution = build_chain_length_distribution(chain_summaries)
    summary = build_simple_bet_chain_summary(simple_bets, edges, chain_summaries)

    simple_bets_path = PROCESSED_DIR / "simple_bets.csv.gz"
    edges_path = PROCESSED_DIR / "simple_bet_chain_edges.csv.gz"
    chains_path = PROCESSED_DIR / "simple_bet_chains.csv"
    lengths_path = PROCESSED_DIR / "simple_bet_chain_lengths.csv"
    summary_path = PROCESSED_DIR / "simple_bet_chain_summary.csv"

    print(f"Saving {simple_bets_path}...", flush=True)
    simple_bets.to_csv(simple_bets_path, index=False, compression="gzip")

    print(f"Saving {edges_path}...", flush=True)
    edges.to_csv(edges_path, index=False, compression="gzip")

    print(f"Saving {chains_path}...", flush=True)
    chain_summaries.to_csv(chains_path, index=False)

    print(f"Saving {lengths_path}...", flush=True)
    length_distribution.to_csv(lengths_path, index=False)

    print(f"Saving {summary_path}...", flush=True)
    summary.to_csv(summary_path, index=False)

    print(
        f"Saved {len(simple_bets)} simple bets, {len(edges)} chain edges, "
        f"and {len(chain_summaries)} chains.",
        flush=True,
    )


if __name__ == "__main__":
    main()
