"""TM-02 bounded historical feasibility pilot, not a temporal-stability test.

The same three 3km squares and query predicates are frozen before requests.
Inventory/topology availability alone cannot validate physical openings or M4.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse
import json
import geopandas as gpd
import pandas as pd
import requests
from shapely.geometry import box
from aggregate_demographics import digest
from walking_network import walk_allowed
from agent2_connector_remediation import permission_state

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/qa/remediation_agent2/historical_pilot'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--execute',action='store_true',help='Execute bounded requests; otherwise save predeclared queries only')
    a=p.parse_args();OUT.mkdir(parents=True,exist_ok=True)
    parks=gpd.read_file(ROOT/'data/processed/parks_jakarta.gpkg').set_index('park_id')
    records=[]
    for gid in ['way_517498552','way_1158752464','way_404675353']:
        point=parks.loc[gid].geometry.representative_point()
        polygon=gpd.GeoSeries([box(point.x-1500,point.y-1500,point.x+1500,point.y+1500)],crs=32748).to_crs(4326).iloc[0]
        west,south,east,north=polygon.bounds
        bbox=f'{south:.8f},{west:.8f},{north:.8f},{east:.8f}'
        for stamp in ['2024-12-31T23:59:59Z','2026-11-19T11:02:20Z']:
            stem=f'{gid}_{stamp[:10]}'
            query=f'[out:json][timeout:20][date:"{stamp}"];(nwr["leisure"="park"]({bbox});way["highway"]({bbox}););(._;>;);out meta;'
            qpath=OUT/f'{stem}.overpassql';qpath.write_text(query,encoding='utf-8')
            record={'park_id':gid,'snapshot_requested_utc':stamp,'aoi_utm_square_m':3000,
                'bbox_south_west_north_east':bbox,'query_path':str(qpath.relative_to(ROOT)),'query_sha256':digest(qpath),
                'endpoint':'https://overpass-api.de/api/interpreter','attempted_utc':datetime.now(timezone.utc).isoformat(),
                'status':'planned_not_executed','route_comparison_status':'not_available','temporal_stability_claim':False,
                'snapshot_is_physical_opening_evidence':False}
            if a.execute:
                try:
                    resp=requests.post(record['endpoint'],data={'data':query},timeout=30)
                    record['http_status']=resp.status_code
                    target=OUT/f'{stem}.response';target.write_bytes(resp.content)
                    record.update(response_path=str(target.relative_to(ROOT)),response_sha256=digest(target))
                    resp.raise_for_status();data=resp.json()
                    if 'remark' in data:raise ValueError(data['remark'])
                    elements=data['elements']
                    record.update(status='inventory_snapshot_retrieved_not_route_validated',
                        mapped_park_elements=sum(e.get('tags',{}).get('leisure')=='park' for e in elements),
                        highway_ways=sum(e['type']=='way' and 'highway' in e.get('tags',{}) for e in elements),
                        policy_allowed_highway_ways=sum(e['type']=='way' and walk_allowed(e.get('tags',{})) for e in elements),
                        explicit_forbidden_nodes=sum(e['type']=='node' and permission_state(e.get('tags',{}))=='explicitly_forbidden' for e in elements),
                        response_osm_base=data.get('osm3s',{}).get('timestamp_osm_base',''))
                except (requests.RequestException,ValueError,KeyError) as exc:
                    record.update(status='unavailable',failure=str(exc))
            records.append(record)
            pd.DataFrame(records).to_csv(OUT.parent/'historical_osm_pilot.csv',index=False)
            print(gid,stamp,record['status'],record.get('failure',''),flush=True)
    plan={'scope':'exploratory availability pilot; TM-01 scientific temporal scope not yet signed',
        'selection':'three named influential destinations from initial top20; selection is purposive, not representative',
        'aoi':'3km square centered on current park representative point; identical both dates',
        'snapshots':['2024-12-31T23:59:59Z','2026-11-19T11:02:20Z'],
        'proposed_materiality_not_approved':{'destination_or_route_availability_change_fraction':.05,
            'threshold_crossing_fraction':.05,'fixed_set_top10_jaccard_below':.90},
        'limitations':'Query availability or raw tag counts cannot establish matching legal routes, temporal stability or physical park opening. No comparison effect is fabricated.',
        'next_if_historical_claims_retained':'Coordinator signs thresholds and AC-01/AC-02 policy; build comparable restricted routes and fixed-normalization M4 within supported AOIs before full reconstruction.'}
    (OUT/'predeclared_plan.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')


if __name__=='__main__':main()
