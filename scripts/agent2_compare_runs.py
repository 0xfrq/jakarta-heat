"""Snapshot and semantically compare two Agent2 offline reproduction runs.

`snapshot DEST` copies the declared Agent2 outputs; `compare A B` separates
byte identity from semantic equality: CSV values/IDs/missingness, JSON without
run-time keys, and GPKG attributes plus exact geometry. PNG/XML/log files are
reported by hash only (renderer/timestamp variability is not a semantic result).
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import sys

import geopandas as gpd
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = [
    'data/processed/demographic_support.csv', 'data/processed/demographic_features_corrected.csv',
    'data/processed/spatial_features_corrected.csv', 'data/processed/final_model_features_corrected.csv',
    'data/processed/final_model_features_corrected.gpkg', 'data/processed/park_access_evidence.csv',
    'data/processed/validated_park_entrances.gpkg', 'data/processed/walking_permission_manifest.json',
    'data/processed/agent2_route_scenarios.csv',
]
OUTPUT_DIRS = ['outputs/qa/remediation_agent2', 'outputs/qa/remediation_agent2/original_masks']
SKIP_SUFFIX = {'.log', '.xml', '.html'}
VOLATILE_KEYS = {'checked_utc', 'generated_utc', 'run_utc', 'timestamp', 'created_utc'}


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def declared(root):
    files = [root/p for p in OUTPUTS]
    for d in OUTPUT_DIRS:
        files += [p for p in sorted((root/d).iterdir()) if p.is_file() and p.suffix not in SKIP_SUFFIX
                  and not p.name.endswith('_equivalence.csv')]  # comparison reports, not pipeline outputs
    return [p.relative_to(root).as_posix() for p in files]


def snapshot(dest):
    dest.mkdir(parents=True, exist_ok=False)
    for rel in declared(ROOT):
        target = dest/rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT/rel, target)
    print(f'Snapshot {len(declared(ROOT))} files -> {dest}')


def strip(obj):
    if isinstance(obj, dict):
        return {k: strip(v) for k, v in obj.items() if k not in VOLATILE_KEYS}
    if isinstance(obj, list):
        return [strip(v) for v in obj]
    return obj


def frame_diff(a, b):
    if list(a.columns) != list(b.columns) or len(a) != len(b):
        return f'schema/rows differ {a.shape} vs {b.shape}'
    worst = 0.0
    for col in a.columns:
        x, y = a[col], b[col]
        if not x.isna().equals(y.isna()):
            return f'missingness differs in {col}'
        if pd.api.types.is_numeric_dtype(x) and pd.api.types.is_numeric_dtype(y):
            xv, yv = x.to_numpy(float), y.to_numpy(float)
            m = ~np.isnan(xv)
            if m.any():
                worst = max(worst, float(np.max(np.abs(xv[m]-yv[m]))))
        elif not x[x.notna()].astype(str).equals(y[y.notna()].astype(str)):
            return f'values differ in {col}'
    return None if worst == 0 else f'max_abs_numeric_diff={worst:.3e}'


def compare_one(a, b):
    suffix = a.suffix.lower()
    if suffix == '.csv':
        return frame_diff(pd.read_csv(a, low_memory=False), pd.read_csv(b, low_memory=False))
    if suffix == '.json':
        ja, jb = (strip(json.loads(p.read_text(encoding='utf-8'))) for p in (a, b))
        return None if ja == jb else 'json content differs'
    if suffix == '.gpkg':
        import pyogrio
        layers = [l[0] for l in pyogrio.list_layers(a)]
        if layers != [l[0] for l in pyogrio.list_layers(b)]:
            return 'layer list differs'
        for layer in layers:
            ga, gb = gpd.read_file(a, layer=layer), gpd.read_file(b, layer=layer)
            if ga.crs != gb.crs:
                return f'{layer}: crs differs'
            msg = frame_diff(pd.DataFrame(ga.drop(columns='geometry')), pd.DataFrame(gb.drop(columns='geometry')))
            if msg:
                return f'{layer}: {msg}'
            if len(ga) and not ga.geometry.geom_equals_exact(gb.geometry, tolerance=0).all():
                return f'{layer}: geometry differs'
        return None
    return 'hash_only'


def compare(a, b):
    rows, failures = [], 0
    names = sorted(set(declared(a)) | set(declared(b)))
    for rel in names:
        pa, pb = a/rel, b/rel
        if not (pa.exists() and pb.exists()):
            rows.append({'path': rel, 'byte_identical': False, 'semantic': 'MISSING'}); failures += 1; continue
        same_bytes = sha(pa) == sha(pb)
        msg = None if same_bytes else compare_one(pa, pb)
        if msg == 'hash_only':
            semantic = 'not_compared_presentation_only'
        elif msg is None:
            semantic = 'equal'
        elif msg.startswith('max_abs_numeric_diff'):
            semantic = 'numeric_tolerance:'+msg
            if float(msg.split('=')[1]) > 1e-9:
                failures += 1
        else:
            semantic = 'DIFFERENT:'+msg; failures += 1
        rows.append({'path': rel, 'byte_identical': same_bytes, 'semantic': semantic,
                     'sha256_a': sha(pa), 'sha256_b': sha(pb)})
    return pd.DataFrame(rows), failures


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('snapshot'); s.add_argument('dest', type=Path)
    c = sub.add_parser('compare'); c.add_argument('a', type=Path); c.add_argument('b', type=Path)
    c.add_argument('--report', type=Path)
    args = p.parse_args()
    if args.cmd == 'snapshot':
        snapshot(args.dest); return
    table, failures = compare(args.a, args.b)
    if args.report:
        table.to_csv(args.report, index=False)
    print(table.semantic.str.split(':').str[0].value_counts().to_string())
    print('byte_identical', int(table.byte_identical.sum()), 'of', len(table))
    print(table.loc[~table.semantic.isin(['equal', 'not_compared_presentation_only'])].to_string(index=False))
    print('SEMANTIC_FAILURES', failures)
    sys.exit(1 if failures else 0)


if __name__ == '__main__':
    main()
