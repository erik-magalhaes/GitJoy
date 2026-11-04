#!/usr/bin/env python3
"""2ª opção do convite da TARDE DE JOGOS NO BECAS (4/nov/2026), da 4ª referência que ele mandou: "GAME NIGHT" com
LETRAS DE MADEIRA tipo Scrabble (cada uma com o numerozinho de pontos), papel envelhecido com bolinhas vermelhas,
cartas de baralho espalhadas na borda, dados e uma pilha de caixas no canto, e o texto em letra de pixel (Silkscreen).
As cartas e os dados são desenhados em formas simples; as caixas são as do acervo (recortes do site).

    /usr/bin/python3 letrinhas.py    # out/letrinhas/post_1080x1350.png, story_1080x1920.png, folha.jpg
"""
import math
import os
import random
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import kit as K
import estilos as ST
from kit import TB

OUT = os.path.join(K.OUT, "letrinhas")
FD = os.path.join(K.REPO, "comum", "fontes")
PAPEL = (236, 214, 170)
VERMELHO = (196, 40, 44)
TINTA = (24, 20, 18)
PONTOS = {"T": 1, "A": 1, "R": 1, "D": 2, "E": 1, "J": 8, "O": 1, "G": 2, "S": 1, "!": 0}


@lru_cache(None)
def F(nome, s):
    return ImageFont.truetype(os.path.join(FD, nome), int(s))


