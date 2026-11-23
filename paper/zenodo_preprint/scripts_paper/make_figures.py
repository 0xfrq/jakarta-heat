import os, json
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib import cm

BASE = r"D:\jakarta-heat-paper"
OUT = os.path.join(BASE, r"paper\zenodo_preprint\input\Figures")
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 8,
    "axes.titlesize": 9,
    "axes.labelsize": 8,
    "legend.fontsize": 7,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "figure.dpi": 150,
    "savefig.dpi": 400,
    "axes.linewidth": 0.6,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

# ---------- data ----------
grid = gpd.read_file(os.path.join(BASE, r"data\processed\grid_500m_jakarta.gpkg"))
cities = gpd.read_file(os.path.join(BASE, r"data\processed\jakarta_5kota.gpkg"))
pri = pd.read_csv(os.path.join(BASE, r"data\processed\modeling\priority_models.csv"))
mg = pd.read_csv(os.path.join(BASE, r"data\processed\modeling\merged_grid.csv"))
lisa = pd.read_csv(os.path.join(BASE, r"data\processed\modeling\lisa_m4.csv"))
parks = gpd.read_file(os.path.join(BASE, r"data\processed\parks_jakarta.gpkg"))

g = grid.merge(pri[["grid_id","valid","m1_score","m1_rank","m1_top","m2_score","m2_rank","m2_top","m3_score","m3_rank","m3_top","m4_score","m4_rank","m4_top"]], on="grid_id", how="left")
g = g.merge(mg[["grid_id","lst_c","ndvi","population","pop_vulnerable","vuln_share","park_distance_m","grid_snap_m","coverage_ratio","area_km2"]], on="grid_id", how="left")
g["excluded"] = ~g["valid"].fillna(False).astype(bool)
g["park_cap"] = g["park_distance_m"].clip(upper=1000)

# city label points (representative point, manual offsets)
city_labels = {
    "Kota Jakarta Barat": ("West Jakarta", (0, 0)),
    "Kota Jakarta Pusat": ("Central Jakarta", (0, 0)),
    "Kota Jakarta Selatan": ("South Jakarta", (0, 0)),
    "Kota Jakarta Timur": ("East Jakarta", (0, 0)),
    "Kota Jakarta Utara": ("North Jakarta", (0, 0)),
}

def base_map(ax, show_grid=True, show_excluded=True):
    cities.plot(ax=ax, facecolor="#f2f2f2", edgecolor="#4d4d4d", linewidth=0.8, zorder=1)
    if show_grid:
        g.plot(ax=ax, facecolor="#ffffff", edgecolor="#d9d9d9", linewidth=0.05, zorder=2)
    if show_excluded:
        g[g["excluded"]].plot(ax=ax, facecolor="#8c8c8c", edgecolor="#555555", linewidth=0.08, zorder=3)
    cities.boundary.plot(ax=ax, color="#333333", linewidth=0.8, zorder=5)
    ax.set_axis_off()
    ax.set_aspect("equal")

def add_scalebar(ax, length_km=5, x=0.05, y=0.04):
    xmin, xmax = ax.get_xlim(); ymin, ymax = ax.get_ylim()
    L = length_km * 1000
    x0 = xmin + (xmax - xmin) * x
    y0 = ymin + (ymax - ymin) * y
    ax.plot([x0, x0 + L], [y0, y0], color="black", lw=2.2, solid_capstyle="butt", zorder=10)
    ax.plot([x0, x0], [y0 - 300, y0 + 300], color="black", lw=1.0, zorder=10)
    ax.plot([x0 + L, x0 + L], [y0 - 300, y0 + 300], color="black", lw=1.0, zorder=10)
    ax.text(x0 + L/2, y0 + 450, f"{length_km} km", ha="center", va="bottom", fontsize=7, zorder=10)

def add_north(ax, x=0.94, y=0.93):
    xmin, xmax = ax.get_xlim(); ymin, ymax = ax.get_ylim()
    xa = xmin + (xmax - xmin) * x
    ya = ymin + (ymax - ymin) * y
    ax.annotate("", xy=(xa, ya + (ymax-ymin)*0.06), xytext=(xa, ya),
                arrowprops=dict(arrowstyle="-|>", color="black", lw=1.1), zorder=10)
    ax.text(xa, ya + (ymax-ymin)*0.065, "N", ha="center", va="bottom", fontsize=8, fontweight="bold", zorder=10)

