from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import requests
from shapely.geometry import box

API_URL = "https://www.geoboundaries.org/api/current/gbOpen/IDN/ADM2/"
CRS_METER = "EPSG:32748"  # UTM zone 48 South (Jakarta), units: meters
CELL_SIZE = 500
CITY_PATTERN = r"\bJakarta\s+(?:Barat|Pusat|Selatan|Timur|Utara)\b"


def create_master_grid(root: Path, input_geojson: Path | None = None) -> None:
    raw = root / "data" / "raw"
    processed = root / "data" / "processed"
    maps = root / "outputs" / "maps"
    for directory in (raw, processed, maps):
        directory.mkdir(parents=True, exist_ok=True)

    if input_geojson is None:
        print("[1/7] Downloading official source metadata...")
        response = requests.get(API_URL, timeout=60)
        response.raise_for_status()
        metadata = response.json()
        source_url = metadata.get("gjDownloadURL")
        if not source_url:
            raise RuntimeError("Metadata has no 'gjDownloadURL' field")
        (raw / "metadata_source.json").write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        input_geojson = raw / "idn_adm2.geojson"
        if not input_geojson.exists():
            print("      Downloading ADM2 GeoJSON (this may take a moment)...")
            with requests.get(source_url, timeout=180, stream=True) as source:
                source.raise_for_status()
                with input_geojson.open("wb") as f:
                    for chunk in source.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)
    else:
        print("[1/7] Using local ADM2 file:", input_geojson)
        if not input_geojson.is_file():
            raise FileNotFoundError(input_geojson)

    print("[2/7] Reading province-wide ADM2 boundaries...")
    adm2 = gpd.read_file(input_geojson)
    if "shapeName" not in adm2.columns:
        raise ValueError(f"Expected 'shapeName' column, found: {list(adm2.columns)}")
    if adm2.crs is None:
        raise ValueError("Source CRS is missing. Do not assign coordinates arbitrarily.")

    city_mask = adm2["shapeName"].fillna("").str.contains(
        CITY_PATTERN, case=False, regex=True
    )
    jakarta = adm2.loc[city_mask, ["shapeName", "geometry"]].copy()
    jakarta = jakarta.rename(columns={"shapeName": "kota"})
    print("      Found cities:", sorted(jakarta["kota"].tolist()))
    if len(jakarta) != 5:
        matches = adm2.loc[
            adm2["shapeName"].fillna("").str.contains("Jakarta", case=False),
            "shapeName",
        ].tolist()
        raise ValueError(
            f"Expected exactly 5 Jakarta city polygons, got {len(jakarta)}. "
            f"Check name differences: {matches}"
        )

    print("[3/7] Reprojecting to metric CRS EPSG:32748...")
    jakarta = jakarta.to_crs(CRS_METER)
    if not jakarta.geometry.is_valid.all():
        print("      Fixing invalid boundary geometries...")
        jakarta["geometry"] = jakarta.geometry.buffer(0)
    if jakarta.geometry.is_empty.any():
        raise ValueError("Some city boundaries are empty after repairing geometry")

    jakarta = jakarta.reset_index(drop=True)
    boundary = jakarta.geometry.union_all()
    minx, miny, maxx, maxy = boundary.bounds
    x0 = math.floor(minx / CELL_SIZE) * CELL_SIZE
    y0 = math.floor(miny / CELL_SIZE) * CELL_SIZE
    nx = math.ceil((maxx - x0) / CELL_SIZE)
    ny = math.ceil((maxy - y0) / CELL_SIZE)

    print(f"[4/7] Creating {CELL_SIZE} m grid ({nx} columns x {ny} rows)...")
    records = []
    for row in range(ny):
        y = y0 + row * CELL_SIZE
        for col in range(nx):
            x = x0 + col * CELL_SIZE
            records.append(
                {
                    "grid_id": f"JKT_R{row:03d}_C{col:03d}",
                    "geometry": box(x, y, x + CELL_SIZE, y + CELL_SIZE),
                }
            )
    grid = gpd.GeoDataFrame(records, geometry="geometry", crs=CRS_METER)
    grid = gpd.clip(grid, boundary, keep_geom_type=True)
    grid = grid.loc[(~grid.geometry.is_empty) & (grid.area > 0)].copy()
    grid = grid.sort_values("grid_id").reset_index(drop=True)
    if grid.empty or grid.grid_id.duplicated().any():
        raise ValueError("Master grid is empty or contains duplicate grid IDs")

    print("[5/7] Assigning city with largest area overlap...")
    # Assign border cells to whichever city occupies the largest part of the cell.
    intersections = gpd.overlay(
        grid[["grid_id", "geometry"]],
        jakarta[["kota", "geometry"]],
        how="intersection",
        keep_geom_type=True,
    )
    intersections["overlap_m2"] = intersections.geometry.area
    owners = (
        intersections.sort_values("overlap_m2", ascending=False)
        .drop_duplicates("grid_id")
        .set_index("grid_id")["kota"]
    )
    grid["kota"] = grid.grid_id.map(owners)
    if grid.kota.isna().any():
        raise ValueError("Some cells have no city assignment")

    grid["area_km2"] = grid.geometry.area / 1_000_000.0
    grid["coverage_ratio"] = grid.geometry.area / (CELL_SIZE * CELL_SIZE)
    # representative_point is always inside the clipped polygon; useful for display.
    rep = gpd.GeoSeries(grid.geometry.representative_point(), crs=CRS_METER).to_crs(4326)
    grid["longitude"] = rep.x
    grid["latitude"] = rep.y

    print("[6/7] Validating and exporting...")
    if not (grid["coverage_ratio"].between(0, 1.000001)).all():
        raise ValueError("Invalid coverage ratio")
    if not grid.geometry.is_valid.all():
        raise ValueError("Some grid geometries are invalid")
    total_boundary_km2 = boundary.area / 1_000_000
    total_grid_km2 = grid["area_km2"].sum()
    if abs(total_grid_km2 - total_boundary_km2) > max(0.1, total_boundary_km2 * 0.005):
        raise ValueError(
            f"Grid coverage does not match selected boundary: "
            f"{total_grid_km2:.2f} vs {total_boundary_km2:.2f} km2"
        )

    # Files in EPSG:32748 are for GIS/raster aggregation.
    jakarta.to_file(processed / "jakarta_5kota.gpkg", driver="GPKG")
    grid.to_file(processed / "grid_500m_jakarta.gpkg", driver="GPKG")
    # GeoJSON in EPSG:4326 is suitable for Folium/Streamlit visualization.
    grid.to_crs(4326).to_file(processed / "grid_500m_jakarta.geojson", driver="GeoJSON")
    grid.drop(columns="geometry").to_csv(
        processed / "grid_master.csv", index=False
    )

    print("[7/7] Creating validation preview...")
    fig, ax = plt.subplots(figsize=(9, 9))
    grid.plot(ax=ax, color="#d9e9f7", edgecolor="#6c8daa", linewidth=0.12)
    jakarta.boundary.plot(ax=ax, edgecolor="#112d46", linewidth=1.0)
    ax.set_title("Jakarta — 500 m Master Grid (5 administrative cities)")
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(maps / "preview_master_grid.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    print("\nSUCCESS")
    print(f"Grid cells: {len(grid):,}")
    print(f"Boundary area: {total_boundary_km2:,.2f} km2")
    print(f"Grid area (clipped): {total_grid_km2:,.2f} km2")
    print("CRS of GeoPackage: EPSG:32748")
    print("CRS of GeoJSON: EPSG:4326")
    print("Cities:", grid.kota.value_counts().to_dict())
    print("Output directory:", processed.resolve())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create Jakarta master grid")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Project root")
    parser.add_argument("--input-geojson", type=Path, default=None)
    args = parser.parse_args()
    create_master_grid(args.root, args.input_geojson)
