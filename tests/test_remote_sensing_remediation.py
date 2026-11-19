"""Audit regression cases: denominators, no support, all nine labels, precision, provenance."""
from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
import rasterio
from rasterio.transform import from_origin
from shapely.geometry import box

ROOT = Path(__file__).resolve().parents[1]


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


agg = load('rs_aggregate', '02b_aggregate_remote_sensing.py')
evidence = load('rs_evidence', '02e_remote_sensing_remediation.py')


def label_raster(tmp_path, values, nodata=255):
    path = tmp_path / 'labels.tif'
    values = np.array(values, dtype='uint8')
    with rasterio.open(path, 'w', driver='GTiff', width=values.shape[1], height=values.shape[0],
                       count=1, dtype='uint8', crs='EPSG:32748', transform=from_origin(0, 20, 10, 10),
                       nodata=nodata) as dst:
        dst.write(values, 1)
        dst.set_band_description(1, 'label_mode')
    return path


def test_partial_labels_use_whole_cell_denominator_and_preserve_conditional(tmp_path):
    path = label_raster(tmp_path, [[1, 6], [255, 255]])
    # Tree 100 m2, built 100 m2, unknown 200 m2; also test fractional pixel overlap.
    grid = gpd.GeoDataFrame({'grid_id': ['full', 'partial']}, geometry=[box(0, 0, 20, 20), box(5, 0, 20, 20)], crs=32748)
    out = agg.aggregate_dw_labels(path, grid)
    assert out.loc['full', 'tree_fraction'] == pytest.approx(.25)
    assert out.loc['full', 'built_fraction'] == pytest.approx(.25)
    assert out.loc['full', 'tree_fraction_valid'] == pytest.approx(.5)
    assert out.loc['partial', 'tree_fraction'] == pytest.approx(50 / 300)
    assert out.loc['partial', 'built_fraction'] == pytest.approx(100 / 300)
    assert out.loc['partial', 'tree_fraction_valid'] == pytest.approx(1 / 3)
    assert np.allclose(out['dw_label_valid_fraction'], .5)
    assert np.allclose(out['dw_label_missing_fraction'], .5)
    assert np.allclose(out[list(agg.DW_FRACTION_COLS)].sum(axis=1), out['dw_label_valid_fraction'])


def test_no_label_support_remains_unknown(tmp_path):
    path = label_raster(tmp_path, [[255, 255]])
    grid = gpd.GeoDataFrame({'grid_id': ['empty']}, geometry=[box(0, 10, 20, 20)], crs=32748)
    out = agg.aggregate_dw_labels(path, grid)
    assert out[list(agg.DW_FRACTION_COLS)].isna().all().all()
    assert out.loc['empty', 'dw_label_valid_fraction'] == 0
    assert out.loc['empty', 'dw_label_missing_fraction'] == 1


def test_all_nine_classes_including_snow_ice_reconcile(tmp_path):
    path = label_raster(tmp_path, [list(range(9))])
    grid = gpd.GeoDataFrame({'grid_id': ['all']}, geometry=[box(0, 10, 90, 20)], crs=32748)
    out = agg.aggregate_dw_labels(path, grid)
    assert out.loc['all', 'snow_ice_fraction'] == pytest.approx(1 / 9)
    assert out[list(agg.DW_FRACTION_COLS)].sum(axis=1).iloc[0] == pytest.approx(1)


@pytest.mark.parametrize('values,nodata', [([[9]], 255), ([[1]], 254)])
def test_bad_labels_or_nodata_rejected(tmp_path, values, nodata):
    path = label_raster(tmp_path, values, nodata)
    grid = gpd.GeoDataFrame({'grid_id': ['bad']}, geometry=[box(0, 10, 10, 20)], crs=32748)
    with pytest.raises(ValueError):
        agg.aggregate_dw_labels(path, grid)


def test_csv_retains_sub_square_metre_area(tmp_path):
    out = pd.DataFrame({'qa_area_m2': [.422884537], 'qa_area_km2': [.422884537 / 1e6], 'lst_mean_c': [42.234]})
    path = tmp_path / 'grid.csv'
    agg.write_grid_csv(out, path)
    saved = pd.read_csv(path)
    assert saved.loc[0, 'qa_area_km2'] > 0
    assert saved.loc[0, 'qa_area_m2'] == pytest.approx(.422884537, abs=1e-12)
    assert saved.loc[0, 'qa_area_km2'] * 1e6 == pytest.approx(.422884537, abs=1e-12)


def test_real_revised_measurements_match_audited_baseline():
    base = pd.read_csv(ROOT / 'data/processed/remote_sensing_grid.csv').set_index('grid_id')
    revised = pd.read_csv(ROOT / 'data/processed/remote_sensing_remediated/remote_sensing_grid.csv').set_index('grid_id')
    pd.testing.assert_frame_equal(base.drop(columns='qa_area_km2'), revised[base.columns].drop(columns='qa_area_km2'))
    assert revised.loc['JKT_R042_C004', 'qa_area_m2'] > 0
    assert revised['qa_area_km2'].gt(0).all()
    assert revised[[*agg.DW_FRACTION_COLS, 'dw_label_missing_fraction']].isna().all().all()
    assert revised['tree_prob_mean'].isna().sum() == 1


