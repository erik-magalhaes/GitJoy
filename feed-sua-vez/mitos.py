#!/usr/bin/env python3
"""Carrossel 1080x1350 "6 MITOS SOBRE JOGOS DE TABULEIRO" (28/out/2026). Conceito próprio: MURAL DE CORTIÇA.
Cada mito é um post-it preso com tachinha e carimbado de vermelho "MITO!"; embaixo, uma ficha pautada com "A VERDADE" e
a caixa OFICIAL de um jogo do acervo que derruba o mito (jogadores, tempo e preço do site). Moldura de madeira.
Identidade da Jéssica (fontes, marrom, contorno e sombra sólida; assinatura-reels/estilo.py).

    python3 mitos.py      # out/mitos/01..08.png (+ out/mitos_folha.jpg)
"""
import json
import os
import random
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
from estilo import (MARROM, PETROLEO, LARANJA, AMARELO, BRANCO, titulo, texto, bloco, pilula, logo, jogo, cola,  # noqa
                    lilita, fig)

OUT = os.path.join(ROOT, "out", "mitos")
W, H = 1080, 1350
VERMELHO = (205, 38, 38)
POSTIT = [(255, 222, 89), (255, 170, 190), (160, 220, 240), (190, 232, 150)]
ACERVO = os.path.join(REPO, "hobby-reels", "assets", "acervo")
SITE = json.load(open(os.path.join(REPO, "comum", "dados", "acervo_site.json"), encoding="utf-8"))
MITOS = [  # (mito, verdade, nome no site, recorte, nome na tela)
    ("“Jogo de tabuleiro\né coisa de criança.”",
     "Tem jogo de investigação, de estratégia e até de terror pra adulto. No Detective, vocês resolvem crimes como numa "
     "série policial.", "Detective: A Modern Crime Board Game", "detective_a_modern_crime_board_game", "Detective"),
    ("“É difícil demais\nde aprender.”",
     "Tem jogo que se explica em 5 minutos e já dá pra sair jogando. Coup é blefe puro: só precisa mentir bem.",
     "Coup: Inquisition", "coup_inquisition", "Coup"),
    ("“Uma partida\ndemora horas.”",
     "Muitos jogos duram 15 minutos: dá pra jogar várias partidas na mesma noite.",
     "BraveRats", "braverats", "BraveRats"),
    ("“Precisa juntar\nmuita gente.”",
     "Tem jogo pra 2, pra casal e até pra jogar sozinho. O Cartógrafos vai de 1 a 100 jogadores!",
     "Cartographers", "cartographers", "Cartógrafos"),
    ("“Todo jogo acaba\nem briga.”",
     "Nos cooperativos, todo mundo joga JUNTO contra o próprio jogo: ganha ou perde a mesa inteira.",
     "The Goonies: Never Say Die", "the_goonies_never_say_die", "The Goonies"),
    ("“Pra jogar jogo bom,\ntem que gastar muito.”",
     "Na Sua Vez você aluga a partir de R$ 15 por 5 dias e testa antes de pensar em comprar.",
     "Bohnanza", "bohnanza", "Bohnanza"),
]


def ficha(nome):
    v = SITE[nome]
    a, b = v["jogadores"].split("–")
    jog = f"{a} jogadores" if a == b else f"{a} a {b} jogadores"
    return f"{jog} · {v['tempo'].replace('min', ' min')} · R$ {v['preco']} por 5 dias"


def fundo():
    return _cortica().copy()


