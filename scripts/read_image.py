"""Save an actual OCR response beside one example. Requires requests."""
import argparse
import base64
import json
import os
import time
from datetime import datetime, timezone

import requests
from .common import ROOT, digest, load_dataset, save_json


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--image', required=True)
    p.add_argument('--parser', choices=['gemini', 'datalab'], required=True)
    p.add_argument('--model', default='gemini-3.5-flash')
    args = p.parse_args()
    images, _ = load_dataset(args.image)
    item = images[args.image]
    path = ROOT / item['file']
    out = path.parent / 'outputs'
    text_path = out / f'{args.parser}.md'
    if text_path.exists():
        p.error(f'{text_path} already exists; preserve it before another run')
    meta = {'provider': args.parser, 'started_at': datetime.now(timezone.utc).isoformat(),
            'image_sha256': digest(path.read_bytes()), 'preprocessing': 'none; original image bytes'}
    if args.parser == 'gemini':
        if 'flash' not in args.model or 'pro' in args.model:
            p.error('Use a Gemini Flash model for this example')
        key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
        if not key:
            p.error('Set GEMINI_API_KEY or GOOGLE_API_KEY')
        prompt = (ROOT / 'prompts/read-image.txt').read_text()
        config = {'temperature': 0, 'maxOutputTokens': 8192}
        r = requests.post(f'https://generativelanguage.googleapis.com/v1beta/models/{args.model}:generateContent',
            headers={'x-goog-api-key': key}, json={
                'contents': [{'role': 'user', 'parts': [{'text': prompt}, {'inlineData': {
                    'mimeType': 'image/jpeg', 'data': base64.b64encode(path.read_bytes()).decode()}}]}],
                'generationConfig': config}, timeout=180)
        r.raise_for_status(); raw = r.json()
        candidates = raw.get('candidates', [])
        if len(candidates) != 1 or candidates[0].get('finishReason') != 'STOP':
            raise RuntimeError('Missing, blocked or truncated OCR response')
        text = '\n'.join(p.get('text', '') for p in candidates[0]['content']['parts'] if not p.get('thought'))
        meta.update(model_requested=args.model, model_reported=raw.get('modelVersion'),
                    prompt=prompt, settings=config, usage=raw.get('usageMetadata'))
    else:
        key = os.environ.get('DATALAB_API_KEY')
        if not key:
            p.error('Set DATALAB_API_KEY')
        headers = {'X-API-Key': key}
        settings = {'mode': 'accurate', 'output_format': 'markdown',
                    'disable_image_extraction': 'true', 'disable_image_captions': 'true',
                    'exact_transcription': 'true'}
        with path.open('rb') as f:
            r = requests.post('https://www.datalab.to/api/v1/convert', headers=headers,
                              files={'file': ('image.jpg', f, 'image/jpeg')}, data=settings, timeout=120)
        r.raise_for_status(); job = r.json()
        check_url = job['request_check_url']
        if not check_url.startswith('https://www.datalab.to/'):
            raise RuntimeError('Unexpected result host')
        for _ in range(100):
            r = requests.get(check_url, headers=headers, timeout=60)
            r.raise_for_status(); raw = r.json()
            if raw.get('status') == 'complete':
                break
            if raw.get('status') in ('failed', 'error'):
                raise RuntimeError('Datalab conversion failed')
            time.sleep(3)
        else:
            raise TimeoutError('Datalab conversion did not complete')
        if not raw.get('success'):
            raise RuntimeError('Datalab conversion was unsuccessful')
        text = raw.get('markdown') or ''
        meta.update(settings=settings, versions=raw.get('versions'), runtime=raw.get('runtime'),
                    total_cost=raw.get('total_cost'), prompt=None)
    meta['output_sha256'] = digest(text.encode())
    meta['completed_at'] = datetime.now(timezone.utc).isoformat()
    out.mkdir(parents=True, exist_ok=True)
    text_path.write_text(text)
    save_json(out / f'{args.parser}-settings.json', meta)
    print(f'Saved real {args.parser} output: {text_path}', flush=True)


if __name__ == '__main__':
    main()
