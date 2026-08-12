"""
Generate 5 dummy baby photos and seed the database
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont
from datetime import date, timedelta

sys.path.insert(0, '/home/vini/baby-album')
from database import init_db, set_baby_name, set_baby_birth_date, add_family_member, add_photo, toggle_reaction

# Colors - pastel baby girl theme
COLORS = [
    ('#f8c8dc', '#fce4ec'),  # pink
    ('#d8b4e2', '#f0e6f6'),  # lavender
    ('#b8e6d0', '#e0f5ec'),  # mint
    ('#fde4c8', '#fef0d8'),  # peach
    ('#c8d8f8', '#e4ecfc'),  # baby blue
]

EMOJIS = ['👶', '🩷', '🌸', '🦋', '🎀', '🧸', '🍼', '✨', '💕', '☁️']

CAPTIONS = [
    "Coming home from the hospital! So tiny and perfect 🥰",
    "First bath — she loved it! Look at those little toes 🛁",
    "Sleeping like a little angel 😴👼",
    "Tummy time champion! Strong little girl 💪",
    "Meeting Grandma for the first time. Instant love 💕",
]

DATES = [
    date.today() - timedelta(days=0),
    date.today() - timedelta(days=1),
    date.today() - timedelta(days=3),
    date.today() - timedelta(days=5),
    date.today() - timedelta(days=7),
]

UPLOAD_DIR = '/home/vini/baby-album/static/uploads'

def create_dummy_image(bg_color, accent_color, caption, index):
    width, height = 600, 600
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    circle_color = accent_color
    draw.ellipse([50, 50, width-50, height-50], fill=circle_color, outline=None)

    emoji = EMOJIS[index % len(EMOJIS)]
    emoji2 = EMOJIS[(index + 3) % len(EMOJIS)]

    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 120)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Decorative emojis in corners
    draw.text((30, 30), emoji, font=font_large, fill=bg_color)
    draw.text((width-90, 30), emoji2, font=font_large, fill=bg_color)
    draw.text((30, height-90), emoji2, font=font_large, fill=bg_color)
    draw.text((width-90, height-90), emoji, font=font_large, fill=bg_color)

    # Little hearts
    for x, y in [(300, 200), (250, 260), (350, 260), (280, 300), (320, 300)]:
        draw.ellipse([x-8, y-8, x+8, y+8], fill='#ff6b9d')

    # Onesie body
    draw.rounded_rectangle([200, 350, 400, 500], radius=30, fill='#ffffff')
    draw.ellipse([260, 330, 340, 370], fill=accent_color)

    draw.text((width//2 - 100, 540), f"🌸 Day {index+1} 🌸", font=font_small, fill='#5a4a5a')

    filename = f"dummy-baby-{index+1}.png"
    filepath = os.path.join(UPLOAD_DIR, filename)
    img.save(filepath)
    print(f"  Created image: {filename}")
    return filename

# Initialize DB
init_db()
print("DB initialized")

# Set up baby
set_baby_name("Sofia")
set_baby_birth_date(DATES[-1])
print(f"Baby: Sofia, born {DATES[-1]}")

# Add family members
add_family_member("Mom", "mom", is_admin=True)
add_family_member("Dad", "dad", is_admin=True)
print("Family members: Mom (mom), Dad (dad)")

# Create and upload photos
photo_ids = []
for i in range(5):
    bg_color = COLORS[i % len(COLORS)][0]
    accent_color = COLORS[i % len(COLORS)][1]
    filename = create_dummy_image(bg_color, accent_color, CAPTIONS[i], i)
    photo = add_photo(filename, f"photo-{i+1}.png", CAPTIONS[i])
    photo_ids.append(photo['id'])
    print(f"  Uploaded photo {i+1}: {CAPTIONS[i][:30]}...")

# Add some reactions
reactions = [
    (1, 1, '❤️'), (1, 2, '😊'),
    (2, 1, '❤️'), (2, 2, '👶'),
    (3, 1, '💕'), (3, 2, '🎉'),
    (4, 1, '❤️'),
    (5, 2, '😊'),
]
for pid, mid, emoji in reactions:
    toggle_reaction(pid, mid, emoji)

print(f"\nDone! Created {len(photo_ids)} photos with reactions.")
print("Ready to go!")