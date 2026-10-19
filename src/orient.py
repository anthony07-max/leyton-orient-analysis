"""Data loading and analysis helpers for the Leyton Orient project."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
MANUAL = ROOT / "manual"
TEAM = "Leyton Orient"

KEEP = ["Div", "Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR", "HTHG", "HTAG",
        "HxG", "AxG", "HS", "AS", "HST", "AST", "HC", "AC", "HF", "AF", "HY", "AY", "HR", "AR",
        "AvgCH", "AvgCD", "AvgCA", "AvgC>2.5", "AvgC<2.5", "PSCH", "PSCD", "PSCA"]


def season_label(code: str) -> str:
    return f"20{code[:2]}/{code[2:]}"


def load_matches(div: str = "E2", seasons: list[str] | None = None,
                 include_manual: bool = True) -> pd.DataFrame:
    """One row per match from football-data.co.uk CSVs (plus hand-entered recent results)."""
    files = sorted(RAW.glob(f"{div}_*.csv"))
    frames = []
    for f in files:
        code = f.stem.split("_")[1]
        if seasons and code not in seasons:
            continue
        d = pd.read_csv(f, encoding="utf-8-sig", on_bad_lines="skip")
        d = d.dropna(subset=["HomeTeam", "AwayTeam", "FTHG"])
        d = d[[c for c in KEEP if c in d.columns]].copy()
        d["season"] = season_label(code)
        d["source"] = "football-data.co.uk"
        frames.append(d)
    m = pd.concat(frames, ignore_index=True)
    if include_manual and div == "E2" and (seasons is None or "2627" in seasons):
        x = pd.read_csv(MANUAL / "league_one_results_2026-10-15_to_17.csv")
        x["Div"], x["season"], x["source"] = "E2", "2026/27", "manual"
        x["FTR"] = np.select([x.FTHG > x.FTAG, x.FTHG < x.FTAG], ["H", "A"], "D")
        m = pd.concat([m, x.drop(columns="Source")], ignore_index=True)
    m["Date"] = pd.to_datetime(m["Date"], dayfirst=True, format="mixed")
    # if the football-data file catches up, drop the duplicate manual rows
    m = m.drop_duplicates(subset=["Date", "HomeTeam", "AwayTeam"], keep="first")
    return m.sort_values("Date", kind="stable").reset_index(drop=True)


def team_view(m: pd.DataFrame) -> pd.DataFrame:
    """Two rows per match: one from each team's perspective."""
    pairs = {"FTHG": "FTAG", "HTHG": "HTAG", "HxG": "AxG", "HS": "AS", "HST": "AST",
             "HC": "AC", "HF": "AF", "HY": "AY", "HR": "AR"}
    names = {"FTHG": "gf", "HTHG": "ht_gf", "HxG": "xgf", "HS": "sf", "HST": "sotf",
             "HC": "cf", "HF": "fouls", "HY": "yc", "HR": "rc"}
    against = {"FTHG": "ga", "HTHG": "ht_ga", "HxG": "xga", "HS": "sa", "HST": "sota",
               "HC": "ca", "HF": "fouls_against", "HY": "yc_opp", "HR": "rc_opp"}
    rows = []
    for home in (True, False):
        d = pd.DataFrame({"season": m.season, "Date": m.Date, "source": m.source,
                          "team": m.HomeTeam if home else m.AwayTeam,
                          "opp": m.AwayTeam if home else m.HomeTeam,
                          "venue": "H" if home else "A"})
        for h, a in pairs.items():
            if h not in m.columns:
                continue
            d[names[h]] = m[h] if home else m[a]
            d[against[h]] = m[a] if home else m[h]
        # closing market probabilities (average of bookmakers, overround removed)
        if {"AvgCH", "AvgCD", "AvgCA"} <= set(m.columns):
            inv = 1 / m[["AvgCH", "AvgCD", "AvgCA"]]
            p = inv.div(inv.sum(axis=1), axis=0)
            d["p_win_mkt"] = p["AvgCH"] if home else p["AvgCA"]
            d["p_draw_mkt"] = p["AvgCD"]
            d["p_loss_mkt"] = p["AvgCA"] if home else p["AvgCH"]
        rows.append(d)
    t = pd.concat(rows, ignore_index=True).sort_values(["Date", "team"]).reset_index(drop=True)
    t["pts"] = np.select([t.gf > t.ga, t.gf == t.ga], [3, 1], 0)
    t["result"] = np.select([t.gf > t.ga, t.gf == t.ga], ["W", "D"], "L")
    return t


def league_table(m: pd.DataFrame) -> pd.DataFrame:
    t = team_view(m)
    g = t.groupby("team").agg(P=("pts", "size"), W=("result", lambda s: (s == "W").sum()),
                              D=("result", lambda s: (s == "D").sum()),
                              L=("result", lambda s: (s == "L").sum()),
                              GF=("gf", "sum"), GA=("ga", "sum"), Pts=("pts", "sum"))
    g["GD"] = g.GF - g.GA
    g = g.sort_values(["Pts", "GD", "GF"], ascending=False)
    g.insert(0, "Pos", range(1, len(g) + 1))
    return g[["Pos", "P", "W", "D", "L", "GF", "GA", "GD", "Pts"]].astype(int)
