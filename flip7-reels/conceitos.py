#!/usr/bin/env python3
"""3 visuais para o vídeo de explicação do FLIP 7: A VINGANÇA (28/out/2026), lado a lado, no mesmo momento do jogo
(a linha com 6 números diferentes e a 7ª carta virando):
  1 AUDITÓRIO ANOS 70: na estética da própria caixa (creme, azul, leque arco-íris, letras Bungee), palco de programa de
    TV com lâmpadas, placar de luz e o "VIRA OU PARA?";
  2 FLIPERAMA 8-BIT: tela de arcade com scanlines, letras pixeladas, SCORE / HI 200, "GAME OVER" quando estoura;
  3 MESA DE CASSINO: feltro verde, fichas, cartas pousadas com sombra, letreiro neon "ESTOUROU?".

    python3 conceitos.py      # out/conceitos.jpg
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "comum"))
from motor import logo_card, cola  # noqa: E402
from cartas import numero, verso, acao, fonte, CREME, MARINHO, CW, CH  # noqa: E402

W, H = 1080, 1920
OUT = os.path.join(ROOT, "out")
CAIXA = os.path.join(ROOT, "assets", "orig", "846730d3bbea4e71b22999497cb442d6-4yjqzi4dnf.png")
LINHA = [3, 8, 11, 5, 12, 1]  # 6 números diferentes já na mesa; a 7ª vira agora
AZUL = (40, 86, 168)
ARCO = [(236, 104, 84), (246, 170, 60), (250, 214, 80), (104, 186, 140), (100, 176, 220), (176, 140, 214)]


def txt(img, s, xy, f, tam, cor, contorno=None, sw=0, anchor="mm", sombra=0):
    d = ImageDraw.Draw(img)
    if sombra:
        d.text((xy[0] + sombra, xy[1] + sombra), s, font=fonte(f, tam), fill=contorno, anchor=anchor, stroke_width=sw,
               stroke_fill=contorno)
    d.text(xy, s, font=fonte(f, tam), fill=cor, anchor=anchor, stroke_width=sw, stroke_fill=contorno)


def linha_cartas(img, y, esc=0.55, girar=True, sombra=True, pix=0):
    cw = CW * esc
    xs = [W / 2 + (k - 2.5) * (cw * 0.98) for k in range(6)]
    for k, n in enumerate(LINHA):
        c = numero(n, esc)
        if pix:
            c = c.resize((c.width // pix, c.height // pix), Image.NEAREST).resize(c.size, Image.NEAREST)
        if sombra:
            sh = Image.new("RGBA", c.size, (0, 0, 0, 0))
            sh.putalpha(c.getchannel("A").point(lambda v: int(v * 0.45)))
            sh = sh.filter(ImageFilter.GaussianBlur(8))
            cola(img, sh, xs[k] + 10, y + 14, rot=(k - 2.5) * 1.5 if girar else 0)
        cola(img, c, xs[k], y, rot=(k - 2.5) * 1.5 if girar else 0)


def virando(img, x, y, esc=0.9, pix=0):
    """A 7ª carta no meio do giro (meio verso, meio frente)."""
    c = numero(13, esc)
    c = c.resize((int(c.width * 0.55), c.height))
    if pix:
        c = c.resize((c.width // pix, c.height // pix), Image.NEAREST).resize(c.size, Image.NEAREST)
    cola(img, c, x, y, rot=-8)


def conceito_auditorio():
    img = Image.new("RGBA", (W, H), AZUL + (255,))
    d = ImageDraw.Draw(img)
    cx, cy = W / 2, 760
    for k in range(24):  # raios creme e azul-claro
        a0, a1 = 2 * math.pi * k / 24, 2 * math.pi * (k + 0.5) / 24
        d.polygon([(cx, cy), (cx + 2400 * math.cos(a0), cy + 2400 * math.sin(a0)),
                   (cx + 2400 * math.cos(a1), cy + 2400 * math.sin(a1))], fill=(56, 106, 186))
    for y in range(0, H, 26):  # meio-tom no rodapé
        for x in range(0 + (13 if (y // 26) % 2 else 0), W, 26):
            r = max(0, (y - 1300) / 620) * 8
            if r > 0.5:
                d.ellipse((x - r, y - r, x + r, y + r), fill=(30, 66, 140))
    for k, c in enumerate(ARCO):  # leque arco-íris gigante atrás do título
        a = math.radians(-62 + k * 25)
        leq = Image.new("RGBA", (230, 360), (0, 0, 0, 0))
        ImageDraw.Draw(leq).rounded_rectangle((0, 0, 229, 359), radius=30, fill=c, outline=MARINHO, width=8)
        leq = leq.rotate(-math.degrees(a), expand=True, resample=Image.BICUBIC)
        img.alpha_composite(leq, (int(cx + math.sin(a) * 200 - leq.width / 2), int(420 - math.cos(a) * 90 - leq.height / 2)))
    # letreiro com lâmpadas
    d.rounded_rectangle((90, 520, W - 90, 760), radius=40, fill=CREME, outline=MARINHO, width=10)
    for k in range(18):
        x = 120 + k * (W - 240) / 17
        for y in (540, 740):
            d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=(255, 220, 110), outline=(200, 130, 40), width=3)
    txt(img, "VIRA OU PARA?", (W / 2, 640), "Bungee-Regular.ttf", 104, (232, 90, 70), MARINHO, 5, sombra=7)
    # balcão do programa com a linha de cartas
    d.rounded_rectangle((40, 1080, W - 40, 1500), radius=46, fill=(246, 237, 214), outline=MARINHO, width=10)
    d.rectangle((40, 1400, W - 40, 1500), fill=(232, 90, 70))
    d.line((40, 1400, W - 40, 1400), fill=MARINHO, width=8)
    linha_cartas(img, 1240)
    virando(img, W / 2 + 330, 960)
    txt(img, "VOCÊ", (W / 2, 1450), "Bungee-Regular.ttf", 54, CREME, MARINHO, 3)
    # placar de luz
    d.rounded_rectangle((300, 1560, W - 300, 1700), radius=24, fill=(20, 26, 50), outline=(250, 214, 80), width=6)
    txt(img, "087 / 200", (W / 2, 1632), "Bungee-Regular.ttf", 70, (255, 120, 90))
    img.alpha_composite(logo_card(150), (W - 186, 46))
    return img


def scanlines(img):
    a = np.asarray(img).astype(float)
    a[::4, :, :3] *= 0.55
    yy, xx = np.mgrid[0:H, 0:W]
    v = 1 - 0.55 * (((xx - W / 2) / (W / 2)) ** 2 * 0.6 + ((yy - H / 2) / (H / 2)) ** 2 * 0.5)
    a[..., :3] *= np.clip(v, 0.3, 1)[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def conceito_arcade():
    img = Image.new("RGBA", (W, H), (10, 8, 26, 255))
    d = ImageDraw.Draw(img)
    for y in range(1100, H, 60):  # chão quadriculado em perspectiva (synthwave)
        d.line((0, y, W, y), fill=(120, 40, 160), width=3)
    for k in range(-12, 13):
        d.line((W / 2 + k * 40, 1100, W / 2 + k * 260, H), fill=(120, 40, 160), width=3)
    d.rectangle((30, 30, W - 30, H - 30), outline=(60, 240, 255), width=8)
    txt(img, "1UP", (90, 140), "PressStart2P-Regular.ttf", 40, (255, 70, 120), anchor="lm")
    txt(img, "SCORE 000087", (90, 200), "PressStart2P-Regular.ttf", 40, (255, 255, 255), anchor="lm")
    txt(img, "HI 200", (W - 90, 200), "PressStart2P-Regular.ttf", 40, (255, 220, 80), anchor="rm")
    txt(img, "FLIP 7", (W / 2, 470), "PressStart2P-Regular.ttf", 130, (255, 220, 80), (255, 70, 120), 0, sombra=10)
    txt(img, "VIRA OU PARA?", (W / 2, 640), "PressStart2P-Regular.ttf", 56, (60, 240, 255))
    linha_cartas(img, 950, esc=0.55, girar=False, sombra=False, pix=5)
    virando(img, W / 2 + 330, 1280, pix=6)
    txt(img, "COMBO x6", (W / 2 - 120, 1260), "PressStart2P-Regular.ttf", 48, (120, 255, 120))
    txt(img, "GAME OVER?", (W / 2, 1520), "PressStart2P-Regular.ttf", 62, (255, 70, 120), (60, 0, 20), 0, sombra=8)
    txt(img, "PRESS FLIP", (W / 2, 1680), "PressStart2P-Regular.ttf", 40, (255, 255, 255))
    img = scanlines(img).convert("RGBA")
    img.alpha_composite(logo_card(150), (W - 186, 260))
    return img


def conceito_cassino():
    rng = np.random.default_rng(2)
    a = np.ones((H, W, 3)) * np.array([22, 104, 62], float) + rng.normal(0, 6, (H, W, 1))
    yy, xx = np.mgrid[0:H, 0:W]
    v = 1 - 0.6 * (((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - 1050) / (H * 0.55)) ** 2)
    a *= np.clip(v, 0.25, 1)[..., None]
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.arc((-200, 620, W + 200, 2400), 200, 340, fill=(220, 180, 80), width=6)  # friso dourado da mesa
    txt(img, "FLIP 7 PAGA +15", (W / 2, 760), "Bungee-Regular.ttf", 52, (230, 196, 100))
    # neon
    base = Image.new("L", (W, 360), 0)
    ImageDraw.Draw(base).text((W / 2, 180), "ESTOUROU?", font=fonte("Bungee-Regular.ttf", 140), fill=255, anchor="mm")
    for r, al in ((24, 0.6), (10, 0.9)):
        lay = Image.new("RGBA", (W, 360), (255, 50, 80, 0))
        lay.putalpha(base.filter(ImageFilter.GaussianBlur(r)).point(lambda p, al=al: int(min(255, p * al * 1.7))))
        img.alpha_composite(lay, (0, 220))
    nuc = Image.new("RGBA", (W, 360), (255, 226, 230, 0))
    nuc.putalpha(base)
    img.alpha_composite(nuc, (0, 220))
    linha_cartas(img, 1150)
    virando(img, W / 2 + 330, 900)
    for k, (x, y, cor) in enumerate([(200, 1520, (214, 50, 50)), (330, 1560, (30, 30, 30)), (780, 1530, (40, 90, 200)),
                                     (900, 1570, (240, 240, 240))]):  # fichas
        for j in range(5):
            d.ellipse((x - 70, y - j * 14 - 26, x + 70, y - j * 14 + 26), fill=cor, outline=(250, 250, 250), width=5)
    cola(img, Image.open(CAIXA).convert("RGBA").resize((260, 260)), W / 2, 1600)
    img.alpha_composite(logo_card(150), (W - 186, 46))
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    ims = [conceito_auditorio(), conceito_arcade(), conceito_cassino()]
    nomes = ["1 · AUDITÓRIO ANOS 70", "2 · FLIPERAMA 8-BIT", "3 · MESA DE CASSINO"]
    sh = Image.new("RGB", (3 * 560 + 40, 1060), (255, 255, 255))
    d = ImageDraw.Draw(sh)
    for k, (im, n) in enumerate(zip(ims, nomes)):
        sh.paste(im.convert("RGB").resize((540, 960), Image.LANCZOS), (20 + k * 560, 80))
        d.text((20 + k * 560 + 270, 40), n, font=fonte("Bungee-Regular.ttf", 34), fill=MARINHO, anchor="mm")
    sh.save(os.path.join(OUT, "conceitos.jpg"), quality=92)
    print("ok")


if __name__ == "__main__":
    main()
