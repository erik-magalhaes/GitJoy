#!/usr/bin/env python3
"""Carrossel 1080x1350 "Monitoria de jogos para eventos" (14/out/2026), identidade da Jéssica (assinatura-reels/estilo.py).
O que eles disseram: levam os jogos e fazem a monitoria o evento TODO (ajudando e ensinando); qualquer tipo de evento;
a quantidade de jogos depende de quantas pessoas e do perfil (a pessoa conta isso e eles separam as opções); a duração
é a do evento; atendem principalmente o ABC Paulista; jogos para crianças e adultos, mais ativos/rápidos e mais calmos;
preço só por orçamento (WhatsApp ou Direct). AINDA NÃO fizeram evento: nada de "já atendemos", depoimento ou foto.

    python3 eventos.py      # out/eventos/01..06.png (+ out/eventos_folha.jpg)
"""
import os
import sys

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
from estilo import (MARROM, PETROLEO, LARANJA, AMARELO, BRANCO, PRATA, titulo, texto, bloco, pilula, logo, jogo, dado,  # noqa
                    peao, fundo, cola, leque)

OUT = os.path.join(ROOT, "out", "eventos")
W, H = 1080, 1350
_R = lambda *p: os.path.join(REPO, *p)  # noqa: E731
ATIVOS = [_R("roleta-reels/assets/happy_salmon.png"), _R("roleta-reels/assets/taco_gato.png"),
          _R("roleta-reels/assets/flash_10.png")]
CALMOS = [_R("roleta-reels/assets/cartografos.png"), _R("roleta-reels/assets/wandering_towers.png"),
          _R("feed-posts/assets/patchwork.png")]
CAPA = [_R("roleta-reels/assets/eu_sou_banana.png"), _R("roleta-reels/assets/spyfall.png"),
        _R("roleta-reels/assets/unicorn_fever.png"), _R("roleta-reels/assets/last_message.png"),
        _R("roleta-reels/assets/dobro.png")]


def arrasta(img):
    cola(img, pilula("arrasta pro lado  →", 28, BRANCO, MARROM, pad=(22, 8), ow=4, sombra=5), W - 200, H - 92, -3)


def capa():
    img = fundo(W, H, 21)
    cola(img, logo(280), W / 2, 165, -2)
    cola(img, titulo("VAI TER\nFESTA?", 170, BRANCO), W / 2, 450, -2)
    cola(img, texto("A gente leva os jogos e ensina todo mundo a jogar!", 44, MARROM, 800, larg_max=860), W / 2, 680)
    cola(img, leque(CAPA, 290), W / 2, 950)
    cola(img, pilula("MONITORIA DE JOGOS PARA EVENTOS", 40, AMARELO, MARROM, pad=(30, 12), fonte_titulo=True), W / 2,
         1160, -2)
    cola(img, dado(100, 6, AMARELO), 130, 175, -14)
    cola(img, peao(140, LARANJA), 950, 170, 10)
    arrasta(img)
    return img


def como_funciona():
    img = fundo(W, H, 22)
    cola(img, titulo("COMO\nFUNCIONA?", 120, BRANCO), W / 2, 240, -2)
    passos = [(1, "Levamos os jogos", "Separados pro seu evento e pro seu público.", AMARELO),
              (2, "Ficamos o evento todo", "Explicando as regras, ajudando e animando as mesas.", LARANJA),
              (3, "Ninguém fica de fora", "Tem jogo pra quem nunca jogou e pra quem já é fã.", PETROLEO)]
    for k, (n, tit, desc, cor) in enumerate(passos):
        card = bloco(880, 240, BRANCO, raio=34)
        cola(card, dado(145, n, cor, MARROM if cor == AMARELO else BRANCO), 110, 120, (-8, 6, -4)[k])
        cola(card, titulo(tit, 54, MARROM, BRANCO, sw=0, sombra=0, larg_max=620), 545, 72)
        cola(card, texto(desc, 34, MARROM, 600, larg_max=600), 545, 160)
        cola(img, card, W / 2 + (-10, 12, -6)[k], 560 + k * 270, (1, -1, 0.6)[k])
    arrasta(img)
    return img


def qualquer_evento():
    img = fundo(W, H, 23)
    cola(img, titulo("PRA QUALQUER\nEVENTO", 120, BRANCO), W / 2, 240, -2)
    tipos = [("Aniversário", LARANJA, BRANCO), ("Empresa", PETROLEO, BRANCO), ("Escola", AMARELO, MARROM),
             ("Casamento", BRANCO, MARROM), ("Chá de bebê", LARANJA, BRANCO), ("Confraternização", AMARELO, MARROM),
             ("Condomínio", PETROLEO, BRANCO), ("Festa em família", BRANCO, MARROM), ("Encontro da galera", LARANJA, BRANCO)]
    y, linha, x0 = 520, [], 0
    linhas = [tipos[0:2], tipos[2:4], tipos[4:6], tipos[6:8], tipos[8:9]]
    for k, l in enumerate(linhas):
        ims = [pilula(t.upper(), 46, c, ct, pad=(32, 14), fonte_titulo=True) for t, c, ct in l]
        larg = sum(i.width for i in ims) + 30 * (len(ims) - 1)
        x = W / 2 - larg / 2
        for j, im in enumerate(ims):
            cola(img, im, x + im.width / 2, y + k * 125, (-3, 2, -2, 3, -1)[(k + j) % 5])
            x += im.width + 30
    del x0, linha
    cola(img, texto("…e o que mais você imaginar!", 44, MARROM, 800), W / 2, 1160)
    arrasta(img)
    return img


