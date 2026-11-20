"""Reproducible Person 2 QA; baseline features are never silently replaced.

Read-only large sources: --source-root. Frozen upstream: outputs/qa/agent2/baseline.
Stages can be rerun separately. All alternative routes are explicit scenarios.
"""
from __future__ import annotations

import argparse
from collections import Counter
import gc
import hashlib
import heapq
import importlib
from itertools import count
import json
import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

import geopandas as gpd
import networkx as nx
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import geometry_mask
from rasterio.windows import from_bounds
from scipy.spatial import cKDTree
from shapely.geometry import box, LineString, Point, mapping
import shapely

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/qa/agent2'
BASE = OUT / 'baseline'
DATA = ROOT / 'data/processed'
CHECKS = []


def check(name, passed, detail=None):
    CHECKS.append({'check': name, 'pass': bool(passed), 'detail': detail})
    if not passed:
        raise ValueError(f'QA FAILED {name}: {detail}')


def write_json(p, obj):
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=lambda x:
                 x.item() if isinstance(x, np.generic) else str(x)), encoding='utf-8')


def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda: f.read(2**20), b''):
            h.update(b)
    return h.hexdigest()


def table(name, df):
    df.to_csv(OUT / f'{name}.csv', index=False)


def keyed(df, ids, label):
    check(label + ': unique nonnull IDs', df.grid_id.notna().all() and not df.grid_id.duplicated().any())
    check(label + ': exact master ID set', set(df.grid_id) == set(ids))
    return df.set_index('grid_id').loc[list(ids)].reset_index()


def frames():
    master = pd.read_csv(BASE / 'person2/grid_master.csv')
    grid = keyed(gpd.read_file(DATA / 'grid_500m_jakarta.gpkg'), master.grid_id, 'geometry')
    spatial = keyed(pd.read_csv(BASE / 'person2/spatial_features.csv'), master.grid_id, 'spatial')
    rs = keyed(pd.read_csv(BASE / 'agent1/data/processed/remote_sensing_grid.csv'), master.grid_id, 'remote sensing')
    cities = gpd.read_file(DATA / 'jakarta_5kota.gpkg')
    parks = gpd.read_file(DATA / 'parks_jakarta.gpkg')
    return master, grid, spatial, rs, cities, parks


def baseline_metrics(sp):
    return {'rows': len(sp), 'unique_ids': sp.grid_id.nunique(),
            'missing': sp.isna().sum().to_dict(),
            'zeros': {c: int(sp[c].eq(0).sum()) for c in ('population','pop_child','pop_elderly')},
            'missing_routes': int(sp.park_distance_m.isna().sum()),
            'far_snap': int(sp.grid_snap_m.gt(250).sum()),
            'access500': int(sp.park_access_500m.sum()), 'access1000': int(sp.park_access_1000m.sum()),
            'distance': sp.park_distance_m.describe(percentiles=[.05,.25,.5,.75,.95,.99]).to_dict()}


def geography():
    master, grid, sp, rs, cities, parks = frames()
    write_json(OUT / 'baseline_metrics.json', baseline_metrics(sp))
    check('expected 2765 master', len(master) == 2765)
    for label, frame in [('grid',grid),('cities',cities),('parks',parks)]:
        check(label+': EPSG32748', frame.crs.to_epsg() == 32748)
        check(label+': valid nonempty polygons', frame.is_valid.all() and not frame.is_empty.any()
              and frame.geom_type.isin(['Polygon','MultiPolygon']).all())
    check('five mainland cities', set(cities.kota.str.replace('Kota ','',regex=False)) ==
          {f'Jakarta {x}' for x in ('Barat','Pusat','Selatan','Timur','Utara')})
    boundary = cities.union_all()
    union = grid.union_all()
    gap = boundary.symmetric_difference(union).area
    overlap = grid.area.sum() - union.area
    check('clip coverage <= 1m2 discrepancy', gap < 1, gap)
    check('no internal overlap <= 1m2 tolerance', abs(overlap) < 1, overlap)
    check('unique grid geometry', not grid.geometry.to_wkb().duplicated().any())
    rc = master.grid_id.str.extract(r'R(\d+)_C(\d+)').astype(int)
    x0 = math.floor(boundary.bounds[0]/500)*500
    y0 = math.floor(boundary.bounds[1]/500)*500
    lattice_errors=[]
    for geom,(r,c) in zip(grid.geometry, rc.itertuples(index=False,name=None)):
        expected=box(x0+c*500,y0+r*500,x0+(c+1)*500,y0+(r+1)*500).intersection(boundary)
        lattice_errors.append(geom.symmetric_difference(expected).area)
    check('500m projected lattice clipped exactly', max(lattice_errors)<.01, max(lattice_errors))
    intersections=gpd.overlay(grid[['grid_id','geometry']],cities[['kota','geometry']],how='intersection')
    intersections['area_m2']=intersections.area
    owners=intersections.sort_values('area_m2',ascending=False).drop_duplicates('grid_id').set_index('grid_id').kota
    check('majority city assignments', grid.grid_id.map(owners).equals(grid.kota))
    check('CSV city matches geometry', master.kota.equals(grid.kota))
    check('CSV area matches geometry', np.allclose(master.area_km2,grid.area/1e6,atol=1e-10))
    check('coverage fraction matches geometry', np.allclose(master.coverage_ratio,grid.area/250000,atol=1e-10))
    pts=grid.representative_point()
    repcity=gpd.sjoin(gpd.GeoDataFrame(grid[['grid_id']],geometry=pts,crs=grid.crs),
                      cities[['kota','geometry']],predicate='within').set_index('grid_id').kota
    area=master.copy()
    area['analysis_area_m2']=grid.area
    area['full_lattice_area_m2']=250000
    area['qa_partial_grid']=master.coverage_ratio.lt(1-1e-8)
    area['qa_coverage_lt10pct']=master.coverage_ratio.lt(.1)
    area['qa_area_lt005km2']=master.area_km2.lt(.05)
    area['distance_study_boundary_m']=pts.distance(boundary.boundary)
    area['representative_point_city']=area.grid_id.map(repcity)
    area['routing_city_differs_majority']=area.kota.ne(area.representative_point_city)
    area['lattice_clip_error_m2']=lattice_errors
    table('grid_area_diagnostics',area)
    gpd.GeoDataFrame(area,geometry=grid.geometry,crs=grid.crs).to_file(OUT/'geographic_qa.gpkg',layer='grid_area',driver='GPKG')
    info={'crs':str(grid.crs),'bounds_utm':grid.total_bounds.tolist(),
          'bounds_wgs84':grid.to_crs(4326).total_bounds.tolist(), 'area_km2':boundary.area/1e6,
          'coverage_symdiff_m2':gap,'overlap_m2':overlap,
          'partial_cells':int(area.qa_partial_grid.sum()), 'coverage_lt10pct':int(area.qa_coverage_lt10pct.sum()),
          'area_lt005km2':int(area.qa_area_lt005km2.sum()),
          'routing_city_differs_majority':int(area.routing_city_differs_majority.sum()),
          'city_counts':master.kota.value_counts().to_dict(), 'min_area_m2':float(grid.area.min())}
    write_json(OUT/'geographic_integrity.json',info)
    print('GEOGRAPHY',info,flush=True)


