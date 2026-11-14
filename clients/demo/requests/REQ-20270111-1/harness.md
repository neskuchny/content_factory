---
id: REQ-20270111-1
flow: f01
budget_credits: 0
---
# Harness for REQ-20270111-1 (FICTIONAL demo)

Flow `f01` (footage plus overlays), code engine only. Static cards are checked before the video is assembled.

| # | Step | Engine | Check | Status |
|---|---|---|---|---|
| 1 | Source skeleton for the clip and the photo | source-skeleton | every file has a skeleton | done |
| 2 | Beat list, 15 s | director | hook in the first 2 s; claims only from the owner's text | done |
| 3 | Cards (name, roast level, "espresso and milk drinks") | code (HTML) | text matches the brief word for word | todo |
| 4 | Assemble footage and cards | code (ffmpeg) | 9:16, 15 s, safe zones respected | todo |
| 5 | Subtitles and copper keyword highlight | code | no text inside the footage | todo |
| 6 | Adaptation for Telegram | adapter | no new facts relative to the hub | todo |
| 7 | QC and jury | reviewer | `review.md` verdict: PASS | todo |

## Questions to the human
1. Should the Telegram post include the bag photo as well as the clip? Put into the approval pack. (decision pending, see `decisions.md`)
