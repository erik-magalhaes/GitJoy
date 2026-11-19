#!/usr/bin/env python3
"""Reels "COMO SE JOGA METRO" (19/nov/2026, pedido dele: "faz um vídeo de como jogar Metro, pode fazer como se fosse uma
COLAGEM"). Edição deles: Calamity Games / Queen Games (2021), Dirk Henn; site: Família R$ 30, 2–6 jogadores, 30 min.

Visual COLAGEM PARISIENSE (diferente da colagem azul do Becas): papel verde-Guimard com grão, recortes de papel creme
rasgado com fibra branca, fita crepe, letras recortadas de revista, etiquetas datilografadas (Special Elite), anotação de
caneta (Permanent Marker), carimbos de borracha e caneta marca-texto traçando as linhas. Peças OFICIAIS do Board Game
Arena (tabuleiro, peças de trilho, vagões e fichas de estação; Real-ESRGAN x4 em assets/orig/*_x4.png) e a foto da caixa
do site. Tudo "pousa" em stop motion (12 poses/s, tremidinho leve).

Regras (manual via Board Game Arena, Gamehelpmetro): vagões nas estações da borda; na vez, joga a peça da mão OU compra
uma e joga essa (fica com a da mão); a peça encosta em outra peça ou na borda, setinha sempre pra cima; trilhos ligam
qualquer linha; linha que chega numa estação pontua 1 por peça atravessada (passou 2x = conta 2x); estação central
dobra; não pode fechar linha passando por UMA peça só, a não ser que não haja outro jeito; acabam as peças = mais pontos.

    /usr/bin/python3 metro.py --frame 1 6 12 ...   # out/frames_metro.jpg
    /usr/bin/python3 metro.py                      # out/metro_previa_final.mp4 (sem voz, legenda do roteiro)
"""
import argparse
import json
import math
import os
import random
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
for p in ("comum", "assinatura-reels", "listas-reels", "becas-reels", "promo"):
    sys.path.insert(0, os.path.join(REPO, p))
import estilo as E  # noqa: E402
import sons as S  # noqa: E402
from motor import encode, out_back  # noqa: E402
from base import final_loudness  # noqa: E402

W, H, FPS = 1080, 1920, 30
OUT = os.path.join(ROOT, "out")
ORIG = os.path.join(ROOT, "assets", "orig")
FD = os.path.join(REPO, "comum", "fontes")

VERDE, VERDE_C = (30, 74, 62), (46, 100, 84)
PAPEL, CREME = (236, 226, 204), (246, 240, 226)
MOST, VERM, PRETO = (222, 168, 58), (198, 52, 40), (26, 24, 22)
AZUL_L, LAR_L = (40, 120, 220), (240, 132, 30)

TEXTO = [
    "E se você tivesse que construir o metrô de Paris? Esse é o Metro, e eu vou te ensinar a jogar!",
    "Cada jogador coloca os seus vagões nas estações da borda do tabuleiro. Cada vagão é o começo de uma linha sua.",
    "Na sua vez, você joga a peça de trilho que está na sua mão... ou compra uma nova e joga essa.",
    "A peça vai do lado de outra peça ou da borda, sempre com a setinha pra cima. E os trilhos vão se ligando.",
    "Só que os trilhos não têm dono: a peça que você coloca pode esticar a sua linha... e a dos outros!",
    "Quando uma linha chega numa estação, ela fecha e pontua: um ponto pra cada peça que ela atravessou.",
    "E se ela chegar na estação central, os pontos dobram!",
    "Só não pode fechar uma linha com uma peça só, se tiver outra opção. Acabaram as peças? Ganha quem tiver mais pontos.",
    "Você fecharia a linha do seu amigo com dois pontinhos? Comenta aí! E aluga o Metro na Sua Vez, o link tá na bio.",
]
NOMES = ["gancho", "vagoes", "vez", "encaixe", "dono", "pontos", "central", "regra", "cta"]
T_COMENTA = 4.6  # dentro da cena final: até aqui é o "comenta", depois a tela final
TELA_FINAL = 3.4


def linha_do_tempo():
    tl = os.path.join(ROOT, "narracao", "timeline.json")
    if os.path.exists(tl) and "--previa" not in sys.argv:
        return json.load(open(tl))
    t, out = 0.0, []
    for k, n in enumerate(NOMES):
        d = max(4.2, len(TEXTO[k]) / 15.0 + 1.0)
        if n == "cta":
            d = max(d, T_COMENTA + TELA_FINAL)
        out.append({"cena": n, "ini": t, "dur": round(d, 2), "fala": None})
        t += d
    return out


TL = linha_do_tempo()
DUR = TL[-1]["ini"] + TL[-1]["dur"]


def cena_em(t):
    for c in TL:
        if t < c["ini"] + c["dur"] or c is TL[-1]:
            return c["cena"], t - c["ini"], c["dur"]


def seg(t, a, b):
    return min(1.0, max(0.0, (t - a) / (b - a))) if b > a else float(t >= a)


# ------------------------------------------------------------------------------------------------ utilidades
@lru_cache(None)
def F(nome, s):
    return ImageFont.truetype(os.path.join(FD, nome), int(s))


