"""Scientific contracts and independent shortest-path tests for Agent2."""
from pathlib import Path
import sys
import json
import math
import numpy as np
import pandas as pd
import networkx as nx
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from person2_contracts import integrate_spatial
from agent2_gis import route, access_class, keyed


def sources():
    master=pd.DataFrame({'grid_id':['a','b']})
    pop=pd.DataFrame({'grid_id':['b','a'],'pop_sum':[0.,100.]})
    age=pd.DataFrame({'grid_id':['a','b'],'pop_child':[20.,0.],'pop_elderly':[10.,0.]})
    acc=pd.DataFrame({'grid_id':['a','b'],'park_distance_m':[300.,np.nan],
        'grid_snap_m':[10.,400.],'park_reachable':[1,0],'park_access_500m':[1,0],'park_access_1000m':[1,0]})
    return [master,pop,age,acc]


def test_exact_join_preserves_unknown_and_zero():
    out=integrate_spatial(*sources())
    assert out.grid_id.tolist()==['a','b']
    assert out.population.tolist()==[100,0]
    assert math.isnan(out.park_distance_m.iloc[1])


@pytest.mark.parametrize('case',['missing_id','extra_id','duplicate','null_id','text','negative','infinity','missing_population','conflicting_alias'])
def test_bad_source_fails_before_output(case):
    master,pop,age,acc=sources()
    if case=='missing_id': pop=pop.iloc[:1]
    elif case=='extra_id': pop.loc[0,'grid_id']='outside'
    elif case=='duplicate': pop.loc[0,'grid_id']='a'
    elif case=='null_id': pop.loc[0,'grid_id']=None
    elif case=='text': pop['pop_sum']=pop.pop_sum.astype(object);pop.loc[0,'pop_sum']='oops'
    elif case=='negative': pop.loc[0,'pop_sum']=-1
    elif case=='infinity': pop.loc[0,'pop_sum']=np.inf
    elif case=='missing_population': pop.loc[0,'pop_sum']=np.nan
    elif case=='conflicting_alias': pop['population']=pop.pop_sum
    with pytest.raises((ValueError,TypeError)):
        integrate_spatial(master,pop,age,acc)


@pytest.mark.parametrize('column,value',[('park_reachable',0),('park_access_500m',0),('park_access_1000m',2)])
def test_inconsistent_indicators_rejected(column,value):
    args=sources();args[3].loc[0,column]=value
    with pytest.raises(ValueError): integrate_spatial(*args)


def test_age_exceeds_total_rejected():
    args=sources();args[2].loc[0,'pop_child']=150
    with pytest.raises(ValueError):integrate_spatial(*args)


def test_weighted_reverse_multisource_matches_independent_single_destinations():
    g=nx.MultiDiGraph()
    g.add_edge(1,2,length=7);g.add_edge(1,2,length=4)
    g.add_edge(2,3,length=9);g.add_edge(2,4,length=20)
    g.add_edge(5,1,length=5);g.add_node(6)
    before=g.copy()
    actual,winner=route(g,[3,4,3],[8.,0.,2.],['far','other','near'])
    expected={}
    for start in g:
        vals=[]
        for end,snap in [(3,2.),(4,0.)]:
            try:vals.append(nx.shortest_path_length(g,start,end,weight='length')+snap)
            except nx.NetworkXNoPath:pass
        if vals:expected[start]=min(vals)
    assert actual==expected
    assert winner[1]=='near'
    assert 6 not in actual
    assert nx.utils.graphs_equal(g,before)


def test_directed_routes_do_not_use_wrong_direction():
    g=nx.MultiDiGraph();g.add_edge(1,2,length=10);g.add_node(3)
    d,_=route(g,[1],[0],['p'])
    assert d=={1:0.}


def test_empty_destinations_and_bad_connectors():
    g=nx.MultiDiGraph();g.add_node(1)
    assert route(g,[],[],[])==({},{})
    with pytest.raises(ValueError):route(g,[1],[-1],['p'])
    with pytest.raises(ValueError):route(g,[1],[],['p'])


def test_access_unknown_is_not_proof_of_public_entry():
    assert access_class(None)=='unknown_or_conditional'
    assert access_class('unknown')=='unknown_or_conditional'
    assert access_class('private')=='restricted_tag'
    assert access_class('yes')=='access_positive_tag_unverified'


