#!/usr/bin/env python3
"""Capa do Reels do Azul Mini em 1 minuto (26/nov): foto da Jéssica com a bolsa do Azul (`assets/capa_jessica.jpg`,
mandada no chat) + só uma placa no estilo do jogo embaixo, dentro da área da grade (y 285–1635). → out/capa_azul.png"""
import os

from PIL import Image, ImageOps

import tema as T

ROOT = os.path.dirname(os.path.abspath(__file__))


def capa():
    img = ImageOps.fit(Image.open(os.path.join(ROOT, "assets", "capa_jessica.jpg")).convert("RGBA"), (1080, 1920),
                       Image.LANCZOS)
    p = T.placa("REGRAS EM 1 MINUTO", 78, sub="OU MENOS!")
    p = p.resize((int(p.width * 1.15), int(p.height * 1.15)), Image.LANCZOS)
    img.alpha_composite(p, (540 - p.width // 2, 1440 - p.height // 2))
    return img.convert("RGB")


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    capa().save(os.path.join(ROOT, "out", "capa_azul.png"))
