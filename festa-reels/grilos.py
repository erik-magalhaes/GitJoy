#!/usr/bin/env python3
"""Reels 2: O SILÊNCIO DA FESTA (CRI CRI) — sem narração; o humor vem do som e do contraste.

Tela escura "A CONFRATERNIZAÇÃO DEPOIS DO AMIGO SECRETO:", legendas de som entre colchetes (closed caption) aparecendo
uma a uma ([grilos], [alguém tosse], [garfo raspando no prato]...) e um medidor de ANIMAÇÃO quase zerado; dado rolando →
"...ATÉ ALGUÉM CHAMAR A SUA VEZ" → cortes secos na batida com as cenas REAIS deles jogando, legendas de som felizes e o
medidor subindo até 100% → "a gente leva os jogos e fica o evento todo ensinando" → cartão final.

    python3 grilos.py --frame 1 4 7 8.5 11 15 18 22
    python3 grilos.py
"""
import argparse
import math
import os
import random
import sys
import wave
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import comum_festa as C  # noqa: E402
from comum_festa import W, H, FPS, E  # noqa: E402
import previsao as P  # noqa: E402  (fontes e utilitários)
from previsao import anton, gro, ease, quebra  # noqa: E402
sys.path.insert(0, os.path.join(C.REPO, "comum"))
from motor import out_back  # noqa: E402
import sons as S  # noqa: E402

SR = 44100
T_VIRA, T_CORTES = 6.9, 7.8
SILENCIO = [(0.7, "[grilos]"), (1.9, "[alguém tosse]"), (3.1, "[garfo raspando no prato]"),
            (4.3, "[alguém: “e o trabalho?”]"), (5.5, "[silêncio constrangedor]")]
CORTES = [("unlock", 1.0, "[“NÃO ACREDITO!”]"), ("sushi", 1.0, "[risada]"), ("canvas", 1.4, "[“minha vez! minha vez!”]"),
          ("sky_dados", 3.0, "[todo mundo junto]"), ("taketime", 18.0, "[“só mais uma partida!”]"),
          ("passaporte", 3.4, "[ninguém no celular]")]
DC = 1.4  # duração de cada corte
T_FIM_CORTES = T_CORTES + DC * len(CORTES)
T_CTA = T_FIM_CORTES + 3.2
DUR = T_CTA + 5.6
AMA, BR, VERM = (255, 205, 40), (255, 255, 255), (220, 50, 50)
PET, LAR = (28, 124, 150), (244, 136, 37)


@lru_cache(None)
def escuro():
    y = np.linspace(-1, 1, H)[:, None]
    x = np.linspace(-1, 1, W)[None, :]
    v = np.clip(1 - (x ** 2 * 0.8 + y ** 2 * 0.5), 0, 1) ** 1.5
    a = (10 + 22 * v)[..., None] * np.array([1.0, 1.0, 1.25])
    return Image.fromarray(a.astype(np.uint8)).convert("RGBA")


