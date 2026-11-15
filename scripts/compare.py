"""PAIR-style image judging with a configurable Gemini Flash judge."""
import argparse
import base64
import json
import os
import random
import re
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

from .common import ROOT, digest, event_mean, load_dataset, read_outputs, save_json

PROMPT = ROOT / 'prompts/compare-outputs.txt'
SCHEMA = {'type': 'object', 'properties': {
    'verdict': {'type': 'string', 'enum': ['A', 'B', 'tie', 'unjudgeable']},
    'evidence': {'type': 'array', 'items': {'type': 'string'}},
    'rationale': {'type': 'string'}}, 'required': ['verdict', 'evidence', 'rationale']}


def validate_verdict(value):
    if not isinstance(value, dict) or value.get('verdict') not in ('A', 'B', 'tie', 'unjudgeable'):
        raise ValueError('Invalid judge verdict')
    if not isinstance(value.get('rationale'), str) or not value['rationale'].strip():
        raise ValueError('Judge omitted its rationale')
    evidence = value.get('evidence')
    if not isinstance(evidence, list) or not evidence or not all(isinstance(e, str) and e.strip() for e in evidence):
        raise ValueError('Judge omitted concrete evidence')
    return value


def candidate_points(verdict, candidate_label):
    if verdict == 'unjudgeable':
        return None
    if verdict == 'tie':
        return 0.5
    if verdict not in ('A', 'B') or candidate_label not in ('A', 'B'):
        raise ValueError('Invalid verdict or label')
    return float(verdict == candidate_label)


def plan(image_ids, rounds, seed):
    if rounds < 1:
        raise ValueError('rounds must be positive')
    rng = random.Random(seed)
    jobs = []
    for image_id in image_ids:
        for repeat in range(rounds):
            labels = ['A', 'B']
            rng.shuffle(labels)
            jobs.extend({'image_id': image_id, 'round': repeat, 'candidate_label': label} for label in labels)
    rng.shuffle(jobs)
    return jobs


def summarize(records, images):
    grouped = defaultdict(list)
    orders = defaultdict(list)
    paired = defaultdict(list)
    for r in records:
        grouped[r['image_id']].append(r.get('points'))
        if r.get('points') is not None:
            orders[r['candidate_label']].append(r['points'])
            paired[(r['image_id'], r['round'])].append(r['points'])
    complete = all(all(p is not None for p in pts) for pts in grouped.values()) and set(grouped) == set(images)
    scores = {i: mean(pts) for i, pts in grouped.items() if all(p is not None for p in pts)}
    # No global score if a failure/abstention would silently change the denominator.
    return {'score': event_mean(scores, images) if complete else None,
            'complete': complete, 'valid_judgments': sum(r.get('points') is not None for r in records),
            'total_judgments': len(records), 'per_image': scores,
            'mean_by_candidate_position': {k: mean(v) for k, v in orders.items()},
            'order_disagreements': sum(len(p) == 2 and p[0] != p[1] for p in paired.values()),
            'complete_order_pairs': sum(len(p) == 2 for p in paired.values())}


def request_judgment(image_bytes, parses, model, key):
    payload = {'systemInstruction': {'parts': [{'text': PROMPT.read_text()}]},
               'contents': [{'role': 'user', 'parts': [
                   {'inlineData': {'mimeType': 'image/jpeg', 'data': base64.b64encode(image_bytes).decode()}},
                   {'text': json.dumps({'parses': parses}, ensure_ascii=False)}]}],
               'generationConfig': {'temperature': 0, 'maxOutputTokens': 4096,
                                    'responseMimeType': 'application/json', 'responseJsonSchema': SCHEMA}}
    request = urllib.request.Request(
        f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
        data=json.dumps(payload).encode(),
        headers={'Content-Type': 'application/json', 'x-goog-api-key': key}, method='POST')
    with urllib.request.urlopen(request, timeout=120) as response:
        raw = json.load(response)
    return raw


