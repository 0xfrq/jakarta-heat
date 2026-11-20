"""Orkestrasi pipeline analisis Agent 3 (dipakai CLI, skrip 03-07, dan dashboard).

Aturan keluaran:
- Keluaran RESMI model (data/processed/modeling, outputs/tables, outputs/figures, outputs/gis) hanya ditulis
  bila data remote sensing ASLI tersedia (status RS_INCOMPLETE/COMPLETE) dan bukan dummy.
- Data dummy (--demo) hanya ditulis ke folder demo dengan watermark.
- Diagnostik data Person 2 (deskriptif/QA, bukan skor model) ditulis ke outputs/qa/agent3/.
- Setiap run menulis manifest provenance (hash masukan, konfigurasi, versi, commit git).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from . import compare as K
from . import config as C
from . import data as D
from . import models as M
from .util import DataError, PendingInputs, git_source_state, read_json, sha256, utc_stamp, versions, write_csv, write_json


def log(msg: str) -> None:
    print(msg, flush=True)


# ---------------------------------------------------------------- 1. gabung
def step_merge(paths: C.Paths, unreachable: str = "exclude", force: bool = False):
    feat, meta, status = D.load_features(paths, unreachable)
    if not status.can_model:
        raise PendingInputs(
            f"Status masukan {status.state}: {status.text} Keluaran resmi model TIDAK ditulis. "
            "Jalankan `python scripts/run_agent3_pipeline.py --p2-only` untuk diagnostik data Person 2."
        )
    if meta["source"] == "dummy" and not paths.demo:
        raise DataError("Masukan bertanda dummy di mode data asli; keluaran resmi ditolak.")
    if meta["valid_share"] < C.MIN_VALID_SHARE and not force:
        raise DataError(f"Hanya {meta['valid_share']:.1%} grid valid (< {C.MIN_VALID_SHARE:.0%}). "
                        "Laporkan ke Agent 1/Person 2, atau jalankan dengan --force dan dokumentasikan.")
    meta["input_status_detail"] = status.to_dict()
    write_csv(feat, paths.merged)
    write_json(paths.merged_meta, meta)
    write_csv(D.quality_table(feat), paths.tables / "data_quality.csv")
    write_csv(feat[[C.KEY, "elig_m1", "elig_m2", "elig_m3", "elig_m4", "valid", "eligibility_reasons"]],
              paths.modeling / "eligibility_by_model.csv")
    log(f"[merge] sumber {meta['source'].upper()}  status {status.state}  grid {meta['n_grid']:,}  "
        f"valid {meta['n_valid']:,} ({meta['valid_share']:.1%})  kebijakan jarak kosong: {meta['unreachable_policy']}")
    return feat, meta


def load_merged(paths: C.Paths):
    from .io import load_merged as _lm

    return _lm(paths)


# ---------------------------------------------------------------- 2. model
def step_priority(paths: C.Paths, feat=None, meta=None, top_frac: float = C.TOP_FRAC):
    if feat is None:
        feat, meta = load_merged(paths)
    pri = M.build_priority_table(feat, top_frac=top_frac)
    write_csv(pri, paths.priority)
    nv = int(pri["valid"].sum())
    pmeta = {
        **C.config_snapshot(),
        "source": meta["source"], "built_at": utc_stamp(), "n_grid": int(len(pri)), "n_valid": nv,
        "top_frac": top_frac, "n_top": M.n_top(nv, top_frac),
        "unreachable_policy": meta.get("unreachable_policy"),
        "rank_rule": "rank 1 = prioritas tertinggi; seri dipecah oleh skor tanpa pemotongan lalu grid_id",
    }
    write_json(paths.priority_meta, pmeta)
    log(f"[model] M1-M4 pada {nv:,} grid valid bersama; top {top_frac:.0%} = {pmeta['n_top']:,} grid")
    return pri, pmeta


# ---------------------------------------------------------------- 3. perbandingan
def step_compare(paths: C.Paths, feat, pri):
    keys = K.model_keys(pri)
    t = paths.tables
    write_csv(K.pairwise_long(pri, keys), t / "model_comparison.csv")
    write_csv(K.spearman_matrix(pri, keys).reset_index(names="model"), t / "spearman_matrix.csv")
    write_csv(K.kendall_matrix(pri, keys).reset_index(names="model"), t / "kendall_matrix.csv")
    write_csv(K.jaccard_matrix(pri, keys).reset_index(names="model"), t / "jaccard_matrix.csv")
    write_csv(K.overlap_table(pri, keys), t / "top_overlap.csv")
    write_csv(K.rank_movement(pri, keys), t / "rank_movement.csv")
    write_csv(K.score_summary(pri, keys), t / "score_summary.csv")
    write_csv(K.top_coverage(pri, feat, keys), t / "model_top10_coverage.csv")
    write_csv(K.kota_summary(pri, feat, keys), t / "kota_summary.csv")
    for a, b in (("m1", "m4"), ("m1", "m2"), ("m2", "m3"), ("m3", "m4")):
        write_csv(K.transition_matrix(pri, a, b).reset_index(), t / f"transition_{a}_{b}.csv")
    write_csv(K.rank_shift(pri, "m1", "m4"), paths.modeling / "rank_shift_m1_m4.csv")
    write_csv(K.heat_vs_aware(pri, feat, "m1", "m4"), t / "heat_vs_aware_m1_m4.csv")
    write_csv(K.eligibility_effect(feat), t / "eligibility_effect_m1.csv")
    log("[compare] Spearman/Kendall/Jaccard/overlap/transisi/kota ditulis ke " + str(t))


# ---------------------------------------------------------------- 4. spasial
def _geo(paths, df):
    g = D.read_grid_gdf(paths.grid)
    out = g.merge(df, on=C.KEY, how="inner", validate="one_to_one")
    return out.reset_index(drop=True)


def step_spatial(paths: C.Paths, feat, pri, perms: int = C.PERMUTATIONS, kinds=C.SPATIAL_WEIGHTS,
                 lisa_models=("M1", "M2", "M3", "M4")):
    from . import spatial as SP

    keys = K.model_keys(pri)
    v = pri.loc[pri["valid"].astype(bool)].merge(feat[[C.KEY, "lst_c", "ndvi"]], on=C.KEY, how="left",
                                                 validate="one_to_one")
    gdf = _geo(paths, v)
    if len(gdf) != len(v):
        raise DataError("Geometri master grid tidak cocok dengan grid valid.")
    cols = [f"{k}_score" for k in keys] + ["lst_c", "ndvi"]
    gm = SP.moran_table(gdf, cols, kinds, perms)
    write_csv(gm, paths.tables / "moran_global.csv")
    lisas, islands = [], {}
    for m in lisa_models:
        out, dropped = SP.lisa_for(gdf, f"{m.lower()}_score", "queen", perms)
        out["model"] = m
        lisas.append(out)
        islands[m] = dropped
        write_csv(out, paths.modeling / f"lisa_{m.lower()}.csv")
    lisa = pd.concat(lisas, ignore_index=True)
    cnt = lisa.groupby(["model", "klaster_fdr"]).size().unstack(fill_value=0).reset_index()
    write_csv(cnt, paths.tables / "lisa_cluster_counts.csv")
    write_json(paths.tables / "spatial_validation_info.json", {
        "weights_baseline": "Queen contiguity (poligon), row-standardized",
        "weights_sensitivity": [k for k in kinds if k != "queen"], "permutations": perms, "seed": C.SEED,
        "alpha": C.LISA_ALPHA, "islands_dropped": islands,
        "local_alternative": "directed", "global_alternative": "greater",
        "testing_family": "each preselected map separately; all non-island eligible grids",
        "catatan": "LISA diuji per grid (uji berganda); klaim memakai kolom klaster_fdr (Benjamini-Hochberg). "
                   "Klaster adalah deskriptif, bukan penjelasan kausal.",
    })
    log(f"[spatial] Moran global {len(gm)} baris; LISA {', '.join(lisa_models)} (Queen, {perms} permutasi)")
    return gm, lisa


# ---------------------------------------------------------------- 5. sensitivitas
def step_sensitivity(paths: C.Paths, feat, models=("M2", "M3", "M4")):
    from . import sensitivity as SE

    infos = {}
    for m in models:
        summ, stab, info = SE.run_sensitivity(feat, m)
        k = m.lower()
        write_csv(summ, paths.tables / f"sensitivity_{k}_summary.csv")
        write_csv(stab, paths.modeling / f"sensitivity_{k}_stability.csv")
        write_json(paths.tables / f"sensitivity_{k}_info.json", info)
        infos[m] = info
        log(f"[sensitivity] {m}: {info['n_scenarios']} skenario, Jaccard median {info['median_jaccard']:.2f}, "
            f"min {info['min_jaccard']:.2f}; {info['share_baseline_top_stable']:.0%} grid top stabil")
    return infos


# ---------------------------------------------------------------- 6. ekspor
def step_export(paths: C.Paths, feat, pri, pmeta, dpi: int = 300, formats=("png", "svg")):
    import matplotlib.pyplot as plt

    from . import figures as F

    dummy = pmeta.get("source") == "dummy"
    paths.figures.mkdir(parents=True, exist_ok=True)
    written = []

    def save(fig, name):
        if dummy:
            F.watermark(fig)
        for fmt in formats:
            p = paths.figures / f"{name}.{fmt}"
            fig.savefig(p, dpi=dpi, bbox_inches="tight")
            written.append(str(p))
        plt.close(fig)

    keys = K.model_keys(pri)
    nt = int(pri["m1_top"].sum())
    save(F.matrix_heatmap(K.spearman_matrix(pri), "Spearman antar skor model", -1.0, 1.0, "RdBu_r"), "fig_spearman")
    save(F.matrix_heatmap(K.jaccard_matrix(pri), "Jaccard 10% grid teratas"), "fig_jaccard")
    save(F.coverage_bars(K.top_coverage(pri, feat)), "fig_coverage_top10")
    save(F.rank_scatter(K.rank_shift(pri, "m1", "m4"), "m1", "m4", nt), "fig_rank_m1_vs_m4")
    save(F.score_hist(pri, keys), "fig_score_distribution")
    save(F.kota_bars(K.kota_summary(pri, feat)), "fig_kota_top10")
    tm = K.transition_matrix(pri, "m1", "m4", normalize=True)
    tm.index = [s.split(" (")[0] for s in tm.index]
    tm.columns = [s.split(" (")[0] for s in tm.columns]
    save(F.matrix_heatmap(tm, "Transisi kelas M1 (baris) ke M4 (kolom)"), "fig_transition_m1_m4")
    sm = paths.tables / "sensitivity_m4_summary.csv"
    if sm.exists():
        save(F.sensitivity_bars(pd.read_csv(sm), C.STABLE_SHARE), "fig_sensitivity_m4")

    geo = D.read_grid_gdf(paths.grid).to_crs(C.CRS_PROJECTED)
    ids = pri[C.KEY]
    fig, axs = plt.subplots(2, 2, figsize=(11, 10))
    for ax, k in zip(axs.ravel(), keys):
        F.map_grid(geo, pri[f"{k}_score"], ids, C.MODEL_LABELS[k.upper()], "Oranges", 0.0, 1.0, ax, label="skor 0-1")
    fig.suptitle("Skor prioritas panas (indeks relatif 0-1; abu-abu = grid tidak dipakai)", fontsize=12)
    save(fig, "fig_map_scores_m1_m4")

    fig, axs = plt.subplots(2, 2, figsize=(11, 10))
    for ax, k in zip(axs.ravel(), keys):
        labels = pri[f"{k}_top"].map({True: "top", False: "lain"}).where(pri["valid"].astype(bool))
        F.map_categories(geo, ids, labels, {"top": "#b2182b", "lain": "#d0d0d0"},
                         f"{C.MODEL_LABELS[k.upper()]}: {nt:,} grid teratas", ax)
    save(fig, "fig_map_top10_m1_m4")

    sh = K.rank_shift(pri, "m1", "m4")
    lim = max(float(sh["shift"].abs().quantile(0.98)), 1.0)
    fig, ax = plt.subplots(figsize=(7, 6.5))
    F.map_grid(geo, sh["shift"].astype(float), sh[C.KEY], "Perubahan peringkat M1 ke M4 (merah = naik prioritas)",
               "RdBu_r", -lim, lim, ax, label="peringkat M1 - peringkat M4")
    save(fig, "fig_map_rank_shift_m1_m4")

    lp = paths.modeling / "lisa_m4.csv"
    if lp.exists():
        lisa = pd.read_csv(lp, dtype={C.KEY: str})
        fig, ax = plt.subplots(figsize=(7, 6.5))
        F.map_categories(geo, lisa[C.KEY], lisa["klaster_fdr"], F.LISA_COLORS,
                         "LISA skor M4 (Queen; signifikan setelah FDR-BH)", ax)
        save(fig, "fig_map_lisa_m4")
    sp = paths.modeling / "sensitivity_m4_stability.csv"
    if sp.exists():
        stab = pd.read_csv(sp, dtype={C.KEY: str})
        fig, ax = plt.subplots(figsize=(7, 6.5))
        F.map_grid(geo, stab["stable_share"].where(stab["baseline_top"]), stab[C.KEY],
                   "Stabilitas grid top M4 (porsi skenario sensitivitas)", "Blues", 0.0, 1.0, ax, label="porsi skenario")
        save(fig, "fig_map_stability_m4")

    # ---- tabel dan GeoPackage
    v = pri.loc[pri["valid"].astype(bool)].merge(
        feat[[C.KEY, "kota", "lst_c", "ndvi", "population", "pop_child", "pop_elderly", "park_distance_m",
              "f_snap_far", "f_low_coverage"]], on=C.KEY, validate="one_to_one")
    for k in keys:
        top = v.loc[v[f"{k}_top"].astype(bool)].sort_values(f"{k}_rank")
        write_csv(top, paths.tables / f"top10_priority_{k}.csv")
    gis = geo.merge(feat[[C.KEY, "kota", "lst_c", "ndvi", "population", "pop_vulnerable", "park_distance_m",
                          "f_park_route_missing", "f_snap_far", "f_low_coverage"]], on=C.KEY, validate="one_to_one")
    gis = gis.merge(pri, on=C.KEY, validate="one_to_one")
    for c in gis.columns:
        if str(gis[c].dtype) in ("Int64", "boolean"):
            gis[c] = gis[c].astype(float)
    paths.gis.mkdir(parents=True, exist_ok=True)
    gp = paths.gis / "priority_models.gpkg"
    gis.to_file(gp, layer="priority_models", driver="GPKG")
    written.append(str(gp))
    log(f"[export] {len(written)} berkas figur/GIS di {paths.figures} dan {paths.gis}")
    return written


# ---------------------------------------------------------------- diagnostik Person 2
def step_p2_diagnostics(paths: C.Paths, perms: int = C.PERMUTATIONS, spatial: bool = True):
    """Analisis deskriptif/QA data Person 2 yang SUDAH dapat dilakukan tanpa remote sensing."""
    feat, meta, status = D.load_features(paths, "exclude")
    q = paths.qa
    write_csv(D.quality_table(feat), q / "person2_quality.csv")
    f = feat.copy()
    f["kota"] = f["kota"].fillna("(tanpa kota)")
    g = f.groupby("kota")
    kota = pd.DataFrame({
        "n_grid": g.size(),
        "populasi": g["population"].sum(),
        "anak_0_14": g["pop_child"].sum(),
        "lansia_65": g["pop_elderly"].sum(),
        "pct_rentan": 100 * (g["pop_child"].sum() + g["pop_elderly"].sum()) / g["population"].sum(),
        "n_rute_tidak_dihitung": g["f_park_route_missing"].sum(),
        "populasi_di_grid_tanpa_rute": f.loc[f["f_park_route_missing"]].groupby("kota")["population"].sum(),
        "jarak_taman_median_m": g["park_distance_m"].median(),
        "pct_grid_akses_500m": 100 * g["park_access_500m"].mean(),
        "pct_grid_akses_1000m": 100 * g["park_access_1000m"].mean(),
        "n_snap_gt_250m": g["f_snap_far"].sum(),
        "n_coverage_lt_10pct": g["f_low_coverage"].sum(),
    }).fillna({"populasi_di_grid_tanpa_rute": 0}).reset_index()
    write_csv(kota, q / "person2_kota_summary.csv")
    corr = M.component_correlations(feat)
    write_csv(corr.reset_index(names="komponen"), q / "person2_component_spearman.csv")
    flagged = feat.loc[feat["f_park_route_missing"] | feat["f_snap_far"] | feat["f_low_coverage"] | feat["f_pop_zero"],
                       [C.KEY, "kota", "population", "pop_vulnerable", "park_distance_m", "grid_snap_m",
                        "coverage_ratio", "area_km2", "f_park_route_missing", "f_snap_far", "f_low_coverage", "f_pop_zero"]]
    write_csv(flagged, q / "person2_flagged_grids.csv")
    out = {"status": status.to_dict(), "n_flagged": int(len(flagged))}
    if spatial:
        from . import spatial as SP

        d = feat[[C.KEY, "population", "pop_vulnerable", "vuln_share", "park_distance_m"]].copy()
        d["log1p_population"] = np.log1p(d["population"])
        d["log1p_pop_vulnerable"] = np.log1p(d["pop_vulnerable"])
        gdf = _geo(paths, d)
        cols = ["log1p_population", "log1p_pop_vulnerable", "vuln_share", "park_distance_m"]
        gm = SP.moran_table(gdf, cols, C.SPATIAL_WEIGHTS, perms)
        write_csv(gm, q / "person2_moran_global.csv")
        lisa, dropped = SP.lisa_for(gdf, "park_distance_m", "queen", perms)
        write_csv(lisa, q / "person2_lisa_park_distance.csv")
        out["moran"] = gm[["variabel", "bobot", "I", "p_sim", "n"]].to_dict("records")
        out["lisa_park_distance_islands"] = dropped
    write_json(q / "person2_diagnostics_info.json", {
        **out, "built_at": utc_stamp(), "source": meta["source"],
        "catatan": "Deskriptif data Person 2 (WorldPop, OSM, jarak jaringan model). Bukan skor prioritas. "
                   "park_distance_m kosong = rute tidak dihitung; dikeluarkan dari statistik jarak.",
    })
    log(f"[p2] diagnostik Person 2 ditulis ke {q} (status masukan {status.state})")
    return out


# ---------------------------------------------------------------- manifest
def _portable_command(argv, root) -> list[str]:
    """Keep the recorded command readable without embedding machine-specific paths."""
    root = Path(root).resolve()
    out = []
    for arg in argv:
        p = Path(arg)
        if p.is_absolute():
            try:
                out.append(p.resolve().relative_to(root).as_posix())
            except ValueError:
                out.append(f"<external>/{p.name}")
        else:
            out.append(arg)
    return out


def write_manifest(paths: C.Paths, steps: list[str], extra: dict | None = None, target=None) -> dict:
    import sys
    from . import provenance as PV

    status = D.assess_inputs(paths)
    inputs = PV.inputs_identity(paths)
    source = git_source_state(paths.root)
    man = {
        "built_at": utc_stamp(), "demo": paths.demo, "input_status": status.state, "input_status_text": status.text,
        "schema_version": 2, "steps": steps, "inputs": inputs, "config": PV.scientific_config(),
        "implementation": PV.implementation_identity(), "outputs": PV.output_identity(paths),
        "build_command": [Path(sys.executable).name, *_portable_command(sys.argv, paths.root)],
        "git_commit": source["revision"], "source_revision": source["commit"], "source_state": source["state"],
        "source_dirty_paths": source["dirty_paths"],
        **versions(), **(extra or {}),
    }
    write_csv(pd.DataFrame([{"path": p, "sha256": h} for p, h in man["outputs"].items()]),
              paths.modeling / "output_sha256_manifest.csv")
    write_json(target or paths.manifest, man)
    return man


def run_all(paths: C.Paths, unreachable: str = "exclude", perms: int = C.PERMUTATIONS, skip_spatial: bool = False,
            skip_figures: bool = False, force: bool = False, dpi: int = 300, formats=("png", "svg")) -> dict:
    """Jalankan seluruh pipeline model. PendingInputs bila remote sensing belum ada."""
    feat, meta = step_merge(paths, unreachable, force)
    pri, pmeta = step_priority(paths, feat, meta)
    step_compare(paths, feat, pri)
    steps = ["merge", "priority", "compare"]
    if not skip_spatial:
        step_spatial(paths, feat, pri, perms)
        steps.append("spatial")
    step_sensitivity(paths, feat)
    steps.append("sensitivity")
    if not skip_figures:
        step_export(paths, feat, pri, pmeta, dpi, formats)
        steps.append("export")
    return write_manifest(paths, steps, {"source": meta["source"], "unreachable_policy": meta["unreachable_policy"],
                                         "n_valid": meta["n_valid"], "runtime": {
                                             "permutations": perms, "seed": C.SEED, "unreachable": unreachable,
                                             "top_frac": C.TOP_FRAC, "spatial_weights": list(C.SPATIAL_WEIGHTS),
                                             "skip_spatial": skip_spatial, "skip_figures": skip_figures,
                                             "force": force, "dpi": dpi, "formats": list(formats),
                                             "local_alternative": "directed", "testing_family": "per map"}})


def official_outputs_status(paths: C.Paths, expected_runtime=None) -> dict:
    """Apakah keluaran resmi ada, dan apakah masih sesuai dengan masukan saat ini (hash)."""
    if not paths.manifest.exists():
        return {"exists": False}
    man = read_json(paths.manifest)
    from .provenance import manifest_status
    stale = manifest_status(paths, man, expected_runtime)
    return {"exists": True, "built_at": man.get("built_at"), "stale_inputs": stale,
            "is_current": not stale, "source": man.get("source"), "runtime": man.get("runtime")}
