# 10 · Game cartridge with its label washed away

[← All examples](../../README.md)

![Game cartridge with its label washed away](image.jpg)

## What are we checking?

The cartridge has a ruined printed label with handwritten markings; a readable game booklet sits beside it.

These are the visible facts we want an OCR output to recover. Each row is one check. These answers were selected by inspecting the photograph; they are not model-generated reference transcripts.

| Check | Expected content | Where to look |
| --- | --- | --- |
| Which game title is readable on the booklet? | Pokemon **and** Black Version 2 | Intact booklet on the left, not the washed cartridge. |
| What kind of booklet is it? | Instruction Booklet | White diagonal lettering on the booklet, not the cartridge. |

The table shows the expected facts, not required formatting. **And** means both pieces must be present. Case, accents, ordinary punctuation and line breaks do not matter; values and labels must still be correct.

The exact rules and accepted alternative spellings are in [checks.json](checks.json). Each `all_of` group must match; any alternative inside that group is accepted.

These few checks measure recovery of selected facts. They do not check every word or catch every invented sentence.

## Actual OCR outputs

**Not run yet.** This example has a photograph and content checks, but no saved parser output or judge result. Expected answers above are not measured results.

## About this photograph

The readable booklet is context, not the washed item. Handwriting on the damaged label is visible, but when it was added is not established. Do not present booklet text or inferred game branding as recovered cartridge print.

Source: [u/Annual_Marsupial3039](https://www.reddit.com/r/gamecollecting/comments/177yav4/whats_the_best_way_to_restore_this_ds_cartridge/)

[How to run an example](../../scripts/README.md)
