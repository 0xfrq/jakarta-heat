"""Independent audited-formula replay for remediation evidence, never official model outputs.

Reads frozen tabular baseline only. Does not import a frozen or sibling jhim.
Each scenario has explicit eligibility; fixed-set comparisons rerank both sides.
"""
from pathlib import Path
import json
import math
import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import from_bounds
from exactextract import exact_extract
from aggregate_demographics import digest

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/processed'
OUT=ROOT/'outputs/qa/remediation_agent2'
OLD=ROOT/'outputs/qa/agent2'
COLS=['population','pop_child','pop_elderly']


def normalize(x,clipped=True):
    lo,hi=x.quantile([.05,.95]) if clipped else (x.min(),x.max())
    if hi<=lo:return pd.Series(.5,index=x.index)
    return ((x-lo)/(hi-lo)).clip(0,1)


def rank_models(df,valid,density=False):
    v=df.loc[valid]
    result=pd.DataFrame(index=df.index)
    for clipped in [True,False]:
        l=normalize(v.lst_c,clipped);n=1-normalize(v.ndvi,clipped)
        pop=v.population/(v.area_km2 if density else 1)
        age=(v.pop_child+v.pop_elderly)/(v.area_km2 if density else 1)
        p=normalize(np.log1p(pop),clipped);a=normalize(np.log1p(age),clipped)
        d=v.park_distance_m.clip(0,1000)/1000
        scores={'m1':l,'m2':.6*l+.4*n,'m3':.4*l+.3*n+.3*p,'m4':.3*l+.2*n+.25*a+.25*d}
        if clipped:main=scores
        else:raw=scores
    for m in scores:
        order=np.lexsort((v.grid_id.to_numpy(),-raw[m].to_numpy(),-main[m].to_numpy()))
        ranks=np.empty(len(v),dtype=int);ranks[order]=np.arange(1,len(v)+1)
        result[m+'_score']=main[m].reindex(df.index)
        result[m+'_rank']=pd.Series(ranks,index=v.index).reindex(df.index)
    return result


