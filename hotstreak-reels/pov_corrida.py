#!/usr/bin/env python3
"""Hot Streak em 1ª PESSOA (9/nov, ideia dele): "tô só correndo normal na rua... olho pra trás e os mascotes estão
atrás de mim... e de repente eu tô DENTRO do jogo". Tudo desenhado aqui (ele não quer Gemini nem gravar), no estilo
chapado da arte do jogo, com os mascotes e a torcida OFICIAIS do manual (p_*.png, v_torcida_limpa.png).

    0–4,2     correndo na rua DE VERDADE (gravação deles na calçada da Matriz, 2x, balanço de corrida)
    4,2–4,7   olha pra trás (chicote com borrão)
    4,7–8,4   os 4 mascotes correndo atrás de você na mesma rua (o vídeo de trás pra frente; espelhar deixava a placa da Alquifarma ao contrário)
    8,4–8,9   olha pra frente de novo (chicote) e a rua virou a pista do Hot Streak
    9,0–15,4  pista do Hot Streak em 1ª pessoa, torcida, confete; os mascotes te ultrapassam com o nome BR
    15,4–19   "EM QUEM VOCÊ APOSTA?" com os 4
    19–24     tela final do hs.py

    /usr/bin/python3 pov_corrida.py --frame 1 3.8 4.4 6 8.7 10 12 14 16 20
    /usr/bin/python3 pov_corrida.py      → out/pov_{com_som,para_musica}_final.mp4
"""
import argparse
import math
import os
import subprocess
import sys
from functools import lru_cache

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import hs as HS
import som_hs as som
from hs import W, H, FPS, RED, YEL, WHITE, INK, cola, placa, estouro, com_sombra, confete, pop, logo_card, ease, seg

ROOT = HS.ROOT
OUT = HS.OUT
sys.path.insert(0, os.path.join(ROOT, "..", "listas-reels"))
from base import final_loudness  # noqa: E402

T_OLHA, T_ATRAS, T_VIRA, T_JOGO, T_COM, T_CTA, DUR = 4.2, 4.7, 8.4, 8.9, 15.4, 19.0, 24.0
F = 950.0           # distância focal (px)
HC = 1.55           # altura do olho (m)
Y0 = 820            # horizonte na tela
PASSO = 2.7         # passos por segundo
VEL = 4.2           # m/s (corrida leve)
DY_RUA = 200        # na rua o horizonte fica mais baixo (mais casa e céu, menos asfalto)
MASC = [("p_hurley.png", "JIBA"), ("p_gobbler.png", "GLUGLU"), ("p_dangle.png", "BRINCO"), ("p_mum.png", "MONA")]

CEU = (178, 222, 238)
ASFALTO, ASFALTO2 = (96, 96, 104), (110, 110, 118)
CALCADA = (226, 214, 190)
GUIA = (240, 236, 226)
CASAS = [(244, 196, 120), (232, 140, 110), (150, 196, 170), (246, 226, 170), (176, 170, 220), (240, 170, 160),
         (200, 220, 150)]
MURO = [(238, 232, 214), (214, 200, 176), (250, 244, 228)]
FOLHA = [(62, 150, 80), (48, 128, 70), (86, 170, 90)]


# ---------------------------------------------------------------- câmera
def balanco(t, forte=1.0):
    """Cabeça de quem corre: sobe e desce 2x por passo e balança de lado."""
    ph = t * PASSO * 2 * math.pi
    return 14 * forte * abs(math.sin(ph)), 9 * forte * math.sin(ph / 2), 1.2 * forte * math.sin(ph / 2)


def proj(x, y, z, dy=0.0, dx=0.0):
    """Ponto do mundo (x lado, y altura, z à frente) → tela."""
    z = max(z, 0.05)
    return W / 2 + dx + F * x / z, Y0 + dy + F * (HC - y) / z


