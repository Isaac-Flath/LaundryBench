# Luna extraction with Jev verification

Saved LightOn OCR → numbered lines → Luna values and citations → Jev verification. Luna extracts values using the image’s schema and cites supporting lines. The script checks that quotations exist; Jev checks whether they support each value.

Verification uses OCR text and flags values below a 0.5 support probability. Extracted values are scored unchanged, with citations and verification saved separately.

This folder is the LightOn-based custom pipeline. Run LightOn parsing first, then install these requirements, set `OPENAI_API_KEY` and `TYPESAFE_API_KEY`, and run `python run.py`. `--ocr-dir` and `--output-dir` allow explicit alternate inputs and destinations; the [Tesseract wrapper](../tesseract-luna-jev/) uses those options to keep its results separate. `--resume` checks image, schema, OCR, and settings before reusing a completed run.
