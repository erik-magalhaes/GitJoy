#!/usr/bin/env python3
"""Imagem de cada plano para o cadastro de planos do site novo (27/nov/2026): QUADRADA 1080x1080 (recomendado pelo
painel, até 5 MB). Reaproveita o cartão do carrossel das assinaturas (`carrossel.cartao_plano`).

    /usr/bin/python3 imagem_plano.py   # out/planos_site/plano_{silver,gold,platinum}.png
"""
import os
from PIL import Image
import carrossel as C
from estilo import fundo, cola, PLANOS

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out", "planos_site")
os.makedirs(OUT, exist_ok=True)
for i, p in enumerate(PLANOS):
    img = fundo(1080, 1080, 7 + i)
    card = C.cartao_plano(i)
    k = 960 / card.height
    card = card.resize((int(card.width * k), int(card.height * k)), Image.LANCZOS)
    cola(img, card, 540, 540, (-1.0, 1.0, -0.8)[i])
    o = os.path.join(OUT, f"plano_{p[0].lower()}.png")
    img.convert("RGB").save(o, optimize=True)
    print(o, os.path.getsize(o) // 1024, "KB")