# ---------------------------------------------------------------- a rua
@lru_cache(None)
def quarteirao(seed):
    """Lista de objetos da rua (casas/muros/árvores/postes) em z de 0 a 400 m, dos dois lados."""
    rng = np.random.default_rng(seed)
    obj = []
    for lado in (-1, 1):
        z = 2.0
        while z < 400:
            larg = rng.uniform(7, 12)
            alt = rng.uniform(4.2, 7.5)
            obj.append(("casa", lado, z, z + larg, alt, CASAS[rng.integers(len(CASAS))], rng.uniform(0, 1)))
            obj.append(("muro", lado, z, z + larg, 1.8, MURO[rng.integers(len(MURO))], rng.uniform(0, 1)))
            if rng.uniform() < 0.7:
                obj.append(("arvore", lado, z + larg * rng.uniform(0.3, 0.7), 0, rng.uniform(3.6, 5.2),
                            FOLHA[rng.integers(len(FOLHA))], rng.uniform(0, 1)))
            z += larg + rng.uniform(0.3, 1.2)
        for z in np.arange(6, 400, 26):
            obj.append(("poste", lado, z + (8 if lado > 0 else 0), 0, 6.5, (70, 70, 80), 0))
    return obj


def rua(t, seed, avanca=True):
    """Quadro da rua em perspectiva. avanca=False: olhando pra trás (tudo se afasta)."""
    by, bx, br = balanco(t)
    by += DY_RUA
    s = VEL * t
    img = Image.new("RGB", (W, H), CEU)
    d = ImageDraw.Draw(img)
    # céu com degradê suave e nuvens chapadas
    for y in range(0, int(Y0 + by) + 2, 6):
        u = y / (Y0 + 1)
        d.rectangle((0, y, W, y + 6), fill=tuple(int(a + (b - a) * u) for a, b in zip((140, 200, 232), CEU)))
    for k, (cx, cy, r) in enumerate(((180, 300, 90), (760, 220, 120), (1000, 420, 70))):
        cx = (cx - t * 10 * (1 if avanca else -1)) % (W + 300) - 150
        for ox, oy, rr in ((0, 0, r), (r * 0.8, 15, r * 0.7), (-r * 0.8, 20, r * 0.6)):
            d.ellipse((cx + ox - rr, cy + oy - rr * 0.6, cx + ox + rr, cy + oy + rr * 0.6), fill=(250, 252, 252))
    yh = Y0 + by
    # chão: asfalto + calçadas (trapézios até o horizonte)
    rua_l, calc = 2.6, 1.7
    far = 400

    def quad(x0, x1, z0, z1, cor):
        pts = [proj(x0, 0, z0, by, bx), proj(x1, 0, z0, by, bx), proj(x1, 0, z1, by, bx), proj(x0, 0, z1, by, bx)]
        d.polygon(pts, fill=cor)

    d.rectangle((0, yh, W, H), fill=CALCADA)
    quad(-rua_l, rua_l, 0.3, far, ASFALTO)
    # faixas do asfalto passando (sensação de velocidade)
    off = s % 6.0
    for z in np.arange(-off + 0.3, 120, 6.0):
        if z > 0.3:
            quad(-rua_l, rua_l, z, z + 3.0, ASFALTO2)
        if z > 0.5:
            quad(-0.09, 0.09, z, z + 2.2, (250, 230, 120))
    for lado in (-1, 1):
        quad(lado * rua_l, lado * (rua_l + 0.18), 0.3, far, GUIA)
        offc = s % 1.4
        for z in np.arange(-offc + 0.4, 60, 1.4):  # juntas da calçada
            if z > 0.4:
                quad(lado * (rua_l + 0.2), lado * (rua_l + calc), z, z + 0.05, (206, 192, 166))
    # objetos de trás pra frente
    obj = quarteirao(seed)
    vis = []
    for o in obj:
        kind, lado, z0, z1, alt, cor, r = o
        zz0 = z0 - s % 400
        zz1 = (z1 - s % 400) if z1 else 0
        if zz0 < -15:
            zz0 += 400
            zz1 = zz1 + 400 if z1 else 0
        vis.append((max(zz0, zz1 if z1 else zz0), kind, lado, zz0, zz1, alt, cor, r))
    vis.sort(key=lambda v: -v[0])
    xc = rua_l + calc  # alinhamento dos muros
    for _, kind, lado, z0, z1, alt, cor, r in vis:
        if kind in ("casa", "muro"):
            if z1 < 0.4 or z0 > 160:
                continue
            za = max(z0, 0.4)
            x = lado * (xc + (3.0 if kind == "casa" else 0))
            sombra_c = tuple(int(c * 0.82) for c in cor)
            pts = [proj(x, 0, za, by, bx), proj(x, 0, z1, by, bx), proj(x, alt, z1, by, bx), proj(x, alt, za, by, bx)]
            d.polygon(pts, fill=cor)
            if kind == "casa":
                # telhado (faixa escura) e janelas
                d.polygon([proj(x, alt, za, by, bx), proj(x, alt, z1, by, bx), proj(x, alt + 0.5, z1, by, bx),
                           proj(x, alt + 0.5, za, by, bx)], fill=(170, 80, 60))
                n = int((z1 - z0) / 3)
                for j in range(n):
                    w0 = z0 + 1.2 + j * 3
                    if w0 < 0.5:
                        continue
                    for wy in ((2.6, 3.8),) if alt < 5.5 else ((2.6, 3.8), (4.4, 5.4)):
                        d.polygon([proj(x, wy[0], w0, by, bx), proj(x, wy[0], w0 + 1.3, by, bx),
                                   proj(x, wy[1], w0 + 1.3, by, bx), proj(x, wy[1], w0, by, bx)], fill=(90, 150, 190))
            else:
                # portão (faixa escura) no meio do muro
                g0 = z0 + (z1 - z0) * (0.3 + 0.3 * r)
                if g0 > 0.5:
                    d.polygon([proj(x, 0, g0, by, bx), proj(x, 0, g0 + 2.4, by, bx), proj(x, 1.7, g0 + 2.4, by, bx),
                               proj(x, 1.7, g0, by, bx)], fill=(120, 110, 100))
            # face da frente (quando o bloco ainda está à frente)
            if z0 > 0.4:
                xin = lado * (xc + (3.0 if kind == "casa" else 0) + (8 if kind == "casa" else 0.25))
                d.polygon([proj(x, 0, z0, by, bx), proj(xin, 0, z0, by, bx), proj(xin, alt, z0, by, bx),
                           proj(x, alt, z0, by, bx)], fill=sombra_c)
        elif kind == "arvore":
            if z0 < 0.6 or z0 > 160:
                continue
            x = lado * (rua_l + 1.2)
            bxp, byp = proj(x, 0, z0, by, bx)
            tx, ty = proj(x, alt * 0.55, z0, by, bx)
            wt = max(2, F * 0.22 / z0)
            d.rectangle((bxp - wt / 2, ty, bxp + wt / 2, byp), fill=(120, 80, 50))
            rc = F * 1.6 / z0
            cx, cy = proj(x, alt * 0.8, z0, by, bx)
            for ox, oy, k in ((0, 0, 1.0), (-0.6, 0.3, 0.75), (0.6, 0.3, 0.75)):
                rr = rc * k
                d.ellipse((cx + ox * rc - rr, cy + oy * rc - rr, cx + ox * rc + rr, cy + oy * rc + rr), fill=cor)
        elif kind == "poste":
            if z0 < 0.6 or z0 > 160:
                continue
            x = lado * (rua_l + 0.5)
            p0 = proj(x, 0, z0, by, bx)
            p1 = proj(x, alt, z0, by, bx)
            p2 = proj(x - lado * 1.2, alt, z0, by, bx)
            wt = max(2, F * 0.12 / z0)
            d.line((p0, p1), fill=cor, width=int(wt))
            d.line((p1, p2), fill=cor, width=int(wt * 0.8))
    img = img.rotate(br, resample=Image.BICUBIC, center=(W / 2, H / 2), expand=False, fillcolor=CEU)
    return img.convert("RGBA")


