"""Matematika perbandingan peringkat dan perlindungan terhadap pencampuran himpunan grid."""
import numpy as np
import pandas as pd
import pytest

from jhim import compare as K
from jhim import config as C
from jhim import models as M


def _pri(scores: dict, valid=None):
    n = len(next(iter(scores.values())))
    df = pd.DataFrame({C.KEY: [f"g{i:02d}" for i in range(n)], "valid": valid if valid is not None else [True] * n})
    v = df.loc[df["valid"]]
    for k, s in scores.items():
        s = pd.Series(s, dtype=float).where(df["valid"])
        df[f"{k}_score"] = s
        r = M.rank_desc(s[df["valid"]], v[C.KEY])
        df[f"{k}_rank"] = r.reindex(df.index).astype("Int64")
        df[f"{k}_top"] = M.top_mask(df[f"{k}_rank"], len(v), 0.2)
        df[f"{k}_class"] = M.priority_class(df[f"{k}_rank"], len(v))
    return df


def test_jaccard():
    assert K.jaccard({1, 2}, {2, 3}) == pytest.approx(1 / 3)
    assert np.isnan(K.jaccard(set(), set()))


def test_identical_and_reversed_rankings():
    x = np.arange(10.0)
    p = _pri({"m1": x, "m2": x * 2 + 1, "m3": -x})
    sp, kt, ja = K.spearman_matrix(p), K.kendall_matrix(p), K.jaccard_matrix(p)
    assert sp.loc["M1", "M2"] == pytest.approx(1.0) and sp.loc["M1", "M3"] == pytest.approx(-1.0)
    assert kt.loc["M1", "M2"] == pytest.approx(1.0) and kt.loc["M1", "M3"] == pytest.approx(-1.0)
    assert ja.loc["M1", "M2"] == 1.0 and ja.loc["M1", "M3"] == 0.0
    mv = K.rank_movement(p).set_index(["model_a", "model_b"])
    assert mv.loc[("M1", "M2"), "mean_abs_shift"] == 0 and mv.loc[("M1", "M3"), "max_abs_shift"] == 9


def test_rank_shift_sign_and_transitions():
    p = _pri({"m1": [10, 9, 8, 7, 6, 5, 4, 3, 2, 1], "m4": [1, 9, 8, 7, 6, 5, 4, 3, 2, 10]})
    sh = K.rank_shift(p, "m1", "m4").set_index(C.KEY)
    assert sh.loc["g09", "shift"] == 9  # dari peringkat 10 ke 1: naik prioritas = positif
    assert sh.loc["g00", "shift"] == -9
    assert sh.loc["g09", "transisi"] == "masuk top di M4" and sh.loc["g00", "transisi"] == "keluar top di M4"
    assert sh.loc["g01", "transisi"] == "tetap top"


def test_transition_matrix_sums_to_n():
    rng = np.random.default_rng(0)
    p = _pri({"m1": rng.random(40), "m4": rng.random(40)})
    t = K.transition_matrix(p, "m1", "m4")
    assert t.to_numpy().sum() == 40 and list(t.index) == list(C.CLASS_LABELS)
    tn = K.transition_matrix(p, "m1", "m4", normalize=True)
    assert np.allclose(tn.sum(axis=1), 1.0)


def test_overlap_table_multiple_cutoffs():
    x = np.arange(20.0)
    p = _pri({"m1": x, "m2": x})
    ov = K.overlap_table(p, fracs=(0.05, 0.1, 0.2))
    assert ov["jaccard"].eq(1.0).all() and ov["n_top"].tolist() == [1, 2, 4]


def test_metrics_only_on_valid_and_refuse_mixed_sets():
    valid = [True] * 8 + [False] * 2
    p = _pri({"m1": np.arange(10.0), "m2": np.arange(10.0)[::-1]}, valid=valid)
    assert K.spearman_matrix(p).loc["M1", "M2"] == pytest.approx(-1.0)
    p.loc[0, "m2_score"] = np.nan  # satu model kehilangan grid -> himpunan berbeda
    with pytest.raises(ValueError, match="tidak sama"):
        K.spearman_matrix(p)


def test_full_comparison_suite(feat_full):
    pri = M.build_priority_table(feat_full)
    long = K.pairwise_long(pri)
    assert set(long["metrik"]) >= {"spearman_skor", "kendall_tau_b", "jaccard_top"}
    assert long["n_valid"].eq(int(feat_full["valid"].sum())).all()
    ks = K.kota_summary(pri, feat_full)
    for m, g in ks.groupby("model"):
        assert g["n_top"].sum() == int(pri[f"{m.lower()}_top"].sum())
    cov = K.top_coverage(pri, feat_full)
    assert cov.iloc[-1]["kelompok"] == "Semua grid valid" and cov.iloc[-1]["pct_populasi_valid"] == pytest.approx(100)
    hv = K.heat_vs_aware(pri, feat_full)
    assert set(hv["transisi"]) <= {"tetap top", "masuk top di M4", "keluar top di M4"}
    ss = K.score_summary(pri)
    assert len(ss) == 4 and (ss["max"] <= 1).all()


def test_eligibility_effect_counts_route_missing(feat_full):
    e = K.eligibility_effect(feat_full).iloc[0]
    assert e["n_elig_m1"] == 80 and e["n_common_valid"] == 77
    assert e["n_top_m1_full_outside_common"] == e["of_which_park_route_missing"]


def test_retop_changes_cutoff():
    p = _pri({"m1": np.arange(20.0)})
    assert int(K.retop(p, 0.5)["m1_top"].sum()) == 10
