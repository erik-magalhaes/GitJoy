#!/usr/bin/env python3
"""Reels do Santorini (out/2026): STOP MOTION com as peças OFICIAIS do manual Spin Master (ampliadas por IA, cena.py)
sobre o mar ao PÔR DO SOL (escolha dele), letreiros em Cinzel dourado. 12 poses/s com tremidinho leve.

Cenas (roteiro de 9 falas):
  1 gancho: torre sobe 1-2-3-cúpula · 2 dois construtores · 3 move 1 casa (sobe 1, desce quanto quiser)
  4 constrói 1 andar vizinho · 5 cúpula fecha · 6 sobe ao 3º = vence · 7 deuses (cartas + Apolo troca, Atlas cúpula)
  8 comenta · 9 tela final

    python3 stopmo.py --frame 3 15 40      # quadros de teste em out/frames.jpg
    python3 stopmo.py --only preview       # out/santorini_previa.mp4 (+ _720p.mp4), legendas do roteiro, sem voz
"""
import argparse
import math
import os
import sys
import zlib
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "comum"))
sys.path.insert(0, os.path.join(REPO, "voodoo-reels"))
import motor  # noqa: E402
from motor import W, H, WHITE, seg, ease, pop, quica, cola, sombra, pilula, logo_card, emoji, folha  # noqa: E402
import cena  # noqa: E402
from cena import A, B, FOLGA  # noqa: E402
from conceitos import txt  # noqa: E402
from conceitos2 import por_do_sol, luz_quente, brilho  # noqa: E402

OUT = os.path.join(ROOT, "out")
FPS = 12
SCENES = [(0.0, 6.0), (6.0, 12.5), (12.5, 20.5), (20.5, 27.5), (27.5, 34.0), (34.0, 42.0), (42.0, 51.0),
          (51.0, 58.5), (58.5, 66.0)]
DUR = SCENES[-1][1]
ROTEIRO = [
    "Construa como um mortal... e vença como um deus. Esse é o Santorini!",
    "Cada jogador tem dois construtores, e eles começam em qualquer casa livre da ilha.",
    "Na sua vez, você move um construtor uma casa, pra qualquer lado. Ele sobe no máximo um andar... mas pra descer, "
    "pode pular quanto quiser.",
    "Depois de mover, esse mesmo construtor constrói um andar numa casa vizinha: o primeiro, o segundo ou o terceiro.",
    "Em cima do terceiro andar vai a cúpula azul. Cúpula fecha a torre: ali ninguém sobe mais.",
    "Pra vencer, é só subir um construtor no terceiro andar. Mas se na sua vez você não conseguir mover e construir... "
    "perdeu.",
    "E tem os deuses gregos! Cada um quebra uma regra: o Apolo troca de lugar com o rival, e o Atlas fecha a torre com "
    "cúpula em qualquer altura.",
    "Partidas de vinte minutos, de duas a quatro pessoas. E aí: você subiria na torre... ou fecharia a do rival? "
    "Comenta aqui!",
    "Aluga o Santorini na Sua Vez! Retira em Mauá ou recebe em casa. O link tá na bio!",
]
LINHA = motor.Linha(os.path.join(ROOT, "narracao", "timeline.json"))
DOURADO, CREME, VINHO = (255, 206, 90), (255, 240, 210), (70, 30, 40)
VERDE, VERMELHO = (34, 170, 90), (220, 50, 50)
CAIXA = os.path.join(REPO, "hobby-reels", "assets", "acervo", "santorini.png")

# peças com a luz quente do pôr do sol (pré-calculadas uma vez)
_peca_orig = cena.peca


@lru_cache(None)
def _peca_quente(n):
    return luz_quente(_peca_orig(n), 0.28)


cena.peca = _peca_quente

TAM = (2200, 1700)
ORIGEM = np.array([TAM[0] * 0.40, TAM[1] * 0.86])
CAM_TODO = (1140, 1000, 1900)  # centro x, centro y, largura (coordenadas da cena)
AREA = (0, 470, W, 1100)      # onde a cena entra na tela (x, y, w, h)


def casa(i, j):
    return cena.casa(i, j, ORIGEM)


@lru_cache(None)
def fundo():
    return por_do_sol()


