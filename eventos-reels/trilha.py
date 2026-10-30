#!/usr/bin/env python3
"""Vídeo da MONITORIA EM EVENTOS da Sua Vez (30/out/2026), visual C escolhido por ele: TRILHA DO ABC.
Fundo xadrez amarelo (tabuleiro), identidade da Jéssica (Lilita + Figtree, contorno marrom, sombra sólida), as cidades do ABC
como casas de uma trilha e o LOGO como peão (nada de peça desenhada à mão), fotos do SITE inteiras em cartões.
Sem narração (texto na tela), ~33 s; entrega _com_trilha e _para_musica (−15,5 LUFS).
Fatos (o que eles passaram): levam os jogos e ficam o evento todo ensinando; qualquer tipo de evento; quantidade e tipo
de jogo conforme o número e o perfil das pessoas; crianças e adultos, agitados e tranquilos; principalmente o ABC;
orçamento pelo Direct ou pelo WhatsApp (11) 97793-3910. Ainda NÃO fizeram evento: nada de "já atendemos".

    python3 trilha.py --frame 2 8 14 20 26 31     # out/frames.jpg
    python3 trilha.py                             # out/eventos_{com_trilha,para_musica}_final.mp4
"""
import math
import os
import sys
from functools import lru_cache

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
sys.path.insert(0, os.path.join(REPO, "listas-reels"))
sys.path.insert(0, os.path.join(REPO, "comum"))
import estilo as E  # noqa: E402
import base  # noqa: E402
from base import foto, entrega  # noqa: E402
from motor import FPS, folha, ease, out_back  # noqa: E402

W, H = 1080, 1920
OUT = os.path.join(ROOT, "out")
# casas da trilha: (nome, x, y); a 1ª é Mauá (a casa da Sua Vez), a última é o evento
CASAS = [("MAUÁ", 250, 1470), ("RIBEIRÃO\nPIRES", 560, 1530), ("RIO GRANDE\nDA SERRA", 850, 1400),
         ("SANTO ANDRÉ", 800, 1150), ("SÃO CAETANO", 480, 1080), ("SÃO BERNARDO", 220, 900),
         ("DIADEMA", 500, 760), ("SEU EVENTO", 830, 720)]
TIPOS = ["ANIVERSÁRIO", "CONFRATERNIZAÇÃO", "EMPRESARIAL", "ESCOLA", "CONDOMÍNIO", "CASAMENTO"]
CRIANCAS = ["uga_buga", "go_cuckoo", "happy_salmon"]
ADULTOS = ["dixit", "telma", "ref_o_jogo_da_refer_ncia"]
WHATS = "(11) 97793-3910"

# cenas: (função, duração)
DUR_GANCHO, DUR_TRILHA, DUR_TIPOS, DUR_JOGOS, DUR_FICA, DUR_CTA = 3.4, 8.2, 5.6, 6.2, 4.8, 5.2


# ---------------------------------------------------------------- peças
@lru_cache(None)
def fundo():
    return E.fundo_xadrez(W, H, base=(255, 214, 90), escuro=(250, 202, 70), casa=120)


@lru_cache(None)
def titulo(txt, s, cor=E.BRANCO):
    return E.titulo(txt, s, cor, larg_max=980)


@lru_cache(None)
def casa(nome, k):
    final = nome == "SEU EVENTO"
    cor = E.LARANJA if nome == "MAUÁ" else (E.MARROM if final else (E.PETROLEO if k % 2 else E.BRANCO))
    fg = E.MARROM if cor == E.BRANCO else (E.AMARELO if final else E.BRANCO)
    w, h = (300, 150) if final else (250, 120)
    im = E.bloco(w, h, cor, raio=24, ow=6, sombra=9).copy()
    d = ImageDraw.Draw(im)
    linhas = nome.split("\n")
    s = 40 if final else (30 if max(len(l) for l in linhas) < 12 else 26)
    f = E.lilita(s) if final else E.fig(s, 900)
    for j, l in enumerate(linhas):
        d.text((w / 2, h / 2 + (j - (len(linhas) - 1) / 2) * (s * 1.1)), l, font=f, fill=fg, anchor="mm")
    return im