def centroid_sum(src, geom):
    win=from_bounds(*geom.bounds,transform=src.transform).round_offsets().round_lengths()
    # Expand one pixel on every side: no omission due to rounding.
    win=rasterio.windows.Window(win.col_off-1,win.row_off-1,win.width+2,win.height+2)
    arr=src.read(1,window=win,masked=True,boundless=True)
    if arr.size==0:
        return np.nan,0
    transform=src.window_transform(win)
    mask=geometry_mask([mapping(geom)],arr.shape,transform,invert=True,all_touched=False)
    vals=arr[mask].compressed()
    vals=vals[np.isfinite(vals)]
    return (float(vals.sum()),len(vals)) if len(vals) else (np.nan,0)


def population(source):
    from exactextract import exact_extract
    master,grid,sp,rs,cities,parks=frames()
    for col in ['population','pop_child','pop_elderly']:
        check(col+': finite nonnegative', np.isfinite(sp[col]).all() and sp[col].ge(0).all())
    demo=master[['grid_id','kota','area_km2']].merge(sp[['grid_id','population','pop_child','pop_elderly']],validate='one_to_one')
    demo['pop_vulnerable']=demo.pop_child+demo.pop_elderly
    demo['vulnerable_share']=demo.pop_vulnerable/demo.population.where(demo.population.gt(0))
    demo['zero_denominator']=demo.population.eq(0)
    demo['age_zero_pop_positive']=demo.population.gt(0)&demo.pop_vulnerable.eq(0)
    demo['age_gt_total']=demo.pop_vulnerable.gt(demo.population+1)
    check('ages <= total +1 person', not demo.age_gt_total.any())
    table('population_age_checks',demo)
    table('population_city_summary',demo.groupby('kota',as_index=False).agg(n_grid=('grid_id','size'),
          population=('population','sum'),pop_child=('pop_child','sum'),pop_elderly=('pop_elderly','sum'),
          population_zero=('zero_denominator','sum'),age_zero_pop_positive=('age_zero_pop_positive','sum')))
    raster_info=[]
    comparisons=demo[['grid_id','kota','population','pop_child','pop_elderly']].copy()
    for col,rel in [('population','worldpop/idn_pop_2024.tif'),
                    ('pop_child','worldpop/age/jakarta_child_2024.tif'),
                    ('pop_elderly','worldpop/age/jakarta_elderly_2024.tif')]:
        p=source/'data/raw'/rel
        print('RASTER AUDIT',p,flush=True)
        with rasterio.open(p) as src:
            g=grid.to_crs(src.crs)
            raster_info.append({'feature':col,'path':str(p),'sha256':sha(p),
                'crs':str(src.crs),'shape':[src.height,src.width], 'res':src.res,'transform':list(src.transform),
                'bounds':list(src.bounds),'nodata':src.nodata,'dtype':src.dtypes,'tags':src.tags(),
                'band_tags':src.tags(1),'units':src.units,'description':src.descriptions})
            vals=[centroid_sum(src,geom) for geom in g.geometry]
            comparisons[col+'_centroid_sum']=[v[0] for v in vals]
            comparisons[col+'_centroid_pixels']=[v[1] for v in vals]
        exact=exact_extract(str(p),g[['grid_id','geometry']],['sum','count'],include_cols=['grid_id'],output='pandas')
        exact=keyed(exact,grid.grid_id,col+' exact extraction')
        comparisons[col+'_fractional_sum']=exact['sum'].to_numpy()
        comparisons[col+'_fractional_pixels']=exact['count'].to_numpy()
        comparisons[col+'_centroid_delta']=comparisons[col+'_centroid_sum']-comparisons[col]
        comparisons[col+'_fractional_delta']=comparisons[col+'_fractional_sum']-comparisons[col]
        comparisons[col+'_qgis_hybrid_sum']=np.where(comparisons[col+'_centroid_pixels']>1,
            comparisons[col+'_centroid_sum'],comparisons[col+'_fractional_sum'])
        comparisons[col+'_qgis_hybrid_delta']=comparisons[col+'_qgis_hybrid_sum']-comparisons[col]
        check(col+': original QGIS hybrid aggregation reproduced',
              comparisons[col+'_qgis_hybrid_delta'].abs().le(.01).all(),
              comparisons[col+'_qgis_hybrid_delta'].abs().max())
    table('population_raster_recomputation',comparisons)
    write_json(OUT/'population_rasters.json',raster_info)
    info={'totals':demo[['population','pop_child','pop_elderly','pop_vulnerable']].sum().to_dict(),
          'vulnerable_share':demo.vulnerable_share.describe(percentiles=[.01,.05,.5,.95,.99]).to_dict(),
          'spearman_population_vulnerable':demo.population.corr(demo.pop_vulnerable,method='spearman'),
          'pearson_population_vulnerable':demo.population.corr(demo.pop_vulnerable),
          'positive_pop_zero_ages':int(demo.age_zero_pop_positive.sum()),
          'zero_population':int(demo.zero_denominator.sum()),
          'recomputation':{col:{method:{'sum':float(comparisons[col+'_'+method+'_sum'].sum()),
                    'max_abs_difference':float(comparisons[col+'_'+method+'_delta'].abs().max()),
                    'n_difference_gt1':int(comparisons[col+'_'+method+'_delta'].abs().gt(1).sum())}
                    for method in ['centroid','fractional','qgis_hybrid']} for col in ['population','pop_child','pop_elderly']}}
    write_json(OUT/'demographic_summary.json',info)
    print('DEMOGRAPHY',info,flush=True)


def access_class(value):
    v=str(value).strip().lower()
    if v in ('no','private','customers','permit'):
        return 'restricted_tag'
    if v in ('yes','public','permissive','designated'):
        return 'access_positive_tag_unverified'
    return 'unknown_or_conditional'


def parks_audit():
    master,grid,sp,rs,cities,parks=frames()
    p=parks.drop(columns='geometry').copy()
    p['access_class']=p.access.map(access_class)
    p['geometry_valid']=parks.is_valid
    p['geometry_duplicate']=parks.geometry.to_wkb().duplicated(keep=False)
    p['osm_id_duplicate']=p.park_id.duplicated(keep=False)
    p['area_recomputed_m2']=parks.area
    p['outside_study_m2']=parks.geometry.difference(cities.union_all()).area
    p['unnamed']=p.name.fillna('').isin(['','Unnamed Park'])
    p['representative_point_inside']=parks.geometry.covers(parks.representative_point())
    p['near_admin_boundary_100m']=parks.distance(cities.boundary.union_all()).le(100)
    p['verified_public_entrance']=False
    table('park_inventory_qa',p)
    check('park IDs unique', not p.osm_id_duplicate.any())
    check('parks intersect study area', parks.intersects(cities.union_all()).all())
    write_json(OUT/'park_summary.json',{'n':len(p),'access':p.access.value_counts(dropna=False).to_dict(),
        'classification':p.access_class.value_counts().to_dict(),'unnamed':int(p.unnamed.sum()),
        'duplicate_geometries':int(p.geometry_duplicate.sum()),'total_area_km2':parks.area.sum()/1e6,
        'original_unclipped_polygons_available':False,'verified_public_entrances':0})


