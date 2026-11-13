#!/usr/bin/env python3
"""CRACHÁ da monitoria para a Tarde de Jogos no Beca’s Café (5/nov/2026). Ele: "a gente queria economizar na camiseta;
temos cordões de pescoço, pensei em crachás; me dá opções de design".

10 x 14 cm em pé (cabe no porta-crachá de PVC comum), 300 dpi. 3 opções:
  A  guarda-chuvinhas (mesma cara da divulgação do evento)
  B  carta de jogo (crachá como uma carta: nome, "classe: MONITOR", habilidade)
  C  bloco de cor forte (lê de longe: MONITORIA enorme + QR do acervo no pé)

    /usr/bin/python3 cracha.py      → out/becas/cracha_opcoes.jpg + cracha_{A,B,C}_A4.pdf (4 por folha: Erik,
                                      Jéssica e 2 com o nome em branco para escrever à mão)
"""
import os
import random

from PIL import Image, ImageDraw

import tarde_becas as TB
from tarde_becas import E, MAR, PET, LAR, AMA, BR, ROSA, CREME

DPI = 300
CW, CH = int(10 / 2.54 * DPI), int(14 / 2.54 * DPI)  # 1181 x 1653
OUT = TB.OUT
NOMES = ["ERIK", "JÉSSICA", None, None]


def furo(d):
    """Marca do furo do cordão (para quem for usar sem porta-crachá)."""
    d.rounded_rectangle((CW / 2 - 70, 46, CW / 2 + 70, 74), 14, outline=(170, 160, 150), width=3)


def linha_nome(d, y, cor):
    d.line((150, y, CW - 150, y), fill=cor, width=4)


def nome(img, txt, y, cor, contorno=MAR, s=170):
    if txt:
        E.cola(img, E.titulo(txt, s, cor, contorno=contorno, larg_max=CW - 160), CW / 2, y, -1.5)
    else:
        linha_nome(ImageDraw.Draw(img), y + 50, contorno)


# ---------------------------------------------------------------- A: guarda-chuvinhas
def cracha_a(n):
    img = TB.fundo(CW, CH, [90, 170, 70, 150, 80], 175)
    d = ImageDraw.Draw(img)
    furo(d)
    lg = E.logo(470)
    img.alpha_composite(lg, (int(CW / 2 - lg.width / 2), 400))
    E.cola(img, E.pilula("MONITORIA", 74, PET, BR, fonte_titulo=True), CW / 2, 790, -2)
    nome(img, n, 1010, LAR)
    E.cola(img, E.pilula("Dúvida no jogo? Me chama!", 46, AMA, MAR), CW / 2, 1240, 1.5)
    E.cola(img, TB.parceria(118), CW / 2, 1480, 0)
    return img


# ---------------------------------------------------------------- B: carta de jogo
def cracha_b(n):
    img = Image.new("RGBA", (CW, CH), PET + (255,))
    d = ImageDraw.Draw(img)
    rnd = random.Random(5)
    for _ in range(140):  # pontinhos claros no fundo petróleo
        x, y, r = rnd.uniform(0, CW), rnd.uniform(0, CH), rnd.uniform(3, 6)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(60, 150, 175))
    furo(d)
    m = 70  # a "carta" creme dentro
    d.rounded_rectangle((m + 10, 120 + 12, CW - m + 10, CH - 70 + 12), 50, fill=MAR)
    d.rounded_rectangle((m, 120, CW - m, CH - 70), 50, fill=CREME, outline=MAR, width=8)
    # índice no canto, como carta de baralho
    for (x, y, rot) in ((m + 70, 205, 0), (CW - m - 70, CH - 155, 180)):
        t = E.titulo("S\nV", 64, LAR, larg_max=200)
        E.cola(img, t, x, y, rot)
    lg = E.logo(400)
    img.alpha_composite(lg, (int(CW / 2 - lg.width / 2), 210))
    d.text((CW / 2, 600), "CLASSE:", font=E.fig(40, 800), fill=PET, anchor="mm")
    E.cola(img, E.titulo("MONITOR" if n != "JÉSSICA" else "MONITORA", 120, AMA, larg_max=CW - 260), CW / 2, 690, 0)
    nome(img, n, 900, LAR, s=150)
    d = ImageDraw.Draw(img)
    # caixa de habilidade
    bx0, by0, bx1, by1 = m + 60, 1080, CW - m - 60, 1380
    d.rounded_rectangle((bx0, by0, bx1, by1), 26, fill=BR, outline=MAR, width=5)
    d.text((CW / 2, by0 + 50), "HABILIDADE ESPECIAL", font=E.lilita(46), fill=ROSA, anchor="mm")
    for k, t in enumerate(["Explica qualquer jogo", "em poucos minutos.", "Me chama na sua mesa!"]):
        d.text((CW / 2, by0 + 125 + k * 56), t, font=E.fig(42, 800 if k < 2 else 900), fill=MAR if k < 2 else PET,
               anchor="mm")
    E.cola(img, TB.parceria(100), CW / 2, 1470, 0)
    return img


