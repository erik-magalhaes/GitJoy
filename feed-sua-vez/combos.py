#!/usr/bin/env python3
"""Carrossel 1080x1350 "COMBOS DA SUA VEZ: 3 jogos = 7 dias" (28/out/2026). Conceito próprio: CARDÁPIO DE LANCHONETE.
Fundo de embalagem de lanche (listras largas laranja × creme), painel de menu marrom com letreiro amarelo, cada combo é
uma BANDEJA com as 3 caixas oficiais em cima do papel de bandeja, estrela de preço ("R$ 60 · os 3 por 7 dias") e a
comanda com jogadores e tempo. Identidade da Jéssica (assinatura-reels/estilo.py).
Preços, jogadores e tempo = site da Sua Vez (comum/dados/acervo_site.json); preço do combo = soma dos 3 aluguéis, e com 3
jogos no carrinho TODOS ficam 7 dias (prazo progressivo). Jogos que ainda não apareceram em carrossel.

    python3 combos.py      # out/combos/01..07.png (+ out/combos_folha.jpg)
"""
import json
import math
import os
import sys
from functools import lru_cache

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
from estilo import (MARROM, PETROLEO, LARANJA, AMARELO, BRANCO, titulo, texto, bloco, pilula, logo, jogo, cola,  # noqa
                    lilita, fig, leque)

OUT = os.path.join(ROOT, "out", "combos")
W, H = 1080, 1350
CREME = (255, 241, 214)
VERMELHO = (214, 64, 64)
ACERVO = os.path.join(REPO, "hobby-reels", "assets", "acervo")
SITE = json.load(open(os.path.join(REPO, "comum", "dados", "acervo_site.json"), encoding="utf-8"))
# (número, nome do combo, frase, cor, [(nome no site, recorte, nome curto)])
COMBOS = [
    (1, "CASAL", "pra noite a dois", VERMELHO,
     [("Allumbra: O Duelo", "allumbra_o_duelo", "Allumbra: O Duelo"), ("1, 2, 3, Lucha!", "1_2_3_lucha", "1, 2, 3, Lucha!"),
      ("Unmatched: Robin Hood vs. Bigfoot", "unmatched_robin_hood_vs_bigfoot", "Unmatched: Robin Hood vs. Bigfoot")]),
    (2, "FAMÍLIA", "pra jogar com a criançada", PETROLEO,
     [("Throw Throw Burrito", "throw_throw_burrito", "Throw Throw Burrito"),
      ("Tesouro do Dragão", "tesouro_do_drag_o", "Tesouro do Dragão"), ("Break the Cube", "break_the_cube", "Break the Cube")]),
    (3, "GALERA", "pra casa cheia e muita risada", (108, 63, 160),
     [("Blablabel", "blablabel", "Blablabel"), ("Ref! O jogo da referência", "ref_o_jogo_da_refer_ncia", "Ref!"),
      ("Telma", "telma", "Telma")]),
    (4, "ESTRATÉGIA", "pra quem gosta de pensar", (40, 140, 80),
     [("Tikal", "tikal", "Tikal"), ("Dwar7s Fall", "dwar7s_fall", "Dwar7s Fall"), ("World Wonders", "world_wonders", "World Wonders")]),
]


def ficha(nome):
    v = SITE[nome]
    a, b = v["jogadores"].split("–")
    jog = f"{a} jogadores" if a == b else f"{a} a {b} jogadores"
    return v["preco"], jog, v["tempo"].replace("min", " min")


