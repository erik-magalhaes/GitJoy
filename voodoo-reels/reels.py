#!/usr/bin/env python3
"""Reels do Vudú (Voodoo) em stop motion de recortes — Sua Vez Locação de Jogos.

As peças são fotos reais do jogo recortadas do fundo e animadas quadro a quadro
(12 quadros/s, com o "tremidinho" de quem reposiciona cada peça com a mão).

Uso:
  python3 reels.py                  # gera out/vudu_preview.mp4 (com legendas) e out/vudu_limpo.mp4
  python3 reels.py --only preview   # só a prévia
  python3 reels.py --frame 14.5     # salva um quadro de teste em out/frame.png
  python3 reels.py mix --voz narracao.m4a   # junta sua narração ao vídeo limpo
"""
import argparse
import math
import os
import subprocess
import sys
import zlib
from functools import lru_cache
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import audio

ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(ROOT, "assets")
PIECES = os.path.join(ASSETS, "pieces")
OUT = os.path.join(ROOT, "out")
W, H = 1080, 1920
FPS = 12  # stop motion "em dois": 12 poses por segundo
DUR = 68.0
FONT = os.path.join(ASSETS, "fonts", "LuckiestGuy-Regular.ttf")

CREAM = (255, 244, 220)
YELLOW = (255, 206, 40)
GREEN = (160, 230, 50)
RED = (235, 50, 45)
PURPLE = (120, 50, 170)
INK = (30, 12, 40)


def ffmpeg_exe():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


# ---------------------------------------------------------------- utilidades
def seg(t, a, b):
    return min(1.0, max(0.0, (t - a) / (b - a)))


def ease_io(u):
    return u * u * (3 - 2 * u)


def ease_out(u):
    return 1 - (1 - u) ** 2


def lerp(a, b, u):
    return a + (b - a) * u


POP = [0.25, 0.75, 1.22, 1.08, 0.95, 1.0]


def pop(t, t0):
    """Escala de "entrada" em poucas poses, como um recorte colocado na mesa."""
    if t < t0:
        return None
    k = int((t - t0) * FPS)
    return POP[k] if k < len(POP) else 1.0


@lru_cache(None)
def font(size):
    return ImageFont.truetype(FONT, size)


@lru_cache(None)
def piece(name):
    path = os.path.join(PIECES, name)
    im = Image.open(path).convert("RGBA")
    return im


def scaled(name, width):
    return _scaled(name, int(width))


@lru_cache(None)
def _scaled(name, width):
    im = piece(name)
    h = int(im.height * width / im.width)
    return im.resize((width, h), Image.LANCZOS)


# ---------------------------------------------------------------- composição
class Ctx:
    def __init__(self, fi):
        self.fi = fi
        self.t = fi / FPS
        self.rng = np.random.default_rng(fi * 7919 + 17)
        self.lt = 0.0

    def j(self, a):
        return float(self.rng.uniform(-a, a))


def place(canvas, ctx, im, x, y, rot=0.0, sc=1.0, sx=1.0, sy=1.0, lift=0.0,
          shadow=0.55, alpha=1.0, jitter=1.0):
    """Cola uma peça recortada com sombra e o erro de posicionamento da mão."""
    if im is None:
        return
    x += ctx.j(2.0 * jitter)
    y += ctx.j(2.0 * jitter)
    rot += ctx.j(0.9 * jitter)
    w = max(2, int(im.width * sc * sx))
    h = max(2, int(im.height * sc * sy))
    if (w, h) != im.size:
        im = im.resize((w, h), Image.BICUBIC)
    if abs(rot) > 0.05:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    a = im.getchannel("A")
    if alpha < 1.0:
        a = a.point(lambda v: int(v * alpha))
        im.putalpha(a)
    px, py = int(x - im.width / 2), int(y - im.height / 2)
    if shadow > 0:
        blur = 7 + lift * 0.06
        op = shadow * alpha * max(0.25, 1 - lift / 500)
        pad = int(blur * 2 + 4)
        sm = Image.new("L", (im.width + pad * 2, im.height + pad * 2), 0)
        sm.paste(a.point(lambda v: int(v * op)), (pad, pad))
        sm = sm.filter(ImageFilter.GaussianBlur(blur))
        ox, oy = int(10 + lift * 0.35), int(16 + lift * 0.8)
        canvas.paste((8, 0, 14), (px - pad + ox, py - pad + oy), sm)
    canvas.paste(im, (px, py), im)


