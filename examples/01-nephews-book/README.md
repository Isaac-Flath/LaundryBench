# 01 · Fox in Socks — wide view

[← All examples](../../README.md)

![Fox in Socks — wide view](image.jpeg)

## What are we checking?

Surviving cover titles and publisher text amid detached paper pulp.

These are the visible facts we want an OCR output to recover. Each row is one check. These answers were selected by inspecting the photograph; they are not model-generated reference transcripts.

| Check | Expected content | Where to look | datalab | gemini |
| --- | --- | --- | --- | --- |
| Which publisher imprint is visible? | Beginner Books | Red lettering in the central panel. | Pass | Pass |
| Which title is on the upper-left blue cover? | The Cat in the Hat | Small blue cover; all six words are visible. | Pass | Pass |
| Which title is on the yellow cover? | One fish two fish red fish blue fish | Four stacked lines on the small yellow cover. | Pass | Pass |

The table shows the expected facts, not required formatting. **And** means both pieces must be present. Case, accents, ordinary punctuation and line breaks do not matter; values and labels must still be correct.

The exact rules and accepted alternative spellings are in [checks.json](checks.json). Each `all_of` group must match; any alternative inside that group is accepted.

These few checks measure recovery of selected facts. They do not check every word or catch every invented sentence.

## Actual OCR outputs

### datalab: 3/3 checks passed

[Open the unedited output](outputs/datalab.md) · [Run settings](outputs/datalab-settings.json)

Datalab Convert, accurate mode. The request enabled exact transcription and disabled image captions and extraction. The returned text still contains scene descriptions; it is preserved as received. No custom reading prompt was sent.

<details>
<summary>Read the full output here</summary>

````text


A photograph showing a white plastic bin filled with a large, crumpled yellow plastic bag. The bag is covered in several Dr. Seuss stickers, including "The Cat in the Hat", "Beginner Books", "One fish two fish red fish blue fish", "Oh, San, can you say?", and "The Cat in the Hat Comes Back". The bag is also covered in a large, white, knotted toy, possibly a rope or a plush. The bin is filled with other debris, including a white plastic bag with a barcode and some dark, crumpled material. The background shows a white surface with scattered brown debris.

The image shows a white plastic bin filled with a large, crumpled yellow plastic bag. The bag is covered in several Dr. Seuss stickers, including "The Cat in the Hat", "Beginner Books", "One fish two fish red fish blue fish", "Oh, San, can you say?", and "The Cat in the Hat Comes Back". The bag is also covered in a large, white, knotted toy, possibly a rope or a plush. The bin is filled with other debris, including a white plastic bag with a barcode and some dark, crumpled material. The background shows a white surface with scattered brown debris.

The stickers on the bag include:

The bag also has some text: "Launched by Dr. Seuss in 1957 with The Cat in the Hat. BEGINNER BOOKS are made for children learning to read all the letters. Fun, funny, and easy to read. There are more than 50 classic and new titles to choose from."

A crumpled, yellow plastic bag with several Dr. Seuss book stickers and a central text block. The stickers include "THE CAT IN THE HAT" (blue), "Beginner Books" (circular with the Cat in the Hat), "Knox in Socks" (orange), "One fish, two fish, red fish, blue fish" (yellow), "Oh, say can you say?" (red), "Ten Apples Up O' Apple" (green), and "THE CAT IN THE HAT COMES BACK" (blue). The central text block reads: "When a fox in socks meets Knox in a box, lips will get locked and tongues tied in knots. CONSIDER YOURSELF WARNED! Launched by Dr. Seuss in 1967 with The Cat in the Hat. BEGINNER BOOKS are made for everyone. Learning to read, learning to read, silly games, fun, family, and easy to read. There are more than 50 classic and new titles to choose from." A small label at the bottom right says "MANUFACTURED IN CHINA".

**THE CAT IN THE HAT**  
by Dr. Seuss

**Beginner Books**  
Knox in Socks  
When a fox in socks meets Knox in a box, lips will get locked and tongues tied in knots.  
**CONSIDER YOURSELF WARNED!**  
Launched by Dr. Seuss in 1967 with *The Cat in the Hat*.  
**BEGINNER BOOKS** are made for everyone. Learning to read, learning to read, silly games, fun, family, and easy to read. There are more than 50 classic and new titles to choose from.

**One fish, two fish, red fish, blue fish**

**Oh, say can you say?**  
by Dr. Seuss  
Oh, in my book,  
The cat in  
THE CAT IN THE HAT  
by Dr. Seuss

**Ten Apples Up O' Apple**  
by Dr. Seuss

**THE CAT IN THE HAT COMES BACK**  
by Dr. Seuss

Random House  
2-99 CAN  
60344400

star dr seuss  
MANUFACTURED IN CHINA

**THE CAT IN THE HAT**  
by Dr. Seuss

CAN READ IT ALL BY MYSELF  
**Beginner Books**

by Dr. Seuss  
One fish  
two fish  
red fish  
blue fish

**Fox in Socks**  
When a fox in socks tumbles  
Knox in a box, lips will get locked  
and tongues tied in knots.  
**CONSIDER YOURSELF WARNED!**

Launched by Dr. Seuss  
in 1957 with  
*The Cat in the Hat*.  
**BEGINNER BOOKS**

are made for children on  
learning to read  
all the new ideas.  
Fun, funny, and  
easy to read.  
There are more than  
50 classic and new titles  
to choose from.

**THE CAT IN THE HAT  
COMES BACK**  
by Dr. Seuss

Fox in Socks

Dr. Seuss

