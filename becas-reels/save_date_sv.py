#!/usr/bin/env python3
"""SAVE THE DATE — MISTÉRIO, com a cara da SUA VEZ (6/nov/2026). Ele: "tá muito na temática do café; quero algo da Sua
Vez, SEM tarde de jogos, sem nada, pra fazer mistério; a novidade sai no sábado (daqui a 2 dias); fique ligado que vem
coisa boa". (O `save_date.py` com guarda-chuvinhas ficou como versão anterior.)

10 s, identidade da Jéssica: azul-claro com trilha de casas, "?" claros flutuando, logo. Uma CARTA DE JOGO virada (verso
petróleo com "?" amarelo) treme, vira e mostra "20 · NOVEMBRO · ANOTA AÍ!" (a única informação). Depois: "SAVE THE
DATE!", "VEM COISA BOA POR AÍ...", "SÁBADO, AO MEIO-DIA, A GENTE CONTA TUDO!" e "fica ligado: ativa o lembrete" + seta.
Área y≈1630–1800 LIVRE para o adesivo de contagem regressiva do Instagram.

    /usr/bin/python3 save_date_sv.py --frame 0.6 1.6 6
    /usr/bin/python3 save_date_sv.py      # out/save_sv_{com_som,para_musica}_final.mp4
"""
import math
import os
import random
import sys
from functools import lru_cache

from PIL import Image, ImageDraw

import kit as K
import sons as S
import tarde as T
from tarde import E, W, H, MAR, PET, LAR, AMA, BR, ROSA

from motor import FPS, out_back  # noqa: E402

OUT = T.OUT
DUR = 10.0
AZUL = (227, 243, 246)
CW_, CH_ = 470, 640  # carta
CY = 985
T_VIRA = (1.25, 1.75)


@lru_cache(None)
def fundo():
    img = Image.new("RGBA", (W, H), AZUL + (255,))
    d = ImageDraw.Draw(img)
    # trilha de casas atravessando a tela (cara de tabuleiro)
    pts = [(W * (0.5 + 0.45 * math.sin(y / 300 + 0.6)), y) for y in range(-60, H + 120, 4)]
    cores = [LAR, PET, AMA, ROSA]
    acc, k = 0.0, 0
    for i in range(1, len(pts)):
        acc += math.dist(pts[i], pts[i - 1])
        if acc >= 120:
            acc = 0
            x, y = pts[i]
            c = tuple(int(v + (255 - v) * 0.55) for v in cores[k % 4])
            d.rounded_rectangle((x - 40, y - 40, x + 40, y + 40), 14, fill=c)
            k += 1
    return img


@lru_cache(None)
def interrogacoes():
    rnd = random.Random(8)
    return [(rnd.uniform(60, W - 60), rnd.uniform(380, 1600), rnd.uniform(60, 120), rnd.uniform(0, 6.28),
             rnd.choice([PET, LAR, ROSA])) for _ in range(9)]


def flutua(img, t):
    for x, y, s, f, cor in interrogacoes():
        c = tuple(int(v + (255 - v) * 0.6) for v in cor)
        q = E.titulo("?", int(s), c, contorno=tuple(int(v + (255 - v) * 0.5) for v in MAR), sw=4, sombra=0)
        E.cola(img, q, x, y + 14 * math.sin(t * 1.3 + f), 12 * math.sin(f))


