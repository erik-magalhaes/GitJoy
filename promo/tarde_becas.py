#!/usr/bin/env python3
"""TARDE DE JOGOS NO BECAS CAFÉ (3/nov/2026). O Becas aceitou; a data ainda está sendo discutida (a ideia dele é o
feriado de 20/11, que não atrapalha o sábado do café). 5/nov: FECHADO = sexta, 20/11 (feriado), a partir das 13h,
Rua Sorocaba, 35, Mauá (DATA e ENDERECO abaixo).
Decisões dele: ingresso R$ 30 com R$ 15 de consumação no café, ~30 vagas, inscrição pelo WhatsApp da loja ou na hora,
no café; cupom de 10% no 1º aluguel para quem participar.

Conceito novo: os GUARDA-CHUVINHOS COLORIDOS que ficam pendurados no teto do Becas (o detalhe que ele viu no perfil),
pendurados no alto da arte, nas cores da Sua Vez; fundo creme quente; caixas oficiais do acervo em leque.

    /usr/bin/python3 tarde_becas.py
      → out/becas/post_1080x1350.png, story_1080x1920.png, cupom.png (9 x 5 cm) e cupons_A4.png/.pdf (10 por folha)
"""
import math
import os
import random
import sys

import qrcode
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
import estilo as E  # noqa: E402

OUT = os.path.join(ROOT, "out", "becas")
CX = os.path.join(REPO, "hobby-reels", "assets", "acervo")
MAR, PET, LAR, AMA, BR = E.MARROM, E.PETROLEO, E.LARANJA, E.AMARELO, E.BRANCO
ROSA = (219, 39, 119)
CREME = (255, 247, 233)
WHATS = "(11) 97793-3910"
SITE = "https://suavez.acervodejogos.com.br/"
CUPOM = "BECAS10"  # sugestão: eles precisam criar o cupom no site (10% no 1º aluguel)
JOGOS = ["hitster", "dixit", "telma", "tapalavras", "say_my_name", "uga_buga"]


# ---------------------------------------------------------------- peças
def guarda_chuva(w, cor, seed=0):
    """Guarda-chuvinha aberto visto de lado: copa em meia-lua com bico ondulado, gomos, ponta e cabo em J."""
    h = int(w * 0.95)
    im = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, top = w / 2 + 10, 14
    r = w / 2
    base = top + r * 0.62
    # copa (meia-elipse) + bico de ondinhas
    copa = [(cx + r * math.cos(a), base - r * 0.62 * math.sin(a)) for a in [math.pi * k / 40 for k in range(41)]]
    n = 5
    ondas = []
    for k in range(n):
        x0, x1 = cx + r - 2 * r * k / n, cx + r - 2 * r * (k + 1) / n
        for j in range(1, 11):
            t = j / 10
            ondas.append((x0 + (x1 - x0) * t, base - math.sin(math.pi * t) * r * 0.16))
    poly = copa + ondas
    sombra = [(x + 5, y + 6) for x, y in poly]
    d.polygon(sombra, fill=MAR)
    d.polygon(poly, fill=cor, outline=MAR)
    clara = tuple(min(255, int(c + (255 - c) * 0.35)) for c in cor)
    for k in range(1, n):  # gomos alternando tom
        x = cx + r - 2 * r * k / n
        d.line([(cx, top + 2), (x, base - 2)], fill=MAR, width=3)
    for k in range(0, n, 2):
        x0, x1 = cx + r - 2 * r * k / n, cx + r - 2 * r * (k + 1) / n
        d.polygon([(cx, top + 4), (x0 - (3 if k else 6), base - 4), (x1 + 3, base - 4)], fill=clara)
    d.line(poly + [poly[0]], fill=MAR, width=5)
    d.line([(cx, top - 10), (cx, top + 2)], fill=MAR, width=5)  # ponta
    # cabo
    d.line([(cx, base), (cx, base + r * 0.75)], fill=MAR, width=6)
    yh = base + r * 0.75
    d.arc((cx - r * 0.22, yh - r * 0.11, cx, yh + r * 0.13), 0, 180, fill=MAR, width=6)
    return im


def guarda_chuvas(img, alturas, larg, seed=3):
    """Fileira de guarda-chuvinhas pendurados por fios desde o topo."""
    W = img.width
    rnd = random.Random(seed)
    cores = [LAR, PET, AMA, ROSA, (118, 176, 65), LAR, PET, AMA]
    d = ImageDraw.Draw(img)
    n = len(alturas)
    for k, y in enumerate(alturas):
        x = (k + 0.5) * W / n + rnd.uniform(-18, 18)
        w = int(larg * rnd.uniform(0.85, 1.1))
        d.line([(x, 0), (x, y)], fill=(150, 120, 100), width=3)
        g = guarda_chuva(w, cores[k % len(cores)], k).rotate(rnd.uniform(-9, 9), expand=True,
                                                               resample=Image.BICUBIC)
        img.alpha_composite(g, (int(x - g.width / 2), int(y - 6)))


