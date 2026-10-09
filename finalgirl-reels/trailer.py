#!/usr/bin/env python3
"""Reels do Final Girl no visual 2, TRAILER SLASHER (escolha do dono): tela escura, facho de lanterna revelando
cada assassino, títulos vermelhos de filme de terror, relâmpagos e trilha de trailer. Caixas da edição
BRASILEIRA (Ludofun) e artes oficiais da Van Ryder (recortes_br.py). Narração do dono (9 falas).

    python3 trailer.py --frame 1 8 12      # quadros de teste em out/frames.jpg
    python3 trailer.py --only preview      # só a versão com legenda (+ 720p para o chat)
    python3 trailer.py                     # com e sem legenda
"""
import argparse
import math
import os
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "..", "comum"))
from motor import (W, H, FPS, WHITE, seg, ease, lerp, pop, quica, font, emoji, logo_card, cola, sombra,  # noqa
                   letreiro, pilula, default_subs, legenda, Linha, encode, previa_720p, folha)
import som  # noqa: E402
import som_fg  # noqa: E402,F401  (registra a música "terror" e os efeitos)

OUT = os.path.join(ROOT, "out")
REC = os.path.join(ROOT, "assets", "recortes")
CREEP = os.path.join(ROOT, "..", "voodoo-reels", "assets", "fonts", "Creepster-Regular.ttf")
VERM = (220, 24, 36)
INK = (12, 10, 14)
BARRA = 70  # faixas de cinema (em cima e embaixo)

ASSASSINOS = [("hans", "HANS", "O Terror em Happy Trails"), ("poltergeist", "POLTERGEIST", "A Assombração da Mansão Creech"),
              ("inkanyamba", "INKANYAMBA", "Massacre nos Bosques"), ("geppetto", "GEPPETTO", "Carnificina no Circo"),
              ("drmedo", "DR. MEDO", "Terror em Maple Lane")]

ROTEIRO = [
    "Você sobreviveria a um filme de terror?",
    "No Final Girl, você é a última sobrevivente, a final girl dos filmes de terror. E joga sozinho!",
    "Cada caixa é um filme diferente, com um assassino e um lugar.",
    "Aqui na Sua Vez tem a primeira temporada inteira: Hans, Poltergeist, Inkanyamba, Geppetto e o Dr. Medo.",
    "No seu turno, o tempo é curto: você corre, procura armas e tenta salvar as vítimas.",
    "Pra atacar ou fugir, você rola os dados: tirou 5 ou 6, deu certo!",
    "Aí é a vez do assassino: ele anda, ataca, e cada vítima que ele pega deixa ele mais forte.",
    "Quando acaba o baralho do Terror, chega o grande final: você contra ele, e só um sai vivo! "
    "Qual assassino você enfrentaria primeiro? Comenta!",
    "Aluga o Final Girl na Sua Vez: cinco dias de jogo, retira em Mauá ou recebe em casa. O link tá na bio!",
]
SCENES = [(0.0, 6.5)] + [(6.5 + 7 * k, 13.5 + 7 * k) for k in range(7)] + [(55.5, 66.5)]
COMENTA = 4.2  # dentro da cena 8: daqui em diante é o "comenta"
TL = Linha(os.path.join(ROOT, "narracao", "timeline.json"))
DUR = TL.tl["duracao"] if TL.tl else SCENES[-1][1]
SUBS = [tuple(x) for x in TL.tl["legendas"]] if TL.tl else default_subs(SCENES, ROTEIRO)


def scene_of(t):
    for i, (a, b) in enumerate(SCENES):
        if t < b:
            return i
    return len(SCENES) - 1


def creep(s):
    return ImageFont.truetype(CREEP, int(s))


# ---------------------------------------------------------------- imagens
@lru_cache(None)
def img(nome):
    return Image.open(os.path.join(REC, nome)).convert("RGBA")


