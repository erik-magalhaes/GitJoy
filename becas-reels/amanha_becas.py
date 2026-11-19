#!/usr/bin/env python3
""""É AMANHÃ!" da Tarde de Jogos no Beca’s (19/nov/2026, véspera; pedido dele: "imagem de divulgação falando que o
evento é amanhã, com animação"). Base do `lembrete_becas.py` (guarda-chuvinhas + calendário pendurado):
o calendário chega mostrando 19, a folha do 19 é ARRANCADA e cai girando, aparece o 20, a caneta circula, estoura
confete e entra "É AMANHÃ!" com as informações.

    /usr/bin/python3 amanha_becas.py --frame 0.6 1.6 2.6 4 8.5
    /usr/bin/python3 amanha_becas.py      # stories (espaço do link) + reels (comenta) + post/story em PNG
"""
import math
import os
import random
import sys
from functools import lru_cache

from PIL import Image, ImageDraw

import kit as K
import sons as S
import story_becas as SB
import tarde as T
import lembrete_becas as L
from tarde import E, TB, W, H, MAR, PET, LAR, AMA, BR, ROSA

from motor import FPS  # noqa: E402

OUT = T.OUT
DUR = 9.5
T_FLIP = 1.35          # folha do 19 arrancada
T_CIRC = (1.9, 2.5)    # caneta circula o 20
T_TIT = 2.55           # "É AMANHÃ!" + confete
VERDE = (64, 168, 82)


