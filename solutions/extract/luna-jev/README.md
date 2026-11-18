# Luna extraction with Jev verification

Image → LightOnOCR-3-4B → numbered OCR lines → Luna values and citations → Jev verification. Luna extracts values using the image’s schema and cites supporting lines. The script checks that quotations exist; Jev checks whether they support each value.

Verification uses OCR text and flags values below a 0.5 support probability. Extracted values are scored unchanged, with citations and verification saved separately.

Install this folder’s requirements (including LightOn inference dependencies), set `OPENAI_API_KEY` and `TYPESAFE_API_KEY`, and run `python run.py` on suitable model-inference hardware. This runs the complete pipeline from source images; no prior parsing run is needed. Use `--image 05` for one image or `--output-dir` for a different destination. OCR intermediates are saved under `output/ocr/` and extracted values under `output/`.

A normal run reruns every stage. `--resume` reuses OCR only when the image, parser settings, and saved output match; extraction is reused only when the image, schema, OCR, extraction settings, and saved prediction match. The [Tesseract pipeline](../tesseract-luna-jev/) shares extraction code but has its own OCR and outputs.
