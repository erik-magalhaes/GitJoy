#!/usr/bin/env python3
"""Quiz "ZOOM RELÂMPAGO" (opção 3, escolhida pelo dono depois que o quiz da lupa ficou "feio, lento e longo").
A arte da caixa ocupa a TELA TODA num detalhe, sem moldura; contagem de 3 s num anel; depois a câmera abre
rápido e a caixa aparece inteira com o nome. Cinco jogos, ~25 s, sem narração (para a música em alta).

    python3 relampago.py --frame 0.5 3 4.5     # quadros de teste em out/frames.jpg
    python3 relampago.py                       # out/relampago_para_musica.mp4 e out/relampago_com_trilha.mp4
"""
import argparse
import math
import os
import subprocess
import sys
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "..", "comum"))
from motor import (W, H, FPS, WHITE, seg, ease, lerp, pop, quica, font, emoji, caixa, caixa_original, logo_card,  # noqa
                   cola, sombra, letreiro, pilula, encode, folha, ffmpeg)
import som  # noqa: E402

OUT = os.path.join(ROOT, "out")
INK = (16, 16, 24)
AMARELO = (255, 214, 70)
GREEN = (22, 163, 74)
DIF = {"FÁCIL": GREEN, "MÉDIO": (44, 120, 200), "DIFÍCIL": (230, 120, 10), "MUITO DIFÍCIL": (200, 40, 60),
       "IMPOSSÍVEL": (20, 20, 20)}
# (caixa, nome, dificuldade, centro do detalhe (fração da caixa), altura do recorte no início e no fim da contagem)
QUIZ = [
    ("ticket_to_ride", "Ticket to Ride", "FÁCIL", (0.62, 0.57), 0.38, 0.46),
    ("king_of_tokyo", "King of Tokyo", "MÉDIO", (0.42, 0.76), 0.30, 0.38),
    ("c_digo_secreto_imagens", "Código Secreto Imagens", "DIFÍCIL", (0.78, 0.66), 0.26, 0.33),
    ("deep_regrets", "Deep Regrets", "MUITO DIFÍCIL", (0.52, 0.20), 0.24, 0.30),
    ("segue_o_fluxo", "Segue o Fluxo", "IMPOSSÍVEL", (0.76, 0.18), 0.20, 0.27),
]
GANCHO = 1.6
RODADA = 3.6
CONTA = 2.4  # duração da contagem dentro da rodada (depois vem a revelação)
FIM0 = GANCHO + RODADA * len(QUIZ)
CTA0 = FIM0 + 2.6
DUR = CTA0 + 3.4


# ---------------------------------------------------------------- imagens
def detalhe(nome, centro, alt):
    """Recorte 9:16 da arte da caixa (alt = altura do recorte em fração da altura da caixa), em tela cheia."""
    im = caixa_original(nome)
    bw, bh = im.size
    h = bh * alt
    w = h * W / H
    # fica dentro da frente da caixa (as bordas do recorte 3D têm lateral, tampa e cantos transparentes)
    x0, x1, y0, y1 = bw * 0.10, bw * 0.92, bh * 0.07, bh * 0.93
    cx = min(max(centro[0] * bw, x0 + w / 2), x1 - w / 2)
    cy = min(max(centro[1] * bh, y0 + h / 2), y1 - h / 2)
    box = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    return im.convert("RGB").resize((W, H), Image.LANCZOS, box=box).convert("RGBA")


@lru_cache(None)
def detalhe_cache(k, alt_q):
    nome, _, _, centro, _, _ = QUIZ[k]
    return detalhe(nome, centro, alt_q / 1000)


def detalhe_em(k, alt):
    """Recorte em tela cheia; a altura é quantizada para reaproveitar quadros iguais."""
    return detalhe_cache(k, int(round(alt * 1000)))


@lru_cache(None)
def fundo_desfocado(nome):
    """Fundo da revelação: a própria arte da caixa, desfocada e escurecida, cobrindo a tela."""
    im = caixa_original(nome).convert("RGB")
    bw, bh = im.size
    w = bh * W / H
    im = im.crop((int(bw / 2 - w / 2), 0, int(bw / 2 + w / 2), bh)).resize((W // 4, H // 4), Image.BILINEAR)
    im = im.filter(ImageFilter.GaussianBlur(10)).resize((W, H), Image.BICUBIC).convert("RGBA")
    im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 120)))
    return im


