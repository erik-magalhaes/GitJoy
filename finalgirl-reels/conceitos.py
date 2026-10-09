#!/usr/bin/env python3
"""Três opções de visual para o Reels do Final Girl (1ª temporada inteira no acervo), com a arte OFICIAL da
Van Ryder Games (caixas 3D com transparência e tabuleiros dos assassinos, 3000 px):

1) LOCADORA DO TERROR: as caixas como fitas numa prateleira de locadora, letreiro de neon (a Sua Vez é locação!).
2) TRAILER SLASHER: tela preta, facho de lanterna revelando o assassino, título vermelho rasgado.
3) EM CARTAZ: fachada de cinema com letreiro de lâmpadas e os filmes como cartazes.

    python3 conceitos.py     # out/conceitos_finalgirl.jpg
"""
import math
import os
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "..", "comum"))
from motor import W, H, WHITE, font, logo_card, cola, sombra, letreiro, pilula  # noqa: E402

OF = os.path.join(ROOT, "assets", "oficial")
CREEP = os.path.join(ROOT, "..", "voodoo-reels", "assets", "fonts", "Creepster-Regular.ttf")
VERM = (210, 20, 30)
# filme → (caixa 3D, assassino, compview, recorte do assassino no compview em fração)
FILMES = {
    "hans": ("FG-FF1-1.png", "HANS", "FF1-compview.png", (0.585, 0.30, 0.80, 0.80)),
    "poltergeist": ("FG-FF2-1.png", "POLTERGEIST", "FF2-compview.png", (0.585, 0.30, 0.80, 0.80)),
    "inkanyamba": ("FG-FF3-1.png", "INKANYAMBA", "FF3-compview.png", (0.585, 0.30, 0.80, 0.80)),
    "geppetto": ("FG-FF4-1.png", "GEPPETTO", "FF4-compview.png", (0.585, 0.30, 0.80, 0.80)),
    "drmedo": ("FG-FF5-1.png", "DR. MEDO", "FF5-compview.png", (0.585, 0.30, 0.80, 0.80)),
}


def creep(s):
    return ImageFont.truetype(CREEP, int(s))


@lru_cache(None)
def oficial(nome):
    return Image.open(os.path.join(OF, nome)).convert("RGBA")


def caixa(k, h):
    im = oficial(FILMES[k][0])
    im = im.crop(im.getbbox())
    return im.resize((int(im.width * h / im.height), int(h)), Image.LANCZOS)


def assassino(k):
    im = oficial(FILMES[k][2])
    x0, y0, x1, y1 = FILMES[k][3]
    return im.crop((int(x0 * im.width), int(y0 * im.height), int(x1 * im.width), int(y1 * im.height)))


def neon(img, txt, x, y, size, cor, fonte=None):
    f = fonte or font("Monoton-Regular.ttf", size)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.text((x, y), txt, font=f, fill=cor + (255,), anchor="mm")
    img.alpha_composite(ov.filter(ImageFilter.GaussianBlur(18)))
    img.alpha_composite(ov.filter(ImageFilter.GaussianBlur(5)))
    d2 = ImageDraw.Draw(img)
    d2.text((x, y), txt, font=f, fill=tuple(min(255, c + 120) for c in cor), anchor="mm")


def wm(img):
    lg = logo_card(160)
    img.alpha_composite(lg, (W - lg.width - 30, 40))


def opcao_locadora():
    yy = np.linspace(0, 1, H)[:, None, None]
    a = (np.array((22, 10, 40)) * (1 - yy) + np.array((6, 4, 12)) * yy) * np.ones((1, W, 1))
    img = Image.fromarray(a.astype(np.uint8), "RGB").convert("RGBA")
    neon(img, "LOCADORA", 540, 230, 120, (255, 40, 140))
    neon(img, "DO TERROR", 540, 380, 96, (60, 200, 255))
    d = ImageDraw.Draw(img)
    for y in (980, 1500):  # prateleiras
        d.rectangle((40, y, 1040, y + 26), fill=(60, 40, 30))
        d.rectangle((40, y + 26, 1040, y + 40), fill=(30, 20, 15))
    ks = list(FILMES)
    for i, k in enumerate(ks[:3]):
        cola(img, sombra(caixa(k, 420), 14, (6, 12), 0.6), 200 + i * 340, 980 - 210)
    for i, k in enumerate(ks[3:]):
        cola(img, sombra(caixa(k, 420), 14, (6, 12), 0.6), 370 + i * 340, 1500 - 210)
    cola(img, pilula("ALUGUE · 5 DIAS", 34, VERM), 880, 1600, -4)
    cola(img, letreiro("Você sobreviveria\na um filme de terror?", 58, WHITE, (0, 0, 0), 8, "Poppins-Black.ttf"), 540, 1760)
    wm(img)
    return img