Oh,  
san  
can  
you  
say?  
by Dr. Seuss  
Illustrated by  
MARTIN REED TWINTER

2-99 CAN  
MANUFACTURED IN CHINA
````

</details>

### gemini: 3/3 checks passed

[Open the unedited output](outputs/gemini.md) · [Run settings](outputs/gemini-settings.json)

Requested `gemini-3.5-flash`; the API reported `gemini-3.6-flash`.

<details>
<summary>Read the full output here</summary>

````text
**Yellow Plastic Packaging**

* **Top-Left Cover (Blue):**
  * Title: `THE CAT IN THE HAT`
  * Author: `By Dr. Seuss`

* **Top-Center Logo:**
  * Outer ring: `I CAN READ IT ALL BY MYSELF`
  * Banner: `Beginner Books`

* **Top-Right Cover (Orange):**
  * Title: `Green Eggs and Ham`
  * Author: `By Dr. Seuss`

* **Middle-Left Cover (Yellow):**
  * Author: `By Dr. Seuss`
  * Text: `One fish`, `two fish`, `red fish`, `blue fish`

* **Center Text Block:**
  * Title: `Fox in Socks`
  * Text: 
    > `When a Fox in socks meets Knox in a box, lips get locked and tongues get tied in knots.`  
    > `CONSIDER YOURSELF WARNED!`  
    > `Launched by Dr. Seuss in 1957 with The Cat in the Hat,`  
    > `BEGINNER BOOKS`  
    > `are made with simple words, clear pictures, and fun story lines easy to read. Today, there are more than 50 classic and new titles to choose from.`

* **Middle-Right Cover (Green):**
  * Title: `Ten Apples Up On Top!`
  * Author: `[unreadable]`

* **Bottom-Left Cover (Pink):**
  * Title: `Oh Say Can You Say?`
  * Author: `By Dr. Seuss`

* **Bottom-Right Cover (Blue):**
  * Title: `THE CAT IN THE HAT COMES BACK`
  * Author: `By Dr. Seuss`

* **Right Edge Text:**
  * `Fox in Socks`
  * `Dr. Seuss`

* **Bottom Markings:**
  * Logo: `dr. seuss enterprises`
  * Text: `MANUFACTURED IN CHINA`
  * Barcode: `0 38334 [unreadable]`

---

**Clothing Tag (inside laundry basket, left side)**

* Partial text: `[unreadable]/2A` / `[unreadable] CN`
````

</details>

## What did the image-based judge say?

The judge saw the photograph and the two outputs, labeled A and B. Parser names were hidden. We reversed their order and asked again. Candidate: **gemini**; baseline: **datalab**.

| Order | A | B | Judge chose |
| --- | --- | --- | --- |
| 1 | gemini | datalab | gemini |
| 2 | datalab | gemini | gemini |

The explanations below are the judge’s claims. Compare them with the photograph yourself.

**Order 1:** Model A is exceptionally accurate, well-structured, and faithfully transcribes both the text on the yellow plastic label and the clothing tag in the basket. Model B contains severe hallucinations, repeated text sections, and incorrect readings.

- Model A accurately transcribes the central text block ('When a Fox in socks meets Knox in a box, lips get locked and tongues get tied in knots. CONSIDER YOURSELF WARNED!...').
- Model A correctly identifies the top-right book title ('Green Eggs and Ham') and middle-right book title ('Ten Apples Up On Top!').
- Model B hallucinates numerous phrases throughout its output (e.g., 'Oh, San, can you say?', 'Ten Apples Up O' Apple', '1967', 'silly games', 'MARTIN REED TWINTER').
- Model B includes long conversational/descriptive text and repeats transcriptions multiple times with varying errors.

**Order 2:** Parse B is exceptionally clean, well-structured, and accurate to the visible pixels on the packaging. Parse A contains multiple repeated paragraphs, hallucinated text, and misidentified titles.

- Parse B correctly transcribes the top-right orange book cover title as 'Green Eggs and Ham', whereas Parse A misidentifies it as 'Knox in Socks'.
- Parse B correctly captures the top logo circular text 'I CAN READ IT ALL BY MYSELF'.
- Parse A repeats the entire description and transcription multiple times with hallucinatory variations (e.g. 'MARTIN REED TWINTER').
- Parse B accurately extracts readable details from the surrounding clothing tags (e.g. '/2A').

Judge API reported: gemini-3.6-flash. Gemini also produced one of the parses, so this is a worked example, not an independent ranking of vendors.

[Judge instructions](../../prompts/compare-outputs.txt) · [Recorded requests and responses](comparison/)

## What to notice

Both outputs pass all three content checks. That does not make either a perfect transcription.

Datalab repeats the central paragraph with different wording and conflicting dates: one passage says 1967, another says 1957. Our three checks concern the publisher and two small cover titles, so they cannot catch that contradiction. Its response also contains scene descriptions even though the request disabled synthetic image captions. The saved output retains them.

Gemini also fills in a substantial central paragraph. Read it against the wrinkled lettering instead of treating fluent text as proof that it was visible. The content checks do not assess that whole paragraph.

This is what the second method adds: the judge can discuss errors outside the three selected facts. Its explanation is still a model output, so the photograph remains the evidence.

The judge preferred Gemini in both orders and called it “exceptionally accurate.” That is the judge’s assessment, not an independently verified transcription. It did not establish that every word of Gemini’s central paragraph is supported by the photograph.

## About this photograph

Original wide photograph supplied in this chat.

Source: My nephew 💀

[How to run an example](../../scripts/README.md)
