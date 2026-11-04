#!/usr/bin/env python3
"""Capa do Reels do tarô ("tira print e descobre sua noite"). Pedido dele: capa que dê CURIOSIDADE para clicar.
Mesmo céu roxo e as mesmas cartas do taro.py. Tudo que importa fica na área da grade do perfil (y 285–1635).

    A  cartas_viradas: as 3 cartas de verso (lua), a do meio levantada e brilhando com um "?" — o que tem embaixo?
    B  print: visor de câmera (REC) em volta das 3 cartas abertas + "PARA NA HORA CERTA"

    python3 capa_taro.py   → out/capa_taro_A.png, out/capa_taro_B.png e out/capa_taro_opcoes.jpg
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import taro as T  # noqa: E402
from taro import W, H, OURO, INK, ROXO, WHITE, CW, CH, font, letreiro, pilula, cola, emoji, logo_card  # noqa: E402

OUT = T.OUT


def brilho(c, cor=(230, 170, 255), raio=34, forca=0.9):
    b = Image.new("RGBA", (c.width + 160, c.height + 160), (0, 0, 0, 0))
    a = Image.new("L", b.size, 0)
    a.paste(c.getchannel("A"), (80, 80))
    g = Image.new("RGBA", b.size, cor + (0,))
    g.putalpha(a.filter(ImageFilter.GaussianBlur(raio)).point(lambda v: int(min(255, v * forca))))
    b.alpha_composite(g)
    b.alpha_composite(c, (80, 80))
    return b


def raios(img, cx, cy, n=18, r=900, a=46):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for k in range(n):
        a0 = k * math.tau / n
        pts = [(cx, cy), (cx + r * math.cos(a0 - 0.06), cy + r * math.sin(a0 - 0.06)),
               (cx + r * math.cos(a0 + 0.06), cy + r * math.sin(a0 + 0.06))]
        d.polygon(pts, fill=(255, 214, 130, a))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(10)))


def interrogacao(c):
    """Verso da carta com um '?' dourado grande por cima da lua."""
    c = c.copy()
    d = ImageDraw.Draw(c)
    d.ellipse((CW / 2 - 118, CH / 2 - 118, CW / 2 + 118, CH / 2 + 118), fill=(70, 30, 110))
    d.text((CW / 2, CH / 2 + 8), "?", font=font("Bungee-Regular.ttf", 230), fill=OURO, anchor="mm",
           stroke_width=6, stroke_fill=INK)
    return c


def topo(img, y_tit=470):
    wm = logo_card(150)
    img.alpha_composite(wm, (W - wm.width - 40, 300))
    cola(img, emoji("🔮", 110), 120, 330, -10)


def capa_a():
    img = T.ceu(0.3).copy()
    topo(img)
    cola(img, letreiro("TIRA PRINT!", 150, OURO, INK, 14, sombra_px=9, cor_sombra=INK), 540, 520, -2)
    cola(img, pilula("E DESCOBRE SUA NOITE DE JOGOS", 40, (120, 40, 170), WHITE, OURO, bw=5), 540, 680, 1)
    raios(img, 540, 1060)
    v = T.verso()
    for x, y, r in ((215, 1110, -12), (865, 1110, 12)):
        cola(img, brilho(v, raio=22, forca=0.5), x, y, r, 0.86)
    cola(img, brilho(interrogacao(v), (255, 210, 120), 40, 1.1), 540, 1045, 0, 0.98)
    cola(img, letreiro("O QUE AS CARTAS\nDIZEM PRA VOCÊ?", 74, WHITE, INK, 10, sombra_px=6, cor_sombra=INK),
         540, 1500, -1)
    return img.convert("RGB")


def visor(img, x0, y0, x1, y1, cor=WHITE, lado=90, w=12):
    d = ImageDraw.Draw(img)
    for cx, cy, sx, sy in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        d.line((cx, cy, cx + sx * lado, cy), fill=cor, width=w)
        d.line((cx, cy, cx, cy + sy * lado), fill=cor, width=w)
    rec = (x0 + 14, y0 - 66)
    d.ellipse((rec[0], rec[1], rec[0] + 30, rec[1] + 30), fill=(235, 40, 60))
    d.text((rec[0] + 44, rec[1] + 15), "REC", font=font("Bungee-Regular.ttf", 32), fill=WHITE, anchor="lm")


def capa_b():
    img = T.ceu(1.1).copy()
    topo(img)
    cola(img, letreiro("PARA NA\nHORA CERTA", 112, OURO, INK, 13, sombra_px=8, cor_sombra=INK), 540, 520, -2)
    cola(img, pilula("TIRA PRINT E VÊ O QUE SAIU", 40, (230, 40, 90)), 540, 720, 1)
    for j, (x, y, r) in enumerate(((200, 1120, -7), (540, 1085, 0), (880, 1120, 7))):
        c = T.frente(j, (3, 5, 2)[j])
        cola(img, brilho(c, raio=26, forca=0.6), x, y, r, 0.92)
    visor(img, 40, 800, W - 40, 1440)
    cola(img, emoji("📸", 120), 930, 1420, 10)
    cola(img, letreiro("QUAL NOITE\nVAI SER A SUA?", 74, WHITE, INK, 10, sombra_px=6, cor_sombra=INK), 520, 1545, -1)
    return img.convert("RGB")


def main():
    os.makedirs(OUT, exist_ok=True)
    a, b = capa_a(), capa_b()
    a.save(os.path.join(OUT, "capa_taro_A.png"))
    b.save(os.path.join(OUT, "capa_taro_B.png"))
    s = 0.42
    fo = Image.new("RGB", (int(W * s) * 2 + 60, int(H * s) + 110), (240, 236, 228))
    d = ImageDraw.Draw(fo)
    for k, (im, rot) in enumerate(((a, "A  cartas viradas"), (b, "B  na hora do print"))):
        x = 20 + k * (int(W * s) + 20)
        fo.paste(im.resize((int(W * s), int(H * s)), Image.LANCZOS), (x, 90))
        d.text((x + 10, 30), rot, font=font("Bungee-Regular.ttf", 40), fill=INK)
        d.rectangle((x, 90 + int(285 * s), x + int(W * s) - 1, 90 + int(1635 * s)), outline=(230, 40, 90), width=3)
    fo.save(os.path.join(OUT, "capa_taro_opcoes.jpg"), quality=90)


if __name__ == "__main__":
    main()
