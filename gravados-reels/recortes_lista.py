#!/usr/bin/env python3
"""Caixas OFICIAIS dos jogos do vídeo "5, 4, 3, 2, 1" (edições que a loja tem):
Galápagos (loja.galapagosjogos.com.br, API ccstore/v1/search): Harmonies, Azul, Azul Duel, Splendor Duel, Ticket to Ride,
Dixit, Jaipur, The Resistance, Marvel United, Hitster. Grok (loja.grokgames.com.br): Flip 7. Compara Jogos (og:image, edição
BR conferida no olho): King of Tokyo (Devir), Coup (Funbox, 2ª ed.), Trio (PaperGames). boop. = edição original (Smirk &
Laughter), que é a caixa da loja. Originais em assets/lista/orig/ (fora do git).

    python3 recortes_lista.py      # assets/lista/<jogo>.png (altura 900, fundo transparente)
"""
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ORIG = os.path.join(HERE, "assets", "lista", "orig")
OUT = os.path.join(HERE, "assets", "lista")
CAPAS = {"king_of_tokyo", "coup", "trio", "boop"}  # capas retas (sem foto 3D): cantinho arredondado


def fundo_branco(a, tol=16):
    h, w = a.shape[:2]
    ref = np.median(np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]]), 0)
    cheio = (np.abs(a.astype(int) - ref).max(2) < tol).astype(np.uint8)
    m = np.zeros((h + 2, w + 2), np.uint8)
    for x, y in [(x, 0) for x in range(0, w, 15)] + [(x, h - 1) for x in range(0, w, 15)] + \
            [(0, y) for y in range(0, h, 15)] + [(w - 1, y) for y in range(0, h, 15)]:
        if cheio[y, x] == 1:
            cv2.floodFill(cheio, m, (x, y), 2)
    obj = (cheio != 2).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(obj)
    obj = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    alfa = np.zeros((h, w), np.uint8)
    cv2.fillPoly(alfa, [cv2.convexHull(cv2.findNonZero(obj))], 255)
    return cv2.erode(alfa, np.ones((3, 3), np.uint8))


def recorta(nome):
    im = Image.open(os.path.join(ORIG, nome + ".png"))
    if nome in CAPAS:
        im = im.convert("RGB")
        a = np.array(im)
        # capa com margem branca? corta pelo conteúdo
        alfa = fundo_branco(a, 10) if a[0].mean() > 235 and a[-1].mean() > 235 else None
        im = im.convert("RGBA")
        if alfa is not None:
            im.putalpha(Image.fromarray(alfa))
            im = im.crop(im.getbbox())
        m = Image.new("L", im.size, 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=im.width // 45, fill=255)
        im.putalpha(m)
    elif im.mode == "RGBA" and np.array(im)[..., 3].min() < 10:
        im = im.crop(im.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox())
    else:
        a = np.array(im.convert("RGB"))
        im = Image.fromarray(np.dstack([a, fundo_branco(a)]), "RGBA")
        im = im.crop(im.getbbox())
        im.putalpha(im.getchannel("A").filter(ImageFilter.GaussianBlur(0.8)))
    im = im.resize((int(im.width * 900 / im.height), 900), Image.LANCZOS)
    im.save(os.path.join(OUT, nome + ".png"), optimize=True)
    print("ok", nome, im.size)


if __name__ == "__main__":
    for f in sorted(os.listdir(ORIG)):
        recorta(f[:-4])
