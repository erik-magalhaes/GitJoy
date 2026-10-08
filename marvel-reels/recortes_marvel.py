#!/usr/bin/env python3
"""Recortes do Reels dos Marvel United.

- caixas 3D das fotos das lojas (fundo branco): flood fill a partir das bordas;
- caixas 3D montadas a partir da capa (as expansões que só têm a arte da frente): frente + lateral + tampa;
- miniaturas uma por uma (fotos em fundo branco): cada pedaço separado vira um PNG.

    python3 recortes_marvel.py     # assets/caixas/*.png e assets/minis/*.png + out/recortes_teste.jpg
"""
import glob
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(ROOT, "assets", "fotos")
CX = os.path.join(ROOT, "assets", "caixas")
MI = os.path.join(ROOT, "assets", "minis")


def mascara_branco(img, tol=16, buracos=False):
    """Fundo = pixels quase brancos ligados à borda da foto."""
    branco = (np.abs(img.astype(int) - 255).max(axis=2) < tol).astype(np.uint8)
    n, lab, _, _ = cv2.connectedComponentsWithStats(branco, connectivity=4)
    externos = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])) - {0}
    fundo = np.isin(lab, list(externos)) & (branco > 0)
    if buracos:  # vãos brancos fechados (entre as pernas das miniaturas) também são fundo
        n2, lab2, st2, _ = cv2.connectedComponentsWithStats(branco, connectivity=4)
        grandes = [i for i in range(1, n2) if st2[i, 4] > 250]
        fundo |= np.isin(lab2, grandes) & (branco > 0)
    return ~fundo


def suaviza(m):
    m = m.astype(np.uint8) * 255
    return cv2.GaussianBlur(cv2.erode(m, np.ones((3, 3), np.uint8)), (3, 3), 0)


def caixa_foto(src, dst):
    img = cv2.imread(src)
    m = mascara_branco(img).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    m = lab == 1 + np.argmax(st[1:, 4])
    # a caixa é convexa: o casco tapa buracos claros perto da borda (logos brancos)
    full = np.zeros(m.shape, np.uint8)
    cv2.fillConvexPoly(full, cv2.convexHull(cv2.findNonZero(m.astype(np.uint8))), 1)
    rgba = Image.fromarray(np.dstack([cv2.cvtColor(img, cv2.COLOR_BGR2RGB), suaviza(full)]), "RGBA")
    rgba.crop(rgba.getbbox()).save(dst)


def apara_capa(path):
    """Tira a moldura lisa (cinza/branca) em volta da arte da capa."""
    im = np.asarray(Image.open(path).convert("RGB")).astype(int)
    ref = im[3, 3]
    dif = np.abs(im - ref).max(axis=2) > 30
    ys, xs = np.where(dif)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    pad = int(0.004 * im.shape[0])
    return Image.fromarray(im[y0 + pad:y1 - pad, x0 + pad:x1 - pad].astype(np.uint8))