@lru_cache(None)
def faixa_topo():
    """Degradê escuro no topo para o título ficar legível sobre qualquer arte."""
    im = Image.new("RGBA", (W, 520), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for y in range(520):
        d.line((0, y, W, y), fill=(0, 0, 0, int(185 * (1 - y / 520) ** 1.4)))
    return im


def anel(img, frac, n, x=540, y=1500, r=105):
    d = ImageDraw.Draw(img)
    d.ellipse((x - r, y - r, x + r, y + r), fill=(0, 0, 0, 150), outline=WHITE, width=8)
    if frac > 0:
        d.arc((x - r, y - r, x + r, y + r), -90, -90 + 360 * frac, fill=AMARELO, width=16)
    d.text((x, y + 4), str(n), font=font("Bungee-Regular.ttf", 120), fill=WHITE, anchor="mm")


def placar(img, k):
    d = ImageDraw.Draw(img)
    for i in range(len(QUIZ)):
        x = 540 + (i - 2) * 56
        if i < k:
            d.ellipse((x - 14, 410 - 14, x + 14, 410 + 14), fill=WHITE)
        elif i == k:
            d.ellipse((x - 18, 410 - 18, x + 18, 410 + 18), fill=AMARELO)
        else:
            d.ellipse((x - 14, 410 - 14, x + 14, 410 + 14), outline=WHITE, width=4)


# ---------------------------------------------------------------- cenas
def cena_gancho(img, t):
    k = min(len(QUIZ) - 1, int(t / 0.32))  # montagem relâmpago dos detalhes
    nome, _, _, centro, a0, _ = QUIZ[k]
    img.alpha_composite(detalhe_em(k, a0))
    img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 90)))
    b = 1 + 0.04 * abs(math.sin(t * 7))
    cola(img, letreiro("SÓ 1% ACERTA", 120, AMARELO, INK, 14), 540, 820, -3, pop(t, -0.3))
    cola(img, letreiro("OS 5!", 200, WHITE, INK, 16), 540, 1030, 2, pop(t, -0.15) * b)


def cena_rodada(img, t, k):
    R = GANCHO + RODADA * k
    u = t - R
    nome, titulo, dif, centro, a0, a1 = QUIZ[k]
    if u < CONTA:
        alt = lerp(a0, a1, ease(seg(u, 0, CONTA)))
        img.alpha_composite(detalhe_em(k, alt))
        img.alpha_composite(faixa_topo(), (0, 0))
        cola(img, letreiro("QUE JOGO É ESSE?", 84, WHITE, INK, 10), 540, 230)
        cola(img, pilula(f"{k + 1}/5 · {dif}", 40, DIF[dif]), 540, 335, 0, pop(t, R))
        placar(img, k)
        n = 3 - int(u / (CONTA / 3))
        anel(img, 1 - u / CONTA, max(1, n))
        if u < 0.12:  # corte seco com flash curto
            img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(200 * (1 - u / 0.12)))))
        return
    v = u - CONTA
    # revelação: a câmera "abre" rápido do detalhe para a caixa inteira
    abre = ease(seg(v, 0, 0.35))
    img.alpha_composite(fundo_desfocado(nome))
    if abre < 1:
        det = detalhe_em(k, a1)
        det = det.copy()
        det.putalpha(int(255 * (1 - abre)))
        img.alpha_composite(det)
    cx = sombra(caixa(nome, 900), 26, (0, 30), 0.55)
    cola(img, cx, 540, 860, 0, lerp(1.6, 1.0, abre), abre)
    if v >= 0.25:
        fita = Image.new("RGBA", (960, 150), (0, 0, 0, 0))
        d = ImageDraw.Draw(fita)
        d.rounded_rectangle((0, 0, 959, 149), radius=34, fill=WHITE)
        f = font("Bungee-Regular.ttf", 80)
        while d.textlength(titulo.upper(), font=f) > 880:
            f = font("Bungee-Regular.ttf", f.size - 4)
        d.text((480, 80), titulo.upper(), font=f, fill=INK, anchor="mm")
        cola(img, fita, 540, 1450, -2, pop(t, R + CONTA + 0.25, 0.3))
    if v >= 0.45:
        cola(img, pilula("TEM NA SUA VEZ!", 40, GREEN), 540, 1590, 2, pop(t, R + CONTA + 0.45, 0.3))
    placar(img, k + 1)


