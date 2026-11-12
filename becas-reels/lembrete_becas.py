#!/usr/bin/env python3
"""LEMBRETE da Tarde de Jogos no Beca’s para os STORIES (12/nov/2026, pedido dele: "vídeo curto pro stories como
lembrete do evento"). 9 s, visual das guarda-chuvinhas: os de `tarde.py` balançando no alto + um guarda-chuva rosa
segurando a folha de calendário (NOVEMBRO / 20, agora com os logos Sua Vez × Beca’s) e a caneta vermelha circulando o 20.
"LEMBRETE!", tarde de jogos, data/horário, endereço, preço e "garanta sua mesa aqui:" + seta com a área y≈1350–1580
LIVRE para o adesivo de link; WhatsApp embaixo. Sem "faltam N dias": serve para qualquer dia até o evento.

    /usr/bin/python3 lembrete_becas.py --frame 0.5 2 4 8.5   # out/frames_lembrete.jpg
    /usr/bin/python3 lembrete_becas.py                       # out/lembrete_becas_{com_som,para_musica}_final.mp4
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
DUR = 9.0
VERM = (214, 48, 49)
CREME_ESC = (236, 226, 208)
CAL_W, CAL_H = 460, 480
W_UMB, FIO = 260, 170
KC = 0.95
T_CIRC = (1.0, 1.7)


def calendario():
    s = 12
    im = Image.new("RGBA", (CAL_W + s + 4, CAL_H + s + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((s, s, s + CAL_W, s + CAL_H), 34, fill=MAR)
    d.rounded_rectangle((0, 0, CAL_W, CAL_H), 34, fill=BR, outline=MAR, width=7)
    d.rounded_rectangle((0, 0, CAL_W, 120), 34, fill=LAR, outline=MAR, width=7)
    d.rectangle((7, 80, CAL_W - 7, 117), fill=LAR)
    d.line((0, 120, CAL_W, 120), fill=MAR, width=7)
    for x in (110, CAL_W - 110):
        d.ellipse((x - 16, 20, x + 16, 52), fill=CREME_ESC, outline=MAR, width=5)
    d.text((CAL_W / 2, 88), "NOVEMBRO", font=E.lilita(52), fill=BR, anchor="mm")
    d.text((CAL_W / 2, 262), "20", font=E.lilita(220), fill=LAR, anchor="mm", stroke_width=8, stroke_fill=MAR)
    p = TB.parceria(80)
    if p.width > CAL_W - 50:
        p = p.resize((CAL_W - 50, int(p.height * (CAL_W - 50) / p.width)), Image.LANCZOS)
    im.alpha_composite(p, (int(CAL_W / 2 - p.width / 2), int(422 - p.height / 2)))
    return im.resize((int(im.width * KC), int(im.height * KC)), Image.LANCZOS)


SB.OBJ["cal_lembrete"] = calendario


def circulo(u):
    def f(sp):
        S_ = sp.width
        cx, cy = S_ / 2, S_ / 2
        hx = cx - 0.055 * W_UMB
        top = cy + FIO - 6 + 14 + 0.75 * W_UMB + 2 + 34
        ox, oy = hx - 6 * (KC - 1), top + 262 * KC
        d = ImageDraw.Draw(sp)
        n = int(120 * u)
        pts = []
        for k in range(n + 1):
            a = -2.2 + 2 * math.pi * 1.12 * k / 120
            r = 1 + 0.05 * math.sin(3 * a)
            pts.append((ox + 170 * KC * r * math.cos(a), oy + 112 * KC * r * math.sin(a)))
        if len(pts) > 1:
            d.line(pts, fill=VERM, width=11, joint="curve")
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
    ang = SB.balanco(t, 2.6, 2.5)
    u = min(1, max(0, (t - T_CIRC[0]) / (T_CIRC[1] - T_CIRC[0])))
    entra = min(1.0, t / 0.6)
    cam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    SB.pendulo(cam, W / 2, ang, W_UMB, ROSA, FIO, "cal_lembrete", circulo(u) if u > 0 else None)
    img.alpha_composite(cam, (0, int(-(1 - T.out_back(entra, 1.2)) * 900)))
    T.poe(img, T.titulo("LEMBRETE!", 150, LAR), W / 2, 1010, t, 1.8, -2)
    T.poe(img, E.pilula("TARDE DE JOGOS NO BECA’S CAFÉ", 46, PET, BR, fonte_titulo=True), W / 2, 1125, t, 2.2, 1)
    T.poe(img, TB.selo_data(38), W / 2, 1200, t, 2.5, -1)
    T.poe(img, TB.selo_endereco(30), W / 2, 1268, t, 2.7, 1)
    T.poe(img, E.pilula("R$ 30 · R$ 15 VIRAM CONSUMAÇÃO", 34, AMA, MAR, fonte_titulo=True), W / 2, 1330, t, 2.9, -1)
    # área y≈1400–1590 livre para o adesivo de link
    if t > 3.3:
        a = min(1, (t - 3.3) / 0.3)
        bob = 8 * math.sin(2 * math.pi * (t - 3.3) / 1.2)
        txt = Image.new("RGBA", (W, 130), (0, 0, 0, 0))
        dt = ImageDraw.Draw(txt)
        dt.text((W / 2 - 60, 45), "garanta sua mesa aqui:", font=E.fig(42, 900), fill=MAR, anchor="mm")
        txt.alpha_composite(seta_baixo(), (int(W / 2 + 205), int(bob)))
        if a < 1:
            txt.putalpha(txt.getchannel("A").point(lambda v: int(v * a)))
        img.alpha_composite(txt, (0, 1365))
    T.poe(img, E.pilula("ou no WhatsApp " + TB.WHATS, 36, BR, MAR), W / 2, 1660, t, 3.6, 0)
    return img.convert("RGB")


def render(fi):
    return quadro(fi / FPS).tobytes()


def audio():
    ev = [(0.08 * k + 0.4, S.sino() * 0.25, 0.25) for k in range(len(T.CHUVAS))]
    ev += [(0.45, S.sino(), 0.4), (T_CIRC[0], S.arrasta(T_CIRC[1] - T_CIRC[0]), 0.45),
           (1.8, S.plim(), 0.5), (2.2, S.cartao(), 0.35), (2.5, S.cartao(), 0.35), (2.9, S.cartao(), 0.35),
           (3.3, S.sino(), 0.35)]
    mus = S.musica_cafe(DUR + 0.5)
    com = os.path.join(OUT, "lembrete_becas_com.wav")
    sem = os.path.join(OUT, "lembrete_becas_sem.wav")
    S.grava(com, DUR, ev, mus, musica_ganho=0.45, fx_ganho=0.8)
    S.grava(sem, DUR, ev, None, fx_ganho=0.8)
    return com, sem


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:]]
        K.folha([quadro(x) for x in ts], os.path.join(OUT, "frames_lembrete.jpg"))
        print("ok")
        return
    com, sem = audio()
    K.entrega("lembrete_becas", DUR, render, com, sem)
    print("ok")


if __name__ == "__main__":
    main()
