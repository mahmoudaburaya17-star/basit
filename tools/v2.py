# -*- coding: utf-8 -*-
"""محرك التصميم v2 (نوفمبر): خلفية داكنة فاخرة، كاروسيل 1080x1350 وريلز 1080x1920 بحركة كلمة بكلمة.
كل الرسم بالكود (Pillow). مفيش صور توليدية."""
import math
import os
import random
import sys
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_images as gi  # noqa: E402
from generate_images import font, tw, LANG  # noqa: E402

ROOT = gi.ROOT
C = dict(bg1="#18251E", bg2="#0C120F", cream="#F3ECDD", mute="#A9B3A9", acc="#E6784F", acc2="#F2B36B",
         sage="#8DB59C", card="#1F2E26", line="#34463B", white="#FFFFFF")


def rgb(h, a=255):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


_bg_cache = {}


def background(w, h):
    k = (w, h)
    if k in _bg_cache:
        return _bg_cache[k].copy()
    top, bot = rgb(C["bg1"]), rgb(C["bg2"])
    img = Image.new("RGBA", (w, h))
    px = img.load()
    for y in range(h):
        t = y / (h - 1)
        c = tuple(int(top[i] * (1 - t) + bot[i] * t) for i in range(3)) + (255,)
        for x in range(w):
            px[x, y] = c
    # توهج دافي ناعم
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([-w * 0.2, -h * 0.3, w * 0.9, h * 0.32], fill=rgb("#3C6B52", 85))
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    img = Image.alpha_composite(img, glow)
    # حبيبات خفيفة
    rnd = random.Random(7)
    grain = Image.effect_noise((w, h), 22).convert("L").point(lambda v: 0 if v < 128 else int((v - 128) * 0.25))
    g = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    g.putalpha(grain)
    img = Image.alpha_composite(img, g)
    _bg_cache[k] = img
    return img.copy()


def ease(p):
    p = max(0.0, min(1.0, p))
    return 1 - (1 - p) ** 3


def prog(t, t0, dur=0.55):
    return ease((t - t0) / dur)


def words_layout(text, size, maxw, bold=True):
    """يرجّع أسطر، كل سطر قايمة كلمات بإحداثيات x (من اليمين) لعرض RTL."""
    f = font(size, bold)
    sp = tw(" ", f) or size * 0.28
    lines, cur, curw = [], [], 0
    for word in text.split():
        ww = tw(word, f)
        add = ww if not cur else sp + ww
        if cur and curw + add > maxw:
            lines.append(cur)
            cur, curw = [], 0
            add = ww
        cur.append((word, ww))
        curw += add
    if cur:
        lines.append(cur)
    out = []
    for ln in lines:
        x = 0
        row = []
        for word, ww in ln:
            row.append((word, x, ww))
            x += ww + sp
        out.append((row, x - sp))
    return out


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.img = background(w, h)

    def layer(self):
        return Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))

    def put(self, ly, alpha=1.0):
        if alpha < 1.0:
            ly.putalpha(ly.getchannel("A").point(lambda v: int(v * alpha)))
        self.img = Image.alpha_composite(self.img, ly)

    def text(self, s, xr, y, size, color=None, bold=True, alpha=1.0, rise=0, anchor="ra"):
        if alpha <= 0:
            return
        ly = self.layer()
        ImageDraw.Draw(ly).text((xr, y + rise), s, font=font(size, bold), fill=rgb(color or C["cream"]),
                                anchor=anchor, **LANG)
        self.put(ly, alpha)

    def block(self, s, xr, y, size, maxw, color=None, bold=True, lh=1.38, t=None, t0=0.0, step=0.12,
              dur=0.45, align="right"):
        """فقرة: لو t اتحدد بتظهر كلمة بكلمة (كينيتك). بترجّع y بعد الفقرة."""
        lay = words_layout(s, size, maxw, bold)
        idx = 0
        for li, (row, lw) in enumerate(lay):
            yy = y + int(li * size * lh)
            off = 0 if align == "right" else (maxw - lw) / 2 if align == "center" else 0
            for word, x, ww in row:
                a = 1.0
                rise = 0
                if t is not None:
                    p = prog(t, t0 + idx * step, dur)
                    a, rise = p, int((1 - p) * 26)
                if a > 0:
                    self.text(word, xr - x - off, yy, size, color, bold, a, rise)
                idx += 1
        return y + int(len(lay) * size * lh)

    def rrect(self, box, fill, radius=28, alpha=1.0, outline=None, width=2):
        ly = self.layer()
        ImageDraw.Draw(ly).rounded_rectangle(box, radius=radius, fill=rgb(fill) if fill else None,
                                             outline=rgb(outline) if outline else None, width=width)
        self.put(ly, alpha)

    def paste_icon(self, icon, cx, cy, alpha=1.0):
        ly = self.layer()
        ly.paste(icon, (int(cx - icon.width / 2), int(cy - icon.height / 2)), icon)
        self.put(ly, alpha)

    def wordmark(self, y=64, counter=None):
        d = ImageDraw.Draw(self.img)
        d.text((self.w - 80, y), "بسيط", font=font(54), fill=rgb(C["cream"]), anchor="rm", **LANG)
        d.ellipse([self.w - 80 - tw("بسيط", font(54)) - 34, y - 8, self.w - 80 - tw("بسيط", font(54)) - 18, y + 8],
                  fill=rgb(C["acc"]))
        if counter:
            d.text((80, y), counter, font=font(34, False), fill=rgb(C["mute"]), anchor="lm")


