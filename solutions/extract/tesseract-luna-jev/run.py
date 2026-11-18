"""Use the existing Luna/Jev extractor with saved Tesseract OCR."""
import argparse
from pathlib import Path
import subprocess
import sys
from dotenv import load_dotenv

SOLUTION = Path(__file__).resolve().parent
BENCHMARK = SOLUTION.parents[2]
sys.path.insert(0, str(BENCHMARK))
from scripts.solution import select_images, prediction_status

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', help='One image ID; omit for all images')
    parser.add_argument('--resume', action='store_true', help='Skip unchanged saved predictions')
    args = parser.parse_args()
    load_dotenv(SOLUTION / '.env')
    ocr_dir = BENCHMARK / 'solutions/parse/tesseract/output'
    for image in select_images(args.image):
        image_id = image.parent.name.split('-', 1)[0]
        if prediction_status(ocr_dir / f'{image_id}.md', image) != 'current':
            parser.error(f'Run Tesseract parsing for image {image_id} first; its OCR is missing or stale.')
    subprocess.run([
        sys.executable, str(SOLUTION.parent / 'luna-jev' / 'run.py'),
        '--ocr-dir', str(ocr_dir),
        '--output-dir', str(SOLUTION / 'output'), *sys.argv[1:],
    ], check=True)
