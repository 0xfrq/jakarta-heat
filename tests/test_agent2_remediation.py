"""Integration and scientific invariants for actual remediation outputs."""
from pathlib import Path
import sys
import json
import hashlib
import math
import networkx as nx
import geopandas as gpd
import numpy as np
import pandas as pd
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from agent2_park_evidence import two_destinations
from agent2_connector_remediation import permission_state
from aggregate_demographics import digest, verify_manifest
OUT=ROOT/'outputs/qa/remediation_agent2'
DATA=ROOT/'data/processed'


def test_two_distinct_destinations_matches_brute_force_directed_parallel_paths():
    g=nx.MultiDiGraph()
    g.add_edge(1,2,length=20);g.add_edge(1,2,length=2)
    g.add_edge(2,3,length=7);g.add_edge(2,4,length=3)
    g.add_edge(5,1,length=2);g.add_node(6)
    candidates=[(3,0,'a'),(4,5,'b'),(3,4,'c')]
    result=two_destinations(g,*zip(*candidates))
    for node in g:
        brute=[]
        for dest,snap,park in candidates:
            try:brute.append((nx.shortest_path_length(g,node,dest,weight='length')+snap,park))
            except nx.NetworkXNoPath:pass
        assert result.get(node,[])==sorted(brute)[:2]


@pytest.mark.parametrize('tags,state',[
    ({'foot':'no','access':'yes'},'explicitly_forbidden'),
    ({'access':'private','foot':'yes'},'explicit_foot_permission_unverified'),
    ({'access':'private'},'explicitly_forbidden'),
    ({'access:conditional':'no @ (20:00-06:00)'},'conditional_unknown'),
    ({'barrier':'gate'},'barrier_permission_unknown'),
    ({},'unknown')])
def test_permission_hierarchy_preserves_unknown(tags,state):assert permission_state(tags)==state


def test_buffered_sources_identical_on_existing_valid_pixels():
    c=pd.read_csv(OUT/'buffered_source_compatibility.csv')
    assert len(c)==2 and c.metadata_compatible.all()
    assert c.common_valid_pixels.eq(74429).all()
    assert c.max_abs_difference.eq(0).all() and c.lost_valid_pixels.eq(0).all()


def test_actual_demographic_nulls_and_recovered_support_propagate():
    s=pd.read_csv(DATA/'demographic_support.csv')
    d=pd.read_csv(DATA/'demographic_features_corrected.csv')
    final=pd.read_csv(DATA/'final_model_features_corrected.csv')
    spatial=pd.read_csv(DATA/'spatial_features_corrected.csv')
    assert len(s)==len(d)==len(final)==len(spatial)==2765
    for frame in [s,d,final,spatial]:assert frame.grid_id.is_unique
    for col in ['population','pop_child','pop_elderly']:
        assert s[col+'_support_pixels'].eq(0).sum()==6
        assert d[col].isna().equals(s[col+'_support_pixels'].eq(0))
        assert spatial[col].isna().equals(d[col].isna())
        assert final[col].isna().equals(d[col].isna())
        assert final[col+'_support_state'].equals(s[col+'_support_state'])
        assert s[col+'_support_area_fraction'].between(0,1+1e-12).all()
    assert final.model_eligible_corrected_common_proposal.equals(
        final.model_eligible_agent3_baseline&final[['population','pop_child','pop_elderly']].notna().all(axis=1))
    assert final.model_eligible_agent3_baseline.sum()==2538
    assert final.model_eligible_corrected_common_proposal.sum()==2536
    assert final.loc[final.qa_route_not_computed,'park_distance_m'].isna().all()
    assert final.loc[final.population.isna(),'vulnerable_share'].isna().all()
    assert final.loc[final.qa_age_zero_pop_positive,'grid_id'].tolist()==['JKT_R050_C061']


def test_preserved_sources_byte_match_audited_baseline():
    assert digest(DATA/'spatial_features.csv')=='f87a91125587650638a0c0637e1e8ae04f925938082511840cbd47a2e6a8c724'
    assert digest(DATA/'final_model_features.csv')=='fa6a258f8f848c0afc3a44ad51c49a4df9390b2b131dd900b37a6b4f72a2e376'
    for name in ['population_grid.csv','vulnerability_grid.csv','accessibility_grid.csv']:
        assert digest(DATA/name)==digest(ROOT/'outputs/qa/agent2/baseline/person2'/name)


def test_corrected_gis_alignment_is_exact_and_nulls_survive():
    old=gpd.read_file(DATA/'grid_500m_jakarta.gpkg').set_index('grid_id')
    new=gpd.read_file(DATA/'final_model_features_corrected.gpkg').set_index('grid_id')
    assert new.crs.to_epsg()==32748 and new.index.equals(old.index)
    assert new.geometry.geom_equals(old.geometry).all()
    assert new.kota.equals(old.kota)
    assert new.population.isna().sum()==6


