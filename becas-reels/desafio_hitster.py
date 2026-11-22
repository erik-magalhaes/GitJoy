#!/usr/bin/env python3
"""DESAFIO HITSTER ENTRE MESAS no Domingo de Jogos (22/nov/2026, ele adorou a ideia). Às 16h todo mundo para por ~20 min,
cada MESA vira um time: o Erik toca uma música do Hitster pelo app (sem mostrar a carta), cada mesa escreve O ANO e
levanta a folha; ano certo = 3 pontos, até 2 anos de diferença = 2, década certa = 1; 10 músicas; a mesa campeã ganha um
VOUCHER do Beca’s pra próxima visita (valor a combinar com o café: o voucher sai com o valor em branco).

Peças (out/desafio/):
- post.png / story.png: anúncio no visual de fim de ano do domingo (caixa oficial do Hitster).
- placar_A3.pdf e placar_A4.pdf: placar de parede, mesas 1–8 × músicas 1–10 + total.
- palpites_mesas_1-8.pdf: uma folha por mesa com 10 quadrões numerados (escreve o ano com canetão e levanta a folha).
- vouchers_A4.pdf: 10 vouchers 9 x 5 cm por folha, numerados 01–10 (valor e validade em branco).
- roteiro_apresentador.pdf: o passo a passo do Erik, pontuação e desempate.

    /usr/bin/python3 desafio_hitster.py
"""
import os

from PIL import Image, ImageDraw

import domingo as D
from tarde import E, TB, W, H, MAR, PET, LAR, AMA, BR

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
PASTA = os.path.join(D.OUT, "desafio")
DPI = 300
A4 = (2480, 3508)
A3P = (4961, 3508)  # A3 deitado
CAIXA = os.path.join(REPO, "hobby-reels", "assets", "acervo", "hitster.png")
VERM = D.VERM
HORA_DESAFIO = "16H"
MESAS = 8
MUSICAS = 10
CINZA = (120, 120, 120)


def caixa(h):
    im = Image.open(CAIXA).convert("RGBA")
    im = im.crop(im.getbbox())
    return im.resize((int(im.width * h / im.height), h), Image.LANCZOS)


