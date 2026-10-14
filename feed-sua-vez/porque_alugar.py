#!/usr/bin/env python3
"""Carrossel 1080x1350 "Por que alugar?" (pedido em 14/out/2026: "os carrosséis estão tendo boas visualizações").
Identidade das artes da Jéssica (assinatura-reels/estilo.py). Capa + 5 motivos + chamada.
Preços de loja = menor preço do Compara Jogos (lowPrice) em 14/10/2026; aluguel = preço do site por 5 dias.
Jogos escolhidos entre os que ainda apareceram pouco em posts (variar jogos entre posts).

    python3 porque_alugar.py      # out/porque_alugar/01..07.png (+ out/porque_alugar_folha.jpg)
"""
import os
import sys

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
from estilo import (MARROM, PETROLEO, LARANJA, AMARELO, BRANCO, titulo, texto, bloco, pilula, logo, jogo, dado, peao,  # noqa
                    fundo, cola, leque)

OUT = os.path.join(ROOT, "out", "porque_alugar")
W, H = 1080, 1350
_R = lambda *p: os.path.join(REPO, *p)  # noqa: E731
PRECOS = [  # (caixa oficial, nome, menor preço de loja em 14/10/2026, aluguel 5 dias)
    (_R("feed-posts/assets/critter_kitchen.png"), "Critter Kitchen", 283, 30),
    (_R("feed-posts/assets/victorian.png"), "Victorian Masterminds", 258, 30),
    (_R("feed-posts/assets/everdell_duo.png"), "Everdell Duo", 225, 30),
]
VARIADOS = [_R("roleta-reels/assets/unicorn_fever.png"), _R("roleta-reels/assets/wandering_towers.png"),
            _R("feed-posts/assets/monkey_palace.png"), _R("roleta-reels/assets/sheriff.png"),
            _R("feed-posts/assets/next_station.png"), _R("roleta-reels/assets/cartografos.png"),
            _R("roleta-reels/assets/art_society.png"), _R("feed-posts/assets/santa_kaos.png")]


def arrasta(img):
    cola(img, pilula("arrasta pro lado  →", 28, BRANCO, MARROM, pad=(22, 8), ow=4, sombra=5), W - 200, H - 92, -3)


def cabeca(img, n, tit):
    cola(img, pilula(f"MOTIVO {n}", 36, LARANJA, BRANCO, pad=(28, 10)), W / 2, 150, -3)
    cola(img, titulo(tit, 100, BRANCO, larg_max=940), W / 2, 330, -2)


def capa():
    img = fundo(W, H, 11)
    cola(img, logo(280), W / 2, 165, -2)
    cola(img, titulo("POR QUE\nALUGAR?", 170, BRANCO), W / 2, 480, -2)
    cola(img, pilula("5 MOTIVOS PRA JOGAR MAIS", 46, AMARELO, MARROM, pad=(34, 14), fonte_titulo=True), W / 2, 730, 2)
    cola(img, leque([p for p, *_ in PRECOS] + VARIADOS[:2], 300), W / 2, 1010)
    cola(img, dado(100, 4, AMARELO), 130, 175, -14)
    cola(img, peao(140, PETROLEO), 950, 170, 10)
    arrasta(img)
    return img


def linha_preco(p, nome, loja, alug):
    c = bloco(900, 215, BRANCO, raio=34)
    d = ImageDraw.Draw(c)
    cola(c, jogo(p, 185, 230), 140, 108, -4)
    cola(c, titulo(nome, 46, MARROM, BRANCO, sw=0, sombra=0, larg_max=560), 585, 52)
    cola(c, texto("nas lojas", 28, MARROM, 700), 440, 120)
    pr = titulo(f"R$ {loja}", 58, MARROM, BRANCO, sw=0, sombra=0)
    cola(c, pr, 440, 170)
    d.line((440 - pr.width / 2 + 8, 182, 440 + pr.width / 2 - 8, 158), fill=(214, 40, 40), width=8)  # riscado
    cola(c, texto("na Sua Vez", 28, PETROLEO, 800), 700, 120)
    cola(c, pilula(f"R$ {alug}", 48, PETROLEO, BRANCO, pad=(26, 8), fonte_titulo=True), 700, 172)
    return c


def motivo_caro():
    img = fundo(W, H, 12)
    cabeca(img, 1, "JOGO MODERNO\nÉ CARO")
    for k, row in enumerate(PRECOS):
        cola(img, linha_preco(*row), W / 2 + (-6, 8, -4)[k], 560 + k * 235, (-0.8, 0.8, -0.5)[k])
    cola(img, texto("Menor preço no Compara Jogos em 14/10/2026 · aluguel por 5 dias.", 26, MARROM, 600), W / 2, 1185)
    arrasta(img)
    return img


