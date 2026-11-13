---
name: review-loop
description: Review your own just-finished implementation in a loop with the code-reviewer agent, apply the minimal corrections, and hand back only the decisions that need a human.
---

# review-loop

The step between implementing and opening the PR. The `code-reviewer` agent finds problems; you, the implementer, apply the **minimal corrections** and ask the user about the rest. Teammates review whatever reaches the PR.

Every round's review comes from a `code-reviewer` dispatch and its real reply. Your own reading of the code serves triage only. Reply to the user in the language they wrote in.

Two goals pull on every choice here. The same change should get the same outcome on every run, so triage follows the table below instead of judgement calls. And the diff should not grow beyond what the fixes need, so a correction that needs more than a few lines becomes a question for the user.

## Budget

- 3 rounds. Round 1 reviews the whole change; later rounds review changed code and open ids.
- 5 rounds when the change touches security, permissions, auth, data loss, or concurrency and a blocker or should stays open with evidence, or when the user asks.
- Stop early when a round returns only nits.

Keep a **ledger** across rounds: id, severity, axis, outcome (`fixed`, `decision`, `optional`, `disagree`).

## 1. Scope

Pin the change: the base sha, one diff command reused every round, and the paths it covers, untracked files included. Scope it to this session's changes as the harness config's `workflow.md` says (the `.config/` directory two levels above this skill's real directory), so other agents' work stays out. When the change does not separate cleanly from unrelated edits, ask.

Record the size baseline: `git diff --shortstat <base>` plus the line count of untracked files in scope.

## 2. Intent

Find the ticket: an id in the branch name or commit messages, read through the configured tracker. Its acceptance criteria and out-of-scope notes feed the reviewer. With no ticket, state the intent and out-of-scope in 1-2 sentences from this session's request. With neither, ask.

## 3. Checks

Run the tests, lint, and typecheck covering the change. Send the reviewer a change that passes them; report any check that is missing or was already failing.

## 4. Review

Dispatch `code-reviewer` with its input block filled. Set `Security: active` when the diff touches input handling, auth, permissions, persisted data, or concurrency. `Context` carries facts only, never instructions about what to report. Wait for its reply. A timeout, an error, or an empty reply is a failed round, never an approval: dispatch again with the ledger.

## 5. Triage

Check each finding at its cited `file:line`. The check decides only whether the claim holds; keep the reviewer's severity and axis as given, so two runs on the same change triage alike.

| Finding | Outcome |
|---|---|
| Claim does not hold | `disagree`, with evidence (file:line, test, output) |
| blocker or should, axis ac, bug, security, or standards, and the fix keeps every exported name, signature, type, and the behaviour the intent describes, in at most ~10 changed lines besides its test | `fixed`: apply it |
| blocker or should whose fix changes an export, a signature, a type, or intended behaviour, or needs more than ~10 lines | `decision` |
| scope | `decision`, recommending removal |
| nit, any axis | `optional` |

A fix is the smallest that closes the finding: delete or narrow before adding a helper, option, lock, cache, or layer. Add a test only for a fixed blocker: one focused case that fails without the fix, in the module's existing test file, reusing its fixtures.

Fixes land in the working tree; committing is the caller's call.

## 6. Re-check

Re-run the checks and measure the size as in step 1. When a fix grew the diff beyond what it needs, cut first. A fix that breaks a check is reverted and moves to `decision`.

## 7. Next round

Start one when budget remains and a fix changed behaviour code or a blocker or should is open that is not a `decision`. Send the same input plus the ledger. An id still disputed after two replies moves to `decision` with both sides.

The loop ends when `code-reviewer` returns APPROVE on the current diff, when only `decision` and `optional` items are open, or when the budget ends. A spent budget is reported as such, never as approval.

## 8. Report

Show the report, then ask (step 9). Write it in the user's language, as Markdown that reads at a glance:

- First line, in bold: the state in plain words (ready to open the PR, N things need your decision, or the round budget ran out with issues open).
- Second line: rounds, size before and after, test result.
- Then these sections, in this order, leaving out empty ones: **Fixed**, **Needs your decision**, **Optional improvements**, **Not applied** (disagreements).
- One line per item: `` `file:line` ``, then what would happen and what changed, in one plain sentence. Number the items in the last three sections so the user can refer to them.
- Security items go first in their section and start with the word for "security" in the user's language.
- Leave out reviewer vocabulary: no ids, no severity or axis names. No tables, no emojis.

Example (for a Spanish-speaking user):

```markdown
**Hay 2 cosas que necesito que decidas antes de abrir la PR.**
2 rondas · diff +74/-6 → +88/-7 · tests 8/8

**Arreglado**
- `src/discounts.ts:15` · Seguridad: el código del cliente iba pegado al SQL; ahora va como parámetro `$1`.
- `src/orders.ts:6` · `placeOrder` no esperaba a `computeTotal` y guardaba el total como `undefined`; ahora lo espera.

**Necesitas decidir**
1. `src/orders.ts:5` · Ningún pedido registra la redención (criterio 3). Arreglarlo cambia la firma de `placeOrder`.
2. `src/discounts.ts:11` · La caché no la pide el ticket, no caduca y crece con cada código inventado.

**Mejoras opcionales**
1. `src/discounts.ts:34` · `discountAmount` es un export por defecto y CONTRIBUTING.md solo admite exports con nombre.
```

## 9. Ask, apply, and close

When there are `decision` or `optional` items, ask the user with the AskUserQuestion tool right after the report:

- One question per decision, up to four per call. The options are the ways out, with your recommendation first and marked as recommended; each option says what it changes (signature, behaviour, lines).
- One multi-select question for the optional improvements, with up to four per question. With more than four, ask which numbers from the report to apply.

Apply what the user picks, following step 5's limits. An optional item that turns out bigger than its one-line fix goes back to the user. Then re-check (step 6) and run one last review round on the changed code, even when the budget is spent. Close with a short report in the same format, covering only what changed since the first one.

Without an interactive way to ask, the report from step 8 is the final answer.
