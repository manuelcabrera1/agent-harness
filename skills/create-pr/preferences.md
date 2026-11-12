# Preferences

Everything team- or taste-specific that `create-pr` needs lives in a preferences file and a body template, so the skill itself stays generic. This document says where those files live, what the first-run interview asks, and what every key does.

## Where config lives

Two locations, both optional:

| Path | Scope | Good for |
|---|---|---|
| `~/.claude/create-pr/preferences.md` | every repo | tone, language, push behaviour, assignee — your personal defaults |
| `<repo root>/.claude/create-pr/preferences.md` | the current repo, wherever inside it you are working | tracker, ticket-id pattern, template — team conventions |

Read the global file first, then the repo one, and let the repo keys win key by key. Anything neither file sets falls back to the defaults in the schema below. That layering is the point of having two files: a single tracker and template per repo, one voice across all of them.

## How the body template resolves

The body is composed, not copied: a **core** that every PR gets, plus a **fragment** for the kind of change it is. A `feat` and a `fix` need different things from the author — one has to say what you can now do, the other why it broke — and asking every PR for both is how templates end up full of "N/A".

The core comes from `template.core` when a preferences file sets it — absolute, or relative to the file that named it, which also lets you point at a template the repo already has, such as `.github/pull_request_template.md`. Otherwise it's `template.md` next to the repo preferences file, then next to the global one, then the [template.md](template.md) shipped with this skill.

The fragment is `templates/<type>.md`, looked up in the repo config directory, then the global one, then this skill's own [templates/](templates), first hit winning. `<type>` is the conventional-commit type of the change — the skill ships `feat`, `fix`, `refactor`, `perf` and `chore`. No file for that type means core only, which is the right answer for `docs` or `style`. Adding a type is dropping a `revert.md` in your own `templates/`; overriding one is putting a file with the same name there, and it replaces the shipped fragment rather than merging with it. `template.by_type: none` turns the whole mechanism off.

`template.extra` covers the sections that hang off *what the diff touches* rather than what kind of change it is — a rollout checklist whenever a migration file appears, say. It's empty by default:

```yaml
template:
  extra:
    - file: templates/migration.md
      paths: ['**/migrations/**', '**/*.sql']
```

## First-run setup

Run the interview when no preferences file exists in either location, or when the user asks to configure the skill ("set up create-pr", "change my PR template", "cambia la plantilla de PR"). In the first case, write the file and then carry on with the PR they actually asked for; in the second, write the file and stop.

Use `AskUserQuestion` and ask in the language the user is speaking. **Skip anything the user already told you** — "open a PR for ABC-123, no push, don't ask me before creating" answers half the interview, and asking it again is what makes a setup flow feel like paperwork. If the answers are all known, just write the file and show it.

Group the questions like this, four or fewer per call:

