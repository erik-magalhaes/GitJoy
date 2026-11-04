#!/usr/bin/env python3
"""Convite da TARDE DE JOGOS NO BECAS no estilo das referências que ele mandou em 4/nov/2026 (Pinterest):
"GAMES DAY!" (moldura de casas de tabuleiro verde-água / mostarda / creme em volta de um miolo bordô, figurinhas retrô
com contorno escuro e sombra deslocada: explosão, raio, cartas, dados) + "GAME NIGHT" retrô anos 60 (grão, estrelas
atômicas, letras condensadas creme e mostarda). As figurinhas são formas simples desenhadas (nada de meeple/peão à mão);
nas casas também entram as CAIXAS do acervo como adesivos e um guarda-chuvinha do Becas.

    /usr/bin/python3 gamesday.py              # out/gamesday/post_1080x1350.png, story_1080x1920.png, folha.jpg
    /usr/bin/python3 gamesday.py --reels      # out/gamesday_{com_som,para_musica}_final.mp4
    /usr/bin/python3 gamesday.py --frame 1 4 9 16 22
"""
import math
import os
import random
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import kit as K
import sons as S
import estilos as ST
from kit import E, TB

OUT = os.path.join(K.OUT, "gamesday")
FD = os.path.join(K.REPO, "comum", "fontes")
BORDO, BORDO2 = (92, 16, 16), (70, 10, 12)
VERDE, MOSTARDA, CREME, LARANJA = (67, 190, 143), (245, 196, 92), (250, 226, 170), (236, 120, 44)
TINTA = (44, 10, 10)           # contorno das figurinhas
ROXO = (96, 70, 170)
CREME_TXT = (247, 228, 190)
WHATS = TB.WHATS


@lru_cache(None)
def F(nome, s, peso=None):
    f = ImageFont.truetype(os.path.join(FD, nome), int(s))
    if peso:
        f.set_variation_by_axes(list(peso))
    return f


def grao(img, amp=14, seed=3):
    a = np.asarray(img.convert("RGB"), np.int16)
    n = np.random.default_rng(seed).integers(-amp, amp + 1, a.shape[:2], dtype=np.int16)
    a = np.clip(a + n[..., None], 0, 255).astype(np.uint8)
    return Image.fromarray(a).convert("RGBA")


# ---------------------------------------------------------------- figurinhas (contorno escuro + sombra deslocada)
def figurinha(desenho, w, h, sombra=(10, 12)):
    """desenho(d, ox, oy) desenha a forma; aqui vira contorno + sombra sólida em TINTA."""
    im = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    desenho(ImageDraw.Draw(im), 20, 20)
    a = im.getchannel("A")
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.paste(TINTA + (255,), sombra, a)
    sh.alpha_composite(im)
    return sh


@lru_cache(None)
def explosao(r=120, cor=LARANJA, cor2=(250, 160, 70), n=9, seed=1):
    rnd = random.Random(seed)
    pts = []
    for k in range(2 * n):
        rr = (r if k % 2 == 0 else r * 0.45) * rnd.uniform(0.82, 1.0)
        a = math.pi * k / n + rnd.uniform(-0.08, 0.08)
        pts.append((rr * math.cos(a), rr * math.sin(a)))

    def des(d, ox, oy):
        P = [(x + r + ox, y + r + oy) for x, y in pts]
        d.polygon(P, fill=cor, outline=TINTA, width=7)
        P2 = [(x * 0.62 + r + ox, y * 0.62 + r + oy) for x, y in pts]
        d.polygon(P2, fill=cor2)
    return figurinha(des, 2 * r, 2 * r)


@lru_cache(None)
def raio(h=200, cor=(226, 82, 52)):
    s = h / 200
    pts = [(70, 0), (150, 0), (110, 80), (160, 80), (40, 200), (75, 105), (25, 105)]
    lado = [(x + 14, y + 10) for x, y in pts]

    def des(d, ox, oy):
        d.polygon([(x * s + ox, y * s + oy) for x, y in lado], fill=VERDE, outline=TINTA, width=6)
        d.polygon([(x * s + ox, y * s + oy) for x, y in pts], fill=cor, outline=TINTA, width=7)
    return figurinha(des, int(175 * s), int(215 * s))


