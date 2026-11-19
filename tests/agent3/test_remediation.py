"""Scientific regressions from auditor findings; real frozen artifacts checked independently."""
import json

import numpy as np
import pandas as pd
import pytest

from jhim import config as C, data as D, models as M, pipeline as P, provenance as PV, remediation as R
from jhim.util import DataError
from conftest import REPO


def support_table(paths):
    ids = pd.read_csv(paths.spatial_features).grid_id
    return pd.DataFrame({"grid_id": ids, "support_version": "test-source-v1",
                         "qa_population_source_no_support": False, "qa_age_source_no_support": False})


def test_unsupported_zeros_propagate_to_scores_and_eligibility(root_full):
    s = support_table(root_full)
    s.loc[0, "qa_age_source_no_support"] = True
    s.loc[1, ["qa_age_source_no_support", "qa_population_source_no_support"]] = True
    s.to_csv(root_full.demographic_support, index=False)
    f, _, _ = D.load_features(root_full)
    assert f.loc[:1, ["pop_child", "pop_elderly", "pop_vulnerable", "vuln_share"]].isna().all().all()
    assert np.isnan(f.loc[1, "population"]) and f.loc[1, "raw_population"] > 0
    assert f.loc[:1, "elig_m1"].all() and f.loc[:1, "elig_m2"].all()
    assert not f.loc[1, "elig_m3"] and not f.loc[:1, "elig_m4"].any()
    pri = M.build_priority_table(f)
    assert pri.loc[:1, ["m3_score", "m4_score"]].isna().all().all()
    assert "missing_age_support" in f.loc[0, "eligibility_reasons"]
    # A genuine supported zero stays distinct; zero-denominator composition is undefined.
    assert f.loc[3, "population"] == 0 and np.isnan(f.loc[3, "vuln_share"])
    assert f.loc[3, "valid"]


def test_corrected_values_preserve_raw_exports(root_full):
    s = support_table(root_full)
    s.to_csv(root_full.demographic_support, index=False)
    corrected = pd.read_csv(root_full.spatial_features)[[C.KEY, "population", "pop_child", "pop_elderly"]]
    old = corrected.loc[0, "pop_child"]
    corrected["support_version"] = "test-source-v1"
    corrected.loc[0, "pop_child"] = old / 2
    corrected.to_csv(root_full.demographic_corrected, index=False)
    f, _, _ = D.load_features(root_full)
    assert f.loc[0, "pop_child"] == pytest.approx(old / 2)
    assert f.loc[0, "raw_pop_child"] == pytest.approx(old)


@pytest.mark.parametrize("bad", ["partial_ids", "invalid_flag", "missing_version"])
def test_support_contract_failures_are_not_silently_accepted(root_full, bad):
    s = support_table(root_full)
    if bad == "partial_ids":
        s = s.iloc[1:]
    elif bad == "invalid_flag":
        s["qa_age_source_no_support"] = "unknown"
    else:
        s = s.drop(columns="support_version")
    s.to_csv(root_full.demographic_support, index=False)
    with pytest.raises(DataError):
        D.load_features(root_full)


def test_manifest_detects_config_code_runtime_support_and_output_mutation(root_full, monkeypatch, tmp_path):
    # Minimal actual model outputs; safe mutations only in test workspace/config memory.
    source = tmp_path / "source"
    (source / "jhim").mkdir(parents=True)
    code = source / "jhim/science.py"
    code.write_text("coefficient = 1\n")
    monkeypatch.setattr(PV, "SOURCE_ROOT", source)
    s = support_table(root_full)
    s.to_csv(root_full.demographic_support, index=False)
    f, meta = P.step_merge(root_full)
    P.step_priority(root_full, f, meta)
    manifest = P.write_manifest(root_full, ["merge", "priority"], {"runtime": {"permutations": 19, "seed": 42}})
    assert not P.official_outputs_status(root_full)["stale_inputs"]
    assert "runtime_parameters" in P.official_outputs_status(root_full, {"permutations": 999})["stale_inputs"]
    monkeypatch.setitem(C.MODELS["M4"], "lst", .31)
    assert "scientific_config" in P.official_outputs_status(root_full)["stale_inputs"]
    monkeypatch.setitem(C.MODELS["M4"], "lst", .3)
    code.write_text("coefficient = 2\n")
    assert "implementation" in P.official_outputs_status(root_full)["stale_inputs"]
    code.write_text("coefficient = 1\n")
    s.loc[0, "qa_age_source_no_support"] = True
    s.to_csv(root_full.demographic_support, index=False)
    assert "demographic_support" in P.official_outputs_status(root_full)["stale_inputs"]
    root_full.priority.write_text(root_full.priority.read_text() + "\n")
    assert "output_content" in P.official_outputs_status(root_full)["stale_inputs"]
    assert manifest["runtime"]["permutations"] == 19