# ---------------------------------------------------------------- adesivos de texto
def wrap(text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if fnt.getlength(test) <= maxw or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return "\n".join(lines)


@lru_cache(None)
def sticker(text, size=92, color=CREAM, maxw=930, ink=INK, paper=(255, 255, 255)):
    """Texto como recorte de papel: preenchimento, contorno escuro e borda branca."""
    fnt = font(size)
    txt = wrap(text, fnt, maxw)
    s1 = max(4, size // 11)
    s2 = s1 + max(6, size // 7)
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    bb = d.multiline_textbbox((0, 0), txt, font=fnt, align="center", spacing=8, stroke_width=s2)
    bb = [int(math.floor(bb[0])), int(math.floor(bb[1])), int(math.ceil(bb[2])), int(math.ceil(bb[3]))]
    pad = 10
    w, h = bb[2] - bb[0] + pad * 2, bb[3] - bb[1] + pad * 2
    org = (pad - bb[0], pad - bb[1])

    def mask(stroke):
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).multiline_text(org, txt, font=fnt, fill=255, align="center",
                                         spacing=8, stroke_width=stroke, stroke_fill=255)
        return m

    m2 = mask(s2).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.2))
    out = Image.new("RGBA", (w, h), paper + (0,))
    out.putalpha(m2)
    layer = Image.new("RGBA", (w, h), ink + (255,))
    out.paste(layer, (0, 0), mask(s1))
    fill = Image.new("RGBA", (w, h), color + (255,))
    out.paste(fill, (0, 0), mask(0))
    return out


def headline(canvas, ctx, text, t0, t1=None, y=300, size=92, color=CREAM, x=540, rot=0.0):
    lt = ctx.lt
    if lt < t0 or (t1 is not None and lt >= t1):
        return
    s = pop(lt, t0)
    place(canvas, ctx, sticker(text, size, color), x, y, rot=rot, sc=s, shadow=0.6)


@lru_cache(None)
def star(size, color=YELLOW):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = size / 2
    pts = []
    for k in range(10):
        r = (c - 8) if k % 2 == 0 else (c - 8) * 0.45
        a = -math.pi / 2 + k * math.pi / 5
        pts.append((c + r * math.cos(a), c + r * math.sin(a)))
    d.polygon(pts, fill=(255, 255, 255, 255))
    inner = [(c + (px - c) * 0.8, c + (py - c) * 0.8) for px, py in pts]
    d.polygon(inner, fill=color + (255,))
    return im


# ---------------------------------------------------------------- fundos
@lru_cache(None)
def bg_table():
    im = piece("board_photo.png").convert("RGB")
    s = H / im.height
    im = im.resize((int(im.width * s), H), Image.LANCZOS)
    x0 = (im.width - W) // 2
    im = im.crop((x0, 0, x0 + W, H)).filter(ImageFilter.GaussianBlur(14))
    a = np.asarray(im, np.float32) * np.array([0.42, 0.34, 0.50])
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


BOARD_X0 = 300
BOARD_S = H / 1080


@lru_cache(None)
def bg_board():
    im = piece("board_photo.png").convert("RGB")
    im = im.resize((int(im.width * BOARD_S), H), Image.LANCZOS)
    x0 = int(BOARD_X0 * BOARD_S)
    im = im.crop((x0, 0, x0 + W, H))
    a = np.asarray(im, np.float32) * 0.82
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def board_pt(x, y):
    return ((x - BOARD_X0) * BOARD_S, y * BOARD_S)


@lru_cache(None)
def bg_art(dark=0.38):
    im = piece("art.jpg").convert("RGB")
    s = H / im.height
    im = im.resize((int(im.width * s), H), Image.LANCZOS)
    x0 = (im.width - W) // 2
    im = im.crop((x0, 0, x0 + W, H)).filter(ImageFilter.GaussianBlur(10))
    a = np.asarray(im, np.float32) * dark
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def background(ctx, which):
    im = {"table": bg_table, "board": bg_board, "art": bg_art}[which]()
    return im.copy()


# ---------------------------------------------------------------- logo da loja
LOGO_PATH = os.path.join(ASSETS, "logo_suavez.png")


@lru_cache(None)
def logo():
    if os.path.exists(LOGO_PATH):
        # logo oficial sobre um cartão branco, para ler bem nos fundos escuros
        lg = Image.open(LOGO_PATH).convert("RGBA")
        pad = int(lg.width * 0.06)
        card = Image.new("RGBA", (lg.width + pad * 2, lg.height + pad * 2), (0, 0, 0, 0))
        ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1),
                                               radius=pad * 2, fill=(255, 255, 255, 255))
        card.alpha_composite(lg, (pad, pad))
        return card
    # marcador provisório até chegar o logo oficial
    S = 600
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((6, 6, S - 6, S - 6), fill=(255, 255, 255, 255))
    d.ellipse((22, 22, S - 22, S - 22), fill=(255, 196, 30, 255))
    d.ellipse((46, 46, S - 46, S - 46), outline=INK + (255,), width=8)
    f1, f2 = font(150), font(46)
    for txt, f, y in (("SUA", f1, 205), ("VEZ", f1, 355), ("LOCAÇÃO DE JOGOS", f2, 480)):
        d.text((S / 2, y), txt, font=f, fill=INK + (255,), anchor="mm")
    return im


