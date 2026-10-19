"""Time-weighted Dixon-Coles match model and season simulation.

Each team has an attack and a defence rating. Expected goals for a match are
    log(lambda_home) = mu + home + attack[home] - defence[away]
    log(lambda_away) = mu        + attack[away] - defence[home]
Matches are weighted by exp(-ln2 * age / half_life), so recent games count more,
and a small ridge penalty shrinks teams with few matches towards average. The
Dixon-Coles rho term then corrects the frequency of 0-0, 1-0, 0-1 and 1-1 scores.
Fitting on Championship, League One and League Two together lets teams that
change division carry their rating with them, which links the three scales.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.optimize import minimize, minimize_scalar
from scipy.stats import poisson

MAXG = 10


class DixonColes:
    def __init__(self, half_life: float = 240.0, ridge: float = 2.0):
        self.half_life, self.ridge = half_life, ridge

    def fit(self, m: pd.DataFrame, ref_date) -> "DixonColes":
        m = m[m.Date < ref_date]
        teams = sorted(set(m.HomeTeam) | set(m.AwayTeam))
        self.teams = teams
        idx = {t: i for i, t in enumerate(teams)}
        h = m.HomeTeam.map(idx).to_numpy(); a = m.AwayTeam.map(idx).to_numpy()
        yh = m.FTHG.to_numpy(float); ya = m.FTAG.to_numpy(float)
        age = (pd.Timestamp(ref_date) - m.Date).dt.days.to_numpy(float)
        w = np.exp(-np.log(2) * age / self.half_life)
        n = len(teams); r = self.ridge

        def unpack(p):
            return p[0], p[1], p[2:2 + n], p[2 + n:]

        def nll(p):
            mu, home, att, de = unpack(p)
            lh = mu + home + att[h] - de[a]; la = mu + att[a] - de[h]
            eh, ea = np.exp(lh), np.exp(la)
            ll = w * (yh * lh - eh + ya * la - ea)
            f = -ll.sum() + r * (att @ att + de @ de)
            rh = w * (yh - eh); ra = w * (ya - ea)
            g = np.zeros_like(p)
            g[0] = -(rh.sum() + ra.sum()); g[1] = -rh.sum()
            ga = -(np.bincount(h, rh, n) + np.bincount(a, ra, n)) + 2 * r * att
            gd = (np.bincount(a, rh, n) + np.bincount(h, ra, n)) + 2 * r * de
            g[2:2 + n] = ga; g[2 + n:] = gd
            return f, g

        p0 = np.zeros(2 + 2 * n); p0[0] = np.log(max(yh.mean(), 0.1))
        res = minimize(nll, p0, jac=True, method="L-BFGS-B")
        self.mu, self.home, att, de = unpack(res.x)
        self.attack = pd.Series(att, index=teams); self.defence = pd.Series(de, index=teams)
        lh, la = self._lams(m.HomeTeam, m.AwayTeam)
        self.rho = minimize_scalar(lambda rho: -(w * np.log(np.clip(
            _tau(yh, ya, lh, la, rho), 1e-10, None))).sum(),
            bounds=(-0.2, 0.2), method="bounded").x
        return self

    def _lams(self, home, away):
        att = self.attack.reindex(home).fillna(0).to_numpy(); dea = self.defence.reindex(away).fillna(0).to_numpy()
        ata = self.attack.reindex(away).fillna(0).to_numpy(); deh = self.defence.reindex(home).fillna(0).to_numpy()
        return (np.exp(self.mu + self.home + np.asarray(att) - dea),
                np.exp(self.mu + np.asarray(ata) - deh))

    def score_matrix(self, home: str, away: str) -> np.ndarray:
        lh, la = self._lams(pd.Index([home]), pd.Index([away]))
        g = np.arange(MAXG + 1)
        M = np.outer(poisson.pmf(g, lh[0]), poisson.pmf(g, la[0]))
        M[0, 0] *= 1 - lh[0] * la[0] * self.rho; M[0, 1] *= 1 + lh[0] * self.rho
        M[1, 0] *= 1 + la[0] * self.rho; M[1, 1] *= 1 - self.rho
        return M / M.sum()

    def predict(self, home: str, away: str) -> tuple[float, float, float]:
        M = self.score_matrix(home, away)
        return np.tril(M, -1).sum(), np.trace(M), np.triu(M, 1).sum()

    def ratings(self, teams=None) -> pd.DataFrame:
        """Expected goals for/against per game against an average team at a neutral venue."""
        mid = self.mu + self.home / 2
        df = pd.DataFrame({"attack": self.attack, "defence": self.defence})
        df["xg_for"] = np.exp(mid + df.attack); df["xg_against"] = np.exp(mid - df.defence)
        df["net"] = df.xg_for - df.xg_against
        return (df.loc[teams] if teams is not None else df).sort_values("net", ascending=False)


def _tau(x, y, lh, la, rho):
    t = np.ones_like(lh)
    t = np.where((x == 0) & (y == 0), 1 - lh * la * rho, t)
    t = np.where((x == 0) & (y == 1), 1 + lh * rho, t)
    t = np.where((x == 1) & (y == 0), 1 + la * rho, t)
    t = np.where((x == 1) & (y == 1), 1 - rho, t)
    return t


def rps(p: np.ndarray, outcome: np.ndarray) -> np.ndarray:
    """Ranked probability score for ordered outcomes (home, draw, away); lower is better."""
    o = np.zeros_like(p); o[np.arange(len(p)), outcome] = 1
    return ((np.cumsum(p, 1) - np.cumsum(o, 1))[:, :2] ** 2).sum(1) / 2


def walk_forward(all_m: pd.DataFrame, target: pd.DataFrame, half_life=240, ridge=2.0,
                 step_days=7) -> pd.DataFrame:
    """Refit every `step_days` on all matches before the block and predict the block."""
    target = target.sort_values("Date")
    start, end = target.Date.min(), target.Date.max()
    out = []
    t0 = start
    while t0 <= end:
        blk = target[(target.Date >= t0) & (target.Date < t0 + pd.Timedelta(days=step_days))]
        if len(blk):
            mdl = DixonColes(half_life, ridge).fit(all_m, t0)
            for r in blk.itertuples():
                ph, pd_, pa = mdl.predict(r.HomeTeam, r.AwayTeam)
                out.append((r.Index, ph, pd_, pa))
        t0 += pd.Timedelta(days=step_days)
    p = pd.DataFrame(out, columns=["i", "pH", "pD", "pA"]).set_index("i")
    return target.join(p)


def simulate_season(model: DixonColes, played: pd.DataFrame, teams: list[str],
                    n_sims: int = 10000, seed: int = 7) -> tuple[pd.DataFrame, np.ndarray]:
    """Simulate the unplayed fixtures of a double round-robin; returns positions per sim."""
    done = set(zip(played.HomeTeam, played.AwayTeam))
    fx = [(h, a) for h in teams for a in teams if h != a and (h, a) not in done]
    rng = np.random.default_rng(seed)
    idx = {t: i for i, t in enumerate(teams)}
    pts = np.zeros((n_sims, len(teams))); gd = np.zeros_like(pts); gf = np.zeros_like(pts)
    for r in played.itertuples():
        i, j = idx[r.HomeTeam], idx[r.AwayTeam]
        pts[:, i] += 3 * (r.FTHG > r.FTAG) + (r.FTHG == r.FTAG)
        pts[:, j] += 3 * (r.FTAG > r.FTHG) + (r.FTHG == r.FTAG)
        gd[:, i] += r.FTHG - r.FTAG; gd[:, j] += r.FTAG - r.FTHG; gf[:, i] += r.FTHG; gf[:, j] += r.FTAG
    for h, a in fx:
        M = model.score_matrix(h, a).ravel()
        k = rng.choice(M.size, size=n_sims, p=M)
        x, y = k // (MAXG + 1), k % (MAXG + 1)
        i, j = idx[h], idx[a]
        pts[:, i] += 3 * (x > y) + (x == y); pts[:, j] += 3 * (y > x) + (x == y)
        gd[:, i] += x - y; gd[:, j] += y - x; gf[:, i] += x; gf[:, j] += y
    key = pts * 1e6 + (gd + 500) * 1e3 + gf + rng.random(pts.shape) * 1e-3
    order = (-key).argsort(1)
    pos = np.empty_like(order); rows = np.arange(n_sims)[:, None]
    pos[rows, order] = np.arange(1, len(teams) + 1)
    summary = pd.DataFrame({"team": teams, "mean_pts": pts.mean(0),
                            "p10_pts": np.percentile(pts, 10, 0), "p90_pts": np.percentile(pts, 90, 0),
                            "mean_pos": pos.mean(0),
                            "p_top2": (pos <= 2).mean(0), "p_top6": (pos <= 6).mean(0),
                            "p_bottom4": (pos >= len(teams) - 3).mean(0)}).set_index("team")
    return summary.sort_values("mean_pts", ascending=False), pos
