#!/usr/bin/env python3
"""Reels 2 do Becas: JOGO DAS XÍCARAS (3/nov/2026). O vídeo é um jogo: na mesa do café (toalha xadrez, guarda-chuvinhas
do Becas no alto), uma xícara cobre o dado e as 3 embaralham cada vez mais rápido. "COMENTA 1, 2 OU 3!", contagem, a
xícara certa sobe e o dado rola direto para as cenas REAIS de jogo na mesa deles ("NO BECAS, O JOGO É DE VERDADE"),
e fecha no convite. Som de louça, mesa e um lounge de piano elétrico (nada das trilhas de antes).

    /usr/bin/python3 xicaras.py --frame 0.5 1.3 4 8.6 10.8 12.6 15 19   # out/frames_xicaras.jpg
    /usr/bin/python3 xicaras.py                                          # out/xicaras_{com_som,para_musica}_final.mp4
"""
import math
import os
import random
import sys
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter

import kit as K
import sons as S
from kit import W, H, FPS, E, TB, MAR, PET, LAR, AMA, BR, ROSA, ease

sys.path.insert(0, K.ROOT)
import tarde  # noqa: E402

SLOT_X = [170, 500, 830]
ESC = 1.25                        # xícaras maiores
MESA_Y = 1300                     # base das xícaras
CORES = [PET, AMA, ROSA]
BAIXA = (0.9, 1.35)               # a xícara do meio desce sobre o dado
EMB0 = 1.6
TROCAS = [(0, 1, .62), (1, 2, .58), (0, 2, .54), (0, 1, .48), (1, 2, .44), (0, 2, .40), (0, 1, .36), (1, 2, .33),
          (0, 1, .30), (0, 2, .30), (1, 2, .28)]
INI_T = [EMB0]
for _, _, d in TROCAS:
    INI_T.append(INI_T[-1] + d + 0.04)
EMB1 = INI_T[-1]
CONTA = EMB1 + 0.25               # "COMENTA 1, 2 OU 3!" + 3, 2, 1
REVELA = CONTA + 2.6
MERGULHO = REVELA + 1.5           # o dado vem para a tela e vira montagem
MONT = [("critter", 0.3, 1.4), ("passaporte", 1.0, 1.3), ("canvas", 1.4, 1.3), ("sky_dados", 3.5, 1.3),
        ("art", 0.6, 1.3)]
INI_M = [MERGULHO + 0.35]
for _, _, d in MONT:
    INI_M.append(INI_M[-1] + d)
CTA = INI_M[-1]
DUR = CTA + 6.6


def posicoes(t):
    """slot (posição contínua) e profundidade de cada xícara no tempo t. Xícara 1 cobre o dado."""
    slot = [0, 1, 2]
    for k, (a, b, d) in enumerate(TROCAS):
        t0 = INI_T[k]
        if t < t0:
            break
        ia, ib = slot.index(a), slot.index(b)
        if t < t0 + d:
            u = ease((t - t0) / d)
            pos = [float(s) for s in slot]
            prof = [0.0, 0.0, 0.0]
            pos[ia] = a + (b - a) * u
            pos[ib] = b + (a - b) * u
            prof[ia] = math.sin(math.pi * u)      # passa na frente
            prof[ib] = -math.sin(math.pi * u)     # passa por trás
            return pos, prof
        slot[ia], slot[ib] = b, a
    return [float(s) for s in slot], [0.0, 0.0, 0.0]


def slot_final():
    pos, _ = posicoes(EMB1 + 0.01)
    return int(round(pos[1]))


RESPOSTA = slot_final() + 1