def nota(s, cor):
    """Notinha musical desenhada (as fontes não têm ♪)."""
    im = Image.new("RGBA", (int(s * 0.9), s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = s * 0.2
    for cx in (s * 0.2, s * 0.62):
        d.ellipse((cx - r, s - 2.1 * r, cx + r, s - 0.1 * r), fill=cor, outline=MAR, width=3)
        d.rectangle((cx + r - 7, s * 0.12, cx + r, s - r), fill=MAR)
    d.polygon([(s * 0.2 + r - 7, s * 0.12), (s * 0.62 + r, 0), (s * 0.62 + r, s * 0.14), (s * 0.2 + r - 7, s * 0.26)],
              fill=MAR)
    return im


def pontos(w):
    """Quadrinho com a pontuação."""
    c = E.bloco(w, 250, BR, raio=30, ow=6, sombra=10).copy()
    d = ImageDraw.Draw(c)
    for k, (p, txt) in enumerate((("3", "ANO CERTINHO"), ("2", "ATÉ 2 ANOS DE DIFERENÇA"), ("1", "DÉCADA CERTA"))):
        y = 52 + k * 72
        d.ellipse((40, y - 28, 96, y + 28), fill=(LAR, PET, AMA)[k], outline=MAR, width=4)
        d.text((68, y + 1), p, font=E.lilita(38), fill=BR if k < 2 else MAR, anchor="mm")
        d.text((120, y), f"PONTO{'S' if p != '1' else ''}: {txt}", font=E.lilita(36), fill=MAR, anchor="lm")
    return c


# ---------------------------------------------------------------- anúncio
def anuncio(h):
    img = D.fundo(3.0).crop((0, 0, W, h))
    oy = 0 if h == 1350 else 120
    E.cola(img, E.titulo("DESAFIO\nHITSTER!", 150, LAR), 540, oy + 400, -2, 1, 1)
    E.cola(img, E.pilula(f"ÀS {HORA_DESAFIO}: TODAS AS MESAS JOGAM JUNTAS", 38, PET, BR, fonte_titulo=True), 540,
           oy + 590, 1, 1, 1)
    E.cola(img, caixa(380), 290, oy + 850, -6, 1, 1)
    for x, y, s, c, r in ((150, oy + 640, 70, VERM, -12), (470, oy + 660, 56, PET, 10), (980, oy + 1000, 64, AMA, 8)):
        E.cola(img, nota(s, c), x, y, r, 1, 1)
    passos = E.bloco(570, 330, BR, raio=30, ow=6, sombra=10).copy()
    d = ImageDraw.Draw(passos)
    for k, txt in enumerate(("a música toca", "cada mesa chuta o ano", "chegou perto? pontua!")):
        y = 62 + k * 100
        d.ellipse((30, y - 30, 90, y + 30), fill=(LAR, PET, AMA)[k], outline=MAR, width=4)
        d.text((60, y + 1), str(k + 1), font=E.lilita(40), fill=BR if k < 2 else MAR, anchor="mm")
        d.text((110, y), txt, font=E.fig(34, 900), fill=MAR, anchor="lm")
    E.cola(img, passos, 745, oy + 830, 2, 1, 1)
    premio = E.bloco(940, 190, AMA, raio=34, ow=7, sombra=12).copy()
    d = ImageDraw.Draw(premio)
    d.text((470, 62), "A MESA CAMPEÃ GANHA", font=E.lilita(50), fill=MAR, anchor="mm")
    d.text((470, 130), "UM VOUCHER DO BECA’S PRA PRÓXIMA VISITA!", font=E.lilita(40), fill=VERM, anchor="mm")
    E.cola(img, premio, 540, oy + 1110, -1, 1, 1)
    if h == 1350:
        E.cola(img, E.pilula(f"DOMINGO DE JOGOS · {D.DATA.split(', ')[-1]} · SÓ 30 VAGAS", 34, VERM, BR,
                             fonte_titulo=True), 540, 1280, 1, 1, 1)
    else:
        E.cola(img, E.pilula(f"DOMINGO DE JOGOS · {D.DATA.split(', ')[-1]} · SÓ 30 VAGAS", 36, VERM, BR,
                             fonte_titulo=True), 540, oy + 1290, 1, 1, 1)
        E.cola(img, E.pilula("garanta a vaga da sua mesa:", 40, BR, MAR), 540, 1590, 0, 1, 1)
        E.cola(img, D.seta(), 540, 1690, 0, 0.5, 1)
    return img.convert("RGB")


# ---------------------------------------------------------------- impressos
def cabecalho(pg, titulo, y=170, s=150, logo=True):
    d = ImageDraw.Draw(pg)
    d.text((pg.width / 2, y), titulo, font=E.lilita(s), fill=LAR, anchor="mm", stroke_width=8, stroke_fill=MAR)
    if logo:
        lg = TB.parceria(150)
        pg.paste(lg, (pg.width - lg.width - 120, y - 75), lg)


def placar(tam):
    pg = Image.new("RGB", tam, BR)
    d = ImageDraw.Draw(pg)
    k = tam[0] / A3P[0]
    cabecalho(pg, "DESAFIO HITSTER · PLACAR", int(190 * k), int(170 * k))
    x0, y0 = int(140 * k), int(400 * k)
    larg_mesa, larg_tot = int(560 * k), int(560 * k)
    col = (tam[0] - 2 * x0 - larg_mesa - larg_tot) / MUSICAS
    lh = (tam[1] - y0 - int(420 * k)) / (MESAS + 1)
    f_cab, f_m = E.lilita(int(70 * k)), E.lilita(int(80 * k))
    for i in range(MESAS + 1):
        y = y0 + i * lh
        if i % 2 == 0 and i > 0:
            d.rectangle((x0, y, tam[0] - x0, y + lh), fill=(246, 240, 228))
        if i == 0:
            d.rectangle((x0, y, tam[0] - x0, y + lh), fill=PET)
    d.text((x0 + larg_mesa / 2, y0 + lh / 2), "MESA", font=f_cab, fill=BR, anchor="mm")
    for j in range(MUSICAS):
        cx = x0 + larg_mesa + (j + 0.5) * col
        d.text((cx, y0 + lh / 2), f"♪{j + 1}" if False else str(j + 1), font=f_cab, fill=BR, anchor="mm")
    d.text((tam[0] - x0 - larg_tot / 2, y0 + lh / 2), "TOTAL", font=f_cab, fill=AMA, anchor="mm")
    for i in range(1, MESAS + 1):
        d.text((x0 + larg_mesa / 2, y0 + (i + 0.5) * lh), str(i), font=f_m, fill=MAR, anchor="mm")
    for i in range(MESAS + 2):
        y = y0 + i * lh
        d.line((x0, y, tam[0] - x0, y), fill=MAR, width=max(3, int(8 * k)))
    xs = [x0, x0 + larg_mesa] + [x0 + larg_mesa + j * col for j in range(1, MUSICAS + 1)] + [tam[0] - x0]
    for x in xs:
        d.line((x, y0, x, y0 + (MESAS + 1) * lh), fill=MAR, width=max(3, int(8 * k)))
    leg = "ANO CERTINHO = 3   ·   ATÉ 2 ANOS = 2   ·   DÉCADA CERTA = 1   ·   A MESA CAMPEÃ GANHA VOUCHER DO BECA’S!"
    d.text((tam[0] / 2, tam[1] - int(200 * k)), leg, font=E.lilita(int(84 * k)), fill=MAR, anchor="mm")
    return pg


def palpites(m):
    pg = Image.new("RGB", A4, BR)
    d = ImageDraw.Draw(pg)
    d.rounded_rectangle((120, 90, A4[0] - 120, 480), 50, fill=LAR, outline=MAR, width=10)
    d.text((A4[0] / 2, 240), f"MESA {m}", font=E.lilita(230), fill=BR, anchor="mm", stroke_width=10, stroke_fill=MAR)
    d.text((A4[0] / 2, 410), "nome do time: ______________________", font=E.fig(64, 800), fill=BR, anchor="mm")
    d.text((A4[0] / 2, 560), "Escrevam o ANO bem grande com canetão e levantem a folha!", font=E.fig(58, 800),
           fill=MAR, anchor="mm")
    bw, bh, gx, gy = 1060, 480, 120, 60
    x0 = (A4[0] - 2 * bw - gx) / 2
    for k in range(MUSICAS):
        c, l = k % 2, k // 2
        x, y = x0 + c * (bw + gx), 660 + l * (bh + gy)
        d.rounded_rectangle((x, y, x + bw, y + bh), 36, outline=MAR, width=8)
        d.rounded_rectangle((x, y, x + 300, y + 110), 36, fill=PET)
        d.rectangle((x + 40, y + 70, x + 300, y + 110), fill=PET)
        d.text((x + 150, y + 58), f"MÚSICA {k + 1}", font=E.lilita(52), fill=BR, anchor="mm")
        d.text((x + bw - 40, y + bh - 40), "ANO", font=E.fig(44, 800), fill=(180, 170, 160), anchor="rs")
    return pg


VW, VH = int(9 / 2.54 * DPI), int(5 / 2.54 * DPI)


def voucher(n):
    img = Image.new("RGBA", (VW, VH), BR + (255,))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, VW, 22), fill=VERM)
    d.rectangle((0, VH - 22, VW, VH), fill=VERM)
    d.rectangle((0, 0, VW - 1, VH - 1), outline=(190, 190, 190), width=2)
    lg = TB.logo_becas(120)
    img.alpha_composite(lg, (40, 70))
    d.text((200 + 40, 92), "VOUCHER", font=E.lilita(84), fill=LAR, anchor="lm", stroke_width=4, stroke_fill=MAR)
    d.text((200 + 44, 168), "MESA CAMPEÃ · DESAFIO HITSTER", font=E.fig(32, 900), fill=MAR, anchor="lm")
    d.text((50, 268), "vale:", font=E.fig(40, 800), fill=MAR, anchor="lm")
    d.line((160, 290, VW - 60, 290), fill=MAR, width=3)
    d.text((50, 360), "na sua próxima visita ao Beca’s Café", font=E.fig(36, 800), fill=MAR, anchor="lm")
    d.text((50, 450), "válido até ____/____", font=E.fig(34, 700), fill=MAR, anchor="lm")
    d.rounded_rectangle((VW - 230, 410, VW - 40, 490), 16, fill=AMA, outline=MAR, width=4)
    d.text((VW - 135, 450), f"Nº {n:02d}", font=E.lilita(42), fill=MAR, anchor="mm")
    sv = E.logo(150)
    img.alpha_composite(sv, (VW - sv.width - 40, 60))
    return img


