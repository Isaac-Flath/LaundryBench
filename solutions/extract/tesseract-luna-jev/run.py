"""Run tesseract OCR → Luna extraction → Jev verification from source images."""
from pathlib import Path
import sys

SOLUTION = Path(__file__).resolve().parent
sys.path.insert(0, str(SOLUTION.parents[2]))
from scripts.luna_jev import main


if __name__ == '__main__':
    main(SOLUTION, 'tesseract')
