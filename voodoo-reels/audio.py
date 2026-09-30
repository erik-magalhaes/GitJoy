"""Trilha sintetizada (música vudu + efeitos) sincronizada com as cenas do reels.py."""
import wave

import numpy as np
from scipy.signal import lfilter

SR = 44100
rng = np.random.default_rng(7)


def t_(dur):
    return np.arange(int(dur * SR)) / SR


def env(dur, tau, attack=0.003):
    t = t_(dur)
    return np.minimum(1, t / attack) * np.exp(-t / tau)


def lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    return lfilter([1 - a], [1, -a], x)


def hp(x, fc):
    return x - lp(x, fc)


def noise(dur):
    return rng.uniform(-1, 1, int(dur * SR))


# ---------------------------------------------------------------- instrumentos
def doum(f0=95):
    t = t_(0.5)
    f = f0 * (0.55 + 0.45 * np.exp(-t / 0.05))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(0.5, 0.18)


def tek():
    return (np.sin(2 * np.pi * 330 * t_(0.15)) * 0.5 + hp(noise(0.15), 1500) * 0.4) * env(0.15, 0.03)


def shaker():
    return hp(noise(0.07), 5000) * env(0.07, 0.015, 0.01)


def marimba(f):
    t = t_(0.7)
    return (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t / 0.04)) * env(0.7, 0.22)


def bass(f):
    t = t_(1.2)
    x = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)
    return lp(x, 400) * env(1.2, 0.45, 0.01)


def note(name):
    names = {"C": -9, "D": -7, "Eb": -6, "F": -4, "G": -2, "A": 0, "Bb": 1}
    n, o = name[:-1], int(name[-1])
    return 440 * 2 ** ((names[n] + 12 * (o - 4)) / 12)


def add(buf, x, at, gain=1.0):
    i = int(at * SR)
    if i >= len(buf):
        return
    x = x[: len(buf) - i]
    buf[i:i + len(x)] += x * gain


def music(dur):
    out = np.zeros(int(dur * SR))
    beat = 60 / 100
    bar = beat * 4
    riff = [["D5", None, "F5", "G5", None, "A5", "G5", "F5"],
            ["D5", None, "C5", "D5", None, "F5", "D5", None],
            ["D5", None, "F5", "G5", None, "A5", "C6", "A5"],
            ["G5", None, "F5", "D5", None, "C5", "D5", None]]
    roots = ["D2", "D2", "Bb1", "A1"]
    t, b = 0.0, 0
    while t < dur - 0.8:
        intro = t < 4.8
        add(out, doum(), t, 0.9)
        add(out, doum(80), t + beat * 1.5, 0.6)
        if not intro:
            add(out, doum(), t + beat * 2.5, 0.7)
            for k in (1, 2, 3, 3.5):
                add(out, tek(), t + beat * k, 0.35)
            for k in range(8):
                add(out, shaker(), t + beat * k / 2, 0.22 if k % 2 else 0.35)
            add(out, bass(note(roots[b % 4])), t, 0.55)
            for k, n in enumerate(riff[b % 4]):
                if n:
                    add(out, marimba(note(n)), t + beat * k / 2, 0.22)
        else:
            add(out, bass(note("D2")), t, 0.5)
        t += bar
        b += 1
    # final
    add(out, doum(70) * 1.4, dur - 0.75, 1.0)
    add(out, bass(note("D2")), dur - 0.75, 0.8)
    drone = (np.sin(2 * np.pi * note("D3") * t_(dur)) + 0.6 * np.sin(2 * np.pi * note("A3") * t_(dur)))
    drone *= 0.05 * (0.7 + 0.3 * np.sin(2 * np.pi * 0.1 * t_(dur)))
    out += lp(drone, 900)
    fade = np.ones_like(out)
    n = int(0.4 * SR)
    fade[-n:] = np.linspace(1, 0, n)
    return out * fade


# ---------------------------------------------------------------- efeitos
def fx_pop():
    t = t_(0.09)
    f = 300 + 900 * t / 0.09
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(0.09, 0.04)


def fx_clack():
    t = t_(0.06)
    return (hp(noise(0.06), 2500) * 0.7 + np.sin(2 * np.pi * 1900 * t) * 0.5) * env(0.06, 0.012)


def fx_thud():
    return doum(70) * 0.9 + lp(noise(0.5), 300) * env(0.5, 0.06) * 0.6


def fx_whoosh(d=0.35):
    t = t_(d)
    e = np.sin(np.pi * t / d) ** 2
    return lp(hp(noise(d), 400), 3000) * e


def fx_zap():
    t = t_(0.6)
    f = 1400 * np.exp(-t / 0.15) + 120
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.4 + hp(noise(0.6), 3000) * 0.3
    return lp(x, 5000) * env(0.6, 0.2)


def fx_ding():
    t = t_(1.0)
    return (np.sin(2 * np.pi * 1318 * t) + 0.5 * np.sin(2 * np.pi * 1976 * t)) * env(1.0, 0.3)


def fx_boing():
    t = t_(0.3)
    f = 180 + 260 * t / 0.3 + 30 * np.sin(2 * np.pi * 18 * t)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(0.3, 0.12)


def fx_buzz():
    t = t_(0.5)
    x = np.sign(np.sin(2 * np.pi * 110 * t)) + np.sign(np.sin(2 * np.pi * 116 * t))
    return lp(x, 1500) * env(0.5, 0.35, 0.01) * 0.5


