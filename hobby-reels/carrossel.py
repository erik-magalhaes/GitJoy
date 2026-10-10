#!/usr/bin/env python3
"""Carrossel para o feed (8 telas 1080 x 1350) com o conteúdo do Reels "o que são jogos modernos", no mesmo visual
da estante de madeira e das etiquetas kraft. Caixas: só fotos OFICIAIS que já temos no projeto (nada de recorte do site).

    python3 carrossel.py      # out/carrossel/01.png ... 08.png e out/carrossel/todas.jpg (folha de conferência)
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

import ludoteca as L
from ludoteca import (ORANGE, ORANGE_D, NAVY, WHITE, GREEN, BLUE, KRAFT, INK, POP, POPB, SEMI, font, sombra, cola,
                      titulo, kraft, preco, icone, logo_card)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(L.OUT, "carrossel")
W, H = 1080, 1350
CX = {  # caixas oficiais
    "sintonia": "sintonia-reels/assets/pieces/box.png",
    "arquitetos": "architects-reels/assets/oficial/caixa3d.png",
    "vudu": "voodoo-reels/assets/pieces/box.png",
    "marvel": "marvel-reels/assets/caixas/base.png",
    "xmen": "marvel-reels/assets/caixas/xmen.png",
    "deadpool": "marvel-reels/assets/caixas/deadpool.png",
    "spider": "marvel-reels/assets/caixas/spider_geddon.png",
    "finalgirl": "finalgirl-reels/assets/recortes/caixa_hans.png",
    "fgbase": "finalgirl-reels/assets/recortes/caixa_base.png",
    "cuckoo": "gravados-reels/assets/oficial/go_cuckoo.png",
    "draft": "gravados-reels/assets/oficial/draftosaurus.png",
    "gravity": "gravados-reels/assets/oficial/gravity_superstar.png",
    "scooby": "gravados-reels/assets/oficial/scooby_doo.png",
    "hotstreak": "hotstreak-reels/assets/pecas/caixa.png",
}


def caixa(nome, h):
    im = Image.open(os.path.join(REPO, CX[nome])).convert("RGBA")
    im = im.crop(im.getbbox())
    if nome == "scooby":  # capa reta: cantos arredondados
        m = Image.new("L", im.size, 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=im.width // 40, fill=255)
        im.putalpha(m)
    im = im.resize((int(im.width * h / im.height), int(h)), Image.LANCZOS)
    return sombra(im, 12, (8, 14), 0.55)


def fundo(escuro=0.0):
    """Parede de madeira com luz quente vinda de cima (igual ao vídeo)."""
    img = L.parede().crop((0, 0, W, H)).copy()
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ov).ellipse((-300, -450, W + 300, 800), fill=(255, 200, 120, 50))
    img.alpha_composite(ov.filter(ImageFilter.GaussianBlur(90)))
    if escuro:
        img.alpha_composite(Image.new("RGBA", (W, H), (20, 10, 5, int(170 * escuro))))
    return img


def prateleira(img, y, caixas, h=300, rot=0):
    """Fileira de caixas apoiadas numa prateleira de madeira em y."""
    ims = [caixa(n, h) for n in caixas]
    tot = sum(i.width for i in ims) - 40 * (len(ims) - 1)
    x = (W - tot) / 2
    for k, im in enumerate(ims):
        img.alpha_composite(im, (int(x), int(y - im.height + 22)))
        x += im.width - 40
    L.prateleira(ImageDraw.Draw(img), y, 0, W)


def marca(img, n):
    """Logo pequeno no canto + 'n/8' e a setinha de arrastar (menos na última)."""
    lg = logo_card(150)
    img.alpha_composite(lg, (W - lg.width - 34, 34))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((34, 44, 150, 104), radius=30, fill=(0, 0, 0, 120))
    d.text((92, 74), f"{n}/8", font=font(POP, 32), fill=WHITE, anchor="mm")
    if n < 8:  # etiqueta "arrasta" com setinha desenhada (a fonte não tem o símbolo →)
        k = kraft("arrasta      ", 34).copy()
        dk = ImageDraw.Draw(k)
        cy = k.height / 2 + 14
        x1 = k.width - 58
        dk.polygon([(x1, cy - 13), (x1 + 22, cy), (x1, cy + 13)], fill=INK)
        dk.line((x1 - 26, cy, x1 + 4, cy), fill=INK, width=6)
        cola(img, k, W - 160, H - 92, -3)


def s1():
    img = fundo()
    prateleira(img, 1210, ["vudu", "arquitetos", "marvel", "gravity"], 300)
    cola(img, titulo("JOGO DE TABULEIRO\nÉ SÓ BANCO\nIMOBILIÁRIO?", 104, WHITE, NAVY), 540, 400, -2)
    cola(img, kraft("Conheça os jogos modernos", 52), 540, 690, 2)
    return img


def s2():
    img = fundo(0.35)
    prateleira(img, 1210, ["sintonia", "draft", "scooby"], 330)
    cola(img, titulo("TEM PRA TODO\nTIPO DE GENTE", 100, WHITE, ORANGE_D), 540, 260, -2)
    itens = [("regras", "Regras simples ou complexas", ORANGE), ("relogio", "Partidas de 15 min ou de 2 horas", BLUE)]
    for k, (ic, txt, cor) in enumerate(itens):
        y = 520 + k * 150
        cola(img, kraft(txt, 44), 580, y, (-1) ** k * 1.5)
        cola(img, icone(ic, 52, cor), 110, y + 30)
    return img


def s3():
    img = fundo(0.35)
    cola(img, titulo("ESCOLHA O\nSEU ESTILO", 104, WHITE, ORANGE_D), 540, 230, -2)
    tipos = [("sintonia", "FESTA", "pra dar risada", ORANGE, "risada"),
             ("marvel", "COOPERATIVO", "todo mundo junto", BLUE, "maos"),
             ("arquitetos", "ESTRATÉGIA", "pra fritar a cuca", GREEN, "cerebro")]
    for k, (n, tag, sub, cor, ic) in enumerate(tipos):
        x = 190 + k * 350
        b = caixa(n, 330)
        cola(img, b, x, 760)
        L.prateleira(ImageDraw.Draw(img), 940, 0, W) if k == 0 else None
        cola(img, icone(ic, 48, cor), x, 1040)
        d = ImageDraw.Draw(img)
        d.text((x, 1125), tag, font=font(POPB, 46), fill=WHITE, anchor="mm", stroke_width=5, stroke_fill=NAVY)
        d.text((x, 1180), sub, font=font(SEMI, 32), fill=(250, 235, 215), anchor="mm")
    return img


def s4():
    img = fundo(0.35)
    cola(img, titulo("E TEM JOGO PRA\nCASAL E ATÉ SOLO", 96, WHITE, ORANGE_D), 540, 240, -2)
    itens = [("gravity", "FAMÍLIA", "a partir de 7 anos", "coracao", ORANGE),  # Go Cuckoo saiu (ele achou amassado)
             ("draft", "PRA DOIS", "perfeito pro casal", "todos", BLUE),
             ("finalgirl", "SOLO", "pra jogar sozinho", "pessoa", GREEN)]
    for k, (n, tag, sub, ic, cor) in enumerate(itens):
        x = 190 + k * 350
        cola(img, caixa(n, 330), x, 760)
        cola(img, icone(ic, 48, cor), x, 1040)
        d = ImageDraw.Draw(img)
        d.text((x, 1125), tag, font=font(POPB, 46), fill=WHITE, anchor="mm", stroke_width=5, stroke_fill=NAVY)
        d.text((x, 1180), sub, font=font(SEMI, 32), fill=(250, 235, 215), anchor="mm")
    L.prateleira(ImageDraw.Draw(img), 940, 0, W)
    return img


def s5():
    img = fundo(0.45)
    cola(img, titulo("MAS JOGO MODERNO\nCOSTUMA SER CARO...", 92, WHITE, NAVY), 540, 240, -2)
    cola(img, caixa("hotstreak", 260), 540, 590, -3)
    cola(img, preco("NA LOJA", "R$ 279", (150, 40, 40), 420, True), 300, 930, -6)
    cola(img, preco("NA SUA VEZ", "R$ 30", GREEN, 420), 790, 930, 5)
    cola(img, kraft("por 5 dias de jogo", 42), 790, 1090, 2)
    d = ImageDraw.Draw(img)
    d.text((470, 1190), "Hot Streak: a partir de R$ 279 nas lojas (Compara Jogos, out/2026)", font=font(SEMI, 24),
           fill=(235, 220, 200), anchor="mm")
    return img


def s6():
    img = fundo(0.35)
    prateleira(img, 1210, ["xmen", "deadpool", "spider"], 320)
    cola(img, titulo("POR ISSO\nALUGAR FAZ\nTANTO SENTIDO", 100, WHITE, ORANGE_D), 540, 300, -2)
    passos = [("ok", "Joga 5 dias com a galera"), ("coracao", "Gostou? Compra sem medo de errar")]
    for k, (ic, txt) in enumerate(passos):
        y = 610 + k * 150
        cola(img, kraft(txt, 44), 580, y, (-1) ** k * 1.5)
        cola(img, icone(ic, 52, GREEN if k == 0 else ORANGE), 110, y + 30)
    return img


def s7():
    img = fundo(0.5)
    cola(img, titulo("QUANTO MAIS JOGOS,\nMAIS DIAS!", 88, WHITE, ORANGE_D), 540, 250, -2)
    base = 1130
    for k, (jogos, dias, cor) in enumerate(L.DEGRAUS):
        g = L.degrau(k)
        g = g.resize((int(g.width * 0.95), int(g.height * 0.95)), Image.LANCZOS)
        x = 220 + k * 320
        img.alpha_composite(g, (int(x - g.width / 2), int(base - g.height + 40)))
    L.prateleira(ImageDraw.Draw(img), base, 0, W)
    cola(img, kraft("Vale pra todo o carrinho, pelo mesmo preço!", 36), 470, 1188, 0)
    return img


def s8():
    img = fundo(0.4)
    cola(img, logo_card(430), 540, 230)
    prateleira(img, 760, ["gravity", "scooby", "finalgirl", "arquitetos"], 280)
    cola(img, titulo("ALUGUE NA SUA VEZ!", 96, WHITE, ORANGE_D), 540, 870, -2)
    d = ImageDraw.Draw(img)
    linhas = [("RESERVE ONLINE · RETIRE EM MAUÁ", WHITE), ("OU RECEBA EM CASA", (134, 239, 172)),
              ("LINK NA BIO · @SUAVEZ_BG", (255, 190, 120))]
    for k, (txt, cor) in enumerate(linhas):
        d.text((540, 990 + k * 66), txt, font=font(POPB, 46), fill=cor, anchor="mm", stroke_width=4, stroke_fill=NAVY)
    cola(img, kraft("Qual você jogaria primeiro? Comenta!", 40), 540, 1230, -2)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    telas = [s1, s2, s3, s4, s5, s6, s7, s8]
    ims = []
    for n, fn in enumerate(telas, 1):
        im = fn()
        marca(im, n)
        im = im.convert("RGB")
        im.save(os.path.join(OUT, f"{n:02d}.png"))
        ims.append(im)
    folha = Image.new("RGB", (4 * 540, 2 * 675))
    for k, im in enumerate(ims):
        folha.paste(im.resize((540, 675), Image.LANCZOS), ((k % 4) * 540, (k // 4) * 675))
    folha.save(os.path.join(OUT, "todas.jpg"), quality=88)
    print("ok", len(ims))


if __name__ == "__main__":
    main()
