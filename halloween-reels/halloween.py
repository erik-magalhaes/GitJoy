#!/usr/bin/env python3
"""Reels de Halloween SEM GRAVAÇÃO (ideia 6 da lista que ele aprovou): "6 jogos pra um Halloween de arrepiar".
Visual próprio (diferente do trailer do Final Girl, que é vermelho/lanterna): noite ROXA com lua cheia, morcegos voando,
névoa lisa e lápides; cada caixa OFICIAL sobe da névoa com brilho laranja de abóbora, nome em Creepster laranja, frase e
jogadores/tempo (dados do site da Sua Vez, comum/dados/acervo_site.json). Sem narração: tudo escrito na tela.
Duas versões: _com_trilha (terror do som_fg) e _para_musica (só efeitos; ele põe a música em alta no Instagram).

    python3 halloween.py --frame 1 5 26 30     # quadros de teste em out/frames.jpg
    python3 halloween.py                       # out/halloween_com_trilha.mp4 e out/halloween_para_musica.mp4
"""
import argparse
import math
import os
import random
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "comum"))
sys.path.insert(0, os.path.join(REPO, "finalgirl-reels"))
from motor import W, H, FPS, WHITE, seg, ease, lerp, pop, font, emoji, logo_card, cola, sombra, letreiro, pilula, encode, folha  # noqa
import som  # noqa: E402
import som_fg  # noqa: E402,F401  (registra a música "terror" e os efeitos braam/trovão/riser)

OUT = os.path.join(ROOT, "out")
AS = os.path.join(ROOT, "assets")
CREEP = os.path.join(REPO, "voodoo-reels", "assets", "fonts", "Creepster-Regular.ttf")
LARANJA = (255, 138, 20)
ROXO = (150, 70, 220)
INK = (14, 6, 24)
JOGOS = [  # (arquivo, nome na tela, frase, jogadores · tempo) — conferido no site da Sua Vez
    ("finalgirl", "FINAL GIRL", "Sobreviva ao assassino... sozinho.", "1 JOGADOR · 60 MIN"),
    ("scooby", "SCOOBY-DOO", "Desmascare o monstro com a turma.", "1 A 5 JOGADORES · 30 MIN"),
    ("dracula", "DRÁCULA VS\nVAN HELSING", "Caçador contra vampiro, frente a frente.", "2 JOGADORES · 45 MIN"),
    ("tiny_zombies", "TINY EPIC\nZOMBIES", "Sobreviva a um shopping cheio de zumbis.", "1 A 5 JOGADORES · 45 MIN"),
    ("paranormal", "PARANORMAL\nDETECTIVES", "Um fantasma tenta contar como morreu.", "2 A 6 JOGADORES · 50 MIN"),
    ("dceased", "DCEASED", "Heróis contra zumbis em Gotham.", "1 A 4 JOGADORES · 60 MIN"),
]
GANCHO = 3.0
POR_JOGO = 3.6
T_COM = GANCHO + POR_JOGO * len(JOGOS)
COMENTA = 2.8
T_CTA = T_COM + COMENTA
DUR = T_CTA + 4.0


def creep(s):
    return ImageFont.truetype(CREEP, int(s))


