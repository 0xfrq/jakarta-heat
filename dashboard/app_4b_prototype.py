"""Job 4B: prototype dashboard dengan DATA ASLI dari Orang 2 (populasi + kelompok rentan).

Jalankan:  python -m streamlit run dashboard/app_4b_prototype.py
Membaca:
    data/processed/grid_500m_jakarta.gpkg      master grid (geometri + grid_id)
    data/processed/population_grid.csv         kolom: grid_id, pop_sum
    data/processed/vulnerability_grid.csv      kolom: grid_id, pop_child, pop_elderly
Belum ada LST, NDVI, atau akses taman, jadi belum ada skor prioritas. Dashboard final (app.py)
menampilkan skor setelah 03_prepare_model.py --merge dan 04_priority_model.py dijalankan.
"""
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
GRID_PATH = ROOT / "data/processed/grid_500m_jakarta.gpkg"
POP_PATH = ROOT / "data/processed/population_grid.csv"
VULN_PATH = ROOT / "data/processed/vulnerability_grid.csv"


def norm_id(s):
    return s.astype(str).str.strip()


def join_population(grid, pop):
    """Gabungkan pop_sum ke master grid (left join, satu-ke-satu). Kembalikan (tabel, ringkasan)."""
    if "grid_id" not in grid.columns:
        raise ValueError(f"Master grid tidak punya kolom grid_id. Kolom: {list(grid.columns)}")
    for c in ("grid_id", "pop_sum"):
        if c not in pop.columns:
            raise ValueError(f"population_grid.csv tidak punya kolom {c}. Kolom: {list(pop.columns)}")
    grid = grid.copy()
    grid["grid_id"] = norm_id(grid["grid_id"])
    if grid["grid_id"].duplicated().any():
        raise ValueError("Master grid: grid_id duplikat.")
    pop = pop[["grid_id", "pop_sum"]].copy()
    pop["grid_id"] = norm_id(pop["grid_id"])
    if pop["grid_id"].duplicated().any():
        raise ValueError("population_grid.csv: grid_id duplikat.")
    pop["pop_sum"] = pd.to_numeric(pop["pop_sum"], errors="coerce")
    out = grid.merge(pop, on="grid_id", how="left", validate="one_to_one")
    summary = {
        "n_grid": int(len(out)),
        "n_with_pop": int(out["pop_sum"].notna().sum()),
        "n_without_pop": int(out["pop_sum"].isna().sum()),
        "n_pop_rows_not_in_grid": int((~pop["grid_id"].isin(grid["grid_id"])).sum()),
        "n_negative": int((out["pop_sum"] < 0).sum()),
        "total_pop": float(out["pop_sum"].sum()),
    }
    return out, summary


def join_vulnerability(df, vuln):
    """Gabungkan pop_child dan pop_elderly (left join, satu-ke-satu); hitung kolom turunan. Kembalikan (tabel, ringkasan)."""
    for c in ("grid_id", "pop_child", "pop_elderly"):
        if c not in vuln.columns:
            raise ValueError(f"vulnerability_grid.csv tidak punya kolom {c}. Kolom: {list(vuln.columns)}")
    vuln = vuln[["grid_id", "pop_child", "pop_elderly"]].copy()
    vuln["grid_id"] = norm_id(vuln["grid_id"])
    if vuln["grid_id"].duplicated().any():
        raise ValueError("vulnerability_grid.csv: grid_id duplikat.")
    for c in ("pop_child", "pop_elderly"):
        vuln[c] = pd.to_numeric(vuln[c], errors="coerce")
    out = df.merge(vuln, on="grid_id", how="left", validate="one_to_one")
    out["pop_vulnerable"] = out["pop_child"] + out["pop_elderly"]
    out["share_vulnerable"] = out["pop_vulnerable"] / out["pop_sum"].where(out["pop_sum"] > 0)
    summary = {
        "n_with_vuln": int(out["pop_vulnerable"].notna().sum()),
        "n_vuln_rows_not_in_grid": int((~vuln["grid_id"].isin(df["grid_id"])).sum()),
        "n_vuln_without_pop": int((out["pop_vulnerable"].notna() & out["pop_sum"].isna()).sum()),
        "n_age_gt_pop": int((out["pop_vulnerable"] > out["pop_sum"] * 1.05 + 1).sum()),
        "total_vulnerable": float(out["pop_vulnerable"].sum()),
    }
    return out, summary


def ramp(v):
    """0..1 -> warna hex (kuning ke merah); NaN -> abu-abu."""
    if pd.isna(v):
        return "#cccccc"
    v = min(max(float(v), 0.0), 1.0)
    return f"#{255:02x}{int(235 - 200 * v):02x}{int(120 - 100 * v):02x}"