def caixa_montada(capa, dst, prof=0.2, lado=None):
    """Caixa em 3D a partir da capa: frente reta, lateral esquerda e tampa em perspectiva (como nos renders oficiais)."""
    c = capa.convert("RGB")
    s = 1200 / c.width
    c = c.resize((1200, int(c.height * s)), Image.LANCZOS)
    w, h = c.size
    d = int(w * prof)  # profundidade da caixa
    dx, dy = int(d * 0.55), int(d * 0.32)  # recuo da lateral e da tampa
    W2, H2 = w + dx, h + dy
    out = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    # lateral: faixa da borda esquerda da arte, escurecida, em paralelogramo
    tira = c.crop((0, 0, max(8, int(w * 0.06)), h)).resize((dx, h), Image.LANCZOS)
    tira = Image.blend(tira, Image.new("RGB", tira.size, (40, 44, 58)), 0.55)
    lado_im = tira.transform((dx, H2), Image.QUAD, (0, -dy, 0, h - dy, dx, h, dx, 0), Image.BICUBIC)
    m = Image.new("L", (dx, H2), 0)
    ImageDraw.Draw(m).polygon([(0, 0), (dx, dy), (dx, H2), (0, h)], fill=255)
    lado_im = lado_im.convert("RGBA")
    lado_im.putalpha(m)
    out.alpha_composite(lado_im, (0, 0))
    # tampa: faixa do topo da arte, clareada
    topo = c.crop((0, 0, w, max(8, int(h * 0.05)))).resize((w, dy), Image.LANCZOS)
    topo = Image.blend(topo, Image.new("RGB", topo.size, (220, 225, 235)), 0.35)
    topo_im = topo.transform((W2, dy), Image.QUAD, (-dx, 0, 0, dy, w, dy, w - dx, 0), Image.BICUBIC).convert("RGBA")
    mt = Image.new("L", (W2, dy), 0)
    ImageDraw.Draw(mt).polygon([(0, 0), (dx, dy), (W2, dy), (W2 - dx, 0)], fill=255)
    topo_im.putalpha(mt)
    out.alpha_composite(topo_im, (0, 0))
    out.paste(c, (dx, dy))
    dd = ImageDraw.Draw(out)  # quinas levemente marcadas
    dd.line((dx, dy, dx, H2), fill=(20, 20, 30, 120), width=3)
    dd.line((dx, dy, W2, dy), fill=(255, 255, 255, 90), width=3)
    out.save(dst)


def minis(src, prefixo, min_frac=0.004):
    """Separa as miniaturas de uma foto em fundo branco (cada componente grande vira um PNG)."""
    img = cv2.imread(src)
    m = mascara_branco(img, 22, buracos=True).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    area = img.shape[0] * img.shape[1]
    feitos = []
    ordem = sorted([i for i in range(1, n) if st[i, 4] > area * min_frac], key=lambda i: (st[i, 1] // 300, st[i, 0]))
    for k, i in enumerate(ordem):
        x, y, w, h, _ = st[i]
        mk = (lab == i)
        mk = cv2.morphologyEx(mk.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8)) > 0
        rgba = np.dstack([cv2.cvtColor(img, cv2.COLOR_BGR2RGB), suaviza(mk)])[y:y + h, x:x + w]
        out = os.path.join(MI, f"{prefixo}_{k + 1}.png")
        Image.fromarray(rgba, "RGBA").save(out)
        feitos.append(out)
    return feitos


def main():
    os.makedirs(CX, exist_ok=True)
    os.makedirs(MI, exist_ok=True)
    for n in ("base", "xmen", "civil_war", "blue_team"):
        caixa_foto(os.path.join(F, f"caixa_{n}.jpg"), os.path.join(CX, f"{n}.png"))
    caixa_foto(os.path.join(F, "mv_1736429485827.jpg"), os.path.join(CX, "multiverse.png"))
    for n in ("deadpool", "enter-the-spider-verse", "rise-of-the-black-panther", "spider-geddon", "x-men-gold-team"):
        caixa_montada(apara_capa(os.path.join(F, f"capa_{n}.jpg")), os.path.join(CX, n.replace("-", "_") + ".png"))
    minis(os.path.join(F, "minis_herois_base.jpg"), "heroi")
    minis(os.path.join(F, "minis_viloes_base.jpg"), "vilao")
    minis(os.path.join(F, "minis_xmen.jpg"), "xmen")
    # folha de teste em fundo escuro
    fs = sorted(glob.glob(os.path.join(CX, "*.png"))) + sorted(glob.glob(os.path.join(MI, "*.png")))
    sheet = Image.new("RGB", (6 * 300, ((len(fs) + 5) // 6) * 320), (14, 16, 30))
    for k, f in enumerate(fs):
        im = Image.open(f)
        im.thumbnail((280, 280))
        sheet.paste(im, ((k % 6) * 300 + 10, (k // 6) * 320 + 10), im)
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    sheet.save(os.path.join(ROOT, "out", "recortes_teste.jpg"), quality=90)
    print(len(fs), "recortes")


if __name__ == "__main__":
    main()
