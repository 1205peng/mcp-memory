from http.server import HTTPServer, BaseHTTPRequestHandler
import sqlite3, os, json

db_path = os.environ.get("MEMORY_DB", "/data/memory.db")

def init_db():
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

init_db()

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_POST(self):
        if self.path == "/memory":
            length = int(self.headers["Content-Length"])
            body = json.loads(self.rfile.read(length))
            try:
                with sqlite3.connect(db_path) as conn:
                    conn.execute("INSERT INTO memories (key,content) VALUES (?,?)", (body["key"], body["content"]))
                self._send(200, {"status": "stored"})
            except sqlite3.IntegrityError:
                self._send(200, {"status": "key_exists"})

    def do_GET(self):
        if self.path == "/":
            self._send(200, {"service": "MCP Memory Server", "status": "running"})
        elif self.path.startswith("/memory/"):
            key = self.path.split("/memory/")[1]
            with sqlite3.connect(db_path) as conn:
                row = conn.execute("SELECT content FROM memories WHERE key=?", (key,)).fetchone()
            if row:
                self._send(200, {"key": key, "content": row[0]})
            else:
                self._send(404, {"status": "not_found"})
        elif self.path.startswith("/search?q="):
            q = self.path.split("q=")[1]
            with sqlite3.connect(db_path) as conn:
                rows = conn.execute("SELECT key,content FROM memories WHERE key LIKE ? OR content LIKE ?", (f"%{q}%",f"%{q}%")).fetchall()
            self._send(200, [{"key":r[0],"content":r[1]} for r in rows])

    def do_DELETE(self):
        if self.path.startswith("/memory/"):
            key = self.path.split("/memory/")[1]
            with sqlite3.connect(db_path) as conn:
                conn.execute("DELETE FROM memories WHERE key=?", (key,))
            self._send(200, {"status": "deleted"})

port = int(os.environ.get("PORT", 8080))
print(f"MCP Memory Server running on port {port}")
HTTPServer(("0.0.0.0", port), Handler).serve_forever()
