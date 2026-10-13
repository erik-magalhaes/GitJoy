#!/usr/bin/env python3
"""Carrossel 1080x1350 das ASSINATURAS da Sua Vez! (pedido da Jéssica, 13/out/2026):
capa → como funciona → Silver → Gold → Platinum → chamada para assinar (link na bio). Identidade em estilo.py.

    python3 carrossel.py      # out/carrossel/01_capa.png ... 06_assine.png (+ out/carrossel_folha.jpg)
"""
import os

from PIL import Image, ImageDraw

from estilo import (MARROM, PETROLEO, LARANJA, AMARELO, BRANCO, PRATA, CAT, PLANOS, JOGOS, titulo, texto, bloco, pilula,
                    logo, jogo, dado, peao, fundo, cola, selos_categoria, leque, brl)

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out", "carrossel")
W, H = 1080, 1350


def arrasta(img, txt="arrasta pro lado"):
    cola(img, pilula(txt + "  →", 28, BRANCO, MARROM, pad=(22, 8), ow=4, sombra=5), W - 200, H - 92, -3)


def capa():
    img = fundo(W, H, 1)
    cola(img, logo(300), W / 2, 175, -2)
    cola(img, pilula("NOVIDADE!", 40, LARANJA, BRANCO, pad=(30, 10)), W / 2, 335, 3)
    cola(img, titulo("ASSINATURA\nSUA VEZ!", 140, BRANCO, larg_max=860), W / 2, 535, -2)
    cola(img, texto("Jogue o mês inteiro e troque de jogo\nquantas vezes quiser.", 44, MARROM, 700), W / 2, 755)
    jogos = [JOGOS["POCKET"][0], JOGOS["FAMÍLIA"][0], JOGOS["DELUXE"][1], JOGOS["ESTRATÉGICO"][0], JOGOS["FAMÍLIA"][1]]
    cola(img, leque(jogos, 300), W / 2, 1010)
    cola(img, pilula("A PARTIR DE R$ 49/MÊS", 46, AMARELO, MARROM, pad=(34, 14), fonte_titulo=True), W / 2, 1215, -2)
    cola(img, dado(100, 5, AMARELO), 110, 1150, -14)
    cola(img, peao(140, LARANJA), 975, 1140, 10)
    return img


PASSOS = [(1, "Escolha seu plano", "Silver, Gold ou Platinum: o que muda é quantos jogos você leva por vez.", AMARELO),
          (2, "Pegue seus jogos", "Retire em Mauá ou receba em casa.", LARANJA),
          (3, "Devolveu? Troca!", "Devolva um jogo e pegue outro. Sem limite de trocas no mês!", PETROLEO)]


def cartao_passo(k):
    n, tit, desc, cor = PASSOS[k]
    card = bloco(880, 250, BRANCO, raio=34)
    cola(card, dado(150, n, cor, BRANCO if cor != AMARELO else MARROM), 110, 125, (-8, 6, -4)[k])
    cola(card, titulo(tit, 58, MARROM, BRANCO, sw=0, sombra=0), 545, 75)
    cola(card, texto(desc, 34, MARROM, 600, larg_max=600), 545, 165)
    return card


def como_funciona():
    img = fundo(W, H, 2)
    cola(img, titulo("COMO FUNCIONA?", 104, BRANCO), W / 2, 160, -2)
    for k in range(3):
        cola(img, cartao_passo(k), W / 2 + (-10, 12, -6)[k], 330 + k * 290 + 110, (1, -1, 0.6)[k])
    cola(img, texto("Na entrega em casa, a taxa varia conforme a região e é cobrada a cada troca.", 26, MARROM, 600,
                    larg_max=700), W / 2, 1195)
    arrasta(img)
    return img


