"""Build the two-page staff briefing PDF from results/key_numbers.json and figures/.

Run after executing the notebook:  python src/make_briefing.py
"""
import json
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)

ROOT = Path(__file__).resolve().parents[1]
k = json.loads((ROOT / "results" / "key_numbers.json").read_text())
OUT = ROOT / "reports" / "Leyton_Orient_staff_briefing_2026-10-19.pdf"
RED = colors.HexColor("#D7182A")

ss = getSampleStyleSheet()
H1 = ParagraphStyle("h1", parent=ss["Title"], fontSize=15, leading=18, alignment=TA_LEFT, spaceAfter=2, textColor=RED)
SUB = ParagraphStyle("sub", parent=ss["Normal"], fontSize=8, leading=10, textColor=colors.HexColor("#555555"))
H2 = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=10.5, leading=13, spaceBefore=5, spaceAfter=2, textColor=RED)
B = ParagraphStyle("b", parent=ss["Normal"], fontSize=8.4, leading=10.6)
BL = ParagraphStyle("bl", parent=B, leftIndent=9, bulletIndent=0)
SM = ParagraphStyle("sm", parent=B, fontSize=7, leading=8.6, textColor=colors.HexColor("#444444"))


def bullets(items, style=BL):
    return [Paragraph(t, style, bulletText="•") for t in items]


def img(name, width):
    from reportlab.lib.utils import ImageReader
    p = ROOT / "figures" / name
    w, h = ImageReader(str(p)).getSize()
    return Image(str(p), width=width, height=width * h / w)


pct = lambda x: f"{100 * x:.0f}%"
s = k["sim"]; lv = k["lever"]; pr = k["profile"]; val = k["val"]
gf, xg = k["o_gf_xg"]; ga, xga = k["o_ga_xga"]
W = A4[0] - 3 * cm

