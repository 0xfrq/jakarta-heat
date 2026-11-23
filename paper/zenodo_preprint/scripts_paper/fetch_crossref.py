import json, time, urllib.request

dois = [
"10.1002/qj.49710845502","10.1016/j.rse.2003.11.005","10.1016/S0034-4257(03)00079-8",
"10.3390/rs11010048","10.1021/es2030438","10.1016/j.ecolind.2012.01.001",
"10.1016/j.scitotenv.2016.10.195","10.1016/j.rsase.2023.101062",
"10.1088/1755-1315/737/1/012002","10.14710/geoplanning.11.1.31-42",
"10.1038/s41598-020-66288-z","10.1016/j.habitatint.2023.102924",
"10.9734/bjecc/2017/33529","10.1088/1748-9326/ab3b99","10.1073/pnas.2024792118",
"10.1016/j.socscimed.2006.07.030","10.1289/ehp.0900683","10.1016/j.wace.2013.07.004",
"10.1093/pnasnexus/pgae360","10.1016/j.landurbplan.2020.103907","10.1186/1476-069X-8-40",
"10.1016/j.maturitas.2011.03.008","10.1016/j.envint.2014.11.016","10.1038/s41467-024-47197-5",
"10.3390/ijerph15040640","10.1016/j.landurbplan.2014.01.017","10.1016/j.landurbplan.2016.05.017",
"10.1016/j.landurbplan.2016.06.008","10.1016/j.landurbplan.2007.01.014","10.3390/land15060989",
"10.3390/ijerph16244894","10.1038/s41598-024-67277-2","10.1016/j.landurbplan.2010.05.006",
"10.1016/j.heliyon.2019.e01339","10.1080/13658810600661508","10.1111/j.1467-985X.2005.00350.x",
"10.1111/j.1467-985X.2012.01059.x","10.1007/s11205-017-1832-9","10.1111/j.1538-4632.1995.tb00338.x",
"10.1111/j.1538-4632.1992.tb00261.x","10.1111/j.2517-6161.1995.tb02031.x","10.1214/aos/1013699998",
"10.1068/b35097","10.1111/tgis.12073","10.1038/s41467-023-39698-6","10.1016/j.healthplace.2009.06.002",
"10.1068/b29120","10.1038/s41597-022-01307-4","10.1016/j.ufug.2025.128790",
"10.1016/j.ijdrr.2026.106057","10.1038/s41467-021-22799-5","10.1016/j.landurbplan.2023.104836",
"10.1016/j.ecolind.2018.09.058","10.1016/j.uclim.2022.101255","10.1016/j.ufug.2022.127685",
"10.5258/SOTON/WP00841",
]

def get(doi):
    req=urllib.request.Request("https://api.crossref.org/works/"+doi,
        headers={"User-Agent":"JakartaHeatPaper/1.0 (mailto:research@example.org)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["message"]

rows=[]
for d in dois:
    for attempt in range(4):
        try:
            m=get(d); break
        except Exception as e:
            print("retry",d,attempt,e); time.sleep(5)
    else:
        rows.append({"doi":d,"title":"ERROR","authors":"","year":"","venue":"","volume":"","issue":"","page":"","type":""}); continue
    def name(a):
        fam=a.get("family",""); giv=a.get("given","")
        return (fam+", "+giv).strip(", ")
    rows.append({
        "doi":d,
        "title": (m.get("title") or [""])[0],
        "authors": "; ".join(name(a) for a in m.get("author",[])),
        "year": (m.get("issued",{}).get("date-parts",[[None]])[0][0]),
        "venue": (m.get("container-title") or [""])[0],
        "volume": m.get("volume",""), "issue": m.get("issue",""), "page": m.get("page",""),
        "type": m.get("type",""),
    })
    time.sleep(1.2)

with open(r"D:\jakarta-heat-paper\paper\zenodo_preprint\scripts_paper\crossref_metadata.json","w",encoding="utf-8") as f:
    json.dump(rows,f,ensure_ascii=False,indent=2)
for x in rows:
    print(f'{x["doi"]} | {x["year"]} | {x["title"][:58]} | {x["venue"][:36]} | {x["volume"]}({x["issue"]}):{x["page"]} | {x["authors"][:70]}')

