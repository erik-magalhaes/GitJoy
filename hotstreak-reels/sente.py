#!/usr/bin/env python3
"""Hot Streak — "É ASSIM QUE VOCÊ SE SENTE JOGANDO HOT STREAK" (9/nov, 3ª rodada do POV): ele não quis a gravação deles
nem os textos contando a história. Agora: só gente CORRENDO (vídeos LIVRES do Mixkit, licença gratuita sem atribuição:
40765 pés, 40748 moça correndo, 717 rapaz de costas; 4K → recorte 9:16 em out/stock/) → chicote → dentro do jogo em 1ª
pessoa (pista, torcida oficial, os 4 mascotes passando) com UMA frase só → tela final do hs.py.

    /usr/bin/python3 sente.py --frame 0.5 2 3.8 5 6.5 9 12 15
    /usr/bin/python3 sente.py            → out/sente_{com_som,para_musica}_final.mp4
"""
import argparse
import math
import os
import subprocess

import numpy as np
from PIL import Image

import hs as HS
import pov_corrida as P
from hs import W, H, FPS, RED, YEL, WHITE, INK, cola, placa, confete, pop, logo_card, ease, seg

OUT = HS.OUT
STOCK = os.path.join(OUT, "stock")
PLANOS = [("40765", 0.0, 1.6), ("40748", 1.6, 3.3), ("717", 3.3, 5.0)]  # (clipe, início, fim) no vídeo
T_VIRA, T_JOGO, T_CTA = 5.0, 5.45, 13.5
DUR = T_CTA + 5.0
ULTRA = [(6.2, 0, -2.4), (7.4, 1, 2.4), (8.6, 2, -0.8), (9.8, 3, 0.8)]


def quadro_stock(t):
    for clip, a, b in PLANOS:
        if t < b or clip == PLANOS[-1][0]:
            d = os.path.join(STOCK, clip)
            n = len(os.listdir(d))
            k = int(min(n, max(1, (t - a) * 30 + 1)))
            return Image.open(os.path.join(d, "%04d.jpg" % k)).convert("RGBA")


def corrida(t):
    img = quadro_stock(t)
    for clip, a, b in PLANOS[1:]:  # cortes secos com um "flash" curtinho na batida
        if 0 <= t - a < 0.08:
            img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, 120)))
    return img


def jogo(t):
    by, bx, br = P.balanco(t, 0.9)
    img = P.pista_pov(t)
    lista = []
    for t0, k, x in ULTRA:
        if t >= t0:
            v = t - t0
            lista.append((1.1 + 3.2 * v + 1.6 * v * v, k, x))
    for z, k, x in sorted(lista, reverse=True):
        P.mascote_frente(img, P.MASC[k][0], x, z, t, k * 1.3, by, bx, alt=1.9)
    confete(img, t, 80, 9, 0, 1600)
    u = t - T_JOGO
    cola(img, placa("É ASSIM QUE VOCÊ\nSE SENTE JOGANDO", 78, WHITE, INK), 540, 1170, -2, pop(t, T_JOGO + 0.3))
    if u > 0.75:
        b = 1 + 0.03 * abs(math.sin(t * 5))
        cola(img, placa("HOT STREAK!", 120, RED, YEL), 540, 1430, 2, pop(t, T_JOGO + 0.75) * b)
    if u < 0.15:
        img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(220 * (1 - u / 0.15)))))
    return img


def vira(t):
    u = ease(seg(t, T_VIRA, T_JOGO))
    a, b = corrida(min(t, PLANOS[-1][2] - 0.01)), jogo(T_JOGO)
    k = 120 * math.sin(u * math.pi)
    a, b = P.borrao_h(a, k), P.borrao_h(b, k)
    img = Image.new("RGBA", (W, H))
    img.paste(a, (int(-W * u), 0))
    img.paste(b, (int(W * (1 - u)), 0))
    return img


def frame(fi):
    t = fi / FPS
    if t < T_VIRA:
        img = corrida(t)
    elif t < T_JOGO:
        img = vira(t)
    elif t < T_CTA:
        img = jogo(t)
    else:
        img = Image.new("RGBA", (W, H), (40, 110, 60, 255))
        HS.cena_cta(img, HS.SCENES[HS.CTA][0] + (t - T_CTA))
    if t < T_CTA:
        wm = logo_card(180)
        img.alpha_composite(wm, (W - wm.width - 30, 40))
    return img.convert("RGB")


def render(fi):
    return frame(fi).tobytes()


def audio():
    som = P.som
    SR = som.SR
    n = int(DUR * SR)
    fx = np.zeros(n)
    fx += P.passos(0.0, T_VIRA, 0.6)[:n] if len(P.passos(0.0, T_VIRA, 0.6)) >= n else np.pad(P.passos(0.0, T_VIRA, 0.6), (0, n))[:n]
    fx += np.pad(P.respira(0.1, T_VIRA), (0, n))[:n]
    cues = [(T_VIRA, "swoosh", 0.9), (T_JOGO, "crowd", 0.9), (T_JOGO + 0.05, "bugle", 0.8),
            (T_JOGO + 0.75, "pop", 0.6), (T_CTA, "cash", 0.6)]
    cues += [(t0 + 0.1, "boing", 0.45) for t0, _, _ in ULTRA]
    for t, nome, g in cues:
        som.add(fx, som.sn.FX[nome](), t, g)
    mus = np.zeros(n)
    tt = np.arange(n) / SR
    # na corrida: só uma batida de pulso que acelera; no jogo entra o galope do Hot Streak
    for b in np.arange(0.2, T_VIRA, 0.45 - 0.0):
        som.add(mus, som.kick(), b, 0.35)
    g = som.galope(DUR - T_JOGO + 0.5)
    som.add(mus, g / (np.abs(g).max() + 1e-9) * 0.3, T_JOGO, 1.0)
    import wave

    def grava(path, x):
        x = np.tanh(x * 1.1) / np.tanh(1.1)
        x = x / (np.abs(x).max() + 1e-9) * 0.7
        st = np.repeat((x * 32767).astype(np.int16)[:, None], 2, 1)
        with wave.open(path, "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(st.tobytes())

    com, sem = os.path.join(OUT, "sente_com.wav"), os.path.join(OUT, "sente_sem.wav")
    grava(com, fx * 0.55 + mus)
    grava(sem, fx * 0.55)
    return com, sem


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    a = ap.parse_args()
    if a.frame:
        ims = [frame(int(round(x * FPS))) for x in a.frame]
        cols = min(8, len(ims))
        rows = math.ceil(len(ims) / cols)
        sheet = Image.new("RGB", (270 * cols, 480 * rows))
        for k, im in enumerate(ims):
            sheet.paste(im.resize((270, 480), Image.LANCZOS), (270 * (k % cols), 480 * (k // cols)))
        sheet.save(os.path.join(OUT, "frames_sente.jpg"), quality=88)
        return
    com, sem = audio()
    n = int(DUR * FPS)
    base = os.path.join(OUT, "sente_com_som.mp4")
    HS.encode(base, com, n, render, list(range(n)))
    semv = os.path.join(OUT, "sente_para_musica.mp4")
    subprocess.run([HS.ffmpeg(), "-y", "-loglevel", "error", "-i", base, "-i", sem, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", semv], check=True)
    for arq in (base, semv):
        P.final_loudness(arq, arq.replace(".mp4", "_final.mp4"))
    print("ok", DUR)


if __name__ == "__main__":
    main()
