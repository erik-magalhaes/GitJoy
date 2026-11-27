#!/usr/bin/env python3
"""Visual com a cara do AZUL (26/nov, ele: "os stickers a gente faz em outro tipo de vídeo; coloca na temática do
jogo"): azulejos portugueses azul e branco, placas creme com moldura azul dupla como o letreiro da caixa, serifa
clássica (DM Serif Display), relógio = MOSTRUÁRIO do jogo (disco com mandala azul), as 5 peças do jogo nos cantos.

    /usr/bin/python3 tema.py      # out/tema_teste.jpg
"""
import math
import os
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
W, H = 1080, 1920
SERIF = os.path.join(REPO, "comum", "fontes", "DMSerifDisplay-Regular.ttf")
FIG = os.path.join(REPO, "assinatura-reels", "assets", "fonts", "Figtree.ttf")
AZ_ESC = (22, 48, 110)
AZ = (36, 96, 178)
TURQ = (70, 176, 200)
CREME = (251, 243, 226)
BRANCO = (250, 250, 246)
LARANJA = (232, 122, 38)
VERM = (196, 52, 52)
OURO = (236, 182, 64)
PRETO = (30, 34, 46)


def serif(s):
    return ImageFont.truetype(SERIF, int(s))


def fig(s, peso=800):
    f = ImageFont.truetype(FIG, int(s))
    try:
        f.set_variation_by_axes([peso])
    except Exception:
        pass
    return f


def sombra(im, r=10, dx=0, dy=8, a=0.35):
    p = r * 2 + abs(dy) + 4
    out = Image.new("RGBA", (im.width + 2 * p, im.height + 2 * p), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (10, 20, 50, 0))
    al = Image.new("L", out.size, 0)
    al.paste(im.getchannel("A"), (p + dx, p + dy))
    sh.putalpha(al.point(lambda v: int(v * a)).filter(ImageFilter.GaussianBlur(r)))
    out.alpha_composite(sh)
    out.alpha_composite(im, (p, p))
    return out


# ---------------------------------------------------------------- azulejo português (azul e branco)
@lru_cache(None)
def azulejo_pt(s=160, var=0):
    """Azulejo azul e branco: quartos de flor nos cantos (juntando 4 vira uma flor) + estrela/rosácea no meio."""
    k = 4
    S = s * k
    im = Image.new("RGBA", (S, S), BRANCO + (255,))
    d = ImageDraw.Draw(im)
    c = S / 2
    az, az2 = (AZ, AZ_ESC) if var % 2 == 0 else (AZ_ESC, AZ)
    for (x, y) in [(0, 0), (S, 0), (0, S), (S, S)]:  # quartos de flor
        d.ellipse((x - S * .30, y - S * .30, x + S * .30, y + S * .30), fill=az)
        d.ellipse((x - S * .2, y - S * .2, x + S * .2, y + S * .2), fill=BRANCO)
        d.ellipse((x - S * .1, y - S * .1, x + S * .1, y + S * .1), fill=az2)
    for a in range(8):  # rosácea central
        ang = math.radians(a * 45 + (22.5 if var >= 2 else 0))
        x, y = c + S * .17 * math.cos(ang), c + S * .17 * math.sin(ang)
        d.ellipse((x - S * .085, y - S * .085, x + S * .085, y + S * .085), fill=az)
    d.ellipse((c - S * .1, c - S * .1, c + S * .1, c + S * .1), fill=BRANCO)
    d.ellipse((c - S * .055, c - S * .055, c + S * .055, c + S * .055), fill=az2)
    for (dx, dy) in [(0, -1), (0, 1), (-1, 0), (1, 0)]:  # losangos nas bordas
        x, y = c + dx * S * .5, c + dy * S * .5
        d.polygon([(x - S * .07, y), (x, y - S * .07), (x + S * .07, y), (x, y + S * .07)], fill=az2)
    d.rectangle((0, 0, S - 1, S - 1), outline=(205, 214, 228), width=k * 2)
    return im.resize((s, s), Image.LANCZOS)


