"""Trilha do Reels do 7 Wonders Arquitetos: lira + tambores "antigos" + efeitos de obra + voz (opcional)."""
import os
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "voodoo-reels"))
sys.path.insert(0, os.path.join(HERE, "..", "sintonia-reels"))
from audio import (SR, add, env, hp, lp, noise, t_, read_wav, doum, shaker,  # noqa: E402
                   fx_pop, fx_whoosh, fx_ding, fx_fanfare, fx_chime, fx_thud, fx_clack)
from trilha import note, fx_tick  # noqa: E402


def lira(f, d=1.4, decay=0.997):
    """Corda dedilhada (Karplus-Strong)."""
    n = int(d * SR)
    p = max(2, int(SR / f))
    rng = np.random.default_rng(int(f * 10))
    buf = list(lp(rng.uniform(-1, 1, p), 5000))
    out = np.zeros(n)
    for i in range(n):
        j = i % p
        v = buf[j]
        out[i] = v
        buf[j] = decay * 0.5 * (v + buf[(j + 1) % p])
    return lp(out, 4500)


_LIRA = {}


def lira_c(f):
    k = round(f, 2)
    if k not in _LIRA:
        _LIRA[k] = lira(f)
    return _LIRA[k]


def strings(freqs, dur):
    t = t_(dur)
    x = sum(2 * ((f * t + 0.3 * np.sin(2 * np.pi * 5 * t) / 100) % 1) - 1 + 2 * ((f * 1.004 * t) % 1) - 1
            for f in freqs) / (2 * len(freqs))
    e = np.minimum(1, t / 0.5) * np.minimum(1, (dur - t) / 0.5)
    return lp(lp(x, 1200), 1500) * e


def tom(f0=80):
    t = t_(0.6)
    f = f0 * (0.6 + 0.4 * np.exp(-t / 0.06))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(0.6, 0.25) + lp(noise(0.6), 400) * env(0.6, 0.02) * 0.4


def music(dur):
    out = np.zeros(int(dur * SR))
    beat = 60 / 100
    bar = beat * 4
    prog = [["D3", "F3", "A3"], ["C3", "E3", "G3"], ["Bb2", "D3", "F3"], ["C3", "E3", "G3"]]
    roots = ["D2", "C2", "Bb1", "C2"]
    arp = [0, 1, 2, 1, 0, 2, 1, 2]
    mel = [["A4", None, "D5", None, "C5", "A4", None, "G4"], ["E4", None, "G4", None, "A4", None, "G4", "E4"],
           ["F4", None, "D4", None, "F4", "G4", None, "A4"], ["G4", None, "E4", "G4", None, "C5", None, None]]
    t, b = 0.0, 0
    while t < dur - 1.5:
        intro = t < 2.4
        ch = [note(n) for n in prog[b % 4]]
        add(out, strings(ch, bar), t, 0.35)
        for k in range(8):
            f = ch[arp[k]] * 2
            add(out, lira_c(f), t + beat * k / 2, 0.30 if k % 2 == 0 else 0.22)
        if not intro:
            add(out, tom(70), t, 0.9)
            add(out, tom(70), t + beat * 1.5, 0.6)
            add(out, tom(70), t + beat * 2, 0.8)
            add(out, doum(160) * 0.6, t + beat * 3, 0.5)
            add(out, doum(160) * 0.6, t + beat * 3.5, 0.35)
            for k in range(8):
                add(out, shaker(), t + beat * k / 2, 0.25 if k % 2 else 0.15)
            r = note(roots[b % 4])
            for k in (0, 2, 2.5):
                add(out, lira_c(r * 2) * 0.9, t + beat * k, 0.45)
            if b % 2 == 1 or t > 44:
                for k, n in enumerate(mel[b % 4]):
                    if n:
                        add(out, lira_c(note(n) * 2), t + beat * k / 2, 0.20)
        t += bar
        b += 1
    add(out, tom(60) * 1.3, dur - 1.4, 1.0)
    add(out, strings([note("D3"), note("F3"), note("A3"), note("D4")], 1.4), dur - 1.4, 0.8)
    n = int(0.5 * SR)
    out[-n:] *= np.linspace(1, 0, n)
    return out


# ---------------------------------------------------------------- efeitos
def fx_card():
    t = t_(0.12)
    return lp(hp(noise(0.12), 1500), 6000) * env(0.12, 0.025, 0.004) * 0.9


