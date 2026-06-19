# Project Memory

## Current Goal
- Build a Python/Jupyter data-analysis project for `satoshiDiceBetting.md`: identify SatoshiDice bets, analyze betting/payout behavior, build simple-bet chains, and scrape WalletExplorer with Selenium for selected chains.

## Completed Steps
- Created `dataset_lookup/` with first-line inspection copies of each raw dataset.
- Added `src/config.py` with project paths and `SATOSHI_PER_BTC = 100_000_000`.
- Added `src/load_data.py` with typed Pandas loaders for `transactions.csv`, `outputs.csv`, `inputs.csv`, `mapping.csv`, and `satoshiDiceInfos.tsv`.
- Added `src/identify_bets.py` for mapping SatoshiDice addresses, identifying outputs to SatoshiDice, building bet transactions, and producing an identification report.
- Added `scripts/build_bet_dataset.py` to build intermediate bet datasets and write CSV/CSV.GZ/JSON outputs.
- Ran the full bet-identification build successfully; current report found 27/27 SatoshiDice addresses and 1,965,817 non-coinbase bet transactions.
- Added `AGENTS.md` with repo-specific instructions for future OpenCode sessions.
- Added Git ignore rules so raw datasets, generated outputs, virtualenvs, and Python caches are not committed.
- Simplified bet identification: coinbase transactions are now excluded a priori when building bet transactions, no `candidate_bet_transactions` table is generated, and the identification report keeps only essential counts.
- Added time-series analysis for project section 4.1: `src/analyses.py` computes bet percentages by period and `scripts/build_bet_time_series.py` writes day/week/month CSV files.
- Added reusable plotting infrastructure: `src/plotting.py` contains plotting functions and `scripts/build_figures.py` writes PNG figures under `outputs/figures/`.

## Important Findings
- Main CSV files have no header; column names must come from `src/load_data.py`.
- `satoshiDiceInfos.tsv` has a first URL line before the real header; loader uses `skiprows=1` and a regex separator.
- `outputs.csv` is large, but reading only `txId`, `position`, `addressId`, and `amount` is feasible in RAM; keep `position` for UTXO joins.
- `mapping.csv` has about 8.7M rows; sample runs should usually still read full mapping unless using `--sample-mapping` only as a smoke test.
- `transactions.txId` is not globally unique because duplicate historical coinbase txIds `142572` and `142726` exist. Filter `isCoinbase == 0` before merges that validate `txId` uniqueness.
- `build_bet_transactions()` always filters `isCoinbase == 0` before merging, then raises if any non-coinbase `txId` duplicates remain.
- For bet percentage over time, the denominator is all rows in `transactions.csv` including coinbase transactions; the numerator is unique SatoshiDice bet `txId` values from `bet_transactions.csv.gz`.

## Commands
- Syntax check: `python -m compileall src scripts`
- Full build: `python scripts/build_bet_dataset.py`
- Sample with full mapping: `python scripts/build_bet_dataset.py --sample 100000`
- Smoke test with sampled mapping: `python scripts/build_bet_dataset.py --sample 100000 --sample-mapping 100000`
- Build bet percentage time series from processed outputs: `python scripts/build_bet_time_series.py`
- Sample time-series build: `python scripts/build_bet_time_series.py --sample 100000`
- Build PNG figures: `python scripts/build_figures.py`
- Build PNG figures from sample processed data: `python scripts/build_figures.py --sample`

## Outputs
- Full build outputs are in `outputs/processed/`.
- Sample outputs are in `outputs/processed/sample/` and must not be treated as final analysis results.
- Generated bet-identification files are `satoshi_addresses.csv`, `satoshi_bet_outputs.csv.gz`, `bet_transactions.csv.gz`, and `identification_report.json`.
- Generated time-series files are `bet_percentage_by_day.csv`, `bet_percentage_by_week.csv`, and `bet_percentage_by_month.csv`.
- Generated figures are saved as PNG files under `outputs/figures/`; sample figure runs write to `outputs/figures/sample/`.
- CSV/CSV.GZ is preferred over Parquet because the project is course-facing and uses standard formats.

## Next Logical Steps
- Implement address popularity by count and amount, then plots for the generated time-series/address analyses.
- Implement payout matching using `inputs.csv` and UTXO joins on `(prevTxId, prevTxpos) -> (txId, position)`.
- Implement top-3-address analyses: temporal distributions, fee/amount correlation, and intervals between consecutive bets.
- Implement simple-bet chain graph analysis with NetworkX.
- Implement WalletExplorer Selenium scraping with caching for chain address wallet lookups.

## Memory Maintenance
- Append or update this file after each important logical step: new pipeline stage, completed analysis, discovered dataset gotcha, fixed bug, or changed workflow.
- Do not erase useful previous context; prefer adding dated or sectioned notes when a past issue may help future agents.