def cena_fim(img, t):
    img.alpha_composite(fundo_desfocado(QUIZ[-1][0]))
    a = FIM0
    cola(img, letreiro("QUANTOS VOCÊ\nACERTOU?", 112, AMARELO, INK, 14), 540, 760, -2, pop(t, a))
    b = 1 + 0.05 * abs(math.sin(t * 6))
    cola(img, letreiro("COMENTA AQUI!", 90, WHITE, INK, 12), 500, 1130, 2, pop(t, a + 0.35) * b)
    cola(img, emoji("👇", 110), 930, 1140 + 14 * math.sin(t * 9), 0, pop(t, a + 0.45))


def cena_cta(img, t):
    a = CTA0
    img.alpha_composite(fundo_desfocado(QUIZ[0][0]))
    cola(img, logo_card(430), 540, 260, 0, pop(t, a))
    for i, (nome, *_r) in enumerate(QUIZ):
        t0 = a + 0.15 + i * 0.07
        if t >= t0:
            x = 540 + (i - 2) * 175
            y = 680 + abs(i - 2) * 24
            cola(img, sombra(caixa(nome, 330), 14, (6, 14), 0.5), x, lerp(-400, y, quica(t, t0, 0.45)), (i - 2) * 6)
    itens = [(0.6, letreiro("ALUGUE ESSES\nE +160 JOGOS!", 80, WHITE, INK, 12), 1050),
             (0.9, pilula("5 DIAS DE JOGO · 3 JOGOS = 7 DIAS", 38, INK), 1250),
             (1.1, pilula("RESERVE ONLINE · RETIRE EM MAUÁ E ABC", 34, WHITE, INK, INK), 1360),
             (1.3, pilula("OU RECEBA EM CASA!", 42, GREEN), 1470),
             (1.5, pilula("LINK NA BIO · @SUAVEZ_BG", 50, (249, 115, 22)), 1600)]
    for t0, im, y in itens:
        if t >= a + t0:
            cola(img, im, 540, y, 0, pop(t, a + t0))


def frame_at(t):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    if t < GANCHO:
        cena_gancho(img, t)
    elif t < FIM0:
        cena_rodada(img, t, int((t - GANCHO) // RODADA))
    elif t < CTA0:
        cena_fim(img, t)
    else:
        cena_cta(img, t)
    if t < CTA0:
        wm = logo_card(160)
        img.alpha_composite(wm, (W - wm.width - 30, 40))
    return img


def render_frame(fi):
    return frame_at(fi / FPS).convert("RGB").tobytes()


def cues():
    c = [(0.0, "pop", 0.5), (0.15, "boing", 0.4)] + [(x * 0.32, "tick", 0.25) for x in range(5)]
    for k in range(len(QUIZ)):
        R = GANCHO + RODADA * k
        c += [(R, "whoosh", 0.5)] + [(R + j * CONTA / 3, "relogio", 0.6 + 0.1 * j) for j in range(3)]
        c += [(R + CONTA, "reveal", 0.8), (R + CONTA + 0.25, "ding", 0.4)]
    c += [(FIM0, "pop", 0.5), (FIM0 + 0.35, "boing", 0.5), (CTA0, "whoosh", 0.4), (CTA0 + 1.5, "ding", 0.6)]
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.frame:
        folha([frame_at(x).convert("RGB") for x in a.frame], os.path.join(OUT, "frames.jpg"))
        return
    wav_fx, wav_tr = os.path.join(OUT, "rel_efeitos.wav"), os.path.join(OUT, "rel_trilha.wav")
    som.build(wav_fx, DUR, cues(), musica=None, fx_ganho=0.8)
    som.build(wav_tr, DUR, cues(), musica="gameshow")
    v1 = os.path.join(OUT, "relampago_para_musica.mp4")
    encode(v1, render_frame, list(range(int(DUR * FPS))), wav_fx)
    v2 = os.path.join(OUT, "relampago_com_trilha.mp4")
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", v1, "-i", wav_tr, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-af", "volume=2dB,alimiter=limit=0.89:level=false", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", v2], check=True)


if __name__ == "__main__":
    main()
