"""Transcribe each image with LightOnOCR-3-4B, then score the saved Markdown."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from PIL import Image, ImageOps
import torch
from transformers import AutoProcessor, Qwen3_5ForConditionalGeneration

SOLUTION = Path(__file__).resolve().parent
BENCHMARK = SOLUTION.parents[2]
MODEL = "lightonai/LightOnOCR-3-4B"
REVISION = "b71010f095dc3735de7ee6b9969bff8f8f50b39a"
MAX_NEW_TOKENS = 4096
MAX_IMAGE_SIDE = 2048


def transcribe_image(image_path, model, processor):
    with Image.open(image_path) as image:
        image = ImageOps.exif_transpose(image).convert('RGB')
        image.thumbnail((MAX_IMAGE_SIDE, MAX_IMAGE_SIDE))
    # Image only is LightOn's transcription prompt; "grounding" also adds descriptions.
    conversation = [{'role': 'user', 'content': [{'type': 'image', 'image': image}]}]
    inputs = processor.apply_chat_template(
        conversation, add_generation_prompt=True, tokenize=True,
        return_dict=True, return_tensors='pt', enable_thinking=False,
    ).to(model.device)
    with torch.inference_mode():
        output = model.generate(**inputs, max_new_tokens=MAX_NEW_TOKENS, do_sample=False)
    generated = output[0, inputs['input_ids'].shape[1]:]
    text = processor.decode(generated, skip_special_tokens=True)
    return text, len(generated)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', help='Run and score one image ID; omit for all ten')
    args = parser.parse_args()
    model = Qwen3_5ForConditionalGeneration.from_pretrained(
        MODEL, revision=REVISION, dtype=torch.bfloat16, device_map='auto',
    ).eval()
    processor = AutoProcessor.from_pretrained(MODEL, revision=REVISION)
    output_dir = SOLUTION / 'output'
    (output_dir / 'raw').mkdir(parents=True, exist_ok=True)
    (output_dir / 'scores.json').unlink(missing_ok=True)
    for image_path in sorted((BENCHMARK / 'data').glob('*/image.*')):
        image_id = image_path.parent.name.split('-', 1)[0]
        if args.image and image_id != args.image:
            continue
        print(f'Transcribing {image_id}', flush=True)
        text, token_count = transcribe_image(image_path, model, processor)
        (output_dir / f'{image_id}.md').write_text(text, encoding='utf-8')
        metadata = {'model': MODEL, 'revision': REVISION, 'device': str(model.device),
                    'max_image_side': MAX_IMAGE_SIDE, 'max_new_tokens': MAX_NEW_TOKENS,
                    'generated_tokens': token_count, 'hit_token_limit': token_count == MAX_NEW_TOKENS}
        (output_dir / 'raw' / f'{image_id}.json').write_text(json.dumps(metadata, indent=2))
    command = [sys.executable, '-m', 'scripts.check', str(output_dir),
               '--out', str(output_dir / 'scores.json')]
    if args.image:
        command += ['--image', args.image]
    subprocess.run(command, cwd=BENCHMARK, check=True)


if __name__ == '__main__':
    main()
