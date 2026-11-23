import pandas as pd, os
p=r"D:\jakarta-heat-paper\paper\zenodo_preprint\CLAIM_EVIDENCE_MATRIX.csv"
df=pd.read_csv(p)
mask=df.claim_id=="C33"
df.loc[mask,"claim_text"]="Matched-weight incremental comparisons relative to M3: park addition J=0.490 (167/254), reweighting J=0.961 (249), age swap J=0.984 (252). The corresponding M4-relative values are park 0.861 (235), reweighting 0.423 (151) and age 0.419 (150)."
df.loc[mask,"verification"]="Exact independent recomputation from component_contributions.csv; M3 baseline for these rows; M4-relative values differ (see C39)."
df.loc[mask,"limitations"]="The values are M3-relative, not M4-relative; Table 7 currently mislabels them."
df.loc[mask,"status"]="VERIFIED"
new={
"claim_id":"C39",
"section":"5.4 / Table 7",
"claim_text":"Table 7 caption and footnote state that all Jaccard values are relative to M4 and that retained counts are with the M4 top set.",
"source":"Tables/table6_attribution.tex; matched_weight_comparison.csv; component_contributions.csv; independent_attribution_comparisons.csv",
"data_version":"RC1 3b8ed05; fixed IDs/anchors",
"verification":"Rows 15-20 are M3-relative. Exact M4-relative recomputation: reweighting 0.422969/151; age 0.418994/150; park 0.860806/235; age+reweight 0.422969/151; park+reweight 0.976654/251; age+park 0.847273/233.",
"limitations":"Table/caption is internally inconsistent; split into M3-relative incremental and M4-relative construct tables. Release blocked until corrected.",
"status":"BLOCKED"
}
df=pd.concat([df,pd.DataFrame([new])],ignore_index=True)
df.to_csv(p,index=False,encoding="utf-8")
print(df.shape, df.status.value_counts().to_dict())
print(df[df.claim_id.isin(["C33","C39"])][["claim_id","status","claim_text"]].to_string(index=False))
