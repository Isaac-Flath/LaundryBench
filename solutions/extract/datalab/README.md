# Datalab extraction

Adapts the course’s Datalab approach: accurate parsing plus accurate extraction with verification and phrase citations. Sends each image and its schema directly to extraction; Datalab handles parsing internally. The scored JSON contains field values; citations and verification metadata stay in the raw response. Missing fields remain missing.

From this folder, with Python 3.12+:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Fill in .env, then:
python run.py
```

`python run.py --image 05` processes and scores only that image. Only `DATALAB_API_KEY` goes in `.env`; settings are constants in `run.py`. `.env` is loaded from this folder; existing environment variables take precedence. Rerunning replaces the selected predictions and `output/scores.json`.

`output/01.json` through `output/10.json` are scored predictions. `output/raw/` keeps provider responses or intermediate OCR files. `output/scores.json` contains per-check results and the aggregate score. `.env`, `.venv/`, and `output/` stay local and are ignored by Git.

[Course implementation](https://github.com/Isaac-Flath/pdf-to-production/blob/main/kyc_pipeline/extract_datalab.py).
