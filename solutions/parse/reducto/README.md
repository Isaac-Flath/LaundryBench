# Reducto parsing

Image → Reducto Parse → Markdown. Uploads the original photograph, disables figure summaries, and joins the returned chunks without rewriting their content. Other parsing settings use the service defaults, so raw responses and run dates matter when comparing later runs.

Install `pip install -r requirements.txt`, set `REDUCTO_API_KEY` in the environment or this folder's `.env`, then run `python run.py`. Use `--image 05` for one document or `--resume` to skip unchanged saved predictions. This calls a paid API.

[Parse API reference](https://docs.reducto.ai/api-reference/parse).