story = [
    Paragraph("Leyton Orient: post-match and performance briefing", H1),
    Paragraph("Prepared 19 Oct 2026 by Anthony Adusei-Poku (independent analysis from public data, not club data). "
              "League One table to 17 Oct 2026; match xG and shot data to 10 Oct 2026.", SUB),
    Spacer(1, 4),
    Paragraph("Key points", H2),
    *bullets([
        f"<b>Blackpool (H) 2-0, 17 Oct:</b> won with 37.7% possession and 3 corners to 11, but 6 shots on target to 4 and 3 big chances missed to 0. "
        f"Second clean sheet in a row after 0-0 at Bradford, where Bradford had no shots on target.",
        f"<b>Table vs process:</b> {k['orient_pos']}th on {k['orient_pts']} points ({k['orient_wdl'][0]}W {k['orient_wdl'][1]}D {k['orient_wdl'][2]}L), "
        f"but <b>{k['o_xgd_rank']}rd of 24 on xG difference</b> ({k['o_xgd_pg']:+.2f} per game). Over the first 9 games Orient scored {gf} from {xg:.1f} xG and conceded {ga} from {xga:.1f} xG.",
        f"<b>Biggest lever: shots on target conceded.</b> Orient face {lv['sota']:.2f} a game (top-six average {lv['top6_sota']:.2f}). "
        f"League One history values closing that gap at about <b>+{lv['pts46_sota']:.0f} points a season</b>, more than matching top-six creation (+{lv['pts46_sotf']:.0f}).",
        f"<b>Sustainability risk:</b> points are being held up by finishing (0.39 goals per shot on target) and saves (0.73 save rate), both above top-six averages. "
        f"Across 215 League One team-seasons these rates barely carry over; shot-on-target share does.",
        f"<b>Projection:</b> a Dixon-Coles model simulated 10,000 times gives a mean of {s['mean_pts']:.0f} points, "
        f"{pct(s['p_top6'])} chance of the top six and {pct(s['p_bottom4'])} of the bottom four. Next: Reading (A) Wed 21 Oct, the division's 2nd-best side by xG difference.",
    ]),
    Paragraph("1. Post-match: Leyton Orient 2-0 Blackpool (Sat 17 Oct 2026)", H2),
    Table([[img("01_blackpool_match_stats.png", W * 0.56),
            [Paragraph("Goals: Forrester 31' (header, Gilbert cross), Scarlett 76' (pen). Att. 8,055.", B), Spacer(1, 3),
             *bullets([
                 "<b>Out of possession by design:</b> 271 passes attempted to 446; Blackpool had 26 touches in Orient's box to 16 and won 31 aerials to 18.",
                 "<b>Efficient in transition:</b> 6 of 14 shots on target, 3 big chances missed, Olowu header off the bar before the penalty.",
                 "<b>Watch-point:</b> 11 corners conceded here and 11 at Bradford. Orient concede 6.8 corners a game (20th) and win 3.7 (23rd), so set-piece defending is a high-volume task.",
                 "<b>Box defending held:</b> 20 headed clearances; Forrester cleared Ashworth's header off the line.",
             ])]]], colWidths=[W * 0.58, W * 0.42], style=[("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]),
    Paragraph("2. Season so far: results ahead of the process", H2),
    img("02_season_xg_trend.png", W * 0.98),
    Paragraph(f"Away form is strong (4 games, {k['o_away'][1]} pts, {k['o_away'][2]}-{k['o_away'][3]}); home form is not "
              f"({k['o_home'][0]} games, {k['o_home'][1]} pts, {k['o_home'][2]}-{k['o_home'][3]}). The 5-0 at Bromley (1.67 xG) supplies 4 of the 13 goals in the xG sample. "
              f"Orient take {k['o_shots_pg'][0]} shots a game (22nd) at {k['o_xg_per_shot'][0]:.3f} xG per shot (league {k['lg_xg_per_shot']:.3f}) and face {k['o_shots_pg'][1]} (19th).", B),
    PageBreak(),
    Paragraph("3. What drives League One points, and where Orient stand", H2),
    Table([[img("07_orient_multiseason_profile.png", W * 0.60), [
        *bullets([
            f"<b>2024/25 (6th, 78 pts):</b> SoT share {pr['2024/25']['SoT share']:.0%}, finishing {pr['2024/25']['Goals per SoT']:.2f} goals per SoT.",
            f"<b>2025/26 (20th, 52 pts):</b> SoT share fell to {pr['2025/26']['SoT share']:.0%}; SoT conceded rose to {pr['2025/26']['SoT against']:.1f} a game; save rate {pr['2025/26']['Save rate']:.2f}.",
            f"<b>2026/27 (9 games):</b> SoT share {pr['2026/27']['SoT share']:.0%}, shots against {pr['2026/27']['Shots against']:.1f} a game (top-six avg {pr['Top-six average 2017/18-2025/26']['Shots against']:.1f}).",
            f"Game state: in 2025/26 Orient took {k['gamestate']['level_ppg']['2025/26']:.2f} pts per game from {k['gamestate']['level_n']['2025/26']} matches level at half-time (league avg {k['gamestate']['league_level_ppg']:.2f}), roughly 10 points lost.",
        ])]]], colWidths=[W * 0.62, W * 0.38], style=[("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]),
    Table([[img("08_improvement_levers.png", W * 0.55),
            Paragraph(f"Regression on {k['reg']['n']} League One team-seasons (2017/18-2025/26): each extra shot on target per game is worth about "
                      f"<b>+{lv['per1_sot_46']:.1f} points a season</b>, each one conceded about <b>-{lv['per1_sota_46']:.1f}</b> (R² {k['reg']['r2']:.2f}). "
                      f"On current rates it expects {lv['ppg_pred_now']:.2f} points per game ({lv['pts46_pred_now']:.0f} over 46).<br/><br/>"
                      f"What to trust early: over the first 9 games, shot and shot-on-target shares correlate about 0.49 with points over the rest of a season, "
                      f"and 0.47-0.51 from one season to the next. Finishing (0.20; 0.08 year to year) and save rate (0.10; 0.16) are mostly noise.", B)]],
          colWidths=[W * 0.57, W * 0.43], style=[("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]),
    Paragraph("4. Next three fixtures and season outlook", H2),
]
rows = [["Date", "Fixture", "Orient win", "Draw", "Orient loss", "Opp. xGD rank", "Opponent profile (2026/27 to 10 Oct)"]]
opp = k["opp_prof"]
desc = {"Reading": "2.05 xG for, 0.97 against per game; 16.6 shots a game", "Burton": "0.83 xG for, 1.51 against; 10.1 shots a game",
        "Cambridge": "1.13 xG for, 1.42 against; 7.0 corners won a game"}
for r, name in zip(k["next"], ["Reading", "Burton", "Cambridge"]):
    rows.append([r["date"][8:10] + " Oct", r["fixture"].replace("Leyton Orient", "Orient"), pct(r["Orient win"]), pct(r["draw"]),
                 pct(r["Orient loss"]), f"{opp[name]['xgd_rank']} of 24", Paragraph(desc[name], SM)])
t = Table(rows, colWidths=[1.3 * cm, 3.6 * cm, 1.6 * cm, 1.2 * cm, 1.7 * cm, 2.5 * cm, W - 11.9 * cm])
t.setStyle(TableStyle([("FONTSIZE", (0, 0), (-1, -1), 7.6), ("BACKGROUND", (0, 0), (-1, 0), RED), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                       ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
story += [t, Spacer(1, 3), Table([[img("10_season_projection.png", W * 0.58), [
    *bullets([
        f"Projected points {s['mean_pts']:.0f} (80% range {s['p10_pts']:.0f}-{s['p90_pts']:.0f}); median finish {k['sim_median_pos']}th (80% range {k['sim_pos_p10_p90'][0]}th-{k['sim_pos_p10_p90'][1]}th).",
        f"Top six {pct(s['p_top6'])}; automatic promotion {pct(s['p_top2'])}; bottom four {pct(s['p_bottom4'])}.",
        f"The model uses scores only (rates Orient {k['dc_rank']}th); on xG they rank {k['o_xgd_rank']}rd, so this outlook is if anything generous.",
        f"Validated out of sample on all {k['val_n']} League One 2025/26 matches: RPS {val['Dixon-Coles (scores only)']['RPS']:.4f} vs {val['Base rates (2024/25 H/D/A)']['RPS']:.4f} for base rates and {val['Betting market (closing avg)']['RPS']:.4f} for the closing market.",
    ])]]], colWidths=[W * 0.6, W * 0.4], style=[("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]),
    Paragraph("<b>Data and limits.</b> Results, shots, corners, odds and match xG: football-data.co.uk (free CSVs; the provider of the new 2026/27 xG column is not documented, "
              "so xG is treated as indicative, and it tracks shots on target with r = 0.64). Orient v Blackpool stats: Sky Sports match page. Results 15-17 Oct: Football Web Pages. "
              "No shot locations, set-piece tags or player data are freely available for League One, so set pieces are measured by corner volume only. Nine or ten matches is a small sample. "
              "Full method and code: github.com/anthony07-max/leyton-orient-analysis", SM)]

doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=1.5 * cm, rightMargin=1.5 * cm, topMargin=1.2 * cm, bottomMargin=1.0 * cm,
                        title="Leyton Orient post-match and performance briefing, 19 Oct 2026", author="Anthony Adusei-Poku")
doc.build(story)
print("wrote", OUT)
