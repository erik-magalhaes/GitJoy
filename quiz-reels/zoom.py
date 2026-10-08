#!/usr/bin/env python3
"""Reels "Que jogo é esse?" (adivinha o jogo pelo zoom): SEM narração, só texto na tela, para o dono pôr a
MÚSICA EM ALTA no Instagram. Uma lupa mostra um detalhe da caixa e vai se afastando, com contagem 5-4-3-2-1;
depois a caixa aparece inteira com o nome. Seis rodadas, do FÁCIL ao IMPOSSÍVEL, e no fim
"Quantos você acertou? Comenta!" + tela da Sua Vez.

    python3 zoom.py --frame 1 8 12      # quadros de teste em out/frames.jpg
    python3 zoom.py                     # out/quiz_para_musica.mp4 (só efeitos) e out/quiz_com_trilha.mp4
"""
import argparse
import math
import os
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "..", "comum"))
from motor import (W, H, FPS, WHITE, seg, ease, lerp, pop, quica, font, emoji, caixa, caixa_original, logo_card,  # noqa
                   cola, sombra, letreiro, pilula, encode, previa_720p, folha)
import som  # noqa: E402

OUT = os.path.join(ROOT, "out")
ORANGE = (249, 115, 22)
ORANGE_D = (214, 84, 6)
NAVY = (15, 23, 42)
GREEN = (22, 163, 74)
DIF = {"FÁCIL": GREEN, "MÉDIO": (44, 120, 200), "DIFÍCIL": (200, 40, 60), "IMPOSSÍVEL": (20, 20, 20)}

# (caixa, nome na tela, dificuldade, centro do zoom em fração da caixa, zoom inicial)
QUIZ = [
    ("ticket_to_ride", "Ticket to Ride", "FÁCIL", (0.52, 0.55), 2.6),
    ("king_of_tokyo", "King of Tokyo", "FÁCIL", (0.44, 0.84), 2.8),
    ("dixit", "Dixit", "MÉDIO", (0.36, 0.62), 2.8),
    ("camel_up_second_edition", "Camel Up", "MÉDIO", (0.70, 0.30), 3.0),
    ("santorini", "Santorini", "DIFÍCIL", (0.30, 0.40), 3.2),
    ("wingspan", "Wingspan", "IMPOSSÍVEL", (0.80, 0.24), 3.4),
]
HOOK, RODADA = 4.0, 9.0
FIM0 = HOOK + RODADA * len(QUIZ)  # 58
CTA0 = FIM0 + 4.5
DUR = CTA0 + 5.0
LX, LY, LR = 540, 960, 390  # lupa
REVELA = 6.0  # dentro da rodada


# ---------------------------------------------------------------- peças
def fundo(t):
    """Palco de game show nas cores da Sua Vez: degradê laranja com raios girando devagar."""
    img = fundo_base().copy()
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    cx, cy, n = 540, 900, 20
    for i in range(n):
        a0 = i * 2 * math.pi / n + t * 0.12
        d.polygon([(cx, cy), (cx + 2400 * math.cos(a0), cy + 2400 * math.sin(a0)),
                   (cx + 2400 * math.cos(a0 + 0.16), cy + 2400 * math.sin(a0 + 0.16))], fill=(255, 255, 255, 22))
    img.alpha_composite(ov)
    return img


@lru_cache(None)
def fundo_base():
    yy = np.linspace(0, 1, H)[:, None, None]
    a = (np.array(ORANGE) * (1 - yy) + np.array(ORANGE_D) * 0.75 * yy) * np.ones((1, W, 1))
    return Image.fromarray(a.astype(np.uint8), "RGB").convert("RGBA")


@lru_cache(None)
def caixa_chapada(nome):
    """Caixa sobre um fundo creme liso (dentro da lupa o fundo transparente entregaria o formato)."""
    cx = caixa_original(nome)
    f = Image.new("RGBA", cx.size, (255, 244, 230, 255))
    f.alpha_composite(cx)
    return f


