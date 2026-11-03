#!/usr/bin/env python3
"""Reels 1 do Becas: PARA DE ROLAR (3/nov/2026). O vídeo começa fingindo ser o próprio feed (posts cinza passando com
o dedo), a tela TRINCA e ESTOURA em cacos, e por baixo aparecem as cenas REAIS de jogo na mesa deles, em cortes na
batida (118 bpm), cada uma com o nome do jogo batendo na tela. Fecha com os guarda-chuvinhas do Becas e o convite.
Pedido dele: priorizar os JOGOS (cenas de jogo na mesa), sons diferentes dos vídeos anteriores.

    /usr/bin/python3 para_de_rolar.py --frame 1 2.8 3.2 4.5 9 15 20   # out/frames_rolar.jpg
    /usr/bin/python3 para_de_rolar.py                                  # out/rolar_{com_som,para_musica}_final.mp4
"""
import math
import os
import random
import sys
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter

import kit as K
import sons as S
from kit import W, H, FPS, E, TB, MAR, PET, LAR, AMA, BR, ease

sys.path.insert(0, K.ROOT)
import tarde  # noqa: E402  (guarda-chuvinhas balançando)

FEED_FIM = 3.0          # a tela trinca de 2,55 a 3,0 e estoura em 3,0
REVELA = 3.0
BPM = 118
B = 60 / BPM
# montagem: (clipe, t0 no bruto, batidas, velocidade)
MONT = [("critter", 0.3, 4, 1.0), ("sushi", 0.6, 2, 1.0), ("canvas", 1.4, 2, 1.0), ("art", 0.6, 2, 1.0),
        ("passaporte", 1.0, 2, 1.0), ("unlock", 0.8, 2, 1.0), ("sky_dados", 3.5, 2, 1.0), ("taketime", 18.0, 2, 1.2),
        ("sky_painel", 2.5, 2, 1.0), ("canvas", 4.0, 1, 1.0), ("critter", 3.6, 1, 1.0), ("sushi", 3.2, 1, 1.0),
        ("unlock", 3.4, 1, 1.0)]
INI = [REVELA]
for _, _, nb, _ in MONT:
    INI.append(INI[-1] + nb * B)
CTA = INI[-1]
DUR = CTA + 6.6


def trechos():
    out = [(c, t0, nb * B + 0.05, v) for c, t0, nb, v in MONT]
    out.append(("sky_caixa", 4.0, DUR - CTA + 0.1, 0.5))
    return out


# ---------------------------------------------------------------- o feed falso
@lru_cache(None)
def feed_longo():
    alto = 6200
    img = Image.new("RGBA", (W, alto), (238, 238, 238, 255))
    d = ImageDraw.Draw(img)
    rnd = random.Random(2)
    y = 40
    while y < alto:
        d.ellipse((40, y + 20, 112, y + 92), fill=(200, 200, 200))
        d.rounded_rectangle((134, y + 36, 134 + rnd.randint(180, 320), y + 62), 12, fill=(206, 206, 206))
        d.rounded_rectangle((134, y + 72, 134 + rnd.randint(100, 180), y + 88), 8, fill=(220, 220, 220))
        c = rnd.randint(180, 212)
        d.rectangle((0, y + 115, W, y + 115 + 820), fill=(c, c, c))
        for j in range(rnd.randint(2, 4)):  # "foto" genérica: manchas cinza
            cx, cy, r = rnd.uniform(100, 980), y + 115 + rnd.uniform(100, 720), rnd.uniform(80, 240)
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(c - 14, c - 14, c - 14))
        for k in range(3):
            d.ellipse((40 + k * 84, y + 960, 92 + k * 84, y + 1012), outline=(165, 165, 165), width=6)
        y += 1060
    return img.filter(ImageFilter.GaussianBlur(1.0))


# rolagens: (início, duração, deslocamento)
FLICKS = [(0.15, 0.55, 760), (0.85, 0.5, 920), (1.45, 0.42, 1080), (1.95, 0.4, 1280)]


def rolagem(t):
    y = 0.0
    for t0, d, dy in FLICKS:
        if t >= t0:
            u = min(1.0, (t - t0) / d)
            y += dy * (1 - (1 - u) ** 3)
    return y