@lru_cache(None)
def verso():
    im = Image.new("RGBA", (CW_ + 16, CH_ + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((14, 14, CW_ + 14, CH_ + 14), 44, fill=MAR)
    d.rounded_rectangle((0, 0, CW_, CH_), 44, fill=PET, outline=MAR, width=8)
    d.rounded_rectangle((26, 26, CW_ - 26, CH_ - 26), 30, outline=(90, 175, 200), width=5)
    lis = Image.new("RGBA", (CW_, CH_), (0, 0, 0, 0))  # listras finas do verso, só dentro da carta
    dl = ImageDraw.Draw(lis)
    for i in range(-CH_, CW_, 46):
        dl.line((i, 0, i + CH_, CH_), fill=(36, 138, 164, 255), width=10)
    m = Image.new("L", (CW_, CH_), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, CW_ - 1, CH_ - 1), 44, fill=255)
    lis.putalpha(Image.fromarray(__import__("numpy").minimum(__import__("numpy").asarray(lis.getchannel("A")),
                                                               __import__("numpy").asarray(m))))
    im.alpha_composite(lis)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((26, 26, CW_ - 26, CH_ - 26), 30, outline=(90, 175, 200), width=5)
    d.rounded_rectangle((0, 0, CW_, CH_), 44, outline=MAR, width=8)
    q = E.titulo("?", 330, AMA, sw=12)
    im.alpha_composite(q, (int(CW_ / 2 - q.width / 2), int(CH_ / 2 - q.height / 2)))
    return im


@lru_cache(None)
def frente():
    im = Image.new("RGBA", (CW_ + 16, CH_ + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((14, 14, CW_ + 14, CH_ + 14), 44, fill=MAR)
    d.rounded_rectangle((0, 0, CW_, CH_), 44, fill=(255, 250, 240), outline=MAR, width=8)
    d.rounded_rectangle((26, 26, CW_ - 26, CH_ - 26), 30, outline=(240, 200, 150), width=5)
    d.text((CW_ / 2, 115), "NOVEMBRO", font=E.lilita(64), fill=PET, anchor="mm")
    n = E.titulo("20", 250, LAR, sw=9)
    im.alpha_composite(n, (int(CW_ / 2 - n.width / 2), int(320 - n.height / 2)))
    p = E.pilula("ANOTA AÍ!", 50, AMA, MAR, fonte_titulo=True)
    E.cola(im, p, CW_ / 2, 530, -2)
    return im


def carta(img, t):
    if t < 0.0:
        return
    entra = min(1.0, t / 0.5)
    y = CY + (1 - out_back(entra, 1.3)) * 1300
    treme = 4 * math.sin(t * 40) * max(0, min(1, (t - 0.5) / 0.2)) if t < T_VIRA[0] else 0
    if t < T_VIRA[0]:
        face, sx = verso(), 1.0
    elif t < T_VIRA[1]:
        u = (t - T_VIRA[0]) / (T_VIRA[1] - T_VIRA[0])
        sx = abs(math.cos(math.pi * u))
        face = verso() if u < 0.5 else frente()
    else:
        face, sx = frente(), 1.0
    rot = treme + (2.5 * math.sin(t * 1.1) if t > T_VIRA[1] else 0)
    if sx < 0.999:
        face = face.resize((max(2, int(face.width * sx)), face.height), Image.BICUBIC)
    E.cola(img, face, W / 2, y, rot)


@lru_cache(None)
def seta_baixo():
    im = Image.new("RGBA", (90, 110), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.line((45, 5, 45, 80), fill=MAR, width=12)
    d.polygon([(10, 62), (80, 62), (45, 105)], fill=MAR)
    return im


def quadro(t):
    img = fundo().copy()
    flutua(img, t)
    T.poe(img, T.logo(230), W / 2, 330, t, 0.1)
    carta(img, t)
    T.poe(img, T.titulo("SAVE THE DATE!", 135, LAR), W / 2, 515, t, 1.9, -2)
    T.poe(img, E.pilula("VEM COISA BOA POR AÍ...", 52, PET, BR, fonte_titulo=True), W / 2, 1395, t, 2.4, 1.5)
    T.poe(img, E.pilula("SÁBADO, AO MEIO-DIA, A GENTE CONTA TUDO!", 36, AMA, MAR, fonte_titulo=True), W / 2, 1480, t,
          2.8, -1)
    if t > 3.3:
        a = min(1, (t - 3.3) / 0.3)
        bob = 8 * math.sin(2 * math.pi * (t - 3.3) / 1.2)
        txt = Image.new("RGBA", (W, 130), (0, 0, 0, 0))
        dt = ImageDraw.Draw(txt)
        dt.text((W / 2 - 60, 45), "fica ligado: ativa o lembrete", font=E.fig(40, 900), fill=MAR, anchor="mm")
        txt.alpha_composite(seta_baixo(), (int(W / 2 + 270), int(bob)))
        if a < 1:
            txt.putalpha(txt.getchannel("A").point(lambda v: int(v * a)))
        img.alpha_composite(txt, (0, 1525))
    return img.convert("RGB")


def render(fi):
    return quadro(fi / FPS).tobytes()


def audio():
    ev = [(0.1, S.cartao(), 0.4), (0.55, S.dado(), 0.35), (T_VIRA[0], S.carta_vira(), 0.7),
          (T_VIRA[1], S.plim(), 0.5), (1.9, S.sino(), 0.35), (2.4, S.cartao(), 0.35), (2.8, S.cartao(), 0.35),
          (3.3, S.sino(), 0.3)]
    mus = S.musica_marimba_pop(DUR + 0.5)
    com = os.path.join(OUT, "save_sv_com.wav")
    sem = os.path.join(OUT, "save_sv_sem.wav")
    S.grava(com, DUR, ev, mus, musica_ganho=0.42, fx_ganho=0.8)
    S.grava(sem, DUR, ev, None, fx_ganho=0.8)
    return com, sem


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:]]
        K.folha([quadro(x) for x in ts], os.path.join(OUT, "frames_save_sv.jpg"))
        print("ok")
        return
    com, sem = audio()
    K.entrega("save_sv", DUR, render, com, sem)
    print("ok")


if __name__ == "__main__":
    main()
