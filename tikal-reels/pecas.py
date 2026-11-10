"""Peças oficiais do Tikal prontas para compor (carregadas de assets/pecas/, ver recortes.py)."""
import math
import os
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
PEC = os.path.join(ROOT, "assets", "pecas")
ORIG = os.path.join(ROOT, "assets", "orig")
W, H = 1080, 1920
# cores dos exploradores (tiradas dos meeples oficiais)
CORES = {"vermelho": (214, 38, 70), "azul": (24, 140, 214), "laranja": (240, 118, 32), "branco": (238, 240, 246)}


def fonte(nome, s):
    for d in (os.path.join(ROOT, "assets", "fonts"), os.path.join(REPO, "comum", "fontes"), os.path.join(REPO, "taco-reels", "assets", "fonts"),
              os.path.join(REPO, "halloween-reels", "assets", "fonts"), os.path.join(REPO, "assinatura-reels", "assets", "fonts")):
        p = os.path.join(d, nome)
        if os.path.exists(p):
            return ImageFont.truetype(p, s)
    raise FileNotFoundError(nome)


@lru_cache(None)
def img(nome):
    return Image.open(os.path.join(PEC, nome)).convert("RGBA")


@lru_cache(None)
def hexa(tipo, w):
    im = img(f"hex_{tipo}.png")
    return im.resize((w, round(w * im.height / im.width)), Image.LANCZOS)


@lru_cache(None)
def meeple(cor, h):
    """Meeple oficial (o branco sozinho do render da editora) tingido na cor do jogador, mantendo a luz."""
    im = img("meeple_00.png")
    a = np.asarray(im).astype(float)
    lum = a[..., :3].mean(2) / 235.0
    c = np.array(CORES[cor], float)
    rgb = np.clip(c[None, None] * (0.25 + 0.95 * lum[..., None]) + 255 * np.clip(lum - 1.0, 0, 1)[..., None], 0, 255)
    out = np.dstack([rgb, a[..., 3]]).astype(np.uint8)
    s = Image.fromarray(out)
    return s.resize((round(h * s.width / s.height), h), Image.LANCZOS)


@lru_cache(None)
def tesouro(k, d):
    return img(f"tesouro_{k}.png").resize((d, d), Image.LANCZOS)


@lru_cache(None)
def capa():
    return Image.open(os.path.join(ORIG, "Tikal-FR-BoxFIN.jpg")).convert("RGB")


def cola(base, sp, cx, cy, rot=0.0, esc=1.0, alpha=1.0, sombra=0):
    if esc != 1.0:
        sp = sp.resize((max(1, round(sp.width * esc)), max(1, round(sp.height * esc))), Image.LANCZOS)
    if rot:
        sp = sp.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1:
        sp = sp.copy()
        sp.putalpha(sp.getchannel("A").point(lambda v: int(v * alpha)))
    if sombra:
        sh = Image.new("RGBA", sp.size, (0, 0, 0, 0))
        sh.putalpha(sp.getchannel("A").point(lambda v: int(v * 0.45)))
        sh = sh.filter(ImageFilter.GaussianBlur(sombra))
        base.alpha_composite(sh, (int(cx - sp.width / 2 + sombra * 0.6), int(cy - sp.height / 2 + sombra)))
    base.alpha_composite(sp, (int(cx - sp.width / 2), int(cy - sp.height / 2)))


def hex_centro(col, lin, w, x0, y0):
    """Grade de hexágonos de lado plano em cima: colunas a 0,75·w, colunas ímpares descem meia altura."""
    h = w * math.sqrt(3) / 2
    return x0 + col * 0.75 * w, y0 + lin * h + (h / 2 if col % 2 else 0)