def load_light_graph(path):
    """Streaming GraphML, preserving parallel directed length edges and node coordinates.

    WKT geometry/unused strings are skipped. Equivalent length graph, no source mutation.
    """
    ns='{http://graphml.graphdrawing.org/xmlns}'
    keys={}
    graph=nx.MultiDiGraph()
    stats=Counter()
    for event,el in ET.iterparse(path,events=['end']):
        tag=el.tag.removeprefix(ns)
        if tag=='key':
            keys[el.attrib['id']]=el.attrib.get('attr.name')
            el.clear()
        elif tag=='node':
            d={keys[x.attrib['key']]:x.text for x in el.findall(ns+'data')}
            graph.add_node(int(el.attrib['id']),x=float(d['x']),y=float(d['y']))
            el.clear()
        elif tag=='edge':
            d={keys[x.attrib['key']]:x.text for x in el.findall(ns+'data')}
            length=float(d['length'])
            if not math.isfinite(length) or length<0:
                raise ValueError('Invalid edge length')
            graph.add_edge(int(el.attrib['source']),int(el.attrib['target']),
                           key=int(el.attrib.get('id',0)),length=length)
            for k in ('highway','foot','access','service','oneway','oneway:foot'):
                stats[(k,str(d.get(k,'<missing>')))]+=1
            el.clear()
        elif tag=='graph':
            for x in el.findall(ns+'data'):
                graph.graph[keys[x.attrib['key']]]=x.text
    return graph,stats


def nearest(graph, points):
    ids=np.array(list(graph.nodes),dtype=np.int64)
    xy=np.array([(graph.nodes[n]['x'],graph.nodes[n]['y']) for n in ids])
    dist,pos=cKDTree(xy).query(np.column_stack([points.x,points.y]))
    return ids[pos],dist,xy[pos]


def route(graph, nodes, snaps, park_ids):
    """Multi-source Dijkstra with connector costs; returns distance and winning park.

    Edge to virtual sink reversed handles directed walks toward destinations.
    """
    best={}
    if not len(nodes)==len(snaps)==len(park_ids):
        raise ValueError('Destination nodes, connectors and identifiers must have equal lengths')
    for n,s,p in zip(nodes,snaps,park_ids):
        if not math.isfinite(float(s)) or s < 0 or n not in graph:
            raise ValueError('Invalid destination connector')
        if n not in best or (float(s),str(p))<best[n]:
            best[n]=(float(s),str(p))
    if not best:
        return {},{}
    # Weighted virtual-source equivalent, without materializing all full paths.
    reverse=graph.reverse(copy=False)
    serial=count()
    queue=[];seen={};dist={};winner={}
    for n,(s,p) in sorted(best.items(),key=lambda item:(item[1],item[0])):
        seen[n]=s
        heapq.heappush(queue,(s,next(serial),n,p))
    while queue:
        cost,_,n,park=heapq.heappop(queue)
        if n in dist:
            continue
        dist[n]=cost;winner[n]=park
        for v,parallel in reverse.adj[n].items():
            weight=min(edge['length'] for edge in parallel.values())
            if not math.isfinite(weight) or weight<0:
                raise ValueError('Invalid network length')
            candidate=cost+weight
            if v not in dist and candidate<seen.get(v,math.inf):
                seen[v]=candidate
                heapq.heappush(queue,(candidate,next(serial),v,park))
    return dist,winner


def component_info(graph,park_nodes):
    comps=sorted(nx.weakly_connected_components(graph),key=lambda c:(-len(c),min(c)))
    membership={n:i for i,c in enumerate(comps) for n in c}
    pc=Counter(membership[n] for n in park_nodes)
    return membership,[len(c) for c in comps],pc


