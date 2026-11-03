#!/usr/bin/env python3
"""Reels C do Becas: TVs RETRÔ (referência das TVs com tela verde do Pinterest, 3/nov/2026). Noite com luzes da cidade
desfocadas, TVs de madeira empilhadas (desenhadas: os bancos de foto estão bloqueados no proxy) que LIGAM uma a uma
com a cena REAL de jogo deles em cada tela; depois uma TV grande "zapeia" os canais (chiado entre eles, canal no canto
em fósforo verde, nome e ficha em âmbar), a TV mostra as informações sendo digitadas e o final volta para a pilha.
Som: TV de tubo ligando, chiado, bip de canal e chiptune.

    /usr/bin/python3 v_tvs.py --frame 1 2.6 4 8 14 18 22 25
    /usr/bin/python3 v_tvs.py             # out/tvs_{com_som,para_musica}_final.mp4
"""
import math
import os
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

import kit as K
import sons as S
import estilos as ST
from kit import W, H, FPS, ease

FOSF, AMBAR = ST.FOSF, ST.AMBAR
CANAIS = [("sushi", 0.4, "SUSHI GO!", "2 A 5 JOGADORES · 15 MIN"),
          ("critter", 0.6, "CRITTER KITCHEN", "1 A 5 JOGADORES · 60 MIN"),
          ("passaporte", 0.8, "PASSAPORTE MUNDO", "1 A 6 JOGADORES · 45 MIN"),
          ("unlock", 0.6, "UNLOCK!", "1 A 6 JOGADORES · 90 MIN"),
          ("art", 0.5, "ART SOCIETY", "2 A 4 JOGADORES · 60 MIN"),
          ("sky_dados", 3.5, "SKY TEAM", "2 JOGADORES · 20 MIN")]
LIGA = 3.0
PC = 2.2
INFO = LIGA + len(CANAIS) * PC
CTA = INFO + 4.4
DUR = CTA + 5.0
# pilha de TVs: (x, y, w, h, giro, com botões)
PILHA = [(290, 520, 480, 360, -2, True), (780, 560, 440, 340, 2, False), (300, 950, 500, 380, 1, True),
         (790, 990, 460, 360, -3, False), (300, 1390, 520, 380, -1, True), (790, 1420, 480, 360, 2, False)]


@lru_cache(None)
def gabinete(w, h, seed, botoes):
    """TV sem tela (a tela entra a cada quadro). Devolve imagem com sombra e a caixa da tela nela."""
    pw = int(w * 0.2) if botoes else 0
    im = ST.madeira(w, h, seed)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w - 1, h - 1), outline=(40, 26, 16), width=6)
    sx0, sy0, sx1, sy1 = 34, 34, w - pw - 34, h - 34
    d.rounded_rectangle((sx0 - 14, sy0 - 14, sx1 + 14, sy1 + 14), 40, fill=(28, 26, 24))
    if botoes:
        px = w - pw
        d.rectangle((px - 6, 22, w - 22, h - 22), fill=(52, 40, 30))
        for k in range(2):
            cy, cx = 90 + k * 120, px + pw / 2 - 10
            d.ellipse((cx - 40, cy - 40, cx + 40, cy + 40), fill=(30, 28, 26))
            d.ellipse((cx - 30, cy - 30, cx + 30, cy + 30), fill=(170, 160, 140))
            d.line((cx, cy, cx + 22 * math.cos(k + 1), cy - 22 * math.sin(k + 1)), fill=(40, 30, 20), width=6)
        for k in range(8):
            y = h * 0.55 + k * 18
            if y < h - 30:
                d.line((px + 16, y, w - 36, y), fill=(26, 20, 16), width=6)
    sh = ST.sombra(im, 18, (10, 16), 170)
    off = 2 * 18
    return sh, (sx0 + off, sy0 + off, sx1 + off, sy1 + off)


