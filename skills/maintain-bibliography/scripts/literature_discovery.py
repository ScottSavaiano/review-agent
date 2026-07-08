#!/usr/bin/env python3
"""literature_discovery.py — the curriculum-owned academic-graph client for the
research agent's stage-7 literature discovery.

Queries OpenAlex, Crossref, and Semantic Scholar directly over their public REST
APIs. No third-party MCP, no third-party Python dependency — standard library
only (urllib + json), so it installs nowhere and runs anywhere Hermes runs
(decision-log 2026-06-27). Keyless / polite-pool: it identifies with a PROGRAM
`mailto` (never a student's email) so OpenAlex and Crossref route us to their
polite pool; Semantic Scholar is keyless at lower limits with an optional key.

Two operations, matching the two skills that use it:

  discover   assemble a candidate set for the reading lists — search each API
             from the topic/brief queries, optionally chase citations backward
             and forward from the reference-article DOIs, merge and dedupe.
             Used by `literature-discovery`.

  resolve    verify one identifier (DOI / URL / arXiv id / free-text citation or
             title) against the academic graph and return the real record, or a
             clear "not resolved" verdict. This is the ANTI-HALLUCINATION guard —
             "a paper that cannot be verified is not found." Used by BOTH
             `literature-discovery` (to confirm supplied "add this" references)
             and `literature-filter-and-verify` (verify-before-list). It never
             invents a record; it only returns what an API actually returns.

  access     classify a candidate's open-access signals into a triage HINT
             (a/b/c). Advisory only — the definitive fetchability probe is
             `fetch-articles` (this just reads the OA metadata the graph gives).

Output is JSON on stdout (or --out FILE); a one-line-per-source status goes to
stderr. Use --dry-run to print the request URLs without calling the network
(offline validation / rate-limit-free inspection).

Examples:
  python3 literature_discovery.py discover \
      --query "adolescent social media depression" \
      --query "screen time mental health teens" \
      --seed-doi 10.1016/j.jadohealth.2020.09.017 \
      --from-year 2015 --max-per-source 25 --out candidates.json

  python3 literature_discovery.py resolve --doi 10.1257/aer.90.4.1064
  python3 literature_discovery.py resolve --citation "Argyle et al 2023 silicon sampling"
  python3 literature_discovery.py access --doi 10.1371/journal.pone.0000000
"""

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

# ---- identity / limits -------------------------------------------------------

# PLACEHOLDER program contact — confirm the real program alias at profile bundle
# time (reconciliation flag 3 in the SKILL: a PROGRAM mailto, never a student's).
DEFAULT_MAILTO = "research-curriculum@bxscience.edu"
UA = "HermesResearchCurriculum/1.0 (classroom use; literature-discovery)"
TIMEOUT = 45
PAUSE = 0.34  # brief courtesy pause between calls (well under any polite-pool cap)

OPENALEX = "https://api.openalex.org"
CROSSREF = "https://api.crossref.org"
S2 = "https://api.semanticscholar.org/graph/v1"
S2_FIELDS = "title,year,abstract,authors,venue,externalIds,citationCount,openAccessPdf"


# ---- HTTP --------------------------------------------------------------------

def http_json(url, headers=None, dry_run=False):
    """GET url and parse JSON. Returns (data, error). Never raises for a network
    or HTTP problem — the caller degrades gracefully so one dead API does not
    sink the whole discover run."""
    if dry_run:
        return None, f"DRY-RUN {url}"
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8", "replace"))
        time.sleep(PAUSE)
        return data, None
    except urllib.error.HTTPError as exc:
        return None, f"HTTP {exc.code} {exc.reason}"
    except Exception as exc:  # URLError, timeout, JSON decode, etc.
        return None, f"{type(exc).__name__}: {exc}"


# ---- normalization helpers ---------------------------------------------------

def norm_doi(value):
    """Return a bare lowercase DOI (10.xxxx/...) from a DOI, a doi.org URL, or a
    string that contains one; else None."""
    if not value:
        return None
    m = re.search(r"10\.\d{4,9}/[^\s\"'<>]+", str(value))
    return m.group(0).rstrip(").,;").lower() if m else None


def norm_arxiv(value):
    if not value:
        return None
    m = re.search(r"arxiv[:/]?\s*(\d{4}\.\d{4,5})(v\d+)?", str(value), re.I)
    return m.group(1) if m else None