# ---------- Figure 1: study area ----------
fig, ax = plt.subplots(figsize=(6.6, 4.7))
base_map(ax)
for _, row in cities.iterrows():
    p = row.geometry.representative_point()
    name = city_labels.get(row["kota"], (row["kota"], (0,0)))[0]
    ax.annotate(name, xy=(p.x, p.y), xytext=(0,0), textcoords="offset points",
                ha="center", va="center", fontsize=7.5, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.22", fc="white", ec="none", alpha=0.82), zorder=11)
add_scalebar(ax); add_north(ax)
handles = [Patch(facecolor="#ffffff", edgecolor="#bdbdbd", label="500 m grid (n = 2,765)"),
           Patch(facecolor="#8c8c8c", edgecolor="#555555", label="Excluded from common comparison (n = 229)")]
ax.legend(handles=handles, loc="lower right", frameon=True, framealpha=0.9, borderpad=0.5)
ax.set_title("Five mainland Jakarta cities and the 500 m analysis grid", loc="left", fontweight="bold")
fig.tight_layout()
for ext in ("pdf","png"):
    fig.savefig(os.path.join(OUT, f"fig01_study_area.{ext}"), bbox_inches="tight")
plt.close(fig)

# ---------- Figure 2: LST and NDVI ----------
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.6))
for ax, col, cmap, label, vmin, vmax in [
    (axes[0], "lst_c", "inferno", "Land surface temperature (°C)", 37.1, 44.5),
    (axes[1], "ndvi", "YlGn", "NDVI (unitless)", 0.17, 0.50)]:
    base_map(ax, show_grid=False)
    g[g["valid"]].plot(ax=ax, column=col, cmap=cmap, vmin=vmin, vmax=vmax,
                       edgecolor="none", linewidth=0, zorder=4, rasterized=True)
    g[g["excluded"]].plot(ax=ax, facecolor="#bdbdbd", edgecolor="none", zorder=3)
    cities.boundary.plot(ax=ax, color="#333333", linewidth=0.7, zorder=5)
    sm = cm.ScalarMappable(norm=plt.Normalize(vmin=vmin, vmax=vmax), cmap=cmap)
    cb = fig.colorbar(sm, ax=ax, fraction=0.035, pad=0.015)
    cb.set_label(label)
    ax.set_title("(a) LST, common sample" if col=="lst_c" else "(b) NDVI, common sample", loc="left")
add_scalebar(axes[0], 5, 0.03, 0.03)
fig.suptitle("Environmental inputs (n = 2,536 common grids; grey = excluded)", x=0.02, ha="left", fontsize=9, fontweight="bold")
fig.tight_layout(rect=[0,0,1,0.94])
for ext in ("pdf","png"):
    fig.savefig(os.path.join(OUT, f"fig02_environment.{ext}"), bbox_inches="tight")
plt.close(fig)

# ---------- Figure 3: population and park access ----------
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.6))
ax = axes[0]
base_map(ax, show_grid=False)
g[g["valid"]].assign(logpop=np.log10(g.loc[g["valid"],"population"].clip(lower=0.1))).plot(
    ax=ax, column="logpop", cmap="viridis", vmin=2, vmax=4.05, edgecolor="none", linewidth=0, zorder=4, rasterized=True)
g[g["excluded"]].plot(ax=ax, facecolor="#bdbdbd", edgecolor="none", zorder=3)
cities.boundary.plot(ax=ax, color="#333333", linewidth=0.7, zorder=5)
sm = cm.ScalarMappable(norm=plt.Normalize(2,4.05), cmap="viridis")
cb = fig.colorbar(sm, ax=ax, fraction=0.035, pad=0.015); cb.set_label("log10 population per grid")
ax.set_title("(a) Modelled population, 2024", loc="left")

