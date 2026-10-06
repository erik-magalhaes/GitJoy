"""Trilha do Reels do Nekojima: tema de transmissão esportiva + efeitos (torcida, apito, choque, madeira)."""
import os
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "voodoo-reels"))
sys.path.insert(0, os.path.join(HERE, "..", "sintonia-reels"))
sys.path.insert(0, os.path.join(HERE, "..", "architects-reels"))
from audio import (SR, add, env, hp, lp, noise, t_, read_wav, fx_pop, fx_whoosh, fx_ding,  # noqa: E402
                   fx_zap, fx_rattle, fx_clack, fx_thud)
from trilha import note, kick, clap, hat  # noqa: E402
from trilha_arq import fx_meow  # noqa: E402


def saw(f, t):
    return 2 * ((f * t) % 1) - 1


def brass(freqs, d=0.22):
    t = t_(d)
    x = sum(saw(f, t) + saw(f * 1.005, t) for f in freqs) / (2 * len(freqs))
    return lp(x, 2600) * env(d, d * 0.6, 0.008)


def bass(f, d):
    t = t_(d)
    return lp(saw(f, t), 400) * env(d, d * 0.7, 0.004)


def music(dur):
    out = np.zeros(int(dur * SR))
    beat = 60 / 126
    bar = beat * 4
    prog = [["E4", "G4", "B4"], ["C4", "E4", "G4"], ["D4", "F#4", "A4"], ["B3", "D4", "F#4"]]
    roots = ["E2", "C2", "D2", "B1"]
    t, b = 0.0, 0
    while t < dur - 1.0:
        ch = [note(n) for n in prog[b % 4]]
        calm = t < 2.6  # gancho: só tensão (batimento) até a torre cair
        if not calm:
            for k in range(4):
                add(out, kick(), t + beat * k, 0.8)
            for k in (1, 3):
                add(out, clap(), t + beat * k, 0.45)
            for k in range(8):
                add(out, hat(k % 2 == 1), t + beat * k / 2, 0.2)
            r = note(roots[b % 4])
            for k in range(8):
                add(out, bass(r * (2 if k % 2 else 1), beat * 0.45), t + beat * k / 2, 0.45)
            for k in (0, 1.5, 3):  # metais de vinheta esportiva
                add(out, brass(ch), t + beat * k, 0.35)
        t += bar
        b += 1
    add(out, brass([note("E4"), note("G#4"), note("B4"), note("E5")], 1.0), dur - 1.0, 0.8)
    n = int(0.5 * SR)
    out[-n:] *= np.linspace(1, 0, n)
    return out


def fx_hit():
    o = np.zeros(int(0.7 * SR))
    add(o, fx_thud(), 0, 0.8)
    add(o, lp(noise(0.3), 3000) * env(0.3, 0.05), 0, 0.6)
    add(o, kick(), 0, 0.7)
    return o


def fx_stinger():
    o = np.zeros(int(0.8 * SR))
    add(o, fx_whoosh(0.4), 0, 0.8)
    add(o, kick(), 0.18, 0.6)
    return o


def fx_beat():
    o = np.zeros(int(0.5 * SR))
    for k, g in ((0, 1.0), (0.16, 0.7)):
        t = t_(0.2)
        add(o, np.sin(2 * np.pi * 55 * t) * env(0.2, 0.06), k, g)
    return o


def fx_crash():
    """Torre de madeira desabando: muitos toques de madeira + baque."""
    rng = np.random.default_rng(3)
    o = np.zeros(int(1.8 * SR))
    add(o, fx_thud(), 0, 1.0)
    for k in range(26):
        tt = rng.uniform(0, 1.2) ** 1.4
        t = t_(0.12)
        f = rng.uniform(600, 1500)
        x = (np.sin(2 * np.pi * f * t) * 0.6 + hp(noise(0.12), 1500) * 0.4) * env(0.12, 0.02)
        add(o, x, tt, rng.uniform(0.3, 0.8))
    return o


def fx_crowd():
    d = 2.2
    t = t_(d)
    x = lp(hp(noise(d), 300), 2500) + 0.5 * lp(hp(noise(d), 150), 900)
    e = np.minimum(1, t / 0.25) * np.exp(-np.maximum(0, t - 0.6) / 0.7)
    return x * e * 0.8


def fx_whistle():
    d = 0.7
    t = t_(d)
    f = 2900 + 120 * np.sign(np.sin(2 * np.pi * 28 * t))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.6 + hp(noise(d), 4000) * 0.1
    return x * np.minimum(1, t / 0.02) * np.minimum(1, (d - t) / 0.05)


def fx_var():
    o = np.zeros(int(1.0 * SR))
    for k in range(3):
        t = t_(0.12)
        add(o, np.sin(2 * np.pi * 1400 * t) * env(0.12, 0.08), k * 0.22, 0.6)
    return o


FX = {"pop": fx_pop, "swoosh": lambda: fx_whoosh(0.3), "hit": fx_hit, "stinger": fx_stinger, "beat": fx_beat,
      "crash": fx_crash, "crowd": fx_crowd, "whistle": fx_whistle, "dice": fx_rattle, "cube": fx_clack,
      "wood": fx_clack, "zap": fx_zap, "var": fx_var, "ding": fx_ding, "meow": fx_meow}


def build(path, dur, warp=None, voz=None, cues=()):
    warp = warp or (lambda t: t)
    m = music(dur)
    m = m / (np.abs(m).max() + 1e-9) * 0.28
    s = np.zeros_like(m)
    for t, name, g in cues:
        if g > 0:
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
