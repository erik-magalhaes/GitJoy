"""Trilha do Reels do Sintonia: groove leve e animado + efeitos + voz (opcional)."""
import os
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "voodoo-reels"))
from audio import (SR, add, env, hp, lp, noise, t_, read_wav,  # noqa: E402
                   fx_pop, fx_whoosh, fx_ding, fx_fanfare, fx_boing, fx_chime)


SEMI = {"C": -9, "C#": -8, "Db": -8, "D": -7, "Eb": -6, "E": -5, "F": -4, "F#": -3, "G": -2,
        "Ab": -1, "A": 0, "Bb": 1, "B": 2}


def note(name):
    n, o = name[:-1], int(name[-1])
    return 440 * 2 ** ((SEMI[n] + 12 * (o - 4)) / 12)


def kick():
    t = t_(0.35)
    f = 150 * np.exp(-t / 0.04) + 48
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(0.35, 0.12)


def clap():
    out = np.zeros(int(0.25 * SR))
    for k in range(3):
        add(out, hp(lp(noise(0.2), 2500), 800) * env(0.2, 0.05 if k == 2 else 0.01), k * 0.011, 0.6)
    return out


def hat(open_=False):
    d = 0.18 if open_ else 0.05
    return hp(noise(d), 7000) * env(d, 0.06 if open_ else 0.012)


def keys(freqs, dur):
    t = t_(dur)
    x = sum(np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.3) for f in freqs)
    trem = 1 + 0.15 * np.sin(2 * np.pi * 5 * t)
    return lp(x * trem, 2500) * env(dur, dur * 0.7, 0.01) / len(freqs)


def pluck(f):
    t = t_(0.5)
    x = np.sign(np.sin(2 * np.pi * f * t)) * 0.3 + np.sin(2 * np.pi * f * t)
    return lp(x, 3000) * env(0.5, 0.12)


def bassline(f, d):
    t = t_(d)
    x = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)
    return lp(x, 500) * env(d, d * 0.6, 0.005)


def music(dur):
    out = np.zeros(int(dur * SR))
    beat = 60 / 108
    bar = beat * 4
    chords = [["F4", "A4", "C5"], ["A3", "C4", "E4"], ["Bb3", "D4", "F4"], ["C4", "E4", "G4"]]
    roots = ["F2", "A2", "Bb2", "C3"]
    mel = [["C6", None, "A5", None, "F5", "G5", None, "A5"], ["E5", None, "C5", "E5", None, "G5", "A5", None],
           ["D5", None, "F5", None, "Bb5", "A5", None, "F5"], ["G5", None, "E5", "C5", None, "D5", "E5", "G5"]]
    t, b = 0.0, 0
    while t < dur - 1.2:
        intro = t < 5.8
        ch = [note(n) for n in chords[b % 4]]
        add(out, keys(ch, bar * 0.95), t, 0.55)
        for k in (0, 2.5) if not intro else (0,):
            add(out, kick(), t + beat * k, 0.9)
        if not intro:
            add(out, kick(), t + beat * 2, 0.8)
            for k in (1, 3):
                add(out, clap(), t + beat * k, 0.5)
            for k in range(8):
                add(out, hat(k == 7), t + beat * k / 2, 0.22 if k % 2 else 0.3)
            r = note(roots[b % 4])
            for k, mult in ((0, 1), (1.5, 1), (2, 2), (3, 1), (3.5, 1.5)):
                add(out, bassline(r * mult, beat * 0.45), t + beat * k, 0.5)
            if b % 2 == 1 or t > 46:
                for k, n in enumerate(mel[b % 4]):
                    if n:
                        add(out, pluck(note(n)), t + beat * k / 2, 0.16)
        t += bar
        b += 1
    add(out, kick() * 1.3, dur - 1.0, 1.0)
    add(out, keys([note("F4"), note("A4"), note("C5"), note("F5")], 1.0), dur - 1.0, 0.8)
    n = int(0.5 * SR)
    out[-n:] *= np.linspace(1, 0, n)
    return out


def fx_tick():
    t = t_(0.03)
    return (np.sin(2 * np.pi * 2400 * t) * 0.6 + hp(noise(0.03), 4000) * 0.4) * env(0.03, 0.006)


def fx_ratchet(d=0.8, rate=14):
    out = np.zeros(int(d * SR) + SR // 20)
    for k in range(int(d * rate)):
        add(out, fx_tick(), k / rate, 0.5)
    return out


def fx_reveal():
    out = np.zeros(int(1.2 * SR))
    add(out, fx_whoosh(0.4), 0, 0.6)
    add(out, fx_fanfare(), 0.35, 0.9)
    return out


FX = {"pop": fx_pop, "whoosh": fx_whoosh, "ding": fx_ding, "reveal": fx_reveal, "boing": fx_boing,
      "chime": fx_chime, "ratchet": fx_ratchet, "tick": fx_tick}


def cue_list():
    c = []
    P = lambda t, g=0.45: c.append((t, "pop", g))
    P(0.15); P(0.45); P(0.5, 0.3); c.append((1.0, "ratchet", 0.35)); c.append((3.0, "ratchet", 0.35)); P(3.0)
    c += [(6.0, "whoosh", 0.7)]; P(6.45, 0.6); P(6.9); P(7.3); c.append((8.2, "ding", 0.45))
    P(12.1); P(12.3); P(12.3, 0.3); c.append((13.0, "ratchet", 0.4)); c.append((14.6, "whoosh", 0.4))
    P(14.7); c.append((17.6, "whoosh", 0.35))
    P(20.1); P(20.6, 0.6); c.append((20.65, "boing", 0.25))
    P(25.3); c.append((26.0, "ratchet", 0.4)); P(27.6); c.append((28.6, "ratchet", 0.45)); P(25.8, 0.3)
    c.append((32.4, "reveal", 0.8)); P(32.2); P(33.3, 0.6); c.append((33.3, "ding", 0.5)); P(34.6)
    P(38.1); P(38.3)
    for i in range(3):
        P(38.8 + i * 0.9, 0.5)
    for i in range(3):
        P(41.8 + i * 0.25, 0.35)
    P(47.1); c.append((47.8, "whoosh", 0.4)); P(47.4, 0.3); P(49.0, 0.55); P(50.2, 0.4)
    P(57.1, 0.6); P(57.8); P(58.1); P(58.4); P(59.0, 0.5)
    c.append((DUR_HINT - 1.0, "chime", 0.5))
    return c


DUR_HINT = 66.0


def build(path, dur, warp=None, voz=None):
    global DUR_HINT
    DUR_HINT = 66.0
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
