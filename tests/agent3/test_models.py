"""Normalisasi, arah skor, bobot, kelayakan bersama, peringkat deterministik, kelas."""
import math

import numpy as np
import pandas as pd
import pytest

from jhim import config as C
from jhim import models as M


def test_norm01_minmax_clip_constant_and_nan():
    x = pd.Series([0.0, 1.0, 2.0, 3.0, np.nan])
    assert M.norm01(x, clip=None).tolist()[:4] == [0.0, 1 / 3, 2 / 3, 1.0]
    assert np.isnan(M.norm01(x, clip=None).iloc[4])
    assert (M.norm01(pd.Series([5.0, 5.0]), clip=None) == 0.5).all()
    big = pd.Series(np.arange(101, dtype=float))
    c = M.norm01(big, clip=(0.05, 0.95))
    assert c.iloc[0] == 0.0 and c.iloc[100] == 1.0 and c.between(0, 1).all()


def test_norm01_rank_method():
    r = M.norm01(pd.Series([10.0, 30.0, 20.0]), method="rank")
    assert r.tolist() == [0.0, 1.0, 0.5]
    with pytest.raises(ValueError):
        M.norm01(pd.Series([1.0, 2.0]), method="zscore")


def test_component_directions(feat_full):
    v = feat_full.loc[feat_full["valid"]]
    c = M.components(v, clip=None)
    assert c["lst"].corr(v["lst_c"], method="spearman") > 0.99
    assert c["ndvi_low"].corr(v["ndvi"], method="spearman") < -0.99
    assert c["pop"].corr(v["population"], method="spearman") > 0.99
    order = v["park_distance_m"].sort_values().index
    assert c.loc[order, "park_deficit"].is_monotonic_increasing  # jenuh = 1 pada >= 1000 m
    assert c.apply(lambda s: s.dropna().between(0, 1).all()).all()
    assert c["vuln_share"].isna().equals(v["population"].eq(0))


def test_configured_weights_sum_to_one_and_reference_known_components():
    known = {"lst", "ndvi_low", "pop", "pop_density", "vuln", "vuln_share", "park_deficit", "trees_low"}
    for m, w in C.MODELS.items():
        assert math.isclose(sum(w.values()), 1.0), m
        assert set(w) <= known
    assert C.MODELS["M1"] == {"lst": 1.0}
    assert "pop" not in C.MODELS["M4"]  # M4 memakai penduduk rentan, bukan total populasi (hindari double counting)


def test_invalid_weights_rejected():
    for w in ({}, {"lst": -1.0}, {"lst": 0.0}, {"lst": float("nan")}):
        with pytest.raises(ValueError):
            M.normalize_weights(w)
    assert M.normalize_weights({"a": 2.0, "b": 2.0}) == {"a": 0.5, "b": 0.5}


def test_m1_rank_follows_lst(feat_full):
    v = feat_full.loc[feat_full["valid"]]
    _, r = M.score_rank(v, C.MODELS["M1"], clip=None)
    assert r.loc[v["lst_c"].idxmax()] == 1 and r.loc[v["lst_c"].idxmin()] == len(v)


def test_ranking_is_deterministic_under_row_shuffle(feat_full):
    v = feat_full.loc[feat_full["valid"]]
    _, r1 = M.score_rank(v, C.MODELS["M4"])
    sh = v.sample(frac=1, random_state=3)
    _, r2 = M.score_rank(sh, C.MODELS["M4"])
    a = pd.Series(r1.to_numpy(), index=v[C.KEY].to_numpy())
    b = pd.Series(r2.to_numpy(), index=sh[C.KEY].to_numpy())
    assert a.sort_index().equals(b.sort_index())
    assert sorted(r1) == list(range(1, len(v) + 1))  # peringkat unik 1..n


def test_ties_broken_by_secondary_then_grid_id():
    s = pd.Series([1.0, 1.0, 1.0, 0.5])
    r = M.rank_desc(s, pd.Series(["c", "a", "b", "d"]))
    assert r.tolist() == [3, 1, 2, 4]
    r2 = M.rank_desc(s, pd.Series(["c", "a", "b", "d"]), secondary=pd.Series([0.9, 0.1, 0.5, 0.0]))
    assert r2.tolist() == [1, 3, 2, 4]
    with pytest.raises(ValueError):
        M.rank_desc(pd.Series([1.0, np.nan]), pd.Series(["a", "b"]))


def test_build_priority_table_common_set(feat_full):
    pri = M.build_priority_table(feat_full)
    nv = int(feat_full["valid"].sum())
    assert len(pri) == len(feat_full) and int(pri["valid"].sum()) == nv
    for k in ("m1", "m2", "m3", "m4"):
        sc = pri[f"{k}_score"]
        assert sc[pri["valid"]].notna().all() and sc[~pri["valid"]].isna().all()
        assert int(pri[f"{k}_top"].sum()) == math.ceil(0.10 * nv)
        assert pri.loc[pri["valid"], f"{k}_class"].notna().all()
    assert pri.loc[pri["valid"], "m1_score"].between(0, 1).all()


def test_no_valid_cells_raises(root_p2):
    from jhim import data as D

    feat, _, _ = D.load_features(root_p2)
    with pytest.raises(ValueError, match="Tidak ada grid valid"):
        M.build_priority_table(feat)


def test_priority_class_boundaries():
    rank = pd.Series(range(1, 21))
    cls = M.priority_class(rank, 20)
    counts = cls.value_counts().reindex(C.CLASS_LABELS).tolist()
    assert counts == [2, 3, 5, 10]  # 10%, 25%, 50%, 100% dari 20
    assert M.priority_class(pd.Series([pd.NA], dtype="Int64"), 20).isna().all()


def test_n_top_and_top_mask():
    assert M.n_top(2539, 0.10) == 254 and M.n_top(0) == 0
    with pytest.raises(ValueError):
        M.n_top(10, 0)


def test_population_density_and_vuln_share_components(feat_full):
    v = feat_full.loc[feat_full["valid"]]
    c = M.components(v)
    assert {"pop_density", "vuln_share"} <= set(c.columns)
    zero = v["population"] == 0
    assert c.loc[zero, "vuln_share"].isna().all()  # composition has no zero denominator
    assert c.loc[~zero, "vuln_share"].notna().all()


def test_component_correlations_runs_without_rs(root_p2):
    from jhim import data as D

    feat, _, _ = D.load_features(root_p2)
    corr = M.component_correlations(feat)
    assert "lst" not in corr.columns and corr.loc["pop", "vuln"] > 0.9
