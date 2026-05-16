"""Scrape every UKLO past-paper / past-problem PDF into GCS.

Why this is a VM job, not a local script:

    `www.uklo.org` and `archives.uklo.org` sit behind a SiteGround CAPTCHA
    that returns HTTP 202 + a JS challenge to residential / Anthropic-sandbox
    IPs but answers normally to Google Cloud IPs. We therefore launch a
    short-lived Compute Engine VM in `us-central1-a`, hand it a startup
    script that fetches the two index pages, derives a deduped PDF URL list,
    downloads each PDF in parallel, and rsyncs the lot to
    `gs://<bucket>/raw/uklo_pdf/`. The VM is created with
    `--instance-termination-action=DELETE` and `--max-run-duration=20m` so it
    cleans up unattended; the startup script also issues `shutdown -h +1`.

Outputs in GCS:

    gs://<bucket>/raw/uklo_pdf/<flattened-url>.pdf  - one file per PDF
    gs://<bucket>/scratch/uklo_pdf_urls.txt         - deduped URL manifest
    gs://<bucket>/scratch/download_logs/            - fetch log + DONE marker

Run from the repo root:

    uv run python scripts/scrape_uklo_pdfs.py --bucket cot-rosetta-interp-data

The script blocks until the VM writes a DONE marker to GCS, then prints a
summary (total PDFs, HTTP code distribution, content-type distribution) and
optionally cleans up failures (HTML files erroneously saved as .pdf when the
upstream URL 404s).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

INDEX_URLS = [
    ("past_papers", "https://www.uklo.org/past-exam-papers/"),
    ("archives_past", "https://archives.uklo.org/past-problems"),
]

STARTUP_SCRIPT = r"""#!/bin/bash
set -x
exec > /tmp/scrape.log 2>&1

BUCKET="__BUCKET__"
SCRATCH="gs://${BUCKET}/scratch"
RAW="gs://${BUCKET}/raw/uklo_pdf/"
LOGS="${SCRATCH}/download_logs/"

UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
WORK=/tmp/uklo
mkdir -p "$WORK/files" && cd "$WORK"

# 1. Fetch index pages
__FETCH_INDEX__

# 2. Extract every .pdf href, dedupe, materialize manifest
python3 - <<'PY'
import re, pathlib
urls = set()
for p in pathlib.Path('.').glob('index_*.html'):
    text = p.read_text(errors='replace')
    for m in re.finditer(r'href="([^"]*\.pdf[^"]*)"', text):
        u = m.group(1).strip()
        if u.startswith('//'): u = 'https:' + u
        if u.startswith('/'):  u = 'https://www.uklo.org' + u
        if u.startswith('http'): urls.add(u)
pathlib.Path('manifest.txt').write_text("\n".join(sorted(urls)) + "\n")
print(f"manifest: {len(urls)} unique URLs")
PY
gsutil cp manifest.txt "${SCRATCH}/uklo_pdf_urls.txt"

# 3. Build flattened-filename plan and parallel-download
> upload_plan.tsv
while IFS= read -r url; do
  [ -z "$url" ] && continue
  flat=$(printf "%s" "${url#https://}" | tr '/' '_' | sed 's/__\+/__/g')
  printf "%s\t%s\n" "$url" "$flat" >> upload_plan.tsv
done < manifest.txt

> fetch_log.txt
fetch_one() {
  local url="$1" out="$2"
  curl -sL -A "$UA" --retry 4 --retry-delay 2 --retry-all-errors --max-time 90 \
    -w "FETCH\t%{http_code}\t%{size_download}\t%{content_type}\t$url\n" \
    -o "files/$out" "$url" >> fetch_log.txt 2>&1 \
    || printf "FAIL\t%s\n" "$url" >> fetch_log.txt
}
export -f fetch_one
export UA

awk -F'\t' '{print $1 "\t" $2}' upload_plan.tsv \
  | xargs -n1 -P8 -I{} bash -c 'p="{}"; u=$(echo "$p" | cut -f1); o=$(echo "$p" | cut -f2); fetch_one "$u" "$o"'

