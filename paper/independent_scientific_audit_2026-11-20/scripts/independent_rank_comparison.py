import pandas as pd, numpy as np, os
BASE=r"D:\jakarta-heat-paper"
OUT=r"D:\jakarta-heat-paper\paper\independent_scientific_audit_2026-11-20\evidence"
m=pd.read_csv(os.path.join(BASE,r"data\processed\modeling\merged_grid.csv"))
p=pd.read_csv(os.path.join(BASE,r"data\processed\modeling\priority_models.csv"))
v=m[m.grid_id.isin(p.loc[p.valid,"grid_id"])].copy().reset_index(drop=True)
q=p.set_index("grid_id").loc[v.grid_id].reset_index()

def n(x, clip=True):
    if clip:
        lo,hi=x.quantile(.05),x.quantile(.95)
    else:
        lo,hi=x.min(),x.max()
    return ((x-lo)/(hi-lo)).clip(0,1) if clip else (x-lo)/(hi-lo)

L=n(v.lst_c); V=1-n(v.ndvi); P=n(np.log1p(v.population)); A=n(np.log1p(v.pop_vulnerable)); D=v.park_distance_m.clip(lower=0,upper=1000)/1000
Lr=n(v.lst_c,False); Vr=1-n(v.ndvi,False); Pr=n(np.log1p(v.population),False); Ar=n(np.log1p(v.pop_vulnerable),False)
scores={"m1":L,"m2":.6*L+.4*V,"m3":.4*L+.3*V+.3*P,"m4":.3*L+.2*V+.25*A+.25*D}
raws={"m1":Lr,"m2":.6*Lr+.4*Vr,"m3":.4*Lr+.3*Vr+.3*Pr,"m4":.3*Lr+.2*Vr+.25*Ar+.25*D}

def rank_exact(score, raw):
    df=pd.DataFrame({"grid_id":v.grid_id,"score":score,"raw":raw})
    df=df.sort_values(["score","raw","grid_id"],ascending=[False,False,True],kind="mergesort").reset_index(drop=True)
    df["rank"]=np.arange(1,len(df)+1)
    return df.set_index("grid_id")["rank"]

ranks={k:rank_exact(scores[k],raws[k]) for k in scores}
for k in ranks:
    saved=q.set_index("grid_id")[k+"_rank"]
    print(k,"rank mismatch",int((ranks[k].reindex(saved.index)!=saved).sum()))

rows=[]
for a,b in [("m1","m2"),("m1","m3"),("m1","m4"),("m2","m3"),("m2","m4"),("m3","m4")]:
    ra,rb=ranks[a],ranks[b]
    ta=set(ra.index[ra<=254]); tb=set(rb.index[rb<=254])
    rows.append({"pair":f"{a.upper()}-{b.upper()}",
                 "jaccard_10":len(ta&tb)/len(ta|tb),"shared_10":len(ta&tb),
                 "mean_abs":float((ra-rb).abs().mean()),
                 "median_abs":float((ra-rb).abs().median()),
                 "p90_abs":float((ra-rb).abs().quantile(.9)),
                 "max_abs":float((ra-rb).abs().max())})
r=pd.DataFrame(rows)
print(r.to_string(index=False,float_format=lambda x:f"{x:.6f}"))
r.to_csv(os.path.join(OUT,"independent_rank_comparison_exact.csv"),index=False)
