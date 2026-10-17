#!/usr/bin/env python3
"""Reels "QUANTO TEMPO VOCÊ TEM?" (ideia 5, aprovada por ele em 17/out/2026). Sem narração, tudo escrito.
Identidade da Jéssica (Lilita One + Figtree, contorno marrom, sombra sólida, azul-claro/amarelo/laranja/petróleo): um
relógio grande cujo ponteiro corre até 15 min, 30 min, 1 hora e, na "noite toda", dá voltas enquanto o fundo escurece.
Em cada faixa, 3 FOTOS DO SITE caem em cartões. Tempo e jogadores = os do site da Sua Vez.

    python3 tempo.py --frame 1 4 ...   # out/frames.jpg
    python3 tempo.py                   # out/tempo_{com_trilha,para_musica}_final.mp4
"""
import argparse
import math
import os
import sys
from functools import lru_cache

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from base import W, H, FPS, OUT, texto, foto, folha, entrega  # noqa: E402
from motor import seg, ease, lerp, out_back, logo_card, cola  # noqa: E402

MARROM, AZUL_CL, AMARELO, LARANJA, PETROLEO, BRANCO = (63, 36, 18), (227, 243, 246), (255, 199, 31), (244, 136, 37), \
    (28, 124, 150), (250, 250, 250)
NOITE = (24, 30, 70)
FAIXAS = [  # (rótulo, minutos no relógio, cor, [(foto, nome, linha do site)])
    ("15 MIN", 15, LARANJA, [("tesouro_do_drag_o", "Tesouro do Dragão", "2 a 6 · 15 min"),
                             ("bad_signs", "Bad Signs", "2 a 6 · 15 min"), ("trio", "Trio", "3 a 6 · 15 min")]),
    ("30 MIN", 30, PETROLEO, [("beaver_creek", "Beaver Creek", "1 a 5 · 30 min"), ("metro", "Metro", "2 a 6 · 30 min"),
                              ("4_gods", "4 Gods", "2 a 4 · 30 min")]),
    ("1 HORA", 60, (210, 70, 60), [("c_atl", "Cóatl", "1 a 4 · 60 min"), ("dwar7s_fall", "Dwar7s Fall", "2 a 4 · 60 min"),
                                   ("echoes_of_time", "Echoes of Time", "2 a 4 · 60 min")]),
    ("A NOITE TODA", 240, (90, 60, 170), [("tikal", "Tikal", "2 a 4 · 90 min"), ("emberleaf", "Emberleaf", "1 a 5 · 2 h"),
                                          ("vast_the_fearsome_foes", "Vast", "1 a 7 · 90 min")]),
]
GANCHO = 2.2
POR = 3.4
T_SALVA = GANCHO + POR * len(FAIXAS)
SALVA = 2.0
T_CTA = T_SALVA + SALVA
DUR = T_CTA + 3.4
CX, CY, R = W / 2, 600, 285


def minutos(t):
    """Posição do ponteiro (em minutos) no tempo t."""
    if t < GANCHO:
        return (t / GANCHO) * 5
    alvo_ant = 5
    for k, (_r, m, _c, _j) in enumerate(FAIXAS):
        t0 = GANCHO + k * POR
        if t < t0 + POR or k == len(FAIXAS) - 1:
            u = ease(seg(t, t0, t0 + (0.6 if m < 100 else 1.4)))
            return lerp(alvo_ant, m, u)
        alvo_ant = m
    return FAIXAS[-1][1]


def noite(t):
    t0 = GANCHO + 3 * POR
    return ease(seg(t, t0, t0 + 0.5)) * (1 - ease(seg(t, T_SALVA, T_SALVA + 0.5)))


