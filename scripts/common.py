"""Load benchmark data and save results. Standard library only."""
import json
from pathlib import Path
from typing import Literal

ROOT = Path(__file__).resolve().parents[1]


def list_images() -> list[Path]:
    return sorted((ROOT / 'data').glob('*/image.*'))


def load_dataset(task: Literal['parse', 'extract'], image_id: str | None = None):
    dataset = {}
    for path in list_images():
        folder = path.parent
        document_id = folder.name.split('-', 1)[0]
        if image_id is not None and document_id != image_id:
            continue
        image_tests = json.loads((folder / f'{task}_tests.json').read_text())
        if task == 'extract':
            image_tests['schema'] = json.loads((folder / 'extract_schema.json').read_text())
        dataset[document_id] = image_tests
    return dataset


def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