# ---------------------------------------------------------------- desenho
@lru_cache(None)
def xicara(cor):
    """Xícara virada de boca para baixo (como no jogo dos copinhos), no traço da loja."""
    w, h = 250, 230
    im = Image.new("RGBA", (w + 110, h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x0 = 20
    corpo = [(x0 + 48, 12), (x0 + w - 48, 12), (x0 + w - 6, h - 18), (x0 + 6, h - 18)]
    d.polygon([(x + 9, y + 10) for x, y in corpo], fill=MAR)  # sombra sólida
    # asa
    d.arc((x0 + w - 60, 50, x0 + w + 70, 175), -80, 80, fill=MAR, width=26)
    d.arc((x0 + w - 60, 50, x0 + w + 70, 175), -80, 80, fill=cor, width=12)
    d.polygon(corpo, fill=cor)
    clara = tuple(min(255, int(c + (255 - c) * 0.4)) for c in cor)
    d.polygon([(x0 + 70, 26), (x0 + 96, 26), (x0 + 52, h - 34), (x0 + 30, h - 34)], fill=clara)  # brilho
    d.rectangle((x0 + 18, h - 74, x0 + w - 18, h - 52), fill=BR)  # faixa branca
    for k in range(5):
        d.ellipse((x0 + 44 + k * 38, h - 70, x0 + 58 + k * 38, h - 56), fill=cor)
    d.line(corpo + [corpo[0]], fill=MAR, width=7)
    d.rounded_rectangle((x0 - 4, h - 26, x0 + w + 4, h - 6), 10, fill=BR, outline=MAR, width=6)  # boca (borda)
    return im


@lru_cache(None)
def dado(s=185):
    im = Image.new("RGBA", (s + 30, s + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 12, s + 10, s + 12), 28, fill=MAR)
    d.rounded_rectangle((0, 0, s, s), 28, fill=BR, outline=MAR, width=7)
    r = s * 0.085
    for px, py in ((.25, .25), (.75, .25), (.5, .5), (.25, .75), (.75, .75)):
        d.ellipse((px * s - r, py * s - r, px * s + r, py * s + r), fill=LAR)
    return im


@lru_cache(None)
def cenario():
    img = Image.new("RGBA", (W, H), (250, 238, 220, 255))
    d = ImageDraw.Draw(img)
    rnd = random.Random(3)
    for _ in range(160):  # parede com confete claro
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, 1120), rnd.uniform(3, 6)
        c = tuple(int(v + (255 - v) * 0.7) for v in (LAR, PET, AMA, ROSA)[rnd.randrange(4)])
        d.ellipse((x - r, y - r, x + r, y + r), fill=c)
    # mesa com toalha xadrez em perspectiva leve
    topo = 1120
    d.rectangle((0, topo - 14, W, topo), fill=MAR)
    for i in range(16):
        y0 = topo + (i ** 1.35) * 22
        y1 = topo + ((i + 1) ** 1.35) * 22
        for j in range(-4, 20):
            xa = W / 2 + (j - 8) * 80 * (1 + (y0 - topo) / 700)
            xb = W / 2 + (j - 7) * 80 * (1 + (y0 - topo) / 700)
            xc = W / 2 + (j - 7) * 80 * (1 + (y1 - topo) / 700)
            xd = W / 2 + (j - 8) * 80 * (1 + (y1 - topo) / 700)
            cor = (236, 128, 56) if (i + j) % 2 else (252, 244, 232)
            d.polygon([(xa, y0), (xb, y0), (xc, y1), (xd, y1)], fill=cor)
    return img


def sombra_chao(img, x, y, w, a=90):
    sh = Image.new("RGBA", (int(w) + 40, 70), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((20, 10, int(w) + 20, 60), fill=(60, 30, 10, a))
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    img.alpha_composite(sh, (int(x - sh.width / 2), int(y - 35)))


def mesa(t):
    img = cenario().copy()
    tarde.guarda_chuvas(img, t + 3)  # já pendurados, balançando
    pos, prof = posicoes(t)
    # o dado: visível antes da xícara descer e na revelação
    sobe = 0.0
    if t < BAIXA[1]:
        sobe = 1 - ease(max(0.0, (t - BAIXA[0]) / (BAIXA[1] - BAIXA[0])))
    elif t >= REVELA:
        sobe = ease(min(1.0, (t - REVELA) / 0.45))
    xi = 1  # a xícara que cobre o dado
    ordem = sorted(range(3), key=lambda i: prof[i])
    if sobe > 0.01:
        xd = SLOT_X[0] + (SLOT_X[2] - SLOT_X[0]) * pos[xi] / 2
        sombra_chao(img, xd, MESA_Y + 2, 150)
        E.cola(img, dado(), xd, MESA_Y - 100, -6)
    for i in ordem:
        x = SLOT_X[0] + (SLOT_X[2] - SLOT_X[0]) * pos[i] / 2
        p = prof[i]
        y = MESA_Y + 40 * p
        esc = ESC * (1 + 0.08 * p)
        lev = 250 * sobe if i == xi else 0
        sombra_chao(img, x, y + 4, 230 * esc, int(90 * (1 - lev / 600)))
        E.cola(img, xicara(CORES[i]), x + 30 * esc, y - 120 * esc - lev, (6 if i == xi and sobe > 0 else 0) * sobe, esc)
    return img


def numeros(img, t):
    for k, x in enumerate(SLOT_X):
        K.poe(img, K.etiqueta(str(k + 1), 70, BR, MAR), x, MESA_Y + 120, t, CONTA + 0.1 * k, 0, d=0.25)


def quadro_jogo(t):
    img = mesa(t)
    if t < EMB0 + 0.4:
        K.poe(img, K.titulo("ONDE ESTÁ\nO DADO?", 150, LAR), W / 2, 620, t, 0.05, -3)
    elif t < CONTA:
        K.poe(img, K.titulo("NÃO PISCA!", 130, LAR), W / 2, 680, t, EMB0 + 0.4, 2)
    elif t < REVELA:
        K.poe(img, K.titulo("COMENTA\n1, 2 OU 3!", 140, LAR), W / 2, 600, t, CONTA, -2)
        numeros(img, t)
        n = 3 - int((t - CONTA - 0.6) / 0.66)
        if t > CONTA + 0.6 and n > 0:
            u = (t - CONTA - 0.6) % 0.66
            E.cola(img, K.titulo(str(n), 200, AMA), W / 2, 880, 0, 1 + 0.4 * max(0, 1 - u * 6))
    else:
        numeros(img, t)
        K.poe(img, K.titulo(f"ERA A {RESPOSTA}!", 150, AMA), W / 2, 640, t, REVELA + 0.3, 3)
    K.marca(img)
    return img


def mergulho(t):
    """O dado cresce até cobrir a tela (vira a passagem para a montagem)."""
    img = quadro_jogo(t)
    u = (t - MERGULHO) / 0.35
    xd = SLOT_X[RESPOSTA - 1]
    s = 0.31 + 5 * ease(min(1.0, u))
    E.cola(img, dado(600), xd + (W / 2 - xd) * ease(u), MESA_Y - 100 + (H / 2 - MESA_Y + 100) * ease(u), 360 * u, s)
    return img


def montagem(t):
    k = max(i for i in range(len(MONT)) if INI_M[i] <= t)
    c, t0, d = MONT[k]
    u = t - INI_M[k]
    img = K.quadro_clip(c, t0, d + 0.05, 1.0, u)
    K.escurece(img, 1260, 1640, 120)
    K.poe(img, K.etiqueta(K.CLIPES[c][1], 54, (AMA, BR, LAR)[k % 3], MAR if k % 3 < 2 else BR), 330, 1470, u, 0.0,
          (-3, 2, -2)[k % 3], d=0.18)
    if t - INI_M[0] < 2.7:
        K.escurece(img, 520, 1040, 150)
        K.poe(img, K.titulo("NO BECAS, O JOGO\nÉ DE VERDADE!", 112, AMA), W / 2, 770, t, INI_M[0] + 0.1, -2)
    if u < 2 / FPS and k:
        img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, 120)))
    if t - INI_M[0] < 0.2:
        img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * (1 - (t - INI_M[0]) / 0.2)))))
    K.marca(img)
    return img


