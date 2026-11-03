"""Sons NOVOS para os 3 Reels do Becas (3/nov/2026). Pedido dele: "os vídeos estão ficando iguais, com os mesmos sons".
Nada aqui reaproveita as trilhas de `comum/som.py` (gameshow/travessa/brincalhona): cada vídeo tem um mundo sonoro próprio.

- feed (vídeo 1): rolagem do dedo, trinca e estilhaço de vidro, estouro grave, batida "pop" 118 bpm;
- café (vídeo 2): louça (xícara batendo, arrastando na mesa), tique de contagem, lounge de piano elétrico com vassourinha;
- relógio (vídeo 3): tique-taque que vira percussão, obturador, batida que acelera.
Tudo em numpy, 44,1 kHz, sem direitos autorais.
"""
import wave

import numpy as np

SR = 44100
RNG = np.random.default_rng(11)


def t_(d):
    return np.arange(int(d * SR)) / SR


def ruido(d):
    return RNG.standard_normal(int(d * SR))


def env(d, a=0.005, r=None):
    """Envelope ataque linear + queda exponencial."""
    t = t_(d)
    r = r or d / 4
    e = np.exp(-np.maximum(t - a, 0) / r)
    e[t < a] = t[t < a] / a
    return e


def lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):  # curto: só usado em sons de < 1 s
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y


def lp_fft(x, fc, q=1.0):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (f / fc) ** (2 * q))
    return np.fft.irfft(X, len(x))


def hp_fft(x, fc, q=1.0):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR) + 1e-9
    X *= 1 / np.sqrt(1 + (fc / f) ** (2 * q))
    return np.fft.irfft(X, len(x))


def bp_fft(x, f0, f1):
    return hp_fft(lp_fft(x, f1, 2), f0, 2)


def add(buf, s, t0, g=1.0):
    i = int(t0 * SR)
    if i >= len(buf) or i + len(s) <= 0:
        return
    j0 = max(0, -i)
    s = s[j0:]
    i = max(i, 0)
    n = min(len(s), len(buf) - i)
    buf[i:i + n] += s[:n] * g


def hz(nota):
    """'A4', 'C#5'… → Hz."""
    nomes = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4, "F#": -3, "G": -2, "G#": -1, "A": 0, "A#": 1,
             "B": 2}
    n, o = nota[:-1], int(nota[-1])
    return 440 * 2 ** ((nomes[n] + 12 * (o - 4)) / 12)


# ---------------------------------------------------------------- efeitos: feed
def rolagem():
    """Dedo arrastando a tela: sopro curto e agudo subindo."""
    d = 0.22
    x = bp_fft(ruido(d), 1800, 7000) * env(d, 0.03, 0.05)
    return x * 0.6


def trinca():
    """Vidro trincando: estalos secos em sequência + chiado fino."""
    d = 0.6
    out = np.zeros(int(d * SR))
    for k in range(9):
        c = hp_fft(ruido(0.03), 3000) * env(0.03, 0.0005, 0.004)
        add(out, c, 0.02 + k * 0.045 + RNG.uniform(0, 0.02), 0.9 - k * 0.06)
    add(out, hp_fft(ruido(0.5), 6000) * env(0.5, 0.01, 0.12), 0, 0.25)
    return out


def estilhaco():
    """Vidro estourando: impacto + cacos tilintando (senos agudos inarmônicos)."""
    d = 1.6
    out = np.zeros(int(d * SR))
    add(out, hp_fft(ruido(0.25), 1500) * env(0.25, 0.001, 0.05), 0, 1.0)
    for k in range(26):
        f = RNG.uniform(2500, 9000)
        dd = RNG.uniform(0.08, 0.4)
        s = np.sin(2 * np.pi * f * t_(dd)) * env(dd, 0.001, dd / 5)
        add(out, s, RNG.uniform(0.02, 1.0), RNG.uniform(0.1, 0.35))
    return out


def estouro():
    """Grave que abre o vídeo colorido (queda de 90 → 35 Hz)."""
    d = 1.2
    t = t_(d)
    f = 35 + 55 * np.exp(-t * 6)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(d, 0.003, 0.35)
    return np.tanh(s * 1.6) * 0.9


def cartao():
    """Etiqueta batendo na tela: 'tump' de papelão."""
    d = 0.18
    t = t_(d)
    s = np.sin(2 * np.pi * (180 + 120 * np.exp(-t * 40)) * t) * env(d, 0.001, 0.04)
    return s * 0.7 + lp(ruido(d), 1200) * env(d, 0.001, 0.02) * 0.4


