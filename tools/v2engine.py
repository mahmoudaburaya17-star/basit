# -*- coding: utf-8 -*-
"""محرك محتوى v2: كروت 1080x1350، كاروسيل، وريلز 1080x1920 من مواصفات (specs) بالكود.
الموسيقى بتتركّب في render_reel. كل حاجة مولّدة بالكود من غير صور توليدية."""
import os
import subprocess
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v2  # noqa: E402
import make_music as mm  # noqa: E402
from v2 import C, Canvas, prog, rgb  # noqa: E402

W, H = 1080, 1350
R = W - 80


def pill(c, text, w_=W, y=150, alpha=1.0):
    if alpha <= 0:
        return
    pw = int(v2.tw(text, v2.font(36)) + 64)
    c.rrect([w_ - 80 - pw, y, w_ - 80, y + 64], C["card"], 32, alpha=alpha, outline=C["line"])
    c.text(text, w_ - 80 - 32, y + 8, 36, C["acc2"], True, alpha=alpha)


def panel(c, cx, cy, icon_name, label, good, pw=410, ph=400, alpha=1.0):
    c.rrect([cx - pw // 2, cy - ph // 2, cx + pw // 2, cy + ph // 2], C["card"], 34, alpha=alpha, outline=C["line"])
    ic = v2.icon(icon_name, 330, 250)
    c.paste_icon(ic, cx, cy - 30, alpha)
    c.paste_icon(v2.badge_icon(good), cx + pw // 2 - 55, cy - ph // 2 + 55, alpha)
    c.text(label, cx, cy + ph // 2 - 88, 40, C["sage"] if good else C["acc"], True, alpha=alpha, anchor="ma")


def head(c, counter=None):
    c.wordmark(counter=counter)


# ------------------------------- كروت -------------------------------
def tip_card(spec):
    c = Canvas(W, H)
    head(c)
    pill(c, spec.get("kicker", "نصيحة الصبح"))
    c.block(spec["tip"], R, 330, 84, 920, lh=1.38)
    c.paste_icon(v2.icon(spec.get("icon", "tee"), 420, 330), W // 2, 1050)
    return c.img.convert("RGB")


def poll_card(spec):
    c = Canvas(W, H)
    head(c)
    pill(c, spec.get("kicker", "سؤال النهارده"))
    y = c.block(spec["question"], R, 290, 80, 920, lh=1.35)
    y += 40
    for i, opt in enumerate(spec["options"]):
        c.rrect([80, y, R, y + 120], C["card"], 30, outline=C["line"])
        c.text(opt, R - 120, y + 24, 46, C["cream"], True)
        c.text(str(i + 1), R - 60, y + 16, 60, C["acc"], True, anchor="ma")
        y += 148
    c.text("اكتب رقم اختيارك في التعليقات", W // 2, min(y + 30, 1250), 38, C["mute"], False, anchor="ma")
    return c.img.convert("RGB")


def myth_card(spec):
    c = Canvas(W, H)
    head(c)
    pill(c, "صح ولا غلط؟")
    c.text("؟", 150, 160, 340, C["line"], True)
    c.block(spec["statement"], R, 360, 88, 900, lh=1.4)
    c.rrect([80, 1090, R, 1210], C["card"], 30, outline=C["line"])
    c.text("جاوب في التعليقات والإجابة في أول تعليق", W // 2, 1118, 40, C["acc2"], True, anchor="ma")
    return c.img.convert("RGB")


def stat_card(spec):
    c = Canvas(W, H)
    head(c)
    pill(c, spec.get("kicker", "الأرقام بتحكي"))
    c.text(spec["big"], R, 300, spec.get("size", 250), C["acc"], True)
    y = c.block(spec["caption"], R, 640, 74, 920, lh=1.35)
    c.block(spec.get("sub", ""), R, y + 30, 42, 920, C["mute"], False, lh=1.5)
    return c.img.convert("RGB")


# ------------------------------- كاروسيل -------------------------------
def carousel(spec):
    """spec: kicker, title, icon, slides=[...], returns list of PIL images. أنواع الشرايح: point / vs / list."""
    slides = spec["slides"]
    N = len(slides) + 2
    out = []
    c = Canvas(W, H)
    head(c, "1 / %d" % N)
    pill(c, spec.get("kicker", "قبل ما تشتري"))
    c.block(spec["title"], R, 290, 100, 920, lh=1.3)
    ic = v2.icon(spec.get("icon", "tee"), 520, 420)
    ic = ic.resize((int(ic.width * 1.2), int(ic.height * 1.2)), Image.LANCZOS)
    c.paste_icon(ic, W // 2, 1000)
    c.text("اسحب وشوف", W // 2, 1250, 38, C["mute"], False, anchor="ma")
    out.append(c.img.convert("RGB"))
    for i, s in enumerate(slides):
        c = Canvas(W, H)
        head(c, "%d / %d" % (i + 2, N))
        t = s["type"]
        if t == "list":
            c.text(s["title"], R, 190, 84, C["cream"], True)
            y = 360
            for j, it in enumerate(s["items"]):
                c.rrect([80, y, R, y + 150], C["card"], 30, outline=C["line"])
                c.text(str(j + 1), R - 60, y + 28, 70, C["acc"], True, anchor="ma")
                c.block(it, R - 140, y + 28, 40, 700, C["cream"], True, lh=1.25)
                y += 180
        else:
            c.text(str(s.get("n", i + 1)), R, 100, 220, C["acc"], True)
            c.text(s["title"], R, 410, 78, C["cream"], True)
            c.block(s["body"], R, 540, 46, 920, C["mute"], False, lh=1.5)
            if t == "vs":
                (bn, bl), (gn, gl) = s["bad"], s["good"]
                panel(c, R - 190 - 440, 990, bn, bl, False)
                panel(c, R - 190, 990, gn, gl, True)
            else:
                c.rrect([80, 770, R, 1260], C["card"], 36, outline=C["line"])
                ic = v2.icon(s.get("icon", "tee"), 460, 340)
                ic = ic.resize((int(ic.width * 1.3), int(ic.height * 1.3)), Image.LANCZOS)
                c.paste_icon(ic, W // 2, 1015)
        out.append(c.img.convert("RGB"))
    c = Canvas(W, H)
    head(c, "%d / %d" % (N, N))
    c.block("احفظ البوست وابعته لصاحبك اللي بيشتري تيشيرتات", R, 330, 90, 920, lh=1.35)
    c.rrect([80, 880, R, 1130], C["card"], 34, outline=C["line"])
    c.text("تابع بسيط", R - 50, 920, 70, C["cream"], True)
    c.text("نظرة هادية على التيشيرت السادة، من غير بيع ولا ضجة.", R - 50, 1025, 36, C["mute"], False)
    out.append(c.img.convert("RGB"))
    return out


# ------------------------------- ريلز -------------------------------
RW, RH, FPS = 1080, 1920, 30
DURS = {"hook": 3.8, "step": 5.6, "vs": 7.0, "stat": 5.4, "cta": 4.8}
_glow_cache = {}


def _glow():
    if "g" not in _glow_cache:
        from PIL import ImageFilter
        ly = Image.new("RGBA", (RW, RH), (0, 0, 0, 0))
        ImageDraw.Draw(ly).ellipse([240, 800, 840, 1400], fill=rgb("#F2B36B", 120))
        _glow_cache["g"] = ly.filter(ImageFilter.GaussianBlur(130))
    return _glow_cache["g"]


def reel_duration(spec):
    return sum(DURS[s["type"]] + s.get("extra", 0) for s in spec["scenes"])


_ic_cache = {}


def _ic(name, w, h):
    k = (name, w, h)
    if k not in _ic_cache:
        _ic_cache[k] = v2.icon(name, w, h)
    return _ic_cache[k]


def reel_frame(spec, t, total):
    c = Canvas(RW, RH)
    c.wordmark(y=150)
    series = spec.get("series", "")
    acc = 0.0
    for sc in spec["scenes"]:
        d = DURS[sc["type"]] + sc.get("extra", 0)
        if t < acc + d or sc is spec["scenes"][-1]:
            s = t - acc
            draw_scene(c, sc, s, series)
            break
        acc += d
    dr = ImageDraw.Draw(c.img)
    dr.rectangle([0, 0, int(RW * t / total), 10], fill=rgb(C["acc"]))
    return c.img.convert("RGB")


def draw_scene(c, sc, s, series):
    t = sc["type"]
    if t == "hook":
        pill(c, series or "بسيط", RW, 200, prog(s, 0.0))
        y = c.block(sc["main"], R, 480, 112, 920, t=s, t0=0.4, step=0.26, lh=1.3)
        if sc.get("sub"):
            c.block(sc["sub"], R, y + 30, 64, 920, C["acc2"], t=s, t0=1.4 + 0.1 * len(sc["main"].split()), step=0.2, lh=1.3)
        if sc.get("icon"):
            c.paste_icon(_ic(sc["icon"], 520, 420), RW // 2, 1400, prog(s, 1.8, 0.9))
    elif t == "step":
        pill(c, sc.get("label", "الخطوة %s" % sc.get("n", "")), RW, 200, prog(s, 0.0))
        if sc.get("n"):
            c.text(str(sc["n"]), R, 330, 300, C["acc"], True, alpha=prog(s, 0.0))
        y = c.block(sc["title"], R, 700, 96, 920, t=s, t0=0.4, step=0.28, lh=1.3)
        if sc.get("sub"):
            c.block(sc["sub"], R, y + 20, 50, 920, C["mute"], False, t=s, t0=1.6, step=0.18)
        if sc.get("icon"):
            if sc["icon"] == "sun":
                c.put(_glow().copy(), prog(s, 1.2, 1.0))
            c.paste_icon(_ic(sc["icon"], 520, 400), RW // 2, 1440, prog(s, 2.0, 0.8))
    elif t == "vs":
        pill(c, sc.get("label", "قارن"), RW, 200, prog(s, 0.0))
        y = c.block(sc["title"], R, 420, 92, 920, t=s, t0=0.3, step=0.28, lh=1.3)
        if sc.get("sub"):
            c.block(sc["sub"], R, y + 20, 46, 920, C["mute"], False, t=s, t0=1.5, step=0.16)
        for k, (key, good) in enumerate((("good", True), ("bad", False))):
            icn, lab = sc[key]
            cx = R - 215 - k * 450
            p = prog(s, 2.8 + k * 1.3, 0.7)
            if p > 0:
                c.rrect([cx - 215, 1040, cx + 215, 1520], C["card"], 36, alpha=p, outline=C["line"])
                c.paste_icon(_ic(icn, 330, 250), cx, 1240, p)
                c.paste_icon(v2.badge_icon(good, 40), cx + 160, 1080, p)
                c.text(lab, cx, 1440, 42, C["sage"] if good else C["acc"], True, alpha=p, anchor="ma")
    elif t == "stat":
        pill(c, sc.get("label", "الأرقام بتحكي"), RW, 200, prog(s, 0.0))
        big = sc["big"]
        if sc.get("count"):
            a, b = sc["count"]
            v = int(round(a + (b - a) * min(1.0, s / 1.6)))
            big = "%d%s" % (v, sc.get("suffix", ""))
        c.text(big, R, 420, sc.get("size", 260), C["acc"], True, alpha=prog(s, 0.1))
        y = c.block(sc["caption"], R, 800, 76, 920, t=s, t0=1.0, step=0.22, lh=1.35)
        if sc.get("sub"):
            c.block(sc["sub"], R, y + 20, 46, 920, C["mute"], False, t=s, t0=2.4, step=0.16, lh=1.45)
    else:  # cta
        y = c.block(sc.get("main", "جرّب دلوقتي"), R, 600, 124, 920, t=s, t0=0.2, step=0.3, lh=1.25)
        c.block(sc.get("sub", "وقولنا رأيك في التعليقات"), R, y + 30, 60, 920, C["acc2"], t=s, t0=1.0, step=0.2, lh=1.3)
        c.rrect([R - 520, 1100, R, 1260], C["card"], 40, alpha=prog(s, 1.8), outline=C["line"])
        c.text("تابع بسيط", R - 40, 1135, 76, C["cream"], True, alpha=prog(s, 1.8))


def render_reel(spec, out, seed=0, volume=0.7, cover_at=2.6):
    total = reel_duration(spec)
    tmp = out + ".silent.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (RW, RH),
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", "-an", tmp]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(int(total * FPS)):
        im = reel_frame(spec, i / FPS, total)
        if i == int(cover_at * FPS):
            im.save(out.replace(".mp4", "-cover.png"))
        pr.stdin.write(im.tobytes())
    pr.stdin.close()
    pr.wait()
    wav = out + ".wav"
    mm.write(wav, mm.make(total, seed=seed))
    subprocess.check_call(["ffmpeg", "-loglevel", "error", "-y", "-i", tmp, "-i", wav, "-map", "0:v:0", "-map", "1:a:0",
                           "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-af", "volume=%s" % volume, "-shortest",
                           "-movflags", "+faststart", out])
    os.remove(tmp)
    os.remove(wav)
    return total
