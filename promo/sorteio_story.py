#!/usr/bin/env python3
"""LEMBRETE do sorteio do HITSTER em vídeo para os STORIES (9/nov/2026, ele: "um videozinho bem rapidinho pra stories,
só pra lembrar do sorteio"). Mesmo visual das artes de `sorteio_hitster.py` (festa do Hitster: preto com luzes
rosa/ciano/amarelo, disco de vinil, equalizador), agora pulsando na batida: "LEMBRETE!", "SORTEIO DO HITSTER!", disco
girando atrás da caixa oficial, os 3 passos, "VALE ATÉ 15/11 · RESULTADO 16/11", o bônus de +2 dias e o aviso do
Instagram. Área y≈1450–1610 LIVRE (meio de baixo) para o adesivo de link/menção do post do sorteio.

    /usr/bin/python3 sorteio_story.py --frame 0.3 1 2.5 7
    /usr/bin/python3 sorteio_story.py      # out/sorteio/lembrete_{com_som,para_musica}_final.mp4
"""
import math
import os
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "becas-reels"))
import kit as K  # noqa: E402
import sons as S  # noqa: E402
import tarde as T  # noqa: E402
from tarde import E, W, H  # noqa: E402
from motor import FPS  # noqa: E402
import sorteio_hitster as SH  # noqa: E402

OUT = SH.OUT
K.OUT = OUT
DUR = 9.0
BPM = 118
BEAT = 60 / BPM


def pulso(t):
    """1 na batida, caindo rápido até a próxima."""
    return math.exp(-((t % BEAT) / BEAT) * 5)


@lru_cache(None)
def luzes():
    luz = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(luz)
    for cor, (x, y, r) in zip((SH.ROSA, SH.CIANO, SH.AMAR, SH.ROSA, SH.CIANO),
                              ((0.1, 0.12, 0.38), (0.95, 0.3, 0.4), (0.15, 0.85, 0.3), (0.9, 0.95, 0.35),
                               (0.5, 0.5, 0.22))):
        R = r * W
        d.ellipse((x * W - R, y * H - R, x * W + R, y * H + R), fill=cor + (255,))
    a = np.asarray(luz.filter(ImageFilter.GaussianBlur(W * 0.12))).astype(np.float32)
    return a[..., :3] * (a[..., 3:] / 255.0)


def fundo(t):
    k = 0.22 + 0.12 * pulso(t)
    base = np.array(SH.PRETO, np.float32)
    rgb = np.clip(base + luzes() * k, 0, 255).astype(np.uint8)
    img = Image.fromarray(rgb).convert("RGBA")
    d = ImageDraw.Draw(img)
    n = 40
    for j in range(n):  # equalizador mexendo
        x = j * W / n
        h = (0.2 + 0.8 * abs(math.sin(j * 0.55 + t * (3 + (j % 5)))) * (0.6 + 0.4 * pulso(t))) * 70
        cor = (SH.ROSA, SH.CIANO, SH.AMAR)[j % 3]
        d.rounded_rectangle((x + 4, H - h - 12, x + W / n - 4, H - 12), radius=5, fill=cor + (170,))
    return img


@lru_cache(None)
def disco():
    im = SH.disco(230)
    d = ImageDraw.Draw(im)
    c = im.width / 2
    for a0 in (20, 200):  # reflexo de luz no vinil (pra ver que gira)
        d.pieslice((c - 215, c - 215, c + 215, c + 215), a0, a0 + 18, fill=(255, 255, 255, 22))
    rs = 230 // 3
    d.ellipse((c - rs, c - rs, c + rs, c + rs), fill=SH.ROSA)
    d.text((c, c - 22), "HIT", font=E.lilita(34), fill=E.BRANCO, anchor="mm")
    d.ellipse((c - 8, c - 8, c + 8, c + 8), fill=SH.PRETO)
    return im


@lru_cache(None)
def caixa():
    return E.jogo(SH.CAIXA, 360)


