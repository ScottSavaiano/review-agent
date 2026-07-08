#!/usr/bin/env python3
"""Check the student's OpenRouter sub-key budget.

Reads OPENROUTER_API_KEY from the environment, calls
GET https://openrouter.ai/api/v1/key, parses the per-key budget data,
and prints a formatted summary that the mentor can read aloud.

Per-call cost translations rest on the curriculum's verified
session-cost estimates from decision-history-and-rationale.md Section 11.1:
  - Default tier (Haiku 4.5, cached effective): ~$0.047 per 10-turn session
  - Careful tier (Opus 4.8, cached effective):  ~$0.232 per 10-turn consultation
If pricing changes (detected by the teacher-admin monitor-curriculum-models
skill), update these constants in the same release.

Exit codes:
  0 = success (output is the formatted summary)
  1 = missing or invalid API key
  2 = API unreachable / timed out
  3 = unexpected response shape
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_TIER_PER_SESSION = 0.047   # Haiku 4.5 cached effective, ~10-turn
CAREFUL_TIER_PER_SESSION = 0.232   # Opus 4.8 cached effective, ~10-turn

ENDPOINT = "https://openrouter.ai/api/v1/key"
USER_AGENT = "hermes-research-curriculum/0.2.0 (check-budget)"
HTTP_REFERER = "https://github.com/ScottSavaiano/project-mentor"


def _fetch_key_info(api_key: str) -> dict:
    req = urllib.request.Request(
        ENDPOINT,
        headers={
            "Authorization": f"Bearer {api_key}",
            "User-Agent": USER_AGENT,
            "HTTP-Referer": HTTP_REFERER,
            "X-Title": "Hermes Research Curriculum - Budget Check",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        return json.loads(response.read())


def _format_summary(data: dict) -> str:
    usage_total = float(data.get("usage") or 0)
    usage_daily = float(data.get("usage_daily") or 0)
    usage_weekly = float(data.get("usage_weekly") or 0)
    usage_monthly = float(data.get("usage_monthly") or 0)
    limit = data.get("limit")
    limit_remaining = data.get("limit_remaining")

    lines = []
    lines.append("Budget summary (from OpenRouter /api/v1/key):")
    lines.append("")
    lines.append(f"  Used today:       ${usage_daily:.4f}")
    lines.append(f"  Used this week:   ${usage_weekly:.4f}")
    lines.append(f"  Used this month:  ${usage_monthly:.4f}")
    lines.append(f"  Used (lifetime):  ${usage_total:.4f}")
    lines.append("")

    if limit is None:
        lines.append("  Spending limit:   NOT SET on this key.")
        lines.append("  (No per-key cap configured. Talk to the educator who")
        lines.append("   administers your AI account if you expect a limit to")
        lines.append("   be in place.)")
        return "\n".join(lines)

    limit_f = float(limit)
    # Prefer limit_remaining directly — OpenRouter computes this as the
    # current-period remaining budget, which on a monthly-reset key is what
    # the student actually has. limit_f - usage_total would conflate the
    # period-reset limit with the lifetime usage and undercount remaining
    # budget. If limit_remaining is not present, report uncertainty rather
    # than computing a potentially-wrong delta.
    if limit_remaining is None:
        lines.append(f"  Total budget:     ${limit_f:.2f}")
        lines.append("  Remaining:        (limit_remaining not present in API response;")
        lines.append("                    cannot compute remaining budget reliably from")
        lines.append("                    lifetime usage alone. Ask the educator to confirm.)")
        return "\n".join(lines)

    remaining_f = max(float(limit_remaining), 0.0)
    pct_used = (1.0 - (remaining_f / limit_f)) * 100 if limit_f > 0 else 100.0

    lines.append(f"  Total budget:     ${limit_f:.2f}")
    lines.append(f"  Remaining:        ${remaining_f:.4f}  ({pct_used:.1f}% used)")
    lines.append("")

    default_sessions = int(remaining_f / DEFAULT_TIER_PER_SESSION) if remaining_f > 0 else 0
    careful_consults = int(remaining_f / CAREFUL_TIER_PER_SESSION) if remaining_f > 0 else 0

    lines.append("At curriculum-typical use rates, your remaining budget is:")
    lines.append(f"  ~{default_sessions:,} more default-tier (Haiku 4.5) mentor sessions, OR")
    lines.append(f"  ~{careful_consults:,} more careful-tier (Opus 4.8) consultations,")
    lines.append("  in any mix.")
    lines.append("")
    lines.append("(Sessions vary in length and depth; treat the numbers as rough guidance,")
    lines.append(" not exact remaining counts.)")

    if pct_used >= 90:
        lines.append("")
        lines.append("NOTE: You are at 90%+ of your budget. If you need more, talk with")
        lines.append("your research teacher about additional allocation.")
    elif pct_used >= 75:
        lines.append("")
        lines.append("NOTE: You are at 75%+ of your budget. Worth being intentional about")
        lines.append("which conversations are most valuable to keep using budget on.")

    return "\n".join(lines)


def main() -> int:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print(
            "ERROR: OPENROUTER_API_KEY is not set in the environment.\n"
            "The mentor cannot check your budget without it. Contact the\n"
            "educator who administers your AI account about getting your\n"
            "key configured.",
            file=sys.stderr,
        )
        return 1

    try:
        data = _fetch_key_info(api_key)
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            print(
                f"ERROR: OpenRouter rejected the key (HTTP {e.code}).\n"
                "Your OPENROUTER_API_KEY may be invalid or expired. Contact\n"
                "the educator who administers your AI account about reissuing it.",
                file=sys.stderr,
            )
            return 1
        print(
            f"ERROR: OpenRouter's budget API returned HTTP {e.code}.\n"
            "Try again in a few minutes; if it keeps failing, let the\n"
            "educator who administers your AI account know.",
            file=sys.stderr,
        )
        return 2
    except Exception as e:
        print(
            f"ERROR: Could not reach OpenRouter's budget API ({type(e).__name__}: {e}).\n"
            "Try again in a few minutes; if it keeps failing, let the\n"
            "educator who administers your AI account know.",
            file=sys.stderr,
        )
        return 2

    payload = data.get("data")
    if not isinstance(payload, dict):
        print(
            "ERROR: OpenRouter returned an unexpected response shape.\n"
            f"Raw response: {json.dumps(data)[:400]}",
            file=sys.stderr,
        )
        return 3

    print(_format_summary(payload))
    return 0


if __name__ == "__main__":
    sys.exit(main())