def norm_title(t):
    """Lowercase, strip punctuation/whitespace — a dedupe key when DOIs are absent."""
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


def strip_jats(text):
    """Crossref abstracts arrive as JATS XML; strip the tags to plain text."""
    if not text:
        return None
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip() or None


def reconstruct_abstract(inverted_index):
    """OpenAlex ships abstracts as an inverted index {word: [positions]}; put the
    words back in order."""
    if not inverted_index:
        return None
    positions = []
    for word, idxs in inverted_index.items():
        for i in idxs:
            positions.append((i, word))
    if not positions:
        return None
    positions.sort()
    return " ".join(w for _, w in positions)


def blank_record():
    return {
        "title": None, "authors": [], "year": None, "venue": None,
        "doi": None, "identifiers": {}, "abstract": None,
        "citation_count": None, "is_oa": None, "oa_url": None, "oa_pdf_url": None,
        "source": None,          # which API produced the record (or "merged")
        "provenance": "search",  # channel-level; the SKILL overrides for supplied/corpus
        "found_via": None,       # query:<q> | backward:<seed> | forward:<seed> | resolve
        "dual_purpose": False,   # the 🔁 cross-flag — set by the SKILL, not the script
    }


# ---- per-source normalizers --------------------------------------------------

def from_openalex(w):
    r = blank_record()
    r["source"] = "openalex"
    r["title"] = w.get("display_name") or w.get("title")
    r["year"] = w.get("publication_year")
    r["doi"] = norm_doi(w.get("doi"))
    r["authors"] = [a.get("author", {}).get("display_name")
                    for a in (w.get("authorships") or []) if a.get("author")]
    loc = (w.get("primary_location") or {}).get("source") or {}
    r["venue"] = loc.get("display_name")
    r["citation_count"] = w.get("cited_by_count")
    r["abstract"] = reconstruct_abstract(w.get("abstract_inverted_index"))
    oa = w.get("open_access") or {}
    r["is_oa"] = oa.get("is_oa")
    r["oa_url"] = oa.get("oa_url")
    best = w.get("best_oa_location") or {}
    r["oa_pdf_url"] = best.get("pdf_url")
    ids = w.get("ids") or {}
    r["identifiers"] = {k: v for k, v in {
        "doi": r["doi"], "openalex": w.get("id"),
        "pmid": ids.get("pmid"), "mag": ids.get("mag"),
    }.items() if v}
    r["_referenced_works"] = w.get("referenced_works") or []  # for backward chasing
    return r


def from_crossref(it):
    r = blank_record()
    r["source"] = "crossref"
    r["title"] = (it.get("title") or [None])[0]
    r["doi"] = norm_doi(it.get("DOI"))
    r["authors"] = [" ".join(x for x in [a.get("given"), a.get("family")] if x)
                    for a in (it.get("author") or [])]
    r["venue"] = (it.get("container-title") or [None])[0]
    parts = (it.get("issued") or {}).get("date-parts") or [[None]]
    r["year"] = parts[0][0] if parts and parts[0] else None
    r["citation_count"] = it.get("is-referenced-by-count")
    r["abstract"] = strip_jats(it.get("abstract"))
    r["identifiers"] = {k: v for k, v in {"doi": r["doi"], "url": it.get("URL")}.items() if v}
    return r


def from_s2(p):
    r = blank_record()
    r["source"] = "semanticscholar"
    r["title"] = p.get("title")
    r["year"] = p.get("year")
    r["authors"] = [a.get("name") for a in (p.get("authors") or []) if a.get("name")]
    r["venue"] = p.get("venue")
    r["citation_count"] = p.get("citationCount")
    r["abstract"] = p.get("abstract")
    ext = p.get("externalIds") or {}
    r["doi"] = norm_doi(ext.get("DOI"))
    oap = p.get("openAccessPdf") or {}
    r["oa_pdf_url"] = oap.get("url")
    r["is_oa"] = bool(oap.get("url")) or None
    r["identifiers"] = {k: v for k, v in {
        "doi": r["doi"], "s2": p.get("paperId"),
        "arxiv": ext.get("ArXiv"), "pmid": ext.get("PubMed"),
    }.items() if v}
    return r


# ---- search ------------------------------------------------------------------

