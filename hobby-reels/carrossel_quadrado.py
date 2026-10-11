#!/usr/bin/env python3
"""Mesmo carrossel do carrossel.py (8 telas, estante de madeira + etiquetas kraft), no formato QUADRADO 1080 x 1080
para post no feed (pedido dele). As telas são as mesmas, só reposicionadas para caber no quadrado.

    python3 carrossel_quadrado.py      # out/carrossel_1x1/01.png ... 08.png e todas.jpg
"""
import os

from PIL import Image, ImageDraw

import carrossel as C
import ludoteca as L
from ludoteca import ORANGE, ORANGE_D, NAVY, WHITE, GREEN, BLUE, POPB, SEMI, font, cola, titulo, kraft, preco, icone, logo_card

C.H = 1080  # fundo() e marca() usam o H do carrossel
W, H = C.W, C.H
OUT = os.path.join(L.OUT, "carrossel_1x1")
caixa, fundo, prateleira = C.caixa, C.fundo, C.prateleira


def tres(img, itens, y_caixa=570, h=270, y_tab=725):
    """3 caixas lado a lado com ícone, tag e subtítulo (telas 3 e 4)."""
    for k, (n, tag, sub, cor, ic) in enumerate(itens):
        x = 190 + k * 350
        cola(img, caixa(n, h), x, y_caixa)
        cola(img, icone(ic, 42, cor), x, y_tab + 75)
        d = ImageDraw.Draw(img)
        d.text((x, y_tab + 148), tag, font=font(POPB, 42), fill=WHITE, anchor="mm", stroke_width=5, stroke_fill=NAVY)
        d.text((x, y_tab + 196), sub, font=font(SEMI, 30), fill=(250, 235, 215), anchor="mm")
    L.prateleira(ImageDraw.Draw(img), y_tab, 0, W)


def s1():
    img = fundo()
    prateleira(img, 990, ["vudu", "arquitetos", "marvel", "gravity"], 250)
    cola(img, titulo("JOGO DE TABULEIRO\nÉ SÓ BANCO\nIMOBILIÁRIO?", 92, WHITE, NAVY), 540, 330, -2)
    cola(img, kraft("Conheça os jogos modernos", 48), 540, 600, 2)
    return img


def s2():
    img = fundo(0.35)
    prateleira(img, 1000, ["sintonia", "draft", "scooby"], 270)
    cola(img, titulo("TEM PRA TODO\nTIPO DE GENTE", 90, WHITE, ORANGE_D), 540, 210, -2)
    itens = [("regras", "Regras simples ou complexas", ORANGE), ("relogio", "Partidas de 15 min ou de 2 horas", BLUE)]
    for k, (ic, txt, cor) in enumerate(itens):
        y = 420 + k * 130
        cola(img, kraft(txt, 42), 580, y, (-1) ** k * 1.5)
        cola(img, icone(ic, 48, cor), 110, y + 28)
    return img


def s3():
    img = fundo(0.35)
    cola(img, titulo("ESCOLHA O\nSEU ESTILO", 92, WHITE, ORANGE_D), 540, 200, -2)
    tres(img, [("sintonia", "FESTA", "pra dar risada", ORANGE, "risada"),
               ("marvel", "COOPERATIVO", "todo mundo junto", BLUE, "maos"),
               ("arquitetos", "ESTRATÉGIA", "pra fritar a cuca", GREEN, "cerebro")])
    return img


def s4():
    img = fundo(0.35)
    cola(img, titulo("E TEM JOGO PRA\nCASAL E ATÉ SOLO", 86, WHITE, ORANGE_D), 540, 205, -2)
    tres(img, [("gravity", "FAMÍLIA", "a partir de 7 anos", ORANGE, "coracao"),
               ("draft", "PRA DOIS", "perfeito pro casal", BLUE, "todos"),
               ("finalgirl", "SOLO", "pra jogar sozinho", GREEN, "pessoa")])
    return img