def recorte_zoom(nome, centro, z, lado):
    """Pedaço quadrado da caixa ampliado z vezes (z=1: a caixa inteira cabe no círculo)."""
    im = caixa_chapada(nome)
    bw, bh = im.size
    s = max(bw, bh) * 1.05 / z
    cx, cy = centro[0] * bw, centro[1] * bh
    # perto de z=1 o centro desliza para o meio da caixa
    u = seg(z, 1.0, 1.8)
    cx, cy = lerp(bw / 2, cx, u), lerp(bh / 2, cy, u)
    if s < min(bw, bh):
        cx = min(max(cx, s / 2), bw - s / 2)
        cy = min(max(cy, s / 2), bh - s / 2)
    box = (cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2)
    return _crop(im, box, lado)


def _crop(im, box, lado):
    """Recorte quadrado já redimensionado; o que cair fora da caixa fica creme."""
    bw, bh = im.size
    x0, y0, x1, y1 = box
    ix0, iy0, ix1, iy1 = max(0, x0), max(0, y0), min(bw, x1), min(bh, y1)
    s = x1 - x0
    k = lado / s
    pedaco = Image.new("RGBA", (lado, lado), (255, 244, 230, 255))
    if ix1 > ix0 and iy1 > iy0:
        dw, dh = max(1, round((ix1 - ix0) * k)), max(1, round((iy1 - iy0) * k))
        p = im.resize((dw, dh), Image.LANCZOS, box=(ix0, iy0, ix1, iy1))
        pedaco.alpha_composite(p, (int((ix0 - x0) * k), int((iy0 - y0) * k)))
    return pedaco


@lru_cache(None)
def moldura_lupa(r):
    """Aro, cabo, sombra e reflexo da lupa (sem o vidro), centrada em (r+400, r+400)."""
    c = r + 400
    im = Image.new("RGBA", (2 * c, 2 * c), (0, 0, 0, 0))
    ang = math.radians(50)
    x0, y0 = c + r * math.cos(ang), c + r * math.sin(ang)
    x1, y1 = c + (r + 330) * math.cos(ang), c + (r + 330) * math.sin(ang)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse((c - r - 30 + 14, c - r - 30 + 24, c + r + 30 + 14, c + r + 30 + 24), fill=(60, 20, 0, 110))
    sd.line((x0 + 14, y0 + 24, x1 + 14, y1 + 24), fill=(60, 20, 0, 110), width=86)
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
    d = ImageDraw.Draw(im)
    d.line((x0, y0, x1, y1), fill=NAVY, width=86)
    d.ellipse((x1 - 43, y1 - 43, x1 + 43, y1 + 43), fill=NAVY)
    d.line((x0, y0, x0 + 90 * math.cos(ang), y0 + 90 * math.sin(ang)), fill=(200, 205, 215), width=96)
    # buraco do vidro (a sombra não pode ficar por cima do detalhe)
    a = np.asarray(im).copy()
    yy, xx = np.mgrid[:2 * c, :2 * c]
    a[(xx - c) ** 2 + (yy - c) ** 2 <= r * r] = 0
    im = Image.fromarray(a, "RGBA")
    d = ImageDraw.Draw(im)
    rf = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(rf).arc((c - r * 0.8, c - r * 0.8, c + r * 0.8, c + r * 0.8), 200, 250, fill=(255, 255, 255, 120),
                           width=22)
    im.alpha_composite(rf.filter(ImageFilter.GaussianBlur(3)))
    d = ImageDraw.Draw(im)
    d.ellipse((c - r - 30, c - r - 30, c + r + 30, c + r + 30), outline=WHITE, width=34)
    d.ellipse((c - r - 32, c - r - 32, c + r + 32, c + r + 32), outline=NAVY, width=6)
    return im


@lru_cache(None)
def mascara_circulo(r):
    m = Image.new("L", (2 * r, 2 * r), 0)
    ImageDraw.Draw(m).ellipse((0, 0, 2 * r - 1, 2 * r - 1), fill=255)
    return m


def lupa(img, detalhe, cx, cy, r, rot=0.0):
    """Lupa com o detalhe (quadrado 2r x 2r) dentro do vidro."""
    lente = Image.new("RGBA", (2 * r, 2 * r), (0, 0, 0, 0))
    lente.paste(detalhe, (0, 0), mascara_circulo(r))
    fr = moldura_lupa(r).copy()
    c = r + 400
    fr.alpha_composite(lente, (c - r, c - r))
    # o aro por cima do vidro
    fr.alpha_composite(moldura_lupa(r))
    cola(img, fr, cx, cy, rot)


