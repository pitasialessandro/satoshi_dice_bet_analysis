import pandas as pd

from src.config import SATOSHI_PER_BTC


def map_satoshi_addresses(dice_infos, mapping):
    """Map SatoshiDice Bitcoin addresses to dataset addressId values."""
    satoshi_addresses = dice_infos.merge(
        mapping,
        left_on="Address",
        right_on="hash",
        how="left",
        validate="one_to_one",
    )

    return satoshi_addresses.drop(columns=["hash"])


def identify_satoshi_bet_outputs(outputs, satoshi_addresses):
    """Return outputs whose destination address is a known SatoshiDice address."""
    address_columns = [
        "addressId",
        "Address",
        "Name",
        "WinOdds",
        "PriceMultiplier",
        "HousePercentage",
        "ExpectReturn",
        "MinimumBet",
        "MaximumBet",
    ]
    known_addresses = satoshi_addresses.dropna(subset=["addressId"])[address_columns]
    known_addresses = known_addresses.astype({"addressId": "int64"})

    bet_outputs = outputs.merge(
        known_addresses,
        on="addressId",
        how="inner",
        validate="many_to_one",
    )
    bet_outputs = bet_outputs.rename(
        columns={
            "amount": "betAmount",
            "Address": "satoshiAddress",
            "Name": "diceName",
        }
    )
    bet_outputs["betAmountBtc"] = bet_outputs["betAmount"] / SATOSHI_PER_BTC

    return bet_outputs


def build_bet_transactions(transactions, bet_outputs, exclude_coinbase=True):
    """Attach transaction metadata to SatoshiDice bet outputs."""
    transaction_metadata = transactions
    if exclude_coinbase:
        transaction_metadata = transactions[transactions["isCoinbase"] == 0].copy()

    # txId should be unique but this wasn't true due to 2 faulty historical coinbase transactions (txId = 142572, 142726)
    # not a problem for the project since we are ignoring coinbase transactions
    # if transaction_metadata["txId"].duplicated().any():
    #     transaction_metadata = transaction_metadata.drop_duplicates("txId", keep="first")

    bet_transactions = bet_outputs.merge(
        transaction_metadata,
        on="txId",
        how="left",
        validate="many_to_one",
    )

    bet_transactions["datetime"] = pd.to_datetime(
        bet_transactions["timestamp"], unit="s", utc=True
    )
    bet_transactions["feeBtc"] = bet_transactions["fee"] / SATOSHI_PER_BTC

    ordered_columns = [
        "txId",
        "timestamp",
        "datetime",
        "blockId",
        "isCoinbase",
        "fee",
        "feeBtc",
        "position",
        "addressId",
        "satoshiAddress",
        "diceName",
        "betAmount",
        "betAmountBtc",
        "WinOdds",
        "PriceMultiplier",
        "HousePercentage",
        "ExpectReturn",
        "MinimumBet",
        "MaximumBet",
    ]

    return bet_transactions[ordered_columns].sort_values(
        ["timestamp", "txId", "position"], ignore_index=True
    )


def build_identification_report(
    transactions,
    satoshi_addresses,
    bet_outputs,
    candidate_bet_transactions,
    bet_transactions,
):
    """Build basic sanity-check metrics for the bet identification step."""
    coinbase_tx_ids = set(transactions.loc[transactions["isCoinbase"] == 1, "txId"])
    candidate_tx_ids = set(bet_outputs["txId"])

    return {
        "total_transactions": len(transactions),
        "coinbase_transactions": int(transactions["isCoinbase"].sum()),
        "non_coinbase_transactions": int((transactions["isCoinbase"] == 0).sum()),
        "satoshi_addresses_total": len(satoshi_addresses),
        "satoshi_addresses_found_in_mapping": int(satoshi_addresses["addressId"].notna().sum()),
        "satoshi_addresses_missing_in_mapping": int(satoshi_addresses["addressId"].isna().sum()),
        "satoshi_bet_outputs": len(bet_outputs),
        "candidate_bet_transactions": len(candidate_tx_ids),
        "candidate_bet_transactions_coinbase": len(candidate_tx_ids & coinbase_tx_ids),
        "bet_transactions_non_coinbase": int(bet_transactions["txId"].nunique()),
    }


def identify_bets(transactions, outputs, mapping, dice_infos):
    satoshi_addresses = map_satoshi_addresses(dice_infos, mapping)
    bet_outputs = identify_satoshi_bet_outputs(outputs, satoshi_addresses)
    # TODO: remove this candidates since we don't need it for analysis, as well is confusing with the "candidate_bet_transactions" in the report since they mean 2 different things
    candidate_bet_transactions = build_bet_transactions(
        transactions, bet_outputs, exclude_coinbase=False
    )
    bet_transactions = build_bet_transactions(transactions, bet_outputs, exclude_coinbase=True)
    report = build_identification_report(
        transactions,
        satoshi_addresses,
        bet_outputs,
        candidate_bet_transactions,
        bet_transactions,
    )

    return {
        "satoshi_addresses": satoshi_addresses,
        "satoshi_bet_outputs": bet_outputs,
        "candidate_bet_transactions": candidate_bet_transactions,
        "bet_transactions": bet_transactions,
        "report": report,
    }
