#!/usr/bin/env python3
"""Wonderland's War em PRIMEIRA PESSOA ("óculos de realidade virtual"): câmera baixa andando sobre o tabuleiro oficial
(foto da Galápagos retificada e ampliada 4x por IA, assets/orig/tabuleiro_x4.jpg, fora do git).
Teste:  python3 pov.py --teste   → out/teste_pov.jpg"""
import math
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "comum"))
from motor import W, H, font, cola, sombra  # noqa: E402

OUT = os.path.join(ROOT, "out")
AS = os.path.join(ROOT, "assets")
_TAB = None


def tab():
    global _TAB
    if _TAB is None:
        _TAB = cv2.imread(os.path.join(AS, "orig", "tabuleiro_x4.jpg"))[..., ::-1].copy()
    return _TAB


def camera(cx, cy, h, yaw, pitch, f=820, ceu=None):
    """Projeta o tabuleiro (plano z=0, unidades = px do tabuleiro_x4) visto de (cx,cy,h); yaw 0 = olhando para -y
    (para o alto do tabuleiro), pitch = graus para baixo. Devolve RGB uint8 HxW e a matriz para projetar pontos."""
    T = tab()
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    dx = (xs - W / 2) / f
    dy = -(ys - H / 2) / f
    dz = np.ones_like(dx)
    p = math.radians(pitch)
    # inclina para baixo (gira em torno do eixo x da câmera)
    y2 = dy * math.cos(p) - dz * math.sin(p)
    z2 = dy * math.sin(p) + dz * math.cos(p)
    a = math.radians(yaw)
    # mundo: x direita, y para baixo no tabuleiro, z para cima; frente da câmera (z2) aponta para (sin a, -cos a)
    wx = dx * math.cos(a) + z2 * math.sin(a)
    wy = dx * math.sin(a) - z2 * math.cos(a)
    wz = y2
    t = np.where(wz < -1e-4, h / -np.minimum(wz, -1e-4), 1e9)
    u = (cx + wx * t).astype(np.float32)
    v = (cy + wy * t).astype(np.float32)
    img = cv2.remap(T, u, v, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(28, 10, 40))
    dist = np.where(wz < -1e-4, t, 1e9)
    fog = np.clip((dist - 2.2 * h) / (9 * h), 0, 1)[..., None]
    ceu_ = ceu if ceu is not None else fundo_ceu()
    out = img * (1 - fog * 0.85) + ceu_ * (fog * 0.85)
    out = np.where((wz >= -1e-4)[..., None], ceu_, out)
    return out.clip(0, 255).astype(np.uint8), (cx, cy, h, yaw, pitch, f)


def projeta(cam, x, y, z=0.0):
    cx, cy, h, yaw, pitch, f = cam
    a, p = math.radians(yaw), math.radians(pitch)
    rx, ry, rz = x - cx, y - cy, z - h
    # inverso de camera(): direção mundo -> câmera
    dxc = rx * math.cos(a) + ry * math.sin(a)
    z2 = rx * math.sin(a) - ry * math.cos(a)
    y2 = rz
    dy = y2 * math.cos(p) + z2 * math.sin(p)
    dz = -y2 * math.sin(p) + z2 * math.cos(p)
    if dz <= 1:
        return None
    return W / 2 + f * dxc / dz, H / 2 - f * dy / dz, f / dz


_CEU = None


