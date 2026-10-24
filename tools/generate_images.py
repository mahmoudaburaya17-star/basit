# -*- coding: utf-8 -*-
"""يولّد صور بوستات فيسبوك (1080x1080) من content/calendar_data.py.

التشغيل:  python3 tools/generate_images.py
لتغيير اسم البراند أو الألوان عدّل الثوابت تحت وأعد التشغيل.
"""
import os
import sys
import json

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "content"))
from schedule import POSTS  # noqa: E402

BRAND = "بسيط"
TAGLINE = "التيشيرت السادة بالأرقام"
W = H = 1080
MARGIN = 80

BG = "#F4EFE8"
INK = "#1F1F1F"
SOFT = "#E3DACB"
MUTED = "#6B645A"
ACCENT = "#C8553D"
OLIVE = "#3C5A4A"

FONT_PATH = os.path.join(ROOT, "fonts", "Cairo.ttf")  # Cairo (OFL)
W_BOLD, W_REG = 800, 500
LANG = dict(direction="rtl", language="ar")


_cache = {}


def font(size, bold=True):
    key = (size, bold)
    if key not in _cache:
        f = ImageFont.truetype(FONT_PATH, size, layout_engine=ImageFont.Layout.RAQM)
        f.set_variation_by_axes([W_BOLD if bold else W_REG, 0])
        _cache[key] = f
    return _cache[key]


_tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))


def tw(text, f):
    return _tmp.textlength(text, font=f, **LANG)


def wrap(text, f, maxw):
    lines, cur = [], []
    for word in text.split():
        trial = " ".join(cur + [word])
        if cur and tw(trial, f) > maxw:
            lines.append(" ".join(cur))
            cur = [word]
        else:
            cur.append(word)
    if cur:
        lines.append(" ".join(cur))
    return lines


def fit_lines(text, maxw, max_lines, sizes, bold=True):
    for s in sizes:
        f = font(s, bold)
        lines = wrap(text, f, maxw)
        if len(lines) <= max_lines:
            return f, lines, s
    f = font(sizes[-1], bold)
    return f, wrap(text, f, maxw), sizes[-1]


def draw_lines(d, lines, f, x_right, y, fill, lh):
    for ln in lines:
        d.text((x_right, y - int(f.size * 0.2)), ln, font=f, fill=fill, anchor="ra", **LANG)
        y += lh
    return y


def base(kicker=None):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # الشريط العلوي
    d.rectangle([0, 0, W, 14], fill=ACCENT)
    if kicker:
        kf = font(34)
        kw = tw(kicker, kf) + 56
        d.rounded_rectangle([W - MARGIN - kw, 70, W - MARGIN, 128], radius=29, fill=INK)
        d.text((W - MARGIN - 28, 99), kicker, font=kf, fill=BG, anchor="rm", **LANG)
    # الفوتر
    d.line([MARGIN, H - 112, W - MARGIN, H - 112], fill=SOFT, width=3)
    d.text((W - MARGIN, H - 56), BRAND, font=font(52), fill=INK, anchor="rm", **LANG)
    d.text((MARGIN, H - 56), TAGLINE, font=font(28, False), fill=MUTED, anchor="lm", **LANG)
    return img, d


def title_block(d, title, y=170, maxw=W - 2 * MARGIN, max_lines=3, sizes=(84, 76, 68, 60, 54)):
    f, lines, s = fit_lines(title, maxw, 1, [z for z in sizes if z >= 60] or sizes)
    if len(lines) != 1:
        f, lines, s = fit_lines(title, maxw, max_lines, sizes)
    lh = int(s * 1.4)
    y = draw_lines(d, lines, f, W - MARGIN, y, INK, lh)
    return y


def tee(d, cx, top, w, h, color, outline=INK, collar=BG):
    """رسم تيشيرت بسيط. (cx, top) مركز الكتف، w عرض الجسم، h الطول."""
    def P(x, y):
        return (cx + x * w, top + y * h)
    pts = [(-0.13, 0), (-0.30, 0.05), (-0.52, 0.22), (-0.43, 0.36), (-0.30, 0.29), (-0.30, 1.0),
           (0.30, 1.0), (0.30, 0.29), (0.43, 0.36), (0.52, 0.22), (0.30, 0.05), (0.13, 0)]
    d.polygon([P(*p) for p in pts], fill=color, outline=outline)
    d.line([P(*p) for p in pts] + [P(*pts[0])], fill=outline, width=3)
    # فتحة الرقبة
    x0, y0 = P(-0.13, -0.045)
    x1, y1 = P(0.13, 0.085)
    d.ellipse([x0, y0, x1, y1], fill=collar, outline=outline, width=3)