@lru_cache(None)
def titulo_feed():
    return E.titulo("SÁBADO ROLANDO\nO FEED DE NOVO?", 122, BR, larg_max=980)


CENTRO = (560, 1330)


def rachaduras(q, seed=4):
    """Linhas da trinca até a fração q (0–1)."""
    rnd = random.Random(seed)
    linhas = []
    for k in range(16):
        a = k * 2 * math.pi / 16 + rnd.uniform(-0.2, 0.2)
        x, y = CENTRO
        for j in range(7):
            r = rnd.uniform(60, 170)
            a += rnd.uniform(-0.35, 0.35)
            x2, y2 = x + r * math.cos(a), y + r * math.sin(a)
            if j / 7 < q:
                linhas.append((x, y, x2, y2))
            x, y = x2, y2
    return linhas


def tela_feed(t):
    img = feed_longo().crop((0, int(rolagem(t)), W, int(rolagem(t)) + H)).copy()
    K.poe(img, titulo_feed(), W / 2, 760, t, 0.05, -2)
    if t >= 2.55:
        q = min(1.0, (t - 2.55) / 0.4)
        d = ImageDraw.Draw(img)
        for x, y, x2, y2 in rachaduras(q):
            d.line((x + 3, y + 3, x2 + 3, y2 + 3), fill=(60, 60, 60, 160), width=3)
            d.line((x, y, x2, y2), fill=(255, 255, 255, 255), width=5)
        r = 26 * q
        d.ellipse((CENTRO[0] - r, CENTRO[1] - r, CENTRO[0] + r, CENTRO[1] + r), fill=(255, 255, 255, 200))
    return img


@lru_cache(None)
def cacos():
    """Corta o feed trincado em cacos (fatias radiais × anéis). Cada caco: (imagem, centro, direção)."""
    base = tela_feed(FEED_FIM - 1e-3)
    rnd = random.Random(9)
    n, aneis = 14, [0, 260, 620, 2400]
    out = []
    for k in range(n):
        a0 = k * 2 * math.pi / n + rnd.uniform(-0.08, 0.08)
        a1 = (k + 1) * 2 * math.pi / n + rnd.uniform(-0.08, 0.08)
        for j in range(len(aneis) - 1):
            r0, r1 = aneis[j], aneis[j + 1]
            pts = [(CENTRO[0] + r0 * math.cos(a0), CENTRO[1] + r0 * math.sin(a0)),
                   (CENTRO[0] + r1 * math.cos(a0), CENTRO[1] + r1 * math.sin(a0)),
                   (CENTRO[0] + r1 * math.cos(a1), CENTRO[1] + r1 * math.sin(a1)),
                   (CENTRO[0] + r0 * math.cos(a1), CENTRO[1] + r0 * math.sin(a1))]
            m = Image.new("L", (W, H), 0)
            ImageDraw.Draw(m).polygon(pts, fill=255)
            bb = m.getbbox()
            if not bb:
                continue
            pe = base.crop(bb)
            pe.putalpha(m.crop(bb))
            ImageDraw.Draw(pe).polygon([(x - bb[0], y - bb[1]) for x, y in pts], outline=(255, 255, 255, 255),
                                       width=4)
            cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
            am = (a0 + a1) / 2
            out.append((pe, (cx, cy), (math.cos(am), math.sin(am)), rnd.uniform(-1, 1), j))
    return out


def estilhaca(img, u):
    """u = segundos desde o estouro."""
    for pe, (cx, cy), (dx, dy), giro, anel in cacos():
        v = 900 + 500 * (2 - anel)
        x = cx + dx * v * u
        y = cy + dy * v * u + 2600 * u * u
        rot = giro * 260 * u
        a = max(0.0, 1 - u / 0.75)
        if a > 0:
            E.cola(img, pe, x, y, rot, 1 + 0.25 * u, a)


