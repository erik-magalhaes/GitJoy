#!/usr/bin/env python3
"""Capa do livro "Três Segredos e um CEO" (romance do Erik), 1600x2400 (proporção 2:3, padrão de e-book/Amazon KDP).

Foto: homem de costas, sem camisa, no escuro (CC0, rawpixel/Wikimedia, ampliada 4x com Real-ESRGAN).
Visual: noir quente — sombras pretas, pele em vermelho-cobre (o cabelo "cor de fogo" da Helena), título dourado.

    python3 capa.py   → out/capa.png, out/capa.jpg e out/capa_miniatura.jpg
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
FONTES = os.path.join(AQUI, "assets", "fonts")
OUT = os.path.join(AQUI, "out")
W, H = 1600, 2400

CREME = (246, 232, 212)
VERMELHO = (196, 30, 42)
OURO = [(255, 236, 178), (226, 176, 92), (164, 110, 44), (240, 200, 120)]


def fonte(nome, tam, peso=None):
    f = ImageFont.truetype(os.path.join(FONTES, nome), tam)
    if peso:
        try:
            f.set_variation_by_axes([peso])
        except Exception:
            pass
    return f


def foto():
    im = Image.open(os.path.join(AQUI, "assets", "foto_costas.jpg")).convert("RGB")
    # zoom de 18% no corpo (as costas ocupam mais a capa)
    z = 1.18
    im = im.resize((round(W * z), round(im.height * W * z / im.width)), Image.LANCZOS)
    dx = round((im.width - W) * 0.55)
    im = im.crop((dx, 0, dx + W, H))
    a = np.asarray(im).astype(np.float32) / 255
    lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
    # a janela estourada vira luz âmbar de fim de tarde, mais suave
    jan = np.clip((lum - 0.55) / 0.35, 0, 1)
    lum = lum * (1 - 0.45 * jan)
    # gradiente de cor por luminância: preto → vinho → cobre → creme dourado
    pts = np.array([0, 0.08, 0.25, 0.5, 1.0])
    cores = np.array([[4, 2, 3], [34, 6, 10], [120, 34, 26], [214, 120, 72], [255, 222, 170]], np.float32) / 255
    l = np.clip(lum * 1.25, 0, 1)
    out = np.stack([np.interp(l, pts, cores[:, c]) for c in range(3)], -1)
    # um pouco da cor original de volta, para a pele não ficar chapada
    out = out * 0.85 + a * np.array([0.9, 0.6, 0.5]) * 0.15
    # escurece a base (área do título) e as bordas
    y = np.linspace(0, 1, H)[:, None]
    x = np.linspace(-1, 1, W)[None, :]
    base = np.clip((y - 0.42) / 0.3, 0, 1) ** 1.3
    vin = 1 - 0.55 * np.clip(np.sqrt(x ** 2 * 0.8 + (y - 0.35) ** 2 * 1.2) - 0.35, 0, 1)
    out = out * (1 - 0.92 * base[..., None]) * vin[..., None]
    img = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))
    # brilho suave nas luzes (pele e janela)
    luz = img.point(lambda v: max(0, v - 120) * 2).filter(ImageFilter.GaussianBlur(28))
    img = Image.fromarray(np.clip(np.asarray(img, np.int16) + np.asarray(luz, np.int16) * 0.35, 0, 255).astype(np.uint8))
    return img


def brasa(img):
    """Luz vermelha vindo da esquerda (o 'fogo' da Helena) + faíscas."""
    a = np.asarray(img).astype(np.float32)
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.exp(-(((x - 80) / 700) ** 2 + ((y - 1150) / 900) ** 2))
    a += g[..., None] * np.array([150, 20, 25]) * 0.55
    rng = np.random.default_rng(7)
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    fa = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(fa)
    for _ in range(90):
        px, py = rng.uniform(0, W), rng.uniform(900, 2300)
        r = rng.uniform(1.5, 4.5)
        c = (255, int(rng.uniform(90, 170)), 60)
        d.ellipse((px - r, py - r, px + r, py + r), fill=c)
    fa = Image.blend(fa.filter(ImageFilter.GaussianBlur(4)), fa, 0.5)
    return Image.fromarray(np.clip(np.asarray(img, np.int16) + np.asarray(fa, np.int16) * 0.8, 0, 255).astype(np.uint8))


def texto_ouro(img, xy, txt, f, ancora="mm", espaco=0, sombra=True):
    """Texto com degradê dourado, sombra e brilho."""
    m = Image.new("L", img.size)
    d = ImageDraw.Draw(m)
    if espaco:
        larg = sum(d.textlength(c, font=f) for c in txt) + espaco * (len(txt) - 1)
        x0 = xy[0] - larg / 2 if ancora[0] == "m" else xy[0]
        for c in txt:
            d.text((x0, xy[1]), c, font=f, fill=255, anchor="l" + ancora[1])
            x0 += d.textlength(c, font=f) + espaco
    else:
        d.text(xy, txt, font=f, fill=255, anchor=ancora)
    bb = m.getbbox()
    if sombra:
        s = m.filter(ImageFilter.GaussianBlur(14))
        img.paste((0, 0, 0), (0, 0), s.point(lambda v: min(255, v * 2)))
        brilho = m.filter(ImageFilter.GaussianBlur(26)).point(lambda v: v // 3)
        img.paste((230, 120, 60), (0, 0), brilho)
    h = bb[3] - bb[1]
    grad = np.zeros((H, W, 3), np.float32)
    t = np.clip((np.arange(H) - bb[1]) / max(1, h), 0, 1)
    pts = np.linspace(0, 1, len(OURO))
    for c in range(3):
        grad[..., c] = np.interp(t, pts, [o[c] for o in OURO])[:, None]
    img.paste(Image.fromarray(grad.astype(np.uint8)), (0, 0), m)
    return bb


def texto(img, xy, txt, f, cor, ancora="mm", espaco=0, sombra=10):
    m = Image.new("L", img.size)
    d = ImageDraw.Draw(m)
    if espaco:
        larg = sum(d.textlength(c, font=f) for c in txt) + espaco * (len(txt) - 1)
        x0 = xy[0] - larg / 2 if ancora[0] == "m" else xy[0]
        for c in txt:
            d.text((x0, xy[1]), c, font=f, fill=255, anchor="l" + ancora[1])
            x0 += d.textlength(c, font=f) + espaco
    else:
        d.multiline_text(xy, txt, font=f, fill=255, anchor=ancora, spacing=18,
                         align="left" if ancora[0] == "l" else "center")
    if sombra:
        img.paste((0, 0, 0), (0, 0), m.filter(ImageFilter.GaussianBlur(sombra)))
    img.paste(cor, (0, 0), m)
    return m.getbbox()


def capa():
    img = brasa(foto())
    d = ImageDraw.Draw(img)

    # topo: autor
    texto(img, (W / 2, 120), "ISADORA VALENTE", fonte("Cinzel.ttf", 54, 700), CREME, espaco=14)

    # gancho polêmico, à esquerda no escuro
    fi = fonte("PlayfairDisplay-Italic.ttf", 64, 500)
    texto(img, (110, 950), "Uma noite.\nNove meses.\nTrês filhos.", fi, CREME, ancora="la", sombra=12)
    texto(img, (110, 1235), "E agora ele é\no meu chefe.", fonte("PlayfairDisplay-Italic.ttf", 64, 800),
          (255, 92, 80), ancora="la", sombra=12)

    # título
    texto_ouro(img, (W / 2, 1600), "TRÊS SEGREDOS", fonte("Cinzel.ttf", 150, 900), espaco=6)
    texto(img, (W / 2, 1755), "e um", fonte("GreatVibes.ttf", 150), (235, 60, 60), sombra=10)
    texto_ouro(img, (W / 2, 1945), "CEO", fonte("PlayfairDisplay.ttf", 330, 900), espaco=24)

    # filete + frase de efeito
    d.line((W / 2 - 330, 2175, W / 2 - 40, 2175), fill=(200, 150, 80), width=3)
    d.line((W / 2 + 40, 2175, W / 2 + 330, 2175), fill=(200, 150, 80), width=3)
    d.ellipse((W / 2 - 9, 2166, W / 2 + 9, 2184), fill=VERMELHO)
    texto(img, (W / 2, 2250), "Ele quer os filhos. A máfia quer o dinheiro.\nE ela só quer não cair na cama do chefe… de novo.",
          fonte("PlayfairDisplay-Italic.ttf", 42, 400), CREME, sombra=8)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    img = capa()
    img.save(os.path.join(OUT, "capa.png"))
    img.save(os.path.join(OUT, "capa.jpg"), quality=94)
    img.resize((200, 300), Image.LANCZOS).save(os.path.join(OUT, "capa_miniatura.jpg"), quality=92)
    print("ok", os.path.join(OUT, "capa.jpg"))


if __name__ == "__main__":
    main()
