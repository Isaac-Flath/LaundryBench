"""Upload each photograph to Reducto Parse and score its returned text."""
import argparse
import os
from pathlib import Path
import sys

from dotenv import load_dotenv
import requests

SOLUTION = Path(__file__).resolve().parent
BENCHMARK = SOLUTION.parents[2]
sys.path.insert(0, str(BENCHMARK))
from scripts.common import save_json
from scripts.solution import select_images, record_prediction, prediction_status, score_solution

API = 'https://platform.reducto.ai'
OPTIONS = {'enhance': {'summarize_figures': False},
           'retrieval': {'chunking': {'chunk_mode': 'disabled'}},
           'settings': {'force_url_result': False}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', help='One image ID; omit for all images')
    parser.add_argument('--resume', action='store_true', help='Skip unchanged saved predictions')
    args = parser.parse_args()
    load_dotenv(SOLUTION / '.env')
    session = requests.Session()
    session.headers['Authorization'] = f"Bearer {os.environ['REDUCTO_API_KEY']}"
    output = SOLUTION / 'output'
    (output / 'raw').mkdir(parents=True, exist_ok=True)
    (output / 'scores.json').unlink(missing_ok=True)
    for image in select_images(args.image):
        image_id = image.parent.name.split('-', 1)[0]
        prediction = output / f'{image_id}.md'
        if args.resume and prediction_status(prediction, image, settings=OPTIONS) == 'current':
            continue
        print(f'Reducto parse {image_id}', flush=True)
        with image.open('rb') as file:
            upload = session.post(API + '/upload', files={'file': (image.name, file)}, timeout=120)
        upload.raise_for_status()
        request = {'input': upload.json()['file_id'], **OPTIONS}
        save_json(output / 'raw' / f'{image_id}.request.json', request)
        response = session.post(API + '/parse', json=request, timeout=600)
        response.raise_for_status()
        result = response.json()
        save_json(output / 'raw' / f'{image_id}.json', result)
        prediction.write_text('\n\n'.join(chunk['content'] for chunk in result['result']['chunks']))
        record_prediction(prediction, image, OPTIONS)
    score_solution('parse', output, args.image)


if __name__ == '__main__':
    main()
