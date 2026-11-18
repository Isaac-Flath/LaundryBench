# Datalab parsing

Image → Datalab Convert → Markdown. Accurate mode uses exact transcription, includes headers and footers, and disables generated image captions. The returned text is scored against the parse checks.

Install `pip install -r requirements.txt`, set `DATALAB_API_KEY` in the environment or this folder's `.env`, and run `python run.py`. Use `--image 05` for one document or `--resume` to reuse unchanged predictions. This calls a paid API. Raw responses and input/schema metadata are saved with each prediction.

[Datalab SDK documentation](https://github.com/datalab-to/sdk).