@lru_cache(None)
def tabuleiro():
    t = cena.tabuleiro(ORIGEM, TAM)
    return luz_quente(t, 0.2)


def tremor(chave, frame, amp=1.6):
    h = zlib.crc32(f"{chave}-{frame}".encode())
    return np.array([((h & 255) / 255 - 0.5) * 2 * amp, (((h >> 8) & 255) / 255 - 0.5) * 2 * amp])


# ---------------------------------------------------------------- desenho da cena (objetos de trás para a frente)
def brilho_casa(img, i, j, cor, a=170):
    c = casa(i, j)
    h = 0.5 * FOLGA * 0.92
    q = [c - h * A - h * B, c + h * A - h * B, c + h * A + h * B, c - h * A + h * B]
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).polygon([tuple(p) for p in q], fill=cor + (a,), outline=(255, 255, 240, 255), width=9)
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(4)))


def torre(img, i, j, niveis, f, cai=None, cai_ini=None):
    """cai = (progresso 0..1) da ÚLTIMA peça da torre caindo de cima."""
    centro = casa(i, j) + tremor((i, j), f)
    if cai is None or cai >= 1 or not niveis:
        return cena.poe_torre(img, centro, niveis)
    base = niveis[:-1]
    topo = cena.poe_torre(img, centro, base)
    y = -(1 - quica_u(cai)) * 520
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    cena.poe_torre(lay, centro, niveis, sombra=False)
    if base:
        so = Image.new("RGBA", img.size, (0, 0, 0, 0))
        cena.poe_torre(so, centro, base, sombra=False)
        a = np.asarray(lay).copy()
        a[np.asarray(so)[..., 3] > 200] = 0
        lay = Image.fromarray(a)
    img.alpha_composite(lay, (0, int(y)))
    return topo


def quica_u(u):
    return quica(u, 0.0, 1.0)


def peao(img, ponto, cor, f, chave, lift=0.0):
    cena.poe_peao(img, ponto + tremor(chave, f, 1.2) + np.array([0, -lift]), cor)


def topo_de(i, j, niveis):
    lay = Image.new("RGBA", (8, 8))
    return cena.poe_torre(lay, casa(i, j), niveis.replace("c", ""), sombra=False) if niveis else casa(i, j)


def desenha(f, torres, peoes=(), destaque=None, caindo=None, cam=CAM_TODO, extra=None):
    """torres {(i,j): "123c"}; peoes [(pos_ini, pos_fim, u, cor, altura_pulo)] em casas; caindo {(i,j): u}."""
    img = tabuleiro().copy()
    if destaque:
        for (i, j), cor in destaque.items():
            brilho_casa(img, i, j, cor)
    objs = []
    for k, niv in torres.items():
        objs.append((k[0] + k[1], "t", k, niv))
    for p in peoes:
        a, b, u, cor, alt = p
        ii = a[0] + (b[0] - a[0]) * u
        jj = a[1] + (b[1] - a[1]) * u
        objs.append((max(a[0] + a[1], b[0] + b[1]) - 0.01 if 0 < u < 1 else ii + jj - 0.01, "p", p, None))
    for _, tipo, k, niv in sorted(objs, key=lambda o: -o[0]):
        if tipo == "t":
            torre(img, k[0], k[1], niv, f, (caindo or {}).get(k))
        else:
            a, b, u, cor, alt = k
            pa = topo_de(*a, torres.get(a, ""))
            pb = topo_de(*b, torres.get(b, ""))
            ue = ease(u)
            p = pa + (pb - pa) * ue
            peao(img, p, cor, f, (a, cor), lift=math.sin(math.pi * min(1, max(0, u))) * alt)
    if extra:
        extra(img)
    return camera(img, cam)


def camera(img, cam):
    cx, cy, w = cam
    h = w * AREA[3] / AREA[2]
    caixa = (int(cx - w / 2), int(cy - h / 2), int(cx + w / 2), int(cy + h / 2))
    return img.crop(caixa).resize((AREA[2], AREA[3]), Image.LANCZOS)


def cam_lerp(c0, c1, u):
    u = ease(min(1, max(0, u)))
    return tuple(a + (b - a) * u for a, b in zip(c0, c1))


