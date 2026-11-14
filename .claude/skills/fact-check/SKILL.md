---
name: fact-check
description: "Verify claims about the product, prices, timelines, clients and the company against the client's product base. Use when writing scripts and texts, during adaptation and during review."
---

# Fact check

## What counts as a fact
Any claim about product properties, materials, price or price factors, timelines,
warranty, geography, the working process, clients, reviews, or people at the company.

## Procedure
1. List all facts from the text.
2. For each one, find confirmation in `clients/<client>/product-base/` (grep by keywords)
   or in `memory/confirmed-answers.md` (the client's confirmed answers).
3. Write a block in the script:
```
## Facts
- "Withstands the rated snow load …" → product-base/products.md#loads ✔
- "Installation takes 3 days" → NOT FOUND ✖ → question to the client
```
4. For anything unconfirmed: remove it from the text, **or** rephrase it without specifics, **or** put
   one precise question in the approval pack.

## Never
- Confirm a fact with a link to the web, competitors or "common knowledge".
- Invent client stories, quotes or reviews.
- Round or "improve" numbers.
