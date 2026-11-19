"""Strict source joins for Person 2. Missing walking routes remain unknown."""
from __future__ import annotations
import numpy as np
import pandas as pd

ALIASES = {'pop_sum':'population','child_sum':'pop_child','elderly_sum':'pop_elderly','elder;y_sum':'pop_elderly'}


def validate_ids(frame, master_ids, label):
    if 'grid_id' not in frame or frame.grid_id.isna().any() or frame.grid_id.astype(str).str.strip().eq('').any():
        raise ValueError(f'{label}: missing grid_id')
    if frame.grid_id.duplicated().any():
        raise ValueError(f'{label}: duplicate grid_id')
    missing=set(master_ids)-set(frame.grid_id)
    extra=set(frame.grid_id)-set(master_ids)
    if missing or extra:
        raise ValueError(f'{label}: ID mismatch missing={sorted(missing)[:5]}, extra={sorted(extra)[:5]}')


def canonical_columns(frame):
    out=frame.rename(columns=ALIASES).copy()
    if out.columns.duplicated().any():
        raise ValueError('Conflicting canonical/alias columns; resolve explicitly before integration')
    return out


def validate_demographic_support(frame, support, master_ids):
    """A missing estimate is legal only with an explicit, empty source mask.

    Support is measured on every polygon/pixel intersection, independently of
    whether the hybrid aggregation selected pixel centres.
    """
    validate_ids(support, master_ids, 'demographic support')
    out = frame.merge(support, on='grid_id', validate='one_to_one')
    for col in ['population', 'pop_child', 'pop_elderly']:
        count_col, state_col = col+'_support_pixels', col+'_support_state'
        if count_col not in out or state_col not in out:
            raise ValueError(f'Missing support contract for {col}')
        counts = pd.to_numeric(out[count_col], errors='raise')
        if counts.isna().any() or not np.isfinite(counts).all() or counts.lt(0).any() or counts.mod(1).ne(0).any():
            raise ValueError(f'Invalid source support count: {col}')
        absent = counts.eq(0)
        if not out[col].isna().equals(absent):
            raise ValueError(f'{col}: null must match absent source support exactly')
        if not out.loc[absent, state_col].eq('no_source_support').all():
            raise ValueError(f'{col}: undocumented null')
        positive = ~absent
        expected = np.where(out.loc[positive, col].eq(0), 'valid_estimated_zero', 'valid_uncertain_estimate')
        if not np.array_equal(out.loc[positive, state_col], expected):
            raise ValueError(f'{col}: inconsistent estimate state')
    return out


def integrate_spatial(master, population, ages, accessibility, demographic_support=None):
    validate_ids(master,master.grid_id,'master')
    out=master[['grid_id']].copy()
    required=[('population',population,['population']),('age',ages,['pop_child','pop_elderly']),
              ('accessibility',accessibility,['park_distance_m','grid_snap_m','park_reachable','park_access_500m','park_access_1000m'])]
    for label,raw,cols in required:
        frame=canonical_columns(raw)
        validate_ids(frame,master.grid_id,label)
        if not set(cols)<=set(frame):
            raise ValueError(f'{label}: required columns {cols}')
        for col in cols:
            frame[col]=pd.to_numeric(frame[col],errors='raise')
            vals=frame[col].dropna()
            if not np.isfinite(vals).all() or vals.lt(0).any():
                raise ValueError(f'{label}: invalid nonnegative finite values in {col}')
            documented_demo = demographic_support is not None and col in ['population','pop_child','pop_elderly']
            if col!='park_distance_m' and not documented_demo and frame[col].isna().any():
                raise ValueError(f'{label}: missing {col}')
        out=out.merge(frame[['grid_id',*cols]],on='grid_id',how='left',validate='one_to_one')
    if demographic_support is not None:
        out = validate_demographic_support(out, demographic_support, master.grid_id)
    known=out.park_distance_m.notna()
    if not out.park_reachable.isin([0,1]).all() or not np.array_equal(out.park_reachable,known.astype(int)):
        raise ValueError('park_reachable must indicate whether route was computed')
    for threshold in [500,1000]:
        col=f'park_access_{threshold}m'
        if not out[col].isin([0,1]).all() or not np.array_equal(out[col],out.park_distance_m.le(threshold).astype(int)):
            raise ValueError(f'{col}: inconsistent legacy threshold flag')
    if (out.pop_child+out.pop_elderly>out.population*1.05+1).any():
        raise ValueError('Age sum exceeds total beyond Agent3 tolerance (5% +1 person)')
    return out