# ---------------- رسومات (بتتعمل على مقياس 3x وتتصغّر لحدة أعلى) ----------------
S = 3


def icon_canvas(w, h):
    return Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))


def finish(img):
    return img.resize((img.width // S, img.height // S), Image.LANCZOS)


def tee_icon(w=560, h=470, base="#E8E1D2", shade="#BFB6A2", collar="#CFC6B3"):
    im = icon_canvas(w, h)
    d = ImageDraw.Draw(im)
    sx, sy, oy = w / 1.16, h * 0.93, h * 0.05

    def P(x, y):
        return ((w / 2 + x * sx) * S, (oy + y * sy) * S)
    pts = [(-0.12, 0), (-0.30, 0.055), (-0.58, 0.25), (-0.47, 0.40), (-0.30, 0.31), (-0.30, 1.0),
           (0.30, 1.0), (0.30, 0.31), (0.47, 0.40), (0.58, 0.25), (0.30, 0.055), (0.12, 0)]
    d.polygon([P(*p) for p in pts], fill=rgb(base))
    # ظل ناعم على الجنب الأيمن وتحت الإبط
    d.polygon([P(0.30, 0.31), P(0.30, 1.0), P(0.215, 1.0), P(0.235, 0.36)], fill=rgb("#D2C9B6"))
    d.polygon([P(0.47, 0.40), P(0.30, 0.31), P(0.30, 0.37), P(0.40, 0.44)], fill=rgb("#C4BBA7"))
    # طيّات خفيفة
    d.line([P(-0.10, 0.70), P(-0.02, 0.78), P(0.04, 0.9)], fill=rgb("#D4CCBA"), width=int(2.5 * S))
    d.line([P(-0.22, 0.55), P(-0.17, 0.66)], fill=rgb("#D8D0BE"), width=int(2.5 * S))
    # حافة الأكمام والذيل
    for sgn in (-1, 1):
        d.line([P(sgn * 0.58, 0.25), P(sgn * 0.47, 0.40)], fill=rgb(shade), width=int(5 * S))
    d.line([P(-0.30, 0.965), P(0.30, 0.965)], fill=rgb("#CEC5B2"), width=int(2.5 * S))
    # الياقة
    x0, y0 = P(-0.145, -0.03)
    x1, y1 = P(0.145, 0.115)
    d.ellipse([x0, y0, x1, y1], fill=rgb(collar))
    x0, y0 = P(-0.112, -0.005)
    x1, y1 = P(0.112, 0.082)
    d.ellipse([x0, y0, x1, y1], fill=rgb(C["bg1"]))
    return finish(im)


def weave_icon(w, h, density=22, jitter=0.0, color="#E8E1D2", bgc="#0C120F", seed=1):
    """خيوط قماش: density = عدد الخيوط. كل ما قل العدد الفراغات أكبر."""
    im = icon_canvas(w, h)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w * S, h * S], radius=26 * S, fill=rgb(bgc))
    rnd = random.Random(seed)
    gap = w / density
    thick = max(2.0, gap * 0.62)
    x = gap / 2
    while x < w:
        xx = (x + rnd.uniform(-jitter, jitter)) * S
        d.line([(xx, 0), (xx, h * S)], fill=rgb(color), width=int(thick * S))
        x += gap
    y = gap / 2
    while y < h:
        yy = (y + rnd.uniform(-jitter, jitter)) * S
        # الخيوط الأفقية فوق/تحت
        d.line([(0, yy), (w * S, yy)], fill=rgb(color, 215), width=int(thick * S * 0.9))
        y += gap
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w * S, h * S], radius=26 * S, fill=255)
    im.putalpha(Image.composite(im.getchannel("A"), Image.new("L", im.size, 0), mask))
    return finish(im)