def fundo_ceu():
    global _CEU
    if _CEU is None:
        y = np.linspace(0, 1, H)[:, None, None]
        topo, base = np.array([18, 6, 34.]), np.array([120, 50, 140.])
        c = topo * (1 - y) + base * y
        c = np.broadcast_to(c, (H, W, 3)).copy()
        rng = np.random.default_rng(3)
        for _ in range(260):
            x0, y0 = rng.integers(0, W), rng.integers(0, H // 2)
            c[y0:y0 + 2, x0:x0 + 2] = (255, 230, 255)
        _CEU = c
    return _CEU


_P = {}


def pers(n):
    if n not in _P:
        im = Image.open(os.path.join(AS, "pers", n + ".png")).convert("RGBA")
        a = np.asarray(im).copy()
        if n == "chapeleiro":
            a[:150, 250:, 3] = 0
        lum = a[..., :3].mean(2)
        a[..., 3] = np.where((lum > 228) & (np.arange(a.shape[0])[:, None] > a.shape[0] * 0.8), 0, a[..., 3])
        im = Image.fromarray(a, "RGBA")
        _P[n] = im.crop(im.getbbox())
    return _P[n]


def standee(img, cam, n, x, y, alt=330):
    r = projeta(cam, x, y)
    if r is None:
        return
    sx, sy, esc = r
    p = pers(n)
    hh = alt * esc
    if hh < 8 or hh > 4000:
        return
    q = p.resize((max(2, int(p.width * hh / p.height)), int(hh)), Image.LANCZOS)
    img.alpha_composite(sombra(q, 10, (0, 8), 0.45), (int(sx - q.width / 2 - 20), int(sy - q.height - 20)))
    img.alpha_composite(q, (int(sx - q.width / 2), int(sy - q.height)))


def oculos(img, t=0.0, txt=None):
    """Moldura de óculos VR: vinheta nas bordas em formato de lente + HUD fino."""
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle((26, 60, W - 26, H - 60), radius=170, fill=255)
    m = m.filter(ImageFilter.GaussianBlur(40))
    preto = Image.new("RGBA", (W, H), (6, 2, 12, 255))
    preto.putalpha(Image.eval(m, lambda v: 255 - v))
    img.alpha_composite(preto)
    hud = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(hud)
    c = (200, 255, 240, 170)
    for (x, y, sx, sy) in ((120, 190, 1, 1), (W - 120, 190, -1, 1), (120, H - 330, 1, -1), (W - 120, H - 330, -1, -1)):
        d.line((x, y, x + 60 * sx, y), fill=c, width=4)
        d.line((x, y, x, y + 60 * sy), fill=c, width=4)
    d.ellipse((W / 2 - 8, H / 2 - 8, W / 2 + 8, H / 2 + 8), outline=c, width=3)
    if txt:
        d.text((150, 215), txt, font=font("Bungee-Regular.ttf", 34), fill=c)
    img.alpha_composite(hud)


def teste():
    os.makedirs(OUT, exist_ok=True)
    quadros = []
    # 1 sentado na mesa do Chá Maluco olhando os outros líderes
    rgb, cam = camera(1700, 2600, 300, -60, 18)
    im = Image.fromarray(rgb).convert("RGBA")
    standee(im, cam, "chapeleiro", 900, 1500)
    standee(im, cam, "rainha", 1250, 1150)
    oculos(im, txt="RODADA I · CHÁ MALUCO")
    quadros.append(im)
    # 2 andando por uma região (floresta verde à esquerda)
    rgb, cam = camera(900, 2500, 180, -10, 12)
    im = Image.fromarray(rgb).convert("RGBA")
    oculos(im, txt="REGIÃO: FLORESTA")
    quadros.append(im)
    # 3 visão alta: o tabuleiro todo
    rgb, cam = camera(1280, 4300, 1500, 0, 32)
    im = Image.fromarray(rgb).convert("RGBA")
    oculos(im, txt="ENTRANDO NO PAÍS DAS MARAVILHAS")
    quadros.append(im)
    s = 0.4
    fo = Image.new("RGB", (int(W * s) * 3 + 40, int(H * s)), "white")
    for i, q in enumerate(quadros):
        fo.paste(q.convert("RGB").resize((int(W * s), int(H * s))), (i * (int(W * s) + 20), 0))
    fo.save(os.path.join(OUT, "teste_pov.jpg"), quality=90)


if __name__ == "__main__":
    teste()