def roteiro():
    pg = Image.new("RGB", A4, BR)
    d = ImageDraw.Draw(pg)
    cabecalho(pg, "DESAFIO HITSTER", 190, 150, logo=False)
    d.text((A4[0] / 2, 330), f"roteiro do apresentador · domingo de jogos · às {HORA_DESAFIO.lower()}",
           font=E.fig(60, 800), fill=PET, anchor="mm")
    linhas = [
        ("ANTES", ["Separe 10 cartas do Hitster (misture épocas; músicas bem conhecidas).",
                   "Caixinha de som + celular com o app do Hitster.",
                   "Entregue a folha de palpites e um canetão por mesa; placar na parede."]),
        ("ABERTURA (2 MIN)", ["\"Pausa nos jogos! Agora cada mesa é um time.\"",
                              "Explique: toca a música, a mesa combina o ano, escreve no quadro da música e levanta.",
                              "Conte o prêmio: a mesa campeã ganha voucher do Beca’s pra próxima visita."]),
        ("CADA RODADA (~2 MIN)", ["Toque ~30 s da música, sem mostrar a carta.",
                                  "Conte 3-2-1: todas as mesas levantam a folha AO MESMO TEMPO.",
                                  "Revele o ano da carta e marque os pontos no placar:",
                                  "ano certinho = 3 · até 2 anos de diferença = 2 · década certa = 1."]),
        ("DESEMPATE", ["Uma música extra: ganha a mesa que chegar MAIS PERTO do ano."]),
        ("FINAL", ["Anuncie a campeã, entregue 1 voucher por pessoa da mesa e tire a foto da mesa!",
                   "Filme 1 rodada (o 3-2-1 + a revelação): é o melhor vídeo pro Instagram."]),
    ]
    y = 470
    for tit, itens in linhas:
        d.rounded_rectangle((140, y, 1100, y + 100), 30, fill=LAR)
        d.text((180, y + 50), tit, font=E.lilita(62), fill=BR, anchor="lm")
        y += 140
        for it in itens:
            d.text((200, y), "•  " + it, font=E.fig(52, 700), fill=MAR, anchor="lm")
            y += 82
        y += 40
    d.text((A4[0] / 2, A4[1] - 140), "Duração total: uns 20 minutos. Depois todo mundo volta pros jogos!",
           font=E.fig(54, 800), fill=PET, anchor="mm")
    return pg


