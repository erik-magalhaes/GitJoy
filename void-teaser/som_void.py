"""Trilha e efeitos do teaser VOID (sintetizados em numpy) + mixagem com a narração.

python3 som_void.py -> out/void_audio.wav
"""
import os
import subprocess
import sys
import wave

import numpy as np
from scipy.signal import fftconvolve

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "finalgirl-reels"))
from som_fg import fx_braam, fx_riser, saw  # noqa: E402
from som import SR, add, env, hp, lp, noise, t_, fx_whoosh  # noqa: E402

sys.path.insert(0, HERE)
import teaser as T  # noqa: E402

rng = np.random.default_rng(42)


def reverb(x, seg=2.6, mix=0.3):
    n = int(seg * SR)
    ir = rng.standard_normal(n) * np.exp(-np.arange(n) / SR / (seg / 6))
    ir = lp(ir, 5000)
    ir /= np.sqrt((ir ** 2).sum())
    w = fftconvolve(x, ir)[: len(x)]
    return x * (1 - mix) + w * mix * 2.2


def ler_wav(p):
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True).stdout
    return np.frombuffer(out, np.float32).astype(np.float64)


# ------------------------------------------------------------------ efeitos
def fx_tiro():
    d = 2.5
    t = t_(d)
    crack = hp(noise(d), 1800) * env(d, 0.012, 0.0005) * 2.2
    corpo = lp(noise(d), 900) * env(d, 0.06, 0.001) * 2.0
    boom = np.sin(2 * np.pi * np.cumsum(70 * (1 + 2 * np.exp(-t / 0.02))) / SR) * env(d, 0.18, 0.001) * 1.5
    cauda = lp(noise(d), 600) * np.exp(-t / 0.7) * np.minimum(1, t / 0.05) * 0.35
    return np.tanh((crack + corpo + boom + cauda) * 1.3)


def fx_engatilha():
    out = np.zeros(int(0.5 * SR))
    for k, (f, g) in enumerate(((2400, 0.8), (1700, 1.0))):
        x = hp(noise(0.04), f) * env(0.04, 0.006, 0.0005)
        add(out, x, k * 0.16, g)
    return out


def fx_porta():
    """Rangido de metal + batida do portão."""
    d = 1.8
    t = t_(d)
    f = 180 + 90 * np.sin(2 * np.pi * 1.3 * t) + 40 * rng.standard_normal(len(t)).cumsum() / SR
    rang = saw(f, d) * (0.3 + 0.7 * (np.sin(2 * np.pi * 23 * t) > 0.2))
    rang = hp(lp(rang, 2500), 300) * np.minimum(1, t / 0.2) * np.exp(-t / 1.2) * 0.25
    out = np.zeros(int(2.8 * SR))
    add(out, rang, 0, 1)
    add(out, lp(noise(1.0), 300) * env(1.0, 0.25) * 1.2, 1.55, 1)  # batida grave
    add(out, hp(noise(0.6), 1200) * env(0.6, 0.12) * 0.4, 1.55, 1)
    return out


def fx_tecla():
    return hp(noise(0.03), 2500) * env(0.03, 0.004, 0.0003)


def fx_bip(f=1800, d=0.09):
    t = t_(d)
    return np.sin(2 * np.pi * f * t) * env(d, d / 2.5, 0.002) * 0.4


def fx_lamina():
    """'Shing' metálico."""
    d = 1.6
    t = t_(d)
    parciais = (2350, 3710, 5120, 6930)
    x = sum(np.sin(2 * np.pi * f * t) * np.exp(-t / (0.5 - k * 0.08)) for k, f in enumerate(parciais)) / 4
    raspa = hp(noise(0.35), 3500) * np.minimum(1, t_(0.35) / 0.25) * np.exp(-t_(0.35) / 0.1) * 0.5
    out = np.zeros(len(t))
    add(out, raspa, 0, 1)
    add(out, x * np.minimum(1, t / 0.005), 0.25, 0.6)
    return out


def fx_cravada():
    d = 0.8
    t = t_(d)
    baque = lp(noise(d), 400) * env(d, 0.05) * 1.6
    vib = np.sin(2 * np.pi * 330 * t) * np.sin(2 * np.pi * 21 * t) * env(d, 0.25) * 0.35
    return baque + vib


def fx_passo():
    d = 0.35
    return lp(noise(d), 260) * env(d, 0.05, 0.002) * 1.2 + hp(noise(d), 2500) * env(d, 0.02) * 0.15


def fx_corrente():
    out = np.zeros(int(0.9 * SR))
    for k in range(6):
        t = t_(0.25)
        f = rng.uniform(2800, 4200)
        add(out, np.sin(2 * np.pi * f * t) * env(0.25, 0.05) * 0.3, k * 0.09 + rng.uniform(0, 0.04), 1)
    return out


