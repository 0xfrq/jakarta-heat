from pathlib import Path
p = Path(r"D:\jakarta-heat-paper\paper\zenodo_preprint\input\Manuscript.tex")
s = p.read_text(encoding="utf-8")
old = """\\item \\textbf{Raw-data portability.} The raw WorldPop, OpenStreetMap and
GraphML bundle is distributed separately and is not tracked in the manuscript
repository; exact raw-input hashes require that bundle. The processed tables and
code reproduce the reported results. A clean-checkout test suite and
relative-path output manifests are documented in the reproducibility note.
These engineering checks do not make the raw bundle public and do not establish
acquisition-level satellite provenance."""
new = """\\item \\textbf{Raw-data portability.} The raw WorldPop, OpenStreetMap and GraphML
inputs are not redistributed in this preprint package and are not tracked in the
manuscript repository; exact raw-input hashes require the separate research
bundle. The processed tables and code reproduce the reported results. A
clean-checkout test suite and relative-path output manifests are documented in
the reproducibility note. These engineering checks do not make the raw bundle
public and do not establish acquisition-level satellite provenance."""
if old not in s:
    raise SystemExit("old block not found")
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("fixed raw-data limitation")
