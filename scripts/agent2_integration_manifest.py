"""Write docs/integration_manifest.json: IN-01 preparation evidence, not a release.

Read-only git inspection of all registered worktrees (no checkout, commit, merge
or write elsewhere), Agent2 source/output hashes, canonical corrected paths and
the interface checklist the integrator must resolve. IN-01 stays BLOCKED until a
committed consolidated candidate exists.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import subprocess

from aggregate_demographics import digest

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'docs/agent2_preintegration_manifest.json'
CANONICAL = {
    'demographic_support': 'data/processed/demographic_support.csv',
    'demographic_features_corrected': 'data/processed/demographic_features_corrected.csv',
    'spatial_features_corrected': 'data/processed/spatial_features_corrected.csv',
    'final_model_features_corrected': 'data/processed/final_model_features_corrected.csv',
    'final_model_features_corrected_gpkg': 'data/processed/final_model_features_corrected.gpkg',
    'route_scenarios_per_grid': 'data/processed/agent2_route_scenarios.csv',
    'park_access_evidence': 'data/processed/park_access_evidence.csv',
    'validated_park_entrances': 'data/processed/validated_park_entrances.gpkg',
    'walking_permission_manifest': 'data/processed/walking_permission_manifest.json',
    'scenario_registry': 'docs/agent2_scenario_registry.csv',
    'variable_reference_periods': 'docs/agent2_variable_reference_periods.csv',
    'frozen_input_manifest': 'docs/agent2_frozen_inputs.json',
    'requirements_lock': 'requirements.lock',
}
LEGACY_PRESERVED = ['data/processed/spatial_features.csv', 'data/processed/final_model_features.csv',
                    'data/processed/population_grid.csv', 'data/processed/vulnerability_grid.csv',
                    'data/processed/accessibility_grid.csv', 'data/processed/parks_jakarta.gpkg']


def git(*args, cwd=ROOT):
    # --no-optional-locks: never refresh another worktree's index (strictly read-only).
    return subprocess.run(['git', '--no-optional-locks', *args], cwd=cwd, capture_output=True, text=True, check=True).stdout


def worktrees():
    items, cur = [], {}
    for line in git('worktree', 'list', '--porcelain').splitlines():
        if not line:
            if cur: items.append(cur); cur = {}
            continue
        key, _, value = line.partition(' ')
        cur[key] = value
    if cur: items.append(cur)
    result = []
    for w in items:
        path = Path(w['worktree'])
        status = git('status', '--porcelain=v1', '--untracked-files=normal', cwd=path).splitlines()
        result.append({'path': w['worktree'], 'branch': w.get('branch', ''), 'head': w.get('HEAD', ''),
                       'dirty_entries': len(status), 'status_porcelain': status})
    return result


def hashed(paths):
    return {p: {'sha256': digest(ROOT/p), 'bytes': (ROOT/p).stat().st_size} for p in paths if (ROOT/p).is_file()}


def main():
    status = git('status', '--porcelain=v1', '--untracked-files=all').splitlines()
    owned = sorted(line[3:] for line in status
                   if line[3:].startswith(('scripts/', 'tests/', 'docs/', 'handoff/'))
                   or line[3:] in ('README.md', 'requirements.lock', 'requirements-agent2.txt'))
    owned = [p.split(' -> ')[-1] for p in owned]
    manifest = {
        'manifest_version': 'agent2-IN-01-prep-v1',
        'generated_utc': datetime.now(timezone.utc).isoformat(),
        'status': 'IN-01 BLOCKED: no committed consolidated candidate; this manifest is preparation evidence only',
        'consolidated_tests': 'NOT YET TESTED',
        'agreed_base': git('rev-parse', 'main').strip(),
        'worktrees': worktrees(),
        'agent2_dirty_source_hashes': hashed([p for p in owned if (ROOT/p).is_file()]),
        'canonical_corrected_paths': {k: {'path': v, **hashed([v]).get(v, {'missing': True})} for k, v in CANONICAL.items()},
        'legacy_outputs_preserved_unchanged': hashed(LEGACY_PRESERVED),
        'frozen_inputs': {
            'manifest': 'docs/agent2_frozen_inputs.json',
            'bundle': 'dist/agent2_frozen_inputs_v1.zip (gitignored; transfer out-of-band, verify .sha256)',
            'git_tracked': False,
            'note': 'raw rasters, OSM XML, GraphML and Overpass cache are gitignored; candidate must ship the bundle or retrievable hash-verified artifacts',
        },
        'interface_checklist': [
            {'item': 'nullable demographic support', 'state': 'READY_AGENT2',
             'detail': 'demographic_support.csv carries support_version, qa_population_source_no_support, qa_age_source_no_support (Agent3 DM-02 contract in agent3 docs/demographic_model_interface.md); 6 no-support cells are null, valid zeros stay 0'},
            {'item': 'raw value columns', 'state': 'NOTE',
             'detail': 'Agent2 keeps *_raw columns; Agent3 creates raw_* from its own base table. Both may coexist; integrator must not drop either silently'},
            {'item': 'support_version consistency', 'state': 'READY_AGENT2',
             'detail': 'identical support_version in demographic_support.csv and demographic_features_corrected.csv (Agent3 rejects conflicting versions)'},
            {'item': 'per-grid route scenario versions', 'state': 'READY_AGENT2',
             'detail': 'data/processed/agent2_route_scenarios.csv long format (grid_id, scenario_id, policies, metric label, provenance hash); unknown access never promoted'},
            {'item': 'person2_contracts integration', 'state': 'PENDING_INTEGRATOR',
             'detail': 'scripts/person2_contracts.py accepts documented nulls; legacy path unchanged'},
            {'item': 'README conflict', 'state': 'PENDING_INTEGRATOR',
             'detail': 'Agent2 and Agent3 both modify README.md; resolve by hand, keep both sections'},
            {'item': 'dashboard rename', 'state': 'PENDING_INTEGRATOR',
             'detail': 'Agent3 renames dashboard/app.py -> dashboard/app_4b_prototype.py and adds new dashboard/app.py; Agent2 does not touch dashboard'},
            {'item': 'RS aliases / optional fractions', 'state': 'PENDING_A1_A3',
             'detail': 'Agent1 remediated RS outputs are uncommitted; aliases (lst_mean_c/lst_c, ndvi_mean/ndvi) must be reconciled by integrator; Agent2 does not rename RS fields'},
            {'item': 'no sibling or frozen-package imports', 'state': 'READY_AGENT2_REMEDIATION_LANE',
             'detail': 'Agent2 remediation scripts (run_reproduction.ps1 stages) read local frozen inputs only and import no jhim'},
            {'item': 'frozen Agent3 jhim snapshot in Agent2 branch', 'state': 'PENDING_INTEGRATOR',
             'detail': 'outputs/qa/agent2/baseline/agent3/jhim/ is an audited-evidence copy. Legacy pre-audit stage scripts/agent2_gis.py integration() (line ~555) inserts it on sys.path; not used by tests or the reproduction lane. Release candidate must not run that stage against the real jhim or ship the copy as importable code (archive it or drop the stage)'},
            {'item': 'JKT_R037_C062', 'state': 'NOTE',
             'detail': 'delivered LST/NDVI exist; 50% thermal-coverage exclusion is a modeling QA decision, not RS delivery failure'},
            {'item': 'Scope Consolidated', 'state': 'BLOCKED',
             'detail': 'run_reproduction.ps1 -Scope Consolidated fails explicitly while tests/test_remote_sensing_grid.py, tests/agent3 or scripts/run_agent3_pipeline.py are absent'},
        ],
        'human_decisions_required': [
            'commit/integration authorization and integrator designation (IN-01)',
            'TM-01 temporal scope (mixed 2024 raster / 2026 OSM proxy vs historical claims)',
            'AC-01 primary destination construct (broad candidate proxy vs validated public parks)',
            'AC-02 permission hierarchy, conditional-access treatment, connector evidence standard',
            'BG-01 primary allocation (hybrid vs fractional), coverage threshold, count vs density objective',
            'DM-01/DM-02 shared vs model-specific eligibility; adoption of corrected demographics by Agent3',
        ],
    }
    OUT.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
    print('Wrote', OUT.relative_to(ROOT), 'worktrees', len(manifest['worktrees']),
          'agent2 sources', len(manifest['agent2_dirty_source_hashes']))


if __name__ == '__main__':
    main()
