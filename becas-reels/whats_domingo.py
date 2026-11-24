#!/usr/bin/env python3
"""Imagem do Domingo de Jogos 13/12 para mandar no WHATSAPP (24/nov). Igual ao post do feed, mas sem "link na bio":
no lugar, o endereço do Beca’s e a reserva pelo WhatsApp da loja. 1080x1500 → out/domingo/whatsapp.png
"""
import os

from PIL import Image

import domingo as D
from tarde import E, TB, MAR, PET, AMA, BR


def whatsapp():
    alto = Image.new("RGBA", (1080, 1500))
    alto.alpha_composite(D.fundo(3.0).crop((0, 0, 1080, 1500)))
    post = D.post().convert("RGBA").crop((0, 0, 1080, 1270))  # sem a pílula do link na bio
    alto.alpha_composite(post)
    E.cola(alto, E.pilula("BECA’S CAFÉ · RUA SOROCABA, 35 · MAUÁ", 32, BR, MAR, fonte_titulo=True), 540, 1310, 1, 1, 1)
    E.cola(alto, E.pilula("TEM DESAFIO HITSTER VALENDO PRÊMIO!", 32, AMA, MAR, fonte_titulo=True), 540, 1375, -1, 1, 1)
    E.cola(alto, E.pilula(f"RESERVE PELO WHATSAPP {TB.WHATS}", 36, PET, BR, fonte_titulo=True), 540, 1445, 0, 1, 1)
    return alto.convert("RGB")


if __name__ == "__main__":
    os.makedirs(os.path.join(D.OUT, "domingo"), exist_ok=True)
    p = os.path.join(D.OUT, "domingo", "whatsapp.png")
    whatsapp().save(p)
    print(p)