@lru_cache(None)
def parede_azulejos(w=W, h=H, s=180, clareia=0.0):
    im = Image.new("RGBA", (w, h))
    for y in range(0, h, s):
        for x in range(0, w, s):
            im.alpha_composite(azulejo_pt(s, ((x // s) + (y // s)) % 2 * 2), (x, y))
    if clareia:
        im = Image.blend(im, Image.new("RGBA", (w, h), CREME + (255,)), clareia)
    return im


# ---------------------------------------------------------------- as 5 peças do jogo (em relevo, como as de resina)
PECAS = {
    "azul": ((40, 110, 205), BRANCO, "flor"),
    "amarelo": ((238, 168, 52), (205, 70, 40), "losango"),
    "vermelho": ((214, 58, 58), (250, 210, 120), "circulo"),
    "preto": ((34, 40, 58), (96, 205, 220), "estrela"),
    "turquesa": ((120, 205, 222), BRANCO, "floco"),
}


@lru_cache(None)
def peca(cor, s=120):
    fundo, tinta, motivo = PECAS[cor]
    k = 4
    S = s * k
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    esc = tuple(int(v * .62) for v in fundo)
    d.rounded_rectangle((0, S * .06, S - 1, S - 1), S * .12, fill=esc)            # lateral (espessura)
    d.rounded_rectangle((0, 0, S - 1, S * .94), S * .12, fill=fundo)
    c, cy = S / 2, S * .47
    if motivo == "flor":
        for a in range(4):
            ang = math.radians(45 + a * 90)
            x, y = c + S * .17 * math.cos(ang), cy + S * .17 * math.sin(ang)
            d.ellipse((x - S * .13, y - S * .13, x + S * .13, y + S * .13), fill=tinta)
        d.ellipse((c - S * .07, cy - S * .07, c + S * .07, cy + S * .07), fill=OURO)
    elif motivo == "losango":
        d.polygon([(c, cy - S * .3), (c + S * .3, cy), (c, cy + S * .3), (c - S * .3, cy)], fill=tinta)
        d.polygon([(c, cy - S * .15), (c + S * .15, cy), (c, cy + S * .15), (c - S * .15, cy)], fill=fundo)
    elif motivo == "circulo":
        d.ellipse((c - S * .27, cy - S * .27, c + S * .27, cy + S * .27), outline=tinta, width=int(S * .07))
        d.ellipse((c - S * .08, cy - S * .08, c + S * .08, cy + S * .08), fill=tinta)
    elif motivo == "estrela":
        pts = []
        for a in range(16):
            r = S * (.32 if a % 2 == 0 else .13)
            ang = math.radians(-90 + a * 22.5)
            pts.append((c + r * math.cos(ang), cy + r * math.sin(ang)))
        d.polygon(pts, fill=tinta)
    elif motivo == "floco":
        for a in range(3):
            ang = math.radians(a * 60)
            dx, dy = S * .3 * math.cos(ang), S * .3 * math.sin(ang)
            d.line((c - dx, cy - dy, c + dx, cy + dy), fill=tinta, width=int(S * .06))
        d.ellipse((c - S * .07, cy - S * .07, c + S * .07, cy + S * .07), fill=tinta)
    d.rounded_rectangle((S * .06, S * .04, S * .5, S * .14), S * .05, fill=(255, 255, 255, 70))  # brilho
    return sombra(im.resize((s, s), Image.LANCZOS), 6, 0, 6, 0.4)


# ---------------------------------------------------------------- placas (como o letreiro da caixa)
def _moldura(d, x0, y0, x1, y1, r):
    d.rounded_rectangle((x0, y0, x1, y1), r, fill=CREME, outline=AZ_ESC, width=8)
    d.rounded_rectangle((x0 + 12, y0 + 12, x1 - 12, y1 - 12), max(4, r - 10), outline=AZ, width=3)


def placa(txt, s=64, cor=AZ_ESC, minw=0, sub=None):
    f = serif(s)
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    b = d0.textbbox((0, 0), txt, font=f)
    w = max(minw, b[2] - b[0] + s * 1.6)
    h = s * 1.55 + (s * .62 if sub else 0)
    im = Image.new("RGBA", (int(w) + 60, int(h) + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x0, x1 = 30, w + 30
    _moldura(d, x0, 2, x1, h, 18)
    for x in (x0, x1):  # pontas em losango, como o letreiro
        d.polygon([(x - 28, h / 2), (x, h / 2 - 24), (x + 28, h / 2), (x, h / 2 + 24)], fill=AZ_ESC)
        d.polygon([(x - 14, h / 2), (x, h / 2 - 12), (x + 14, h / 2), (x, h / 2 + 12)], fill=OURO)
    yt = s * .78 + 2
    d.text((im.width / 2, yt), txt, font=f, fill=cor, anchor="mm")
    if sub:
        d.text((im.width / 2, yt + s * .78), sub, font=fig(s * .42), fill=AZ, anchor="mm")
    return sombra(im, 10, 0, 8, 0.35)


def letreiro(txt, s=120, cor=BRANCO, contorno=AZ_ESC):
    """Texto grande em serifa, branco com contorno azul e sombra."""
    f = serif(s)
    sw = max(5, int(s * .07))
    linhas = txt.split("\n")
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    w = max(d0.textbbox((0, 0), l, font=f, stroke_width=sw)[2] for l in linhas) + 20
    lh = int(s * 1.02)
    im = Image.new("RGBA", (w, lh * len(linhas) + 2 * sw + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k, l in enumerate(linhas):
        d.text((w / 2, sw + 5 + k * lh + lh / 2), l, font=f, fill=cor, stroke_width=sw, stroke_fill=contorno, anchor="mm")
    return sombra(im, 8, 0, 8, 0.45)


# ---------------------------------------------------------------- mostruário (o relógio)
@lru_cache(None)
def _mostruario_base(s):
    k = 3
    S = s * k
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = S / 2
    d.ellipse((0, 0, S - 1, S - 1), fill=(196, 116, 70))                      # borda terracota (como os do jogo)
    d.ellipse((S * .04, S * .04, S * .96, S * .96), fill=CREME)
    d.ellipse((S * .09, S * .09, S * .91, S * .91), fill=AZ)
    for a in range(16):  # pétalas da mandala
        ang = math.radians(a * 22.5)
        x, y = c + S * .335 * math.cos(ang), c + S * .335 * math.sin(ang)
        d.ellipse((x - S * .06, y - S * .06, x + S * .06, y + S * .06), fill=TURQ if a % 2 else BRANCO)
    d.ellipse((S * .2, S * .2, S * .8, S * .8), fill=AZ_ESC)
    d.ellipse((S * .23, S * .23, S * .77, S * .77), fill=CREME)
    return im.resize((s, s), Image.LANCZOS)


def mostruario(seg_rest, s=200, alerta=False):
    im = _mostruario_base(s).copy()
    d = ImageDraw.Draw(im)
    m = max(0, int(math.ceil(seg_rest)))
    d.text((s / 2, s / 2 + 2), f"{m // 60}:{m % 60:02d}", font=serif(s * .2), fill=VERM if alerta else AZ_ESC,
           anchor="mm")
    return sombra(im, 8, 0, 6, 0.4)


# ---------------------------------------------------------------- cartão do asterisco
@lru_cache(None)
def nota_asterisco():
    w, faixa = 1000, 34
    linhas = ["o azulejo QUEBRA quando não", "cabe na linha da esquerda:", "você pegou mais do que cabe."]
    h = 100 + 64 * len(linhas) + 40 + faixa
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    _moldura(d, 2, 2, w - 3, h - 3, 26)
    for x in range(26, w - 26 - faixa, faixa):  # faixinha de azulejos no pé
        t = azulejo_pt(faixa, (x // faixa) % 2 * 2)
        im.alpha_composite(t, (x, h - faixa - 22))
    d.text((40, 66), "*", font=serif(120), fill=VERM, anchor="lm")
    d.text((104, 62), "Quando quebra?", font=serif(58), fill=VERM, anchor="lm")
    for k, l in enumerate(linhas):
        d.text((48, 140 + k * 64), l, font=fig(46), fill=AZ_ESC, anchor="lm")
    return sombra(im, 12, 0, 10, 0.4)


def teste():
    img = parede_azulejos(clareia=0.55).copy()
    img.alpha_composite(placa("NA SUA VEZ", 60), (200, 200))
    img.alpha_composite(letreiro("AZUL MINI", 140), (200, 380))
    img.alpha_composite(mostruario(42, 220), (40, 40))
    img.alpha_composite(nota_asterisco(), (20, 700))
    for k, c in enumerate(PECAS):
        img.alpha_composite(peca(c, 130), (80 + k * 190, 1200))
    img.alpha_composite(placa("+2", 90), (300, 1450))
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    img.convert("RGB").save(os.path.join(ROOT, "out", "tema_teste.jpg"), quality=90)


if __name__ == "__main__":
    teste()
