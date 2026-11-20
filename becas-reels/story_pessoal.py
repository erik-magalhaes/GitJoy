#!/usr/bin/env python3
"""Stories PESSOAL do Erik sobre a Tarde de Jogos (20/nov/2026): "videozinho rápido, só pra dar uma comentada, sem
muita informação, sem frufru". Só as cenas do dia (brutos/nov20) e uma frase por vez em texto simples tipo Instagram
(branco com sombra leve, sem logo, sem selo, sem tela final). 12 s.

    /usr/bin/python3 story_pessoal.py --frame 1 5 10
    /usr/bin/python3 story_pessoal.py
"""
import os
import sys
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter

import kit as K
import sons as S
import obrigado as O
from tarde import E, W, H

from motor import FPS  # noqa: E402

OUT = K.OUT
PLANOS = [("v", 0.8, 3.0), ("v", 13.5, 2.6), ("v", 27.6, 2.2), ("v", 40.0, 1.8), ("f", "IMG_194900.jpg", 3.2)]
INI = [0.0]
for p in PLANOS:
    INI.append(INI[-1] + p[2])
DUR = INI[-1]
FRASES = [(0.3, 3.0, "que tarde!"), (3.0, 7.8, "6 horas de jogo, 35 jogos diferentes\ne muita gente nova"),
          (8.6, DUR, "obrigado @becascafe e\n@espacofamilyheaven")]


@lru_cache(None)
def texto(txt):
    f = E.fig(54, 800)
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    linhas = txt.split("\n")
    w = int(max(d0.textlength(l, font=f) for l in linhas)) + 60
    h = len(linhas) * 70 + 50
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k, l in enumerate(linhas):
        d.text((w / 2, 35 + k * 70 + 30), l, font=f, fill=(0, 0, 0, 170), anchor="mm")
    im = im.filter(ImageFilter.GaussianBlur(6))
    d = ImageDraw.Draw(im)
    for k, l in enumerate(linhas):
        d.text((w / 2, 32 + k * 70 + 30), l, font=f, fill=(255, 255, 255, 255), anchor="mm")
    return im


def quadro(t):
    k = max(i for i in range(len(PLANOS)) if INI[i] <= t) if t < DUR else len(PLANOS) - 1
    tipo, ref, d = PLANOS[k]
    u = t - INI[k]
    if tipo == "v":
        img = K.quadro_clip("dia", ref, d, 1.0, u)
    else:
        img = O.zoom(O.foto(ref), u / d, 0.05)
    for a, b, txt in FRASES:
        if a <= t < b:
            al = min(1.0, (t - a) / 0.25, (b - t) / 0.25 if b < DUR else 1.0)
            im = texto(txt).copy()
            im.putalpha(im.getchannel("A").point(lambda v: int(v * al)))
            img.alpha_composite(im, (int(W / 2 - im.width / 2), 1330))
    return img.convert("RGB")


def render(fi):
    return quadro(fi / FPS).tobytes()


def main():
    K.prepara([("dia", r, d, 1.0) for tp, r, d in PLANOS if tp == "v"])
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:]]
        K.folha([quadro(x) for x in ts], os.path.join(OUT, "frames_pessoal.jpg"))
        print("ok", DUR)
        return
    mus = S.musica_cafe(DUR + 0.5)
    com = os.path.join(OUT, "pessoal_com.wav")
    sem = os.path.join(OUT, "pessoal_sem.wav")
    S.grava(com, DUR, [], mus, musica_ganho=0.45)
    S.grava(sem, DUR, [], None)
    K.entrega("story_pessoal", DUR, render, com, sem)
    print("ok", DUR)


if __name__ == "__main__":
    main()
