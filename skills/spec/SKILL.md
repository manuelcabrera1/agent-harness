---
name: spec
description: Turn a closed design in the conversation into an epic ticket whose body is the spec, without interviewing. Use when a design session has settled its decisions and the work is an initiative needing several tickets, or when the user asks for a spec ("escribe la spec", "súbelo como épica").
---

# spec

Read `~/.agents/skills/to-spec/SKILL.md` and follow it, with the changes below. Where they disagree, these win.

The **harness config** is the `.config/` directory two levels above this skill's real directory (resolve the base directory with `realpath`, then `../..`).

- **Tracker**: it is described in the harness config's `tracker.md`; read that file in place of running `/setup-matt-pocock-skills`.
- **Seams (step 2)**: record them in the testing-decisions section and move on. The concrete tests are approved later, at `/build`'s checkpoint, before any code exists.
- **Template (step 3)**: write the config's **Epic body**, in the config's language, in place of the `spec-template`; its sections carry the `spec-template` ones under the team's headings. Title per the config.
- **Publish (step 3)**: **create** the epic with no further confirmation: the design session already approved its decisions. The triage role becomes whatever the config maps it to.

Done when the epic exists. Reply with the epic as a link named by its title and its id, and keep the id the tracker needs for parents in context: `tickets` hangs the subtasks from it.
