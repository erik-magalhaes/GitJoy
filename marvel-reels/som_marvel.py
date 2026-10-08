"""Trilha do Reels dos Marvel United: trailer de filme de herói (cordas em ostinato, tambores épicos, metais, "BRAAAM")
+ efeitos (portal abrindo, faísca, impacto, subida de tensão)."""
import os
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "voodoo-reels"))
sys.path.insert(0, os.path.join(HERE, "..", "sintonia-reels"))
sys.path.insert(0, os.path.join(HERE, "..", "nekojima-reels"))
sys.path.insert(0, os.path.join(HERE, "..", "hotstreak-reels"))
from audio import SR, add, env, hp, lp, noise, t_, read_wav, fx_pop, fx_whoosh, fx_ding  # noqa: E402
from trilha import note, kick  # noqa: E402
import som_neko as sn  # noqa: E402
import som_hs  # noqa: E402


def saw(f, t):
    return 2 * ((f * t) % 1) - 1


def cordas(f, d):
    """Cordas em staccato (serra filtrada com ataque curto)."""
    t = t_(d)
    x = saw(f, t) + saw(f * 1.004, t) + 0.5 * saw(f * 2, t)
    return lp(x, 2200) * np.minimum(1, t / 0.008) * np.exp(-t / (d * 0.5)) * 0.35


def metal(freqs, d):
    t = t_(d)
    x = sum(saw(f, t) + saw(f * 1.003, t) for f in freqs) / len(freqs)
    a = np.minimum(1, t / 0.06) * np.exp(-np.maximum(0, t - d * 0.4) / (d * 0.3))
    return lp(x, 1600) * a * 0.5


def taiko():
    d = 0.9
    t = t_(d)
    f = 90 * np.exp(-t / 0.08) + 45
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(d, 0.35)
    return x + lp(noise(d), 900) * env(d, 0.05) * 0.5


def fx_braam():
    """O "BRAAAM" de trailer: metais graves + sub."""
    d = 2.4
    t = t_(d)
    x = sum(saw(note(n), t) + saw(note(n) * 1.006, t) for n in ("D2", "A2", "D3", "F3")) / 8
    a = np.minimum(1, t / 0.04) * np.exp(-t / 1.1)
    sub = np.sin(2 * np.pi * 36.7 * t) * np.exp(-t / 0.9)
    return lp(x, 900) * a * 0.9 + sub * 0.8


def fx_portal():
    """Portal abrindo: chiado subindo + brilho cintilante."""
    d = 1.4
    t = t_(d)
    o = np.zeros(int(d * SR))
    sweep = hp(noise(d), 600) * np.minimum(1, t / 0.6) * np.exp(-np.maximum(0, t - 0.8) / 0.25)
    add(o, lp(sweep, 7000), 0, 0.6)
    rng = np.random.default_rng(3)
    for _ in range(28):
        tt = rng.uniform(0.1, 1.1)
        f = rng.uniform(2000, 5200)
        tk = t_(0.12)
        add(o, np.sin(2 * np.pi * f * tk) * env(0.12, 0.03), tt, rng.uniform(0.05, 0.15))
    return o


def fx_riser(d=2.0):
    t = t_(d)
    f = 200 * (8 ** (t / d))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3 + hp(noise(d), 2000) * 0.3
    return x * (t / d) ** 2


def fx_impacto():
    o = np.zeros(int(1.2 * SR))
    add(o, taiko(), 0, 1.0)
    add(o, sn.fx_hit(), 0, 0.7)
    return o


FX = {"pop": fx_pop, "swoosh": lambda: fx_whoosh(0.35), "ding": fx_ding, "portal": fx_portal, "braam": fx_braam,
      "riser": fx_riser, "impacto": fx_impacto, "cash": som_hs.fx_cash, "crowd": sn.fx_crowd, "zap": sn.FX["zap"],
      "flip": som_hs.fx_flip}


def trailer(dur):
    out = np.zeros(int(dur * SR))
    beat = 60 / 116
    prog = [("D3", ["D3", "F3", "A3"]), ("Bb2", ["Bb2", "D3", "F3"]), ("F2", ["F3", "A3", "C4"]),
            ("C3", ["C3", "E3", "G3"])]
    t, b = 0.0, 0
    while t < dur - 1.5:
        root, acorde = prog[(b // 1) % 4]
        bar = beat * 4
        calmo = t < 2.0
        for j in range(16):  # ostinato de cordas em semicolcheias
            n = [acorde[0], acorde[0], acorde[1], acorde[0], acorde[2], acorde[0], acorde[1], acorde[2]][j % 8]
            add(out, cordas(note(n) * 2, beat / 4 * 0.9), t + j * beat / 4, 0.28 if calmo else 0.42)
        add(out, metal([note(n) for n in acorde], bar * 0.9), t, 0.18 if calmo else 0.35)
        if not calmo:
            for j in (0, 1.5, 2, 3, 3.5):
                add(out, taiko(), t + j * beat, 0.55)
            for j in range(4):
                add(out, kick(), t + j * beat, 0.4)
        t += bar
        b += 1
    add(out, fx_braam(), dur - 2.5, 0.9)
    n = int(0.6 * SR)
    out[-n:] *= np.linspace(1, 0, n)
    return out


def build(path, dur, warp=None, voz=None, cues=()):
    warp = warp or (lambda t: t)
    m = trailer(dur)
    m = m / (np.abs(m).max() + 1e-9) * 0.3
    s = np.zeros_like(m)
    for t, name, g in cues:
        if g > 0:
            add(s, FX[name](), warp(t), g)
    bed = m + s * 0.5
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