@lru_cache(None)
def carta(h=220, naipe="♠", cor_naipe=TINTA):
    w = int(h * 0.7)
    fn = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(h * 0.38))
    fs = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(h * 0.12))

    def des(d, ox, oy):
        d.rounded_rectangle((ox, oy, ox + w, oy + h), int(h * 0.09), fill=MOSTARDA, outline=ROXO, width=8)
        d.ellipse((ox + w * 0.35, oy + h * 0.1, ox + w * 1.3, oy + h * 0.95), fill=(240, 170, 60))
        d.rounded_rectangle((ox, oy, ox + w, oy + h), int(h * 0.09), outline=ROXO, width=8)
        d.text((ox + w / 2, oy + h / 2), naipe, font=fn, fill=cor_naipe, anchor="mm")
        d.text((ox + w * 0.17, oy + h * 0.13), "A", font=fs, fill=cor_naipe, anchor="mm")
    return figurinha(des, w, h, (8, 10))


@lru_cache(None)
def dado3d(s=150, seed=2):
    """Cubo em perspectiva (3 faces) com pintas, creme com contorno escuro."""
    a = s * 0.5

    def des(d, ox, oy):
        cx, cy = ox + s * 0.55, oy + s * 0.5
        top = [(cx, cy - a), (cx + a * 0.95, cy - a * 0.5), (cx, cy), (cx - a * 0.95, cy - a * 0.5)]
        esq = [(cx - a * 0.95, cy - a * 0.5), (cx, cy), (cx, cy + a), (cx - a * 0.95, cy + a * 0.5)]
        dir_ = [(cx, cy), (cx + a * 0.95, cy - a * 0.5), (cx + a * 0.95, cy + a * 0.5), (cx, cy + a)]
        d.polygon(top, fill=(252, 240, 220), outline=TINTA, width=6)
        d.polygon(esq, fill=(246, 222, 190), outline=TINTA, width=6)
        d.polygon(dir_, fill=(232, 196, 160), outline=TINTA, width=6)
        r = s * 0.055

        def pinta(face, u, v):
            p0, p1, p3 = face[0], face[1], face[3]
            x = p0[0] + (p1[0] - p0[0]) * u + (p3[0] - p0[0]) * v
            y = p0[1] + (p1[1] - p0[1]) * u + (p3[1] - p0[1]) * v
            d.ellipse((x - r, y - r * 0.8, x + r, y + r * 0.8), fill=TINTA)
        for u, v in ((.5, .5),):
            pinta(top, u, v)
        for u, v in ((.3, .3), (.7, .7)):
            pinta(esq, u, v)
        for u, v in ((.27, .27), (.73, .27), (.5, .5), (.27, .73), (.73, .73)):
            pinta(dir_, u, v)
    return figurinha(des, int(s * 1.1), int(s * 1.05), (8, 10))


