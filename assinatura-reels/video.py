#!/usr/bin/env python3
"""Reels 9:16 das ASSINATURAS (pedido da Jéssica, 13/out/2026), sem ninguém aparecendo e sem narração: tudo escrito
na tela, na identidade da Sua Vez! (estilo.py) e com os mesmos cartões do carrossel (carrossel.py).
Cenas: gancho → "chegou a assinatura" → como funciona (3 passos) → Silver → Gold → Platinum → comenta → CTA.
Duas versões: _com_trilha (gameshow do comum/som.py) e _para_musica (só efeitos).

    python3 video.py --frame 1 4 9 13 18 23 27 30
    python3 video.py
"""
import argparse
import math
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "comum"))
from motor import FPS, seg, ease, lerp, pop, encode, folha  # noqa: E402
import som  # noqa: E402
from estilo import MARROM, PETROLEO, LARANJA, AMARELO, BRANCO, JOGOS, titulo, texto, pilula, logo, dado, peao, \
    fundo, cola, leque  # noqa: E402
from carrossel import cartao_passo, cartao_plano, mini_plano  # noqa: E402

OUT = os.path.join(ROOT, "out")
W, H = 1080, 1920
T_CHEGOU = 2.8
T_COMO = 5.4
T_PLANO = [11.6, 16.0, 20.4]
DUR_PLANO = 4.4
T_COM = 24.8
T_CTA = 28.0
DUR = 32.0
FRASE = {0: "Pra começar a jogar sem compromisso.", 1: "Dois jogos em casa e muito mais estratégia.",
         2: "O acervo inteiro, até os Deluxe."}

_FUNDO = None


def bg():
    global _FUNDO
    if _FUNDO is None:
        _FUNDO = fundo(W, H, 5)
    return _FUNDO.copy()


def entra(t, t0, d=0.45):
    """0→1 com leve passada do ponto (cartão chegando)."""
    u = seg(t, t0, t0 + d)
    return 1 - (1 - u) ** 3 + 0.08 * math.sin(u * math.pi) if u < 1 else 1.0


def cena_gancho(img, t):
    cola(img, titulo("E SE VOCÊ\nPUDESSE JOGAR\nO MÊS INTEIRO?", 130, BRANCO, larg_max=940), W / 2, 820, -2,
         pop(t, 0.05, 0.45))
    for k, (x, y, f, c) in enumerate(((180, 1300, 5, AMARELO), (540, 1330, 3, LARANJA), (900, 1290, 6, BRANCO))):
        q = entra(t, 0.5 + 0.15 * k, 0.5)
        cola(img, dado(150, f, c, MARROM if c != LARANJA else BRANCO), x, lerp(-200, y, q), lerp(200, (-12, 8, 15)[k], q))


def cena_chegou(img, t):
    u = t - T_CHEGOU
    cola(img, pilula("CHEGOU!", 48, LARANJA, BRANCO, pad=(34, 12)), W / 2, 470, 3, pop(t, T_CHEGOU))
    cola(img, titulo("ASSINATURA\nSUA VEZ!", 150, BRANCO, larg_max=900), W / 2, 700, -2, pop(t, T_CHEGOU + 0.15))
    cola(img, texto("Jogue o mês inteiro e troque\nde jogo quantas vezes quiser.", 46, MARROM, 800), W / 2, 960,
         0, 1, min(1, seg(u, 0.5, 0.8)))
    q = entra(t, T_CHEGOU + 0.6, 0.6)
    jogos = [JOGOS["POCKET"][0], JOGOS["FAMÍLIA"][0], JOGOS["DELUXE"][1], JOGOS["ESTRATÉGICO"][0], JOGOS["FAMÍLIA"][1]]
    cola(img, leque(jogos, 330), W / 2, lerp(2300, 1340, q))


def cena_como(img, t):
    cola(img, titulo("COMO FUNCIONA?", 110, BRANCO), W / 2, 380, -2, pop(t, T_COMO))
    for k in range(3):
        t0 = T_COMO + 0.5 + 1.5 * k
        q = entra(t, t0, 0.45)
        if q <= 0:
            continue
        x = lerp(W + 600, W / 2 + (-10, 12, -6)[k], q)
        cola(img, cartao_passo(k), x, 680 + k * 300, (1, -1, 0.6)[k] + (1 - q) * 10)
    if t > T_COMO + 4.6:
        cola(img, texto("Na entrega em casa, a taxa varia conforme a região e é cobrada a cada troca.", 30, MARROM, 600,
                        larg_max=820), W / 2, 1620, 0, 1, min(1, seg(t, T_COMO + 4.6, T_COMO + 5.0)))