@lru_cache(None)
def passo(k):
    t, c = (("Siga a @suavez_bg", SH.ROSA), ("Curta o post do sorteio", SH.CIANO),
            ("Marque 2 amigos nos comentários", SH.AMAR))[k]
    return SH.passo(k + 1, t, 860, c)


@lru_cache(None)
def seta():
    im = Image.new("RGBA", (90, 110), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.line((45, 5, 45, 80), fill=SH.AMAR, width=12)
    d.polygon([(10, 62), (80, 62), (45, 105)], fill=SH.AMAR)
    return im


def quadro(t):
    img = fundo(t)
    img.alpha_composite(E.logo(170), (W - 205, 40))
    b = 1 + 0.035 * pulso(t)
    T.poe(img, E.pilula("LEMBRETE!", 56, SH.AMAR, E.MARROM, fonte_titulo=True), W / 2, 215, t, 0.05, -3)
    if t > 0.25:
        a, s = T.surge(t, 0.25, 0.35)
        E.cola(img, E.titulo("SORTEIO DO\nHITSTER!", 122, E.BRANCO), W / 2, 410, -2, s * b, a)
    if t > 0.6:
        a, s = T.surge(t, 0.6, 0.4)
        E.cola(img, disco().rotate(-t * 150, resample=Image.BICUBIC), W / 2 + 150, 715, 0, s, a)
        E.cola(img, caixa(), W / 2 - 90, 760, -6 + 2 * math.sin(t * 2.2), s, a)
    for k in range(3):
        T.poe(img, passo(k), W / 2, 995 + k * 125, t, 1.3 + 0.35 * k, (k - 1) * 0.8)
    if t > 2.6:
        a = min(1, (t - 2.6) / 0.3)
        bob = 10 * math.sin(2 * math.pi * (t - 2.6) / 1.1)
        txt = Image.new("RGBA", (W, 130), (0, 0, 0, 0))
        dt = ImageDraw.Draw(txt)
        dt.text((W / 2 - 55, 50), "toca aqui e participa:", font=E.fig(42, 900), fill=E.BRANCO, anchor="mm")
        txt.alpha_composite(seta(), (int(W / 2 + 225), int(bob)))
        if a < 1:
            txt.putalpha(txt.getchannel("A").point(lambda v: int(v * a)))
        img.alpha_composite(txt, (0, 1325))
    T.poe(img, E.pilula(f"VALE ATÉ {SH.FIM} · RESULTADO DIA {SH.RESULTADO}", 36, SH.ROSA, E.BRANCO), W / 2, 1655,
          t, 2.3, 1)
    T.poe(img, E.pilula("E QUEM ALUGAR ATÉ 15/11 GANHA +2 DIAS DE JOGO!", 30, SH.CIANO, E.MARROM), W / 2, 1745, t,
          2.8, -1)
    if t > 3.0:
        E.cola(img, E.texto("Esta promoção não é patrocinada nem administrada pelo Instagram.", 22, (230, 230, 240),
                            620), W / 2, 1815, 0, 1, min(1, (t - 3.0) / 0.3))
    return img.convert("RGB")


def render(fi):
    return quadro(fi / FPS).tobytes()


def audio():
    ev = [(0.05, S.sino(), 0.45), (0.25, S.cartao(), 0.4), (0.6, S.carta_vira(), 0.5)]
    ev += [(1.3 + 0.35 * k, S.plim(), 0.35) for k in range(3)]
    ev += [(2.3, S.cartao(), 0.35), (2.6, S.sino(), 0.3), (2.8, S.cartao(), 0.35)]
    mus = S.musica_pop(DUR + 0.5, 0.0, BPM)
    com = os.path.join(OUT, "lembrete_com.wav")
    sem = os.path.join(OUT, "lembrete_sem.wav")
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
    K.entrega("lembrete", DUR, render, com, sem)
    print("ok")


if __name__ == "__main__":
    main()
