# -*- coding: utf-8 -*-
"""يضيف موسيقى هادية مولّدة بالكود لكل فيديو في videos/ (بدل الصامت).  python3 tools/add_music.py [names]"""
import glob, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_music as mm

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
files = sorted(glob.glob(os.path.join(ROOT, "videos", "*.mp4")))
names = [a for a in sys.argv[1:] if not a.startswith("--")]
if names:
    files = [f for f in files if os.path.basename(f)[:-4] in names]
for i, f in enumerate(files):
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                         "-of", "csv=p=0", f]).decode().strip())
    has_audio = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
                                         "stream=codec_type", "-of", "csv=p=0", f]).decode().strip()
    if has_audio and "--force" not in sys.argv:
        print("skip (has audio)", f)
        continue
    with tempfile.TemporaryDirectory() as td:
        wav, out = os.path.join(td, "m.wav"), os.path.join(td, "o.mp4")
        mm.write(wav, mm.make(dur, seed=i))
        subprocess.check_call(["ffmpeg", "-loglevel", "error", "-y", "-i", f, "-i", wav, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
                               "-c:a", "aac", "-b:a", "160k", "-af", "volume=0.7", "-shortest",
                               "-movflags", "+faststart", out])
        os.replace(out, f)
    print("music added", os.path.basename(f), "%.1fs" % dur)
