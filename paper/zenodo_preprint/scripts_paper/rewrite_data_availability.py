from pathlib import Path
p = Path(r"D:\jakarta-heat-paper\paper\zenodo_preprint\input\Manuscript.tex")
s = p.read_text(encoding="utf-8")
start = s.index("\\section*{Data and Code Availability}")
end = s.index("\\section*{Acknowledgements}")
new = r"""\section*{Data and Code Availability}

Processed grid tables, model outputs, figure-generation scripts and the LaTeX
source are held in the project repository under
\texttt{paper/zenodo\_preprint}. The repository is not yet publicly archived and
no dataset DOI has been assigned. The raw WorldPop, OpenStreetMap and GraphML
bundle is distributed separately and is not tracked in the manuscript
repository. WorldPop data are subject to CC BY 4.0 \citep{worldpop2025};
OpenStreetMap data are subject to the Open Database License and attribution
requirements \citep{osm2026}. Original Landsat acquisition records were not
available for independent verification, but the raster-to-grid aggregation can
be reproduced from the retained exports.

A technical reproducibility note in the repository records the analysis
environment (Python 3.12.10; pandas 3.1.1; numpy 2.5.5; geopandas 1.2.0;
libpysal 4.15.1; esda 2.10.0), software revisions, input and output hashes,
clean-checkout test results, manifest paths and the two-build table replay.
These records concern computational reproducibility and do not establish
acquisition-level satellite provenance.

"""
s = s[:start] + new + s[end:]
p.write_text(s, encoding="utf-8")
print("rewrote data availability")