def ruido(w, h, escala, seed):
    rng = np.random.default_rng(seed)
    a = rng.random((h // escala + 2, w // escala + 2))
    im = Image.fromarray((a * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    return np.asarray(im, dtype=np.float32) / 255


def textura(w, h, cor, seed, forca=26):
    base = np.array(cor, np.float32)[None, None, :] * np.ones((h, w, 1), np.float32)
    n = (ruido(w, h, 70, seed) - 0.5) * forca + (ruido(w, h, 18, seed + 1) - 0.5) * forca * 0.6 + \
        (ruido(w, h, 3, seed + 2) - 0.5) * forca * 0.5
    return Image.fromarray(np.clip(base + n[..., None], 0, 255).astype(np.uint8)).convert("RGBA")


def sombra(im, r=12, off=(8, 12), a=130):
    sh = Image.new("RGBA", (im.width + 4 * r, im.height + 4 * r), (0, 0, 0, 0))
    m = im.getchannel("A").point(lambda v: v * a // 255)
    sh.paste((0, 0, 0, 255), (2 * r + off[0], 2 * r + off[1]), m)
    sh = sh.filter(ImageFilter.GaussianBlur(r))
    sh.alpha_composite(im, (2 * r, 2 * r))
    return sh


def tremor(t, k=0, amp=2.2):
    """Tremidinho de stop motion: muda 12 vezes por segundo."""
    q = int(t * 12)
    rnd = random.Random(q * 131 + k * 17)
    return rnd.uniform(-amp, amp), rnd.uniform(-amp, amp), rnd.uniform(-0.5, 0.5)


def cola(img, im, cx, cy, rot=0.0, esc=1.0, alpha=1.0):
    if esc <= 0.01 or alpha <= 0.01:
        return
    if esc != 1.0:
        im = im.resize((max(1, int(im.width * esc)), max(1, int(im.height * esc))), Image.LANCZOS)
    if rot:
        im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    if alpha < 1:
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    img.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def pousa(img, im, cx, cy, rot, t, t0, k=0, d=0.25):
    """Peça que cai do alto e pousa (stop motion: quadros a 12/s)."""
    if t < t0:
        return
    tq = math.floor(t * 12) / 12
    u = min(1.0, max(0.0, (tq - t0) / d))
    esc = 1.0 + 0.35 * (1 - u)
    a = min(1.0, u * 2.5)
    dx, dy, dr = tremor(t, k)
    cola(img, im, cx + dx, cy + dy - 60 * (1 - u), rot + dr + 6 * (1 - u), esc, a)


def rasgado(pts, seed, amp=10):
    rnd = random.Random(seed)
    out = []
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        n = max(2, int(math.dist((x0, y0), (x1, y1)) / 8))
        nx, ny = -(y1 - y0), (x1 - x0)
        L = math.hypot(nx, ny) or 1
        for k in range(n):
            t = k / n
            e = rnd.uniform(-amp, amp) * 0.5
            out.append((x0 + (x1 - x0) * t + nx / L * e, y0 + (y1 - y0) * t + ny / L * e))
    return out


@lru_cache(None)
def papel(w, h, seed, cor=PAPEL, borda=True):
    """Pedaço de papel rasgado (fibra branca na borda) com sombra."""
    m = Image.new("L", (w + 40, h + 40), 0)
    pts = rasgado([(20, 20), (w + 20, 20), (w + 20, h + 20), (20, h + 20), (20, 20)], seed, 12)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    out = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    if borda:
        out.paste((252, 250, 244, 255), (0, 0), m)
        m = m.filter(ImageFilter.MinFilter(7))
    tx = textura(w + 40, h + 40, cor, seed)
    out.paste(tx, (0, 0), m)
    return out


@lru_cache(None)
def fita(w=170, seed=0, cor=(232, 214, 160)):
    im = Image.new("RGBA", (w, 54), (0, 0, 0, 0))
    pts = rasgado([(0, 4), (w, 4)], seed, 4)[:-1] + [(w, 4)] + list(reversed(rasgado([(0, 50), (w, 50)], seed + 1, 4)))
    pts = [(x, y) for x, y in pts]
    ImageDraw.Draw(im).polygon(pts + [(0, 50)], fill=cor + (200,))
    tx = textura(w, 54, cor, seed + 9, 18)
    tx.putalpha(im.getchannel("A"))
    return tx


def recorte(im, borda=12, seed=0):
    """Imagem recortada com tesoura: borda branca irregular + sombra."""
    pad = borda + 8
    a = Image.new("L", (im.width + 2 * pad, im.height + 2 * pad), 0)
    a.paste(im.getchannel("A"), (pad, pad))
    b = a.filter(ImageFilter.MaxFilter(borda * 2 + 1 if borda * 2 + 1 <= 31 else 31))
    out = Image.new("RGBA", a.size, (0, 0, 0, 0))
    out.paste((252, 250, 244, 255), (0, 0), b)
    out.alpha_composite(im, (pad, pad))
    return sombra(out, 10, (7, 10), 120)


@lru_cache(None)
def letra(ch, i, s=150):
    fontes = ["Anton-Regular.ttf", "AbrilFatface-Regular.ttf", "ArchivoBlack-Regular.ttf", "DMSerifDisplay-Regular.ttf",
              "BebasNeue-Regular.ttf", "Shrikhand-Regular.ttf"]
    papeis = [(PAPEL, PRETO), (VERM, CREME), (PRETO, CREME), (MOST, PRETO), (CREME, VERM), ((198, 214, 200), PRETO),
              ((176, 200, 222), PRETO)]
    rnd = random.Random(i * 7 + ord(ch) * 3)
    f = F(fontes[rnd.randrange(len(fontes))], s * rnd.uniform(0.85, 1.1))
    fundo, cor = papeis[rnd.randrange(len(papeis))]
    bb = f.getbbox(ch)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    px, py = rnd.randint(12, 24), rnd.randint(12, 24)
    im = textura(w + 2 * px, h + 2 * py, fundo, i + 50, 22)
    ImageDraw.Draw(im).text((px - bb[0], py - bb[1]), ch, font=f, fill=cor)
    m = Image.new("L", im.size, 0)
    j = lambda: rnd.randint(0, 6)  # noqa: E731
    ImageDraw.Draw(m).polygon([(j(), j()), (im.width - j(), j()), (im.width - j(), im.height - j()),
                               (j(), im.height - j())], fill=255)
    im.putalpha(m)
    return sombra(im, 6, (5, 7), 140).rotate(rnd.uniform(-8, 8), expand=True, resample=Image.BICUBIC)


def titulo(img, txt, cx, cy, t, t0, s=150, larg=980, passo=0.09, seed=0):
    """Letras recortadas batendo uma a uma (12 poses/s)."""
    linhas = txt.split("\n")
    y = cy - (len(linhas) - 1) * s * 0.6
    n = 0
    for li, linha in enumerate(linhas):
        pecas = [letra(ch, seed + li * 40 + k, s) if ch != " " else None for k, ch in enumerate(linha)]
        tot = sum((p.width - 26 if p else s * 0.32) for p in pecas)
        esc = min(1.0, larg / tot)
        x = cx - tot * esc / 2
        for p in pecas:
            if p is None:
                x += s * 0.32 * esc
                continue
            ti = t0 + n * passo
            n += 1
            wq = (p.width - 26) * esc
            if t >= ti:
                tq = math.floor(t * 12) / 12
                u = min(1.0, max(0.0, (tq - ti) / 0.17))
                e = esc * (1 + 0.5 * (1 - u))
                dx, dy, _ = tremor(t, n, 1.5)
                cola(img, p, x + wq / 2 + dx, y + dy, 0, e, min(1, u * 2 + 0.3))
            x += wq
        y += s * 1.2


@lru_cache(None)
def etiqueta(txt, s=44, cor=CREME, fonte="SpecialElite-Regular.ttf", tinta=PRETO, seed=3, larg_max=900):
    """Tira de papel datilografada."""
    f = F(fonte, s)
    linhas = txt.split("\n")
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    while max(d0.textlength(l, font=f) for l in linhas) > larg_max - 60 and s > 20:
        s -= 2
        f = F(fonte, s)
    w = int(max(d0.textlength(l, font=f) for l in linhas)) + 60
    h = int(len(linhas) * s * 1.3) + 36
    p = papel(w, h, seed, cor).copy()
    d = ImageDraw.Draw(p)
    for k, l in enumerate(linhas):
        d.text((50, 38 + k * s * 1.3 + s * 0.55), l, font=f, fill=tinta, anchor="lm")
    return sombra(p, 8, (6, 9), 110)


def datilo(img, txt, cx, cy, t, t0, rot=0.0, s=44, cor=CREME, seed=3, cps=34):
    """Etiqueta que pousa e o texto vai sendo datilografado."""
    if t < t0:
        return
    full = etiqueta(txt, s, cor, seed=seed)
    n = int((t - t0) * cps)
    parcial = "\n".join(txt.split("\n"))
    tot = len(parcial.replace("\n", ""))
    if n < tot:
        cont, out = 0, []
        for l in parcial.split("\n"):
            q = max(0, min(len(l), n - cont))
            out.append(l[:q] + " " * (len(l) - q))
            cont += len(l)
        im = etiqueta("\n".join(out), s, cor, seed=seed)
        im = im.crop((0, 0, full.width, full.height)) if im.size != full.size else im
    else:
        im = full
    dx, dy, dr = tremor(t, seed, 1.2)
    cola(img, im, cx + dx, cy + dy, rot + dr)


@lru_cache(None)
def nota(txt, s=58, cor=VERM, larg=900):
    f = F("PermanentMarker-Regular.ttf", s)
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    linhas = txt.split("\n")
    w = int(max(d0.textlength(l, font=f) for l in linhas)) + 30
    h = int(len(linhas) * s * 1.25) + 30
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k, l in enumerate(linhas):
        d.text((w / 2, 15 + k * s * 1.25 + s * 0.6), l, font=f, fill=cor, anchor="mm")
    return im


def escreve(img, txt, cx, cy, t, t0, d=0.6, s=58, cor=VERM, rot=0.0):
    """Anotação de caneta que se revela da esquerda pra direita."""
    if t < t0:
        return
    im = nota(txt, s, cor)
    u = min(1.0, (t - t0) / d)
    if u < 1:
        im = im.copy()
        m = Image.new("L", im.size, 0)
        ImageDraw.Draw(m).rectangle((0, 0, int(im.width * u), im.height), fill=255)
        im.putalpha(Image.fromarray(np.minimum(np.array(im.getchannel("A")), np.array(m))))
    cola(img, im, cx, cy, rot)


@lru_cache(None)
def carimbo_img(txt, cor=VERM, s=80, redondo=False, sub=""):
    f = F("Anton-Regular.ttf", s)
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    tw = d0.textlength(txt, font=f)
    if redondo:
        r = int(max(tw / 2 + 40, s * 1.1))
        im = Image.new("RGBA", (2 * r + 20, 2 * r + 20), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.ellipse((10, 10, 2 * r + 10, 2 * r + 10), outline=cor, width=12)
        d.text((r + 10, r + 10 - (s * 0.15 if sub else 0)), txt, font=f, fill=cor, anchor="mm")
        if sub:
            d.text((r + 10, r + 10 + s * 0.65), sub, font=F("SpecialElite-Regular.ttf", s * 0.32), fill=cor, anchor="mm")
    else:
        w, h = int(tw + 70), int(s * 1.5)
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((5, 5, w - 5, h - 5), 14, outline=cor, width=9)
        d.text((w / 2, h / 2 + 2), txt, font=f, fill=cor, anchor="mm")
    a = np.array(im.getchannel("A")).astype(float)
    r = ruido(im.width, im.height, 3, len(txt))
    a *= np.clip((r - 0.08) * 2.4, 0.5, 1.0)
    im.putalpha(Image.fromarray(a.astype(np.uint8)))
    return im


def carimba(img, txt, cx, cy, t, t0, rot=-10, cor=VERM, s=80, redondo=False, sub=""):
    if t < t0:
        return
    u = min(1.0, (t - t0) / 0.12)
    cola(img, carimbo_img(txt, cor, s, redondo, sub), cx, cy, rot, 1.7 - 0.7 * u, 0.3 + 0.7 * u)


def seta(img, x0, y0, x1, y1, cor=VERM, w=10, u=1.0):
    """Seta de caneta."""
    if u <= 0:
        return
    d = ImageDraw.Draw(img)
    xe, ye = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
    d.line((x0, y0, xe, ye), fill=cor, width=w)
    if u >= 1:
        a = math.atan2(y1 - y0, x1 - x0)
        for da in (2.6, -2.6):
            d.line((x1, y1, x1 + 40 * math.cos(a + da), y1 + 40 * math.sin(a + da)), fill=cor, width=w)


# ------------------------------------------------------------------------------------------------ peças oficiais
def _abre(nome, fallback):
    p = os.path.join(ORIG, nome)
    return Image.open(p if os.path.exists(p) else os.path.join(ORIG, fallback))


@lru_cache(None)
def folha_pecas():
    im = _abre("tiles_x4.png", "tiles_rgb.png").convert("RGB")
    return im, im.width // 8


@lru_cache(None)
def peca(k, lado=250):
    im, c = folha_pecas()
    t = im.crop(((k % 8) * c, (k // 8) * c, (k % 8) * c + c, (k // 8) * c + c)).resize((lado, lado), Image.LANCZOS)
    t = t.convert("RGBA")
    d = ImageDraw.Draw(t)
    d.rectangle((0, 0, lado - 1, lado - 1), outline=(60, 44, 30, 255), width=2)
    return t


def chroma(im):
    a = np.array(im.convert("RGB")).astype(int)
    verde = (a[..., 1] > 150) & (a[..., 0] < 120) & (a[..., 2] < 120)
    al = np.where(verde, 0, 255).astype(np.uint8)
    out = im.convert("RGBA")
    out.putalpha(Image.fromarray(al).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8)))
    return out


CORES = ["azul", "verde", "roxo", "preto", "branco", "vermelho", "amarelo", "laranja"]


@lru_cache(None)
def vagao(cor, h=110):
    im = _abre("wagons_x4.png", "wagons_rgb.png")
    cw, ch = im.width / 8, im.height / 4
    k = CORES.index(cor)
    v = chroma(im.crop((int(k * cw), 0, int((k + 1) * cw), int(ch))))
    return v.resize((int(v.width * h / v.height), h), Image.LANCZOS)


@lru_cache(None)
def estacao(n, w=120):
    im = _abre("tokens_x4.png", "tokens_rgb.png")
    cw, ch = im.width / 10, im.height / 4
    k = n - 1
    c, r = k % 8, k // 8
    v = chroma(im.crop((int(c * cw), int(r * ch), int((c + 1) * cw), int((r + 1) * ch))))
    return v.resize((w, int(v.height * w / v.width)), Image.LANCZOS)


@lru_cache(None)
def central(lado=520):
    return peca(33, lado)


@lru_cache(None)
def verso(lado=250):
    return peca(32, lado)


@lru_cache(None)
def tabuleiro(lado=900):
    p = os.path.join(ORIG, "board_x4.png")
    im = Image.open(p if os.path.exists(p) else os.path.join(ORIG, "main_board_2.jpg")).convert("RGBA")
    return im.resize((lado, lado), Image.LANCZOS)


@lru_cache(None)
def caixa_foto(w=560):
    im = Image.open(os.path.join(ROOT, "assets", "caixa_site.jpg")).convert("RGBA")
    return im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)


@lru_cache(None)
def polaroide(w=560, seed=1):
    f = caixa_foto(w)
    m = 26
    im = textura(w + 2 * m, f.height + m + 110, CREME, seed, 10)
    im.alpha_composite(f, (m, m))
    return sombra(im, 12, (8, 12), 130)


# ------------------------------------------------------------------------------------------------ fundo
@lru_cache(None)
def fundo_base():
    img = textura(W, H, VERDE, 7, 30)
    d = ImageDraw.Draw(img)
    # linhas finas de "mapa" bem apagadas
    rnd = random.Random(5)
    for _ in range(26):
        x0, y0 = rnd.uniform(-200, W + 200), rnd.uniform(-200, H + 200)
        a = rnd.uniform(0, math.pi)
        L = rnd.uniform(400, 1400)
        d.line((x0, y0, x0 + L * math.cos(a), y0 + L * math.sin(a)), fill=VERDE_C + (255,), width=rnd.choice([3, 5, 8]))
    img = img.filter(ImageFilter.GaussianBlur(1.2))
    return img


def fundo():
    return fundo_base().copy()


# ------------------------------------------------------------------------------------------------ mini tabuleiro
CS = 250              # lado da casa no mini tabuleiro
GX, GY = 165, 650     # canto de cima à esquerda da grade 2x3 na tela
A_, B_ = 0.32, 0.675  # posições das pontas dos trilhos em cada lado da peça


@lru_cache(None)
def casa_vazia(seed):
    tb = tabuleiro(1600)
    x0 = 190 + (seed % 3) * 95   # só o "azul" do tabuleiro, longe da estação central
    y0 = 190 + (seed // 3) * 110
    return tb.crop((x0, y0, x0 + 190, y0 + 190)).resize((CS, CS), Image.LANCZOS)


@lru_cache(None)
def grade_base():
    w, h = 3 * CS, 2 * CS
    p = papel(w + 200, h + 220, 21, (214, 200, 172)).copy()
    for r in range(2):
        for c in range(3):
            p.alpha_composite(casa_vazia(r * 3 + c), (120 + c * CS, 130 + r * CS))
    d = ImageDraw.Draw(p)
    d.rectangle((120, 130, 120 + w, 130 + h), outline=(70, 52, 36, 255), width=4)
    return p


def pos(r, c, fx=0.5, fy=0.5):
    return GX + (c + fx) * CS, GY + (r + fy) * CS


def desenha_grade(img, t):
    g = grade_base()
    dx, dy, dr = tremor(t, 99, 1.0)
    img.alpha_composite(g, (int(GX - 120 - 20 + dx), int(GY - 130 - 20 + dy)))


def poe_peca(img, k, r, c, t, t0, kk=0):
    x, y = pos(r, c)
    if t < t0:
        return
    tq = math.floor(t * 12) / 12
    u = min(1.0, (tq - t0) / 0.25)
    sp = sombra(peca(k, CS), 8, (5, 8), 120) if u < 1 else sombra(peca(k, CS), 4, (2, 3), 90)
    dx, dy, dr = tremor(t, kk, 1.0) if u >= 1 else (0, 0, 0)
    cola(img, sp, x + dx + 3, y + dy - 70 * (1 - u) + 4, dr + 8 * (1 - u), 1 + 0.25 * (1 - u), min(1, u * 2 + 0.2))


def poe_estacao(img, n, x, y, t, t0, k=0):
    pousa(img, recorte(estacao(n, 112), 8, n), x, y, 0, t, t0, k)


def poe_vagao(img, cor, x, y, rot, t, t0, k=0, h=96):
    pousa(img, sombra(vagao(cor, h), 5, (3, 5), 120), x, y, rot, t, t0, k)


# estações do mini tabuleiro (posição do vagão/ficha na margem)
EST_AZUL = (GX - 70, GY + (1 + A_) * CS)          # esquerda da casa (1,0), ponta "a"
EST_LAR = (GX + A_ * CS, GY + 2 * CS + 70)        # embaixo da casa (1,0), ponta "a"
EST_FIM = (GX + (1 + A_) * CS, GY - 72)           # em cima da casa (0,1), ponta "a"
EST_C1 = (GX + A_ * CS, GY - 72)                  # em cima da casa (0,0)
EST_C2 = (GX - 70, GY + A_ * CS)                  # esquerda da casa (0,0)


def caminho_azul():
    """Linha azul: esquerda (1,0) → reta → curva em (1,1) (peça 17, canto de cima à esquerda) → sobe por (0,1)."""
    pts = [EST_AZUL, pos(1, 0, 0, A_), pos(1, 0, 1, A_)]
    cx, cy = pos(1, 1, 0, 0)
    r = A_ * CS
    pts += [(cx + r * math.sin(math.pi / 2 * k / 12), cy + r * math.cos(math.pi / 2 * k / 12)) for k in range(1, 13)]
    pts += [pos(0, 1, A_, 1), pos(0, 1, A_, 0), EST_FIM]
    return pts


def caminho_laranja():
    return [EST_LAR, pos(1, 0, A_, 1), pos(1, 0, A_, 0)]


def traco(img, pts, u, cor, w=22, alpha=170):
    """Marca-texto: percorre a polilinha até a fração u."""
    if u <= 0:
        return
    L = [0.0]
    for i in range(1, len(pts)):
        L.append(L[-1] + math.dist(pts[i - 1], pts[i]))
    alvo = L[-1] * min(1.0, u)
    out = [pts[0]]
    for i in range(1, len(pts)):
        if L[i] <= alvo:
            out.append(pts[i])
        else:
            f = (alvo - L[i - 1]) / (L[i] - L[i - 1])
            out.append((pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * f, pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * f))
            break
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.line(out, fill=cor + (alpha,), width=w, joint="curve")
    for p in (out[0], out[-1]):
        d.ellipse((p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2), fill=cor + (alpha,))
    img.alpha_composite(lay)
    return out[-1]


# ------------------------------------------------------------------------------------------------ cenas
def logo_marca(img):
    img.alpha_composite(E.logo(165), (W - 200, 42))


def cena_gancho(img, t, u, dur):
    datilo(img, "E SE VOCÊ CONSTRUÍSSE\nO METRÔ DE PARIS?", W / 2, 320, t, 0.0, -2, 60, MOST, seed=4, cps=110)
    titulo(img, "METRO", W / 2, 640, t, 0.55, 210, 900, 0.1, seed=11)
    pousa(img, polaroide(520, 2), W / 2 - 40, 1150, 4, t, 1.2, 3)
    if t >= 1.4:
        cola(img, fita(190, 1), W / 2 - 40, 900, -8)
    datilo(img, "COMO SE JOGA, NUM MINUTO", W / 2 + 120, 1500, t, 1.8, 3, 40, CREME, seed=6)


# estações da borda do tabuleiro em escala 0–1 (centro da ficha) e cores dos vagões
def est_borda(n):
    """Estações numeradas: 1–8 esquerda (de baixo pra cima), 9–16 em cima, 17–24 direita, 25–32 embaixo."""
    m, p0, dp = 0.045, 0.145, 0.101
    k = (n - 1) % 8
    if n <= 8:
        return m, p0 + (7 - k) * dp
    if n <= 16:
        return p0 + k * dp, m
    if n <= 24:
        return 1 - m, p0 + k * dp
    return p0 + (7 - k) * dp, 1 - m


VAGOES = [(2, "azul"), (5, "laranja"), (11, "verde"), (14, "azul"), (19, "laranja"), (22, "verde"), (27, "azul"),
          (30, "laranja"), (7, "verde"), (16, "laranja")]


def cena_vagoes(img, t, u, dur):
    t0 = TL[1]["ini"]
    lado = 920
    x0, y0 = (W - lado) / 2, 520
    dx, dy, dr = tremor(t, 7, 1.0)
    tb = papel(lado, lado, 31, PAPEL, True)
    img.alpha_composite(sombra(tb, 12, (8, 12), 120), (int(x0 - 44 + dx), int(y0 - 44 + dy)))
    img.alpha_composite(tabuleiro(lado - 30), (int(x0 + 15 + dx), int(y0 + 15 + dy)))
    for j, (n, cor) in enumerate(VAGOES):
        fx, fy = est_borda(n)
        poe_vagao(img, cor, x0 + 15 + fx * (lado - 30), y0 + 15 + fy * (lado - 30), 0, t, t0 + 0.6 + j * 0.28, j, 124)
    datilo(img, "CADA VAGÃO = O COMEÇO\nDE UMA LINHA SUA", W / 2, 330, t, t0 + 0.1, -2, 46, MOST, seed=8)
    escreve(img, "estações da borda!", W / 2, 1530, t, t0 + 0.9 + 0.28 * len(VAGOES), 0.7, 60, CREME, -3)


def cena_vez(img, t, u, dur):
    datilo(img, "NA SUA VEZ:", W / 2, 300, t, TL[2]["ini"], -2, 54, MOST, seed=9)
    # 1: a peça da mão
    p1 = papel(400, 470, 41, CREME)
    cola(img, sombra(p1, 10, (7, 10), 110), 280, 820, -3)
    cola(img, nota("SUA MÃO", 54, PRETO), 280, 640, -3)
    a = seg(u, 0.12, 0.42)
    cola(img, sombra(peca(4, 260), 8, (5, 8), 120), 280, 860 - 120 * math.sin(a * math.pi) * 0, -3 + 2 * a)
    carimba(img, "1", 120, 1010, u * dur, 0.4, -8, VERM, 90, True)
    # 2: compra do monte
    p2 = papel(400, 470, 43, CREME)
    cola(img, sombra(p2, 10, (7, 10), 110), 800, 820, 3)
    cola(img, nota("MONTE", 54, PRETO), 800, 640, 3)
    for k in range(4):
        cola(img, sombra(verso(240), 6, (4, 6), 110), 800 - k * 5, 880 - k * 9, 3)
    escreve(img, "OU", W / 2 + 10, 860, u * dur, dur * 0.35, 0.3, 90, VERM, 0)
    b = seg(u, 0.5, 0.72)
    if b > 0:
        x = 800 + (W / 2 - 800) * b
        y = 840 + (1300 - 840) * b
        lado = 240 + 40 * b
        k = peca(11, int(lado)) if b > 0.5 else verso(int(lado))
        sx = abs(math.cos(b * math.pi))
        ims = k.resize((max(1, int(k.width * max(0.08, sx))), k.height), Image.LANCZOS)
        cola(img, sombra(ims, 8, (5, 8), 120), x, y, -4 * b)
    carimba(img, "2", 960, 1010, u * dur, dur * 0.48, 8, VERM, 90, True)
    datilo(img, "COMPROU? JOGA ESSA!\n(a da mão fica com você)", W / 2, 1530, t, TL[2]["ini"] + dur * 0.75, 2, 40,
           CREME, seed=12)


SEQ = [(18, 1, 0), (17, 1, 1), (15, 0, 1)]  # (peça, linha, coluna) do exemplo


def base_mini(img, t, t_est=0.0, com_lar=True):
    desenha_grade(img, t)
    poe_estacao(img, 3, EST_AZUL[0] - 2, EST_AZUL[1], t, t_est, 1)
    poe_vagao(img, "azul", EST_AZUL[0] + 30, EST_AZUL[1], -90, t, t_est + 0.1, 2)
    poe_estacao(img, 12, EST_FIM[0], EST_FIM[1] - 4, t, t_est + 0.15, 3)
    if com_lar:
        poe_estacao(img, 29, EST_LAR[0], EST_LAR[1] + 4, t, t_est + 0.2, 4)
        poe_vagao(img, "laranja", EST_LAR[0], EST_LAR[1] - 26, 0, t, t_est + 0.3, 5)


def cena_encaixe(img, t, u, dur):
    t0 = TL[3]["ini"]
    datilo(img, "A PEÇA ENCOSTA EM OUTRA\nPEÇA OU NA BORDA", W / 2, 330, t, t0, -2, 46, MOST, seed=14)
    base_mini(img, t, t0 + 0.1, com_lar=False)
    tz = [t0 + dur * f for f in (0.18, 0.38, 0.58)]
    for j, (k, r, c) in enumerate(SEQ):
        poe_peca(img, k, r, c, t, tz[j], 30 + j)
    # setinha da peça (canto de baixo à direita da peça)
    if t > tz[0] + 0.4:
        x, y = pos(1, 0, 0.88, 0.86)
        d = ImageDraw.Draw(img)
        d.ellipse((x - 46, y - 46, x + 46, y + 46), outline=VERM, width=8)
        escreve(img, "setinha\npra cima!", x + 130, y + 210, t, tz[0] + 0.5, 0.5, 52, VERM, -6)
        seta(img, x + 90, y + 140, x + 40, y + 50, VERM, 8, seg(t, tz[0] + 0.9, tz[0] + 1.1))
    if u > 0.75:
        escreve(img, "os trilhos se ligam!", W / 2, 1520, t, t0 + dur * 0.75, 0.6, 58, CREME, -2)


def cena_dono(img, t, u, dur):
    t0 = TL[4]["ini"]
    datilo(img, "OS TRILHOS NÃO TÊM DONO!", W / 2, 330, t, t0, -2, 50, MOST, seed=16)
    base_mini(img, t, t0 - 10, com_lar=True)
    poe_peca(img, 18, 1, 0, t, t0 + 0.4, 40)
    traco(img, [EST_AZUL, pos(1, 0, 0, A_), pos(1, 0, 1, A_)], seg(u, 0.3, 0.5), AZUL_L)
    traco(img, caminho_laranja(), seg(u, 0.55, 0.72), LAR_L)
    if u > 0.74:
        escreve(img, "a mesma peça ajudou\nas duas linhas!", W / 2 + 120, 1500, t, t0 + dur * 0.74, 0.7, 54, CREME, -3)


def cena_pontos(img, t, u, dur):
    t0 = TL[5]["ini"]
    datilo(img, "CHEGOU NA ESTAÇÃO?\n1 PONTO POR PEÇA!", W / 2, 330, t, t0, -2, 48, MOST, seed=18)
    base_mini(img, t, t0 - 10, com_lar=False)
    for j, (k, r, c) in enumerate(SEQ):
        poe_peca(img, k, r, c, t, t0 - 10, 30 + j)
    pts = caminho_azul()
    traco(img, pts, seg(u, 0.12, 0.62), AZUL_L)
    # contagem: 1, 2, 3 quando a linha passa por cada peça
    marcas = [(0.2, pos(1, 0, 0.5, 0.72)), (0.36, pos(1, 1, 0.55, 0.62)), (0.52, pos(0, 1, 0.72, 0.5))]
    for j, (f, (x, y)) in enumerate(marcas):
        carimba(img, str(j + 1), x, y, u * dur, dur * f, -8 + 6 * j, PRETO, 70, True)
    carimba(img, "+3 PONTOS", W / 2 + 160, 1440, u * dur, dur * 0.68, -9, VERM, 96)


def cena_central(img, t, u, dur):
    t0 = TL[6]["ini"]
    datilo(img, "ESTAÇÃO CENTRAL", W / 2, 330, t, t0, -2, 54, MOST, seed=20)
    cx, cy = W / 2, 900
    pousa(img, recorte(central(560), 14, 3), cx, cy, -2, t, t0 + 0.1, 50)
    traco(img, [(80, cy - 140), (cx - 300, cy - 140), (cx - 230, cy - 140)], seg(u, 0.15, 0.4), AZUL_L, 24)
    carimba(img, "x2", cx + 230, cy + 260, u * dur, dur * 0.42, -12, VERM, 190, True)
    datilo(img, "3 PEÇAS x 2 = 6 PONTOS", W / 2, 1450, t, t0 + dur * 0.6, 2, 46, CREME, seed=22)


def cena_regra(img, t, u, dur):
    t0 = TL[7]["ini"]
    if u < 0.55:
        datilo(img, "PROIBIDO:", W / 2, 330, t, t0, -2, 56, MOST, seed=24)
        desenha_grade(img, t)
        poe_estacao(img, 9, EST_C1[0], EST_C1[1] - 4, t, t0, 61)
        poe_estacao(img, 6, EST_C2[0] - 2, EST_C2[1], t, t0 + 0.1, 62)
        poe_vagao(img, "azul", EST_C2[0] + 30, EST_C2[1], -90, t, t0 + 0.15, 63)
        poe_peca(img, 17, 0, 0, t, t0 + 0.3, 64)
        cx, cy = pos(0, 0, 0, 0)
        arco = [EST_C2, pos(0, 0, 0, A_)] + [(cx + A_ * CS * math.sin(math.pi / 2 * k / 12),
                                              cy + A_ * CS * math.cos(math.pi / 2 * k / 12)) for k in range(13)] + \
               [pos(0, 0, A_, 0), EST_C1]
        traco(img, arco, seg(u, 0.1, 0.25), AZUL_L)
        if u > 0.27:
            x, y = pos(0, 0)
            d = ImageDraw.Draw(img)
            k = min(1.0, (u - 0.27) / 0.06)
            d.line((x - 150, y - 150, x - 150 + 300 * k, y - 150 + 300 * k), fill=VERM, width=26)
            if u > 0.33:
                k2 = min(1.0, (u - 0.33) / 0.06)
                d.line((x + 150, y - 150, x + 150 - 300 * k2, y - 150 + 300 * k2), fill=VERM, width=26)
        carimba(img, "LINHA DE 1 PEÇA SÓ", W / 2 + 40, 1290, u * dur, dur * 0.36, -6, VERM, 70)
        escreve(img, "(a não ser que não\ntenha outro jeito)", W / 2 + 40, 1480, t, t0 + dur * 0.42, 0.6, 50, CREME, -2)
    else:
        v = (u - 0.55) / 0.45
        datilo(img, "ACABARAM AS PEÇAS?", W / 2, 330, t, t0 + dur * 0.55, -2, 54, MOST, seed=26)
        p = papel(640, 640, 51, CREME)
        cola(img, sombra(p, 10, (7, 10), 110), W / 2, 900, 2)
        d = ImageDraw.Draw(img)
        linhas = [("azul", "AZUL", "34"), ("laranja", "LARANJA", "29"), ("verde", "VERDE", "27")]
        for j, (cor, nm, pt) in enumerate(linhas):
            if v > 0.1 + j * 0.15:
                y = 720 + j * 150
                cola(img, vagao(cor, 90), W / 2 - 200, y, 0)
                d.text((W / 2 - 120, y), nm, font=F("SpecialElite-Regular.ttf", 58), fill=PRETO, anchor="lm")
                d.text((W / 2 + 230, y), pt, font=F("SpecialElite-Regular.ttf", 64), fill=PRETO, anchor="rm")
        if v > 0.6:
            k = min(1.0, (v - 0.6) / 0.15)
            d.ellipse((W / 2 + 120, 660, W / 2 + 280, 790), outline=VERM, width=9) if k >= 1 else None
        carimba(img, "MAIS PONTOS GANHA!", W / 2, 1380, u * dur, dur * (0.55 + 0.45 * 0.62), -5, VERM, 84)


def cena_cta(img, t, u, dur):
    t0 = TL[8]["ini"]
    if u * dur < T_COMENTA:
        titulo(img, "COMENTA\nAÍ!", W / 2, 640, t, t0 + 0.1, 170, 900, 0.07, seed=71)
        datilo(img, "Você fecharia a linha do seu\namigo com dois pontinhos?", W / 2, 1080, t, t0 + 0.9, 2, 46,
               CREME, seed=28)
        pousa(img, recorte(peca(16, 230), 10, 4), 250, 1400, -10, t, t0 + 1.4, 81)
        pousa(img, sombra(vagao("laranja", 150), 6, (4, 6), 120), 820, 1380, 12, t, t0 + 1.6, 82)
        return
    # tela final
    tf = t0 + T_COMENTA
    cola(img, E.logo(260), W / 2, 190, 0)
    titulo(img, "ALUGUE O METRO", W / 2, 420, t, tf + 0.1, 112, 980, 0.04, seed=91)
    pousa(img, polaroide(400, 5), W / 2, 850, -4, t, tf + 0.3, 91)
    if t >= tf + 0.5:
        cola(img, fita(170, 6), W / 2 - 10, 585, 5)
    datilo(img, "2 a 6 jogadores · 30 min · 5 dias de jogo", W / 2, 1255, t, tf + 0.5, -2, 40, CREME, seed=30, cps=90)
    datilo(img, "RESERVE ONLINE · RETIRE EM MAUÁ\nOU RECEBA EM CASA", W / 2, 1385, t, tf + 0.8, 2, 40, MOST, seed=32,
           cps=90)
    carimba(img, "LINK NA BIO · @SUAVEZ_BG", W / 2, 1530, t, tf + 1.2, -3, VERM, 60)


CENA_FN = {"gancho": cena_gancho, "vagoes": cena_vagoes, "vez": cena_vez, "encaixe": cena_encaixe,
           "dono": cena_dono, "pontos": cena_pontos, "central": cena_central, "regra": cena_regra, "cta": cena_cta}


def legenda(img, t):
    if "--sem-legenda" in sys.argv:
        return
    cena, u, dur = cena_em(t)
    k = NOMES.index(cena)
    c = TL[k]
    if c.get("palavras"):
        pal = [p for p in c["palavras"] if p["ini"] <= t]
        if not pal:
            return
        txts = [p["w"] for p in c["palavras"]]
        ini = ((len(pal) - 1) // 5) * 5
        txt = " ".join(txts[ini:ini + 5])
    else:
        palavras = TEXTO[k].split()
        n = math.ceil(len(palavras) / 5)
        j = min(n - 1, int(u / dur * n))
        txt = " ".join(palavras[j * 5:(j + 1) * 5])
    f = F("Anton-Regular.ttf", 56)
    d = ImageDraw.Draw(img)
    d.text((W / 2, 1735), txt.upper(), font=f, fill="white", anchor="mm", stroke_width=6, stroke_fill="black")


def quadro(t):
    cena, u, dur = cena_em(t)
    img = fundo()
    CENA_FN[cena](img, t, u / dur, dur)
    # transição: rasgo de papel creme passando nas emendas
    for c in TL[1:]:
        dd = t - c["ini"]
        if -0.16 < dd < 0.16:
            v = (dd + 0.16) / 0.32
            x = -W * 0.3 + v * W * 1.6
            m = Image.new("L", (W, H), 0)
            pts = rasgado([(x - 700, -40), (x - 300, H + 40)], int(c["ini"] * 10), 30)
            ImageDraw.Draw(m).polygon([(-W, -40)] + pts + [(-W, H + 40)], fill=255)
            img.paste(textura(W, H, PAPEL, 3, 20), (0, 0), m)
    final = cena == "cta" and u >= T_COMENTA
    if not final:
        logo_marca(img)
    legenda(img, t)
    return img.convert("RGB")


def render(fi):
    return quadro(fi / FPS).tobytes()


# ------------------------------------------------------------------------------------------------ som
SR = S.SR


def acordeao(f, d):
    t = np.arange(int(d * SR)) / SR
    x = sum(np.sign(np.sin(2 * np.pi * f * dt * t)) * 0.3 + np.sin(2 * np.pi * f * dt * t)
            for dt in (1.0, 1.004, 0.996))
    x = S.lp_fft(x, 2600)
    env = np.minimum(1, t / 0.03) * np.minimum(1, (d - t) / 0.06) * (0.85 + 0.15 * np.sin(2 * np.pi * 5.5 * t))
    return x * env * 0.18


def trilha(dur):
    """Valsa musette (acordeão, baixo e acordes em 3/4), em loop, sem direitos."""
    out = np.zeros(int((dur + 1) * SR))
    bpm = 168
    b = 60 / bpm
    prog = [("C3", ["E4", "G4", "C5"]), ("G2", ["D4", "F4", "B4"]), ("G2", ["D4", "F4", "B4"]), ("C3", ["E4", "G4", "C5"]),
            ("F2", ["F4", "A4", "C5"]), ("C3", ["E4", "G4", "C5"]), ("G2", ["D4", "G4", "B4"]), ("C3", ["E4", "G4", "C5"])]
    mel = ["E5", "D5", "C5", "G4", "A4", "B4", "C5", "D5", "E5", "F5", "E5", "D5", "C5", "B4", "D5", "C5"]
    n = int(dur / (3 * b)) + 1
    for k in range(n):
        t0 = k * 3 * b
        baixo, ac = prog[k % len(prog)]
        S.add(out, S.baixo(S.hz(baixo), b * 0.9), t0, 0.55)
        for j in (1, 2):
            for nt in ac:
                S.add(out, acordeao(S.hz(nt), b * 0.6), t0 + j * b, 0.22)
        if k >= 2:
            S.add(out, acordeao(S.hz(mel[(2 * k) % len(mel)]), b * 1.9), t0, 0.5)
            S.add(out, acordeao(S.hz(mel[(2 * k + 1) % len(mel)]), b * 0.9), t0 + 2 * b, 0.45)
    return out[:int(dur * SR)]


def cues():
    ev = []
    for c in TL:
        i, d, n = c["ini"], c["dur"], c["cena"]
        if i > 0:
            ev.append((i - 0.12, S.rasgo(0.35), 0.4))
        if n == "gancho":
            ev += [(0.05, S.tecla(), 0.3)] + [(0.55 + j * 0.1, S.tesoura(), 0.25) for j in range(5)]
            ev += [(1.2, S.cartao(), 0.4), (1.45, S.fita(), 0.35)]
        if n == "vagoes":
            ev += [(i + 0.6 + j * 0.28, S.tic(), 0.35) for j in range(len(VAGOES))]
        if n == "vez":
            ev += [(i + 0.4, S.estouro(), 0.3), (i + d * 0.48, S.estouro(), 0.3), (i + d * 0.5, S.carta_vira(), 0.4)]
        if n == "encaixe":
            ev += [(i + d * f + 0.2, S.cartao(), 0.5) for f in (0.18, 0.38, 0.58)]
        if n == "dono":
            ev += [(i + 0.6, S.cartao(), 0.5), (i + d * 0.3, S.arrasta(d * 0.2), 0.3), (i + d * 0.55, S.arrasta(d * 0.17), 0.3)]
        if n == "pontos":
            ev += [(i + d * 0.12, S.arrasta(d * 0.5), 0.3)] + [(i + d * f, S.estouro(), 0.35) for f in (0.2, 0.36, 0.52)]
            ev += [(i + d * 0.68, S.estouro(), 0.5), (i + d * 0.7, S.plim(), 0.4)]
        if n == "central":
            ev += [(i + 0.1, S.cartao(), 0.4), (i + d * 0.42, S.estouro(), 0.6), (i + d * 0.44, S.sino(), 0.4)]
        if n == "regra":
            ev += [(i + d * 0.3, S.rasgo(0.25), 0.4), (i + d * 0.36, S.estouro(), 0.5), (i + d * 0.83, S.estouro(), 0.5),
                   (i + d * 0.85, S.plim(), 0.4)]
        if n == "cta":
            ev += [(i + 0.1 + j * 0.07, S.tesoura(), 0.2) for j in range(8)]
            ev += [(i + T_COMENTA, S.rasgo(0.4), 0.4), (i + T_COMENTA + 0.9, S.estouro(), 0.5)]
    return ev


def audio(nome):
    com = os.path.join(OUT, f"{nome}_com.wav")
    sem = os.path.join(OUT, f"{nome}_sem.wav")
    S.grava(com, DUR, cues(), trilha(DUR + 0.5), musica_ganho=0.34, fx_ganho=0.8)
    S.grava(sem, DUR, cues(), None, fx_ganho=0.8)
    return com, sem


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    ap.add_argument("--previa", action="store_true")
    ap.add_argument("--sem-legenda", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.frame:
        ims = [quadro(x) for x in a.frame]
        cols = min(5, len(ims))
        rows = math.ceil(len(ims) / cols)
        sh = Image.new("RGB", (360 * cols, 640 * rows))
        for k, im in enumerate(ims):
            sh.paste(im.resize((360, 640), Image.LANCZOS), (360 * (k % cols), 640 * (k // cols)))
        sh.save(os.path.join(OUT, "frames_metro.jpg"), quality=88)
        print("ok", DUR)
        return
    nome = "metro_previa"
    com, sem = audio(nome)
    n = int(round(DUR * FPS))
    base = os.path.join(OUT, f"{nome}.mp4")
    encode(base, render, list(range(n)), com)
    final_loudness(base, base.replace(".mp4", "_final.mp4"))
    print("ok", DUR)


if __name__ == "__main__":
    main()
