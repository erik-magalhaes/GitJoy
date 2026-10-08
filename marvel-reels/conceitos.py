#!/usr/bin/env python3
"""Três conceitos visuais para o Reels dos Marvel United do acervo + Multiverse (quadros parados para escolher).

    python3 conceitos.py    # out/conceito_1..3.png e out/conceitos_marvel.jpg
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
CAP = os.path.join(ROOT, "assets", "capas")
FN = os.path.join(ROOT, "assets", "fonts")
OUT = os.path.join(ROOT, "out")
W, H = 1080, 1920
WHITE, NAVY = (255, 255, 255), (15, 23, 42)
CAPAS = ["marvel_united", "marvel_united_x_men", "marvel_united_enter_the_spider_verse", "marvel_united_deadpool",
         "marvel_united_civil_war", "marvel_united_rise_of_the_black_panther", "marvel_united_spider_geddon",
         "marvel_united_x_men_blue_team", "marvel_united_x_men_gold_team"]


def font(n, s):
    return ImageFont.truetype(os.path.join(FN, n), s)


def capa(n, w):
    im = Image.open(os.path.join(CAP, n + ".jpg")).convert("RGB")
    return im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)


def caixa_mv(h):
    im = Image.open(os.path.join(ROOT, "assets", "multiverse_caixa.png")).convert("RGBA")
    return im.resize((int(im.width * h / im.height), h), Image.LANCZOS)


def sombra(im, blur=14, off=(10, 18), op=0.5, cor=(0, 0, 0)):
    pad = blur * 3
    out = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    a = Image.new("L", out.size, 0)
    a.paste(im.getchannel("A").point(lambda v: int(v * op)), (pad + off[0], pad + off[1]))
    sh = Image.new("RGBA", out.size, cor + (255,))
    sh.putalpha(a.filter(ImageFilter.GaussianBlur(blur)))
    out.alpha_composite(sh)
    out.alpha_composite(im, (pad, pad))
    return out


def cola(img, im, x, y, rot=0):
    if rot:
        im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))


def logo(img, w=170):
    lg = Image.open(os.path.join(ROOT, "assets", "logo_suavez.png")).convert("RGBA")
    lg = lg.resize((w, int(lg.height * w / lg.width)), Image.LANCZOS)
    card = Image.new("RGBA", (lg.width + 24, lg.height + 20), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=16, fill=WHITE)
    card.alpha_composite(lg, (12, 10))
    img.alpha_composite(card, (W - card.width - 30, 40))


def titulo(img, txt, y, size=90, cor=WHITE, contorno=(120, 10, 20), f="Bangers-Regular.ttf"):
    d = ImageDraw.Draw(img)
    for k, l in enumerate(txt.split("\n")):
        d.text((540, y + k * size * 1.05), l, font=font(f, size), fill=cor, anchor="mm", stroke_width=size // 10,
               stroke_fill=contorno)


def cosmos(seed=1, c1=(30, 6, 60), c2=(4, 10, 40)):
    """Fundo de espaço do multiverso: degradê roxo, estrelas e névoa."""
    yy = np.linspace(0, 1, H)[:, None, None]
    a = (np.array(c1) * (1 - yy) + np.array(c2) * yy) * np.ones((1, W, 1))
    img = Image.fromarray(a.astype(np.uint8), "RGB").convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    rng = np.random.default_rng(seed)
    for _ in range(14):
        x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(150, 420)
        c = [(120, 40, 200), (40, 120, 255), (255, 60, 140)][rng.integers(3)]
        d.ellipse((x - r, y - r, x + r, y + r), fill=c + (40,))
    img.alpha_composite(ov.filter(ImageFilter.GaussianBlur(90)))
    d = ImageDraw.Draw(img)
    for _ in range(260):
        x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(0.8, 2.6)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, int(rng.uniform(120, 255))))
    return img


def portal(img, n, cx, cy, r, seed=0):
    """Capa vista por um portal circular de faíscas."""
    c = capa(n, int(r * 2.2))
    m = Image.new("L", c.size, 0)
    ImageDraw.Draw(m).ellipse((c.width / 2 - r, c.height / 2 - r, c.width / 2 + r, c.height / 2 + r), fill=255)
    c = c.convert("RGBA")
    c.putalpha(m)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lay.alpha_composite(c, (int(cx - c.width / 2), int(cy - c.height / 2)))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    g.ellipse((cx - r - 26, cy - r - 26, cx + r + 26, cy + r + 26), outline=(255, 150, 40, 255), width=26)
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(18)))
    img.alpha_composite(lay)
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(seed)
    for _ in range(120):  # faíscas girando na borda
        a = rng.uniform(0, 2 * math.pi)
        rr = r + rng.uniform(-6, 14)
        L = rng.uniform(10, 34)
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
        d.line((x, y, x - L * math.sin(a), y + L * math.cos(a)), fill=(255, int(rng.uniform(170, 240)), 80), width=3)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(255, 220, 120), width=5)


# ---------------------------------------------------------------- 1. portais do multiverso
def conceito_portais():
    img = cosmos(1)
    for k, (n, x, y, r) in enumerate(((CAPAS[1], 280, 560, 190), (CAPAS[2], 800, 700, 210), (CAPAS[3], 330, 1050, 170),
                                       (CAPAS[5], 800, 1200, 160))):
        portal(img, n, x, y, r, k)
    cola(img, sombra(caixa_mv(520)), 540, 1450, -4)
    titulo(img, "9 UNIVERSOS\nMARVEL NO ACERVO!", 230, 100)
    logo(img)
    return img


# ---------------------------------------------------------------- 2. seleção de personagem (videogame)
def conceito_selecao():
    img = Image.new("RGBA", (W, H), (10, 12, 30, 255))
    d = ImageDraw.Draw(img)
    for y in range(0, H, 6):  # linhas de tela de fliperama
        d.line((0, y, W, y), fill=(18, 22, 48), width=2)
    for k in range(-H, W + H, 140):
        d.line((k, 0, k - H * 0.4, H), fill=(30, 20, 70), width=40)
    titulo(img, "ESCOLHA SUA\nAVENTURA!", 220, 104, (255, 220, 40), (150, 0, 40))
    cw = 300
    for k, n in enumerate(CAPAS):
        x, y = 210 + (k % 3) * 330, 560 + (k // 3) * 330
        c = capa(n, cw).convert("RGBA")
        c = c.crop((0, 0, cw, cw))
        sel = k == 2
        d.rectangle((x - cw / 2 - 8, y - cw / 2 - 8, x + cw / 2 + 8, y + cw / 2 + 8),
                    fill=(255, 220, 40) if sel else (60, 70, 120))
        img.alpha_composite(c, (int(x - cw / 2), int(y - cw / 2)))
        if sel:
            d.text((x - cw / 2 + 10, y - cw / 2 - 40), "P1", font=font("Bungee-Regular.ttf", 46), fill=(255, 220, 40))
    d.rounded_rectangle((90, 1540, 990, 1660), radius=20, fill=(220, 30, 50))
    d.text((540, 1600), "NOVO DESAFIANTE: MULTIVERSE!", font=font("Bungee-Regular.ttf", 46), fill=WHITE, anchor="mm")
    logo(img)
    return img


# ---------------------------------------------------------------- 3. cartas holográficas
def carta_holo(n, w, seed=0, rara=False):
    h = int(w * 1.42)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    borda = (255, 200, 40) if rara else (200, 210, 230)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=int(w * 0.06), fill=borda)
    d.rounded_rectangle((w * 0.05, w * 0.05, w * 0.95, h - w * 0.05), radius=int(w * 0.04), fill=(20, 20, 40))
    if n == "multiverse":
        cx = caixa_mv(int(h * 0.62))
        im.alpha_composite(cx, (int(w / 2 - cx.width / 2), int(h * 0.08)))
    else:
        c = capa(n, int(w * 0.86)).crop((0, 0, int(w * 0.86), int(w * 0.86)))
        im.paste(c, (int(w * 0.07), int(w * 0.09)))
    # brilho holográfico (faixas de arco-íris na diagonal)
    holo = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    hd = ImageDraw.Draw(holo)
    for k in range(-h, w + h, 22):
        c = [(255, 80, 120), (255, 220, 80), (80, 255, 200), (80, 160, 255), (200, 100, 255)][(k // 22) % 5]
        hd.line((k, 0, k + h * 0.6, h), fill=c + (34,), width=14)
    im.alpha_composite(holo)
    nome = "MULTIVERSE" if n == "multiverse" else n.replace("marvel_united", "").replace("_", " ").strip().upper() or \
        "MARVEL UNITED"
    f = font("Bungee-Regular.ttf", int(w * 0.075))
    d = ImageDraw.Draw(im)
    d.text((w / 2, h * 0.78), nome[:22], font=f, fill=WHITE, anchor="mm")
    d.text((w / 2, h * 0.88), "1-5 JOG. · 40 MIN", font=font("Poppins-ExtraBold.ttf", int(w * 0.06)),
           fill=borda, anchor="mm")
    if rara:
        d.rounded_rectangle((w * 0.62, h * 0.02, w * 0.98, h * 0.1), radius=10, fill=(220, 30, 50))
        d.text((w * 0.8, h * 0.06), "EM BREVE", font=font("Bungee-Regular.ttf", int(w * 0.05)), fill=WHITE, anchor="mm")
    return sombra(im, 14, (10, 18), 0.6)


def conceito_cartas():
    img = cosmos(5, (10, 10, 30), (40, 8, 50))
    for k, (n, x, y, r) in enumerate(((CAPAS[1], 250, 760, -14), (CAPAS[6], 830, 760, 14), (CAPAS[0], 540, 700, 0))):
        cola(img, carta_holo(n, 400, k), x, y, r)
    cola(img, carta_holo("multiverse", 520, 9, rara=True), 540, 1290, -3)
    titulo(img, "COLEÇÃO\nMARVEL UNITED", 230, 100, WHITE, (20, 40, 140))
    logo(img)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    ims = [conceito_portais(), conceito_selecao(), conceito_cartas()]
    nomes = ["1 · PORTAIS DO MULTIVERSO", "2 · TELA DE SELEÇÃO", "3 · CARTAS HOLOGRÁFICAS"]
    sheet = Image.new("RGB", (3 * 540 + 80, 960 + 140), (245, 240, 235))
    d = ImageDraw.Draw(sheet)
    for k, im in enumerate(ims):
        im.convert("RGB").save(os.path.join(OUT, f"conceito_{k + 1}.png"))
        sheet.paste(im.convert("RGB").resize((540, 960), Image.LANCZOS), (20 + k * 560, 110))
        d.text((20 + k * 560 + 270, 55), nomes[k], font=font("Poppins-ExtraBold.ttf", 34), fill=NAVY, anchor="mm")
    sheet.save(os.path.join(OUT, "conceitos_marvel.jpg"), quality=90)
    print("ok")


if __name__ == "__main__":
    main()