1. **Tracker** — ClickUp, Jira, Linear, GitHub Issues, none, or other. If they pick one, ask them to paste the URL of any ticket, and derive `url_template` and `id_pattern` from it: `https://acme.atlassian.net/browse/ABC-123` becomes `https://acme.atlassian.net/browse/{id}` with `[A-Z]+-\d+`. Deriving beats asking for a regex.
2. **Template** — offer the shipped core plus the per-type fragments, the repo's own `.github/pull_request_template.md` when one exists (check before asking), or "I'll paste mine". Whatever they choose becomes the *core*: write a pasted template to `template.md` next to the preferences file verbatim, and when they bring their own, ask once whether the per-type fragments go on top of it or not.
3. **Voice** — the language the PR is written in (default `en`, and worth confirming rather than assuming: it's the one setting the user notices on every single PR) and the tone.
4. **Habits** — multi-select over the switches that change what the command does: confirm before creating (on by default), assign the PR to me (on), push when the branch has no upstream (off), open as draft (off).

Where to save it is a fifth question worth asking only when the answers actually split — a tracker or template that belongs to one repo alongside a voice that doesn't. Otherwise write everything globally; that's the common case, and one file is easier to find later.

Don't ask about the rest of the schema. `alerts`, `detail`, `title.*`, `change_type`, `template.extra`, `reviewers`, `labels` and the two footer switches all have defaults that are right for almost everyone; they exist in the file so someone who wants to hand-tune can, not because they earn a question.

After writing, show the user the file and its path, so editing it by hand later is obvious.

## The file

A `yaml` block for the settings, followed by free prose the skill reads as extra instructions. Both parts are optional; a file with three keys in it is a perfectly good preferences file.

~~~markdown
# create-pr preferences

```yaml
language: en
tracker:
  name: jira
  url_template: https://acme.atlassian.net/browse/{id}
  id_pattern: '[A-Z]{2,}-\d+'
  required: true
tone: neutral
push: never
assignee: '@me'
```

## Notes

Scope in this monorepo is the app, not the package inside it: `web`, never `web-ui`.
~~~

## Schema

Defaults in bold.

**`language`** — the language the body is written in, and the title too unless `title.language` says otherwise, **`en`**. This one overrides everything around it: write in this language even when the conversation, the commit messages and the ticket are in another one, and translate the source material rather than mirroring it. Reviewers expect one language on PRs, and it isn't whichever one the author happened to be typing in that afternoon. Identifiers, paths, quoted code and conventional-commit types stay verbatim.

**`tracker.name`** — the issue tracker, or **`none`** to drop ticket handling entirely. The name is a label for the interview; the two keys below are what actually do the work.

**`tracker.url_template`** — the ticket URL with `{id}` where the id goes. Required when the tracker isn't `none`.

**`tracker.id_pattern`** — a regex the id must match, used both to validate what the user gives you and to spot an id in the branch name (`feature/ABC-123-retry-webhooks` → `ABC-123`). A detected id is a suggestion: confirm it before using it.

**`tracker.required`** — when **`true`**, no PR without a ticket id: ask for it before anything else and don't invent one. Set `false` for repos where chores and dependency bumps have no ticket, and drop the ticket line from the body when there's none.

**`template.core`** — path to the core template, unset by default. See the resolution order above.

**`template.by_type`** — the directory holding the per-type fragments, **`templates`**, relative to the preferences file. `none` disables fragments and leaves every PR with just the core.

**`template.extra`** — fragments keyed by touched paths rather than by change type, **empty**. Each entry is a `file` and a list of `paths` globs; the fragment is appended when the diff touches a match. Keep this short — a body assembled from five fragments is the padding the type split exists to avoid.

**`change_type`** — how the kind of change is decided. **`auto`** takes the conventional-commit type from the title when the repo uses them and infers it from the diff otherwise; `title` only ever reads the title and falls back to core-only; `ask` asks. What the user says outright ("this is a refactor") beats all three.

In every template file, angle-bracket text (`<one or two sentences...>`) is an instruction to you, not literal text — replace it, and never leave one in a PR body. Same for `{{TICKET_URL}}` and `{{TICKET_ID}}`: substitute them, and when there's no ticket, drop the whole line that held the placeholder. HTML comments are stripped before the body is posted, which is what makes them the right place to mark a section optional. Keep checkbox lists as they are and tick what genuinely applies.

**`title.language`** — the language the title is written in, by default **whatever `language` says**. Set it where the title answers to a convention the body doesn't: a repo whose commit history is English keeps English titles above a Spanish body.

**`title.convention`** — **`auto`** reads the last commits on the base branch and follows what it finds; `conventional-commits` and `plain` force it either way.

**`title.max_length`** — soft ceiling, **`70`**. Aim under it; a couple of characters over beats truncating into vagueness.

**`title.include_ticket_id`** — whether the id goes in the title, **`false`** (it's in the body).

**`title.scope`** — free text describing how scopes work here, for repos where the obvious guess is wrong. Empty by default.

**`tone`** — **`neutral`** is plain and factual; `direct` cuts every softener; `warm` allows some first person; `formal` keeps it impersonal and complete. Tone changes wording only. It never changes what's covered or how long the body is — those are `detail` and the rules in SKILL.md.

**`detail`** — how much Solution a PR gets. **`proportional`** scales it to the diff, which is the behaviour SKILL.md describes in full and the right answer nearly always. `minimal` keeps it to a couple of sentences whatever the size, for teams that do their reviewing in the diff; `thorough` walks through the meaningful changes even on small PRs.

**`alerts`** — GitHub alert blocks (`> [!WARNING]`). **`sparing`** applies the test in SKILL.md, meaning most PRs get none; `never` forbids them; `allowed` relaxes the bar but still won't add one just to decorate.

**`push`** — what to do when the branch has no upstream. **`never`** stops and tells the user to push; `ask` offers to run `git push -u origin HEAD`; `auto` pushes and says so. Nothing here ever commits, amends or force-pushes, whatever this is set to.

**`base_branch`** — **`auto`** detects the remote's default branch; set a name to pin it.

**`draft`** — **`never`**, `always`, or `ask`. Adds `--draft`.

**`assignee`** — **`@me`**, `none`, or a login. `@me` is the authenticated `gh` user.

**`reviewers`** — logins or teams for `--reviewer`, **empty**. Requesting review is visible to the people named, so keep this to reviewers a team convention actually mandates.

**`labels`** — labels for `--label`, **empty**. Fails the whole command if a label doesn't exist in the repo, so only put stable ones here.

**`attribution_footer`** — when **`false`**, no "Generated with Claude Code" footer and no `Co-Authored-By` trailer. Many teams reject those on sight; turn it on only if the user asks.

**`test_plan_section`** — when **`false`**, no test-plan section unless the template has one or the user asks.

**`confirm_before_create`** — when **`true`**, print the title and body and wait. Keep it on: a PR is visible to the team the moment it exists, and it can't be quietly unsent. Turning it off is for deliberate automation only.

**`extra_instructions`** — free text, or the prose after the yaml block. The escape hatch for conventions that aren't worth a key: "always mention the affected service in the title", "link the design doc when the diff touches the editor". Follow it unless it contradicts the invariants in SKILL.md.

## When setup can't run

If the interview isn't possible — non-interactive, or the user says "just open the PR, don't ask me things" — use the defaults above with `tracker.name: none`, and set `language` to the language the user is writing in, which is the only signal available. Create the PR, then mention once that setup exists and would pin this down.
