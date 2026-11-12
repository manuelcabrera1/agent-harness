---
name: tickets
description: Break an epic or spec into tracer-bullet subtasks with blocking edges and publish them under it. Use after `spec` creates an epic, or when the user asks to split work into tickets ("divide en tickets", "desglosa la épica").
---

# tickets

Read `~/.agents/skills/to-tickets/SKILL.md` and follow it, with the changes below. Where they disagree, these win.

The **harness config** is the `.config/` directory two levels above this skill's real directory (resolve the base directory with `realpath`, then `../..`).

- **Tracker**: it is described in the harness config's `tracker.md`; read that file in place of running `/setup-matt-pocock-skills`.
- **Source (step 1)**: the epic from this session, or the ticket id the user passes, read with **read**.
- **Quiz (step 4)**: this is the checkpoint that approves the tickets. Show the breakdown as a numbered list (title, blocked by, what it delivers) and ask the three questions in one message.
- **Publish (step 5)**: for each approved ticket, blockers first, **create child** under the epic with the config's **Ticket body**, in the config's language: `What to build` becomes the solution, the acceptance criteria keep their own section, and the context is one sentence pointing at the epic. Then **block** each ticket on its blockers. Create without further confirmation: step 4 approved them.

Done when every approved ticket exists under the epic with its blocking edges. Reply with one line per ticket: link named by its title, its id, and the ids that block it.
