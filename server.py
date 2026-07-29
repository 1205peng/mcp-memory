from http.server import HTTPServer, BaseHTTPRequestHandler
import json, os

db_path = os.environ.get("MEMORY_DB", "memory.json")

if not os.path.exists(db_path):
    with open(db_path, "w") as f:
        json.dump({}, f)

class Handler(BaseHTTPRequestHandler):
    def _read_db(self):
        with open(db_path) as f:
            return json.load(f)

    def _write_db(self, data):
        with open(db_path, "w") as f:
            json.dump(data, f)

    def _send(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_POST(self):
        if self.path == "/memory":
            length = int(self.headers["Content-Length"])
            body = json.loads(self.rfile.read(length))
            db = self._read_db()
            db[body["key"]] = body["content"]
            self._write_db(db)
            self._send(200, {"status": "stored"})

    def do_GET(self):
        if self.path == "/":
            self._send(200, {"service":"MCP Memory Server","status":"running"})
        elif self.path.startswith("/memory/"):
            key = self.path.split("/memory/")[1]
            db = self._read_db()
            if key in db:
                self._send(200, {"key":key,"content":db[key]})
            else:
                self._send(404, {"status":"not_found"})

    def do_DELETE(self):
        if self.path.startswith("/memory/"):
            key = self.path.split("/memory/")[1]
            db = self._read_db()
            db.pop(key, None)
            self._write_db(db)
            self._send(200, {"status":"deleted"})

HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
