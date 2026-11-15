# 08 · Jeans with a washed-out patch

[← All examples](../../README.md)

![Jeans with a washed-out patch](image.jpg)

## What are we checking?

Inner baggy pleated and silverTab labels remain readable beside the almost blank back patch.

These are the visible facts we want an OCR output to recover. Each row is one check. These answers were selected by inspecting the photograph; they are not model-generated reference transcripts.

| Check | Expected content | Where to look |
| --- | --- | --- |
| What fit is printed on the inner label? | baggy pleated | Large lettering on the black inner label. |
| Which brand line is on that label? | silverTab | Logo to the right of the fit. |
| What waist and length are printed? | W36 **and** L34 | Small pale tag below the inner label: W36 L34. |

The table shows the expected facts, not required formatting. **And** means both pieces must be present. Case, accents, ordinary punctuation and line breaks do not matter; values and labels must still be correct.

The exact rules and accepted alternative spellings are in [checks.json](checks.json). Each `all_of` group must match; any alternative inside that group is accepted.

These few checks measure recovery of selected facts. They do not check every word or catch every invented sentence.

## Actual OCR outputs

**Not run yet.** This example has a photograph and content checks, but no saved parser output or judge result. Expected answers above are not measured results.

## About this photograph

Readable text is on the surviving labels; do not infer the vanished back-patch lettering.

Source: [u/carschap](https://www.reddit.com/r/VintageClothing/comments/xyrs37/rmildlyinfuriating_washed_these_one_time_and_the/)

[How to run an example](../../scripts/README.md)
