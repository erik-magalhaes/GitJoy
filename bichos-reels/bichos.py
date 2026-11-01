#!/usr/bin/env python3
"""Reels "TIRA PRINT: QUE JOGADOR VOCÊ É?" (1/nov/2026, ideia dele: o tarô + bichinho engraçado).
Uma carta grande troca de bichinho a cada 2 quadros em LOOP (como a última versão de roleta-reels/taro.py); cada
carta = bichinho + tipo de jogador + o jogo do acervo de onde o bicho vem (a piada vem da mecânica do jogo).
Arte: folha 4x3 que ELES fizeram no Gemini (assets/gemini_bichos.jpg), cada quadro com fundo próprio de cor lisa →
corte RETANGULAR (sem recortar o bicho). Caixas: recortes das fotos do site.
Sem narração; _com_trilha (trilha em loop sintetizada aqui) e _para_musica; *_final.mp4 a −15,5 LUFS.

    python3 bichos.py --frame 0 0.07 1 2.5
    python3 bichos.py
"""
import argparse
import math
import os
import random
import subprocess
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "comum"))
sys.path.insert(0, os.path.join(REPO, "listas-reels"))
from motor import W, H, FPS, WHITE, font, logo_card, cola, sombra, letreiro, pilula, encode, folha, ffmpeg  # noqa
import som  # noqa: E402
from som import SR, add, env, lp, t_  # noqa: E402
from base import final_loudness  # noqa: E402

OUT = os.path.join(ROOT, "out")
GEMINI = os.path.join(ROOT, "assets", "gemini_bichos.jpg")
AC = os.path.join(REPO, "hobby-reels", "assets", "acervo")
INK = (40, 26, 18)
FUNDO = (22, 62, 76)
AMAR = (255, 199, 31)
# (tipo de jogador, nome do jogo, caixa) na ordem da folha do Gemini
BICHOS = [
    ("O QUE DIZ QUE NUNCA\nJOGOU (E GANHA)", "o BOM, o MAU e o BODE", os.path.join(AC, "o_bom_o_mau_e_o_bode.png")),
    ("O QUE GUARDA A\nCAIXA CERTINHO", "Beaver Creek", os.path.join(AC, "beaver_creek.png")),
    ("O QUE BAGUNÇA\nTODAS AS PEÇAS", "Monkey Palace", os.path.join(AC, "monkey_palace.png")),
    ("O QUE APOSTA TUDO\nNO ÚLTIMO SEGUNDO", "Camel Up", os.path.join(AC, "camel_up_second_edition.png")),
    ("O QUE DISPARA NA FRENTE\nE ESQUECE DO RESTO", "First Rat", os.path.join(AC, "first_rat.png")),
    ("O QUE TÁ ENCURRALADO\nE NÃO ADMITE", "Hive", os.path.join(AC, "hive.png")),
    ("O QUE SÓ QUER VER\nO CIRCO PEGAR FOGO", "Survive the Island", os.path.join(AC, "survive_the_island.png")),
    ("O QUE PEGA A PEÇA\nQUE VOCÊ QUERIA", "Draftosaurus", os.path.join(AC, "draftosaurus.png")),
    ("O QUE NÃO DIVIDE\nNADA COM NINGUÉM", "Tesouro do Dragão", os.path.join(AC, "tesouro_do_drag_o.png")),
    ("O QUE EMPURRA TODO\nMUNDO PRA FORA", "boop.", os.path.join(REPO, "gravados-reels", "assets", "lista", "boop.png")),
    ("O QUE SE ARREPENDE\nDE CADA JOGADA", "Deep Regrets", os.path.join(REPO, "hobby-reels", "assets", "caixas",
                                                                       "deep_regrets.png")),
    ("O QUE MENTE\nOLHANDO NO OLHO", "Mascarade", os.path.join(AC, "mascarade_second_edition.png")),
]
PERIODO = 2  # quadros em cada bichinho (15 por segundo, como o tarô final)
DUR = 240 / 30  # 240 quadros = 10 voltas de 12 bichinhos × 2 quadros → o quadro 240 é igual ao 0 (loop)
CW, CH = 780, 1080
CX, CY = 540, 965
ARTE_H = 760