ax = axes[1]
base_map(ax, show_grid=False)
g[g["valid"]].plot(ax=ax, column="park_cap", cmap="RdYlBu", vmin=0, vmax=1000,
                   edgecolor="none", linewidth=0, zorder=4, rasterized=True)
g[g["excluded"]].plot(ax=ax, facecolor="#bdbdbd", edgecolor="none", zorder=3)
cities.boundary.plot(ax=ax, color="#333333", linewidth=0.7, zorder=5)
sm = cm.ScalarMappable(norm=plt.Normalize(0,1000), cmap="RdYlBu")
cb = fig.colorbar(sm, ax=ax, fraction=0.035, pad=0.015); cb.set_label("Network distance (m), capped at 1,000")
ax.set_title("(b) Candidate-park distance, OSM 2026", loc="left")
add_scalebar(axes[0], 5, 0.03, 0.03)
fig.suptitle("Exposure and accessibility inputs (common sample; grey = excluded)", x=0.02, ha="left", fontsize=9, fontweight="bold")
fig.tight_layout(rect=[0,0,1,0.94])
for ext in ("pdf","png"):
    fig.savefig(os.path.join(OUT, f"fig03_population_access.{ext}"), bbox_inches="tight")
plt.close(fig)

# ---------- Figure 4: priority maps ----------
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.6))
for ax, topcol, title in [(axes[0], "m1_top", "(a) M1: LST only"),
                          (axes[1], "m4_top", "(b) M4: heat, vegetation, age count, park deficit")]:
    base_map(ax, show_grid=False)
    g[g["valid"] & ~g[topcol]].plot(ax=ax, facecolor="#e6e6e6", edgecolor="white", linewidth=0.05, zorder=3, rasterized=True)
    g[g["valid"] & g[topcol]].plot(ax=ax, facecolor="#c0392b", edgecolor="#7b241c", linewidth=0.1, zorder=4, rasterized=True)
    g[g["excluded"]].plot(ax=ax, facecolor="#7f8c8d", edgecolor="none", zorder=2, rasterized=True)
    cities.boundary.plot(ax=ax, color="#333333", linewidth=0.7, zorder=5)
    ax.set_title(title, loc="left")
add_scalebar(axes[0], 5, 0.03, 0.03)
handles = [Patch(facecolor="#c0392b", edgecolor="#7b241c", label="Top decile (n = 254)"),
           Patch(facecolor="#e6e6e6", edgecolor="white", label="Eligible, not top decile"),
           Patch(facecolor="#7f8c8d", edgecolor="none", label="Excluded (n = 229)")]
axes[1].legend(handles=handles, loc="lower right", frameon=True, framealpha=0.9, borderpad=0.5, fontsize=6.5)
fig.suptitle("Top-decile priority sets under M1 and M4", x=0.02, ha="left", fontsize=9, fontweight="bold")
fig.tight_layout(rect=[0,0,1,0.94])
for ext in ("pdf","png"):
    fig.savefig(os.path.join(OUT, f"fig04_priority_maps.{ext}"), bbox_inches="tight")
plt.close(fig)

