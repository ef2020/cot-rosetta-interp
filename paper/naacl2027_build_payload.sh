# cloud_runner payload: compile the NAACL 2027 short paper (ACL template).
# Expects the folder (main.tex, sections/, acl.sty, acl_natbib.bst,
# custom.bib) at gs://cot-rosetta-interp-data/scratch/naacl_src/

set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq --no-install-recommends \
    texlive-latex-base texlive-latex-recommended texlive-latex-extra \
    texlive-fonts-recommended texlive-fonts-extra texlive-plain-generic \
    cm-super >/dev/null

mkdir -p /tmp/build /tmp/output
gsutil -q -m cp -r "gs://cot-rosetta-interp-data/scratch/naacl_src/*" /tmp/build/
cd /tmp/build

build_failed=0
pdflatex -interaction=nonstopmode -halt-on-error main.tex || build_failed=1
if [ "$build_failed" -eq 0 ]; then
    bibtex main || true
    pdflatex -interaction=nonstopmode -halt-on-error main.tex || build_failed=1
    pdflatex -interaction=nonstopmode -halt-on-error main.tex || build_failed=1
fi

cp -f main.log /tmp/output/ 2>/dev/null || true
cp -f main.blg /tmp/output/ 2>/dev/null || true
[ -f main.pdf ] && cp -f main.pdf /tmp/output/
{
  grep -c "LaTeX Warning: Citation" main.log 2>/dev/null | sed 's/^/undefined_citations=/' || true
  python3 - <<'EOF'
import re
log = open("/tmp/build/main.log", errors="replace").read()
m = re.findall(r"Output written on main\.pdf \((\d+) page", log)
print(f"total_pages={m[-1] if m else 'unknown'}")
EOF
  echo "build_failed=$build_failed"
} > /tmp/output/buildinfo.txt

mark_done
