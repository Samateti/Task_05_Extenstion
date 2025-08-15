import os
import math
import numpy as np
import pandas as pd

match_df = pd.read_csv("C:/Users/Sathvik/Downloads/syracuse_lacrosse_2025_cleaned.csv")
player_df = pd.read_csv("C:/Users/Sathvik/Downloads/syracuse_lacrosse_2025_player_stats.csv")

player_logs_path = "syracuse_lacrosse_2025_player_game_logs.csv"
scoring_events_path = "syracuse_lacrosse_2025_scoring_events.csv"

has_game_logs = os.path.exists(player_logs_path)
has_events = os.path.exists(scoring_events_path)

player_logs = pd.read_csv(player_logs_path) if has_game_logs else None
events = pd.read_csv(scoring_events_path) if has_events else None

match_df["Score_Diff"] = match_df["SU_Score"] - match_df["Opponent_Score"]
match_df["Abs_Diff"] = match_df["Score_Diff"].abs()

def gini(values: np.ndarray) -> float:
    v = np.array(values, dtype=float)
    v = v[v >= 0]
    if v.size == 0 or np.all(v == 0):
        return 0.0
    v_sorted = np.sort(v)
    n = v_sorted.size
    cum = np.cumsum(v_sorted)
    return 1.0 + 1.0/n - 2.0*np.sum(cum / cum[-1]) / n

def herfindahl(values: np.ndarray) -> float:
    v = np.array(values, dtype=float)
    tot = v.sum()
    if tot <= 0:
        return 0.0
    shares = v / tot
    return np.sum(shares**2)

def safe_pct(n, d) -> str:
    return "—" if d == 0 else f"{100*n/d:.1f}%"

def pythagorean_expectation(goals_for, goals_against, exponent=2.2) -> float:
    gf_e = goals_for ** exponent
    ga_e = goals_against ** exponent
    denom = gf_e + ga_e
    return float(gf_e / denom) if denom > 0 else np.nan

def print_header(title):
    print("\n" + "="*len(title))
    print(title)
    print("="*len(title))

print_header("Baseline Season Snapshot")

match_count = match_df.shape[0]
wins = (match_df["Result"] == "W").sum()
losses = (match_df["Result"] == "L").sum()

player_df = player_df.copy()
player_df["Avg_Points"] = player_df["Points"] / player_df["Games_Played"]
player_df["Goal_Rate"] = player_df["Goals"] / player_df["Games_Played"]

leading_scorer = player_df.sort_values("Goals", ascending=False).iloc[0]
top_avg_point_player = player_df.sort_values("Avg_Points", ascending=False).iloc[0]
tightest_match = match_df.sort_values("Abs_Diff").iloc[0]
highest_scoring_match = match_df.sort_values("SU_Score", ascending=False).iloc[0]
assist_king = player_df.sort_values("Assists", ascending=False).iloc[0]
close_defeat_count = ((match_df["Result"] == "L") & (match_df["Score_Diff"] >= -3)).sum()
top_win = match_df[match_df["Result"] == "W"].sort_values("Score_Diff", ascending=False).iloc[0]

print(f"Games: {match_count}  |  W-L: {wins}-{losses}")
print(f"Leading scorer: {leading_scorer['Player']} ({leading_scorer['Goals']} goals)")
print(f"Top PPG: {top_avg_point_player['Player']} ({top_avg_point_player['Avg_Points']:.2f})")
print(f"Tightest match: vs {tightest_match['Opponent']} on {tightest_match['Date']} ({tightest_match['SU_Score']}-{tightest_match['Opponent_Score']})")
print(f"Highest SU score: {highest_scoring_match['SU_Score']} vs {highest_scoring_match['Opponent']}")
print(f"Assist leader: {assist_king['Player']} ({assist_king['Assists']})")
print(f"Narrow defeats (≤3): {close_defeat_count}")
print(f"Biggest win: {top_win['SU_Score']}-{top_win['Opponent_Score']} vs {top_win['Opponent']} on {top_win['Date']} (margin {top_win['Score_Diff']})")

