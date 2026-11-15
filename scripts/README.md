# Run one example

Start with an [example page](../examples/01-nephews-book/README.md). It shows the image, the checks, and any actual results. You only need these scripts if you want to reproduce or extend it.

## Check a saved output

From the repository root, using Python 3.10 or later:

```sh
python3 -m scripts.check --image 01 --parser gemini
```

This reads `examples/01-nephews-book/outputs/gemini.md` and checks it against that folder’s `checks.json`. It prints a pass or miss for each question. It makes no API calls. Change `--parser` to `datalab` to inspect the other saved output.

A pass means that selected piece of content was found. Three passes out of three do **not** mean the whole transcription is correct. Case, accents, ordinary punctuation, line breaks, Markdown and HTML are normalized. Simple tables preserve label/value associations. Numbers remain exact; there is no fuzzy matching. Arbitrary paraphrases and complex nested tables may need additional explicit aliases.

Each row has equal weight within a photograph. If you later run all ten, each incident has equal weight in the average. Missing outputs cause an error; an empty output is a valid empty file. Omit `--image` to check all ten once they have outputs. Add `--out reports/content.json` to save the report.

## Get an actual OCR output

The committed nephew example uses the original photograph without cropping or resizing. Both outputs are unedited. For a new example, set the relevant API key in your environment and run:

```sh
uv run --with requests python -m scripts.read_image --image 02 --parser gemini --model gemini-3.5-flash
uv run --with requests python -m scripts.read_image --image 02 --parser datalab
```

These send the image to the provider and use API quota. Gemini reads `GEMINI_API_KEY` or `GOOGLE_API_KEY`; Datalab reads `DATALAB_API_KEY`. Existing outputs are never overwritten. The commands save the answer and its settings beside the example. Preserve the old output before rerunning it.

Gemini gets the [reading prompt](../prompts/read-image.txt). Datalab uses accurate mode, exact transcription, and no synthetic image captions or extracted images. Those are different approaches to the same photo, not identical configurations. The [Datalab API reference](https://www.datalab.to/redoc) and [Gemini API reference](https://ai.google.dev/api/generate-content) describe their request formats. Requested and reported model versions are recorded separately because aliases can resolve to a different version.

For another parser, save its text as `outputs/my-parser.md` inside the example folder, then use `--parser my-parser`. Keep its settings alongside it. Supply only the image and reading instructions to the parser, never the expected answers or source story.

## Ask the judge to compare two outputs

```sh
python3 -m scripts.compare --image 01 --candidate gemini --baseline datalab \
  --model gemini-3.5-flash --out reports/nephew-comparison
```

This makes two API requests: one per A/B order. Both contain the same photograph and saved outputs. It uses an adaptation of Reducto’s [PAIR approach](https://reducto.ai/blog/pairwise-ai-ranking-parse-evaluation), with [instructions for damaged documents](../prompts/compare-outputs.txt). This is our example implementation, not Reducto’s official scorer.

The judge considers useful recovered information, incorrect values, omissions and unsupported guesses. Cosmetic formatting does not determine the winner. Read its reasons against the image; its verdict is another model’s opinion. It may be wrong, and using Gemini to judge a Gemini output can introduce bias.

`--dry-run` prints the plan without calling the API. The output directory must be new. `--rounds 2` repeats both orders. Wins are 1, ties 0.5 and losses 0; that relative score is separate from the content checks. A missing, malformed or unjudgeable response prevents a complete score. The directory retains both anonymous orderings, raw responses, prompt, model versions and hashes.

## Update the readable pages

```sh
python3 -m scripts.build_pages
```

This rebuilds each example’s `README.md` from its checks and saved outputs. To display a judge run on that page, keep the run in the example’s `comparison/` directory. Add human observations in `NOTES.md`; the page includes them too. This command makes no API calls.

## The code

| File | Job |
| --- | --- |
| `check.py` | Match saved OCR text against the image’s few content checks. |
| `read_image.py` | Call a parser and save its actual answer. |
| `compare.py` | Show the image and two answers to the judge in both orders. |
| `build_pages.py` | Put the saved data into readable example pages. |
| `common.py` | Locate images and outputs, verify image hashes, and write JSON. |

There is no software-test suite or synthetic calibration dataset in this learning example. Earlier versions had both; Git history preserves them.
