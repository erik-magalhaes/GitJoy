#!/usr/bin/env python3
"""TARDE DE JOGOS NO BECAS CAFÉ (3/nov/2026). O Becas aceitou; a data ainda está sendo discutida (a ideia dele é o
feriado de 20/11, que não atrapalha o sábado do café), então as artes saem SEM data ("DATA EM BREVE").
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


def selo_data(s):
    return E.pilula("DATA EM BREVE", s, AMA, MAR, fonte_titulo=True)


def card_info(w):
    c = E.bloco(w, 330, BR, raio=32, ow=7, sombra=12).copy()
    d = ImageDraw.Draw(c)
    d.text((40, 52), "R$ 30", font=E.lilita(96), fill=LAR, anchor="lm", stroke_width=4, stroke_fill=MAR)
    d.text((300, 36), "por pessoa,", font=E.fig(36, 800), fill=MAR, anchor="lm")
    d.text((300, 80), "e R$ 15 viram consumação", font=E.fig(36, 800), fill=PET, anchor="lm")
    d.text((300, 120), "no café ☕".replace(" ☕", ""), font=E.fig(36, 800), fill=PET, anchor="lm")
    d.line((40, 160, w - 40, 160), fill=(225, 210, 190), width=3)
    for k, t in enumerate(["A gente ensina todos os jogos, mesa por mesa",
                           "Jogos rápidos e divertidos, pra quem nunca jogou",
                           "Venha sozinho, em dupla ou com a galera"]):
        y = 200 + k * 46
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
    E.cola(img, selo_data(36), 820, 500, 6)
    leque(img, W / 2, 640, 190, 145)
    E.cola(img, card_info(900), W / 2, 935, 0)
    E.cola(img, inscricao(900), W / 2, 1226, 0)
    return img


def story():
    W, H = 1080, 1920
    img = fundo(W, H, [120, 210, 90, 190, 100, 200], 160)
    E.cola(img, E.pilula("SUA VEZ  ×  BECAS CAFÉ", 38, BR, MAR, fonte_titulo=True), W / 2, 470, -1.5)
    E.cola(img, E.titulo("TARDE\nDE JOGOS", 170, LAR), W / 2, 680, -2)
    E.cola(img, selo_data(44), 850, 835, 6)
    leque(img, W / 2, 1040, 240, 160)
    E.cola(img, card_info(920), W / 2, 1390, 0)
    E.cola(img, inscricao(920), W / 2, 1680, 0)
    lg = E.logo(200)
    img.alpha_composite(lg, (int(W / 2 - lg.width / 2), 1808))
    return img


# ---------------------------------------------------------------- cupom (impresso)
DPI = 300
CW, CH = int(9 / 2.54 * DPI), int(5 / 2.54 * DPI)  # 9 x 5 cm


def qr(tam):
    q = qrcode.QRCode(border=0, box_size=10, error_correction=qrcode.constants.ERROR_CORRECT_M)
    q.add_data(SITE)
    q.make(fit=True)
    return q.make_image(fill_color=MAR, back_color=BR).convert("RGB").resize((tam, tam), Image.NEAREST)


def cupom():
    img = Image.new("RGBA", (CW, CH), BR + (255,))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 26, CH), fill=LAR)  # faixa colorida na esquerda
    d.rectangle((26, 0, 40, CH), fill=AMA)
    lg = E.logo(250)
    img.alpha_composite(lg, (70, 34))
    d.text((70, 250), "10% OFF", font=E.lilita(120), fill=LAR, anchor="lm", stroke_width=4, stroke_fill=MAR)
    d.text((72, 335), "no seu 1º aluguel", font=E.fig(40, 800), fill=MAR, anchor="lm")
    # código num retângulo tracejado
    x0, y0, x1, y1 = 70, 380, 600, 470
    for x in range(x0, x1, 22):
        d.line((x, y0, min(x + 12, x1), y0), fill=MAR, width=4)
        d.line((x, y1, min(x + 12, x1), y1), fill=MAR, width=4)
    for y in range(y0, y1, 22):
        d.line((x0, y, x0, min(y + 12, y1)), fill=MAR, width=4)
        d.line((x1, y, x1, min(y + 12, y1)), fill=MAR, width=4)
    d.text(((x0 + x1) / 2, (y0 + y1) / 2), f"CUPOM: {CUPOM}", font=E.lilita(54), fill=PET, anchor="mm")
    d.text((72, 520), "Valeu por jogar com a gente no Becas!", font=E.fig(28, 700), fill=MAR, anchor="lm")
    q = qr(300)
    img.paste(q, (CW - 340, 130))
    d.text((CW - 190, 470), "reserve no site", font=E.fig(28, 800), fill=MAR, anchor="mm")
    d.text((CW - 190, 510), "@suavez_bg", font=E.fig(28, 800), fill=PET, anchor="mm")
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
