"""Satu-satunya tempat angka tetap dan jalur berkas.

Semua keputusan metodologis (bobot, normalisasi, batas jarak taman) ada di sini dan harus
DIKUNCI sebelum melihat hasil dari data asli (lihat panduan, bagian keputusan).
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

# JHIM_ROOT hanya untuk pengujian: memindahkan semua jalur data/keluaran ke folder lain.
ROOT = Path(os.environ.get("JHIM_ROOT") or Path(__file__).resolve().parents[1])

# ---------------------------------------------------------------- kolom
KEY = "grid_id"
RS_COLS = ("lst_c", "ndvi")
POP_COLS = ("population", "pop_child", "pop_elderly", "park_distance_m", "park_access_500m")
FEATURE_COLS = RS_COLS + POP_COLS
POP_ALIASES = {"pop_sum": "population"}  # nama kolom di file populasi Orang 2 saat ini

# rentang wajar; nilai di luar rentang dikosongkan lalu sel dikeluarkan (gagal lunak)
LST_RANGE_C = (15.0, 60.0)
NDVI_RANGE = (-1.0, 1.0)
AGE_TOLERANCE = 1.05  # (anak + lansia) boleh melebihi populasi paling banyak 5% (+1 jiwa)
MIN_ID_OVERLAP = 0.50  # di bawah ini, grid_id kemungkinan dari versi grid yang berbeda

# ---------------------------------------------------------------- pemodelan
TOP_FRAC = 0.10
NORM_CLIP = (0.05, 0.95)  # normalisasi min-max setelah dipotong pada persentil ke-5 dan ke-95
PARK_CAP_M = 1000.0  # defisit akses taman jenuh (=1) pada jarak >= 1000 m
PARK_THRESHOLDS_M = (500.0, 1000.0)  # ambang untuk uji sensitivitas

# Bobot ditetapkan SEBELUM melihat hasil. Jumlah tiap model = 1.
MODELS: dict[str, dict[str, float]] = {
    "M1": {"lst": 1.0},
    "M2": {"lst": 0.60, "ndvi_low": 0.40},
    "M3": {"lst": 0.40, "ndvi_low": 0.30, "pop": 0.30},
    "M4": {"lst": 0.30, "ndvi_low": 0.20, "vuln": 0.25, "park_deficit": 0.25},
}
MODEL_LABELS = {
    "M1": "M1: LST",
    "M2": "M2: LST + NDVI rendah",
    "M3": "M3: LST + NDVI + populasi",
    "M4": "M4: LST + NDVI + penduduk rentan + akses taman",
}
COMPONENT_LABELS = {
    "lst": "LST",
    "ndvi_low": "NDVI rendah",
    "pop": "Populasi (log)",
    "vuln": "Penduduk rentan 0-14 dan 65+ (log)",
    "park_deficit": "Defisit akses taman",
}

# ---------------------------------------------------------------- sensitivitas dan spasial
WEIGHT_FACTORS = (0.8, 1.2)  # bobot tiap komponen dikali 0,8 dan 1,2 lalu dinormalisasi ulang
STABLE_SHARE = 0.80  # grid disebut stabil bila masuk 10% teratas di >= 80% skenario
LISA_ALPHA = 0.05
PERMUTATIONS = 999
SEED = 42


@dataclass(frozen=True)
class Paths:
    """Jalur berkas. demo=True memakai folder terpisah supaya data dummy tidak bercampur data asli."""

    demo: bool = False
    root: Path = ROOT

    @property
    def grid(self) -> Path:
        return self.root / "data/processed/grid_500m_jakarta.gpkg"

    @property
    def inputs_dir(self) -> Path:
        return self.root / ("data/processed/dummy" if self.demo else "data/processed")

    @property
    def rs(self) -> Path:
        return self.inputs_dir / "remote_sensing_grid.csv"

    @property
    def pop(self) -> Path:
        return self.inputs_dir / "population_accessibility_grid.csv"

    @property
    def pop_parts(self) -> tuple[Path, ...]:
        """Berkas terpisah dari Orang 2 (dipakai bila berkas gabungan di atas tidak ada).

        Semuanya opsional satu per satu; kolom dari berkas yang ada digabung lewat grid_id.
        """
        d = self.inputs_dir
        return (d / "population_grid.csv", d / "vulnerability_grid.csv", d / "park_access_grid.csv")

    @property
    def modeling(self) -> Path:
        return self.root / ("data/processed/modeling_demo" if self.demo else "data/processed/modeling")

    @property
    def tables(self) -> Path:
        return self.root / ("outputs/demo/tables" if self.demo else "outputs/tables")

    @property
    def figures(self) -> Path:
        return self.root / ("outputs/demo/figures" if self.demo else "outputs/figures")

    # berkas hasil
    @property
    def merged(self) -> Path:
        return self.modeling / "merged_grid.csv"

    @property
    def merged_meta(self) -> Path:
        return self.modeling / "merged_meta.json"

    @property
    def priority(self) -> Path:
        return self.modeling / "priority_models.csv"

    @property
    def priority_meta(self) -> Path:
        return self.modeling / "priority_meta.json"
