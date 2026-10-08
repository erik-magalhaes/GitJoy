#!/usr/bin/env python3
"""Reels "BYE BYE..." para a trend com a música American Pie ("bye, bye, Miss American Pie").
Visual retrô anos 70 (a música é de 1971): raios de sol laranja/mostarda/marrom, letras com sombra 3D e
polaroides que dão tchau e voam para fora. Cada "BYE BYE" é uma coisa chata de que a pessoa se despede;
no fim, "OI, SUA VEZ!". SEM narração e SEM a música (o dono põe o áudio da trend no Instagram).

    python3 byebye.py --frame 1 5 45     # quadros de teste em out/frames.jpg
    python3 byebye.py                    # out/byebye_para_musica.mp4 (só efeitos) e out/byebye_com_trilha.mp4
"""
import argparse
import math
import os
import subprocess
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "..", "comum"))
from motor import (W, H, FPS, WHITE, seg, ease, lerp, pop, quica, font, emoji, caixa, logo_card, cola, sombra,  # noqa
                   pilula, encode, previa_720p, folha, ffmpeg)
import som  # noqa: E402

OUT = os.path.join(ROOT, "out")
CREME = (250, 238, 212)
MARROM = (92, 46, 26)
LARANJA = (228, 112, 38)
MOSTARDA = (236, 172, 52)
VERMELHO = (196, 66, 46)
VERDE = (70, 130, 70)

# (texto do adeus, emoji da polaroide, cor da "foto")
ADEUS = [
    ("domingo rolando\no celular", "📱", (110, 170, 200)),
    ("pagar R$ 400 num jogo\nque você jogou 1 vez", "💸", (170, 120, 190)),
    ("comprar jogo no escuro\ne se arrepender", "🙈", (130, 180, 120)),
    ("estante cheia de\ncaixa parada", "📦", (240, 190, 120)),
    ("maratona de série...\nde novo", "📺", (110, 170, 200)),
    ("\"não tem nada\npra fazer hoje\"", "🥱", (170, 120, 190)),
    ("rolê que nunca sai\ndo grupo do zap", "💬", (130, 180, 120)),
    ("almoço de família\nsem assunto", "🦗", (240, 190, 120)),
    ("rolê caro no\nshopping", "🛍️", (110, 170, 200)),
    ("aquele jogo que\nnunca acaba", "⏳", (170, 120, 190)),
]
GANCHO = 2.6
ITEM = 4.0
OI0 = GANCHO + ITEM * len(ADEUS)  # 42.6
COM0 = OI0 + 14.0
CTA0 = COM0 + 4.0
DUR = CTA0 + 5.0
CAIXAS = ["dixit", "king_of_tokyo", "ticket_to_ride", "camel_up_second_edition", "wingspan", "root", "santorini"]


# ---------------------------------------------------------------- peças
@lru_cache(None)
def raios(fase):
    img = Image.new("RGBA", (W, H), CREME + (255,))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    cx, cy, n = 540, 2050, 24
    cores = [LARANJA, MOSTARDA, VERMELHO, MOSTARDA]
    for i in range(n):
        a0 = math.pi + i * math.pi / n + fase
        a1 = a0 + math.pi / n * 0.5
        d.polygon([(cx, cy), (cx + 3000 * math.cos(a0), cy + 3000 * math.sin(a0)),
                   (cx + 3000 * math.cos(a1), cy + 3000 * math.sin(a1))], fill=cores[i % 4] + (60,))
    img.alpha_composite(ov)
    return img


def fundo(t, sobe=0.0):
    """Raios de sol retrô girando devagar e o sol de listras no rodapé (sobe no 'OI, SUA VEZ')."""
    fase = round(math.sin(t * 0.35) * 0.05, 3)
    img = raios(fase).copy()
    d = ImageDraw.Draw(img)
    cy = 2050 - 60 - sobe * 380
    for k, c in enumerate((MOSTARDA, LARANJA, VERMELHO, MARROM)):
        r = 460 - k * 95 + sobe * 60
        d.ellipse((540 - r, cy - r, 540 + r, cy + r), fill=c)
    return img


