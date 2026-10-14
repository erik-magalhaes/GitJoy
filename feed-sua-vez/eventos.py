#!/usr/bin/env python3
"""Carrossel 1080x1350 "Monitoria de jogos para eventos" — conceito próprio: CONVITE DE FESTA (14/out/2026).
Pedido: "não quero copia e cola dos outros carrosséis, só mudando o fundo". Cada tela é uma peça de festa diferente:
capa = envelope com o convite saindo; como funciona = PROGRAMAÇÃO de convite impresso (linha do tempo pontilhada);
tipos de evento = BALÕES; jogos = CARDÁPIO da festa; orçamento = ficha de RSVP com linhas pra preencher;
final = INGRESSO destacável. Fundo roxo com confete (ele pediu roxo). Identidade da Jéssica (assinatura-reels/estilo.py).
O que eles disseram: levam os jogos e fazem a monitoria o evento TODO; qualquer evento; quantidade conforme nº e perfil
de pessoas; duração = do evento; ABC Paulista; crianças e adultos, agitados e tranquilos; orçamento por WhatsApp ou
Direct. AINDA NÃO fizeram evento: nada de "já atendemos", depoimento ou foto.

    python3 eventos.py      # out/eventos/01..06.png (+ out/eventos_folha.jpg)
"""
import math
import os
import sys

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
from estilo import (MARROM, PETROLEO, LARANJA, AMARELO, BRANCO, titulo, texto, bloco, pilula, logo, jogo, dado,  # noqa
                    fundo_confete, cola, leque, lilita)

OUT = os.path.join(ROOT, "out", "eventos")
W, H = 1080, 1350
ROXO = (108, 63, 160)
CREME = (255, 248, 236)
CONFETE = (AMARELO, BRANCO, LARANJA, PETROLEO)
_R = lambda *p: os.path.join(REPO, *p)  # noqa: E731
ATIVOS = [_R("roleta-reels/assets/happy_salmon.png"), _R("roleta-reels/assets/taco_gato.png"),
          _R("roleta-reels/assets/flash_10.png")]
CALMOS = [_R("roleta-reels/assets/cartografos.png"), _R("roleta-reels/assets/wandering_towers.png"),
          _R("feed-posts/assets/patchwork.png")]
CAPA = [_R("roleta-reels/assets/eu_sou_banana.png"), _R("roleta-reels/assets/spyfall.png"),
        _R("roleta-reels/assets/unicorn_fever.png"), _R("roleta-reels/assets/last_message.png")]


def bg(semente, livre=(90, 200, 990, 1250)):
    return fundo_confete(W, H, base=ROXO, cores=CONFETE, semente=semente, n=170, livre=livre)


def arrasta(img):
    cola(img, pilula("arrasta pro lado  →", 28, BRANCO, MARROM, pad=(22, 8), ow=4, sombra=5), W - 200, H - 70, -3)


