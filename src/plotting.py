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
