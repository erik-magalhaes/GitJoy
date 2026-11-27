#!/usr/bin/env python3
"""Reels "COFFEE RUSH EM 1 MINUTO OU MENOS" (14/nov/2026). A Jéssica gravou 7 vídeos (brutos fora do git em
brutos/nov14/): o gancho com a caixa (câmera da frente = ESPELHADO), a fila de pedidos, os baristas andando no balcão de
ingredientes, pegando ingredientes e montando a xícara, o leque de receitas, a entrega e a fila andando, e o fecho
("E esse é o Coffee Rush!"). Fluxo pedido pelo Erik: eu edito PRIMEIRO, ele narra o meio por cima depois.
A voz da Jéssica fica no gancho e no fecho; o meio fica sem voz (só trilha baixa e os selos) até a narração chegar.
Conceito: CONTRA O RELÓGIO (como Take Time / Sky Team), com cara de cafeteria: relógio-xícara contando 60 s.

    python3 umminuto.py --info
    python3 umminuto.py --frame 1 10 40
    python3 umminuto.py                 # out/umminuto.mp4
"""
import argparse
import json
import math
import os
import subprocess
import sys
import wave
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "comum"))
sys.path.insert(0, os.path.join(REPO, "listas-reels"))
sys.path.insert(0, os.path.join(REPO, "becas-reels"))
from motor import W, H, FPS, WHITE, ease, seg, out_back, logo_card, cola, folha, ffmpeg  # noqa: E402
import som  # noqa: E402
import sons  # noqa: E402
from base import texto  # noqa: E402

som.MUSICAS["cafe"] = lambda d: sons.musica_cafe(d)

BR = os.path.join(ROOT, "brutos", "nov14")
OUT = os.path.join(ROOT, "out")
INK = (63, 36, 18)  # marrom da identidade
CREME, CAFE, LARANJA, PETROLEO = (250, 240, 222), (111, 64, 36), (244, 136, 37), (28, 124, 150)
VERMELHO, VERDE, AMARELO = (214, 46, 52), (40, 150, 80), (255, 199, 31)
GRADE = "hqdn3d=1.5:1.5:3:3,unsharp=5:5:0.35:5:5:0.0,eq=contrast=1.02:saturation=1.02"
# voz da Jéssica com MUITA rua atrás (gravou perto da janela): rede neural de ruído (arnndn, modelo "sh" do rnnoise-models
# em comum/rnnn/) + afftdn. Medido: rua nas pausas caiu 13–25 dB e a fala ficou no mesmo nível.
RNNN = os.path.join(REPO, "comum", "rnnn", "sh.rnnn")
VOZ = (f"highpass=f=90,aresample=48000,arnndn=m={RNNN}:mix=0.92,afftdn=nr=10:nf=-45,"
       "equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1.4:g=1.5")

