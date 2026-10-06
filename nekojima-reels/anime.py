#!/usr/bin/env python3
"""Reels do Nekojima em estilo ANIME (escolhido pelo dono; a versão "transmissão esportiva" em neko.py foi engano).

Cada cena é um "corte" de anime: foto oficial num painel inclinado com borda branca, linhas de velocidade
piscando no fundo, onomatopeias em japonês (ドキドキ, ガシャーン, ビリビリ, ニャー...), pétalas de sakura,
quadro de impacto, card de episódio e tela de VS. Mesmo roteiro, cenas e narração do neko.py.

    python3 anime.py --frame 3 10 20      # quadros de teste (out/frames.jpg)
    python3 anime.py --only preview       # prévia com legendas
    python3 anime.py                      # com e sem legendas
"""
import argparse
import math
import os
import subprocess
from functools import lru_cache
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps

import neko
from neko import (SCENES, ROTEIRO, to_orig, warp, seg, ease, lerp, out_back, wrap, photo, box_img, logo_card,
                  ffmpeg_exe, scene_of)

ROOT = neko.ROOT
FONTS = neko.FONTS
OUT = neko.OUT
W, H, FPS = 1080, 1920, 30
POSE = 12  # linhas de velocidade e tremidas trocam a 12 poses/s, como em anime

WHITE = (255, 255, 255)
INK = (24, 16, 40)
PINK = (255, 92, 150)
SAKURA = (255, 190, 210)
TEAL = (40, 200, 190)
YELLOW = (255, 220, 60)
RED = (232, 40, 60)
PURPLE = (110, 70, 190)
NAVY = (20, 24, 70)


@lru_cache(None)
def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


DELA = "DelaGothicOne-Regular.ttf"
POP = "Poppins-ExtraBold.ttf"

# paleta de cada cena (topo, base) — céu de anime
PAL = [((255, 120, 90), (120, 30, 80)), ((90, 200, 230), (255, 170, 200)), ((255, 200, 90), (255, 110, 150)),
       ((120, 220, 210), (60, 90, 190)), ((255, 160, 80), (200, 50, 90)), ((90, 70, 170), (230, 70, 120)),
       ((255, 170, 210), (120, 90, 220)), ((40, 40, 90), (230, 60, 90)), ((90, 200, 230), (255, 170, 200))]

# painel de cada cena: foto, zoom (início, fim), foco (início, fim), inclinação
PANEL = [("torre2.jpg", (1.0, 1.15), (540, 480), (560, 430), -3),
         ("capa_arte.jpg", (1.0, 1.06), (540, 560), (540, 600), 2),
         ("dados.jpg", (1.1, 1.5), (420, 560), (300, 560), -2),
         ("loja2.jpg", (1.2, 1.7), (560, 560), (700, 640), 3),
         ("torre.jpg", (1.05, 1.3), (450, 420), (450, 400), -2),
         ("torre2.jpg", (1.35, 1.55), (650, 420), (680, 460), 2),
         ("gato_fio.jpg", (1.0, 1.2), (540, 520), (520, 470), -3),
         ("caiu.jpg", (1.0, 1.12), (540, 560), (560, 560), 3),
         ("capa_arte.jpg", (1.0, 1.0), (540, 540), (540, 540), 0)]
PX0, PY0, PX1, PY1 = 40, 300, 1040, 1480  # caixa do painel


@lru_cache(None)
def sky(i):
    a, b = (np.array(c, np.float32) for c in PAL[i])
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    img = a * (1 - y) + b * y
    img = np.repeat(img, W, 1)
    return Image.fromarray(img.clip(0, 255).astype(np.uint8))


