#!/usr/bin/env python3
"""Halloween, 3ª versão: visual "PÔSTER DE CINEMA" (opção 1 de conceitos.py, escolhida por ele).
A noite roxa (halloween.py) ele achou "muito infantil". Aqui é tudo adulto e limpo: fundo preto, um facho de luz fria
que acende piscando (lâmpada velha), a caixa OFICIAL surge na luz e aproxima devagar, o nome entra em letreiro serifado
(Cinzel) com as letras se juntando, frase em itálico (Cormorant) e a linha de créditos do pôster. Sem granulado, sem
emoji. Sem narração: tudo escrito na tela. Versões _com_trilha (terror do som_fg) e _para_musica.

    python3 poster.py --frame 0.5 2.6 4.5 ...    # quadros de teste em out/frames.jpg
    python3 poster.py                            # out/poster_com_trilha.mp4 e out/poster_para_musica.mp4
"""
import argparse
import math
import os
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "comum"))
sys.path.insert(0, os.path.join(REPO, "finalgirl-reels"))
from motor import W, H, FPS, seg, ease, lerp, logo_card, cola, sombra, encode, folha  # noqa: E402
import som  # noqa: E402
import som_fg  # noqa: E402,F401  (registra "terror", braam, lanterna, stinger...)

OUT = os.path.join(ROOT, "out")
AS = os.path.join(ROOT, "assets")
FT = os.path.join(AS, "fonts")
FUNDO = (6, 7, 9)
CREME = (238, 228, 210)
CINZA = (150, 152, 160)
VERMELHO = (178, 22, 28)

JOGOS = [  # (arquivo, título em linhas, frase, créditos) — jogadores/tempo do site da Sua Vez
    ("finalgirl", ["FINAL GIRL"], "Sobreviva ao assassino. Sozinho.", "1 JOGADOR  ·  60 MINUTOS  ·  14+"),
    ("vale_monstros", ["O VALE DOS", "MONSTROS II"], "Os monstros invadiram a cidade.", "1 A 6 JOGADORES  ·  90 MINUTOS"),
    ("nao_corte", ["POR FAVOR,", "NÃO CORTE", "MINHA CABEÇA!"], "Tente não ser a próxima vítima.",
     "3 A 6 JOGADORES  ·  30 MINUTOS"),
    ("mascarade", ["MASCARADE"], "Quem está por trás da máscara?", "4 A 12 JOGADORES  ·  30 MINUTOS"),
]
GANCHO = 2.2
POR = 2.7
T_COM = GANCHO + POR * len(JOGOS)
COMENTA = 2.2
T_CTA = T_COM + COMENTA
DUR = T_CTA + 3.6


# ---------------------------------------------------------------- tipografia
@lru_cache(None)
def fnt(nome, s, peso=None):
    f = ImageFont.truetype(os.path.join(FT, nome), int(s))
    if peso:
        f.set_variation_by_axes([peso])
    return f


def larg_esp(txt, f, track):
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    return sum(d.textlength(c, font=f) for c in txt) + track * (len(txt) - 1)


@lru_cache(None)
def linha(txt, nome, s, peso, cor, track, sombra_luz=False):
    """Uma linha de texto com espaçamento entre letras, numa imagem transparente justa."""
    f = fnt(nome, s, peso)
    lw = larg_esp(txt, f, track)
    im = Image.new("RGBA", (int(lw + 40), int(s * 1.5)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = 20
    for c in txt:
        d.text((x, im.height / 2), c, font=f, fill=cor, anchor="lm")
        x += d.textlength(c, font=f) + track
    if sombra_luz:  # brilho bem fino, nítido (ele não gosta de halo borrado)
        g = Image.new("RGBA", im.size, cor + (0,))
        g.putalpha(im.getchannel("A").filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * 0.35)))
        g.alpha_composite(im)
        im = g
    return im


def titulo_cabe(linhas, max_w=960, max_s=128):
    """Maior tamanho de Cinzel em que todas as linhas cabem em max_w."""
    s = max_s
    while s > 50:
        track = s * 0.14
        if all(larg_esp(l, fnt("Cinzel.ttf", s, 700), track) <= max_w for l in linhas):
            return s
        s -= 4
    return s


# ---------------------------------------------------------------- luz e caixa
@lru_cache(None)
def facho():
    """Facho de luz fria vindo de cima + poça de luz no chão (estático; a intensidade varia no tempo)."""
    luz = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(luz).polygon([(440, -60), (640, -60), (980, 1240), (100, 1240)], fill=(170, 190, 215, 50))
    luz = luz.filter(ImageFilter.GaussianBlur(70))
    chao = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(chao).ellipse((170, 1100, 910, 1270), fill=(160, 180, 205, 60))
    luz.alpha_composite(chao.filter(ImageFilter.GaussianBlur(40)))
    return luz


