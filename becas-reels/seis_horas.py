#!/usr/bin/env python3
"""Reels 3 do Becas: 6 HORAS EM 30 SEGUNDOS (3/nov/2026). A tarde inteira de jogos (13h–19h) passando num relógio de
placar no alto, com as cenas REAIS de jogo na mesa deles (Take Time, Sushi Go!, Critter Kitchen, Canvas, Art Society,
Passaporte Mundo, Unlock!, Sky Team) e uma etiqueta por horário. O tique-taque É a percussão e acelera junto com o
relógio; às 19h toca o despertador ("JÁ ACABOU?!") e entra o convite com os guarda-chuvinhas do Becas.

    /usr/bin/python3 seis_horas.py --frame 0.8 3 7 12 17 21.5 24 27   # out/frames_horas.jpg
    /usr/bin/python3 seis_horas.py                                     # out/horas_{com_som,para_musica}_final.mp4
"""
import math
import os
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

import kit as K
import sons as S
from kit import W, H, FPS, E, MAR, PET, LAR, AMA, BR, ROSA, ease

sys.path.insert(0, K.ROOT)
import tarde  # noqa: E402

# (clipe, t0, duração na tela, velocidade, hora alvo em minutos desde 13h, etiqueta)
SEG = [("taketime2", 3.0, 2.5, 1.0, 0, "CHEGOU, ESCOLHEU A MESA"),
       ("taketime", 18.0, 2.3, 1.2, 15, "A GENTE ENSINA O JOGO"),
       ("sushi", 0.4, 2.1, 1.0, 60, "1ª RODADA: SUSHI GO!"),
       ("critter", 0.3, 2.1, 1.0, 100, "O CRITTER KITCHEN VIROU BAGUNÇA"),
       ("canvas", 1.4, 1.9, 1.0, 140, "MONTANDO QUADROS NO CANVAS"),
       ("art", 0.6, 1.9, 1.0, 180, "LEILÃO NO ART SOCIETY"),
       ("passaporte", 1.0, 1.7, 1.0, 225, "VOLTA AO MUNDO NO PASSAPORTE"),
       ("unlock", 0.8, 1.7, 1.0, 270, "FUGINDO DA SALA NO UNLOCK!"),
       ("sky_dados", 3.5, 1.6, 1.0, 315, "POUSANDO O AVIÃO NO SKY TEAM"),
       ("sky_painel", 2.5, 1.6, 1.0, 359, "18h59: \"SÓ MAIS UMA?\"")]
INI = [0.0]
for s in SEG:
    INI.append(INI[-1] + s[2])
ALARME = INI[-1]          # 19:00 em ponto
CTA = ALARME + 1.5
DUR = CTA + 6.4
ROLA = 0.45               # o relógio corre até a hora nova nos primeiros 0,45 s de cada cena


def trechos():
    out = [(c, t0, d + 0.05, v) for c, t0, d, v, _, _ in SEG]
    out.append(("sky_painel", 2.5 + 1.6, 1.6, 0.4))           # quadro "congelado" no despertador
    out.append(("taketime2", 9.0, DUR - CTA + 0.1, 0.5))      # fundo do convite
    return out


def minutos(t):
    """Minutos desde 13h no tempo t do vídeo."""
    if t >= ALARME:
        return 360
    k = max(i for i in range(len(SEG)) if INI[i] <= t)
    alvo = SEG[k][4]
    antes = SEG[k - 1][4] if k else -1
    u = t - INI[k]
    if k == 0:
        return 0
    if u < ROLA:
        return antes + (alvo - antes) * ease(u / ROLA)
    return alvo


@lru_cache(None)
def placar(hh, mm, vermelho=False):
    w, h = 560, 230
    c = E.bloco(w, h, MAR, raio=36, ow=8, sombra=12).copy()
    d = ImageDraw.Draw(c)
    d.text((w / 2, 46), "SÁBADO NO BECAS", font=E.lilita(36), fill=(255, 220, 160), anchor="mm")
    cor = (235, 70, 60) if vermelho else AMA
    # dígitos em "plaquinhas" de placar
    txt = f"{hh:02d}:{mm:02d}"
    x = 64
    for ch in txt:
        if ch == ":":
            d.text((x + 14, 142), ":", font=E.lilita(130), fill=cor, anchor="mm")
            x += 30
            continue
        d.rounded_rectangle((x, 82, x + 92, 202), 14, fill=(92, 58, 36))
        d.line((x + 2, 142, x + 90, 142), fill=(60, 36, 20), width=3)
        d.text((x + 46, 144), ch, font=E.lilita(118), fill=cor, anchor="mm")
        x += 102
    return c


def barra(img, frac):
    """Linha do tempo 13h → 19h embaixo do placar."""
    d = ImageDraw.Draw(img)
    x0, x1, y = 170, 910, 430
    d.rounded_rectangle((x0 - 6, y - 16, x1 + 6, y + 16), 16, fill=MAR)
    d.rounded_rectangle((x0, y - 10, x0 + (x1 - x0) * frac, y + 10), 10, fill=LAR)
    for k, hh in enumerate(range(13, 20)):
        x = x0 + (x1 - x0) * k / 6
        d.text((x, y + 40), f"{hh}h", font=E.lilita(30), fill=BR, anchor="mm", stroke_width=4, stroke_fill=MAR)


