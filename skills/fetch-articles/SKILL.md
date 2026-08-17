---
name: fetch-articles
description: Fetches reference articles into the shared workspace and extracts agent-readable text versions. In the research-agent profile it backs `literature-discovery`'s supplied-article ingest ('add this' / PDF drop), `paper-engagement`'s full-text fetch, and curriculum-corpus staging; fires on request whenever a reference article should be saved locally — the student supplies a URL or DOI, or drops a legitimately obtained PDF into articles/ for text extraction. (The mentor-profile copy also fires at first project startup to pre-stage the method-exemplar library — that startup mode is the mentor's, not fired here.) Never circumvents paywalls; hosts that block scripted clients are reported with the link for a human browser download.
---

# Fetch Articles

**Last edited:** 2026-08-03 (Cowork — **staging source repointed from the private `curriculum-articles` GitHub repository to the class-restricted Drive folder** per the same-date educator ruling eliminating student GitHub accounts. Prose only: `fetch_articles.py` is unchanged, because its existing `--staging <dir>` flag already copies from a local directory and a mirrored Drive folder *is* a local directory. Added the shared-folder-does-not-mirror catch and the shortcut/Shared-drive routes.) Prior: 2026-06-29 (Cowork — **re-bundled into the research-agent profile** from the project-mentor copy (R7a — rules travel, not reimplemented): firing/usage framed for the research lane (supplied-article ingest, full-text fetch, corpus staging); the fetch rules (403-is-final, no paywall circumvention, private-repo staging) are verbatim; delivery-voice neutralized; "Where this skill lives" updated. **Canonical source = the project-mentor copy; sync any change.**) Prior: 2026-06-06 (Cowork — numeric "Type N" reference-article labels retired; practical names throughout). Prior: 2026-06-04 (Cowork — first draft; script tested end-to-end against all 20 manifest entries same day)
*Editing convention: see `00-handoff.md` → "Editing conventions" for editor identifiers and revision-marker rules.*

**Status: Draft, awaiting educator review.** Authored against decision-log entry 2026-06-04 ("Local article staging"), architecture spec §2 (reference-articles typology) and §11 (workspace files), and `design-project` Phase 3f.

## What this skill is

`fetch-articles` maintains the workspace's local article library: canonical PDFs for the student and teacher to read, and extracted text versions for the agents to search and quote. It exists because reference articles do their work only when they are actually present — the mentor teaches from them, the research agent mines them during literature synthesis, the Review Agent checks claims against them, and the student learns published-paper craft by reading them.

The skill is deliberately general. Its first job is pre-staging the method-exemplar library at project startup, but the same mechanism serves any reference article the student selects across the project — Research Problem Articles, Project Reference Articles consolidations, Paper Structure Reference Articles.

## Workspace layout

```
articles/<slug>.pdf        ← canonical copy (figures, tables, typesetting)
articles/text/<slug>.md    ← extracted text, for agent retrieval and quoting
articles/fetch-report.md   ← what succeeded, what needs a browser, what failed
```

The PDF is always canonical. The `.md` extraction is a retrieval surface — its header says so, names the source and extraction date, and carries the do-not-redistribute note. When quoting an article to the student, quote from the extraction but point the student at the PDF.

## When this skill fires

**1. First project startup (exemplar pre-staging) — mentor-profile mode, not fired in the research profile.** When the workspace's `articles/` directory does not yet contain the method-exemplar library, run the script in manifest mode against the `design-project` manifest:

```
python3 scripts/fetch_articles.py --workspace <terminal.cwd> \
  --manifest ../design-project/references/method-exemplars.yaml \
  --staging "<Drive mount>/curriculum-articles/articles"      # see below
```

Of the 22 manifest entries, 13 fetch directly (verified 2026-06-04: NBER, arXiv, ACL Anthology, Harvard DASH, MIT Economics, Opportunity Insights serve scripted clients); 9 require a one-time browser download (PNAS ×7-host block, Elsevier ×2, MDPI). The fetch report lists exactly which, with links. The intended flow is that **provisioning runs this before the student's first session** with the Drive staging directory supplied, so students start with the full library; the skill's startup check is the safety net for workspaces provisioned without it.

The canonical staging source is the **class-restricted Drive folder `curriculum-articles`**, shared to the cohort by the educator, which holds the fully staged 20-article set in both representations. Because every student already runs Google Drive for Desktop in Mirror mode for their workspace, that folder is an ordinary **local directory** on their machine, and staging is a file copy — pass it as `--staging`:

```
python3 scripts/fetch_articles.py --workspace <terminal.cwd> \
  --manifest ../design-project/references/method-exemplars.yaml \
  --staging "<Drive mount>/curriculum-articles/articles"
```

There is **no clone, no git, no account, no authentication and no network call** on this path. It replaced the private `curriculum-articles` GitHub repository on 2026-08-03 (decision log — *NO STUDENT GITHUB ACCOUNTS*), because that repo was the last thing in the program that required a student to hold a GitHub account, and the 2FA that came with it. The repo survives as the **teacher-side** store and version history; students never touch it. The manifest in this skill's sibling (`design-project/references/`) remains the source of truth; the Drive folder is its staged mirror.

**Reaching the folder — the one operational catch.** A folder that arrives in *Shared with me* is **not** mirrored to disk by Drive for Desktop. Two ways to make it local, and the skill accepts either:

- **(a) Shortcut into My Drive** *(documented default)* — the student right-clicks the shared folder at drive.google.com → **Organize → Add shortcut → My Drive**. Shortcuts do mirror. Needs no IT provisioning.
- **(b) A Shared drive** *(preferred where available)* — mirrors at `.../GoogleDrive-<email>/Shared drives/<name>/` with nothing for the student to do. Requires that IT enable shared drives for student accounts; that is an open IT question, not an assumption.

If the folder is not on disk, say so plainly, fall back to manifest mode (13 of 22 entries fetch directly), and tell the student which of (a)/(b) applies to their class. **Never** attempt a network workaround, a clone, or a sign-in.

**2. On request, for any article.** When a conversation settles on a reference article worth keeping locally — a Research Problem Article during research-problem framing, a Paper Structure Reference Article — and a full-text-accessible URL is in hand:

```
python3 scripts/fetch_articles.py --workspace <terminal.cwd> \
  --url <pdf-url> --slug <author-year> --citation "<one-line citation>"
```

**3. Convert-only, for PDFs the student obtained themselves.** When an article is paywalled, the student gets it the legitimate way — school library, public library card, teacher's copy — and drops the PDF into `articles/` as `<slug>.pdf`. Then:

```
python3 scripts/fetch_articles.py --workspace <terminal.cwd> --convert-only
```

extracts text for any PDF lacking it. This is the expected path for a large fraction of student-selected articles, and it is not a failure mode — say so plainly if the student is frustrated.

## The access posture (load-bearing)

This skill **never circumvents paywalls or access controls.** A 403 from a host is a host asking for a browser or a subscription, and the script treats it as final — no retry tricks, no mirror hunting, no proxy suggestions. The agent's register when an article is not freely fetchable: name the legitimate routes (the school library's databases, a public library card, asking the research teacher or faculty mentor, emailing the corresponding author — authors nearly always share) and move on. Local copies are for personal study within the student's own research workspace; nothing in `articles/` is ever committed to a public repository or redistributed. This posture is part of the curriculum's research-integrity project activation sequence, not an inconvenience to route around.