@lru_cache(None)
def fundo_vinheta():
    yy, xx = np.mgrid[0:H, 0:W]
    v = 1 - 0.55 * np.clip(np.hypot((xx - 540) / 800, (yy - 900) / 1150), 0, 1) ** 2
    a = np.empty((H, W, 3), np.float32)
    a[:] = FUNDO
    return Image.fromarray((a * v[..., None]).clip(0, 255).astype(np.uint8)).convert("RGBA")


@lru_cache(None)
def caixa(n, h):
    im = Image.open(os.path.join(AS, n + ".png")).convert("RGBA")
    im = im.crop(im.getbbox())
    im = im.resize((int(im.width * h / im.height), int(h)), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32)
    a[..., :3] *= np.array((0.9, 0.94, 1.03))  # puxa para a luz fria, sem lavar a arte
    # luz de cima: topo da caixa um pouco mais claro, base mais escura
    g = np.linspace(1.08, 0.78, im.height)[:, None, None]
    a[..., :3] *= g
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    return sombra(im, 30, (0, 40), 0.85)


def lampada(u):
    """Intensidade da luz: acende piscando como lâmpada velha (0 → pisca → firme) e apaga no fim."""
    if u < 0:
        return 0.0
    pisca = [(0.0, 0.07, 0.9), (0.07, 0.13, 0.15), (0.13, 0.2, 1.0), (0.2, 0.25, 0.4)]
    for a, b, v in pisca:
        if a <= u < b:
            return v
    return 1.0 - 0.03 * math.sin(u * 23) * math.sin(u * 7)  # zumbido leve, sem tremer a imagem


def aplica_luz(img, k):
    if k <= 0:
        return
    lz = facho()
    if k < 0.999:
        lz = lz.copy()
        lz.putalpha(lz.getchannel("A").point(lambda v: int(v * k)))
    img.alpha_composite(lz)


def letreiro_entra(img, linhas, s, y0, u, t_in=0.3, dur=0.55, alpha=1.0):
    """Título que surge com as letras se juntando (tracking diminui) e fade."""
    p = ease(seg(u, t_in, t_in + dur))
    if p <= 0:
        return y0
    track = s * (0.14 + 0.22 * (1 - p))
    lh = s * 1.12
    for k, l in enumerate(linhas):
        im = linha(l, "Cinzel.ttf", s, 700, CREME, round(track), True)
        cola(img, im, 540, y0 + lh * k, 0, 1.0, p * alpha)
    return y0 + lh * len(linhas)


def fade_txt(img, im, y, u, t0, alpha=1.0, d=0.35):
    p = ease(seg(u, t0, t0 + d))
    cola(img, im, 540, y + 14 * (1 - p), 0, 1.0, p * alpha)


# ---------------------------------------------------------------- cenas
def cena_gancho(img, t):
    k = lampada(t - 0.0)
    aplica_luz(img, k * 0.8)
    cola(img, linha("A SUA VEZ APRESENTA", "Cinzel.ttf", 34, 500, (200, 205, 215), 7), 540, 360, 0, 1.0, 1.0)
    ImageDraw.Draw(img).line((470, 410, 610, 410), fill=VERMELHO, width=3)
    ls = ["QUATRO JOGOS", "PARA NÃO", "DORMIR"]
    s = titulo_cabe(ls, 960, 112)
    for j, l in enumerate(ls):
        cola(img, linha(l, "Cinzel.ttf", s, 700, CREME, round(s * 0.14), True), 540, 760 + j * s * 1.18, 0, 1.0 + 0.02 * t / GANCHO, 1.0)
    fade_txt(img, linha("Você tem coragem?", "Cormorant-Italic.ttf", 66, 500, (205, 205, 210), 0), 1210, t, 0.5)
    fade_txt(img, linha("ESPECIAL DE HALLOWEEN  ·  31 DE OUTUBRO", "Cinzel.ttf", 32, 600, VERMELHO, 5), 1330, t, 0.8)
    fim = 1 - ease(seg(t, GANCHO - 0.2, GANCHO))
    return fim


def cena_jogo(img, t, j):
    u = t - (GANCHO + POR * j)
    nome, linhas, frase, cred = JOGOS[j]
    k = lampada(u)
    aplica_luz(img, k)
    nl = len(linhas)
    s = titulo_cabe(linhas, 960, 124 if nl == 1 else 104)
    h = {1: 760, 2: 680, 3: 600}[nl]
    if nome == "vale_monstros":
        h = 600
    bloco = s * 1.12 * nl
    y_tit = 1470 - bloco + s * 0.56 - (0 if nl < 3 else 10)
    cy = min(760, (y_tit - s * 0.56 - 60) - h / 2 - 10 + 40)
    zoom = 1.0 + 0.04 * ease(seg(u, 0, POR))
    cola(img, caixa(nome, h), 540, cy, 0, zoom, min(1.0, k * 1.1))
    fim = letreiro_entra(img, linhas, s, y_tit, u)
    fade_txt(img, linha(frase, "Cormorant-Italic.ttf", 62, 500, (205, 205, 210), 0), 1505, u, 0.65)
    fade_txt(img, linha(cred, "Cinzel.ttf", 31, 600, CINZA, 4), 1572, u, 0.85)
    del fim
    return 1 - ease(seg(u, POR - 0.22, POR))


