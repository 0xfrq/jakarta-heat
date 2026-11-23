import re, json, time, urllib.request, urllib.parse, os, csv
BIB=r"D:\jakarta-heat-paper\paper\zenodo_preprint\input\References.bib"
OUT=r"D:\jakarta-heat-paper\paper\independent_scientific_audit_2026-11-20\evidence"
s=open(BIB,encoding="utf-8").read()
entries=re.findall(r'@(\w+)\{([^,]+),(.*?)\n\}',s,re.S)

def field(body,name):
    m=re.search(r'\n\s*'+name+r'\s*=\s*\{(.*?)\}\s*,?',body,re.S|re.I)
    return re.sub(r'\s+',' ',m.group(1)).strip() if m else ""

rows=[]
for typ,key,body in entries:
    doi=field(body,"doi")
    title=field(body,"title")
    year=field(body,"year")
    journal=field(body,"journal") or field(body,"howpublished")
    vol=field(body,"volume"); num=field(body,"number"); pages=field(body,"pages")
    rows.append({"key":key,"type":typ,"doi":doi,"bib_title":title,"bib_year":year,"bib_venue":journal,"bib_volume":vol,"bib_number":num,"bib_pages":pages})

def fetch(doi):
    req=urllib.request.Request("https://doi.org/"+doi,headers={"Accept":"application/vnd.citationstyles.csl+json","User-Agent":"JakartaHeatPaper-Audit/1.0"})
    with urllib.request.urlopen(req,timeout=30) as r:
        return json.load(r)

for i,row in enumerate(rows):
    if not row["doi"]:
        row["status"]="NO_DOI"
        continue
    data=None; err=""
    for attempt in range(3):
        try:
            data=fetch(row["doi"]); break
        except Exception as e:
            err=str(e); time.sleep(2)
    if data is None:
        row["status"]="FETCH_ERROR"; row["error"]=err; continue
    row["status"]="OK"
    row["doi_title"]=data.get("title","")
    row["doi_year"]=data.get("issued",{}).get("date-parts",[[None]])[0][0]
    row["doi_venue"]=data.get("container-title","")
    row["doi_volume"]=data.get("volume","")
    row["doi_issue"]=data.get("issue","")
    row["doi_page"]=data.get("page","") or data.get("article-number","")
    auth=data.get("author",[])
    row["doi_authors"]="; ".join((a.get("family","")+", "+a.get("given","")).strip(", ") for a in auth[:6])
    row["doi_n_authors"]=len(auth)
    time.sleep(0.8)

outcsv=os.path.join(OUT,"reference_verification.csv")
fields=[]
for r in rows:
    for k in r:
        if k not in fields: fields.append(k)
with open(outcsv,"w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
print("wrote",outcsv,"rows",len(rows))
from collections import Counter
print(Counter(r["status"] for r in rows))
for r in rows:
    if r["status"]!="OK": print("NON-OK",r["key"],r["status"],r.get("error",""))
