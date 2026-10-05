"""Trilha do Reels do MLEM: synth espacial animado + efeitos + voz (opcional)."""
import os
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "voodoo-reels"))
sys.path.insert(0, os.path.join(HERE, "..", "sintonia-reels"))
from audio import (SR, add, env, hp, lp, noise, t_, read_wav, fx_pop, fx_whoosh, fx_ding,  # noqa: E402
                   fx_fanfare, fx_chime, fx_rattle, fx_clack, fx_boing)
from trilha import note, kick, clap, hat  # noqa: E402


def saw(f, t):
    return 2 * ((f * t) % 1) - 1


def pad(freqs, dur):
    t = t_(dur)
    x = sum(saw(f, t) + saw(f * 1.006, t) for f in freqs) / (2 * len(freqs))
    e = np.minimum(1, t / 0.4) * np.minimum(1, (dur - t) / 0.4)
    return lp(lp(x, 1400), 1800) * e


def arp_note(f, d=0.16):
    t = t_(d)
    x = np.sign(np.sin(2 * np.pi * f * t)) * 0.5 + np.sin(2 * np.pi * 2 * f * t) * 0.3
    return lp(x, 3500) * env(d, 0.07)


def bass(f, d):
    t = t_(d)
    return lp(saw(f, t), 300) * env(d, d * 0.7, 0.005)


def music(dur):
    out = np.zeros(int(dur * SR))
    beat = 60 / 116
    bar = beat * 4
    prog = [["A3", "C4", "E4"], ["F3", "A3", "C4"], ["C4", "E4", "G4"], ["G3", "B3", "D4"]]
    roots = ["A1", "F1", "C2", "G1"]
    t, b = 0.0, 0
    while t < dur - 1.2:
        intro = t < 2.2
        ch = [note(n) for n in prog[b % 4]]
        add(out, pad(ch, bar), t, 0.5)
        if not intro:
            for k in range(16):  # arpejo em semicolcheias
                f = ch[k % 3] * (2 if (k // 3) % 2 else 1)
                add(out, arp_note(f), t + beat * k / 4, 0.22)
            for k in (0, 1, 2, 3):
                add(out, kick(), t + beat * k, 0.75 if k % 2 == 0 else 0.55)
            for k in (1, 3):
                add(out, clap(), t + beat * k, 0.35)
            for k in range(8):
                add(out, hat(k % 2 == 1), t + beat * k / 2, 0.18)
            r = note(roots[b % 4])
            for k in range(8):
                add(out, bass(r * (2 if k % 2 else 1), beat * 0.45), t + beat * k / 2, 0.4)
        t += bar
        b += 1
    add(out, pad([note("A3"), note("C4"), note("E4"), note("A4")], 1.2), dur - 1.2, 0.8)
    n = int(0.5 * SR)
    out[-n:] *= np.linspace(1, 0, n)
    return out


def fx_beep(f=880):
    t = t_(0.18)
    return np.sin(2 * np.pi * f * t) * env(0.18, 0.08, 0.005)


def fx_launch():
    d = 3.0
    t = t_(d)
    x = lp(noise(d), 500) * 1.4 + lp(noise(d), 120) * 2.0
    e = np.minimum(1, t / 0.6) * np.exp(-np.maximum(0, t - 1.5) / 0.7)
    return x * e


def fx_alarm():
    d = 1.6
    t = t_(d)
    f = np.where((t * 4).astype(int) % 2 == 0, 880, 660)
    return np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.3 * lp(np.ones_like(t), 10)


def fx_boom():
    d = 2.0
    t = t_(d)
    x = lp(noise(d), 300) * 2.5 * np.exp(-t / 0.5) + np.sin(2 * np.pi * 45 * t) * np.exp(-t / 0.6)
    return x


FX = {"pop": fx_pop, "whoosh": fx_whoosh, "ding": fx_ding, "fanfare": fx_fanfare, "chime": fx_chime,
      "rattle": fx_rattle, "clack": fx_clack, "boing": fx_boing, "beep": fx_beep, "beephi": lambda: fx_beep(1320),
      "launch": fx_launch, "alarm": fx_alarm, "boom": fx_boom}


def cue_list():
    c = []
    P = lambda t, g=0.45: c.append((t, "pop", g))
    c += [(0.0, "beep", 0.6), (0.8, "beep", 0.6), (1.6, "beep", 0.6), (2.35, "beephi", 0.7), (2.3, "launch", 0.9)]
    P(2.6); P(3.4)
    c += [(5.6, "whoosh", 0.5)]; P(5.7); P(6.0); c.append((6.1, "whoosh", 0.4)); P(7.3); P(8.3)
    P(12.1); P(12.3)
    for i in range(4):
        c.append((13.0 + i * 0.7, "whoosh", 0.25)); c.append((13.5 + i * 0.7, "pop", 0.5))
    P(19.1); P(19.3); c.append((19.6, "rattle", 0.8))
    for k in range(6):
        c.append((19.6 + k * 0.05 + 0.9, "clack", 0.6))
    c.append((21.2, "ding", 0.3)); P(21.2); c.append((22.0, "whoosh", 0.4)); c.append((23.0, "whoosh", 0.5)); P(23.2, 0.6)
    P(24.6)
    P(28.1); P(28.3); P(28.8); c.append((30.6, "boing", 0.4)); c.append((31.4, "ding", 0.5)); P(31.0)
    c.append((33.2, "whoosh", 0.6)); P(33.6); P(33.9); P(34.0)
    c.append((38.3, "rattle", 0.6)); c += [(39.3, "clack", 0.6), (39.35, "clack", 0.6)]
    c.append((39.4, "alarm", 0.5)); c.append((40.4, "boom", 1.0)); P(40.5, 0.6); P(41.6)
    P(45.1); P(45.4); P(47.6); P(47.8); P(48.0); P(49.0); P(49.3)
    P(53.1, 0.6); P(53.8); P(54.2); P(54.5); P(55.6)
    c.append((58.6, "whoosh", 0.4)); P(58.6); P(59.3); P(59.6); P(59.9); P(60.5)
    c.append((64.5, "chime", 0.5))
    return c


def build(path, dur, warp=None, voz=None):
    warp = warp or (lambda t: t)
    m = music(dur)
    m = m / (np.abs(m).max() + 1e-9) * 0.30
    s = np.zeros_like(m)
    for t, name, g in cue_list():
        add(s, FX[name](), warp(t), g)
    bed = m + s * 0.55
    bed = np.tanh(bed * 1.2) / np.tanh(1.2) * 0.62
    if voz:
        v = np.zeros_like(bed)
        for arq, t0 in voz:
            add(v, read_wav(arq), t0, 1.0)
        act = lp(np.abs(v), 8)
        act = np.clip(act / (act.max() * 0.15 + 1e-9), 0, 1)
        mix = bed * (1 - 0.62 * lp(lp(act, 3), 3)) + v * 0.95
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
