#!/usr/bin/env python3
"""Reels B do Becas: TABULEIRO ROXO + LIMA (referência "noite de jogos" do Pinterest, 3/nov/2026). Roxo vibrante com
grão, tabuleiro creme com trilha de casas; título minúsculo gordo (Unbounded) com o "de" numa mancha lima; caixas como
cartas de borda lima. A cada jogo, dois dados rolam, a "peça" (casa acesa em lima) anda na trilha e a cena REAL de jogo
deles aparece dentro do tabuleiro, com "casa N: ..." e a carta lima com o nome. Som: dados, cartas, marimba saltitante.

    /usr/bin/python3 v_tabuleiro.py --frame 1 2.8 3.4 5 9 18 21 25
    /usr/bin/python3 v_tabuleiro.py       # out/tabuleiro_{com_som,para_musica}_final.mp4
"""
import math
import os
import random
import sys
from functools import lru_cache

from PIL import Image, ImageDraw

import kit as K
import sons as S
import estilos as ST
from kit import W, H, FPS, ease, out_back

JOGOS = [("critter", 0.6, "critter kitchen", "1 a 5 jogadores · 60 min", "casa 3: hora da cozinha!"),
         ("sushi", 0.4, "sushi go!", "2 a 5 jogadores · 15 min", "casa 7: monte seu prato"),
         ("canvas", 1.4, "canvas", "1 a 5 jogadores · 30 min", "casa 10: pinte sua obra"),
         ("art", 0.5, "art society", "2 a 4 jogadores · 60 min", "casa 14: arremate o quadro"),
         ("unlock", 0.6, "unlock!", "1 a 6 jogadores · 90 min", "casa 19: fuja da sala"),
         ("taketime", 3.0, "take time", "2 a 4 jogadores · 30 min", "casa 23: contra o relógio")]
CASAS = [3, 7, 10, 14, 19, 23]
GANCHO = 3.2
PJ = 2.5
DADOS = 0.55                  # dados rolando no começo de cada jogo
INFO = GANCHO + len(JOGOS) * PJ
CTA = INFO + 4.0
DUR = CTA + 4.8
BX0, BY0, BX1, BY1 = 70, 300, W - 70, 1500   # tabuleiro
CASA = 82
ROXO, LIMA, CREME, PRETO = ST.ROXO, ST.LIMA, ST.CREME_B, ST.PRETO_B


@lru_cache(None)
def base_tab():
    img = ST.fundo_roxo().copy()
    area = ST.tabuleiro(img, BX0, BY0, BX1, BY1, CASA)
    return img, area


def perimetro():
    """Retângulos das casas da trilha, em sentido horário a partir do canto de cima à esquerda."""
    xi, yi, xf, yf = BX0 + CASA, BY0 + CASA, BX1 - CASA, BY1 - CASA
    nx, ny = int((xf - xi) / CASA), int((yf - yi) / CASA)
    cw, ch = (xf - xi) / nx, (yf - yi) / ny
    out = []
    for k in range(nx):
        out.append((xi + k * cw, BY0 + 12, xi + (k + 1) * cw, yi))
    for k in range(ny):
        out.append((xf, yi + k * ch, BX1 - 12, yi + (k + 1) * ch))
    for k in range(nx):
        out.append((xf - (k + 1) * cw, yf, xf - k * cw, BY1 - 12))
    for k in range(ny):
        out.append((BX0 + 12, yf - (k + 1) * ch, xi, yf - k * ch))
    return out


PER = perimetro()


def acende(img, idx, numero=True):
    x0, y0, x1, y1 = PER[idx % len(PER)]
    d = ImageDraw.Draw(img)
    d.rectangle((x0 + 5, y0 + 5, x1 - 4, y1 - 4), fill=LIMA)
    if numero:
        d.text(((x0 + x1) / 2, (y0 + y1) / 2), str(idx), font=ST.F("DelaGothicOne-Regular.ttf", 30), fill=PRETO,
               anchor="mm")