@lru_cache(None)
def watermark():
    lg = logo()
    w = 200
    im = lg.resize((w, int(lg.height * w / lg.width)), Image.LANCZOS)
    im.putalpha(im.getchannel("A").point(lambda v: int(v * 0.62)))
    return im


# ---------------------------------------------------------------- peças
DICE = ["die_A0.png", "die_A2.png", "die_A3a.png", "die_A3b.png",
        "die_B2.png", "die_B4.png", "die_B5a.png", "die_B5b.png"]
SKULLS = [f"skull_{i}.png" for i in range(5)]
DIE_W = 235


def die_img(name):
    return scaled(name, DIE_W)


def doll_img(width):
    return scaled("doll.png", width)


def bounce_path(u, p0, p1, height, n=3):
    e = ease_out(u)
    x = lerp(p0[0], p1[0], e)
    y = lerp(p0[1], p1[1], e)
    lift = abs(math.sin(math.pi * n * e)) * height * (1 - e) ** 1.2
    return x, y - lift, lift


# ---------------------------------------------------------------- cenas
# Cada cena recebe ctx (ctx.lt = tempo local) e devolve a imagem RGB.

def s_hook(ctx):
    lt = ctx.lt
    c = background(ctx, "table")
    # caveiras entram uma a uma, pulando
    spots = [(165, 760), (915, 760), (190, 1170), (890, 1170)]
    for i, (x, y) in enumerate(spots):
        t0 = 1.5 + i * 0.28
        if lt < t0:
            continue
        u = seg(lt, t0, t0 + 0.5)
        sx0 = -150 if x < 540 else W + 150
        px, py, lift = bounce_path(u, (sx0, y - 200), (x, y), 160, 2)
        rot = (1 - u) * (-40 if x < 540 else 40)
        place(c, ctx, scaled(SKULLS[i], 150), px, py, rot=rot, lift=lift)
    # boneco entra saltando de baixo
    u = seg(lt, 0.15, 1.2)
    x, y, lift = bounce_path(u, (540, 2400), (540, 930), 260, 3)
    shake = 0.0
    sx = sy = 1.0
    since = lt - 3.0
    if 0 <= since < 0.7:
        k = int(since * FPS)
        shake = [26, -22, 18, -14, 9, -5, 3, 0, 0][k]
        sx, sy = [(1.12, 0.9), (0.93, 1.08), (1.05, 0.96), (1, 1)][min(k, 3)]
    rot = math.sin(lt * 5) * 3 if u >= 1 else (1 - u) * 20
    place(c, ctx, doll_img(620), x + shake, y, rot=rot, sx=sx, sy=sy, lift=lift)
    if 3.0 <= lt < 3.9:
        k = int((lt - 3.0) * FPS)
        for i in range(6):
            a = i * math.pi / 3 + 0.3
            r = 330 + k * 22
            place(c, ctx, star(90 if i % 2 else 70), 540 + r * math.cos(a), 930 + r * math.sin(a) * 1.2,
                  rot=k * 25, shadow=0.3)
    headline(c, ctx, "E SE VOCÊ PUDESSE", 0.3, y=250, size=78)
    headline(c, ctx, "AMALDIÇOAR SEUS AMIGOS?", 1.1, y=410, size=100, color=GREEN)
    headline(c, ctx, "+ PONTOS?!", 3.3, x=800, y=1330, size=110, color=YELLOW, rot=8)
    return c


def s_title(ctx):
    lt = ctx.lt
    c = background(ctx, "art")
    box = scaled("box.png", 720)
    # boneco espiando atrás da caixa
    if lt >= 2.6:
        u = ease_io(seg(lt, 2.6, 3.3))
        place(c, ctx, doll_img(430), lerp(700, 905, u), 900, rot=lerp(0, -14, u) + math.sin(lt * 6) * 2)
    u = seg(lt, 0.1, 0.55)
    y = lerp(-700, 960, ease_io(u) ** 2)
    sx = sy = 1.0
    since = lt - 0.55
    if 0 <= since < 0.35:
        sx, sy = [(1.06, 0.92), (0.97, 1.04), (1.01, 0.99), (1, 1)][min(int(since * FPS), 3)]
    place(c, ctx, box, 540, y, rot=(1 - u) * -12, sx=sx, sy=sy, lift=(1 - u) * 300)
    lg = pop(lt, 1.1)
    if lg:
        place(c, ctx, scaled("logo_vudu.png", 860), 540, 260, sc=lg, rot=math.sin(lt * 4) * 1.5)
    headline(c, ctx, "O JOGO DAS MALDIÇÕES", 1.8, 3.6, y=1370, size=84, color=YELLOW, rot=-3)
    headline(c, ctx, "SEUS AMIGOS VIRAM AS VÍTIMAS", 3.6, y=1370, size=78, color=GREEN, rot=2)
    return c