@lru_cache(None)
def limpa(nome, h):
    """Imagem na altura h, sem bloquinhos de JPEG (denoise) e com nitidez leve."""
    import cv2
    im = img(nome)
    a = np.array(im)
    rgb = cv2.fastNlMeansDenoisingColored(np.ascontiguousarray(a[..., :3]), None, 3, 3, 7, 21)
    im = Image.merge("RGBA", (*Image.fromarray(rgb).split(), im.getchannel("A")))
    w = int(im.width * h / im.height)
    return im.resize((w, int(h)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.4, 70, 2))


@lru_cache(None)
def esfuma(nome, h, borda=0.16):
    """Arte (retangular) com as bordas sumindo no escuro: nada de retângulo aparecendo."""
    im = limpa(nome, h).copy()
    w_, h_ = im.size
    m = Image.new("L", (w_, h_), 0)
    bx, by = int(w_ * borda), int(h_ * borda * 0.7)
    ImageDraw.Draw(m).rounded_rectangle((bx, by, w_ - bx, h_ - by), radius=min(bx, by), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(max(bx, by) * 0.7))
    im.putalpha(Image.fromarray((np.array(m, np.float32) * np.array(im.getchannel("A"), np.float32) / 255).astype(np.uint8)))
    return im


@lru_cache(None)
def nevoa(k):
    """Camadas de névoa lisa (ruído grande bem desfocado: nada de granulado)."""
    rng = np.random.default_rng(k)
    a = rng.random((48, 27)).astype(np.float32)
    im = Image.fromarray((a * 255).astype(np.uint8), "L").resize((W * 2, H), Image.BICUBIC)
    return im.filter(ImageFilter.GaussianBlur(60))


@lru_cache(None)
def vinheta():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
    return np.clip(1.15 - d * 0.75, 0.25, 1)[..., None]


@lru_cache(None)
def facho_base(r):
    """Máscara do facho de lanterna (círculo com borda macia), em tamanho 2R x 2R."""
    R = int(r * 1.6)
    yy, xx = np.mgrid[-R:R, -R:R].astype(np.float32)
    d = np.sqrt(xx ** 2 + yy ** 2) / r
    return np.clip(1.25 - d, 0, 1) ** 1.6


def facho(cx, cy, r):
    m = np.zeros((H, W), np.float32)
    b = facho_base(int(r))
    R = b.shape[0] // 2
    x0, y0 = int(cx) - R, int(cy) - R
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + 2 * R), min(H, y0 + 2 * R)
    if xa < xb and ya < yb:
        m[ya:yb, xa:xb] = b[ya - y0:yb - y0, xa - x0:xb - x0]
    return m[..., None]


def fundo_escuro(t):
    """Preto azulado com névoa passando devagar."""
    base = np.zeros((H, W, 3), np.float32) + np.array([8, 9, 14], np.float32)
    nv = np.array(nevoa(1), np.float32)
    off = int((t * 30) % W)
    camada = nv[:, off:off + W] / 255.0
    base += camada[..., None] * np.array([26, 28, 38], np.float32)
    return base


def no_escuro(cena_rgba, t, cx, cy, r, luz=1.0, fundo=0.22):
    """Compõe a cena (imagem RGBA cheia) no escuro, revelada pelo facho de lanterna."""
    base = fundo_escuro(t)
    a = np.array(cena_rgba, np.float32)
    rgb, al = a[..., :3], a[..., 3:] / 255.0
    m = np.minimum(1.0, facho(cx, cy, r) * luz * 1.25)
    calor = np.array([1.06, 1.0, 0.9], np.float32)  # luz de lanterna levemente quente
    vis = rgb * (fundo + (1 - fundo) * m) * np.where(m > 0.05, calor, 1.0)
    out = base * (1 - al) + vis * al
    out += (m * 18 * np.array([1, 0.95, 0.8], np.float32)) * (1 - al)  # poeira iluminada pelo facho
    out *= vinheta()
    return out


def para_img(arr):
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def tela(*itens):
    """Monta uma camada RGBA cheia com (imagem, x, y, rot, escala, alpha) centrados."""
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for it in itens:
        cola(c, *it)
    return c


