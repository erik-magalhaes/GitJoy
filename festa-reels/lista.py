#!/usr/bin/env python3
"""Reels 3: A LISTA DA FESTA — sem narração. Folha de caderno numa mesa de madeira; a caneta escreve e marca
✓ comida, ✓ música, ✓ amigo secreto, ✓ decoração; no último item ("fazer a galera se divertir junta, sem celular") a caneta
para e rabisca "???"; o carimbo vermelho "RESOLVIDO: SUA VEZ" bate na folha; três polaroides com as cenas REAIS deles
jogando caem na mesa; um post-it "a gente leva os jogos e fica o evento todo ensinando"; post-it final com o contato.

    python3 lista.py --frame 0.5 3 7 9 10.5 14 17 21
    python3 lista.py
"""
import argparse
import math
import os
import random
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import comum_festa as C  # noqa: E402
from comum_festa import W, H, FPS, E  # noqa: E402
from previsao import anton, gro, ease, quebra  # noqa: E402
sys.path.insert(0, os.path.join(C.REPO, "comum"))
from motor import out_back  # noqa: E402
import sons as S  # noqa: E402

SR = 44100
FT = os.path.join(C.REPO, "taco-reels", "assets", "fonts")
TINTA = (24, 40, 110)
VERM = (205, 30, 40)
ITENS = ["comida", "música", "amigo secreto", "decoração", "fazer a galera se divertir (sem celular)"]
T_ITEM = [0.7, 1.95, 3.2, 4.45, 5.7]  # começo da escrita de cada item
T_RABISCO, T_CARIMBO = 7.6, 8.9
POLA = [("art", 0.6, "leilão disputado!"), ("critter", 1.0, "risada garantida"), ("unlock", 1.0, "todo mundo junto")]
T_POLA = [9.8, 10.6, 11.4]
T_POSTIT, T_CTA = 13.6, 17.2
DUR = 23.0
PX, PY, PWID, PHGT, PROT = 120, 200, 840, 1010, -2.0  # folha de caderno


@lru_cache(None)
def mao(s):
    return ImageFont.truetype(os.path.join(FT, "PatrickHand-Regular.ttf"), s)


@lru_cache(None)
def marcador(s):
    return ImageFont.truetype(os.path.join(C.F, "PermanentMarker-Regular.ttf"), s)


