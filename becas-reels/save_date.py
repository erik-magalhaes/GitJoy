#!/usr/bin/env python3
"""SAVE THE DATE em vídeo para os STORIES (5/nov/2026). Pedido dele: "vídeo pro Stories, Save the Date, dia 20/11; eu
vou colocar aquele contador de tempo do Instagram".

10 s, visual das guarda-chuvinhas (os de `tarde.py` balançando no alto) + um guarda-chuva grande segurando uma FOLHA DE
CALENDÁRIO (20 / NOVEMBRO) que balança como pêndulo (`story_becas.pendulo`); uma caneta vermelha circula o 20. Depois:
logos Sua Vez × Beca’s, "SAVE THE DATE!", tarde de jogos, horário e endereço. A área y≈1610–1790 fica LIVRE para o
adesivo de CONTAGEM REGRESSIVA do Instagram (com "ativa o lembrete" + seta logo acima). Do segundo ~4 em diante tudo
fica parado (só o balanço), para o adesivo ficar legível.

    /usr/bin/python3 save_date.py --frame 0.5 2 4 9     # out/frames_save.jpg
    /usr/bin/python3 save_date.py                       # out/save_date_{com_som,para_musica}_final.mp4
"""
import math
import os
import sys
from functools import lru_cache

from PIL import Image, ImageDraw

import kit as K
import sons as S
import story_becas as SB
import tarde as T
from tarde import E, TB, W, H, MAR, PET, LAR, AMA, BR, ROSA

from motor import FPS  # noqa: E402

OUT = T.OUT
DUR = 10.0
VERM = (214, 48, 49)
CAL_W, CAL_H = 460, 480
W_UMB, FIO = 300, 230
T_CIRC = (1.3, 2.1)  # a caneta circula o 20
KC = 1.3  # escala da folha do calendário


