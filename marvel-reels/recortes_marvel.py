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


def caixa_no_molde(capa_path, molde_png, dst, frente, lado):
    """Aplica uma capa oficial na foto 3D oficial de outra caixa do MESMO formato (luz e quinas de verdade).
    frente/lado = quinas (TL, TR, BR, BL) da face na foto do molde, em pixels."""
    molde = np.asarray(Image.open(molde_png).convert("RGBA")).copy()
    h, w = molde.shape[:2]
    capa = np.asarray(apara_capa(capa_path).convert("RGB"))
    ch, cw = capa.shape[:2]

    def warp(src, quad):
        sh, sw = src.shape[:2]
        M = cv2.getPerspectiveTransform(np.float32([[0, 0], [sw, 0], [sw, sh], [0, sh]]), np.float32(quad))
        img = cv2.warpPerspective(src, M, (w, h), flags=cv2.INTER_CUBIC)
        mk = cv2.warpPerspective(np.full((sh, sw), 255, np.uint8), M, (w, h))
        return img, mk

    # sombreamento da foto original (luz da face), para manter o volume
    luz = cv2.cvtColor(molde[..., :3], cv2.COLOR_RGB2GRAY).astype(float)
    f_img, f_m = warp(capa, frente)
    lado_src = cv2.resize(capa[:, :int(cw * 0.14)], (int(cw * 0.14), ch))
    l_img, l_m = warp((lado_src * 0.72).astype(np.uint8), lado)
    out = molde.copy()
    for img, mk in ((l_img, l_m), (f_img, f_m)):
        sel = (mk > 128) & (molde[..., 3] > 0)
        out[sel, :3] = img[sel]
    rgba = Image.fromarray(out, "RGBA")
    rgba.save(dst)


def main():
    os.makedirs(CX, exist_ok=True)
    os.makedirs(MI, exist_ok=True)
    for n in ("base", "xmen", "civil_war", "blue_team"):  # fotos 3D da Bravo (Civil War: a oficial tem lateral branca)
        caixa_foto(os.path.join(F, f"caixa_{n}.jpg"), os.path.join(CX, f"{n}.png"))
    caixa_foto(os.path.join(F, "mv_1736429485827.jpg"), os.path.join(CX, "multiverse.png"))
    # fotos 3D oficiais (Spin Master/CMON) das lojas: muito melhores que montar a caixa a partir da capa
    for n, arq in (("deadpool", "oficial_deadpool"),
                   ("spider_geddon", "oficial_spider_geddon"), ("rise_of_the_black_panther", "oficial_black_panther"),
                   ("enter_the_spider_verse", "oficial_spider_verse")):
        caixa_foto(os.path.join(F, arq + ".jpg"), os.path.join(CX, n + ".png"))
    # Gold Team: só existe a capa; aplicada na foto 3D oficial da Blue Team (mesmo formato de caixa)
    caixa_no_molde(os.path.join(F, "capa_x-men-gold-team.jpg"), os.path.join(CX, "blue_team.png"),
                   os.path.join(CX, "x_men_gold_team.png"),
                   [(196, 126), (1320, 27), (1259, 1241), (195, 1597)], [(3, 121), (196, 126), (195, 1597), (73, 1484)])
    minis(os.path.join(F, "minis_herois_base.jpg"), "heroi")
    minis(os.path.join(F, "minis_viloes_base.jpg"), "vilao")
    minis(os.path.join(F, "minis_xmen.jpg"), "xmen")
    minis(os.path.join(F, "minis_black_panther.jpg"), "panther")
    minis(os.path.join(F, "minis_spider_verse.jpg"), "aranha")
    minis(os.path.join(F, "minis_civil_war.jpg"), "civil", 0.0015)
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
