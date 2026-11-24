# -*- coding: utf-8 -*-
"""ريلز موشن جرافيك (دفعة 2): hanger (كوميدي) | measure (شرح) | smell (كوميدي خفيف)
python3 tools/mg_reels2.py <name> out.mp4  |  frames <name> sheet.jpg t1 t2 ..."""
import math, os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mg_reels import *  # noqa
import mg_reels as R

# ============ 1) تعليق ولا طي (كوميدي) ============
HG_TOTAL = 20.0


def hanger_draw(st, cx, y):
    st.line([(cx - 8, y - 70), (cx - 8, y - 40), (cx + 18, y - 28)], "#B9B09A", 9)
    st.circ(cx - 8, y - 82, 14, outline="#B9B09A", width=8)
    st.line([(cx, y - 28), (cx - 230, y + 40), (cx + 230, y + 40), (cx, y - 28)], "#B9B09A", 9)


def hanger_stage(t):
    st = Stage()
    bubs = []
    CX, FY = 540, 1500
    drop = back(seg(t, 0.4, 1.2))
    if t < 9.2:
        yy = FY - (1 - clamp(drop)) * 800
        mascot(st, CX, yy, 1.05, face="happy" if t < 3.6 else "pain", sweat=t * 2 if 5.0 < t < 9 else 0)
        hanger_draw(st, CX, yy - 360)
        if 4.6 <= t < 9.2:                      # الكتف بيتمط: نتوءات
            k = seg(t, 4.6, 7.0)
            for s in (-1, 1):
                st.circ(CX + s * 205, yy - 330 + 18 * k, 14 + 22 * k, fill="#EFE6CC", outline="#CDBF9C", width=4)
        if 1.8 <= t < 4.4:
            bubs.append(("أنا معلّق من أسبوع!", 540, yy - 480, seg(t, 1.8, 2.2), (0, 150)))
        if 5.2 <= t < 9.0:
            bubs.append(("آه! كتفي بيتمط!", 540, yy - 480, seg(t, 5.2, 5.6), (0, 150)))
    else:
        k = back(seg(t, 9.2, 10.0))
        st.rr(120, 1190, 960, 1700, 40, fill="#22342A", outline="#3C5446", width=6)
        st.rr(150, 1560, 930, 1670, 24, fill="#EFE6CC", outline="#CDBF9C", width=5)
        st.rr(165, 1445, 915, 1555, 24, fill="#E5DCBD", outline="#CDBF9C", width=5)
        mascot(st, CX, 1440 - (1 - clamp(k)) * 500, 0.55, sy=0.8, face="proud")
        if t >= 10.4:
            for i in range(4):
                a = (t * 2 + i) % 3 / 3
                sparkle(st, 300 + i * 150, 1290 + 30 * math.sin(i * 2 + t), 12 * (1 - a), int(255 * (1 - a)))
        if 10.4 <= t < 14.6:
            bubs.append(("كده أنا مرتاح!", 540, 1280, seg(t, 10.4, 10.8), (0, 100)))
    return st, bubs, None


HG_EVENTS = [(0.4, sfx_whoosh(0.6), 0.3), (1.2, sfx_thud(), 0.35), (1.8, sfx_pop(600), 0.3), (4.6, sfx_slide(1.2, 500, 180), 0.3),
             (5.2, sfx_pop(420), 0.3), (7.0, sfx_boing(), 0.25), (9.2, sfx_whoosh(0.5, True), 0.3), (10.0, sfx_thud(), 0.3),
             (10.4, sfx_ding(), 0.35), (14.8, sfx_whoosh(0.4, True), 0.2)]
HG_HEADS = [(0.0, "تعلّق ولا تطوي؟"), (4.6, "التعليق الطويل ممكن يمط الكتف"), (9.4, "الطي أحسن للتيشيرتات التقيلة"),
            (12.4, "والتعليق مناسب للقطع الخفيفة")]
hanger_frame = make_frame(hanger_stage, HG_HEADS, "هزار في هزار", HG_TOTAL,
                          (14.8, "بتعلّق ولا بتطوي؟", "قولنا في التعليقات"))

# ============ 2) إزاي تقيس مقاسك (شرح) ============
MS_TOTAL = 21.0
MCARDS = [("افرده على سطح مستوي", "fold"), ("قيس العرض تحت الإبط", "tape"),
          ("اكتب الرقم في موبايلك", "tag")]


def measure_stage(t):
    st = Stage()
    lift = eio(seg(t, 7.5, 8.5))
    if lift < 1:
        sl = back(seg(t, 0.5, 1.4))
        yoff = -1000 * lift - (1 - sl) * 800
        shirt_plain(st, 540, 1300, 1.25, False, 0, yoff)
        k = eio(seg(t, 3.0, 5.0))
        if k > 0:
            y = 1300 + yoff + 40
            x0, x1 = 540 - 190 * k, 540 + 190 * k
            st.line([(x0, y), (x1, y)], "#E6784F", 10)
            st.poly([(x0, y), (x0 + 36, y - 22), (x0 + 36, y + 22)], "#E6784F")
            st.poly([(x1, y), (x1 - 36, y - 22), (x1 - 36, y + 22)], "#E6784F")
            if k > 0.95:
                st.text("؟؟ سم", 540, y - 70, 64, "#F2B36B", True)
    for i, (txt, ic) in enumerate(MCARDS):
        t0 = 8.6 + 2.2 * i
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


