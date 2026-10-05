#!/usr/bin/env python3
"""Reels do Sintonia (Wavelength) — Sua Vez Locação de Jogos.

Motion graphics vetorial (cairo, 30 quadros/s) no estilo da caixa: listras
onduladas retrô e o sintonizador animado. O espectador joga uma rodada no fim.

Uso:
  python3 sintonia.py                 # out/sintonia_preview.mp4 (legendas) e out/sintonia_limpo.mp4
  python3 sintonia.py --frame 21.5    # quadro de teste em out/frame.png
"""
import argparse
import json
import math
import os
import subprocess
import sys
from functools import lru_cache
from multiprocessing import Pool

import cairo
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import trilha  # noqa: E402

ASSETS = os.path.join(ROOT, "assets")
OUT = os.path.join(ROOT, "out")
W, H = 1080, 1920
FPS = 30
DUR = 66.0

F_BLACK = os.path.join(ASSETS, "fonts", "Poppins-Black.ttf")
F_XBOLD = os.path.join(ASSETS, "fonts", "Poppins-ExtraBold.ttf")
F_SEMI = os.path.join(ASSETS, "fonts", "Poppins-SemiBold.ttf")
F_JOSEFIN = os.path.join(ASSETS, "fonts", "JosefinSans.ttf")

# paleta tirada da arte da caixa
NAVY = (0.11, 0.14, 0.25)
CREAM = (0.97, 0.93, 0.85)
TEAL = (0.47, 0.78, 0.71)
MINT = (0.67, 0.86, 0.78)
CORAL = (0.94, 0.39, 0.29)
PINK = (0.95, 0.65, 0.71)
MUSTARD = (0.95, 0.70, 0.23)
BLUE = (0.31, 0.56, 0.75)
RED = (0.80, 0.16, 0.18)
ORANGE = (0.95, 0.60, 0.29)
WHITE = (1, 1, 1)
STRIPES = [NAVY, TEAL, CORAL, PINK, MUSTARD, MINT, BLUE, CREAM]


def rgb255(c):
    return tuple(int(v * 255) for v in c)


def ffmpeg_exe():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


# ---------------------------------------------------------------- tempo e easing
def seg(t, a, b):
    return min(1.0, max(0.0, (t - a) / (b - a)))


def out_cubic(u):
    return 1 - (1 - u) ** 3


def in_out(u):
    return u * u * (3 - 2 * u)


def out_back(u, s=1.7):
    u -= 1
    return u * u * ((s + 1) * u + s) + 1


def lerp(a, b, u):
    return a + (b - a) * u


def appear(t, t0, d=0.45, t1=None, dout=0.3):
    """Escala de entrada com overshoot (0→1) e saída suave."""
    if t < t0:
        return 0.0
    s = out_back(seg(t, t0, t0 + d))
    if t1 is not None and t > t1:
        s *= 1 - in_out(seg(t, t1, t1 + dout))
    return max(0.0, s)


# ---------------------------------------------------------------- texto (PIL → cairo)
@lru_cache(None)
def font(path, size):
    f = ImageFont.truetype(path, size)
    if path == F_JOSEFIN:
        f.set_variation_by_axes([650])
    return f


def wrap(text, fnt, maxw, tracking=0):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if line_w(test, fnt, tracking) <= maxw or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def line_w(s, fnt, tracking):
    return fnt.getlength(s) + tracking * max(0, len(s) - 1)


