---
name: diagnose
description: Find the cause of a bug and pin it with a failing test, then hand it to /build or leave it as a ticket. Use when the user reports something broken, failing, throwing or slow ("por qué falla", "está roto", a stack trace), or when /dev routes a bug here.
---

# diagnose

Read `~/.agents/skills/diagnosing-bugs/SKILL.md` and follow it, with the changes below. Where they disagree, these win. Reply to the user in the language they wrote in.

- **Phases 1-4** as written.
- **Phase 5 stops at red.** Turn the minimised repro into the regression test at the correct seam and watch it fail. The fix belongs to `/build`, which owns the green. When no correct seam exists, that is the finding: record it and go on without the test.
- **Phase 6**: remove the `[DEBUG-…]` instrumentation and throwaway harnesses; the regression test stays, uncommitted.

## Hand-over

Show the user, in one message:

- The cause: the confirmed hypothesis, with `file:line`.
- The regression test (or the missing seam).
- The fix you propose, in 1-3 lines.

Then ask: fix it now, or leave it as a ticket?

- **Now**: invoke `build`, handing over the cause, the proposed fix and the red test as its intent. `/build` writes the mini-spec and creates the ticket after its checkpoint.
- **Later**: invoke `create-ticket` with the cause in Oportunidad, the proposed fix in Solución and the regression test as the first acceptance criterion; it starts **later** (`to-do`). Mention that the red test stays uncommitted in the working tree.