def fundo(t):
    n = noite(t)
    cor = tuple(int(lerp(a, b, n)) for a, b in zip(AZUL_CL, NOITE))
    img = Image.new("RGBA", (W, H), cor + (255,))
    d = ImageDraw.Draw(img)
    pont = tuple(int(lerp(a, b, n)) for a, b in zip((205, 230, 236), (40, 48, 96)))
    for y in range(40, H, 70):  # pontinhos da "trilha" do tabuleiro
        for x in range(40 + (y // 70 % 2) * 35, W, 70):
            d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=pont)
    return img


def relogio(img, t):
    d = ImageDraw.Draw(img)
    m = minutos(t)
    d.ellipse((CX - R + 14, CY - R + 16, CX + R + 14, CY + R + 16), fill=MARROM)  # sombra sólida
    d.ellipse((CX - R, CY - R, CX + R, CY + R), fill=BRANCO, outline=MARROM, width=14)
    cor = FAIXAS[0][2]
    for k, (_r, mm, c, _j) in enumerate(FAIXAS):
        if GANCHO + k * POR <= t:
            cor = c
    if t >= GANCHO and m <= 60:  # fatia colorida do tempo
        d.pieslice((CX - R + 26, CY - R + 26, CX + R - 26, CY + R - 26), -90, -90 + m * 6, fill=cor + (255,))
    for k in range(60):
        a = math.radians(k * 6 - 90)
        r0 = R - (44 if k % 5 == 0 else 32)
        d.line((CX + r0 * math.cos(a), CY + r0 * math.sin(a), CX + (R - 22) * math.cos(a), CY + (R - 22) * math.sin(a)),
               fill=MARROM, width=8 if k % 5 == 0 else 3)
    a = math.radians(m * 6 - 90)
    d.line((CX, CY, CX + (R - 60) * math.cos(a), CY + (R - 60) * math.sin(a)), fill=MARROM, width=18)
    d.ellipse((CX - 26, CY - 26, CX + 26, CY + 26), fill=AMARELO, outline=MARROM, width=8)
    for dx in (-110, 110):  # sininhos do despertador
        d.ellipse((CX + dx - 54, CY - R - 40, CX + dx + 54, CY - R + 50), fill=AMARELO, outline=MARROM, width=10)


@lru_cache(None)
def cartao(arq, w):
    return foto(arq, w, borda=9, cor_borda=MARROM, raio=26, sombra_a=0)


def card_solido(img, arq, x, y, w, rot):
    c = cartao(arq, w)
    sh = Image.new("RGBA", c.size, MARROM + (255,))
    sh.putalpha(c.getchannel("A"))
    cola(img, sh, x + 12, y + 14, rot=rot)
    cola(img, c, x, y, rot=rot)


def cena_gancho(img, t):
    u = out_back(seg(t, 0.0, 0.45))
    cola(img, texto("QUANTO TEMPO\nVOCÊ TEM?", "lilita", 120, BRANCO, MARROM, 10, 10, MARROM, entre=1.05), W / 2, 1200,
         rot=-2, sc=u)
    v = ease(seg(t, 0.6, 1.0))
    cola(img, texto("a gente tem o jogo certo pra ele", "figtree", 54, MARROM), W / 2, 1480, alpha=v)


def cena_faixa(img, t, k):
    rot_, m, cor, jogos = FAIXAS[k]
    t0 = GANCHO + k * POR
    lt = t - t0
    n = noite(t)
    sai = ease(seg(lt, POR - 0.2, POR))
    u = out_back(seg(lt, 0.15, 0.5))
    cola(img, texto(rot_, "lilita", 104, BRANCO, MARROM, 9, 9, MARROM), W / 2, 1000, rot=-3, sc=u * (1 - sai))
    xs = [190, 540, 890]
    for j, (arq, nome, linha) in enumerate(jogos):
        c = out_back(seg(lt, 0.35 + j * 0.16, 0.75 + j * 0.16))
        if c <= 0.01:
            continue
        y = 1330 + lerp(-500, 0, min(1, c)) + 600 * sai
        rot = (-4, 2, 5)[j] * (1 - 0.5 * min(1, c))
        card_solido(img, arq, xs[j], y, 330, rot)
        f = ease(seg(lt, 0.6 + j * 0.16, 0.9 + j * 0.16)) * (1 - sai)
        corn = BRANCO if n > 0.5 else MARROM
        cola(img, texto(nome, "lilita", 50 if len(nome) < 14 else 42, corn), xs[j], 1555, alpha=f)
        cola(img, texto(linha, "figtree", 38, corn), xs[j], 1610, alpha=f)


def cena_salva(img, t):
    lt = t - T_SALVA
    u = out_back(seg(lt, 0.0, 0.4))
    cola(img, texto("SALVA PRA PRÓXIMA\nNOITE DE JOGOS!", "lilita", 96, AMARELO, MARROM, 9, 9, MARROM, entre=1.05), W / 2,
         1080, rot=-2, sc=u)
    v = ease(seg(lt, 0.4, 0.8))
    cola(img, texto("e comenta: quanto tempo VOCÊ tem?", "figtree", 48, MARROM), W / 2, 1330, alpha=v)


def cena_cta(img, t):
    lt = t - T_CTA
    u = out_back(seg(lt, 0.0, 0.4))
    cola(img, logo_card(480), W / 2, 960, sc=u)
    v = ease(seg(lt, 0.3, 0.7))
    for k, (txt, s) in enumerate([("ALUGUE NA SUA VEZ", 92), ("3 JOGOS = 7 DIAS DE JOGO", 58),
                                   ("RESERVE ONLINE · RETIRE EM MAUÁ\nOU RECEBA EM CASA", 48), ("LINK NA BIO · @SUAVEZ_BG", 56)]):
        nome = "lilita" if k in (0, 3) else "figtree"
        cola(img, texto(txt, nome, s, MARROM if k else PETROLEO), W / 2, 1290 + k * 135 + (30 if k == 3 else 0), alpha=v)


def frame(t):
    img = fundo(t)
    if t < T_CTA:
        relogio(img, t)
    if t < GANCHO:
        cena_gancho(img, t)
    elif t < T_SALVA:
        cena_faixa(img, t, min(len(FAIXAS) - 1, int((t - GANCHO) / POR)))
    elif t < T_CTA:
        cena_salva(img, t)
    else:
        cena_cta(img, t)
    if t < T_CTA:
        img.alpha_composite(logo_card(150), (W - 186, 46))
    return img.convert("RGB")


def render_frame(fi):
    return frame(fi / FPS).tobytes()


def cues():
    c = [(0.05, "relogio", 0.6), (0.2, "pop", 0.6)]
    for k in range(len(FAIXAS)):
        t0 = GANCHO + k * POR
        c += [(t0, "whoosh", 0.4), (t0 + 0.2, "ding", 0.5)]
        c += [(t0 + 0.55 + j * 0.16, "pop", 0.5) for j in range(3)]
        c += [(t0 + 1.2 + q * 0.5, "tick", 0.25) for q in range(4)]
    c += [(T_SALVA, "reveal", 0.6), (T_CTA, "chime", 0.6)]
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    a = ap.parse_args()
    print(f"duração {DUR:.1f} s")
    if a.frame:
        os.makedirs(OUT, exist_ok=True)
        folha([frame(x) for x in a.frame], os.path.join(OUT, "frames_tempo.jpg"))
        return
    entrega("tempo", DUR, render_frame, cues(), "gameshow", musica_ganho=0.28)


if __name__ == "__main__":
    main()
