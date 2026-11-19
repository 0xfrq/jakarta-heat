"""Uji sensitivitas prioritas (EKSPLORATIF, bukan konfirmatori).

Pertanyaan: seberapa stabil himpunan grid prioritas tinggi bila satu keputusan metodologis diubah
(bobot, normalisasi, ambang taman, perlakuan jarak kosong, jumlah vs kepadatan/komposisi penduduk,
eksklusi QA, indikator tutupan lahan)? Satu keputusan diubah per skenario (one-at-a-time), sehingga
jumlah skenario tetap kecil dan masing-masing menjawab pertanyaan yang jelas.

Skenario yang mengubah himpunan grid layak (mis. jarak kosong diimputasi, eksklusi QA) dibandingkan
apa adanya: Jaccard memakai himpunan top masing-masing; Spearman memakai irisan grid kedua himpunan.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from . import config as C
from .models import n_top, normalize_weights, score_rank


@dataclass
class Scenario:
    name: str
    group: str
    weights: dict
    kw: dict = field(default_factory=dict)  # argumen score_rank/components
    policy: str | None = None  # kebijakan jarak taman kosong (None = sama dengan baseline)
    exclude: str | None = None  # kolom bendera; grid bertanda True dikeluarkan
    note: str = ""
    require: tuple = ()  # kolom mentah yang wajib terisi di skenario ini (grid tanpa nilai dikeluarkan, dilaporkan)


def _swap(w: dict, old: str, new: str) -> dict:
    out = dict(w)
    out[new] = out.pop(old)
    return out


def build_scenarios(weights: dict, feat: pd.DataFrame) -> list[Scenario]:
    w0 = normalize_weights(weights)
    sc: list[Scenario] = []
    if len(w0) > 1:
        for comp in w0:
            for f in C.WEIGHT_FACTORS:
                w = dict(w0)
                w[comp] *= f
                sc.append(Scenario(f"bobot {comp} x{f:g}", "bobot", w))
        sc.append(Scenario("bobot sama rata", "bobot", {k: 1.0 for k in w0}))
    sc += [
        Scenario("normalisasi min-max murni", "normalisasi", w0, {"clip": None}),
        Scenario("normalisasi persentil 1-99", "normalisasi", w0, {"clip": (0.01, 0.99)}),
        Scenario("normalisasi peringkat persentil", "normalisasi", w0, {"method": "rank"}),
    ]
    if "park_deficit" in w0:
        for thr in C.PARK_THRESHOLDS_M:
            sc.append(Scenario(f"akses taman biner >{thr:g} m", "ambang taman", w0,
                               {"park_mode": "binary", "park_thr": thr}))
        for cap in C.PARK_CAPS_ALT_M:
            sc.append(Scenario(f"defisit taman jenuh {cap:g} m", "ambang taman", w0, {"park_cap": cap}))
        sc.append(Scenario("jarak kosong = defisit maksimum", "jarak taman kosong", w0, policy="worst",
                           note="Asumsi terburuk; BUKAN bukti tidak ada taman"))
        sc.append(Scenario("jarak kosong = median teramati", "jarak taman kosong", w0, policy="median",
                           note="Asumsi netral"))
    if "pop" in w0:
        sc.append(Scenario("kepadatan penduduk (bukan jumlah)", "penduduk", _swap(w0, "pop", "pop_density"),
                           note="Sel pantai kecil dapat berkepadatan tinggi dengan jumlah kecil"))
    if "vuln" in w0:
        sc.append(Scenario("porsi rentan (bukan jumlah)", "penduduk", _swap(w0, "vuln", "vuln_share"),
                           note="Komposisi usia; tidak memuat besaran penduduk"))
        w = dict(w0)
        w["pop"] = w.pop("vuln")
        sc.append(Scenario("total populasi (bukan rentan)", "penduduk", w))
    if "ndvi_low" in w0 and "trees_prob" in feat.columns and feat["trees_prob"].notna().any():
        sc.append(Scenario("Dynamic World pohon rendah (ganti NDVI)", "tutupan lahan", _swap(w0, "ndvi_low", "trees_low"),
                           require=("trees_prob",), note="Probabilitas kelas, bukan fraksi tutupan"))
    sc.append(Scenario(f"keluarkan snap > {C.SNAP_QA_M:g} m", "eksklusi QA", w0, exclude="f_snap_far"))
    sc.append(Scenario(f"keluarkan coverage < {C.LOW_COVERAGE:.0%}", "eksklusi QA", w0, exclude="f_low_coverage"))
    if "f_rs_qa" in feat.columns and feat["f_rs_qa"].astype(bool).any():
        sc.append(Scenario("keluarkan rs_qa_ok = False (Agent 1)", "eksklusi QA", w0, exclude="f_rs_qa"))
    return sc


def _eligible(feat: pd.DataFrame, s: Scenario, cache: dict) -> pd.DataFrame:
    from .data import clean_values

    f = feat
    if s.policy:
        if s.policy not in cache:
            cache[s.policy] = clean_values(feat, s.policy)
        f = cache[s.policy]
    v = f.loc[f["valid"].astype(bool)]
    if s.exclude:
        v = v.loc[~v[s.exclude].astype(bool)]
    for col in s.require:
        v = v.loc[v[col].notna()]
    return v


def _tops(v: pd.DataFrame, rank: pd.Series, fracs) -> dict:
    return {fr: set(v.loc[rank <= n_top(len(v), fr), C.KEY]) for fr in fracs}


def _j(a, b):
    u = len(a | b)
    return len(a & b) / u if u else np.nan


def run_sensitivity(feat: pd.DataFrame, model: str = "M4", top_frac: float = C.TOP_FRAC, weights=None,
                    fracs=C.TOP_FRACS):
    """Bandingkan himpunan top baseline dengan tiap skenario.

    feat: keluaran data.clean_values dengan kebijakan baseline (kolom `valid` dipakai).
    Kembalikan (ringkasan per skenario, stabilitas per grid, info dict).
    """
    w0 = normalize_weights(weights or C.MODELS[model])
    fracs = tuple(sorted(set(fracs) | {top_frac}))
    base = feat.loc[feat["valid"].astype(bool)].copy()
    if base.empty:
        raise ValueError("Tidak ada grid valid.")
    b_score, b_rank = score_rank(base, w0)
    b_tops = _tops(base, b_rank, fracs)
    b_score_by_id = pd.Series(b_score.to_numpy(), index=base[C.KEY].to_numpy())
    base_ids = set(base[C.KEY])

    rows, in_top, elig = [], {}, {}
    cache: dict = {}
    scen = build_scenarios(w0, feat)
    for s in scen:
        v = _eligible(feat, s, cache)
        sc, rk = score_rank(v, s.weights, **s.kw)
        tops = _tops(v, rk, fracs)
        ids = set(v[C.KEY])
        common = sorted(ids & base_ids)
        s_by_id = pd.Series(sc.to_numpy(), index=v[C.KEY].to_numpy())
        rho = float(pd.Series(s_by_id[common].to_numpy()).corr(pd.Series(b_score_by_id[common].to_numpy()),
                                                                method="spearman")) if len(common) > 2 else np.nan
        main_top = tops[top_frac]
        row = {
            "skenario": s.name, "kelompok": s.group, "jenis": "eksploratif",
            "n_layak": len(v), "n_tambah_vs_baseline": len(ids - base_ids), "n_hilang_vs_baseline": len(base_ids - ids),
            "spearman_vs_baseline": rho,
            "grid_top_berubah": int(len(b_tops[top_frac] - main_top)),
            "top_dari_grid_tambahan": int(len(main_top - base_ids)),
            "catatan": s.note,
        }
        for fr in fracs:
            row[f"jaccard_top{int(round(fr * 100))}"] = _j(tops[fr], b_tops[fr])
        row["jaccard_vs_baseline"] = row[f"jaccard_top{int(round(top_frac * 100))}"]
        rows.append(row)
        in_top[s.name] = base[C.KEY].isin(main_top).to_numpy()
        elig[s.name] = base[C.KEY].isin(ids).to_numpy()
    summ = pd.DataFrame(rows)

    T = np.vstack(list(in_top.values()))
    E = np.vstack(list(elig.values()))
    n_el = E.sum(axis=0)
    share = np.where(n_el > 0, (T & E).sum(axis=0) / np.maximum(n_el, 1), np.nan)
    stab = pd.DataFrame({
        C.KEY: base[C.KEY].to_numpy(),
        "baseline_rank": b_rank.to_numpy(),
        "baseline_top": base[C.KEY].isin(b_tops[top_frac]).to_numpy(),
        "n_skenario_layak": n_el,
        "stable_share": share,
        "in_all_scenarios": ((T | ~E).all(axis=0)) & (n_el > 0),
    })
    bt = stab.loc[stab["baseline_top"]]
    info = {
        "model": model,
        "weights": w0,
        "n_valid": int(len(base)),
        "n_top": int(n_top(len(base), top_frac)),
        "top_frac": top_frac,
        "n_scenarios": int(len(scen)),
        "n_baseline_top_stable": int((bt["stable_share"] >= C.STABLE_SHARE).sum()),
        "share_baseline_top_stable": float((bt["stable_share"] >= C.STABLE_SHARE).mean()) if len(bt) else float("nan"),
        "n_baseline_top_in_all": int(bt["in_all_scenarios"].sum()),
        "min_jaccard": float(summ["jaccard_vs_baseline"].min()),
        "median_jaccard": float(summ["jaccard_vs_baseline"].median()),
        "stable_threshold": C.STABLE_SHARE,
        "catatan": "Analisis eksploratif one-at-a-time; stable_share dihitung atas skenario tempat grid layak.",
    }
    return summ, stab, info
