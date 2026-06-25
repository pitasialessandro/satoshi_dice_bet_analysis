import networkx as nx
import pandas as pd

from src.config import SATOSHI_PER_BTC


def get_most_popular_satoshi_address(address_popularity):
    return address_popularity.nlargest(1, "bet_count").iloc[0]


def build_simple_bets(inputs, outputs, bet_transactions, address_popularity):
    top_address = get_most_popular_satoshi_address(address_popularity)
    top_address_id = top_address["addressId"]

    selected_bet_outputs = bet_transactions[
        bet_transactions["addressId"] == top_address_id
    ].copy()

    # Build one explicit count table so the simple-bet definition is visible.
    selected_satoshi_counts = selected_bet_outputs.groupby("txId").size().reset_index(
        name="selectedSatoshiOutputCount"
    )
    selected_tx_ids = selected_satoshi_counts["txId"]
    candidate_inputs = inputs[inputs["txId"].isin(selected_tx_ids)].copy()
    candidate_outputs = outputs[outputs["txId"].isin(selected_tx_ids)].copy()

    total_satoshi_counts = bet_transactions.groupby("txId").size().reset_index(
        name="totalSatoshiOutputCount"
    )
    input_counts = candidate_inputs.groupby("txId").size().reset_index(name="inputCount")
    output_counts = candidate_outputs.groupby("txId").size().reset_index(name="outputCount")

    tx_counts = selected_satoshi_counts.merge(
        total_satoshi_counts,
        on="txId",
        how="left",
        validate="one_to_one",
    ).merge(
        input_counts,
        on="txId",
        how="left",
        validate="one_to_one",
    ).merge(
        output_counts,
        on="txId",
        how="left",
        validate="one_to_one",
    )

    simple_tx_ids = tx_counts.loc[
        (tx_counts["selectedSatoshiOutputCount"] == 1)
        & (tx_counts["totalSatoshiOutputCount"] == 1)
        & (tx_counts["inputCount"] == 1)
        & (tx_counts["outputCount"] == 2),
        "txId",
    ]

    simple_inputs = candidate_inputs[candidate_inputs["txId"].isin(simple_tx_ids)].rename(
        columns={"prevTxId": "inputPrevTxId", "prevTxpos": "inputPrevTxpos"}
    )

    simple_bet_outputs = selected_bet_outputs[
        selected_bet_outputs["txId"].isin(simple_tx_ids)
    ].rename(columns={"position": "betOutputPosition"})

    simple_outputs = candidate_outputs[candidate_outputs["txId"].isin(simple_tx_ids)]
    change_outputs = simple_outputs.merge(
        simple_bet_outputs[["txId", "betOutputPosition"]],
        on="txId",
        how="inner",
        validate="many_to_one",
    )
    change_outputs = change_outputs[
        change_outputs["position"] != change_outputs["betOutputPosition"]
    ].rename(
        columns={
            "position": "changeOutputPosition",
            "addressId": "changeAddressId",
            "amount": "changeAmount",
        }
    )
    change_outputs["changeAmountBtc"] = change_outputs["changeAmount"] / SATOSHI_PER_BTC

    previous_outputs = outputs[outputs["txId"].isin(simple_inputs["inputPrevTxId"])].rename(
        columns={
            "txId": "inputPrevTxId",
            "position": "inputPrevTxpos",
            "addressId": "inputAddressId",
            "amount": "inputAmount",
        }
    )
    input_sources = simple_inputs.merge(
        previous_outputs,
        on=["inputPrevTxId", "inputPrevTxpos"],
        how="left",
        validate="many_to_one",
    )
    input_sources["inputAmountBtc"] = input_sources["inputAmount"] / SATOSHI_PER_BTC

    simple_bets = simple_bet_outputs.merge(
        input_sources,
        on="txId",
        how="inner",
        validate="one_to_one",
    ).merge(
        change_outputs[
            ["txId", "changeOutputPosition", "changeAddressId", "changeAmount", "changeAmountBtc"]
        ],
        on="txId",
        how="inner",
        validate="one_to_one",
    )

    ordered_columns = [
        "txId",
        "timestamp",
        "datetime",
        "blockId",
        "fee",
        "feeBtc",
        "addressId",
        "satoshiAddress",
        "diceName",
        "betOutputPosition",
        "betAmount",
        "betAmountBtc",
        "inputPrevTxId",
        "inputPrevTxpos",
        "inputAddressId",
        "inputAmount",
        "inputAmountBtc",
        "changeOutputPosition",
        "changeAddressId",
        "changeAmount",
        "changeAmountBtc",
    ]

    return simple_bets[ordered_columns].sort_values(
        ["timestamp", "txId"], ignore_index=True
    )