## Maintenance notes

- Extraction tooling: the script prefers poppler's `pdftotext` (fast C implementation; handles graphics-heavy PDFs that stall pure-Python extractors — two of the PNAS exemplars hung both pdfminer.six and pypdf for minutes, while pdftotext finished in seconds) and falls back to `pdfminer.six` (`pip install pdfminer.six`) where poppler is absent. The script degrades gracefully with neither (PDFs fetch; extraction reports the missing tooling).
- Idempotent: existing PDFs are skipped unless `--force`. Re-running after a browser download completes the picture; the report regenerates each run.
- Extraction of two-column academic layouts is serviceable, not beautiful — adequate for search and quoting. Image-only/scanned PDFs are flagged (<500 extracted chars).
- The method-exemplar manifest (`../design-project/references/method-exemplars.yaml`) is owned by `design-project`; when its exemplars change, re-run manifest mode — new slugs fetch, existing ones skip.

## Where this skill lives in the architecture

A **supporting skill**, **re-bundled into the research-agent profile** (2026-06-29) from the project-mentor copy per R7a (rules travel, not reimplemented) — curator-protected and update-refreshed per platform primer §7. In the research profile it provides the fetch capability that `literature-discovery` (supplied-article ingest / 'add this'), `paper-engagement` (full-text staging), and the curriculum-corpus access call. The mentor-profile copy additionally owns the method-exemplar pre-staging (the operational half of `design-project`'s exemplar design); that startup mode is the mentor's. **Canonical source = the project-mentor copy; sync any change across profiles.**

## Status

**Draft, awaiting educator review.** Script smoke-tested 2026-06-04 end-to-end in all three modes against the live manifest: 11/11 scriptable entries fetched, 9/9 browser-only entries correctly routed to the report, staging-directory copy verified, 12/12 extractions clean, idempotency verified. Open authoring items: none at draft time. The provisioning hook (running manifest mode before first session, Tier 9 install scripts) is noted in the implementation plan when Tier 9 is authored.
