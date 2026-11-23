import pandas as pd, os
BASE=r"D:\jakarta-heat-paper\paper\zenodo_preprint\input"
df=pd.read_csv(os.path.join(BASE,"Supplementary_Tables","full_scenario_results.csv"))
labels={
"uniform_fractional_agent2_values":"Uniform fractional allocation",
"akses taman biner >1000 m":"Binary park threshold >1,000 m",
"akses taman biner >500 m":"Binary park threshold >500 m",
"defisit taman jenuh 1500 m":"Park-deficit cap 1,500 m",
"defisit taman jenuh 750 m":"Park-deficit cap 750 m",
"bobot lst x0.8":"LST weight x0.8",
"bobot lst x1.2":"LST weight x1.2",
"bobot ndvi_low x0.8":"NDVI-deficit weight x0.8",
"bobot ndvi_low x1.2":"NDVI-deficit weight x1.2",
"bobot park_deficit x0.8":"Park-deficit weight x0.8",
"bobot park_deficit x1.2":"Park-deficit weight x1.2",
"bobot sama rata":"Equal weights",
"bobot vuln x0.8":"Vulnerable-count weight x0.8",
"bobot vuln x1.2":"Vulnerable-count weight x1.2",
"keluarkan coverage < 10%":"Exclude coverage <10%",
"keluarkan rs_qa_ok = False (Agent 1)":"Exclude remote-sensing QA failures",
"keluarkan snap > 250 m":"Exclude snap >250 m",
"jarak kosong = defisit maksimum":"Missing distance = maximum deficit",
"jarak kosong = median teramati":"Missing distance = observed median",
"joint_pop_cap1500_clipped_fractional":"Total population, cap 1,500 m, clipped, fractional",
"joint_pop_cap1500_clipped_legacy":"Total population, cap 1,500 m, clipped, hybrid",
"joint_pop_cap1500_rank_fractional":"Total population, cap 1,500 m, rank, fractional",
"joint_pop_cap1500_rank_legacy":"Total population, cap 1,500 m, rank, hybrid",
"joint_pop_cap750_clipped_fractional":"Total population, cap 750 m, clipped, fractional",
"joint_pop_cap750_clipped_legacy":"Total population, cap 750 m, clipped, hybrid",
"joint_pop_cap750_rank_fractional":"Total population, cap 750 m, rank, fractional",
"joint_pop_cap750_rank_legacy":"Total population, cap 750 m, rank, hybrid",
"joint_vuln_cap1500_clipped_fractional":"Vulnerable count, cap 1,500 m, clipped, fractional",
"joint_vuln_cap1500_clipped_legacy":"Vulnerable count, cap 1,500 m, clipped, hybrid",
"joint_vuln_cap1500_rank_fractional":"Vulnerable count, cap 1,500 m, rank, fractional",
"joint_vuln_cap1500_rank_legacy":"Vulnerable count, cap 1,500 m, rank, hybrid",
"joint_vuln_cap750_clipped_fractional":"Vulnerable count, cap 750 m, clipped, fractional",
"joint_vuln_cap750_clipped_legacy":"Vulnerable count, cap 750 m, clipped, hybrid",
"joint_vuln_cap750_rank_fractional":"Vulnerable count, cap 750 m, rank, fractional",
"joint_vuln_cap750_rank_legacy":"Vulnerable count, cap 750 m, rank, hybrid",
"corrected_support":"Corrected demographic support",
"normalisasi min-max murni":"Pure min-max normalisation",
"normalisasi peringkat persentil":"Percentile-rank normalisation",
"normalisasi persentil 1-99":"1st-99th percentile normalisation",
"porsi rentan (bukan jumlah)":"Vulnerable share (not count)",
"total populasi (bukan rentan)":"Total population (not vulnerable count)",
"agent2_audited_baseline":"Route policy: baseline",
"agent2_explicit_nodes_and_connectors_conservative":"Route policy: conservative nodes + connectors",
"agent2_explicit_nodes_conservative":"Route policy: conservative nodes",
"agent2_full_jakarta_extent":"Route policy: full extent",
"agent2_positive_tags_destination_coverage_stress":"Route policy: positive tags",
"thermal_support_0.25":"Thermal support 25%",
"thermal_support_0.5":"Thermal support 50%",
"Dynamic World pohon rendah (ganti NDVI)":"Tree-probability land cover (NDVI replacement)",
}
df["display_label"]=df.scenario.map(labels)
assert df.display_label.notna().all(), df[df.display_label.isna()].scenario.tolist()
family={"aggregation":"Aggregation","ambang taman":"Park threshold","bobot":"Weights",
 "eksklusi QA":"QA exclusion","jarak taman kosong":"Missing park distance",
 "joint_factorial":"Joint factorial","missing_support":"Missing support",
 "normalisasi":"Normalisation","penduduk":"Population definition",
 "route_policy":"Route policy","thermal_support":"Thermal support","tutupan lahan":"Land cover"}
def esc(s):
    return str(s).replace("\\","\\textbackslash{}").replace("_","\\_").replace("&","\\&").replace("%","\\%").replace(">","$>$").replace("<","$<$")
lines=[r"\begin{longtable}{@{}p{0.22\textwidth} p{0.52\textwidth} r r@{}}",
r"\caption{Executed scenario top-decile results at the 10\% budget. Jaccard and shared cells are relative to the M4 top-254 set.}\label{tab:s7}\\",
r"\toprule",r"Family & Scenario & Jaccard & Shared/254 \\",r"\midrule",r"\endfirsthead",
r"\toprule",r"Family & Scenario & Jaccard & Shared/254 \\",r"\midrule",r"\endhead",r"\bottomrule",r"\endfoot"]
for _,r in df.sort_values(["family","display_label"]).iterrows():
    lines.append(f"{esc(family.get(r.family,r.family))} & {esc(r.display_label)} & {r.jaccard_with_M4:.3f} & {int(r.shared_with_M4)} \\\\")
lines.append(r"\end{longtable}")
open(os.path.join(BASE,"Tables","tableS7_scenarios.tex"),"w",encoding="utf-8").write("\n".join(lines))
print("regenerated",len(df))
