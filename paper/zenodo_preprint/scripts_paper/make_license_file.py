from pathlib import Path
pkg = Path(r"D:\jakarta-heat-paper\paper\zenodo_preprint\zenodo_release")
legal = (pkg / "_cc_by_4.0_legalcode.txt").read_text(encoding="utf-8")
header = """LICENSE FOR AUTHOR-OWNED MANUSCRIPT MATERIAL
================================================

Copyright (c) 2026 The Authors.
Muhammad Fariq Faqih, Muhammad Alim Mustofa, Mu'adz Abdulloh.
Renaro Lab, Indonesia.

SPDX-License-Identifier: CC-BY-4.0

This work is licensed under a Creative Commons Attribution 4.0
International License (CC BY 4.0).

License URL:
https://creativecommons.org/licenses/by/4.0/

Scope
-----
This license applies to the author-created manuscript text, original figures,
and original supplementary narrative in this preprint package. Third-party
datasets, software dependencies, maps, and the LaTeX template remain subject
to their own licenses and attribution requirements. The template source is
distributed under GPL-3.0-or-later and is not relicensed by this notice.

Attribution should identify the authors, the manuscript title, and the
preprint version where practicable, and should indicate if changes were made.

The full Creative Commons Attribution 4.0 International legal code follows.

=======================================================================

"""
(pkg / "LICENSE_MANUSCRIPT.txt").write_text(header + legal, encoding="utf-8")
(pkg / "_cc_by_4.0_legalcode.txt").unlink()
print("license written")
