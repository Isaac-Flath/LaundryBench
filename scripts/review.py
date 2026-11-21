"""Serve the viewer locally; discover benchmark data, save review notes, and transcribe audio."""
import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from .common import ROOT, list_images, save_json

NOTES_PATH = ROOT / 'review-notes.json'
NOTES_LOCK = threading.Lock()
ASSEMBLYAI_API = 'https://api.assemblyai.com/v2'
SPEECH_MODELS = ['assemblyai-stt-3-7', 'universal-2']


def load_notes():
    if not NOTES_PATH.exists():
        return {}
    return json.loads(NOTES_PATH.read_text(encoding='utf-8'))


def transcribe_audio(audio_bytes):
    api_key = os.environ.get('ASSEMBLYAI_API_KEY')
    if not api_key:
        raise RuntimeError('Set ASSEMBLYAI_API_KEY before starting scripts.review to enable transcription.')
    headers = {'Authorization': api_key}
    upload_req = Request(f'{ASSEMBLYAI_API}/upload', data=audio_bytes,
                         headers={**headers, 'Content-Type': 'application/octet-stream'}, method='POST')
    with urlopen(upload_req, timeout=60) as response:
        upload_url = json.loads(response.read())['upload_url']
    payload = json.dumps({'audio_url': upload_url, 'speech_models': SPEECH_MODELS}).encode()
    start_req = Request(f'{ASSEMBLYAI_API}/transcript', data=payload,
                        headers={**headers, 'Content-Type': 'application/json'}, method='POST')
    with urlopen(start_req, timeout=30) as response:
        transcript_id = json.loads(response.read())['id']
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        poll_req = Request(f'{ASSEMBLYAI_API}/transcript/{transcript_id}', headers=headers)
        with urlopen(poll_req, timeout=30) as response:
            result = json.loads(response.read())
        if result['status'] == 'completed':
            return result.get('text') or ''
        if result['status'] == 'error':
            raise RuntimeError(result.get('error') or 'AssemblyAI transcription failed')
        time.sleep(0.8)
    raise RuntimeError('Transcription timed out')


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == '/images.json':
            images = [{'id': p.parent.name.split('-', 1)[0],
                       'title': p.parent.name.split('-', 1)[1].replace('-', ' ').capitalize(),
                       'file': str(p.relative_to(ROOT))} for p in list_images()]
            return self.send_json(200, images)
        if path == '/notes.json':
            with NOTES_LOCK:
                return self.send_json(200, load_notes())
        return super().do_GET()

    def do_POST(self):
        path = urlsplit(self.path).path
        length = int(self.headers.get('Content-Length', '0'))
        body = self.rfile.read(length)
        if path == '/notes.json':
            try:
                data = json.loads(body)
                key = data['key']
                note = data.get('note')
            except (ValueError, KeyError, TypeError):
                return self.send_json(400, {'error': 'Expected {"key": ..., "note": ...}'})
            with NOTES_LOCK:
                notes = load_notes()
                if note and (note.get('text') or '').strip():
                    notes[key] = note
                else:
                    notes.pop(key, None)
                save_json(NOTES_PATH, notes)
                return self.send_json(200, {'ok': True, 'count': len(notes)})
        if path == '/transcribe':
            if not body:
                return self.send_json(400, {'error': 'Empty audio upload'})
            try:
                text = transcribe_audio(body)
            except HTTPError as error:
                detail = error.read().decode('utf-8', errors='replace')
                return self.send_json(502, {'error': f'AssemblyAI HTTP {error.code}: {detail[:200]}'})
            except (URLError, RuntimeError) as error:
                return self.send_json(503, {'error': str(error)})
            return self.send_json(200, {'text': text})
        return self.send_json(404, {'error': 'Not found'})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    print(f'http://127.0.0.1:{args.port}/review.html', flush=True)
    ThreadingHTTPServer(('127.0.0.1', args.port), Handler).serve_forever()
