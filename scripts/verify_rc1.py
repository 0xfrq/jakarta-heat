"""Independent RC1 equations, input adoption, spatial arithmetic and output lineage checks."""
import json
import math
import subprocess
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.stats import false_discovery_control

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from jhim import config as C, data as D, pipeline as P
from jhim.provenance import inputs_identity, manifest_status
from jhim.util import sha256, write_json

def check():
    paths, candidate = C.Paths(root=ROOT), C.RemediationPaths(root=ROOT)
    f = pd.read_csv(paths.merged).set_index(C.KEY)
    r = pd.read_csv(candidate.merged).set_index(C.KEY)
    pri = pd.read_csv(paths.priority).set_index(C.KEY)
    rp = pd.read_csv(candidate.priority).set_index(C.KEY)
    support = pd.read_csv(paths.demographic_support).set_index(C.KEY).loc[f.index]
    corrected = pd.read_csv(paths.demographic_corrected).set_index(C.KEY).loc[f.index]
    rs, _ = D.load_remote_sensing(paths)
    rs = rs.set_index(C.KEY).loc[f.index]
    assert len(f) == 2765 and f.index.is_unique
    for col in ("population", "pop_child", "pop_elderly"):
        np.testing.assert_allclose(f[col], corrected[col], equal_nan=True, rtol=0, atol=1e-12)
        np.testing.assert_allclose(r[col], f[col], equal_nan=True, rtol=0, atol=1e-12)
    assert (f.support_version == support.support_version).all()
    assert f.qa_age_source_no_support.equals(support.qa_age_source_no_support)
    assert f.qa_population_source_no_support.equals(support.qa_population_source_no_support)
    assert f.loc[support.qa_age_source_no_support, ["pop_child", "pop_elderly"]].isna().all().all()
    assert f.loc[support.qa_population_source_no_support, "population"].isna().all()
    for col in ("lst_c", "ndvi", "lst_valid_frac"):
        np.testing.assert_allclose(f[col], rs[col], equal_nan=True, rtol=0, atol=1e-12)
        np.testing.assert_allclose(r[col], rs[col], equal_nan=True, rtol=0, atol=1e-12)
    assert f.valid.equals(r.valid)
    v = f.loc[f.valid]
    def norm(x, clip=True):
        lo, hi = x.quantile([.05, .95]) if clip else (x.min(), x.max())
        return ((x-lo)/(hi-lo)).clip(0, 1)
    scores, raw = {}, {}
    for clip, dest in ((True, scores), (False, raw)):
        l, n = norm(v.lst_c, clip), 1-norm(v.ndvi, clip)
        p, a = norm(np.log1p(v.population), clip), norm(np.log1p(v.pop_child+v.pop_elderly), clip)
        d = v.park_distance_m.clip(0, 1000)/1000
        dest.update(m1=l, m2=.6*l+.4*n, m3=.4*l+.3*n+.3*p, m4=.3*l+.2*n+.25*a+.25*d)
    for model in scores:
        for saved in (pri, rp):
            np.testing.assert_allclose(saved.loc[v.index, model+"_score"], scores[model], atol=1e-12, rtol=0)
            assert saved.loc[~f.valid, model+"_score"].isna().all()
            order = np.lexsort((v.index.to_numpy(), -raw[model].to_numpy(), -scores[model].to_numpy()))
            ranks = np.empty(len(v), dtype=int)
            ranks[order] = np.arange(1, len(v)+1)
            np.testing.assert_array_equal(saved.loc[v.index, model+"_rank"], ranks)
            assert saved[model+"_top"].sum() == math.ceil(.1*len(v))
    grid = D.read_grid_gdf(paths.grid).set_index(C.KEY)
    for obj in (paths, candidate):
        geo = gpd.read_file(obj.gis / "priority_models.gpkg").set_index(C.KEY).loc[f.index]
        assert geo.crs.to_epsg() == 32748
        assert geo.geometry.equals(grid.loc[f.index].geometry)
        for model in scores:
            np.testing.assert_allclose(geo[model+"_score"], pri[model+"_score"], atol=1e-12, equal_nan=True)
            np.testing.assert_allclose(geo[model+"_rank"], pri[model+"_rank"], atol=0, equal_nan=True)
    contrib = pd.read_csv(candidate.tables / "component_contributions.csv")
    np.testing.assert_allclose(contrib.sum_delta_terms, contrib.score_delta, atol=1e-12)
    att = pd.read_csv(candidate.tables / "rank_change_attribution.csv")
    np.testing.assert_allclose(att.filter(regex="^shapley_rank_gain_").sum(axis=1), att.rank_gain, atol=1e-10)
    lisa = pd.read_csv(candidate.tables / "lisa_tail_permutation_grid.csv")
    for _, table in lisa.groupby("variant"):
        assert ((false_discovery_control(table.p_sim, method="bh") <= .05) == (table.klaster_fdr != "ns")).all()
        assert ((false_discovery_control(table.p_sim, method="by") <= .05) == (table.klaster_by != "ns")).all()
    edges = pd.read_csv(candidate.tables / "spatial_weight_neighbors.csv")
    y = pri.loc[edges.grid_id.unique(), "m4_score"]
    z = y-y.mean()
    manual = len(y)/edges.weight.sum() * (edges.weight*edges.grid_id.map(z)*edges.neighbor_id.map(z)).sum()/np.square(z).sum()
    gm = pd.read_csv(candidate.tables / "moran_global.csv")
    assert abs(manual-gm.loc[(gm.variabel == "m4_score") & (gm.bobot == "queen"), "I"].iloc[0]) < 1e-12
    registry = pd.read_csv(ROOT / "docs/scenario_registry.csv")
    routes = pd.read_csv(paths.processed / "agent2_route_scenarios.csv")
    for scenario in routes.scenario_id.unique():
        assert ((registry.scenario == "agent2_"+scenario) & (registry.status == "EXECUTED")).any()
    for obj in (paths, candidate):
        man = json.loads(obj.manifest.read_text(encoding="utf-8"))
        assert not manifest_status(obj, man), manifest_status(obj, man)
    assert P.official_outputs_status(paths)["is_current"]
    # Dashboard feature/model caches call these same loader/scoring functions; compare full frames.
    from dashboard.lib.context import _features, _priority, _sig
    df, _, status = _features(False, "exclude", _sig(paths))
    dp = _priority(False, "exclude", _sig(paths)).set_index(C.KEY)
    assert status.can_model
    for model in scores:
        np.testing.assert_allclose(dp[model+"_score"], pri[model+"_score"], equal_nan=True, atol=1e-12)
    original = json.loads((ROOT / "outputs/qa/rc1/original_audit_hashes.json").read_text(encoding="utf-8"))
    for directory, files in original.items():
        for name, expected in files.items():
            assert sha256(Path(directory)/name) == expected, name
    refs = json.loads((ROOT / "outputs/qa/rc1/source_refs.json").read_text())
    for name, expected in refs.items():
        assert subprocess.check_output(["git", "rev-parse", name], text=True).strip() == expected
        if name != "main":
            subprocess.run(["git", "merge-base", "--is-ancestor", expected, "HEAD"], check=True)
    report = {"result": "PASS", "n_master": len(f), "n_common": len(v),
              "no_age_support": int(support.qa_age_source_no_support.sum()),
              "no_population_support": int(support.qa_population_source_no_support.sum()),
              "manual_moran_m4": float(manual), "canonical_inputs": inputs_identity(paths),
              "checks": ["A1 canonical RS adoption", "A2 corrected counts/support adoption", "independent scores/ranks/top sets",
                         "GIS geometry/table identity", "contributions/Shapley", "BH/BY", "manual Moran",
                         "five A2 route scenarios consumed", "dashboard/model equality", "fresh manifests", "immutable original audits and source refs"],
              "boundary": "Engineering verification; scientific closure remains with independent reviewer/coordinator."}
    write_json(ROOT / "outputs/qa/rc1/verification.json", report)
    write_json(ROOT / "docs/integration_manifest.json", {
        "schema_version": "rc1-1", "branch": "integration/rc1",
        "candidate_source_commit": json.loads(paths.manifest.read_text(encoding="utf-8"))["git_commit"],
        "source_refs": refs, "canonical_inputs": inputs_identity(paths),
        "canonical_outputs": {"features": str(paths.merged.relative_to(ROOT)),
                              "priority": str(paths.priority.relative_to(ROOT)),
                              "remediation": str(candidate.modeling.relative_to(ROOT)),
                              "dashboard": "dashboard/app.py"},
        "verification": "outputs/qa/rc1/verification.json", "replay": "outputs/remediation/qa/replay_verification.json",
        "source_of_truth": "Current RC1 inputs supersede historical preintegration statements in agent ledgers.",
        "scientific_status": "Provisional mixed-period candidate-park proxy; independent scientific sign-off pending"})
    print(json.dumps({k:v for k,v in report.items() if k != "canonical_inputs"}, indent=2))

if __name__ == "__main__":
    check()