@lru_cache(None)
def estrela_atomica(r=70, cor=CREME, n=8):
    im = Image.new("RGBA", (2 * r + 10, 2 * r + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k in range(n):
        a = math.pi * k / n
        rr = r if k % 2 == 0 else r * 0.6
        d.line((r + 5 - rr * math.cos(a), r + 5 - rr * math.sin(a), r + 5 + rr * math.cos(a),
                r + 5 + rr * math.sin(a)), fill=cor, width=5)
    d.ellipse((r - 6, r - 6, r + 16, r + 16), fill=cor)
    return im


@lru_cache(None)
def xicara(s=170):
    def des(d, ox, oy):
        d.ellipse((ox, oy + s * 0.72, ox + s * 1.1, oy + s * 0.98), fill=CREME, outline=TINTA, width=6)  # pires
        d.rounded_rectangle((ox + s * 0.15, oy + s * 0.25, ox + s * 0.85, oy + s * 0.85), int(s * 0.18),
                            fill=(46, 150, 140), outline=TINTA, width=7)
        d.arc((ox + s * 0.72, oy + s * 0.35, ox + s * 1.08, oy + s * 0.68), -90, 90, fill=TINTA, width=14)
        d.ellipse((ox + s * 0.15, oy + s * 0.18, ox + s * 0.85, oy + s * 0.36), fill=(120, 70, 40), outline=TINTA,
                  width=6)
        for k in range(3):  # vapor
            x = ox + s * (0.32 + 0.18 * k)
            d.arc((x - 18, oy - s * 0.12, x + 18, oy + s * 0.12), 90, 270, fill=CREME, width=6)
    return figurinha(des, int(s * 1.15), int(s * 1.0))


@lru_cache(None)
def guarda(s=170):
    g = TB.guarda_chuva(s, LARANJA, 0)
    return g


@lru_cache(None)
def caixa_adesivo(nome, h=170, rot=0):
    cx = Image.open(os.path.join(K.REPO, "hobby-reels", "assets", "acervo", nome + ".png")).convert("RGBA")
    cx = cx.crop(cx.getbbox())
    s = h / cx.height
    cx = cx.resize((int(cx.width * s), h), Image.LANCZOS)
    a = cx.getchannel("A").filter(ImageFilter.MaxFilter(13))  # borda branca de adesivo
    base = Image.new("RGBA", (cx.width + 16, cx.height + 16), (0, 0, 0, 0))
    base.paste((255, 250, 240, 255), (2, 2), a.resize((cx.width + 12, cx.height + 12)))
    base.alpha_composite(cx, (8, 8))
    sh = Image.new("RGBA", (base.width + 14, base.height + 14), (0, 0, 0, 0))
    sh.paste(TINTA + (255,), (10, 12), base.getchannel("A"))
    sh.alpha_composite(base)
    return sh.rotate(rot, expand=True, resample=Image.BICUBIC)


FIGS = {"explosao": lambda: explosao(), "raio": lambda: raio(), "carta1": lambda: carta(230, "♠"),
        "carta2": lambda: carta(230, "♦", (210, 60, 40)), "carta3": lambda: carta(220, "♣"),
        "dado": lambda: dado3d(), "dado2": lambda: dado3d(130, 5), "xicara": lambda: xicara(),
        "guarda": lambda: guarda(), "explosao2": lambda: explosao(95, VERDE, (140, 230, 190), 8, 4)}


# ---------------------------------------------------------------- o tabuleiro (moldura de casas + miolo bordô)
def casas_borda(cols, rows):
    out = []
    for c in range(cols):
        out.append((c, 0))
    for r in range(1, rows):
        out.append((cols - 1, r))
    for c in range(cols - 2, -1, -1):
        out.append((c, rows - 1))
    for r in range(rows - 2, 0, -1):
        out.append((0, r))
    return out


def geometria(W, H, cols, rows, m=40):
    cw, ch = (W - 2 * m) / cols, (H - 2 * m) / rows
    return m, cw, ch


def tabuleiro(W, H, cols, rows, n_visiveis=None):
    """Fundo bordô, faixa preta, casas coloridas na borda (n_visiveis para animar) e o miolo bordô."""
    m, cw, ch = geometria(W, H, cols, rows)
    img = Image.new("RGBA", (W, H), BORDO + (255,))
    d = ImageDraw.Draw(img)
    d.rectangle((m - 14, m - 14, W - m + 14, H - m + 14), fill=(20, 6, 6))
    d.rectangle((m + cw, m + ch, W - m - cw, H - m - ch), fill=BORDO2)
    cores = [VERDE, MOSTARDA, CREME]
    lista = casas_borda(cols, rows)
    for k, (c, r) in enumerate(lista):
        if n_visiveis is not None and k >= n_visiveis:
            continue
        cor = cores[(c + r) % 3] if (c + r) % 3 != 2 or k % 4 else cores[1]
        d.rectangle((m + c * cw + 3, m + r * ch + 3, m + (c + 1) * cw - 3, m + (r + 1) * ch - 3), fill=cor)
    # miolo com uma borda clara fina
    d.rectangle((m + cw + 6, m + ch + 6, W - m - cw - 6, H - m - ch - 6), outline=(120, 30, 28), width=4)
    return img


def centro_casa(W, H, cols, rows, c, r):
    m, cw, ch = geometria(W, H, cols, rows)
    return m + (c + 0.5) * cw, m + (r + 0.5) * ch


# figurinha de cada casa (col, linha, nome, giro) — a moldura fica cheia como na referência
def mapa(cols, rows):
    jogos = ["hitster", "dixit", "telma", "tapalavras", "say_my_name", "uga_buga"]
    figs = ["explosao", "raio", "carta1", "dado", "xicara", "guarda", "explosao2", "carta2", "dado2", "carta3"]
    lista = casas_borda(cols, rows)
    out, fi, ji = [], 0, 0
    rnd = random.Random(7)
    for k, (c, r) in enumerate(lista):
        if k % 3 == 1 and ji < len(jogos):
            out.append((c, r, "cx:" + jogos[ji], rnd.uniform(-10, 10)))
            ji += 1
        elif k % 3 != 2:
            out.append((c, r, figs[fi % len(figs)], rnd.uniform(-14, 14)))
            fi += 1
    return out


def poe_figs(img, W, H, cols, rows, t=None, t0=0.0, passo=0.08):
    m, cw, ch = geometria(W, H, cols, rows)
    for k, (c, r, nome, rot) in enumerate(mapa(cols, rows)):
        x, y = centro_casa(W, H, cols, rows, c, r)
        if nome.startswith("cx:"):
            im = caixa_adesivo(nome[3:], int(ch * 0.78), int(rot))
        else:
            im = FIGS[nome]()
            esc = min(cw * 1.05 / im.width, ch * 1.05 / im.height)
            im = im.resize((int(im.width * esc), int(im.height * esc)), Image.LANCZOS)
            im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
        sc, a = 1.0, 1.0
        if t is not None:
            a, sc = K.surge(t, t0 + k * passo, 0.3)
            if a <= 0:
                continue
            sc *= 1 + 0.05 * math.sin(t * 3 + k)  # respira
        E.cola(img, im, x, y, 0, sc, a)


# ---------------------------------------------------------------- textos do miolo
def tracejado(d, x0, x1, y, cor=MOSTARDA):
    x = x0
    while x < x1:
        d.line((x, y, min(x + 18, x1), y), fill=cor, width=4)
        x += 30


def miolo(img, W, H, cols, rows, story=False, so=None, k=None):
    """Conteúdo do miolo bordô, ajustado para caber (k = escala; None = acha a maior que cabe).
    so = conjunto de blocos a mostrar (para animar)."""
    m, cw, ch = geometria(W, H, cols, rows)
    x0, y0, x1, y1 = m + cw, m + ch, W - m - cw, H - m - ch
    if k is None:
        k = 1.25
        while k > 0.5:
            teste = Image.new("RGBA", (W, H))
            if _miolo(teste, x0, y0, x1, y1, story, None, k) <= y1 - 24:
                break
            k -= 0.03
    return _miolo(img, x0, y0, x1, y1, story, so, k)


def _cabe(d, txt, fonte_nome, s, maxw, peso=None):
    while s > 12 and d.textlength(txt, font=F(fonte_nome, s, peso)) > maxw:
        s -= 1
    return F(fonte_nome, s, peso)


def _miolo(img, x0, y0, x1, y1, story, so, k):
    cx = (x0 + x1) / 2
    d = ImageDraw.Draw(img)
    larg = x1 - x0 - 50
    y = y0 + 30 * k

    def mostra(b):
        return so is None or b in so
    lg = K.logo(int(150 * k))
    if mostra("logo"):
        img.alpha_composite(lg, (int(cx - lg.width / 2), int(y)))
    y += lg.height + 22 * k
    ft = _cabe(d, "TARDE DE", "Anton-Regular.ttf", int(150 * k), larg)
    for li, (txt, cor) in enumerate((("TARDE DE", CREME_TXT), ("JOGOS!", MOSTARDA))):
        if mostra("titulo"):
            d.text((cx + 5, y + 6), txt, font=ft, fill=(30, 4, 4), anchor="mt")
            d.text((cx, y), txt, font=ft, fill=cor, anchor="mt")
        y += ft.size * 1.08
    y += 14 * k
    if mostra("titulo"):
        tracejado(d, x0 + 30, x1 - 30, y, MOSTARDA)
    y += 26 * k
    for txt in ("Venha jogar com os amigos, a família", "e quem você ainda nem conhece!"):
        fb = _cabe(d, "Venha jogar com os amigos, a família", "SpaceGrotesk.ttf", int(36 * k), larg, (600,))
        if mostra("convite"):
            d.text((cx, y), txt, font=fb, fill=(255, 245, 230), anchor="mt")
        y += fb.size * 1.3
    y += 18 * k
    et = F("SpaceGrotesk.ttf", int(34 * k), (700,))
    if mostra("lista"):
        w_et = d.textlength("NA TARDE TEM", font=et) + 40
        d.rectangle((cx - w_et / 2, y, cx + w_et / 2, y + et.size * 1.5), fill=MOSTARDA)
        d.text((cx, y + et.size * 0.75), "NA TARDE TEM", font=et, fill=TINTA, anchor="mm")
    y += et.size * 1.5 + 18 * k
    itens = ["JOGOS DE TABULEIRO E DE CARTAS", "A GENTE ENSINA TODOS OS JOGOS", "CAFÉ E COMIDINHAS DO BECAS"]
    fi = _cabe(d, itens[0], "SpaceGrotesk.ttf", int(34 * k), larg - 50, (700,))
    for it in itens:
        if mostra("lista"):
            d.ellipse((x0 + 34, y + fi.size * 0.32, x0 + 48, y + fi.size * 0.32 + 14), fill=CREME_TXT)
            d.text((x0 + 62, y), it, font=fi, fill=(255, 245, 230))
        y += fi.size * 1.45
    y += 10 * k
    if mostra("data"):
        tracejado(d, x0 + 30, x1 - 30, y, MOSTARDA)
    y += 24 * k
    fd = _cabe(d, "DATA EM BREVE", "Anton-Regular.ttf", int(104 * k), larg)
    if mostra("data"):
        d.text((cx, y), "DATA EM BREVE", font=fd, fill=CREME_TXT, anchor="mt")
    y += fd.size * 1.12
    fp = _cabe(d, "R$ 30 por pessoa, e R$ 15 viram consumação no café", "SpaceGrotesk.ttf", int(32 * k), larg, (700,))
    if mostra("data"):
        d.text((cx, y), "R$ 30 por pessoa, e R$ 15 viram consumação no café", font=fp, fill=MOSTARDA, anchor="mt")
    y += fp.size * 1.5
    fl = F("Anton-Regular.ttf", int(58 * k))
    if mostra("data"):
        d.text((cx, y), "@ BECAS CAFÉ", font=fl, fill=CREME_TXT, anchor="mt")
    y += fl.size * 1.3
    fr = F("Anton-Regular.ttf", int(50 * k))
    fn = F("Anton-Regular.ttf", int(64 * k))
    hpil = fr.size * 1.2 + fn.size * 1.25 + 20 * k
    if mostra("reserva"):
        w = max(d.textlength("RESERVE NO WHATSAPP", font=fr), d.textlength(WHATS, font=fn)) + 70
        d.rounded_rectangle((cx - w / 2, y, cx + w / 2, y + hpil), 18, fill=VERDE, outline=TINTA, width=5)
        d.text((cx, y + 12 * k), "RESERVE NO WHATSAPP", font=fr, fill=TINTA, anchor="mt")
        d.text((cx, y + 12 * k + fr.size * 1.15), WHATS, font=fn, fill=TINTA, anchor="mt")
    y += hpil + 14 * k
    fz = _cabe(d, "não reservou? passa lá no dia: se tiver mesa, é só chegar!", "SpaceGrotesk.ttf", int(28 * k),
               larg, (600,))
    if mostra("reserva"):
        d.text((cx, y), "não reservou? passa lá no dia: se tiver mesa, é só chegar!", font=fz, fill=(240, 220, 200),
               anchor="mt")
    y += fz.size * 1.4
    return y


def acabamento(img, W, H):
    for (x, y, r) in ((W * 0.5, 22, 18), (W - 22, H * 0.5, 16)):
        pass
    return grao(img, 12)


def post():
    W, H, cols, rows = 1080, 1350, 6, 7
    img = tabuleiro(W, H, cols, rows)
    poe_figs(img, W, H, cols, rows)
    miolo(img, W, H, cols, rows)
    return acabamento(img, W, H)


def story():
    W, H, cols, rows = 1080, 1920, 6, 9
    img = tabuleiro(W, H, cols, rows)
    poe_figs(img, W, H, cols, rows)
    y = miolo(img, W, H, cols, rows, story=True)
    # espaço para o adesivo de link (logo abaixo do miolo)
    d = ImageDraw.Draw(img)
    m, cw, ch = geometria(W, H, cols, rows)
    # o adesivo de link do Instagram vai por cima das casas de baixo
    return acabamento(img, W, H)


# ======================================================================= REELS
W, H, FPS = 1080, 1920, 30
COLS, ROWS = 6, 9
JOGOS_V = [("critter", 0.6, "CRITTER KITCHEN"), ("sushi", 0.4, "SUSHI GO!"), ("canvas", 1.4, "CANVAS"),
           ("art", 0.5, "ART SOCIETY"), ("passaporte", 0.8, "PASSAPORTE MUNDO"), ("unlock", 0.6, "UNLOCK!")]
MONTA = 3.0          # casas e figurinhas aparecem
PJ = 1.9
INI_J = MONTA + 0.2
INFO = INI_J + len(JOGOS_V) * PJ
DUR = INFO + 7.5


@lru_cache(None)
def base_reels():
    img = tabuleiro(W, H, COLS, ROWS)
    poe_figs(img, W, H, COLS, ROWS)
    return img


def miolo_rect():
    m, cw, ch = geometria(W, H, COLS, ROWS)
    return int(m + cw + 10), int(m + ch + 10), int(W - m - cw - 10), int(H - m - ch - 10)


def quadro(t):
    if t < MONTA:
        n = int(len(casas_borda(COLS, ROWS)) * min(1.0, t / 1.2)) + 1
        img = tabuleiro(W, H, COLS, ROWS, n)
        poe_figs(img, W, H, COLS, ROWS, t, 0.9, 0.06)
        d = ImageDraw.Draw(img)
        x0, y0, x1, y1 = miolo_rect()
        cx = (x0 + x1) / 2
        f = F("Anton-Regular.ttf", 128)
        for li, (txt, cor, t0) in enumerate((("TARDE DE", CREME_TXT, 0.3), ("JOGOS!", MOSTARDA, 0.8))):
            a, s = K.surge(t, t0, 0.25)
            if a > 0:
                im = Image.new("RGBA", (700, 220), (0, 0, 0, 0))
                di = ImageDraw.Draw(im)
                di.text((356, 116), txt, font=f, fill=(30, 4, 4), anchor="mm")
                di.text((350, 110), txt, font=f, fill=cor, anchor="mm")
                E.cola(img, im, cx, 760 + li * 190, -3 if li else 2, s, a)
        a, s = K.surge(t, 1.6, 0.3)
        if a > 0:
            E.cola(img, ST.estrela(60, 30, 8, MOSTARDA + (255,)) if False else estrela_atomica(70, MOSTARDA),
                   cx + 230, 640, 0, s, a)
            d.text((cx, 1150), "SUA VEZ × BECAS CAFÉ", font=F("SpaceGrotesk.ttf", 44, (700,)), fill=(255, 245, 230),
                   anchor="mm")
        return grao(img, 10, int(t * 30) % 5).convert("RGB")
    img = base_reels().copy()
    x0, y0, x1, y1 = miolo_rect()
    cx = (x0 + x1) / 2
    d = ImageDraw.Draw(img)
    if t < INFO:
        k = min(len(JOGOS_V) - 1, int((t - INI_J) / PJ))
        u = t - INI_J - k * PJ
        nome, t0, titulo = JOGOS_V[k]
        fr = K.quadro_clip(nome, *ST.FULL[nome], 1.0, t0 + max(0.0, u)).convert("RGB")
        w, h = x1 - x0, y1 - y0 - 260
        fr = ST.cobre(fr, w, h)
        img.paste(fr, (x0, y0 + 130))
        d.rectangle((x0, y0 + 130, x1, y0 + 130 + h), outline=TINTA, width=8)
        d.text((cx, y0 + 66), "NA MESA HOJE:", font=F("Anton-Regular.ttf", 76), fill=MOSTARDA, anchor="mm")
        a, s = K.surge(u, 0.1, 0.22)
        if a > 0:
            ft = F("Anton-Regular.ttf", 92 if len(titulo) < 12 else 76)
            im = Image.new("RGBA", (int(d.textlength(titulo, font=ft)) + 70, 140), (0, 0, 0, 0))
            di = ImageDraw.Draw(im)
            di.rounded_rectangle((0, 0, im.width - 1, 139), 18, fill=VERDE, outline=TINTA, width=6)
            di.text((im.width / 2, 70), titulo, font=ft, fill=TINTA, anchor="mm")
            E.cola(img, im, cx, y1 - 66, (-3, 2, -2)[k % 3], s, a)
        if u < 2 / FPS and k:
            img.alpha_composite(Image.new("RGBA", (W, H), (255, 240, 200, 110)))
    else:
        u = t - INFO
        blocos = {"logo"}
        for b, tb in (("titulo", 0.2), ("convite", 0.9), ("lista", 1.6), ("data", 2.6), ("reserva", 3.4)):
            if u >= tb:
                blocos.add(b)
        miolo(img, W, H, COLS, ROWS, story=True, so=blocos)
        if u > 4.6:  # pílula por cima da fileira de casas de baixo
            fc = F("Anton-Regular.ttf", 50)
            txt = "COMENTA: QUAL JOGO VOCÊ QUER APRENDER?"
            pw = int(d.textlength(txt, font=fc)) + 60
            pil = Image.new("RGBA", (pw, 100), (0, 0, 0, 0))
            dp = ImageDraw.Draw(pil)
            dp.rounded_rectangle((0, 0, pw - 1, 99), 24, fill=MOSTARDA, outline=TINTA, width=6)
            dp.text((pw / 2, 50), txt, font=fc, fill=TINTA, anchor="mm")
            m_, cw_, ch_ = geometria(W, H, COLS, ROWS)
            K.poe(img, pil, cx, H - m_ - ch_ / 2, u, 4.6, -2)
    return grao(img, 10, int(t * 30) % 5).convert("RGB")


def render(fi):
    return quadro(fi / FPS).tobytes()


def musica_retro(dur, bpm=104):
    """Anos 60: órgão (drawbars), baixo andando, vassourinha com balanço, guitarra 'surf' em notas curtas."""
    out = np.zeros(int(dur * S.SR) + S.SR)
    b = 60 / bpm

    def orgao(f, d):
        t = S.t_(d)
        s = sum(g * np.sin(2 * np.pi * f * m * t) for m, g in ((0.5, .5), (1, 1), (2, .6), (3, .3), (4, .25)))
        return s * np.minimum(1, t / 0.01) * np.minimum(1, (d - t) / 0.05) * (1 + 0.1 * np.sin(2 * np.pi * 6 * t))
    prog = [["A3", "C#4", "E4"], ["D3", "F#3", "A3"], ["E3", "G#3", "B3"], ["D3", "F#3", "A3"]]
    anda = [["A1", "C#2", "E2", "F#2"], ["D2", "F#2", "A2", "B2"], ["E2", "G#2", "B2", "C#3"], ["D2", "F#2", "A2", "F#2"]]
    surf = ["E5", "C#5", "A4", "E5", "F#5", "E5", "C#5", "B4"]
    n = int(dur / b) + 1
    for k in range(n):
        t = k * b
        c = (k // 4) % 4
        S.add(out, S.baixo(S.hz(anda[c][k % 4]), b * 0.9), t, 0.5)
        S.add(out, S.vassourinha(), t, 0.45)
        S.add(out, S.chimbal(0.04), t + b * 0.66, 0.15)
        if k % 2 == 1:
            S.add(out, S.snare(0.15), t, 0.3)
        if k % 2 == 0:
            S.add(out, sum(orgao(S.hz(nn), b * 1.6) for nn in prog[c]) / 3, t, 0.28)
        if k % 2 == 1:
            S.add(out, S.marimba(S.hz(surf[k % len(surf)]), 0.35), t + b * 0.5, 0.25)
    return out[:int(dur * S.SR)]


def audio(com, sem):
    ev = [(0.05 + k * 0.05, S.carta_vira(), 0.25) for k in range(0, 24, 2)]
    ev += [(0.3, S.cartao(), 0.6), (0.8, S.cartao(), 0.6)]
    for k in range(len(mapa(COLS, ROWS))):
        if k % 2 == 0:
            ev.append((0.9 + k * 0.06, S.tique(), 0.3))
    for k in range(len(JOGOS_V)):
        ev += [(INI_J + k * PJ, S.carta_vira(), 0.6), (INI_J + k * PJ + 0.1, S.cartao(), 0.5)]
    ev += [(INFO + tb, S.cartao(), 0.5) for tb in (0.2, 0.9, 1.6, 2.6, 3.4)] + [(INFO + 3.4, S.sino(), 0.4)]
    mus = musica_retro(DUR)
    S.grava(com, DUR, ev, mus, musica_ganho=0.5, fx_ganho=0.8)
    S.grava(sem, DUR, ev, None, fx_ganho=0.8)


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--reels" in sys.argv or "--frame" in sys.argv:
        K.prepara([(n, t0, d, 1.0) for n, (t0, d) in ST.FULL.items()])
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:]]
        K.folha([quadro(x) for x in ts], os.path.join(K.OUT, "frames_gamesday.jpg"))
        print("ok", round(DUR, 1))
        return
    if "--reels" in sys.argv:
        com, sem = os.path.join(K.OUT, "gamesday_com.wav"), os.path.join(K.OUT, "gamesday_sem.wav")
        audio(com, sem)
        K.entrega("gamesday", DUR, render, com, sem)
        return
    p, s = post(), story()
    p.convert("RGB").save(os.path.join(OUT, "post_1080x1350.png"))
    s.convert("RGB").save(os.path.join(OUT, "story_1080x1920.png"))
    sh = Image.new("RGB", (540 + 20 + 540, 960), (255, 255, 255))
    sh.paste(p.convert("RGB").resize((540, 675)), (0, 0))
    sh.paste(s.convert("RGB").resize((540, 960)), (560, 0))
    sh.save(os.path.join(OUT, "folha.jpg"), quality=90)
    print("ok")


if __name__ == "__main__":
    main()