# ---------------------------------------------------------------- mascotes
def mascote_frente(img, nome, x, z, t, fase, dy=0.0, dx=0.0, alt=1.7):
    """Mascote correndo NA DIREÇÃO da câmera (pulinho, balanço, esticadinha) no ponto (x, z) do chão."""
    ph = HS.pose(t) * 2 * math.pi * 1.7 + fase
    hop = abs(math.sin(ph)) * 0.18
    px, py = proj(x, hop, z, dy, dx)
    h = F * alt / z
    sq = 1 + 0.06 * math.cos(2 * ph)
    d = ImageDraw.Draw(img, "RGBA")
    gx, gy = proj(x, 0, z, dy, dx)
    d.ellipse((gx - h * 0.26, gy - h * 0.035, gx + h * 0.26, gy + h * 0.035), fill=(25, 25, 25, 70))
    # +0,07h: o sprite com sombra tem margem embaixo; assim o pé encosta na sombra do chão
    cola(img, com_sombra(nome, int(min(2400, max(40, h)))), px, py - h * 0.43, 8 * math.sin(ph), 1.0, 1 / sq, sq)


def borrao_h(img, k):
    if k < 2:
        return img
    a = cv2.blur(np.asarray(img.convert("RGB")), (int(k) | 1, 1))
    return Image.fromarray(a).convert("RGBA")


