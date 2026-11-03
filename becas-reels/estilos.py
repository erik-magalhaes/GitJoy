#!/usr/bin/env python3
"""Teste de 3 estilos NOVOS a partir das referências do Pinterest que ele mandou (3/nov/2026): "testa novas fontes, novas
cores, sair do basicão — até pros vídeos do dia a dia". Fontes novas (Google Fonts, OFL/Apache) em comum/fontes/.

  A COLAGEM / RECORTE: papel amassado com rasgos azuis, título de letras recortadas de revista (cada letra numa fonte e
    num papel), cena de jogo dentro de um rasgo, placa escrita à mão (Permanent Marker), dados em máquina de escrever.
  B TABULEIRO ROXO + LIMA: roxo vibrante com grão, tabuleiro creme com trilha de casas na borda, título minúsculo gordo
    (Unbounded/Dela Gothic) com "de" numa mancha lima, caixas como cartas soltas, o vídeo dentro do tabuleiro.
  C TVs RETRÔ: TVs de madeira empilhadas à noite (desenhadas), cada tela passando uma cena de jogo com linhas de CRT e
    brilho; uma tela mostra as informações em letra de fósforo verde (VT323 / Silkscreen).

    /usr/bin/python3 estilos.py     # out/estilos.jpg (2 quadros de cada) + out/estilos_fontes.jpg
"""
import math
import os
import random
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

import kit as K
from kit import W, H, E, TB

FD = os.path.join(K.REPO, "comum", "fontes")
OUT = K.OUT
FULL = {"critter": (0.0, 7.1), "sushi": (0.0, 6.9), "canvas": (0.4, 7.6), "art": (0.0, 6.7),
        "passaporte": (0.3, 7.5), "unlock": (0.3, 7.4), "sky_dados": (0.5, 18.0), "taketime": (16.0, 26.0)}


@lru_cache(None)
def F(nome, s, peso=None):
    f = ImageFont.truetype(os.path.join(FD, nome), int(s))
    if peso:
        try:
            f.set_variation_by_axes(list(peso))
        except Exception:  # noqa: BLE001
            pass
    return f


def clip(nome, u):
    t0, L = FULL[nome]
    return K.quadro_clip(nome, t0, L, 1.0, u).convert("RGB")


def cobre(im, w, h):
    s = max(w / im.width, h / im.height)
    im2 = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    x, y = (im2.width - w) // 2, (im2.height - h) // 2
    return im2.crop((x, y, x + w, y + h))