def s5():
    img = fundo(0.45)
    cola(img, titulo("MAS JOGO MODERNO\nCOSTUMA SER CARO...", 82, WHITE, NAVY), 540, 200, -2)
    cola(img, caixa("hotstreak", 220), 540, 485, -3)
    cola(img, preco("NA LOJA", "R$ 279", (150, 40, 40), 380, True), 300, 750, -6)
    cola(img, preco("NA SUA VEZ", "R$ 30", GREEN, 380), 790, 750, 5)
    cola(img, kraft("por 5 dias de jogo", 40), 790, 870, 2)
    ImageDraw.Draw(img).text((380, 985), "Hot Streak: a partir de R$ 279 nas lojas (Compara Jogos, out/2026)",
                             font=font(SEMI, 20), fill=(235, 220, 200), anchor="mm")
    return img


def s6():
    img = fundo(0.35)
    prateleira(img, 1000, ["xmen", "deadpool", "spider"], 260)
    cola(img, titulo("POR ISSO\nALUGAR FAZ\nTANTO SENTIDO", 88, WHITE, ORANGE_D), 540, 250, -2)
    for k, (ic, txt) in enumerate([("ok", "Joga 5 dias com a galera"), ("coracao", "Gostou? Compra sem medo de errar")]):
        y = 520 + k * 130
        cola(img, kraft(txt, 42), 580, y, (-1) ** k * 1.5)
        cola(img, icone(ic, 48, GREEN if k == 0 else ORANGE), 110, y + 28)
    return img


def s7():
    img = fundo(0.5)
    cola(img, titulo("QUANTO MAIS JOGOS,\nMAIS DIAS!", 80, WHITE, ORANGE_D), 540, 210, -2)
    base = 850
    for k in range(len(L.DEGRAUS)):
        g = L.degrau(k)
        g = g.resize((int(g.width * 0.78), int(g.height * 0.78)), Image.LANCZOS)
        x = 220 + k * 320
        img.alpha_composite(g, (int(x - g.width / 2), int(base - g.height + 33)))
    L.prateleira(ImageDraw.Draw(img), base, 0, W)
    cola(img, kraft("Vale pra todo o carrinho, pelo mesmo preço!", 32), 440, 918, 0)
    return img


def s8():
    img = fundo(0.4)
    cola(img, logo_card(340), 540, 170)
    prateleira(img, 590, ["gravity", "scooby", "finalgirl", "arquitetos"], 230)
    cola(img, titulo("ALUGUE NA SUA VEZ!", 84, WHITE, ORANGE_D), 540, 685, -2)
    d = ImageDraw.Draw(img)
    for k, (txt, cor) in enumerate([("RESERVE ONLINE · RETIRE EM MAUÁ", WHITE), ("OU RECEBA EM CASA", (134, 239, 172)),
                                    ("LINK NA BIO · @SUAVEZ_BG", (255, 190, 120))]):
        d.text((540, 790 + k * 58), txt, font=font(POPB, 40), fill=cor, anchor="mm", stroke_width=4, stroke_fill=NAVY)
    cola(img, kraft("Qual você jogaria primeiro? Comenta!", 36), 540, 1000, -2)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    ims = []
    for n, fn in enumerate([s1, s2, s3, s4, s5, s6, s7, s8], 1):
        im = fn()
        C.marca(im, n)
        im = im.convert("RGB")
        im.save(os.path.join(OUT, f"{n:02d}.png"))
        ims.append(im)
    folha = Image.new("RGB", (4 * 540, 2 * 540))
    for k, im in enumerate(ims):
        folha.paste(im.resize((540, 540), Image.LANCZOS), ((k % 4) * 540, (k // 4) * 540))
    folha.save(os.path.join(OUT, "todas.jpg"), quality=88)
    print("ok", len(ims), ims[0].size)


if __name__ == "__main__":
    main()
