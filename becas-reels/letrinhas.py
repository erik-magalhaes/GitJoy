#!/usr/bin/env python3
"""2ª opção do convite da TARDE DE JOGOS NO BECAS (4/nov/2026), da 4ª referência que ele mandou: "GAME NIGHT" com
LETRAS DE MADEIRA tipo Scrabble (cada uma com o numerozinho de pontos), papel envelhecido com bolinhas vermelhas,
cartas de baralho espalhadas na borda, dados e uma pilha de caixas no canto, e o texto em letra de pixel (Silkscreen).
As cartas e os dados são desenhados em formas simples; as caixas são as do acervo (recortes do site).

    /usr/bin/python3 letrinhas.py    # out/letrinhas/post_1080x1350.png, story_1080x1920.png, folha.jpg
"""
import math
import os
import random
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import kit as K
import estilos as ST
from kit import TB

OUT = os.path.join(K.OUT, "letrinhas")
FD = os.path.join(K.REPO, "comum", "fontes")
PAPEL = (236, 214, 170)
VERMELHO = (196, 40, 44)
TINTA = (24, 20, 18)
PONTOS = {"T": 1, "A": 1, "R": 1, "D": 2, "E": 1, "J": 8, "O": 1, "G": 2, "S": 1, "!": 0}


@lru_cache(None)
def F(nome, s):
    return ImageFont.truetype(os.path.join(FD, nome), int(s))


