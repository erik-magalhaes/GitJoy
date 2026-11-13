#!/usr/bin/env python3
"""FLYER PRETO E BRANCO da Tarde de Jogos no Beca’s (13/nov/2026, pedido dele: "versão P&B que não fique feia, colorido
sai mais caro"). Não é o colorido convertido pra cinza (o fundo creme, as fotos das caixas e os confetes virariam um
cinza sujo): é um desenho próprio pra P&B, fundo branco (gasta pouca tinta), guarda-chuvinhas em traço com gomos
hachurados, título vazado com contorno e sombra preta, pílulas pretas/contornadas e QR do site.

    /usr/bin/python3 flyer_pb.py   → out/becas/flyer_pb_A5.png/.pdf e out/becas/imprimir/04b_flyer_PB_2_por_A4.pdf
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageOps

import tarde_becas as TB
from tarde_becas import E

OUT = TB.OUT
DPI = 300
W, H = 1748, 2480  # A5 a 300 dpi
K = (0, 0, 0)
BR = (255, 255, 255)
CINZA = (150, 150, 150)


def guarda_chuva_pb(w, seed=0):
    """Guarda-chuvinha em traço: copa branca com contorno preto, gomos alternados com hachura diagonal."""
    rnd = random.Random(seed)
    h = int(w * 1.05)
    im = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, top, r = w / 2 + 10, 16, w / 2
    base = top + r * 0.62
    copa = [(cx + r * math.cos(a), base - r * 0.62 * math.sin(a)) for a in [math.pi * k / 40 for k in range(41)]]
    n = 5
    ondas = []
    for k in range(n):
        x0, x1 = cx + r - 2 * r * k / n, cx + r - 2 * r * (k + 1) / n
        for j in range(1, 11):
            t = j / 10
            ondas.append((x0 + (x1 - x0) * t, base - math.sin(math.pi * t) * r * 0.16))
    poly = copa + ondas
    d.polygon(poly, fill=BR)
    # hachura nos gomos pares (máscara do gomo)
    hach = Image.new("L", im.size, 0)
    dh = ImageDraw.Draw(hach)
    for k in range(0, n, 2):
        x0, x1 = cx + r - 2 * r * k / n, cx + r - 2 * r * (k + 1) / n
        dh.polygon([(cx, top + 2), (x0, base), (x1, base)], fill=255)
    lin = Image.new("L", im.size, 0)
    dl = ImageDraw.Draw(lin)
    passo = 11 + rnd.randint(0, 3)
    for x in range(-im.height, im.width, passo):
        dl.line((x, im.height, x + im.height, 0), fill=255, width=3)
    copa_m = Image.new("L", im.size, 0)
    ImageDraw.Draw(copa_m).polygon(poly, fill=255)
    from PIL import ImageChops
    m = ImageChops.multiply(ImageChops.multiply(hach, lin), copa_m)
    im.paste(K + (255,), (0, 0), m)
    for k in range(1, n):
        x = cx + r - 2 * r * k / n
        d.line([(cx, top + 2), (x, base - 2)], fill=K, width=4)
    d.line(poly + [poly[0]], fill=K, width=6, joint="curve")
    d.line([(cx, top - 12), (cx, top + 2)], fill=K, width=6)
    d.line([(cx, base), (cx, base + r * 0.8)], fill=K, width=6)
    yh = base + r * 0.8
    d.arc((cx - r * 0.24, yh - r * 0.12, cx, yh + r * 0.14), 0, 180, fill=K, width=6)
    return im


def titulo(txt, s):
    """Letras brancas com contorno preto grosso e sombra preta deslocada (tipo carimbo), gasta pouca tinta."""
    f = E.lilita(s)
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    l, t, r_, b = d0.textbbox((0, 0), txt, font=f, stroke_width=10)
    im = Image.new("RGBA", (r_ - l + 40, b - t + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    o = (10 - l, 10 - t)
    d.text((o[0] + 14, o[1] + 14), txt, font=f, fill=K, stroke_width=10, stroke_fill=K)
    d.text(o, txt, font=f, fill=BR, stroke_width=10, stroke_fill=K)
    return im


def pilula(txt, s, cheia=True):
    f = E.lilita(s) if cheia else E.fig(s, 800)
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    tw = d0.textlength(txt, font=f)
    w, h = int(tw + s * 1.4), int(s * 1.7)
    im = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((4, 4, w + 4, h + 4), h // 2, fill=K if cheia else BR, outline=K, width=5)
    d.text((w / 2 + 4, h / 2 + 4), txt, font=f, fill=BR if cheia else K, anchor="mm")
    return im


def cola(img, im, cx, cy):
    img.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def logos_pb(h):
    """Sua Vez × Beca’s em tons de cinza (os logos são fotos coloridas: em P&B ficam em cinza, sem perder a forma)."""
    p = TB.parceria(h)
    a = p.getchannel("A")
    g = ImageOps.grayscale(p.convert("RGB"))
    g = ImageOps.autocontrast(g, cutoff=1)
    out = Image.merge("RGBA", (g, g, g, a))
    return out


def flyer_pb():
    img = Image.new("RGBA", (W, H), BR + (255,))
    d = ImageDraw.Draw(img)
    rnd = random.Random(5)
    # fileira de guarda-chuvinhas pendurados
    for k, y in enumerate([110, 200, 80, 175, 95, 190]):
        x = (k + 0.5) * W / 6 + rnd.uniform(-20, 20)
        d.line([(x, 0), (x, y)], fill=CINZA, width=4)
        g = guarda_chuva_pb(int(215 * rnd.uniform(0.9, 1.08)), k).rotate(rnd.uniform(-9, 9), expand=True,
                                                                           resample=Image.BICUBIC)
        img.alpha_composite(g, (int(x - g.width / 2), int(y - 8)))
    cola(img, logos_pb(165), W / 2, 560)
    cola(img, titulo("TARDE", 260), W / 2, 790)
    cola(img, titulo("DE JOGOS", 260), W / 2, 1035)
    cola(img, pilula("SEXTA, 20/11 (FERIADO) · 13H ÀS 19H", 58), W / 2, 1250)
    cola(img, pilula("BECA’S CAFÉ · RUA SOROCABA, 35 · MAUÁ", 46, cheia=False), W / 2, 1355)
    # preço + o que é
    y0 = 1450
    d.rounded_rectangle((120, y0, W - 120, y0 + 520), 40, outline=K, width=7)
    d.text((190, y0 + 125), "R$ 30", font=E.lilita(170), fill=K, anchor="lm")
    d.text((680, y0 + 85), "por pessoa,", font=E.fig(56, 800), fill=K, anchor="lm")
    d.text((680, y0 + 160), "e R$ 15 viram consumação", font=E.fig(52, 800), fill=K, anchor="lm")
    d.text((680, y0 + 225), "no café", font=E.fig(52, 800), fill=K, anchor="lm")
    d.line((190, y0 + 290, W - 190, y0 + 290), fill=CINZA, width=3)
    for k, t in enumerate(["A gente ensina todos os jogos, mesa por mesa",
                           "Jogos rápidos e divertidos, pra quem nunca jogou",
                           "Venha sozinho, em dupla ou com a galera"]):
        y = y0 + 350 + k * 62
        d.ellipse((190, y - 15, 220, y + 15), outline=K, width=5)
        d.text((250, y), t, font=E.fig(46, 700), fill=K, anchor="lm")
    # reserva: faixa preta
    y1 = 2010
    d.rounded_rectangle((120, y1, W - 120, y1 + 250), 40, fill=K)
    d.text((W / 2, y1 + 62), "GARANTA SUA MESA PELO WHATSAPP", font=E.lilita(66), fill=BR, anchor="mm")
    d.text((W / 2, y1 + 140), TB.WHATS, font=E.lilita(78), fill=BR, anchor="mm")
    d.text((W / 2, y1 + 212), "Não reservou? Se tiver mesa livre, é só chegar e jogar!", font=E.fig(40, 700),
           fill=BR, anchor="mm")
    # QR do site
    q = TB.qr(190).convert("L").point(lambda v: 0 if v < 128 else 255).convert("RGB")
    img.paste(q, (140, 2280))
    d.text((370, 2335), "Conheça o nosso acervo:", font=E.fig(48, 800), fill=K, anchor="lm")
    d.text((370, 2410), "suavez.acervodejogos.com.br · @suavez_bg", font=E.fig(44, 700), fill=K, anchor="lm")
    return img.convert("L").convert("RGB")


def main():
    f = flyer_pb()
    f.save(os.path.join(OUT, "flyer_pb_A5.png"))
    f.save(os.path.join(OUT, "flyer_pb_A5.pdf"), resolution=DPI)
    A4 = (2480, 3508)
    a4 = Image.new("RGB", A4, BR)
    f2 = f.rotate(90, expand=True).resize((A4[0], A4[1] // 2), Image.LANCZOS)
    a4.paste(f2, (0, 0))
    a4.paste(f2, (0, A4[1] // 2))
    ImageDraw.Draw(a4).line((0, A4[1] // 2, A4[0], A4[1] // 2), fill=(170, 170, 170), width=3)
    os.makedirs(os.path.join(OUT, "imprimir"), exist_ok=True)
    a4.save(os.path.join(OUT, "imprimir", "04b_flyer_PB_2_por_A4.pdf"), resolution=DPI)
    print("ok")


if __name__ == "__main__":
    main()
