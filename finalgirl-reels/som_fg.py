"""Trilha de TRAILER DE TERROR do Final Girl (sintetizada em numpy, sem direitos autorais).

Música "terror": drone grave, batida de coração que acelera, cordas em trêmulo e notas soltas de piano.
Efeitos: braam (impacto de trailer), trovão, riser, estalo de lanterna, coração, ampulheta, dados, stinger.
Registra tudo no comum/som.py (som.MUSICAS["terror"] e som.FX) para usar o mesmo som.build.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "comum"))
import som  # noqa: E402
from som import SR, add, env, hp, lp, noise, t_, fx_whoosh  # noqa: E402

rng = np.random.default_rng(13)


def saw(f, d):
    ph = np.cumsum(np.full(int(d * SR), f) if np.isscalar(f) else f) / SR
    return 2 * (ph % 1) - 1


def fx_braam():
    """Impacto grave de trailer: serra a 55 Hz abrindo e fechando o filtro + estrondo."""
    d = 2.2
    t = t_(d)
    x = sum(saw(55 * m, d) for m in (1, 1.006, 0.5, 1.5)) / 4
    corte = 120 + 1400 * np.exp(-t / 0.35)
    y = np.zeros_like(x)
    a = 0.0
    for i in range(0, len(x), 256):  # filtro que fecha devagar (em blocos)
        a = np.exp(-2 * np.pi * corte[i] / SR)
        seg_ = x[i:i + 256]
        z = np.zeros_like(seg_)
        prev = y[i - 1] if i else 0.0
        for j, v in enumerate(seg_):
            prev = (1 - a) * v + a * prev
            z[j] = prev
        y[i:i + 256] = z
    y *= np.minimum(1, t / 0.02) * np.exp(-t / 0.9)
    boom = lp(noise(d), 180) * env(d, 0.25) * 1.5
    return np.tanh((y * 1.6 + boom) * 1.2) * 0.9


def fx_trovao():
    d = 2.6
    t = t_(d)
    crack = hp(noise(d), 1500) * env(d, 0.05) * 0.8
    ronco = lp(noise(d), 160) * (np.minimum(1, t / 0.15) * np.exp(-t / 0.9)) * 2.2
    return crack + ronco


def fx_riser(d=1.6):
    t = t_(d)
    f = 300 + 2400 * (t / d) ** 2
    tom = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25
    ar = hp(noise(d), 2000) * 0.5
    return (tom + ar) * (t / d) ** 1.5


def fx_lanterna():
    """Clique da lanterna."""
    out = np.zeros(int(0.15 * SR))
    add(out, hp(noise(0.02), 2500) * env(0.02, 0.004), 0, 0.8)
    add(out, hp(noise(0.02), 1800) * env(0.02, 0.004), 0.05, 0.6)
    return out


def fx_coracao():
    out = np.zeros(int(0.7 * SR))
    for k, g in ((0, 1.0), (0.22, 0.7)):
        t = t_(0.25)
        f = 55 * (1 + 0.8 * np.exp(-t / 0.03))
        add(out, np.sin(2 * np.pi * np.cumsum(f) / SR) * env(0.25, 0.08), k, g)
    return out


def fx_stinger():
    """Cordas guinchando (o 'IIIH' do filme de terror)."""
    d = 1.0
    t = t_(d)
    x = sum(np.sin(2 * np.pi * (f * (1 + 0.004 * np.sin(2 * np.pi * 7 * t))) * t) for f in (1480, 1568, 1661))
    return hp(x / 3 + hp(noise(d), 4000) * 0.15, 600) * np.minimum(1, t / 0.01) * np.exp(-t / 0.4) * 0.5


def fx_dados():
    out = np.zeros(int(0.8 * SR))
    for k in range(7):
        add(out, hp(noise(0.03), 1200) * env(0.03, 0.008), k * 0.07 + rng.uniform(0, 0.03), 0.6 - k * 0.06)
    return out


def fx_ampulheta():
    d = 0.5
    return lp(hp(noise(d), 3000), 9000) * env(d, 0.25, 0.05) * 0.4


def fx_grito():
    """Corte de vítima: golpe seco + estalo agudo."""
    out = np.zeros(int(0.6 * SR))
    add(out, lp(noise(0.3), 500) * env(0.3, 0.06), 0, 1.0)
    add(out, fx_stinger()[: int(0.4 * SR)], 0.02, 0.6)
    return out


def terror(dur):
    n = int(dur * SR)
    out = np.zeros(n)
    t = t_(dur)
    # drone grave (lá menor) que respira
    drone = (np.sin(2 * np.pi * 55 * t) + 0.6 * np.sin(2 * np.pi * 82.4 * t) + 0.4 * np.sin(2 * np.pi * 110.3 * t))
    drone = lp(drone + 0.25 * saw(55.2, dur), 400) * (0.7 + 0.3 * np.sin(2 * np.pi * t / 9))
    out += drone * 0.35
    # cordas em trêmulo (sobe a tensão aos poucos)
    trem = (0.55 + 0.45 * np.sin(2 * np.pi * 9 * t)) * np.minimum(1, t / 12)
    cordas = sum(np.sin(2 * np.pi * f * t + 0.3 * np.sin(2 * np.pi * 5 * t)) for f in (440, 523.3, 659.3))
    out += lp(cordas, 2500) * trem * 0.06
    # coração: de 60 a 100 bpm
    tt = 1.0
    while tt < dur - 1:
        add(out, fx_coracao(), tt, 0.5)
        bpm = 60 + 40 * min(1, tt / dur)
        tt += 60 / bpm
    # notas soltas de piano (caixinha de música desafinada)
    notas = [880, 830.6, 659.3, 587.3, 523.3, 493.9]
    tt = 3.0
    k = 0
    while tt < dur - 2:
        d = 2.5
        tp = t_(d)
        f = notas[k % len(notas)]
        add(out, (np.sin(2 * np.pi * f * tp) + 0.3 * np.sin(2 * np.pi * 2.01 * f * tp)) * env(d, 0.8), tt, 0.12)
        tt += 2.6
        k += 1
    m = int(1.2 * SR)
    out[-m:] *= np.linspace(1, 0, m)
    return out


som.MUSICAS["terror"] = terror
som.FX.update({"braam": fx_braam, "trovao": fx_trovao, "riser": fx_riser, "lanterna": fx_lanterna,
               "coracao": fx_coracao, "stinger": fx_stinger, "dados": fx_dados, "ampulheta": fx_ampulheta,
               "grito": fx_grito, "whoosh_longo": lambda: fx_whoosh(0.6)})
