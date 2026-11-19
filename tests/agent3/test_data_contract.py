"""Kontrak data: skema, ID, tipe, join satu-ke-satu, CRS, status masukan."""
import numpy as np
import pandas as pd
import pytest
from conftest import REPO, grid_ids, make_grid_gdf, p2_frame, rs_frame, write_root

from jhim import config as C
from jhim import data as D
from jhim.util import DataError


def test_status_p2_only_when_rs_missing(root_p2):
    st = D.assess_inputs(root_p2)
    assert st.state == D.P2_ONLY and not st.can_model and st.n_grid == 80


def test_status_complete(root_full):
    st = D.assess_inputs(root_full)
    assert st.state == D.COMPLETE and st.can_model and st.n_rs_usable == 80


def test_status_incomplete_when_lst_missing(tmp_path):
    ids = grid_ids()
    rs = rs_frame(ids)
    rs.loc[:4, "lst_c"] = np.nan
    st = D.assess_inputs(write_root(tmp_path, rs=rs))
    assert st.state == D.RS_INCOMPLETE and st.n_rs_usable == 75


def test_status_invalid_on_duplicate_rs_ids(tmp_path):
    ids = grid_ids()
    rs = pd.concat([rs_frame(ids), rs_frame(ids).iloc[:1]])
    st = D.assess_inputs(write_root(tmp_path, rs=rs))
    assert st.state == D.INVALID and "tidak unik" in st.errors[0]


def test_status_invalid_dummy_in_real_folder(tmp_path):
    rs = rs_frame(grid_ids()).assign(is_dummy=1)
    st = D.assess_inputs(write_root(tmp_path, rs=rs))
    assert st.state == D.INVALID and "dummy" in st.errors[0]


def test_status_invalid_other_grid_version(tmp_path):
    rs = rs_frame(grid_ids()).assign(**{C.KEY: [f"OTHER_{i}" for i in range(80)]})
    assert D.assess_inputs(write_root(tmp_path, rs=rs)).state == D.INVALID


def test_missing_person2_file(tmp_path):
    paths = write_root(tmp_path)
    paths.spatial_features.unlink()
    st = D.assess_inputs(paths)
    assert st.state == D.INVALID and "tidak ditemukan" in st.errors[0]


def test_missing_required_column(tmp_path):
    p2 = p2_frame(grid_ids()).drop(columns="pop_elderly")
    st = D.assess_inputs(write_root(tmp_path, p2=p2))
    assert st.state == D.INVALID and "pop_elderly" in st.errors[0]


def test_non_numeric_values_are_structural_errors(tmp_path):
    p2 = p2_frame(grid_ids()).astype({"population": object})
    p2.loc[0, "population"] = "abc"
    with pytest.raises(DataError, match="bukan angka"):
        D.load_population_inputs(write_root(tmp_path, p2=p2))


def test_empty_and_duplicate_ids_rejected():
    with pytest.raises(DataError, match="kosong"):
        D._check_key(pd.DataFrame({C.KEY: ["a", None]}), "x")
    with pytest.raises(DataError, match="tidak unik"):
        D._check_key(pd.DataFrame({C.KEY: ["a", "a ", "b"]}), "x")  # spasi dinormalisasi -> duplikat


def test_excel_style_ids_normalised():
    out = D.norm_ids(pd.Series([" 12.0", "13"]))
    assert out.tolist() == ["12", "13"]


def test_merge_one_to_one_preserves_rows_and_order(root_full):
    grid = D.read_grid_table(root_full.grid)
    rs = rs_frame(grid[C.KEY].tolist()).sample(frac=1, random_state=0)  # urutan acak
    rs = pd.concat([rs.iloc[2:], pd.DataFrame({C.KEY: ["EXTRA"], "lst_c": [40.0], "ndvi": [0.1]})])
    pop, _ = D.load_population_inputs(root_full)
    out, notes, dummy = D.merge_inputs(grid[C.KEY], rs, pop)
    assert len(out) == 80 and out[C.KEY].tolist() == grid[C.KEY].tolist()
    assert out["lst_c"].isna().sum() == 2  # dua grid tanpa baris -> NaN, bukan 0
    assert (out["lst_c"] == 0).sum() == 0
    assert any("tidak ada di master" in n for n in notes) and not dummy


