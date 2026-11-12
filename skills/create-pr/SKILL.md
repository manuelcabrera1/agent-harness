---
name: create-pr
description: Create a GitHub pull request with a descriptive title derived from the branch's commits and a body composed from a configurable core template plus a fragment for the kind of change (feat, fix, refactor, perf, chore), linking the ticket in whichever issue tracker the user configured (ClickUp, Jira, Linear, GitHub Issues, or none). Use this skill whenever the user asks to "create a PR", "open a pull request", "abrir PR", "crear pull request", or invokes /create-pr — even if they don't specify the format explicitly. The skill reads its conventions from a preferences file and runs a short setup interview the first time, so also use it when the user wants to configure or change them: "set up create-pr", "change my PR template", "cambiar la plantilla de PR", "que no haga push".
---

# Create Pull Request

Create a GitHub pull request with `gh`: a title derived from the branch's commits and diff, and a body built from the configured template.

No team's workflow is baked in here. The tracker, the template, the voice and the habits all come from a preferences file — [preferences.md](preferences.md) has the resolution order, the setup interview and the full schema. This file is the craft: how to read the branch, what makes a good title, and what makes a body worth a reviewer's time.

## When to use

When the user asks to create or open a PR — `/create-pr ABC-123`, `crea una PR para ABC-123`, or a bare "create a PR". Also when they ask to set up or change any of the conventions, in which case run the interview and stop there.

This skill creates the PR and nothing else. It never commits, amends or force-pushes, whatever the preferences say.

### Unattended draft

When the invocation asks for an unattended draft, open the PR as a **draft** and skip the confirmation of step 6, whatever the preferences say: nobody is asked to review a draft, and the user reads it on GitHub before marking it ready. The caller pushes the branch first. Every other step runs as written.

## Workflow

### 1. Load configuration

Before anything else, read the preferences (global, then repo, repo keys winning) and the template they resolve to. If neither preferences file exists, run the setup interview from [preferences.md](preferences.md), write the file, then continue with the PR the user asked for. If a file exists but is malformed or partial, fill the gaps with schema defaults, say which ones you defaulted, and carry on.

Everything below reads settings by name — `tracker.required`, `push`, `detail` — and those names are defined in the schema.

### 2. Gather context

In parallel:

- `git status` — clean tree and branch name
- `git rev-parse --abbrev-ref HEAD` — current branch
- `git symbolic-ref refs/remotes/origin/HEAD` (or `git remote show origin | grep "HEAD branch"`) — the base branch, unless `base_branch` pins one
- `git log <base>..HEAD --pretty=format:"%h %s"` — the commits
- `git diff <base>...HEAD --stat` — the size
- `git diff <base>...HEAD` — the actual changes, so the Solution reflects what happened rather than what the commit subjects claim

If the branch has no upstream (`git rev-parse --abbrev-ref --symbolic-full-name @{u}` fails), follow `push`: stop and ask the user to push, offer to push, or push with `git push -u origin HEAD` and say so.

### 3. Resolve the ticket

Skip this entirely when `tracker.name` is `none`.

Otherwise take the id from the user's invocation, or look for one in the branch name using `tracker.id_pattern` — `feature/ABC-123-retry-webhooks` gives you `ABC-123`. A detected id is a suggestion, so confirm it rather than assuming. With no id and `tracker.required` true, ask before doing anything else and never invent one; with `required` false, drop the ticket line from the body and move on.

The URL comes from `tracker.url_template` with `{id}` substituted.

### 4. Compose the title

The title says what the PR achieves, in the words a teammate would use to tell someone else about it: short, plain, under `title.max_length`, and written in `title.language`. Describe the outcome rather than the mechanism, so `fix(auth): reject password reset tokens after first use` beats `fix(auth): add used flag check to ResetPassword`. Avoid filler verbs like "improve", "update", "handle" or "refactor some" unless they really are the change, and skip any lead-in like "this PR" or "changes to". If the reader still has to open the PR to learn what it does, rewrite the title.

Derive it from the commits and the diff — not from the ticket id, and not by copying one commit subject verbatim unless that subject already summarises the whole PR.

With `title.convention` set to `auto`, look at recent commits on the base branch and follow what you find; under conventional commits that means `type(scope): short description`, present tense, lowercase after the colon, no trailing period. Pick the scope the same way, from the surrounding history, or from `title.scope` when it says how scopes work here. Keep the ticket id out unless `title.include_ticket_id` is on.

