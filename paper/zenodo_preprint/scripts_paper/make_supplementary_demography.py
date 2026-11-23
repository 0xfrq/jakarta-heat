import pandas as pd, os
BASE=r"D:\jakarta-heat-paper"
OUT=r"D:\jakarta-heat-paper\paper\zenodo_preprint\input\Supplementary_Tables"
os.makedirs(OUT,exist_ok=True)
m=pd.read_csv(os.path.join(BASE,r"data\processed\modeling\merged_grid.csv")).set_index("grid_id")
s=pd.read_csv(os.path.join(BASE,r"data\processed\demographic_support.csv"))
# no-source-support rows
no=s[(s.population_support_state=="no_source_support") | (s.pop_child_support_state=="no_source_support") | (s.pop_elderly_support_state=="no_source_support")]
rows=[]
for _,r in no.iterrows():
    gid=r.grid_id
    rows.append({"grid_id":gid,"kota":m.loc[gid,"kota"],"area_km2":round(float(m.loc[gid,"area_km2"]),6),
                 "coverage_ratio":round(float(m.loc[gid,"coverage_ratio"]),6),
                 "population_support_state":r.population_support_state,
                 "pop_child_support_state":r.pop_child_support_state,
                 "pop_elderly_support_state":r.pop_elderly_support_state,
                 "population_analytical":m.loc[gid,"population"] if pd.notna(m.loc[gid,"population"]) else "",
                 "raw_population":m.loc[gid,"raw_population"],
                 "raw_pop_child":m.loc[gid,"raw_pop_child"],
                 "raw_pop_elderly":m.loc[gid,"raw_pop_elderly"]})
pd.DataFrame(rows).to_csv(os.path.join(OUT,"demographic_no_support.csv"),index=False)
print(pd.DataFrame(rows).to_string(index=False))

elig=[
 ("Master grid cells",2765,"Five mainland cities; 500 m lattice"),
 ("Route-only missing",222,"No path to a candidate park in baseline graph"),
 ("Route + population + age missing",4,"Already outside common set because of route"),
 ("Population/age missing only",2,"JKT_R003_C031; JKT_R057_C063"),
 ("Low LST support",1,"JKT_R037_C062; 27.759% valid LST area"),
 ("Excluded union",229,"8.28% of master grid"),
 ("Legacy common set",2538,"2,765 - 222 - 4 - 1"),
 ("RC1 common set",2536,"2,538 - 2 population-only slivers"),
 ("Spatial observations after island",2535,"JKT_R013_C019 is a Queen island")]
pd.DataFrame(elig,columns=["category","n","note"]).to_csv(os.path.join(OUT,"eligibility_reconciliation.csv"),index=False)
print("wrote",OUT)