def cam_casa(i, j, w=1300, dy=-160):
    c = casa(i, j)
    return (c[0], c[1] + dy, w)


# ---------------------------------------------------------------- textos
@lru_cache(None)
def titulo(t, size=96, cor=DOURADO, sombra_px=4):
    return txt(t, "cinzel", size, cor, VINHO, 5, sombra_px)


@lru_cache(None)
def selo(t, cor=VINHO, fg=CREME):
    return pilula(t, 44, cor, fg, fg)


def poe_texto(img, im, x, y, t, t0, rot=0):
    if t >= t0:
        cola(img, im, x, y, rot, pop(t, t0))


# ---------------------------------------------------------------- cenas (t = tempo LOCAL da cena, f = quadro global)
GANCHO = {(1, 1): "123", (3, 1): "12", (1, 3): "1", (3, 3): "2"}


def s1(c, t, f):
    tor = dict(GANCHO)
    tor[(2, 2)] = "123c"[: 1 + min(3, int(max(0, t - 0.6) / 0.55))] if t >= 0.6 else ""
    n = len(tor[(2, 2)])
    u = (t - 0.6 - (n - 1) * 0.55) / 0.35 if n else None
    if not tor[(2, 2)]:
        del tor[(2, 2)]
    zoom = cam_lerp(cam_casa(2, 2, 1400), CAM_TODO, seg(t, 3.0, 5.5))
    sc = desenha(f, tor, caindo={(2, 2): u} if n else None, cam=zoom)
    c.alpha_composite(sc, AREA[:2])
    poe_texto(c, titulo("SUBA AO 3º ANDAR\nE VENÇA", 92, CREME), W / 2, 260, t, 0.0)
    poe_texto(c, titulo("CONSTRUA COMO UM MORTAL.\nVENÇA COMO UM DEUS.", 64), W / 2, 1520, t, 2.9)


def s2(c, t, f):
    lugares = [((1, 1), "azul"), ((3, 3), "cinza"), ((1, 3), "azul"), ((3, 1), "cinza")]
    c.alpha_composite(_s2_quadro(f, t, lugares), AREA[:2])
    poe_texto(c, titulo("2 CONSTRUTORES\nPARA CADA UM", 88, CREME), W / 2, 260, t, 0.2)
    poe_texto(c, selo("COMEÇAM EM QUALQUER CASA LIVRE"), W / 2, 1520, t, 3.4)


def _s2_quadro(f, t, lugares):
    img = tabuleiro().copy()
    for k, (pos, cor) in sorted(enumerate(lugares), key=lambda e: -(e[1][0][0] + e[1][0][1])):
        t0 = 0.5 + 0.7 * k
        if t < t0:
            continue
        u = min(1, (t - t0) / 0.45)
        peao(img, casa(*pos), cor, f, (pos, cor), lift=(1 - quica_u(u)) * 520)
    return camera(img, CAM_TODO)


S3_TOR = {(1, 2): "1", (3, 2): "12", (2, 3): "1", (1, 1): "12"}


def s3(c, t, f):
    viz = {(i, j) for i in (1, 2, 3) for j in (1, 2, 3)} - {(2, 2)}
    dest = {}
    if 0.8 <= t < 6.0:
        dest = {k: DOURADO for k in viz}
        if 2.4 <= t < 4.2:
            dest[(3, 2)] = VERMELHO
        if t >= 4.2:
            dest[(1, 2)] = VERDE
    if t < 4.6:
        pe = [((2, 2), (2, 2), 1.0, "azul", 0)]
    else:
        pe = [((2, 2), (1, 2), min(1, (t - 4.6) / 0.6), "azul", 160)]
    if 2.4 <= t < 3.6:  # tenta subir 2 andares: vai e volta
        u = (t - 2.4) / 1.2
        pe = [((2, 2), (3, 2), 0.35 * math.sin(math.pi * u), "azul", 60)]
    sc = desenha(f, S3_TOR, pe, dest, cam=cam_casa(2, 2, 1500, -120))
    c.alpha_composite(sc, AREA[:2])
    poe_texto(c, titulo("ANDA 1 CASA,\nPRA QUALQUER LADO", 80, CREME), W / 2, 260, t, 0.2)
    if 2.6 <= t < 4.2:
        cola(c, emoji("❌", 170), 760, 640, 0, pop(t, 2.6))
        cola(c, selo("2 ANDARES DE UMA VEZ? NÃO!", VERMELHO, WHITE), W / 2, 1520, 0, pop(t, 2.6))
    if t >= 4.6:
        cola(c, selo("SOBE NO MÁXIMO 1 ANDAR", VERDE, WHITE), W / 2, 1450, 0, pop(t, 4.6))
        poe_texto(c, selo("DESCER: QUANTO QUISER"), W / 2, 1545, t, 5.8)


