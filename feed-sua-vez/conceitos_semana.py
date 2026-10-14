#!/usr/bin/env python3
"""3 visuais para o carrossel "Avaliando os jogos que jogamos essa semana" (14/out/2026), mostrados com a mesma tela
(Splendor Duel, nota 8 do Erik): A boletim no caderno, B trilha de pontos do tabuleiro, C medidor de game show.

    python3 conceitos_semana.py    # out/conceitos_semana.jpg
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
from estilo import (MARROM, PETROLEO, LARANJA, AMARELO, BRANCO, titulo, texto, bloco, pilula, logo, peao,  # noqa
                    cola, lilita)

W, H = 1080, 1350
MAO = os.path.join(REPO, "architects-reels", "assets", "fonts", "ArchitectsDaughter-Regular.ttf")
FOTO = os.path.join(REPO, "hobby-reels", "assets", "acervo_foto", "splendor_duel.jpg")
NOME, NOTA = "SPLENDOR DUEL", 8
FALA = "Ótimo pra duas pessoas e ótimo pra ter briga. Minha esposa ficou bem brava ontem... mas eu ganhei!"
VERMELHO = (214, 48, 49)


def mao(s):
    return ImageFont.truetype(MAO if os.path.exists(MAO) else
                              next(os.path.join(r, f) for r, _, fs in os.walk(REPO) for f in fs
                                   if f == "ArchitectsDaughter-Regular.ttf"), s)


def escrito(txt, s, cor, larg):
    f = mao(s)
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    linhas, atual = [], ""
    for p in txt.split(" "):
        t = (atual + " " + p).strip()
        if d0.textlength(t, font=f) > larg and atual:
            linhas.append(atual)
            atual = p
        else:
            atual = t
    linhas.append(atual)
    im = Image.new("RGBA", (larg + 20, int(len(linhas) * s * 1.35 + 20)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k, l in enumerate(linhas):
        d.text((10, 10 + k * s * 1.35), l, font=f, fill=cor)
    return im


def foto(lado, borda=0):
    im = Image.open(FOTO).convert("RGBA").resize((lado, lado), Image.LANCZOS)
    if not borda:
        return im
    b = Image.new("RGBA", (lado + 2 * borda, lado + 2 * borda + borda * 3), BRANCO + (255,))
    b.alpha_composite(im, (borda, borda))
    return b


def fita(w=170, h=52):
    im = Image.new("RGBA", (w, h), (238, 222, 170, 215))
    return im


def opcao_a():
    """Boletim: folha de caderno, polaroide colada com fita, nota em vermelho circulada à mão."""
    img = Image.new("RGBA", (W, H), (253, 250, 240, 255))
    d = ImageDraw.Draw(img)
    for y in range(190, H, 58):
        d.line((0, y, W, y), fill=(178, 208, 232), width=3)
    d.line((120, 0, 120, H), fill=(236, 140, 140), width=4)
    for y in range(150, H, 260):
        d.ellipse((38, y, 78, y + 40), fill=(230, 226, 214))
    cola(img, titulo("AVALIANDO OS JOGOS DA SEMANA", 50, BRANCO, larg_max=860), 590, 95, -1)
    p = foto(500, 26)
    cola(img, p, 420, 520, -4)
    cola(img, fita(), 420, 215, 3)
    cola(img, titulo(NOME, 84, LARANJA), 600, 905, -2)
    r = Image.new("RGBA", (330, 260), (0, 0, 0, 0))
    dr = ImageDraw.Draw(r)
    dr.text((165, 128), f"{NOTA}/10", font=mao(130), fill=VERMELHO, anchor="mm")
    dr.ellipse((14, 20, 316, 236), outline=VERMELHO, width=8)
    cola(img, r, 860, 520, 8)
    cola(img, escrito(FALA, 44, (40, 52, 120), 820), 590, 1100)
    cola(img, escrito("— Erik", 44, (40, 52, 120), 200), 900, 1255)
    return img


def opcao_b():
    """Trilha de pontos: a borda é a trilha 0–10 do tabuleiro e o peão para na nota."""
    img = Image.new("RGBA", (W, H), (250, 238, 214, 255))
    cores = [AMARELO, LARANJA, PETROLEO, (108, 63, 160), VERMELHO]
    casas = []
    n_top, lado = 11, 98
    for k in range(n_top):
        casas.append((22 + k * lado, 22))
    d = ImageDraw.Draw(img)
    for k, (x, y) in enumerate(casas):
        c = cores[k % 5]
        d.rounded_rectangle((x, y, x + lado - 8, y + lado - 8), radius=18, fill=c, outline=MARROM, width=6)
        d.text((x + (lado - 8) / 2, y + (lado - 8) / 2 + 3), str(k), font=lilita(52),
               fill=MARROM if c == AMARELO else BRANCO, anchor="mm")
    cola(img, peao(120, BRANCO), casas[NOTA][0] + 45, 185, -6)
    cola(img, titulo("JOGOS DA SEMANA", 64, BRANCO), W / 2, 220, -1)
    card = bloco(520, 520, BRANCO, raio=36, ow=8, sombra=14)
    card.alpha_composite(foto(500), (10, 10))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, 520, 520), radius=36, outline=MARROM, width=8)
    cola(img, card, 330, 580, -3)
    nota = bloco(300, 300, PETROLEO, raio=150, ow=8, sombra=14)
    cola(nota, titulo(str(NOTA), 170, AMARELO), 150, 135)
    cola(nota, texto("de 10", 40, BRANCO, 900), 150, 235)
    cola(img, nota, 820, 560, 6)
    cola(img, titulo(NOME, 92, LARANJA), W / 2, 935, -2)
    bal = bloco(900, 230, BRANCO, raio=40, ow=7, sombra=10)
    cola(bal, texto("“" + FALA + "”", 36, MARROM, 700, larg_max=820), 450, 115)
    cola(img, bal, W / 2, 1145, 1)
    return img


def opcao_c():
    """Medidor de game show: ponteiro de 0 a 10 sobre um arco colorido, mesa escura."""
    img = Image.new("RGBA", (W, H), (44, 28, 20, 255))
    d = ImageDraw.Draw(img)
    for r in range(900, 0, -30):
        a = int(40 * (1 - r / 900))
        d.ellipse((W / 2 - r, 300 - r * 0.7, W / 2 + r, 300 + r * 0.7), fill=(44 + a, 28 + a // 2, 20 + a // 3))
    cola(img, titulo("NOTA DA SEMANA", 70, AMARELO), W / 2, 90, 0)
    card = bloco(400, 400, BRANCO, raio=30, ow=8, sombra=12)
    card.alpha_composite(foto(380), (10, 10))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, 400, 400), radius=30, outline=MARROM, width=8)
    cola(img, card, W / 2, 360, -2)
    cx, cy, R = W / 2, 950, 330
    arco = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    da = ImageDraw.Draw(arco)
    seq = [VERMELHO, VERMELHO, LARANJA, LARANJA, AMARELO, AMARELO, (150, 200, 60), (150, 200, 60), (60, 170, 80),
           (60, 170, 80)]
    for k in range(10):
        a0, a1 = 180 + k * 18, 180 + (k + 1) * 18
        da.pieslice((cx - R, cy - R, cx + R, cy + R), a0, a1, fill=seq[k], outline=MARROM, width=6)
    da.ellipse((cx - R + 110, cy - R + 110, cx + R - 110, cy + R - 110), fill=(44, 28, 20))
    img.alpha_composite(arco)
    for k in range(11):
        a = math.radians(180 + k * 18)
        d.text((cx + (R + 34) * math.cos(a), cy + (R + 34) * math.sin(a)), str(k), font=lilita(40), fill=BRANCO,
               anchor="mm")
    a = math.radians(180 + NOTA * 18)
    d.line((cx, cy, cx + (R - 40) * math.cos(a), cy + (R - 40) * math.sin(a)), fill=BRANCO, width=16)
    d.ellipse((cx - 34, cy - 34, cx + 34, cy + 34), fill=BRANCO, outline=MARROM, width=6)
    cola(img, titulo(f"{NOTA}/10", 120, BRANCO), cx, cy - 115)
    d.rectangle((0, cy + 10, W, H), fill=(44, 28, 20))
    cola(img, titulo(NOME, 84, LARANJA), W / 2, 1040, -1)
    cola(img, texto("“" + FALA + "”", 36, BRANCO, 700, larg_max=900), W / 2, 1195)
    return img


def main():
    ops = [opcao_a(), opcao_b(), opcao_c()]
    folha = Image.new("RGB", (3 * 540 + 40, 675 + 90), (255, 255, 255))
    d = ImageDraw.Draw(folha)
    for k, im in enumerate(ops):
        folha.paste(im.convert("RGB").resize((540, 675), Image.LANCZOS), (10 + k * 550, 80))
        d.text((10 + k * 550 + 270, 40), ("1 · BOLETIM NO CADERNO", "2 · TRILHA DE PONTOS", "3 · MEDIDOR")[k],
               font=lilita(40), fill=MARROM, anchor="mm")
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    folha.save(os.path.join(ROOT, "out", "conceitos_semana.jpg"), quality=90)
    print("ok")


if __name__ == "__main__":
    main()
