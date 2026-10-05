#!/usr/bin/env python3
"""Reels do MLEM: Space Agency em stop motion de recortes — Sua Vez.

Mesma pegada do Reels do Vudú: fotos reais das peças recortadas e animadas
quadro a quadro (12 poses/s, tremidinho da mão, sombras, granulação).

Uso:
  python3 stopmo.py               # out/mlem_preview.mp4 (legendas) e out/mlem_limpo.mp4
  python3 stopmo.py --frame 30    # quadro de teste em out/frame.png
"""
import argparse
import json
import math
import os
import subprocess
import sys
from functools import lru_cache
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "..", "voodoo-reels"))
sys.path.insert(0, ROOT)
import reels as R  # noqa: E402  (infra do stop motion do Vudú)
import som  # noqa: E402

PIECES = os.path.join(ROOT, "assets", "pieces")
OUT = os.path.join(ROOT, "out")
W, H, FPS = R.W, R.H, R.FPS
DUR = 66.0
seg, lerp, ease_io, ease_out, pop = R.seg, R.lerp, R.ease_io, R.ease_out, R.pop
sticker, headline, star, bounce_path = R.sticker, R.headline, R.star, R.bounce_path


def place(canvas, ctx, im, x, y, sc=1.0, **kw):
    """Igual ao do Vudú, mas não desenha o que ainda não entrou em cena (sc None/0)."""
    if not sc:
        return
    R.place(canvas, ctx, im, x, y, sc=sc, **kw)

CREAM = (255, 244, 220)
GOLD = (245, 205, 95)
CYAN = (110, 225, 245)
PINK = (250, 120, 185)
RED = (235, 50, 45)
YELLOW = (255, 206, 40)
INK = (20, 16, 50)
SPACE_INK = (25, 20, 70)


@lru_cache(None)
def piece(name):
    return Image.open(os.path.join(PIECES, name)).convert("RGBA")


@lru_cache(None)
def scaled(name, width):
    im = piece(name)
    return im.resize((int(width), int(im.height * width / im.width)), Image.LANCZOS)


@lru_cache(None)
def rocket_up(width):
    """Foguete da arte do jogo, girado para apontar para cima."""
    return scaled("rocket.png", width).rotate(90, expand=True, resample=Image.BICUBIC)


# ---------------------------------------------------------------- fundos (foto do tabuleiro, como no Vudú)
@lru_cache(None)
def bg_table():
    im = piece("board_photo.jpg").convert("RGB")
    s = H / im.height
    im = im.resize((int(im.width * s), H), Image.LANCZOS)
    x0 = (im.width - W) // 2
    im = im.crop((x0, 0, x0 + W, H)).filter(ImageFilter.GaussianBlur(12))
    a = np.asarray(im, np.float32) * np.array([0.45, 0.45, 0.62])
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


COSMOS_CROP = (16, 18, 343, 1195)  # tira as bordas brancas da foto do tabuleiro


@lru_cache(None)
def cosmos_big():
    """Tabuleiro do cosmos (foto vertical do jogo) ampliado para a largura do vídeo."""
    im = piece("cosmos_strip.jpg").convert("RGB")
    im = im.crop(COSMOS_CROP)
    im = im.resize((W, int(im.height * W / im.width)), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.6))
    a = np.asarray(im, np.float32) * 0.80
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def bg_track(progress=0.0):
    """Recorte do cosmos; progress 0 → base do tabuleiro, 1 → topo (o foguete sobe)."""
    big = cosmos_big()
    y0 = int((big.height - H) * (1 - progress))
    return big.crop((0, y0, W, y0 + H))


