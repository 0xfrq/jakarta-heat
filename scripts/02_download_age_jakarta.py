
from pathlib import Path
import geopandas as gpd
import requests
from shapely.geometry import mapping

ROOT = Path(__file__).resolve().parents[1]

BOUNDARY = ROOT / "data/processed/jakarta_5kota.gpkg"
OUTPUT = ROOT / "data/raw/worldpop/age"

OUTPUT.mkdir(parents=True, exist_ok=True)

# Baca batas Jakarta
jakarta = gpd.read_file(BOUNDARY).to_crs("EPSG:4326")

# Gabungkan 5 kota menjadi satu wilayah
geometry = jakarta.geometry.union_all()
geojson = mapping(geometry)

API_URL = "https://api.worldpop.org/v3/raster"

GROUPS = {
    "child": [0, 14],
    "elderly": [65, 90],
}

for group, ages in GROUPS.items():
    print(f"Downloading {group}...")

    payload = {
        "geojson": geojson,
        "year": 2024,
        "layer": "agesex",
        "age_range": ages,
        "sex": "both",
        "bands": "sum",
        "resolution": "100m"
    }

    response = requests.post(
        API_URL,
        json=payload,
        timeout=240
    )

    response.raise_for_status()

    if "tiff" not in response.headers.get(
        "Content-Type", ""
    ).lower():
        raise RuntimeError(
            f"Unexpected API response: {response.text[:500]}"
        )

    path = OUTPUT / f"jakarta_{group}_2024.tif"
    path.write_bytes(response.content)

    print(f"Saved: {path}")
    print(f"Size: {path.stat().st_size / 1e6:.2f} MB")

print("DOWNLOAD COMPLETED!")
