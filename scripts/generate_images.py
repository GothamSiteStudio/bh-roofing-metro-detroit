#!/usr/bin/env python
"""Generate photorealistic site imagery for BH Roofing Metro Detroit via the
Gemini image API, then crop/resize/compress to web-optimized WebP.
Idempotent: skips images that already exist in assets/img/. Run again to fill gaps.

Subcommands:
  python generate_images.py            # generate all imagery + variants + why-icons + og
  python generate_images.py variants   # (re)build responsive -480/-800/-1200 variants
  python generate_images.py why-icons  # (re)build the 6 why-card 3D icon illustrations
  python generate_images.py favicons   # (re)build favicon / app-icon PNGs + .ico (no API key needed)
"""
import base64, json, os, sys, time, urllib.request, urllib.error, io
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT, "assets", "img")
RAW_DIR = os.path.join(ROOT, "scripts", "_raw")
os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(RAW_DIR, exist_ok=True)

# API key: from GEMINI_API_KEY env var, or a file pointed to by GEMINI_KEY_FILE.
KEY = os.environ.get("GEMINI_API_KEY", "").strip()
if not KEY:
    kf = os.environ.get("GEMINI_KEY_FILE", "")
    if kf and os.path.exists(kf):
        KEY = open(kf, encoding="utf-8").read().strip()
MODEL = "gemini-2.5-flash-image"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}"

STYLE = (" Professional editorial real-estate & construction photography, natural daylight, clean and crisp, "
         "sharp focus, high detail, photorealistic, inviting. No text, no words, no watermark, "
         "no brand logos, no readable signage, no people's faces in closeups unless specified.")

# name: (prompt, aspect 'wide'|'card'|'portrait', (w,h))
IMAGES = {
 "hero-home": ("A beautiful upscale suburban Michigan two-story home at golden hour with a freshly installed dark "
    "charcoal architectural asphalt shingle roof, crisp ridge line and clean flashing, manicured landscaping, warm "
    "inviting light, wide welcoming exterior composition, cinematic warm light, blue sky with soft clouds.", "wide", (1600,1000)),
 "svc-replacement": ("A brand-new architectural asphalt shingle roof on an attractive metro Detroit colonial home, rich "
    "dimensional charcoal-gray shingles, clean straight courses, new drip edge and ridge vent, bright clear day, curb appeal.", "card", (1200,800)),
 "svc-repair": ("Close up of a professional roofer's gloved hands lifting and replacing a damaged asphalt shingle and "
    "sealing flashing on a residential roof, tools and roofing nails visible, shallow depth of field, skilled craftsmanship.", "card", (1200,800)),
 "svc-storm": ("A residential asphalt shingle roof with visible wind and hail storm damage — lifted and torn shingles, "
    "scattered debris, a blue emergency tarp partially covering one section, overcast dramatic sky after a storm, Michigan home.", "card", (1200,800)),
 "svc-inspection": ("A professional roof inspector in a safety harness kneeling on a residential shingle roof examining "
    "the flashing around a brick chimney with a clipboard, clear day, careful detailed inspection, trustworthy.", "card", (1200,800)),
 "svc-commercial": ("A flat low-slope commercial building roof with a clean white TPO membrane, roof drains and HVAC units, "
    "a worker heat-welding a seam in the distance, bright daytime, professional industrial roofing, no readable signage.", "card", (1200,800)),
 "svc-metal": ("A modern standing-seam metal roof in a deep charcoal-gray finish on an upscale Michigan home, crisp vertical "
    "seams, sleek contemporary architecture, bright clear sky, premium look, sharp reflections.", "card", (1200,800)),
 "svc-gutters": ("Newly installed seamless aluminum gutters and a downspout along the eaves of an attractive suburban home "
    "with a fresh shingle roof, clean straight lines, green lawn, sunny day, crisp detail.", "card", (1200,800)),
 "svc-siding": ("A handsome suburban Michigan home with freshly installed light gray vinyl siding and clean white trim, "
    "soffit and fascia, a section of new shingle roof visible, bright curb-appeal exterior, blue sky.", "card", (1200,800)),
 "svc-ventilation": ("A residential attic interior showing a clean ridge vent and baffled soffit ventilation with new "
    "insulation and rafters, shafts of daylight, tidy well-ventilated attic space, detailed and bright.", "card", (1200,800)),
 "svc-cost": ("A clean neat flat lay on a table: asphalt architectural shingle samples in several colors, a roofing "
    "estimate notepad, a tape measure, and a small metal roofing sample, bright studio light, top-down, organized.", "card", (1200,800)),
 "area-neighborhood": ("A leafy tree-lined street in an attractive metro Detroit Michigan suburb with well-kept colonial "
    "and ranch homes with pitched shingle roofs, green lawns, summer afternoon, wide establishing shot, blue sky.", "wide", (1600,900)),
 "area-neighborhood2": ("A charming autumn street of brick colonial and mid-century ranch homes with shingle roofs in a "
    "Michigan suburb, orange and gold trees, warm afternoon light, welcoming residential scene.", "wide", (1600,900)),
 "process-install": ("Two professional roofers in plain navy work uniforms and safety gear installing architectural "
    "shingles on a residential roof, teamwork, nail gun and chalk line visible, bright daylight, no readable branding.", "card", (1200,800)),
 "about-team": ("A friendly confident professional roofer in a plain navy uniform and cap standing with arms crossed "
    "beside a clean white work van in a Michigan driveway, a house with a new roof behind, approachable, trustworthy, "
    "bright morning light, no readable branding.", "card", (1200,900)),
 "cta-roof": ("A stunning metro Detroit home with a brand-new architectural shingle roof at warm dusk with a glowing "
    "porch light and soft sky, rich inviting tones, crisp roof line against the evening sky.", "wide", (1600,760)),
}