def compatibility():
    items=[]
    for group in ['child','elderly']:
        old=ROOT/f'data/raw/worldpop/age/jakarta_{group}_2024.tif'
        new=ROOT/f'data/raw/worldpop/age_buffered/jakarta_{group}_2024_buffered.tif'
        with rasterio.open(old) as a,rasterio.open(new) as b:
            if a.crs!=b.crs or not np.allclose(a.res,b.res,atol=1e-12):raise ValueError('Incompatible raster grid')
            offset=~b.transform*(a.transform.c,a.transform.f)
            if not np.allclose(offset,np.round(offset),atol=1e-6):raise ValueError('Noninteger pixel alignment')
            for key in ['RELEASE','YEAR','DOI','SEX','AGE_RANGE','UNITS','LAYER','RESOLUTION']:
                if a.tags().get(key)!=b.tags().get(key):raise ValueError('Changed source semantics: '+key)
            av=a.read(1,masked=True)
            bv=b.read(1,window=from_bounds(*a.bounds,transform=b.transform).round_offsets().round_lengths(),masked=True)
            common=~(np.ma.getmaskarray(av)|np.ma.getmaskarray(bv))
            delta=float(np.abs(av.data[common]-bv.data[common]).max())
            lost=int((~np.ma.getmaskarray(av)&np.ma.getmaskarray(bv)).sum())
            if delta!=0 or lost:raise ValueError('Buffered source changed existing valid pixels')
            items.append({'group':group,'original_sha256':digest(old),'buffered_sha256':digest(new),
                'common_valid_pixels':int(common.sum()),'max_abs_difference':delta,'lost_valid_pixels':lost,
                'recovered_pixels_original_extent':int((np.ma.getmaskarray(av)&~np.ma.getmaskarray(bv)).sum()),
                'metadata_compatible':True})
    pd.DataFrame(items).to_csv(OUT/'buffered_source_compatibility.csv',index=False)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    compatibility()
    baseline=pd.read_csv(DATA/'final_model_features.csv')
    corrected=pd.read_csv(DATA/'demographic_features_corrected.csv').set_index('grid_id').loc[baseline.grid_id].reset_index()
    support=pd.read_csv(DATA/'demographic_support.csv').set_index('grid_id').loc[baseline.grid_id].reset_index()
    original_support=pd.read_csv(OUT/'original_masks/demographic_support.csv').set_index('grid_id').loc[baseline.grid_id].reset_index()
    diag=pd.read_csv(OLD/'network_grid_diagnostics.csv').set_index('grid_id').loc[baseline.grid_id].reset_index()
    oldvalid=baseline.model_eligible_agent3_baseline
    expected=pd.read_csv(OLD/'baseline/agent3/data/processed/modeling/priority_models.csv').set_index('grid_id').loc[baseline.grid_id].reset_index()
    replay=rank_models(baseline,oldvalid)
    for m in ['m1','m2','m3','m4']:
        np.testing.assert_allclose(replay[m+'_score'],expected[m+'_score'],atol=1e-12,equal_nan=True)
        np.testing.assert_array_equal(replay[m+'_rank'].fillna(-1),expected[m+'_rank'].fillna(-1))
    revised=baseline.copy()
    for col in COLS:
        revised[col]=corrected[col]
        revised[col+'_raw']=baseline[col]
    revised['pop_vulnerable']=revised.pop_child+revised.pop_elderly
    revised['vulnerable_share']=revised.pop_vulnerable/revised.population.where(revised.population.gt(0))
    for col in support.columns:
        if col!='grid_id':revised[col]=support[col]
    revised['qa_age_source_no_support']=support.pop_child_support_pixels.eq(0)|support.pop_elderly_support_pixels.eq(0)
    revised['qa_total_source_no_support']=support.population_support_pixels.eq(0)
    revised['qa_age_zero_pop_positive']=revised.population.gt(0)&revised.pop_vulnerable.eq(0)
    revised['source_delivery_complete_baseline']=baseline.input_delivery_complete
    revised['demographic_analytical_complete']=revised[COLS].notna().all(axis=1)
    revised['model_eligible_corrected_common_proposal']=oldvalid&revised.demographic_analytical_complete
    reasons=[]
    for row in revised.itertuples():
        parts=[]
        if row.qa_route_not_computed:parts.append('route_not_computed')
        if row.qa_lst_low_valid:parts.append('lst_valid_lt0.5')
        if row.qa_total_source_no_support:parts.append('total_no_source_support')
        if row.qa_age_source_no_support:parts.append('age_no_source_support')
        reasons.append(';'.join(parts))
    revised['model_exclusion_reason_corrected']=reasons
    # Old full table is explicitly preserved; this is the versioned analytical interface for DM-02.
    revised.to_csv(DATA/'final_model_features_corrected.csv',index=False)
    reconciliation=baseline[['grid_id','kota','population','pop_child','pop_elderly','model_eligible_agent3_baseline']].copy()
    for col in COLS:
        reconciliation[col+'_corrected']=revised[col]
        reconciliation[col+'_original_support_pixels']=original_support[col+'_support_pixels']
        reconciliation[col+'_corrected_support_pixels']=support[col+'_support_pixels']
        reconciliation[col+'_difference']=revised[col]-baseline[col]
    reconciliation['corrected_common_proposal']=revised.model_eligible_corrected_common_proposal
    reconciliation.to_csv(OUT/'demographic_support_reconciliation.csv',index=False)
    # Independent exactextract verifies all new fractional sums (separate pixel implementation).
    grid=gpd.read_file(DATA/'grid_500m_jakarta.gpkg').set_index('grid_id').loc[baseline.grid_id].reset_index()
    gpd.GeoDataFrame(revised,geometry=grid.geometry,crs=grid.crs).to_file(
        DATA/'final_model_features_corrected.gpkg',layer='corrected_source_features',driver='GPKG')
    comparisons=pd.read_csv(OUT/'demographic_reaggregation_comparison.csv').set_index('grid_id').loc[baseline.grid_id].reset_index()
    independent=[]
    for col,path in [('population',ROOT/'data/raw/worldpop/idn_pop_2024.tif'),
        ('pop_child',ROOT/'data/raw/worldpop/age_buffered/jakarta_child_2024_buffered.tif'),
        ('pop_elderly',ROOT/'data/raw/worldpop/age_buffered/jakarta_elderly_2024_buffered.tif')]:
        with rasterio.open(path) as src:g=grid.to_crs(src.crs)
        e=exact_extract(str(path),g,['sum','count'],output='pandas')
        delta=np.abs(e['sum']-comparisons[col+'_fractional'].fillna(0))
        if delta.max()>.001:raise ValueError(f'Independent extraction mismatch {col}: {delta.max()}')
        independent.append({'feature':col,'max_fractional_sum_delta':float(delta.max()),
            'no_support_id_match':bool(np.array_equal(e['count'].eq(0),support[col+'_support_pixels'].eq(0)))})
    pd.DataFrame(independent).to_csv(OUT/'independent_fractional_verification.csv',index=False)
    scenarios=[]
    orig_missing=baseline.copy()
    for col in COLS:orig_missing[col]=orig_missing[col].mask(original_support[col+'_support_pixels'].eq(0))
    scenarios.append(('original_masks_nulls',orig_missing,oldvalid&orig_missing[COLS].notna().all(axis=1),False))
    valid=revised.model_eligible_corrected_common_proposal
    scenarios.append(('buffered_hybrid_corrected',revised,valid,False))
    fractional=revised.copy()
    for col in COLS:fractional[col]=comparisons[col+'_fractional']
    scenarios.append(('buffered_fractional_corrected',fractional,valid&fractional[COLS].notna().all(axis=1),False))
    for threshold in [0.,.1,.25,.5]:
        scenarios.append((f'coverage_ge_{threshold:g}',revised,valid&revised.coverage_ratio.ge(threshold),False))
    scenarios.append(('density_objective_exploratory',revised,valid,True))
    for name,col in [('positive_tags_destination_coverage_stress','positive_access_tag_scenario_distance_m'),
        ('explicit_nodes_conservative','explicit_node_restriction_scenario_distance_m'),('full_jakarta_extent','full_distance_m')]:
        alt=revised.copy();alt['park_distance_m']=diag[col]
        scenarios.append((name,alt,valid&alt.park_distance_m.notna(),False))
    legal=OUT/'restriction_route_comparison.csv'
    if legal.exists():
        d=pd.read_csv(legal).set_index('grid_id').loc[baseline.grid_id].reset_index()
        alt=revised.copy();alt['park_distance_m']=d.connector_restriction_distance_m
        scenarios.append(('explicit_nodes_and_connectors_conservative',alt,valid&alt.park_distance_m.notna(),False))
    # Per-grid route versions for Agent3 joint scenario replay (not only aggregate Jaccards).
    route_specs=[
        ('audited_baseline',baseline.park_distance_m,DATA/'final_model_features.csv','city graph','all non-restricted OSM candidate parks','OSM way tags only','nearest node, unvalidated'),
        ('full_jakarta_extent',diag.full_distance_m,OLD/'network_grid_diagnostics.csv','full DKI graph','all non-restricted OSM candidate parks','OSM way tags only','nearest node, unvalidated'),
        ('positive_tags_destination_coverage_stress',diag.positive_access_tag_scenario_distance_m,OLD/'network_grid_diagnostics.csv','full DKI graph','access=yes/permissive tagged parks only (stress)','OSM way tags only','nearest node, unvalidated'),
        ('explicit_nodes_conservative',diag.explicit_node_restriction_scenario_distance_m,OLD/'network_grid_diagnostics.csv','full DKI graph','all non-restricted OSM candidate parks','AC-02-v1 explicit forbidden nodes removed (assumed)','nearest node, unvalidated')]
    if legal.exists():
        route_specs.append(('explicit_nodes_and_connectors_conservative',d.connector_restriction_distance_m,legal,'full DKI graph',
            'all non-restricted OSM candidate parks','AC-02-v1 explicit forbidden nodes removed (assumed)','forbidden-node connectors excluded; no resnap'))
    route_rows=[]
    for sid,dist,src,network,dest,perm,conn in route_specs:
        part=baseline[['grid_id']].copy();part['scenario_id']=sid;part['park_distance_m']=dist.to_numpy()
        part['metric_label']=np.where(part.park_distance_m.notna(),'observed_shortest_path_2026_osm_proxy','no_route_under_scenario_unknown_not_zero')
        part['stress_assumption']=sid in ('positive_tags_destination_coverage_stress','explicit_nodes_conservative','explicit_nodes_and_connectors_conservative')
        part['network_extent']=network;part['destination_policy']=dest;part['permission_policy']=perm;part['connector_policy']=conn
        part['public_access_verified']=False;part['source_table']=src.relative_to(ROOT).as_posix();part['source_sha256']=digest(src)
        route_rows.append(part)
    pd.concat(route_rows,ignore_index=True).to_csv(DATA/'agent2_route_scenarios.csv',index=False)
    rows=[];changed=[];ranks=[];thresholds=[]
    for name,alt,eligible,density in scenarios:
        actual=rank_models(alt,eligible,density)
        rank_table=baseline[['grid_id','kota']].join(actual)
        rank_table['scenario']=name;rank_table['eligible']=eligible
        ranks.append(rank_table)
        for fixed in [False,True]:
            common=oldvalid&eligible
            b=rank_models(baseline,common) if fixed else replay
            a=rank_models(alt,common,density) if fixed else actual
            nb=int(common.sum()) if fixed else int(oldvalid.sum())
            na=int(common.sum()) if fixed else int(eligible.sum())
            for fraction in [.05,.10,.20]:
                for model in ['m3','m4']:
                    btop=set(baseline.loc[b[model+'_rank'].le(math.ceil(nb*fraction)),'grid_id'])
                    atop=set(baseline.loc[a[model+'_rank'].le(math.ceil(na*fraction)),'grid_id'])
                    intersection=b[model+'_rank'].notna()&a[model+'_rank'].notna()
                    rows.append({'scenario':name,'fixed_common_set':fixed,'model':model,'top_fraction':fraction,
                        'baseline_n':nb,'alternative_n':na,'baseline_top_n':len(btop),'alternative_top_n':len(atop),
                        'retained':len(btop&atop),'entered':len(atop-btop),'left':len(btop-atop),
                        'jaccard':len(btop&atop)/len(btop|atop),
                        'rank_spearman':b.loc[intersection,model+'_rank'].corr(a.loc[intersection,model+'_rank'],method='spearman'),
                        'normalization':'reestimated on each eligible set; fixed comparisons use same IDs',
                        'status':'exploratory; audited provisional weights; not official replacement'})
                    for gid in sorted(btop^atop):changed.append({'scenario':name,'fixed_common_set':fixed,'model':model,
                        'top_fraction':fraction,'grid_id':gid,'change':'entered' if gid in atop else 'left'})
        distances=alt.loc[oldvalid,'park_distance_m']
        thresholds.append({'scenario':name,'original_common_n':int(oldvalid.sum()),'known':int(distances.notna().sum()),
            'within_500':int(distances.le(500).sum()),'within_1000':int(distances.le(1000).sum()),
            'saturated_at_1000':int(distances.ge(1000).sum()),'unknown':int(distances.isna().sum())})
    effect=pd.DataFrame(rows)
    effect.to_csv(OUT/'remediation_model_scenarios.csv',index=False)
    pd.DataFrame(changed).to_csv(OUT/'changed_priority_grids.csv',index=False)
    pd.concat(ranks,ignore_index=True).to_csv(OUT/'remediation_scenario_ranks.csv',index=False)
    pd.DataFrame(thresholds).to_csv(OUT/'park_validation_impact.csv',index=False)
    partial=revised[['grid_id','kota','area_km2','coverage_ratio',*COLS]].copy()
    for t in [0.,.1,.25,.5]:partial[f'keep_coverage_ge_{t:g}']=revised.coverage_ratio.ge(t)
    for c in COLS:partial[c+'_fractional']=fractional[c]
    partial.to_csv(OUT/'partial_grid_scenarios.csv',index=False)
    summary={'baseline_common':int(oldvalid.sum()),'corrected_common_proposal':int(valid.sum()),
        'original_no_support':{c:int(original_support[c+'_support_pixels'].eq(0).sum()) for c in COLS},
        'corrected_no_support':{c:int(support[c+'_support_pixels'].eq(0).sum()) for c in COLS},
        'original_age_missing_recovered_ids':revised.loc[original_support.pop_child_support_pixels.eq(0)&support.pop_child_support_pixels.gt(0),'grid_id'].tolist(),
        'total_people_known_original_age_missing':float(baseline.loc[original_support.pop_child_support_pixels.eq(0),'population'].sum()),
        'sum_difference_people':{c:float(revised[c].sum()-baseline[c].sum()) for c in COLS},
        'partial_n':int(revised.coverage_ratio.lt(1-1e-8).sum()),'coverage_lt_0_1_n':int(revised.coverage_ratio.lt(.1).sum()),
        'six_null_ids':revised.loc[revised.population.isna(),'grid_id'].tolist(),
        'independent_baseline_scores_and_ranks_match':True}
    (OUT/'scientific_effect_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2),flush=True)
    print(effect.loc[effect.model.eq('m4')&effect.top_fraction.eq(.1),['scenario','fixed_common_set','alternative_n','retained','entered','left','jaccard']].to_string(index=False))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(13,7))
    city=gpd.read_file(DATA/'jakarta_5kota.gpkg')
    changes=pd.DataFrame(changed)
    for ax,scenario,label in zip(axes,['buffered_hybrid_corrected','buffered_fractional_corrected'],
                                ['Buffered hybrid vs audited baseline','Buffered fractional vs audited baseline']):
        city.boundary.plot(ax=ax,color='0.6',linewidth=.6)
        cases=changes[changes.scenario.eq(scenario)&~changes.fixed_common_set&changes.model.eq('m4')&changes.top_fraction.eq(.1)]
        if len(cases):
            shapes=grid[['grid_id','geometry']].merge(cases,on='grid_id',validate='one_to_one')
            for state,color in [('entered','#b44722'),('left','#176b8c')]:
                subset=shapes[shapes.change.eq(state)]
                if len(subset):subset.plot(ax=ax,color=color,label=state)
        for row in city.itertuples():
            p=row.geometry.representative_point();ax.text(p.x,p.y,row.kota.replace('Kota Jakarta ',' '),fontsize=8)
        n_in,n_out=int(cases.change.eq('entered').sum()),int(cases.change.eq('left').sum())
        ax.set_title(f'{label}\nM4 top 10%: {n_in} enter (red), {n_out} leave (blue)',fontsize=10);ax.set_axis_off()
    fig.suptitle('Exploratory source/aggregation effects; 2024 raster estimates + 2026 OSM proxy',fontsize=12)
    fig.tight_layout(rect=(0,0,1,.93));fig.savefig(OUT/'demographic_aggregation_priority_changes.png',dpi=140);plt.close(fig)


if __name__=='__main__':main()