@lru_cache(None)
def titulo(txt, size, cor=VERM, brilho=True):
    """Título de filme de terror: Creepster vermelho com brilho e contorno escuro."""
    f = creep(size)
    linhas = txt.split("\n")
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    lw = max(tmp.textlength(l, font=f) for l in linhas)
    lh = size * 1.0
    w, h = int(lw + 80), int(lh * len(linhas) + 80)
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for k, l in enumerate(linhas):
        d.text((w / 2, 40 + lh * k + lh / 2), l, font=f, fill=cor, anchor="mm", stroke_width=4, stroke_fill=(30, 0, 0))
    if not brilho:
        return lay
    glow = Image.new("RGBA", (w, h), cor + (0,))
    glow.putalpha(lay.getchannel("A").filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * 0.7)))
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.alpha_composite(glow)
    out.alpha_composite(lay)
    return out


@lru_cache(None)
def frase(txt, size, cor=WHITE, fonte="Poppins-Black.ttf"):
    return letreiro(txt, size, cor, (0, 0, 0), 8, fonte)


def relampago(t, t0, d=0.35):
    """Brilho branco de relâmpago (dois clarões)."""
    u = t - t0
    if u < 0 or u > d:
        return 0.0
    return max(0.0, 1 - u / 0.08) * 0.85 + (0.5 if 0.14 < u < 0.2 else 0.0)


def tremor(t, amp=3.0):
    return amp * math.sin(t * 37.0), amp * math.cos(t * 29.0)


# ---------------------------------------------------------------- cenas
def cena_gancho(u, t):
    hans = esfuma("hans_grande.png", 2050, 0.12)
    z = 1.0 + 0.05 * u / 6.5
    hz = hans.resize((int(hans.width * z), int(hans.height * z)), Image.BICUBIC)
    c = tela((hz, W / 2, H / 2 + 120, 0, 1.0))
    # o facho procura no escuro e para no rosto
    k = ease(seg(u, 0.2, 1.8))
    cx = lerp(150, W / 2 + 20, k) + 18 * math.sin(u * 2.1)
    cy = lerp(1500, 700, k) + 12 * math.sin(u * 2.7)
    arr = no_escuro(c, t, cx, cy, 420 + 60 * k)
    out = para_img(arr)
    cola(out, frase("VOCÊ SOBREVIVERIA", 74), W / 2, 300, 0, 1.0)
    cola(out, titulo("A UM FILME\nDE TERROR?", 150), W / 2, 1360, -2, 1.0)
    return out, [relampago(t, 2.6), relampago(t, 4.9)]


def cena_sobrevivente(u, t):
    cx = limpa("caixa_base.png", 900)
    c = tela((sombra(cx, 30, (10, 26), 0.7), W / 2, 980, 0, 0.92 + 0.04 * ease(seg(u, 0, 6))))
    luz = ease(seg(u, 0.1, 0.5))
    arr = no_escuro(c, t, W / 2 + 25 * math.sin(u * 1.3), 980 + 15 * math.sin(u * 1.9), 520, luz)
    out = para_img(arr)
    cola(out, titulo("FINAL GIRL", 190), W / 2, 330, 0, pop(u, 0.4))
    cola(out, frase("você é a última sobrevivente", 50), W / 2, 500, 0, pop(u, 1.2))
    if u > 3.6:
        cola(out, pilula("1 JOGADOR · SOLO", 52, VERM, WHITE, WHITE), W / 2, 1560, -6, quica(u, 3.6))
    return out, [relampago(t, SCENES[1][0] + 0.05)]