# ---------------------------------------------------------------- rua DE VERDADE (gravação deles no Beca's, 6/nov)
REAL = os.path.join(OUT, "rua_real")   # 151125 de 12 a 23 s (calçada da Matriz, sem placa de carro), 30 q/s
NREAL = len(os.listdir(REAL)) if os.path.isdir(REAL) else 1
DY_REAL = 20                            # horizonte da calçada no vídeo (~y 780)


def rua_real(t, para_tras=False):
    """Correndo de verdade: o vídeo deles a 2x com balanço de corrida. Pra trás = o mesmo trecho de trás pra frente."""
    by, bx, br = balanco(t, 1.2)
    s = 0.5 + t * 2.0 if not para_tras else 10.6 - (t - T_OLHA) * 1.7
    n = int(min(NREAL, max(1, round(s * 30))))
    im = Image.open(os.path.join(REAL, "%04d.jpg" % n)).convert("RGB")
    k = 1.08
    im = im.resize((int(W * k), int(H * k)), Image.BICUBIC)
    x0 = (im.width - W) / 2 - bx
    y0 = (im.height - H) / 2 - by * 0.8
    im = im.crop((int(x0), int(y0), int(x0) + W, int(y0) + H)).rotate(br, resample=Image.BICUBIC)
    return im.convert("RGBA")


# ---------------------------------------------------------------- cenas
def cena_rua(t):
    img = rua_real(t)
    if t < 3.3:
        cola(img, placa("EU TAVA SÓ\nCORRENDO NORMAL...", 84, WHITE, INK), 540, 360, -2, pop(t, 0.15))
    else:
        tr = 3.3
        cola(img, estouro("TUM\nTUM!", 300), 240 + 15 * math.sin(t * 30), 470, -8, pop(t, tr))
        cola(img, estouro("TUM\nTUM!", 260), 850, 420 + 10 * math.sin(t * 27), 10, pop(t, tr + 0.35))
        cola(img, placa("...QUE BARULHO\nÉ ESSE?!", 80, YEL, RED), 540, 1350, 2, pop(t, tr + 0.2))
    return img


