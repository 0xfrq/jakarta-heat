import pandas as pd, numpy as np, os
BASE=r"D:\jakarta-heat-paper"
OUT=r"D:\jakarta-heat-paper\paper\independent_scientific_audit_2026-11-20\evidence"
p=pd.read_csv(os.path.join(BASE,r"data\processed\modeling\priority_models.csv"))
v=p[p.valid].copy()
rows=[]
for a,b in [("m1","m2"),("m1","m3"),("m1","m4"),("m2","m3"),("m2","m4"),("m3","m4")]:
    # ranks are saved; recompute rank from scores to be independent of saved rank
    ra=v[a+"_score"].rank(ascending=False,method="first")
    rb=v[b+"_score"].rank(ascending=False,method="first")
    ta=set(v.loc[ra<=254,"grid_id"]); tb=set(v.loc[rb<=254,"grid_id"])
    rows.append({"pair":f"{a.upper()}-{b.upper()}",
                 "spearman":v[a+"_score"].corr(v[b+"_score"],method="spearman"),
                 "kendall":v[a+"_score"].corr(v[b+"_score"],method="kendall"),
                 "jaccard_10":len(ta&tb)/len(ta|tb),
                 "shared_10":len(ta&tb),
                 "mean_abs_rank_shift":float((ra-rb).abs().mean()),
                 "median_abs_rank_shift":float((ra-rb).abs().median())})
r=pd.DataFrame(rows)
print(r.to_string(index=False,float_format=lambda x:f"{x:.6f}"))
r.to_csv(os.path.join(OUT,"independent_model_comparison.csv"),index=False)
