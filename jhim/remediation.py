"""Executable audit remediation analyses on real frozen inputs, never the official baseline.

All models/scenarios are provisional. Counterfactual contributions are arithmetic, not causes.
Audit evidence supplies support diagnostics only; it does not repair or replace Agent 2's sources.
"""
from __future__ import annotations

import itertools
import json
import math
import os
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

from . import config as C, data as D, models as M
from .util import DataError, sha256, write_csv, write_json


def _provenance_path(path, root, audit_root=None):
    """Repository-relative path; audit evidence is labelled relative to its read-only root."""
    p = Path(path).resolve()
    try:
        return p.relative_to(Path(root).resolve()).as_posix()
    except ValueError:
        pass
    if audit_root is not None:
        try:
            return "audit/" + p.relative_to(Path(audit_root).resolve()).as_posix()
        except ValueError:
            pass
    return p.name


def _newline_equivalent(source: Path, target: Path) -> bool:
    """True only for text artefacts whose sole byte difference is CRLF vs LF."""
    if source.suffix.lower() not in {".csv", ".json", ".txt", ".md", ".tsv"}:
        return False
    a = source.read_bytes().replace(b"\r\n", b"\n")
    b = target.read_bytes().replace(b"\r\n", b"\n")
    return a == b


def freeze(source, target, root=None, audit_root=None):
    source, target = Path(source), Path(target)
    if not source.exists():
        raise DataError(f"Required frozen input unavailable: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    source_hash, target_hash = sha256(source), sha256(target)
    newline_only = False
    if target.exists() and source_hash != target_hash:
        if not _newline_equivalent(source, target):
            raise DataError(f"Frozen input differs; choose a new versioned path: {target}")
        # Keep the already-frozen bytes and record the reconciliation explicitly.
        # The analytical CSV/JSON content is identical; only CRLF/LF differs.
        newline_only = True
    if not target.exists():
        shutil.copyfile(source, target)
    record = {
        "source": _provenance_path(source, root, audit_root) if root else source.as_posix(),
        "copy": _provenance_path(target, root, audit_root) if root else target.as_posix(),
        "sha256": sha256(target),
    }
    if newline_only:
        record.update({"source_sha256": source_hash, "copy_sha256": target_hash,
                       "reconciliation": "newline_only_crlf_lf; analytical content byte-identical after newline normalisation"})
    return record


def prepare_inputs(root, audit):
    """Freeze local audited values plus read-only auditor masks. No sibling data access."""
    root, audit = Path(root), Path(audit)
    dest = root / "data/processed/remediation_inputs"
    sources = [
        (root / "data/processed/modeling/merged_grid.csv", "audited_merged_grid.csv"),
        (root / "data/processed/modeling/priority_models.csv", "audited_priority_models.csv"),
        (root / "data/processed/spatial_features.csv", "spatial_features.csv"),
        (audit / "evidence/gis/independent_raster_support.csv", "auditor_raster_support.csv"),
        (audit / "evidence/gis/independent_full_network.csv", "auditor_network.csv"),
    ]
    provenance = [freeze(src, dest / name, root=root, audit_root=audit) for src, name in sources]
    baseline = pd.read_csv(dest / "audited_merged_grid.csv")
    rs = baseline[[C.KEY, *[c for c in (*C.RS_COLS, *C.RS_OPTIONAL, *C.RS_TEXT) if c in baseline]]]
    write_csv(rs, dest / "remote_sensing_grid.csv")
    raw = pd.read_csv(dest / "auditor_raster_support.csv")
    support = raw[[C.KEY, "population_support_pixels", "pop_child_support_pixels", "pop_elderly_support_pixels"]].copy()
    support["qa_population_source_no_support"] = raw.population_support_pixels <= 0
    support["qa_age_source_no_support"] = (raw.pop_child_support_pixels <= 0) | (raw.pop_elderly_support_pixels <= 0)
    support["support_version"] = "audit-2026-11-20-fractional-mask-v1-PROVISIONAL"
    support["support_origin"] = "independent_raster_support.csv; pixel-equivalent intersected support, not integer centers"
    write_csv(support, dest / "demographic_support.csv")
    write_json(dest / "input_lineage.json", {"source_files": provenance,
        "derived": {n: sha256(dest / n) for n in ("remote_sensing_grid.csv", "demographic_support.csv")},
        "restriction": "RS values copied from existing audited merged output, not a new Agent1 export; "
                       "support evidence provisional pending canonical DM-01; raw exports unchanged."})
    return dest


def prepare_integrated_inputs(root, audit):
    """Versioned comparisons only; measured inputs come from canonical worktree paths."""
    root, audit = Path(root), Path(audit)
    dest = root / "data/processed/integrated_comparisons"
    old = root / "data/processed/remediation_inputs"
    sources = [(old / n, n) for n in ("audited_merged_grid.csv", "audited_priority_models.csv")]
    sources += [(audit / "evidence/gis/independent_raster_support.csv", "auditor_raster_support.csv"),
                (audit / "evidence/gis/independent_full_network.csv", "auditor_network.csv")]
    entries = [freeze(src, dest / name, root=root, audit_root=audit) for src, name in sources]
    paths = C.Paths(root=root)
    for p in (paths.rs, paths.demographic_support, paths.demographic_corrected,
              root / "data/processed/agent2_route_scenarios.csv"):
        if not p.is_file():
            raise DataError(f"Required canonical input unavailable: {p}")
    write_json(dest / "input_lineage.json", {"source_files": entries, "mode": "integrated",
        "canonical": {p.relative_to(root).as_posix(): sha256(p) for p in
            (paths.rs, paths.demographic_support, paths.demographic_corrected,
             root / "data/processed/agent2_route_scenarios.csv")},
        "restriction": "Auditor tables are comparisons only; canonical Agent1/Agent2 inputs drive analysis."})
    return dest


def rank(comp, raw_comp, weights, ids):
    s = M.weighted_score(comp, weights)
    return s, M.rank_desc(s, ids, M.weighted_score(raw_comp, weights))


def sets(ids, ranks, fraction):
    return set(ids.loc[ranks <= M.n_top(len(ids), fraction)])


def overlap(a, b):
    return {"retained": len(a & b), "entered": len(b - a), "left": len(a - b),
            "jaccard": len(a & b) / len(a | b) if a | b else np.nan}


def compare_rankings(base, other, name, family, mode, fractions=C.TOP_FRACS):
    """ID-indexed rank vectors; exact budget and universe recorded for every row."""
    ids = base.index.intersection(other.index)
    rho = base.loc[ids].corr(other.loc[ids], method="spearman") if len(ids) > 2 else np.nan
    rows = []
    for frac in fractions:
        a = set(base.index[base <= M.n_top(len(base), frac)])
        b = set(other.index[other <= M.n_top(len(other), frac)])
        rows.append({"scenario": name, "family": family, "comparison": mode, "top_fraction": frac,
                     "baseline_n": len(base), "scenario_n": len(other), "intersection_n": len(ids),
                     "baseline_budget": len(a), "scenario_budget": len(b), "rank_spearman": rho,
                     **overlap(a, b)})
    return rows


def by_id(v, ranks):
    return pd.Series(ranks.to_numpy(), index=v[C.KEY].to_numpy())


def support_analysis(baseline, corrected, paths):
    rows, changed = [], []
    for model in C.MODELS:
        a, b = baseline.loc[baseline.valid], corrected.loc[corrected.valid]
        ar = by_id(a, M.score_rank(a, C.MODELS[model])[1])
        br = by_id(b, M.score_rank(b, C.MODELS[model])[1])
        rows += compare_rankings(ar, br, model, "demographic_support", "eligibility_changing_refit_anchors")
        same = a.loc[a[C.KEY].isin(b[C.KEY])]
        sr = by_id(same, M.score_rank(same, C.MODELS[model])[1])
        rows += compare_rankings(sr, br, model, "demographic_support", "fixed_intersection_refit_same_anchors")
        for frac in C.TOP_FRACS:
            at = set(ar.index[ar <= M.n_top(len(ar), frac)])
            bt = set(br.index[br <= M.n_top(len(br), frac)])
            for gid in sorted(at ^ bt):
                changed.append({C.KEY: gid, "model": model, "top_fraction": frac,
                                "change": "entered" if gid in bt else "left",
                                "baseline_rank": ar.get(gid), "corrected_rank": br.get(gid)})
    write_csv(pd.DataFrame(rows), paths.tables / "demographic_support_sensitivity.csv")
    write_csv(pd.DataFrame(changed), paths.tables / "demographic_changed_priorities.csv")


def ablations(feat, paths):
    v = feat.loc[feat.valid].copy()
    c, raw = M.components(v), M.components(v, clip=None)
    anchors = []
    for name, values in (("lst", v.lst_c), ("ndvi", v.ndvi), ("population_log1p", np.log1p(v.population)),
                         ("age_count_log1p", np.log1p(v.pop_vulnerable)), ("vuln_share", v.vuln_share),
                         ("child_share", v.pop_child / v.population), ("elderly_share", v.pop_elderly / v.population)):
        anchors.append({"component": name, "n": len(v), "p05": values.quantile(.05), "p95": values.quantile(.95),
                        "minimum": values.min(), "maximum": values.max()})
    write_csv(pd.DataFrame(anchors), paths.tables / "normalization_anchors.csv")
    for name, col in (("child_share", "pop_child"), ("elderly_share", "pop_elderly")):
        share = v[col] / v.population.where(v.population > 0)
        c[name], raw[name] = M.norm01(share), M.norm01(share, clip=None)
    # All score-only swaps retain identical IDs/anchors. Unsupported denominators never enter.
    if c[["vuln_share", "child_share", "elderly_share"]].isna().any().any():
        raise DataError("Composition ablations require a shared positive-population subset")
    a = c.vuln
    alternatives = {
        "m4": C.MODELS["M4"], "m3": C.MODELS["M3"], "heat_only": C.MODELS["M1"],
        "equal_weight": {"lst": 1, "ndvi_low": 1, "vuln": 1, "park_deficit": 1},
        "total_count_swap": {"lst": .3, "ndvi_low": .2, "pop": .25, "park_deficit": .25},
        "vulnerable_share": {"lst": .3, "ndvi_low": .2, "vuln_share": .25, "park_deficit": .25},
        "child_share": {"lst": .3, "ndvi_low": .2, "child_share": .25, "park_deficit": .25},
        "elderly_share": {"lst": .3, "ndvi_low": .2, "elderly_share": .25, "park_deficit": .25},
        "no_park": {"lst": .3, "ndvi_low": .2, "vuln": .25},
        "no_demography": {"lst": .3, "ndvi_low": .2, "park_deficit": .25},
        "park_only": {"park_deficit": 1},
        "proportional_m3_plus_park": {"lst": .3, "ndvi_low": .225, "pop": .225, "park_deficit": .25},
    }
    scores, ranks = {}, {}
    for name, weights in alternatives.items():
        scores[name], ranks[name] = rank(c, raw, weights, v[C.KEY])
    contributions = v[[C.KEY, "kota", "population", "pop_vulnerable", "vuln_share"]].copy()
    for col in c:
        contributions[f"normalized_{col}"] = c[col]
    for model, weights in C.MODELS.items():
        for col, weight in weights.items():
            contributions[f"{model.lower()}_{col}_contribution"] = weight * c[col]
        contributions[f"{model.lower()}_score"] = M.weighted_score(c, weights)
    contributions["delta_lst"] = -.1 * c.lst
    contributions["delta_ndvi"] = -.1 * c.ndvi_low
    contributions["delta_population"] = -.3 * c["pop"]
    contributions["delta_age_count"] = .25 * a
    contributions["delta_park"] = .25 * c.park_deficit
    contributions["score_delta"] = contributions.m4_score - contributions.m3_score
    contributions["sum_delta_terms"] = contributions.filter(regex="^delta_").sum(axis=1)
    if not np.allclose(contributions.score_delta, contributions.sum_delta_terms, atol=1e-10, rtol=0):
        raise AssertionError("M3/M4 decomposition failed")
    write_csv(contributions, paths.tables / "component_contributions.csv")
    rows = []
    for name, rk in ranks.items():
        rows += compare_rankings(by_id(v, ranks["m4"]), by_id(v, rk), name, "construct_or_ablation",
                                 "fixed_IDs_fixed_anchors")
    write_csv(pd.DataFrame(rows), paths.tables / "ablation_comparison.csv")
    write_csv(pd.DataFrame([r for r in rows if r["scenario"] in ("heat_only", "equal_weight")]),
              paths.tables / "benchmark_comparison.csv")

    # Exact 3-factor Shapley reranking. Factors sum to the full M3->M4 score delta.
    # reweighting: -.1L-.1V-.05P, age swap: .25(A-P), park: .25D.
    factors = {"reweighting": (-.1 * c.lst - .1 * c.ndvi_low - .05 * c["pop"],
                                -.1 * raw.lst - .1 * raw.ndvi_low - .05 * raw["pop"]),
               "age_swap": (.25 * (c.vuln - c["pop"]), .25 * (raw.vuln - raw["pop"])),
               "park_addition": (.25 * c.park_deficit, .25 * raw.park_deficit)}
    base_s = M.weighted_score(c, C.MODELS["M3"])
    base_raw = M.weighted_score(raw, C.MODELS["M3"])
    keys = list(factors)
    coalition_ranks = {}
    for size in range(4):
        for comb in itertools.combinations(keys, size):
            coalition_ranks[frozenset(comb)] = M.rank_desc(
                base_s + sum((factors[k][0] for k in comb), start=0), v[C.KEY],
                base_raw + sum((factors[k][1] for k in comb), start=0))
    attribution = v[[C.KEY, "kota"]].copy()
    attribution["m3_rank"] = coalition_ranks[frozenset()]
    attribution["m4_rank"] = coalition_ranks[frozenset(keys)]
    for key in keys:
        shap = pd.Series(0., index=v.index)
        marginal = []
        others = [k for k in keys if k != key]
        for size in range(3):
            for comb in itertools.combinations(others, size):
                before, after = frozenset(comb), frozenset((*comb, key))
                diff = coalition_ranks[before] - coalition_ranks[after]
                shap += math.factorial(size) * math.factorial(2 - size) / 6 * diff
                marginal.append(diff)
        attribution[f"shapley_rank_gain_{key}"] = shap
        attribution[f"order_min_{key}"] = pd.concat(marginal, axis=1).min(axis=1)
        attribution[f"order_max_{key}"] = pd.concat(marginal, axis=1).max(axis=1)
    attribution["rank_gain"] = attribution.m3_rank - attribution.m4_rank
    if not np.allclose(attribution.filter(regex="^shapley_rank_gain_").sum(axis=1), attribution.rank_gain, atol=1e-10):
        raise AssertionError("Shapley rank attribution failed")
    write_csv(attribution, paths.tables / "rank_change_attribution.csv")
    coalition_rows = []
    for coalition, rk in coalition_ranks.items():
        coalition_rows += compare_rankings(by_id(v, ranks["m3"]), by_id(v, rk),
                                           "+".join(sorted(coalition)) or "m3", "incremental_effects",
                                           "fixed_IDs_fixed_anchors")
    write_csv(pd.DataFrame(coalition_rows), paths.tables / "matched_weight_comparison.csv")
    membership = v[[C.KEY, "kota", "x", "y"]].copy() if "x" in v else v[[C.KEY, "kota"]].copy()
    for name, rk in ranks.items():
        membership[f"{name}_rank"] = rk
        membership[f"{name}_top"] = rk <= M.n_top(len(v))
    membership["matched_shift"] = np.select(
        [membership.proportional_m3_plus_park_top & ~membership.m4_top,
         ~membership.proportional_m3_plus_park_top & membership.m4_top,
         membership.proportional_m3_plus_park_top & membership.m4_top],
        ["left", "entered", "stable"], default="other eligible")
    membership["park_increment_shift"] = np.select(
        [membership.m3_top & ~membership.proportional_m3_plus_park_top,
         ~membership.m3_top & membership.proportional_m3_plus_park_top,
         membership.m3_top & membership.proportional_m3_plus_park_top],
        ["left", "entered", "stable"], default="other eligible")
    write_csv(membership, paths.tables / "priority_membership.csv")
    # Number x relative surface burden is an explicitly new objective, not a health dose.
    burden = v[[C.KEY, "kota", "population", "pop_vulnerable", "vuln_share", "lst_c"]].copy()
    burden["relative_thermal_burden"] = c.lst
    burden["population_times_relative_burden"] = burden.population * c.lst
    burden["age_count_times_relative_burden"] = burden.pop_vulnerable * c.lst
    write_csv(burden, paths.tables / "count_composition_burden.csv")
    return c, raw, ranks, membership


def anchored(raw_values, anchor_values, clip=C.NORM_CLIP, method="minmax"):
    if method == "rank":
        ref = np.sort(anchor_values.dropna().to_numpy())
        if len(ref) < 2 or len(np.unique(ref)) == 1:
            return pd.Series(.5, index=raw_values.index).where(raw_values.notna())
        ranks = (np.searchsorted(ref, raw_values, side="left") + np.searchsorted(ref, raw_values, side="right") + 1) / 2
        return pd.Series((ranks - 1) / (len(ref) - 1), index=raw_values.index).clip(0, 1).where(raw_values.notna())
    lo, hi = (anchor_values.quantile(clip[0]), anchor_values.quantile(clip[1])) if clip else (anchor_values.min(), anchor_values.max())
    return ((raw_values - lo) / (hi - lo)).clip(0, 1) if hi > lo else raw_values.notna().map({True: .5, False: np.nan})


def fixed_components(feat, anchor, clip=C.NORM_CLIP, method="minmax", park_cap=C.PARK_CAP_M,
                     park_mode="continuous", park_thr=None):
    c = pd.DataFrame(index=feat.index)
    for col, name, log in (("lst_c", "lst", False), ("ndvi", "ndvi_low", False),
                            ("population", "pop", True), ("pop_vulnerable", "vuln", True),
                            ("pop_density_km2", "pop_density", True), ("vuln_share", "vuln_share", False),
                            ("trees_prob", "trees_low", False)):
        if col not in feat or col not in anchor:
            continue
        x, a = feat[col], anchor[col]
        if log:
            x, a = np.log1p(x), np.log1p(a)
        c[name] = anchored(x, a, clip, method)
    c["ndvi_low"] = 1 - c.ndvi_low
    if "trees_low" in c:
        c["trees_low"] = 1 - c.trees_low
    distance = feat.park_distance_used_m if "park_distance_used_m" in feat else feat.park_distance_m
    c["park_deficit"] = distance.clip(0, park_cap) / park_cap if park_mode == "continuous" else (distance > park_thr).astype(float).where(distance.notna())
    return c


def selection_analysis(baseline, feat, paths):
    f = feat.copy()
    f["selection_group"] = np.select([baseline.f_park_route_missing, baseline.f_lst_low_valid],
                                      ["route_missing", "thermal_QA_excluded"], default="audited_included")
    write_csv(f[[C.KEY, "kota", "selection_group", "valid", "eligibility_reasons"]],
              paths.tables / "selection_membership.csv")
    profiles = []
    measures = ["lst_c", "ndvi", "population", "pop_vulnerable", "vuln_share", "area_km2", "coverage_ratio",
                "grid_snap_m", "lst_valid_frac", "component_nodes", "component_park_nodes"]
    for (city, group), t in f.groupby(["kota", "selection_group"]):
        for col in measures:
            values = t[col] if col in t else pd.Series(dtype=float)
            ref = f.loc[f.selection_group == "audited_included", col] if col in f else pd.Series(dtype=float)
            pooled = np.sqrt((values.var() + ref.var()) / 2)
            profiles.append({"kota": city, "selection_group": group, "variable": col, "n_grid": len(t),
                             "n_observed": int(values.notna().sum()), "n_missing": int(values.isna().sum()),
                             "sum": values.sum(min_count=1), "mean": values.mean(), "q25": values.quantile(.25),
                             "median": values.median(), "q75": values.quantile(.75),
                             "standardized_mean_difference_vs_included": (values.mean() - ref.mean()) / pooled if pooled > 0 else np.nan,
                             "n_age_no_support": int(t.qa_age_source_no_support.sum()),
                             "n_total_no_support": int(t.qa_population_source_no_support.sum())})
    write_csv(pd.DataFrame(profiles), paths.tables / "eligibility_selection_profile.csv")
    city_rows = []
    for model in ("M1", "M2", "M3"):
        for universe, mask in (("model_specific", f[f"elig_{model.lower()}"]), ("common", f.valid)):
            v = f.loc[mask]
            _, rk = M.score_rank(v, C.MODELS[model])
            top = v.loc[rk <= M.n_top(len(v))]
            write_csv(v[[C.KEY, "kota"]].assign(rank=rk, top=rk <= M.n_top(len(v)), model=model, universe=universe),
                      paths.tables / f"{model.lower()}_{universe}_eligibility.csv")
            for city, t in v.groupby("kota"):
                tt = top.loc[top.kota == city]
                city_rows.append({"model": model, "universe": universe, "kota": city, "n_eligible": len(t),
                                  "n_top": len(tt), "population_supported_sum": t.population.sum(min_count=1),
                                  "top_population_supported_sum": tt.population.sum(min_count=1),
                                  "area_km2": t.area_km2.sum(), "top_area_km2": tt.area_km2.sum()})
    write_csv(pd.DataFrame(city_rows), paths.tables / "full_area_vs_common_city.csv")
    thermal = feat.loc[feat.elig_m1]
    _, rk = M.score_rank(thermal, C.MODELS["M1"])
    lost = thermal.loc[(rk <= M.n_top(len(thermal))) & ~thermal.valid]
    write_csv(lost[[C.KEY, "kota", "lst_c", "f_park_route_missing"]], paths.tables / "full_thermal_top_lost.csv")
    anchor = feat.loc[feat.valid]
    possible = feat.loc[feat.elig_m2 & feat[["population", "pop_child", "pop_elderly"]].notna().all(axis=1) & ~feat.f_age_gt_pop].copy()
    comp = fixed_components(possible, anchor)
    base_score = .3 * comp.lst + .2 * comp.ndvi_low + .25 * comp.vuln
    known = comp.park_deficit.notna()
    low = base_score + .25 * comp.park_deficit.fillna(0)
    high = base_score + .25 * comp.park_deficit.fillna(1)
    lower, upper = low.to_numpy(), high.to_numpy()
    # Conservative interval ranks: all ties count as possibly ahead; deterministic tie details do not narrow bounds.
    best = 1 + (lower[None, :] > upper[:, None]).sum(axis=1)
    worst = (upper[None, :] >= lower[:, None]).sum(axis=1)
    bounds = possible[[C.KEY, "kota", "park_distance_m", "population"]].copy()
    bounds["m4_lower_fixed_anchors"], bounds["m4_upper_fixed_anchors"] = low, high
    bounds["best_rank_bound"], bounds["worst_rank_bound"] = best, worst
    for frac in C.TOP_FRACS:
        label = int(100 * frac)
        budget = M.n_top(len(bounds), frac)
        bounds[f"possibly_top{label}"] = best <= budget
        bounds[f"guaranteed_top{label}"] = worst <= budget
    write_csv(bounds, paths.tables / "missing_access_bounds.csv")
    return f


def rs_scenarios(feat, paths):
    anchor = feat.loc[feat.valid]
    nonrs = feat.valid_p2 & feat.lst_c.notna() & feat.ndvi.notna()
    variants = {"support_50pct": feat.lst_valid_frac >= .5,
                "support_25pct_flagged": feat.lst_valid_frac >= .25,
                "include_delivered_flagged": feat.lst_valid_frac >= 0,
                "support_50pct_and_rs_qa_ok": (feat.lst_valid_frac >= .5) & ~feat.f_rs_qa}
    br = by_id(anchor, M.score_rank(anchor, C.MODELS["M4"])[1])
    rows, members = [], []
    for name, mask in variants.items():
        v = feat.loc[nonrs & mask]
        comp = fixed_components(v, anchor)
        s = M.weighted_score(comp, C.MODELS["M4"])
        rk = M.rank_desc(s, v[C.KEY], M.weighted_score(fixed_components(v, anchor, clip=None), C.MODELS["M4"]))
        rr = by_id(v, rk)
        block = compare_rankings(br, rr, name, "thermal_support", "eligibility_changing_fixed_baseline_anchors")
        for row in block:
            row["target_eligible"] = "JKT_R037_C062" in set(v[C.KEY])
        rows += block
        members.append(v[[C.KEY, "lst_c", "ndvi", "lst_valid_frac", "coverage_ratio", "rs_qa_flags"]].assign(
            scenario=name, score=s, rank=rk))
    write_csv(pd.DataFrame(rows), paths.tables / "rs_eligibility_sensitivity.csv")
    write_csv(pd.concat(members), paths.tables / "rs_scenario_membership.csv")
    write_json(paths.tables / "rs_target_support.json", {"grid_id": "JKT_R037_C062", "delivered": True,
        "valid_lst_area_m2_auditor": 6724.1312, "clipped_grid_area_m2_auditor": 24223.1114,
        "independent_support_fraction": 6724.1312 / 24223.1114,
        "nominal_cell_coverage_fraction": 24223.1114 / 250000,
        "interpretation": "Different denominators; support threshold is provisional modeling QA, never missing delivery"})


def scenario_families(feat, inputs, paths):
    """Replayable scenario registry plus bounded joint factorial. Missing GIS versions stay blocked."""
    from . import sensitivity as SE
    v = feat.loc[feat.valid]
    registry, comparisons, membership = [], [], []
    def add(name, family, candidate, weights=None, kw=None, stress=False, assumption=""):
        weights, kw = weights or C.MODELS["M4"], kw or {}
        candidate = candidate.loc[candidate.valid].copy()
        common = v.loc[v[C.KEY].isin(candidate[C.KEY])]
        fixed = candidate.loc[candidate[C.KEY].isin(v[C.KEY])]
        # Fixed comparisons use components anchored to the same ID set for both versions.
        for mode, a, b in (("eligibility_changing_refit_anchors", v, candidate),
                            ("fixed_intersection_same_anchors", common, fixed)):
            _, ar = M.score_rank(a, C.MODELS["M4"])
            if mode.startswith("fixed"):
                bc = fixed_components(b, a, **kw)
                raw_kw = {k: value for k, value in kw.items() if k not in ("clip", "method")}
                braw = fixed_components(b, a, clip=None, **raw_kw) if kw.get("method") != "rank" else bc
                _, rb = rank(bc, braw, weights, b[C.KEY])
            else:
                _, rb = M.score_rank(b, weights, **kw)
            comparisons.extend(compare_rankings(by_id(a, ar), by_id(b, rb), name, family, mode))
            for gid, rk in zip(b[C.KEY], rb):
                membership.append({C.KEY: gid, "scenario": name, "family": family, "comparison": mode,
                                   "rank": rk, "n_eligible": len(b), "top10": rk <= M.n_top(len(b))})
        registry.append({"scenario": name, "family": family, "status": "EXECUTED", "stress_assumption": stress,
                         "weights": json.dumps(weights, sort_keys=True), "parameters": json.dumps(kw, sort_keys=True),
                         "assumption": assumption, "approval": "PROVISIONAL; team envelope unsigned"})
    for scenario in SE.build_scenarios(C.MODELS["M4"], feat):
        f = feat.copy()
        if scenario.policy:
            f = D.clean_values(f, scenario.policy)
        if scenario.exclude:
            f["valid"] &= ~f[scenario.exclude]
        for col in scenario.require:
            f["valid"] &= f[col].notna()
        # Use used distance consistently for assumed scenarios, never mutate observed distance.
        if scenario.policy:
            f["assumed_park_distance_m"] = f.park_distance_used_m
        add(scenario.name, scenario.group, f, scenario.weights, scenario.kw,
            stress=bool(scenario.policy), assumption=scenario.note)
    fractional = feat.copy()
    integrated = inputs.name == "integrated_comparisons"
    if integrated:
        source = pd.read_csv(paths.root / "outputs/qa/remediation_agent2/partial_grid_scenarios.csv").set_index(C.KEY)
        for col in ("population", "pop_child", "pop_elderly"):
            fractional[col] = fractional[C.KEY].map(source[f"{col}_fractional"])
    else:
        source = pd.read_csv(inputs / "auditor_raster_support.csv").set_index(C.KEY)
        for col in ("population", "pop_child", "pop_elderly"):
            fractional[col] = fractional[C.KEY].map(source[f"{col}_exact_sum"])
    fractional = D.clean_values(fractional)
    add("uniform_fractional_agent2_values" if integrated else "uniform_fractional_auditor_values", "aggregation", fractional,
        assumption="Uniform pixel-area allocation sensitivity; versioned source support nulls retained")
    for threshold in (.25, .5):
        f = feat.copy()
        f["valid"] = f.valid_p2 & f.lst_c.notna() & f.ndvi.notna() & (f.lst_valid_frac >= threshold)
        add(f"thermal_support_{threshold}", "thermal_support", f)
    add("corrected_support", "missing_support", feat, assumption="Versioned demographic support consumed by loader")
    routes_path = paths.processed / "agent2_route_scenarios.csv"
    if routes_path.exists():
        routes = pd.read_csv(routes_path)
        for scenario, table in routes.groupby("scenario_id"):
            f = feat.copy()
            table = table.set_index(C.KEY)
            if set(table.index) != set(f[C.KEY]) or not table.index.is_unique:
                raise DataError(f"Route scenario {scenario}: exact unique master IDs required")
            f["park_distance_m"] = f[C.KEY].map(table["park_distance_m"])
            f = D.clean_values(f)
            add(f"agent2_{scenario}", "route_policy", f,
                stress="positive" in scenario,
                assumption="Agent2 per-grid route version; unknown routes remain null; candidate proxy")
    # 2 x 2 x 2 x 2 joint envelope; bounded, prespecified alternatives, never optimized for results.
    for demography, cap, norm, aggregation in itertools.product(("vuln", "pop"), (750., 1500.), ("clipped", "rank"), ("legacy", "fractional")):
        w = {"lst": .3, "ndvi_low": .2, demography: .25, "park_deficit": .25}
        name = f"joint_{demography}_cap{cap:g}_{norm}_{aggregation}"
        add(name, "joint_factorial", feat if aggregation == "legacy" else fractional, w,
            {"park_cap": cap, "method": "rank" if norm == "rank" else "minmax"},
            assumption="2 constructs x 2 caps x 2 normalizations x 2 aggregation rules; shared support policy")
    for name, family, dependency in (("verified_physical_entrances", "entrance_barrier", "AC-01/02 physical entrance evidence unavailable"),
                                      ("historical_2024", "temporal", "TM-01 mixed-period framing proposed; optional if approved"),
                                      ("seasonal_composite", "thermal_sampling", "RS-01 alternative composite unavailable")):
        registry.append({"scenario": name, "family": family, "status": "BLOCKED" if family != "temporal" else "CONDITIONAL",
                         "stress_assumption": "stress" in name, "assumption": dependency, "approval": "pending coordinator/source owner"})
    table = pd.DataFrame(comparisons)
    write_csv(table, paths.tables / "robustness_by_family.csv")
    write_csv(pd.DataFrame(registry), paths.root / "docs/scenario_registry.csv")
    mem = pd.DataFrame(membership)
    write_csv(mem, paths.tables / "joint_scenario_priority_sets.csv")
    write_csv(table.groupby(["family", "comparison", "top_fraction"]).agg(
        n_scenarios=("scenario", "nunique"), min_jaccard=("jaccard", "min"), max_jaccard=("jaccard", "max")
    ).reset_index(), paths.tables / "robustness_family_summary.csv")
    st = mem.loc[(mem.family == "joint_factorial") & (mem.comparison == "fixed_intersection_same_anchors")]
    stability = st.groupby(C.KEY).agg(n_scenarios=("scenario", "nunique"), n_top=("top10", "sum")).reset_index()
    stability["scenario_frequency"] = stability.n_top / stability.n_scenarios
    write_csv(stability, paths.tables / "joint_scenario_stability.csv")


def spatial_sensitivity(feat, pri, paths, high_perms=9999):
    from . import spatial as SP
    geo = D.read_grid_gdf(paths.grid).merge(pri.loc[pri.valid, [C.KEY, "m4_score"]], on=C.KEY, validate="one_to_one")
    w, used, islands = SP.prepare_weights(geo)
    neighbors = [{C.KEY: used.iloc[i][C.KEY], "neighbor_id": used.iloc[j][C.KEY], "weight": w.weights[i][n]}
                 for i, js in w.neighbors.items() for n, j in enumerate(js)]
    write_csv(pd.DataFrame(neighbors), paths.tables / "spatial_weight_neighbors.csv")
    write_json(paths.tables / "spatial_weight_manifest.json", {"kind": "queen", "row_standardized": True,
               "n": len(used), "directed_pairs": len(neighbors), "islands": islands,
               "esda": __import__("esda").__version__, "seed": C.SEED})
    variants = [("directed", 999), ("two-sided", 999), ("directed", high_perms), ("two-sided", high_perms)]
    tables, rows = [], []
    reference = None
    for alternative, perms in variants:
        t = SP.local_moran(used.m4_score, w, perms, alternative=alternative)
        t[C.KEY] = used[C.KEY].to_numpy()
        t["variant"] = f"{alternative}_{perms}"
        if reference is None:
            reference = t.set_index(C.KEY)
        for correction in ("klaster_p05", "klaster_fdr", "klaster_by"):
            labels = t.set_index(C.KEY)[correction]
            rows.append({"alternative": alternative, "permutations": perms, "correction": correction,
                         "n": len(t), "n_significant": int((labels != "ns").sum()),
                         "changed_vs_directed999_BH": int((labels != reference.klaster_fdr).sum()),
                         "minimum_attainable_p": 1 / (perms + 1)})
        tables.append(t)
    write_csv(pd.DataFrame(rows), paths.tables / "lisa_tail_permutation_sensitivity.csv")
    write_csv(pd.concat(tables), paths.tables / "lisa_tail_permutation_grid.csv")


def figures(feat, paths):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from . import figures as F
    geo = D.read_grid_gdf(paths.grid).to_crs(C.CRS_PROJECTED)
    boundary = __import__("geopandas").read_file(paths.boundary).to_crs(C.CRS_PROJECTED)
    paths.figures.mkdir(parents=True, exist_ok=True)
    from matplotlib import patheffects
    # Fixed SVG id salt and no SVG date: identical inputs give byte-stable vector figures across replays.
    matplotlib.rcParams["svg.hashsalt"] = "jhim-remediation-figures"
    manifest = []
    # Geometry inputs are part of every map; each source is a real inspectable file with its content hash.
    geometry_sources = [paths.grid, paths.boundary]

    def rel(p):
        p = Path(p).resolve()
        try:
            return p.relative_to(Path(paths.root).resolve()).as_posix()
        except ValueError:
            return p.as_posix()

    def save(fig, name, sources, claim, maps=True):
        # Placed below the axes (va=top); bbox_inches="tight" expands the canvas so it never overlaps axis labels.
        fig.text(.5, 0, "Exploratory: thermal/demography 2024; OSM 2026 candidate-park proxy; five mainland cities",
                 ha="center", va="top", fontsize=7)
        files = [*sources, *(geometry_sources if maps else [])]
        missing = [str(f) for f in files if not Path(f).exists()]
        if missing:
            raise DataError(f"Figure {name} source missing: {missing}")
        for fmt in ("png", "svg"):
            file = paths.figures / f"{name}.{fmt}"
            fig.savefig(file, dpi=150, bbox_inches="tight", metadata={"Date": None} if fmt == "svg" else None)
            manifest.append({"figure": rel(file), "sha256": sha256(file),
                             "source_files": ";".join(rel(f) for f in files),
                             "source_sha256": ";".join(sha256(f) for f in files),
                             "claim": claim, "independence": "same model inputs; not external validation"})
        plt.close(fig)

    def context(ax):
        boundary.boundary.plot(ax=ax, color="#444444", linewidth=.5)
        city_col = next((c for c in ("kota", "NAMOBJ", "WADMKK", "name") if c in boundary), None)
        if city_col:
            # Halo text instead of an opaque box so city names never hide priority cells.
            for _, row in boundary.iterrows():
                point = row.geometry.representative_point()
                ax.annotate(str(row[city_col]).replace("Kota Jakarta ", ""), (point.x, point.y), fontsize=6,
                            ha="center", color="#222222", alpha=.9,
                            path_effects=[patheffects.withStroke(linewidth=1.8, foreground="white")])

    def mark_small(ax, ids, color, label):
        # Coastal/edge cells are clipped slivers; a marker keeps rare categories visible at print scale.
        pts = geo.loc[geo[C.KEY].isin(ids)].geometry.representative_point()
        if len(pts):
            return ax.scatter(pts.x, pts.y, s=28, facecolor="none", edgecolor=color, linewidth=1.1, label=label, zorder=5)
        return None

    shift_colors = {"entered": "#b2182b", "left": "#2166ac", "stable": "#762a83", "other eligible": "#dddddd"}
    members_file = paths.tables / "priority_membership.csv"
    members = pd.read_csv(members_file)
    for name, column, title, claim in [
        ("matched_weight_priority_shifts", "matched_shift", "M4 vs proportional M3 + park: top 10% on fixed IDs and anchors",
         "M4 vs proportional M3 + park: fixed IDs and anchors"),
        ("matched_park_increment", "park_increment_shift", "M3 vs .75 M3 + .25 park: proportional matched addition (top 10%)",
         "Added park term separated from residual reweighting and age swap")]:
        counts = members[column].value_counts()
        fig, ax = plt.subplots(figsize=(8, 7))
        F.map_categories(geo, members[C.KEY], members[column], shift_colors, title, ax,
                         legend_labels={k: f"{k} (n={int(counts.get(k, 0))})" for k in shift_colors})
        context(ax)
        save(fig, name, [members_file], claim)

    route, thermal = feat.f_park_route_missing.astype(bool), feat.f_lst_low_valid.astype(bool)
    demographic = feat.qa_age_source_no_support.astype(bool) | feat.qa_population_source_no_support.astype(bool)
    other = ~feat.valid.astype(bool) & ~route & ~thermal & ~demographic
    n_reasons = route.astype(int) + thermal.astype(int) + demographic.astype(int) + other.astype(int)
    reason = pd.Series(np.select([n_reasons > 1, route, thermal, demographic, other],
                                 ["multiple reasons", "route unknown", "thermal QA", "demographic unsupported", "other QA"],
                                 default="eligible"), index=feat.index)
    reason_colors = {"eligible": "#dddddd", "route unknown": "#762a83", "thermal QA": "#e66101",
                     "demographic unsupported": "#1b9e77", "multiple reasons": "#000000", "other QA": "#a6761d"}
    counts = reason.value_counts()
    reason_colors = {k: v for k, v in reason_colors.items() if k in counts or k in ("eligible", "route unknown")}
    fig, ax = plt.subplots(figsize=(8, 7))
    F.map_categories(geo, feat[C.KEY], reason, reason_colors,
                     f"Selection into shared comparison (n={int(feat.valid.sum())} of {len(feat)}); unknown remains explicit", ax,
                     legend_labels={k: f"{k} (n={int(counts.get(k, 0))})" for k in reason_colors})
    legend = ax.get_legend()
    handles = [h for key in ("thermal QA", "demographic unsupported", "multiple reasons") if key in reason_colors
               for h in [mark_small(ax, feat.loc[reason == key, C.KEY], reason_colors[key], f"{key}: location marker")] if h]
    ax.add_artist(legend)
    if handles:
        ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0, .22), fontsize=6, frameon=False)
    context(ax)
    save(fig, "eligibility_and_excluded_priority_map", [paths.modeling / "eligibility_by_model.csv", paths.merged],
         "Selection into shared comparison; overlapping reasons shown as 'multiple reasons'; unknown remains explicit")
    # Model-specific full-area and common-set priority maps have separately declared universes/budgets.
    fig, axs = plt.subplots(3, 2, figsize=(12, 17))
    universe_files = []
    for i, model in enumerate(("m1", "m2", "m3")):
        for j, universe in enumerate(("model_specific", "common")):
            file = paths.tables / f"{model}_{universe}_eligibility.csv"
            universe_files.append(file)
            t = pd.read_csv(file)
            label = t.top.map({True: "top", False: "other eligible"})
            F.map_categories(geo, t[C.KEY], label, {"top": "#b2182b", "other eligible": "#dddddd"},
                             f"{model.upper()} {universe}: n={len(t)}, top={int(t.top.sum())}", axs[i, j])
            context(axs[i, j])
    save(fig, "model_specific_vs_common", universe_files, "Different analysis universes; hatched excluded/unknown")
    stability_file = paths.tables / "joint_scenario_stability.csv"
    stability = pd.read_csv(stability_file)
    fig, ax = plt.subplots(figsize=(8, 7))
    F.map_grid(geo, stability.scenario_frequency, stability[C.KEY],
               "Top-10% frequency across 16 executed joint scenarios (not probability; access families pending)",
               "Blues", 0, 1, ax, label="fraction of 16 joint scenarios")
    context(ax)
    save(fig, "scenario_family_stability", [stability_file], "Conditional on executed families; access families pending")
    contribution_file = paths.tables / "component_contributions.csv"
    contribution = pd.read_csv(contribution_file)
    fig, ax = plt.subplots(figsize=(8, 4))
    contribution[["m4_lst_contribution", "m4_ndvi_low_contribution", "m4_vuln_contribution", "m4_park_deficit_contribution"]].mean().plot.bar(ax=ax)
    ax.set(ylabel="Mean weighted contribution to M4", title=f"Arithmetic contributions (n={len(contribution)}); no causal attribution")
    ax.set_xticklabels(["LST", "low NDVI", "age count", "park proxy"], rotation=0)
    save(fig, "component_contributions", [contribution_file], "Weighted terms sum exactly to score", maps=False)
    burden_file = paths.tables / "count_composition_burden.csv"
    burden = pd.read_csv(burden_file)
    share = burden.vuln_share.dropna()
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.scatter(burden.pop_vulnerable, burden.vuln_share, s=4, alpha=.35)
    ax.set(xlabel="Modeled child + elderly count (persons/grid)", ylabel="Child + elderly share\n(positive total denominator)",
           title=f"Count and composition answer different questions (n={len(share)}; "
                 f"share p05–p95 {share.quantile(.05):.3f}–{share.quantile(.95):.3f})")
    ax.title.set_fontsize(9)
    save(fig, "count_versus_composition", [burden_file], "Population magnitude and age composition separately; share range is narrow", maps=False)
    # Reproducible cases are grid/city contexts, never invented neighborhood names or verified access.
    # Balanced by direction: the four largest M3->M4 gains and four largest losses (ties broken by grid ID).
    att_file = paths.tables / "rank_change_attribution.csv"
    att = pd.read_csv(att_file)
    ordered = att.sort_values(["rank_gain", C.KEY], ascending=[False, True])
    gains = ordered.head(4).assign(case_selection="largest M3->M4 rank gain")
    losses = att.sort_values(["rank_gain", C.KEY], ascending=[True, True]).head(4).assign(case_selection="largest M3->M4 rank loss")
    cases = pd.concat([gains, losses], ignore_index=True).merge(feat, on=[C.KEY, "kota"], validate="one_to_one")
    cases_file = paths.tables / "geographic_cases.csv"
    write_csv(cases, cases_file)
    fig, ax = plt.subplots(figsize=(10, 8))
    lim = float(np.ceil(att.rank_gain.abs().max() / 100) * 100)
    F.map_grid(geo, att.rank_gain, att[C.KEY], "M3→M4 rank change; labelled: 4 largest gains and 4 largest losses",
               "RdBu_r", -lim, lim, ax, legend=False)
    # Horizontal colorbar keeps both side margins free for case labels.
    scale = plt.cm.ScalarMappable(cmap="RdBu_r", norm=matplotlib.colors.Normalize(-lim, lim))
    fig.colorbar(scale, ax=ax, orientation="horizontal", fraction=.035, pad=.02, shrink=.6,
                 label="rank gain = M3 rank − M4 rank (positive = higher M4 priority)")
    context(ax)
    locations = geo.merge(cases[[C.KEY, "rank_gain"]], on=C.KEY, validate="one_to_one")
    pts = locations.geometry.representative_point()
    locations = locations.assign(px=pts.x, py=pts.y)
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    mid = (x0 + x1) / 2
    # Labels sit in the left/right margins with leader lines, so they cannot cover city names or each other.
    for side, part in locations.groupby(locations.px >= mid):
        part = part.sort_values("py", ascending=False).reset_index(drop=True)
        ys = np.linspace(y1 - .08 * (y1 - y0), y0 + .25 * (y1 - y0), max(len(part), 2))[:len(part)]
        tx = x1 + .02 * (x1 - x0) if side else x0 - .02 * (x1 - x0)
        for (_, row), ty in zip(part.iterrows(), ys):
            ax.annotate(f"{row[C.KEY]} ({int(row.rank_gain):+d})", (row.px, row.py), xytext=(tx, ty), textcoords="data",
                        ha="left" if side else "right", va="center", fontsize=6, annotation_clip=False,
                        arrowprops={"arrowstyle": "-", "linewidth": .4, "color": "#333333"})
        ax.scatter(part.px, part.py, s=22, facecolor="none", edgecolor="black", linewidth=.8, zorder=5)
    save(fig, "annotated_geographic_cases", [cases_file, att_file],
         "Grid-level arithmetic shift in both directions; independent entrance evidence unavailable")
    paper = paths.root / "outputs/remediation/paper"
    write_csv(pd.DataFrame(manifest), paper / "figure_manifest.csv")


