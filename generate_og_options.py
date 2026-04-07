"""Generate 3 light OG image options to choose from."""
from PIL import Image, ImageDraw, ImageFont
import os

def load_font(size):
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSDisplay.ttf",
        "/System/Library/Fonts/SFNS.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()

os.makedirs("static/images", exist_ok=True)
W, H = 1200, 630


# ── Option 1: Soft Blush ──────────────────────────────────────────────────────
# White background, rose pink + soft lilac, clean and elegant
img  = Image.new("RGB", (W, H), (255, 252, 254))
draw = ImageDraw.Draw(img)

PINK   = (236, 72, 153)
LILAC  = (168, 85, 247)
ROSE   = (251, 207, 232)
DARK   = (76, 29, 60)
MUTED  = (157, 100, 140)

# Soft pink blob top-left
draw.ellipse([-120, -120, 360, 360], fill=(254, 231, 243))
# Soft purple blob bottom-right
draw.ellipse([800, 350, 1350, 800], fill=(245, 237, 255))

# Top accent bar
draw.rectangle([0, 0, W, 7], fill=PINK)

# Sparkles
draw.text((100, 105), "✦", font=load_font(30), fill=PINK)
draw.text((158, 115), "✦", font=load_font(18), fill=LILAC)
draw.text((700, 100), "✦", font=load_font(22), fill=ROSE)

# Name
draw.text((100, 150), "Sarah Chidzanga", font=load_font(74), fill=DARK)
# Underline
draw.rectangle([100, 248, 400, 254], fill=PINK)
draw.rectangle([400, 248, 575, 254], fill=LILAC)

draw.text((100, 272), "Integration Engineering Intern at Jamf", font=load_font(33), fill=MUTED)
draw.text((100, 328), "Sunsets · Code · Stories from Zimbabwe", font=load_font(27), fill=MUTED)

def pill(draw, x, y, text, font, outline, textcol, bg):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    px, py = 18, 10
    draw.rounded_rectangle([x, y, x+tw+px*2, y+th+py*2], radius=20, fill=bg, outline=outline, width=2)
    draw.text((x+px, y+py), text, font=font, fill=textcol)
    return x + tw + px*2 + 14

fp = load_font(24)
x = 100
x = pill(draw, x, 408, "Flask",      fp, PINK,  PINK,  (254,231,243))
x = pill(draw, x, 408, "AWS Lambda", fp, LILAC, LILAC, (245,237,255))
x = pill(draw, x, 408, "DynamoDB",   fp, PINK,  PINK,  (254,231,243))
pill(draw,     x, 408, "Swift",      fp, LILAC, LILAC, (245,237,255))

draw.text((100, H-95), "♡  sarah-chidzanga.dev", font=load_font(22), fill=PINK)

img.save("static/images/og_option1.png", "PNG")
print("Saved option 1 — Soft Blush")


# ── Option 2: Lavender Dream ──────────────────────────────────────────────────
# Soft lavender background, white card, purple + pink
img  = Image.new("RGB", (W, H), (237, 233, 254))
draw = ImageDraw.Draw(img)

PURPLE = (124, 58, 237)
PINK2  = (219, 39, 119)
WHITE  = (255, 255, 255)
DARK2  = (46, 16, 101)
MUTED2 = (109, 76, 165)

# White card
draw.rounded_rectangle([50, 50, W-50, H-50], radius=28, fill=(255, 255, 255))

# Top bar inside card
draw.rounded_rectangle([50, 50, W-50, 58], radius=10, fill=PURPLE)

# Decorative circle top-right (inside card)
draw.ellipse([820, 60, 1160, 400], outline=(220, 210, 255), width=3)
draw.ellipse([870, 100, 1120, 360], outline=(237, 230, 255), width=2)

draw.text((110, 105), "✦", font=load_font(28), fill=PURPLE)
draw.text((160, 113), "✦", font=load_font(16), fill=PINK2)

draw.text((110, 155), "Sarah Chidzanga", font=load_font(74), fill=DARK2)
draw.rectangle([110, 250, 430, 257], fill=PURPLE)
draw.rectangle([430, 250, 580, 257], fill=PINK2)

draw.text((110, 275), "Integration Engineering Intern at Jamf", font=load_font(33), fill=MUTED2)
draw.text((110, 330), "Sunsets · Code · Stories from Zimbabwe", font=load_font(27), fill=MUTED2)

x = 110
x = pill(draw, x, 410, "Flask",      load_font(24), PURPLE, PURPLE, (243,240,255))
x = pill(draw, x, 410, "AWS Lambda", load_font(24), PINK2,  PINK2,  (253,242,248))
x = pill(draw, x, 410, "DynamoDB",   load_font(24), PURPLE, PURPLE, (243,240,255))
pill(draw,     x, 410, "Swift",      load_font(24), PINK2,  PINK2,  (253,242,248))

draw.text((110, H-100), "♡  sarah-chidzanga.dev", font=load_font(22), fill=PINK2)

img.save("static/images/og_option2.png", "PNG")
print("Saved option 2 — Lavender Dream")


# ── Option 3: Peach Blossom ───────────────────────────────────────────────────
# Warm peach/cream gradient feel, pink + purple on light
img  = Image.new("RGB", (W, H), (255, 247, 250))
draw = ImageDraw.Draw(img)

HOTPINK = (236, 72, 153)
MAUVE   = (168, 85, 247)
PEACH   = (254, 215, 226)
CREAM   = (255, 241, 242)
DARK3   = (80, 20, 55)
MUTED3  = (160, 90, 130)

# Peach blobs
draw.ellipse([-80, -80, 450, 380], fill=(255, 236, 245))
draw.ellipse([750, 300, 1350, 780], fill=(252, 231, 255))
draw.ellipse([900, -80, 1350, 300], fill=(255, 240, 250))

# Thin pink border frame
draw.rounded_rectangle([40, 40, W-40, H-40], radius=24, outline=HOTPINK, width=2)
draw.rounded_rectangle([50, 50, W-50, H-50], radius=22, outline=(251,207,232), width=1)

draw.text((100, 100), "✦", font=load_font(32), fill=HOTPINK)
draw.text((148, 112), "✦", font=load_font(20), fill=MAUVE)
draw.text((178, 102), "✦", font=load_font(14), fill=HOTPINK)

draw.text((100, 155), "Sarah Chidzanga", font=load_font(74), fill=DARK3)

# Wavy underline (dashed using small rectangles)
for i in range(100, 580, 20):
    draw.rectangle([i, 255, i+12, 260], fill=HOTPINK if (i//20)%2==0 else MAUVE)

draw.text((100, 275), "Integration Engineering Intern at Jamf", font=load_font(33), fill=MUTED3)
draw.text((100, 330), "Sunsets · Code · Stories from Zimbabwe", font=load_font(27), fill=MUTED3)

x = 100
x = pill(draw, x, 410, "Flask",      load_font(24), HOTPINK, HOTPINK, (255,236,245))
x = pill(draw, x, 410, "AWS Lambda", load_font(24), MAUVE,   MAUVE,   (248,236,255))
x = pill(draw, x, 410, "DynamoDB",   load_font(24), HOTPINK, HOTPINK, (255,236,245))
pill(draw,     x, 410, "Swift",      load_font(24), MAUVE,   MAUVE,   (248,236,255))

draw.text((100, H-98), "♡  sarah-chidzanga.dev", font=load_font(22), fill=HOTPINK)

img.save("static/images/og_option3.png", "PNG")
print("Saved option 3 — Peach Blossom")

print("\nAll 3 saved to static/images/ — open them in Finder to compare!")