def tv_com(conteudo, w, h, seed, botoes, liga=1.0):
    """Gabinete + tela de tubo. liga < 1 = ligando (linha branca que abre)."""
    gab, (x0, y0, x1, y1) = gabinete(w, h, seed, botoes)
    im = gab.copy()
    sw, shh = x1 - x0, y1 - y0
    if liga <= 0:
        tela = Image.new("RGBA", (sw, shh), (12, 14, 14, 255))
    else:
        tela = ST.tela_crt(conteudo, sw, shh)
        if liga < 1:
            hh = max(4, int(shh * ease(liga)))
            fa = tela.resize((sw, hh))
            base = Image.new("RGBA", (sw, shh), (12, 14, 14, 255))
            branco = Image.new("RGBA", (sw, hh), (230, 255, 240, int(220 * (1 - liga))))
            fa.alpha_composite(branco)
            base.alpha_composite(fa, (0, (shh - hh) // 2))
            tela = base
    m = Image.new("L", (sw, shh), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, sw - 1, shh - 1), int(min(sw, shh) * 0.12), fill=255)
    im.paste(tela, (x0, y0), m)
    return im


def chiado(w, h, seed):
    rng = np.random.default_rng(seed)
    a = rng.integers(0, 255, (h // 3, w // 3), dtype=np.uint8)
    return Image.fromarray(a).resize((w, h), Image.NEAREST).convert("RGB")


def frame_clip(nome, t0, u):
    return K.quadro_clip(nome, *ST.FULL[nome], 1.0, t0 + u).convert("RGB")


@lru_cache(None)
def texto_tela(linhas, cores, tam=(900, 680), s=96, glow=True):
    im = Image.new("RGB", tam, (6, 22, 12))
    d = ImageDraw.Draw(im)
    y = tam[1] / 2 - len(linhas) * s * 0.6
    for l, c in zip(linhas, cores):
        d.text((tam[0] / 2, y + s * 0.6), l, font=ST.F("VT323-Regular.ttf", s), fill=c, anchor="mm")
        y += s * 1.2
    return ImageChops.screen(im, im.filter(ImageFilter.GaussianBlur(6))) if glow else im


def pilha(img, t, conteudos, t_liga):
    for k, (x, y, w, h, r, b) in enumerate(PILHA):
        liga = min(1.0, max(0.0, (t - t_liga - k * 0.3) / 0.3)) if t_liga is not None else 1.0
        ST.cola(img, tv_com(conteudos[k], w, h, 10 + k, b, liga), x, y, r)


def cena_liga(t):
    img = ST.noite().copy()
    ImageDraw.Draw(img).rectangle((0, 1700, W, H), fill=(26, 20, 16))
    conts = [frame_clip(c[0], c[1], t) for c in CANAIS]
    pilha(img, t, conts, 0.3)
    d = ImageDraw.Draw(img)
    if t > 0.2:
        d.text((W / 2, 200), "SINTONIZA AÍ!", font=ST.F("PressStart2P-Regular.ttf", 56), fill=FOSF, anchor="mm")
    if t > 2.3:
        d.text((W / 2, 1790), "TARDE DE JOGOS · BECAS CAFÉ", font=ST.F("VT323-Regular.ttf", 76), fill=AMBAR,
               anchor="mm")
    return img


# TV grande do zapping
TG = (1000, 860)
TELA_G = (732, 792)   # tamanho da tela da TV grande (para nada ser cortado)


def tv_grande(img, conteudo, liga=1.0):
    ST.cola(img, tv_com(conteudo, TG[0], TG[1], 3, True, liga), W / 2, 800, 0)


def cena_canal(t):
    k = min(len(CANAIS) - 1, int((t - LIGA) / PC))
    u = t - LIGA - k * PC
    nome, t0, titulo, ficha = CANAIS[k]
    img = ST.noite().copy()
    ImageDraw.Draw(img).rectangle((0, 1340, W, H), fill=(26, 20, 16))
    if u < 0.22:
        cont = chiado(*TELA_G, int(t * 60))
    else:
        cont = ST.cobre(frame_clip(nome, t0, u), *TELA_G)
        d = ImageDraw.Draw(cont)  # canal no canto, como na TV
        fw = cont.width
        d.text((fw * 0.06, cont.height * 0.06), f"CH {k + 3:02d}", font=ST.F("VT323-Regular.ttf", int(fw * 0.09)),
               fill=FOSF, stroke_width=3, stroke_fill=(0, 40, 10))
    tv_grande(img, cont, 1.0 if k else min(1.0, u / 0.3 + 0.01))
    d = ImageDraw.Draw(img)
    a = min(1.0, max(0.0, (u - 0.25) / 0.15))
    if a > 0:
        d.text((W / 2, 1420), titulo, font=ST.F("PressStart2P-Regular.ttf", 54 if len(titulo) < 13 else 44),
               fill=AMBAR, anchor="mm")
        d.text((W / 2, 1520), ficha, font=ST.F("VT323-Regular.ttf", 70), fill=FOSF, anchor="mm")
    d.text((W / 2, 200), "ZAPEANDO OS CANAIS...", font=ST.F("Silkscreen-Bold.ttf", 52), fill=(180, 255, 210),
           anchor="mm")
    img.alpha_composite(K.logo(150), (W - 180, 40))
    return img


INFO_TXT = ["> TARDE DE JOGOS", "> BECAS CAFÉ", "R$30 (R$15 EM CAFÉ)", "A GENTE ENSINA TUDO", "DATA EM BREVE_"]
INFO_COR = [FOSF, FOSF, AMBAR, (180, 255, 210), FOSF]


def cena_info(t):
    u = t - INFO
    img = ST.noite().copy()
    ImageDraw.Draw(img).rectangle((0, 1340, W, H), fill=(26, 20, 16))
    n = int(u / 0.035)
    linhas, resto = [], n
    for l in INFO_TXT:
        linhas.append(l[:max(0, resto)])
        resto -= len(l)
    cursor = "█" if int(u * 3) % 2 == 0 else " "
    tela = Image.new("RGB", TELA_G, (6, 22, 12))
    d = ImageDraw.Draw(tela)
    for k, (l, c) in enumerate(zip(linhas, INFO_COR)):
        d.text((40, 90 + k * 128), l + (cursor if l and len(l) < len(INFO_TXT[k]) else ""),
               font=ST.F("VT323-Regular.ttf", 76), fill=c)
    tela = ImageChops.screen(tela, tela.filter(ImageFilter.GaussianBlur(6)))
    tv_grande(img, tela)
    d = ImageDraw.Draw(img)
    d.text((W / 2, 200), "INFORMAÇÕES:", font=ST.F("Silkscreen-Bold.ttf", 56), fill=(180, 255, 210), anchor="mm")
    if u > 2.6:
        d.text((W / 2, 1440), "RESERVE: (11) 97793-3910", font=ST.F("VT323-Regular.ttf", 90), fill=AMBAR,
               anchor="mm")
        d.text((W / 2, 1530), "OU CHEGUE NO DIA", font=ST.F("VT323-Regular.ttf", 70), fill=FOSF, anchor="mm")
    img.alpha_composite(K.logo(150), (W - 180, 40))
    return img


def cena_cta(t):
    u = t - CTA
    img = ST.noite().copy()
    ImageDraw.Draw(img).rectangle((0, 1700, W, H), fill=(26, 20, 16))
    textos = [texto_tela(("SINTONIZE:",), (AMBAR,), (600, 460), 110),
              texto_tela(("BECAS", "CAFÉ"), (FOSF, FOSF), (600, 460), 120),
              None, None,
              texto_tela(("WHATSAPP", "(11) 97793", "-3910"), (FOSF, AMBAR, AMBAR), (600, 460), 92),
              texto_tela(("COMENTA:", "QUAL CANAL", "VOCÊ VÊ?"), (AMBAR, FOSF, FOSF), (600, 460), 84)]
    conts = []
    for k, tx in enumerate(textos):
        if tx is None:
            c = CANAIS[k]
            conts.append(frame_clip(c[0], c[1], u + 2))
        else:
            conts.append(tx)
    pilha(img, u, conts, None)
    img.alpha_composite(K.logo(200), (int(W / 2 - 100), 120))
    return img


def quadro(t):
    if t < LIGA:
        img = cena_liga(t)
    elif t < INFO:
        img = cena_canal(t)
    elif t < CTA:
        img = cena_info(t)
    else:
        img = cena_cta(t)
        if t - CTA < 0.2:
            img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(160 * (1 - (t - CTA) / 0.2)))))
    return img.convert("RGB")


