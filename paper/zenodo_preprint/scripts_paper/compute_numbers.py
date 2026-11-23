import pandas as pd, numpy as np, json

base = r"D:\jakarta-heat-paper"
p = pd.read_csv(base + r"\data\processed\modeling\priority_models.csv")
m = pd.read_csv(base + r"\data\processed\modeling\merged_grid.csv")
el = pd.read_csv(base + r"\data\processed\modeling\eligibility_by_model.csv")

out = {}
out["master_grids"] = int(len(m))
out["common_valid"] = int(p["valid"].sum())
out["eligible"] = {k:int(el[k].sum()) for k in ["elig_m1","elig_m2","elig_m3","elig_m4"]}
out["top_budget"] = int(p["m4_top"].sum())

v = p[p["valid"]].copy()
# top sets
for k in ["m1","m2","m3","m4"]:
    out[f"{k}_top_n"] = int(v[f"{k}_top"].sum())

top4 = v[v["m4_top"]].copy()
out["m4_top_score_min"] = float(top4["m4_score"].min())
out["m4_top_score_max"] = float(top4["m4_score"].max())
out["m4_top_rank_max"] = int(top4["m4_rank"].max())
out["m4_top_pop_sum"] = float(top4["c_pop"].notna().sum())  # placeholder
# population from merged
mm = m.set_index("grid_id")
top4m = mm.loc[top4["grid_id"]]
out["m4_top_population"] = float(top4m["population"].sum())
out["total_supported_population_common"] = float(mm.loc[v["grid_id"],"population"].sum())
out["m4_top_population_share_common"] = out["m4_top_population"]/out["total_supported_population_common"]
out["m4_top_area_km2"] = float(top4m["area_km2"].sum())
out["m4_top_vuln_share_min"] = float(top4m["vuln_share"].min())
out["m4_top_vuln_share_max"] = float(top4m["vuln_share"].max())

near = mm[(mm["park_distance_m"]<=500) & (mm.index.isin(v["grid_id"]))]
out["near500_n_common"] = int(len(near))
out["near500_in_top4"] = int((near.index.isin(top4["grid_id"])).sum())
out["near500_max_m4_score"] = float(top4["m4_score"].max()) if False else float(v.set_index("grid_id").loc[near.index,"m4_score"].max())
out["top4_min_park_distance"] = float(top4m["park_distance_m"].min())
out["top4_ge1000_n"] = int((top4m["park_distance_m"]>=1000).sum())
out["top4_route_missing"] = int(top4m["park_distance_m"].isna().sum())
out["all_park_distance_missing"] = int(m["park_distance_m"].isna().sum())
out["all_pop_missing"] = int(m["population"].isna().sum())
out["all_age_missing"] = int(m["pop_child"].isna().sum())

# city composition of top sets
for k in ["m1","m2","m3","m4"]:
    ids = v[v[f"{k}_top"]]["grid_id"]
    out[f"{k}_top_by_city"] = mm.loc[ids,"kota"].value_counts().to_dict()

# selection profile aggregates
inc = mm.loc[v["grid_id"]]
exc = mm.loc[~mm.index.isin(v["grid_id"])]
def prof(df):
    return {
        "n": int(len(df)),
        "population": float(df["population"].sum()),
        "lst_mean": float(df["lst_c"].mean()),
        "ndvi_mean": float(df["ndvi"].mean()),
        "coverage_mean": float(df["coverage_ratio"].mean()),
        "snap_mean": float(df["grid_snap_m"].mean()),
    }
out["selection_included"] = prof(inc)
out["selection_excluded"] = prof(exc)
out["selection_excluded_pct_grid"] = len(exc)/len(mm)*100
out["selection_excluded_pct_pop"] = exc["population"].sum()/(mm["population"].sum())*100

# eligibility reason counts
r = el[~el["valid"]]["eligibility_reasons"].fillna("").str.split(";").explode().str.strip()
out["exclusion_reason_counts"] = r[r!=""].value_counts().to_dict()

# m4 top near-park examples
ex = mm.loc["JKT_R056_C048"]
out["example_near_park"] = {k: (float(ex[k]) if isinstance(ex[k], (int,float,np.floating)) else ex[k]) for k in ["lst_c","population","park_distance_m","vuln_share","kota"]}
pm = p.set_index("grid_id").loc["JKT_R056_C048"]
out["example_near_park"]["m4_score"] = float(pm["m4_score"]); out["example_near_park"]["m4_rank"] = int(pm["m4_rank"])
# how many top4 cooler than example
out["top4_cooler_than_example"] = int((top4m["lst_c"] < ex["lst_c"]).sum())

# score correlations from model comparison table
mc = pd.read_csv(base + r"\outputs\tables\model_comparison.csv")
out["model_comparison"] = mc.to_dict(orient="records")

# lisa
lisa = pd.read_csv(base + r"\outputs\remediation\tables\lisa_tail_permutation_sensitivity.csv")
out["lisa_sensitivity"] = lisa.to_dict(orient="records")
lisa_counts = pd.read_csv(base + r"\outputs\tables\lisa_cluster_counts.csv")
out["lisa_counts"] = lisa_counts.to_dict(orient="records")

# shapley
ra = pd.read_csv(base + r"\outputs\remediation\tables\rank_change_attribution.csv")
cols=['shapley_rank_gain_reweighting','shapley_rank_gain_age_swap','shapley_rank_gain_park_addition']
a=ra[cols].abs().sum(); out["shapley_share_pct"] = {c: float(a[c]/a.sum()*100) for c in cols}
out["shapley_abs_mean"] = {c: float(ra[c].abs().mean()) for c in cols}

# robustness at 10%
rb = pd.read_csv(base + r"\outputs\remediation\tables\robustness_family_summary.csv")
rb10 = rb[rb["top_fraction"]==0.1]
out["robustness_10pct"] = rb10.to_dict(orient="records")

with open(base + r"\paper\zenodo_preprint\scripts_paper\manuscript_numbers.json","w",encoding="utf-8") as f:
    json.dump(out,f,indent=2,ensure_ascii=False,default=str)
print(json.dumps({k:out[k] for k in ["master_grids","common_valid","eligible","top_budget","m4_top_score_min","near500_n_common","near500_in_top4","near500_max_m4_score","top4_min_park_distance","top4_ge1000_n","m4_top_population","m4_top_population_share_common","m4_top_vuln_share_min","m4_top_vuln_share_max","selection_excluded_pct_grid","selection_excluded_pct_pop","selection_included","selection_excluded","example_near_park","top4_cooler_than_example","exclusion_reason_counts","shapley_share_pct"]},indent=2,ensure_ascii=False,default=str))

