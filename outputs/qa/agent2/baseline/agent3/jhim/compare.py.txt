"""Perbandingan antar-model. Semua metrik dihitung pada himpunan grid valid BERSAMA (kolom `valid`)."""
from __future__ import annotations

import itertools

import numpy as np
import pandas as pd

from . import config as C


def model_keys(pri: pd.DataFrame) -> list[str]:
    return sorted({c.split("_")[0] for c in pri.columns if c.endswith("_score")})


def _valid(pri: pd.DataFrame) -> pd.DataFrame:
    v = pri.loc[pri["valid"].astype(bool)]
    for k in model_keys(pri):
        if v[f"{k}_score"].isna().any():
            raise ValueError(f"{k}: skor kosong di grid valid; himpunan grid antar-model tidak sama.")
    return v


def spearman_matrix(pri: pd.DataFrame, keys=None) -> pd.DataFrame:
    keys = keys or model_keys(pri)
    v = _valid(pri)
    m = v[[f"{k}_score" for k in keys]].astype(float).corr(method="spearman")
    m.index = m.columns = [k.upper() for k in keys]
    return m


def kendall_matrix(pri: pd.DataFrame, keys=None) -> pd.DataFrame:
    """Kendall tau-b antar skor (lebih tahan terhadap seri dan mudah diinterpretasi sebagai pasangan konkordan)."""
    from scipy.stats import kendalltau

    keys = keys or model_keys(pri)
    v = _valid(pri)
    lab = [k.upper() for k in keys]
    m = pd.DataFrame(np.eye(len(keys)), index=lab, columns=lab)
    for (i, a), (j, b) in itertools.combinations(enumerate(keys), 2):
        t = kendalltau(v[f"{a}_score"].astype(float), v[f"{b}_score"].astype(float)).statistic
        m.iat[i, j] = m.iat[j, i] = float(t)
    return m


def _tops(pri, keys, frac=None):
    from .models import n_top

    v = _valid(pri)
    if frac is None:
        return {k: set(v.loc[v[f"{k}_top"].astype(bool), C.KEY]) for k in keys}
    nt = n_top(len(v), frac)
    return {k: set(v.loc[v[f"{k}_rank"] <= nt, C.KEY]) for k in keys}


def jaccard(a: set, b: set) -> float:
    u = len(a | b)
    return len(a & b) / u if u else np.nan


def jaccard_matrix(pri: pd.DataFrame, keys=None, frac=None) -> pd.DataFrame:
    keys = keys or model_keys(pri)
    tops = _tops(pri, keys, frac)
    lab = [k.upper() for k in keys]
    m = pd.DataFrame(index=lab, columns=lab, dtype=float)
    for a, b in itertools.product(keys, keys):
        m.loc[a.upper(), b.upper()] = jaccard(tops[a], tops[b])
    return m


def overlap_table(pri: pd.DataFrame, keys=None, fracs=C.TOP_FRACS) -> pd.DataFrame:
    """Overlap himpunan prioritas tinggi untuk beberapa ambang (top 5/10/20%)."""
    keys = keys or model_keys(pri)
    rows = []
    for f in fracs:
        tops = _tops(pri, keys, f)
        for a, b in itertools.combinations(keys, 2):
            ta, tb = tops[a], tops[b]
            rows.append({
                "top_frac": f, "model_a": a.upper(), "model_b": b.upper(), "n_top": len(ta),
                "n_shared": len(ta & tb), "jaccard": jaccard(ta, tb),
                "share_of_a_retained": len(ta & tb) / len(ta) if ta else np.nan,
            })
    return pd.DataFrame(rows)


def rank_movement(pri: pd.DataFrame, keys=None) -> pd.DataFrame:
    """Ringkasan perubahan peringkat absolut per pasangan model."""
    keys = keys or model_keys(pri)
    v = _valid(pri)
    n = len(v)
    rows = []
    for a, b in itertools.combinations(keys, 2):
        d = (v[f"{a}_rank"].astype(int) - v[f"{b}_rank"].astype(int))
        ad = d.abs()
        rows.append({
            "model_a": a.upper(), "model_b": b.upper(), "n_valid": n,
            "mean_abs_shift": float(ad.mean()), "median_abs_shift": float(ad.median()),
            "p90_abs_shift": float(ad.quantile(0.9)), "max_abs_shift": int(ad.max()),
            "pct_shift_gt_10pct_n": 100 * float((ad > 0.10 * n).mean()),
            "pct_unchanged": 100 * float((ad == 0).mean()),
        })
    return pd.DataFrame(rows)


