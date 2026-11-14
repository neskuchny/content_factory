---
name: idea-dice
description: "Idea dice: a way to get away from the first obvious concept. The video's topic is crossed with a random real thing (an object, a profession, a natural phenomenon, an invention, a genre, an everyday situation) and an unexpected angle emerges from the intersection. Use for the producer during the sighting round (3–5 different variants per topic), when concepts come out similar, and when the human asks for \"something interesting\"."
---

# Idea dice

Based on `dice.py` / `sparks.json` from sarpstar/cinecode (MIT); the list of "sparks" is our own, written
for everyday topics and the client's audience.

## How to roll
`python3 scripts/qa/dice.py [N] [--seed S]` outputs N sparks (3 by default) from `config/sparks.yaml`,
one from each of different categories. The seed is written into the brief so the roll can be repeated.

## How to use
1. The video's topic (for example, "choosing a spot for the product") + a spark (for example, "weather forecast").
2. Look for a real intersection: a format, mechanic, visual language or conflict that the spark gives the topic
   ("forecast for seedlings: shade expected on this plot until noon").
3. From three sparks, make three **fully different** concepts for the sighting round (hook, mechanic, ending).
4. Test: if the concept could be handed to any other company unchanged, roll again.
5. A spark adds no facts about the product: the fact-check rules stay in force.

## Prohibitions
- Do not mock people, professions, regions or nationalities.
- Do not use other people's brands, characters, songs or recognizable formats of specific shows.
- Do not touch politics, religion or tragedies.
