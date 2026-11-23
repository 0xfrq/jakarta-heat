import pandas as pd, numpy as np, os, json
BASE=r"D:\jakarta-heat-paper"
OUT=r"D:\jakarta-heat-paper\paper\independent_scientific_audit_2026-11-20\evidence"
p=pd.read_csv(os.path.join(BASE,r"data\processed\modeling\priority_models.csv"))
m=pd.read_csv(os.path.join(BASE,r"data\processed\modeling\merged_grid.csv")).set_index("grid_id")
v=p[p.valid]
top4=v[v.m4_top]; mm=m.loc[top4.grid_id]
near=m.loc[v.grid_id]; near=near[near.park_distance_m<=500]
out={
 "top_budget":int(len(top4)),
 "m4_top_cutoff":float(top4.m4_score.min()),
 "near500_n":int(len(near)),
 "near500_in_top4":int(near.index.isin(top4.grid_id).sum()),
 "near500_max_score":float(v.set_index("grid_id").loc[near.index,"m4_score"].max()),
 "top_min_park_distance":float(mm.park_distance_m.min()),
 "top_at_cap":int((mm.park_distance_m>=1000).sum()),
 "top_population":float(mm.population.sum()),
 "total_population":float(m.loc[v.grid_id,"population"].sum()),
 "top_area_km2":float(mm.area_km2.sum()),
 "example":{"grid_id":"JKT_R056_C048","lst_c":float(m.loc["JKT_R056_C048","lst_c"]),"population":float(m.loc["JKT_R056_C048","population"]),"park_distance_m":float(m.loc["JKT_R056_C048","park_distance_m"]),"m4_score":float(v.set_index("grid_id").loc["JKT_R056_C048","m4_score"]),"m4_rank":int(v.set_index("grid_id").loc["JKT_R056_C048","m4_rank"])}
}
out["example"]["top_cooler"]=int((mm.lst_c<out["example"]["lst_c"]).sum())
print(json.dumps(out,indent=2))
with open(os.path.join(OUT,"independent_cutoff_check.json"),"w",encoding="utf-8") as f: json.dump(out,f,indent=2)
