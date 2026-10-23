#!/usr/bin/env python3
"""Capa do 2º livro da E.M. Valentine, "Sob as Ordens do Presidente", 1600x2400 (KDP). Três opções para ele escolher.

Visual diferente do 1º livro (noir vinho/cobre): azul-presidencial + dourado, a cor da gravata azul do Augusto.
Fotos CC0 (fontes em assets/presidente/FONTES.txt), ampliadas 4x com Real-ESRGAN:
    a = homem de terno afrouxando a gravata (rawpixel 676354c7)
    b = mulher com os dedos nos lábios, P&B (StockSnap 199b06c6) — ela lê lábios
    c = mãos de terno, anel e relógio (rawpixel 043cad70) — o poder

    python3 capa_presidente.py   → out/presidente/capa_{a,b,c}.jpg + opcoes.jpg
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from divulgacao import CREME, fonte, texto, texto_ouro

AQUI = os.path.dirname(os.path.abspath(__file__))
FOTOS = os.path.join(AQUI, "assets", "presidente")
OUT = os.path.join(AQUI, "out", "presidente")
W, H = 1600, 2400
VERMELHO = (214, 48, 52)

# foto, centro horizontal do recorte (0–1), zoom, cores do degradê (preto → … → claro), mistura com a cor original
OPCOES = {
    "a": ("gravata.png", 0.53, 1.0, [(2, 4, 10), (10, 20, 44), (46, 70, 118), (196, 160, 128), (250, 232, 205)], 0.25),
    "b": ("labios.png", 0.40, 1.0, [(2, 3, 8), (12, 18, 38), (60, 76, 112), (150, 162, 190), (172, 182, 206)], 0.0),
    "c": ("maos.png", 0.42, 1.05, [(2, 4, 10), (8, 16, 40), (34, 58, 112), (200, 160, 110), (252, 230, 190)], 0.3),
}


def foto(nome, cx, zoom, cores, mistura):
    im = Image.open(os.path.join(FOTOS, nome)).convert("RGB")
    s = H * zoom / im.height
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x0 = int(np.clip(im.width * cx - W / 2, 0, im.width - W))
    y0 = (im.height - H) // 2
    im = im.crop((x0, y0, x0 + W, y0 + H))
    a = np.asarray(im).astype(np.float32) / 255
    lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
    pts = np.array([0, 0.1, 0.3, 0.62, 1.0])
    c = np.array(cores, np.float32) / 255
    l = np.clip(lum * 1.15, 0, 1)
    out = np.stack([np.interp(l, pts, c[:, k]) for k in range(3)], -1)
    out = out * (1 - mistura) + a * mistura
    # escurece embaixo (título) e em cima (autor), vinheta nas bordas
    y = np.linspace(0, 1, H)[:, None]
    x = np.linspace(-1, 1, W)[None, :]
    base = np.clip((y - 0.4) / 0.26, 0, 1) ** 1.1
    topo = np.clip((0.16 - y) / 0.16, 0, 1)
    vin = 1 - 0.5 * np.clip(np.sqrt(x ** 2 * 0.9 + (y - 0.4) ** 2) - 0.45, 0, 1)
    out = out * (1 - 0.93 * base[..., None]) * (1 - 0.75 * topo[..., None]) * vin[..., None]
    img = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))
    luz = img.point(lambda v: max(0, v - 140) * 2).filter(ImageFilter.GaussianBlur(24))
    return Image.fromarray(np.clip(np.asarray(img, np.int16) + np.asarray(luz, np.int16) * 0.3, 0, 255).astype(np.uint8))


def cabe(txt, nome, tam, peso, largura, espaco=0):
    """Maior fonte (até tam) em que o texto cabe na largura."""
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    while tam > 20:
        f = fonte(nome, tam, peso)
        if sum(d.textlength(ch, font=f) for ch in txt) + espaco * (len(txt) - 1) <= largura:
            return f
        tam -= 4
    return fonte(nome, tam, peso)


def capa(k):
    nome, cx, zoom, cores, mistura = OPCOES[k]
    img = foto(nome, cx, zoom, cores, mistura)
    d = ImageDraw.Draw(img)

    texto(img, (W / 2, 120), "E.M. VALENTINE", fonte("Cinzel.ttf", 54, 700), CREME, espaco=14)
    texto(img, (W / 2, 190), "DA AUTORA DE TRÊS SEGREDOS E UM CEO", fonte("Cinzel.ttf", 26, 700), (226, 190, 120), espaco=5, sombra=6)

    # gancho, com uma sombra larga atrás para ler em cima da foto
    m = Image.new("L", img.size)
    ImageDraw.Draw(m).ellipse((150, 1170, W - 150, 1410), fill=170)
    img.paste((2, 4, 12), (0, 0), m.filter(ImageFilter.GaussianBlur(60)))
    fi = fonte("PlayfairDisplay-Italic.ttf", 66, 500)
    texto(img, (W / 2, 1250), "Ninguém diz não ao Presidente.", fi, CREME, sombra=14)
    texto(img, (W / 2, 1335), "Até ela.", fonte("PlayfairDisplay-Italic.ttf", 72, 800), VERMELHO, sombra=14)

    # título
    texto_ouro(img, (W / 2, 1600), "SOB AS ORDENS", cabe("SOB AS ORDENS", "Cinzel.ttf", 150, 900, W - 160, 6), espaco=6)
    texto(img, (W / 2, 1745), "do", fonte("GreatVibes.ttf", 140), VERMELHO, sombra=10)
    texto_ouro(img, (W / 2, 1925), "PRESIDENTE", cabe("PRESIDENTE", "PlayfairDisplay.ttf", 240, 900, W - 140, 10), espaco=10)

    d.line((W / 2 - 330, 2130, W / 2 - 40, 2130), fill=(200, 160, 90), width=3)
    d.line((W / 2 + 40, 2130, W / 2 + 330, 2130), fill=(200, 160, 90), width=3)
    d.ellipse((W / 2 - 9, 2121, W / 2 + 9, 2139), fill=(30, 60, 130))
    texto(img, (W / 2, 2225), "Ele manda no país inteiro.\nEla é a única que ele obedece.",
          fonte("PlayfairDisplay-Italic.ttf", 46, 400), CREME, sombra=8)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    mini = []
    for k in OPCOES:
        img = capa(k)
        img.save(os.path.join(OUT, f"capa_{k}.jpg"), quality=94)
        mini.append(img.resize((500, 750), Image.LANCZOS))
    folha = Image.new("RGB", (3 * 500 + 4 * 30, 750 + 120), (236, 236, 236))
    d = ImageDraw.Draw(folha)
    for i, m in enumerate(mini):
        folha.paste(m, (30 + i * 530, 30))
        d.text((30 + i * 530 + 250, 815), "ABC"[i], font=fonte("Cinzel.ttf", 44, 900), fill=(20, 30, 60), anchor="mm")
    folha.save(os.path.join(OUT, "opcoes.jpg"), quality=92)
    print("ok", OUT)


if __name__ == "__main__":
    main()
