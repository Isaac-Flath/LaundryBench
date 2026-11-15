# LaundryParseBench

**The only benchmark you can trust for parsing documents that went through the wash.**

My nephew put his copy of *Fox in Socks* in the washing machine. It came out ruined: a wrinkled cover, a pile of paper pulp, and just enough surviving text to make me wonder what an OCR model could recover.

It was also a useful reminder about degraded documents. Some text is hard to read. Some is physically gone. A good parser needs to recover what survives and recognize where the evidence ends—even when it recognizes the book.

Most of us have accidentally washed something we meant to keep: a grocery list left in a pocket, a receipt, a few bills. LaundryParseBench takes that familiar mistake seriously, starting with ten images of books, cards, labels, and money after a wash.

![All ten images](previews/contact-sheet.jpg)

## Start with a photograph

Open [my nephew’s book](examples/01-nephews-book/README.md). You can see the image, the three facts we check, actual Gemini and Datalab outputs, and what an image-based judge says about them. Read the outputs against the photo—the point is to inspect what happened.

| ID | Example | What you can inspect |
| --- | --- | --- |
| 01 | [Fox in Socks — wide view](examples/01-nephews-book/README.md) | Checks + real OCR outputs + judge comparison |
| 02 | [Gödel, Escher, Bach](examples/02-godel-escher-bach/README.md) | Checks ready; not run yet |
| 03 | [Anatomy textbook](examples/03-anatomy-textbook/README.md) | Checks ready; not run yet |
| 04 | [Letters from a Stoic](examples/04-stoic-book/README.md) | Checks ready; not run yet |
| 05 | [Pokémon card pinned flat](examples/05-pokemon-card/README.md) | Checks ready; not run yet |
| 06 | [Meathook Massacre II](examples/06-meathook-massacre/README.md) | Checks ready; not run yet |
| 07 | [Trading-card pack left in a pocket](examples/07-shredded-cards/README.md) | Checks ready; not run yet |
| 08 | [Jeans with a washed-out patch](examples/08-jeans-label/README.md) | Checks ready; not run yet |
| 09 | [Banknotes shredded in the wash](examples/09-banknotes/README.md) | Checks ready; not run yet |
| 10 | [Game cartridge with its label washed away](examples/10-game-cartridge/README.md) | Checks ready; not run yet |

## What is a “test” here?

A test is a small question about recoverable content. On the jeans label, for example: **did the output recover waist 36 and length 34?** A table, a sentence or `W36 L34` can all pass. Swapping the values fails.

Each photograph has only two or three such checks, 26 in total. A pass says that fact was recovered; it does not certify the whole output. The separate image-based judge compares two actual outputs, including omitted text and unsupported guesses, then explains its preference. Its reasons are there for you to inspect too.

The nephew photo is the worked example. The other nine have visible-text checks but no saved model runs yet. This is a small learning collection, with no claim of a comprehensive model ranking.

## How to read an example

1. **Open its `README.md`.** The photograph, checks and available results are together on that page.
2. **Read `outputs/gemini.md` or `outputs/datalab.md`** for an unedited model answer. A `.md` file is just text with lightweight formatting.
3. **Open `checks.json` only if you want the exact matching rules.** It contains the same expected facts shown in the page’s table. It is data, not another set of model outputs.
4. **Read the judge’s explanation on the page.** Its raw responses are under `comparison/` if you want the details.

The [prompts](prompts/README.md) are the instructions sent to models. They do not create the expected answers. The [scripts](scripts/README.md) run OCR, check saved answers, compare outputs and assemble the pages. You can understand the examples without reading or running any Python.

`manifest.json` records image filenames, sources and hashes; `previews/` contains the contact sheet. Neither is needed to read an individual example.

The content checks were selected by visual inspection with an assistant, not independently adjudicated by a human. Each check includes where to look in the photograph so you can disagree with it or improve it.

## Image rights

This repository is private. The nine online images remain third-party material; no redistribution license has been verified. Attribution and source links are recorded for every file. Inclusion does not grant permission to republish the photographs. The supplied nephew photograph has no public license specified either.
