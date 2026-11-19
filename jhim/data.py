"""Baca, validasi, gabung, dan bersihkan data per grid (kontrak data Agent 3).

Prinsip:
- Kesalahan STRUKTUR (berkas/kolom/ID/tipe) menghentikan proses dengan DataError yang jelas.
- Nilai buruk dikosongkan, diberi bendera f_*, dan sel dikeluarkan dari himpunan pembanding.
- Tidak ada baris yang dihapus: keluaran selalu satu baris per grid master.
- Nilai kosong TIDAK PERNAH diisi 0. `park_distance_m` kosong berarti rute tidak dihitung,
  bukan jarak nol, bukan jarak tak hingga, dan bukan bukti tidak ada taman publik.
  Nilai mentah tidak ditimpa; skenario imputasi ditulis ke `park_distance_used_m`.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from . import config as C
from .util import DataError, utc_stamp, versions

# status masukan
INVALID, P2_ONLY, RS_INCOMPLETE, COMPLETE = "INVALID", "P2_ONLY", "RS_INCOMPLETE", "COMPLETE"
STATUS_TEXT = {
    INVALID: "Masukan tidak konsisten atau tidak valid; lihat daftar galat.",
    P2_ONLY: "Data Person 2 tersedia dan valid; data remote sensing Agent 1 BELUM ada. "
             "Skor M1-M4 belum dapat dihitung.",
    RS_INCOMPLETE: "Data remote sensing ada tetapi sebagian grid tidak punya nilai LST/NDVI dari Agent 1; "
                   "grid tersebut dikeluarkan dan dilaporkan.",
    COMPLETE: "Semua masukan tersedia untuk seluruh grid dan lolos validasi struktur. Grid yang gagal "
              "aturan QA (bila ada) dikeluarkan dan dilaporkan di catatan.",
}


# ---------------------------------------------------------------- kunci
def norm_ids(s: pd.Series) -> pd.Series:
    """Seragamkan grid_id menjadi teks (hilangkan spasi dan akhiran '.0' bawaan Excel)."""
    out = s.astype("string").str.strip().str.replace(r"\.0+$", "", regex=True)
    return out.astype(str)


def _check_key(df: pd.DataFrame, name: str) -> pd.DataFrame:
    if C.KEY not in df.columns:
        raise DataError(f"{name}: kolom {C.KEY} tidak ada. Kolom yang ada: {list(df.columns)}")
    raw = df[C.KEY]
    if raw.isna().any() or (raw.astype("string").str.strip() == "").any():
        raise DataError(f"{name}: ada {C.KEY} kosong.")
    out = df.copy()
    out[C.KEY] = norm_ids(raw)
    dup = out.loc[out[C.KEY].duplicated(keep=False), C.KEY]
    if len(dup):
        ex = ", ".join(sorted(dup.unique())[:5])
        raise DataError(f"{name}: {C.KEY} tidak unik ({dup.nunique()} id berulang, contoh: {ex}).")
    return out


def _to_numeric_strict(df: pd.DataFrame, cols, name: str) -> pd.DataFrame:
    """Ubah kolom ke float. Teks bukan angka (selain kosong) adalah galat struktur, bukan NaN diam-diam."""
    out = df.copy()
    for c in cols:
        if c not in out.columns:
            continue
        raw = out[c]
        num = pd.to_numeric(raw, errors="coerce")
        bad = num.isna() & raw.notna() & (raw.astype("string").str.strip() != "")
        if bad.any():
            ex = ", ".join(map(str, raw[bad].astype(str).unique()[:3]))
            raise DataError(f"{name}: kolom {c} memuat {int(bad.sum())} nilai bukan angka (contoh: {ex}).")
        out[c] = num.astype(float)
    return out


# ---------------------------------------------------------------- baca grid
def read_grid_table(path) -> pd.DataFrame:
    """DataFrame [grid_id, x, y, (kota, area_km2, coverage_ratio)] dengan titik tengah dalam meter (EPSG:32748).

    .gpkg dibaca dengan geopandas. .csv (untuk uji tanpa geopandas) harus punya kolom grid_id, x, y.
    """
    p = Path(path)
    if not p.exists():
        raise DataError(f"Master grid tidak ditemukan: {p}")
    if p.suffix.lower() == ".csv":
        df = pd.read_csv(p, dtype={C.KEY: "string"})
        miss = [c for c in (C.KEY, "x", "y") if c not in df.columns]
        if miss:
            raise DataError(f"CSV grid perlu kolom {miss}.")
        keep = [C.KEY, "x", "y", *[a for a in C.MASTER_ATTRS if a in df.columns]]
        return _check_key(df[keep], "grid")
    g = read_grid_gdf(p, attrs=True)
    ctr = g.to_crs(C.CRS_PROJECTED).geometry.centroid
    out = pd.DataFrame({C.KEY: g[C.KEY].to_numpy(), "x": ctr.x.to_numpy(), "y": ctr.y.to_numpy()})
    for a in C.MASTER_ATTRS:
        if a in g.columns:
            out[a] = g[a].to_numpy()
    return _check_key(out, "grid")


def read_grid_gdf(path, attrs: bool = False):
    """Baca master grid sebagai GeoDataFrame [grid_id, (atribut master), geometry].

    Memilih layer pertama di .gpkg yang PUNYA geometri dan kolom grid_id; menolak bila CRS tidak ada,
    ada geometri kosong/tidak valid, atau grid_id duplikat.
    """
    try:
        import geopandas as gpd
    except ImportError as exc:
        raise DataError("geopandas belum terpasang: python -m pip install geopandas") from exc
    p = Path(path)
    if not p.exists():
        raise DataError(f"Master grid tidak ditemukan: {p}")
    try:
        names = list(gpd.list_layers(p)["name"])
    except Exception:
        names = [None]
    seen = []
    for name in names:
        g = gpd.read_file(p, layer=name) if name else gpd.read_file(p)
        try:
            geom_name = g.geometry.name
        except (AttributeError, TypeError):
            seen.append(f"{name}: tanpa geometri")
            continue
        if C.KEY not in g.columns:
            seen.append(f"{name}: tanpa kolom {C.KEY} (kolom: {list(g.columns)[:8]})")
            continue
        if g.crs is None:
            raise DataError(f"Layer {name}: CRS tidak ada.")
        g = g.rename_geometry("geometry") if geom_name != "geometry" else g
        if g.geometry.isna().any() or g.geometry.is_empty.any():
            raise DataError(f"Layer {name}: {int((g.geometry.isna() | g.geometry.is_empty).sum())} geometri kosong.")
        cols = [C.KEY, *[a for a in C.MASTER_ATTRS if attrs and a in g.columns], "geometry"]
        out = g[cols].copy()
        out[C.KEY] = norm_ids(out[C.KEY])
        if out[C.KEY].duplicated().any():
            raise DataError(f"Layer {name}: {C.KEY} duplikat di master grid.")
        return out.reset_index(drop=True)
    raise DataError("Tidak ada layer grid yang punya geometri dan kolom grid_id. Layer yang ditemukan: " + "; ".join(seen))


def load_master_attrs(paths: C.Paths) -> pd.DataFrame | None:
    """Atribut master (kota, area_km2, coverage_ratio) dari grid_master.csv; None bila tidak ada."""
    p = paths.grid_master
    if not p.exists():
        return None
    d = read_input_csv(p, (), p.name)
    keep = [C.KEY, *[a for a in C.MASTER_ATTRS if a in d.columns]]
    d = d[keep]
    return _to_numeric_strict(d, [a for a in ("area_km2", "coverage_ratio") if a in d.columns], p.name)


# ---------------------------------------------------------------- baca masukan
def read_input_csv(path, required, name: str, aliases: dict | None = None) -> pd.DataFrame:
    """aliases: {nama_di_berkas: nama_baku}, mis. {"pop_sum": "population"} (dipakai bila nama baku tidak ada)."""
    p = Path(path)
    if not p.exists():
        raise DataError(f"{name}: berkas tidak ditemukan: {p}")
    try:
        df = pd.read_csv(p, dtype={C.KEY: "string"})
    except Exception as exc:  # parser pandas punya banyak jenis galat
        raise DataError(f"{name}: gagal dibaca ({exc})") from exc
    df.columns = [str(c).strip() for c in df.columns]
    for old, new in (aliases or {}).items():
        if old in df.columns and new not in df.columns:
            df = df.rename(columns={old: new})
    miss = [c for c in (C.KEY, *required) if c not in df.columns]
    if miss:
        raise DataError(f"{name}: kolom wajib hilang: {miss}. Kolom yang ada: {list(df.columns)}")
    return _check_key(df, name)


def _finish_pop(df: pd.DataFrame, name: str, notes: list[str]) -> pd.DataFrame:
    num = [c for c in (*C.POP_REQUIRED, *C.POP_OPTIONAL) if c in df.columns]
    df = _to_numeric_strict(df, num, name)
    if "park_reachable" not in df.columns:
        df["park_reachable"] = df["park_distance_m"].notna().astype(float)
        notes.append(f"{name}: park_reachable tidak ada; diturunkan dari park_distance_m (kosong = 0).")
    return df


def support_bool(s: pd.Series) -> pd.Series:
    """Parse a documented support flag; unknown spellings must not turn into False."""
    mapped = s.astype("string").str.strip().str.lower().map({"true": True, "false": False, "1": True, "0": False,
                                                           "1.0": True, "0.0": False})
    if mapped.isna().any():
        raise DataError(f"Support flag has missing/invalid values: {s[mapped.isna()].head().tolist()}")
    return mapped.astype(bool)


def attach_demographic_evidence(df, paths, notes):
    """Versioned, full-ID overlays. Keep exported numbers beside analytical values."""
    out = df.copy()
    for path, corrected in ((paths.demographic_support, False), (paths.demographic_corrected, True)):
        if not path.exists():
            continue
        required = ("support_version",) if corrected else ("support_version", "qa_population_source_no_support", "qa_age_source_no_support")
        d = read_input_csv(path, required, path.name)
        if set(d[C.KEY]) != set(out[C.KEY]) or d["support_version"].isna().any():
            raise DataError(f"{path.name}: support version and exact full grid ID set required")
        if corrected:
            for col in ("population", "pop_child", "pop_elderly"):
                if col not in d:
                    raise DataError(f"{path.name}: missing corrected {col}")
                out[f"raw_{col}"] = out.get(f"raw_{col}", out[col])
                values = _to_numeric_strict(d, [col], path.name).set_index(C.KEY)[col]
                out[col] = out[C.KEY].map(values)
        for col in d:
            if col != C.KEY and (not corrected or col not in ("population", "pop_child", "pop_elderly")):
                values = d.set_index(C.KEY)[col]
                incoming = out[C.KEY].map(values)
                if col in out and not out[col].fillna("<null>").equals(incoming.fillna("<null>")):
                    raise DataError(f"{path.name}: conflicting evidence column {col}")
                out[col] = incoming
        notes.append(f"Demographic evidence: {path.name}; versions {sorted(d.support_version.unique())}")
    if "qa_age_source_no_support" not in out:
        notes.append("Demographic source support unavailable: legacy values are unverified, not confirmed zeros.")
    return out


def load_population_inputs(paths: C.Paths) -> tuple[pd.DataFrame, list[str]]:
    """Muat data penduduk dan akses taman dari Person 2. Urutan pencarian:

    1. spatial_features.csv (integrasi Person 2; berkas utama)
    2. population_accessibility_grid.csv (format gabungan lama; dipakai data dummy)
    3. gabungan population_grid.csv + vulnerability_grid.csv + accessibility_grid.csv
    """
    notes: list[str] = []
    for p in (paths.spatial_features, paths.pop):
        if p.exists():
            d = read_input_csv(p, C.POP_REQUIRED, p.name, aliases=C.POP_ALIASES)
            notes.append(f"Person 2: {p.name} ({len(d):,} baris)")
            return attach_demographic_evidence(_finish_pop(d, p.name, notes), paths, notes), notes

    found = [p for p in paths.pop_parts if p.exists()]
    if not found:
        names = ", ".join(p.name for p in (paths.spatial_features, paths.pop, *paths.pop_parts))
        raise DataError(f"Data Person 2 tidak ditemukan di {paths.inputs_dir}. Harus ada salah satu dari: {names}")
    merged = None
    for p in found:
        d = read_input_csv(p, (), p.name, aliases=C.POP_ALIASES)
        clash = [c for c in d.columns if c != C.KEY and merged is not None and c in merged.columns]
        if clash:
            raise DataError(f"{p.name}: kolom {clash} sudah ada di berkas lain; satu kolom hanya boleh di satu berkas.")
        notes.append(f"{p.name}: {len(d):,} baris, kolom {[c for c in d.columns if c != C.KEY]}")
        merged = d if merged is None else merged.merge(d, on=C.KEY, how="outer", validate="one_to_one")
    miss = [c for c in C.POP_REQUIRED if c not in merged.columns]
    if miss:
        have = ", ".join(p.name for p in found)
        raise DataError(f"Data Person 2 belum lengkap. Kolom yang masih kurang: {miss}. Berkas yang terbaca: {have}.")
    return attach_demographic_evidence(_finish_pop(merged, "Person 2 (berkas terpisah)", notes), paths, notes), notes


def load_remote_sensing(paths: C.Paths) -> tuple[pd.DataFrame | None, list[str]]:
    """Muat remote_sensing_grid.csv (Agent 1). (None, catatan) bila berkas belum ada."""
    p = paths.rs
    if not p.exists():
        return None, [f"Remote sensing: {p.name} belum ada di {p.parent}."]
    d = read_input_csv(p, C.RS_COLS, p.name, aliases=C.RS_ALIASES)
    if "rs_qa_ok" in d.columns:  # True/False (teks atau bool) -> 1/0
        d["rs_qa_ok"] = d["rs_qa_ok"].map(lambda v: {"true": 1.0, "false": 0.0, "1": 1.0, "0": 0.0, "1.0": 1.0, "0.0": 0.0}.get(
            str(v).strip().lower(), np.nan) if pd.notna(v) else np.nan)
    d = _to_numeric_strict(d, [c for c in (*C.RS_COLS, *C.RS_OPTIONAL) if c in d.columns], p.name)
    opt = [c for c in C.RS_OPTIONAL if c in d.columns]
    return d, [f"Remote sensing: {p.name} ({len(d):,} baris; kolom opsional: {opt or 'tidak ada'})"]


def _is_dummy(d: pd.DataFrame | None) -> bool:
    return d is not None and "is_dummy" in d.columns and bool(
        pd.to_numeric(d["is_dummy"], errors="coerce").fillna(0).astype(bool).any())


# ---------------------------------------------------------------- status masukan
@dataclass
class InputStatus:
    state: str
    demo: bool
    files: dict = field(default_factory=dict)
    n_grid: int = 0
    n_rs_rows: int = 0
    n_rs_usable: int = 0
    errors: list = field(default_factory=list)
    notes: list = field(default_factory=list)

    @property
    def text(self) -> str:
        return STATUS_TEXT[self.state]

    @property
    def can_model(self) -> bool:
        return self.state in (RS_INCOMPLETE, COMPLETE)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["text"] = self.text
        return d


def assess_inputs(paths: C.Paths) -> InputStatus:
    """Periksa keberadaan dan validitas struktur semua masukan tanpa memodelkan."""
    st = InputStatus(state=INVALID, demo=paths.demo)
    for label, p in (("master_grid", paths.grid), ("grid_master_csv", paths.grid_master),
                     ("person2_spatial_features", paths.spatial_features), ("remote_sensing", paths.rs)):
        st.files[label] = {"path": str(p), "exists": p.exists()}
    try:
        grid = read_grid_table(paths.grid)
        st.n_grid = len(grid)
        if not paths.demo and st.n_grid != C.EXPECTED_N_GRID:
            st.notes.append(f"Master grid berisi {st.n_grid:,} grid (diharapkan {C.EXPECTED_N_GRID:,}).")
        pop, n = load_population_inputs(paths)
        st.notes += n
        missing = int((~grid[C.KEY].isin(pop[C.KEY])).sum())
        extra = int((~pop[C.KEY].isin(grid[C.KEY])).sum())
        if missing or extra:
            st.notes.append(f"Person 2 vs master: {missing} grid master tanpa baris, {extra} baris di luar master.")
        if _is_dummy(pop) and not paths.demo:
            raise DataError("Data Person 2 di folder data asli memuat is_dummy=1.")
        rs, n = load_remote_sensing(paths)
        st.notes += n
        if rs is None:
            st.state = P2_ONLY
            return st
        if _is_dummy(rs) and not paths.demo:
            raise DataError("remote_sensing_grid.csv di folder data asli memuat is_dummy=1 (data dummy).")
        st.n_rs_rows = len(rs)
        overlap = float(rs[C.KEY].isin(grid[C.KEY]).mean()) if len(rs) else 0.0
        if overlap < C.MIN_ID_OVERLAP:
            raise DataError(f"remote_sensing: hanya {overlap:.0%} grid_id cocok dengan master grid.")
        r = grid[[C.KEY]].merge(rs, on=C.KEY, how="left", validate="one_to_one")
        # "dikirim" = Agent 1 memberi nilai LST dan NDVI; "dapat dipakai" = juga lolos aturan QA Agent 3.
        delivered = r["lst_c"].notna() & r["ndvi"].notna()
        ok = r["lst_c"].between(*C.LST_RANGE_C) & r["ndvi"].between(*C.NDVI_RANGE)
        if "lst_valid_frac" in r.columns:
            ok &= r["lst_valid_frac"] >= C.MIN_LST_VALID_FRAC
        st.n_rs_usable = int(ok.sum())
        n_missing = int((~delivered).sum())
        st.state = COMPLETE if n_missing == 0 else RS_INCOMPLETE
        if n_missing:
            st.notes.append(f"Remote sensing: {n_missing:,} dari {st.n_grid:,} grid tanpa nilai LST/NDVI dari Agent 1.")
        qa_out = r.loc[delivered & ~ok, C.KEY].tolist()
        if qa_out:
            ex = ", ".join(qa_out[:5]) + (" ..." if len(qa_out) > 5 else "")
            st.notes.append(
                f"Remote sensing: {len(qa_out):,} grid punya nilai tetapi DIKELUARKAN aturan QA "
                f"(LST/NDVI di luar rentang atau piksel LST valid < {C.MIN_LST_VALID_FRAC:.0%}): {ex}")
    except DataError as exc:
        st.state = INVALID
        st.errors.append(str(exc))
    return st


# ---------------------------------------------------------------- gabung
def merge_inputs(ids: pd.Series, rs: pd.DataFrame | None, pop: pd.DataFrame, master: pd.DataFrame | None = None):
    """Gabungkan ke master grid (left join, satu-ke-satu). Kembalikan (DataFrame, catatan, dummy).

    rs=None diperbolehkan (remote sensing belum ada): kolom LST/NDVI menjadi NaN.
    """
    base = _check_key(pd.DataFrame({C.KEY: ids.to_numpy()}), "master grid")
    notes: list[str] = []
    dummy = _is_dummy(rs) or _is_dummy(pop)
    # Preserve versioned source-support fields and routing diagnostics, including raw exports.
    sources = [("population_accessibility", pop, tuple(c for c in pop if c != C.KEY))]
    if rs is not None:
        sources.insert(0, ("remote_sensing", rs, (*C.RS_COLS, *C.RS_OPTIONAL, *C.RS_TEXT)))
    else:
        notes.append("remote_sensing: belum tersedia; kolom LST/NDVI kosong.")
    if master is not None:
        sources.append(("grid_master", master, C.MASTER_ATTRS))
    out = base
    for name, d, cols in sources:
        in_grid = d[C.KEY].isin(base[C.KEY])
        overlap = float(in_grid.mean()) if len(d) else 0.0
        if overlap < C.MIN_ID_OVERLAP:
            raise DataError(
                f"{name}: hanya {overlap:.0%} grid_id cocok dengan master grid. "
                "Kemungkinan versi grid berbeda; periksa dengan pemilik data."
            )
        n_extra = int((~in_grid).sum())
        n_absent = int((~base[C.KEY].isin(d[C.KEY])).sum())
        if n_extra:
            notes.append(f"{name}: {n_extra} baris tidak ada di master grid (diabaikan).")
        if n_absent:
            notes.append(f"{name}: {n_absent} grid master tidak punya baris di berkas ini (jadi kosong).")
        use = [c for c in cols if c in d.columns and c not in out.columns]
        extra_cols = [c for c in d.columns if c not in (C.KEY, "is_dummy", *cols)]
        if extra_cols:
            notes.append(f"{name}: kolom tidak dipakai diabaikan: {extra_cols}")
        out = out.merge(d.loc[in_grid, [C.KEY, *use]], on=C.KEY, how="left", validate="one_to_one")
    if len(out) != len(base) or not out[C.KEY].equals(base[C.KEY]):
        raise DataError("Penggabungan menggandakan, menghilangkan, atau mengubah urutan grid (tidak boleh terjadi).")
    for c in (*C.FEATURE_COLS, *C.POP_OPTIONAL, "area_km2", "coverage_ratio"):
        if c not in out.columns:
            out[c] = np.nan
    if "kota" not in out.columns:
        out["kota"] = pd.NA
    return out, notes, dummy


# ---------------------------------------------------------------- bersihkan
def _bad(s: pd.Series, lo=None, hi=None):
    """Kembalikan (kosong, di_luar_rentang) untuk deret numerik."""
    miss = s.isna()
    oor = pd.Series(False, index=s.index)
    if lo is not None:
        oor |= s < lo
    if hi is not None:
        oor |= s > hi
    return miss, oor & ~miss


def normalize_policy(unreachable: str) -> str:
    u = C.UNREACHABLE_ALIASES.get(unreachable, unreachable)
    if u not in C.UNREACHABLE_POLICIES:
        raise ValueError(f"unreachable harus salah satu dari {C.UNREACHABLE_POLICIES} (atau 'cap')")
    return u


def clean_values(df: pd.DataFrame, unreachable: str = "exclude") -> pd.DataFrame:
    """Ubah ke numerik, kosongkan nilai tidak wajar, beri bendera, hitung kelayakan.

    unreachable: perlakuan park_distance_m kosong (rute tidak dihitung), lihat config.UNREACHABLE_POLICIES.
        Nilai mentah park_distance_m TIDAK diubah; nilai yang dipakai model ada di park_distance_used_m.

    Kolom kelayakan:
        valid_rs  LST dan NDVI tersedia dan wajar (serta lst_valid_frac cukup, bila ada)
        valid_p2  populasi, anak, lansia, dan jarak taman yang dipakai tersedia dan konsisten
        elig_m1..elig_m4  kelayakan masing-masing model
        valid     = elig_m4 = himpunan grid pembanding BERSAMA untuk semua model
    """
    unreachable = normalize_policy(unreachable)
    out = df.copy()
    # Missing support is not a numerical zero. Preserve originals even when clean_values is rerun.
    for value, flag in (("population", "qa_population_source_no_support"),
                        ("pop_child", "qa_age_source_no_support"), ("pop_elderly", "qa_age_source_no_support")):
        if flag in out:
            out[flag] = support_bool(out[flag])
            out[f"raw_{value}"] = out.get(f"raw_{value}", out[value]).copy()
            out.loc[out[flag], value] = np.nan
    num = [c for c in (*C.FEATURE_COLS, *C.RS_OPTIONAL, *C.POP_OPTIONAL, "area_km2", "coverage_ratio") if c in out.columns]
    for c in num:
        out[c] = pd.to_numeric(out[c], errors="coerce")

    specs = {
        "lst_c": C.LST_RANGE_C,
        "ndvi": C.NDVI_RANGE,
        "population": (0, None),
        "pop_child": (0, None),
        "pop_elderly": (0, None),
        "park_distance_m": (0, None),
    }
    for col, (lo, hi) in specs.items():
        miss, oor = _bad(out[col], lo, hi)
        out[f"f_{col}_missing"] = miss
        out[f"f_{col}_range"] = oor
        out.loc[oor, col] = np.nan
    for col in ("trees_prob", "built_prob", "lst_valid_frac"):
        if col in out.columns:
            _, oor = _bad(out[col], *C.PROB_RANGE)
            out.loc[oor, col] = np.nan

    # ---- jarak taman: nilai yang dipakai model (mentah tidak diubah)
    unknown = out["park_distance_m"].isna() & ~out["f_park_distance_m_range"]
    out["f_park_route_missing"] = unknown
    used = out["park_distance_m"].copy()
    if unreachable == "worst":
        used[unknown] = C.PARK_CAP_M
    elif unreachable == "median":
        used[unknown] = float(out["park_distance_m"].median()) if out["park_distance_m"].notna().any() else np.nan
    out["park_distance_used_m"] = used
    out["f_park_imputed"] = unknown & used.notna()
    out["f_park_unreachable"] = out["f_park_imputed"]  # nama lama

    reach = out["park_reachable"] if "park_reachable" in out.columns else pd.Series(np.nan, index=out.index)
    out["f_reach_mismatch"] = reach.notna() & ((reach == 0) != out["park_distance_m"].isna())

    # ---- demografi turunan
    out["pop_vulnerable"] = out["pop_child"] + out["pop_elderly"]
    out["f_age_gt_pop"] = (out["pop_vulnerable"] > out["population"] * C.AGE_TOLERANCE + 1).fillna(False)
    share = out["pop_vulnerable"] / out["population"].where(out["population"] > 0)
    # Composition has no defined denominator for zero or missing population.
    out["vuln_share"] = share.clip(upper=1.0)
    area = out["area_km2"].where(out["area_km2"] > 0)
    out["pop_density_km2"] = out["population"] / area
    out["f_pop_zero"] = out["population"] == 0

    # ---- QA Person 2 dan remote sensing
    out["f_snap_far"] = (out["grid_snap_m"] > C.SNAP_QA_M).fillna(False)
    out["f_low_coverage"] = (out["coverage_ratio"] < C.LOW_COVERAGE).fillna(False)
    out["f_rs_qa"] = (out["rs_qa_ok"] == 0).fillna(False) if "rs_qa_ok" in out.columns else False
    out["f_lst_low_valid"] = (
        (out["lst_valid_frac"] < C.MIN_LST_VALID_FRAC).fillna(False) if "lst_valid_frac" in out.columns
        else pd.Series(False, index=out.index)
    )

    for k, thr in (("park_access_500m", 500), ("park_access_1000m", 1000)):
        acc = out[k] if k in out.columns else pd.Series(np.nan, index=out.index)
        nb = acc.notna() & ~acc.isin([0, 1])
        out.loc[nb, k] = np.nan
        both = out[k].notna() & out["park_distance_m"].notna()
        out[f"f_{k}_mismatch"] = both & ((out["park_distance_m"] <= thr).astype(float) != out[k])
        if k == "park_access_500m":
            out["f_access_not_binary"] = nb
            out["f_access_mismatch"] = out[f"f_{k}_mismatch"]

    # ---- kelayakan
    lst_ok = out["lst_c"].notna() & ~out["f_lst_low_valid"]
    out["valid_rs"] = lst_ok & out["ndvi"].notna()
    out["valid_p2"] = (out[["population", "pop_child", "pop_elderly", "park_distance_used_m"]].notna().all(axis=1)
                       & ~out["f_age_gt_pop"])
    out["elig_m1"] = lst_ok
    out["elig_m2"] = out["valid_rs"]
    out["elig_m3"] = out["elig_m2"] & out["population"].notna()
    out["elig_m4"] = out["valid_rs"] & out["valid_p2"]
    out["valid"] = out["elig_m4"]
    reason_flags = {
        "missing_thermal_measurement": out[["lst_c", "ndvi"]].isna().any(axis=1),
        "low_lst_support_QA": out["f_lst_low_valid"],
        "missing_total_population": out["population"].isna(),
        "missing_age_support_or_value": out[["pop_child", "pop_elderly"]].isna().any(axis=1),
        "age_inconsistent": out["f_age_gt_pop"],
        "missing_walking_route": out["park_distance_used_m"].isna(),
    }
    out["eligibility_reasons"] = [";".join(k for k, f in reason_flags.items() if bool(f.loc[i]))
                                  for i in out.index]
    return out


def quality_table(df: pd.DataFrame) -> pd.DataFrame:
    """Ringkasan: berapa sel kosong/tidak wajar/ditandai per variabel dan berapa yang dikeluarkan."""
    n = len(df)
    rows = []
    for col in ("lst_c", "ndvi", "population", "pop_child", "pop_elderly", "park_distance_m"):
        rows.append({"item": f"{col} kosong", "jumlah": int(df[f"f_{col}_missing"].sum())})
        if df[f"f_{col}_range"].any():
            rows.append({"item": f"{col} di luar rentang (dikosongkan)", "jumlah": int(df[f"f_{col}_range"].sum())})
    rows += [
        {"item": "rute taman tidak dihitung (park_distance_m kosong)", "jumlah": int(df["f_park_route_missing"].sum())},
        {"item": "jarak taman diimputasi (skenario worst/median)", "jumlah": int(df["f_park_imputed"].sum())},
        {"item": "park_reachable tidak konsisten dengan jarak", "jumlah": int(df["f_reach_mismatch"].sum())},
        {"item": f"QA: snap grid ke jaringan > {C.SNAP_QA_M:g} m", "jumlah": int(df["f_snap_far"].sum())},
        {"item": f"QA: coverage sel < {C.LOW_COVERAGE:.0%} (pantai/batas)", "jumlah": int(df["f_low_coverage"].sum())},
        {"item": "populasi = 0", "jumlah": int(df["f_pop_zero"].sum())},
        {"item": "anak + lansia melebihi populasi (>5%)", "jumlah": int(df["f_age_gt_pop"].sum())},
        {"item": "park_access_500m tidak konsisten dengan jarak", "jumlah": int(df["f_park_access_500m_mismatch"].sum())},
        {"item": "park_access_1000m tidak konsisten dengan jarak", "jumlah": int(df["f_park_access_1000m_mismatch"].sum())},
        {"item": f"LST porsi piksel valid < {C.MIN_LST_VALID_FRAC:.0%}", "jumlah": int(df["f_lst_low_valid"].sum())},
        {"item": "QA remote sensing Agent 1: rs_qa_ok = False (ditandai)", "jumlah": int(df["f_rs_qa"].sum())},
        {"item": "grid valid data Person 2", "jumlah": int(df["valid_p2"].sum())},
        {"item": "grid valid remote sensing", "jumlah": int(df["valid_rs"].sum())},
        {"item": "GRID DIKELUARKAN dari perbandingan", "jumlah": int((~df["valid"]).sum())},
        {"item": "GRID VALID (himpunan pembanding bersama)", "jumlah": int(df["valid"].sum())},
    ]
    t = pd.DataFrame(rows)
    t["persen"] = (100 * t["jumlah"] / max(n, 1)).round(1)
    return t


def build_meta(df: pd.DataFrame, notes: list[str], dummy: bool, unreachable: str) -> dict:
    return {
        "source": "dummy" if dummy else "real",
        "built_at": utc_stamp(),
        "n_grid": int(len(df)),
        "n_valid": int(df["valid"].sum()),
        "valid_share": float(df["valid"].mean()) if len(df) else 0.0,
        "n_valid_rs": int(df["valid_rs"].sum()),
        "n_valid_p2": int(df["valid_p2"].sum()),
        "unreachable_policy": normalize_policy(unreachable),
        "notes": notes,
        **versions(),
    }


def load_features(paths: C.Paths, unreachable: str = "exclude"):
    """Muat semua masukan yang ADA, gabung, bersihkan. Kembalikan (df, meta, status).

    Tidak gagal bila remote sensing belum ada (status P2_ONLY); DataError bila struktur tidak valid.
    """
    status = assess_inputs(paths)
    if status.state == INVALID:
        raise DataError("Masukan tidak valid: " + " | ".join(status.errors))
    grid = read_grid_table(paths.grid)
    rs, rs_notes = load_remote_sensing(paths)
    pop, pop_notes = load_population_inputs(paths)
    master = load_master_attrs(paths)
    if master is None:
        attrs = [a for a in C.MASTER_ATTRS if a in grid.columns]
        master = grid[[C.KEY, *attrs]] if attrs else None
    merged, notes, dummy = merge_inputs(grid[C.KEY], rs, pop, master)
    clean = clean_values(merged, unreachable)
    meta = build_meta(clean, pop_notes + rs_notes + notes, dummy or paths.demo, unreachable)
    meta["input_status"] = status.state
    return clean, meta, status