def final(t):
    u = t - CTA
    img = cenario().copy()
    tarde.guarda_chuvas(img, u)
    for i, x in enumerate(SLOT_X):  # as 3 xícaras descansando na mesa
        sombra_chao(img, x, MESA_Y + 220, 200)
        E.cola(img, xicara(CORES[i]), x + 26, MESA_Y + 110, 0, 0.85)
    K.poe(img, K.logo(230), W / 2, 450, u, 0.2)
    K.poe(img, K.card_cta(), W / 2, 860, u, 0.45, -1.5, d=0.35)
    K.poe(img, K.etiqueta("ACERTOU? COMENTA O NÚMERO!", 44, PET, BR), W / 2, 1210, u, 1.3, 1.5)
    return img


def quadro(t):
    if t < MERGULHO:
        img = quadro_jogo(t)
    elif t < INI_M[0]:
        img = mergulho(t)
    elif t < CTA:
        img = montagem(t)
    else:
        img = final(t)
        if t - CTA < 0.2:
            img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(200 * (1 - (t - CTA) / 0.2)))))
    return img.convert("RGB")


def render(fi):
    return quadro(fi / FPS).tobytes()


def trechos():
    return [(c, t0, d + 0.05, 1.0) for c, t0, d in MONT]


def audio(path_com, path_sem):
    ev = [(0.05, S.cartao(), 0.6), (0.3, S.dado(), 0.7), (BAIXA[1] - 0.02, S.louca(2200), 0.8)]
    for k, (a, b, d) in enumerate(TROCAS):
        ev += [(INI_T[k], S.arrasta(d), 0.8), (INI_T[k] + d * 0.95, S.louca(1900 + 140 * (k % 3)), 0.55)]
    ev += [(CONTA, S.cartao(), 0.6)]
    ev += [(CONTA + 0.6 + j * 0.66, S.tique(), 0.9) for j in range(3)]
    ev += [(REVELA, S.louca(2500), 0.7), (REVELA + 0.3, S.sino(), 0.8), (MERGULHO, S.dado(), 0.8),
           (MERGULHO + 0.05, S.sopro(0.35), 0.7), (INI_M[0], S.estouro(), 0.6)]
    ev += [(INI_M[k], S.cartao(), 0.5) for k in range(1, len(MONT))]
    ev += [(CTA, S.sopro(0.5, False), 0.6), (CTA + 0.45, S.cartao(), 0.6)]
    mus = S.musica_cafe(DUR)
    S.grava(path_com, DUR, ev, mus, musica_ganho=0.45, fx_ganho=0.85)
    S.grava(path_sem, DUR, ev, None, fx_ganho=0.85)


def main():
    os.makedirs(K.OUT, exist_ok=True)
    K.prepara(trechos())
    print("resposta:", RESPOSTA, "duração:", round(DUR, 2))
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:]]
        K.folha([quadro(x) for x in ts], os.path.join(K.OUT, "frames_xicaras.jpg"))
        return
    com, sem = os.path.join(K.OUT, "xicaras_com.wav"), os.path.join(K.OUT, "xicaras_sem.wav")
    audio(com, sem)
    K.entrega("xicaras", DUR, render, com, sem)


if __name__ == "__main__":
    main()
