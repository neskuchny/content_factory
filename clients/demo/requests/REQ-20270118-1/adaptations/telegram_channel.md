# REQ-20270118-1 → Telegram channel (spoke)

> FICTIONAL demo client — all names and facts are invented.

Hub: `docs/showcase/freshness-dial.mp4` (18 s code film). Channel: `@example_channel`, manual publishing
(`channels.yaml → telegram_channel`: "short text + the reel's best 15 s clip or one picture; no new facts").

**Picture:** [`telegram_channel.jpg`](telegram_channel.jpg) — frame 12.7 s: the copper band is lit and the title
reads "Best brewed about 5 to 28 days after roast".

**Text:**

> Look for the roast date on the bag. We rest our beans for 5 days before packing, and they are best brewed
> about 5 to 28 days after the roast date. Grind just before brewing.
>
> https://brewline.example/visit?utm_source=telegram&utm_medium=social&utm_campaign=2027-W03&utm_content=REQ-20270118-1

**Facts check:** every sentence is the hub caption (`beats.md` → "Caption and link"), sourced from
`product-base/roasting-process.md` (#4, beans rest 5 days; #5, roast date on every bag) and
`product-base/care-tips.md` (Freshness: 5–28 days; grind just before brewing). No new facts, no prices.
`words_check.py --lang en`: only the expected "best" and "5 days" / "28 days" hints, all sourced.
