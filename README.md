# LaundryBench

**The only benchmark you can trust for parsing documents that went through the wash.**

My nephew put his copy of *Fox in Socks* in the washing machine. It came out ruined.  There was just enough surviving text among the debris to make out some text. 

I scrambled to figure out how to recover this lost data in a panic.  I checked every OCR benchmark I could find, and there was no category for "machine-washed documents".  How do I know what model to use to read what's left of the text?  😱

This led me to create 2 novel AI benchmarks, `LaundryParseBench` and `LaundryExtractBench`.  If you left your grocery list in your pocket when you washed your clothes, there's now a benchmark to help you choose what OCR model can help you recover it with confidence.

(Ok, but really it's just a good fun educational benchmark.  It will demonstrate a variety of types of tests for both parsing and extraction, and teach you about degraded documents, imputation, and evaluation)

![Benchmark images](_benchmark-images.jpg)

## Run a solution

| Parse | Extract |
| --- | --- |
| [LightOnOCR-3-4B](solutions/parse/lighton/) | [LightOn OCR → Luna → Jev](solutions/extract/luna-jev/) |
| [Datalab](solutions/parse/datalab/) | [Datalab](solutions/extract/datalab/) |

Follow the solution’s setup instructions, then run `python run.py`. Add `--image 05` to try one image. Luna/Jev requires LightOn’s saved OCR; Datalab extraction accepts images directly.

Each solution saves predictions, raw responses, and `scores.json` in its `output/` folder. Model settings live in `run.py`; API keys go in `.env`. Keys and outputs are gitignored.

## Score your own outputs

Run these commands from the repository root with Python 3.10+. The scorers need no dependencies or API keys. Add `--image 05` to score one image.

**Parse:** save unedited OCR as `01.md` through `10.md` (`.txt` and `.html` also work).

```sh
python3 -m scripts.check /path/to/predictions --out /path/to/parse-scores.json
```

**Extract:** give your model each image—or its OCR—and `extract_schema.json`. Save field values as `01.json` through `10.json`. Include every field; use `null` when unavailable. Infer values only where the schema permits it.

```sh
python3 -m scripts.extract /path/to/predictions --out /path/to/extract-scores.json
```

Do not give models the test files: they contain expected answers.

## Data and checks

Each `data/NN-name/` folder contains:

```text
image.jpg              # .jpeg and .png also supported
parse_tests.json       # text and reading-order checks
extract_tests.json     # expected field values
extract_schema.json    # model-facing schema
```

- **Parse:** 34 text checks and 2 local reading-order checks. Matching ignores case, accents, whitespace, ordinary punctuation, Markdown, and HTML. Accepted alternatives are explicit; there is no fuzzy matching. `contains_all` requires every group; `any_of` accepts any alternative within a group.
- **Extract:** 30 field checks, grouped as visible, inferred, or unavailable. Strings must match the whole value after normalization; numbers and booleans must have the correct type. Schema validity is reported separately.

Checks pass or fail, and image scores are averaged with equal weight. These checks cover selected information, not every omission or hallucination. `human_reference` helps locate text and is not scored. Expected answers have not been independently human-reviewed.

To inspect images beside their checks:

```sh
python3 -m scripts.review
```

Open [the review app](http://127.0.0.1:8765/review.html). To change a check, edit its JSON file and reload.

<details>
<summary>Images and sources</summary>

| ID | Image / checks | Source |
| --- | --- | --- |
| 01 | [Fox in Socks — wide view](data/01-nephews-book/) | My nephew 💀 |
| 02 | [Gödel, Escher, Bach](data/02-godel-escher-bach/) | [AlexKo / Alteryx Community](https://community.alteryx.com/en/discussion/426908/finding-a-book-in-my-laundry-an-inspire-nashville-photo-journal) |
| 03 | [Anatomy textbook](data/03-anatomy-textbook/) | [u/Pol_Slattery](https://www.reddit.com/r/Wellthatsucks/comments/m9024o/my_textbook_somehow_made_it_into_my_washing/) |
| 04 | [Letters from a Stoic](data/04-stoic-book/) | [u/gogodboss](https://www.reddit.com/r/mildlyinfuriating/comments/1ukoqxz/i_accidentally_put_my_book_in_the_washing_machine/) |
| 05 | [Pokémon card pinned flat](data/05-pokemon-card/) | [u/rhubarb_thehawlic](https://www.reddit.com/r/Wellthatsucks/comments/1xqsui7/5th_grade_me_accidentally_washed_a_pokemon_card_i/) |
| 06 | [Meathook Massacre II](data/06-meathook-massacre/) | [u/cartmicah3](https://www.reddit.com/r/mtg/comments/1fw9vqq/this_is_what_meathook_massacre_2_looks_like_going/) |
| 07 | [Trading-card pack left in a pocket](data/07-shredded-cards/) | [u/Lipzilla](https://www.reddit.com/r/mtg/comments/129syxr/so_i_just_ruin_a_most_wanted_card_on_accident/) |
| 08 | [Jeans with a washed-out patch](data/08-jeans-label/) | [u/carschap](https://www.reddit.com/r/VintageClothing/comments/xyrs37/rmildlyinfuriating_washed_these_one_time_and_the/) |
| 09 | [Banknotes shredded in the wash](data/09-banknotes/) | [u/BocceBurger](https://www.reddit.com/r/mildlyinfuriating/comments/tyoljy/i_accidentally_washed_10/) |
| 10 | [Game cartridge with its label washed away](data/10-game-cartridge/) | [u/Annual_Marsupial3039](https://www.reddit.com/r/gamecollecting/comments/177yav4/whats_the_best_way_to_restore_this_ds_cartridge/) |

</details>

## Contribute

Anyone can open a pull request:

- **Data:** Put something with text through the wash, photograph what survives, and add it under `data/NN-name/` with the three JSON files shown above. Keep some text readable and add a few useful, visually verifiable checks. Add your photo credit to the source table.
- **Solutions:** Add a parsing or extraction implementation under `solutions/parse/` or `solutions/extract/`. Include runnable code, dependencies, setup instructions, and an `.env.example` if it needs API keys. Follow an existing solution’s output format so the scorer can evaluate it.

## Roadmap

More documents, a published baseline, and reproducible leaderboard submissions.