# ---------------------------------------------------------------- efeitos: café
def louca(f0=2100):
    """Xícara de porcelana batendo: parciais inarmônicos com queda rápida."""
    d = 0.7
    out = np.zeros(int(d * SR))
    for mult, g, r in ((1.0, 0.6, 0.18), (2.76, 0.35, 0.10), (5.4, 0.22, 0.06), (8.9, 0.12, 0.04)):
        add(out, np.sin(2 * np.pi * f0 * mult * t_(d)) * env(d, 0.0005, r), 0, g)
    add(out, hp_fft(ruido(0.02), 4000) * env(0.02, 0.0003, 0.004), 0, 0.5)
    return out * 0.6


def arrasta(d=0.35):
    """Xícara arrastando na mesa (ruído grave filtrado)."""
    return bp_fft(ruido(d), 200, 1600) * env(d, 0.05, d / 2) * 0.45


def tique():
    d = 0.06
    return hp_fft(ruido(d), 2500) * env(d, 0.0005, 0.008) * 0.8


def sino():
    """'Acertou': sino de balcão de café."""
    d = 1.8
    out = np.zeros(int(d * SR))
    for mult, g in ((1, 0.5), (2.0, 0.25), (3.01, 0.15), (4.2, 0.08)):
        add(out, np.sin(2 * np.pi * 1320 * mult * t_(d)) * env(d, 0.001, 0.5 / mult), 0, g)
    return out


def dado():
    """Dado rolando na mesa: batidinhas que espaçam."""
    out = np.zeros(int(0.8 * SR))
    t = 0.0
    for k in range(6):
        s = bp_fft(ruido(0.03), 800, 5000) * env(0.03, 0.0005, 0.006)
        add(out, s, t, 0.9 - k * 0.12)
        t += 0.05 + k * 0.03
    return out


# ---------------------------------------------------------------- efeitos: relógio
def tic(agudo=True):
    d = 0.08
    f = 3200 if agudo else 2300
    return (np.sin(2 * np.pi * f * t_(d)) * env(d, 0.0003, 0.01) * 0.6 + hp_fft(ruido(d), 3000)
            * env(d, 0.0003, 0.004) * 0.4)


def obturador():
    """Clique de câmera (dois estalos)."""
    out = np.zeros(int(0.15 * SR))
    for t0, g in ((0, 0.9), (0.055, 0.6)):
        add(out, bp_fft(ruido(0.03), 1500, 8000) * env(0.03, 0.0003, 0.005), t0, g)
    return out


def sopro(d=0.5, sobe=True):
    """Whoosh de passagem de tempo."""
    x = ruido(d)
    e = np.sin(np.pi * t_(d) / d) ** 2
    lo, hi = (500, 5000) if sobe else (300, 3000)
    return bp_fft(x, lo, hi) * e * 0.5


def despertador():
    d = 1.0
    t = t_(d)
    trem = (np.sin(2 * np.pi * 22 * t) > 0).astype(float)
    s = (np.sin(2 * np.pi * 2600 * t) + 0.5 * np.sin(2 * np.pi * 3900 * t)) * trem * env(d, 0.005, 0.5)
    return s * 0.35


# ---------------------------------------------------------------- bateria e timbres
def kick(d=0.4):
    t = t_(d)
    f = 45 + 110 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(d, 0.001, 0.12)


def snare(d=0.25):
    t = t_(d)
    return (bp_fft(ruido(d), 1200, 8000) * env(d, 0.001, 0.05) * 0.7 + np.sin(2 * np.pi * 190 * t)
            * env(d, 0.001, 0.03) * 0.4)


def clap(d=0.3):
    out = np.zeros(int(d * SR))
    for k in range(3):
        add(out, bp_fft(ruido(0.02), 1000, 6000) * env(0.02, 0.0005, 0.006), k * 0.011, 0.7)
    add(out, bp_fft(ruido(d), 1000, 6000) * env(d, 0.001, 0.06), 0.03, 0.6)
    return out


def chimbal(d=0.05, aberto=False):
    d = 0.22 if aberto else d
    return hp_fft(ruido(d), 7000) * env(d, 0.0005, 0.08 if aberto else 0.012)


def vassourinha(d=0.25):
    """Vassourinha de jazz na caixa: chiado macio."""
    return bp_fft(ruido(d), 2000, 9000) * env(d, 0.03, 0.08) * 0.35


def baixo(f, d):
    t = t_(d)
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)
    return s * env(d, 0.005, d * 0.6)


def rhodes(f, d):
    """Piano elétrico: seno + tine com tremolo leve."""
    t = t_(d)
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 6)
    s += 0.12 * np.sin(2 * np.pi * 7 * f * t) * np.exp(-t * 25)
    return s * env(d, 0.004, d * 0.7) * (1 + 0.15 * np.sin(2 * np.pi * 5 * t))


def sintetizador(f, d):
    """Lead brilhante (dente de serra suavizada) para o pop do vídeo 1."""
    t = t_(d)
    s = sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, 7))
    return s * env(d, 0.01, d * 0.5) * 0.35