@lru_cache(None)
def logo(w):
    return E.logo(w)


def surge(t, t0, d=0.35):
    if t < t0:
        return 0.0, 0.0
    u = min(1.0, (t - t0) / d)
    return min(1.0, u * 2), out_back(u)


def poe(img, im, x, y, t, t0, rot=0.0, d=0.35):
    a, s = surge(t, t0, d)
    E.cola(img, im, x, y, rot, s, a)


def trilha_pontos(img, a, b, q):
    """Pontinhos da trilha de a até b, até a fração q."""
    d = ImageDraw.Draw(img)
    n = max(2, int(math.dist(a, b) / 34))
    for j in range(1, n):
        if j / n > q:
            break
        x, y = a[0] + (b[0] - a[0]) * j / n, a[1] + (b[1] - a[1]) * j / n
        d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=E.MARROM)


# ---------------------------------------------------------------- cenas
def c_gancho(img, t):
    poe(img, titulo("VAI FAZER\nUM EVENTO?", 150, E.BRANCO), W / 2, 620, t, 0.05, -3)
    poe(img, titulo("A GENTE LEVA\nOS JOGOS!", 116, E.AMARELO), W / 2, 1060, t, 0.9, 2)
    poe(img, E.pilula("E FICA O EVENTO TODO ENSINANDO", 40, E.PETROLEO, E.BRANCO), W / 2, 1380, t, 1.8, -1.5)


def c_trilha(img, t):
    poe(img, titulo("A GENTE VAI\nATÉ VOCÊ!", 112), W / 2, 260, t, 0.05, -2)
    poe(img, E.pilula("MAUÁ E TODO O ABC PAULISTA", 40, E.BRANCO), W / 2, 440, t, 0.4, 1.5)
    # a trilha vai se desenhando e as casas aparecem uma a uma
    passo = 0.42
    for k in range(len(CASAS) - 1):
        a, b = CASAS[k][1:], CASAS[k + 1][1:]
        q = min(1, max(0, (t - 0.6 - k * passo) / passo))
        trilha_pontos(img, a, b, q)
    for k, (n, x, y) in enumerate(CASAS):
        poe(img, casa(n, k), x, y, t, 0.5 + k * passo, (k % 3 - 1) * 3)
    # o logo pula de casa em casa (de Mauá até o evento)
    t0 = 0.5 + len(CASAS) * passo + 0.2
    pulo = 0.36
    u = max(0.0, (t - t0) / pulo)
    k = min(int(u), len(CASAS) - 1)
    f = u - k if k < len(CASAS) - 1 else 0
    a = CASAS[k][1:]
    b = CASAS[min(k + 1, len(CASAS) - 1)][1:]
    x = a[0] + (b[0] - a[0]) * ease(f)
    y = a[1] + (b[1] - a[1]) * ease(f) - 108 - 90 * math.sin(math.pi * f)
    achata = 1 - 0.12 * max(0, 1 - f * 6) if k > 0 else 1  # amassadinha ao cair
    poe(img, logo(190), x, y + 10 * (1 - achata), t, 0.8, -4 + 8 * f)
    if t > t0 + (len(CASAS) - 1) * pulo:  # chegou: estouro de confete na casa do evento
        q = min(1, (t - t0 - (len(CASAS) - 1) * pulo) / 0.6)
        d = ImageDraw.Draw(img)
        cx, cy = CASAS[-1][1:]
        for j in range(18):
            ang = j * 2 * math.pi / 18
            r = 60 + 170 * ease(q)
            c = (E.LARANJA, E.PETROLEO, E.BRANCO, E.MARROM)[j % 4]
            px, py = cx + r * math.cos(ang), cy + r * math.sin(ang) + 60 * q * q
            s = 12 * (1 - q * 0.5)
            d.ellipse((px - s, py - s, px + s, py + s), fill=c)
        poe(img, E.pilula("CHEGAMOS!", 44, E.AMARELO), cx - 40, cy + 120, t, t0 + (len(CASAS) - 1) * pulo, 4)


