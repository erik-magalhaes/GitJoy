#!/usr/bin/env python3
"""Story do cupom do ABC: quem mora no ABC tem 5% de desconto na locação com o cupom JOGAABC5 (pedido dele, 12/out).
Visual da loja (o das promoções: creme com listras laranja, cartão do logo, Poppins azul-marinho, laranja/verde/azul).
Deixa um espaço LIVRE (y ~1330–1560) para ele colar o adesivo de link do Instagram, com uma seta apontando.

    python3 story_cupom_abc.py      # out/story_cupom_abc.png
"""
import os

from PIL import Image, ImageDraw

from promo_3jogos import ORANGE, ORANGE_D, NAVY, GREEN, BLUE, WHITE, BLACK, XB, SB, LOGO, OUT, f, fundo, paste_c, \
    shadowed, text_c

W, H = 1080, 1920
CUPOM = "JOGAABC5"  # "Joga ABC 5" (como o JOGAMAUA5 = "Joga Mauá 5")


def ticket(w, h):
    """Cupom com recortes redondos nas laterais e borda tracejada."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=36, fill=WHITE)
    r = 38
    for x in (0, w):  # recortes de "ticket"
        d.ellipse((x - r, h / 2 - r, x + r, h / 2 + r), fill=(0, 0, 0, 0))
    m = 26
    x = m + 20
    while x < w - m - 20:  # tracejado laranja por dentro
        d.line((x, m, x + 22, m), fill=ORANGE, width=5)
        d.line((x, h - m, x + 22, h - m), fill=ORANGE, width=5)
        x += 38
    text_c(d, (w / 2, 78), "USE O CUPOM", f(XB, 38), NAVY)
    s = 124
    while d.textlength(CUPOM, font=f(BLACK, s)) > w - 150:  # cabe entre os recortes do ticket
        s -= 4
    text_c(d, (w / 2, h / 2 + 4), CUPOM, f(BLACK, s), ORANGE_D)
    text_c(d, (w / 2, h - 70), "no carrinho do site", f(SB, 34), NAVY)
    return im


def seta(w, h, cor):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((w / 2 - 14, 0, w / 2 + 14, h - 50), radius=14, fill=cor)
    d.polygon([(w / 2 - 46, h - 62), (w / 2 + 46, h - 62), (w / 2, h)], fill=cor)
    return im


def main():
    img = fundo(W, H)
    d = ImageDraw.Draw(img)
    lg = Image.open(LOGO).convert("RGBA")
    lw = 280
    lg = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS)
    card = Image.new("RGBA", (lg.width + 40, lg.height + 30), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=26, fill=WHITE)
    card.alpha_composite(lg, (20, 15))
    paste_c(img, shadowed(card, 12, (4, 8), 0.2), W / 2, 300)
    text_c(d, (W / 2, 520), "MORA NO ABC?", f(BLACK, 104), NAVY)
    d.rounded_rectangle((110, 595, W - 110, 815), radius=50, fill=ORANGE)
    text_c(d, (W / 2, 712), "5% OFF", f(BLACK, 170), WHITE)
    text_c(d, (W / 2, 872), "na locação dos seus jogos!", f(XB, 46), NAVY)
    paste_c(img, shadowed(ticket(820, 380), 16, (6, 12), 0.22), W / 2, 1135, -2)
    d = ImageDraw.Draw(img)
    text_c(d, (W / 2, 1365), "Reserve pelo link:", f(XB, 42), GREEN)
    paste_c(img, seta(110, 110, GREEN), W / 2, 1455)
    # 1510–1610: espaço livre para o adesivo de link do Instagram
    text_c(d, (W / 2, 1655), "RETIRE EM MAUÁ OU RECEBA EM CASA", f(XB, 34), NAVY)
    text_c(d, (W / 2, 1702), "@suavez_bg", f(SB, 32), BLUE)
    os.makedirs(OUT, exist_ok=True)
    img.convert("RGB").save(os.path.join(OUT, "story_cupom_abc.png"))
    print("ok")


if __name__ == "__main__":
    main()
