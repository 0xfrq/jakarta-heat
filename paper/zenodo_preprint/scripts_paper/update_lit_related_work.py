from pathlib import Path
p = Path(r"D:\jakarta-heat-paper\paper\zenodo_preprint\input\Manuscript.tex")
s = p.read_text(encoding="utf-8")

# 1. Composite-index subsection: add recent composite/risk examples.
old = """A composite can change rankings even
when the underlying data are unchanged. This is not a defect unique to heat
indices; it is a general property of multidimensional indicators."""
new = """A composite can change rankings even
when the underlying data are unchanged. This is not a defect unique to heat
indices; it is a general property of multidimensional indicators. Elmarakby and
Elkadi \\citep{elmarakby2024} illustrate the planning use of this logic in a
district Heat Risk Index that combines UHI intensity, green cover and population
density, while Perdinan et al.\\ \\citep{perdinan2026} build a regression-informed
vegetation-adaptation priority index for Jakarta. Such indices make priorities
legible, but the index itself does not show how much a ranking change follows
from adding a construct rather than from reweighting."""
if old not in s:
    raise SystemExit("composite block not found")
s = s.replace(old, new, 1)

# 2. Age/access subsection: add Ramadhanis and Dong before the OSM caveat.
old = """Access to a cooling refuge is also an equity question in its own right
\\citep{voelkel2018,amorim2023}. The broader point is that a
park-distance term is a model of access, not a measurement of public access."""
new = """Access to a cooling refuge is also an equity question in its own right
\\citep{voelkel2018,amorim2023}. Ramadhanis et al.\\ \\citep{ramadhanis2026}
combine under-five population density with OSM green-space network distance in
Jakarta, and Dong et al.\\ \\citep{dong2024} use an improved two-step floating
catchment area and bivariate local Moran's \\textit{I} to compare cooling
accessibility with heat-risk exposure in Zhengzhou. These studies make
accessibility the estimand. Our park term is a simpler candidate-park distance
inside a composite screening index, and our contribution concerns the
sensitivity of the resulting ranking rather than a new accessibility metric. The
broader point is that a park-distance term is a model of access, not a
measurement of public access."""
if old not in s:
    raise SystemExit("age/access block not found")
s = s.replace(old, new, 1)

# 3. Sensitivity subsection: acknowledge direct ranking-disagreement work.
old = """A cluster map is therefore not a
self-interpreting result. Our design treats model comparison, attribution,
scenario analysis and LISA sensitivity as parts of one evidentiary system rather
than as separate appendices."""
new = """A cluster map is therefore not a
self-interpreting result. Fitria et al.\\ \\citep{fitria2026} make this explicit
by comparing equal-weight and PCA heat-vulnerability indices across 158
Taiwanese districts and mapping where their priority rankings disagree; Perdinan
et al.\\ \\citep{perdinan2026} test weight and threshold stability in Jakarta.
Our design complements that work by attributing a sequential M3-to-M4 change to
park addition, reweighting and age substitution, and by propagating
candidate-park and network uncertainty through the ranking rather than treating
the destination layer as fixed."""
if old not in s:
    raise SystemExit("sensitivity block not found")
s = s.replace(old, new, 1)

# 4. Jakarta-specific subsection: add recent studies and sharpen the gap.
old = """Jakarta has a substantial applied literature on LST, vegetation and heat. Putra
et al.\\ \\citep{putra2021} document increasing urban heat island area in relation
to land-use change; Siswanto et al.\\ \\citep{siswanto2023} characterise the
spatio-temporal urban heat island of the Jakarta metropolitan area; and Rizki et
al.\\ \\citep{rizki2024} examine the impact of urban green space on the heat island
in East Jakarta. Salsabila et al.\\ \\citep{salsabila2023} show through ethnographic
and practice-based work that cooling in Jakarta's informal settlements is
entangled with social life and communal space. Manik and Syaukat
\\citep{manik2017} compare heat vulnerability in two tropical Indonesian cities.
These studies establish the local relevance of heat and vegetation, but they do
not provide a cell-level attribution of how demographic and network-access
assumptions reshape a priority ranking. That is the space this paper occupies."""
new = """Jakarta has a substantial applied literature on LST, vegetation and heat. Putra
et al.\\ \\citep{putra2021} document increasing urban heat island area in relation
to land-use change; Siswanto et al.\\ \\citep{siswanto2023} characterise the
spatio-temporal urban heat island of the Jakarta metropolitan area; and Rizki et
al.\\ \\citep{rizki2024} examine the impact of urban green space on the heat island
in East Jakarta. Ulfiasari and Yola \\citep{ulfiasari2022} use Landsat 5 and 8
imagery to trace a decade of UHI expansion across the Jakarta metropolitan area;
Perdinan et al.\\ \\citep{perdinan2026} develop regression-informed
vegetation-adaptation priorities for Jakarta; and Ramadhanis et al.\\
\\citep{ramadhanis2026} assess child-specific green-space accessibility with
WorldPop and OSM network data. Salsabila et al.\\ \\citep{salsabila2023} show
through ethnographic and practice-based work that cooling in Jakarta's informal
settlements is entangled with social life and communal space, and Manik and
Syaukat \\citep{manik2017} compare heat vulnerability in two tropical Indonesian
cities. These studies establish local relevance, multi-indicator prioritisation
and green-space accessibility as active research questions. They leave less
examined how a sequential change from heat-only to heat--population--age--park
screening reshapes cell-level priorities, and how modelled candidate-park
destinations and routing change that ranking."""
if old not in s:
    raise SystemExit("Jakarta block not found")
s = s.replace(old, new, 1)

# 5. Positioning and contribution: explicitly acknowledge the closest work.
old = """Table~\\ref{tab:literature} summarises the closest bodies of work. The table is
not a systematic review and does not establish that no similar study exists. It
shows that every individual ingredient of our analysis has precedent: LST--NDVI
mapping, heat vulnerability indices, age-sensitive risk, network-based park
access and composite-indicator sensitivity. The combination-only claim is
therefore not defensible. What remains is a narrower and more useful claim: a
quantitative attribution and uncertainty audit of how priorities shift when
these ingredients are assembled in one Jakarta screening index, including
negative findings about redundancy and mechanical threshold behaviour. We
present that contribution as conditional on the analytical specification and
the sensitivity analyses reported below."""
new = """Table~\\ref{tab:literature} summarises the closest bodies of work. It is not a
systematic review and does not establish that no similar study exists. Every
individual ingredient of our analysis has precedent: LST--NDVI mapping, heat
vulnerability indices, age-sensitive risk, network-based park access and
composite-indicator sensitivity. Recent Jakarta work already combines thermal
condition, vegetation deficit, built-up intensity and population exposure in an
adaptation-prioritisation framework and tests weight and threshold stability
\\citep{perdinan2026}; recent Taiwanese work treats disagreement between
priority rankings as a decision-support diagnostic \\citep{fitria2026}. The
combination-only claim, and the claim that sensitivity analysis is new, are
therefore not defensible. What remains is narrower: a cell-level attribution of
a sequential screening transition, a test of age-count redundancy, and an
uncertainty analysis of modelled candidate-park accessibility in Jakarta. We
present that contribution as conditional on the analytical specification and
the sensitivity analyses reported below."""
if old not in s:
    raise SystemExit("positioning block not found")
s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
print("related work updated")
