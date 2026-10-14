#!/usr/bin/env python3
"""Carrossel 1080x1350 "Por que alugar?" — conceito próprio: CARTAS NA MANGA (14/out/2026).
Pedido: "gosto da forma, mas tá copia e cola dos outros, só mudou o fundo; quero algo mais diverso". Então cada motivo
é uma CARTA DE BARALHO gigante (índice no canto como carta de verdade, borda colorida, o resto do baralho aparecendo
atrás); capa = leque de cartas viradas; final = a carta com o logo. Fundo amarelo xadrez. Identidade da Jéssica
(fontes, marrom, contorno e sombra sólida) de assinatura-reels/estilo.py.
Preços de loja = menor preço do Compara Jogos (lowPrice) em 14/10/2026; aluguel = preço do site por 5 dias.

    python3 porque_alugar.py      # out/porque_alugar/01..07.png (+ out/porque_alugar_folha.jpg)
"""
import os
import sys
from functools import lru_cache

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
from estilo import (MARROM, PETROLEO, LARANJA, AMARELO, BRANCO, titulo, texto, bloco, pilula, logo, jogo, dado,  # noqa
                    fundo_xadrez, cola, lilita)

OUT = os.path.join(ROOT, "out", "porque_alugar")
W, H = 1080, 1350
CW, CH = 700, 980  # tamanho da carta
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
COR = {1: LARANJA, 2: PETROLEO, 3: (108, 63, 160), 4: (214, 64, 64), 5: PETROLEO}


