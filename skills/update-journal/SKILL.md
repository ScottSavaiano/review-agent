---
name: update-journal
description: The Review Agent's weekly journaling workflow (obligations V1 / V1a / V1a-ext / V2 / V3), owned by the Review Agent. Runs once a week (the Friday reflection). Three parts: (1) the week's record — a receipts-based summary reconstructed from workspace file history + the week's decisions.md + the logs + bibliography changes, from which it proposes top-3 candidates in four buckets (accomplishments, decisions, open questions, next-week follow-ups); (2) the Reflection Paragraph the student writes in two halves — (a) a MANDATORY response to at least one STS essay/application-question prompt (this week's peppered prompt from the academic-year calendar, plus any stage-fired prompt that came due), with the relevant project artifacts surfaced as raw material, and (b) an open-write (free-write anything else, with the Top-3 lists as optional material — no required pick); (3) the current-cycle status read (activation + current cycle only; finished cycles sealed; no future cycles; within-cycle progress; read-only vs project_paper_status.md, discrepancies surfaced to the mentor). The peppered STS prompts are the substance of the reflection and also accumulate in the separate always-accessible STS evidence bank (application-evidence.md). The agent prompts and surfaces material but NEVER composes the student's prose (§8.2). Journals are written into the workspace, which syncs to the teacher's shared Google Drive view automatically (no push step). Source of truth: design/weekly-journal-and-sts-evidence-2026-07-08.md. Status — DRAFT (Tier 3, Phase B; first draft 2026-07-08).
---

# Update Journal (weekly reflection — Review Agent V1)

**Last edited:** 2026-07-08 (Cowork — first draft. Authored against `design/weekly-journal-and-sts-evidence-2026-07-08.md` (the authoritative design — the three-part spine, the two-half Reflection Paragraph, the peppered calendar, the stage-gated table, the evidence bank, the adaptivity rules), `design/cross-agent-obligations.md` V1/V1a/V1a-ext/V2/V3, and `regeneron-sts-reference.md` §4 (the application-question map). Part of the Tier-3 Phase B build.)
*Editing convention: see `00-handoff.md` → "Editing conventions" for editor identifiers and revision-marker rules.*

## What this skill is

The Review Agent's **weekly journaling workflow**. It runs once a week (the Friday reflection, invoked by the weekly-reflection cron — Phase B2 — or on the student's request), and the Review Agent **owns** it (V3): other agents may invite a reflection at a natural close, but only this skill runs the workflow.

It produces the week's `journals/<student-name>-<date>.md`, and it feeds a separate, always-accessible **STS evidence bank** (`application-evidence.md`) that the student builds across the 2.5 years.

Two commitments shape everything below: the **peppered STS prompts are the substance of the reflection** (the student responds to at least one application-question prompt every week, so the evidence stays front-of-mind and the late scramble disappears), and the agent **never composes the student's prose** — it prompts, and it surfaces the student's own artifacts as raw material (§8.2). Journals are written into the workspace, which lives in Google Drive (Mirror mode) and syncs to the teacher's shared view automatically — so the teacher can see them without any push step.

## The weekly run — three parts, in order

### Part 1 — the week's record (receipts)

Reconstruct what actually happened this week and show it to the student, so they never face a blank page:
- the workspace file history (files written/changed, stages advanced);
- the week's `decisions.md` entries;
- the logs touched (`reviews/` plan-reviews and QC-audits, the Dataset Creation / Data Analysis / Data Validity logs);
- bibliography changes (new ✗ entries, entries verified ✓).

From this, propose **top-3 candidates in each of four buckets**: **accomplishments**, **decisions**, **open questions**, **next-week follow-ups**. This is *fodder* for Part 2 — the student will draw on it — not a deliverable to be filed on its own.

**Two things must be swept up if they happened this week and are not yet in the journal:**

**The data-policy check.** If `check-data-policy` ran this week (Stage 5, or a source/door change at Stage 18/22),
its notes are sitting in `data/data-validity-log.md` and the student has not necessarily written them up. Surface
them and ask for it — *in their own words*: which source, which door, what the policy actually says (quoted), what
mode they are in, why that follows from the clause, and what it changes about how they work. It belongs in the
journal the week it happened or soon after. Later it becomes a Methods sentence.

**The prompt log and AI-use citation.** The weekly reflection carries both (R.1). If the agent wrote code this
week, or helped identify a statistical test, or was used to develop an idea, the **Society for Science AI Use
Table requires a log of the prompts** and an explicit citation of which portions were AI-generated. Not optional,
and not something to reconstruct at the end of two years.

### Part 2 — the Reflection Paragraph (the student writes it)

The two halves:

**(a) The required STS response — mandatory, at least one.** Surface **this week's peppered prompt** (from the calendar below) **plus any stage-fired prompt that came due this week** (see the stage-gated table). For each, surface the relevant project artifacts as raw material — the stage's logs, the week's decisions, the records — so the student is writing from their own work, not from memory. The student answers **in their own words**; the agent never drafts it. Each response is dated and appended to the **STS evidence bank** under its application-question heading.