# ---------------------------------------------------------------- C: bloco de cor (lê de longe)
def cracha_c(n):
    img = Image.new("RGBA", (CW, CH), LAR + (255,))
    d = ImageDraw.Draw(img)
    for k in range(-CH, CW, 90):  # listras diagonais sutis
        d.line((k, 0, k + CH, CH), fill=(248, 150, 60), width=30)
    furo(d)
    lg = E.logo(420)
    img.alpha_composite(lg, (int(CW / 2 - lg.width / 2), 140))
    E.cola(img, E.titulo("MONI\nTORIA", 210, BR, larg_max=CW - 120), CW / 2, 640, -2)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((90, 905, CW - 90, 1135), 34, fill=BR, outline=MAR, width=7)
    if n:
        E.cola(img, E.titulo(n, 140, (64, 170, 200), larg_max=CW - 260), CW / 2, 1020, 0)  # 5/nov: nome mais claro (pedido)
    else:
        d.line((170, 1070, CW - 170, 1070), fill=MAR, width=4)
    # QR do acervo + chamada
    q = TB.qr(250)
    img.paste(q, (110, 1230))
    d.rounded_rectangle((100, 1220, 370, 1490), 18, outline=MAR, width=5)
    d.text((410, 1270), "Gostou do jogo?", font=E.fig(44, 900), fill=BR, anchor="lm")
    d.text((410, 1330), "Aluga e joga", font=E.fig(44, 900), fill=MAR, anchor="lm")
    d.text((410, 1385), "em casa!", font=E.fig(44, 900), fill=MAR, anchor="lm")
    d.text((410, 1450), "@suavez_bg", font=E.fig(40, 900), fill=BR, anchor="lm")
    E.cola(img, TB.logo_becas(110), CW - 150, CH - 95, 3)
    return img


# ---------------------------------------------------------------- D: ingresso (2ª rodada, 5/nov)
def cracha_d(n):
    img = Image.new("RGBA", (CW, CH), MAR + (255,))
    d = ImageDraw.Draw(img)
    rnd = random.Random(9)
    for _ in range(120):
        x, y, r = rnd.uniform(0, CW), rnd.uniform(0, CH), rnd.uniform(3, 6)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(95, 60, 38))
    furo(d)
    m, top, bot, corte = 70, 120, CH - 60, 1200
    d.rounded_rectangle((m, top, CW - m, bot), 40, fill=CREME)
    for x in (m, CW - m):  # recortes do picote
        d.ellipse((x - 45, corte - 45, x + 45, corte + 45), fill=MAR)
    for x in range(m + 60, CW - m - 60, 38):
        d.line((x, corte, x + 20, corte), fill=(180, 160, 140), width=5)
    d.rectangle((m, top, CW - m, top + 120), fill=LAR)
    d.rounded_rectangle((m, top, CW - m, top + 160), 40, fill=None)
    d.text((CW / 2, top + 62), "INGRESSO STAFF · ACESSO TOTAL", font=E.lilita(52), fill=BR, anchor="mm")
    lg = E.logo(380)
    img.alpha_composite(lg, (int(CW / 2 - lg.width / 2), top + 165))
    E.cola(img, E.titulo("MONITORIA", 150, LAR, larg_max=CW - 220), CW / 2, 715, -1.5)
    nome(img, n, 900, PET, s=150)
    d = ImageDraw.Draw(img)
    d.text((CW / 2, 1065), "TARDE DE JOGOS · 20/11 · 13H ÀS 19H", font=E.fig(40, 900), fill=MAR, anchor="mm")
    d.text((CW / 2, 1125), "BECA’S CAFÉ · MAUÁ", font=E.fig(40, 800), fill=PET, anchor="mm")
    # canhoto
    d.text((CW / 2, corte + 85), "VALE 1 EXPLICAÇÃO DE JOGO", font=E.lilita(54), fill=ROSA, anchor="mm")
    d.text((CW / 2, corte + 145), "(ou quantas você precisar!)", font=E.fig(40, 800), fill=MAR, anchor="mm")
    rnd = random.Random(3)
    x = 230
    while x < CW - 230:  # código de barras
        w = rnd.choice((4, 6, 10, 14))
        d.rectangle((x, corte + 200, x + w, corte + 330), fill=MAR)
        x += w + rnd.choice((5, 8, 12))
    d.text((CW / 2, corte + 370), "Nº 0001 · @suavez_bg", font=E.fig(32, 800), fill=MAR, anchor="mm")
    return img


