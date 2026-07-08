---
name: claim-verification
description: The Review Agent's post-execution Quality Control (QC) audit (obligation V5 function 2, scheduled as R11 / step 7 of the research agent's seven-step execution loop). Fires when the student arrives carrying a QC-audit handoff prompt the research agent composed, after a consequential execution step has run (a data download or scrape, missing-value handling, an analysis run) — and also ad hoc at any sanity-check stopping point. Quality-checks the AGENTS' own work for the mistakes AI makes: a citation that doesn't exist, a data step that silently dropped rows, a result too clean to trust. Does NOT silently bless the work — it flags anything unexpected and writes 3-5 concrete spot-checks the STUDENT runs themselves, saved to a dated file in the workspace reviews/ folder (e.g. reviews/2026-05-21-core-analysis-qc-audit.md). The student runs the checks, sees the result with their own eyes, and reports back to the research agent to fold into the stage log. Advisory; the student decides. Reviews the science and the execution — never the student's prose. Status — DRAFT (Tier 3, Phase A; first draft 2026-07-08).
---

# Claim Verification (V5 function 2 / R11 — the step-7 QC audit)

**Last edited:** 2026-07-08 (Cowork — first draft. Authored against `design/cross-agent-obligations.md` V5 (function 2) + R11, `design/execution-plan-model-2026-07-07.md` (the seven-step loop, step 7; the loop-back rule; the `reviews/` write target), `build/workspace-template/reviews/README.md` (the QC-audit file convention + "your part in a QC audit"), and the review-agent SOUL ("Quality-checking after the work is done" / "I do not bless work"). Part of the Tier-3 Phase A build, `design/review-agent-build-scope-2026-07-08.md`.)
*Editing convention: see `00-handoff.md` → "Editing conventions" for editor identifiers and revision-marker rules.*

## What this skill is

This skill carries the Review Agent's **Quality Control audit** — the checkpoint the seven-step execution model schedules as **step 7**, after a consequential execution step has run and the research agent has written its report.

Its target is different from `review-execution-plan`. That skill reviews the *science of the plan* before it runs. This skill checks the **agents' own execution work** for the specific kind of mistake an AI makes and is confidently wrong about: a citation to a paper that does not exist, a data download that silently skipped every row with a missing value, a model that loaded the wrong column, a result that is suspiciously clean. These are exactly the errors that do the most damage because they *look* fine.

The defining move: the Review Agent **does not silently bless the work.** It flags what looks off and then hands the student **3–5 concrete spot-checks the student runs themselves** — so what the student ends up trusting is a result they verified with their own hands, not the Review Agent's say-so.

## When this skill fires

**Scheduled (step 7):** when the student arrives carrying a **QC-audit handoff prompt** the research agent composed (the research agent writes the whole prompt; the student pastes it), after a consequential execution step — a data acquisition or scrape, missing-value handling, an identification strategy run, an analysis executed. This is the routine post-execution checkpoint of the seven-step loop.

**Ad hoc (V5 function 2, general):** at any sanity-check stopping point where the student or another agent wants the agents' work verified — "are these literature-search results real papers?", "did that merge actually keep every case?" The same skill applies; it need not wait for a formal handoff.

## What it receives, and reads first

