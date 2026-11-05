#!/usr/bin/env python3
"""Referência 2 de 4/nov/2026: pôster "GAME NIGHT" retrô ANOS 60 (verde-petróleo, laranja, mostarda e creme chapados,
grão de impressão, estrelas atômicas, tabuleiro de hexágonos com desenhos simples, cartas em leque, dados, lápis e
folha de pontos). Só esta referência (ele pediu para NÃO misturar). Peças: post 1080x1350, story 1080x1920 e Reels.
Formas simples desenhadas (nada de meeple/peão); no Reels as cenas de jogo deles entram como cartões-postais.

    /usr/bin/python3 retro60.py              # out/retro60/post_1080x1350.png, story_1080x1920.png, folha.jpg
    /usr/bin/python3 retro60.py --frame 1 3 6 12 18 21
    /usr/bin/python3 retro60.py --reels      # out/retro60_{com_som,para_musica}_final.mp4
"""
import math
import os
import random
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import kit as K
import sons as S
import estilos as ST
from kit import TB

OUT = os.path.join(K.OUT, "retro60")
FD = os.path.join(K.REPO, "comum", "fontes")
PET = (24, 78, 86)
PET_ESC = (14, 50, 56)
LAR = (222, 96, 44)
MOS = (240, 176, 44)
CRE = (244, 228, 196)
TIN = (26, 30, 34)


@lru_cache(None)
def F(nome, s, peso=None):
    f = ImageFont.truetype(os.path.join(FD, nome), int(s))
    if peso:
        f.set_variation_by_axes(list(peso))
    return f


def grao(img, amp=16, seed=1):
    a = np.asarray(img.convert("RGB"), np.int16)
    rng = np.random.default_rng(seed)
    n = rng.integers(-amp, amp + 1, a.shape[:2], dtype=np.int16)
    a = np.clip(a + n[..., None], 0, 255).astype(np.uint8)
    return Image.fromarray(a).convert("RGBA")


# ---------------------------------------------------------------- ilustração chapada
def fundo(W, H, y_mesa):
    img = Image.new("RGBA", (W, H), PET + (255,))
    d = ImageDraw.Draw(img)
    d.polygon([(0, y_mesa + 120), (W, y_mesa - 80), (W, H), (0, H)], fill=LAR)  # mesa laranja em diagonal
    return img


