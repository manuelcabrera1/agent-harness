#!/usr/bin/env python3
"""Submit a Conventional Comments code review to a GitHub PR via `gh`, never requesting changes.

Payload (JSON file, or `-` for stdin):

    {
      "event": "APPROVE",              // or "COMMENT". REQUEST_CHANGES is rejected.
      "body": "general comment",       // the verdict
      "commit_id": "<sha>",            // optional; resolved from the PR head if absent
      "labels": ["question", ...],     // optional; the enabled labels (defaults below)
      "fallback_heading": "...",       // optional; heading used if inline anchoring fails
      "comments": [
        {"path": "src/a.ts", "line": 48, "side": "RIGHT",
         "body": "question (blocking): ...\\n\\ndiscussion..."},
        {"path": "src/b.ts", "start_line": 10, "line": 14, "body": "nitpick: ..."}
      ]
    }

Every comment body must match the Conventional Comments grammar
(https://conventionalcomments.org/):

    <label> [decorations]: <subject>

    [discussion]

Two invariants are enforced here rather than left to the caller, because both are
silent failures otherwise:

  * REQUEST_CHANGES is refused outright. A review made with less context than the
    author has should not hard-block a PR; use COMMENT and say what does not add up.
  * APPROVE is refused while any comment is (blocking). Approving a change you just
    said must not be accepted until resolved is incoherent, and the author has no way
    to tell which half you meant.

Length is checked too, but only warned about: one line of subject, two of discussion,
a verdict of two or three lines. A long review is one nobody reads, and the padding
is invisible to whoever wrote it.

GitHub itself rejects a review when a comment points outside the diff, and rejects
APPROVE on your own PR. Either would throw the whole review away, so both degrade:
self-approval falls back to a plain comment, un-anchorable comments get folded into
the body with their file:line intact.

Usage:
    python3 submit_review.py --repo owner/name --pr 123 --payload review.json
    python3 submit_review.py --repo owner/name --pr 123 --payload - --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter

DEFAULT_LABELS = [
    "question", "suggestion", "issue",
    "nitpick", "todo", "thought", "note", "chore",
]
SPEC_LABELS = DEFAULT_LABELS + ["praise", "typo", "polish", "quibble"]
DECORATIONS = {"blocking", "non-blocking", "if-minor"}
# Labels the spec defines as non-blocking by nature. Only checked under their
# canonical English names -- a team that aliases them opts out of the check.
NEVER_BLOCKING = {"praise", "nitpick", "thought", "note", "quibble"}
DEFAULT_FALLBACK_HEADING = "Comments (could not be anchored to the diff lines)"

# Brevity limits, from SKILL.md: one line of subject, at most two of discussion,
# and a verdict of two or three lines. Warnings rather than errors -- a quoted rule
# or a permalink can push a comment over honestly. Counted on prose only, since a
# code fence is not padding.
MAX_SUBJECT_CHARS = 140
MAX_DISCUSSION_CHARS = 240
MAX_BODY_CHARS = 420
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)

# The spec renders labels in bold, and GitHub renders markdown, so `**question:**`
# and `question:` are both legitimate. Accept either.
COMMENT_RE = re.compile(
    r"^\**(?P<label>[^\s():*]+)\**"   # label, optionally bold
    r"(?:\s*\((?P<dec>[^)]*)\))?"     # optional (decorations)
    r"\**:\**\s*(?P<subject>\S.*)",   # ": " then a non-empty subject
    re.DOTALL,
)


def die(msg: str, code: int = 1) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def run_gh(args: list[str], stdin: str | None = None) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(["gh", *args], input=stdin, capture_output=True, text=True)
    except FileNotFoundError:
        die("`gh` not found on PATH. Install the GitHub CLI or submit the review manually.")
    return proc.returncode, proc.stdout, proc.stderr


def load_payload(path: str) -> dict:
    raw = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        die(f"payload is not valid JSON: {exc}")
    if not isinstance(payload, dict):
        die("payload must be a JSON object")
    return payload


def enabled_labels(payload: dict) -> list[str]:
    raw = payload.get("labels") or DEFAULT_LABELS
    labels = [str(x).strip().rstrip(":") for x in raw if str(x).strip()]
    return labels or DEFAULT_LABELS


def parse_comment(body: str) -> tuple[str, set[str], str] | None:
    m = COMMENT_RE.match(body.lstrip())
    if not m:
        return None
    raw_dec = m.group("dec") or ""
    decorations = {d.strip().lower() for d in raw_dec.split(",") if d.strip()}
    return m.group("label"), decorations, m.group("subject")


def validate(payload: dict) -> list[str]:
    """Validate the payload. Returns the labels of blocking comments, if any."""
    event = (payload.get("event") or "").upper()
    if event == "REQUEST_CHANGES":
        die(
            "this skill never submits REQUEST_CHANGES.\n"
            "  A review made with less context than the author has should not hard-block a PR.\n"
            "  Use event=COMMENT and say in the body what does not add up (verdict tier C).\n"
            "  If a blocking review is genuinely wanted, the user can run "
            "`gh pr review --request-changes` themselves.",
            code=2,
        )
    if event not in ("APPROVE", "COMMENT"):
        die(f"event must be APPROVE or COMMENT, got {payload.get('event')!r}")
    if not (payload.get("body") or "").strip():
        die("body is required: every review states its verdict explicitly")

    labels = enabled_labels(payload)
    blocking: list[str] = []

    for i, c in enumerate(payload.get("comments") or []):
        where = f"comments[{i}]"
        if not isinstance(c, dict):
            die(f"{where} must be an object")
        if not c.get("path"):
            die(f"{where} is missing 'path'")
        if not (c.get("body") or "").strip():
            die(f"{where} is missing 'body'")
        if not isinstance(c.get("line"), int):
            die(f"{where} needs an integer 'line' (the last line the comment covers)")

        parsed = parse_comment(c["body"])
        if not parsed:
            die(
                f"{where} does not match the Conventional Comments grammar "
                f"'<label> [decorations]: <subject>'.\n"
                f"  Got: {c['body'][:60]!r}\n"
                f"  Enabled labels: {', '.join(labels)}"
            )
        label, decorations, _ = parsed

        if label not in labels:
            hint = (
                f" It is a Conventional Comments label but not enabled — add it to 'labels' "
                f"in ~/.claude/code-review-style.json if the team uses it."
                if label in SPEC_LABELS else ""
            )
            die(f"{where} uses label {label!r}, which is not enabled.{hint}\n"
                f"  Enabled: {', '.join(labels)}")

        unknown = decorations - DECORATIONS
        if unknown:
            die(f"{where} has unknown decoration(s) {', '.join(sorted(unknown))}. "
                f"The spec defines: {', '.join(sorted(DECORATIONS))}")

        if "blocking" in decorations and "non-blocking" in decorations:
            die(f"{where} is marked both blocking and non-blocking")

        if "blocking" in decorations:
            if label in NEVER_BLOCKING:
                die(
                    f"{where} is {label!r} decorated (blocking), but {label!r} is non-blocking by "
                    f"nature.\n  If it really should hold up the merge it isn't a {label} — "
                    f"'question (blocking)' or 'issue (blocking)' is the honest label."
                )
            blocking.append(label)

    if blocking and event == "APPROVE":
        die(
            f"cannot APPROVE while {len(blocking)} comment(s) are marked (blocking): "
            f"{', '.join(blocking)}.\n"
            "  A blocking comment says the change should not be accepted until it is resolved.\n"
            "  Either use event=COMMENT (verdict tier C) or drop the (blocking) decorations."
        )
    return blocking


def prose_len(text: str) -> int:
    """Characters of prose: fenced code dropped, whitespace collapsed."""
    return len(" ".join(FENCE_RE.sub("", text).split()))


def length_warnings(payload: dict) -> list[str]:
    """Flag comments that drifted long. Not fatal, but brevity is the CRITICAL rule."""
    warnings: list[str] = []

    body_len = prose_len(payload.get("body") or "")
    if body_len > MAX_BODY_CHARS:
        warnings.append(
            f"the review body is {body_len} chars of prose (~{MAX_BODY_CHARS} is the ceiling). "
            "It states the verdict in 2-3 lines; it is not a recap of the inline comments."
        )

    for i, c in enumerate(payload.get("comments") or []):
        parsed = parse_comment(c.get("body") or "")
        if not parsed:
            continue
        _, _, rest = parsed
        subject, _, discussion = rest.partition("\n\n")
        where = f"comments[{i}] ({c.get('path')}:{c.get('line')})"
        if prose_len(subject) > MAX_SUBJECT_CHARS:
            warnings.append(
                f"{where} subject is {prose_len(subject)} chars — it should be one line, "
                "the finding without the run-up to it."
            )
        if prose_len(discussion) > MAX_DISCUSSION_CHARS:
            warnings.append(
                f"{where} discussion is {prose_len(discussion)} chars — two lines maximum, "
                "carrying only the failure scenario, the evidence, or the way out."
            )
    return warnings


def resolve_commit_id(repo: str, pr: int) -> str:
    code, out, err = run_gh(
        ["pr", "view", str(pr), "--repo", repo, "--json", "headRefOid", "-q", ".headRefOid"]
    )
    if code != 0:
        die(f"could not resolve the PR head SHA: {err.strip() or out.strip()}")
    sha = out.strip()
    if not sha:
        die("could not resolve the PR head SHA (empty response)")
    return sha


def api_body(payload: dict) -> dict:
    out = {
        "commit_id": payload["commit_id"],
        "body": payload["body"],
        "event": payload["event"].upper(),
    }
    comments = []
    for c in payload.get("comments") or []:
        entry = {
            "path": c["path"],
            "line": c["line"],
            "side": c.get("side", "RIGHT"),
            "body": c["body"],
        }
        if isinstance(c.get("start_line"), int) and c["start_line"] != c["line"]:
            entry["start_line"] = c["start_line"]
            entry["start_side"] = c.get("start_side", entry["side"])
        comments.append(entry)
    if comments:
        out["comments"] = comments
    return out


def fold_comments_into_body(payload: dict) -> dict:
    """Move inline comments into the body, keeping their file:line so nothing is lost."""
    comments = payload.get("comments") or []
    if not comments:
        return payload
    heading = payload.get("fallback_heading") or DEFAULT_FALLBACK_HEADING
    lines = [payload["body"].rstrip(), "", "---", "", heading, ""]
    for c in comments:
        text = "\n  ".join(c["body"].strip().splitlines())
        lines.append(f"- `{c['path']}:{c['line']}` — {text}")
    folded = dict(payload)
    folded["body"] = "\n".join(lines)
    folded["comments"] = []
    return folded


def label_breakdown(payload: dict) -> str:
    counts: Counter[str] = Counter()
    for c in payload.get("comments") or []:
        parsed = parse_comment(c["body"])
        if parsed:
            label, decorations, _ = parsed
            suffix = " (blocking)" if "blocking" in decorations else ""
            counts[f"{label}{suffix}"] += 1
    return ", ".join(f"{n}x {label}" for label, n in counts.most_common()) or "none"


def post(repo: str, pr: int, payload: dict) -> tuple[int, str, str]:
    return run_gh(
        ["api", "--method", "POST", f"/repos/{repo}/pulls/{pr}/reviews", "--input", "-"],
        stdin=json.dumps(api_body(payload)),
    )


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--repo", required=True, help="owner/name")
    ap.add_argument("--pr", required=True, type=int)
    ap.add_argument("--payload", required=True, help="path to the JSON payload, or - for stdin")
    ap.add_argument("--dry-run", action="store_true", help="print what would be sent and exit")
    args = ap.parse_args()

    payload = load_payload(args.payload)
    validate(payload)
    for w in length_warnings(payload):
        print(f"warning: {w}", file=sys.stderr)

    if args.dry_run:
        payload.setdefault("commit_id", "<resolved at submit time>")
        print(json.dumps(api_body(payload), indent=2, ensure_ascii=False))
        n = len(payload.get("comments") or [])
        print(f"\n[dry run] would POST to /repos/{args.repo}/pulls/{args.pr}/reviews")
        print(f"[dry run] event={payload['event'].upper()}, {n} inline comment(s)")
        print(f"[dry run] labels: {label_breakdown(payload)}")
        return

    if not payload.get("commit_id"):
        payload["commit_id"] = resolve_commit_id(args.repo, args.pr)

    attempts = ["as composed"]
    code, out, err = post(args.repo, args.pr, payload)
    combined = f"{out}\n{err}".lower()

    # Degradation ladder: keep the review, adjust only what GitHub refused.
    if code != 0 and payload["event"].upper() == "APPROVE" and "your own pull request" in combined:
        print("note: GitHub does not allow approving your own PR — submitting as a comment "
              "instead, verdict text unchanged.", file=sys.stderr)
        payload = dict(payload, event="COMMENT")
        attempts.append("event downgraded to COMMENT")
        code, out, err = post(args.repo, args.pr, payload)
        combined = f"{out}\n{err}".lower()

    if code != 0 and (payload.get("comments") or []):
        print("note: GitHub rejected the inline comments (likely a line outside the diff) — "
              "folding them into the review body so none are lost.", file=sys.stderr)
        payload = fold_comments_into_body(payload)
        attempts.append("comments folded into the body")
        code, out, err = post(args.repo, args.pr, payload)

    if code != 0:
        print(f"error: gh failed after {len(attempts)} attempt(s) ({', '.join(attempts)})",
              file=sys.stderr)
        print((err or out).strip(), file=sys.stderr)
        sys.exit(1)

    try:
        url = json.loads(out).get("html_url", "")
    except (json.JSONDecodeError, AttributeError):
        url = ""
    print(f"review submitted ({payload['event'].upper()}){f': {url}' if url else ''}")


if __name__ == "__main__":
    main()
