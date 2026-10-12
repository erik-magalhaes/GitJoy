#!/usr/bin/env python3
"""Reels "A CARTOMANTE DOS JOGOS — tira print e descobre sua noite" (ele escolheu a opção A, tarô, de conceitos2.py).
3 cartas de tarô (I PRA AQUECER · II O JOGÃO · III PRA FECHAR) chegam viradas, desviram e os jogos trocam rápido em cada
carta, cada uma num ritmo diferente (a combinação muda o tempo todo). Cada quadro é NÍTIDO (sem borrão): o print sai
legível. Só jogos que ainda não apareceram em post (pedido dele). Sem narração; duas versões:
_com_trilha (trilha "mística" sintetizada aqui) e _para_musica (só efeitos).

    python3 taro.py --frame 1 3 8 15 18
    python3 taro.py
"""
import argparse
import math
import os
import random
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "comum"))
from motor import W, H, FPS, WHITE, seg, ease, lerp, pop, font, emoji, logo_card, cola, sombra, letreiro, pilula, encode, folha  # noqa
import som  # noqa: E402
from som import SR, add, env, hp, lp, noise, t_  # noqa: E402

OUT = os.path.join(ROOT, "out")
AS = os.path.join(ROOT, "assets")
INK = (20, 16, 30)
OURO = (232, 190, 92)
ROXO = (110, 60, 140)
CARTAS = [("I", "PRA AQUECER", [("the_mind", "THE MIND"), ("fantasy_realms", "FANTASY REALMS"), ("taco_gato", "TACO GATO..."),
                                  ("splito", "SPLITO"), ("flash_10", "FLASH 10"), ("dobro", "DOBRO"), ("loser", "LOSER")]),
          ("II", "O JOGÃO", [("sheriff", "SHERIFF"), ("cartografos", "CARTÓGRAFOS"), ("unicorn_fever", "UNICORN FEVER"),
                             ("sea_salt", "SEA SALT & PAPER"), ("art_society", "ART SOCIETY"), ("bad_company", "BAD COMPANY"),
                             ("wandering_towers", "WANDERING TOWERS"), ("rebirth", "REBIRTH")]),
          ("III", "PRA FECHAR", [("spyfall", "SPYFALL"), ("last_message", "LAST MESSAGE"), ("happy_salmon", "HAPPY SALMON"),
                                 ("eu_sou_banana", "EU SOU UMA BANANA"), ("danca_tronos", "DANÇA DOS TRONOS"),
                                 ("perfil_express", "PERFIL EXPRESS"), ("telma", "TELMA")])]
PERIODO = [4, 3, 5]  # quadros que cada carta fica em cada jogo (ritmos diferentes; ele pediu MAIS RÁPIDO)
CW, CH = 330, 650
POS = [(188, 1000, -6), (540, 965, 0), (892, 1000, 6)]
T_CHEGA, T_VIRA, T_GIRA = 0.0, 2.2, 3.0
T_COM = 13.5
T_CTA = 16.3
DUR = 20.3


# ---------------------------------------------------------------- som
def fx_harpa():
    o = np.zeros(int(1.6 * SR))
    for k, f in enumerate((440, 523.3, 659.3, 880, 1046.5)):
        t = t_(1.2)
        add(o, (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * env(1.2, 0.5), k * 0.07, 0.35)
    return o


def fx_vira():
    d = 0.25
    return hp(noise(d), 2500) * env(d, 0.06) * 0.6


def fx_tique():
    t = t_(0.06)
    return np.sin(2 * np.pi * 2400 * t) * env(0.06, 0.02) * 0.4


def mistica(dur):
    n = int(dur * SR)
    out = np.zeros(n)
    t = t_(dur)
    pad = sum(np.sin(2 * np.pi * f * t + 0.2 * np.sin(2 * np.pi * 0.3 * t)) for f in (110, 164.8, 220, 246.9))
    out += lp(pad, 900) * 0.18 * (0.8 + 0.2 * np.sin(2 * np.pi * t / 6))
    arp = [440, 523.3, 659.3, 783.99, 659.3, 523.3]
    k, tt = 0, 0.2
    while tt < dur - 0.5:
        d = 0.9
        tp = t_(d)
        f = arp[k % len(arp)]
        add(out, (np.sin(2 * np.pi * f * tp) + 0.25 * np.sin(4 * np.pi * f * tp)) * env(d, 0.35), tt, 0.12)
        tt += 0.3
        k += 1
    m = int(1.0 * SR)
    out[-m:] *= np.linspace(1, 0, m)
    return out


som.MUSICAS["mistica"] = mistica
som.FX.update({"harpa": fx_harpa, "vira": fx_vira, "tique": fx_tique})


# ---------------------------------------------------------------- imagens
@lru_cache(None)
def fundo():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    for y in range(H):
        u = y / H
        d.line((0, y, W, y), fill=(int(52 - 34 * u), int(20 + 2 * u), int(84 - 46 * u)))
    luz = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(luz).ellipse((120, 620, 960, 1440), fill=(200, 120, 255, 80))
    img.alpha_composite(luz.filter(ImageFilter.GaussianBlur(130)))
    return img


ESTRELAS = [(random.Random(i).uniform(0, W), random.Random(i + 99).uniform(0, H), random.Random(i + 7).uniform(1, 3.2),
             random.Random(i + 3).uniform(0, 6.28)) for i in range(140)]


def ceu(t):
    img = fundo().copy()
    d = ImageDraw.Draw(img)
    for x, y, r, f in ESTRELAS:
        a = int(110 + 110 * math.sin(t * 2.2 + f))
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 232, 170, max(30, a)))
    for k in range(18):  # partículas douradas subindo
        rnd = random.Random(k)
        x = rnd.uniform(100, 980) + 20 * math.sin(t + k)
        y = (rnd.uniform(0, H) - t * rnd.uniform(40, 90)) % H
        r = rnd.uniform(2, 4)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 214, 120, 160))
    return img


