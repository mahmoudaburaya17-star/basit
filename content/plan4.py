# -*- coding: utf-8 -*-
"""خطة 4 منشورات يوميًا (من 28 أكتوبر): نصيحة الصبح + منشور الظهر (بيتبدّل: سؤال / ستايل / اختبار) + ريل بموسيقى + موضوع رئيسي بالليل.
بيقرا content/calendar.json (المحتوى الأصلي) وبيكتب content/calendar4.json (الجدول الفعلي)."""
import json, os, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
src = json.load(open(os.path.join(HERE, "calendar.json"), encoding="utf-8"))
by = {(p["date"], p["slot"]): p for p in src}
TIMES = {"A": "09:00", "M": "13:00", "R": "19:30", "E": "21:30"}
FRI = {"A": "10:00", "M": "14:30", "R": "19:30", "E": "21:30"}
CYCLE = ["B", "D", "F"]  # سؤال، ستايل، اختبار/خفيف
start, end = datetime.date(2026, 10, 28), datetime.date(2026, 11, 7)
out, used = [], set()
d, k = start, 0
while d <= end:
    ds = d.isoformat()
    times = FRI if d.weekday() == 4 else TIMES
    mid = by[(ds, CYCLE[k % 3])]
    k += 1
    for slot, p in (("A", by[(ds, "A")]), ("M", mid), ("R", by[(ds, "R")]), ("E", by[(ds, "E")])):
        q = dict(p)
        q["slot"], q["time"] = slot, times[slot]
        out.append(q)
        used.add((ds, p["slot"]))
    d += datetime.timedelta(days=1)
reserve = [p for p in src if (p["date"], p["slot"]) not in used and p["date"] >= start.isoformat() and p["slot"] != "R"]
json.dump({"posts": out, "reserve": reserve}, open(os.path.join(HERE, "calendar4.json"), "w"), ensure_ascii=False, indent=1)
print(len(out), "scheduled;", len(reserve), "reserve")
