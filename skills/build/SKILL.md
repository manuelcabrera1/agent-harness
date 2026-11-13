---
name: build
description: Take a ticket or a concrete change all the way to an open draft PR - approved tests, TDD without committing, review-loop, single-purpose commits, PR, tracker. Use when the user asks to implement a ticket end to end ("/build ABC-123", "implementa este ticket", "llévalo hasta la PR"), or when /dev or /diagnose hand over a change.
---

# build

From a ticket or a prompt to an open draft PR. The user stops you at two **checkpoints**; everything between them runs on its own. Reply to the user in the language they wrote in.

The **harness config** is the `.config/` directory two levels above this skill's real directory (resolve the base directory with `realpath`, then `../..`): `tracker.md` for tickets, `workflow.md` for ids, branches and version control.

## 1. Intent

- **With a ticket**: **read** it. Its solution, acceptance criteria and out of scope (when present) are the intent.
- **Without one**: write a **mini-spec** from the prompt or the diagnosis that handed over: intent in 1-2 sentences, numbered acceptance criteria, out of scope.

Explore the code the change touches until you can name the **seams**: the public interfaces the tests will drive. Prefer existing seams and the highest one available.

## 2. Checkpoint 1: acceptance criteria and tests

Show, in one message:

- The acceptance criteria and the out of scope.
- The tests, numbered. Each one: its `it('…')` description, one line of given / when / then, its seam, and the criterion it covers (`AC2`). Coming from /diagnose, test 1 is the reproducing test, already written and red.
- The **decisions** already taken that the tests do not show: how a value object reaches a response, the shape of a contract field, how each test seeds its data. One line each, with the alternative discarded. They go in this list, where the user approves them with the tests, even when an insight block also mentions them.

Ask the user to approve, remove (by number) or add. This is the moment the tests are judged before any implementation exists, so each one carries enough detail to be judged on its own. Without a ticket, this checkpoint also approves the ticket's content.

Done when the user approves a list.

## 3. Ticket

- Without a ticket: invoke `create-ticket` with the approved mini-spec and tests; it **starts now**.
- With a ticket: **start** it unless it is already in progress.

Keep the ticket id: the branch and the PR carry it.

## 4. Implement

Invoke `tdd` and follow its loop, with these changes:

- The seams and tests approved at checkpoint 1 are the pre-agreed seams: no further confirmation.
- One approved test per cycle, red then green.
- **Leave everything uncommitted.** `commit-split` writes the history at the end.

Run typecheck and the single test file as you go. A test that proves unnecessary, or a missing one, changes the list: note it for the final report rather than asking.

## 5. Verify

Run the full tests, lint and typecheck of every workspace the change touches. Done when they pass, or when a failure is shown to predate the change.

## 6. Review

Invoke `review-loop`, passing the intent, the acceptance criteria and the out of scope from step 1.

## 7. Checkpoint 2: decisions

Only when `review-loop` returns items under **Needs decision**: show them, one line each with the options and its recommendation, and wait. Apply the answers, then verify again (step 5). With nothing to decide, go straight on.

## 8. Publish

1. Invoke `commit-split`, on the branch named after the ticket.
2. Push the branch as `workflow.md` says, then invoke `create-pr` with the ticket id, asking for an unattended draft. Invoking `/build` is the user's request to push and open that draft.
3. Invoke `tracker-sync`.

## 9. Report

- The PR as a link, and the ticket as a link named by its title.
- The commits, oldest first.
- Tests that changed against checkpoint 1: added, removed, and why.
- The review's follow-ups.