@lru_cache(None)
def caixa(n, h, larg):
    im = Image.open(os.path.join(AS, n + ".png")).convert("RGBA")
    im = im.crop(im.getbbox())
    s = min(h / im.height, larg / im.width)
    return im.resize((max(2, int(im.width * s)), max(2, int(im.height * s))), Image.LANCZOS)


def moldura(dc):
    dc.rounded_rectangle((0, 0, CW - 1, CH - 1), radius=26, fill=(250, 240, 220), outline=OURO, width=11)
    dc.rounded_rectangle((20, 20, CW - 21, CH - 21), radius=17, outline=(150, 100, 40), width=3)
    for cx_ in (52, CW - 52):
        dc.polygon([(cx_, 50), (cx_ + 12, 66), (cx_, 82), (cx_ - 12, 66)], fill=OURO)


@lru_cache(None)
def frente(j, n_jogo):
    num, nome, jogos = CARTAS[j]
    c = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    dc = ImageDraw.Draw(c)
    moldura(dc)
    dc.text((CW / 2, 66), num, font=font("Bungee-Regular.ttf", 46), fill=ROXO, anchor="mm")
    dc.text((CW / 2, 118), nome, font=font("Bungee-Regular.ttf", 30), fill=ROXO, anchor="mm")
    n, rot = jogos[n_jogo]
    im = caixa(n, 370, 262)
    c.alpha_composite(sombra(im, 8, (0, 6), 0.35), (int(CW / 2 - im.width / 2 - 16), int(350 - im.height / 2 - 16)))
    f = font("Poppins-Black.ttf", 30 if len(rot) < 14 else 25)
    dc.text((CW / 2, CH - 70), rot, font=f, fill=INK, anchor="mm")
    return c


@lru_cache(None)
def verso():
    c = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    dc = ImageDraw.Draw(c)
    dc.rounded_rectangle((0, 0, CW - 1, CH - 1), radius=26, fill=(70, 30, 110), outline=OURO, width=11)
    dc.rounded_rectangle((20, 20, CW - 21, CH - 21), radius=17, outline=OURO, width=3)
    cx, cy = CW / 2, CH / 2
    dc.ellipse((cx - 80, cy - 80, cx + 80, cy + 80), fill=OURO)
    dc.ellipse((cx - 50, cy - 95, cx + 110, cy + 65), fill=(70, 30, 110))  # lua crescente
    for k in range(8):
        a = k * math.tau / 8
        x, y = cx + 125 * math.cos(a), cy + 125 * math.sin(a)
        dc.polygon([(x, y - 14), (x + 6, y), (x, y + 14), (x - 6, y)], fill=OURO)
    for y in (70, CH - 70):
        dc.polygon([(cx, y - 18), (cx + 14, y), (cx, y + 18), (cx - 14, y)], fill=OURO)
    return c


def jogo_da_vez(j, fi):
    jogos = CARTAS[j][2]
    passo = fi // PERIODO[j] + j * 3  # fase diferente em cada carta
    return passo % len(jogos)


def carta(img, j, t, fi):
    x, y, r = POS[j]
    chega = ease(seg(t, T_CHEGA + 0.15 * j, T_CHEGA + 0.15 * j + 0.7))
    yy = lerp(y + 1100, y, chega)
    rr = lerp(r - 25, r, chega)
    u = seg(t, T_VIRA + 0.12 * j, T_VIRA + 0.12 * j + 0.5)
    if u < 0.5:
        face, sx = verso(), 1 - u * 2
    else:
        k = jogo_da_vez(j, fi) if t >= T_GIRA else 0
        face, sx = frente(j, k), (u - 0.5) * 2
    if t >= T_CTA:
        face, sx = frente(j, 0), 1.0
    if sx < 0.03:
        return
    f = face.resize((max(2, int(CW * sx)), CH), Image.BICUBIC) if sx < 0.999 else face
    brilho = Image.new("RGBA", (f.width + 120, f.height + 120), (0, 0, 0, 0))
    a = Image.new("L", brilho.size, 0)
    a.paste(f.getchannel("A"), (60, 60))
    gl = Image.new("RGBA", brilho.size, (220, 160, 255, 0))
    gl.putalpha(a.filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * 0.7)))
    brilho.alpha_composite(gl)
    brilho.alpha_composite(f, (60, 60))
    cola(img, brilho, x, yy, rr)


