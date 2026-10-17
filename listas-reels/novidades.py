#!/usr/bin/env python3
"""Reels "CHEGOU NA SUA VEZ!" (ideia 9, aprovada por ele em 17/out/2026): os 4 jogos que entraram no site. Só texto.
Uma caixa de entrega de papelão no pé da tela: treme, as abas abrem e cada jogo SOBE de dentro dela (a FOTO DO SITE, num
cartão), com selo NOVIDADE, nome, jogadores/tempo (os do site) e uma frase do que é o jogo (conferida na ficha do site).
Fecha com os 4 juntos ("Qual você aluga primeiro?") e o CTA.

    python3 novidades.py --frame 1 3 ...   # out/frames_novidades.jpg
    python3 novidades.py                   # out/novidades_{com_trilha,para_musica}_final.mp4
"""
import argparse
import math
import os
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from base import W, H, FPS, OUT, texto, foto, folha, entrega  # noqa: E402
from motor import seg, ease, lerp, out_back, logo_card, cola, sombra  # noqa: E402

FUNDO_A, FUNDO_B = (14, 74, 92), (6, 36, 50)
AMARELO, BRANCO, TINTA = (255, 199, 31), (255, 255, 255), (30, 22, 14)
KRAFT, KRAFT_ESC, FITA = (200, 152, 98), (160, 114, 70), (226, 196, 140)
JOGOS = [  # (foto do site, nome, linha do site, frase)
    ("marvel_united_multiverse", "Marvel United: Multiverse", "1 a 5 jogadores · 40 min",
     "Heróis da Marvel juntos\ncontra um vilão do jogo"),
    ("trial_by_trolley", "Trial by Trolley", "3 a 13 jogadores · 90 min",
     "Convença o maquinista a mandar\no bonde pro trilho do outro time"),
    ("trio", "Trio", "3 a 6 jogadores · 15 min", "Ache 3 cartas iguais revelando\nas cartas dos outros"),
    ("convidados_indesejados", "Convidados Indesejados", "1 a 8 jogadores · 75 min",
     "Quem matou o Sr. Walton?\nDedução com cartas e pistas"),
]
GANCHO = 2.4
POR = 3.5
T_FIM = GANCHO + POR * len(JOGOS)
FIM = 2.8
T_CTA = T_FIM + FIM
DUR = T_CTA + 3.4
BX, BY, BW, BH = W / 2, 1560, 700, 330  # caixa: centro da frente, largura, altura


@lru_cache(None)
def fundo():
    yy = np.linspace(0, 1, H)[:, None, None]
    a = np.array(FUNDO_A) * (1 - yy) + np.array(FUNDO_B) * yy
    img = Image.fromarray((a * np.ones((1, W, 1))).astype(np.uint8)).convert("RGBA")
    luz = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(luz).ellipse((W / 2 - 520, 200, W / 2 + 520, 1200), fill=(120, 220, 240, 70))
    img.alpha_composite(luz.filter(ImageFilter.GaussianBlur(150)))
    return img


rng = np.random.default_rng(5)
CONFETE = [(rng.random() * W, rng.random() * H, rng.random() * 6.28, 0.6 + rng.random(),
            [(244, 136, 37), (255, 199, 31), (250, 250, 250), (230, 70, 90), (90, 200, 150)][int(rng.random() * 5)])
           for _ in range(70)]


def confete(img, t, forca):
    if forca <= 0.01:
        return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for x, y, f, v, c in CONFETE:
        yy = (y + t * 160 * v) % H
        xx = x + 30 * math.sin(t * 2 * v + f)
        a = math.sin(t * 4 * v + f)
        d.polygon([(xx - 9, yy - 5 * a), (xx + 9, yy + 5 * a), (xx + 9, yy + 5 * a + 8), (xx - 9, yy - 5 * a + 8)],
                  fill=c + (int(220 * forca),))
    img.alpha_composite(lay)


def abertura(t):
    """0 = caixa fechada, 1 = abas abertas."""
    return ease(seg(t, GANCHO - 0.5, GANCHO))


def tremor(t):
    if t < GANCHO - 0.5:
        return 8 * math.sin(t * 40) * (0.4 + 0.6 * seg(t, 0.4, GANCHO - 0.5))
    return 0


