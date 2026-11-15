# Third-party notices

This project is released under the MIT license. It contains or refers to the following third-party
material.

## Vendored: ffmpeg-skill

- Location: `.claude/skills/ffmpeg-skill/`
- Source: https://github.com/kajisho5/ffmpeg-skill
- Author: kajisho5
- License: MIT (copyright (c) 2026 kajisho5). The full text is in
  `.claude/skills/ffmpeg-skill/LICENSE`.
- Pinned to commit `6e42a79247909659b3d80833120b272fb5e46aba` (2026-11-07), as recorded in
  `.claude/skills/ffmpeg-skill/VENDORED.md`. `SKILL.md`, `scripts/`, `references/` and `LICENSE`
  were copied unchanged.

It requires a local FFmpeg installation (FFmpeg itself is not included and has its own licenses).

## External service: treg

- Site: https://treg.to; source: https://github.com/superdesigndev/treg
- License: Apache License 2.0 with additional terms (no redistribution as a competing hosted or managed
  registry without the authors' permission; calling the hosted service is allowed).
- No code is vendored. The factory only lists the hosted MCP endpoint in `.mcp.json` and describes how
  to use it in `.claude/skills/treg-gateway/SKILL.md`. The service and the models behind it have their
  own terms and prices; you need your own account.

## Ideas credited: cinecode

Some techniques are adapted from [sarpstar/cinecode](https://github.com/sarpstar/cinecode) (MIT),
a project for films written in code. No code is vendored. The credit appears in the files where
the idea is used:

- `flows/f18-code-film.md`: ideas and rules for code-drawn films
- `.claude/skills/jury/SKILL.md`: the "jury" review questions
- `.claude/skills/idea-dice/SKILL.md`: the idea "dice"
- `scripts/qa/words_check.py`: the idea of a phrase checker (the word lists are our own)
- `docs/10-external-tools-review.md`: the review that led to these choices

The lists and texts in these files were written for this project.

## Referenced, not bundled

These are named in the documentation or flows. Nothing from them is included in this repository;
you install them yourself and accept their licenses and terms.

- **Remotion** (`remotion-dev/skills` and the Remotion renderer): has its own company license
  terms, which require a paid license for companies above a size threshold. It is an optional
  install only. Check https://www.remotion.dev/license before using it commercially.
- **HyperFrames** (`heygen-com/hyperframes`): installed with `npx skills add`; see its own license.
- **three.js**, **GSAP**: used by code-film and motion flows when you write scenes; installed or
  loaded by you.
- **Playwright / Chromium**: used for headless rendering; installed by you.
- **Fonts**: no fonts are bundled. If you use fonts in rendered videos, check their licenses.
- **FFmpeg**, **faster-whisper**, **Pillow** (optional), **PyYAML**: installed by you.
- **Services and MCP servers** such as Higgsfield, ElevenLabs (via Higgsfield), Linear and Google
  Drive: third-party services with their own terms and pricing. The generated media and any music or
  sound effects you use carry their own licenses; check them for commercial use (see the
  `sound-design` skill).

Product and company names are trademarks of their respective owners and are used only to describe
compatibility. This project is not affiliated with or endorsed by them.