def placar(img, k, feitos):
    d = ImageDraw.Draw(img)
    for i in range(len(QUIZ)):
        x = 540 + (i - 2.5) * 80
        if i < feitos:
            d.ellipse((x - 22, 350 - 22, x + 22, 350 + 22), fill=WHITE, outline=WHITE, width=5)
        elif i == k:
            d.ellipse((x - 26, 350 - 26, x + 26, 350 + 26), fill=(255, 220, 90), outline=WHITE, width=5)
        else:
            d.ellipse((x - 22, 350 - 22, x + 22, 350 + 22), outline=WHITE, width=5)


def cabecalho(img, t, k=-1, feitos=0):
    cola(img, letreiro("QUE JOGO É ESSE?", 70, WHITE, NAVY, 10), 500, 250, 0, pop(t, -0.3))
    cola(img, emoji("🔍", 80), 905, 250, 8 * math.sin(t * 3))
    placar(img, k, feitos)


def confete(img, t, t0, seed=0, n=70, cx=540, cy=900):
    u = t - t0
    if u < 0 or u > 2.6:
        return
    rng = np.random.default_rng(seed)
    d = ImageDraw.Draw(img)
    cores = [(255, 220, 90), WHITE, (22, 163, 74), (44, 120, 200), (230, 60, 90)]
    for _ in range(n):
        a = rng.uniform(0, 2 * math.pi)
        v = rng.uniform(500, 1300)
        x = cx + math.cos(a) * v * u
        y = cy + math.sin(a) * v * u + 900 * u * u
        s = rng.uniform(10, 20)
        rot = rng.uniform(0, 6) + u * 8
        pts = [(x + s * math.cos(rot + q * math.pi / 2), y + s * 0.5 * math.sin(rot + q * math.pi / 2)) for q in range(4)]
        d.polygon(pts, fill=cores[rng.integers(len(cores))])


# ---------------------------------------------------------------- cenas
def cena_gancho(img, t):
    cabecalho(img, t)
    some = 1 - ease(seg(t, HOOK - 0.9, HOOK - 0.5))
    cola(img, letreiro("SÓ 1% ACERTA", 120, (255, 230, 90), NAVY, 14), 540, 560, -2, pop(t, -0.3), some)
    b = 1 + 0.05 * abs(math.sin(t * 4))
    cola(img, letreiro("OS 6!", 190, WHITE, NAVY, 16), 540, 730, 2, pop(t, -0.15) * b, some)
    # a lupa passeia por detalhes de todas as caixas (um "trailer")
    k = int(t / 0.55) % len(QUIZ)
    nome, _, _, centro, z0 = QUIZ[k]
    sai = ease(seg(t, HOOK - 0.6, HOOK))
    x, y = lerp(540, LX, sai), lerp(1230, LY, sai)
    r = int(lerp(280, LR, sai))
    lupa(img, recorte_zoom(nome, centro, z0 * 1.2, 2 * r), x, y, r, 4 * math.sin(t * 2))
    if t < HOOK - 0.5:
        cola(img, letreiro("PAUSA E CHUTA!", 50, WHITE, NAVY, 8), 540, 1660, 0, pop(t, 0.6))


