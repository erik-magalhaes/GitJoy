#!/usr/bin/env python3
"""2ª rodada de visuais do Flip 7 (28/out/2026). Ele não gostou dos 3 primeiros (conceitos.py) nem das cartas (cartas.py:
"bem diferente das cartas do jogo") e pediu algo ESTILIZADO como o lápis de cor do Taco Gato. Agora as cartas seguem o
desenho REAL (carta_real.py) e o estilo vem por cima (estilos.py): 1 papel recortado, 2 giz na lousa, 3 neon.
Mesmo momento nos 3: 6 números diferentes na linha e a 7ª carta chegando.

    python3 conceitos2.py      # out/conceitos2.jpg
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "comum"))
from motor import logo_card, cola  # noqa: E402
from carta_real import camadas, fonte  # noqa: E402
import estilos  # noqa: E402

W, H = 1080, 1920
OUT = os.path.join(ROOT, "out")
LINHA = [3, 8, 11, 5, 12, 1]


def linha(img, estilo, y, esc, sem=0, rot=True):
    cs = [estilo(camadas(n), esc, sem + k) for k, n in enumerate(LINHA)]
    passo = cs[0].width * 0.86
    for k, c in enumerate(cs):
        cola(img, c, W / 2 + (k - 2.5) * passo, y + (abs(k - 2.5) * 12 if rot else 0), rot=(k - 2.5) * 3 if rot else 0)


def kraft():
    rng = np.random.default_rng(1)
    a = np.ones((H, W, 3)) * np.array([196, 160, 116], float)
    a += cv2_blur(rng.normal(0, 10, (H, W)), 2)[..., None]
    a += (rng.random((H, W)) < 0.01)[..., None] * -30
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


def cv2_blur(x, s):
    import cv2
    return cv2.GaussianBlur(x.astype(np.float32), (0, 0), s)


def letras_papel(txt, s, cores, sem=0):
    """Título de letras recortadas de papel colorido (cada letra de uma cor, um pouco torta)."""
    rng = np.random.default_rng(sem)
    f = fonte("Bungee-Regular.ttf", s)
    ims = []
    for k, ch in enumerate(txt):
        if ch == " ":
            ims.append(None)
            continue
        g = Image.new("RGBA", (int(s * 1.1), int(s * 1.3)), (0, 0, 0, 0))
        d = ImageDraw.Draw(g)
        d.text((g.width / 2 + 6, g.height / 2 + 8), ch, font=f, fill=(60, 40, 20, 110), anchor="mm")
        d.text((g.width / 2, g.height / 2), ch, font=f, fill=cores[k % len(cores)], anchor="mm", stroke_width=6,
               stroke_fill=(250, 246, 236))
        ims.append(g.rotate(rng.uniform(-8, 8), expand=True, resample=Image.BICUBIC))
    w = sum((im.width * 0.72 if im else s * 0.4) for im in ims)
    out = Image.new("RGBA", (int(w + s), int(s * 1.6)), (0, 0, 0, 0))
    x = s / 2
    for im in ims:
        if im is None:
            x += s * 0.4
            continue
        out.alpha_composite(im, (int(x), int(out.height / 2 - im.height / 2 + rng.uniform(-8, 8))))
        x += im.width * 0.72
    return out


def conceito_papel():
    img = kraft()
    cores = [(232, 70, 60), (246, 150, 50), (240, 196, 50), (90, 180, 110), (70, 160, 220), (150, 110, 210)]
    for k, c in enumerate(cores):  # leque de papel gigante atrás do título
        a = math.radians(-60 + k * 24)
        f = Image.new("RGBA", (240, 380), c + (255,))
        f = estilos_papel_peca(f, k)
        f = f.rotate(-math.degrees(a), expand=True, resample=Image.BICUBIC)
        img.alpha_composite(f, (int(W / 2 + math.sin(a) * 210 - f.width / 2), int(420 - math.cos(a) * 100 - f.height / 2)))
    cola(img, letras_papel("VIRA OU PARA?", 84, cores), W / 2, 700)
    linha(img, estilos.papel, 1250, 0.3)
    c7 = estilos.papel(camadas(13, "sortudo", "SORTUDO"), 0.36, 9)
    cola(img, c7, W / 2 + 250, 960, rot=-14)
    cola(img, letras_papel("ESTOUROU?", 90, [(40, 52, 120)]), W / 2, 1640)
    img.alpha_composite(logo_card(150), (W - 186, 46))
    return img


def estilos_papel_peca(im, sem):
    """Um retângulo de cor vira pedaço de papel (borda irregular + sombra)."""
    import cv2
    rng = np.random.default_rng(sem)
    a = np.asarray(im).copy()
    m = a[..., 3] > 0
    m = estilos._borda_irregular(m, rng, 4)
    out = np.zeros((a.shape[0] + 20, a.shape[1] + 20, 4), np.uint8)
    sh = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 6)
    out[14:14 + a.shape[0], 12:12 + a.shape[1], 3] = (sh * 110).astype(np.uint8)
    fib = 1 + 0.05 * cv2.GaussianBlur(rng.normal(0, 1, m.shape).astype(np.float32), (0, 0), 1.2)
    reg = out[:a.shape[0], :a.shape[1]]
    reg[m, :3] = np.clip(a[..., :3] * fib[..., None], 0, 255)[m]
    reg[m, 3] = 255
    return Image.fromarray(out)


def lousa():
    rng = np.random.default_rng(3)
    a = np.ones((H, W, 3)) * np.array([38, 58, 50], float)
    a += cv2_blur(rng.normal(0, 18, (H, W)), 40)[..., None]  # manchas de apagador
    a += rng.normal(0, 4, (H, W, 1))
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 26), fill=(120, 80, 46))
    d.rectangle((0, H - 26, W, H), fill=(120, 80, 46))
    return img


def letras_giz(txt, s, cor, sem=0):
    import cv2
    rng = np.random.default_rng(sem)
    f = ImageFont.truetype(os.path.join(REPO, "taco-reels", "assets", "fonts", "Kalam-Bold.ttf"), s)
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    b = d0.multiline_textbbox((0, 0), txt, font=f, align="center")
    m = Image.new("L", (int(b[2]) + 40, int(b[3]) + 40), 0)
    ImageDraw.Draw(m).multiline_text((20, 20), txt, font=f, fill=255, align="center")
    mm = np.asarray(m) > 127
    tex = estilos._giz_textura(mm.shape, rng)
    a = np.zeros(mm.shape + (4,), np.uint8)
    k = mm & (tex > 0.4)
    a[k, :3] = cor
    a[k, 3] = 240
    return Image.fromarray(a).filter(ImageFilter.GaussianBlur(0.6))


def conceito_giz():
    img = lousa()
    cola(img, letras_giz("Vira ou para?", 150, (250, 246, 230)), W / 2, 330, rot=-3)
    cola(img, letras_giz("(o jogo de cartas\nmais viciante do mundo)", 56, (250, 214, 120)), W / 2, 520, rot=-2)
    linha(img, estilos.giz, 1150, 0.3)
    cola(img, estilos.giz(camadas(13, "sortudo", "SORTUDO"), 0.36, 9), W / 2 + 250, 860, rot=-14)
    seta = letras_giz("repetiu? ESTOUROU!", 70, (255, 150, 140))
    cola(img, seta, W / 2, 1560, rot=-2)
    img.alpha_composite(logo_card(150), (W - 186, 46))
    return img


def parede():
    rng = np.random.default_rng(4)
    a = np.ones((H, W, 3)) * np.array([26, 18, 30], float)
    for j in range(0, H, 70):  # tijolinhos escuros
        off = 70 if (j // 70) % 2 else 0
        for i in range(-off, W, 140):
            a[j + 4:j + 66, max(0, i + 4):max(0, i + 136)] += rng.uniform(4, 14)
    a += rng.normal(0, 3, (H, W, 1))
    yy, xx = np.mgrid[0:H, 0:W]
    a *= np.clip(1 - 0.5 * (((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2) * 2, 0.3, 1)[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


def letreiro_neon(txt, s, cor):
    import cv2
    f = fonte("Monoton-Regular.ttf", s)
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    b = d0.multiline_textbbox((0, 0), txt, font=f, align="center")
    w, h = int(b[2]) + 120, int(b[3]) + 120
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).multiline_text((60, 60), txt, font=f, fill=255, align="center")
    mm = np.asarray(m).astype(np.float32) / 255
    out = np.zeros((h, w, 4), np.float64)
    for sig, al in ((22, 0.5), (7, 0.9)):
        g = cv2.GaussianBlur(mm, (0, 0), sig) * al * 2.4
        out[..., :3] += g[..., None] * np.array(cor)
        out[..., 3] = np.maximum(out[..., 3], np.clip(g * 255, 0, 255))
    out[mm > 0.5, :3] = np.array(cor) * 0.3 + 255 * 0.7
    out[mm > 0.5, 3] = 255
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def conceito_neon():
    img = parede()
    cola(img, letreiro_neon("VIRA OU\nPARA?", 150, (255, 70, 150)), W / 2, 450)
    linha(img, estilos.neon, 1180, 0.3, rot=False)
    cola(img, estilos.neon(camadas(13, "sortudo", "SORTUDO"), 0.36, 9), W / 2 + 250, 880, rot=-14)
    cola(img, letreiro_neon("FLIP 7", 110, (90, 200, 255)), W / 2, 1600)
    img.alpha_composite(logo_card(150), (W - 186, 46))
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    ims = [conceito_papel(), conceito_giz(), conceito_neon()]
    nomes = ["1 · PAPEL RECORTADO", "2 · GIZ NA LOUSA", "3 · NEON"]
    sh = Image.new("RGB", (3 * 560 + 40, 1060), (255, 255, 255))
    d = ImageDraw.Draw(sh)
    for k, (im, n) in enumerate(zip(ims, nomes)):
        sh.paste(im.convert("RGB").resize((540, 960), Image.LANCZOS), (20 + k * 560, 80))
        d.text((20 + k * 560 + 270, 40), n, font=fonte("Bungee-Regular.ttf", 34), fill=(40, 52, 120), anchor="mm")
    sh.save(os.path.join(OUT, "conceitos2.jpg"), quality=92)
    print("ok")


if __name__ == "__main__":
    main()