@lru_cache(None)
def bg_box():
    im = piece("box_back.jpg").convert("RGB")
    s = H / im.height
    im = im.resize((int(im.width * s), H), Image.LANCZOS)
    x0 = (im.width - W) // 2
    im = im.crop((x0, 0, x0 + W, H)).filter(ImageFilter.GaussianBlur(14))
    a = np.asarray(im, np.float32) * 0.40
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def bg(which, ctx, red=0.0, progress=0.0):
    im = bg_track(progress) if which == "track" else {"table": bg_table, "box": bg_box}[which]().copy()
    if red > 0:
        im = Image.blend(im, Image.new("RGB", im.size, (190, 20, 25)), 0.35 * red)
    return im



@lru_cache(None)
def polaroid(name, width=640, caption=""):
    """Foto real do jogo como polaroide (borda branca + legenda escrita à mão)."""
    ph = piece(name).convert("RGB")
    ph = ph.resize((width, int(ph.height * width / ph.width)), Image.LANCZOS)
    b, bottom = 24, 110 if caption else 24
    card = Image.new("RGBA", (width + 2 * b, ph.height + b + bottom), (250, 248, 240, 255))
    card.paste(ph, (b, b))
    if caption:
        f = R.font(54)
        d = ImageDraw.Draw(card)
        d.text((card.width / 2, ph.height + b + bottom / 2), caption, font=f, fill=(40, 30, 60, 255), anchor="mm")
    return card


def drop_photo(c, ctx, lt, t0, t1, name, x, y, rot, caption="", width=640):
    """A foto cai na mesa em poucas poses, fica e depois é puxada para fora."""
    if lt < t0 or lt >= t1 + 0.5:
        return
    u = seg(lt, t0, t0 + 0.45)
    out = seg(lt, t1, t1 + 0.5)
    yy = lerp(-800, y, ease_out(u)) if u < 1 else y
    xx = x + (W + 700) * ease_io(out)
    sx = sy = 1.0
    k = int((lt - t0 - 0.45) * FPS)
    if 0 <= k < 3:
        sx, sy = [(1.04, 0.95), (0.98, 1.02), (1, 1)][k]
    place(c, ctx, polaroid(name, width, caption), xx, yy, rot=rot + (1 - u) * 25 + out * 20, sx=sx, sy=sy,
          lift=(1 - u) * 300 + out * 150)


DICE = ["d1.png", "d2.png", "d3.png", "d4.png", "d5.png", "d6.png"]
CATS = ["cat_l.png", "cat_m.png", "cat_r.png"]


def die_img(name, w=190):
    return scaled(name, w)


def tumbling(t, k):
    return DICE[(int(t * FPS) * 3 + k * 5) % len(DICE)]


def flame(c, ctx, x, y, k=1.0):
    """Chama do foguete feita de estrelinhas de papel que trocam a cada pose."""
    for i in range(3):
        ox = ctx.j(18)
        oy = 70 + i * 55 * k + ctx.j(10)
        place(c, ctx, star(int((80 - i * 18) * k) or 10, (255, 150 - i * 40, 40)), x + ox, y + oy,
              rot=ctx.j(40), shadow=0.0)


# ---------------------------------------------------------------- cenas
def s_hook(ctx):
    lt = ctx.lt
    c = bg("table", ctx)
    launch = seg(lt, 2.4, 4.8)
    ry = lerp(1300, -800, ease_io(launch) ** 1.3)
    shake = math.sin(lt * 40) * 8 * (1 - launch) if lt > 1.8 else 0
    place(c, ctx, rocket_up(720), 540 + shake, ry, lift=40 + 400 * launch)
    if lt > 2.2:
        flame(c, ctx, 540 + shake, ry + 380, 1.5)
    if lt < 2.4:
        n = 3 - int(lt / 0.8)
        place(c, ctx, sticker(str(n), 300, YELLOW), 540, 560, rot=(-6, 4, -3)[3 - n], sc=pop(lt, (3 - n) * 0.8))
    if lt > 2.3:
        for i in range(6):  # fumaça de algodão na base
            k = seg(lt, 2.3, 3.8)
            place(c, ctx, star(140, (235, 235, 245)), 540 + (i - 2.5) * 140 * (0.5 + k), 1700 - k * 60,
                  rot=i * 30, sc=0.6 + k * 0.8, alpha=1 - k, shadow=0.2)
    headline(c, ctx, "GATOS NO ESPAÇO.", 2.6, y=1080, size=104, color=GOLD)
    headline(c, ctx, "O QUE PODERIA DAR ERRADO?", 3.4, y=1230, size=74, color=CREAM, rot=-2)
    return c


