#!/usr/bin/env python3
"""Cartãozinho para o evento (no estilo do cartão de referência que ele mandou: quadrado, fundo claro, uma cor só,
desenhos cortados nos cantos): logo, frase curta, QR code do site, cupom JOGAMAUA5 (5%) e @suavez_bg.
Tamanho 9 x 9 cm; sai também uma folha A4 com 6 cartões e marcas de corte, para imprimir em papel comum e recortar.

    python3 promo/cartao_evento.py   # promo/out/cartao_evento.png, cartao_evento_A4.pdf e .png
"""
import math
import os

import qrcode
from PIL import Image, ImageDraw

from promo_3jogos import ORANGE, ORANGE_D, NAVY, WHITE, BLACK, XB, SB, LOGO, OUT, f, text_c

DPI = 300
CM = DPI / 2.54
LADO = int(9 * CM)  # 9 cm
CUPOM = "JOGAMAUA5"
SITE = "https://suavez.acervodejogos.com.br/"
FUNDO = (255, 250, 244)
COR = ORANGE_D


def meeple(d, cx, cy, s, cor, rot=0.0, contorno=None):
    """Meeple (bonequinho de jogo) desenhado como polígono + cabeça, girado."""
    pts = [(0, -0.30), (0.42, -0.08), (0.42, 0.06), (0.20, 0.06), (0.36, 0.50), (0.10, 0.50), (0, 0.30),
           (-0.10, 0.50), (-0.36, 0.50), (-0.20, 0.06), (-0.42, 0.06), (-0.42, -0.08)]
    c, s_ = math.cos(rot), math.sin(rot)
    P = [(cx + s * (x * c - y * s_), cy + s * (x * s_ + y * c)) for x, y in pts]
    hx, hy = cx + s * (0 * c - (-0.40) * s_), cy + s * (0 * s_ + (-0.40) * c)
    r = s * 0.17
    if contorno:
        d.polygon(P, fill=cor, outline=contorno, width=int(s * 0.05))
        d.ellipse((hx - r, hy - r, hx + r, hy + r), fill=cor, outline=contorno, width=int(s * 0.05))
    else:
        d.polygon(P, fill=cor)
        d.ellipse((hx - r, hy - r, hx + r, hy + r), fill=cor)


def dado(d, cx, cy, s, cor, rot=0.0, n=5):
    """Dado (quadrado arredondado girado) com os pontos em branco."""
    im = Image.new("RGBA", (int(s), int(s)), (0, 0, 0, 0))
    di = ImageDraw.Draw(im)
    di.rounded_rectangle((0, 0, s - 1, s - 1), radius=int(s * 0.2), fill=cor)
    pos = {5: [(0.27, 0.27), (0.73, 0.27), (0.5, 0.5), (0.27, 0.73), (0.73, 0.73)], 3: [(0.27, 0.27), (0.5, 0.5), (0.73, 0.73)]}
    r = s * 0.08
    for x, y in pos[n]:
        di.ellipse((x * s - r, y * s - r, x * s + r, y * s + r), fill=FUNDO)
    im = im.rotate(math.degrees(rot), expand=True, resample=Image.BICUBIC)
    return im, (int(cx - im.width / 2), int(cy - im.height / 2))


def qr(tam):
    q = qrcode.QRCode(border=0, box_size=10, error_correction=qrcode.constants.ERROR_CORRECT_M)
    q.add_data(SITE)
    q.make(fit=True)
    return q.make_image(fill_color=NAVY, back_color=FUNDO).convert("RGB").resize((tam, tam), Image.NEAREST)


