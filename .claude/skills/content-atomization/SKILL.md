---
name: content-atomization
description: "The hub-and-spokes model: how one hub content unit (Reels, long video, carousel, object) is broken down into adaptations for all of the client's spoke platforms without new production. Use during planning and adaptation."
---

# Atomization: hub to spokes

Hubs and spokes are defined in `clients/<client>/channels.yaml` (`role: hub | spoke`).

## Default matrix
| Hub source | What it becomes |
|---|---|
| Reels (object / production) | Shorts · VK Clips · Telegram channel (video + explanation) · profile Stories and WhatsApp status (a segment + an invitation to talk) · video pin · Threads (a thought + a question) · Yandex Maps post (real objects only) |
| AI visualization | Pinterest (pins with different houses and settings) · Stories ("what it could look like at your place") · Threads (discussion of the solution). **Does not go** to Yandex Maps as an object and is never passed off as a completed project |
| Carousel | Telegram / VK post (photo + the key takeaway) · card pins · Threads (a short breakdown) |
| Long video | VK Video · Rutube (same master) · 3–6 Shorts cut-downs · Telegram digest with a link · Threads (individual thoughts) · YouTube posts |
| Specialist answer | Telegram "question and answer" · Stories · Threads · FAQ in `product-base/` |
| Real object (case) | Maps (case + photos) · VK post · Telegram post · object pins |

## Rules
- A spoke **gets no** separate production beyond light adaptation (crop, format, caption).
- Each adaptation answers one reader question and has a next step.
- Technical facts are identical in every version; only the presentation changes.
- If a platform consumes a disproportionate amount of resources, the orchestrator proposes simplifying it.
