import os, json, numpy as np, pandas as pd, geopandas as gpd
from libpysal import weights as W
import esda

BASE = r"D:\jakarta-heat-paper"
OUT = r"D:\jakarta-heat-paper\paper\independent_scientific_audit_2026-11-20\evidence"
grid = gpd.read_file(os.path.join(BASE, r"data\processed\grid_500m_jakarta.gpkg"))
pri = pd.read_csv(os.path.join(BASE, r"data\processed\modeling\priority_models.csv"))
v = pri.loc[pri.valid]
g = grid.merge(v[["grid_id","m4_score"]], on="grid_id", how="inner").reset_index(drop=True)

def bh(p, q=0.05):
    p = np.asarray(p, float); ok = np.isfinite(p); rej = np.zeros(len(p), bool)
    pv = p[ok]; m = len(pv)
    order = np.argsort(pv, kind="stable")
    passed = pv[order] <= q * (np.arange(1, m+1)/m)
    if passed.any():
        k = np.max(np.nonzero(passed)[0]); sel = np.zeros(m, bool); sel[order[:k+1]] = True
        rej[np.nonzero(ok)[0]] = sel
    return rej

def by(p, q=0.05):
    p = np.asarray(p, float); m = int(np.isfinite(p).sum())
    h = float(np.sum(1.0/np.arange(1, m+1)))
    return bh(p, q/h)

w = W.Queen.from_dataframe(g, use_index=False, silence_warnings=True)
keep = [i for i in range(len(g)) if i not in set(w.islands)]
g2 = g.iloc[keep].reset_index(drop=True)
w = W.Queen.from_dataframe(g2, use_index=False, silence_warnings=True)
w.transform = "r"
y = g2["m4_score"].to_numpy()

out = {"n": int(len(g2)), "islands_removed": int(len(g)-len(g2))}
for alt in ["directed","two-sided"]:
    ml = esda.Moran_Local(y, w, permutations=9999, seed=42, alternative=alt)
    p = ml.p_sim
    for name, rej in [("bh", bh(p)), ("by", by(p))]:
        labels = [ {1:"HH",2:"LH",3:"LL",4:"HL"}.get(int(q),"ns") if s else "ns" for q,s in zip(ml.q, rej) ]
        out[f"{alt}_{name}"] = {"n_significant": int(sum(rej)), "counts": {k: labels.count(k) for k in ["HH","LL","HL","LH","ns"]}, "min_p": float(np.min(p))}
    print(alt, out[f"{alt}_bh"], out[f"{alt}_by"])

with open(os.path.join(OUT, "independent_spatial_9999.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2)
print("wrote", os.path.join(OUT, "independent_spatial_9999.json"))
