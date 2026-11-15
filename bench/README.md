# Evaluation

Two scores answer different questions. Keep them separate.

| Method | What it measures | What it misses |
| --- | --- | --- |
| Content checks | Recovery of 26 useful facts: two or three per photograph. | Unchecked omissions and invented text. This is partial recall. |
| PAIR-style judge | Which of two parses better matches the photograph, including omissions, wrong values and unsupported guesses. | An absolute accuracy score. The judge can still misread the image. |

## Content checks

Read every question, accepted answer and evidence location in [CHECKS.md](CHECKS.md). The machine-readable version is [checks.json](checks.json). The checks were selected by visually inspecting the images before comparing parser outputs. They have been reviewed by the authoring assistant, not independently adjudicated by a human.

We check surviving names, titles, identifiers and values. Missing letters, destroyed text, ambiguous handwriting and details known only from a source story are excluded. Image 10 explicitly checks the booklet beside the cartridge; it does not claim that text survived on the cartridge.

Case, accents, line breaks, ordinary punctuation, Markdown and HTML do not affect matching. Simple tables retain label/value associations: `Waist: 36, Length: 34` and a table containing those values both pass; swapping them fails. Numeric values remain exact. Accepted aliases are explicit, with no fuzzy matching that might excuse an incorrect serial number or amount. Complex nested tables and arbitrary paraphrases are outside this small scorer's supported formats.

Each check is pass/fail. Average checks within each image, then average images: a three-check image has the same weight as a two-check image. If multiple views of one incident are added later, their scores share one incident's weight. The current ten images represent ten different incidents.

A parse can pass every check and still invent an entire paragraph. That is why we also judge the full parse against the image. Do not present content-check recall as overall parsing accuracy.

## Prepare parser outputs

Give each parser the same original image and [parse prompt](parse_prompt.txt), or document a provider's fixed OCR settings. Supply the image bytes without source descriptions, descriptive filenames, expected answers or source pages. Keep preprocessing, model versions and settings with the run. Do not tune the checks to accommodate a particular parser's mistakes.

Save each parser's unedited text output in its own directory as `01.md` through `10.md`. Plain `.txt` and `.html` are also accepted; exactly one file per image is required. An empty parse is an empty file. A missing file is an error, not a skipped example. Convert a provider's response envelope to its text field without rewriting that text.

Run from the repository root with Python 3.10 or later. No Python dependencies are required:

```sh
python3 -m bench.unit runs/parser-a --out reports/parser-a-content.json
```

The report includes every pass/fail result, the checks version and hash, and hashes of the submitted text. Image hashes must match the annotated files before either evaluation runs.

## Image-based pairwise judging

This is an independent adaptation of Reducto's [PAIR approach](https://reducto.ai/blog/pairwise-ai-ranking-parse-evaluation), using the [laundry-specific rubric](pair_prompt.txt) and a configurable Gemini Flash judge. These are not official Reducto scores.

The judge receives the image and two anonymous parses. It considers recovered information, correct associations and unsupported claims. It ignores cosmetic formatting. Each round runs both A/B orders; the default is two rounds, or 40 calls for ten images. A seeded shuffle sets the request order. Candidate wins score 1, ties 0.5, and losses 0. Average within each image, then across incidents. Use the same baseline and judge configuration when comparing candidates.

Set `GEMINI_API_KEY` or `GOOGLE_API_KEY` in your environment. Choose an explicit supported Gemini Flash model ID; the API may resolve an alias to a different version. Both requested and reported versions are saved.

Preview the call plan without making API requests:

```sh
python3 -m bench.pair --candidate runs/parser-a --baseline runs/parser-b \
  --model gemini-3.5-flash --out reports/a-vs-b --dry-run
```

Remove `--dry-run` to evaluate. The output directory must be new. These calls send the images and parses to Google's API and use your account's API quota.

Every judgment saves the anonymous inputs, evidence, rationale and raw response. Run metadata records the prompt, seed, model request and input hashes. The summary reports results by image and A/B position, plus disagreements between swapped-order comparisons. An error, malformed response or `unjudgeable` verdict prevents a complete aggregate score; failures never become ties or disappear from the denominator. Review disagreements before drawing conclusions. Repeated judgments of the same photo are not independent new examples.

A win rate is relative to the chosen baseline. Two equally poor parses can tie. These ten photos are a small diagnostic set, not evidence that a parser works on every damaged document.

## Small, meaningful validation

Run the scorer's offline tests:

```sh
python3 -m unittest discover -s tests -v
```

The tests cover formatting equivalence, incorrect values and associations, hidden metadata, missing outputs, incident weighting, A/B mapping and failed judgments.

Before using a new judge configuration, run the three [calibration controls](calibration.json) in both orders:

```sh
python3 -m bench.pair --calibrate --rounds 1 \
  --model gemini-3.5-flash --out reports/judge-calibration
```

The controls expect a tie for equivalent formatting, prefer correct waist/length values, and reject invented text on a blank patch. They use synthetic parses of image 08. The [recorded run](../validation/pair-calibration-2026-11-15/summary.json) passed all six comparisons. This verifies those controls, not general judge accuracy. No parser leaderboard has been run or claimed.
