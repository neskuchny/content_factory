# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

_Nothing yet._

## [0.1.0] - TBD

The first public, English-language release of the content factory: a Claude Code harness that
turns a client's raw material and product knowledge into short-form video, with a human approving
every unit before anything is published.

### Added

- **Framework.** `CLAUDE.md` as the constitution every agent reads first: three layers of
  mutability (framework, client data, working artifacts), the weekly cycle with stages 0–8 and a
  gate for each, one-off requests (`REQ-<YYYYMMDD>-<n>`), planning rules, hard prohibitions and the
  task-board protocol.
- **11 agent roles** in `.claude/agents/`: orchestrator, producer, director, studio, reviewer,
  adapter, publisher, analyst, media-indexer, feedback, onboarding. Each sets its model, effort,
  tools and allowed MCP calls.
- **21 skills** in `.claude/skills/`, among them `weekly-cycle`, `source-skeleton`,
  `approval-pack`, `fact-check`, `video-code`, `seamless-insert`, `jury`, `publish-kit`,
  `perf-loop`, `memory-compaction` and `dispatch`. `ffmpeg-skill` is vendored (MIT) at a pinned
  commit; see `THIRD_PARTY_NOTICES.md`.
- **19 video flows** `flows/f00`–`f18` (from text-only and long-to-short to object inserts,
  infographics, avatars and code films) plus the step library from which the director assembles a
  `harness.md` for any video.
- **Configuration** in `config/`: `engines.yaml` (format → engine), `permissions-matrix.yaml`
  (per-role read and write rules), `pricing.yaml`, `sparks.yaml` (idea dice).
- **Scripts that need no model**: the permissions hook `scripts/guard/guard.py`, metric baselines
  and cost summaries (`scripts/analytics/`), a public Telegram collector, a static dashboard, an
  Openverse search helper, QA helpers (`words_check.py`, `dice.py`) and the tick gatekeeper
  `scripts/ticks/precheck.py`.
- **Templates** for a new client, a week and a one-off request (`templates/`).
- **Demo client** `clients/demo/`: a fictional specialty-coffee roaster with a product base,
  a sample week (`2027-W02`) and a sample request (`REQ-20270111-1`). All names and facts are
  invented.
- **Locales.** Language is a per-client setting (`passport.yaml: language`, BCP-47, default `en`).
  Locale data lives in `config/locales/` (`en.yaml`, `ru.yaml`);
  `scripts/qa/words_check.py --lang <code>` picks the stoplist.
- **Documentation**: setup and run modes, how the harness works, the general harness methodology,
  the video formats catalogue, memory / analytics / ticks / permissions, and research notes.
- **Tests and CI.** A `unittest` suite in `tests/` (guard, demo client, repository hygiene,
  script smoke tests, `words_check`). The `ci` GitHub Actions workflow byte-compiles every Python
  file and runs the suite on Python 3.12 with read-only repository permissions.
  The `factory-ticks` workflow ships with its hourly schedule disabled.
- **Community files**: MIT `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`,
  `THIRD_PARTY_NOTICES.md`.

### Security

- **guard: factory-script whitelist bypass.** The whitelist for the factory's own scripts now
  applies only to a single plain command. Anything with file redirects, `;`, `&`, `|`, backticks
  or `$(` gets the normal checks. Previously, for example,
  `python3 scripts/ticks/precheck.py > CLAUDE.md` was allowed for any role.
- **guard: segment-aware path globs.** `*` no longer matches across `/`, so a role's glob cannot
  reach another role's area.
- **guard: `/tmp` traversal.** The `/tmp` and `/dev` exemption now compares the resolved path, so
  `/tmp/../etc/x` is denied.

### Fixed

- **precheck: approval-pack section parsing.** Each `## <ID>` section of the approval pack is
  parsed on its own, so a pending unit is no longer read together with the next unit's decision.
- The five tests that covered these issues were expected failures; they now pass and run as
  regular regression tests. New tests check that harmless pipes and stderr redirects still work.

[Unreleased]: https://github.com/neskuchny/content_factory/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/neskuchny/content_factory/releases/tag/v0.1.0