def cena_filmes(u, t):
    ks = [k for k, _, _ in ASSASSINOS]
    pos = [(250, 830), (540, 800), (830, 830), (395, 1290), (685, 1290)]
    itens = []
    for i, (k, (x, y)) in enumerate(zip(ks, pos)):
        t0 = 0.5 + 0.55 * i
        if u >= t0:
            b = limpa(f"caixa_{k}.png", 470)
            itens.append((sombra(b, 18, (6, 16), 0.7), x, y + 40 * (1 - ease(seg(u, t0, t0 + 0.3))), (i - 2) * 2.5,
                          1.0, ease(seg(u, t0, t0 + 0.25))))
    c = tela(*itens)
    cx = 540 + 330 * math.sin(u * 0.9)
    cy = 1050 + 260 * math.sin(u * 0.6 + 1)
    arr = no_escuro(c, t, cx, cy, 560, fundo=0.30)
    out = para_img(arr)
    cola(out, titulo("CADA CAIXA\nÉ UM FILME", 140), W / 2, 330, 0, pop(u, 0.2))
    if u > 3.8:
        cola(out, pilula("1 ASSASSINO + 1 LUGAR", 50, VERM, WHITE, WHITE), W / 2, 1620 - 70, 3, quica(u, 3.8))
    return out, [relampago(t, SCENES[2][0] + 0.5 + 0.55 * i, 0.12) * 0.4 for i in range(5)]


def cena_assassinos(u, t):
    d = 7.0 / 5
    i = min(4, int(u / d))
    v = u - i * d
    k, nome, filme = ASSASSINOS[i]
    art = esfuma(f"assassino_{k}.png", 1500)
    z = 1.0 + 0.08 * v / d
    dx, dy = tremor(t, 2.0)
    c = tela((art, W / 2 + dx, 860 + dy, 0, z))
    arr = no_escuro(c, t, W / 2 + 40 * math.sin(v * 3), 700 + 30 * math.cos(v * 2), 560, fundo=0.18)
    out = para_img(arr)
    cola(out, titulo(nome, 170), W / 2, 1360, 0, pop(v, 0.05, 0.25))
    cola(out, frase(filme, 44, (235, 225, 225), "Poppins-ExtraBold.ttf"), W / 2, 1500, 0, pop(v, 0.2, 0.25))
    cola(out, pilula(f"{i + 1}/5", 34, INK, WHITE, VERM), 120, 180, 0, 1.0)
    return out, [relampago(t, SCENES[3][0] + i * d, 0.25)]


@lru_cache(None)
def mapa_camp():
    """Tabuleiro do acampamento (Happy Trails) tirado da arte oficial, escurecido."""
    im = Image.open(os.path.join(ROOT, "assets", "oficial", "FF1-compview.png")).convert("RGB")
    w, h = im.size
    m = im.crop((int(0.04 * w), int(0.33 * h), int(0.54 * w), int(0.97 * h)))
    m = m.resize((int(m.width * 1950 / m.height), 1950), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.2))
    m = m.convert("RGBA")
    al = Image.new("L", m.size, 0)
    ImageDraw.Draw(al).rounded_rectangle((120, 120, m.width - 120, m.height - 120), radius=120, fill=255)
    m.putalpha(al.filter(ImageFilter.GaussianBlur(90)))
    return m


def cena_turno(u, t):
    mp = mapa_camp()
    c = tela((mp, W / 2 - 60 * u / 7, H / 2, 0, 1.0))
    arr = no_escuro(c, t, 540 + 280 * math.sin(u * 0.8), 950 + 300 * math.sin(u * 0.5), 600, fundo=0.28)
    out = para_img(arr)
    cola(out, titulo("SEU TURNO", 150), W / 2, 280, 0, pop(u, 0.1))
    # ampulhetas do tempo (6) que vão acabando
    n = 6 - min(6, int(max(0, u - 1.0) / 0.9))
    for j in range(6):
        e = emoji("⏳", 78)
        cola(out, e, 215 + j * 130, 470, 0, 1.0, 1.0 if j < n else 0.18)
    cola(out, frase("o tempo é curto!", 46, (230, 220, 220), "Poppins-ExtraBold.ttf"), W / 2, 580, 0, pop(u, 0.6))
    acoes = [("🏃", "CORRER", 1.4), ("🪓", "PROCURAR ARMAS", 2.6), ("🆘", "SALVAR AS VÍTIMAS", 3.8)]
    for q, (ic, txt, t0) in enumerate(acoes):
        if u >= t0:
            p = pilula(txt, 56, INK, WHITE, VERM)
            y = 980 + q * 190
            cola(out, emoji(ic, 96), 150, y, 0, quica(u, t0))
            cola(out, p, 220 + p.width / 2, y, 0, pop(u, t0 + 0.1))
    return out, []


