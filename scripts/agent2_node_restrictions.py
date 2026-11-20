"""Conservative explicit OSM-node restrictions sensitivity on existing length graph.

No network download/rebuild. Match source node vertices to saved edge vertices within
5cm numerical tolerance. Remove incident edges: no inferred openings or gate access.
This is a scenario, not a validated public pedestrian network.
"""
import xml.etree.ElementTree as ET
from pathlib import Path
import json
import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from shapely.geometry import Point
from scipy.spatial import cKDTree
from agent2_gis import ROOT,OUT,DATA,load_light_graph,nearest,route,table,write_json
from walking_network import values

SOURCE=ROOT


def main():
    blocked=[]
    all_restrictions=[]
    for _,el in ET.iterparse(SOURCE/'data/raw/osm/jakarta_all_walk.osm',events=['end']):
        if el.tag=='node':
            tags={t.attrib['k']:t.attrib['v'] for t in el.findall('tag')}
            foot=values(tags.get('foot'));access=values(tags.get('access'))
            reject=bool(foot&{'no','private'} or (access&{'no','private'} and not foot&{'yes','designated','permissive'}))
            if reject:
                blocked.append({'osm_node_id':int(el.attrib['id']),'lon':float(el.attrib['lon']),
                    'lat':float(el.attrib['lat']),'foot':tags.get('foot'),'access':tags.get('access'),
                    'barrier':tags.get('barrier'),'reason':'explicit_node_foot_or_access_restriction'})
            el.clear()
        elif el.tag=='way':el.clear()
    b=pd.DataFrame(blocked)
    points=gpd.GeoDataFrame(b,geometry=gpd.points_from_xy(b.lon,b.lat),crs=4326).to_crs(32748)
    points.to_file(OUT/'geographic_qa.gpkg',layer='explicit_restricted_osm_nodes',driver='GPKG')
    tree=cKDTree(np.column_stack([points.geometry.x,points.geometry.y]))
    graph,_=load_light_graph(SOURCE/'data/processed/walk_jakarta_all.graphml')
    grid=gpd.read_file(DATA/'grid_500m_jakarta.gpkg')
    parks=gpd.read_file(DATA/'parks_jakarta.gpkg')
    # Fix connectors on the original graph: isolates the edge-policy effect and
    # prevents a forbidden node being silently snapped across a gate elsewhere.
    gn,gs,gxy=nearest(graph,grid.representative_point())
    pn,ps,pxy=nearest(graph,parks.representative_point())
    retained=set(b.osm_node_id)&set(graph)
    removed=[]
    ns='{http://graphml.graphdrawing.org/xmlns}'
    keys={}
    print('Scan existing simplified edge vertices for explicit restricted source nodes',flush=True)
    for _,el in ET.iterparse(SOURCE/'data/processed/walk_jakarta_all.graphml',events=['end']):
        tag=el.tag.removeprefix(ns)
        if tag=='key':keys[el.attrib['id']]=el.attrib.get('attr.name');el.clear()
        elif tag=='node':el.clear()
        elif tag=='edge':
            u,v,k=int(el.attrib['source']),int(el.attrib['target']),int(el.attrib.get('id',0))
            fields={keys[x.attrib['key']]:x.text for x in el.findall(ns+'data')}
            if u in retained or v in retained:
                removed.append((u,v,k))
            elif 'geometry' in fields:
                line=shapely.from_wkt(fields['geometry'])
                xy=np.array(line.coords)
                if tree.query(xy,distance_upper_bound=.05)[0].min()<.05:
                    removed.append((u,v,k))
            el.clear()
    graph.remove_edges_from(removed)
    eligible=np.array([n not in retained for n in pn])
    dist,win=route(graph,pn[eligible],ps[eligible],parks.loc[eligible,'park_id'])
    diag=pd.read_csv(OUT/'network_grid_diagnostics.csv')
    diag['explicit_node_restriction_scenario_distance_m']=[dist.get(n,np.nan)+s for n,s in zip(gn,gs)]
    diag['explicit_node_restriction_scenario_snap_m']=gs
    diag['restriction_scenario_same_origin_node']=np.array(gn)==diag.full_node
    table('network_grid_diagnostics',diag)
    table('node_restriction_scenario',diag[['grid_id','kota','park_distance_m','full_distance_m',
          'explicit_node_restriction_scenario_distance_m','explicit_node_restriction_scenario_snap_m','restriction_scenario_same_origin_node']])
    table('explicit_restricted_osm_nodes',b)
    summary={'blocked_source_nodes':len(b),'blocked_retained_graph_nodes':len(retained),'removed_directed_edges':len(removed),
             'known_routes':int(diag.explicit_node_restriction_scenario_distance_m.notna().sum()),
             'missing_routes':int(diag.explicit_node_restriction_scenario_distance_m.isna().sum()),
             'baseline_known_now_missing':int((diag.park_distance_m.notna()&diag.explicit_node_restriction_scenario_distance_m.isna()).sum()),
             'same_origin_node':int(diag.restriction_scenario_same_origin_node.sum()),
             'policy':'Fixed original snap nodes/connectors. Exclude parks snapped onto forbidden nodes. Block explicit node foot=no/private or access=no/private unless foot=yes/designated/permissive; remove crossing simplified edges, 0.05m vertex tolerance',
             'status':'CONSERVATIVE SENSITIVITY ONLY; ignores conditional hours and not verified in field'}
    write_json(OUT/'node_restriction_summary.json',summary)
    print(summary,flush=True)


if __name__=='__main__':main()
