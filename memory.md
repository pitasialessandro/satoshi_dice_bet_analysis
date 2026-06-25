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
- Added address popularity analysis for project section 4.2: `scripts/build_address_popularity.py` writes `address_popularity.csv`, and `scripts/build_figures.py` now also generates the two-panel popularity comparison PNG.
- Simplified `address_popularity.csv` to only keep fields needed by the project: address metadata, `bet_count`, and `total_bet_amount_btc`.
- Simplified address popularity computation to one groupby: `bet_count` uses `txId.nunique()` and `total_bet_amount_btc` sums output amounts per SatoshiDice address.
- Added payout matching for project section 4.3: `src/payouts.py` links bet outputs to later spending inputs, and `scripts/build_payout_matches.py` writes payout matches plus block-distance summary.
- Full payout build found 2,349,938 payout links; 1,965,206 of 1,965,817 bet transactions have a matched payout spend (99.97%). Median block distance is 0 and mean block distance is about 1.25 blocks.
- Added first top-3-address analysis for project section 4.4: `scripts/build_top_address_distributions.py` writes hourly/daily/weekly bet-count distributions for the three addresses with largest `bet_count`.
- Added top-3 fee/amount correlation analysis: `scripts/build_top3_fee_amount_correlation.py` writes an aggregated points file and a correlation summary with an `all_top3` row plus per-address rows.
- Full top-3 fee/amount build produced 1,392,137 points. Aggregate correlation is very weak: Pearson about 0.005 and Spearman about 0.106, consistent with fees not being a SatoshiDice game mechanic.
- Added top-3 consecutive-bet interval analysis: `scripts/build_top3_bet_intervals.py` computes timestamp-based intervals between consecutive bets for each of the three most popular addresses.
- Added simple-bet chain analysis for project section 5: `src/simple_bet_chains.py` filters simple bets for the most popular SatoshiDice address, links change outputs to later simple-bet inputs with NetworkX, and computes chain summaries plus length distribution.
- Full simple-bet chain build uses `lessthan 32000` / `1dice8EMZmqKvrGE4Qc9bUFf9PX3xaYDp` as the most popular address. It produced 526,834 simple bets, 311,847 chain edges, and 214,987 chains. Maximum chain length is 717 simple bets; median chain length is 1, mean is about 2.45, p95 is 7, and p99 is 20.
- Simplified `src/simple_bet_chains.py` for explainability: the simple-bet filter now builds an explicit count table (`selectedSatoshiOutputCount`, `totalSatoshiOutputCount`, `inputCount`, `outputCount`) and chain extraction no longer uses `nx.weakly_connected_components`; it creates a `nx.DiGraph()` but walks linear UTXO chains from starts to ends.

## Important Findings
- Main CSV files have no header; column names must come from `src/load_data.py`.
- `satoshiDiceInfos.tsv` has a first URL line before the real header; loader uses `skiprows=1` and a regex separator.
- `outputs.csv` is large, but reading only `txId`, `position`, `addressId`, and `amount` is feasible in RAM; keep `position` for UTXO joins.
- `mapping.csv` has about 8.7M rows; sample runs should usually still read full mapping unless using `--sample-mapping` only as a smoke test.
- `transactions.txId` is not globally unique because duplicate historical coinbase txIds `142572` and `142726` exist. Filter `isCoinbase == 0` before merges that validate `txId` uniqueness.
- `build_bet_transactions()` always filters `isCoinbase == 0` before merging, then raises if any non-coinbase `txId` duplicates remain.
- For bet percentage over time, the denominator is all rows in `transactions.csv` including coinbase transactions; the numerator is unique SatoshiDice bet `txId` values from `bet_transactions.csv.gz`.
- Address popularity uses two different metrics: `bet_count` counts unique `txId` values per SatoshiDice address, while `total_bet_amount_btc` sums the BTC sent to that address. The final table is left-joined from `satoshi_addresses.csv`, so all 27 known addresses remain present even if an address had zero bets.
- Payout matching uses the UTXO relation `inputs.prevTxId/prevTxpos -> bet_transactions.txId/position`; distances are measured only as block difference, not as numeric `txId` difference or timestamp difference. Timestamp-based distance was discarded because Bitcoin block timestamps are miner-provided and not reliable enough for this analysis.
- Top-3-address analysis selects addresses with `address_popularity.nlargest(3, "bet_count")`; do not rely on CSV ordering because `address_popularity.csv` may be sorted for plotting readability.
- Fee/amount correlation is interpreted as an empirical check, not a causal game mechanic: Bitcoin fees affect miner inclusion incentives, not SatoshiDice win probability.
- Spearman correlation uses `pandas.Series.corr(method="spearman")`; SciPy must be installed in the project environment because Pandas delegates Spearman computation internally.
- Consecutive-bet interval analysis intentionally uses transaction timestamps and timestamp sorting, because the project asks for temporal intervals; this differs from payout distance, where timestamp distance was discarded.
- `top3_bet_intervals_time.png` uses a global 99th-percentile x-axis cutoff only for readability; full interval outliers remain in `top3_bet_intervals.csv.gz` and should be discussed from the processed data/notebook.
- Simple bet definition for chain analysis: selected SatoshiDice address is the most popular one by `bet_count`; a simple bet has exactly 1 input, exactly 2 outputs, exactly one output to that selected SatoshiDice address, and exactly one total SatoshiDice output. The other output is interpreted as the change output.
- Simple-bet chain edges link `source.txId/source.changeOutputPosition` to `target.inputPrevTxId/target.inputPrevTxpos`. Chains are extracted by finding simple bets without a parent and following each change-output child until the sequence ends; isolated simple bets have chain length 1.
- `simple_bet_chain_lengths.png` aggregates lengths greater than 50 only in the plot for readability; `simple_bet_chain_lengths.csv` keeps the full length distribution.

