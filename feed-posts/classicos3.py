#!/usr/bin/env python3
"""3º comparativo antigo × moderno (14–15/out/2026). Pedido dele: "nesse tema a gente mantém o MESMO design" do
"Curte esse clássico?" (carrosseis2.py, antes × depois em papel envelhecido, 1080 x 1080), com jogos NOVOS.
Pares ESCOLHIDOS POR ELE (15/out, "vamos resetar"): Lince → Spot it! Hip, Imagem & Ação → Say my Name e
Xadrez → Hive (pedido de volta) e Scotland Yard → Convidados Indesejados 1 e 2 ("pode colocar os dois na mesma imagem"; NÃO estão no site).
Clássicos = fotos da Ri Happy recortadas (cl_*.png); modernos = recortes das fotos do site (hobby-reels/assets/acervo)
ou caixas oficiais da editora (Convidados Indesejados: Across the Board).

    python3 classicos3.py      # out/v3_classicos/01.png ... e todas.jpg
"""
import math

import numpy as np
from PIL import Image, ImageDraw

import carrosseis2 as c2
from carrosseis2 import (S, NAVY, WHITE, font, cola, sombra, letreiro, pilula, caixa, quebra, papel_velho,
                         corte_rasgado, logo_card, ORANGE)

PARES = [  # (clássico, recorte do clássico, recorte(s) do moderno, nome do moderno, nome no site, motivo)
    ("LINCE", "cl_lince", ["spot_it_hip"], "SPOT IT! HIP", "Spot it! Hip",
     "Ache a figura igual: entre duas cartas, sempre tem exatamente uma."),
    ("IMAGEM & AÇÃO", "cl_imagem", ["say_my_name"], "SAY MY NAME", "Say my Name",
     "Adivinhação em equipe com fala, mímica e até cantoria. E cada rodada fica mais difícil."),
    ("XADREZ", "cl_xadrez", ["hive"], "HIVE", "Hive",  # ele pediu de volta em 15/out
     "Estratégia a dois, sem tabuleiro: cerque a abelha rainha do adversário."),
    ("SCOTLAND YARD", "cl_scotland", ["convidados1", "convidados2"], "CONVIDADOS INDESEJADOS 1 E 2",
     "Convidados Indesejados",
     "Interrogue suspeitos, procure pistas e troque informações: quem matou, como e por quê?"),
]
CORES = [(219, 39, 119), (37, 99, 235), (147, 51, 234), (13, 148, 136)]
FORA_DO_SITE = {"Convidados Indesejados": "1 A 8 JOGADORES · O 2 É PARA DUPLAS"}  # fichas da Across the Board


def info(nome_site):
    if nome_site in FORA_DO_SITE:
        return FORA_DO_SITE[nome_site]
    d = c2.SITE[nome_site]
    a, b = d["jogadores"].split("–")
    jog = f"{a} JOGADORES" if a == b else f"{a} A {b} JOGADORES"
    return f"{jog} · {d['tempo'].replace('min', ' MIN')}"


def moderno(ns, h, larg):
    """Uma caixa, ou duas na mesma imagem (a 2ª um pouco menor, à frente e deslocada)."""
    if len(ns) == 1:
        return caixa(ns[0], h, larg)
    a = caixa(ns[0], int(h * 0.82), int(larg * 0.82))
    b = caixa(ns[1], int(h * 0.72), int(larg * 0.72))
    im = Image.new("RGBA", (int(a.width * 0.55 + b.width), int(a.height * 0.35 + b.height)), (0, 0, 0, 0))
    im.alpha_composite(a, (0, 0))
    sb = sombra(b, 10, (6, 10), 0.35)
    im.alpha_composite(sb, (int(a.width * 0.55) - (sb.width - b.width) // 2, int(a.height * 0.35) - (sb.height - b.height) // 2))
    return im


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
    cola(img, sombra(moderno(n, 400, 380), 16, (8, 14), 0.4), 800, 760, 4)
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
    n = len(PARES)
    passo = 1080 / n
    for j, p in enumerate(PARES):
        x = passo * (j + 0.5)
        cola(img, sombra(envelhece(caixa(p[1], 170, passo - 40)), 8, (4, 6), 0.3), x, 290, (-5, 3, -4, 4)[j % 4])
    corte_rasgado(img, 455)
    for j, p in enumerate(PARES):
        x = passo * (j + 0.5)
        cola(img, sombra(moderno(p[2], 280, passo - 20), 12, (6, 12), 0.4), x, 690, (-6, 3, 5, -3)[j % 4])
    cola(img, letreiro("TÊM VERSÕES MODERNAS!", 62, WHITE, NAVY, 10), 470, 945, -2)
    return img


def main():
    c2.salva("v3_classicos", [capa()] + [antes_depois(k) for k in range(len(PARES))] + [c2.antes_cta()])


if __name__ == "__main__":
    main()