def aba(d, cx, y, lado, u):
    """Aba presa na lateral da boca da caixa (lado = -1 esquerda, +1 direita): fechada aponta para dentro e cobre a
    boca; aberta fica quase deitada para fora."""
    th = math.radians(lerp(0, 160, u))
    L = BW / 2
    a0 = (cx + lado * BW / 2, y)
    a1 = (cx + lado * (BW / 2 - 40), y - 60)
    v = (-lado * L * math.cos(th), -L * math.sin(th) * 0.9)
    pts = [a0, a1, (a1[0] + v[0], a1[1] + v[1]), (a0[0] + v[0], a0[1] + v[1])]
    d.polygon(pts, fill=KRAFT if th > math.pi / 2 else KRAFT_ESC, outline=TINTA, width=6)


def caixa_atras(img, t):
    d = ImageDraw.Draw(img)
    x = BX + tremor(t)
    topo = BY - BH / 2
    d.polygon([(x - BW / 2, topo), (x + BW / 2, topo), (x + BW / 2 - 40, topo - 60), (x - BW / 2 + 40, topo - 60)],
              fill=(110, 76, 44), outline=TINTA, width=6)  # boca da caixa (fundo escuro)
    u = abertura(t)
    if u > 0.02:
        aba(d, x, topo, -1, u)
        aba(d, x, topo, 1, u)


def caixa_frente(img, t):
    d = ImageDraw.Draw(img)
    x = BX + tremor(t)
    topo = BY - BH / 2
    d.rectangle((x - BW / 2 + 16, topo + 16, x + BW / 2 + 16, BY + BH / 2 + 16), fill=(0, 0, 0, 90))
    d.rectangle((x - BW / 2, topo, x + BW / 2, BY + BH / 2), fill=KRAFT, outline=TINTA, width=7)
    d.rectangle((x - 70, topo, x + 70, BY + BH / 2), fill=FITA)
    cola(img, texto("FRÁGIL · JOGOS NOVOS", "bungee", 34, (150, 40, 30)), x, BY + 90, rot=-3)
    if abertura(t) < 0.02:  # fechada: abas deitadas por cima, com a fita
        d.polygon([(x - BW / 2, topo), (x + BW / 2, topo), (x + BW / 2 - 40, topo - 60), (x - BW / 2 + 40, topo - 60)],
                  fill=KRAFT_ESC, outline=TINTA, width=6)
        d.rectangle((x - 70, topo - 60, x + 70, topo), fill=FITA)


@lru_cache(None)
def cartao(arq, w):
    return foto(arq, w, borda=12, cor_borda=BRANCO, raio=26, sombra_a=0.55)


def jogo_sobe(img, t, k, w=600):
    arq, *_ = JOGOS[k]
    lt = t - GANCHO - k * POR
    sobe = out_back(seg(lt, 0.05, 0.6), 1.2)
    sai = ease(seg(lt, POR - 0.3, POR))
    y = lerp(BY, 640, sobe) - 1300 * sai
    cola(img, cartao(arq, w), W / 2 + tremor(t), y, rot=lerp(0, -8, sai))


@lru_cache(None)
def selo_novidade():
    s = texto("NOVIDADE!", "bungee", 54, TINTA)
    im = Image.new("RGBA", (s.width + 40, s.height + 10), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=im.height // 2, fill=AMARELO,
                                          outline=TINTA, width=6)
    im.alpha_composite(s, (20, 5))
    return im


def cena_gancho(img, t):
    u = out_back(seg(t, 0.1, 0.55))
    cola(img, texto("CHEGOU\nNOVIDADE!", "lilita", 150, AMARELO, TINTA, 10, 10, TINTA, entre=1.0), W / 2, 640, rot=-3, sc=u)
    v = ease(seg(t, 0.6, 1.0))
    cola(img, texto("4 jogos novos no acervo da Sua Vez", "figtree", 50, BRANCO), W / 2, 960, alpha=v)


def cena_fim(img, t):
    lt = t - T_FIM
    u = out_back(seg(lt, 0.0, 0.4))
    cola(img, texto("QUAL VOCÊ ALUGA\nPRIMEIRO?", "lilita", 96, AMARELO, TINTA, 9, 9, TINTA, entre=1.05), W / 2, 330,
         rot=-2, sc=u)
    pos = [(300, 760), (780, 760), (300, 1230), (780, 1230)]
    for k, (arq, nome, _l, _f) in enumerate(JOGOS):
        c = out_back(seg(lt, 0.15 + k * 0.1, 0.5 + k * 0.1))
        cola(img, cartao(arq, 400), pos[k][0], pos[k][1], rot=(-3, 3, 2, -2)[k], sc=c)
    v = ease(seg(lt, 0.8, 1.2))
    cola(img, texto("Comenta aqui!", "lilita", 76, BRANCO, TINTA, 7, 6, TINTA), W / 2, 1580, alpha=v)