def s_intro(ctx):
    lt = ctx.lt
    c = bg("box", ctx)
    # gatos entram pulando dos lados
    for i, (name, x, w) in enumerate(((CATS[0], 210, 390), (CATS[2], 880, 420), (CATS[1], 540, 400))):
        t0 = 1.6 + i * 0.35
        if lt >= t0:
            u = seg(lt, t0, t0 + 0.6)
            sx0 = -300 if x < 540 else (W + 300 if x > 540 else 540)
            px, py, lift = bounce_path(u, (sx0, 2000 if x == 540 else 1500), (x, 1430), 260, 2)
            place(c, ctx, scaled(name, w), px, py, rot=math.sin(lt * 5 + i) * 3, lift=lift)
    u = seg(lt, 0.1, 0.55)
    sx = sy = 1.0
    if 0 <= lt - 0.55 < 0.35:
        sx, sy = [(1.06, 0.92), (0.97, 1.04), (1.01, 0.99), (1, 1)][min(int((lt - 0.55) * FPS), 3)]
    place(c, ctx, scaled("box.png", 620), 540, lerp(-700, 720, ease_io(u) ** 2), rot=(1 - u) * -12,
          sx=sx, sy=sy, lift=(1 - u) * 300)
    headline(c, ctx, "DE REINER KNIZIA", 1.2, y=250, size=70, color=CYAN, rot=-2)
    headline(c, ctx, "COMANDE UMA AGÊNCIA DE GATOS", 3.0, y=1150, size=70, color=GOLD, rot=2)
    return c


WINDOWS = [-0.20, -0.07, 0.06, 0.19]  # posição (fração do comprimento) das janelas no foguete


def s_board(ctx):
    lt = ctx.lt
    c = bg("table", ctx)
    rw = 1000
    rk = scaled("rocket.png", rw)
    place(c, ctx, rk, 540, 1120, rot=8)
    for i in range(4):
        t0 = 1.0 + i * 0.7
        u = seg(lt, t0, t0 + 0.55)
        if 0 < u < 1:
            name = CATS[i % 3]
            sx0 = -250 if i % 2 == 0 else W + 250
            tx = 540 + WINDOWS[i] * rw * 1.4
            px, py, lift = bounce_path(u, (sx0, 700), (tx, 1080), 300, 1)
            place(c, ctx, scaled(name, 300), px, py, sc=lerp(1.0, 0.25, u), rot=u * 30, lift=lift)
        if t0 + 0.55 <= lt < t0 + 0.9:
            k = int((lt - t0 - 0.55) * FPS)
            for j in range(4):
                a = j * math.pi / 2 + 0.4
                place(c, ctx, star(60, YELLOW), 540 + WINDOWS[i] * rw * 1.4 + math.cos(a) * (60 + k * 18),
                      1080 + math.sin(a) * (60 + k * 18), rot=k * 30, shadow=0.2)
    drop_photo(c, ctx, lt, 4.6, 6.6, "board_photo.jpg", 540, 1180, -5, "O TABULEIRO DO COSMOS", 720)
    headline(c, ctx, "TODA RODADA", 0.1, y=280, size=70, color=CYAN)
    headline(c, ctx, "CADA UM EMBARCA UM GATO", 0.4, y=420, size=84, color=GOLD, rot=-2)
    return c


