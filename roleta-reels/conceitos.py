#!/usr/bin/env python3
"""Reels "Monte sua noite de jogos — TIRA PRINT!": as caixas trocam rápido em 3 casas (pra aquecer / o jogão / pra fechar
a noite); cada um dá print num instante e cai numa noite diferente ("a minha deu..."). Fecha com "aluga os seus 3 =
7 dias". Este arquivo só monta 3 OPÇÕES DE VISUAL lado a lado para ele escolher.

    python3 conceitos.py      # out/conceitos.jpg
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "comum"))
from motor import W, H, WHITE, font, logo_card, cola, sombra, letreiro, pilula  # noqa: E402

OUT = os.path.join(ROOT, "out")
INK = (20, 16, 30)
AMARELO = (255, 214, 70)
# caixas OFICIAIS que já temos no projeto e que estão no acervo da Sua Vez
CAIXAS = {
    "ticket": "gravados-reels/assets/lista/ticket_to_ride.png", "dixit": "gravados-reels/assets/lista/dixit.png",
    "king": "gravados-reels/assets/lista/king_of_tokyo.png", "resistance": "gravados-reels/assets/lista/the_resistance.png",
    "boop": "gravados-reels/assets/lista/boop.png", "splendor": "gravados-reels/assets/lista/splendor_duel.png",
    "azulduel": "gravados-reels/assets/lista/azul_duel.png", "harmonies": "gravados-reels/assets/lista/harmonies.png",
    "hitster": "gravados-reels/assets/lista/hitster.png", "marvel": "gravados-reels/assets/lista/marvel_united.png",
    "cuckoo": "gravados-reels/assets/oficial/go_cuckoo.png", "draft": "gravados-reels/assets/oficial/draftosaurus.png",
    "gravity": "gravados-reels/assets/oficial/gravity_superstar.png", "scooby": "gravados-reels/assets/oficial/scooby_doo.png",
    "banana": "gravados-reels/assets/perguntas/bananagrams.png", "coffee": "gravados-reels/assets/perguntas/coffee_rush.png",
    "marrakech": "gravados-reels/assets/perguntas/marrakech.png", "uno": "gravados-reels/assets/perguntas/uno.png",
    "hotstreak": "hotstreak-reels/assets/pecas/caixa.png", "arquitetos": "architects-reels/assets/oficial/caixa3d.png",
    "vudu": "voodoo-reels/assets/pieces/box.png", "sintonia": "sintonia-reels/assets/pieces/box.png",
    "finalgirl": "finalgirl-reels/assets/recortes/caixa_base.png", "deadpool": "marvel-reels/assets/caixas/deadpool.png",
}
CASAS = ["PRA AQUECER", "O JOGÃO", "PRA FECHAR"]


def caixa(nome, h, larg=None):
    im = Image.open(os.path.join(REPO, CAIXAS[nome])).convert("RGBA")
    im = im.crop(im.getbbox())
    s = h / im.height
    if larg and im.width * s > larg:
        s = larg / im.width
    return im.resize((max(2, int(im.width * s)), max(2, int(im.height * s))), Image.LANCZOS)


def borrada(im, n=40):
    """Caixa 'girando' (borrão vertical, como o rolo do caça-níquel)."""
    pad = Image.new("RGBA", (im.width, im.height + 2 * n), (0, 0, 0, 0))
    pad.alpha_composite(im, (0, n))
    import numpy as np
    import cv2
    a = np.asarray(pad).astype(np.float32)
    k = np.ones((n, 1), np.float32) / n
    b = cv2.filter2D(a, -1, k)
    return Image.fromarray(b.clip(0, 255).astype(np.uint8))


def titulo(img, y=290, cor=AMARELO):
    cola(img, letreiro("MONTE SUA NOITE\nDE JOGOS", 90, cor, INK, 14, sombra_px=8, cor_sombra=INK), 540, y, -2)
    cola(img, pilula("TIRA PRINT AGORA! 📸".replace(" 📸", ""), 54, (230, 30, 80), WHITE, WHITE, bw=6), 540, y + 210, 2)


def rodape(img):
    cola(img, pilula("ALUGA OS SEUS 3 = 7 DIAS!", 44, (22, 163, 74)), 540, 1600, 0)
    wm = logo_card(150)
    img.alpha_composite(wm, (W - wm.width - 30, 40))


# ---------------------------------------------------------------- opção 1: caça-níquel neon
def opcao1():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    for y in range(H):  # degradê roxo → azul-noite
        u = y / H
        d.line((0, y, W, y), fill=(int(70 - 50 * u), int(20 + 5 * u), int(110 - 40 * u)))
    for _ in range(90):  # luzinhas de cassino ao fundo
        rnd = random.Random(_)
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(2, 6)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 220, 120, 120))
    img = img.filter(ImageFilter.GaussianBlur(1))
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 50, 560, 1030, 1420
    d.rounded_rectangle((x0, y0, x1, y1), radius=60, fill=(150, 20, 40), outline=(255, 200, 60), width=14)
    for k in range(26):  # lâmpadas na moldura
        t = k / 26
        per = 2 * ((x1 - x0) + (y1 - y0))
        p = t * per
        if p < x1 - x0:
            x, y = x0 + p, y0
        elif p < (x1 - x0) + (y1 - y0):
            x, y = x1, y0 + p - (x1 - x0)
        elif p < 2 * (x1 - x0) + (y1 - y0):
            x, y = x1 - (p - (x1 - x0) - (y1 - y0)), y1
        else:
            x, y = x0, y1 - (p - 2 * (x1 - x0) - (y1 - y0))
        d.ellipse((x - 11, y - 11, x + 11, y + 11), fill=(255, 245, 200) if k % 2 else (255, 170, 40))
    nomes = ["dixit", "king", "coffee"]
    for j in range(3):
        wx = 95 + j * 305
        d.rounded_rectangle((wx, 650, wx + 280, 1170), radius=26, fill=(255, 250, 240), outline=(60, 10, 20), width=8)
        im = caixa(nomes[j], 300, 240)
        if j == 2:
            im = borrada(im, 70)
        cola(img, sombra(im, 10, (0, 8), 0.4), wx + 140, 910)
        d.text((wx + 140, 1230), CASAS[j], font=font("Bungee-Regular.ttf", 34), fill=WHITE, anchor="mm",
               stroke_width=4, stroke_fill=INK)
    d.rounded_rectangle((1000, 760, 1040, 1040), radius=20, fill=(200, 200, 210))  # alavanca
    d.ellipse((985, 690, 1055, 760), fill=(230, 30, 60), outline=WHITE, width=5)
    titulo(img)
    rodape(img)
    return img


# ---------------------------------------------------------------- opção 2: roda da sorte (programa de auditório)
def opcao2():
    img = Image.new("RGBA", (W, H), (255, 200, 40, 255))
    d = ImageDraw.Draw(img)
    cx, cy = 540, 1950
    for j in range(30):  # raios de auditório
        a0, a1 = j * math.tau / 30, (j + 0.5) * math.tau / 30
        d.polygon([(cx, cy), (cx + 3000 * math.cos(a0), cy + 3000 * math.sin(a0)),
                   (cx + 3000 * math.cos(a1), cy + 3000 * math.sin(a1))], fill=(255, 170, 30))
    cx, cy, r = 540, 990, 360
    cores = [(230, 40, 90), (40, 160, 255), (60, 200, 90), (140, 90, 255), (255, 130, 0), (0, 190, 190)]
    nomes = ["ticket", "uno", "scooby", "hitster", "marrakech", "draft", "boop", "gravity", "banana", "harmonies",
             "splendor", "vudu"]
    n = len(nomes)
    roda = Image.new("RGBA", (2 * r + 40, 2 * r + 40), (0, 0, 0, 0))
    dr = ImageDraw.Draw(roda)
    c = r + 20
    dr.ellipse((0, 0, 2 * r + 40, 2 * r + 40), fill=(255, 255, 255))
    for j in range(n):
        a0, a1 = -90 + j * 360 / n, -90 + (j + 1) * 360 / n
        dr.pieslice((20, 20, 2 * r + 20, 2 * r + 20), a0, a1, fill=cores[j % len(cores)], outline=WHITE, width=6)
    for j, nm in enumerate(nomes):
        a = math.radians(-90 + (j + 0.5) * 360 / n)
        im = caixa(nm, 120, 110)
        im = im.rotate(-math.degrees(a) - 90, expand=True, resample=Image.BICUBIC)
        roda.alpha_composite(im, (int(c + 0.66 * r * math.cos(a) - im.width / 2), int(c + 0.66 * r * math.sin(a) - im.height / 2)))
    dr.ellipse((c - 70, c - 70, c + 70, c + 70), fill=(255, 214, 70), outline=WHITE, width=8)
    roda = roda.rotate(8, resample=Image.BICUBIC)
    cola(img, sombra(roda, 24, (0, 24), 0.4), cx, cy)
    d = ImageDraw.Draw(img)
    d.polygon([(cx - 45, cy - r - 70), (cx + 45, cy - r - 70), (cx, cy - r + 30)], fill=(230, 30, 60), outline=WHITE, width=6)
    # as 3 casas do resultado
    for j, nm in enumerate(["ticket", "uno", None]):
        x = 210 + j * 330
        d.rounded_rectangle((x - 130, 1480 - 110, x + 130, 1480 + 70), radius=24, fill=(255, 255, 255, 230),
                            outline=INK, width=6)
        if nm:
            cola(img, caixa(nm, 140, 200), x, 1440)
        else:
            d.text((x, 1440), "?", font=font("Bungee-Regular.ttf", 110), fill=(200, 200, 210), anchor="mm")
        d.text((x, 1525), CASAS[j], font=font("Bungee-Regular.ttf", 28), fill=INK, anchor="mm")
    titulo(img, 270, WHITE)
    cola(img, pilula("ALUGA OS SEUS 3 = 7 DIAS!", 40, (22, 163, 74)), 540, 1660, 0)
    wm = logo_card(150)
    img.alpha_composite(wm, (W - wm.width - 30, 40))
    return img


# ---------------------------------------------------------------- opção 3: cartas na mesa de feltro
def opcao3():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    for y in range(H):
        u = abs(y - H * 0.55) / H
        d.line((0, y, W, y), fill=(int(20 + 20 * (1 - u)), int(90 + 40 * (1 - u)), int(55 + 20 * (1 - u))))
    luz = Image.new("L", (W, H), 0)
    ImageDraw.Draw(luz).ellipse((-100, 450, W + 100, 1650), fill=120)
    img = Image.composite(Image.new("RGBA", (W, H), (70, 170, 100, 255)), img, luz.filter(ImageFilter.GaussianBlur(160)))
    d = ImageDraw.Draw(img)
    nomes = ["banana", "finalgirl", "azulduel"]
    for j in range(3):
        y = 720 + j * 290
        carta = Image.new("RGBA", (900, 250), (0, 0, 0, 0))
        dc = ImageDraw.Draw(carta)
        dc.rounded_rectangle((0, 0, 899, 249), radius=30, fill=(255, 252, 245), outline=(212, 175, 55), width=8)
        dc.text((40, 125), f"{j + 1}", font=font("Bungee-Regular.ttf", 110), fill=(212, 175, 55), anchor="lm")
        dc.text((170, 70), CASAS[j], font=font("Bungee-Regular.ttf", 40), fill=INK, anchor="lm")
        dc.text((170, 130), ["um rapidinho pra abrir", "o principal da noite", "pra rir antes de ir embora"][j],
                font=font("Poppins-SemiBold.ttf", 34), fill=(90, 90, 100), anchor="lm")
        im = caixa(nomes[j], 210, 260)
        if j == 2:  # a última ainda "trocando"
            im = borrada(im, 50)
        carta.alpha_composite(im, (900 - 40 - im.width, int(125 - im.height / 2)))
        cola(img, sombra(carta, 18, (0, 14), 0.5), 540, y, (-1.5, 1, -1)[j])
    titulo(img)
    rodape(img)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    ims = [opcao1(), opcao2(), opcao3()]
    folha = Image.new("RGB", (3 * 540 + 40, 960 + 90), (245, 240, 230))
    d = ImageDraw.Draw(folha)
    for k, (im, nome) in enumerate(zip(ims, ["1 · Caça-níquel neon", "2 · Roda da sorte", "3 · Cartas na mesa"])):
        folha.paste(im.convert("RGB").resize((540, 960), Image.LANCZOS), (10 + k * 550, 80))
        d.text((10 + k * 550 + 270, 40), nome, font=font("Bungee-Regular.ttf", 34), fill=INK, anchor="mm")
    folha.save(os.path.join(OUT, "conceitos.jpg"), quality=92)
    print("ok")


if __name__ == "__main__":
    main()