def cena_cta(img, t):
    lt = t - T_CTA
    u = out_back(seg(lt, 0.0, 0.4))
    cola(img, logo_card(480), W / 2, 760, sc=u)
    v = ease(seg(lt, 0.3, 0.7))
    linhas = [("JÁ DÁ PRA ALUGAR!", "lilita", 92, AMARELO), ("3 JOGOS = 7 DIAS DE JOGO", "figtree", 54, BRANCO),
              ("RESERVE ONLINE · RETIRE EM MAUÁ\nOU RECEBA EM CASA", "figtree", 46, BRANCO),
              ("LINK NA BIO · @SUAVEZ_BG", "lilita", 60, BRANCO)]
    for k, (txt, f, s, cor) in enumerate(linhas):
        cola(img, texto(txt, f, s, cor, TINTA, 7 if f == "lilita" else 0, 6 if f == "lilita" else 0, TINTA, entre=1.2),
             W / 2, 1080 + k * 150 + (30 if k == 3 else 0), alpha=v)


def frame(t):
    img = fundo().copy()
    em_jogo = GANCHO <= t < T_FIM
    k = min(len(JOGOS) - 1, int((t - GANCHO) / POR)) if em_jogo else -1
    if t < T_FIM:
        lt = t - GANCHO - max(k, 0) * POR
        confete(img, t, ease(seg(lt, 0.3, 0.6)) * (1 - ease(seg(lt, 2.2, 2.8))) if em_jogo else 0)
        caixa_atras(img, t)
        if em_jogo:
            jogo_sobe(img, t, k)
        caixa_frente(img, t)
    if t < GANCHO:
        cena_gancho(img, t)
    elif em_jogo:
        lt = t - GANCHO - k * POR
        sai = ease(seg(lt, POR - 0.3, POR))
        cola(img, selo_novidade(), 290, 330, rot=-10, sc=out_back(seg(lt, 0.45, 0.75)) * (1 - sai))
        textos_jogo(img, t, k)
    elif t < T_CTA:
        confete(img, t, 1.0)
        cena_fim(img, t)
    else:
        cena_cta(img, t)
    if t < T_CTA:
        img.alpha_composite(logo_card(150), (W - 186, 46))
    return img.convert("RGB")


def textos_jogo(img, t, k):
    """Nome, jogadores/tempo e frase (o selo é desenhado em frame())."""
    _arq, nome, linha, frase = JOGOS[k]
    lt = t - GANCHO - k * POR
    sai = ease(seg(lt, POR - 0.3, POR))
    a = ease(seg(lt, 0.55, 0.85)) * (1 - sai)
    tam = 70 if len(nome) < 16 else 58
    cola(img, texto(nome, "lilita", tam, BRANCO, TINTA, 7, 6, TINTA), W / 2, 1010, alpha=a)
    cola(img, texto(linha, "figtree", 42, AMARELO), W / 2, 1085, alpha=a)
    cola(img, texto(frase, "figtree", 40, BRANCO, None, 0, 3, (0, 0, 0), entre=1.22), W / 2, 1170, alpha=a)


def render_frame(fi):
    return frame(fi / FPS).tobytes()


def cues():
    c = [(0.1, "pop", 0.6), (0.5, "flip", 0.4), (1.0, "flip", 0.4), (GANCHO - 0.5, "rasga", 0.6)]
    for k in range(len(JOGOS)):
        t0 = GANCHO + k * POR
        c += [(t0 + 0.05, "whoosh", 0.45), (t0 + 0.45, "reveal", 0.55), (t0 + 0.5, "plateia", 0.25)]
    c += [(T_FIM, "reveal", 0.6)] + [(T_FIM + 0.15 + k * 0.1, "pop", 0.45) for k in range(4)] + [(T_CTA, "chime", 0.6)]
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    a = ap.parse_args()
    print(f"duração {DUR:.1f} s")
    if a.frame:
        os.makedirs(OUT, exist_ok=True)
        folha([frame(x) for x in a.frame], os.path.join(OUT, "frames_novidades.jpg"))
        return
    entrega("novidades", DUR, render_frame, cues(), "gameshow", musica_ganho=0.28)


if __name__ == "__main__":
    main()
