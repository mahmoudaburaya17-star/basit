# -*- coding: utf-8 -*-
"""ريل تجريبي (نوفمبر): جرّب في 30 ثانية - اختبار الشفافية. 1080x1920، حركة كلمة بكلمة + موسيقى."""
import os, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import v2
from v2 import C, Canvas, prog
from PIL import Image, ImageDraw, ImageFilter

W, H, FPS = 1080, 1920, 30
DUR = 26.0
R = W - 80
_glow = None


def glow(cx, cy, rad, color, a=140):
    ly = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ly).ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=v2.rgb(color, a))
    return ly.filter(ImageFilter.GaussianBlur(rad * 0.45))


_cache = {}
def icons():
    if not _cache:
        _cache["sun"] = v2.sun_icon()
        _cache["tee"] = v2.tee_icon(620, 520)
        _cache["bad"] = v2.weave_icon(400, 400, 9)
        _cache["good"] = v2.weave_icon(400, 400, 26)
        _cache["g"] = glow(540, 1090, 300, "#F2B36B", 120)
        _cache["ok"] = v2.badge_icon(True, 40)
        _cache["no"] = v2.badge_icon(False, 40)
    return _cache


def pill(c, text, t):
    p = prog(t, 0.0)
    if p <= 0:
        return
    pw = int(v2.tw(text, v2.font(40)) + 72)
    c.rrect([R - pw, 200, R, 276], C["card"], 38, alpha=p, outline=C["line"])
    c.text(text, R - 36, 211, 40, C["acc2"], True, alpha=p)


def frame(t):
    ic = icons()
    c = Canvas(W, H)
    c.wordmark(y=150)
    if t < 3.4:
        pill(c, "جرّب في 30 ثانية", t)
        y = c.block("تيشيرتك شفاف؟", R, 480, 112, 920, t=t, t0=0.4, step=0.28, lh=1.3)
        c.block("جرّب الاختبار ده في البيت", R, y + 30, 66, 920, C["acc2"], t=t, t0=1.4, step=0.2, lh=1.3)
        c.paste_icon(ic["tee"], W // 2, 1400, prog(t, 1.8, 0.9))
    elif t < 10:
        s = t - 3.4
        pill(c, "الخطوة 1", s)
        c.text("1", R, 330, 300, C["acc"], True, alpha=prog(s, 0.0))
        c.block("ارفعه قدام الضوء", R, 700, 96, 900, t=s, t0=0.4, step=0.3, lh=1.3)
        c.block("شباك أو لمبة قوية", R, 860, 50, 900, C["mute"], False, t=s, t0=1.6, step=0.25)
        g = ic["g"].copy()
        c.put(g, prog(s, 1.2, 1.0))
        c.paste_icon(ic["sun"], W // 2, 1090, prog(s, 1.4, 0.8))
        c.paste_icon(ic["tee"], W // 2, 1480, prog(s, 2.2, 0.8))
    elif t < 17.5:
        s = t - 10
        pill(c, "الخطوة 2", s)
        c.text("2", R, 330, 300, C["acc"], True, alpha=prog(s, 0.0))
        c.block("بص على القماش", R, 700, 96, 900, t=s, t0=0.4, step=0.3, lh=1.3)
        c.block("شايف جلدك أو إيدك من ورا القماش؟", R, 860, 46, 900, C["mute"], False, t=s, t0=1.4, step=0.16)
        for k, (key, lab, good) in enumerate((("good", "نسيج كثيف", True), ("bad", "نسيج مفتوح", False))):
            cx = R - 215 - k * 450
            p = prog(s, 2.6 + k * 1.2, 0.7)
            c.rrect([cx - 215, 1000, cx + 215, 1520], C["card"], 36, alpha=p, outline=C["line"])
            c.paste_icon(ic[key], cx, 1210, p)
            c.paste_icon(ic["ok" if good else "no"], cx + 160, 1040, p)
            c.text(lab, cx, 1430, 42, C["sage"] if good else C["acc"], True, alpha=p, anchor="ma")
    elif t < 22.0:
        s = t - 17.5
        pill(c, "النتيجة", s)
        c.block("الفراغات كبيرة؟", R, 520, 100, 900, C["acc"], t=s, t0=0.3, step=0.28, lh=1.3)
        c.block("القماش هيبان على الجلد وهيحسسك بتعب في الصيف.", R, 720, 54, 900, C["cream"], False, t=s, t0=1.2, step=0.15)
        c.block("نسيج كثيف ومنتظم؟", R, 1040, 100, 900, C["sage"], t=s, t0=2.2, step=0.28, lh=1.3)
        c.block("غالبًا مريح وساتر أكتر.", R, 1240, 54, 900, C["cream"], False, t=s, t0=3.1, step=0.15)
    else:
        s = t - 22.0
        c.block("جرّب دلوقتي", R, 600, 128, 900, t=s, t0=0.2, step=0.3, lh=1.25)
        c.block("وقولنا النتيجة في التعليقات", R, 860, 60, 900, C["acc2"], t=s, t0=1.0, step=0.2)
        c.rrect([R - 520, 1100, R, 1260], C["card"], 40, alpha=prog(s, 1.8), outline=C["line"])
        c.text("تابع بسيط", R - 40, 1135, 76, C["cream"], True, alpha=prog(s, 1.8))
    d = ImageDraw.Draw(c.img)
    d.rectangle([0, 0, int(W * t / DUR), 10], fill=v2.rgb(C["acc"]))
    return c.img.convert("RGB")


def render(out):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", "-an", out]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(DUR * FPS)
    for i in range(n):
        im = frame(i / FPS)
        if i == int(2.5 * FPS):
            im.save(out.replace(".mp4", "-cover.png"))
        pr.stdin.write(im.tobytes())
    pr.stdin.close()
    pr.wait()


if __name__ == "__main__":
    out = os.path.join(v2.ROOT, "v2", "reel-light-test.mp4")
    if len(sys.argv) > 1 and sys.argv[1] == "frames":
        for t in (1.5, 6, 13, 19, 24):
            frame(t).save("/tmp/claude-0/-home-claude/30998021-a284-5eae-bb13-efc9de31dcdb/scratchpad/rf_%s.png" % t)
    else:
        render(out)
