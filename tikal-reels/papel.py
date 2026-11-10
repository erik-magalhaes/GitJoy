"""Papel e escrita REALISTAS para o caderno do Tikal (pedido dele 10/nov: "mais realista as escritas e a folha, nada de
animação"). O papel é uma 'foto' de caderno: fibras em várias escalas, luz vindo do alto à esquerda, curvatura e sombra
perto da espiral de arame, pauta impressa fina e irregular. A escrita é caneta esferográfica: fonte de mão real (Caveat),
cada letra com giro, altura e tamanho um pouco diferentes, linha de base ondulando, tinta com falhas/pressão variável e
aplicada em MULTIPLICAR sobre o papel (a textura aparece através da tinta)."""
import math
import random
from functools import lru_cache

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from pecas import W, H, fonte

LINHA0, PASSO = 250, 64
TINTA_AZUL = (22, 38, 112)
TINTA_VERM = (178, 24, 32)
GRAFITE = (78, 78, 84)


def _ruido(shape, escala, semente):
    rnd = np.random.default_rng(semente)
    h, w = shape
    n = rnd.normal(0, 1, (max(2, h // escala), max(2, w // escala)))
    return cv2.resize(n, (w, h), interpolation=cv2.INTER_CUBIC)


@lru_cache(None)
def folha(k):
    """Folha de caderno fotografada: devolve RGBA 1080x1920 (já com a mesa nas bordas que a folha não cobre)."""
    sh = (H, W)
    papel = np.array([241, 236, 222], np.float32)
    n = (0.018 * _ruido(sh, 160, k) + 0.012 * _ruido(sh, 24, k + 1) + 0.010 * _ruido(sh, 3, k + 2)
         + 0.006 * np.random.default_rng(k + 3).normal(0, 1, sh))
    # fibras: riscos finos alongados
    fib = cv2.GaussianBlur(np.random.default_rng(k + 4).normal(0, 1, sh).astype(np.float32), (0, 0), sigmaX=6, sigmaY=0.6)
    n += 0.015 * fib
    a = papel[None, None] * (1 + n[..., None])
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    luz = 1.04 - 0.10 * ((xx / W) * 0.6 + (yy / H) * 0.8) - 0.10 * ((xx / W - 0.45) ** 2 + (yy / H - 0.45) ** 2)
    # curvatura perto da espiral (a folha afunda e escurece)
    curva = 1 - 0.16 * np.exp(-(xx - 40) / 70.0) * (xx > 0)
    a *= (luz * curva)[..., None]
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    # pauta impressa (fina, com intensidade irregular) e margem
    pauta = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(pauta)
    for y in range(LINHA0, H - 30, PASSO):
        d.line((100, y, W, y), fill=150, width=2)
    d.line((150, 0, 150, H), fill=255, width=2)
    pm = np.asarray(pauta).astype(np.float32) / 255
    pm = cv2.GaussianBlur(pm, (0, 0), 0.6) * np.clip(0.75 + 0.35 * _ruido(sh, 40, k + 5), 0.3, 1.0)
    cor_p = np.zeros((H, W, 3), np.float32)
    cor_p[...] = (132, 168, 205)
    margem = (np.abs(xx - 150) < 4)
    cor_p[margem] = (214, 104, 110)
    base = np.asarray(img)[..., :3].astype(np.float32)
    base = base * (1 - pm[..., None]) + (base * cor_p / 255.0) * pm[..., None] * 1.0 + base * pm[..., None] * 0.0
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert("RGBA")
    # furos e espiral de arame
    d = ImageDraw.Draw(img)
    for y in range(95, H, 92):
        d.ellipse((58, y - 13, 82, y + 13), fill=(60, 40, 26, 255))
    esp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    de = ImageDraw.Draw(esp)
    for y in range(95, H, 92):
        for j, (c, w_) in enumerate((((40, 40, 44), 9), ((150, 152, 158), 6), ((225, 228, 232), 2))):
            de.arc((-30, y - 30 + j, 92, y + 18 + j), 200, 360, fill=c + (255,), width=w_)
    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sombra.putalpha(esp.getchannel("A").point(lambda v: int(v * 0.5)))
    img.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(5)), (6, 8))
    img.alpha_composite(esp)
    return img


@lru_cache(None)
def _glifos(txt, s, fnome, peso, semente):
    """Desenha o texto letra a letra com variação de mão. Devolve (máscara de tinta float, larguras por linha, alt)."""
    f = fonte(fnome, s)
    try:
        f.set_variation_by_axes([peso])
    except Exception:
        pass
    rnd = random.Random(semente)
    linhas = txt.split("\n")
    alt = int(s * 1.05)
    larg_tot = [int(f.getlength(li) * 1.08) + 30 for li in linhas]
    im = Image.new("L", (max(larg_tot) + 40, alt * len(linhas) + 40), 0)
    larguras = []
    for i, li in enumerate(linhas):
        x = 10.0
        fase = rnd.uniform(0, 6)
        incl = rnd.uniform(-0.012, 0.012)  # a linha sobe/desce um pouco
        for ch in li:
            w = f.getlength(ch)
            if ch != " ":
                e = rnd.uniform(0.95, 1.05)
                g = Image.new("L", (int(s * 1.6), int(s * 1.6)), 0)
                ImageDraw.Draw(g).text((s * 0.3, s * 0.15), ch, font=f, fill=255)
                g = g.resize((max(1, int(g.width * e)), max(1, int(g.height * e))), Image.LANCZOS)
                g = g.rotate(rnd.uniform(-4, 4), resample=Image.BICUBIC)
                y = 18 + i * alt + 3 * math.sin(x / 55 + fase) + incl * x + rnd.uniform(-1.5, 1.5)
                im.paste(255, (int(x - s * 0.3 * e), int(y - s * 0.15 * e)), g)
            x += w * rnd.uniform(0.98, 1.06)
        larguras.append(int(x) + 10)
    return np.asarray(im).astype(np.float32) / 255, larguras, alt


@lru_cache(None)
def tinta(txt, s, cor=TINTA_AZUL, fnome="Caveat.ttf", peso=520, semente=1):
    """Tinta de esferográfica: textura de pressão, falhas finas, bordas levemente borradas. Devolve RGBA."""
    m, larg, alt = _glifos(txt, s, fnome, peso, semente)
    h, w = m.shape
    pres = np.clip(0.80 + 0.22 * _ruido((h, w), 30, semente + 9), 0.55, 1.0)
    falha = np.clip(1.0 - 0.45 * (np.random.default_rng(semente).random((h, w)) < 0.06), 0, 1)
    falha = cv2.GaussianBlur(falha.astype(np.float32), (0, 0), 0.6)
    a = cv2.GaussianBlur(m, (0, 0), 0.55) * pres * falha
    rgb = np.zeros((h, w, 3), np.float32)
    rgb[...] = cor
    # tinta acumulada nas bordas do traço (um pouco mais escura)
    borda = np.clip(m - cv2.GaussianBlur(m, (0, 0), 1.2), 0, 1)
    rgb *= (1 - 0.35 * borda)[..., None]
    out = np.dstack([rgb, np.clip(a * 255 * 0.93, 0, 255)]).astype(np.uint8)
    return Image.fromarray(out), larg, alt


def multiplica(base, sp, x, y, alpha=1.0):
    """Aplica sp sobre base em modo multiplicar (tinta/grafite), respeitando o alfa."""
    x, y = int(x), int(y)
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(base.width, x + sp.width), min(base.height, y + sp.height)
    if x1 <= x0 or y1 <= y0:
        return
    b = np.asarray(base.crop((x0, y0, x1, y1))).astype(np.float32)
    s_ = np.asarray(sp.crop((x0 - x, y0 - y, x1 - x, y1 - y))).astype(np.float32)
    a = s_[..., 3:4] / 255 * alpha
    mult = b[..., :3] * (s_[..., :3] / 255)
    b[..., :3] = b[..., :3] * (1 - a) + mult * a
    base.paste(Image.fromarray(np.clip(b, 0, 255).astype(np.uint8)), (x0, y0))