def network(source):
    master,grid,sp,rs,cities,parks=frames()
    gp=grid.representative_point()
    pp=parks.representative_point()
    print('LOAD full length graph (source read-only)',flush=True)
    full,stats=load_light_graph(source/'data/processed/walk_jakarta_all.graphml')
    check('full graph CRS',str(full.graph.get('crs')).upper()=='EPSG:32748',full.graph)
    check('full graph filter version2',str(full.graph.get('walking_pipeline_version'))=='2')
    table('network_edge_tags',pd.DataFrame([{'tag':k,'value':v,'directed_edges':n} for (k,v),n in stats.items()]))
    gn,gs,gxy=nearest(full,gp)
    pn,ps,pxy=nearest(full,pp)
    dist,winners=route(full,pn,ps,parks.park_id)
    membership,sizes,pc=component_info(full,pn)
    diag=master[['grid_id','kota','area_km2','coverage_ratio']].merge(sp,on='grid_id',validate='one_to_one')
    diag['baseline_route_missing']=sp.park_distance_m.isna()
    diag['full_node']=gn
    diag['full_snap_m']=gs
    diag['full_node_x']=gxy[:,0];diag['full_node_y']=gxy[:,1]
    diag['grid_x']=gp.x;diag['grid_y']=gp.y
    diag['full_component']=[membership[n] for n in gn]
    diag['full_component_nodes']=[sizes[membership[n]] for n in gn]
    diag['full_component_park_nodes']=[pc[membership[n]] for n in gn]
    diag['full_distance_m']=[dist.get(n,np.nan)+s for n,s in zip(gn,gs)]
    diag['full_nearest_park_id']=[winners.get(n) for n in gn]
    diag['boundary_distance_m']=gp.distance(cities.union_all().boundary)
    pnqa=parks.drop(columns='geometry').copy()
    pnqa['full_node']=pn;pnqa['park_snap_m']=ps
    pnqa['full_component']=[membership[n] for n in pn]
    pnqa['full_component_nodes']=[sizes[membership[n]] for n in pn]
    pnqa['full_grid_destinations']=pnqa.park_id.map(diag.full_nearest_park_id.value_counts()).fillna(0).astype(int)
    pnqa['access_class']=pnqa.access.map(access_class)
    table('park_network_destinations',pnqa)
    table('network_components',pd.DataFrame({'component':range(len(sizes)),'nodes':sizes,
          'park_nodes':[pc[i] for i in range(len(sizes))]}))
    citymetrics=[]
    for city in cities.itertuples():
        slug=city.kota.replace('Kota ','').lower().replace(' ','_')
        selected=gp.within(city.geometry)
        ix=np.flatnonzero(selected)
        area=city.geometry.buffer(1500)
        eligible=parks.intersects(area)
        print('LOAD city',slug,flush=True)
        cg,cstats=load_light_graph(source/f'data/processed/walk_{slug}.graphml')
        cn,cs,cxy=nearest(cg,gp.iloc[ix])
        cpn,cps,cp_xy=nearest(cg,pp[eligible])
        cd,cw=route(cg,cpn,cps,parks.loc[eligible,'park_id'])
        cm,cz,cp=component_info(cg,cpn)
        baseline_file=pd.read_csv(BASE/'person2/accessibility_grid.csv').set_index('grid_id')
        expected=baseline_file.loc[grid.iloc[ix].grid_id,'park_distance_m'].to_numpy()
        computed=np.array([cd.get(n,np.nan)+s for n,s in zip(cn,cs)])
        check(slug+': route reproduces missing set',np.array_equal(np.isnan(expected),np.isnan(computed)))
        check(slug+': route reproduces known lengths',np.allclose(expected,computed,equal_nan=True,atol=1e-6),
              float(np.nanmax(np.abs(expected-computed))))
        check(slug+': snap reproduces lengths',np.allclose(sp.iloc[ix].grid_snap_m,cs,atol=1e-6))
        # Verify actual city cache edges against the common full graph, not metadata alone.
        unmatched=sum(1 for u,v,k,d in cg.edges(keys=True,data=True) if not full.has_edge(u,v,k)
                      or abs(full[u][v][k]['length']-d['length'])>1e-9)
        check(slug+': every edge from common full graph',unmatched==0,unmatched)
        for key,vals in {'routing_city':[city.kota]*len(ix),'city_node':cn,'city_snap_m':cs,
                         'city_node_x':cxy[:,0],'city_node_y':cxy[:,1],
                         'city_component':[cm[n] for n in cn],
                         'city_component_nodes':[cz[cm[n]] for n in cn],
                         'city_component_park_nodes':[cp[cm[n]] for n in cn],
                         'city_distance_recomputed_m':computed,
                         'city_nearest_park_id':[cw.get(n) for n in cn],
                         'city_buffer_boundary_m':gp.iloc[ix].distance(area.boundary).to_numpy()}.items():
            if key not in diag:
                diag[key]=pd.Series(index=diag.index,dtype='object' if key in ('routing_city','city_nearest_park_id') else 'float64')
            diag.loc[ix,key]=vals
        citymetrics.append({'city':city.kota,'nodes':len(cg),'edges':cg.number_of_edges(),'components':len(cz),
                            'largest_component':cz[0],'baseline_missing':int(np.isnan(expected).sum()),
                            'full_missing':int(diag.iloc[ix].full_distance_m.isna().sum()),
                            'source_metadata':json.loads((source/f'data/processed/walk_{slug}.meta.json').read_text())})
        del cg,cd,cw,cm;gc.collect()
    diag['distance_change_full_minus_baseline_m']=diag.full_distance_m-diag.park_distance_m
    diag['same_snap_node']=diag.full_node.eq(diag.city_node)
    diag['missing_cause']=np.select([
        diag.baseline_route_missing&diag.full_distance_m.notna()&diag.same_snap_node,
        diag.baseline_route_missing&diag.full_distance_m.notna()&~diag.same_snap_node,
        diag.baseline_route_missing&diag.full_distance_m.isna()&diag.full_component_park_nodes.eq(0),
        diag.baseline_route_missing&diag.full_distance_m.isna()&diag.full_component_park_nodes.gt(0)],
        ['city_crop_or_destination_filter_artifact','changed_nearest_node_full_graph',
         'disconnected_component_without_candidate_park','directed_unreachable_despite_park_component'],
        default='route_computed')
    diag['qa_far_snap']=diag.grid_snap_m.gt(250)
    diag['snap_severity']=pd.cut(diag.grid_snap_m,[-1,250,500,1000,np.inf],labels=['<=250','250-500','500-1000','>1000']).astype(str)
    # Straight-line polygon vs representative point: two deliberately distinct scenarios.
    pu=parks.union_all()
    diag['euclidean_park_polygon_m']=gp.distance(pu)
    pcoords=np.column_stack([pp.x,pp.y])
    diag['euclidean_park_rep_m']=cKDTree(pcoords).query(np.column_stack([gp.x,gp.y]))[0]
    diag['network_to_euclidean_rep_ratio']=diag.full_distance_m/diag.euclidean_park_rep_m.replace(0,np.nan)
    positive=pnqa.access_class.eq('access_positive_tag_unverified')
    sd,sw=route(full,pn[positive],ps[positive],parks.loc[positive,'park_id'])
    diag['positive_access_tag_scenario_distance_m']=[sd.get(n,np.nan)+s for n,s in zip(gn,gs)]
    diag['full_destination_access_class']=diag.full_nearest_park_id.map(pnqa.set_index('park_id').access_class)
    check('route no shorter than Euclidean rep',
          (diag.full_distance_m+2>=diag.euclidean_park_rep_m).fillna(True)[diag.full_distance_m.notna()].all())
    table('network_grid_diagnostics',diag)
    missing=diag[diag.baseline_route_missing]
    far=diag[diag.qa_far_snap]
    table('unreachable_grid_diagnostics',missing)
    table('far_snap_grid_diagnostics',far)
    table('unreachable_cause_by_city',missing.groupby(['kota','missing_cause'],as_index=False).agg(n_grid=('grid_id','size'),population=('population','sum')))
    table('far_snap_by_city',far.groupby(['kota','snap_severity'],as_index=False).agg(n_grid=('grid_id','size'),missing_routes=('baseline_route_missing','sum')))
    for name,part in [('unreachable',missing),('far_snap',far)]:
        gpd.GeoDataFrame(part.merge(grid[['grid_id','geometry']],validate='one_to_one'),geometry='geometry',crs=grid.crs).to_file(
            OUT/'geographic_qa.gpkg',layer=name,driver='GPKG')
    points=gpd.GeoDataFrame(far[['grid_id','grid_snap_m']],geometry=[Point(x,y) for x,y in zip(far.grid_x,far.grid_y)],crs=grid.crs)
    points.to_file(OUT/'geographic_qa.gpkg',layer='far_snap_grid_points',driver='GPKG')
    points.geometry=[Point(x,y) for x,y in zip(far.city_node_x,far.city_node_y)]
    points.to_file(OUT/'geographic_qa.gpkg',layer='far_snap_nodes',driver='GPKG')
    points.geometry=[LineString([(x,y),(nx_,ny)]) for x,y,nx_,ny in zip(far.grid_x,far.grid_y,far.city_node_x,far.city_node_y)]
    points.to_file(OUT/'geographic_qa.gpkg',layer='far_snap_connectors',driver='GPKG')
    # Nearest simplified node can be far from a nearby edge: diagnose without changing snaps.
    edge_rows=[]
    for city in cities.itertuples():
        slug=city.kota.replace('Kota ','').lower().replace(' ','_')
        roads=gpd.read_file(source/f'data/processed/roads_walk_{slug}.gpkg')
        for row in far[far.routing_city.eq(city.kota)].itertuples():
            point=Point(row.grid_x,row.grid_y)
            edge_rows.append({'grid_id':row.grid_id,'nearest_edge_geometry_m':roads.distance(point).min(),
                              'nearest_node_m':row.grid_snap_m})
    edge_df=pd.DataFrame(edge_rows)
    table('far_snap_node_vs_edge',edge_df)
    extremes=pnqa.sort_values('full_grid_destinations',ascending=False).head(8).copy()
    samples=pd.concat([extremes,pnqa[pnqa.name.eq('Unnamed Park')].head(3),
                       pnqa[pnqa.access_class.eq('access_positive_tag_unverified')].head(3)]).drop_duplicates('park_id')
    samples['evidence']='Local OSM polygon/tags and graph only; no field/gate verification'
    samples['confirmed_exclusion']=False
    table('park_manual_review_samples',samples)
    info={'full_nodes':len(full),'full_edges':full.number_of_edges(),'full_components':len(sizes),
          'full_largest_component':sizes[0],'graph_attributes':full.graph,
          'reciprocal_edge_missing':sum(not full.has_edge(v,u) for u,v in full.edges()),
          'city_metrics':citymetrics,'baseline_missing':len(missing),'full_missing':int(diag.full_distance_m.isna().sum()),
          'resolved_by_full':int((diag.baseline_route_missing&diag.full_distance_m.notna()).sum()),
          'cause_counts':missing.missing_cause.value_counts().to_dict(),
          'far_count':len(far),'far_missing_overlap':int(far.baseline_route_missing.sum()),
          'far_snap_distribution':far.grid_snap_m.describe().to_dict(),
          'far_node_but_edge_lt250':int(edge_df.nearest_edge_geometry_m.lt(250).sum()),
          'distance_changes':diag.distance_change_full_minus_baseline_m.describe().to_dict(),
          'changed_known_gt1m':int(diag.distance_change_full_minus_baseline_m.abs().gt(1).sum()),
          'euclidean_500':int(diag.euclidean_park_polygon_m.le(500).sum()),
          'full_network_500':int(diag.full_distance_m.le(500).sum()),
          'positive_tag_scenario_missing':int(diag.positive_access_tag_scenario_distance_m.isna().sum()),
          'positive_tag_parks':int(positive.sum())}
    write_json(OUT/'network_summary.json',info)
    print('NETWORK',info,flush=True)


