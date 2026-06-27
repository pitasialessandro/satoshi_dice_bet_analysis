from datetime import datetime, timezone
from pathlib import Path
from time import sleep

import pandas as pd
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


WALLET_CACHE_COLUMNS = [
    "address",
    "walletId",
    "walletName",
    "walletUrl",
    "lookupStatus",
    "error",
    "scrapedAt",
]


def build_top_chain_members(chains, simple_bets, edges):
    simple_bet_by_tx = simple_bets.set_index("txId")
    child_by_source = dict(edges[["sourceTxId", "targetTxId"]].itertuples(index=False, name=None))

    rows = []
    for chain_rank, chain in enumerate(chains.itertuples(index=False), start=1):
        current_tx_id = int(chain.startTxId)

        for position in range(1, int(chain.chainLength) + 1):
            bet = simple_bet_by_tx.loc[current_tx_id]
            rows.append(
                {
                    "chainRank": chain_rank,
                    "chainId": int(chain.chainId),
                    "chainLength": int(chain.chainLength),
                    "positionInChain": position,
                    "txId": current_tx_id,
                    "timestamp": int(bet["timestamp"]),
                    "inputAddressId": int(bet["inputAddressId"]),
                    "changeAddressId": int(bet["changeAddressId"]),
                }
            )

            if current_tx_id == int(chain.endTxId):
                break

            next_tx_id = child_by_source.get(current_tx_id)
            if next_tx_id is None:
                raise ValueError(f"Broken chain at txId {current_tx_id}.")
            current_tx_id = int(next_tx_id)

    return pd.DataFrame(rows)


def load_mapping_for_address_ids(mapping_path, address_ids, chunksize=1_000_000):
    wanted_ids = set(int(address_id) for address_id in address_ids)
    chunks = []
    found_ids = set()

    for chunk in pd.read_csv(
        mapping_path,
        header=None,
        usecols=[0, 1],
        names=["address", "addressId"],
        dtype={"address": "string", "addressId": "int64"},
        chunksize=chunksize,
    ):
        matches = chunk[chunk["addressId"].isin(wanted_ids)]
        if not matches.empty:
            chunks.append(matches)
            found_ids.update(matches["addressId"].astype("int64"))

        if len(found_ids) == len(wanted_ids):
            break

    if not chunks:
        return pd.DataFrame(columns=["addressId", "address"])

    return pd.concat(chunks, ignore_index=True).drop_duplicates("addressId")


def build_top_chain_addresses(chain_members, mapping):
    input_addresses = chain_members[
        ["chainRank", "chainId", "chainLength", "positionInChain", "inputAddressId"]
    ].rename(columns={"inputAddressId": "addressId"})
    input_addresses["addressRole"] = "input"

    change_addresses = chain_members[
        ["chainRank", "chainId", "chainLength", "positionInChain", "changeAddressId"]
    ].rename(columns={"changeAddressId": "addressId"})
    change_addresses["addressRole"] = "change"

    addresses = pd.concat([input_addresses, change_addresses], ignore_index=True)
    addresses = addresses.groupby(
        ["chainRank", "chainId", "chainLength", "addressId"], as_index=False
    ).agg(
        firstPositionInChain=("positionInChain", "min"),
        addressRole=("addressRole", lambda values: ",".join(sorted(set(values)))),
    )

    return addresses.merge(
        mapping,
        on="addressId",
        how="left",
        validate="many_to_one",
    ).sort_values(
        ["chainRank", "firstPositionInChain", "addressId"], ignore_index=True
    )


def load_wallet_cache(cache_path):
    if Path(cache_path).exists():
        return pd.read_csv(cache_path, dtype="string")
    return pd.DataFrame(columns=WALLET_CACHE_COLUMNS)


def save_wallet_cache(cache, cache_path):
    cache[WALLET_CACHE_COLUMNS].to_csv(cache_path, index=False)


