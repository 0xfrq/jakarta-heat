"""Retrieve versioned buffered WorldPop age surfaces; never replace old rasters."""
from pathlib import Path
import argparse
from datetime import datetime, timezone
import json
import geopandas as gpd
import requests
from shapely.geometry import mapping, box
from aggregate_demographics import digest

ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--boundary',type=Path,default=ROOT/'data/processed/jakarta_5kota.gpkg')
    p.add_argument('--output',type=Path,default=ROOT/'data/raw/worldpop/age_buffered')
    p.add_argument('--buffer-m',type=float,default=1000.)
    p.add_argument('--timeout',type=float,default=45.)
    a=p.parse_args()
    if a.buffer_m<200:raise ValueError('Use >=200m buffer to retain overlapping source pixel centres')
    boundary=gpd.read_file(a.boundary).to_crs(32748).union_all()
    geom=gpd.GeoSeries([box(*boundary.buffer(a.buffer_m).bounds)],crs=32748).to_crs(4326).iloc[0]
    a.output.mkdir(parents=True,exist_ok=True)
    records=[]
    for group,ages in {'child':[0,14],'elderly':[65,90]}.items():
        payload={'geojson':mapping(geom),'year':2024,'layer':'agesex','age_range':ages,
                 'sex':'both','bands':'sum','resolution':'100m'}
        target=a.output/f'jakarta_{group}_2024_buffered.tif'
        item={'group':group,'url':'https://api.worldpop.org/v3/raster','request':payload,
              'retrieved_utc':datetime.now(timezone.utc).isoformat(),'buffer_m':a.buffer_m}
        if target.exists():raise FileExistsError(f'Preserve existing retrieval: {target}')
        (a.output/f'{group}_request.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
        try:
            resp=requests.post(item['url'],json=payload,timeout=a.timeout)
            item['http_status']=resp.status_code
            resp.raise_for_status()
            if 'tiff' not in resp.headers.get('Content-Type','').lower():
                raise ValueError('Response is not a GeoTIFF: '+resp.text[:200])
            target.write_bytes(resp.content)
            item.update(status='retrieved_not_yet_compatibility_validated',path=str(target),sha256=digest(target))
        except (requests.RequestException,ValueError) as exc:
            item.update(status='unavailable',error=str(exc))
        records.append(item)
        print(group,item['status'],item.get('error',''),flush=True)
        (a.output/'retrieval_manifest.json').write_text(json.dumps(records,indent=2),encoding='utf-8')

if __name__=='__main__':main()
