"""A CPU-only baseline: one unmodified Tesseract pass per photograph."""
import argparse
from pathlib import Path
import subprocess
import sys

SOLUTION = Path(__file__).resolve().parent
BENCHMARK = SOLUTION.parents[2]
sys.path.insert(0, str(BENCHMARK))
from scripts.common import save_json
from scripts.solution import select_images, record_prediction, prediction_status, score_solution


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', help='One image ID; omit for all images')
    parser.add_argument('--resume', action='store_true', help='Skip unchanged saved predictions')
    args = parser.parse_args()
    version = subprocess.run(['tesseract', '--version'], capture_output=True, text=True, check=True).stdout.splitlines()[0]
    settings = {'model': version, 'language': 'eng', 'psm': 11, 'oem': 1}
    output = SOLUTION / 'output'
    (output / 'raw').mkdir(parents=True, exist_ok=True)
    (output / 'scores.json').unlink(missing_ok=True)
    for image in select_images(args.image):
        image_id = image.parent.name.split('-', 1)[0]
        prediction = output / f'{image_id}.md'
        if args.resume and prediction_status(prediction, image, settings=settings) == 'current':
            continue
        print(f'Tesseract {image_id}', flush=True)
        result = subprocess.run(['tesseract', str(image), 'stdout', '-l', 'eng', '--oem', '1', '--psm', '11'],
                                capture_output=True, text=True, check=True, timeout=180)
        prediction.write_text(result.stdout)
        save_json(output / 'raw' / f'{image_id}.json', {'settings': settings, 'stderr': result.stderr})
        record_prediction(prediction, image, settings)
    score_solution('parse', output, args.image)


if __name__ == '__main__':
    main()
