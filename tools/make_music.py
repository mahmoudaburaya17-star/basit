# -*- coding: utf-8 -*-
"""يولّد موسيقى هادية أصلية بالكود (تركيب صوتي، من غير ذكاء اصطناعي توليدي ولا مقاطع جاهزة).

بيانو ناعم بأربيجيو + باد هادي + ريفرب خفيف. كل فيديو بيطلع بتونالتي ومزاج مختلف شوية.
الاستخدام: python3 tools/make_music.py <seconds> <out.wav> [seed]
"""
import sys
import numpy as np
import wave

SR = 44100
# جذور (Hz) لتونالتيات هادية
ROOTS = [261.63, 220.00, 196.00, 233.08, 246.94, 293.66]
PROGS = [  # (درجات الجذر بالنصف تون، نوع الكورد)
    [(0, "maj7"), (9, "m7"), (5, "maj7"), (7, "6")],
    [(0, "maj7"), (5, "maj7"), (9, "m7"), (7, "6")],
    [(0, "6"), (7, "6"), (9, "m7"), (5, "maj7")],
]
CH = {"maj7": [0, 4, 7, 11], "m7": [0, 3, 7, 10], "6": [0, 4, 7, 9]}


def hz(root, semi):
    return root * 2 ** (semi / 12.0)


def pluck(freq, dur, vel=0.5):
    t = np.arange(int(SR * dur)) / SR
    env = np.exp(-t * 2.6) * (1 - np.exp(-t * 90))
    s = (np.sin(2 * np.pi * freq * t) + 0.28 * np.sin(2 * np.pi * freq * 2 * t) * np.exp(-t * 4)
         + 0.08 * np.sin(2 * np.pi * freq * 3 * t) * np.exp(-t * 6))
    return s * env * vel


def pad(freqs, dur, vel=0.12):
    t = np.arange(int(SR * dur)) / SR
    env = np.minimum(1, t / 1.2) * np.minimum(1, (dur - t) / 1.2)
    out = np.zeros_like(t)
    for f in freqs:
        for d in (-0.6, 0.0, 0.7):
            out += np.sin(2 * np.pi * (f + d * 0.3) * t) / 3
    return out / len(freqs) * env * vel


def reverb(x, rng, length=2.2, mix=0.28):
    n = int(SR * length)
    ir = rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 2.4)
    ir[0] = 0
    nfft = 1 << int(np.ceil(np.log2(len(x) + n)))
    y = np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(ir, nfft), nfft)[:len(x)]
    y *= np.max(np.abs(x)) / (np.max(np.abs(y)) + 1e-9)
    return x * (1 - mix) + y * mix


def add(out, s, t):
    i = max(0, int(t * SR))
    m = min(len(s), len(out) - i)
    if m > 0:
        out[i:i + m] += s[:m]


def make(seconds, seed=0):
    rng = np.random.default_rng(seed)
    root = ROOTS[seed % len(ROOTS)] / 2
    prog = PROGS[seed % len(PROGS)]
    bpm = 66 + (seed % 3) * 4
    beat = 60.0 / bpm
    bar = beat * 4
    n = int(SR * (seconds + 3))
    out = np.zeros(n)
    t0, bi = 0.0, 0
    while t0 < seconds + 1:
        semi, kind = prog[bi % len(prog)]
        notes = [hz(root * 2, semi + k) for k in CH[kind]]
        # باد
        p = pad([hz(root, semi + k) for k in CH[kind][:3]], bar + 0.8)
        add(out, p, t0)
        # أربيجيو بنمط بسيط بتتغير لمسته
        pattern = [0, 1, 2, 3, 2, 1, 2, 1] if bi % 2 == 0 else [0, 2, 1, 3, 1, 2, 3, 2]
        for k, idx in enumerate(pattern):
            if rng.random() < 0.12:
                continue
            tt = t0 + k * beat / 2 + rng.normal(0, 0.006)
            f = notes[idx] * (2 if k == 7 and bi % 4 == 3 else 1)
            s = pluck(f, 2.4, 0.36 + 0.1 * rng.random())
            add(out, s, tt)
        # نغمة باص طويلة وهادية
        add(out, pluck(hz(root, semi), 3.6, 0.28), t0)
        t0 += bar
        bi += 1
    out = reverb(out, rng)
    out = out[:int(SR * seconds)]
    fade = int(SR * 1.5)
    out[:fade] *= np.linspace(0, 1, fade)
    out[-int(SR * 2.5):] *= np.linspace(1, 0, int(SR * 2.5))
    out = out / (np.max(np.abs(out)) + 1e-9) * 0.55
    return out


def write(path, x):
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    secs = float(sys.argv[1])
    out = sys.argv[2]
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    write(out, make(secs, seed))
    print("wrote", out)