def cena_comenta(img, t):
    u = t - T_COM
    aplica_luz(img, lampada(u) * 0.7)
    for j, l in enumerate(["QUAL VOCÊ", "ENCARA", "PRIMEIRO?"]):
        cola(img, linha(l, "Cinzel.ttf", 112, 700, CREME, 14, True), 540, 700 + j * 132, 0, 1.0,
             ease(seg(u, 0.1 + 0.12 * j, 0.45 + 0.12 * j)))
    fade_txt(img, linha("Comenta aqui.", "Cormorant-Italic.ttf", 80, 600, (205, 205, 210), 0), 1150, u, 0.6)
    ImageDraw.Draw(img).line((470, 1240, 610, 1240), fill=VERMELHO, width=3)
    return 1 - ease(seg(u, COMENTA - 0.2, COMENTA))


def cena_cta(img, t):
    u = t - T_CTA
    aplica_luz(img, lampada(u))
    p = ease(seg(u, 0.0, 0.4))
    cola(img, logo_card(330), 540, 200, 0, 1.0, p)
    pos = [(205, "vale_monstros", 300, -4), (395, "nao_corte", 330, -2), (880, "mascarade", 330, 4)]
    for j, (x, n, h, r) in enumerate(pos):
        cola(img, caixa(n, h), x, 640 + (30 if n == "vale_monstros" else 0), r, 1.0, ease(seg(u, 0.1 + 0.08 * j, 0.5 + 0.08 * j)))
    cola(img, caixa("finalgirl", 420), 640, 610, 0, 1.0, ease(seg(u, 0.2, 0.6)))
    for j, l in enumerate(["EM CARTAZ", "NA SUA VEZ"]):
        cola(img, linha(l, "Cinzel.ttf", 104, 700, CREME, 14, True), 540, 1000 + j * 118, 0, 1.0,
             ease(seg(u, 0.35 + 0.1 * j, 0.7 + 0.1 * j)))
    itens = [(0.7, "5 DIAS DE JOGO  ·  3 JOGOS = 7 DIAS", 40, CREME, 1255),
             (0.8, "RESERVE ONLINE  ·  RETIRE EM MAUÁ E ABC", 37, CREME, 1325),
             (0.9, "OU RECEBA EM CASA", 37, CREME, 1385),
             (1.0, "LINK NA BIO  ·  @SUAVEZ_BG", 46, (235, 60, 60), 1480)]
    for t0, txt, s, cor, y in itens:
        fade_txt(img, linha(txt, "Cinzel.ttf", s, 700, cor, 4), y, u, t0)
    ImageDraw.Draw(img).line((440, 1420, 640, 1420), fill=VERMELHO, width=3) if u > 0.95 else None
    return 1.0


def frame(t):
    img = fundo_vinheta().copy()
    if t < GANCHO:
        f = cena_gancho(img, t)
    elif t < T_COM:
        f = cena_jogo(img, t, int((t - GANCHO) // POR))
    elif t < T_CTA:
        f = cena_comenta(img, t)
    else:
        f = cena_cta(img, t)
    if t < T_CTA:
        wm = logo_card(140)
        img.alpha_composite(wm, (W - wm.width - 30, 40))
    if f < 1:  # some no escuro entre os pôsteres
        img = Image.blend(Image.new("RGBA", (W, H), FUNDO + (255,)), img, max(0.0, f))
    return img.convert("RGB")


def render_frame(fi):
    return frame(fi / FPS).tobytes()


def cues():
    c = [(0.0, "lanterna", 0.6), (0.05, "braam", 0.7), (1.6, "riser", 0.35)]
    for j in range(len(JOGOS)):
        t0 = GANCHO + POR * j
        c += [(t0, "lanterna", 0.55), (t0 + 0.13, "braam", 0.6), (t0 + 0.3, "stinger", 0.2)]
    c += [(T_COM, "lanterna", 0.5), (T_COM + 0.1, "coracao", 0.4), (T_CTA, "lanterna", 0.5), (T_CTA + 0.1, "braam", 0.55)]
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    print(f"duração {DUR:.1f} s")
    if a.frame:
        folha([frame(x) for x in a.frame], os.path.join(OUT, "frames.jpg"))
        return
    n = int(DUR * FPS)
    for nome, musica in (("com_trilha", "terror"), ("para_musica", None)):
        wav = os.path.join(OUT, f"poster_{nome}.wav")
        som.build(wav, DUR, cues(), musica=musica, fx_ganho=0.55 if musica else 0.45, musica_ganho=0.32)
        encode(os.path.join(OUT, f"poster_{nome}.mp4"), render_frame, list(range(n)), wav)


if __name__ == "__main__":
    main()
