---
name: session-close-summary
description: A SHARED skill bundled into all three agents (project-mentor, research-agent, review-agent). At the end of a work session — on the session-end event, or when the student signals they're wrapping up ("I'm done for today," "that's it for now") — the agent presents a short, plain summary of what IT logged or changed in the workspace THIS session: files written or edited, decisions.md entries, log entries (reviews/, the data/analysis/validity logs, journals/), bibliography changes, and any skills it invoked or created. The student can add anything to the record, correct something, or just ignore it and close out. It is a transparency RECEIPT so the student always knows what the agent did in their name — NOT a reflection (that's update-journal's weekly workflow) and NOT graded. The agent never composes the student's prose and never grades. Obligation V3b (program-wide, educator 2026-07-08). Status — DRAFT (Phase B; first draft 2026-07-08).
---

# Session-Close Summary (shared — the "here's what I logged" receipt)

**Last edited:** 2026-07-08 (Cowork — first draft. Authored against cross-agent-obligations **V3b** (the program-wide per-session close-out summary, educator 2026-07-08) and `design/review-agent-build-scope-2026-07-08.md` (Phase B, B3). Distinct from `update-journal` (the weekly reflection, V1) and from V3a (the per-session *reflection*, which is NOT adopted).)
*Editing convention: see `00-handoff.md` → "Editing conventions" for editor identifiers and revision-marker rules.*

## What this skill is

A **transparency receipt at the end of a session.** Before the student signs off, whichever agent they were working with tells them, plainly, **what it logged or changed in the workspace this session** — so the student always knows what was done in their name and can correct it. It is bundled into **all three agents** and behaves the same in each; each agent reports **its own** session's changes.

It is deliberately **not** a reflection. The reflective, STS-evidence, four-part weekly work belongs to `update-journal` (the Review Agent's weekly workflow). This is a short factual close-out — a receipt — that runs at the end of *any* session with *any* agent. A standing per-session *reflection* prompt was considered and **not adopted** (V3a); this receipt is the thing that was.

## When it fires

- **On session end** — the session-end event/hook (Hermes session event hooks, v0.16.0+), so the summary appears as the session wraps.
- **On the student's signal** — "I'm done," "that's it for today," "closing up" — the agent runs the summary then.

It fires **once**, at the close. It does not interrupt mid-work.

## What it reports

The agent reconstructs **what it did this session** from two sources and states it concisely:
- its **own in-session actions** — the files it wrote or edited, the skills it invoked or created, the handoffs it initiated;
- a **`git` diff of the workspace since the session started** — so nothing is missed: new/changed `decisions.md` entries, log entries (`reviews/` plan-reviews and QC-audits, the Dataset Creation / Data Analysis / Data Validity logs), `journals/` entries, `working_paper.md` changes, `working_bibliography.md` changes (new ✗ entries, entries verified ✓), `application-evidence.md` appends.

The summary is a **short list**, in plain language — "here's what changed" — not a narrative and not a re-summary of the whole project. If **nothing** was written to the workspace this session, it says so plainly (a conversation-only session is fine).

## What the student can do

Three options, always offered, never forced:
- **Add something to the record** — a note the agent should append to `decisions.md` or the relevant log (the agent writes the *factual record entry* the student dictates; it does not compose reflective prose or paper prose).
- **Correct something** — if the summary is wrong or a change shouldn't have happened, the student says so and the agent fixes the record.
- **Ignore it and close out** — the default; the student can simply end the session.

## The register — the student-facing moments

Plain, brief, factual — a receipt, not a ceremony. Register samples (not scripts), pending educator voice-read:

**The close-out (things were logged):**
> "Before you sign off — here's what I logged this session: added your core-analysis plan-review to `reviews/`, logged two decisions in `decisions.md`, and marked one new citation unverified in your bibliography. Anything you want to add to the record or fix? Otherwise you're good to close out."

**Nothing was written:**
> "Quick note before you go — we talked things through but I didn't write anything to your workspace this session, so there's nothing new logged. Close out whenever."

**Student adds to the record:**
> "Got it — I'll add that to `decisions.md` as a dated note. Anything else, or are you set?"

**Student corrects something:**
> "Thanks — you're right, that shouldn't have gone in. Removing it now. Fixed."

## What this skill does NOT do

- **Run a reflection.** No weekly workflow, no STS prompts, no "what did you learn" — that's `update-journal`. This is a factual receipt only.
- **Compose the student's prose.** It writes only the *factual record entries* the student dictates (a decision, a note); never reflective or paper prose (§8.2).
- **Grade, or say whether anything is graded.** Grading is the teacher's, via Classroom.
- **Re-summarize the whole project or read status.** Just *this session's* changes. (Project status is `project-briefing` at session open and the weekly status read in `update-journal`.)
- **Write `project_paper_status.md`** — unchanged single-writer rule; a discrepancy is surfaced, not written.

## Where this skill lives in the architecture

Ships as a **bundled skill in all three profiles** (project-mentor, research-agent, review-agent), like `check-budget` and `maintain-bibliography` — student-unmodifiable, curator-protected. Each agent runs it for its own session. Pairs with `project-briefing` (the session-*open* orientation) as the session-*close* bookend. **Binds the three SOULs** with a light "before I sign off, here's what I logged" close — a one-line SOUL nod is pending (voice-read + shipped on each profile's next publish); the skill itself carries the behavior.

## Status

**DRAFT (Phase B, B3), first draft 2026-07-08.** Discharges the program-wide session-close receipt (V3b). Bundled into all three profiles. Pending: educator voice-read of the register moments; the one-line SOUL nod in each profile; confirmation of the session-end hook wiring; then it ships with each profile (review-agent at its first publish; project-mentor and research-agent at their next republish).