# (arquivo, início, fim, tipo, espelha) — tempos no bruto
TRECHOS = [
    ("073758", 0.00, 6.15, "gancho", True),   # "E aproveitando o nosso evento... Coffee Rush em 1 minuto ou menos. Vamos?"
    ("074437", 0.00, 9.70, "exp", False),     # a cafeteria: baristas fazendo café e os pedidos do lado (1º, pedido dele)
    ("075447", 0.00, 12.50, "exp", False),    # meeple ROSA anda 3 casas, pega os ingredientes, põe na xícara
    ("075447", 12.50, 19.60, "exp", False),   # xícara ao lado da receita, entrega
    ("075656", 0.00, 12.60, "exp", False),    # a fila anda, pedido cai = penalidade, ficha de pressa
    ("075858", 0.00, 8.30, "exp", False),     # PODERES: ela vira a peça de poder na cafeteria (até antes de virar a câmera pro balcão)
    ("083950", 0.00, 4.20, "exp", False),     # leque de cartas de pedido entregues = quem tem mais vence (FIM, pedido dele)
    ("084314", 1.15, 3.25, "fecho", True),    # "E esse é o Coffee Rush!" (começa 0,2 s antes da fala, que vem em 1,35 s; corta logo depois)
]
# selos das regras: (índice do trecho, segundos depois do início do trecho, texto, cor)
# (tempos acertados pela fala do Erik; no trecho 5 o tempo é do BRUTO, que roda mais devagar: VEL)
SELOS = [
    (1, 1.0, "CADA UM TEM SUA CAFETERIA", PETROLEO),
    (1, 3.0, "OS PEDIDOS CHEGAM DO LADO", LARANJA),
    (2, 1.9, "ANDA ATÉ 3 CASAS", CAFE),
    (2, 3.9, "SEM DIAGONAL!", VERMELHO),
    (2, 6.3, "PEGA O INGREDIENTE DE CADA CASA", PETROLEO),
    (2, 7.9, "MONTA NA XÍCARA", LARANJA),
    (3, 1.4, "SIGA A RECEITA DO PEDIDO", CAFE),
    (3, 2.7, "ENTREGOU! GUARDA O PEDIDO", VERDE),
    (4, 0.6, "FIM DA RODADA: A FILA ANDA", PETROLEO),
    (4, 5.6, "PEDIDO PERDIDO = PENALIDADE", VERMELHO),
    (4, 7.5, "FICHA DE PRESSA: +1 MOVIMENTO!", AMARELO),  # ela mostra a moedinha
    (5, 2.5, "PODERES ESPECIAIS!", LARANJA),
    (5, 4.6, "VIROU = PODER LIBERADO!", VERDE),
    (6, 1.0, "MAIS CAFÉS ENTREGUES = VITÓRIA!", VERDE),
]
# o vídeo dos poderes (8,3 s) é mais curto que a fala 5 (9,6 s): roda a 0,82x
VEL = {5: 0.82}
# narração do Erik (narracao/frase_NN.wav + palavras.json): fala N entra no trecho N, LEAD segundos depois do início
NAR = os.path.join(ROOT, "narracao")
LEAD = {1: 0.3, 2: 1.0, 3: 1.4, 4: 0.4, 5: 0.25, 6: 0.3}
CORRIGE = {"Coffridge,": "Coffee Rush,", "figil": "ficha", "bebida": "a bebida", "mais": "a mais"}
CORRIGE_EM = {"01": {"bebida"}, "04": {"figil", "mais"}}  # só nessas falas
LEGENDA = True
# notas fixas (ficam na tela mais tempo, embaixo do selo): (trecho, de, até, texto, cor)
NOTAS = [
    (4, 6.6, 12.6, "Perdeu um pedido? Ganha 1 ficha de pressa!", PETROLEO),
    (5, 5.4, 8.3, "Um dos poderes: casa de fita dourada = pega 2!", LARANJA),
]
# legendas da Jéssica (texto conferido de ouvido; o Whisper ouviu "Calfrush e Nelwing do Talmenis")
LEG = [
    (0, 0.05, 1.70, "E aproveitando o nosso evento"),
    (0, 1.70, 3.30, "que está chegando,\nhoje eu vou te ensinar"),
    (0, 3.70, 5.95, "Coffee Rush em 1 minuto\nou menos. Vamos?"),
    (7, 0.15, 2.10, "E esse é o Coffee Rush!"),
]
CARIMBO, COMENTA, FIM = 0.15, 3.8, 4.6
HOLD = 2.3  # o último quadro da mesa fica parado com o carimbo antes do fecho


ULT = max(i for i, tr in enumerate(TRECHOS) if tr[3] == "exp")  # último trecho da explicação


def linha():
    tl, t = [], 0.0
    for i, (arq, a, b, tipo, esp) in enumerate(TRECHOS):
        v = VEL.get(i, 1.0)
        n = round((b - a) / v * FPS)
        tl.append(dict(i=i, arq=arq, a=a, n=n, t0=t, tipo=tipo, esp=esp, v=v))
        t += n / FPS + (HOLD if i == ULT else 0)
    return tl


