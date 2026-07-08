---
name: maintain-bibliography
description: Maintain the student's working bibliography for their paper, human-in-the-loop. A SHARED skill bundled into all three agents (project-mentor, research-agent, review-agent). The full human-in-the-loop verification runs on student demand at any time and always at weekly journaling; at session close only the bibliography's CHANGES are reported (not the verification loop). On each run it reads the current paper draft (working_paper.md) for the student's in-text citations, reconciles them against working_bibliography.md, and for any in-text citation not yet in the bibliography it searches up the full reference and adds it marked UNVERIFIED ✗ (never inventing a DOI or field). It presents the bibliography as an APA-formatted list with a verified ✓ / unverified ✗ mark per entry, and runs the student through DOI-click verification: the student clicks each candidate DOI (or confirms a DOI-less source), confirms it opens the correct work, and only the student's confirmation flips an entry ✗ → ✓. This is the STS-compliance mechanism against AI-hallucinated citations (the 2027 rules prohibit AI-generated citations and the qualifying audit clicks DOIs). Reuses the resolve engine (co-bundled literature_discovery.py). Source of truth: design/citation-integrity-gate-2026-07-08.md. Status — DRAFT (shared skill; first draft 2026-07-08).
---

# Maintain Bibliography (shared — human-in-the-loop citation integrity)