def test_target_delivered_with_low_support():
    rs = pd.read_csv(ROOT / 'data/processed/remote_sensing_grid.csv').set_index('grid_id')
    row = rs.loc['JKT_R037_C062']
    assert row['lst_mean_c'] == 42.234 and row['ndvi_mean'] == .2961
    assert .25 < row['lst_valid_fraction'] < .5
    assert 'partial_lst' in row['rs_qa_flags']


def test_revised_csv_gpkg_area_values_and_geometry_agree():
    folder = ROOT / 'data/processed/remote_sensing_remediated'
    df = pd.read_csv(folder / 'remote_sensing_grid.csv').set_index('grid_id')
    g = gpd.read_file(folder / 'remote_sensing_grid.gpkg').set_index('grid_id').loc[df.index]
    original = gpd.read_file(ROOT / 'data/processed/grid_500m_jakarta.gpkg').set_index('grid_id').loc[df.index]
    assert g.geometry.geom_equals(original.geometry).all()
    assert np.allclose(g.geometry.area, df['qa_area_m2'], rtol=1e-12, atol=1e-8)
    for col in ['lst_c', 'ndvi', 'lst_observation_count']:
        assert np.allclose(g[col], df[col], rtol=0, atol=1e-10)


def test_revised_output_accepted_by_jhim_loader():
    import sys
    sys.path.insert(0, str(ROOT))
    from jhim import config, data
    loaded = data.read_input_csv(ROOT / 'data/processed/remote_sensing_remediated/remote_sensing_grid.csv',
                                 config.RS_COLS, 'revised RS')
    assert len(loaded) == 2765
    assert loaded[['lst_c', 'ndvi']].notna().all().all()


def scene_file(tmp_path, date='2024-05-01T00:00:00Z', duplicate=False):
    path = tmp_path / 'scenes.csv'
    row = {'dataset_id': 'LANDSAT/LC09/C02/T1_L2', 'image_id': 'LANDSAT/LC09/C02/T1_L2/test',
           'acquired_at_utc': date, 'wrs_path': '122', 'wrs_row': '064', 'processing_level': 'L2SP', 'recipe_id': 'test'}
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=evidence.SCENE_FIELDS)
        writer.writeheader()
        writer.writerow(row)
        if duplicate:
            writer.writerow(row)
    return path


@pytest.mark.parametrize('date', ['2025-01-01T00:00:00Z', '2023-12-31T23:59:59Z', '2024-01-01'])
def test_scene_manifest_rejects_out_of_period_or_naive_dates(tmp_path, date):
    with pytest.raises(ValueError):
        evidence.validate_scene_manifest(scene_file(tmp_path, date))


def test_scene_manifest_rejects_duplicates(tmp_path):
    with pytest.raises(ValueError):
        evidence.validate_scene_manifest(scene_file(tmp_path, duplicate=True))


def test_scene_date_check_does_not_assert_export_linkage(tmp_path):
    result = evidence.validate_scene_manifest(scene_file(tmp_path))
    assert result['state'] == 'PARTIAL'  # DW collection still absent


def test_empty_scene_inventory_is_blocked(tmp_path):
    path = tmp_path / 'empty.csv'
    path.write_text(','.join(evidence.SCENE_FIELDS) + '\n', encoding='utf-8')
    assert evidence.validate_scene_manifest(path)['state'] == 'BLOCKED'


def test_replay_detects_changed_support_and_values(tmp_path):
    a = label_raster(tmp_path, [[1, 255]])
    b = tmp_path / 'changed.tif'
    b.write_bytes(a.read_bytes())
    with rasterio.open(b, 'r+') as dst:
        dst.write(np.array([[2, 1]], dtype='uint8'), 1)
    result = evidence.compare_rasters(a, b)[0]
    assert result['valid_mask_changed_pixels'] == 1
    assert result['max_abs_difference'] == 1


def test_manifest_detects_changed_content(tmp_path, monkeypatch):
    monkeypatch.setattr(evidence, 'ROOT', tmp_path)
    f = tmp_path / 'input.txt'
    f.write_text('frozen', encoding='utf-8')
    manifest = tmp_path / 'manifest.json'
    manifest.write_text(json.dumps({'files': [{'path': f.name, 'sha256': evidence.sha256(f)}]}), encoding='utf-8')
    assert evidence.verify_manifest(manifest) == 1
    f.write_text('changed', encoding='utf-8')
    with pytest.raises(ValueError, match='hash mismatch'):
        evidence.verify_manifest(manifest)
