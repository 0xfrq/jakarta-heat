"""Bobot spasial, islands, Moran global/lokal, FDR, determinisme permutasi."""
import numpy as np
import pandas as pd
import pytest
from conftest import NC, NR, make_grid_gdf

from jhim import config as C
from jhim import spatial as SP

pytest.importorskip("libpysal")
pytest.importorskip("esda")


def test_bh_fdr_known_example():
    p = np.array([0.01, 0.04, 0.03, 0.005, np.nan])
    # urut: 0.005, 0.01, 0.03, 0.04 ; batas q*k/m = .0125, .025, .0375, .05 -> semua lolos
    assert SP.bh_fdr(p, 0.05).tolist() == [True, True, True, True, False]
    assert SP.bh_fdr(np.array([0.04, 0.9]), 0.05).tolist() == [False, False]  # 0.04 > 0.025


def test_bh_fdr_step_up():
    p = np.array([0.02, 0.9])
    # m=2: batas k=1 -> 0.025; 0.02 <= 0.025 -> ditolak
    assert SP.bh_fdr(p, 0.05).tolist() == [True, False]


def test_lisa_labels():
    assert SP.lisa_labels([1, 2, 3, 4], [0.01, 0.2, 0.01, 0.04]) == ["HH", "ns", "LL", "HL"]
    assert SP.lisa_labels([1, 3], [0.01, 0.01], reject=[False, True]) == ["ns", "LL"]


def test_lattice_neighbor_counts():
    ids = [f"JKT_R{r:03d}_C{c:03d}" for r in range(3) for c in range(3)]
    q = SP.lattice_neighbors(ids, "queen")
    r = SP.lattice_neighbors(ids, "rook")
    assert len(q[0]) == 3 and len(q[1]) == 5 and len(q[4]) == 8
    assert len(r[0]) == 2 and len(r[4]) == 4
    with pytest.raises(ValueError):
        SP.parse_rc("bad-id")


def test_fast_queen_matches_libpysal_and_lattice():
    g = make_grid_gdf()
    fast = SP.build_weights(g, "queen")
    lib = SP.build_weights(g, "queen_libpysal")
    lat = SP.build_weights(g, "lattice_queen")
    for i in range(len(g)):
        assert set(fast.neighbors[i]) == set(lib.neighbors[i]) == set(lat.neighbors[i])
    rook = SP.build_weights(g, "rook")
    assert rook.mean_neighbors < fast.mean_neighbors
    assert SP.build_weights(g, "knn8").mean_neighbors == 8


def test_islands_are_dropped_and_reported():
    g = make_grid_gdf(isolated=True)
    w, used, dropped = SP.prepare_weights(g, "queen")
    assert dropped == ["JKT_R050_C050"] and len(used) == NR * NC and not w.islands
    assert w.transform.upper() == "R"
    assert np.allclose([sum(v) for v in w.weights.values()], 1.0)  # baris-standar


def _surface(kind):
    g = make_grid_gdf()
    rc = np.array([SP.parse_rc(i) for i in g[C.KEY]])
    if kind == "gradient":
        y = rc[:, 1] + 0.1 * rc[:, 0]
    else:  # papan catur
        y = ((rc[:, 0] + rc[:, 1]) % 2).astype(float)
    return g.assign(y=y)


def test_global_moran_signs_and_determinism():
    g = _surface("gradient")
    w, used, _ = SP.prepare_weights(g, "queen")
    a = SP.global_moran(used["y"], w, 99, seed=7)
    b = SP.global_moran(used["y"], w, 99, seed=7)
    assert a == b and a["I"] > 0.8 and a["p_sim"] == pytest.approx(0.01)
    wr, used_r, _ = SP.prepare_weights(_surface("checker"), "rook")
    c = SP.global_moran(used_r["y"], wr, 99)
    assert c["I"] < -0.9


def test_moran_rejects_nan():
    g = _surface("gradient")
    w, used, _ = SP.prepare_weights(g, "queen")
    y = used["y"].to_numpy().copy()
    y[0] = np.nan
    with pytest.raises(ValueError):
        SP.global_moran(y, w, 9)


def test_local_moran_deterministic_and_fdr_subset():
    g = _surface("gradient")
    a, dropped = SP.lisa_for(g, "y", "queen", permutations=99, seed=3)
    b, _ = SP.lisa_for(g, "y", "queen", permutations=99, seed=3)
    pd.testing.assert_frame_equal(a, b)
    assert not dropped and len(a) == NR * NC
    sig_raw = a["klaster_p05"] != "ns"
    sig_fdr = a["klaster_fdr"] != "ns"
    assert (sig_fdr <= sig_raw).all()  # FDR tidak pernah menambah grid signifikan
    assert set(a["klaster_p05"]) <= {"HH", "LL", "HL", "LH", "ns"}


def test_moran_table_skips_missing_values():
    g = _surface("gradient")
    g.loc[:4, "y"] = np.nan
    t = SP.moran_table(g, ["y"], ("queen", "rook"), permutations=9)
    assert len(t) == 2 and (t["n"] == NR * NC - 5).all()
