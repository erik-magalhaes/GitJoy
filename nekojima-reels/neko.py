#!/usr/bin/env python3
"""Reels do Nekojima – "transmissão esportiva ao vivo" do Campeonato de Mão Firme.

As fotos oficiais entram inteiras numa "câmera" quadrada (sem recortar os fios), com grafismos de TV:
AO VIVO, placar de postes/gatos, medidor de tensão, telestrador (setas e círculos), VAR e replay.

    python3 neko.py --frame 3 10 20       # quadros de teste (out/frames.jpg)
    python3 neko.py --only preview        # prévia com legendas
    python3 neko.py                       # com e sem legendas
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
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import som_neko as som  # noqa: E402

FOTOS = os.path.join(ROOT, "assets", "fotos")
FONTS = os.path.join(ROOT, "assets", "fonts")
OUT = os.path.join(ROOT, "out")
W, H = 1080, 1920
FPS = 30
DUR = 66.0
CAM_Y = 420  # janela da câmera: 1080 x 1080 de y=420 a y=1500

NAVY = (10, 20, 46)
NAVY2 = (22, 40, 86)
TEAL = (46, 196, 182)
PINK = (238, 66, 118)
YELLOW = (255, 206, 40)
WHITE = (255, 255, 255)
RED = (230, 40, 40)
GREEN = (60, 210, 90)


def seg(t, a, b):
    return min(1.0, max(0.0, (t - a) / (b - a)))


def ease(u):
    return u * u * (3 - 2 * u)


def out_back(u, s=1.7):
    u -= 1
    return u * u * ((s + 1) * u + s) + 1


def lerp(a, b, u):
    return a + (b - a) * u


def ffmpeg_exe():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


@lru_cache(None)
def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


ANTON = "Anton-Regular.ttf"
POP = "Poppins-ExtraBold.ttf"


def wrap(text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if fnt.getlength(t) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


@lru_cache(None)
def photo(name):
    im = Image.open(os.path.join(FOTOS, name)).convert("RGB")
    if im.width != 1080:
        im = im.resize((1080, int(im.height * 1080 / im.width)), Image.LANCZOS)
    return im


def cam_view(name, z, fx, fy, shake=0.0, t=0.0):
    """Recorte da foto (1080 px) com zoom z centrado em (fx, fy). Devolve a imagem e o mapa foto→tela."""
    im = photo(name)
    s = 1080 / z
    x0 = min(max(0, fx - s / 2), im.width - s)
    y0 = min(max(0, fy - s / 2), im.height - s)
    if shake:
        x0 += shake * math.sin(t * 61)
        y0 += shake * math.cos(t * 47)
        x0 = min(max(0, x0), im.width - s)
        y0 = min(max(0, y0), im.height - s)
    view = im.resize((1080, 1080), Image.BICUBIC, box=(x0, y0, x0 + s, y0 + s))

    def to_screen(px, py):
        return (px - x0) * z, CAM_Y + (py - y0) * z
    return view, to_screen


# ---------------------------------------------------------------- grafismos de TV
@lru_cache(None)
def bar_img(text, size=56, bg=NAVY, fg=WHITE, accent=TEAL, maxw=900):
    """Tarja inclinada de "lower third"."""
    f = font(ANTON, size)
    lines = wrap(text, f, maxw)
    lh = int(size * 1.15)
    tw = max(f.getlength(l) for l in lines)
    w, h = int(tw + size * 1.4), int(lh * len(lines) + size * 0.5)
    sl = int(h * 0.35)
    im = Image.new("RGBA", (w + sl + 30, h + 14), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(sl + 10, 10), (w + sl + 10, 10), (w + 10, h + 10), (10, h + 10)], fill=(0, 0, 0, 120))
    d.polygon([(sl, 0), (w + sl, 0), (w, h), (0, h)], fill=bg)
    d.polygon([(sl, 0), (sl + 22, 0), (22, h), (0, h)], fill=accent)
    for i, l in enumerate(lines):
        d.text(((w + sl) / 2 + 10, size * 0.25 + lh * i + lh / 2), l, font=f, fill=fg, anchor="mm")
    return im


@lru_cache(None)
def big_img(text, size=170, fill=YELLOW, stroke=NAVY):
    f = font(ANTON, size)
    tw = f.getlength(text)
    w, h = int(tw + 80), int(size * 1.5)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((w / 2 + 10, h / 2 + 12), text, font=f, fill=(0, 0, 0, 140), anchor="mm")
    d.text((w / 2, h / 2), text, font=f, fill=fill, anchor="mm", stroke_width=12, stroke_fill=stroke)
    return im


@lru_cache(None)
def chip_img(text, size=40, bg=YELLOW, fg=NAVY):
    f = font(POP, size)
    w, h = int(f.getlength(text)) + 60, int(size * 1.7)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), radius=12, fill=bg)
    ImageDraw.Draw(im).text((w / 2, h / 2 + 2), text, font=f, fill=fg, anchor="mm")
    return im


@lru_cache(None)
def logo_card(width):
    lg = Image.open(os.path.join(ROOT, "assets", "logo_suavez.png")).convert("RGBA")
    pad = int(lg.width * 0.06)
    card = Image.new("RGBA", (lg.width + pad * 2, lg.height + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=pad * 2,
                                           fill=(255, 255, 255, 255))
    card.alpha_composite(lg, (pad, pad))
    return card.resize((int(width), int(card.height * width / card.width)), Image.LANCZOS)


@lru_cache(None)
def box_img(width):
    """Caixa 3D (foto em fundo branco): o branco das bordas vira transparente."""
    im = Image.open(os.path.join(FOTOS, "caixa3d.png")).convert("RGB")
    a = np.asarray(im).astype(np.int16)
    import cv2
    bg = (a.min(2) > 240).astype(np.uint8)
    ff = bg.copy()
    mask = np.zeros((ff.shape[0] + 2, ff.shape[1] + 2), np.uint8)
    for sx, sy in [(0, 0), (ff.shape[1] - 1, 0), (0, ff.shape[0] - 1), (ff.shape[1] - 1, ff.shape[0] - 1)]:
        if ff[sy, sx]:
            cv2.floodFill(ff, mask, (sx, sy), 2)
    alpha = np.where(ff == 2, 0, 255).astype(np.uint8)
    alpha = cv2.GaussianBlur(cv2.erode(alpha, np.ones((3, 3), np.uint8)), (3, 3), 0)
    rgba = Image.fromarray(np.dstack([a.astype(np.uint8), alpha]), "RGBA")
    rgba = rgba.crop(rgba.getbbox())
    return rgba.resize((int(width), int(rgba.height * width / rgba.width)), Image.LANCZOS)


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


# elementos: (t0, tipo, args, x, y, rot[, t1]) — "bar" entra deslizando da esquerda, "big" bate na tela
ELS = [
    (2.7, "big", ("CAIU!!!", 210, YELLOW), 540, 960, -6, 5.4),
    (3.4, "bar", ("A CULPA É SUA?", 64, PINK, WHITE, YELLOW), 540, 1560, 0),
    (5.8, "bar", ("NEKOJIMA · A ILHA DOS GATOS", 56), 540, 1560, 0, 9.0),
    (9.1, "bar", ("MISSÃO: MONTAR A REDE ELÉTRICA", 56, NAVY, WHITE, PINK), 540, 1560, 0),
    (6.6, "chip", ("1 A 5 JOGADORES", 38), 830, 1430, 0),
    (12.3, "bar", ("LANCE 1: ROLA OS DOIS DADOS", 56), 540, 1560, 0),
    (13.6, "chip", ("= BAIRROS DOS POSTES", 36, TEAL, NAVY), 330, 1180, 0),
    (16.0, "bar", ("TORII PRETO? QUEM ESCOLHE É O DA DIREITA", 46, NAVY, WHITE, YELLOW), 540, 1560, 0),
    (19.3, "bar", ("LANCE 2: TIRA UM CUBO DO SAQUINHO", 52), 540, 1560, 0),
    (26.3, "bar", ("LANCE 3: UM POSTE EM CADA BAIRRO", 52), 540, 1560, 0),
    (28.6, "chip", ("PODE EMPILHAR!", 40), 300, 640, -4),
    (31.0, "big", ("NÃO TOCA NO FIO!", 120, YELLOW, RED), 540, 1000, -4, 33.6),
    (32.0, "big", ("CHOQUE!", 170, WHITE, RED), 560, 1220, 6, 33.6),
    (34.2, "bar", ("VAR: O FIO ENCOSTOU?", 60, RED, WHITE, YELLOW), 540, 1560, 0),
    (35.4, "chip", ("X  NO TABULEIRO", 40, RED, WHITE), 300, 560, 0),
    (36.4, "chip", ("X  EM OUTRO FIO", 40, RED, WHITE), 300, 650, 0),
    (37.4, "chip", ("X  EM OUTRO POSTE", 40, RED, WHITE), 300, 740, 0),
    (41.3, "bar", ("CUBO PRETO = GATINHO NO FIO", 58, NAVY, WHITE, PINK), 540, 1560, 0),
    (43.5, "big", ("MIAU!", 150, PINK, NAVY), 820, 700, 8, 46.0),
    (45.0, "chip", ("CADA GATO DEIXA MAIS BAMBO", 38), 540, 1420, 0),
    (48.3, "bar", ("COMPETITIVO: QUEM DERRUBA PERDE", 54, RED, WHITE, YELLOW), 540, 1560, 0, 51.7),
    (51.8, "bar", ("COOPERATIVO: O MAIS ALTO POSSÍVEL", 54, TEAL, NAVY, WHITE), 540, 1560, 0, 54.4),
    (54.5, "bar", ("COMENTA AQUI!", 70, YELLOW, NAVY, PINK), 540, 1560, 0),
    (57.4, "logo", (480,), 540, 560, 0),
    (58.2, "bar", ("ALUGUE O NEKOJIMA!", 70, PINK, WHITE, YELLOW), 540, 860, 0),
    (59.2, "chip", ("1 A 5 JOGADORES", 40), 790, 1060, 0),
    (59.6, "chip", ("PARTIDAS RÁPIDAS", 40), 790, 1160, 0),
    (60.0, "chip", ("5 DIAS DE JOGO", 40, TEAL, NAVY), 790, 1260, 0),
    (61.0, "bar", ("RESERVE ONLINE · RETIRE EM MAUÁ E ABC", 40), 540, 1420, 0),
    (61.8, "bar", ("LINK NA BIO · @SUAVEZ_BG", 60, YELLOW, NAVY, PINK), 540, 1560, 0),
]

SCENES = [(0.0, 5.6), (5.6, 12.2), (12.2, 19.2), (19.2, 26.2), (26.2, 34.0), (34.0, 41.2), (41.2, 48.2),
          (48.2, 57.2), (57.2, 66.0)]
TR = 0.35  # vinheta entre cenas

# câmera de cada cena: foto, (zoom inicial, zoom final), foco (x, y) inicial e final
CAMS = [
    ("torre2.jpg", (1.0, 1.25), (540, 470), (560, 420)),
    ("capa_arte.jpg", (1.0, 1.08), (540, 540), (540, 600)),
    ("dados.jpg", (1.0, 1.5), (540, 540), (330, 560)),
    ("loja2.jpg", (1.0, 1.7), (540, 540), (700, 640)),
    ("torre.jpg", (1.05, 1.35), (450, 420), (450, 400)),
    ("torre2.jpg", (1.4, 1.6), (650, 420), (680, 460)),
    ("gato_fio.jpg", (1.0, 1.25), (540, 540), (520, 470)),
    ("caiu.jpg", (1.0, 1.15), (540, 540), (560, 560)),
    ("capa_arte.jpg", (1.0, 1.0), (540, 540), (540, 540)),
]


def scene_of(t):
    for i, (a, b) in enumerate(SCENES):
        if a <= t < b:
            return i
    return len(SCENES) - 1


# medidor de tensão (0..1) e placar ao longo do vídeo
TENSAO = [(0, 0.2), (2.4, 0.95), (2.7, 1.0), (5.6, 0.1), (12, 0.15), (26, 0.3), (31, 0.7), (34, 0.5), (41, 0.55),
          (44, 0.8), (48, 0.9), (49.2, 1.0), (51.8, 0.4), (57, 0.2), (66, 0.2)]
POSTES = [(0, 0), (12.2, 0), (27.6, 2), (29.0, 4), (41, 6), (48, 9)]
GATOS = [(0, 0), (43.3, 1), (44.6, 2)]


def interp(keys, t):
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if a <= t <= b:
            return lerp(va, vb, ease(seg(t, a, b)))
    return keys[-1][1]


def step(keys, t):
    v = keys[0][1]
    for a, va in keys:
        if t >= a:
            v = va
    return v


@lru_cache(None)
def background():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    base = np.array(NAVY, np.float32) + (np.array(NAVY2, np.float32) - np.array(NAVY, np.float32)) * \
        (1 - np.abs(y / H - 0.45) * 1.6).clip(0, 1)[..., None]
    img = Image.fromarray(base.clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img, "RGBA")
    for k in range(-H, W, 60):  # listras diagonais de fundo de estúdio
        d.line((k, H, k + H, 0), fill=(255, 255, 255, 12), width=18)
    return img.convert("RGB")


def header(img, t):
    d = ImageDraw.Draw(img, "RGBA")
    # faixa do campeonato
    d.polygon([(0, 150), (900, 150), (860, 250), (0, 250)], fill=PINK)
    d.polygon([(0, 150), (40, 150), (0, 250)], fill=YELLOW)
    d.text((60, 200), "CAMPEONATO DE MÃO FIRME", font=font(ANTON, 62), fill=WHITE, anchor="lm")
    # AO VIVO + relógio
    d.rounded_rectangle((40, 60, 270, 120), radius=10, fill=RED)
    if int(t * 2) % 2 == 0:
        d.ellipse((58, 78, 82, 102), fill=WHITE)
    d.text((170, 91), "AO VIVO", font=font(ANTON, 40), fill=WHITE, anchor="mm")
    d.rounded_rectangle((285, 60, 430, 120), radius=10, fill=(0, 0, 0, 150))
    d.text((357, 91), f"{int(t // 60):02d}:{int(t % 60):02d}", font=font(ANTON, 40), fill=WHITE, anchor="mm")
    # placar
    f = font(ANTON, 40)
    d.rectangle((0, 270, 1080, 400), fill=(0, 0, 0, 120))
    po, ga = int(step(POSTES, t)), int(step(GATOS, t))
    for x, lab, val, col in ((40, "POSTES", f"{po:02d}/21", TEAL), (330, "GATOS", f"{ga}/7", PINK)):
        d.text((x, 300), lab, font=font(POP, 26), fill=(200, 210, 230), anchor="lm")
        d.text((x, 355), val, font=font(ANTON, 54), fill=col, anchor="lm")
    # tensão: barra horizontal + batimento
    ten = interp(TENSAO, t)
    d.text((600, 300), "TENSÃO", font=font(POP, 26), fill=(200, 210, 230), anchor="lm")
    x0, x1 = 600, 1040
    n = 14
    for k in range(n):
        u = k / (n - 1)
        col = GREEN if u < 0.5 else YELLOW if u < 0.8 else RED
        on = u <= ten + 1e-3
        xa = x0 + k * (x1 - x0) / n
        d.rectangle((xa, 335, xa + (x1 - x0) / n - 6, 380), fill=col + ((255,) if on else (50,)))
    if ten > 0.85 and int(t * 6) % 2 == 0:
        d.rectangle((x0 - 6, 330, x1 + 2, 385), outline=RED, width=4)


def cam_frame(img, t, i):
    name, (z0, z1), f0, f1 = CAMS[i]
    a, b = SCENES[i]
    u = seg(t, a, b)
    z = lerp(z0, z1, ease(u))
    fx, fy = lerp(f0[0], f1[0], ease(u)), lerp(f0[1], f1[1], ease(u))
    shake = 0
    if i == 0 and t >= 2.6:  # o gancho corta para a torre caindo
        name, z, fx, fy = "caindo.jpg", lerp(1.0, 1.12, seg(t, 2.6, 5.6)), 560, 460
        shake = 22 * (1 - seg(t, 2.6, 3.4))
    view, to_s = cam_view(name, z, fx, fy, shake, t)
    if i == 7 and t >= 52.0:  # replay: torre alta no cooperativo
        view, to_s = cam_view("torre2.jpg", lerp(1.0, 1.1, seg(t, 52, 57.2)), 540, 480)
    if i == 8:
        view = view.filter(ImageFilter.GaussianBlur(10))
        view = Image.blend(view, Image.new("RGB", view.size, NAVY), 0.45)
    img.paste(view, (0, CAM_Y))
    return to_s


def cam_border(img, t, label):
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((0, CAM_Y - 6, 1080, CAM_Y), fill=TEAL)
    d.rectangle((0, CAM_Y + 1080, 1080, CAM_Y + 1086), fill=TEAL)
    # cantos de visor
    for (x, y, sx, sy) in ((30, CAM_Y + 30, 1, 1), (1050, CAM_Y + 30, -1, 1), (30, CAM_Y + 1050, 1, -1),
                           (1050, CAM_Y + 1050, -1, -1)):
        d.line((x, y, x + 60 * sx, y), fill=WHITE + (200,), width=5)
        d.line((x, y, x, y + 60 * sy), fill=WHITE + (200,), width=5)
    if label:
        d.rounded_rectangle((60, CAM_Y + 50, 60 + 30 + font(ANTON, 34).getlength(label), CAM_Y + 104), radius=8,
                            fill=(0, 0, 0, 150))
        d.text((75, CAM_Y + 77), label, font=font(ANTON, 34), fill=WHITE, anchor="lm")


def tele_circle(img, c, r, u, color=YELLOW, width=9):
    if u <= 0:
        return
    d = ImageDraw.Draw(img, "RGBA")
    d.arc((c[0] - r, c[1] - r * 0.85, c[0] + r, c[1] + r * 0.85), -100, -100 + 360 * min(1, u), fill=color,
          width=width)


def tele_arrow(img, p0, p1, u, color=YELLOW, width=9):
    if u <= 0:
        return
    d = ImageDraw.Draw(img, "RGBA")
    x = lerp(p0[0], p1[0], min(1, u))
    y = lerp(p0[1], p1[1], min(1, u))
    d.line((p0[0], p0[1], x, y), fill=color, width=width)
    if u >= 1:
        ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        for da in (2.6, -2.6):
            d.line((x, y, x + 40 * math.cos(ang + da), y + 40 * math.sin(ang + da)), fill=color, width=width)


def sparks(img, t, t0, c, n=12):
    u = (t - t0) / 0.6
    if not 0 <= u < 1:
        return
    d = ImageDraw.Draw(img, "RGBA")
    rng = np.random.default_rng(int(t * FPS))
    for k in range(n):
        a = rng.uniform(0, 2 * math.pi)
        r0, r1 = 20 + 120 * u, 60 + 200 * u
        d.line((c[0] + math.cos(a) * r0, c[1] + math.sin(a) * r0, c[0] + math.cos(a) * r1,
                c[1] + math.sin(a) * r1), fill=(255, 240, 120, int(255 * (1 - u))), width=6)


LABELS = ["CÂM 1 · AO VIVO", "CÂM 2 · ABERTURA", "CÂM 3 · DADOS", "CÂM 1 · O SAQUINHO", "CÂM 2 · A TORRE",
          "VAR · REVISÃO", "CÂM 3 · CLOSE", "REPLAY", ""]


def overlays(img, t, i, to_s):
    d = ImageDraw.Draw(img, "RGBA")
    if i == 2:  # dados
        tele_circle(img, to_s(185, 545), 80, seg(t, 13.2, 13.7))
        tele_circle(img, to_s(352, 530), 80, seg(t, 13.5, 14.0))
    if i == 3:  # saquinho, cubos e cores dos fios
        tele_circle(img, to_s(760, 670), 120, seg(t, 20.0, 20.5))
        for k, (col, lab) in enumerate(((PINK, "ROSA = FIO CURTO"), (WHITE, "BRANCO = FIO MÉDIO"),
                                        (TEAL, "AZUL = FIO LONGO"))):
            t0 = 21.8 + k * 0.9
            if t >= t0:
                u = ease(seg(t, t0, t0 + 0.3))
                x = lerp(-500, 40, u)
                y = 560 + k * 92
                d.rounded_rectangle((x, y, x + 520, y + 74), radius=12, fill=(10, 20, 46, 220))
                d.rectangle((x + 14, y + 22, x + 110, y + 52), fill=col)
                d.text((x + 130, y + 37), lab, font=font(ANTON, 42), fill=WHITE, anchor="lm")
    if i == 4:  # postes e fios
        tele_arrow(img, (230, 760), (430, 620), seg(t, 28.2, 28.7))
        if t >= 31.0:
            p = to_s(470, 300)
            sparks(img, t, 31.0, p)
            sparks(img, t, 32.0, to_s(560, 520))
    if i == 5:  # VAR: linhas de checagem
        dim = Image.new("RGBA", (1080, 1080), (0, 30, 60, 70))
        img.paste(dim, (0, CAM_Y), dim)
        if t >= 34.6:
            yy = CAM_Y + (int((t - 34.6) * 900) % 1080)
            d.line((0, yy, 1080, yy), fill=(120, 255, 180, 160), width=4)
        for k, t0 in enumerate((35.4, 36.4, 37.4)):
            u = seg(t, t0, t0 + 0.3)
            if u > 0:
                c = [(760, 1300), (820, 920), (600, 720)][k]
                d.line((c[0] - 50 * u, c[1] - 50 * u, c[0] + 50 * u, c[1] + 50 * u), fill=RED, width=12)
                d.line((c[0] - 50 * u, c[1] + 50 * u, c[0] + 50 * u, c[1] - 50 * u), fill=RED, width=12)
        if t >= 39.2:
            paste_c(img, chip_img("REVISÃO: LANCE VÁLIDO!", 44, GREEN, NAVY), 540, 1380, 0, 1.0)
    if i == 6:  # gatinho
        tele_circle(img, to_s(510, 480), 210, seg(t, 41.8, 42.4), PINK)
    if i == 7:  # replay
        if t < 52.0:
            for yy in range(CAM_Y, CAM_Y + 1080, 6):
                d.line((0, yy, 1080, yy), fill=(0, 0, 0, 40), width=2)
            if int(t * 2) % 2 == 0:
                d.text((960, CAM_Y + 80), "<< REPLAY", font=font(POP, 34), fill=WHITE, anchor="rm")
        else:  # enquete
            u = ease(seg(t, 54.6, 55.4))
            for k, (lab, col, val) in enumerate((("MÃO FIRME", TEAL, 0.52), ("DERRUBA TUDO", PINK, 0.48))):
                y = 1180 + k * 120
                d.rounded_rectangle((60, y, 1020, y + 96), radius=16, fill=(10, 20, 46, 230))
                d.rounded_rectangle((60, y, 60 + 960 * val * u, y + 96), radius=16, fill=col + (255,))
                d.text((90, y + 48), lab, font=font(ANTON, 50), fill=WHITE, anchor="lm")
                d.text((990, y + 48), "?", font=font(ANTON, 54), fill=WHITE, anchor="rm")
    if i == 8:
        u = ease(seg(t, 58.6, 59.2))
        if u > 0:
            paste_c(img, box_img(420), lerp(-300, 300, u), 1150, -4)


def draw_elements(img, t, i):
    a, b = SCENES[i]
    for e in ELS:
        t0, kind, args, x, y, rot = e[:6]
        t1 = e[6] if len(e) > 6 else b
        if not (a <= t0 < b) or t < t0 or t >= t1:
            continue
        if kind == "bar":
            u = ease(seg(t, t0, t0 + 0.28))
            im = bar_img(*args)
            paste_c(img, im, lerp(-im.width, x, u), y, rot)
        elif kind == "big":
            u = seg(t, t0, t0 + 0.18)
            im = big_img(*args)
            paste_c(img, im, x, y, rot, lerp(2.0, 1.0, ease(u)) if u < 1 else 1 + 0.02 * math.sin((t - t0) * 20),
                    min(1, u * 2))
        elif kind == "chip":
            u = seg(t, t0, t0 + 0.3)
            paste_c(img, chip_img(*args), x, y, rot, max(0.05, out_back(u)) if u < 1 else 1.0)
        elif kind == "logo":
            u = seg(t, t0, t0 + 0.35)
            paste_c(img, logo_card(*args), x, y, rot, max(0.05, out_back(u)) if u < 1 else 1.0)


def stinger(img, u):
    """Vinheta: faixas diagonais nas cores do jogo cruzando a tela."""
    d = ImageDraw.Draw(img)
    off = lerp(-2400, 1600, u)
    for k, col in enumerate((TEAL, PINK, YELLOW, NAVY)):
        x = off + k * 180
        d.polygon([(x, 0), (x + 700, 0), (x + 700 - 900, H), (x - 900, H)], fill=col)


def frame_at(t):
    i = scene_of(t)
    img = background().copy()
    to_s = cam_frame(img, t, i)
    overlays(img, t, i, to_s)
    cam_border(img, t, LABELS[i])
    header(img, t)
    draw_elements(img, t, i)
    a, _ = SCENES[i]
    if i > 0 and a - TR / 2 <= t < a + TR / 2:
        stinger(img, (t - (a - TR / 2)) / TR)
    if i > 0 and SCENES[i][1] - TR / 2 <= t < SCENES[i][1] and i < len(SCENES) - 1:
        stinger(img, (t - (SCENES[i][1] - TR / 2)) / TR)
    if i == 0 and 2.6 <= t < 2.75:  # flash do corte
        img = Image.blend(img, Image.new("RGB", img.size, WHITE), 0.7 * (1 - seg(t, 2.6, 2.75)))
    return img


# ---------------------------------------------------------------- roteiro, narração e legendas
ROTEIRO = [
    "Essa torre vai cair... e a culpa vai ser sua!",
    "Esse é o Nekojima: uma ilha de gatos no Japão onde vocês precisam montar a rede elétrica.",
    "Na sua vez, você rola os dois dados: eles dizem em quais bairros da ilha vão os seus postes.",
    "Depois tira um cubo do saquinho: a cor diz qual poste você pega, e cada cor tem um fio de tamanho diferente.",
    "Aí coloca um poste em cada bairro, pode até empilhar em cima dos outros... mas não pode encostar a mão nos fios!",
    "E tem mais: os fios não podem tocar no tabuleiro, em outro fio nem em outro poste.",
    "Saiu cubo preto? Tem gatinho pra pendurar no fio... e cada gato deixa tudo mais bambo.",
    "No competitivo, quem derrubar a torre perde. No cooperativo, vocês tentam chegar o mais alto juntos. "
    "E aí, você é mão firme ou derruba tudo? Comenta aqui!",
    "De 1 a 5 jogadores, em partidas rápidas: aluga o Nekojima na Sua Vez, o link tá na bio!",
]


def default_subs():
    out = []
    for (a, b), txt in zip(SCENES, ROTEIRO):
        chunks, cur = [], []
        for w in txt.split():
            cur.append(w)
            if len(" ".join(cur)) > 34 or w[-1] in ".?!:":
                chunks.append(" ".join(cur))
                cur = []
        if cur:
            chunks.append(" ".join(cur))
        span = (b - a - 0.5) / len(chunks)
        for k, ch in enumerate(chunks):
            out.append((a + 0.3 + k * span, a + 0.3 + (k + 1) * span, ch))
    return out


SUBS = default_subs()
TIMELINE_PATH = os.path.join(ROOT, "narracao", "timeline.json")
TIMELINE = None
if os.path.exists(TIMELINE_PATH):
    TIMELINE = json.load(open(TIMELINE_PATH, encoding="utf-8"))
    DUR = TIMELINE["duracao"]
    SUBS = [tuple(x) for x in TIMELINE["legendas"]]


def to_orig(t):
    if TIMELINE is None:
        return t
    for o0, o1, n0, n1 in TIMELINE["cenas"]:
        if n0 <= t < n1:
            return o0 + (t - n0) * (o1 - o0) / (n1 - n0)
    o0, o1, n0, n1 = TIMELINE["cenas"][-1]
    return o0 + (t - n0) * (o1 - o0) / (n1 - n0)


def warp(t_orig):
    if TIMELINE is None:
        return t_orig
    for o0, o1, n0, n1 in TIMELINE["cenas"]:
        if o0 <= t_orig < o1:
            return n0 + (t_orig - o0) * (n1 - n0) / (o1 - o0)
    return t_orig


def _cues():
    c = []
    for e in ELS:
        c.append((e[0], {"bar": "swoosh", "big": "hit", "chip": "pop", "logo": "pop"}[e[1]], 0.5))
    c += [(a - TR / 2, "stinger", 0.6) for a, _ in SCENES[1:]]
    c += [(k * 0.42, "beat", 0.35 + k * 0.05) for k in range(6)]  # batimento acelerando
    c += [(2.6, "crash", 1.0), (2.8, "crowd", 0.8), (0.0, "whistle", 0.0)]
    c += [(13.2, "dice", 0.7), (20.0, "cube", 0.6), (27.6, "wood", 0.6), (29.0, "wood", 0.6),
          (31.0, "zap", 0.8), (32.0, "zap", 0.9), (34.2, "var", 0.7), (39.2, "ding", 0.5),
          (42.0, "meow", 0.6), (43.5, "meow", 0.5), (48.3, "crash", 0.7), (48.6, "crowd", 0.6),
          (52.0, "whistle", 0.6), (54.6, "pop", 0.4), (65.0, "crowd", 0.5)]
    return c


CUES = _cues()


@lru_cache(None)
def sub_img(text):
    f = font(POP, 48)
    lines = wrap(text, f, 920)
    lh = 60
    w = int(max(f.getlength(l) for l in lines)) + 50
    h = lh * len(lines) + 24
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=18, fill=(0, 0, 0, 200))
    for k, l in enumerate(lines):
        d.text((w / 2, 12 + lh * k + lh / 2), l, font=f, fill=WHITE, anchor="mm")
    return im


@lru_cache(None)
def watermark():
    lg = logo_card(170).copy()
    lg.putalpha(lg.getchannel("A").point(lambda v: int(v * 0.95)))
    return lg


def render_frame(args):
    fi, subs = args
    t = fi / FPS
    to = to_orig(t)
    img = frame_at(to)
    if scene_of(to) < len(SCENES) - 1:
        wm = watermark()
        img.paste(wm, (W - wm.width - 30, 40), wm)
    if subs:
        for a_, b_, s in SUBS:
            if a_ <= t < b_:
                si = sub_img(s)
                img.paste(si, ((W - si.width) // 2, 1740 - si.height // 2), si)
    return img.tobytes()


def render(out_path, wav, subs, workers=4):
    n = int(DUR * FPS)
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
    wav = os.path.join(OUT, "trilha.wav")
    voz = [(os.path.join(ROOT, v["arquivo"]), v["inicio"]) for v in TIMELINE["voz"]] if TIMELINE else None
    som.build(wav, DUR, warp=warp, voz=voz, cues=CUES)
    with open(os.path.join(ROOT, "legendas.srt"), "w", encoding="utf-8") as f:
        for k, (a_, b_, s) in enumerate(SUBS, 1):
            ts = lambda x: f"{int(x // 3600):02}:{int(x // 60 % 60):02}:{int(x % 60):02},{int(round(x * 1000)) % 1000:03}"
            f.write(f"{k}\n{ts(a_)} --> {ts(b_)}\n{s}\n\n")
    if a.only != "limpo":
        render(os.path.join(OUT, "neko_preview.mp4"), wav, subs=True)
    if a.only != "preview":
        render(os.path.join(OUT, "neko_limpo.mp4"), wav, subs=False)


if __name__ == "__main__":
    main()
