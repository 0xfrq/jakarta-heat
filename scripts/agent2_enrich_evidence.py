"""Recover local provenance, clipping, park tags and source-extent evidence."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import xml.etree.ElementTree as ET
import geopandas as gpd
import pandas as pd
import numpy as np
import osmnx as ox
import rasterio
import requests
from shapely.geometry import box
from agent2_gis import ROOT, OUT, DATA, BASE, sha, table, write_json, check

SOURCE=ROOT.parent/'jakarta-heat'


class Text(HTMLParser):
    def __init__(self):
        super().__init__();self.parts=[];self.links=[];self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ['script','style']:self.skip+=1
        if tag=='a':self.links.extend(v for k,v in attrs if k=='href')
    def handle_endtag(self,tag):
        if tag in ['script','style']:self.skip=max(0,self.skip-1)
    def handle_data(self,data):
        if not self.skip and data.strip():self.parts.append(data.strip())


def official_sources():
    urls=['https://api.worldpop.org/v3/','https://api.worldpop.org/v3/documentation',
          'https://api.worldpop.org/v3/about',
          'https://raw.githubusercontent.com/qgis/QGIS/release-3_44/src/analysis/vector/qgszonalstatistics.cpp']
    result=[]
    for i,url in enumerate(urls):
        try:
            resp=requests.get(url,timeout=30);resp.raise_for_status()
            parser=Text();parser.feed(resp.text)
            if i==0:
                for link in parser.links:
                    if 'method' in link.lower():
                        from urllib.parse import urljoin
                        extra=urljoin(url,link)
                        if extra not in urls:urls.append(extra)
            content='\n'.join(parser.parts) if '<html' in resp.text.lower() else resp.text
            target=OUT/f'official_source_{i}.txt';target.write_text(content,encoding='utf-8')
            result.append({'url':url,'status':resp.status_code,'saved':target.name,'sha256':sha(target),
                           'utc':datetime.now(timezone.utc).isoformat(),
                           'substantive_text_retrieved':len(content)>200,
                           'note':'A JavaScript shell alone does not verify API methodology; use primary documentation via browser/search and TIFF tags.'})
        except requests.RequestException as e:
            result.append({'url':url,'error':str(e)})
    write_json(OUT/'official_sources.json',result)


def park_cache():
    parks=gpd.read_file(DATA/'parks_jakarta.gpkg')
    cities=gpd.read_file(DATA/'jakarta_5kota.gpkg')
    cache=SOURCE/'cache/6e077f2b7acf776f3021034c57eb512f76e96175.json'
    response=json.loads(cache.read_text())
    raw=ox.features._create_gdf([response],cities.to_crs(4326).union_all(),{'leisure':'park'})
    raw=raw[raw.geom_type.isin(['Polygon','MultiPolygon'])].copy()
    raw['park_id']=[f'{kind}_{osm_id}' for kind,osm_id in raw.index]
    raw=raw.to_crs(32748).reset_index(drop=True)
    raw['raw_access']=raw['access'].fillna('unknown')
    raw['included_baseline']=raw.park_id.isin(parks.park_id)
    raw['original_area_m2']=raw.area
    raw['outside_study_area_m2']=raw.geometry.difference(cities.union_all()).area
    raw['city_intersection_count']=[sum(geom.intersection(c).area>1 for c in cities.geometry) for geom in raw.geometry]
    raw['osm_snapshot_utc']=response['osm3s']['timestamp_osm_base']
    keep=['park_id','name','raw_access','included_baseline','original_area_m2','outside_study_area_m2',
          'city_intersection_count','osm_snapshot_utc']
    for col in ['operator','opening_hours','entrance','barrier','fee','foot']:
        if col in raw:keep.append(col)
    table('parks_original_cache_inventory',raw[keep])
    table('parks_excluded_original_tags',raw.loc[~raw.included_baseline,keep])
    common=raw.set_index('park_id').loc[parks.park_id]
    clipped=common.geometry.intersection(cities.union_all())
    delta=[a.symmetric_difference(b).area for a,b in zip(clipped,parks.geometry)]
    check('parks cached OSM polygons reproduce clipped inventory',max(delta)<.01,max(delta))
    raw[keep+['geometry']].to_file(OUT/'geographic_qa.gpkg',layer='original_park_polygons',driver='GPKG')
    info={'cache':str(cache),'cache_sha256':sha(cache),'snapshot':response['osm3s'],
          'raw_polygon_count':len(raw),'baseline':len(parks),'excluded':int((~raw.included_baseline).sum()),
          'excluded_access_tags':raw.loc[~raw.included_baseline,'raw_access'].value_counts().to_dict(),
          'parks_crossing_city_borders':int(raw.city_intersection_count.gt(1).sum()),
          'parks_extend_outside_study':int(raw.outside_study_area_m2.gt(1).sum()),
          'maximum_geometry_difference_m2':max(delta)}
    write_json(OUT/'park_cache_provenance.json',info)
    print('PARK CACHE',info,flush=True)


def source_extent():
    grid=gpd.read_file(DATA/'grid_500m_jakarta.gpkg')
    source=SOURCE/'data/raw/osm/jakarta_all.osm'
    with source.open(encoding='utf-8') as f:
        header=''.join(next(f) for _ in range(3))
    import re
    attrs=dict(re.findall(r'(minlat|minlon|maxlat|maxlon)="([^"]+)"',header))
    bbox=box(float(attrs['minlon']),float(attrs['minlat']),float(attrs['maxlon']),float(attrs['maxlat']))
    projected=gpd.GeoSeries([bbox],crs=4326).to_crs(32748).iloc[0]
    # Densify long latitude/longitude sides before projection.
    projected=gpd.GeoSeries([bbox.segmentize(.001)],crs=4326).to_crs(32748).iloc[0]
    pts=grid.representative_point()
    diag=pd.read_csv(OUT/'network_grid_diagnostics.csv')
    diag['declared_extract_boundary_distance_m']=pts.distance(projected.boundary)
    diag['analysis_area_outside_declared_extract_m2']=grid.geometry.difference(projected).area
    diag['within_1500m_declared_extract_edge']=diag.declared_extract_boundary_distance_m.lt(1500)
    table('network_source_extent',diag[['grid_id','kota','baseline_route_missing',
          'declared_extract_boundary_distance_m','analysis_area_outside_declared_extract_m2','within_1500m_declared_extract_edge']])
    write_json(OUT/'network_source_extent_summary.json',{'declared_osm_bounds':attrs,
        'grid_intersects_outside_declared_extract':int(diag.analysis_area_outside_declared_extract_m2.gt(.01).sum()),
        'outside_area_m2':float(diag.analysis_area_outside_declared_extract_m2.sum()),
        'grids_within1500m_edge':int(diag.within_1500m_declared_extract_edge.sum()),
        'missing_grids_within1500m_edge':int((diag.baseline_route_missing&diag.within_1500m_declared_extract_edge).sum()),
        'limitation':'Header bounds describe declared source coverage, not verified outside-route completeness.'})
    # Observe revision timestamps without parsing/rebuilding the 1.9GB OSM graph.
    import mmap
    first=None;last=None;count=0
    with source.open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as mm:
        for match in re.finditer(rb'timestamp="([0-9TZ:-]+)"',mm):
            value=match.group(1)
            first=value if first is None or value<first else first
            last=value if last is None or value>last else last
            count+=1
    write_json(OUT/'osm_revision_timestamp_evidence.json',{'earliest_revision_utc':first.decode() if first else None,
        'latest_revision_utc':last.decode() if last else None,'revision_timestamp_count':count,
        'source_sha256':sha(source),'source_url':None,
        'meaning':'Latest object revision is a lower bound on extraction date; it does not establish an exact snapshot date.'})
    counters=Counter()
    filtered=SOURCE/'data/raw/osm/jakarta_all_walk.osm'
    for event,el in ET.iterparse(filtered,events=['end']):
        if el.tag in ['node','way']:
            tags={tag.attrib['k']:tag.attrib['v'] for tag in el.findall('tag')}
            for k,v in tags.items():
                if k in ['barrier','access','foot','oneway:foot','foot:conditional','access:conditional','service']:
                    counters[(el.tag,k,v)]+=1
            el.clear()
    table('raw_walk_restriction_tags',pd.DataFrame([{'element':e,'tag':k,'value':v,'count':n} for (e,k,v),n in counters.items()]))


def age_alignment():
    pop=SOURCE/'data/raw/worldpop/idn_pop_2024.tif'
    age=SOURCE/'data/raw/worldpop/age/jakarta_child_2024.tif'
    elder=SOURCE/'data/raw/worldpop/age/jakarta_elderly_2024.tif'
    with rasterio.open(pop) as p,rasterio.open(age) as a,rasterio.open(elder) as e:
        from rasterio.windows import from_bounds
        win=from_bounds(*a.bounds,transform=p.transform).round_offsets().round_lengths()
        pv=p.read(1,window=win,masked=True)
        av=a.read(1,masked=True);ev=e.read(1,masked=True)
        offsets=~p.transform*(a.transform.c,a.transform.f)
        common=~(np.ma.getmaskarray(pv)|np.ma.getmaskarray(av)|np.ma.getmaskarray(ev))&(pv>0)
        childratio=np.asarray(av)[common]/np.asarray(pv)[common]
        elderratio=np.asarray(ev)[common]/np.asarray(pv)[common]
        vals=pd.DataFrame({'child_share':childratio,'elderly_share':elderratio})
        rounded=vals.round(5).value_counts().rename('pixels').reset_index()
        table('age_source_pixel_ratio_groups',rounded)
        write_json(OUT/'age_alignment_summary.json',{'same_crs':p.crs==a.crs==e.crs,'same_pixel_size':bool(np.allclose(p.res,a.res)),
            'age_origin_offset_total_pixels':offsets,'integer_pixel_offsets':bool(np.allclose(offsets,np.round(offsets),atol=1e-5)),
            'age_shape_matches_total_window':pv.shape==av.shape,'common_populated_pixels':int(common.sum()),
            'unique_rounded_child_share':int(vals.child_share.round(5).nunique()),
            'unique_rounded_elderly_share':int(vals.elderly_share.round(5).nunique()),
            'major_share_pairs':rounded.head(10).to_dict('records')})
    z=pd.read_csv(OUT/'population_raster_recomputation.csv')
    z=z[(z.population>0)&z.pop_child.eq(0)&z.pop_elderly.eq(0)].copy()
    z['age_source_no_support']=z.pop_child_fractional_pixels.eq(0)|z.pop_elderly_fractional_pixels.eq(0)
    z['evidence']=np.where(z.age_source_no_support,
        'No valid fractional pixel support in API age raster; zero sum does not verify demographic absence',
        'Valid API age pixels exist but sum to zero; verify modeled zero rather than infer census absence')
    table('zero_age_populated_grid_diagnostics',z)


if __name__=='__main__':
    official_sources();park_cache();source_extent();age_alignment()
