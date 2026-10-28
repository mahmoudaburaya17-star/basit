# -*- coding: utf-8 -*-
"""بنّاء بوستات v2: كاروسيل (cover/item/end) وكروت مفردة (tip/poll) بمقاس 1080x1350."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v2  # noqa: E402
from v2 import C, Canvas, S, icon_canvas, finish, rgb  # noqa: E402
from PIL import ImageDraw  # noqa: E402

W, H = 1080, 1350


def pill(c, text, y=150):
    pw = int(v2.tw(text, v2.font(36)) + 64)
    c.rrect([W - 80 - pw, y, W - 80, y + 64], C["card"], 32, outline=C["line"])
    c.text(text, W - 80 - 32, y + 8, 36, C["acc2"], True)


def stamp_icon(text, good, w=380, h=300):
    im = icon_canvas(w, h)
    d = ImageDraw.Draw(im)
    col = C["sage"] if good else C["acc"]
    d.rounded_rectangle([40 * S, 60 * S, (w - 40) * S, (h - 60) * S], radius=40 * S, fill=rgb(col))
    im = finish(im)
    c = ImageDraw.Draw(im)
    c.text((w / 2, h / 2 - 8), text, font=v2.font(110), fill=rgb("#0C120F"), anchor="mm", direction="rtl", language="ar")
    return im


def symbol_icon(kind, w=380, h=300, label=""):
    im = icon_canvas(w, h)
    d = ImageDraw.Draw(im)
    ink = rgb("#E8E1D2")
    lw = int(9 * S)
    cx, cy = w / 2 * S, h / 2 * S
    u = S
    if kind == "bucket":
        d.polygon([(cx - 90 * u, cy - 50 * u), (cx + 90 * u, cy - 50 * u), (cx + 70 * u, cy + 70 * u), (cx - 70 * u, cy + 70 * u)], outline=ink, width=lw)
        d.line([(cx - 90 * u, cy - 50 * u), (cx - 60 * u, cy - 70 * u), (cx + 60 * u, cy - 70 * u), (cx + 90 * u, cy - 50 * u)], fill=ink, width=lw)
    elif kind == "triangle":
        d.polygon([(cx, cy - 85 * u), (cx - 90 * u, cy + 70 * u), (cx + 90 * u, cy + 70 * u)], outline=ink, width=lw)
    elif kind == "tumble":
        d.rectangle([cx - 85 * u, cy - 85 * u, cx + 85 * u, cy + 85 * u], outline=ink, width=lw)
        d.ellipse([cx - 55 * u, cy - 55 * u, cx + 55 * u, cy + 55 * u], outline=ink, width=lw)
    elif kind == "iron":
        d.polygon([(cx - 95 * u, cy + 60 * u), (cx + 95 * u, cy + 60 * u), (cx + 70 * u, cy - 10 * u), (cx + 10 * u, cy - 55 * u), (cx - 95 * u, cy - 55 * u)], outline=ink, width=lw)
    elif kind == "dry":
        d.ellipse([cx - 80 * u, cy - 80 * u, cx + 80 * u, cy + 80 * u], outline=ink, width=lw)
    if label:
        im = finish(im)
        ImageDraw.Draw(im).text((w / 2, h / 2 + (14 if kind == "bucket" else 6)), label, font=v2.font(46), fill=rgb("#E8E1D2"), anchor="mm")
        return im
    return finish(im)


def swatch_icon(colors, w=380, h=300):
    im = icon_canvas(w, h)
    d = ImageDraw.Draw(im)
    n = len(colors)
    gap = 14
    sw = (w - gap * (n + 1)) / n
    for i, col in enumerate(colors):
        x0 = gap + i * (sw + gap)
        d.rounded_rectangle([x0 * S, 30 * S, (x0 + sw) * S, (h - 30) * S], radius=26 * S, fill=rgb(col), outline=rgb(C["line"]), width=int(3 * S))
    return finish(im)


def head(c, i, n):
    c.wordmark(counter="%d / %d" % (i, n))


def cover(title, kicker, n):
    c = Canvas(W, H)
    head(c, 1, n)
    pill(c, kicker, 150)
    c.block(title, W - 80, 280, 100, 900, lh=1.3)
    c.paste_icon(v2.tee_icon(), W // 2, 1000)
    c.text("اسحب وشوف", W // 2, 1250, 38, C["mute"], False, anchor="ma")
    return c


def panel(c, cx, cy, icon, label=None, good=None):
    c.rrect([cx - 205, cy - 175, cx + 205, cy + 230], C["card"], 34, outline=C["line"])
    c.paste_icon(icon, cx, cy - 10)
    if good is not None:
        c.paste_icon(v2.badge_icon(good), cx + 150, cy - 140)
    if label:
        c.text(label, cx, cy + 150, 40, C["sage"] if good in (True, None) else C["acc"], True, anchor="ma")


def item(i, n, num, title, body, visual=None, takeaway=None):
    """visual: ('pair', bad_icon, good_icon, bad_label, good_label) | ('one', icon, label) | None"""
    c = Canvas(W, H)
    head(c, i, n)
    c.text(str(num), W - 80, 100, 220, C["acc"], True)
    c.text(title, W - 80, 410, 78, C["cream"], True)
    c.block(body, W - 80, 540, 42, 880, C["mute"], False, lh=1.5)
    if visual and visual[0] == "pair":
        _, bad, good, bl, gl = visual
        panel(c, W - 80 - 190, 990, good, gl, True)
        panel(c, W - 80 - 190 - 440, 990, bad, bl, False)
    elif visual and visual[0] == "one":
        panel(c, W // 2, 990, visual[1], visual[2], None)
    elif takeaway:
        c.rrect([80, 880, W - 80, 1200], C["card"], 34, outline=C["line"])
        c.text("الخلاصة", W - 120, 920, 34, C["acc2"], True)
        c.block(takeaway, W - 120, 985, 54, 840, C["cream"], True, lh=1.35)
    return c


def end(i, n, title="احفظ البوست وابعته لصاحبك", sub="نظرة هادية على التيشيرت السادة، من غير بيع ولا ضجة."):
    c = Canvas(W, H)
    head(c, i, n)
    c.block(title, W - 80, 330, 96, 900, lh=1.35)
    c.rrect([80, 880, W - 80, 1130], C["card"], 34, outline=C["line"])
    c.text("تابع بسيط", W - 130, 920, 70, C["cream"], True)
    c.text(sub, W - 130, 1025, 36, C["mute"], False)
    return c


def tip_card(kicker, title, body):
    c = Canvas(W, H)
    c.wordmark(counter=None)
    pill(c, kicker, 150)
    y = c.block(title, W - 80, 330, 96, 900, C["cream"], True, lh=1.3)
    c.rrect([80, y + 50, W - 80, y + 54], C["acc"], 2)
    c.block(body, W - 80, y + 100, 50, 880, C["mute"], False, lh=1.55)
    c.paste_icon(v2.tee_icon(360, 300), W // 2 + 250, 1180)
    return c


def poll_card(kicker, question, options):
    c = Canvas(W, H)
    c.wordmark(counter=None)
    pill(c, kicker, 150)
    y = c.block(question, W - 80, 320, 90, 900, C["cream"], True, lh=1.3)
    y += 70
    for k, o in enumerate(options):
        c.rrect([80, y, W - 80, y + 130], C["card"], 36, outline=C["line"])
        c.rrect([W - 80 - 100, y + 15, W - 80 - 20, y + 115], C["acc"], 28)
        c.text(str(k + 1), W - 80 - 60, y + 22, 64, "#0C120F", True, anchor="ma")
        c.text(o, W - 80 - 140, y + 32, 52, C["cream"], True)
        y += 160
    c.text("اكتب رقم اختيارك في التعليقات", W // 2, min(y + 40, 1250), 38, C["mute"], False, anchor="ma")
    return c


def save(c, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    c.img.convert("RGB").save(path, optimize=True)
