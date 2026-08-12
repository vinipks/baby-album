# Baby Album 👶

A private family photo timeline for your baby. Each family member gets their own access code. Photos show how old the baby was in **Xm Xw Xd** format. Reactions with emojis.

## Quick Start

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

## Tech

- **Backend:** FastAPI + SQLite
- **Frontend:** Vanilla JS SPA (no framework needed)
- **Storage:** Local filesystem (`static/uploads/`)