import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, os.getenv("RAG_DB_PATH", "rag.db"))


def connect():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init():
    with connect() as db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS materials (id INTEGER PRIMARY KEY AUTOINCREMENT, slot TEXT NOT NULL, name TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
        )
        db.execute("CREATE INDEX IF NOT EXISTS idx_materials_slot ON materials(slot)")


def add(slot, name, content):
    with connect() as db:
        cursor = db.execute(
            "INSERT INTO materials(slot,name,content) VALUES(?,?,?)",
            (slot, name, content),
        )
        return cursor.lastrowid


def list_materials(slot=None):
    with connect() as db:
        if slot:
            rows = db.execute(
                "SELECT id,slot,name,created_at FROM materials WHERE slot=? ORDER BY id",
                (slot,),
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT id,slot,name,created_at FROM materials ORDER BY id"
            ).fetchall()
    return [dict(row) for row in rows]


def get_slot_materials(slot):
    with connect() as db:
        return db.execute(
            "SELECT name,content FROM materials WHERE slot=? ORDER BY id", (slot,)
        ).fetchall()


def delete(material_id):
    with connect() as db:
        row = db.execute(
            "SELECT slot FROM materials WHERE id=?", (material_id,)
        ).fetchone()
        if not row:
            return None
        db.execute("DELETE FROM materials WHERE id=?", (material_id,))
    return row["slot"]
