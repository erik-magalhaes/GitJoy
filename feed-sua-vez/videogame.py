#!/usr/bin/env python3
"""Carrossel "SE VOCÊ JOGA ___, VAI CURTIR ___" (11/nov/2026, ideia dele): videogame → jogo de tabuleiro do acervo.

Conceito: TELA DE VIDEOGAME (fundo azul-noite com grade de pixels e estrelinhas quadradas, HUD com corações e "FASE n/7",
letra de pixel Press Start 2P para o lado do videogame) + a identidade da Jéssica para o lado do tabuleiro (cartão
creme com contorno marrom e sombra sólida, Lilita/Figtree, caixa OFICIAL recortada do site).
O videogame aparece SÓ PELO NOME (sem imagem: direitos autorais).

    /usr/bin/python3 videogame.py --teste    # out/videogame/teste.jpg (capa + 1ª tela)
    /usr/bin/python3 videogame.py            # out/videogame/NN.png + stories/story_NN.png
"""
import os
import random
import sys
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
import estilo as E  # noqa: E402

AC = os.path.join(REPO, "hobby-reels", "assets", "acervo")
PIXEL = os.path.join(REPO, "comum", "fontes", "PressStart2P-Regular.ttf")
OUT = os.path.join(ROOT, "out", "videogame")
W, H = 1080, 1350
NOITE = (18, 34, 58)
GRADE = (28, 50, 80)
CIANO = (110, 226, 240)
CREME = (255, 246, 228)

# (videogame, jogo, nome no site (ficha), caixa, frase)
PARES = [
    ("AMONG US", "The Resistance", "The Resistance", "the_resistance.png",
     "Tem traidor na mesa e ninguém confia em ninguém. Só que aqui você olha na cara de quem mente."),
    ("JURASSIC WORLD EVOLUTION", "Dinosaur Island", "Dinosaur Island", "dinosaur_island.png",
     "Monte o seu parque, crie dinossauros, receba os visitantes... e torça pra nenhum fugir."),
    ("STARDEW VALLEY", "Everdell Duo", "Everdell Duo", "everdell_duo.png",
     "Uma vila tranquila de bichinhos pra construir sem pressa, carta por carta."),
    ("HADES", "Clank! Catacombs", "Clank!: Catacombs", "clank_catacombs.png",
     "Desce na masmorra, monta o seu baralho no caminho e tenta sair vivo com o tesouro."),
    ("MARIO KART", "Unicorn Fever", "Unicorn Fever", "unicorn_fever.png",
     "Corrida de unicórnios cheia de golpe baixo: você aposta e joga magia pra atrapalhar os outros."),
    ("CIVILIZATION", "World Wonders", "World Wonders", "world_wonders.png",
     "Construa a sua cidade e erga as grandes maravilhas do mundo, rodada a rodada."),
    ("GTA", "Bad Company", "Bad Company", "bad_company.png",
     "Monte a gangue, planeje os assaltos e fuja da polícia."),
]


def pixel(s):
    return ImageFont.truetype(PIXEL, int(s))


def _lw(txt, f):
    return ImageDraw.Draw(Image.new("L", (1, 1))).textlength(txt, font=f)


def quebra(txt, f, larg):
    linhas, atual = [], ""
    for p in txt.split(" "):
        t = (atual + " " + p).strip()
        if _lw(t, f) > larg and atual:
            linhas.append(atual)
            atual = p
        else:
            atual = t
    linhas.append(atual)
    return linhas


