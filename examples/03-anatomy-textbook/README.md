# 03 · Anatomy textbook

[← All examples](../../README.md)

![Anatomy textbook](image.jpg)

## What are we checking?

Readable body-text fragments and headings on crumpled pages; many folds and missing regions.

These are the visible facts we want an OCR output to recover. Each row is one check. These answers were selected by inspecting the photograph; they are not model-generated reference transcripts.

| Check | Expected content | Where to look |
| --- | --- | --- |
| Which bone is named in the heading? | Sphenoid | Heading under the skull figures, left exposed page. |
| Which section heading follows it? | Anatomy | The next heading on the same exposed page. |

The table shows the expected facts, not required formatting. **And** means both pieces must be present. Case, accents, ordinary punctuation and line breaks do not matter; values and labels must still be correct.

The exact rules and accepted alternative spellings are in [checks.json](checks.json). Each `all_of` group must match; any alternative inside that group is accepted.

These few checks measure recovery of selected facts. They do not check every word or catch every invented sentence.

## Actual OCR outputs

**Not run yet.** This example has a photograph and content checks, but no saved parser output or judge result. Expected answers above are not measured results.

## About this photograph

Subject identified by the author as a guide to the human skeleton.

Source: [u/Pol_Slattery](https://www.reddit.com/r/Wellthatsucks/comments/m9024o/my_textbook_somehow_made_it_into_my_washing/)

[How to run an example](../../scripts/README.md)