print_header("1) Pythagorean Expectation")
GF = match_df["SU_Score"].sum()
GA = match_df["Opponent_Score"].sum()
pyth_win_pct = pythagorean_expectation(GF, GA)
actual_win_pct = wins / match_count if match_count > 0 else np.nan
exp_wins = pyth_win_pct * match_count if not np.isnan(pyth_win_pct) else np.nan
luck = wins - exp_wins if not np.isnan(exp_wins) else np.nan
print(f"Goals For: {GF}, Goals Against: {GA}")
print(f"Expected Win%: {pyth_win_pct:.3f}")
print(f"Actual Win%: {actual_win_pct:.3f}")
print(f"Expected Wins: {exp_wins:.2f} vs Actual Wins: {wins}  →  Luck: {luck:+.2f}")

print_header("2) Scoring Concentration")
gini_goals = gini(player_df["Goals"].values)
gini_points = gini(player_df["Points"].values)
hhi_goals = herfindahl(player_df["Goals"].values)
hhi_points = herfindahl(player_df["Points"].values)
print(f"Gini(Goals): {gini_goals:.3f}  |  Gini(Points): {gini_points:.3f}")
print(f"HHI(Goals): {hhi_goals:.3f}   |  HHI(Points): {hhi_points:.3f}")

team_points = player_df["Points"].sum()
player_df["Offense_Share_%"] = 100 * player_df["Points"] / team_points if team_points > 0 else 0
top_offense_share = player_df.sort_values("Offense_Share_%", ascending=False).head(5)[["Player", "Points", "Offense_Share_%"]]
print("\nTop 5 offense shares (by Points):")
print(top_offense_share.to_string(index=False, formatters={"Offense_Share_%": lambda x: f"{x:.1f}%"}))

print_header("3) Opponent Profiles")
opp_summary = match_df.groupby("Opponent", as_index=False).agg(
    Games=("Opponent", "size"),
    Avg_GF=("SU_Score", "mean"),
    Avg_GA=("Opponent_Score", "mean"),
    Avg_Margin=("Score_Diff", "mean"),
    Wins=("Result", lambda s: (s=="W").sum())
)
opp_summary["Win%"] = opp_summary["Wins"] / opp_summary["Games"]
print(opp_summary.sort_values("Avg_Margin", ascending=False).to_string(index=False, float_format=lambda x: f"{x:.2f}"))

best_opp = opp_summary.sort_values("Avg_Margin", ascending=False).head(3)
tough_opp = opp_summary.sort_values("Avg_Margin").head(3)
print("\nBest Opponents by Avg Margin:")
print(best_opp.to_string(index=False, float_format=lambda x: f"{x:.2f}"))
print("\nToughest Opponents by Avg Margin:")
print(tough_opp.to_string(index=False, float_format=lambda x: f"{x:.2f}"))

print_header("4) Close-Game Performance")
def record_for_filter(df):
    w = (df["Result"]=="W").sum()
    l = (df["Result"]=="L").sum()
    return f"{w}-{l} ({safe_pct(w, w+l)})"

one_goal = match_df[match_df["Abs_Diff"] == 1]
two_goal = match_df[match_df["Abs_Diff"] == 2]
three_or_less = match_df[match_df["Abs_Diff"] <= 3]
print(f"1-goal games: {len(one_goal)} | Record: {record_for_filter(one_goal)}")
print(f"2-goal games: {len(two_goal)} | Record: {record_for_filter(two_goal)}")
print(f"≤3-goal games: {len(three_or_less)} | Record: {record_for_filter(three_or_less)}")

print_header("5) Team Momentum")
try:
    match_df["Date"] = pd.to_datetime(match_df["Date"])
    ms_sorted = match_df.sort_values("Date").reset_index(drop=True)
except Exception:
    ms_sorted = match_df.reset_index(drop=True)

window = 3
ms_sorted["SU_Roll_Avg"] = ms_sorted["SU_Score"].rolling(window, min_periods=1).mean()
ms_sorted["Opp_Roll_Avg"] = ms_sorted["Opponent_Score"].rolling(window, min_periods=1).mean()
ms_sorted["Margin_Roll_Avg"] = ms_sorted["Score_Diff"].rolling(window, min_periods=1).mean()
print(ms_sorted[["Date","Opponent","SU_Score","Opponent_Score","Score_Diff","SU_Roll_Avg","Opp_Roll_Avg","Margin_Roll_Avg"]]
      .to_string(index=False, float_format=lambda x: f"{x:.2f}"))