@lru_cache(None)
def retro(txt, size, cor=CREME, sombra_=MARROM, prof=12, contorno=MARROM, fonte="AlfaSlabOne-Regular.ttf"):
    """Letreiro anos 70: texto com sombra 3D em degraus e contorno."""
    f = font(fonte, size)
    linhas = txt.split("\n")
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    lw = max(tmp.textlength(l, font=f) for l in linhas)
    lh = size * 1.12
    im = Image.new("RGBA", (int(lw + prof * 2 + 40), int(lh * len(linhas) + prof * 2 + 40)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k, l in enumerate(linhas):
        x, y = im.width / 2 - prof / 2, 20 + k * lh + size * 0.55
        for s in range(prof, 0, -1):
            d.text((x + s, y + s), l, font=f, fill=sombra_, anchor="mm", stroke_width=4, stroke_fill=sombra_)
        d.text((x, y), l, font=f, fill=cor, anchor="mm", stroke_width=4, stroke_fill=contorno)
    return im


@lru_cache(None)
def polaroide(k, w=600):
    """Polaroide com a 'foto' (fundo colorido + emoji) e sombra suave."""
    _, em, cor = ADEUS[k]
    hh = int(w * 1.18)
    p = Image.new("RGBA", (w, hh), (255, 253, 247, 255))
    fw = w - 56
    yy = np.linspace(0, 1, fw)[:, None, None]
    grad = (np.array(cor) * (1.08 - 0.25 * yy)).clip(0, 255) * np.ones((1, fw, 1))
    foto = Image.fromarray(grad.astype(np.uint8), "RGB").convert("RGBA")
    e = emoji(em, int(fw * 0.6))
    sh = Image.new("RGBA", e.size, (0, 0, 0, 0))
    sh.putalpha(e.getchannel("A").point(lambda v: int(v * 0.3)))
    foto.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), (fw // 2 - e.width // 2 + 10, fw // 2 - e.height // 2 + 18))
    foto.alpha_composite(e, (fw // 2 - e.width // 2, fw // 2 - e.height // 2))
    p.alpha_composite(foto, (28, 28))
    d = ImageDraw.Draw(p)
    d.text((w / 2, fw + 28 + (hh - fw - 28) / 2), f"#{k + 1}", font=font("AlfaSlabOne-Regular.ttf", 54), fill=MARROM,
           anchor="mm")
    return sombra(p, 16, (10, 20), 0.35, (60, 30, 10))


@lru_cache(None)
def etiqueta(txt, size=62):
    linhas = txt.split("\n")
    f = font("Poppins-Black.ttf", size)
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    w = int(max(tmp.textlength(l, font=f) for l in linhas) + 90)
    h = int(len(linhas) * size * 1.3 + 50)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=36, fill=CREME, outline=MARROM, width=6)
    for i, l in enumerate(linhas):
        d.text((w / 2, 25 + size * 0.65 + i * size * 1.3), l, font=f, fill=MARROM, anchor="mm")
    return im


# ---------------------------------------------------------------- cenas
def cena_gancho(img, t):
    for i, k in enumerate((3, 1, 0)):  # pilha de polaroides caindo na mesa
        v = quica(t, -0.35 + i * 0.12, 0.5)
        cola(img, polaroide(k, 470), 540 + (i - 1) * 190, lerp(-400, 1020 + abs(i - 1) * 50, v), (i - 1) * -12)
    cola(img, retro("10 COISAS PRA\nDAR BYE BYE", 108, CREME, MARROM, 14), 540, 400, -2, pop(t, -0.3))
    cola(img, emoji("👋", 160), 880, 640, 20 * math.sin(t * 9))
    if t >= 0.9:
        cola(img, etiqueta("de qual você já deu?", 54), 540, 1500, 2, pop(t, 0.9))


def cena_adeus(img, t, k):
    a = GANCHO + ITEM * k
    u = t - a
    txt, _, _ = ADEUS[k]
    b = 1 + 0.08 * max(0.0, 1 - u / 0.3)
    cola(img, retro("BYE BYE,", 150, CREME, MARROM, 14), 540, 290, -2 if k % 2 else 2, b)
    # polaroide cai, fica, e no fim sai voando dando tchau
    cai = quica(t, a, 0.5)
    vai = ease(seg(u, ITEM - 0.65, ITEM))
    rot = (5 if k % 2 else -5) + 3 * math.sin(u * 2.2)
    x = lerp(540, 1500 if k % 2 == 0 else -420, vai)
    y = lerp(-500, 850, cai) - 700 * vai
    cola(img, polaroide(k), x, y, rot + vai * (40 if k % 2 == 0 else -40))
    # mãozinha dando tchau
    if u < ITEM - 0.5:
        cola(img, emoji("👋", 170), x + (300 if k % 2 == 0 else -300), y - 330, 25 * math.sin(u * 11), pop(t, a + 0.3))
    if u >= 0.25:
        alpha = 1 - seg(u, ITEM - 0.5, ITEM - 0.2)
        cola(img, etiqueta(txt), 540, 1430, -1 if k % 2 else 1, pop(t, a + 0.25), alpha)


def cena_oi(img, t):
    a = OI0
    u = t - a
    cola(img, retro("OI,", 170, MOSTARDA, MARROM, 14), 540, 270, -3, pop(t, a + 0.1))
    cola(img, retro("SUA VEZ!", 160, CREME, MARROM, 14), 540, 450, 2, pop(t, a + 0.45))
    if u < 3.6:
        cola(img, sombra(logo_card(560), 20, (0, 20), 0.35, (60, 30, 10)), 540, 900, 0, pop(t, a + 0.9))
        cola(img, etiqueta("locação de jogos de tabuleiro\nem Mauá e no ABC", 50), 540, 1250, 0, pop(t, a + 1.4))
        return
    # caixas do acervo em leque
    for i, n in enumerate(CAIXAS):
        t0 = a + 3.6 + i * 0.1
        if t >= t0:
            v = quica(t, t0, 0.5)
            cola(img, sombra(caixa(n, 300), 14, (8, 14), 0.4, (60, 30, 10)), 540 + (i - 3) * 125,
                 lerp(-400, 860 + abs(i - 3) * 28, v), (i - 3) * 7)
    if u < 7.1:
        cola(img, etiqueta("+160 JOGOS\nPRA ALUGAR", 76), 540, 1300, -2, pop(t, a + 4.1))
    elif u < 10.6:
        cola(img, etiqueta("5 DIAS DE JOGO", 76), 540, 1250, -2, pop(t, a + 7.1))
        cola(img, retro("a partir de R$ 15", 88, MOSTARDA, MARROM, 10), 540, 1420, 1, pop(t, a + 7.5))
    else:
        cola(img, etiqueta("E QUANTO MAIS JOGOS,\nMAIS DIAS!", 60), 540, 1210, -1, pop(t, a + 10.6))
        for i, (j, d) in enumerate(((3, 7), (5, 10), (7, 15))):
            t0 = a + 11.0 + i * 0.45
            if t >= t0:
                cor = (MOSTARDA, LARANJA, VERMELHO)[i]
                cola(img, pilula(f"{j} JOGOS = {d} DIAS", 50, cor, CREME, MARROM, "AlfaSlabOne-Regular.ttf", 6),
                     540, 1390 + i * 125, (-1) ** i * 2, pop(t, t0))


def cena_comenta(img, t):
    a = COM0
    cola(img, retro("DE QUAL VOCÊ VAI\nDAR BYE BYE?", 96, CREME, MARROM, 12), 540, 380, -2, pop(t, a + 0.05))
    for k in range(len(ADEUS)):  # mini polaroides numeradas
        t0 = a + 0.4 + k * 0.08
        if t >= t0:
            x = 540 + ((k % 5) - 2) * 190
            y = 830 + (k // 5) * 300
            cola(img, polaroide(k, 170), x, y, ((k * 37) % 11) - 5, pop(t, t0))
    if t >= a + 1.4:
        b = 1 + 0.05 * abs(math.sin(t * 5))
        cola(img, etiqueta("COMENTA O NÚMERO!", 70), 500, 1400, -2, pop(t, a + 1.4) * b)
        cola(img, emoji("👇", 110), 930, 1400 + 12 * math.sin(t * 8))


def cena_cta(img, t):
    a = CTA0
    cola(img, sombra(logo_card(440), 18, (0, 18), 0.3, (60, 30, 10)), 540, 250, 0, pop(t, a + 0.05))
    for i, n in enumerate(CAIXAS[:5]):
        t0 = a + 0.3 + i * 0.1
        if t >= t0:
            cola(img, sombra(caixa(n, 300), 14, (8, 14), 0.4, (60, 30, 10)), 540 + (i - 2) * 160,
                 lerp(-400, 700 + abs(i - 2) * 26, quica(t, t0, 0.5)), (i - 2) * 7)
    itens = [(1.0, retro("ALUGUE NA SUA VEZ!", 84, CREME, MARROM, 10), 1030),
             (1.4, pilula("5 DIAS DE JOGO · 3 JOGOS = 7 DIAS", 38, MARROM, CREME, MARROM), 1190),
             (1.8, pilula("RESERVE ONLINE · RETIRE EM MAUÁ E ABC", 34, CREME, MARROM, MARROM), 1305),
             (2.1, pilula("OU RECEBA EM CASA!", 42, VERDE, CREME, MARROM), 1415),
             (2.5, pilula("LINK NA BIO · @SUAVEZ_BG", 50, VERMELHO, CREME, MARROM), 1550)]
    for t0, im, y in itens:
        if t >= a + t0:
            b = 1 + 0.04 * abs(math.sin(t * 5)) if y == 1550 else 1
            cola(img, im, 540, y, 0, pop(t, a + t0) * b)


def frame_at(t):
    sobe = ease(seg(t, OI0, OI0 + 1.0)) * (1 - ease(seg(t, COM0, COM0 + 0.6)))
    img = fundo(t, sobe)
    if t < GANCHO:
        cena_gancho(img, t)
    elif t < OI0:
        cena_adeus(img, t, int((t - GANCHO) // ITEM))
    elif t < COM0:
        cena_oi(img, t)
    elif t < CTA0:
        cena_comenta(img, t)
    else:
        cena_cta(img, t)
    if t < CTA0:
        wm = logo_card(170)
        img.alpha_composite(wm, (W - wm.width - 30, 40))
    for tc in (GANCHO, OI0, COM0, CTA0):  # piscada de luz quente nas viradas
        if abs(t - tc) < 0.18:
            img.alpha_composite(Image.new("RGBA", (W, H), CREME + (int(230 * (1 - abs(t - tc) / 0.18)),)))
    return img


def render_frame(fi):
    return frame_at(fi / FPS).convert("RGB").tobytes()


def cues():
    c = [(0.0, "pop", 0.4), (0.15, "pop", 0.3), (0.3, "pop", 0.3), (0.9, "pop", 0.4)]
    for k in range(len(ADEUS)):
        a = GANCHO + ITEM * k
        c += [(a, "flip", 0.6), (a + 0.4, "carimbo", 0.35), (a + 0.25, "pop", 0.35), (a + ITEM - 0.65, "tchau", 0.6)]
    c += [(OI0 + 0.1, "chime", 0.6), (OI0 + 0.45, "pop", 0.5), (OI0 + 0.9, "ding", 0.5), (OI0 + 1.4, "pop", 0.4)]
    c += [(OI0 + 3.6 + i * 0.1 + 0.3, "pop", 0.3) for i in range(len(CAIXAS))] + [(OI0 + 4.1, "pop", 0.5)]
    c += [(OI0 + 7.1, "pop", 0.5), (OI0 + 7.5, "ding", 0.5), (OI0 + 10.6, "pop", 0.5)]
    c += [(OI0 + 11.0 + i * 0.45, "barra", 0.6) for i in range(3)]
    c += [(COM0, "whoosh", 0.4)] + [(COM0 + 0.4 + k * 0.08, "tick", 0.2) for k in range(10)] + [(COM0 + 1.4, "boing", 0.5)]
    c += [(CTA0, "whoosh", 0.4)] + [(CTA0 + x, "pop", 0.4) for x in (1.0, 1.4, 1.8, 2.1)] + [(CTA0 + 2.5, "ding", 0.6)]
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
    som.build(wav_tr, DUR, cues(), musica="retro70")
    v1 = os.path.join(OUT, "byebye_para_musica.mp4")
    encode(v1, render_frame, list(range(n)), wav_fx)
    v2 = os.path.join(OUT, "byebye_com_trilha.mp4")
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", v1, "-i", wav_tr, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", v2], check=True)
    previa_720p(v1, os.path.join(OUT, "byebye_para_musica_720p.mp4"))
    previa_720p(v2, os.path.join(OUT, "byebye_com_trilha_720p.mp4"))


if __name__ == "__main__":
    main()
