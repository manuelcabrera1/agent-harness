---
name: create-ticket
description: Create one ticket in the issue tracker from a need, a bug, a closed design or a chat thread, written to the team's template. Use when the user asks to create, register or track a task ("crea una tarea", "apúntalo en el backlog", a Slack thread URL to track), or when a flow (/build, /diagnose, /design) needs a ticket that does not exist yet.
---

# create-ticket

Turn a need into one ticket. Reply to the user in the language they wrote in.

The **harness config** is the `.config/` directory two levels above this skill's real directory (resolve the base directory with `realpath`, then `../..`). Read `tracker.md` there first: where tickets live, their statuses, the title and body templates. Every write goes through its operations (**create**, **create child**, **start**).

## Inputs

Any mix of: a chat thread URL, free text, the current conversation (a closed design, a diagnosis, a mini-spec), and overrides (extra tags, assignees, title, parent ticket, status).

A Slack URL is the primary source. Decode `/archives/<channel>/p<ts>` into the channel id and the ts with a `.` before its last 6 digits (`p1779089943164239` → `1779089943.164239`); for a reply permalink, take the `thread_ts` query param. Read the parent message and every reply with `slack_read_thread`.

A vague intent with nothing to frame a story from: ask for a thread or a short description of the problem.

## 1. Draft

Title and body follow the config's **Title**, **Ticket body** and **Writing rules**. When the conversation already holds acceptance criteria (a `/build` checkpoint, a diagnosis with its reproducing test), carry them over verbatim.

## 2. Decide the moment

- **Starts now**: the caller is `/build` or `/diagnose`, or the user says they are starting it.
- **Later**: everything else.

## 3. Confirm

When a flow checkpoint already approved this content, skip to step 4. Otherwise show the title, the full body, the destination (lists, parent, current sprint when it starts now), status, tags and assignees, and the thread permalink when there is one. Wait for an explicit OK or edits.

## 4. Create

**create** (or **create child** with a parent), then **start** when it starts now. Done when the ticket exists in every place its moment requires.

Reply with one line: the ticket as a link named by its title, its id, and where it landed.

## 5. Thread follow-up

Only when a chat thread was the source. Propose replying inside that thread (`thread_ts` = the parent ts) with the config's **Source follow-up** message, verbatim. Show the message and its thread, and send it only after a second, explicit OK: posting is a separate action from creating. After sending, add the permalink to your reply.
