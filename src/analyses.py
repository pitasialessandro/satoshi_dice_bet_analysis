import pandas as pd


PERIOD_FREQUENCIES = {
    "day": "D",
    "week": "W",
    "month": "M",
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
