#!/usr/bin/env python3
"""Ícones oficiais de ação do Marvel United (Mover, Atacar, Ação Heroica, Coringa), renderizados direto do
manual oficial da CMON (pág. 8), em alta resolução e sem a textura de papel do fundo.
(Os ícones têm degradês, então não dá para redesenhar traço a traço como no Hot Streak:
a textura do fundo é trocada por uma imagem transparente e a página é renderizada com alfa.)

    curl -sL -o manual.pdf https://cmon-files.s3.amazonaws.com/pdf/assets_item/resource/202/Marvel_United_Rulebook.pdf
    python3 icones_oficiais.py manual.pdf     # assets/minis/icone_{mover,atacar,heroica,coringa}.png
"""
import os
import sys

import cv2
import numpy as np
import pymupdf
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
MI = os.path.join(ROOT, "assets", "minis")
# caixas (em pontos) em volta de cada ícone, ao lado do título da ação na pág. 8
ICONES = {"mover": (78, 85, 135, 125), "atacar": (88, 140, 142, 185),
          "heroica": (130, 308, 192, 355), "coringa": (78, 430, 130, 470)}
TEXTURA = 5347  # xref da textura de papel do fundo da página


def main(pdf, dpi=1000):
    page = pymupdf.open(pdf)[7]
    vazio = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 4, 4), True)
    vazio.clear_with(0)
    page.replace_image(TEXTURA, pixmap=vazio)
    for nome, box in ICONES.items():
        px = page.get_pixmap(dpi=dpi, clip=pymupdf.Rect(box), alpha=True)
        a = np.asarray(Image.frombytes("RGBA", (px.width, px.height), px.samples)).copy()
        # sobra uma camada preta a 50% (127) no fundo: o ícone é o maior pedaço opaco (o contorno preto fecha tudo)
        op = (a[..., 3] > 235).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats(op)
        ic = lab == 1 + np.argmax(st[1:, 4])
        ic = cv2.morphologyEx(ic.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        alfa = cv2.GaussianBlur(cv2.dilate(ic * 255, np.ones((3, 3), np.uint8)), (3, 3), 0)
        a[..., 3] = alfa
        im = Image.fromarray(a, "RGBA")
        im = im.crop(im.getbbox())
        im.save(os.path.join(MI, f"icone_{nome}.png"))
        print(nome, im.size)


if __name__ == "__main__":
    main(sys.argv[1])
