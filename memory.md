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

## Important Findings
- Main CSV files have no header; column names must come from `src/load_data.py`.
- `satoshiDiceInfos.tsv` has a first URL line before the real header; loader uses `skiprows=1` and a regex separator.
- `outputs.csv` is large, but reading only `txId`, `position`, `addressId`, and `amount` is feasible in RAM; keep `position` for UTXO joins.
- `mapping.csv` has about 8.7M rows; sample runs should usually still read full mapping unless using `--sample-mapping` only as a smoke test.
- `transactions.txId` is not globally unique because duplicate historical coinbase txIds `142572` and `142726` exist. Filter `isCoinbase == 0` before merges that validate `txId` uniqueness.
- `candidate_bet_transactions` currently means a saved intermediate table, while report key `candidate_bet_transactions` means unique candidate `txId`; this naming can be confusing and may be cleaned up later.

## Commands
- Syntax check: `python -m compileall src scripts`
- Full build: `python scripts/build_bet_dataset.py`
- Sample with full mapping: `python scripts/build_bet_dataset.py --sample 100000`
- Smoke test with sampled mapping: `python scripts/build_bet_dataset.py --sample 100000 --sample-mapping 100000`

## Outputs
- Full build outputs are in `outputs/processed/`.
- Sample outputs are in `outputs/processed/sample/` and must not be treated as final analysis results.
- CSV/CSV.GZ is preferred over Parquet because the project is course-facing and uses standard formats.

## Next Logical Steps
- Add focused readers for processed CSV/CSV.GZ outputs so later analyses can start from `outputs/processed/bet_transactions.csv.gz` instead of raw CSVs.
- Implement general bet analyses: percentage of bet transactions over time, address popularity by count and amount, and plots.
- Implement payout matching using `inputs.csv` and UTXO joins on `(prevTxId, prevTxpos) -> (txId, position)`.
- Implement top-3-address analyses: temporal distributions, fee/amount correlation, and intervals between consecutive bets.
- Implement simple-bet chain graph analysis with NetworkX.
- Implement WalletExplorer Selenium scraping with caching for chain address wallet lookups.

## Memory Maintenance
- Append or update this file after each important logical step: new pipeline stage, completed analysis, discovered dataset gotcha, fixed bug, or changed workflow.
- Do not erase useful previous context; prefer adding dated or sectioned notes when a past issue may help future agents.
