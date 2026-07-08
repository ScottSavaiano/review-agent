---
name: paper-coverage
description: The read-only paper-coverage view + archival snapshot — the shared, safe subset of compile-working-paper, bundled into all three agents. It READS working_paper.md, reconciles it against the expected-item set (section-scaffolds.yaml + the student's paper_structure.md), and renders a chat-window coverage view (written / open per section, a progress count, and a ≈N-of-25-pages reading), and it can take a dated archival snapshot of working_paper.md into versions/. It NEVER ingests the Google-Docs round-trip, NEVER reconciles-writes or regenerates working_paper.md, NEVER re-surfaces markers or restores headings, and NEVER touches the student's prose — all of that stays single-homed in the mentor's compile-working-paper (the one compiler/reconciler of the living paper). This exists so project-briefing (all three profiles) and the review agent's weekly cron (V6 archival snapshot) can read coverage and snapshot the paper without a second agent ever recompiling it. Purely mechanical: no judgment on the writing, not a rationale trigger, not a model-escalation moment. Status — DRAFT (2026-07-09).
---

# Paper Coverage (read-only view + archival snapshot — shared)

**Last edited:** 2026-07-09 (Cowork — first draft. Extracted as the read-only subset of `compile-working-paper` (S3 option c) so `project-briefing` (bundled in all three profiles) and the Review Agent's weekly cron (V6) can read paper coverage and snapshot the paper without giving the research/review profiles a second **compiler** of the living paper. `compile-working-paper` stays **single-homed in the mentor** as the sole round-trip reconciler/writer of `working_paper.md` (R8/R10, contract §4.6, spec §5.4/§12). Authored against the `compile-working-paper` SKILL.md (modes 1/3, the read/render + `versions/` snapshot) and decision-history §8.2 (never judges/authors the writing).)
*Editing convention: see `00-handoff.md` → "Editing conventions" for editor identifiers and revision-marker rules.*

## What this skill is

`paper-coverage` is the **read-only, mechanical** slice of the paper-state machinery — the part that is safe to run from any profile because it never *compiles* or *changes* the paper. It does two things:

1. **Reads and renders the coverage view.** It reads `working_paper.md`, reconciles it against the expected-item set (`section-scaffolds.yaml` + the student's `paper_structure.md`), and renders a chat-window status view: written / open per section, a progress count, and a **≈ N of 25 pages** reading. Pure read + render.
2. **Takes an archival snapshot (on request).** It can copy the current `working_paper.md` into `versions/` under a dated filename and report the delta ("your paper grew ~N pages this week" / "unchanged — fine to note"). A backup copy — never a reconcile.

That is the whole of it. It is the shared, all-three-profiles counterpart to the mentor-only `compile-working-paper`.

## The hard boundary — it reads and snapshots; it never compiles the paper

`compile-working-paper` (mentor only) is the **one compiler/reconciler** of the living paper — it ingests the student's Google-Docs round-trip, format-converts it back into `working_paper.md`, re-surfaces dropped scaffold markers, and restores dropped headings. `paper-coverage` does **none** of that:

- It **never ingests the round-trip** (no OAuth pull, no Markdown export ingest, no regeneration of `working_paper.md` from the Doc).
- It **never reconciles-writes** `working_paper.md`, never re-surfaces a marker, never restores a heading. If reconciliation surfaces a *dropped* item, `paper-coverage` **reports it as an open coverage fact**; it does not re-lay the marker (that is `compile-working-paper`'s reconcile-write, and it stays in the mentor).
- It **never touches the student's prose** — never composes, edits, or judges the writing (decision-history §8.2).
- The **only** thing it writes is a `versions/` archival **copy** of the paper (a backup, not a change to `working_paper.md`). Even that is a mechanical snapshot, never a reconcile.

So there is still exactly **one** agent that recompiles the living paper (the mentor, via `compile-working-paper`); `paper-coverage` only ever looks and backs up. If a student in the research or review profile wants their latest Doc edits *pulled in and recompiled*, that is `compile-working-paper`'s job — they do it with the mentor. `paper-coverage` can tell them their coverage as it stands and point them there.

## When it fires

- **`project-briefing` calls it** (all three profiles) for the paper-coverage slice of the session-open brief — the read/render, mode 1.
- **The Review Agent's weekly cron calls it** for the **V6 archival snapshot** — the dated `versions/` copy + the journaling delta note.
- **On a student's read request** ("what's my paper coverage," "how many pages have I written") in any profile — the read/render.

It is never a rationale trigger or a model-escalation moment; purely mechanical, default tier.

## What it reads / writes

- **Reads:** `working_paper.md`, `section-scaffolds.yaml` (the template), the student's `paper_structure.md`. (Same expected-item reconciliation logic as `compile-working-paper` modes 1/3, read-only.)
- **Writes:** only a dated archival snapshot into `versions/` (a copy of the current `working_paper.md`). It **never** writes `working_paper.md`, `project_paper_status.md`, or `decisions.md`.

## The status view (rendered for a chat window)

Plain Markdown that reads in any chat window: per-section written / partly-written / open (in `paper_structure.md` order), a progress count ("X of N items written"), and a "≈ N of 25 pages" reading — facts only, never a judgment on the writing, never length-policing (register X3). Identical in shape to `compile-working-paper`'s status view (this is that render, factored out).

## What this skill does NOT do

- Ingest the Google-Docs round-trip, or regenerate / reconcile-write `working_paper.md` (that is `compile-working-paper`, mentor-only).
- Re-surface a dropped scaffold marker or restore a heading (reconcile-writes — also `compile-working-paper`).
- Compose, edit, or judge the student's prose (§8.2).
- Write `project_paper_status.md` (walkthrough-owned) or `decisions.md`.

## Where this skill lives in the architecture

A **shared read-only utility bundled into all three profiles** (like `check-budget` and `project-briefing`). It is the safe subset of the mentor's `compile-working-paper`: the read/render + the `versions/` snapshot, with the round-trip reconcile and the marker/heading restores deliberately left out and single-homed in the mentor. `project-briefing` consumes its rendered coverage; the Review Agent's weekly cron uses its archival snapshot for V6.

## Status

**DRAFT (2026-07-09).** Fixes S3 (the `project-briefing` → `compile-working-paper` cross-profile dependency) without giving research/review a second paper compiler. Pending: educator voice-read (no student-facing "moment" beyond the coverage render, which is inherited from `compile-working-paper`); ships with the next all-three republish. `compile-working-paper` remains the mentor-only full tool; an optional future DRY refactor could have it call `paper-coverage` for its read/render slice.
