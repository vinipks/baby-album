"""
Baby Album — SQLite database layer
"""
import sqlite3
import os
from datetime import datetime, date
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), "baby_album.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS settings (
                key   TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS family_members (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL,
                access_code TEXT NOT NULL UNIQUE,
                is_admin    INTEGER NOT NULL DEFAULT 0,
                created_at  TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS photos (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                filename     TEXT NOT NULL,
                original_name TEXT NOT NULL,
                caption      TEXT DEFAULT '',
                uploaded_at  TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS reactions (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                photo_id         INTEGER NOT NULL,
                family_member_id INTEGER NOT NULL,
                emoji            TEXT NOT NULL,
                created_at       TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (photo_id) REFERENCES photos(id) ON DELETE CASCADE,
                FOREIGN KEY (family_member_id) REFERENCES family_members(id) ON DELETE CASCADE,
                UNIQUE(photo_id, family_member_id, emoji)
            );

            CREATE INDEX IF NOT EXISTS idx_photos_uploaded_at ON photos(uploaded_at);
            CREATE INDEX IF NOT EXISTS idx_reactions_photo ON reactions(photo_id);
        """)


# ── Settings ──────────────────────────────────────────────────────────

def get_setting(key: str) -> str | None:
    with get_conn() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row["value"] if row else None


def set_setting(key: str, value: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )


def get_baby_birth_date() -> date | None:
    v = get_setting("baby_birth_date")
    return date.fromisoformat(v) if v else None


def set_baby_birth_date(d: date):
    set_setting("baby_birth_date", d.isoformat())


def get_baby_name() -> str:
    return get_setting("baby_name") or "Baby"


def set_baby_name(name: str):
    set_setting("baby_name", name)


# ── Family Members ────────────────────────────────────────────────────

def add_family_member(name: str, access_code: str, is_admin: bool = False) -> dict:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO family_members (name, access_code, is_admin) VALUES (?, ?, ?)",
            (name, name, 1 if is_admin else 0),
        )
        return {"id": cur.lastrowid, "name": name, "is_admin": is_admin}


def get_family_member_by_code(code: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, name, is_admin FROM family_members WHERE access_code=?", (code,)
        ).fetchone()
        return dict(row) if row else None


def list_family_members() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, name, access_code, is_admin, created_at FROM family_members ORDER BY created_at"
        ).fetchall()
        return [dict(r) for r in rows]


# ── Photos ────────────────────────────────────────────────────────────

def add_photo(filename: str, original_name: str, caption: str = "") -> dict:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO photos (filename, original_name, caption) VALUES (?, ?, ?)",
            (filename, original_name, caption),
        )
        return {"id": cur.lastrowid, "filename": filename}


def get_photos(page: int = 1, per_page: int = 20) -> list[dict]:
    offset = (page - 1) * per_page
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT p.id, p.filename, p.original_name, p.caption, p.uploaded_at
               FROM photos p
               ORDER BY p.uploaded_at DESC
               LIMIT ? OFFSET ?""",
            (per_page, offset),
        ).fetchall()
        return [dict(r) for r in rows]


def get_photo(id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, filename, original_name, caption, uploaded_at FROM photos WHERE id=?",
            (id,),
        ).fetchone()
        return dict(row) if row else None


def get_photo_count() -> int:
    with get_conn() as conn:
        return conn.execute("SELECT COUNT(*) FROM photos").fetchone()[0]


# ── Reactions ─────────────────────────────────────────────────────────────────

def toggle_reaction(photo_id: int, member_id: int, emoji: str) -> dict:
    """Toggle a reaction. Returns {'active': True} if added, {'active': False} if removed."""
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT id FROM reactions WHERE photo_id=? AND family_member_id=? AND emoji=?",
            (photo_id, member_id, emoji),
        ).fetchone()
        if existing:
            conn.execute("DELETE FROM reactions WHERE id=?", (existing["id"],))
            return {"active": False}
        else:
            conn.execute(
                "INSERT INTO reactions (photo_id, family_member_id, emoji) VALUES (?, ?, ?)",
                (photo_id, member_id, emoji),
            )
            return {"active": True}


def get_reactions(photo_id: int) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT r.id, r.emoji, r.family_member_id, fm.name as member_name, r.created_at
               FROM reactions r
               JOIN family_members fm ON fm.id = r.family_member_id
               WHERE r.photo_id=?
               ORDER BY r.created_at""",
            (photo_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_all_reactions_grouped() -> dict[int, list[dict]]:
    """Returns {photo_id: [reaction_dict, ...]} for all photos."""
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT r.photo_id, r.emoji, r.family_member_id, fm.name as member_name
               FROM reactions r
               JOIN family_members fm ON fm.id = r.family_member_id
               ORDER BY r.photo_id, r.emoji"""
        ).fetchall()
        result = {}
        for r in rows:
            result.setdefault(r["photo_id"], []).append(dict(r))
        return result