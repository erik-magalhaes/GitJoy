#!/usr/bin/env python3
"""Carrossel "SEU SIGNO, SEU JOGO" (12/nov/2026), 2º da série do "Seu mês, seu jogo" (mesmo visual, importa seu_mes):
bichinhos que ELES fizeram no Gemini (folha 4x3, na ordem dos signos, ampliada 4x com Real-ESRGAN →
assets/seu_signo/gemini_signos_x4.png), frase do signo, caixa do jogo no canto. 1080x1350 + Stories 1080x1920.

    python3 seu_signo.py   # out/seu_signo/01..14.png + stories/ + out/seu_signo_previa.jpg
"""
import os
import random

import numpy as np
from PIL import Image

import seu_mes as SM
from seu_mes import W, H, E, letra, caixa, bicho, selo, papel

ROOT = os.path.dirname(os.path.abspath(__file__))
SM.GEMINI = os.path.join(ROOT, "assets", "seu_signo", "gemini_signos_x4.png")
SM.FUNDO_GEMINI = np.array([245, 237, 214], float)

SIGNOS = [  # (signo, datas, frase, jogo, recorte, fundo pastel)
    ("ÁRIES", "21/3 a 19/4", "CHEGA CHUTANDO A PORTA\nE JÁ QUER DESTRUIR TÓQUIO", "King of Tokyo", "king_of_tokyo",
     (250, 210, 200)),
    ("TOURO", "20/4 a 20/5", "SÓ SAI DO SOSSEGO SE\nA PAISAGEM FOR BONITA", "Harmonies", "harmonies", (220, 236, 206)),
    ("GÊMEOS", "21/5 a 20/6", "FALA TUDO EM DOBRO\n(E AO MESMO TEMPO)", "Dobro", "dobro", (252, 232, 190)),
    ("CÂNCER", "21/6 a 22/7", "CASEIRO DEMAIS:\nNÃO SAI DA CONCHA", "Sea Salt & Paper", "sea_salt_paper",
     (204, 230, 236)),
    ("LEÃO", "23/7 a 22/8", "NASCEU PRO PALCO:\nQUER TODO MUNDO OLHANDO", "Say my Name", "say_my_name",
     (252, 222, 186)),
    ("VIRGEM", "23/8 a 22/9", "TUDO ALINHADINHO,\nNEM UM AZULEJO TORTO", "Azul Duel", "azul_duel", (214, 222, 244)),
    ("LIBRA", "23/9 a 22/10", "ARTISTA QUE NÃO CONSEGUE\nESCOLHER ENTRE DUAS CORES", "Canvas", "canvas",
     (246, 210, 226)),
    ("ESCORPIÃO", "23/10 a 21/11", "MISTERIOSO QUE JÁ\nSABE O SEU SEGREDO", "Spyfall", "spyfall", (222, 212, 236)),
    ("SAGITÁRIO", "22/11 a 21/12", "MOCHILEIRO QUE NEM VOLTOU\nE JÁ QUER OUTRO PAÍS", "Passaporte Mundo",
     "passaporte_mundo", (236, 228, 200)),
    ("CAPRICÓRNIO", "22/12 a 19/1", "WORKAHOLIC CONSTRUINDO\nMARAVILHA ATÉ NO DOMINGO", "7 Wonders Duel",
     "7_wonders_duel", (232, 222, 210)),
    ("AQUÁRIO", "20/1 a 18/2", "DIFERENTÃO QUE VEIO\nDE OUTRA GALÁXIA", "Sideral", "sideral_fus_o_gal_ctica",
     (212, 236, 230)),
    ("PEIXES", "19/2 a 20/3", "SONHADOR QUE VIVE\nNO MUNDO DA LUA", "Dixit", "dixit", (206, 220, 244)),
]


