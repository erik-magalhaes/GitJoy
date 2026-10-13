"""Identidade visual das artes da Sua Vez! passada pela Jéssica (13/out/2026), usada nas peças das ASSINATURAS:
Lilita One (títulos) + Figtree (texto); marrom #3F2412 (texto, contornos e sombra sólida), azul-petróleo #1C7C96
(Família), laranja #F48825 (Pocket), fundo azul-claro #E3F3F6, amarelo #FFC71F, branco #FAFAFA; contornos grossos
marrons, sombra sólida deslocada, elementos levemente girados, selos em pílula, cara de tabuleiro/peças; logo numa
caixa branca com contorno.
"""
import math
import os
import random
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
FT = os.path.join(ROOT, "assets", "fonts")
LOGO = os.path.join(REPO, "voodoo-reels", "assets", "logo_suavez.png")

MARROM = (63, 36, 18)
PETROLEO = (28, 124, 150)
LARANJA = (244, 136, 37)
FUNDO = (227, 243, 246)
AMARELO = (255, 199, 31)
BRANCO = (250, 250, 250)
PRATA = (205, 214, 219)
CAT = {  # categoria → (cor do selo, cor do texto)
    "POCKET": (LARANJA, BRANCO),
    "FAMÍLIA": (PETROLEO, BRANCO),
    "ESTRATÉGICO": (MARROM, BRANCO),
    "DELUXE": (AMARELO, MARROM),
}
PLANOS = [  # (nome, preço, jogos por vez, categorias, cor do cartão, cor do título, observação)
    ("SILVER", 49, 1, ["POCKET", "FAMÍLIA"], PRATA, MARROM, None),
    ("GOLD", 89, 2, ["POCKET", "FAMÍLIA", "ESTRATÉGICO"], AMARELO, MARROM, None),
    ("PLATINUM", 139, 3, ["POCKET", "FAMÍLIA", "ESTRATÉGICO", "DELUXE"], PETROLEO, BRANCO, "máx. 1 Deluxe por vez"),
]
# caixas OFICIAIS que já estão no projeto, por categoria (preço do site: 15/30/45/60)
_R = lambda *p: os.path.join(REPO, *p)  # noqa: E731
JOGOS = {
    "POCKET": [_R("roleta-reels/assets/the_mind.png"), _R("feed-posts/assets/jungo.png"),
               _R("roleta-reels/assets/happy_salmon.png"), _R("roleta-reels/assets/splito.png")],
    "FAMÍLIA": [_R("gravados-reels/assets/lista/ticket_to_ride.png"), _R("gravados-reels/assets/lista/harmonies.png"),
                _R("gravados-reels/assets/lista/king_of_tokyo.png"), _R("gravados-reels/assets/lista/dixit.png")],
    "ESTRATÉGICO": [_R("feed-posts/assets/mind_mgmt.png"), _R("feed-posts/assets/dinosaur_world.png"),
                    _R("roleta-reels/assets/rebirth.png")],
    "DELUXE": [_R("halloween-reels/assets/finalgirl.png"), _R("feed-posts/assets/wonderland.png")],
}


@lru_cache(None)
def fonte(nome, s, peso=None):
    f = ImageFont.truetype(os.path.join(FT, nome), int(s))
    if peso:
        f.set_variation_by_axes([peso])
    return f


def lilita(s):
    return fonte("LilitaOne.ttf", s)


def fig(s, peso=700):
    return fonte("Figtree.ttf", s, peso)


def _larg(txt, f):
    return ImageDraw.Draw(Image.new("L", (1, 1))).textlength(txt, font=f)


@lru_cache(None)
def titulo(txt, s, cor=BRANCO, contorno=MARROM, sw=None, sombra=None, larg_max=None):
    """Título em Lilita One com contorno marrom grosso e sombra sólida deslocada (várias linhas com \\n)."""
    linhas = txt.split("\n")
    while larg_max and max(_larg(l, lilita(s)) for l in linhas) > larg_max and s > 20:
        s -= 2
    f = lilita(s)
    sw = sw if sw is not None else max(3, int(s * 0.09))
    sombra = sombra if sombra is not None else max(4, int(s * 0.07))
    lh = s * 1.02
    w = int(max(_larg(l, f) for l in linhas) + 2 * sw + sombra + 20)
    h = int(lh * len(linhas) + 2 * sw + sombra + s * 0.3)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k, l in enumerate(linhas):
        y = sw + 10 + lh * k + s * 0.5
        if sombra:
            d.text((w / 2 - sombra / 2 + sombra, y + sombra), l, font=f, fill=contorno, anchor="mm", stroke_width=sw,
                   stroke_fill=contorno)
        d.text((w / 2 - sombra / 2, y), l, font=f, fill=cor, anchor="mm", stroke_width=sw, stroke_fill=contorno)
    return im