def run(root, audit, high_perms=9999, skip_spatial=False, integrated=False):
    from . import pipeline as P
    root = Path(root)
    if integrated:
        for name in ("JHIM_INPUT_DIR", "JHIM_RS_PATH", "JHIM_DEMOGRAPHIC_SUPPORT", "JHIM_DEMOGRAPHIC_CORRECTED"):
            os.environ.pop(name, None)
        inputs = prepare_integrated_inputs(root, audit)
    else:
        inputs = prepare_inputs(root, audit)
        os.environ["JHIM_INPUT_DIR"] = str(inputs)
        os.environ.pop("JHIM_RS_PATH", None)
        os.environ["JHIM_DEMOGRAPHIC_SUPPORT"] = str(inputs / "demographic_support.csv")
        os.environ.pop("JHIM_DEMOGRAPHIC_CORRECTED", None)
    paths = C.RemediationPaths(root=root)
    baseline = pd.read_csv(inputs / "audited_merged_grid.csv")
    feat, meta, status = D.load_features(paths)
    network = pd.read_csv(inputs / "auditor_network.csv")
    feat = feat.merge(network[[C.KEY, "component", "component_nodes", "component_park_nodes"]], on=C.KEY, validate="one_to_one")
    write_csv(feat, paths.merged)
    write_json(paths.merged_meta, meta)
    write_csv(feat[[C.KEY, "elig_m1", "elig_m2", "elig_m3", "elig_m4", "valid", "eligibility_reasons",
                    "qa_age_source_no_support", "qa_population_source_no_support", "support_version"]], paths.modeling / "eligibility_by_model.csv")
    write_csv(D.quality_table(feat), paths.tables / "data_quality.csv")
    pri, pmeta = P.step_priority(paths, feat, meta)
    P.step_compare(paths, feat, pri)
    support_analysis(baseline, feat, paths)
    ablations(feat, paths)
    selection_analysis(baseline, feat, paths)
    rs_scenarios(feat, paths)
    scenario_families(feat, inputs, paths)
    if not skip_spatial:
        P.step_spatial(paths, feat, pri, perms=999)
        spatial_sensitivity(feat, pri, paths, high_perms)
    figures(feat, paths)
    # GIS includes missingness/support and per-model eligibility, matching the exported tables by ID.
    geo = D.read_grid_gdf(paths.grid).merge(feat, on=C.KEY, validate="one_to_one").merge(
        pri.drop(columns="valid"), on=C.KEY, validate="one_to_one")
    for col in geo:
        if str(geo[col].dtype) in ("Int64", "boolean"):
            geo[col] = geo[col].astype(float)
    paths.gis.mkdir(parents=True, exist_ok=True)
    geo.to_file(paths.gis / "priority_models.gpkg", layer="priority_models", driver="GPKG")
    steps = ["remediation", "merge", "priority", "compare", "ablations", "selection", "scenario_families", "figures"]
    if not skip_spatial:
        steps += ["spatial", "lisa_sensitivity"]
    manifest = P.write_manifest(paths, steps, {"source": "real-integrated-candidate" if integrated else "real-audited-derived-candidate", "n_valid": int(feat.valid.sum()),
                    "runtime": {"permutations": 999, "high_permutations": high_perms, "seed": C.SEED,
                                "skip_spatial": skip_spatial, "local_alternative": "directed", "top_frac": C.TOP_FRAC},
                    "limitations": ["Acquisition lineage and physical entrance verification remain incomplete",
                                    "All scientific policy alternatives unsigned; audited official baseline retained"],
                    "frozen_lineage": json.loads((inputs / "input_lineage.json").read_text(encoding="utf-8"))})
    return manifest
