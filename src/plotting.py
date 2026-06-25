import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd


def plot_monthly_transactions_vs_bet_share(monthly_df, output_path=None):
    df = monthly_df.copy()
    # matplotlib needs a specific timestamp to plot so we convert it 
    df["month"] = pd.PeriodIndex(df["period"], freq="M").to_timestamp()

    fig, ax_transactions = plt.subplots(figsize=(12, 6))

    # bar chart
    ax_transactions.bar(
        df["month"],
        df["total_transactions"],
        width=24,
        color="#8fb6d9",
        alpha=0.75,
        label="Total Bitcoin transactions",
    )
    ax_transactions.set_ylabel("Total transactions")
    ax_transactions.tick_params(axis="y")
    ax_transactions.grid(axis="y", alpha=0.25)

    # twinx -> new twin axis
    ax_percentage = ax_transactions.twinx()
    # linear plot
    ax_percentage.plot(
        df["month"],
        df["bet_percentage"],
        color="#c43d32",
        linewidth=2.4,
        marker="o",
        markersize=4,
        label="SatoshiDice share",
    )
    ax_percentage.set_ylabel("SatoshiDice transactions (%)")
    ax_percentage.tick_params(axis="y")
    ax_percentage.set_ylim(bottom=0)

    # idxmax -> find percentage peak
    peak = df.loc[df["bet_percentage"].idxmax()]
    # draw on chart
    ax_percentage.annotate(
        f"Peak: {peak['period']}\n{peak['bet_percentage']:.1f}%",
        xy=(peak["month"], peak["bet_percentage"]),
        xytext=(15, 25),
        textcoords="offset points",
        arrowprops={"arrowstyle": "->", "color": "#333333", "lw": 1},
        fontsize=9,
        bbox={"boxstyle": "round,pad=0.3", "fc": "white", "ec": "#999999"},
    )

    ax_transactions.set_title(
        "Monthly Bitcoin Transactions and SatoshiDice Share"
    )

    # time axis readability
    ax_transactions.set_xlabel("Month")
    ax_transactions.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
    ax_transactions.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    fig.autofmt_xdate(rotation=45)

    # merge legends in a unique one 
    handles_1, labels_1 = ax_transactions.get_legend_handles_labels()
    handles_2, labels_2 = ax_percentage.get_legend_handles_labels()
    ax_transactions.legend(
        handles_1 + handles_2,
        labels_1 + labels_2,
        loc="upper left",
        frameon=True,
    )

    fig.tight_layout()

    if output_path is not None:
        fig.savefig(output_path, dpi=160, bbox_inches="tight")

    return fig, (ax_transactions, ax_percentage)


def plot_address_popularity_comparison(address_popularity, output_path=None):
    df = address_popularity.copy()
    labels = df["diceName"].astype(str)

    fig, (ax_count, ax_amount) = plt.subplots(
        ncols=2,
        figsize=(14, 9),
        sharey=True,
        gridspec_kw={"width_ratios": [1, 1.15]},
    )

    ax_count.barh(
        labels,
        df["bet_count"],
        color="#6aa6c8",
        alpha=0.85,
    )
    ax_count.set_title("Popularity by Number of Bets")
    ax_count.set_xlabel("Unique bet transactions")
    ax_count.grid(axis="x", alpha=0.25)

    ax_amount.barh(
        labels,
        df["total_bet_amount_btc"],
        color="#d98f45",
        alpha=0.85,
    )
    ax_amount.set_title("Popularity by Total Bet Amount")
    ax_amount.set_xlabel("Total amount bet (BTC)")
    ax_amount.grid(axis="x", alpha=0.25)

    fig.suptitle("SatoshiDice Address Popularity", y=0.995)
    fig.tight_layout()

    if output_path is not None:
        fig.savefig(output_path, dpi=160, bbox_inches="tight")

    return fig, (ax_count, ax_amount)


def _values_up_to_quantile(values, quantile=0.99):
    upper_bound = values.quantile(quantile)
    return values[values <= upper_bound], upper_bound


def plot_payout_block_distance_distribution(payout_matches, output_path=None):
    values, upper_bound = _values_up_to_quantile(payout_matches["blockDistance"])
    # count how many times each value appears in the series
    # then sort by index (block distance, not frequency) 
    counts = values.value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(10, 6))
    # bar chart with log scale
    ax.bar(counts.index, counts.values, color="#6aa6c8", alpha=0.85)
    ax.set_yscale("log")
    ax.set_title("Bet to Payout Distance in Blocks")
    ax.set_xlabel(f"Block distance (<= 99th percentile: {upper_bound:.0f})")
    ax.set_ylabel("Payout link count (log scale)")
    ax.set_xticks(counts.index)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()

    if output_path is not None:
        fig.savefig(output_path, dpi=160, bbox_inches="tight")

    return fig, ax