def fundo(W, H, alturas, larg):
    img = Image.new("RGBA", (W, H), CREME + (255,))
    d = ImageDraw.Draw(img)
    rnd = random.Random(7)
    for _ in range(160):  # pontinhos de confete bem claros
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(3, 6)
        c = (LAR, PET, AMA, ROSA)[rnd.randrange(4)]
        c = tuple(int(v + (255 - v) * 0.7) for v in c)
        d.ellipse((x - r, y - r, x + r, y + r), fill=c)
    guarda_chuvas(img, alturas, larg)
    return img


def caixa(nome, h):
    im = Image.open(os.path.join(CX, nome + ".png")).convert("RGBA")
    im = im.crop(im.getbbox())
    im = im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
    sh = Image.new("RGBA", (im.width + 24, im.height + 24), (0, 0, 0, 0))
    sh.paste(MAR + (130,), (12, 16), im.getchannel("A"))
    sh = sh.filter(ImageFilter.GaussianBlur(5))
    sh.alpha_composite(im, (2, 2))
    return sh


def leque(img, cx, cy, h, passo):
    n = len(JOGOS)
    for k, nome in enumerate(JOGOS):
        a = (k - (n - 1) / 2)
        E.cola(img, caixa(nome, h), cx + a * passo, cy + abs(a) * h * 0.06, -a * 4.5)


DATA = "SEXTA, 20/11 (FERIADO) · 13H ÀS 19H"  # 5/nov: o Becas aceitou o feriado de 20/11, das 13h às 19h
ENDERECO = "BECAS CAFÉ · RUA SOROCABA, 35 · MAUÁ"  # Restaurant Guru: R. Sorocaba, 35, Mauá, 09370-150


def selo_data(s):
    return E.pilula(DATA, s, AMA, MAR, fonte_titulo=True)


def selo_endereco(s):
    return E.pilula(ENDERECO, s, BR, PET, fonte_titulo=True)


def card_info(w):
    c = E.bloco(w, 345, BR, raio=32, ow=7, sombra=12).copy()
    d = ImageDraw.Draw(c)
    d.text((40, 94), "R$ 30", font=E.lilita(96), fill=LAR, anchor="lm", stroke_width=4, stroke_fill=MAR)
    d.text((300, 50), "por pessoa,", font=E.fig(36, 800), fill=MAR, anchor="lm")
    d.text((300, 94), "e R$ 15 viram consumação", font=E.fig(36, 800), fill=PET, anchor="lm")
    d.text((300, 136), "no café ☕".replace(" ☕", ""), font=E.fig(36, 800), fill=PET, anchor="lm")
    d.line((40, 180, w - 40, 180), fill=(225, 210, 190), width=3)
    for k, t in enumerate(["A gente ensina todos os jogos, mesa por mesa",
                           "Jogos rápidos e divertidos, pra quem nunca jogou",
                           "Venha sozinho, em dupla ou com a galera"]):
        y = 222 + k * 46
        d.ellipse((40, y - 11, 62, y + 11), fill=(LAR, PET, ROSA)[k], outline=MAR, width=3)
        d.text((80, y), t, font=E.fig(33, 700), fill=MAR, anchor="lm")
    return c


def inscricao(w):
    """Reserva pelo WhatsApp em destaque, mas deixando claro que no dia também dá pra chegar (pedido dele: sem nº de vagas)."""
    c = E.bloco(w, 232, PET, raio=36, ow=7, sombra=11).copy()
    d = ImageDraw.Draw(c)
    d.text((w / 2, 48), "GARANTA SUA MESA PELO WHATSAPP", font=E.lilita(44), fill=BR, anchor="mm")
    d.text((w / 2, 100), WHATS, font=E.lilita(46), fill=AMA, anchor="mm")
    d.line((60, 136, w - 60, 136), fill=(90, 160, 180), width=2)
    d.text((w / 2, 163), "Não reservou? Passa lá no dia:", font=E.fig(31, 700), fill=BR, anchor="mm")
    d.text((w / 2, 200), "se tiver mesa livre, é só chegar e jogar!", font=E.fig(31, 800), fill=BR, anchor="mm")
    return c


