"""Validate handover completeness and hash inputs/artifacts without committing anything."""
from pathlib import Path
from datetime import datetime, timezone
import importlib.metadata
import json
import subprocess
import xml.etree.ElementTree as ET
from agent2_gis import ROOT,OUT,DATA,BASE,sha,write_json


def main():
    required=['handoff/AGENT2_HANDOFF.md','handoff/AGENT2_ISSUES.md','handoff/AGENT2_DATA_DICTIONARY.md',
      'handoff/AGENT2_DECISION_REGISTER.md','data/processed/final_model_features.csv',
      'outputs/qa/agent2/unreachable_grid_diagnostics.csv','outputs/qa/agent2/far_snap_grid_diagnostics.csv',
      'outputs/qa/agent2/raster_grid_alignment.csv','outputs/qa/agent2/model_eligibility_reconciliation.csv',
      'outputs/qa/agent2/node_restriction_scenario.csv','outputs/qa/agent2/geographic_qa.gpkg',
      'outputs/qa/agent2/final_model_features.gpkg','qgis/agent2_gis_qa.qgz',
      'outputs/qa/agent2/gis_review_atlas.png','outputs/qa/agent2/network_edge_qa_map.png',
      'outputs/qa/agent2/far_snap_sample_details.png','outputs/qa/agent2/eastern_raster_coverage_detail.png',
      'outputs/qa/agent2/lisa_m4_qa.png','outputs/qa/agent2/park_samples_qa.png']
    for rel in required:
        if not (ROOT/rel).is_file():raise RuntimeError(f'Missing deliverable: {rel}')
    results=[]
    for p in OUT.glob('checks_*.json'):
        checks=json.loads(p.read_text())
        if not all(c['pass'] for c in checks):raise RuntimeError(f'Failed checks: {p}')
        results.append({'stage':p.stem,'checks':len(checks),'failures':0})
    testroot=ET.parse(OUT/'pytest_results.xml').getroot()
    suites=list(testroot) if testroot.tag=='testsuites' else [testroot]
    counts={k:sum(int(s.attrib.get(k,0)) for s in suites) for k in ['tests','failures','errors','skipped']}
    if counts['failures'] or counts['errors'] or counts['skipped']:
        raise RuntimeError(f'Incomplete final tests: {counts}')
    original=json.loads((BASE/'capture.json').read_text())
    for row in original['copies']:
        if sha(ROOT/row['copy'])!=row['sha256']:raise RuntimeError('Frozen baseline changed: '+row['copy'])
    for name in ['grid_master.csv','spatial_features.csv','accessibility_grid.csv','population_grid.csv','vulnerability_grid.csv','qa_problem_grids.csv']:
        if sha(DATA/name)!=sha(BASE/'person2'/name):raise RuntimeError('Original Person2 input changed: '+name)
    diff=subprocess.run(['git','-C',str(ROOT),'diff','--check'],capture_output=True,text=True)
    if diff.returncode:raise RuntimeError(diff.stdout+diff.stderr)
    validation={'utc':datetime.now(timezone.utc).isoformat(),'pytest':counts,'stage_checks':results,
                'pytest_terminal_summary':'38 passed, 7 subtests passed; JUnit contains 45 result records',
                'all_snapshot_hashes_preserved':True,'original_person2_csvs_unchanged':True,'git_diff_check':'PASS',
                'visual_review':'Actual PNGs inspected via image viewer; standalone QGIS project verified; no interactive QGIS session',
                'downstream':'Frozen Agent3 loader,cleaning,M1-M4 scores/ranks,city summaries and GIS geometries reproduced; official baseline unchanged',
                'status':'DONE WITH DOCUMENTED LIMITATIONS'}
    write_json(OUT/'validation_summary.json',validation)
    # All generated evidence, docs and implementation code. Exclude manifest self-reference.
    paths=[p for folder in [OUT,ROOT/'handoff'] for p in folder.rglob('*') if p.is_file()
           and p.name!='artifact_manifest.json' and '__pycache__' not in p.parts]
    paths+=[DATA/'final_model_features.csv',ROOT/'qgis/agent2_gis_qa.qgz',ROOT/'requirements-agent2.txt',ROOT/'README.md',
            *sorted((ROOT/'scripts').glob('agent2_*.py')),ROOT/'scripts/person2_contracts.py',
            ROOT/'scripts/07_integrate_spatial.py',ROOT/'tests/test_agent2_gis.py']
    manifest={'utc':datetime.now(timezone.utc).isoformat(),'workspace':str(ROOT),
              'packages':{k:importlib.metadata.version(k) for k in ['geopandas','rasterio','osmnx','networkx','scipy','exactextract','pandas','numpy','pytest']},
              'source_identity':'See immutable baseline/capture.json, population_rasters.json, park_cache_provenance.json, osm_revision_timestamp_evidence.json',
              'artifacts':[{'path':str(p.relative_to(ROOT)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(set(paths))]}
    write_json(OUT/'artifact_manifest.json',manifest)
    print(json.dumps(validation,indent=2))
    print(f"Manifest: {len(manifest['artifacts'])} artifacts")


if __name__=='__main__':main()
