"""Dashboard: impor, navigasi semua halaman, mode data asli (tanpa RS) dan DEMO, tanpa exception.

Memakai data di repositori (data/processed). Dilewati bila data atau streamlit tidak tersedia.
"""
import pytest
from conftest import REPO

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

APP = str(REPO / "dashboard/app.py")
PAGES = ["overview", "data_explorer", "heat_vegetation", "priority_models", "model_comparison",
         "spatial_stats", "sensitivity", "methods"]
HAVE_DATA = (REPO / "data/processed/spatial_features.csv").exists() and (REPO / "data/processed/dummy").exists()
pytestmark = pytest.mark.skipif(not HAVE_DATA, reason="data repositori tidak tersedia")


def _run(page: str, mode: str) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=300)
    at.session_state["mode"] = mode
    at.run()
    at.switch_page(f"views/{page}.py")
    at.run()
    return at


@pytest.mark.parametrize("page", PAGES)
def test_pages_real_mode(page):
    at = _run(page, "Data asli")
    assert not at.exception, [e.value for e in at.exception]
    assert len(at.title) == 1
    text = " ".join(m.value for m in at.markdown) + " ".join(w.value for w in at.warning) + \
        " ".join(i.value for i in at.info)
    assert "MODE DEMO" not in text  # data asli tidak boleh berlabel demo
    rs_present = (REPO / "data/processed/remote_sensing_grid.csv").exists()
    if page in ("priority_models", "model_comparison", "sensitivity", "heat_vegetation") and not rs_present:
        assert any("belum tersedia" in w.value for w in at.warning)


@pytest.mark.parametrize("page", ["overview", "priority_models", "model_comparison", "sensitivity"])
def test_pages_demo_mode_always_labelled(page):
    at = _run(page, "DEMO (data sintetis)")
    assert not at.exception, [e.value for e in at.exception]
    assert any("MODE DEMO" in e.value for e in at.error)


@pytest.mark.parametrize("page", PAGES)
def test_pages_missing_rs_mode(page, monkeypatch, tmp_path):
    monkeypatch.setenv("JHIM_RS_PATH", str(tmp_path / "unavailable_remote_sensing.csv"))
    at = _run(page, "Data asli")
    assert not at.exception, [e.value for e in at.exception]
    assert len(at.title) == 1
    if page in ("priority_models", "model_comparison", "sensitivity", "heat_vegetation"):
        assert any("belum tersedia" in w.value for w in at.warning)


@pytest.mark.parametrize("page", PAGES)
def test_pages_corrected_candidate_scope_and_support(page, monkeypatch):
    inputs = REPO / "data/processed/remediation_inputs"
    if not (inputs / "demographic_support.csv").exists():
        pytest.skip("corrected frozen candidate unavailable")
    monkeypatch.setenv("JHIM_INPUT_DIR", str(inputs))
    monkeypatch.setenv("JHIM_RS_PATH", str(inputs / "remote_sensing_grid.csv"))
    monkeypatch.setenv("JHIM_DEMOGRAPHIC_SUPPORT", str(inputs / "demographic_support.csv"))
    at = _run(page, "Data asli")
    assert not at.exception, [e.value for e in at.exception]
    visible = " ".join(e.value for kind in (at.caption, at.warning) for e in kind)
    assert "2026" in visible and "2024" in visible
    assert "19 grid" in visible and "2,526" in visible
    assert "provisional" in visible.lower() or "belum disahkan" in visible


def test_candidate_custom_weights_and_missingness_filter(monkeypatch):
    inputs = REPO / "data/processed/remediation_inputs"
    if not inputs.exists():
        pytest.skip("corrected frozen candidate unavailable")
    monkeypatch.setenv("JHIM_INPUT_DIR", str(inputs))
    at = _run("priority_models", "Data asli")
    at.toggle[0].set_value(True).run()
    assert not at.exception
    assert any("EKSPLORATIF" in e.value for e in at.warning)
    at.slider[0].set_value(.35).run()
    assert not at.exception
    assert any(m.value == "253" for m in at.metric)
    at = _run("data_explorer", "Data asli")
    at.multiselect[0].set_value(["qa_age_source_no_support"]).run()
    assert not at.exception
    assert any(len(t.value) == 19 for t in at.dataframe)


def test_candidate_spatial_tail_and_correction_controls(monkeypatch):
    """Tail (directed/two-sided) and correction (BH/BY/uncorrected) controls recompute without errors."""
    inputs = REPO / "data/processed/remediation_inputs"
    if not (inputs / "demographic_support.csv").exists():
        pytest.skip("corrected frozen candidate unavailable")
    monkeypatch.setenv("JHIM_INPUT_DIR", str(inputs))
    monkeypatch.setenv("JHIM_RS_PATH", str(inputs / "remote_sensing_grid.csv"))
    monkeypatch.setenv("JHIM_DEMOGRAPHIC_SUPPORT", str(inputs / "demographic_support.csv"))
    at = _run("spatial_stats", "Data asli")
    assert not at.exception, [e.value for e in at.exception]

    def widget(kind, label):
        return next(w for w in getattr(at, kind) if w.label == label)

    # Keep global Moran small so the test exercises the LISA controls rather than permutation volume.
    widget("multiselect", "Variabel").set_value(["m4_score"]).run()
    widget("multiselect", "Definisi tetangga").set_value(["queen"]).run()
    widget("select_slider", "Permutasi").set_value(99).run()
    widget("selectbox", "Variabel LISA").set_value("m4_score").run()
    assert not at.exception, [e.value for e in at.exception]
    crosstabs = {}
    for alternative in ("directed", "two-sided"):
        widget("selectbox", "Alternatif LISA (provisional)").set_value(alternative).run()
        for option in widget("radio", "Signifikansi").options:
            widget("radio", "Signifikansi").set_value(option).run()
            assert not at.exception, (alternative, option, [e.value for e in at.exception])
            # Tested-not-significant and untested grids are reported separately (unknown is not a test result).
            assert any("grid tidak diuji" in c.value for c in at.caption)
            if option.startswith("BY"):
                # 99 permutations cannot pass BY on ~2500 tests; the UI must say this is resolution, not absence.
                assert any("resolusi permutasi" in i.value for i in at.info)
        crosstabs[alternative] = at.dataframe[-1].value.to_numpy().sum()
        assert any(f"1/(99+1)" in c.value for c in at.caption)
    # Both alternatives produce a p<0.05 x FDR cross-tabulation over the same eligible non-island grids.
    assert crosstabs["directed"] == crosstabs["two-sided"] > 2000
