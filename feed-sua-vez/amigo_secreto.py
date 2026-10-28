#!/usr/bin/env python3
"""Carrossel 1080x1350 "VAI DAR JOGO NO AMIGO SECRETO? ALUGA ANTES E TESTA!" (28/out/2026; ele trocou o "Natal" por
amigo secreto). Conceito próprio: PAPEL DE PRESENTE. Fundo de papel de presente (petróleo com bolinhas e a fita laranja
cruzada), cada perfil é um PAPELZINHO DO SORTEIO ("Você tirou: o competitivo") e a sugestão vem numa ETIQUETA KRAFT de
presente com barbante e a caixa oficial do jogo. Identidade da Jéssica (assinatura-reels/estilo.py).
Ideia: antes de comprar um jogo de presente, aluga, testa com a pessoa ou com a turma e só depois compra o certo; e pra
festa do amigo secreto, 3 jogos ficam 7 dias. Jogos que ainda não apareceram em carrossel; ficha = site da Sua Vez.

    python3 amigo_secreto.py      # out/amigo_secreto/01..08.png (+ out/amigo_secreto_folha.jpg)
"""
import json
import os
import random
import sys
from functools import lru_cache

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
from estilo import (MARROM, PETROLEO, LARANJA, AMARELO, BRANCO, titulo, texto, bloco, pilula, logo, jogo, cola,  # noqa
                    lilita, fig)

OUT = os.path.join(ROOT, "out", "amigo_secreto")
W, H = 1080, 1350
KRAFT, PAPEL = (214, 178, 128), (252, 250, 244)
VERMELHO = (205, 50, 50)
ACERVO = os.path.join(REPO, "hobby-reels", "assets", "acervo")
SITE = json.load(open(os.path.join(REPO, "comum", "dados", "acervo_site.json"), encoding="utf-8"))
PERFIS = [  # (quem você tirou, por que esse jogo, nome no site, recorte, nome na tela)
    ("o que diz que\nnão gosta de jogo", "Leve e rapidinho: em 20 minutos ele já tá pedindo revanche.",
     "Dobro", "dobro", "Dobro"),
    ("o competitivo", "Um leilão de luxo em que quem gasta demais está fora. Perfeito pra quem odeia perder.",
     "High Society", "high_society", "High Society"),
    ("o casal da turma", "Jogo de cartas lindo, de 2 a 4 jogadores, que funciona muito bem a dois.",
     "Sea Salt & Paper", "sea_salt_paper", "Sea Salt & Paper"),
    ("a criança\nda família", "Decorar nome de homem das cavernas e gritar primeiro: risada garantida pra todas as idades.",
     "Uga Buga", "uga_buga", "Uga Buga"),
    ("o estrategista", "Dados, trocas e escolhas no bazar: tem decisão boa em toda rodada.",
     "Istanbul: The Dice Game", "istanbul_the_dice_game", "Istanbul: Jogo de Dados"),
]


def ficha(nome):
    v = SITE[nome]
    a, b = v["jogadores"].split("–")
    jog = f"{a} jogadores" if a == b else f"{a} a {b} jogadores"
    return f"{jog} · {v['tempo'].replace('min', ' min')} · R$ {v['preco']} por 5 dias"


