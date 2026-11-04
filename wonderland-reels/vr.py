#!/usr/bin/env python3
"""Wonderland's War — "E SE VOCÊ ENTRASSE DENTRO DO JOGO?" (ideia dele, 4/nov): visão em PRIMEIRA PESSOA de quem
pôs óculos de realidade virtual. Sem narração; tudo escrito no HUD dos óculos.

Material OFICIAL da Galápagos (assets/orig, fora do git): o tabuleiro montado retificado + Real-ESRGAN (pov.camera, sempre
com a câmera ALTA: de perto a foto vira borrão), o gato da capa, as artes da Torre Vermelha e da Morsa (verso da caixa)
e a caixa 3D. Termos da caixa BR: Festa do Chá, Bolsa, Aliados, Apoiadores, Fragmentos de Loucura, Floresta Tulgea.

Regras (manual): Festa do Chá = anda até uma cadeira livre e pega a carta; com 4 cartas vai para uma região; Guerra =
todos puxam fichas da bolsa; Loucura faz perder apoiadores; para quando quiser (mão vazia); mais força vence a região
(prêmio + castelo); 3 rodadas, mais pontos vence.

    python3 vr.py --frame 1 8 14 20 26 29 35 39 43 47
    python3 vr.py            → out/wonderland_{com_som,para_musica}_final.mp4
"""
import argparse
import math
import os
import random
import sys
from functools import lru_cache

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
for p in ("comum", "listas-reels", "becas-reels"):
    sys.path.insert(0, os.path.join(REPO, p))
from motor import W, H, FPS, encode, folha, logo_card, sombra, cola  # noqa: E402
from base import final_loudness  # noqa: E402
import sons as S  # noqa: E402
import pov  # noqa: E402

OUT = os.path.join(ROOT, "out")
ART = os.path.join(ROOT, "assets", "artes")
F_HUD = os.path.join(REPO, "comum", "fontes", "SpaceGrotesk.ttf")
F_VT = os.path.join(REPO, "comum", "fontes", "VT323-Regular.ttf")
F_CIN = os.path.join(REPO, "halloween-reels", "assets", "fonts", "Cinzel.ttf")
CIANO = (150, 255, 235)
OURO = (247, 205, 96)
ROXO = (150, 70, 200)
VERM = (240, 60, 70)

# ---------------------------------------------------------------- linha do tempo
T_DIVE, T_DESCE, T_CHA, T_REGIAO, T_GUERRA, T_FIM, T_SAI, T_OLHO, T_COM, T_CTA, DUR = (
    3.0, 6.0, 11.0, 18.0, 23.0, 33.0, 36.5, 38.6, 42.5, 46.0, 51.0)
FLORESTA = (430, 1560)          # centro da Floresta Tulgea no tabuleiro_x4
MESA = (1280, 1650)            # meio da mesa da Festa do Chá


def ease(x):
    x = min(1, max(0, x))
    return x * x * (3 - 2 * x)


def lerp(a, b, u):
    return a + (b - a) * u


@lru_cache(None)
def fnt(path, size, peso=None):
    f = ImageFont.truetype(path, size)
    if peso is not None:
        try:
            f.set_variation_by_axes([peso])
        except Exception:
            pass
    return f


def hud_font(size, peso=600):
    return fnt(F_HUD, size, peso)


def cin(size, peso=800):
    return fnt(F_CIN, size, peso)


def texto(img, s, f, xy, cor, anchor="mm", stroke=0, scor=(0, 0, 0), alpha=1.0, brilho=0):
    if alpha <= 0.01:
        return
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    if brilho:
        g = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(g).multiline_text(xy, s, font=f, fill=cor + (255,), anchor=anchor, align="center",
                                         stroke_width=stroke + 4, stroke_fill=cor + (255,), spacing=10)
        g = g.filter(ImageFilter.GaussianBlur(brilho))
        lay.alpha_composite(g)
    d.multiline_text(xy, s, font=f, fill=cor + (255,), anchor=anchor, align="center", stroke_width=stroke,
                     stroke_fill=scor + (255,), spacing=10)
    if alpha < 1:
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * alpha)))
    img.alpha_composite(lay)


def digita(s, t, cps=28):
    n = int(max(0, t) * cps)
    return s[:n]


@lru_cache(None)
def arte(n, alt):
    im = Image.open(os.path.join(ART, n + ".png")).convert("RGBA")
    if n == "torre":
        im = im.crop((0, 0, im.width, int(im.height * 0.84)))
    if n == "morsa":
        im = im.crop((0, 0, im.width, int(im.height * 0.66)))
    im = im.resize((int(im.width * alt / im.height), alt), Image.LANCZOS)
    if n == "gato":
        m = Image.new("L", im.size, 0)
        b = int(im.width * 0.08)
        ImageDraw.Draw(m).rounded_rectangle((b, b, im.width - b, im.height - b), b, fill=255)
        im.putalpha(m.filter(ImageFilter.GaussianBlur(b * 0.8)))
    return im


