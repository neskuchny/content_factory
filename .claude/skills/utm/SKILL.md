---
name: utm
description: "Building and logging links with UTM tags for every publication according to the client's scheme. Use during adaptation and publishing."
---

# UTM

The scheme is in `clients/<client>/utm.yaml`. If it is missing, do not tag the link; ask a question.

## Format
`<base_url>?utm_source=<source>&utm_medium=<medium>&utm_campaign=<W>&utm_content=<ID>-<placement>`
- `source` — a platform from `utm.yaml` (`instagram`, `youtube`, `vk_video`, `rutube`, `pinterest`, …);
- `content` — the unit ID and the link placement (`desc`, `pin`, `comment`, `story`).

## Rules
- The destination page matches the product in the publication. Check that it opens (HTTP 200).
- Record every link in `07-publications.md`: `ID | platform | link`.
- Do not promise that every click will be counted: UTM prepares measurement but does not set up end-to-end analytics.
