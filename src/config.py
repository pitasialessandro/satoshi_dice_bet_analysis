from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATASETS_DIR = PROJECT_ROOT / "datasets"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
PROCESSED_DIR = OUTPUTS_DIR / "processed"

TRANSACTIONS_PATH = DATASETS_DIR / "transactions.csv"
INPUTS_PATH = DATASETS_DIR / "inputs.csv"
OUTPUTS_PATH = DATASETS_DIR / "outputs.csv"
MAPPING_PATH = DATASETS_DIR / "mapping.csv"
SATOSHI_DICE_INFOS_PATH = DATASETS_DIR / "satoshiDiceInfos.tsv"

SATOSHI_PER_BTC = 100_000_000
