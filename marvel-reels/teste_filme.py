#!/usr/bin/env python3
"""Quadros de teste do visual "filme de herói" (para aprovação antes de animar).

    python3 teste_filme.py    # out/teste_filme.jpg
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
CX = os.path.join(ROOT, "assets", "caixas")
MI = os.path.join(ROOT, "assets", "minis")
FN = os.path.join(ROOT, "assets", "fonts")
W, H = 1080, 1920
WHITE = (255, 255, 255)
GOLD = (255, 200, 70)


def font(n, s):
    return ImageFont.truetype(os.path.join(FN, n), s)


def peca(path, h):
    im = Image.open(path).convert("RGBA")
    return im.resize((max(2, int(im.width * h / im.height)), h), Image.LANCZOS)


def cena_escura(c1=(8, 10, 22), c2=(2, 2, 6)):
    yy = np.linspace(0, 1, H)[:, None, None]
    a = (np.array(c1) * (1 - yy) + np.array(c2) * yy) * np.ones((1, W, 1))
    return Image.fromarray(a.astype(np.uint8), "RGB").convert("RGBA")


def luz(img, cx, cy, r, cor, a=120):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ov).ellipse((cx - r, cy - r, cx + r, cy + r), fill=cor + (a,))
    img.alpha_composite(ov.filter(ImageFilter.GaussianBlur(r * 0.45)))


def holofote(img, x, cor=(180, 210, 255), a=60):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ov).polygon([(x - 60, 0), (x + 60, 0), (x + 380, H), (x - 380, H)], fill=cor + (a,))
    img.alpha_composite(ov.filter(ImageFilter.GaussianBlur(40)))


def chao_reflexo(img, objs, y_chao):
    """Piso preto brilhante: reflexo invertido e esmaecido de cada objeto."""
    for im, x in objs:
        r = im.transpose(Image.FLIP_TOP_BOTTOM)
        a = np.asarray(r.getchannel("A")).astype(float)
        grad = np.linspace(0.35, 0, r.height)[:, None]
        r.putalpha(Image.fromarray((a * grad).astype(np.uint8)))
        img.alpha_composite(r, (int(x - im.width / 2), int(y_chao)))


def contorno_luz(im, cor=(140, 200, 255), w=10):
    """Luz de recorte (rim light) atrás da peça."""
    a = im.getchannel("A").filter(ImageFilter.MaxFilter(w | 1)).filter(ImageFilter.GaussianBlur(w))
    g = Image.new("RGBA", im.size, cor + (255,))
    g.putalpha(a)
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.alpha_composite(g)
    out.alpha_composite(im)
    return out


def flare(img, x, y, s=1.0):
    """Brilho de lente anamórfico: risco horizontal azul + estrela fina no centro."""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for k, (w_, a) in enumerate(((24, 40), (10, 90), (3, 220))):
        d.line((0, y, W, y), fill=(120, 180, 255, a), width=int(w_ * s))
    d.line((x, y - 140 * s, x, y + 140 * s), fill=(200, 230, 255, 140), width=3)
    d.ellipse((x - 14 * s, y - 14 * s, x + 14 * s, y + 14 * s), fill=(255, 255, 255, 255))
    for dx, r in ((-260, 26), (180, 40), (420, 18)):
        d.ellipse((x + dx * s - r, y - r, x + dx * s + r, y + r), outline=(150, 200, 255, 70), width=3)
    img.alpha_composite(ov.filter(ImageFilter.GaussianBlur(3)))


def grao(img, seed=0):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 9, (H // 2, W // 2)).astype(np.int16)
    n = Image.fromarray(np.clip(n + 128, 0, 255).astype(np.uint8)).resize((W, H))
    a = np.asarray(img.convert("RGB")).astype(np.int16) + (np.asarray(n).astype(np.int16)[..., None] - 128)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


def letreiro(img, txt, y, size=96, cor=WHITE, glow=(90, 160, 255)):
    """Título de trailer: letras finas e largas com brilho metálico."""
    f = font("Bungee-Regular.ttf", size)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for k, l in enumerate(txt.split("\n")):
        d.text((540, y + k * size * 1.12), l, font=f, fill=glow + (255,), anchor="mm")
    img.alpha_composite(ov.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(img)
    for k, l in enumerate(txt.split("\n")):
        d.text((540, y + k * size * 1.12), l, font=f, fill=cor, anchor="mm")


def logo(img, w=170):
    lg = Image.open(os.path.join(ROOT, "assets", "logo_suavez.png")).convert("RGBA")
    lg = lg.resize((w, int(lg.height * w / lg.width)), Image.LANCZOS)
    card = Image.new("RGBA", (lg.width + 24, lg.height + 20), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=16, fill=WHITE)
    card.alpha_composite(lg, (12, 10))
    img.alpha_composite(card, (W - card.width - 30, 40))


def quadro_elenco():
    img = cena_escura()
    holofote(img, 540)
    luz(img, 540, 1200, 500, (40, 90, 200), 90)
    y_chao = 1330
    herois = [("heroi_1", 300), ("heroi_3", 420), ("heroi_2", 640), ("heroi_5", 540), ("heroi_7", 760)]
    objs = []
    for (n, x), h, z in zip(herois, (430, 470, 560, 470, 430), (0, 1, 3, 2, 0)):
        pass
    ordem = [("heroi_1", 190, 360), ("heroi_7", 890, 360), ("heroi_3", 360, 410), ("heroi_5", 720, 410),
             ("heroi_2", 540, 520)]
    for n, x, h in ordem:
        im = contorno_luz(peca(os.path.join(MI, n + ".png"), h))
        img.alpha_composite(im, (int(x - im.width / 2), int(y_chao - im.height)))
        objs.append((im, x))
    chao_reflexo(img, objs, y_chao)
    flare(img, 760, 640, 1.0)
    letreiro(img, "ESTE TIME\nCABE NA SUA MESA", 300, 84)
    img = grao(img, 1)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 90), fill=(0, 0, 0))
    d.rectangle((0, H - 90, W, H), fill=(0, 0, 0))
    logo(img)
    return img


def quadro_fase():
    img = cena_escura((14, 6, 6), (2, 1, 1))
    luz(img, 540, 900, 520, (200, 40, 30), 110)
    holofote(img, 540, (255, 200, 160), 50)
    cx = contorno_luz(peca(os.path.join(CX, "base.png"), 780), (255, 140, 90), 14)
    img.alpha_composite(cx, (540 - cx.width // 2, 1300 - cx.height))
    chao_reflexo(img, [(cx, 540)], 1300)
    letreiro(img, "FASE 1", 260, 120, WHITE, (255, 80, 60))
    d = ImageDraw.Draw(img)
    d.text((540, 390), "MARVEL UNITED · JOGO BASE", font=font("Poppins-ExtraBold.ttf", 48), fill=GOLD, anchor="mm")
    v1 = peca(os.path.join(MI, "vilao_1.png"), 360)
    img.alpha_composite(contorno_luz(v1, (255, 90, 60), 8), (40, 1480 - 360))
    img = grao(img, 2)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 90), fill=(0, 0, 0))
    d.rectangle((0, H - 90, W, H), fill=(0, 0, 0))
    logo(img)
    return img


def quadro_combo():
    img = cena_escura((6, 8, 24), (2, 2, 8))
    luz(img, 540, 1000, 560, (60, 40, 200), 100)
    itens = [("base", 270, 980, 470, -8), ("deadpool", 810, 980, 400, 8), ("enter_the_spider_verse", 540, 1180, 420, 0)]
    for n, x, y, h, r in itens:
        im = contorno_luz(peca(os.path.join(CX, n + ".png"), h), (120, 170, 255), 10).rotate(r, expand=True,
                                                                                        resample=Image.BICUBIC)
        img.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))
    letreiro(img, "1 BASE + 2 EXPANSÕES", 280, 70)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((170, 1450, 910, 1580), radius=30, fill=(220, 30, 50))
    d.text((540, 1515), "= 7 DIAS DE JOGO!", font=font("Bungee-Regular.ttf", 66), fill=WHITE, anchor="mm")
    d.text((540, 400), "pelo mesmo preço de cada caixa", font=font("Poppins-ExtraBold.ttf", 40), fill=GOLD, anchor="mm")
    img = grao(img, 3)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 90), fill=(0, 0, 0))
    d.rectangle((0, H - 90, W, H), fill=(0, 0, 0))
    logo(img)
    return img


if __name__ == "__main__":
    ims = [quadro_elenco(), quadro_fase(), quadro_combo()]
    sheet = Image.new("RGB", (3 * 540 + 40, 980), (20, 20, 20))
    for k, im in enumerate(ims):
        sheet.paste(im.convert("RGB").resize((540, 960), Image.LANCZOS), (10 + k * 550, 10))
    sheet.save(os.path.join(ROOT, "out", "teste_filme.jpg"), quality=90)
    print("ok")
