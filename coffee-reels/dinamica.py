#!/usr/bin/env python3
"""Vídeo explicativo da DINÂMICA "Kaizen do Café" (Coffee Rush) para o time de melhoria contínua do Erik (29/out/2026).
NÃO explica as regras (pedido dele: "eu não quero vídeo explicando a regra, eu quero vídeo explicando a dinâmica"):
a ideia, quem joga, por que o Coffee Rush (jogo × processo), a agenda, rodada 1, A3, rodada 2, comparar, padronizar,
ponte com o trabalho, no visual do kit em PDF (dinamica-kaizen/).
Sem narração, tudo escrito; peças OFICIAIS da Galápagos (recortes.py): ingredientes, barista (o vermelho é o azul
com a cor girada; no modo 2 jogadores as cores são vermelho e azul), caixa e foto dos componentes.
Regras conferidas (manual via rulespal + Board Game Arena): tabuleiro 4x4, anda 1 a 3 casas sem diagonal e pega o
ingrediente de CADA casa em que entra; 3 xícaras; pedido completo vai pro adversário (aba 1); no fim do turno tudo desce
1 aba, o que sai da aba 4 é penalidade (−1, ganha ficha de pressa) e, com 2 jogadores, entra 1 pedido novo na sua aba 1.

    python3 dinamica.py --frame 3 20 40      # out/frames.jpg
    python3 dinamica.py                      # out/dinamica_final.mp4 (+ _chat.mp4)
"""
import math
import os
import subprocess
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "listas-reels"))
sys.path.insert(0, os.path.join(REPO, "comum"))
from base import texto, fonte, final_loudness  # noqa: E402
from motor import W, H, FPS, encode, folha, ffmpeg, cola, sombra, ease, out_back  # noqa: E402
import som  # noqa: E402

A = os.path.join(ROOT, "assets")
OUT = os.path.join(ROOT, "out")
MARROM, PETROLEO, LARANJA, AMARELO, CREME = (63, 36, 18), (28, 124, 150), (244, 136, 37), (255, 199, 31), (248, 240, 226)
VERDE, VERMELHO, BRANCO = (70, 160, 90), (214, 60, 50), (250, 250, 250)
GRADE = [["gelo", "caramelo", "espuma", "cafe"], ["cafe", "leite", "agua", "cha"],
         ["cha", "chocolate", "leite", "gelo"], ["espuma", "agua", "caramelo", "chocolate"]]
BORDA = {"cafe": (120, 80, 50), "leite": (150, 150, 150), "agua": (80, 170, 220), "cha": (90, 170, 80),
         "gelo": (130, 200, 230), "caramelo": LARANJA, "chocolate": (140, 80, 50), "espuma": (200, 190, 160)}
P1, P2, P3, P4, P5 = ("cafe", "leite"), ("cha", "gelo", "agua"), ("cafe", "chocolate", "espuma"), \
    ("caramelo", "leite", "gelo"), ("cha", "leite")


# ------------------------------------------------------------------ peças
def T(txt, s, cor=MARROM, f="lilita", sw=0, contorno=None, sh=0, cs=MARROM):
    return texto(txt, f, s, cor, contorno, sw, sh, cs)


@lru_cache(None)
def ing(nome, s):
    im = Image.open(os.path.join(A, "ing", nome + ".png")).convert("RGBA")
    im.thumbnail((s, s), Image.LANCZOS)
    return im


@lru_cache(None)
def barista(cor, h):
    im = Image.open(os.path.join(A, f"barista_{cor}.png")).convert("RGBA")
    im = im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
    return sombra(im, 8, (6, 10), 0.4)


@lru_cache(None)
def caixa(h):
    im = Image.open(os.path.join(A, "caixa.png")).convert("RGBA")
    im = im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
    return sombra(im, 24, (0, 26), 0.45)


@lru_cache(None)
def componentes(w):
    im = Image.open(os.path.join(A, "componentes.png")).convert("RGBA")
    im = im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)
    return sombra(im, 20, (0, 20), 0.35)


