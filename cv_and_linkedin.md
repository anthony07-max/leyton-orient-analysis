# CV bullets, LinkedIn post and outreach note: Leyton Orient project

All figures below come from the executed notebook (`orient_analysis.ipynb`) and `results/key_numbers.json`. Data cut-off: table to 17 Oct 2026, xG and shots to 10 Oct 2026.

## CV bullet points (choose 2-3)

**Leyton Orient Performance Briefing & League One Match Model | Python, pandas, statsmodels, SciPy, ReportLab** · github.com/anthony07-max/leyton-orient-analysis

- Produced a two-page post-match and season briefing for Leyton Orient from free public data (football-data.co.uk results, shots, corners, odds and match xG). It showed that Orient sat 9th on points but 23rd of 24 on xG difference, with 11 points from games worth 8.2 expected points.
- Analysed 215 League One team-seasons (2017/18 to 2025/26) to separate signal from noise. Early-season shot-on-target share predicted the rest of the season (r = 0.49), while finishing and save rates barely persisted year to year (r = 0.08 and 0.16). A regression of points on shots on target (R² = 0.67) valued cutting Orient's shots on target conceded to top-six level at about +14 points a season.
- Built a time-weighted Dixon-Coles match model across the Championship, League One and League Two. Tested out of sample on all 552 League One matches of 2025/26, it scored a ranked probability score of 0.2184, against 0.2280 for base rates and 0.2097 for closing betting odds. I used it to simulate the rest of the 2026/27 season 10,000 times and preview fixtures.

*Shorter one-line version:* Built a Leyton Orient performance briefing and a validated Dixon-Coles League One model from free data. It found Orient 9th on points but 23rd on xG difference, and valued cutting shots on target conceded to top-six level at about +14 points a season.

## LinkedIn post

For my third football analytics project, I wrote the kind of briefing a club analyst might hand to coaching staff on a Monday morning, about my own club: Leyton Orient. ⚽🔴

League One event data isn't freely available, so I built it from free public data: football-data.co.uk's results, shots, corners, odds and (new this season) match xG, plus the published stats from Saturday's game.

What I did:
🔹 A post-match report on Orient 2-0 Blackpool (17 Oct): 37.7% possession and 3 corners to 11, but 6 shots on target to 4 and the only big chances
🔹 A season-so-far review using xG for and against, shot profile, corners and home/away splits
🔹 A test of 215 League One team-seasons (2017/18 to 2025/26) to see which early-season numbers actually predict the rest of a season
🔹 A Dixon-Coles match model, tested against the betting market, to project the rest of 2026/27

What I found:
✅ Orient are 9th on points but 23rd of 24 on xG difference after nine games with xG data: 11 points from games worth 8.2 expected points
✅ Finishing and save rates are mostly noise year to year (r = 0.08 and 0.16), but share of shots on target persists (r = 0.47), and Orient's is 45%
✅ The biggest lever is shots on target conceded: getting them down to top-six level is worth about +14 points a season in League One history
✅ The model closed about half the gap between naive base rates and the closing odds on 552 unseen matches, and gives Orient a 10% chance of the top six

There's a two-page staff briefing (PDF), and the notebook and write-up are on GitHub: https://github.com/anthony07-max/leyton-orient-analysis

Thanks to football-data.co.uk for making this data free. I'm looking for junior data and sports analytics roles in London, so I'd love to connect with anyone working in football analysis or recruitment.

#FootballAnalytics #SportsAnalytics #DataScience #LeytonOrient #EFL #LeagueOne #Python

## Outreach note to Leyton Orient's analysis or recruitment staff (draft, not sent)

**Subject:** A short data briefing on Orient's start to the season

Hi [name],

I'm an MSc Data Science graduate (University of East London) and an Orient fan, building a football analytics portfolio. As practice, I wrote a two-page briefing on our start to 2026/27 using only free public data: a post-match look at Saturday's 2-0 win over Blackpool, xG and shot trends for the season, and a simple League One match model.

The headline is that the table (9th) is ahead of the underlying numbers (23rd on xG difference so far). In League One history, the shots on target we concede look like the biggest lever. You will have far better data than I do, so I'm sharing this in case it's useful as an outside view, not as a pitch.

The PDF is attached, and the full method is here: https://github.com/anthony07-max/leyton-orient-analysis

If you ever had ten minutes, I'd be grateful for any feedback on what would make work like this more useful to a club like ours. Either way, thanks for reading, and good luck at Reading on Wednesday.

Best wishes,
Anthony Adusei-Poku
[LinkedIn URL] · [email]
