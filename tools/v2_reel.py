# -*- coding: utf-8 -*-
"""محرك ريلز v2 مبني على مشاهد: hook / step / myth / stat / list / end.  كل ريل = سبيك dict.
الاستخدام من بايثون: render_reel(spec, out_mp4)"""
import math
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v2  # noqa: E402
import make_music as mm  # noqa: E402
from v2 import C, Canvas, prog  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

W, H, FPS = 1080, 1920, 30
R = W - 80
_ic = {}


def ic():
    if not _ic:
        _ic["tee"] = v2.tee_icon(620, 520)
        _ic["ok"] = v2.badge_icon(True, 44)
        _ic["no"] = v2.badge_icon(False, 44)
        _ic["sun"] = v2.sun_icon()
    return _ic


def read_time(text, per_word=0.32, base=1.2):
    return base + len(text.split()) * per_word


def dur(scene):
    k = scene["k"]
    if k == "hook":
        return 3.6 + 0.2 * len(scene.get("sub", "").split())
    if k == "step":
        return max(4.8, read_time(scene["body"], 0.28, 2.6))
    if k == "myth":
        return 4.2 + 2.6 + max(5.0, read_time(scene["why"], 0.28, 2.2))
    if k == "stat":
        return 7.0
    if k == "list":
        return 2.4 + len(scene["items"]) * 3.0 + 1.0
    if k == "beats":
        return sum(max(2.6, read_time(b, 0.30, 1.0)) for b in scene["lines"]) + 0.8
    if k == "end":
        return 4.6
    raise ValueError(k)


def total(spec):
    return sum(dur(s) for s in spec["scenes"])


def pill(c, text, t, y=215):
    p = prog(t, 0.0)
    if p <= 0:
        return
    pw = int(v2.tw(text, v2.font(40)) + 72)
    c.rrect([R - pw, y, R, y + 76], C["card"], 38, alpha=p, outline=C["line"])
    c.text(text, R - 36, y + 11, 40, C["acc2"], True, alpha=p)


def ring(c, cx, cy, r, p, color):
    ly = c.layer()
    d = ImageDraw.Draw(ly)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=v2.rgb(C["line"]), width=14)
    d.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * p, fill=v2.rgb(color), width=14)
    c.put(ly)