S4_TOR = {(1, 2): "1", (3, 2): "12", (1, 1): "12", (2, 3): "1"}


def s4(c, t, f):
    tor = dict(S4_TOR)
    caindo = {}
    passos = [((2, 2), "1", 0.8), ((1, 1), "123", 2.5), ((2, 3), "12", 4.2)]
    for k, niv, t0 in passos:
        if t >= t0:
            tor[k] = niv
            caindo[k] = min(1, (t - t0) / 0.4)
    dest = {}
    for k, niv, t0 in passos:
        if t0 - 0.5 <= t < t0 + 0.8:
            dest[k] = DOURADO
    sc = desenha(f, tor, [((1, 2), (1, 2), 1.0, "azul", 0)], dest, caindo, cam=cam_casa(1, 2, 1600, -200))
    c.alpha_composite(sc, AREA[:2])
    poe_texto(c, titulo("E CONSTRÓI 1 ANDAR\nNUMA CASA VIZINHA", 80, CREME), W / 2, 260, t, 0.2)
    for k, (_, niv, t0) in enumerate(passos):
        if t >= t0 + 0.3:
            cola(c, selo(f"{len(niv)}º ANDAR", (40, 90, 170), WHITE), 220 + 320 * k, 1520, (-3, 2, -2)[k], pop(t, t0 + 0.3))


S5_TOR = {(1, 2): "1", (3, 2): "12", (1, 1): "123", (2, 3): "12", (2, 2): "1"}


def s5(c, t, f):
    tor = dict(S5_TOR)
    caindo = {}
    if t >= 0.9:
        tor[(1, 1)] = "123c"
        caindo[(1, 1)] = min(1, (t - 0.9) / 0.45)
    sc = desenha(f, tor, [((1, 2), (1, 2), 1.0, "azul", 0)], cam=cam_casa(1, 1, 1250, -330))
    c.alpha_composite(sc, AREA[:2])
    poe_texto(c, titulo("A CÚPULA\nFECHA A TORRE", 92, CREME), W / 2, 260, t, 0.2)
    if t >= 1.6:
        cola(c, emoji("🔒", 150), 660, 640, 8, pop(t, 1.6))
        cola(c, selo("ALI NINGUÉM SOBE MAIS"), W / 2, 1520, 0, pop(t, 2.0))


S6_TOR = {(1, 2): "12", (2, 2): "123", (1, 1): "123c", (3, 2): "12", (2, 3): "1"}


def s6(c, t, f):
    if t < 1.2:
        pe = [((1, 2), (1, 2), 1.0, "azul", 0)]
    else:
        pe = [((1, 2), (2, 2), min(1, (t - 1.2) / 0.7), "azul", 180)]
    pe.append(((3, 3), (3, 3), 1.0, "cinza", 0))
    vit = t >= 1.9

    def extra(img):
        if vit:
            p = topo_de(2, 2, "123")
            lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
            d = ImageDraw.Draw(lay)
            u = seg(t, 1.9, 2.6)
            for k in range(16):
                a = k * math.tau / 16 + t * 0.3
                r = 900 * u
                d.polygon([tuple(p), (p[0] + r * math.cos(a - 0.08), p[1] + r * math.sin(a - 0.08)),
                           (p[0] + r * math.cos(a + 0.08), p[1] + r * math.sin(a + 0.08))], fill=(255, 230, 140, 70))
            img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(8)))
    cam = cam_lerp(CAM_TODO, cam_casa(2, 2, 1300, -330), seg(t, 0.6, 2.0))
    sc = desenha(f, S6_TOR, pe, {(2, 2): DOURADO} if 0.5 < t < 1.9 else None, cam=cam, extra=extra)
    c.alpha_composite(sc, AREA[:2])
    if vit:
        brilho(c, W / 2, 760, 420, a=int(140 * seg(t, 1.9, 2.4)))
        cola(c, titulo("VENCEU.", 170), W / 2, 270, 0, pop(t, 2.0))
    else:
        poe_texto(c, titulo("PRA VENCER:\nSUBA AO 3º ANDAR", 82, CREME), W / 2, 260, t, 0.2)
    if t >= 4.6:
        cola(c, selo("SEM JOGADA POSSÍVEL? PERDEU!", VERMELHO, WHITE), W / 2, 1520, 0, pop(t, 4.6))


