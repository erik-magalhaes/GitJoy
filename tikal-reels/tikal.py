#!/usr/bin/env python3
"""Reels "COMO SE JOGA TIKAL" (10/nov/2026). Visual B "TRAILER NA SELVA" (conceitos.py): a arte OFICIAL da capa em tela
cheia, escurecida, com raios de luz e névoa; o tabuleiro de hexágonos OFICIAIS (manual da Super Meeple, recortes.py) em
perspectiva, com a câmera passeando; exploradores (meeple oficial tingido) em pé; letreiros em Cinzel dourado e as 10
tabuletas de Pontos de Ação no alto. Regras conferidas no manual (ver CLAUDE.md).

9 falas (roteiro mandado em 10/nov): gancho · hexágono · 10 PA · templo · tesouro · maioria · guardião/troca · vulcão ·
comenta + CTA. Enquanto a narração não chega, cada cena tem a duração de `CENAS`; com `narracao/timeline.json` (gerado
pelo narracao.py) as cenas esticam para a fala.

    /usr/bin/python3 tikal.py --frame 2 8 15 ...   # out/frames_tikal.jpg
    /usr/bin/python3 tikal.py                      # out/tikal_previa.mp4 (sem voz, legenda do roteiro)
"""
import argparse
import json
import math
import os
import subprocess
import sys
from functools import lru_cache

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import pecas as P
from pecas import W, H, fonte, cola

REPO = P.REPO
for p in ("comum", "assinatura-reels", "listas-reels", "becas-reels"):
    sys.path.insert(0, os.path.join(REPO, p))
import estilo as E  # noqa: E402
import sons as S  # noqa: E402
from motor import FPS, encode, ease, out_back, ffmpeg  # noqa: E402
from base import final_loudness  # noqa: E402

OUT = os.path.join(P.ROOT, "out")
OURO, OURO_ESC, CREME = (244, 200, 84), (52, 34, 10), (246, 238, 214)
VERM, AZUL = "vermelho", "azul"

TEXTO = [
    "Você entraria na selva atrás de templos perdidos? Esse é o Tikal, e você comanda uma expedição!",
    "Na sua vez, você tira um hexágono e aumenta a selva: pode sair um templo, uma ruína cheia de tesouros, uma "
    "clareira… ou um vulcão.",
    "Depois, você tem 10 pontos de ação. Colocar um explorador no acampamento custa 1, e andar custa 1 para cada pedra "
    "do caminho.",
    "Chegou no templo? Com 2 pontos você escava mais um andar, e o templo passa a valer mais.",
    "Na ruína, cavar um tesouro custa 3. E tesouros iguais valem mais: um vale 1, um par vale 3, e três iguais valem 6!",
    "Mas o templo só dá pontos para quem tem mais exploradores nele, e o seu chefe da expedição vale por três!",
    "Quer garantir? Por 5 pontos você põe um guardião, e o templo é seu até o fim. E dá até para trocar tesouro com o "
    "adversário, e ele não pode recusar!",
    "Quando sai um vulcão, todo mundo conta pontos: os templos que domina e os tesouros. No fim, mais uma contagem, e "
    "quem tiver mais pontos vence!",
    "Você seria quem escava templos ou quem rouba tesouro? Comenta aí! E aluga o Tikal na Sua Vez, o link tá na bio.",
]
CENAS = [("gancho", 6.0), ("hexagono", 7.0), ("pa", 7.5), ("templo", 6.0), ("tesouro", 7.5), ("maioria", 6.5),
         ("guardiao", 8.0), ("vulcao", 7.5), ("cta", 9.0)]
T_COMENTA = 4.2  # dentro da cena final: até aqui é o "comenta", depois a tela final


def linha_do_tempo():
    tl = os.path.join(P.ROOT, "narracao", "timeline.json")
    if os.path.exists(tl) and "--previa" not in sys.argv:
        return json.load(open(tl))
    t, out = 0.0, []
    for k, (n, d) in enumerate(CENAS):
        out.append({"cena": n, "ini": t, "dur": d, "fala": None})
        t += d
    return out


TL = linha_do_tempo()
DUR = TL[-1]["ini"] + TL[-1]["dur"]


def cena_em(t):
    for c in TL:
        if t < c["ini"] + c["dur"] or c is TL[-1]:
            return c["cena"], t - c["ini"], c["dur"]


def seg(t, a, b):
    return min(1.0, max(0.0, (t - a) / (b - a))) if b > a else float(t >= a)


def surge(t, t0, d=0.35):
    if t < t0:
        return 0.0, 0.0
    u = min(1.0, (t - t0) / d)
    return min(1.0, u * 2), out_back(u)


# ------------------------------------------------------------------------------------------------ fundo (capa)
@lru_cache(None)
def capa_base():
    c = P.capa()
    y0, y1 = int(c.height * 0.215), int(c.height * 0.915)
    hh = y1 - y0
    ww = int(hh * W / H)
    x = int(c.width * 0.60 - ww / 2)
    bg = c.crop((x - 110, y0 + 90, x + ww + 110, y1)).resize((W + 200, H + 110), Image.LANCZOS)
    return np.asarray(bg).astype(np.float32)


