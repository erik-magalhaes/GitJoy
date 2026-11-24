#!/usr/bin/env python3
"""Reels/Stories "AS VAGAS ESTÃO ACABANDO!" (9/12 no cronograma do Domingo de Jogos). O quadro de vagas pendurado com os
30 ingressinhos e o carimbo RESERVADA batendo um a um até o número REAL de vendidas (`--vendidas N`, que eles passam no
dia: nunca inventar) → "RESTAM N VAGAS!" → convite. Estilo aprovado (fundo vermelho natalino, guarda-chuvinhas).

    /usr/bin/python3 vagas_reels.py --vendidas 18 --frame 1 3 6 9 [--stories]
    /usr/bin/python3 vagas_reels.py --vendidas 18     # out/vagas{18}_{reels,stories}_..._final.mp4
"""
import os
import sys

from PIL import Image

import domingo as D
import kit as K
import sons as S
from tarde import E, W, H, MAR, PET, LAR, AMA, BR
from motor import FPS

OUT = D.OUT
VERDE = (24, 110, 66)
T_CAR = 1.3          # começam os carimbos
PASSO = 0.09         # um carimbo a cada 90 ms
VENDIDAS = 18


def t_restam():
    return T_CAR + VENDIDAS * PASSO + 0.5


def dur_total():
    return t_restam() + 3.2 + 6.4


def cena_quadro(img, t):
    img.alpha_composite(D.fundo(t + 3.0))
    K.poe(img, K.titulo("AS VAGAS ESTÃO\nACABANDO!", 120, AMA), W / 2, 470, t, 0.1, -2)
    n = 0 if t < T_CAR else min(VENDIDAS, int((t - T_CAR) / PASSO) + 1)
    E.cola(img, D.painel(n), W / 2, 1060, 0, 1, 1)
    tr = t_restam()
    if t > tr:
        restam = D.VAGAS - VENDIDAS
        txt = "ÚLTIMA VAGA!" if restam == 1 else f"RESTAM {restam} VAGAS!"
        K.poe(img, K.titulo(txt, 110, AMA), W / 2, 1530, t, tr, 2)
        K.poe(img, E.pilula("garanta a sua antes que acabe!", 42, BR, MAR), W / 2, 1650, t, tr + 0.5, -1)
    K.marca(img)


def quadro(t, modo="reels"):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    tc = t_restam() + 3.2
    if t < tc:
        cena_quadro(img, t)
    else:
        D.T_CTA = tc
        D.cta(img, t, modo)
        if 0 <= t - tc < 0.12:
            img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(200 * (1 - (t - tc) / 0.12)))))
    return img.convert("RGB")


def render_reels(fi):
    return quadro(fi / FPS, "reels").tobytes()


def render_stories(fi):
    return quadro(fi / FPS, "stories").tobytes()


def audio(nome, dur):
    ev = [(0.1, S.sino(), 0.35)]
    ev += [(T_CAR + k * PASSO, S.tic(k % 2 == 0), 0.45) for k in range(VENDIDAS)]
    ev += [(t_restam(), S.estouro(), 0.5), (t_restam() + 3.2, S.carta_vira(), 0.5)]
    mus = S.musica_pop(dur + 0.5, 0.0)
    com = os.path.join(OUT, f"{nome}_com.wav")
    sem = os.path.join(OUT, f"{nome}_sem.wav")
    S.grava(com, dur, ev, mus, musica_ganho=0.45, fx_ganho=0.75)
    S.grava(sem, dur, ev, None, fx_ganho=0.75)
    return com, sem


def main():
    global VENDIDAS
    args = sys.argv[1:]
    if "--vendidas" in args:
        VENDIDAS = int(args[args.index("--vendidas") + 1])
    modo = "stories" if "--stories" in args else "reels"
    if "--frame" in args:
        ts = [float(a) for a in args[args.index("--frame") + 1:] if not a.startswith("--") and a.replace(".", "").isdigit()
              and float(a) < 60]
        K.folha([quadro(t, modo) for t in ts], os.path.join(OUT, "frames_vagas.jpg"))
        print("DUR", dur_total())
        return
    dur = dur_total()
    for m in ("reels", "stories"):
        nome = f"vagas{VENDIDAS}_{m}"
        com, sem = audio(nome, dur)
        K.entrega(nome, dur, render_reels if m == "reels" else render_stories, com, sem)
    print("ok", dur)


if __name__ == "__main__":
    main()