def calendario(num):
    s = 12
    im = Image.new("RGBA", (L.CAL_W + s + 4, L.CAL_H + s + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((s, s, s + L.CAL_W, s + L.CAL_H), 34, fill=MAR)
    d.rounded_rectangle((0, 0, L.CAL_W, L.CAL_H), 34, fill=BR, outline=MAR, width=7)
    d.rounded_rectangle((0, 0, L.CAL_W, 120), 34, fill=LAR, outline=MAR, width=7)
    d.rectangle((7, 80, L.CAL_W - 7, 117), fill=LAR)
    d.line((0, 120, L.CAL_W, 120), fill=MAR, width=7)
    for x in (110, L.CAL_W - 110):
        d.ellipse((x - 16, 20, x + 16, 52), fill=L.CREME_ESC, outline=MAR, width=5)
    d.text((L.CAL_W / 2, 88), "NOVEMBRO", font=E.lilita(52), fill=BR, anchor="mm")
    d.text((L.CAL_W / 2, 262), num, font=E.lilita(220), fill=LAR if num == "20" else (150, 140, 130), anchor="mm",
           stroke_width=8, stroke_fill=MAR)
    p = TB.parceria(80)
    if p.width > L.CAL_W - 50:
        p = p.resize((L.CAL_W - 50, int(p.height * (L.CAL_W - 50) / p.width)), Image.LANCZOS)
    im.alpha_composite(p, (int(L.CAL_W / 2 - p.width / 2), int(422 - p.height / 2)))
    return im.resize((int(im.width * L.KC), int(im.height * L.KC)), Image.LANCZOS)


SB.OBJ["cal_19"] = lambda: calendario("19")
SB.OBJ["cal_20"] = lambda: calendario("20")


@lru_cache(None)
def folha_19():
    """Só a parte branca do calendário com o 19 (a folha que é arrancada)."""
    c = calendario("19")
    k = L.KC
    return c.crop((0, int(118 * k), int(L.CAL_W * k) + 2, int(L.CAL_H * k) + 2))


def folha_caindo(img, t):
    u = t - T_FLIP
    if u < 0 or u > 1.2:
        return
    f = folha_19()
    x = W / 2 + 260 * u + 30 * math.sin(u * 6)
    y = 640 + 120 * u + 1500 * u * u
    ang = -70 * u - 40 * u * u
    r = f.rotate(ang, expand=True, resample=Image.BICUBIC)
    if u > 0.8:
        r.putalpha(r.getchannel("A").point(lambda v: int(v * (1.2 - u) / 0.4)))
    img.alpha_composite(r, (int(x - r.width / 2), int(y - r.height / 2)))


random.seed(7)
CONF = [(random.uniform(0, 2 * math.pi), random.uniform(500, 1300), random.choice([LAR, AMA, PET, ROSA, VERDE, BR]),
         random.uniform(-400, 400), random.randint(10, 20)) for _ in range(90)]


def confete(img, t, cx=W / 2, cy=1000):
    u = t - T_TIT
    if u < 0 or u > 2.2:
        return
    d = ImageDraw.Draw(img)
    for a, v, cor, giro, s in CONF:
        x = cx + math.cos(a) * v * u * 0.9
        y = cy + math.sin(a) * v * u * 0.75 + 900 * u * u
        if y > H + 40:
            continue
        al = int(255 * min(1, (2.2 - u) / 0.6))
        w = s * abs(math.cos(math.radians(giro * u)))
        d.rectangle((x - w / 2, y - s / 2, x + w / 2 + 1, y + s / 2), fill=cor + (al,))


def quadro(t, modo="stories"):
    img = T.fundo().copy()
    T.guarda_chuvas(img, t)
    ang = SB.balanco(t, 2.6, 2.5)
    u = min(1, max(0, (t - T_CIRC[0]) / (T_CIRC[1] - T_CIRC[0])))
    entra = min(1.0, t / 0.6)
    cam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    chave = "cal_19" if t < T_FLIP else "cal_20"
    SB.pendulo(cam, W / 2, ang, L.W_UMB, ROSA, L.FIO, chave, L.circulo(u) if u > 0 else None)
    img.alpha_composite(cam, (0, int(-(1 - T.out_back(entra, 1.2)) * 900)))
    folha_caindo(img, t)
    T.poe(img, T.titulo("É AMANHÃ!", 160, LAR), W / 2, 1010, t, T_TIT, -2)
    T.poe(img, E.pilula("TARDE DE JOGOS NO BECA’S CAFÉ", 46, PET, BR, fonte_titulo=True), W / 2, 1130, t,
          T_TIT + 0.35, 1)
    T.poe(img, TB.selo_data(38), W / 2, 1205, t, T_TIT + 0.6, -1)
    T.poe(img, TB.selo_endereco(30), W / 2, 1273, t, T_TIT + 0.8, 1)
    T.poe(img, E.pilula("R$ 30 · R$ 15 VIRAM CONSUMAÇÃO", 34, AMA, MAR, fonte_titulo=True), W / 2, 1335, t,
          T_TIT + 1.0, -1)
    t_cta = T_TIT + 1.4
    if modo == "stories":  # área y≈1440–1600 livre para o adesivo de link
        if t > t_cta:
            a = min(1, (t - t_cta) / 0.3)
            bob = 8 * math.sin(2 * math.pi * (t - t_cta) / 1.2)
            txt = Image.new("RGBA", (W, 130), (0, 0, 0, 0))
            dt = ImageDraw.Draw(txt)
            dt.text((W / 2 - 60, 45), "garanta sua mesa aqui:", font=E.fig(42, 900), fill=MAR, anchor="mm")
            txt.alpha_composite(L.seta_baixo(), (int(W / 2 + 205), int(bob)))
            if a < 1:
                txt.putalpha(txt.getchannel("A").point(lambda v: int(v * a)))
            img.alpha_composite(txt, (0, 1370))
        T.poe(img, E.pilula("ou no WhatsApp " + TB.WHATS, 36, BR, MAR), W / 2, 1665, t, t_cta + 0.3, 0)
    else:
        T.poe(img, E.pilula("Comenta: qual jogo você quer jogar amanhã?", 36, BR, MAR), W / 2, 1420, t, t_cta, 1)
        T.poe(img, E.pilula("RESERVE NO WHATSAPP " + TB.WHATS, 36, LAR, BR, fonte_titulo=True), W / 2, 1500, t,
              t_cta + 0.3, -1)
    confete(img, t)
    return img.convert("RGB")


def render_stories(fi):
    return quadro(fi / FPS, "stories").tobytes()


def render_reels(fi):
    return quadro(fi / FPS, "reels").tobytes()


def audio(nome):
    ev = [(0.08 * k + 0.4, S.sino() * 0.25, 0.25) for k in range(len(T.CHUVAS))]
    ev += [(0.45, S.sino(), 0.4), (T_FLIP, S.rasgo(), 0.6), (T_FLIP + 0.1, S.sopro(0.5, False), 0.3),
           (T_CIRC[0], S.arrasta(T_CIRC[1] - T_CIRC[0]), 0.45), (T_TIT, S.estouro(), 0.6), (T_TIT, S.plim(), 0.5),
           (T_TIT + 0.35, S.cartao(), 0.35), (T_TIT + 0.6, S.cartao(), 0.35), (T_TIT + 0.8, S.cartao(), 0.35),
           (T_TIT + 1.0, S.cartao(), 0.35), (T_TIT + 1.4, S.sino(), 0.35)]
    mus = S.musica_pop(DUR + 0.5, 0.0)
    com = os.path.join(OUT, f"{nome}_com.wav")
    sem = os.path.join(OUT, f"{nome}_sem.wav")
    S.grava(com, DUR, ev, mus, musica_ganho=0.4, fx_ganho=0.8)
    S.grava(sem, DUR, ev, None, fx_ganho=0.8)
    return com, sem


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:]]
        K.folha([quadro(x) for x in ts] + [quadro(DUR - 0.1, "reels")], os.path.join(OUT, "frames_amanha.jpg"))
        print("ok")
        return
    d = os.path.join(OUT, "amanha")
    os.makedirs(d, exist_ok=True)
    quadro(DUR - 0.1, "stories").save(os.path.join(d, "story_amanha.png"))
    quadro(DUR - 0.1, "reels").crop((0, 200, W, 1550)).save(os.path.join(d, "post_amanha.png"))
    for nome, rnd in (("amanha_stories", render_stories), ("amanha_reels", render_reels)):
        com, sem = audio(nome)
        K.entrega(nome, DUR, rnd, com, sem)
    print("ok")


if __name__ == "__main__":
    main()
