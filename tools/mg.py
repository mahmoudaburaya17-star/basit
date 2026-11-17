# -*- coding: utf-8 -*-
"""موشن جرافيك كوميدي بالكود: شخصية "بسيط" (تيشيرت بوش) + غسالة + فقاعات كلام + مؤثرات صوتية متصنّعة.
كل حاجة بتتعمل بـ Pillow/numpy. python3 tools/mg.py washer out.mp4"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v2  # noqa
from v2 import C, rgb, Canvas, prog, ease
from generate_images import font, LANG
import make_music as mm

W, H, FPS = 1080, 1920, 30
SS = 2
Y0, Y1 = 330, 1780            # منطقة المشهد
SW, SH = W * SS, (Y1 - Y0) * SS
INK = "#1B2A22"
CREAM = "#F3ECDD"
SHADE = "#D9CDB3"


def lerp(a, b, t):
    return a + (b - a) * t


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def seg(t, a, b):
    return clamp((t - a) / (b - a))


def eio(p):
    p = clamp(p)
    return p * p * (3 - 2 * p)


def back(p, k=1.7):
    p = clamp(p)
    return 1 + (k + 1) * (p - 1) ** 3 + k * (p - 1) ** 2


def _c(x):
    return x if isinstance(x, tuple) else rgb(x)


class Stage:
    def __init__(self):
        self.im = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def P(self, x, y):
        return (x * SS, (y - Y0) * SS)

    def poly(self, pts, fill, outline=None, width=0):
        q = [self.P(*p) for p in pts]
        self.d.polygon(q, fill=_c(fill) if fill is not None else None)
        if outline:
            self.d.line(q + [q[0]], fill=_c(outline), width=int(width * SS), joint="curve")

    def circ(self, cx, cy, r, fill=None, outline=None, width=0):
        x, y = self.P(cx, cy)
        self.d.ellipse([x - r * SS, y - r * SS, x + r * SS, y + r * SS],
                       fill=_c(fill) if fill is not None else None,
                       outline=_c(outline) if outline else None, width=int(width * SS))

    def ell(self, cx, cy, rx, ry, fill=None, outline=None, width=0):
        x, y = self.P(cx, cy)
        self.d.ellipse([x - rx * SS, y - ry * SS, x + rx * SS, y + ry * SS],
                       fill=_c(fill) if fill is not None else None,
                       outline=_c(outline) if outline else None, width=int(width * SS))

    def rr(self, x0, y0, x1, y1, r, fill=None, outline=None, width=0):
        a, b = self.P(x0, y0), self.P(x1, y1)
        self.d.rounded_rectangle([a[0], a[1], b[0], b[1]], r * SS,
                                 fill=_c(fill) if fill is not None else None,
                                 outline=_c(outline) if outline else None, width=int(width * SS))

    def arc(self, cx, cy, rx, ry, a0, a1, color, width):
        x, y = self.P(cx, cy)
        self.d.arc([x - rx * SS, y - ry * SS, x + rx * SS, y + ry * SS], a0, a1, fill=_c(color), width=int(width * SS))

    def line(self, pts, color, width):
        self.d.line([self.P(*p) for p in pts], fill=_c(color), width=int(width * SS), joint="curve")

    def text(self, s, x, y, size, color, bold=True, anchor="mm"):
        self.d.text(self.P(x, y), s, font=font(int(size * SS), bold), fill=_c(color), anchor=anchor, **LANG)

    def result(self, extra=None):
        return self.im.resize((W, Y1 - Y0), Image.LANCZOS)


# ---------------------------- الشخصية ----------------------------
BODY = [(-110, -165), (-55, -170), (-36, -138), (0, -126), (36, -138), (55, -170), (110, -165), (215, -92),
        (172, -28), (120, -66), (120, 168), (-120, 168), (-120, -66), (-172, -28), (-215, -92)]


def xf(pts, cx, cy, s=1.0, sx=1.0, sy=1.0, rot=0.0):
    out = []
    c, sn = math.cos(rot), math.sin(rot)
    for x, y in pts:
        y2 = (y - 168) * sy + 168      # الاسكواش حوالين القاعدة
        x2 = x * sx
        out.append((cx + s * (x2 * c - (y2 - 168) * sn), cy + s * (x2 * sn + (y2 - 168) * c)))
    return out


def mascot(st, cx, cy, s=0.75, sx=1.0, sy=1.0, rot=0.0, face="happy", blink=False, sweat=0.0, wave=0.0, tint=None, wrinkle=0.0):
    """cx, cy = منتصف القاعدة. s = المقياس الكلي."""
    body = xf(BODY, cx, cy, s, sx, sy, rot)
    fill = CREAM if not tint else tint
    # ضل
    st.ell(cx, cy + 6 * s, 135 * s * sx, 16 * s, fill=(0, 0, 0, 70))
    st.poly(body, fill, SHADE, 7 * s)

    def T(x, y):
        return xf([(x, y)], cx, cy, s, sx, sy, rot)[0]
    # ياقة
    pts = [T(-55, -170), T(-36, -138), T(0, -126), T(36, -138), T(55, -170)]
    st.line(pts, "#CDBF9C", 12 * s)
    if wrinkle > 0:
        import random as _r
        rr_ = _r.Random(11)
        for _ in range(9):
            x = rr_.uniform(-95, 95); y = rr_.uniform(-90, 130)
            ln = [T(x + dx, y + dy) for dx, dy in ((0, 0), (14, -10), (28, 2), (42, -8))]
            st.line(ln, (150, 135, 105, int(190 * wrinkle)), 5 * s)
    if face is None:
        return body
    # وش
    ex, ey = 46, -28
    for k in (-1, 1):
        x, y = T(k * ex, ey)
        r = (15 if face != "shock" else 22) * s * (0.9 if blink else 1)
        if face in ("pain",):
            st.line([T(k * ex - k * 18, ey - 12), T(k * ex + k * 14, ey), T(k * ex - k * 18, ey + 12)], INK, 7 * s)
        elif blink:
            st.line([T(k * ex - 14, ey), T(k * ex + 14, ey)], INK, 6 * s)
        else:
            st.circ(x, y, r, fill=INK)
            st.circ(x + 5 * s, y - 6 * s, r * 0.32, fill="#FFFFFF")
    mx, my = T(0, 28)
    if face == "happy":
        st.arc(mx, my - 14 * s, 34 * s, 28 * s, 20, 160, INK, 7 * s)
    elif face == "shock":
        st.ell(mx, my + 6 * s, 20 * s, 28 * s, fill=INK)
    elif face == "pain":
        st.arc(mx, my + 30 * s, 32 * s, 26 * s, 200, 340, INK, 7 * s)
    elif face == "proud":
        st.arc(mx, my - 14 * s, 38 * s, 30 * s, 15, 165, INK, 7 * s)
        for k in (-1, 1):
            bx, by = T(k * 78, 8)
            st.circ(bx, by, 14 * s, fill=(230, 120, 79, 110))
    if sweat > 0:
        for i, k in enumerate((-1, 1)):
            x, y = T(k * 96, -88)
            dy = (sweat * 40 + i * 25) % 60
            st.poly([(x, y + dy - 20 * s), (x - 9 * s, y + dy), (x + 9 * s, y + dy)], "#7FC8F8")
            st.circ(x, y + dy + 2 * s, 9 * s, fill="#7FC8F8")
    return body


# ---------------------------- الغسالة ----------------------------
MX, MY = 740, 1300     # مركز الباب
def washer(st, shake=(0, 0), heat=0.0, disp="30", disp_col="#6FD39B", door=0.0, spin=0.0, inside=None, glow=0.0):
    ox, oy = shake
    x0, x1, y0, y1 = 480 + ox, 1000 + ox, 970 + oy, 1650 + oy
    st.rr(x0, y0, x1, y1, 46, fill="#E8E2D2", outline="#BDB39A", width=7)
    st.rr(x0 + 20, y0 + 20, x1 - 20, y0 + 150, 26, fill="#2A3A32")
    st.text(disp, x1 - 120, y0 + 85, 80, disp_col, True)
    st.circ(x0 + 88, y0 + 85, 40, fill="#CFC6AF", outline="#9E957E", width=5)
    st.line([(x0 + 88, y0 + 85), (x0 + 88 + 26 * math.cos(spin * 0.2 + 1), y0 + 85 + 26 * math.sin(spin * 0.2 + 1))], INK, 8)
    cx, cy = MX + ox, MY + oy
    st.circ(cx, cy, 214, fill="#C8BFA6", outline="#9E957E", width=8)
    st.circ(cx, cy, 182, fill="#16231D")
    if door < 0.5:
        # جوه الدرام
        if inside:
            inside(st, cx, cy)
        # زجاج
        gl = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
        gd = ImageDraw.Draw(gl)
        a, b = st.P(cx - 182, cy - 182), st.P(cx + 182, cy + 182)
        gd.ellipse([a[0], a[1], b[0], b[1]], fill=(140, 190, 230, 60))
        gd.arc([a[0] + 30 * SS, a[1] + 30 * SS, b[0] - 30 * SS, b[1] - 30 * SS], 200, 250, fill=(255, 255, 255, 130), width=10 * SS)
        st.im.alpha_composite(gl)
    else:
        w = (1 - (door - 0.5) * 2)       # الباب بيتفتح (ضغط أفقي)
        st.ell(cx - 150 * (1 - w) , cy, 182 * max(0.12, w), 182, fill="#C8BFA6", outline="#9E957E", width=6)
    st.rr(x0 + 40, y1 - 40, x1 - 40, y1 + 20, 10, fill="#9E957E")


def steam(st, t, amount, ox=0):
    if amount <= 0:
        return
    for i in range(9):
        ph = (t * 0.6 + i * 0.13) % 1.0
        x = 560 + i * 60 + math.sin(t * 3 + i) * 18 + ox
        y = 990 - ph * 330
        r = 16 + ph * 34
        a = int(150 * amount * (1 - ph) * math.sin(ph * math.pi))
        st.circ(x, y, r, fill=(255, 255, 255, a))


# ---------------------------- فقاعة الكلام ----------------------------
def bubble(st, text, cx, cy, p, tail=(0, 80), size=50, w=None):
    if p <= 0:
        return
    s = back(p)
    from generate_images import tw
    wd = (w or (tw(text, font(size, True)) + 90)) * s
    cx0 = cx
    cx = min(max(cx, wd / 2 + 24), W - wd / 2 - 24)
    tail = (tail[0] + (cx0 - cx), tail[1])
    h = (size * 1.9) * s
    x0, x1, y0, y1 = cx - wd / 2, cx + wd / 2, cy - h / 2, cy + h / 2
    st.rr(x0, y0, x1, y1, 38 * s, fill="#F6F0E2", outline="#D9CDB3", width=5)
    tx, ty = cx + tail[0], cy + tail[1]
    st.poly([(cx - 26 * s + tail[0] * 0.2, y1 - 6), (cx + 26 * s + tail[0] * 0.2, y1 - 6), (tx, ty)], "#F6F0E2")
    st.text(text, cx, cy - 4, size * s, INK, True)


# ---------------------------- المؤثرات الصوتية ----------------------------
SR = mm.SR


def _t(d):
    return np.arange(int(SR * d)) / SR


def sfx_pop(f0=700):
    t = _t(0.18)
    f = f0 * np.exp(-t * 14)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 22) * 0.9


def sfx_whoosh(d=0.5, up=False):
    n = np.random.default_rng(3).standard_normal(int(SR * d))
    t = _t(d)
    env = np.sin(np.pi * t / d) ** 2
    from scipy.signal import lfilter
    a = np.exp(-2 * np.pi * (900 + 1800 * (t / d if up else 1 - t / d)) / SR)
    y = lfilter([1 - a[0]], [1, -a[0]], n)  # ناعم تقريبًا
    return y * env * 0.9


def sfx_slide(d=0.9, f0=1500, f1=260):
    t = _t(d)
    f = f0 * (f1 / f0) ** (t / d)
    vib = 1 + 0.015 * np.sin(2 * np.pi * 18 * t)
    return np.sin(2 * np.pi * np.cumsum(f * vib) / SR) * np.exp(-t * 2.0) * 0.5


def sfx_boing(d=0.6):
    t = _t(d)
    f = 220 + 160 * np.exp(-t * 6) * np.cos(2 * np.pi * 9 * t)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6) * 0.7


def sfx_ding(f=1318):
    t = _t(1.2)
    return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.01 * t)) * np.exp(-t * 3.2) * 0.45


def sfx_thud():
    t = _t(0.25)
    return np.sin(2 * np.pi * 70 * t * np.exp(-t * 4)) * np.exp(-t * 16) * 0.9


def sfx_hum(d, level_fn):
    t = _t(d)
    rng = np.random.default_rng(5)
    lvl = np.array([level_fn(x) for x in t[::441]])
    lvl = np.interp(t, t[::441], lvl)
    return (np.sin(2 * np.pi * 85 * t) * 0.5 + np.sin(2 * np.pi * 170 * t + 1) * 0.25 + rng.standard_normal(len(t)) * 0.05) * lvl


def mix_sfx(total, events, hum=None):
    buf = np.zeros(int(SR * total) + SR)
    for t0, y, g in events:
        i = int(t0 * SR)
        m = min(len(y), len(buf) - i)
        if m > 0:
            buf[i:i + m] += y[:m] * g
    if hum is not None:
        t0, d, fn, g = hum
        y = sfx_hum(d, fn)
        i = int(t0 * SR)
        m = min(len(y), len(buf) - i)
        buf[i:i + m] += y[:m] * g
    return buf[:int(SR * total)]


# ---------------------------- مشهد الغسالة (كوميدي) ----------------------------
TOTAL = 20.0
FLOOR = 1650


def title(c, t):
    # سلسلة + عنوان كينيتك
    v2.pill(c, "مشهد كوميدي", 1080, 190, prog(t, 0.0)) if hasattr(v2, "pill") else None


def washer_scene(t):
    st = Stage()
    out = {"bubbles": []}
    # حالة الحرارة
    temp = 30
    if 4.6 <= t < 10.2:
        temp = int(lerp(30, 90, eio(seg(t, 4.8, 8.8))))
    elif 10.2 <= t < 14.2:
        temp = 90
    heat = 0.0
    if 4.6 <= t < 10.4:
        heat = eio(seg(t, 4.8, 8.6))
    elif 10.4 <= t < 12.4:
        heat = 1 - seg(t, 10.4, 12.4)
    tcol = "#6FD39B" if temp <= 35 else ("#F2B36B" if temp < 70 else "#FF6A4D")
    # اهتزاز
    sh = (0, 0)
    if 5.0 <= t < 10.2:
        a = 2 + 9 * eio(seg(t, 5.0, 9.0))
        sh = (math.sin(t * 50) * a, math.cos(t * 41) * a * 0.6)
    door = 0.0
    if t >= 10.9:
        door = eio(seg(t, 10.9, 11.5))
    if t >= 15.4 and t < 15.4:
        door = 0
    spin = t * 40 if 4.6 <= t < 10.2 else 0

    def inside(s_, cx, cy):
        if 4.3 <= t < 10.4:
            sc = 0.30
            rot = t * 9
            body = xf(BODY, cx, cy + 40, sc, 1, 1, rot)
            s_.poly(body, CREAM, SHADE, 2)
            if t > 7.5:
                pass
    washer(st, sh, heat, str(temp), tcol, door, spin, inside)
    # بخار
    if 5.5 <= t < 11.2:
        steam(st, t, min(1, seg(t, 5.5, 7.5)) * (1 if t < 10.4 else 1 - seg(t, 10.4, 11.2)), sh[0])
    if 10.4 <= t < 12.0:
        steam(st, t, 1.0 - seg(t, 10.4, 12.0) * 0.4, 0)

    # ----- الشخصية -----
    FX, FY = 262, FLOOR
    if t < 3.3:
        # دخول من فوق + ارتداد
        p = seg(t, 0.35, 1.05)
        y = lerp(FY - 900, FY, ease(p) if p < 1 else 1)
        if p >= 1:
            k = seg(t, 1.05, 1.5)
            sq = 1 - 0.22 * math.sin(k * math.pi) * (1 - k)
        else:
            k = 0
            sq = 1
        if p > 0:
            mascot(st, FX, y, 0.9, sx=1 / sq if p >= 1 else 0.9, sy=sq if p >= 1 else 1.12,
                   face="proud" if t > 1.4 else "happy", blink=(2.6 < t < 2.7))
        if t > 1.5:
            out["bubbles"].append(("أنا XL ومبسوط بنفسي!", 250, FY - 560, seg(t, 1.5, 1.9), (30, 150)))
    elif t < 4.35:
        # قفزة جوه الغسالة
        p = seg(t, 3.4, 4.3)
        x = lerp(FX, MX, eio(p))
        y = FY - 380 * math.sin(p * math.pi) - lerp(0, (FY - MY) * 0.0, p) + lerp(0, -(FY - MY - 150) * eio(p), 1)
        s = 0.9 * lerp(1, 0.38, eio(p))
        rot = p * 6.28 * 1
        mascot(st, x, y, s, rot=rot, face="shock" if p > 0.5 else "happy")
    elif t < 10.9:
        if 4.3 <= t < 4.7:
            pass
        if 8.0 < t:
            out["bubbles"].append(("آه يا حر! أنا بسخن!", 300, 990, seg(t, 8.0, 8.4), (50, 90)))
    elif t < 15.4:
        # التيشيرت الصغير بيتدحرج ويقع
        p = seg(t, 11.0, 12.1)
        x = lerp(MX - 90, 270, ease(p))
        y = lerp(MY + 120, FLOOR, ease(p) ** 2) - 220 * math.sin(p * math.pi) * (1 - p * 0.3)
        k = seg(t, 12.1, 12.5)
        sq = 1 - 0.25 * math.sin(k * math.pi)
        sc = 0.55
        if t < 13.9:
            mascot(st, x, y, sc, sx=1 / sq if k > 0 else 1, sy=sq if k > 0 else 1, rot=(1 - p) * 8 if p < 1 else 0,
                   face="shock" if t < 13.0 else "pain", sweat=t * 2 if t > 12.2 else 0)
            if t > 12.3:
                out["bubbles"].append(("إيه ده؟! كنت XL وبقيت S!", 330, FLOOR - 420, seg(t, 12.3, 12.7), (-20, 150)))
        else:
            # بيطلع بـ "بوف" ويظهر الأصلي
            p2 = seg(t, 13.9, 14.3)
            mascot(st, 270, FLOOR, sc * (1 - p2), face="pain")
        if t >= 14.4:
            p3 = seg(t, 14.4, 14.9)
            mascot(st, 262, FLOOR, 0.9 * back(p3), face="proud")
            if t > 15.0:
                out["bubbles"].append(("على 30 لسه XL وزي الفل!", 270, FLOOR - 560, seg(t, 15.0, 15.4), (30, 150)))
    else:
        mascot(st, 262, FLOOR, 0.9, face="proud", blink=(18.2 < t < 18.3))
    out['heat'] = heat
    return st, out, temp


SCR = ["بتغسل تيشيرتك على 90 درجة؟", "المية السخنة بتصغّر القطن", "30 درجة تكفي وزيادة", "اقرا التيكت (الليبل) اللي جوه التيشيرت"]


def frame(t):
    c = Canvas(W, H)
    c.wordmark(y=150)
    st, out, temp = washer_scene(t)
    if out['heat'] > 0:
        g = Image.new("RGBA", (W // 2, H // 2), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse([120, 320, 620, 820], fill=(230, 80, 40, int(150 * out['heat'])))
        g = g.filter(ImageFilter.GaussianBlur(50)).resize((W, H), Image.BILINEAR)
        c.img.alpha_composite(g)
    for (txt, bx, by, p, tail) in out["bubbles"]:
        bubble(st, txt, bx, by, p, tail, size=46)
    im = st.result()
    c.img.alpha_composite(im, (0, Y0))
    # عناوين
    if t < 4.3:
        c.block(SCR[0], 1000, 250, 98, 920, t=t, t0=0.3, step=0.28, lh=1.25)
        v2_pill(c, "هزار في هزار", prog(t, 0.0))
    elif t < 12.8:
        c.block(SCR[1], 1000, 250, 98, 920, t=t - 4.3, t0=0.0, step=0.28, lh=1.25) if t < 10.9 else None
        v2_pill(c, "هزار في هزار", 1)
        if t >= 10.9:
            c.block("شوف مقاسه بقى إيه...", 1000, 250, 98, 920, t=t - 10.9, t0=0.0, step=0.28, lh=1.25)
    elif t < 16.2:
        c.block(SCR[2], 1000, 250, 98, 920, t=t - 14.0, t0=0.0, step=0.28, lh=1.25) if t >= 14.0 else \
            c.block("شوف مقاسه بقى إيه...", 1000, 250, 98, 920)
        v2_pill(c, "هزار في هزار", 1)
    else:
        # CTA
        ov = Image.new("RGBA", (W, H), (12, 18, 15, int(200 * prog(t, 16.2, 0.5))))
        c.img.alpha_composite(ov)
        y = c.block(SCR[3], 1000, 640, 104, 920, t=t - 16.4, t0=0.0, step=0.3, lh=1.3)
        c.rrect([480, 1100, 1000, 1260], C["card"], 40, alpha=prog(t, 18.0), outline=C["line"])
        c.text("تابعنا على بسيط", 960, 1135, 76, C["cream"], True, alpha=prog(t, 18.0))
    dr = ImageDraw.Draw(c.img)
    dr.rectangle([0, 0, int(W * t / TOTAL), 10], fill=rgb(C["acc"]))
    return c.img.convert("RGB")


def v2_pill(c, txt, p):
    from v2engine import pill
    pill(c, txt, W, 195, p)


WASH_EVENTS = [(0.35, sfx_whoosh(0.5), 0.35), (1.0, sfx_thud(), 0.5), (1.05, sfx_boing(), 0.25),
          (1.5, sfx_pop(900), 0.3), (3.4, sfx_whoosh(0.7), 0.4), (4.25, sfx_pop(500), 0.5),
          (4.7, sfx_pop(800), 0.2), (8.0, sfx_pop(1000), 0.3), (10.3, sfx_ding(), 0.5),
          (10.9, sfx_whoosh(0.4), 0.3), (11.0, sfx_slide(1.0), 0.5), (12.1, sfx_thud(), 0.6),
          (12.3, sfx_pop(600), 0.3), (13.9, sfx_pop(1100), 0.5), (14.4, sfx_boing(), 0.3),
          (14.5, sfx_ding(1568), 0.35), (15.0, sfx_pop(900), 0.3), (16.4, sfx_whoosh(0.4, True), 0.2)]
WASH_HUM = (4.6, 5.8, lambda x: 0.0 + 0.5 * clamp((x - 0.0) / 1.0) * (1 if x < 4.2 else 0.8), 0.45)

def render(out, total=TOTAL):
    return render_generic(out, frame, total, WASH_EVENTS, WASH_HUM, 7)


def render_generic(out, frame_fn, total, ev, hum, seed):
    tmp = out + ".silent.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H), "-r", str(FPS),
           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", tmp]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(int(total * FPS)):
        pr.stdin.write(frame_fn(i / FPS).tobytes())
    pr.stdin.close()
    pr.wait()
    sfx = mix_sfx(total, ev, hum)
    music = mm.make(total, seed=seed)
    mono = music.mean(axis=0) if music.ndim == 2 else music
    mus = np.stack([mono * 0.8, mono * 0.8]) if music.ndim == 2 else music
    s2 = np.stack([sfx, sfx])
    n = min(mus.shape[1], s2.shape[1])
    mixed = mus[:, :n] * 0.9 + s2[:, :n] * 0.55
    mixed = mixed / (np.max(np.abs(mixed)) + 1e-9) * 0.7
    wav = out + ".wav"
    mm.write(wav, mixed)
    subprocess.check_call(["ffmpeg", "-loglevel", "error", "-y", "-i", tmp, "-i", wav, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
                           "-c:a", "aac", "-b:a", "160k", "-af", "volume=0.6", "-shortest", "-movflags", "+faststart", out])
    os.remove(tmp)
    os.remove(wav)


if __name__ == "__main__":
    if sys.argv[1] == "frames":
        ts = [float(x) for x in sys.argv[3:]]
        ims = [frame(t).resize((360, 640)) for t in ts]
        sheet = Image.new("RGB", (360 * len(ims), 640))
        for i, im in enumerate(ims):
            sheet.paste(im, (360 * i, 0))
        sheet.save(sys.argv[2])
    else:
        render(sys.argv[2])
