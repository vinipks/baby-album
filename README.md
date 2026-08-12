# Baby Album 👶

A private family photo timeline for your baby. Each family member gets their own access code. Photos show how old the baby was in **Xm Xw Xd** format. Reactions with emojis.

## 🚀 Deploy to Render (free, 1-click)

This is the easiest way to access your album from anywhere. Render connects to this GitHub repo, runs the Python backend, and gives you a public URL like `https://baby-album.onrender.com`.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/vinipks/baby-album)

**Steps:**
1. Click the button above → sign in with GitHub (or create a free account)
2. It will pre-fill the repo — click **Deploy**
3. Wait ~2 minutes for the build
4. Open the URL it gives you (e.g. `https://baby-album.onrender.com`)
5. Set up your baby's name + birth date, log in as `mom`/`dad`

> ⚠️ **Note:** Render's free tier stores uploaded photos in ephemeral storage — they're reset on each redeploy. For a permanent backup, also run it locally (below) and keep your photos there.

## Quick Start (local)

```bash
pip install -r requirements.txt
python main.py
```

Then open **http://localhost:5555**

1. Set up baby's name and birth date
2. Log in as **Mom** (code: `mom`) or **Dad** (code: `dad`)
3. Start uploading photos!
4. Add family members and give them their own access codes

## Features

- 📸 **Timeline view** — scroll through photos chronologically
- 👶 **Age stamps** — each photo shows months, weeks, days since birth
- ❤️ **Reactions** — tap a heart, smiley, or any emoji
- 🔐 **Private** — each family member has a unique access code
- 👑 **Admin** — Mom & Dad can upload photos and manage members
- 📱 **Mobile-friendly** — works great on phones
- 🎀 **Pastel baby girl theme** — soft pinks, lavenders, mint

## Default Admin Codes

| Name | Code |
|------|------|
| Mom  | `mom` |
| Dad  | `dad` |

Change these or add more from the Family Members panel in the app.

## Demo Content

Run `python seed_dummy.py` to populate the album with 5 sample photos and reactions for testing.

## Tech

- **Backend:** FastAPI + SQLite
- **Frontend:** Vanilla JS SPA (no framework needed)
- **Storage:** Local filesystem (`static/uploads/`)
- **Deployment:** Dockerfile + render.yaml (Render free tier)