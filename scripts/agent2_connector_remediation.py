"""AC-02: fixed-node conservative gate and straight-connector screen.

OSM prohibition evidence is not physical validation. Conditional and unknown
barriers remain unknown. This command never replaces accessibility_grid.csv.
"""
from pathlib import Path
import json
import xml.etree.ElementTree as ET
import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from shapely.geometry import LineString
from scipy.spatial import cKDTree
from agent2_gis import load_light_graph, route
from walking_network import values
from aggregate_demographics import digest

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/processed'
OLD=ROOT/'outputs/qa/agent2'
OUT=ROOT/'outputs/qa/remediation_agent2'


def permission_state(tags):
    foot=values(tags.get('foot'));access=values(tags.get('access'))
    if foot&{'no','private'}:return 'explicitly_forbidden'
    if access&{'no','private'} and not foot&{'yes','designated','permissive'}:return 'explicitly_forbidden'
    if tags.get('foot:conditional') or tags.get('access:conditional'):return 'conditional_unknown'
    if foot&{'yes','designated','permissive'}:return 'explicit_foot_permission_unverified'
    if tags.get('barrier'):return 'barrier_permission_unknown'
    return 'unknown'


def connector_records(ids,points,nodes,xs,ys,blocked,kind):
    rows=[];geoms=[]
    tree=shapely.STRtree(blocked.geometry.to_numpy())
    for ident,point,node,x,y in zip(ids,points,nodes,xs,ys):
        line=LineString([(point.x,point.y),(x,y)])
        hits=tree.query(line,predicate='dwithin',distance=.05)
        rows.append({'feature_id':ident,'connector_type':kind,'original_node_id':int(node),
            'connector_length_m':line.length,'forbidden_source_node_count':len(hits),
            'forbidden_source_node_ids':';'.join(map(str,blocked.iloc[hits].osm_node_id.tolist())),
            'permission_override':'','screen_state':'excluded_explicit_osm_prohibition' if len(hits) else 'physical_access_unresolved',
            'conditional_access_state':'not_resolved','entrance_verified':False,
            'inspection_method':'automated_0.05m_source_node_intersection; not field or legal verification'})
        geoms.append(line)
    return gpd.GeoDataFrame(rows,geometry=geoms,crs=32748)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    raw=ROOT/'data/raw/osm/jakarta_all_walk.osm'
    graph_path=DATA/'walk_jakarta_all.graphml'
    # Retain all relevant node tags, including permissions and unresolved conditional cases.
    rows=[]
    for _,el in ET.iterparse(raw,events=['end']):
        if el.tag=='node':
            tags={t.attrib['k']:t.attrib['v'] for t in el.findall('tag')}
            if any(k in tags for k in ['barrier','access','foot','foot:conditional','access:conditional']):
                rows.append({'osm_node_id':int(el.attrib['id']),'lon':float(el.attrib['lon']),
                    'lat':float(el.attrib['lat']),'permission_state':permission_state(tags),'raw_tags_json':json.dumps(tags,sort_keys=True)})
            el.clear()
        elif el.tag=='way':el.clear()
    nodes=pd.DataFrame(rows)
    nodes.to_csv(OUT/'walking_node_permission_evidence.csv',index=False)
    forbidden=nodes[nodes.permission_state.eq('explicitly_forbidden')].copy()
    blocked=gpd.GeoDataFrame(forbidden,geometry=gpd.points_from_xy(forbidden.lon,forbidden.lat),crs=4326).to_crs(32748)
    diag=pd.read_csv(OLD/'network_grid_diagnostics.csv')
    parks=gpd.read_file(DATA/'parks_jakarta.gpkg')
    dest=pd.read_csv(OLD/'park_network_destinations.csv').set_index('park_id').loc[parks.park_id].reset_index()
    grid=gpd.read_file(DATA/'grid_500m_jakarta.gpkg').set_index('grid_id').loc[diag.grid_id].reset_index()
    origins=connector_records(diag.grid_id,grid.representative_point(),diag.full_node,diag.full_node_x,diag.full_node_y,blocked,'origin')
    graph,_=load_light_graph(graph_path)
    dest_x=[graph.nodes[int(n)]['x'] for n in dest.full_node]
    dest_y=[graph.nodes[int(n)]['y'] for n in dest.full_node]
    destinations=connector_records(dest.park_id,parks.representative_point(),dest.full_node,dest_x,dest_y,blocked,'park')
    priorities=pd.read_csv(OLD/'baseline/agent3/data/processed/modeling/priority_models.csv').set_index('grid_id')
    origins['baseline_m4_top']=origins.feature_id.map(priorities.m4_top).fillna(False)
    origins['far_snap']=origins.connector_length_m.gt(250)
    origins['review_priority']=origins.baseline_m4_top|origins.far_snap
    connectors=pd.concat([origins,destinations],ignore_index=True)
    connectors.drop(columns='geometry').to_csv(OUT/'connector_validation.csv',index=False)
    origins.to_file(OUT/'connector_validation.gpkg',layer='origin_connectors',driver='GPKG')
    destinations.to_file(OUT/'connector_validation.gpkg',layer='park_connectors',driver='GPKG')
    blocked.to_file(OUT/'connector_validation.gpkg',layer='source_prohibitions',driver='GPKG')
    retained=set(forbidden.osm_node_id)&set(graph)
    tree=cKDTree(np.column_stack([blocked.geometry.x,blocked.geometry.y]))
    keys={};removed=[];ns='{http://graphml.graphdrawing.org/xmlns}'
    print('Screen original simplified edges without changing snap nodes',flush=True)
    for _,el in ET.iterparse(graph_path,events=['end']):
        tag=el.tag.removeprefix(ns)
        if tag=='key':keys[el.attrib['id']]=el.attrib.get('attr.name');el.clear()
        elif tag=='node':el.clear()
        elif tag=='edge':
            u,v,k=int(el.attrib['source']),int(el.attrib['target']),int(el.attrib.get('id',0))
            fields={keys[x.attrib['key']]:x.text for x in el.findall(ns+'data')}
            reject=u in retained or v in retained
            if not reject and 'geometry' in fields:
                line=shapely.from_wkt(fields['geometry'])
                reject=tree.query(np.asarray(line.coords),distance_upper_bound=.05)[0].min()<.05
            if reject:removed.append((u,v,k))
            el.clear()
    graph.remove_edges_from(removed)
    allowed_nodes=~dest.full_node.isin(retained)
    d,_=route(graph,dest.loc[allowed_nodes,'full_node'],dest.loc[allowed_nodes,'park_snap_m'],dest.loc[allowed_nodes,'park_id'])
    restricted=np.array([d.get(int(n),np.nan)+s for n,s in zip(diag.full_node,diag.full_snap_m)])
    np.testing.assert_allclose(restricted,diag.explicit_node_restriction_scenario_distance_m,atol=1e-6,equal_nan=True)
    allowed_dest=allowed_nodes&destinations.forbidden_source_node_count.eq(0)
    legal,winner=route(graph,dest.loc[allowed_dest,'full_node'],dest.loc[allowed_dest,'park_snap_m'],dest.loc[allowed_dest,'park_id'])
    legal_dist=np.array([legal.get(int(n),np.nan)+s if ok else np.nan for n,s,ok in
        zip(diag.full_node,diag.full_snap_m,origins.forbidden_source_node_count.eq(0))])
    result=diag[['grid_id','kota','park_distance_m','full_distance_m','full_node','full_snap_m']].copy()
    result['explicit_node_restriction_distance_m']=restricted
    result['connector_restriction_distance_m']=legal_dist
    result['same_origin_node']=True
    result['connector_restriction_winner_park_id']=[winner.get(int(n),'') if np.isfinite(d) else '' for n,d in zip(diag.full_node,legal_dist)]
    result.to_csv(OUT/'restriction_route_comparison.csv',index=False)
    known=np.isfinite(legal_dist)&np.isfinite(restricted)
    if (legal_dist[known]+1e-6<restricted[known]).any():raise ValueError('Restriction shortened a route')
    manifest={'policy_version':'AC-02-v1-conservative-exploratory','source_graph_sha256':digest(graph_path),
        'source_walk_xml_sha256':digest(raw),'precedence':['foot=no/private forbids',
        'access=no/private forbids unless foot=yes/designated/permissive',
        'conditional tags remain unresolved','barrier alone is not confirmed closure'],
        'edge_policy':'remove edges with explicit forbidden endpoints or 0.05m-matched geometry vertices',
        'connector_policy':'exclude direct origin/park connector within 0.05m of explicitly forbidden source node; do not resnap',
        'unknown_physical_crossings':'unresolved; no water/fence legality or opening-hours validation',
        'node_counts':nodes.permission_state.value_counts().to_dict(),'removed_directed_edges':len(removed),
        'origin_connector_forbidden':int(origins.forbidden_source_node_count.gt(0).sum()),
        'park_connector_forbidden':int(destinations.forbidden_source_node_count.gt(0).sum()),
        'baseline_missing':int(diag.park_distance_m.isna().sum()),'node_scenario_missing':int(np.isnan(restricted).sum()),
        'connector_scenario_missing':int(np.isnan(legal_dist).sum()),'same_original_snap_nodes':True,
        'coordinator_policy_approval':'pending','physical_connector_validation':'unresolved'}
    (DATA/'walking_permission_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps(manifest,indent=2),flush=True)
    # Disputed connectors are shown against candidates and prohibited-node evidence.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(9,10))
    gpd.read_file(DATA/'jakarta_5kota.gpkg').boundary.plot(ax=ax,color='0.6',linewidth=.5)
    parks.plot(ax=ax,color='green',alpha=.4)
    origins[origins.review_priority].plot(ax=ax,color='darkorange',linewidth=1)
    disputed=connectors[connectors.forbidden_source_node_count.gt(0)]
    if len(disputed):disputed.plot(ax=ax,color='red',linewidth=2)
    ax.set_title('2026 OSM connector screen: orange review, red explicit node conflict\nPhysical access and gates remain unverified')
    ax.set_axis_off();fig.tight_layout();fig.savefig(OUT/'disputed_connectors.png',dpi=140);plt.close(fig)


if __name__=='__main__':main()
