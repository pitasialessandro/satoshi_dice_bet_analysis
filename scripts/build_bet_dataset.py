import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import PROCESSED_DIR
from src.identify_bets import identify_bets
from src.load_data import (
    load_mapping,
    load_outputs,
    load_satoshi_dice_infos,
    load_transactions,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Build intermediate SatoshiDice bet datasets."
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=None,
        help="Read only the first N rows from transactions and outputs.",
    )
    parser.add_argument(
        "--sample-mapping",
        type=int,
        default=None,
        help="Read only the first N mapping rows. results will not be accurate.",
    )
    return parser.parse_args()


def save_results(result, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)

    result["satoshi_addresses"].to_csv(
        output_dir / "satoshi_addresses.csv", index=False
    )
    result["satoshi_bet_outputs"].to_csv(
        output_dir / "satoshi_bet_outputs.csv.gz", index=False, compression="gzip"
    )
    result["bet_transactions"].to_csv(
        output_dir / "bet_transactions.csv.gz", index=False, compression="gzip"
    )

    with (output_dir / "identification_report.json").open("w", encoding="utf-8") as f:
        json.dump(result["report"], f, indent=2)


def print_report(report):
    print("\nIdentification report", flush=True)
    for key, value in report.items():
        print(f"{key}: {value}", flush=True)


def main():
    args = parse_args()

    if args.sample is None:
        print("Running on complete transactions and outputs datasets.", flush=True)
    else:
        print(f"Running in sample mode with first {args.sample} rows.", flush=True)

    if args.sample_mapping is not None:
        print(
            f"Mapping is also sampled to first {args.sample_mapping} rows. "
            "Use this only for smoke tests.",
            flush=True,
        )

    print("Loading transactions...", flush=True)
    transactions = load_transactions(nrows=args.sample)

    print("Loading outputs...", flush=True)
    outputs = load_outputs(nrows=args.sample)

    print("Loading mapping...", flush=True)
    mapping = load_mapping(nrows=args.sample_mapping)

    print("Loading SatoshiDice address infos...", flush=True)
    dice_infos = load_satoshi_dice_infos()

    print("Identifying SatoshiDice bets...", flush=True)
    result = identify_bets(transactions, outputs, mapping, dice_infos)

    print_report(result["report"])

    print("\nSaving intermediate datasets...", flush=True)
    output_dir = PROCESSED_DIR
    if args.sample is not None or args.sample_mapping is not None:
        output_dir = PROCESSED_DIR / "sample"

    save_results(result, output_dir)

    print(f"Saved files in: {output_dir}", flush=True)


if __name__ == "__main__":
    main()