def ruido(w, h, escala, seed):
    rng = np.random.default_rng(seed)
    a = rng.random((h // escala + 2, w // escala + 2))
    return np.asarray(Image.fromarray((a * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255


def papel(W, H):
    base = np.array(PAPEL, np.float32)[None, None, :] * np.ones((H, W, 1), np.float32)
    n = (ruido(W, H, 120, 1) - 0.5) * 40 + (ruido(W, H, 8, 2) - 0.5) * 16
    yy, xx = np.mgrid[0:H, 0:W]
    borda = np.clip(1 - ((xx - W / 2) / (W * 0.62)) ** 2 - ((yy - H / 2) / (H * 0.62)) ** 2, 0, 1)
    a = base + n[..., None] - (1 - borda[..., None]) * np.array([40, 50, 60])  # cantos queimados
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(img)
    passo = 150
    for j, y in enumerate(range(40, H, passo // 2)):  # bolinhas vermelhas em quincôncio
        for x in range(40 + (passo // 2 if j % 2 else 0), W, passo):
            d.ellipse((x - 17, y - 17, x + 17, y + 17), fill=VERMELHO)
    return img


@lru_cache(None)
def peca(letra, tam=170, seed=0):
    """Letra de madeira: madeira clara com veio, cantos levemente gastos, letra preta e o número de pontos."""
    rnd = random.Random(seed)
    tons = [(224, 196, 150), (210, 176, 128), (236, 218, 178), (196, 160, 112), (240, 150, 80)]
    base = np.array(tons[rnd.randrange(len(tons))], np.float32)
    w = h = tam
    y = np.arange(h)[:, None]
    x = np.arange(w)[None, :]
    n = ruido(w, h, 30, seed + 9)
    veio = np.sin((y * 0.12 + n * 6 + rnd.uniform(0, 6)) * 1.0) * 0.5 + 0.5
    a = base[None, None, :] + (veio[..., None] - 0.5) * 26 + (ruido(w, h, 3, seed + 3)[..., None] - 0.5) * 14
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), int(tam * 0.08), fill=255)
    im.putalpha(m)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((3, 3, w - 4, h - 4), int(tam * 0.08), outline=(150, 112, 70, 160), width=4)
    f = F("ArchivoBlack-Regular.ttf", int(tam * 0.62))
    d.text((w * 0.47, h * 0.48), letra, font=f, fill=TINTA, anchor="mm")
    p = PONTOS.get(letra, 1)
    if p:
        d.text((w * 0.84, h * 0.84), str(p), font=F("ArchivoBlack-Regular.ttf", int(tam * 0.18)), fill=TINTA,
               anchor="mm")
    sh = Image.new("RGBA", (w + 30, h + 30), (0, 0, 0, 0))
    sh.paste((60, 30, 20, 140), (10, 14), m)
    sh = sh.filter(ImageFilter.GaussianBlur(5))
    sh.alpha_composite(im, (4, 4))
    return sh.rotate(rnd.uniform(-7, 7), expand=True, resample=Image.BICUBIC)


def palavra(img, txt, cx, cy, tam, seed=0, espaco=0.08):
    n = len(txt)
    passo = tam * (1 + espaco)
    x = cx - passo * (n - 1) / 2
    rnd = random.Random(seed)
    for k, ch in enumerate(txt):
        p = peca(ch, tam, seed * 20 + k)
        img.alpha_composite(p, (int(x - p.width / 2), int(cy - p.height / 2 + rnd.uniform(-10, 10))))
        x += passo


NAIPES = ["♠", "♥", "♣", "♦"]


@lru_cache(None)
def carta(valor, naipe, h=320):
    w = int(h * 0.7)
    cor = VERMELHO if naipe in "♥♦" else TINTA
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), int(h * 0.06), fill=(250, 248, 242), outline=(170, 170, 170), width=2)
    fv = F("ArchivoBlack-Regular.ttf", int(h * 0.11))
    fn = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(h * 0.1))
    fg = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(h * 0.36))
    d.text((h * 0.07, h * 0.04), valor, font=fv, fill=cor)
    d.text((h * 0.075, h * 0.17), naipe, font=fn, fill=cor)
    d.text((w / 2, h / 2), naipe, font=fg, fill=cor, anchor="mm")
    sh = Image.new("RGBA", (w + 30, h + 30), (0, 0, 0, 0))
    sh.paste((40, 20, 10, 110), (10, 12), im.getchannel("A"))
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    sh.alpha_composite(im, (4, 4))
    return sh


def cartas_borda(img, W, H, seed, y_ini):
    """Cartas espalhadas no pé e na lateral esquerda (como na referência)."""
    rnd = random.Random(seed)
    vals = ["A", "7", "8", "10", "J", "Q", "K", "2", "3", "9"]
    pos = [(x, y_ini + rnd.uniform(-40, 90)) for x in range(-40, W + 120, 170)]
    pos += [(rnd.uniform(-90, -10), y) for y in range(int(y_ini * 0.35), int(y_ini), 260)]
    for k, (x, y) in enumerate(pos):
        c = carta(rnd.choice(vals), NAIPES[k % 4], rnd.choice([300, 330, 360]))
        c = c.rotate(rnd.uniform(-35, 35), expand=True, resample=Image.BICUBIC)
        img.alpha_composite(c, (int(x - c.width / 2), int(y)))


def dado_simples(s, n, seed):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((3, 3, s - 4, s - 4), int(s * 0.18), fill=(240, 226, 204), outline=(120, 80, 60), width=4)
    P = {5: [(.27, .27), (.73, .27), (.5, .5), (.27, .73), (.73, .73)], 3: [(.27, .27), (.5, .5), (.73, .73)],
         6: [(.27, .25), (.73, .25), (.27, .5), (.73, .5), (.27, .75), (.73, .75)]}[n]
    for px, py in P:
        r = s * 0.08
        d.ellipse((px * s - r, py * s - r, px * s + r, py * s + r), fill=VERMELHO)
    sh = Image.new("RGBA", (s + 24, s + 24), (0, 0, 0, 0))
    sh.paste((40, 20, 10, 120), (8, 12), im.getchannel("A"))
    sh = sh.filter(ImageFilter.GaussianBlur(5))
    sh.alpha_composite(im, (2, 2))
    return sh.rotate(random.Random(seed).uniform(-30, 30), expand=True, resample=Image.BICUBIC)


@lru_cache(None)
def caixa(nome, h):
    cx = Image.open(os.path.join(K.REPO, "hobby-reels", "assets", "acervo", nome + ".png")).convert("RGBA")
    cx = cx.crop(cx.getbbox())
    cx = cx.resize((int(cx.width * h / cx.height), h), Image.LANCZOS)
    sh = Image.new("RGBA", (cx.width + 30, cx.height + 30), (0, 0, 0, 0))
    sh.paste((40, 20, 10, 130), (10, 14), cx.getchannel("A"))
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    sh.alpha_composite(cx, (4, 4))
    return sh


def cantos(img, W, H):
    for k, (nome, x, y, r) in enumerate((("dixit", W - 190, 170, -8), ("hitster", W - 330, 210, 10),
                                          ("telma", W - 150, 330, 6))):
        c = caixa(nome, 230).rotate(r, expand=True, resample=Image.BICUBIC)
        img.alpha_composite(c, (int(x - c.width / 2), int(y - c.height / 2)))
    for k, (x, y, n) in enumerate(((150, 150, 5), (290, 250, 3), (130, 330, 6))):
        dd = dado_simples(110, n, k)
        img.alpha_composite(dd, (int(x - dd.width / 2), int(y - dd.height / 2)))


def texto_pixel(img, linhas, cx, y, s, entre=1.5):
    d = ImageDraw.Draw(img)
    for li, (txt, cor) in enumerate(linhas):
        f = F("Silkscreen-Bold.ttf", s)
        while d.textlength(txt, font=f) > img.width - 120 and f.size > 20:
            f = F("Silkscreen-Bold.ttf", f.size - 2)
        d.text((cx + 3, y + 3), txt, font=f, fill=(250, 240, 220), anchor="mt")
        d.text((cx, y), txt, font=f, fill=cor, anchor="mt")
        y += s * entre
    return y


INFO = [("NO BECAS CAFÉ · DATA EM BREVE", TINTA), ("R$ 30 (R$ 15 VIRAM CAFÉ)", VERMELHO),
        ("A GENTE ENSINA TODOS OS JOGOS", TINTA), ("RESERVE: (11) 97793-3910", VERMELHO)]


def post():
    W, H = 1080, 1350
    img = papel(W, H)
    cantos(img, W, H)
    lg = K.logo(140)
    img.alpha_composite(lg, (int(W / 2 - lg.width / 2), 60))
    palavra(img, "TARDE", W / 2, 520, 168, 1)
    palavra(img, "DE", W / 2, 700, 150, 2)
    palavra(img, "JOGOS!", W / 2, 870, 150, 3)
    cartas_borda(img, W, H, 4, 1190)
    # faixa de papel para o texto não brigar com as bolinhas
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((70, 975, W - 70, 1175), 18, fill=(246, 232, 200), outline=(150, 112, 70), width=3)
    texto_pixel(img, INFO, W / 2, 995, 36, 1.3)
    return img


def story():
    W, H = 1080, 1920
    img = papel(W, H)
    cantos(img, W, H)
    lg = K.logo(160)
    img.alpha_composite(lg, (int(W / 2 - lg.width / 2), 120))
    palavra(img, "TARDE", W / 2, 640, 176, 1)
    palavra(img, "DE", W / 2, 830, 160, 2)
    palavra(img, "JOGOS!", W / 2, 1010, 160, 3)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((60, 1130, W - 60, 1450), 20, fill=(246, 232, 200), outline=(150, 112, 70), width=3)
    texto_pixel(img, INFO, W / 2, 1160, 40, 1.8)
    cartas_borda(img, W, H, 4, 1690)  # o adesivo de link vai entre o texto e as cartas (y ~1480–1640)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    p, s = post(), story()
    p.convert("RGB").save(os.path.join(OUT, "post_1080x1350.png"))
    s.convert("RGB").save(os.path.join(OUT, "story_1080x1920.png"))
    sh = Image.new("RGB", (540 + 20 + 540, 960), (255, 255, 255))
    sh.paste(p.convert("RGB").resize((540, 675)), (0, 0))
    sh.paste(s.convert("RGB").resize((540, 960)), (560, 0))
    sh.save(os.path.join(OUT, "folha.jpg"), quality=90)
    print("ok")


if __name__ == "__main__":
    main()