def pairwise_long(pri: pd.DataFrame, keys=None) -> pd.DataFrame:
    """Tabel panjang untuk model_comparison.csv: metrik, model_a, model_b, nilai, n_valid."""
    keys = keys or model_keys(pri)
    sp, kt, ja = spearman_matrix(pri, keys), kendall_matrix(pri, keys), jaccard_matrix(pri, keys)
    mv = rank_movement(pri, keys).set_index(["model_a", "model_b"])
    n = int(_valid(pri).shape[0])
    rows = []
    for a, b in itertools.combinations([k.upper() for k in keys], 2):
        for met, val in (("spearman_skor", sp.loc[a, b]), ("kendall_tau_b", kt.loc[a, b]),
                         ("jaccard_top", ja.loc[a, b]), ("mean_abs_rank_shift", mv.loc[(a, b), "mean_abs_shift"]),
                         ("median_abs_rank_shift", mv.loc[(a, b), "median_abs_shift"])):
            rows.append({"metrik": met, "model_a": a, "model_b": b, "nilai": float(val), "n_valid": n})
    return pd.DataFrame(rows)


def transition_matrix(pri: pd.DataFrame, a: str = "m1", b: str = "m4", normalize: bool = False) -> pd.DataFrame:
    """Matriks transisi kelas prioritas dari model a (baris) ke model b (kolom)."""
    v = _valid(pri)
    t = pd.crosstab(v[f"{a}_class"], v[f"{b}_class"], rownames=[a.upper()], colnames=[b.upper()])
    t = t.reindex(index=list(C.CLASS_LABELS), columns=list(C.CLASS_LABELS), fill_value=0)
    if normalize:
        t = t.div(t.sum(axis=1).replace(0, np.nan), axis=0)
    return t


def score_summary(pri: pd.DataFrame, keys=None) -> pd.DataFrame:
    keys = keys or model_keys(pri)
    v = _valid(pri)
    rows = []
    for k in keys:
        s = v[f"{k}_score"].astype(float)
        rows.append({"model": k.upper(), "n": int(s.size), "mean": s.mean(), "sd": s.std(), "min": s.min(),
                     "p05": s.quantile(0.05), "p25": s.quantile(0.25), "median": s.median(),
                     "p75": s.quantile(0.75), "p95": s.quantile(0.95), "max": s.max(),
                     "n_ties_at_max": int((s == s.max()).sum())})
    return pd.DataFrame(rows)


def top_coverage(pri: pd.DataFrame, feat: pd.DataFrame, keys=None) -> pd.DataFrame:
    """Siapa dan apa yang ada di grid teratas tiap model (dibanding semua grid valid)."""
    keys = keys or model_keys(pri)
    cols = [C.KEY, "population", "pop_child", "pop_elderly", "lst_c", "ndvi", "park_distance_m"]
    j = pri[[C.KEY, "valid", *[f"{k}_top" for k in keys]]].merge(feat[cols], on=C.KEY, how="left", validate="one_to_one")
    j = j.loc[j["valid"].astype(bool)].copy()
    j["vulnerable"] = j["pop_child"] + j["pop_elderly"]
    tot_pop, tot_vul = float(j["population"].sum()), float(j["vulnerable"].sum())

    def row(label, sub):
        return {
            "kelompok": label,
            "n_grid": int(len(sub)),
            "populasi": float(sub["population"].sum()),
            "pct_populasi_valid": 100 * float(sub["population"].sum()) / tot_pop if tot_pop else np.nan,
            "penduduk_rentan": float(sub["vulnerable"].sum()),
            "pct_rentan_valid": 100 * float(sub["vulnerable"].sum()) / tot_vul if tot_vul else np.nan,
            "lst_rata2": float(sub["lst_c"].mean()),
            "ndvi_rata2": float(sub["ndvi"].mean()),
            "jarak_taman_median_m": float(sub["park_distance_m"].median()),
            "pct_grid_taman_lebih_500m": 100 * float((sub["park_distance_m"] > 500).mean()) if len(sub) else np.nan,
        }

    rows = [row(f"{k.upper()} top", j.loc[j[f"{k}_top"].astype(bool)]) for k in keys]
    rows.append(row("Semua grid valid", j))
    return pd.DataFrame(rows)


