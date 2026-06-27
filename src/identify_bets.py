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

    return bet_outputs[
        ["txId", "position", "addressId", "satoshiAddress", "diceName", "betAmountBtc"]
    ]


def build_bet_transactions(transactions, bet_outputs):
    """Attach transaction metadata to SatoshiDice bet outputs."""
    transaction_metadata = transactions[transactions["isCoinbase"] == 0].copy()

    if transaction_metadata["txId"].duplicated().any():
        raise ValueError("Duplicate non-coinbase txId values found.")

    bet_transactions = bet_outputs.merge(
        transaction_metadata,
        on="txId",
        how="left",
        validate="many_to_one",
    )

    bet_transactions["feeBtc"] = bet_transactions["fee"] / SATOSHI_PER_BTC

    ordered_columns = [
        "txId",
        "timestamp",
        "blockId",
        "feeBtc",
        "position",
        "addressId",
        "satoshiAddress",
        "diceName",
        "betAmountBtc",
    ]

    return bet_transactions[ordered_columns].sort_values(
        ["timestamp", "txId", "position"], ignore_index=True
    )


def build_identification_report(
    transactions,
    bet_outputs,
    bet_transactions,
):
    """Build basic sanity-check metrics for the bet identification step."""
    return {
        "total_transactions": len(transactions),
        "coinbase_transactions": int(transactions["isCoinbase"].sum()),
        "non_coinbase_transactions": int((transactions["isCoinbase"] == 0).sum()),
        "satoshi_bet_outputs": len(bet_outputs),
        "bet_transactions": int(bet_transactions["txId"].nunique()),
    }


def identify_bets(transactions, outputs, mapping, dice_infos):
    satoshi_addresses = map_satoshi_addresses(dice_infos, mapping)
    bet_outputs = identify_satoshi_bet_outputs(outputs, satoshi_addresses)
    bet_transactions = build_bet_transactions(transactions, bet_outputs)
    report = build_identification_report(
        transactions,
        bet_outputs,
        bet_transactions,
    )

    return {
        "satoshi_addresses": satoshi_addresses,
        "satoshi_bet_outputs": bet_outputs,
        "bet_transactions": bet_transactions,
        "report": report,
    }
