---
name: design
description: Close the design of an initiative and leave it in the tracker as tickets ready to build. Use when the user brings an initiative, a feature request or a plan to shape ("nos llega una iniciativa", "se quiere plantear", "producto pide"), or when /dev routes a design here.
---

# design

From an idea to tickets in the tracker. This session ends there: building starts in a new session from a ticket. Reply to the user in the language they wrote in.

## 1. Context

Read whatever the prompt brings (a Slack thread, a doc, a ticket) and explore the code it touches. Facts are your job: dispatch subagents for broad sweeps rather than asking the user.

## 2. Method

- **Default**: invoke `grilling` and `domain-modeling`, so terms and hard-to-reverse decisions land in the glossary and ADRs as the interview goes.
- **A question only running code can answer** (a state model, a UI to see): propose `prototype` for that question, then come back to the interview.
- **Reading legwork** (external docs, APIs): run `research` in the background and keep grilling the questions that do not depend on it.
- **Too big for one session** (greenfield, the way there not yet visible): propose `wayfinder` and hand over to it; it ends at `spec` too.

Done when the user confirms the design is closed.

## 3. Publish

- **Several tickets or several sessions of work**: invoke `spec`, then `tickets` on the epic it creates.
- **One ticket**: invoke `create-ticket`; it starts **later**.

No extra confirmation before writing: the closing checkpoint approved the content.

## 4. Report

The tickets as links named by their titles, with their ids, and the one to start with: the first ticket with no blockers. The next session opens with `/build <id>`.