def cena_rodada(img, t, k):
    R = HOOK + RODADA * k
    u = t - R
    nome, titulo, dif, centro, z0 = QUIZ[k]
    cabecalho(img, t, k, k)
    cola(img, pilula(f"RODADA {k + 1} · {dif}", 44, DIF[dif]), 540, 450, 0, pop(t, R + 0.05))
    if u < REVELA:
        z = lerp(z0, max(1.35, z0 * 0.5), ease(seg(u, 0.3, REVELA)))
        entra = ease(seg(u, 0, 0.45)) if k > 0 else 1.0
        x = lerp(1500, LX, entra)
        treme = 3 * math.sin(u * 40) * seg(u, REVELA - 1.0, REVELA)  # treme no fim da contagem
        lupa(img, recorte_zoom(nome, centro, z, 2 * LR), x + treme, LY, LR, lerp(20, 0, entra))
        if u >= 1.0:  # contagem 5..1
            n = 5 - int(u - 1.0)
            t0 = R + 1.0 + (5 - n)
            cor = WHITE if n > 2 else (255, 230, 90)
            cola(img, letreiro(str(n), 170, cor, NAVY, 14), 540, 1530, 0, pop(t, t0, 0.25))
        if 0.3 <= u < 1.0:
            cola(img, letreiro("VALENDO!", 90, (255, 230, 90), NAVY, 12), 540, 1530, -3, pop(t, R + 0.3))
    else:
        v = u - REVELA
        if v < 0.25:  # flash
            img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * (1 - v / 0.25)))))
        confete(img, t, R + REVELA, seed=k, cy=900)
        sai = ease(seg(u, RODADA - 0.45, RODADA))
        cx_ = sombra(caixa(nome, 820), 22, (16, 30), 0.5, (60, 20, 0))
        cola(img, cx_, lerp(540, -700, sai), 950, lerp(0, -15, sai), pop(t, R + REVELA, 0.4))
        if v >= 0.3:
            fita = Image.new("RGBA", (900, 140), (0, 0, 0, 0))
            d = ImageDraw.Draw(fita)
            d.rounded_rectangle((0, 0, 899, 139), radius=30, fill=NAVY, outline=WHITE, width=6)
            f = font("Bungee-Regular.ttf", 76)
            while d.textlength(titulo.upper(), font=f) > 820:
                f = font("Bungee-Regular.ttf", f.size - 4)
            d.text((450, 74), titulo.upper(), font=f, fill=WHITE, anchor="mm")
            cola(img, fita, lerp(540, -700, sai), 1440, -2, pop(t, R + REVELA + 0.3))
        if v >= 0.6:
            cola(img, pilula("TEM NA SUA VEZ!", 44, GREEN), lerp(540, -700, sai), 1590, 2, pop(t, R + REVELA + 0.6))


def cena_fim(img, t):
    a = FIM0
    cabecalho(img, t, -1, len(QUIZ))
    cola(img, letreiro("QUANTOS VOCÊ\nACERTOU?", 104, (255, 230, 90), NAVY, 14), 540, 640, -2, pop(t, a + 0.05))
    linhas = [("0 a 2", "😅", "BORA JOGAR MAIS!"), ("3 a 4", "😎", "JOGADOR DE RESPEITO"),
              ("5 ou 6", "🧠", "MESTRE DO TABULEIRO")]
    for i, (n, e, txt) in enumerate(linhas):
        t0 = a + 0.6 + i * 0.35
        if t >= t0:
            card = Image.new("RGBA", (900, 150), (0, 0, 0, 0))
            d = ImageDraw.Draw(card)
            d.rounded_rectangle((0, 0, 899, 149), radius=36, fill=WHITE, outline=NAVY, width=6)
            d.text((40, 75), n, font=font("Bungee-Regular.ttf", 52), fill=ORANGE_D, anchor="lm")
            card.alpha_composite(emoji(e, 84), (270, 33))
            d.text((375, 75), txt, font=font("Poppins-Black.ttf", 40), fill=NAVY, anchor="lm")
            cola(img, card, 540, 960 + i * 175, (-1) ** i * 1.5, pop(t, t0))
    if t >= a + 1.9:
        b = 1 + 0.05 * abs(math.sin(t * 5))
        cola(img, letreiro("COMENTA AQUI!", 84, WHITE, NAVY, 12), 500, 1560, -2, pop(t, a + 1.9) * b)
        cola(img, emoji("👇", 96), 920, 1560 + 12 * math.sin(t * 8))


