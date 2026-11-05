#!/usr/bin/env python3
"""Reels da TARDE DE JOGOS NO BECA’S CAFÉ (3/nov/2026, pedido dele: "faz também um Reels para divulgar o evento").
Mesmo visual das artes (`promo/tarde_becas.py`): creme quente com confete claro e os GUARDA-CHUVINHOS coloridos do
teto do Becas pendurados no alto, agora BALANÇANDO (caem no gancho e ficam num vaivém). Sem narração (texto na tela),
~30 s; entrega _com_trilha e _para_musica (−15,5 LUFS). Data ainda não definida → "DATA EM BREVE".
Fatos: sábado à tarde (o horário só entra quando a data fechar), R$ 30 com R$ 15 de consumação no café, a Sua Vez
ensina os jogos mesa por mesa, reserva pelo WhatsApp (11) 97793-3910 ou chega no dia se tiver mesa livre.
Sem número de vagas (pedido dele).

    /usr/bin/python3 tarde.py --frame 1 4 9 15 20 26 30   # out/frames.jpg
    /usr/bin/python3 tarde.py                             # out/becas_{com_trilha,para_musica}_final.mp4
"""
import math
import os
import random
import sys
from functools import lru_cache

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
for p in ("assinatura-reels", "listas-reels", "comum", "promo"):
    sys.path.insert(0, os.path.join(REPO, p))
import estilo as E  # noqa: E402
import base  # noqa: E402
from base import entrega  # noqa: E402
from motor import FPS, folha, ease, out_back  # noqa: E402
import tarde_becas as TB  # noqa: E402

W, H = 1080, 1920
OUT = os.path.join(ROOT, "out")
MAR, PET, LAR, AMA, BR, ROSA = E.MARROM, E.PETROLEO, E.LARANJA, E.AMARELO, E.BRANCO, TB.ROSA
VERDE = (118, 176, 65)
# guarda-chuvas: (x, comprimento do fio, largura, cor, fase); o canto de cima à direita fica para o logo
CHUVAS = [(95, 150, 150, LAR, 0.0), (265, 250, 135, PET, 1.3), (430, 135, 150, AMA, 2.1), (590, 230, 140, ROSA, 0.6),
          (750, 160, 145, VERDE, 2.8), (905, 290, 120, LAR, 1.9)]

DUR_GANCHO, DUR_COMO, DUR_JOGOS, DUR_PRECO, DUR_QUEM, DUR_CTA = 4.0, 6.0, 5.6, 4.6, 3.8, 6.4


# ---------------------------------------------------------------- peças
@lru_cache(None)
def fundo():
    img = Image.new("RGBA", (W, H), TB.CREME + (255,))
    d = ImageDraw.Draw(img)
    rnd = random.Random(7)
    for _ in range(220):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(3, 6)
        c = (LAR, PET, AMA, ROSA)[rnd.randrange(4)]
        c = tuple(int(v + (255 - v) * 0.7) for v in c)
        d.ellipse((x - r, y - r, x + r, y + r), fill=c)
    return img


@lru_cache(None)
def chuva(k):
    x, L, w, cor, _ = CHUVAS[k]
    return TB.guarda_chuva(w, cor, k)


@lru_cache(None)
def chuva_rot(k, ang10):
    return chuva(k).rotate(ang10 / 10, expand=True, resample=Image.BICUBIC)


def guarda_chuvas(img, t):
    """Pendurados num fio desde o topo. Caem no começo (com quique) e depois balançam como pêndulo."""
    d = ImageDraw.Draw(img)
    for k, (x, L, w, cor, fase) in enumerate(CHUVAS):
        t0 = 0.08 * k
        u = max(0.0, t - t0)
        queda = min(1.0, u / 0.55)
        Lq = L * out_back(queda, 1.3) if queda < 1 else L
        amort = 1 + 5 * math.exp(-u * 1.6)  # balanço forte ao cair, depois suave
        ang = 3.2 * amort * math.sin(2 * math.pi * u / (1.9 + 0.15 * k) + fase)  # graus
        a = math.radians(ang)
        px, py = x + Lq * math.sin(a), Lq * math.cos(a)
        d.line([(x, -5), (px, py)], fill=(150, 120, 100), width=3)
        g = chuva_rot(k, int(round(-ang * 10)))
        # o topo do guarda-chuva (ponta) fica no fim do fio: o centro está a h/2 abaixo, girado junto
        h2 = chuva(k).height / 2 - 6
        cx, cy = px + h2 * math.sin(a), py + h2 * math.cos(a)
        img.alpha_composite(g, (int(cx - g.width / 2), int(cy - g.height / 2)))


