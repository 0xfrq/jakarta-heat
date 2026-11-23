import pandas as pd, numpy as np, os
BASE=r"D:\jakarta-heat-paper"
OUT=r"D:\jakarta-heat-paper\paper\independent_scientific_audit_2026-11-20\evidence"
pri=pd.read_csv(os.path.join(BASE,r"data\processed\modeling\priority_models.csv"))
t4=set(pri.loc[pri.valid & pri.m4_top,"grid_id"])
js=pd.read_csv(os.path.join(BASE,r"outputs\remediation\tables\joint_scenario_priority_sets.csv"))
js=js[js.comparison=="eligibility_changing_refit_anchors"]
rows=[]
for (fam,scen),d in js.groupby(["family","scenario"]):
    t=set(d.loc[d.top10.astype(bool),"grid_id"])
    rows.append({"family":fam,"scenario":scen,"n_top":len(t),"intersection":len(t&t4),
                 "jaccard":len(t&t4)/len(t|t4) if t|t4 else np.nan})
r=pd.DataFrame(rows)
summary=r.groupby("family").agg(n=("scenario","nunique"),min_j=("jaccard","min"),max_j=("jaccard","max")).reset_index()
print(summary.to_string(index=False))
r.to_csv(os.path.join(OUT,"independent_scenario_jaccard.csv"),index=False)
summary.to_csv(os.path.join(OUT,"independent_scenario_family_summary.csv"),index=False)
