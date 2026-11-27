#!/usr/bin/env python3
"""Contagem do Domingo de Jogos 13/12 (cronograma: 6/12 "falta 1 semana", 11/12 "últimas vagas", 12/12 "é amanhã",
13/12 "é hoje"). Estilo aprovado: fundo vermelho natalino com guarda-chuvinhas balançando e pisca-pisca; um guarda-chuva
rosa segura a folha de calendário DEZEMBRO / 13 (logos Sua Vez × Beca’s) e a caneta circula o 13. Reels (comenta + link na
bio) e Stories (espaço livre y≈1400–1590 pro adesivo de link), mais post 1080x1350 e story parado (PNG).

    /usr/bin/python3 contagem_domingo.py semana --frame 0.5 2 5 9 [--stories]
    /usr/bin/python3 contagem_domingo.py semana|ultimas|amanha|hoje     # vídeos + PNGs em out/contagem/
"""
import math
import os
import sys
from functools import lru_cache

from PIL import Image, ImageDraw

import domingo as D
import kit as K
import sons as S
import story_becas as SB
import lembrete_becas as LB
from tarde import E, TB, W, H, MAR, PET, LAR, AMA, BR, ROSA
from motor import FPS

OUT = D.OUT
PASTA = os.path.join(OUT, "contagem")
VERDE = (24, 110, 66)
DUR = 11.0
# modo: (título, frase do selo de cima, comenta do Reels)
MODOS = {
    "semana": ("FALTA 1\nSEMANA!", "DOMINGO DE JOGOS · ESPECIAL DE NATAL", "Comenta: com quem você vem?"),
    "ultimas": ("ÚLTIMAS\nVAGAS!", "DOMINGO DE JOGOS · ESPECIAL DE NATAL", "Marca quem não pode ficar de fora!"),
    "amanha": ("É AMANHÃ!", "DOMINGO DE JOGOS · ESPECIAL DE NATAL", "Comenta: qual jogo você quer jogar?"),
    "hoje": ("É HOJE!", "DOMINGO DE JOGOS · ESPECIAL DE NATAL", "Te esperamos no Beca’s!"),
}


