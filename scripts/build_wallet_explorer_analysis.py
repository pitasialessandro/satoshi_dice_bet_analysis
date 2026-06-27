import sys
from pathlib import Path

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import MAPPING_PATH, PROCESSED_DIR
from src.walletexplorer import (
    build_top_chain_addresses,
    build_top_chain_members,
    load_mapping_for_address_ids,
    load_wallet_cache,
    save_wallet_cache,
    scrape_missing_wallets,
    summarize_chain_wallets,
)


TOP_H = 10
REQUEST_SLEEP_SECONDS = 0


def load_simple_bets():
    return pd.read_csv(
        PROCESSED_DIR / "simple_bets.csv.gz",
        usecols=["txId", "timestamp", "inputAddressId", "changeAddressId"],
        dtype={
            "txId": "int64",
            "timestamp": "int64",
            "inputAddressId": "int64",
            "changeAddressId": "int64",
        },
    )


def load_chain_edges():
    return pd.read_csv(
        PROCESSED_DIR / "simple_bet_chain_edges.csv.gz",
        dtype={"sourceTxId": "int64", "targetTxId": "int64"},
    )


def build_chrome_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=options)


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Loading top {TOP_H} simple-bet chains...", flush=True)
    chains = pd.read_csv(PROCESSED_DIR / "simple_bet_chains.csv", nrows=TOP_H)

    print("Loading simple bets and chain edges...", flush=True)
    simple_bets = load_simple_bets()
    edges = load_chain_edges()

    print("Building top-chain member table...", flush=True)
    chain_members = build_top_chain_members(chains, simple_bets, edges)
    members_path = PROCESSED_DIR / "top_chain_members.csv.gz"
    chain_members.to_csv(members_path, index=False, compression="gzip")
    print(f"Saved {members_path}", flush=True)

    address_ids = pd.unique(
        pd.concat(
            [chain_members["inputAddressId"], chain_members["changeAddressId"]],
            ignore_index=True,
        )
    )

    print("Mapping chain addressIds to Bitcoin addresses...", flush=True)
    mapping = load_mapping_for_address_ids(MAPPING_PATH, address_ids)
    chain_addresses = build_top_chain_addresses(chain_members, mapping)
    addresses_path = PROCESSED_DIR / "top_chain_addresses.csv"
    chain_addresses.to_csv(addresses_path, index=False)
    print(f"Saved {addresses_path}", flush=True)

    missing_addresses = chain_addresses["address"].isna().sum()
    if missing_addresses:
        print(f"Warning: {missing_addresses} addressIds were not found in mapping.csv", flush=True)

    cache_path = PROCESSED_DIR / "walletexplorer_address_wallets.csv"
    wallet_cache = load_wallet_cache(cache_path)
    save_wallet_cache(wallet_cache, cache_path)

    addresses = list(chain_addresses["address"].dropna().drop_duplicates())
    print(f"WalletExplorer addresses to check: {len(addresses)}", flush=True)

    print("Starting Chrome WebDriver...", flush=True)
    driver = build_chrome_driver()
    try:
        wallet_cache = scrape_missing_wallets(
            driver,
            addresses,
            wallet_cache,
            cache_path,
            request_sleep_seconds=REQUEST_SLEEP_SECONDS,
        )
    finally:
        driver.quit()

    print("Building wallet summary by chain...", flush=True)
    summary = summarize_chain_wallets(chain_addresses, wallet_cache)
    summary_path = PROCESSED_DIR / "top_chain_wallet_summary.csv"
    summary.to_csv(summary_path, index=False)
    print(f"Saved {summary_path}", flush=True)

    print("Done.", flush=True)


if __name__ == "__main__":
    main()
