# Luna extraction with Jev verification

LightOn OCR → numbered lines → Luna values and citations → Jev evidence checks. Run [the parser](../../parse/lighton/) first. This follows the extraction-and-verification approach in [PDF to Production](https://github.com/Isaac-Flath/pdf-to-production/blob/main/kyc_pipeline/extract_scratch.py), without page classification or retrieval for these single-image documents.

From this folder:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add OPENAI_API_KEY and TYPESAFE_API_KEY to .env.
python run.py
```

Add `--image 05` to run one image. Models and the verification threshold are constants in `run.py`.

Luna receives the OCR and `extract_schema.json`, never the test answers. Each non-null value includes line IDs and quotations. The script checks that quotations exist, then asks Jev whether they support the value. Support probabilities of at least 0.5 mark a value verified; other values are flagged. Null values are marked missing. Verification checks the OCR evidence, not the original pixels, and does not change extracted values or benchmark scores.

Results: `output/NN.json` and `output/scores.json`. `output/raw/` contains the OCR, model requests and responses, citations, and verification decisions. Credentials and outputs are gitignored.
