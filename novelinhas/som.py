"""Trilha de suspense e efeitos sintetizados em numpy (44,1 kHz, mono)."""
import numpy as np
from scipy.signal import butter, sosfilt

SR = 44100


def _t(d):
    return np.arange(int(d * SR)) / SR


def _env(n, a=0.005, r=0.2):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / max(r, 1e-4))
    return e


def _lp(x, f, ordem=2):
    return sosfilt(butter(ordem, f, "low", fs=SR, output="sos"), x)


def _bp(x, f1, f2, ordem=2):
    return sosfilt(butter(ordem, [f1, f2], "band", fs=SR, output="sos"), x)


def _hp(x, f, ordem=2):
    return sosfilt(butter(ordem, f, "high", fs=SR, output="sos"), x)


def saw(f, t):
    return 2 * ((f * t) % 1.0) - 1


def nota(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ------------------------------------------------------------------ efeitos
def receb():
    """'Tuc-tuc' de mensagem recebida."""
    out = np.zeros(int(0.22 * SR))
    for k, (f, t0) in enumerate(((1046, 0.0), (1397, 0.075))):
        t = _t(0.12)
        s = np.sin(2 * np.pi * f * t) * _env(len(t), 0.002, 0.035)
        i = int(t0 * SR)
        out[i:i + len(s)] += s * (0.5 if k == 0 else 0.42)
    return out


def envio():
    t = _t(0.12)
    f = 500 + 1600 * t / t[-1]
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(len(t), 0.003, 0.03)
    return 0.4 * s


def teclas(dur):
    out = np.zeros(int(dur * SR) + 1)
    rnd = np.random.default_rng(3)
    t = 0.0
    while t < dur:
        n = int(0.012 * SR)
        clique = _bp(rnd.standard_normal(n), 1800, 6000) * _env(n, 0.0005, 0.003)
        i = int(t * SR)
        out[i:i + n] += clique[:len(out) - i] * 0.35
        t += rnd.uniform(0.06, 0.11)
    return out


def notif():
    """Ding de notificação (três notas de sino)."""
    out = np.zeros(int(0.9 * SR))
    for f, t0 in ((1568, 0.0), (1319, 0.11), (2093, 0.22)):
        t = _t(0.6)
        s = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2.76 * f * t) * np.exp(-t / 0.05))
        s *= _env(len(t), 0.002, 0.18)
        i = int(t0 * SR)
        out[i:i + len(s)] += 0.32 * s
    return out


def whoosh(dur=0.32, sobe=True):
    rnd = np.random.default_rng(5)
    n = int(dur * SR)
    x = rnd.standard_normal(n)
    out = np.zeros(n)
    passos = 16
    for k in range(passos):
        a, b = k * n // passos, (k + 1) * n // passos
        p = k / (passos - 1)
        fc = 400 + 3000 * (p if sobe else 1 - p)
        out[a:b] = _bp(x[a:b], fc * 0.6, fc * 1.4)
    env = np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    return 0.5 * out * env / (np.abs(out).max() + 1e-9)


def apaga():
    return whoosh(0.4, sobe=False) * 0.8


def impacto():
    t = _t(1.6)
    boom = np.sin(2 * np.pi * (55 + 40 * np.exp(-t / 0.08)) * t) * np.exp(-t / 0.5)
    rnd = np.random.default_rng(9)
    ruido = _lp(rnd.standard_normal(len(t)), 900) * np.exp(-t / 0.12)
    return 0.8 * boom + 0.25 * ruido / (np.abs(ruido).max() + 1e-9)


def _metal(acorde, dur, ataque=0.01):
    t = _t(dur)
    s = np.zeros(len(t))
    for m in acorde:
        for det in (-0.12, 0.0, 0.11):
            s += saw(nota(m + det), t)
    s = _lp(s / (len(acorde) * 3), 1800)
    return s * _env(len(t), ataque, dur * 0.55)


def tantan():
    """'Tan, tan, taaan!' de novela: dois golpes curtos e um longo, com tímpano."""
    out = np.zeros(int(3.4 * SR))
    acorde = [38, 45, 50, 53, 57]  # ré menor grave
    for t0, d, g in ((0.0, 0.32, 0.8), (0.36, 0.32, 0.85), (0.74, 2.6, 1.0)):
        s = _metal(acorde if t0 < 0.7 else [37, 44, 49, 52, 56], d * 1.4) * g
        tt = _t(1.2)
        timp = np.sin(2 * np.pi * (73 + 25 * np.exp(-tt / 0.05)) * tt) * np.exp(-tt / (0.25 if d < 1 else 0.7))
        i = int(t0 * SR)
        out[i:i + len(s)] += 0.6 * s[:len(out) - i]
        out[i:i + len(timp)] += 0.5 * timp[:len(out) - i]
    # cauda de "sala"
    rev = np.zeros_like(out)
    for k, dl in enumerate((0.043, 0.071, 0.113, 0.157, 0.211)):
        n = int(dl * SR)
        rev[n:] += out[:-n] * (0.35 * 0.8 ** k)
    return out + _lp(rev, 3000)


EFEITOS = dict(receb=receb, envio=envio, notif=notif, whoosh=whoosh, apaga=apaga, impacto=impacto, tantan=tantan)