# ---------------------------------------------------------------- som (loop perfeito, sem fade)
def fx_tique():
    t = t_(0.05)
    return np.sin(2 * np.pi * 2600 * t) * env(0.05, 0.015) * 0.35


def brincalhona(dur):
    """Marimba saltitante em dó maior pentatônico + baixo, em loop: passo dur/32 e o rabo das notas volta ao começo."""
    n = int(round(dur * SR))
    longo = np.zeros(n + SR)
    passo = dur / 32
    mel = [523.3, 659.3, 784.0, 659.3, 880.0, 784.0, 659.3, 587.3, 523.3, 587.3, 659.3, 784.0, 1046.5, 880.0, 784.0,
           659.3]
    for k in range(32):
        d = 0.35
        tp = t_(d)
        f = mel[k % len(mel)]
        tom = (np.sin(2 * np.pi * f * tp) + 0.35 * np.sin(2 * np.pi * 4 * f * tp) * np.exp(-tp * 40)) * np.exp(-tp * 9)
        add(longo, tom, k * passo, 0.16 if k % 2 == 0 else 0.11)
        if k % 4 == 0:  # baixo nos tempos
            fb = (130.8, 174.6, 196.0, 130.8)[(k // 8) % 4]
            tb = t_(0.5)
            add(longo, np.sin(2 * np.pi * fb * tb) * np.exp(-tb * 5), k * passo, 0.22)
        if k % 2 == 1:  # chocalho leve no contratempo
            ch = np.random.default_rng(k).standard_normal(int(0.04 * SR)) * np.exp(-np.arange(int(0.04 * SR)) / 300)
            add(longo, ch, k * passo, 0.03)
    out = longo[:n].copy()
    out[:len(longo) - n] += longo[n:]
    return lp(np.tile(out, 3), 6000)[n:2 * n]


som.MUSICAS["brincalhona"] = brincalhona
som.FX.update({"tique": fx_tique})


# ---------------------------------------------------------------- imagens
@lru_cache(None)
def celulas():
    """Acha os 12 quadros pela faixa branca entre eles."""
    a = np.asarray(Image.open(GEMINI).convert("RGB")).astype(int)
    bran = a.min(-1) > 235

    def faixas(v):
        r, s = [], None
        for i, x in enumerate(v):
            if not x and s is None:
                s = i
            if x and s is not None:
                r.append((s, i))
                s = None
        if s is not None:
            r.append((s, len(v)))
        return [x for x in r if x[1] - x[0] > 100]

    xs, ys = faixas(bran.mean(0) > 0.9), faixas(bran.mean(1) > 0.9)
    assert len(xs) == 4 and len(ys) == 3, (xs, ys)
    return [(x0 + 4, y0 + 4, x1 - 4, y1 - 4) for (y0, y1) in ys for (x0, x1) in xs]


@lru_cache(None)
def arte(k):
    """O quadro inteiro (nada cortado) na altura da arte; as laterais vêm da própria cor lisa do fundo."""
    im = Image.open(GEMINI).convert("RGB").crop(celulas()[k])
    cor = tuple(int(c) for c in np.median(np.r_[np.asarray(im)[:6].reshape(-1, 3), np.asarray(im)[-6:].reshape(-1, 3)], 0))
    s = ARTE_H / im.height
    im = im.resize((int(im.width * s), ARTE_H), Image.LANCZOS)
    out = Image.new("RGB", (CW - 60, ARTE_H), cor)
    out.paste(im, ((out.width - im.width) // 2, 0))
    return out


@lru_cache(None)
def caixa(path, h, larg):
    im = Image.open(path).convert("RGBA")
    im = im.crop(im.getbbox())
    s = min(h / im.height, larg / im.width)
    return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)


@lru_cache(None)
def carta(k):
    tipo, jogo, cx = BICHOS[k]
    c = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((0, 0, CW - 1, CH - 1), radius=40, fill=(252, 248, 240), outline=INK, width=8)
    c.paste(arte(k), (30, 30))
    d.rounded_rectangle((30, 30, CW - 31, 30 + ARTE_H), radius=22, outline=INK, width=5)
    d.multiline_text((CW / 2, 30 + ARTE_H + 78), tipo, font=font("Poppins-Black.ttf", 42), fill=INK, anchor="mm",
                     align="center", spacing=4)
    im = caixa(cx, 140, 170)
    c.alpha_composite(sombra(im, 6, (0, 4), 0.35), (int(150 - im.width / 2 - 12), int(CH - 88 - im.height / 2 - 12)))
    d.text((240, CH - 100), "JOGO:", font=font("Poppins-Black.ttf", 26), fill=(150, 110, 80), anchor="lm")
    f = font("Poppins-Black.ttf", 40 if len(jogo) < 16 else 31)
    d.text((240, CH - 62), jogo, font=f, fill=(28, 124, 150), anchor="lm")
    # sombra sólida deslocada (identidade da loja)
    s = Image.new("RGBA", (CW + 16, CH + 16), (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle((16, 16, CW + 15, CH + 15), radius=40, fill=INK)
    s.alpha_composite(c, (0, 0))
    return s


@lru_cache(None)
def fundo():
    img = Image.new("RGBA", (W, H), FUNDO + (255,))
    d = ImageDraw.Draw(img)
    for y in range(30, H, 64):
        for x in range(30 + (32 if (y // 64) % 2 else 0), W, 64):
            d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(34, 84, 100))
    return img


def frame(fi):
    t = fi / FPS
    img = fundo().copy()
    d = ImageDraw.Draw(img)
    for i in range(14):  # confetinho girando devagar (período = DUR, fecha o loop)
        rnd = random.Random(i)
        a = 2 * math.pi * t / DUR + rnd.uniform(0, 6.28)
        x = rnd.uniform(40, W - 40) + 18 * math.cos(a)
        y = rnd.uniform(120, H - 120) + 18 * math.sin(a)
        cor = ((244, 136, 37), AMAR, (250, 250, 250), (230, 80, 120))[i % 4]
        d.rounded_rectangle((x - 9, y - 5, x + 9, y + 5), radius=3, fill=cor)
    cola(img, letreiro("QUE JOGADOR\nVOCÊ É?", 92, AMAR, INK, 11, sombra_px=7, cor_sombra=INK), 540, 215, -2)
    b = 1 + 0.04 * abs(math.sin(4 * math.pi * t / DUR * 3))
    cola(img, pilula("TIRA PRINT E DESCOBRE!", 40, (230, 70, 110), WHITE, WHITE, bw=5), 540, 375, 1, b)
    k = (fi // PERIODO) % len(BICHOS)
    cola(img, carta(k), CX, CY, 0)
    if t < DUR / 2:
        cola(img, pilula("COMENTA QUAL VOCÊ TIROU!", 40, (244, 136, 37)), 540, 1565, -1)
    else:
        cola(img, pilula("ALUGA O SEU · LINK NA BIO", 40, (22, 150, 90)), 540, 1565, -1)
    wm = logo_card(130)
    img.alpha_composite(wm, (W - wm.width - 26, 30))
    return img.convert("RGB")


def render_frame(fi):
    return frame(fi).tobytes()


def cues():
    return [(i * DUR / 60, "tique", 0.16) for i in range(60)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.frame:
        folha([frame(int(round(x * FPS))) for x in a.frame], os.path.join(OUT, "frames.jpg"))
        return
    n = int(round(DUR * FPS))
    base = None
    for nome, musica in (("com_trilha", "brincalhona"), ("para_musica", None)):
        wav = os.path.join(OUT, f"bichos_{nome}.wav")
        som.build(wav, DUR + 1e-9, cues(), musica=musica, fx_ganho=0.5, musica_ganho=0.3)
        mp4 = os.path.join(OUT, f"bichos_{nome}.mp4")
        if base is None:
            encode(mp4, render_frame, list(range(n)), wav)
            base = mp4
        else:
            subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", base, "-i", wav, "-map", "0:v", "-map", "1:a",
                            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", mp4], check=True)
        final_loudness(mp4, mp4.replace(".mp4", "_final.mp4"))


if __name__ == "__main__":
    main()