def badge_icon(good, r=34):
    im = icon_canvas(r * 2, r * 2)
    d = ImageDraw.Draw(im)
    col = C["sage"] if good else C["acc"]
    d.ellipse([0, 0, r * 2 * S, r * 2 * S], fill=rgb(col))
    k = r * S
    if good:
        d.line([(k * 0.55, k * 1.05), (k * 0.9, k * 1.4), (k * 1.5, k * 0.65)], fill=rgb("#0C120F"), width=int(6 * S), joint="curve")
    else:
        d.line([(k * 0.65, k * 0.65), (k * 1.35, k * 1.35)], fill=rgb("#0C120F"), width=int(6 * S))
        d.line([(k * 1.35, k * 0.65), (k * 0.65, k * 1.35)], fill=rgb("#0C120F"), width=int(6 * S))
    return finish(im)


def collar_icon(w=380, h=300, stretched=False):
    im = icon_canvas(w, h)
    d = ImageDraw.Draw(im)
    cx, cy = w / 2 * S, h / 2 * S
    rx, ry = (150 if not stretched else 175) * S, (96 if not stretched else 110) * S
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=rgb("#CFC6B3"))
    rx2, ry2 = rx - 34 * S, ry - 30 * S
    d.ellipse([cx - rx2, cy - ry2, cx + rx2, cy + ry2], fill=rgb("#1F2E26"))
    # خطوط الريب
    for i in range(36):
        a = i / 36 * 2 * math.pi
        x0, y0 = cx + math.cos(a) * rx2, cy + math.sin(a) * ry2
        x1, y1 = cx + math.cos(a) * rx, cy + math.sin(a) * ry
        d.line([(x0, y0), (x1, y1)], fill=rgb("#B5AB96"), width=int(2 * S))
    return finish(im)


def seam_icon(w=380, h=300, good=True):
    im = icon_canvas(w, h)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w * S, h * S], radius=26 * S, fill=rgb("#E8E1D2"))
    pts = []
    for i in range(0, 101):
        x = (30 + i * (w - 60) / 100) * S
        y = (h / 2 + (0 if good else math.sin(i / 100 * 5 * math.pi) * 20 + (i % 7) * 1.4)) * S
        pts.append((x, y))
    # خط الخياطة المتقطع
    for k in range(0, len(pts) - 2, 3):
        d.line([pts[k], pts[k + 1]], fill=rgb("#E6784F"), width=int(6 * S))
    d.line([(30 * S, (h / 2 - 22) * S), ((w - 30) * S, (h / 2 - 22) * S)], fill=rgb("#CFC6B3"), width=int(3 * S))
    return finish(im)


