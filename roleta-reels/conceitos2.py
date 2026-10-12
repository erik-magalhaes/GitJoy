#!/usr/bin/env python3
"""2ª rodada de visuais do "tira print" (ele gostou da ideia das 3 cartas, a opção 3, mas não do design).
Só jogos que AINDA NÃO apareceram em nenhum post (pedido dele). Três opções novas lado a lado:

    A · Tarô da noite de jogos  (cartas de cartomante, roxo e dourado)
    B · Cardápio da noite       (lousa de restaurante: entrada, prato principal, sobremesa)
    C · Raspadinha premiada     (bilhete de raspadinha com 3 janelas)

    python3 conceitos2.py      # out/conceitos2.jpg
"""
import math
import os
import random
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "comum"))
from motor import W, H, WHITE, font, emoji, logo_card, cola, sombra, letreiro, pilula  # noqa: E402

OUT = os.path.join(ROOT, "out")
AS = os.path.join(ROOT, "assets")
INK = (20, 16, 30)
OURO = (232, 190, 92)
AQUECER = ["the_mind", "fantasy_realms", "taco_gato"]
JOGAO = ["sheriff", "cartografos", "unicorn_fever", "sea_salt"]
FECHAR = ["spyfall", "last_message", "happy_salmon"]


@lru_cache(None)
def caixa(n, h, larg=None):
    im = Image.open(os.path.join(AS, n + ".png")).convert("RGBA")
    im = im.crop(im.getbbox())
    s = h / im.height
    if larg and im.width * s > larg:
        s = larg / im.width
    return im.resize((max(2, int(im.width * s)), max(2, int(im.height * s))), Image.LANCZOS)


def borrada(im, n=50):
    import cv2
    pad = Image.new("RGBA", (im.width, im.height + 2 * n), (0, 0, 0, 0))
    pad.alpha_composite(im, (0, n))
    a = cv2.filter2D(np.asarray(pad).astype(np.float32), -1, np.ones((n, 1), np.float32) / n)
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def marca(img):
    wm = logo_card(140)
    img.alpha_composite(wm, (W - wm.width - 30, 40))
    cola(img, pilula("ALUGA OS SEUS 3 = 7 DIAS!", 40, (22, 163, 74)), 540, 1640, 0)


# ---------------------------------------------------------------- A: tarô
def opcao_a():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    for y in range(H):
        u = y / H
        d.line((0, y, W, y), fill=(int(48 - 30 * u), int(18 + 4 * u), int(78 - 40 * u)))
    rnd = random.Random(2)
    for _ in range(120):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(1, 3)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 230, 160, rnd.randint(60, 200)))
    luz = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(luz).ellipse((140, 650, 940, 1450), fill=(200, 120, 255, 70))
    img.alpha_composite(luz.filter(ImageFilter.GaussianBlur(120)))
    cola(img, letreiro("A CARTOMANTE\nDOS JOGOS", 92, OURO, INK, 12, sombra_px=7, cor_sombra=INK), 540, 250, -1)
    cola(img, pilula("TIRA PRINT E DESCOBRE SUA NOITE", 38, (120, 40, 170), WHITE, OURO, bw=5), 540, 450, 0)
    rot = [("I", "PRA AQUECER", "the_mind"), ("II", "O JOGÃO", "sheriff"), ("III", "PRA FECHAR", None)]
    for j, (num, nome, n) in enumerate(rot):
        c = Image.new("RGBA", (310, 560), (0, 0, 0, 0))
        dc = ImageDraw.Draw(c)
        dc.rounded_rectangle((0, 0, 309, 559), radius=24, fill=(250, 240, 220), outline=OURO, width=10)
        dc.rounded_rectangle((18, 18, 291, 541), radius=16, outline=(150, 100, 40), width=3)
        dc.text((155, 62), num, font=font("Bungee-Regular.ttf", 44), fill=(110, 60, 140), anchor="mm")
        dc.text((155, 505), nome, font=font("Bungee-Regular.ttf", 30), fill=(110, 60, 140), anchor="mm")
        for cx_ in (48, 262):  # losangos dourados nos cantos
            dc.polygon([(cx_, 46), (cx_ + 12, 62), (cx_, 78), (cx_ - 12, 62)], fill=OURO)
        if n:
            im = caixa(n, 330, 250)
        else:
            im = borrada(caixa("spyfall", 330, 250), 60)
        c.alpha_composite(im, (int(155 - im.width / 2), int(285 - im.height / 2)))
        cola(img, sombra(c, 22, (0, 18), 0.6), 190 + j * 350, 1010 + (0, -30, 0)[j], (-6, 0, 6)[j])
    cola(img, letreiro("comenta o que saiu pra você!", 46, WHITE, INK, 8, "Poppins-Black.ttf"), 540, 1420, 0)
    marca(img)
    return img


