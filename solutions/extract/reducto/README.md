# Reducto extraction

Image + the model-facing schema → Reducto Extract → JSON. Sends each original photograph directly to extraction, with image context enabled and figure summaries disabled. Citations are disabled so the returned values have the requested schema shape; raw provider responses are still saved. A single-element result list is unwrapped into its one document object. Values are not corrected against test answers.

Install `pip install -r requirements.txt`, set `REDUCTO_API_KEY` in the environment or this folder's `.env`, then run `python run.py`. Use `--image 05` for one document or `--resume` to skip predictions whose image, schema, settings, and output are unchanged. This calls a paid API. It does not require the separate parse runner.

[Extract API reference](https://docs.reducto.ai/api-reference/extract).