### 5. Compose the body

The body is the core template plus the fragment for this kind of change, in that order. Decide the kind first, per `change_type`: normally the conventional-commit type of the title you just wrote (`feat`, `fix`, `refactor`, `perf`, `chore`), or the same vocabulary inferred from the diff when the repo doesn't use conventional commits. What the user says outright — "this is a refactor" — wins over both. One kind per PR: pick what dominates the diff instead of stacking fragments, so a feature that also carries a migration is a `feat` whose deploy order goes in the core's rollout section. [preferences.md](preferences.md) has the lookup order and how to add or override a fragment.

Then fill it in. Angle-bracket text is an instruction to you: replace it, and never leave one in a PR body. Substitute `{{TICKET_URL}}` and `{{TICKET_ID}}`, dropping the whole line when there's no ticket. Strip HTML comments; keep any checkbox list and tick what genuinely applies. Translate the headings into `language` along with the prose you write under them, so a Spanish body carries `## Solución` rather than a Spanish paragraph sitting under `## Solution`.

**A section you can't fill honestly gets deleted, heading included.** Never leave a heading with nothing under it, never write "N/A" or "nothing", and never invent content to fill one — a section like that costs the reviewer a read and returns nothing. On a small PR most fragment sections legitimately disappear and the body collapses back to Problem and Solution; that's the template working as intended, not a gap you need to cover.

Problem and Solution are where the writing happens, whatever fragment follows them. Both go straight to the point: open with the fact itself, not with "This PR…", "In order to…" or "The goal of this change is…", don't repeat what the title already said, and cut any sentence the reviewer wouldn't miss. When a sentence is about a specific place in the code, name the file (`src/auth/ResetPassword.ts`) or symbol in backticks instead of describing it at length; a precise reference is shorter than a paraphrase and lets the reviewer jump straight there.

**Problem** is a plain statement of the issue or need being addressed, one or two sentences. Don't smuggle the solution in here.

**Solution** describes what changed and, above all, *why*. The diff already shows the *what*; what saves the reviewer time is the reasoning the diff can't show. With `detail: proportional` — the default — scale it to the PR, leaning on the commits as a guide but writing a coherent summary rather than a commit-list dump:

- **Small, self-explanatory PR** (a fix or a tweak, one or two commits, small diff): one or two sentences, straight to the point. If the title and diff already make the intent obvious, don't restate them at length. Padding a small PR buries the signal.
- **Medium PR**: a short list of the meaningful changes, each with a clause of rationale where it isn't obvious.
- **Large PR (~500+ lines), especially features and refactors**: walk through each meaningful change and justify it. For a refactor, say what moved and why the new shape is better; for a feature, cover the main pieces and the decisions behind them — trade-offs weighed, alternatives rejected, follow-ups left. Treat this as required: at this size the reviewer can't reconstruct the intent from the diff, and a bare change list forces them to reverse-engineer your reasoning. The justification *is* the deliverable.

Length is proportional both ways. A one-line fix gets a one-line solution; a 500-line refactor gets a real walkthrough, but even there each point is a sentence or two of substance, not a paragraph of context. `detail: minimal` collapses this to a couple of sentences regardless of size, and `thorough` walks through the changes even on small PRs.

**Alert blocks are the exception, not part of the template.** The default body carries no alerts at all, and that's the right outcome for most PRs, large ones included. The prose already tells the normal story; an alert is a flare that hijacks attention, so it only pays off when missing it would cause harm. With `alerts: sparing`, apply this test before adding one: *if the reviewer skipped this line, would something real go wrong?* If not, the point belongs in the Solution prose or nowhere. When one earns its place, match the type to the stakes — `> [!WARNING]` / `> [!CAUTION]` for something that can break, regress or bite later (breaking change, risky migration, data-loss risk); `> [!IMPORTANT]` for a constraint the reviewer must understand to work with the change correctly. `> [!NOTE]` and `> [!TIP]` are almost always decoration; write those as prose.

Write the body in `language`, regardless of the language of the conversation, the commits or the ticket — translate the source material instead of mirroring it. Follow `tone` for wording, and `extra_instructions` for anything the schema doesn't cover. Add the attribution footer only if `attribution_footer` is on, and a test-plan section only if the template has one or the user asks.