@lru_cache(None)
def dado_face(n, s=170):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((4, 4, s - 5, s - 5), 28, fill=(248, 246, 240), outline=PRETO, width=7)
    P = {1: [(.5, .5)], 2: [(.28, .28), (.72, .72)], 3: [(.28, .28), (.5, .5), (.72, .72)],
         4: [(.28, .28), (.72, .28), (.28, .72), (.72, .72)], 5: [(.28, .28), (.72, .28), (.5, .5), (.28, .72),
                                                                 (.72, .72)],
         6: [(.28, .25), (.72, .25), (.28, .5), (.72, .5), (.28, .75), (.72, .75)]}
    for px, py in P[n]:
        r = s * 0.08
        d.ellipse((px * s - r, py * s - r, px * s + r, py * s + r), fill=PRETO)
    return ST.sombra(im, 8, (6, 10), 130)


def rola_dados(img, u, soma, seed):
    """Dois dados quicando no meio do tabuleiro; param na soma que dá o avanço."""
    a = min(soma - 1, 6)
    b = soma - a
    rnd = random.Random(seed)
    for j, final in enumerate((a, b)):
        q = min(1.0, u / DADOS)
        face = final if q >= 0.85 else rnd.Random(int(u * 30) + j).randint(1, 6) if False else \
            random.Random(int(u * 30) * 7 + j + seed).randint(1, 6)
        x = W / 2 + (-120 if j == 0 else 120) + (1 - q) * (-400 if j == 0 else 400)
        y = 900 - abs(math.sin(q * math.pi * 3)) * 160 * (1 - q)
        ST.cola(img, dado_face(final if q >= 0.85 else face), x, y, (1 - q) * 720 * (1 if j else -1))


def carta_nome(titulo, ficha):
    et = Image.new("RGBA", (640, 210), (0, 0, 0, 0))
    de = ImageDraw.Draw(et)
    de.rounded_rectangle((0, 0, 639, 209), 28, fill=LIMA, outline=PRETO, width=7)
    f = ST.F("Unbounded.ttf", 64 if len(titulo) < 12 else 52, (900,))
    de.text((40, 72), titulo, font=f, fill=PRETO, anchor="lm")
    de.text((40, 152), ficha, font=ST.F("SpaceGrotesk.ttf", 36, (700,)), fill=PRETO, anchor="lm")
    return ST.sombra(et, 8, (6, 10), 130)


def titulo_grande(img, t, y0=760):
    d = ImageDraw.Draw(img)
    f1 = ST.F("Unbounded.ttf", 158, (900,))
    for txt, t0, y in (("tarde", 0.35, y0), ("jogos", 1.25, y0 + 290)):
        a, s = K.surge(t, t0, 0.3)
        if a > 0:
            im = Image.new("RGBA", (900, 220), (0, 0, 0, 0))
            ImageDraw.Draw(im).text((450, 110), txt, font=f1, fill=PRETO, anchor="mm")
            K.E.cola(img, im, W / 2, y, 0, s, a)
    a, s = K.surge(t, 0.8, 0.3)
    if a > 0:
        m = ST.mancha(260, 170, LIMA).copy()
        ImageDraw.Draw(m).text((130, 82), "de", font=ST.F("Unbounded.ttf", 108, (900,)), fill=PRETO, anchor="mm")
        K.E.cola(img, m, W / 2, y0 + 145, -4, s, a)


CARTAS = [("hitster", 150, 200, -18), ("dixit", 950, 190, 14), ("telma", 140, 1690, 12), ("uga_buga", 950, 1680, -12)]


@lru_cache(None)
def carta_cx(nome):
    return ST.carta_caixa(nome, 250)


def cartas_cantos(img, t, t0=1.6):
    for k, (nome, x, y, r) in enumerate(CARTAS):
        q = ease(min(1.0, max(0.0, (t - t0 - k * 0.15) / 0.35)))
        if q > 0:
            sx = x + (1 - q) * (-500 if x < W / 2 else 500)
            ST.cola(img, carta_cx(nome), sx, y, r * q)


