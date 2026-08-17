---
name: project-briefing
description: The student's orientation layer — the whole-project, cross-agent "where am I, what happened, what's next" briefing. Runs automatically at session open (on_session_start) and on demand ("catch me up," "where are we," "what should I do next"). Reads the shared workspace files (project_paper_status.md, decisions.md, the journals/, and recent workspace file changes) and composes paper-coverage's coverage view into a short two-part brief: recent activity (last ~3 days / 3 sessions, across all three agents) and a recommended next step (a concrete, position-derived recommendation for where to start — navigational, not a substantive research recommendation). Bundled into all three student-facing profiles; tilts toward the agent the student is in while sharing one status core. It is the shared status engine the Review Agent's weekly journal opens with. Writes only its own dated briefings/ log — never project_paper_status.md, never the student's prose; makes no decisions and judges nothing. Status — draft, awaiting teacher-admin critique and educator review.
---

# Project Briefing

**Last edited:** 2026-07-08 (Cowork — **re-bundled into the review-agent profile** (Phase B5; the skill was designed cross-agent / bundled into all three profiles; this is the review copy). **Review-seat tilt confirmed (open item 3):** foregrounds the **journal state** (last reflection date, missed weeks), the **open parking-lot items** (`journals/parking-lot.md`), and **outstanding review obligations** (any `reviews/` plan-review or QC-audit the student still owes a spot-check on), and recommends the next **review/journal action**, atop the shared status core. It is the on-ramp `update-journal` opens with for its status core. **Canonical source = the project-mentor copy; shared core synced across profiles.**) Prior: 2026-06-29 (Cowork — re-bundled into the research-agent profile; research-seat tilt confirmed). Prior: 2026-06-10 (Cowork — first draft, authored against the 2026-06-10 design conversation: the whole-project/cross-agent scope; per-seat tilt with a shared core (err comprehensive for now); recent = last ~3 days / 3 sessions; "what's next" carries the walkthrough dependency; the standalone dated `briefings/` update log; the composition chain compile-working-paper → project-briefing → the Review Agent's weekly journal opening)
*Editing convention: see `00-handoff.md` → "Editing conventions" for editor identifiers and revision-marker rules. This skill also carries a Status section at the bottom recording the draft-vs-promoted lifecycle.*

## What this skill is

`project-briefing` is the student's **orientation layer.** Where `compile-working-paper` answers "what's the state of my paper," `project-briefing` answers the bigger question a student has when they sit down after time away: *"where am I in this whole project, what happened since I was last here, and what do I do next?"*

It is the **first skill that deliberately reads across all three agents.** It can, because the **shared workspace files are the only channel the three profiles share** (platform primer §7) — so a brief assembled from those files reflects the project mentor's, the research agent's, and the Review Agent's work alike, no matter which agent the student opened. *(Caveat, see open item 8: file changes are not agent-attributed — Drive sync records that a file changed, not which agent changed it — so reading out cross-agent activity as "the research agent did X" is best-effort inference from which files moved; absent per-agent attribution it is a plain file-change summary.)*

Its character sits between the kinds of skills already built: **not mechanical** like `compile-working-paper` (it composes a short readable narrative), and **not Socratic / evaluative** like the stage-skills (it makes no decision, asks no five-question gate, and **judges none of the work — not the science, not the writing**). It does one navigational thing the others don't: it **recommends where to start next** — a *position-derived* pointer (which step to pick up), never an evaluation and never a *substantive* research recommendation (which gap, which method — those stay the student's, developed Socratically by the stage-skills). It is **light, read-only synthesis that orients, recommends a starting point, and points forward.** It is the **shared status engine** the Review Agent's weekly journal opens with (see "The composition chain").

## When this skill fires