def test_fractional_counts_conserve_union_and_independent_extraction_agrees():
    c=pd.read_csv(OUT/'aggregation_conservation.csv')
    assert c['pass'].all() and c.difference_people.abs().lt(.01).all()
    independent=pd.read_csv(OUT/'independent_fractional_verification.csv')
    assert independent.no_support_id_match.all()
    assert independent.max_fractional_sum_delta.lt(.001).all()


def test_scenario_universes_top_budgets_and_changed_ids_reconcile():
    d=pd.read_csv(OUT/'remediation_model_scenarios.csv')
    assert (d.loc[d.fixed_common_set,'baseline_n']==d.loc[d.fixed_common_set,'alternative_n']).all()
    for row in d.itertuples():
        assert row.baseline_top_n==math.ceil(row.baseline_n*row.top_fraction)
        assert row.alternative_top_n==math.ceil(row.alternative_n*row.top_fraction)
        assert row.retained+row.entered==row.alternative_top_n
        assert row.retained+row.left==row.baseline_top_n
        assert row.jaccard==pytest.approx(row.retained/(row.retained+row.entered+row.left))
    corrected=d[d.scenario.eq('buffered_hybrid_corrected')&~d.fixed_common_set&d.model.eq('m4')&d.top_fraction.eq(.1)].iloc[0]
    assert corrected.alternative_n==2536 and corrected.retained==253
    cases=pd.read_csv(OUT/'changed_priority_grids.csv')
    cases=cases[cases.scenario.eq('buffered_hybrid_corrected')&~cases.fixed_common_set&cases.model.eq('m4')&cases.top_fraction.eq(.1)]
    assert set(cases.grid_id)=={'JKT_R039_C051','JKT_R056_C043'}


def test_candidates_are_never_upgraded_to_verified_public_by_tags():
    e=pd.read_csv(DATA/'park_access_evidence.csv')
    p=gpd.read_file(DATA/'parks_jakarta.gpkg')
    assert len(e)==1015 and set(e.park_id)==set(p.park_id)
    assert e.access_evidence_state.notna().all() and e.raw_tags_json.map(json.loads).notna().all()
    assert not e.public_access_verified.any() and not e.entrance_verified.any()
    assert e.initial_auditor_top20.sum()==20
    assert e.loc[e.initial_auditor_top20,'review_status'].eq('unresolved').all()
    assert len(gpd.read_file(DATA/'validated_park_entrances.gpkg'))==0


def test_alternative_destinations_are_distinct_and_distances_monotonic():
    d=pd.read_csv(OUT/'park_alternative_destinations.csv')
    first=d[d.candidate_order.eq(1)].set_index('grid_id')
    second=d[d.candidate_order.eq(2)].set_index('grid_id')
    joined=first.merge(second,left_index=True,right_index=True,suffixes=('_first','_second'),how='inner')
    assert joined.park_id_first.ne(joined.park_id_second).all()
    assert (joined.modeled_network_distance_m_second>=joined.modeled_network_distance_m_first-1e-6).all()
    assert not d.access_verified.any()


def test_conservative_route_outputs_keep_nodes_and_exclude_flagged_origin_connectors():
    d=pd.read_csv(OUT/'restriction_route_comparison.csv')
    c=pd.read_csv(OUT/'connector_validation.csv')
    origins=c[c.connector_type.eq('origin')].set_index('feature_id').loc[d.grid_id]
    assert d.same_origin_node.all() and len(d)==2765
    assert d.loc[origins.forbidden_source_node_count.gt(0).to_numpy(),'connector_restriction_distance_m'].isna().all()
    assert not (d.full_distance_m.isna()&d.connector_restriction_distance_m.notna()).any()
    known=d.full_distance_m.notna()&d.connector_restriction_distance_m.notna()
    assert (d.loc[known,'connector_restriction_distance_m']>=d.loc[known,'full_distance_m']-1e-6).all()
    destinations=c[c.connector_type.eq('park')].set_index('feature_id')
    winners=d.connector_restriction_winner_park_id.dropna()
    assert destinations.loc[winners,'forbidden_source_node_count'].eq(0).all()


def test_historical_failure_is_not_temporal_pass():
    d=pd.read_csv(OUT/'historical_osm_pilot.csv')
    assert len(d)==6
    assert not d.temporal_stability_claim.any()
    assert not d.snapshot_is_physical_opening_evidence.any()
    if d.status.eq('unavailable').any():assert d.loc[d.status.eq('unavailable'),'route_comparison_status'].eq('not_available').all()