# ---------- Figure 5: rank displacement ----------
v = g[g["valid"]].copy()
fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.3), gridspec_kw={"width_ratios":[1.15,1]})
ax=axes[0]
ax.scatter(v["m1_rank"], v["m4_rank"], s=3, alpha=0.20, color="#2c3e50", linewidths=0, rasterized=True)
ax.plot([1,2536],[1,2536], color="#c0392b", lw=1, ls="--", label="1:1")
ax.axhline(254, color="#7f8c8d", lw=0.8, ls=":"); ax.axvline(254, color="#7f8c8d", lw=0.8, ls=":")
ax.set_xlim(0,2536); ax.set_ylim(2536,0)
ax.set_xlabel("M1 rank (1 = highest priority)"); ax.set_ylabel("M4 rank")
ax.set_title("(a) Rank displacement, M1 to M4", loc="left")
ax.text(0.04,0.06,"Spearman ρ = 0.847\nJaccard (top 10%) = 0.384", transform=ax.transAxes, fontsize=7,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#cccccc"))
ax.legend(loc="upper right", frameon=False, fontsize=7)

ax=axes[1]
delta = (v["m4_rank"] - v["m1_rank"])
ax.hist(delta, bins=60, color="#5d6d7e", edgecolor="white", linewidth=0.3)
ax.axvline(0, color="#c0392b", lw=1, ls="--")
ax.axvline(delta.median(), color="#e67e22", lw=1, ls="-", label=f"median = {delta.median():.0f}")
ax.set_xlabel("M4 rank − M1 rank"); ax.set_ylabel("Grid cells")
ax.set_title("(b) Distribution of rank change", loc="left")
ax.legend(frameon=False, fontsize=7)
fig.tight_layout()
for ext in ("pdf","png"):
    fig.savefig(os.path.join(OUT, f"fig05_rank_shift.{ext}"), bbox_inches="tight")
plt.close(fig)

# ---------- Figure 6: attribution and sensitivity ----------
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.4), gridspec_kw={"width_ratios":[0.9,1.35]})
ax=axes[0]
labels=["Park\naddition","Reweighting","Age\nsubstitution"]
vals=[85.46,13.25,1.29]
bars=ax.barh(labels[::-1], vals[::-1], color=["#c0392b","#e67e22","#7f8c8d"][::-1], height=0.55)
for b,val in zip(bars, vals[::-1]):
    ax.text(val+1.5, b.get_y()+b.get_height()/2, f"{val:.2f}%", va="center", fontsize=8)
ax.set_xlim(0,100); ax.set_xlabel("Share of absolute Shapley rank movement (%)")
ax.set_title("(a) M3-to-M4 attribution", loc="left")
ax.spines[["top","right"]].set_visible(False)

ax=axes[1]
rb = pd.read_csv(os.path.join(BASE, r"outputs\remediation\tables\robustness_family_summary.csv"))
rb = rb[(rb["top_fraction"]==0.1) & (rb["comparison"]=="eligibility_changing_refit_anchors")]
name_map = {
 "aggregation":"Aggregation","ambang taman":"Park threshold","bobot":"Weights",
 "eksklusi QA":"QA exclusions","jarak taman kosong":"Missing park distance",
 "joint_factorial":"Joint factorial (16)","missing_support":"Missing support",
 "normalisasi":"Normalisation","penduduk":"Population definition",
 "route_policy":"Route policy","thermal_support":"Thermal support","tutupan lahan":"Land cover"}
rb["label"]=rb["family"].map(name_map).fillna(rb["family"])
rb=rb.sort_values("min_jaccard")
y=np.arange(len(rb))
colors=["#c0392b" if f in ("route_policy","penduduk","joint_factorial") else "#5d6d7e" for f in rb["family"]]
ax.hlines(y, rb["min_jaccard"], rb["max_jaccard"], color=colors, lw=2.2, alpha=0.85)
ax.scatter(rb["min_jaccard"], y, color=colors, s=16, zorder=3)
ax.scatter(rb["max_jaccard"], y, color=colors, s=16, zorder=3, marker="|", linewidths=1.4)
ax.axvline(1.0, color="#7f8c8d", lw=0.8, ls=":")
ax.set_yticks(y); ax.set_yticklabels(rb["label"], fontsize=6.5)
ax.set_xlim(0.25,1.02); ax.set_xlabel("Jaccard overlap of top-decile set vs. M4")
ax.set_title("(b) Scenario-family sensitivity (min–max)", loc="left")
ax.spines[["top","right"]].set_visible(False)
fig.tight_layout()
for ext in ("pdf","png"):
    fig.savefig(os.path.join(OUT, f"fig06_attribution_sensitivity.{ext}"), bbox_inches="tight")
plt.close(fig)