@lru_cache(None)
def mesa():
    rng = np.random.default_rng(7)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    larg = 216
    tab = (xx // larg).astype(int)
    off = rng.uniform(0, 100, 12)
    var = rng.uniform(0.9, 1.07, 12)
    veio = np.sin((yy * 0.010 + np.sin(yy * 0.0035 + off[tab]) * 3.2 + (xx % larg) * 0.07) * 2.0)
    lum = var[tab] * (0.93 + 0.055 * veio)
    img = np.array([150, 98, 60], np.float32)[None, None] * lum[..., None]
    img[(xx % larg) < 3] *= 0.6
    yv = np.linspace(-1, 1, H)[:, None]
    xv = np.linspace(-1, 1, W)[None, :]
    img *= (1.05 - 0.4 * (xv ** 2 + (yv * 0.9) ** 2) ** 1.1)[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


LH = 118  # altura da linha da pauta
Y0 = 280  # 1ª linha dos itens (na folha)


@lru_cache(None)
def folha_base():
    im = Image.new("RGBA", (PWID, PHGT), (252, 250, 242, 255))
    d = ImageDraw.Draw(im)
    for y in range(Y0 - 40, PHGT - 30, LH // 2):
        d.line((40, y, PWID - 30, y), fill=(160, 190, 225, 255), width=2)
    d.line((110, 0, 110, PHGT), fill=(230, 120, 130, 255), width=3)
    for y in range(60, PHGT, 120):  # furos da espiral
        d.ellipse((24, y, 52, y + 28), fill=(150, 98, 60, 255))
    d.text((PWID / 2 + 30, 120), "FESTA DE FIM DE ANO", font=marcador(70), fill=VERM, anchor="mm")
    d.text((PWID / 2 + 30, 200), "o que falta?", font=mao(60), fill=TINTA, anchor="mm")
    return im


def pos_item(i):
    return 190, Y0 + i * 104


def check(d, x, y, u, cor=(20, 140, 60)):
    """✓ desenhado em dois traços."""
    p1, p2, p3 = (x, y), (x + 26, y + 30), (x + 74, y - 40)
    if u <= 0:
        return
    a = min(1, u / 0.4)
    d.line((p1, (p1[0] + (p2[0] - p1[0]) * a, p1[1] + (p2[1] - p1[1]) * a)), fill=cor, width=12)
    if u > 0.4:
        b = min(1, (u - 0.4) / 0.6)
        d.line((p2, (p2[0] + (p3[0] - p2[0]) * b, p2[1] + (p3[1] - p2[1]) * b)), fill=cor, width=12)


def escrever(d, txt, x, y, u, f, larg=560):
    """Escreve letra a letra; devolve a posição da ponta da caneta."""
    linhas = quebra(txt, f, larg)
    tot = sum(len(l) for l in linhas)
    n = int(tot * min(1, u))
    pena = (x, y)
    for i, ln in enumerate(linhas):
        k = min(len(ln), n)
        n -= k
        if k > 0:
            parte = ln[:k]
            d.text((x, y + i * 62), parte, font=f, fill=TINTA, anchor="lm")
            pena = (x + d.textlength(parte, font=f), y + i * 62)
    return pena, len(linhas)


def folha(t):
    im = folha_base().copy()
    d = ImageDraw.Draw(im)
    pena = None
    for i, txt in enumerate(ITENS):
        t0 = T_ITEM[i]
        bx, by = pos_item(i)
        d.rounded_rectangle((bx - 70, by - 26, bx - 22, by + 22), 6, outline=TINTA, width=4)
        if t < t0:
            continue
        dur = 0.75 if i < 4 else 1.6
        p, nl = escrever(d, txt, bx, by, (t - t0) / dur, mao(64))
        if t - t0 < dur:
            pena = p
        if i < 4:
            u = (t - t0 - dur - 0.05) / 0.35
            check(d, bx - 64, by - 4, u)
            if 0 < u < 1:
                pena = (bx - 30, by)
        else:
            if T_RABISCO <= t:  # a caneta para e rabisca "???"
                u = (t - T_RABISCO) / 1.0
                n = int(3 * min(1, u * 1.4))
                d.text((bx + 525, by + 62), "?" * max(1, n) if u > 0 else "", font=marcador(70), fill=VERM, anchor="lm")
                pena = (bx + 525 + 10 * math.sin(t * 40), by + 62 + 6 * math.cos(t * 33)) if t < T_CARIMBO else None
    return im, pena


@lru_cache(None)
def caneta():
    im = Image.new("RGBA", (60, 380), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(30, 0), (22, 30), (38, 30)], fill=(20, 30, 90, 255))
    d.rectangle((20, 30, 40, 70), fill=(200, 200, 205, 255))
    d.rounded_rectangle((16, 70, 44, 370), 10, fill=(30, 50, 140, 255))
    d.rectangle((16, 200, 44, 230), fill=(240, 240, 245, 255))
    return im


@lru_cache(None)
def carimbo():
    w, h = 760, 230
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 8, w - 8, h - 8), 26, outline=VERM + (255,), width=12)
    d.text((w / 2, 72), "RESOLVIDO:", font=anton(70), fill=VERM + (255,), anchor="mm")
    d.text((w / 2, 160), "CHAMA A SUA VEZ!", font=anton(80), fill=VERM + (255,), anchor="mm")
    a = np.asarray(im).copy()
    rng = np.random.default_rng(3)
    falha = rng.random(a.shape[:2]) < 0.12  # tinta falhada de carimbo
    a[..., 3] = np.where(falha, (a[..., 3] * 0.35).astype(np.uint8), a[..., 3])
    return Image.fromarray(a, "RGBA")