def search_openalex(query, n, mailto, dry_run):
    filt = []
    if query.get("from_year"):
        filt.append(f"from_publication_date:{query['from_year']}-01-01")
    if query.get("to_year"):
        filt.append(f"to_publication_date:{query['to_year']}-12-31")
    params = {"search": query["q"], "per-page": min(n, 200), "mailto": mailto}
    if filt:
        params["filter"] = ",".join(filt)
    url = f"{OPENALEX}/works?" + urllib.parse.urlencode(params)
    data, err = http_json(url, dry_run=dry_run)
    if err:
        return [], err
    return [from_openalex(w) for w in data.get("results", [])], None


def search_crossref(query, n, mailto, dry_run):
    params = {"query": query["q"], "rows": min(n, 100), "mailto": mailto,
              "select": "DOI,title,author,container-title,issued,"
                        "is-referenced-by-count,abstract,URL"}
    if query.get("from_year"):
        params["filter"] = f"from-pub-date:{query['from_year']}-01-01"
    url = f"{CROSSREF}/works?" + urllib.parse.urlencode(params)
    data, err = http_json(url, dry_run=dry_run)
    if err:
        return [], err
    return [from_crossref(i) for i in (data.get("message", {}).get("items", []))], None


def search_s2(query, n, key, dry_run):
    params = {"query": query["q"], "limit": min(n, 100), "fields": S2_FIELDS}
    if query.get("from_year"):
        params["year"] = f"{query['from_year']}-"
    url = f"{S2}/paper/search?" + urllib.parse.urlencode(params)
    headers = {"x-api-key": key} if key else None
    data, err = http_json(url, headers=headers, dry_run=dry_run)
    if err:
        return [], err
    return [from_s2(p) for p in (data.get("data") or [])], None


# ---- citation chasing (OpenAlex — one graph, keeps it simple) ----------------

def openalex_work_by_doi(doi, mailto, dry_run):
    url = f"{OPENALEX}/works/doi:{urllib.parse.quote(doi)}?mailto={urllib.parse.quote(mailto)}"
    data, err = http_json(url, dry_run=dry_run)
    return (None, err) if err else (data, None)


def openalex_batch(ids, mailto, dry_run):
    """Fetch up to 50 OpenAlex works by id in one call (backward chasing)."""
    out = []
    for i in range(0, len(ids), 50):
        chunk = "|".join(x.rsplit("/", 1)[-1] for x in ids[i:i + 50])
        url = (f"{OPENALEX}/works?filter=openalex:{chunk}"
               f"&per-page=50&mailto={urllib.parse.quote(mailto)}")
        data, err = http_json(url, dry_run=dry_run)
        if err:
            return out, err
        out += [from_openalex(w) for w in data.get("results", [])]
    return out, None


def openalex_citing(work_id, n, mailto, dry_run):
    """Works that cite work_id (forward chasing)."""
    short = work_id.rsplit("/", 1)[-1]
    url = (f"{OPENALEX}/works?filter=cites:{short}"
           f"&per-page={min(n, 200)}&mailto={urllib.parse.quote(mailto)}")
    data, err = http_json(url, dry_run=dry_run)
    if err:
        return [], err
    return [from_openalex(w) for w in data.get("results", [])], None


# ---- dedupe ------------------------------------------------------------------

def dedupe(records):
    """Merge by DOI (fallback normalized title). Keep the richest record; union
    identifiers; prefer a present abstract / OA pdf / citation count."""
    merged = {}
    order = []
    for r in records:
        key = r.get("doi") or ("title:" + norm_title(r.get("title")))
        if not key or key == "title:":
            continue
        if key not in merged:
            merged[key] = r
            order.append(key)
            continue
        keep = merged[key]
        keep["identifiers"] = {**r.get("identifiers", {}), **keep.get("identifiers", {})}
        for f in ("abstract", "oa_pdf_url", "oa_url", "venue", "year"):
            if not keep.get(f) and r.get(f):
                keep[f] = r[f]
        if (r.get("citation_count") or -1) > (keep.get("citation_count") or -1):
            keep["citation_count"] = r["citation_count"]
        if r.get("is_oa") and not keep.get("is_oa"):
            keep["is_oa"] = True
        if len(r.get("authors") or []) > len(keep.get("authors") or []):
            keep["authors"] = r["authors"]
        srcs = set(str(keep.get("source", "")).split("+")) | {r.get("source")}
        keep["source"] = "+".join(sorted(s for s in srcs if s))
    return [merged[k] for k in order]


