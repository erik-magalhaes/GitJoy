#!/usr/bin/env python3
"""BYE BYE curto (≈12 s) para a trend "bye, bye, Miss American Pie", do jeito que o dono pediu:
o Banco Imobiliário aberto na mesa, passando devagar com cara de antigo, e no "tchan" da música
VIRA para um jogo moderno aberto (Hot Streak, depois Ticket to Ride: Lendas do Oeste), fechando com a Sua Vez.
Sem áudio: a música da trend entra no Instagram. A virada acontece em VIRADA segundos.
(A versão longa com polaroides, byebye.py, foi rejeitada: "ficou horrível".)

    python3 curto.py --frame 1 3.2 6 10    # quadros de teste em out/frames.jpg
    python3 curto.py                       # out/byebye_curto.mp4
"""
import argparse
import math
import os
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "..", "comum"))
from motor import (W, H, FPS, WHITE, seg, ease, lerp, pop, emoji, logo_card, cola, sombra, letreiro, pilula,  # noqa
                   encode, folha)

A = os.path.join(ROOT, "assets")
OUT = os.path.join(ROOT, "out")
HS_FOTO = os.path.join(ROOT, "..", "hotstreak-reels", "assets", "fotos", "HS4751.jpg")
INK = (30, 22, 18)
AMARELO = (255, 214, 70)
VIRADA = 3.0   # o "tchan" da música: troca do jogo antigo para o moderno
TROCA2 = 6.4   # segundo jogo moderno
FIM = 9.4      # tela da Sua Vez
DUR = 12.4


@lru_cache(None)
def mesa(tom=1.0):
    """Mesa de madeira (tábuas com veios), gerada em numpy: limpa, sem ruído."""
    rng = np.random.default_rng(3)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    larg = 230
    tab = (xx // larg).astype(int)
    base = np.array([150, 98, 60], np.float32)
    img = np.zeros((H, W, 3), np.float32)
    off = rng.uniform(0, 100, 20)
    var = rng.uniform(0.88, 1.08, 20)
    veio = np.sin((yy * 0.012 + np.sin(yy * 0.004 + off[tab]) * 3 + (xx % larg) * 0.08) * 2.2)
    veio2 = np.sin(yy * 0.05 + (xx % larg) * 0.31 + off[tab])
    lum = var[tab] * (0.92 + 0.06 * veio + 0.025 * veio2)
    img = base[None, None] * lum[..., None] * tom
    junta = ((xx % larg) < 3)
    img[junta] *= 0.55
    yv = np.linspace(-1, 1, H)[:, None]
    xv = np.linspace(-1, 1, W)[None, :]
    img *= (1 - 0.35 * (xv ** 2 + yv ** 2) ** 1.2)[..., None]  # vinheta suave
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


@lru_cache(None)
def banco_antigo():
    """Banco Imobiliário com cara de 'coisa do passado': cor lavada e quente (sem granulado)."""
    im = Image.open(os.path.join(A, "banco_imobiliario_aberto.png")).convert("RGBA")
    a = im.getchannel("A")
    rgb = ImageEnhance.Color(im.convert("RGB")).enhance(0.35)
    rgb = Image.blend(rgb, Image.new("RGB", rgb.size, (190, 150, 100)), 0.18)
    rgb = ImageEnhance.Contrast(rgb).enhance(0.9)
    out = rgb.convert("RGBA")
    out.putalpha(a)
    return out


@lru_cache(None)
def peca(nome, w):
    im = Image.open(os.path.join(A, nome + ".png")).convert("RGBA")
    return im.resize((int(w), int(im.height * w / im.width)), Image.LANCZOS)


@lru_cache(None)
def hs_foto():
    im = Image.open(HS_FOTO).convert("RGB")
    s = H * 1.12 / im.height
    return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)


def cena_banco(img, t):
    img.alpha_composite(mesa(0.8))
    # tabuleiro passando devagar (câmera deslizando e girando um pouco)
    u = t / VIRADA
    b = banco_antigo()
    w = 1500
    bi = b.resize((w, int(b.height * w / b.width)), Image.LANCZOS)
    cola(img, sombra(bi, 24, (14, 30), 0.5), lerp(640, 440, u), lerp(1020, 960, u), lerp(-14, -6, u), lerp(1.0, 1.12, u))
    escurece = Image.new("RGBA", (W, H), (20, 12, 6, 70))
    img.alpha_composite(escurece)
    cola(img, letreiro("BYE BYE,", 150, WHITE, INK, 12, "AlfaSlabOne-Regular.ttf", 10, INK), 540, 300, -3, pop(t, -0.3))
    cola(img, letreiro("BANCO IMOBILIÁRIO", 74, AMARELO, INK, 10, "AlfaSlabOne-Regular.ttf", 6, INK), 540, 460, -3,
         pop(t, -0.15))
    cola(img, emoji("👋", 150), 900, 620, 25 * math.sin(t * 10))
    if t > 0.7:
        cola(img, pilula("4 horas de partida... e briga no final", 40, (0, 0, 0), WHITE, WHITE, "Poppins-Black.ttf"),
             540, 1560, 2, pop(t, 0.7))


