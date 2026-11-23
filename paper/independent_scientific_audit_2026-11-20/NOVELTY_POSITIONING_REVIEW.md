# Novelty and Positioning Review

**Manuscript:** From Thermal Hotspots to Spatial Priorities: Attribution and
Sensitivity of Urban Heat Screening in Jakarta
**Date:** 21 November 2026
**Scope:** final literature positioning review. No empirical results or models
were changed.

## 1. Claims already established by prior literature

The following claims are not novel and are now explicitly attributed:

- Urban heat islands have been mapped in Jakarta and its metropolitan area using
  Landsat imagery and remote-sensing change analysis (Ulfiasari & Yola, 2022;
  Putra et al., 2021; Siswanto et al., 2023; Rizki et al., 2024).
- Multi-indicator spatial prioritisation for vegetation-based heat adaptation
  has been developed for Jakarta with regression-informed weights and
  threshold/weight stability tests (Perdinan et al., 2026).
- Children's vulnerability to green-space accessibility has been assessed in
  Jakarta using WorldPop under-five estimates, OSM green spaces and network
  distances (Ramadhanis et al., 2026).
- Composite heat-risk and heat-vulnerability indices have been used to
  prioritise districts and interventions (Elmarakby & Elkadi, 2024; Reid et al.,
  2009; Wolf & McGregor, 2013; Sidiqui et al., 2022).
- Accessibility-based thermal analysis has used floating catchments and spatial
  statistics to compare cooling service with heat exposure (Dong et al., 2024;
  Kim & Kwak, 2026).
- Sensitivity of spatial priorities to aggregation, weighting and thresholds is
  an established research problem (Fitria et al., 2026; Perdinan et al., 2026;
  Saisana et al., 2005; Paruolo et al., 2013; Greco et al., 2019).
- Ranking disagreement can itself be treated as decision-support information
  (Fitria et al., 2026).

## 2. Overlap with recent work

The overlap is substantial and is acknowledged in the Introduction, Related Work
and Discussion:

- **Perdinan et al. (2026):** Jakarta, multi-indicator heat adaptation
  prioritisation, weighted index, weight/threshold sensitivity.
- **Fitria et al. (2026):** explicit comparison of alternative heat-priority
  rankings and a spatial disagreement diagnostic.
- **Ramadhanis et al. (2026):** Jakarta children, green-space network access and
  vulnerability mapping.
- **Dong et al. (2024):** accessibility-based thermal analysis with 2SFCA and
  bivariate local Moran's I.
- **Elmarakby & Elkadi (2024):** composite heat-risk index for intervention
  prioritisation.
- **Ulfiasari & Yola (2022):** Jakarta metropolitan UHI mapping and planning
  context.

These studies mean the paper cannot claim to be the first Jakarta
multi-indicator heat-prioritisation study, the first accessibility-based thermal
study, or the first sensitivity analysis of spatial priorities.

## 3. Contributions that remain supported

The defensible contribution is narrower and tied to the verified outputs:

1. **Sequential construct attribution.** The paper quantifies how the M3→M4
   transition changes the top-decile set and attributes the change to park
   addition, reweighting and age substitution using an exact three-factor
   Shapley decomposition (85.46% / 13.25% / 1.29%).
2. **Demographic redundancy.** It shows empirically that an age count is nearly
   collinear with total population in this dataset; a count-to-count swap leaves
   the top decile almost unchanged, whereas a count-to-share swap changes it
   substantially. This is a finding about the behaviour of the specified
   screening index, not a universal claim about age vulnerability.
3. **Mechanical park-threshold behaviour.** Under the additive M4, the top-decile
   cutoff exceeds the maximum score of all 537 near-park cells, so no cell within
   500 m of a candidate park enters the top 254. This is presented as an
   arithmetic/construct property, not as evidence that parks are unimportant.
4. **Candidate-park and network uncertainty.** The paper propagates alternative
   destination, connector, missing-route and demographic assumptions through the
   ranking and reports the observed sensitivity.
5. **Conditional spatial inference.** The paper reports LISA convention
   sensitivity with a primary two-sided/9,999/BH specification and 493
   significant M4 cells, while retaining alternatives.

The combination of these analyses is a useful complement to Perdinan et al. and
Fitria et al., but it is not a claim of first invention. It is a focused
attribution and uncertainty analysis of a Jakarta screening index.

## 4. Title, abstract and conclusion

- **Title:** unchanged. It describes the content (attribution and sensitivity of
  screening priorities) without claiming firstness or validation.
- **Abstract:** unchanged in its empirical claims; it does not claim to be the
  first integration or the first sensitivity analysis.
- **Conclusion:** already states that the study is not a new integrated framework
  and not a validated vulnerability map. No stronger novelty claim is present.
- **Related Work / Discussion:** revised to acknowledge Perdinan et al., Fitria
  et al., Ramadhanis et al., Dong et al., Elmarakby & Elkadi and Ulfiasari &
  Yola, and to state the narrower contribution explicitly.

No title or abstract change is required for honesty. A modest phrasing
improvement was made in Related Work: the text now says that neither the
combination itself nor sensitivity analysis is new.

## 5. Is additional analysis needed?

No new empirical analysis is needed for this literature revision. The existing
verified outputs already support the narrower contribution. The following would
be new research questions, not requirements for this preprint:

- a formal comparison of accessibility metrics (distance, 2SFCA, G2SFCA);
- a field validation of candidate-park access and entrances;
- an outcome-linked validation of the index against health or observed heat
  exposure;
- a multi-city replication of the attribution decomposition.

These are stated as future work or limitations, not used to manufacture novelty.

## 6. Conclusion

The literature revision strengthens the paper by removing an inflated
combination-only claim and by positioning the work relative to the closest
Jakarta and methodological comparators. The supported contribution remains the
attribution and sensitivity analysis of spatial priorities, including
demographic redundancy, mechanical park-threshold behaviour and candidate-park
uncertainty. **No material novelty conflict requiring a HOLD was found.**
