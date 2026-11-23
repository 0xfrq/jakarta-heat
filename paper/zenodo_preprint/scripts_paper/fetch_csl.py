import json, time, urllib.request

dois=["10.1038/s41598-020-66288-z","10.1073/pnas.2024792118","10.1093/pnasnexus/pgae360",
"10.1038/s41467-024-47197-5","10.1038/s41467-023-39698-6","10.1038/s41597-022-01307-4",
"10.1038/s41467-021-22799-5","10.1038/s41598-024-67277-2","10.3390/land15060989",
"10.1016/j.ijdrr.2026.106057","10.1016/j.ufug.2025.128790","10.1016/j.rse.2003.11.005",
"10.1016/j.rsase.2023.101062","10.1016/j.habitatint.2023.102924","10.1016/j.landurbplan.2016.05.017"]

for d in dois:
    for attempt in range(3):
        try:
            req=urllib.request.Request("https://doi.org/"+d, headers={"Accept":"application/vnd.citationstyles.csl+json","User-Agent":"JakartaHeatPaper/1.0"})
            with urllib.request.urlopen(req,timeout=60) as r:
                m=json.load(r)
            print(d,"|",m.get("article-number"),"|",m.get("volume"),m.get("issue"),m.get("page"),"|",(m.get("title") or "")[:70])
            break
        except Exception as e:
            print("retry",d,attempt,e); time.sleep(3)
    time.sleep(1)