def sombra(im, r=14, off=(10, 14), a=120):
    sh = Image.new("RGBA", (im.width + 4 * r, im.height + 4 * r), (0, 0, 0, 0))
    m = im.getchannel("A").point(lambda v: v * a // 255)
    sh.paste((0, 0, 0, 255), (2 * r + off[0], 2 * r + off[1]), m)
    sh = sh.filter(ImageFilter.GaussianBlur(r))
    sh.alpha_composite(im, (2 * r, 2 * r))
    return sh


def cola(img, im, cx, cy, rot=0):
    if rot:
        im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def ruido(w, h, escala, seed, amp=1.0):
    rng = np.random.default_rng(seed)
    a = rng.random((h // escala + 2, w // escala + 2))
    im = Image.fromarray((a * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    return np.asarray(im, dtype=np.float32) / 255 * amp


# ======================================================================= A COLAGEM
AZUL, PAPEL, VERM, ROXO_A, PRETO = (34, 78, 168), (238, 234, 226), (214, 66, 48), (140, 108, 240), (24, 22, 22)


@lru_cache(None)
def papel_amassado():
    base = np.array(PAPEL, np.float32)[None, None, :] * np.ones((H, W, 1), np.float32)
    n = ruido(W, H, 90, 1) * 0.6 + ruido(W, H, 30, 2) * 0.3 + ruido(W, H, 6, 3) * 0.1
    sh = (n - 0.5) * 30
    a = np.clip(base + sh[..., None], 0, 255).astype(np.uint8)
    return Image.fromarray(a).convert("RGBA").filter(ImageFilter.GaussianBlur(0.6))


@lru_cache(None)
def azul_textura():
    base = np.array(AZUL, np.float32)[None, None, :] * np.ones((H, W, 1), np.float32)
    n = (ruido(W, H, 4, 7) - 0.5) * 40 + (ruido(W, H, 60, 8) - 0.5) * 30
    return Image.fromarray(np.clip(base + n[..., None], 0, 255).astype(np.uint8)).convert("RGBA")


def borda_rasgada(pts_base, seed, amp=18):
    rnd = random.Random(seed)
    out = []
    for i in range(len(pts_base) - 1):
        (x0, y0), (x1, y1) = pts_base[i], pts_base[i + 1]
        n = max(2, int(math.dist((x0, y0), (x1, y1)) / 9))
        for k in range(n):
            t = k / n
            out.append((x0 + (x1 - x0) * t + rnd.uniform(-amp, amp) * 0.4, y0 + (y1 - y0) * t + rnd.uniform(-amp, amp)))
    return out


def fundo_colagem():
    img = azul_textura().copy()
    # faixa de papel rasgado no meio (diagonal), com borda branca de fibra
    topo = borda_rasgada([(-20, 330), (W + 20, 120)], 3, 26)
    baixo = borda_rasgada([(W + 20, 1500), (-20, 1760)], 5, 26)
    poly = topo + baixo
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon(poly, fill=255)
    fibra = m.filter(ImageFilter.MaxFilter(11))
    img.paste((250, 250, 248, 255), (0, 0), fibra)
    img.paste(papel_amassado(), (0, 0), m)
    return img


@lru_cache(None)
def letra_recortada(ch, i, s=170):
    fontes = ["Anton-Regular.ttf", "AbrilFatface-Regular.ttf", "ArchivoBlack-Regular.ttf", "DMSerifDisplay-Regular.ttf",
              "RubikMonoOne-Regular.ttf", "Shrikhand-Regular.ttf", "BebasNeue-Regular.ttf"]
    papeis = [((232, 226, 214), PRETO), (VERM, PRETO), ((40, 38, 36), (238, 232, 220)), ((210, 196, 170), PRETO),
              (ROXO_A, (30, 20, 60)), ((248, 246, 240), VERM), ((196, 210, 200), PRETO)]
    rnd = random.Random(i * 7 + ord(ch))
    f = F(fontes[rnd.randrange(len(fontes))], s * rnd.uniform(0.85, 1.12))
    fundo, cor = papeis[rnd.randrange(len(papeis))]
    bb = f.getbbox(ch)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    px, py = rnd.randint(14, 30), rnd.randint(14, 30)
    im = Image.new("RGBA", (w + 2 * px, h + 2 * py), fundo + (255,))
    # textura de papel de revista
    n = (ruido(im.width, im.height, 3, i + 50) - 0.5) * 24
    a = np.clip(np.asarray(im, np.float32)[..., :3] + n[..., None], 0, 255).astype(np.uint8)
    im = Image.fromarray(a).convert("RGBA")
    ImageDraw.Draw(im).text((px - bb[0], py - bb[1]), ch, font=f, fill=cor)
    # recorte de tesoura: cantos levemente irregulares
    m = Image.new("L", im.size, 0)
    j = lambda: rnd.randint(0, 7)  # noqa: E731
    ImageDraw.Draw(m).polygon([(j(), j()), (im.width - j(), j()), (im.width - j(), im.height - j()),
                               (j(), im.height - j())], fill=255)
    im.putalpha(m)
    return sombra(im, 6, (5, 7), 140).rotate(rnd.uniform(-9, 9), expand=True, resample=Image.BICUBIC)


def titulo_recortado(img, txt, cx, cy, s=170, larg=980):
    linhas = txt.split("\n")
    y = cy - (len(linhas) - 1) * s * 0.62
    for li, linha in enumerate(linhas):
        peças = [letra_recortada(ch, li * 40 + k, s) if ch != " " else None for k, ch in enumerate(linha)]
        tot = sum((p.width - 28 if p else s * 0.35) for p in peças)
        esc = min(1.0, larg / tot)
        x = cx - tot * esc / 2
        for p in peças:
            if p is None:
                x += s * 0.35 * esc
                continue
            q = p.resize((int(p.width * esc), int(p.height * esc)), Image.LANCZOS) if esc < 1 else p
            img.alpha_composite(q, (int(x - 14 * esc), int(y - q.height / 2)))
            x += (p.width - 28) * esc
        y += s * 1.24


def placa(txt, w=560, h=420):
    im = Image.new("RGBA", (w, h), (205, 190, 160, 255))
    n = (ruido(w, h, 5, 21) - 0.5) * 30 + (ruido(w, h, 50, 22) - 0.5) * 30
    a = np.clip(np.asarray(im, np.float32)[..., :3] + n[..., None], 0, 255).astype(np.uint8)
    im = Image.fromarray(a).convert("RGBA")
    d = ImageDraw.Draw(im)
    linhas = txt.split("\n")
    f = F("PermanentMarker-Regular.ttf", 58)
    for k, l in enumerate(linhas):
        d.text((w / 2, h / 2 + (k - (len(linhas) - 1) / 2) * 70), l, font=f, fill=(30, 26, 24), anchor="mm")
    return sombra(im, 10, (8, 10), 130)


def estrela(r1, r2, n, cor):
    im = Image.new("RGBA", (2 * r1 + 10, 2 * r1 + 10), (0, 0, 0, 0))
    pts = []
    rnd = random.Random(4)
    for k in range(2 * n):
        r = (r1 if k % 2 == 0 else r2) * rnd.uniform(0.85, 1.1)
        a = math.pi * k / n
        pts.append((r1 + 5 + r * math.cos(a), r1 + 5 + r * math.sin(a)))
    ImageDraw.Draw(im).polygon(pts, fill=cor)
    return im


def maquina(img, x, y, linhas, s=46, cor=PRETO):
    d = ImageDraw.Draw(img)
    for k, l in enumerate(linhas):
        d.text((x, y + k * s * 1.35), l, font=F("SpecialElite-Regular.ttf", s), fill=cor)


def janela_rasgada(img, frame, cx, cy, w, h, seed=9, rot=-3):
    """Cena de jogo dentro de um rasgo de papel."""
    pts = borda_rasgada([(0, 0), (w, 0), (w, h), (0, h), (0, 0)], seed, 10)
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    fr = cobre(frame, w, h).convert("RGBA")
    fr.putalpha(m)
    borda = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    mb = Image.new("L", (w + 40, h + 40), 0)
    mb.paste(m.filter(ImageFilter.MaxFilter(15)), (20, 20))
    borda.paste((250, 249, 245, 255), (0, 0), mb)
    borda.alpha_composite(fr, (20, 20))
    cola(img, sombra(borda, 12, (8, 12), 120), cx, cy, rot)


def colagem_1():
    img = fundo_colagem()
    titulo_recortado(img, "TARDE\nDE JOGOS!", W / 2, 680, 235)
    cola(img, estrela(250, 150, 14, VERM + (255,)), 780, 1310, 8)
    cola(img, placa("VEM JOGAR\nCOM A GENTE\nNO BECAS!", 520, 330), 760, 1300, 6)
    maquina(img, 70, 1080, ["# sábado à tarde", "# Becas Café", "# R$ 30", "#  (R$ 15 em café)", "# data em breve"], 50)
    img.alpha_composite(K.logo(150), (W - 180, 40))
    return img


def colagem_2():
    img = fundo_colagem()
    janela_rasgada(img, clip("critter", 1.2), W / 2, 900, 860, 900, 11, -2)
    lab = letra_recortada  # reaproveita estilo de recorte para a etiqueta
    titulo_recortado(img, "CRITTER KITCHEN", W / 2, 1450, 100, 940)
    cola(img, placa("dá pra rir\njogando?", 440, 230), 330, 360, -7)
    img.alpha_composite(K.logo(150), (W - 180, 40))
    return img


# ======================================================================= B TABULEIRO ROXO + LIMA
ROXO, LIMA, CREME_B, PRETO_B = (88, 58, 232), (196, 244, 70), (238, 233, 218), (22, 20, 26)


@lru_cache(None)
def fundo_roxo():
    base = np.array(ROXO, np.float32)[None, None, :] * np.ones((H, W, 1), np.float32)
    n = (ruido(W, H, 2, 31) - 0.5) * 34
    return Image.fromarray(np.clip(base + n[..., None], 0, 255).astype(np.uint8)).convert("RGBA")


def tabuleiro(img, x0, y0, x1, y1, casa=78, acesa=None):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x0 + 14, y0 + 16, x1 + 14, y1 + 16), 54, fill=PRETO_B)
    d.rounded_rectangle((x0, y0, x1, y1), 54, fill=CREME_B, outline=PRETO_B, width=10)
    # trilha de casas na borda
    xi, yi, xf, yf = x0 + casa, y0 + casa, x1 - casa, y1 - casa
    d.rounded_rectangle((xi, yi, xf, yf), 26, outline=PRETO_B, width=8)
    nx, ny = int((xf - xi) / casa), int((yf - yi) / casa)
    casas = []
    for k in range(nx + 1):
        x = xi + (xf - xi) * k / nx
        d.line((x, y0 + 10, x, yi), fill=PRETO_B, width=5)
        d.line((x, yf, x, y1 - 10), fill=PRETO_B, width=5)
    for k in range(ny + 1):
        y = yi + (yf - yi) * k / ny
        d.line((x0 + 10, y, xi, y), fill=PRETO_B, width=5)
        d.line((xf, y, x1 - 10, y), fill=PRETO_B, width=5)
    if acesa is not None:
        x = xi + (xf - xi) * (acesa % nx) / nx
        d.rectangle((x + 5, y0 + 14, x + (xf - xi) / nx - 4, yi - 4), fill=LIMA)
    return (xi + 8, yi + 8, xf - 8, yf - 8)


def mancha(w, h, cor, seed=2):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rnd = random.Random(seed)
    for _ in range(9):
        r = rnd.uniform(0.25, 0.4) * h
        cx, cy = rnd.uniform(r, w - r), rnd.uniform(h * 0.4, h * 0.6)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=cor)
    return im


def carta_caixa(nome, w=300):
    """Caixa do acervo num cartão creme com borda lima (como as cartas da referência)."""
    cx = Image.open(os.path.join(K.REPO, "hobby-reels", "assets", "acervo", nome + ".png")).convert("RGBA")
    cx = cx.crop(cx.getbbox())
    h = int(w * 1.3)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 30, fill=LIMA)
    d.rounded_rectangle((16, 16, w - 17, h - 17), 22, fill=CREME_B)
    s = min((w - 60) / cx.width, (h - 60) / cx.height)
    cx = cx.resize((int(cx.width * s), int(cx.height * s)), Image.LANCZOS)
    im.alpha_composite(cx, ((w - cx.width) // 2, (h - cx.height) // 2))
    return sombra(im, 10, (6, 10), 110)


def dado_b(s=130, pontos=5):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((4, 4, s - 5, s - 5), 22, fill=(248, 246, 240), outline=PRETO_B, width=6)
    pos = {5: [(.27, .27), (.73, .27), (.5, .5), (.27, .73), (.73, .73)], 4: [(.27, .27), (.73, .27), (.27, .73),
                                                                              (.73, .73)]}[pontos]
    for px, py in pos:
        r = s * 0.075
        d.ellipse((px * s - r, py * s - r, px * s + r, py * s + r), fill=PRETO_B)
    return sombra(im, 8, (5, 8), 120)


def tab_1():
    img = fundo_roxo().copy()
    for nome, x, y, r in (("hitster", 150, 260, -18), ("dixit", 960, 330, 14), ("telma", 140, 1690, 12),
                          ("uga_buga", 950, 1640, -12)):
        cola(img, carta_caixa(nome, 270), x, y, r)
    tabuleiro(img, 90, 470, W - 90, 1450, 82, acesa=None)
    d = ImageDraw.Draw(img)
    f1 = F("Unbounded.ttf", 158, (900,))
    d.text((W / 2, 760), "tarde", font=f1, fill=PRETO_B, anchor="mm")
    m = mancha(260, 170, LIMA)
    cola(img, m, W / 2, 905)
    d.text((W / 2, 902), "de", font=F("Unbounded.ttf", 108, (900,)), fill=PRETO_B, anchor="mm")
    d.text((W / 2, 1050), "jogos", font=f1, fill=PRETO_B, anchor="mm")
    d.rounded_rectangle((W / 2 - 230, 600 - 34, W / 2 + 230, 600 + 34), 34, outline=PRETO_B, width=4)
    d.text((W / 2, 600), "@suavez_bg × becas café", font=F("SpaceGrotesk.ttf", 34, (700,)), fill=PRETO_B, anchor="mm")
    d.text((W / 2, 1200), "DATA EM BREVE · R$ 30", font=F("DelaGothicOne-Regular.ttf", 46), fill=PRETO_B, anchor="mm")
    d.text((W / 2, 1270), "a gente ensina todos os jogos!", font=F("SpaceGrotesk.ttf", 36, (600,)),
           fill=PRETO_B, anchor="mm")
    cola(img, dado_b(130, 5), 860, 560, 12)
    cola(img, dado_b(120, 4), 230, 1350, -10)
    return img


def tab_2():
    img = fundo_roxo().copy()
    area = tabuleiro(img, 70, 300, W - 70, 1560, 82, acesa=4)
    fr = cobre(clip("sushi", 1.0), int(area[2] - area[0]), int(area[3] - area[1])).convert("RGBA")
    m = Image.new("L", fr.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, fr.width - 1, fr.height - 1), 20, fill=255)
    img.paste(fr, (int(area[0]), int(area[1])), m)
    d = ImageDraw.Draw(img)
    # etiqueta lima "carta" com o nome do jogo
    et = Image.new("RGBA", (560, 200), (0, 0, 0, 0))
    de = ImageDraw.Draw(et)
    de.rounded_rectangle((0, 0, 559, 199), 26, fill=LIMA, outline=PRETO_B, width=6)
    de.text((40, 60), "sushi go!", font=F("Unbounded.ttf", 66, (900,)), fill=PRETO_B, anchor="lm")
    de.text((40, 140), "2 a 5 jogadores · 15 min", font=F("SpaceGrotesk.ttf", 34, (700,)), fill=PRETO_B, anchor="lm")
    cola(img, sombra(et, 8, (6, 10), 130), 380, 1430, -4)
    d.text((W / 2, 200), "casa 4: pegue uma carta", font=F("DelaGothicOne-Regular.ttf", 48), fill=LIMA, anchor="mm")
    img.alpha_composite(K.logo(150), (W - 180, 40))
    return img


# ======================================================================= C TVs RETRÔ
FOSF, AMBAR = (70, 255, 140), (255, 176, 0)


@lru_cache(None)
def noite():
    img = Image.new("RGBA", (W, H), (10, 14, 22, 255))
    d = ImageDraw.Draw(img)
    for y in range(H):  # degradê
        c = int(10 + 18 * (y / H))
        d.line((0, y, W, y), fill=(c, c + 4, c + 12))
    bok = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    db = ImageDraw.Draw(bok)
    rnd = random.Random(5)
    for _ in range(46):  # luzes da cidade desfocadas
        x, y, r = rnd.uniform(0, W), rnd.uniform(120, 900), rnd.uniform(10, 34)
        c = rnd.choice([(255, 190, 110), (255, 230, 170), (120, 170, 255), (255, 120, 90)])
        db.ellipse((x - r, y - r, x + r, y + r), fill=c + (int(rnd.uniform(60, 150)),))
    img.alpha_composite(bok.filter(ImageFilter.GaussianBlur(6)))
    return img


def madeira(w, h, seed):
    y = np.arange(h)[:, None]
    x = np.arange(w)[None, :]
    n = ruido(w, h, 40, seed)
    veio = np.sin((x * 0.02 + n * 9) * 3.0) * 0.5 + 0.5
    base = np.array([96, 62, 36], np.float32)
    claro = np.array([140, 96, 58], np.float32)
    a = base + (claro - base) * veio[..., None] * 0.8 + (ruido(w, h, 3, seed + 1)[..., None] - 0.5) * 14
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


def tela_crt(conteudo, w, h):
    """Aplica cara de tubo: linhas, brilho nas bordas escuras, reflexo."""
    im = cobre(conteudo, w, h).convert("RGB")
    im = Image.blend(im, Image.new("RGB", (w, h), (20, 40, 30)), 0.08)
    a = np.asarray(im, np.float32)
    a[::4] *= 0.78  # linhas de varredura
    yy, xx = np.mgrid[0:h, 0:w]
    v = 1 - 0.55 * (((xx - w / 2) / (w / 2)) ** 4 + ((yy - h / 2) / (h / 2)) ** 4)
    a *= np.clip(v, 0.25, 1)[..., None]
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), int(min(w, h) * 0.12), fill=255)
    im.putalpha(m)
    ref = Image.new("RGBA", (w, h), (0, 0, 0, 0))  # reflexo do vidro
    ImageDraw.Draw(ref).ellipse((-w * 0.2, -h * 0.5, w * 0.7, h * 0.35), fill=(255, 255, 255, 34))
    im.alpha_composite(ref.filter(ImageFilter.GaussianBlur(20)))
    return im