@lru_cache(None)
def cartas():
    tab = Image.open(os.path.join(ROOT, "assets", "fotos", "zatu_2.png"))
    c = tab.crop((0, int(tab.height * 0.47), tab.width, tab.height))
    al = np.asarray(c.getchannel("A")).astype(np.float32)
    corte = np.clip(np.arange(c.height) / (c.height * 0.16), 0, 1)[:, None]
    c.putalpha(Image.fromarray((al * corte).astype(np.uint8)))
    return luz_quente(c.resize((1040, int(c.height * 1040 / c.width)), Image.LANCZOS), 0.2)


S7_TOR = {(1, 2): "1", (2, 3): "12", (3, 1): "12", (2, 1): "1"}


def s7(c, t, f):
    if t < 3.0:
        brilho(c, W / 2, 1000, 480, a=140)
        cola(c, sombra(cartas(), 30, (0, 30), 0.45), W / 2, 1000, 0, 0.9 + 0.1 * ease(seg(t, 0, 0.6)))
        poe_texto(c, titulo("E OS DEUSES\nQUEBRAM AS REGRAS", 84), W / 2, 260, t, 0.1)
        return
    u = t - 3.0
    tor = dict(S7_TOR)
    caindo = {}
    if u < 3.0:  # Apolo: troca com o rival
        k = min(1, max(0, (u - 0.8) / 0.7))
        pe = [((2, 2), (3, 2), k, "azul", 150), ((3, 2), (2, 2), k, "cinza", 60)]
        rot, sub = "APOLO", "TROCA DE LUGAR COM O RIVAL"
    else:  # Atlas: cúpula em qualquer altura
        pe = [((3, 2), (3, 2), 1.0, "azul", 0), ((2, 2), (2, 2), 1.0, "cinza", 0)]
        if u >= 3.8:
            tor[(2, 1)] = "1c"
            caindo[(2, 1)] = min(1, (u - 3.8) / 0.45)
        rot, sub = "ATLAS", "CÚPULA EM QUALQUER ALTURA"
    sc = desenha(f, tor, pe, None, caindo, cam=cam_casa(2, 2, 1500, -200))
    c.alpha_composite(sc, AREA[:2])
    t0 = 3.0 if rot == "APOLO" else 6.0
    cola(c, titulo(rot, 150), W / 2, 250, 0, pop(t, t0))
    cola(c, selo(sub), W / 2, 1520, 0, pop(t, t0 + 0.3))


def s8(c, t, f):
    tor = {(1, 2): "12", (2, 2): "123", (1, 1): "123c", (3, 2): "12", (2, 3): "1", (3, 3): "123"}
    pe = [((2, 3), (2, 3), 1.0, "azul", 0), ((3, 2), (3, 2), 1.0, "cinza", 0)]
    cam = cam_lerp(CAM_TODO, (CAM_TODO[0] + 80, CAM_TODO[1] - 40, CAM_TODO[2] * 0.9), seg(t, 0, 7.5))
    sc = desenha(f, tor, pe, {(3, 3): DOURADO} if int(t * 2) % 2 == 0 else None, cam=cam)
    c.alpha_composite(sc, AREA[:2])
    poe_texto(c, titulo("VOCÊ SUBIRIA...\nOU FECHARIA A TORRE?", 74, CREME), W / 2, 270, t, 0.2)
    poe_texto(c, selo("2 A 4 JOGADORES · 20 MIN"), W / 2, 1450, t, 0.6)
    poe_texto(c, pilula("COMENTA AQUI!", 50, DOURADO, VINHO, VINHO), W / 2, 1545, t, 3.0)


