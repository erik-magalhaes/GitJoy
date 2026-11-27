#!/usr/bin/env python3
"""AZUL MINI EXPLICADO EM 1 MINUTO (25/nov, pedido dele): estilo ADESIVOS FOFOS (referência: capa "Cute & Groovy"
que ele mandou — fundo rosa clarinho, doodles com contorno escuro grosso, cores pastel, borda branca de adesivo).
Sem narração: tudo escrito na tela; relógio-adesivo contando de 1:00 durante a explicação.
Edição deles = Galápagos AZU501 (2 a 4 jogadores, 8+). Regras = as do Azul (o Mini só muda o tamanho).

    /usr/bin/python3 azul.py --frame 1 6 12 18 25 32 38 45 52 58 62 66
    /usr/bin/python3 azul.py            # out/azul_{com_som,para_musica}_final.mp4
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
sys.path.insert(0, os.path.join(REPO, "becas-reels"))
sys.path.insert(0, os.path.join(REPO, "comum"))
import kit as K  # noqa: E402
import sons as S  # noqa: E402

K.OUT = os.path.join(ROOT, "out")
W, H, FPS = 1080, 1920, 30
TINTA = (52, 34, 58)          # contorno dos adesivos
ROSA_BG = (255, 232, 236)
BR = (255, 255, 255)
ROSA, LILAS, MENTA, AMAR, PESS, CEU = (255, 150, 190), (196, 170, 240), (150, 225, 200), (255, 214, 102), \
    (255, 176, 130), (150, 205, 245)
LILITA = os.path.join(REPO, "assinatura-reels", "assets", "fonts", "LilitaOne.ttf")
FIG = os.path.join(REPO, "assinatura-reels", "assets", "fonts", "Figtree.ttf")
# azulejos: (fundo, desenho, motivo)
AZ = {
    "azul": ((62, 120, 214), BR, "flor"),
    "amarelo": ((255, 186, 60), (232, 90, 50), "losango"),
    "vermelho": ((236, 80, 80), (255, 214, 120), "circulo"),
    "preto": ((48, 52, 74), (110, 220, 230), "estrela"),
    "turquesa": ((120, 215, 225), BR, "floco"),
}
CORES = list(AZ)


def fonte(s, fig=False, peso=800):
    f = ImageFont.truetype(FIG if fig else LILITA, int(s))
    if fig:
        try:
            f.set_variation_by_axes([peso])
        except Exception:
            pass
    return f


def ease(u):
    u = min(1, max(0, u))
    return u * u * (3 - 2 * u)


def out_back(u, k=1.7):
    u = min(1, max(0, u)) - 1
    return 1 + (k + 1) * u ** 3 + k * u ** 2


# ---------------------------------------------------------------- adesivo
def adesivo(im, borda=14, sombra=True):
    """Borda branca de adesivo + sombra suave embaixo."""
    p = borda + 16
    a = Image.new("L", (im.width + 2 * p, im.height + 2 * p), 0)
    a.paste(im.getchannel("A"), (p, p))
    big = a.filter(ImageFilter.MaxFilter(borda * 2 + 1)).filter(ImageFilter.GaussianBlur(1.2))
    out = Image.new("RGBA", a.size, (0, 0, 0, 0))
    if sombra:
        sh = Image.new("RGBA", a.size, TINTA + (0,))
        sh.putalpha(big.point(lambda v: int(v * 0.28)).filter(ImageFilter.GaussianBlur(6)))
        out.alpha_composite(sh, (6, 10)) if False else out.alpha_composite(sh.transform(
            a.size, Image.AFFINE, (1, 0, -6, 0, 1, -10)))
    branco = Image.new("RGBA", a.size, BR + (0,))
    branco.putalpha(big)
    out.alpha_composite(branco)
    out.alpha_composite(im, (p, p))
    return out


def texto(txt, s, cor=BR, contorno=TINTA, sw=None, linha=1.0, fig=False, borda=12):
    f = fonte(s, fig)
    sw = sw if sw is not None else max(4, int(s * 0.09))
    linhas = txt.split("\n")
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    bbs = [d0.textbbox((0, 0), l, font=f, stroke_width=sw) for l in linhas]
    w = max(b[2] - b[0] for b in bbs) + 10
    lh = int(s * 1.05 * linha)
    im = Image.new("RGBA", (int(w), lh * len(linhas) + sw * 2 + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k, l in enumerate(linhas):
        d.text((im.width / 2, sw + 5 + k * lh + lh / 2), l, font=f, fill=cor, stroke_width=sw, stroke_fill=contorno,
               anchor="mm")
    return adesivo(im, borda) if borda else im


def pilula(txt, s, fundo, cor=TINTA, fig=True):
    f = fonte(s, fig)
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    b = d0.textbbox((0, 0), txt, font=f)
    w, h = b[2] - b[0] + s * 1.3, s * 1.75
    im = Image.new("RGBA", (int(w) + 12, int(h) + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((5, 5, w + 5, h + 5), h / 2, fill=fundo, outline=TINTA, width=6)
    d.text((w / 2 + 5, h / 2 + 5), txt, font=f, fill=cor, anchor="mm")
    return adesivo(im, 10)


# ---------------------------------------------------------------- doodles
def estrela_pts(cx, cy, r1, r2, n=5, rot=-90):
    pts = []
    for k in range(n * 2):
        r = r1 if k % 2 == 0 else r2
        a = math.radians(rot + k * 180 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


@lru_cache(None)
def doodle(tipo, s=90, cor=AMAR):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c, lw = s / 2, max(4, s // 16)
    if tipo == "estrela":
        d.polygon(estrela_pts(c, c, s * 0.45, s * 0.22), fill=cor, outline=TINTA, width=lw)
    elif tipo == "coracao":
        r = s * 0.2
        d.ellipse((c - 2 * r, c - 1.6 * r, c, c + 0.4 * r), fill=cor)
        d.ellipse((c, c - 1.6 * r, c + 2 * r, c + 0.4 * r), fill=cor)
        d.polygon([(c - 1.93 * r, c - 0.2 * r), (c + 1.93 * r, c - 0.2 * r), (c, c + 2.1 * r)], fill=cor)
        m = im.getchannel("A").filter(ImageFilter.MaxFilter(lw * 2 + 1))
        o = Image.new("RGBA", im.size, TINTA + (255,))
        o.putalpha(m)
        o.alpha_composite(im)
        im = o
    elif tipo == "flor":
        for k in range(6):
            a = math.radians(k * 60)
            x, y = c + s * 0.24 * math.cos(a), c + s * 0.24 * math.sin(a)
            d.ellipse((x - s * 0.17, y - s * 0.17, x + s * 0.17, y + s * 0.17), fill=cor, outline=TINTA, width=lw)
        d.ellipse((c - s * 0.13, c - s * 0.13, c + s * 0.13, c + s * 0.13), fill=AMAR, outline=TINTA, width=lw)
    elif tipo == "brilho":
        d.polygon(estrela_pts(c, c, s * 0.46, s * 0.12, 4), fill=cor, outline=TINTA, width=lw)
    return im


DOODLES = None


def doodles():
    global DOODLES
    if DOODLES is None:
        rnd = random.Random(7)
        DOODLES = []
        for k in range(26):
            x, y = rnd.uniform(30, W - 30), rnd.uniform(240, H - 60)
            DOODLES.append((rnd.choice(["estrela", "coracao", "flor", "brilho"]),
                            rnd.choice([AMAR, ROSA, LILAS, MENTA, PESS, CEU]), x, y, rnd.uniform(40, 80),
                            rnd.uniform(0, 6.28), rnd.uniform(-20, 20)))
    return DOODLES


@lru_cache(None)
def fundo_base():
    im = Image.new("RGBA", (W, H), ROSA_BG + (255,))
    d = ImageDraw.Draw(im)
    for y in range(0, H, 48):  # bolinhas bem clarinhas
        for x in range((y // 48) % 2 * 24, W, 48):
            d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(250, 214, 222))
    return im


def fundo(t):
    im = fundo_base().copy()
    for tipo, cor, x, y, s, fase, rot in doodles():
        b = 1 + 0.08 * math.sin(t * 2.2 + fase)
        sp = doodle(tipo, int(s), cor).rotate(rot + 6 * math.sin(t * 1.3 + fase), resample=Image.BICUBIC, expand=True)
        sp = sp.resize((int(sp.width * b), int(sp.height * b)), Image.LANCZOS)
        sp.putalpha(sp.getchannel("A").point(lambda v: int(v * 0.55)))
        im.alpha_composite(sp, (int(x - sp.width / 2), int(y - sp.height / 2)))
    return im


def cola(img, sp, x, y, rot=0.0, s=1.0, a=1.0):
    if s <= 0.01 or a <= 0.01:
        return
    if s != 1:
        sp = sp.resize((max(1, int(sp.width * s)), max(1, int(sp.height * s))), Image.LANCZOS)
    if rot:
        sp = sp.rotate(rot, resample=Image.BICUBIC, expand=True)
    if a < 1:
        sp = sp.copy()
        sp.putalpha(sp.getchannel("A").point(lambda v: int(v * a)))
    img.alpha_composite(sp, (int(x - sp.width / 2), int(y - sp.height / 2)))


def pop(img, sp, x, y, t, t0, rot=0.0, s=1.0, wob=True):
    """Adesivo que 'cola' com pulinho e depois balança de leve."""
    u = (t - t0) / 0.35
    if u <= 0:
        return
    k = out_back(u) if u < 1 else 1.0
    r = rot + (2.0 * math.sin((t - t0) * 2.4 + x * 0.01) if wob else 0)
    cola(img, sp, x, y, r, s * k)


# ---------------------------------------------------------------- peças
@lru_cache(None)
def azulejo(cor, s=110):
    fundo_c, tinta, motivo = AZ[cor]
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lw = max(4, s // 18)
    d.rounded_rectangle((2, 2, s - 3, s - 3), s * 0.18, fill=fundo_c, outline=TINTA, width=lw)
    c = s / 2
    if motivo == "flor":
        for k in range(4):
            a = math.radians(45 + k * 90)
            x, y = c + s * 0.17 * math.cos(a), c + s * 0.17 * math.sin(a)
            d.ellipse((x - s * .13, y - s * .13, x + s * .13, y + s * .13), fill=tinta)
        d.ellipse((c - s * .08, c - s * .08, c + s * .08, c + s * .08), fill=AMAR)
    elif motivo == "losango":
        d.polygon([(c, s * .2), (s * .8, c), (c, s * .8), (s * .2, c)], fill=tinta)
        d.polygon([(c, s * .36), (s * .64, c), (c, s * .64), (s * .36, c)], fill=fundo_c)
    elif motivo == "circulo":
        d.ellipse((s * .24, s * .24, s * .76, s * .76), outline=tinta, width=max(5, s // 12))
        d.ellipse((s * .42, s * .42, s * .58, s * .58), fill=tinta)
    elif motivo == "estrela":
        d.polygon(estrela_pts(c, c, s * .32, s * .14, 4, -90), fill=tinta)
        d.polygon(estrela_pts(c, c, s * .2, s * .08, 4, -45), fill=tinta)
    elif motivo == "floco":
        for k in range(3):
            a = math.radians(k * 60)
            dx, dy = s * .3 * math.cos(a), s * .3 * math.sin(a)
            d.line((c - dx, c - dy, c + dx, c + dy), fill=tinta, width=max(5, s // 14))
        d.ellipse((c - s * .07, c - s * .07, c + s * .07, c + s * .07), fill=tinta)
    # brilhinho
    d.arc((s * .14, s * .12, s * .5, s * .48), 190, 250, fill=(255, 255, 255), width=max(3, s // 26))
    return im


@lru_cache(None)
def az_ad(cor, s=110):
    return adesivo(azulejo(cor, s), 7)


@lru_cache(None)
def fabrica(s=300):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((4, 4, s - 5, s - 5), fill=(255, 245, 225), outline=TINTA, width=8)
    d.ellipse((s * .12, s * .12, s * .88, s * .88), outline=(255, 200, 150), width=6)
    return adesivo(im, 10)


def poe_fabrica(img, x, y, cores, t, t0, ts=118, esconde=()):
    pop(img, fabrica(), x, y, t, t0)
    for k, c in enumerate(cores):
        if k in esconde:
            continue
        dx, dy = (k % 2 - 0.5) * ts * 0.95, (k // 2 - 0.5) * ts * 0.95
        pop(img, az_ad(c, ts), x + dx, y + dy, t, t0 + 0.15 + k * 0.06, (k * 7) % 11 - 5)


def pos_fabrica(x, y, k, ts=118):
    return x + (k % 2 - 0.5) * ts * 0.95, y + (k // 2 - 0.5) * ts * 0.95


@lru_cache(None)
def parede(cel=120, marcas=True):
    """Parede 5x5 com os motivos clarinhos (como no tabuleiro)."""
    n = 5
    pad = 22
    s = cel * n + pad * 2
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((3, 3, s - 4, s - 4), 34, fill=(255, 250, 240), outline=TINTA, width=8)
    for r in range(n):
        for c in range(n):
            cor = CORES[(c - r) % 5]
            x, y = pad + c * cel, pad + r * cel
            t = azulejo(cor, cel - 14).copy()
            t.putalpha(t.getchannel("A").point(lambda v: int(v * 0.28)))
            im.alpha_composite(t, (x + 7, y + 7))
    return adesivo(im, 12)


def celula_parede(cx, cy, r, c, cel=120):
    s = cel * 5 + 44
    return cx - s / 2 + 22 + c * cel + cel / 2, cy - s / 2 + 22 + r * cel + cel / 2


def cor_parede(r, c):
    return CORES[(c - r) % 5]


@lru_cache(None)
def linhas_preparo(cel=100):
    """Escadinha 1..5 (alinhada à direita, como no tabuleiro)."""
    w = cel * 5 + 40
    h = cel * 5 + 40
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((3, 3, w - 4, h - 4), 30, fill=(255, 250, 240), outline=TINTA, width=8)
    for r in range(5):
        for k in range(r + 1):
            x = w - 20 - (k + 1) * cel
            y = 20 + r * cel
            d.rounded_rectangle((x + 8, y + 8, x + cel - 8, y + cel - 8), 16, fill=(250, 226, 232), outline=(230, 180, 195),
                                width=4)
    return adesivo(im, 12)


def celula_linha(cx, cy, r, k, cel=100):
    w = cel * 5 + 40
    x0, y0 = cx - (w + 52) / 2 + 26, cy - (w + 52) / 2 + 26
    return x0 + w - 20 - (k + 1) * cel + cel / 2, y0 + 20 + r * cel + cel / 2


@lru_cache(None)
def chao(cel=100):
    vals = ["-1", "-1", "-2", "-2", "-2", "-3", "-3"]
    w = cel * 7 + 40
    h = cel + 80
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((3, 3, w - 4, h - 4), 26, fill=(255, 235, 235), outline=TINTA, width=8)
    for k, v in enumerate(vals):
        x = 20 + k * cel
        d.text((x + cel / 2, 38), v, font=fonte(36), fill=(220, 60, 80), anchor="mm")
        d.rounded_rectangle((x + 8, 64, x + cel - 8, 64 + cel - 16), 14, fill=(245, 215, 220), outline=(230, 170, 185),
                            width=4)
    return adesivo(im, 12)


def celula_chao(cx, cy, k, cel=100):
    w = cel * 7 + 40
    h = cel + 80
    return cx - (w + 52) / 2 + 26 + 20 + k * cel + cel / 2, cy - (h + 52) / 2 + 26 + 64 + (cel - 16) / 2


@lru_cache(None)
def marcador1(s=110):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((3, 3, s - 4, s - 4), 20, fill=BR, outline=TINTA, width=7)
    d.text((s / 2, s / 2 + 2), "1", font=fonte(s * .62), fill=(236, 80, 80), anchor="mm")
    return adesivo(im, 7)


@lru_cache(None)
def caixa():
    """Caixa oficial (Galápagos AZU501) sem o fundo branco."""
    import cv2
    src = os.path.join(ROOT, "assets", "orig", "AZU501_OCC.png")
    im = cv2.imread(src)
    h, w = im.shape[:2]
    claro = (im.min(axis=2) > 236).astype(np.uint8)
    mask = np.zeros((h + 2, w + 2), np.uint8)
    fundo_m = np.zeros((h, w), np.uint8)
    for (x, y) in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        tmp = claro.copy()
        cv2.floodFill(tmp, mask, (x, y), 2)
        fundo_m |= (tmp == 2).astype(np.uint8)
    obj = (1 - fundo_m) * 255
    obj = cv2.erode(obj.astype(np.uint8), np.ones((3, 3), np.uint8))
    obj = cv2.GaussianBlur(obj, (3, 3), 0)
    ys, xs = np.where(obj > 128)
    rgba = np.dstack([im[:, :, ::-1], obj])
    out = Image.fromarray(rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1], "RGBA")
    return out


@lru_cache(None)
def caixa_ad(h=760):
    c = caixa()
    c = c.resize((int(c.width * h / c.height), h), Image.LANCZOS)
    return adesivo(c, 16)


# ---------------------------------------------------------------- relógio
def relogio(seg_rest, s=190, pulsa=0.0):
    im = Image.new("RGBA", (s + 40, s + 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = (s + 40) / 2, 30 + s / 2
    for dx in (-1, 1):  # sininhos
        d.ellipse((cx + dx * s * .32 - 30, 6, cx + dx * s * .32 + 30, 60), fill=ROSA, outline=TINTA, width=6)
    cor = (255, 120, 140) if seg_rest <= 10 else ROSA
    d.ellipse((cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2), fill=cor, outline=TINTA, width=8)
    d.ellipse((cx - s * .38, cy - s * .38, cx + s * .38, cy + s * .38), fill=BR, outline=TINTA, width=5)
    m = max(0, int(math.ceil(seg_rest)))
    d.text((cx, cy + 3), f"{m // 60}:{m % 60:02d}", font=fonte(s * .27), fill=TINTA, anchor="mm")
    sp = adesivo(im, 10)
    if pulsa:
        sp = sp.resize((int(sp.width * (1 + pulsa)), int(sp.height * (1 + pulsa))), Image.LANCZOS)
    return sp


# ---------------------------------------------------------------- roteiro
T0 = 3.0          # começa a explicação (relógio anda)
CENAS = [  # (início, nome)
    (3.0, "objetivo"), (9.0, "fabricas"), (15.5, "pega"), (22.5, "centro"), (28.5, "linha"),
    (35.0, "chao"), (41.0, "parede"), (48.5, "fim"),
]
T1 = 56.0         # fim da explicação
T_COM = 59.0
T_CTA = 63.0
DUR = 69.0


def titulo_cena(img, t, t0, txt, y=330, cor=BR, s=104):
    pop(img, texto(txt, s, cor), W / 2, y, t, t0 + 0.05, -2)


def legenda(img, t, t0, txt, y=1640, s=54):
    pop(img, pilula(txt, s, BR), W / 2, y, t, t0, 1)


def cena_gancho(img, t):
    pop(img, texto("AZUL MINI", 150, (120, 200, 255)), W / 2, 420, t, 0.15, -3)
    pop(img, texto("EXPLICADO EM\n1 MINUTO!", 104, AMAR), W / 2, 640, t, 0.55, 2)
    pop(img, caixa_ad(820), W / 2, 1230, t, 0.9, 4 * math.sin(t * 1.5))
    for k, c in enumerate(["azul", "amarelo", "vermelho", "preto", "turquesa"]):
        ang = t * 0.9 + k * 1.256
        pop(img, az_ad(c, 120), W / 2 + 420 * math.cos(ang), 1230 + 470 * math.sin(ang), t, 1.2 + k * 0.1, k * 13)


def cena_objetivo(img, t, t0):
    titulo_cena(img, t, t0, "OBJETIVO:")
    pop(img, texto("decorar a parede\ndo palácio!", 78, ROSA), W / 2, 500, t, t0 + 0.4, 1)
    cx, cy = W / 2, 1060
    pop(img, parede(), cx, cy, t, t0 + 0.6, 0, wob=False)
    rnd = random.Random(3)
    cel = [(r, c) for r in range(5) for c in range(5)]
    rnd.shuffle(cel)
    for k, (r, c) in enumerate(cel[:14]):
        x, y = celula_parede(cx, cy, r, c)
        pop(img, az_ad(cor_parede(r, c), 102), x, y, t, t0 + 1.0 + k * 0.22, rnd.uniform(-4, 4), wob=False)
    legenda(img, t, t0 + 3.6, "quem fizer mais pontos vence!")


FAB = [("azul", "azul", "amarelo", "preto"), ("vermelho", "turquesa", "turquesa", "amarelo"),
       ("preto", "azul", "vermelho", "vermelho"), ("amarelo", "amarelo", "turquesa", "azul"),
       ("turquesa", "preto", "preto", "vermelho")]
FAB_POS = [(280, 700), (800, 700), (540, 1020), (280, 1340), (800, 1340)]


def cena_fabricas(img, t, t0):
    titulo_cena(img, t, t0, "NA MESA:")
    for k, (x, y) in enumerate(FAB_POS):
        poe_fabrica(img, x, y, FAB[k], t, t0 + 0.4 + k * 0.35)
    legenda(img, t, t0 + 2.6, "fábricas com 4 azulejos cada")


def cena_pega(img, t, t0):
    titulo_cena(img, t, t0, "NA SUA VEZ:")
    pop(img, texto("pega TODOS de\nUMA cor de uma fábrica", 66, AMAR), W / 2, 500, t, t0 + 0.3, 1)
    fx, fy = W / 2, 880
    cores = FAB[0]
    u_pega = ease((t - (t0 + 2.0)) / 0.7)
    u_resto = ease((t - (t0 + 3.4)) / 0.8)
    esconde = (0, 1, 2, 3) if t > t0 + 2.0 else ()
    pop(img, fabrica(), fx, fy, t, t0 + 0.2)
    if not esconde:
        poe_fabrica(img, fx, fy, cores, t, t0 + 0.2)
    else:
        for k in (0, 1):  # os 2 azuis vão pra mão
            x0, y0 = pos_fabrica(fx, fy, k)
            x1, y1 = 420 + k * 120, 1250
            cola(img, az_ad("azul", 100), x0 + (x1 - x0) * u_pega, y0 + (y1 - y0) * u_pega - 120 * math.sin(math.pi * u_pega),
                 -6 + k * 10)
        for j, k in enumerate((2, 3)):  # o resto pro centro
            x0, y0 = pos_fabrica(fx, fy, k)
            x1, y1 = 470 + j * 140, 1480
            cola(img, az_ad(cores[k], 100), x0 + (x1 - x0) * u_resto, y0 + (y1 - y0) * u_resto, 5 - j * 10)
    if t > t0 + 2.0:
        pop(img, pilula("SEUS!", 40, CEU), 780, 1250, t, t0 + 2.6, -4)
    if t > t0 + 3.4:
        pop(img, pilula("o resto vai pro CENTRO", 40, PESS), W / 2, 1610, t, t0 + 3.9, 2)


def cena_centro(img, t, t0):
    titulo_cena(img, t, t0, "OU PEGA\nDO CENTRO!", s=86, y=380)
    cx, cy = W / 2, 930
    m = Image.new("RGBA", (560, 380), (0, 0, 0, 0))
    ImageDraw.Draw(m).ellipse((4, 4, 555, 375), fill=(255, 245, 225), outline=TINTA, width=8)
    pop(img, adesivo(m, 10), cx, cy, t, t0 + 0.3, wob=False)
    pts = [("amarelo", -150, -60), ("preto", -40, -90), ("vermelho", 80, -60), ("vermelho", 170, 30),
           ("turquesa", -120, 60), ("amarelo", 10, 70)]
    for k, (c, dx, dy) in enumerate(pts):
        pop(img, az_ad(c, 100), cx + dx, cy + dy, t, t0 + 0.5 + k * 0.08, k * 9 - 20)
    # o marcador 1 sai do centro pro jogador
    u = ease((t - (t0 + 2.4)) / 0.8)
    x = cx + 180 * (1 - u) + 820 * u - 820 * 0 if False else cx + 200 - 0 * u
    mx, my = cx - 230 + 0 * u, cy - 70
    tx, ty = 820, 1330
    pop(img, marcador1(), mx + (tx - mx) * u, my + (ty - my) * u - 150 * math.sin(math.pi * u), t, t0 + 0.9,
        -8 + 16 * u)
    pop(img, texto("o 1º a pegar do centro\nleva o marcador 1:", 52, BR, fig=False), 400, 1330, t, t0 + 2.6, -2)
    legenda(img, t, t0 + 3.4, "joga primeiro, mas perde 1 ponto")


def cena_linha(img, t, t0):
    titulo_cena(img, t, t0, "COLOCA NUMA\nLINHA!", y=380)
    cx, cy = W / 2, 980
    pop(img, linhas_preparo(), cx, cy, t, t0 + 0.3, wob=False)
    # 3 azuis entram na linha 3
    for k in range(3):
        x1, y1 = celula_linha(cx, cy, 2, k)
        u = ease((t - (t0 + 1.2 + k * 0.35)) / 0.5)
        if u > 0:
            cola(img, az_ad("azul", 92), x1, y1 - 400 * (1 - u), 0, 1, min(1, u * 3))
    # linha 1 com um vermelho, linha 2 com amarelo
    for (r, k, c, dt) in [(0, 0, "vermelho", 0.6), (1, 0, "amarelo", 0.8)]:
        x1, y1 = celula_linha(cx, cy, r, k)
        pop(img, az_ad(c, 92), x1, y1, t, t0 + dt, wob=False)
    pop(img, pilula("linha 3 = 3 azulejos", 46, CEU), W / 2, 1440, t, t0 + 2.6, -2)
    legenda(img, t, t0 + 3.4, "cada linha aceita UMA cor só")


def cena_chao(img, t, t0):
    titulo_cena(img, t, t0, "SOBROU?", cor=(255, 120, 140), s=110)
    pop(img, texto("cai no CHÃO!", 80, AMAR), W / 2, 520, t, t0 + 0.4, 2)
    cx, cy = W / 2, 1180
    pop(img, chao(), cx, cy, t, t0 + 0.6, wob=False)
    for k in range(3):
        x1, y1 = celula_chao(cx, cy, k)
        u = (t - (t0 + 1.3 + k * 0.4)) / 0.55
        if u > 0:
            uu = min(1, u)
            y = 760 + (y1 - 760) * uu * uu
            rot = (1 - uu) * 200 * (1 if k % 2 else -1)
            cola(img, az_ad(["vermelho", "vermelho", "preto"][k], 88), x1, y, rot)
    pop(img, texto("-4 PONTOS!", 110, (255, 120, 140)), W / 2, 1420, t, t0 + 2.9, -3)
    legenda(img, t, t0 + 3.4, "cada um que cai tira pontos", y=1620)


def cena_parede(img, t, t0):
    titulo_cena(img, t, t0, "FIM DA RODADA:", s=96)
    pop(img, texto("linha cheia = 1 azulejo\nvai pra parede", 64, AMAR), W / 2, 500, t, t0 + 0.3, 1)
    cx, cy = W / 2, 1060
    pop(img, parede(), cx, cy, t, t0 + 0.5, wob=False)
    ja = [(2, 0), (2, 1), (1, 2), (3, 2)]
    for k, (r, c) in enumerate(ja):
        x, y = celula_parede(cx, cy, r, c)
        pop(img, az_ad(cor_parede(r, c), 102), x, y, t, t0 + 0.7 + k * 0.1, wob=False)
    r, c = 2, 2
    x1, y1 = celula_parede(cx, cy, r, c)
    u = ease((t - (t0 + 1.8)) / 0.7)
    if u > 0:
        cola(img, az_ad(cor_parede(r, c), 102), x1, y1 - 520 * (1 - u), 0, 1 + 0.4 * (1 - u))
    if t > t0 + 2.6:
        # brilhos nos vizinhos
        for (rr, cc) in ja + [(2, 2)]:
            x, y = celula_parede(cx, cy, rr, cc)
            b = 0.5 + 0.5 * math.sin((t - t0) * 9 + rr + cc)
            cola(img, doodle("brilho", 60, AMAR), x + 42, y - 42, 0, 0.6 + 0.4 * b)
        pop(img, texto("+6", 120, AMAR), cx + 330, cy - 310, t, t0 + 2.9, 8)
    legenda(img, t, t0 + 3.4, "pontua pelos azulejos ligados a ele")


def cena_fim(img, t, t0):
    titulo_cena(img, t, t0, "ACABA QUANDO...", s=100)
    pop(img, texto("alguém completa uma\nlinha da parede!", 66, AMAR), W / 2, 500, t, t0 + 0.4, -1)
    for k, (txt, pts, cor) in enumerate([("LINHA", "+2", CEU), ("COLUNA", "+7", MENTA), ("5 DE UMA COR", "+10", ROSA)]):
        y = 820 + k * 250
        pop(img, pilula(txt, 52, cor, fig=False), W / 2 - 130, y, t, t0 + 1.2 + k * 0.6, -3 + k * 3)
        pop(img, texto(pts, 110, AMAR), W / 2 + 290, y, t, t0 + 1.4 + k * 0.6, 6)
    pop(img, texto("MAIS PONTOS VENCE!", 84, (120, 200, 255)), W / 2, 1600, t, t0 + 3.6, -2)


FUNCS = {"objetivo": cena_objetivo, "fabricas": cena_fabricas, "pega": cena_pega, "centro": cena_centro,
         "linha": cena_linha, "chao": cena_chao, "parede": cena_parede, "fim": cena_fim}


def cena_carimbo(img, t):
    u = t - T1
    s = 1.6 - 0.6 * out_back(min(1, u / 0.3)) if u < 0.3 else 1.0
    pop(img, texto("EXPLICADO EM\n%d SEGUNDOS!" % round(T1 - T0), 110, AMAR), W / 2, 900, t, T1, -6, s)
    for k in range(10):
        a = k * 0.628 + u * 0.8
        pop(img, doodle(["estrela", "coracao", "brilho"][k % 3], 90, [AMAR, ROSA, MENTA, CEU][k % 4]),
            W / 2 + 430 * math.cos(a), 900 + 430 * math.sin(a), t, T1 + 0.2 + k * 0.05)


def cena_comenta(img, t):
    pop(img, texto("E AÍ?", 140, AMAR), W / 2, 520, t, T_COM, -3)
    pop(img, texto("você seria o que\nderruba tudo no chão?", 70, BR), W / 2, 820, t, T_COM + 0.4, 2)
    pop(img, pilula("Comenta aqui! 💬".replace(" 💬", ""), 60, ROSA), W / 2, 1080, t, T_COM + 0.9, -2)
    for k, c in enumerate(["vermelho", "preto", "amarelo"]):
        y = 1300 + 60 * (k % 2)
        pop(img, az_ad(c, 130), 300 + k * 240, y + 20 * math.sin(t * 3 + k), t, T_COM + 1.2 + k * 0.15, k * 20 - 20)


def cena_cta(img, t):
    pop(img, K.logo(240), W / 2, 260, t, T_CTA, 0, wob=False)
    pop(img, texto("ALUGUE O\nAZUL MINI", 104, (120, 200, 255)), W / 2, 520, t, T_CTA + 0.2, -2)
    pop(img, caixa_ad(620), W / 2, 1020, t, T_CTA + 0.4, 3)
    pop(img, pilula("2 a 4 jogadores · 8+", 44, MENTA), W / 2, 1400, t, T_CTA + 0.7, -2)
    pop(img, pilula("RETIRE EM MAUÁ OU RECEBA EM CASA", 38, AMAR, fig=False), W / 2, 1510, t, T_CTA + 0.9, 1)
    pop(img, pilula("LINK NA BIO · @SUAVEZ_BG", 44, ROSA, fig=False), W / 2, 1620, t, T_CTA + 1.1, -1)


def quadro(t):
    img = fundo(t)
    if t < T0:
        cena_gancho(img, t)
    elif t < T1:
        nome, t0 = None, 0
        for ti, n in CENAS:
            if t >= ti:
                nome, t0 = n, ti
        FUNCS[nome](img, t, t0)
    elif t < T_COM:
        cena_carimbo(img, t)
    elif t < T_CTA:
        cena_comenta(img, t)
    else:
        cena_cta(img, t)
    # relógio
    if T0 - 0.4 < t < T1 + 2.6:
        rest = max(0.0, 60 - (min(t, T1) - T0))
        pul = 0.06 * abs(math.sin(t * 6)) if (60 - (t - T0)) <= 10 and t < T1 else 0
        pop(img, relogio(rest, pulsa=pul), 150, 150, t, T0 - 0.4, -4)
    if t < T_CTA:
        cola(img, K.logo(150), W - 110, 95)
    # flash de troca de cena
    for tb in [T0] + [c[0] for c in CENAS[1:]] + [T1, T_COM, T_CTA]:
        dd = t - tb
        if 0 <= dd < 0.1:
            img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(160 * (1 - dd / 0.1)))))
    return img.convert("RGB")


def render(fi):
    return quadro(fi / FPS).tobytes()


def audio():
    ev = [(0.15, S.estouro(), 0.5), (0.55, S.estouro(), 0.5), (0.9, S.plim(), 0.4)]
    for ti, _ in CENAS:
        ev += [(ti, S.sopro(0.35), 0.35), (ti + 0.05, S.plim(), 0.35)]
    ev += [(c, S.tic(k % 2 == 0), 0.3) for k, c in enumerate(np.arange(T0, T1, 1.0))]
    ev += [(T1, S.estouro(), 0.6), (T1 + 0.05, S.sino(), 0.5), (T_COM, S.plim(), 0.45), (T_CTA, S.carta_vira(), 0.5)]
    mus = S.musica_marimba_pop(DUR + 0.5)
    com = os.path.join(K.OUT, "azul_com.wav")
    sem = os.path.join(K.OUT, "azul_sem.wav")
    S.grava(com, DUR, ev, mus, musica_ganho=0.42, fx_ganho=0.7)
    S.grava(sem, DUR, ev, None, fx_ganho=0.7)
    return com, sem


def main():
    os.makedirs(K.OUT, exist_ok=True)
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:]]
        K.folha([quadro(x) for x in ts], os.path.join(K.OUT, "frames_azul.jpg"))
        return
    com, sem = audio()
    K.entrega("azul", DUR, render, com, sem)
    print("ok", DUR)


if __name__ == "__main__":
    main()
