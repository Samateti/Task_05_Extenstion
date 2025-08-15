
# Syracuse Women’s Lacrosse 2025 – Advanced Performance Analysis

## Dataset Overview

This project analyzes the Syracuse Women’s Lacrosse 2025 season using:

* **`syracuse_lacrosse_2025_cleaned.csv`** – Match-level statistics (score, opponent, date, result).
* **`syracuse_lacrosse_2025_player_stats.csv`** – Player season statistics (goals, assists, games played, points).
* *(Optional)* **`syracuse_lacrosse_2025_player_game_logs.csv`** – Per-game player stats (enables Win/Loss splits & clutch performance analysis).
* *(Optional)* **`syracuse_lacrosse_2025_scoring_events.csv`** – Play-by-play scoring with scorer/assister info (enables synergy pair analysis).

## Core Analysis

The script computes:

1. **Baseline Season Snapshot** – Games played, W–L record, leaders in scoring, assists, PPG, and notable games.
2. **Pythagorean Expectation** – Compares expected vs actual win rate to assess “luck” or over/under-performance.
3. **Scoring Concentration** – Gini & HHI indices to measure offensive balance or reliance on a few players.
4. **Opponent Profiles** – Averages and margins vs each opponent; best and toughest matchups.
5. **Close-Game Records** – Performance in 1-, 2-, and ≤3-goal games.
6. **Team Momentum** – Rolling 3-game averages for scoring, defense, and margin to spot streaks.
7. **Player Efficiency & Reliability** – Offense share %, Z-scores for high-impact players.

## Bonus Analyses

* **Win/Loss Splits & Clutch Players** *(requires per-game logs)* – Compare individual stats in wins vs losses; identify top performers in close games.
* **Synergy Pairs** *(requires scorer/assister events)* – Find most frequent scorer–assister combinations.
* **Scoring Dynamics** – Correlation and OLS regression between SU and opponent scores as a pace proxy.

## Tools & Technologies

* Python 3.10+
* Pandas, NumPy
* CSV data files
* (Optional) Jupyter Notebook for exploration

## Interesting Insights (Example)

* Syracuse outperformed its Pythagorean win expectation by +1.2 wins.
* Offense Gini index of 0.34 → moderately balanced scoring.
* Best matchup: +6.5 avg margin vs Harvard; toughest: -2.0 vs Maryland.
* 3–0 record in 1-goal games shows strong clutch play.
* Emma Ward led with 46 assists and the highest share of total team points.
* Top synergy: Ward → Muchnick (14 goals created).

## How to Run

1. Install Python dependencies:

```bash
pip install pandas numpy
```

2. Place the CSV files in the same directory as the script (rename if needed to match the file paths in the code).
3. Run the script:

```bash
python advanced_lacrosse_analysis.py
```

4. View the printed output in the terminal.
   *(Optional)* Save results to CSV by modifying the script to include `.to_csv()` calls.

