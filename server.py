from fastapi import FastAPI, Request
from pydantic import BaseModel
import sqlite3, os, json

app = FastAPI()
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

class Memory(BaseModel):
    key: str
    content: str

@app.get("/")
def root():
    return {"service": "MCP Memory Server", "status": "running"}

@app.post("/memory")
def add_memory(mem: Memory):
    with sqlite3.connect(db_path) as conn:
        try:
            conn.execute("INSERT INTO memories (key,content) VALUES (?,?)", (mem.key, mem.content))
            return {"status": "stored", "key": mem.key}
        except sqlite3.IntegrityError:
            return {"status": "key_exists", "key": mem.key}

@app.get("/memory/{key}")
def get_memory(key: str):
    with sqlite3.connect(db_path) as conn:
        row = conn.execute("SELECT content FROM memories WHERE key=?", (key,)).fetchone()
        if row:
            return {"key": key, "content": row[0]}
        return {"status": "not_found"}

@app.delete("/memory/{key}")
def delete_memory(key: str):
    with sqlite3.connect(db_path) as conn:
        conn.execute("DELETE FROM memories WHERE key=?", (key,))
        return {"status": "deleted"}

@app.get("/search")
def search_memory(q: str):
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT key, content FROM memories WHERE key LIKE ? OR content LIKE ?",
            (f"%{q}%", f"%{q}%")
        ).fetchall()
        return [{"key": r[0], "content": r[1]} for r in rows]
