#!/usr/bin/env python3
"""2ª rodada da capa de "Sob as Ordens do Presidente": ele gostou da B (mulher com os dedos nos lábios) e pediu mais
opções. Seis variações em cima da ideia "a boca / o silêncio":

    b1 = a B como estava
    b2 = a mesma foto bem fechada na boca e nos dedos
    b3 = a mesma foto com moldura dourada dupla e o título em cima
    b4 = a mesma foto em dourado/sépia em vez de azul
    b5 = só a boca de batom vermelho, o resto em azul-noite (rawpixel cdeaba58)
    b6 = mulher sentada no escuro (StockSnap 1e29be5f)

    python3 capa_presidente2.py   → out/presidente/capa_b{1..6}.jpg + opcoes2.jpg
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from capa_presidente import FOTOS, H, OUT, VERMELHO, W, cabe
from divulgacao import CREME, fonte, texto, texto_ouro

AZUL = [(2, 3, 8), (12, 18, 38), (60, 76, 112), (150, 162, 190), (172, 182, 206)]
OURO_SEPIA = [(4, 3, 2), (30, 20, 12), (110, 78, 44), (210, 172, 118), (236, 214, 176)]
NOITE = [(2, 3, 8), (8, 14, 34), (40, 58, 100), (170, 176, 200), (226, 228, 236)]


def grade(im, cores, mistura=0.0):
    a = np.asarray(im).astype(np.float32) / 255
    lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
    pts = np.array([0, 0.1, 0.3, 0.62, 1.0])
    c = np.array(cores, np.float32) / 255
    out = np.stack([np.interp(np.clip(lum * 1.15, 0, 1), pts, c[:, k]) for k in range(3)], -1)
    return out * (1 - mistura) + a * mistura


def recorte(nome, cx, cy, zoom):
    im = Image.open(os.path.join(FOTOS, nome)).convert("RGB")
    s = max(H * zoom / im.height, W * zoom / im.width)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x0 = int(np.clip(im.width * cx - W / 2, 0, im.width - W))
    y0 = int(np.clip(im.height * cy - H / 2, 0, im.height - H))
    return im.crop((x0, y0, x0 + W, y0 + H))


def escurece(out, base_de=0.4, topo_ate=0.16, forca_base=0.93):
    y = np.linspace(0, 1, H)[:, None]
    x = np.linspace(-1, 1, W)[None, :]
    base = np.clip((y - base_de) / 0.26, 0, 1) ** 1.1
    topo = np.clip((topo_ate - y) / max(topo_ate, 1e-3), 0, 1)
    vin = 1 - 0.5 * np.clip(np.sqrt(x ** 2 * 0.9 + (y - 0.4) ** 2) - 0.45, 0, 1)
    out = out * (1 - forca_base * base[..., None]) * (1 - 0.75 * topo[..., None]) * vin[..., None]
    img = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))
    luz = img.point(lambda v: max(0, v - 140) * 2).filter(ImageFilter.GaussianBlur(24))
    return Image.fromarray(np.clip(np.asarray(img, np.int16) + np.asarray(luz, np.int16) * 0.3, 0, 255).astype(np.uint8))


def labios_vermelhos():
    """Boca de batom inteira numa faixa, o vermelho original preservado e o resto em azul-noite."""
    im = Image.open(os.path.join(FOTOS, "batom.png")).convert("RGB")
    # recorta só a boca (sem o batom à direita) e espelha para a boca ficar no meio
    im = im.crop((0, int(im.height * 0.08), int(im.width * 0.70), int(im.height * 0.78)))
    larg = W + 200
    im = im.resize((larg, round(im.height * larg / im.width)), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32) / 255
    verm = np.clip((a[..., 0] - np.maximum(a[..., 1], a[..., 2]) - 0.18) / 0.25, 0, 1)
    verm = np.asarray(Image.fromarray((verm * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3)), np.float32)[..., None] / 255
    g = grade(im, [(2, 3, 8), (5, 8, 20), (10, 16, 38), (20, 30, 62), (26, 38, 76)])
    out = g * (1 - verm) + (a * np.array([1.05, 0.85, 0.9])) * verm
    faixa = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))
    fundo = np.zeros((H, W, 3), np.float32) + np.array([4, 6, 14]) / 255
    m = np.ones((faixa.height, faixa.width), np.float32)
    yy = np.linspace(-1, 1, faixa.height)[:, None]
    xx = np.linspace(-1, 1, faixa.width)[None, :]
    m *= np.clip((1 - np.abs(yy)) / 0.35, 0, 1) * np.clip((1 - np.abs(xx)) / 0.2, 0, 1)
    y0 = 250
    fa = np.asarray(faixa, np.float32) / 255
    h = min(faixa.height, H - y0)
    fundo[y0:y0 + h] = fa[:h, 100:100 + W] * m[:h, 100:100 + W, None] + fundo[y0:y0 + h] * (1 - m[:h, 100:100 + W, None])
    return fundo


def titulo(img, topo=False):
    d = ImageDraw.Draw(img)
    if topo:
        texto(img, (W / 2, 200), "E.M. VALENTINE", fonte("Cinzel.ttf", 50, 700), CREME, espaco=14)
        texto_ouro(img, (W / 2, 360), "SOB AS ORDENS", cabe("SOB AS ORDENS", "Cinzel.ttf", 130, 900, W - 300, 6), espaco=6)
        texto(img, (W / 2, 480), "do", fonte("GreatVibes.ttf", 120), VERMELHO, sombra=10)
        texto_ouro(img, (W / 2, 640), "PRESIDENTE", cabe("PRESIDENTE", "PlayfairDisplay.ttf", 210, 900, W - 280, 10), espaco=10)
        texto(img, (W / 2, 1950), "Ninguém diz não ao Presidente.", fonte("PlayfairDisplay-Italic.ttf", 62, 500), CREME, sombra=14)
        texto(img, (W / 2, 2035), "Até ela.", fonte("PlayfairDisplay-Italic.ttf", 68, 800), VERMELHO, sombra=14)
        texto(img, (W / 2, 2190), "DA AUTORA DE TRÊS SEGREDOS E UM CEO", fonte("Cinzel.ttf", 26, 700), (226, 190, 120), espaco=5, sombra=6)
        return
    texto(img, (W / 2, 120), "E.M. VALENTINE", fonte("Cinzel.ttf", 54, 700), CREME, espaco=14)
    texto(img, (W / 2, 190), "DA AUTORA DE TRÊS SEGREDOS E UM CEO", fonte("Cinzel.ttf", 26, 700), (226, 190, 120), espaco=5, sombra=6)
    m = Image.new("L", img.size)
    ImageDraw.Draw(m).ellipse((150, 1170, W - 150, 1410), fill=170)
    img.paste((2, 4, 12), (0, 0), m.filter(ImageFilter.GaussianBlur(60)))
    texto(img, (W / 2, 1250), "Ninguém diz não ao Presidente.", fonte("PlayfairDisplay-Italic.ttf", 66, 500), CREME, sombra=14)
    texto(img, (W / 2, 1335), "Até ela.", fonte("PlayfairDisplay-Italic.ttf", 72, 800), VERMELHO, sombra=14)
    texto_ouro(img, (W / 2, 1600), "SOB AS ORDENS", cabe("SOB AS ORDENS", "Cinzel.ttf", 150, 900, W - 160, 6), espaco=6)
    texto(img, (W / 2, 1745), "do", fonte("GreatVibes.ttf", 140), VERMELHO, sombra=10)
    texto_ouro(img, (W / 2, 1925), "PRESIDENTE", cabe("PRESIDENTE", "PlayfairDisplay.ttf", 240, 900, W - 140, 10), espaco=10)
    d.line((W / 2 - 330, 2130, W / 2 - 40, 2130), fill=(200, 160, 90), width=3)
    d.line((W / 2 + 40, 2130, W / 2 + 330, 2130), fill=(200, 160, 90), width=3)
    d.ellipse((W / 2 - 9, 2121, W / 2 + 9, 2139), fill=(30, 60, 130))
    texto(img, (W / 2, 2225), "Ele manda no país inteiro.\nEla é a única que ele obedece.",
          fonte("PlayfairDisplay-Italic.ttf", 46, 400), CREME, sombra=8)


def moldura(img):
    d = ImageDraw.Draw(img)
    for m, w, c in ((60, 4, (226, 176, 92)), (78, 2, (164, 110, 44))):
        d.rectangle((m, m, W - m, H - m), outline=c, width=w)
    for x, y in ((60, 60), (W - 60, 60), (60, H - 60), (W - 60, H - 60)):
        d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=(196, 30, 42))


def capa(k):
    if k == "b1":
        img = escurece(grade(recorte("labios.png", 0.40, 0.5, 1.0), AZUL))
        titulo(img)
    elif k == "b2":
        img = escurece(grade(recorte("labios.png", 0.58, 0.36, 2.1), AZUL))
        titulo(img)
    elif k == "b3":
        out = grade(recorte("labios.png", 0.45, 0.42, 1.25), AZUL)
        y = np.linspace(0, 1, H)[:, None]
        cima = np.clip((0.36 - y) / 0.16, 0, 1)
        baixo = np.clip((y - 0.72) / 0.12, 0, 1)
        img = escurece(out * (1 - 0.96 * cima[..., None]) * (1 - 0.9 * baixo[..., None]), base_de=2, topo_ate=0)
        moldura(img)
        titulo(img, topo=True)
    elif k == "b4":
        img = escurece(grade(recorte("labios.png", 0.40, 0.5, 1.0), OURO_SEPIA))
        titulo(img)
    elif k == "b5":
        img = escurece(labios_vermelhos(), base_de=0.52, topo_ate=0.1, forca_base=0.6)
        titulo(img)
    elif k == "b6":
        img = escurece(grade(recorte("escuro.png", 0.5, 0.42, 1.0), NOITE), base_de=0.45)
        titulo(img)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    ks = ["b1", "b2", "b3", "b4", "b5", "b6"]
    mini = []
    for k in ks:
        img = capa(k)
        img.save(os.path.join(OUT, f"capa_{k}.jpg"), quality=94)
        mini.append(img.resize((420, 630), Image.LANCZOS))
    folha = Image.new("RGB", (3 * 420 + 4 * 30, 2 * (630 + 90) + 30), (236, 236, 236))
    d = ImageDraw.Draw(folha)
    for i, m in enumerate(mini):
        x, y = 30 + (i % 3) * 450, 30 + (i // 3) * 720
        folha.paste(m, (x, y))
        d.text((x + 210, y + 665), str(i + 1), font=fonte("Cinzel.ttf", 40, 900), fill=(20, 30, 60), anchor="mm")
    folha.save(os.path.join(OUT, "opcoes2.jpg"), quality=92)
    print("ok", OUT)


if __name__ == "__main__":
    main()