def tv(conteudo, w, h, seed, lado_botoes=True):
    """TV de madeira: gabinete, moldura escura, tela de tubo, painel de botões."""
    pw = int(w * 0.2) if lado_botoes else 0
    im = madeira(w, h, seed)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w - 1, h - 1), outline=(40, 26, 16), width=6)
    sx0, sy0, sx1, sy1 = 34, 34, w - pw - 34, h - 34
    d.rounded_rectangle((sx0 - 14, sy0 - 14, sx1 + 14, sy1 + 14), 40, fill=(28, 26, 24))
    tela = tela_crt(conteudo, sx1 - sx0, sy1 - sy0)
    glow = Image.new("RGBA", im.size, (0, 0, 0, 0))
    im.alpha_composite(tela, (sx0, sy0))
    if lado_botoes:
        px = w - pw
        d.rectangle((px - 6, 22, w - 22, h - 22), fill=(52, 40, 30))
        for k in range(2):  # botões giratórios
            cy = 90 + k * 120
            cx = px + pw / 2 - 10
            d.ellipse((cx - 40, cy - 40, cx + 40, cy + 40), fill=(30, 28, 26))
            d.ellipse((cx - 30, cy - 30, cx + 30, cy + 30), fill=(170, 160, 140))
            d.line((cx, cy, cx + 22 * math.cos(k + 1), cy - 22 * math.sin(k + 1)), fill=(40, 30, 20), width=6)
        for k in range(8):  # grade do alto-falante
            y = h * 0.55 + k * 18
            d.line((px + 16, y, w - 36, y), fill=(26, 20, 16), width=6)
    return sombra(im, 18, (10, 16), 170)