def render(fi):
    return quadro(fi / FPS).tobytes()


def audio(com, sem):
    ev = [(0.3 + k * 0.3, S.crt_liga(), 0.6) for k in range(len(PILHA))]
    for k in range(len(CANAIS)):
        t0 = LIGA + k * PC
        if k == 0:
            ev += [(t0, S.crt_liga(), 0.8)]
        ev += [(t0, S.estatica(0.22), 0.8), (t0 + 0.22, S.bip(), 0.6)]
    ev += [(INFO, S.estatica(0.15), 0.6)]
    tot = sum(len(l) for l in INFO_TXT)
    ev += [(INFO + j * 0.035 * 2, S.bip(2600, 0.03), 0.25) for j in range(tot // 2)]
    ev += [(CTA, S.estatica(0.2), 0.7)] + [(CTA + 0.2 + k * 0.12, S.bip(1760 + 220 * k), 0.4) for k in range(4)]
    mus = S.musica_chip(DUR, 0.3)
    S.grava(com, DUR, ev, mus, musica_ganho=0.42, fx_ganho=0.85)
    S.grava(sem, DUR, ev, None, fx_ganho=0.85)


def main():
    os.makedirs(K.OUT, exist_ok=True)
    K.prepara([(n, t0, d, 1.0) for n, (t0, d) in ST.FULL.items()])
    print("duração", round(DUR, 1))
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:]]
        K.folha([quadro(x) for x in ts], os.path.join(K.OUT, "frames_tvs.jpg"))
        return
    com, sem = os.path.join(K.OUT, "tvs_com.wav"), os.path.join(K.OUT, "tvs_sem.wav")
    audio(com, sem)
    K.entrega("tvs", DUR, render, com, sem)


if __name__ == "__main__":
    main()