TL = linha()
M = {"exp": TL[1]["t0"], "fim_exp": TL[ULT]["t0"] + TL[ULT]["n"] / FPS, "fecho": TL[ULT + 1]["t0"]}
M["comenta"] = TL[ULT + 1]["t0"] + TL[ULT + 1]["n"] / FPS
M["fim"] = M["comenta"] + COMENTA
DUR = M["fim"] + FIM
SELOS_T = [(TL[i]["t0"] + dt / TL[i]["v"], txt, cor) for i, dt, txt, cor in SELOS]
NOTAS_T = [(TL[i]["t0"] + a / TL[i]["v"], TL[i]["t0"] + b / TL[i]["v"], txt, cor) for i, a, b, txt, cor in NOTAS]
LEG_T = [(TL[i]["t0"] + a, TL[i]["t0"] + b, txt) for i, a, b, txt in LEG]


def legenda_narracao(maxc=24):
    """Legenda da fala do Erik em pedaços de uma linha (o que ele FALOU, com as correções do Whisper)."""
    pal = json.load(open(os.path.join(NAR, "palavras.json"), encoding="utf-8"))
    out = []
    for k, ws in sorted(pal.items()):
        t0 = TL[int(k)]["t0"] + LEAD[int(k)]
        ws = [[a, b, CORRIGE[w] if w in CORRIGE and (w not in sum(map(list, CORRIGE_EM.values()), []) or
                                                    w in CORRIGE_EM.get(k, ())) else w] for a, b, w in ws]
        pedacos, cur = [], []
        for w in ws:
            if cur and len(" ".join(x[2] for x in cur + [w])) > maxc:
                pedacos.append(cur)
                cur = []
            cur.append(w)
            if w[2][-1] in ".!?" or (w[2][-1] == "," and len(" ".join(x[2] for x in cur)) > 10):
                pedacos.append(cur)
                cur = []
        if cur:
            pedacos.append(cur)
        for j, p in enumerate(pedacos):
            fim = pedacos[j + 1][0][0] if j + 1 < len(pedacos) else p[-1][1] + 0.35
            out.append((t0 + p[0][0], t0 + fim, " ".join(x[2] for x in p)))
    return out


LEG_N = legenda_narracao()


# ---------------------------------------------------------------- relógio-xícara
R = 112


@lru_cache(None)
def xicara():
    s = 2 * R + 120
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = s / 2
    d.ellipse((c - R - 4, c - R + 14, c + R + 14, c + R + 26), fill=(0, 0, 0, 90))  # sombra
    d.ellipse((c + R - 30, c - 40, c + R + 48, c + 40), outline=INK, width=26)  # asa
    d.ellipse((c + R - 30, c - 40, c + R + 48, c + 40), outline=CREME, width=12)
    d.ellipse((c - R, c - R, c + R, c + R), fill=CREME, outline=INK, width=8)
    r2 = R - 22
    for k in range(r2, 0, -2):  # café visto de cima: borda clara (crema) → centro escuro
        u = k / r2
        cor = tuple(int(CAFE[j] * (1 - 0.45 * (1 - u)) + (196, 140, 90)[j] * u ** 6) for j in range(3))
        d.ellipse((c - k, c - k, c + k, c + k), fill=cor)
    for k in range(12):
        a = math.radians(k * 30 - 90)
        r0 = r2 - (14 if k % 3 == 0 else 8)
        d.line((c + math.cos(a) * r0, c + math.sin(a) * r0, c + math.cos(a) * (r2 - 2), c + math.sin(a) * (r2 - 2)),
               fill=CREME, width=6 if k % 3 == 0 else 3)
    return im