def test_support_files_meet_agent3_dm02_contract():
    """Agent3 attach_demographic_evidence requires these fields; versions must agree."""
    s=pd.read_csv(DATA/'demographic_support.csv')
    d=pd.read_csv(DATA/'demographic_features_corrected.csv')
    assert set(s.grid_id)==set(d.grid_id) and len(s)==2765
    assert s.support_version.notna().all() and (s.support_version=='agent2-DM-01-v1-buffered-age').all()
    assert set(d.support_version)==set(s.support_version)
    for flag in ['qa_population_source_no_support','qa_age_source_no_support']:
        assert s[flag].dtype==bool
    assert s.qa_population_source_no_support.equals(s.population_support_pixels.eq(0))
    assert s.qa_age_source_no_support.equals(s.pop_child_support_pixels.eq(0)|s.pop_elderly_support_pixels.eq(0))
    assert s.qa_population_source_no_support.sum()==6 and s.qa_age_source_no_support.sum()==6
    original=pd.read_csv(OUT/'original_masks/demographic_support.csv')
    assert (original.support_version=='agent2-DM-01-v1-original-masks').all()
    assert original.qa_age_source_no_support.sum()==19
    # Overlay columns must never collide with the base analytical fields Agent3 keeps.
    assert not {'population','pop_child','pop_elderly','park_distance_m'}&set(s.columns)


def test_per_grid_route_scenarios_replayable_and_unknown_not_zero():
    r=pd.read_csv(DATA/'agent2_route_scenarios.csv')
    final=pd.read_csv(DATA/'final_model_features.csv')
    scenarios=set(r.scenario_id)
    assert {'audited_baseline','full_jakarta_extent','positive_tags_destination_coverage_stress',
            'explicit_nodes_conservative','explicit_nodes_and_connectors_conservative'}<=scenarios
    assert not r.duplicated(['grid_id','scenario_id']).any()
    for sid,part in r.groupby('scenario_id'):
        assert len(part)==2765 and set(part.grid_id)==set(final.grid_id)
        assert part.metric_label.eq('no_route_under_scenario_unknown_not_zero').equals(part.park_distance_m.isna())
        assert part.source_sha256.str.fullmatch('[0-9a-f]{64}').all()
    assert not r.public_access_verified.any()
    base=r[r.scenario_id.eq('audited_baseline')].set_index('grid_id').park_distance_m
    np.testing.assert_allclose(base.loc[final.grid_id].to_numpy(),final.park_distance_m.to_numpy(),equal_nan=True)
    assert base.isna().sum()==226
    conservative=r[r.scenario_id.eq('explicit_nodes_and_connectors_conservative')].set_index('grid_id').park_distance_m
    full=r[r.scenario_id.eq('full_jakarta_extent')].set_index('grid_id').park_distance_m
    assert conservative.isna().sum()==407
    both=conservative.notna()&full.notna()
    assert (conservative[both]>=full[both]-1e-6).all()


def test_source_manifests_are_portable_relative_paths(tmp_path):
    """The manifest path contract is checkout-portable; hash checks need restored inputs.

    The WorldPop rasters are intentionally Git-ignored and are supplied as a
    separate frozen bundle.  A clean source checkout can therefore prove the
    path contract and must not fail merely because data/raw is absent.  Hash
    verification is exercised below on a synthetic fixture with the same
    verifier, and is run against the real frozen inputs by
    scripts/verify_source_manifests.py (documented in docs/RC2_REPRODUCE.md).
    """
    for path in [OUT/'demographic_source_manifest.json',OUT/'original_masks/demographic_source_manifest.json']:
        items = json.loads(path.read_text(encoding='utf-8'))
        assert len(items) == 3 and {item['feature'] for item in items} == {'population','pop_child','pop_elderly'}
        for item in items:
            rel = Path(item['path'])
            assert not rel.is_absolute() and ':' not in item['path'], item['path']
            assert '\\' not in item['path'] and not item['path'].startswith('../'), item['path']
            assert len(item['sha256']) == 64 and set(item['sha256']) <= set('0123456789abcdef'), item['path']
        report = verify_manifest(items, ROOT)
        assert report['checked'] == 3
        assert report['mismatches'] == [], report
    # Exercise the same resolver on a self-contained fixture, including mutation detection.
    fixture_root = tmp_path/'source-fixture'
    payload = b'worldpop synthetic fixture; not a substitute for the frozen raster\n'
    (fixture_root/'data/raw/worldpop').mkdir(parents=True)
    (fixture_root/'data/raw/worldpop/idn_pop_2024.tif').write_bytes(payload)
    fixture = [{'feature':'population','path':'data/raw/worldpop/idn_pop_2024.tif',
                'sha256':hashlib.sha256(payload).hexdigest()}]
    clean = verify_manifest(fixture, fixture_root, require_all=True)
    assert clean['ok'] and clean['matched'] == 1 and not clean['missing']
    (fixture_root/'data/raw/worldpop/idn_pop_2024.tif').write_bytes(payload+b'mutated')
    mutated = verify_manifest(fixture, fixture_root, require_all=True)
    assert not mutated['ok'] and len(mutated['mismatches']) == 1