def kota_summary(pri: pd.DataFrame, feat: pd.DataFrame, keys=None) -> pd.DataFrame:
    """Sebaran grid prioritas tinggi per kota administratif, per model (format panjang)."""
    keys = keys or model_keys(pri)
    j = pri.merge(feat[[C.KEY, "kota", "population"]], on=C.KEY, how="left", validate="one_to_one")
    j = j.loc[j["valid"].astype(bool)]
    rows = []
    for k in keys:
        top = j.loc[j[f"{k}_top"].astype(bool)]
        n_top_all = len(top)
        for kota, g in j.groupby("kota", dropna=False):
            t = g.loc[g[f"{k}_top"].astype(bool)]
            rows.append({
                "model": k.upper(), "kota": kota, "n_grid_valid": len(g), "n_top": len(t),
                "pct_top_dari_total_top": 100 * len(t) / n_top_all if n_top_all else np.nan,
                "pct_grid_kota_yang_top": 100 * len(t) / len(g) if len(g) else np.nan,
                "populasi_di_top": float(t["population"].sum()),
            })
    return pd.DataFrame(rows)


def rank_shift(pri: pd.DataFrame, a: str = "m1", b: str = "m4") -> pd.DataFrame:
    """Perubahan peringkat grid dari model a ke model b.

    shift = rank_a - rank_b; POSITIF berarti grid naik prioritas di model b (angka peringkat mengecil).
    """
    v = _valid(pri)[[C.KEY, f"{a}_rank", f"{b}_rank", f"{a}_top", f"{b}_top"]].copy()
    v = v.rename(columns={f"{a}_rank": "rank_a", f"{b}_rank": "rank_b", f"{a}_top": "top_a", f"{b}_top": "top_b"})
    v["shift"] = (v["rank_a"].astype(int) - v["rank_b"].astype(int))
    ta, tb = v["top_a"].astype(bool), v["top_b"].astype(bool)
    v["transisi"] = np.select(
        [ta & tb, tb & ~ta, ta & ~tb],
        ["tetap top", f"masuk top di {b.upper()}", f"keluar top di {b.upper()}"],
        default="bukan top",
    )
    return v.sort_values(["shift", C.KEY], ascending=[False, True], kind="stable").reset_index(drop=True)


def heat_vs_aware(pri: pd.DataFrame, feat: pd.DataFrame, a: str = "m1", b: str = "m4") -> pd.DataFrame:
    """Profil grid yang hanya diprioritaskan model panas (a), hanya model sadar-kerentanan (b), atau keduanya."""
    sh = rank_shift(pri, a, b)
    cols = [C.KEY, "kota", "lst_c", "ndvi", "population", "pop_vulnerable", "vuln_share", "park_distance_m",
            "f_snap_far", "f_low_coverage"]
    j = sh.merge(feat[[c for c in cols if c in feat.columns]], on=C.KEY, how="left", validate="one_to_one")
    j = j.loc[j["transisi"] != "bukan top"]
    agg = j.groupby("transisi").agg(
        n_grid=(C.KEY, "size"), lst_rata2=("lst_c", "mean"), ndvi_rata2=("ndvi", "mean"),
        populasi_total=("population", "sum"), rentan_total=("pop_vulnerable", "sum"),
        porsi_rentan_median=("vuln_share", "median"), jarak_taman_median_m=("park_distance_m", "median"),
        n_snap_far=("f_snap_far", "sum"), n_low_coverage=("f_low_coverage", "sum"),
    )
    return agg.reset_index()


def retop(pri: pd.DataFrame, frac: float = C.TOP_FRAC) -> pd.DataFrame:
    """Hitung ulang kolom *_top dari peringkat untuk bagian teratas `frac` (dipakai slider dashboard)."""
    from .models import n_top

    out = pri.copy()
    nv = int(out["valid"].astype(bool).sum())
    for k in model_keys(out):
        out[f"{k}_top"] = (out[f"{k}_rank"] <= n_top(nv, frac)).fillna(False).astype(bool)
    return out


def eligibility_effect(feat: pd.DataFrame, frac: float = C.TOP_FRAC) -> pd.DataFrame:
    """Berapa grid prioritas M1 (dihitung pada semua grid ber-LST) hilang karena himpunan pembanding bersama.

    Mendokumentasikan dampak mengeluarkan grid tanpa rute taman dsb. terhadap model panas murni.
    """
    from .models import n_top, score_rank

    e1 = feat.loc[feat["elig_m1"].astype(bool)]
    if e1.empty:
        return pd.DataFrame()
    _, r = score_rank(e1, C.MODELS["M1"])
    top = e1.loc[r <= n_top(len(e1), frac)]
    out_common = ~top["valid"].astype(bool)
    return pd.DataFrame([{
        "n_elig_m1": len(e1), "n_common_valid": int(feat["valid"].sum()), "n_top_m1_full": len(top),
        "n_top_m1_full_outside_common": int(out_common.sum()),
        "pct_top_m1_full_outside_common": 100 * float(out_common.mean()),
        "of_which_park_route_missing": int((top["f_park_route_missing"] & out_common).sum()),
    }])