def para_todos():
    img = fundo(W, H, 24)
    cola(img, titulo("JOGO PRA\nTODO MUNDO", 120, BRANCO), W / 2, 240, -2)
    for k, (tit, sub, paths, cor, ct) in enumerate((("AGITADOS", "rápidos e cheios de risada", ATIVOS, LARANJA, BRANCO),
                                                     ("TRANQUILOS", "pra jogar com calma", CALMOS, PETROLEO, BRANCO))):
        card = bloco(450, 720, cor, raio=36, ow=7, sombra=12)
        cola(card, titulo(tit, 62, BRANCO, sw=5, sombra=5), 225, 75)
        cola(card, texto(sub, 32, ct, 800, larg_max=400), 225, 145)
        for j, p in enumerate(paths):
            cola(card, jogo(p, 205, 230), 225 + (-65, 65, 0)[j], 315 + j * 150, (-6, 5, -3)[j])
        cola(img, card, 285 + k * 510, 840, (-2, 2)[k])
    cola(img, pilula("PRA CRIANÇAS E ADULTOS", 44, AMARELO, MARROM, pad=(30, 12), fonte_titulo=True), W / 2, 1255, -2)
    return img


def orcamento():
    img = fundo(W, H, 25)
    cola(img, titulo("COMO PEDIR\nSEU ORÇAMENTO", 112, BRANCO, larg_max=960), W / 2, 240, -2)
    itens = [(1, "Quantas pessoas", "Mais ou menos quantas vão estar no evento.", AMARELO),
             (2, "Quem são elas", "Idades e se curtem jogos mais agitados ou mais calmos.", LARANJA),
             (3, "Data, local e horário", "A monitoria dura o tempo do seu evento.", PETROLEO)]
    for k, (n, tit, desc, cor) in enumerate(itens):
        card = bloco(880, 220, BRANCO, raio=34)
        cola(card, dado(135, n, cor, MARROM if cor == AMARELO else BRANCO), 105, 110, (-8, 6, -4)[k])
        cola(card, titulo(tit, 52, MARROM, BRANCO, sw=0, sombra=0, larg_max=620), 545, 68)
        cola(card, texto(desc, 32, MARROM, 600, larg_max=600), 545, 148)
        cola(img, card, W / 2 + (-10, 12, -6)[k], 480 + k * 232, (1, -1, 0.6)[k])
    cola(img, texto("Com isso, a gente separa a seleção de jogos ideal pra sua festa.", 36, MARROM, 800,
                    larg_max=860), W / 2, 1110)
    arrasta(img)
    return img


def chamada():
    img = fundo(W, H, 26)
    cola(img, logo(300), W / 2, 190, 2)
    cola(img, titulo("BORA LEVAR\nJOGO PRA\nSUA FESTA?", 130, BRANCO), W / 2, 530, -2)
    cola(img, pilula("ORÇAMENTO PELO DIRECT", 54, AMARELO, MARROM, pad=(38, 16), fonte_titulo=True), W / 2, 860, -2)
    cola(img, pilula("OU PELO WHATSAPP DO LINK NA BIO", 40, PETROLEO, BRANCO, pad=(30, 12)), W / 2, 975, 2)
    cola(img, pilula("ATENDEMOS O ABC PAULISTA", 38, LARANJA, BRANCO, pad=(28, 12)), W / 2, 1080, -1)
    cola(img, texto("@suavez_bg", 40, MARROM, 800), W / 2, 1180)
    cola(img, dado(110, 5, AMARELO), 140, 1180, -14)
    cola(img, peao(150, PETROLEO), 940, 1170, 10)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    telas = [capa(), como_funciona(), qualquer_evento(), para_todos(), orcamento(), chamada()]
    for k, im in enumerate(telas):
        im.convert("RGB").save(os.path.join(OUT, f"{k + 1:02d}.png"))
    folha = Image.new("RGB", (3 * 540 + 40, 2 * 675 + 30), (255, 255, 255))
    for k, im in enumerate(telas):
        folha.paste(im.convert("RGB").resize((540, 675), Image.LANCZOS), (10 + (k % 3) * 550, 10 + (k // 3) * 685))
    folha.save(os.path.join(ROOT, "out", "eventos_folha.jpg"), quality=90)
    print("ok")


if __name__ == "__main__":
    main()
