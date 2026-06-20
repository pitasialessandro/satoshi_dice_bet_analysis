import argparse
import sys
from pathlib import Path

import pandas as pd
import matplotlib

# Anti-grain geometry backend -> generates static images in memory instead of in a GUI
matplotlib.use("Agg")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import FIGURES_DIR, PROCESSED_DIR
from src.plotting import (
    plot_address_popularity_comparison,
    plot_monthly_transactions_vs_bet_share,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Build project figures as PNG files.")
    return parser.parse_args()


def main():
    args = parse_args()

    processed_dir = PROCESSED_DIR
    figures_dir = FIGURES_DIR
    figures_dir.mkdir(parents=True, exist_ok=True)

    print("Loading monthly bet percentage data...", flush=True)
    monthly = pd.read_csv(processed_dir / "bet_percentage_by_month.csv")

    output_path = figures_dir / "monthly_transactions_vs_satoshidice_share.png"
    print(f"Saving {output_path}...", flush=True)
    fig, _ = plot_monthly_transactions_vs_bet_share(monthly, output_path=output_path)
    fig.clear()

    print("Loading address popularity data...", flush=True)
    address_popularity = pd.read_csv(processed_dir / "address_popularity.csv")

    output_path = figures_dir / "address_popularity_comparison.png"
    print(f"Saving {output_path}...", flush=True)
    fig, _ = plot_address_popularity_comparison(
        address_popularity, output_path=output_path
    )
    fig.clear()

    print(f"Saved figures in: {figures_dir}", flush=True)


if __name__ == "__main__":
    main()