def cena_hotstreak(img, t):
    u = (t - VIRADA) / (TROCA2 - VIRADA)
    f = hs_foto()
    # pan da direita (rainha + mão) para a esquerda (cachorro-quente), com o soco de zoom no "tchan"
    soco = 1 + 0.12 * (1 - ease(seg(t, VIRADA, VIRADA + 0.35)))
    x0 = lerp(f.width * 0.55, f.width * 0.36, ease(u)) - W / 2
    cx = Image.new("RGBA", (W, H))
    cx.paste(f.crop((int(x0), int((f.height - H) / 2), int(x0) + W, int((f.height - H) / 2) + H)))
    if soco > 1.001:
        cx = cx.resize((int(W * soco), int(H * soco)), Image.BICUBIC).crop(
            (int((W * soco - W) / 2), int((H * soco - H) / 2), int((W * soco - W) / 2) + W, int((H * soco - H) / 2) + H))
    img.alpha_composite(cx)
    cola(img, letreiro("OI, JOGOS\nMODERNOS!", 128, AMARELO, INK, 12, "AlfaSlabOne-Regular.ttf", 10, INK), 540, 330, -3,
         pop(t, VIRADA, 0.3))
    cola(img, emoji("🤩", 130), 900, 560, 10 * math.sin(t * 6), pop(t, VIRADA + 0.15))
    cola(img, pilula("HOT STREAK · corrida de mascotes e apostas", 36, (200, 30, 40), WHITE, WHITE, "Poppins-Black.ttf"),
         540, 1560, -2, pop(t, VIRADA + 0.4))


def cena_ttr(img, t):
    img.alpha_composite(mesa(1.05))
    u = (t - TROCA2) / (FIM - TROCA2)
    sp = peca("ttr_lendas_do_oeste_aberto", 1150)
    cola(img, sombra(sp, 20, (10, 24), 0.45), 560, lerp(1080, 1040, u), lerp(-4, 0, u), lerp(1.05, 1.15, u) * pop(t, TROCA2, 0.3))
    cx = peca("ttr_lendas_do_oeste_caixa", 520)
    cola(img, sombra(cx, 18, (8, 20), 0.5), 790, lerp(1700, 640, ease(seg(t, TROCA2 + 0.2, TROCA2 + 0.7))), 8)
    cola(img, letreiro("E MUITO\nMAIS!", 120, WHITE, INK, 12, "AlfaSlabOne-Regular.ttf", 10, INK), 300, 330, -4,
         pop(t, TROCA2 + 0.1))
    cola(img, pilula("TICKET TO RIDE · LENDAS DO OESTE", 38, (30, 90, 160), WHITE, WHITE, "Poppins-Black.ttf"),
         540, 1560, 2, pop(t, TROCA2 + 0.4))


def cena_fim(img, t):
    img.alpha_composite(mesa(1.0))
    img.alpha_composite(Image.new("RGBA", (W, H), (20, 12, 6, 120)))
    cola(img, sombra(logo_card(520), 20, (0, 20), 0.4), 540, 420, 0, pop(t, FIM))
    cola(img, letreiro("+160 JOGOS\nPRA ALUGAR", 104, AMARELO, INK, 12, "AlfaSlabOne-Regular.ttf", 8, INK), 540, 840, -2,
         pop(t, FIM + 0.25))
    cola(img, pilula("5 DIAS A PARTIR DE R$ 15", 46, (200, 30, 40)), 540, 1090, 0, pop(t, FIM + 0.5))
    cola(img, pilula("RETIRE EM MAUÁ E ABC OU RECEBA EM CASA", 30, WHITE, INK, INK), 540, 1215, 0, pop(t, FIM + 0.7))
    b = 1 + 0.04 * abs(math.sin(t * 5))
    cola(img, pilula("LINK NA BIO · @SUAVEZ_BG", 52, (22, 140, 70)), 540, 1360, 0, pop(t, FIM + 0.9) * b)


def frame_at(t):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    if t < VIRADA:
        cena_banco(img, t)
    elif t < TROCA2:
        cena_hotstreak(img, t)
    elif t < FIM:
        cena_ttr(img, t)
    else:
        cena_fim(img, t)
    if t < FIM:
        wm = logo_card(170)
        img.alpha_composite(wm, (W - wm.width - 30, 40))
    for tc, a0 in ((VIRADA, 255), (TROCA2, 200), (FIM, 160)):  # flash no "tchan" e nas trocas
        if 0 <= t - tc < 0.18:
            img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(a0 * (1 - (t - tc) / 0.18)))))
    return img


def render_frame(fi):
    return frame_at(fi / FPS).convert("RGB").tobytes()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.frame:
        folha([frame_at(x).convert("RGB") for x in a.frame], os.path.join(OUT, "frames.jpg"))
        return
    encode(os.path.join(OUT, "byebye_curto.mp4"), render_frame, list(range(int(DUR * FPS))))


if __name__ == "__main__":
    main()