@lru_cache(None)
def raios():
    luz = Image.new("L", (W, H), 0)
    dl = ImageDraw.Draw(luz)
    for k in range(5):
        x0 = 520 + k * 90
        dl.polygon([(x0, 0), (x0 + 60, 0), (x0 - 260 + k * 40, H), (x0 - 420 + k * 40, H)], fill=46)
    return np.asarray(luz.filter(ImageFilter.GaussianBlur(30))).astype(np.float32) / 255


def fundo(t, escuro=0.48, foco=None):
    """Capa com movimento lento (Ken Burns), escurecida embaixo, raios de luz pulsando de leve."""
    a = capa_base()
    dx = int(100 + 70 * math.sin(t * 0.11))
    dy = int(55 + 40 * math.sin(t * 0.07 + 1))
    im = a[dy:dy + H, dx:dx + W]
    yy = np.linspace(0, 1, H)[:, None, None]
    k = escuro * (0.95 - 0.35 * yy)
    im = im * k * np.array([0.9, 1.0, 0.94], np.float32)
    r = raios()[..., None] * (0.8 + 0.2 * math.sin(t * 0.9))
    im = im + r * np.array([255, 240, 190], np.float32)
    return Image.fromarray(np.clip(im, 0, 255).astype(np.uint8)).convert("RGBA")


# ------------------------------------------------------------------------------------------------ tabuleiro
BW, BH, HW = 1640, 1340, 360
X0, Y0 = 230, 230
# (coluna, linha): tipo — o mapa do vídeo. O acampamento-base é a clareira (0,1).
MAPA = {(0, 0): "templo", (1, 0): "clareira", (2, 0): "ruina", (3, 0): "clareira", (4, 0): "templo",
        (0, 1): "clareira", (1, 1): "templo", (2, 1): "clareira", (3, 1): "ruina", (4, 1): "clareira",
        (0, 2): "ruina", (1, 2): "clareira", (2, 2): "templo", (3, 2): "clareira"}
NOVO = (4, 2)  # onde cai o hexágono novo (cena 2) e o vulcão (cena 8)
CAMPO, TEMPLO, RUINA = (0, 1), (1, 1), (2, 0)


def hc(c, l):
    return P.hex_centro(c, l, HW, X0, Y0)


@lru_cache(None)
def tabuleiro_base(sem=()):
    tab = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    for (c, l), t in sorted(MAPA.items(), key=lambda k: (k[0][1], k[0][0])):
        if (c, l) in sem:
            continue
        x, y = hc(c, l)
        cola(tab, P.hexa(t, HW), x, y, sombra=8)
    return tab


def camera(fx, fy, zoom, giro=0.0):
    """Homografia tabuleiro → tela: centra (fx, fy), aplica zoom e giro, e inclina como um filme (perspectiva)."""
    c, s = math.cos(giro), math.sin(giro)
    T = np.array([[1, 0, -fx], [0, 1, -fy], [0, 0, 1]], float)
    R = np.array([[c * zoom, -s * zoom, 0], [s * zoom, c * zoom, 0], [0, 0, 1]], float)
    src = np.float32([[-500, -500], [500, -500], [500, 500], [-500, 500]])
    dst = np.float32([[-330, -360], [330, -360], [560, 380], [-560, 380]])
    Pm = cv2.getPerspectiveTransform(src, dst).astype(float)
    S0 = np.array([[1, 0, W / 2], [0, 1, 1230], [0, 0, 1]], float)
    return S0 @ Pm @ R @ T


def proj(M, x, y):
    v = M @ np.array([x, y, 1.0])
    return v[0] / v[2], v[1] / v[2]


def escala(M, x, y):
    a = proj(M, x, y)
    b = proj(M, x + 20, y)
    return math.dist(a, b) / 20


def desenha_tab(img, M, tab):
    warp = cv2.warpPerspective(np.asarray(tab), M, (W, H), flags=cv2.INTER_LINEAR)
    img.alpha_composite(Image.fromarray(warp))