def capa():
    img = bg(31, (60, 60, 1020, 1300))
    # convite saindo do envelope
    conv = bloco(720, 760, CREME, raio=26, ow=7, sombra=12)
    d = ImageDraw.Draw(conv)
    d.rounded_rectangle((26, 26, 694, 734), radius=18, outline=AMARELO, width=6)
    cola(conv, texto("VOCÊ ESTÁ CONVIDADO PRA UMA", 30, MARROM, 900), 360, 80)
    cola(conv, titulo("FESTA COM\nJOGOS!", 104, AMARELO, sw=8, sombra=8), 360, 230)
    cola(conv, texto("A gente leva os jogos e ensina todo mundo a jogar.", 34, MARROM, 800, larg_max=560), 360, 410)
    cola(conv, leque(CAPA, 210, passo=0.6), 360, 590)
    env_w, env_h = 900, 420
    env = Image.new("RGBA", (env_w + 16, env_h + 16), (0, 0, 0, 0))
    de = ImageDraw.Draw(env)
    de.rounded_rectangle((14, 14, env_w + 14, env_h + 14), radius=24, fill=MARROM)
    de.rounded_rectangle((0, 0, env_w, env_h), radius=24, fill=PETROLEO, outline=MARROM, width=8)
    de.polygon([(8, 10), (env_w / 2, env_h * 0.55), (env_w - 8, 10)], fill=(38, 142, 168), outline=MARROM)
    de.line([(8, env_h - 8), (env_w / 2, env_h * 0.45), (env_w - 8, env_h - 8)], fill=MARROM, width=7)
    cola(img, conv, W / 2, 610, -2)
    cola(img, env, W / 2, 1090, 0)
    cola(img, pilula("MONITORIA DE JOGOS PARA EVENTOS", 38, AMARELO, MARROM, pad=(28, 12), fonte_titulo=True), W / 2,
         1110, -2)
    cola(img, logo(230), 160, 135, -6)
    cola(img, titulo("VAI TER FESTA?", 92, BRANCO), 640, 140, 2)
    arrasta(img)
    return img


def programacao():
    img = bg(32)
    papel = bloco(860, 1080, CREME, raio=30, ow=7, sombra=12)
    d = ImageDraw.Draw(papel)
    d.rounded_rectangle((24, 24, 836, 1056), radius=20, outline=ROXO, width=5)
    cola(papel, texto("~ programação ~", 34, ROXO, 800), 430, 85)
    cola(papel, titulo("COMO FUNCIONA", 84, LARANJA, sw=6, sombra=6), 430, 175)
    itens = [("Chegamos com os jogos", "separados pro seu evento e pro seu público"),
             ("Explicamos as regras", "pra quem nunca jogou e pra quem já é fã"),
             ("Ficamos o evento todo", "ajudando, animando e trocando as mesas"),
             ("Ninguém fica de fora", "tem jogo pra criança e pra adulto")]
    x0 = 150
    for k, (tit, sub) in enumerate(itens):
        y = 330 + k * 180
        if k < len(itens) - 1:
            for yy in range(int(y + 40), int(y + 150), 22):  # linha pontilhada da programação
                d.ellipse((x0 - 5, yy - 5, x0 + 5, yy + 5), fill=ROXO)
        cola(papel, dado(84, k + 1, (AMARELO, LARANJA, PETROLEO, ROXO)[k], MARROM if k == 0 else BRANCO), x0, y,
             (-6, 4, -3, 5)[k])
        cola(papel, titulo(tit, 48, MARROM, BRANCO, sw=0, sombra=0), 495, y - 20)
        cola(papel, texto(sub, 30, MARROM, 600), 495, y + 35)
    cola(papel, texto("duração: o tempo do seu evento", 30, ROXO, 800), 430, 1005)
    cola(img, papel, W / 2, 640, 1.2)
    arrasta(img)
    return img