def badge(d, cx, cy, n, r=34):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ACCENT)
    d.text((cx, cy - 2), str(n), font=font(38), fill="white", anchor="mm")


# ----------------------------- القوالب -----------------------------

def t_statement(spec):
    img, d = base(spec.get("kicker"))
    f, lines, s = fit_lines(spec["title"], W - 2 * MARGIN, 4, (110, 98, 90, 80, 70))
    lh = int(s * 1.45)
    total = lh * len(lines)
    y = 235
    draw_lines(d, lines, f, W - MARGIN, y, INK, lh)
    ay = y + total + 20
    d.rectangle([W - MARGIN - 160, ay, W - MARGIN, ay + 10], fill=ACCENT)
    y_end = ay + 30
    if spec.get("sub"):
        sf, sl, ss = fit_lines(spec["sub"], W - 2 * MARGIN, 3, (44, 40, 36), bold=False)
        y_end = draw_lines(d, sl, sf, W - MARGIN, ay + 50, MUTED, int(ss * 1.5))
    size = min(300, H - 150 - y_end - 20)
    if size >= 150:
        tee(d, W - MARGIN - int(size * 0.5), y_end + 20, int(size * 0.95), size, SOFT, outline=MUTED)
    return img


def t_list(spec):
    img, d = base(spec.get("kicker"))
    y0 = title_block(d, spec["title"], y=165, max_lines=2, sizes=(74, 68, 62, 56))
    items = spec["items"]
    numbered = spec.get("numbered", False)
    avail_top, avail_bot = y0 + 30, H - 150
    for s in (46, 42, 38, 34, 30):
        f = font(s, False)
        maxw = W - 2 * MARGIN - 110
        blocks = [wrap(it, f, maxw) for it in items]
        lh = int(s * 1.5)
        gap = int(s * 0.7)
        total = sum(len(b) * lh for b in blocks) + gap * (len(blocks) - 1)
        if total <= avail_bot - avail_top:
            break
    y = avail_top + max(0, (avail_bot - avail_top - total) // 2) if len(items) <= 4 else avail_top
    for i, b in enumerate(blocks, 1):
        cy = y + lh // 2
        if numbered:
            badge(d, W - MARGIN - 34, cy, i, r=32)
        else:
            d.ellipse([W - MARGIN - 40, cy - 12, W - MARGIN - 16, cy + 12], fill=ACCENT)
        y = draw_lines(d, b, f, W - MARGIN - 90, y, INK, lh)
        y += gap
    return img


def t_compare(spec):
    img, d = base(spec.get("kicker"))
    y0 = title_block(d, spec["title"], y=165, max_lines=2, sizes=(74, 68, 62, 56))
    colw = (W - 2 * MARGIN - 40) // 2
    top, bot = y0 + 40, H - 150
    f = font(40, False)
    boxes = [(W - MARGIN - colw, spec["left"], OLIVE), (MARGIN, spec["right"], ACCENT)]
    need = 0
    for _, (_, items), _ in boxes:
        h = 150 + sum(len(wrap(it, f, colw - 100)) * 54 + 30 for it in items) + 20
        need = max(need, h)
    bot = min(bot, top + need)
    for x, (head, items), col in boxes:
        d.rounded_rectangle([x, top, x + colw, bot], radius=28, fill="white", outline=SOFT, width=3)
        d.rounded_rectangle([x, top, x + colw, top + 100], radius=28, fill=col)
        d.rectangle([x, top + 60, x + colw, top + 100], fill=col)
        hf, hl, hs = fit_lines(head, colw - 50, 1, (46, 42, 38, 34))
        d.text((x + colw // 2, top + 52), hl[0], font=hf, fill="white", anchor="mm", **LANG)
        y = top + 140
        for it in items:
            lines = wrap(it, f, colw - 100)
            cy = y + 27
            d.ellipse([x + colw - 56, cy - 9, x + colw - 38, cy + 9], fill=col)
            y = draw_lines(d, lines, f, x + colw - 74, y, INK, 54)
            y += 30
    return img


def t_poll(spec):
    img, d = base(spec.get("kicker"))
    y0 = title_block(d, spec["title"], y=165, max_lines=3, sizes=(70, 64, 58, 52))
    opts = spec["options"]
    top, bot = y0 + 30, H - 150
    n = len(opts)
    gap = 18
    bh = min(120, (bot - top - gap * (n - 1)) // n)
    f = font(40, False)
    y = top
    for i, o in enumerate(opts, 1):
        d.rounded_rectangle([MARGIN, y, W - MARGIN, y + bh], radius=26, fill="white", outline=SOFT, width=3)
        badge(d, W - MARGIN - 56, y + bh // 2, i, r=32)
        lines = wrap(o, f, W - 2 * MARGIN - 150)
        ty = y + (bh - len(lines) * 50) // 2
        draw_lines(d, lines, f, W - MARGIN - 110, ty, INK, 50)
        y += bh + gap
    return img


def t_ladder(spec):
    img, d = base(spec.get("kicker"))
    y0 = title_block(d, spec["title"], y=165, max_lines=2, sizes=(70, 64, 58, 52))
    rows = spec["rows"]
    colors = [OLIVE, ACCENT, INK]
    y = y0 + 45
    maxw = W - 2 * MARGIN
    pf = font(38)
    for (label, price, frac), col in zip(rows, colors):
        d.text((W - MARGIN, y - 8), label, font=font(40), fill=INK, anchor="ra", **LANG)
        y += 74
        need = int(tw(price, pf)) + 56
        bw = max(need, int(maxw * frac))
        d.rounded_rectangle([W - MARGIN - bw, y, W - MARGIN, y + 74], radius=20, fill=col)
        d.text((W - MARGIN - 28, y + 37), price, font=pf, fill="white", anchor="rm", **LANG)
        y += 74 + 22
    if spec.get("note"):
        nf, nl, ns = fit_lines(spec["note"], W - 2 * MARGIN, 1, (28, 26, 24), bold=False)
        draw_lines(d, nl, nf, W - MARGIN, H - 150, MUTED, 36)
    return img


def t_swatch(spec):
    img, d = base(spec.get("kicker"))
    y0 = title_block(d, spec["title"], y=165, max_lines=2, sizes=(74, 68, 62, 56))
    if spec.get("sub"):
        d.text((W - MARGIN, y0 + 5), spec["sub"], font=font(36, False), fill=MUTED, anchor="ra", **LANG)
    colors = spec["colors"]
    cols = 3
    cw = (W - 2 * MARGIN) // cols
    top = y0 + 80
    rowh = (H - 150 - top) // 2
    for i, (name, hexv) in enumerate(colors):
        r, c = divmod(i, cols)
        cx = W - MARGIN - cw * c - cw // 2
        ty = top + r * rowh
        tee(d, cx, ty + 20, 150, 160, hexv, outline=INK, collar=BG)
        label = name
        if spec.get("numbered"):
            badge(d, cx + 72, ty + 30, i + 1, r=26)
        d.text((cx, ty + 20 + 160 + 34), label, font=font(36), fill=INK, anchor="mm", **LANG)
    return img


def t_fits(spec):
    img, d = base(spec.get("kicker"))
    y0 = title_block(d, spec["title"], y=165, max_lines=2, sizes=(74, 68, 62, 56))
    if spec.get("sub"):
        d.text((W - MARGIN, y0 + 5), spec["sub"], font=font(36, False), fill=MUTED, anchor="ra", **LANG)
    fits = [("سليم", 0.62, 1.0, OLIVE), ("ريجولار", 0.78, 1.05, "#8D9096"), ("أوفرسايز", 0.98, 1.15, ACCENT)]
    cw = (W - 2 * MARGIN) // 3
    base_w, base_h = 300, 330
    for i, (name, ws, hs, col) in enumerate(fits):
        cx = W - MARGIN - cw * i - cw // 2
        w, h = int(base_w * ws * 0.62), int(base_h * hs * 0.62)
        top = 480 + (int(base_h * 1.15 * 0.62) - h)
        tee(d, cx, top, w, h, "white", outline=col)
        d.line([cx - int(w * 0.3), top + h + 22, cx + int(w * 0.3), top + h + 22], fill=col, width=5)
        d.text((cx, top + h + 70), name, font=font(40), fill=INK, anchor="mm", **LANG)
        if spec.get("numbered"):
            badge(d, cx, top + h + 140, i + 1, r=30)
    return img


def t_qa(spec):
    img, d = base(spec.get("kicker"))
    y = 170
    d.text((W - MARGIN, y), "السؤال", font=font(36), fill=ACCENT, anchor="ra", **LANG)
    f, lines, s = fit_lines(spec["q"], W - 2 * MARGIN, 3, (68, 62, 56, 50))
    y = draw_lines(d, lines, f, W - MARGIN, y + 60, INK, int(s * 1.35))
    y += 40
    d.rounded_rectangle([MARGIN, y, W - MARGIN, H - 150], radius=30, fill="white", outline=SOFT, width=3)
    d.text((W - MARGIN - 40, y + 30), "الجواب", font=font(36), fill=OLIVE, anchor="ra", **LANG)
    af, al, as_ = fit_lines(spec["a"], W - 2 * MARGIN - 80, 7, (46, 42, 38, 34), bold=False)
    draw_lines(d, al, af, W - MARGIN - 40, y + 100, INK, int(as_ * 1.5))
    return img


def t_bignum(spec):
    img, d = base(spec.get("kicker"))
    y0 = title_block(d, spec["title"], y=165, max_lines=2, sizes=(74, 68, 62, 56))
    y = y0 + 40
    cols = [OLIVE, ACCENT]
    for (big, small), col in zip(spec["lines"], cols):
        d.rounded_rectangle([MARGIN, y, W - MARGIN, y + 250], radius=30, fill="white", outline=SOFT, width=3)
        d.text((W - MARGIN - 50, y + 85), big, font=font(120), fill=col, anchor="rm", **LANG)
        d.text((W - MARGIN - 50, y + 190), small, font=font(36, False), fill=INK, anchor="rm", **LANG)
        y += 290
    if spec.get("note"):
        d.text((W - MARGIN, H - 190), spec["note"], font=font(30, False), fill=MUTED, anchor="ra", **LANG)
    return img


COLORS = {"أبيض": "#F7F5F0", "أسود": "#1C1C1C", "كحلي": "#1F2F4D", "رمادي": "#8D9096", "رمادي غامق": "#4A4D52",
          "زيتي": "#5B6340", "بيج": "#CDB89A", "بني": "#6B4A33", "سماوي": "#8FB4D6",
          "جينز غامق": "#2E3F5C", "جينز فاتح": "#7F9BBF"}


def pants(d, cx, top, w, h, color, outline=INK):
    def P(x, y):
        return (cx + x * w, top + y * h)
    pts = [(-0.45, 0), (0.45, 0), (0.40, 1.0), (0.04, 1.0), (0.0, 0.30), (-0.04, 1.0), (-0.40, 1.0)]
    d.polygon([P(*p) for p in pts], fill=color)
    d.line([P(*p) for p in pts] + [P(*pts[0])], fill=outline, width=3)


def t_outfit(spec):
    img, d = base(spec.get("kicker"))
    y0 = title_block(d, spec["title"], y=165, max_lines=2, sizes=(74, 68, 62, 56))
    tee_c = COLORS[spec["tee"]]
    pan_c = COLORS[spec["pants"]]
    sho_c = COLORS[spec["shoe_color"]]
    cx = 300
    top = y0 + 50
    tee(d, cx, top, 230, 250, tee_c)
    pants(d, cx, top + 235, 200, 330, pan_c)
    # أحذية
    for dx in (-48, 48):
        d.rounded_rectangle([cx + dx - 42, top + 235 + 330 - 8, cx + dx + 42, top + 235 + 330 + 32], radius=16,
                            fill=sho_c, outline=INK, width=3)
    # قايمة
    rows = [("التيشيرت", spec["tee"], tee_c), ("البنطلون", spec["pants"], pan_c), ("الحذاء", spec["shoe"], sho_c)]
    y = y0 + 90
    for label, name, col in rows:
        d.text((W - MARGIN, y), label, font=font(34, False), fill=MUTED, anchor="ra", **LANG)
        d.ellipse([W - MARGIN - 560, y + 72, W - MARGIN - 520, y + 112], fill=col, outline=INK, width=3)
        d.text((W - MARGIN - 36, y + 70), name, font=font(46), fill=INK, anchor="ra", **LANG)
        y += 170
    return img


TEMPLATES = {"statement": t_statement, "list": t_list, "compare": t_compare, "poll": t_poll,
             "ladder": t_ladder, "swatch": t_swatch, "fits": t_fits, "qa": t_qa, "bignum": t_bignum, "outfit": t_outfit}


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "images")
    os.makedirs(out, exist_ok=True)
    manifest = []
    for p in POSTS:
        spec = p["image"]
        name = None
        if spec:
            name = "%s.png" % p["image_key"]
            img = TEMPLATES[spec["t"]](spec)
            img.save(os.path.join(out, name), optimize=True)
        manifest.append({**{k: p[k] for k in ("id", "date", "time", "slot", "pillar", "text")},
                         "image": ("images/" + name) if name else None,
                         "alt": (spec.get("title") if spec else None),
                         **{k: p[k] for k in ("video", "video_cover", "moved_from") if p.get(k)}})
    if len(sys.argv) <= 1:
        with open(os.path.join(ROOT, "content", "calendar.json"), "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, ensure_ascii=False, indent=2)
    print("images:", sum(1 for m in manifest if m["image"]), "posts:", len(manifest))


if __name__ == "__main__":
    main()
