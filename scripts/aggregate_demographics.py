"""DM-01: raster-to-grid aggregation with source masks, no empty-sum zeros.

Offline and portable: all three source paths are explicit. Default estimand is
the documented historical QGIS hybrid; fractional allocation is a sensitivity.
Neither writes the original QGIS CSVs or modifies raster inputs.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import geopandas as gpd
import numpy as np
import pandas as pd
from pyproj import Transformer
import rasterio
from rasterio.features import geometry_mask
from rasterio.windows import Window, from_bounds
import shapely
from exactextract import exact_extract

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ('population', 'pop_child', 'pop_elderly')


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(2**20), b''):
            h.update(block)
    return h.hexdigest()


def verify_manifest(items, root, source_root=None, require_all=False):
    """Verify a source manifest without assuming the raw data is in the checkout.

    Paths in the committed manifests are repository-relative POSIX paths.  A
    clean source checkout therefore contains the manifest but not the ignored
    raw raster.  ``root`` is the checkout root; ``source_root`` is an optional
    read-only restored-frozen-input root used only for hash verification.  The
    result distinguishes a missing external input from a hash mismatch instead
    of silently treating either as a pass.
    """
    root = Path(root).resolve()
    source_root = Path(source_root).resolve() if source_root else root
    rows = []
    for item in items:
        rel = str(item['path'])
        target = root / Path(rel)
        resolution = 'repository'
        if not target.is_file() and source_root != root:
            target = source_root / Path(rel)
            resolution = 'external_source_root'
        exists = target.is_file()
        actual = digest(target) if exists else None
        rows.append({
            'feature': item.get('feature'),
            'path': rel,
            'expected_sha256': item['sha256'],
            'actual_sha256': actual,
            'exists': exists,
            'resolution': resolution,
            'match': bool(exists and actual == item['sha256']),
        })
    missing = [row['path'] for row in rows if not row['exists']]
    mismatches = [row for row in rows if row['exists'] and not row['match']]
    ok = not mismatches and (not require_all or not missing)
    return {
        'root': root.as_posix(),
        'source_root': source_root.as_posix(),
        'checked': len(rows),
        'existing': sum(row['exists'] for row in rows),
        'matched': sum(row['match'] for row in rows),
        'missing': missing,
        'mismatches': mismatches,
        'require_all': bool(require_all),
        'ok': ok,
    }


def polygon_stats(src, geom, area_transform, analysis_geom=None):
    """Intersect actual native raster pixels; count valid pixels and UTM area.

    Weights for people/cell are intersection/native-cell area. Area support is
    measured separately in metres; it is never multiplied into counts again.
    """
    w = from_bounds(*geom.bounds, transform=src.transform)
    c0, r0 = int(np.floor(w.col_off))-1, int(np.floor(w.row_off))-1
    c1, r1 = int(np.ceil(w.col_off+w.width))+1, int(np.ceil(w.row_off+w.height))+1
    win = Window(c0, r0, c1-c0, r1-r0)
    outside = c0<0 or r0<0 or c1>src.width or r1>src.height
    a = src.read(1, window=win, boundless=outside, masked=True)
    rr, cc = np.meshgrid(np.arange(r0,r1), np.arange(c0,c1), indexing='ij')
    x0 = src.transform.c + cc*src.transform.a
    y0 = src.transform.f + rr*src.transform.e
    cells = shapely.box(x0, y0+src.transform.e, x0+src.transform.a, y0)
    pieces = shapely.intersection(cells, geom)
    fractions = shapely.area(pieces)/abs(src.transform.a*src.transform.e)
    overlap = fractions > 1e-12
    valid = overlap & ~np.ma.getmaskarray(a) & np.isfinite(a.data)
    centres = geometry_mask([geom], a.shape, src.window_transform(win), invert=True)
    centre_valid = centres & ~np.ma.getmaskarray(a) & np.isfinite(a.data)
    n = int(valid.sum())
    fractional = float(np.sum(a.data[valid].astype(float)*fractions[valid])) if n else np.nan
    center_n = int(centre_valid.sum())
    center_sum = float(np.sum(a.data[centre_valid].astype(float))) if center_n else np.nan
    if n:
        projected = shapely.transform(pieces[valid], area_transform, interleaved=False)
        # Newly introduced vertices approximate curved projected edges. Intersect
        # their union back with the actual UTM analysis polygon, so support area
        # cannot extend beyond its stated denominator (especially in slivers).
        area = float(shapely.intersection(shapely.union_all(projected),analysis_geom).area) if analysis_geom is not None else float(shapely.area(projected).sum())
    else:
        area = 0.
    hybrid = center_sum if center_n > 1 else fractional
    return {'support_pixels': n, 'overlapping_pixels':int(overlap.sum()),
        'support_fractional_pixels':float(fractions[valid].sum()), 'support_area_m2':area,
        'center_pixels':center_n, 'hybrid':hybrid, 'fractional':fractional}


def aggregate(grid_path, sources, baseline_path, output_dir, qa_dir, method='hybrid', support_version='agent2-DM-01-v1'):
    grid = gpd.read_file(grid_path)
    if grid.crs.to_epsg() != 32748 or not grid.grid_id.is_unique or grid.grid_id.isna().any():
        raise ValueError('Expected unique master polygons in EPSG:32748')
    raw = pd.read_csv(baseline_path).set_index('grid_id').loc[grid.grid_id].reset_index()
    support = grid[['grid_id']].copy()
    # Agent3 DM-02 contract requires a nonempty support_version shared by both files.
    support['support_version'] = support_version
    support['demographic_support_version'] = support_version
    corrected = grid[['grid_id']].copy()
    comparison = grid[['grid_id']].copy()
    manifest, conservation = [], []
    for col, path in sources.items():
        print(f'Aggregate {col}: {path}', flush=True)
        source_hash = digest(path)
        with rasterio.open(path) as src:
            if src.transform.b or src.transform.d or src.transform.a <= 0 or src.transform.e >= 0:
                raise ValueError('Rotated or south-up raster is not supported')
            polygons = grid.to_crs(src.crs)
            transform = Transformer.from_crs(src.crs, grid.crs, always_xy=True).transform
            stats = pd.DataFrame([polygon_stats(src, geom, transform, original) for geom,original in zip(polygons.geometry,grid.geometry)])
            resolved = Path(path).resolve()
            # Portable provenance: project-relative path (identity is the sha256).
            shown = resolved.relative_to(ROOT).as_posix() if resolved.is_relative_to(ROOT) else resolved.as_posix()
            manifest.append({'feature':col, 'path':shown, 'sha256':source_hash,
                'tags':src.tags(), 'band_tags':src.tags(1), 'crs':str(src.crs),
                'transform':list(src.transform), 'nodata':src.nodata, 'method':method})
            # Independent exactextract union operation tests native-cell allocation conservation.
            union = gpd.GeoDataFrame(geometry=[polygons.union_all()], crs=src.crs)
        union_total = float(exact_extract(str(path), union, ['sum'], output='pandas')['sum'].iloc[0])
        allocated = float(stats.fractional.sum())
        delta = allocated-union_total
        if abs(delta) > .01:
            raise ValueError(f'Fractional conservation failed for {col}: {delta}')
        conservation.append({'feature':col, 'fractional_sum_grids':allocated, 'fractional_study_union':union_total,
            'difference_people':delta, 'tolerance_people':.01, 'pass':abs(delta)<.01,
            'hybrid_sum_grids':float(stats.hybrid.sum()), 'hybrid_minus_fractional_people':float(stats.hybrid.sum())-allocated})
        values = stats[method]
        corrected[col] = values
        corrected[col+'_raw'] = raw[col]
        # Support area is an intersection with the UTM polygon, so it cannot
        # mathematically exceed the polygon area. GEOS overlay rounding can add
        # ~1e-11 relative excess; clip only that, and fail on anything material.
        grid_area = grid.area.to_numpy()
        excess = stats.support_area_m2.to_numpy()/grid_area-1
        if np.nanmax(excess) > 1e-9:
            raise ValueError(f'Support area exceeds polygon area for {col}: {np.nanmax(excess)}')
        stats['support_area_m2'] = np.minimum(stats.support_area_m2.to_numpy(), grid_area)
        for field in ['support_pixels','overlapping_pixels','support_fractional_pixels','support_area_m2','center_pixels']:
            support[col+'_'+field] = stats[field]
        support[col+'_support_area_fraction'] = stats.support_area_m2.to_numpy()/grid_area
        support[col+'_support_state'] = np.select([stats.support_pixels.eq(0),values.eq(0)],
            ['no_source_support','valid_estimated_zero'], default='valid_uncertain_estimate')
        support[col+'_export_state'] = np.where(stats.support_pixels.eq(0)&raw[col].eq(0),
            'processing_empty_sum_zero','supported_source_export')
        support[col+'_source_sha256'] = source_hash
        comparison[col+'_raw'] = raw[col]
        comparison[col+'_hybrid'] = stats.hybrid
        comparison[col+'_fractional'] = stats.fractional
        comparison[col+'_hybrid_delta'] = stats.hybrid-raw[col]
    support['qa_population_source_no_support'] = support.population_support_pixels.eq(0)
    support['qa_age_source_no_support'] = support.pop_child_support_pixels.eq(0)|support.pop_elderly_support_pixels.eq(0)
    corrected['pop_vulnerable'] = corrected.pop_child+corrected.pop_elderly
    corrected['vulnerable_share'] = corrected.pop_vulnerable/corrected.population.where(corrected.population.gt(0))
    corrected['aggregation_method'] = method
    corrected['support_version'] = support_version
    output_dir.mkdir(parents=True, exist_ok=True)
    qa_dir.mkdir(parents=True, exist_ok=True)
    support.to_csv(output_dir/'demographic_support.csv', index=False)
    corrected.to_csv(output_dir/'demographic_features_corrected.csv', index=False)
    comparison.to_csv(qa_dir/'demographic_reaggregation_comparison.csv', index=False)
    pd.DataFrame(conservation).to_csv(qa_dir/'aggregation_conservation.csv', index=False)
    (qa_dir/'demographic_source_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    return support, corrected


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--grid',type=Path,default=ROOT/'data/processed/grid_500m_jakarta.gpkg')
    p.add_argument('--baseline',type=Path,default=ROOT/'data/processed/spatial_features.csv')
    for col in FEATURES:
        p.add_argument('--'+col.replace('_','-'),type=Path,required=True)
    p.add_argument('--output-dir',type=Path,default=ROOT/'data/processed')
    p.add_argument('--qa-dir',type=Path,default=ROOT/'outputs/qa/remediation_agent2')
    p.add_argument('--method',choices=['hybrid','fractional'],default='hybrid')
    p.add_argument('--support-version',default='agent2-DM-01-v1')
    a=p.parse_args()
    support, corrected=aggregate(a.grid,{c:getattr(a,c) for c in FEATURES},a.baseline,a.output_dir,a.qa_dir,a.method,a.support_version)
    print({c:int(corrected[c].isna().sum()) for c in FEATURES},flush=True)


if __name__=='__main__':main()
