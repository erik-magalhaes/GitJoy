#!/usr/bin/env python3
"""Story "ÚLTIMAS HORAS" do cupom do ABC (pedido dele, 15/out à noite): o JOGAABC5 (5% na locação para quem mora no
ABC) vale até 15/10. Mesmo visual do story_cupom_abc.py; relógio em contagem, faixa "ACABA HOJE!" e o espaço LIVRE
(y ~1565–1630) para o adesivo de link do Instagram.

    python3 story_cupom_abc_ultimas.py      # out/story_cupom_abc_ultimas.png
"""
import math
import os

from PIL import Image, ImageDraw

from promo_3jogos import ORANGE, ORANGE_D, NAVY, GREEN, BLUE, WHITE, BLACK, XB, SB, LOGO, OUT, f, fundo, paste_c, \
    shadowed, text_c
from story_cupom_abc import ticket, seta

W, H = 1080, 1920
VERMELHO = (220, 50, 47)


def relogio(r):
    """Relógio simples (círculo, marcas e ponteiros quase na meia-noite)."""
    im = Image.new("RGBA", (2 * r + 20, 2 * r + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = r + 10
    d.ellipse((c - r, c - r, c + r, c + r), fill=WHITE, outline=NAVY, width=14)
    for k in range(12):
        a = k * math.tau / 12
        r0 = r - 30 if k % 3 else r - 42
        d.line((c + r0 * math.sin(a), c - r0 * math.cos(a), c + (r - 20) * math.sin(a), c - (r - 20) * math.cos(a)),
               fill=NAVY, width=8 if k % 3 == 0 else 5)
    for ang, comp, lw, cor in ((-15, 0.48, 14, NAVY), (-40, 0.7, 9, VERMELHO)):  # 11h55
        a = math.radians(ang)
        d.line((c, c, c + r * comp * math.sin(a), c - r * comp * math.cos(a)), fill=cor, width=lw)
    d.ellipse((c - 14, c - 14, c + 14, c + 14), fill=VERMELHO)
    return im


def main():
    img = fundo(W, H)
    d = ImageDraw.Draw(img)
    lg = Image.open(LOGO).convert("RGBA")
    lw = 240
    lg = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS)
    card = Image.new("RGBA", (lg.width + 40, lg.height + 30), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=26, fill=WHITE)
    card.alpha_composite(lg, (20, 15))
    paste_c(img, shadowed(card, 12, (4, 8), 0.2), W / 2, 250)
    text_c(d, (455, 425), "ÚLTIMAS", f(BLACK, 150), NAVY)
    text_c(d, (455, 570), "HORAS!", f(BLACK, 150), ORANGE_D)
    paste_c(img, shadowed(relogio(90), 10, (4, 8), 0.22), 912, 498, 8)
    d = ImageDraw.Draw(img)
    faixa = Image.new("RGBA", (720, 110), (0, 0, 0, 0))
    fd = ImageDraw.Draw(faixa)
    fd.rounded_rectangle((0, 0, 719, 109), radius=55, fill=VERMELHO)
    text_c(fd, (360, 58), "O CUPOM ACABA HOJE!", f(BLACK, 54), WHITE)
    paste_c(img, shadowed(faixa, 10, (4, 8), 0.2), W / 2, 715, -2)
    d = ImageDraw.Draw(img)
    text_c(d, (W / 2, 840), "Mora no ABC? Garanta seus", f(XB, 46), NAVY)
    text_c(d, (W / 2, 900), "5% OFF na locação dos jogos", f(XB, 46), NAVY)
    paste_c(img, shadowed(ticket(820, 380), 16, (6, 12), 0.22), W / 2, 1145, -2)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((W / 2 - 270, 1354, W / 2 + 270, 1424), radius=35, fill=NAVY)
    text_c(d, (W / 2, 1390), "VÁLIDO SÓ ATÉ HOJE, 15/10", f(BLACK, 38), WHITE)
    text_c(d, (W / 2, 1470), "Reserve agora pelo link:", f(XB, 42), GREEN)
    paste_c(img, seta(100, 80, GREEN), W / 2, 1535)
    # 1580–1640: espaço livre para o adesivo de link do Instagram
    text_c(d, (W / 2, 1700), "RETIRE EM MAUÁ OU RECEBA EM CASA", f(XB, 34), NAVY)
    text_c(d, (W / 2, 1745), "@suavez_bg", f(SB, 32), BLUE)
    os.makedirs(OUT, exist_ok=True)
    img.convert("RGB").save(os.path.join(OUT, "story_cupom_abc_ultimas.png"))
    print("ok")


if __name__ == "__main__":
    main()