def build_simple_bet_edges(simple_bets):
    source_changes = simple_bets[
        ["txId", "timestamp", "blockId", "changeOutputPosition"]
    ].rename(
        columns={
            "txId": "sourceTxId",
            "timestamp": "sourceTimestamp",
            "blockId": "sourceBlockId",
        }
    )
    target_inputs = simple_bets[
        ["txId", "timestamp", "blockId", "inputPrevTxId", "inputPrevTxpos"]
    ].rename(
        columns={
            "txId": "targetTxId",
            "timestamp": "targetTimestamp",
            "blockId": "targetBlockId",
        }
    )

    edges = target_inputs.merge(
        source_changes,
        left_on=["inputPrevTxId", "inputPrevTxpos"],
        right_on=["sourceTxId", "changeOutputPosition"],
        how="inner",
        validate="one_to_one",
    )
    edges = edges[edges["sourceTxId"] != edges["targetTxId"]].copy()
    edges["blockDistance"] = edges["targetBlockId"] - edges["sourceBlockId"]
    edges["timeDistanceSeconds"] = edges["targetTimestamp"] - edges["sourceTimestamp"]

    ordered_columns = [
        "sourceTxId",
        "targetTxId",
        "changeOutputPosition",
        "sourceTimestamp",
        "targetTimestamp",
        "sourceBlockId",
        "targetBlockId",
        "blockDistance",
        "timeDistanceSeconds",
    ]

    return edges[ordered_columns].sort_values(
        ["sourceTimestamp", "sourceTxId", "targetTxId"], ignore_index=True
    )


def build_simple_bet_chain_summaries(simple_bets, edges):
    graph = nx.DiGraph()
    node_metadata = simple_bets.set_index("txId")[["timestamp", "blockId"]].to_dict("index")
    graph.add_nodes_from((tx_id, metadata) for tx_id, metadata in node_metadata.items())
    graph.add_edges_from(edges[["sourceTxId", "targetTxId"]].itertuples(index=False, name=None))

    # Each simple bet has one input and one change output, so chains are linear.
    child_by_source = dict(
        edges[["sourceTxId", "targetTxId"]].itertuples(index=False, name=None)
    )
    parent_by_target = dict(
        edges[["targetTxId", "sourceTxId"]].itertuples(index=False, name=None)
    )
    ordered_tx_ids = list(simple_bets["txId"])
    start_tx_ids = [tx_id for tx_id in ordered_tx_ids if tx_id not in parent_by_target]

    rows = []
    visited = set()

    def add_chain(chain):
        start_tx_id = chain[0]
        end_tx_id = chain[-1]
        start_timestamp = graph.nodes[start_tx_id].get("timestamp")
        end_timestamp = graph.nodes[end_tx_id].get("timestamp")

        rows.append(
            {
                "chainId": len(rows) + 1,
                "chainLength": len(chain),
                "edgeCount": len(chain) - 1,
                "startTxId": start_tx_id,
                "endTxId": end_tx_id,
                "startTimestamp": start_timestamp,
                "endTimestamp": end_timestamp,
                "startBlockId": graph.nodes[start_tx_id].get("blockId"),
                "endBlockId": graph.nodes[end_tx_id].get("blockId"),
                "durationSeconds": end_timestamp - start_timestamp,
            }
        )

    for start_tx_id in start_tx_ids:
        if start_tx_id in visited:
            continue

        chain = []
        current_tx_id = start_tx_id
        while current_tx_id not in visited:
            visited.add(current_tx_id)
            chain.append(current_tx_id)

            next_tx_id = child_by_source.get(current_tx_id)
            if next_tx_id is None:
                break
            current_tx_id = next_tx_id

        add_chain(chain)

    # This fallback should not be needed for normal UTXO chains, but avoids dropping nodes.
    for start_tx_id in ordered_tx_ids:
        if start_tx_id in visited:
            continue

        chain = []
        current_tx_id = start_tx_id
        while current_tx_id not in visited:
            visited.add(current_tx_id)
            chain.append(current_tx_id)

            next_tx_id = child_by_source.get(current_tx_id)
            if next_tx_id is None:
                break
            current_tx_id = next_tx_id

        add_chain(chain)

    return pd.DataFrame(rows).sort_values(
        ["chainLength", "edgeCount", "startTimestamp"],
        ascending=[False, False, True],
        ignore_index=True,
    )


def build_chain_length_distribution(chain_summaries):
    distribution = chain_summaries.groupby("chainLength", as_index=False).agg(
        chainCount=("chainId", "count")
    )
    distribution["simpleBetCount"] = distribution["chainLength"] * distribution["chainCount"]
    distribution["chainPercentage"] = (
        distribution["chainCount"] / distribution["chainCount"].sum() * 100
    )

    return distribution.sort_values("chainLength", ignore_index=True)


def build_simple_bet_chain_summary(simple_bets, edges, chain_summaries):
    return pd.DataFrame(
        [
            {
                "simple_bets": len(simple_bets),
                "simple_bet_edges": len(edges),
                "chains": len(chain_summaries),
                "isolated_simple_bets": int((chain_summaries["chainLength"] == 1).sum()),
                "max_chain_length": int(chain_summaries["chainLength"].max()),
                "mean_chain_length": chain_summaries["chainLength"].mean(),
                "median_chain_length": chain_summaries["chainLength"].median(),
                "p95_chain_length": chain_summaries["chainLength"].quantile(0.95),
                "p99_chain_length": chain_summaries["chainLength"].quantile(0.99),
            }
        ]
    )
