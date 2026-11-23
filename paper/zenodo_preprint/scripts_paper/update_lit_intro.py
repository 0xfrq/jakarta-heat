from pathlib import Path
p = Path(r"D:\jakarta-heat-paper\paper\zenodo_preprint\input\Manuscript.tex")
s = p.read_text(encoding="utf-8")
old = """A growing literature combines heat, demographic vulnerability and green-space
access. Sidiqui et al.\\ \\citep{sidiqui2022} map urban heat vulnerability with
GIS data and socio-demographic indicators; Kim and Kwak \\citep{kim2026} develop a
cooling-weighted park-accessibility framework for older adults using an
OpenStreetMap walking network; Fung et al.\\ \\citep{fung2024} prioritise social
vulnerability in urban heat mitigation; and Sobhaninia et al.\\
\\citep{sobhaninia2025} review methods for siting green infrastructure. The idea
of combining LST, age and access is therefore not new. What remains
underdeveloped is a quantitative account of how much each added construct
changes a priority ranking, how much of the change is attributable to
accessibility rather than reweighting, and how sensitive the result is to
imperfect destination and network data. Those questions are methodological and
empirical at once, and they are the focus of this study."""
new = """A growing literature combines heat, demographic vulnerability and green-space
access. Jakarta studies have moved from mapping the urban heat island
\\citep{ulfiasari2022} to regression-informed vegetation adaptation priorities
\\citep{perdinan2026} and child-specific green-space vulnerability
\\citep{ramadhanis2026}. Elsewhere, accessibility-based thermal assessments
combine cooling supply, heat exposure and network catchments
\\citep{dong2024,kim2026}, while composite heat-risk indices aggregate UHI
intensity, green cover and population density into planning tiers
\\citep{elmarakby2024}. A parallel literature asks whether priority rankings
survive alternative aggregation choices, including weight and threshold
scenarios in Jakarta \\citep{perdinan2026} and equal-weight versus
principal-component indices in Taiwan \\citep{fitria2026}. These studies
establish the relevance of the components and the value of sensitivity testing.
They leave less examined the attribution of a sequential model transition: how
much of a ranking change follows from adding a construct rather than from
reweighting, and how candidate-park and pedestrian-network uncertainty
propagates into the resulting priorities in Jakarta. Those questions are
methodological and empirical at once, and they are the focus of this study."""
if old not in s:
    raise SystemExit("intro block not found")
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("intro updated")