# ---------------------------------------------------------------- cenário
@lru_cache(None)
def ceu():
    """Céu roxo em degradê, lua cheia com halo, estrelas e silhueta de lápides e árvores secas."""
    y = np.linspace(0, 1, H)[:, None]
    top, mid, bot = np.array([40, 12, 70]), np.array([22, 8, 44]), np.array([6, 3, 14])
    c = np.where(y < 0.55, top + (mid - top) * (y / 0.55), mid + (bot - mid) * ((y - 0.55) / 0.45))
    img = Image.fromarray(np.repeat(c[:, None, :], W, 1).reshape(H, W, 3).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(img)
    rnd = random.Random(3)
    for _ in range(80):
        x, yy, r = rnd.uniform(0, W), rnd.uniform(0, H * 0.5), rnd.uniform(1, 2.6)
        d.ellipse((x - r, yy - r, x + r, yy + r), fill=(255, 240, 255, rnd.randint(90, 200)))
    halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(halo).ellipse((800 - 260, 300 - 260, 800 + 260, 300 + 260), fill=(255, 220, 160, 90))
    img.alpha_composite(halo.filter(ImageFilter.GaussianBlur(90)))
    d = ImageDraw.Draw(img)
    d.ellipse((800 - 120, 300 - 120, 800 + 120, 300 + 120), fill=(255, 240, 200))
    for cx, cy, r in ((760, 270, 22), (840, 340, 16), (790, 350, 10)):  # crateras
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(240, 220, 180))
    # silhueta do cemitério
    sil = (10, 4, 18)
    d.polygon([(0, 1650), (180, 1610), (420, 1640), (700, 1600), (1080, 1630), (1080, H), (0, H)], fill=sil)
    for x, h in ((90, 120), (260, 90), (820, 110), (990, 85)):
        d.rounded_rectangle((x - 40, 1620 - h, x + 40, 1680), radius=36, fill=sil)
    for x0, s in ((40, 1.0), (1000, -1.0)):  # árvores secas nos cantos
        d.line((x0, 1650, x0 + 30 * s, 1200), fill=sil, width=26)
        for yb, comp in ((1350, 150), (1260, 110), (1420, 90)):
            d.line((x0 + 22 * s, yb, x0 + (22 + comp) * s, yb - 70), fill=sil, width=12)
    return img


@lru_cache(None)
def nevoa(k):
    rng = np.random.default_rng(k)
    a = rng.random((40, 24)).astype(np.float32)
    return np.array(Image.fromarray((a * 255).astype(np.uint8), "L").resize((W * 2, 700), Image.BICUBIC)
                    .filter(ImageFilter.GaussianBlur(55)), np.float32) / 255


def camada_nevoa(t, k, vel, y0, cor, forca):
    nv = nevoa(k)
    off = int((t * vel) % W)
    m = nv[:, off:off + W]
    m = m * np.linspace(0, 1, 700)[:, None] ** 0.8  # mais densa embaixo
    a = (m * forca * 255).clip(0, 255).astype(np.uint8)
    lay = Image.new("RGBA", (W, 700), cor + (0,))
    lay.putalpha(Image.fromarray(a))
    return lay, (0, y0)


def morcego(s, asa):
    """Morcego em silhueta; asa em [-1, 1] bate as asas."""
    im = Image.new("RGBA", (int(s * 2.2), int(s * 1.4)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = im.width / 2, im.height / 2
    ay = cy - asa * s * 0.45
    for lado in (-1, 1):
        d.polygon([(cx, cy), (cx + lado * s * 0.25, cy - s * 0.15), (cx + lado * s * 0.6, ay - s * 0.1),
                   (cx + lado * s * 1.05, ay), (cx + lado * s * 0.8, cy + s * 0.05), (cx + lado * s * 0.55, cy - s * 0.02),
                   (cx + lado * s * 0.35, cy + s * 0.12)], fill=(8, 2, 14))
    d.ellipse((cx - s * 0.16, cy - s * 0.22, cx + s * 0.16, cy + s * 0.25), fill=(8, 2, 14))
    return im


MORCEGOS = [(random.Random(i).uniform(0, 1), random.Random(i + 50).uniform(150, 1000), random.Random(i + 9).uniform(40, 90),
             random.Random(i + 3).uniform(0.06, 0.12)) for i in range(7)]


def cenario(t):
    img = ceu().copy()
    for fase, y, s, vel in MORCEGOS:
        x = ((fase + t * vel) % 1.3) * (W + 300) - 300
        cola(img, morcego(int(s), math.sin(t * 14 + fase * 9)), x, y + 30 * math.sin(t * 1.5 + fase * 6))
    for k, (vel, y0, cor, f) in enumerate(((22, 1150, (150, 110, 190), 0.55), (-35, 1300, (190, 160, 220), 0.6))):
        lay, pos = camada_nevoa(t, k + 1, vel, y0, cor, f)
        img.alpha_composite(lay, pos)
    return img


# ---------------------------------------------------------------- textos e caixas
@lru_cache(None)
def titulo(txt, size, cor=LARANJA):
    f = creep(size)
    linhas = txt.split("\n")
    lw = max(ImageDraw.Draw(Image.new("RGBA", (1, 1))).textlength(l, font=f) for l in linhas)
    lh = size * 1.0
    w, h = int(lw + 100), int(lh * len(linhas) + 100)
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for k, l in enumerate(linhas):
        d.text((w / 2, 50 + lh * k + lh / 2), l, font=f, fill=cor, anchor="mm", stroke_width=5, stroke_fill=INK)
    glow = Image.new("RGBA", (w, h), cor + (0,))
    glow.putalpha(lay.getchannel("A").filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * 0.75)))
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.alpha_composite(glow)
    out.alpha_composite(lay)
    return out