@lru_cache(None)
def speed_lines(i, k, cx=540, cy=900):
    """Linhas de foco radiais (4 variações sorteadas que se alternam)."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(i * 10 + k)
    R = 2400
    for _ in range(110):
        a = rng.uniform(0, 2 * math.pi)
        w = rng.uniform(0.004, 0.02)
        r0 = rng.uniform(380, 700)
        p = [(cx + math.cos(a - w) * R, cy + math.sin(a - w) * R), (cx + math.cos(a) * r0, cy + math.sin(a) * r0),
             (cx + math.cos(a + w) * R, cy + math.sin(a + w) * R)]
        d.polygon(p, fill=(255, 255, 255, int(rng.uniform(60, 150))))
    return im


@lru_cache(None)
def panel_layers(tilt):
    """Máscaras da borda branca, contorno e sombra do painel (caras de calcular: uma vez por inclinação)."""
    m = panel_mask(tilt)
    border = m.filter(ImageFilter.MaxFilter(25))
    outer = border.filter(ImageFilter.MaxFilter(9))
    sh_ = outer.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.5))
    return border, outer, sh_


@lru_cache(None)
def panel_mask(tilt):
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    o = tilt * 14
    d.polygon([(PX0, PY0 + o), (PX1, PY0 - o), (PX1 - 10, PY1 - o), (PX0 + 10, PY1 + o)], fill=255)
    return m


def panel(img, i, t, name=None, z=None, focus=None, shake=0.0):
    pname, (z0, z1), f0, f1, tilt = PANEL[i]
    a, b = SCENES[i]
    u = ease(seg(t, a, b))
    name = name or pname
    z = z or lerp(z0, z1, u)
    fx, fy = focus or (lerp(f0[0], f1[0], u), lerp(f0[1], f1[1], u))
    pw, ph = PX1 - PX0, PY1 - PY0
    im = photo(name)
    s = min(im.width, im.height) / z
    sw, sh = s * pw / ph, s
    if sw > im.width:
        sw, sh = im.width, im.width * ph / pw
    x0 = min(max(0, fx - sw / 2 + shake * math.sin(t * 70)), im.width - sw)
    y0 = min(max(0, fy - sh / 2 + shake * math.cos(t * 53)), im.height - sh)
    view = im.resize((pw, ph), Image.BICUBIC, box=(x0, y0, x0 + sw, y0 + sh))
    layer = Image.new("RGB", (W, H))
    layer.paste(view, (PX0, PY0))
    m = panel_mask(tilt)
    # sombra + borda branca grossa + contorno escuro, estilo cut-in de anime
    border, outer, sh_ = panel_layers(tilt)
    img.paste((20, 10, 30), (14, 22), sh_)
    img.paste(INK, (0, 0), outer)
    img.paste(WHITE, (0, 0), border)
    img.paste(layer, (0, 0), m)

    def to_s(px, py):
        return PX0 + (px - x0) * pw / sw, PY0 + (py - y0) * ph / sh
    return to_s


# ---------------------------------------------------------------- letreiros
@lru_cache(None)
def sfx_img(text, size=150, fill=YELLOW):
    """Onomatopeia japonesa: preenchimento colorido, contorno branco grosso e borda escura."""
    f = font(DELA, size)
    tw = f.getlength(text)
    w, h = int(tw + size), int(size * 1.7)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = (w / 2, h / 2)
    d.text(c, text, font=f, fill=INK, anchor="mm", stroke_width=int(size * 0.2), stroke_fill=INK)
    d.text(c, text, font=f, fill=WHITE, anchor="mm", stroke_width=int(size * 0.13), stroke_fill=WHITE)
    d.text(c, text, font=f, fill=fill, anchor="mm")
    return im


@lru_cache(None)
def title_img(text, size=84, stroke=PINK, maxw=960, fill=WHITE):
    f = font(DELA, size)
    while f.getlength(text) > maxw and size > 34:  # cabe numa linha só: diminui a letra em vez de quebrar
        size -= 2
        f = font(DELA, size)
    lines = wrap(text, f, maxw)
    lh = int(size * 1.2)
    tw = max(f.getlength(l) for l in lines)
    sw = max(6, size // 7)
    w, h = int(tw + sw * 4 + 20), int(lh * len(lines) + sw * 4 + 20)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k, l in enumerate(lines):
        c = (w / 2, sw * 2 + 10 + lh * k + lh / 2)
        d.text((c[0] + 6, c[1] + 8), l, font=f, fill=INK, anchor="mm", stroke_width=sw + 4, stroke_fill=INK)
        d.text(c, l, font=f, fill=fill, anchor="mm", stroke_width=sw, stroke_fill=stroke)
    return im


@lru_cache(None)
def tag_img(text, size=44, bg=WHITE, fg=INK):
    f = font(DELA, size)
    w, h = int(f.getlength(text)) + 70, int(size * 1.75)
    im = Image.new("RGBA", (w + 10, h + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 12, w + 8, h + 12), radius=h // 2, fill=INK)
    d.rounded_rectangle((0, 0, w, h), radius=h // 2, fill=bg, outline=INK, width=5)
    d.text((w / 2, h / 2 + 2), text, font=f, fill=fg, anchor="mm")
    return im


def paste_c(img, im, x, y, rot=0.0, scale=1.0, alpha=1.0):
    if scale <= 0.02 or alpha <= 0.01:
        return
    if abs(scale - 1) > 0.002:
        im = im.resize((max(2, int(im.width * scale)), max(2, int(im.height * scale))), Image.BICUBIC)
    if abs(rot) > 0.1:
        im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    if alpha < 1:
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    img.paste(im, (int(x - im.width / 2), int(y - im.height / 2)), im)


def jit(t, a=4.0, seed=0):
    k = int(t * POSE)
    rng = np.random.default_rng(k * 31 + seed)
    return rng.uniform(-a, a), rng.uniform(-a, a)


# elementos: (t0, tipo, args, x, y, rot[, t1]); "sfx" treme a 12 poses/s
ELS = [
    (0.3, "sfx", ("ドキドキ", 120, PINK), 760, 560, 8, 2.6),
    (0.6, "title", ("ESSA TORRE VAI CAIR...", 54, RED), 540, 1590, -2, 2.6),
    (2.7, "sfx", ("ガシャーン!", 150, YELLOW), 540, 760, -8, 5.6),
    (2.9, "title", ("CAIU!!!", 150, RED), 540, 1060, 4, 5.6),
    (3.6, "title", ("E A CULPA É SUA?!", 60, PURPLE), 540, 1590, -2, 5.6),
    (6.0, "title", ("NEKOJIMA", 120, TEAL), 540, 1400, -3),
    (6.6, "tag", ("EPISÓDIO 1 · A ILHA DOS GATOS", 40, YELLOW, INK), 540, 1560, 0),
    (9.6, "tag", ("MISSÃO: MONTAR A REDE ELÉTRICA!", 40, WHITE, INK), 540, 230, 2),
    (10.4, "tag", ("1 A 5 JOGADORES", 40, PINK, WHITE), 300, 1250, -4),
    (12.4, "title", ("ROLA OS DOIS DADOS!", 54, PINK), 540, 215, -2),
    (13.2, "sfx", ("コロコロ", 110, YELLOW), 820, 640, 10, 15.8),
    (14.2, "tag", ("= OS BAIRROS DOS POSTES", 40, YELLOW, INK), 420, 1140, 0),
    (16.2, "title", ("FACE PRETA? QUEM ESCOLHE É O DA DIREITA!", 46, PURPLE), 540, 1590, 0),
    (19.4, "title", ("TIRA UM CUBO DO SAQUINHO!", 54, TEAL), 540, 215, 2),
    (26.4, "title", ("UM POSTE EM CADA BAIRRO", 54, PINK), 540, 215, -2),
    (28.6, "tag", ("PODE EMPILHAR!", 46, YELLOW, INK), 330, 640, -6, 31.0),
    (31.0, "sfx", ("ビリビリ", 140, YELLOW), 700, 760, -10, 33.8),
    (31.2, "title", ("NÃO TOCA NO FIO!", 86, RED), 540, 1120, 3, 33.8),
    (32.0, "title", ("CHOQUE!", 120, YELLOW), 560, 1360, -5, 33.8),
    (34.3, "title", ("OS FIOS NÃO PODEM TOCAR...", 54, PURPLE), 540, 215, -2),
    (35.4, "tag", ("X  NO TABULEIRO", 46, RED, WHITE), 330, 1180, -3),
    (36.4, "tag", ("X  EM OUTRO FIO", 46, RED, WHITE), 600, 1290, 2),
    (37.4, "tag", ("X  EM OUTRO POSTE", 46, RED, WHITE), 420, 1400, -2),
    (38.4, "sfx", ("ダメ!", 150, RED), 800, 620, 12, 41.2),
    (41.4, "title", ("CUBO PRETO = GATINHO NO FIO!", 54, PINK), 540, 215, 2),
    (42.4, "sfx", ("ニャー!", 140, PINK), 780, 640, 10),
    (44.8, "sfx", ("ゴゴゴ", 110, PURPLE), 250, 1250, -6),
    (45.2, "tag", ("CADA GATO DEIXA MAIS BAMBO!", 40, WHITE, INK), 600, 1420, 2),
    (48.4, "title", ("COMPETITIVO: QUEM DERRUBA PERDE!", 54, RED), 540, 215, -2, 51.7),
    (49.0, "sfx", ("ガーン!", 140, YELLOW), 760, 700, 8, 51.7),
    (51.8, "title", ("COOPERATIVO: O MAIS ALTO JUNTOS!", 54, TEAL), 540, 215, 2, 54.3),
    (52.2, "sfx", ("キラキラ", 110, YELLOW), 300, 640, -8, 54.3),
    (56.6, "title", ("COMENTA AQUI!", 90, PINK), 540, 1580, -3),
    (57.6, "logo", (460,), 540, 300, -2),
    (58.4, "title", ("ALUGUE O NEKOJIMA!", 78, PINK), 540, 590, -2),
    (59.4, "tag", ("1 A 5 JOGADORES", 40, YELLOW, INK), 790, 1000, 4),
    (59.8, "tag", ("PARTIDAS RÁPIDAS", 40, WHITE, INK), 790, 1120, -3),
    (60.2, "tag", ("5 DIAS DE JOGO", 40, TEAL, INK), 790, 1240, 3),
    (61.0, "tag", ("RESERVE ONLINE · RETIRE EM MAUÁ E ABC", 34, WHITE, INK), 540, 1430, 0),
    (61.8, "title", ("LINK NA BIO · @SUAVEZ_BG", 46, PINK), 540, 1570, 0),
]


def draw_elements(img, t, i):
    a, b = SCENES[i]
    for k, e in enumerate(ELS):
        t0, kind, args, x, y, rot = e[:6]
        t1 = e[6] if len(e) > 6 else b
        if not (a <= t0 < b) or t < t0 or t >= t1:
            continue
        u = seg(t, t0, t0 + 0.25)
        sc = max(0.05, out_back(u)) if u < 1 else 1.0
        if kind == "sfx":
            dx, dy = jit(t, 6, k)
            sc = lerp(1.8, 1.0, ease(u)) if u < 1 else 1.0 + 0.04 * math.sin((t - t0) * 18)
            paste_c(img, sfx_img(*args), x + dx, y + dy, rot, sc, min(1, u * 2))
        elif kind == "title":
            paste_c(img, title_img(*args), x, y, rot, sc)
        elif kind == "tag":
            paste_c(img, tag_img(*args), x, y, rot, sc)
        elif kind == "logo":
            paste_c(img, logo_card(*args), x, y, rot, sc)


# ---------------------------------------------------------------- efeitos
def petals(img, t, n=26, seed=1):
    d = ImageDraw.Draw(img, "RGBA")
    rng = np.random.default_rng(seed)
    for k in range(n):
        x0, sp, ph, sz = rng.uniform(-100, W + 100), rng.uniform(90, 200), rng.uniform(0, 10), rng.uniform(14, 26)
        y = (rng.uniform(0, H) + t * sp) % (H + 200) - 100
        x = x0 + 60 * math.sin(t * 1.3 + ph) - t * 25 % W
        a = t * 2 + ph
        rx, ry = sz, sz * (0.45 + 0.35 * abs(math.sin(a)))
        pts = [(x + math.cos(a) * rx * math.cos(q) - math.sin(a) * ry * math.sin(q),
                y + math.sin(a) * rx * math.cos(q) + math.cos(a) * ry * math.sin(q)) for q in np.linspace(0, 6.28, 10)]
        d.polygon(pts, fill=SAKURA + (220,))


def sparkle(img, x, y, r, col=WHITE):
    d = ImageDraw.Draw(img, "RGBA")
    d.polygon([(x, y - r), (x + r * 0.22, y - r * 0.22), (x + r, y), (x + r * 0.22, y + r * 0.22), (x, y + r),
               (x - r * 0.22, y + r * 0.22), (x - r, y), (x - r * 0.22, y - r * 0.22)], fill=col + (240,))


def sparkles(img, t, cx, cy, spread, n=7, seed=3):
    rng = np.random.default_rng(seed)
    for k in range(n):
        ph = rng.uniform(0, 6.28)
        s = max(0, math.sin(t * 5 + ph))
        sparkle(img, cx + rng.uniform(-spread, spread), cy + rng.uniform(-spread, spread), 10 + 32 * s, YELLOW if k % 2 else WHITE)


def bolt(img, t, p0, p1, seed=0):
    k = int(t * POSE)
    rng = np.random.default_rng(k * 13 + seed)
    pts = [p0]
    for s in np.linspace(0.15, 0.85, 6):
        pts.append((lerp(p0[0], p1[0], s) + rng.uniform(-50, 50), lerp(p0[1], p1[1], s) + rng.uniform(-30, 30)))
    pts.append(p1)
    d = ImageDraw.Draw(img, "RGBA")
    d.line(pts, fill=YELLOW + (255,), width=20, joint="curve")
    d.line(pts, fill=WHITE + (255,), width=8, joint="curve")


def torii(img, x, y, s, alpha=1.0):
    d = ImageDraw.Draw(img, "RGBA")
    c = RED + (int(255 * alpha),)
    k = INK + (int(255 * alpha),)
    d.polygon([(x - s * 1.1, y - s * 0.95), (x + s * 1.1, y - s * 0.95), (x + s * 0.95, y - s * 0.75),
               (x - s * 0.95, y - s * 0.75)], fill=k)
    d.rectangle((x - s * 0.85, y - s * 0.75, x + s * 0.85, y - s * 0.6), fill=c)
    d.rectangle((x - s * 0.75, y - s * 0.4, x + s * 0.75, y - s * 0.28), fill=c)
    for sx in (-1, 1):
        d.rectangle((x + sx * s * 0.6 - s * 0.09, y - s * 0.62, x + sx * s * 0.6 + s * 0.09, y + s * 0.9), fill=c)


def circle_mark(img, c, r, u, col=YELLOW):
    if u <= 0:
        return
    d = ImageDraw.Draw(img, "RGBA")
    d.arc((c[0] - r, c[1] - r, c[0] + r, c[1] + r), -90, -90 + 360 * min(1, u), fill=INK, width=16)
    d.arc((c[0] - r, c[1] - r, c[0] + r, c[1] + r), -90, -90 + 360 * min(1, u), fill=col, width=9)


def vs_screen(img, t, t0):
    u = ease(seg(t, t0, t0 + 0.4))
    d = ImageDraw.Draw(img, "RGBA")
    off = lerp(-W, 0, u)
    d.polygon([(off, 300), (off + W * 1.2, 300), (off + W * 0.2, 1500), (off, 1500)], fill=TEAL)
    d.polygon([(W - off, 300), (W - off, 1500), (W - off - W * 1.2, 1500), (W - off - W * 0.2, 300)], fill=PINK)
    for k in range(int(t * POSE) % 3, 40, 3):  # linhas de velocidade horizontais
        yy = 320 + k * 30
        d.line((0, yy, W, yy), fill=(255, 255, 255, 40), width=4)
    if u >= 1:
        paste_c(img, title_img("MÃO FIRME", 80, NAVY), 330, 620, -6)
        paste_c(img, title_img("DERRUBA TUDO", 72, RED), 560, 1180, -6)
        dx, dy = jit(t, 5, 9)
        paste_c(img, sfx_img("VS", 210, YELLOW), 540 + dx, 900 + dy, -8, 1 + 0.05 * math.sin(t * 12))


def impact(img, t, t0, dur=0.17):
    """Quadro de impacto: cores invertidas por instantes."""
    if t0 <= t < t0 + dur:
        inv = ImageOps.invert(img)
        return ImageChops.blend(inv, Image.new("RGB", img.size, WHITE), 0.15) if t < t0 + dur / 2 else inv
    return img


def frame_at(t):
    i = scene_of(t)
    img = sky(i).copy()
    k = int(t * POSE) % 4
    if i not in (1, 8):
        img.paste(speed_lines(i, k), (0, 0), speed_lines(i, k))
    else:
        petals(img, t)
    shake = 0
    name = None
    if i == 0 and t >= 2.6:
        name, shake = "caindo.jpg", 30 * (1 - seg(t, 2.6, 3.4))
    if i == 4 and 31.0 <= t < 33.8:
        shake = 8
    if i == 7 and t >= 51.7:
        name = "torre2.jpg"
    if i == 7 and t >= 54.4:
        vs_screen(img, t, 54.4)
    elif i == 8:
        petals(img, t, 18, 5)
        u = ease(seg(t, 58.9, 59.5))
        if u > 0:
            paste_c(img, box_img(440), lerp(-300, 310, u), 1130, -5)
    else:
        to_s = panel(img, i, t, name=name, shake=shake)
        if i == 1:
            petals(img, t, 18, 7)
            paste_c(img, sfx_img("猫島", 170, PINK), 790, 1230 + 6 * math.sin(t * 3), -6)
        if i == 2:
            circle_mark(img, to_s(185, 545), 95, seg(t, 13.4, 13.9))
            circle_mark(img, to_s(352, 530), 95, seg(t, 13.6, 14.1), PINK)
            sparkles(img, t, *to_s(270, 540), 160)
            if t >= 16.2:  # a face especial do dado é preta com adaga
                circle_mark(img, to_s(388, 607), 70 + 6 * math.sin(t * 10), 1.0, RED)
        if i == 3:
            circle_mark(img, to_s(760, 670), 140, seg(t, 20.0, 20.5))
            for kk, (col, lab) in enumerate(((PINK, "ROSA = FIO CURTO"), (WHITE, "BRANCO = FIO MÉDIO"),
                                             (TEAL, "AZUL = FIO LONGO"))):
                t0 = 21.8 + kk * 0.9
                if t >= t0:
                    paste_c(img, tag_img(lab, 42, col, INK), lerp(-400, 400 + kk * 60, ease(seg(t, t0, t0 + 0.3))),
                            1180 + kk * 120, -3 + kk * 2)
        if i == 4 and 31.0 <= t < 33.8:
            bolt(img, t, (260, 420), (520, 900), 1)
            bolt(img, t, (900, 380), (620, 820), 2)
        if i == 6:
            circle_mark(img, to_s(510, 480), 230, seg(t, 41.8, 42.4), PINK)
            sparkles(img, t, *to_s(510, 480), 260, 9, 5)
        if i == 7 and t >= 51.7:
            sparkles(img, t, 540, 800, 380, 12, 8)
    draw_elements(img, t, i)
    img = impact(img, t, 2.6)
    img = impact(img, t, 31.0, 0.1)
    img = impact(img, t, 48.4, 0.12)
    a, _ = SCENES[i]
    if i > 0 and a <= t < a + 0.12:  # corte seco com flash branco
        img = Image.blend(img, Image.new("RGB", img.size, WHITE), 0.8 * (1 - seg(t, a, a + 0.12)))
    return img


# ---------------------------------------------------------------- som, legendas e render
def _cues():
    c = []
    for e in ELS:
        c.append((e[0], {"sfx": "hit", "title": "swoosh", "tag": "pop", "logo": "pop"}[e[1]], 0.45))
    c += [(a, "stinger", 0.5) for a, _ in SCENES[1:]]
    c += [(k * 0.42, "beat", 0.35 + k * 0.05) for k in range(6)]
    c += [(2.6, "crash", 1.0), (13.2, "dice", 0.7), (20.0, "cube", 0.6), (27.6, "wood", 0.6), (29.0, "wood", 0.6),
          (31.0, "zap", 0.9), (32.0, "zap", 0.9), (38.4, "var", 0.5), (42.4, "meow", 0.7), (48.4, "crash", 0.7),
          (52.2, "ding", 0.5), (54.4, "hit", 0.8), (65.0, "ding", 0.4)]
    return c


CUES = _cues()


def render_frame(args):
    fi, subs = args
    t = fi / FPS
    to = to_orig(t)
    img = frame_at(to)
    if scene_of(to) < len(SCENES) - 1:
        wm = neko.watermark()
        img.paste(wm, (W - wm.width - 30, 40), wm)
    if subs:
        for a_, b_, s in neko.SUBS:
            if a_ <= t < b_:
                si = neko.sub_img(s)
                img.paste(si, ((W - si.width) // 2, 1740 - si.height // 2), si)
    return img.tobytes()


def render(out_path, wav, subs, workers=4):
    n = int(neko.DUR * FPS)
    cmd = [ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-framerate", str(FPS), "-i", "-", "-i", wav,
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-maxrate", "8M", "-bufsize", "16M",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out_path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(workers) as pool:
        for k, fr in enumerate(pool.imap(render_frame, [(j, subs) for j in range(n)], chunksize=6)):
            p.stdin.write(fr)
            if k % 300 == 0:
                print(f"  quadro {k}/{n}", flush=True)
    p.stdin.close()
    p.wait()
    print("ok:", out_path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    ap.add_argument("--only", choices=["preview", "limpo"])
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.frame:
        ims = [Image.frombytes("RGB", (W, H), render_frame((int(x * FPS), True))) for x in a.frame]
        ims[0].save(os.path.join(OUT, "frame.png"))
        sheet = Image.new("RGB", (360 * len(ims), 640))
        for k, im in enumerate(ims):
            sheet.paste(im.resize((360, 640), Image.LANCZOS), (360 * k, 0))
        sheet.save(os.path.join(OUT, "frames.jpg"), quality=90)
        return
    wav = os.path.join(OUT, "trilha_anime.wav")
    voz = [(os.path.join(ROOT, v["arquivo"]), v["inicio"]) for v in neko.TIMELINE["voz"]] if neko.TIMELINE else None
    neko.som.build(wav, neko.DUR, warp=warp, voz=voz, cues=CUES, estilo="anime")
    if a.only != "limpo":
        render(os.path.join(OUT, "anime_preview.mp4"), wav, subs=True)
    if a.only != "preview":
        render(os.path.join(OUT, "anime_limpo.mp4"), wav, subs=False)


if __name__ == "__main__":
    main()
