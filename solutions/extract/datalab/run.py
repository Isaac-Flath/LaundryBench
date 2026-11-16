"""Datalab extraction solution. Run with --image 01 to try one image."""
import argparse
from dataclasses import asdict
import json
import os
from pathlib import Path
import subprocess
import sys

from dotenv import load_dotenv
from datalab_sdk import DatalabClient, ExtractOptions

SOLUTION = Path(__file__).resolve().parent
BENCHMARK = SOLUTION.parents[2]
PARSE_MODE = "accurate"
EXTRACT_MODE = "accurate"


def extract_values(client, image_path, schema, raw_path):
    options = ExtractOptions(
        page_schema=json.dumps(schema), mode=PARSE_MODE,
        extraction_mode=EXTRACT_MODE, citation_granularity='phrase',
    )
    result = client.extract(image_path, options=options)
    raw_path.write_text(json.dumps(asdict(result), indent=2))
    if not result.success:
        raise RuntimeError(result.error)
    fields = json.loads(result.extraction_schema_json)
    # Keep provider citations and verification metadata in the raw response only.
    return {name: fields[name] for name in schema['properties'] if name in fields}


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
        schema = json.loads((image_path.parent / 'extract_schema.json').read_text())
        values = extract_values(client, image_path, schema, output_dir / 'raw' / f'{image_id}.json')
        text = json.dumps(values, ensure_ascii=False, indent=2)
        (output_dir / f'{image_id}.json').write_text(text, encoding='utf-8')
    command = [sys.executable, '-m', 'scripts.extract', str(output_dir),
               '--out', str(output_dir / 'scores.json')]
    if args.image:
        command += ['--image', args.image]
    subprocess.run(command, cwd=BENCHMARK, check=True)


if __name__ == '__main__':
    main()
