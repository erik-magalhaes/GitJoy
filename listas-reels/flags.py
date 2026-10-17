#!/usr/bin/env python3
"""Reels "RED FLAG × GREEN FLAG NA MESA DE JOGO" (ideia 8, frases aprovadas por ele em 17/out/2026). Só texto.
Alterna vermelho/verde: o fundo inteiro vira da cor da bandeira (cortina diagonal), a bandeira tremula no mastro e a
frase entra num cartão de papel. Fecha com "Qual red flag você é? Marca o amigo!" e o CTA.

    python3 flags.py --frame 1 3 ...   # out/frames_flags.jpg
    python3 flags.py                   # out/flags_{com_trilha,para_musica}_final.mp4
"""
import argparse
import math
import os
import sys
from functools import lru_cache

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from base import W, H, FPS, OUT, texto, folha, entrega  # noqa: E402
from motor import seg, ease, lerp, out_back, logo_card, cola, sombra  # noqa: E402

TINTA, PAPEL = (28, 20, 24), (252, 248, 238)
VERM, VERM_ESC = (236, 52, 56), (120, 18, 26)
VERDE, VERDE_ESC = (40, 196, 104), (10, 84, 46)
FRASES = [  # (red?, frase)
    (True, "Ler o manual DEPOIS\nde perder"),
    (False, "Ensinar a regra\ncom paciência"),
    (True, "Explicar uma regra nova\nsó quando está ganhando"),
    (False, "Levar petisco\n(e guardanapo!)"),
    (True, "Demorar 10 minutos\nna vez"),
    (False, "Pedir revanche\ncom um sorriso"),
    (True, "Comer salgadinho\ne pegar nas cartas"),
    (False, "Guardar tudo organizado\nno saquinho"),
    (True, "Dizer \"é só um jogo\" e\nficar emburrado 3 dias"),
    (False, "Devolver o jogo alugado\ncompletinho"),
]
GANCHO = 2.4
POR = 2.0
T_FIM = GANCHO + POR * len(FRASES)
FIM = 2.6
T_CTA = T_FIM + FIM
DUR = T_CTA + 3.4


def cores(red):
    return (VERM, VERM_ESC) if red else (VERDE, VERDE_ESC)


@lru_cache(None)
def listras(cor, esc):
    img = Image.new("RGBA", (W, H), esc + (255,))  # fundo escuro, bandeira clara: contraste
    d = ImageDraw.Draw(img)
    c2 = tuple(int(lerp(a, b, 0.8)) for a, b in zip(cor, esc))
    for k in range(-H, W + H, 120):
        d.polygon([(k, 0), (k + 60, 0), (k + 60 - H, H), (k - H, H)], fill=c2)
    return img


def fundo(t):
    if t < GANCHO:
        img = listras(VERM, VERM_ESC).copy()
        verde = listras(VERDE, VERDE_ESC)
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).polygon([(W * 0.62, 0), (W, 0), (W, H), (W * 0.38, H)], fill=255)
        img.paste(verde, (0, 0), m)
        return img
    if t >= T_FIM:
        return listras((40, 30, 60), (20, 14, 30)).copy()
    k = min(len(FRASES) - 1, int((t - GANCHO) / POR))
    lt = t - GANCHO - k * POR
    novo = listras(*cores(FRASES[k][0]))
    ant = listras(*cores(FRASES[k - 1][0])) if k else listras((40, 30, 60), (20, 14, 30))
    u = ease(seg(lt, 0.0, 0.28))
    if u >= 1:
        return novo.copy()
    img = ant.copy()
    x = lerp(-H * 0.6, W + H * 0.6, u)  # cortina diagonal
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([(-10, 0), (x + H * 0.3, 0), (x - H * 0.3, H), (-10, H)], fill=255)
    img.paste(novo, (0, 0), m)
    return img


