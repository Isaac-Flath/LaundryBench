# Prompts

- **[read-image.txt](read-image.txt)** is sent with a photograph to Gemini. Gemini’s answer becomes an actual OCR output, saved under that example’s `outputs/` folder. Datalab uses its own conversion pipeline and settings instead.
- **[compare-outputs.txt](compare-outputs.txt)** is sent with a photograph and two actual OCR outputs. The judge returns its preference and reasons. It does not generate a reference transcription.

Neither prompt creates the expected answers. Those live in each example’s `checks.json` and were chosen by inspecting the photograph. The readable example pages are built from saved data by `scripts/build_pages.py`; no model writes those pages.
