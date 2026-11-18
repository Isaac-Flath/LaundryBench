# Tesseract parsing

Image → Tesseract → text, using CPU only. One pass over the original photograph with English (`eng`), the LSTM engine (`--oem 1`), and sparse-text segmentation (`--psm 11`). No cropping, rotations, LLM correction, or per-image tuning. Sparse mode does not promise reading order, so the order checks can expose that limitation.

Install Tesseract 5 with English language data (macOS: `brew install tesseract`; Debian/Ubuntu: `sudo apt install tesseract-ocr tesseract-ocr-eng`). This runner needs only Python's standard library. Run `python3 run.py`; use `--image 05` for one document or `--resume` to reuse unchanged predictions. The installed Tesseract version and settings are recorded with each result.

This is the lightweight custom baseline, not a replacement name for historical LightOn results. See the [Tesseract command-line documentation](https://tesseract-ocr.github.io/tessdoc/Command-Line-Usage.html).