def plot_top_address_bet_distribution(distribution, freq, output_path=None):
    df = distribution.copy()
    df["periodDate"] = pd.PeriodIndex(df["period"], freq=freq).to_timestamp()

    fig, ax = plt.subplots(figsize=(12, 6))

    # plot a line for each address
    # group-by returns a DataFrameGroupBy obj that contains sub-DataFrames
    # avoiding filtering manually by each address
    for dice_name, group in df.groupby("diceName", sort=False):
        group = group.sort_values("periodDate")
        ax.plot(
            group["periodDate"],
            group["bet_count"],
            linewidth=1.8,
            label=dice_name,
        )

    ax.set_title("Top 3 SatoshiDice Addresses: Bet Distribution Over Time")
    ax.set_xlabel("Period")
    ax.set_ylabel("Unique bet transactions")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(title="Address type")

    if freq == "h":
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    elif freq == "D":
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    else:
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

    fig.autofmt_xdate(rotation=45)
    fig.tight_layout()

    if output_path is not None:
        fig.savefig(output_path, dpi=160, bbox_inches="tight")

    return fig, ax


def plot_top3_fee_amount_correlation(points, correlation_summary=None, output_path=None):
    df = points[points["betAmountBtc"] > 0].copy()
    if len(df) > 120_000:
        df = df.sample(120_000, random_state=42)

    fig, ax = plt.subplots(figsize=(10, 6))

    for dice_name, group in df.groupby("diceName", sort=False):
        ax.scatter(
            group["betAmountBtc"],
            group["feeBtc"],
            s=6,
            alpha=0.16,
            label=dice_name,
        )

    title = "Top 3 SatoshiDice Addresses: Bet Amount vs Transaction Fee"
    if correlation_summary is not None:
        all_top3 = correlation_summary[correlation_summary["scope"] == "all_top3"]
        if not all_top3.empty:
            spearman = all_top3["spearman_fee_amount"].iloc[0]
            title = f"{title}\nSpearman correlation: {spearman:.3f}"

    ax.set_title(title)
    ax.set_xlabel("Bet amount (BTC, log scale)")
    ax.set_ylabel("Transaction fee (BTC)")
    ax.set_xscale("log")
    ax.grid(alpha=0.25)
    ax.legend(title="Address type", markerscale=2)
    fig.tight_layout()

    if output_path is not None:
        fig.savefig(output_path, dpi=160, bbox_inches="tight")

    return fig, ax


def plot_top3_bet_interval_distribution(bet_intervals, output_path=None):
    df = bet_intervals.dropna(subset=["timeIntervalMinutes"]).copy()
    dice_names = list(df["diceName"].drop_duplicates())
    upper_bound = df["timeIntervalMinutes"].quantile(0.99)

    fig, axes = plt.subplots(
        nrows=len(dice_names),
        figsize=(10, 9),
        sharex=True,
    )
    if len(dice_names) == 1:
        axes = [axes]

    for ax, dice_name in zip(axes, dice_names):
        values = df.loc[df["diceName"] == dice_name, "timeIntervalMinutes"]
        values = values[values <= upper_bound]

        ax.hist(values, bins=60, color="#6aa6c8", alpha=0.85, log=True)
        ax.set_title(dice_name)
        ax.set_ylabel("Intervals count\n(log scale)")
        ax.grid(axis="y", alpha=0.25)

    axes[-1].set_xlabel(
        f"Minutes between consecutive bets (<= global 99th percentile: {upper_bound:.2f})"
    )
    fig.suptitle("Top 3 SatoshiDice Addresses: Time Between Consecutive Bets", y=0.995)
    fig.tight_layout()

    if output_path is not None:
        fig.savefig(output_path, dpi=160, bbox_inches="tight")

    return fig, axes


def plot_simple_bet_chain_length_distribution(chain_lengths, output_path=None):
    df = chain_lengths.sort_values("chainLength").copy()
    visible = df[df["chainLength"] <= 50].copy()
    tail = df[df["chainLength"] > 50]

    if not tail.empty:
        visible = pd.concat(
            [
                visible,
                pd.DataFrame(
                    [
                        {
                            "chainLength": 51,
                            "chainCount": tail["chainCount"].sum(),
                            "simpleBetCount": tail["simpleBetCount"].sum(),
                            "chainPercentage": tail["chainPercentage"].sum(),
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )

    labels = visible["chainLength"].astype(str)
    labels = labels.mask(visible["chainLength"] == 51, "51+")

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(labels, visible["chainCount"], color="#6aa6c8", alpha=0.85)
    ax.set_yscale("log")
    ax.set_title("Simple-Bet Chain Length Distribution")
    ax.set_xlabel("Chain length (number of simple bets)")
    ax.set_ylabel("Chain count (log scale)")
    ax.grid(axis="y", alpha=0.25)
    ax.tick_params(axis="x", rotation=45)

    longest = df.loc[df["chainLength"].idxmax()]
    ax.annotate(
        f"Longest chain: {int(longest['chainLength'])} bets",
        xy=(0.98, 0.92),
        xycoords="axes fraction",
        ha="right",
        bbox={"boxstyle": "round,pad=0.3", "fc": "white", "ec": "#999999"},
        fontsize=9,
    )

    fig.tight_layout()

    if output_path is not None:
        fig.savefig(output_path, dpi=160, bbox_inches="tight")

    return fig, ax
