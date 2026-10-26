#!/usr/bin/env python3
"""Reels "COMO SE JOGA TACO GATO CABRA QUEIJO PIZZA" em DESENHO DE LÁPIS DE COR (pedido dele em 26/out/2026, com a
referência do elefante × gato rabiscados). Tudo desenhado a partir das cartas OFICIAIS da PaperGames (lapis.py): papel
creme, contorno preto tremido, hachura de lápis, letra à mão, setinhas. O desenho "treme" 12 vezes por segundo (boil:
3 versões de cada desenho, trocando a cada 2 quadros a 24 fps), como animação feita à mão.

Cenas (roteiro de 9 falas aprovado, na ordem de uma partida):
 1 gancho (as 5 palavras se escrevendo, cada uma com a sua carta) · 2 preparação (baralho distribuído em 4 montes
 virados) · 3 a vez (as cartas caem no monte e cada jogador fala a próxima palavra) · 4 bateu! (GATO + carta do gato:
 4 mãos batendo, a última leva a pilha) · 5 especiais (gorila / narval / marmota com o gesto) · 6 capivara (carta + o gesto
 oficial) · 7 erros (a pilha é sua) · 8 vitória + "comenta" · 9 tela final (caixa oficial em lápis).

    python3 taco.py --frame 2 9 16 ...   # out/frames_taco.jpg
    python3 taco.py                      # out/taco_previa.mp4 (sem voz, legenda do roteiro)
"""
import argparse
import math
import os
import sys
from functools import lru_cache

import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "comum"))
import motor  # noqa: E402
from motor import seg, ease, out_back, logo_card, folha  # noqa: E402
import som  # noqa: E402
from lapis import carta, desenho, lapis, fonte, rabisco, contornos, PAPEL, GRAFITE  # noqa: E402

W, H, FPS = 1080, 1920, 24
motor.FPS = FPS  # o encode do motor usa o FPS do módulo
ASSETS = os.path.join(ROOT, "assets")
OUT = os.path.join(ROOT, "out")
VERMELHO, AZUL, VERDE = (200, 52, 40), (40, 90, 170), (40, 140, 80)
CARTAS = {"gorila": "frente_11.png", "taco": "frente_15.png", "gato": "frente_16.png", "narval": "frente_25.png",
          "cabra": "frente_28.png", "queijo": "frente_39.png", "marmota": "frente_49.png", "pizza": "frente_56.png",
          "capivara": "capivara.png"}
PALAVRAS = ["taco", "gato", "cabra", "queijo", "pizza"]
# roteiro (falas) e duração de cada cena na prévia; com a narração, cada cena estica/encolhe para caber a fala
ROTEIRO = [
    "Esse jogo tem só 5 palavras... e mesmo assim todo mundo erra!",
    "Embaralha e divide todas as cartas. Cada um fica com seu monte virado pra baixo, sem olhar.",
    "Na sua vez, você vira uma carta no meio e fala a próxima palavra: taco, gato, cabra, queijo, pizza... e começa de novo.",
    "Se a carta for igual à palavra que você falou, todo mundo bate a mão no monte! O último a bater leva a pilha inteira.",
    "Tem as especiais! Gorila: bate no peito. Narval: faz um chifre com as mãos. Marmota: bate as duas mãos na mesa. E só depois bate no monte.",
    "E a nossa caixa ainda tem a Capivara: dois dedinhos na boca, imitando os dentes!",
    "Errou o gesto? Bateu sem precisar? Hesitou? A pilha é sua!",
    "Ganha quem acabar as cartas e for o primeiro a bater na próxima. Comenta aqui: qual palavra você sempre erra?",
    "Taco Gato Cabra Queijo Pizza, de 2 a 8 jogadores. Aluga na Sua Vez, o link tá na bio!",
]
DURS = [5.2, 6.4, 9.0, 8.0, 10.5, 5.8, 6.2, 7.8, 6.0]
INICIO = [sum(DURS[:k]) for k in range(len(DURS))]
DUR = sum(DURS)
CENTRO = (540, 1000)
# os 4 jogadores em volta do monte (montes virados) e de onde vem a mão de cada um
LUGARES = [(220, 1330), (860, 1330), (860, 640), (220, 640)]


def semente(t):
    return int(t * FPS) // 2 % 3  # 12 desenhos por segundo, 3 versões que se revezam