**Last edited:** 2026-07-08 (Cowork — first draft. Authored against `design/citation-integrity-gate-2026-07-08.md` (the authoritative requirement — the continuous working bibliography + the closing gate), the citation-lifecycle audit (decision-log 2026-07-08), `regeneron-sts-reference.md` (§3 AI rules; the 2027 no-AI-generated-citations prohibition + the DOI-clicking audit), and `literature-discovery`'s `resolve` engine. Educator direction 2026-07-08: the student must be in the loop on DOI verification — they click each DOI before it is marked verified.)
*Editing convention: see `00-handoff.md` → "Editing conventions" for editor identifiers and revision-marker rules.*

## What this skill is

This skill keeps the student's **working bibliography** — the reference list for their *paper* — correct, complete, and **human-verified**, continuously across the year rather than in one scramble at the end. It is the primary defense against an **AI-hallucinated citation** reaching the submitted paper: the specific failure the Regeneron STS 2027 rules target by prohibiting AI-generated citations (2026-cycle submissions were caught with fabricated references), and the reason the qualifying audit **clicks DOIs**.

The design principle is **human-in-the-loop**: the agent finds, searches, resolves, and formats — but **only the student's own click on a DOI (or confirmation of a source) marks an entry verified.** The agent never certifies a citation for the student, and never invents one.

This is distinct from `reference_articles.md` (the curated reading-list of reference *articles* the student learns from). This skill maintains **`working_bibliography.md`** — every source the *paper* actually cites.

## Why this meets the Regeneron STS rules

This skill exists to satisfy specific STS requirements, and it is worth being explicit about how (full mapping: `design/citation-integrity-gate-2026-07-08.md`; rules: `regeneron-sts-reference.md` §3):

- **"No AI-generated citations."** The skill **never invents** a citation, DOI, or field — it only searches up, resolves, and formats *real* records; unfindable sources stay flagged ✗, never fabricated. So nothing in the bibliography is AI-generated; every entry is a *verified real* one.
- **AI-as-tooling is permitted, disclosed, cited.** Verifying and formatting references is instrument use (not report authorship), and it is disclosed by name in the student's AI-usage answer.
- **The report is written without AI.** The skill never touches the paper's prose; in-text citations are the student's own; the bibliography is a separate, disclosed artifact.
- **The audit clicks DOIs.** Every indexed work must carry a **real, clickable, resolving DOI**; a bad or missing one is blocked — so any DOI a judge clicks reaches the correct live source.
- **Authentic student contribution.** Only the **student's own click** grants a ✓; the agent's resolve is a pre-check, never the verification. The safeguard is human-owned and the checks are documentable evidence.

## Where this skill lives

A **shared skill, bundled into all three profiles** (project-mentor, research-agent, review-agent), like `fetch-articles`, `check-budget`, and `project-briefing`. It carries a **co-bundled copy of the `resolve` engine** (`scripts/literature_discovery.py`) so it runs in the mentor and Review Agent profiles too, not only the research agent. Any agent the student is with can maintain the bibliography.

## When it runs

**The "full verification process"** means: search up any references missing from the bibliography, then walk the student through verifying **every outstanding unverified ✗ entry** — the student **clicks each unchecked DOI** (type-A indexed works) and **confirms each non-DOI reference is live** (type-B sources) — promoting each to ✓ as they go. It runs in exactly two situations:

- **On student demand, any time** — "show me my bibliography," "check my citations," "am I missing any references?" The full process runs. This is the primary path; the student owns their bibliography and can open it whenever.
- **Every week at journaling time** — the full process is **always** run as part of the weekly reflection: sync the bibliography with the week's writing and verify any new ✗ entries with the student. This is the standing cadence that keeps ✗ from piling up.

At **session close**, the full process does **NOT** run. The per-session close-out summary (cross-agent-obligations V3b) only **reports what changed** in the bibliography this session — e.g. "2 new references were added from your in-text citations and are marked unverified ✗" — so the student knows the state. It does not launch the DOI-click loop; that waits for the student's next on-demand call or the weekly journaling run.

It is **never forced mid-writing** and never interrupts drafting to demand verification.

## The working bibliography file

`working_bibliography.md` (workspace root). An APA-formatted list, split into a **Verified ✓** section and an **Unverified ✗** section, with a header comment explaining the marks. Example:

```markdown
# Working Bibliography — <project>
<!-- Maintained by maintain-bibliography. ✓ = you clicked the DOI/source and confirmed it. ✗ = not yet verified by you. -->

## Verified ✓
- ✓ Gimbrone, C., Bushman, B. J., … (2022). The politics of depression… *Social Science & Medicine*, 301, 114896. https://doi.org/10.1016/j.socscimed.2022.114896

## Unverified ✗  (click the DOI/source and confirm to verify)
- ✗ Smith, J., & Lee, K. (2021). [title] … *Journal Name*, vol(iss), pp.  candidate DOI: https://doi.org/10.xxxx/xxxxx  — auto-added from your in-text cite "(Smith & Lee, 2021)"; not yet clicked
- ✗ "(Doe, 2020)" — in-text cite with no source located yet; needs your input
```

## What it does on each invocation

1. **Read the paper for in-text citations.** Parse `working_paper.md` for the student's own in-text source citations (their APA in-text cites).
2. **Reconcile against `working_bibliography.md`.** Identify in-text citations that have **no matching bibliography entry**.
3. **Search up each missing reference.** For each unmatched in-text cite, use the `resolve`/discover engine to locate the real work; construct the full APA reference with its **candidate DOI** (for an indexed work) or its **URL/identifier** (for a DOI-less source); add it to the bibliography **marked unverified ✗**. If a source cannot be located, add a **flagged stub** naming the in-text cite and asking the student for input — **never fabricate** a DOI, author, year, or any field to fill the gap.
4. **Present the bibliography** as the APA list with each entry's ✓ / ✗ mark, so the student sees at a glance which citations are still unproven.
5. **Run the DOI-click verification** for ✗ entries (below).

## The DOI-click loop — the human-in-the-loop control

For each **unverified ✗** entry:

- The agent may first run `resolve` as a **technical pre-check** — does the candidate DOI resolve against Crossref/OpenAlex/Semantic Scholar at all? If it does **not** resolve, the agent says so plainly and does not present it as ready; the entry stays ✗ and the student is asked to supply the correct source. A non-resolving DOI is never quietly kept.
- The agent presents the **clickable `https://doi.org/<doi>`** and asks the student to **click it, open the source, and confirm it is the correct work they cited.**
- **Only the student's confirmation flips ✗ → ✓.** The agent never marks an entry verified on its own — not even one whose DOI resolves cleanly. The click, and the student's "yes, that's the right paper," are what grant the ✓.
- For a **DOI-less (type-B) source** — a website, report, dataset, news article, book, preprint, or student-database full text with no DOI — there is no DOI to click; the student instead confirms the **live URL / source** is correct and reachable. Same rule: the student's confirmation grants the ✓.

## Type A vs Type B (which sources need a DOI)

- **Type A — indexed scholarly work** (journal article, most conference papers, DOI-bearing books/chapters): a **real, clickable, resolving DOI is required** to verify. No DOI, or a non-resolving DOI → stays ✗.
- **Type B — legitimately DOI-less**: website, government/NGO report, dataset, news article, book without a DOI, preprint, student-database full text, archival/primary material. **Not forced to have a DOI**; verified by confirming the live source. Classify conservatively — if a work *is* indexed with a DOI, it is type A.

## Anti-hallucination — the hard rules

- **Never invent a DOI or any bibliographic field.** Every field comes from the resolved record or the actual source. A field that cannot be sourced leaves the entry ✗ and flagged — it is never completed by the model. This is the defense against an "format these into APA" step inventing a plausible DOI/volume/page.
- **Never mark an entry ✓ without the student's click/confirmation.** Agent resolution is a pre-check, not a verification.
- **Never drop a citation silently or add one silently as verified.** Everything is surfaced with its mark.

## The register — the student-facing moments

Direct, specific, warmth it does not fake; the human-in-the-loop click is always the student's. Register samples (not scripts), educator-approved 2026-07-08:

**Opening the bibliography (on-demand or weekly):**
> "Here's your working bibliography. Six references are verified, three are still unverified — I found those three from citations in your paper, but you haven't checked them yet. Let's go through them now so they're solid."

**The DOI-click prompt (indexed work, type A):**
> "This one's still unverified: Smith & Lee (2021). Here's its DOI — https://doi.org/10.xxxx/xxxxx. Click it and tell me: does it open the exact paper you meant to cite? If yes, I'll mark it verified. If it opens something else or a dead page, we'll track down the right one."

**Confirming a non-DOI source (type B):**
> "This source has no DOI — it's a Pew Research report, which is normal for that kind of source. Here's the link: [url]. Open it and confirm it's live and it's the report you cited. Once you've eyeballed it, I'll mark it verified."

**A DOI doesn't resolve (the pre-check fails):**
> "Heads up on this one: the DOI I found for '(Doe, 2020)' doesn't resolve — when I check it against the citation indexes, nothing comes back. That usually means the DOI is wrong or the reference is off. Can you find the real source? I won't put a citation in your bibliography that a judge would click and hit a dead page."

**No source found (a flagged stub, never invented):**
> "I couldn't find a source matching your in-text cite '(Garcia, 2019)' — no match in the indexes. I've left it in your bibliography as a flag, not a made-up reference. Do you have the paper, or a DOI or link? I won't invent one."

**The session-close change report (part of the V3b close-out summary — reports only, no verification):**
> "One bibliography note before you go: I added 2 references from new citations in your draft today, both marked unverified ✗. Nothing to do right now — we'll click through them next time you check your bibliography, or at your weekly reflection."

**All clear:**
> "That's all of them — every reference in your bibliography is now verified: you clicked each DOI and confirmed each source yourself. That's exactly what STS wants, and you did the checking, not me."

## What this skill does NOT do

- **Write or edit the student's report prose.** It reads the paper for in-text cites and maintains the separate bibliography file; it never touches the paper's sentences (the §8.2 / STS writing line).
- **Certify citations for the student.** The ✓ is the student's to grant by clicking.
- **Invent references or fields.** See the hard rules above.
- **Replace the closing gate.** At submission, `framing-for-competition` runs the final confirmation that zero ✗ remain and emits the References section (`design/citation-integrity-gate-2026-07-08.md`). This skill is what makes that final gate a formality rather than a scramble.

## Relationship to the other citation guards

- **Front end** — `literature-discovery` / `literature-filter-and-verify` already block AI-*found* citations that don't resolve, at reading-list time. This skill picks up at *writing* time, when the student is citing sources in the paper.
- **Backstop** — the Review Agent's `claim-verification` spot-checks are a sampled, advisory second look; this skill is the exhaustive, student-driven maintenance.
- **Closing gate** — `framing-for-competition` (year 3) is the final pre-submission confirmation.

## The resolve engine

Reuses `literature_discovery.py` (co-bundled at `skills/maintain-bibliography/scripts/`): its `resolve` operation confirms a DOI is real against the indices, and its discover/search finds a reference from an in-text cite's author/title/year. No new verifier is introduced.

## Status

**DRAFT (shared skill), first draft 2026-07-08.** Discharges the continuous half of the citation-integrity requirement (`design/citation-integrity-gate-2026-07-08.md`); pairs with the `framing-for-competition` closing gate (unbuilt) and the Review Agent's `claim-verification` backstop. Bundled into all three profiles; carries a co-bundled `resolve` script. Pending: educator voice-read of the student-facing moments, a teacher-admin critique, and bundling/commit with the profiles (mentor + research are live; review lands with its first publish).
