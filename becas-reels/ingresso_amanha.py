#!/usr/bin/env python3
"""INGRESSO da Tarde de Jogos no Beca’s para o WhatsApp de quem JÁ reservou (19/nov/2026, véspera).
O "SUA MESA JÁ TÁ GUARDADA" do `amanha_becas.py --confirmados` ele não gostou ("faz outro") → conceito novo:
um INGRESSO de verdade (canhoto picotado, código de barras) que sobe no fundo petróleo e leva o carimbo vermelho
"CONFIRMADO!" com uma pancada; confete; "TE ESPERAMOS AMANHÃ!".

    /usr/bin/python3 ingresso_amanha.py --frame 0.8 1.6 2.6 4 7.5
    /usr/bin/python3 ingresso_amanha.py      # PNG + vídeo (com som / para música)
"""
import math
import os
import random
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

import kit as K
import sons as S
import tarde as T
from tarde import E, TB, W, H, MAR, PET, LAR, AMA, BR, ROSA

from motor import FPS, out_back  # noqa: E402

OUT = T.OUT
DUR = 8.0
T_TIC = 0.45           # ingresso sobe
T_LIN = 1.15           # linhas aparecem
T_CAR = 2.35           # carimbo bate
T_FIM = 3.0            # "TE ESPERAMOS AMANHÃ!"
VERM = (206, 38, 44)
VERDE = (64, 168, 82)
CREME = (255, 249, 236)
TW, TH = 800, 1190     # ingresso
PERF = 960             # linha do picote
ROT = -3.0
CX, CY = W / 2, 1000


# ---------------------------------------------------------------- fundo
@lru_cache(None)
def fundo():
    img = Image.new("RGBA", (W, H), (22, 96, 118, 255))
    d = ImageDraw.Draw(img)
    for k in range(-H, W + H, 90):  # listras diagonais suaves
        d.polygon([(k, 0), (k + 45, 0), (k + 45 - H * 0.6, H), (k - H * 0.6, H)], fill=(26, 108, 132, 255))
    rnd = random.Random(11)
    for _ in range(70):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        if 120 < x < W - 120 and 380 < y < 1640:  # nada atrás do ingresso
            continue
        c = rnd.choice([LAR, AMA, ROSA, BR, VERDE])
        s = rnd.randint(8, 16)
        if rnd.random() < 0.5:
            d.ellipse((x - s, y - s, x + s, y + s), fill=c + (255,))
        else:
            a = rnd.uniform(0, math.pi)
            dx, dy = math.cos(a) * s * 1.3, math.sin(a) * s * 1.3
            d.line((x - dx, y - dy, x + dx, y + dy), fill=c + (255,), width=7)
    vin = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vin).ellipse((-300, -200, W + 300, H + 200), fill=255)
    vin = vin.filter(ImageFilter.GaussianBlur(160))
    esc = Image.new("RGBA", (W, H), (8, 40, 52, 255))
    return Image.composite(img, esc, vin)


def cabe(txt, larg, s, fonte=E.lilita):
    while s > 18 and ImageDraw.Draw(Image.new("L", (1, 1))).textlength(txt, font=fonte(s)) > larg:
        s -= 2
    return fonte(s)


# ---------------------------------------------------------------- ingresso
LINHAS = [("QUANDO", "AMANHÃ! SEXTA, 20/11"), ("HORÁRIO", "DAS 13H ÀS 19H"),
          ("ONDE", "BECA’S CAFÉ · RUA SOROCABA, 35 · MAUÁ"), ("INCLUI", "R$ 15 DE CONSUMAÇÃO NO CAFÉ\n+ JOGOS E MONITORIA")]
Y_LIN = [430, 560, 690, 820]


