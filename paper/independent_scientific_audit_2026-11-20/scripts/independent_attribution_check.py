import pandas as pd, numpy as np, os
BASE=r"D:\jakarta-heat-paper"
OUT=r"D:\jakarta-heat-paper\paper\independent_scientific_audit_2026-11-20\evidence"
c=pd.read_csv(os.path.join(BASE,r"outputs\remediation\tables\component_contributions.csv"))
L=c.normalized_lst; V=c.normalized_ndvi_low; P=c.normalized_pop; A=c.normalized_vuln; D=c.normalized_park_deficit
scores={
 "m3": .4*L+.3*V+.3*P,
 "reweighting": .3*L+.2*V+.25*P,
 "age_swap": .4*L+.3*V+.05*P+.25*A,
 "park_addition": .4*L+.3*V+.3*P+.25*D,
 "age_reweight": .3*L+.2*V+.25*A,
 "park_reweight": .3*L+.2*V+.25*P+.25*D,
 "age_park": .4*L+.3*V+.05*P+.25*A+.25*D,
 "m4": .3*L+.2*V+.25*A+.25*D,
}
def top(s): return set(c.loc[s.rank(ascending=False,method="first")<=254,"grid_id"])
t3=top(scores["m3"]); t4=top(scores["m4"])
rows=[]
for k,s in scores.items():
    t=top(s)
    rows.append({"scenario":k,"n_top":len(t),
                 "overlap_M3":len(t&t3),"jaccard_M3":len(t&t3)/len(t|t3),
                 "overlap_M4":len(t&t4),"jaccard_M4":len(t&t4)/len(t|t4)})
r=pd.DataFrame(rows)
print(r.to_string(index=False,float_format=lambda x:f"{x:.6f}"))
r.to_csv(os.path.join(OUT,"independent_attribution_comparisons.csv"),index=False)