def de_pe(img, M, sp, x, y, h, rot=0.0, alpha=1.0, pulo=0.0):
    """Sprite em pé no tabuleiro (meeple, ficha): a base fica no ponto projetado, com sombra no chão."""
    sx, sy = proj(M, x, y)
    k = escala(M, x, y)
    hh = max(4, int(h * k))
    s = sp.resize((max(1, int(sp.width * hh / sp.height)), hh), Image.LANCZOS)
    sh = Image.new("RGBA", (int(s.width * 1.2), int(s.width * 0.42)), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((0, 0, sh.width - 1, sh.height - 1), fill=(0, 0, 0, int(120 * alpha)))
    sh = sh.filter(ImageFilter.GaussianBlur(5))
    img.alpha_composite(sh, (int(sx - sh.width / 2), int(sy - sh.height / 2)))
    cola(img, s, sx, sy - hh / 2 - pulo * k, rot, 1.0, alpha)


# ------------------------------------------------------------------------------------------------ textos
def letreiro(txt, s, cor=OURO):
    f = fonte("Cinzel.ttf", s)
    linhas = txt.split("\n")
    larg = max(int(f.getlength(li)) for li in linhas) + 40
    alt = int(s * 1.18 * len(linhas)) + 30
    pad = 40
    im = Image.new("RGBA", (larg + 2 * pad, alt + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("L", im.size, 0)
    ds = ImageDraw.Draw(sh)
    for k, li in enumerate(linhas):  # halo escuro atrás do letreiro (legível sobre a capa clara)
        ds.text((larg / 2 + pad, pad + 15 + s * 0.59 + k * s * 1.18), li, font=f, fill=200, anchor="mm",
                stroke_width=s // 6)
    im.putalpha(sh.filter(ImageFilter.GaussianBlur(s // 5)))
    im = Image.merge("RGBA", (Image.new("L", im.size, 8),) * 3 + (im.getchannel("A"),))
    d = ImageDraw.Draw(im)
    for k, li in enumerate(linhas):
        y = pad + 15 + s * 0.59 + k * s * 1.18
        larg_ = larg + 2 * pad
        d.text((larg_ / 2 + 3, y + 5), li, font=f, fill=(0, 0, 0, 170), anchor="mm")
        d.text((larg_ / 2, y), li, font=f, fill=cor, anchor="mm", stroke_width=max(2, s // 28), stroke_fill=OURO_ESC)
    return im


def placa(txt, s=46, cor=CREME, larg_max=900):
    """Placa escura com borda dourada, texto em Anton (regra curta)."""
    f = fonte("Anton-Regular.ttf", s)
    linhas = txt.split("\n")
    larg = min(larg_max, max(int(f.getlength(li)) for li in linhas) + 70)
    alt = int(s * 1.25 * len(linhas)) + 40
    im = Image.new("RGBA", (larg + 16, alt + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 8, larg + 8, alt + 8), 26, fill=(20, 26, 16, 225), outline=OURO, width=5)
    for k, li in enumerate(linhas):
        d.text((larg / 2 + 8, 28 + s * 0.62 + k * s * 1.25), li, font=f, fill=cor, anchor="mm")
    return im


def custo(txt, cor=(220, 60, 50)):
    f = fonte("Anton-Regular.ttf", 64)
    im = Image.new("RGBA", (int(f.getlength(txt)) + 60, 100), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, im.width - 1, 99), 50, fill=cor, outline=CREME, width=5)
    d.text((im.width / 2, 52), txt, font=f, fill="white", anchor="mm")
    return im


def tabuletas(img, gastos, y=330, brilho=None):
    """As 10 tabuletas de Pontos de Ação. `gastos` pode ser fracionário (a última apagando)."""
    d = ImageDraw.Draw(img)
    f = fonte("Anton-Regular.ttf", 30)
    for k in range(10):
        x = 128 + k * 92
        u = min(1.0, max(0.0, gastos - k))  # 0 = cheia, 1 = gasta
        c = tuple(int(a + (b - a) * u) for a, b in zip((236, 196, 92), (70, 60, 48)))
        yy = y + 10 * u
        d.rounded_rectangle((x - 38, yy - 46, x + 38, yy + 46), 12, fill=c, outline=(40, 26, 10), width=5)
        d.text((x, yy), "PA", font=f, fill=(60, 40, 14) if u < 0.5 else (110, 96, 76), anchor="mm")
    d.text((W / 2, y + 82), f"{10 - math.ceil(gastos - 1e-6)} PONTOS DE AÇÃO", font=fonte("Anton-Regular.ttf", 40),
           fill=CREME, anchor="mm", stroke_width=4, stroke_fill=(20, 16, 8))


def legenda(img, t):
    if "--sem-legenda" in sys.argv:
        return
    cena, u, dur = cena_em(t)
    k = [c["cena"] for c in TL].index(cena)
    c = TL[k]
    if c.get("palavras"):
        pal = [p for p in c["palavras"] if p["ini"] <= t]
        if not pal:
            return
        txts = [p["w"] for p in c["palavras"]]
        idx = len(pal) - 1
        ini = (idx // 6) * 6
        txt = " ".join(txts[ini:ini + 6])
    else:
        palavras = TEXTO[k].split()
        n = math.ceil(len(palavras) / 6)
        j = min(n - 1, int(u / dur * n))
        txt = " ".join(palavras[j * 6:(j + 1) * 6])
    f = fonte("Anton-Regular.ttf", 54)
    d = ImageDraw.Draw(img)
    d.text((W / 2, 1720), txt.upper(), font=f, fill="white", anchor="mm", stroke_width=6, stroke_fill="black")


# ------------------------------------------------------------------------------------------------ peças desenhadas
@lru_cache(None)
def andar_templo(n, w=150):
    """Placa de andar de templo (pedra cinza com o número, como as peças do jogo)."""
    im = Image.new("RGBA", (w, w), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((4, 4, w - 5, w - 5), 14, fill=(150, 152, 150), outline=(70, 72, 70), width=5)
    d.rounded_rectangle((20, 20, w - 21, w - 21), 8, fill=(176, 178, 174), outline=(110, 112, 108), width=3)
    d.text((w / 2, w / 2 + 2), str(n), font=fonte("Anton-Regular.ttf", int(w * 0.55)), fill=(60, 80, 110),
           anchor="mm", stroke_width=2, stroke_fill=(220, 224, 228))
    return im


@lru_cache(None)
def selo_valor(n, s=110):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((3, 3, s - 4, s - 4), fill=OURO, outline=OURO_ESC, width=6)
    d.text((s / 2, s / 2 + 3), str(n), font=fonte("Anton-Regular.ttf", int(s * 0.6)), fill=OURO_ESC, anchor="mm")
    return im


def laje(img, M, x, y, acesa):
    """Destaque de uma laje (pedra do caminho) no chão."""
    pts = [proj(M, x + dx, y + dy) for dx, dy in ((-22, -16), (22, -16), (22, 16), (-22, 16))]
    d = ImageDraw.Draw(img)
    cor = (255, 226, 120, 255) if acesa else (190, 190, 180, 220)
    d.polygon(pts, fill=cor, outline=(60, 50, 30))


def caminho(a, b, n):
    """n lajes no meio da borda entre os hexágonos a e b."""
    (x1, y1), (x2, y2) = hc(*a), hc(*b)
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = -(y2 - y1), x2 - x1
    L = math.hypot(dx, dy)
    dx, dy = dx / L, dy / L
    return [(mx + dx * (k - (n - 1) / 2) * 52, my + dy * (k - (n - 1) / 2) * 52) for k in range(n)]


def anda(a, b, u):
    (x1, y1), (x2, y2) = a, b
    return x1 + (x2 - x1) * u, y1 + (y2 - y1) * u, 26 * abs(math.sin(u * math.pi * 3))


# ------------------------------------------------------------------------------------------------ cenas
def cena_gancho(t, u, dur):
    img = fundo(t, 0.75)
    z = 1 + 0.05 * u / dur
    if z != 1:
        big = img.resize((int(W * z), int(H * z)), Image.LANCZOS)
        img = big.crop(((big.width - W) // 2, (big.height - H) // 2, (big.width - W) // 2 + W, (big.height - H) // 2 + H))
    a, s = surge(u, 0.15, 0.5)
    if a:
        cola(img, letreiro("VOCÊ ENTRARIA\nNA SELVA ATRÁS\nDE TEMPLOS\nPERDIDOS?", 92), W / 2, 560, 0, s, a)
    a, s = surge(u, dur * 0.52, 0.5)
    if a:
        cola(img, P.img("logo_tikal.png"), W / 2, 1180, 0, 0.36 * s, a)
        a2, _ = surge(u, dur * 0.62, 0.4)
        if a2:
            cola(img, placa("VOCÊ COMANDA UMA EXPEDIÇÃO!", 50), W / 2, 1420, 0, 1, a2)
    return img


def cena_hexagono(t, u, dur):
    img = fundo(t)
    fx, fy = hc(*NOVO)
    M = camera(fx - 260 + 120 * u / dur, fy - 260, 1.0, -0.12)
    desenha_tab(img, M, tabuleiro_base((NOVO,)))
    # o hexágono novo cai do alto e encaixa
    q = seg(u, 0.6, 1.5)
    if q > 0:
        tipo = ["templo", "ruina", "clareira", "vulcao"][min(3, int(max(0, u - 2.6) / (dur - 3.2) * 4))] if u > 2.6 else "templo"
        tab = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
        e = 1 + 0.8 * (1 - ease(q))
        cola(tab, P.hexa(tipo, HW), fx, fy - 300 * (1 - ease(q)), 0, e, min(1, q * 2), sombra=10)
        desenha_tab(img, M, tab)
        if u > 2.6:
            nomes = {"templo": "TEMPLO", "ruina": "RUÍNA COM TESOURO", "clareira": "CLAREIRA", "vulcao": "VULCÃO!"}
            j = min(3, int((u - 2.6) / (dur - 3.2) * 4))
            u0 = 2.6 + j * (dur - 3.2) / 4
            a, s = surge(u, u0, 0.25)
            sx, sy = proj(M, fx, fy)
            cola(img, placa(nomes[tipo], 54, OURO), sx, sy - 210, 0, s, a)
    a, s = surge(u, 0.1, 0.4)
    cola(img, letreiro("TIRE UM HEXÁGONO\nE AUMENTE A SELVA", 72), W / 2, 450, 0, s, a)
    return img


def cena_pa(t, u, dur):
    img = fundo(t)
    cx, cy = hc(*CAMPO)
    tx, ty = hc(*TEMPLO)
    M = camera((cx + tx) / 2, (cy + ty) / 2 - 40, 1.25, 0.0)
    desenha_tab(img, M, tabuleiro_base())
    lajes = caminho(CAMPO, TEMPLO, 2)
    t_entra, t_anda = dur * 0.30, dur * 0.52
    gasto = 0.0
    # acampamento-base
    sx, sy = proj(M, cx, cy)
    cola(img, placa("ACAMPAMENTO-BASE", 34, OURO), sx, sy + 120 * escala(M, cx, cy))
    if u >= t_entra:
        gasto = 1 * seg(u, t_entra, t_entra + 0.3)
        q = seg(u, t_anda, dur - 0.6)
        for k, (lx, ly) in enumerate(lajes):
            laje(img, M, lx, ly, q * 2 > k + 0.5)
        gasto += 2 * q
        x, y, pulo = anda((cx, cy), (tx, ty), ease(q)) if q > 0 else (cx, cy, 0)
        queda = 1 - ease(seg(u, t_entra, t_entra + 0.35))
        de_pe(img, M, P.meeple(VERM, 300), x, y, 140, 0, 1, pulo + 400 * queda)
        a, s = surge(u, t_entra, 0.3)
        if u < t_anda:
            cola(img, custo("COLOCAR: 1 PA"), W / 2, 1460, 0, s, a)
        else:
            a, s = surge(u, t_anda, 0.3)
            cola(img, custo("ANDAR: 1 PA POR PEDRA"), W / 2, 1460, 0, s, a)
    a, s = surge(u, 0.05, 0.4)
    cola(img, letreiro("10 PONTOS DE AÇÃO", 70), W / 2, 205, 0, s, a)
    if u > 0.3:
        tabuletas(img, gasto, 330)
    return img


def cena_templo(t, u, dur):
    img = fundo(t)
    tx, ty = hc(*TEMPLO)
    M = camera(tx, ty - 30, 1.65, 0.05)
    desenha_tab(img, M, tabuleiro_base())
    de_pe(img, M, P.meeple(VERM, 300), tx - 110, ty + 40, 140)
    de_pe(img, M, P.meeple(VERM, 300), tx + 110, ty + 50, 140)
    sx, sy = proj(M, tx, ty)
    k1, k2 = dur * 0.3, dur * 0.6
    valor = 4 + (u >= k1 + 0.5) + (u >= k2 + 0.5)
    for j, kk in enumerate((k1, k2)):
        q = seg(u, kk, kk + 0.5)
        if 0 < q < 1:
            cola(img, andar_templo(5 + j, 170), sx, sy - 40 - 420 * (1 - ease(q)), 0, 1, min(1, q * 3))
    bump = 1 + 0.25 * max(0, 1 - abs(u - k1 - 0.5) * 4) + 0.25 * max(0, 1 - abs(u - k2 - 0.5) * 4)
    cola(img, selo_valor(valor, 150), sx, sy - 250, 0, bump)
    gasto = 3 + 2 * seg(u, k1, k1 + 0.4) + 2 * seg(u, k2, k2 + 0.4)
    tabuletas(img, gasto, 330)
    a, s = surge(u, 0.1, 0.4)
    cola(img, letreiro("ESCAVE UM ANDAR", 74), W / 2, 520, 0, s, a)
    a, s = surge(u, k1, 0.3)
    cola(img, custo("2 PA POR ANDAR"), W / 2, 1480, 0, s, a)
    return img


TES = [(0, 0), (1, 1), (2, 2)]  # (ficha, grupo)


def cena_tesouro(t, u, dur):
    img = fundo(t)
    rx, ry = hc(*RUINA)
    M = camera(rx, ry + 60, 1.45, -0.05)
    desenha_tab(img, M, tabuleiro_base())
    de_pe(img, M, P.meeple(AZUL, 300), rx - 100, ry + 60, 140)
    sx, sy = proj(M, rx, ry)
    tc = dur * 0.18
    q = seg(u, tc, tc + 0.7)
    if q > 0:  # a ficha sai da ruína e voa pro alto
        yy = sy - 40 - 300 * ease(q)
        cola(img, P.tesouro(4, 190), sx, yy, 0, 0.6 + 0.4 * ease(q))
    a, s = surge(u, tc, 0.3)
    cola(img, custo("CAVAR: 3 PA"), W / 2, 1150, 0, s, a)
    # 1 / par / trinca
    grupos = [([4], "1 PONTO"), ([4, 4], "PAR = 3"), ([4, 4, 4], "TRINCA = 6")]
    t0 = dur * 0.42
    for j, (fichas, rot) in enumerate(grupos):
        tj = t0 + j * (dur - t0 - 0.6) / 3
        a, s = surge(u, tj, 0.35)
        if not a:
            continue
        x = 200 + j * 340
        for i, f in enumerate(fichas):
            cola(img, P.tesouro(f, 130), x + (i - (len(fichas) - 1) / 2) * 60, 1380 - i * 14, (i - 1) * 6, s, a)
        cola(img, placa(rot, 42, OURO if j == 2 else CREME), x, 1530, 0, s, a)
    a, s = surge(u, 0.1, 0.4)
    cola(img, letreiro("NA RUÍNA,\nCAVE TESOUROS", 74), W / 2, 450, 0, s, a)
    return img


def cena_maioria(t, u, dur):
    img = fundo(t)
    tx, ty = hc(*TEMPLO)
    M = camera(tx, ty - 20, 1.7, 0.0)
    desenha_tab(img, M, tabuleiro_base())
    sx, sy = proj(M, tx, ty)
    cola(img, selo_valor(6, 130), sx, sy - 250)
    pos_v = [(tx - 130, ty + 20), (tx - 60, ty + 95)]
    pos_a = [(tx + 70, ty + 90), (tx + 140, ty + 20), (tx + 120, ty - 60)]
    t_chefe = dur * 0.45
    for k, (x, y) in enumerate(pos_a):
        a, s = surge(u, 0.3 + 0.15 * k, 0.3)
        if a:
            de_pe(img, M, P.meeple(AZUL, 300), x, y, 135, 0, a)
    for k, (x, y) in enumerate(pos_v):
        a, s = surge(u, 0.8 + 0.15 * k, 0.3)
        if a:
            de_pe(img, M, P.meeple(VERM, 300), x, y, 135, 0, a)
    a, s = surge(u, t_chefe, 0.4)
    if a:
        de_pe(img, M, P.meeple(VERM, 300), tx - 150, ty - 70, 200, 0, a, 300 * (1 - ease(seg(u, t_chefe, t_chefe + 0.4))))
        cx, cy = proj(M, tx - 150, ty - 70)
        cola(img, placa("CHEFE = 3", 40, OURO), cx - 40, cy - 250, 0, s, a)
    # placar
    verm = 2 + (3 if u >= t_chefe + 0.3 else 0)
    d = ImageDraw.Draw(img)
    f = fonte("Anton-Regular.ttf", 96)
    yb = 1450
    d.rounded_rectangle((150, yb - 75, 930, yb + 75), 30, fill=(20, 26, 16, 230), outline=OURO, width=5)
    d.text((340, yb), str(verm), font=f, fill=P.CORES[VERM], anchor="mm", stroke_width=4, stroke_fill="black")
    d.text((540, yb), "×", font=f, fill=CREME, anchor="mm")
    d.text((740, yb), "3", font=f, fill=P.CORES[AZUL], anchor="mm", stroke_width=4, stroke_fill="black")
    if u >= t_chefe + 0.5:
        a, s = surge(u, t_chefe + 0.5, 0.35)
        cola(img, placa("O TEMPLO É DO VERMELHO!", 50, OURO), W / 2, 1600, 0, s, a)
    a, s = surge(u, 0.05, 0.4)
    cola(img, letreiro("QUEM TEM MAIS\nEXPLORADORES\nLEVA O TEMPLO", 70), W / 2, 470, 0, s, a)
    return img


def cena_guardiao(t, u, dur):
    img = fundo(t)
    tx, ty = hc(*TEMPLO)
    meio = dur * 0.5
    if u < meio:
        M = camera(tx, ty - 20, 1.7, 0.0)
        desenha_tab(img, M, tabuleiro_base())
        sx, sy = proj(M, tx, ty)
        cola(img, selo_valor(6, 130), sx, sy - 250)
        q = seg(u, 0.5, 1.2)
        sai = seg(u, 1.4, 2.0)
        for k, (x, y) in enumerate([(tx - 130, ty + 20), (tx - 60, ty + 95)]):
            if sai < 1:
                de_pe(img, M, P.meeple(VERM, 300), x, y, 135, 0, 1 - sai, 200 * sai)
        x, y, _ = anda((tx - 150, ty - 70), (tx, ty), ease(q))
        de_pe(img, M, P.meeple(VERM, 300), x, y, 170, 0, 1, 120 * math.sin(q * math.pi) + 60 * ease(q))
        a, s = surge(u, 1.3, 0.35)
        cola(img, custo("GUARDIÃO: 5 PA"), W / 2, 1430, 0, s, a)
        a, s = surge(u, 1.7, 0.35)
        cola(img, placa("O TEMPLO É SEU ATÉ O FIM!", 50, OURO), W / 2, 1570, 0, s, a)
        a, s = surge(u, 0.05, 0.4)
        cola(img, letreiro("QUER GARANTIR?", 80), W / 2, 470, 0, s, a)
        return img
    # troca de tesouro entre jogadores
    v = u - meio
    d2 = dur - meio
    for k, (cor, x) in enumerate(((VERM, 290), (AZUL, 790))):
        cola(img, P.meeple(cor, 230), x, 900)
        cola(img, placa("VOCÊ" if k == 0 else "ADVERSÁRIO", 40, CREME), x, 1060)
    q = ease(seg(v, 0.5, 1.4))
    for k, (f, x0, x1) in enumerate(((1, 290, 790), (5, 790, 290))):
        x = x0 + (x1 - x0) * q
        y = 1240 - 180 * math.sin(q * math.pi) * (1 if k == 0 else -1)
        cola(img, P.tesouro(f, 170), x, y, 360 * q * (1 if k else -1) * 0.1)
    a, s = surge(v, 0.4, 0.3)
    cola(img, custo("TROCAR TESOURO: 3 PA"), W / 2, 1440, 0, s, a)
    a, s = surge(v, 1.4, 0.35)
    cola(img, placa("E ELE NÃO PODE RECUSAR!", 52, OURO), W / 2, 1580, 0, s, a)
    a, s = surge(v, 0.05, 0.4)
    cola(img, letreiro("E DÁ PRA TROCAR\nTESOURO À FORÇA", 76), W / 2, 470, 0, s, a)
    return img


def cena_vulcao(t, u, dur):
    tremor = max(0, 1 - abs(u - 1.25) * 2.2)
    img = fundo(t, 0.55)
    fx, fy = hc(*NOVO)
    M = camera(fx - 200 + 14 * tremor * math.sin(u * 60), fy - 200, 1.1, -0.1)
    desenha_tab(img, M, tabuleiro_base((NOVO,)))
    q = seg(u, 0.4, 1.2)
    tab = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    cola(tab, P.hexa("vulcao", HW), fx, fy - 300 * (1 - ease(q)), 0, 1 + 0.8 * (1 - ease(q)), min(1, q * 2), sombra=10)
    desenha_tab(img, M, tab)
    if u > 1.2:  # brilho laranja
        g = Image.new("RGBA", (W, H), (255, 110, 20, int(70 * min(1, (u - 1.2) * 2) * (0.7 + 0.3 * math.sin(u * 7)))))
        img.alpha_composite(g)
    a, s = surge(u, 1.25, 0.4)
    cola(img, letreiro("VULCÃO!\nHORA DE CONTAR", 84, (255, 214, 120)), W / 2, 450, 0, s, a)
    t1 = dur * 0.38
    a, s = surge(u, t1, 0.35)
    if a:
        cola(img, selo_valor(6, 140), 300, 1180, 0, s, a)
        cola(img, placa("TEMPLOS QUE\nVOCÊ DOMINA", 40), 300, 1360, 0, s, a)
    a, s = surge(u, t1 + 0.5, 0.35)
    if a:
        for i in range(3):
            cola(img, P.tesouro(4, 110), 780 + (i - 1) * 55, 1180 - i * 10, 0, s, a)
        cola(img, placa("+ SEUS\nTESOUROS", 40), 780, 1360, 0, s, a)
    a, s = surge(u, dur * 0.66, 0.4)
    cola(img, placa("3 VULCÕES + CONTAGEM FINAL", 46, OURO), W / 2, 1530, 0, s, a)
    a, s = surge(u, dur * 0.80, 0.4)
    cola(img, letreiro("MAIS PONTOS VENCE!", 70), W / 2, 760, 0, s, a)
    return img


def cena_cta(t, u, dur):
    if u < T_COMENTA:
        img = fundo(t, 0.5)
        a, s = surge(u, 0.1, 0.45)
        cola(img, letreiro("VOCÊ ESCAVA\nTEMPLOS OU\nROUBA TESOURO?", 92), W / 2, 640, 0, s, a)
        a, s = surge(u, 0.9, 0.35)
        cola(img, E.pilula("COMENTA AQUI!", 64, E.AMARELO, E.MARROM, fonte_titulo=True), W / 2, 1050, -2, s, a)
        a, s = surge(u, 1.3, 0.35)
        if a:
            cola(img, P.meeple(VERM, 260), 330, 1340, -6, s, a)
            cola(img, P.tesouro(0, 200), 760, 1340, 8, s, a)
        return img
    v = u - T_COMENTA
    img = fundo(t, 0.42)
    d = ImageDraw.Draw(img)
    a, s = surge(v, 0.05, 0.4)
    img.alpha_composite(E.logo(230), (W // 2 - 115, 140))
    cola(img, P.img("caixa.png"), W / 2, 770, -3, 0.5 * s, a)
    a, s = surge(v, 0.35, 0.35)
    cola(img, letreiro("ALUGUE O TIKAL", 92), W / 2, 1230, 0, s, a)
    a, s = surge(v, 0.6, 0.35)
    cola(img, E.pilula("2 A 4 JOGADORES · 90 MIN · 5 DIAS DE JOGO", 36, E.BRANCO, E.MARROM), W / 2, 1360, 0, s, a)
    a, s = surge(v, 0.8, 0.35)
    cola(img, E.pilula("RESERVE ONLINE · RETIRE EM MAUÁ OU RECEBA EM CASA", 30, E.AMARELO, E.MARROM), W / 2, 1450, 0, s, a)
    a, s = surge(v, 1.0, 0.35)
    cola(img, E.pilula("LINK NA BIO · @SUAVEZ_BG", 46, E.LARANJA, E.BRANCO, fonte_titulo=True), W / 2, 1550, 1, s, a)
    return img


CENA_FN = {"gancho": cena_gancho, "hexagono": cena_hexagono, "pa": cena_pa, "templo": cena_templo,
           "tesouro": cena_tesouro, "maioria": cena_maioria, "guardiao": cena_guardiao, "vulcao": cena_vulcao,
           "cta": cena_cta}


def quadro(t):
    cena, u, dur = cena_em(t)
    img = CENA_FN[cena](t, u, dur)
    # transição: escurece 0,18 s nas emendas
    ini = [c["ini"] for c in TL][1:]
    for c0 in ini:
        dd = abs(t - c0)
        if dd < 0.18:
            img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - dd / 0.18) * 0.85))))
    final = cena == "cta" and u >= T_COMENTA
    if not final:
        img.alpha_composite(E.logo(170), (W - 205, 40))
    legenda(img, t)
    return img.convert("RGB")


def render(fi):
    return quadro(fi / FPS).tobytes()


# ------------------------------------------------------------------------------------------------ som
SR = S.SR


def tom(f0=110, d=0.45):
    t = np.arange(int(d * SR)) / SR
    f = f0 * (1 + 0.6 * np.exp(-t * 18))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)


def shaker(d=0.08):
    n = int(d * SR)
    x = np.random.default_rng(3).normal(0, 1, n)
    x = S.hp_fft(x, 5000)
    return x * np.exp(-np.arange(n) / SR * 40) * 0.5


def baque(d=0.5):
    t = np.arange(int(d * SR)) / SR
    return (np.sin(2 * np.pi * 55 * t) * np.exp(-t * 9) + S.lp_fft(np.random.default_rng(1).normal(0, 1, len(t)), 400)
            * np.exp(-t * 14) * 0.6)


def ronco(d=1.6):
    t = np.arange(int(d * SR)) / SR
    x = S.lp_fft(np.random.default_rng(2).normal(0, 1, len(t)), 140) * 3
    return x * np.minimum(1, t * 6) * np.exp(-t * 1.6)


def trilha(dur):
    """Selva de aventura: tambores (tons graves), chocalho, marimba pentatônica e um drone grave."""
    out = np.zeros(int((dur + 1) * SR))
    bpm = 100
    b = 60 / bpm
    escala = ["D3", "F3", "G3", "A3", "C4", "D4", "F4"]
    mel = [0, 2, 3, 2, 4, 3, 2, 0, 1, 2, 3, 5, 4, 3, 2, 1]
    n = int(dur / b) + 1
    for k in range(n):
        t0 = k * b
        S.add(out, tom(90 if k % 4 == 0 else 130), t0, 0.7 if k % 2 == 0 else 0.4)
        if k % 4 == 3:
            S.add(out, tom(160, 0.3), t0 + b / 2, 0.35)
        for j in range(2):
            S.add(out, shaker(), t0 + j * b / 2 + b / 4, 0.18)
        if k >= 4 and k % 2 == 0:
            S.add(out, S.marimba(S.hz(escala[mel[(k // 2) % len(mel)]]), b * 1.6), t0, 0.4)
    t = np.arange(len(out)) / SR
    out += 0.07 * np.sin(2 * np.pi * S.hz("D2") * t) * (0.6 + 0.4 * np.sin(t * 0.5))
    return out[:int(dur * SR)]


def cues():
    ev = []
    for c in TL:
        i, d, n = c["ini"], c["dur"], c["cena"]
        ev.append((i, S.sopro(0.4), 0.25))
        if n == "gancho":
            ev += [(i + 0.15, S.sino(), 0.3), (i + d * 0.52, baque(), 0.7)]
        if n == "hexagono":
            ev += [(i + 1.45, baque(), 0.8)]
            ev += [(i + 2.6 + j * (d - 3.2) / 4, S.plim(), 0.3) for j in range(4)]
        if n == "pa":
            ev += [(i + d * 0.30 + 0.33, baque(0.3), 0.5)]
            ev += [(i + d * 0.52 + j * 0.12, S.tic(), 0.35) for j in range(0, 30, 3)]
        if n == "templo":
            ev += [(i + d * x + 0.5, baque(), 0.7) for x in (0.3, 0.6)]
        if n == "tesouro":
            ev += [(i + d * 0.18, S.sino(), 0.4)] + [(i + d * 0.42 + j * (d * 0.58 - 0.6) / 3, S.plim(), 0.35)
                                                       for j in range(3)]
        if n == "maioria":
            ev += [(i + d * 0.45 + 0.4, baque(), 0.7), (i + d * 0.45 + 0.5, S.sino(), 0.3)]
        if n == "guardiao":
            ev += [(i + 1.2, baque(), 0.6), (i + d * 0.5 + 0.5, S.sopro(0.6), 0.4), (i + d * 0.5 + 1.4, S.plim(), 0.4)]
        if n == "vulcao":
            ev += [(i + 1.2, ronco(), 1.0), (i + 1.2, baque(0.8), 0.9), (i + d * 0.38, S.sino(), 0.35),
                   (i + d * 0.8, S.sino(), 0.4)]
        if n == "cta":
            ev += [(i + 0.9, S.plim(), 0.4), (i + T_COMENTA, S.sopro(0.5), 0.3)]
    return ev


def audio(nome):
    com = os.path.join(OUT, f"{nome}_com.wav")
    sem = os.path.join(OUT, f"{nome}_sem.wav")
    mus = trilha(DUR + 0.5)
    S.grava(com, DUR, cues(), mus, musica_ganho=0.38, fx_ganho=0.8)
    S.grava(sem, DUR, cues(), None, fx_ganho=0.8)
    return com, sem


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    ap.add_argument("--previa", action="store_true")
    ap.add_argument("--sem-legenda", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.frame:
        ims = [quadro(x) for x in a.frame]
        cols = min(6, len(ims))
        rows = math.ceil(len(ims) / cols)
        sh = Image.new("RGB", (360 * cols, 640 * rows))
        for k, im in enumerate(ims):
            sh.paste(im.resize((360, 640), Image.LANCZOS), (360 * (k % cols), 640 * (k // cols)))
        sh.save(os.path.join(OUT, "frames_tikal.jpg"), quality=88)
        print("ok")
        return
    nome = "tikal_previa"
    com, sem = audio(nome)
    n = int(round(DUR * FPS))
    base = os.path.join(OUT, f"{nome}.mp4")
    encode(base, render, list(range(n)), com)
    final_loudness(base, base.replace(".mp4", "_final.mp4"))
    print("ok", DUR)


if __name__ == "__main__":
    main()