def forma():
    """Máscara do ingresso: cantos redondos + meia-lua dos dois lados no picote."""
    m = Image.new("L", (TW, TH), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle((0, 0, TW - 1, TH - 1), 40, fill=255)
    r = 38
    d.ellipse((-r, PERF - r, r, PERF + r), fill=0)
    d.ellipse((TW - r, PERF - r, TW + r, PERF + r), fill=0)
    return m


@lru_cache(None)
def ingresso(n_lin=4):
    """Ingresso com as `n_lin` primeiras linhas (sem sombra, sem carimbo)."""
    m = forma()
    im = Image.new("RGBA", (TW, TH), CREME + (255,))
    d = ImageDraw.Draw(im)
    # faixa do cabeçalho
    d.rectangle((0, 0, TW, 215), fill=LAR)
    for x in range(-200, TW, 46):
        d.polygon([(x, 0), (x + 20, 0), (x + 20 + 215 * 0.5, 215), (x + 215 * 0.5, 215)], fill=(248, 150, 56))
    d.line((0, 215, TW, 215), fill=MAR, width=7)
    d.text((TW / 2, 52), "—  I N G R E S S O  —", font=E.fig(30, 900), fill=BR, anchor="mm")
    t = E.titulo("TARDE DE JOGOS", 84, BR, larg_max=TW - 80)
    im.alpha_composite(t, (int(TW / 2 - t.width / 2), 138 - t.height // 2))
    p = TB.parceria(100)
    im.alpha_composite(p, (int(TW / 2 - p.width / 2), 312 - p.height // 2))
    # linhas
    for k, (rot, val) in enumerate(LINHAS[:n_lin]):
        y = Y_LIN[k]
        d.line((60, y - 22, TW - 60, y - 22), fill=(226, 212, 190), width=3)
        d.text((60, y), rot, font=E.fig(28, 900), fill=PET, anchor="lm")
        vs = val.split("\n")
        for j, v in enumerate(vs):
            f = cabe(v, TW - 240, 50 if j == 0 else 40)
            d.text((195, y + j * 54), v, font=f, fill=MAR if j == 0 else (120, 82, 50), anchor="lm")
    # picote
    for x in range(52, TW - 50, 26):
        d.line((x, PERF, x + 13, PERF), fill=(170, 150, 125), width=4)
    # canhoto
    d.text((60, PERF + 72), "ADMITE:", font=E.fig(26, 900), fill=PET, anchor="lm")
    d.text((60, PERF + 128), "VOCÊ!", font=E.lilita(64), fill=MAR, anchor="lm")
    rnd = random.Random(4)
    x = 330
    while x < TW - 60:
        w = rnd.choice([3, 3, 5, 7, 9])
        d.rectangle((x, PERF + 50, x + w, PERF + 160), fill=MAR)
        x += w + rnd.choice([4, 5, 7, 9])
    d.text(((330 + TW - 60) / 2, PERF + 186), "SUA VEZ × BECA’S · 20.11.2026", font=E.fig(20, 800), fill=(120, 82, 50),
           anchor="mm")
    # contorno
    out = Image.new("RGBA", (TW, TH), (0, 0, 0, 0))
    out.paste(im, (0, 0), m)
    contorno = ImageChops.subtract(m, m.filter(ImageFilter.MinFilter(13)))
    out.paste(Image.new("RGBA", (TW, TH), MAR + (255,)), (0, 0), contorno)
    return out


@lru_cache(None)
def carimbo():
    s = 390
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((6, 6, s - 6, s - 6), outline=VERM, width=14)
    d.ellipse((34, 34, s - 34, s - 34), outline=VERM, width=5)
    d.rectangle((0, s / 2 - 52, s, s / 2 + 52), fill=VERM)
    d.text((s / 2, s / 2 + 2), "CONFIRMADO!", font=cabe("CONFIRMADO!", s - 30, 60), fill=CREME, anchor="mm")
    d.text((s / 2, 102), "MESA GUARDADA", font=E.fig(28, 900), fill=VERM, anchor="mm")
    d.text((s / 2, s - 100), "• 20/11 •", font=E.fig(30, 900), fill=VERM, anchor="mm")
    # tinta falhada
    a = np.array(im.getchannel("A")).astype(float)
    rnd = np.random.default_rng(3)
    ruido = Image.fromarray((rnd.random((s // 6, s // 6)) * 255).astype(np.uint8)).resize((s, s), Image.BICUBIC)
    r = np.array(ruido) / 255.0
    a *= np.clip((r - 0.05) * 2.6, 0.6, 1.0) * 0.95
    im.putalpha(Image.fromarray(a.astype(np.uint8)))
    return im.rotate(16, expand=True, resample=Image.BICUBIC)


def brilho(im, u):
    """Faixa de brilho atravessando o ingresso (u de 0 a 1)."""
    if u <= 0 or u >= 1:
        return im
    faixa = Image.new("L", im.size, 0)
    x = -300 + (im.width + 600) * u
    ImageDraw.Draw(faixa).polygon([(x, 0), (x + 90, 0), (x + 90 - 400, im.height), (x - 400, im.height)], fill=90)
    faixa = faixa.filter(ImageFilter.GaussianBlur(25))
    a = Image.fromarray((np.array(faixa).astype(float) * np.array(im.getchannel("A")) / 255).astype(np.uint8))
    out = im.copy()
    out.paste(Image.new("RGBA", im.size, (255, 255, 255, 255)), (0, 0), a)
    out.putalpha(im.getchannel("A"))
    return out


random.seed(5)
CONF = [(random.uniform(0, 2 * math.pi), random.uniform(500, 1400), random.choice([LAR, AMA, ROSA, VERDE, BR]),
         random.uniform(-400, 400), random.randint(12, 22)) for _ in range(110)]


def confete(img, t, cx, cy):
    u = t - T_CAR
    if u < 0 or u > 2.4:
        return
    d = ImageDraw.Draw(img)
    for a, v, cor, giro, s in CONF:
        x = cx + math.cos(a) * v * u * 0.9
        y = cy + math.sin(a) * v * u * 0.8 - 300 * u + 1000 * u * u
        if y > H + 40:
            continue
        al = int(255 * min(1, (2.4 - u) / 0.6))
        w = s * abs(math.cos(math.radians(giro * u)))
        d.rectangle((x - w / 2, y - s / 2, x + w / 2 + 1, y + s / 2), fill=cor + (al,))


def quadro(t):
    img = fundo().copy()
    # título
    T.poe(img, E.titulo("SEU LUGAR TÁ", 86, BR), W / 2, 205, t, 0.05, -2)
    T.poe(img, E.titulo("GARANTIDO!", 128, AMA), W / 2, 320, t, 0.25, 2)
    # ingresso
    n = 0 if t < T_LIN else min(4, 1 + int((t - T_LIN) / 0.22))
    tk = ingresso(n).copy()
    if t >= T_CAR:  # carimbo
        u = min(1.0, (t - T_CAR) / 0.13)
        c = carimbo()
        esc = 1.9 - 0.9 * u
        cs = c.resize((int(c.width * esc), int(c.height * esc)), Image.LANCZOS)
        if u < 1:
            cs.putalpha(cs.getchannel("A").point(lambda v: int(v * (0.3 + 0.7 * u))))
        cx, cy = 585, PERF + 72
        lay = Image.new("RGBA", tk.size, (0, 0, 0, 0))
        lay.alpha_composite(cs, (int(cx - cs.width / 2), int(cy - cs.height / 2)))
        lay.putalpha(Image.fromarray(np.minimum(np.array(lay.getchannel("A")), np.array(tk.getchannel("A")))))
        tk.alpha_composite(lay)
    ciclo = (t - 3.6) % 2.6 / 0.9 if t > 3.6 else -1
    tk = brilho(tk, ciclo)
    # sombra sólida
    sh = Image.new("RGBA", (TW + 18, TH + 18), (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", (TW, TH), MAR + (255,)), (18, 18), tk.getchannel("A"))
    sh.alpha_composite(tk, (0, 0))
    # entrada + pancada do carimbo + flutuar
    e = min(1.0, max(0.0, (t - T_TIC) / 0.6))
    dy = (1 - out_back(e, 1.1)) * 1400 if t >= T_TIC else 2000
    dt = t - T_CAR
    tranco = 14 * math.exp(-dt * 14) * math.cos(dt * 60) if dt >= 0 else 0
    bob = 8 * math.sin(2 * math.pi * (t - T_FIM) / 2.4) if t > T_FIM else 0
    rot = ROT + (6 * (1 - e) if e < 1 else 0) + tranco * 0.08
    r = sh.rotate(rot, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(r, (int(CX - r.width / 2), int(CY + dy + tranco + bob - r.height / 2)))
    confete(img, t, CX + 30, 1300)
    T.poe(img, E.titulo("TE ESPERAMOS AMANHÃ!", 78, BR), W / 2, 1655, t, T_FIM, -1)
    T.poe(img, E.pilula("Dúvidas? WhatsApp " + TB.WHATS, 34, AMA, MAR), W / 2, 1770, t, T_FIM + 0.3, 1)
    return img.convert("RGB")


def render(fi):
    return quadro(fi / FPS).tobytes()


def pancada():
    n = int(0.35 * S.SR)
    tt = np.arange(n) / S.SR
    grave = np.sin(2 * np.pi * (95 - 40 * tt) * tt) * np.exp(-tt * 18)
    estalo = np.random.default_rng(1).normal(0, 1, n) * np.exp(-tt * 70)
    return grave * 1.0 + S.lp(estalo, 2500) * 0.6


def audio():
    ev = [(0.05, S.cartao(), 0.4), (0.25, S.cartao(), 0.4), (T_TIC, S.sopro(0.5, True), 0.45)]
    ev += [(T_LIN + 0.22 * k, S.cartao(), 0.35) for k in range(4)]
    ev += [(T_CAR - 0.05, S.sopro(0.15, False), 0.3), (T_CAR + 0.1, pancada(), 1.0), (T_CAR + 0.12, S.estouro(), 0.55),
           (T_CAR + 0.15, S.plim(), 0.5), (T_FIM, S.sino(), 0.4), (T_FIM + 0.3, S.cartao(), 0.35)]
    mus = S.musica_pop(DUR + 0.5, 0.0)
    com = os.path.join(OUT, "ingresso_com.wav")
    sem = os.path.join(OUT, "ingresso_sem.wav")
    S.grava(com, DUR, ev, mus, musica_ganho=0.4, fx_ganho=0.85)
    S.grava(sem, DUR, ev, None, fx_ganho=0.85)
    return com, sem


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:]]
        K.folha([quadro(x) for x in ts], os.path.join(OUT, "frames_ingresso.jpg"))
        print("ok")
        return
    d = os.path.join(OUT, "amanha")
    os.makedirs(d, exist_ok=True)
    quadro(DUR - 0.6).save(os.path.join(d, "whats_ingresso.png"))
    com, sem = audio()
    K.entrega("ingresso_amanha", DUR, render, com, sem)
    print("ok")


if __name__ == "__main__":
    main()
