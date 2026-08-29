# cloud_runner payload: fetch NeurIPS 2026 template + arXiv citation metadata.

set -euo pipefail
mkdir -p /tmp/output

# 1. Official NeurIPS 2026 LaTeX kit (linked from the workshop CFP).
: # template already fetched
:

# 2. arXiv metadata for citations to verify/resolve (Atom XML).
IDS="2406.06196,2503.02972,2406.17038,2509.21820,2508.11260,2504.05081,2309.05660,2509.01016,2301.13379,2305.12295,2307.13702,2305.04388,2507.22928,2503.18878,2504.07128,2501.12948,2305.08809,2303.02536,2407.14561,2407.21783,2501.17148"
curl -sS -m 120 "https://export.arxiv.org/api/query?id_list=${IDS}&max_results=40" -o /tmp/output/arxiv_by_id.xml
sleep 3
# Title searches for entries whose IDs are uncertain.
curl -sS -m 60 "https://export.arxiv.org/api/query?search_query=ti:%22LINGOLY-TOO%22&max_results=3" -o /tmp/output/arxiv_lingolytoo.xml
sleep 3
curl -sS -m 60 "https://export.arxiv.org/api/query?search_query=ti:%22modeLing%22&max_results=5" -o /tmp/output/arxiv_modeling.xml
sleep 3
curl -sS -m 60 "https://export.arxiv.org/api/query?search_query=ti:%22AxBench%22&max_results=3" -o /tmp/output/arxiv_axbench.xml

mark_done