def hem_icon(w=380, h=300, good=True):
    im = icon_canvas(w, h)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w * S, h * S], radius=26 * S, fill=rgb("#E8E1D2"))
    rows = [h * 0.42, h * 0.58] if good else [h * 0.5]
    for r_i, y in enumerate(rows):
        x = 30
        while x < w - 40:
            off = 0 if good else math.sin(x / 18) * 9
            d.line([(x * S, (y + off) * S), ((x + 16) * S, (y + off + (0 if good else 3)) * S)], fill=rgb("#E6784F" if good else "#B5654B"), width=int(5 * S))
            x += 24 if good else 24 + (x % 11)
    d.line([(0, (h * 0.86) * S), (w * S, (h * 0.86) * S)], fill=rgb("#CFC6B3"), width=int(3 * S))
    return finish(im)


def surface_icon(w=380, h=300, good=True):
    im = icon_canvas(w, h)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w * S, h * S], radius=26 * S, fill=rgb("#E8E1D2"))
    rnd = random.Random(3)
    if not good:
        for _ in range(46):
            x, y, r = rnd.uniform(24, w - 24), rnd.uniform(24, h - 24), rnd.uniform(5, 11)
            d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=rgb("#CFC6B3"), outline=rgb("#B5AB96"), width=int(2 * S))
    else:
        for yy in range(30, h - 20, 26):
            d.line([(24 * S, yy * S), ((w - 24) * S, yy * S)], fill=rgb("#D9D1BF"), width=int(3 * S))
    return finish(im)


def sun_icon(w=380, h=300):
    im = icon_canvas(w, h)
    d = ImageDraw.Draw(im)
    cx, cy = w / 2 * S, h / 2 * S
    d.ellipse([cx - 52 * S, cy - 52 * S, cx + 52 * S, cy + 52 * S], fill=rgb("#F2B36B"))
    for i in range(12):
        a = i / 12 * 2 * math.pi
        d.line([(cx + math.cos(a) * 74 * S, cy + math.sin(a) * 74 * S), (cx + math.cos(a) * 112 * S, cy + math.sin(a) * 112 * S)], fill=rgb("#F2B36B"), width=int(8 * S))
    return finish(im)


# ---------------- أيقونات إضافية ----------------
def _p(w=380, h=300):
    im = icon_canvas(w, h)
    return im, ImageDraw.Draw(im), w * S, h * S


def drop_icon(w=380, h=300, col="#7FB7C9"):
    im, d, W_, H_ = _p(w, h)
    cx, cy = W_ / 2, H_ * 0.58
    r = H_ * 0.26
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgb(col))
    d.polygon([(cx, cy - r * 2.05), (cx - r * 0.93, cy - r * 0.35), (cx + r * 0.93, cy - r * 0.35)], fill=rgb(col))
    d.ellipse([cx - r * 0.55, cy - r * 0.2, cx - r * 0.2, cy + r * 0.3], fill=rgb("#FFFFFF", 90))
    return finish(im)


def tape_icon(w=380, h=300):
    im, d, W_, H_ = _p(w, h)
    d.rounded_rectangle([W_ * 0.06, H_ * 0.38, W_ * 0.94, H_ * 0.62], radius=14 * S, fill=rgb("#F2B36B"))
    for i in range(0, 31):
        x = W_ * 0.09 + i * (W_ * 0.82 / 30)
        ln = H_ * (0.12 if i % 5 == 0 else 0.07)
        d.line([(x, H_ * 0.38), (x, H_ * 0.38 + ln)], fill=rgb("#4A3A22"), width=int(2.5 * S))
    return finish(im)


