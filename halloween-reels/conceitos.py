#!/usr/bin/env python3
"""Halloween, 3ª rodada: ele achou o visual da noite roxa "muito infantil" e pediu para mudar TODO o visual.
Três opções mais adultas, lado a lado (mesmos jogos da 2ª versão):

    1 · Pôster de cinema   (preto, luz fria de cima, letreiro serifado espaçado, bloco de créditos)
    2 · Mansão gótica      (papel de parede vinho, retrato em moldura dourada, velas, placa de museu)
    3 · Tabuleiro Ouija    (madeira escura, letras em arco; a prancheta soletra o nome do jogo)

    python3 conceitos.py      # out/conceitos.jpg
"""
import math
import os
import random
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "comum"))
from motor import W, H, font, logo_card, cola, sombra  # noqa: E402

OUT = os.path.join(ROOT, "out")
AS = os.path.join(ROOT, "assets")
FT = os.path.join(AS, "fonts")
OURO = (214, 178, 104)
CREME = (238, 228, 210)


def fnt(nome, s, peso=None):
    f = ImageFont.truetype(os.path.join(FT, nome), int(s))
    if peso:
        try:
            f.set_variation_by_axes([peso])
        except Exception:
            pass
    return f


def espacado(d, xy, txt, f, fill, track, anchor="mm"):
    """Texto com espaçamento entre letras (letreiro de cinema)."""
    larg = sum(d.textlength(c, font=f) for c in txt) + track * (len(txt) - 1)
    x = xy[0] - larg / 2 if anchor == "mm" else xy[0]
    for c in txt:
        d.text((x, xy[1]), c, font=f, fill=fill, anchor="lm")
        x += d.textlength(c, font=f) + track


@lru_cache(None)
def caixa(n, h):
    im = Image.open(os.path.join(AS, n + ".png")).convert("RGBA")
    im = im.crop(im.getbbox())
    return im.resize((int(im.width * h / im.height), int(h)), Image.LANCZOS)


def tom(im, mult, add=(0, 0, 0)):
    a = np.asarray(im).astype(np.float32)
    a[..., :3] = a[..., :3] * np.array(mult) + np.array(add)
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def marca(img):
    wm = logo_card(140)
    img.alpha_composite(wm, (W - wm.width - 30, 40))


# ---------------------------------------------------------------- 1: pôster de cinema
def opcao_1():
    img = Image.new("RGBA", (W, H), (6, 7, 9, 255))
    luz = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(luz).polygon([(440, -50), (640, -50), (960, 1250), (120, 1250)], fill=(170, 190, 215, 46))
    img.alpha_composite(luz.filter(ImageFilter.GaussianBlur(70)))
    chao = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(chao).ellipse((190, 1110, 890, 1260), fill=(160, 180, 205, 60))
    img.alpha_composite(chao.filter(ImageFilter.GaussianBlur(40)))
    bx = tom(caixa("finalgirl", 760), (0.86, 0.92, 1.05))
    cola(img, sombra(bx, 30, (0, 40), 0.8), 540, 780)
    d = ImageDraw.Draw(img)
    espacado(d, (540, 190), "UMA NOITE.  QUATRO JOGOS.", fnt("Cinzel.ttf", 34, 500), (200, 205, 215), 6)
    d.line((470, 240, 610, 240), fill=(170, 20, 25), width=3)
    espacado(d, (540, 1300), "FINAL GIRL", fnt("Cinzel.ttf", 128, 700), CREME, 18)
    d.text((540, 1405), "Sobreviva ao assassino. Sozinho.", font=fnt("Cormorant-Italic.ttf", 58, 500),
           fill=(205, 205, 210), anchor="mm")
    cred = fnt("Cinzel.ttf", 26, 600)
    espacado(d, (540, 1505), "1 JOGADOR  ·  60 MINUTOS  ·  14+", cred, (150, 152, 160), 4)
    espacado(d, (540, 1550), "EM CARTAZ NA SUA VEZ  ·  31 DE OUTUBRO", cred, (170, 20, 25), 4)
    marca(img)
    return img