def cena_gancho(t):
    img, area = base_tab()
    img = img.copy()
    cartas_cantos(img, t)
    titulo_grande(img, t)
    d = ImageDraw.Draw(img)
    if t > 0.1:
        d.rounded_rectangle((W / 2 - 250, 520 - 34, W / 2 + 250, 520 + 34), 34, outline=PRETO, width=4)
        d.text((W / 2, 520), "sua vez × becas café", font=ST.F("SpaceGrotesk.ttf", 36, (700,)), fill=PRETO,
               anchor="mm")
    if t > 2.0:
        d.text((W / 2, 1330), "BORA JOGAR?", font=ST.F("DelaGothicOne-Regular.ttf", 64), fill=PRETO, anchor="mm")
    acende(img, int(t * 6) % len(PER), False)
    return img


def cena_jogo(t):
    k = min(len(JOGOS) - 1, int((t - GANCHO) / PJ))
    u = t - GANCHO - k * PJ
    nome, t0, titulo, ficha, frase = JOGOS[k]
    img, area = base_tab()
    img = img.copy()
    casa_ant = CASAS[k - 1] if k else 0
    passo = casa_ant + int((CASAS[k] - casa_ant) * min(1.0, max(0.0, (u - DADOS) / 0.5)))
    if u < DADOS:  # dados rolando sobre o tabuleiro vazio
        acende(img, casa_ant)
        rola_dados(img, u, CASAS[k] - casa_ant, k)
    else:
        w, h = int(area[2] - area[0]), int(area[3] - area[1])
        fr = ST.cobre(K.quadro_clip(nome, *ST.FULL[nome], 1.0, t0 + u - DADOS).convert("RGB"), w, h).convert("RGBA")
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 20, fill=255)
        q = ease(min(1.0, (u - DADOS) / 0.25))
        if q < 1:
            fr = fr.resize((max(1, int(w * (0.6 + 0.4 * q))), max(1, int(h * (0.6 + 0.4 * q)))))
            m = m.resize(fr.size)
        img.paste(fr, (int((area[0] + area[2]) / 2 - fr.width / 2), int((area[1] + area[3]) / 2 - fr.height / 2)), m)
        acende(img, passo)
        K.poe(img, carta_nome(titulo, ficha), 400, 1420, u, DADOS + 0.3, -4, d=0.25)
    d = ImageDraw.Draw(img)
    a, _ = K.surge(u, DADOS, 0.2)
    if a > 0:
        d.text((W / 2, 200), frase, font=ST.F("DelaGothicOne-Regular.ttf", 54), fill=LIMA, anchor="mm")
    img.alpha_composite(K.logo(150), (W - 180, 40))
    return img


INFO_CARTAS = [("becas café", "a tarde de jogos é lá"), ("R$ 30", "e R$ 15 viram café"),
               ("a gente ensina", "todos os jogos, mesa por mesa"), ("data em breve", "fica de olho aqui!")]


def cena_info(t):
    u = t - INFO
    img, area = base_tab()
    img = img.copy()
    acende(img, CASAS[-1])
    d = ImageDraw.Draw(img)
    d.text((W / 2, 200), "anota aí:", font=ST.F("Unbounded.ttf", 80, (900,)), fill=LIMA, anchor="mm")
    for k, (a_, b_) in enumerate(INFO_CARTAS):
        t0 = 0.3 + k * 0.6
        q = ease(min(1.0, max(0.0, (u - t0) / 0.35)))
        if q <= 0:
            continue
        c = Image.new("RGBA", (820, 210), (0, 0, 0, 0))
        dc = ImageDraw.Draw(c)
        dc.rounded_rectangle((0, 0, 819, 209), 28, fill=LIMA if k % 2 == 0 else (255, 255, 255), outline=PRETO,
                             width=7)
        dc.text((40, 72), a_, font=ST.F("Unbounded.ttf", 62, (900,)), fill=PRETO, anchor="lm")
        dc.text((40, 152), b_, font=ST.F("SpaceGrotesk.ttf", 38, (700,)), fill=PRETO, anchor="lm")
        ST.cola(img, ST.sombra(c, 8, (6, 10), 130), W / 2 + (1 - q) * 900, 520 + k * 250, (-3, 2, -2, 3)[k])
    img.alpha_composite(K.logo(150), (W - 180, 40))
    return img


