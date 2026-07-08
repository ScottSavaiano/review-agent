---
name: check-budget
description: Pull the student's current OpenRouter sub-key usage and remaining budget via the /api/v1/key endpoint, and display a student-friendly summary that translates raw dollars into "roughly N more default-tier sessions or M more careful consultations" at the curriculum's typical per-session cost. Fires when the student asks how much budget they have used, how much remains, whether they can afford to use the careful tier, or any similar budget question. Also fires when invoked by another skill (the `redirect-off-topic` skill, in particular, points students here when budget visibility would help them choose). Runs a bundled Python script that makes the API call and formats the output.
---

# Check Budget

**Last edited:** 2026-06-29 (Cowork — **re-bundled into the research-agent profile** from the project-mentor copy; delivery-voice neutralized ("the mentor" → "the agent") so the same file reads right in any profile; "Where this skill lives" updated. **Canonical source = the project-mentor copy; sync any change across profiles.**) Prior: (pre-2026-05-26 baseline state — authored 2026-05-24, edit history before the attribution convention's adoption not retroactively reconstructed)
*Editing convention: see `00-handoff.md` → "Editing conventions" for editor identifiers and revision-marker rules.*

## What this skill is

This skill gives the student a clear, current picture of their OpenRouter sub-key budget — how much the educator has allocated to them, how much they have used (today, this week, this month), how much remains, and what the remaining amount translates to in practical curriculum terms (roughly how many more default-tier mentor sessions or careful-tier consultations they can run before hitting their limit).

The budget mechanism: the educator administers an OpenRouter organization account with per-student sub-keys, each carrying a spending limit the educator sets (and adjusts on request via the pre-approval process described in `decision-history-and-rationale.md` Section 11.4 and Section 13). The sub-key's limit and current usage are visible via OpenRouter's `/api/v1/key` endpoint when called with the student's own key as the Authorization bearer. This skill makes that call and presents the result in human terms.

## When this skill fires

The skill fires when the student asks about their budget. Concrete examples:

- Direct questions: "How much budget do I have left?" / "What's my usage?" / "Can I afford a careful-tier consultation?"
- Indirect cues during a budget-relevant moment: "I want to be careful with my spending — what's my balance?"
- Invocation from another skill: `redirect-off-topic` recommends a budget check when the student is considering whether to spend project budget on an off-topic tangent; `model-escalation` may invoke it when the student is weighing whether to upgrade for a high-judgment moment.

The skill also runs when the student types `/check-budget` directly in the TUI. Hermes supports slash-command-to-skill dispatch via the mechanism in `agent/skill_commands.py` and `agent/skill_bundles.py` of the Hermes source — bundles are checked first, then skills. The slash-command alias is registered by the skill's frontmatter `name:` field (`check-budget`), which becomes the `/check-budget` invocation automatically once the skill is bundled in the profile's `.bundled_manifest`. No additional registration plumbing is required.

## When this skill does NOT fire

- The student is asking about cost in the abstract ("how much does Opus cost per turn?") rather than their specific remaining budget. That is a question for the agent to answer from the SOUL's "When to use a stronger model" section or from general knowledge, not a budget-check.
- The student is asking about the *project's* budget overall rather than their own (e.g., "how much is the school spending on this?"). That is an educator-side question, not a student-side one; the agent declines to speak for the school's overall ledger.
- The student is mid-conversation on a research question and the skill would be a distraction. The mentor uses judgment — if a budget check would interrupt productive thinking, it can be deferred to a natural pause.

## What this skill does

When the skill fires, it runs the bundled `scripts/check_budget.py` script, which:

1. Reads the student's `OPENROUTER_API_KEY` from the profile's environment.
2. Sends `GET https://openrouter.ai/api/v1/key` with that key as the Authorization bearer, with a `User-Agent` header identifying the curriculum and an `HTTP-Referer` for OpenRouter's attribution surface.
3. Parses the response. OpenRouter returns the per-key information nested under a top-level `data:` object — the relevant fields are `data.limit`, `data.limit_remaining`, `data.usage`, `data.usage_daily`, `data.usage_weekly`, `data.usage_monthly`. The script handles the nesting; future maintainers writing parallel code should not assume top-level keys.
4. Computes the practical translations: `limit_remaining` ÷ typical-default-session-cost ≈ N more default-tier sessions; `limit_remaining` ÷ typical-careful-session-cost ≈ M more careful-tier consultations. The script prefers `limit_remaining` directly (which OpenRouter computes as the current-period remaining budget) over `limit - usage_total` (which would conflate the period-reset limit with the lifetime usage and silently undercount the student's remaining budget on a monthly-reset key).
5. Prints a formatted summary to the agent's tool output.

The mentor reads the tool output and delivers the summary to the student in its own voice — not by pasting the raw output, but by translating the numbers into language that matches the SOUL ("You have used $X.XX this month — most of it on the default tier — and you have $Y.YY remaining. At the rate you have been working, that is roughly N more default-tier sessions or M more careful-tier consultations").

## What the typical-cost translations rest on

The translations are heuristics, not promises. The skill uses curriculum-verified per-session cost estimates from `decision-history-and-rationale.md` Section 11.1:

- **Default tier (Haiku 4.5, cached effective):** ~$0.047 per 10-turn mentor session with the curriculum's typical ~10K-token system prompt + workspace context.
- **Careful tier (Opus 4.8, cached effective):** ~$0.23 per 10-turn high-judgment consultation.

These are session-shape averages, not exact predictions. The per-session estimate assumes the curriculum's typical session shape (about 10 turns, ~10K-token system prompt + workspace, ~500-token completions per turn). A student who routinely runs short consultations (3-4 turns) will see their actual cost-per-session run substantially below the estimate, and "N more sessions" will undercount their real remaining headroom. A student running long deep-work sessions (20+ turns) will burn through budget faster than the estimate predicts. The summary's mentor-voice framing makes the heuristic nature clear ("roughly," "at the rate you have been working"); the script does NOT yet personalize the estimate per-student based on their actual usage_daily ÷ daily-session-count. A future revision could pull that personalization in — for now, the unpersonalized estimate is the trade-off for keeping the skill simple. If the educator's `monitor-curriculum-models` skill (Tier 8) detects pricing changes for the curriculum's three models, the typical-cost values in this skill's script are updated in the same release.

## The output register

The mentor's voice in delivering the budget summary should match the SOUL — direct, specific, not alarmist or congratulatory.

**Plenty remaining:**

> "You have used $3.40 of your $40 budget this month — most of it on the default tier. That leaves you $36.60, which is roughly 750 more default-tier sessions or 160 more careful-tier consultations at the rate you have been working. You have room."

**Approaching the limit:**

> "You have used $32 of your $40 budget this month. You have $8 left, which is roughly 170 default-tier sessions or 35 careful-tier consultations at the rate you have been working. We are at about 80% spent — worth thinking about which kinds of conversations are most valuable to keep using budget on. If you need more, that is a conversation with your research teacher."

**Over the limit (rare; the educator's pre-approval gate normally catches this before it happens):**

> "You are out of budget for the month — you have used $40 of $40. The next call would fail. To continue, you need to talk with your research teacher about additional budget."

The mentor's tone is honest and useful — not moralizing about spending, not congratulating on frugality, not catastrophizing about running low.

## Edge cases the script handles

- **No `limit` set on the sub-key** (`limit: null` in the API response). The script reports total usage without a remaining-budget translation, with a note that no spending cap is configured on this key.
- **`limit` is set but `limit_remaining` is missing** from the API response. This can happen if the OpenRouter API shape shifts or if the per-key budget is mid-update. The script refuses to compute remaining budget from `limit - usage_total` (which would silently undercount, since `usage_total` is the lifetime figure and `limit` may reset monthly) and instead reports the total budget plus an explicit "cannot compute remaining reliably — ask the educator to confirm" message. The student gets honest uncertainty, not a wrong number.
- **`OPENROUTER_API_KEY` missing or invalid.** The script returns a clear error the agent can pass through: "I cannot check your budget — your OPENROUTER_API_KEY is not set or is not valid. Contact the educator who administers your AI account about getting your key configured."
- **API call fails or times out.** The script returns "OpenRouter's budget API is not responding right now — try again in a few minutes."
- **API response is malformed.** The script returns the raw response with a note that it could not parse it, so the educator can investigate.

## Where this skill lives in the architecture

This is the **research-agent profile's copy** of `check-budget`, re-bundled from the project-mentor profile (2026-06-29) — same script, same behavior, bundled here so budget questions work regardless of which agent the student is in. Bundled status makes it student-unmodifiable, curator-protected, and refreshed by profile updates (`hermes-platform-primer.md` §7). The script lives at `skills/check-budget/scripts/check_budget.py`. **Canonical source = the project-mentor copy; sync any change across all profiles.**

The **research-agent profile now ships this copy** (2026-06-29); the review-agent profile will ship the same when it is built — the same script and SKILL.md in each profile so it is available regardless of which agent the student is talking to.

## Status

**Draft, awaiting educator review.** The typical-cost values for the practical translations should be confirmed by the educator (current numbers come from the 2026-05-24 voice-test session and the Section 11.1 cost estimates; they may want revision after the first semester of real usage data). The script implementation and the slash-command registration are pending; this SKILL.md sets the contract.
