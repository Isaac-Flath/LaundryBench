# 07 · Trading-card pack left in a pocket

[← All examples](../../README.md)

![Trading-card pack left in a pocket](image.jpg)

## What are we checking?

Several cards retain title and rule fragments despite torn edges, folds and missing sections.

These are the visible facts we want an OCR output to recover. Each row is one check. These answers were selected by inspecting the photograph; they are not model-generated reference transcripts.

| Check | Expected content | Where to look |
| --- | --- | --- |
| Which creature subtype is visible on the diagonal card? | Phyrexian Chimera | Gold type bar on the middle card. |
| Which keyword survives on the front card? | Vigilance | First rules line on the torn front card. |

The table shows the expected facts, not required formatting. **And** means both pieces must be present. Case, accents, ordinary punctuation and line breaks do not matter; values and labels must still be correct.

The exact rules and accepted alternative spellings are in [checks.json](checks.json). Each `all_of` group must match; any alternative inside that group is accepted.

These few checks measure recovery of selected facts. They do not check every word or catch every invented sentence.

## Actual OCR outputs

**Not run yet.** This example has a photograph and content checks, but no saved parser output or judge result. Expected answers above are not measured results.

## About this photograph

Multiple cards in one photograph, including a badly torn Elesh Norn card.

Source: [u/Lipzilla](https://www.reddit.com/r/mtg/comments/129syxr/so_i_just_ruin_a_most_wanted_card_on_accident/)

[How to run an example](../../scripts/README.md)