def polaroide(nome, t0, rot, u):
    w, h = 330, 400
    q = C.clip(nome, t0, 2.4, max(0.0, min(2.35, u)))
    q = q.resize((int(W * 0.34), int(H * 0.34)))
    cx, cy = q.width // 2, int(q.height * 0.5)
    q = q.crop((cx - 145, cy - 145, cx + 145, cy + 145))
    im = Image.new("RGBA", (w, h), (250, 250, 246, 255))
    im.paste(q, (20, 20))
    d = ImageDraw.Draw(im)
    d.text((w / 2, 360), rot, font=mao(40), fill=TINTA, anchor="mm")
    return im


def fita(img, x, y, rot):
    f = Image.new("RGBA", (150, 46), (235, 225, 190, 190))
    E.cola(img, f, x, y, rot, 1, 1)


def postit(linhas, w=700, h=520, cor=(255, 226, 90)):
    im = Image.new("RGBA", (w, h), cor + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, 40), fill=tuple(int(c * 0.93) for c in cor) + (255,))
    y = 110
    for txt, f, c in linhas:
        for ln in quebra(txt, f, w - 80):
            d.text((w / 2, y), ln, font=f, fill=c, anchor="mm")
            y += f.size + 14
        y += 10
    return im


def frame(fi):
    t = fi / FPS
    img = mesa().copy()
    fo, pena = folha(t)
    sombra = Image.new("RGBA", (PWID + 60, PHGT + 60), (0, 0, 0, 0))
    ImageDraw.Draw(sombra).rectangle((30, 30, PWID + 30, PHGT + 30), fill=(0, 0, 0, 120))
    sombra = sombra.filter(ImageFilter.GaussianBlur(18))
    sc = 1.0 if t < T_CTA else 1.0 - 0.0 * ease((t - T_CTA) / 0.4)
    E.cola(img, sombra, PX + PWID // 2 + 14, PY + PHGT // 2 + 18, PROT, sc, 1)
    E.cola(img, fo, PX + PWID // 2, PY + PHGT // 2, PROT, sc, 1)
    if pena is not None and t < T_CARIMBO:  # caneta na ponta do texto (coordenadas da folha → tela)
        a = math.radians(-PROT)
        px, py = pena[0] - PWID / 2, pena[1] - PHGT / 2
        sx = PX + PWID / 2 + px * math.cos(a) - py * math.sin(a)
        sy = PY + PHGT / 2 + px * math.sin(a) + py * math.cos(a)
        cn = caneta().rotate(28, expand=True, resample=Image.BICUBIC)
        img.alpha_composite(cn, (int(sx - (cn.width / 2 - 89)), int(sy - (cn.height / 2 - 168))))
    if t >= T_CARIMBO:  # carimbo bate
        u = (t - T_CARIMBO) / 0.18
        s = 1.6 - 0.6 * ease(u) if u < 1 else 1.0
        E.cola(img, carimbo(), 560, 1150, -6, s * 0.9, min(1, u))
    for i, (nome, t0, rot) in enumerate(POLA):
        if t >= T_POLA[i]:
            u = (t - T_POLA[i]) / 0.35
            p = polaroide(nome, t0, rot, t - T_POLA[i])
            x, y, r = (215, 1420, -7), (540, 1450, 4), (865, 1410, -3)
            xx, yy, rr = [x, y, r][i]
            sh = Image.new("RGBA", (p.width + 40, p.height + 40), (0, 0, 0, 0))
            ImageDraw.Draw(sh).rectangle((20, 26, p.width + 20, p.height + 26), fill=(0, 0, 0, 120))
            sh = sh.filter(ImageFilter.GaussianBlur(10))
            esc = (1.25 - 0.25 * ease(u)) * 0.9
            E.cola(img, sh, xx + 8, yy + 10, rr, esc, min(1, u))
            E.cola(img, p, xx, yy - int(60 * (1 - ease(u))), rr, esc, min(1, u * 1.5))
            if u > 1:
                fita(img, xx, yy - 175, rr + 5)
    if T_POSTIT <= t < T_CTA:
        u = (t - T_POSTIT) / 0.3
        p = postit([("A gente leva os jogos", anton(64), (40, 30, 20)),
                    ("e fica o evento todo ensinando!", mao(54), TINTA),
                    ("amigo secreto · firma · família", mao(46), (120, 60, 20))], 720, 430)
        E.cola(img, p, 560, 600, 3, 1.3 - 0.3 * ease(u), min(1, u * 1.5))
    if t >= T_CTA:
        u = (t - T_CTA) / 0.35
        img.alpha_composite(Image.new("RGBA", (W, H), (20, 12, 6, int(140 * min(1, u)))))
        p = postit([("EVENTOS DE FIM DE ANO", anton(70), VERM),
                    ("A gente leva os jogos e fica o evento todo ensinando.", mao(52), TINTA),
                    ("ABC Paulista e São Paulo capital", mao(50), (40, 30, 20)),
                    (f"Orçamento: WhatsApp {C.WHATS}", anton(46), (20, 120, 60))], 860, 760)
        E.cola(img, p, W // 2, 820, -2, 1.2 - 0.2 * ease(u), min(1, u * 1.5))
        lg = C.kit.logo(230)
        E.cola(img, lg, W // 2, 330, 0, out_back(ease((t - T_CTA - 0.2) / 0.3)), 1)
        b = ease((t - T_CTA - 0.9) / 0.3)
        if b > 0:
            E.cola(img, E.pilula("COMENTA: QUAL EVENTO SEU PRECISAVA DE JOGOS?", 36, (255, 205, 40), (40, 30, 20)),
                   W // 2, 1320, 2, out_back(b), 1)
    if t < T_CTA:
        C.kit.marca(img)
    return img.convert("RGB")


def render(fi):
    return frame(fi).tobytes()


# ---------------------------------------------------------------- som
def risco(d):
    """Caneta no papel: chiado filtrado com pulsos."""
    t = S.t_(d)
    r = S.bp_fft(S.ruido(d), 1500, 6000) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 7 * t)))
    return r * S.env(d, 0.02, 0.05)


def baque():
    d = 0.4
    t = S.t_(d)
    return (np.sin(2 * np.pi * 90 * t) * np.exp(-t * 18) + S.lp(S.ruido(d), 900) * np.exp(-t * 30) * 0.6)


def audio():
    n = int(DUR * SR)
    fx = np.zeros(n)
    for i, t0 in enumerate(T_ITEM):
        dur = 0.75 if i < 4 else 1.6
        S.add(fx, risco(dur), t0, 0.5)
        if i < 4:
            S.add(fx, risco(0.3), t0 + dur + 0.05, 0.7)
    S.add(fx, risco(0.9), T_RABISCO, 0.4)
    S.add(fx, baque(), T_CARIMBO, 1.0)
    for t0 in T_POLA:
        S.add(fx, S.cartao() if hasattr(S, "cartao") else S.sopro(0.3), t0, 0.6)
    S.add(fx, S.cartao() if hasattr(S, "cartao") else S.sopro(0.3), T_POSTIT, 0.5)
    S.add(fx, S.sino(), T_CTA, 0.4)
    mus = S.musica_cafe(DUR)
    rampa = np.ones(n)
    tt = np.arange(n) / SR
    rampa[tt < T_CARIMBO] = 0.35  # música baixinha até o carimbo, depois sobe
    rampa = np.convolve(rampa, np.ones(int(0.3 * SR)) / int(0.3 * SR), "same")
    mus = mus[:n] * rampa
    com, sem = os.path.join(C.OUT, "lis_com.wav"), os.path.join(C.OUT, "lis_sem.wav")
    os.makedirs(C.OUT, exist_ok=True)
    S.grava(com, DUR, [(0, fx, 1.0)], mus, musica_ganho=0.45, fx_ganho=0.9)
    S.grava(sem, DUR, [(0, fx, 1.0)], None, fx_ganho=0.9)
    return com, sem


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", nargs="*", type=float)
    a = ap.parse_args()
    C.prepara([(n, t0, 2.4) for n, t0, _ in POLA])
    if a.frame:
        C.folha([frame(int(x * FPS)) for x in a.frame], os.path.join(C.OUT, "frames_lis.jpg"))
        return
    com, sem = audio()
    C.entrega("lista", DUR, render, com, sem)
    print(C.chat(os.path.join(C.OUT, "lista_com_som_final.mp4")))
    print(C.chat(os.path.join(C.OUT, "lista_para_musica_final.mp4")))


if __name__ == "__main__":
    main()
