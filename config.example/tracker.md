# Tracker

The single source of truth for where tickets live and what they look like. Skills ask for an **operation** (below); this file says how the tracker performs it. Swapping trackers means rewriting the Adapter section and nothing else.

Write every ticket title and body in <language>, whatever the source language.

## Adapter: <tracker>

Operate through <the tracker's MCP tools or CLI>.

|              |                                  |
| ------------ | -------------------------------- |
| Backlog      | <list / project / board and id>  |
| Other lists  | <lists a ticket is also added to, if any> |
| Tags         | <default tags>                   |
| Assignee     | <default assignee>               |

### Operations

Fill in how your tracker performs each one. Skills only ever name these.

| Operation | How |
|---|---|
| **create** | <create a ticket in the backlog, status for work to do later> |
| **create child** | <create a ticket under a parent> |
| **block** | <mark a ticket as blocked by another> |
| **start** | <move to in progress, add to the current sprint/iteration> |
| **read** | <read a ticket with its full body> |
| **comment** | <comment on a ticket> |
| **move** | <change status> |
| **list** | <list tickets, paginating to the end> |
| **search** | <free-text search> |

### Status lifecycle

| Moment | Status |
|---|---|
| Created from a design, to be done later | <to-do> |
| Work starts on it | **start** → <in progress> |

Triage roles used by mattpocock/skills (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`) map to: <statuses or labels>. When a skill says "publish to the issue tracker", that is **create**.

## Team convention

### Title

<prefix, verb form, length limit>

### Ticket body

Used for loose tickets and for the subtasks of an epic. It must carry acceptance criteria: `/build` consumes them.

```markdown
## <Problem / context>
## <Solution>
## <Acceptance criteria>
- [ ] <observable behaviour>
## <Related resources>
```

### Epic body

Used for the parent ticket of an initiative; the spec is this body. It carries the sections of mattpocock's `to-spec` template under your own headings.

```markdown
## <Problem>
## <Solution>
## <User stories>
## <Implementation decisions>
## <Testing decisions>
## <Out of scope>
## <Related resources>
```

### Writing rules

<length, tone, formatting>

## Source follow-up

When a ticket was created from a chat thread, the reply posted in that thread is exactly:

```
<message> → <ticket URL>
```
