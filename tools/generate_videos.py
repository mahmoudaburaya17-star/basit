# -*- coding: utf-8 -*-
"""يولّد فيديوهات ريلز عمودية (1080x1920، 30 إطار/ثانية) لصفحة بسيط بالموشن جرافيك.

التشغيل:  python3 tools/generate_videos.py [اسم_فيديو ...]
الفيديوهات صامتة بنص على الشاشة (أغلب المشاهدة على فيسبوك من غير صوت).
المخرجات: videos/<name>.mp4 + videos/<name>-cover.png
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_images as gi  # noqa: E402
from generate_images import font, tw, wrap, BRAND, TAGLINE, BG, INK, SOFT, MUTED, ACCENT, OLIVE, LANG  # noqa: E402

ROOT = gi.ROOT
VW, VH = 1080, 1920
FPS = 30
MARGIN = 90


def ease(p):
    p = max(0.0, min(1.0, p))
    return 1 - (1 - p) ** 3


def prog(t, t0, dur=0.6):
    return ease((t - t0) / dur)


def rgba(hexcol, a=255):
    hexcol = hexcol.lstrip("#")
    return tuple(int(hexcol[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


class Frame:
    def __init__(self):
        self.img = Image.new("RGBA", (VW, VH), rgba(BG))
        d = ImageDraw.Draw(self.img)
        d.rectangle([0, 0, VW, 16], fill=rgba(ACCENT))
        # الفوتر ثابت (داخل منطقة آمنة بعيد عن واجهة الريلز)
        d.line([MARGIN, VH - 330, VW - MARGIN, VH - 330], fill=rgba(SOFT), width=3)
        d.text((VW - MARGIN, VH - 270), BRAND, font=font(64), fill=rgba(INK), anchor="rm", **LANG)
        d.text((MARGIN, VH - 270), TAGLINE, font=font(32, False), fill=rgba(MUTED), anchor="lm", **LANG)

    def layer(self):
        return Image.new("RGBA", (VW, VH), (0, 0, 0, 0))

    def put(self, layer, alpha=1.0):
        if alpha < 1.0:
            a = layer.getchannel("A").point(lambda v: int(v * alpha))
            layer.putalpha(a)
        self.img = Image.alpha_composite(self.img, layer)

    def text(self, s, xr, y, size, color=INK, bold=True, p=1.0, rise=40, anchor="ra"):
        if p <= 0:
            return
        ly = self.layer()
        d = ImageDraw.Draw(ly)
        f = font(size, bold)
        d.text((xr, y + int((1 - p) * rise) - int(size * 0.2)), s, font=f, fill=rgba(color), anchor=anchor, **LANG)
        self.put(ly, p)

    def paragraph(self, s, xr, y, size, maxw, color=INK, bold=True, p=1.0, lh=1.4):
        lines = wrap(s, font(size, bold), maxw)
        for i, ln in enumerate(lines):
            self.text(ln, xr, y + int(i * size * lh), size, color, bold, p)
        return y + int(len(lines) * size * lh)

    def kicker(self, s, p=1.0):
        if p <= 0:
            return
        ly = self.layer()
        d = ImageDraw.Draw(ly)
        kf = font(40)
        kw = tw(s, kf) + 70
        d.rounded_rectangle([VW - MARGIN - kw, 150, VW - MARGIN, 224], radius=37, fill=rgba(INK))
        d.text((VW - MARGIN - 35, 188), s, font=kf, fill=rgba(BG), anchor="rm", **LANG)
        self.put(ly, p)

    def rect(self, box, color, p=1.0, radius=0):
        if p <= 0:
            return
        ly = self.layer()
        d = ImageDraw.Draw(ly)
        if radius:
            d.rounded_rectangle(box, radius=radius, fill=rgba(color))
        else:
            d.rectangle(box, fill=rgba(color))
        self.put(ly, p)

    def badge(self, cx, cy, n, p=1.0, r=48):
        if p <= 0:
            return
        ly = self.layer()
        d = ImageDraw.Draw(ly)
        rr = int(r * (0.6 + 0.4 * p))
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=rgba(ACCENT))
        d.text((cx, cy - 2), str(n), font=font(54), fill=rgba("#FFFFFF"), anchor="mm")
        self.put(ly, p)

    def progress_bar(self, t, total):
        d = ImageDraw.Draw(self.img)
        d.rectangle([0, 16, int(VW * t / total), 26], fill=rgba(OLIVE))


# ------------------------------- الفيديوهات -------------------------------

def outro(f, t, t0):
    p = prog(t, t0)
    f.text("تابع بسيط", VW - MARGIN, 760, 130, INK, True, p)
    f.text("للمعلومات اللي بتفيدك قبل ما تشتري", VW - MARGIN, 930, 54, MUTED, False, prog(t, t0 + 0.3))
    f.text("احفظ الفيديو وابعته لصاحبك", VW - MARGIN, 1030, 54, ACCENT, True, prog(t, t0 + 0.6))


def v_gsm(f, t):
    f.kicker("دليل سريع", prog(t, 0.0))
    if t < 3.5:
        f.text("يعني إيه", VW - MARGIN, 430, 120, INK, True, prog(t, 0.3))
        f.text("GSM", VW - MARGIN, 600, 260, ACCENT, True, prog(t, 0.7))
        f.text("في التيشيرت؟", VW - MARGIN, 930, 120, INK, True, prog(t, 1.1))
    elif t < 8:
        s = t - 3.5
        f.text("وزن القماش", VW - MARGIN, 380, 96, INK, True, prog(s, 0.0))
        f.text("بالجرام", VW - MARGIN, 520, 96, INK, True, prog(s, 0.4))
        f.text("لكل متر مربع", VW - MARGIN, 660, 96, INK, True, prog(s, 0.8))
        p = prog(s, 1.4, 0.9)
        side = int(560 * p)
        cx, cy = VW // 2, 1230
        f.rect([cx - side // 2, cy - side // 2, cx + side // 2, cy + side // 2], SOFT, 1.0, 16)
        if p > 0.95:
            f.text("1 متر × 1 متر", cx, cy - 40, 54, INK, True, prog(s, 2.4), anchor="ma")
            f.text("وزنه = GSM", cx, cy + 40, 54, ACCENT, True, prog(s, 2.8), anchor="ma")
    elif t < 15:
        s = t - 8
        f.text("3 أوزان شائعة", VW - MARGIN, 330, 84, INK, True, prog(s, 0.0))
        rows = [("خفيف وصيفي", "150 – 180", 0.45, SOFT), ("متوسط، للاستخدام اليومي", "180 – 220", 0.72, OLIVE),
                ("تقيل وأوسع في الشكل", "220 وأكتر", 1.0, ACCENT)]
        y = 560
        for i, (lab, num, ratio, col) in enumerate(rows):
            p = prog(s, 0.8 + i * 1.6, 0.9)
            f.text(lab, VW - MARGIN, y, 52, INK, True, prog(s, 0.8 + i * 1.6, 0.5))
            maxw = VW - 2 * MARGIN
            bw = int(maxw * ratio * p)
            f.rect([VW - MARGIN - bw, y + 90, VW - MARGIN, y + 190], col, 1.0, 20)
            f.text(num + " جم", VW - MARGIN - 30, y + 112, 56, "#FFFFFF" if col != SOFT else INK, True, p)
            y += 300
    elif t < 18.5:
        s = t - 15
        f.text("الرقم الأعلى", VW - MARGIN, 640, 110, INK, True, prog(s, 0.0))
        f.text("مش دايمًا الأحسن", VW - MARGIN, 800, 110, ACCENT, True, prog(s, 0.4))
        f.text("بيعتمد على الجو والقصة اللي عايزها", VW - MARGIN, 1000, 52, MUTED, False, prog(s, 1.0))
    else:
        outro(f, t, 18.5)


def v_size(f, t):
    f.kicker("دليل المقاس", prog(t, 0.0))
    cx, top, w, h = VW // 2, 520, 560, 760

    def draw_tee(alpha):
        ly = f.layer()
        d = ImageDraw.Draw(ly)
        gi.tee(d, cx, top, w, h, "#E9E4DA", outline=INK, collar=BG)
        f.put(ly, alpha)

    if t < 3:
        f.text("إزاي تعرف مقاسك", VW - MARGIN, 330, 90, INK, True, prog(t, 0.2))
        f.text("من غير جدول؟", VW - MARGIN, 450, 90, ACCENT, True, prog(t, 0.6))
        draw_tee(prog(t, 1.0))
        return
    draw_tee(1.0)
    f.text("(أرقام مثال للتوضيح)", VW - MARGIN, 1320, 38, MUTED, False, 1.0)
    d = ImageDraw.Draw(f.img)
    s = t - 3
    if t < 7.5:
        f.badge(VW - MARGIN - 40, 1480, 1, prog(s, 0.0))
        f.paragraph("افرد تيشيرت ماشي عليك على سطح مسطح", VW - MARGIN - 120, 1440, 46, 740, INK, True, prog(s, 0.1))
    if 7.5 <= t < 12:
        s2 = t - 7.5
        f.badge(VW - MARGIN - 40, 1480, 2, prog(s2, 0.0))
        f.paragraph("قيس العرض من تحت الإبط للإبط", VW - MARGIN - 120, 1440, 46, 740, INK, True, prog(s2, 0.1))
    if t >= 7.5:
        x0 = cx - int(w * 0.30)
        x1 = x0 + int(2 * w * 0.30 * prog(t, 7.5, 1.2))
        y = top + int(h * 0.5)
        ly = f.layer()
        dd = ImageDraw.Draw(ly)
        dd.line([x0, y, x1, y], fill=rgba(ACCENT), width=10)
        dd.polygon([(x0, y), (x0 + 28, y - 18), (x0 + 28, y + 18)], fill=rgba(ACCENT))
        f.put(ly)
        f.text("52 سم", cx, y - 90, 64, ACCENT, True, prog(t, 8.6), anchor="ma")
    if 12 <= t < 16:
        s3 = t - 12
        f.badge(VW - MARGIN - 40, 1480, 3, prog(s3, 0.0))
        f.paragraph("اضرب العرض × 2 = محيط التيشيرت", VW - MARGIN - 120, 1440, 46, 740, INK, True, prog(s3, 0.1))
        f.text("52 × 2 = 104 سم", cx, top + int(h * 0.5) + 70, 64, INK, True, prog(s3, 0.5), anchor="ma")
    if t >= 16 and t < 20:
        s4 = t - 16
        f.badge(VW - MARGIN - 40, 1480, 4, prog(s4, 0.0))
        f.paragraph("المريح: أكبر من صدرك بـ 6 – 10 سم", VW - MARGIN - 120, 1440, 46, 740, INK, True, prog(s4, 0.1))
        f.text("52 × 2 = 104 سم", cx, top + int(h * 0.5) + 70, 64, INK, True, 1.0, anchor="ma")
    if t >= 20:
        pass


def v_size_wrap(f, t):
    if t < 20:
        v_size(f, t)
    else:
        f.kicker("دليل المقاس", 1.0)
        f.text("احفظ الأرقام دي", VW - MARGIN, 560, 110, INK, True, prog(t, 20.0))
        f.text("هتفيدك مع أي براند", VW - MARGIN, 720, 84, ACCENT, True, prog(t, 20.4))
        outro_t = t - 22.5
        if outro_t > 0:
            f.text("تابع بسيط", VW - MARGIN, 1000, 100, INK, True, prog(t, 22.5))


def v_wash(f, t):
    f.kicker("عناية", prog(t, 0.0))
    if t < 3:
        f.text("الغسيل الصح", VW - MARGIN, 450, 130, INK, True, prog(t, 0.2))
        f.text("في 4 خطوات", VW - MARGIN, 640, 130, ACCENT, True, prog(t, 0.6))
        f.text("بيطوّل عمر التيشيرت", VW - MARGIN, 860, 60, MUTED, False, prog(t, 1.2))
        return
    steps = ["اقلبه من جوه", "مية باردة أو فاترة", "منظف بكمية قليلة", "انشره مفرود في الظل"]
    notes = ["الاحتكاك على الوش الداخلي مش الخارجي", "حوالي 30 درجة", "الزيادة بتسيب رواسب وتبهّت اللون",
             "الشمس المباشرة بتبهّت اللون"]
    s = t - 3
    y = 380
    for i, (st, nt) in enumerate(zip(steps, notes)):
        t0 = i * 2.8
        p = prog(s, t0, 0.7)
        if p > 0:
            f.rect([MARGIN, y, VW - MARGIN, y + 250], "#FFFFFF", p, 28)
            f.badge(VW - MARGIN - 80, y + 125, i + 1, p)
            f.text(st, VW - MARGIN - 170, y + 55, 62, INK, True, p)
            f.text(nt, VW - MARGIN - 170, y + 150, 38, MUTED, False, prog(s, t0 + 0.4))
        y += 300
    if s > 12.0:
        f.rect([0, 26, VW, VH - 340], BG, min(1.0, (s - 12.0) / 0.5))
        f.text("غسيل صح", VW - MARGIN, 640, 120, INK, True, prog(s, 12.6))
        f.text("تيشيرت أطول عمرًا", VW - MARGIN, 800, 100, ACCENT, True, prog(s, 13.0))
        f.text("تابع بسيط", VW - MARGIN, 1060, 90, INK, True, prog(s, 14.0))
        f.text("احفظ الفيديو وابعته لصاحبك", VW - MARGIN, 1200, 48, MUTED, False, prog(s, 14.4))


VIDEOS = {
    "gsm-in-20s": (v_gsm, 21.0),
    "measure-your-size": (v_size_wrap, 26.0),
    "right-wash": (v_wash, 21.0),
}


def render(name):
    fn, dur = VIDEOS[name]
    out = os.path.join(ROOT, "videos", name + ".mp4")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (VW, VH),
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", "-an", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(dur * FPS)
    cover_t = 0.5 if name != "gsm-in-20s" else 1.8
    for i in range(n):
        t = i / FPS
        fr = Frame()
        fn(fr, t)
        fr.progress_bar(t, dur)
        rgb = fr.img.convert("RGB")
        proc.stdin.write(rgb.tobytes())
        if i == int(cover_t * FPS):
            rgb.save(os.path.join(ROOT, "videos", name + "-cover.png"))
    proc.stdin.close()
    proc.wait()
    print("done", out, "%.1fs" % dur)


if __name__ == "__main__":
    names = sys.argv[1:] or list(VIDEOS)
    for nm in names:
        render(nm)
