#!/usr/bin/env bash
set -euo pipefail
export PATH="/c/Users/VICTUS/AppData/Local/Temp/opencode/TinyTeX/TinyTeX/bin/windows:$PATH"
export BASH="$(command -v bash)"
cd /d/jakarta-heat-paper/paper/zenodo_preprint
./build.sh --target zenodo  --input-dir input --main Manuscript.tex
./build.sh --target neutral --input-dir input --main Manuscript.tex
./build.sh --target zenodo  --input-dir input --main Supplementary.tex
