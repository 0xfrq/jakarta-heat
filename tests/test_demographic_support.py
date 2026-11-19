"""Missing-mask contracts and independent pixel allocation regression tests."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from rasterio.io import MemoryFile
from rasterio.transform import from_origin
from shapely.geometry import box

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from aggregate_demographics import polygon_stats
from person2_contracts import integrate_spatial


def stats(values,geom):
    a=np.asarray(values,dtype='float32')
    with MemoryFile() as mem:
        with mem.open(driver='GTiff',height=a.shape[0],width=a.shape[1],count=1,dtype='float32',
                      crs='EPSG:32748',transform=from_origin(0,20,10,10),nodata=-99999) as raster:
            raster.write(a,1)
            return polygon_stats(raster,geom,lambda x,y:(x,y))


def test_empty_mask_is_not_population_zero():
    s=stats([[-99999,-99999]],box(0,10,20,20))
    assert s['support_pixels']==0 and s['support_area_m2']==0
    assert np.isnan(s['hybrid']) and np.isnan(s['fractional'])


def test_supported_zero_and_fractional_pixel_allocation():
    zero=stats([[0,100]],box(0,10,10,20))
    assert zero['support_pixels']==1 and zero['hybrid']==0
    partial=stats([[0,100]],box(15,10,20,20))
    assert partial['fractional']==pytest.approx(50)
    assert partial['support_area_m2']==pytest.approx(50)


def test_hybrid_and_fractional_are_different_estimands():
    s=stats([[100,100,100]],box(0,10,24,20))
    assert s['center_pixels']==2
    assert s['hybrid']==200
    assert s['fractional']==pytest.approx(240)


def inputs():
    master=pd.DataFrame({'grid_id':['a','b']})
    pop=pd.DataFrame({'grid_id':['a','b'],'population':[100.,np.nan]})
    age=pd.DataFrame({'grid_id':['a','b'],'pop_child':[0.,np.nan],'pop_elderly':[10.,np.nan]})
    acc=pd.DataFrame({'grid_id':['a','b'],'park_distance_m':[300.,np.nan],
        'grid_snap_m':[10.,20.],'park_reachable':[1,0],'park_access_500m':[1,0],'park_access_1000m':[1,0]})
    support=master.copy()
    for col,zero in [('population',False),('pop_child',True),('pop_elderly',False)]:
        support[col+'_support_pixels']=[2,0]
        support[col+'_support_state']=['valid_estimated_zero' if zero else 'valid_uncertain_estimate','no_source_support']
    return master,pop,age,acc,support


def test_documented_null_survives_join_and_states_survive_ingestion():
    d=integrate_spatial(*inputs())
    assert d.loc[1,['population','pop_child','pop_elderly']].isna().all()
    assert d.loc[0,'pop_child']==0
    assert d.loc[1,'population_support_state']=='no_source_support'


@pytest.mark.parametrize('fault',['fabricated_zero','undocumented_null','wrong_state','fractional_pixel_count','missing_id','supported_null'])
def test_support_contract_rejects_semantic_corruption(fault):
    args=list(inputs());s=args[-1]
    if fault=='fabricated_zero':args[1].loc[1,'population']=0
    elif fault=='undocumented_null':s.loc[1,'population_support_state']='valid_estimated_zero'
    elif fault=='wrong_state':s.loc[0,'pop_child_support_state']='valid_uncertain_estimate'
    elif fault=='fractional_pixel_count':
        s['population_support_pixels']=s.population_support_pixels.astype(float)
        s.loc[0,'population_support_pixels']=.5
    elif fault=='missing_id':args[-1]=s.iloc[:1]
    elif fault=='supported_null':args[1].loc[0,'population']=np.nan
    with pytest.raises(ValueError):integrate_spatial(*args)


def test_real_original_mask_ids_match_independent_auditor_evidence():
    old=pd.read_csv(ROOT/'outputs/qa/remediation_agent2/original_masks/demographic_support.csv')
    expected={'JKT_R003_C031','JKT_R057_C063','JKT_R061_C009','JKT_R061_C010','JKT_R061_C011','JKT_R062_C043'}
    assert len(old)==2765
    assert set(old.loc[old.population_support_pixels.eq(0),'grid_id'])==expected
    assert old.pop_child_support_pixels.eq(0).sum()==19
    assert old.pop_elderly_support_pixels.eq(0).sum()==19
    case=old.set_index('grid_id').loc['JKT_R050_C061']
    assert case.pop_child_support_pixels>0 and case.pop_child_support_state=='valid_estimated_zero'
