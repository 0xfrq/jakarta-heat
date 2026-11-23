import pandas as pd, numpy as np, os, json
BASE=r"D:\jakarta-heat-paper"
OUT=r"D:\jakarta-heat-paper\paper\independent_scientific_audit_2026-11-20\evidence"
m=pd.read_csv(os.path.join(BASE,r"data\processed\modeling\merged_grid.csv"))
p=pd.read_csv(os.path.join(BASE,r"data\processed\modeling\priority_models.csv"))
v=m[m.grid_id.isin(p.loc[p.valid,"grid_id"])].copy()
q=p.set_index("grid_id").loc[v.grid_id]
def n(x):
    lo,hi=x.quantile(.05),x.quantile(.95); return ((x-lo)/(hi-lo)).clip(0,1)
L=n(v.lst_c); V=1-n(v.ndvi); P=n(np.log1p(v.population)); A=n(np.log1p(v.pop_vulnerable)); D=v.park_distance_m.clip(lower=0,upper=1000)/1000
s={"m1":L,"m2":.6*L+.4*V,"m3":.4*L+.3*V+.3*P,"m4":.3*L+.2*V+.25*A+.25*D}
rows=[]
for k,x in s.items():
    rows.append({"model":k.upper(),"n":len(x),"max_abs_score_diff":float(np.max(np.abs(x.values-q[k+"_score"].values))),
                 "top_budget":254,"top_set_symmetric_difference":int(len(set(v.loc[x.rank(ascending=False,method='first')<=254,'grid_id'])^set(v.loc[q[k+'_top'].values,'grid_id'])))})
r=pd.DataFrame(rows); print(r.to_string(index=False)); r.to_csv(os.path.join(OUT,"independent_score_check.csv"),index=False)
