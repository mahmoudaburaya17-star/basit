# -*- coding: utf-8 -*-
"""ريلز موشن جرافيك بالكود (بالمصري): بعضها كوميدي بشخصية "بسيط" وبعضها شرح نظيف.
python3 tools/mg_reels.py <name> out.mp4   |   frames <name> sheet.jpg t1 t2 ...
الأسماء: closet (كوميدي) | dark (شرح) | print (اختبار) | cotton (كوميدي خفيف)"""
import math, os, random, sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mg
from mg import *  # noqa
import v2
from v2engine import pill


def icon_on(st, name, cx, cy, w, h, alpha=1.0):
    im = v2.icon(name, int(w), int(h))
    im = im.resize((int(im.width * SS), int(im.height * SS)), Image.LANCZOS)
    if alpha < 1:
        im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    x, y = st.P(cx, cy)
    st.im.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))


def make_frame(stage_fn, heads, pill_text, total, cta):
    """heads: [(t0, text)] عناوين كينيتك. cta: (t0, main, sub)"""
    def frame_fn(t):
        c = Canvas(W, H)
        c.wordmark(y=150)
        st, bubs, extra = stage_fn(t)
        if extra and extra.get("heat", 0) > 0:
            g = Image.new("RGBA", (W // 2, H // 2), (0, 0, 0, 0))
            ImageDraw.Draw(g).ellipse([120, 320, 620, 820], fill=(230, 80, 40, int(150 * extra["heat"])))
            c.img.alpha_composite(g.filter(ImageFilter.GaussianBlur(50)).resize((W, H), Image.BILINEAR))
        for (txt, bx, by, p, tail) in bubs:
            bubble(st, txt, bx, by, p, tail, size=46)
        c.img.alpha_composite(st.result(), (0, Y0))
        pill(c, pill_text, W, 195, 1)
        cur = None
        for h0, txt in heads:
            if t >= h0:
                cur = (h0, txt)
        if cur and t < cta[0]:
            c.block(cur[1], 1000, 250, 98, 920, t=t - cur[0], t0=0.0, step=0.28, lh=1.25)
        if t >= cta[0]:
            ov = Image.new("RGBA", (W, H), (12, 18, 15, int(247 * prog(t, cta[0], 0.5))))
            c.img.alpha_composite(ov)
            y = c.block(cta[1], 1000, 600, 104, 920, t=t - cta[0] - 0.2, t0=0.0, step=0.3, lh=1.3)
            c.block(cta[2], 1000, y + 30, 60, 920, C["acc2"], t=t - cta[0] - 0.9, t0=0.0, step=0.2, lh=1.3)
            c.rrect([430, 1180, 1000, 1330], C["card"], 40, alpha=prog(t, cta[0] + 1.6), outline=C["line"])
            c.text("تابعنا على بسيط", 960, 1215, 70, C["cream"], True, alpha=prog(t, cta[0] + 1.6))
        dr = ImageDraw.Draw(c.img)
        dr.rectangle([0, 0, int(W * t / total), 10], fill=rgb(C["acc"]))
        return c.img.convert("RGB")
    return frame_fn


def sparkle(st, x, y, r, a=255, color="#F2B36B"):
    c = rgb(color, a)
    st.poly([(x, y - r), (x + r * 0.25, y - r * 0.25), (x + r, y), (x + r * 0.25, y + r * 0.25), (x, y + r),
             (x - r * 0.25, y + r * 0.25), (x - r, y), (x - r * 0.25, y - r * 0.25)], c)


# =============================== 1) الدولاب (كوميدي) ===============================
CL_TOTAL = 21.0
FAV = {1, 5, 6, 10}


def closet_stage(t):
    st = Stage()
    bubs = []
    st.rr(60, 880, 1020, 1690, 40, fill="#22342A", outline="#3C5446", width=6)
    for y in (1130, 1400):
        st.rr(80, y, 1000, y + 16, 8, fill="#3C5446")
    for k in range(12):
        row, col = k // 4, k % 4
        x = 190 + col * 233
        y = 1115 + row * 270
        p = back(seg(t, 2.0 + 0.2 * k, 2.5 + 0.2 * k))
        if p <= 0:
            continue
        fav = k in FAV
        sc = 0.40 * p
        face, tint, yy, sx, sy = "happy", None, y, 1, 1
        if t > 7.0 and fav and t < 11.3:
            ph = (t - 7.0) * 5 + k
            yy = y - 16 * abs(math.sin(ph))
            face = "proud"
            if int(t * 4) % 2 == 0:
                sparkle(st, x + 66, y - 120, 14)
        if t >= 11.0 and not fav:
            tint = "#A5ADA4"
            face = "pain"
            sy = 1 - 0.04 * math.sin(t * 3 + k)
        if t >= 11.0 and fav:
            face = "proud"
        mascot(st, x, yy, sc, sx=sx, sy=sy, face=face, tint=tint)
    if 7.4 <= t < 11.3:
        bubs.append(("أنا اللي بتلبسني كل يوم!", 560, 960, seg(t, 7.4, 7.8), (-140, 120)))
    if 11.6 <= t < 12.8:
        bubs.append(("حد فاكرني؟", 330, 960, seg(t, 11.6, 12.0), (-40, 130)))
    if t >= 12.8:
        bubs.append(("أنا هنا من 6 شهور!", 760, 1230, seg(t, 12.8, 13.2), (110, 120)))
    return st, bubs, None


CL_EVENTS = [(1.9 + 0.2 * k, sfx_pop(500 + 40 * k), 0.22) for k in range(12)] + [
    (7.4, sfx_ding(), 0.4), (7.4, sfx_boing(), 0.2), (11.0, sfx_slide(0.9, 900, 220), 0.4), (11.6, sfx_pop(500), 0.3),
    (12.8, sfx_pop(420), 0.3), (17.4, sfx_whoosh(0.4, True), 0.25)]
CL_HEADS = [(0.0, "دولابك فيه 12 تيشيرت.. بتلبس منهم كام؟"), (7.0, "في العادة بنلبس 4 بس!"),
            (11.0, "والباقي قاعد مستني دوره"), (14.8, "اسأل نفسك: ليه؟ المقاس؟ الخامة؟")]
closet_frame = make_frame(closet_stage, CL_HEADS, "هزار في هزار", CL_TOTAL,
                          (17.4, "كام تيشيرت بتلبسهم فعلًا؟", "قولنا رقمك في التعليقات"))


# =============================== 2) الغامق والعيوب (شرح) ===============================
DK_TOTAL = 20.5
DARK, DARKL = "#3A4750", "#222C33"
_rs = random.Random(4)
SPECKS = [(_rs.uniform(-92, 92), _rs.uniform(-100, 140), _rs.uniform(3.5, 7)) for _ in range(34)]


def shirt_plain(st, cx, cy, s, dark, specks_p, yoff=0):
    body = xf(BODY, cx, cy + yoff, s)
    st.ell(cx, cy + yoff + 6 * s, 135 * s, 16 * s, fill=(0, 0, 0, 70))
    st.poly(body, DARK if dark else CREAM, DARKL if dark else SHADE, 7 * s)
    pts = xf([(-55, -170), (-36, -138), (0, -126), (36, -138), (55, -170)], cx, cy + yoff, s)
    st.line(pts, "#4C5B66" if dark else "#CDBF9C", 12 * s)
    n = int(len(SPECKS) * specks_p)
    for i in range(n):
        x, y, r = SPECKS[i]
        px, py = xf([(x, y)], cx, cy + yoff, s)[0]
        st.circ(px, py, r * s * 1.1, fill=(236, 230, 214, 235) if dark else (190, 178, 150, 45))


CARDS = [("اقلبه من جوه قبل الغسيل", "tee"), ("مية باردة ومنظف قليل", "drop"), ("انشره في الظل", "sun")]


def dark_stage(t):
    st = Stage()
    lift = eio(seg(t, 7.0, 8.0))
    if lift < 1:
        yoff = -1000 * lift
        sl = back(seg(t, 0.5, 1.4))
        shirt_plain(st, 290, 1330, 0.9, False, seg(t, 3.0, 6.0), yoff - (1 - sl) * 700)
        shirt_plain(st, 790, 1330, 0.9, True, seg(t, 3.0, 6.0), yoff - (1 - sl) * 700)
        if t > 2.0:
            a = seg(t, 2.0, 2.5)
            st.rr(110, 1420, 470, 1500, 30, fill=(31, 46, 38, int(255 * a)), outline=rgb("#34463B", int(255 * a)), width=4)
            st.text("فاتح: العيوب مستخبية", 290, 1460, 38, C["sage"], True) if a > 0.5 else None
            st.rr(610, 1420, 970, 1500, 30, fill=(31, 46, 38, int(255 * a)), outline=rgb("#34463B", int(255 * a)), width=4)
            st.text("غامق: كله باين!", 790, 1460, 38, C["acc2"], True) if a > 0.5 else None
    for i, (txt, ic) in enumerate(CARDS):
        t0 = 8.2 + 2.2 * i
        p = ease(seg(t, t0, t0 + 0.6))
        if p <= 0:
            continue
        y = 740 + i * 250
        dx = (1 - p) * 700
        st.rr(70 + dx, y, 1010 + dx, y + 200, 42, fill=(31, 46, 38, int(255 * p)), outline=rgb("#34463B", int(255 * p)), width=4)
        st.circ(930 + dx, y + 100, 56, fill="#E6784F")
        st.text(str(i + 1), 930 + dx, y + 96, 70, "#18251E", True)
        st.text(txt, 860 + dx, y + 100, 52, C["cream"], True, anchor="rm")
        icon_on(st, ic, 170 + dx, y + 100, 150, 120, p)
    return st, [], None


DK_EVENTS = [(0.5, sfx_whoosh(0.6), 0.35), (1.3, sfx_thud(), 0.3), (2.0, sfx_pop(600), 0.3), (3.0, sfx_whoosh(1.5), 0.15),
             (7.0, sfx_whoosh(0.5, True), 0.35), (8.2, sfx_pop(700), 0.4), (10.4, sfx_pop(800), 0.4), (12.6, sfx_pop(900), 0.4),
             (14.9, sfx_ding(1568), 0.3)]
DK_HEADS = [(0.0, "ليه العيوب بتبان أكتر على الغامق؟"), (3.0, "الوبر والبهتان والرواسب بتظهر عليه أسرع"),
            (7.2, "٣ حاجات بتفرق")]
dark_frame = make_frame(dark_stage, DK_HEADS, "حكاية خامة", DK_TOTAL,
                        (15.2, "جرّب كده وقولنا", "لونك المفضل إيه؟"))


# =============================== 3) اختبار الطباعة (شرح) ===============================
PR_TOTAL = 19.0


def check(st, x, y, r, good):
    if good:
        st.circ(x, y, r, fill="#6FD39B")
        st.line([(x - r * 0.45, y), (x - r * 0.1, y + r * 0.35), (x + r * 0.5, y - r * 0.35)], "#18251E", r * 0.28)
    else:
        st.circ(x, y, r, fill="#FF6A4D")
        st.line([(x - r * 0.4, y - r * 0.4), (x + r * 0.4, y + r * 0.4)], "#18251E", r * 0.28)
        st.line([(x + r * 0.4, y - r * 0.4), (x - r * 0.4, y + r * 0.4)], "#18251E", r * 0.28)


def print_stage(t):
    st = Stage()
    slide = back(seg(t, 0.4, 1.3))
    pull = 0.0
    if 3.0 <= t < 8.0:
        pull = math.sin(seg(t, 3.0, 8.0) * math.pi)       # شد وبعدين رجوع
    sxf = 1 + 0.20 * pull
    crack = clamp(pull * 1.4) if t < 8.0 else (1.0 if t >= 8.0 else 0)
    if t >= 8.0:
        crack = 1.0
    for side, (cx, good) in enumerate(((270, True), (810, False))):
        y0 = 1300 - (1 - slide) * 800
        body = xf(BODY, cx, y0, 1.0, sx=sxf)
        st.ell(cx, y0 + 6, 130, 15, fill=(0, 0, 0, 70))
        st.poly(body, CREAM, SHADE, 6)
        st.line(xf([(-55, -170), (-36, -138), (0, -126), (36, -138), (55, -170)], cx, y0, 1.0, sx=sxf), "#CDBF9C", 11)
        psx = sxf if good else 1.0
        patch = xf([(-62, -80), (62, -80), (62, 20), (-62, 20)], cx, y0, 1.0, sx=psx)
        st.poly(patch, "#E6784F", "#B95A38", 3)
        # تفاصيل الطباعة
        mid = xf([(0, -30)], cx, y0, 1.0, sx=psx)[0]
        st.circ(mid[0], mid[1], 20, fill="#F6D8C3")
        if not good and crack > 0.05:
            rr_ = random.Random(5)
            for i in range(7):
                x = rr_.uniform(-55, 55); yy = rr_.uniform(-76, 16)
                n = int(2 + 3 * crack)
                pts = [xf([(x + k * 9 * rr_.choice((-1, 1)) * crack, yy + k * 8)], cx, y0, 1.0, sx=1.0)[0] for k in range(n)]
                st.line(pts, "#4A2418", 3)
            if crack > 0.5:
                for i in range(3):
                    fx = cx - 40 + i * 40
                    fy = y0 - 140 + ((t * 120 + i * 70) % 220)
                    st.poly([(fx, fy), (fx + 8, fy + 4), (fx + 3, fy + 12)], "#E6784F")
        # أسهم الشد
        if 3.0 <= t < 8.0:
            for k in (-1, 1):
                hx = cx + k * (215 * sxf + 20 + 14 * pull)
                hy = y0 - 60
                st.poly([(hx, hy - 24), (hx + k * 42, hy), (hx, hy + 24)], "#F2B36B")
                st.line([(hx - k * 34, hy), (hx, hy)], "#F2B36B", 12)
        # حكم
        if t >= 8.2:
            a = seg(t, 8.2, 8.8)
            st.rr(cx - 190, 1450, cx + 190, 1540, 30, fill=(31, 46, 38, int(255 * a)), outline=rgb("#34463B", int(255 * a)), width=4)
            if a > 0.5:
                st.text("بتتحرك مع القماش" if good else "بتتشقق وتتقشر", cx, 1495, 36, C["sage"] if good else C["acc"], True)
                check(st, cx + 160, 1425, 28, good)
    return st, [], None


PR_EVENTS = [(0.4, sfx_whoosh(0.7), 0.35), (1.3, sfx_thud(), 0.3), (3.0, sfx_slide(1.0, 300, 700), 0.2),
             (5.0, sfx_pop(300), 0.25), (5.4, sfx_pop(260), 0.25), (6.0, sfx_pop(280), 0.2), (8.2, sfx_ding(), 0.4),
             (8.4, sfx_slide(0.6, 800, 200), 0.3), (14.8, sfx_whoosh(0.4, True), 0.2)]
PR_HEADS = [(0.0, "طباعة تيشيرتك بتستحمل الشد؟"), (3.0, "شدّ القماش تحت الطباعة شدّة خفيفة"),
            (8.2, "الطباعة الكويسة بتتحرك مع القماش")]
print_frame = make_frame(print_stage, PR_HEADS, "جرّب في 30 ثانية", PR_TOTAL,
                         (14.6, "جرّبها دلوقتي", "وقولنا النتيجة في التعليقات"))


# =============================== 4) القطن بيتكرمش (كوميدي خفيف) ===============================
CT_TOTAL = 19.5


def iron_draw(st, x, y, steam_on, t):
    st.poly([(x - 130, y), (x + 120, y), (x + 150, y - 40), (x + 80, y - 90), (x - 120, y - 90)], "#CFC6AF", "#9E957E", 5)
    st.poly([(x - 130, y), (x + 120, y), (x + 150, y - 40), (x + 100, y - 8), (x - 130, y - 8)], "#E6784F")
    st.rr(x - 100, y - 150, x + 60, y - 85, 30, fill="#2A3A32", outline="#9E957E", width=4)
    if steam_on:
        for i in range(4):
            ph = (t * 1.1 + i * 0.27) % 1
            st.circ(x - 60 + i * 55, y + 10 - ph * 60 + 40, 10 + ph * 22, fill=(255, 255, 255, int(160 * (1 - ph))))


def cotton_stage(t):
    st = Stage()
    bubs = []
    FXX, FYY = 380, 1560
    wr = 1.0 - eio(seg(t, 4.0, 9.0))
    face = "pain" if t < 8.6 else "happy"
    p = back(seg(t, 0.4, 1.1))
    yy = FYY - (1 - clamp(p)) * 800
    sxm = 1.0
    if 8.6 <= t < 9.2:
        k = seg(t, 8.6, 9.2)
        sxm = 1 + 0.12 * math.sin(k * math.pi)
    mascot(st, FXX, yy, 1.35 if False else 1.0, sx=sxm, face=face if t > 0.6 else "pain", wrinkle=clamp(wr),
           sweat=t * 2 if t < 4.0 and t > 1.4 else 0)
    if t >= 1.6 and t < 4.4:
        bubs.append(("أنا متكرمش خالص!", 400, FYY - 560, seg(t, 1.6, 2.0), (-30, 150)))
    if 4.0 <= t < 9.2:
        k = seg(t, 4.0, 9.0)
        ix = 380 + 140 * math.sin(k * math.pi * 5) + (1 - eio(seg(t, 4.0, 4.7))) * 600
        iy = FYY - 330 - 20 * math.sin(k * 40)
        iron_draw(st, ix, iy, True, t)
    if t >= 9.4 and t < 12.6:
        bubs.append(("آه.. كده أحسن بكتير!", 400, FYY - 560, seg(t, 9.4, 9.8), (-30, 150)))
    if t >= 9.6:
        for i in range(5):
            a = (t * 2 + i) % 3 / 3.0
            sparkle(st, 380 - 190 + i * 95 + 30 * math.sin(t + i), FYY - 360 + 40 * math.cos(i * 2), 12 * (1 - a), int(255 * (1 - a)))
    return st, bubs, None


CT_EVENTS = [(0.4, sfx_whoosh(0.6), 0.3), (1.1, sfx_thud(), 0.4), (1.6, sfx_pop(600), 0.3), (2.3, sfx_slide(0.8, 600, 200), 0.3),
             (4.0, sfx_whoosh(0.6), 0.35), (5.0, sfx_pop(400), 0.15), (6.2, sfx_pop(420), 0.15), (7.4, sfx_pop(440), 0.15),
             (8.6, sfx_boing(), 0.3), (8.7, sfx_ding(1568), 0.4), (9.4, sfx_pop(900), 0.3), (15.0, sfx_whoosh(0.4, True), 0.2)]
CT_HEADS = [(0.0, "القطن بيتكرمش؟ أيوه فعلًا!"), (4.0, "كل الحكاية في الغسيل والنشر"), (9.6, "انشره مفرود وعلّقه وهو لسه ناشف شوية"),]
cotton_frame = make_frame(cotton_stage, CT_HEADS, "هزار في هزار", CT_TOTAL,
                          (15.0, "بتكوي ولا بتعلّق؟", "قولنا في التعليقات"))

REELS = {
    "closet": (closet_frame, CL_TOTAL, CL_EVENTS, None, 11),
    "dark": (dark_frame, DK_TOTAL, DK_EVENTS, None, 12),
    "print": (print_frame, PR_TOTAL, PR_EVENTS, None, 13),
    "cotton": (cotton_frame, CT_TOTAL, CT_EVENTS, None, 14),
}

if __name__ == "__main__":
    if sys.argv[1] == "frames":
        fn = REELS[sys.argv[2]][0]
        ts = [float(x) for x in sys.argv[4:]]
        ims = [fn(t).resize((360, 640)) for t in ts]
        sheet = Image.new("RGB", (360 * len(ims), 640))
        for i, im in enumerate(ims):
            sheet.paste(im, (360 * i, 0))
        sheet.save(sys.argv[3])
    else:
        fr, total, ev, hum, seed = REELS[sys.argv[1]]
        render_generic(sys.argv[2], fr, total, ev, hum, seed)