# ---------------------------------------------------------------- telas
def post():
    W, H = 1080, 1350
    img = fundo(W, H, [60, 120, 40, 105, 50, 115], 140)
    E.cola(img, E.pilula("SUA VEZ  ×  BECAS CAFÉ", 32, BR, MAR, fonte_titulo=True), W / 2, 300, -1.5)
    E.cola(img, E.titulo("TARDE DE JOGOS", 118, LAR), W / 2, 410, -2)
    E.cola(img, selo_data(34), W / 2, 505, 1.5)
    E.cola(img, selo_endereco(26), W / 2, 572, -1)
    leque(img, W / 2, 680, 170, 140)
    E.cola(img, card_info(900), W / 2, 930, 0)
    E.cola(img, inscricao(900), W / 2, 1228, 0)
    return img


def story():
    W, H = 1080, 1920
    img = fundo(W, H, [120, 210, 90, 190, 100, 200], 160)
    E.cola(img, E.pilula("SUA VEZ  ×  BECAS CAFÉ", 38, BR, MAR, fonte_titulo=True), W / 2, 470, -1.5)
    E.cola(img, E.titulo("TARDE\nDE JOGOS", 170, LAR), W / 2, 680, -2)
    E.cola(img, selo_data(42), W / 2, 845, 1.5)
    E.cola(img, selo_endereco(32), W / 2, 925, -1)
    leque(img, W / 2, 1085, 220, 155)
    E.cola(img, card_info(920), W / 2, 1378, 0)
    E.cola(img, inscricao(920), W / 2, 1672, 0)
    lg = E.logo(165)
    img.alpha_composite(lg, (int(W / 2 - lg.width / 2), 1798))
    return img


def flyer():
    """Flyer A5 (14,8 x 21 cm) para imprimir/deixar no balcão: o post em cima + faixa com QR do site."""
    W, H = 1080, 1528  # proporção A5
    img = fundo(W, H, [60, 120, 40, 105, 50, 115], 140)
    p = post()
    img.alpha_composite(p.crop((0, 230, 1080, 1350)), (0, 230))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((70, 1368, W - 70, 1508), 28, fill=BR, outline=MAR, width=6)
    q = qr(118)
    img.paste(q, (96, 1379))
    d.text((240, 1408), "Conheça o nosso acervo:", font=E.fig(32, 800), fill=MAR, anchor="lm")
    d.text((240, 1458), "suavez.acervodejogos.com.br · @suavez_bg", font=E.fig(30, 700), fill=PET, anchor="lm")
    return img


# ---------------------------------------------------------------- cupom (impresso)
DPI = 300
CW, CH = int(9 / 2.54 * DPI), int(5 / 2.54 * DPI)  # 9 x 5 cm


def qr(tam):
    q = qrcode.QRCode(border=0, box_size=10, error_correction=qrcode.constants.ERROR_CORRECT_M)
    q.add_data(SITE)
    q.make(fit=True)
    return q.make_image(fill_color=MAR, back_color=BR).convert("RGB").resize((tam, tam), Image.NEAREST)


def tracejado(d, box, cor, w=4, passo=22, traco=12):
    x0, y0, x1, y1 = box
    for x in range(x0, x1, passo):
        d.line((x, y0, min(x + traco, x1), y0), fill=cor, width=w)
        d.line((x, y1, min(x + traco, x1), y1), fill=cor, width=w)
    for y in range(y0, y1, passo):
        d.line((x0, y, x0, min(y + traco, y1)), fill=cor, width=w)
        d.line((x1, y, x1, min(y + traco, y1)), fill=cor, width=w)