def ruido(w, h, escala, seed):
    rng = np.random.default_rng(seed)
    a = rng.random((h // escala + 2, w // escala + 2))
    return np.asarray(Image.fromarray((a * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255


def papel(W, H):
    base = np.array(PAPEL, np.float32)[None, None, :] * np.ones((H, W, 1), np.float32)
    n = (ruido(W, H, 120, 1) - 0.5) * 40 + (ruido(W, H, 8, 2) - 0.5) * 16
    yy, xx = np.mgrid[0:H, 0:W]
    borda = np.clip(1 - ((xx - W / 2) / (W * 0.62)) ** 2 - ((yy - H / 2) / (H * 0.62)) ** 2, 0, 1)
    a = base + n[..., None] - (1 - borda[..., None]) * np.array([40, 50, 60])  # cantos queimados
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(img)
    passo = 150
    for j, y in enumerate(range(40, H, passo // 2)):  # bolinhas vermelhas em quincôncio
        for x in range(40 + (passo // 2 if j % 2 else 0), W, passo):
            d.ellipse((x - 17, y - 17, x + 17, y + 17), fill=VERMELHO)
    return img


@lru_cache(None)
def peca(letra, tam=170, seed=0):
    """Letra de madeira: madeira clara com veio, cantos levemente gastos, letra preta e o número de pontos."""
    rnd = random.Random(seed)
    tons = [(224, 196, 150), (210, 176, 128), (236, 218, 178), (196, 160, 112), (240, 150, 80)]
    base = np.array(tons[rnd.randrange(len(tons))], np.float32)
    w = h = tam
    y = np.arange(h)[:, None]
    x = np.arange(w)[None, :]
    n = ruido(w, h, 30, seed + 9)
    veio = np.sin((y * 0.12 + n * 6 + rnd.uniform(0, 6)) * 1.0) * 0.5 + 0.5
    a = base[None, None, :] + (veio[..., None] - 0.5) * 26 + (ruido(w, h, 3, seed + 3)[..., None] - 0.5) * 14
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), int(tam * 0.08), fill=255)
    im.putalpha(m)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((3, 3, w - 4, h - 4), int(tam * 0.08), outline=(150, 112, 70, 160), width=4)
    f = F("ArchivoBlack-Regular.ttf", int(tam * 0.62))
    d.text((w * 0.47, h * 0.48), letra, font=f, fill=TINTA, anchor="mm")
    p = PONTOS.get(letra, 1)
    if p:
        d.text((w * 0.84, h * 0.84), str(p), font=F("ArchivoBlack-Regular.ttf", int(tam * 0.18)), fill=TINTA,
               anchor="mm")
    sh = Image.new("RGBA", (w + 30, h + 30), (0, 0, 0, 0))
    sh.paste((60, 30, 20, 140), (10, 14), m)
    sh = sh.filter(ImageFilter.GaussianBlur(5))
    sh.alpha_composite(im, (4, 4))
    return sh.rotate(rnd.uniform(-7, 7), expand=True, resample=Image.BICUBIC)


def palavra(img, txt, cx, cy, tam, seed=0, espaco=0.08):
    n = len(txt)
    passo = tam * (1 + espaco)
    x = cx - passo * (n - 1) / 2
    rnd = random.Random(seed)
    for k, ch in enumerate(txt):
        p = peca(ch, tam, seed * 20 + k)
        img.alpha_composite(p, (int(x - p.width / 2), int(cy - p.height / 2 + rnd.uniform(-10, 10))))
        x += passo


NAIPES = ["♠", "♥", "♣", "♦"]


@lru_cache(None)
def carta(valor, naipe, h=320):
    w = int(h * 0.7)
    cor = VERMELHO if naipe in "♥♦" else TINTA
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), int(h * 0.06), fill=(250, 248, 242), outline=(170, 170, 170), width=2)
    fv = F("ArchivoBlack-Regular.ttf", int(h * 0.11))
    fn = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(h * 0.1))
    fg = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(h * 0.36))
    d.text((h * 0.07, h * 0.04), valor, font=fv, fill=cor)
    d.text((h * 0.075, h * 0.17), naipe, font=fn, fill=cor)
    d.text((w / 2, h / 2), naipe, font=fg, fill=cor, anchor="mm")
    sh = Image.new("RGBA", (w + 30, h + 30), (0, 0, 0, 0))
    sh.paste((40, 20, 10, 110), (10, 12), im.getchannel("A"))
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    sh.alpha_composite(im, (4, 4))
    return sh


def cartas_borda(img, W, H, seed, y_ini):
    """Cartas espalhadas no pé e na lateral esquerda (como na referência)."""
    rnd = random.Random(seed)
    vals = ["A", "7", "8", "10", "J", "Q", "K", "2", "3", "9"]
    pos = [(x, y_ini + rnd.uniform(-40, 90)) for x in range(-40, W + 120, 170)]
    pos += [(rnd.uniform(-90, -10), y) for y in range(int(y_ini * 0.35), int(y_ini), 260)]
    for k, (x, y) in enumerate(pos):
        c = carta(rnd.choice(vals), NAIPES[k % 4], rnd.choice([300, 330, 360]))
        c = c.rotate(rnd.uniform(-35, 35), expand=True, resample=Image.BICUBIC)
        img.alpha_composite(c, (int(x - c.width / 2), int(y)))


def dado_simples(s, n, seed):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((3, 3, s - 4, s - 4), int(s * 0.18), fill=(240, 226, 204), outline=(120, 80, 60), width=4)
    P = {5: [(.27, .27), (.73, .27), (.5, .5), (.27, .73), (.73, .73)], 3: [(.27, .27), (.5, .5), (.73, .73)],
         6: [(.27, .25), (.73, .25), (.27, .5), (.73, .5), (.27, .75), (.73, .75)]}[n]
    for px, py in P:
        r = s * 0.08
        d.ellipse((px * s - r, py * s - r, px * s + r, py * s + r), fill=VERMELHO)
    sh = Image.new("RGBA", (s + 24, s + 24), (0, 0, 0, 0))
    sh.paste((40, 20, 10, 120), (8, 12), im.getchannel("A"))
    sh = sh.filter(ImageFilter.GaussianBlur(5))
    sh.alpha_composite(im, (2, 2))
    return sh.rotate(random.Random(seed).uniform(-30, 30), expand=True, resample=Image.BICUBIC)


@lru_cache(None)
def caixa(nome, h):
    cx = Image.open(os.path.join(K.REPO, "hobby-reels", "assets", "acervo", nome + ".png")).convert("RGBA")
    cx = cx.crop(cx.getbbox())
    cx = cx.resize((int(cx.width * h / cx.height), h), Image.LANCZOS)
    sh = Image.new("RGBA", (cx.width + 30, cx.height + 30), (0, 0, 0, 0))
    sh.paste((40, 20, 10, 130), (10, 14), cx.getchannel("A"))
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    sh.alpha_composite(cx, (4, 4))
    return sh


def cantos(img, W, H):
    for k, (nome, x, y, r) in enumerate((("dixit", W - 190, 170, -8), ("hitster", W - 330, 210, 10),
                                          ("telma", W - 150, 330, 6))):
        c = caixa(nome, 230).rotate(r, expand=True, resample=Image.BICUBIC)
        img.alpha_composite(c, (int(x - c.width / 2), int(y - c.height / 2)))
    for k, (x, y, n) in enumerate(((150, 150, 5), (290, 250, 3), (130, 330, 6))):
        dd = dado_simples(110, n, k)
        img.alpha_composite(dd, (int(x - dd.width / 2), int(y - dd.height / 2)))


def texto_pixel(img, linhas, cx, y, s, entre=1.5):
    d = ImageDraw.Draw(img)
    for li, (txt, cor) in enumerate(linhas):
        f = F("Silkscreen-Bold.ttf", s)
        while d.textlength(txt, font=f) > img.width - 120 and f.size > 20:
            f = F("Silkscreen-Bold.ttf", f.size - 2)
        d.text((cx + 3, y + 3), txt, font=f, fill=(250, 240, 220), anchor="mt")
        d.text((cx, y), txt, font=f, fill=cor, anchor="mt")
        y += s * entre
    return y


INFO = [("NO BECAS CAFÉ · DATA EM BREVE", TINTA), ("R$ 30 (R$ 15 VIRAM CAFÉ)", VERMELHO),
        ("A GENTE ENSINA TODOS OS JOGOS", TINTA), ("RESERVE: (11) 97793-3910", VERMELHO)]


def post():
    W, H = 1080, 1350
    img = papel(W, H)
    cantos(img, W, H)
    lg = K.logo(140)
    img.alpha_composite(lg, (int(W / 2 - lg.width / 2), 60))
    palavra(img, "TARDE", W / 2, 520, 168, 1)
    palavra(img, "DE", W / 2, 700, 150, 2)
    palavra(img, "JOGOS!", W / 2, 870, 150, 3)
    cartas_borda(img, W, H, 4, 1190)
    # faixa de papel para o texto não brigar com as bolinhas
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((70, 975, W - 70, 1175), 18, fill=(246, 232, 200), outline=(150, 112, 70), width=3)
    texto_pixel(img, INFO, W / 2, 995, 36, 1.3)
    return img


def story():
    W, H = 1080, 1920
    img = papel(W, H)
    cantos(img, W, H)
    lg = K.logo(160)
    img.alpha_composite(lg, (int(W / 2 - lg.width / 2), 120))
    palavra(img, "TARDE", W / 2, 640, 176, 1)
    palavra(img, "DE", W / 2, 830, 160, 2)
    palavra(img, "JOGOS!", W / 2, 1010, 160, 3)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((60, 1130, W - 60, 1450), 20, fill=(246, 232, 200), outline=(150, 112, 70), width=3)
    texto_pixel(img, INFO, W / 2, 1160, 40, 1.8)
    cartas_borda(img, W, H, 4, 1690)  # o adesivo de link vai entre o texto e as cartas (y ~1480–1640)
    return img


# ======================================================================= REELS
import sys  # noqa: E402

import sons as S  # noqa: E402

RW, RH, FPS = 1080, 1920, 30
TITULO = [("TARDE", 520, 176, 1), ("DE", 710, 160, 2), ("JOGOS!", 890, 160, 3)]
CAIR = 0.11                    # uma letra a cada 0,11 s
N_LET = sum(len(p[0]) for p in TITULO)
ABRE = N_LET * CAIR + 0.9
JOGOS = [("critter", 0.6, "CRITTER KITCHEN", "♠", "A"), ("sushi", 0.4, "SUSHI GO!", "♥", "K"),
         ("canvas", 1.4, "CANVAS", "♣", "Q"), ("art", 0.5, "ART SOCIETY", "♦", "J"),
         ("passaporte", 0.8, "PASSAPORTE MUNDO", "♠", "10"), ("unlock", 0.6, "UNLOCK!", "♥", "7")]
PJ = 1.9
INFO_T = ABRE + len(JOGOS) * PJ
RDUR = INFO_T + 6.4


@lru_cache(None)
def fundo_reels():
    img = papel(RW, RH)
    cantos(img, RW, RH)
    cartas_borda(img, RW, RH, 4, 1700)
    lg = K.logo(150)
    img.alpha_composite(lg, (int(RW / 2 - lg.width / 2), 70))
    return img


def titulo_reels(img, t, cair=True):
    k = 0
    for txt, cy, tam, seed in TITULO:
        n = len(txt)
        passo = tam * 1.08
        x = RW / 2 - passo * (n - 1) / 2
        rnd = random.Random(seed)
        for j, ch in enumerate(txt):
            t0 = k * CAIR
            dy = rnd.uniform(-10, 10)
            if not cair or t >= t0:
                q = 1.0 if not cair else min(1.0, (t - t0) / 0.18)
                p = peca(ch, tam, seed * 20 + j)
                y = cy + dy - (1 - q) ** 2 * 500
                img.alpha_composite(p, (int(x - p.width / 2), int(y - p.height / 2)))
            x += passo
            k += 1


@lru_cache(None)
def carta_moldura(valor, naipe, w=820, h=1060):
    cor = VERMELHO if naipe in "♥♦" else TINTA
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 46, fill=(250, 248, 242), outline=(170, 170, 170), width=3)
    fv = F("ArchivoBlack-Regular.ttf", 64)
    fn = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 56)
    for (x, y, rot) in ((50, 30, 0),):
        d.text((x, y), valor, font=fv, fill=cor)
        d.text((x + 4, y + 82), naipe, font=fn, fill=cor)
    d.text((w - 50, h - 30), valor, font=fv, fill=cor, anchor="rd")
    d.text((w - 54, h - 112), naipe, font=fn, fill=cor, anchor="rd")
    return im


def cena_jogo(img, t):
    k = min(len(JOGOS) - 1, int((t - ABRE) / PJ))
    u = t - ABRE - k * PJ
    nome, t0, titulo, naipe, valor = JOGOS[k]
    c = carta_moldura(valor, naipe).copy()
    fr = ST.cobre(K.quadro_clip(nome, *ST.FULL[nome], 1.0, t0 + u).convert("RGB"), 640, 820).convert("RGBA")
    m = Image.new("L", fr.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, 639, 819), 24, fill=255)
    c.paste(fr, (90, 120), m)
    sh = Image.new("RGBA", (c.width + 40, c.height + 40), (0, 0, 0, 0))
    sh.paste((40, 20, 10, 120), (14, 18), c.getchannel("A"))
    sh = sh.filter(ImageFilter.GaussianBlur(8))
    sh.alpha_composite(c, (4, 4))
    q = K.ease(min(1.0, u / 0.28))
    rot = (-5, 4, -3, 5, -4, 3)[k] + (1 - q) * 30 * (1 if k % 2 else -1)
    K.E.cola(img, sh, RW / 2 + (1 - q) * (1100 if k % 2 else -1100), 950, rot)
    d = ImageDraw.Draw(img)
    f = F("Silkscreen-Bold.ttf", 54 if len(titulo) < 13 else 44)
    w = d.textlength(titulo, font=f) + 60
    d.rounded_rectangle((RW / 2 - w / 2, 1530, RW / 2 + w / 2, 1620), 14, fill=(246, 232, 200), outline=(150, 112, 70),
                        width=3)
    n = int(max(0, u - 0.2) / 0.04)
    d.text((RW / 2, 1575), titulo[:n], font=f, fill=TINTA, anchor="mm")


