#!/usr/bin/env python3
"""Recorta as peças usadas no vídeo a partir das fotos (cartas por perspectiva, maravilha por fundo claro)."""
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(ROOT, "assets", "fotos")
P = os.path.join(ROOT, "assets", "pecas")
CW, CH = 540, 800

# quinas (TL, TR, BR, BL) de cada carta na foto
CARTAS = {
    "carta_azul_gato": ("b18.jpg", [(1115, 545), (1465, 690), (1406, 1168), (1002, 1080)]),
    "carta_vidro": ("b19.jpg", [(1230, 868), (1424, 950), (1316, 1240), (1114, 1150)]),
    "carta_vermelha": ("b18.jpg", [(1480, 695), (1810, 825), (1790, 1330), (1410, 1190)]),
}


def autolevels(w, lo=1.0, hi=99.5):
    out = np.empty_like(w)
    for c in range(3):
        a, b = np.percentile(w[..., c], (lo, hi))
        out[..., c] = np.clip((w[..., c].astype(np.float32) - a) * 255 / max(1, b - a), 0, 255)
    return out


def levels_l(w, lo=1.0, hi=99.0, chroma=1.3):
    """Estica só a luminância (tira o brilho lavado sem mudar a cor) e reforça a cor."""
    lab = cv2.cvtColor(w, cv2.COLOR_BGR2LAB).astype(np.float32)
    a, b = np.percentile(lab[..., 0], (lo, hi))
    lab[..., 0] = np.clip((lab[..., 0] - a) * 255 / max(1, b - a), 0, 255)
    lab[..., 1:] = np.clip((lab[..., 1:] - 128) * chroma + 128, 0, 255)
    return cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)


def card(src, quad, inset=6):
    im = cv2.imread(os.path.join(F, src))
    M = cv2.getPerspectiveTransform(np.float32(quad), np.float32([(0, 0), (CW, 0), (CW, CH), (0, CH)]))
    w = cv2.warpPerspective(im, M, (CW, CH), flags=cv2.INTER_CUBIC)
    w = w[inset:CH - inset, inset:CW - inset]
    w = cv2.resize(w, (CW, CH), interpolation=cv2.INTER_CUBIC)
    w = levels_l(w, chroma=1.0 if src == "b3.jpg" else 1.3)
    # foto de celular é lavada: um pouco mais de contraste e saturação
    if src != "b3.jpg":  # a foto em fundo preto já é saturada
        hsv = cv2.cvtColor(w, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[..., 1] = np.clip(hsv[..., 1] * 1.25, 0, 255)
        w = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        w = np.clip((w.astype(np.float32) - 128) * 1.12 + 128 + 6, 0, 255).astype(np.uint8)
    img = Image.fromarray(cv2.cvtColor(w, cv2.COLOR_BGR2RGB)).convert("RGBA")
    m = Image.new("L", (CW, CH), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, CW - 1, CH - 1), radius=34, fill=255)
    img.putalpha(m)
    return img


# peças fotografadas em fundo preto (b3.jpg): (x, y, w, h)
PRETO = {
    "fichas_vitoria": (447, 304, 366, 258), "conflito_guerra": (969, 538, 121, 107),
    "conflito_paz": (920, 654, 123, 111), "progresso_a": (1540, 538, 118, 108),
    "progresso_b": (641, 1031, 115, 112), "progresso_c": (821, 1047, 119, 114),
    "progresso_d": (1582, 1082, 125, 120), "progresso_verso": (316, 971, 128, 122),
    "monte_central": (512, 812, 259, 175), "monte_suporte": (732, 1341, 218, 284)
}


def cut_black(name, box, thr=55, pad=6):
    im = cv2.imread(os.path.join(F, "b3.jpg"))
    x, y, w, h = box
    c = im[max(0, y - pad):y + h + pad, max(0, x - pad):x + w + pad]
    g = cv2.cvtColor(c, cv2.COLOR_BGR2GRAY)
    m = (g > thr).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    k = 1 + int(np.argmax(st[1:, 4])) if name != "fichas_vitoria" else None
    keep = (lab == k) if k else (m > 0)
    cs, _ = cv2.findContours(keep.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    full = np.zeros_like(m)
    cv2.drawContours(full, [cc for cc in cs if cv2.contourArea(cc) > 400], -1, 255, -1)
    full = cv2.erode(full, np.ones((3, 3), np.uint8))
    a = cv2.GaussianBlur(full, (3, 3), 0)
    rgb = cv2.cvtColor(autolevels(c, 0.5, 99.8), cv2.COLOR_BGR2RGB)
    img = Image.fromarray(np.dstack([rgb, a]), "RGBA")
    img = img.crop(img.getbbox())
    img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
    if name == "gato":  # tira o pedaço da maravilha que encosta no peão
        m = img.getchannel("A")
        ImageDraw.Draw(m).polygon([(298, 130), (252, 255), (190, img.height), (img.width, img.height),
                                   (img.width, 130)], fill=0)
        img.putalpha(m)
        img = img.crop(img.getbbox())
    img.save(os.path.join(P, name + ".png"))


def card_black(name, box, pad=8):
    """Carta inteira em fundo preto: acha o retângulo girado e desentorta."""
    im = cv2.imread(os.path.join(F, "b3.jpg"))
    x, y, w, h = box
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    m = np.zeros_like(g)
    m[y - pad:y + h + pad, x - pad:x + w + pad] = (g[y - pad:y + h + pad, x - pad:x + w + pad] > 60)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=cv2.contourArea)
    pts = cv2.boxPoints(cv2.minAreaRect(c))
    # ordena TL, TR, BR, BL com o lado maior na vertical
    pts = sorted(pts, key=lambda p: p[1])
    top, bot = sorted(pts[:2], key=lambda p: p[0]), sorted(pts[2:], key=lambda p: p[0])
    quad = [top[0], top[1], bot[1], bot[0]]
    d = lambda a, b: np.hypot(*(np.array(a) - np.array(b)))
    if d(quad[0], quad[1]) > d(quad[1], quad[2]):  # deitada: gira a ordem
        quad = [quad[3], quad[0], quad[1], quad[2]]
    return quad