def crop_resize(im, w, h):
    im = im.convert("RGB")
    tw, th = w, h
    sw, sh = im.size
    scale = max(tw/sw, th/sh)
    nw, nh = int(sw*scale+0.5), int(sh*scale+0.5)
    im = im.resize((nw, nh), Image.LANCZOS)
    left = (nw-tw)//2; top = (nh-th)//2
    return im.crop((left, top, left+tw, top+th))

def gen(name, prompt, tries=3, style=None):
    raw_path = os.path.join(RAW_DIR, name+".png")
    if os.path.exists(raw_path):
        return raw_path
    if not KEY:
        raise SystemExit("Set GEMINI_API_KEY (or GEMINI_KEY_FILE) to run image generation.")
    body = {"contents":[{"parts":[{"text": prompt + (STYLE if style is None else style)}]}]}
    for t in range(tries):
        try:
            req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                headers={"Content-Type":"application/json"})
            r = urllib.request.urlopen(req, timeout=180)
            d = json.load(r)
            for p in d["candidates"][0]["content"]["parts"]:
                if "inlineData" in p:
                    open(raw_path,"wb").write(base64.b64decode(p["inlineData"]["data"]))
                    return raw_path
            print(f"  [{name}] no image part, retry"); time.sleep(3)
        except urllib.error.HTTPError as e:
            print(f"  [{name}] HTTP {e.code}: {e.read().decode()[:200]}"); time.sleep(5+t*5)
        except Exception as e:
            print(f"  [{name}] err {e}"); time.sleep(5)
    return None