@lru_cache(None)
def tela_info():
    im = Image.new("RGB", (900, 680), (6, 22, 12))
    d = ImageDraw.Draw(im)
    f = F("VT323-Regular.ttf", 112)
    d.text((40, 60), "> TARDE DE JOGOS", font=f, fill=FOSF)
    d.text((40, 190), "> BECAS CAFÉ", font=f, fill=FOSF)
    d.text((40, 330), "R$30 (R$15 EM CAFÉ)", font=F("VT323-Regular.ttf", 86), fill=AMBAR)
    d.text((40, 440), "DATA EM BREVE_", font=F("VT323-Regular.ttf", 86), fill=FOSF)
    d.text((40, 560), "RESERVE: (11) 97793-3910", font=F("VT323-Regular.ttf", 70), fill=(180, 255, 210))
    glow = im.filter(ImageFilter.GaussianBlur(6))
    return ImageChops.screen(im, glow)


def tvs_1():
    img = noite().copy()
    d = ImageDraw.Draw(img)
    d.rectangle((0, 1640, W, H), fill=(26, 20, 16))  # chão/mesa
    # pilha: grande embaixo (info), duas em cima (jogos), uma de lado
    cola(img, tv(clip("sky_dados", 4.0), 520, 400, 1), 300, 640, -2)
    cola(img, tv(clip("canvas", 2.0), 470, 380, 2, False), 790, 700, 3)
    cola(img, tv(tela_info(), 968, 760, 3, False), W / 2, 1240, 0)
    # brilho verde das telas no ambiente
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(gl).ellipse((100, 900, 980, 1700), fill=(40, 255, 140, 30))
    img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(80)))
    d = ImageDraw.Draw(img)
    d.text((W / 2, 260), "SÁBADO NO BECAS", font=F("Silkscreen-Bold.ttf", 64), fill=AMBAR, anchor="mm")
    img.alpha_composite(K.logo(150), (W - 180, 40))
    return img


