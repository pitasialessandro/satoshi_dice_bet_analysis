import pandas as pd

from src.config import (
    INPUTS_PATH,
    MAPPING_PATH,
    OUTPUTS_PATH,
    SATOSHI_DICE_INFOS_PATH,
    TRANSACTIONS_PATH,
)


def load_transactions(nrows=None):
    return pd.read_csv(
        TRANSACTIONS_PATH,
        header=None,
        usecols=[0, 1, 2, 3, 4],
        names=["timestamp", "blockId", "txId", "isCoinbase", "fee"],
        dtype={
            "timestamp": "int64",
            "blockId": "int32",
            "txId": "int64",
            "isCoinbase": "int8",
            "fee": "int64",
        },
        nrows=nrows,
    )


def load_outputs(nrows=None):
    return pd.read_csv(
        OUTPUTS_PATH,
        header=None,
        usecols=[0, 1, 2, 3],
        names=["txId", "position", "addressId", "amount"],
        dtype={
            "txId": "int64",
            "position": "int16",
            "addressId": "int64",
            "amount": "int64",
        },
        nrows=nrows,
    )


def load_inputs(nrows=None):
    return pd.read_csv(
        INPUTS_PATH,
        header=None,
        usecols=[0, 1, 2],
        names=["txId", "prevTxId", "prevTxpos"],
        dtype={
            "txId": "int64",
            "prevTxId": "int64",
            "prevTxpos": "int16",
        },
        nrows=nrows,
    )


def load_mapping(nrows=None):
    return pd.read_csv(
        MAPPING_PATH,
        header=None,
        usecols=[0, 1],
        names=["hash", "addressId"],
        dtype={
            "hash": "string",
            "addressId": "int64",
        },
        nrows=nrows,
    )


def load_satoshi_dice_infos():
    df = pd.read_csv(
        SATOSHI_DICE_INFOS_PATH,
        skiprows=1,
        sep=r"\s{2,}|\t",
        engine="python",
    )
    # filter and cast floats
    df["WinOdds"] = df["WinOdds"].str.replace("%", "", regex=False).astype(float)
    df["PriceMultiplier"] = (
        df["PriceMultiplier"].str.replace("x", "", regex=False).astype(float)
    )
    df["HousePercentage"] = (
        df["HousePercentage"].str.replace("%", "", regex=False).astype(float)
    )
    df["ExpectReturn"] = (
        df["ExpectReturn"].str.replace("%", "", regex=False).astype(float)
    )
    df["MinimumBet"] = df["MinimumBet"].astype(float)
    df["MaximumBet"] = df["MaximumBet"].astype(float)

    return df
