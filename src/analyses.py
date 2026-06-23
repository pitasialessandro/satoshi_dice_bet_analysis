import pandas as pd


PERIOD_FREQUENCIES = {
    "day": "D",
    "week": "W",
    "month": "M",
}

TOP_ADDRESS_DISTRIBUTION_FREQUENCIES = {
    "hour": "h",
    "day": "D",
    "week": "W",
}


def add_period_column(df, freq, timestamp_col="timestamp"):
    result = df.copy()
    datetimes = pd.to_datetime(result[timestamp_col], unit="s")
    result["period"] = datetimes.dt.to_period(freq).astype(str)
    return result


def count_transactions_by_period(transactions, freq):
    transactions = add_period_column(transactions, freq)
    counts = transactions.groupby("period", sort=True).size()
    return counts.rename("total_transactions")


def count_unique_bets_by_period(bet_transactions, freq):
    unique_bets = bet_transactions.drop_duplicates("txId")
    unique_bets = add_period_column(unique_bets, freq)
    counts = unique_bets.groupby("period", sort=True).size()
    return counts.rename("bet_transactions")


def compute_bet_percentage_over_time(transactions, bet_transactions, freq):
    total_counts = count_transactions_by_period(transactions, freq)
    bet_counts = count_unique_bets_by_period(bet_transactions, freq)

    summary = pd.concat([total_counts, bet_counts], axis=1)
    summary["bet_transactions"] = summary["bet_transactions"].fillna(0).astype("int64")
    summary = summary.dropna(subset=["total_transactions"])
    summary["total_transactions"] = summary["total_transactions"].astype("int64")
    summary["bet_percentage"] = (
        summary["bet_transactions"] / summary["total_transactions"] * 100
    )

    return summary.reset_index()


def compute_bet_percentages_for_default_periods(transactions, bet_transactions):
    return {
        period_name: compute_bet_percentage_over_time(
            transactions, bet_transactions, freq
        )
        for period_name, freq in PERIOD_FREQUENCIES.items()
    }


def compute_address_popularity(bet_transactions, satoshi_addresses):
    address_columns = ["addressId", "satoshiAddress", "diceName"]

    popularity = bet_transactions.groupby(address_columns, as_index=False).agg(
        bet_count=("txId", "nunique"),
        total_bet_amount_btc=("betAmountBtc", "sum"),
    )

    address_lookup = satoshi_addresses.rename(
        columns={"Address": "satoshiAddress", "Name": "diceName"}
    )[address_columns + ["WinOdds", "PriceMultiplier"]]

    popularity = address_lookup.merge(
        popularity,
        on=address_columns,
        how="left",
        validate="one_to_one",
    )

    numeric_columns = ["bet_count", "total_bet_amount_btc"]
    popularity[numeric_columns] = popularity[numeric_columns].fillna(0)
    popularity["bet_count"] = popularity["bet_count"].astype("int64")

    return popularity.sort_values(
        ["bet_count", "total_bet_amount_btc"], ascending=True, ignore_index=True
    )


def get_top_addresses_by_bet_count(address_popularity, n=3):
    return address_popularity.nlargest(n, "bet_count")[
        ["addressId", "satoshiAddress", "diceName"]
    ].reset_index(drop=True)


def compute_top_address_bet_distribution(bet_transactions, top_addresses, freq):
    # this function gets called for each freq (hour, day, month)
    top_address_ids = top_addresses["addressId"]
    filtered = bet_transactions[bet_transactions["addressId"].isin(top_address_ids)].copy()
    filtered = filtered.drop_duplicates(["addressId", "txId"])

    # timestamp UNIX -> exact date -> date period (truncation)
    filtered["period"] = pd.to_datetime(filtered["timestamp"], unit="s").dt.to_period(freq)

    # with groupby a multi-index gets created by the concatenation of period and addressId
    distribution = filtered.groupby(["period", "addressId"]).agg(
        # count unique transactions aggregating by period
        bet_count=("txId", "nunique")
    )

    # avoid blank periods by creating a full range period list (not the case for this analysis)
    all_periods = pd.period_range(
        filtered["period"].min(), filtered["period"].max(), freq=freq
    )

    # fill gaps with cartesian product and reindex
    full_index = pd.MultiIndex.from_product(
        [all_periods, top_address_ids], names=["period", "addressId"]
    )
    distribution = distribution.reindex(full_index, fill_value=0)
    distribution = distribution.reset_index().merge(
        top_addresses,
        on="addressId",
        how="left",
        validate="many_to_one",
    )
    distribution["period"] = distribution["period"].astype(str)

    return distribution[
        ["period", "addressId", "satoshiAddress", "diceName", "bet_count"]
    ]


def compute_top_address_bet_distributions(bet_transactions, address_popularity, n=3):
    top_addresses = get_top_addresses_by_bet_count(address_popularity, n=n)
    return {
        period_name: compute_top_address_bet_distribution(
            bet_transactions, top_addresses, freq
        )
        for period_name, freq in TOP_ADDRESS_DISTRIBUTION_FREQUENCIES.items()
    }