# rolagem de dados -------------------------------------------------------
FINAL = [(190, 960), (385, 1135), (560, 945), (760, 1120), (905, 960)]
FINAL_FACE = ["die_A3b.png", "die_A0.png", "die_B2.png", "die_B5b.png", "die_B4.png"]
FINAL_ROT = [-9, 13, 4, -15, 8]
KEEP = [0, 2, 3]
ROW = [(170, 660), (390, 660), (610, 660), (830, 660)]
T_THROW = 0.5
T_REROLL = 6.6


def throw_state(k, lt, t0, p0, p1, rot_f, face_f, dur):
    u = seg(lt, t0, t0 + dur)
    x, y, lift = bounce_path(u, p0, p1, 260, 3)
    if u < 1:
        ctx_face = DICE[(int(lt * FPS) * 3 + k * 5) % len(DICE)]
        rot = rot_f + (1 - ease_out(u)) * (620 + k * 90)
        return x, y, rot, ctx_face, lift
    return x, y, rot_f, face_f, 0.0


def die_roll_scene(ctx, c):
    lt = ctx.lt
    slot_of = {0: 0, 2: 1, 3: 2}
    for k in range(5):
        t0 = T_THROW + k * 0.07
        if lt < t0:
            continue
        dur = 1.15 + k * 0.08
        p0 = (W + 180 + k * 40, 1650 - k * 30)
        x, y, rot, face, lift = throw_state(k, lt, t0, p0, FINAL[k], FINAL_ROT[k], FINAL_FACE[k], dur)
        sc = 1.0
        if k in KEEP:  # guardar os que servem
            s0 = 3.6 + KEEP.index(k) * 0.14
            u = ease_io(seg(lt, s0, s0 + 0.55))
            if u > 0:
                tx, ty = ROW[slot_of[k]]
                lift = math.sin(math.pi * u) * 120
                x, y = lerp(x, tx, u), lerp(y, ty, u) - lift
                rot = lerp(rot, 0, u)
                sc = lerp(1.0, 0.82, u)
        if k == 4:  # um dado vai embora: custo da nova rolagem
            u = seg(lt, 5.4, 5.9)
            if u >= 1:
                continue
            if u > 0:
                lift = u * 250
                x, y = lerp(x, W + 200, ease_io(u)), y - lift
                rot += u * 90
        if k == 1:  # o dado que é rolado de novo
            if lt >= T_REROLL:
                x, y, rot, face, lift = throw_state(1, lt, T_REROLL, FINAL[1], (560, 1110), -6,
                                                    "die_A2.png", 1.1)
            u = ease_io(seg(lt, 8.8, 9.4))
            if u > 0:
                tx, ty = ROW[3]
                lift = math.sin(math.pi * u) * 120
                x, y = lerp(x, tx, u), lerp(y, ty, u) - lift
                rot = lerp(rot, 0, u)
                sc = lerp(1.0, 0.82, u)
        place(c, ctx, die_img(face), x, y, rot=rot, sc=sc, lift=lift)


def s_dice(ctx):
    lt = ctx.lt
    c = background(ctx, "table")
    die_roll_scene(ctx, c)
    headline(c, ctx, "ROLE 5 DADOS DE INGREDIENTES", 0.2, 3.6, y=330)
    headline(c, ctx, "GUARDE OS QUE SERVEM", 3.6, 5.4, y=330, color=GREEN)
    headline(c, ctx, "CADA NOVA ROLAGEM CUSTA 1 DADO", 5.4, y=330, color=YELLOW)
    if 5.5 <= lt < 7.4:
        place(c, ctx, sticker("-1 DADO", 96, RED), 850, 960, rot=-10, sc=pop(lt, 5.5))
    return c


# carta de maldição ------------------------------------------------------
KEPT_FACES = ["die_A3b.png", "die_B2.png", "die_B5b.png", "die_A2.png"]
CARD_POS = (540, 1080)