def main():
    st.set_page_config(page_title="Jakarta Heat Inequality", layout="wide")
    st.title("Jakarta Heat Inequality Mapper")
    st.info("Data asli dari Orang 2 (belum divalidasi). Belum ada skor prioritas: LST, NDVI, dan akses taman belum masuk.")

    try:
        grid = gpd.read_file(GRID_PATH)
    except Exception as exc:
        st.error(f"Master grid tidak bisa dibaca: {GRID_PATH}\n\n{exc}")
        st.stop()
    try:
        gname = grid.geometry.name  # nama kolom geometri yang sebenarnya
    except (AttributeError, TypeError):
        st.error("Layer yang terbaca tidak punya geometri (mungkin layer lain di .gpkg, atau bukan berkas grid). "
                 f"Kolom yang terbaca: {list(grid.columns)}")
        st.stop()
    try:
        pop = pd.read_csv(POP_PATH, dtype={"grid_id": str})
        grid, s = join_population(grid, pop)
        vuln = pd.read_csv(VULN_PATH, dtype={"grid_id": str})
        grid, v = join_vulnerability(grid, vuln)
    except (OSError, ValueError) as exc:
        st.error(f"Data Orang 2 bermasalah: {exc}")
        st.stop()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Jumlah grid (master)", f"{s['n_grid']:,}")
    c2.metric("Grid punya pop_sum", f"{s['n_with_pop']:,}")
    c3.metric("Grid punya data rentan", f"{v['n_with_vuln']:,}")
    c4.metric("Total pop_sum", f"{s['total_pop']:,.0f}")
    st.caption(f"Penduduk rentan (0-14 dan 65+) total: {v['total_vulnerable']:,.0f}")
    if s["n_pop_rows_not_in_grid"]:
        st.warning(f"{s['n_pop_rows_not_in_grid']:,} baris di population_grid.csv tidak ada di master grid (diabaikan).")
    if v["n_vuln_rows_not_in_grid"]:
        st.warning(f"{v['n_vuln_rows_not_in_grid']:,} baris di vulnerability_grid.csv tidak ada di master grid (diabaikan).")
    if v["n_vuln_without_pop"]:
        st.warning(f"{v['n_vuln_without_pop']:,} grid punya data rentan tetapi tidak punya pop_sum (tidak bisa dicek silang).")
    if v["n_age_gt_pop"]:
        st.warning(f"{v['n_age_gt_pop']:,} grid punya anak + lansia melebihi pop_sum lebih dari 5%. Tanyakan ke Orang 2.")
    if s["n_negative"]:
        st.warning(f"{s['n_negative']:,} grid punya pop_sum negatif.")
    st.caption("Grid yang tidak ada di salah satu berkas bukan berarti 0 penduduk. Tanyakan ke Orang 2 apakah baris "
               "yang tidak ada berarti laut/di luar raster atau memang nol.")

    st.write("Preview atribut master grid")
    st.dataframe(pd.DataFrame(grid.drop(columns=gname)).head(20))
    st.write("Sepuluh grid dengan penduduk rentan terbesar")
    st.dataframe(pd.DataFrame(grid.drop(columns=gname)).nlargest(10, "pop_vulnerable")
                 [["grid_id", "pop_sum", "pop_child", "pop_elderly", "pop_vulnerable"]])

    layers = {
        "pop_sum (peringkat persentil)": "pop_sum",
        "Anak 0-14 (peringkat persentil)": "pop_child",
        "Lansia 65+ (peringkat persentil)": "pop_elderly",
        "Penduduk rentan (peringkat persentil)": "pop_vulnerable",
        "Porsi rentan terhadap pop_sum (peringkat persentil)": "share_vulnerable",
    }
    layer = st.selectbox("Warnai titik dengan", list(layers))
    pts = grid.to_crs("EPSG:32748").copy()
    pts[gname] = pts.geometry.representative_point()
    pts = pts.to_crs("EPSG:4326")
    pts["lat"] = pts.geometry.y
    pts["lon"] = pts.geometry.x
    values = pts[layers[layer]].rank(pct=True)
    pts["color"] = [ramp(x) for x in values]
    st.map(pts[["lat", "lon", "color"]], latitude="lat", longitude="lon", color="color", size=120)
    st.caption("Titik abu-abu = nilai tidak tersedia. Warna menunjukkan peringkat persentil, bukan nilai absolut.")


if __name__ == "__main__":
    main()