# ---------------------------------------------------------------- E: letras de madeira (tipo Scrabble)
PONTOS = {"A": 1, "E": 1, "I": 1, "O": 1, "S": 1, "R": 1, "T": 1, "M": 1, "N": 3, "C": 2, "K": 5, "J": 5, "É": 1,
          "U": 1, "D": 2, "V": 4, "Z": 8, "Ç": 3, "Ã": 1}


def peca(letra, t, cor=(236, 208, 160)):
    im = Image.new("RGBA", (t + 12, t + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 10, t + 8, t + 10), int(t * 0.14), fill=(120, 80, 45))
    d.rounded_rectangle((0, 0, t, t), int(t * 0.14), fill=cor, outline=(150, 105, 60), width=4)
    d.rounded_rectangle((8, 8, t - 8, t - 8), int(t * 0.1), outline=(250, 230, 195), width=3)
    d.text((t / 2, t / 2 + 2), letra, font=E.lilita(int(t * 0.62)), fill=MAR, anchor="mm")
    d.text((t - 20, t - 18), str(PONTOS.get(letra, 2)), font=E.fig(int(t * 0.2), 900), fill=MAR, anchor="mm")
    return im


def fileira(img, palavra, cy, t, gap=10, rot=True, cor=(236, 208, 160)):
    rnd = random.Random(len(palavra))
    w = len(palavra) * (t + gap) - gap
    x0 = CW / 2 - w / 2
    for k, c in enumerate(palavra):
        p = peca(c, t, cor)
        if rot:
            p = p.rotate(rnd.uniform(-5, 5), expand=True, resample=Image.BICUBIC)
        img.alpha_composite(p, (int(x0 + k * (t + gap) + t / 2 - p.width / 2), int(cy - p.height / 2)))