# ---------------------------------------------------------------- 2: mansão gótica
def papel_parede():
    img = Image.new("RGBA", (W, H), (44, 10, 18, 255))
    d = ImageDraw.Draw(img)
    for yy in range(-60, H + 120, 180):
        for xx in range(-60, W + 120, 150):
            ox = 75 if (yy // 180) % 2 else 0
            cx, cy = xx + ox, yy
            d.polygon([(cx, cy - 46), (cx + 26, cy), (cx, cy + 46), (cx - 26, cy)], outline=(70, 20, 32), width=3)
            d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=(64, 18, 30))
    v = np.zeros((H, W), np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    v = 1 - 0.75 * np.clip(np.hypot((xx - 540) / 720, (yy - 820) / 1000), 0, 1) ** 1.6
    a = np.asarray(img).astype(np.float32)
    a[..., :3] *= v[..., None]
    return Image.fromarray(a.astype(np.uint8))


def moldura(w, h):
    m = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(m)
    for k, (c, lw) in enumerate([((120, 88, 40), 34), (OURO, 14), ((90, 64, 28), 6), ((240, 210, 140), 3)]):
        o = (0, 22, 34, 40)[k]
        d.rectangle((o, o, w - 1 - o, h - 1 - o), outline=c, width=lw)
    for cx, cy in ((0, 0), (w, 0), (0, h), (w, h)):
        d.ellipse((cx - 40, cy - 40, cx + 40, cy + 40), fill=(120, 88, 40), outline=OURO, width=6)
        d.ellipse((cx - 14, cy - 14, cx + 14, cy + 14), fill=(240, 210, 140))
    return m


def vela(img, x, y, fase):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    gd.ellipse((x - 230, y - 330, x + 230, y + 130), fill=(255, 150, 60, 70))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(80)))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x - 26, y - 40, x + 26, y + 260), radius=8, fill=(232, 222, 196))
    d.polygon([(x - 26, y - 40), (x - 10, y - 20), (x + 2, y - 46), (x + 26, y - 40)], fill=(232, 222, 196))
    d.line((x, y - 60, x, y - 40), fill=(40, 30, 20), width=4)
    fl = 1 + 0.08 * math.sin(fase)
    d.ellipse((x - 14, y - 120 * fl, x + 14, y - 52), fill=(255, 200, 90))
    d.ellipse((x - 7, y - 100 * fl, x + 7, y - 56), fill=(255, 245, 210))
    d.rounded_rectangle((x - 70, y + 250, x + 70, y + 280), radius=10, fill=(150, 112, 50))