def dado(n, s=220, cor=(245, 242, 235), pip=(20, 20, 20)):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((4, 4, s - 5, s - 5), radius=int(s * 0.18), fill=cor, outline=(60, 60, 60), width=4)
    pos = {1: [(0.5, 0.5)], 2: [(0.27, 0.27), (0.73, 0.73)], 3: [(0.27, 0.27), (0.5, 0.5), (0.73, 0.73)],
           4: [(0.27, 0.27), (0.73, 0.27), (0.27, 0.73), (0.73, 0.73)],
           5: [(0.27, 0.27), (0.73, 0.27), (0.5, 0.5), (0.27, 0.73), (0.73, 0.73)],
           6: [(0.27, 0.25), (0.73, 0.25), (0.27, 0.5), (0.73, 0.5), (0.27, 0.75), (0.73, 0.75)]}
    r = s * 0.085
    for x, y in pos[n]:
        d.ellipse((x * s - r, y * s - r, x * s + r, y * s + r), fill=pip)
    return im


def cena_dados(u, t):
    finais = [2, 5, 6]
    out = para_img(no_escuro(tela(), t, 540, 1000, 600, fundo=0.0))
    cola(out, titulo("ROLE OS DADOS", 140), W / 2, 280, 0, pop(u, 0.1))
    for j, fnum in enumerate(finais):
        t0 = 0.8 + j * 0.15
        cai = ease(seg(u, t0, t0 + 1.0))
        rolando = u < t0 + 1.0
        face = (int(u * 14 + j * 3) % 6) + 1 if rolando else fnum
        x = 260 + j * 280
        y = lerp(-200, 980, cai) + (0 if cai >= 1 else -60 * math.sin(cai * math.pi * 3) * (1 - cai))
        rot = (1 - cai) * 540 * (1 if j % 2 else -1)
        ok = fnum >= 5 and u > 2.6
        dd = dado(face, 220, (180, 255, 190) if ok else (245, 242, 235))
        if u > 2.6 and fnum < 5:
            dd = dado(face, 220, (120, 120, 120), (40, 40, 40))
        cola(out, sombra(dd, 14, (6, 14), 0.6), x, y, rot, 1.0 + (0.08 * pop(u, 2.6) if ok else 0))
    if u > 2.8:
        cola(out, titulo("5 OU 6 =\nSUCESSO!", 130, (80, 230, 110)), W / 2, 1400, -2, pop(u, 2.8))
    return out, []


@lru_cache(None)
def vitima(s=150):
    """Silhueta de vítima (meeple) em branco."""
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((s * 0.34, s * 0.04, s * 0.66, s * 0.34), fill=(235, 235, 235))
    d.polygon([(s * 0.5, s * 0.3), (s * 0.95, s * 0.62), (s * 0.78, s * 0.72), (s * 0.68, s * 0.62),
               (s * 0.8, s * 0.98), (s * 0.58, s * 0.98), (s * 0.5, s * 0.74), (s * 0.42, s * 0.98),
               (s * 0.2, s * 0.98), (s * 0.32, s * 0.62), (s * 0.22, s * 0.72), (s * 0.05, s * 0.62)],
              fill=(235, 235, 235))
    return im