def hanger_icon(w=380, h=300):
    im, d, W_, H_ = _p(w, h)
    cx = W_ / 2
    d.arc([cx - W_ * 0.05, H_ * 0.12, cx + W_ * 0.05 + W_ * 0.04, H_ * 0.34], 180, 450, fill=rgb("#CFC6B3"), width=int(8 * S))
    d.line([(cx + W_ * 0.04, H_ * 0.33), (cx + W_ * 0.04, H_ * 0.42)], fill=rgb("#CFC6B3"), width=int(8 * S))
    d.line([(cx + W_ * 0.04, H_ * 0.42), (cx - W_ * 0.36, H_ * 0.8)], fill=rgb("#CFC6B3"), width=int(9 * S))
    d.line([(cx + W_ * 0.04, H_ * 0.42), (cx + W_ * 0.44, H_ * 0.8)], fill=rgb("#CFC6B3"), width=int(9 * S))
    d.line([(cx - W_ * 0.36, H_ * 0.8), (cx + W_ * 0.44, H_ * 0.8)], fill=rgb("#CFC6B3"), width=int(9 * S))
    return finish(im)


def iron_icon(w=380, h=300):
    im, d, W_, H_ = _p(w, h)
    pts = [(W_ * 0.12, H_ * 0.72), (W_ * 0.88, H_ * 0.72), (W_ * 0.80, H_ * 0.52), (W_ * 0.55, H_ * 0.40), (W_ * 0.22, H_ * 0.46)]
    d.polygon(pts, fill=rgb("#CFC6B3"))
    d.rounded_rectangle([W_ * 0.12, H_ * 0.72, W_ * 0.88, H_ * 0.80], radius=8 * S, fill=rgb("#8DB59C"))
    d.arc([W_ * 0.25, H_ * 0.14, W_ * 0.62, H_ * 0.52], 200, 340, fill=rgb("#E6784F"), width=int(14 * S))
    for i in range(3):
        x = W_ * (0.30 + i * 0.18)
        d.line([(x, H_ * 0.84), (x + W_ * 0.04, H_ * 0.94)], fill=rgb("#A9B3A9"), width=int(4 * S))
    return finish(im)


def tag_icon(w=380, h=300):
    im, d, W_, H_ = _p(w, h)
    d.polygon([(W_ * 0.28, H_ * 0.18), (W_ * 0.72, H_ * 0.18), (W_ * 0.78, H_ * 0.30), (W_ * 0.78, H_ * 0.86), (W_ * 0.22, H_ * 0.86), (W_ * 0.22, H_ * 0.30)], fill=rgb("#E8E1D2"))
    d.ellipse([W_ * 0.46, H_ * 0.23, W_ * 0.54, H_ * 0.31], fill=rgb("#18251E"))
    for i, ln in enumerate((0.34, 0.26, 0.30, 0.22)):
        y = H_ * (0.42 + i * 0.1)
        d.line([(W_ * 0.30, y), (W_ * (0.30 + ln), y)], fill=rgb("#8A826F"), width=int(6 * S))
    return finish(im)


def thermo_icon(w=380, h=300, level=0.5, col="#E6784F"):
    im, d, W_, H_ = _p(w, h)
    cx = W_ / 2
    d.rounded_rectangle([cx - W_ * 0.05, H_ * 0.08, cx + W_ * 0.05, H_ * 0.72], radius=int(W_ * 0.05), fill=rgb("#E8E1D2"))
    d.ellipse([cx - W_ * 0.11, H_ * 0.62, cx + W_ * 0.11, H_ * 0.62 + W_ * 0.22], fill=rgb("#E8E1D2"))
    top = H_ * (0.70 - 0.55 * level)
    d.rounded_rectangle([cx - W_ * 0.025, top, cx + W_ * 0.025, H_ * 0.72], radius=int(W_ * 0.025), fill=rgb(col))
    d.ellipse([cx - W_ * 0.08, H_ * 0.65, cx + W_ * 0.08, H_ * 0.65 + W_ * 0.16], fill=rgb(col))
    for i in range(5):
        y = H_ * (0.14 + i * 0.1)
        d.line([(cx + W_ * 0.08, y), (cx + W_ * 0.14, y)], fill=rgb("#A9B3A9"), width=int(3 * S))
    return finish(im)