def opcao_2():
    img = papel_parede()
    d = ImageDraw.Draw(img)
    d.text((540, 200), "Os retratos da mansão", font=fnt("Cormorant-Italic.ttf", 64, 600), fill=OURO, anchor="mm")
    espacado(d, (540, 270), "QUATRO JOGOS PARA O HALLOWEEN", fnt("Cinzel.ttf", 30, 600), (200, 170, 120), 5)
    fw, fh = 640, 820
    tela = Image.new("RGBA", (fw - 80, fh - 80), (18, 12, 12, 255))
    bx = tom(caixa("vale_monstros", 560), (1.0, 0.92, 0.8))
    tela.alpha_composite(bx, ((tela.width - bx.width) // 2, (tela.height - bx.height) // 2))
    q = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
    q.alpha_composite(tela, (40, 40))
    q.alpha_composite(moldura(fw, fh))
    cola(img, sombra(q, 30, (0, 30), 0.8), 540, 820)
    vela(img, 120, 1150, 0.3)
    vela(img, 960, 1150, 2.0)
    d = ImageDraw.Draw(img)
    pl = Image.new("RGBA", (620, 190), (0, 0, 0, 0))
    dp = ImageDraw.Draw(pl)
    dp.rounded_rectangle((0, 0, 619, 189), radius=10, fill=(150, 116, 58), outline=(240, 210, 140), width=4)
    dp.text((310, 62), "O VALE DOS MONSTROS II", font=fnt("Cinzel.ttf", 40, 700), fill=(40, 22, 10), anchor="mm")
    dp.text((310, 118), "Os monstros invadiram a cidade.", font=fnt("Cormorant-Italic.ttf", 38, 600), fill=(50, 28, 12),
            anchor="mm")
    dp.text((310, 160), "1 A 6 JOGADORES · 90 MIN", font=fnt("Cinzel.ttf", 22, 600), fill=(70, 44, 20), anchor="mm")
    cola(img, sombra(pl, 12, (0, 10), 0.6), 540, 1370)
    marca(img)
    return img


# ---------------------------------------------------------------- 3: tabuleiro Ouija
def madeira():
    rng = np.random.default_rng(7)
    yy = np.arange(H)[:, None]
    xx = np.arange(W)[None, :]
    ruido = np.array(Image.fromarray((rng.random((60, 8)) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC),
                     np.float32) / 255
    veio = 0.5 + 0.5 * np.sin(yy / 11.0 + ruido * 5 + np.sin(xx / 260.0) * 2)
    base = np.array([52, 30, 18], np.float32)
    a = base[None, None, :] * (0.75 + 0.35 * veio[..., None])
    v = 1 - 0.8 * np.clip(np.hypot((xx - 540) / 700, (yy - 900) / 1000), 0, 1) ** 1.8
    a = a * v[..., None]
    return Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert("RGBA")


def opcao_3():
    img = madeira()
    d = ImageDraw.Draw(img)
    f = fnt("Cinzel.ttf", 60, 700)
    for ls, rx, ry in (("ABCDEFGHIJKLM", 480, 210), ("NOPQRSTUVWXYZ", 420, 150)):
        n = len(ls)
        cy = 700 if ls[0] == "A" else 900
        for k, c in enumerate(ls):
            ang = math.radians(195 + 150 * k / (n - 1))
            x, y = 540 + rx * math.cos(ang), cy + ry * math.sin(ang) + 60
            d.text((x, y), c, font=f, fill=(222, 196, 150), anchor="mm")
    d.text((150, 260), "SIM", font=fnt("Cinzel.ttf", 64, 700), fill=(222, 196, 150), anchor="mm")
    d.text((930, 260), "NÃO", font=fnt("Cinzel.ttf", 64, 700), fill=(222, 196, 150), anchor="mm")
    for x in (150, 930):
        d.ellipse((x - 46, 140, x + 46, 220), outline=(222, 196, 150), width=3)
    espacado(d, (540, 1100), "1 2 3 4 5 6 7 8 9 0", fnt("Cinzel.ttf", 40, 600), (200, 176, 130), 8)
    espacado(d, (540, 1185), "ADEUS", fnt("Cinzel.ttf", 50, 700), (222, 196, 150), 14)
    # prancheta parada sobre a letra "M" do nome soletrado
    pr = Image.new("RGBA", (300, 340), (0, 0, 0, 0))
    dp = ImageDraw.Draw(pr)
    dp.polygon([(150, 6), (292, 250), (230, 334), (70, 334), (8, 250)], fill=(232, 214, 176), outline=(120, 84, 40))
    dp.ellipse((95, 120, 205, 230), fill=(0, 0, 0, 0), outline=(120, 84, 40), width=8)
    pr2 = Image.new("RGBA", pr.size, (0, 0, 0, 0))
    pr2.alpha_composite(pr)
    lente = Image.new("L", pr.size, 0)
    ImageDraw.Draw(lente).ellipse((100, 125, 200, 225), fill=255)
    pr2.putalpha(Image.fromarray(np.minimum(np.asarray(pr2.getchannel("A")), 255 - np.asarray(lente))))
    cola(img, sombra(pr2, 16, (0, 18), 0.6), 560, 520, -8)
    soletra = "M A S C A"
    espacado(d, (540, 1300), soletra + " _ _ _ _", fnt("Cinzel.ttf", 56, 700), (255, 150, 60), 6)
    bx = caixa("mascarade", 420)
    cola(img, sombra(tom(bx, (1.0, 0.9, 0.78)), 22, (0, 24), 0.8), 540, 1570, -4, 0.7)
    d.text((540, 70 + 40), "", font=f)
    marca(img)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    ims = [opcao_1(), opcao_2(), opcao_3()]
    folha = Image.new("RGB", (3 * 540 + 40, 960 + 90), (24, 22, 26))
    d = ImageDraw.Draw(folha)
    for k, (im, nome) in enumerate(zip(ims, ["1 · Pôster de cinema", "2 · Mansão gótica", "3 · Tabuleiro Ouija"])):
        folha.paste(im.convert("RGB").resize((540, 960), Image.LANCZOS), (10 + k * 550, 80))
        d.text((10 + k * 550 + 270, 40), nome, font=font("Bungee-Regular.ttf", 32), fill=(240, 235, 225), anchor="mm")
    folha.save(os.path.join(OUT, "conceitos.jpg"), quality=92)
    print("ok")


if __name__ == "__main__":
    main()
