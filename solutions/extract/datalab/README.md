# Datalab extraction

Image + schema → Datalab Extract → JSON values, citations, and verification. Each image is sent directly to extraction; Datalab handles parsing internally. Both parsing and extraction use accurate mode. Field values are scored against the extraction checks, with citations and verification preserved in the raw response.

Install `pip install -r requirements.txt`, set `DATALAB_API_KEY` in the environment or this folder's `.env`, and run `python run.py`. Use `--image 05` for one document or `--resume` to reuse unchanged predictions. This calls a paid API. Raw responses and input/schema metadata are saved with each prediction.

[Datalab SDK documentation](https://github.com/datalab-to/sdk).