def cracha_e(n):
    img = Image.new("RGBA", (CW, CH), (250, 244, 232, 255))
    d = ImageDraw.Draw(img)
    for y in range(0, CH, 70):  # bolinhas vermelhas do papel (a referência das letrinhas)
        for x in range((y // 70) % 2 * 35, CW, 70):
            d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=(226, 120, 110))
    furo(d)
    lg = E.logo(400)
    img.alpha_composite(lg, (int(CW / 2 - lg.width / 2), 130))
    fileira(img, "MONITOR" if n != "JÉSSICA" else "MONITORA", 640, 118 if n != "JÉSSICA" else 112, cor=(250, 200, 120))
    if n:
        fileira(img, n, 900, 150 if len(n) <= 5 else 132)
    else:
        for k in range(6):
            img.alpha_composite(peca(" ", 132), (int(CW / 2 - 3 * 142 + k * 142), 830))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((110, 1110, CW - 110, 1330), 30, fill=BR, outline=MAR, width=6)
    d.text((CW / 2, 1175), "TRAVOU NO JOGO?", font=E.lilita(62), fill=LAR, anchor="mm")
    d.text((CW / 2, 1255), "É só me chamar na sua mesa!", font=E.fig(44, 900), fill=MAR, anchor="mm")
    E.cola(img, TB.parceria(110), CW / 2, 1480, 0)
    return img


# ---------------------------------------------------------------- F: trilha de tabuleiro na borda
def cracha_f(n):
    img = Image.new("RGBA", (CW, CH), CREME + (255,))
    d = ImageDraw.Draw(img)
    cores = [LAR, PET, AMA, ROSA, (118, 176, 65)]
    c = 118  # tamanho da casa
    cols, lins = CW // c, CH // c
    ox, oy = (CW - cols * c) / 2, (CH - lins * c) / 2
    casas = [(i, 0) for i in range(cols)] + [(cols - 1, j) for j in range(1, lins)] + \
            [(i, lins - 1) for i in range(cols - 2, -1, -1)] + [(0, j) for j in range(lins - 2, 0, -1)]
    for k, (i, j) in enumerate(casas):
        x, y = ox + i * c, oy + j * c
        d.rectangle((x + 4, y + 4, x + c - 4, y + c - 4), fill=cores[k % 5], outline=MAR, width=4)
    # casa INÍCIO no canto de baixo à esquerda
    x, y = ox, oy + (lins - 1) * c
    d.rectangle((x + 4, y + 4, x + c - 4, y + c - 4), fill=BR, outline=MAR, width=4)
    d.text((x + c / 2, y + c / 2), "INÍCIO", font=E.lilita(28), fill=MAR, anchor="mm")
    d.rounded_rectangle((CW / 2 - 70, oy + 30, CW / 2 + 70, oy + 58), 14, fill=CREME, outline=(170, 160, 150), width=3)
    lg = E.logo(400)
    img.alpha_composite(lg, (int(CW / 2 - lg.width / 2), int(oy + c + 50)))
    E.cola(img, E.pilula("MONITORA" if n == "JÉSSICA" else "MONITOR", 80, PET, BR, fonte_titulo=True), CW / 2, 640, -2)
    nome(img, n, 840, LAR, s=160)
    d = ImageDraw.Draw(img)
    d.text((CW / 2, 1020), "Travou no jogo?", font=E.lilita(60), fill=ROSA, anchor="mm")
    d.text((CW / 2, 1090), "Não volte casas:", font=E.fig(44, 900), fill=MAR, anchor="mm")
    d.text((CW / 2, 1145), "me chama na sua mesa!", font=E.fig(44, 900), fill=MAR, anchor="mm")
    E.cola(img, TB.parceria(100), CW / 2, 1340, 0)
    return img


# ---------------------------------------------------------------- 3ª rodada (5/nov): SÓ SUA VEZ, sem data nem café
# Ele: "mais focado na Sua Vez, sem tanta informação do Beca’s, pra usar em qualquer evento".
AZUL_CLARO = (227, 243, 246)


def monitor(n):
    return "MONITORA" if n == "JÉSSICA" else "MONITOR"


def cracha_g(n):
    """Azul-claro da identidade, trilha pontilhada atravessando, logo grande."""
    img = Image.new("RGBA", (CW, CH), AZUL_CLARO + (255,))
    d = ImageDraw.Draw(img)
    import math
    pts = [(CW * (0.5 + 0.42 * math.sin(t / 26)), t * 1.0) for t in range(0, CH + 40, 4)]
    for k in range(0, len(pts), 9):  # trilha de bolinhas, como casas de um tabuleiro
        x, y = pts[k]
        cor = (LAR, PET, AMA, ROSA)[(k // 9) % 4]
        d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=tuple(int(v + (255 - v) * 0.45) for v in cor))
    furo(d)
    lg = E.logo(640)
    img.alpha_composite(lg, (int(CW / 2 - lg.width / 2), 170))
    E.cola(img, E.pilula(monitor(n), 80, AMA, MAR, fonte_titulo=True), CW / 2, 760, -2)
    nome(img, n, 960, LAR, s=170)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((120, 1200, CW - 120, 1420), 30, fill=BR, outline=MAR, width=6)
    d.text((CW / 2, 1268), "A gente ensina,", font=E.lilita(62), fill=PET, anchor="mm")
    d.text((CW / 2, 1348), "você joga!", font=E.lilita(62), fill=LAR, anchor="mm")
    d.text((CW / 2, 1530), "@suavez_bg", font=E.fig(46, 900), fill=MAR, anchor="mm")
    return img


def seta(w, h, cor):
    im = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = [(0, h * 0.3), (w * 0.55, h * 0.3), (w * 0.55, 0), (w, h / 2), (w * 0.55, h), (w * 0.55, h * 0.7), (0, h * 0.7)]
    d.polygon([(x + 10, y + 10) for x, y in pts], fill=MAR)
    d.polygon(pts, fill=cor, outline=MAR)
    d.line(pts + [pts[0]], fill=MAR, width=6)
    return im


def cracha_h(n):
    """Trocadilho com o nome da loja: o marcador de turno 'É A VEZ DE:' apontando para o nome."""
    img = Image.new("RGBA", (CW, CH), AMA + (255,))
    d = ImageDraw.Draw(img)
    for k in range(-CH, CW, 110):
        d.line((k, 0, k + CH, CH), fill=(255, 210, 70), width=40)
    furo(d)
    lg = E.logo(470)
    img.alpha_composite(lg, (int(CW / 2 - lg.width / 2), 140))
    E.cola(img, E.titulo("É A VEZ DE:", 110, BR, larg_max=CW - 200), CW / 2, 640, -2)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((90 + 12, 760 + 12, CW - 90 + 12, 1000 + 12), 40, fill=MAR)
    d.rounded_rectangle((90, 760, CW - 90, 1000), 40, fill=BR, outline=MAR, width=7)
    if n:
        E.cola(img, E.titulo(n, 150, LAR, larg_max=CW - 330), CW / 2, 880, 0)
    else:
        d.line((230, 930, CW - 230, 930), fill=MAR, width=4)
    E.cola(img, seta(150, 110, PET), 70, 880, 0)
    E.cola(img, seta(150, 110, PET).transpose(Image.FLIP_LEFT_RIGHT), CW - 70, 880, 0)
    E.cola(img, E.pilula(monitor(n) + " DE JOGOS", 62, PET, BR, fonte_titulo=True), CW / 2, 1110, 1.5)
    d = ImageDraw.Draw(img)
    d.text((CW / 2, 1300), "Travou na jogada?", font=E.fig(52, 900), fill=MAR, anchor="mm")
    d.text((CW / 2, 1370), "Me chama que eu explico!", font=E.fig(52, 900), fill=MAR, anchor="mm")
    d.text((CW / 2, 1530), "@suavez_bg", font=E.fig(46, 900), fill=PET, anchor="mm")
    return img


def cracha_i(n):
    """Limpo, de 'equipe': faixa petróleo com o logo, nome numa faixa laranja, QR do acervo no pé."""
    img = Image.new("RGBA", (CW, CH), BR + (255,))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, CW, 640), fill=PET)
    rnd = random.Random(4)
    for _ in range(70):
        x, y, r = rnd.uniform(0, CW), rnd.uniform(0, 640), rnd.uniform(3, 6)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(60, 150, 175))
    furo(d)
    lg = E.logo(600)
    img.alpha_composite(lg, (int(CW / 2 - lg.width / 2), 200))
    d.rectangle((0, 640, CW, 660), fill=AMA)
    d.rectangle((0, 700, CW, 920), fill=LAR)
    if n:
        E.cola(img, E.titulo(n, 160, BR, larg_max=CW - 140), CW / 2, 810, 0)
    else:
        d.line((150, 870, CW - 150, 870), fill=BR, width=5)
    d.text((CW / 2, 1000), monitor(n) + " · JOGOS DE TABULEIRO", font=E.lilita(54), fill=PET, anchor="mm")
    d.line((140, 1065, CW - 140, 1065), fill=(225, 215, 200), width=4)
    q = TB.qr(300)
    img.paste(q, (120, 1150))
    d.text((470, 1200), "Alugue jogos", font=E.lilita(52), fill=LAR, anchor="lm")
    d.text((470, 1260), "de tabuleiro", font=E.lilita(52), fill=LAR, anchor="lm")
    d.text((470, 1330), "e jogue em casa!", font=E.fig(42, 900), fill=MAR, anchor="lm")
    d.text((470, 1410), "@suavez_bg", font=E.fig(42, 900), fill=PET, anchor="lm")
    d.rectangle((0, CH - 60, CW, CH), fill=PET)
    return img


