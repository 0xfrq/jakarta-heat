"""Modul sensitivitas: skenario yang relevan, himpunan grid yang berubah dilaporkan, metrik dalam rentang."""
import pytest

from jhim import config as C
from jhim import sensitivity as SE


def test_m4_scenarios_cover_required_questions(feat_full):
    summ, stab, info = SE.run_sensitivity(feat_full, "M4")
    groups = set(summ["kelompok"])
    assert {"bobot", "normalisasi", "ambang taman", "jarak taman kosong", "penduduk", "eksklusi QA",
            "tutupan lahan"} <= groups
    assert (summ["jenis"] == "eksploratif").all()
    for c in ("jaccard_top5", "jaccard_top10", "jaccard_top20", "spearman_vs_baseline"):
        assert summ[c].dropna().between(-1, 1).all()
    assert stab["stable_share"].between(0, 1).all()
    assert info["n_top"] == stab["baseline_top"].sum() and info["n_scenarios"] == len(summ)


def test_missing_distance_scenarios_expand_set(feat_full):
    summ, _, _ = SE.run_sensitivity(feat_full, "M4")
    s = summ.set_index("skenario")
    for name in ("jarak kosong = defisit maksimum", "jarak kosong = median teramati"):
        assert s.loc[name, "n_tambah_vs_baseline"] == 3 and s.loc[name, "n_hilang_vs_baseline"] == 0
    assert s.loc["keluarkan snap > 250 m", "n_hilang_vs_baseline"] == 2


def test_scenario_specific_missing_values_are_excluded_and_reported(feat_full):
    """Regresi: 1 grid tanpa tree_prob_mean di data Agent 1 membuat skenario Dynamic World gagal."""
    f = feat_full.copy()
    f.loc[f.index[f["valid"]][0], "trees_prob"] = float("nan")
    summ, _, _ = SE.run_sensitivity(f, "M2")
    row = summ.set_index("skenario").loc["Dynamic World pohon rendah (ganti NDVI)"]
    assert row["n_hilang_vs_baseline"] == 1 and row["n_layak"] == int(f["valid"].sum()) - 1


def test_m1_has_no_park_or_population_scenarios(feat_full):
    summ, _, _ = SE.run_sensitivity(feat_full, "M1")
    assert not ({"ambang taman", "jarak taman kosong", "penduduk", "bobot"} & set(summ["kelompok"]))


def test_scenarios_change_one_decision_at_a_time(feat_full):
    w0 = C.MODELS["M4"]
    for s in SE.build_scenarios(w0, feat_full):
        changed = [s.weights != w0, bool(s.kw), s.policy is not None, s.exclude is not None]
        assert sum(changed) == 1, s.name


def test_no_valid_cells(root_p2):
    from jhim import data as D

    feat, _, _ = D.load_features(root_p2)
    with pytest.raises(ValueError):
        SE.run_sensitivity(feat, "M4")