def cena_cta(img, t):
    a = CTA0
    cola(img, logo_card(430), 540, 250, 0, pop(t, a + 0.05))
    for i, (nome, *_r) in enumerate(QUIZ):
        t0 = a + 0.3 + i * 0.1
        if t >= t0:
            v = quica(t, t0, 0.5)
            x = 540 + (i - 2.5) * 150
            y = 700 + abs(i - 2.5) * 22
            cola(img, sombra(caixa(nome, 330), 14, (6, 14), 0.4, (60, 20, 0)), x, lerp(-400, y, v), (i - 2.5) * 6)
    itens = [(1.0, letreiro("ALUGUE ESSES\nE +160 JOGOS!", 76, WHITE, NAVY, 12), 1070),
             (1.4, pilula("5 DIAS DE JOGO · 3 JOGOS = 7 DIAS", 38, NAVY), 1260),
             (1.8, pilula("RESERVE ONLINE · RETIRE EM MAUÁ E ABC", 34, WHITE, NAVY, NAVY), 1375),
             (2.1, pilula("OU RECEBA EM CASA!", 42, GREEN), 1485),
             (2.5, pilula("LINK NA BIO · @SUAVEZ_BG", 50, NAVY), 1620)]
    for t0, im, y in itens:
        if t >= a + t0:
            b = 1 + 0.04 * abs(math.sin(t * 5)) if y == 1620 else 1
            cola(img, im, 540, y, 0, pop(t, a + t0) * b)


def frame_at(t):
    img = fundo(t)
    if t < HOOK:
        cena_gancho(img, t)
    elif t < FIM0:
        cena_rodada(img, t, int((t - HOOK) // RODADA))
    elif t < CTA0:
        cena_fim(img, t)
    else:
        cena_cta(img, t)
    if t < CTA0:
        wm = logo_card(170)
        img.alpha_composite(wm, (W - wm.width - 30, 40))
    # transição suave entre o fim e o CTA
    for tc in (FIM0, CTA0):
        if abs(t - tc) < 0.2:
            img.alpha_composite(Image.new("RGBA", (W, H), (255, 240, 220, int(230 * (1 - abs(t - tc) / 0.2)))))
    return img


def render_frame(fi):
    return frame_at(fi / FPS).convert("RGB").tobytes()


def cues():
    c = [(0.0, "pop", 0.5), (0.1, "boing", 0.4)]
    c += [(x * 0.55, "tick", 0.25) for x in range(7)]
    for k in range(len(QUIZ)):
        R = HOOK + RODADA * k
        c += [(R, "whoosh", 0.5), (R + 0.05, "pop", 0.4), (R + 0.3, "pop", 0.4)]
        c += [(R + 1.0 + j, "relogio", 0.6 + 0.08 * j) for j in range(5)]
        c += [(R + REVELA, "reveal", 0.8), (R + REVELA + 0.1, "plateia", 0.5), (R + REVELA + 0.6, "ding", 0.4),
              (R + RODADA - 0.45, "whoosh", 0.4)]
    c += [(FIM0, "pop", 0.5)] + [(FIM0 + 0.6 + i * 0.35, "pop", 0.4) for i in range(3)] + [(FIM0 + 1.9, "boing", 0.5)]
    c += [(CTA0, "whoosh", 0.4)] + [(CTA0 + 0.3 + i * 0.1 + 0.3, "pop", 0.3) for i in range(6)]
    c += [(CTA0 + x, "pop", 0.4) for x in (1.0, 1.4, 1.8, 2.1)] + [(CTA0 + 2.5, "ding", 0.6)]
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.frame:
        folha([frame_at(x).convert("RGB") for x in a.frame], os.path.join(OUT, "frames.jpg"))
        return
    n = int(DUR * FPS)
    wav_fx = os.path.join(OUT, "efeitos.wav")
    wav_tr = os.path.join(OUT, "trilha.wav")
    som.build(wav_fx, DUR, cues(), musica=None, fx_ganho=0.8)
    som.build(wav_tr, DUR, cues(), musica="gameshow")
    encode(os.path.join(OUT, "quiz_para_musica.mp4"), render_frame, list(range(n)), wav_fx)
    # a versão com trilha reaproveita o vídeo: só troca o áudio
    import subprocess
    from motor import ffmpeg
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", os.path.join(OUT, "quiz_para_musica.mp4"), "-i", wav_tr,
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    os.path.join(OUT, "quiz_com_trilha.mp4")], check=True)
    previa_720p(os.path.join(OUT, "quiz_com_trilha.mp4"), os.path.join(OUT, "quiz_com_trilha_720p.mp4"))
    previa_720p(os.path.join(OUT, "quiz_para_musica.mp4"), os.path.join(OUT, "quiz_para_musica_720p.mp4"))


if __name__ == "__main__":
    main()