def artifact(name):
    p=ROOT/'outputs/qa/agent2'/name
    if not p.exists():pytest.skip(f'Generate actual artifacts first: {name}')
    return p


def test_real_source_population_and_rebuild_identical():
    original=pd.read_csv(ROOT/'data/processed/spatial_features.csv')
    rebuilt=pd.read_csv(artifact('spatial_features_rebuilt.csv'))
    pd.testing.assert_frame_equal(original,rebuilt,check_dtype=False)


def test_actual_all_missing_and_far_cases_accounted_for():
    d=pd.read_csv(artifact('network_grid_diagnostics.csv'))
    u=pd.read_csv(artifact('unreachable_grid_diagnostics.csv'))
    f=pd.read_csv(artifact('far_snap_grid_diagnostics.csv'))
    assert len(d)==2765 and d.grid_id.is_unique
    assert set(u.grid_id)==set(d.loc[d.park_distance_m.isna(),'grid_id'])
    assert len(u)==226 and len(f)==66
    assert u.full_component_park_nodes.eq(0).all()
    assert u.full_distance_m.isna().all()
    assert d.city_distance_recomputed_m.isna().equals(d.park_distance_m.isna())
    np.testing.assert_allclose(d.city_distance_recomputed_m,d.park_distance_m,equal_nan=True,atol=1e-6)


def test_final_delivery_distinct_from_eligibility_and_no_imputation():
    p=ROOT/'data/processed/final_model_features.csv'
    if not p.exists():pytest.skip('Run integration stage')
    d=pd.read_csv(p)
    assert len(d)==2765 and d.grid_id.is_unique
    assert d.input_delivery_complete.all()
    assert d.model_eligible_agent3_baseline.sum()==2538
    assert not (d.qa_route_not_computed&d.qa_lst_low_valid).any()
    assert d.loc[d.qa_route_not_computed,'park_within_500m_known'].isna().all()
    assert d.loc[d.qa_route_not_computed,'park_distance_m'].isna().all()
    assert d.loc[d.population.eq(0),'vulnerable_share'].isna().all()


def test_all_grid_raster_alignment_precision():
    d=pd.read_csv(artifact('raster_grid_alignment.csv'))
    assert len(d)==2765
    assert d.lst_c_delta.abs().max()<.001
    assert d.ndvi_delta.abs().max()<.0001
    assert d.loc[d.qa_lst_low_valid,'grid_id'].tolist()==['JKT_R037_C062']


def test_geometry_integrity_report():
    d=json.loads(artifact('geographic_integrity.json').read_text())
    assert d['coverage_symdiff_m2']<1
    assert abs(d['overlap_m2'])<1
    assert len(d['city_counts'])==5


def test_hybrid_population_reproduces_original():
    d=pd.read_csv(artifact('population_raster_recomputation.csv'))
    for col in ['population','pop_child','pop_elderly']:
        assert col+'_qgis_hybrid_delta' in d
        assert d[col+'_qgis_hybrid_delta'].abs().max()<.01


def test_downstream_eligibility_reconciles():
    d=pd.read_csv(artifact('model_eligibility_reconciliation.csv'))
    assert not d.discrepancy.any()
    assert d.agent3_valid.sum()==2538


def test_restriction_scenario_cannot_create_a_route_or_shorten_it():
    d=pd.read_csv(artifact('node_restriction_scenario.csv'))
    b=d.full_distance_m
    a=d.explicit_node_restriction_scenario_distance_m
    assert d.restriction_scenario_same_origin_node.all()
    assert not (b.isna()&a.notna()).any()
    known=b.notna()&a.notna()
    assert (a[known]+1e-6>=b[known]).all()


def test_fixed_population_scenarios_use_identical_comparison_count():
    d=pd.read_csv(artifact('gis_model_sensitivity_summary.csv'))
    assert (d.loc[d.fixed_common_population,'n_valid']==d.loc[d.fixed_common_population,'comparison_baseline_n_valid']).all()


def test_age_support_zeros_are_flagged_without_overwriting_source():
    d=pd.read_csv(ROOT/'data/processed/final_model_features.csv')
    assert d.qa_age_source_no_support.sum()==19
    assert (d.qa_age_source_no_support&d.population.gt(0)).sum()==13
    assert d.loc[d.qa_age_source_no_support,'pop_child'].eq(0).all()