def cut_white(name, src, box, thr=236):
    """Peça em fundo branco: tudo que é quase branco e encosta na borda vira transparente."""
    im = cv2.imread(os.path.join(F, src))
    x0, y0, x1, y1 = box
    c = im[y0:y1, x0:x1].copy()
    bg = (c.min(2) > thr).astype(np.uint8)
    ff = bg.copy()
    h, w = bg.shape
    mask = np.zeros((h + 2, w + 2), np.uint8)
    for sx, sy in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        if ff[sy, sx]:
            cv2.floodFill(ff, mask, (sx, sy), 2)
    fg = (ff != 2).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(fg)
    fg = (lab == 1 + int(np.argmax(st[1:, 4]))).astype(np.uint8) * 255
    fg = cv2.erode(fg, np.ones((3, 3), np.uint8))
    a = cv2.GaussianBlur(fg, (3, 3), 0)
    rgb = cv2.cvtColor(c, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(np.dstack([rgb, a]), "RGBA")
    img.crop(img.getbbox()).save(os.path.join(P, name + ".png"))


ICONES = {"pedra": (500, 950), "madeira": (700, 895), "tijolo": (890, 900), "papiro": (1080, 910),
          "vidro": (1320, 960), "sci_tabua": (690, 1690), "sci_roda": (980, 1662), "sci_compasso": (1205, 1725)}
TABULEIROS = {"alexandria": (160, 640, 600, 1150), "halicarnasso": (600, 640, 1045, 1150),
              "olimpia": (1050, 640, 1490, 1150), "rodes": (1490, 640, 1950, 1150),
              "efeso": (230, 1150, 760, 1620), "babilonia": (760, 1150, 1275, 1630), "gize": (1275, 1150, 1800, 1640)}


def icone(name, c, r=43, out=300):
    im = cv2.imread(os.path.join(F, "b19.jpg"))
    x, y = c
    w = levels_l(im[y - r:y + r, x - r:x + r], 0.5, 99.5, 1.25)
    rgb = Image.fromarray(cv2.cvtColor(w, cv2.COLOR_BGR2RGB)).resize((out, out), Image.LANCZOS)
    m = Image.new("L", (out * 4, out * 4), 0)
    ImageDraw.Draw(m).ellipse((8, 8, out * 4 - 8, out * 4 - 8), fill=255)
    rgb = rgb.convert("RGBA")
    rgb.putalpha(m.resize((out, out), Image.LANCZOS))
    rgb.save(os.path.join(P, "ic_" + name + ".png"))


def tabuleiro(name, box):
    im = cv2.imread(os.path.join(F, "b6.jpg"))
    x0, y0, x1, y1 = box
    w = levels_l(im[y0:y1, x0:x1], 1.0, 99.0, 1.25)
    Image.fromarray(cv2.cvtColor(w, cv2.COLOR_BGR2RGB)).save(os.path.join(P, "tab_" + name + ".jpg"), quality=93)


def main():
    for k, c in ICONES.items():
        icone(k, c)
    for k, b in TABULEIROS.items():
        tabuleiro(k, b)
    for k, b in PRETO.items():
        cut_black(k, b)
        print("ok", k)
    cut_white("maravilha_babilonia", "b2.png", (900, 700, 1655, 1375))
    cut_white("caixa", "b5.png", (0, 0, 2000, 2000), thr=245)
    print("ok maravilha/caixa")
    CARTAS["carta_ouro"] = ("b3.jpg", card_black("carta_ouro", (1232, 1681, 293, 311)))
    for k, (src, q) in CARTAS.items():
        card(src, q).save(os.path.join(P, k + ".png"))
        print("ok", k)


if __name__ == "__main__":
    main()
