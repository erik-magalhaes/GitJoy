#!/usr/bin/env python3
"""Flyer impresso para evento (A5, 300 dpi): o que é a Sua Vez, como funciona, preço, prazo progressivo
(3 jogos = 7 dias, 5 = 10, 7 = 15) e o cupom do evento JOGAMAUA5 (5% de desconto na locação), com QR code do site.

    python3 promo/flyer_evento.py   # promo/out/flyer_evento.png e .pdf (A5) + flyer_evento_A4_2x.pdf (2 por folha A4)
"""
import os

import qrcode
from PIL import Image, ImageDraw

from promo_3jogos import (ORANGE, ORANGE_D, NAVY, GREEN, BLUE, WHITE, BLACK, XB, SB, LOGO, OUT, f, fundo, paste_c,
                          shadowed, text_c)
from promo_progressivo import escada

CUPOM = "JOGAMAUA5"
SITE = "https://suavez.acervodejogos.com.br/"
W, H = 1748, 2480  # A5 a 300 dpi
S = H / 2060  # o layout foi pensado em ~2060 "unidades" de altura


# 15 caixas DIFERENTES nas pilhas (fotos oficiais que já temos no projeto; nada de recorte do site)
PILHAS = [["hotstreak-reels/assets/pecas/caixa.png", "gravados-reels/assets/oficial/draftosaurus.png",
           "gravados-reels/assets/oficial/gravity_superstar.png"],
          ["architects-reels/assets/oficial/caixa3d.png", "voodoo-reels/assets/pieces/box.png",
           "sintonia-reels/assets/pieces/box.png", "gravados-reels/assets/oficial/go_cuckoo.png",
           "gravados-reels/assets/oficial/scooby_doo.png"],
          ["marvel-reels/assets/caixas/base.png", "finalgirl-reels/assets/oficial/FG-CoreBox.png",
           "marvel-reels/assets/caixas/xmen.png", "finalgirl-reels/assets/oficial/FG-FF1-1.png",
           "marvel-reels/assets/caixas/spider_geddon.png", "finalgirl-reels/assets/oficial/FG-FF4-1.png",
           "marvel-reels/assets/caixas/deadpool.png"]]


def caixas_pilha(larg):
    """Cada degrau ganha suas caixas (todas diferentes) em fileiras: 3 → 3; 5 → 2+3; 7 → 3+4 (a de trás mais alta)."""
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = []
    for grupo in PILHAS:
        n = len(grupo)
        filas = [grupo] if n <= 3 else [grupo[:n // 2], grupo[n // 2:]]
        cols = max(len(f_) for f_ in filas)
        cel = larg / (cols * 0.86 + 0.14)  # caixas encostadas com ~14% de sobreposição
        ims_filas = []
        for fila in filas:
            ims = []
            for p in fila:
                im = Image.open(os.path.join(repo, p)).convert("RGBA")
                im = im.crop(im.getbbox())
                sc = min(cel / im.width, cel * 1.15 / im.height)
                ims.append(im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS))
            ims_filas.append(ims)
        alt = max(i.height for i in ims_filas[-1])
        dy = int(alt * 0.55)
        H_ = alt + dy * (len(filas) - 1) + 20
        im_ = Image.new("RGBA", (int(larg), H_), (0, 0, 0, 0))
        for r, ims in enumerate(ims_filas):
            x0 = (larg - (len(ims) * cel * 0.86 + cel * 0.14)) / 2
            for c, im in enumerate(ims):
                cx = x0 + c * cel * 0.86 + cel / 2
                y0 = r * dy + (alt - im.height)
                im_.alpha_composite(shadowed(im, 6, (3, 6), 0.3), (int(cx - im.width / 2), int(y0)))
        out.append(im_)
    return out


def qr(tam):
    q = qrcode.QRCode(border=1, box_size=10, error_correction=qrcode.constants.ERROR_CORRECT_M)
    q.add_data(SITE)
    q.make(fit=True)
    return q.make_image(fill_color=NAVY, back_color="white").convert("RGBA").resize((tam, tam), Image.NEAREST)


def cupom(w, h):
    """Ticket recortado com borda tracejada: o cupom do evento."""
    im = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = int(h * 0.16)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=int(28 * S), fill=NAVY)
    for x in (0, w):  # "mordidas" laterais do ticket
        d.ellipse((x - r, h / 2 - r, x + r, h / 2 + r), fill=(0, 0, 0, 0))
    m = 22 * S
    x = m
    while x < w - m:  # borda tracejada
        for y in (m, h - m):
            d.line((x, y, min(x + 22 * S, w - m), y), fill=ORANGE, width=int(4 * S))
        x += 40 * S
    text_c(d, (w / 2, h * 0.2), "CUPOM EXCLUSIVO DO EVENTO", f(XB, int(34 * S)), WHITE)
    cw = d.textlength(CUPOM, font=f(BLACK, int(96 * S)))
    bx = (w / 2 - cw / 2 - 30 * S, h * 0.32, w / 2 + cw / 2 + 30 * S, h * 0.66)
    d.rounded_rectangle(bx, radius=int(20 * S), fill=WHITE)
    text_c(d, (w / 2, (bx[1] + bx[3]) / 2 + 4 * S), CUPOM, f(BLACK, int(96 * S)), ORANGE_D)
    text_c(d, (w / 2, h * 0.82), "5% DE DESCONTO NA LOCAÇÃO", f(BLACK, int(46 * S)), ORANGE)
    return im