@lru_cache(None)
def _cortica():
    """Cortiça (pontinhos claros e escuros) dentro de uma moldura de madeira."""
    rng = np.random.default_rng(7)
    a = np.ones((H, W, 3)) * np.array([196, 148, 96], float)
    a += rng.normal(0, 9, (H, W, 1))
    for cor, n, r in (((150, 104, 62), 2600, 3), ((222, 182, 130), 2200, 2), ((128, 86, 50), 900, 2)):
        ys, xs = rng.integers(0, H, n), rng.integers(0, W, n)
        for y, x in zip(ys, xs):
            a[max(0, y - r):y + r, max(0, x - r):x + r] = cor
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)).convert("RGBA")
    d = ImageDraw.Draw(img)
    m = 34
    d.rectangle((0, 0, W, m), fill=(120, 74, 40))
    d.rectangle((0, H - m, W, H), fill=(120, 74, 40))
    d.rectangle((0, 0, m, H), fill=(138, 86, 48))
    d.rectangle((W - m, 0, W, H), fill=(138, 86, 48))
    d.rectangle((m, m, W - m, H - m), outline=MARROM, width=6)
    return img


def tachinha(img, x, y, cor=VERMELHO):
    d = ImageDraw.Draw(img)
    d.ellipse((x - 20 + 6, y - 20 + 8, x + 20 + 6, y + 20 + 8), fill=(0, 0, 0, 90))
    d.ellipse((x - 20, y - 20, x + 20, y + 20), fill=cor, outline=MARROM, width=4)
    d.ellipse((x - 9, y - 12, x + 1, y - 2), fill=(255, 255, 255, 170))


def postit(txt, w, h, cor, s=64):
    im = Image.new("RGBA", (w + 24, h + 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(14, 16), (w + 14, 10), (w + 18, h + 20), (18, h + 14)], fill=(60, 36, 18, 110))  # sombra
    d.rectangle((0, 0, w, h), fill=cor)
    d.rectangle((0, 0, w, 46), fill=tuple(max(0, c - 18) for c in cor))  # faixa da cola
    tx = titulo(txt, s, MARROM, MARROM, sw=0, sombra=0, larg_max=w - 70)
    im.alpha_composite(tx, ((w - tx.width) // 2, 46 + (h - 46 - tx.height) // 2))
    return im


@lru_cache(None)
def carimbo(txt="MITO!", s=150):
    """Carimbo de borracha vermelho, meio falhado."""
    f = lilita(s)
    tw = ImageDraw.Draw(Image.new("L", (1, 1))).textlength(txt, font=f)
    w, h = int(tw + 90), int(s * 1.3)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 8, w - 8, h - 8), radius=26, outline=VERMELHO, width=14)
    d.text((w / 2, h / 2 + 6), txt, font=f, fill=VERMELHO, anchor="mm")
    rng = np.random.default_rng(3)  # falhas da tinta
    a = np.asarray(im.getchannel("A")).astype(float)
    a *= np.clip(rng.uniform(0.55, 1.15, a.shape), 0, 1)
    buracos = rng.random(a.shape) < 0.04
    a[buracos] = 0
    im.putalpha(Image.fromarray(a.astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)))
    return im


def cartao_verdade(verdade, nome_site, recorte, nome, w=900, h=620):
    """Ficha pautada branca: A VERDADE + texto + caixa do jogo + ficha do site."""
    im = bloco(w, h, BRANCO, raio=10, ow=5, sombra=12)
    d = ImageDraw.Draw(im)
    for y in range(130, h - 20, 52):
        d.line((26, y, w - 26, y), fill=(200, 222, 236), width=3)
    d.line((110, 20, 110, h - 20), fill=(240, 150, 150), width=3)
    cola(im, pilula("A VERDADE:", 46, (40, 140, 80), BRANCO, pad=(26, 10), fonte_titulo=True), 270, 70, -2)
    tx = texto(verdade, 37, MARROM, 800, larg_max=440, entre=1.37, alinha="lm")
    cola(im, tx, 135 + tx.width / 2, 300)  # texto à esquerda, nunca invade a caixa
    cx = jogo(os.path.join(ACERVO, recorte + ".png"), 310, 250)
    cola(im, cx, w - 150, 280, 4)
    cola(im, pilula(nome, 36, AMARELO, MARROM, pad=(22, 8), fonte_titulo=True), w - 150, 470, -3)
    cola(im, texto(ficha(nome_site), 30, PETROLEO, 800), w / 2 + 20, h - 60)
    return im