OPCOES = {"A": cracha_a, "B": cracha_b, "C": cracha_c}
OPCOES3 = {"G": cracha_g, "H": cracha_h, "I": cracha_i}
OPCOES2 = {"D": cracha_d, "E": cracha_e, "F": cracha_f}


def folha_a4(f, nomes=None):
    nomes = nomes or NOMES
    A4 = (int(21 / 2.54 * DPI), int(29.7 / 2.54 * DPI))
    fo = Image.new("RGB", A4, (255, 255, 255))
    d = ImageDraw.Draw(fo)
    lins = (len(nomes) + 1) // 2
    mx, my = (A4[0] - 2 * CW) // 2, (A4[1] - lins * CH) // 2
    for k, n in enumerate(nomes):
        fo.paste(f(n).convert("RGB"), (mx + (k % 2) * CW, my + (k // 2) * CH))
    for j in range(3):  # marcas de corte
        x = mx + j * CW
        d.line((x, my - 50, x, my - 12), fill=(120, 120, 120), width=3)
        d.line((x, my + lins * CH + 12, x, my + lins * CH + 50), fill=(120, 120, 120), width=3)
    for j in range(lins + 1):
        y = my + j * CH
        d.line((mx - 50, y, mx - 12, y), fill=(120, 120, 120), width=3)
        d.line((mx + 2 * CW + 12, y, mx + 2 * CW + 50, y), fill=(120, 120, 120), width=3)
    return fo


def folha_dupla(f, nomes=("ERIK", "JÉSSICA"), esc=0.95, sangria=24, gap_cm=1.5):
    """13/nov ("não corre risco de ficar ruim pra cortar?"): os 2 crachás UM EMBAIXO DO OUTRO com 1,5 cm entre eles
    (lado a lado sobravam só 5 mm de margem na A4, a impressora corta), a 95% (9,5 x 13,3 cm: entra folgado no
    porta-crachá 10 x 14) e com 2 mm de SANGRIA (a borda do desenho continua pra fora da linha de corte: se a tesoura
    desviar um pouco, não aparece filete branco). Marcas de corte nos 4 cantos de cada um."""
    import numpy as np
    A4 = (int(21 / 2.54 * DPI), int(29.7 / 2.54 * DPI))
    fo = Image.new("RGB", A4, (255, 255, 255))
    d = ImageDraw.Draw(fo)
    w, h = int(CW * esc), int(CH * esc)
    gap = int(gap_cm / 2.54 * DPI)
    x0 = (A4[0] - w) // 2
    y0 = (A4[1] - 2 * h - gap) // 2
    for k, n in enumerate(nomes):
        c = np.asarray(f(n).convert("RGB").resize((w, h), Image.LANCZOS))
        c = np.pad(c, ((sangria, sangria), (sangria, sangria), (0, 0)), mode="edge")
        y = y0 + k * (h + gap)
        fo.paste(Image.fromarray(c), (x0 - sangria, y - sangria))
        for cx in (x0, x0 + w):  # marcas de corte fora da sangria
            for cy in (y, y + h):
                sx = -1 if cx == x0 else 1
                sy = -1 if cy == y else 1
                d.line((cx, cy + sy * (sangria + 10), cx, cy + sy * (sangria + 70)), fill=(90, 90, 90), width=3)
                d.line((cx + sx * (sangria + 10), cy, cx + sx * (sangria + 70), cy), fill=(90, 90, 90), width=3)
    return fo


def main():
    os.makedirs(OUT, exist_ok=True)
    folha_dupla(OPCOES["C"]).save(os.path.join(OUT, "cracha_C_Erik_Jessica.pdf"), resolution=DPI)
    w = 420
    h = int(w * CH / CW)
    for arq, ops in (("cracha_opcoes.jpg", OPCOES), ("cracha_opcoes2.jpg", OPCOES2), ("cracha_opcoes3.jpg", OPCOES3)):
        folha_opcoes(arq, ops, w, h)
    print("ok")


def folha_opcoes(arq, ops, w, h):
    sh = Image.new("RGB", (3 * w + 4 * 30, h + 110), (240, 236, 228))
    d = ImageDraw.Draw(sh)
    for k, (letra, f) in enumerate(ops.items()):
        c = f("ERIK").convert("RGB").resize((w, h), Image.LANCZOS)
        sh.paste(c, (30 + k * (w + 30), 90))
        d.text((30 + k * (w + 30) + w / 2, 45), f"OPÇÃO {letra}", font=E.lilita(48), fill=MAR, anchor="mm")
        folha_a4(f).save(os.path.join(OUT, f"cracha_{letra}_A4.pdf"), resolution=DPI)
    sh.save(os.path.join(OUT, arq), quality=90)


if __name__ == "__main__":
    main()