def s_card(ctx):
    lt = ctx.lt
    c = background(ctx, "table")
    # dados guardados pulam para dentro da carta
    for i, face in enumerate(KEPT_FACES):
        tx, ty = ROW[i]
        t0 = 2.9 + i * 0.22
        u = seg(lt, t0, t0 + 0.45)
        if u >= 1:
            continue
        x = lerp(tx, CARD_POS[0], u)
        y = lerp(ty, CARD_POS[1] - 60, u) - math.sin(math.pi * u) * 220
        place(c, ctx, die_img(face), x, y, sc=lerp(0.82, 0.3, u), rot=u * 200, lift=math.sin(math.pi * u) * 220)
    # carta: desliza virada, vira e depois voa até o alvo
    u_in = ease_out(seg(lt, 0.2, 1.1))
    x = lerp(W + 400, CARD_POS[0], u_in)
    rot = lerp(25, -3, u_in)
    flip = seg(lt, 1.35, 1.85)
    sx = abs(math.cos(math.pi * flip))
    img = scaled("card_back.png", 640) if flip < 0.5 else scaled("card_kapoera.png", 590)
    y = CARD_POS[1]
    sc = 1.0
    fly = seg(lt, 4.5, 5.2)
    if fly >= 1:
        img = None
    elif fly > 0:
        x = lerp(CARD_POS[0], 540, fly)
        y = lerp(CARD_POS[1], 700, fly)
        sc = lerp(1, 0.25, fly)
        rot = -3 + fly * 540
    if lt >= 0.2:
        place(c, ctx, img, x, y, rot=rot, sx=max(0.04, sx), sc=sc, lift=100 * fly + 30 * math.sin(math.pi * flip))
    # o alvo: o Vuduzinho leva a maldição
    if lt >= 4.3:
        u = ease_out(seg(lt, 4.3, 4.8))
        dx = 0.0
        since = lt - 5.2
        sx2 = sy2 = 1.0
        if 0 <= since < 0.8:
            k = int(since * FPS)
            dx = [30, -26, 22, -18, 12, -8, 5, -3, 0, 0][k]
            sx2, sy2 = [(1.15, 0.88), (0.92, 1.1), (1.05, 0.96), (1, 1)][min(k, 3)]
        place(c, ctx, doll_img(520), lerp(-400, 540, u) + dx, 960, rot=lerp(-30, 0, u) + math.sin(lt * 7) * 3,
              sx=sx2, sy=sy2)
        if 5.2 <= lt < 6.2:
            k = int((lt - 5.2) * FPS)
            for i in range(7):
                a = i * 2 * math.pi / 7
                r = 300 + k * 18
                place(c, ctx, star(80 if i % 2 else 60, GREEN), 540 + r * math.cos(a), 960 + r * math.sin(a),
                      rot=k * 30, shadow=0.3)
    if 5.2 <= lt < 5.3:  # clarão
        c = Image.blend(c, Image.new("RGB", c.size, (220, 255, 200)), 0.55)
    headline(c, ctx, "JUNTOU OS INGREDIENTES DA CARTA?", 0.3, 5.2, y=330)
    headline(c, ctx, "LANCE A MALDIÇÃO!", 5.2, y=330, color=GREEN, size=104)
    if lt >= 5.6:
        place(c, ctx, sticker("+ PONTOS!", 110, YELLOW), 790, 1330, rot=9, sc=pop(lt, 5.6))
    return c


# maldições ----------------------------------------------------------------
def s_curse_feet(ctx):
    lt = ctx.lt
    c = background(ctx, "table")
    s = pop(lt, 0.1) or 0
    if s:
        place(c, ctx, scaled("card_kapoera.png", 440), 540, 650, rot=-4 + math.sin(lt * 3) * 1.5, sc=s)
    # boneco "flutuando": nunca encosta o pé no chão
    hop = abs(math.sin(lt * math.pi * 1.4))
    lift = 60 + hop * 110
    base_y = 1290
    kick = math.sin(lt * 11) * 7
    place(c, ctx, doll_img(380), 540, base_y - lift, rot=kick, lift=lift, sx=1 + hop * 0.04, sy=1 - hop * 0.03)
    headline(c, ctx, "PÉ NO CHÃO? NEM PENSAR!", 0.4, y=250, size=88, color=YELLOW)
    return c


def s_curse_arms(ctx):
    lt = ctx.lt
    c = background(ctx, "table")
    s = pop(lt, 0.1) or 0
    if s:
        place(c, ctx, scaled("card_tutakobraco.png", 430), 540, 650, rot=3 + math.sin(lt * 3) * 1.5, sc=s)
    tremble = math.sin(lt * 23) * 0.025
    stretch = 1.0 + 0.12 * ease_io(seg(lt, 0.5, 1.4)) + tremble
    place(c, ctx, doll_img(390), 540, 1210, sx=stretch, sy=1 - (stretch - 1) * 0.4, rot=math.sin(lt * 9) * 1.5)
    headline(c, ctx, "BRAÇOS ESTICADOS O TEMPO TODO!", 0.4, y=270, size=84, color=GREEN)
    if lt >= 5.3:
        place(c, ctx, sticker("E TEM PIOR...", 92, RED), 540, 1380, rot=-6, sc=pop(lt, 5.3))
    return c