@lru_cache(None)
def fundo():
    a = np.ones((H, W, 3)) * np.array(CREME, float)
    yy, xx = np.mgrid[0:H, 0:W]
    pont = ((xx % 54 < 5) & (yy % 54 < 5))
    a[pont] -= 10
    a *= np.clip(1.04 - 0.12 * (((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2) * 2, 0.8, 1.04)[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


@lru_cache(None)
def bloco(w, h, cor=BRANCO, borda=MARROM, bw=6, raio=26, sh=10):
    im = Image.new("RGBA", (w + sh + 4, h + sh + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((sh, sh, w - 1 + sh, h - 1 + sh), radius=raio, fill=borda)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=raio, fill=cor, outline=borda, width=bw)
    return im


@lru_cache(None)
def pilula(txt, s, cor=LARANJA, fg=BRANCO):
    t = T(txt, s, fg)
    w, h = t.width + 30, int(s * 1.55)
    im = bloco(w, h, cor, MARROM, 5, h // 2, 6).copy()
    im.alpha_composite(t, ((w - t.width) // 2, (h - t.height) // 2))
    return im


@lru_cache(None)
def casa(nome, s):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((2, 2, s - 3, s - 3), radius=18, fill=(255, 252, 244), outline=BORDA[nome], width=9)
    i = ing(nome, int(s * 0.68))
    im.alpha_composite(i, ((s - i.width) // 2, (s - i.height) // 2))
    return im


@lru_cache(None)
def pedido(rec, w=150, cor=PETROLEO, penal=False):
    h = int(w * 1.36)
    im = bloco(w, h, (250, 244, 228) if not penal else (240, 210, 205), MARROM, 5, 16, 6).copy()
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((4, 4, w - 5, int(h * 0.22)), radius=12, fill=cor if not penal else VERMELHO)
    t = T("PEDIDO" if not penal else "PERDIDO", int(w * 0.17), BRANCO)
    im.alpha_composite(t, ((w - t.width) // 2, int(h * 0.11) - t.height // 2 + 2))
    s = int(w * 0.42)
    pos = [(0.3, 0.45), (0.7, 0.45), (0.5, 0.75)] if len(rec) == 3 else [(0.3, 0.6), (0.7, 0.6)]
    for (fx, fy), n in zip(pos, rec):
        i = ing(n, s)
        im.alpha_composite(i, (int(fx * w - i.width / 2), int(fy * h - i.height / 2)))
    if penal:
        t = T("−1", int(w * 0.38), VERMELHO, sw=4, contorno=BRANCO)
        im.alpha_composite(t, ((w - t.width) // 2, int(h * 0.62) - t.height // 2))
    return im


@lru_cache(None)
def xicara(conteudo=(), s=150):
    im = Image.new("RGBA", (s + 40, s + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((s - 10, s * 0.28, s + 34, s * 0.72), outline=(190, 205, 210), width=10)  # asa
    d.ellipse((4, 4, s - 4, s - 4), fill=(236, 246, 248), outline=(170, 190, 196), width=8)
    d.ellipse((s * 0.16, s * 0.16, s * 0.84, s * 0.84), outline=(210, 226, 230), width=4)
    k = len(conteudo)
    for j, n in enumerate(conteudo):
        a = 2 * math.pi * j / max(1, k) - math.pi / 2
        r = 0 if k == 1 else s * 0.17
        i = ing(n, int(s * 0.36))
        im.alpha_composite(i, (int(s / 2 + r * math.cos(a) - i.width / 2), int(s / 2 + r * math.sin(a) - i.height / 2)))
    return im


@lru_cache(None)
def marca(ok, s, cor=None):
    """✓ ou ✗ desenhados (as fontes não têm esses símbolos)."""
    cor = cor or ((40, 140, 70) if ok else VERMELHO)
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    w = max(4, s // 7)
    if ok:
        d.line([(s * 0.12, s * 0.55), (s * 0.4, s * 0.82), (s * 0.88, s * 0.2)], fill=cor, width=w, joint="curve")
    else:
        d.line([(s * 0.18, s * 0.18), (s * 0.82, s * 0.82)], fill=cor, width=w)
        d.line([(s * 0.82, s * 0.18), (s * 0.18, s * 0.82)], fill=cor, width=w)
    return im


def surge(t, t0, d=0.35):
    """(alpha, escala) de um elemento que entra com pulinho em t0."""
    if t < t0:
        return 0.0, 0.0
    u = min(1.0, (t - t0) / d)
    return min(1.0, u * 2), out_back(u)


def poe(img, im, x, y, t, t0, rot=0, d=0.35):
    a, s = surge(t, t0, d)
    cola(img, im, x, y, rot, s, a)


def cabecalho(img, n, nome, t):
    poe(img, pilula(f"{n} · {nome}" if n else nome, 40, LARANJA), W / 2, 150, t, 0.0)


# ------------------------------------------------------------------ cenas (cada uma recebe img e o tempo local)
def c_gancho(img, t):
    poe(img, T("KAIZEN\nDO CAFÉ", 150, AMARELO, sw=10, contorno=MARROM, sh=12), W / 2, 380, t, 0.1, -3)
    poe(img, T("uma dinâmica de melhoria contínua\ncom o jogo Coffee Rush", 46, MARROM, "figtree"), W / 2, 640, t, 0.6)
    a, s = surge(t, 0.3, 0.6)
    cola(img, caixa(720), W / 2, 1180 - 6 * math.sin(t * 2), 4 * math.sin(t * 1.3), s * (1 + 0.01 * t), a)


def c_ideia(img, t):
    cabecalho(img, 1, "A IDEIA", t)
    poe(img, T("O time sente a dor\ndo problema JOGANDO", 70), W / 2, 330, t, 0.2)
    passos = [("JOGA", "rodada 1", PETROLEO), ("MEDE", "ficha", LARANJA), ("A3", "causa e plano", VERMELHO),
              ("JOGA DE NOVO", "rodada 2", PETROLEO), ("COMPARA", "e padroniza", VERDE)]
    for k, (a_, b, c) in enumerate(passos):
        t0 = 1.0 + k * 0.8
        y = 560 + k * 200
        im = bloco(720, 160, BRANCO).copy()
        im.alpha_composite(pilula(str(k + 1), 56, c), (24, 28))
        tt = T(a_, 56, c)
        im.alpha_composite(tt, (150, 80 - tt.height // 2 - 6))
        tb = T(b, 32, (120, 96, 80), "figtree")
        im.alpha_composite(tb, (720 - tb.width - 30, 80 - tb.height // 2))
        poe(img, im, W / 2 + (k % 2 - 0.5) * 30, y, t, t0, (k % 2 - 0.5) * 2)
        if k < 4:
            poe(img, T("↓", 50, MARROM, "figtree"), W / 2, y + 100, t, t0 + 0.4)
    poe(img, T("= o PDCA na prática", 54, MARROM, "figtree"), W / 2, 1560, t, 5.4)


def c_quem(img, t):
    cabecalho(img, 2, "QUEM JOGA", t)
    poe(img, T("4 pessoas = 2 duplas", 76), W / 2, 330, t, 0.2)
    for k, (cor, nome, cx) in enumerate((("azul", "DUPLA A", 290), ("vermelho", "DUPLA B", 790))):
        t0 = 0.8 + k * 0.6
        poe(img, bloco(440, 520, BRANCO), cx, 760, t, t0)
        poe(img, T(nome, 56, PETROLEO if k == 0 else VERMELHO), cx, 560, t, t0 + 0.1)
        poe(img, barista(cor, 300), cx - 80, 790, t, t0 + 0.3, -4)
        poe(img, barista(cor, 300), cx + 80, 790, t, t0 + 0.45, 4)
        poe(img, T("2 pessoas · 2 baristas", 34, MARROM, "figtree"), cx, 980, t, t0 + 0.5)
    poe(img, T("Cada dupla é UM jogador\nno modo de 2 jogadores", 56), W / 2, 1180, t, 2.6)
    poe(img, T("Você é o facilitador:\ncronometra, conta os turnos e faz as perguntas.", 40, (110, 86, 70), "figtree"),
        W / 2, 1420, t, 3.8)


# ---------- o jogo é um processo
MAPA = [("4 abas", "prazo do cliente (lead time)"), ("saiu da aba 4", "cliente perdido / atraso"),
        ("3 xícaras", "capacidade (WIP)"), ("ingrediente errado", "retrabalho / desperdício"),
        ("pedidos do outro time", "pico de demanda"), ("1 barista por turno", "gargalo + decisão em equipe"),
        ("melhorias", "kaizen: investe agora, ganha depois")]


def c_processo(img, t):
    cabecalho(img, 3, "POR QUE O COFFEE RUSH", t)
    poe(img, T("A cafeteria do jogo\nfunciona como um processo", 64), W / 2, 330, t, 0.2)
    for k, (a_, b) in enumerate(MAPA):
        t0 = 1.0 + k * 0.75
        y = 560 + k * 148
        im = bloco(940, 124, BRANCO, raio=20, sh=7).copy()
        ta = T(a_, 40, PETROLEO)
        im.alpha_composite(ta, (28, 58 - ta.height // 2))
        tb = T(b, 34, MARROM, "figtree")
        im.alpha_composite(tb, (930 - tb.width - 24, 58 - tb.height // 2))
        poe(img, im, W / 2, y, t, t0)


# ---------- a sexta-feira
AGENDA = [("Abertura + treino", 10, (150, 130, 110)), ("Rodada 1", 15, PETROLEO), ("A3", 30, VERMELHO),
          ("Rodada 2", 15, PETROLEO), ("Comparar e padronizar", 15, VERDE), ("Ponte com o trabalho", 5, LARANJA)]


def c_agenda(img, t):
    cabecalho(img, 4, "A AGENDA", t)
    poe(img, T("uns 90 minutos", 90), W / 2, 330, t, 0.2)
    y = 520
    tot = 0
    for k, (nome, m, c) in enumerate(AGENDA):
        t0 = 0.8 + k * 0.6
        h = 60 + m * 7
        im = bloco(860, h, c, MARROM, 5, 18, 7).copy()
        tn = T(nome, 42, BRANCO)
        im.alpha_composite(tn, (30, h // 2 - tn.height // 2 - 2))
        tm = T(f"{m} min", 40, BRANCO)
        im.alpha_composite(tm, (830 - tm.width, h // 2 - tm.height // 2 - 2))
        poe(img, im, W / 2, y + h / 2, t, t0)
        hh = f"0:{tot:02d}" if tot < 60 else f"1:{tot - 60:02d}"
        poe(img, T(hh, 30, (120, 96, 80), "figtree"), 70, y + 20, t, t0)
        y += h + 18
        tot += m


def c_rodada1(img, t):
    cabecalho(img, 5, "RODADA 1", t)
    poe(img, T("Medir a\ncondição atual", 80), W / 2, 360, t, 0.2)
    itens = [("12 turnos por dupla", "jogo do zero, mesmo limite nas 2 rodadas"),
             ("Sem dicas", "deixe o caos acontecer"),
             ("Quem não mexe o barista anota", "a ficha de medição, turno a turno")]
    for k, (a_, b) in enumerate(itens):
        im = bloco(900, 160, BRANCO).copy()
        ta = T(a_, 46, PETROLEO)
        im.alpha_composite(ta, (36, 52 - ta.height // 2))
        tb = T(b, 34, (110, 86, 70), "figtree")
        im.alpha_composite(tb, (36, 116 - tb.height // 2))
        poe(img, im, W / 2, 620 + k * 190, t, 0.9 + k * 0.6)
    # mini ficha preenchendo
    cols = ["entregues", "perdidos", "retrabalho", "na aba 4"]
    a, s = surge(t, 2.8)
    ficha = bloco(900, 330, (255, 252, 244), raio=18).copy()
    d = ImageDraw.Draw(ficha)
    for j, cname in enumerate(cols):
        tc = T(cname, 28, BRANCO, "figtree")
        d.rectangle((120 + j * 190, 16, 120 + j * 190 + 180, 60), fill=MARROM)
        ficha.alpha_composite(tc, (int(210 + j * 190 - tc.width / 2), 38 - tc.height // 2))
    vals = [[1, 0, 0, 1], [0, 0, 1, 2], [1, 1, 0, 1], [2, 0, 0, 0]]
    for i in range(4):
        tt = T(f"turno {i + 1}", 26, MARROM, "figtree")
        ficha.alpha_composite(tt, (20, 88 + i * 60 - tt.height // 2))
        for j in range(4):
            if t > 3.4 + i * 0.5 + j * 0.1:
                tv = T(str(vals[i][j]), 34, VERMELHO if j == 1 and vals[i][j] else MARROM, "figtree")
                ficha.alpha_composite(tv, (int(210 + j * 190 - tv.width / 2), 88 + i * 60 - tv.height // 2))
    cola(img, ficha, W / 2, 1340, 0, s, a)


def c_a3(img, t):
    cabecalho(img, 6, "O A3 EM DUPLA (30 MIN)", t)
    passos = [("Condição atual", "os números da ficha: onde doeu e quando começou"),
              ("Meta", "uma só, com número: ex. no máx. 1 cliente perdido"),
              ("5 porquês", "do maior problema até algo que a dupla controla"),
              ("Contramedidas", "no máx. 3, só de MÉTODO: quem faz o quê")]
    for k, (a_, b) in enumerate(passos):
        im = bloco(940, 150, BRANCO).copy()
        im.alpha_composite(pilula(str(k + 1), 44, VERMELHO), (22, 30))
        ta = T(a_, 46, MARROM)
        im.alpha_composite(ta, (120, 48 - ta.height // 2))
        tb = T(b, 30, (110, 86, 70), "figtree")
        im.alpha_composite(tb, (120, 108 - tb.height // 2))
        poe(img, im, W / 2, 330 + k * 175, t, 0.4 + k * 0.6)
    # exemplo dos porquês
    poe(img, pilula("EXEMPLO", 30, PETROLEO), W / 2, 1050, t, 3.2)
    porques = ["Perdemos 3 clientes", "por quê? pedidos ficaram na aba 4",
               "por quê? a gente pegava ingrediente do pedido novo", "por quê? cada um olhava um pedido diferente",
               "causa: não tinha critério de prioridade"]
    for k, p in enumerate(porques):
        cor = VERMELHO if k == len(porques) - 1 else MARROM
        poe(img, T(p, 36 if k else 40, cor, "figtree" if k else "lilita"), W / 2, 1130 + k * 66, t, 3.6 + k * 0.9)


def c_regra(img, t):
    cabecalho(img, 6, "O A3 EM DUPLA (30 MIN)", t)
    poe(img, T("A regra de ouro:", 70), W / 2, 330, t, 0.2)
    poe(img, T("Muda o MÉTODO,\nnão a regra do jogo.", 84, PETROLEO), W / 2, 520, t, 0.6)
    nao = ["andar 4 casas", "pegar 2 pedidos"]
    sim = ["atender primeiro o pedido\nmais perto da aba 4", "1 xícara por pedido", "um olha o balcão,\no outro o tabuleiro",
           "conferir antes de entregar"]
    for k, n in enumerate(nao):
        tn = T(n, 44, VERMELHO, "figtree")
        im = Image.new("RGBA", (tn.width + 80, max(tn.height, 64)), (0, 0, 0, 0))
        im.alpha_composite(marca(False, 56), (0, (im.height - 56) // 2))
        im.alpha_composite(tn, (76, (im.height - tn.height) // 2))
        poe(img, im, W / 2, 760 + k * 70, t, 1.6 + k * 0.4)
    for k, s in enumerate(sim):
        im = bloco(820, 130, (232, 244, 232), VERDE, 5, 20, 6).copy()
        ts = T(s, 36, (40, 110, 60), "figtree")
        im.alpha_composite(marca(True, 64), (30, 33))
        im.alpha_composite(ts, (110, 65 - ts.height // 2))
        poe(img, im, W / 2, 960 + k * 150, t, 2.8 + k * 0.6)
    poe(img, T("exemplos de contramedidas", 32, (120, 96, 80), "figtree"), W / 2, 1560, t, 3.0)


def c_rodada2(img, t):
    cabecalho(img, 7, "RODADA 2", t)
    poe(img, T("Testar o plano", 84), W / 2, 330, t, 0.2)
    itens = [("Jogo novo, do zero", "mesmos 12 turnos e a mesma ficha"),
             ("Cada dupla segue o próprio A3", "o plano está no papel, não na memória"),
             ("Você observa", "anote quando alguém esquece o combinado:\nisso também é dado")]
    for k, (a_, b) in enumerate(itens):
        im = bloco(920, 200, BRANCO).copy()
        ta = T(a_, 46, PETROLEO)
        im.alpha_composite(ta, (36, 56 - ta.height // 2))
        tb = T(b, 34, (110, 86, 70), "figtree")
        im.alpha_composite(tb, (36, 136 - tb.height // 2))
        poe(img, im, W / 2, 620 + k * 240, t, 0.8 + k * 0.7)
    poe(img, barista("azul", 220), W / 2 - 160, 1430, t, 2.6, -6)
    poe(img, barista("vermelho", 220), W / 2 + 160, 1430, t, 2.8, 6)


def c_compara(img, t):
    cabecalho(img, 8, "COMPARAR E PADRONIZAR", t)
    poe(img, T("Rodada 1 × Rodada 2", 72), W / 2, 320, t, 0.2)
    poe(img, pilula("EXEMPLO", 30, PETROLEO), W / 2, 430, t, 0.4)
    barras = [("Clientes perdidos", 4, 1, VERMELHO), ("Pedidos entregues", 5, 8, VERDE)]
    for k, (nome, r1, r2, c) in enumerate(barras):
        cx = W / 2 + (k - 0.5) * 460
        poe(img, T(nome, 38, MARROM), cx, 1090, t, 0.6)
        for j, (v, lab) in enumerate(((r1, "R1"), (r2, "R2"))):
            q = ease(min(1, max(0, (t - 1.0 - j * 0.6) / 0.8)))
            h = int(v * 48 * q) + 2
            x = cx + (j - 0.5) * 170
            d = ImageDraw.Draw(img)
            d.rounded_rectangle((x - 60, 1000 - h, x + 60, 1000), radius=12, fill=c if j else tuple(int(a * 0.6 + 100)
                                                                                                    for a in c),
                                outline=MARROM, width=5)
            if q > 0.9:
                cola(img, T(str(v), 48, MARROM), x, 1000 - h - 40)
            cola(img, T(lab, 34, MARROM, "figtree"), x, 1022)
    poe(img, T("Bateu a meta? O que mais ajudou?\nFoi MÉTODO ou foi SORTE das cartas?", 44, MARROM, "figtree"),
        W / 2, 1220, t, 2.8)
    poe(img, pilula("CADA DUPLA ESCOLHE 1 REGRA DE OURO", 36, VERDE), W / 2, 1400, t, 4.0)
    poe(img, T("= o procedimento padrão da cafeteria", 40, (110, 86, 70), "figtree"), W / 2, 1520, t, 4.6)


def c_ponte(img, t):
    cabecalho(img, 9, "PONTE COM O TRABALHO", t)
    poe(img, T("E no nosso dia a dia?", 78), W / 2, 340, t, 0.2)
    perg = ["Onde tem pedido parado\nna aba 4?", "O que a gente faz hoje\nsem medir?",
            "Qual foi o 5º porquê\ne onde ele aparece aqui?"]
    for k, p in enumerate(perg):
        im = bloco(880, 210, BRANCO).copy()
        tp = T(p, 50, PETROLEO)
        im.alpha_composite(tp, ((880 - tp.width) // 2, 105 - tp.height // 2))
        poe(img, im, W / 2, 620 + k * 250, t, 0.8 + k * 0.9, (k - 1) * 1.5)
    poe(img, pilula("FECHA: 1 PROBLEMA REAL PARA UM A3 DE VERDADE", 32, LARANJA), W / 2, 1440, t, 3.8)


def c_fim(img, t):
    poe(img, T("KAIZEN\nDO CAFÉ", 130, AMARELO, sw=9, contorno=MARROM, sh=10), W / 2, 380, t, 0.1)
    a, s = surge(t, 0.3, 0.5)
    cola(img, caixa(560), W / 2, 960, 3, s, a)
    poe(img, T("No kit em PDF:\nroteiro, regras em 1 página, ficha e A3", 44, MARROM, "figtree"), W / 2, 1420, t, 1.0)


CENAS = [(c_gancho, 4.5), (c_ideia, 7.5), (c_quem, 6.5), (c_processo, 9.0), (c_agenda, 6.5), (c_rodada1, 7.5),
         (c_a3, 9.5), (c_regra, 7.0), (c_rodada2, 6.0), (c_compara, 7.5), (c_ponte, 7.0), (c_fim, 4.5)]
INI = np.cumsum([0] + [d for _, d in CENAS])
DUR = float(INI[-1])
TRANS = 0.35


def quadro(t):
    img = fundo().copy()
    k = int(np.searchsorted(INI, t, side="right") - 1)
    k = min(k, len(CENAS) - 1)
    f, d = CENAS[k]
    u = t - INI[k]
    f(img, u)
    # transição: a cena desliza para a esquerda no fim
    if k < len(CENAS) - 1 and u > d - TRANS:
        q = ease((u - (d - TRANS)) / TRANS)
        base = fundo().copy()
        base.alpha_composite(img, (int(-q * W * 0.25), 0))
        img = Image.blend(base, fundo(), q * 0.9)
    elif k > 0 and u < 0.2:
        img = Image.blend(fundo(), img, u / 0.2)
    return img.convert("RGB")


def render(fi):
    return quadro(fi / FPS).tobytes()


def cues():
    c = []
    for k, (f, d) in enumerate(CENAS):
        c.append((INI[k] + 0.02, "whoosh", 0.35))
        c.append((INI[k] + 0.25, "pop", 0.45))
    t0 = INI[[f for f, _ in CENAS].index(c_compara)]
    c += [(t0 + 4.0, "ding", 0.6)]
    return c


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:]]
        folha([quadro(t) for t in ts], os.path.join(OUT, "frames.jpg"))
        print("ok frames", DUR)
        return
    print("duração", DUR)
    wav = os.path.join(OUT, "dinamica.wav")
    som.build(wav, DUR, cues(), musica="travessa", fx_ganho=0.5, musica_ganho=0.22)
    mp4 = os.path.join(OUT, "dinamica.mp4")
    encode(mp4, render, list(range(int(DUR * FPS))), wav)
    fin = os.path.join(OUT, "dinamica_final.mp4")
    final_loudness(mp4, fin)
    chat = os.path.join(OUT, "dinamica_chat.mp4")
    kbps = int(27 * 8 * 1024 / DUR) - 200
    base = [ffmpeg(), "-y", "-loglevel", "error", "-i", fin, "-c:v", "libx264", "-preset", "slow", "-tune", "animation",
            "-b:v", f"{kbps}k"]
    log = os.path.join(OUT, "pass")
    subprocess.run(base + ["-pass", "1", "-passlogfile", log, "-an", "-f", "null", "/dev/null"], check=True)
    subprocess.run(base + ["-pass", "2", "-passlogfile", log, "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
                           chat], check=True)
    print("ok:", chat, os.path.getsize(chat) // 1024 ** 2, "MB")


if __name__ == "__main__":
    main()
