#!/usr/bin/env python3
"""Fotos OFICIAIS das caixas (fotos de divulgação das editoras publicadas nas lojas Shopify):
EDIÇÕES ATUAIS/BRASILEIRAS (pedido dele): cuckoo_devir.jpg (edição nova da Devir, 2023, foto da Bravo Jogos),
draft_meeplebr.png (caixa 3D da MeepleBR, site da editora), gravity.jpg (Sit Down!/Luma, Shop of Magic; a caixa dele é a
mesma arte da Sit Down!), scooby.jpg (capa da CMON, igual à caixa dele). Recorte do fundo branco por flood fill a partir das bordas + casco convexo.

    python3 recortes_oficiais.py      # assets/oficial/*.png
"""
import os

import cv2
import numpy as np
from PIL import Image, ImageFilter

OF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "oficial")


def recorta(nome, saida, tol=18, caixa=None, sombra_cinza=False):
    a = Image.open(os.path.join(OF, nome)).convert("RGB")
    if caixa:
        a = a.crop(caixa)
    a = np.array(a)
    h, w = a.shape[:2]
    ref = np.median(np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]]), 0)  # cor do fundo (branco ou cinza claro)
    fundo = np.abs(a.astype(int) - ref).max(2) < tol
    if sombra_cinza:  # sombra cinza no chão (sem cor) também é fundo
        ai = a.astype(int)
        fundo |= ((ai.max(2) - ai.min(2)) < 10) & (ai.min(2) > 120)
    fundo = fundo.astype(np.uint8)
    m = np.zeros((h + 2, w + 2), np.uint8)
    cheio = fundo.copy()
    for x, y in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)] + [(x, 0) for x in range(0, w, 20)] + \
            [(x, h - 1) for x in range(0, w, 20)] + [(0, y) for y in range(0, h, 20)] + [(w - 1, y) for y in range(0, h, 20)]:
        if cheio[y, x] == 1:
            cv2.floodFill(cheio, m, (x, y), 2)
    obj = (cheio != 2).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(obj)
    obj = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    pts = cv2.findNonZero(obj)
    alfa = np.zeros((h, w), np.uint8)
    cv2.fillPoly(alfa, [cv2.convexHull(pts)], 255)
    alfa = cv2.erode(alfa, np.ones((3, 3), np.uint8))
    im = Image.fromarray(np.dstack([a, alfa]), "RGBA")
    im = im.crop(im.getbbox())
    im.putalpha(im.getchannel("A").filter(ImageFilter.GaussianBlur(0.8)))
    im.save(os.path.join(OF, saida))
    print("ok", saida, im.size)


if __name__ == "__main__":
    recorta("cuckoo_devir.jpg", "go_cuckoo.png", 14)
    recorta("gravity.jpg", "gravity_superstar.png")
    recorta("draft_meeplebr.png", "draftosaurus.png", 12, (150, 150, 820, 760), True)  # sem a marca d'água da editora
    sc = Image.open(os.path.join(OF, "scooby.jpg")).convert("RGBA")  # capa reta (sem foto 3D oficial)
    sc.save(os.path.join(OF, "scooby_doo.png"))
    print("ok scooby_doo.png", sc.size)