def fx_couro():
    d = 1.0
    t = t_(d)
    x = np.zeros(len(t))
    for k in range(18):
        pos = int(rng.uniform(0, 0.85) * SR)
        g = lp(hp(noise(0.03), 600), 3000) * env(0.03, 0.01)
        x[pos:pos + len(g)] += g * rng.uniform(0.3, 1)
    return x * 0.6


def fx_zumbido(d):
    """Zumbido elétrico de lâmpada com estalos."""
    t = t_(d)
    x = (np.sign(np.sin(2 * np.pi * 120 * t)) * 0.3 + np.sin(2 * np.pi * 240 * t) * 0.3)
    x = lp(x, 1800) * 0.25
    return x


def fx_estalo():
    return hp(noise(0.05), 1500) * env(0.05, 0.008, 0.0005)


def fx_impacto_final():
    d = 4.5
    t = t_(d)
    sub = np.sin(2 * np.pi * np.cumsum(42 * (1 + 0.8 * np.exp(-t / 0.08))) / SR) * np.exp(-t / 1.4)
    corpo = lp(noise(d), 220) * np.exp(-t / 0.6) * 1.2
    alto = hp(noise(d), 2500) * np.exp(-t / 0.2) * 0.3
    return np.tanh((sub * 1.4 + corpo + alto) * 1.2)


def fx_cidade(d):
    """Murmúrio de multidão + caça-níqueis ao longe."""
    t = t_(d)
    mur = lp(hp(noise(d), 200), 1100) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.3 * t)) * 0.35
    out = mur.copy()
    k = 0.2
    while k < d - 0.5:
        f = rng.choice([1318, 1568, 1760, 2093])
        add(out, np.sin(2 * np.pi * f * t_(0.4)) * env(0.4, 0.12) * 0.08, k, 1)
        k += rng.uniform(0.12, 0.5)
    return out


# ------------------------------------------------------------------ música
def musica(dur):
    n = int(dur * SR)
    t = t_(dur)
    out = np.zeros(n)
    # drone grave (ré menor) que cresce depois da cidade
    cres = np.clip((t - 3.5) / 6, 0, 1)
    drone = np.sin(2 * np.pi * 36.7 * t) + 0.7 * np.sin(2 * np.pi * 73.4 * t) + 0.35 * np.sin(2 * np.pi * 110.0 * t)
    drone = lp(drone + 0.3 * saw(73.6, dur), 300) * (0.75 + 0.25 * np.sin(2 * np.pi * t / 7))
    out += drone * 0.32 * cres
    # cordas graves em ostinato (pulsos de colcheia) a partir do galpão
    bpm = 92
    batida = 60 / bpm
    ini = 14.0
    tt = ini
    k = 0
    notas = [73.4, 73.4, 87.3, 73.4, 65.4, 73.4, 77.8, 73.4]
    while tt < T.APAGA:
        f = notas[k % len(notas)]
        d = batida / 2 * 0.95
        x = saw(f, d) + 0.5 * saw(f * 2.003, d)
        x = lp(x, 700) * env(d, d / 2, 0.01)
        g = 0.10 + 0.08 * min(1, (tt - ini) / 40)
        add(out, x, tt, g)
        tt += batida / 2
        k += 1
    # batidas graves (tímpano) em cada tempo forte, ficam mais densas no final
    tt = ini
    while tt < T.APAGA:
        tp = t_(0.6)
        bum = np.sin(2 * np.pi * np.cumsum(55 * (1 + 0.6 * np.exp(-tp / 0.04))) / SR) * env(0.6, 0.22)
        add(out, bum, tt, 0.35)
        tt += batida * (4 if tt < 58 else 2)
    # nota alta de piano sinistra
    tt = 6.0
    for f in [587.3, 554.4, 587.3, 440.0, 466.2, 440.0, 349.2, 329.6] * 2:
        if tt > T.APAGA - 2:
            break
        tp = t_(3)
        add(out, (np.sin(2 * np.pi * f * tp) + 0.25 * np.sin(2 * np.pi * 2 * f * tp)) * env(3, 1.0), tt, 0.05)
        tt += 4.2
    # tudo para no apagão
    corte = int(T.APAGA * SR)
    out[corte:] = 0
    return out


