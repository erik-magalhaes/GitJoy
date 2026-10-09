"""Trilha do Reels do hobby: lo-fi quentinho de ludoteca (piano elétrico com acordes de sétima, baixo redondo,
bateria macia) + efeitos (caixa na prateleira, etiqueta, caixa registradora)."""
import os
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "voodoo-reels"))
sys.path.insert(0, os.path.join(HERE, "..", "sintonia-reels"))
sys.path.insert(0, os.path.join(HERE, "..", "comum"))
sys.path.insert(0, os.path.join(HERE, "..", "hotstreak-reels"))
from audio import SR, add, env, hp, lp, noise, t_, read_wav, fx_pop, fx_whoosh, fx_ding, fx_clack, fx_thud  # noqa
from trilha import note, kick, hat, keys, pluck, bassline  # noqa: E402
import som_hs  # noqa: E402  (caixa registradora, carta virando, torcida)


def fx_caixa():
    """Caixa de papelão pousando na prateleira de madeira."""
    o = np.zeros(int(0.5 * SR))
    add(o, fx_thud(), 0, 0.7)
    add(o, lp(noise(0.08), 1800) * env(0.08, 0.02), 0, 0.5)
    add(o, fx_clack(), 0.01, 0.25)
    return o


def fx_papel():
    d = 0.25
    return lp(hp(noise(d), 1500), 7000) * env(d, 0.06, 0.02) * 0.6


def fx_tick():
    o = np.zeros(int(0.06 * SR))
    add(o, hp(noise(0.03), 3000) * env(0.03, 0.006), 0, 0.6)
    return o


FX = {"pop": fx_pop, "swoosh": lambda: fx_whoosh(0.3), "ding": fx_ding, "caixa": fx_caixa, "papel": fx_papel,
      "tick": fx_tick, "cash": som_hs.fx_cash, "flip": som_hs.fx_flip, "crowd": som_hs.sn.fx_crowd}


def snare():
    d = 0.18
    return (hp(lp(noise(d), 5000), 1200) * 0.7 + np.sin(2 * np.pi * 190 * t_(d)) * 0.4) * env(d, 0.05)


def lofi(dur):
    out = np.zeros(int(dur * SR))
    beat = 60 / 88
    bar = beat * 4
    prog = [["C4", "E4", "G4", "B4"], ["A3", "C4", "E4", "G4"], ["D4", "F4", "A4", "C5"], ["G3", "B3", "D4", "F4"]]
    roots = ["C2", "A1", "D2", "G1"]
    mel = [["E5", None, "G5", "B5"], ["A5", "G5", None, "E5"], ["F5", None, "A5", "C6"], ["B5", "A5", "G5", None]]
    t, b = 0.0, 0
    while t < dur - 1.5:
        k = b % 4
        add(out, keys([note(n) for n in prog[k]], bar * 0.95), t, 0.55)
        r = note(roots[k])
        add(out, bassline(r, beat * 1.6), t, 0.5)
        add(out, bassline(r * 1.5, beat * 0.8), t + beat * 2.5, 0.35)
        if t > 1.0:  # bateria entra depois do gancho
            for j in (0, 2.5):
                add(out, kick(), t + beat * j, 0.55)
            for j in (1, 3):
                add(out, snare(), t + beat * j, 0.3)
            for j in range(8):
                sw = 0.06 if j % 2 else 0  # suingue
                add(out, hat(j == 7), t + beat * (j / 2 + sw), 0.12)
        if b >= 2:
            for j, n in enumerate(mel[k]):
                if n:
                    add(out, pluck(note(n)), t + beat * j, 0.16)
        t += bar
        b += 1
    add(out, keys([note("C4"), note("E4"), note("G4"), note("B4"), note("D5")], 2.0), dur - 2.0, 0.7)
    # chiadinho de vinil
    out += lp(hp(noise(dur), 3000), 9000)[:len(out)] * 0.004
    n = int(0.6 * SR)
    out[-n:] *= np.linspace(1, 0, n)
    return out


def build(path, dur, warp=None, voz=None, cues=()):
    warp = warp or (lambda t: t)
    m = lofi(dur)
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
        duck = 1 - 0.6 * lp(lp(act, 3), 3)
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
