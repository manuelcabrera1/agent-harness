---
name: commit-split
description: Turn this session's finished, uncommitted work into a history of small single-purpose commits, test before implementation, on the session's branch. Use when an implementation is done and reviewed and the working tree holds it ("parte esto en commits", "commitea lo que hemos hecho"), and as the step after review-loop in /build.
---

# commit-split

The implementation was written without committing; this skill writes the history. Each commit carries **one purpose** a reviewer can read on its own: the history tells the final design, never the path to it (no "address review", no "fix typo in previous commit").

The **harness config** is the `.config/` directory two levels above this skill's real directory (resolve the base directory with `realpath`, then `../..`). Its `workflow.md` says which version-control tool to use and how, the branch pattern, the commit conventions and the linters.

## 1. Scope

List the uncommitted changes as `workflow.md`'s **Session scope** says. Take only the files and hunks this session changed; when a change's ownership is unclear, ask.

The branch is the session's: the one it already uses, or one named after the ticket with the **Branches** pattern.

## 2. Lint

Run the linters from `workflow.md` in every workspace the change touches, so their edits land inside the commits rather than after them. List the changes again afterwards: ids may have changed.

## 3. Plan

Group the changes into **units**: one behaviour, one refactor, one config change. Order them so each builds on the ones before:

1. Prefactors, making the change easy.
2. Per behaviour: its tests, then the code that turns them green. The test commit always comes first: the history shows red before green.
3. Translations, tooling, dependencies, config.

Messages follow `workflow.md`'s **Commits**.

A hunk that mixes two units cannot always be split by the tool: isolate the lines of the first unit with a temporary edit, commit, then restore the rest.

Outside /build, show the plan (one line per commit: message and files) and wait for an OK. Inside /build, the review already approved the content: commit straight away.

## 4. Commit

Commit the units oldest first, each with only its own changes, as `workflow.md`'s **Commit** says.

Done when every change in scope is committed and nothing of the session is left uncommitted. Reply with the commits, oldest first, one line each.