@lru_cache(None)
def carta(n, alt=420):
    """Arte oficial dentro de uma moldura de carta dourada (a moldura é do HUD, não peça do jogo)."""
    a = arte(n, alt - 60)
    w = a.width + 60
    c = Image.new("RGBA", (w, alt), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((0, 0, w - 1, alt - 1), 26, fill=(30, 12, 44, 255), outline=OURO + (255,), width=8)
    m = Image.new("L", a.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, a.width - 1, a.height - 1), 16, fill=255)
    c.paste(a, (30, 30), m)
    return c


@lru_cache(None)
def ficha(n, r=115):
    """Ficha da bolsa: a arte do aliado num círculo (como as fichas do jogo)."""
    a = arte(n, 2 * r)
    a = a.crop(((a.width - 2 * r) // 2, 0, (a.width - 2 * r) // 2 + 2 * r, 2 * r)) if a.width > 2 * r else a
    c = Image.new("RGBA", (2 * r + 24, 2 * r + 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.ellipse((0, 0, 2 * r + 23, 2 * r + 23), fill=(235, 225, 210, 255))
    m = Image.new("L", a.size, 0)
    ImageDraw.Draw(m).ellipse((0, 0, a.width - 1, a.height - 1), fill=255)
    c.paste(a, (12, 12), m)
    d.ellipse((6, 6, 2 * r + 17, 2 * r + 17), outline=OURO + (255,), width=6)
    return c


@lru_cache(None)
def ficha_loucura(r=115):
    c = Image.new("RGBA", (2 * r + 24, 2 * r + 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.ellipse((0, 0, 2 * r + 23, 2 * r + 23), fill=(25, 8, 30, 255), outline=VERM + (255,), width=10)
    rnd = random.Random(4)
    cx = cy = r + 12
    for k in range(9):  # estilhaço
        a0 = rnd.uniform(0, math.tau)
        d.line((cx, cy, cx + r * 0.9 * math.cos(a0), cy + r * 0.9 * math.sin(a0)), fill=(200, 60, 230, 255), width=7)
    d.text((cx, cy), "?!", font=cin(130), fill=(255, 230, 255, 255), anchor="mm")
    return c


# ---------------------------------------------------------------- óculos / HUD
@lru_cache(None)
def mascara_lente(abre):
    """Lente dos óculos: 1 = toda aberta, 0 = fechada. Formato arredondado com bordas suaves."""
    m = Image.new("L", (W // 4, H // 4), 0)
    d = ImageDraw.Draw(m)
    if abre > 0.01:
        hw, hh = (W // 4 - 12) / 2 * abre ** 0.5, (H // 4 - 34) / 2 * abre
        cx, cy = W // 8, H // 8
        d.rounded_rectangle((cx - hw, cy - hh, cx + hw, cy + hh), radius=int(min(hw, hh, 46)), fill=255)
    return m.filter(ImageFilter.GaussianBlur(9)).resize((W, H), Image.BILINEAR)


def lente(img, abre=1.0):
    q = round(abre * 40) / 40
    m = mascara_lente(q)
    preto = Image.new("RGBA", (W, H), (5, 2, 10, 255))
    preto.putalpha(Image.eval(m, lambda v: 255 - v))
    img.alpha_composite(preto)


def hud(img, t, titulo=None, cor=CIANO):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    c = cor + (180,)
    for (x, y, sx, sy) in ((70, 150, 1, 1), (W - 70, 150, -1, 1), (70, 1560, 1, -1), (W - 70, 1560, -1, -1)):
        d.line((x, y, x + 70 * sx, y), fill=c, width=5)
        d.line((x, y, x, y + 70 * sy), fill=c, width=5)
    d.ellipse((W / 2 - 9, H / 2 - 9, W / 2 + 9, H / 2 + 9), outline=c, width=3)
    d.line((W / 2 - 34, H / 2, W / 2 - 16, H / 2), fill=c, width=3)
    d.line((W / 2 + 16, H / 2, W / 2 + 34, H / 2), fill=c, width=3)
    if titulo:
        d.text((100, 190), titulo, font=fnt(F_VT, 54), fill=cor + (235,))
    if int(t * 2) % 2 == 0:  # REC piscando
        d.ellipse((100, 262, 122, 284), fill=(255, 70, 80, 220))
    d.text((134, 273), "VR · AO VIVO", font=fnt(F_VT, 38), fill=cor + (200,), anchor="lm")
    img.alpha_composite(lay)


def painel(img, linhas, y, alpha=1.0, cor=CIANO, larg=900):
    """Caixa de diálogo do HUD (vidro escuro, borda neon) com 1–3 linhas."""
    if alpha <= 0.01:
        return
    f1, f2 = hud_font(54, 700), hud_font(42, 500)
    hh = 40 + 66 + 56 * (len(linhas) - 1) + 30
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x0 = (W - larg) // 2
    d.rounded_rectangle((x0, y, x0 + larg, y + hh), 26, fill=(10, 6, 24, 190), outline=cor + (220,), width=4)
    d.text((W / 2, y + 40 + 28), linhas[0], font=f1, fill=cor + (255,), anchor="mm")
    for k, s in enumerate(linhas[1:]):
        d.text((W / 2, y + 40 + 66 + 56 * k + 22), s, font=f2, fill=(240, 240, 255, 255), anchor="mm")
    if alpha < 1:
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * alpha)))
    img.alpha_composite(lay)


def glitch(img, forca, seed):
    if forca <= 0.01:
        return img
    a = np.asarray(img.convert("RGB")).copy()
    rnd = np.random.default_rng(seed)
    sh = int(18 * forca)
    a[..., 0] = np.roll(a[..., 0], sh, axis=1)
    a[..., 2] = np.roll(a[..., 2], -sh, axis=1)
    for _ in range(int(10 * forca)):
        y0 = rnd.integers(0, H - 40)
        hh = rnd.integers(8, 60)
        a[y0:y0 + hh] = np.roll(a[y0:y0 + hh], rnd.integers(-80, 80), axis=1)
    return Image.fromarray(a).convert("RGBA")


def marca(img):
    wm = logo_card(130)
    img.alpha_composite(wm, (W - wm.width - 40, 40))


# ---------------------------------------------------------------- câmera em 1ª pessoa
def balanco(t):
    """Respiração/cabeça: um balanço lento (a cabeça de quem está com os óculos)."""
    return 6 * math.sin(t * 1.3), 1.2 * math.sin(t * 0.9)


def _alvo(tx, ty, h, yaw, pitch):
    """Posição da câmera para olhar o ponto (tx,ty) do tabuleiro com esse yaw/pitch."""
    d = h / math.tan(math.radians(pitch))
    a = math.radians(yaw)
    return tx - d * math.sin(a), ty + d * math.cos(a)


# chaves: (t, alvo_x, alvo_y, altura, yaw, pitch) — a câmera fica ALTA (de perto a foto oficial borra)
CHAVES = [
    (T_DESCE, 1280, 1800, 6500, 25, 82),
    (T_CHA, 1280, 1700, 2100, 0, 50),
    (T_CHA + 6.5, 1400, 1550, 1900, -12, 53),
    (T_REGIAO + 0.3, 1400, 1550, 1900, -12, 53),
    (T_GUERRA, FLORESTA[0], FLORESTA[1], 1750, -70, 50),
    (T_FIM, FLORESTA[0], FLORESTA[1], 1650, -50, 51),
    (T_SAI, 1280, 1800, 4200, 0, 62),
]


def cam_em(t):
    """(cx, cy, h, yaw, pitch) do voo em cada momento."""
    by, bp = balanco(t)
    for (t0, *a), (t1, *b) in zip(CHAVES, CHAVES[1:]):
        if t < t1 or (t1, *b) == CHAVES[-1]:
            u = ease((t - t0) / (t1 - t0))
            if T_GUERRA <= t0 < T_FIM:  # giro lento e constante durante a guerra
                u = min(1, max(0, (t - t0) / (t1 - t0)))
            tx, ty, h, yaw, pitch = (lerp(x, y, u) for x, y in zip(a, b))
            break
    h = math.exp(lerp(math.log(a[2]), math.log(b[2]), u))
    cx, cy = _alvo(tx, ty, h, yaw, pitch)
    return cx, cy, h, yaw + by * 0.3, pitch + bp


def mundo(t):
    cx, cy, h, yaw, pitch = cam_em(t)
    rgb, cam = pov.camera(cx, cy, h, yaw, pitch, f=900)
    im = Image.fromarray(rgb).convert("RGBA")
    if T_GUERRA <= t < T_FIM:  # tom de guerra
        v = Image.new("RGBA", (W, H), (120, 0, 30, int(55 * ease((t - T_GUERRA) / 0.6))))
        im.alpha_composite(v)
    return im, cam


def alfinete(img, cam, x, y, rot, t0, t, cor=CIANO):
    """Marcador do HUD preso num ponto do tabuleiro (a casa onde foram os apoiadores)."""
    if t < t0:
        return
    p = pov.projeta(cam, x, y)
    if p is None:
        return
    sx, sy, _ = p
    k = ease((t - t0) / 0.35)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    r = 22 + 30 * (1 - k)
    d.ellipse((sx - r, sy - r * 0.45, sx + r, sy + r * 0.45), outline=cor + (230,), width=5)
    top = sy - 130 * k
    d.line((sx, sy, sx, top), fill=cor + (230,), width=4)
    if rot:
        f = hud_font(40, 700)
        tw = d.textlength(rot, font=f)
        d.rounded_rectangle((sx - tw / 2 - 18, top - 64, sx + tw / 2 + 18, top), 14, fill=(10, 6, 24, 210),
                            outline=cor + (230,), width=3)
        d.text((sx, top - 32), rot, font=f, fill=(255, 255, 255, 255), anchor="mm")
    lay.putalpha(lay.getchannel("A").point(lambda v: int(v * k)))
    img.alpha_composite(lay)


# ---------------------------------------------------------------- cenas
def cena_gancho(t):
    img = Image.new("RGBA", (W, H), (5, 2, 10, 255))
    # já mostra o gato ao fundo, desfocado, enquanto a lente "liga"
    g = arte("gato", 1500)
    g = g.filter(ImageFilter.GaussianBlur(14))
    img.alpha_composite(g, ((W - g.width) // 2, (H - g.height) // 2))
    img.alpha_composite(Image.new("RGBA", (W, H), (5, 2, 10, 150)))
    lente(img, ease(t / 0.9))
    hud(img, t, "INICIANDO REALIDADE VIRTUAL")
    texto(img, "E SE VOCÊ\nENTRASSE\nDENTRO\nDO JOGO?", cin(112), (W / 2, 900), OURO, stroke=4, scor=(30, 10, 40),
          brilho=16)
    s = digita("> carregando: WONDERLAND'S WAR...", t - 0.6, 30)
    texto(img, s, fnt(F_VT, 50), (W / 2, 1380), CIANO)
    barra = ease((t - 0.6) / 2.2)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((240, 1440, 840, 1466), 12, outline=CIANO + (200,), width=3)
    d.rounded_rectangle((246, 1446, 246 + 588 * barra, 1460), 8, fill=CIANO + (230,))
    return img


def cena_mergulho(t):
    u = (t - T_DIVE) / (T_DESCE - T_DIVE)
    img = Image.new("RGBA", (W, H), (5, 2, 10, 255))
    g = arte("gato", 1500)
    esc = 1 + 7 * ease(u) ** 2.2
    # mergulha na boca do gato (o sorriso fica a ~62% da altura da arte)
    fx, fy = 0.56, 0.60
    gw, gh = int(g.width * esc), int(g.height * esc)
    if esc > 1.01:
        crop_w, crop_h = W / esc, H / esc
        cx, cy = fx * g.width, fy * g.height
        x0 = min(max(cx - crop_w / 2, -crop_w), g.width)
        y0 = min(max(cy - crop_h / 2, -crop_h), g.height)
        bg = Image.new("RGBA", (int(crop_w) + 2, int(crop_h) + 2), (5, 2, 10, 255))
        bg.alpha_composite(g, (int(-x0), int(-y0)))
        img = bg.resize((W, H), Image.BICUBIC)
    else:
        img.alpha_composite(g, ((W - g.width) // 2, (H - g.height) // 2))
    if u > 0.5:  # borrão de velocidade radial (zoom)
        k = (u - 0.5) / 0.5
        z = img.resize((int(W * 1.06), int(H * 1.06)), Image.BILINEAR).crop((int(W * .03), int(H * .03),
                                                                               int(W * .03) + W, int(H * .03) + H))
        img = Image.blend(img, z, 0.5 * k)
    lente(img, 1)
    hud(img, t, "ATRAVESSANDO O ESPELHO")
    if u > 0.85:  # flash
        img.alpha_composite(Image.new("RGBA", (W, H), (255, 245, 255, int(255 * (u - 0.85) / 0.15))))
    return img


def inventario(img, t, n_cartas, t_ult):
    """4 casas de carta no HUD (alto à esquerda)."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.text((100, 340), "CARTAS", font=fnt(F_VT, 40), fill=CIANO + (220,))
    for k in range(4):
        x, y = 100 + k * 92, 382
        d.rounded_rectangle((x, y, x + 78, y + 108), 10, outline=CIANO + (200,), width=3,
                            fill=(OURO + (230,)) if k < n_cartas else (10, 6, 24, 120))
    img.alpha_composite(lay)


def cena_mundo(t):
    if t < T_DESCE + 0.25:
        pass
    img, cam = mundo(t)
    titulo = "RODADA 1 DE 3"
    if t < T_CHA:  # chegada
        u = (t - T_DESCE)
        texto(img, "PAÍS DAS\nMARAVILHAS", cin(118), (W / 2, 640), OURO, stroke=4, scor=(30, 10, 40), brilho=18,
              alpha=ease(u / 0.6) * (1 - ease((t - (T_CHA - 0.5)) / 0.5)))
        painel(img, ["BEM-VINDO!", "Você é um dos líderes da guerra", "pelo País das Maravilhas"], 1180,
               alpha=ease((u - 1.2) / 0.4) * (1 - ease((t - (T_CHA - 0.4)) / 0.4)))
        if u < 0.35:
            img.alpha_composite(Image.new("RGBA", (W, H), (255, 245, 255, int(255 * (1 - u / 0.35)))))
    elif t < T_REGIAO:  # Festa do Chá
        u = t - T_CHA
        titulo = "RODADA 1 · FESTA DO CHÁ"
        alfinete(img, cam, MESA[0] + 300, MESA[1] + 250, "CADEIRA LIVRE", T_CHA + 0.6, t)
        n = 2 + (t >= T_CHA + 2.6) + (t >= T_CHA + 4.6)
        inventario(img, t, n, 0)
        painel(img, ["FESTA DO CHÁ", "Ande até uma cadeira livre", "e pegue a carta que está nela"], 1180,
               alpha=ease((u - 0.3) / 0.4) * (1 - ease((u - 5.4) / 0.3)))
        for k, (n_, t0) in enumerate((("torre", T_CHA + 1.6), ("morsa", T_CHA + 3.6))):
            v = (t - t0) / 1.0
            if 0 <= v <= 1:  # carta sobe da mesa, fica um instante grande e voa pro inventário
                c = carta(n_)
                if v < 0.55:
                    w = ease(v / 0.35)
                    cola(img, sombra(c, 20, (0, 20), 0.5), W // 2, int(lerp(1150, 900, w)), lerp(-8, 0, w),
                         lerp(0.3, 1.0, w))
                    cola(img, c, W // 2, int(lerp(1150, 900, w)), lerp(-8, 0, w), lerp(0.3, 1.0, w))
                else:
                    w = ease((v - 0.55) / 0.45)
                    cola(img, c, int(lerp(W / 2, 139 + (2 + k) * 92, w)), int(lerp(900, 436, w)), 0,
                         lerp(1.0, 0.24, w))
        if u > 5.6:
            texto(img, "4 CARTAS?\nHORA DA GUERRA!", cin(96), (W / 2, 1250), OURO, stroke=4, scor=(30, 10, 40),
                  brilho=14, alpha=ease((u - 5.6) / 0.3))
    elif t < T_GUERRA:  # vai até a região
        u = t - T_REGIAO
        titulo = "RODADA 1 · ESCOLHA A REGIÃO"
        inventario(img, t, 4, 0)
        alfinete(img, cam, FLORESTA[0], FLORESTA[1], "FLORESTA TULGEA", T_REGIAO + 1.2, t, OURO)
        for k, (dx, dy) in enumerate(((-260, 160), (180, 240), (-60, 380))):
            alfinete(img, cam, FLORESTA[0] + dx, FLORESTA[1] + dy, "", T_REGIAO + 2.4 + 0.35 * k, t)
        painel(img, ["+3 APOIADORES", "Seu líder e seus apoiadores", "vão lutar nesta região"], 1240,
               alpha=ease((u - 2.2) / 0.4))
    elif t < T_FIM:
        img = cena_guerra(t, img, cam)
        titulo = "GUERRA · FLORESTA TULGEA"
    else:  # sobe
        u = t - T_FIM
        titulo = "FIM DA RODADA"
        texto(img, "3 RODADAS", cin(110), (W / 2, 620), OURO, stroke=4, scor=(30, 10, 40), brilho=16,
              alpha=ease(u / 0.4))
        painel(img, ["QUEM SOMAR MAIS PONTOS", "governa o País das Maravilhas"], 1220, alpha=ease((u - 0.5) / 0.4))
    lente(img, 1)
    hud(img, t, titulo, VERM if T_GUERRA <= t < T_FIM else CIANO)
    marca(img)
    return img


GUERRA = [  # (instante relativo, tipo)
    (1.2, "torre", 3), (3.0, "morsa", 2), (4.8, "loucura", 0), (6.6, "vazia", 0)]


def cena_guerra(t, img, cam):
    u = t - T_GUERRA
    texto(img, "GUERRA!", cin(150), (W / 2, 560), VERM, stroke=5, scor=(30, 0, 10), brilho=20,
          alpha=ease(u / 0.3) * (1 - ease((u - 1.1) / 0.3)))
    forca, adv = 0, min(8, 2 + int(u * 0.9))
    perdeu = False
    for t0, tipo, val in GUERRA:
        if u >= t0 + 0.5:
            forca += val
            if tipo == "loucura":
                perdeu = True
    # barras de força
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.text((100, 340), "SUA FORÇA", font=fnt(F_VT, 42), fill=CIANO + (230,))
    d.text((W - 100, 340), "RIVAL", font=fnt(F_VT, 42), fill=(255, 150, 160, 230), anchor="ra")
    d.rounded_rectangle((100, 392, 480, 430), 12, outline=CIANO + (220,), width=3)
    d.rounded_rectangle((106, 398, 106 + 368 * min(1, forca / 10), 424), 8, fill=CIANO + (240,))
    d.text((500, 411), str(forca), font=hud_font(46, 700), fill=(255, 255, 255, 255), anchor="lm")
    d.rounded_rectangle((W - 480, 392, W - 100, 430), 12, outline=(255, 150, 160, 220), width=3)
    d.rounded_rectangle((W - 106 - 368 * min(1, adv / 10), 398, W - 106, 424), 8, fill=(255, 120, 130, 240))
    d.text((W - 500, 411), str(adv), font=hud_font(46, 700), fill=(255, 255, 255, 255), anchor="rm")
    img.alpha_composite(lay)
    alfinete(img, cam, FLORESTA[0], FLORESTA[1], "FLORESTA TULGEA", -1, t, VERM)
    apo = 2 if perdeu else 3
    for k, (dx, dy) in enumerate(((-260, 160), (180, 240), (-60, 380))[:apo]):
        alfinete(img, cam, FLORESTA[0] + dx, FLORESTA[1] + dy, "", -1, t, CIANO)
    if u > 1.0 and u < 1.2 + 0.3:
        painel(img, ["PUXE FICHAS DA BOLSA", "todos ao mesmo tempo"], 1240, alpha=1)
    for t0, tipo, val in GUERRA:
        v = u - t0
        if 0 <= v < 1.75:
            k = ease(v / 0.3)
            sai = ease((v - 1.45) / 0.3)
            y = lerp(1100, 610, k) - 200 * sai
            if tipo in ("torre", "morsa"):
                cola(img, sombra(ficha(tipo), 18, (0, 18), 0.5), W // 2, int(y), 0, k * (1 - sai * 0.6))
                cola(img, ficha(tipo), W // 2, int(y), 0, k * (1 - sai * 0.6))
                nome = "TORRE VERMELHA" if tipo == "torre" else "MORSA"
                painel(img, [f"+{val} DE FORÇA", f"Você puxou: {nome}"], 1240, alpha=k * (1 - sai))
            elif tipo == "loucura":
                cola(img, ficha_loucura(), W // 2, int(y), 0, k * (1 - sai * 0.6))
                painel(img, ["FRAGMENTO DE LOUCURA!", "Você perde um apoiador"], 1240, alpha=k * (1 - sai),
                       cor=VERM)
                if v < 0.6:
                    img = glitch(img, 1 - v / 0.6, int(t * FPS))
                    img.alpha_composite(Image.new("RGBA", (W, H), (255, 0, 40, int(90 * (1 - v / 0.6)))))
            else:
                painel(img, ["MÃO VAZIA = VOCÊ PAROU", "Puxar mais? Arriscar mais loucura..."], 1240,
                       alpha=k * (1 - sai))
    if u > 8.5:
        k = ease((u - 8.5) / 0.35)
        texto(img, "VITÓRIA!", cin(150), (W / 2, 640), OURO, stroke=5, scor=(30, 10, 40), brilho=22, alpha=k)
        painel(img, ["A FLORESTA É SUA", "+ pontos  ·  + castelo"], 1240, alpha=k, cor=OURO)
    return img


@lru_cache(None)
def fundo_mesa():
    """'O mundo real': luz quente desfocada de uma mesa de jogo (bokeh), sem foto inventada."""
    img = Image.new("RGB", (W, H), (40, 24, 18))
    d = ImageDraw.Draw(img)
    for y in range(H):
        v = y / H
        d.line((0, y, W, y), fill=(int(60 + 60 * v), int(36 + 30 * v), int(26 + 10 * v)))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lay)
    rnd = random.Random(7)
    for _ in range(26):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H * 0.6), rnd.uniform(40, 130)
        dl.ellipse((x - r, y - r, x + r, y + r), fill=(255, rnd.randint(170, 220), 120, rnd.randint(40, 90)))
    lay = lay.filter(ImageFilter.GaussianBlur(18))
    img = img.convert("RGBA")
    img.alpha_composite(lay)
    return img


def cena_sai(t):
    if t < T_OLHO:  # DESCONECTANDO: glitch e a lente fechando
        u = (t - T_SAI) / (T_OLHO - T_SAI)
        img, cam = mundo(min(t, T_SAI - 0.01))
        img = glitch(img, 0.3 + 0.7 * u, int(t * FPS))
        lente(img, 1 - ease(u))
        texto(img, digita("> DESCONECTANDO...", t - T_SAI, 22), fnt(F_VT, 64), (W / 2, H / 2), CIANO)
        return img
    # abre o olho: pálpebras se abrindo (com uma piscada) e o "mundo real"
    u = t - T_OLHO
    img = fundo_mesa().copy()
    c = Image.open(os.path.join(ART, "caixa.png")).convert("RGBA")
    c.thumbnail((620, 760))
    img.alpha_composite(sombra(c, 30, (0, 30), 0.55), (W // 2 - c.width // 2 - 60, 980 - c.height // 2 - 60 + 30))
    img.alpha_composite(c, (W // 2 - c.width // 2, 980 - c.height // 2))
    foco = 1 - ease((u - 0.3) / 1.2)
    if foco > 0.02:
        img = img.filter(ImageFilter.GaussianBlur(18 * foco))
    abre = ease(u / 0.7) if u < 0.9 else (1 - math.sin(min(1, (u - 0.9) / 0.35) * math.pi) * 0.85)
    if u > 1.25:
        abre = 1
    hh = H * 0.62 * abre
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse((-W * 0.35, H / 2 - hh, W * 1.35, H / 2 + hh), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(60))
    preto = Image.new("RGBA", (W, H), (8, 4, 4, 255))
    preto.putalpha(Image.eval(m, lambda v: 255 - v))
    img.alpha_composite(preto)
    if u > 1.6:
        k = ease((u - 1.6) / 0.35)
        texto(img, "“...ESSE JOGO É\nMUITO BOM!”", cin(100), (W / 2, 470), (255, 240, 210), stroke=5,
              scor=(40, 20, 10), brilho=10, alpha=k)
    marca(img)
    return img


def cena_comenta(t):
    u = t - T_COM
    img = fundo_mesa().copy().filter(ImageFilter.GaussianBlur(6)).convert("RGBA")
    img.alpha_composite(Image.new("RGBA", (W, H), (20, 8, 30, 150)))
    g = arte("gato", 900)
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(2)), ((W - g.width) // 2, 1020 - g.height // 2))
    img.alpha_composite(Image.new("RGBA", (W, H), (10, 4, 20, 110)))
    texto(img, "SE VOCÊ ENTRASSE\nNO JOGO, QUAL LÍDER\nVOCÊ SERIA?", cin(80), (W / 2, 470), OURO, stroke=4,
          scor=(30, 10, 40), brilho=12, alpha=ease(u / 0.3))
    nomes = ["ALICE", "CHAPELEIRO LOUCO", "RAINHA DE COPAS", "JAGUADARTE", "GATO DE CHESHIRE"]
    for k, s in enumerate(nomes):
        a = ease((u - 0.4 - 0.18 * k) / 0.25)
        texto(img, s, hud_font(50, 700), (W / 2, 900 + 92 * k), (255, 255, 255), stroke=4, scor=(40, 10, 50),
              alpha=a)
    a = ease((u - 1.5) / 0.3)
    painel(img, ["COMENTA AQUI!"], 1420, alpha=a, cor=OURO, larg=620)
    marca(img)
    return img


def cena_cta(t):
    u = t - T_CTA
    img = Image.new("RGBA", (W, H), (14, 6, 24, 255))
    g = arte("gato", 1800).filter(ImageFilter.GaussianBlur(26))
    img.alpha_composite(g, ((W - g.width) // 2, (H - g.height) // 2))
    img.alpha_composite(Image.new("RGBA", (W, H), (14, 6, 24, 170)))
    lg = logo_card(300)
    img.alpha_composite(lg, ((W - lg.width) // 2, 110))
    c = Image.open(os.path.join(ART, "caixa.png")).convert("RGBA")
    c.thumbnail((560, 640))
    s = 0.9 + 0.1 * ease(u / 0.5)
    cola(img, sombra(c, 30, (0, 30), 0.6), W // 2, 760, 0, s)
    cola(img, c, W // 2, 760, 0, s)
    texto(img, "ALUGUE O\nWONDERLAND'S WAR", cin(84), (W / 2, 1200), OURO, stroke=4, scor=(30, 10, 40), brilho=10)
    texto(img, "2 a 5 jogadores  ·  125 min  ·  7 dias de jogo", hud_font(40, 600), (W / 2, 1345), (255, 255, 255))
    texto(img, "RESERVE ONLINE\nRETIRE EM MAUÁ OU RECEBA EM CASA", hud_font(44, 700), (W / 2, 1460), CIANO)
    texto(img, "LINK NA BIO · @SUAVEZ_BG", hud_font(52, 800), (W / 2, 1590), OURO)
    return img


def frame(fi):
    t = fi / FPS
    if t < T_DIVE:
        img = cena_gancho(t)
    elif t < T_DESCE:
        img = cena_mergulho(t)
    elif t < T_SAI:
        img = cena_mundo(t)
    elif t < T_COM:
        img = cena_sai(t)
    elif t < T_CTA:
        img = cena_comenta(t)
    else:
        img = cena_cta(t)
    return img.convert("RGB")


def render(fi):
    return frame(fi).tobytes()


# ---------------------------------------------------------------- som
SR = S.SR


def nota(f, d, tipo="caixinha"):
    t = S.t_(d)
    if tipo == "caixinha":  # caixinha de música
        s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) + 0.12 * np.sin(2 * np.pi * 4.1 * f * t)
        return s * np.exp(-t * 4.5)
    if tipo == "pizz":
        s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)
        return s * np.exp(-t * 9)
    s = sum(np.sin(2 * np.pi * f * k * t) / k for k in (1, 2, 3))  # pad
    return s * np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.4)


def valsa(dur):
    """Valsa sombria em 3/4 (ré menor), caixinha de música + pizzicato + pad."""
    n = int(dur * SR)
    out = np.zeros(n + SR * 3)
    bpm = 132
    b = 60 / bpm
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)  # noqa: E731
    acordes = [(50, [62, 65, 69]), (46, [62, 65, 70]), (43, [62, 67, 70]), (45, [61, 64, 69])]
    mel = [74, 77, 76, 74, 73, 74, 70, 69, 74, 77, 81, 79, 77, 76, 74, 73]
    t, k = 0.0, 0
    while t < dur:
        raiz, ac = acordes[(k // 1) % 4]
        S.add(out, nota(hz(raiz), 0.5, "pizz"), t, 0.7)
        for j in (1, 2):
            for m in ac:
                S.add(out, nota(hz(m - 12), 0.3, "pizz"), t + j * b, 0.18)
        S.add(out, nota(hz(raiz + 12), 3 * b, "pad"), t, 0.10)
        for j in range(3):
            if (k * 3 + j) % 2 == 0 or j == 0:
                S.add(out, nota(hz(mel[(k * 3 + j) % len(mel)]), 0.9), t + j * b, 0.33)
        t += 3 * b
        k += 1
    return out[:n]


def whoosh(d=1.0, sobe=True):
    t = S.t_(d)
    r = S.ruido(d)
    f0, f1 = (300, 3000) if sobe else (3000, 300)
    s = np.zeros_like(r)
    # filtro passa-faixa que varre: aproxima com blocos
    nb = 20
    for i in range(nb):
        a, b = i * len(r) // nb, (i + 1) * len(r) // nb
        fc = f0 * (f1 / f0) ** (i / nb)
        s[a:b] = S.bp_fft(r, fc * 0.6, fc * 1.6)[a:b]
    return s * np.sin(np.pi * t / d) ** 2


def boot():
    o = np.zeros(int(1.2 * SR))
    for k, f in enumerate((880, 1320, 1760)):
        S.add(o, S.bip(f, 0.09), 0.12 * k, 0.6)
    return o


def ficha_som():
    t = S.t_(0.18)
    return (np.sin(2 * np.pi * 2400 * t) * 0.5 + S.ruido(0.18) * 0.3) * np.exp(-t * 30)


def vitoria():
    o = np.zeros(int(2.0 * SR))
    for k, m in enumerate((74, 78, 81, 86)):
        S.add(o, nota(440 * 2 ** ((m - 69) / 12), 1.4), 0.09 * k, 0.5)
    return o


def desliga():
    d = 1.4
    t = S.t_(d)
    f = 900 * np.exp(-t * 3)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.5) * 0.6


def eventos():
    ev = [(0.05, boot(), 0.5), (0.6, S.estatica(0.4), 0.15), (T_DIVE + 0.4, whoosh(2.4), 0.9),
          (T_DESCE - 0.15, S.sino(), 0.5), (T_DESCE + 0.1, whoosh(3.2, False), 0.5)]
    for t0 in (T_CHA + 1.6, T_CHA + 3.6):
        ev += [(t0, S.carta_vira(), 0.7), (t0 + 0.6, S.sopro(0.4), 0.4), (t0 + 0.95, S.bip(1760, 0.06), 0.4)]
    ev += [(T_REGIAO + 0.2, whoosh(2.2), 0.5)]
    for k in range(3):
        ev.append((T_REGIAO + 2.4 + 0.35 * k, S.bip(1320 + 220 * k, 0.07), 0.5))
    ev += [(T_GUERRA, S.kick(0.6), 1.0), (T_GUERRA + 0.05, S.estouro(), 0.5)]
    for t0, tipo, _ in GUERRA:
        tt = T_GUERRA + t0
        ev.append((tt - 0.1, S.arrasta(0.3), 0.4))
        if tipo in ("torre", "morsa"):
            ev.append((tt + 0.2, ficha_som(), 0.8))
        elif tipo == "loucura":
            ev += [(tt + 0.1, S.estatica(0.6), 0.6), (tt + 0.1, S.estilhaco(), 0.5)]
    ev += [(T_GUERRA + 8.5, vitoria(), 0.8), (T_FIM + 0.1, whoosh(2.5), 0.5),
           (T_SAI + 0.1, S.estatica(1.0), 0.4), (T_SAI + 0.3, desliga(), 0.8),
           (T_OLHO + 1.6, S.plim(), 0.4), (T_COM + 0.1, S.sopro(0.5), 0.3), (T_CTA, S.sino(), 0.4)]
    return ev


def audio():
    os.makedirs(OUT, exist_ok=True)
    m = valsa(DUR)
    n = int(DUR * SR)
    tt = np.arange(n) / SR
    env = np.ones(n)
    env[(tt >= T_SAI) & (tt < T_OLHO + 1.2)] = 0.15  # o mundo "desliga" e a música volta no mundo real
    env = np.convolve(env, np.ones(int(0.25 * SR)) / int(0.25 * SR), "same")
    m = m * env
    com = os.path.join(OUT, "wl_com.wav")
    sem = os.path.join(OUT, "wl_sem.wav")
    S.grava(com, DUR, eventos(), m, musica_ganho=0.42, fx_ganho=0.8)
    S.grava(sem, DUR, eventos(), None, fx_ganho=0.8)
    return com, sem


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", nargs="*", type=float)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.frame:
        folha([frame(int(t * FPS)) for t in a.frame], os.path.join(OUT, "frames.jpg"))
        return
    com, sem = audio()
    n = int(round(DUR * FPS))
    base = os.path.join(OUT, "wonderland_com_som.mp4")
    encode(base, render, list(range(n)), com)
    import subprocess
    from motor import ffmpeg
    semv = os.path.join(OUT, "wonderland_para_musica.mp4")
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", base, "-i", sem, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", semv], check=True)
    for arq in (base, semv):
        final_loudness(arq, arq.replace(".mp4", "_final.mp4"))


if __name__ == "__main__":
    main()