def fx_paper():
    d = 0.5
    t = t_(d)
    e = np.sin(np.pi * t / d) ** 1.5
    return lp(hp(noise(d), 900), 5000) * e * (0.6 + 0.4 * np.sin(2 * np.pi * 23 * t))


def fx_draw():
    d = 1.0
    t = t_(d)
    return hp(lp(noise(d), 3500), 1200) * (0.4 + 0.3 * np.abs(np.sin(2 * np.pi * 3 * t))) * np.sin(np.pi * t / d)


def fx_stamp():
    out = np.zeros(int(0.6 * SR))
    add(out, fx_thud(), 0, 0.9)
    add(out, fx_clack(), 0, 0.6)
    return out


def fx_build():
    """Tum! de pedra assentando + poeirinha."""
    out = np.zeros(int(1.4 * SR))
    add(out, tom(55) * 1.4, 0, 1.0)
    add(out, lp(noise(0.9), 900) * env(0.9, 0.3, 0.02), 0.05, 0.5)
    add(out, fx_clack(), 0.0, 0.5)
    add(out, fx_ding(), 0.25, 0.25)
    return out


def fx_horn():
    d = 0.9
    t = t_(d)
    f = 233 * (1 + 0.012 * np.sin(2 * np.pi * 5.5 * t)) * (0.94 + 0.06 * np.minimum(1, t / 0.12))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = sum(np.sin(k * ph) / k ** 0.8 for k in range(1, 9))
    e = np.minimum(1, t / 0.08) * np.minimum(1, (d - t) / 0.25)
    return lp(x, 2500) * e * 0.5


def fx_clash():
    t = t_(1.2)
    x = sum(np.sin(2 * np.pi * f * t) * np.exp(-t / dd) for f, dd in ((1240, 0.5), (1873, 0.35), (2650, 0.25),
                                                                          (3410, 0.2)))
    out = x * 0.4 + hp(noise(1.2), 2500) * env(1.2, 0.08) * 0.8
    o = np.zeros(int(1.5 * SR))
    add(o, out, 0, 1.0)
    add(o, tom(60), 0, 0.9)
    return o


def fx_coin():
    t = t_(0.6)
    return (np.sin(2 * np.pi * 1975 * t) + 0.6 * np.sin(2 * np.pi * 2637 * t)) * env(0.6, 0.15)


def fx_meow():
    d = 0.5
    t = t_(d)
    f = 600 + 350 * np.sin(np.pi * t / d) - 150 * t / d
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = sum(np.sin(k * ph) * (0.7 ** k) for k in range(1, 6))
    return lp(x, 3000) * np.sin(np.pi * t / d) ** 0.8 * 0.6


def fx_tickfast():
    out = np.zeros(int(2.2 * SR))
    for k in range(20):
        add(out, fx_tick(), k * 0.1, 0.5)
    return out


FX = {"pop": fx_pop, "whoosh": fx_whoosh, "ding": fx_ding, "fanfare": fx_fanfare, "chime": fx_chime,
      "card": fx_card, "paper": fx_paper, "draw": fx_draw, "stamp": fx_stamp, "build": fx_build, "horn": fx_horn,
      "clash": fx_clash, "coin": fx_coin, "meow": fx_meow, "tick": fx_tickfast}


def build(path, dur, warp=None, voz=None, cues=()):
    warp = warp or (lambda t: t)
    m = music(dur)
    m = m / (np.abs(m).max() + 1e-9) * 0.30
    s = np.zeros_like(m)
    for t, name, g in cues:
        add(s, FX[name](), warp(t), g)
    bed = m + s * 0.55
    bed = np.tanh(bed * 1.2) / np.tanh(1.2) * 0.62
    if voz:
        v = np.zeros_like(bed)
        for arq, t0 in voz:
            add(v, read_wav(arq), t0, 1.0)
        act = lp(np.abs(v), 8)
        act = np.clip(act / (act.max() * 0.15 + 1e-9), 0, 1)
        duck = 1 - 0.62 * lp(lp(act, 3), 3)
        mix = bed * duck + v * 0.95
    else:
        mix = bed
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.71
    st = np.repeat((mix * 32767).astype(np.int16)[:, None], 2, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(st.tobytes())
    print("ok:", path)
