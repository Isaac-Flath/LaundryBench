"""Datalab solution. Run with --image 01 to try one image."""
import argparse
from dataclasses import asdict
import json
import os
from pathlib import Path
import subprocess
import sys

from dotenv import load_dotenv
from datalab_sdk import DatalabClient, ConvertOptions

SOLUTION = Path(__file__).resolve().parent
BENCHMARK = SOLUTION.parents[2]
MODE = "accurate"


def parse_image(client, image_path, raw_path):
    options = ConvertOptions(
        mode=MODE, output_format='markdown', exact_transcription=True,
        disable_image_captions=True, keep_pageheader_in_output=True,
        keep_pagefooter_in_output=True,
    )
    result = client.convert(image_path, options=options)
    raw_path.write_text(json.dumps(asdict(result), indent=2))
    if not result.success:
        raise RuntimeError(result.error)
    return result.markdown


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', help='Run and score one image ID; omit for all ten')
    args = parser.parse_args()
    load_dotenv(SOLUTION / '.env')
    output_dir = SOLUTION / 'output'
    (output_dir / 'raw').mkdir(parents=True, exist_ok=True)
    (output_dir / 'scores.json').unlink(missing_ok=True)
    client = DatalabClient(api_key=os.environ["DATALAB_API_KEY"])
    for image_path in sorted((BENCHMARK / 'data').glob('*/image.*')):
        image_id = image_path.parent.name.split('-', 1)[0]
        if args.image and image_id != args.image:
            continue
        print(f'Processing {image_id}', flush=True)
        text = parse_image(client, image_path, output_dir / 'raw' / f'{image_id}.json')
        (output_dir / f'{image_id}.md').write_text(text, encoding='utf-8')
    command = [sys.executable, '-m', 'scripts.check', str(output_dir),
               '--out', str(output_dir / 'scores.json')]
    if args.image:
        command += ['--image', args.image]
    subprocess.run(command, cwd=BENCHMARK, check=True)


if __name__ == '__main__':
    main()
