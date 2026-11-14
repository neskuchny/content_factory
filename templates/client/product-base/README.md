# Product base

The only source of facts for all agents (see skill `fact-check`). Empty at first: the client has to supply
materials (catalog, specifications, price factors, FAQ, confirmed answers from specialists).

## Structure (one file per product)
```
product-a.md        # one file per product or product line
product-b.md
process.md          # how the work goes: request → measurement → design → production → delivery
pricing-factors.md  # what drives the price (no concrete prices unless the client allows it)
faq.md              # frequent questions and doubts + confirmed answers
objects/            # completed projects: task, solution, details, result, photos
media/              # reference product photos for AI visualizations (2–3 angles, dimensions)
```

## Product file template
```markdown
# <Product>
## What it is and who it is for
## Variants and configurations
## Materials and components
## Specifications (with source)
## Use and care
## What affects the cost
## Frequent doubts → answer (who confirmed, date)
## Reference photos: media/<...>
```

For a filled-in example see `clients/demo/product-base/`.
