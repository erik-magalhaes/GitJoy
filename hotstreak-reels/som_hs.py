"""Trilha do Reels do Hot Streak: galope de corrida com metais + efeitos (corneta de largada, caixa registradora,
carta virando, tombo, torcida)."""
import os
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "nekojima-reels"))
import som_neko as sn  # noqa: E402
from som_neko import SR, add, env, hp, lp, noise, t_, read_wav, note, kick, clap, hat, brass, bass, saw  # noqa: E402
from audio import fx_boing  # noqa: E402


def trompete(f, d):
    t = t_(d)
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(1, t / 0.2)
    ph = np.cumsum(f * vib) / SR
    x = sum(np.sin(2 * np.pi * k * ph) / k ** 0.9 for k in range(1, 9))
    a = np.minimum(1, t / 0.025) * np.minimum(1, (d - t) / 0.04)
    return lp(x, 3800) * a * 0.5


def fx_bugle():
    """Corneta de chamada para a largada (como no hipódromo)."""
    seq = [("G4", 0.14), ("C5", 0.14), ("E5", 0.14), ("G5", 0.28), ("E5", 0.14), ("G5", 0.55)]
    o = np.zeros(int(1.6 * SR))
    t = 0.0
    for n, d in seq:
        add(o, trompete(note(n), d * 0.95), t, 0.8)
        t += d
    return o


def fx_cash():
    """Caixa registradora: tique da gaveta + sininho."""
    o = np.zeros(int(0.9 * SR))
    add(o, hp(noise(0.05), 2500) * env(0.05, 0.01), 0, 0.6)
    add(o, hp(noise(0.06), 1800) * env(0.06, 0.015), 0.07, 0.5)
    for f, g in ((2637, 0.5), (3520, 0.35), (5274, 0.15)):
        t = t_(0.7)
        add(o, np.sin(2 * np.pi * f * t) * env(0.7, 0.25), 0.16, g)
    return o


def fx_flip():
    """Carta virando na mesa."""
    o = np.zeros(int(0.3 * SR))
    add(o, lp(hp(noise(0.12), 900), 6000) * env(0.12, 0.03, 0.02), 0, 0.7)
    add(o, hp(noise(0.03), 2000) * env(0.03, 0.008), 0.1, 0.8)
    return o


def fx_tombo():
    """Tombo: boing descendo + baque."""
    o = np.zeros(int(0.9 * SR))
    t = t_(0.5)
    f = 420 * np.exp(-t / 0.25) + 90
    add(o, np.sin(2 * np.pi * np.cumsum(f) / SR) * env(0.5, 0.25) * (1 + 0.4 * np.sin(2 * np.pi * 18 * t)), 0, 0.6)
    add(o, sn.fx_hit(), 0.35, 0.7)
    return o


def fx_buzzer():
    """Buzina de desclassificação."""
    d = 0.75
    t = t_(d)
    x = sum(np.sign(np.sin(2 * np.pi * f * t)) for f in (110, 116, 165)) / 3
    return lp(x, 2200) * np.minimum(1, t / 0.01) * np.minimum(1, (d - t) / 0.05) * 0.7


def fx_shh():
    d = 0.9
    t = t_(d)
    return lp(hp(noise(d), 2500), 7000) * np.minimum(1, t / 0.15) * np.minimum(1, (d - t) / 0.3) * 0.6


def fx_aah():
    """Torcida gritando mais forte (gritaria da mesa)."""
    o = np.zeros(int(2.6 * SR))
    add(o, sn.fx_crowd(), 0, 1.0)
    add(o, sn.fx_crowd(), 0.15, 0.8)
    d = 1.8
    t = t_(d)
    v = sum(lp(saw(f * (1 + 0.01 * np.sin(2 * np.pi * 5 * t + f)), t), 1800) for f in (220, 262, 330, 392)) / 4
    add(o, v * np.minimum(1, t / 0.15) * np.exp(-np.maximum(0, t - 0.8) / 0.5) * 0.35, 0.05, 1.0)
    return o


sn.FX.update({"bugle": fx_bugle, "cash": fx_cash, "flip": fx_flip, "tombo": fx_tombo, "buzzer": fx_buzzer,
              "shh": fx_shh, "aah": fx_aah, "boing": fx_boing})


def galope(dur):
    """Galope de corrida (2/4 rápido): baixo oom-pah, metais e uma melodia que sobe."""
    out = np.zeros(int(dur * SR))
    beat = 60 / 152
    bar = beat * 2
    prog = [["C4", "E4", "G4"], ["C4", "E4", "G4"], ["G3", "B3", "D4"], ["G3", "B3", "D4"],
            ["A3", "C4", "E4"], ["F3", "A3", "C4"], ["D4", "F#4", "A4"], ["G3", "B3", "D4"]]
    roots = ["C2", "C2", "G1", "G1", "A1", "F1", "D2", "G1"]
    mel = [["G5", "E5", "G5", "E5"], ["C6", "B5", "A5", "G5"], ["F5", "D5", "F5", "D5"], ["B5", "A5", "G5", "F5"],
           ["E5", "C5", "E5", "A5"], ["F5", "A5", "C6", "A5"], ["F#5", "A5", "D6", "C6"], ["B5", "G5", "D5", "B4"]]
    t, b = 0.0, 0
    while t < dur - 1.0:
        k = b % 8
        calm = t < 2.2  # gancho: só a torcida e o batimento
        r = note(roots[k])
        for j in range(2):
            add(out, kick(), t + beat * j, 0.75 if not calm else 0.3)
            add(out, bass(r, beat * 0.4), t + beat * j, 0.5)
            add(out, brass([note(n) for n in prog[k]], beat * 0.35), t + beat * j + beat / 2, 0.3)
        if not calm:
            add(out, clap(), t + beat, 0.4)
            for j in range(4):
                add(out, hat(j % 2 == 1), t + beat * j / 2, 0.18)
            if (b // 8) % 2 == 1 or t > 34:  # melodia entra na segunda volta e na corrida
                for j, n in enumerate(mel[k]):
                    add(out, trompete(note(n), beat * 0.45), t + beat * j / 2, 0.14)
        t += bar
        b += 1
    add(out, brass([note("C4"), note("E4"), note("G4"), note("C5")], 1.0), dur - 1.0, 0.8)
    n = int(0.5 * SR)
    out[-n:] *= np.linspace(1, 0, n)
    return out


def build(path, dur, warp=None, voz=None, cues=()):
    warp = warp or (lambda t: t)
    m = galope(dur)
    m = m / (np.abs(m).max() + 1e-9) * 0.28
    s = np.zeros_like(m)
    for t, name, g in cues:
        if g > 0:
            add(s, sn.FX[name](), warp(t), g)
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
