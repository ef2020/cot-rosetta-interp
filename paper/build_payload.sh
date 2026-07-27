# cloud_runner payload: compile the workshop paper with TeX Live.
# Expects main.tex + references.bib at gs://<bucket>/scratch/paper_src/
# (upload them before launching; see paper/README.md).

set -euo pipefail

export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq --no-install-recommends \
    texlive-latex-base texlive-latex-recommended texlive-latex-extra \
    texlive-fonts-recommended texlive-plain-generic >/dev/null

mkdir -p /tmp/build /tmp/output
gsutil -q cp "gs://cot-rosetta-interp-data/scratch/paper_src/*" /tmp/build/
cd /tmp/build

# Run the full pdflatex/bibtex cycle; capture logs even on failure.
build_failed=0
pdflatex -interaction=nonstopmode -halt-on-error main.tex || build_failed=1
if [ "$build_failed" -eq 0 ]; then
    bibtex main || true
    pdflatex -interaction=nonstopmode -halt-on-error main.tex || build_failed=1
    pdflatex -interaction=nonstopmode -halt-on-error main.tex || build_failed=1
fi

cp -f main.log /tmp/output/ 2>/dev/null || true
cp -f main.blg /tmp/output/ 2>/dev/null || true
if [ -f main.pdf ]; then
    cp -f main.pdf /tmp/output/
    # Page count, so the 5-page main-text budget can be checked from the log.
    python3 - <<'EOF' > /tmp/output/pagecount.txt
import re
log = open("/tmp/build/main.log", errors="replace").read()
m = re.findall(r"Output written on main\.pdf \((\d+) page", log)
print(f"total_pages={m[-1] if m else 'unknown'}")
EOF
fi
echo "build_failed=$build_failed" >> /tmp/output/pagecount.txt || true

mark_done
