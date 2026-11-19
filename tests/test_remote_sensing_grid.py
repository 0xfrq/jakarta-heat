"""Contract tests for the Person 1 / Agent 1 remote-sensing deliverable.

Run from the repository root:  python -m pytest tests/test_remote_sensing_grid.py -q
Requires: pandas, numpy (geopandas/rasterio not needed for these tests).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
RS = PROC / "remote_sensing_grid.csv"
META = PROC / "remote_sensing_grid.meta.json"
KEY = "grid_id"

CONTRACT = ["grid_id", "lst_mean_c", "ndvi_mean", "tree_fraction", "grass_fraction", "built_fraction",
            "lst_valid_fraction", "lst_observation_count"]


@pytest.fixture(scope="module")
def rs() -> pd.DataFrame:
    if not RS.exists():
        pytest.skip("remote_sensing_grid.csv not built; run scripts/02b_aggregate_remote_sensing.py")
    return pd.read_csv(RS, dtype={KEY: "string"})


@pytest.fixture(scope="module")
def master() -> pd.DataFrame:
    return pd.read_csv(PROC / "grid_master.csv", dtype={KEY: "string"})


def test_contract_columns(rs):
    assert rs.columns[: len(CONTRACT)].tolist() == CONTRACT
    assert {"lst_c", "ndvi"} <= set(rs.columns)  # compatibility aliases for jhim/dashboard


def test_one_row_per_master_grid(rs, master):
    assert len(rs) == len(master) == 2765
    assert not rs[KEY].duplicated().any()
    assert rs[KEY].tolist() == master[KEY].tolist()  # same IDs, same order


def test_grid_id_schema(rs):
    assert rs[KEY].str.fullmatch(r"JKT_R\d{3}_C\d{3}").all()


def test_join_with_spatial_features_is_one_to_one(rs):
    sp = pd.read_csv(PROC / "spatial_features.csv", dtype={KEY: "string"})
    j = sp.merge(rs, on=KEY, how="inner", validate="one_to_one")
    assert len(j) == len(sp) == len(rs)


def test_lst_units_and_range(rs):
    lst = rs["lst_mean_c"].dropna()
    assert lst.between(15, 60).all(), "LST outside plausible Celsius range: Kelvin / DN / double scaling?"
    assert 30 < lst.median() < 50
    assert (rs["lst_min_c"] <= rs["lst_mean_c"] + 1e-6).all()
    assert (rs["lst_mean_c"] <= rs["lst_max_c"] + 1e-6).all()
    assert (rs["lst_mean_c"].dropna() != 0).all()


def test_ndvi_range(rs):
    assert rs["ndvi_mean"].dropna().between(-1, 1).all()


@pytest.mark.parametrize("col", ["tree_fraction", "grass_fraction", "built_fraction", "lst_valid_fraction",
                                 "ndvi_valid_fraction", "landsat_footprint_fraction", "dw_valid_fraction",
                                 "tree_prob_mean", "built_prob_mean"])
def test_fractions_in_unit_interval(rs, col):
    assert rs[col].dropna().between(0, 1).all()


def test_aliases_identical(rs):
    assert rs["lst_c"].equals(rs["lst_mean_c"])
    assert rs["ndvi"].equals(rs["ndvi_mean"])


def test_missing_lst_only_where_no_valid_pixels(rs):
    miss = rs["lst_mean_c"].isna()
    assert (rs.loc[miss, "lst_valid_fraction"].fillna(0) == 0).all()
    assert (rs.loc[~miss, "lst_valid_fraction"] > 0).all()


def test_dw_fractions_never_zero_filled_placeholders(rs, ):
    meta = json.loads(META.read_text(encoding="utf-8"))
    status = meta["notes"]["dw_fraction_status"]
    cols = ["tree_fraction", "grass_fraction", "built_fraction"]
    if status.startswith("BLOCKED"):
        assert rs[cols].isna().all().all()
    else:
        ok = rs["tree_fraction"].notna()
        s = rs.loc[ok, ["water_fraction", "tree_fraction", "grass_fraction", "flooded_vegetation_fraction",
                        "crops_fraction", "shrub_fraction", "built_fraction", "bare_fraction"]].sum(axis=1)
        assert np.allclose(s, 1, atol=0.02)


def test_physical_consistency(rs):
    # surface temperature should fall with vegetation and rise with built-up probability
    assert rs["lst_mean_c"].corr(rs["ndvi_mean"]) < -0.3
    assert rs["lst_mean_c"].corr(rs["built_prob_mean"]) > 0.3
    assert rs["ndvi_mean"].corr(rs["tree_prob_mean"]) > 0.3


def test_metadata_records_period_and_reducers():
    meta = json.loads(META.read_text(encoding="utf-8"))
    assert meta["period"] == {"start": "2024-01-01", "end_exclusive": "2025-01-01"}
    assert "median" in meta["temporal_reducer"]["landsat"]
    assert "coverage-weighted" in meta["spatial_reducer"]
    assert meta["inputs"]["landsat"]["crs"] == "EPSG:32748"
    assert meta["summary"]["n_rows"] == 2765


def test_gee_script_uses_official_collection2_scaling():
    js = (ROOT / "scripts" / "02_remote_sensing_gee.js").read_text(encoding="utf-8")
    assert "LANDSAT/LC09/C02/T1_L2" in js
    assert re.search(r"ST_B10'\)\s*\.multiply\(0\.00341802\)\.add\(149\.0\)\.subtract\(273\.15\)", js)
    assert js.count("multiply(0.0000275).add(-0.2)") == 2  # SR_B4 and SR_B5, scaled once each
    assert "bitwiseAnd(63)" in js  # QA_PIXEL bits 0-5: fill, dilated cloud, cirrus, cloud, shadow, snow
    assert "'L2SP'" in js
    assert "START = YEAR + '-01-01'" in js and "END = (YEAR + 1) + '-01-01'" in js


def test_jhim_loader_accepts_output():
    sys.path.insert(0, str(ROOT))
    try:
        from jhim import config as C
        from jhim import data as D
    except Exception as exc:  # pragma: no cover - Agent 3 code may move
        pytest.skip(f"jhim not importable: {exc}")
    df = D.read_input_csv(RS, C.RS_COLS, "remote_sensing_grid.csv")
    assert len(df) == 2765
