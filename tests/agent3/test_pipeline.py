"""Pipeline end-to-end pada fixture: penolakan tanpa RS, keluaran resmi, manifest, kode keluar CLI."""
import json
import os
import subprocess
import sys

import pandas as pd
import pytest
from conftest import REPO

from jhim import config as C
from jhim import pipeline as P
from jhim.util import PendingInputs


def test_p2_only_refuses_official_outputs(root_p2):
    with pytest.raises(PendingInputs):
        P.run_all(root_p2, perms=9, skip_figures=True)
    assert not root_p2.priority.exists() and not root_p2.merged.exists()
    assert not root_p2.tables.exists()


def test_p2_diagnostics_written_to_qa(root_p2):
    out = P.step_p2_diagnostics(root_p2, perms=9)
    for f in ("person2_quality.csv", "person2_kota_summary.csv", "person2_component_spearman.csv",
              "person2_flagged_grids.csv", "person2_moran_global.csv", "person2_diagnostics_info.json"):
        assert (root_p2.qa / f).exists(), f
    assert out["status"]["state"] == "P2_ONLY"
    k = pd.read_csv(root_p2.qa / "person2_kota_summary.csv")
    assert k["n_grid"].sum() == 80 and k["n_rute_tidak_dihitung"].sum() == 3


def test_full_pipeline_writes_outputs_and_manifest(root_full):
    man = P.run_all(root_full, perms=19, formats=("png",), dpi=40)
    assert man["input_status"] == "COMPLETE" and man["source"] == "real"
    assert man["inputs"]["remote_sensing"]["sha256"] and man["config"]["models"] == C.MODELS
    assert man["runtime"]["permutations"] == 19
    pri = pd.read_csv(root_full.priority)
    assert len(pri) == 80 and int(pri["valid"].sum()) == 77
    for f in ("model_comparison.csv", "kendall_matrix.csv", "top_overlap.csv", "transition_m1_m4.csv",
              "kota_summary.csv", "moran_global.csv", "lisa_cluster_counts.csv", "sensitivity_m4_summary.csv",
              "eligibility_effect_m1.csv"):
        assert (root_full.tables / f).exists(), f
    assert (root_full.figures / "fig_map_scores_m1_m4.png").exists()
    assert (root_full.gis / "priority_models.gpkg").exists()
    st = P.official_outputs_status(root_full)
    assert st["exists"] and st["stale_inputs"] == []
    # masukan berubah -> keluaran ditandai usang
    rs = pd.read_csv(root_full.rs)
    rs.loc[0, "lst_c"] += 1
    rs.to_csv(root_full.rs, index=False)
    assert "remote_sensing" in P.official_outputs_status(root_full)["stale_inputs"]


def test_low_valid_share_requires_force(tmp_path):
    from conftest import grid_ids, rs_frame, write_root

    rs = rs_frame(grid_ids())
    rs.loc[:40, "lst_c"] = None
    paths = write_root(tmp_path, rs=rs)
    with pytest.raises(Exception, match="--force"):
        P.step_merge(paths)
    feat, meta = P.step_merge(paths, force=True)
    assert meta["valid_share"] < C.MIN_VALID_SHARE


def _cli(root, *args):
    env = {**os.environ, "JHIM_ROOT": str(root), "PYTHONIOENCODING": "utf-8"}
    return subprocess.run([sys.executable, str(REPO / "scripts/run_agent3_pipeline.py"), *args],
                          capture_output=True, text=True, env=env, timeout=600)


def test_cli_exit_codes(root_p2):
    r = _cli(root_p2.root, "--status")
    assert r.returncode == 0 and "P2_ONLY" in r.stdout
    r = _cli(root_p2.root, "--skip-figures", "--perms", "9")
    assert r.returncode == 2 and "TERTUNDA" in r.stderr
    r = _cli(root_p2.root, "--p2-only", "--perms", "9")
    assert r.returncode == 0
    man = json.loads((root_p2.root / "outputs/qa/agent3/run_manifest.json").read_text(encoding="utf-8"))
    assert man["input_status"] == "P2_ONLY"
    assert man["runtime"]["permutations"] == 9


def test_cli_invalid_exit_code(root_p2):
    root_p2.spatial_features.unlink()
    r = _cli(root_p2.root, "--status")
    assert r.returncode == 1 and "GALAT" in r.stdout
