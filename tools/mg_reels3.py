# -*- coding: utf-8 -*-
"""ريلز دفعة 3: label (شرح) | fit (كوميدي). python3 tools/mg_reels3.py <name> out.mp4 | frames <name> sheet.jpg t.."""
import math, os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mg_reels import *  # noqa
from mg_reels import shirt_plain, make_frame, icon_on, sparkle
import mg_reels as R

# ===== 1) التيكت (الليبل) بيقولك إيه (شرح) =====
LB_TOTAL = 21.0
LCARDS = [("درجة الغسيل المناسبة", "thermo_low"), ("نوع الخامة", "cotton"), ("تعليمات الكي", "iron")]


def label_stage(t):
    st = Stage()
    lift = eio(seg(t, 7.0, 8.0))
    if lift < 1:
        sl = back(seg(t, 0.5, 1.4))
        yoff = -1000 * lift - (1 - sl) * 800
        shirt_plain(st, 540, 1300, 1.25, False, 0, yoff)
        k = seg(t, 2.5, 3.3)
        if k > 0:
            x, y = 640, 1300 + yoff - 190
            st.rr(x - 55, y, x + 55, y + 120, 12, fill=(255, 255, 255, int(255 * k)), outline=rgb("#CDBF9C", int(255 * k)), width=5)
            for i in range(3):
                st.line([(x - 32, y + 30 + i * 30), (x + 32, y + 30 + i * 30)], (120, 110, 90, int(255 * k)), 7)
        if t > 3.6:
            a = seg(t, 3.6, 4.2)
            st.rr(150, 1520, 930, 1620, 30, fill=(31, 46, 38, int(255 * a)), outline=rgb("#34463B", int(255 * a)), width=4)
            if a > 0.5:
                st.text("جوه التيشيرت من ورا", 540, 1570, 46, C["acc2"], True)
    for i, (txt, ic) in enumerate(LCARDS):
        t0 = 8.4 + 2.2 * i
        p = ease(seg(t, t0, t0 + 0.6))
        if p <= 0:
            continue
        y = 740 + i * 250
        dx = (1 - p) * 700
        st.rr(70 + dx, y, 1010 + dx, y + 200, 42, fill=(31, 46, 38, int(255 * p)), outline=rgb("#34463B", int(255 * p)), width=4)
        st.circ(930 + dx, y + 100, 56, fill="#E6784F")
        st.text(str(i + 1), 930 + dx, y + 96, 70, "#18251E", True)
        st.text(txt, 860 + dx, y + 100, 50, C["cream"], True, anchor="rm")
        icon_on(st, ic, 170 + dx, y + 100, 150, 120, p)
    return st, [], None


LB_EVENTS = [(0.5, sfx_whoosh(0.6), 0.35), (1.3, sfx_thud(), 0.3), (2.5, sfx_pop(700), 0.3), (3.6, sfx_pop(560), 0.3),
             (7.0, sfx_whoosh(0.5, True), 0.35), (8.4, sfx_pop(700), 0.4), (10.6, sfx_pop(800), 0.4), (12.8, sfx_pop(900), 0.4),
             (15.2, sfx_ding(1568), 0.3)]
LB_HEADS = [(0.0, "قريت التيكت (الليبل) قبل كده؟"), (3.0, "فيه معلومات مهمة جوه التيشيرت"), (7.2, "٣ حاجات بتقولهالك")]
label_frame = make_frame(label_stage, LB_HEADS, "حكاية خامة", LB_TOTAL,
                         (15.4, "اقلب تيشيرتك دلوقتي", "وقولنا مكتوب عليه إيه"))

# ===== 2) المقاس المظبوط (كوميدي) =====
FT_TOTAL = 20.0


def fit_stage(t):
    st = Stage()
    bubs = []
    CX, FY = 540, 1520
    p = back(seg(t, 0.4, 1.1))
    yy = FY - (1 - clamp(p)) * 800
    sc = 1.0
    if t < 9.0:
        sc = 1.45
        face = "shock" if t > 2.0 else "happy"
        wob = 0.03 * math.sin(t * 3)
        mascot(st, CX, yy, sc, sx=1 + wob, face=face)
    else:
        k = eio(seg(t, 9.0, 10.0))
        sc = 1.45 - 0.45 * k
        mascot(st, CX, yy, sc, face="proud" if t > 10 else "shock")
        if t >= 10.2:
            for i in range(5):
                a = (t * 2 + i) % 3 / 3
                sparkle(st, CX - 220 + i * 110 + 20 * math.sin(t + i), yy - 400 + 40 * math.cos(i * 2), 12 * (1 - a), int(255 * (1 - a)))
    if 2.0 <= t < 6.0:
        bubs.append(("أنا واسع عليه أوي!", 540, 800, seg(t, 2.0, 2.4), (0, 120)))
    if 10.4 <= t < 14.6:
        bubs.append(("كده أنا مظبوط!", 540, yy - 480, seg(t, 10.4, 10.8), (0, 140)))
    return st, bubs, None


FT_EVENTS = [(0.4, sfx_whoosh(0.6), 0.3), (1.1, sfx_thud(), 0.4), (2.0, sfx_pop(500), 0.3), (4.0, sfx_slide(0.8, 500, 220), 0.25),
             (9.0, sfx_whoosh(0.5, True), 0.3), (9.9, sfx_boing(), 0.3), (10.4, sfx_ding(), 0.4), (14.8, sfx_whoosh(0.4, True), 0.2)]
FT_HEADS = [(0.0, "واسع ولا مظبوط؟"), (4.0, "الأوسع مش دايمًا أريح"), (9.4, "الكتف يقع على طرف كتفك"),
            (12.4, "والصدر مرتاح من غير ما يتشد")]
fit_frame = make_frame(fit_stage, FT_HEADS, "هزار في هزار", FT_TOTAL,
                       (14.8, "مقاسك مظبوط ولا واسع؟", "قولنا في التعليقات"))

R.REELS.update({"label": (label_frame, LB_TOTAL, LB_EVENTS, None, 31), "fit": (fit_frame, FT_TOTAL, FT_EVENTS, None, 32)})
if __name__ == "__main__":
    if sys.argv[1] == "frames":
        fn = R.REELS[sys.argv[2]][0]
        ims = [fn(float(x)).resize((360, 640)) for x in sys.argv[4:]]
        sh = Image.new("RGB", (360 * len(ims), 640))
        [sh.paste(im, (360 * i, 0)) for i, im in enumerate(ims)]
        sh.save(sys.argv[3])
    else:
        fr, total, ev, hum, seed = R.REELS[sys.argv[1]]
        render_generic(sys.argv[2], fr, total, ev, hum, seed)