def cupom():
    """Cartãozinho 9 x 5 cm entregue a quem pagou: vale R$ 15 de consumação + cupom do 1º aluguel + QR do site."""
    img = Image.new("RGBA", (CW, CH), BR + (255,))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 22, CH), fill=LAR)  # faixa colorida na esquerda
    d.rectangle((22, 0, 34, CH), fill=AMA)
    # cabeçalho
    lg = E.logo(96)
    img.alpha_composite(lg, (58, 22))
    d.text((58 + lg.width + 16, 46), "TARDE DE JOGOS NO BECAS CAFÉ", font=E.lilita(34), fill=MAR, anchor="lm")
    d.text((58 + lg.width + 16, 92), "sexta, 20/11 · 13h às 19h", font=E.fig(26, 700), fill=PET, anchor="lm")
    # vale de consumação
    vx0, vy0, vx1, vy1 = 58, 150, 690, 370
    d.rounded_rectangle((vx0 + 7, vy0 + 7, vx1 + 7, vy1 + 7), 22, fill=MAR)
    d.rounded_rectangle((vx0, vy0, vx1, vy1), 22, fill=AMA, outline=MAR, width=5)
    d.text((vx0 + 30, vy0 + 42), "VALE CONSUMAÇÃO", font=E.fig(30, 900), fill=MAR, anchor="lm")
    d.text((vx0 + 26, vy0 + 128), "R$ 15", font=E.lilita(118), fill=LAR, anchor="lm", stroke_width=5, stroke_fill=MAR)
    d.text((vx0 + 360, vy0 + 112), "no Becas Café", font=E.fig(30, 800), fill=MAR, anchor="lm")
    d.text((vx0 + 360, vy0 + 152), "em 20/11", font=E.fig(30, 800), fill=MAR, anchor="lm")
    d.text((vx0 + 30, vy0 + 196), "entregue no caixa ao fazer o pedido", font=E.fig(23, 700), fill=MAR, anchor="lm")
    # cupom do 1º aluguel
    tracejado(d, (58, 400, 690, 520), PET)
    d.text((82, 436), "10% OFF no seu 1º aluguel", font=E.fig(30, 900), fill=MAR, anchor="lm")
    d.text((82, 486), "CUPOM:", font=E.fig(30, 800), fill=MAR, anchor="lm")
    d.text((212, 488), CUPOM, font=E.lilita(50), fill=PET, anchor="lm")
    d.text((374, 562), "Valeu por jogar com a gente!", font=E.fig(24, 700), fill=MAR, anchor="mm")
    # QR do site
    q = qr(290)
    qx = CW - 335
    img.paste(q, (qx, 150))
    d.text((qx + 145, 470), "conheça o acervo", font=E.fig(26, 800), fill=MAR, anchor="mm")
    d.text((qx + 145, 508), "e alugue no site", font=E.fig(26, 800), fill=MAR, anchor="mm")
    d.text((qx + 145, 552), "@suavez_bg", font=E.fig(26, 900), fill=PET, anchor="mm")
    return img


def folha_cupons():
    A4 = (int(21 / 2.54 * DPI), int(29.7 / 2.54 * DPI))
    folha = Image.new("RGB", A4, (255, 255, 255))
    d = ImageDraw.Draw(folha)
    c = cupom().convert("RGB")
    cols, lins = 2, 5
    mx, my = (A4[0] - cols * CW) // 2, (A4[1] - lins * CH) // 2
    for i in range(lins):
        for j in range(cols):
            folha.paste(c, (mx + j * CW, my + i * CH))
    # marcas de corte
    for j in range(cols + 1):
        x = mx + j * CW
        d.line((x, my - 60, x, my - 15), fill=(120, 120, 120), width=3)
        d.line((x, my + lins * CH + 15, x, my + lins * CH + 60), fill=(120, 120, 120), width=3)
    for i in range(lins + 1):
        y = my + i * CH
        d.line((mx - 60, y, mx - 15, y), fill=(120, 120, 120), width=3)
        d.line((mx + cols * CW + 15, y, mx + cols * CW + 60, y), fill=(120, 120, 120), width=3)
    return folha


def main():
    os.makedirs(OUT, exist_ok=True)
    p, s = post(), story()
    p.convert("RGB").save(os.path.join(OUT, "post_1080x1350.png"))
    s.convert("RGB").save(os.path.join(OUT, "story_1080x1920.png"))
    cupom().convert("RGB").save(os.path.join(OUT, "cupom.png"), dpi=(DPI, DPI))
    fl = flyer().convert("RGB").resize((1748, 2480), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.2, 60, 2))
    fl.save(os.path.join(OUT, "flyer_A5.png"), dpi=(DPI, DPI))
    fl.save(os.path.join(OUT, "flyer_A5.pdf"), resolution=DPI)
    f = folha_cupons()
    f.save(os.path.join(OUT, "cupons_A4.png"), dpi=(DPI, DPI))
    f.save(os.path.join(OUT, "cupons_A4.pdf"), resolution=DPI)
    sh = Image.new("RGB", (540 + 20 + 540, 960), (255, 255, 255))
    sh.paste(p.convert("RGB").resize((540, 675)), (0, 0))
    sh.paste(s.convert("RGB").resize((540, 960)), (560, 0))
    sh.paste(cupom().convert("RGB").resize((531, 295)), (5, 680))
    sh.save(os.path.join(OUT, "folha.jpg"), quality=90)
    print("ok")


if __name__ == "__main__":
    main()