def texto_pixel(img, txt, s, cx, y, cor, larg=860, sombra=(0, 0, 0), entre=1.5):
    """Texto em pixel centralizado em cx, com sombra dura de 1 'pixel'. Devolve o y do fim."""
    f = pixel(s)
    while max(_lw(l, f) for l in quebra(txt, f, larg)) > larg and s > 14:
        s -= 2
        f = pixel(s)
    d = ImageDraw.Draw(img)
    o = max(3, s // 8)
    for l in quebra(txt, f, larg):
        if sombra:
            d.text((cx + o, y + o), l, font=f, fill=sombra, anchor="ma")
        d.text((cx, y), l, font=f, fill=cor, anchor="ma")
        y += int(s * entre)
    return y


@lru_cache(None)
def _fundo(semente):
    img = Image.new("RGBA", (W, H), NOITE + (255,))
    d = ImageDraw.Draw(img)
    for x in range(0, W, 30):  # grade de pixels
        d.line((x, 0, x, H), fill=GRADE, width=1)
    for y in range(0, H, 30):
        d.line((0, y, W, y), fill=GRADE, width=1)
    rnd = random.Random(semente)
    for _ in range(22):  # estrelinhas quadradas (pixel)
        x = rnd.choice([rnd.randrange(0, 90, 30), rnd.randrange(990, W, 30)])  # só nas laterais
        y = rnd.randrange(150, H, 30)
        c = rnd.choice([E.AMARELO, E.LARANJA, CIANO, (255, 255, 255)])
        k = rnd.choice([1, 1, 2])
        p = 10 * k
        d.rectangle((x + 10, y, x + 10 + p - 1, y + 3 * p - 1), fill=c)  # cruz de pixel
        d.rectangle((x, y + 10, x + 3 * p - 1, y + 10 + p - 1), fill=c)
    return img


def fundo(semente=1):
    return _fundo(semente).copy()


def coracao(d, x, y, p=8, cor=(232, 64, 80)):
    """Coração de pixel 7x6 (p = tamanho do pixel)."""
    mapa = ["0110110", "1111111", "1111111", "0111110", "0011100", "0001000"]
    for j, linha in enumerate(mapa):
        for i, c in enumerate(linha):
            if c == "1":
                d.rectangle((x + i * p, y + j * p, x + (i + 1) * p - 1, y + (j + 1) * p - 1), fill=cor)


def seta_pixel(d, cx, y, p=12, cor=E.AMARELO):
    """Seta para baixo em pixels."""
    mapa = ["0011100", "0011100", "0011100", "1111111", "0111110", "0011100", "0001000"]
    x0 = cx - 7 * p // 2
    for j, linha in enumerate(mapa):
        for i, c in enumerate(linha):
            if c == "1":
                d.rectangle((x0 + i * p + 4, y + j * p + 4, x0 + (i + 1) * p + 3, y + (j + 1) * p + 3), fill=(0, 0, 0))
                d.rectangle((x0 + i * p, y + j * p, x0 + (i + 1) * p - 1, y + (j + 1) * p - 1), fill=cor)


def hud(img, fase, total):
    d = ImageDraw.Draw(img)
    for k in range(3):
        coracao(d, 60 + k * 66, 56)
    f = pixel(26)
    t = f"FASE {fase}/{total}"
    d.text((W - 60 + 3, 62 + 3), t, font=f, fill=(0, 0, 0), anchor="ra")
    d.text((W - 60, 62), t, font=f, fill=(255, 255, 255), anchor="ra")


def tela_crt(w, h):
    """Tela de videogame: moldura marrom grossa com sombra sólida, vidro escuro com scanlines."""
    im = E.bloco(w, h, (12, 22, 34), raio=34, ow=8, sombra=12)
    d = ImageDraw.Draw(im)
    for y in range(16, h - 12, 6):
        d.line((16, y, w - 16, y), fill=(20, 34, 50), width=2)
    return im


def ficha(nome_site):
    import json
    d = json.load(open(os.path.join(REPO, "comum", "dados", "acervo_site.json")))[nome_site]
    jog = d["jogadores"].replace("–", " a ")
    a, _, b = jog.partition(" a ")
    jog = f"{a} jogadores" if a == b else f"{jog} jogadores"
    dias = 7 if d["preco"] == 60 else 5
    return f"{jog} · {d['tempo'].replace('min', ' min')} · R$ {d['preco']} / {dias} dias"


def tela_par(k):
    vg, nome, site, caixa, frase = PARES[k]
    img = fundo(k + 3)
    hud(img, k + 1, len(PARES))
    d = ImageDraw.Draw(img)
    # tela do videogame
    tw, th = 900, 300
    crt = tela_crt(tw, th)
    x0, y0 = (W - tw) // 2, 150
    img.alpha_composite(crt, (x0, y0))
    sv = E.texto("SE VOCÊ JOGA", 34, cor=CIANO, peso=900)
    img.alpha_composite(sv, ((W - sv.width) // 2, y0 + 36))
    yy = y0 + 36 + sv.height
    f = pixel(64)
    n_linhas = len(quebra(vg, f, 800))
    s = 64 if n_linhas == 1 else 46
    texto_pixel(img, vg, s, W // 2, yy + (34 if n_linhas == 1 else 18), E.AMARELO, larg=800, entre=1.45)
    # seta "próxima fase"
    seta_pixel(d, W // 2, y0 + th + 34, p=11)
    # cartão do tabuleiro
    cw, ch = 900, 700
    cy0 = y0 + th + 130
    card = E.bloco(cw, ch, CREME, raio=40, ow=8, sombra=14)
    img.alpha_composite(card, ((W - cw) // 2, cy0))
    pl = E.pilula("VAI CURTIR", 34, E.LARANJA, (255, 255, 255), fonte_titulo=True)
    img.alpha_composite(pl, ((W - pl.width) // 2, cy0 - pl.height // 2 - 4))
    cx_img = E.jogo(os.path.join(AC, caixa), 360, larg=420)
    img.alpha_composite(cx_img, ((W - cx_img.width) // 2, cy0 + 58))
    y = cy0 + 58 + cx_img.height + 10
    t = E.titulo(nome, 66, cor=E.LARANJA, larg_max=820)
    img.alpha_composite(t, ((W - t.width) // 2, y))
    y += t.height + 2
    fi = E.texto(ficha(site), 27, cor=E.PETROLEO, peso=800, larg_max=820)
    img.alpha_composite(fi, ((W - fi.width) // 2, y))
    y += fi.height + 6
    fr = E.texto(frase, 31, cor=E.MARROM, peso=600, larg_max=780, entre=1.3)
    img.alpha_composite(fr, ((W - fr.width) // 2, y))
    lg = E.logo(170)
    img.alpha_composite(lg, ((W - lg.width) // 2, 34))
    return img


def tela_capa():
    img = fundo(1)
    d = ImageDraw.Draw(img)
    for k in range(3):
        coracao(d, 60 + k * 66, 56)
    f = pixel(26)
    d.text((W - 57, 65), "1UP", font=f, fill=(0, 0, 0), anchor="ra")
    d.text((W - 60, 62), "1UP", font=f, fill=E.AMARELO, anchor="ra")
    tw, th = 920, 470
    crt = tela_crt(tw, th)
    y0 = 150
    img.alpha_composite(crt, ((W - tw) // 2, y0))
    sv = E.texto("SE VOCÊ JOGA", 50, cor=CIANO, peso=900)
    img.alpha_composite(sv, ((W - sv.width) // 2, y0 + 50))
    y = y0 + 50 + sv.height
    y = texto_pixel(img, "VIDEOGAME...", 66, W // 2, y + 26, E.AMARELO, larg=840)
    texto_pixel(img, "PRESS START", 30, W // 2, y + 70, (255, 255, 255), larg=820)
    t = E.titulo("...VAI CURTIR ESSES\nJOGOS DE TABULEIRO!", 84, cor=E.AMARELO, larg_max=960)
    img.alpha_composite(t, ((W - t.width) // 2, y0 + th + 40))
    caixas = [os.path.join(AC, p[3]) for p in PARES[:5]]
    lq = E.leque(caixas, 290)
    if lq.width > W - 40:
        lq = lq.resize((W - 40, int(lq.height * (W - 40) / lq.width)), Image.LANCZOS)
    img.alpha_composite(lq, ((W - lq.width) // 2, y0 + th + 40 + t.height - 10))
    lg = E.logo(170)
    img.alpha_composite(lg, ((W - lg.width) // 2, 34))
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--teste" in sys.argv:
        a, b = tela_capa(), tela_par(0)
        f = Image.new("RGB", (W * 2 + 40, H), (255, 255, 255))
        f.paste(a.convert("RGB"), (0, 0))
        f.paste(b.convert("RGB"), (W + 40, 0))
        f.save(os.path.join(OUT, "teste.jpg"), quality=90)
        print("ok teste")
        return


if __name__ == "__main__":
    main()
