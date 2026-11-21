"""Serve the viewer locally; discover benchmark data and save local review notes."""
import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
from urllib.parse import urlsplit

from .common import ROOT, list_images, save_json

NOTES_PATH = ROOT / 'review-notes.json'
NOTES_LOCK = threading.Lock()


def load_notes():
    if not NOTES_PATH.exists():
        return {}
    return json.loads(NOTES_PATH.read_text(encoding='utf-8'))


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
        if urlsplit(self.path).path != '/notes.json':
            return self.send_json(404, {'error': 'Not found'})
        length = int(self.headers.get('Content-Length', '0'))
        try:
            data = json.loads(self.rfile.read(length))
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    print(f'http://127.0.0.1:{args.port}/review.html', flush=True)
    ThreadingHTTPServer(('127.0.0.1', args.port), Handler).serve_forever()
