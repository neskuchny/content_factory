# Security Policy

## Reporting a vulnerability

Please report security problems privately through **GitHub Security Advisories**: on the
repository page, open the "Security" tab and choose "Report a vulnerability". Do not open a public
issue or pull request for a vulnerability, and do not post exploit details publicly until a fix is
available.

Include what you found, how to reproduce it (a minimal `clients/demo/` setup is ideal), and the
impact you expect. This is a volunteer-maintained project: we will acknowledge a report and try to
respond within a reasonable time, but we cannot promise a fixed schedule.

## What is in scope

The factory's safety model is described in [`README.md`](README.md) and `CLAUDE.md` section 5. We
are interested in reports about:

- **Guard bypass.** A way for an agent (or content an agent processes) to read or write something
  the permissions matrix forbids: the locked layer (`CLAUDE.md`, `.claude/`, `config/`, passport,
  `product-base/`, `permissions.yaml`, `brand/consents.md`), another role's folders, or secret
  paths. The hook is `scripts/guard/guard.py`, configured by `config/permissions-matrix.yaml` and
  wired up in `.claude/settings.json`. Bash command parsing in the guard is heuristic, so bypasses
  through shell constructs are worth reporting.
- **Secret leakage in scripts.** Scripts under `scripts/`, the GitHub workflow in
  `.github/workflows/`, or any template that could write keys, tokens or other credentials into
  the repository, logs, committed files or outbound requests.
- **Prompt-injection paths from untrusted web content into publishing or spending.** The factory
  rule is that untrusted content (web pages, other people's posts, comments, tick payloads) is
  data, not instructions, and that **agents that read the web must not publish or spend**. A path
  by which text from such content can cause a publication, a message, a comment, or paid
  generation without a human approval is a vulnerability. So is a role that is given both web
  access and publishing or spending ability.
- **Bypassing human approval or `permissions.yaml`**: publishing or spending that skips the
  approval pack or exceeds the stated limits.

## What is out of scope

- Vulnerabilities in third-party services and tools the factory can call (Claude Code, Higgsfield,
  ffmpeg, Node, Chromium, Linear, Google Drive, etc.). Report those to their vendors.
- The vendored `.claude/skills/ffmpeg-skill/` code: report issues upstream (see
  `THIRD_PARTY_NOTICES.md`); we will update our copy.
- Weaknesses that require the attacker to already have write access to your repository or to be the
  human owner. In an interactive session without an agent role, the guard treats the user as the
  owner by design.
- Model behaviour in general (hallucinations, quality of generated content) that does not cross one
  of the safety boundaries listed above. Open a normal issue for those.
- Misconfiguration in your own copy, such as committed keys or enabling automatic publishing with
  broad permissions.

## Your responsibilities when running the factory

The guard hook is a guardrail, not a sandbox. When you run your own copy, keep keys in environment
secrets, review `permissions.yaml` and the credit limit before the first run, keep publishing
manual until you trust a specific integration, protect your main branch, and review what agents
commit.