def cena_atras(t, olhando=1.0):
    by, bx, br = balanco(t, 1.3)
    by = DY_REAL + by * 0.3
    img = rua_real(t, True)
    u = t - T_ATRAS
    for k, (nome, _) in enumerate(MASC):
        x = (-0.95, 1.0, -0.4, 0.45)[k]
        z = (2.9, 3.2, 4.3, 4.6)[k] - 0.8 * ease(seg(u, 0, 3.5))
        mascote_frente(img, nome, x, z, t, k * 1.4, by, bx)
    if u > 0.2:
        cola(img, placa("...AÍ EU OLHEI\nPRA TRÁS!", 90, RED, YEL), 540, 330, 2, pop(t, T_ATRAS + 0.2))
    if u > 1.4:
        cola(img, estouro("SOCORRO!", 330), 830, 600, 9, pop(t, T_ATRAS + 1.4))
    return img


def cena_olha(t):
    """Chicote: a rua da frente sai pra esquerda borrada e a de trás entra pela direita."""
    u = ease(seg(t, T_OLHA, T_ATRAS))
    a = rua_real(t)
    b = cena_atras(t)
    k = 120 * math.sin(u * math.pi)
    a, b = borrao_h(a, k), borrao_h(b, k)
    img = Image.new("RGBA", (W, H))
    img.paste(a, (int(-W * u), 0))
    img.paste(b, (int(W * (1 - u)), 0))
    return img


# --- dentro do jogo
@lru_cache(None)
def torcida_alta():
    tc = HS.torcida()
    k = (Y0 + 260) / tc.height
    return tc.resize((int(tc.width * k), Y0 + 260), Image.LANCZOS)


def pista_pov(t):
    by, bx, br = balanco(t, 0.9)
    img = Image.new("RGB", (W, H), (36, 110, 54))
    tc = torcida_alta()
    img.paste(tc.convert("RGB"), (int((W - tc.width) / 2 + bx * 0.3), int(-170 + by * 0.4)), tc)
    d = ImageDraw.Draw(img)
    s = VEL * 1.6 * t
    far = 120
    lanes = 4
    lw = 1.6
    x0 = -lanes * lw / 2

    def quad(xa, xb, za, zb, cor):
        d.polygon([proj(xa, 0, za, by, bx), proj(xb, 0, za, by, bx), proj(xb, 0, zb, by, bx), proj(xa, 0, zb, by, bx)],
                  fill=cor)

    quad(x0 - 30, x0 + lanes * lw + 30, 0.3, far, (36, 110, 54))
    for k in range(lanes):
        quad(x0 + k * lw, x0 + (k + 1) * lw, 0.3, far, (52, 160, 76) if k % 2 else (62, 178, 86))
    for k in range(lanes + 1):
        xl = x0 + k * lw
        if k in (0, lanes):
            quad(xl - 0.06, xl + 0.06, 0.3, far, WHITE)
            continue
        off = s % 2.4
        for z in np.arange(-off + 0.3, 70, 2.4):
            if z > 0.3:
                quad(xl - 0.05, xl + 0.05, z, z + 1.1, (245, 245, 235))
    off = s % 5.0  # estrelinhas do tapete passando
    for z in np.arange(-off + 0.6, 60, 5.0):
        for k in range(lanes):
            if z < 0.6:
                continue
            cx, cy = proj(x0 + (k + 0.5) * lw, 0, z + (k % 2) * 2.5, by, bx)
            r = F * 0.28 / (z + (k % 2) * 2.5)
            HS.estrela(d, cx, cy, r, (176, 232, 176))
    img = img.rotate(br, resample=Image.BICUBIC, center=(W / 2, H / 2), expand=False, fillcolor=(36, 110, 54))
    return img.convert("RGBA")


ULTRAPASSA = [(9.6, 0, -2.4), (10.9, 1, 2.4), (12.2, 2, -0.8), (13.5, 3, 0.8)]  # (instante, mascote, x da raia)