def cena_assassino(u, t):
    art = esfuma("assassino_hans.png", 1450)
    z = 0.92 + 0.22 * ease(seg(u, 0, 7))  # ele vem chegando
    dx, dy = tremor(t, 2.5)
    c = tela((art, 700 + dx, 900 + dy, 0, z))
    arr = no_escuro(c, t, 700, 700 + 20 * math.sin(u * 2), 580, fundo=0.20)
    out = para_img(arr)
    cola(out, titulo("A VEZ DO\nASSASSINO", 130), W / 2, 300, -2, pop(u, 0.1))
    mortes = [2.2, 3.6, 5.0]
    for j in range(3):
        y = 760 + j * 230
        if u < mortes[j]:
            cola(out, vitima(150), 150, y, 0, 1.0)
        elif u < mortes[j] + 0.5:
            cola(out, emoji("💀", 120), 150, y, 0, quica(u, mortes[j], 0.4))
        else:
            cola(out, emoji("💀", 120), 150, y, 0, 1.0, 0.85)
    # medidor de Sede de Sangue
    nivel = sum(1 for m in mortes if u >= m)
    mx, my = 960, 1180
    bar = Image.new("RGBA", (90, 520), (0, 0, 0, 0))
    db = ImageDraw.Draw(bar)
    for q in range(5):
        y0 = 520 - (q + 1) * 100
        db.rounded_rectangle((6, y0 + 8, 84, y0 + 92), radius=14, fill=VERM + (255,) if q < nivel + 1 else (60, 20, 24, 220),
                             outline=(255, 255, 255, 160), width=3)
    cola(out, bar, mx, my, 0, 1.0)
    cola(out, frase("SEDE DE\nSANGUE", 40, (255, 200, 200), "Poppins-Black.ttf"), mx - 20, my + 340, 0, 1.0)
    return out, [relampago(t, SCENES[6][0] + m, 0.15) * 0.6 for m in mortes]


@lru_cache(None)
def rosto_final_girl():
    """A 'final girl' da capa brasileira do Happy Trails (rosto em destaque)."""
    cx = img("caixa_hans.png")
    w, h = cx.size
    return cx.crop((int(0.30 * w), int(0.41 * h), int(0.80 * w), int(0.82 * h)))


def cena_final(u, t):
    if u < 2.0:  # baralho do Terror acabando
        out = para_img(no_escuro(tela(), t, 540, 960, 520, fundo=0.0))
        n = 8 - int(u / 0.25)
        for j in range(max(0, n)):
            carta = Image.new("RGBA", (380, 540), (0, 0, 0, 0))
            dc = ImageDraw.Draw(carta)
            dc.rounded_rectangle((0, 0, 379, 539), radius=26, fill=(40, 6, 10), outline=VERM, width=6)
            dc.text((190, 270), "TERROR", font=creep(80), fill=VERM, anchor="mm")
            cola(out, carta, W / 2 + j * 4, 960 - j * 6, -3 + j, 1.0)
        cola(out, frase("o baralho do Terror\nestá acabando...", 52), W / 2, 1450, 0, pop(u, 0.2))
        return out, []
    v = u - 2.0
    fg = limpa_rosto()
    hans = esfuma("assassino_hans.png", 1100)
    c = tela((fg, 285, 1000, 0, 1.0), (hans, 830, 980, 0, 1.0))
    arr = no_escuro(c, t, 540, 980, 760, fundo=0.25)
    out = para_img(arr)
    if v < 2.2:
        cola(out, titulo("GRANDE\nFINAL", 190), W / 2, 330, 0, pop(v, 0.0, 0.3))
        cola(out, titulo("VS", 170, WHITE), 560, 1000, 0, pop(v, 0.5, 0.3))
        cola(out, frase("só um sai vivo!", 60), W / 2, 1520, 0, pop(v, 1.0))
    else:
        w_ = v - 2.2
        escuro = Image.new("RGBA", (W, H), (0, 0, 0, 170))
        out.alpha_composite(escuro)
        cola(out, frase("QUAL ASSASSINO\nVOCÊ ENFRENTARIA?", 76), W / 2, 400, 0, pop(w_, 0.0))
        pos = [(200, 800), (540, 800), (880, 800), (370, 1150), (710, 1150)]
        for j, ((k, nome, _), (x, y)) in enumerate(zip(ASSASSINOS, pos)):
            th = limpa(f"assassino_{k}.png", 520)
            th = th.crop((0, 0, th.width, int(th.height * 0.62)))
            card = Image.new("RGBA", (th.width + 14, th.height + 14), WHITE)
            card.alpha_composite(th, (7, 7))
            card = card.resize((250, int(250 * card.height / card.width)), Image.LANCZOS)
            cola(out, card, x, y, (j - 2) * 3, pop(w_, 0.2 + j * 0.12))
            cola(out, frase(nome, 34, (255, 210, 210), "Poppins-Black.ttf"), x, y + card.height / 2 + 30, 0,
                 pop(w_, 0.3 + j * 0.12))
        cola(out, titulo("COMENTA AQUI!", 120), W / 2 - 40, 1470, -2, pop(w_, 0.9) * (1 + 0.04 * abs(math.sin(t * 6))))
        cola(out, emoji("👇", 100), 940, 1490 + 12 * math.sin(t * 9), 0, pop(w_, 1.0))
    return out, [relampago(t, SCENES[7][0] + 2.0, 0.3)]