def cena_cta(t):
    u = t - CTA
    img = ST.fundo_roxo().copy()
    cartas_cantos(img, u, 0.0)
    d = ImageDraw.Draw(img)
    K.poe(img, K.logo(240), W / 2, 470, u, 0.1)
    for txt, y, t0 in (("sua vez", 760, 0.2), ("de jogar!", 940, 0.45)):
        a, s = K.surge(u, t0, 0.3)
        if a > 0:
            im = Image.new("RGBA", (1000, 220), (0, 0, 0, 0))
            ImageDraw.Draw(im).text((500, 110), txt, font=ST.F("Unbounded.ttf", 150, (900,)), fill=LIMA, anchor="mm",
                                    stroke_width=6, stroke_fill=PRETO)
            K.E.cola(img, im, W / 2, y, 0, s, a)
    if u > 0.9:
        c = Image.new("RGBA", (860, 230), (0, 0, 0, 0))
        dc = ImageDraw.Draw(c)
        dc.rounded_rectangle((0, 0, 859, 229), 30, fill=CREME, outline=PRETO, width=7)
        dc.text((430, 80), "reserve sua mesa no whatsapp", font=ST.F("SpaceGrotesk.ttf", 40, (700,)), fill=PRETO,
                anchor="mm")
        dc.text((430, 160), "(11) 97793-3910", font=ST.F("Unbounded.ttf", 66, (900,)), fill=PRETO, anchor="mm")
        K.poe(img, ST.sombra(c, 8, (6, 10), 130), W / 2, 1200, u, 0.9, -2)
    if u > 1.6:
        d.text((W / 2, 1420), "comenta: qual jogo você quer aprender?", font=ST.F("SpaceGrotesk.ttf", 42, (700,)),
               fill=(255, 255, 255), anchor="mm")
    return img


def quadro(t):
    if t < GANCHO:
        img = cena_gancho(t)
    elif t < INFO:
        img = cena_jogo(t)
    elif t < CTA:
        img = cena_info(t)
    else:
        img = cena_cta(t)
    return img.convert("RGB")


def render(fi):
    return quadro(fi / FPS).tobytes()


def audio(com, sem):
    ev = [(0.35, S.cartao(), 0.6), (0.8, S.cartao(), 0.6), (1.25, S.cartao(), 0.6)]
    ev += [(1.6 + k * 0.15, S.carta_vira(), 0.6) for k in range(4)]
    for k in range(len(JOGOS)):
        t0 = GANCHO + k * PJ
        ev += [(t0, S.dado(), 0.9), (t0 + 0.12, S.dado(), 0.7)]
        passos = CASAS[k] - (CASAS[k - 1] if k else 0)
        ev += [(t0 + DADOS + j * 0.5 / passos, S.tique(), 0.35) for j in range(passos)]
        ev += [(t0 + DADOS + 0.3, S.carta_vira(), 0.6)]
    ev += [(INFO + 0.3 + k * 0.6, S.carta_vira(), 0.7) for k in range(4)]
    ev += [(CTA + 0.2, S.cartao(), 0.6), (CTA + 0.45, S.cartao(), 0.6), (CTA + 0.9, S.sino(), 0.4)]
    mus = S.musica_marimba_pop(DUR)
    S.grava(com, DUR, ev, mus, musica_ganho=0.45, fx_ganho=0.85)
    S.grava(sem, DUR, ev, None, fx_ganho=0.85)


def main():
    os.makedirs(K.OUT, exist_ok=True)
    K.prepara([(n, t0, d, 1.0) for n, (t0, d) in ST.FULL.items()])
    print("duração", round(DUR, 1))
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:]]
        K.folha([quadro(x) for x in ts], os.path.join(K.OUT, "frames_tabuleiro.jpg"))
        return
    com, sem = os.path.join(K.OUT, "tabuleiro_com.wav"), os.path.join(K.OUT, "tabuleiro_sem.wav")
    audio(com, sem)
    K.entrega("tabuleiro", DUR, render, com, sem)


if __name__ == "__main__":
    main()