def cartao_plano(i):
    nome, preco, por_vez, cats, cor, cor_tit, obs = PLANOS[i]
    card = bloco(900, 1010, cor, raio=46, ow=9, sombra=16)
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((40, 40, 860, 300), radius=34, fill=BRANCO, outline=MARROM, width=6)
    cola(card, titulo(nome, 120, cor if cor != PRATA else (150, 166, 175), sw=8, sombra=8), 450, 120)
    cola(card, titulo(f"R$ {preco}", 96, MARROM, BRANCO, sw=0, sombra=0), 400, 238)
    cola(card, texto("/mês", 40, MARROM, 800), 400 + 12 + titulo(f"R$ {preco}", 96, MARROM, BRANCO, sw=0, sombra=0).width / 2
         + 40, 248)
    jogos_txt = f"{por_vez} JOGO POR VEZ" if por_vez == 1 else f"{por_vez} JOGOS POR VEZ"
    cola(card, pilula(jogos_txt, 54, BRANCO, MARROM, pad=(34, 12), fonte_titulo=True), 450, 380, -2)
    branco = cor_tit == BRANCO
    ImageDraw.Draw(card).rounded_rectangle((60, 440, 840, 668 if len(cats) == 4 else 615), radius=30, fill=BRANCO,
                                           outline=MARROM, width=5)  # painel branco: os selos não somem no cartão
    cola(card, texto("Categorias do plano:" if i < 2 else "O acervo inteiro:", 36, MARROM, 800), 450, 482)
    cola(card, selos_categoria(cats, 34, larg_max=800), 450, 560 if len(cats) < 4 else 585)
    exemplos = []
    for c in cats:
        exemplos += JOGOS[c][:2 if len(cats) <= 2 or c == "ESTRATÉGICO" else 1]
    if i == 2:
        exemplos = [JOGOS["POCKET"][1], JOGOS["FAMÍLIA"][2], JOGOS["DELUXE"][0], JOGOS["ESTRATÉGICO"][1], JOGOS["DELUXE"][1]]
    cola(card, leque(exemplos[:5], 225), 450, 775 if len(cats) < 4 else 808)
    extra = obs or {0: "pra começar a jogar", 1: "mais jogos e mais estratégia"}[i]
    cola(card, pilula(extra.upper() if not obs else obs, 30, AMARELO if obs else LARANJA, MARROM if obs else BRANCO,
                      pad=(24, 8), ow=4, sombra=5), 450, 968)
    del d
    return card


def plano(i):
    img = fundo(W, H, 3 + i)
    cola(img, cartao_plano(i), W / 2 - 4, 625, (-1.2, 1.0, -0.8)[i])
    if i < 2:
        arrasta(img)
    return img


def mini_plano(k):
    nome, preco, por_vez, cats, cor, cor_tit, obs = PLANOS[k]
    c = bloco(290, 330, cor, raio=32, ow=7, sombra=11)
    cola(c, titulo(nome, 54 if nome != "PLATINUM" else 46, BRANCO, sw=5, sombra=5), 145, 70)
    cola(c, titulo(f"R$ {preco}", 66, cor_tit, sw=0, sombra=0), 145, 160)
    cola(c, texto("/mês", 28, cor_tit, 800), 145, 210)
    cola(c, texto(f"{por_vez} jogo{'s' if por_vez > 1 else ''}\npor vez", 32, cor_tit, 800), 145, 275)
    return c


def assine():
    img = fundo(W, H, 7)
    cola(img, logo(260), W / 2, 150, 2)
    cola(img, titulo("QUAL É O\nSEU PLANO?", 128, BRANCO), W / 2, 395, -2)
    xs = [205, 540, 875]
    for k in range(3):
        cola(img, mini_plano(k), xs[k], 760 + (0, -20, 0)[k], (-4, 0, 4)[k])
    cola(img, pilula("ASSINE PELO LINK NA BIO", 58, AMARELO, MARROM, pad=(40, 18), fonte_titulo=True), W / 2, 1035, -2)
    cola(img, texto("suavez.acervodejogos.com.br  ·  @suavez_bg", 34, MARROM, 800), W / 2, 1150)
    cola(img, texto("Retire em Mauá ou receba em casa", 32, PETROLEO, 800), W / 2, 1205)
    cola(img, dado(96, 6, LARANJA, BRANCO), 120, 1090, 14)
    cola(img, peao(130, PETROLEO), 965, 1080, -10)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    telas = [("01_capa", capa()), ("02_como_funciona", como_funciona()), ("03_silver", plano(0)),
             ("04_gold", plano(1)), ("05_platinum", plano(2)), ("06_assine", assine())]
    for nome, im in telas:
        im.convert("RGB").save(os.path.join(OUT, nome + ".png"))
    folha = Image.new("RGB", (3 * 540 + 40, 2 * 675 + 30), (255, 255, 255))
    for k, (_, im) in enumerate(telas):
        folha.paste(im.convert("RGB").resize((540, 675), Image.LANCZOS), (10 + (k % 3) * 550, 10 + (k // 3) * 685))
    folha.save(os.path.join(ROOT, "out", "carrossel_folha.jpg"), quality=90)
    print("ok")


if __name__ == "__main__":
    main()
