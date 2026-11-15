# 04 · Letters from a Stoic

[← All examples](../../README.md)

![Letters from a Stoic](image.jpeg)

## What are we checking?

Title fragments, SENECA and CAPSTONE survive on a torn, deformed book.

These are the visible facts we want an OCR output to recover. Each row is one check. These answers were selected by inspecting the photograph; they are not model-generated reference transcripts.

| Check | Expected content | Where to look |
| --- | --- | --- |
| Which author is named? | Seneca | SENECA on the main exposed page. |
| Which publisher imprint is named? | Capstone | Logo at the bottom of the exposed page. |
| What readable title phrase survives? | From a Stoic | Only FROM A STOIC is required; missing initial letters are not. |

The table shows the expected facts, not required formatting. **And** means both pieces must be present. Case, accents, ordinary punctuation and line breaks do not matter; values and labels must still be correct.

The exact rules and accepted alternative spellings are in [checks.json](checks.json). Each `all_of` group must match; any alternative inside that group is accepted.

These few checks measure recovery of selected facts. They do not check every word or catch every invented sentence.

## Actual OCR outputs

**Not run yet.** This example has a photograph and content checks, but no saved parser output or judge result. Expected answers above are not measured results.

## About this photograph

Missing letters must stay missing in an image-only transcription.

Source: [u/gogodboss](https://www.reddit.com/r/mildlyinfuriating/comments/1ukoqxz/i_accidentally_put_my_book_in_the_washing_machine/)

[How to run an example](../../scripts/README.md)
