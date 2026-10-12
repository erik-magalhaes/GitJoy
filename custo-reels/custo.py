#!/usr/bin/env python3
"""Reels SEM GRAVAÇÃO "Quanto custaria comprar tudo isso?" (ideia 7 que ele aprovou). Visual próprio: CUPOM FISCAL.
Cada caixa OFICIAL cai numa pilha, o cupom imprime a linha com o MENOR preço de loja (Compara Jogos, lowPrice do dia,
comum/dados/precos_loja.json) e o total vai subindo; carimbo do total; depois o "cupom" da Sua Vez: os 7 por 15 dias
(prazo progressivo: 7 jogos = 15 dias), preço do site (comum/dados/acervo_site.json). Sem narração.
Duas versões: _com_trilha e _para_musica (só efeitos; ele põe a música em alta no Instagram).

    python3 custo.py --frame 2 9 17 21 27
    python3 custo.py
"""
import argparse
import json
import math
import os
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "comum"))
from motor import W, H, FPS, WHITE, seg, ease, lerp, pop, quica, font, emoji, logo_card, cola, sombra, letreiro, pilula, encode, folha  # noqa
import som  # noqa: E402
from som import SR, add, env, hp, noise, t_  # noqa: E402

OUT = os.path.join(ROOT, "out")
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
INK = (24, 24, 32)
VERDE = (22, 163, 74)
VERM = (215, 35, 45)
LOJA = json.load(open(os.path.join(REPO, "comum", "dados", "precos_loja.json"), encoding="utf-8"))
SITE = json.load(open(os.path.join(REPO, "comum", "dados", "acervo_site.json"), encoding="utf-8"))
JOGOS = [  # (nome no site/Compara Jogos, nome no cupom, imagem oficial, altura na pilha, x, y do centro na pilha)
    ("Hot Streak", "HOT STREAK", "hotstreak-reels/assets/pecas/caixa.png", 200, 300, 960),
    ("Ticket to Ride", "TICKET TO RIDE", "gravados-reels/assets/lista/ticket_to_ride.png", 270, 720, 930),
    ("Coffee Rush", "COFFEE RUSH", "gravados-reels/assets/perguntas/coffee_rush.png", 290, 520, 920),
    ("Harmonies", "HARMONIES", "gravados-reels/assets/lista/harmonies.png", 250, 330, 720),
    ("Splendor Duel", "SPLENDOR DUEL", "gravados-reels/assets/lista/splendor_duel.png", 260, 760, 700),
    ("Dixit", "DIXIT", "gravados-reels/assets/lista/dixit.png", 230, 560, 640),
    ("Marrakech", "MARRAKECH", "gravados-reels/assets/perguntas/marrakech.png", 220, 450, 470),
]
PRECO = [LOJA[n][0] for n, *_ in JOGOS]
ALUGUEL = sum(SITE[n]["preco"] for n, *_ in JOGOS)
TOTAL = sum(PRECO)
GANCHO = 1.7
POR = 1.1  # 2ª versão: ele achou "um pouquinho demorado" (29 s → ~20 s)
T_TOTAL = GANCHO + POR * len(JOGOS)
T_SV = T_TOTAL + 2.0
T_COM = T_SV + 3.3
T_CTA = T_COM + 2.0
DUR = T_CTA + 3.3


def brl(v):
    s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return "R$ " + s


def mono(s):
    return ImageFont.truetype(MONO, int(s))


# ---------------------------------------------------------------- som (gaveta da registradora e impressora térmica)
def fx_cash():
    o = np.zeros(int(0.9 * SR))
    add(o, hp(noise(0.05), 2500) * env(0.05, 0.01), 0, 0.6)
    add(o, hp(noise(0.06), 1800) * env(0.06, 0.015), 0.07, 0.5)
    for f, g in ((2637, 0.5), (3520, 0.35), (5274, 0.15)):
        t = t_(0.7)
        add(o, np.sin(2 * np.pi * f * t) * env(0.7, 0.25), 0.16, g)
    return o