def test_merge_without_rs(root_p2):
    grid = D.read_grid_table(root_p2.grid)
    pop, _ = D.load_population_inputs(root_p2)
    out, notes, _ = D.merge_inputs(grid[C.KEY], None, pop)
    assert out["lst_c"].isna().all() and len(out) == 80


def test_load_features_never_drops_rows(root_p2):
    feat, meta, st = D.load_features(root_p2)
    assert len(feat) == 80 and meta["n_valid"] == 0 and meta["input_status"] == D.P2_ONLY
    assert feat["valid_p2"].sum() == 77  # 3 jarak kosong


def test_agent1_column_names_accepted(tmp_path):
    """Skema remote_sensing_grid.csv Agent 1 (commit cdda424): alias opsional + rs_qa_ok teks."""
    ids = grid_ids()
    base = rs_frame(ids)
    rs = pd.DataFrame({C.KEY: ids, "lst_mean_c": base["lst_c"], "ndvi_mean": base["ndvi"],
                       "lst_c": base["lst_c"], "ndvi": base["ndvi"], "tree_fraction": np.nan,
                       "lst_valid_fraction": 1.0, "lst_observation_count": 10.0, "lst_unc_mean_k": 3.5,
                       "tree_prob_mean": 0.1, "built_prob_mean": 0.6,
                       "rs_qa_flags": ["edge_cell"] + [""] * 79, "rs_qa_ok": ["False"] + ["True"] * 79})
    rs.loc[1, "lst_valid_fraction"] = 0.27  # partial_lst -> dikeluarkan (< 0.5)
    paths = write_root(tmp_path, rs=rs)
    d, notes = D.load_remote_sensing(paths)
    assert {"lst_valid_frac", "lst_obs", "lst_unc_k", "trees_prob", "built_prob", "rs_qa_ok"} <= set(d.columns)
    assert d["rs_qa_ok"].tolist()[:2] == [0.0, 1.0]
    feat, meta, st = D.load_features(paths)
    # semua grid punya nilai dari Agent 1 -> COMPLETE; 1 grid gugur aturan QA dilaporkan di catatan
    assert st.state == D.COMPLETE and st.n_rs_usable == 79
    assert any("DIKELUARKAN aturan QA" in n and ids[1] in n for n in st.notes)
    assert feat.loc[0, "f_rs_qa"] and feat.loc[0, "rs_qa_flags"] == "edge_cell"
    assert feat.loc[0, "valid_rs"] and not feat.loc[1, "valid_rs"]  # QA buruk ditandai, porsi valid rendah dikeluarkan


def test_numeric_rs_qa_flags_survive_csv_roundtrip(root_full):
    rs = pd.read_csv(root_full.rs)
    rs["rs_qa_ok"] = 1.0
    rs.loc[0, "rs_qa_ok"] = 0.0
    rs.to_csv(root_full.rs, index=False)
    f, _, _ = D.load_features(root_full)
    assert f.loc[0, "f_rs_qa"] and f["f_rs_qa"].sum() == 1


AGENT1_RS = REPO / "data/processed/remote_sensing_grid.csv"


@pytest.mark.skipif(not AGENT1_RS.exists(), reason="keluaran Agent 1 tidak tersedia di mesin ini")
def test_real_agent1_remote_sensing_contract(monkeypatch):
    monkeypatch.setenv("JHIM_RS_PATH", str(AGENT1_RS))
    paths = C.Paths(root=REPO)
    st = D.assess_inputs(paths)
    assert st.state == D.COMPLETE and st.n_rs_rows == C.EXPECTED_N_GRID
    assert st.n_rs_usable == C.EXPECTED_N_GRID - 1  # JKT_R037_C062: piksel LST valid 27,8% < 50%
    assert any("JKT_R037_C062" in n for n in st.notes)
    rs, _ = D.load_remote_sensing(paths)
    assert rs[C.KEY].is_unique and rs["lst_c"].between(*C.LST_RANGE_C).all() and rs["ndvi"].between(-1, 1).all()