@lru_cache(None)
def estrela(r=60, cor=CRE, n=8):
    im = Image.new("RGBA", (2 * r + 10, 2 * r + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k in range(n):
        a = math.pi * k / n
        rr = r if k % 2 == 0 else r * 0.55
        d.line((r + 5 - rr * math.cos(a), r + 5 - rr * math.sin(a), r + 5 + rr * math.cos(a),
                r + 5 + rr * math.sin(a)), fill=cor, width=4)
    return im


def glifo(d, cx, cy, r, tipo, cor):
    if tipo == "arvores":
        for k in range(3):
            x = cx - r * 0.35 + k * r * 0.35
            d.polygon([(x, cy - r * 0.32), (x - r * 0.14, cy + r * 0.12), (x + r * 0.14, cy + r * 0.12)], fill=cor)
    elif tipo == "ondas":
        for k in range(3):
            y = cy - r * 0.25 + k * r * 0.25
            d.arc((cx - r * 0.4, y - 8, cx, y + 8), 180, 360, fill=cor, width=4)
            d.arc((cx, y - 8, cx + r * 0.4, y + 8), 0, 180, fill=cor, width=4)
    elif tipo == "montanha":
        d.polygon([(cx - r * 0.5, cy + r * 0.25), (cx - r * 0.15, cy - r * 0.3), (cx + r * 0.1, cy + r * 0.25)],
                  fill=cor)
        d.polygon([(cx - r * 0.1, cy + r * 0.25), (cx + r * 0.2, cy - r * 0.15), (cx + r * 0.5, cy + r * 0.25)],
                  fill=cor)
    elif tipo == "pontos":
        for k in range(5):
            x = cx - r * 0.3 + (k % 3) * r * 0.3
            y = cy - r * 0.12 + (k // 3) * r * 0.25
            d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=cor)


@lru_cache(None)
def tabuleiro_hex(cols=6, rows=5, r=78, seed=3):
    """Tabuleiro de hexágonos chapado, com borda escura, visto em leve perspectiva."""
    rnd = random.Random(seed)
    w = int(cols * r * 1.75 + r * 2)
    h = int(rows * r * 1.52 + r * 2)
    im = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    centros = []
    for row in range(rows):
        for col in range(cols):
            cx = 30 + r * 1.2 + col * r * 1.74 + (r * 0.87 if row % 2 else 0)
            cy = 30 + r * 1.1 + row * r * 1.5
            centros.append((cx, cy))
    # borda do tabuleiro (casco dos hexágonos, engordado)
    pts_todos = []
    for cx, cy in centros:
        for k in range(6):
            a = math.pi / 6 + k * math.pi / 3
            pts_todos.append((cx + (r + 26) * math.cos(a), cy + (r + 26) * math.sin(a)))
    xs = [p[0] for p in pts_todos]
    ys = [p[1] for p in pts_todos]
    d.rounded_rectangle((min(xs), min(ys), max(xs), max(ys)), 40, fill=PET_ESC)
    d.rounded_rectangle((min(xs) + 14, min(ys) + 14, max(xs) - 14, max(ys) - 14), 30, fill=(214, 200, 168))
    tipos = ["arvores", "ondas", "montanha", "pontos", None]
    cores = [(PET, CRE), (MOS, PET_ESC), (LAR, CRE), (CRE, PET), ((54, 120, 120), CRE)]
    for cx, cy in centros:
        fundo_c, glif_c = cores[rnd.randrange(len(cores))]
        hexa = [(cx + r * math.cos(math.pi / 6 + k * math.pi / 3), cy + r * math.sin(math.pi / 6 + k * math.pi / 3))
                for k in range(6)]
        d.polygon(hexa, fill=fundo_c, outline=PET_ESC, width=5)
        t = tipos[rnd.randrange(len(tipos))]
        if t:
            glifo(d, cx, cy, r, t, glif_c)
    # perspectiva: achata e inclina
    im = im.resize((im.width, int(im.height * 0.72)), Image.LANCZOS)
    return im.rotate(-10, expand=True, resample=Image.BICUBIC)


@lru_cache(None)
def leque_cartas(h=360):
    w = int(h * 0.66)
    cartas = []
    estilos = [(MOS, "sol"), (LAR, "faixas"), (PET_ESC, "linhas"), (PET, "estrela")]
    for cor, tipo in estilos:
        c = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(c)
        d.rounded_rectangle((0, 0, w - 1, h - 1), 22, fill=CRE)
        d.rounded_rectangle((14, 14, w - 15, h - 15), 16, fill=cor)
        if tipo == "sol":
            d.ellipse((w * 0.25, h * 0.25, w * 0.75, h * 0.25 + w * 0.5), fill=LAR)
        elif tipo == "faixas":
            for k in range(4):
                d.rectangle((14, 40 + k * 70, w - 15, 60 + k * 70), fill=CRE)
        elif tipo == "linhas":
            for k in range(5):
                d.line((30, h * 0.2 + k * 50, w - 30, h * 0.15 + k * 50), fill=MOS, width=5)
        else:
            c.alpha_composite(estrela(int(w * 0.36), PET_ESC), (int(w * 0.14), int(h * 0.3)))
        cartas.append(c)
    out = Image.new("RGBA", (int(w * 2.4), int(h * 1.5)), (0, 0, 0, 0))
    for k, c in enumerate(cartas):
        cc = c.rotate(25 - k * 14, expand=True, resample=Image.BICUBIC)
        out.alpha_composite(cc, (int(k * w * 0.32), int(abs(k - 1.5) * 18)))
    return out


@lru_cache(None)
def dado60(s=120, cor=CRE, pinta=PET_ESC, n=5):
    im = Image.new("RGBA", (s + 20, s + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((12, 14, s + 12, s + 14), 22, fill=PET_ESC)
    d.rounded_rectangle((0, 0, s, s), 22, fill=cor)
    P = {5: [(.27, .27), (.73, .27), (.5, .5), (.27, .73), (.73, .73)], 4: [(.27, .27), (.73, .27), (.27, .73),
                                                                          (.73, .73)], 2: [(.3, .3), (.7, .7)]}[n]
    for px, py in P:
        r = s * 0.08
        d.ellipse((px * s - r, py * s - r, px * s + r, py * s + r), fill=pinta)
    return im


@lru_cache(None)
def xicara60(s=230):
    im = Image.new("RGBA", (int(s * 1.4), int(s * 1.25)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((0, s * 0.85, s * 1.3, s * 1.2), fill=PET_ESC)
    d.ellipse((s * 0.05, s * 0.86, s * 1.25, s * 1.15), fill=CRE)
    d.arc((s * 0.82, s * 0.35, s * 1.25, s * 0.8), -90, 90, fill=LAR, width=22)
    d.chord((s * 0.12, s * 0.05, s * 0.98, s * 1.05), 0, 180, fill=LAR)
    d.rectangle((s * 0.12, s * 0.3, s * 0.98, s * 0.55), fill=LAR)
    for k in range(7):  # zigue-zague creme
        x = s * 0.15 + k * s * 0.12
        d.line((x, s * 0.62, x + s * 0.06, s * 0.52), fill=CRE, width=6)
        d.line((x + s * 0.06, s * 0.52, x + s * 0.12, s * 0.62), fill=CRE, width=6)
    d.ellipse((s * 0.12, s * 0.2, s * 0.98, s * 0.42), fill=(120, 60, 30))
    for k in range(3):
        x = s * (0.32 + 0.16 * k)
        d.arc((x - 16, -s * 0.1, x + 16, s * 0.18), 90, 270, fill=CRE, width=6)
    return im


@lru_cache(None)
def folha_pontos(w=560, h=420, linhas=None):
    """Folha de pontos creme pautada (como na referência), com as informações."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((10, 12, w - 1, h - 1), fill=PET_ESC)
    d.rectangle((0, 0, w - 11, h - 13), fill=CRE)
    for y in range(70, h - 20, 58):
        d.line((20, y, w - 31, y), fill=(200, 180, 150), width=3)
    if linhas:
        y = 26
        for txt, s, cor in linhas:
            f = F("SpaceGrotesk.ttf", s, (700,))
            while d.textlength(txt, font=f) > w - 70 and f.size > 18:
                f = F("SpaceGrotesk.ttf", f.size - 1, (700,))
            d.text((34, y), txt, font=f, fill=cor)
            y += 58
    return im


def lapis(img, x, y, rot=-30):
    p = Image.new("RGBA", (420, 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(p)
    d.rectangle((40, 6, 380, 34), fill=MOS)
    d.rectangle((380, 6, 410, 34), fill=(230, 140, 140))
    d.polygon([(40, 6), (0, 20), (40, 34)], fill=(232, 200, 160))
    d.polygon([(12, 16), (0, 20), (12, 24)], fill=TIN)
    p = p.rotate(rot, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(p, (int(x - p.width / 2), int(y - p.height / 2)))


def titulo(img, cx, y, s=1.0, a=1.0, n_letras=None):
    d = ImageDraw.Draw(img)
    f1 = F("ArchivoBlack-Regular.ttf", int(150 * s))
    f2 = F("ArchivoBlack-Regular.ttf", int(240 * s))
    for txt, f, cor, yy in (("TARDE DE", f1, CRE, y), ("JOGOS!", f2, MOS, y + 170 * s)):
        if n_letras is not None:
            txt = txt[:max(0, n_letras)]
            n_letras -= len("TARDE DE") if f is f1 else 0
        d.text((cx + 8 * s, yy + 10 * s), txt, font=f, fill=PET_ESC, anchor="mt")
        d.text((cx, yy), txt, font=f, fill=cor, anchor="mt")


INFO = [("Becas Café · R. Sorocaba, 35", 34, PET_ESC), ("sexta, 20/11 (feriado) · 13h às 19h", 34, LAR),
        ("R$ 30 (R$ 15 viram consumação)", 32, PET_ESC), ("a gente ensina todos os jogos", 32, PET_ESC),
        ("reserve: (11) 97793-3910", 34, LAR), ("ou chegue no dia!", 30, PET_ESC)]


def poster(W, H, story=False):
    y_mesa = 760 if not story else 1180
    img = fundo(W, H, y_mesa)
    for x, y, r in ((90, 120, 50), (W - 120, 90, 40), (W - 80, 560 if not story else 720, 60), (150, 600, 34)):
        img.alpha_composite(estrela(r, CRE), (int(x - r), int(y - r)))
    lg = K.logo(130)
    img.alpha_composite(lg, (W - lg.width - 30, 30))
    titulo(img, W / 2, 110 if not story else 300, 1.0)
    tb = tabuleiro_hex()
    esc = 0.78 if not story else 0.92
    tb = tb.resize((int(tb.width * esc), int(tb.height * esc)), Image.LANCZOS)
    img.alpha_composite(tb, (int(W * 0.18), y_mesa - 260 if not story else y_mesa - 330))
    lq = leque_cartas(300 if not story else 340)
    img.alpha_composite(lq, (-60, H - lq.height + (40 if not story else -190)))
    for k, (x, y, n, c) in enumerate(((330, H - 230, 5, CRE), (450, H - 180, 4, PET), (390, H - 330, 2, MOS))):
        if story:
            y -= 220
        img.alpha_composite(dado60(110, c, PET_ESC if c != PET else CRE, n), (x, y))
    xc = xicara60(210)
    img.alpha_composite(xc, (W - xc.width - 20, y_mesa - 210 if not story else y_mesa - 260))
    lapis(img, W - 330, H - 40 if not story else H - 250, -18)  # por baixo da folha, só a ponta aparece
    fp = folha_pontos(540 if not story else 600, 420 if not story else 470, tuple(INFO))
    fp = fp.rotate(4, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(fp, (W - fp.width - 30, H - fp.height - (60 if not story else 280)))
    return grao(img, 16)


def post():
    return poster(1080, 1350)


def story():
    return poster(1080, 1920, True)  # adesivo de link no pé (y ~1560–1700), sobre a mesa laranja


# ======================================================================= REELS
W, H, FPS = 1080, 1920, 30
JOGOS = [("critter", 0.6, "CRITTER KITCHEN"), ("sushi", 0.4, "SUSHI GO!"), ("canvas", 1.4, "CANVAS"),
         ("art", 0.5, "ART SOCIETY"), ("passaporte", 0.8, "PASSAPORTE MUNDO"), ("unlock", 0.6, "UNLOCK!")]
ABRE = 3.2
PJ = 1.9
INFO_T = ABRE + len(JOGOS) * PJ
DUR = INFO_T + 6.6


@lru_cache(None)
def poster_reels():
    return poster(W, H, True)


def postal(frame, w=760, h=900, titulo_txt=""):
    fr = ST.cobre(frame, w, h).convert("RGBA")
    c = Image.new("RGBA", (w + 60, h + 150), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rectangle((14, 16, w + 60, h + 150), fill=PET_ESC)
    d.rectangle((0, 0, w + 46, h + 136), fill=CRE)
    c.alpha_composite(fr, (23, 23))
    f = F("ArchivoBlack-Regular.ttf", 60 if len(titulo_txt) < 13 else 48)
    d.text((w / 2 + 23, h + 82), titulo_txt, font=f, fill=LAR, anchor="mm")
    return c


def quadro(t):
    if t < ABRE:
        img = fundo(W, H, 1180)
        u = t
        for k, (x, y, r) in enumerate(((90, 120, 50), (W - 120, 90, 40), (W - 80, 720, 60), (150, 600, 34))):
            a, s = K.surge(u, 0.2 + k * 0.15, 0.3)
            if a:
                st = estrela(r, CRE).rotate(u * 40, resample=Image.BICUBIC)
                K.E.cola(img, st, x, y, 0, s, a)
        titulo(img, W / 2, 300, 1.0, n_letras=int(u / 0.08))
        tb = tabuleiro_hex()
        tb = tb.resize((int(tb.width * 0.92), int(tb.height * 0.92)), Image.LANCZOS)
        q = K.ease(min(1.0, max(0.0, (u - 1.0) / 0.6)))
        img.alpha_composite(tb, (int(W * 0.18), int(850 + (1 - q) * 900)))
        lq = leque_cartas(340)
        q2 = K.ease(min(1.0, max(0.0, (u - 1.6) / 0.5)))
        img.alpha_composite(lq, (int(-60 - (1 - q2) * 600), H - lq.height - 190))
        xc = xicara60(210)
        q3 = K.ease(min(1.0, max(0.0, (u - 2.0) / 0.5)))
        img.alpha_composite(xc, (int(W - xc.width - 20 + (1 - q3) * 500), 920))
        img.alpha_composite(K.logo(130), (W - 160, 30))
        return grao(img, 16, int(t * 12)).convert("RGB")
    img = poster_reels().copy()
    if t < INFO_T:
        k = min(len(JOGOS) - 1, int((t - ABRE) / PJ))
        u = t - ABRE - k * PJ
        nome, t0, tt = JOGOS[k]
        img.alpha_composite(Image.new("RGBA", (W, H), (14, 40, 46, 150)))
        d = ImageDraw.Draw(img)
        d.text((W / 2 + 5, 216), "NA MESA:", font=F("ArchivoBlack-Regular.ttf", 110), fill=PET_ESC, anchor="mm")
        d.text((W / 2, 210), "NA MESA:", font=F("ArchivoBlack-Regular.ttf", 110), fill=MOS, anchor="mm")
        p = postal(K.quadro_clip(nome, *ST.FULL[nome], 1.0, t0 + u).convert("RGB"), titulo_txt=tt)
        q = K.ease(min(1.0, u / 0.3))
        rot = (-4, 3, -2, 4, -3, 2)[k]
        K.E.cola(img, p, W / 2 + (1 - q) * (900 if k % 2 else -900), 1000, rot * q)
    else:
        u = t - INFO_T
        fp = folha_pontos(600, 470, tuple(INFO))
        fp = fp.rotate(4, expand=True, resample=Image.BICUBIC)
        if u > 3.2:
            d = ImageDraw.Draw(img)
            for li, txt in enumerate(("COMENTA: QUAL JOGO", "VOCÊ QUER APRENDER?")):
                d.text((W / 2 + 4, 745 + li * 62 + 4), txt, font=F("ArchivoBlack-Regular.ttf", 50), fill=PET_ESC,
                       anchor="mm")
                d.text((W / 2, 745 + li * 62), txt, font=F("ArchivoBlack-Regular.ttf", 50), fill=CRE, anchor="mm")
    return grao(img, 16, int(t * 12)).convert("RGB")


def render(fi):
    return quadro(fi / FPS).tobytes()


def audio(com, sem):
    ev = [(k * 0.08, S.tecla(), 0.25) for k in range(14)]
    ev += [(1.0, S.sopro(0.5), 0.6), (1.6, S.carta_vira(), 0.6), (2.0, S.louca(2200), 0.5)]
    for k in range(len(JOGOS)):
        ev += [(ABRE + k * PJ, S.sopro(0.3), 0.5), (ABRE + k * PJ + 0.28, S.cartao(), 0.5)]
    ev += [(INFO_T, S.sopro(0.4, False), 0.5), (INFO_T + 3.2, S.sino(), 0.4)]
    from gamesday import musica_retro
    mus = musica_retro(DUR)
    S.grava(com, DUR, ev, mus, musica_ganho=0.5, fx_ganho=0.8)
    S.grava(sem, DUR, ev, None, fx_ganho=0.8)


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--reels" in sys.argv or "--frame" in sys.argv:
        K.prepara([(n, t0, d, 1.0) for n, (t0, d) in ST.FULL.items()])
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:]]
        K.folha([quadro(x) for x in ts], os.path.join(K.OUT, "frames_retro60.jpg"))
        print("ok", round(DUR, 1))
        return
    if "--reels" in sys.argv:
        com, sem = os.path.join(K.OUT, "retro60_com.wav"), os.path.join(K.OUT, "retro60_sem.wav")
        audio(com, sem)
        K.entrega("retro60", DUR, render, com, sem)
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