def test_fixed_anchor_transform_preserves_reference(feat_full):
    f = feat_full.loc[feat_full.valid]
    for kwargs in ({}, {"clip": None}, {"method": "rank"}, {"park_cap": 750}, {"park_mode": "binary", "park_thr": 500}):
        a, b = R.fixed_components(f, f, **kwargs), M.components(f, **kwargs)
        for col in a:
            np.testing.assert_allclose(a[col], b[col], atol=1e-12, equal_nan=True)


def test_actual_top_budget_override_not_replaced_by_default(root_full):
    f, meta = P.step_merge(root_full)
    pri, pmeta = P.step_priority(root_full, f, meta, top_frac=.2)
    assert pmeta["top_frac"] == .2 and pmeta["n_top"] == 16
    assert pri.m4_top.sum() == 16


def test_explicit_spatial_tail_BH_and_BY_matches_independent_reference():
    from conftest import make_grid_gdf
    from jhim import spatial as SP
    from esda.moran import Moran_Local
    from scipy.stats import false_discovery_control
    g = make_grid_gdf()
    w, used, _ = SP.prepare_weights(g)
    y = np.arange(len(used)) + np.sin(np.arange(len(used)))
    for alternative in ("directed", "two-sided"):
        t = SP.local_moran(y, w, 99, seed=11, alternative=alternative)
        independent = Moran_Local(y, w, permutations=99, seed=11, alternative=alternative)
        np.testing.assert_allclose(t.p_sim, independent.p_sim)
        assert ((t.klaster_fdr != "ns") == (false_discovery_control(t.p_sim, method="bh") <= .05)).all()
        assert ((t.klaster_by != "ns") == (false_discovery_control(t.p_sim, method="by") <= .05)).all()
        assert (t.p_sim >= .01).all()


TABLES = REPO / "outputs/remediation/tables"
HAVE_CANDIDATE = (TABLES / "component_contributions.csv").exists()


@pytest.mark.skipif(not HAVE_CANDIDATE, reason="real remediation candidate not yet generated")
def test_real_independent_contributions_and_attribution():
    t = pd.read_csv(TABLES / "component_contributions.csv")
    for model in C.MODELS:
        k = model.lower()
        cols = [c for c in t if c.startswith(k + "_") and c.endswith("_contribution")]
        np.testing.assert_allclose(t[cols].sum(axis=1), t[f"{k}_score"], atol=1e-10, rtol=0)
    np.testing.assert_allclose(t.filter(regex="^delta_").sum(axis=1), t.m4_score - t.m3_score, atol=1e-10, rtol=0)
    a = pd.read_csv(TABLES / "rank_change_attribution.csv")
    np.testing.assert_allclose(a.filter(regex="^shapley_rank_gain_").sum(axis=1), a.m3_rank - a.m4_rank, atol=1e-10)
    # Independent real-data normalized-score formula; no call to model scoring helpers.
    f = pd.read_csv(REPO / "data/processed/modeling_remediation/merged_grid.csv")
    v = f.loc[f.valid].set_index(C.KEY).loc[t.grid_id]
    def n(x):
        lo, hi = x.quantile(.05), x.quantile(.95)
        return ((x - lo) / (hi - lo)).clip(0, 1)
    score = .3 * n(v.lst_c) + .2 * (1 - n(v.ndvi)) + .25 * n(np.log1p(v.pop_child + v.pop_elderly)) + .25 * v.park_distance_m.clip(upper=1000) / 1000
    np.testing.assert_allclose(score.to_numpy(), t.m4_score, atol=1e-10, rtol=0)


@pytest.mark.skipif(not HAVE_CANDIDATE, reason="real remediation candidate not yet generated")
def test_real_support_selection_and_bounds_reconcile():
    f = pd.read_csv(REPO / "data/processed/modeling_remediation/merged_grid.csv")
    assert len(f) == 2765 and f.grid_id.is_unique and f.valid.sum() == 2526
    assert f.qa_age_source_no_support.sum() == 19 and f.qa_population_source_no_support.sum() == 6
    assert f.loc[f.qa_age_source_no_support, ["pop_child", "pop_elderly", "vuln_share"]].isna().all().all()
    assert f.loc[f.qa_population_source_no_support, "population"].isna().all()
    assert f.loc[f.grid_id == "JKT_R050_C061", "pop_child"].iloc[0] == 0
    assert f.f_park_route_missing.sum() == 226 and f.f_lst_low_valid.sum() == 1
    s = pd.read_csv(TABLES / "selection_membership.csv")
    assert len(s) == len(f) and (s.selection_group == "route_missing").sum() == 226
    assert len(pd.read_csv(TABLES / "full_thermal_top_lost.csv")) == 18
    b = pd.read_csv(TABLES / "missing_access_bounds.csv")
    assert b.park_distance_m.isna().any()
    np.testing.assert_allclose((b.m4_upper_fixed_anchors - b.m4_lower_fixed_anchors)[b.park_distance_m.isna()], .25)
    assert (b.best_rank_bound <= b.worst_rank_bound).all()