def tela_mito(k, mito, verdade, nome_site, recorte, nome):
    img = fundo()
    rnd = random.Random(k)
    cola(img, pilula(f"MITO Nº {k}", 40, MARROM, BRANCO, pad=(24, 10), fonte_titulo=True), 190, 100, -4)
    rot = rnd.choice((-4, -3, 3, 4))
    cola(img, postit(mito, 760, 380, POSTIT[(k - 1) % 4]), W / 2, 360, rot)
    tachinha(img, W / 2, 180)
    cola(img, cartao_verdade(verdade, nome_site, recorte, nome), W / 2, 935, rnd.choice((-1.5, 1.5)))
    tachinha(img, 140, 650, PETROLEO)
    tachinha(img, W - 140, 650, PETROLEO)
    cola(img, carimbo("MITO!", 110), 760, 580, -12)  # por cima, no canto do post-it (sem cobrir a frase)
    cola(img, pilula("arrasta pro próximo mito  →" if k < len(MITOS) else "arrasta  →", 32, BRANCO, MARROM,
                     pad=(24, 9), ow=5, sombra=6), W / 2, H - 60)
    return img


def capa():
    img = fundo()
    cola(img, logo(250), W - 190, 120, 3)
    for k, (x, y, r) in enumerate([(250, 330, -8), (790, 420, 7), (300, 860, 6), (810, 980, -6)]):
        im = Image.new("RGBA", (320, 320), POSTIT[k] + (255,))
        cola(img, im, x, y, r)
        tachinha(img, x + 4, y - 140)
    cola(img, titulo("6 MITOS", 190, BRANCO), W / 2, 520, -4)
    cola(img, titulo("sobre jogos de\ntabuleiro", 104, AMARELO), W / 2, 760, 2)
    cola(img, carimbo("MITO!", 120), 760, 1000, -14)
    cola(img, pilula("que a gente vai derrubar agora  →", 40, BRANCO, MARROM, pad=(30, 12)), W / 2, 1150, -2)
    return img


def final():
    img = fundo()
    cola(img, postit("Qual desses você\njá acreditou?", 820, 440, POSTIT[0], s=86), W / 2, 400, -3)
    tachinha(img, W / 2, 200)
    cola(img, pilula("Comenta o número do mito!", 46, VERMELHO, BRANCO, pad=(30, 12), fonte_titulo=True), W / 2, 680, 2)
    c = bloco(760, 380, BRANCO, raio=10, ow=5, sombra=12)
    cola(c, logo(320), 380, 120, -2)
    cola(c, texto("Alugue a partir de R$ 15 por 5 dias.\nRetire em Mauá ou receba em casa.", 34, MARROM, 800,
                  entre=1.3), 380, 270)
    cola(img, c, W / 2, 980, 1.5)
    tachinha(img, W / 2 - 330, 800, PETROLEO)
    tachinha(img, W / 2 + 330, 800, PETROLEO)
    cola(img, pilula("LINK NA BIO · @SUAVEZ_BG", 40, AMARELO, MARROM, pad=(30, 14), fonte_titulo=True), W / 2, 1230, -2)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    telas = [capa()] + [tela_mito(k + 1, *m) for k, m in enumerate(MITOS)] + [final()]
    for k, im in enumerate(telas):
        im.convert("RGB").save(os.path.join(OUT, f"{k + 1:02d}.png"))
    folha = Image.new("RGB", (4 * 405 + 50, 2 * 506 + 30), (255, 255, 255))
    for k, im in enumerate(telas):
        folha.paste(im.convert("RGB").resize((405, 506), Image.LANCZOS), (10 + (k % 4) * 415, 10 + (k // 4) * 516))
    folha.save(os.path.join(ROOT, "out", "mitos_folha.jpg"), quality=90)
    print("ok", len(telas))


if __name__ == "__main__":
    main()