INFO_R = [("NO BECAS CAFÉ", TINTA), ("DATA EM BREVE", VERMELHO), ("R$ 30 (R$ 15 VIRAM CAFÉ)", TINTA),
          ("A GENTE ENSINA TODOS OS JOGOS", TINTA), ("RESERVE: (11) 97793-3910", VERMELHO),
          ("COMENTA: QUAL JOGO VOCÊ", TINTA), ("QUER APRENDER?", TINTA)]


def cena_info(img, t):
    u = t - INFO_T
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((60, 1100, RW - 60, 1660), 20, fill=(246, 232, 200), outline=(150, 112, 70), width=3)
    n = int(u / 0.03)
    linhas = []
    for txt, cor in INFO_R:
        linhas.append((txt[:max(0, n)], cor))
        n -= len(txt)
        if n <= 0:
            break
    texto_pixel(img, linhas, RW / 2, 1135, 42, 1.75)


def quadro(t):
    img = fundo_reels().copy()
    if t < ABRE:
        titulo_reels(img, t)
    elif t < INFO_T:
        titulo_reels(img, t, False)
        img.alpha_composite(Image.new("RGBA", (RW, RH), (60, 30, 20, 90)))
        cena_jogo(img, t)
    else:
        titulo_reels(img, t, False)
        cena_info(img, t)
    return img.convert("RGB")


