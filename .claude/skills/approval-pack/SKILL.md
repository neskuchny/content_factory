---
name: approval-pack
description: "Assemble the week's single approval pack for the human: all content units for all platforms in one message or page, with previews, variants and a simple way to reply. Use at stage 6."
---

# Approval pack

The goal is for the human to spend **as little time as possible** and still answer on every unit.

## Format of `weeks/<W>/06-approval.md`
```markdown
# Approval <YYYY-Www> — <client>
Summary: N hub units, M adaptations, budget spent X of Y. Quota: met / not met (why).

## Questions (answer in one line)
1. ...

## W44-R01 · Reels · "<topic>"
Preview: <link to file>   Variants: A (hook "…") · B (hook "…") · C (…)
Adaptations: Shorts, Telegram channel, VK, Pinterest
Facts: ✔ checked   AI: no
decision: pending        # Take A | Take all | Not this | Redo: <comment>
comment:
```

## Delivery
- If a Telegram channel is connected (channels), send a short summary and a link to the pack. Replies
  are accepted in the format `R01 A`, `R02 not this: too promotional`.
- Otherwise publish the pack as an artifact page or as a file in Google Drive.
- Copy the human's replies into the `decision`/`comment` fields **verbatim**.

## Rules
- Show the variants of one topic side by side so they are easy to choose between.
- Put the questions that block publishing first.
- No filler: one line of context per unit.