## Commands
- Syntax check: `python -m compileall src scripts`
- Full build: `python scripts/build_bet_dataset.py`
- Sample with full mapping: `python scripts/build_bet_dataset.py --sample 100000`
- Smoke test with sampled mapping: `python scripts/build_bet_dataset.py --sample 100000 --sample-mapping 100000`
- Build bet percentage time series from processed outputs: `python scripts/build_bet_time_series.py`
- Sample time-series build: `python scripts/build_bet_time_series.py --sample 100000`
- Build address popularity table: `python scripts/build_address_popularity.py`
- Build payout matches and distance summary: `python scripts/build_payout_matches.py`
- Build top-3 address temporal distributions: `python scripts/build_top_address_distributions.py`
- Build top-3 fee/amount correlation: `python scripts/build_top3_fee_amount_correlation.py`
- Build top-3 consecutive bet intervals: `python scripts/build_top3_bet_intervals.py`
- Build simple-bet chains: `python scripts/build_simple_bet_chains.py`
- Build PNG figures: `python scripts/build_figures.py`

## Outputs
- Full build outputs are in `outputs/processed/`.
- Sample outputs are in `outputs/processed/sample/` and must not be treated as final analysis results.
- Generated bet-identification files are `satoshi_addresses.csv`, `satoshi_bet_outputs.csv.gz`, `bet_transactions.csv.gz`, and `identification_report.json`.
- Generated time-series files are `bet_percentage_by_day.csv`, `bet_percentage_by_week.csv`, and `bet_percentage_by_month.csv`.
- Generated address popularity file is `address_popularity.csv`.
- Generated payout files are `payout_matches.csv.gz` and `payout_distance_summary.csv`.
- Generated top-3 temporal distribution files are `top3_bet_distribution_by_hour.csv`, `top3_bet_distribution_by_day.csv`, and `top3_bet_distribution_by_week.csv`.
- Generated top-3 fee/amount files are `top3_fee_amount_points.csv.gz` and `top3_fee_amount_correlation.csv`.
- Generated top-3 interval files are `top3_bet_intervals.csv.gz` and `top3_bet_interval_summary.csv`.
- Generated simple-bet chain files are `simple_bets.csv.gz`, `simple_bet_chain_edges.csv.gz`, `simple_bet_chains.csv`, `simple_bet_chain_lengths.csv`, and `simple_bet_chain_summary.csv`.
- Generated figures are saved as PNG files under `outputs/figures/`.
- CSV/CSV.GZ is preferred over Parquet because the project is course-facing and uses standard formats.

## Next Logical Steps
- Implement WalletExplorer Selenium scraping with caching for chain address wallet lookups.

## Memory Maintenance
- Append or update this file after each important logical step: new pipeline stage, completed analysis, discovered dataset gotcha, fixed bug, or changed workflow.
- Do not erase useful previous context; prefer adding dated or sectioned notes when a past issue may help future agents.
- Preserve user-added code comments/reminders when editing files; do not rewrite or remove them unless the user explicitly asks.