def balao(txt, cor, ct, w=300):
    h = int(w * 1.18)
    im = Image.new("RGBA", (w + 20, h + 170), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((12, 12, w + 12, h + 12), fill=MARROM)  # sombra sólida
    d.ellipse((0, 0, w, h), fill=cor, outline=MARROM, width=7)
    d.polygon([(w / 2 - 18, h - 4), (w / 2 + 18, h - 4), (w / 2, h + 22)], fill=cor, outline=MARROM)
    d.ellipse((w * 0.2, h * 0.12, w * 0.38, h * 0.32), fill=(255, 255, 255, 110))
    pts = [(w / 2 + 14 * math.sin(k / 5), h + 22 + k * 4) for k in range(36)]
    d.line(pts, fill=BRANCO, width=4)
    linhas = txt.split("\n")
    s = 46 if max(len(l) for l in linhas) <= 9 else 38
    for k, l in enumerate(linhas):
        d.text((w / 2, h / 2 + (k - (len(linhas) - 1) / 2) * s * 1.05), l, font=lilita(s), fill=ct, anchor="mm")
    return im


def tipos():
    img = bg(33, (0, 0, 0, 0))
    cola(img, titulo("PRA QUALQUER\nEVENTO", 116, BRANCO), W / 2, 200, -2)
    bal = [("ANIVER-\nSÁRIO", AMARELO, MARROM), ("EMPRESA", LARANJA, BRANCO), ("ESCOLA", PETROLEO, BRANCO),
           ("CASA-\nMENTO", BRANCO, MARROM), ("CHÁ DE\nBEBÊ", AMARELO, MARROM), ("CONDO-\nMÍNIO", PETROLEO, BRANCO),
           ("FAMÍLIA", LARANJA, BRANCO), ("GALERA", BRANCO, MARROM)]
    pos = [(170, 600), (420, 560), (670, 600), (910, 560), (170, 950), (420, 910), (670, 950), (910, 910)]
    for (t, c, ct), (x, y), r in zip(bal, pos, (-6, 4, -3, 6, 5, -4, 3, -5)):
        cola(img, balao(t, c, ct, 215), x, y, r)
    cola(img, pilula("…e o que mais você imaginar!", 40, BRANCO, MARROM, pad=(30, 12)), W / 2, 1180, -2)
    arrasta(img)
    return img


def cardapio():
    img = bg(34)
    menu = bloco(880, 1100, CREME, raio=30, ow=7, sombra=12)
    d = ImageDraw.Draw(menu)
    cola(menu, texto("cardápio da festa", 34, ROXO, 800), 440, 70)
    cola(menu, titulo("JOGO PRA\nTODO MUNDO", 80, LARANJA, sw=6, sombra=6), 440, 195)
    secoes = [("AGITADOS", "rápidos e cheios de risada", ATIVOS, 390), ("TRANQUILOS", "pra jogar com calma", CALMOS, 720)]
    for tit, sub, paths, y in secoes:
        d.line((60, y - 40, 820, y - 40), fill=ROXO, width=3)
        cola(menu, titulo(tit, 52, MARROM, BRANCO, sw=0, sombra=0), 440, y)
        cola(menu, texto(sub, 30, MARROM, 600), 440, y + 50)
        for j, p in enumerate(paths):
            cola(menu, jogo(p, 170, 200), 200 + j * 240, y + 180, (-5, 3, -2)[j])
    cola(menu, pilula("PRA CRIANÇAS E ADULTOS", 36, AMARELO, MARROM, pad=(26, 10), fonte_titulo=True), 440, 1040, -2)
    cola(img, menu, W / 2, 650, -1)
    arrasta(img)
    return img


def rsvp():
    img = bg(35)
    ficha = bloco(860, 1060, BRANCO, raio=30, ow=7, sombra=12)
    d = ImageDraw.Draw(ficha)
    d.rounded_rectangle((0, 0, 860, 170), radius=30, fill=LARANJA, outline=MARROM, width=7)
    d.rectangle((7, 120, 853, 170), fill=LARANJA)
    d.line((0, 170, 860, 170), fill=MARROM, width=7)
    cola(ficha, titulo("PEÇA SEU ORÇAMENTO", 66, BRANCO, sw=5, sombra=5), 430, 88)
    campos = [("Quantas pessoas?", "mais ou menos quantas vão estar no evento"),
              ("Quem vai?", "idades e se curtem jogos agitados ou calmos"),
              ("Data, local e horário", "a monitoria dura o tempo do seu evento")]
    for k, (cmp, dica) in enumerate(campos):
        y = 270 + k * 230
        cola(ficha, titulo(cmp, 50, MARROM, BRANCO, sw=0, sombra=0), 330, y, 0)
        cola(ficha, texto(dica, 28, (120, 96, 80), 600), 380, y + 50)
        for x in range(70, 790, 28):  # linha pra preencher
            d.line((x, y + 120, x + 16, y + 120), fill=MARROM, width=4)
        cola(ficha, dado(70, k + 1, (AMARELO, LARANJA, PETROLEO)[k], MARROM if k == 0 else BRANCO), 760, y, 8)
    cola(ficha, texto("Com isso, a gente separa a seleção de jogos ideal pra sua festa.", 32, ROXO, 800,
                      larg_max=540), 350, 975)
    cola(img, ficha, W / 2, 640, 1)
    carimbo = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
    dc = ImageDraw.Draw(carimbo)
    dc.ellipse((10, 10, 290, 290), outline=(214, 40, 40), width=10)
    dc.ellipse((34, 34, 266, 266), outline=(214, 40, 40), width=4)
    dc.text((150, 120), "ATENDEMOS", font=lilita(34), fill=(214, 40, 40), anchor="mm")
    dc.text((150, 175), "ABC", font=lilita(70), fill=(214, 40, 40), anchor="mm")
    dc.text((150, 225), "PAULISTA", font=lilita(30), fill=(214, 40, 40), anchor="mm")
    cola(img, carimbo, 905, 1095, -14, 0.78, 0.9)
    arrasta(img)
    return img


def ingresso():
    img = bg(36, (0, 0, 0, 0))
    cola(img, logo(280), W / 2, 170, 2)
    cola(img, titulo("BORA LEVAR JOGO\nPRA SUA FESTA?", 104, BRANCO, larg_max=980), W / 2, 400, -2)
    tw, th = 960, 470
    tk = Image.new("RGBA", (tw + 16, th + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(tk)
    for off, cor in ((14, MARROM), (0, AMARELO)):  # ingresso com recortes redondos
        d.rounded_rectangle((off, off, tw + off, th + off), radius=30, fill=cor)
    d.rounded_rectangle((0, 0, tw, th), radius=30, outline=MARROM, width=7)
    for x in (0, tw):
        d.ellipse((x - 40, th / 2 - 40, x + 40, th / 2 + 40), fill=(0, 0, 0, 0))
    for y in range(30, th - 20, 30):  # picote do canhoto
        d.line((690, y, 690, y + 14), fill=MARROM, width=5)
    cola(tk, texto("INGRESSO PARA", 30, MARROM, 900), 345, 70)
    cola(tk, titulo("ORÇAMENTO", 84, BRANCO, sw=7, sombra=7), 345, 155)
    cola(tk, pilula("PELO DIRECT", 40, BRANCO, MARROM, pad=(26, 10), fonte_titulo=True), 345, 270, -2)
    cola(tk, texto("ou pelo WhatsApp do link na bio", 32, MARROM, 800), 345, 360)
    cola(tk, texto("atendemos o", 28, MARROM, 800), 825, 130)
    cola(tk, titulo("ABC", 72, BRANCO, sw=6, sombra=6), 825, 200)
    cola(tk, texto("paulista", 28, MARROM, 800), 825, 270)
    cola(tk, texto("@suavez_bg", 28, MARROM, 900), 825, 370)
    cola(img, tk, W / 2, 830, -3)
    cola(img, dado(120, 5, AMARELO), 150, 1170, -14)
    cola(img, dado(100, 2, LARANJA, BRANCO), 930, 1160, 12)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    telas = [capa(), programacao(), tipos(), cardapio(), rsvp(), ingresso()]
    for k, im in enumerate(telas):
        im.convert("RGB").save(os.path.join(OUT, f"{k + 1:02d}.png"))
    folha = Image.new("RGB", (3 * 540 + 40, 2 * 675 + 30), (255, 255, 255))
    for k, im in enumerate(telas):
        folha.paste(im.convert("RGB").resize((540, 675), Image.LANCZOS), (10 + (k % 3) * 550, 10 + (k // 3) * 685))
    folha.save(os.path.join(ROOT, "out", "eventos_folha.jpg"), quality=90)
    print("ok")


if __name__ == "__main__":
    main()