# erro e pontuação -----------------------------------------------------------
SPACE = {n: board_pt(*p) for n, p in {
    7: (668, 331), 9: (805, 425), 10: (736, 533), 11: (601, 624)}.items()}
RED_SKULL = "skull_3.png"


def skull_on_board(c, ctx, lt, hops, start):
    """hops: lista de (t0, destino). Caveira vermelha pulando no marcador de pontos."""
    pos = SPACE[start]
    for t0, dest in hops:
        u = seg(lt, t0, t0 + 0.42)
        if u <= 0:
            break
        p1 = SPACE[dest]
        lift = math.sin(math.pi * u) * 190
        pos_now = (lerp(pos[0], p1[0], ease_io(u)), lerp(pos[1], p1[1], ease_io(u)) - lift)
        if u < 1:
            place(c, ctx, scaled(RED_SKULL, 175), pos_now[0], pos_now[1] - 70, rot=math.sin(math.pi * u) * 25, lift=lift)
            return p1
        pos = p1
    place(c, ctx, scaled(RED_SKULL, 175), pos[0], pos[1] - 70)
    return pos


def s_fail(ctx):
    lt = ctx.lt
    if lt < 3.0:
        c = background(ctx, "table")
        # braços caem e o pé encosta no chão
        u = ease_io(seg(lt, 0.7, 1.2))
        y = lerp(1000, 1080, u)
        place(c, ctx, doll_img(560), 540, y, sx=lerp(1.0, 0.86, u), sy=lerp(1.0, 1.04, u), rot=lerp(0, -6, u))
        headline(c, ctx, "ESQUECEU A MALDIÇÃO?", 0.2, y=320, size=92)
        s = pop(lt, 1.4)
        if s:
            place(c, ctx, sticker("ESQUECEU!", 140, RED), 540, 1000, rot=-12, sc=s)
        return c
    c = background(ctx, "board")
    ltb = lt - 3.0
    skull_on_board(c, ctx, ltb, [(0.8, 9)], 7)
    headline(c, ctx, "PONTOS EXTRAS PRA QUEM LANÇOU!", 0.1, y=300, size=86, color=YELLOW)
    if ltb >= 1.2:
        x, y = SPACE[9]
        place(c, ctx, sticker("+2", 150, YELLOW), x - 190, y - 210, rot=-10, sc=pop(ltb, 1.2))
    return c


CONFETTI_COLORS = [(255, 206, 40), (160, 230, 50), (235, 50, 45), (80, 170, 255), (255, 110, 200)]


def s_win(ctx):
    lt = ctx.lt
    c = background(ctx, "board")
    pos = skull_on_board(c, ctx, lt, [(0.3, 10), (0.9, 11)], 9)
    if lt >= 1.5:
        d = ImageDraw.Draw(c)
        rng = np.random.default_rng(42)
        k = int((lt - 1.5) * FPS)
        for i in range(70):
            x0 = rng.uniform(0, W)
            vy = rng.uniform(40, 90)
            y = -40 + (k * vy + rng.uniform(0, 300)) % (H + 80)
            x = x0 + math.sin(k * 0.6 + i) * 25
            col = CONFETTI_COLORS[i % len(CONFETTI_COLORS)]
            sz = rng.uniform(14, 26)
            ang = (k * 40 + i * 33) % 180
            cs = abs(math.cos(math.radians(ang)))
            d.polygon([(x - sz, y - sz * 0.5 * cs), (x + sz, y - sz * 0.5 * cs),
                       (x + sz, y + sz * 0.5 * cs), (x - sz, y + sz * 0.5 * cs)], fill=col)
        place(c, ctx, sticker("VENCEU!", 120, GREEN), pos[0] + 40, pos[1] - 290, rot=-8, sc=pop(lt, 1.5))
    headline(c, ctx, "11 PONTOS = VITÓRIA!", 0.1, y=300, size=100, color=YELLOW)
    chips = [("2 A 8 JOGADORES", 2.3), ("PARTIDAS DE ~30 MIN", 2.7), ("A PARTIR DE 8 ANOS", 3.1)]
    for i, (txt, t0) in enumerate(chips):
        s = pop(lt, t0)
        if s:
            place(c, ctx, sticker(txt, 62, CREAM, ink=PURPLE), 540, 1170 + i * 105, rot=(-2, 2, -1)[i], sc=s)
    return c


