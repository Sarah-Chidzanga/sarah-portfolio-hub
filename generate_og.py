"""Generate static/images/og.png using the botanical colour palette."""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1200, 630

CREAM   = (242, 222, 199)   # #F2DEC7 — background
BLUSH   = (225, 184, 162)   # #E1B8A2 — soft border
ROSE    = (207, 125, 101)   # #CF7D65 — primary accent
KHAKI   = (171, 166, 111)   # #ABA66F — secondary accent
SAGE    = (153, 180, 170)   # #99B4AA — soft sage
OLIVE   = (107, 109, 67)    # #6B6D43 — muted text
BROWN   = (61, 31, 13)      # #3D1F0D — dark text
WHITE   = (253, 248, 243)   # #FDF8F3 — card white

img  = Image.new("RGB", (W, H), CREAM)
draw = ImageDraw.Draw(img)

# Soft blush blob — top left
draw.ellipse([-150, -150, 450, 350], fill=(237, 213, 179))
# Soft sage blob — bottom right
draw.ellipse([750, 300, 1350, 800], fill=(220, 235, 228))
# Small rose blob — top right
draw.ellipse([900, -100, 1300, 280], fill=(240, 215, 205))

# White card panel
draw.rounded_rectangle([55, 55, W-55, H-55], radius=24, fill=WHITE)

# Rose top bar on card
draw.rounded_rectangle([55, 55, W-55, 63], radius=12, fill=ROSE)

# Decorative concentric circles — bottom right
draw.ellipse([790, 240, 1150, 600], outline=BLUSH, width=3)
draw.ellipse([840, 280, 1110, 560], outline=(200, 175, 155), width=2)
draw.ellipse([890, 320, 1070, 520], outline=SAGE, width=2)

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

# Sparkles
draw.text((105, 100), "✦", font=load_font(28), fill=ROSE)
draw.text((150, 110), "✦", font=load_font(16), fill=SAGE)
draw.text((174, 103), "✦", font=load_font(12), fill=KHAKI)

# Name
draw.text((105, 148), "Sarah Chidzanga", font=load_font(72), fill=BROWN)

# Two-tone underline
draw.rectangle([105, 243, 390, 249], fill=ROSE)
draw.rectangle([390, 243, 565, 249], fill=SAGE)

# Role + tagline
draw.text((105, 268), "Integration Engineering Intern at Jamf", font=load_font(32), fill=OLIVE)
draw.text((105, 322), "Sunsets · Code · Stories from Zimbabwe", font=load_font(26), fill=(150, 120, 95))

# Pills
def pill(x, y, text, color, bg):
    font = load_font(23)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    px, py = 16, 9
    draw.rounded_rectangle([x, y, x+tw+px*2, y+th+py*2], radius=18, fill=bg, outline=color, width=2)
    draw.text((x+px, y+py), text, font=font, fill=color)
    return x + tw + px*2 + 12

x = 105
x = pill(x, 400, "Flask",      ROSE,  (247, 235, 228))
x = pill(x, 400, "AWS Lambda", SAGE,  (228, 238, 234))
x = pill(x, 400, "DynamoDB",   KHAKI, (238, 237, 220))
pill(x,     400, "Swift",      ROSE,  (247, 235, 228))

# Bottom signature
draw.text((105, H-95), "♡  sarah-chidzanga.dev", font=load_font(21), fill=ROSE)

os.makedirs("static/images", exist_ok=True)
img.save("static/images/og.png", "PNG", optimize=True)
print(f"Saved static/images/og.png  ({os.path.getsize('static/images/og.png')//1024} KB)")
