#!/usr/bin/env python3
"""Reels/Stories do DESAFIO HITSTER (30/11 no cronograma do Domingo de Jogos 13/12). Mesmo estilo aprovado do
`domingo_festa.py` (fundo vermelho natalino, guarda-chuvinhas e pisca-pisca): a polaroide pendurada no guarda-chuva mostra
as mesas jogando Hitster em 20/11 → tela do desafio (caixa oficial, 3 passos) → "VALENDO PRÊMIO!" (sem dizer qual) →
convite do domingo.

    /usr/bin/python3 desafio_reels.py --frame 1 5 9 13 17 [--stories]
    /usr/bin/python3 desafio_reels.py      # out/desafio_{reels,stories}_{com_som,para_musica}_final.mp4
"""
import math
import os
import sys

from PIL import Image, ImageDraw

import domingo_festa as F
import desafio_hitster as DH
from domingo_festa import D, K, S, E, W, H, FPS, OUT, MAR, PET, LAR, AMA, BR

VERDE = (24, 110, 66)
F.CENAS = [
    (F.BRUTO, F.CROP, 12.6, 2.6, "TEM DESAFIO NO DOMINGO!"),
    (F.BRUTO, F.CROP, 40.2, 2.3, "TOCA A MÚSICA..."),
    (F.BRUTO, F.CROP, 47.4, 2.4, "...E CADA MESA CHUTA O ANO!"),
]
F.INI = []
_t = 0.0
for c in F.CENAS:
    F.INI.append(_t)
    _t += c[3]
T_DES = _t
T_PREMIO = T_DES + 5.2
T_CTA = T_PREMIO + 3.4
DUR = T_CTA + 6.4
D.T_TIT, D.T_QUADRO, D.T_CTA = T_DES, T_PREMIO, T_CTA


def passos(n):
    """Quadro com os 3 passos; `n` = quantos já apareceram."""
    p = E.bloco(560, 330, BR, raio=30, ow=6, sombra=10).copy()
    d = ImageDraw.Draw(p)
    for k, txt in enumerate(("toca a música", "cada mesa chuta o ano", "chegou perto? pontua!")):
        if k >= n:
            break
        y = 62 + k * 100
        d.ellipse((30, y - 30, 90, y + 30), fill=(LAR, PET, AMA)[k], outline=MAR, width=4)
        d.text((60, y + 1), str(k + 1), font=E.lilita(40), fill=BR if k < 2 else MAR, anchor="mm")
        d.text((110, y), txt, font=E.fig(36, 900), fill=MAR, anchor="lm")
    return p


def cena_desafio(img, t):
    u = t - T_DES
    img.alpha_composite(D.fundo(t))
    K.poe(img, K.titulo("DESAFIO\nHITSTER!", 150, LAR), W / 2, 640, t, T_DES + 0.05, -2)
    K.poe(img, E.pilula("ÀS 16H, NO DOMINGO DE JOGOS", 40, VERDE, BR, fonte_titulo=True), W / 2, 870, t, T_DES + 0.4, 1)
    if u > 0.6:
        pulo = abs(math.sin((u - 0.6) * 3.2)) * 18
        E.cola(img, DH.caixa(470), 300, 1270 - pulo, -6 + 2 * math.sin(u * 2), 1, 1)
    for x, y, sz, c, r, t0 in ((120, 1040, 74, AMA, -12, 0.8), (520, 1010, 60, BR, 10, 1.0), (980, 1510, 70, AMA, 8, 1.2)):
        if u > t0:
            E.cola(img, DH.nota(sz, c), x, y + 10 * math.sin(u * 3 + x), r + 6 * math.sin(u * 2 + y), 1, 1)
    n = min(3, int(max(0.0, u - 1.4) / 0.9) + (1 if u > 1.4 else 0))
    if n:
        E.cola(img, passos(n), 790, 1280, 2, 1, 1)


