#!/usr/bin/env python3
"""Arte da promoção de prazo progressivo: 3 jogos = 7 dias, 5 jogos = 10 dias, 7 jogos = 15 dias.

    python3 promo/promo_progressivo.py   # gera promo/out/promo_progressivo_feed.png e _story.png
"""
import os

from PIL import Image, ImageDraw

from promo_3jogos import (ORANGE, ORANGE_D, NAVY, GREEN, GREEN_L, BLUE, WHITE, BLACK, XB, SB, LOGO, OUT,
                          caixas, f, fundo, paste_c, shadowed, text_c)

FAIXAS = [(3, 7, BLUE), (5, 10, ORANGE), (7, 15, GREEN)]


def pilha(n, h):
    """n caixas de jogo empilhadas em leque (repete as caixas que temos)."""
    bx = caixas(h)
    w = int(bx[0].width + (n - 1) * h * 0.28 + 40)
    im = Image.new("RGBA", (w, int(h * 1.25)), (0, 0, 0, 0))
    for k in range(n):
        b = bx[k % len(bx)].rotate((k - (n - 1) / 2) * 6, expand=True, resample=Image.BICUBIC)
        im.alpha_composite(b, (int(k * h * 0.28), int(abs(k - (n - 1) / 2) * h * 0.04)))
    return im


def escada(width, height):
    """Três degraus subindo: quanto mais jogos, mais dias."""
    im = Image.new("RGBA", (int(width), int(height)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    gap = width * 0.04
    cw = (width - gap * 2) / 3
    for k, (jogos, dias, cor) in enumerate(FAIXAS):
        x0 = k * (cw + gap)
        bh = height * (0.48 + 0.15 * k)  # cada degrau mais alto (o topo fica livre para as caixas)
        y0 = height - bh
        d.rounded_rectangle((x0 + 8, y0 + 12, x0 + cw + 8, height + 12), radius=int(cw * 0.12), fill=NAVY + (60,))
        d.rounded_rectangle((x0, y0, x0 + cw, height), radius=int(cw * 0.12), fill=cor)
        text_c(d, (x0 + cw / 2, y0 + bh * 0.15), f"{jogos} JOGOS", f(XB, int(cw * 0.15)), WHITE)
        d.line((x0 + cw * 0.2, y0 + bh * 0.28, x0 + cw * 0.8, y0 + bh * 0.28), fill=WHITE + (150,), width=4)
        text_c(d, (x0 + cw / 2, y0 + bh * 0.56), str(dias), f(BLACK, int(min(cw * 0.48, bh * 0.4))), WHITE)
        text_c(d, (x0 + cw / 2, y0 + bh * 0.86), "DIAS", f(BLACK, int(cw * 0.17)), WHITE)
        p = pilha(jogos, int(cw * 0.36))
        p = p.resize((int(min(cw * 0.95, p.width)), int(p.height * min(cw * 0.95, p.width) / p.width)))
        im.alpha_composite(p, (int(x0 + cw / 2 - p.width / 2), int(y0 - p.height + 10)))
    return im


def arte(W, H, story):
    img = fundo(W, H)
    d = ImageDraw.Draw(img)
    s = W / 1080
    y = (170 if story else 40) * s
    lg = Image.open(LOGO).convert("RGBA")
    lw = int(300 * s * (1 if story else 0.78))
    lg = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS)
    card = Image.new("RGBA", (lg.width + 40, lg.height + 30), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=26, fill=WHITE)
    card.alpha_composite(lg, (20, 15))
    paste_c(img, shadowed(card, 12, (4, 8), 0.2), W / 2, y + card.height / 2)
    y += card.height + (50 if story else 28) * s
    text_c(d, (W / 2, y + 40 * s), "QUANTO MAIS JOGOS,", f(BLACK, int(80 * s)), NAVY)
    y += 105 * s
    band_h = 140 * s
    d.rounded_rectangle((60 * s, y, W - 60 * s, y + band_h), radius=int(36 * s), fill=ORANGE)
    text_c(d, (W / 2, y + band_h / 2 + 4), "MAIS DIAS DE JOGO!", f(BLACK, int(80 * s)), WHITE)
    y += band_h + (60 if story else 30) * s
    eh = (740 if story else 600) * s
    esc = escada(W - 120 * s, eh)
    paste_c(img, esc, W / 2, y + eh / 2)
    y += eh + (60 if story else 40) * s
    text_c(d, (W / 2, y + 10 * s), "O prazo extra vale para TODOS os jogos do carrinho,", f(SB, int(34 * s)), NAVY)
    text_c(d, (W / 2, y + 56 * s), "pelo mesmo preço!", f(XB, int(40 * s)), ORANGE_D)
    y += (120 if story else 105) * s
    if story:
        box = (60 * s, y, W - 60 * s, y + 110 * s)
        d.rounded_rectangle(box, radius=int(26 * s), fill=GREEN_L, outline=(134, 239, 172), width=3)
        text_c(d, (W / 2, y + 55 * s), "Monte o carrinho no site: o prazo entra sozinho!", f(XB, int(34 * s)),
               (21, 101, 52))
        y += 150 * s
    text_c(d, (W / 2, y + 10 * s), "RETIRE EM MAUÁ OU RECEBA EM CASA", f(XB, int(36 * s)), NAVY)
    text_c(d, (W / 2, y + 62 * s), "suavez.acervodejogos.com.br  ·  @suavez_bg", f(SB, int(32 * s)), ORANGE_D)
    return img.convert("RGB")


def main():
    os.makedirs(OUT, exist_ok=True)
    arte(1080, 1350, False).save(os.path.join(OUT, "promo_progressivo_feed.png"))
    arte(1080, 1920, True).save(os.path.join(OUT, "promo_progressivo_story.png"))
    print("ok")


if __name__ == "__main__":
    main()
