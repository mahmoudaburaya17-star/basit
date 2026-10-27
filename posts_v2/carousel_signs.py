# -*- coding: utf-8 -*-
"""كاروسيل تجريبي (نوفمبر): ٥ علامات إن التيشيرت هيعيش. 7 شرايح 1080x1350."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import v2
from v2 import C, Canvas
from PIL import ImageDraw

W, H = 1080, 1350
OUT = os.path.join(v2.ROOT, "v2", "carousel-signs")
os.makedirs(OUT, exist_ok=True)
N = 7
SIGNS = [
    ("الياقة بترجع لشكلها", "اشدّها بإيدك وسيبها. الياقة الكويسة بترجع مكانها من غير ما تفضل واسعة أو متموجة.",
     lambda: (v2.collar_icon(stretched=True), v2.collar_icon()), ("بتتمط", "بترجع")),
    ("خط الكتف مستقيم", "الخياطة عند الكتف المفروض تبقى مستقيمة ومسطّحة من غير تعرّج أو لف.",
     lambda: (v2.seam_icon(good=False), v2.seam_icon(good=True)), ("معوّج", "مستقيم")),
    ("اختبار الضوء", "ارفعه قدام الشباك. لو شفت جلدك أو إيدك بوضوح من ورا القماش، يبقى هيبان على الجسم.",
     lambda: (v2.weave_icon(380, 300, 9), v2.weave_icon(380, 300, 26)), ("شفاف", "كثيف")),
    ("الحافة من تحت", "الذيل والأكمام بخياطة مزدوجة منتظمة ومتساوية، مش خط واحد متعرّج.",
     lambda: (v2.hem_icon(good=False), v2.hem_icon(good=True)), ("متعرّج", "منتظم")),
    ("سطح القماش متساوي", "بص وإحساس بإيدك: السطح الناعم من غير نتوءات أو وبر زايد بيدل على غزل أحسن.",
     lambda: (v2.surface_icon(good=False), v2.surface_icon(good=True)), ("نتوءات", "متساوي")),
]


def head(c, i):
    c.wordmark(counter="%d / %d" % (i, N))


def slide_cover():
    c = Canvas(W, H)
    head(c, 1)
    pw = int(v2.tw("قبل ما تشتري", v2.font(36)) + 64)
    c.rrect([W - 80 - pw, 150, W - 80, 214], C["card"], 32, outline=C["line"])
    c.text("قبل ما تشتري", W - 80 - 32, 158, 36, C["acc2"], True)
    c.block("٥ علامات بتقولك إن التيشيرت ده هيعيش", W - 80, 280, 104, 900, lh=1.3)
    c.paste_icon(v2.tee_icon(), W // 2, 960)
    c.text("اسحب وشوف", W // 2, 1236, 38, C["mute"], False, anchor="ma")
    return c


def slide_sign(i, sign):
    title, body, icons, labels = sign
    c = Canvas(W, H)
    head(c, i + 2)
    c.text(str(i + 1), W - 80, 100, 220, C["acc"], True)
    c.text(title, W - 80, 410, 78, C["cream"], True)
    y = c.block(body, W - 80, 540, 42, 880, C["mute"], False, lh=1.5)
    bad, good = icons()
    for k, (ic, lab, g) in enumerate(((good, labels[1], True), (bad, labels[0], False))):
        cx = W - 80 - 190 - k * 440
        cy = 990
        c.rrect([cx - 205, cy - 175, cx + 205, cy + 230], C["card"], 34, outline=C["line"])
        c.paste_icon(ic, cx, cy - 10)
        c.paste_icon(v2.badge_icon(g), cx + 150, cy - 140)
        c.text(lab, cx, cy + 150, 40, C["sage"] if g else C["acc"], True, anchor="ma")
    return c


def slide_cta():
    c = Canvas(W, H)
    head(c, N)
    c.block("احفظ البوست وابعته لصاحبك اللي بيشتري تيشيرتات", W - 80, 330, 92, 900, lh=1.35)
    c.rrect([80, 880, W - 80, 1130], C["card"], 34, outline=C["line"])
    c.text("تابع بسيط", W - 130, 920, 70, C["cream"], True)
    c.text("نظرة هادية على التيشيرت السادة، من غير بيع ولا ضجة.", W - 130, 1025, 36, C["mute"], False)
    return c


if __name__ == "__main__":
    slides = [slide_cover()] + [slide_sign(i, s) for i, s in enumerate(SIGNS)] + [slide_cta()]
    for n, c in enumerate(slides, 1):
        c.img.convert("RGB").save(os.path.join(OUT, "%02d.png" % n), optimize=True)
    print("slides", len(slides))
