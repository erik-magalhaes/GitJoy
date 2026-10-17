#!/usr/bin/env python3
"""Reels "QUANTAS PESSOAS VÃO JOGAR?" (ideia 6, aprovada por ele em 17/out/2026). Sem narração, tudo escrito.
Mesa redonda de feltro verde vista de cima, num piso de tábuas; as cadeiras vão chegando em volta (1, 2, 4, 6 e 10) e o
número fica no meio da mesa. Em cada faixa, 3 FOTOS DO SITE em cartões brancos. Jogadores/tempo = os do site.
(Nada de meeple desenhado à mão: só cadeiras, que são formas simples.)

    python3 pessoas.py --frame 1 4 ...   # out/frames_pessoas.jpg
    python3 pessoas.py                   # out/pessoas_{com_trilha,para_musica}_final.mp4
"""
import argparse
import math
import os
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from base import W, H, FPS, OUT, texto, foto, folha, entrega  # noqa: E402
from motor import seg, ease, lerp, out_back, logo_card, cola, sombra  # noqa: E402

TINTA, CREME, AMARELO, VERDE, MADEIRA = (40, 26, 16), (255, 246, 228), (255, 199, 31), (30, 110, 70), (150, 92, 50)
CORES_CAD = [(230, 90, 60), (40, 130, 190), (250, 180, 40), (120, 80, 170), (60, 160, 100)]
FAIXAS = [  # (rótulo, nº de cadeiras, texto do meio, [(foto, nome, linha do site)])
    ("SOZINHO", 1, "1", [("world_wonders", "World Wonders", "1 a 5 · 70 min"), ("fliptown", "Fliptown", "1 a 4 · 45 min"),
                         ("dice_colony", "Dice Colony", "1 a 4 · 60 min")]),
    ("A DOIS", 2, "2", [("7_wonders_duel", "7 Wonders Duel", "2 · 30 min"), ("fugitive_second_edition", "Fugitive", "2 · 20 min"),
                        ("allumbra_o_duelo", "Allumbra", "2 · 10 min")]),
    ("3 OU 4", 4, "3–4", [("samoa", "Samoa", "2 a 4 · 25 min"), ("savernake_forest", "Savernake Forest", "2 a 4 · 40 min"),
                          ("rebirth", "Rebirth", "2 a 4 · 60 min")]),
    ("5 OU MAIS", 6, "5+", [("blablabel", "Blablabel", "3 a 9 · 35 min"), ("conectados", "Conectados", "4 a 8 · 60 min"),
                            ("encantados", "Encantados", "2 a 6 · 60 min")]),
    ("FESTA!", 10, "10+", [("ref_o_jogo_da_refer_ncia", "Ref!", "2 a 10 · 25 min"), ("top_geek_pop", "É Top!?", "2 a 10 · 30 min"),
                           ("uno_stacko", "UNO Stacko", "2 a 10 · 20 min")]),
]
GANCHO = 2.2
POR = 3.2
T_SALVA = GANCHO + POR * len(FAIXAS)
SALVA = 2.0
T_CTA = T_SALVA + SALVA
DUR = T_CTA + 3.4
MX, MY, MR, RC = W / 2, 620, 250, 345  # mesa: centro, raio; raio das cadeiras


@lru_cache(None)
def piso():
    rng = np.random.default_rng(3)
    a = np.zeros((H, W, 3), np.float32)
    tab = 120
    for k, x in enumerate(range(0, W, tab)):
        base = np.array([214, 178, 134]) * (0.94 + 0.08 * rng.random())
        veio = (np.sin(np.linspace(0, 40 + 20 * rng.random(), H))[:, None] * 6)
        a[:, x:x + tab] = (base + veio)[:, None, :]
        a[:, x:x + 3] = (150, 112, 76)
    return Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert("RGBA")


@lru_cache(None)
def mesa():
    s = 2 * MR + 80
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = s / 2
    d.ellipse((c - MR, c - MR, c + MR, c + MR), fill=MADEIRA)
    d.ellipse((c - MR + 22, c - MR + 22, c + MR - 22, c + MR - 22), fill=VERDE)
    d.ellipse((c - MR + 22, c - MR + 22, c + MR - 22, c + MR - 22), outline=(20, 80, 50), width=6)
    return sombra(im, 20, (0, 22), 0.45)


