#!/usr/bin/env python3
"""3ª rodada da capa de "Sob as Ordens do Presidente": ele perguntou "não tem algo com casal?". Cinco opções com casal,
no mesmo azul-presidencial + dourado das rodadas anteriores (helpers de capa_presidente2.py):

    c1 = mão dela (com anel) no rosto dele, de terno, beijo em P&B (StockSnap HXDO55F695)
    c2 = beijo com a mão no rosto, terno escuro, a pele um pouco mais quente (rawpixel 11515785)
    c3 = a c1 com moldura dourada e o título em cima
    c4 = pernas: calça de terno e salto vermelho (o vermelho fica, o resto vai pro azul) (rawpixel 5916060)
    c5 = silhuetas se beijando no escuro, na chuva (StockSnap JQBY35SC9K)

    python3 capa_presidente3.py   → out/presidente/capa_c{1..5}.jpg + opcoes3.jpg
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from capa_presidente import H, OUT, W
from capa_presidente2 import AZUL, NOITE, escurece, grade, moldura, recorte, titulo
from divulgacao import fonte


def mantem_vermelho(im, cores, forca=1.0):
    """Degradê azul em tudo, menos no vermelho (o salto), que fica com a cor original."""
    a = np.asarray(im).astype(np.float32) / 255
    verm = np.clip((a[..., 0] - np.maximum(a[..., 1], a[..., 2]) - 0.22) / 0.2, 0, 1)
    verm *= np.linspace(0, 1, a.shape[0])[:, None] > 0.62  # só os sapatos, não a pele
    verm = np.asarray(Image.fromarray((verm * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2)), np.float32)[..., None] / 255
    return grade(im, cores) * (1 - verm) + (a * np.array([1.1, 0.8, 0.85])) * verm * forca


def capa(k):
    if k == "c1":
        img = escurece(grade(recorte("casal_maos.png", 0.58, 0.42, 1.0), AZUL))
        titulo(img)
    elif k == "c2":
        img = escurece(grade(recorte("casal_beijo.png", 0.55, 0.42, 1.0), AZUL, mistura=0.22))
        titulo(img)
    elif k == "c3":
        out = grade(recorte("casal_maos.png", 0.57, 0.30, 1.15), AZUL)
        y = np.linspace(0, 1, H)[:, None]
        cima = np.clip((0.36 - y) / 0.16, 0, 1)
        baixo = np.clip((y - 0.72) / 0.12, 0, 1)
        img = escurece(out * (1 - 0.96 * cima[..., None]) * (1 - 0.9 * baixo[..., None]), base_de=2, topo_ate=0)
        moldura(img)
        titulo(img, topo=True)
    elif k == "c4":
        out = mantem_vermelho(recorte("casal_salto.png", 0.42, 0.62, 1.0), AZUL)
        y = np.linspace(0, 1, H)[:, None]
        cima = np.clip((0.36 - y) / 0.16, 0, 1)
        baixo = np.clip((y - 0.76) / 0.1, 0, 1)
        img = escurece(out * (1 - 0.96 * cima[..., None]) * (1 - 0.9 * baixo[..., None]), base_de=2, topo_ate=0)
        titulo(img, topo=True)
    elif k == "c5":
        img = escurece(grade(recorte("casal_chuva.png", 0.53, 0.6, 1.2), NOITE), base_de=0.56)
        titulo(img)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    ks = ["c1", "c2", "c3", "c4", "c5"]
    mini = []
    for k in ks:
        img = capa(k)
        img.save(os.path.join(OUT, f"capa_{k}.jpg"), quality=94)
        mini.append(img.resize((420, 630), Image.LANCZOS))
    folha = Image.new("RGB", (5 * 420 + 6 * 30, 630 + 120), (236, 236, 236))
    d = ImageDraw.Draw(folha)
    for i, m in enumerate(mini):
        x = 30 + i * 450
        folha.paste(m, (x, 30))
        d.text((x + 210, 700), str(i + 1), font=fonte("Cinzel.ttf", 40, 900), fill=(20, 30, 60), anchor="mm")
    folha.save(os.path.join(OUT, "opcoes3.jpg"), quality=92)
    print("ok", OUT)


if __name__ == "__main__":
    main()
