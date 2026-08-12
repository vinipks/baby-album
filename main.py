"""
Baby Album — FastAPI app
"""
import os
import uuid
from datetime import datetime, date
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from database import (
    init_db, get_baby_birth_date, set_baby_birth_date,
    get_baby_name, set_baby_name,
    add_family_member, get_family_member_by_code, list_family_members,
    add_photo, get_photos, get_photo, get_photo_count,
    toggle_reaction, get_reactions, get_all_reactions_grouped,
)

app = FastAPI(title="Baby Album")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ── Helper ────────────────────────────────────────────────────────────

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".heic"}


def compute_age(birth_date: date, photo_date: date) -> str:
    """Compute age in Xm Xw Xd format from birth_date to photo_date."""
    if photo_date < birth_date:
        return "0m 0w 0d"

    # Total days difference
    delta = photo_date - birth_date
    total_days = delta.days

    months = total_days // 30
    weeks = (total_days % 30) // 7
    days = total_days % 7

    parts = []
    if months > 0:
        parts.append(f"{months}m")
    if weeks > 0 or months > 0:
        parts.append(f"{weeks}w")
    parts.append(f"{days}d")
    return " ".join(parts)


# ── Settings ──────────────────────────────────────────────────────────

@app.post("/api/setup")
async def setup(baby_name: str = Form(...), birth_date: str = Form(...)):
    """Set baby name and birth date on first run."""
    try:
        bd = date.fromisoformat(birth_date)
    except ValueError:
        raise HTTPException(400, "Invalid date format. Use YYYY-MM-DD.")
    set_baby_name(baby_name)
    set_baby_birth_date(bd)
    # Seed admin if none exist
    if not list_family_members():
        add_family_member("Mom", "mom", is_admin=True)
        add_family_member("Dad", "dad", is_admin=True)
    return {"ok": True}


@app.get("/api/settings")
async def get_settings():
    return {
        "baby_name": get_baby_name(),
        "baby_birth_date": str(get_baby_birth_date()) if get_baby_birth_date() else None,
        "setup_done": get_baby_birth_date() is not None,
    }


# ── Auth ──────────────────────────────────────────────────────────────

@app.post("/api/login")
async def login(access_code: str = Form(...)):
    member = get_family_member_by_code(access_code)
    if not member:
        raise HTTPException(401, "Invalid access code")
    return member


# ── Family Members ────────────────────────────────────────────────────

@app.get("/api/members")
async def list_members():
    return list_family_members()


@app.post("/api/members")
async def create_member(name: str = Form(...), access_code: str = Form(...)):
    existing = get_family_member_by_code(access_code)
    if existing:
        raise HTTPException(409, "Access code already in use")
    member = add_family_member(name, access_code)
    return member


# ── Photos ────────────────────────────────────────────────────────────

@app.get("/api/photos")
async def list_photos(page: int = 1, per_page: int = 20):
    birth_date = get_baby_birth_date()
    photos = get_photos(page=page, per_page=per_page)
    total = get_photo_count()
    total_pages = max(1, (total + per_page - 1) // per_page)

    # Get all reactions grouped by photo
    all_reactions = get_all_reactions_grouped()

    result = []
    for p in photos:
        try:
            photo_date = datetime.fromisoformat(p["uploaded_at"]).date()
        except (ValueError, TypeError):
            photo_date = date.today()

        age = compute_age(birth_date, photo_date) if birth_date else ""

        reactions = all_reactions.get(p["id"], [])
        # Group reactions by emoji with list of names
        emoji_counts = {}
        for r in reactions:
            if r["emoji"] not in emoji_counts:
                emoji_counts[r["emoji"]] = {"emoji": r["emoji"], "count": 0, "members": []}
            emoji_counts[r["emoji"]]["count"] += 1
            emoji_counts[r["emoji"]]["members"].append(r["member_name"])

        result.append({
            **p,
            "age": age,
            "photo_date": p["uploaded_at"][:10],
            "reactions": list(emoji_counts.values()),
            "image_url": f"/static/uploads/{p['filename']}",
        })

    return {
        "photos": result,
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
        "has_more": page < total_pages,
    }


@app.post("/api/photos/upload")
async def upload_photo(
    file: UploadFile = File(...),
    caption: str = Form(""),
):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type: {ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    # Generate unique filename
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / unique_name

    content = await file.read()
    file_path.write_bytes(content)

    photo = add_photo(unique_name, file.filename, caption)
    return {"ok": True, "photo": {**photo, "image_url": f"/static/uploads/{unique_name}"}}


# ── Reactions ─────────────────────────────────────────────────────────

@app.post("/api/photos/{photo_id}/react")
async def react_to_photo(photo_id: int, member_id: int = Form(...), emoji: str = Form(...)):
    result = toggle_reaction(photo_id, member_id, emoji)
    # Return updated reactions
    reactions = get_reactions(photo_id)
    return {"ok": True, "active": result["active"], "reactions": reactions}


# ── Serve SPA ─────────────────────────────────────────────────────────

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/{path:path}")
async def serve_spa(path: str):
    if path and (Path(BASE_DIR / "static" / path).exists() or path.startswith("uploads/")):
        return FileResponse(BASE_DIR / "static" / path)
    return FileResponse(BASE_DIR / "static" / "index.html")


# ── Init ──────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    init_db()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5555)