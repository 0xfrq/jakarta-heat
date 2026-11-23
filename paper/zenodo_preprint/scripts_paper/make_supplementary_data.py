import pandas as pd, numpy as np, os
BASE=r"D:\jakarta-heat-paper"
OUT=r"D:\jakarta-heat-paper\paper\zenodo_preprint\input\Supplementary_Tables"
os.makedirs(OUT,exist_ok=True)
pri=pd.read_csv(os.path.join(BASE,r"data\processed\modeling\priority_models.csv"))
t4=set(pri.loc[pri.valid & pri.m4_top,"grid_id"])
js=pd.read_csv(os.path.join(BASE,r"outputs\remediation\tables\joint_scenario_priority_sets.csv"))
js=js[js.comparison=="eligibility_changing_refit_anchors"]
rows=[]
for (fam,scen),d in js.groupby(["family","scenario"]):
    t=set(d.loc[d.top10.astype(bool),"grid_id"])
    rows.append({"family":fam,"scenario":scen,"n_eligible":int(d.n_eligible.iloc[0]),"n_top":len(t),
                 "shared_with_M4":len(t&t4),"jaccard_with_M4":round(len(t&t4)/len(t|t4),6)})
r=pd.DataFrame(rows).sort_values(["family","scenario"])
r.to_csv(os.path.join(OUT,"full_scenario_results.csv"),index=False)
print(r.shape)
print(r.head(10).to_string(index=False))

# Demographic no-support cells
m=pd.read_csv(os.path.join(BASE,r"data\processed\modeling\merged_grid.csv"))
d=pd.read_csv(os.path.join(BASE,r"data\processed\demographic_features_corrected.csv"))
sup=pd.read_csv(os.path.join(BASE,r"data\processed\demographic_support.csv"))
# find support state columns
print(sup.columns.tolist()[:30])
