"""Regression checks for the canonical A1/A2 -> A3 and dashboard integration boundary."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from jhim import config as C, data as D

def test_canonical_corrected_demographics_and_rs_are_consumed(monkeypatch):
    for key in ("JHIM_INPUT_DIR", "JHIM_RS_PATH", "JHIM_DEMOGRAPHIC_SUPPORT", "JHIM_DEMOGRAPHIC_CORRECTED"):
        monkeypatch.delenv(key, raising=False)
    paths = C.Paths(root=ROOT)
    assert paths.rs == ROOT / "data/processed/remote_sensing_remediated/remote_sensing_grid.csv"
    f, _, st = D.load_features(paths)
    assert st.can_model
    expected = pd.read_csv(paths.demographic_corrected).set_index(C.KEY).loc[f.grid_id]
    for col in ("population", "pop_child", "pop_elderly"):
        np.testing.assert_allclose(f[col], expected[col], equal_nan=True, atol=1e-12)
        assert f"raw_{col}" in f and f"{col}_raw" in f
    assert f.support_version.eq("agent2-DM-01-v1-buffered-age").all()
    assert f.qa_age_source_no_support.sum() == f.qa_population_source_no_support.sum() == 6
    old = pd.read_csv(ROOT / "data/processed/remediation_inputs/demographic_support.csv").set_index(C.KEY)
    recovered = set(old.loc[old.qa_age_source_no_support].index) - set(f.loc[f.qa_age_source_no_support, C.KEY])
    assert len(recovered) == 13
    assert f.set_index(C.KEY).loc[list(recovered), ["pop_child", "pop_elderly"]].notna().all().all()

def test_demo_never_uses_real_demographic_overrides(monkeypatch):
    monkeypatch.setenv("JHIM_DEMOGRAPHIC_SUPPORT", str(ROOT / "data/processed/demographic_support.csv"))
    monkeypatch.setenv("JHIM_DEMOGRAPHIC_CORRECTED", str(ROOT / "data/processed/demographic_features_corrected.csv"))
    paths = C.Paths(root=ROOT, demo=True)
    assert paths.demographic_support.parent.name == "dummy"
    assert paths.demographic_corrected.parent.name == "dummy"