SLOTS = [(210, 1130), (450, 1240), (700, 1130), (910, 1250), (330, 1400), (690, 1420)]
FINAL = ["d5.png", "d2.png", "d5.png", "d6.png", "d4.png", "d3.png"]
FINAL_ROT = [-8, 12, 24, -14, 6, -20]
PICK = (0, 2)  # os dois "2" escolhidos


def dice_throw(c, ctx, lt, t0, faces, slots, rots, w=190, skip=()):
    for k, (face, (x, y), r) in enumerate(zip(faces, slots, rots)):
        if k in skip:
            continue
        s0 = t0 + k * 0.06
        if lt < s0:
            continue
        u = seg(lt, s0, s0 + 1.1)
        px, py, lift = bounce_path(u, (W + 200 + k * 30, 1900), (x, y), 240, 3)
        if u < 1:
            place(c, ctx, die_img(tumbling(lt, k), w), px, py, rot=r + (1 - ease_out(u)) * 700, lift=lift)
        else:
            place(c, ctx, die_img(face, w), x, y, rot=r)


def s_dice(ctx):
    lt = ctx.lt
    adv = ease_out(seg(lt, 4.0, 5.2))
    c = bg("track", ctx, progress=0.05 + 0.10 * adv)
    place(c, ctx, rocket_up(260), lerp(700, 560, adv), lerp(880, 560, adv), rot=-10, lift=60)
    if adv > 0 and lt < 5.4:
        flame(c, ctx, lerp(700, 560, adv) - 10, lerp(880, 560, adv) + 160, 0.7)
    skip = PICK if lt >= 3.0 else ()
    dice_throw(c, ctx, lt, 0.6, FINAL, SLOTS, FINAL_ROT, skip=skip)
    if 2.2 <= lt < 3.0:  # destaque: o grupo escolhido
        for k in PICK:
            x, y = SLOTS[k]
            place(c, ctx, sticker("2", 80, INK, paper=YELLOW), x + 70, y - 90, sc=pop(lt, 2.2), shadow=0.3)
    for k in PICK:  # os dados escolhidos voam até o foguete
        u = seg(lt, 3.0, 3.7)
        if 0 < u < 1:
            x0, y0 = SLOTS[k]
            place(c, ctx, die_img(FINAL[k]), lerp(x0, 700, ease_io(u)), lerp(y0, 880, ease_io(u)) - math.sin(u * math.pi) * 200,
                  sc=lerp(1, 0.3, u), rot=u * 300, lift=math.sin(u * math.pi) * 200)
    drop_photo(c, ctx, lt, 6.6, 8.6, "dice_photo.jpg", 540, 1000, 6, "OS DADOS DO JOGO", 700)
    headline(c, ctx, "O CAPITÃO ROLA 6 DADOS", 0.1, y=260, size=84, color=GOLD)
    if 2.2 <= lt < 4.0:
        place(c, ctx, sticker("ESCOLHE UM GRUPO", 76, CYAN), 540, 1580, rot=-2, sc=pop(lt, 2.2))
    if lt >= 4.2:
        place(c, ctx, sticker("+4", 150, YELLOW), 330, 640, rot=-10, sc=pop(lt, 4.2))
    if lt >= 5.6:
        place(c, ctx, sticker("DADO USADO SAI DA RODADA", 70, RED), 540, 1580, rot=2, sc=pop(lt, 5.6))
    return c