def acorde(notas, d, timbre):
    return sum(timbre(hz(n), d) for n in notas) / len(notas)


# ---------------------------------------------------------------- músicas
def musica_pop(dur, ini, bpm=118):
    """Vídeo 1: começa em `ini` (o estouro do vidro). Batida reta, palmas no 2 e 4, baixo e acordes brilhantes."""
    out = np.zeros(int(dur * SR) + SR)
    b = 60 / bpm
    prog = [["A3", "C#4", "E4"], ["F#3", "A3", "C#4"], ["D3", "F#3", "A3"], ["E3", "G#3", "B3"]]
    raiz = ["A1", "F#1", "D2", "E2"]
    n = int((dur - ini) / b) + 1
    for k in range(n):
        t = ini + k * b
        add(out, kick(), t, 0.9)
        if k % 2 == 1:
            add(out, clap(), t, 0.5)
        add(out, chimbal(), t + b / 2, 0.25)
        add(out, chimbal(aberto=True), t + b / 2, 0.08)
        c = (k // 4) % 4
        add(out, baixo(hz(raiz[c]), b * 0.9), t, 0.55)
        add(out, baixo(hz(raiz[c]) * 2, b * 0.4), t + b / 2, 0.25)
        if k % 4 == 0:
            add(out, acorde(prog[c], b * 3.8, sintetizador), t, 0.45)
    return out[:int(dur * SR)]


def musica_cafe(dur, bpm=92):
    """Vídeo 2: lounge de café (piano elétrico, contrabaixo andando, vassourinha + aro)."""
    out = np.zeros(int(dur * SR) + SR)
    b = 60 / bpm
    prog = [["D4", "F4", "A4", "C5"], ["G3", "B3", "D4", "F4"], ["C4", "E4", "G4", "B4"], ["A3", "C#4", "E4", "G4"]]
    andando = [["D2", "F2", "A2", "C3"], ["G2", "B2", "D3", "F3"], ["C2", "E2", "G2", "B2"], ["A2", "C#3", "E3", "G3"]]
    n = int(dur / b) + 1
    for k in range(n):
        t = k * b
        c = (k // 4) % 4
        add(out, baixo(hz(andando[c][k % 4]), b * 0.95), t, 0.5)
        add(out, vassourinha(), t, 0.5)
        if k % 2 == 1:
            add(out, snare(0.12) * 0.4, t, 0.35)
        add(out, chimbal(0.04), t + b * 0.66, 0.12)
        if k % 4 == 0:
            add(out, acorde(prog[c], b * 2.2, rhodes), t, 0.5)
        if k % 4 == 2:
            add(out, acorde(prog[c], b * 1.5, rhodes), t + b * 0.5, 0.35)
    return out[:int(dur * SR)]


def musica_relogio(dur, marcos):
    """Vídeo 3: o tique-taque É a percussão; a batida acelera conforme o relógio corre.
    marcos = [(t, bpm)]: bpm interpolado no tempo."""
    out = np.zeros(int(dur * SR) + SR)
    ts = np.array([m[0] for m in marcos])
    bs = np.array([m[1] for m in marcos])
    t, k = 0.0, 0
    raiz = ["E2", "C2", "G2", "D2"]
    while t < dur:
        bpm = np.interp(t, ts, bs)
        b = 60 / bpm
        add(out, tic(k % 2 == 0), t, 0.55)
        if k % 4 == 0:
            add(out, kick(), t, 0.85)
        if k % 4 == 2:
            add(out, snare(), t, 0.4)
        if k % 2 == 0:
            add(out, baixo(hz(raiz[(k // 8) % 4]), b * 1.8), t, 0.45)
        add(out, chimbal(), t + b / 2, 0.18)
        t += b
        k += 1
    return out[:int(dur * SR)]


# ---------------------------------------------------------------- mixagem
def grava(path, dur, eventos, musica=None, musica_ganho=0.5, fx_ganho=0.8):
    """eventos = [(t, array, ganho)]. musica = array já no tamanho. Grava wav estéreo 16 bits."""
    n = int(dur * SR)
    fx = np.zeros(n)
    for t, s, g in eventos:
        add(fx, s, t, g)
    mix = fx * fx_ganho
    if musica is not None:
        m = musica[:n]
        m = np.pad(m, (0, n - len(m)))
        mix = mix + m / (np.abs(m).max() + 1e-9) * musica_ganho
    mix = np.tanh(mix * 0.9) / np.tanh(0.9)
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.7
    fade = int(0.04 * SR)
    mix[:fade] *= np.linspace(0, 1, fade)
    st = np.repeat((mix * 32767).astype(np.int16)[:, None], 2, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(st.tobytes())
