#!/usr/bin/env python3
"""fetch_articles.py — fetch reference articles into the shared workspace and
extract agent-readable text versions.

Three modes:
  Manifest:      python3 fetch_articles.py --manifest PATH [--staging DIR]
  Single fetch:  python3 fetch_articles.py --url URL --slug SLUG [--citation TEXT]
  Convert-only:  python3 fetch_articles.py --convert-only

Layout (relative to --workspace, default current directory):
  articles/<slug>.pdf        canonical copy for the student and teacher
  articles/text/<slug>.md    extracted text for agent search/quoting
  articles/fetch-report.md   what succeeded, what needs a browser, what failed

Never circumvents paywalls or access controls. Hosts that block scripted
clients are reported with the link for a human to use in a browser; the
downloaded file goes in the staging directory (manifest mode) or directly
into articles/ (any mode), and convert-only finishes the job.

Extraction: prefers poppler's pdftotext (fast, robust on graphics-heavy PDFs);
falls back to pdfminer.six (pip install pdfminer.six) when pdftotext is absent.
"""

import argparse
import datetime
import re
import shutil
import sys
import urllib.request
from pathlib import Path

UA = "Mozilla/5.0 (compatible; HermesCurriculumFetcher/1.0; classroom use)"
TIMEOUT = 60


# ---------- minimal manifest parser (no YAML dependency) ----------

def parse_manifest(path):
    """Parse the flat list-of-dicts YAML shape the exemplar manifest uses."""
    entries, current = [], None
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.split(" #")[0].rstrip()
        if not line.strip() or line.strip().startswith("#"):
            continue
        m = re.match(r"^\s*-\s+(\w+):\s*(.*)$", line)
        if m:
            if current:
                entries.append(current)
            current = {m.group(1): _val(m.group(2))}
            continue
        m = re.match(r"^\s+(\w+):\s*(.*)$", line)
        if m and current is not None:
            current[m.group(1)] = _val(m.group(2))
    if current:
        entries.append(current)
    return entries


def _val(s):
    s = s.strip().strip('"')
    if s.startswith("[") and s.endswith("]"):
        return [x.strip() for x in s[1:-1].split(",") if x.strip()]
    return s


# ---------- fetch ----------