def s_decide(ctx):
    lt = ctx.lt
    c = bg("track", ctx, progress=0.15 + 0.35 * ease_out(seg(ctx.lt, 5.2, 6.4)))
    place(c, ctx, scaled("moon_token.png", 380), 250, 820, rot=-8)
    place(c, ctx, sticker("+3", 110, YELLOW), 250, 610, rot=8, sc=pop(lt, 0.3))
    climb = ease_out(seg(lt, 5.2, 6.4))
    rx, ry = lerp(760, 760, climb), lerp(900, 520, climb)
    place(c, ctx, rocket_up(300), rx, ry, rot=-6, lift=80)
    if 5.0 < lt < 6.6:
        flame(c, ctx, rx, ry + 190, 0.8)
    # o gato da esquerda pula do foguete para a lua
    u = seg(lt, 2.6, 3.3)
    if u > 0:
        px, py, lift = bounce_path(u, (rx, ry), (250, 760), 300, 1)
        place(c, ctx, scaled(CATS[0], lerp(120, 230, u)), px, py, rot=(1 - u) * 40, lift=lift)
    headline(c, ctx, "PULA OU CONTINUA?", 0.1, y=270, size=96, color=GOLD)
    if lt < 4.8:
        place(c, ctx, sticker("PULAR NA LUA", 66, CYAN), 290, 1420, rot=-4, sc=pop(lt, 0.8))
        place(c, ctx, sticker("CONTINUAR", 66, PINK), 790, 1420, rot=4, sc=pop(lt, 1.0))
    if 3.2 <= lt < 5.2:
        place(c, ctx, sticker("PONTOS GARANTIDOS!", 64, CYAN), 300, 1060, rot=-6, sc=pop(lt, 3.2))
    if lt >= 5.6:
        headline(c, ctx, "QUANTO MAIS LONGE,", 5.6, y=1150, size=80, color=CREAM)
        headline(c, ctx, "MAIS PONTOS!", 5.9, y=1290, size=110, color=YELLOW, rot=-3)
        n = 1 + min(3, int((lt - 6.2) / 0.5)) if lt > 6.2 else 0
        for i in range(n):
            place(c, ctx, scaled("fish_token.png", 140), 160 + i * 250, 1520, rot=(-12, 8, -5, 14)[i], sc=pop(lt, 6.2 + i * 0.5))
    return c


def s_crash(ctx):
    lt = ctx.lt
    alert = 1.0 if (lt > 1.4 and int(lt * 4) % 2 == 0 and lt < 2.4) else 0.0
    c = bg("track", ctx, red=alert, progress=0.55)
    boom = seg(lt, 2.4, 3.4)
    if lt < 2.4:
        sh = math.sin(lt * 50) * (4 + 14 * seg(lt, 1.2, 2.4))
        place(c, ctx, rocket_up(320), 540 + sh, 640, rot=sh * 0.6, lift=80)
    dice_throw(c, ctx, lt, 0.3, ["d1.png", "d1.png"], [(400, 1250), (690, 1250)], [10, -15])
    if 1.4 <= lt:
        for x in (400, 690):
            place(c, ctx, sticker("X", 220, RED), x, 1250, rot=-8, sc=pop(lt, 1.4), shadow=0.3)
    if 1.5 <= lt < 2.4:
        place(c, ctx, sticker("NENHUM DADO SERVE!", 70, RED), 540, 1480, rot=-3, sc=pop(lt, 1.5))
    headline(c, ctx, "ÚLTIMA ROLAGEM...", 0.1, 2.4, y=280, size=80, color=CREAM)
    if lt >= 2.4:
        k = int((lt - 2.4) * FPS)
        rng = np.random.default_rng(9)
        for i in range(16):  # explosão de estrelas de papel
            a = rng.uniform(0, 2 * math.pi)
            r = rng.uniform(150, 650) * ease_out(boom)
            col = ((255, 150, 40), (255, 206, 40), (235, 50, 45), (255, 240, 200))[i % 4]
            place(c, ctx, star(int(rng.uniform(90, 170)), col), 540 + math.cos(a) * r, 640 + math.sin(a) * r,
                  rot=k * 25 + i * 20, sc=max(0.2, 1 - boom * 0.5), shadow=0.25)
        if lt < 2.55:
            c = Image.blend(c, Image.new("RGB", c.size, (255, 240, 200)), 0.6)
        headline(c, ctx, "FALHA CÓSMICA!", 2.5, y=280, size=118, color=RED)
        for i, name in enumerate(CATS):  # os gatos caem de volta
            u = seg(lt, 2.7 + i * 0.12, 4.6 + i * 0.12)
            if u > 0:
                x = 540 + (i - 1) * 300 * ease_out(u)
                y = 640 - 200 * math.sin(min(1, u * 1.6) * math.pi / 2) + 1500 * u * u
                place(c, ctx, scaled(name, 260), x, y, rot=u * 520 * (1 if i % 2 else -1), lift=200)
        if lt >= 3.6:
            place(c, ctx, sticker("QUEM FICOU NO FOGUETE NÃO PONTUA", 58, CREAM), 540, 1520, rot=2, sc=pop(lt, 3.6))
    return c