def raster_alignment():
    from exactextract import exact_extract
    master,grid,sp,rs,cities,parks=frames()
    upstream_grid=gpd.read_file(BASE/'agent1/data/processed/remote_sensing_grid.gpkg').set_index('grid_id').loc[grid.grid_id]
    check('Agent1 geometry equals Person2', np.all(shapely.equals(grid.geometry.to_numpy(),upstream_grid.geometry.to_numpy())))
    check('Agent1 geometry CRS',upstream_grid.crs==grid.crs)
    check('all LST NDVI delivered',rs[['lst_c','ndvi']].notna().all().all())
    report=master[['grid_id','kota','area_km2','coverage_ratio']].merge(rs,on='grid_id',validate='one_to_one')
    # Recompute ALL grids from local rasters, independent of upstream aggregation code.
    for fn,bands in [('jakarta_2024_lst_ndvi_qa.tif',[(1,'lst_c'),(2,'ndvi')]),
                     ('jakarta_2024_trees_built_probability.tif',[(1,'tree_prob_mean'),(2,'built_prob_mean')])]:
        p=DATA/'remote_sensing'/fn
        with rasterio.open(p) as src:
            check(fn+': projected CRS alignment',src.crs.to_epsg()==32748)
            res=src.res
        ex=exact_extract(str(p),grid[['grid_id','geometry']],['mean','count'],include_cols=['grid_id'],output='pandas')
        ex=keyed(ex,grid.grid_id,fn)
        for b,col in bands:
            report[col+'_recomputed']=ex[f'band_{b}_mean'].to_numpy()
            report[col+'_delta']=report[col+'_recomputed']-report[col]
            tol={'lst_c':.001,'ndvi':.0001,'tree_prob_mean':1e-6,'built_prob_mean':1e-6}[col]
            check(col+': recomputed all grid means within CSV precision',
                  report[col+'_delta'].abs().dropna().le(tol).all(),report[col+'_delta'].abs().max())
            if col=='lst_c':
                report['lst_valid_fraction_recomputed']=ex[f'band_{b}_count'].to_numpy()*res[0]*res[1]/grid.area
                check('LST valid fraction all cells',np.allclose(report.lst_valid_fraction_recomputed,rs.lst_valid_fraction,atol=.001))
    report['qa_lst_low_valid']=report.lst_valid_fraction.lt(.5)
    table('raster_grid_alignment',report)
    report_g=gpd.GeoDataFrame(report,geometry=grid.geometry,crs=grid.crs)
    report_g[report_g.qa_lst_low_valid|report_g.grid_id.isin(['JKT_R037_C061','JKT_R038_C061','JKT_R038_C062'])].to_file(
        OUT/'geographic_qa.gpkg',layer='eastern_lst_coverage',driver='GPKG')
    write_json(OUT/'remote_alignment_summary.json',{'rows':len(rs),'delivered':int(rs[['lst_c','ndvi']].notna().all(axis=1).sum()),
        'low_coverage':report.loc[report.qa_lst_low_valid,['grid_id','kota','area_km2','lst_valid_fraction','rs_qa_flags']].to_dict('records'),
        'threshold_sensitivity':{str(t):int((rs.lst_valid_fraction.ge(t)&sp.park_distance_m.notna()).sum()) for t in [0,.25,.5,.75,.9, .99]},
        'geometry_exact_match':True,'full_raster_means_recomputed':True,
        'gee_asset_geometry_directly_verified':False})


