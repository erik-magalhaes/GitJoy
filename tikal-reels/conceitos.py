#!/usr/bin/env python3
"""3 visuais para o vídeo explicando o TIKAL (10/nov/2026), todos com as peças OFICIAIS (pecas.py):
  A MAPA VIVO — vista de cima, pergaminho do manual, hexágonos caindo, exploradores andando pelas lajes, 10 PA em tabuletas
  B TRAILER NA SELVA — arte da capa em tela cheia (escura, névoa, raios de luz), tabuleiro em perspectiva, letreiro dourado
  C CADERNO DO ARQUEÓLOGO — página de caderno, peças "fotografadas" presas com fita, anotações à mão e carimbo
    /usr/bin/python3 conceitos.py   → out/conceitos.jpg
"""
import math
import os
import random

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import pecas as P
from pecas import W, H, fonte, cola

OUT = os.path.join(P.ROOT, "out")
VERDE, CREME, MARROM, OURO = (28, 86, 44), (244, 230, 196), (63, 36, 18), (240, 196, 80)


def texto_c(d, xy, txt, f, cor, sw=0, sc=None, anchor="mm"):
    d.text(xy, txt, font=f, fill=cor, anchor=anchor, stroke_width=sw, stroke_fill=sc)


def pergaminho(semente=1, base=(232, 210, 160)):
    rnd = np.random.default_rng(semente)
    n = rnd.normal(0, 1, (H // 8, W // 8))
    n = cv2.GaussianBlur(n, (0, 0), 6)
    n = cv2.resize(n, (W, H), interpolation=cv2.INTER_CUBIC)
    f = cv2.GaussianBlur(rnd.normal(0, 1, (H, W)), (0, 0), 1.2)
    a = np.array(base, float)[None, None] * (1 + 0.10 * n[..., None] + 0.02 * f[..., None])
    yy, xx = np.mgrid[0:H, 0:W]
    v = 1 - 0.35 * (((xx - W / 2) / (W * 0.7)) ** 2 + ((yy - H / 2) / (H * 0.7)) ** 2)
    return Image.fromarray(np.clip(a * v[..., None], 0, 255).astype(np.uint8)).convert("RGBA")


def lajes(d, p0, p1, n, cor=(150, 150, 140)):
    for k in range(n):
        u = (k + 1) / (n + 1)
        x, y = p0[0] + (p1[0] - p0[0]) * u, p0[1] + (p1[1] - p0[1]) * u
        d.rounded_rectangle((x - 16, y - 12, x + 16, y + 12), 5, fill=cor, outline=(70, 70, 64), width=3)


def tabuletas(img, gastos, y=330):
    d = ImageDraw.Draw(img)
    for k in range(10):
        x = 120 + k * 93
        on = k >= gastos
        c = (226, 190, 92) if on else (120, 104, 80)
        d.rounded_rectangle((x - 38, y - 44, x + 38, y + 44), 10, fill=c, outline=MARROM, width=5)
        texto_c(d, (x, y), "PA", fonte("Anton-Regular.ttf", 34), MARROM if on else (80, 66, 50))


# ------------------------------------------------------------------------------------------- A
def mapa_vivo():
    img = pergaminho()
    d = ImageDraw.Draw(img)
    texto_c(d, (W / 2, 150), "VOCÊ TEM 10 PONTOS", fonte("Anton-Regular.ttf", 92), (250, 244, 220), 8, VERDE)
    texto_c(d, (W / 2, 245), "DE AÇÃO POR TURNO", fonte("Anton-Regular.ttf", 70), (250, 244, 220), 7, VERDE)
    tabuletas(img, 3)
    w = 330
    pos = {(0, 0): "templo", (1, 0): "clareira", (2, 0): "ruina", (0, 1): "clareira", (1, 1): "templo",
           (2, 1): "vulcao", (1, 2): "ruina", (0, 2): "templo", (2, 2): "clareira"}
    x0, y0 = 290, 620
    for (c, l), t in sorted(pos.items(), key=lambda k: (k[0][1], k[0][0])):
        cx, cy = P.hex_centro(c, l, w, x0, y0)
        cola(img, P.hexa(t, w), cx, cy, sombra=10)
    d = ImageDraw.Draw(img)
    a, b = P.hex_centro(0, 1, w, x0, y0), P.hex_centro(1, 1, w, x0, y0)
    lajes(d, a, b, 2)
    # caminho pontilhado do explorador
    for k in range(14):
        u = k / 13
        x, y = a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u - 60 * math.sin(math.pi * u)
        d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=(255, 255, 255))
    for k, (cor, dx) in enumerate((("vermelho", -40), ("vermelho", 30), ("azul", 0))):
        cx, cy = b[0] + dx + (0 if k < 2 else -10), b[1] + (40 if k < 2 else -60)
        cola(img, P.meeple(cor, 120), cx, cy, sombra=6)
    cola(img, P.meeple("vermelho", 140), a[0], a[1] - 10, -12, sombra=6)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((180, 1530, 900, 1640), 30, fill=(250, 244, 220), outline=MARROM, width=6)
    texto_c(d, (W / 2, 1585), "ANDAR = 1 PA POR LAJE", fonte("Anton-Regular.ttf", 58), MARROM)
    return img


# ------------------------------------------------------------------------------------------- B
def trailer():
    c = P.capa()
    # recorte vertical da capa em volta do templo, escurecido
    y0 = int(c.height * 0.215)  # abaixo do logo da capa e acima dos nomes dos autores
    y1 = int(c.height * 0.915)
    hh = y1 - y0
    ww = int(hh * W / H)
    x = int(c.width * 0.60 - ww / 2)
    bg = c.crop((x, y0, x + ww, y1)).resize((W, H), Image.LANCZOS)
    a = np.asarray(bg).astype(float)
    yy = np.linspace(0, 1, H)[:, None, None]
    a = a * (0.55 + 0.25 * (1 - yy)) * np.array([0.92, 1.0, 0.95])
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    # raios de luz
    luz = Image.new("L", (W, H), 0)
    dl = ImageDraw.Draw(luz)
    for k in range(5):
        x0 = 520 + k * 90
        dl.polygon([(x0, 0), (x0 + 60, 0), (x0 - 260 + k * 40, H), (x0 - 420 + k * 40, H)], fill=40)
    luz = luz.filter(ImageFilter.GaussianBlur(30))
    img.alpha_composite(Image.merge("RGBA", (Image.new("L", (W, H), 255), Image.new("L", (W, H), 240),
                                             Image.new("L", (W, H), 190), luz)))
    # tabuleiro de hexágonos em perspectiva no pé
    tab = Image.new("RGBA", (1500, 1100), (0, 0, 0, 0))
    w = 340
    tipos = ["templo", "clareira", "ruina", "clareira", "templo", "vulcao", "ruina", "templo", "clareira", "clareira",
             "templo", "ruina"]
    k = 0
    for l in range(3):
        for c in range(4):
            cx, cy = P.hex_centro(c, l, w, 270, 220)
            cola(tab, P.hexa(tipos[k % len(tipos)], w), cx, cy)
            k += 1
    src = np.float32([[0, 0], [1500, 0], [1500, 1100], [0, 1100]])
    dst = np.float32([[150, 1230], [930, 1230], [1260, 1880], [-180, 1880]])
    M = cv2.getPerspectiveTransform(src, dst)
    warp = cv2.warpPerspective(np.asarray(tab), M, (W, H), flags=cv2.INTER_LINEAR)
    img.alpha_composite(Image.fromarray(warp))
    for cor, x, y, h in (("vermelho", 470, 1400, 120), ("azul", 650, 1460, 135), ("laranja", 380, 1600, 165),
                         ("vermelho", 520, 1610, 160)):
        cola(img, P.meeple(cor, h), x, y, sombra=8)
    d = ImageDraw.Draw(img)
    texto_c(d, (W / 2, 330), "QUEM DOMINA", fonte("Cinzel.ttf", 104), OURO, 4, (40, 26, 8))
    texto_c(d, (W / 2, 450), "OS TEMPLOS?", fonte("Cinzel.ttf", 104), OURO, 4, (40, 26, 8))
    texto_c(d, (W / 2, 560), "uma expedição no coração da selva", fonte("Cormorant-Italic.ttf", 54), (240, 236, 220))
    return img


# ------------------------------------------------------------------------------------------- C
def caderno():
    img = pergaminho(3, (240, 232, 210))
    d = ImageDraw.Draw(img)
    for y in range(260, H, 62):
        d.line((0, y, W, y), fill=(170, 190, 210), width=2)
    d.line((120, 0, 120, H), fill=(220, 120, 120), width=3)
    mao = fonte("PatrickHand-Regular.ttf", 84)
    texto_c(d, (W / 2 + 40, 170), "Diário da expedição", mao, (40, 50, 110))

    def foto(sp, cx, cy, rot, w):
        f = Image.new("RGBA", (w + 40, w + 90), (252, 250, 244, 255))
        s = sp.copy()
        s.thumbnail((w, w))
        f.alpha_composite(s, (20 + (w - s.width) // 2, 20 + (w - s.height) // 2))
        cola(img, f, cx, cy, rot, sombra=10)
        fita = Image.new("RGBA", (170, 54), (230, 214, 160, 200))
        cola(img, fita, cx, cy - (w + 90) / 2 + 10, rot + 8)

    foto(P.hexa("templo", 420), 330, 620, -5, 420)
    foto(P.hexa("ruina", 360), 790, 980, 6, 360)
    d = ImageDraw.Draw(img)
    f2 = fonte("PatrickHand-Regular.ttf", 58)
    d.text((560, 470), "Templo!\ncada andar = +1 nível\n(2 PA)", font=f2, fill=(40, 50, 110), spacing=4)
    d.text((150, 920), "Ruína: cava o\ntesouro (3 PA)", font=f2, fill=(40, 50, 110), spacing=4)
    d.line((470, 1010, 600, 980), fill=(200, 30, 30), width=6)
    for k, t in enumerate((0, 1, 2)):
        cola(img, P.tesouro(t, 150), 260 + k * 170, 1260, (k - 1) * 8, sombra=6)
    cola(img, P.meeple("vermelho", 170), 840, 1330, 8, sombra=6)
    # carimbo
    car = Image.new("RGBA", (420, 170), (0, 0, 0, 0))
    dc = ImageDraw.Draw(car)
    dc.rounded_rectangle((6, 6, 414, 164), 22, outline=(200, 30, 40, 230), width=10)
    dc.text((210, 88), "10 PA", font=fonte("Anton-Regular.ttf", 110), fill=(200, 30, 40, 230), anchor="mm")
    cola(img, car, 560, 1560, 9)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    ims = [mapa_vivo(), trailer(), caderno()]
    for n, im in zip("ABC", ims):
        im.convert("RGB").save(os.path.join(OUT, f"conceito_{n}.jpg"), quality=92)
    sh = Image.new("RGB", (3 * 560 + 40, 1040), (30, 30, 30))
    d = ImageDraw.Draw(sh)
    for k, (im, t) in enumerate(zip(ims, ("A  MAPA VIVO", "B  TRAILER NA SELVA", "C  CADERNO DO ARQUEÓLOGO"))):
        s = im.convert("RGB").resize((540, 960), Image.LANCZOS)
        sh.paste(s, (10 + k * 570, 70))
        d.text((10 + k * 570 + 270, 35), t, font=fonte("Anton-Regular.ttf", 40), fill="white", anchor="mm")
    sh.save(os.path.join(OUT, "conceitos.jpg"), quality=90)
    print("ok")


if __name__ == "__main__":
    main()
