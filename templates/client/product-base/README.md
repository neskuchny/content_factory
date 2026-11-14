# Product base

The only source of facts for all agents (see skill `fact-check`). Empty at first: the client supplies
materials (site, catalog, price list, specifications, FAQ, answers from specialists).

## Structure (one file per topic; adapt the names to the business)
```
about.md            # the business: what, where, since when, locations, delivery or service area
product-a.md        # one file per product or product line
process.md          # how ordering, delivery or service works, step by step
prices.md           # prices or price factors, each with may_publish and valid_until
faq.md              # frequent questions and doubts + confirmed answers
cases/              # finished orders or projects: task, solution, result, photos (with consent)
media/              # reference product photos for AI visualizations (2–3 angles, dimensions)
```

## Every fact carries its source
A link, a file, or "said by <name>, <role> on <date>". A fact without a source is a question for the
client, not a fact. Prices also carry `may_publish: yes | no` (may it appear in a video or caption) and
`valid_until` if they change.

## Product file template
```markdown
# <Product>
## What it is and who it is for
## Variants
## Ingredients, materials or components
## Specifications (with source)
## Use and care
## Price (may_publish, valid_until, source)
## Frequent doubts → answer (who confirmed, date)
## Reference photos: media/<...>
```

For a filled-in example see `clients/demo/product-base/`.
