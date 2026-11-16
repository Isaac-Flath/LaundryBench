# Datalab

Datalab Convert in accurate mode, with exact transcription, headers and footers included, and generated image captions disabled.

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

`output/01.md` through `output/10.md` are scored predictions. `output/raw/` keeps provider responses or intermediate OCR files. `output/scores.json` contains per-check results and the aggregate score. `.env`, `.venv/`, and `output/` stay local and are ignored by Git.

[API / tool reference](https://documentation.datalab.to/docs/welcome/sdk/overview).