@lru_cache(None)
def frase(txt, size=44):
    return letreiro(txt, size, WHITE, INK, 8, "Poppins-Black.ttf")


@lru_cache(None)
def caixa(nome, h, brilho=True):
    im = Image.open(os.path.join(AS, nome + ".png")).convert("RGBA")
    im = im.crop(im.getbbox())
    im = im.resize((max(2, int(im.width * h / im.height)), int(h)), Image.LANCZOS)
    if not brilho:
        return sombra(im, 14, (0, 12), 0.6)
    pad = 90
    out = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    g = Image.new("RGBA", out.size, LARANJA + (0,))
    a = Image.new("L", out.size, 0)
    a.paste(im.getchannel("A"), (pad, pad))
    g.putalpha(a.filter(ImageFilter.GaussianBlur(40)).point(lambda v: int(v * 0.85)))
    out.alpha_composite(g)
    out.alpha_composite(im, (pad, pad))
    return out


def relampago(t, t0, d=0.3):
    u = t - t0
    if u < 0 or u > d:
        return 0.0
    return max(0.0, 1 - u / 0.07) * 0.7 + (0.4 if 0.12 < u < 0.17 else 0.0)


def flash_de(t):
    tempos = [0.15, 1.9] + [GANCHO + POR_JOGO * k - 0.02 for k in range(len(JOGOS))] + [T_CTA]
    return max(relampago(t, x) for x in tempos)


def cena_jogo(img, t, k):
    t0 = GANCHO + POR_JOGO * k
    u = t - t0
    nome, tit, fr, info = JOGOS[k]
    sobe = ease(seg(u, 0.0, 0.7))
    desce = ease(seg(u, POR_JOGO - 0.35, POR_JOGO))
    y = lerp(1500, 840, sobe) + 520 * desce + 10 * math.sin(u * 2.2)
    alpha = min(sobe * 1.3, 1.0) * (1 - desce)
    h = 640 if nome not in ("tiny_zombies", "paranormal") else 560
    cola(img, caixa(nome, h), 540, y, -2 + 2 * math.sin(u * 1.4), 1.0, alpha)
    cola(img, pilula(f"{k + 1}/6", 34, INK, WHITE, LARANJA), 110, 130, 0, pop(t, t0 + 0.1))
    a2 = 1 - desce
    cola(img, titulo(tit, 120 if "\n" not in tit else 104), 540, 1330 if "\n" not in tit else 1300, -2, pop(t, t0 + 0.35), a2)
    cola(img, frase(fr, 42), 540, 1470, 0, pop(t, t0 + 0.6), a2)
    cola(img, pilula(info, 36, ROXO, WHITE, WHITE), 540, 1565, 0, pop(t, t0 + 0.8), a2)