def s_info(ctx):
    lt = ctx.lt
    c = bg("table", ctx)
    u = ease_out(seg(lt, 0.3, 1.0))
    place(c, ctx, scaled("player_board_cut.png", 860), lerp(-600, 540, u), 760, rot=lerp(-20, -4, u))
    headline(c, ctx, "CADA GATO TEM UM PODER", 0.1, y=260, size=84, color=GOLD)
    if lt >= 2.6:
        place(c, ctx, scaled("tokens_pile.png", 420), 260, 1290, rot=-6, sc=pop(lt, 2.6))
        place(c, ctx, sticker("PLANETAS PREMIAM QUEM TEM MAIS GATOS", 60, CYAN, maxw=560), 730, 1290, rot=3, sc=pop(lt, 2.9))
    place(c, ctx, sticker("2 A 5 JOGADORES", 64, CREAM), 290, 1560, rot=-3, sc=pop(lt, 4.0))
    place(c, ctx, sticker("30 A 60 MIN", 64, YELLOW), 800, 1560, rot=3, sc=pop(lt, 4.3))
    return c


def s_engage(ctx):
    lt = ctx.lt
    c = bg("table", ctx)
    bob = abs(math.sin(lt * 3)) * 30
    place(c, ctx, scaled(CATS[1], 330), 540, 1330 - bob, rot=math.sin(lt * 4) * 5, lift=bob)
    headline(c, ctx, "E VOCÊ?", 0.1, y=320, size=170, color=GOLD)
    headline(c, ctx, "PULA NA PRIMEIRA LUA", 0.8, y=620, size=80, color=CYAN, rot=-3)
    headline(c, ctx, "OU", 1.2, y=740, size=70, color=CREAM)
    headline(c, ctx, "ARRISCA ATÉ O FIM?", 1.5, y=860, size=88, color=PINK, rot=2)
    if lt >= 2.6:
        place(c, ctx, sticker("COMENTA AQUI", 90, YELLOW), 540, 1050 + abs(math.sin(lt * 5)) * 10, rot=-2,
              sc=pop(lt, 2.6))
    return c


def s_cta(ctx):
    lt = ctx.lt
    c = bg("box", ctx)
    s = pop(lt, 0.3)
    if s:
        lg = R.logo()
        place(c, ctx, lg.resize((760, int(lg.height * 760 / lg.width)), Image.LANCZOS), 540, 430, sc=s,
              rot=math.sin(lt * 3) * 2, shadow=0.7)
    headline(c, ctx, "ALUGUE O MLEM", 1.1, y=790, size=100, color=GOLD)
    headline(c, ctx, "NA SUA VEZ!", 1.5, y=910, size=118, color=CREAM, rot=-3)
    s = pop(lt, 1.8)
    if s:
        place(c, ctx, scaled("box.png", 360), 300, 1270, rot=-8, sc=s)
        place(c, ctx, scaled(CATS[0], 300), 820, 1290, rot=math.sin(lt * 8) * 7, sc=s)
    s = pop(lt, 2.7)
    if s:
        place(c, ctx, sticker("LINK NA BIO", 90, CYAN), 540, 1540 + abs(math.sin(lt * 5)) * 12, rot=2, sc=s)
    return c