@lru_cache(None)
def _papel():
    """Papel de presente: petróleo com bolinhas claras e a fita laranja cruzada com laço."""
    img = Image.new("RGBA", (W, H), PETROLEO + (255,))
    d = ImageDraw.Draw(img)
    for y in range(0, H + 60, 60):
        for x in range(0 + (30 if (y // 60) % 2 else 0), W + 60, 60):
            d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=(44, 146, 172))
    for k in range(0, W + H, 240):  # estrelinhas
        x, y = (k * 7) % W, (k * 13) % H
        r1, r2 = 16, 5
        d.polygon([(x, y - r1), (x + r2, y - r2), (x + r1, y), (x + r2, y + r2), (x, y + r1), (x - r2, y + r2), (x - r1, y),
                   (x - r2, y - r2)], fill=(255, 214, 120))
    fx = 150  # fita vertical à esquerda e horizontal embaixo
    d.rectangle((fx - 34, 0, fx + 34, H), fill=LARANJA)
    d.line((fx - 34, 0, fx - 34, H), fill=MARROM, width=4)
    d.line((fx + 34, 0, fx + 34, H), fill=MARROM, width=4)
    fy = H - 190
    d.rectangle((0, fy - 34, W, fy + 34), fill=LARANJA)
    d.line((0, fy - 34, W, fy - 34), fill=MARROM, width=4)
    d.line((0, fy + 34, W, fy + 34), fill=MARROM, width=4)
    for sx in (-1, 1):  # laço no cruzamento
        d.polygon([(fx, fy), (fx + sx * 120, fy - 70), (fx + sx * 120, fy + 70)], fill=(255, 170, 70), outline=MARROM)
    d.ellipse((fx - 30, fy - 30, fx + 30, fy + 30), fill=LARANJA, outline=MARROM, width=5)
    return img


def fundo():
    return _papel().copy()


def papelzinho(linha1, linha2, w=760, h=330, s=86):
    """Papelzinho do sorteio, aberto, com as marcas da dobra."""
    im = Image.new("RGBA", (w + 24, h + 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((14, 16, w + 14, h + 16), fill=(20, 40, 50, 120))
    d.polygon([(0, 6), (w, 0), (w - 4, h), (4, h - 4)], fill=PAPEL)
    for frac in (1 / 3, 2 / 3):  # vincos da dobra
        x = int(w * frac)
        d.line((x, 4, x - 2, h - 4), fill=(222, 218, 205), width=3)
    d.line((10, h / 2, w - 10, h / 2 - 3), fill=(230, 226, 214), width=2)
    t1 = texto(linha1, 40, (120, 110, 100), 700)
    t2 = titulo(linha2.upper(), s, VERMELHO, VERMELHO, sw=0, sombra=0, larg_max=w - 80)
    im.alpha_composite(t1, ((w - t1.width) // 2, 34))
    im.alpha_composite(t2, ((w - t2.width) // 2, 34 + t1.height + (h - 60 - t1.height - t2.height) // 2))
    return im


def etiqueta(motivo, nome_site, recorte, nome, w=880, h=640):
    """Etiqueta kraft de presente (canto cortado + furinho com barbante) com a caixa do jogo."""
    im = Image.new("RGBA", (w + 30, h + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = 90
    pts = [(c, 0), (w, 0), (w, h), (c, h), (0, h - c), (0, c)]
    d.polygon([(x + 14, y + 16) for x, y in pts], fill=MARROM)
    d.polygon(pts, fill=KRAFT, outline=MARROM, width=7)
    d.ellipse((34, h / 2 - 22, 78, h / 2 + 22), fill=PETROLEO, outline=MARROM, width=5)  # furinho
    cola(im, pilula("TESTE ANTES:", 40, VERMELHO, BRANCO, pad=(24, 10), fonte_titulo=True), 300, 74, -2)
    tx = texto(motivo, 36, MARROM, 800, larg_max=420, entre=1.35, alinha="lm")
    cola(im, tx, 120 + tx.width / 2, 300)
    cola(im, jogo(os.path.join(ACERVO, recorte + ".png"), 330, 270), w - 175, 290, 5)
    cola(im, pilula(nome, 34, AMARELO, MARROM, pad=(22, 8), fonte_titulo=True), w - 175, 490, -3)
    cola(im, texto(ficha(nome_site), 30, MARROM, 800), w / 2 + 30, h - 58)
    return im


def barbante(img, x0, y0, x1, y1):
    d = ImageDraw.Draw(img)
    pts = [(x0 + (x1 - x0) * u, y0 + (y1 - y0) * u + 60 * (u * (1 - u)) * 4) for u in [k / 20 for k in range(21)]]
    d.line(pts, fill=(250, 236, 205), width=6, joint="curve")


def capa():
    img = fundo()
    cola(img, logo(250), W - 180, 115, 3)
    cola(img, titulo("VAI DAR JOGO\nNO AMIGO\nSECRETO?", 128, BRANCO), W / 2 + 40, 400, -3)
    cola(img, papelzinho("você tirou:", "???", w=620, h=260, s=110), W / 2 + 40, 830, 5)
    cola(img, pilula("aluga antes e testa!  →", 46, AMARELO, MARROM, pad=(32, 14), fonte_titulo=True),
         W / 2 + 60, 1050, -2)
    return img


def como_funciona():
    img = fundo()
    cola(img, titulo("SEM MEDO\nDE ERRAR", 120, BRANCO), W / 2 + 40, 220, -2)
    passos = [("1", "Aluga o jogo que você\nquer dar de presente", "a partir de R$ 15 por 5 dias"),
              ("2", "Joga com a pessoa\n(ou com a turma)", "e vê se combina com ela"),
              ("3", "Curtiu? Aí é só comprar\no presente certo", "sem arriscar no escuro")]
    for k, (n, a, b) in enumerate(passos):
        y = 520 + k * 255
        c = bloco(760, 210, PAPEL, raio=26, ow=6, sombra=12)
        cola(c, titulo(n, 110, LARANJA), 85, 105)
        cola(c, texto(a, 38, MARROM, 900, entre=1.2, alinha="lm"), 170 + texto(a, 38, MARROM, 900, entre=1.2,
                                                                                alinha="lm").width / 2, 85)
        cola(c, texto(b, 30, PETROLEO, 800, alinha="lm"), 170 + texto(b, 30, PETROLEO, 800, alinha="lm").width / 2, 165)
        cola(img, c, W / 2 + 50, y, (-1.5, 1.5, -1)[k])
    cola(img, pilula("quem você tirou?  →", 36, BRANCO, MARROM, pad=(26, 10)), W / 2 + 60, H - 70)
    return img


def tela_perfil(k, quem, motivo, nome_site, recorte, nome):
    img = fundo()
    rnd = random.Random(k)
    cola(img, papelzinho("você tirou:", quem.replace("\n", " ") if len(quem) < 18 else quem), W / 2 + 40, 280,
         rnd.choice((-4, 4)))
    cola(img, etiqueta(motivo, nome_site, recorte, nome), W / 2 + 40, 800, rnd.choice((-2, 2)))
    barbante(img, 175, 800, 150, 1160)
    cola(img, pilula("arrasta  →", 32, BRANCO, MARROM, pad=(24, 9), ow=5, sombra=6), W / 2 + 60, H - 60)
    return img


def final():
    img = fundo()
    cola(img, titulo("E PRA FESTA DO\nAMIGO SECRETO?", 100, BRANCO), W / 2 + 40, 210, -2)
    c = bloco(820, 760, PAPEL, raio=36, ow=8, sombra=14)
    cola(c, titulo("Leva 3 jogos:", 80, LARANJA), 410, 100)
    cola(c, texto("os 3 ficam 7 dias com você,\npelo mesmo preço de 5!", 42, MARROM, 900, entre=1.25), 410, 230)
    paths = [os.path.join(ACERVO, p[3] + ".png") for p in (PERFIS[0], PERFIS[3], PERFIS[1])]
    for j, p in enumerate(paths):
        cola(c, jogo(p, 200, 180), 190 + j * 215, 440, (-6, 0, 6)[j])
    cola(c, pilula("Marca aqui quem você quer tirar!", 34, VERMELHO, BRANCO, pad=(24, 10)), 410, 640, 2)
    cola(img, c, W / 2 + 40, 760, 1)
    cola(img, logo(250), W / 2 + 40 - 250, 1255, -3)
    cola(img, pilula("LINK NA BIO · @SUAVEZ_BG", 36, AMARELO, MARROM, pad=(26, 12), fonte_titulo=True),
         W / 2 + 180, 1255, 2)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    telas = [capa(), como_funciona()] + [tela_perfil(k + 1, *p) for k, p in enumerate(PERFIS)] + [final()]
    for k, im in enumerate(telas):
        im.convert("RGB").save(os.path.join(OUT, f"{k + 1:02d}.png"))
    folha = Image.new("RGB", (4 * 405 + 50, 2 * 506 + 30), (255, 255, 255))
    for k, im in enumerate(telas):
        folha.paste(im.convert("RGB").resize((405, 506), Image.LANCZOS), (10 + (k % 4) * 415, 10 + (k // 4) * 516))
    folha.save(os.path.join(ROOT, "out", "amigo_secreto_folha.jpg"), quality=90)
    print("ok", len(telas))


if __name__ == "__main__":
    main()
