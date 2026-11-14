# Repository settings to set by hand

These live in GitHub's settings, not in git, so the owner sets them once in the web UI
(repository `neskuchny/content_factory`). Nothing here needs a token or an app.

## 1. About (the gear icon next to "About" on the repository page)

- **Description** (111 characters):

  ```text
  Claude Code harness that makes short-form social video: 11 agents, 19 video flows, a human approves every unit.
  ```

- **Website:** none. Leave the field empty.
- **Topics** (12):

  ```text
  claude-code  ai-agents  multi-agent  llm-agents  human-in-the-loop  content-automation
  video-production  short-form-video  social-media  ffmpeg  mcp  claude
  ```

- **Include in the home page:** keep *Releases*; untick *Packages* and *Deployments* (the
  project publishes neither).

## 2. Social preview

Settings → General → **Social preview** → *Edit* → *Upload an image…* →
`docs/assets/social-preview.png` (1280 × 640 PNG, about 67 KB; GitHub accepts up to 1 MB and
recommends 1280 × 640). The source is `docs/assets/src/social-preview.html`; re-rendering it needs
the two font files named in its header comment, which are not in the repository.

## 3. Template repository (Settings → General)

- Tick **Template repository**. People then get a **Use this template** button and start their own
  private copy without forking (a fork of a public repository is public, and their copy will hold
  client data). The README's "Start here" section and the `setup` skill describe both ways: a
  template copy, or a clone pushed to their own private repository (easier updates).

## 4. Features (Settings → General → Features)

- **Issues:** on.
- **Discussions:** on. Suggested categories:
  - *Announcements* (maintainers only): releases and breaking changes to the instruction files.
  - *Q&A* (answers enabled): setup, running the demo client, model and generator questions.
  - *Ideas*: new flows, steps, skills, locales.
  - *Show and tell*: harnesses built from this one for other tasks (see `docs/08-harness-methodology.md`).
- **Wiki:** off (documentation lives in `docs/`).
- **Projects:** off unless you plan to use them.

## 5. Security (Settings → Code security)

- **Private vulnerability reporting:** on. `SECURITY.md` asks reporters to use
  "Security → Report a vulnerability", which only exists when this is enabled.
- **Dependabot alerts:** on. Optionally Dependabot security updates for `requirements.txt` and the
  GitHub Actions used in `.github/workflows/`.
- **Secret scanning** and **push protection:** on (free for public repositories). The project rule
  is that keys never enter the repository; push protection enforces it at `git push`.

## 6. Actions (Settings → Actions → General)

- **Workflow permissions:** *Read repository contents and packages permissions* (the default
  read-only token). `ci.yml` already asks only for `contents: read`; `factory-ticks.yml` asks for
  `contents: write` explicitly in its own file.
- **Fork pull request workflows:** keep *Require approval for first-time contributors*.
- `factory-ticks.yml` has its hourly schedule commented out and needs two repository secrets
  before it can do anything (see the comment at the top of the file). Do not add those secrets to
  the public repository unless you run the factory from it.

## 6. Branch protection (Settings → Rules → Rulesets → New branch ruleset)

Suggested ruleset for the default branch (`main`):

- Target: *Include default branch*. Enforcement: *Active*.
- **Restrict deletions** and **Block force pushes.**
- **Require a pull request before merging**, with 1 approving review once there is more than one
  maintainer, and *Dismiss stale approvals when new commits are pushed*.
- **Require status checks to pass:** add the check `test` (the job in the `ci` workflow) and tick
  *Require branches to be up to date before merging*.
- Optional: **Require linear history** (squash or rebase merges only).
- Add the repository admin to the bypass list only if you need to push emergency fixes.

If you use the ticks workflow, it commits client data to a separate `factory` branch. Do not
include `factory` in this ruleset, or the tick cannot push.

## 7. First release: v0.1.0

1. In `CHANGELOG.md`, replace `TBD` in `## [0.1.0] - TBD` with the release date (`YYYY-MM-DD`) and
   merge that change to `main`.
2. Releases → *Draft a new release* → tag `v0.1.0` on `main` (create the tag on publish) →
   title `v0.1.0: initial English release` → paste the notes below → *Set as the latest release*.

Suggested release notes:

```markdown
The first public release of Content Factory: a Claude Code harness that turns a client's raw
material and product knowledge into short-form video, with a human approving every unit before
anything is published.

**What is inside**
- `CLAUDE.md`: the rules every agent reads first: three layers of mutability, a weekly cycle of
  stages 0–8 with a gate each, hard prohibitions, the task-board protocol.
- 11 agent roles, 21 skills, 19 video flows (f00–f18) and a step library for building new routes.
- `scripts/guard/guard.py`: a PreToolUse hook that checks every read, write and Bash command
  against a per-role permissions matrix, and keeps the locked layer human-only.
- Scripts that need no model: metric baselines, cost summaries, a dashboard, the tick gatekeeper.
- A fictional demo client (a specialty-coffee roaster) with a sample week and a sample request.
- Per-client language (`passport.yaml: language`), with English and Russian locale data.
- A unittest suite and a CI workflow (Python 3.12).

**Security fixes since the internal version**
- The guard's factory-script whitelist no longer lets redirects or chained commands through.
- Path globs in the permissions matrix are segment-aware.
- The `/tmp` exemption resolves the path first, so `/tmp/../` traversal is denied.
- The tick gatekeeper parses each approval-pack section on its own.

**Before you try it**
- You need your own Claude Code account and, for paid generation, your own generator account
  (Higgsfield via MCP is wired in). Spend is tracked and limited per client, but it is your account.
- Publishing is manual by default: the factory prepares a kit, a human posts it.
- This is a working harness extracted from real use, not a polished product. No agent had passed
  a full weekly cycle end to end when the docs were written; expect to tune prompts and flows.

Full list of changes: [CHANGELOG.md](https://github.com/neskuchny/content_factory/blob/v0.1.0/CHANGELOG.md).
```
