"""Trilhas e efeitos dos Reels novos (sintetizados em numpy, sem direitos autorais).

- gameshow: quiz animado (palmas, baixo saltitante, sininhos);
- travessa: trilha divertida de "tipos de jogador" (pizzicato, clarinete de brincadeira, estalos);
- retro70: groove anos 70 (reserva do BYE BYE, caso não use a música da trend).
build(..., musica=None) grava só os efeitos (versão para pôr a música em alta no Instagram).
"""
import os
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "voodoo-reels"))
sys.path.insert(0, os.path.join(HERE, "..", "sintonia-reels"))
from audio import SR, add, env, hp, lp, noise, t_, read_wav, fx_pop, fx_whoosh, fx_ding, fx_boing, fx_chime  # noqa: E402
from trilha import note, kick, clap, hat, keys, pluck, bassline, fx_tick, fx_reveal  # noqa: E402


# ---------------------------------------------------------------- efeitos
def fx_flip():
    """Carta virando: estalo de papel."""
    out = np.zeros(int(0.25 * SR))
    add(out, hp(noise(0.06), 2500) * env(0.06, 0.012), 0, 0.7)
    add(out, hp(noise(0.05), 3500) * env(0.05, 0.01), 0.07, 0.5)
    return out


def fx_rasga():
    """Pacotinho de figurinha rasgando."""
    d = 0.45
    x = hp(noise(d), 1800) * (0.5 + 0.5 * np.abs(np.sin(np.arange(int(d * SR)) / SR * 2 * np.pi * 38)))
    return lp(x, 9000) * env(d, 0.25, 0.02)


def fx_brilho():
    """Brilho holográfico: arpejo de sininhos subindo."""
    out = np.zeros(int(0.9 * SR))
    for k, n in enumerate(("E6", "G6", "B6", "E7")):
        t = t_(0.5)
        add(out, np.sin(2 * np.pi * note(n) * t) * env(0.5, 0.15), k * 0.07, 0.25)
    return out


def fx_barra():
    t = t_(0.08)
    return np.sin(2 * np.pi * (900 + 3000 * t) * t) * env(0.08, 0.03) * 0.5


def fx_carimbo():
    t = t_(0.3)
    f = 120 * np.exp(-t / 0.03) + 60
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(0.3, 0.08) + lp(noise(0.3), 1200) * env(0.3, 0.02) * 0.6


def fx_relogio():
    """Tique do relógio da contagem."""
    t = t_(0.06)
    return (np.sin(2 * np.pi * 1600 * t) * 0.5 + hp(noise(0.06), 3000) * 0.5) * env(0.06, 0.01)


def fx_tchau():
    """Polaroide saindo voando: assobio descendo + vento."""
    d = 0.5
    t = t_(d)
    f = 1800 * np.exp(-t / 0.25) + 500
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(d, 0.2, 0.02) * 0.35
    return x + fx_whoosh(0.5)[: len(x)] * 0.6


def fx_plateia():
    """Plateia comemorando (ruído filtrado com palmas)."""
    d = 1.6
    out = lp(hp(noise(d), 400), 3500) * np.minimum(1, t_(d) / 0.1) * np.exp(-t_(d) / 0.8) * 0.35
    rng = np.random.default_rng(5)
    for _ in range(40):
        add(out, clap() * 0.5, rng.uniform(0, 1.2), rng.uniform(0.2, 0.5))
    return out


FX = {"pop": fx_pop, "whoosh": lambda: fx_whoosh(0.35), "ding": fx_ding, "reveal": fx_reveal, "boing": fx_boing,
      "chime": fx_chime, "tick": fx_tick, "flip": fx_flip, "rasga": fx_rasga, "brilho": fx_brilho,
      "barra": fx_barra, "carimbo": fx_carimbo, "relogio": fx_relogio, "tchau": fx_tchau, "plateia": fx_plateia}


# ---------------------------------------------------------------- músicas
def gameshow(dur):
    out = np.zeros(int(dur * SR))
    beat = 60 / 124
    bar = beat * 4
    chords = [["C4", "E4", "G4"], ["A3", "C4", "E4"], ["F3", "A3", "C4"], ["G3", "B3", "D4"]]
    roots = ["C3", "A2", "F2", "G2"]
    mel = [["E5", "G5", None, "C6", None, "G5", "A5", None], ["C6", None, "A5", "E5", None, "G5", None, "E5"],
           ["F5", "A5", None, "C6", "A5", None, "F5", "G5"], ["D5", None, "G5", "B5", None, "D6", "B5", None]]
    t, b = 0.0, 0
    while t < dur - 1.0:
        add(out, keys([note(n) for n in chords[b % 4]], bar * 0.9), t, 0.4)
        for k in (0, 1, 2, 3):
            add(out, kick(), t + beat * k, 0.75)
        for k in (1, 3):
            add(out, clap(), t + beat * k, 0.5)
        for k in range(8):
            add(out, hat(k % 2 == 1), t + beat * k / 2, 0.2)
        r = note(roots[b % 4])
        for k, mult in ((0, 1), (0.5, 2), (1.5, 1), (2, 2), (3, 1), (3.5, 1.5)):
            add(out, bassline(r * mult, beat * 0.4), t + beat * k, 0.5)
        if b % 2 == 1:
            for k, n in enumerate(mel[b % 4]):
                if n:
                    add(out, pluck(note(n)), t + beat * k / 2, 0.14)
        t += bar
        b += 1
    n = int(0.6 * SR)
    out[-n:] *= np.linspace(1, 0, n)
    return out