@lru_cache(None)
def texto(txt, s, cor=MARROM, peso=700, larg_max=None, entre=1.25, alinha="mm"):
    """Texto corrido em Figtree, quebrando linha em larg_max."""
    f = fig(s, peso)
    linhas = []
    for par in txt.split("\n"):
        atual = ""
        for p in par.split(" "):
            t = (atual + " " + p).strip()
            if larg_max and _larg(t, f) > larg_max and atual:
                linhas.append(atual)
                atual = p
            else:
                atual = t
        linhas.append(atual)
    lh = s * entre
    w = int(max(_larg(l, f) for l in linhas) + 10)
    im = Image.new("RGBA", (w, int(lh * len(linhas) + s * 0.4)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k, l in enumerate(linhas):
        x = w / 2 if alinha == "mm" else 5
        d.text((x, lh * k + lh / 2 + s * 0.15), l, font=f, fill=cor, anchor=alinha)
    return im


def bloco(w, h, cor, raio=36, ow=7, sombra=12, contorno=MARROM):
    """Retângulo arredondado com contorno marrom grosso e sombra sólida deslocada."""
    im = Image.new("RGBA", (w + sombra + 2, h + sombra + 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if sombra:
        d.rounded_rectangle((sombra, sombra, sombra + w, sombra + h), radius=raio, fill=contorno)
    d.rounded_rectangle((0, 0, w, h), radius=raio, fill=cor, outline=contorno, width=ow)
    return im


@lru_cache(None)
def pilula(txt, s, cor=AMARELO, cor_txt=MARROM, peso=900, pad=(30, 14), ow=5, sombra=7, fonte_titulo=False):
    f = lilita(s) if fonte_titulo else fig(s, peso)
    tw = _larg(txt, f)
    w, h = int(tw + 2 * pad[0]), int(s * 1.15 + 2 * pad[1])
    im = bloco(w, h, cor, raio=h // 2, ow=ow, sombra=sombra)
    ImageDraw.Draw(im).text((w / 2, h / 2 + (2 if fonte_titulo else 0)), txt, font=f, fill=cor_txt, anchor="mm")
    return im


@lru_cache(None)
def logo(w):
    lg = Image.open(LOGO).convert("RGBA")
    lw = int(w - 50)
    lg = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS)
    im = bloco(lg.width + 50, lg.height + 36, BRANCO, raio=28, ow=6, sombra=9)
    im.alpha_composite(lg, (25, 18))
    return im


@lru_cache(None)
def jogo(path, h, larg=None):
    """Caixa OFICIAL com sombra sólida marrom suave."""
    im = Image.open(path).convert("RGBA")
    im = im.crop(im.getbbox())
    s = h / im.height
    if larg and im.width * s > larg:
        s = larg / im.width
    im = im.resize((max(2, int(im.width * s)), max(2, int(im.height * s))), Image.LANCZOS)
    o = max(5, int(im.height * 0.035))
    out = Image.new("RGBA", (im.width + o, im.height + o), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, MARROM + (255,))
    sh.putalpha(im.getchannel("A").point(lambda v: int(v * 0.85)))
    out.alpha_composite(sh, (o, o))
    out.alpha_composite(im)
    return out


@lru_cache(None)
def dado(s, face, cor=BRANCO, pip=MARROM):
    """Dado com contorno marrom e sombra sólida (peça de jogo)."""
    im = bloco(s, s, cor, raio=s // 5, ow=max(4, s // 16), sombra=max(4, s // 12))
    d = ImageDraw.Draw(im)
    pos = {1: [(.5, .5)], 2: [(.28, .28), (.72, .72)], 3: [(.26, .26), (.5, .5), (.74, .74)],
           4: [(.28, .28), (.72, .28), (.28, .72), (.72, .72)],
           5: [(.26, .26), (.74, .26), (.5, .5), (.26, .74), (.74, .74)],
           6: [(.28, .22), (.72, .22), (.28, .5), (.72, .5), (.28, .78), (.72, .78)]}[face]
    r = s * 0.085
    for x, y in pos:
        d.ellipse((x * s - r, y * s - r, x * s + r, y * s + r), fill=pip)
    return im


@lru_cache(None)
def peao(h, cor):
    """Peão clássico de tabuleiro (bola + corpo), geométrico, com contorno e sombra sólida."""
    w = int(h * 0.62)
    o = max(4, h // 18)
    im = Image.new("RGBA", (w + o + 4, h + o + 4), (0, 0, 0, 0))
    for dx, c, fill in ((o, MARROM, MARROM), (0, MARROM, cor)):
        d = ImageDraw.Draw(im)
        ow = max(4, h // 22)
        cx = w / 2 + dx
        top = dx
        d.polygon([(cx - w * 0.2, top + h * 0.38), (cx + w * 0.2, top + h * 0.38), (cx + w * 0.42, top + h * 0.86),
                   (cx - w * 0.42, top + h * 0.86)], fill=fill, outline=c, width=ow)
        d.rounded_rectangle((cx - w * 0.48, top + h * 0.8, cx + w * 0.48, top + h * 0.97), radius=int(h * 0.06), fill=fill,
                            outline=c, width=ow)
        d.ellipse((cx - w * 0.3, top + h * 0.02, cx + w * 0.3, top + h * 0.42), fill=fill, outline=c, width=ow)
    return im


def fundo(W, H, semente=1):
    """Azul-claro com trilha de tabuleiro (casas) nas bordas e pontilhado leve."""
    img = Image.new("RGBA", (W, H), FUNDO + (255,))
    d = ImageDraw.Draw(img)
    rnd = random.Random(semente)
    for y in range(40, H, 70):  # pontilhado de mesa
        for x in range(40 + (35 if (y // 70) % 2 else 0), W, 70):
            d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(206, 232, 238))
    casa = 92
    cores = [(255, 255, 255), (206, 232, 238)]
    k = 0
    for x in range(-20, W + casa, casa + 10):  # trilha em cima e embaixo
        for y in (-40, H - casa + 40):
            d.rounded_rectangle((x, y, x + casa, y + casa), radius=18, fill=cores[k % 2], outline=(190, 222, 230), width=4)
            k += 1
    del rnd
    return img


def cola(img, im, cx, cy, rot=0.0, esc=1.0, alpha=1.0):
    if esc <= 0.01 or alpha <= 0.01:
        return
    if abs(esc - 1) > 0.003:
        im = im.resize((max(2, int(im.width * esc)), max(2, int(im.height * esc))), Image.BICUBIC)
    if abs(rot) > 0.05:
        im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    if alpha < 0.999:
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    img.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def selos_categoria(cats, s=34, gap=14, larg_max=None):
    """Fileira de selos das categorias (quebra em 2 linhas se não couber)."""
    ims = [pilula(c, s, CAT[c][0], CAT[c][1], pad=(24, 10), ow=4, sombra=6) for c in cats]
    linhas, atual, lw = [], [], 0
    for im in ims:
        if larg_max and atual and lw + im.width + gap > larg_max:
            linhas.append(atual)
            atual, lw = [], 0
        atual.append(im)
        lw += im.width + gap
    linhas.append(atual)
    W = max(sum(i.width for i in l) + gap * (len(l) - 1) for l in linhas)
    hl = ims[0].height
    out = Image.new("RGBA", (W, hl * len(linhas) + gap * (len(linhas) - 1)), (0, 0, 0, 0))
    for k, l in enumerate(linhas):
        x = (W - (sum(i.width for i in l) + gap * (len(l) - 1))) // 2
        for im in l:
            out.alpha_composite(im, (x, k * (hl + gap)))
            x += im.width + gap
    return out


def leque(paths, h, passo=0.62, ang=7):
    """Caixas em leque (a do meio por cima)."""
    ims = [jogo(p, h, int(h * 0.95)) for p in paths]
    n = len(ims)
    larg = int(sum(i.width for i in ims) * passo + ims[-1].width * (1 - passo) + 80)
    out = Image.new("RGBA", (larg, int(h * 1.3)), (0, 0, 0, 0))
    ordem = sorted(range(n), key=lambda k: -abs(k - (n - 1) / 2))
    xs, x = [], 40
    for im in ims:
        xs.append(x)
        x += im.width * passo
    for k in ordem:
        a = (k - (n - 1) / 2) * ang
        r = ims[k].rotate(-a, expand=True, resample=Image.BICUBIC)
        y = int(out.height / 2 - r.height / 2 + abs(k - (n - 1) / 2) * h * 0.06)
        out.alpha_composite(r, (int(xs[k] + ims[k].width / 2 - r.width / 2), max(0, y)))
    return out


def brl(v):
    return f"R$ {v}"


def onda(t, f=1.0, a=1.0):
    return a * math.sin(t * f)