# ---------------------------------------------------------------- B: cardápio na lousa
def opcao_b():
    img = Image.new("RGBA", (W, H), (150, 95, 55, 255))
    d = ImageDraw.Draw(img)
    for k in range(0, H, 26):  # tábua de madeira
        d.line((0, k, W, k + 6), fill=(140, 88, 50), width=3)
    d.rounded_rectangle((50, 170, 1030, 1560), radius=30, fill=(150, 100, 60))
    lousa = Image.new("RGBA", (920, 1330), (38, 48, 44, 255))
    rnd = np.random.default_rng(4)
    a = (rnd.random((70, 50)) * 18).astype(np.uint8)
    giz = Image.fromarray(a).resize(lousa.size, Image.BICUBIC).filter(ImageFilter.GaussianBlur(25))
    lousa.alpha_composite(Image.merge("RGBA", (giz, giz, giz, giz)))
    dl = ImageDraw.Draw(lousa)
    dl.text((460, 90), "MENU DA NOITE", font=font("Bungee-Regular.ttf", 74), fill=(245, 240, 225), anchor="mm")
    dl.text((460, 165), "de jogos  ·  tira print e faça seu pedido", font=font("Poppins-SemiBold.ttf", 32),
            fill=(220, 215, 200), anchor="mm")
    dl.line((120, 210, 800, 210), fill=(230, 225, 210), width=3)
    pratos = [("ENTRADA", "fantasy_realms", (255, 190, 120)), ("PRATO PRINCIPAL", "cartografos", (150, 220, 255)),
              ("SOBREMESA", None, (255, 160, 200))]
    for j, (nome, n, cor) in enumerate(pratos):
        y = 260 + j * 345
        dl.text((70, y + 30), nome, font=font("Bungee-Regular.ttf", 46), fill=cor, anchor="lm")
        dl.text((70, y + 95), ["algo leve pra abrir o apetite", "o jogo que vai segurar a noite", "pra rir antes de ir embora"][j],
                font=font("Poppins-SemiBold.ttf", 30), fill=(220, 215, 200), anchor="lm")
        dl.line((70, y + 300, 850, y + 300), fill=(120, 130, 125), width=2)
        im = caixa(n, 270, 260) if n else borrada(caixa("last_message", 270, 260), 60)
        lousa.alpha_composite(sombra(im, 10, (0, 8), 0.5), (int(720 - im.width / 2 - 20), int(y + 150 - im.height / 2 - 20)))
    img.alpha_composite(lousa, (80, 200))
    cola(img, emoji("🍽️", 110), 130, 175, -10)
    marca(img)
    return img


# ---------------------------------------------------------------- C: raspadinha
def opcao_c():
    img = Image.new("RGBA", (W, H), (255, 200, 40, 255))
    d = ImageDraw.Draw(img)
    for j in range(24):
        a0, a1 = j * math.tau / 24, (j + 0.5) * math.tau / 24
        d.polygon([(540, 980), (540 + 2400 * math.cos(a0), 980 + 2400 * math.sin(a0)),
                   (540 + 2400 * math.cos(a1), 980 + 2400 * math.sin(a1))], fill=(255, 175, 30))
    bil = Image.new("RGBA", (960, 1240), (0, 0, 0, 0))
    db = ImageDraw.Draw(bil)
    db.rounded_rectangle((0, 0, 959, 1239), radius=40, fill=(230, 40, 90), outline=WHITE, width=12)
    db.rounded_rectangle((30, 30, 929, 1209), radius=28, outline=(255, 214, 70), width=5)
    db.text((480, 120), "RASPADINHA", font=font("Bungee-Regular.ttf", 96), fill=WHITE, anchor="mm")
    db.text((480, 215), "DA NOITE DE JOGOS", font=font("Bungee-Regular.ttf", 48), fill=(255, 214, 70), anchor="mm")
    db.text((480, 290), "tira print pra raspar!", font=font("Poppins-Black.ttf", 36), fill=WHITE, anchor="mm")
    nomes = [("PRA AQUECER", "taco_gato"), ("O JOGÃO", "unicorn_fever"), ("PRA FECHAR", None)]
    for j, (nome, n) in enumerate(nomes):
        x = 170 + j * 310
        db.rounded_rectangle((x - 140, 360, x + 140, 900), radius=24, fill=(255, 250, 240), outline=(255, 214, 70), width=6)
        if n:
            im = caixa(n, 400, 250)
            bil.alpha_composite(im, (int(x - im.width / 2), int(630 - im.height / 2)))
        else:  # ainda coberta de prata (o resto já foi "raspado")
            prata = Image.new("RGBA", (270, 530), (190, 195, 205, 255))
            dp = ImageDraw.Draw(prata)
            for k in range(0, 600, 18):
                dp.line((k - 300, 0, k, 530), fill=(210, 215, 225), width=8)
            dp.text((135, 265), "?", font=font("Bungee-Regular.ttf", 160), fill=(150, 155, 165), anchor="mm")
            bil.alpha_composite(prata, (x - 135, 365))
        db.text((x, 950), nome, font=font("Bungee-Regular.ttf", 34), fill=WHITE, anchor="mm")
    db.text((480, 1090), "PRÊMIO: SUA NOITE DE JOGOS 🎲".replace(" 🎲", ""), font=font("Bungee-Regular.ttf", 44),
            fill=(255, 214, 70), anchor="mm")
    db.text((480, 1155), "comenta o que saiu pra você!", font=font("Poppins-Black.ttf", 34), fill=WHITE, anchor="mm")
    cola(img, sombra(bil, 24, (0, 20), 0.5), 540, 900, -2)
    marca(img)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    ims = [opcao_a(), opcao_b(), opcao_c()]
    folha = Image.new("RGB", (3 * 540 + 40, 960 + 90), (245, 240, 230))
    d = ImageDraw.Draw(folha)
    for k, (im, nome) in enumerate(zip(ims, ["A · Tarô dos jogos", "B · Cardápio da noite", "C · Raspadinha"])):
        folha.paste(im.convert("RGB").resize((540, 960), Image.LANCZOS), (10 + k * 550, 80))
        d.text((10 + k * 550 + 270, 40), nome, font=font("Bungee-Regular.ttf", 34), fill=INK, anchor="mm")
    folha.save(os.path.join(OUT, "conceitos2.jpg"), quality=92)
    print("ok")


if __name__ == "__main__":
    main()