def fx_flap():
    return lp(noise(0.12), 2500) * env(0.12, 0.03)


def fx_fanfare():
    out = np.zeros(int(1.4 * SR))
    for k, n in enumerate(["D5", "F5", "A5", "D6"]):
        f = note(n)
        t = t_(0.9 if k == 3 else 0.35)
        x = (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * 2 * f * t) + 0.2 * np.sin(2 * np.pi * 3 * f * t))
        x *= env(len(t) / SR, 0.5 if k == 3 else 0.2, 0.01)
        add(out, x, k * 0.13, 0.5)
    return out


def fx_rattle(d=0.45):
    out = np.zeros(int(d * SR) + SR // 10)
    for k in range(9):
        add(out, fx_clack(), rng.uniform(0, d), rng.uniform(0.3, 0.7))
    return out


def fx_dundun():
    return (doum(60) * 1.2)


def fx_chime():
    out = np.zeros(int(1.6 * SR))
    for k, n in enumerate(["A5", "D6", "F6", "A6"]):
        f = note(n)
        t = t_(1.2)
        add(out, np.sin(2 * np.pi * f * t) * env(1.2, 0.4), k * 0.08, 0.4)
    return out


FX = {"pop": fx_pop, "clack": fx_clack, "thud": fx_thud, "whoosh": fx_whoosh, "zap": fx_zap,
      "ding": fx_ding, "boing": fx_boing, "buzz": fx_buzz, "flap": fx_flap, "fanfare": fx_fanfare,
      "rattle": fx_rattle, "dundun": fx_dundun, "chime": fx_chime}


def contacts(t0, dur, n=3):
    """Instantes em que um objeto do bounce_path toca a mesa."""
    out = []
    for k in range(1, n + 1):
        e = k / n
        u = 1 - np.sqrt(1 - e) if e < 1 else 1.0
        out.append(t0 + dur * u)
    return out


def cue_list():
    c = []
    P = lambda t, g=0.5: c.append((t, "pop", g))
    # 1. gancho
    P(0.3); P(1.1)
    for t in contacts(0.15, 1.05):
        c.append((t, "thud", 0.5))
    for i in range(4):
        for t in contacts(1.5 + i * 0.28, 0.5, 2):
            c.append((t, "clack", 0.6))
    c += [(3.0, "zap", 0.7), (3.0, "thud", 0.6)]
    P(3.3)
    # 2. título
    c += [(5.1, "whoosh", 0.5), (5.55, "thud", 0.9)]
    P(6.1, 0.6); P(6.8); c.append((7.6, "whoosh", 0.25)); P(8.6)
    # 3. dados
    P(11.2)
    c.append((11.45, "rattle", 0.7))
    for k in range(5):
        for t in contacts(11 + 0.5 + k * 0.07, 1.15 + k * 0.08):
            c.append((t, "clack", 0.7))
    P(14.6)
    for i in range(3):
        c.append((14.6 + i * 0.14 + 0.55, "clack", 0.5))
    c.append((16.4, "whoosh", 0.4)); P(16.4); P(16.5, 0.6)
    c.append((17.6, "rattle", 0.6))
    for t in contacts(17.6, 1.1):
        c.append((t, "clack", 0.7))
    c.append((20.35, "clack", 0.5))
    # 4. carta
    c.append((22.2, "whoosh", 0.5)); P(22.3)
    c.append((23.35, "flap", 0.8))
    for i in range(4):
        c.append((24.9 + i * 0.22 + 0.45, "pop", 0.4))
    c += [(26.5, "whoosh", 0.5), (27.2, "zap", 0.8), (27.2, "thud", 0.5)]
    P(27.2); c.append((27.6, "ding", 0.5)); P(27.6)
    # 5. maldições
    P(30.1); P(30.4)
    for k in range(1, 11):
        c.append((30 + k / 1.4, "boing", 0.25))
    P(37.6); P(37.9); c.append((38.0, "whoosh", 0.3))
    c += [(42.8, "dundun", 0.9)]; P(42.8)
    # 6. esqueceu
    P(45.2); c.append((45.7, "flap", 0.6)); c.append((46.4, "buzz", 0.6)); P(46.4, 0.4)
    P(48.1)
    c += [(48.8, "whoosh", 0.25), (49.22, "clack", 0.7), (49.2, "ding", 0.5)]; P(49.2)
    # 7. vitória
    P(52.1)
    c += [(52.72, "clack", 0.7), (53.32, "clack", 0.7), (53.4, "fanfare", 0.8)]
    P(53.5)
    for t in (54.3, 54.7, 55.1):
        P(t, 0.4)
    # 8. chamada
    for t in (58.2, 58.3, 58.5, 59.1, 59.5, 60.7, 63.0, 63.3):
        P(t, 0.45)
    c.append((67.3, "chime", 0.6))
    return c


def build(path, dur):
    m = music(dur)
    m = m / (np.abs(m).max() + 1e-9) * 0.30
    s = np.zeros_like(m)
    for t, name, g in cue_list():
        add(s, FX[name](), t, g)
    mix = m + s * 0.55
    mix = np.tanh(mix * 1.2) / np.tanh(1.2)
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.89
    pcm = (mix * 32767).astype(np.int16)
    st = np.repeat(pcm[:, None], 2, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(st.tobytes())
    print("ok:", path)
