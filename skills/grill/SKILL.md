---
name: grill
description: Interview the user to close a design, asking only the decisions that are really theirs, a few per round with options, assuming the rest out loud, and recording terms and decisions in the glossary and ADRs. Use when a plan, initiative or idea needs its decisions settled ("grill me", "ayúdame a cerrar el diseño", "vamos a darle una vuelta"), and as the interview inside /design.
---

# grill

Read `~/.agents/skills/grill-with-docs/SKILL.md` and follow it, with the changes below. Where they disagree with it or with the skills it calls, these win.

## Rounds

Split each round's frontier in two:

- **Assumed**: a decision with a clear recommended answer that is cheap to reverse. List these first, one line each, under a heading meaning "Assumed unless you say otherwise", in the user's language. Silence accepts them.
- **Open**: a trade-off, a business rule, or a decision that is expensive to reverse. Ask at most **3** per round with `AskUserQuestion`: 2-4 options each, your recommendation first and marked, one line of context per question so it stands on its own. The rest of the open frontier waits for the next round.

Open each round with one line, in the user's language: `Round <n> · <decided> decided · ~<open> open`.

Keep the context to what the decision needs: a `file:line` or a fact earns its place only when it changes the answer.

## Close

The interview is done when the frontier is empty. Show the decisions, one line each, and ask the user to confirm the design is closed: that confirmation is the checkpoint that lets the tickets be published without asking again.