def cena_jogo(t):
    by, bx, br = balanco(t, 0.9)
    img = pista_pov(t)
    u = t - T_JOGO
    # mascotes passando: chegam por trás (bem perto, embaixo) e vão ficando lá na frente
    lista = []
    for t0, k, x in ULTRAPASSA:
        if t >= t0:
            v = t - t0
            z = 1.1 + 3.2 * v + 1.6 * v * v
            lista.append((z, k, x, t0))
    for z, k, x, t0 in sorted(lista, reverse=True):
        nome, apelido = MASC[k]
        mascote_frente(img, nome, x, z, t, k * 1.3, by, bx, alt=1.9)
        if t - t0 < 1.3:
            px, py = proj(x, 2.3, z, by, bx)
            cola(img, placa(apelido, 70, YEL, RED), min(W - 170, max(170, px)), max(330, py - 60), -3, pop(t, t0 + 0.15))
    confete(img, t, 70, 9, 0, 1600)
    if u < 2.6:
        cola(img, placa("EU TÔ DENTRO\nDO HOT STREAK!", 96, RED, YEL), 540, 1330, -2, pop(t, T_JOGO + 0.1))
    elif t < T_COM:
        cola(img, placa("E ELES TÃO\nGANHANDO DE MIM!", 84, WHITE, INK), 540, 1360, 2, pop(t, T_JOGO + 2.6))
    if u < 0.15:
        img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(220 * (1 - u / 0.15)))))
    return img


def cena_vira(t):
    """Olha pra FRENTE de novo (chicote no sentido contrário) e a rua virou a pista do Hot Streak."""
    u = ease(seg(t, T_VIRA, T_JOGO))
    a = cena_atras(t)
    b = cena_jogo(T_JOGO + 0.2)
    k = 120 * math.sin(u * math.pi)
    a, b = borrao_h(a, k), borrao_h(b, k)
    img = Image.new("RGBA", (W, H))
    img.paste(a, (int(W * u), 0))
    img.paste(b, (int(-W * (1 - u)), 0))
    return img


def cena_comenta(t):
    u = t - T_COM
    img = pista_pov(T_COM + u * 0.3)
    img.alpha_composite(Image.new("RGBA", (W, H), (20, 10, 20, 120)))
    confete(img, t, 60, 4, 0, H)
    cola(img, placa("E VOCÊ,\nEM QUEM APOSTA?", 100, RED, YEL), 540, 360, -2, pop(t, T_COM + 0.1))
    for k, (nome, apelido) in enumerate(MASC):
        cx = 150 + k * 260
        cy = 1000 + (40 if k % 2 else 0)
        sc = pop(t, T_COM + 0.4 + 0.18 * k)
        hop = 20 * abs(math.sin((t + k * 0.3) * 6))
        cola(img, com_sombra(nome, 380), cx, cy - hop, (-1) ** k * 4, sc)
        cola(img, placa(apelido, 46, WHITE, INK), cx, cy + 250, (-1) ** k * 3, sc)
    if u > 1.3:
        b = 1 + 0.04 * abs(math.sin(t * 5))
        cola(img, placa("COMENTA AQUI!", 88, YEL, RED), 540, 1500, 2, pop(t, T_COM + 1.3) * b)
    return img


def frame(fi):
    t = fi / FPS
    if t < T_OLHA:
        img = cena_rua(t)
    elif t < T_ATRAS:
        img = cena_olha(t)
    elif t < T_VIRA:
        img = cena_atras(t)
    elif t < T_JOGO:
        img = cena_vira(t)
    elif t < T_COM:
        img = cena_jogo(t)
    elif t < T_CTA:
        img = cena_comenta(t)
    else:
        img = Image.new("RGBA", (W, H), (40, 110, 60, 255))
        HS.cena_cta(img, HS.SCENES[HS.CTA][0] + (t - T_CTA))
    if t < T_CTA:
        wm = logo_card(180)
        img.alpha_composite(wm, (W - wm.width - 30, 40))
    return img.convert("RGB")


def render(fi):
    return frame(fi).tobytes()


# ---------------------------------------------------------------- som
SR = som.SR


