#!/usr/bin/env python3
"""Reels do MLEM: Space Agency — Sua Vez Locação de Jogos.

Conceito: transmissão ao vivo de um lançamento da "Agência Espacial MLEM".
Motion graphics em cairo (30 quadros/s): painel de controle de missão,
contagem regressiva, foguete com gatos, rolagem de dados e a falha cósmica.

Uso:
  python3 mlem.py               # out/mlem_preview.mp4 (legendas) e out/mlem_limpo.mp4
  python3 mlem.py --frame 30    # quadro de teste em out/frame.png
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
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "..", "sintonia-reels"))
sys.path.insert(0, ROOT)
from sintonia import (seg, out_cubic, in_out, out_back, lerp, appear, text_surf, surf_from_pil,  # noqa: E402
                      blit, text, rrect, fill, logo_surf, ffmpeg_exe, F_BLACK, F_XBOLD, F_SEMI)
import som  # noqa: E402

ASSETS = os.path.join(ROOT, "assets")
OUT = os.path.join(ROOT, "out")
W, H = 1080, 1920
FPS = 30
DUR = 66.0
F_ORB = os.path.join(ASSETS, "fonts", "Orbitron.ttf")

SPACE_TOP = (0.03, 0.05, 0.15)
SPACE_BOT = (0.09, 0.15, 0.36)
GOLD = (0.95, 0.82, 0.47)
CYAN = (0.40, 0.87, 0.97)
PURPLE = (0.50, 0.36, 0.86)
LILAC = (0.74, 0.62, 0.98)
PINK = (0.97, 0.47, 0.72)
ORANGE = (1.0, 0.60, 0.20)
YELLOW = (1.0, 0.86, 0.30)
RED = (0.96, 0.25, 0.27)
GREEN = (0.45, 0.88, 0.55)
WHITE = (1, 1, 1)
INK = (0.06, 0.07, 0.18)
CAT_COLORS = [ORANGE, CYAN, PINK, YELLOW, GREEN]


@lru_cache(None)
def image_surf(name, width):
    im = Image.open(os.path.join(ASSETS, name)).convert("RGBA")
    im = im.resize((int(width), int(im.height * width / im.width)), Image.LANCZOS)
    return surf_from_pil(im), im.width, im.height


def T(cr, s, x, y, size, color=WHITE, path=F_BLACK, **kw):
    text(cr, s, x, y, size, color, path, **kw)


def glow_text(cr, s, x, y, size, color=GOLD, path=F_ORB, sc=1.0, **kw):
    """Título com brilho neon (camadas mais largas e transparentes)."""
    for k, a in ((10, 0.10), (6, 0.16), (3, 0.25)):
        for dx, dy in ((k, 0), (-k, 0), (0, k), (0, -k)):
            text(cr, s, x + dx * sc, y + dy * sc, size, color, path, sc=sc, alpha=a, **kw)
    text(cr, s, x, y, size, color, path, sc=sc, **kw)


def pill(cr, s, x, y, sc, bg=PURPLE, ink=WHITE, size=46, path=F_XBOLD, outline=None):
    if sc <= 0.03:
        return
    surf = text_surf(s, size, ink, path, 0, 940, 1.0)
    w, h = surf[1] + 64, surf[2] + 26
    cr.save()
    cr.translate(x, y)
    cr.scale(sc, sc)
    rrect(cr, -w / 2, -h / 2, w, h, h / 2)
    fill(cr, bg)
    if outline:
        rrect(cr, -w / 2, -h / 2, w, h, h / 2)
        cr.set_source_rgb(*outline)
        cr.set_line_width(4)
        cr.stroke()
    blit(cr, surf, 0, 2)
    cr.restore()


# ---------------------------------------------------------------- espaço
@lru_cache(None)
def star_layers():
    rng = np.random.default_rng(11)
    return [rng.uniform(0, 1, (n, 3)) for n in (160, 90, 40)]


def space(cr, t, speed=1.0, shake=0.0, tint=None):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *SPACE_TOP)
    g.add_color_stop_rgb(1, *SPACE_BOT)
    cr.set_source(g)
    cr.paint()
    # nebulosas
    for (nx, ny, nr, c, a) in ((0.2, 0.3, 520, PURPLE, 0.22), (0.85, 0.65, 600, CYAN, 0.12), (0.4, 0.9, 500, PINK, 0.12)):
        rg = cairo.RadialGradient(nx * W, ny * H, 10, nx * W, ny * H, nr)
        rg.add_color_stop_rgba(0, *c, a)
        rg.add_color_stop_rgba(1, *c, 0)
        cr.set_source(rg)
        cr.paint()
    # estrelas em 3 camadas (parallax: o foguete "sobe")
    for li, layer in enumerate(star_layers()):
        v = (40, 110, 260)[li] * speed
        size = (1.4, 2.2, 3.4)[li]
        for x, y, b in layer:
            yy = (y * H + t * v) % H
            xx = x * W + shake * math.sin(t * 50 + y * 9)
            cr.arc(xx, yy, size * (0.6 + 0.6 * b), 0, 2 * math.pi)
            fill(cr, WHITE, 0.35 + 0.5 * b)
            if speed > 2.5 and li == 2:
                cr.move_to(xx, yy)
                cr.line_to(xx, yy - v * 0.06)
                cr.set_source_rgba(1, 1, 1, 0.25)
                cr.set_line_width(2)
                cr.stroke()
    if tint:
        cr.set_source_rgba(*tint)
        cr.paint()


def planet(cr, x, y, r, c1, c2, ring=False, crater=False):
    rg = cairo.RadialGradient(x - r * 0.35, y - r * 0.35, r * 0.1, x, y, r)
    rg.add_color_stop_rgb(0, *c1)
    rg.add_color_stop_rgb(1, *c2)
    cr.arc(x, y, r, 0, 2 * math.pi)
    cr.set_source(rg)
    cr.fill()
    if crater:
        for dx, dy, rr in ((-0.3, -0.2, 0.18), (0.25, 0.1, 0.14), (-0.05, 0.4, 0.1)):
            cr.arc(x + dx * r, y + dy * r, rr * r, 0, 2 * math.pi)
            fill(cr, INK, 0.18)
    if ring:
        cr.save()
        cr.translate(x, y)
        cr.rotate(-0.35)
        cr.scale(1, 0.28)
        cr.arc(0, 0, r * 1.7, 0, 2 * math.pi)
        cr.restore()
        cr.set_source_rgba(*GOLD, 0.8)
        cr.set_line_width(r * 0.10)
        cr.stroke()


# ---------------------------------------------------------------- foguete e gatos
def cat_head(cr, x, y, r, c, alpha=1.0, eyes=True):
    cr.save()
    cr.translate(x, y)
    for sx in (-1, 1):
        cr.move_to(sx * r * 0.85, -r * 0.25)
        cr.line_to(sx * r * 0.75, -r * 1.15)
        cr.line_to(sx * r * 0.20, -r * 0.80)
        cr.close_path()
        fill(cr, c, alpha)
    cr.arc(0, 0, r, 0, 2 * math.pi)
    fill(cr, c, alpha)
    if eyes:
        for sx in (-1, 1):
            cr.save()
            cr.translate(sx * r * 0.38, -r * 0.05)
            cr.scale(1, 1.3)
            cr.arc(0, 0, r * 0.15, 0, 2 * math.pi)
            cr.restore()
            fill(cr, INK, alpha)
        cr.move_to(-r * 0.1, r * 0.25)
        cr.line_to(r * 0.1, r * 0.25)
        cr.line_to(0, r * 0.38)
        cr.close_path()
        fill(cr, INK, alpha * 0.8)
    cr.restore()


def rocket(cr, x, y, sc=1.0, rot=0.0, cats=(), flame=1.0, t=0.0, shake=0.0):
    cr.save()
    cr.translate(x + shake * math.sin(t * 61), y + shake * math.cos(t * 47))
    cr.rotate(math.radians(rot))
    cr.scale(sc, sc)
    # chama
    if flame > 0:
        fl = 1 + 0.18 * math.sin(t * 40) + 0.1 * math.sin(t * 73)
        for c, w_, l in ((ORANGE, 70, 260), (YELLOW, 44, 180), (WHITE, 20, 90)):
            cr.move_to(-w_, 300)
            cr.curve_to(-w_ * 0.8, 300 + l * 0.6 * fl * flame, -w_ * 0.2, 300 + l * fl * flame, 0, 300 + l * 1.15 * fl * flame)
            cr.curve_to(w_ * 0.2, 300 + l * fl * flame, w_ * 0.8, 300 + l * 0.6 * fl * flame, w_, 300)
            cr.close_path()
            fill(cr, c, 0.9)
    # aletas
    for sx in (-1, 1):
        cr.move_to(sx * 110, 120)
        cr.line_to(sx * 230, 300)
        cr.line_to(sx * 200, 330)
        cr.line_to(sx * 90, 280)
        cr.close_path()
        fill(cr, PINK)
    # corpo
    g = cairo.LinearGradient(-140, 0, 140, 0)
    g.add_color_stop_rgb(0, 0.36, 0.24, 0.70)
    g.add_color_stop_rgb(0.45, *LILAC)
    g.add_color_stop_rgb(1, 0.30, 0.20, 0.62)
    cr.move_to(0, -420)
    cr.curve_to(150, -300, 150, 120, 110, 300)
    cr.line_to(-110, 300)
    cr.curve_to(-150, 120, -150, -300, 0, -420)
    cr.close_path()
    cr.set_source(g)
    cr.fill()
    # bico
    cr.move_to(0, -420)
    cr.curve_to(70, -360, 95, -310, 105, -280)
    cr.line_to(-105, -280)
    cr.curve_to(-95, -310, -70, -360, 0, -420)
    cr.close_path()
    fill(cr, PINK)
    # base/bocal
    rrect(cr, -80, 290, 160, 40, 12)
    fill(cr, INK)
    # janelas com gatos
    for i in range(4):
        wy = -200 + i * 115
        cr.arc(0, wy, 46, 0, 2 * math.pi)
        fill(cr, INK)
        cr.arc(0, wy, 38, 0, 2 * math.pi)
        fill(cr, (0.16, 0.22, 0.45))
        if i < len(cats) and cats[i] is not None:
            cat_head(cr, 0, wy + 6, 24, cats[i])
        cr.arc(-14, wy - 14, 9, 0, 2 * math.pi)
        fill(cr, WHITE, 0.5)
    cr.restore()


# ---------------------------------------------------------------- dados
PIPS = {1: [(0, 0)], 2: [(-1, -1), (1, 1)], 3: [(-1, -1), (0, 0), (1, 1)],
        4: [(-1, -1), (1, -1), (-1, 1), (1, 1)]}


def paw(cr, x, y, r, c):
    cr.save()
    cr.translate(x, y)
    cr.save()
    cr.scale(1, 0.85)
    cr.arc(0, r * 0.35, r * 0.55, 0, 2 * math.pi)
    cr.restore()
    fill(cr, c)
    for ang, d in ((-55, 0.75), (-20, 0.9), (20, 0.9), (55, 0.75)):
        a = math.radians(ang - 90)
        cr.arc(d * r * math.cos(a), d * r * math.sin(a) + r * 0.1, r * 0.22, 0, 2 * math.pi)
        fill(cr, c)
    cr.restore()


def die(cr, x, y, face, size=120, rot=0.0, sc=1.0, hl=0.0, dim=0.0, alpha=1.0):
    if sc <= 0.03 or alpha <= 0.01:
        return
    cr.save()
    cr.translate(x, y)
    cr.rotate(math.radians(rot))
    cr.scale(sc, sc)
    s = size
    if hl > 0:
        rrect(cr, -s / 2 - 14, -s / 2 - 14, s + 28, s + 28, 30)
        fill(cr, YELLOW, 0.55 * hl)
    rrect(cr, -s / 2 + 6, -s / 2 + 10, s, s, 22)
    fill(cr, INK, 0.35 * alpha)
    rrect(cr, -s / 2, -s / 2, s, s, 22)
    fill(cr, (0.97, 0.97, 0.95), alpha)
    if face == "paw":
        paw(cr, 0, -s * 0.05, s * 0.28, (0.12, 0.12, 0.16))
    else:
        for px, py in PIPS[face]:
            cr.arc(px * s * 0.25, py * s * 0.25, s * 0.085, 0, 2 * math.pi)
            fill(cr, (0.12, 0.12, 0.16), alpha)
    if dim > 0:
        rrect(cr, -s / 2, -s / 2, s, s, 22)
        fill(cr, INK, 0.55 * dim)
    cr.restore()


FACES = [1, 2, 2, 3, 4, "paw"]


def tumbling_face(t, k):
    return FACES[int(t * 14 + k * 3) % len(FACES)]


def roll_dice(cr, t, t0, faces, slots, size=160, dur=0.9, hl_group=None, hl=0.0, gone=None, dim_all=0.0):
    """Dados entram rolando e param nas faces dadas."""
    for k, (face, (x, y)) in enumerate(zip(faces, slots)):
        if gone and k in gone and gone[k] <= t:
            continue
        u = seg(t, t0 + k * 0.05, t0 + k * 0.05 + dur)
        if u <= 0:
            continue
        e = out_cubic(u)
        xx = lerp(x + (k - 2.5) * 40, x, e)
        yy = lerp(H + 150, y, e) - abs(math.sin(e * math.pi * 2.5)) * 120 * (1 - e)
        rot = (1 - e) * (540 + k * 80)
        f = face if u >= 1 else tumbling_face(t, k)
        h = hl if (hl_group is not None and face == hl_group) else 0.0
        die(cr, xx, yy, f, size, rot, 1.0, h, dim_all if h == 0 else 0)


# ---------------------------------------------------------------- HUD
def hud(cr, t, mission=True, alert=0.0):
    c = RED if alert > 0.5 else CYAN
    a = 0.75
    cr.set_line_width(5)
    cr.set_source_rgba(*c, a)
    L = 70
    m = 40
    for (x, y, dx, dy) in ((m, 170, 1, 1), (W - m, 170, -1, 1), (m, H - 120, 1, -1), (W - m, H - 120, -1, -1)):
        cr.move_to(x, y + dy * L)
        cr.line_to(x, y)
        cr.line_to(x + dx * L, y)
        cr.stroke()
    if mission:
        on = (int(t * 2) % 2 == 0)
        cr.arc(70, 110, 11, 0, 2 * math.pi)
        fill(cr, RED, 1.0 if on else 0.35)
        T(cr, "AO VIVO", 92, 110, 30, WHITE, F_ORB, anchor=(0, 0.5))
        T(cr, "AGÊNCIA ESPACIAL MLEM", 70, 150, 24, CYAN, F_ORB, anchor=(0, 0.5), alpha=0.9)
        mm, ss = divmod(int(t), 60)
        T(cr, f"T+{mm:02d}:{ss:02d}", W - 250, 1795, 30, CYAN, F_ORB, anchor=(0, 0.5), alpha=0.85)


# ---------------------------------------------------------------- cenas
def s_hook(cr, t, d):
    launch = seg(t, 2.4, 4.6)
    space(cr, t, speed=0.3 + 4 * in_out(launch), shake=6 * launch)
    # contagem regressiva
    if t < 2.4:
        n = 3 - int(t / 0.8)
        lt = (t % 0.8) / 0.8
        r = 200 + 30 * out_back(min(1, lt * 3))
        cr.arc(540, 820, r, 0, 2 * math.pi)
        cr.set_source_rgba(*CYAN, 0.9 * (1 - lt * 0.6))
        cr.set_line_width(10)
        cr.stroke()
        cr.arc(540, 820, r - 26, -math.pi / 2, -math.pi / 2 + 2 * math.pi * (1 - lt))
        cr.set_source_rgba(*GOLD, 0.9)
        cr.set_line_width(14)
        cr.stroke()
        glow_text(cr, str(n), 540, 820, 260, WHITE, F_ORB, sc=out_back(min(1, lt * 2.5)))
    # foguete sobe
    ry = lerp(1500, -700, in_out(launch) ** 1.4) if t >= 2.2 else 1500
    rocket(cr, 540, ry, 0.9, 0, cats=[ORANGE, CYAN, PINK, YELLOW], flame=1.0 if t > 2.2 else 0.4, t=t,
           shake=4 * launch)
    # fumaça na base
    if t > 2.2:
        k = seg(t, 2.2, 3.6)
        for i in range(9):
            a = i / 9 * math.pi
            r = 80 + 260 * out_cubic(k)
            cr.arc(540 + math.cos(a) * r * 1.4, 1800 - math.sin(a) * r * 0.25, 90 + 40 * k, 0, 2 * math.pi)
            fill(cr, (0.85, 0.85, 0.95), 0.55 * (1 - k))
    if t > 2.6:
        glow_text(cr, "GATOS NO ESPAÇO.", 540, 1080, 84, GOLD, F_BLACK, sc=appear(t, 2.6))
    if t > 3.4:
        T(cr, "O QUE PODERIA DAR ERRADO?", 540, 1200, 62, WHITE, F_BLACK, sc=appear(t, 3.4), maxw=1000)
    hud(cr, t)


def s_intro(cr, t, d):
    space(cr, t + 6, speed=0.4)
    planet(cr, 880, 420, 150, (0.55, 0.95, 0.85), (0.10, 0.45, 0.45), crater=True)
    planet(cr, 160, 650, 70, (1.0, 0.75, 0.45), (0.65, 0.30, 0.15), ring=True)
    s = appear(t, 0.2, 0.6)
    T(cr, "MLEM", 540, 330, 190, GOLD, F_ORB, sc=s, tracking=8)
    T(cr, "SPACE AGENCY", 540, 470, 64, GOLD, F_ORB, sc=appear(t, 0.5), tracking=6)
    rise = out_cubic(seg(t, 0.6, 1.6))
    blit(cr, image_surf("pieces/cats.png", 1060), 540, lerp(2300, 1530, rise), anchor=(0.5, 0.5))
    pill(cr, "DE REINER KNIZIA", 540, 640, appear(t, 1.8), PURPLE, WHITE, 42)
    if t > 2.8:
        pill(cr, "COMANDE UMA AGÊNCIA DE GATOS", 540, 740, appear(t, 2.8), GOLD, INK, 44)
    hud(cr, t + 6)


def s_board(cr, t, d):
    space(cr, t + 12, speed=0.5)
    T(cr, "TODA RODADA", 540, 300, 52, CYAN, F_ORB, sc=appear(t, 0.1), tracking=6)
    glow_text(cr, "CADA UM EMBARCA UM GATO", 540, 400, 66, GOLD, F_BLACK, sc=appear(t, 0.3), maxw=1000)
    cats = []
    for i in range(4):
        t0 = 1.0 + i * 0.7
        if t >= t0 + 0.5:
            cats.append(CAT_COLORS[i])
        else:
            cats.append(None)
    rocket(cr, 540, 1150, 1.15, 0, cats=cats, flame=0.25, t=t)
    for i in range(4):
        t0 = 1.0 + i * 0.7
        u = seg(t, t0, t0 + 0.5)
        if 0 < u < 1:
            sx = -100 if i % 2 == 0 else W + 100
            x = lerp(sx, 540, out_cubic(u))
            y = lerp(700 + i * 200, 1150 + (-200 + i * 115) * 1.15, out_cubic(u)) - math.sin(u * math.pi) * 160
            cat_head(cr, x, y, 40 * lerp(1.6, 1.15, u), CAT_COLORS[i])
    hud(cr, t + 12)


ROLL1 = [2, 4, 2, 1, "paw", 3]
SLOTS6 = [(230, 1140), (540, 1140), (850, 1140), (230, 1360), (540, 1360), (850, 1360)]


def s_dice(cr, t, d):
    space(cr, t + 19, speed=0.6)
    T(cr, "O CAPITÃO ROLA", 540, 300, 54, CYAN, F_ORB, sc=appear(t, 0.1), tracking=4)
    glow_text(cr, "6 DADOS", 540, 410, 110, GOLD, F_BLACK, sc=appear(t, 0.3))
    # foguete pequeno no alto, avança depois da escolha
    adv = out_cubic(seg(t, 4.0, 5.2))
    rocket(cr, lerp(540, 540, adv), lerp(820, 640, adv), 0.42, 0, cats=[ORANGE, CYAN, PINK, YELLOW],
           flame=0.4 + 0.8 * adv, t=t)
    hl = in_out(seg(t, 2.2, 2.6))
    gone = {0: 3.6, 2: 3.6}
    # os dois "2" voam até o foguete e somem
    for k in (0, 2):
        u = seg(t, 3.0, 3.6)
        if 0 < u < 1:
            x0, y0 = SLOTS6[k]
            die(cr, lerp(x0, 540, in_out(u)), lerp(y0, 820, in_out(u)), 2, 160, u * 360, lerp(1, 0.3, u), 1.0)
    roll_dice(cr, t, 0.6, ROLL1, SLOTS6, hl_group=2, hl=hl, gone={0: 3.0, 2: 3.0}, dim_all=hl * 0.6)
    if t > 2.2:
        pill(cr, "ESCOLHE UM GRUPO", 540, 1555, appear(t, 2.2, 0.4, 4.0), PURPLE, WHITE, 46)
    if t > 4.2:
        glow_text(cr, "+4", 800, 600, 120, YELLOW, F_BLACK, sc=appear(t, 4.2))
    if t > 5.6:
        pill(cr, "DADO USADO SAI DA RODADA", 540, 1555, appear(t, 5.6), RED, WHITE, 46)
    hud(cr, t + 19)


ROLL2 = [4, 4, "paw", 1]
SLOTS4 = [(240, 1300), (440, 1300), (640, 1300), (840, 1300)]


def s_decide(cr, t, d):
    climb = out_cubic(seg(t, 5.2, 6.6))
    space(cr, t + 28, speed=0.6 + 3 * climb * (1 - seg(t, 6.6, 8.0)))
    # lua com pontos
    planet(cr, 230, 760, 110, (0.92, 0.92, 0.97), (0.45, 0.48, 0.6), crater=True)
    pill(cr, "+3", 230, 900, appear(t, 0.3), GOLD, INK, 50)
    jumped = t > 2.6
    jump_u = seg(t, 2.6, 3.4)
    cats = [None if jumped else ORANGE, CYAN, PINK, YELLOW]
    rocket(cr, 700, lerp(820, 700, climb), 0.55, 0, cats=cats, flame=0.5 + climb, t=t)
    if 0 < jump_u:
        x = lerp(700, 230, out_cubic(jump_u))
        y = lerp(820 - 200 * 0.55, 700, out_cubic(jump_u)) - math.sin(jump_u * math.pi) * 200
        cat_head(cr, x, y, 34, ORANGE)
    glow_text(cr, "PULA OU CONTINUA?", 540, 330, 76, GOLD, F_BLACK, sc=appear(t, 0.1), maxw=1000)
    if t < 5.0:
        a = appear(t, 0.8, 0.4, 4.6)
        pill(cr, "PULAR NA LUA", 300, 1500, a, CYAN, INK, 46)
        pill(cr, "CONTINUAR", 780, 1500, a, PINK, INK, 46)
    if 3.0 < t < 5.4:
        T(cr, "PONTOS GARANTIDOS!", 540, 1080, 50, CYAN, F_BLACK, sc=appear(t, 3.0, 0.4, 5.0))
    if t > 5.6:
        glow_text(cr, "QUANTO MAIS LONGE,", 540, 1150, 64, WHITE, F_BLACK, sc=appear(t, 5.6))
        glow_text(cr, "MAIS PONTOS", 540, 1250, 90, YELLOW, F_BLACK, sc=appear(t, 5.9))
        # contador de pontos subindo
        pts = int(lerp(3, 12, seg(t, 6.0, 8.0)))
        pill(cr, f"{pts} PONTOS", 540, 1480, appear(t, 6.0), GOLD, INK, 60)
    hud(cr, t + 28)


ROLL3 = [1, 1]


def s_crash(cr, t, d):
    boom = seg(t, 2.4, 3.4)
    alert = 1.0 if (t > 1.6 and int(t * 4) % 2 == 0) else 0.0
    space(cr, t + 38, speed=0.4, tint=(0.9, 0.1, 0.1, 0.18 * alert) if t > 1.6 else None)
    T(cr, "ÚLTIMA ROLAGEM...", 540, 320, 60, WHITE, F_ORB, sc=appear(t, 0.1), alpha=1 - seg(t, 2.3, 2.5))
    if t < 2.5:
        rocket(cr, 540, 760, 0.55, math.sin(t * 30) * (2 + 4 * seg(t, 1.2, 2.4)), cats=[None, CYAN, PINK, YELLOW],
               flame=0.6, t=t, shake=10 * seg(t, 1.2, 2.4))
    roll_dice(cr, t, 0.3, ROLL3, [(400, 1260), (680, 1260)], dim_all=0)
    if t > 1.4:
        for x in (400, 680):
            s = appear(t, 1.4, 0.3)
            cr.save()
            cr.translate(x, 1260)
            cr.scale(s, s)
            cr.set_source_rgb(*RED)
            cr.set_line_width(18)
            cr.move_to(-60, -60)
            cr.line_to(60, 60)
            cr.move_to(60, -60)
            cr.line_to(-60, 60)
            cr.stroke()
            cr.restore()
        if t < 2.4:
            T(cr, "NENHUM DADO SERVE!", 540, 1470, 52, RED, F_BLACK, sc=appear(t, 1.5))
    if t >= 2.4:
        # explosão
        rng = np.random.default_rng(5)
        for i in range(70):
            a = rng.uniform(0, 2 * math.pi)
            sp = rng.uniform(200, 900)
            r = sp * out_cubic(boom)
            x, y = 540 + math.cos(a) * r, 760 + math.sin(a) * r * 0.9
            sz = rng.uniform(10, 40) * (1 - boom * 0.7)
            c = (ORANGE, YELLOW, RED, WHITE)[i % 4]
            cr.arc(x, y, sz, 0, 2 * math.pi)
            fill(cr, c, 1 - boom * 0.8)
        fl = max(0, 1 - seg(t, 2.4, 2.8))
        rg = cairo.RadialGradient(540, 760, 10, 540, 760, 700)
        rg.add_color_stop_rgba(0, 1, 0.95, 0.8, 0.95 * fl)
        rg.add_color_stop_rgba(1, 1, 0.5, 0.2, 0)
        cr.set_source(rg)
        cr.paint()
        glow_text(cr, "FALHA CÓSMICA!", 540, 330, 100, RED, F_BLACK, sc=appear(t, 2.5, 0.5), maxw=1040)
        # gatos caindo de volta
        for i, c in enumerate((CYAN, PINK, YELLOW)):
            u = seg(t, 2.8 + i * 0.12, 4.8 + i * 0.12)
            if u > 0:
                x = 540 + (i - 1) * 260 * out_cubic(u)
                y = 760 - 220 * math.sin(min(1, u * 1.6) * math.pi / 2) + 1400 * u ** 2
                cr.save()
                cr.translate(x, y)
                cr.rotate(u * 9 * (1 if i % 2 else -1))
                cat_head(cr, 0, 0, 48, c)
                cr.restore()
        if t > 3.6:
            pill(cr, "QUEM FICOU NO FOGUETE NÃO PONTUA", 540, 1555, appear(t, 3.6), RED, WHITE, 42)
    hud(cr, t + 38, alert=alert)


def s_info(cr, t, d):
    space(cr, t + 45, speed=0.4)
    glow_text(cr, "CADA GATO TEM UM PODER", 540, 300, 64, GOLD, F_BLACK, sc=appear(t, 0.1), maxw=1000)
    s = appear(t, 0.4, 0.6)
    blit(cr, image_surf("pieces/player_board.jpg", 640), 540, 760, sc=s, rot=-3)
    planet(cr, 280, 1330, 120, (0.75, 0.55, 1.0), (0.30, 0.15, 0.55), ring=True)
    if t > 2.6:
        for i, c in enumerate((CYAN, CYAN, PINK)):
            u = appear(t, 2.6 + i * 0.2)
            if u > 0.03:
                cat_head(cr, 280 + (i - 1) * 70, 1330 - 140, 30 * u, c)
        T(cr, "PLANETAS PREMIAM", 690, 1300, 44, WHITE, F_XBOLD, sc=appear(t, 2.6), maxw=0)
        T(cr, "QUEM TEM MAIS GATOS", 690, 1362, 44, YELLOW, F_XBOLD, sc=appear(t, 2.8), maxw=0)
    pill(cr, "2 A 5 JOGADORES", 300, 1560, appear(t, 4.0), PURPLE, WHITE, 44)
    pill(cr, "30 A 60 MIN", 780, 1560, appear(t, 4.3), CYAN, INK, 44)
    hud(cr, t + 45)


def s_engage(cr, t, d):
    space(cr, t + 53, speed=1.0)
    glow_text(cr, "E VOCÊ?", 540, 380, 150, GOLD, F_BLACK, sc=appear(t, 0.1))
    pulse = 1 + 0.05 * math.sin(t * 6)
    a = appear(t, 0.8)
    pill(cr, "PULA NA PRIMEIRA LUA", 540, 820, a * pulse, CYAN, INK, 56)
    T(cr, "OU", 540, 960, 60, WHITE, F_ORB, sc=appear(t, 1.2))
    pill(cr, "ARRISCA ATÉ O FIM", 540, 1100, appear(t, 1.5) * (1 + 0.05 * math.sin(t * 6 + 1.5)), PINK, INK, 56)
    if t > 2.6:
        pill(cr, "COMENTA AQUI", 540, 1420, appear(t, 2.6) * (1 + 0.04 * math.sin(t * 7)), GOLD, INK, 60)
    rocket(cr, lerp(-200, W + 200, seg(t, 0, 5.5)), 1570, 0.3, 90, cats=[ORANGE, CYAN, PINK, YELLOW], flame=0.8, t=t)
    hud(cr, t + 53)


def s_cta(cr, t, d):
    space(cr, t + 58, speed=0.5)
    blit(cr, logo_surf(760), 540, 420, sc=appear(t, 0.1, 0.55), rot=math.sin(t * 2) * 1.5)
    glow_text(cr, "ALUGUE O MLEM", 540, 780, 86, GOLD, F_BLACK, sc=appear(t, 0.8))
    glow_text(cr, "NA SUA VEZ!", 540, 890, 110, WHITE, F_BLACK, sc=appear(t, 1.1))
    blit(cr, image_surf("pieces/box.png", 400), 540, 1180 + math.sin(t * 2.2) * 8, sc=appear(t, 1.4), rot=-5)
    pill(cr, "LINK NA BIO", 540, 1530, appear(t, 2.0) * (1 + 0.05 * math.sin(t * 6)), CYAN, INK, 60)


SCENES = [
    (0.0, 5.5, s_hook),
    (5.5, 12.0, s_intro),
    (12.0, 19.0, s_board),
    (19.0, 28.0, s_dice),
    (28.0, 38.0, s_decide),
    (38.0, 45.0, s_crash),
    (45.0, 53.0, s_info),
    (53.0, 58.5, s_engage),
    (58.5, 66.0, s_cta),
]

SUBS = [
    (0.3, 2.4, "3... 2... 1..."),
    (2.6, 5.2, "Gatos no espaço. O que poderia dar errado?"),
    (5.7, 9.0, "Esse é o MLEM: cada jogador comanda"),
    (9.0, 11.8, "uma agência espacial de gatos miaustronautas."),
    (12.2, 18.8, "Toda rodada, cada um coloca um gato no foguete."),
    (19.2, 23.4, "O capitão rola seis dados e escolhe um grupo..."),
    (23.4, 27.8, "o foguete avança, mas os dados usados saem da rodada."),
    (28.2, 33.2, "A cada parada, você decide: pula numa lua e garante pontos..."),
    (33.2, 37.8, "ou continua, porque quanto mais longe, mais pontos."),
    (38.2, 40.6, "Mas se nenhum dado servir..."),
    (40.6, 44.8, "BOOM! Falha cósmica, e quem ficou no foguete não pontua."),
    (45.2, 49.0, "Cada gato tem um poder, e os planetas premiam quem tiver mais gatos."),
    (49.0, 52.8, "De 2 a 5 jogadores, em uns 40 minutos."),
    (53.2, 58.2, "E você, pula na primeira lua ou arrisca até o fim? Comenta!"),
    (58.7, 65.6, "Aluga o MLEM na Sua Vez: link na bio!"),
]

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
    fill(cr, INK, 0.78)
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
        blit(cr, logo_surf(190), W - 34, 92, anchor=(1, 0), alpha=0.92)
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
    ap.add_argument("--check", action="store_true", help="renderiza todos os quadros sem gravar")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.frame is not None:
        buf = render_frame((int(a.frame * FPS), True))
        Image.frombuffer("RGBA", (W, H), buf, "raw", "BGRA", 0, 1).convert("RGB").save(os.path.join(OUT, "frame.png"))
        return
    if a.check:
        bad = []
        for fi in range(int(DUR * FPS)):
            try:
                render_frame((fi, True))
            except Exception as e:  # noqa: BLE001
                bad.append((fi, repr(e)[:60]))
        print("quadros com erro:", bad[:10], len(bad))
        return
    wav = os.path.join(OUT, "trilha.wav")
    voz = [(os.path.join(ROOT, v["arquivo"]), v["inicio"]) for v in TIMELINE["voz"]] if TIMELINE else None
    som.build(wav, DUR, warp=warp, voz=voz)
    write_srt(os.path.join(ROOT, "legendas.srt"))
    if a.only != "limpo":
        render(os.path.join(OUT, "mlem_preview.mp4"), wav, subs=True)
    if a.only != "preview":
        render(os.path.join(OUT, "mlem_limpo.mp4"), wav, subs=False)


if __name__ == "__main__":
    main()
