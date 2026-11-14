---
flow: f00-text-only
title: Text only → route selection
inputs: [text brief]
complexity: —
---
## When
The task arrived as text with no materials ("make a video about winter use of the product").

## Steps
1. **Parse the brief:** goal, platform, length, audience, target action, tone. Ask a human one
   question about whatever is missing. If a reasonable default can answer it, take the default and
   write it down.
2. **Check the archive:** look in `media-index/` for suitable sources. If there are any, this is no
   longer f00: switch to a flow that works with sources.
3. **Pick a no-shoot format:**
   | If you need to | Flow |
   |---|---|
   | Explain, compare, show numbers | f10 infographic |
   | Show "how it could be" with the product at the client's site | f04 / f17 (AI frames only, no source footage) |
   | An expert speaks, no shoot available | f13 avatar (only with consent in `brand/consents.md`) |
   | Story, emotion, premium | f16 film |
   | Adult audience, light delivery | f11 comic |
   | A service or an interface | f14 |
4. **Or a shoot brief** (skill `shoot-brief`) if shooting honestly beats generating
   (real objects, the company's people).
5. Record the decision and the route in `harness.md`.

## Rule
Do not try to make with AI generation what it does badly (exact text, complex hands, crowds,
the client's real objects without references). In those cases, shoot or use code.