def scene_frame(c, spec, sc, s):
    k = sc["k"]
    series = spec["series"]
    if k == "hook":
        pill(c, series, s)
        y = c.block(sc["title"], R, 480, 112, 920, t=s, t0=0.4, step=0.28, lh=1.3)
        if sc.get("sub"):
            c.block(sc["sub"], R, y + 30, 66, 920, C["acc2"], t=s, t0=1.5, step=0.2, lh=1.3)
        c.paste_icon(ic()["tee"], W // 2, 1420, prog(s, 1.8, 0.9))
    elif k == "step":
        pill(c, series if sc.get("pill") is None else sc["pill"], s)
        c.text(str(sc["n"]), R, 330, 300, C["acc"], True, alpha=prog(s, 0.0))
        y = c.block(sc["title"], R, 700, 92, 920, t=s, t0=0.4, step=0.3, lh=1.3)
        c.block(sc["body"], R, y + 30, 50, 920, C["cream"], False, t=s, t0=1.4, step=0.22, lh=1.5)
    elif k == "myth":
        pill(c, "صح ولا غلط؟", s)
        if s < 4.2:
            c.block(sc["claim"], R, 560, 96, 920, t=s, t0=0.3, step=0.26, lh=1.35)
        elif s < 6.8:
            u = s - 4.2
            c.block(sc["claim"], R, 360, 64, 920, C["mute"], lh=1.35)
            ring(c, W // 2, 1100, 170, min(1, u / 2.4), C["acc2"])
            c.text(str(max(1, 3 - int(u / 0.87))), W // 2, 1040, 170, C["cream"], True, anchor="ma")
        else:
            u = s - 6.8
            c.block(sc["claim"], R, 360, 56, 920, C["mute"], lh=1.35)
            col = C["sage"] if sc["verdict"] == "صح" else C["acc"]
            p = prog(u, 0.0, 0.5)
            pw = 420
            c.rrect([W // 2 - pw // 2, 640, W // 2 + pw // 2, 640 + int(250 * (0.6 + 0.4 * p))], col, 44, alpha=p)
            c.text(sc["verdict"], W // 2, 672, 130, "#0C120F", True, alpha=p, anchor="ma")
            c.block(sc["why"], R, 990, 54, 920, C["cream"], False, t=u, t0=0.8, step=0.2, lh=1.5)
    elif k == "stat":
        pill(c, series, s)
        c.block(sc["title"], R, 400, 70, 920, C["mute"], lh=1.3)
        p = prog(s, 0.6, 1.6)
        val = sc["value"] * p
        txt = ("%d" % round(val)) if sc.get("int", True) else ("%.1f" % val)
        c.text(txt + (" " + sc["unit"] if sc.get("unit") else ""), R, 640, 230, C["acc"], True, alpha=1.0)
        # أعمدة مقارنة
        y = 1010
        for i, (lab, v, col) in enumerate(sc["bars"]):
            pb = prog(s, 1.8 + i * 0.8, 0.9)
            mx = max(b[1] for b in sc["bars"])
            bw = int((W - 160) * 0.62 * v / mx * pb)
            c.rrect([R - bw, y, R, y + 70], col, 22, alpha=1.0 if pb > 0 else 0)
            c.text(lab, R, y + 84, 40, C["cream"], True, alpha=pb)
            c.text(sc.get("barfmt", "%d") % v, R - bw - 16, y + 8, 46, C["cream"], True, alpha=pb, anchor="ra")
            y += 210
        if sc.get("note"):
            c.text(sc["note"], R, 1650, 34, C["mute"], False, alpha=prog(s, 4.2))
    elif k == "list":
        pill(c, series, s)
        c.block(sc["title"], R, 420, 84, 920, lh=1.3, t=s, t0=0.2, step=0.22)
        y0 = 760
        for i, it in enumerate(sc["items"]):
            p = prog(s, 2.4 + i * 3.0, 0.6)
            if p <= 0:
                continue
            c.rrect([80, y0, R, y0 + 210], C["card"], 32, alpha=p, outline=C["line"])
            c.text(str(i + 1), R - 36, y0 + 40, 100, C["acc"], True, alpha=p)
            c.block(it, R - 150, y0 + 60, 50, 700, C["cream"], True, lh=1.3)
            y0 += 240
    elif k == "beats":
        pill(c, series, s)
        t0 = 0.3
        y = 420
        for b in sc["lines"]:
            d = max(2.6, read_time(b, 0.30, 1.0))
            if s >= t0:
                y = c.block(b, R, y, 66, 920, C["cream"] if s - t0 < d + 0.01 or True else C["mute"], True, lh=1.4,
                            t=s, t0=t0, step=0.16) + 46
            t0 += d
    elif k == "end":
        c.block(sc.get("title", "جرّب دلوقتي"), R, 600, 128, 920, t=s, t0=0.2, step=0.3, lh=1.25)
        c.block(sc.get("sub", "وقولنا النتيجة في التعليقات"), R, 860, 60, 920, C["acc2"], t=s, t0=1.0, step=0.2)
        c.rrect([R - 520, 1100, R, 1260], C["card"], 40, alpha=prog(s, 1.8), outline=C["line"])
        c.text("تابع بسيط", R - 40, 1135, 76, C["cream"], True, alpha=prog(s, 1.8))


def frame(spec, t):
    scenes = spec["scenes"]
    acc = 0.0
    for sc in scenes:
        d = dur(sc)
        if t < acc + d or sc is scenes[-1]:
            c = Canvas(W, H)
            c.wordmark(y=150)
            scene_frame(c, spec, sc, t - acc)
            T = total(spec)
            ImageDraw.Draw(c.img).rectangle([0, 0, int(W * t / T), 10], fill=v2.rgb(C["acc"]))
            return c.img.convert("RGB")
        acc += d


def render_reel(spec, out, seed=0, cover_t=None):
    T = total(spec)
    tmp = out + ".silent.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-pix_fmt", "yuv420p", "-an", tmp]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(T * FPS)
    ct = int((cover_t if cover_t is not None else 2.6) * FPS)
    for i in range(n):
        im = frame(spec, i / FPS)
        if i == ct:
            im.save(out.replace(".mp4", "-cover.png"))
        pr.stdin.write(im.tobytes())
    pr.stdin.close()
    pr.wait()
    wav = out + ".wav"
    mm.write(wav, mm.make(T, seed=seed))
    subprocess.check_call(["ffmpeg", "-loglevel", "error", "-y", "-i", tmp, "-i", wav, "-map", "0:v:0", "-map", "1:a:0",
                           "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-af", "volume=0.7", "-shortest",
                           "-movflags", "+faststart", out])
    os.remove(tmp)
    os.remove(wav)
    return T