def motivo_teste():
    img = fundo(W, H, 13)
    cabeca(img, 2, "TESTE ANTES\nDE COMPRAR")
    card = bloco(860, 560, BRANCO, raio=40)
    cola(card, jogo(VARIADOS[2], 330, 330), 230, 290, -6)
    cola(card, texto("Ficou na dúvida se o jogo é a cara do seu grupo? Aluga, joga com a galera e só compra se amar.",
                     40, MARROM, 700, larg_max=420), 620, 230)
    cola(card, pilula("TESTADO E APROVADO!", 34, AMARELO, MARROM, pad=(24, 10)), 620, 440, -3)
    cola(img, card, W / 2, 800, 1)
    arrasta(img)
    return img


def motivo_variedade():
    img = fundo(W, H, 14)
    cabeca(img, 3, "UM JOGO NOVO\nTODA SEMANA")
    pos = [(230, 640, -6), (540, 610, 3), (850, 640, 6), (230, 960, 4), (540, 930, -3), (850, 960, -5)]
    for (x, y, r), p in zip(pos, VARIADOS[2:] + VARIADOS[:2]):
        cola(img, jogo(p, 250, 260), x, y, r)
    cola(img, pilula("163 JOGOS NO ACERVO", 56, AMARELO, MARROM, pad=(36, 14), fonte_titulo=True), W / 2, 1180, -2)
    arrasta(img)
    return img


def motivo_espaco():
    img = fundo(W, H, 15)
    cabeca(img, 4, "NADA DE JOGO\nPARADO NA ESTANTE")
    card = bloco(860, 520, BRANCO, raio=40)
    passos = [(1, "Jogou", AMARELO), (2, "Devolveu", LARANJA), (3, "Pegou outro", PETROLEO)]
    for k, (n, txt, cor) in enumerate(passos):
        x = 150 + k * 280
        cola(card, dado(150, n, cor, MARROM if cor == AMARELO else BRANCO), x, 180, (-8, 5, -4)[k])
        cola(card, titulo(txt, 46, MARROM, BRANCO, sw=0, sombra=0), x, 330)
    cola(card, texto("A estante não lota e a noite de jogos nunca fica repetida.", 36, MARROM, 700, larg_max=760),
         430, 440)
    cola(img, card, W / 2, 800, -1)
    arrasta(img)
    return img


def motivo_dias():
    img = fundo(W, H, 16)
    cabeca(img, 5, "QUANTO MAIS JOGOS,\nMAIS DIAS")
    for k, (jogos, dias, cor) in enumerate(((3, 7, AMARELO), (5, 10, LARANJA), (7, 15, PETROLEO))):
        hb = 300 + 110 * k
        c = bloco(270, hb, cor, raio=30, ow=7, sombra=11)
        ct = MARROM if cor == AMARELO else BRANCO
        cola(c, titulo(f"{jogos} JOGOS", 44, ct, sw=0, sombra=0), 135, 55)
        cola(c, titulo(str(dias), 130, ct, sw=0, sombra=0), 135, hb / 2 + 25)
        cola(c, titulo("DIAS", 46, ct, sw=0, sombra=0), 135, hb - 45)
        cola(img, c, 220 + k * 320, 1040 - hb / 2, 0)
    cola(img, texto("Pelo mesmo preço, pra todos os jogos do carrinho.", 36, MARROM, 800), W / 2, 1115)
    cola(img, pilula("OU ASSINE A PARTIR DE R$ 49/MÊS", 34, AMARELO, MARROM, pad=(26, 10)), W / 2, 1185, 2)
    arrasta(img)
    return img


def chamada():
    img = fundo(W, H, 17)
    cola(img, logo(300), W / 2, 200, 2)
    cola(img, titulo("BORA\nJOGAR?", 170, BRANCO), W / 2, 500, -2)
    cola(img, leque(VARIADOS[4:8], 260), W / 2, 830)
    cola(img, pilula("ALUGUE PELO LINK NA BIO", 56, AMARELO, MARROM, pad=(38, 16), fonte_titulo=True), W / 2, 1060, -2)
    cola(img, texto("Retire em Mauá ou receba em casa", 36, PETROLEO, 800), W / 2, 1160)
    cola(img, texto("suavez.acervodejogos.com.br  ·  @suavez_bg", 32, MARROM, 800), W / 2, 1215)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    telas = [capa(), motivo_caro(), motivo_teste(), motivo_variedade(), motivo_espaco(), motivo_dias(), chamada()]
    for k, im in enumerate(telas):
        im.convert("RGB").save(os.path.join(OUT, f"{k + 1:02d}.png"))
    folha = Image.new("RGB", (4 * 405 + 50, 2 * 506 + 30), (255, 255, 255))
    for k, im in enumerate(telas):
        folha.paste(im.convert("RGB").resize((405, 506), Image.LANCZOS), (10 + (k % 4) * 415, 10 + (k // 4) * 516))
    folha.save(os.path.join(ROOT, "out", "porque_alugar_folha.jpg"), quality=90)
    print("ok")


if __name__ == "__main__":
    main()
