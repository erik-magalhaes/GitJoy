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
        E.cola(img, E.titulo(n, 140, PET, larg_max=CW - 260), CW / 2, 1020, 0)
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


OPCOES = {"A": cracha_a, "B": cracha_b, "C": cracha_c}


def folha_a4(f):
    A4 = (int(21 / 2.54 * DPI), int(29.7 / 2.54 * DPI))
    fo = Image.new("RGB", A4, (255, 255, 255))
    d = ImageDraw.Draw(fo)
    mx, my = (A4[0] - 2 * CW) // 2, (A4[1] - 2 * CH) // 2
    for k, n in enumerate(NOMES):
        fo.paste(f(n).convert("RGB"), (mx + (k % 2) * CW, my + (k // 2) * CH))
    for j in range(3):  # marcas de corte
        x = mx + j * CW
        d.line((x, my - 50, x, my - 12), fill=(120, 120, 120), width=3)
        d.line((x, my + 2 * CH + 12, x, my + 2 * CH + 50), fill=(120, 120, 120), width=3)
        y = my + j * CH
        d.line((mx - 50, y, mx - 12, y), fill=(120, 120, 120), width=3)
        d.line((mx + 2 * CW + 12, y, mx + 2 * CW + 50, y), fill=(120, 120, 120), width=3)
    return fo


def main():
    os.makedirs(OUT, exist_ok=True)
    w = 420
    h = int(w * CH / CW)
    sh = Image.new("RGB", (3 * w + 4 * 30, h + 110), (240, 236, 228))
    d = ImageDraw.Draw(sh)
    for k, (letra, f) in enumerate(OPCOES.items()):
        c = f("ERIK").convert("RGB").resize((w, h), Image.LANCZOS)
        sh.paste(c, (30 + k * (w + 30), 90))
        d.text((30 + k * (w + 30) + w / 2, 45), f"OPÇÃO {letra}", font=E.lilita(48), fill=MAR, anchor="mm")
        folha_a4(f).save(os.path.join(OUT, f"cracha_{letra}_A4.pdf"), resolution=DPI)
    sh.save(os.path.join(OUT, "cracha_opcoes.jpg"), quality=90)
    print("ok")


if __name__ == "__main__":
    main()
