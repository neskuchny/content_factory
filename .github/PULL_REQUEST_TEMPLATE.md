## What and why

<!-- What does this change, and what problem does it solve? Link the issue if there is one. -->

## What is affected

<!-- Agents, skills, flows, scripts, config, docs, templates, the demo client. -->

## Checklist

- [ ] Framework files are in English; no Cyrillic outside `config/locales/`
- [ ] No client data, secrets, personal e-mail addresses or private links
- [ ] `python3 -m unittest discover -s tests -v` passes
- [ ] If a script changed: tests added or updated, and `python3 scripts/dashboard/build.py --client demo` and `python3 scripts/analytics/costs.py --client demo` still run
- [ ] If a safety rule, the guard hook or `config/permissions-matrix.yaml` changed: explained below and tested
- [ ] Docs updated where behaviour changed, and they claim only what the tree supports
- [ ] Third-party code or ideas are credited in `THIRD_PARTY_NOTICES.md` with their license
- [ ] Safety properties are intact: facts only from the product base, AI content labelled, consent for real people, human approval per unit, manual publishing by default, web-reading agents do not publish or spend

## Safety-relevant changes (if any)

<!-- For changes to locked files, the guard or the permissions matrix: how did you test that it still blocks what it should? -->

## How you tested

<!-- Commands run, demo client used, and what you saw. -->