# 4. Bulk upload
gsutil -m rsync -r files/ "$RAW"

# 5. Logs + completion marker
gsutil cp fetch_log.txt    "${LOGS}fetch_log.txt"
gsutil cp upload_plan.tsv  "${LOGS}upload_plan.tsv"
gsutil cp /tmp/scrape.log  "${LOGS}scrape.log"
echo "DONE $(date -u +%FT%TZ) $(ls files/ | wc -l) files" > /tmp/done.txt
gsutil cp /tmp/done.txt "${LOGS}DONE.txt"

shutdown -h +1
"""


def render_startup_script(bucket: str) -> str:
    fetch_lines = "\n".join(
        f'curl -sL -A "$UA" -o "index_{label}.html" "{url}"'
        for label, url in INDEX_URLS
    )
    return STARTUP_SCRIPT.replace("__BUCKET__", bucket).replace("__FETCH_INDEX__", fetch_lines)


def gcloud(*args: str, check: bool = True, capture: bool = False) -> str:
    cmd = ["gcloud", *args]
    print(f"$ {' '.join(cmd)}", flush=True)
    res = subprocess.run(cmd, check=check, capture_output=capture, text=True)
    return (res.stdout or "") if capture else ""


def gsutil_exists(uri: str) -> bool:
    try:
        subprocess.run(
            ["gcloud", "storage", "ls", uri],
            check=True, capture_output=True, text=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def cat_gcs(uri: str) -> str:
    return subprocess.check_output(["gcloud", "storage", "cat", uri], text=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bucket", required=True)
    ap.add_argument("--zone", default="us-central1-a")
    ap.add_argument("--instance", default="uklo-scrape-1")
    ap.add_argument("--machine-type", default="e2-small")
    ap.add_argument("--max-wait-min", type=int, default=20)
    ap.add_argument(
        "--service-account",
        default="claude-agent@cot-rosetta-interp.iam.gserviceaccount.com",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Render the startup script and print it; do not provision a VM.",
    )
    args = ap.parse_args(argv)

    script = render_startup_script(args.bucket)
    script_path = Path("/tmp") / f"scrape_uklo_{args.instance}.sh"
    script_path.write_text(script)
    print(f"Wrote startup script to {script_path}")

    if args.dry_run:
        print(script)
        return 0

    gcloud(
        "compute", "instances", "create", args.instance,
        f"--zone={args.zone}",
        f"--machine-type={args.machine_type}",
        "--image-family=debian-12",
        "--image-project=debian-cloud",
        f"--service-account={args.service_account}",
        "--scopes=https://www.googleapis.com/auth/cloud-platform",
        f"--metadata-from-file=startup-script={script_path}",
        "--no-shielded-secure-boot",
        "--instance-termination-action=DELETE",
        f"--max-run-duration={args.max_wait_min}m",
    )

    done_uri = f"gs://{args.bucket}/scratch/download_logs/DONE.txt"
    deadline = time.time() + args.max_wait_min * 60
    print(f"Waiting up to {args.max_wait_min}m for {done_uri} ...", flush=True)
    while time.time() < deadline:
        if gsutil_exists(done_uri):
            print("DONE marker found:", cat_gcs(done_uri).strip())
            break
        time.sleep(15)
    else:
        print("Timed out waiting for DONE marker.", file=sys.stderr)
        return 2

    log = cat_gcs(f"gs://{args.bucket}/scratch/download_logs/fetch_log.txt")
    codes: dict[str, int] = {}
    types: dict[str, int] = {}
    for line in log.splitlines():
        parts = line.split("\t")
        if parts and parts[0] == "FETCH" and len(parts) >= 5:
            codes[parts[1]] = codes.get(parts[1], 0) + 1
            types[parts[3]] = types.get(parts[3], 0) + 1
    print("HTTP code distribution:", dict(sorted(codes.items())))
    print("Content-type distribution:", dict(sorted(types.items())))
    print(
        "NOTE: any non-200 fetch leaves a stale (HTML) file in raw/uklo_pdf/. "
        "Identify them via the FETCH log and `gcloud storage rm` before normalization."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