def integration():
    raise RuntimeError("Historical integration stage retired: run scripts/run_rc1.py using the live jhim package. Frozen baseline code is evidence only.")
    master,grid,sp,rs,cities,parks=frames()
    area=pd.read_csv(OUT/'grid_area_diagnostics.csv')
    demo=pd.read_csv(OUT/'population_age_checks.csv')
    diag=pd.read_csv(OUT/'network_grid_diagnostics.csv')
    popqa=pd.read_csv(OUT/'population_raster_recomputation.csv')
    final=master.merge(sp,on='grid_id',validate='one_to_one').merge(rs,on='grid_id',validate='one_to_one')
    final=final.merge(demo[['grid_id','pop_vulnerable','vulnerable_share']],validate='one_to_one')
    final['input_delivery_complete']=final[['lst_c','ndvi','population','pop_child','pop_elderly']].notna().all(axis=1)
    final['qa_route_not_computed']=final.park_distance_m.isna()
    final['qa_far_snap']=final.grid_snap_m.gt(250)
    final['qa_partial_grid']=final.coverage_ratio.lt(1-1e-8)
    final['qa_coverage_lt10pct']=final.coverage_ratio.lt(.1)
    final['qa_lst_low_valid']=final.lst_valid_fraction.lt(.5)
    final['qa_age_zero_pop_positive']=final.population.gt(0)&final.pop_vulnerable.eq(0)
    final['qa_age_source_no_support']=popqa.pop_child_fractional_pixels.eq(0)|popqa.pop_elderly_fractional_pixels.eq(0)
    final['model_eligible_agent3_baseline']=~(final.qa_route_not_computed|final.qa_lst_low_valid)
    final['model_exclusion_reason']=np.select([final.qa_route_not_computed&final.qa_lst_low_valid,
        final.qa_route_not_computed,final.qa_lst_low_valid],['route_not_computed;lst_valid_lt0.5','route_not_computed','lst_valid_lt0.5'],default='')
    # Known-distance indicators: NaN preserves unknown; legacy binary fields remain unchanged.
    for threshold in [500,1000]:
        final[f'park_within_{threshold}m_known']=final.park_distance_m.le(threshold).astype(float).where(final.park_distance_m.notna())
    for col in ['population','pop_child','pop_elderly','park_distance_m','grid_snap_m']:
        check(col+': source value preserved',np.allclose(final[col],sp[col],equal_nan=True))
    check('final exact IDs',final.grid_id.equals(master.grid_id))
    check('final all source delivery complete',final.input_delivery_complete.all())
    check('eligibility no unknown distance imputation',final.loc[final.qa_route_not_computed,'park_distance_m'].isna().all())
    final.to_csv(DATA/'final_model_features.csv',index=False)
    gpd.GeoDataFrame(final,geometry=grid.geometry,crs=grid.crs).to_file(OUT/'final_model_features.gpkg',layer='source_features',driver='GPKG')
    # Isolated import of frozen Agent3 code. Do not import baseline worktree package by accident.
    from jhim import data as D, config as C, models as M
    original=pd.read_csv(BASE/'agent3/data/processed/modeling/merged_grid.csv')
    pri=pd.read_csv(BASE/'agent3/data/processed/modeling/priority_models.csv')
    rs3=D.read_input_csv(BASE/'agent1/data/processed/remote_sensing_grid.csv',C.RS_COLS,'Agent1',aliases=C.RS_ALIASES)
    merged,notes,dummy=D.merge_inputs(master.grid_id,rs3,sp,master)
    cleaned=D.clean_values(merged)
    check('Agent3 loader exact eligibility agreement',np.array_equal(cleaned.valid,final.model_eligible_agent3_baseline))
    check('Agent3 original eligibility agreement',np.array_equal(original.valid,cleaned.valid))
    fresh=M.build_priority_table(cleaned)
    for m in ['m1','m2','m3','m4']:
        check(m+': baseline scores reproduced',np.allclose(fresh[m+'_score'],pri[m+'_score'],equal_nan=True))
        check(m+': baseline ranks reproduced',np.allclose(fresh[m+'_rank'].to_numpy(dtype=float,na_value=np.nan),pri[m+'_rank'],equal_nan=True))
    reconciliation=final[['grid_id','kota','qa_route_not_computed','qa_lst_low_valid','model_eligible_agent3_baseline','model_exclusion_reason']].copy()
    reconciliation['agent3_valid']=original.valid
    reconciliation['discrepancy']=reconciliation.model_eligible_agent3_baseline.ne(reconciliation.agent3_valid)
    table('model_eligibility_reconciliation',reconciliation)
    # GIS integrity of frozen model map, not just CSV IDs.
    modelg=gpd.read_file(BASE/'agent3/outputs/gis/priority_models.gpkg')
    modelg=keyed(modelg,master.grid_id,'Agent3 GIS')
    check('Agent3 GIS CRS',modelg.crs==grid.crs)
    check('Agent3 GIS exact master geometry',np.all(shapely.equals(modelg.geometry.to_numpy(),grid.geometry.to_numpy())))
    if 'kota' in modelg:
        check('Agent3 GIS city assignment',modelg.kota.equals(master.kota))
    for col in ['population','pop_child','pop_elderly','park_distance_m']:
        check('Agent3 merged '+col,np.allclose(original[col],sp[col],equal_nan=True))
        if col in modelg:
            check('Agent3 GIS '+col,np.allclose(modelg[col],sp[col],equal_nan=True))
    if 'pop_vulnerable' in modelg:
        check('Agent3 GIS combined ages',np.allclose(modelg.pop_vulnerable,sp.pop_child+sp.pop_elderly))
    from jhim.spatial import queen_neighbors_fast
    neighbors=queen_neighbors_fast(grid)
    lattice_only=0
    for i,ns in neighbors.items():
        r,c=int(master.grid_id.iloc[i][5:8]),int(master.grid_id.iloc[i][10:13])
        for j in ns:
            r2,c2=int(master.grid_id.iloc[j][5:8]),int(master.grid_id.iloc[j][10:13])
            if max(abs(r-r2),abs(c-c2))>1:
                lattice_only+=1
    check('Queen adjacency geographically local',lattice_only==0)
    # City summaries independent aggregation.
    cityrows=[]
    for m in ['m1','m2','m3','m4']:
        for kota,ix in master.groupby('kota').groups.items():
            top=fresh.loc[ix,m+'_top']
            cityrows.append({'model':m.upper(),'kota':kota,'n_grid_valid':int(cleaned.loc[ix,'valid'].sum()),
                             'n_top':int(top.sum()),'populasi_di_top':float(sp.loc[ix,'population'][top].sum())})
    citydf=pd.DataFrame(cityrows)
    supplied=pd.read_csv(BASE/'agent3/outputs/tables/kota_summary.csv')
    compare=citydf.merge(supplied,on=['model','kota'],suffixes=('_recomputed','_agent3'),validate='one_to_one')
    for col in ['n_grid_valid','n_top','populasi_di_top']:
        check('city summary '+col,np.allclose(compare[col+'_recomputed'],compare[col+'_agent3']))
    table('model_city_summary_reconciliation',compare)
    # Scenarios keep model formulas/weights untouched; rankings re-estimated by frozen engine.
    scenario_rows=[]
    scenario_tables=[]
    scenario_specs=[('full_jakarta_network','full_distance_m'),('straight_line_polygon','euclidean_park_polygon_m'),
                     ('straight_line_representative_point','euclidean_park_rep_m'),
                     ('positive_access_tags_only','positive_access_tag_scenario_distance_m')]
    if 'explicit_node_restriction_scenario_distance_m' in diag:
        scenario_specs.append(('explicit_node_restrictions','explicit_node_restriction_scenario_distance_m'))
    scenario_specs.extend([('fractional_population_aggregation',None),('exclude_age_source_no_support',None)])
    for name,col in scenario_specs:
        for fixed in [False,True]:
            alt=merged.copy()
            if col:
                alt['park_distance_m']=diag[col]
                alt['park_reachable']=diag[col].notna().astype(int)
                for thr in [500,1000]:
                    alt[f'park_access_{thr}m']=(diag[col]<=thr).astype(int)
            if name=='fractional_population_aggregation':
                for feature in ['population','pop_child','pop_elderly']:
                    alt[feature]=popqa[feature+'_fractional_sum']
            ac=D.clean_values(alt)
            if name=='exclude_age_source_no_support':
                ac['valid'] &= ~final.qa_age_source_no_support
            comparison_baseline=fresh
            if fixed:
                ac['valid'] &= cleaned.valid
                fixed_baseline=cleaned.copy()
                fixed_baseline['valid']=ac.valid
                comparison_baseline=M.build_priority_table(fixed_baseline)
            if not ac.valid.any():
                scenario_rows.append({'scenario':name,'fixed_common_population':fixed,'n_valid':0})
                continue
            ap=M.build_priority_table(ac)
            topbase=set(comparison_baseline.loc[comparison_baseline.m4_top,'grid_id'])
            topalt=set(ap.loc[ap.m4_top,'grid_id'])
            common=comparison_baseline.merge(ap,on='grid_id',suffixes=('_baseline','_scenario'))
            valid=common.m4_rank_baseline.notna()&common.m4_rank_scenario.notna()
            scenario_rows.append({'scenario':name,'fixed_common_population':fixed,'n_valid':int(ac.valid.sum()),
                'comparison_baseline_n_valid':int(comparison_baseline.valid.sum()),
                'eligibility_added':int((ac.valid&~cleaned.valid).sum()),
                'eligibility_removed':int((~ac.valid&cleaned.valid).sum()),
                'm4_top_jaccard':len(topbase&topalt)/len(topbase|topalt),
                'm4_top_overlap':len(topbase&topalt),'m4_top_added':len(topalt-topbase),
                'm4_rank_spearman_intersection':common.loc[valid,'m4_rank_baseline'].corr(common.loc[valid,'m4_rank_scenario'],method='spearman'),
                'known_distances':int(alt.park_distance_m.notna().sum()),'median_distance_m':alt.park_distance_m.median()})
            ap['scenario']=name;ap['fixed_common_population']=fixed
            scenario_tables.append(ap)
    table('gis_model_sensitivity_summary',pd.DataFrame(scenario_rows))
    table('gis_model_sensitivity_grid',pd.concat(scenario_tables,ignore_index=True))
    # Missingness selection and quality effects among top grids.
    sel=master[['grid_id','kota','area_km2','coverage_ratio']].merge(sp,on='grid_id').merge(rs[['grid_id','lst_c','ndvi']],on='grid_id')
    sel['route_missing']=sel.park_distance_m.isna()
    table('route_missingness_selection',sel.groupby(['kota','route_missing'],as_index=False).agg(n_grid=('grid_id','size'),
        population=('population','sum'),median_population=('population','median'),mean_lst_c=('lst_c','mean'),
        mean_ndvi=('ndvi','mean'),median_coverage=('coverage_ratio','median')))
    qa=final[['grid_id','qa_far_snap','qa_partial_grid','qa_coverage_lt10pct','qa_lst_low_valid']].merge(fresh,on='grid_id')
    table('model_top_quality',pd.DataFrame([{'model':m,'n_top':int(qa[m+'_top'].sum()),
        **{col:int(qa.loc[qa[m+'_top'],col].sum()) for col in ['qa_far_snap','qa_partial_grid','qa_coverage_lt10pct','qa_lst_low_valid']}}
        for m in ['m1','m2','m3','m4']]))
    write_json(OUT/'integration_summary.json',{'n':len(final),'delivery_complete':int(final.input_delivery_complete.sum()),
        'eligible':int(final.model_eligible_agent3_baseline.sum()),'missing_route':int(final.qa_route_not_computed.sum()),
        'lst_quality_excluded':int(final.qa_lst_low_valid.sum()),
        'exclusion_intersection':int((final.qa_route_not_computed&final.qa_lst_low_valid).sum()),
        'canonical_agent3_baseline_unchanged':True,'agent3_snapshot':str(BASE/'agent3'),
        'adjacency_directed_pairs':sum(map(len,neighbors.values())),
        'loader_notes':notes,'source_integrated_sha256':sha(DATA/'final_model_features.csv')})