def clean(records):
    """Drop the internal _referenced_works helper before emitting."""
    for r in records:
        r.pop("_referenced_works", None)
    return records


# ---- access hint -------------------------------------------------------------

def access_hint(r):
    """Advisory triage hint from OA metadata. The definitive fetchability probe
    is `fetch-articles`; this only reads what the graph reported."""
    if r.get("oa_pdf_url"):
        return {"hint": "a", "flag": "✅", "note": "open PDF in the graph — fetch-articles can likely stage it",
                "pdf_url": r["oa_pdf_url"]}
    if r.get("is_oa") or r.get("oa_url"):
        return {"hint": "b", "flag": "🟡✔️", "note": "OA landing page but no direct PDF — may need one human step",
                "landing": r.get("oa_url")}
    return {"hint": "c", "flag": "❌", "note": "no open full text in the graph — likely abstract-only"}


# ---- commands ----------------------------------------------------------------

def cmd_discover(args):
    mailto, status, all_recs = args.mailto, [], []
    sources = set(args.sources)
    queries = [{"q": q, "from_year": args.from_year, "to_year": args.to_year}
               for q in (args.query or [])]

    for q in queries:
        if "openalex" in sources:
            recs, err = search_openalex(q, args.max_per_source, mailto, args.dry_run)
            status.append(f"openalex  query={q['q']!r:40} -> {err or str(len(recs))+' hits'}")
            for r in recs:
                r["found_via"] = f"query:{q['q']}"
            all_recs += recs
        if "crossref" in sources:
            recs, err = search_crossref(q, args.max_per_source, mailto, args.dry_run)
            status.append(f"crossref  query={q['q']!r:40} -> {err or str(len(recs))+' hits'}")
            for r in recs:
                r["found_via"] = f"query:{q['q']}"
            all_recs += recs
        if "s2" in sources:
            recs, err = search_s2(q, args.max_per_source, args.s2_key, args.dry_run)
            status.append(f"s2        query={q['q']!r:40} -> {err or str(len(recs))+' hits'}")
            for r in recs:
                r["found_via"] = f"query:{q['q']}"
            all_recs += recs

    # citation chasing from the reference-article seeds (OpenAlex graph)
    for doi in (args.seed_doi or []):
        d = norm_doi(doi) or doi
        work, err = openalex_work_by_doi(d, mailto, args.dry_run)
        if err or not work:
            status.append(f"seed      {d:44} -> {err or 'not found in OpenAlex'}")
            continue
        seed = from_openalex(work)
        if not args.no_backward and seed.get("_referenced_works"):
            back, berr = openalex_batch(seed["_referenced_works"], mailto, args.dry_run)
            status.append(f"backward  {d:44} -> {berr or str(len(back))+' refs'}")
            for r in back:
                r["found_via"] = f"backward:{d}"
            all_recs += back
        if not args.no_forward:
            fwd, ferr = openalex_citing(work.get("id", ""), args.max_per_source, mailto, args.dry_run)
            status.append(f"forward   {d:44} -> {ferr or str(len(fwd))+' citing'}")
            for r in fwd:
                r["found_via"] = f"forward:{d}"
            all_recs += fwd

    for line in status:
        print(line, file=sys.stderr)
    if args.dry_run:
        print("[dry-run] no records assembled", file=sys.stderr)
        return

    out = clean(dedupe(all_recs))
    print(f"assembled {len(out)} unique candidates from {len(all_recs)} raw hits",
          file=sys.stderr)
    emit({"count": len(out), "candidates": out}, args.out)