@lru_cache(None)
def limpa_rosto():
    im = rosto_final_girl()
    h = 720
    im = im.resize((int(im.width * h / im.height), h), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.4, 60, 2))
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((70, 70, im.width - 70, im.height - 70), radius=80, fill=255)
    im.putalpha(m.filter(ImageFilter.GaussianBlur(55)))
    return im


def cena_cta(u, t):
    fundo = para_img(fundo_escuro(t) * vinheta())
    out = fundo
    cola(out, logo_card(320), W / 2, 200, 0, pop(u, 0.1))
    caixas = [("caixa_hans.png", 160, 760, -10), ("caixa_poltergeist.png", 300, 720, -5), ("caixa_drmedo.png", 920, 760, 10),
              ("caixa_geppetto.png", 780, 720, 5), ("caixa_inkanyamba.png", 540, 700, 0)]
    for j, (nome, x, y, r) in enumerate(caixas):
        cola(out, sombra(limpa(nome, 430), 16, (6, 16), 0.7), x, y, r, pop(u, 0.25 + j * 0.08))
    cola(out, sombra(limpa("caixa_base.png", 450), 18, (8, 18), 0.75), W / 2, 780, 0, pop(u, 0.7))
    cola(out, titulo("ALUGUE O\nFINAL GIRL", 120), W / 2, 1070, -2, pop(u, 1.0))
    itens = [(1.3, pilula("1 JOGADOR · 20 A 60 MIN · 14+", 36, INK, WHITE, VERM), 1258),
             (1.5, pilula("5 DIAS DE JOGO", 44, VERM), 1336),
             (1.7, pilula("RESERVE ONLINE · RETIRE EM MAUÁ E ABC", 31, WHITE, INK, INK), 1408),
             (1.9, pilula("OU RECEBA EM CASA!", 38, (22, 163, 74)), 1478),
             (2.1, pilula("LINK NA BIO · @SUAVEZ_BG", 46, (249, 115, 22)), 1560)]
    for t0, im, y in itens:
        if u >= t0:
            cola(out, im, W / 2, y, 0, pop(u, t0))
    return out, [relampago(t, SCENES[8][0] + 0.05, 0.25)]


CENAS = [cena_gancho, cena_sobrevivente, cena_filmes, cena_assassinos, cena_turno, cena_dados, cena_assassino,
         cena_final, cena_cta]


def frame_at(t):
    i = scene_of(t)
    a, b = SCENES[i]
    out, flashes = CENAS[i](t - a, t)
    fl = max([0.0] + flashes)
    if fl > 0:
        out = Image.blend(out.convert("RGB"), Image.new("RGB", (W, H), (235, 240, 255)), min(0.85, fl)).convert("RGBA")
    # transição: corte para o preto rápido entre cenas
    fade = min(1.0, seg(t, a, a + 0.18)) * (1 - seg(t, b - 0.12, b)) if i < len(SCENES) - 1 else min(1.0, seg(t, a, a + 0.18))
    if fade < 1:
        out = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), out.convert("RGB"), fade).convert("RGBA")
    if i < len(SCENES) - 1:  # faixas de cinema
        d = ImageDraw.Draw(out)
        d.rectangle((0, 0, W, BARRA), fill=(0, 0, 0))
        d.rectangle((0, H - BARRA, W, H), fill=(0, 0, 0))
    return out


