import pandas as pd


def match_payout_transactions(inputs, bet_transactions, transactions):
    bet_outputs = bet_transactions[
        [
            "txId",
            "position",
            "timestamp",
            "blockId",
            "addressId",
            "satoshiAddress",
            "diceName",
            "betAmountBtc",
        ]
    ].rename(
        columns={
            "txId": "betTxId",
            "position": "betOutputPosition",
            "timestamp": "betTimestamp",
            "blockId": "betBlockId",
        }
    )

    input_spends = inputs.rename(columns={"txId": "payoutTxId"})
    payout_matches = input_spends.merge(
        bet_outputs,
        left_on=["prevTxId", "prevTxpos"],
        right_on=["betTxId", "betOutputPosition"],
        how="inner",
        validate="many_to_one",
    )

    transaction_metadata = transactions[transactions["isCoinbase"] == 0].copy()
    if transaction_metadata["txId"].duplicated().any():
        raise ValueError("Duplicate non-coinbase txId values found.")

    # find metadata related to input transactions
    # we already have metadata for bet transactions from bet_outputs
    payout_metadata = transaction_metadata[
        ["txId", "timestamp", "blockId", "fee"]
    ].rename(
        columns={
            "txId": "payoutTxId",
            "timestamp": "payoutTimestamp",
            "blockId": "payoutBlockId",
            "fee": "payoutFee",
        }
    )

    payout_matches = payout_matches.merge(
        payout_metadata,
        on="payoutTxId",
        how="left",
        validate="many_to_one",
    )

    payout_matches["blockDistance"] = (
        payout_matches["payoutBlockId"] - payout_matches["betBlockId"]
    )

    ordered_columns = [
        "betTxId",
        "betOutputPosition",
        "payoutTxId",
        "addressId",
        "satoshiAddress",
        "diceName",
        "betAmountBtc",
        "betTimestamp",
        "betBlockId",
        "payoutTimestamp",
        "payoutBlockId",
        "payoutFee",
        "blockDistance",
    ]

    return payout_matches[ordered_columns].sort_values(
        ["betTimestamp", "betTxId", "betOutputPosition"], ignore_index=True
    )


def build_payout_distance_summary(payout_matches, total_bet_transactions):
    block_distance = payout_matches["blockDistance"]
    bet_transactions_with_payout = payout_matches["betTxId"].nunique()

    return pd.DataFrame(
        [
            {
                "total_bet_transactions": total_bet_transactions,
                "bet_transactions_with_payout": bet_transactions_with_payout,
                "bet_transactions_with_payout_percentage": (
                    bet_transactions_with_payout / total_bet_transactions * 100
                ),
                "payout_transactions": payout_matches["payoutTxId"].nunique(),
                "payout_links": len(payout_matches),
                "block_distance_mean": block_distance.mean(),
                "block_distance_median": block_distance.median(),
                "block_distance_p75": block_distance.quantile(0.75),
                "block_distance_p90": block_distance.quantile(0.90),
                "block_distance_p95": block_distance.quantile(0.95),
            }
        ]
    )
