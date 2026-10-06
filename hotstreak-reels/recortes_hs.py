#!/usr/bin/env python3
"""Recortes do Hot Streak: bonecos de vinil da foto oficial (fundo verde da pista + branco) com GrabCut."""
import os

import cv2
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(ROOT, "assets", "fotos")
P = os.path.join(ROOT, "assets", "pecas")


def fundo_pista(c):
    """Máscara do fundo: verde da pista, linhas/estrelas brancas e o branco da mesa."""
    hsv = cv2.cvtColor(c, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    verde = (h > 40) & (h < 90) & (s > 70) & (v > 60)
    branco = (s < 35) & (v > 170)
    return verde | branco


def recorta(img, box, keep=1, out=None, scale=0.5):
    x0, y0, x1, y1 = box
    c = img[y0:y1, x0:x1].copy()
    bg = fundo_pista(c)
    mask = np.where(bg, cv2.GC_PR_BGD, cv2.GC_PR_FGD).astype(np.uint8)
    mask[cv2.erode(bg.astype(np.uint8), np.ones((15, 15), np.uint8)) > 0] = cv2.GC_BGD
    mask[cv2.erode((~bg).astype(np.uint8), np.ones((25, 25), np.uint8)) > 0] = cv2.GC_FGD
    small = cv2.resize(c, None, fx=0.5, fy=0.5)
    ms = cv2.resize(mask, (small.shape[1], small.shape[0]), interpolation=cv2.INTER_NEAREST)
    bgm, fgm = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    cv2.grabCut(small, ms, None, bgm, fgm, 5, cv2.GC_INIT_WITH_MASK)
    m = np.isin(ms, (cv2.GC_FGD, cv2.GC_PR_FGD)).astype(np.uint8) * 255
    m = cv2.resize(m, (c.shape[1], c.shape[0]), interpolation=cv2.INTER_LINEAR)
    m = (m > 127).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    order = np.argsort(-st[1:, 4])[:keep] + 1
    m = np.isin(lab, order).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    full = np.zeros_like(m)
    cv2.drawContours(full, cs, -1, 255, -1)
    full = cv2.GaussianBlur(cv2.erode(full, np.ones((3, 3), np.uint8)), (5, 5), 0)
    rgba = Image.fromarray(np.dstack([cv2.cvtColor(c, cv2.COLOR_BGR2RGB), full]), "RGBA")
    rgba = rgba.crop(rgba.getbbox())
    rgba = rgba.resize((int(rgba.width * scale), int(rgba.height * scale)), Image.LANCZOS)
    rgba.save(os.path.join(P, out))
    return rgba


def main():
    os.makedirs(P, exist_ok=True)
    img = cv2.imread(os.path.join(F, "HS4751.jpg"))
    recorta(img, (1300, 1750, 2150, 2950), out="hurley.png")
    recorta(img, (3650, 1180, 4480, 2300), out="dangle.png")
    recorta(img, (2950, 2580, 4150, 3720), out="gobbler_caido.png")
    print("ok", sorted(os.listdir(P)))


if __name__ == "__main__":
    main()


def caixa():
    """Caixa do jogo (foto oficial em fundo vermelho liso): GrabCut com o fundo marcado pela cor."""
    img = cv2.imread(os.path.join(F, "HS4378_2.jpg"))
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    ref = np.median(np.concatenate([lab[:60].reshape(-1, 3), lab[-60:].reshape(-1, 3)]), 0)
    dist = np.linalg.norm(lab - ref, axis=2)
    # fundo e também a sombra (mesmo tom de vermelho, só mais escura)
    dab = np.linalg.norm(lab[..., 1:] - ref[1:], axis=2)
    bg = (dist < 14) | ((dab < 12) & (lab[..., 0] < ref[0] + 6))
    mask = np.where(bg, cv2.GC_PR_BGD, cv2.GC_PR_FGD).astype(np.uint8)
    mask[cv2.erode(bg.astype(np.uint8), np.ones((21, 21), np.uint8)) > 0] = cv2.GC_BGD
    mask[cv2.erode((~bg).astype(np.uint8), np.ones((31, 31), np.uint8)) > 0] = cv2.GC_FGD
    bgm, fgm = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    cv2.grabCut(img, mask, None, bgm, fgm, 4, cv2.GC_INIT_WITH_MASK)
    m = np.isin(mask, (cv2.GC_FGD, cv2.GC_PR_FGD)).astype(np.uint8)
    n, labs, st, _ = cv2.connectedComponentsWithStats(m)
    m = (labs == 1 + np.argmax(st[1:, 4])).astype(np.uint8)
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    full = np.zeros_like(m)
    cv2.drawContours(full, cs, -1, 255, -1)
    full = cv2.GaussianBlur(cv2.erode(full, np.ones((3, 3), np.uint8)), (5, 5), 0)
    rgba = Image.fromarray(np.dstack([cv2.cvtColor(img, cv2.COLOR_BGR2RGB), full]), "RGBA")
    rgba.crop(rgba.getbbox()).save(os.path.join(P, "caixa.png"))


def bilhetes_br(urso="Gluglu"):
    """Bilhetes com os nomes da edição brasileira: troca "Gobbler" pelo nome do urso e "YES" por "SIM"."""
    from PIL import ImageDraw, ImageFont
    fn = os.path.join(ROOT, "assets", "fonts")
    for lado in ("safe", "risky"):
        im = Image.open(os.path.join(P, f"ticket_gobbler_{lado}.png")).convert("RGBA")
        d = ImageDraw.Draw(im)
        mag = im.getpixel((70, 550))[:3]
        txt = im.getpixel((150, 95))[:3]
        d.rounded_rectangle((52, 58, 283, 142), radius=18, fill=mag)
        d.rounded_rectangle((52, 500, 283, 612), radius=18, fill=mag)
        f = ImageFont.truetype(os.path.join(fn, "AlfaSlabOne-Regular.ttf"), 56)
        d.text((167, 100), urso, font=f, fill=txt, anchor="mm")
        f2 = ImageFont.truetype(os.path.join(fn, "AlfaSlabOne-Regular.ttf"), 40)
        d.text((167, 556), "O Urso", font=f2, fill=txt, anchor="mm")
        im.save(os.path.join(P, f"ticket_urso_{lado}.png"))
        im = Image.open(os.path.join(P, f"ticket_yes_{lado}.png")).convert("RGBA")
        d = ImageDraw.Draw(im)
        painel = im.getpixel((60, 330))[:3]
        verde = im.getpixel((100, 300))[:3]
        d.rounded_rectangle((52, 62, 288, 628), radius=20, fill=painel)
        lay = Image.new("RGBA", (566, 236), (0, 0, 0, 0))
        ImageDraw.Draw(lay).text((283, 118), "SIM", font=ImageFont.truetype(os.path.join(fn, "Bungee-Regular.ttf"),
                                                                             190), fill=verde, anchor="mm")
        lay = lay.rotate(90, expand=True)
        im.alpha_composite(lay, (52, 62))
        im.save(os.path.join(P, f"ticket_sim_{lado}.png"))