@lru_cache(None)
def caixa_sant(h):
    im = Image.open(CAIXA).convert("RGBA")
    im = im.crop(im.getbbox())
    return sombra(im.resize((int(im.width * h / im.height), h), Image.LANCZOS), 26, (0, 22), 0.5)


def s9(c, t, f):
    brilho(c, W / 2, 780, 520, a=150)
    cola(c, logo_card(360), W / 2, 230, 0, pop(t, 0.0))
    cola(c, caixa_sant(560), W / 2, 760, -3, pop(t, 0.25))
    itens = [(0.6, titulo("ALUGUE O SANTORINI", 82), 1130), (0.85, selo("2 A 4 JOGADORES · 20 MIN"), 1250),
             (1.0, pilula("5 DIAS DE JOGO", 46, DOURADO, VINHO, VINHO), 1345),
             (1.15, selo("RESERVE ONLINE · RETIRE EM MAUÁ E ABC"), 1440),
             (1.3, pilula("OU RECEBA EM CASA!", 42, VERDE), 1530), (1.45, pilula("LINK NA BIO · @SUAVEZ_BG", 46, (249, 115, 22)), 1625)]
    for t0, im, y in itens:
        poe_texto(c, im, W / 2, y, t, t0)


CENAS = [s1, s2, s3, s4, s5, s6, s7, s8, s9]


# ---------------------------------------------------------------- quadro
def quadro(n, com_legenda=True, subs=None):
    t = n / FPS
    to = LINHA.to_orig(t)
    k = max(i for i, (a, b) in enumerate(SCENES) if a <= min(to, DUR - 1e-6))
    a, b = SCENES[k]
    img = fundo().copy()
    CENAS[k](img, to - a, n)
    if k < 8:
        wm = logo_card(150)
        img.alpha_composite(wm, (W - wm.width - 30, 40))
    # passagem entre cenas: flash quente curto
    d = min(abs(to - a), abs(b - to))
    if d < 0.12 and k > 0:
        lay = Image.new("RGBA", (W, H), (255, 220, 170, int(160 * (1 - d / 0.12))))
        img.alpha_composite(lay)
    if com_legenda and subs:
        motor.legenda(img, subs, t, y=1740)
    return img


def _render(args):
    n, leg = args
    return quadro(n, leg, SUBS).convert("RGB").tobytes()


SUBS = motor.default_subs(SCENES, ROTEIRO)


# ---------------------------------------------------------------- som
def trilha(dur):
    """Pluck "grego" (escala de ré menor harmônica, ritmo de sirtaki suave) + baixo + pad; sem direitos autorais."""
    from audio import SR, add, env, lp, t_

    def note(nome):  # o note() do Vudú não tem E nem C#
        semi = {"C": -9, "C#": -8, "D": -7, "Eb": -6, "E": -5, "F": -4, "F#": -3, "G": -2, "A": 0, "Bb": 1, "B": 2}
        return 440 * 2 ** ((semi[nome[:-1]] + 12 * (int(nome[-1]) - 4)) / 12)
    out = np.zeros(int(dur * SR))
    beat = 60 / 100
    acordes = [("D3", ["D4", "F4", "A4"]), ("G2", ["G3", "Bb3", "D4"]), ("A2", ["A3", "C#4", "E4"]),
               ("D3", ["D4", "F4", "A4"])]
    mel = ["A4", "D5", "F5", "E5", "D5", "C#5", "D5", "A4", "Bb4", "D5", "G5", "F5", "E5", "D5", "C#5", "E5",
           "A4", "C#5", "E5", "G5", "F5", "E5", "D5", "C#5", "D5", "F5", "A5", "F5", "E5", "D5", "D5", None]

    def pluck(f, d=0.45):
        t = t_(d)
        x = (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(4 * np.pi * f * t) + 0.2 * np.sin(6 * np.pi * f * t))
        return lp(x, 4200) * env(d, 0.16)

    def pad(fs, d):
        t = t_(d)
        x = sum(np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 1.003 * t) for f in fs)
        a = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 0.6)
        return lp(x, 1500) * a / len(fs)

    t, b = 0.0, 0
    while t < dur - 0.5:
        raiz, ac = acordes[b % 4]
        add(out, pad([note(n) for n in ac], beat * 4), t, 0.18)
        for k in (0, 2):
            add(out, pluck(note(raiz), 0.7), t + beat * k, 0.5)
        for k in range(8):
            n = mel[(b * 8 + k) % len(mel)]
            if n and t > 0.2:
                add(out, pluck(note(n)), t + beat * k / 2, 0.22 if k % 2 == 0 else 0.15)
        t += beat * 4
        b += 1
    n = int(1.2 * SR)
    out[-n:] *= np.linspace(1, 0, n)
    return out


