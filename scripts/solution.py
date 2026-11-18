"""Shared file bookkeeping for example solutions; never sends test answers to models."""
from datetime import datetime, timezone
import hashlib
import json

from .common import list_images, load_dataset, save_json
from .check import score_outputs as score_parse, read_ocr_outputs
from .extract import score_outputs as score_extract


def select_images(image_id=None):
    images = [p for p in list_images() if image_id is None or p.parent.name.startswith(image_id + '-')]
    if not images:
        raise ValueError(f'Unknown image ID: {image_id}')
    return images


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metadata_path(prediction):
    return prediction.parent / 'raw' / f'{prediction.stem}.metadata.json'


def record_prediction(prediction, image, settings, schema=None):
    """Record the exact input and output only after a prediction is saved."""
    save_json(metadata_path(prediction), {
        'created_at': datetime.now(timezone.utc).isoformat(),
        'image_sha256': sha256(image), 'output_sha256': sha256(prediction),
        'schema': schema, 'settings': settings,
    })


def prediction_status(prediction, image, schema=None, settings=None):
    if not prediction.exists():
        return 'not run'
    metadata = metadata_path(prediction)
    if not metadata.exists():
        return 'unverified input version'
    try:
        saved = json.loads(metadata.read_text())
        current = (saved['image_sha256'] == sha256(image)
                   and saved['output_sha256'] == sha256(prediction)
                   and saved['schema'] == schema
                   and (settings is None or saved['settings'] == settings))
    except (ValueError, KeyError):
        return 'invalid run metadata'
    return 'current' if current else 'input, schema, settings, or output changed'


def score_solution(track, output_dir, image_id=None):
    dataset = load_dataset(track, image_id)
    if track == 'parse':
        report = score_parse(read_ocr_outputs(output_dir, dataset), dataset)
    else:
        outputs = {key: (output_dir / f'{key}.json').read_text() for key in dataset}
        report = score_extract(outputs, dataset)
    save_json(output_dir / 'scores.json', report)
    print(f"{track}: {report['passed']}/{report['total']} checks", flush=True)
