#!/usr/bin/env python3
"""Carrossel "SUA CIDADE, SEU JOGO" (13/nov/2026), 3º da série do "Seu mês, seu jogo" (mesmo visual, importa seu_mes
e seu_signo): 8 bichinhos que ELES fizeram no Gemini (folha 4x2 = as 7 cidades do ABC + São Paulo, ampliada 4x com
Real-ESRGAN → assets/seu_cidade/gemini_cidades_x4.jpg), frase da cidade, caixa do jogo no canto. 1080x1350 + Stories.

    /usr/bin/python3 seu_cidade.py   # out/seu_cidade/01..10.png + stories/ + out/seu_cidade_previa.jpg
"""
import os
import random

import numpy as np
from PIL import Image

import seu_mes as SM
import seu_signo as SS
from seu_mes import W, H, E, letra, caixa, selo, papel

ROOT = os.path.dirname(os.path.abspath(__file__))
SM.GEMINI = os.path.join(ROOT, "assets", "seu_cidade", "gemini_cidades_x4.jpg")

CIDADES = [  # (cidade, frase, jogo, recorte (relativo a hobby-reels/assets/acervo), fundo pastel)
    ("SANTO ANDRÉ", "TRILHEIRO DE PARANAPIACABA:\nNÃO SAI DE CASA SEM MAPA", "Cartographers", "cartographers",
     (220, 236, 214)),
    ("SÃO BERNARDO\nDO CAMPO", "CRIADO NO MEIO DOS MOTORES:\nSÓ PENSA EM CORRIDA", "Heat: Pedal to the Metal",
     "../../../feed-sua-vez/assets/seu_cidade/heat", (214, 226, 240)),
    ("SÃO CAETANO\nDO SUL", "TUDO ARRUMADINHO,\nCADA COISA NO SEU QUADRADO", "Patchwork",
     "../../../roleta-reels/assets/patchwork", (240, 226, 210)),
    ("DIADEMA", "NÃO PARA DE DANÇAR E\nSABE O ANO DE TODA MÚSICA", "Hitster", "hitster", (250, 214, 206)),
    ("MAUÁ", "TERRA DO BARÃO DE MAUÁ:\nNASCEU EM CIMA DOS TRILHOS", "Ticket to Ride", "ticket_to_ride",
     (252, 230, 196)),
    ("RIBEIRÃO PIRES", "SÓ QUER SOSSEGO, MATO\nE UM CHOCOLATINHO", "Savernake Forest", "savernake_forest",
     (236, 222, 206)),
    ("RIO GRANDE\nDA SERRA", "VIVE SUBINDO A SERRA\nATRÁS DE UM TESOURO", "Treasure Island", "treasure_island",
     (212, 234, 226)),
    ("SÃO PAULO", "SEMPRE ATRASADO\nE MORANDO NO METRÔ", "Metro", "metro", (226, 222, 236)),
]


def bicho(k, h):
    """A folha das cidades é 4x2 (a do seu_mes é 4x3): troca o nº de linhas só durante o recorte."""
    orig = SM.bicho.__wrapped__
    import inspect
    src = inspect.getsource(orig).replace("im.shape[0] / 3", "im.shape[0] / 2")
    src = src[src.index("def "):].replace("def bicho(", "def _b(")
    ns = dict(SM.__dict__)
    exec(src, ns)
    return ns["_b"](k, h)


_cache = {}


def bichinho(k, h):
    if (k, h) not in _cache:
        _cache[(k, h)] = bicho(k, h)
    return _cache[(k, h)]


def tela_cidade(k):
    cid, frase, jogo, rec, cor = CIDADES[k]
    img = papel(cor, k + 61)
    duas = "\n" in cid
    letra(img, cid, 96 if duas else 110, W / 2, 175 if duas else 160, semente=k)
    b = bichinho(k, 480)
    if b.width > 820:
        b = b.resize((820, int(b.height * 820 / b.width)), Image.LANCZOS)
    img.alpha_composite(b, (int(W / 2 - b.width / 2), int(580 - b.height / 2)))
    letra(img, frase, 60, W / 2, 900, semente=k + 50)
    cx = caixa(rec, 350, 380)
    x0 = int(W - 5 - cx.width)
    img.alpha_composite(cx, (x0, int(H + 15 - cx.height)))
    letra(img, "jogo: " + jogo, 44, (200 + x0 + 40) / 2, 1215, (80, 70, 70), sw=1, semente=k + 90)
    selo(img, 34, H - 128, 150)
    return img


def tela_capa():
    img = papel((214, 230, 236), 299)
    letra(img, "SUA CIDADE,\nSEU JOGO", 124, W / 2, 610, semente=27)
    letra(img, "(qual é a sua?)", 60, W / 2, 800, (90, 70, 70), sw=2, semente=28)
    pos = [(150, 230), (410, 215), (670, 215), (930, 230), (150, 1110), (410, 1130), (670, 1130), (930, 1110)]
    for k, (x, y) in enumerate(pos):
        cx = bichinho(k, 250)
        if cx.width > 250:
            cx = cx.resize((250, int(cx.height * 250 / cx.width)), Image.LANCZOS)
        cx = cx.rotate(random.Random(k).uniform(-6, 6), expand=True, resample=Image.BICUBIC)
        img.alpha_composite(cx, (int(x - cx.width / 2), int(y - cx.height / 2)))
    selo(img, W / 2 - 85, 905, 170)
    return img


def tela_final():
    img = papel((252, 230, 196), 277)
    letra(img, "E AÍ,\nDE QUE CIDADE VOCÊ É?", 96, W / 2, 380, semente=23)
    letra(img, "comenta aqui\ne marca quem é da sua cidade!", 58, W / 2, 640, (90, 70, 70), sw=2, semente=24)
    lg = E.logo(330)
    img.alpha_composite(lg, (int(W / 2 - lg.width / 2), 820))
    letra(img, "ALUGA O SEU NA SUA VEZ\nO LINK TÁ NA BIO", 56, W / 2, 1150, semente=25)
    return img


def main():
    d = os.path.join(ROOT, "out", "seu_cidade")
    os.makedirs(os.path.join(d, "stories"), exist_ok=True)
    telas = [tela_capa()] + [tela_cidade(k) for k in range(8)] + [tela_final()]
    for k, im in enumerate(telas, 1):
        im.convert("RGB").save(os.path.join(d, f"{k:02d}.png"))
        SS.story_de(im, k == len(telas)).convert("RGB").save(os.path.join(d, "stories", f"story_{k:02d}.png"))
    sh = Image.new("RGB", (5 * 330 + 10, 2 * 420 + 10), (255, 255, 255))
    for k, im in enumerate(telas):
        sh.paste(im.convert("RGB").resize((320, 400), Image.LANCZOS), (10 + (k % 5) * 330, 10 + (k // 5) * 420))
    sh.save(os.path.join(ROOT, "out", "seu_cidade_previa.jpg"), quality=90)
    print("ok", len(telas))


if __name__ == "__main__":
    main()
