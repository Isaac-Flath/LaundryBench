# LightOn parsing

Image → Markdown with [LightOnOCR-3-4B](https://huggingface.co/lightonai/LightOnOCR-3-4B). Requires Python 3.12 and an NVIDIA GPU with room for the 4B model in BF16. The included attention kernels use Triton.

From this folder:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Add `--image 05` to run one image. No API keys are needed. The model, pinned revision, and token limit are constants in `run.py`. Images are rotated using EXIF and resized to at most 2048 pixels on their longest side. Generation uses the model's image-only transcription prompt and greedy decoding.

Results: `output/NN.md`, generation metadata in `output/raw/`, and `output/scores.json`. Outputs are gitignored. The benchmark run used an H100 GPU.