def _resolve_lookup(args):
    """Return (record, reason). Tries DOI first (Crossref then OpenAlex), then a
    title/citation search (OpenAlex) for a confident single match."""
    doi = norm_doi(args.doi) or norm_doi(args.url) or norm_doi(args.citation)
    if doi:
        url = f"{CROSSREF}/works/{urllib.parse.quote(doi)}?mailto={urllib.parse.quote(args.mailto)}"
        data, err = http_json(url, dry_run=args.dry_run)
        if data and data.get("message"):
            return from_crossref(data["message"]), None
        work, oerr = openalex_work_by_doi(doi, args.mailto, args.dry_run)
        if work:
            return clean([from_openalex(work)])[0], None
        return None, f"DOI {doi} did not resolve in Crossref ({err}) or OpenAlex ({oerr})"

    arxiv = norm_arxiv(args.url) or norm_arxiv(args.citation)
    if arxiv:
        data, err = http_json(f"{S2}/paper/arXiv:{arxiv}?fields={S2_FIELDS}", dry_run=args.dry_run)
        if data:
            return from_s2(data), None
        return None, f"arXiv:{arxiv} did not resolve ({err})"

    text = args.title or args.citation
    if not text:
        return None, "no identifier given (need --doi / --url / --title / --citation)"
    params = {"search": text, "per-page": 3, "mailto": args.mailto}
    data, err = http_json(f"{OPENALEX}/works?" + urllib.parse.urlencode(params), dry_run=args.dry_run)
    if err or not data or not data.get("results"):
        return None, f"no academic-graph match for {text!r} ({err or 'no results'})"
    top = from_openalex(data["results"][0])
    # accept only a confident title match — do not list on a fuzzy guess
    if norm_title(text) and norm_title(top["title"]).find(norm_title(text)[:40]) < 0 \
            and norm_title(text).find(norm_title(top["title"])[:40]) < 0:
        return None, (f"closest match was {top['title']!r} — not a confident match for "
                      f"{text!r}; supply a DOI to confirm")
    return clean([top])[0], None


def cmd_resolve(args):
    if args.dry_run:
        print(f"[dry-run] would resolve: doi={args.doi} url={args.url} "
              f"title={args.title} citation={args.citation}", file=sys.stderr)
        return
    rec, reason = _resolve_lookup(args)
    if rec:
        emit({"resolved": True, "real": True, "record": rec}, args.out)
    else:
        # the anti-hallucination verdict: not resolved == not found == not listed
        emit({"resolved": False, "real": False, "reason": reason}, args.out)


def cmd_access(args):
    if args.dry_run:
        print(f"[dry-run] would classify access for doi={args.doi}", file=sys.stderr)
        return
    rec, reason = _resolve_lookup(args)
    if not rec:
        emit({"resolved": False, "reason": reason}, args.out)
        return
    emit({"resolved": True, "record": rec, "access": access_hint(rec)}, args.out)


# ---- io ----------------------------------------------------------------------

def emit(obj, out):
    text = json.dumps(obj, indent=2, ensure_ascii=False)
    if out:
        Path(out).write_text(text + "\n", encoding="utf-8")
        print(f"wrote {out}", file=sys.stderr)
    else:
        print(text)


def build_parser():
    # common options live on a parent parser so they are accepted AFTER the
    # subcommand (e.g. `discover --query ... --out x.json`), the conventional shape.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--mailto", default=DEFAULT_MAILTO,
                        help="program polite-pool contact (NOT a student's email)")
    common.add_argument("--s2-key", default=None, help="optional Semantic Scholar API key")
    common.add_argument("--out", default=None, help="write JSON here instead of stdout")
    common.add_argument("--dry-run", action="store_true",
                        help="print request URLs / intent without calling the network")

    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("discover", parents=[common], help="assemble a candidate set")
    d.add_argument("--query", action="append", help="a search string (repeatable)")
    d.add_argument("--seed-doi", action="append", help="reference-article DOI to chase (repeatable)")
    d.add_argument("--from-year", type=int, default=None)
    d.add_argument("--to-year", type=int, default=None)
    d.add_argument("--max-per-source", type=int, default=25)
    d.add_argument("--sources", nargs="+", default=["openalex", "crossref", "s2"],
                   choices=["openalex", "crossref", "s2"])
    d.add_argument("--no-backward", action="store_true", help="skip backward citation chasing")
    d.add_argument("--no-forward", action="store_true", help="skip forward citation chasing")
    d.set_defaults(func=cmd_discover)

    r = sub.add_parser("resolve", parents=[common], help="verify one identifier against the graph")
    r.add_argument("--doi")
    r.add_argument("--url")
    r.add_argument("--title")
    r.add_argument("--citation")
    r.set_defaults(func=cmd_resolve)

    a = sub.add_parser("access", parents=[common], help="OA access triage hint for one identifier")
    a.add_argument("--doi")
    a.add_argument("--url")
    a.add_argument("--title")
    a.add_argument("--citation")
    a.set_defaults(func=cmd_access)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.cmd == "discover" and not (args.query or args.seed_doi):
        print("discover needs at least one --query or --seed-doi", file=sys.stderr)
        return 2
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