def visual():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    master,grid,sp,rs,cities,parks=frames()
    diag=pd.read_csv(OUT/'network_grid_diagnostics.csv')
    pri=pd.read_csv(BASE/'agent3/data/processed/modeling/priority_models.csv')
    lisa=pd.read_csv(BASE/'agent3/data/processed/modeling/lisa_m4.csv')
    g=grid[['grid_id','geometry']].merge(master.drop(columns='grid_id'),left_index=True,right_index=True)
    for d in [sp,rs,diag[['grid_id','full_distance_m','euclidean_park_polygon_m']]]:
        g=g.merge(d,on='grid_id',validate='one_to_one')
    g=g.merge(pri[['grid_id','m1_score','m2_score','m3_score','m4_score','m1_rank','m4_rank']],on='grid_id',validate='one_to_one')
    g['rank_gain_m1_to_m4']=g.m1_rank-g.m4_rank
    g['pop_vulnerable']=g.pop_child+g.pop_elderly
    g['route_missing']=g.park_distance_m.isna().astype(int)
    cols=[('lst_c','LST median 2024 (C)','inferno'),('ndvi','NDVI 2024','YlGn'),
          ('population','Estimated population (persons)','viridis'),('pop_vulnerable','Age-group count (persons)','viridis'),
          ('park_distance_m','Baseline modeled walking distance (m)','magma'),('route_missing','Route not computed (1=yes)','coolwarm'),
          ('m1_score','M1 provisional score','OrRd'),('m2_score','M2 provisional score','OrRd'),
          ('m3_score','M3 provisional score','OrRd'),('m4_score','M4 provisional score','OrRd'),
          ('rank_gain_m1_to_m4','Rank gain M1 to M4','RdBu'),('full_distance_m','Full-network scenario distance (m)','magma')]
    fig,axs=plt.subplots(3,4,figsize=(20,16))
    for ax,(c,title,cmap) in zip(axs.flat,cols):
        opts={}
        if c=='rank_gain_m1_to_m4':
            from matplotlib.colors import TwoSlopeNorm
            opts['norm']=TwoSlopeNorm(vmin=g[c].min(),vcenter=0,vmax=g[c].max())
        g.plot(column=c,ax=ax,cmap=cmap,legend=True,missing_kwds={'color':'#dddddd'},**opts)
        cities.boundary.plot(ax=ax,color='black',linewidth=.3)
        ax.set_title(title,fontsize=11);ax.set_axis_off()
    fig.suptitle('Agent 2 reproducible GIS review | grey = unavailable/excluded',fontsize=16)
    fig.tight_layout();fig.savefig(OUT/'gis_review_atlas.png',dpi=130);plt.close(fig)
    fig,axs=plt.subplots(1,3,figsize=(17,8))
    for ax in axs:
        grid.plot(ax=ax,color='#eeeeee',edgecolor='#aaaaaa',linewidth=.08)
        cities.boundary.plot(ax=ax,color='black',linewidth=.5);ax.set_axis_off()
    g[g.route_missing.eq(1)].plot(ax=axs[0],color='#c33f3f')
    parks.plot(ax=axs[0],color='#1b7837');axs[0].set_title('Uncomputed routes and candidate parks')
    g[g.grid_snap_m.gt(250)].plot(ax=axs[1],color='#c86412')
    lines=gpd.read_file(OUT/'geographic_qa.gpkg',layer='far_snap_connectors')
    lines.plot(ax=axs[1],color='#174a7e',linewidth=1);axs[1].set_title('Far snaps >250m and connectors')
    tiny=g[g.coverage_ratio.lt(.1)]
    tiny.plot(ax=axs[2],color='#8e44ad')
    tiny.representative_point().plot(ax=axs[2],color='#8e44ad',markersize=9)
    axs[2].set_title('Coverage <10% (markers locate tiny clipped cells)')
    fig.tight_layout();fig.savefig(OUT/'network_edge_qa_map.png',dpi=150);plt.close(fig)
    # Detailed sample panels showing actual edge geometries and snap connectors.
    selected=diag.sort_values('grid_snap_m',ascending=False).head(4)
    fig,axs=plt.subplots(2,2,figsize=(12,12))
    for ax,row in zip(axs.flat,selected.itertuples()):
        radius=max(750,row.grid_snap_m+200)
        bounds=(row.grid_x-radius,row.grid_y-radius,row.grid_x+radius,row.grid_y+radius)
        slug=row.routing_city.replace('Kota ','').lower().replace(' ','_')
        roads=gpd.read_file(ARGS.source_root/f'data/processed/roads_walk_{slug}.gpkg',bbox=bounds)
        roads.plot(ax=ax,color='#555555',linewidth=.6)
        grid[grid.grid_id.eq(row.grid_id)].boundary.plot(ax=ax,color='#cf4411',linewidth=2)
        ax.plot([row.grid_x,row.city_node_x],[row.grid_y,row.city_node_y],color='blue',marker='o')
        ax.set_xlim(bounds[0],bounds[2]);ax.set_ylim(bounds[1],bounds[3]);ax.set_aspect('equal')
        ax.set_title(f'{row.grid_id}: {row.grid_snap_m:.0f} m snap');ax.tick_params(labelsize=7)
    fig.tight_layout();fig.savefig(OUT/'far_snap_sample_details.png',dpi=140);plt.close(fig)
    # LISA labels are drawn from actual frozen Agent3 output.
    label=next((c for c in ['klaster_fdr','cluster_fdr','lisa_cluster_fdr','cluster'] if c in lisa),None)
    if label:
        lg=grid[['grid_id','geometry']].merge(lisa,on='grid_id',validate='one_to_one')
        fig,ax=plt.subplots(figsize=(8,9));lg.plot(column=label,ax=ax,legend=True,categorical=True,
            legend_kwds={'loc':'upper left','bbox_to_anchor':(1,1)})
        ax.set_title('Agent3 M4 LISA (frozen output)');ax.set_axis_off()
        fig.tight_layout();fig.savefig(OUT/'lisa_m4_qa.png',dpi=140);plt.close(fig)
    # Inspect real pixel support at the four eastern cells, not a choropleth alone.
    from rasterio.plot import show
    from rasterio.windows import from_bounds
    east=grid[grid.grid_id.isin(['JKT_R037_C061','JKT_R037_C062','JKT_R038_C061','JKT_R038_C062'])]
    xmin,ymin,xmax,ymax=east.total_bounds
    bounds=(xmin-150,ymin-150,xmax+150,ymax+150)
    fig,axs=plt.subplots(1,2,figsize=(13,8))
    with rasterio.open(DATA/'remote_sensing/jakarta_2024_lst_ndvi_qa.tif') as src:
        win=from_bounds(*bounds,transform=src.transform)
        for ax,band,title in zip(axs,[1,5],['LST pixels (C); blank = no valid retrieval','Valid LST support (1 valid; 0 no retrieval)']):
            arr=src.read(band,window=win,masked=True)
            show(arr,transform=src.window_transform(win),ax=ax,cmap='inferno' if band==1 else 'YlGn')
            fig.colorbar(ax.images[-1],ax=ax,shrink=.75,ticks=[0,1] if band==5 else None)
            east.boundary.plot(ax=ax,color='#00a9d5',linewidth=1.2)
            for row in east.itertuples():
                p=row.geometry.representative_point()
                frac=rs.set_index('grid_id').loc[row.grid_id,'lst_valid_fraction']
                ax.annotate(f'{row.grid_id}\nvalid={frac:.3f}',(p.x,p.y),fontsize=8,
                    bbox={'facecolor':'white','alpha':.75,'pad':2})
            ax.set_title(title);ax.tick_params(labelsize=7);ax.set_aspect('equal')
    fig.tight_layout();fig.savefig(OUT/'eastern_raster_coverage_detail.png',dpi=150);plt.close(fig)
    # Local polygon/road inspection only; tags do not establish verified public entry.
    parkqa=pd.read_csv(OUT/'park_network_destinations.csv')
    selected_ids=list(parkqa.sort_values('full_grid_destinations',ascending=False).head(2).park_id)
    for name in ['RPTRA Rorotan','Taman Sungai Kendal','Lapangan Tenis']:
        selected_ids.extend(parkqa.loc[parkqa.name.eq(name),'park_id'].head(1))
    inventory=pd.read_csv(OUT/'park_inventory_qa.csv')
    selected_ids.extend(inventory.loc[inventory.near_admin_boundary_100m,'park_id'].head(1))
    fig,axs=plt.subplots(2,3,figsize=(16,11))
    for ax,pid in zip(axs.flat,selected_ids):
        row=parks.set_index('park_id').loc[pid]
        point=row.geometry.representative_point()
        city=cities.loc[cities.geometry.intersects(point),'kota'].iloc[0]
        slug=city.replace('Kota ','').lower().replace(' ','_')
        xmin,ymin,xmax,ymax=row.geometry.bounds
        pad=max(150,(xmax-xmin)*.15,(ymax-ymin)*.15)
        bounds=(xmin-pad,ymin-pad,xmax+pad,ymax+pad)
        roads=gpd.read_file(ARGS.source_root/f'data/processed/roads_walk_{slug}.gpkg',bbox=bounds)
        roads.plot(ax=ax,color='#666666',linewidth=.7)
        parks[parks.park_id.eq(pid)].plot(ax=ax,color='#83ca91',edgecolor='#14622c',alpha=.7)
        ax.scatter([point.x],[point.y],color='#c13831',s=25,label='polygon representative point')
        ax.set_xlim(bounds[0],bounds[2]);ax.set_ylim(bounds[1],bounds[3]);ax.set_aspect('equal')
        ax.set_title(f'{pid}\n{row["name"]}\nOSM access={row["access"]}; entry unverified',fontsize=9)
        ax.tick_params(labelsize=6)
    fig.suptitle('Park QA samples: candidate polygons and retained road geometry; no gate validation')
    fig.tight_layout();fig.savefig(OUT/'park_samples_qa.png',dpi=140);plt.close(fig)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root',type=Path,default=ROOT)
    parser.add_argument('--stage',choices=['geography','population','parks','network','raster','integration','visual','all'],default='all')
    ARGS=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    funcs={'geography':geography,'population':lambda:population(ARGS.source_root),'parks':parks_audit,
           'network':lambda:network(ARGS.source_root),'raster':raster_alignment,'integration':integration,'visual':visual}
    try:
        for name,func in funcs.items():
            if ARGS.stage in (name,'all'):
                print('STAGE',name,flush=True);func()
    finally:
        write_json(OUT/f'checks_{ARGS.stage}.json',CHECKS)