def calendario():
    """Folha de calendário: faixa laranja com argolas, NOVEMBRO, 20 grande, SEXTA · FERIADO."""
    s = 12
    im = Image.new("RGBA", (CAL_W + s + 4, CAL_H + s + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((s, s, s + CAL_W, s + CAL_H), 34, fill=MAR)
    d.rounded_rectangle((0, 0, CAL_W, CAL_H), 34, fill=BR, outline=MAR, width=7)
    d.rounded_rectangle((0, 0, CAL_W, 120), 34, fill=LAR, outline=MAR, width=7)
    d.rectangle((7, 80, CAL_W - 7, 117), fill=LAR)
    d.line((0, 120, CAL_W, 120), fill=MAR, width=7)
    for x in (110, CAL_W - 110):  # argolas
        d.ellipse((x - 16, 20, x + 16, 52), fill=CREME_ESC, outline=MAR, width=5)
    d.text((CAL_W / 2, 88), "NOVEMBRO", font=E.lilita(52), fill=BR, anchor="mm")
    d.text((CAL_W / 2, 270), "20", font=E.lilita(230), fill=LAR, anchor="mm", stroke_width=8, stroke_fill=MAR)
    lg = E.logo(190)  # 6/nov: teaser SEM o nome do café (ele pediu); só o logo da Sua Vez
    lg = lg.resize((int(lg.width * 74 / lg.height), 74), Image.LANCZOS)
    im.alpha_composite(lg, (int(CAL_W / 2 - lg.width / 2), int(428 - lg.height / 2)))
    return im.resize((int(im.width * KC), int(im.height * KC)), Image.LANCZOS)


CREME_ESC = (236, 226, 208)
SB.OBJ["cal"] = calendario


def circulo(u):
    """Traço de caneta vermelha em volta do 20 (u = 0..1 = quanto já foi desenhado), sobre a folha."""
    def f(sp):
        S_ = sp.width
        cx, cy = S_ / 2, S_ / 2
        hx = cx - 0.055 * W_UMB
        top = cy + FIO - 6 + 14 + 0.75 * W_UMB + 2 + 34
        ox, oy = hx - 6 * (KC - 1), top + 270 * KC  # centro do "20"
        d = ImageDraw.Draw(sp)
        n = int(120 * u)
        pts = []
        for k in range(n + 1):
            a = -2.2 + 2 * math.pi * 1.12 * k / 120
            r = 1 + 0.05 * math.sin(3 * a)
            pts.append((ox + 175 * KC * r * math.cos(a), oy + 118 * KC * r * math.sin(a)))
        if len(pts) > 1:
            d.line(pts, fill=VERM, width=13, joint="curve")
    return f


@lru_cache(None)
def seta_baixo():
    im = Image.new("RGBA", (90, 110), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.line((45, 5, 45, 80), fill=MAR, width=12)
    d.polygon([(10, 62), (80, 62), (45, 105)], fill=MAR)
    return im


def quadro(t):
    img = T.fundo().copy()
    T.guarda_chuvas(img, t)
    # calendário pendurado (entra caindo como os guarda-chuvinhas: o fio cresce no começo)
    ang = SB.balanco(t, 3.0, 2.5)
    u = min(1, max(0, (t - T_CIRC[0]) / (T_CIRC[1] - T_CIRC[0])))
    entra = min(1.0, t / 0.6)
    if entra < 1:
        cam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        SB.pendulo(cam, W / 2, ang, W_UMB, ROSA, FIO, "cal", circulo(u) if u > 0 else None)
        img.alpha_composite(cam, (0, int(-(1 - T.out_back(entra, 1.2)) * 900)))
    else:
        SB.pendulo(img, W / 2, ang, W_UMB, ROSA, FIO, "cal", circulo(u) if u > 0 else None)
    T.poe(img, T.titulo("SAVE THE DATE!", 140, LAR), W / 2, 1228, t, 2.2, -2)
    T.poe(img, E.pilula("VEM NOVIDADE POR AÍ...", 50, PET, BR, fonte_titulo=True), W / 2, 1350, t, 2.6, 1)
    T.poe(img, E.pilula("SÁBADO, AO MEIO-DIA,", 42, AMA, MAR, fonte_titulo=True), W / 2, 1428, t, 2.9, -1)
    T.poe(img, E.pilula("A GENTE CONTA TUDO!", 42, AMA, MAR, fonte_titulo=True), W / 2, 1495, t, 3.1, 1)
    if t > 3.4:  # dica do adesivo de contagem regressiva (o adesivo do Instagram vai logo abaixo)
        a = min(1, (t - 3.4) / 0.3)
        bob = 8 * math.sin(2 * math.pi * (t - 3.4) / 1.2)
        d = ImageDraw.Draw(img)
        txt = Image.new("RGBA", (W, 130), (0, 0, 0, 0))
        dt = ImageDraw.Draw(txt)
        dt.text((W / 2 - 60, 45), "ativa o lembrete pra não perder:", font=E.fig(40, 900), fill=MAR, anchor="mm")
        txt.alpha_composite(seta_baixo(), (int(W / 2 + 285), int(0 + bob)))
        if a < 1:
            txt.putalpha(txt.getchannel("A").point(lambda v: int(v * a)))
        img.alpha_composite(txt, (0, 1530))
        del d
    return img.convert("RGB")


def render(fi):
    return quadro(fi / FPS).tobytes()


def audio():
    ev = [(0.08 * k + 0.4, S.sino() * 0.25, 0.25) for k in range(len(T.CHUVAS))]
    ev += [(0.45, S.sino(), 0.4), (T_CIRC[0], S.arrasta(T_CIRC[1] - T_CIRC[0]), 0.45),
           (2.2, S.plim(), 0.5), (2.6, S.cartao(), 0.35), (2.9, S.cartao(), 0.35), (3.4, S.sino(), 0.35)]
    mus = S.musica_cafe(DUR + 0.5)
    com = os.path.join(OUT, "save_date_com.wav")
    sem = os.path.join(OUT, "save_date_sem.wav")
    S.grava(com, DUR, ev, mus, musica_ganho=0.45, fx_ganho=0.8)
    S.grava(sem, DUR, ev, None, fx_ganho=0.8)
    return com, sem


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:]]
        K.folha([quadro(x) for x in ts], os.path.join(OUT, "frames_save.jpg"))
        print("ok")
        return
    com, sem = audio()
    K.entrega("save_date", DUR, render, com, sem)
    print("ok")


if __name__ == "__main__":
    main()
