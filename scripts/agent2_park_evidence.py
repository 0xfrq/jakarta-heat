"""AC-01: archived source tags, unresolved evidence hierarchy and alternatives."""
from pathlib import Path
from datetime import datetime, timezone
import heapq
import argparse
from itertools import count
import json
import geopandas as gpd
import numpy as np
import pandas as pd
import requests
from agent2_gis import load_light_graph
from aggregate_demographics import digest

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/processed';OLD=ROOT/'outputs/qa/agent2';OUT=ROOT/'outputs/qa/remediation_agent2'


def two_destinations(graph,nodes,snaps,parks):
    """Two nearest distinct park labels on a directed multigraph; no new links."""
    serial=count();queue=[];settled={}
    for node,snap,park in zip(nodes,snaps,parks):
        heapq.heappush(queue,(float(snap),next(serial),int(node),str(park)))
    reverse=graph.reverse(copy=False)
    while queue:
        cost,_,node,park=heapq.heappop(queue)
        labels=settled.setdefault(node,[])
        if len(labels)>=2 or any(p==park for _,p in labels):continue
        labels.append((cost,park))
        for other,edges in reverse.adj[node].items():
            current=settled.get(other,[])
            if len(current)<2 and not any(p==park for _,p in current):
                w=min(e['length'] for e in edges.values())
                heapq.heappush(queue,(cost+w,next(serial),other,park))
    return settled


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh-evidence',action='store_true',help='Fetch official context pages; offline replay uses archived evidence')
    args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    cache=ROOT/'cache/6e077f2b7acf776f3021034c57eb512f76e96175.json'
    raw=json.loads(cache.read_text(encoding='utf-8'))
    tagmap={f"{e['type']}_{e['id']}":e.get('tags',{}) for e in raw['elements'] if e.get('tags',{}).get('leisure')=='park'}
    parks=gpd.read_file(DATA/'parks_jakarta.gpkg')
    priority=pd.read_csv(OUT/'park_impact_priority_auditor.csv').head(20)
    topids=set(priority.park_id)
    # These documents establish name/location/context, not exact mapped entrance or current opening.
    sources={
        'way_517498552':('https://www.beritajakarta.id/read/6836/tahun-2015-dki-bangun-15-taman-terpadu','',
            'Municipal report names a planned Taman Walang improvement; dated plan does not prove current opening or polygon identity.'),
        'way_1158752464':('https://timur.jakarta.go.id/kecamatan/Makasar/informasi/potensi','',
            'Municipal district listing names Taman Segitiga Intirub at Jl Komodor Halim; no verified entrance or operating hours.'),
        'way_155961172':('https://m.beritajakarta.id/read/128999/pt-jiep-berhasil-kembalikan-fungsi-hutan-kota-di-kawasan-industri-pulogadung','',
            'Municipal report describes restoration and intended jogging/public use; exact OSM polygon match and current access unresolved.'),
        'way_404675353':('https://smartcity.jakarta.go.id/id/blog/nikmati-jakarta-bareng-bus-wisata-transjakarta/','',
            'Official tourism page names RPTRA Kalijodo; RTH/RPTRA subareas and exact mapped entrance remain unresolved.')}
    archive=OUT/'park_official_evidence_sources.json'
    previous=json.loads(archive.read_text(encoding='utf-8')) if archive.exists() else []
    archived={r['park_id']:r for r in previous}
    retrieved=datetime.now(timezone.utc).isoformat() if args.refresh_evidence else (previous[0]['checked_utc'] if previous else '')
    evidence_records=[]
    for park_id,(url,published,note) in sources.items():
        if not args.refresh_evidence:
            rec=archived.get(park_id,{'park_id':park_id,'url':url,'publication_date':published,'checked_utc':'',
                'limited_finding':note,'retrieval_status':'not_fetched_offline','proves_current_public_opening':False,'proves_entrance_location':False})
            rec['publication_date']=published
            evidence_records.append(rec)
            continue
        rec={'park_id':park_id,'url':url,'publication_date':published,'checked_utc':retrieved,'limited_finding':note,
             'proves_current_public_opening':False,'proves_entrance_location':False}
        try:
            resp=requests.get(url,timeout=20)
            target=OUT/f'park_source_{park_id}.html';target.write_bytes(resp.content)
            rec.update(http_status=resp.status_code,snapshot_path=target.name,sha256=digest(target))
        except requests.RequestException as exc:rec['retrieval_error']=str(exc)
        evidence_records.append(rec)
    (OUT/'park_official_evidence_sources.json').write_text(json.dumps(evidence_records,indent=2),encoding='utf-8')
    rows=[]
    for row in parks.itertuples():
        tags=tagmap[row.park_id];access=str(tags.get('access','unknown')).lower()
        conditional=any(tags.get(k) for k in ['access:conditional','foot:conditional','opening_hours'])
        state='conditional_unverified' if conditional else ('positive_osm_tag_unverified' if access in ['yes','permissive'] else 'unknown')
        if access in ['private','no','customers','permit']:state='excluded_restricted'
        source=sources.get(row.park_id,('','','No independent access/entrance evidence located in this targeted review.'))
        rows.append({'park_id':row.park_id,'name':row.name,'access_evidence_state':state,
            'public_access_verified':False,'entrance_verified':False,'baseline_candidate':True,
            'initial_auditor_top20':row.park_id in topids,'review_status':'unresolved',
            'source_access_tag':access,'source_snapshot_utc':raw['osm3s']['timestamp_osm_base'],
            'raw_tags_json':json.dumps(tags,ensure_ascii=False,sort_keys=True),
            **{key:tags.get(key,'') for key in ['operator','operator:type','opening_hours','entrance','barrier','fee','foot','access:conditional','foot:conditional']},
            'evidence_url':source[0],'evidence_publication_date':source[1],'evidence_checked_utc':retrieved,
            'evidence_scope':source[2],'exact_osm_polygon_identity_verified':False})
    evidence=pd.DataFrame(rows)
    evidence.to_csv(DATA/'park_access_evidence.csv',index=False)
    evidence[evidence.initial_auditor_top20].to_csv(OUT/'park_top20_review.csv',index=False)
    # Zero verified entrances is a meaningful empty inventory; never synthesize gates from centroids.
    empty=gpd.GeoDataFrame({'park_id':pd.Series(dtype='str'),'evidence_url':pd.Series(dtype='str'),
        'verified_on':pd.Series(dtype='str'),'permission_state':pd.Series(dtype='str')},geometry=gpd.GeoSeries([],crs=32748))
    empty.to_file(DATA/'validated_park_entrances.gpkg',layer='verified_entrances',driver='GPKG',geometry_type='Point')
    diag=pd.read_csv(OLD/'network_grid_diagnostics.csv')
    dest=pd.read_csv(OLD/'park_network_destinations.csv')
    graph,_=load_light_graph(DATA/'walk_jakarta_all.graphml')
    print('Compute two distinct candidate destinations on fixed full-graph nodes',flush=True)
    second=two_destinations(graph,dest.full_node,dest.park_snap_m,dest.park_id)
    alternatives=[]
    baseline=pd.read_csv(OLD/'baseline/agent3/data/processed/modeling/priority_models.csv').set_index('grid_id')
    for row in diag.itertuples():
        rank=baseline.loc[row.grid_id,'m4_rank']
        for position,(distance,park) in enumerate(second.get(int(row.full_node),[]),1):
            alternatives.append({'grid_id':row.grid_id,'candidate_order':position,'park_id':park,
                'modeled_network_distance_m':distance+row.full_snap_m,'origin_node_id':int(row.full_node),
                'auditor_top20_winning_park':row.full_nearest_park_id in topids,
                'near_baseline_top10_cutoff':bool(pd.notna(rank) and 220<=rank<=290),
                'near_500_or_1000m':bool(pd.notna(row.park_distance_m) and min(abs(row.park_distance_m-500),abs(row.park_distance_m-1000))<=50),
                'access_verified':False,'entrance_verified':False,'metric_scope':'2026 broad OSM candidate full-graph proxy'})
    alternatives=pd.DataFrame(alternatives)
    first=alternatives[alternatives.candidate_order.eq(1)].set_index('grid_id').modeled_network_distance_m.reindex(diag.grid_id)
    np.testing.assert_allclose(first,diag.full_distance_m,atol=1e-6,equal_nan=True)
    alternatives.to_csv(OUT/'park_alternative_destinations.csv',index=False)
    top=diag.grid_id.map(baseline.m4_top)
    summary={'candidate_count':len(evidence),'evidence_states':evidence.access_evidence_state.value_counts().to_dict(),
        'verified_public_access':0,'verified_entrances':0,'initial_top20_reviewed_or_unresolved':int(evidence.initial_auditor_top20.sum()),
        'baseline_top_m4_n':int(top.sum()),'baseline_top_m4_winners_in_top20':int((top&diag.full_nearest_park_id.isin(topids)).sum()),
        'origins_with_second_candidate':int(alternatives.candidate_order.eq(2).sum()),
        'official_context_documents':len(sources),'inventory_changed':False,
        'policy':'broad non-explicitly-restricted candidates; positive-only is a destination coverage stress test',
        'coordinator_approval':'pending; no actual 2024 public-access claim'}
    (OUT/'park_evidence_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2),flush=True)


if __name__=='__main__':main()
