from pathlib import Path
import geopandas as gpd

root = Path(__file__).resolve().parents[1]
path = root / "data/processed/grid_500m_jakarta.gpkg"
grid = gpd.read_file(path)

assert "grid_id" in grid.columns, "Kolom grid_id tidak ada"
assert grid["grid_id"].notna().all(), "Ada grid_id kosong"
assert grid["grid_id"].is_unique, "Ada grid_id duplikat"
assert grid.crs is not None, "CRS grid tidak ada"

print("Jumlah grid:", len(grid))
print("CRS:", grid.crs)
print("Contoh kolom:", list(grid.columns))
print(grid[["grid_id"]].head())