@lru_cache(None)
def cadeira(cor):
    im = Image.new("RGBA", (150, 150), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((18, 38, 132, 136), radius=26, fill=cor, outline=TINTA, width=6)  # assento
    d.rounded_rectangle((10, 8, 140, 46), radius=16, fill=tuple(int(v * 0.75) for v in cor), outline=TINTA, width=6)  # encosto
    return sombra(im, 8, (0, 8), 0.4)


def cadeiras(img, t):
    k = min(len(FAIXAS) - 1, max(0, int((t - GANCHO) / POR))) if t >= GANCHO else -1
    n = FAIXAS[k][1] if k >= 0 else 0
    t0 = GANCHO + max(k, 0) * POR
    for j in range(n):
        ang = -math.pi / 2 + 2 * math.pi * j / n + (math.pi / n if n in (2, 4) else 0) * 0
        if n == 1:
            ang = math.pi / 2
        u = out_back(seg(t, t0 + 0.05 + j * 0.05, t0 + 0.35 + j * 0.05))
        r = lerp(RC + 260, RC, min(1, u))
        x, y = MX + r * math.cos(ang), MY + r * math.sin(ang)
        rot = -math.degrees(ang) - 90
        cola(img, cadeira(CORES_CAD[j % len(CORES_CAD)]), x, y, rot=rot, alpha=min(1, u * 2))


def meio(img, t):
    if t < GANCHO:
        return
    k = min(len(FAIXAS) - 1, int((t - GANCHO) / POR))
    lt = t - GANCHO - k * POR
    u = out_back(seg(lt, 0.2, 0.5))
    txt = FAIXAS[k][2]
    cola(img, texto(txt, "alfa", 150 if len(txt) < 3 else 116, CREME, TINTA, 8, 7, TINTA), MX, MY, sc=u)


@lru_cache(None)
def cartao(arq, w):
    return foto(arq, w, borda=12, cor_borda=CREME, raio=24, sombra_a=0.55)


def cena_gancho(img, t):
    u = out_back(seg(t, 0.0, 0.45))
    cola(img, texto("?", "alfa", 200, AMARELO, TINTA, 9, 8, TINTA), MX, MY, sc=u)
    v = out_back(seg(t, 0.15, 0.6))
    cola(img, texto("QUANTAS PESSOAS\nVÃO JOGAR?", "alfa", 88, CREME, TINTA, 9, 9, TINTA, entre=1.08), W / 2, 1180,
         rot=-2, sc=v)
    w = ease(seg(t, 0.7, 1.1))
    cola(img, texto("tem jogo certo pra cada mesa", "poppins_eb", 50, TINTA), W / 2, 1460, alpha=w)


def cena_faixa(img, t, k):
    rot_, _n, _m, jogos = FAIXAS[k]
    lt = t - GANCHO - k * POR
    sai = ease(seg(lt, POR - 0.2, POR))
    u = out_back(seg(lt, 0.3, 0.6))
    cola(img, texto(rot_, "alfa", 96, AMARELO, TINTA, 8, 8, TINTA), W / 2, 1095, rot=2, sc=u * (1 - sai))
    xs = [190, 540, 890]
    for j, (arq, nome, linha) in enumerate(jogos):
        c = ease(seg(lt, 0.45 + j * 0.15, 0.8 + j * 0.15))
        if c <= 0.01:
            continue
        x = xs[j] + lerp(700 if j == 2 else -700 if j == 0 else 0, 0, c)
        y = 1345 + lerp(0 if j != 1 else 700, 0, c) + 700 * sai
        cola(img, cartao(arq, 330), x, y, rot=(-3, 0, 3)[j])
        f = ease(seg(lt, 0.7 + j * 0.15, 1.0 + j * 0.15)) * (1 - sai)
        cola(img, texto(nome, "alfa", 46 if len(nome) < 12 else 38, CREME, TINTA, 5, 4, TINTA), xs[j], 1565, alpha=f)
        cola(img, texto(linha, "poppins_eb", 36, TINTA), xs[j], 1622, alpha=f)


def cena_salva(img, t):
    lt = t - T_SALVA
    u = out_back(seg(lt, 0.0, 0.4))
    cola(img, texto("MANDA PRO GRUPO\nDA NOITE DE JOGOS!", "alfa", 86, AMARELO, TINTA, 8, 8, TINTA, entre=1.08), W / 2,
         1150, rot=-2, sc=u)
    v = ease(seg(lt, 0.4, 0.8))
    cola(img, texto("e comenta: quantos são aí?", "poppins_eb", 50, TINTA), W / 2, 1400, alpha=v)


def cena_cta(img, t):
    lt = t - T_CTA
    u = out_back(seg(lt, 0.0, 0.4))
    cola(img, logo_card(480), W / 2, 760, sc=u)
    v = ease(seg(lt, 0.3, 0.7))
    linhas = [("ALUGUE NA SUA VEZ", "alfa", 84, CREME), ("3 JOGOS = 7 DIAS DE JOGO", "poppins", 56, (170, 50, 30)),
              ("RESERVE ONLINE · RETIRE EM MAUÁ\nOU RECEBA EM CASA", "poppins_eb", 44, TINTA),
              ("LINK NA BIO · @SUAVEZ_BG", "alfa", 54, CREME)]
    for k, (txt, f, s, cor) in enumerate(linhas):
        cola(img, texto(txt, f, s, cor, TINTA, 6 if f == "alfa" else 0, 5 if f == "alfa" else 0, TINTA, entre=1.2), W / 2,
             1080 + k * 150 + (30 if k == 3 else 0), alpha=v)


def frame(t):
    img = piso().copy()
    if t < T_SALVA:
        cola(img, mesa(), MX, MY)
        cadeiras(img, t)
        meio(img, t)
    if t < GANCHO:
        cena_gancho(img, t)
    elif t < T_SALVA:
        cena_faixa(img, t, min(len(FAIXAS) - 1, int((t - GANCHO) / POR)))
    elif t < T_CTA:
        cena_salva(img, t)
    else:
        cena_cta(img, t)
    if t < T_CTA:
        img.alpha_composite(logo_card(150), (W - 186, 46))
    return img.convert("RGB")


def render_frame(fi):
    return frame(fi / FPS).tobytes()


def cues():
    c = [(0.05, "pop", 0.6), (0.2, "boing", 0.5)]
    for k, (_r, n, _m, _j) in enumerate(FAIXAS):
        t0 = GANCHO + k * POR
        c += [(t0 + 0.12 + j * 0.05, "pop", 0.35) for j in range(n)]
        c += [(t0 + 0.3, "ding", 0.5)]
        c += [(t0 + 0.55 + j * 0.15, "whoosh", 0.35) for j in range(3)]
    c += [(T_SALVA, "reveal", 0.6), (T_CTA, "chime", 0.6)]
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    a = ap.parse_args()
    print(f"duração {DUR:.1f} s")
    if a.frame:
        os.makedirs(OUT, exist_ok=True)
        folha([frame(x) for x in a.frame], os.path.join(OUT, "frames_pessoas.jpg"))
        return
    entrega("pessoas", DUR, render_frame, cues(), "travessa", musica_ganho=0.28)


if __name__ == "__main__":
    main()