def medidor(img, cx, cy, r, val, rotulo=True):
    """Medidor de ANIMAÇÃO (meia-lua vermelho → verde) com ponteiro."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    n = 40
    for k in range(n):
        a0 = 180 + k * 180 / n
        f = k / (n - 1)
        cor = (int(230 - 180 * f), int(60 + 160 * f), 60, 255)
        d.arc((cx - r, cy - r, cx + r, cy + r), a0, a0 + 180 / n + 0.5, fill=cor, width=int(r * 0.22))
    ang = math.radians(180 + 180 * val)
    d.line((cx, cy, cx + r * 0.82 * math.cos(ang), cy + r * 0.82 * math.sin(ang)), fill=BR + (255,), width=10)
    d.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), fill=BR + (255,))
    if rotulo:
        d.text((cx, cy + 60), f"ANIMAÇÃO: {int(round(val * 100))}%", font=anton(int(r * 0.32)), fill=BR + (255,),
               anchor="mm")
    img.alpha_composite(lay)


def cc(img, txt, y, a=1.0, cor=BR, tam=58):
    """Legenda de som (closed caption)."""
    if a <= 0:
        return
    f = gro(tam, 700)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    linhas = quebra(txt, f, 920)
    for i, ln in enumerate(linhas):
        tw = d.textlength(ln, font=f)
        yy = y + i * (tam + 22)
        d.rectangle((W / 2 - tw / 2 - 20, yy - tam / 2 - 10, W / 2 + tw / 2 + 20, yy + tam / 2 + 12), fill=(0, 0, 0, 220))
        d.text((W / 2, yy), ln, font=f, fill=cor + (255,), anchor="mm")
    if a < 1:
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    img.alpha_composite(lay)


def relogio(img, t, cor=(170, 170, 180)):
    d = ImageDraw.Draw(img)
    s = 3 + int(t)
    d.text((60, 120), f"21:47:{s:02d}", font=gro(40, 600), fill=cor)


def cena_silencio(t):
    img = escuro().copy()
    d = ImageDraw.Draw(img)
    d.text((W / 2, 400), "A CONFRATERNIZAÇÃO", font=anton(96), fill=BR, anchor="mm")
    d.text((W / 2, 510), "DEPOIS DO AMIGO SECRETO:", font=anton(76), fill=(200, 200, 210), anchor="mm")
    relogio(img, t)
    vis = [s for t0, s in SILENCIO if t >= t0]
    for i, s in enumerate(vis[-3:]):  # empilha as 3 últimas, as antigas mais apagadas
        idade = len(vis[-3:]) - 1 - i
        t0 = [a for a, b in SILENCIO if b == s][0]
        cc(img, s, 740 + i * 160, ease((t - t0) / 0.25) * (1.0 - 0.35 * idade), BR, 54)
    val = 0.04 + 0.02 * math.sin(t * 3.1)
    medidor(img, W // 2, 1400, 220, val)
    return img


def cena_vira(t):
    u = t - T_VIRA
    img = escuro().copy()
    a = ease(u / 0.25)
    d = ImageDraw.Draw(img)
    d.text((W / 2, 820), "...ATÉ ALGUÉM", font=anton(110), fill=BR, anchor="mm")
    d.text((W / 2, 950), "CHAMAR A SUA VEZ", font=anton(110), fill=AMA, anchor="mm")
    E.cola(img, C.kit.logo(320), W // 2, 1230, 0, out_back(a), 1)
    return img


def cena_cortes(t):
    u = t - T_CORTES
    i = min(len(CORTES) - 1, int(u / DC))
    nome, t0, rot = CORTES[i]
    uu = u - i * DC
    q = C.clip(nome, t0, DC, uu)
    z = 1.06 - 0.06 * ease(uu / DC)  # zoom que abre
    img = q.resize((int(W * z), int(H * z)))
    ox, oy = (img.width - W) // 2, (img.height - H) // 2
    img = img.crop((ox, oy, ox + W, oy + H))
    P.legenda  # (sem legenda de fala aqui)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(lay).rectangle((0, 0, W, 330), fill=(0, 0, 0, 90))
    img.alpha_composite(lay)
    cc(img, rot, 1430, ease(uu / 0.15), AMA, 58)
    val = min(1.0, 0.1 + 0.9 * (u + 0.4) / (DC * len(CORTES)))
    medidor(img, 860, 300, 120, val)
    if uu < 0.1:
        img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(230 * (1 - uu / 0.1)))))
    C.kit.marca(img)
    return img


CONF = [(random.Random(i).uniform(0, W), random.Random(i + 50).uniform(-H, 0), random.Random(i + 9).choice(
    [AMA, LAR, PET, (230, 70, 120), (90, 200, 120)]), random.Random(i + 3).uniform(0, 6.28)) for i in range(90)]


def confete(img, u):
    d = ImageDraw.Draw(img)
    for x, y0, cor, f in CONF:
        y = y0 + u * 900
        if 0 <= y <= H:
            xx = x + 30 * math.sin(u * 3 + f)
            w = 14 * abs(math.cos(u * 6 + f)) + 3
            d.rectangle((xx - w, y - 8, xx + w, y + 8), fill=cor)


def cena_cem(t):
    u = t - T_FIM_CORTES
    img = Image.new("RGBA", (W, H), PET + (255,))
    confete(img, u)
    medidor(img, W // 2, 760, 300, 1.0, rotulo=False)
    d = ImageDraw.Draw(img)
    d.text((W / 2, 880), "ANIMAÇÃO: 100%", font=anton(110), fill=AMA, anchor="mm")
    a = ease((u - 0.5) / 0.3)
    if a > 0:
        c = Image.new("RGBA", (940, 300), (0, 0, 0, 0))
        dc = ImageDraw.Draw(c)
        dc.rounded_rectangle((0, 0, 939, 299), 30, fill=(255, 255, 255, 245))
        dc.text((470, 80), "A GENTE LEVA OS JOGOS", font=anton(70), fill=PET, anchor="mm")
        dc.text((470, 170), "e fica o evento todo", font=gro(50, 700), fill=(40, 40, 50), anchor="mm")
        dc.text((470, 230), "ensinando a jogar", font=gro(50, 700), fill=(40, 40, 50), anchor="mm")
        E.cola(img, c, W // 2, 1180, -2, out_back(a), 1)
    C.kit.marca(img)
    return img


def cena_cta(t):
    u = t - T_CTA
    img = Image.new("RGBA", (W, H), PET + (255,))
    confete(img, u + 3.2)
    d = ImageDraw.Draw(img)
    lg = C.kit.logo(300)
    img.alpha_composite(lg, (W // 2 - lg.width // 2, 230))
    d.text((W / 2, 610), "LEVA A SUA VEZ", font=anton(120), fill=BR, anchor="mm")
    d.text((W / 2, 730), "PRO SEU EVENTO", font=anton(120), fill=AMA, anchor="mm")
    for i, s in enumerate(["AMIGO SECRETO", "FIRMA", "FAMÍLIA", "ANIVERSÁRIO"]):
        a = ease((u - 0.2 - 0.15 * i) / 0.25)
        p = E.pilula(s, 40, BR, PET)
        E.cola(img, p, (300, 780, 300, 780)[i], (880, 880, 990, 990)[i], (-3, 2, 2, -3)[i], out_back(a), 1)
    d.text((W / 2, 1120), "ABC PAULISTA E SÃO PAULO CAPITAL", font=gro(46, 800), fill=BR, anchor="mm")
    d.rounded_rectangle((90, 1180, W - 90, 1290), 30, fill=(30, 160, 80))
    d.text((W / 2, 1235), f"ORÇAMENTO: WHATSAPP {C.WHATS}", font=gro(46, 800), fill=BR, anchor="mm")
    b = ease((u - 0.9) / 0.3)
    if b > 0:
        p = E.pilula("COMENTA: QUAL EVENTO SEU PRECISAVA DE JOGOS?", 36, AMA, (40, 30, 20))
        E.cola(img, p, W // 2, 1400, -2, out_back(b), 1)
    return img


def frame(fi):
    t = fi / FPS
    if t < T_VIRA:
        img = cena_silencio(t)
    elif t < T_CORTES:
        img = cena_vira(t)
    elif t < T_FIM_CORTES:
        img = cena_cortes(t)
    elif t < T_CTA:
        img = cena_cem(t)
    else:
        img = cena_cta(t)
    return img.convert("RGB")


def render(fi):
    return frame(fi).tobytes()


# ---------------------------------------------------------------- som
def grilos(dur):
    t = np.arange(int(dur * SR)) / SR
    out = np.zeros_like(t)
    for f0, ritmo, fase in ((4300, 2.1, 0.0), (4700, 2.6, 0.7), (3900, 1.7, 1.9)):
        trem = (np.sin(2 * np.pi * 28 * t) > 0.2).astype(float)  # chilreio (pulsos rápidos)
        janela = (np.sin(2 * np.pi * ritmo * t + fase) > 0.55).astype(float)
        out += np.sin(2 * np.pi * f0 * t) * trem * janela
    return np.convolve(out, np.ones(30) / 30, "same") * 0.25


def tosse():
    d = 0.45
    o = np.zeros(int(d * SR))
    for k, t0 in enumerate((0.0, 0.2)):
        r = S.bp_fft(S.ruido(0.16), 300, 2500) * S.env(0.16, 0.005, 0.1)
        S.add(o, r, t0, 0.9 - 0.3 * k)
    return o


def garfo():
    d = 0.7
    t = S.t_(d)
    f = 2800 + 900 * np.sin(2 * np.pi * 1.5 * t)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.5 + 0.5 * np.sin(2 * np.pi * 9 * t))
    return (s * 0.3 + S.hp_fft(S.ruido(d), 3000) * 0.4) * S.env(d, 0.05, 0.2)


def audio():
    n = int(DUR * SR)
    fx = np.zeros(n)
    S.add(fx, grilos(T_VIRA), 0.0, 0.5)
    S.add(fx, tosse(), 1.9, 0.6)
    S.add(fx, garfo(), 3.1, 0.35)
    S.add(fx, S.dado(), T_VIRA - 0.1, 1.0)
    S.add(fx, S.estouro(), T_CORTES - 0.02, 0.6)
    for i in range(len(CORTES)):
        S.add(fx, S.whoosh(0.25) if hasattr(S, "whoosh") else S.sopro(0.25), T_CORTES + i * DC - 0.1, 0.3)
    S.add(fx, S.plim(), T_FIM_CORTES + 0.1, 0.6)
    S.add(fx, S.sino(), T_CTA, 0.4)
    mus = S.musica_pop(DUR, T_CORTES)
    os.makedirs(C.OUT, exist_ok=True)
    com, sem = os.path.join(C.OUT, "gri_com.wav"), os.path.join(C.OUT, "gri_sem.wav")
    S.grava(com, DUR, [(0, fx, 1.0)], mus, musica_ganho=0.5, fx_ganho=0.9)
    S.grava(sem, DUR, [(0, fx, 1.0)], None, fx_ganho=0.9)
    return com, sem


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", nargs="*", type=float)
    a = ap.parse_args()
    C.prepara([(n, t0, DC) for n, t0, _ in CORTES])
    if a.frame:
        C.folha([frame(int(x * FPS)) for x in a.frame], os.path.join(C.OUT, "frames_gri.jpg"))
        print("DUR", round(DUR, 2))
        return
    com, sem = audio()
    C.entrega("silencio", DUR, render, com, sem)
    print(C.chat(os.path.join(C.OUT, "silencio_com_som_final.mp4")))
    print(C.chat(os.path.join(C.OUT, "silencio_para_musica_final.mp4")))


if __name__ == "__main__":
    main()