def fundo():
    """Embalagem de lanche: listras verticais largas laranja × creme, levemente inclinadas."""
    big = Image.new("RGBA", (W * 2, H * 2), CREME + (255,))
    d = ImageDraw.Draw(big)
    for x in range(0, W * 2, 180):
        d.rectangle((x, 0, x + 90, H * 2), fill=LARANJA)
    big = big.rotate(-8, resample=Image.BICUBIC)
    return big.crop((W // 2, H // 2, W // 2 + W, H // 2 + H))


@lru_cache(None)
def letreiro(txt, s, cor=AMARELO, w=None, pad=34):
    """Painel de menu marrom com letreiro amarelo e lampadinhas na borda."""
    tx = titulo(txt, s, cor, MARROM, sw=max(3, s // 14), sombra=0)
    w = w or tx.width + 2 * pad + 40
    h = tx.height + 2 * pad
    im = bloco(w, h, (52, 30, 16), raio=30, ow=8, sombra=12)
    d = ImageDraw.Draw(im)
    for k in range(0, w, 46):  # lampadinhas
        for y in (16, h - 16):
            d.ellipse((k + 18, y - 6, k + 30, y + 6), fill=(255, 226, 140))
    im.alpha_composite(tx, ((w - tx.width) // 2, (h - tx.height) // 2))
    return im


def estrela(txt1, txt2, r=150, cor=AMARELO):
    """Estrela de preço (como selo de oferta de lanchonete)."""
    s = int(r * 2 + 40)
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = s / 2
    pts = [(c + (r if k % 2 == 0 else r * 0.82) * math.cos(math.pi * k / 14),
            c + (r if k % 2 == 0 else r * 0.82) * math.sin(math.pi * k / 14)) for k in range(28)]
    d.polygon([(x + 10, y + 12) for x, y in pts], fill=MARROM)
    d.polygon(pts, fill=cor, outline=MARROM, width=7)
    t1 = titulo(txt1, int(r * 0.52), BRANCO, MARROM, sw=6, sombra=5)
    t2 = texto(txt2, int(r * 0.17), MARROM, 900, larg_max=r * 1.3, entre=1.05)
    im.alpha_composite(t1, (int(c - t1.width / 2), int(c - t1.height / 2 - r * 0.16)))
    im.alpha_composite(t2, (int(c - t2.width / 2), int(c + r * 0.22)))
    return im


def bandeja(paths, w=900, h=470):
    """Bandeja (marrom) com papel de bandeja creme e as 3 caixas em leque em cima."""
    im = bloco(w, h, (120, 74, 40), raio=60, ow=8, sombra=14)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((40, 34, w - 40, h - 34), radius=34, fill=CREME, outline=MARROM, width=4)
    for y in range(60, h - 50, 46):  # papel de bandeja com "Sua Vez!" em marca d'água
        for x in range(70 + (60 if (y // 46) % 2 else 0), w - 80, 130):
            d.text((x, y), "Sua Vez!", font=fig(22, 900), fill=(240, 220, 186))
    ims = [jogo(p, 300, 250) for p in paths]  # lado a lado, a do meio um pouco à frente (nenhuma escondida)
    for k in (0, 2, 1):
        x = w / 2 + (k - 1) * 265
        cola(im, ims[k], x, h / 2 + (0 if k == 1 else 12), (6, 0, -6)[k], 1.06 if k == 1 else 0.98)
    return im


def comanda(itens, w=900):
    """Comanda de papel com os 3 jogos (jogadores e tempo)."""
    linhas = []
    for nome_site, _rec, curto in itens:
        _p, jog, tempo = ficha(nome_site)
        linhas.append((curto, f"{jog} · {tempo}"))
    lh = 74
    h = 44 + lh * len(linhas)
    im = bloco(w, h, BRANCO, raio=22, ow=6, sombra=10)
    d = ImageDraw.Draw(im)
    for k, (a, b) in enumerate(linhas):
        y = 22 + lh * k + lh / 2
        d.text((40, y), "•", font=fig(40, 900), fill=LARANJA, anchor="lm")
        f = fig(34, 900)
        while d.textlength(a, font=f) > w - 430 and f.size > 22:
            f = fig(f.size - 2, 900)
        d.text((80, y), a, font=f, fill=MARROM, anchor="lm")
        d.text((w - 36, y), b, font=fig(28, 700), fill=(120, 90, 70), anchor="rm")
        if k < len(linhas) - 1:
            for x in range(40, w - 36, 22):
                d.line((x, y + lh / 2, x + 10, y + lh / 2), fill=(220, 205, 190), width=3)
    return im


def rodape(img, txt="arrasta pro próximo combo  →"):
    cola(img, pilula(txt, 34, BRANCO, MARROM, pad=(26, 10), ow=5, sombra=6), W / 2, H - 70)


def capa():
    img = fundo()
    cola(img, logo(260), W / 2, 120)
    cola(img, letreiro("COMBOS DA SUA VEZ", 92), W / 2, 330, -2)
    cola(img, titulo("3 JOGOS\n= 7 DIAS", 170, BRANCO), W / 2, 640, -3)
    paths = [os.path.join(ACERVO, c[4][0][1] + ".png") for c in COMBOS] + [os.path.join(ACERVO, COMBOS[0][4][2][1] + ".png")]
    cola(img, leque(paths[:4], 300, passo=0.62, ang=8), W / 2, 1000, 0, 0.95)
    cola(img, pilula("escolha o seu combo  →", 40, AMARELO, MARROM, pad=(30, 12)), W / 2, H - 90, -2)
    return img


def como_funciona():
    img = fundo()
    cola(img, letreiro("COMO FUNCIONA?", 84), W / 2, 150, 2)
    c = bloco(900, 860, BRANCO, raio=46, ow=8, sombra=14)
    cola(c, titulo("Pega 3 jogos", 88, LARANJA), 450, 110)
    cola(c, texto("e TODOS ficam 7 dias com você,\npelo mesmo preço de 5!", 44, MARROM, 800, entre=1.25), 450, 250)
    d = ImageDraw.Draw(c)
    d.line((90, 345, 810, 345), fill=(235, 222, 205), width=5)
    cola(c, texto("e se quiser mais:", 38, PETROLEO, 900), 450, 405)
    for k, (j, dias, cor) in enumerate([(3, 7, LARANJA), (5, 10, PETROLEO), (7, 15, (40, 140, 80))]):
        y = 470 + k * 95
        cola(c, pilula(f"{j} jogos", 44, cor, BRANCO, pad=(28, 10), fonte_titulo=True), 280, y)
        cola(c, texto("→", 54, MARROM, 900), 450, y - 4)
        cola(c, pilula(f"{dias} dias", 44, AMARELO, MARROM, pad=(28, 10), fonte_titulo=True), 620, y)
    cola(c, texto("Montamos 4 combos prontos pra você.\nBora ver?", 36, MARROM, 800, entre=1.2), 450, 765)
    cola(img, c, W / 2, 720, -1.5)
    rodape(img, "arrasta pro combo nº 1  →")
    return img


def tela_combo(num, nome, frase, cor, itens):
    img = fundo()
    cola(img, letreiro(f"COMBO Nº {num}", 70), 330, 120, -3)
    cola(img, titulo(nome, 132, BRANCO, larg_max=900), W / 2, 285, 2)
    cola(img, pilula(frase, 40, cor, BRANCO, pad=(30, 12)), W / 2, 410, -2)
    paths = [os.path.join(ACERVO, r + ".png") for _n, r, _c in itens]
    cola(img, bandeja(paths), W / 2, 690)
    total = sum(ficha(n)[0] for n, _r, _c in itens)
    cola(img, estrela(f"R$ {total}", "os 3 por 7 dias", r=135), 935, 900, 10)
    cola(img, comanda(itens), W / 2, 1110, 1)
    rodape(img, "arrasta pro próximo combo  →" if num < len(COMBOS) else "arrasta  →")
    return img


def final():
    img = fundo()
    cola(img, letreiro("QUAL É O SEU?", 96), W / 2, 170, -2)
    c = bloco(880, 900, BRANCO, raio=46, ow=8, sombra=14)
    cola(c, titulo("Comenta o\nnúmero do combo!", 74, LARANJA), 440, 150)
    for k, (num, nome, _f, cor, _i) in enumerate(COMBOS):
        x, y = 240 + (k % 2) * 400, 350 + (k // 2) * 120
        cola(c, pilula(f"{num} · {nome}", 40, cor, BRANCO, pad=(26, 10), fonte_titulo=True), x, y, (-2, 2)[k % 2])
    d = ImageDraw.Draw(c)
    d.line((90, 545, 790, 545), fill=(235, 222, 205), width=5)
    cola(c, texto("ou monte o seu: qualquer 3 jogos\ndo acervo ficam 7 dias", 38, MARROM, 800, entre=1.25), 440, 630)
    cola(c, logo(300), 440, 790, -2)
    cola(img, c, W / 2, 720, 1)
    cola(img, pilula("ALUGUE PELO LINK NA BIO · @SUAVEZ_BG", 38, AMARELO, MARROM, pad=(30, 14), fonte_titulo=True),
         W / 2, 1240, -2)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    telas = [capa(), como_funciona()] + [tela_combo(*c) for c in COMBOS] + [final()]
    for k, im in enumerate(telas):
        im.convert("RGB").save(os.path.join(OUT, f"{k + 1:02d}.png"))
    folha = Image.new("RGB", (4 * 405 + 50, 2 * 506 + 30), (255, 255, 255))
    for k, im in enumerate(telas):
        folha.paste(im.convert("RGB").resize((405, 506), Image.LANCZOS), (10 + (k % 4) * 415, 10 + (k // 4) * 516))
    folha.save(os.path.join(ROOT, "out", "combos_folha.jpg"), quality=90)
    print("ok", len(telas))


if __name__ == "__main__":
    main()