# ---------- Figure 7: LISA ----------
lisa_grid = pd.read_csv(os.path.join(BASE, r"outputs\remediation\tables\lisa_tail_permutation_grid.csv"))
li = lisa_grid[(lisa_grid.alternative == "two-sided") & (lisa_grid.permutations == 9999)].copy()
li["lab"] = li["klaster_fdr"].fillna("ns")
gli = g.merge(li[["grid_id","lab","lisa_I","p_sim"]], on="grid_id", how="left")
fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.7), gridspec_kw={"width_ratios":[1.25,1]})
ax=axes[0]
base_map(ax, show_grid=False)
colors={"HH":"#c0392b","LL":"#2e86c1","HL":"#f39c12","LH":"#85c1e9","ns":"#e5e5e5"}
for lab in ["ns","LL","LH","HL","HH"]:
    sub=gli[gli["lab"]==lab]
    if len(sub):
        sub.plot(ax=ax, facecolor=colors[lab], edgecolor="none", zorder=4, rasterized=True)
# The single Queen island has no local statistic; show it separately from
# the cells excluded from the common comparison.
untested = gli[gli["lab"].isna()]
if len(untested):
    untested.plot(ax=ax, facecolor="#bdbdbd", edgecolor="none", zorder=3, rasterized=True)
g[g["excluded"]].plot(ax=ax, facecolor="#7f8c8d", edgecolor="none", zorder=2, rasterized=True)
cities.boundary.plot(ax=ax, color="#333333", linewidth=0.7, zorder=5)
ax.set_title("(a) M4 LISA clusters (two-sided, 9,999 permutations, BH)", loc="left")
handles=[Patch(facecolor=colors[k], label=v) for k,v in
         [("HH","High–high"),("LL","Low–low"),("HL","High–low"),("LH","Low–high"),("ns","Not significant")]]
handles.append(Patch(facecolor="#7f8c8d", label="Excluded"))
if len(untested):
    handles.append(Patch(facecolor="#bdbdbd", label="Not tested (island)"))
ax.legend(handles=handles, loc="lower right", frameon=True, framealpha=0.9, fontsize=6.2, ncol=2)

ax=axes[1]
ls = pd.read_csv(os.path.join(BASE, r"outputs\remediation\tables\lisa_tail_permutation_sensitivity.csv"))
ls = ls[ls["correction"].isin(["klaster_fdr","klaster_by"])].copy()
ls["primary"] = (ls.alternative=="two-sided") & (ls.permutations==9999) & (ls.correction=="klaster_fdr")
ls["short"] = ls["alternative"].str.replace("two-sided","Two-sided").str.replace("directed","Directed") + "\n" + ls["permutations"].astype(str) + " / " + ls["correction"].str.replace("klaster_","").str.upper()
ls.loc[ls["primary"], "short"] = ls.loc[ls["primary"], "short"] + "\n(primary)"
ls = ls.sort_values(["primary","alternative","permutations","correction"], ascending=[False,True,True,True])
y=np.arange(len(ls))
cols=["#c0392b" if r.primary else "#5d6d7e" for r in ls.itertuples()]
ax.barh(y, ls["n_significant"], color=cols, height=0.62)
for yy,val in zip(y,ls["n_significant"]):
    ax.text(val+8, yy, str(int(val)), va="center", fontsize=6.5)
ax.set_yticks(y); ax.set_yticklabels(ls["short"], fontsize=5.8)
ax.set_xlabel("Significant local clusters (n)"); ax.set_xlim(0,760)
ax.set_title("(b) LISA count by convention", loc="left")
ax.spines[["top","right"]].set_visible(False)
fig.tight_layout()
for ext in ("pdf","png"):
    fig.savefig(os.path.join(OUT, f"fig07_lisa.{ext}"), bbox_inches="tight")
plt.close(fig)

# ---------- Supplementary S1: score distributions ----------
fig, ax = plt.subplots(figsize=(6.0, 3.2))
data=[v["m1_score"],v["m2_score"],v["m3_score"],v["m4_score"]]
parts=ax.violinplot(data, showmeans=False, showmedians=True, widths=0.75)
for pc in parts["bodies"]:
    pc.set_facecolor("#5d6d7e"); pc.set_alpha(0.55)
ax.set_xticks([1,2,3,4]); ax.set_xticklabels(["M1","M2","M3","M4"])
ax.set_ylabel("Priority score (0–1)"); ax.set_title("Score distributions across the common sample (n = 2,536)", loc="left")
ax.spines[["top","right"]].set_visible(False)
fig.tight_layout()
for ext in ("pdf","png"):
    fig.savefig(os.path.join(OUT, f"figS1_score_distributions.{ext}"), bbox_inches="tight")
