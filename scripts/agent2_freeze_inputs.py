"""Freeze/check the explicit portable Agent2 offline input closure.

No sibling lookup at runtime. Frozen audited tables are data for comparisons,
never imported Python packages. --freeze is an intentional new input version.
"""
from pathlib import Path
import argparse
import json
import platform
import subprocess
import zipfile
from aggregate_demographics import digest

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'docs/agent2_frozen_inputs.json'
INPUTS=[
 'data/processed/grid_master.csv','data/processed/grid_500m_jakarta.gpkg',
 'data/processed/jakarta_5kota.gpkg','data/processed/parks_jakarta.gpkg',
 'data/processed/population_grid.csv','data/processed/vulnerability_grid.csv',
 'data/processed/accessibility_grid.csv','data/processed/spatial_features.csv',
 'data/processed/final_model_features.csv','data/processed/walk_jakarta_all.graphml',
 'data/raw/osm/jakarta_all_walk.osm','data/raw/worldpop/idn_pop_2024.tif',
 'data/raw/worldpop/age/jakarta_child_2024.tif','data/raw/worldpop/age/jakarta_elderly_2024.tif',
 'data/raw/worldpop/age_buffered/jakarta_child_2024_buffered.tif',
 'data/raw/worldpop/age_buffered/jakarta_elderly_2024_buffered.tif',
 'data/raw/worldpop/age_buffered/retrieval_manifest.json',
 'data/raw/worldpop/age_buffered/child_request.json','data/raw/worldpop/age_buffered/elderly_request.json',
 'cache/6e077f2b7acf776f3021034c57eb512f76e96175.json',
 'outputs/qa/agent2/network_grid_diagnostics.csv','outputs/qa/agent2/park_network_destinations.csv',
 'outputs/qa/agent2/baseline/agent3/data/processed/modeling/priority_models.csv',
 'outputs/qa/remediation_agent2/park_impact_priority_auditor.csv',
 'outputs/qa/remediation_agent2/park_official_evidence_sources.json',
 *[f'outputs/qa/remediation_agent2/park_source_{gid}.html' for gid in
   ['way_517498552','way_1158752464','way_155961172','way_404675353']],
 # Legacy GIS tests inspect these fixed evidence tables (not active model imports).
 *[f'outputs/qa/agent2/{name}' for name in ['spatial_features_rebuilt.csv','unreachable_grid_diagnostics.csv',
   'far_snap_grid_diagnostics.csv','raster_grid_alignment.csv','geographic_integrity.json',
   'population_raster_recomputation.csv','model_eligibility_reconciliation.csv',
   'node_restriction_scenario.csv','gis_model_sensitivity_summary.csv']],
 # Audited baseline copies: preservation tests compare live legacy exports to these.
 *[f'outputs/qa/agent2/baseline/person2/{name}' for name in ['population_grid.csv','vulnerability_grid.csv','accessibility_grid.csv']],
 # Online-lane evidence (TM-02 pilot: 6 HTTP 406 responses) archived; never re-requested offline.
 'outputs/qa/remediation_agent2/historical_osm_pilot.csv',
 'outputs/qa/remediation_agent2/historical_pilot/predeclared_plan.json',
 *[f'outputs/qa/remediation_agent2/historical_pilot/{gid}_{day}.{ext}' for gid in ['way_1158752464','way_404675353','way_517498552']
   for day in ['2024-12-31','2026-11-19'] for ext in ['overpassql','response']],
]


def check_inputs():
    manifest=json.loads(MANIFEST.read_text(encoding='utf-8'))
    errors=[]
    for item in manifest['inputs']:
        p=ROOT/item['path']
        if not p.is_file():errors.append('missing '+item['path'])
        elif digest(p)!=item['sha256']:errors.append('changed '+item['path'])
    if errors:raise ValueError('Frozen input mismatch: '+'; '.join(errors))
    return manifest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--freeze',action='store_true')
    p.add_argument('--bundle',type=Path)
    p.add_argument('--restore',type=Path,help='Restore only missing inputs, and reject any changed existing file')
    a=p.parse_args()
    if a.freeze:
        MANIFEST.parent.mkdir(parents=True,exist_ok=True)
        manifest={'version':'Agent2-remediation-v2','supersedes':'v1 (clean-room restore showed audited baseline copies and TM-02 pilot archive were missing)','scope':'Agent2 frozen-input offline rebuild; not consolidated release',
            'python':platform.python_version(),'platform':platform.platform(),
            'source_reference':'2024 WorldPop R2025A / 2026-11-19 OSM; source dates are not all observation dates',
            'licenses':{'WorldPop':'CC BY 4.0','OpenStreetMap':'ODbL 1.0; attribution required'},
            'inputs':[{'path':r,'sha256':digest(ROOT/r),'bytes':(ROOT/r).stat().st_size} for r in INPUTS]}
        MANIFEST.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    if a.restore:
        with zipfile.ZipFile(a.restore) as archive:
            allowed={r['path'] for r in json.loads(MANIFEST.read_text(encoding='utf-8'))['inputs']}
            for item in archive.infolist():
                target=(ROOT/item.filename).resolve()
                if not target.is_relative_to(ROOT.resolve()) or item.filename not in allowed:
                    raise ValueError('Unexpected archived path: '+item.filename)
                payload=archive.read(item)
                import hashlib
                expected=next(r['sha256'] for r in json.loads(MANIFEST.read_text(encoding='utf-8'))['inputs'] if r['path']==item.filename)
                if hashlib.sha256(payload).hexdigest()!=expected:raise ValueError('Archive hash mismatch')
                if target.exists():
                    if digest(target)!=expected:raise ValueError('Refuse overwrite: '+str(target))
                else:target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(payload)
    manifest=check_inputs()
    print(f"Verified {len(manifest['inputs'])} frozen input hashes",flush=True)
    if a.bundle:
        if a.bundle.exists():raise FileExistsError('Do not overwrite existing frozen bundle')
        with zipfile.ZipFile(a.bundle,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as archive:
            for item in manifest['inputs']:archive.write(ROOT/item['path'],item['path'])
        a.bundle.with_suffix('.sha256').write_text(digest(a.bundle)+'  '+a.bundle.name+'\n',encoding='utf-8')
        print('Frozen bundle:',a.bundle,flush=True)


if __name__=='__main__':main()