def calendario():
    s = 12
    cw, ch = LB.CAL_W, LB.CAL_H
    im = Image.new("RGBA", (cw + s + 4, ch + s + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((s, s, s + cw, s + ch), 34, fill=MAR)
    d.rounded_rectangle((0, 0, cw, ch), 34, fill=BR, outline=MAR, width=7)
    d.rounded_rectangle((0, 0, cw, 120), 34, fill=VERDE, outline=MAR, width=7)
    d.rectangle((7, 80, cw - 7, 117), fill=VERDE)
    d.line((0, 120, cw, 120), fill=MAR, width=7)
    for x in (110, cw - 110):
        d.ellipse((x - 16, 20, x + 16, 52), fill=LB.CREME_ESC, outline=MAR, width=5)
    d.text((cw / 2, 88), "DEZEMBRO", font=E.lilita(52), fill=BR, anchor="mm")
    d.text((cw / 2, 262), "13", font=E.lilita(220), fill=LAR, anchor="mm", stroke_width=8, stroke_fill=MAR)
    p = TB.parceria(80)
    if p.width > cw - 50:
        p = p.resize((cw - 50, int(p.height * (cw - 50) / p.width)), Image.LANCZOS)
    im.alpha_composite(p, (int(cw / 2 - p.width / 2), int(422 - p.height / 2)))
    return im.resize((int(im.width * LB.KC), int(im.height * LB.KC)), Image.LANCZOS)


SB.OBJ["cal_dez13"] = calendario


@lru_cache(None)
def seta_branca():
    im = Image.new("RGBA", (90, 110), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.line((45, 5, 45, 80), fill=BR, width=12)
    d.polygon([(10, 62), (80, 62), (45, 105)], fill=BR)
    return im


@lru_cache(None)
def fundo_parado():
    import domingo_carrossel as DC
    return DC.fundo_parado()


def quadro(t, modo, formato="reels", parado=False):
    tit, selo, comenta = MODOS[modo]
    img = (fundo_parado().copy() if parado else D.fundo(t + 3.0))
    ang = 0 if parado else SB.balanco(t, 2.6, 2.5)
    u = min(1, max(0, (t - LB.T_CIRC[0]) / (LB.T_CIRC[1] - LB.T_CIRC[0])))
    entra = 1.0 if parado else min(1.0, t / 0.6)
    cam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    SB.pendulo(cam, W / 2, ang, LB.W_UMB, ROSA, LB.FIO + 40, "cal_dez13", LB.circulo(u) if u > 0 else None)
    img.alpha_composite(cam, (0, int(-(1 - D.T.out_back(entra, 1.2)) * 900) - 40))
    y0 = 1050 if "\n" not in tit else 1090
    K.poe(img, K.titulo(tit, 150, AMA), W / 2, y0, t, 1.8, -2)
    yb = y0 + (110 if "\n" not in tit else 175)
    K.poe(img, E.pilula(selo, 40, VERDE, BR, fonte_titulo=True), W / 2, yb, t, 2.2, 1)
    K.poe(img, E.pilula(f"{D.DATA} · {D.HORA}", 38, AMA, MAR, fonte_titulo=True), W / 2, yb + 75, t, 2.5, -1)
    K.poe(img, E.pilula("BECA’S CAFÉ · RUA SOROCABA, 35 · MAUÁ", 32, BR, MAR, fonte_titulo=True), W / 2, yb + 145, t,
          2.7, 1)
    if formato == "stories":
        if t > 3.2:
            a = min(1, (t - 3.2) / 0.3)
            bob = 0 if parado else 8 * math.sin(2 * math.pi * (t - 3.2) / 1.2)
            txt = Image.new("RGBA", (W, 130), (0, 0, 0, 0))
            dt = ImageDraw.Draw(txt)
            dt.text((W / 2 - 60, 45), "garanta sua vaga aqui:", font=E.fig(42, 900), fill=BR, anchor="mm")
            txt.alpha_composite(seta_branca(), (int(W / 2 + 200), int(bob)))
            if a < 1:
                txt.putalpha(txt.getchannel("A").point(lambda v: int(v * a)))
            img.alpha_composite(txt, (0, yb + 205))
        K.poe(img, E.pilula("VAGAS LIMITADAS: FAÇA SUA RESERVA!", 34, PET, BR, fonte_titulo=True), W / 2, 1700, t, 3.6)
    else:
        K.poe(img, E.pilula("RESERVE PELO LINK NA BIO", 40, PET, BR, fonte_titulo=True), W / 2, yb + 235, t, 3.2, -1)
        if formato != "post":
            K.poe(img, E.pilula(comenta, 36, BR, MAR), W / 2, yb + 320, t, 3.5, 1)
    return img.convert("RGB")


def audio(nome):
    ev = [(0.45, S.sino(), 0.4), (LB.T_CIRC[0], S.arrasta(LB.T_CIRC[1] - LB.T_CIRC[0]), 0.45),
          (1.8, S.estouro(), 0.45), (2.2, S.cartao(), 0.35), (2.5, S.cartao(), 0.35), (2.7, S.cartao(), 0.35),
          (3.2, S.plim(), 0.4)]
    mus = S.musica_pop(DUR + 0.5, 0.0)
    com = os.path.join(OUT, f"{nome}_com.wav")
    sem = os.path.join(OUT, f"{nome}_sem.wav")
    S.grava(com, DUR, ev, mus, musica_ganho=0.45, fx_ganho=0.8)
    S.grava(sem, DUR, ev, None, fx_ganho=0.8)
    return com, sem


MODO = "semana"


def render_reels(fi):
    return quadro(fi / FPS, MODO, "reels").tobytes()


def render_stories(fi):
    return quadro(fi / FPS, MODO, "stories").tobytes()


def main():
    global MODO
    args = [a for a in sys.argv[1:]]
    MODO = args[0] if args and args[0] in MODOS else "semana"
    fmt = "stories" if "--stories" in args else "reels"
    if "--frame" in args:
        ts = [float(a) for a in args[args.index("--frame") + 1:] if not a.startswith("--")]
        K.folha([quadro(t, MODO, fmt) for t in ts], os.path.join(OUT, "frames_contagem.jpg"))
        return
    os.makedirs(PASTA, exist_ok=True)
    st = quadro(9.0, MODO, "stories", parado=True)
    st.save(os.path.join(PASTA, f"{MODO}_story.png"))
    rl = quadro(9.0, MODO, "post", parado=True)
    rl.crop((0, 225, W, 225 + 1350)).save(os.path.join(PASTA, f"{MODO}_post.png"))
    if "--so-fotos" in args:
        return
    for m in ("reels", "stories"):
        com, sem = audio(f"{MODO}_{m}")
        K.entrega(f"{MODO}_{m}", DUR, render_reels if m == "reels" else render_stories, com, sem)
    print("ok", MODO)


if __name__ == "__main__":
    main()