# ---------------------------------------------------------------- sprites em lápis (cache por processo)
@lru_cache(None)
def spr_carta(nome, w, s):
    return carta(CARTAS[nome], w, nome.upper(), s)


@lru_cache(None)
def spr_verso(w, s):
    im = Image.open(os.path.join(ASSETS, "cartas", "verso.png")).convert("RGBA")
    out = lapis(im, w, s + 40)
    d = ImageDraw.Draw(out)
    rng = np.random.default_rng(s + 41)
    a = np.asarray(out.getchannel("A")) > 128
    for c in contornos(a, passo=5, minimo=50)[:1]:
        rabisco(d, c, rng, larg=max(3, w // 120), amp=2.0 * w / 500, passadas=3)
    return out


@lru_cache(None)
def spr_arte(nome, w, s):
    """Só o bicho/comida da carta (sem o fundo colorido nem o texto), redesenhado grande em lápis."""
    im = np.asarray(Image.open(os.path.join(ASSETS, "cartas", CARTAS[nome])).convert("RGBA")).copy()
    h = im.shape[0]
    ww0 = im.shape[1]
    im = im[int(0.2 * h):int(0.8 * h), int(0.05 * ww0):int(0.95 * ww0)]  # sem o fio da borda da carta
    rgb = im[..., :3].astype(int)
    borda = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
    fundo = np.median(borda, 0)
    perto = (np.abs(rgb - fundo).sum(2) < 60).astype(np.uint8)
    hh, ww = perto.shape
    mask = np.zeros((hh + 2, ww + 2), np.uint8)
    ff = perto.copy()
    for x in range(0, ww, 8):
        for y in (0, hh - 1):
            if ff[y, x] == 1:
                cv2.floodFill(ff, mask, (x, y), 2)
    for y in range(0, hh, 8):
        for x in (0, ww - 1):
            if ff[y, x] == 1:
                cv2.floodFill(ff, mask, (x, y), 2)
    im[..., 3] = np.where(ff == 2, 0, im[..., 3])
    ys, xs = np.nonzero(im[..., 3] > 128)
    im = im[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return desenho(Image.fromarray(im), w, s + 10)


@lru_cache(None)
def spr_mao(cod, w, s, rot=0, espelho=False):
    im = Image.open(os.path.join(ASSETS, "openmoji", cod + "-pele.png")).convert("RGBA")
    im = im.crop(im.getbbox())
    if espelho:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    out = desenho(im, w, s + 20)
    return out.rotate(rot, expand=True, resample=Image.BICUBIC) if rot else out


def sem_fundo(im):
    """Tira o fundo branco (ou transparente) ligado aos cantos e corta no que sobrou."""
    a = np.asarray(im.convert("RGBA")).copy()
    claro = ((a[..., :3].astype(int).min(2) > 235) | (a[..., 3] < 40)).astype(np.uint8)
    hh, ww = claro.shape
    mask = np.zeros((hh + 2, ww + 2), np.uint8)
    for p in [(0, 0), (ww - 1, 0), (0, hh - 1), (ww - 1, hh - 1)]:
        if claro[p[1], p[0]] == 1:
            cv2.floodFill(claro, mask, p, 2)
    a[..., 3] = np.where(claro == 2, 0, a[..., 3])
    im = Image.fromarray(a)
    return im.crop(im.getbbox())


@lru_cache(None)
def spr_img(arq, w, s, linha_lim=100, fino=False, bordas=False, traco=1.0):
    return desenho(sem_fundo(Image.open(os.path.join(ASSETS, arq))), w, s + 30, linha_lim=linha_lim, fino=fino,
                   bordas=bordas, traco=traco)


# ---------------------------------------------------------------- desenho na tela
@lru_cache(None)
def papel():
    rng = np.random.default_rng(3)
    a = np.ones((H, W, 3)) * np.array(PAPEL, float)
    a += rng.normal(0, 2.0, (H, W, 1))
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


def cola(img, im, cx, cy, rot=0.0, sc=1.0, alpha=1.0):
    if sc <= 0.02 or alpha <= 0.01:
        return
    if abs(sc - 1) > 0.01:
        im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BILINEAR)
    if abs(rot) > 0.3:
        im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    if alpha < 0.99:
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    img.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


@lru_cache(None)
def letra(txt, s, cor=GRAFITE, nome="Kalam-Bold.ttf"):
    f = fonte(nome, s)
    linhas = txt.split("\n")
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    lw = max(tmp.textlength(l, font=f) for l in linhas)
    lh = s * 1.12
    im = Image.new("RGBA", (int(lw + 30), int(lh * len(linhas) + 30)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k, l in enumerate(linhas):
        d.text((im.width / 2, 15 + lh * (k + 0.5)), l, font=f, fill=cor, anchor="mm")
    return im


def escreve(img, txt, x, y, s, prog=1.0, cor=GRAFITE, rot=0.0):
    """Texto escrito à mão aparecendo da esquerda para a direita (como se a caneta estivesse escrevendo)."""
    if prog <= 0:
        return
    im = letra(txt, s, cor)
    if prog < 1:
        im = im.copy()
        m = Image.new("L", im.size, 0)
        ImageDraw.Draw(m).rectangle((0, 0, int(im.width * prog), im.height), fill=255)
        im.putalpha(Image.fromarray(np.minimum(np.asarray(im.getchannel("A")), np.asarray(m))))
    cola(img, im, x, y, rot)


def seta(img, p0, p1, t, curva=40, prog=1.0):
    if prog <= 0:
        return
    rng = np.random.default_rng(semente(t) + 70)
    d = ImageDraw.Draw(img)
    n = max(3, int(25 * prog))
    pts = []
    for k in range(n):
        u = k / 24
        pts.append((p0[0] + (p1[0] - p0[0]) * u + math.sin(u * math.pi) * curva, p0[1] + (p1[1] - p0[1]) * u))
    rabisco(d, pts, rng, larg=4, amp=1.0, passadas=2, fechado=False)
    if prog >= 1:
        ang = math.atan2(p1[1] - pts[-3][1], p1[0] - pts[-3][0])
        for sd in (-0.55, 0.55):
            q = (p1[0] - 34 * math.cos(ang + sd), p1[1] - 34 * math.sin(ang + sd))
            rabisco(d, [p1, ((p1[0] + q[0]) / 2, (p1[1] + q[1]) / 2), q], rng, larg=4, amp=0.7, passadas=2, fechado=False)


def balao(img, txt, x, y, t, sc=1.0, s=86, cor=GRAFITE):
    """Balão de fala branco com contorno rabiscado e a palavra à mão."""
    if sc <= 0.02:
        return
    im = letra(txt, int(s * sc), cor)
    rx, ry = im.width * 0.62 + 20, im.height * 0.75 + 12
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(lay).ellipse((x - rx, y - ry, x + rx, y + ry), fill=(255, 255, 255, 240))
    img.alpha_composite(lay)
    rng = np.random.default_rng(semente(t) + 80)
    rabisco(ImageDraw.Draw(img), [(x + rx * math.cos(a), y + ry * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 48)[:-1]],
            rng, larg=4, amp=1.8, passadas=2)
    cola(img, im, x, y, rot=3)


def risca(img, x, y, r, t, cor=VERMELHO, prog=1.0):
    """X vermelho rabiscado."""
    rng = np.random.default_rng(semente(t) + 90)
    d = ImageDraw.Draw(img)
    for (a, b) in (((-1, -1), (1, 1)), ((1, -1), (-1, 1))):
        if prog <= 0:
            break
        p = min(1.0, prog * 2)
        prog -= 0.5
        q0 = (x + a[0] * r, y + a[1] * r)
        q1 = (x + a[0] * r + (b[0] - a[0]) * r * p, y + a[1] * r + (b[1] - a[1]) * r * p)
        rabisco(d, [q0, ((q0[0] + q1[0]) / 2, (q0[1] + q1[1]) / 2), q1], rng, cor=cor, larg=9, amp=2.5, passadas=2, fechado=False)


def estouro(img, x, y, t, txt="PÁ!", sc=1.0):
    """Onomatopeia do tapa: estrela rabiscada amarela + letra."""
    if sc <= 0.02:
        return
    rng = np.random.default_rng(semente(t) + 95)
    pts = []
    for k in range(24):
        a = 2 * math.pi * k / 24
        r = (150 if k % 2 == 0 else 95) * sc
        pts.append((x + r * math.cos(a), y + r * 0.8 * math.sin(a)))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(lay).polygon(pts, fill=(255, 214, 80, 235))
    img.alpha_composite(lay)
    rabisco(ImageDraw.Draw(img), pts, rng, larg=4, amp=1.5, passadas=2)
    cola(img, letra(txt, int(92 * sc), VERMELHO), x, y, rot=-6)


def mesa_montes(img, t, cartas_por=(1, 1, 1, 1), sc=1.0):
    """Os 4 montes virados dos jogadores (desenhados em lápis com o verso)."""
    s = semente(t)
    for k, (x, y) in enumerate(LUGARES):
        n = cartas_por[k]
        if n <= 0:
            continue
        for j in range(min(n, 3)):
            cola(img, spr_verso(180, s), x - j * 5, y - j * 6, rot=(-8, 6, -4, 9)[k] + j * 2, sc=sc)


# ---------------------------------------------------------------- cenas
def cena1(img, t):
    """Gancho: as 5 palavras se escrevendo, cada uma com a carta ao lado."""
    s = semente(t)
    for k, p in enumerate(PALAVRAS):
        t0 = 0.15 + k * 0.42
        y = 330 + k * 205
        x = 430 if k % 2 == 0 else 650
        escreve(img, p.upper() if False else p.capitalize(), x, y, 128, ease(seg(t, t0, t0 + 0.35)), rot=(-3, 2, -2, 3, -1)[k])
        cx = 870 if k % 2 == 0 else 210
        cola(img, spr_carta(p, 190, s), cx, y + 10, rot=(10, -9, 8, -10, 7)[k], sc=out_back(seg(t, t0 + 0.1, t0 + 0.45)))
    escreve(img, "só 5 palavras...", 540, 1400, 84, ease(seg(t, 2.5, 3.1)), rot=-2)
    escreve(img, "e TODO MUNDO erra!", 540, 1510, 96, ease(seg(t, 3.3, 3.9)), cor=VERMELHO, rot=-2)


def cena2(img, t, lt):
    """Preparação: o baralho vai sendo distribuído para os 4 montes, virado para baixo."""
    s = semente(t)
    n = 16
    dist = [0, 0, 0, 0]
    for k in range(n):
        t0 = 0.6 + k * 0.17
        u = ease(seg(lt, t0, t0 + 0.32))
        if u <= 0:
            continue
        dono = k % 4
        if u >= 1:
            dist[dono] += 1
            continue
        x0, y0 = CENTRO
        x1, y1 = LUGARES[dono]
        cola(img, spr_verso(200, s), x0 + (x1 - x0) * u, y0 + (y1 - y0) * u - math.sin(u * math.pi) * 120, rot=360 * u * 0.6)
    mesa_montes(img, t, dist)
    resto = n - sum(dist)
    if lt < 0.6 + n * 0.17 + 0.3:
        for j in range(max(1, min(4, resto // 4 + 1))):
            cola(img, spr_verso(230, s), CENTRO[0] - j * 4, CENTRO[1] - j * 6, rot=3 + j)
    escreve(img, "embaralha e divide tudo", 540, 300, 74, ease(seg(lt, 0.0, 0.6)), rot=-2)
    escreve(img, "um monte pra cada,", 540, 1480, 64, ease(seg(lt, 3.6, 4.2)), rot=-1)
    escreve(img, "virado pra baixo. SEM OLHAR!", 540, 1560, 64, ease(seg(lt, 4.3, 5.0)), cor=VERMELHO, rot=-1)


# sequência da cena 3: (jogador, palavra falada, carta que cai) — nunca bate (carta ≠ palavra)
SEQ3 = [(0, "taco", "pizza"), (1, "gato", "cabra"), (2, "cabra", "taco"), (3, "queijo", "gato"), (0, "pizza", "queijo")]


def pilha(img, t, itens, sc=1.0):
    """Monte do meio: lista de (carta, rotação) de baixo para cima."""
    s = semente(t)
    for k, (c, r) in enumerate(itens[-4:]):
        cola(img, spr_carta(c, 300, s), CENTRO[0] + (k % 2) * 8 - 4, CENTRO[1] - k * 3, rot=r, sc=sc)


def joga(img, t, lt, k, jog, palavra, c, t0, dur=1.3, mostra_balao=True):
    """A carta sai do monte do jogador, vira no ar e cai no meio; o balão com a palavra aparece em cima do jogador."""
    s = semente(t)
    u = ease(seg(lt, t0, t0 + 0.45))
    x0, y0 = LUGARES[jog]
    if 0 < u < 1:
        x = x0 + (CENTRO[0] - x0) * u
        y = y0 + (CENTRO[1] - y0) * u - math.sin(u * math.pi) * 90
        vira = abs(math.cos(u * math.pi))  # vira no meio do caminho (fica fininha e volta com a frente)
        sp = spr_verso(240, s) if u < 0.5 else spr_carta(c, 300, s)
        sp = sp.resize((max(2, int(sp.width * max(0.06, vira))), sp.height))
        cola(img, sp, x, y, rot=(-10 + 20 * u))
    if mostra_balao:
        b = out_back(seg(lt, t0 - 0.05, t0 + 0.25)) * (1 - ease(seg(lt, t0 + dur - 0.2, t0 + dur)))
        bx = min(max(LUGARES[jog][0], 260), 820)
        by = LUGARES[jog][1] + (-260 if jog in (0, 1) else 250)
        balao(img, palavra.upper() + "!", bx, by, t, sc=b)


def cena3(img, t, lt):
    """A vez: cada jogador vira uma carta no meio e fala a próxima palavra (aqui nenhuma bate)."""
    mesa_montes(img, t)
    caidas = []
    for k, (jog, pal, c) in enumerate(SEQ3):
        t0 = 0.6 + k * 1.35
        if lt >= t0 + 0.45:
            caidas.append((c, (-12, 8, -5, 11, -3)[k]))
    pilha(img, t, caidas)
    for k, (jog, pal, c) in enumerate(SEQ3):
        joga(img, t, lt, k, jog, pal, c, 0.6 + k * 1.35)
    # a ordem das palavras embaixo, com a da vez sublinhada
    atual = max([k for k in range(len(SEQ3)) if lt >= 0.6 + k * 1.35 - 0.05] or [-1])
    xs = [140, 330, 540, 750, 950]
    for k, p in enumerate(PALAVRAS):
        cor = VERMELHO if k == atual else GRAFITE
        escreve(img, p, xs[k], 1500, 62 if k != atual else 72, ease(seg(lt, 0.0 + k * 0.1, 0.4 + k * 0.1)), cor=cor)
    if atual >= 0:
        seta(img, (xs[atual] - 40, 1565), (xs[atual] + 40, 1565), t, curva=0)
    escreve(img, "e começa de novo! ↺", 540, 300, 70, ease(seg(lt, 7.4, 8.0)), rot=-2)


def cena4(img, t, lt):
    """Bateu: o jogador fala GATO e cai a carta do gato → todo mundo bate; o último leva a pilha."""
    s = semente(t)
    mesa_montes(img, t)
    base = [("pizza", -12), ("cabra", 8), ("taco", -5), ("queijo", 11)]
    caiu = lt >= 0.6 + 0.45
    leva = ease(seg(lt, 5.2, 5.9))
    if leva <= 0:
        pilha(img, t, base + ([("gato", -2)] if caiu else []))
    else:  # a pilha inteira escorrega para o último que bateu (jogador 3, em cima à esquerda)
        x = CENTRO[0] + (LUGARES[3][0] - CENTRO[0]) * leva
        y = CENTRO[1] + (LUGARES[3][1] - CENTRO[1]) * leva
        for k, (c, r) in enumerate((base + [("gato", -2)])[-4:]):
            cola(img, spr_carta(c, 300, s), x, y - k * 3, rot=r, sc=1 - 0.35 * leva)
    joga(img, t, lt, 0, 1, "gato", "gato", 0.6, dur=4.2)
    if caiu and lt < 2.9:
        escreve(img, "carta = palavra!", 540, 330, 84, ease(seg(lt, 1.15, 1.6)), cor=VERDE, rot=-2)
    # as 4 mãos batendo: os 3 primeiros quase juntos, o 4º atrasado
    tapas = [(0, 1.45), (1, 1.6), (2, 1.75), (3, 2.55)]
    for jog, tt in tapas:
        u = ease(seg(lt, tt, tt + 0.22))
        if u <= 0 or lt > 5.2:
            continue
        x0, y0 = LUGARES[jog]
        alvo = (CENTRO[0] + (jog % 2 * 2 - 1) * 40, CENTRO[1] + (1 if jog < 2 else -1) * 40)
        x = x0 + (alvo[0] - x0) * u
        y = y0 + (alvo[1] - y0) * u
        rot = {0: 135, 1: -135, 2: -45, 3: 45}[jog]
        cola(img, spr_mao("270B", 260, s, rot), x, y)
    for jog, tt in tapas:
        if tt + 0.2 <= lt < tt + 0.65:
            estouro(img, CENTRO[0] + (jog - 1.5) * 60, CENTRO[1] - 220, t, "PÁ!", out_back(seg(lt, tt + 0.2, tt + 0.4)))
    if lt >= 2.9:
        escreve(img, "o ÚLTIMO a bater", 560, 290, 74, ease(seg(lt, 3.0, 3.5)), cor=VERMELHO, rot=-2)
        escreve(img, "leva a pilha inteira!", 560, 380, 70, ease(seg(lt, 3.6, 4.2)), rot=-2)
        seta(img, (330, 430), (250, 530), t, curva=-25, prog=ease(seg(lt, 3.2, 3.6)))


ESPECIAIS = [("gorila", "bate no peito!"), ("narval", "chifre com as mãos!"), ("marmota", "mãos na mesa!")]


def cena5(img, t, lt):
    """Especiais: cada bicho grande com o gesto; depois todo mundo bate no monte."""
    s = semente(t)
    bloco = 3.2
    k = min(2, int(lt / bloco))
    bt = lt - k * bloco
    nome, gesto = ESPECIAIS[k]
    entra = out_back(seg(bt, 0.0, 0.35))
    cola(img, spr_carta(nome, 230, s), 170, 430, rot=-9, sc=entra)
    escreve(img, nome.capitalize() + "!", 600, 360, 110, ease(seg(bt, 0.1, 0.5)), rot=-3)
    cola(img, spr_arte(nome, 560, s), 540, 1000, sc=entra)
    if nome == "gorila":  # dois punhos batendo no peito, alternados
        for lado, fase in ((-1, 0.0), (1, 0.5)):
            pulso = abs(math.sin((bt * 2.2 + fase) * math.pi))
            cola(img, spr_mao("1F44A", 170, s, 90 if lado < 0 else -90, lado > 0), 540 + lado * 95, 1080 - 30 * pulso,
                 sc=entra)
    elif nome == "narval":  # duas mãos juntas formando o chifre
        sobe = ease(seg(bt, 0.6, 1.1))
        for lado in (-1, 1):
            cola(img, spr_mao("270B", 190, s, -20 * lado, lado > 0), 540 + lado * 55, 760 - 140 * sobe, sc=entra)
    else:  # marmota: as duas mãos batendo na mesa
        for lado in (-1, 1):
            pulso = abs(math.sin(bt * 2.4 * math.pi))
            cola(img, spr_mao("270B", 200, s, 180, lado > 0), 540 + lado * 270, 1250 + 40 * pulso, sc=entra)
        if bt > 0.8 and abs(math.sin(bt * 2.4 * math.pi)) > 0.9:
            estouro(img, 540, 1330, t, "PÁ!", 0.6)
    escreve(img, gesto, 540, 1450, 84, ease(seg(bt, 0.6, 1.2)), cor=VERMELHO, rot=-2)
    if k == 2:
        escreve(img, "...e só depois bate no monte!", 540, 1550, 60, ease(seg(bt, 2.2, 2.8)), rot=-1)


def cena6(img, t, lt):
    """Capivara (a carta extra da caixa da Sua Vez) e o gesto oficial."""
    s = semente(t)
    escreve(img, "na nossa caixa", 540, 300, 74, ease(seg(lt, 0.0, 0.5)), rot=-2)
    escreve(img, "tem a CAPIVARA!", 540, 395, 96, ease(seg(lt, 0.4, 0.9)), cor=VERMELHO, rot=-2)
    cola(img, spr_carta("capivara", 340, s), 270, 840, rot=-8, sc=out_back(seg(lt, 0.3, 0.7)))
    cola(img, spr_img("capivara_gesto.png", 500, s, 110, True, True, 0.55), 770, 940, rot=4, sc=out_back(seg(lt, 0.9, 1.3)))
    seta(img, (640, 1300), (730, 1190), t, curva=30, prog=ease(seg(lt, 1.6, 2.0)))
    escreve(img, "dois dedinhos na boca:", 520, 1420, 64, ease(seg(lt, 1.8, 2.4)), rot=-1)
    escreve(img, "os dentes da capivara!", 520, 1510, 70, ease(seg(lt, 2.4, 3.0)), cor=VERMELHO, rot=-1)


ERROS = ["errou o gesto?", "bateu sem precisar?", "hesitou?"]


def cena7(img, t, lt):
    """Erros: três situações riscadas e a pilha indo para quem errou."""
    s = semente(t)
    mesa_montes(img, t)
    pilha(img, t, [("taco", -6), ("narval", 7), ("queijo", -3)])
    for k, e in enumerate(ERROS):
        t0 = 0.3 + k * 1.2
        y = 300 + k * 110
        escreve(img, e, 520, y, 74, ease(seg(lt, t0, t0 + 0.5)), rot=-2)
        risca(img, 900, y, 34, t, prog=ease(seg(lt, t0 + 0.5, t0 + 0.8)))
    escreve(img, "A PILHA É SUA!", 540, 1530, 100, ease(seg(lt, 4.0, 4.6)), cor=VERMELHO, rot=-3)
    if lt > 4.3:
        seta(img, (470, 1450), (330, 1390), t, curva=-30, prog=ease(seg(lt, 4.3, 4.8)))


def cena8(img, t, lt):
    """Vitória: quem está sem cartas e bate primeiro ganha; depois a pergunta para comentar."""
    s = semente(t)
    if lt < 4.3:
        mesa_montes(img, t, (0, 2, 2, 2))
        escreve(img, "0 cartas", LUGARES[0][0], LUGARES[0][1] + 10, 62, ease(seg(lt, 0.2, 0.6)), cor=VERMELHO)
        pilha(img, t, [("pizza", -6), ("queijo", 5)] + ([("queijo", -2)] if lt > 1.3 else []))
        if lt > 1.0:
            balao(img, "QUEIJO!", 820, 1160, t, sc=out_back(seg(lt, 1.0, 1.3)))
        u = ease(seg(lt, 1.5, 1.7))
        if u > 0:
            x0, y0 = LUGARES[0]
            cola(img, spr_mao("270B", 260, s, 135), x0 + (CENTRO[0] - 40 - x0) * u, y0 + (CENTRO[1] + 40 - y0) * u)
        if lt > 1.7:
            estouro(img, 540, 760, t, "1º!", out_back(seg(lt, 1.7, 1.95)))
            escreve(img, "sem cartas e bateu PRIMEIRO:", 540, 300, 66, ease(seg(lt, 2.0, 2.6)), rot=-2)
            escreve(img, "GANHOU!", 540, 410, 120, ease(seg(lt, 2.6, 3.0)), cor=VERDE, rot=-3)
    else:
        bt = lt - 4.3
        escreve(img, "Comenta aqui:", 540, 520, 96, ease(seg(bt, 0.0, 0.5)), rot=-2)
        escreve(img, "qual palavra você\nSEMPRE erra?", 540, 760, 104, ease(seg(bt, 0.4, 1.1)), cor=VERMELHO, rot=-2)
        for k, p in enumerate(PALAVRAS):
            cola(img, spr_carta(p, 170, s), 150 + k * 195, 1180 + (k % 2) * 60, rot=(-8, 6, -5, 9, -7)[k],
                 sc=out_back(seg(bt, 1.0 + k * 0.12, 1.3 + k * 0.12)))


def cena9(img, t, lt):
    """Tela final: a caixa oficial em lápis + os dados de aluguel escritos à mão."""
    s = semente(t)
    cola(img, logo_card(360), 540, 220, sc=out_back(seg(lt, 0.0, 0.4)))
    cola(img, spr_img("caixa_frente.png", 400, s), 540, 690, rot=-4, sc=out_back(seg(lt, 0.15, 0.55)))
    escreve(img, "ALUGUE O TACO GATO\nCABRA QUEIJO PIZZA", 540, 1070, 76, ease(seg(lt, 0.5, 1.2)), cor=VERMELHO, rot=-2)
    escreve(img, "2 a 8 jogadores · 5 dias de jogo", 540, 1240, 58, ease(seg(lt, 1.1, 1.6)))
    escreve(img, "reserve online · retire em Mauá\nou receba em casa", 540, 1360, 54, ease(seg(lt, 1.5, 2.0)))
    escreve(img, "LINK NA BIO · @SUAVEZ_BG", 540, 1510, 72, ease(seg(lt, 1.9, 2.4)), cor=AZUL, rot=-1)


CENAS = [None, cena2, cena3, cena4, cena5, cena6, cena7, cena8, cena9]


# ---------------------------------------------------------------- legenda da prévia (roteiro)
def quebra(txt, n=30):
    pal, linhas, cur = txt.split(), [], ""
    for p in pal:
        if len(cur) + len(p) + 1 > n and cur:
            linhas.append(cur)
            cur = p
        else:
            cur = (cur + " " + p).strip()
    linhas.append(cur)
    return linhas


def legenda(img, t, k, lt):
    """Na prévia a fala entra em pedaços de 2 linhas embaixo (com a narração, a legenda segue as palavras dele)."""
    linhas = quebra(ROTEIRO[k])
    blocos = [linhas[i:i + 2] for i in range(0, len(linhas), 2)]
    b = blocos[min(len(blocos) - 1, int(lt / DURS[k] * len(blocos)))]
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(lay).rounded_rectangle((40, 1830 - 70 * len(b), 1040, 1900), radius=26, fill=(255, 255, 255, 200))
    img.alpha_composite(lay)
    for j, l in enumerate(b):
        cola(img, letra(l, 52, GRAFITE, "PatrickHand-Regular.ttf"), 540, 1830 - 70 * len(b) + 40 + j * 68)


def frame(t, com_legenda=True):
    img = papel().copy()
    k = max(i for i in range(len(DURS)) if t >= INICIO[i] - 1e-9)
    lt = t - INICIO[k]
    if k == 0:
        cena1(img, t)
    else:
        CENAS[k](img, t, lt)
    if k < 8:
        img.alpha_composite(logo_card(150), (W - 186, 46))
    if com_legenda:
        legenda(img, t, k, lt)
    return img.convert("RGB")


def render_frame(fi):
    return frame(fi / FPS).tobytes()


def cues():
    c = [(0.15 + k * 0.42, "pop", 0.4) for k in range(5)] + [(3.3, "boing", 0.4)]
    t2 = INICIO[1]
    c += [(t2 + 0.6 + k * 0.17, "flip", 0.35) for k in range(16)]
    t3 = INICIO[2]
    for k in range(len(SEQ3)):
        c += [(t3 + 0.6 + k * 1.35, "whoosh", 0.25), (t3 + 1.05 + k * 1.35, "flip", 0.5)]
    t4 = INICIO[3]
    c += [(t4 + 1.05, "flip", 0.5), (t4 + 1.15, "ding", 0.5)]
    c += [(t4 + tt + 0.2, "carimbo", 0.55) for tt in (1.45, 1.6, 1.75, 2.55)]
    c += [(t4 + 5.2, "whoosh", 0.4)]
    t5 = INICIO[4]
    c += [(t5 + k * 3.2, "pop", 0.5) for k in range(3)]
    t6 = INICIO[5]
    c += [(t6 + 0.3, "pop", 0.5), (t6 + 0.9, "pop", 0.5)]
    t7 = INICIO[6]
    c += [(t7 + 0.8 + k * 1.2, "carimbo", 0.35) for k in range(3)] + [(t7 + 4.0, "boing", 0.5)]
    t8 = INICIO[7]
    c += [(t8 + 1.3, "flip", 0.5), (t8 + 1.7, "carimbo", 0.6), (t8 + 1.9, "chime", 0.5), (t8 + 4.3, "whoosh", 0.4)]
    c += [(INICIO[8], "whoosh", 0.4), (INICIO[8] + 0.5, "chime", 0.5)]
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    print(f"duração {DUR:.1f} s")
    if a.frame:
        folha([frame(x) for x in a.frame], os.path.join(OUT, "frames_taco.jpg"))
        return
    wav = os.path.join(OUT, "taco_previa.wav")
    som.build(wav, DUR, cues(), musica="travessa", fx_ganho=0.55, musica_ganho=0.3)
    motor.encode(os.path.join(OUT, "taco_previa_1080.mp4"), render_frame, list(range(int(round(DUR * FPS)))), wav)


if __name__ == "__main__":
    main()