def c_tipos(img, t):
    poe(img, titulo("QUALQUER TIPO\nDE EVENTO", 116), W / 2, 330, t, 0.05, -2)
    for k, n in enumerate(TIPOS):
        x = W / 2 + (-1 if k % 2 == 0 else 1) * 230
        y = 640 + (k // 2) * 260
        im = E.bloco(420, 180, (E.PETROLEO, E.BRANCO, E.LARANJA)[k % 3], raio=28, ow=6, sombra=10).copy()
        cor = E.MARROM if k % 3 == 1 else E.BRANCO
        f = E.lilita(48 if len(n) < 12 else 38)
        ImageDraw.Draw(im).text((210, 92), n, font=f, fill=cor, anchor="mm")
        # carta virando (escala horizontal)
        t0 = 0.6 + k * 0.38
        if t < t0:
            continue
        q = min(1, (t - t0) / 0.32)
        sx = abs(math.cos(math.pi * (1 - q) / 2 * 2)) if q < 1 else 1
        if q < 0.5:  # primeira metade: verso (marrom com o logo pequeno)
            im = E.bloco(420, 180, E.MARROM, raio=28, ow=6, sombra=10).copy()
            lg = logo(150)
            im.alpha_composite(lg, ((420 - lg.width) // 2, (180 - lg.height) // 2))
        im2 = im.resize((max(2, int(im.width * max(0.04, sx))), im.height))
        E.cola(img, im2, x, y, (k % 3 - 1) * 2.5)
    poe(img, E.texto("...e o que mais você inventar!", 44, E.MARROM, 800), W / 2, 1460, t, 3.4)


def c_jogos(img, t):
    poe(img, titulo("JOGOS PRA\nTODO MUNDO", 116), W / 2, 300, t, 0.05, 2)
    for col, (rot, lista, cor) in enumerate((("CRIANÇAS", CRIANCAS, E.LARANJA), ("ADULTOS", ADULTOS, E.PETROLEO))):
        cx = W / 2 + (col - 0.5) * 480
        poe(img, E.pilula(rot, 46, cor, E.BRANCO, fonte_titulo=True), cx, 520, t, 0.5 + col * 0.3)
        for k, n in enumerate(lista):
            poe(img, foto(n, 240, sombra_a=0.35), cx, 740 + k * 262, t, 0.8 + col * 0.3 + k * 0.3,
                (k - 1) * 3 * (1 if col else -1))
    poe(img, E.pilula("AGITADOS E TRANQUILOS", 40, E.BRANCO), W / 2, 1440, t, 2.6, -1.5)
    poe(img, E.texto("A quantidade de jogos depende\ndo número e do perfil das pessoas", 38, E.MARROM, 800),
        W / 2, 1550, t, 3.4)


def c_fica(img, t):
    poe(img, titulo("E A GENTE FICA\nO EVENTO TODO", 112), W / 2, 330, t, 0.05, -2)
    # barra de tempo do evento: do começo ao fim, com o logo andando por casinhas de tabuleiro
    n = 7
    x0, x1, y = 130, W - 130, 900
    for j in range(n):
        x = x0 + (x1 - x0) * j / (n - 1)
        cor = E.BRANCO if j % 2 else E.PETROLEO
        poe(img, E.bloco(110, 110, cor, raio=20, ow=5, sombra=7), x, y, t, 0.4 + j * 0.08)
    poe(img, E.texto("começo", 34, E.MARROM, 800), x0, y + 110, t, 0.6)
    poe(img, E.texto("fim", 34, E.MARROM, 800), x1, y + 110, t, 0.9)
    q = ease(min(1, max(0, (t - 1.0) / 2.8)))
    hop = abs(math.sin(q * math.pi * (n - 1)))
    poe(img, logo(170), x0 + (x1 - x0) * q, y - 110 - 50 * hop, t, 0.8)
    itens = ["explicando as regras", "jogando junto", "trocando de jogo quando a galera quiser"]
    for k, s in enumerate(itens):
        poe(img, E.pilula(s.upper(), 36, (E.AMARELO, E.BRANCO, E.LARANJA)[k],
                          E.MARROM if k < 2 else E.BRANCO), W / 2, 1150 + k * 130, t, 1.4 + k * 0.6, (k - 1) * 1.5)


def c_cta(img, t):
    poe(img, logo(420), W / 2, 330, t, 0.05)
    poe(img, titulo("PEÇA SEU\nORÇAMENTO!", 130), W / 2, 680, t, 0.4, -2)
    cart = E.bloco(860, 330, E.BRANCO, raio=36, ow=7, sombra=12).copy()
    d = ImageDraw.Draw(cart)
    d.text((430, 80), "WhatsApp", font=E.fig(46, 800), fill=E.PETROLEO, anchor="mm")
    d.text((430, 160), WHATS, font=E.lilita(84), fill=E.MARROM, anchor="mm")
    d.text((430, 255), "ou no Direct · @suavez_bg", font=E.fig(42, 800), fill=E.MARROM, anchor="mm")
    poe(img, cart, W / 2, 1030, t, 0.9, 1)
    poe(img, E.pilula("MAUÁ E TODO O ABC PAULISTA", 42, E.LARANJA, E.BRANCO), W / 2, 1320, t, 1.5, -1.5)
    poe(img, E.texto("Comenta aqui: qual evento seu\nprecisava de jogos?", 42, E.MARROM, 800), W / 2, 1500, t, 2.2)


CENAS = [(c_gancho, DUR_GANCHO), (c_trilha, DUR_TRILHA), (c_tipos, DUR_TIPOS), (c_jogos, DUR_JOGOS),
         (c_fica, DUR_FICA), (c_cta, DUR_CTA)]
INI = [0.0]
for _, d_ in CENAS:
    INI.append(INI[-1] + d_)
DUR = INI[-1]
TRANS = 0.3


def quadro(t):
    k = max(i for i in range(len(CENAS)) if INI[i] <= t) if t < DUR else len(CENAS) - 1
    f, d = CENAS[k]
    u = t - INI[k]
    img = fundo().copy()
    cena = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f(cena, u)
    if k < len(CENAS) - 1 and u > d - TRANS:  # sai para a esquerda
        q = ease((u - (d - TRANS)) / TRANS)
        img.alpha_composite(cena, (int(-q * W), 0))
    elif k > 0 and u < TRANS:  # entra pela direita
        q = ease(u / TRANS)
        img.alpha_composite(cena, (int((1 - q) * W), 0))
    else:
        img.alpha_composite(cena)
    if f is not c_cta:
        img.alpha_composite(logo(190), (W - 228, 46))
    return img.convert("RGB")


def render(fi):
    return quadro(fi / FPS).tobytes()


def cues():
    c = [(INI[k] + 0.02, "whoosh", 0.35) for k in range(1, len(CENAS))]
    c += [(0.1, "pop", 0.5), (0.95, "pop", 0.5), (1.85, "pop", 0.4)]
    t0 = INI[1]
    c += [(t0 + 0.5 + k * 0.42, "pop", 0.35) for k in range(len(CASAS))]
    tp = t0 + 0.5 + len(CASAS) * 0.42 + 0.2
    c += [(tp + k * 0.36, "boing", 0.3) for k in range(1, len(CASAS))]
    c += [(tp + (len(CASAS) - 1) * 0.36 + 0.05, "brilho", 0.5)]
    c += [(INI[2] + 0.6 + k * 0.38, "flip", 0.5) for k in range(len(TIPOS))]
    c += [(INI[3] + 0.8 + k * 0.3, "pop", 0.35) for k in range(6)]
    c += [(INI[5] + 0.4, "ding", 0.55)]
    return c


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:]]
        folha([quadro(x) for x in ts], os.path.join(OUT, "frames.jpg"))
        print("ok", DUR)
        return
    print("duração", DUR)
    base.OUT = OUT  # os vídeos saem em eventos-reels/out
    entrega("eventos", DUR, render, cues(), "gameshow", musica_ganho=0.26)


if __name__ == "__main__":
    main()
