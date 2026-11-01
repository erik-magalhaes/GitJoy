#!/usr/bin/env python3
"""Reels em LOOP "JOGO DA MEMÓRIA" (1/nov/2026, ideia 6 da lista; ele escolheu 1 e 6). Usa os 12 bichinhos do Gemini
(bichos-reels/assets/gemini_bichos.jpg). As 12 cartas ficam abertas ~2,8 s ("DECORA EM 3 SEGUNDOS!"), viram numa onda,
cada verso com um NÚMERO, e aparece "ONDE ESTAVA O CAMELO? COMENTA O NÚMERO!". No fim as cartas desviram: a resposta
está no começo do loop. Sem narração; _com_trilha e _para_musica (−15,5 LUFS).

    python3 memoria.py --frame 0 1.5 3.0 3.3 5 7.8
    python3 memoria.py
"""
import argparse
import math
import os
from functools import lru_cache

from PIL import Image, ImageDraw

import comum_loop as C
from motor import W, H, FPS, WHITE, font, logo_card, cola, sombra, letreiro, pilula, folha  # noqa: E402
from bichos import arte as _arte_bicho, celulas, GEMINI  # noqa: E402,F401

DUR = 8.0
T_VIRA = 2.8      # começa a virar para o verso
T_DESVIRA = 7.45  # começa a desvirar (termina antes de DUR → o último quadro = o primeiro)
ONDA = 0.035      # atraso entre cartas na onda
GIRO = 0.18       # duração do giro de cada carta
ALVO = 3          # o camelo
NOME_ALVO = "O CAMELO"
INK = (40, 26, 18)
AMAR = (255, 199, 31)
FUNDO = (108, 63, 160)
CW, CH = 222, 296
GX, GY = 24, 22
X0 = (W - (4 * CW + 3 * GX)) / 2 + CW / 2
Y0 = 560


@lru_cache(None)
def face(k):
    im = Image.open(GEMINI).convert("RGB").crop(celulas()[k]).resize((CW - 16, CH - 16), Image.LANCZOS)
    c = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    m = Image.new("L", (CW - 16, CH - 16), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, CW - 17, CH - 17), radius=14, fill=255)
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((0, 0, CW - 1, CH - 1), radius=20, fill=(252, 248, 240), outline=INK, width=5)
    c.paste(im, (8, 8), m)
    return c


@lru_cache(None)
def verso(k):
    c = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((0, 0, CW - 1, CH - 1), radius=20, fill=(28, 124, 150), outline=INK, width=5)
    d.rounded_rectangle((14, 14, CW - 15, CH - 15), radius=12, outline=(120, 200, 220), width=3)
    for y in range(30, CH - 20, 26):  # bolinhas
        for x in range(30 + (13 if (y // 26) % 2 else 0), CW - 20, 26):
            d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(46, 146, 172))
    d.ellipse((CW / 2 - 66, CH / 2 - 66, CW / 2 + 66, CH / 2 + 66), fill=(252, 248, 240), outline=INK, width=5)
    d.text((CW / 2, CH / 2 + 4), str(k + 1), font=font("Bungee-Regular.ttf", 74), fill=INK, anchor="mm")
    return c


def lado(k, t):
    """(imagem, escala horizontal) da carta k no tempo t."""
    def giro(t0):
        u = (t - t0 - k * ONDA) / GIRO
        return min(1.0, max(0.0, u))
    if t < T_DESVIRA:
        u = giro(T_VIRA)  # face → verso
        a, b = face(k), verso(k)
    else:
        u = giro(T_DESVIRA)  # verso → face
        a, b = verso(k), face(k)
    if u < 0.5:
        return a, math.cos(u * math.pi)
    return b, -math.cos(u * math.pi)


def frame(fi):
    t = fi / FPS
    img = Image.new("RGBA", (W, H), FUNDO + (255,))
    d = ImageDraw.Draw(img)
    for y in range(24, H, 48):
        for x in range(24 + (24 if (y // 48) % 2 else 0), W, 48):
            d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(122, 78, 176))
    cola(img, letreiro("JOGO DA\nMEMÓRIA", 96, AMAR, INK, 11, sombra_px=7, cor_sombra=INK), 540, 215, -2)
    abertas = t < T_VIRA + 0.1 or t >= T_DESVIRA + 0.3
    if abertas:
        resta = max(1, math.ceil(T_VIRA - t)) if t < T_VIRA else 3
        cola(img, pilula(f"DECORA! {resta}", 44, (230, 70, 110)), 540, 385, 1)
    else:
        cola(img, pilula("COMENTA O NÚMERO!", 42, (244, 136, 37)), 540, 385, 1,
             1 + 0.05 * abs(math.sin((t - T_VIRA) * 5)))
    for k in range(12):
        x = X0 + (k % 4) * (CW + GX)
        y = Y0 + (k // 4) * (CH + GY)
        im, sx = lado(k, t)
        if sx < 0.02:
            continue
        im2 = im.resize((max(2, int(CW * sx)), CH), Image.BICUBIC) if sx < 0.999 else im
        img.alpha_composite(sombra(im2, 6, (0, 6), 0.35), (int(x - im2.width / 2 - 12), int(y - CH / 2 - 12)))
        img.alpha_composite(im2, (int(x - im2.width / 2), int(y - CH / 2)))
    if not abertas:  # a pergunta, com a carta do alvo pequena
        u = min(1.0, (t - T_VIRA - 0.6) / 0.25)
        if u > 0:
            cola(img, letreiro(f"ONDE ESTAVA\n{NOME_ALVO}?", 64, WHITE, INK, 9), 470, 1540, -1, 0.6 + 0.4 * u)
            mini = face(ALVO).resize((int(CW * 0.62), int(CH * 0.62)), Image.LANCZOS)
            cola(img, mini, 870, 1530, 6, 0.6 + 0.4 * u)
    wm = logo_card(120)
    img.alpha_composite(wm, (W - wm.width - 24, 26))
    return img.convert("RGB")


def render_frame(fi):
    return frame(fi).tobytes()


def cues():
    c = [(T_VIRA - 2.0, "tick", 0.4), (T_VIRA - 1.0, "tick", 0.4)]
    c += [(T_VIRA + k * ONDA * 3, "flip", 0.35) for k in range(4)]
    c += [(T_VIRA + 0.6, "pop", 0.7)]
    c += [(T_DESVIRA + k * ONDA * 3, "flip", 0.35) for k in range(4)]
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    a = ap.parse_args()
    os.makedirs(C.OUT, exist_ok=True)
    if a.frame:
        folha([frame(int(round(x * FPS))) for x in a.frame], os.path.join(C.OUT, "memoria_frames.jpg"))
        return
    C.entrega("memoria", DUR, render_frame, cues())


if __name__ == "__main__":
    main()