def cartao():
    L = LADO
    img = Image.new("RGB", (L, L), FUNDO)
    d = ImageDraw.Draw(img)
    s = L / 1000  # o desenho foi pensado num quadrado de 1000
    # enfeites cortados nos cantos (como os cookies da referência)
    meeple(d, 40 * s, 60 * s, 230 * s, COR, -0.5)
    im, p = dado(d, 950 * s, 70 * s, 150 * s, COR, 0.4)
    img.paste(im, p, im)
    im, p = dado(d, 975 * s, 930 * s, 200 * s, COR, -0.3, 3)
    img.paste(im, p, im)
    meeple(d, 70 * s, 960 * s, 170 * s, COR, 0.35)
    for x, y, r in ((850 * s, 260 * s, 12 * s), (150 * s, 330 * s, 10 * s), (880 * s, 640 * s, 9 * s), (120 * s, 700 * s, 12 * s)):
        d.ellipse((x - r, y - r, x + r, y + r), outline=COR, width=int(4 * s))
    # logo
    lg = Image.open(LOGO).convert("RGBA")
    lw = int(400 * s)
    lg = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS)
    img.paste(lg, (int(L / 2 - lw / 2), int(55 * s)), lg)
    y = 55 * s + lg.height + 22 * s
    text_c(d, (L / 2, y + 22 * s), "Bora jogar?", f(XB, int(44 * s)), NAVY)
    text_c(d, (L / 2, y + 78 * s), "Alugue jogos de tabuleiro", f(BLACK, int(46 * s)), COR)
    text_c(d, (L / 2, y + 128 * s), "e jogue em casa por 5 dias!", f(BLACK, int(46 * s)), COR)
    y += 175 * s
    # QR + cupom lado a lado
    qs = int(250 * s)
    qx = int(190 * s)
    img.paste(qr(qs), (qx, int(y)))
    d.text((qx + qs / 2, y + qs + 26 * s), "aponte a câmera", font=f(SB, int(26 * s)), fill=NAVY, anchor="mm")
    cx0, cx1 = 475 * s, 860 * s
    d.rounded_rectangle((cx0, y + 10 * s, cx1, y + qs - 10 * s), radius=int(26 * s), outline=COR, width=int(5 * s))
    mid = (cx0 + cx1) / 2
    d.text((mid, y + 55 * s), "CUPOM", font=f(XB, int(30 * s)), fill=NAVY, anchor="mm")
    d.text((mid, y + 112 * s), CUPOM, font=f(BLACK, int(44 * s)), fill=COR, anchor="mm")
    d.text((mid, y + 175 * s), "5% OFF", font=f(BLACK, int(44 * s)), fill=NAVY, anchor="mm")
    y += qs + 70 * s
    d.text((L / 2, y + 10 * s), "@suavez_bg", font=f(BLACK, int(42 * s)), fill=COR, anchor="mm")
    d.text((L / 2, y + 58 * s), "Mauá e ABC · retire ou receba em casa", font=f(SB, int(27 * s)), fill=NAVY,
           anchor="mm")
    return img


def folha_a4(c):
    """A4 em pé com 2 x 3 cartões e marcas de corte nos cantos."""
    W, H = int(21 * CM), int(29.7 * CM)
    a4 = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(a4)
    gap = int(0.4 * CM)
    x0 = (W - 2 * LADO - gap) // 2
    y0 = (H - 3 * LADO - 2 * gap) // 2
    m = int(0.35 * CM)
    for r in range(3):
        for k in range(2):
            x, y = x0 + k * (LADO + gap), y0 + r * (LADO + gap)
            a4.paste(c, (x, y))
            d.rectangle((x, y, x + LADO - 1, y + LADO - 1), outline=(215, 215, 215), width=2)  # linha fina de corte
            for cx_, cy_ in ((x, y), (x + LADO, y), (x, y + LADO), (x + LADO, y + LADO)):
                d.line((cx_ - m, cy_, cx_ - 6, cy_), fill=(120, 120, 120), width=2) if cx_ == x else \
                    d.line((cx_ + 6, cy_, cx_ + m, cy_), fill=(120, 120, 120), width=2)
                d.line((cx_, cy_ - m, cx_, cy_ - 6), fill=(120, 120, 120), width=2) if cy_ == y else \
                    d.line((cx_, cy_ + 6, cx_, cy_ + m), fill=(120, 120, 120), width=2)
    return a4


def main():
    os.makedirs(OUT, exist_ok=True)
    c = cartao()
    c.save(os.path.join(OUT, "cartao_evento.png"), dpi=(DPI, DPI))
    a4 = folha_a4(c)
    a4.save(os.path.join(OUT, "cartao_evento_A4.png"), dpi=(DPI, DPI))
    a4.save(os.path.join(OUT, "cartao_evento_A4.pdf"), resolution=DPI)
    print("ok", c.size, a4.size)


if __name__ == "__main__":
    main()
