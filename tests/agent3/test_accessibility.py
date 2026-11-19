"""Jarak taman: NaN = rute tidak dihitung (bukan 0, bukan tak hingga); imputasi hanya di kolom terpisah."""
import numpy as np
import pandas as pd
import pytest

from jhim import config as C
from jhim import data as D
from jhim import models as M

ROUTE_MISSING = [7, 11, 13]


def _merged(root):
    grid = D.read_grid_table(root.grid)
    pop, _ = D.load_population_inputs(root)
    rs, _ = D.load_remote_sensing(root)
    out, _, _ = D.merge_inputs(grid[C.KEY], rs, pop, D.load_master_attrs(root))
    return out


@pytest.mark.parametrize("policy", ["exclude", "worst", "median", "cap"])
def test_raw_distance_never_overwritten(root_full, policy):
    f = D.clean_values(_merged(root_full), policy)
    assert f.loc[ROUTE_MISSING, "park_distance_m"].isna().all()
    assert f.loc[ROUTE_MISSING, "f_park_route_missing"].all()
    assert int(f["f_park_route_missing"].sum()) == 3


def test_exclude_policy_drops_from_common_set(root_full):
    f = D.clean_values(_merged(root_full), "exclude")
    assert not f.loc[ROUTE_MISSING, "valid"].any()
    assert f.loc[ROUTE_MISSING, "park_distance_used_m"].isna().all()
    assert not f["f_park_imputed"].any()
    # model panas murni tetap layak untuk grid tsb (dipakai diagnostik efek kelayakan)
    assert f.loc[ROUTE_MISSING, "elig_m1"].all()


def test_worst_policy_is_max_deficit_and_flagged(root_full):
    f = D.clean_values(_merged(root_full), "worst")
    assert (f.loc[ROUTE_MISSING, "park_distance_used_m"] == C.PARK_CAP_M).all()
    assert f.loc[ROUTE_MISSING, "f_park_imputed"].all() and f.loc[ROUTE_MISSING, "valid"].all()
    comp = M.components(f.loc[f["valid"]])
    assert (comp.loc[ROUTE_MISSING, "park_deficit"] == 1.0).all()


def test_median_policy_uses_observed_median(root_full):
    m = _merged(root_full)
    f = D.clean_values(m, "median")
    med = pd.to_numeric(m["park_distance_m"]).median()
    assert np.allclose(f.loc[ROUTE_MISSING, "park_distance_used_m"], med)


def test_true_zero_distance_is_not_missing(root_full):
    f = D.clean_values(_merged(root_full), "exclude")
    assert f.loc[5, "park_distance_m"] == 0.0 and not f.loc[5, "f_park_route_missing"]
    assert f.loc[5, "valid"]
    assert M.components(f.loc[f["valid"]]).loc[5, "park_deficit"] == 0.0


def test_unknown_policy_rejected(root_full):
    with pytest.raises(ValueError):
        D.clean_values(_merged(root_full), "zero")


def test_snap_and_coverage_flags(root_full):
    f = D.clean_values(_merged(root_full))
    assert f.loc[[2, 9], "f_snap_far"].all() and int(f["f_snap_far"].sum()) == 2
    assert f.loc[[2, 9], "valid"].all()  # ditandai untuk QA, tidak dikeluarkan diam-diam


def test_reachable_mismatch_detected(root_full):
    m = _merged(root_full)
    m.loc[0, "park_reachable"] = 0  # klaim tidak terjangkau padahal jarak ada
    f = D.clean_values(m)
    assert f.loc[0, "f_reach_mismatch"] and int(f["f_reach_mismatch"].sum()) == 1


def test_access_flag_inconsistency_detected(root_full):
    m = _merged(root_full)
    i = int(m["park_distance_m"].idxmax())
    m.loc[i, "park_access_500m"] = 1
    f = D.clean_values(m)
    assert f.loc[i, "f_park_access_500m_mismatch"]


def test_park_deficit_binary_and_capped():
    df = pd.DataFrame({C.KEY: list("abcd"), "lst_c": 30.0, "ndvi": 0.3, "population": 10.0, "pop_child": 1.0,
                       "pop_elderly": 1.0, "park_distance_m": [0.0, 499.0, 501.0, 5000.0]})
    cont = M.components(df)["park_deficit"].tolist()
    assert cont == [0.0, 0.499, 0.501, 1.0]
    binr = M.components(df, park_mode="binary", park_thr=500)["park_deficit"].tolist()
    assert binr == [0.0, 0.0, 1.0, 1.0]