best_streak = ms_sorted.sort_values("Margin_Roll_Avg", ascending=False).head(1)
worst_streak = ms_sorted.sort_values("Margin_Roll_Avg", ascending=True).head(1)
print("\nBest 3-game rolling stretch:")
print(best_streak[["Date","Opponent","Margin_Roll_Avg"]].to_string(index=False, float_format=lambda x: f"{x:.2f}"))
print("\nToughest 3-game rolling stretch:")
print(worst_streak[["Date","Opponent","Margin_Roll_Avg"]].to_string(index=False, float_format=lambda x: f"{x:.2f}"))

print_header("6) Player Efficiency & Reliability")
team_points = player_df["Points"].sum()
team_goals = player_df["Goals"].sum()
player_df["Share_of_Team_Points_%"] = 100 * player_df["Points"] / team_points if team_points > 0 else 0
player_df["Share_of_Team_Goals_%"] = 100 * player_df["Goals"] / team_goals if team_goals > 0 else 0
for col in ["Goals","Assists","Points","Avg_Points"]:
    mu = player_df[col].mean()
    sd = player_df[col].std(ddof=0)
    player_df[f"Z_{col}"] = (player_df[col]-mu)/sd if sd > 0 else 0
eff_cols = ["Player","Games_Played","Goals","Assists","Points","Avg_Points",
            "Share_of_Team_Points_%","Share_of_Team_Goals_%","Z_Points","Z_Avg_Points"]
print(player_df[eff_cols].sort_values("Avg_Points", ascending=False)
      .to_string(index=False, float_format=lambda x: f"{x:.2f}"))

if has_game_logs:
    print_header("BONUS A) Win/Loss Splits & Clutch")
    try:
        player_logs["Date"] = pd.to_datetime(player_logs["Date"])
        match_df["Date"] = pd.to_datetime(match_df["Date"])
    except Exception:
        pass
    merge_keys = ["Date","Opponent"]
    merged = pd.merge(
        player_logs,
        match_df[merge_keys + ["Result","Score_Diff","SU_Score","Opponent_Score"]],
        on=merge_keys,
        how="inner"
    )
    wl = merged.groupby(["Player","Result"], as_index=False).agg(
        Games=("Points","size"),
        Avg_Points=("Points","mean"),
        Avg_Goals=("Goals","mean"),
        Avg_Assists=("Assists","mean")
    )
    wl_pivot = wl.pivot(index="Player", columns="Result",
                        values=["Games","Avg_Points","Avg_Goals","Avg_Assists"]).fillna(0)
    wl_pivot.columns = [f"{a}_{b}" for a,b in wl_pivot.columns]
    print("Win/Loss per-player splits:")
    print(wl_pivot.sort_values("Avg_Points_W", ascending=False).head(15).to_string(float_format=lambda x: f"{x:.2f}"))
    close = merged[merged["Score_Diff"].abs() <= 3]
    if not close.empty:
        clutch = close.groupby("Player", as_index=False).agg(
            Games=("Points","size"),
            Clutch_PPG=("Points","mean"),
            Clutch_G=("Goals","mean"),
            Clutch_A=("Assists","mean")
        )
        print("\nClutch performers:")
        print(clutch.sort_values("Clutch_PPG", ascending=False).head(15).to_string(index=False, float_format=lambda x: f"{x:.2f}"))
    else:
        print("\nNo close-game rows found in per-game logs.")

if has_events and "Assister" in events.columns and "Scorer" in events.columns:
    print_header("BONUS B) Synergy Pairs")
    valid = events.dropna(subset=["Scorer","Assister"])
    pair_counts = valid.groupby(["Assister","Scorer"], as_index=False).size().rename(columns={"size":"Goals_Created"})
    pair_top = pair_counts.sort_values("Goals_Created", ascending=False).head(20)
    print(pair_top.to_string(index=False))

print_header("BONUS C) Scoring Dynamics")
corr = np.corrcoef(match_df["SU_Score"], match_df["Opponent_Score"])[0,1]
print(f"Correlation(SU_Score, Opponent_Score): {corr:.3f}")
X = np.vstack([np.ones(len(match_df)), match_df["Opponent_Score"].values]).T
y = match_df["SU_Score"].values
try:
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    print(f"OLS: SU_Score ≈ {beta[0]:.2f} + {beta[1]:.2f} * Opponent_Score")
except Exception as e:
    print(f"OLS failed: {e}")

print("\nDone.")
