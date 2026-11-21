# LightOn parsing

Image → LightOnOCR-3-4B → Markdown. Images are oriented using EXIF and resized to a maximum side length of 2048 pixels. The model uses an image-only transcription prompt and greedy decoding. The saved text is scored against the parse checks.

Install the pinned dependencies with `pip install -r requirements.txt`, then run `python run.py` on suitable model-inference hardware. Use `--image 05` for one image. Each completed prediction records its image hash, output hash, model revision, settings, and run date for the local results comparison.
