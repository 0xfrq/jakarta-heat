"""Satu-satunya tempat angka tetap dan jalur berkas.

Semua keputusan metodologis (bobot, normalisasi, batas jarak taman, kelas prioritas) ada di sini.
STATUS: PROVISIONAL. Bobot dan ambang ditetapkan oleh Person 3 / Agent 3 SEBELUM data LST asli
tersedia, tidak diturunkan dari literatur tertentu, dan BELUM disetujui tim. Lihat
`docs/agent3_methods.md` dan uji sensitivitas sebelum menarik kesimpulan.

Jalur dapat dipindah dengan variabel lingkungan:
    JHIM_ROOT       akar repositori (bawaan: folder di atas paket ini)
    JHIM_INPUT_DIR  folder masukan data asli (bawaan: <root>/data/processed)
    JHIM_RS_PATH    berkas remote sensing Agent 1 (bawaan: <input_dir>/remote_sensing_grid.csv)
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

# JHIM_ROOT juga dipakai pengujian: memindahkan semua jalur data/keluaran ke folder lain.
ROOT = Path(os.environ.get("JHIM_ROOT") or Path(__file__).resolve().parents[1])

# ---------------------------------------------------------------- kontrak data
KEY = "grid_id"
EXPECTED_N_GRID = 2765  # master grid 500 m, lima kota daratan (tanpa Kepulauan Seribu)
CRS_PROJECTED = "EPSG:32748"  # WGS 84 / UTM 48S (meter); semua perhitungan jarak/luas
CRS_WEB = "EPSG:4326"  # hanya untuk peta web

# Agent 1 -> data/processed/remote_sensing_grid.csv
RS_COLS = ("lst_c", "ndvi")  # wajib
RS_OPTIONAL = ("lst_unc_k", "lst_obs", "lst_valid_frac", "trees_prob", "built_prob", "rs_pixel_count", "rs_qa_ok")
RS_TEXT = ("rs_qa_flags",)  # kolom teks QA Agent 1 (dibawa apa adanya untuk pelaporan)
# alias nama yang MAKNANYA identik (bukan statistik lain). Nama kanan = nama di
# remote_sensing_grid.csv Agent 1 (scripts/02b_aggregate_remote_sensing.py, commit cdda424):
# rata-rata per grid (tertimbang cakupan piksel) dari nilai per piksel.
RS_ALIASES = {
    "lst_valid": "lst_valid_frac", "lst_valid_share": "lst_valid_frac", "lst_valid_fraction": "lst_valid_frac",
    "lst_unc_mean_k": "lst_unc_k", "lst_observation_count": "lst_obs",
    "tree_prob_mean": "trees_prob", "built_prob_mean": "built_prob",
}

# Person 2 -> data/processed/spatial_features.csv
POP_REQUIRED = ("population", "pop_child", "pop_elderly", "park_distance_m")
POP_OPTIONAL = ("park_reachable", "park_access_500m", "park_access_1000m", "grid_snap_m")
POP_COLS = POP_REQUIRED + ("park_access_500m",)  # kompatibilitas nama lama
POP_ALIASES = {"pop_sum": "population", "child_sum": "pop_child", "elderly_sum": "pop_elderly"}
MASTER_ATTRS = ("kota", "area_km2", "coverage_ratio")

FEATURE_COLS = RS_COLS + POP_REQUIRED + ("park_access_500m",)

# rentang wajar; nilai di luar rentang dikosongkan lalu sel dikeluarkan (gagal lunak)
LST_RANGE_C = (15.0, 60.0)  # LST permukaan (bukan suhu udara); piksel maks QA Agent 1 = 56.9 C
NDVI_RANGE = (-1.0, 1.0)
PROB_RANGE = (0.0, 1.0)
AGE_TOLERANCE = 1.05  # (anak + lansia) boleh melebihi populasi paling banyak 5% (+1 jiwa)
MIN_ID_OVERLAP = 0.50  # di bawah ini, grid_id kemungkinan dari versi grid yang berbeda
MIN_LST_VALID_FRAC = 0.50  # bila kolom lst_valid_frac ada: grid < 50% piksel valid dikeluarkan
MIN_VALID_SHARE = 0.70  # pipeline resmi menolak berjalan bila grid valid < 70% (kecuali --force)

# QA Person 2
SNAP_QA_M = 250.0  # jarak snap titik grid ke jaringan > 250 m ditandai
LOW_COVERAGE = 0.10  # sel dengan < 10% luas di daratan Jakarta ditandai (pantai/batas)

# ---------------------------------------------------------------- pemodelan
TOP_FRAC = 0.10
TOP_FRACS = (0.05, 0.10, 0.20)  # ambang alternatif untuk overlap/sensitivitas
# kelas prioritas berbasis peringkat (bagian kumulatif dari grid valid), PROVISIONAL
CLASS_CUTOFFS = (0.10, 0.25, 0.50)
CLASS_LABELS = ("1 Sangat tinggi (top 10%)", "2 Tinggi (10-25%)", "3 Sedang (25-50%)", "4 Rendah (50-100%)")
NORM_CLIP = (0.05, 0.95)  # normalisasi min-max setelah dipotong pada persentil ke-5 dan ke-95
PARK_CAP_M = 1000.0  # defisit akses taman jenuh (=1) pada jarak >= 1000 m
PARK_THRESHOLDS_M = (500.0, 1000.0)  # ambang biner untuk uji sensitivitas
PARK_CAPS_ALT_M = (750.0, 1500.0)  # batas jenuh alternatif untuk uji sensitivitas
# Kebijakan jarak taman yang tidak terhitung (park_distance_m kosong = rute TIDAK dihitung):
#   exclude (BASELINE): grid dikeluarkan dari himpunan pembanding; tidak ada nilai buatan.
#   worst  (sensitivitas): diperlakukan sebagai defisit maksimum (= PARK_CAP_M).
#   median (sensitivitas): diisi median jarak teramati (netral).
UNREACHABLE_POLICIES = ("exclude", "worst", "median")
UNREACHABLE_ALIASES = {"cap": "worst"}

# Bobot ditetapkan SEBELUM melihat hasil. Jumlah tiap model = 1. PROVISIONAL.
MODELS: dict[str, dict[str, float]] = {
    "M1": {"lst": 1.0},
    "M2": {"lst": 0.60, "ndvi_low": 0.40},
    "M3": {"lst": 0.40, "ndvi_low": 0.30, "pop": 0.30},
    "M4": {"lst": 0.30, "ndvi_low": 0.20, "vuln": 0.25, "park_deficit": 0.25},
}
WEIGHTS_STATUS = (
    "PROVISIONAL: bobot ditetapkan Person 3 sebelum data LST asli tersedia; bukan dari literatur "
    "spesifik dan belum disepakati tim. Hasil wajib dibaca bersama uji sensitivitas."
)
MODEL_LABELS = {
    "M1": "M1: LST",
    "M2": "M2: LST + NDVI rendah",
    "M3": "M3: LST + NDVI + populasi",
    "M4": "M4: LST + NDVI + hitungan usia + proksi taman kandidat",
}
MODEL_FORMULAS = {
    "M1": "S1 = n(LST)",
    "M2": "S2 = 0.60 n(LST) + 0.40 [1 - n(NDVI)]",
    "M3": "S3 = 0.40 n(LST) + 0.30 [1 - n(NDVI)] + 0.30 n(log1p(populasi))",
    "M4": "S4 = 0.30 n(LST) + 0.20 [1 - n(NDVI)] + 0.25 n(log1p(anak 0-14 + lansia 65+)) "
          "+ 0.25 min(jarak_taman, 1000)/1000",
}
COMPONENT_LABELS = {
    "lst": "LST (suhu permukaan)",
    "ndvi_low": "NDVI rendah",
    "pop": "Populasi (log1p jumlah)",
    "pop_density": "Kepadatan populasi (log1p jiwa/km2)",
    "vuln": "Penduduk rentan 0-14 dan 65+ (log1p jumlah)",
    "vuln_share": "Porsi penduduk rentan",
    "park_deficit": "Defisit akses taman (jarak jaringan)",
    "trees_low": "Probabilitas pohon rendah (Dynamic World)",
}

# ---------------------------------------------------------------- sensitivitas dan spasial
WEIGHT_FACTORS = (0.8, 1.2)  # bobot tiap komponen dikali 0,8 dan 1,2 lalu dinormalisasi ulang
STABLE_SHARE = 0.80  # grid disebut stabil bila masuk 10% teratas di >= 80% skenario
LISA_ALPHA = 0.05
PERMUTATIONS = 999
SEED = 42
SPATIAL_WEIGHTS = ("queen", "rook", "knn8")  # baseline: queen (lihat docs/agent3_methods.md)


def _env_path(name: str) -> Path | None:
    v = os.environ.get(name)
    return Path(v) if v else None


@dataclass(frozen=True)
class Paths:
    """Jalur berkas. demo=True memakai folder terpisah supaya data dummy tidak bercampur data asli."""

    demo: bool = False
    root: Path = field(default_factory=lambda: ROOT)

    # ---- masukan
    @property
    def processed(self) -> Path:
        return self.root / "data/processed"

    @property
    def grid(self) -> Path:
        return self.processed / "grid_500m_jakarta.gpkg"

    @property
    def boundary(self) -> Path:
        return self.processed / "jakarta_5kota.gpkg"

    @property
    def grid_master(self) -> Path:
        return self.processed / "grid_master.csv"

    @property
    def inputs_dir(self) -> Path:
        if self.demo:
            return self.processed / "dummy"
        return _env_path("JHIM_INPUT_DIR") or self.processed

    @property
    def rs(self) -> Path:
        if not self.demo and _env_path("JHIM_RS_PATH"):
            return _env_path("JHIM_RS_PATH")
        revised = self.inputs_dir / "remote_sensing_remediated/remote_sensing_grid.csv"
        if not self.demo and revised.exists():
            return revised
        return self.inputs_dir / "remote_sensing_grid.csv"

    @property
    def spatial_features(self) -> Path:
        """Berkas integrasi Person 2 (utama)."""
        return self.inputs_dir / "spatial_features.csv"

    @property
    def demographic_support(self) -> Path:
        if self.demo:
            return self.inputs_dir / "demographic_support.csv"
        return _env_path("JHIM_DEMOGRAPHIC_SUPPORT") or self.inputs_dir / "demographic_support.csv"

    @property
    def demographic_corrected(self) -> Path:
        if self.demo:
            return self.inputs_dir / "demographic_features_corrected.csv"
        return _env_path("JHIM_DEMOGRAPHIC_CORRECTED") or self.inputs_dir / "demographic_features_corrected.csv"

    @property
    def pop(self) -> Path:
        """Format gabungan lama (dipakai data dummy)."""
        return self.inputs_dir / "population_accessibility_grid.csv"

    @property
    def pop_parts(self) -> tuple[Path, ...]:
        d = self.inputs_dir
        return (d / "population_grid.csv", d / "vulnerability_grid.csv", d / "accessibility_grid.csv")

    # ---- keluaran
    @property
    def modeling(self) -> Path:
        return self.root / ("data/processed/modeling_demo" if self.demo else "data/processed/modeling")

    @property
    def tables(self) -> Path:
        return self.root / ("outputs/demo/tables" if self.demo else "outputs/tables")

    @property
    def figures(self) -> Path:
        return self.root / ("outputs/demo/figures" if self.demo else "outputs/figures")

    @property
    def gis(self) -> Path:
        return self.root / ("outputs/demo/gis" if self.demo else "outputs/gis")

    @property
    def qa(self) -> Path:
        """Keluaran QA/deskriptif dari data Person 2 (bukan hasil model)."""
        return self.root / ("outputs/demo/qa" if self.demo else "outputs/qa/agent3")

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

    @property
    def manifest(self) -> Path:
        return self.modeling / "run_manifest.json"


def config_snapshot() -> dict:
    """Semua parameter metodologis (untuk manifest/provenance)."""
    return {
        "models": MODELS,
        "weights_status": WEIGHTS_STATUS,
        "model_formulas": MODEL_FORMULAS,
        "norm_clip": list(NORM_CLIP),
        "park_cap_m": PARK_CAP_M,
        "park_thresholds_m": list(PARK_THRESHOLDS_M),
        "park_caps_alt_m": list(PARK_CAPS_ALT_M),
        "top_frac": TOP_FRAC,
        "top_fracs": list(TOP_FRACS),
        "class_cutoffs": list(CLASS_CUTOFFS),
        "lst_range_c": list(LST_RANGE_C),
        "ndvi_range": list(NDVI_RANGE),
        "min_lst_valid_frac": MIN_LST_VALID_FRAC,
        "snap_qa_m": SNAP_QA_M,
        "low_coverage": LOW_COVERAGE,
        "age_tolerance": AGE_TOLERANCE,
        "weight_factors": list(WEIGHT_FACTORS),
        "stable_share": STABLE_SHARE,
        "lisa_alpha": LISA_ALPHA,
        "permutations": PERMUTATIONS,
        "seed": SEED,
        "spatial_weights_baseline": "queen",
        "local_alternative": "directed",
        "global_alternative": "greater",
        "multiple_testing_family": "each preselected map separately; non-island eligible grids",
    }


@dataclass(frozen=True)
class RemediationPaths(Paths):
    """Separate candidate outputs; audited baseline directories are never overwritten."""
    @property
    def modeling(self):
        return self.processed / "modeling_remediation"

    @property
    def tables(self):
        return self.root / "outputs/remediation/tables"

    @property
    def figures(self):
        return self.root / "outputs/remediation/figures"

    @property
    def gis(self):
        return self.root / "outputs/remediation/gis"

    @property
    def qa(self):
        return self.root / "outputs/remediation/qa"