**(b) The open-write.** The student free-writes anything else they want to keep in the journal — open questions, something they're proud of, a frustration, a big upcoming milestone they want to think on. The **Top-3 lists from Part 1 are available as optional material** to pull from if something sparks; there is **no required pick**.

The whole paragraph is the student's; the agent may ask one clarifying question but writes none of it.

### Part 3 — the current-cycle status read (V2)

A plain-language milestone check: the activation steps + the **current** cycle's stages and sections. Finished cycles show **sealed/done**; **future cycles are not listed** — whether a Cycle 2 or 3 happens is decided only after the current cycle's results, so nothing future is shown as "pending," and progress is reported **within-cycle only**, never as a percent of the whole project. Reconcile **read-only** against `project_paper_status.md`; if the student's sense of where things stand differs from the file, **surface the discrepancy for the mentor's next session** (M1) — do not silently change the file (this skill never writes `project_paper_status.md`).

### The parking-lot review (X5)

Read the **Open** section of `journals/parking-lot.md` — the off-topic items any of the three agents parked during the week (the X5 write-path). Surface each to the student and let them triage it: **take it up** on their own somewhere better suited to it, **keep it parked**, or **drop it**. For each item the student resolves, move it to the **Resolved** section with a one-line note of what they decided (`- [x] … → resolved: <decision>`); leave the rest open. If the parking lot is empty, say so and move on. This is the moment the weekly-reflection list the redirect skills promised actually gets reviewed — nothing parked is lost, and nothing off-topic ever eats research time to get here.

## The STS evidence bank (`application-evidence.md`)

A separate, persistent workspace file, always openable by the student ("show me my application evidence"). It aggregates **every** STS-tagged response — the weekly peppered ones from Part 2(a) **and** the stage-fired ones — organized by application question, each entry dated. The agent **appends**; it never composes. This is what the student later mines, in their own words, for the actual application — the finalize pass, never new late drafting.

## The three firing modes

**A. Stage-gated (point-in-time, mandatory) — fires when a stage completes, while the work is fresh; surfaces that stage's artifacts.**

| Fires at | Prompt (working name) | STS item | Words |
|---|---|---|---|
| Project Activation A (research problem) · Stage 11 | "Where my idea came from" | Q9 | 250 |
| Project Activation A · Stage 16 | "Why I'm doing this study" | Q12a | 200 |
| Project Activation B (methods setup) · Stage 14 | "How I designed it" | Q12b | 200 |
| Stage 5 · 18/22 | "What parts of data collection I did myself" (surface the 3 logs) | Q12c–d | 200 |
| Stage 19/23 | "What I did in the analysis" (surface the 3 logs) | Q12e | 200 |
| Stage 21/25 | "What I concluded and how I got there" | Q12f | 200 |
| Stage 11 · 21/25 | "Why this matters and what's next" | Q15 | 200 |
| Stage 9 · 13 | Title + layperson's summary | — | 275 |
| Stage 12 | "Support and disclosures" | Disclosure/COI | 200 |

The three logs surfaced at the data/analysis prompts: **Data Validity Log** (Stage 5), **Dataset Creation Log** (18/22), **Data Analysis Log** (19/23).

**B. Peppered (recurring developmental) — the substance of the weekly reflection, on the fixed calendar below.**

| Prompt (working name) | STS item |
|---|---|
| "How I've grown / where this is heading" | Essay 1 |
| "What was mine / what I didn't do" | Q11 + Q13 |
| "Limitations / what I'd caveat" | Q14 |
| "AI use so far" | Q8–9 |
| "Anything a reader might flag" | Q7 |
| "Something beyond research" | Essay 2 |

**C. Continuous / automatic.** Q10 (duration) + the data timeline are harvested from the dated journals + git — a light confirm, never a writing task.

## The peppered calendar (one academic year; repeats each of the 2.5 years)

Every non-off week surfaces one peppered prompt (repeats are fine); stage-fired prompts layer on in real time.

| Month·Week | Prompt | | Month·Week | Prompt |
|---|---|---|---|---|
| Sep 1 | off (year start) | | Feb 1 | Essay 1 |
| Sep 2 | off (year start) | | Feb 2 | Q11+Q13 |
| Sep 3 | Essay 1 | | Feb 3 | Q14 |
| Sep 4 | Q11+Q13 | | Feb 4 | off (winter break) |
| Oct 1 | Q14 | | Mar 1 | Essay 1 |
| Oct 2 | Q8–9 | | Mar 2 | Q7 |
| Oct 3 | Essay 1 | | Mar 3 | Q8–9 |
| Oct 4 | Q11+Q13 | | Mar 4 | Q11+Q13 |
| Nov 1 | Q14 | | Apr 1 | off (spring break) |
| Nov 2 | Q7 | | Apr 2 | Essay 1 |
| Nov 3 | Essay 1 | | Apr 3 | Q14 |
| Nov 4 | off (Thanksgiving) | | Apr 4 | Essay 2 |
| Dec 1 | Q11+Q13 | | May 1 | Essay 1 |
| Dec 2 | Q14 | | May 2 | Q11+Q13 |
| Dec 3 | off (winter recess) | | May 3 | Q14 |
| Dec 4 | off (winter recess) | | May 4 | off (last week of May) |
| Jan 1 | Essay 1 | | Jun 1 | Essay 1 |
| Jan 2 | Q8–9 | | Jun 2 | Q7 / Q8–9 (year-end wrap) |
| Jan 3 | Essay 2 | | Jun 3 | off (last week of school) |
| Jan 4 | off (midyear exams) | | | |

