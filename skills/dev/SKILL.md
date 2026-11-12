---
name: dev
description: Entry point. Read the prompt, pick the flow (design, diagnose, build, explore) and run it.
disable-model-invocation: true
---

# dev

Pick the flow from the prompt, announce it in one line, and invoke it with the prompt as its input. Reply in the language the user wrote in.

The **harness config** is the `.config/` directory two levels above this skill's real directory (resolve the base directory with `realpath`, then `../..`).

| Signal in the prompt | Flow |
|---|---|
| A ticket id (the pattern in the harness config's `workflow.md`), or a concrete change to make: «implementa», «añade», «haz que…» | `build` |
| Something broken: «por qué falla», «está roto», an error, a stack trace, a failing test | `diagnose` |
| An initiative or a plan to shape: «nos llega una iniciativa», «se quiere plantear», «producto pide» | `design` |
| A question to answer: «investiga cómo funciona», «dónde se…», «qué opinas de» | `explore` |

Announce, in the user's language: `→ <flow>: <why, in a few words>. Not that? Tell me.` and invoke it straight away; the user corrects you by answering.

When two flows fit equally, ask once with `AskUserQuestion`, the likelier flow first. A ticket id wins over everything else: a ticket that turns out to be a bug report still goes to `build`, whose checkpoint shows what it understood.
