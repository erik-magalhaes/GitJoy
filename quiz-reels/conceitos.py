#!/usr/bin/env python3
"""Três opções novas de quiz curto (o dono achou o zoom com lupa feio, lento e longo):
1) Adivinha pelos EMOJIS  2) ESTE OU AQUELE? (duelo rápido)  3) ZOOM RELÂMPAGO em tela cheia.

    python3 conceitos.py      # out/conceitos_quiz.jpg
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "..", "comum"))
from motor import W, H, WHITE, font, emoji, caixa, caixa_original, logo_card, cola, sombra, letreiro, pilula  # noqa

INK = (16, 16, 24)
ORANGE = (249, 115, 22)
AMARELO = (255, 214, 70)


def degrade(c1, c2):
    yy = np.linspace(0, 1, H)[:, None, None]
    a = (np.array(c1) * (1 - yy) + np.array(c2) * yy) * np.ones((1, W, 1))
    return Image.fromarray(a.astype(np.uint8), "RGB").convert("RGBA")


def wm(img):
    lg = logo_card(160)
    img.alpha_composite(lg, (W - lg.width - 30, 40))


def opcao_emojis():
    """Fundo escuro limpo, 3 emojis grandes em 'balões' e a contagem em barra; o nome aparece por cima."""
    img = degrade((28, 22, 60), (8, 8, 16))
    cola(img, letreiro("ADIVINHA O JOGO\nPELOS EMOJIS", 84, WHITE, INK, 0), 540, 330)
    cola(img, pilula("JOGO 2 DE 5", 38, ORANGE), 540, 520)
    for i, e in enumerate(("🦖", "🏙️", "👑")):
        x = 540 + (i - 1) * 300
        bolha = Image.new("RGBA", (260, 260), (0, 0, 0, 0))
        ImageDraw.Draw(bolha).ellipse((0, 0, 259, 259), fill=(255, 255, 255, 28), outline=(255, 255, 255, 90), width=4)
        cola(img, bolha, x, 900)
        cola(img, emoji(e, 170), x, 900, (i - 1) * 6)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((140, 1180, 940, 1210), radius=15, fill=(255, 255, 255, 40))
    d.rounded_rectangle((140, 1180, 640, 1210), radius=15, fill=AMARELO)
    cola(img, letreiro("3", 150, AMARELO, INK, 0), 540, 1370)
    wm(img)
    return img


def opcao_duelo():
    """Tela dividida em duas cores, uma caixa de cada lado e o VS no meio; pergunta curta no topo."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    d.polygon([(0, 0), (W, 0), (W, 820), (0, 1100)], fill=(230, 70, 60))
    d.polygon([(0, 1100), (W, 820), (W, H), (0, H)], fill=(40, 110, 220))
    cola(img, letreiro("ESTE OU AQUELE?", 92, WHITE, INK, 10), 540, 230)
    cola(img, sombra(caixa("king_of_tokyo", 520), 20, (10, 24), 0.5), 330, 640, -6)
    cola(img, sombra(caixa("camel_up_second_edition", 520), 20, (10, 24), 0.5), 750, 1350, 6)
    cola(img, letreiro("VS", 170, AMARELO, INK, 14), 540, 960, -8)
    cola(img, pilula("DUELO 3 DE 6", 36, INK), 540, 360)
    cola(img, letreiro("comenta seu placar!", 52, WHITE, INK, 8, "Poppins-Black.ttf"), 540, 1720)
    wm(img)
    return img


def opcao_relampago():
    """A arte da caixa ocupa a tela toda (sem moldura), recortada num detalhe; tarja e contagem em cima."""
    cx = caixa_original("deep_regrets")
    bw, bh = cx.size
    s = bh * 0.32
    det = cx.crop((int(bw * 0.52 - s * 0.28), int(bh * 0.22 - s / 2), int(bw * 0.52 + s * 0.28), int(bh * 0.22 + s / 2)))
    img = det.convert("RGB").resize((W, H), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2)).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for y in range(0, 420):
        d.line((0, y, W, y), fill=(0, 0, 0, int(170 * (1 - y / 420))))
    img.alpha_composite(ov)
    cola(img, letreiro("QUE JOGO É ESSE?", 88, WHITE, INK, 10), 540, 230)
    cola(img, pilula("4/5 · MUITO DIFÍCIL", 40, (200, 40, 60)), 540, 360)
    d = ImageDraw.Draw(img)
    d.ellipse((440, 1400, 640, 1600), fill=(0, 0, 0, 150), outline=WHITE, width=8)
    d.arc((440, 1400, 640, 1600), -90, 150, fill=AMARELO, width=14)
    d.text((540, 1505), "2", font=font("Bungee-Regular.ttf", 110), fill=WHITE, anchor="mm")
    wm(img)
    return img


if __name__ == "__main__":
    ims = [opcao_emojis(), opcao_duelo(), opcao_relampago()]
    sheet = Image.new("RGB", (3 * 540 + 40, 1040), (24, 24, 24))
    d = ImageDraw.Draw(sheet)
    for k, (im, t) in enumerate(zip(ims, ("1 · EMOJIS", "2 · ESTE OU AQUELE?", "3 · ZOOM RELÂMPAGO"))):
        sheet.paste(im.convert("RGB").resize((540, 960), Image.LANCZOS), (10 + k * 550, 70))
        d.text((10 + k * 550 + 270, 35), t, font=font("Bungee-Regular.ttf", 36), fill=WHITE, anchor="mm")
    sheet.save(os.path.join(ROOT, "out", "conceitos_quiz.jpg"), quality=90)
    print("ok")