The skill resolves the current academic week from the date against this calendar to pick the week's peppered prompt.

## Adaptivity rules over the fixed calendar

1. **Early-program substitution.** If the calendar lands on Q7 or Q8–9 before there is anything to say (early year 1 — no paper, little AI-execution history yet), substitute an always-available developmental prompt (Essay 1 / Q11+Q13 / Q14). The calendar is the default; project maturity governs.
2. **Stage-fired layering.** When a stage completes in a given week, its mandatory prompt is added *on top* of the peppered one — that week carries two or more.
3. **No double-drafting.** If a stage-fired prompt and the peppered prompt would ask essentially the same thing the same week, collapse them to one.

## The register — the student-facing moments

Direct, warm without flattery; the writing is always the student's. Register samples (not scripts), pending educator voice-read:

**Opening (Part 1 → Part 2):**
> "Here's your week, pulled from what you actually did — three things you got done, the decisions you logged, the questions still open, and what's queued for next week. Don't start from a blank page; start from this. When you're ready, we'll write your reflection."

**The required STS prompt (peppered, e.g. Essay 1):**
> "This week's reflection prompt is one you'll come back to from time to time over the course of your personal research project journey: 'How have you grown as a researcher lately? What can you do or see now that you couldn't a few months ago, and where do you think this is heading?' The materials from this week's progress report could be a great place to start, but write whatever you want: I'll log what you say in your application-evidence file so it's there when you need it."

**A stage-fired prompt layered on (e.g. after the analysis stage):**
> "You also just finished your core analysis this week, so there's a second, one-time prompt — while it's fresh: what did you actually do in the analysis, and what calls did you make along the way? Here are your Data Analysis Log and Data Validity Log to jog your memory. Write it in your own words."

**The open-write:**
> "That's the required part. Now the open half — write about anything else you want to keep in your journal, including for example any open questions you have, something you're proud of, a frustration, or something big coming up in your project milestones that you want to 'journal on.' Your Top-3 lists from a moment ago are there to pull from if any of them spark something."

**Surfacing artifacts, never drafting:**
> "I've pulled the records so you're writing from your own work, not from memory. I won't write any of it for you — that's the one line I hold — but ask me anything about what's in these logs."

**The status read (Part 3):**
> "Last thing — where the project stands. You're in Cycle 1, on the core analysis stage; the activation and your planning stages are done. I'm not counting future cycles, since whether there's a Cycle 2 depends on how this one lands. One mismatch with your status file — you have the core Results marked started, the file doesn't — I'll flag that for your mentor rather than change it myself."

**The parking-lot review (X5):**
> "You parked three off-topic things this week — a Common App question, a stats-class problem, and 'find me a summer program.' Want to take any of them up on your own now, keep them parked, or drop them? Whatever you decide, I'll mark it — nothing here was lost, it just waited for the right moment, which is now."

## What this skill does NOT do

- **Compose the student's prose** — reflection or STS-evidence (§8.2). Prompts + surfaced artifacts only; one clarifying question is fine, a written sentence is not.
- **Grade** anything — grading is the teacher's call, not the agent's (and the agent stays silent on whether any given reflection is graded).
- **Write `project_paper_status.md`** — read-only; discrepancies go to the mentor (M1).
- **Run a per-session reflection** — V3a (per-session reflection) is not adopted; the session-close *summary* is a separate logging receipt (B3), not this workflow.
- **Show future cycles as "pending"** or a percent-of-whole-project (V2).

## Where this skill lives in the architecture

Ships in the **review-agent profile** (the Review Agent owns the journal, V3). Invoked by the **weekly-reflection cron** (Phase B2), which wraps it with the closing acts — V1c corpus-integrity audit, the full `maintain-bibliography` verification, and the V6 archival snapshot. *(The former V1b weekly commit+push closing act is retired under the 2026-07-09 Drive-based-workspace decision — Drive Mirror sync is the teacher-visibility heartbeat now; see cross-agent-obligations V1b.)* Reads `journals/` and writes `journals/<student>-<date>.md` + appends `application-evidence.md`. Composes with `project-briefing` (the shared status engine the weekly journal opens with) and `maintain-bibliography`.

## Status

**DRAFT (Tier 3, Phase B), first draft 2026-07-08.** Discharges V1/V1a/V1a-ext/V2/V3. Pending: the `review-soul` clause-lint profile (Phase D); teacher-admin critique; then ships with the review-agent's first publish. (Register moments voice-read + approved 2026-07-08; the weekly-reflection cron is built — B2.) Source of truth: `design/weekly-journal-and-sts-evidence-2026-07-08.md`.
