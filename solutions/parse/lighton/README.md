# LightOn parsing

Image → LightOnOCR-3-4B → Markdown. Images are oriented using EXIF and resized to a maximum side length of 2048 pixels. The model uses an image-only transcription prompt and greedy decoding. The saved text is scored against the parse checks.