@lru_cache(None)
def digital(txt, cor):
    return texto(txt, "lilita", 64, cor, INK, 6, 5, INK)


XW, XH, SS = 300, 330, 2  # relógio = xícara de vidro (como as do jogo) enchendo de café; cheia = 1 minuto


def _forma(d, fill=None, outline=None, width=0):
    k = SS
    d.polygon([(40 * k, 118 * k), (220 * k, 118 * k), (206 * k, 250 * k), (54 * k, 250 * k)], fill=fill)
    d.rounded_rectangle((54 * k, 200 * k, 206 * k, 296 * k), radius=46 * k, fill=fill)


@lru_cache(None)
def _mascara():
    m = Image.new("L", (XW * SS, XH * SS), 0)
    _forma(ImageDraw.Draw(m), fill=255)
    return m


def xicara_cheia(frac, t, caindo):
    k = SS
    im = Image.new("RGBA", (XW * k, XH * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((24 * k, 282 * k, 236 * k, 318 * k), fill=(0, 0, 0, 80))  # sombra/pires
    d.ellipse((204 * k, 150 * k, 270 * k, 250 * k), outline=INK, width=16 * k)  # asa
    d.ellipse((204 * k, 150 * k, 270 * k, 250 * k), outline=(214, 236, 242), width=7 * k)
    vidro = Image.new("RGBA", im.size, (230, 245, 250, 150))
    cafe = Image.new("RGBA", im.size, (0, 0, 0, 0))
    dc = ImageDraw.Draw(cafe)
    topo = 294 - frac * (294 - 126)
    if frac > 0.002:
        for yy in range(int(topo * k), 300 * k, 2):  # mais escuro no fundo
            u = (yy / k - topo) / max(1, 300 - topo)
            dc.line((0, yy, XW * k, yy), fill=tuple(int(c * (1 - 0.35 * u)) for c in (150, 88, 44)) + (255,), width=2)
        onda = [(x * k, (topo + 3 * math.sin(x / 13 + t * 9)) * k) for x in range(30, 232, 4)]
        dc.polygon(onda + [(232 * k, (topo + 12) * k), (30 * k, (topo + 12) * k)], fill=(214, 160, 100, 255))  # crema
        for b in range(7):  # bolhinhas na crema
            bx = 60 + (b * 37 + int(t * 40)) % 140
            dc.ellipse(((bx - 3) * k, (topo + 2) * k, (bx + 3) * k, (topo + 8) * k), fill=(240, 205, 160, 255))
    vidro.alpha_composite(cafe)
    m = _mascara()
    im.paste(vidro, (0, 0), m)
    # reflexo do vidro
    d.line((66 * k, 140 * k, 80 * k, 262 * k), fill=(255, 255, 255, 170), width=9 * k)
    d.line((40 * k, 118 * k, 54 * k, 250 * k), fill=INK, width=8 * k)
    d.line((220 * k, 118 * k, 206 * k, 250 * k), fill=INK, width=8 * k)
    d.arc((54 * k, 200 * k, 206 * k, 296 * k), 0, 180, fill=INK, width=8 * k)
    d.line((36 * k, 118 * k, 224 * k, 118 * k), fill=INK, width=8 * k)  # borda
    if caindo:  # o filete de café caindo do alto e respingando
        for yy in range(0, int(topo * k), 2):
            w = (8 + 1.0 * math.sin(yy / (9 * k) - t * 22)) * k
            cx = (130 + 1.2 * math.sin(yy / (23 * k) + t * 5)) * k
            d.line((cx - w, yy, cx + w, yy), fill=(120, 68, 32, 255), width=2)
        for g in range(4):
            fase = (t * 2.4 + g / 4) % 1
            gx = 130 + (g - 1.5) * 22 * fase
            gy = topo - 18 * math.sin(math.pi * fase)
            d.ellipse(((gx - 4) * k, (gy - 4) * k, (gx + 4) * k, (gy + 4) * k), fill=(120, 68, 32, 255))
    elif frac > 0.9:  # cheia: fumacinha
        for g in range(3):
            fase = (t * 0.6 + g / 3) % 1
            a = int(170 * math.sin(math.pi * fase))
            pts = [((96 + g * 34 + 8 * math.sin(v / 9 + t * 3 + g)) * k, (108 - v - 50 * fase) * k) for v in range(0, 70, 4)]
            d.line(pts, fill=(255, 255, 255, a), width=6 * k)
    return im.resize((XW, XH), Image.LANCZOS)


def relogio(img, t, x, y, sc=1.0):
    t0, t1 = M["exp"], M["fim_exp"]
    usado = min(max(0.0, t - t0), t1 - t0)
    resta = max(0.0, 60 - usado)
    urgente = resta < 10.5 and t < t1
    caindo = t0 <= t < t1
    pulso = 1.0 + (0.05 * max(0.0, math.cos((t - t0) * 2 * math.pi)) if urgente else 0.0)
    cola(img, xicara_cheia(usado / 60, t, caindo), x, y, sc=sc * pulso)
    s_ = int(math.ceil(resta - 1e-6)) if t < t1 else int(round(resta))
    cola(img, digital(f"0:{s_:02d}" if s_ < 60 else "1:00", (255, 110, 110) if urgente else WHITE), x - 10,
         y + (XH / 2 + 26) * sc, sc=sc)


# ---------------------------------------------------------------- textos
@lru_cache(None)
def pilula(txt, s, cor, fg=WHITE):
    tx = texto(txt, "lilita", s, fg)
    im = Image.new("RGBA", (tx.width + 44, tx.height + 10), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=im.height // 2, fill=cor,
                                          outline=INK, width=6)
    im.alpha_composite(tx, (22, 5))
    return im


@lru_cache(None)
def legenda_img(txt):
    return texto(txt, "lilita", 70, WHITE, INK, 8, 6, INK, entre=1.08)


@lru_cache(None)
def carimbo(seg_):
    tx = texto(f"EXPLICADO\nEM {seg_} SEGUNDOS!", "lilita", 88, WHITE, INK, 8, 7, INK, entre=1.05)
    im = Image.new("RGBA", (tx.width + 70, tx.height + 50), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=34, fill=VERDE, outline=INK, width=9)
    im.alpha_composite(tx, (35, 25))
    return im


@lru_cache(None)
def caixa(w):
    im = Image.open(os.path.join(ROOT, "assets", "caixa.png")).convert("RGBA")
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def legenda(img, t, y, lista=None):
    if not LEGENDA:
        return
    for a, b, txt in (LEG_T if lista is None else lista):
        if a <= t < b:
            sc = 0.85 + 0.15 * ease(min(1.0, (t - a) / 0.12))
            im = legenda_img(txt)
            cola(img, im, W / 2, y, sc=sc * min(1.0, 980 / im.width))


def overlay(t):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if t >= M["fim"]:
        tela_final(img, t - M["fim"])
        return img
    if t >= M["comenta"]:
        lt = t - M["comenta"]
        cola(img, texto("VOCÊ SERIA\nUM BOM BARISTA?", "lilita", 104, WHITE, INK, 9, 8, INK, entre=1.05),
             W / 2, 800, rot=-2, sc=out_back(seg(lt, 0.0, 0.4)))
        cola(img, pilula("Comenta aqui!", 72, LARANJA), W / 2, 1080, rot=3, sc=out_back(seg(lt, 0.4, 0.75)))
        return img
    img.alpha_composite(logo_card(150), (W - 186, 46))
    if t < M["exp"]:  # gancho: título enquanto ela fala; some quando a caixa entra (3,3 s)
        some = 1 - ease(seg(t, 3.1, 3.45))
        cola(img, texto("COFFEE RUSH\nEM 1 MINUTO", "lilita", 112, WHITE, INK, 9, 8, INK, entre=1.02), W / 2, 1100,
             rot=-2, sc=out_back(seg(t, 0.05, 0.45)) * some)
        cola(img, pilula("(OU MENOS!)", 58, VERMELHO), W / 2 + 140, 1270, rot=4, sc=out_back(seg(t, 0.6, 1.0)) * some)
        relogio(img, t, 190, 215, sc=out_back(seg(t, 0.2, 0.6)))
        legenda(img, t, 1640)
        return img
    if t < M["fecho"]:
        fim = M["fim_exp"]
        if fim <= t < fim + CARIMBO + 2.6:
            pass
        ativos = [s for s in SELOS_T if s[0] <= t]
        if ativos:
            t0, txt, cor = ativos[-1]
            prox = [s[0] for s in SELOS_T if s[0] > t0]
            dura = min(3.4, (prox[0] - t0) if prox else 3.4)
            lt = t - t0
            if lt < dura:
                u = out_back(seg(lt, 0.0, 0.3)) * (1 - ease(seg(lt, dura - 0.2, dura)))
                cola(img, pilula(txt, 60, cor), W / 2 + 70, 520, rot=-3 if len(prox) % 2 else 3,
                     sc=u * min(1.0, 860 / pilula(txt, 60, cor).width))
    if M["exp"] <= t < M["fecho"]:
        legenda(img, t, 1690, LEG_N)
    for a, b, txt, cor in NOTAS_T:
        if a <= t < b:
            u = out_back(seg(t - a, 0.0, 0.3)) * (1 - ease(seg(t, b - 0.2, b)))
            pl = pilula(txt, 46, cor)
            cola(img, pl, W / 2, 1560, rot=-1, sc=u * min(1.0, 980 / pl.width))
    # relógio até o fim da explicação + carimbo (que fica no começo do fecho), depois sai voando
    fim = M["fim_exp"]
    sai = ease(seg(t, M["fecho"] - 0.3, M["fecho"] + 0.1))
    if sai < 1:
        relogio(img, t, 190, 215 - 460 * sai)
    if fim <= t < M["fecho"]:
        lt = t - fim - CARIMBO
        cola(img, carimbo(int(fim - M["exp"])), W / 2, 960, rot=-4,
             sc=out_back(seg(lt, 0.0, 0.35)) * (1 - ease(seg(t, M["fecho"] - 0.25, M["fecho"]))))
    if t >= M["fecho"]:
        legenda(img, t, 900)
    return img


def overlay_cache_clear():
    pass


def tela_final(img, lt):
    cola(img, logo_card(300), W / 2, 215, sc=out_back(seg(lt, 0.0, 0.4)))
    cola(img, caixa(520), W / 2, 740, rot=-3, sc=out_back(seg(lt, 0.15, 0.5)))
    v = ease(seg(lt, 0.5, 0.9))
    linhas = [("ALUGUE O COFFEE RUSH", "lilita", 80, AMARELO, 1160),
              ("2 a 4 jogadores · 30 min", "figtree", 48, WHITE, 1262),
              ("RESERVE ONLINE · RETIRE EM MAUÁ\nOU RECEBA EM CASA", "figtree", 44, WHITE, 1375),
              ("LINK NA BIO · @SUAVEZ_BG", "lilita", 58, WHITE, 1515)]
    for txt, f, s, cor, y in linhas:
        cola(img, texto(txt, f, s, cor, INK, 6 if f == "lilita" else 0, 5 if f == "lilita" else 3, INK, entre=1.2),
             W / 2, y, alpha=v)
    cola(img, pilula("E NA MESA DA TARDE DE JOGOS NO BECA’S · 20/11", 40, LARANJA), W / 2, 1620, rot=-2,
         sc=out_back(seg(lt, 0.9, 1.25)))


# ---------------------------------------------------------------- vídeo
def ler(p):
    vf = (f"setpts=PTS/{p['v']}," if p["v"] != 1 else "") + f"fps={FPS},scale={W}:{H}," + ("hflip," if p["esp"] else "") + GRADE
    pr = subprocess.Popen([ffmpeg(), "-loglevel", "error", "-ss", f"{p['a']:.3f}", "-i",
                           os.path.join(BR, p["arq"] + ".mp4"), "-frames:v", str(p["n"]), "-vf", vf, "-f", "rawvideo",
                           "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    k, ultimo = 0, None
    while k < p["n"]:
        buf = pr.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        ultimo = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        yield ultimo
        k += 1
    while k < p["n"]:
        yield ultimo
        k += 1
    pr.wait()


def zoom(fr, s, cy=0.45):
    if s <= 1.001:
        return fr
    import cv2
    w, h = W / s, H / s
    x0, y0 = (W - w) / 2, min(max(0.0, cy * H - h / 2), H - h)
    M_ = np.float32([[s, 0, -x0 * s], [0, s, -y0 * s]])
    return cv2.warpAffine(fr, M_, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


def quadros():
    ultimo = None
    for p in TL:
        for k, fr in enumerate(ler(p)):
            ultimo = fr
            if p["tipo"] == "exp":  # mesa: aproximação lenta e contínua (dá movimento sem cortar nada importante)
                yield zoom(fr, 1.0 + 0.06 * k / max(1, p["n"]))
            else:
                yield fr
        if p["i"] == ULT:
            for _ in range(round(HOLD * FPS)):
                yield zoom(ultimo, 1.06)
    base = Image.fromarray(ultimo).filter(ImageFilter.GaussianBlur(20))
    escuro = np.asarray(Image.blend(base, Image.new("RGB", (W, H), (60, 34, 18)), 0.55))
    n = round(COMENTA * FPS)
    for k in range(n):
        yield zoom(escuro, 1.0 + 0.05 * k / n)
    fundo = np.asarray(Image.blend(base, Image.new("RGB", (W, H), (60, 34, 18)), 0.72))
    for _ in range(round(FIM * FPS) + 2):
        yield fundo


# ---------------------------------------------------------------- áudio
def ler_audio(arq, a, d):
    r = subprocess.run([ffmpeg(), "-loglevel", "error", "-ss", f"{a:.3f}", "-t", f"{d + 0.05:.4f}", "-i",
                        os.path.join(BR, arq + ".mp4"), "-vn", "-ac", "1", "-ar", "44100", "-af", VOZ, "-f", "s16le",
                        "-"], capture_output=True)
    x = np.frombuffer(r.stdout, np.int16).astype(np.float64) / 32768
    n = int(round(d * 44100))
    return np.pad(x, (0, max(0, n - len(x))))[:n]


def cues():
    c = [(0.0, "pop", 0.4), (0.3, "whoosh", 0.3), (M["exp"], "relogio", 0.5)]
    for k in range(1, int(M["fim_exp"] - M["exp"]) + 1):
        tk = M["exp"] + k
        if tk < M["fim_exp"]:
            c.append((tk, "tick", 0.14 if 60 - k > 10 else 0.3))
    for tv, _t, _c in SELOS_T:
        c.append((tv, "pop", 0.35))
    f = M["fim_exp"] + CARIMBO
    c += [(f, "ding", 0.6), (f + 0.05, "carimbo", 0.5), (f + 0.3, "plateia", 0.3),
          (M["comenta"], "whoosh", 0.4), (M["comenta"] + 0.4, "pop", 0.5), (M["fim"], "whoosh", 0.4),
          (M["fim"] + 0.5, "chime", 0.5)]
    return c


def audio(path):
    sr = 44100
    voz = np.zeros(int(DUR * sr) + sr)
    for p in TL:
        if p["tipo"] == "exp":
            continue
        x = ler_audio(p["arq"], p["a"], p["n"] / FPS)
        q = int(0.03 * sr)
        e = np.sqrt(np.convolve(x ** 2, np.ones(q) / q, "same"))
        x = x * 10 ** (-20 / 20) / (np.sqrt((x[e > e.max() * 0.12] ** 2).mean()) + 1e-9)
        f = int(0.02 * sr)
        x[:f] *= np.linspace(0, 1, f)
        x[-f:] *= np.linspace(1, 0, f)
        i = int(round(p["t0"] * sr))
        voz[i:i + len(x)] += x
    for k in range(1, 7):  # narração do Erik, no mesmo nível da voz da Jéssica
        with wave.open(os.path.join(NAR, f"frase_{k:02d}.wav")) as w:
            x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
        q = int(0.03 * sr)
        e = np.sqrt(np.convolve(x ** 2, np.ones(q) / q, "same"))
        x = x * 10 ** (-20 / 20) / (np.sqrt((x[e > e.max() * 0.12] ** 2).mean()) + 1e-9)
        i = int(round((TL[k]["t0"] + LEAD[k]) * sr))
        voz[i:i + len(x)] += x
    vp = os.path.join(OUT, "umminuto_voz.wav")
    with wave.open(vp, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.clip(voz, -1, 1) * 32767).astype(np.int16).tobytes())
    som.build(path, DUR, cues(), musica="cafe", voz=[(vp, 0.0)], fx_ganho=0.35, duck=0.55, musica_ganho=0.24,
              satura=False)
    r = subprocess.run([ffmpeg(), "-hide_banner", "-i", path, "-af", "loudnorm=I=-15.5:TP=-2:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    tmp = path.replace(".wav", "_n.wav")
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", path, "-af",
                    f"loudnorm=I=-15.5:TP=-2:LRA=11:linear=true:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
                    f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}",
                    "-ar", "44100", tmp], check=True)
    os.replace(tmp, path)


def render(saida, wav):
    p = subprocess.Popen([ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-framerate", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-b:v", "3000k", "-preset",
                          "medium", "-tune", "film", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest",
                          "-movflags", "+faststart", saida], stdin=subprocess.PIPE)
    for n, fr in enumerate(quadros()):
        t = n / FPS
        if t >= DUR:
            break
        im = Image.fromarray(fr).convert("RGBA")
        im.alpha_composite(overlay(t))
        p.stdin.write(im.convert("RGB").tobytes())
    p.stdin.close()
    p.wait()
    print("ok", saida, os.path.getsize(saida) // 1024 ** 2, "MB", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    ap.add_argument("--info", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    print(f"duração {DUR:.1f} s", {k: round(v, 1) for k, v in M.items()},
          f"explicação {M['fim_exp'] - M['exp']:.1f} s")
    if a.info:
        for p in TL:
            print(f"{p['t0']:6.2f} {p['n'] / FPS:5.2f} {p['arq']} {p['a']:.2f} {p['tipo']}")
        for s in SELOS_T:
            print(f"selo {s[0]:6.2f} {s[1]}")
        return
    if a.frame:
        alvo = {round(x * FPS): x for x in a.frame}
        ims = {}
        for n, fr in enumerate(quadros()):
            if n in alvo:
                im = Image.fromarray(fr).convert("RGBA")
                im.alpha_composite(overlay(n / FPS))
                ims[n] = im.convert("RGB")
            if len(ims) == len(alvo):
                break
        folha([ims[k] for k in sorted(ims)], os.path.join(OUT, "frames_umminuto.jpg"))
        return
    global LEGENDA
    wav = os.path.join(OUT, "umminuto.wav")
    audio(wav)
    for LEGENDA, nome in ((True, "legendado"), (False, "sem_legenda")):
        overlay_cache_clear()
        render(os.path.join(OUT, f"umminuto_{nome}.mp4"), wav)


if __name__ == "__main__":
    main()
