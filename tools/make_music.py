# -*- coding: utf-8 -*-
"""يولّد موسيقى هادية أصلية بالكود (تركيب صوتي): إلكتريك بيانو دافي + باد ناعم + لحن خفيف متباعد + ريفرب ستيريو.
من غير ذكاء اصطناعي توليدي ولا مقاطع جاهزة. الاستخدام: python3 tools/make_music.py <seconds> <out.wav> [seed]"""
import sys
import wave
import numpy as np

SR = 44100
ROOTS = [130.81, 110.00, 98.00, 116.54, 123.47, 146.83]  # C3, A2, G2, Bb2, B2, D3
PROGS = [
    [(0, [0, 7, 11, 14, 16]), (-3, [0, 7, 10, 14, 15]), (-7, [0, 7, 11, 14, 16]), (-5, [0, 7, 9, 14, 16])],
    [(0, [0, 7, 11, 14, 16]), (-7, [0, 7, 11, 14, 16]), (-3, [0, 7, 10, 14, 15]), (-5, [0, 7, 9, 14, 16])],
    [(-3, [0, 7, 10, 14, 15]), (-7, [0, 7, 11, 14, 16]), (0, [0, 7, 11, 14, 16]), (-5, [0, 7, 9, 14, 16])],
]
PENT = [0, 2, 4, 7, 9, 12, 14, 16]  # بنتاتونك ميجر


def hz(root, semi):
    return root * 2 ** (semi / 12.0)


def epiano(freq, dur, vel, rng):
    t = np.arange(int(SR * dur)) / SR
    atk = 1 - np.exp(-t * 220)
    body = np.exp(-t * 1.25)
    s = np.sin(2 * np.pi * freq * t) * body
    s += 0.30 * np.sin(2 * np.pi * freq * 2.0 * t) * np.exp(-t * 2.4)
    s += 0.10 * np.sin(2 * np.pi * freq * 3.0 * t) * np.exp(-t * 4.0)
    s += 0.16 * np.sin(2 * np.pi * freq * 7.0 * t) * np.exp(-t * 14)  # لمعة المطرقة
    trem = 1 + 0.07 * np.sin(2 * np.pi * (4.2 + rng.random() * 0.6) * t)
    return s * atk * trem * vel


def pad(freqs, dur, vel):
    t = np.arange(int(SR * dur)) / SR
    env = np.minimum(1, t / 1.6) * np.minimum(1, (dur - t) / 1.6)
    out = np.zeros_like(t)
    for f in freqs:
        for d in (-0.5, 0.0, 0.5):
            out += np.sin(2 * np.pi * (f + d) * t + d)
    return out / (len(freqs) * 3) * env * vel


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    try:
        from scipy.signal import lfilter
        return lfilter([1 - a], [1, -a], x)
    except Exception:
        k = int(SR / cutoff / 2) | 1
        return np.convolve(x, np.ones(k) / k, mode="same")


def reverb(x, rng, length=2.8, mix=0.34):
    n = int(SR * length)
    ir = rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 1.9)
    ir[:int(0.02 * SR)] *= 0.2
    nfft = 1 << int(np.ceil(np.log2(len(x) + n)))
    y = np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(ir, nfft), nfft)[:len(x)]
    y = lowpass(y, 2600)
    y *= np.max(np.abs(x)) / (np.max(np.abs(y)) + 1e-9)
    return x * (1 - mix) + y * mix


def put(buf, s, t, pan=0.0):
    i = max(0, int(t * SR))
    m = min(len(s), buf.shape[1] - i)
    if m <= 0:
        return
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[0, i:i + m] += s[:m] * l
    buf[1, i:i + m] += s[:m] * r


def make(seconds, seed=0):
    rng = np.random.default_rng(seed)
    root = ROOTS[seed % len(ROOTS)]
    prog = PROGS[seed % len(PROGS)]
    bpm = 56 + (seed % 3) * 3
    beat = 60.0 / bpm
    bar = beat * 4
    n = int(SR * (seconds + 4))
    buf = np.zeros((2, n))
    t0, bi = 0.0, 0
    motif = [int(x) for x in rng.choice(len(PENT), 3, replace=False)]
    while t0 < seconds + 1:
        off, voic = prog[bi % len(prog)]
        base = root * 2 ** (off / 12.0)
        # باد
        p = pad([hz(base, voic[0]), hz(base, voic[1]), hz(base, voic[2])], bar + 1.4, 0.10)
        put(buf, p, t0 - 0.2)
        # باص دافي
        put(buf, epiano(hz(base, -12), 3.2, 0.34, rng), t0, 0.0)
        # كورد مفرود (ستروم بطيء)
        for k, semi in enumerate(voic):
            f = hz(base, semi + 12)
            put(buf, epiano(f, 4.2, 0.20 + 0.03 * rng.random(), rng), t0 + 0.05 + k * 0.11 + rng.normal(0, 0.006),
                pan=-0.45 + 0.22 * k)
        # كورد خفيف تاني في نص الميزان
        if bi % 2 == 1:
            for k, semi in enumerate(voic[1:4]):
                put(buf, epiano(hz(base, semi + 12), 2.6, 0.12, rng), t0 + 2 * beat + k * 0.09, pan=0.3 - 0.3 * k)
        # لحن متباعد: نغمتين أو تلاتة في الميزان
        if bi >= 1:
            slots = sorted(rng.choice([1.0, 1.5, 2.5, 3.0, 3.5], size=2 + (bi % 2), replace=False))
            for j, sl in enumerate(slots):
                semi = PENT[motif[(bi + j) % 3]] + 12
                put(buf, epiano(hz(base * (1 if off == 0 else 2 ** (-off / 12.0)), semi + 12), 3.0,
                                0.26 + 0.05 * rng.random(), rng), t0 + sl * beat + rng.normal(0, 0.008),
                    pan=0.15 + 0.4 * rng.random())
        t0 += bar
        bi += 1
    out = np.stack([lowpass(buf[0], 4200), lowpass(buf[1], 4200)])
    out = np.stack([reverb(out[0], rng), reverb(out[1], np.random.default_rng(seed + 99))])
    out = out[:, :int(SR * seconds)]
    fi, fo = int(SR * 1.2), int(SR * 2.5)
    out[:, :fi] *= np.linspace(0, 1, fi)
    out[:, -fo:] *= np.linspace(1, 0, fo)
    out = out / (np.max(np.abs(out)) + 1e-9) * 0.6
    return out


def write(path, x):
    if x.ndim == 1:
        x = np.stack([x, x])
    pcm = (np.clip(x.T, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    secs = float(sys.argv[1])
    out = sys.argv[2]
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    write(out, make(secs, seed))
    print("wrote", out)
