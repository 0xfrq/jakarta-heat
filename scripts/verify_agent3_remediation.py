"""Independent arithmetic/ID/export checks; does not call analytical scoring helpers."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from jhim.util import write_json, sha256


def check():
    tables = ROOT / "outputs/remediation/tables"
    inputs = ROOT / "data/processed/remediation_inputs"
    merged = pd.read_csv(ROOT / "data/processed/modeling_remediation/merged_grid.csv")
    pri = pd.read_csv(ROOT / "data/processed/modeling_remediation/priority_models.csv")
    original = pd.read_csv(inputs / "audited_merged_grid.csv")
    assert len(merged) == 2765 and merged.grid_id.is_unique and original.grid_id.equals(merged.grid_id)
    assert merged.valid.sum() == 2526 and original.valid.sum() == 2538
    assert merged.qa_age_source_no_support.sum() == 19 and merged.qa_population_source_no_support.sum() == 6
    assert merged.loc[merged.qa_age_source_no_support, ["pop_child", "pop_elderly", "pop_vulnerable", "vuln_share"]].isna().all().all()
    np.testing.assert_allclose(merged.park_distance_m, original.park_distance_m, equal_nan=True)
    for c in ("lst_c", "ndvi", "lst_valid_frac"):
        np.testing.assert_allclose(merged[c], original[c], atol=0, rtol=0, equal_nan=True)
    assert merged.f_park_route_missing.sum() == 226 and merged.f_lst_low_valid.sum() == 1
    v = merged.loc[merged.valid]
    def n(x):
        return ((x - x.quantile(.05)) / (x.quantile(.95) - x.quantile(.05))).clip(0, 1)
    l, nd, p, a, d = n(v.lst_c), 1 - n(v.ndvi), n(np.log1p(v.population)), n(np.log1p(v.pop_child + v.pop_elderly)), v.park_distance_m.clip(0, 1000) / 1000
    formula = {"m1": l, "m2": .6 * l + .4 * nd, "m3": .4 * l + .3 * nd + .3 * p,
               "m4": .3 * l + .2 * nd + .25 * a + .25 * d}
    for model, score in formula.items():
        np.testing.assert_allclose(pri.loc[pri.valid, f"{model}_score"], score, atol=1e-12, rtol=0)
        assert pri.loc[~pri.valid, f"{model}_score"].isna().all()
        assert pri[f"{model}_top"].sum() == 253
    contributions = pd.read_csv(tables / "component_contributions.csv")
    err = float(np.max(np.abs(contributions.sum_delta_terms - contributions.score_delta)))
    assert err < 1e-10
    att = pd.read_csv(tables / "rank_change_attribution.csv")
    shap_error = float(np.max(np.abs(att.filter(regex="^shapley_rank_gain_").sum(axis=1) - att.rank_gain)))
    assert shap_error < 1e-10
    import geopandas as gpd
    gis = gpd.read_file(ROOT / "outputs/remediation/gis/priority_models.gpkg")
    joint = pri.merge(gis.drop(columns="geometry"), on="grid_id", suffixes=("_csv", "_gis"), validate="one_to_one")
    assert len(joint) == 2765
    for model in formula:
        np.testing.assert_allclose(joint[f"{model}_score_csv"], joint[f"{model}_score_gis"], equal_nan=True, atol=1e-12)
        np.testing.assert_allclose(joint[f"{model}_rank_csv"], joint[f"{model}_rank_gis"], equal_nan=True, atol=0)
    # Independent BH through SciPy, plus matrix-form Moran I from saved neighbor IDs.
    from scipy.stats import false_discovery_control
    lisa = pd.read_csv(tables / "lisa_tail_permutation_grid.csv")
    for _, t in lisa.groupby("variant"):
        assert ((false_discovery_control(t.p_sim.to_numpy(), method="bh") <= .05) == (t.klaster_fdr != "ns")).all()
        assert ((false_discovery_control(t.p_sim.to_numpy(), method="by") <= .05) == (t.klaster_by != "ns")).all()
        assert (t.p_sim > 0).all()
    neighbors = pd.read_csv(tables / "spatial_weight_neighbors.csv")
    y = pri.set_index("grid_id").loc[neighbors.grid_id.unique(), "m4_score"]
    z = y - y.mean()
    term = neighbors.weight.to_numpy() * neighbors.grid_id.map(z).to_numpy() * neighbors.neighbor_id.map(z).to_numpy()
    manual_i = len(y) / neighbors.weight.sum() * term.sum() / np.square(z).sum()
    gm = pd.read_csv(tables / "moran_global.csv")
    saved_i = gm.loc[(gm.variabel == "m4_score") & (gm.bobot == "queen"), "I"].iloc[0]
    assert abs(manual_i - saved_i) < 1e-12
    identity = json.loads((inputs / "input_lineage.json").read_text(encoding="utf-8"))
    for entry in identity["source_files"]:
        assert sha256(entry["copy"]) == entry["sha256"]
    # Baseline files remain exactly the original bytes, not just equivalent scores.
    for name, target in (("audited_merged_grid.csv", ROOT / "data/processed/modeling/merged_grid.csv"),
                         ("audited_priority_models.csv", ROOT / "data/processed/modeling/priority_models.csv"),
                         ("spatial_features.csv", ROOT / "data/processed/spatial_features.csv")):
        assert sha256(inputs / name) == sha256(target)
    report = {"result": "PASS within local frozen candidate", "n_master": len(merged), "n_common": int(merged.valid.sum()),
              "max_score_decomposition_error": err, "max_rank_attribution_error": shap_error,
              "manual_moran_m4": float(manual_i), "checks": ["support null propagation", "all four independent equations",
               "contribution sums", "Shapley efficiency", "GIS/table scores and ranks", "independent BH/BY", "manual Moran I",
               "preserved raw walking/RS", "frozen input hashes", "baseline byte preservation"],
              "boundary": "No consolidated integration or scientific sign-off is implied."}
    write_json(ROOT / "outputs/remediation/qa/independent_verification.json", report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    check()