def scrape_wallet_for_address(driver, address, wait_seconds=8):
    url = f"https://www.walletexplorer.com/address/{address}"
    scraped_at = datetime.now(timezone.utc).isoformat()

    try:
        driver.get(url)
        WebDriverWait(driver, wait_seconds).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
        )

        try:
            wallet_item = driver.find_element(By.CSS_SELECTOR, "span.wallet_renamer_item")
        except NoSuchElementException:
            return {
                "address": address,
                "walletId": None,
                "walletName": None,
                "walletUrl": None,
                "lookupStatus": "not_found",
                "error": None,
                "scrapedAt": scraped_at,
            }

        wallet_link = wallet_item.find_element(By.CSS_SELECTOR, "a")
        wallet_name = wallet_item.find_element(By.CSS_SELECTOR, "span.wallet_name")

        return {
            "address": address,
            "walletId": wallet_item.get_attribute("data-wallet-id"),
            "walletName": wallet_name.text,
            "walletUrl": wallet_link.get_attribute("href"),
            "lookupStatus": "ok",
            "error": None,
            "scrapedAt": scraped_at,
        }
    except TimeoutException as exc:
        return _wallet_error_row(address, "timeout", exc, scraped_at)
    except Exception as exc:
        return _wallet_error_row(address, "error", exc, scraped_at)


def _wallet_error_row(address, status, exc, scraped_at):
    return {
        "address": address,
        "walletId": None,
        "walletName": None,
        "walletUrl": None,
        "lookupStatus": status,
        "error": str(exc)[:500],
        "scrapedAt": scraped_at,
    }


def scrape_missing_wallets(driver, addresses, cache, cache_path, request_sleep_seconds=0.2):
    cached_addresses = set(cache.loc[cache["lookupStatus"].isin(["ok", "not_found"]), "address"])
    addresses_to_scrape = [address for address in addresses if address not in cached_addresses]

    for index, address in enumerate(addresses_to_scrape, start=1):
        print(f"[{index}/{len(addresses_to_scrape)}] Scraping {address}...", flush=True)
        result = scrape_wallet_for_address(driver, address)
        cache = pd.concat([cache, pd.DataFrame([result])], ignore_index=True)
        cache = cache.drop_duplicates("address", keep="last")
        save_wallet_cache(cache, cache_path)
        sleep(request_sleep_seconds)

    return cache


def summarize_chain_wallets(chain_addresses, wallet_cache):
    resolved = chain_addresses.merge(
        wallet_cache,
        on="address",
        how="left",
        validate="many_to_one",
    )

    rows = []
    for (chain_rank, chain_id, chain_length), group in resolved.groupby(
        ["chainRank", "chainId", "chainLength"], sort=True
    ):
        ok = group[group["lookupStatus"] == "ok"]
        wallet_counts = ok.groupby(["walletId", "walletName"], dropna=False).size()

        if wallet_counts.empty:
            dominant_wallet_id = None
            dominant_wallet_name = None
            dominant_count = 0
            dominant_share = 0
            distinct_wallets = 0
        else:
            wallet_counts = wallet_counts.sort_values(ascending=False)
            dominant_wallet_id, dominant_wallet_name = wallet_counts.index[0]
            dominant_count = int(wallet_counts.iloc[0])
            dominant_share = dominant_count / len(ok)
            distinct_wallets = int(ok["walletId"].nunique())

        rows.append(
            {
                "chainRank": chain_rank,
                "chainId": chain_id,
                "chainLength": chain_length,
                "addresses": len(group),
                "resolvedAddresses": len(ok),
                "unresolvedAddresses": int((group["lookupStatus"] != "ok").sum()),
                "distinctWallets": distinct_wallets,
                "dominantWalletId": dominant_wallet_id,
                "dominantWalletName": dominant_wallet_name,
                "dominantWalletAddressCount": dominant_count,
                "dominantWalletShare": dominant_share,
                "conclusion": _wallet_conclusion(len(group), len(ok), distinct_wallets, dominant_share),
            }
        )

    return pd.DataFrame(rows)


def _wallet_conclusion(total_addresses, resolved_addresses, distinct_wallets, dominant_share):
    if resolved_addresses == 0 or resolved_addresses / total_addresses < 0.5:
        return "inconclusive"
    if distinct_wallets == 1 and resolved_addresses == total_addresses:
        return "single_wallet"
    if dominant_share >= 0.9:
        return "mostly_single_wallet"
    return "multiple_wallets"
