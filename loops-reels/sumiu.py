#!/usr/bin/env python3
"""Reels em LOOP "QUAL CAIXA SUMIU?" (1/nov/2026, ideia 1 da lista de vídeos que dão replay; ele escolheu 1 e 6).
Estante de madeira com 9 caixas do acervo por ~3,6 s ("DECORA!" com barrinha de tempo) → flash → a mesma estante com
UMA caixa a menos ("QUAL SUMIU? COMENTA!"). Quando o vídeo recomeça a caixa volta: a resposta está no começo do loop,
então a pessoa assiste de novo para conferir. Sem narração; _com_trilha e _para_musica (−15,5 LUFS).

    python3 sumiu.py --frame 0 2 3.7 5
    python3 sumiu.py
"""
import argparse
import math
import os
import random
import sys
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter

import comum_loop as C
from motor import W, H, FPS, WHITE, logo_card, cola, sombra, letreiro, pilula, folha  # noqa: E402

AC = os.path.join(C.REPO, "hobby-reels", "assets", "acervo")
CAIXAS = ["echoes_of_time", "treasure_island", "encantados", "savernake_forest", "c_atl", "metro",
          "dice_colony", "sideral_fus_o_gal_ctica", "world_wonders"]
SUMIU = 5  # metro (fileira do meio, à direita)
DUR = 7.0
T_SOME = 3.6   # o flash
INK = (40, 26, 18)
AMAR = (255, 199, 31)
PRAT = [760, 1105, 1450]  # y do tampo de cada prateleira
XS = [205, 540, 875]


@lru_cache(None)
def caixa(n):
    im = Image.open(os.path.join(AC, n + ".png")).convert("RGBA")
    im = im.crop(im.getbbox())
    s = min(270 / im.height, 270 / im.width)
    return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)


@lru_cache(None)
def estante():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    for y in range(H):  # parede verde-petróleo escura com luz no meio
        u = abs(y - 1050) / 1100
        d.line((0, y, W, y), fill=(int(30 - 12 * u), int(74 - 30 * u), int(84 - 32 * u)))
    luz = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(luz).ellipse((60, 420, 1020, 1640), fill=(255, 220, 160, 55))
    img.alpha_composite(luz.filter(ImageFilter.GaussianBlur(160)))
    d = ImageDraw.Draw(img)
    # laterais e fundo da estante
    d.rectangle((40, 400, 1040, 1520), fill=(70, 44, 26))
    d.rectangle((62, 420, 1018, 1498), fill=(96, 62, 38))
    rnd = random.Random(3)
    for k in range(70):  # veios da madeira do fundo
        y = rnd.uniform(420, 1498)
        d.line((62, y, 1018, y + rnd.uniform(-6, 6)), fill=(88, 56, 34), width=2)
    for y in PRAT:  # tampos
        d.rectangle((40, y, 1040, y + 34), fill=(150, 98, 58))
        d.rectangle((40, y, 1040, y + 7), fill=(186, 128, 80))
        d.rectangle((40, y + 34, 1040, y + 46), fill=(52, 32, 18))
    return img


def prateleira(sem=None):
    img = estante().copy()
    for k, n in enumerate(CAIXAS):
        if k == sem:
            continue
        im = caixa(n)
        x, y = XS[k % 3], PRAT[k // 3]
        sh = sombra(im, 10, (6, 8), 0.55)
        img.alpha_composite(sh, (int(x - im.width / 2 - 20), int(y - im.height - 20 + 4)))
        img.alpha_composite(im, (int(x - im.width / 2), int(y - im.height + 4)))
    return img


@lru_cache(None)
def cheia():
    return prateleira()


@lru_cache(None)
def faltando():
    return prateleira(SUMIU)


def frame(fi):
    t = fi / FPS
    if t < T_SOME:
        img = cheia().copy()
        cola(img, letreiro("QUAL CAIXA\nVAI SUMIR?", 88, AMAR, INK, 11, sombra_px=7, cor_sombra=INK), 540, 200, -2)
        cola(img, pilula("DECORA!", 44, (230, 70, 110)), 540, 345, 1, 1 + 0.05 * math.sin(t * 8))
        u = 1 - t / T_SOME  # barrinha de tempo
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((190, 1585, 890, 1615), radius=15, fill=(20, 40, 46))
        d.rounded_rectangle((190, 1585, 190 + 700 * u, 1615), radius=15, fill=AMAR)
    else:
        img = faltando().copy()
        cola(img, letreiro("QUAL CAIXA\nSUMIU?", 88, AMAR, INK, 11, sombra_px=7, cor_sombra=INK), 540, 200, -2)
        b = 1 + 0.05 * abs(math.sin((t - T_SOME) * 5))
        cola(img, pilula("COMENTA AQUI!", 44, (244, 136, 37)), 540, 345, 1, b)
        x, y = XS[SUMIU % 3], PRAT[SUMIU // 3]
        cola(img, letreiro("?", 150, WHITE, INK, 9), x, y - 140, 0, b)
        cola(img, pilula("ALUGA NA SUA VEZ · LINK NA BIO", 34, (22, 150, 90)), 540, 1600, 0)
        a = max(0.0, 1 - (t - T_SOME) / 0.2)  # flash branco
        if a > 0:
            img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * a))))
    wm = logo_card(120)
    img.alpha_composite(wm, (W - wm.width - 24, 26))
    return img.convert("RGB")


def render_frame(fi):
    return frame(fi).tobytes()


def cues():
    c = [(k * 0.45, "tick", 0.35) for k in range(int(T_SOME / 0.45))]
    c += [(T_SOME - 0.12, "whoosh", 0.8), (T_SOME, "pop", 0.9)]
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    a = ap.parse_args()
    os.makedirs(C.OUT, exist_ok=True)
    if a.frame:
        folha([frame(int(round(x * FPS))) for x in a.frame], os.path.join(C.OUT, "sumiu_frames.jpg"))
        return
    C.entrega("sumiu", DUR, render_frame, cues())


if __name__ == "__main__":
    main()