@pytest.mark.skipif(not HAVE_CANDIDATE, reason="real remediation candidate not yet generated")
def test_real_scenario_membership_recomputes_reported_overlaps():
    table = pd.read_csv(TABLES / "robustness_by_family.csv")
    members = pd.read_csv(TABLES / "joint_scenario_priority_sets.csv")
    f = pd.read_csv(REPO / "data/processed/modeling_remediation/merged_grid.csv")
    for scenario in ("uniform_fractional_auditor_values", "thermal_support_0.25"):
        for mode in table.comparison.unique():
            mem = members.loc[(members.scenario == scenario) & (members.comparison == mode)]
            base = f.loc[f.valid & (f.grid_id.isin(mem.grid_id) if mode.startswith("fixed") else True)]
            rank = M.score_rank(base, C.MODELS["M4"])[1]
            for frac in C.TOP_FRACS:
                a = set(base.loc[rank <= math_ceil(frac * len(base)), C.KEY])
                b = set(mem.loc[mem["rank"] <= math_ceil(frac * len(mem)), C.KEY])
                row = table.loc[(table.scenario == scenario) & (table.comparison == mode) & (table.top_fraction == frac)].iloc[0]
                assert row.retained == len(a & b)
                assert row.jaccard == pytest.approx(len(a & b) / len(a | b))


def math_ceil(x):
    return int(np.ceil(x))


@pytest.mark.skipif(not (REPO / "outputs/remediation/paper/figure_manifest.csv").exists(), reason="figures not generated")
def test_figure_manifest_lists_real_hashed_source_files():
    from jhim.util import sha256
    fm = pd.read_csv(REPO / "outputs/remediation/paper/figure_manifest.csv")
    assert {"figure", "sha256", "source_files", "source_sha256"} <= set(fm.columns)
    for _, row in fm.iterrows():
        assert "\\" not in row.figure and not row.figure.startswith(("/", "D:"))  # portable relative path
        files, hashes = row.source_files.split(";"), row.source_sha256.split(";")
        assert len(files) == len(hashes) >= 1
        for f, h in zip(files, hashes):
            p = REPO / f
            assert p.exists(), f
            assert sha256(p) == h, f"stale source hash {f}"
        assert sha256(REPO / row.figure) == row.sha256


@pytest.mark.skipif(not HAVE_CANDIDATE, reason="real remediation candidate not yet generated")
def test_geographic_cases_balanced_and_reconcile_with_attribution():
    cases = pd.read_csv(TABLES / "geographic_cases.csv")
    att = pd.read_csv(TABLES / "rank_change_attribution.csv")
    assert len(cases) == 8 and cases.grid_id.is_unique
    gains = cases.loc[cases.case_selection == "largest M3->M4 rank gain"]
    losses = cases.loc[cases.case_selection == "largest M3->M4 rank loss"]
    assert len(gains) == len(losses) == 4
    assert gains.rank_gain.min() >= att.rank_gain.nlargest(4).min()
    assert losses.rank_gain.max() <= att.rank_gain.nsmallest(4).max()
    merged = cases.merge(att, on=C.KEY, suffixes=("", "_att"))
    assert (merged.rank_gain == merged.rank_gain_att).all() and (merged.kota == merged.kota_att).all()


def test_replay_helper_rejects_self_comparison_and_ignores_only_build_stamps(monkeypatch, tmp_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("replay", REPO / "scripts/check_agent3_replay.py")
    replay = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(replay)
    assert replay.strip({"built_at": "x", "n": 1, "nested": [{"built_at": "y", "v": 2}]}) == {"n": 1, "nested": [{"v": 2}]}
    assert replay.strip({"permutations": 999}) != replay.strip({"permutations": 9999})
    man = {"built_at": "T1", "implementation": {}, "config": {}, "inputs": {}, "runtime": {}}
    snap = tmp_path / "snap"
    snap.mkdir()
    (snap / "identity.json").write_text(json.dumps({**man, "tables": [], "gis": [], "figure_sha256": {}}), encoding="utf-8")
    monkeypatch.setattr(replay, "SNAPSHOT", snap)
    monkeypatch.setattr(replay, "fresh_manifest", lambda: dict(man))
    with pytest.raises(AssertionError, match="Second run not executed"):
        replay.compare()
    monkeypatch.setattr(replay, "fresh_manifest", lambda: {**man, "built_at": "T2", "runtime": {"permutations": 99}})
    with pytest.raises(AssertionError, match="runtime differs"):
        replay.compare()