def cena_plano(img, t, i):
    t0 = T_PLANO[i]
    q = entra(t, t0, 0.5)
    sai = ease(seg(t, t0 + DUR_PLANO - 0.35, t0 + DUR_PLANO))
    x = lerp(W + 700, W / 2, q) - sai * (W + 700)
    cola(img, cartao_plano(i), x, 860, (-1.2, 1.0, -0.8)[i] + (1 - q) * 8 - sai * 8)
    a = 1 - sai
    if t > t0 + 0.8:
        cola(img, titulo(FRASE[i], 56, BRANCO, sw=5, sombra=5, larg_max=960), W / 2, 1485, -1, pop(t, t0 + 0.8), a)


def cena_comenta(img, t):
    cola(img, titulo("QUAL É O\nSEU PLANO?", 140, BRANCO), W / 2, 560, -2, pop(t, T_COM))
    for k, x in enumerate((205, 540, 875)):
        q = entra(t, T_COM + 0.4 + 0.15 * k, 0.4)
        cola(img, mini_plano(k), x, lerp(2300, 1000 + (0, -20, 0)[k], q), (-4, 0, 4)[k])
    b = 1 + 0.04 * abs(math.sin(t * 6))
    cola(img, pilula("COMENTA AQUI!", 64, LARANJA, BRANCO, pad=(40, 16), fonte_titulo=True), W / 2, 1360, 2,
         pop(t, T_COM + 1.0) * b)


def cena_cta(img, t):
    u = t - T_CTA
    cola(img, logo(380), W / 2, 380, -2, pop(t, T_CTA))
    cola(img, titulo("ASSINE PELO\nLINK NA BIO", 130, BRANCO), W / 2, 700, -2, pop(t, T_CTA + 0.25))
    itens = [(0.6, pilula("SILVER R$ 49 · GOLD R$ 89 · PLATINUM R$ 139", 36, AMARELO, MARROM, pad=(30, 12)), 950),
             (0.8, pilula("TROCAS SEM LIMITE NO MÊS", 40, PETROLEO, BRANCO, pad=(30, 12)), 1060),
             (1.0, pilula("RETIRE EM MAUÁ OU RECEBA EM CASA", 38, LARANJA, BRANCO, pad=(30, 12)), 1170),
             (1.2, texto("suavez.acervodejogos.com.br  ·  @suavez_bg", 38, MARROM, 800), 1290)]
    for t0, im, y in itens:
        if u >= t0:
            cola(img, im, W / 2, y, 0, pop(t, T_CTA + t0))
    q = entra(t, T_CTA + 1.3, 0.5)
    cola(img, dado(130, 6, AMARELO), lerp(-150, 190, q), 1500, -12 + 200 * (1 - q))
    cola(img, peao(170, PETROLEO), lerp(W + 150, 890, q), 1490, 10)


def frame(t):
    img = bg()
    if t < T_CHEGOU:
        cena_gancho(img, t)
    elif t < T_COMO:
        cena_chegou(img, t)
    elif t < T_PLANO[0]:
        cena_como(img, t)
    elif t < T_COM:
        cena_plano(img, t, min(2, int((t - T_PLANO[0]) // DUR_PLANO)))
    elif t < T_CTA:
        cena_comenta(img, t)
    else:
        cena_cta(img, t)
    if t < T_CTA:
        cola(img, logo(170), W - 125, 105, 0)
    return img.convert("RGB")


def render_frame(fi):
    return frame(fi / FPS).tobytes()


def cues():
    c = [(0.05, "pop", 0.5), (0.5, "boing", 0.35), (0.65, "boing", 0.3), (0.8, "boing", 0.3),
         (T_CHEGOU, "reveal", 0.6), (T_CHEGOU + 0.6, "whoosh", 0.4), (T_COMO, "pop", 0.4)]
    c += [(T_COMO + 0.5 + 1.5 * k, "whoosh", 0.4) for k in range(3)]
    for t0 in T_PLANO:
        c += [(t0, "whoosh", 0.5), (t0 + 0.45, "ding", 0.45), (t0 + 0.8, "pop", 0.3)]
    c += [(T_COM, "pop", 0.4), (T_COM + 1.0, "boing", 0.35), (T_CTA, "reveal", 0.6), (T_CTA + 1.2, "ding", 0.5)]
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.frame:
        folha([frame(x) for x in a.frame], os.path.join(OUT, "frames.jpg"))
        return
    n = int(DUR * FPS)
    for nome, musica in (("com_trilha", "gameshow"), ("para_musica", None)):
        wav = os.path.join(OUT, f"assinatura_{nome}.wav")
        som.build(wav, DUR, cues(), musica=musica, fx_ganho=0.5, musica_ganho=0.25)
        encode(os.path.join(OUT, f"assinatura_{nome}.mp4"), render_frame, list(range(n)), wav)


if __name__ == "__main__":
    main()