@lru_cache(None)
def verso():
    """Verso das cartas: azul-petróleo com losangos e o logo no meio."""
    im = bloco(CW, CH, PETROLEO, raio=46, ow=8, sombra=14)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((34, 34, CW - 34, CH - 34), radius=30, outline=BRANCO, width=5)
    for y in range(80, CH - 60, 70):
        for x in range(80 + (35 if (y // 70) % 2 else 0), CW - 60, 70):
            d.polygon([(x, y - 16), (x + 12, y), (x, y + 16), (x - 12, y)], fill=(38, 142, 168))
    lg = logo(380)
    im.alpha_composite(lg, (int(CW / 2 - lg.width / 2), int(CH / 2 - lg.height / 2)))
    return im


def frente(n, tit):
    """Carta de frente: borda colorida, índice (número + dado) nos cantos, título no topo."""
    cor = COR[n]
    im = bloco(CW, CH, BRANCO, raio=46, ow=8, sombra=14)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((26, 26, CW - 26, CH - 26), radius=34, outline=cor, width=14)
    for canto in (0, 1):  # índice no canto, como carta de verdade
        idx = Image.new("RGBA", (80, 125), (0, 0, 0, 0))
        ImageDraw.Draw(idx).text((40, 36), str(n), font=lilita(68), fill=cor, anchor="mm")
        idx.alpha_composite(dado(42, n, cor, BRANCO), (17, 74))
        if canto:
            idx = idx.rotate(180)
            im.alpha_composite(idx, (CW - 50 - idx.width, CH - 48 - idx.height))
        else:
            im.alpha_composite(idx, (50, 46))
    cola(im, titulo(tit, 64, BRANCO, contorno=MARROM, larg_max=440), CW / 2 + 25, 190)
    return im


def baralho(img, carta, cx, cy, rot, atras=2):
    """O resto do baralho (versos) aparecendo atrás da carta principal."""
    for k in range(atras, 0, -1):
        cola(img, verso(), cx + 26 * k, cy - 14 * k, rot + 5 * k)
    cola(img, carta, cx, cy, rot)


def rodape(img, txt="arrasta pra virar a próxima carta  →"):
    cola(img, pilula(txt, 26, BRANCO, MARROM, pad=(20, 8), ow=4, sombra=5), W / 2, H - 70, -1)


def capa():
    img = fundo_xadrez(W, H)
    cola(img, logo(250), 150, 120, -6)
    cola(img, titulo("POR QUE\nALUGAR?", 150, BRANCO), W / 2 + 60, 290, -3)
    for k in range(5):  # leque de cartas viradas
        a = (k - 2) * 13
        cola(img, verso().resize((int(CW * 0.62), int(CH * 0.62)), Image.LANCZOS), W / 2 + (k - 2) * 120,
             920 + abs(k - 2) * 40, -a)
    cola(img, pilula("5 CARTAS NA MANGA PRA VOCÊ JOGAR MAIS", 38, BRANCO, MARROM, pad=(28, 12), fonte_titulo=True),
         W / 2, 560, 2)
    rodape(img, "arrasta pra virar a primeira  →")
    return img


def carta_caro():
    c = frente(1, "JOGO MODERNO\nÉ CARO")
    for k, (p, nome, loja, alug) in enumerate(PRECOS):
        y = 395 + k * 170
        cola(c, jogo(p, 135, 150), 175, y, (-5, 4, -3)[k])
        cola(c, texto(nome, 30, MARROM, 800), 445, y - 48)
        pr = titulo(f"R$ {loja}", 46, MARROM, BRANCO, sw=0, sombra=0)
        cola(c, pr, 365, y + 8)
        ImageDraw.Draw(c).line((365 - pr.width / 2 + 6, y + 18, 365 + pr.width / 2 - 6, y - 2), fill=(214, 40, 40),
                               width=7)
        cola(c, pilula(f"R$ {alug}", 40, PETROLEO, BRANCO, pad=(18, 6), ow=4, sombra=5, fonte_titulo=True), 540, y + 8)
    cola(c, texto("nas lojas × na Sua Vez (5 dias)", 26, MARROM, 700), CW / 2 - 20, 860)
    return c


def carta_teste():
    c = frente(2, "TESTE ANTES\nDE COMPRAR")
    cola(c, jogo(VARIADOS[2], 320, 360), CW / 2, 470, -4)
    cola(c, texto("Aluga, joga com a galera e só compra se amar.", 38, MARROM, 800, larg_max=520), CW / 2, 745)
    cola(c, pilula("TESTADO E APROVADO!", 32, AMARELO, MARROM, pad=(22, 8)), CW / 2 - 20, 850, -3)
    return c


def carta_variedade():
    c = frente(3, "UM JOGO NOVO\nTODA SEMANA")
    for k, p in enumerate(VARIADOS[2:8]):
        cola(c, jogo(p, 150, 165), 185 + (k % 3) * 165, 390 + (k // 3) * 200, (-5, 3, 6, 4, -4, -2)[k])
    cola(c, titulo("163 JOGOS", 78, COR[3], sw=6, sombra=6), CW / 2, 760)
    cola(c, texto("no acervo da Sua Vez", 32, MARROM, 800), CW / 2, 840)
    return c


def carta_estante():
    c = frente(4, "NADA PARADO\nNA ESTANTE")
    for k, (n, txt) in enumerate(((1, "Jogou"), (2, "Devolveu"), (3, "Pegou outro"))):
        y = 370 + k * 150
        cola(c, dado(110, n, (AMARELO, LARANJA, PETROLEO)[k], MARROM if k == 0 else BRANCO), 220, y, (-8, 5, -4)[k])
        cola(c, titulo(txt, 56, MARROM, BRANCO, sw=0, sombra=0), 430, y)
    cola(c, texto("A estante não lota e a noite de jogos nunca repete.", 32, MARROM, 800, larg_max=440), CW / 2 - 25, 815)
    return c


def carta_dias():
    c = frente(5, "MAIS JOGOS,\nMAIS DIAS")
    for k, (jogos, dias, cor) in enumerate(((3, 7, AMARELO), (5, 10, LARANJA), (7, 15, PETROLEO))):
        hb = 210 + 80 * k
        b = bloco(160, hb, cor, raio=24, ow=6, sombra=9)
        ct = MARROM if cor == AMARELO else BRANCO
        cola(b, texto(f"{jogos} jogos", 28, ct, 900), 80, 32)
        cola(b, titulo(str(dias), 90, ct, sw=0, sombra=0), 80, hb / 2 + 12)
        cola(b, texto("dias", 28, ct, 900), 80, hb - 32)
        cola(c, b, 175 + k * 180, 720 - hb / 2, 0)
    cola(c, texto("Mesmo preço, pra todos os jogos do carrinho. Ou assine a partir de R$ 49/mês.", 28, MARROM, 800,
                  larg_max=430), CW / 2 - 25, 828)
    return c


def final():
    img = fundo_xadrez(W, H)
    cola(img, titulo("BORA JOGAR?", 130, BRANCO), W / 2, 150, -3)
    c = bloco(CW, CH - 160, BRANCO, raio=46, ow=8, sombra=14)
    ImageDraw.Draw(c).rounded_rectangle((26, 26, CW - 26, CH - 186), radius=34, outline=PETROLEO, width=14)
    cola(c, logo(360), CW / 2, 190, -2)
    cola(c, pilula("ALUGUE PELO LINK NA BIO", 46, AMARELO, MARROM, pad=(30, 14), fonte_titulo=True), CW / 2, 400, -2)
    cola(c, texto("Retire em Mauá ou receba em casa", 36, MARROM, 800), CW / 2, 510)
    cola(c, texto("suavez.acervodejogos.com.br", 32, PETROLEO, 800), CW / 2, 580)
    cola(c, texto("@suavez_bg", 40, MARROM, 900), CW / 2, 650)
    baralho(img, c, W / 2 - 30, 790, 2, atras=3)
    return img


def tela_carta(carta, n):
    img = fundo_xadrez(W, H)
    baralho(img, carta, W / 2 - 20, 640, (-3, 2.5, -2, 3, -2.5)[n - 1])
    rodape(img)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    cartas = [carta_caro(), carta_teste(), carta_variedade(), carta_estante(), carta_dias()]
    telas = [capa()] + [tela_carta(c, k + 1) for k, c in enumerate(cartas)] + [final()]
    for k, im in enumerate(telas):
        im.convert("RGB").save(os.path.join(OUT, f"{k + 1:02d}.png"))
    folha = Image.new("RGB", (4 * 405 + 50, 2 * 506 + 30), (255, 255, 255))
    for k, im in enumerate(telas):
        folha.paste(im.convert("RGB").resize((405, 506), Image.LANCZOS), (10 + (k % 4) * 415, 10 + (k // 4) * 516))
    folha.save(os.path.join(ROOT, "out", "porque_alugar_folha.jpg"), quality=90)
    print("ok")


if __name__ == "__main__":
    main()
