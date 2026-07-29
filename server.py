from http.server import HTTPServer, BaseHTTPRequestHandler
import json, os, uuid

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
        if self.path == "/mcp":
            length = int(self.headers["Content-Length"])
            body = json.loads(self.rfile.read(length))
            rid = body.get("id", str(uuid.uuid4()))
            method = body.get("method", "")
            if method == "tools/list":
                result = {
                    "tools": [
                        {"name":"store_memory","description":"存一条记忆","inputSchema":{"type":"object","properties":{"key":{"type":"string"},"content":{"type":"string"}},"required":["key","content"]}},
                        {"name":"retrieve_memory","description":"查一条记忆","inputSchema":{"type":"object","properties":{"key":{"type":"string"}},"required":["key"]}},
                        {"name":"delete_memory","description":"删一条记忆","inputSchema":{"type":"object","properties":{"key":{"type":"string"}},"required":["key"]}}
                    ]
                }
                self._send(200, {"jsonrpc":"2.0","id":rid,"result":result})
            elif method == "tools/call":
                name = body["params"]["name"]
                args = body["params"]["arguments"]
                db = self._read_db()
                if name == "store_memory":
                    db[args["key"]] = args["content"]
                    self._write_db(db)
                    self._send(200, {"jsonrpc":"2.0","id":rid,"result":{"content":[{"type":"text","text":"stored"}]}})
                elif name == "retrieve_memory":
                    content = db.get(args["key"], "not_found")
                    self._send(200, {"jsonrpc":"2.0","id":rid,"result":{"content":[{"type":"text","text":content}]}})
                elif name == "delete_memory":
                    db.pop(args["key"], None)
                    self._write_db(db)
                    self._send(200, {"jsonrpc":"2.0","id":rid,"result":{"content":[{"type":"text","text":"deleted"}]}})
            return
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
        elif "/search" in self.path:
            q = self.path.split("q=")[1] if "q=" in self.path else ""
            db = self._read_db()
            results = [{"key":k,"content":v} for k,v in db.items() if q in k or q in v]
            self._send(200, results)

    def do_DELETE(self):
        if self.path.startswith("/memory/"):
            key = self.path.split("/memory/")[1]
            db = self._read_db()
            db.pop(key, None)
            self._write_db(db)
            self._send(200, {"status":"deleted"})

HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