def sons():
    """Efeitos sincronizados com as peças (em tempo ORIGINAL; o warp da narração leva para o vídeo final)."""
    c = []
    for k in range(4):  # gancho: 1-2-3-cúpula
        c.append((0.6 + 0.55 * k + 0.2, "thud" if k < 3 else "clack", 0.9))
    for k in range(4):
        c.append((6.0 + 0.5 + 0.7 * k + 0.27, "clack", 0.8))
    c += [(12.5 + 2.6, "buzz", 0.5), (12.5 + 5.0, "clack", 0.7)]
    for t0 in (0.8, 2.5, 4.2):
        c.append((20.5 + t0 + 0.24, "thud", 0.9))
    c += [(27.5 + 0.9 + 0.27, "clack", 0.9), (27.5 + 1.6, "ding", 0.5)]
    c += [(34.0 + 1.75, "clack", 0.7), (34.0 + 2.0, "fanfare", 0.8), (34.0 + 4.6, "buzz", 0.4)]
    c += [(42.0, "chime", 0.6), (42.0 + 3.0 + 0.9, "whoosh", 0.5), (42.0 + 3.0 + 3.8 + 0.27, "clack", 0.9)]
    c += [(51.0 + 3.0, "pop", 0.6), (58.5 + 0.25, "whoosh", 0.5), (58.5 + 1.45, "ding", 0.5)]
    for a, _ in SCENES[1:]:
        c.append((a - 0.05, "whoosh", 0.35))
    return c


def audio(path, voz=None):
    import wave
    from audio import SR, add, FX
    dur = LINHA.warp(DUR) if LINHA.tl else DUR
    m = trilha(dur)
    m = m / (np.abs(m).max() + 1e-9) * 0.30
    s = np.zeros_like(m)
    for t0, nome, g in sons():
        add(s, FX[nome](), LINHA.warp(t0), g * 0.5)
    mix = m + s
    if voz:
        from audio import read_wav
        v = np.zeros_like(mix)
        for arq, t0 in voz:
            add(v, read_wav(arq), t0, 1.0)
        from audio import lp
        act = np.clip(lp(np.abs(v), 8) / (np.abs(v).max() * 0.15 + 1e-9), 0, 1)
        mix = mix * (1 - 0.6 * lp(lp(act, 3), 3)) + v
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.7
    st = np.repeat((mix * 32767).astype(np.int16)[:, None], 2, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(st.tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    ap.add_argument("--only", choices=["preview"])
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.frame:
        folha([quadro(int(x * FPS), True, SUBS).convert("RGB") for x in a.frame], os.path.join(OUT, "frames.jpg"))
        return
    n = int(DUR * FPS)
    wav = os.path.join(OUT, "previa.wav")
    audio(wav)
    out = os.path.join(OUT, "santorini_previa.mp4")
    motor.FPS = FPS
    _encode(out, [(k, True) for k in range(n)], wav)
    motor.previa_720p(out, os.path.join(OUT, "santorini_previa_720p.mp4"), 4500)


def _encode(out, args, wav):
    import subprocess
    from multiprocessing import Pool
    cmd = [motor.ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-framerate", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "17",
           "-r", "30", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for k, fr in enumerate(pool.imap(_render, args, chunksize=4)):
            p.stdin.write(fr)
            if k % 120 == 0:
                print(f"  quadro {k}/{len(args)}", flush=True)
    p.stdin.close()
    p.wait()
    print("ok:", out, flush=True)


if __name__ == "__main__":
    main()
