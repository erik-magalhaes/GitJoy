#!/usr/bin/env python3
"""Story 1080x1920 das ASSINATURAS (pedido da Jéssica, 13/out/2026): os 3 planos empilhados, "Assine pelo link" com
seta e um espaço LIVRE (y ~1560–1650) para o adesivo de link do Instagram. Identidade em estilo.py.

    python3 story.py      # out/story_assinatura.png
"""
import os

from PIL import Image, ImageDraw

from estilo import (MARROM, PETROLEO, LARANJA, AMARELO, BRANCO, PRATA, CAT, PLANOS, titulo, texto, bloco, pilula, logo,
                    dado, peao, fundo, cola)

ROOT = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920


def linha_plano(k):
    nome, preco, por_vez, cats, cor, cor_tit, obs = PLANOS[k]
    c = bloco(900, 205, cor, raio=36, ow=7, sombra=12)
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((470, 20, 874, 185), radius=28, fill=BRANCO, outline=MARROM, width=5)
    cola(c, titulo(nome, 74 if nome != "PLATINUM" else 64, BRANCO, sw=6, sombra=6), 235, 72)
    cola(c, titulo(f"R$ {preco}/mês", 50, cor_tit, sw=0, sombra=0), 235, 150)
    cola(c, titulo(f"{por_vez} JOGO{'S' if por_vez > 1 else ''} POR VEZ", 42, MARROM, sw=0, sombra=0), 672, 60)
    cats_txt = {0: "Pocket e Família", 1: "+ Estratégico", 2: "Acervo inteiro + Deluxe*"}[k]
    cola(c, texto(cats_txt, 34, PETROLEO if k < 2 else MARROM, 800), 672, 113)
    if obs:
        cola(c, texto("*máx. 1 Deluxe por vez", 24, MARROM, 700), 672, 155)
    else:
        cola(c, texto("trocas sem limite", 26, MARROM, 700), 672, 155)
    return c


def main():
    img = fundo(W, H, 9)
    cola(img, logo(260), W / 2, 250, -2)
    cola(img, pilula("NOVIDADE!", 38, LARANJA, BRANCO, pad=(28, 10)), W / 2, 385, 3)
    cola(img, titulo("ASSINATURA\nSUA VEZ!", 120, BRANCO, larg_max=820), W / 2, 540, -2)
    cola(img, texto("Jogue o mês inteiro e troque de jogo quantas vezes quiser.", 40, MARROM, 700, larg_max=820),
         W / 2, 728)
    for k in range(3):
        cola(img, linha_plano(k), W / 2 + (-8, 10, -4)[k], 905 + k * 232, (-1.2, 1, -0.8)[k])
    cola(img, pilula("ASSINE PELO LINK", 52, AMARELO, MARROM, pad=(36, 14), fonte_titulo=True), W / 2, 1545, -2)
    d = ImageDraw.Draw(img)
    cx = W / 2  # seta para baixo, onde vai o adesivo de link
    d.rounded_rectangle((cx - 12, 1600, cx + 12, 1630), radius=12, fill=MARROM)
    d.polygon([(cx - 36, 1624), (cx + 36, 1624), (cx, 1662)], fill=MARROM)
    # ~1670–1755: espaço livre para o adesivo de link do Instagram
    cola(img, texto("Retire em Mauá ou receba em casa  ·  @suavez_bg", 30, MARROM, 800), W / 2, 1785)
    cola(img, dado(96, 6, AMARELO), 110, 1640, -12)
    cola(img, peao(124, LARANJA), 970, 1635, 10)
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    img.convert("RGB").save(os.path.join(ROOT, "out", "story_assinatura.png"))
    print("ok")


if __name__ == "__main__":
    main()