def passos(t0, t1, ganho=1.0, freq=PASSO, grave=False):
    out = np.zeros(int(DUR * SR) + SR)
    t = t0
    while t < t1:
        tt = som.t_(0.12)
        f0 = 70 if grave else 110
        s = np.sin(2 * np.pi * f0 * tt) * np.exp(-tt * 40) + som.lp(som.noise(0.12), 6) * np.exp(-tt * 30) * 0.6
        som.add(out, s * ganho, t, 1.0)
        t += 1 / freq
    return out[:int(DUR * SR)]


def respira(t0, t1):
    out = np.zeros(int(DUR * SR) + SR)
    t = t0
    while t < t1:
        d = 0.32
        tt = som.t_(d)
        s = som.hp(som.noise(d), 4) * np.sin(np.pi * tt / d) ** 2 * 0.25
        som.add(out, s, t, 1.0)
        t += 1 / (PASSO / 2)
    return out[:int(DUR * SR)]


def audio():
    n = int(DUR * SR)
    fx = np.zeros(n)
    fx += passos(0.0, T_VIRA, 0.5)
    fx += respira(0.1, T_VIRA)
    fx += passos(3.3, T_VIRA, 0.9, 3.2, grave=True)  # os mascotes chegando: TUM TUM
    cues = [(T_OLHA, "swoosh", 0.9), (T_ATRAS + 1.4, "hit", 0.6), (T_VIRA, "swoosh", 0.9), (T_JOGO, "crowd", 0.9),
            (T_JOGO + 0.05, "bugle", 0.8), (T_COM, "ding", 0.6), (T_COM + 1.3, "pop", 0.6), (T_CTA, "cash", 0.6)]
    cues += [(t0 + 0.1, "boing", 0.5) for t0, _, _ in ULTRAPASSA]
    for t, nome, g in cues:
        som.add(fx, som.sn.FX[nome](), t, g)
    mus = np.zeros(n)
    g = som.galope(DUR - T_VIRA + 0.5)
    som.add(mus, g / (np.abs(g).max() + 1e-9) * 0.3, T_VIRA, 1.0)
    # antes da virada: só um pulso baixinho de suspense
    tt = np.arange(n) / SR
    pulso = np.sin(2 * np.pi * 55 * tt) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 1.6 * tt))) * 0.05
    pulso *= np.clip((tt - 2.0) / 1.5, 0, 1) * (tt < T_VIRA)
    mus += pulso
    import wave

    def grava(path, x):
        x = np.tanh(x * 1.1) / np.tanh(1.1)
        x = x / (np.abs(x).max() + 1e-9) * 0.7
        st = np.repeat((x * 32767).astype(np.int16)[:, None], 2, 1)
        with wave.open(path, "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(st.tobytes())

    com, sem = os.path.join(OUT, "pov_com.wav"), os.path.join(OUT, "pov_sem.wav")
    grava(com, fx * 0.55 + mus)
    grava(sem, fx * 0.55)
    return com, sem


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.frame:
        ims = [frame(int(round(x * FPS))) for x in a.frame]
        cols = min(6, len(ims))
        rows = math.ceil(len(ims) / cols)
        sheet = Image.new("RGB", (360 * cols, 640 * rows))
        for k, im in enumerate(ims):
            sheet.paste(im.resize((360, 640), Image.LANCZOS), (360 * (k % cols), 640 * (k // cols)))
        sheet.save(os.path.join(OUT, "frames_pov.jpg"), quality=88)
        return
    com, sem = audio()
    n = int(DUR * FPS)
    base = os.path.join(OUT, "pov_com_som.mp4")
    HS.encode(base, com, n, render, list(range(n)))
    semv = os.path.join(OUT, "pov_para_musica.mp4")
    subprocess.run([HS.ffmpeg(), "-y", "-loglevel", "error", "-i", base, "-i", sem, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", semv], check=True)
    for arq in (base, semv):
        final_loudness(arq, arq.replace(".mp4", "_final.mp4"))
    print("ok", DUR)


if __name__ == "__main__":
    main()