def salva_pdf(pags, nome):
    pags[0].save(os.path.join(PASTA, nome), save_all=True, append_images=pags[1:], resolution=DPI)


def main():
    os.makedirs(PASTA, exist_ok=True)
    anuncio(1350).save(os.path.join(PASTA, "post.png"))
    anuncio(1920).save(os.path.join(PASTA, "story.png"))
    salva_pdf([placar(A3P)], "placar_A3.pdf")
    salva_pdf([placar((3508, 2480))], "placar_A4.pdf")
    salva_pdf([palpites(m) for m in range(1, MESAS + 1)], "palpites_mesas_1-8.pdf")
    salva_pdf([TB.folha([voucher(n) for n in range(1, 11)], 2, 5)], "vouchers_A4.pdf")
    salva_pdf([roteiro()], "roteiro_apresentador.pdf")
    # prévias em JPG pro chat
    placar((3508, 2480)).resize((1400, 990)).save(os.path.join(PASTA, "previa_placar.jpg"), quality=88)
    palpites(1).resize((827, 1170)).save(os.path.join(PASTA, "previa_palpites.jpg"), quality=88)
    voucher(1).convert("RGB").save(os.path.join(PASTA, "previa_voucher.jpg"), quality=92)
    roteiro().resize((827, 1170)).save(os.path.join(PASTA, "previa_roteiro.jpg"), quality=88)
    print("ok", PASTA)


if __name__ == "__main__":
    main()