def frame(t):
    img = cenario(t)
    if t < GANCHO:
        cola(img, emoji("🎃", 190), 540, 620 + 14 * math.sin(t * 3), -6 + 4 * math.sin(t * 2), pop(t, 0.05, 0.5))
        cola(img, titulo("6 JOGOS PRA UM\nHALLOWEEN DE\nARREPIAR", 138), 540, 1040, -2, pop(t, 0.25, 0.5))
        cola(img, frase("se você tiver coragem...", 48), 540, 1420, 2, pop(t, 1.2))
    elif t < T_COM:
        cena_jogo(img, t, int((t - GANCHO) // POR_JOGO))
    elif t < T_CTA:
        u = t - T_COM
        cola(img, titulo("QUAL VOCÊ\nENCARA PRIMEIRO?", 128), 540, 780, -2, pop(t, T_COM))
        b = 1 + 0.04 * abs(math.sin(t * 6))
        cola(img, letreiro("COMENTA AQUI!", 84, WHITE, INK, 12), 500, 1110, 2, pop(t, T_COM + 0.4) * b)
        cola(img, emoji("👻", 110), 900, 1110 + 12 * math.sin(u * 7), 0, pop(t, T_COM + 0.5))
    else:
        u = t - T_CTA
        cola(img, logo_card(340), 540, 230, 0, pop(t, T_CTA))
        pos = [(160, 700, -10, 330), (330, 650, -5, 350), (540, 620, 0, 380), (750, 650, 5, 350), (920, 700, 10, 330)]
        ordem = ["paranormal", "dracula", "finalgirl", "scooby", "dceased"]
        for j, (n, (x, y, r, h)) in enumerate(zip(ordem, pos)):
            if j == 2:
                continue
            cola(img, caixa(n, h, False), x, y, r, pop(t, T_CTA + 0.15 + 0.06 * j))
        cola(img, caixa("finalgirl", 400, False), 540, 620, 0, pop(t, T_CTA + 0.3))
        itens = [(0.5, titulo("ALUGUE SEU\nTERROR!", 120), 1010),
                 (0.8, pilula("5 DIAS DE JOGO · 3 JOGOS = 7 DIAS", 38, ROXO), 1215),
                 (1.0, pilula("RESERVE ONLINE · RETIRE EM MAUÁ E ABC", 34, WHITE, INK, INK), 1320),
                 (1.15, pilula("OU RECEBA EM CASA!", 42, (22, 163, 74)), 1425),
                 (1.3, pilula("LINK NA BIO · @SUAVEZ_BG", 48, LARANJA), 1545)]
        for t0, im, y in itens:
            if u >= t0:
                cola(img, im, 540, y, 0, pop(t, T_CTA + t0))
    if t < T_CTA:
        wm = logo_card(150)
        img.alpha_composite(wm, (W - wm.width - 30, 40))
    fl = flash_de(t)
    if fl > 0:
        img = Image.blend(img.convert("RGB"), Image.new("RGB", (W, H), (225, 215, 255)), min(0.8, fl)).convert("RGBA")
    return img.convert("RGB")


def render_frame(fi):
    return frame(fi / FPS).tobytes()


def cues():
    c = [(0.0, "braam", 0.8), (0.15, "trovao", 0.7), (1.9, "trovao", 0.5), (2.5, "riser", 0.5)]
    for k in range(len(JOGOS)):
        t0 = GANCHO + POR_JOGO * k
        c += [(t0, "braam", 0.6), (t0 + 0.35, "stinger", 0.25), (t0 + POR_JOGO - 0.35, "whoosh", 0.35)]
    c += [(T_COM, "pop", 0.4), (T_COM + 0.4, "boing", 0.35), (T_CTA, "trovao", 0.6), (T_CTA + 1.3, "ding", 0.5)]
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    print(f"duração {DUR:.1f} s")
    if a.frame:
        folha([frame(x) for x in a.frame], os.path.join(OUT, "frames.jpg"))
        return
    n = int(DUR * FPS)
    for nome, musica in (("com_trilha", "terror"), ("para_musica", None)):
        wav = os.path.join(OUT, f"halloween_{nome}.wav")
        som.build(wav, DUR, cues(), musica=musica, fx_ganho=0.55 if musica else 0.45, musica_ganho=0.32)
        encode(os.path.join(OUT, f"halloween_{nome}.mp4"), render_frame, list(range(n)), wav)


if __name__ == "__main__":
    main()