MS_EVENTS = [(0.5, sfx_whoosh(0.6), 0.35), (1.3, sfx_thud(), 0.3), (3.0, sfx_slide(1.5, 400, 800), 0.25), (5.0, sfx_ding(1175), 0.3),
             (7.5, sfx_whoosh(0.5, True), 0.35), (8.6, sfx_pop(700), 0.4), (10.8, sfx_pop(800), 0.4), (13.0, sfx_pop(900), 0.4),
             (15.4, sfx_ding(1568), 0.3)]
MS_HEADS = [(0.0, "عارف مقاسك الحقيقي؟"), (3.0, "قيس العرض بنفسك بدل ما تخمّن"), (7.7, "٣ خطوات بس")]
measure_frame = make_frame(measure_stage, MS_HEADS, "جرّب في 30 ثانية", MS_TOTAL,
                           (15.6, "جرّب دلوقتي", "وقولنا مقاسك الحقيقي"))

# ============ 3) ريحة التيشيرت (كوميدي خفيف) ============
SM_TOTAL = 20.0


def smell_stage(t):
    st = Stage()
    bubs = []
    CX, FY = 540, 1500
    p = back(seg(t, 0.4, 1.1))
    yy = FY - (1 - clamp(p)) * 800
    wet = 1 - eio(seg(t, 6.5, 11.5))
    tint = "#B7C79B" if wet > 0.5 else None
    face = "pain" if t < 11.0 else "happy"
    mascot(st, CX, yy, 1.05, face=face, tint=tint, sweat=t * 2 if 1.5 < t < 6.5 else 0)
    if t < 11.5:
        for i in range(3):
            x0 = CX - 150 + i * 150
            pts = [(x0 + 22 * math.sin(t * 3 + i + j * 0.9), yy - 400 - j * 34) for j in range(7)]
            st.line(pts, (150, 190, 110, int(210 * wet)), 9)
    if 6.5 <= t < 11.5:
        sun = seg(t, 6.5, 7.5)
        st.circ(880, 1000 - (1 - sun) * 300, 90, fill="#F2B36B")
        for i in range(8):
            a = i * math.pi / 4 + t
            st.line([(880 + 120 * math.cos(a), 1000 + 120 * math.sin(a)), (880 + 160 * math.cos(a), 1000 + 160 * math.sin(a))], "#F2B36B", 10)
        for i in range(5):
            ph = (t * 0.9 + i * 0.21) % 1
            st.circ(CX - 180 + i * 90, yy - 340 + ph * 330, 11, fill=(120, 190, 240, int(220 * (1 - ph) * wet)))
    if 1.6 <= t < 6.0:
        bubs.append(("فيه ريحة غريبة!", 540, yy - 500, seg(t, 1.6, 2.0), (0, 150)))
    if 11.8 <= t < 15.5:
        bubs.append(("دلوقتي ريحتي حلوة!", 540, yy - 500, seg(t, 11.8, 12.2), (0, 150)))
    if t >= 11.8:
        for i in range(5):
            a = (t * 2 + i) % 3 / 3
            sparkle(st, CX - 220 + i * 110 + 20 * math.sin(t + i), yy - 380 + 40 * math.cos(i * 2), 12 * (1 - a), int(255 * (1 - a)))
    return st, bubs, None


SM_EVENTS = [(0.4, sfx_whoosh(0.6), 0.3), (1.1, sfx_thud(), 0.35), (1.6, sfx_pop(500), 0.3), (3.5, sfx_slide(0.8, 500, 200), 0.2),
             (6.5, sfx_whoosh(0.6), 0.3), (8.0, sfx_pop(700), 0.15), (9.5, sfx_pop(760), 0.15), (11.5, sfx_ding(1568), 0.4),
             (11.8, sfx_pop(900), 0.3), (15.0, sfx_whoosh(0.4, True), 0.2)]
SM_HEADS = [(0.0, "التيشيرت طلع بريحة غريبة؟"), (4.0, "غالبًا السبب الرطوبة"), (6.6, "انشره ناشف تمامًا"),
            (11.8, "وبعدين خزّنه في دولاب مهوّى")]
smell_frame = make_frame(smell_stage, SM_HEADS, "هزار في هزار", SM_TOTAL,
                         (15.0, "عندك حيلة للريحة؟", "قولنا في التعليقات"))

R.REELS.update({
    "hanger": (hanger_frame, HG_TOTAL, HG_EVENTS, None, 21),
    "measure": (measure_frame, MS_TOTAL, MS_EVENTS, None, 22),
    "smell": (smell_frame, SM_TOTAL, SM_EVENTS, None, 23),
})

if __name__ == "__main__":
    if sys.argv[1] == "frames":
        fn = R.REELS[sys.argv[2]][0]
        ts = [float(x) for x in sys.argv[4:]]
        ims = [fn(t).resize((360, 640)) for t in ts]
        sheet = Image.new("RGB", (360 * len(ims), 640))
        for i, im in enumerate(ims):
            sheet.paste(im, (360 * i, 0))
        sheet.save(sys.argv[3])
    else:
        fr, total, ev, hum, seed = R.REELS[sys.argv[1]]
        render_generic(sys.argv[2], fr, total, ev, hum, seed)