def tela_signo(k):
    sig, datas, frase, jogo, rec, cor = SIGNOS[k]
    img = papel(cor, k + 31)
    letra(img, sig, 110, W / 2, 150, semente=k)
    letra(img, datas, 46, W / 2, 250, (90, 70, 70), sw=1, semente=k + 20)
    b = bicho(k, 540)
    if b.width > 860:
        b = b.resize((860, int(b.height * 860 / b.width)), Image.LANCZOS)
    if k == 4:  # o facho do holofote do Leão foi cortado reto no topo da célula: some aos poucos
        a = np.asarray(b.getchannel("A"), float)
        n = int(b.height * 0.22)
        a[:n] *= np.linspace(0, 1, n)[:, None]
        b.putalpha(Image.fromarray(a.astype(np.uint8)))
    img.alpha_composite(b, (int(W / 2 - b.width / 2), int(600 - b.height / 2)))
    letra(img, frase, 66, W / 2, 968, semente=k + 50)
    cx = caixa(rec, 255, 270)
    x0 = int(W - 30 - cx.width)
    img.alpha_composite(cx, (x0, int(H + 30 - cx.height)))
    letra(img, "jogo: " + jogo, 40, (200 + x0 + 40) / 2, 1205, (80, 70, 70), sw=1, semente=k + 90)
    selo(img, 34, H - 128, 150)
    return img


def tela_capa():
    img = papel((250, 226, 196), 199)
    letra(img, "SEU SIGNO,\nSEU JOGO", 124, W / 2, 610, semente=17)
    letra(img, "(qual é o seu?)", 60, W / 2, 800, (90, 70, 70), sw=2, semente=18)
    pos = [(170, 175), (430, 150), (690, 160), (930, 230), (950, 520), (960, 820), (900, 1120), (640, 1180),
           (380, 1190), (140, 1110), (120, 820), (130, 500)]
    for k, (x, y) in enumerate(pos):
        cx = bicho(k, 210)
        if cx.width > 240:
            cx = cx.resize((240, int(cx.height * 240 / cx.width)), Image.LANCZOS)
        cx = cx.rotate(random.Random(k).uniform(-6, 6), expand=True, resample=Image.BICUBIC)
        img.alpha_composite(cx, (int(x - cx.width / 2), int(y - cx.height / 2)))
    selo(img, W / 2 - 85, 905, 170)
    return img


def tela_final():
    img = papel((222, 212, 236), 177)
    letra(img, "E AÍ,\nQUAL É O SEU SIGNO?", 96, W / 2, 380, semente=13)
    letra(img, "comenta aqui\ne marca quem é do seu signo!", 58, W / 2, 640, (90, 70, 70), sw=2, semente=14)
    lg = E.logo(330)
    img.alpha_composite(lg, (int(W / 2 - lg.width / 2), 820))
    letra(img, "ALUGA O SEU NA SUA VEZ\nO LINK TÁ NA BIO", 56, W / 2, 1150, semente=15)
    return img


def story_de(tela, ultimo=False):
    """Story 1080x1920: a tela no meio (y 285–1635) sobre o mesmo papel estendido; o último tem o espaço do link."""
    cor = tuple(int(v) for v in np.asarray(tela.convert("RGB")).reshape(-1, 3)[:2000].mean(0))
    SM.H = 1920
    try:
        fundo = papel(cor, 5)
    finally:
        SM.H = H
    if ultimo:
        # a tela sobe e o meio de baixo fica livre para o adesivo de link
        t = tela.crop((0, 0, W, 1090))
        fundo.alpha_composite(t, (0, 200))
        letra(fundo, "aluga aqui:", 64, W / 2, 1340, semente=3)
        from PIL import ImageDraw
        dr = ImageDraw.Draw(fundo)
        dr.line([(W / 2, 1395), (W / 2, 1470)], fill=SM.TINTA, width=10)
        dr.polygon([(W / 2 - 30, 1455), (W / 2 + 30, 1455), (W / 2, 1500)], fill=SM.TINTA)
    else:
        fundo.alpha_composite(tela, (0, 285))
    return fundo


def main():
    d = os.path.join(ROOT, "out", "seu_signo")
    os.makedirs(os.path.join(d, "stories"), exist_ok=True)
    telas = [tela_capa()] + [tela_signo(k) for k in range(12)] + [tela_final()]
    for k, im in enumerate(telas, 1):
        im.convert("RGB").save(os.path.join(d, f"{k:02d}.png"))
        story_de(im, k == len(telas)).convert("RGB").save(os.path.join(d, "stories", f"story_{k:02d}.png"))
    sh = Image.new("RGB", (7 * 330 + 10, 2 * 420 + 10), (255, 255, 255))
    for k, im in enumerate(telas):
        sh.paste(im.convert("RGB").resize((320, 400), Image.LANCZOS), (10 + (k % 7) * 330, 10 + (k // 7) * 420))
    sh.save(os.path.join(ROOT, "out", "seu_signo_previa.jpg"), quality=90)
    print("ok", len(telas))


if __name__ == "__main__":
    main()