def fetch_pdf(url, dest):
    """Download url to dest. Returns (ok, message). Never retries a 403 —
    that is a host telling us to use a browser, and we respect it."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = resp.read()
    except Exception as exc:  # HTTPError, URLError, timeout
        return False, f"{type(exc).__name__}: {exc}"
    if not data.startswith(b"%PDF"):
        return False, "response was not a PDF (host likely requires a browser)"
    dest.write_bytes(data)
    return True, f"{len(data)} bytes"


# ---------- extract ----------

def _extract_via_pdftotext(pdf_path):
    """Poppler's pdftotext: fast C implementation, robust on graphics-heavy PDFs
    that stall pure-Python extractors. Returns text or None."""
    import subprocess
    exe = shutil.which("pdftotext")
    if not exe:
        return None
    try:
        out = subprocess.run([exe, str(pdf_path), "-"], capture_output=True,
                             timeout=120, check=True)
        return out.stdout.decode("utf-8", errors="replace")
    except Exception:
        return None


def extract_text_md(pdf_path, md_path, citation=""):
    text = _extract_via_pdftotext(pdf_path)
    if text is None:
        try:
            from pdfminer.high_level import extract_text
        except ImportError:
            return False, ("no extractor available: install poppler (pdftotext) "
                           "or pdfminer.six")
        try:
            text = extract_text(str(pdf_path))
        except Exception as exc:
            return False, f"extraction failed: {type(exc).__name__}: {exc}"
    if len(text.strip()) < 500:
        return False, "extraction produced <500 chars (scanned or image-only PDF?)"
    today = datetime.date.today().isoformat()
    header = (
        f"# {citation or pdf_path.stem}\n\n"
        f"> Text extracted from `articles/{pdf_path.name}` on {today} for agent retrieval.\n"
        f"> The PDF is the canonical copy — figures, tables, and typesetting live there.\n"
        f"> Local copy for personal study within this research workspace; do not redistribute.\n\n---\n\n"
    )
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(header + text, encoding="utf-8")
    return True, f"{len(text)} chars"


# ---------- main ----------

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workspace", default=".", help="workspace root (default: cwd)")
    ap.add_argument("--manifest", help="manifest YAML of articles to fetch")
    ap.add_argument("--staging", help="directory of human-downloaded PDFs named <slug>.pdf")
    ap.add_argument("--url", help="single-article mode: URL to fetch")
    ap.add_argument("--slug", help="single-article mode: filename slug")
    ap.add_argument("--citation", default="", help="single-article mode: citation line")
    ap.add_argument("--convert-only", action="store_true",
                    help="extract text for any PDF in articles/ lacking a text version")
    ap.add_argument("--force", action="store_true", help="re-fetch / re-extract even if present")
    args = ap.parse_args()

    ws = Path(args.workspace)
    art = ws / "articles"
    txt = art / "text"
    art.mkdir(parents=True, exist_ok=True)
    txt.mkdir(parents=True, exist_ok=True)

    fetched, staged, skipped, needs_browser, failed = [], [], [], [], []
    citations = {}

    def handle(slug, url, backup, method, citation):
        citations[slug] = citation
        pdf = art / f"{slug}.pdf"
        if pdf.exists() and not args.force:
            skipped.append(slug)
            return
        if args.staging:
            cand = Path(args.staging) / f"{slug}.pdf"
            if cand.exists():
                shutil.copy2(cand, pdf)
                staged.append(slug)
                return
        if method == "browser":
            needs_browser.append((slug, url))
            return
        ok, msg = fetch_pdf(url, pdf)
        if not ok and backup:
            ok, msg = fetch_pdf(backup, pdf)
        if ok:
            fetched.append(slug)
        else:
            failed.append((slug, url, msg))

    if args.manifest:
        for e in parse_manifest(args.manifest):
            handle(e["slug"], e.get("url", ""), e.get("backup_url", ""),
                   e.get("fetch", "script"), e.get("citation", ""))
    elif args.url:
        if not args.slug:
            sys.exit("--url requires --slug")
        handle(args.slug, args.url, "", "script", args.citation)
    elif not args.convert_only:
        ap.print_help()
        sys.exit(1)

    # extraction pass: every PDF in articles/ lacking (or --force) a text version
    extracted, extract_failed = [], []
    for pdf in sorted(art.glob("*.pdf")):
        md = txt / f"{pdf.stem}.md"
        if md.exists() and not args.force:
            continue
        ok, msg = extract_text_md(pdf, md, citations.get(pdf.stem, ""))
        (extracted if ok else extract_failed).append((pdf.stem, msg))

    # report
    today = datetime.date.today().isoformat()
    lines = [f"# Article fetch report — {today}\n"]
    if fetched:
        lines.append("## Fetched\n" + "\n".join(f"- {s}" for s in fetched) + "\n")
    if staged:
        lines.append("## Copied from staging\n" + "\n".join(f"- {s}" for s in staged) + "\n")
    if skipped:
        lines.append("## Already present (skipped)\n" + "\n".join(f"- {s}" for s in skipped) + "\n")
    if needs_browser:
        lines.append("## Needs a browser download\n"
                     "Open each link, download the PDF, save it as `<slug>.pdf` in the staging\n"
                     "directory (or directly in `articles/`), then re-run.\n" +
                     "\n".join(f"- **{s}**: {u}" for s, u in needs_browser) + "\n")
    if failed:
        lines.append("## Failed\n" + "\n".join(f"- **{s}**: {u} — {m}" for s, u, m in failed) + "\n")
    if extracted:
        lines.append("## Text extracted\n" + "\n".join(f"- {s} ({m})" for s, m in extracted) + "\n")
    if extract_failed:
        lines.append("## Extraction problems\n" + "\n".join(f"- **{s}**: {m}" for s, m in extract_failed) + "\n")
    report = art / "fetch-report.md"
    report.write_text("\n".join(lines), encoding="utf-8")

    print(f"fetched={len(fetched)} staged={len(staged)} skipped={len(skipped)} "
          f"needs_browser={len(needs_browser)} failed={len(failed)} "
          f"extracted={len(extracted)} extract_failed={len(extract_failed)}")
    print(f"report: {report}")
    return 0 if not failed and not extract_failed else 2


if __name__ == "__main__":
    sys.exit(main())
