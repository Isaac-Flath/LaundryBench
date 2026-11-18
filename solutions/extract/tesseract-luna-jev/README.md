# Tesseract → Luna → Jev

Saved Tesseract OCR → numbered lines → Luna extraction and citations → Jev verification. This reuses the [Luna/Jev implementation](../luna-jev/), but reads Tesseract output and writes to its own output folder. Historical LightOn-based outputs remain separate.

Run `python3 solutions/parse/tesseract/run.py` from the repository root first. Then install this folder's requirements, set `OPENAI_API_KEY` and `TYPESAFE_API_KEY` in your environment, and run `python run.py` here. `--image 05` selects one document; `--resume` skips unchanged completed runs.

Tesseract is local and lightweight; Luna and Jev still call paid APIs. Extraction receives OCR text only, so it cannot recover visual evidence that Tesseract missed. Jev flags support issues without changing Luna's predictions or benchmark scores. Nulls and empty lists are not independently verified.
