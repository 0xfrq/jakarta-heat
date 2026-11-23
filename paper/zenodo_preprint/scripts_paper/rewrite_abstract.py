from pathlib import Path
p = Path(r"D:\jakarta-heat-paper\paper\zenodo_preprint\input\Manuscript.tex")
s = p.read_text(encoding="utf-8")
start = s.index("\\begin{abstract}")
end = s.index("\\end{abstract}") + len("\\end{abstract}")
new = r"""\begin{abstract}
\noindent\textbf{Abstract.}\quad Urban heat screening indices combine land
surface temperature, vegetation, population and access to cooling space, but
their priority maps depend on choices about what to include and how to weight
it. We examine how spatial priorities change across four screening models in
the five mainland administrative cities of Jakarta, Indonesia, on a 500~m grid.
The common comparison sample contains 2,536 cells with complete inputs. M1
ranks land surface temperature; M2 adds vegetation; M3 adds modelled total
population; and M4 adds a count of children and older adults plus walking
network distance to 1,015 OpenStreetMap candidate parks. Thermal and
demographic inputs refer to a declared 2024 period; the park and network
snapshot is from November 2026. The M1 and M4 top-decile sets share 141 of 254
cells (55.5\% retention), with a Jaccard overlap of 0.384. Between M3 and M4,
an exact three-factor decomposition attributes 85.5\% of absolute rank movement
to park addition, 13.2\% to reweighting and 1.3\% to the age-count
substitution. The age count is nearly collinear with total population
(Spearman \(\rho=0.9995\)): replacing it with total population leaves the top
decile almost unchanged (Jaccard 0.977), whereas an age-share specification
changes it substantially (0.347). Under the additive M4, the top-decile cutoff
(0.8737) exceeds the maximum score of all 537 near-park cells (0.8696), so no
cell within 500~m of a candidate park enters the top 254; this is a property of
the index and observed inputs, not evidence that parks are unimportant.
Accessibility assumptions also matter: a positive-tag-only stress test yields
Jaccard 0.420, while a conservative connector scenario yields 0.896. The 229
excluded cells are cooler, greener and more peripheral than included cells, so
the results describe a conditional sample rather than all of Jakarta. The study
is an exploratory attribution and uncertainty analysis, not a validated health
risk or public-access model.
\end{abstract}"""
s = s[:start] + new + s[end:]
p.write_text(s, encoding="utf-8")
print("rewrote abstract", len(new))
