# Contributing

Thanks for your interest. This project is an opinionated harness for Claude Code agents, so most
contributions are edits to instructions (Markdown and YAML) rather than application code. Please
read [`CLAUDE.md`](CLAUDE.md) first: it is both the factory's constitution and the best
description of how the pieces fit.

By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md). Contributions are licensed
under the project's MIT license.

## Set up

1. Fork and clone the repository.
2. Install Python 3 and the one third-party dependency: `pip install -r requirements.txt`.
3. For anything that renders video you also need ffmpeg, Node 22+ and Chromium (see the README).
   Most documentation and instruction changes need none of these.
4. To try a change end to end, use the fictional client `clients/demo/` (`config/active-client.txt`
   is `demo`). See `docs/04-setup.md`, section 7.

Never put API keys, tokens or passwords in any file, issue or pull request. Use environment
secrets. If you think you committed a secret, rotate it first, then tell the maintainers.

## Run the checks

```bash
python3 -m unittest discover -s tests -v
python3 scripts/dashboard/build.py --client demo
python3 scripts/analytics/costs.py --client demo
```

The unit tests cover the scripts (guard hook, analytics, gatekeeper and the like). If you change a
script, add or update a test. The two demo commands are a quick smoke test that the example client
still parses.

## Conventions

- **Language.** Framework files (`CLAUDE.md`, `.claude/`, `flows/`, `config/`, `docs/`, `scripts/`,
  `templates/`) are written in English. Non-English text belongs only in locale data under
  `config/locales/` (for example a stoplist for another language) and in your own client data.
- **No client data in this repository.** `clients/` contains only the fictional `demo` client.
  Real names, handles, links, e-mail addresses, product facts, footage and metrics must not be
  committed. Keep real clients in a private repository.
- **Demo client stays fictional.** If you extend it, invent everything and keep the
  "FICTIONAL" markers.
- **No secrets, no heavy files.** No keys, no rendered videos in git (see `.gitignore`).
- **Keep the safety properties.** Changes must not weaken: facts only from `product-base/`, the
  "AI visualization" label, consent for real people, human approval per unit, manual publishing by
  default, and "agents that read the web do not publish or spend".
- **Stay small.** Prefer a short instruction or a small stdlib script to a new dependency. Scripts
  use Python and the standard library plus `PyYAML`; keep it that way unless there is a strong reason.
- **Use absolute paths** in Bash commands that write files (see `CLAUDE.md` section 9; the guard hook
  does not expand variables).
- **Don't invent features in docs.** Describe only what exists in the tree, and say so plainly when
  something is untested.

## Locked files and how to propose changes to them

The framework layer is locked for agents: `CLAUDE.md`, `.claude/agents/`, `.claude/skills/`,
`.claude/settings.json`, `config/`, and in client data the passport, `product-base/`,
`permissions.yaml` and `brand/consents.md`. This is enforced by `scripts/guard/guard.py` according to
`config/permissions-matrix.yaml`. It applies to the factory's agents at run time, not to you as a
human contributor.

For a change to these files:

1. Open an issue (feature request or bug report) describing the problem and the proposed wording or
   behaviour, or go straight to a pull request for a small fix.
2. In the pull request, explain why the change is needed and which agents or flows it affects. For
   changes to the guard, the permissions matrix or any safety rule, say how you tested that it still
   blocks what it should block.
3. Changes to the safety rules are reviewed most strictly and may be declined even if they work.

If you are using the factory and an agent hits the lock, it writes a proposal to
`clients/<client>/memory/proposals.md`. You can turn a good proposal into a pull request.

Vendored code under `.claude/skills/ffmpeg-skill/` is a copy of an upstream project. Do not edit it
here; update it from upstream and record the commit in its `VENDORED.md`.

## Pull request checklist

- [ ] The change is described, with the reason and the affected agents, flows or scripts
- [ ] Framework files are in English; no Cyrillic outside `config/locales/`
- [ ] No client data, secrets, personal e-mail addresses or private links
- [ ] `python3 -m unittest discover -s tests -v` passes
- [ ] If a script changed: tests added or updated; the demo commands still run
- [ ] If a safety rule, the guard or the permissions matrix changed: explained and tested
- [ ] Docs updated where behaviour changed (and the docs do not claim more than the tree supports)
- [ ] Third-party code or ideas are credited in `THIRD_PARTY_NOTICES.md` with their license

## Reporting problems

- Bugs and ideas: open an issue using the templates.
- Security problems (guard bypass, secret leakage, prompt-injection paths): do not open a public
  issue. Follow [`SECURITY.md`](SECURITY.md).