# ------------------------------------------------------------------ trilha
def trilha(dur, seed=1):
    """Cama de suspense: pedal grave, pulso de coração, pizzicato em lá menor e um tique-taque discreto."""
    n = int(dur * SR) + SR
    t = np.arange(n) / SR
    out = np.zeros(n)
    # pedal (lá + mi) com respiração lenta
    pedal = (saw(nota(33), t) + saw(nota(40), t) * 0.7 + saw(nota(33) * 1.003, t) * 0.6)
    pedal = _lp(pedal, 380) * (0.55 + 0.45 * np.sin(2 * np.pi * t / 8.0) ** 2)
    out += 0.16 * pedal
    bpm = 84
    beat = 60 / bpm
    rnd = np.random.default_rng(seed)
    # pulso tipo coração (tum-tum)
    k = 0
    while k * beat * 2 < dur + 1:
        for off, g in ((0.0, 1.0), (0.22, 0.7)):
            i = int((k * beat * 2 + off) * SR)
            tt = _t(0.25)
            s = np.sin(2 * np.pi * (52 + 30 * np.exp(-tt / 0.03)) * tt) * np.exp(-tt / 0.09)
            out[i:i + len(s)] += 0.32 * g * s[:max(0, n - i)]
        k += 1
    # pizzicato: arpejo menor harmônico
    escala = [57, 60, 64, 68, 69, 64, 60, 59, 57, 60, 65, 64, 62, 59, 56, 59]
    passo = beat / 2
    i_n = 0
    tp = 0.0
    while tp < dur + 1:
        if rnd.random() < 0.72:
            m = escala[i_n % len(escala)]
            tt = _t(0.5)
            f = nota(m)
            s = (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * 2 * f * tt) + 0.15 * np.sin(2 * np.pi * 3 * f * tt))
            s *= _env(len(tt), 0.002, 0.12)
            i = int(tp * SR)
            out[i:i + len(s)] += 0.085 * s[:max(0, n - i)]
        i_n += 1
        tp += passo
    # tique-taque
    tp = 0.0
    while tp < dur + 1:
        i = int(tp * SR)
        m = int(0.01 * SR)
        clk = _hp(rnd.standard_normal(m), 3000) * _env(m, 0.0005, 0.002)
        out[i:i + m] += 0.05 * clk[:max(0, n - i)]
        tp += beat
    # cordas agudas que entram e saem
    cordas = sum(np.sin(2 * np.pi * nota(m) * t + 0.3 * np.sin(2 * np.pi * 5 * t)) for m in (76, 81))
    out += 0.025 * cordas * np.clip(np.sin(2 * np.pi * t / 16.0 - 1.2), 0, 1)
    return out[:int(dur * SR)]


def telefone(x):
    """Áudio de WhatsApp: banda de telefone + leve saturação."""
    y = _bp(x, 220, 5200, 2)
    y = np.tanh(y * 1.6) / np.tanh(1.6)
    return y * 0.9


def trilha_terror(dur, seed=1):
    """Cama de terror: pedal grave que "bate", vento, sino distante desafinado, assobio agudo e coração lento."""
    n = int(dur * SR) + SR
    t = np.arange(n) / SR
    rnd = np.random.default_rng(seed + 100)
    out = np.zeros(n)
    # pedal grave com batimento (duas frequências quase iguais)
    out += 0.22 * _lp(np.sin(2 * np.pi * 49 * t) + np.sin(2 * np.pi * 49.6 * t) + 0.5 * saw(73.4, t), 300)
    # vento: ruído filtrado que sobe e desce
    vento = _bp(rnd.standard_normal(n), 300, 1400)
    out += 0.05 * vento * (0.4 + 0.6 * np.sin(2 * np.pi * t / 11.0) ** 2)
    # coração lento
    k = 0.0
    while k < dur + 1:
        for off, g in ((0.0, 1.0), (0.26, 0.65)):
            i = int((k + off) * SR)
            tt = _t(0.3)
            s_ = np.sin(2 * np.pi * (45 + 25 * np.exp(-tt / 0.03)) * tt) * np.exp(-tt / 0.1)
            out[i:i + len(s_)] += 0.34 * g * s_[:max(0, n - i)]
        k += 1.6
    # sino distante, inarmônico
    tp = 3.0
    while tp < dur:
        i = int(tp * SR)
        tt = _t(3.0)
        f0 = rnd.choice([220.0, 233.1, 207.7])
        s_ = sum(a * np.sin(2 * np.pi * f0 * r * tt) for r, a in ((1, 1), (2.76, 0.5), (5.4, 0.25), (8.9, 0.12)))
        s_ *= np.exp(-tt / 1.1)
        out[i:i + len(s_)] += 0.06 * s_[:max(0, n - i)]
        tp += rnd.uniform(7, 12)
    # assobio agudo que desliza (aparece e some)
    f = 1500 + 300 * np.sin(2 * np.pi * t / 9.0)
    assobio = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.clip(np.sin(2 * np.pi * t / 13.0 - 2.0), 0, 1) ** 2
    out += 0.012 * assobio
    return out[:int(dur * SR)]


def fantasma(x):
    """Áudio "do além": voz mais baixa e abafada, com eco longo, tremor lento e chiado de fundo."""
    y = _bp(x, 180, 3800, 2) * 0.8
    n = len(y) + int(1.2 * SR)
    out = np.zeros(n)
    out[:len(y)] += y
    for k, (dl, g) in enumerate(((0.09, 0.45), (0.17, 0.35), (0.29, 0.28), (0.47, 0.2), (0.71, 0.14))):
        i = int(dl * SR)
        out[i:i + len(y)] += g * _lp(y, 2500 - 300 * k)
    t = np.arange(n) / SR
    out *= 0.85 + 0.15 * np.sin(2 * np.pi * 4.5 * t)
    rnd = np.random.default_rng(13)
    out += 0.012 * _hp(rnd.standard_normal(n), 2000)
    return out * 0.85