def mix():
    dur = T.DUR
    n = int(dur * SR)
    m = reverb(musica(dur), 3.0, 0.25)
    fx = np.zeros(n)
    add(fx, fx_cidade(5.0) * np.minimum(1, np.linspace(0, 6, int(5.0 * SR))) * np.linspace(1, 0, int(5.0 * SR)) ** 0.5, 0, 0.8)
    add(fx, fx_whoosh(0.8) * 0.6, 3.8, 0.5)
    add(fx, fx_riser(2.0), 6.4, 0.25)
    add(fx, fx_porta(), 8.2 + 3.4 - 1.55 + 0.2, 0.7)
    add(fx, fx_braam(), 14.0, 0.55)
    add(fx, fx_engatilha(), 20.2, 0.9)
    add(fx, fx_riser(1.4), T.TIRO - 1.4, 0.18)
    add(fx, fx_tiro(), T.TIRO, 1.0)
    add(fx, fx_braam(), 26.7, 0.45)
    t = 26.9
    while t < 31.1:
        add(fx, fx_tecla(), t, rng.uniform(0.25, 0.55))
        t += rng.uniform(0.06, 0.18)
    for k in range(10):
        add(fx, fx_bip(rng.choice([1200, 1600, 2400]), 0.07), 31.4 + k * 0.55 + rng.uniform(0, 0.2), 0.35)
    add(fx, fx_bip(880, 0.25), 33.0, 0.5)
    add(fx, fx_bip(880, 0.25), 33.45, 0.5)
    add(fx, fx_braam(), 37.0, 0.45)
    add(fx, fx_lamina(), 37.0 + 2.2, 0.8)
    add(fx, fx_lamina(), 41.2, 0.4)
    add(fx, fx_whoosh(0.4), 44.6, 0.9)
    add(fx, fx_cravada(), 44.6 + 0.42, 1.0)
    add(fx, fx_braam(), 46.3, 0.5)
    tp = 46.3 + 0.6
    while tp < 50.7:
        add(fx, fx_passo(), tp, 0.8)
        tp += math_pi / 5.2
    add(fx, fx_corrente(), 51.4, 0.8)
    add(fx, fx_corrente(), 53.2, 0.5)
    add(fx, fx_porta()[: int(1.4 * SR)] * 0.4, 50.9, 0.4)
    add(fx, fx_couro(), 55.0, 0.9)
    add(fx, fx_couro(), 56.9, 1.0)
    add(fx, fx_braam(), 59.1, 0.7)
    # zumbido/estalos das lâmpadas piscando no final
    t0 = T.CENAS[-1][1]
    zz = fx_zumbido(T.APAGA - t0)
    nivel = np.zeros(len(zz))
    passo = int(SR / 30)
    ultimo = 1
    for i in range(0, len(zz), passo):
        nv, flash = T.piscar(i / SR)
        v = max(nv)
        nivel[i:i + passo] = v
        if v < 0.5 and ultimo >= 0.5 or flash:
            add(fx, fx_estalo(), t0 + i / SR, 0.5)
        ultimo = v
    add(fx, zz * lp(nivel, 30) * np.clip(np.arange(len(zz)) / SR / 2, 0, 1), t0, 0.5)
    add(fx, fx_riser(3.0), T.APAGA - 3.0, 0.3)
    add(fx, fx_impacto_final(), T.APAGA, 1.0)
    fx = reverb(fx, 1.6, 0.18)

    # narração: graves um pouco mais cheios + ambiência curta
    voz = np.zeros(n)
    if SEM_VOZ:
        total = m * 1.15 + fx * 0.8
    else:
        for i in range(8):
            v = ler_wav(os.path.join(HERE, T.VOZ_DIR, f"t_{i + 1:02d}.wav"))
            add(voz, v, T.INICIO[i], 1.0)
        voz = reverb(voz, 1.2, 0.10)
        tem_voz = lp(np.abs(voz), 8) > 0.01
        duck = 1 - 0.55 * lp(tem_voz.astype(float), 3)
        total = m * duck * 0.9 + fx * 0.8 + voz * 1.0
    total = np.tanh(total * 0.9) / 0.9
    total /= np.abs(total).max() / 0.95
    with wave.open(os.path.join(T.OUT, SAIDA), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((total * 32767).astype(np.int16).tobytes())


math_pi = np.pi
SEM_VOZ = os.environ.get("SEM_VOZ") == "1"
SAIDA = os.environ.get("SAIDA_AUDIO", "void_audio.wav")

if __name__ == "__main__":
    # trata as falas: graves +3 dB, presença, compressão leve, 44,1 kHz
    for i in range(1, 9):
        if SEM_VOZ:
            break
        grave = "3.5" if T.VOZ_DIR == "voz" else "1.0"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(HERE, T.VOZ_DIR, f"c_{i:02d}.wav"), "-af",
                        f"highpass=f=70,equalizer=f=110:t=q:w=1:g={grave},equalizer=f=3000:t=q:w=1.5:g=1.5,"
                        "acompressor=threshold=-20dB:ratio=2.5:attack=8:release=150:makeup=2dB",
                        "-ar", str(SR), "-ac", "1", os.path.join(HERE, T.VOZ_DIR, f"t_{i:02d}.wav")], check=True)
    mix()
    print("ok")
