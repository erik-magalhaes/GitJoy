#!/usr/bin/env python3
"""3º comparativo antigo × moderno (14/out/2026). Pedido dele: "nesse tema a gente mantém o MESMO design" do
"Curte esse clássico?" (carrosseis2.py, antes × depois em papel envelhecido, 1080 x 1080), com jogos NOVOS.
Pares (os modernos estão no acervo; nenhum repete posts anteriores): Ludo → Camel Up, Xadrez → Hive, Stop → Tapalavras,
Banco Imobiliário → Bohnanza, Lince → Spot it! Hip e os 2 extras que ele pediu: Truco → Coup, Super Trunfo → 1, 2, 3, Lucha!
Clássicos = fotos da Ri Happy recortadas (cl_*.png); modernos = recortes das fotos do site (hobby-reels/assets/acervo).

    python3 classicos3.py      # out/v3_classicos/01.png ... e todas.jpg
"""
import math

import numpy as np
from PIL import Image, ImageDraw

import carrosseis2 as c2
from carrosseis2 import (S, NAVY, WHITE, font, cola, sombra, letreiro, pilula, caixa, quebra, papel_velho,
                         corte_rasgado, logo_card, ORANGE)

PARES = [  # (clássico, recorte do clássico, recorte do moderno, nome do moderno, nome no site, motivo)
    ("LUDO", "cl_ludo", "camel_up_second_edition", "CAMEL UP", "Camel Up (Second Edition)",
     "Corrida com dados, mas os camelos se empilham e você aposta em quem vai ganhar."),
    ("XADREZ", "cl_xadrez", "hive", "HIVE", "Hive",
     "Estratégia a dois, sem tabuleiro: cerque a abelha rainha do adversário."),
    ("STOP", "cl_stop", "tapalavras", "TAPALAVRAS", "Tapalavras",
     "Fale uma palavra da categoria e aperte a letra antes que o tempo acabe."),
    ("BANCO IMOBILIÁRIO", "cl_banco", "bohnanza", "BOHNANZA", "Bohnanza",
     "Negociação o tempo todo, mas plantando feijões. E sem partida que dura a tarde inteira."),
    ("LINCE", "cl_lince", "spot_it_hip", "SPOT IT! HIP", "Spot it! Hip",
     "Ache a figura igual: entre duas cartas, sempre tem exatamente uma."),
    ("TRUCO", "cl_baralho", "coup_inquisition", "COUP", "Coup: Inquisition",
     "Blefe é tudo: diga que tem a carta, mesmo sem ter. Alguém vai duvidar?"),
    ("SUPER TRUNFO", "cl_trunfo", "1_2_3_lucha", "1, 2, 3, LUCHA!", "1, 2, 3, Lucha!",
     "Duelo de atributos, mas com luchadores e cartas reveladas ao mesmo tempo."),
]
CORES = [(234, 88, 12), (37, 99, 235), (147, 51, 234), (22, 163, 74), (219, 39, 119), (13, 148, 136), (202, 138, 4)]


def info(nome_site):
    d = c2.SITE[nome_site]
    a, b = d["jogadores"].split("–")
    jog = f"{a} JOGADORES" if a == b else f"{a} A {b} JOGADORES"
    return f"{jog} · {d['tempo'].replace('min', ' MIN')}"


def envelhece(im):
    return Image.fromarray((np.asarray(im).astype(np.float32) * np.array([0.96, 0.9, 0.78, 1.0])).clip(0, 255)
                           .astype(np.uint8))


def antes_depois(k):
    cl, ci, n, nome, ns, mot = PARES[k]
    cor = CORES[k]
    img = Image.new("RGBA", (S, S), cor + (255,))
    d = ImageDraw.Draw(img)
    for j in range(16):  # raios no "depois"
        a0, a1 = j * math.tau / 16, (j + 0.5) * math.tau / 16
        d.polygon([(780, 800), (780 + 1600 * math.cos(a0), 800 + 1600 * math.sin(a0)),
                   (780 + 1600 * math.cos(a1), 800 + 1600 * math.sin(a1))], fill=tuple(min(255, c + 22) for c in cor))
    img.alpha_composite(papel_velho(), (0, 0))
    d = ImageDraw.Draw(img)
    cola(img, pilula("ANTES", 34, (120, 90, 55), (250, 240, 220), (120, 90, 55)), 150, 90, -4)
    cola(img, sombra(envelhece(caixa(ci, 250, 330)), 10, (5, 8), 0.35), 230, 270, -5)
    tam = 70 if len(cl) < 9 else (54 if len(cl) < 13 else 40)
    d.text((720, 210), "CURTE", font=font("AlfaSlabOne-Regular.ttf", 52), fill=(90, 62, 35), anchor="mm")
    d.text((720, 285), f"{cl}?", font=font("AlfaSlabOne-Regular.ttf", tam), fill=(90, 62, 35), anchor="mm")
    d.text((720, 370), "o clássico que todo", font=font("Poppins-SemiBold.ttf", 30), fill=(120, 90, 55), anchor="mm")
    d.text((720, 408), "mundo já jogou", font=font("Poppins-SemiBold.ttf", 30), fill=(120, 90, 55), anchor="mm")
    corte_rasgado(img, 455)
    cola(img, pilula("DEPOIS", 34, NAVY, WHITE, WHITE), 160, 545, 3)
    cola(img, sombra(caixa(n, 400, 380), 16, (8, 14), 0.4), 800, 760, 4)
    d = ImageDraw.Draw(img)
    f = font("Poppins-Black.ttf", 44)
    y = 640
    for l in quebra(nome, f, 520):
        d.text((60, y), l, font=f, fill=WHITE, anchor="lm", stroke_width=3, stroke_fill=NAVY)
        y += 54
    fm = font("Poppins-SemiBold.ttf", 31)
    for l in quebra(mot, fm, 520):
        d.text((60, y + 10), l, font=fm, fill=WHITE, anchor="lm")
        y += 42
    pl = pilula(info(ns), 26, NAVY)
    cola(img, pl, 60 + pl.width / 2, y + 50)
    return img


def capa():
    img = Image.new("RGBA", (S, S), CORES[0] + (255,))
    img.alpha_composite(papel_velho(), (0, 0))
    d = ImageDraw.Draw(img)
    d.text((540, 95), "OS CLÁSSICOS", font=font("AlfaSlabOne-Regular.ttf", 80), fill=(90, 62, 35), anchor="mm")
    for j, p in enumerate(PARES):  # 4 em cima, 3 embaixo (meio a meio)
        x = 135 + j * 270 if j < 4 else 270 + (j - 4) * 270
        y = 250 if j < 4 else 365
        cola(img, sombra(envelhece(caixa(p[1], 120, 170)), 8, (4, 6), 0.3), x, y, (-5, 3, -3, 5, -4, 4, -2)[j])
    corte_rasgado(img, 455)
    for j, p in enumerate(PARES):
        x = 135 + j * 270 if j < 4 else 270 + (j - 4) * 270
        y = 600 if j < 4 else 780
        cola(img, sombra(caixa(p[2], 190, 200), 12, (6, 12), 0.4), x, y, (-6, 3, -3, 6, -4, 4, -2)[j])
    cola(img, letreiro("TÊM VERSÕES MODERNAS!", 62, WHITE, NAVY, 10), 470, 945, -2)
    return img


def main():
    c2.salva("v3_classicos", [capa()] + [antes_depois(k) for k in range(len(PARES))] + [c2.antes_cta()])


if __name__ == "__main__":
    main()