def frame(fi):
    t = fi / FPS
    img = ceu(t)
    if t < T_CTA:
        cola(img, letreiro("A CARTOMANTE\nDOS JOGOS", 96, OURO, INK, 12, sombra_px=7, cor_sombra=INK), 540, 260, -1,
             pop(t, 0.05, 0.45))
        cola(img, emoji("🔮", 90), 110, 140, -8, pop(t, 0.4))
        if t < T_COM:
            b = 1 + (0.05 * abs(math.sin(t * 5)) if t >= T_GIRA else 0)
            cola(img, pilula("TIRA PRINT E DESCOBRE SUA NOITE!", 40, (120, 40, 170), WHITE, OURO, bw=5), 540, 470, 0,
                 pop(t, 0.6) * b)
        for j in range(3):
            carta(img, j, t, fi)
        if T_GIRA <= t < T_COM:
            cola(img, letreiro("PRINT AGORA!", 70, WHITE, INK, 10), 540, 1460, -2,
                 1 + 0.06 * math.sin(t * 9))
        if t >= T_COM:
            cola(img, letreiro("O QUE SAIU\nPRA VOCÊ?", 92, OURO, INK, 12), 540, 1450, -2, pop(t, T_COM))
            cola(img, pilula("COMENTA AQUI!", 46, (230, 40, 90)), 540, 1620, 2, pop(t, T_COM + 0.35))
        wm = logo_card(140)
        img.alpha_composite(wm, (W - wm.width - 30, 40)) if t > 0.6 else None
    else:
        u = t - T_CTA
        cola(img, logo_card(380), 540, 240, 0, pop(t, T_CTA))
        cola(img, letreiro("ALUGA OS SEUS 3\nE GANHA 7 DIAS!", 84, OURO, INK, 12, sombra_px=6, cor_sombra=INK), 540, 520,
             -2, pop(t, T_CTA + 0.25))
        for j, (n, x, r) in enumerate([("the_mind", 250, -8), ("sheriff", 540, 0), ("spyfall", 830, 8)]):
            cola(img, sombra(caixa(n, 330, 300), 14, (0, 12), 0.5), x, 860, r, pop(t, T_CTA + 0.4 + 0.08 * j))
        itens = [(0.8, pilula("5 DIAS DE JOGO · 3 JOGOS = 7 DIAS", 38, (120, 40, 170), WHITE, OURO), 1150),
                 (1.0, pilula("RESERVE ONLINE · RETIRE EM MAUÁ E ABC", 34, WHITE, INK, INK), 1255),
                 (1.15, pilula("OU RECEBA EM CASA!", 42, (22, 163, 74)), 1360),
                 (1.3, pilula("LINK NA BIO · @SUAVEZ_BG", 48, (249, 115, 22)), 1480)]
        for t0, im, y in itens:
            if u >= t0:
                cola(img, im, 540, y, 0, pop(t, T_CTA + t0))
    return img.convert("RGB")


def render_frame(fi):
    return frame(fi).tobytes()


def cues():
    c = [(0.0, "harpa", 0.6)] + [(0.15 * j + 0.1, "whoosh", 0.35) for j in range(3)]
    c += [(T_VIRA + 0.12 * j + 0.25, "vira", 0.6) for j in range(3)] + [(T_GIRA, "harpa", 0.5)]
    t = T_GIRA
    while t < T_COM:  # tiquetaque baixinho enquanto as cartas trocam
        c.append((t, "tique", 0.18))
        t += 0.12
    c += [(T_COM, "ding", 0.5), (T_COM + 0.35, "pop", 0.4), (T_CTA, "harpa", 0.6), (T_CTA + 1.3, "ding", 0.5)]
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.frame:
        folha([frame(int(round(x * FPS))) for x in a.frame], os.path.join(OUT, "frames.jpg"))
        return
    n = int(DUR * FPS)
    for nome, musica in (("com_trilha", "mistica"), ("para_musica", None)):
        wav = os.path.join(OUT, f"taro_{nome}.wav")
        som.build(wav, DUR, cues(), musica=musica, fx_ganho=0.5, musica_ganho=0.3)
        encode(os.path.join(OUT, f"taro_{nome}.mp4"), render_frame, list(range(n)), wav)


if __name__ == "__main__":
    main()