def em_cta(to):
    return scene_of(to) == len(SCENES) - 1


def render_frame(args):
    fi, subs = args
    t = fi / FPS
    to = TL.to_orig(t)
    im = frame_at(to)
    if not em_cta(to):
        wm = logo_card(160)
        im.alpha_composite(wm, (W - wm.width - 30, 40 + BARRA - 20))
    if subs and not em_cta(to):
        legenda(im, SUBS, t, y=1740)
    return im.convert("RGB").tobytes()


def cues():
    c = [(0.0, "braam", 0.8), (0.25, "lanterna", 0.6), (2.6, "trovao", 0.8), (4.9, "trovao", 0.6), (5.2, "riser", 0.5)]
    a = SCENES[1][0]
    c += [(a, "braam", 0.7), (a + 0.1, "lanterna", 0.5), (a + 3.6, "stinger", 0.4)]
    a = SCENES[2][0]
    c += [(a + 0.5 + 0.55 * i, "whoosh", 0.5) for i in range(5)] + [(a + 3.8, "braam", 0.5)]
    a = SCENES[3][0]
    c += [(a + i * 1.4, "braam" if i % 2 == 0 else "trovao", 0.65) for i in range(5)]
    a = SCENES[4][0]
    c += [(a + 1.0 + 0.9 * j, "ampulheta", 0.4) for j in range(6)] + [(a + x, "pop", 0.35) for x in (1.4, 2.6, 3.8)]
    a = SCENES[5][0]
    c += [(a + 0.8, "dados", 0.9), (a + 1.8, "dados", 0.6), (a + 2.6, "ding", 0.5), (a + 2.8, "braam", 0.4)]
    a = SCENES[6][0]
    c += [(a + 0.1, "braam", 0.6)] + [(a + m, "grito", 0.6) for m in (2.2, 3.6, 5.0)]
    a = SCENES[7][0]
    c += [(a + j * 0.25, "flip", 0.3) for j in range(8)] + [(a + 1.8, "riser", 0.6), (a + 2.0, "braam", 0.9),
                                                             (a + 2.0, "trovao", 0.7), (a + 2.5, "stinger", 0.4),
                                                             (a + 4.2, "whoosh", 0.4), (a + 5.1, "boing", 0.3)]
    a = SCENES[8][0]
    c += [(a + 0.05, "braam", 0.7), (a + 1.0, "stinger", 0.3), (a + 2.1, "ding", 0.5)]
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    ap.add_argument("--only", choices=["preview", "limpo"])
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.frame:
        folha([Image.frombytes("RGB", (W, H), render_frame((int(round(x * FPS)), True))) for x in a.frame],
              os.path.join(OUT, "frames.jpg"))
        return
    wav = os.path.join(OUT, "trilha.wav")
    voz = [(os.path.join(ROOT, v["arquivo"]), v["inicio"]) for v in TL.tl["voz"]] if TL.tl else None
    som.build(wav, DUR, cues(), musica="terror", warp=TL.warp, voz=voz, fx_ganho=0.55, musica_ganho=0.32,
              satura=voz is None)
    n = int(DUR * FPS)
    if a.only != "limpo":
        encode(os.path.join(OUT, "finalgirl_preview.mp4"), render_frame, [(j, True) for j in range(n)], wav)
        previa_720p(os.path.join(OUT, "finalgirl_preview.mp4"), os.path.join(OUT, "finalgirl_preview_720p.mp4"), 6000)
    if a.only != "preview":
        encode(os.path.join(OUT, "finalgirl_limpo.mp4"), render_frame, [(j, False) for j in range(n)], wav)


if __name__ == "__main__":
    main()