def cena_premio(img, t):
    u = t - T_PREMIO
    img.alpha_composite(D.fundo(t))
    K.poe(img, E.pilula("TODAS AS MESAS JOGAM JUNTAS", 52, PET, BR, fonte_titulo=True), W / 2, 780, t, T_PREMIO + 0.05)
    K.poe(img, K.titulo("VALENDO UM\n1, 2, 3, LUCHA!", 130, AMA), W / 2, 980, t, T_PREMIO + 0.45, -3)
    K.poe(img, DH.caixa(330, DH.LUCHA), W / 2, 1290, t, T_PREMIO + 0.7, -5)
    K.poe(img, E.pilula("a mesa campeã disputa a final!", 46, BR, MAR), W / 2, 1520, t, T_PREMIO + 0.9, 2)
    if u > 0.45:  # confete
        import random
        rnd = random.Random(5)
        d = ImageDraw.Draw(img)
        for _ in range(70):
            x0, vx, vy = W / 2 + rnd.uniform(-60, 60), rnd.uniform(-700, 700), rnd.uniform(-1500, -600)
            tt = u - 0.45
            x, y = x0 + vx * tt, 1100 + vy * tt + 1500 * tt * tt
            if 0 < y < H:
                c = rnd.choice([AMA, LAR, PET, BR, VERDE])
                d.rectangle((x, y, x + 14, y + 9), fill=c)


def quadro(t, modo="reels"):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    if t < T_DES:
        img.alpha_composite(D.fundo(t + 3.0))
        F.polaroide(img, t)
    elif t < T_PREMIO:
        cena_desafio(img, t)
    elif t < T_CTA:
        cena_premio(img, t)
    else:
        D.cta(img, t, modo)
    for tb in (T_DES, T_PREMIO, T_CTA):
        dd = t - tb
        if 0 <= dd < 0.12:
            img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(200 * (1 - dd / 0.12)))))
    if t < T_CTA:
        K.marca(img)
    return img.convert("RGB")


def render_reels(fi):
    return quadro(fi / FPS, "reels").tobytes()


def render_stories(fi):
    return quadro(fi / FPS, "stories").tobytes()


def audio(nome):
    ev = [(0.05, S.sopro(0.4), 0.3), (0.45, S.estouro(), 0.3)]
    ev += [(F.INI[k], S.tic(k % 2 == 0), 0.35) for k in range(1, len(F.CENAS))]
    ev += [(T_DES, S.sino(), 0.45)] + [(T_DES + 1.4 + 0.9 * k, S.plim(), 0.35) for k in range(3)]
    ev += [(T_PREMIO + 0.45, S.estouro(), 0.6), (T_PREMIO + 0.5, S.sino(), 0.4)]
    ev += [(T_CTA, S.sopro(0.5, False), 0.4), (T_CTA + 0.35, S.carta_vira(), 0.5)]
    mus = S.musica_pop(DUR + 0.5, 0.0)
    com = os.path.join(OUT, f"{nome}_com.wav")
    sem = os.path.join(OUT, f"{nome}_sem.wav")
    S.grava(com, DUR, ev, mus, musica_ganho=0.45, fx_ganho=0.75)
    S.grava(sem, DUR, ev, None, fx_ganho=0.75)
    return com, sem


def main():
    args = sys.argv[1:]
    modo = "stories" if "--stories" in args else "reels"
    F.prepara()
    if "--frame" in args:
        ts = [float(a) for a in args[args.index("--frame") + 1:] if not a.startswith("--")]
        K.folha([quadro(t, modo) for t in ts], os.path.join(OUT, "frames_desafio.jpg"))
        print("DUR", DUR)
        return
    for m in ("reels", "stories"):
        com, sem = audio(f"desafio_{m}")
        K.entrega(f"desafio_{m}", DUR, render_reels if m == "reels" else render_stories, com, sem)
    print("ok", DUR)


if __name__ == "__main__":
    main()
