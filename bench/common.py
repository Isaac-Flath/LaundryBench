"""Shared input and weighting rules. Standard library only."""
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_dataset():
    manifest = json.loads((ROOT / 'manifest.json').read_text())
    checks = json.loads((ROOT / 'bench/checks.json').read_text())
    images = {item['id']: item for item in manifest['images']}
    if set(images) != {case['image_id'] for case in checks['cases']}:
        raise ValueError('Manifest and checks cover different images')
    for case in checks['cases']:
        item = images[case['image_id']]
        if not (case['image_sha256'] == item['sha256'] == digest((ROOT / item['file']).read_bytes())):
            raise ValueError(f"Image changed: {item['id']}; review its annotations")
        if case['event_group'] != item['event_group']:
            raise ValueError('Event grouping differs between manifest and checks')
    return images, checks


def read_outputs(directory, image_ids):
    directory = Path(directory)
    outputs = {}
    for image_id in image_ids:
        matches = [directory / f'{image_id}{suffix}' for suffix in ('.md', '.txt', '.html')
                   if (directory / f'{image_id}{suffix}').is_file()]
        if len(matches) != 1:
            raise ValueError(f'{image_id}: need exactly one .md, .txt or .html file in {directory}')
        outputs[image_id] = matches[0].read_text(encoding='utf-8')
    return outputs


def event_mean(scores, images):
    """First average views of the same event; then give each event equal weight."""
    events = defaultdict(list)
    for image_id, score in scores.items():
        events[images[image_id]['event_group']].append(score)
    return mean(mean(values) for values in events.values()) if events else None


def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