def opcao_trailer():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    k = assassino("hans")
    k = k.resize((int(k.width * 1500 / k.height), 1500), Image.LANCZOS)
    cam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cam.alpha_composite(k, (540 - k.width // 2, 300))
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse((150, 360, 930, 1240), fill=255)  # facho da lanterna
    m = m.filter(ImageFilter.GaussianBlur(70))
    img.paste(cam, (0, 0), m)
    d = ImageDraw.Draw(img)
    d.text((540, 1420), "HANS", font=creep(260), fill=VERM, anchor="mm")
    d.text((540, 1580), "O AÇOUGUEIRO", font=font("Poppins-Black.ttf", 52), fill=WHITE, anchor="mm")
    d.text((540, 230), "FINAL GIRL", font=creep(130), fill=WHITE, anchor="mm")
    d.text((540, 340), "você é a última sobrevivente", font=font("Poppins-ExtraBold.ttf", 44), fill=(200, 200, 200), anchor="mm")
    d.rectangle((0, 0, W, 90), fill=(0, 0, 0))
    d.rectangle((0, H - 90, W, H), fill=(0, 0, 0))
    wm(img)
    return img


def opcao_cartaz():
    img = Image.new("RGBA", (W, H), (25, 8, 10, 255))
    d = ImageDraw.Draw(img)
    # letreiro de cinema com lâmpadas
    d.rounded_rectangle((60, 120, 1020, 520), radius=30, fill=(240, 230, 210), outline=(180, 20, 30), width=16)
    for i in range(22):
        x = 90 + i * 43
        for y in (140, 500):
            d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=(255, 220, 120))
    for j in range(8):
        y = 175 + j * 43
        for x in (80, 1000):
            d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=(255, 220, 120))
    d.text((540, 230), "EM CARTAZ", font=font("Bungee-Regular.ttf", 70), fill=(180, 20, 30), anchor="mm")
    d.text((540, 340), "FINAL GIRL", font=creep(120), fill=(20, 20, 20), anchor="mm")
    d.text((540, 445), "5 FILMES · SÓ 1 SOBREVIVE", font=font("Bungee-Regular.ttf", 40), fill=(20, 20, 20), anchor="mm")
    luz = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(luz).ellipse((140, 560, 940, 1660), fill=(255, 200, 150, 60))
    img.alpha_composite(luz.filter(ImageFilter.GaussianBlur(80)))
    for i, k in enumerate(("poltergeist", "geppetto", "drmedo")):
        c = caixa(k, 620 if i == 1 else 520)
        cola(img, sombra(c, 18, (8, 16), 0.6), 540 + (i - 1) * 330, 1110 if i == 1 else 1150, (i - 1) * 6)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 1560, W, H), fill=(60, 10, 14))
    cola(img, letreiro("qual você assistiria?", 58, WHITE, (0, 0, 0), 8, "Poppins-Black.ttf"), 540, 1700)
    wm(img)
    return img


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    ims = [opcao_locadora(), opcao_trailer(), opcao_cartaz()]
    sheet = Image.new("RGB", (3 * 540 + 40, 1040), (24, 24, 24))
    d = ImageDraw.Draw(sheet)
    for k, (im, t) in enumerate(zip(ims, ("1 · LOCADORA DO TERROR", "2 · TRAILER SLASHER", "3 · EM CARTAZ"))):
        sheet.paste(im.convert("RGB").resize((540, 960), Image.LANCZOS), (10 + k * 550, 70))
        d.text((10 + k * 550 + 270, 35), t, font=font("Bungee-Regular.ttf", 32), fill=WHITE, anchor="mm")
    sheet.save(os.path.join(ROOT, "out", "conceitos_finalgirl.jpg"), quality=90)
    print("ok")
