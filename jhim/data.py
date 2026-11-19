"""Baca, validasi, gabung, dan bersihkan data per grid (Job 4A dan awal 6A).

Prinsip: kesalahan STRUKTUR menghentikan proses (DataError); nilai buruk dikosongkan,
diberi bendera, dan sel dikeluarkan dari perbandingan serta dilaporkan.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from . import config as C
from .util import DataError, utc_stamp, versions


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


# ---------------------------------------------------------------- baca
def read_grid_table(path) -> pd.DataFrame:
    """Kembalikan DataFrame [grid_id, x, y] (titik tengah dalam meter, EPSG:32748).

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
        return _check_key(df[[C.KEY, "x", "y"]], "grid")
    g = read_grid_gdf(p)
    ctr = g.to_crs("EPSG:32748").geometry.centroid
    out = pd.DataFrame({C.KEY: g[C.KEY].to_numpy(), "x": ctr.x.to_numpy(), "y": ctr.y.to_numpy()})
    return _check_key(out, "grid")


def read_grid_gdf(path):
    """Baca master grid sebagai GeoDataFrame [grid_id, geometry] (kolom geometri dinamai 'geometry').

    Memilih layer pertama di .gpkg yang PUNYA geometri dan kolom grid_id; menolak bila CRS tidak ada.
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
        try:
            import fiona

            names = list(fiona.listlayers(str(p)))
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
        out = g[[C.KEY, "geometry"]].copy()
        out[C.KEY] = norm_ids(out[C.KEY])
        return out.reset_index(drop=True)
    raise DataError("Tidak ada layer grid yang punya geometri dan kolom grid_id. Layer yang ditemukan: " + "; ".join(seen))


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


def load_population_inputs(paths) -> tuple[pd.DataFrame, list[str]]:
    """Muat data penduduk dan akses taman dari Orang 2.

    1. Bila population_accessibility_grid.csv ada, itu yang dipakai (satu berkas lengkap).
    2. Bila tidak, berkas terpisah digabung lewat grid_id: population_grid.csv (grid_id, pop_sum),
       vulnerability_grid.csv (grid_id, pop_child, pop_elderly), park_access_grid.csv
       (grid_id, park_distance_m, park_access_500m). Berkas yang belum ada dilewati; bila kolom wajib
       masih kurang, DataError menyebut kolom dan berkas yang kurang.
    Grid yang ada di satu berkas tetapi tidak di berkas lain tetap masuk dengan nilai kosong
    (nanti dikeluarkan sebagai tidak valid; tidak pernah diisi 0).
    """
    notes: list[str] = []
    if paths.pop.exists():
        return read_input_csv(paths.pop, C.POP_COLS, paths.pop.name, aliases=C.POP_ALIASES), notes

    found = [p for p in paths.pop_parts if p.exists()]
    if not found:
        names = ", ".join(p.name for p in (paths.pop, *paths.pop_parts))
        raise DataError(f"Data Orang 2 tidak ditemukan di {paths.inputs_dir}. Harus ada salah satu dari: {names}")
    merged = None
    for p in found:
        d = read_input_csv(p, (), p.name, aliases=C.POP_ALIASES)
        clash = [c for c in d.columns if c != C.KEY and merged is not None and c in merged.columns]
        if clash:
            raise DataError(f"{p.name}: kolom {clash} sudah ada di berkas lain; satu kolom hanya boleh di satu berkas.")
        notes.append(f"{p.name}: {len(d):,} baris, kolom {[c for c in d.columns if c != C.KEY]}")
        merged = d if merged is None else merged.merge(d, on=C.KEY, how="outer", validate="one_to_one")
    miss = [c for c in C.POP_COLS if c not in merged.columns]
    if miss:
        have = ", ".join(p.name for p in found)
        raise DataError(
            f"Data Orang 2 belum lengkap. Kolom yang masih kurang: {miss}. Berkas yang terbaca: {have}. "
            "Letakkan kolom itu di berkas yang sesuai (park_access_grid.csv untuk jarak taman) atau di "
            "population_accessibility_grid.csv."
        )
    return merged, notes


# ---------------------------------------------------------------- gabung
def merge_inputs(ids: pd.Series, rs: pd.DataFrame, pop: pd.DataFrame):
    """Gabungkan ke master grid (left join, satu-ke-satu). Kembalikan (DataFrame, catatan, dummy)."""
    base = _check_key(pd.DataFrame({C.KEY: ids.to_numpy()}), "master grid")
    notes: list[str] = []
    dummy = False
    parts = []
    for name, d, cols in (("remote_sensing", rs, C.RS_COLS), ("population_accessibility", pop, C.POP_COLS)):
        if "is_dummy" in d.columns and pd.to_numeric(d["is_dummy"], errors="coerce").fillna(0).astype(bool).any():
            dummy = True
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
        extra_cols = [c for c in d.columns if c not in (C.KEY, "is_dummy", *cols)]
        if extra_cols:
            notes.append(f"{name}: kolom tidak dipakai diabaikan: {extra_cols}")
        parts.append(d[[C.KEY, *[c for c in cols if c in d.columns]]])
    out = base.merge(parts[0], on=C.KEY, how="left", validate="one_to_one")
    out = out.merge(parts[1], on=C.KEY, how="left", validate="one_to_one")
    if len(out) != len(base):
        raise DataError("Penggabungan menggandakan atau menghilangkan grid (tidak boleh terjadi).")
    for c in C.FEATURE_COLS:
        if c not in out.columns:
            out[c] = np.nan
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


def clean_values(df: pd.DataFrame, unreachable: str = "exclude") -> pd.DataFrame:
    """Ubah ke numerik, kosongkan nilai tidak wajar, beri bendera, hitung kolom `valid`.

    unreachable: perlakuan park_distance_m kosong (taman tak terjangkau jaringan jalan kaki)
        "exclude": sel dikeluarkan dari perbandingan (bawaan; paling hati-hati)
        "cap":     jarak diisi PARK_CAP_M (defisit akses maksimum) dan diberi bendera
    Nol TIDAK PERNAH dipakai untuk mengisi nilai kosong.
    """
    if unreachable not in ("exclude", "cap"):
        raise ValueError("unreachable harus 'exclude' atau 'cap'")
    out = df.copy()
    for c in C.FEATURE_COLS:
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

    out["f_park_unreachable"] = False
    if unreachable == "cap":
        un = out["park_distance_m"].isna()
        out.loc[un, "park_distance_m"] = C.PARK_CAP_M
        out["f_park_unreachable"] = un

    age = out["pop_child"] + out["pop_elderly"]
    out["f_age_gt_pop"] = (age > out["population"] * C.AGE_TOLERANCE + 1).fillna(False)
    acc = out["park_access_500m"]
    out["f_access_not_binary"] = (acc.notna() & ~acc.isin([0, 1]))
    out.loc[out["f_access_not_binary"], "park_access_500m"] = np.nan
    both = out["park_access_500m"].notna() & out["park_distance_m"].notna()
    out["f_access_mismatch"] = both & ((out["park_distance_m"] <= 500).astype(float) != out["park_access_500m"])

    need = ["lst_c", "ndvi", "population", "pop_child", "pop_elderly", "park_distance_m"]
    out["valid"] = out[need].notna().all(axis=1) & ~out["f_age_gt_pop"]
    return out


def quality_table(df: pd.DataFrame) -> pd.DataFrame:
    """Ringkasan: berapa sel kosong/tidak wajar per variabel dan berapa yang dikeluarkan."""
    n = len(df)
    rows = []
    for col in ("lst_c", "ndvi", "population", "pop_child", "pop_elderly", "park_distance_m"):
        rows.append({"item": f"{col} kosong", "jumlah": int(df[f"f_{col}_missing"].sum())})
        if df[f"f_{col}_range"].any():
            rows.append({"item": f"{col} di luar rentang (dikosongkan)", "jumlah": int(df[f"f_{col}_range"].sum())})
    if df["f_park_unreachable"].any():
        rows.append({"item": "park_distance_m kosong diisi batas (opsi cap)", "jumlah": int(df["f_park_unreachable"].sum())})
    rows.append({"item": "anak + lansia melebihi populasi (>5%)", "jumlah": int(df["f_age_gt_pop"].sum())})
    rows.append({"item": "info: park_access_500m tidak konsisten dengan jarak", "jumlah": int(df["f_access_mismatch"].sum())})
    rows.append({"item": "GRID DIKELUARKAN dari perbandingan", "jumlah": int((~df["valid"]).sum())})
    rows.append({"item": "GRID VALID", "jumlah": int(df["valid"].sum())})
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
        "unreachable_policy": unreachable,
        "notes": notes,
        **versions(),
    }
