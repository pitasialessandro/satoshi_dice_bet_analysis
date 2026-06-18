# AGENTS.md

## Project Context
- This is a Python data-analysis project for `satoshiDiceBetting.md`; final deliverable is a Jupyter notebook with integrated report/PDF, and WalletExplorer scraping must use Selenium.
- The raw datasets live in `datasets/`; small inspection copies live in `dataset_lookup/` and should be preferred for quickly checking column order/shape.
- There is no README, package manifest, CI, lint, or test config in this repo; treat `src/` and `scripts/` as the executable source of truth.

## Dataset Gotchas
- Main CSV files have no header. Use the column names in `src/load_data.py`, not inferred names.
- `outputs.csv` currently skips `scripttype` via `usecols`; keep `position` because UTXO joins need `(txId, position)`.
- `transactions.csv` keeps `isCoinbase`; project logic excludes `isCoinbase == 1` from betting transactions.
- `satoshiDiceInfos.tsv` has a first line URL before the real header; parse with `skiprows=1` and the regex separator already in `load_satoshi_dice_infos()`.
- Amounts and fees are satoshi integers; use `SATOSHI_PER_BTC = 100_000_000` for BTC conversion.
- `transactions.txId` is not globally unique: duplicate historical coinbase txIds `142572` and `142726` exist. Filter coinbase rows before any merge that validates `txId` as unique.

## Commands
- Syntax check: `python -m compileall src scripts`
- Build intermediate bet datasets from full data: `python scripts/build_bet_dataset.py`
- Fast sample run with full mapping: `python scripts/build_bet_dataset.py --sample 100000`
- Smoke-test-only run that also samples mapping: `python scripts/build_bet_dataset.py --sample 100000 --sample-mapping 100000`; results are intentionally not analytically reliable.

## Outputs
- Full build writes to `outputs/processed/`: `satoshi_addresses.csv`, `satoshi_bet_outputs.csv.gz`, `candidate_bet_transactions.csv.gz`, `bet_transactions.csv.gz`, `identification_report.json`.
- Any run with `--sample` or `--sample-mapping` writes to `outputs/processed/sample/`; do not treat those files as final analysis outputs.
- Existing full identification report found 27/27 SatoshiDice addresses in mapping and 1,965,817 non-coinbase bet transactions.

## Workflow Notes
- Avoid reading `inputs.csv` until payout or chain analysis; bet identification only needs transactions, outputs, mapping, and SatoshiDice info.
- Prefer CSV/CSV.GZ intermediates over Parquet here because the project is course-facing and the current scripts already use standard CSV formats.
- The raw files are large (`outputs.csv` about 24.6M rows, `mapping.csv` about 8.7M rows); use `nrows`/sample flags for development and expect full gzip writes to be slow.
- Keep `memory.md` updated after each important logical step, bug discovery, or workflow change. Do not delete prior useful context; append or revise carefully so future agents retain the history of decisions and past errors.