def fold_icon(w=380, h=300):
    im, d, W_, H_ = _p(w, h)
    cols = ["#E8E1D2", "#CFC6B3", "#8DB59C"]
    for i, c in enumerate(cols):
        y = H_ * (0.58 - i * 0.2)
        d.rounded_rectangle([W_ * 0.2, y, W_ * 0.8, y + H_ * 0.17], radius=12 * S, fill=rgb(c))
        d.line([(W_ * 0.2 + 18 * S, y + H_ * 0.085), (W_ * 0.8 - 18 * S, y + H_ * 0.085)], fill=rgb("#18251E", 60), width=int(2 * S))
    return finish(im)


def cotton_icon(w=380, h=300):
    im, d, W_, H_ = _p(w, h)
    cx, cy = W_ / 2, H_ * 0.42
    for dx, dy in ((-0.1, 0.04), (0.1, 0.04), (0, -0.08), (-0.05, 0.1), (0.05, 0.1), (0, 0.02)):
        r = W_ * 0.11
        d.ellipse([cx + dx * W_ - r, cy + dy * H_ - r, cx + dx * W_ + r, cy + dy * H_ + r], fill=rgb("#F3ECDD"))
    d.polygon([(cx - W_ * 0.16, cy + H_ * 0.12), (cx + W_ * 0.16, cy + H_ * 0.12), (cx + W_ * 0.1, cy + H_ * 0.34), (cx - W_ * 0.1, cy + H_ * 0.34)], fill=rgb("#5E8A6E"))
    d.line([(cx, cy + H_ * 0.34), (cx, H_ * 0.92)], fill=rgb("#5E8A6E"), width=int(8 * S))
    return finish(im)


def stack_icon(w=380, h=300):
    return fold_icon(w, h)


def clock_icon(w=380, h=300):
    im, d, W_, H_ = _p(w, h)
    cx, cy, r = W_ / 2, H_ / 2, H_ * 0.36
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgb("#E8E1D2"))
    d.line([(cx, cy), (cx, cy - r * 0.65)], fill=rgb("#18251E"), width=int(8 * S))
    d.line([(cx, cy), (cx + r * 0.45, cy + r * 0.2)], fill=rgb("#E6784F"), width=int(8 * S))
    return finish(im)


def sunglow_icon(w=380, h=300):
    return sun_icon(w, h)


def icon(name, w=380, h=300):
    """سجل الأيقونات بالاسم: بيرجّع صورة RGBA بمقاس تقريبي w×h."""
    R = {
        "tee": lambda: tee_icon(min(w, 360), min(h, 300)),
        "sun": lambda: sun_icon(w, h),
        "weave_open": lambda: weave_icon(w, h, 9),
        "weave_dense": lambda: weave_icon(w, h, 26),
        "collar_bad": lambda: collar_icon(w, h, True),
        "collar_good": lambda: collar_icon(w, h, False),
        "seam_bad": lambda: seam_icon(w, h, False),
        "seam_good": lambda: seam_icon(w, h, True),
        "hem_bad": lambda: hem_icon(w, h, False),
        "hem_good": lambda: hem_icon(w, h, True),
        "surf_bad": lambda: surface_icon(w, h, False),
        "surf_good": lambda: surface_icon(w, h, True),
        "drop": lambda: drop_icon(w, h),
        "tape": lambda: tape_icon(w, h),
        "hanger": lambda: hanger_icon(w, h),
        "iron": lambda: iron_icon(w, h),
        "tag": lambda: tag_icon(w, h),
        "thermo_low": lambda: thermo_icon(w, h, 0.35, "#7FB7C9"),
        "thermo_high": lambda: thermo_icon(w, h, 0.9, "#E6784F"),
        "fold": lambda: fold_icon(w, h),
        "cotton": lambda: cotton_icon(w, h),
        "clock": lambda: clock_icon(w, h),
    }
    return R[name]()
