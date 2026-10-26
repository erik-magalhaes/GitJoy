#!/usr/bin/env python3
"""Quadro de teste do estilo lápis (26/out/2026): monte de cartas, balão "QUEIJO!", mão batendo, nomes com setinha."""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "comum"))
from motor import logo_card  # noqa: E402
from lapis import carta, desenho, fonte, rabisco, PAPEL, GRAFITE  # noqa: E402

W, H = 1080, 1920


def papel():
    rng = np.random.default_rng(3)
    a = np.ones((H, W, 3)) * np.array(PAPEL, float)
    a += rng.normal(0, 2.2, (H, W, 1))  # fibra do papel bem leve
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


def escrita(img, txt, x, y, s, cor=GRAFITE, rot=0, fonte_nome="Kalam-Bold.ttf"):
    f = fonte(fonte_nome, s)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((x, y), txt, font=f, fill=cor, anchor="mm")
    if rot:
        lay = lay.rotate(rot, center=(x, y), resample=Image.BICUBIC)
    img.alpha_composite(lay)


def seta(img, p0, p1, rng, curva=40):
    d = ImageDraw.Draw(img)
    pts = []
    for k in range(25):
        t = k / 24
        x = p0[0] + (p1[0] - p0[0]) * t + math.sin(t * math.pi) * curva
        y = p0[1] + (p1[1] - p0[1]) * t
        pts.append((x, y))
    rabisco(d, pts, rng, larg=4, amp=1.2, passadas=2, fechado=False)
    ang = math.atan2(p1[1] - pts[-3][1], p1[0] - pts[-3][0])
    for s in (-0.55, 0.55):
        q = (p1[0] - 34 * math.cos(ang + s), p1[1] - 34 * math.sin(ang + s))
        rabisco(d, [p1, ((p1[0] + q[0]) / 2, (p1[1] + q[1]) / 2), q], rng, larg=4, amp=0.8, passadas=2, fechado=False)


def cola(img, im, cx, cy, rot=0):
    im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def main():
    rng = np.random.default_rng(5)
    img = papel()
    escrita(img, "Taco Gato Cabra", 540, 210, 96)
    escrita(img, "Queijo Pizza", 540, 320, 96)
    for k, (f, n, r, dx, dy) in enumerate([("frente_15.png", "TACO", -14, -30, 10), ("frente_28.png", "CABRA", 9, 20, -8),
                                          ("frente_39.png", "QUEIJO", -3, 0, 0)]):
        cola(img, carta(f, 400, n, k + 1), 540 + dx, 1000 + dy, r)
    balao = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(balao)
    d.ellipse((90, 520, 520, 760), fill=(255, 255, 255, 235))
    img.alpha_composite(balao)
    rabisco(ImageDraw.Draw(img), [(305 + 215 * math.cos(t), 640 + 120 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 60)[:-1]],
            rng, larg=4, amp=2, passadas=2)
    escrita(img, "QUEIJO!", 305, 640, 96, rot=4)
    mao = desenho(Image.open(os.path.join(ROOT, "assets", "openmoji", "270B-pele.png")).rotate(180), 380, 3)
    cola(img, mao, 760, 700, -25)
    escrita(img, "carta = palavra?", 770, 1430, 64, rot=-3)
    escrita(img, "BATE NA PILHA!", 760, 1520, 76, cor=(200, 60, 40), rot=-3)
    seta(img, (700, 1380), (620, 1250), rng, curva=-30)
    img.alpha_composite(logo_card(150), (W - 186, 46))
    img.convert("RGB").save(os.path.join(ROOT, "out", "teste_lapis.jpg"), quality=92)


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    main()
