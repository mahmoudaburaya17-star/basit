# -*- coding: utf-8 -*-
"""يفحص ملف سلسلة: python3 tools/validate_series.py content/series_X.py"""
import importlib.util
import re
import sys

LIM = {
    "statement": {"kicker": 14, "title": 40, "sub": 90},
    "list": {"kicker": 14, "title": 45},
    "compare": {"kicker": 14, "title": 45},
    "poll": {"kicker": 14, "title": 55},
    "qa": {"kicker": 14, "title": 45, "q": 75, "a": 170},
    "bignum": {"kicker": 14, "title": 40, "note": 40},
    "swatch": {"kicker": 14, "title": 45, "sub": 40},
    "fits": {"kicker": 14, "title": 45, "sub": 40},
}
BAD = ["جربنا", "اختبرنا", "مصنعنا", "عملاءنا", "عملائنا", "#", "اشتري دلوقتي", "اطلب", "خصم", "عرض خاص",
       "ديفاكتو", "زارا", "مانجو", "LC", "ماكس", "قطونيل", "كولينز", "نايلتون", "H&M"]


def main(path):
    spec = importlib.util.spec_from_file_location("s", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    posts = m.POSTS
    errs, warns = [], []
    days = []
    texts = set()
    mains = path.endswith("series_main.py")
    for i, p in enumerate(posts):
        tag = "#%d" % (i + 1)
        if not mains:
            d = p.get("day")
            if not isinstance(d, int) or not 1 <= d <= 91:
                errs.append("%s: day غلط" % tag)
            days.append(d)
        else:
            if p.get("phase") not in (1, 2, 3):
                errs.append("%s: phase غلط" % tag)
        t = p.get("text", "").strip()
        wc = len(t.split())
        if wc < 8 or wc > 110:
            warns.append("%s: عدد الكلمات %d" % (tag, wc))
        if t in texts:
            errs.append("%s: نص مكرر" % tag)
        texts.add(t)
        for b in BAD:
            if b in t:
                errs.append("%s: كلمة ممنوعة '%s'" % (tag, b))
        emo = len(re.findall(r"[\U0001F300-\U0001FAFF☀-➿]", t))
        if emo > 2:
            warns.append("%s: إيموجي %d" % (tag, emo))
        img = p.get("image")
        if img:
            k = img.get("t")
            if k not in LIM and k != "ladder":
                errs.append("%s: قالب غلط %s" % (tag, k))
                continue
            for f, lim in LIM.get(k, {}).items():
                v = img.get(f)
                if v is None:
                    if f not in ("kicker", "sub", "note"):
                        errs.append("%s: ناقص %s" % (tag, f))
                elif len(v) > lim:
                    errs.append("%s: %s طويل (%d>%d)" % (tag, f, len(v), lim))
            if k == "list":
                its = img.get("items", [])
                if not 3 <= len(its) <= 5:
                    errs.append("%s: items لازم 3-5" % tag)
                for x in its:
                    if len(x) > 55:
                        errs.append("%s: عنصر طويل '%s'" % (tag, x[:20]))
            if k == "poll":
                o = img.get("options", [])
                if not 2 <= len(o) <= 5:
                    errs.append("%s: options لازم 2-5" % tag)
                for x in o:
                    if len(x) > 38:
                        errs.append("%s: خيار طويل '%s'" % (tag, x[:20]))
            if k == "compare":
                for side in ("left", "right"):
                    h, its = img.get(side, ["", []])
                    if len(h) > 16 or not 3 <= len(its) <= 4 or any(len(x) > 28 for x in its):
                        errs.append("%s: compare %s حدود" % (tag, side))
            if k == "bignum":
                ls = img.get("lines", [])
                if len(ls) != 2 or any(len(a) > 12 or len(b) > 45 for a, b in ls):
                    errs.append("%s: bignum lines" % tag)
            if k == "swatch" and len(img.get("colors", [])) != 6:
                errs.append("%s: swatch لازم 6 ألوان" % tag)
    if not mains:
        missing = sorted(set(range(1, 92)) - set(days))
        dup = sorted({d for d in days if days.count(d) > 1})
        if missing:
            errs.append("أيام ناقصة: %s" % missing)
        if dup:
            errs.append("أيام مكررة: %s" % dup)
    print("posts:", len(posts), "| with image:", sum(1 for p in posts if p.get("image")))
    for w in warns:
        print("تحذير:", w)
    for e in errs:
        print("خطأ:", e)
    print("OK" if not errs else "فيه %d أخطاء" % len(errs))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
