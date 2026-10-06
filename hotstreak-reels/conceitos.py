#!/usr/bin/env python3
"""Três propostas de visual para o Reels do Hot Streak (telas paradas para o dono escolher)."""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(ROOT, "assets", "pecas")
FN = os.path.join(ROOT, "assets", "fonts")
OUT = os.path.join(ROOT, "out")
W, H = 1080, 1920
MASC = ["p_hurley.png", "p_gobbler.png", "p_dangle.png", "p_mum.png"]
NOMES = ["HURLEY", "GOBBLER", "DANGLE", "MUM"]


def font(n, s):
    return ImageFont.truetype(os.path.join(FN, n), s)


def peca(n, h):
    im = Image.open(os.path.join(P, n)).convert("RGBA")
    return im.resize((int(im.width * h / im.height), int(h)), Image.LANCZOS)


def sombra(im, blur=14, off=(10, 16), op=0.45, cor=(0, 0, 0)):
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


def neon_texto(txt, fnt, cor, glow=28, core=(255, 255, 255)):
    tw = int(fnt.getlength(txt)) + glow * 6
    th = int(fnt.size * 1.6) + glow * 4
    base = Image.new("L", (tw, th), 0)
    ImageDraw.Draw(base).text((tw / 2, th / 2), txt, font=fnt, fill=255, anchor="mm")
    out = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    for r, op in ((glow * 1.6, 0.55), (glow * 0.7, 0.8), (glow * 0.25, 1.0)):
        g = base.filter(ImageFilter.GaussianBlur(r)).point(lambda v: min(255, int(v * op * 2.2)))
        layer = Image.new("RGBA", (tw, th), cor + (255,))
        layer.putalpha(g)
        out.alpha_composite(layer)
    c = Image.new("RGBA", (tw, th), core + (255,))
    c.putalpha(base)
    out.alpha_composite(c)
    return out


def ficha(r, cor):
    S = r * 2 + 20
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = S / 2
    d.ellipse((c - r, c - r, c + r, c + r), fill=cor, outline=(255, 255, 255), width=4)
    for k in range(8):
        a = k * math.pi / 4
        d.line((c + math.cos(a) * r * 0.62, c + math.sin(a) * r * 0.62, c + math.cos(a) * r * 0.98,
                c + math.sin(a) * r * 0.98), fill=(255, 255, 255), width=int(r * 0.22))
    d.ellipse((c - r * 0.55, c - r * 0.55, c + r * 0.55, c + r * 0.55), outline=(255, 255, 255), width=3)
    return im


