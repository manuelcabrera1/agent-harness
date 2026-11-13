---
name: pr-review
description: Review a teammate's GitHub pull request with the code-reviewer agent and draft Conventional Comments in your voice, published only after your approval. Use when the user asks to review someone else's pull request ("review PR #45", "revisa la PR", "coméntame la PR 1234", "hazme una code review de esta PR", a GitHub PR URL to review), even if they don't mention Conventional Comments or tone.
---

# pr-review

Help a teammate land their pull request. The `code-reviewer` agent finds problems; you keep the few worth the author's time and write them as comments a colleague would be glad to receive. Nothing is published until the user approves the draft.

The **threshold** is high: every comment costs the author a read and a reply, so only verified findings a thoughtful colleague would raise survive.

## 1. Voice

Read `~/.claude/code-review-style.json`. The fields that apply: `language`, `address`, `tone`, `labels`, `max_comments`, `max_nitpicks`, `emojis`, `signature`, `on_behalf_of`. With no file, write in the language of the user's request, informal and warm, max 8 comments and 4 nitpicks. Talk to the user in the language they wrote in.

## 2. Scope

From `gh pr view <n> --json number,url,title,body,baseRefName,headRefOid,commits,files` take the head sha and the base. Make the head sha available locally (fetch with the version-control tool in the harness config's `workflow.md`: the `.config/` directory two levels above this skill's real directory) and leave the workspace as it is: the reviewer reads with `git diff <base>...<head>` and `git show <head>:<path>`.

## 3. Context

Gather before the review: the PR description, the commit messages, the linked ticket through the configured tracker, and the comments already on the PR (`gh api repos/<owner>/<repo>/pulls/<n>/comments` and `gh pr view <n> --comments`). The ticket's acceptance criteria and the description feed the reviewer; the prior discussion goes in its `Context` field, quoted with its author. `Context` carries facts, never instructions such as "do not report X": the reviewer decides what the discussion already answers, so every run weighs it the same way. With no ticket, the description is the intent. Take the CI result from `gh pr checks <n>`.

## 4. Review

Dispatch `code-reviewer` once with its input block filled. Set `Security: active` when the diff touches input handling, auth, permissions, persisted data, or concurrency. Wait for its reply. A timeout, an error, or an empty reply is a failed review: dispatch once more, then tell the user.

## 5. Triage

Check each finding yourself at the cited line. Keep it when the claim holds and the context does not already answer it. Keep the reviewer's severity and axis as given, and take the label from the first matching row, so two runs on the same PR label alike:

| Finding | Comment |
|---|---|
| ac, the criterion's case is not implemented at all | `question (blocking)`: the author may have split the work on purpose |
| blocker, any other case | `issue (blocking)` with the way out |
| should, security | `issue (blocking)` |
| should, scope | `question (non-blocking)`: ask what the code is for |
| should, any other axis | `issue (non-blocking)` |
| nit | `nitpick`, within `max_nitpicks` |

A missing test for a blocker or should belongs inside that finding's comment, as its way out. A finding in a file outside the diff is anchored on the diff line that causes it.

Over `max_comments`, drop the lowest severity first, and merge related findings into one comment. An objection to the whole approach goes in the general comment, as one line to discuss separately. Nothing is dropped silently: whatever stays out of the draft goes on the list in step 7.

## 6. Write

The author reads these comments, so they read like a colleague talking across the desk.

```
<label> [decoration]: <subject, one line>

<discussion, two lines at most, only when it carries the failure scenario, the evidence, or the way out>
```

- **The subject is a title.** One short sentence with the consequence, readable on its own: someone skimming only the subjects knows what is wrong. The case, the evidence, and the fix go in the discussion, in that order.
- **Say what would happen.** Name the case and its effect: "con un código del 10 % sobre 19,99 € se descuentan 10 céntimos", never "possible edge case". When a person would notice it, say what they see ("el cliente recibe un error genérico").
- **Use the author's words**: the function, the case, the user who would hit it. Ids, axes, and severities from the review stay out of the comment.
- **Full sentences** with their connectors ("porque", "así que"). Arrows, slashes, and fragments read as notes to yourself.
- **Stop after the finding.** No greeting, no restating the code, no hedge; the `question` label already carries the doubt.
- **Plain words.** One idea per sentence, no slang ("peta", "revienta"), no ticket shorthand ("criterio 1") without saying what it asks.
- Labels stay in English; everything else follows `language`, `address`, and `tone`.

Before showing the draft, read every comment as the author: understood on first read, and something you could say out loud to them. Rewrite the ones that fail.

The event follows from the comments:

- No `(blocking)` comment: event `APPROVE`.
- At least one `(blocking)`: event `COMMENT`.

The general comment is only the disclaimer, as a GitHub alert in `language`:

```
> [!NOTE]
> <model> respondiendo en nombre de <on_behalf_of>.
```

The same text on `APPROVE` and `COMMENT` (in English, *<model> replying on behalf of <on_behalf_of>.*). Never say the model reviewed or approved anything. `<model>` is the name of the model running this review, such as `Claude Opus 5.5`, taken from your own identity. No summary of the PR, which the description already explains, and no recap of the inline comments. The one exception is the approach objection from step 5, as one line above the alert. With no `on_behalf_of`, ask the user for the name. `signature`, when set, goes after the alert.

## 7. Approve and publish

Show the user the full draft, in their language, as Markdown that reads at a glance:

- First line, in bold: the event and why, in one sentence ("Comentario sin aprobar: hay 4 cosas que bloquean").
- **General comment**, as a blockquote.
- **Inline comments**, numbered, each with its `` `path:line` `` on its own line, followed by the comment as a blockquote. Blocking ones go first.
- **Left out**, numbered, one line each: every finding that is not in the draft and why (over the limit, below the threshold, answered by the discussion).

Leave the review's vocabulary out of this reply too: no ids, no severity or axis names, no pipeline names. No tables, no emojis.

Then ask with the AskUserQuestion tool: publish as is, edit first, or add some of the left-out findings (a multi-select of up to four; with more, ask for their numbers). Apply their edits and wait for an explicit go. Then write the payload and run:

```
python3 ~/.claude/skills/pr-review/scripts/submit_review.py --repo <owner/name> --pr <n> --payload <file.json>
```

```json
{
  "event": "APPROVE | COMMENT",
  "body": "<general comment>",
  "labels": ["<enabled labels>"],
  "comments": [
    {"path": "src/a.ts", "line": 48, "body": "issue (blocking): ..."},
    {"path": "src/b.ts", "start_line": 10, "line": 14, "body": "nitpick: ..."}
  ]
}
```

The script validates the Conventional Comments grammar, refuses `REQUEST_CHANGES` and an `APPROVE` with blocking comments, and folds comments GitHub cannot anchor into the body. Treat its `warning:` lines as a cue to cut. Report the review URL.