def tvs_2():
    img = noite().copy()
    d = ImageDraw.Draw(img)
    d.rectangle((0, 1700, W, H), fill=(26, 20, 16))
    pos = [("critter", 1.0, 290, 470, 480, 360, -2), ("sushi", 1.5, 780, 520, 440, 340, 2),
           ("art", 1.0, 300, 900, 500, 380, 1), ("unlock", 1.0, 790, 950, 460, 360, -3),
           ("passaporte", 2.0, 300, 1340, 520, 380, -1), ("taketime", 4.0, 790, 1380, 480, 360, 2)]
    for k, (c, u, x, y, w, h, r) in enumerate(pos):
        cola(img, tv(clip(c, u), w, h, 10 + k, k % 2 == 0), x, y, r)
    d.text((W / 2, 180), "6 CANAIS. 1 TARDE.", font=F("PressStart2P-Regular.ttf", 46), fill=FOSF, anchor="mm")
    d.text((W / 2, 1700 + 80), "SINTONIZE: BECAS CAFÉ", font=F("VT323-Regular.ttf", 84), fill=AMBAR, anchor="mm")
    img.alpha_composite(K.logo(150), (W - 180, 40))
    return img


# ======================================================================= amostras de fonte (uso no dia a dia)
def amostras():
    w, h = 1080, 1350
    img = Image.new("RGB", (w * 3, h), (255, 255, 255))
    cfg = [
        ("A  COLAGEM", PAPEL, [("Anton-Regular.ttf", 110, PRETO, "ANTON"), ("AbrilFatface-Regular.ttf", 96, VERM,
                                                                         "Abril Fatface"),
                              ("PermanentMarker-Regular.ttf", 80, AZUL, "Permanent Marker"),
                              ("SpecialElite-Regular.ttf", 64, PRETO, "Special Elite (máquina)")],
         [AZUL, PAPEL, VERM, ROXO_A, PRETO]),
        ("B  TABULEIRO", ROXO, [("Unbounded.ttf", 104, LIMA, "unbounded"), ("DelaGothicOne-Regular.ttf", 84, CREME_B,
                                                                            "Dela Gothic"),
                               ("SpaceGrotesk.ttf", 70, CREME_B, "Space Grotesk"),
                               ("BricolageGrotesque.ttf", 80, LIMA, "Bricolage")],
         [ROXO, LIMA, CREME_B, PRETO_B, (255, 255, 255)]),
        ("C  TVs RETRÔ", (12, 18, 26), [("VT323-Regular.ttf", 130, FOSF, "VT323 FOSFORO"),
                                        ("PressStart2P-Regular.ttf", 56, AMBAR, "PRESS START"),
                                        ("Silkscreen-Bold.ttf", 78, (180, 255, 210), "SILKSCREEN"),
                                        ("RubikMonoOne-Regular.ttf", 66, (255, 120, 90), "RUBIK MONO")],
         [(12, 18, 26), FOSF, AMBAR, (255, 120, 90), (120, 110, 100)]),
    ]
    d = ImageDraw.Draw(img)
    for k, (nome, fundo, fontes, pal) in enumerate(cfg):
        x0 = k * w
        d.rectangle((x0, 0, x0 + w, h), fill=fundo)
        txt = (255, 255, 255) if sum(fundo) < 400 else PRETO
        d.text((x0 + 60, 80), nome, font=E.lilita(70), fill=txt)
        y = 230
        for arq, s, cor, amostra in fontes:
            peso = (900,) if arq.startswith("Unbounded") else ((700,) if arq.startswith(("Space", "Bricolage")) else None)
            d.text((x0 + 60, y), amostra, font=F(arq, s, peso), fill=cor)
            y += s * 1.55 + 30
        for j, c in enumerate(pal):
            d.rounded_rectangle((x0 + 60 + j * 190, h - 220, x0 + 220 + j * 190, h - 80), 24, fill=c,
                                outline=(255, 255, 255) if sum(fundo) < 400 else PRETO, width=4)
    return img


def main():
    K.prepara([(n, t0, d, 1.0) for n, (t0, d) in FULL.items()])
    cols = [("A  COLAGEM", [colagem_1(), colagem_2()]), ("B  TABULEIRO", [tab_1(), tab_2()]),
            ("C  TVs RETRÔ", [tvs_1(), tvs_2()])]
    tw, th = 400, 711
    sh = Image.new("RGB", (3 * (2 * tw + 30) + 30, th + 120), (255, 255, 255))
    d = ImageDraw.Draw(sh)
    for c, (nome, ims) in enumerate(cols):
        x0 = 30 + c * (2 * tw + 30)
        d.text((x0 + tw, 55), nome, font=E.lilita(56), fill=E.MARROM, anchor="mm")
        for k, im in enumerate(ims):
            sh.paste(im.convert("RGB").resize((tw - 10, th), Image.LANCZOS), (x0 + k * tw, 100))
            im.convert("RGB").save(os.path.join(OUT, f"estilo_{'abc'[c]}{k + 1}.jpg"), quality=92)
    sh.save(os.path.join(OUT, "estilos.jpg"), quality=90)
    amostras().save(os.path.join(OUT, "estilos_fontes.jpg"), quality=90)
    print("ok")


if __name__ == "__main__":
    main()
