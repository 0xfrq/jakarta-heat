#!/usr/bin/env bash
set -euo pipefail
export PATH="/c/Users/VICTUS/AppData/Local/Temp/opencode/TinyTeX/TinyTeX/bin/windows:$PATH"
export BASH="$(command -v bash)"
cd /d/jakarta-heat-paper/paper/zenodo_preprint
./build.sh --target neutral --input-dir input --main Manuscript.tex
./build.sh --target neutral --input-dir input --main Manuscript-internal.tex
./build.sh --target neutral --input-dir input --main Supplementary.tex
cp output/pdf/Manuscript-neutral.pdf output/pdf/Manuscript-submission-candidate.pdf
cp output/pdf/Manuscript-internal-neutral.pdf output/pdf/Manuscript-internal-review.pdf
cp output/pdf/Supplementary-neutral.pdf output/pdf/Supplementary-submission-candidate.pdf
printf 'candidate PDFs written\n'