def render(fi):
    return quadro(fi / FPS).tobytes()


def batida_madeira():
    out = np.zeros(int(0.2 * S.SR))
    t = S.t_(0.2)
    s = np.sin(2 * np.pi * 820 * t) * S.env(0.2, 0.0005, 0.03) + S.bp_fft(S.ruido(0.2), 600, 4000) * S.env(
        0.2, 0.0005, 0.01) * 0.6
    S.add(out, s, 0, 0.9)
    return out


def audio(com, sem):
    ev = [(k * CAIR + 0.17, batida_madeira(), 0.7) for k in range(N_LET)]
    for k in range(len(JOGOS)):
        t0 = ABRE + k * PJ
        ev += [(t0, S.carta_vira(), 0.7), (t0 + 0.28, S.carta_vira(), 0.4)]
        ev += [(t0 + 0.2 + j * 0.04 * 2, S.bip(2200, 0.03), 0.18) for j in range(len(JOGOS[k][2]) // 2)]
    tot = sum(len(x[0]) for x in INFO_R)
    ev += [(INFO_T + j * 0.06, S.bip(1900, 0.03), 0.2) for j in range(tot // 2)]
    mus = S.musica_cafe(RDUR)
    S.grava(com, RDUR, ev, mus, musica_ganho=0.45, fx_ganho=0.85)
    S.grava(sem, RDUR, ev, None, fx_ganho=0.85)


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--reels" in sys.argv or "--frame" in sys.argv:
        K.prepara([(n, t0, d, 1.0) for n, (t0, d) in ST.FULL.items()])
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:]]
        K.folha([quadro(x) for x in ts], os.path.join(K.OUT, "frames_letrinhas.jpg"))
        print("ok", round(RDUR, 1))
        return
    if "--reels" in sys.argv:
        com, sem = os.path.join(K.OUT, "letrinhas_com.wav"), os.path.join(K.OUT, "letrinhas_sem.wav")
        audio(com, sem)
        K.entrega("letrinhas", RDUR, render, com, sem)
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