def test_legacy_person2_fallback(tmp_path):
    paths = write_root(tmp_path)
    p2 = pd.read_csv(paths.spatial_features).drop(columns=["park_reachable"])
    paths.spatial_features.unlink()
    p2.rename(columns={"population": "pop_sum"}).to_csv(paths.pop, index=False)
    df, notes = D.load_population_inputs(paths)
    assert "population" in df.columns and df["park_reachable"].sum() == 77
    assert any("diturunkan" in n for n in notes)


def test_grid_without_crs_rejected(tmp_path):
    g = make_grid_gdf()
    g = g.set_crs(None, allow_override=True)
    p = tmp_path / "g.gpkg"
    g.to_file(p, driver="GPKG")
    with pytest.raises(DataError, match="CRS"):
        D.read_grid_gdf(p)


def test_grid_projection_and_centroids(root_full):
    g = D.read_grid_gdf(root_full.grid, attrs=True)
    assert g.crs.to_epsg() == 32748 and {"kota", "area_km2", "coverage_ratio"} <= set(g.columns)
    t = D.read_grid_table(root_full.grid)
    assert np.allclose(t["x"].min(), 690250.0) and len(t) == 80


@pytest.mark.skipif(not (REPO / "data/processed/spatial_features.csv").exists(), reason="data Person 2 tidak ada")
def test_real_person2_known_counts():
    """Angka validasi Person 2 yang dilaporkan harus tereproduksi oleh loader Agent 3."""
    paths = C.Paths(root=REPO)
    p2, _ = D.load_population_inputs(paths)
    assert len(p2) == C.EXPECTED_N_GRID and p2[C.KEY].is_unique
    master = D.load_master_attrs(paths)
    assert set(master[C.KEY]) == set(p2[C.KEY])
    grid = D.read_grid_table(paths.grid)
    merged, _, _ = D.merge_inputs(grid[C.KEY], None, p2, master)
    f = D.clean_values(merged)
    assert int(f["f_park_route_missing"].sum()) == 226
    assert int((f["park_reachable"] == 0).sum()) == 226 and int(f["f_reach_mismatch"].sum()) == 0
    assert int(f["f_snap_far"].sum()) == 66
    if paths.demographic_corrected.exists():
        support = pd.read_csv(paths.demographic_support).set_index(C.KEY).loc[f[C.KEY]]
        assert int(f["f_pop_zero"].sum()) == 0
        assert f.population.isna().sum() == support.qa_population_source_no_support.sum() == 6
        assert f.pop_child.isna().sum() == f.pop_elderly.isna().sum() == support.qa_age_source_no_support.sum() == 6
        assert (f.raw_population.eq(0) == f.qa_population_source_no_support).all()
    else:
        assert int(f["f_pop_zero"].sum()) == 6
        assert f[["population", "pop_child", "pop_elderly"]].isna().sum().sum() == 0
    assert int(f["f_park_access_500m_mismatch"].sum()) == 0 and int(f["f_park_access_1000m_mismatch"].sum()) == 0


@pytest.mark.skipif(not (REPO / "data/processed/grid_500m_jakarta.gpkg").exists(), reason="master grid tidak ada")
def test_real_grid_web_projection_inside_jakarta():
    g = D.read_grid_gdf(REPO / "data/processed/grid_500m_jakarta.gpkg").to_crs(C.CRS_WEB)
    minx, miny, maxx, maxy = g.total_bounds
    assert 106.6 < minx < maxx < 107.1 and -6.45 < miny < maxy < -6.0
