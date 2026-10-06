"""Visuais alternativos do stop motion (para não parecer o vídeo do Vudú).

TEMA = "prancheta": mesa de madeira clara com papel de desenho técnico, textos em fita crepe escritos à mão.
TEMA = "pedra":     areia/arenito ensolarado da Antiguidade, textos gravados em placas de pedra.
TEMA = "papel":     colagem em papel colorido, textos em tiras de papel rasgado.
"""
import math
import os
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(ROOT, "assets", "fonts")
W, H = 1080, 1920
TEMA = os.environ.get("TEMA", "prancheta")

GOLD = (255, 200, 60)
RED = (232, 56, 50)
BLUE = (70, 160, 240)
GREEN = (110, 200, 70)


@lru_cache(None)
def font(name, size, var=None):
    f = ImageFont.truetype(os.path.join(FONTS, name), size)
    if var:
        f.set_variation_by_name(var)
    return f


def wrap(text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if fnt.getlength(test) <= maxw or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def _noise(shape, scale, seed):
    rng = np.random.default_rng(seed)
    h, w = shape
    small = rng.normal(0, 1, (max(2, h // scale), max(2, w // scale))).astype(np.float32)
    im = Image.fromarray(((small + 4) * 30).clip(0, 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    return np.asarray(im, np.float32) / 30 - 4


# ---------------------------------------------------------------- fundos
@lru_cache(None)
def bg():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    if TEMA == "prancheta":
        # madeira clara: veios alongados + nós suaves
        grain = np.sin((x * 0.018 + _noise((H, W), 60, 1) * 1.6 + _noise((H, W), 9, 2) * 0.25) * 6.0)
        base = np.array((196, 150, 102), np.float32) + grain[..., None] * np.array((16, 13, 9), np.float32)
        base += _noise((H, W), 3, 3)[..., None] * 3
        img = Image.fromarray(base.clip(0, 255).astype(np.uint8))
        # folha de papel de desenho técnico presa com fita
        sheet = Image.new("RGBA", (980, 1640), (232, 240, 246, 255))
        d = ImageDraw.Draw(sheet)
        for gx in range(0, 980, 30):
            d.line((gx, 0, gx, 1640), fill=(150, 180, 210, 70 if gx % 150 else 140), width=1)
        for gy in range(0, 1640, 30):
            d.line((0, gy, 980, gy), fill=(150, 180, 210, 70 if gy % 150 else 140), width=1)
        d.rectangle((24, 24, 955, 1615), outline=(90, 120, 160, 160), width=3)
        sh = Image.new("L", (sheet.width + 80, sheet.height + 80), 0)
        sh.paste(110, (40, 40, 40 + sheet.width, 40 + sheet.height))
        sh = sh.filter(ImageFilter.GaussianBlur(18))
        sheet_r = sheet.rotate(-1.2, expand=True, resample=Image.BICUBIC)
        sh_r = sh.rotate(-1.2, expand=True)
        img.paste((50, 30, 15), (int(W / 2 - sh_r.width / 2) + 12, int(H / 2 - sh_r.height / 2) + 20), sh_r)
        img.paste(sheet_r, (int(W / 2 - sheet_r.width / 2), int(H / 2 - sheet_r.height / 2) - 30), sheet_r)
        for cx, cy, r in ((90, 150, -38), (990, 150, 40), (90, 1720, 40), (990, 1720, -38)):
            t = tape_img(" ", 30, angle=r)
            img.paste(t, (cx - t.width // 2, cy - t.height // 2), t)
        # lápis no canto
        pen = Image.new("RGBA", (520, 40), (0, 0, 0, 0))
        dp = ImageDraw.Draw(pen)
        dp.rectangle((60, 6, 470, 34), fill=(240, 190, 40, 255))
        dp.rectangle((60, 6, 470, 13), fill=(250, 210, 80, 255))
        dp.rectangle((470, 6, 515, 34), fill=(230, 140, 150, 255))
        dp.polygon([(60, 6), (60, 34), (8, 20)], fill=(230, 200, 160, 255))
        dp.polygon([(26, 14), (26, 26), (8, 20)], fill=(50, 50, 50, 255))
        pen = pen.rotate(28, expand=True, resample=Image.BICUBIC)
        img.paste(pen, (W - pen.width + 30, H - pen.height - 10), pen)
        return img.convert("RGB")
    if TEMA == "pedra":
        light = 1.12 - 0.35 * np.hypot((x - W * 0.25) / W, (y - H * 0.1) / H)
        n1, n2 = _noise((H, W), 80, 4), _noise((H, W), 6, 5)
        base = np.array((214, 182, 136), np.float32) * light[..., None]
        base += n1[..., None] * np.array((10, 9, 7)) + n2[..., None] * 4
        # blocos de pedra: juntas horizontais e verticais desencontradas
        img = Image.fromarray(base.clip(0, 255).astype(np.uint8)).convert("RGBA")
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        rng = np.random.default_rng(9)
        for r, yy in enumerate(range(0, H, 240)):
            d.line((0, yy, W, yy), fill=(120, 90, 60, 90), width=4)
            d.line((0, yy + 3, W, yy + 3), fill=(255, 235, 200, 60), width=2)
            off = 0 if r % 2 else 260
            for xx in range(off, W + 520, 520):
                xj = xx + int(rng.integers(-40, 40))
                d.line((xj, yy, xj, yy + 240), fill=(120, 90, 60, 80), width=4)
        img.alpha_composite(ov.filter(ImageFilter.GaussianBlur(1.2)))
        return img.convert("RGB")
    # papel: fundo de papel creme com fibras
    base = np.array((246, 236, 216), np.float32) + _noise((H, W), 4, 6)[..., None] * 3 + _noise((H, W), 90, 7)[..., None] * 5
    img = Image.fromarray(base.clip(0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(11)
    for k in range(9):  # retalhos coloridos ao fundo
        col = [(255, 214, 120), (140, 210, 200), (250, 160, 140), (180, 200, 250)][k % 4]
        cx, cy = rng.uniform(0, W), rng.uniform(0, H)
        pts = [(cx + math.cos(a) * rng.uniform(140, 260), cy + math.sin(a) * rng.uniform(140, 260))
               for a in np.linspace(0, 2 * math.pi, 9)[:-1]]
        d.polygon(pts, fill=col + (110,))
    return img.convert("RGB")


SHADOW = {"prancheta": ((60, 35, 15), 0.45), "pedra": ((70, 45, 20), 0.5), "papel": ((90, 70, 50), 0.35)}


# ---------------------------------------------------------------- textos
@lru_cache(None)
def tape_img(text, size, color=None, angle=0.0, maxw=900):
    """Fita crepe com texto à mão (caneta preta; destaque em vermelho)."""
    f = font("ArchitectsDaughter-Regular.ttf", size)
    lines = wrap(text, f, maxw) if text.strip() else [" "]
    lh = int(size * 1.15)
    tw = max(f.getlength(l) for l in lines)
    w, h = int(tw + size * 1.2) if text.strip() else 150, int(lh * len(lines) + size * 0.55)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(len(text) * 13 + size)
    # bordas serrilhadas nas pontas
    left = [(rng.uniform(0, 10), yy) for yy in np.linspace(0, h, 9)]
    right = [(w - rng.uniform(0, 10), yy) for yy in np.linspace(h, 0, 9)]
    d.polygon(left + right, fill=(238, 224, 178, 235))
    a = np.asarray(im, np.float32)
    a[..., :3] += _noise((h, w), 3, len(text))[..., None] * 4
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    ink = (200, 36, 36) if color in (GOLD, RED) else (28, 30, 40)
    for i, l in enumerate(lines):
        d.text((w / 2, size * 0.28 + lh * i + lh / 2), l, font=f, fill=ink, anchor="mm", stroke_width=max(1, size // 30),
               stroke_fill=ink)
    if angle:
        im = im.rotate(angle, expand=True, resample=Image.BICUBIC)
    return im


@lru_cache(None)
def stone_img(text, size, color=None, maxw=900):
    """Placa de pedra com letras gravadas (destaque com letras douradas)."""
    f = font("Cinzel-VF.ttf", size, "Black")
    lines = wrap(text, f, maxw)
    lh = int(size * 1.08)
    tw = max(f.getlength(l) for l in lines)
    w, h = int(tw + size * 1.1), int(lh * len(lines) + size * 0.8)
    rng = np.random.default_rng(len(text))
    base = np.array((190, 178, 160), np.float32) + _noise((h, w), 5, len(text) + 1)[..., None] * 7
    base += _noise((h, w), 40, len(text) + 2)[..., None] * 6
    im = Image.fromarray(base.clip(0, 255).astype(np.uint8)).convert("RGBA")
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=int(size * 0.18), fill=255)
    im.putalpha(m)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((3, 3, w - 4, h - 4), radius=int(size * 0.16), outline=(235, 226, 210, 200), width=4)
    d.rounded_rectangle((8, 8, w - 9, h - 9), radius=int(size * 0.14), outline=(120, 108, 92, 160), width=3)
    for i, l in enumerate(lines):
        cx, cy = w / 2, size * 0.42 + lh * i + lh / 2
        d.text((cx + 3, cy + 3), l, font=f, fill=(245, 238, 225, 255), anchor="mm")
        if color in (GOLD, RED):
            d.text((cx, cy), l, font=f, fill=(196, 140, 30, 255), anchor="mm", stroke_width=2, stroke_fill=(90, 60, 20))
        else:
            d.text((cx, cy), l, font=f, fill=(78, 66, 54, 255), anchor="mm")
    return im


PAPEIS = [(38, 150, 140), (236, 96, 72), (240, 170, 40), (70, 110, 200)]


@lru_cache(None)
def paper_img(text, size, color=None, maxw=900):
    """Tira de papel colorido rasgado com letras brancas."""
    f = font("Poppins-ExtraBold.ttf", size)
    lines = wrap(text, f, maxw)
    lh = int(size * 1.15)
    tw = max(f.getlength(l) for l in lines)
    w, h = int(tw + size * 1.0), int(lh * len(lines) + size * 0.6)
    rng = np.random.default_rng(len(text) * 7 + size)
    col = {GOLD: (240, 170, 40), RED: (230, 70, 60), BLUE: (70, 110, 200), GREEN: (38, 150, 140)}.get(
        color, PAPEIS[len(text) % len(PAPEIS)])
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    top = [(xx, rng.uniform(0, 7)) for xx in np.linspace(0, w, 24)]
    bot = [(xx, h - rng.uniform(0, 7)) for xx in np.linspace(w, 0, 24)]
    d.polygon(top + bot, fill=(255, 255, 255, 255))
    inner_t = [(xx, 6 + rng.uniform(0, 6)) for xx in np.linspace(4, w - 4, 24)]
    inner_b = [(xx, h - 6 - rng.uniform(0, 6)) for xx in np.linspace(w - 4, 4, 24)]
    d.polygon(inner_t + inner_b, fill=col + (255,))
    ink = (40, 30, 20) if col == (240, 170, 40) else (255, 255, 255)
    for i, l in enumerate(lines):
        d.text((w / 2, size * 0.3 + lh * i + lh / 2), l, font=f, fill=ink, anchor="mm")
    return im


def label(text, size, color):
    if TEMA == "prancheta":
        return tape_img(text, int(size * 0.95), color)
    if TEMA == "pedra":
        return stone_img(text, int(size * 0.72), color)
    return paper_img(text, int(size * 0.7), color)


VIGNETTE = {"prancheta": 0.28, "pedra": 0.3, "papel": 0.18}