@lru_cache(None)
def titulo(txt, s, cor=LAR):
    return E.titulo(txt, s, cor, larg_max=980)


@lru_cache(None)
def logo(w):
    return E.logo(w)


@lru_cache(None)
def parc(h):
    return TB.parceria(h)


@lru_cache(None)
def caixa(nome, h):
    return TB.caixa(nome, h)


@lru_cache(None)
def card_info():
    return TB.card_info(920)


@lru_cache(None)
def inscricao():
    return TB.inscricao(920)


def surge(t, t0, d=0.35):
    if t < t0:
        return 0.0, 0.0
    u = min(1.0, (t - t0) / d)
    return min(1.0, u * 2), out_back(u)


def poe(img, im, x, y, t, t0, rot=0.0, d=0.35):
    a, s = surge(t, t0, d)
    E.cola(img, im, x, y, rot, s, a)


@lru_cache(None)
def passo(n, txt, cor):
    """Cartão de passo: número num círculo + texto."""
    c = E.bloco(860, 190, BR, raio=30, ow=6, sombra=10).copy()
    d = ImageDraw.Draw(c)
    d.ellipse((30, 35, 150, 155), fill=cor, outline=MAR, width=6)
    d.text((90, 97), str(n), font=E.lilita(78), fill=BR, anchor="mm", stroke_width=3, stroke_fill=MAR)
    linhas = txt.split("\n")
    for j, l in enumerate(linhas):
        y = 95 + (j - (len(linhas) - 1) / 2) * 52
        d.text((185, y), l, font=E.fig(44 if j == 0 else 36, 900 if j == 0 else 700),
               fill=MAR if j == 0 else PET, anchor="lm")
    return c


# ---------------------------------------------------------------- cenas (tudo entre y 380 e 1580)
def c_gancho(img, t):
    poe(img, parc(120), W / 2, 520, t, 0.5)
    poe(img, titulo("BORA JOGAR\nNUM CAFÉ?", 150, LAR), W / 2, 790, t, 0.05, -3)
    poe(img, titulo("TARDE\nDE JOGOS", 140, PET), W / 2, 1180, t, 1.3, 2)
    poe(img, TB.selo_data(44), W / 2, 1400, t, 2.2, 2)
    poe(img, TB.selo_endereco(34), W / 2, 1490, t, 2.6, -1)


def c_como(img, t):
    poe(img, titulo("COMO FUNCIONA?", 116, LAR), W / 2, 480, t, 0.05, -2)
    itens = [("CHEGA E ESCOLHE A MESA", "sozinho, em dupla ou com a galera", LAR),
             ("A GENTE ENSINA O JOGO", "mesa por mesa, sem manual", PET),
             ("É SÓ JOGAR A TARDE TODA", "e pedir aquele café", ROSA)]
    for k, (a, b, cor) in enumerate(itens):
        poe(img, passo(k + 1, a + "\n" + b, cor), W / 2 + (k - 1) * 14, 760 + k * 255, t, 0.6 + k * 1.1,
            (-1.5, 1.2, -1)[k])
    poe(img, E.texto("Nunca jogou nada além de UNO? Perfeito!", 40, MAR, 800), W / 2, 1530, t, 4.2)


def c_jogos(img, t):
    poe(img, titulo("JOGOS RÁPIDOS\nE DIVERTIDOS", 112, LAR), W / 2, 520, t, 0.05, 2)
    for k, n in enumerate(TB.JOGOS):
        col, lin = k % 3, k // 3
        x = W / 2 + (col - 1) * 320
        y = 900 + lin * 380
        poe(img, caixa(n, 300), x, y, t, 0.6 + k * 0.32, (col - 1) * 4 + (lin * 2 - 1) * 1.5, d=0.4)
    poe(img, E.pilula("E MUITO MAIS!", 46, AMA, MAR, fonte_titulo=True), W / 2, 1520, t, 3.0, -2)