def fx_print():
    d = 0.45
    t = t_(d)
    zumbido = np.sign(np.sin(2 * np.pi * 180 * t)) * 0.15 + hp(noise(d), 3000) * 0.25
    return zumbido * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 22 * t))) * np.minimum(1, t / 0.02) * np.minimum(1, (d - t) / 0.05)


def fx_tum():
    t = t_(0.35)
    return np.sin(2 * np.pi * (70 + 60 * np.exp(-t / 0.05)) * t) * env(0.35, 0.12) + hp(noise(0.35), 800) * env(0.35, 0.03) * 0.3


som.FX.update({"cash": fx_cash, "print": fx_print, "tum": fx_tum})


# ---------------------------------------------------------------- imagens
@lru_cache(None)
def fundo():
    y = np.linspace(0, 1, H)[:, None]
    a, b = np.array([255, 236, 210]), np.array([250, 205, 160])
    c = a + (b - a) * y
    img = Image.fromarray(np.repeat(c[:, None, :], W, 1).reshape(H, W, 3).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(img)
    for k in range(-H, W, 70):  # listras diagonais bem leves
        d.line((k, 0, k + H, H), fill=(255, 255, 255, 40), width=26)
    d.rectangle((0, 1060, W, 1100), fill=(150, 95, 55))  # balcão
    d.rectangle((0, 1100, W, H), fill=(120, 75, 45))
    return img


@lru_cache(None)
def caixa(path, h):
    im = Image.open(os.path.join(REPO, path)).convert("RGBA")
    im = im.crop(im.getbbox())
    im = im.resize((max(2, int(im.width * h / im.height)), int(h)), Image.LANCZOS)
    return sombra(im, 12, (6, 12), 0.45)


def cupom(linhas_vis, total_vis, prog_linha, titulo="CUPOM · COMPRANDO TUDO", cor_total=VERM, rodape=None):
    """Papel térmico com serrilhado embaixo; linhas aparecem conforme 'imprimem'."""
    w, lh = 820, 54
    n = len(JOGOS)
    h = 150 + n * lh + 150 + (60 if rodape else 0)
    im = Image.new("RGBA", (w, h + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, h), fill=(253, 252, 248))
    for x in range(0, w, 30):  # serrilhado
        d.polygon([(x, h), (x + 15, h + 22), (x + 30, h)], fill=(253, 252, 248))
    d.text((w / 2, 50), titulo, font=mono(36), fill=INK, anchor="mm")
    d.line((30, 95, w - 30, 95), fill=(150, 150, 150), width=3)
    for i in range(linhas_vis):
        nm, nome_c = JOGOS[i][0], JOGOS[i][1]
        y = 125 + i * lh + lh / 2
        corte = 1.0 if i < linhas_vis - 1 else prog_linha
        txt = f"{nome_c:<16}{brl(PRECO[i]):>13}"
        txt = txt[:max(0, int(len(txt) * corte))]
        d.text((40, y), txt, font=mono(37), fill=INK, anchor="lm")
    y = 125 + n * lh + 20
    d.line((30, y, w - 30, y), fill=(150, 150, 150), width=3)
    d.text((40, y + 60), "TOTAL", font=mono(50), fill=INK, anchor="lm")
    d.text((w - 40, y + 60), brl(total_vis), font=mono(50), fill=cor_total, anchor="rm")
    if rodape:
        d.text((w / 2, y + 130), rodape, font=mono(26), fill=(110, 110, 110), anchor="mm")
    return sombra(im, 14, (0, 14), 0.35)


@lru_cache(None)
def cupom_sv():
    w, h = 820, 470
    im = Image.new("RGBA", (w, h + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, h), fill=(240, 255, 244))
    for x in range(0, w, 30):
        d.polygon([(x, h), (x + 15, h + 22), (x + 30, h)], fill=(240, 255, 244))
    d.text((w / 2, 50), "CUPOM · SUA VEZ", font=mono(36), fill=INK, anchor="mm")
    d.line((30, 95, w - 30, 95), fill=(150, 150, 150), width=3)
    d.text((40, 150), "ALUGUEL DOS 7 JOGOS", font=mono(37), fill=INK, anchor="lm")
    d.text((40, 205), "PRAZO: 15 DIAS (7 JOGOS)", font=mono(37), fill=INK, anchor="lm")
    d.line((30, 255, w - 30, 255), fill=(150, 150, 150), width=3)
    d.text((40, 315), "TOTAL", font=mono(50), fill=INK, anchor="lm")
    d.text((w - 40, 315), brl(ALUGUEL), font=mono(50), fill=VERDE, anchor="rm")
    d.text((w / 2, 410), "7 jogos x R$ 30 · preço por 5 dias,", font=mono(26), fill=(110, 110, 110), anchor="mm")
    d.text((w / 2, 442), "o prazo extra sai de graça", font=mono(26), fill=(110, 110, 110), anchor="mm")
    return sombra(im, 14, (0, 14), 0.35)


def pilha(img, t, ate=None):
    for i, (nm, nc, path, h, x, y) in enumerate(JOGOS):
        t0 = GANCHO + POR * i
        if ate is not None and i >= ate:
            break
        if t < t0:
            break
        q = quica(t, t0, 0.35)
        yy = lerp(y - 900, y, q)
        cola(img, caixa(path, h), x, yy, (-6, 4, -3, 5, -4, 3, -2)[i])


def frame(t):
    img = fundo().copy()
    if t < T_SV:
        pilha(img, t)
        if t < GANCHO + 0.2:
            cola(img, letreiro("QUANTO CUSTA\nCOMPRAR TUDO\nISSO?", 116, WHITE, INK, 14, sombra_px=8, cor_sombra=INK),
                 540, 560, -2, pop(t, 0.05, 0.45))
            cola(img, emoji("🤔", 130), 900, 330, 8, pop(t, 0.5))
        elif t < T_TOTAL:
            cola(img, letreiro("QUANTO CUSTA COMPRAR?", 64, WHITE, INK, 10), 540, 230, -1)
        # cupom imprimindo
        k = min(len(JOGOS), max(0, int((t - GANCHO) // POR) + 1)) if t >= GANCHO else 0
        prog = min(1.0, (t - GANCHO - POR * (k - 1)) / 0.3) if k else 0
        tot = sum(PRECO[:k - 1]) + (PRECO[k - 1] * min(1.0, prog) if k else 0)
        if t >= T_TOTAL:
            tot = TOTAL
        sobe = ease(seg(t, GANCHO - 0.4, GANCHO))
        cola(img, cupom(k, tot, prog, rodape="menor preço · Compara Jogos · 12/10/2026" if t >= T_TOTAL else None),
             540, lerp(2300, 1440, sobe))
        if t >= T_TOTAL:
            cola(img, letreiro(brl(TOTAL).replace(",", ",") + "!", 110, VERM, WHITE, 12), 540, 360, -6, pop(t, T_TOTAL, 0.4))
            cola(img, emoji("😱", 120), 920, 470, 10, pop(t, T_TOTAL + 0.3))
    elif t < T_COM:
        u = t - T_SV
        cola(img, letreiro("OU...", 120, WHITE, INK, 14), 540, 260, -3, pop(t, T_SV))
        cola(img, letreiro("ALUGA OS 7\nNA SUA VEZ!", 110, (255, 214, 70), INK, 14, sombra_px=8, cor_sombra=INK), 540, 520, 2,
             pop(t, T_SV + 0.2))
        cola(img, cupom_sv(), 540, lerp(2200, 1020, ease(seg(u, 0.3, 0.7))))
        if u > 1.1:
            eco = TOTAL - ALUGUEL
            cola(img, pilula(f"ECONOMIA DE {brl(eco)}", 52, VERDE), 540, 1460, -2, pop(t, T_SV + 1.1))
            cola(img, letreiro("e você ainda joga 15 dias!", 52, WHITE, INK, 8, "Poppins-Black.ttf"), 540, 1570, 0,
                 pop(t, T_SV + 1.4))
    elif t < T_CTA:
        pilha(img, 99)
        cola(img, letreiro("QUAL VOCÊ\nALUGARIA\nPRIMEIRO?", 112, (255, 214, 70), INK, 14, sombra_px=8, cor_sombra=INK), 540,
             330, -2, pop(t, T_COM))
        b = 1 + 0.04 * abs(math.sin(t * 6))
        cola(img, letreiro("COMENTA AQUI!", 84, WHITE, INK, 12), 500, 1350, 2, pop(t, T_COM + 0.35) * b)
        cola(img, emoji("👇", 100), 920, 1360 + 12 * math.sin(t * 9), 0, pop(t, T_COM + 0.45))
    else:
        u = t - T_CTA
        cola(img, logo_card(380), 540, 260, 0, pop(t, T_CTA))
        ims = [caixa(path, 165 if "hotstreak" not in path else 110) for nm, nc, path, h, x, y in JOGOS]
        larg = [im.width - 40 for im in ims]
        x = 540 - (sum(larg) - 12 * (len(ims) - 1)) / 2
        for i, im in enumerate(ims):
            cola(img, im, x + larg[i] / 2, 650 + (i % 2) * 30, (-6, 4, -3, 5, -4, 3, -2)[i], pop(t, T_CTA + 0.1 + 0.05 * i))
            x += larg[i] - 12
        itens = [(0.35, letreiro("ALUGUE NA\nSUA VEZ!", 100, (255, 214, 70), INK, 14), 950),
                 (0.55, pilula("3 JOGOS = 7 DIAS · 5 = 10 · 7 = 15", 38, INK), 1150),
                 (0.7, pilula("RESERVE ONLINE · RETIRE EM MAUÁ E ABC", 34, WHITE, INK, INK), 1255),
                 (0.8, pilula("OU RECEBA EM CASA!", 42, VERDE), 1360),
                 (0.9, pilula("LINK NA BIO · @SUAVEZ_BG", 48, (249, 115, 22)), 1480)]
        for t0, im, y in itens:
            if u >= t0:
                cola(img, im, 540, y, 0, pop(t, T_CTA + t0))
    if t < T_CTA:
        wm = logo_card(150)
        img.alpha_composite(wm, (W - wm.width - 30, 40))
    return img.convert("RGB")


def render_frame(fi):
    return frame(fi / FPS).tobytes()


def cues():
    c = [(0.0, "whoosh", 0.4), (0.05, "pop", 0.4)]
    for i in range(len(JOGOS)):
        t0 = GANCHO + POR * i
        c += [(t0 + 0.2, "tum", 0.7), (t0 + 0.03, "print", 0.5), (t0 + 0.35, "cash", 0.35)]
    c += [(T_TOTAL, "cash", 0.8), (T_TOTAL + 0.05, "boing", 0.4), (T_SV, "whoosh", 0.5), (T_SV + 0.3, "print", 0.5),
          (T_SV + 1.1, "ding", 0.6), (T_COM, "pop", 0.4), (T_COM + 0.35, "boing", 0.35), (T_CTA, "whoosh", 0.4),
          (T_CTA + 0.9, "ding", 0.5)]
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    print(f"duração {DUR:.1f} s; total loja {brl(TOTAL)}; aluguel {brl(ALUGUEL)}")
    if a.frame:
        folha([frame(x) for x in a.frame], os.path.join(OUT, "frames.jpg"))
        return
    n = int(DUR * FPS)
    for nome, musica in (("com_trilha", "gameshow"), ("para_musica", None)):
        wav = os.path.join(OUT, f"custo_{nome}.wav")
        som.build(wav, DUR, cues(), musica=musica, fx_ganho=0.5, musica_ganho=0.22)
        encode(os.path.join(OUT, f"custo_{nome}.mp4"), render_frame, list(range(n)), wav)


if __name__ == "__main__":
    main()