- **Automatically at session open** — the `on_session_start` hook (platform primer §7). The student opens any of their agents and is met with the brief, so they re-ground before working.
- **On demand** — when the student asks in their own words: *"catch me up," "where are we," "what's the status of the whole project," "what should I do next."*
- **As the Review Agent's journal on-ramp** — the weekly journaling session opens by invoking this skill for the status core, then layers reflection on top (it does not rebuild the status view).

It is **not** a rationale trigger and **not** a model-escalation moment — it reads state and summarizes; it makes no high-judgment evaluative call (the same deliberate negative as `compile-working-paper`). Default tier.

## What it reads

From the shared workspace (read-only):

- **`project_paper_status.md`** — the live position tracker (current cycle, regime, within-cycle stage, seal status, per-section state, stale verdict, reference-article status). The project activation sequence of "where you are."
- **`decisions.md`** — recent five-question decisions (what major choices were made lately).
- **The `journals/` directory** — the Review Agent's weekly reflections; surfaces "last reflection was [date], N open items, you missed last week" (it *reads* the journal; it never does the journal's reflective work).
- **Recent workspace file changes** — the concrete record of what *files* changed recently and when (file mtimes/content since the last briefing; the basis for the "recent activity" window); reading those changes back as *agent-attributed activity* ("the research agent staged 3 articles") is best-effort inference (open item 8), and degrades gracefully to a plain file-change summary.
- **`project_design.md`** — the project's shape (research problem, current method-approach, research questions, gaps) for framing.
- **`paper-coverage`** — *called* for the paper-coverage slice (what's written / open, page count), which it folds into the brief rather than recomputing.

## The two halves of the brief

**1. Recent activity — "since you were last here."** What happened across all three agents in the recent window: *"you wrote the gap section; the research agent staged 3 articles; last Friday's journal flagged a question about your identification strategy."* Built mainly from **recent workspace file changes** plus recent `decisions.md` and `journals/` entries.

**The recent window: the last ~3 days or last 3 sessions, whichever is determinable.** **File-change timestamps** give a reliable cross-agent *date* window (last 3 days); a *session* count is per-profile (Hermes sessions are per-profile state) and approximate cross-agent, so it is a best-effort secondary anchor. The exact computation — and the "last seen" marker that anchors "since you were last here" — is pinned at implementation (open item 2); the anchor is naturally the **timestamp of the last `briefings/` entry** (below).

**2. The recommended next step — not an open "what do you want to do?" but a concrete recommendation for where to start.** *"I'd start by selecting your paper-structure articles."* The student values a recommendation even without a rationale, so the brief **leads with one**. It is derived from the position in `project_paper_status.md` and the dependency order: a **blocker first** where the status file shows one (a stale-rewrite gate, an unmet precondition — with a brief reason, since that reason is obvious and useful), otherwise the **next step in the cycle template**. It stays a **recommendation, not a mandate** — the student can pick up something else; the brief just gives them a default rather than a blank menu. The recommendation is **navigational** (which step to work on), never substantive (which research choice to make). It **surfaces a position-derived recommendation; it does not compute authoritative dispatch** — that logic, and the dependency map / stale gate it leans on, are the walkthroughs' (`project-walkthrough` / `paper-walkthrough`, authored last) — so the recommendation is best-effort from the status file now and its authoritative derivation is **finalized alongside the walkthroughs** (open item 1).

## Per-seat tilt (a shared core)

The brief is **bundled into all three student-facing profiles** and reads the same shared files everywhere, so its **core is identical** wherever the student opens it (where you are, what changed, what's next). On top of the core it **tilts toward the agent's seat** — both in what it foregrounds *and* in what it recommends: the **project mentor** foregrounds project/paper position and recommends the next foundational/paper step; the **research agent** foregrounds data/execution state and recommends the next execution step; the **Review Agent** foregrounds the journal, open items, and review obligations and recommends the next review/journal action. **Err comprehensive for now** (more rather than less — we trim once we see what reads as noise). The exact per-seat emphasis for the research and review agents is finalized at each agent's build (open item 3).

## The standalone update log (`briefings/`)

`project-briefing` keeps **its own dated update log**, and writes **nothing else** — in particular it **never writes `project_paper_status.md`** (the walkthroughs own it) or `decisions.md`. Each run drops a **timestamped briefing snapshot** into a **`briefings/` directory** (dated files, the same pattern as the paper's `versions/`). This buys three things at once:

- **The "since you were last here" anchor** — the timestamp of the last `briefings/` entry marks the start of the recent window.
- **A browsable project diary** — the student can scroll back through dated briefs to see how the project moved over weeks.
- **A single-writer surface the briefing owns** — no contention with the walkthrough-owned status file. *(Contract §4.6 grants `project-briefing` the **sole writer** of `briefings/` — the 2026-06-10 contract pass, on the `versions/`/`proposals/` precedent — so this is a contract-grounded single-writer fact.)*

It is also another **authentic-process artifact** for the STS trail (a dated record of the project's progress in the student's own workspace). `briefings/` joins `articles/`, `journals/`, `proposals/`, and `versions/` as a workspace document directory, not a state file.

## The composition chain

One clean chain, each layer leaning on the one below and adding only its own value:

**`paper-coverage`** (read-only mechanical coverage) **→ `project-briefing`** (whole-project, cross-agent orientation + the dated log) **→ the Review Agent's weekly journal** (opens with a briefing for the status core, then adds the reflective layer — completed/to-do tracking, where-you-left-off continuity, missed-session summaries, open items, and the targeted writing prompts that generate the student's Regeneron-essay material; V1 / V1a / V1a-ext).

So the status view is **built once** (here) and reused — the journal never rebuilds it; it reflects on top of it.

## The boundary with the weekly journal

- **`project-briefing`** = the **quick, anytime, orienting glance.** No reflection expected; available whenever the student opens an agent or asks. It *mentions* the journal ("your last reflection raised X; you haven't journaled in two weeks") but never does its work.
- **The weekly journal** (Review Agent, `journals/`) = the **deep, weekly, pedagogical reflection** the student writes — their evidence bank for the STS contribution essays (V1a) and the place the essay-material prompts live (V1a-ext). The journal *opens with* this briefing and then adds everything only it does.

The line: the briefing **presents** status; the journal **reflects** on it and **generates essay material**. Shared core, different wrapper.

## The scripted moments

Per the established convention: adapt wording to the student's project; preserve the parts and their order; concise, plain, oriented forward — never judging the work. Student-natural vocabulary (*status / done / next / since you were last here*).

### Moment 1 — The session-open brief

> *"Welcome back. Since you were last here ([date]): [recent activity — what you and your agents did]. You're at [position] — **I'd start by [recommended next step]**[, since [brief reason, only if it's a blocker]]. Want to dive into that, or pick up something else?"*

### Moment 2 — On-demand catch-up ("where are we")

> *"Here's the whole picture: [where you are in the project + cycle]. Recently: [recent activity]. Still open: [open items]. [If relevant: your last reflection was [date]; you have N open items.] **My recommendation: start with [recommended next step].** Or tell me where you'd rather dig in."*

## What this skill writes to the workspace

`briefings/` only — a dated briefing snapshot per run. It **never** writes `project_paper_status.md` (walkthrough-owned; this skill *reads* position, never sets it), **never** writes `decisions.md` (not a rationale trigger), and **never** touches the student's prose or the paper. Return payload per contract §5.1: `completion_status`; `workspace_writes` (the `briefings/` entry); `newly_stale_sections`, `decisions_appended` empty; `seal_state_change` / `new_cycle_decision` / `writing_handoff` all `null`. `advisory_notes` per §5.1 is the skill→dispatching-walkthrough note channel only — **not an inter-skill carrier** (clarified 2026-06-10). **The recommended next step is a *student-facing* element of the rendered brief — not a typed return field.** A caller that consumes this skill's output (the Review Agent's weekly journal, as its status on-ramp) reads the **rendered brief / the `briefings/` workspace file**, not a typed payload — so the position recommendation stays non-actionable narrative, honoring the §5.1 bar on position-recommendation fields.

## Edge cases

**First session / empty project.** No recent activity and no prior `briefings/` entry — the brief introduces the project's starting point and the first step; it does not invent history.

**A long absence.** The recent window is bounded (~3 days / 3 sessions), so after a long gap the brief summarizes the window and points to the `briefings/` diary and the last journal for the fuller gap rather than dumping everything.

**No journal yet (before the Review Agent is in use, or early in the year).** The journal-derived lines are simply omitted; the brief stands on the status file, recent file changes, and `decisions.md`.

**"What's next" before the walkthroughs exist.** It reports the current position from `project_paper_status.md` and a best-effort one-step look-ahead, explicitly the informational read, not an authoritative dispatch (open item 1).

**The student asks it to do real work** (write, decide, reflect deeply). It orients and points them to the right agent/skill — it briefs, it does not do the stage-skills', the paper-skills', or the journal's work.

## Where this skill lives in the architecture

A **cross-agent supporting skill**, authored in the project-mentor build and **bundled into all three student-facing profiles** — the **research-agent copy built 2026-06-29** and the **review-agent copy built 2026-07-08 (Phase B5)** — now bundled into all three; a distribution obligation per spec §12. It reads the shared workspace files and recent file changes, **calls `paper-coverage`** for the paper slice, and writes only its own dated `briefings/` log. It is invoked automatically at `on_session_start`, on demand, and by the Review Agent's weekly journal as its status on-ramp. **Not** a rationale trigger and **not** a model-escalation moment.

## Status

**Draft, authored 2026-06-10 (Cowork)** against the 2026-06-10 design conversation and the architecture (spec §10 the status file, §11 the workspace files, §12 the inventory entry; contract §5.1 the return payload; platform primer §7 the `on_session_start` hook and cross-agent shared-file channel; decision-history §8.2 the no-judgment line; cross-agent-obligations V1/V1a/V1a-ext the journal it feeds).

**Teacher-admin critique passed 2026-06-10** (one blocking — a contract-grounding gap, not a skill-logic hole; five substantive; two minor; nine verified-clean). The recommendation design, the journal boundary, the V1a-ext fence, and both deliberate negatives all verified clean. Dispositions applied: **F2.1/F5.2** (blocking) — `briefings/` lacks a §4.6 writer grant; recorded as open item 7, bound for the contract pass (batched with `versions/`); the "single-writer" claim softened to "intended design, not yet contract-grounded." **F1.1** — the git "records what every agent did" overclaim softened; the agent-attributed-commit-convention dependency named (open item 8). **F3.2** — the recommendation clarified as a student-facing rendered-brief element; `advisory_notes` non-actionable narrative only (honoring the §5.1 position-recommendation bar). **S1** — spec §12 updated to the recommendation framing (drift resolved). **F1.2 + S4** — the `advisory_notes` inter-skill-carrier question + the compile→briefing consumption shape recorded as open item 9 for the contract pass. **F2.2 / F6.1** — open items 2 / 1 sharpened. Educator voice-read: both Moments approved. **Committed.** **Contract/spec pass ran 2026-06-10:** the `briefings/` §4.6 grant landed and the `advisory_notes` inter-skill-carrier question was resolved (it is *not* a carrier) — so this skill's body (the §5.1 return note + the L56 single-writer line) and open items 7/9 are reconciled to the landed canon.

### Open authoring items

**Convention** (per dispatch contract §11): items remain numbered while open; resolved items are retained with strikethrough, their original wording preserved, and a resolution date.

1. **The recommended next step finalizes with the walkthroughs.** The brief now **leads with a recommendation** for where to start (educator, 2026-06-10), derived from the status-file position + dependency order (blocker-first, else next cycle-template step). The authoritative position/dispatch logic — and the dependency map / stale gate the blocker-first rule leans on — is `project-walkthrough` / `paper-walkthrough`'s (authored last). This skill makes a best-effort recommendation from the status file now; pin the precise derivation (and whether the walkthroughs hand the brief an explicit "recommended next" field) at walkthrough authoring. (Educator-approved to build now with this dependency.) **The dependency is plural (F6.1):** the per-seat recommendation on the research and review agents leans on *those agents'* own position logic, not only the mentor walkthroughs — so it is finalized at *each* agent's build. *(Spec §12's entry was updated to the recommendation framing 2026-06-10, resolving the S1 draft-vs-spec drift.)*
2. **The recent-window computation + the "last seen" anchor.** "Last ~3 days or 3 sessions, whichever is determinable": the git-history date window is cross-agent-reliable; a session count is per-profile/approximate. Pin the exact rule and the last-seen anchor (the last `briefings/` timestamp is the natural choice) at implementation. **Note (F2.2):** because the brief writes a `briefings/` entry every run (including each `on_session_start`), that anchor tracks *briefing runs*, not *student presence* — "since you were last here" is an approximation of the prior briefing run. Confirm that's the intended semantics when pinning the rule.
3. **Per-seat tilt specifics.** The shared core is fixed; the research-agent and review-agent emphasis (what each foregrounds) is finalized at each agent's build. Err comprehensive for now.
4. **The `briefings/` log mechanics.** Dated-file naming, snapshot dedup (skip an identical-to-prior brief, or always stamp one per session), retention (kept for the project year), and adding `briefings/` to the spec §11 workspace-directory list. Pin at implementation / the spec pass.
5. **The journal-composition contract.** Exactly what the Review Agent's weekly journal consumes from this skill as its on-ramp (the rendered brief? the `advisory_notes` shape?). Pin when the Review Agent / journaling skill is built (V1 / V1a / V1a-ext), alongside the essay-material-prompt design.
6. ~~**Moment wording.** Both Moments await the educator's voice read, per precedent.~~ **Resolved 2026-06-10** (educator voice-read): both Moments approved as written (the recommendation-leading form).
7. ~~**`briefings/` needs a §4.6 writer grant (F2.1, blocking-on-grounding) — bound for the contract pass.**~~ **Resolved 2026-06-10 (contract pass):** contract §4.6 now grants `project-briefing` the **sole writer of `briefings/`** (line ~198, on the `versions/`/`proposals/` precedent). The single-writer property is contract-grounded.
8. **Cross-agent activity read is a file-change summary, not agent-attributed (F1.1; revised 2026-07-19 for the Drive-based workspace).** The session-open briefing reconstructs "what happened since last time" from **workspace file changes** (which files were written/changed, which stages advanced, new `decisions.md`/`reviews/`/`journals/` entries) — it does **not** attribute changes to a specific agent. The earlier design contemplated reading *agent-attributed git commits* ("the research agent staged 3 articles"), but under the Drive Mirror workspace (2026-07-09) there is no git history to mine and Drive sync does not tag a change with the agent that made it. So the activity read is a **file-state delta** (mtime/content since the last briefing snapshot), which is sufficient for orientation. *(The former "pin an agent-attributed commit convention" forward-constraint is retired with git.)*
9. ~~**`advisory_notes` as an inter-skill carrier + the compile→briefing consumption shape (S4 + F1.2) — bound for the contract pass.**~~ **Resolved 2026-06-10 (contract pass):** §5.1 clarified that `advisory_notes` is **not** an inter-skill carrier; inter-skill composition (compile→briefing→journal) flows through the **shared workspace files + the rendered conversation output**, never the typed payload. So there is no `advisory_notes` carrier shape to define; the compile→briefing and briefing→journal handoffs read the rendered output / workspace. The empirical detail of each read is settled at the consuming skill's implementation.