def pizz(f):
    t = t_(0.35)
    x = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * 2 * f * t) + 0.2 * np.sin(2 * np.pi * 3 * f * t)
    return x * env(0.35, 0.07)


def clarinete(f, d):
    t = t_(d)
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.5 * t)
    ph = 2 * np.pi * np.cumsum(f * vib) / SR
    x = np.sin(ph) + 0.45 * np.sin(3 * ph) + 0.2 * np.sin(5 * ph)
    return lp(x, 2600) * np.minimum(1, t / 0.03) * np.exp(-np.maximum(0, t - d * 0.7) / 0.06) * 0.4


def travessa(dur):
    """Trilha 'de travessura': pizzicato saltitante + clarinete brincalhão + estalos de dedo."""
    out = np.zeros(int(dur * SR))
    beat = 60 / 116
    bar = beat * 4
    roots = ["D3", "G2", "A2", "D3"]
    arpe = [["D4", "F4", "A4", "F4"], ["G3", "Bb3", "D4", "Bb3"], ["A3", "C#4", "E4", "C#4"], ["D4", "F4", "A4", "D5"]]
    mel = [[("A4", 1), ("F4", 0.5), ("G4", 0.5), ("A4", 1), (None, 1)], [("Bb4", 1), ("A4", 0.5), ("G4", 0.5), ("D4", 2)],
           [("E4", 0.5), ("F4", 0.5), ("G4", 0.5), ("A4", 0.5), ("C#5", 1), (None, 1)], [("D5", 1.5), ("A4", 0.5), ("D4", 1), (None, 1)]]
    t, b = 0.0, 0
    while t < dur - 1.0:
        k4 = b % 4
        add(out, bassline(note(roots[k4]), beat * 0.5), t, 0.55)
        add(out, bassline(note(roots[k4]) * 1.5, beat * 0.5), t + beat * 2, 0.45)
        for j in range(8):
            add(out, pizz(note(arpe[k4][j % 4])), t + j * beat / 2, 0.22)
        for j in (1, 3):
            add(out, clap() * 0.6, t + beat * j, 0.4)
        add(out, kick(), t, 0.5)
        add(out, kick(), t + beat * 2, 0.4)
        if t > 3 and b % 2 == 0:
            tt = t
            for n, d in mel[(b // 2) % 4]:
                if n:
                    add(out, clarinete(note(n), d * beat * 0.95), tt, 0.32)
                tt += d * beat
        t += bar
        b += 1
    n = int(0.6 * SR)
    out[-n:] *= np.linspace(1, 0, n)
    return out


def retro70(dur):
    """Groove anos 70: baixo, guitarra 'wah' e órgão."""
    out = np.zeros(int(dur * SR))
    beat = 60 / 112
    bar = beat * 4
    chords = [["G3", "B3", "D4"], ["C4", "E4", "G4"], ["D4", "F#4", "A4"], ["C4", "E4", "G4"]]
    roots = ["G2", "C3", "D3", "C3"]
    t, b = 0.0, 0
    while t < dur - 1.0:
        add(out, keys([note(n) for n in chords[b % 4]], bar * 0.95), t, 0.35)
        for k in (0, 2):
            add(out, kick(), t + beat * k, 0.7)
        for k in (1, 3):
            add(out, clap(), t + beat * k, 0.45)
        for k in range(16):
            add(out, hat(), t + beat * k / 4, 0.12 + 0.08 * (k % 2))
        r = note(roots[b % 4])
        for k, mult in ((0, 1), (0.75, 1), (1.5, 2), (2, 1), (2.75, 1.5), (3.5, 2)):
            add(out, bassline(r * mult, beat * 0.35), t + beat * k, 0.6)
        t += bar
        b += 1
    n = int(0.6 * SR)
    out[-n:] *= np.linspace(1, 0, n)
    return out


MUSICAS = {"gameshow": gameshow, "travessa": travessa, "retro70": retro70}


def build(path, dur, cues=(), musica="gameshow", warp=None, voz=None, fx_ganho=0.5):
    warp = warp or (lambda t: t)
    n = int(dur * SR)
    m = MUSICAS[musica](dur) if musica else np.zeros(n)
    m = m[:n] if len(m) >= n else np.pad(m, (0, n - len(m)))
    if musica:
        m = m / (np.abs(m).max() + 1e-9) * 0.3
    s = np.zeros(n)
    for t, name, g in cues:
        add(s, FX[name](), warp(t), g)
    bed = m + s * fx_ganho
    bed = np.tanh(bed * 1.2) / np.tanh(1.2) * 0.62
    if voz:
        v = np.zeros(n)
        for arq, t0 in voz:
            add(v, read_wav(arq), t0, 1.0)
        act = lp(np.abs(v), 8)
        act = np.clip(act / (act.max() * 0.15 + 1e-9), 0, 1)
        duck = 1 - 0.6 * lp(lp(act, 3), 3)
        mix = bed * duck + v * 0.95
    else:
        mix = bed
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    mix = mix / (np.abs(mix).max() + 1e-9) * (0.71 if musica or voz else 0.5)
    st = np.repeat((mix * 32767).astype(np.int16)[:, None], 2, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(st.tobytes())
    print("ok:", path, flush=True)