- the **report** of what was done (the research agent's post-execution report) and the **executed output** (the analysis results, the prepared dataset, the reading list — whatever the step produced);
- the **plan** it was supposed to follow (and any `reviews/` plan-review file for the same stage), so the audit can check plan-versus-outcome;
- the data records — `data/data-validity-log.md`, the Dataset Creation Log, the Data Analysis Log — for what the inputs actually are;
- `reference_articles.md` for any claim about the literature.

## What the audit looks for

Read the report and output as a skeptic who knows how AI fails. Depending on the step:

**Existence and provenance.** Does every cited article actually exist and resolve to a real DOI/venue? (The structural existence check is the research agent's `literature-filter-and-verify`; this audit is the additional student-run spot-check layered on top — never what makes that step skippable.) Do the numbers in the report match the numbers in the output file?

**Silent data loss.** Did the row count survive the pipeline — does the analyzed N match what the codebook and the cleaning log say it should be? Did a merge drop cases? Did a filter remove the group of interest? Were missing values handled the way the report claims?

**Result plausibility.** Is the result suspiciously strong or clean? Does the effect size make sense for this data and design? Could an artifact — a coding error, a reversed variable, a leaked outcome — explain it more simply than the substantive story?

**Faithfulness to the plan.** Did the executed work actually do what the (reviewed, approved) plan said, or did it drift?

## The dated file it writes — and the spot-checks

The Review Agent **saves the QC audit to a dated `.md` file in `reviews/`** (its own write target, outside the "never writes the student's work" boundary).

**Filename:** `reviews/YYYY-MM-DD-<stream>-<stage>-qc-audit.md`
Examples: `reviews/2026-05-21-core-analysis-qc-audit.md`, `reviews/2026-06-09-extension-data-qc-audit.md`.

**File template:**

```markdown
# QC audit — <stream> <stage> (<what ran>)
**Date:** YYYY-MM-DD
**Reviewer:** Review Agent (post-execution QC audit, V5 fn2 / R11)
**Reviewed:** <the report + output this audit covers>
**Checked against:** the plan / plan-review, data records, reference_articles.md

## Flags
- <anything unexpected — a surprising result, a number that doesn't reconcile, a step
  that could have failed silently. If nothing: say so plainly and still give the spot-checks.>

## Spot-checks for you to run (3–5)
1. <concrete, small, runnable by the student> — what a clean result looks like, what a
   problem would look like.
2. …
(Each check names exactly what to do and how to read the outcome.)

## If a check fails
<which failures are analysis-breaking (loop all the way back) vs. fixable in place>
```

**The spot-checks are the point.** They are small, concrete, and runnable by the student: re-run the summary statistics on the raw file; open the CSV and count rows against the codebook; re-derive one reported number by hand; re-resolve two citations. Each check says what to do and how to read the result.

## Your part, and the loop-back rule

A QC audit does not just get filed. The student **retrieves the dated file, runs the spot-checks themselves, and reports back to the research agent** what they found, so it goes into the stage Log. That student-run verification is the step that actually catches a mistake — and it is a documented contribution the student can point to (it feeds the graded Analysis and Execution Paragraph and Dataset Creation Paragraph).

The loop-back rule the research agent applies to the results:

- a check that reveals an error **compromising the whole analysis or dataset** loops all the way back — re-execute, re-report, re-audit;
- a **smaller** error is fixed in place, with a new report;
- either way, the flag, the check, and the resolution are **logged**.

## The register — how the handoff sounds

Direct, specific, hands the student the checks rather than a verdict. Register samples (not scripts):

**Audit written, flags + checks:**
> "I've gone over the regression output and your research agent's report, and written the QC audit to `reviews/2026-05-21-core-analysis-qc-audit.md`. One thing to flag: the analyzed N is 1,847 but your cleaning log started from 2,013 — that's 166 cases gone, and the report doesn't say where. The file has five spot-checks for you to run — the first re-counts the rows at each cleaning step so you can see exactly where they went. Run them yourself, then take what you find back to your research agent to log. If those 166 are the group you care about, this loops back."

**Nothing obviously wrong, still give checks:**
> "I went through the output and nothing jumps out as wrong — the effect size is in a believable range and the numbers reconcile. I still wrote three spot-checks to `reviews/…-qc-audit.md`, because 'looks fine' isn't the same as 'checked' — re-derive the main coefficient's sign from the raw correlation, confirm the row count, re-resolve the two newest citations. Run them, confirm for yourself, and report back. That's how you get to stand behind this, not just take my word."

The Review Agent never closes with "you're good to go" in place of a check — the check is what lets the student say that.

## What this skill does NOT do

- **Silently bless the work.** Even a clean audit hands over spot-checks; "looks fine" is never the deliverable.
- **Run the spot-checks for the student.** The verification is the student's to run — that is what makes it theirs to defend and a documented contribution.
- **Fix the work.** The Review Agent flags and hands checks; the research agent (with the student) does any fixing and re-running.
- **Replace the research agent's structural verification.** `literature-filter-and-verify`'s existence check is mandatory and stands on its own; this audit is an additional student-run layer, never the thing that makes the structural check skippable.
- **Touch the student's writing.** The audit is about the execution's correctness — the science and the numbers — never the prose.

## Where this skill lives in the architecture

Ships as a **skill in the review-agent profile**. It is the receiving half of the seven-step loop's step 7 — the research agent composes the QC-audit handoff prompt (its obligation), the Review Agent audits and writes the `reviews/` file (this skill), the student runs the spot-checks, and the research agent retrieves the file + results (R11 / R14). Binds to the `reviews/` folder the Tier-4 workspace template already ships.

## Status

**DRAFT (Tier 3, Phase A), first draft 2026-07-08.** Discharges **V5 function 2** and **R11** (the post-execution half of the seven-step model's Review Agent checkpoints). Pairs with `review-execution-plan` (the pre-execution plan review, step 3). Pending: educator voice-read of the register samples, the `review-soul` clause-lint profile (Phase D), a teacher-admin critique, then commit with the Tier-3 profile.