plt.close(fig)

# ---------- Supplementary S2: exclusion map ----------
fig, ax = plt.subplots(figsize=(6.4, 4.5))
base_map(ax, show_grid=True, show_excluded=False)
reason_colors={"missing_walking_route":"#c0392b","missing_total_population":"#f39c12",
               "missing_age_support_or_value":"#8e44ad","low_lst_support_QA":"#2c3e50"}
# assign primary reason
def primary_reason(s):
    if pd.isna(s): return None
    parts=[p.strip() for p in str(s).split(";") if p.strip()]
    for key in ["low_lst_support_QA","missing_total_population","missing_age_support_or_value","missing_walking_route"]:
        if key in parts: return key
    return parts[0] if parts else None
g["reason"]=g["eligibility_reasons"].apply(primary_reason) if "eligibility_reasons" in g.columns else None
# merge reasons from eligibility file
el=pd.read_csv(os.path.join(BASE, r"data\processed\modeling\eligibility_by_model.csv"))
g=g.drop(columns=["reason"]).merge(el[["grid_id","eligibility_reasons"]], on="grid_id", how="left")
g["reason"]=g["eligibility_reasons"].apply(primary_reason)
for k,c in reason_colors.items():
    sub=g[g["reason"]==k]
    if len(sub): sub.plot(ax=ax, facecolor=c, edgecolor="none", zorder=4, rasterized=True)
cities.boundary.plot(ax=ax, color="#333333", linewidth=0.7, zorder=5)
handles=[Patch(facecolor=c, label=k.replace("_"," ")) for k,c in reason_colors.items()]
ax.legend(handles=handles, loc="lower right", frameon=True, fontsize=6.3)
add_scalebar(ax); add_north(ax)
ax.set_title("Where the 229 excluded grids are, by primary reason", loc="left", fontweight="bold")
fig.tight_layout()
for ext in ("pdf","png"):
    fig.savefig(os.path.join(OUT, f"figS2_exclusions.{ext}"), bbox_inches="tight")
plt.close(fig)

# ---------- Supplementary S3: candidate park inventory and missing routes ----------
pe = pd.read_csv(os.path.join(BASE, r"data\processed\park_access_evidence.csv"))
parks2 = parks.merge(pe[["park_id","access_evidence_state"]], on="park_id", how="left")
parks2 = parks2.set_geometry(parks2.geometry.representative_point())
fig, ax = plt.subplots(figsize=(6.4, 4.6))
base_map(ax, show_grid=True, show_excluded=False)
# route-missing cells in grey
miss = g[g["eligibility_reasons"].fillna("").str.contains("missing_walking_route", regex=False)] if "eligibility_reasons" in g.columns else g.iloc[0:0]
if len(miss):
    miss.plot(ax=ax, facecolor="#bdbdbd", edgecolor="none", zorder=3, rasterized=True)
cols = {"unknown":"#5d6d7e", "conditional_unverified":"#e67e22", "positive_osm_tag_unverified":"#27ae60"}
for state, c in cols.items():
    sub = parks2[parks2["access_evidence_state"] == state]
    if len(sub):
        sub.plot(ax=ax, color=c, markersize=3.2, alpha=0.75, zorder=6)
cities.boundary.plot(ax=ax, color="#333333", linewidth=0.7, zorder=5)
handles = [Line2D([0],[0], marker="o", color="none", markerfacecolor=c, markeredgecolor="none",
                  markersize=4, label=k.replace("_"," ")) for k,c in cols.items()]
handles.append(Patch(facecolor="#bdbdbd", label="Route-missing grid"))
ax.legend(handles=handles, loc="lower right", frameon=True, fontsize=6.3)
add_scalebar(ax); add_north(ax)
ax.set_title("Candidate parks by evidence state and route-missing grids", loc="left", fontweight="bold")
fig.tight_layout()
for ext in ("pdf","png"):
    fig.savefig(os.path.join(OUT, f"figS3_park_inventory.{ext}"), bbox_inches="tight")
plt.close(fig)

print("figures written to", OUT)