def make_og(hero_raw):
    """Compose a branded 1200x630 Open Graph image from the hero."""
    out = os.path.join(IMG_DIR, "og-image.jpg")
    im = crop_resize(Image.open(hero_raw), 1200, 630)
    overlay = Image.new("RGBA", im.size, (0,0,0,0))
    od = ImageDraw.Draw(overlay)
    for y in range(im.size[1]):
        a = int(150 * (y/im.size[1])**1.3)
        od.line([(0,y),(im.size[0],y)], fill=(9,20,40,a))
    od.rectangle([0,0,im.size[0],im.size[1]], fill=(9,20,40,70))
    im = Image.alpha_composite(im.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(im)
    def font(sz, bold=True):
        for fp in ([r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf"] if bold
                   else [r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"]):
            if os.path.exists(fp):
                return ImageFont.truetype(fp, sz)
        return ImageFont.load_default()
    d.rectangle([70,300,86,470], fill=(232,161,27))
    d.text((110,300), "BH Roofing", font=font(74), fill=(255,255,255))
    d.text((112,392), "METRO DETROIT", font=font(30), fill=(248,190,76))
    d.text((110,452), "Roof Replacement · Repair · Storm Damage", font=font(28, False), fill=(230,238,246))
    d.text((110,498), "Free Estimates  •  Licensed & Insured", font=font(30), fill=(255,255,255))
    im.save(out, quality=88)
    print("  og-image.jpg written")

# --------------------------------------------------------------------------- #
#  WHY-CARD ICON ILLUSTRATIONS
# --------------------------------------------------------------------------- #
ICON_STYLE = (" Premium minimalist 3D rendered icon illustration for an upscale roofing-company website. "
              "Deep matte navy blue and warm amber gold color palette, soft studio lighting, gentle "
              "soft shadows, subtle reflections, single centered subject, solid very dark navy blue "
              "background, clean, high detail. No text, no words, no letters, no numbers, no watermark.")

WHY_ICONS = {
 "why-clock": "A sleek modern 3D wall clock with warm amber gold hands and markers on a navy face, a few small golden motion streaks around it conveying fast, reliable scheduling.",
 "why-mappin": "A glossy 3D amber gold map location pin standing upright on a small floating stylized navy 3D street-grid map tile with tiny suburban rooftops.",
 "why-roof": "An elegant miniature 3D house with a prominent amber gold pitched shingle roof, clean ridge line, warm golden light, conveying quality roofing.",
 "why-hand": "Two stylized 3D hands in a firm friendly handshake, one with a navy sleeve and one with a warm gray sleeve, subtle amber gold glow, conveying honesty and a fair deal.",
 "why-shield": "A glossy 3D navy and amber gold shield with a small check mark and a subtle roof-peak motif at the top, conveying licensed, insured and guaranteed protection.",
 "why-spark": "A charming miniature 3D suburban house facade with a brand-new amber-lit shingle roof and small golden sparkles floating around the rooftop, conveying curb-appeal and added home value.",
}

def make_why_icons():
    for name, prompt in WHY_ICONS.items():
        webp = os.path.join(IMG_DIR, name + ".webp")
        small = os.path.join(IMG_DIR, name + "-400.webp")
        if os.path.exists(webp) and os.path.exists(small):
            print(f"skip {name} (exists)"); continue
        print(f"generating {name} ...")
        raw = gen(name, prompt, style=ICON_STYLE)
        if not raw:
            print(f"  FAILED {name}"); continue
        im = Image.open(raw)
        crop_resize(im.copy(), 800, 600).save(webp, "WEBP", quality=82, method=6)
        crop_resize(im.copy(), 400, 300).save(small, "WEBP", quality=80, method=6)
        print(f"  -> {name}.webp (800x600) + -400 variant")
    print("why-icons DONE")

# --------------------------------------------------------------------------- #
#  FAVICON / APP ICONS  (drawn with PIL — no API key needed)
# --------------------------------------------------------------------------- #
def _rounded_mask(size, radius):
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([0,0,size-1,size-1], radius=radius, fill=255)
    return m

def draw_icon(size):
    """Navy rounded square with a gold gable roof + house body — matches logo-mark.svg."""
    S = size * 4  # supersample
    im = Image.new("RGB", (S, S), (13,32,53))
    # subtle vertical navy gradient
    top = (28,61,96); bot = (13,32,53)
    for y in range(S):
        t = y / S
        r = int(top[0]*(1-t)+bot[0]*t); g = int(top[1]*(1-t)+bot[1]*t); b = int(top[2]*(1-t)+bot[2]*t)
        ImageDraw.Draw(im).line([(0,y),(S,y)], fill=(r,g,b))
    d = ImageDraw.Draw(im, "RGBA")
    gold = (240,176,40,255); gold_soft = (248,190,76,255)
    cx = S/2
    # gable roof triangle
    apex = (cx, S*0.24)
    left = (S*0.16, S*0.52); right = (S*0.84, S*0.52)
    d.polygon([apex, right, (S*0.70, S*0.52), (cx, S*0.30), (S*0.30, S*0.52), left], fill=gold)
    # house body under roof (semi-transparent gold)
    d.rectangle([S*0.30, S*0.52, S*0.70, S*0.80], fill=(248,190,76,60))
    # door
    d.rounded_rectangle([S*0.44, S*0.63, S*0.56, S*0.80], radius=S*0.05, fill=gold_soft)
    # ground bar
    d.rounded_rectangle([S*0.24, S*0.80, S*0.76, S*0.855], radius=S*0.03, fill=gold)
    im = im.resize((size, size), Image.LANCZOS)
    mask = _rounded_mask(size, int(size*0.23))
    out = Image.new("RGBA", (size, size), (0,0,0,0))
    out.paste(im, (0,0), mask)
    return out

def make_favicons():
    specs = [("icon-512.png",512),("icon-192.png",192),("apple-touch-icon.png",180),
             ("apple-touch-icon-180.png",180),("favicon-32.png",32)]
    for fn, sz in specs:
        draw_icon(sz).save(os.path.join(IMG_DIR, fn))
        print(f"  {fn} ({sz}px)")
    # multi-size .ico at repo root
    ico = draw_icon(256)
    ico.save(os.path.join(ROOT, "favicon.ico"), sizes=[(16,16),(32,32),(48,48),(64,64),(256,256)])
    print("  favicon.ico (root)")
    print("favicons DONE")

# --------------------------------------------------------------------------- #
def make_variants():
    widths = (480, 800, 1200)
    for name, (_prompt, _aspect, (w, h)) in IMAGES.items():
        src_raw = os.path.join(RAW_DIR, name + ".png")
        src_webp = os.path.join(IMG_DIR, name + ".webp")
        src = src_raw if os.path.exists(src_raw) else src_webp
        if not os.path.exists(src):
            print(f"  !! no source for {name}, skipping"); continue
        im0 = Image.open(src)
        for vw in widths:
            if vw >= w:
                continue
            out = os.path.join(IMG_DIR, f"{name}-{vw}.webp")
            if os.path.exists(out):
                continue
            vh = int(round(vw * h / w))
            crop_resize(im0.copy(), vw, vh).save(out, "WEBP", quality=80, method=6)
            print(f"  {name}-{vw}.webp ({vw}x{vh})")
    for name in ("area-neighborhood", "area-neighborhood2"):
        raw = os.path.join(RAW_DIR, name + ".png")
        full = os.path.join(IMG_DIR, name + ".webp")
        if os.path.exists(raw) and os.path.exists(full) and os.path.getsize(full) > 280_000:
            w, h = IMAGES[name][2]
            crop_resize(Image.open(raw), w, h).save(full, "WEBP", quality=74, method=6)
            print(f"  recompressed {name}.webp -> {os.path.getsize(full)//1024}KB")
    print("variants DONE")

def main():
    hero_raw = None
    for name,(prompt,aspect,(w,h)) in IMAGES.items():
        webp = os.path.join(IMG_DIR, name+".webp")
        if os.path.exists(webp):
            print(f"skip {name} (exists)")
            if name=="hero-home": hero_raw = os.path.join(RAW_DIR,"hero-home.png")
            continue
        print(f"generating {name} ...")
        raw = gen(name, prompt)
        if not raw:
            print(f"  FAILED {name}"); continue
        if name=="hero-home": hero_raw = raw
        im = crop_resize(Image.open(raw), w, h)
        im.save(webp, "WEBP", quality=82, method=6)
        if aspect=="wide":
            im.save(os.path.join(IMG_DIR, name+".jpg"), quality=84)
        print(f"  -> {name}.webp ({w}x{h})")
    if hero_raw and os.path.exists(hero_raw):
        make_og(hero_raw)
    print("DONE")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "variants":
        make_variants()
    elif cmd == "why-icons":
        make_why_icons()
    elif cmd == "favicons":
        make_favicons()
    else:
        make_favicons()
        main()
        make_variants()
        make_why_icons()