def decode_response(raw):
    candidates = raw.get('candidates', [])
    if len(candidates) != 1 or candidates[0].get('finishReason') != 'STOP':
        raise ValueError('Missing, blocked, or truncated judge response')
    text = ''.join(p.get('text', '') for p in candidates[0].get('content', {}).get('parts', [])
                   if not p.get('thought'))
    return validate_verdict(json.loads(text))


def run(jobs, images, candidate, baseline, model, out, key):
    records = []
    for index, job in enumerate(jobs):
        image_id = job['image_id']
        label = job['candidate_label']
        parses = {label: candidate[image_id], 'B' if label == 'A' else 'A': baseline[image_id]}
        # Always serialize A first. The randomization changes which parser owns A.
        parses = {k: parses[k] for k in ('A', 'B')}
        image_bytes = (ROOT / images[image_id]['file']).read_bytes()
        record = {**job, 'image_sha256': digest(image_bytes),
                  'parses': parses, 'model_requested': model, 'points': None}
        try:
            raw = request_judgment(image_bytes, parses, model, key)
            record['raw_response'] = raw
            record['model_reported'] = raw.get('modelVersion')
            record['judgment'] = decode_response(raw)
            record['points'] = candidate_points(record['judgment']['verdict'], label)
        except (urllib.error.URLError, TimeoutError, ValueError, KeyError) as error:
            # Preserve raw responses for schema errors; never turn a failure into a tie.
            record['error'] = type(error).__name__ + (f' HTTP {error.code}' if isinstance(error, urllib.error.HTTPError) else '')
        records.append(record)
        save_json(out / f'{index:03d}-{image_id}.json', record)
        print(f"{index+1}/{len(jobs)}: {image_id} {record.get('judgment', {}).get('verdict', 'ERROR')}", flush=True)
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', required=True, help='Saved output name, e.g. gemini')
    parser.add_argument('--baseline', required=True, help='Saved output name, e.g. datalab')
    parser.add_argument('--image', help='One image ID; omit to compare all ten')
    parser.add_argument('--model', required=True, help='Explicit Gemini Flash model ID; actual returned version is recorded')
    parser.add_argument('--out', type=Path, required=True, help='New output directory; existing directories are refused')
    parser.add_argument('--rounds', type=int, default=1, help='Each round evaluates both A/B orders (default: 2 calls per image)')
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if not re.fullmatch(r'gemini-[a-z0-9.-]*flash[a-z0-9.-]*', args.model) or 'pro' in args.model:
        parser.error('Use a Gemini Flash model ID for this low-cost adapter')
    images, _ = load_dataset(args.image)
    candidate = read_outputs(args.candidate, images)
    baseline = read_outputs(args.baseline, images)
    jobs = plan(images, args.rounds, args.seed)
    if args.dry_run:
        print(json.dumps({'images': len(images), 'calls': len(jobs), 'model': args.model, 'jobs': jobs}, indent=2))
        return
    key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    if not key:
        parser.error('Set GEMINI_API_KEY or GOOGLE_API_KEY')
    args.out.mkdir(parents=True, exist_ok=False)
    metadata = {'metric': 'pair_style', 'implementation': 'LaundryParseBench adaptation; not official Reducto scores',
                'started_at': datetime.now(timezone.utc).isoformat(), 'model_requested': args.model,
                'prompt': PROMPT.read_text(), 'prompt_sha256': digest(PROMPT.read_bytes()),
                'manifest_sha256': digest((ROOT / 'manifest.json').read_bytes()),
                'rounds': args.rounds, 'seed': args.seed, 'candidate': args.candidate, 'baseline': args.baseline,
                'candidate_sha256': {i: digest(t.encode()) for i, t in candidate.items()},
                'baseline_sha256': {i: digest(t.encode()) for i, t in baseline.items()}, 'jobs': jobs}
    save_json(args.out / 'run.json', metadata)
    records = run(jobs, images, candidate, baseline, args.model, args.out, key)
    report = summarize(records, images)
    save_json(args.out / 'summary.json', report)
    print(json.dumps(report, indent=2))
    if not report['complete']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
