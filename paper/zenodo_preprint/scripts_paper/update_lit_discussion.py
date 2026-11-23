from pathlib import Path
p = Path(r"D:\jakarta-heat-paper\paper\zenodo_preprint\input\Manuscript.tex")
s = p.read_text(encoding="utf-8")
old = """Our results overlap with prior work in several ways. The LST--NDVI relationship
and the surface urban heat island literature justify the M1/M2 layers
\\citep{oke1982,voogt2003,weng2004,estoque2017}. Heat vulnerability indices
justify the demographic layers \\citep{reid2009,wolf2013}. Network-access studies
justify the park layer \\citep{oh2007,kim2026,feng2019}. Composite-indicator
research justifies the sensitivity design \\citep{saisana2005,paruolo2013,greco2019}.
Jakarta studies establish the local relevance \\citep{siswanto2023,putra2021,rizki2024,varquez2020}.
The contribution is not the combination of these ingredients. It is the
quantitative attribution of how the combination changes priorities, the
demonstration that an age count is nearly redundant with population, and the
disclosure that an additive park term can mechanically determine the top decile.

Compared with Sidiqui et al.\\ \\citep{sidiqui2022}, we use a finer grid, a
network-based candidate-park measure and an explicit attribution decomposition,
but we do not claim a better vulnerability map. Compared with Kim and Kwak
\\citep{kim2026}, we do not implement a cooling-weighted G2SFCA or a
demand-allocation model; our park term is a simpler distance deficit, and our
contribution is the sensitivity of the resulting ranking rather than the
sophistication of the access measure. Compared with Fung et al.\\
\\citep{fung2024}, we do not evaluate heat-mitigation interventions; we evaluate
how a screening index responds to specification choices. These differences are
substantive, and they define a narrower but defensible contribution."""
new = """Our results overlap with prior work in several ways. The LST--NDVI relationship
and the surface urban heat island literature justify the M1/M2 layers
\\citep{oke1982,voogt2003,weng2004,estoque2017}. Heat vulnerability indices
justify the demographic layers \\citep{reid2009,wolf2013}. Network-access studies
justify the park layer \\citep{oh2007,kim2026,feng2019}. Composite-indicator
research justifies the sensitivity design \\citep{saisana2005,paruolo2013,greco2019}.
Jakarta studies establish the local relevance
\\citep{siswanto2023,putra2021,rizki2024,varquez2020}. The contribution is not
the combination of these ingredients. It is the quantitative attribution of how
the combination changes priorities, the demonstration that an age count is
nearly redundant with population, and the disclosure that an additive park term
can mechanically determine the top decile.

The closest Jakarta comparator is Perdinan et al.\\ \\citep{perdinan2026}. They
integrate 30~m LST, vegetation deficit, built-up intensity and population
density through an ordinary least-squares model, construct a weighted priority
index, and evaluate four weighting scenarios and threshold relaxation. Their
priority tiers remain structurally consistent, and high-LST clusters persist in
dense built-up corridors. Their question is which vegetation-based adaptation
tiers are robust to specification, whereas ours is how a sequence of screening
constructs changes cell-level rankings and which component drives that change.
The two findings are compatible: administrative priority tiers can remain
similar while top-decile membership shifts substantially at the cell level. We
do not present M4 as a better adaptation index than their regression-informed
framework; we examine what the construction of a screening index does to its
spatial priorities.

A second comparator treats disagreement itself as decision support. Fitria et
al.\\ \\citep{fitria2026} compare equal-weight and principal-component
heat-vulnerability indices across 158 Taiwanese districts using 17 indicators,
introduce a Spatial Disagreement Index, and find only moderate rank agreement
(Spearman $\\rho=0.52$) with disagreement concentrated in urban--rural fringe
districts. Their leave-one-out analysis further shows that the two aggregation
methods retain different shares of top-priority districts. This is a direct
precedent for interpreting ranking differences as information rather than as
noise. Our exact Shapley decomposition is complementary: it attributes a
sequential M3-to-M4 transition rather than a contrast between two aggregation
methods. We do not claim to be the first study to decompose or diagnose
disagreement among heat-priority rankings.

Ramadhanis et al.\\ \\citep{ramadhanis2026} and Dong et al.\\ \\citep{dong2024}
place demographic and accessibility evidence in a broader context. Ramadhanis
et al.\\ combine under-five population density with OSM green-space network
distance in Jakarta and identify child-specific vulnerability concentrations,
particularly in North, West and East Jakarta. Dong et al.\\ use an improved
two-step floating catchment area and bivariate local Moran's \\textit{I} to
compare cooling accessibility and heat-risk exposure in Zhengzhou. Both studies
make accessibility or age-specific vulnerability the estimand. In our analysis,
age and park distance are components of a screening index; the objects of
inquiry are the redundancy of an age count with total population and the
sensitivity of the ranking to modelled candidate-park destinations and routing.
Our results therefore describe the behaviour of a screening construct, not
verified public access or individual heat-health vulnerability.

Elmarakby and Elkadi \\citep{elmarakby2024} show how a district Heat Risk Index
can prioritise UHI mitigation, and Ulfiasari and Yola \\citep{ulfiasari2022}
document a decade of UHI expansion in metropolitan Jakarta. These studies
establish the planning relevance of composite risk mapping and the local
physical signal. They do not ask how a sequential change in a screening index
redistributes cell-level priorities. Compared with Sidiqui et al.\\
\\citep{sidiqui2022}, we use a finer grid, a network-based candidate-park
measure and an explicit attribution decomposition, but we do not claim a better
vulnerability map. Compared with Kim and Kwak \\citep{kim2026}, we do not
implement a cooling-weighted G2SFCA or a demand-allocation model; our park term
is a simpler distance deficit. Compared with Fung et al.\\ \\citep{fung2024}, we
do not evaluate heat-mitigation interventions; we evaluate how a screening index
responds to specification choices. These differences define a narrower but
defensible contribution."""
if old not in s:
    raise SystemExit("discussion block not found")
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("discussion updated")