@lru_cache(None)
def text_img(text, size, color=NAVY, path=F_BLACK, tracking=0, maxw=940, lh=1.05, align="center"):
    fnt = font(path, size)
    lines = wrap(text, fnt, maxw, tracking) if maxw else text.split("\n")
    asc, desc = fnt.getmetrics()
    lhpx = int((asc + desc) * lh)
    wmax = int(max(line_w(l, fnt, tracking) for l in lines)) + 8
    im = Image.new("RGBA", (wmax, lhpx * len(lines) + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        lw = line_w(l, fnt, tracking)
        x = 4 + (wmax - 8 - lw) / 2 if align == "center" else 4
        y = 4 + i * lhpx
        if tracking:
            for ch in l:
                d.text((x, y), ch, font=fnt, fill=rgb255(color) + (255,))
                x += fnt.getlength(ch) + tracking
        else:
            d.text((x, y), l, font=fnt, fill=rgb255(color) + (255,))
    return im


def surf_from_pil(im):
    """RGBA (PIL) → superfície cairo ARGB32 pré-multiplicada."""
    a = np.asarray(im.convert("RGBA"), np.float32)
    al = a[..., 3:4] / 255.0
    bgra = np.empty_like(a)
    bgra[..., 0] = a[..., 2] * al[..., 0]
    bgra[..., 1] = a[..., 1] * al[..., 0]
    bgra[..., 2] = a[..., 0] * al[..., 0]
    bgra[..., 3] = a[..., 3]
    buf = np.ascontiguousarray(bgra.astype(np.uint8))
    h, w = buf.shape[:2]
    stride = cairo.ImageSurface.format_stride_for_width(cairo.FORMAT_ARGB32, w)
    if stride != w * 4:
        pad = np.zeros((h, stride), np.uint8)
        pad[:, : w * 4] = buf.reshape(h, w * 4)
        buf = pad
    s = cairo.ImageSurface.create_for_data(bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, w, h, stride)
    return s


@lru_cache(None)
def text_surf(*args, **kw):
    im = text_img(*args, **kw)
    return surf_from_pil(im), im.width, im.height


@lru_cache(None)
def image_surf(name, width):
    im = Image.open(os.path.join(ASSETS, name)).convert("RGBA")
    im = im.resize((int(width), int(im.height * width / im.width)), Image.LANCZOS)
    return surf_from_pil(im), im.width, im.height


def blit(cr, surf_wh, x, y, sc=1.0, rot=0.0, alpha=1.0, anchor=(0.5, 0.5)):
    surf, w, h = surf_wh
    if sc <= 0.03 or alpha <= 0.01:
        return
    cr.save()
    cr.translate(x, y)
    cr.rotate(math.radians(rot))
    cr.scale(sc, sc)
    cr.translate(-w * anchor[0], -h * anchor[1])
    cr.set_source_surface(surf, 0, 0)
    cr.paint_with_alpha(alpha)
    cr.restore()


def text(cr, s, x, y, size, color=NAVY, path=F_BLACK, sc=1.0, rot=0.0, alpha=1.0, tracking=0, maxw=940,
         anchor=(0.5, 0.5), lh=1.05):
    blit(cr, text_surf(s, size, color, path, tracking, maxw, lh), x, y, sc, rot, alpha, anchor)


def shadow_text(cr, s, x, y, size, color=CREAM, shadow=NAVY, off=8, **kw):
    """Título com sombra deslocada, no estilo pôster retrô."""
    text(cr, s, x + off, y + off, size, shadow, **kw)
    text(cr, s, x, y, size, color, **kw)


# ---------------------------------------------------------------- formas
def rrect(cr, x, y, w, h, r):
    cr.new_sub_path()
    cr.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    cr.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    cr.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    cr.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    cr.close_path()


def fill(cr, c, a=1.0):
    cr.set_source_rgba(*c, a)
    cr.fill()


def bg_waves(cr, t, amount=1.0, cover=0.0):
    """Fundo creme com faixas onduladas em cima e embaixo (como a caixa).
    cover 0..1 faz as faixas tomarem a tela inteira (transição)."""
    cr.set_source_rgb(*CREAM)
    cr.paint()
    n = len(STRIPES)
    band = 34
    reach = lerp(0.0, H * 0.62, cover)
    for side in (0, 1):
        for i in range(n):
            k = n - i
            depth = (k * band) * amount + reach
            if depth <= 0:
                continue
            ph = t * (0.9 + 0.12 * i) + i * 0.6 + side * 1.7
            cr.new_path()
            if side == 0:
                cr.move_to(0, 0)
                for x in range(0, W + 21, 20):
                    y = depth + 18 * math.sin(x / 95 + ph) + 10 * math.sin(x / 41 - ph * 1.3)
                    cr.line_to(x, y)
                cr.line_to(W, 0)
            else:
                cr.move_to(0, H)
                for x in range(0, W + 21, 20):
                    y = H - depth - 18 * math.sin(x / 95 - ph) - 10 * math.sin(x / 41 + ph * 1.3)
                    cr.line_to(x, y)
                cr.line_to(W, H)
            cr.close_path()
            fill(cr, STRIPES[(i + side * 3) % n])


def stars(cr, cx, cy, R, seed=3):
    rng = np.random.default_rng(seed)
    for _ in range(60):
        a = rng.uniform(0, math.pi)
        r = R * math.sqrt(rng.uniform(0.05, 1))
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        cr.arc(x, y, rng.uniform(1.2, 3.2), 0, 2 * math.pi)
        fill(cr, CREAM, rng.uniform(0.4, 0.9))


def spec_pt(cx, cy, r, a):
    ar = math.radians(a)
    return cx + r * math.sin(ar), cy - r * math.cos(ar)


BANDS = [(-14.0, -8.4, MUSTARD, "2"), (-8.4, -2.8, CORAL, "3"), (-2.8, 2.8, BLUE, "4"),
         (2.8, 8.4, CORAL, "3"), (8.4, 14.0, MUSTARD, "2")]


def dial(cr, cx, cy, R, needle=0.0, target=0.0, cover=0.0, left="", right="", glow=0.0, card_pop=1.0):
    """Sintonizador. needle/target em graus (-90 esquerda … 90 direita).
    cover: 0 fechado (alvo escondido), 1 aberto."""
    # aro serrilhado
    cr.new_path()
    teeth = 64
    for i in range(teeth * 2 + 1):
        a = math.pi + i * math.pi / (teeth * 2)
        rr = R * (1.10 if i % 2 == 0 else 1.075)
        cr.line_to(cx + rr * math.cos(a), cy + rr * math.sin(a))
    cr.line_to(cx + R * 1.10, cy + R * 0.62)
    cr.line_to(cx - R * 1.10, cy + R * 0.62)
    cr.close_path()
    fill(cr, CREAM)
    cr.arc(cx, cy, R * 1.055, math.pi, 2 * math.pi)
    cr.close_path()
    fill(cr, NAVY)
    # face
    cr.arc(cx, cy, R, math.pi, 2 * math.pi)
    cr.close_path()
    fill(cr, CREAM)
    # alvo
    for a0, a1, c, num in BANDS:
        cr.move_to(cx, cy)
        cr.arc(cx, cy, R * 0.98, math.radians(-90 + target + a0), math.radians(-90 + target + a1))
        cr.close_path()
        fill(cr, c)
    for a0, a1, c, num in BANDS:
        mid = target + (a0 + a1) / 2
        x, y = spec_pt(cx, cy, R * 0.90, mid)
        text(cr, num, x, y, int(R * 0.075), NAVY, F_XBOLD, rot=mid)
    if glow > 0:
        cr.move_to(cx, cy)
        cr.arc(cx, cy, R * 0.98, math.radians(-90 + target - 2.8), math.radians(-90 + target + 2.8))
        cr.close_path()
        fill(cr, WHITE, 0.45 * glow)
    # tampa (gira para baixo quando abre)
    phi = math.pi * in_out(cover)
    cr.save()
    cr.rectangle(cx - R * 1.2, cy - R * 1.2, R * 2.4, R * 1.2)
    cr.clip()
    cr.translate(cx, cy)
    cr.rotate(phi)
    cr.arc(0, 0, R * 1.0, math.pi, 2 * math.pi)
    cr.close_path()
    fill(cr, TEAL)
    cr.arc(0, 0, R * 0.22, math.pi, 2 * math.pi)
    cr.close_path()
    fill(cr, MINT, 0.6)
    # alavanca da tampa
    rrect(cr, R * 0.70, -R * 0.07, R * 0.45, R * 0.09, R * 0.045)
    fill(cr, MINT)
    cr.restore()
    # base estrelada
    cr.rectangle(cx - R * 1.12, cy, R * 2.24, R * 0.66)
    fill(cr, NAVY)
    cr.save()
    cr.rectangle(cx - R * 1.12, cy, R * 2.24, R * 0.66)
    cr.clip()
    stars(cr, cx, cy, R * 1.1)
    cr.restore()
    # carta com os dois extremos
    if left and card_pop > 0.03:
        cw, ch = R * 1.25, R * 0.44
        cr.save()
        cr.translate(cx, cy + R * 0.34)
        cr.scale(card_pop, card_pop)
        rrect(cr, -cw / 2, -ch / 2, cw / 2 + 2, ch, 14)
        fill(cr, PINK)
        rrect(cr, -2, -ch / 2, cw / 2 + 2, ch, 14)
        fill(cr, ORANGE)
        text(cr, left, -cw / 4, 14, int(R * 0.066), NAVY, F_XBOLD, maxw=int(cw / 2 - 30), lh=1.0)
        text(cr, right, cw / 4, 14, int(R * 0.066), NAVY, F_XBOLD, maxw=int(cw / 2 - 30), lh=1.0)
        for sx in (-1, 1):
            ax, ay = sx * cw / 4, -ch / 2 + 26
            cr.move_to(ax - 26 * sx, ay)
            cr.line_to(ax + 18 * sx, ay)
            cr.set_source_rgb(*NAVY)
            cr.set_line_width(5)
            cr.stroke()
            cr.move_to(ax + 28 * sx, ay)
            cr.line_to(ax + 12 * sx, ay - 10)
            cr.line_to(ax + 12 * sx, ay + 10)
            cr.close_path()
            fill(cr, NAVY)
        cr.restore()
    # ponteiro
    cr.save()
    cr.translate(cx, cy)
    cr.rotate(math.radians(needle))
    cr.move_to(-R * 0.022, 0)
    cr.line_to(-R * 0.010, -R * 0.93)
    cr.line_to(R * 0.010, -R * 0.93)
    cr.line_to(R * 0.022, 0)
    cr.close_path()
    fill(cr, RED)
    cr.restore()
    cr.arc(cx, cy, R * 0.16, 0, 2 * math.pi)
    fill(cr, RED)
    cr.arc(cx - R * 0.04, cy - R * 0.04, R * 0.07, 0, 2 * math.pi)
    fill(cr, WHITE, 0.25)


def bubble(cr, s, x, y, sc=1.0, tail="left", size=54, maxw=640, color=WHITE, ink=NAVY):
    if sc <= 0.03:
        return
    surf = text_surf(s, size, ink, F_XBOLD, 0, maxw, 1.05)
    w, h = surf[1] + 70, surf[2] + 50
    cr.save()
    cr.translate(x, y)
    cr.scale(sc, sc)
    rrect(cr, -w / 2 + 8, -h / 2 + 10, w, h, 40)
    fill(cr, NAVY, 0.25)
    rrect(cr, -w / 2, -h / 2, w, h, 40)
    cr.move_to(-w * 0.18 if tail == "left" else w * 0.18, h / 2 - 2)
    cr.line_to(-w * 0.30 if tail == "left" else w * 0.30, h / 2 + 50)
    cr.line_to(-w * 0.04 if tail == "left" else w * 0.04, h / 2 - 2)
    fill(cr, color)
    blit(cr, surf, 0, 0)
    cr.restore()


def chip(cr, s, x, y, sc, c=NAVY, ink=CREAM, size=50):
    if sc <= 0.03:
        return
    surf = text_surf(s, size, ink, F_XBOLD, 0, 900, 1.0)
    w, h = surf[1] + 64, surf[2] + 26
    cr.save()
    cr.translate(x, y)
    cr.scale(sc, sc)
    rrect(cr, -w / 2, -h / 2, w, h, h / 2)
    fill(cr, c)
    blit(cr, surf, 0, 2)
    cr.restore()


# ---------------------------------------------------------------- cenas
DX, DY, DR = 540, 1090, 430   # posição do sintonizador


def needle_wobble(t, center, amp):
    return center + amp * math.sin(t * 2.3) + amp * 0.4 * math.sin(t * 5.1)


def s_hook(cr, t, d):
    bg_waves(cr, t, amount=0.8)
    a = appear(t, 0.15, 0.4)
    # ponteiro indeciso, cada vez mais rápido
    nd = 55 * math.sin(t * (1.6 + t * 0.6))
    dial(cr, DX, DY, DR, needle=nd, target=0, cover=0, left="NÃO É SANDUÍCHE", right="É SANDUÍCHE",
         card_pop=appear(t, 0.5))
    shadow_text(cr, "PIZZA É UM TIPO DE", 540, 330, 74, NAVY, CORAL, 6, sc=a, path=F_BLACK)
    shadow_text(cr, "SANDUÍCHE?", 540, 450, 132, CORAL, NAVY, 9, sc=appear(t, 0.45, 0.45), path=F_BLACK)
    if t > 3.0:
        chip(cr, "RESPONDE GIRANDO O PONTEIRO", 540, 1560, appear(t, 3.0), MUSTARD, NAVY, 46)


def s_intro(cr, t, d):
    # transição: listras tomam a tela e revelam a caixa
    cover = 1 - out_cubic(seg(t, 0.0, 0.9))
    bg_waves(cr, t + 6, amount=1.0, cover=cover)
    bs = appear(t, 0.45, 0.6)
    bob = math.sin(t * 2.0) * 10
    blit(cr, image_surf("pieces/box.png", 640), 540, 960 + bob, sc=bs, rot=lerp(-12, -3, out_cubic(seg(t, 0.45, 1.2))))
    text(cr, "S I N T O N I A", 540, 330, 96, NAVY, F_JOSEFIN, sc=appear(t, 0.9), tracking=10)
    text(cr, "O JOGO DE LER A MENTE DOS AMIGOS", 540, 430, 44, CORAL, F_XBOLD, sc=appear(t, 1.3))
    # selo
    s = appear(t, 2.2, 0.5)
    if s > 0.03:
        cr.save()
        cr.translate(850, 1380)
        cr.rotate(math.radians(12 + math.sin(t * 3) * 3))
        cr.scale(s, s)
        n = 22
        cr.new_path()
        for i in range(n * 2):
            r = 150 if i % 2 == 0 else 132
            a = i * math.pi / n
            cr.line_to(r * math.cos(a), r * math.sin(a))
        cr.close_path()
        fill(cr, MUSTARD)
        text(cr, "MELHOR\nPARTY GAME\n2019", 0, 0, 40, NAVY, F_BLACK, maxw=0, lh=1.0)
        cr.restore()


def s_how(cr, t, d):
    bg_waves(cr, t + 12, amount=0.7)
    # a carta entra e o alvo é sorteado (a tampa abre só pro psíquico)
    spin = out_cubic(seg(t, 1.0, 2.6))
    target = lerp(-60, 38, spin)
    cover = in_out(seg(t, 2.6, 3.2)) * (1 - in_out(seg(t, 5.6, 6.2)))
    dial(cr, DX, DY, DR, needle=-70, target=target, cover=cover, left="DIFÍCIL DE ACHAR", right="FÁCIL DE ACHAR",
         card_pop=appear(t, 0.3))
    text(cr, "COMO FUNCIONA", 540, 250, 50, CORAL, F_BLACK, sc=appear(t, 0.1), tracking=4)
    shadow_text(cr, "UMA CARTA, DOIS EXTREMOS", 540, 340, 58, NAVY, MUSTARD, 5, sc=appear(t, 0.3), maxw=1000)
    if t > 2.7:
        a = appear(t, 2.7, 0.4, 6.0)
        chip(cr, "SÓ O PSÍQUICO VÊ ONDE ESTÁ O ALVO", 540, 1560, a, NAVY, CREAM, 44)
        # "olhinho" espiando
        if a > 0.03:
            cr.save()
            cr.translate(540, 500)
            cr.scale(a, a)
            cr.save()
            cr.scale(1, 0.55)
            cr.arc(0, 0, 90, 0, 2 * math.pi)
            cr.restore()
            fill(cr, WHITE)
            cr.arc(0, 0, 38, 0, 2 * math.pi)
            fill(cr, NAVY)
            cr.arc(12, -10, 10, 0, 2 * math.pi)
            fill(cr, WHITE)
            cr.restore()


TARGET_KEYS = 38.0


def s_clue(cr, t, d):
    bg_waves(cr, t + 20, amount=0.7)
    dial(cr, DX, DY, DR, needle=-70, target=TARGET_KEYS, cover=0, left="DIFÍCIL DE ACHAR", right="FÁCIL DE ACHAR")
    text(cr, "O PSÍQUICO DÁ UMA DICA:", 540, 320, 56, NAVY, F_BLACK, sc=appear(t, 0.1))
    bob = math.sin(t * 3) * 6
    bubble(cr, "MINHAS CHAVES!", 540, 520 + bob, appear(t, 0.6, 0.5), "left", 92, 900)


def s_debate(cr, t, d):
    bg_waves(cr, t + 27, amount=0.7)
    # o time gira o ponteiro: vai para a esquerda, depois volta para a direita
    k1 = in_out(seg(t, 1.0, 2.2))
    k2 = in_out(seg(t, 3.6, 5.0))
    nd = lerp(lerp(-70, -45, k1), 31, k2) + math.sin(t * 9) * 1.5 * (1 - k2)
    dial(cr, DX, DY, DR, needle=nd, target=TARGET_KEYS, cover=0, left="DIFÍCIL DE ACHAR", right="FÁCIL DE ACHAR")
    bubble(cr, "EU VIVO PERDENDO MINHAS CHAVES!", 330, 330, appear(t, 0.3, 0.45, 3.4), "left", 46, 480)
    bubble(cr, "TEM COISA BEM MAIS DIFÍCIL, TIPO GANHAR NA LOTERIA!", 720, 520, appear(t, 2.6, 0.45),
           "right", 44, 520, MUSTARD)
    chip(cr, "O TIME DISCUTE E GIRA O PONTEIRO", 540, 1560, appear(t, 0.8), CORAL, CREAM, 44)


def s_reveal(cr, t, d):
    bg_waves(cr, t + 35, amount=0.7 + 0.3 * appear(t, 1.2))
    cover = out_cubic(seg(t, 0.4, 1.2))
    dial(cr, DX, DY, DR, needle=31, target=TARGET_KEYS, cover=cover, left="DIFÍCIL DE ACHAR", right="FÁCIL DE ACHAR",
         glow=0.5 + 0.5 * math.sin(t * 6) if t > 1.2 else 0)
    shadow_text(cr, "REVELA!", 540, 350, 120, CORAL, NAVY, 8, sc=appear(t, 0.2))
    if t > 1.3:
        s = appear(t, 1.3, 0.5)
        shadow_text(cr, "+3", 300, 560, 170, MUSTARD, NAVY, 9, sc=s, rot=-10)
        text(cr, "PONTOS", 300, 680, 50, NAVY, F_BLACK, sc=s, rot=-10)
    chip(cr, "NO CENTRO DO ALVO VALE 4 PONTOS", 540, 1560, appear(t, 2.6), BLUE, CREAM, 44)


QUICK = [("ÁGUA", "TEM COR?"), ("PIZZA", "É SANDUÍCHE?"), ("FILHOTE DE GIRAFA", "É FEIO?")]


def s_quick(cr, t, d):
    bg_waves(cr, t + 42, amount=1.0)
    shadow_text(cr, "CADA RODADA VIRA UMA", 540, 300, 60, NAVY, PINK, 5, sc=appear(t, 0.1))
    shadow_text(cr, "DISCUSSÃO ABSURDA", 540, 400, 84, CORAL, NAVY, 7, sc=appear(t, 0.3))
    for i, (a, b) in enumerate(QUICK):
        t0 = 0.8 + i * 0.9
        s = appear(t, t0, 0.45)
        y = 640 + i * 210
        x = 540 + (-1 if i % 2 else 1) * 30
        if s > 0.03:
            cr.save()
            cr.translate(x, y)
            cr.rotate(math.radians((-3, 2.5, -2)[i]))
            cr.scale(s, s)
            rrect(cr, -440, -85, 880, 170, 30)
            fill(cr, (PINK, MINT, MUSTARD)[i])
            text(cr, a, 0, -26, 54, NAVY, F_BLACK, maxw=820)
            text(cr, b, 0, 36, 46, NAVY, F_SEMI, maxw=820)
            cr.restore()
    chips = [("2 A 12 PESSOAS", NAVY), ("30 A 45 MIN", CORAL), ("14+", BLUE)]
    for i, (s_, c) in enumerate(chips):
        chip(cr, s_, 540, 1300 + i * 100, appear(t, 3.8 + i * 0.25), c, CREAM, 46)


TARGET_YOU = 24.0


def s_you(cr, t, d):
    bg_waves(cr, t + 49, amount=0.9)
    shadow_text(cr, "AGORA É COM VOCÊ!", 540, 280, 76, CORAL, NAVY, 6, sc=appear(t, 0.1), maxw=1020)
    cover = out_cubic(seg(t, 0.8, 1.6))
    dial(cr, DX, DY, DR, needle=-70 + 4 * math.sin(t * 2), target=TARGET_YOU, cover=cover,
         left="LUGAR SILENCIOSO", right="LUGAR BARULHENTO", card_pop=appear(t, 0.4),
         glow=0.4 + 0.4 * math.sin(t * 5) if t > 1.6 else 0)
    bubble(cr, "QUE DICA VOCÊ DARIA?", 540, 520 + math.sin(t * 3) * 6, appear(t, 2.0, 0.5), "left", 70, 900)
    if t > 3.2:
        chip(cr, "COMENTA AQUI EMBAIXO", 540, 1560, appear(t, 3.2) * (1 + 0.04 * math.sin(t * 6)), MUSTARD, NAVY, 52)


def s_cta(cr, t, d):
    bg_waves(cr, t + 58, amount=1.0, cover=0.25 * (1 - out_cubic(seg(t, 0, 0.8))))
    s = appear(t, 0.1, 0.55)
    blit(cr, logo_surf(760), 540, 420, sc=s, rot=math.sin(t * 2) * 1.5)
    shadow_text(cr, "ALUGUE O SINTONIA", 540, 780, 84, NAVY, MUSTARD, 6, sc=appear(t, 0.8))
    shadow_text(cr, "NA SUA VEZ!", 540, 890, 110, CORAL, NAVY, 8, sc=appear(t, 1.1), rot=-2)
    blit(cr, image_surf("pieces/box.png", 420), 540, 1200 + math.sin(t * 2.2) * 8, sc=appear(t, 1.4), rot=-5)
    chip(cr, "LINK NA BIO", 540, 1520, appear(t, 2.0) * (1 + 0.05 * math.sin(t * 6)), TEAL, NAVY, 60)


@lru_cache(None)
def logo_surf(width):
    lg = Image.open(os.path.join(ASSETS, "logo_suavez.png")).convert("RGBA")
    pad = int(lg.width * 0.06)
    card = Image.new("RGBA", (lg.width + pad * 2, lg.height + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=pad * 2,
                                           fill=(255, 255, 255, 255))
    card.alpha_composite(lg, (pad, pad))
    card = card.resize((int(width), int(card.height * width / card.width)), Image.LANCZOS)
    return surf_from_pil(card), card.width, card.height


SCENES = [
    (0.0, 6.0, s_hook),
    (6.0, 12.0, s_intro),
    (12.0, 20.0, s_how),
    (20.0, 25.0, s_clue),
    (25.0, 32.0, s_debate),
    (32.0, 38.0, s_reveal),
    (38.0, 47.0, s_quick),
    (47.0, 57.0, s_you),
    (57.0, 66.0, s_cta),
]

SUBS = [
    (0.2, 2.6, "Pizza é um tipo de sanduíche?"),
    (2.6, 5.8, "Pensa rápido... e responde girando um ponteiro."),
    (6.2, 9.0, "Esse é o Sintonia: o jogo de ler a mente dos amigos,"),
    (9.0, 11.8, "eleito o melhor party game de 2019."),
    (12.2, 15.6, "Cada rodada tem uma carta com dois extremos."),
    (15.6, 19.8, "Só o psíquico vê onde está o alvo... e esconde."),
    (20.2, 24.8, "Aí ele dá uma única dica. Tipo: minhas chaves!"),
    (25.2, 28.6, "O time discute, briga, defende sua opinião..."),
    (28.6, 31.8, "e gira o ponteiro onde acha que a dica se encaixa."),
    (32.2, 35.0, "Revela! Quanto mais perto do centro,"),
    (35.0, 37.8, "mais pontos o time faz."),
    (38.2, 42.6, "E cada rodada vira uma discussão absurda: água tem cor?"),
    (42.6, 46.8, "Dá pra jogar de 2 a 12 pessoas, em uns 40 minutos."),
    (47.2, 51.4, "Agora é com você: lugar silencioso ou barulhento."),
    (51.4, 56.8, "Que dica você daria pra esse alvo? Comenta aqui!"),
    (57.2, 61.0, "Quer testar a sintonia da sua galera?"),
    (61.0, 65.6, "Aluga o Sintonia na Sua Vez: link na bio!"),
]

# narração gravada (opcional): mesmo esquema do Reels do Vudú
TIMELINE_PATH = os.path.join(ROOT, "narracao", "timeline.json")
TIMELINE = None
if os.path.exists(TIMELINE_PATH):
    TIMELINE = json.load(open(TIMELINE_PATH, encoding="utf-8"))
    DUR = TIMELINE["duracao"]
    SUBS = [tuple(x) for x in TIMELINE["legendas"]]
    PLAY = [(n0, n1, fn, (o1 - o0) / (n1 - n0), o1 - o0)
            for (o0, o1, n0, n1), (_, _, fn) in zip(TIMELINE["cenas"], SCENES)]
else:
    PLAY = [(t0, t1, fn, 1.0, t1 - t0) for t0, t1, fn in SCENES]
CTA_START = PLAY[-1][0]


def warp(t_orig):
    if TIMELINE is None:
        return t_orig
    for o0, o1, n0, n1 in TIMELINE["cenas"]:
        if o0 <= t_orig < o1:
            return n0 + (t_orig - o0) * (n1 - n0) / (o1 - o0)
    return t_orig


def subtitle(cr, s):
    surf = text_surf(s, 50, WHITE, F_XBOLD, 0, 900, 1.08)
    w, h = surf[1] + 40, surf[2] + 18
    rrect(cr, 540 - w / 2, 1700 - h / 2, w, h, 22)
    fill(cr, NAVY, 0.82)
    blit(cr, surf, 540, 1700)


def render_frame(args):
    fi, subs = args
    t = fi / FPS
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    cr = cairo.Context(surf)
    for t0, t1, fn, k, d in PLAY:
        if t0 <= t < t1:
            break
    fn(cr, (t - t0) * k, d)
    if t < CTA_START:
        blit(cr, logo_surf(190), W - 34, 92, anchor=(1, 0), alpha=0.9)
    if subs:
        for a, b, s in SUBS:
            if a <= t < b:
                subtitle(cr, s)
    surf.flush()
    return bytes(surf.get_data())


def render(out_path, wav, subs, workers=4):
    n = int(DUR * FPS)
    cmd = [ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
           "-s", f"{W}x{H}", "-framerate", str(FPS), "-i", "-", "-i", wav,
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-maxrate", "8M", "-bufsize", "16M",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out_path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(workers) as pool:
        for i, fr in enumerate(pool.imap(render_frame, [(k, subs) for k in range(n)], chunksize=8)):
            p.stdin.write(fr)
            if i % 300 == 0:
                print(f"  quadro {i}/{n}", flush=True)
    p.stdin.close()
    p.wait()
    print("ok:", out_path)


def write_srt(path):
    def ts(s):
        ms = int(round(s * 1000))
        return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"
    with open(path, "w", encoding="utf-8") as f:
        for i, (a, b, s) in enumerate(SUBS, 1):
            f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{s}\n\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float)
    ap.add_argument("--only", choices=["preview", "limpo"])
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.frame is not None:
        buf = render_frame((int(a.frame * FPS), True))
        im = Image.frombuffer("RGBA", (W, H), buf, "raw", "BGRA", 0, 1).convert("RGB")
        im.save(os.path.join(OUT, "frame.png"))
        return
    wav = os.path.join(OUT, "trilha.wav")
    voz = [(os.path.join(ROOT, v["arquivo"]), v["inicio"]) for v in TIMELINE["voz"]] if TIMELINE else None
    trilha.build(wav, DUR, warp=warp, voz=voz)
    write_srt(os.path.join(ROOT, "legendas.srt"))
    if a.only != "limpo":
        render(os.path.join(OUT, "sintonia_preview.mp4"), wav, subs=True)
    if a.only != "preview":
        render(os.path.join(OUT, "sintonia_limpo.mp4"), wav, subs=False)


if __name__ == "__main__":
    main()
