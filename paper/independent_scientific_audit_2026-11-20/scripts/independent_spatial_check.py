import os, json, numpy as np, pandas as pd, geopandas as gpd
import libpysal
from libpysal import weights as W
import esda

BASE = r"D:\jakarta-heat-paper"
OUT = r"D:\jakarta-heat-paper\paper\independent_scientific_audit_2026-11-20\evidence"

grid = gpd.read_file(os.path.join(BASE, r"data\processed\grid_500m_jakarta.gpkg"))
pri = pd.read_csv(os.path.join(BASE, r"data\processed\modeling\priority_models.csv"))
lisa_saved = pd.read_csv(os.path.join(BASE, r"data\processed\modeling\lisa_m4.csv"))

v = pri.loc[pri.valid].copy()
g = grid.merge(v[["grid_id","m1_score","m2_score","m3_score","m4_score"]], on="grid_id", how="inner")
g = g.reset_index(drop=True)
print("joined", len(g))

w = W.Queen.from_dataframe(g, use_index=False, silence_warnings=True)
print("islands", list(w.islands), "n", w.n)
island_ids = [g.loc[i,"grid_id"] for i in w.islands]
if w.islands:
    keep = [i for i in range(len(g)) if i not in set(w.islands)]
    g2 = g.iloc[keep].reset_index(drop=True)
    # rebuild with integer ids 0..n-1
    w = W.Queen.from_dataframe(g2, use_index=False, silence_warnings=True)
else:
    g2 = g
w.transform = "r"
print("after", w.n, "islands", list(w.islands), "edges", int(sum(w.cardinalities.values())),
      "mean_neighbors", float(sum(w.cardinalities.values())/w.n))

res = {"joined": int(len(g)), "island_ids": island_ids, "n_after": int(w.n),
       "directed_edges": int(sum(w.cardinalities.values())),
       "mean_neighbors": float(sum(w.cardinalities.values())/w.n)}

def bh(p, q=0.05):
    p = np.asarray(p, float); ok = np.isfinite(p); rej = np.zeros(len(p), bool)
    pv = p[ok]; m = len(pv)
    if m == 0: return rej
    order = np.argsort(pv, kind="stable")
    passed = pv[order] <= q * (np.arange(1, m+1)/m)
    if passed.any():
        k = np.max(np.nonzero(passed)[0]); sel = np.zeros(m, bool); sel[order[:k+1]] = True
        rej[np.nonzero(ok)[0]] = sel
    return rej

def by(p, q=0.05):
    # Benjamini-Yekutieli step-up: p_(i) <= (i/m) * q / H_m.
    # Equivalent to BH at q/H_m, where H_m = sum_{j=1}^m 1/j.
    p = np.asarray(p, float)
    m = int(np.isfinite(p).sum())
    if m == 0:
        return np.zeros(len(p), bool)
    h = float(np.sum(1.0 / np.arange(1, m + 1)))
    return bh(p, q / h)

# Moran and LISA for each model
for model in ["m1","m2","m3","m4"]:
    y = g2[f"{model}_score"].to_numpy()
    mi = esda.Moran(y, w, permutations=999, two_tailed=False)
    ml = esda.Moran_Local(y, w, permutations=999, seed=42, alternative="directed")
    p = ml.p_sim
    sig_bh = bh(p); sig_by = by(p)
    # labels: quadrant 1 HH, 2 LH, 3 LL, 4 HL
    quad = {1:"HH",2:"LH",3:"LL",4:"HL"}
    labels_bh = [quad.get(int(q), "ns") if s else "ns" for q,s in zip(ml.q, sig_bh)]
    labels_by = [quad.get(int(q), "ns") if s else "ns" for q,s in zip(ml.q, sig_by)]
    counts_bh = {k: labels_bh.count(k) for k in ["HH","LL","HL","LH","ns"]}
    counts_by = {k: labels_by.count(k) for k in ["HH","LL","HL","LH","ns"]}
    res[model] = {"moran_I": float(mi.I), "moran_p_sim": float(mi.p_sim),
                  "moran_EI": float(mi.EI), "lisa_n": int(len(p)),
                  "bh_significant": int(sig_bh.sum()), "bh_counts": counts_bh,
                  "by_significant": int(sig_by.sum()), "by_counts": counts_by,
                  "min_p": float(np.nanmin(p))}
    print(model, res[model])

# Compare saved M4 labels and p-values
s = lisa_saved.copy()
s = s.set_index("grid_id").loc[g2["grid_id"]]
res["saved_m4_compare"] = {
    "n": int(len(s)),
    "p_mismatch": int((np.abs(s["p_sim"].to_numpy() - res["m4"]["lisa_n"]*0) > 0).sum()),  # placeholder
}
# exact p comparison using recomputed m4 p
ml4 = esda.Moran_Local(g2["m4_score"].to_numpy(), w, permutations=999, seed=42, alternative="directed")
p_re = ml4.p_sim
res["saved_m4_compare"] = {
    "n": int(len(s)),
    "p_max_abs_diff": float(np.max(np.abs(s["p_sim"].to_numpy() - p_re))),
    "label_fdr_mismatch": int((s["klaster_fdr"].astype(str).to_numpy() != np.array([{1:"HH",2:"LH",3:"LL",4:"HL"}.get(int(q),"ns") if sig else "ns" for q,sig in zip(ml4.q, bh(p_re))])).sum()),
}
print("saved compare", res["saved_m4_compare"])

with open(os.path.join(OUT, "independent_spatial_check.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, indent=2, ensure_ascii=False)
print("wrote", os.path.join(OUT, "independent_spatial_check.json"))