def passo(n, t1, t2, cor, w):
    im = Image.new("RGBA", (int(w), int(250 * S)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = 52 * S
    d.ellipse((w / 2 - r, 0, w / 2 + r, 2 * r), fill=cor)
    text_c(d, (w / 2, r + 3 * S), str(n), f(BLACK, int(60 * S)), WHITE)
    text_c(d, (w / 2, 2 * r + 42 * S), t1, f(BLACK, int(34 * S)), NAVY)
    text_c(d, (w / 2, 2 * r + 86 * S), t2, f(SB, int(28 * S)), NAVY)
    return im


def arte():
    img = fundo(W, H)
    d = ImageDraw.Draw(img)
    y = 40 * S
    lg = Image.open(LOGO).convert("RGBA")
    lw = int(270 * S)
    lg = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS)
    card = Image.new("RGBA", (lg.width + 50, lg.height + 36), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=30, fill=WHITE)
    card.alpha_composite(lg, (25, 18))
    paste_c(img, shadowed(card, 14, (4, 10), 0.2), W / 2, y + card.height / 2)
    y += card.height + 26 * S
    text_c(d, (W / 2, y + 40 * S), "ALUGUE JOGOS DE TABULEIRO", f(BLACK, int(70 * S)), NAVY)
    y += 100 * S
    band = 120 * S
    d.rounded_rectangle((70 * S, y, W - 70 * S, y + band), radius=int(34 * S), fill=ORANGE)
    text_c(d, (W / 2, y + band / 2 + 3 * S), "e jogue em casa por 5 dias!", f(BLACK, int(60 * S)), WHITE)
    y += band + 26 * S
    text_c(d, (W / 2, y + 22 * S), "Mais de 160 jogos modernos para toda a família · a partir de R$ 15",
           f(XB, int(30 * S)), NAVY)
    y += 80 * S
    # como funciona
    pw = (W - 140 * S) / 3
    for k, (t1, t2, cor) in enumerate((("RESERVE", "no site", BLUE), ("RETIRE EM MAUÁ", "ou receba em casa", ORANGE),
                                        ("JOGUE 5 DIAS", "e devolva", GREEN))):
        img.alpha_composite(passo(k + 1, t1, t2, cor, pw), (int(70 * S + k * pw), int(y)))
    y += 232 * S
    # prazo progressivo
    text_c(d, (W / 2, y + 30 * S), "QUANTO MAIS JOGOS, MAIS DIAS!", f(BLACK, int(58 * S)), ORANGE_D)
    y += 80 * S
    eh = 540 * S
    paste_c(img, escada(W - 340 * S, eh, caixas_pilha((W - 340 * S) / 3 * 0.94), base=0.40, passo=0.09), W / 2, y + eh / 2)
    y += eh + 26 * S
    text_c(d, (W / 2, y + 16 * S), "O prazo extra vale para todos os jogos do carrinho, pelo mesmo preço!",
           f(XB, int(28 * S)), NAVY)
    y += 70 * S
    # cupom
    ch = 255 * S
    paste_c(img, shadowed(cupom(W - 180 * S, ch), 16, (6, 14), 0.3), W / 2, y + ch / 2)
    y += ch + 30 * S
    # rodapé: QR + contatos
    qs = int(165 * S)
    q = qr(qs)
    qx = int(110 * S)
    fundo_q = Image.new("RGBA", (qs + 24, qs + 24), WHITE)
    fundo_q.alpha_composite(q, (12, 12))
    img.alpha_composite(shadowed(fundo_q, 8, (2, 6), 0.2), (qx - 12, int(y)))
    tx = qx + qs + 60 * S
    d.text((tx, y + 4 * S), "Aponte a câmera e reserve:", font=f(XB, int(30 * S)), fill=NAVY)
    d.text((tx, y + 46 * S), "suavez.acervodejogos.com.br", font=f(BLACK, int(36 * S)), fill=ORANGE_D)
    d.text((tx, y + 98 * S), "Instagram: @suavez_bg", font=f(XB, int(30 * S)), fill=NAVY)
    d.text((tx, y + 140 * S), "Mauá e ABC · retirada ou entrega", font=f(SB, int(26 * S)), fill=NAVY)
    return img.convert("RGB"), y + qs + 24


def main():
    os.makedirs(OUT, exist_ok=True)
    img, fim = arte()
    print("altura usada:", int(fim), "de", H)
    png = os.path.join(OUT, "flyer_evento.png")
    img.save(png, dpi=(300, 300))
    img.save(os.path.join(OUT, "flyer_evento.pdf"), resolution=300)
    a4 = Image.new("RGB", (2 * W, H), WHITE)  # A4 deitado com 2 flyers (cortar ao meio)
    a4.paste(img, (0, 0))
    a4.paste(img, (W, 0))
    a4.save(os.path.join(OUT, "flyer_evento_A4_2x.pdf"), resolution=300)
    print("ok")


if __name__ == "__main__":
    main()
