# -*- coding: utf-8 -*-
"""يبني ملفات نوفمبر (صور الكروت والكاروسيل والريلز) ويكتب content/calendar_nov.json.
python3 tools/build_nov.py cards   |  reels [dates...]"""
import json, os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "content"))
import v2engine as e
import nov_v2 as N

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "nov")
os.makedirs(OUT, exist_ok=True)
HASH = "#بسيط #تيشيرت_رجالي #ملابس_رجالي"
TIMES = dict(A="09:00", M="13:00", R="19:30", E="21:30")
FRI = dict(A="10:00", M="14:30", R="19:30", E="21:30")
import datetime
from PIL import Image


def dd(date):
    return datetime.date.fromisoformat(date)


def build_cards():
    cal = []
    for i, d in enumerate(N.DAYS):
        date = d["date"]
        times = FRI if dd(date).weekday() == 4 else TIMES
        # نصيحة
        p = os.path.join(OUT, date + "-A.jpg")
        e.tip_card(d["tip"]).save(p, quality=90, optimize=True)
        cal.append(dict(date=date, time=times["A"], slot="A", kind="image", images=["nov/%s-A.jpg" % date],
                        text=d["tip"]["cap"] + "\n\n" + HASH, alt=d["tip"]["tip"]))
        # منشور الظهر
        m = d["mid"]
        p = os.path.join(OUT, date + "-M.jpg")
        fn = dict(poll=e.poll_card, myth=e.myth_card, stat=e.stat_card)[m["kind"]]
        fn(m).save(p, quality=90, optimize=True)
        text = m["cap"] + "\n\n" + HASH
        if m.get("answer"):
            # الإجابة جوه الكابشن بعد سطور فاضية (Buffer المجاني مش بيدعم أول تعليق)
            text = ("صح ولا غلط؟ جاوب في التعليقات الأول. 👇\n\nالإجابة تحت بعد ما تجاوب\n.\n.\n.\n.\n.\n.\n"
                    + m["answer"] + "\n\n" + HASH)
        item = dict(date=date, time=times["M"], slot="M", kind="image", images=["nov/%s-M.jpg" % date],
                    text=text, alt=m.get("question") or m.get("statement") or m.get("caption"))
        cal.append(item)
        # كاروسيل
        c = d["car"]
        imgs = []
        if c.get("prebuilt"):
            src = os.path.join(ROOT, c["prebuilt"])
            for k in range(1, 8):
                imgs.append("nov/%s-E-%02d.jpg" % (date, k))
                Image.open(os.path.join(src, "%02d.png" % k)).convert("RGB").save(os.path.join(ROOT, imgs[-1]), quality=90, optimize=True)
        else:
            for k, im in enumerate(e.carousel(c), 1):
                rel = "nov/%s-E-%02d.jpg" % (date, k)
                im.save(os.path.join(ROOT, rel), quality=90, optimize=True)
                imgs.append(rel)
        cal.append(dict(date=date, time=times["E"], slot="E", kind="image", images=imgs,
                        text=c["cap"] + "\n\n" + HASH, alt=c.get("title", "كاروسيل بسيط")))
        # ريل (الملف بيتبني في reels)
        r = d["reel"]
        cal.append(dict(date=date, time=times["R"], slot="R", kind="reel", video="nov/%s-R.mp4" % date,
                        text=r["cap"] + "\n\n" + HASH))
    cal.sort(key=lambda x: (x["date"], x["time"]))
    json.dump(cal, open(os.path.join(ROOT, "content", "calendar_nov.json"), "w"), ensure_ascii=False, indent=1)
    print("cards done", len(cal))


def build_reels(dates):
    for i, d in enumerate(N.DAYS):
        if dates and d["date"] not in dates:
            continue
        out = os.path.join(OUT, d["date"] + "-R.mp4")
        r = d["reel"]
        if r.get("prebuilt"):
            shutil.copy(os.path.join(ROOT, r["prebuilt"]), out)
            print("copied", out)
            continue
        dur = e.render_reel(r, out, seed=20 + i)
        print("reel", d["date"], "%.1fs" % dur, flush=True)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "cards":
        build_cards()
    else:
        build_reels(set(sys.argv[2:]))