def c_preco(img, t):
    poe(img, titulo("QUANTO\nCUSTA?", 130, LAR), W / 2, 560, t, 0.05, -2)
    poe(img, card_info(), W / 2, 1000, t, 0.7, 0)
    poe(img, E.pilula("METADE VOCÊ GASTA NO CAFÉ!", 40, PET, BR), W / 2, 1300, t, 1.9, -1.5)


def c_quem(img, t):
    poe(img, titulo("TRAZ QUEM\nVOCÊ QUISER", 120, LAR), W / 2, 560, t, 0.05, 2)
    for k, (s, cor, fg) in enumerate((("O AMOR", ROSA, BR), ("A FAMÍLIA", PET, BR), ("OS AMIGOS", AMA, MAR),
                                      ("OU VEM SOZINHO!", LAR, BR))):
        poe(img, E.pilula(s, 58, cor, fg, fonte_titulo=True), W / 2 + (-1) ** k * 90, 860 + k * 160, t,
            0.6 + k * 0.45, (-1) ** k * 3)
    poe(img, E.texto("Marca aqui quem vai com você!", 44, MAR, 800), W / 2, 1520, t, 2.6)


def c_cta(img, t):
    poe(img, parc(150), W / 2, 470, t, 0.05)
    poe(img, titulo("TARDE DE JOGOS\nNO BECA’S CAFÉ", 104, LAR), W / 2, 740, t, 0.35, -2)
    poe(img, TB.selo_data(44), W / 2, 905, t, 0.8, 2)
    poe(img, TB.selo_endereco(34), W / 2, 990, t, 1.0, -1)
    poe(img, inscricao(), W / 2, 1190, t, 1.2, 0)
    poe(img, E.texto("Comenta aqui: qual jogo\nvocê quer aprender?", 42, MAR, 800), W / 2, 1480, t, 2.2)


CENAS = [(c_gancho, DUR_GANCHO), (c_como, DUR_COMO), (c_jogos, DUR_JOGOS), (c_preco, DUR_PRECO),
         (c_quem, DUR_QUEM), (c_cta, DUR_CTA)]
INI = [0.0]
for _, d_ in CENAS:
    INI.append(INI[-1] + d_)
DUR = INI[-1]
TRANS = 0.3


def quadro(t):
    k = max(i for i in range(len(CENAS)) if INI[i] <= t) if t < DUR else len(CENAS) - 1
    f, d = CENAS[k]
    u = t - INI[k]
    img = fundo().copy()
    cena = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f(cena, u)
    if k < len(CENAS) - 1 and u > d - TRANS:  # sai para a esquerda
        q = ease((u - (d - TRANS)) / TRANS)
        img.alpha_composite(cena, (int(-q * W), 0))
    elif k > 0 and u < TRANS:  # entra pela direita
        q = ease(u / TRANS)
        img.alpha_composite(cena, (int((1 - q) * W), 0))
    else:
        img.alpha_composite(cena)
    guarda_chuvas(img, t)  # por cima de tudo, o vídeo inteiro
    if f is not c_cta:
        img.alpha_composite(logo(150), (W - 180, 40))
    return img.convert("RGB")


def render(fi):
    return quadro(fi / FPS).tobytes()


def cues():
    c = [(INI[k] + 0.02, "whoosh", 0.35) for k in range(1, len(CENAS))]
    c += [(0.08 * k + 0.4, "boing", 0.25) for k in range(len(CHUVAS))]
    c += [(0.1, "pop", 0.5), (0.55, "pop", 0.4), (1.35, "pop", 0.5), (2.25, "ding", 0.45)]
    c += [(INI[1] + 0.6 + k * 1.1, "pop", 0.45) for k in range(3)]
    c += [(INI[2] + 0.6 + k * 0.32, "pop", 0.35) for k in range(6)]
    c += [(INI[2] + 3.0, "brilho", 0.45)]
    c += [(INI[3] + 0.7, "reveal", 0.5)]
    c += [(INI[4] + 0.6 + k * 0.45, "pop", 0.4) for k in range(4)]
    c += [(INI[5] + 0.8, "ding", 0.55)]
    return c


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:]]
        folha([quadro(x) for x in ts], os.path.join(OUT, "frames.jpg"))
        print("ok", DUR)
        return
    print("duração", DUR)
    base.OUT = OUT
    entrega("becas", DUR, render, cues(), "travessa", musica_ganho=0.26)


if __name__ == "__main__":
    main()
