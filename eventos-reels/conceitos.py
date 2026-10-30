#!/usr/bin/env python3
"""3 visuais para o vídeo da MONITORIA EM EVENTOS da Sua Vez (30/out/2026), no mesmo momento do vídeo:
  A MONTE SEU EVENTO: tela de app com controles (quantas pessoas, idade, clima agitado/tranquilo) e a seleção de jogos
    (fotos do site) que muda conforme os controles: mostra que a quantidade e o tipo de jogo dependem do evento;
  B LETREIRO DE FELTRO: o quadro de letras brancas encaixadas no feltro preto (o das festas), as frases se montando
    letra a letra, fotos dos jogos presas com fita ao lado;
  C TRILHA DO ABC: as cidades do ABC como casas de uma trilha de tabuleiro, o logo da Sua Vez andando até o evento.
Fatos usados (o que eles passaram; ainda NÃO fizeram evento, então nada de "já atendemos"): levam os jogos e ficam o evento
todo ensinando; qualquer tipo de evento; jogos conforme número e perfil das pessoas; crianças e adultos, agitados e
tranquilos; principalmente o ABC Paulista; orçamento pelo Direct ou WhatsApp.

    python3 conceitos.py      # out/conceitos.jpg
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
sys.path.insert(0, os.path.join(REPO, "listas-reels"))
import estilo as E  # noqa: E402
from base import foto  # noqa: E402

W, H = 1080, 1920
OUT = os.path.join(ROOT, "out")
JOGOS = ["happy_salmon", "uga_buga", "telma", "dixit", "ref_o_jogo_da_refer_ncia", "go_cuckoo"]


def t(img, txt, s, x, y, cor=E.MARROM, f="lilita", anchor="mm", sw=0, sc=E.MARROM):
    d = ImageDraw.Draw(img)
    fonte = E.lilita(s) if f == "lilita" else E.fig(s)
    d.text((x, y), txt, font=fonte, fill=cor, anchor=anchor, stroke_width=sw, stroke_fill=sc)


# ---------------------------------------------------------------- A
def slider(img, x, y, w, rotulo, valor, u):
    t(img, rotulo, 38, x, y, E.BRANCO, "fig", "lm")
    t(img, valor, 44, x + w, y, E.AMARELO, "lilita", "rm")
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x, y + 40, x + w, y + 62), radius=11, fill=(14, 84, 104))
    d.rounded_rectangle((x, y + 40, x + w * u, y + 62), radius=11, fill=E.AMARELO)
    d.ellipse((x + w * u - 26, y + 25, x + w * u + 26, y + 77), fill=E.BRANCO, outline=E.MARROM, width=5)


def conceito_app():
    img = Image.new("RGBA", (W, H), E.PETROLEO + (255,))
    d = ImageDraw.Draw(img)
    for y in range(30, H, 60):
        for x in range(30 + (30 if (y // 60) % 2 else 0), W, 60):
            d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(40, 140, 166))
    E.cola(img, E.titulo("MONTE SEU\nEVENTO", 120, E.AMARELO), W / 2, 300, -2)
    painel = E.bloco(900, 1140, (22, 98, 120), raio=50, ow=7, sombra=14)
    img.alpha_composite(painel, (90, 470))
    slider(img, 150, 540, 780, "Quantas pessoas?", "40", 0.45)
    slider(img, 150, 680, 780, "Idade", "crianças + adultos", 0.8)
    slider(img, 150, 820, 780, "Clima", "agitado", 0.25)
    t(img, "A gente leva:", 44, 150, 980, E.BRANCO, "lilita", "lm")
    for k, n in enumerate(JOGOS):
        x, y = 240 + (k % 3) * 300, 1140 + (k // 3) * 290
        E.cola(img, foto(n, 250, sombra_a=0.35), x, y, (k % 3 - 1) * 2)
    E.cola(img, E.pilula("+ MONITORES O EVENTO TODO", 40, E.AMARELO), W / 2, 1700, 1.5)
    img.alpha_composite(E.logo(200), (W - 236, 46))
    return img


# ---------------------------------------------------------------- B
def feltro():
    img = Image.new("RGBA", (W, H), (226, 214, 196, 255))  # parede clara
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((70, 230, W - 70, 1180), radius=18, fill=(150, 108, 70))  # moldura de madeira
    d.rectangle((100, 260, W - 100, 1150), fill=(30, 30, 32))
    for y in range(275, 1150, 26):  # sulcos do feltro
        d.line((100, y, W - 100, y), fill=(20, 20, 22), width=3)
    return img


def letras(img, txt, s, y, cor=(246, 246, 240)):
    f = E.fig(s, 800)
    d = ImageDraw.Draw(img)
    d.text((W / 2 + 3, y + 4), txt, font=f, fill=(10, 10, 10), anchor="mm")  # sombra da letra encaixada
    d.text((W / 2, y), txt, font=f, fill=cor, anchor="mm")


def conceito_feltro():
    img = feltro()
    for k, (txt, cor) in enumerate((("SUA FESTA", None), ("PRECISA DE", None), ("JOGOS", (255, 199, 31)),
                                    ("A GENTE LEVA", None), ("E FICA ENSINANDO", None), ("O EVENTO TODO", None))):
        letras(img, txt, (92 if len(txt) < 14 else 78) if k != 2 else 130, 360 + k * 135 + (20 if k > 2 else 0), cor or (246, 246, 240))
    for k, n in enumerate(JOGOS[:4]):  # fotos presas com fita
        x, y = 200 + k * 230, 1420 + (k % 2) * 60
        rot = (-6, 4, -3, 7)[k]
        im = foto(n, 230, sombra_a=0.3)
        E.cola(img, im, x, y, rot)
        fita = Image.new("RGBA", (120, 40), (240, 226, 170, 210))
        E.cola(img, fita, x, y - 120, rot + 8)
    img.alpha_composite(E.logo(200), (W - 236, 40))
    return img


# ---------------------------------------------------------------- C
CIDADES = ["SANTO ANDRÉ", "SÃO BERNARDO", "SÃO CAETANO", "DIADEMA", "MAUÁ", "RIBEIRÃO PIRES", "RIO GRANDE DA SERRA"]


def conceito_trilha():
    img = E.fundo_xadrez(W, H, base=(255, 214, 90), escuro=(250, 202, 70), casa=120)
    E.cola(img, E.titulo("A GENTE VAI\nATÉ O SEU EVENTO", 92, E.BRANCO), W / 2, 260, -2)
    pts = [(250, 560), (560, 520), (850, 640), (760, 900), (430, 960), (220, 1200), (520, 1360)]
    d = ImageDraw.Draw(img)
    for a, b in zip(pts, pts[1:]):  # trilha pontilhada
        n = int(math.dist(a, b) / 34)
        for j in range(1, n):
            x, y = a[0] + (b[0] - a[0]) * j / n, a[1] + (b[1] - a[1]) * j / n
            d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=E.MARROM)
    for k, ((x, y), c) in enumerate(zip(pts, CIDADES)):
        cor = E.LARANJA if c == "MAUÁ" else (E.PETROLEO if k % 2 else E.BRANCO)
        fg = E.BRANCO if cor != E.BRANCO else E.MARROM
        E.cola(img, E.bloco(250, 120, cor, raio=24, ow=6, sombra=9), x, y, (k % 3 - 1) * 3)
        f = E.fig(30 if len(c) < 13 else 24, 900)
        d = ImageDraw.Draw(img)
        linhas = c.split(" ", 1) if len(c) > 12 else [c]
        for j, l in enumerate(linhas):
            d.text((x - 5, y - 6 + (j - (len(linhas) - 1) / 2) * 32), l, font=f, fill=fg, anchor="mm")
    E.cola(img, E.logo(230), 520, 1220, 4)  # o "peão" é o logo (nada de peça desenhada à mão)
    E.cola(img, E.pilula("SEU EVENTO AQUI!", 46, E.BRANCO), 520, 1500, -2)
    E.cola(img, E.pilula("ORÇAMENTO PELO WHATSAPP", 38, E.PETROLEO, E.BRANCO), W / 2, 1680, 1)
    img.alpha_composite(E.logo(200), (W - 236, 46))
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    ims = [conceito_app(), conceito_feltro(), conceito_trilha()]
    nomes = ["A · MONTE SEU EVENTO", "B · LETREIRO DE FELTRO", "C · TRILHA DO ABC"]
    sh = Image.new("RGB", (3 * 560 + 40, 1060), (255, 255, 255))
    d = ImageDraw.Draw(sh)
    for k, (im, n) in enumerate(zip(ims, nomes)):
        sh.paste(im.convert("RGB").resize((540, 960), Image.LANCZOS), (20 + k * 560, 80))
        d.text((20 + k * 560 + 270, 40), n, font=E.lilita(36), fill=E.MARROM, anchor="mm")
    sh.save(os.path.join(OUT, "conceitos.jpg"), quality=92)
    print("ok")


if __name__ == "__main__":
    main()