SCENES = [
    (0.0, 5.5, s_hook), (5.5, 12.0, s_intro), (12.0, 19.0, s_board), (19.0, 28.0, s_dice),
    (28.0, 38.0, s_decide), (38.0, 45.0, s_crash), (45.0, 53.0, s_info), (53.0, 58.5, s_engage),
    (58.5, 66.0, s_cta),
]

from mlem import SUBS as _SUBS  # noqa: E402  (mesmo roteiro)
SUBS = list(_SUBS)

TIMELINE_PATH = os.path.join(ROOT, "narracao", "timeline.json")
TIMELINE = None
if os.path.exists(TIMELINE_PATH):
    TIMELINE = json.load(open(TIMELINE_PATH, encoding="utf-8"))
    DUR = TIMELINE["duracao"]
    SUBS = [tuple(x) for x in TIMELINE["legendas"]]
    PLAY = [(n0, n1, fn, (o1 - o0) / (n1 - n0)) for (o0, o1, n0, n1), (_, _, fn) in zip(TIMELINE["cenas"], SCENES)]
else:
    PLAY = [(t0, t1, fn, 1.0) for t0, t1, fn in SCENES]
CTA_START = PLAY[-1][0]


def warp(t_orig):
    if TIMELINE is None:
        return t_orig
    for o0, o1, n0, n1 in TIMELINE["cenas"]:
        if o0 <= t_orig < o1:
            return n0 + (t_orig - o0) * (n1 - n0) / (o1 - o0)
    return t_orig


def render_frame(args):
    fi, subs = args
    ctx = R.Ctx(fi)
    t = ctx.t
    for t0, t1, fn, k in PLAY:
        if t0 <= t < t1:
            break
    ctx.lt = (t - t0) * k
    img = fn(ctx)
    if t < CTA_START:
        wm = R.watermark()
        img.paste(wm, (W - wm.width - 34, 96), wm)
    if subs:
        for a, b, s in SUBS:
            if a <= t < b:
                si = R.sub_img(s)
                img.paste(si, ((W - si.width) // 2, 1700 - si.height // 2), si)
    return R.post(img, ctx).tobytes()


def render(out_path, wav, subs, workers=4):
    n = int(DUR * FPS)
    cmd = [R.ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-framerate", str(FPS), "-i", "-", "-i", wav,
           "-vf", "fps=24", "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-maxrate", "7M", "-bufsize", "14M",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out_path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(workers) as pool:
        for i, fr in enumerate(pool.imap(render_frame, [(k, subs) for k in range(n)], chunksize=4)):
            p.stdin.write(fr)
            if i % 120 == 0:
                print(f"  quadro {i}/{n}", flush=True)
    p.stdin.close()
    p.wait()
    print("ok:", out_path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float)
    ap.add_argument("--only", choices=["preview", "limpo"])
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.frame is not None:
        Image.frombytes("RGB", (W, H), render_frame((int(a.frame * FPS), True))).save(os.path.join(OUT, "frame.png"))
        return
    wav = os.path.join(OUT, "trilha.wav")
    voz = [(os.path.join(ROOT, v["arquivo"]), v["inicio"]) for v in TIMELINE["voz"]] if TIMELINE else None
    som.build(wav, DUR, warp=warp, voz=voz)
    with open(os.path.join(ROOT, "legendas.srt"), "w", encoding="utf-8") as f:
        for i, (a_, b_, s) in enumerate(SUBS, 1):
            ts = lambda x: f"{int(x // 3600):02}:{int(x // 60 % 60):02}:{int(x % 60):02},{int(round(x * 1000)) % 1000:03}"
            f.write(f"{i}\n{ts(a_)} --> {ts(b_)}\n{s}\n\n")
    if a.only != "limpo":
        render(os.path.join(OUT, "mlem_preview.mp4"), wav, subs=True)
    if a.only != "preview":
        render(os.path.join(OUT, "mlem_limpo.mp4"), wav, subs=False)


if __name__ == "__main__":
    main()