def s_cta(ctx):
    lt = ctx.lt
    c = background(ctx, "art")
    s = pop(lt, 0.3)
    if s:
        place(c, ctx, scaled("box.png", 330), 200, 1310, rot=-8, sc=s)
    s = pop(lt, 0.5)
    if s:
        wave = math.sin(lt * 8) * 7
        place(c, ctx, doll_img(300), 880, 1300, rot=wave, sc=s)
    s = pop(lt, 0.2)
    if s:
        lg = logo()
        place(c, ctx, lg.resize((760, int(lg.height * 760 / lg.width)), Image.LANCZOS), 540, 450,
              sc=s, rot=math.sin(lt * 3) * 2, shadow=0.7)
    if lt < 5.0:
        headline(c, ctx, "ALUGUE O VUDÚ", 1.1, y=790, size=100)
        headline(c, ctx, "NA SUA VEZ!", 1.5, y=910, size=118, color=YELLOW, rot=-3)
    else:
        headline(c, ctx, "COMENTA AÍ:", 5.0, y=770, size=96, color=YELLOW, rot=-3)
        headline(c, ctx, "QUAL MALDIÇÃO VOCÊ JOGARIA NO SEU MELHOR AMIGO?", 5.3, y=940, size=66)
    s = pop(lt, 2.7)
    if s:
        bob = abs(math.sin(lt * 5)) * 14
        place(c, ctx, sticker("LINK NA BIO", 90, GREEN), 540, 1120 + bob, rot=2, sc=s)
    return c


SCENES = [
    (0.0, 5.0, s_hook),
    (5.0, 11.0, s_title),
    (11.0, 22.0, s_dice),
    (22.0, 30.0, s_card),
    (30.0, 37.5, s_curse_feet),
    (37.5, 45.0, s_curse_arms),
    (45.0, 52.0, s_fail),
    (52.0, 58.0, s_win),
    (58.0, 68.0, s_cta),
]

# legendas (mesmo texto do roteiro de narração)
SUBS = [
    (0.2, 2.5, "E se você pudesse amaldiçoar seus amigos..."),
    (2.5, 4.9, "...e ainda ganhar pontos com isso?"),
    (5.1, 7.9, "Esse é o Vudú: o jogo em que você é um feiticeiro perverso..."),
    (7.9, 10.9, "...e a sua galera vira vítima."),
    (11.2, 14.3, "Na sua vez, você rola cinco dados de ingredientes."),
    (14.3, 17.3, "Não gostou? Guarda os que servem e rola de novo..."),
    (17.3, 21.8, "...mas cada nova rolagem custa um dado."),
    (22.3, 25.4, "Juntou os ingredientes da carta?"),
    (25.4, 29.7, "Lança a maldição em alguém da mesa e marca pontos."),
    (30.1, 31.8, "E aí começa o caos!"),
    (31.8, 37.3, "Na Kapoera, a vítima não pode encostar os pés no chão..."),
    (37.6, 42.6, "Na Tutakobraço, tem que ficar com os braços esticados..."),
    (42.6, 44.9, "...e tem maldição muito pior."),
    (45.3, 48.0, "Esqueceu da maldição?"),
    (48.0, 51.8, "Quem lançou ganha ainda mais pontos."),
    (52.2, 54.9, "Quem chegar primeiro nos 11 pontos vence."),
    (54.9, 57.9, "De 2 a 8 pessoas, em uns 30 minutos."),
    (58.2, 60.9, "Quer amaldiçoar sua galera no fim de semana?"),
    (60.9, 63.4, "Aluga o Vudú na Sua Vez: link na bio!"),
    (63.4, 67.8, "E comenta: qual maldição você jogaria no seu melhor amigo?"),
]


# ---------------------------------------------------------------- narração gravada
TIMELINE_PATH = os.path.join(ROOT, "narracao", "timeline.json")
TIMELINE = None
if os.path.exists(TIMELINE_PATH):
    import json
    TIMELINE = json.load(open(TIMELINE_PATH, encoding="utf-8"))
    DUR = TIMELINE["duracao"]
    SUBS = [tuple(x) for x in TIMELINE["legendas"]]
    # cada cena é esticada/encurtada para caber a fala: (início_novo, fim_novo, função, duração_original)
    PLAY = [(n0, n1, fn, (o1 - o0) / (n1 - n0)) for (o0, o1, n0, n1), (_, _, fn) in zip(TIMELINE["cenas"], SCENES)]
else:
    PLAY = [(t0, t1, fn, 1.0) for t0, t1, fn in SCENES]
CTA_START = PLAY[-1][0]


def warp(t_orig):
    """Converte um instante da linha do tempo original para a nova (efeitos sonoros)."""
    if TIMELINE is None:
        return t_orig
    for o0, o1, n0, n1 in TIMELINE["cenas"]:
        if o0 <= t_orig < o1:
            return n0 + (t_orig - o0) * (n1 - n0) / (o1 - o0)
    return t_orig - TIMELINE["cenas"][-1][1] + TIMELINE["cenas"][-1][3]


