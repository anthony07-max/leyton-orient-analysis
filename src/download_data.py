"""Download free match CSVs from football-data.co.uk into data/raw/.

football-data.co.uk publishes free results, match statistics and betting odds
for English leagues (https://www.football-data.co.uk/englandm.php). Please
credit the site if you reuse the data. Files are small (~100-300 KB each).

Usage:  python src/download_data.py
"""
from pathlib import Path
import time
import requests

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
BASE = "https://football-data.co.uk/mmz4281/{season}/{div}.csv"

# League One (E2) for every season from 2017/18 to the current one; League Two
# (E3) from 2019/20 (Orient's return to the EFL); the Championship (E1) from
# 2022/23. E1 and E3 let the match model rate promoted and relegated teams.
SEASONS = ["1718", "1819", "1920", "2021", "2122", "2223", "2324", "2425", "2526", "2627"]
FILES = [("E2", s) for s in SEASONS]
FILES += [("E3", s) for s in SEASONS[2:]]
FILES += [("E1", s) for s in SEASONS[5:]]


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    for div, season in FILES:
        out = RAW / f"{div}_{season}.csv"
        r = requests.get(BASE.format(season=season, div=div), timeout=60,
                         headers={"User-Agent": "orient-analysis (portfolio project)"})
        r.raise_for_status()
        out.write_bytes(r.content)
        print(f"{out.name}: {len(r.content)/1024:.0f} KB")
        time.sleep(1)  # be polite


if __name__ == "__main__":
    main()