# ---------------------------------------------------------------- montagem
def montagem(t):
    k = max(i for i in range(len(MONT)) if INI[i] <= t)
    c, t0, nb, v = MONT[k]
    u = t - INI[k]
    img = K.quadro_clip(c, t0, nb * B + 0.05, v, u)
    # pulso na batida: zoom de 4% que volta
    fb = ((t - REVELA) % B) / B
    z = 1 + 0.04 * math.exp(-fb * 6)
    if z > 1.001:
        w2, h2 = int(W * z), int(H * z)
        img = img.resize((w2, h2), Image.BILINEAR).crop(((w2 - W) // 2, (h2 - H) // 2, (w2 - W) // 2 + W,
                                                         (h2 - H) // 2 + H))
    K.escurece(img, 1240, 1640, 120)
    nome = K.CLIPES[c][1]
    K.poe(img, K.etiqueta(nome, 54, (AMA, BR, LAR)[k % 3], MAR if k % 3 < 2 else BR), 330, 1470, u, 0.0,
          (-4, 3, -2)[k % 3], d=0.18)
    if k == 0:  # a virada: "OU JOGANDO NO BECAS?"
        K.poe(img, K.titulo("OU JOGANDO\nNO BECAS?", 140, AMA), W / 2, 760, t - REVELA, 0.15, -3, d=0.3)
    if 0 < k < len(MONT) and u < 2 / FPS:  # flash branco de 2 quadros no corte
        fl = Image.new("RGBA", (W, H), (255, 255, 255, int(150 * (1 - u * FPS / 2))))
        img.alpha_composite(fl)
    if t - REVELA < 0.25:  # entrada do estouro: flash
        fl = Image.new("RGBA", (W, H), (255, 255, 255, int(220 * (1 - (t - REVELA) / 0.25))))
        img.alpha_composite(fl)
    K.marca(img)
    return img


def final(t):
    u = t - CTA
    img = K.quadro_clip("sky_caixa", 4.0, DUR - CTA + 0.1, 0.5, u)
    img = K.desfoca(img, 14)
    img.alpha_composite(Image.new("RGBA", (W, H), (40, 24, 12, 120)))
    tarde.guarda_chuvas(img, u)
    K.poe(img, K.logo(230), W / 2, 520, u, 0.3)
    K.poe(img, K.card_cta(), W / 2, 960, u, 0.55, -1.5, d=0.35)
    K.poe(img, E.texto("Comenta: qual desses você\njogaria primeiro?", 46, BR, 800), W / 2, 1400, u, 1.4)
    return img


def quadro(t):
    if t < REVELA:
        return tela_feed(t).convert("RGB")
    if t < CTA:
        img = montagem(t)
        u = t - REVELA
        if u < 0.8:
            estilhaca(img, u)
        return img.convert("RGB")
    img = final(t)
    if t - CTA < 0.25:
        img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(200 * (1 - (t - CTA) / 0.25)))))
    return img.convert("RGB")


def render(fi):
    return quadro(fi / FPS).tobytes()


def audio(path_com, path_sem):
    ev = [(t0 - 0.02, S.rolagem(), 0.9) for t0, _, _ in FLICKS]
    ev += [(2.55, S.trinca(), 0.9), (REVELA, S.estilhaco(), 0.9), (REVELA, S.estouro(), 1.0)]
    ev += [(INI[k], S.cartao(), 0.55) for k in range(1, len(MONT))]
    ev += [(CTA, S.estouro(), 0.6), (CTA + 0.55, S.cartao(), 0.6)]
    ev += [(CTA + 0.08 * k + 0.4, S.louca(1800 + 120 * k), 0.25) for k in range(6)]  # guarda-chuvas tilintando
    mus = S.musica_pop(DUR, REVELA, BPM)
    S.grava(path_com, DUR, ev, mus, musica_ganho=0.55, fx_ganho=0.75)
    S.grava(path_sem, DUR, ev, None, fx_ganho=0.8)


def main():
    os.makedirs(K.OUT, exist_ok=True)
    K.prepara(trechos())
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:]]
        K.folha([quadro(x) for x in ts], os.path.join(K.OUT, "frames_rolar.jpg"))
        print("ok", round(DUR, 2))
        return
    com, sem = os.path.join(K.OUT, "rolar_com.wav"), os.path.join(K.OUT, "rolar_sem.wav")
    audio(com, sem)
    K.entrega("rolar", DUR, render, com, sem)


if __name__ == "__main__":
    main()