def bandeira(img, x, y, red, t, esc=1.0, alpha=1.0):
    """Mastro + pano tremulando (polígono com onda que anda)."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cor, cesc = cores(red)
    cor = tuple(min(255, int(v * 1.08)) for v in cor)
    hm, lw, ph = 520 * esc, 330 * esc, 210 * esc
    d.rounded_rectangle((x - 11 * esc, y - hm / 2, x + 11 * esc, y + hm / 2), radius=10, fill=(240, 236, 226),
                        outline=TINTA, width=int(6 * esc))
    d.ellipse((x - 22 * esc, y - hm / 2 - 34 * esc, x + 22 * esc, y - hm / 2 + 10 * esc), fill=(255, 205, 60),
              outline=TINTA, width=int(6 * esc))
    topo, base = [], []
    for i in range(25):
        u = i / 24
        onda = math.sin(u * 5.0 - t * 7.5) * 22 * esc * u
        px = x + 10 * esc + u * lw
        topo.append((px, y - hm / 2 + 10 * esc + onda))
        base.append((px, y - hm / 2 + 10 * esc + ph + onda * 0.9))
    poly = topo + base[::-1]
    d.polygon(poly, fill=TINTA)
    d.polygon([(px + 6 * esc, py + 6 * esc) for px, py in poly], fill=TINTA)
    d.polygon(poly, fill=cor, outline=(255, 255, 255), width=int(9 * esc))
    for i in range(0, 24, 6):  # dobras
        a, b = topo[i + 3], base[i + 3]
        d.line((a, b), fill=cesc + (120,), width=int(10 * esc))
    if alpha < 1:
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * alpha)))
    img.alpha_composite(lay)


@lru_cache(None)
def cartao(frase):
    tx = texto(frase, "poppins", 74, TINTA, entre=1.18)
    w, h = max(880, tx.width + 80), tx.height + 90
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), radius=28, fill=PAPEL, outline=TINTA, width=7)
    im.alpha_composite(tx, ((w - tx.width) // 2, (h - tx.height) // 2))
    return sombra(im, 16, (10, 18), 0.45)


@lru_cache(None)
def selo(red):
    cor, esc = cores(red)
    return texto("RED FLAG" if red else "GREEN FLAG", "bungee", 92, (255, 255, 255), esc, 9, 8, TINTA)


def cena_gancho(img, t):
    bandeira(img, 250, 700, True, t, 0.85, ease(seg(t, 0, 0.3)))
    bandeira(img, 720, 760, False, t + 1, 0.85, ease(seg(t, 0.15, 0.45)))
    u = out_back(seg(t, 0.25, 0.7))
    cola(img, texto("RED FLAG OU\nGREEN FLAG?", "bungee", 104, (255, 255, 255), TINTA, 9, 9, TINTA, entre=1.1), W / 2,
         1250, rot=-3, sc=u)
    v = ease(seg(t, 0.8, 1.2))
    cola(img, texto("na mesa de jogo", "poppins", 64, (255, 255, 255), TINTA, 5, 5, TINTA), W / 2, 1470, alpha=v)


def cena_frase(img, t, k):
    red, frase = FRASES[k]
    lt = t - GANCHO - k * POR
    sai = ease(seg(lt, POR - 0.16, POR))
    b = ease(seg(lt, 0.1, 0.4))
    bandeira(img, 330 if red else 390, 720 + lerp(260, 0, b), red, t, 1.3, b * (1 - sai))
    u = out_back(seg(lt, 0.22, 0.52))
    cola(img, selo(red), W / 2, 1150, rot=-3 if red else 3, sc=u * (1 - sai))
    c = out_back(seg(lt, 0.34, 0.66))
    cola(img, cartao(frase), W / 2, 1420 + 500 * sai, rot=(2 if red else -2), sc=c)


def cena_fim(img, t):
    lt = t - T_FIM
    bandeira(img, 250, 650, True, t, 0.7, ease(seg(lt, 0, 0.3)))
    bandeira(img, 720, 680, False, t + 1, 0.7, ease(seg(lt, 0.1, 0.4)))
    u = out_back(seg(lt, 0.2, 0.6))
    cola(img, texto("QUAL RED FLAG\nVOCÊ É?", "bungee", 100, (255, 255, 255), TINTA, 9, 9, TINTA, entre=1.1), W / 2,
         1150, rot=-2, sc=u)
    v = out_back(seg(lt, 0.6, 1.0))
    cola(img, texto("Marca o amigo\nque tem todas!", "poppins", 64, (255, 214, 70), TINTA, 5, 5, TINTA, entre=1.15),
         W / 2, 1420, sc=v)


def cena_cta(img, t):
    lt = t - T_CTA
    u = out_back(seg(lt, 0.0, 0.4))
    cola(img, logo_card(480), W / 2, 760, sc=u)
    v = ease(seg(lt, 0.3, 0.7))
    linhas = [("JOGO BOM TEM NA SUA VEZ", "bungee", 64, (255, 255, 255)), ("3 JOGOS = 7 DIAS DE JOGO", "poppins", 56, (255, 214, 70)),
              ("RESERVE ONLINE · RETIRE EM MAUÁ\nOU RECEBA EM CASA", "poppins", 44, (255, 255, 255)),
              ("LINK NA BIO · @SUAVEZ_BG", "bungee", 52, (255, 255, 255))]
    for k, (txt, f, s, cor) in enumerate(linhas):
        cola(img, texto(txt, f, s, cor, TINTA, 5, 5, TINTA, entre=1.2), W / 2, 1080 + k * 150 + (30 if k == 3 else 0),
             alpha=v)


def frame(t):
    img = fundo(t)
    if t < GANCHO:
        cena_gancho(img, t)
    elif t < T_FIM:
        cena_frase(img, t, min(len(FRASES) - 1, int((t - GANCHO) / POR)))
    elif t < T_CTA:
        cena_fim(img, t)
    else:
        cena_cta(img, t)
    if t < T_CTA:
        img.alpha_composite(logo_card(150), (W - 186, 46))
    return img.convert("RGB")


def render_frame(fi):
    return frame(fi / FPS).tobytes()


def cues():
    c = [(0.05, "whoosh", 0.5), (0.3, "pop", 0.6)]
    for k, (red, _f) in enumerate(FRASES):
        t0 = GANCHO + k * POR
        c += [(t0, "whoosh", 0.4), (t0 + 0.24, "carimbo" if red else "ding", 0.45 if red else 0.55),
              (t0 + 0.4, "pop", 0.45)]
    c += [(T_FIM + 0.2, "boing", 0.5), (T_CTA, "chime", 0.6)]
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    a = ap.parse_args()
    print(f"duração {DUR:.1f} s")
    if a.frame:
        os.makedirs(OUT, exist_ok=True)
        folha([frame(x) for x in a.frame], os.path.join(OUT, "frames_flags.jpg"))
        return
    entrega("flags", DUR, render_frame, cues(), "retro70", musica_ganho=0.28)


if __name__ == "__main__":
    main()