### 6. Show the draft and confirm

With `confirm_before_create` on, show the proposed title and body and wait for confirmation or edits. A PR is visible to the team the moment it exists and can't be quietly unsent, so don't skip this because the user asked for autonomy earlier in the session.

### 7. Create the PR

Use a HEREDOC so the body renders correctly:

```bash
gh pr create --title "the title" --body "$(cat <<'EOF'
## Problem

...

## Solution

...
EOF
)"
```

Add `--base <branch>` when the detected base isn't right, `--assignee <assignee>` unless it's `none`, `--draft` per `draft`, and `--reviewer` / `--label` for each configured entry. Return the PR URL when it's created.

## Examples

Both use the shipped core and fragments, on a repo that follows conventional commits.

### Small PR (single fix)

Commits: `fix(auth): mark reset token as used in ResetPassword`

Title: `fix(auth): reject password reset tokens after first use`

The `fix` fragment brings Root cause, Regression guard and an optional Reproduction. The root cause is what the diff can't show, the test is worth naming, and the reproduction is obvious once the cause is stated — so that last one goes, and so does the core's rollout section:

```markdown
## Problem

Resolves https://tracker.example.com/t/ABC-123

`ResetPassword` accepted the same reset token more than once, so a link that leaked from an inbox stayed usable after the password had already been changed.

## Solution

`ResetPassword` (`src/auth/ResetPassword.ts`) now consumes the token in the same transaction as the password update and fails when it has already been used.

## Root cause

The token was only checked for expiry, and nothing marked it spent — a second request inside the validity window looked identical to the first.

## Regression guard

`ResetPasswordTest::rejects_a_token_that_was_already_used` fails without this change.
```

### Larger PR (several commits and an architectural decision)

A big, multi-part PR is still just Problem and Solution — size alone doesn't call for an alert block.

Title: `feat(notifications): send all transactional email through one swappable sender`

```markdown
## Problem

Resolves https://tracker.example.com/t/ABC-456

Each use case that sends email built its own payload and called the provider SDK directly, so the same retry and templating logic was duplicated three times and the domain could not be tested without network access.

## Solution

- Introduce an `EmailSender` port in the notifications domain with a provider-backed adapter in infrastructure, so the domain depends on the port instead of the SDK.
- Route the sign-up, reset-password and invitation flows through the port, dropping the retry logic duplicated across all three.
- Move the inline SDK calls behind the adapter and update the container wiring, which leaves the domain free of provider imports and lets the tests use an in-memory sender.

## What it does now

Nothing changes for the user: the three flows send the same emails they sent before, now through a single sender that can be swapped per environment.

## Out of scope

Marketing email still goes through the old path — ABC-461 moves it once this lands.
```

### When an alert actually earns its place

Only when skipping it would cause real trouble — here, a breaking change reviewers must act on before merging:

```markdown
## Solution

Rename the `owner_id` column on `documents` to `account_id` and update all readers.

> [!WARNING]
> Requires the `2026_06_rename_owner_id` migration to run before deploy. Deploying the code without the migration breaks the document list endpoint.
```

## What not to do

- Don't invent a ticket id. If you don't have one and the tracker requires it, ask.
- Don't push, force-push, commit or amend beyond what `push` allows.
- Don't hardcode a tracker URL, a ticket prefix, a template heading or a scope convention into this skill. Those belong in the preferences file, which is the whole point of it.
- Don't pad a small PR — and don't under-document a large one. A 500+-line feature or refactor that lists changes without justifying them is incomplete.
- Don't dump raw `git log` output as the Solution. Summarise.
- Don't write a title that describes the mechanism or hides behind a vague verb; say what the PR achieves.
- Don't open Problem or Solution with a preamble or restate the title in them. Lead with the fact.
- Don't reach for an alert block by reflex; size or "architectural-ness" doesn't justify one, a concrete gotcha does.
- Don't leave `<angle bracket>` instructions or unresolved `{{PLACEHOLDERS}}` in the body.
- Don't keep a section you have nothing to put in, and don't fill it with "N/A" or invented content. Delete it, heading included.
- Don't stack fragments for two or three kinds of change. One PR, one kind, whatever the diff also happens to touch.
- Don't write in the conversation's language when `language` says otherwise.