# ---------------------------------------------------------------- 1. cassino neon
def cassino():
    y = np.linspace(0, 1, H)[:, None, None]
    base = np.array((14, 6, 30)) * (1 - y) + np.array((52, 8, 48)) * y
    img = Image.fromarray(np.repeat(base, W, 1).astype(np.uint8)).convert("RGBA")
    bok = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(bok)
    rng = np.random.default_rng(4)
    for _ in range(60):
        x, yy, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(10, 60)
        col = [(255, 60, 160), (255, 210, 60), (60, 220, 255), (160, 90, 255)][rng.integers(4)]
        d.ellipse((x - r, yy - r, x + r, yy + r), fill=col + (int(rng.uniform(30, 90)),))
    img.alpha_composite(bok.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(img)
    for k in range(0, W, 46):  # lâmpadas de letreiro
        for yy in (40, H - 40):
            d.ellipse((k + 8, yy - 10, k + 28, yy + 10), fill=(255, 220, 120))
    for k in range(40, H, 46):
        for xx in (30, W - 30):
            d.ellipse((xx - 10, k - 10, xx + 10, k + 10), fill=(255, 220, 120))
    cola(img, neon_texto("HOT STREAK", font("Monoton-Regular.ttf", 120), (255, 50, 150)), W / 2, 260, -4)
    cola(img, neon_texto("CORRIDA · APOSTA · GRITARIA", font("Bungee-Regular.ttf", 40), (60, 220, 255), 14), W / 2,
         430)
    # pista neon em perspectiva
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for k in range(5):
        xt, xb = 300 + k * 120, -140 + k * 340
        od.line((xt, 700, xb, 1560), fill=(60, 255, 160, 255), width=6)
    img.alpha_composite(ov.filter(ImageFilter.GaussianBlur(8)))
    img.alpha_composite(ov)
    odds = ["3:1", "5:1", "2:1", "10:1"]
    for k, (m, o) in enumerate(zip(MASC, odds)):
        x = 175 + k * 245
        cola(img, sombra(peca(m, 400), cor=(80, 0, 60)), x, 1180 + (k % 2) * 40)
        led = Image.new("RGBA", (190, 90), (0, 0, 0, 0))
        ImageDraw.Draw(led).rounded_rectangle((0, 0, 189, 89), radius=14, fill=(10, 10, 20, 230),
                                              outline=(255, 210, 60), width=4)
        cola(led, neon_texto(o, font("Bungee-Regular.ttf", 46), (255, 210, 60), 8), 95, 45)
        cola(img, led, x, 900 + (k % 2) * 40)
    for x, yy, r, c in ((140, 1600, 70, (220, 30, 60)), (930, 1580, 80, (30, 120, 220)), (820, 1690, 60, (20, 20, 20))):
        cola(img, sombra(ficha(r, c)), x, yy, 20)
    t = Image.open(os.path.join(P, "ticket_gobbler_risky.png")).convert("RGBA")
    t = t.resize((520, int(t.height * 520 / t.width)), Image.LANCZOS)
    cola(img, sombra(t), 520, 1620, 8)
    return img


# ---------------------------------------------------------------- 2. arquibancada com a arte do jogo
def pista(w, h):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lanes = 4
    for k in range(lanes):
        y0 = k * h / lanes
        d.rectangle((0, y0, w, y0 + h / lanes), fill=(46, 150, 70) if k % 2 else (56, 170, 80))
        for x in range(30, w, 150):
            d.rounded_rectangle((x, y0 + h / lanes - 14, x + 60, y0 + h / lanes - 4), radius=4,
                                fill=(255, 255, 255))
    for x in range(80, w, 260):
        for k in range(lanes):
            cx, cy, r = x + (k % 2) * 120, k * h / lanes + h / lanes * 0.45, 22
            pts = [(cx + (r if i % 2 == 0 else r * 0.45) * math.cos(-math.pi / 2 + i * math.pi / 5),
                    cy + (r if i % 2 == 0 else r * 0.45) * math.sin(-math.pi / 2 + i * math.pi / 5)) for i in range(10)]
            d.polygon(pts, fill=(170, 230, 170))
    return im


def arquibancada():
    img = Image.new("RGBA", (W, H), (34, 110, 60, 255))
    t = Image.open(os.path.join(P, "v_torcida.png")).convert("RGBA")
    s = 1080 / t.height * 1.0
    t = t.resize((int(t.width * s), 1080), Image.LANCZOS)
    img.alpha_composite(t, ((W - t.width) // 2, -60))
    # tampa a placa "VIDEO RULES" (QR da editora) com uma placa nossa
    plq = Image.new("RGBA", (600, 400), (0, 0, 0, 0))
    ImageDraw.Draw(plq).rectangle((0, 0, 599, 399), fill=(255, 214, 60))
    ImageDraw.Draw(plq).text((300, 140), "APOSTE", font=font("LuckiestGuy-Regular.ttf", 120), fill=(200, 30, 30),
                             anchor="mm")
    ImageDraw.Draw(plq).text((300, 280), "AQUI!", font=font("LuckiestGuy-Regular.ttf", 120), fill=(200, 30, 30),
                             anchor="mm")
    cola(img, plq, 300, 560, 9)
    pv = pista(W + 400, 820)
    pv = pv.transform(pv.size, Image.PERSPECTIVE, (1.15, 0.25, -200, 0, 1.0, 0, 0, 0.00035), Image.BICUBIC)
    img.alpha_composite(pv, (-200, 1000))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 990, W, 1010), fill=(255, 255, 255))
    for k, m in enumerate(MASC):
        x = 160 + k * 255
        cola(img, sombra(peca(m, 430 - k * 15)), x, 1260 + k * 70, [-8, 6, -4, 8][k])
    rng = np.random.default_rng(2)
    for _ in range(140):  # confete
        x, yy = rng.uniform(0, W), rng.uniform(0, H)
        col = [(255, 210, 60), (240, 60, 70), (60, 160, 240), (255, 255, 255), (250, 120, 40)][rng.integers(5)]
        a = rng.uniform(0, math.pi)
        d.line((x, yy, x + 22 * math.cos(a), yy + 22 * math.sin(a)), fill=col, width=9)
    placa = Image.new("RGBA", (900, 180), (0, 0, 0, 0))
    pd = ImageDraw.Draw(placa)
    pd.rectangle((10, 10, 890, 170), fill=(230, 40, 40))
    pd.text((450, 92), "QUEM VAI VENCER?", font=font("LuckiestGuy-Regular.ttf", 100), fill=(255, 220, 60),
            anchor="mm", stroke_width=6, stroke_fill=(150, 20, 20))
    cola(img, sombra(placa), W / 2, 1720, -3)
    return img


# ---------------------------------------------------------------- 3. programa de turfe retrô
def turfe():
    rng = np.random.default_rng(1)
    base = np.array((243, 232, 205), np.float32) + rng.normal(0, 5, (H, W, 1))
    img = Image.fromarray(base.clip(0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(img)
    INK, RED = (30, 24, 20), (196, 40, 36)
    d.rectangle((40, 40, W - 40, H - 40), outline=INK, width=6)
    d.rectangle((54, 54, W - 54, H - 54), outline=INK, width=2)
    slab = lambda s: font("AlfaSlabOne-Regular.ttf", s)
    d.text((W / 2, 130), "PROGRAMA OFICIAL", font=slab(44), fill=INK, anchor="mm")
    d.line((120, 170, W - 120, 170), fill=INK, width=3)
    d.text((W / 2, 280), "HOT STREAK", font=slab(118), fill=RED, anchor="mm", stroke_width=3, stroke_fill=INK)
    d.text((W / 2, 400), "• 1º PÁREO · GRANDE PRÊMIO DOS MASCOTES •", font=slab(34), fill=INK, anchor="mm")
    d.line((120, 450, W - 120, 450), fill=INK, width=3)
    odds = ["3/1", "5/1", "2/1", "10/1"]
    for k, (m, nome, o) in enumerate(zip(MASC, NOMES, odds)):
        y = 560 + k * 250
        d.ellipse((90, y - 40, 170, y + 40), fill=RED if k % 2 else INK)
        d.text((130, y), str(k + 1), font=slab(52), fill=(243, 232, 205), anchor="mm")
        cola(img, peca(m, 210), 290, y)
        d.text((420, y - 30), nome, font=slab(64), fill=INK, anchor="lm")
        d.text((420, y + 34), ["o cachorro-quente", "o urso", "o peixe-pescador", "a rainha"][k],
               font=font("Poppins-ExtraBold.ttf", 30), fill=INK, anchor="lm")
        d.text((W - 110, y), o, font=slab(70), fill=RED, anchor="rm")
        d.line((90, y + 110, W - 90, y + 110), fill=INK, width=2)
    t = Image.open(os.path.join(P, "ticket_yes_risky.png")).convert("RGBA")
    t = t.resize((560, int(t.height * 560 / t.width)), Image.LANCZOS)
    cola(img, sombra(t, op=0.3), 640, 1650, -8)
    selo = Image.new("RGBA", (360, 360), (0, 0, 0, 0))
    sd = ImageDraw.Draw(selo)
    sd.ellipse((10, 10, 350, 350), outline=RED, width=12)
    sd.text((180, 150), "APOSTA", font=slab(54), fill=RED, anchor="mm")
    sd.text((180, 220), "FEITA!", font=slab(54), fill=RED, anchor="mm")
    cola(img, selo, 230, 1650, 14)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    ims = [cassino(), arquibancada(), turfe()]
    nomes = ["1 · CASSINO NEON", "2 · ARQUIBANCADA (ARTE DO JOGO)", "3 · PROGRAMA DE TURFE RETRÔ"]
    for k, im in enumerate(ims):
        im.convert("RGB").save(os.path.join(OUT, f"conceito_{k + 1}.png"))
    sheet = Image.new("RGB", (3 * 560 + 40, 1040), (24, 24, 30))
    d = ImageDraw.Draw(sheet)
    for k, (im, n) in enumerate(zip(ims, nomes)):
        sheet.paste(im.convert("RGB").resize((540, 960), Image.LANCZOS), (20 + k * 560, 70))
        d.text((20 + k * 560 + 270, 36), n, font=font("Poppins-ExtraBold.ttf", 28), fill=(255, 255, 255), anchor="mm")
    sheet.save(os.path.join(OUT, "conceitos_hotstreak.jpg"), quality=92)
    print("ok")


if __name__ == "__main__":
    main()