@lru_cache(None)
def sub_img(text):
    fnt = font(54)
    txt = wrap(text, fnt, 900)
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    bb = d.multiline_textbbox((0, 0), txt, font=fnt, align="center", spacing=6, stroke_width=7)
    bb = [int(math.floor(bb[0])), int(math.floor(bb[1])), int(math.ceil(bb[2])), int(math.ceil(bb[3]))]
    w, h = bb[2] - bb[0] + 20, bb[3] - bb[1] + 20
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).multiline_text((10 - bb[0], 10 - bb[1]), txt, font=fnt, fill=(255, 255, 255, 255),
                                      align="center", spacing=6, stroke_width=7, stroke_fill=(0, 0, 0, 255))
    return im


# ---------------------------------------------------------------- pós (câmera e película)
@lru_cache(None)
def vignette():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2) / 1.414
    return (1 - 0.55 * np.clip(r, 0, 1) ** 2.2)[..., None]


def post(img, ctx):
    a = np.asarray(img, np.float32)
    expo = 1.0 + ctx.j(0.035)  # oscilação da luz entre as poses
    a = a * vignette() * expo
    g = ctx.rng.normal(0, 3.5, (H // 2, W // 2)).astype(np.float32)
    g = np.repeat(np.repeat(g, 2, 0), 2, 1)[..., None]
    a = np.clip(a + g, 0, 255).astype(np.uint8)
    dx, dy = int(ctx.rng.integers(-2, 3)), int(ctx.rng.integers(-2, 3))  # câmera levemente mexida
    a = np.roll(a, (dy, dx), (0, 1))
    return a


def render_frame(args):
    fi, subs = args
    ctx = Ctx(fi)
    t = ctx.t
    for t0, t1, fn, k in PLAY:
        if t0 <= t < t1:
            ctx.lt = (t - t0) * k
            img = fn(ctx)
            break
    else:
        t0, _, fn, k = PLAY[-1]
        ctx.lt = (t - t0) * k
        img = fn(ctx)
    if t < CTA_START:
        wm = watermark()
        img.paste(wm, (W - wm.width - 34, 96), wm)
    if subs:
        for a, b, txt in SUBS:
            if a <= t < b:
                s = sub_img(txt)
                img.paste(s, ((W - s.width) // 2, 1500 - s.height // 2), s)
    return post(img, ctx).tobytes()


def render(out_path, wav, subs, workers=4):
    n = int(DUR * FPS)
    cmd = [ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-framerate", str(FPS), "-i", "-", "-i", wav,
           "-vf", "fps=24", "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-maxrate", "7M", "-bufsize", "14M",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
           "-movflags", "+faststart", out_path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(workers) as pool:
        for i, fr in enumerate(pool.imap(render_frame, [(k, subs) for k in range(n)], chunksize=4)):
            p.stdin.write(fr)
            if i % 120 == 0:
                print(f"  quadro {i}/{n}", flush=True)
    p.stdin.close()
    p.wait()
    print("ok:", out_path)


def mix(voice, out_path):
    clean = os.path.join(OUT, "vudu_limpo.mp4")
    fc = ("[1:a]highpass=f=80,acompressor=threshold=0.1:ratio=3:attack=10:release=200,"
          "loudnorm=I=-16:TP=-1.5,asplit=2[v1][v2];"
          "[0:a][v1]sidechaincompress=threshold=0.04:ratio=8:attack=20:release=400[duck];"
          "[duck][v2]amix=inputs=2:normalize=0,alimiter=limit=0.95[a]")
    subprocess.run([ffmpeg_exe(), "-y", "-i", clean, "-i", voice, "-filter_complex", fc,
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", out_path], check=True)
    print("ok:", out_path)


def write_srt(path):
    def ts(s):
        ms = int(round(s * 1000))
        return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"
    with open(path, "w", encoding="utf-8") as f:
        for i, (a, b, txt) in enumerate(SUBS, 1):
            f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{txt}\n\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="render", choices=["render", "mix"])
    ap.add_argument("--only", choices=["preview", "limpo"])
    ap.add_argument("--frame", type=float)
    ap.add_argument("--voz")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.cmd == "mix":
        mix(a.voz, os.path.join(OUT, "vudu_final.mp4"))
        return
    if a.frame is not None:
        fr = render_frame((int(a.frame * FPS), True))
        Image.frombytes("RGB", (W, H), fr).save(os.path.join(OUT, "frame.png"))
        return
    wav = os.path.join(OUT, "trilha.wav")
    voz = [(os.path.join(ROOT, v["arquivo"]), v["inicio"]) for v in TIMELINE["voz"]] if TIMELINE else None
    audio.build(wav, DUR, warp=warp, voz=voz)
    write_srt(os.path.join(ROOT, "legendas.srt"))
    if a.only != "limpo":
        render(os.path.join(OUT, "vudu_preview.mp4"), wav, subs=True)
    if a.only != "preview":
        render(os.path.join(OUT, "vudu_limpo.mp4"), wav, subs=False)


if __name__ == "__main__":
    main()