def relogio(img, t):
    m = minutos(t)
    hh, mm = 13 + int(m) // 60, int(m) % 60
    vermelho = t >= ALARME
    tremor = 6 * math.sin(t * 90) if ALARME <= t < CTA else 0
    E.cola(img, placar(hh, mm, vermelho), W / 2 + tremor, 250, 0)
    barra(img, m / 360)


def borrao(img, q):
    """Chicote horizontal (q = 1 → borrão forte)."""
    f = max(1, int(1 + 18 * q))
    return img.resize((W // f, H), Image.BILINEAR).resize((W, H), Image.BILINEAR)


def cena(t):
    k = max(i for i in range(len(SEG)) if INI[i] <= t)
    c, t0, d, v, _, txt = SEG[k]
    u = t - INI[k]
    img = K.quadro_clip(c, t0, d + 0.05, v, u)
    if k and u < 3 / FPS:
        img = borrao(img, 1 - u * FPS / 3)
    K.escurece(img, 0, 560, 170)
    K.escurece(img, 1280, 1640, 130)
    relogio(img, t)
    K.poe(img, K.etiqueta(txt, 46, (AMA, BR, LAR, ROSA)[k % 4], MAR if k % 4 < 2 else BR), W / 2, 1460, u, 0.25,
          (-2, 2, -1.5, 1.5)[k % 4], d=0.22)
    if k == 0:  # gancho
        K.poe(img, K.titulo("6 HORAS DE JOGO\nEM 30 SEGUNDOS", 112, BR), W / 2, 900, t, 0.05, -2)
    K.marca(img)
    return img


def alarme(t):
    u = t - ALARME
    img = K.quadro_clip("sky_painel", 4.1, 1.6, 0.4, u)
    pisca = int(u * 8) % 2 == 0
    img.alpha_composite(Image.new("RGBA", (W, H), (200, 30, 20, 70 if pisca else 25)))
    K.escurece(img, 0, 560, 170)
    relogio(img, t)
    K.poe(img, K.titulo("19H?!\nJÁ ACABOU?!", 150, AMA), W / 2, 960, u, 0.1, -3)
    K.marca(img)
    return img


def final(t):
    u = t - CTA
    img = K.desfoca(K.quadro_clip("taketime2", 9.0, DUR - CTA + 0.1, 0.5, u), 14)
    img.alpha_composite(Image.new("RGBA", (W, H), (40, 24, 12, 120)))
    tarde.guarda_chuvas(img, u)
    K.poe(img, K.logo(230), W / 2, 520, u, 0.3)
    K.poe(img, K.card_cta(), W / 2, 960, u, 0.55, 1.5, d=0.35)
    K.poe(img, E.texto("Comenta: que horas você chegaria?", 46, BR, 800), W / 2, 1390, u, 1.4)
    return img


def quadro(t):
    if t < ALARME:
        img = cena(t)
    elif t < CTA:
        img = alarme(t)
    else:
        img = final(t)
    return img.convert("RGB")


def render(fi):
    return quadro(fi / FPS).tobytes()


def audio(path_com, path_sem):
    ev = []
    for k in range(1, len(SEG)):
        ev += [(INI[k] - 0.05, S.sopro(0.35), 0.7), (INI[k], S.obturador(), 0.6)]
        n = int(ROLA / 0.04)
        ev += [(INI[k] + j * 0.04, S.tique(), 0.18) for j in range(n)]  # dígitos girando
    ev += [(0.05, S.cartao(), 0.6), (ALARME, S.despertador(), 0.9), (ALARME + 0.1, S.cartao(), 0.6)]
    ev += [(CTA, S.sopro(0.6, False), 0.6), (CTA + 0.55, S.cartao(), 0.6)]
    ev += [(CTA + 0.08 * k + 0.4, S.louca(1800 + 120 * k), 0.25) for k in range(6)]
    mus = S.musica_relogio(DUR, [(0, 96), (ALARME, 150), (ALARME + 0.01, 92), (DUR, 92)])
    i0, i1 = int(ALARME * S.SR), int(CTA * S.SR)
    mus[i0:i1] = 0  # silêncio no despertador
    j = int(0.5 * S.SR)
    mus[i1:i1 + j] *= np.linspace(0, 1, j)
    S.grava(path_com, DUR, ev, mus, musica_ganho=0.5, fx_ganho=0.8)
    S.grava(path_sem, DUR, ev, None, fx_ganho=0.8)


def main():
    os.makedirs(K.OUT, exist_ok=True)
    K.prepara(trechos())
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:]]
        K.folha([quadro(x) for x in ts], os.path.join(K.OUT, "frames_horas.jpg"))
        print("ok", round(DUR, 2))
        return
    com, sem = os.path.join(K.OUT, "horas_com.wav"), os.path.join(K.OUT, "horas_sem.wav")
    audio(com, sem)
    K.entrega("horas", DUR, render, com, sem)


if __name__ == "__main__":
    main()
