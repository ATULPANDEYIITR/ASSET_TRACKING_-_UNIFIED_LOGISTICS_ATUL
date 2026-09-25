from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "frontend"

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

server = ThreadingHTTPServer(("127.0.0.1", 5500), Handler)

print("ATUL FRONTEND SERVER")
print("http://127.0.0.1:5500")
print("Press CTRL+C to stop.")

server.serve_forever()
