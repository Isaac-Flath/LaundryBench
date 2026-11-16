"""Serve the viewer locally; discover benchmark data from its folders."""
import argparse
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

from .common import ROOT, list_images


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        if urlsplit(self.path).path != '/images.json':
            return super().do_GET()
        images = [{'id': path.parent.name.split('-', 1)[0],
                   'title': path.parent.name.split('-', 1)[1].replace('-', ' ').capitalize(),
                   'file': str(path.relative_to(ROOT))} for path in list_images()]
        body = json.dumps(images).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    print(f'http://127.0.0.1:{args.port}/review.html', flush=True)
    ThreadingHTTPServer(('127.0.0.1', args.port), Handler).serve_forever()
