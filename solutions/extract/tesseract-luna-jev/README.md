# Tesseract → Luna → Jev

Image → Tesseract → numbered OCR lines → Luna extraction and citations → Jev verification. This shares the Luna/Jev extraction code with the [LightOn pipeline](../luna-jev/) and runs its own OCR from source images.

Install Tesseract 5 with English language data (`brew install tesseract` on macOS, or `sudo apt install tesseract-ocr tesseract-ocr-eng` on Debian/Ubuntu) and this folder’s Python requirements. Set `OPENAI_API_KEY` and `TYPESAFE_API_KEY`, then run `python run.py` here. No prior parsing run is needed. `--image 05` selects one document; `--output-dir` changes the destination. OCR intermediates are saved under `output/ocr/` and extracted values under `output/`.

A normal run reruns every stage. `--resume` checks the image and parser settings before reusing OCR, then checks the schema, OCR, extraction settings, and saved prediction before reusing extraction.

Tesseract is local and lightweight; Luna and Jev still call paid APIs. Extraction receives OCR text only, so it cannot recover visual evidence that Tesseract missed. Jev flags support issues without changing Luna's predictions or benchmark scores. Nulls and empty lists are not independently verified.
