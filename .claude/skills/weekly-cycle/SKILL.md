---
name: weekly-cycle
description: "Starting and running the content factory's weekly cycle — creating the week folder, checking stages and gates, what to do at each stage. Use at the start of a week, when checking \"where are we now\", and when recovering after a failure."
---

# Weekly cycle

## Start of the week
1. The week = the ISO week: `date +%G-W%V`.
2. Create `clients/<client>/weeks/<YYYY-Www>/` with the files from `templates/week/` if they do not exist yet.
3. Fill in the header of `01-plan.md`: the week's quotas from `quotas.yaml`, the budget limit from `permissions.yaml`.

## Where are we now (recovery)
The state of the week is determined **by files only**, not by session memory:
| File state | Meaning |
|---|---|
| no `01-plan.md`, or it has `status: draft` | stage 1 |
| `01-plan.md` has `status: final`, no `03-scripts/` for all IDs | stages 2–3 |
| scripts exist, no `04-production/<ID>/review.md` with PASS | stage 4 |
| all hubs PASS, no `05-adaptations/` | stage 5 |
| no `06-approval.md`, or it contains `decision: pending` | stage 6 — waiting for the human |
| approved units exist without a line in `07-publications.md` | stage 7 |
| no `08-retro.md` | stage 8 |

Continue from the first unclosed stage. Do not redo finished work.

## Unit statuses (the `status` field in the plan)
`planned → brief_sent → scripted → produced → reviewed → adapted → in_approval → approved | rejected | rework → published | kit_ready`

## Stop conditions
- Budget exceeded → stop, ask the human.
- 3 FAILs in a row from the reviewer → stop for that unit, ask the human with examples.
- No facts → do not invent; put the question in the approval pack.
