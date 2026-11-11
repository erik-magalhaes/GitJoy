#!/usr/bin/env python3
"""Dois carrosséis "SE VOCÊ AMA ___, VAI CURTIR ___" (11/nov/2026, depois do de videogame), cada um com conceito próprio:

  animacao  BALDE DE PIPOCA: pôster oficial (TMDB, versão BR) numa moldura de letreiro de cinema com lampadinhas; a caixa
            do jogo SALTA de um balde de pipoca listrado e o rótulo do balde traz nome, ficha e frase.
  filmes    INGRESSO DE CINEMA: fundo de cortina vermelha com holofote; um ingresso creme em pé com o pôster ("ADMITE 1")
            em cima, picote no meio e o canhoto "VAI CURTIR" com a caixa, nome, ficha e frase.

Identidade da Jéssica (Lilita/Figtree, contorno marrom, sombra sólida). Fichas do site (`acervo_site.json`).

    /usr/bin/python3 cinema.py animacao --teste
    /usr/bin/python3 cinema.py filmes            # out/<nome>/NN.png + stories/story_NN.png + previa.jpg
"""
import json
import math
import os
import random
import sys
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
import estilo as E  # noqa: E402

AC = os.path.join(REPO, "hobby-reels", "assets", "acervo")
POS = os.path.join(ROOT, "assets", "filmes")
W, H = 1080, 1350
CREME = (255, 246, 228)
VERMELHO = (214, 48, 49)
SITE = json.load(open(os.path.join(REPO, "comum", "dados", "acervo_site.json")))

# (filme, pôster, jogo, nome no site, caixa, frase)
LISTAS = {
    "animacao": [
        ("Ratatouille", "ratatouille", "Critter Kitchen", "Critter Kitchen", f"{AC}/critter_kitchen.png",
         "Bichinhos na cozinha disputando os melhores ingredientes pra agradar os clientes."),
        ("Alice no País das Maravilhas", "alice", "Wonderland's War", "Wonderland's War", f"{AC}/wonderland_s_war.png",
         "O Chapeleiro, a Rainha Vermelha e o Gato de Cheshire em guerra pelo País das Maravilhas."),
        ("Robin Hood", "robin_hood", "Unmatched: Robin Hood vs. Pé-Grande", "Unmatched: Robin Hood vs. Bigfoot",
         f"{AC}/unmatched_robin_hood_vs_bigfoot.png", "O próprio Robin Hood num duelo contra o Pé-Grande, cada um com seus golpes."),
        ("Procurando Nemo", "nemo", "Sea Salt & Paper", "Sea Salt & Paper", f"{AC}/sea_salt_paper.png",
         "Peixes, caranguejos, polvos e barquinhos de papel: junte as duplas e mergulhe nos pontos."),
        ("Moana", "moana", "Survive the Island", "Survive The Island", f"{AC}/survive_the_island.png",
         "Fuja da ilha que está afundando, num mar cheio de tubarões e monstros marinhos."),
        ("Como Treinar o seu Dragão", "dragao", "Flamecraft", "Flamecraft", f"{AC}/flamecraft.png",
         "Dragõezinhos fofos trabalhando nas lojinhas da cidade, cada um com o seu talento."),
        ("Hotel Transilvânia", "hotel", "Drácula vs Van Helsing", "Dracula vs Van Helsing", f"{AC}/dracula_vs_van_helsing.png",
         "O Drácula de verdade num duelo de 2: ele quer dominar a cidade, o Van Helsing quer acabar com ele."),
    ],
    "filmes": [
        ("Indiana Jones", "indiana", "Tikal", "Tikal", f"{AC}/tikal.png",
         "Explore a selva, descubra templos perdidos e cave os tesouros antes dos outros."),
        ("Piratas do Caribe", "piratas", "Treasure Island", "Treasure Island", f"{AC}/treasure_island.png",
         "Um pirata esconde o tesouro e os outros caçam no mapa... seguindo pistas que podem ser mentira."),
        ("Missão Impossível", "missao", "Spyfall", "Spyfall", f"{AC}/spyfall.png",
         "Todo mundo sabe o local da missão, menos o espião. Descubra quem é antes que ele descubra onde está."),
        ("Pânico", "panico", "Final Girl", "Final Girl", f"{REPO}/finalgirl-reels/assets/recortes/caixa_base.png",
         "Você é a sobrevivente: salve as vítimas, ache uma arma e enfrente o assassino."),
        ("Harry Potter", "harry", "Wandering Towers", "Wandering Towers", f"{AC}/wandering_towers.png",
         "Magos, torres que andam pelo tabuleiro e poções pra encher antes que o jogo acabe."),
        ("Os Vingadores", "vingadores", "Marvel United", "Marvel United", f"{REPO}/gravados-reels/assets/lista/marvel_united.png",
         "Junte os heróis da Marvel e derrote o vilão em equipe: é cooperativo!"),
    ],
}


def ficha(nome):
    d = SITE[nome]
    a, _, b = d["jogadores"].partition("–")
    jog = f"{a} jogador" + ("" if a == "1" and a == b else "es") if a == b else f"{a} a {b} jogadores"
    dias = 7 if d["preco"] == 60 else 5
    return f"{jog} · {d['tempo'].replace('min', ' min')} · R$ {d['preco']} / {dias} dias"


@lru_cache(None)
def poster(nome, h, raio=16):
    im = Image.open(os.path.join(POS, nome + ".jpg")).convert("RGB")
    w = int(h * 2 / 3)
    r = im.width / im.height
    if r > 2 / 3:
        nw = int(im.height * 2 / 3)
        im = im.crop(((im.width - nw) // 2, 0, (im.width - nw) // 2 + nw, im.height))
    else:
        nh = int(im.width * 3 / 2)
        im = im.crop((0, 0, im.width, nh))
    im = im.resize((w, h), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=raio, fill=255)
    im.putalpha(m)
    return im


def cola_centro(img, im, cx, y):
    img.alpha_composite(im, (int(cx - im.width / 2), int(y)))


def logo_topo(img, y=30, w=170):
    lg = E.logo(w)
    img.alpha_composite(lg, ((W - lg.width) // 2, y))
    return y + lg.height


# ----------------------------------------------------------------------------------------- ANIMAÇÃO: balde de pipoca
@lru_cache(None)
def _fundo_pipoca(hh, semente):
    img = Image.new("RGBA", (W, hh), (255, 214, 102, 255))
    d = ImageDraw.Draw(img)
    for x in range(-hh, W + hh, 120):  # raios diagonais suaves
        d.polygon([(x, 0), (x + 60, 0), (x + 60 + hh // 3, hh), (x + hh // 3, hh)], fill=(255, 205, 84))
    rnd = random.Random(semente)
    for _ in range(26):  # pipocas soltas nas bordas
        x = rnd.choice([rnd.randint(10, 110), rnd.randint(W - 110, W - 10)])
        y = rnd.randint(140, hh - 40)
        pipoca(d, x, y, rnd.randint(16, 26), rnd)
    return img


def pipoca(d, x, y, r, rnd):
    """Pipoca desenhada: 4–5 bolinhas creme com contorno marrom fino."""
    pts = [(x + rnd.randint(-r // 2, r // 2), y + rnd.randint(-r // 2, r // 2)) for _ in range(4)]
    for px, py in pts:
        rr = r * rnd.uniform(0.55, 0.8)
        d.ellipse((px - rr - 3, py - rr - 3, px + rr + 3, py + rr + 3), fill=E.MARROM)
    for px, py in pts:
        rr = r * rnd.uniform(0.55, 0.8)
        d.ellipse((px - rr, py - rr, px + rr, py + rr), fill=(255, 250, 236))
    d.ellipse((x - r * 0.25, y - r * 0.25, x + r * 0.15, y + r * 0.15), fill=(252, 218, 120))


def marquise(post_h, titulo=None):
    """Moldura de letreiro de cinema com lampadinhas em volta do pôster."""
    pw = int(post_h * 2 / 3)
    m = 34
    w, h = pw + 2 * m, post_h + 2 * m
    im = E.bloco(w, h, VERMELHO, raio=26, ow=7, sombra=12)
    d = ImageDraw.Draw(im)
    passo = 38
    for x in range(m // 2 + 6, w - 6, passo):
        for y in (m // 2, h - m // 2):
            d.ellipse((x - 8, y - 8, x + 8, y + 8), fill=E.MARROM)
            d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=(255, 238, 150))
    for y in range(m // 2 + passo, h - m // 2 - 10, passo):
        for x in (m // 2, w - m // 2):
            d.ellipse((x - 8, y - 8, x + 8, y + 8), fill=E.MARROM)
            d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=(255, 238, 150))
    return im, (m, m)


def balde(w_top, h):
    """Balde de pipoca listrado (vermelho × branco), trapézio com contorno marrom e sombra sólida."""
    w_bot = int(w_top * 0.8)
    s = 12
    im = Image.new("RGBA", (w_top + s + 4, h + s + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    poly = lambda dx, dy: [(dx, dy), (w_top + dx, dy), (w_top - (w_top - w_bot) // 2 + dx, h + dy), ((w_top - w_bot) // 2 + dx, h + dy)]
    d.polygon(poly(s, s), fill=E.MARROM)
    listras = Image.new("RGBA", (w_top, h), (0, 0, 0, 0))
    dl = ImageDraw.Draw(listras)
    n = 9
    for k in range(n):
        x0t, x1t = w_top * k / n, w_top * (k + 1) / n
        x0b = (w_top - w_bot) / 2 + w_bot * k / n
        x1b = (w_top - w_bot) / 2 + w_bot * (k + 1) / n
        dl.polygon([(x0t, 0), (x1t, 0), (x1b, h), (x0b, h)], fill=VERMELHO if k % 2 == 0 else (255, 250, 240))
    mask = Image.new("L", (w_top, h), 0)
    ImageDraw.Draw(mask).polygon(poly(0, 0), fill=255)
    im.paste(listras, (0, 0), mask)
    d.polygon(poly(0, 0), outline=E.MARROM, width=7)
    return im


def tela_animacao(k, pares):
    filme, pst, nome, site, caixa, frase = pares[k]
    img = _fundo_pipoca(H, k + 2).copy()
    logo_topo(img, 26, 160)
    pl = E.pilula(f"SESSÃO {k + 1}/{len(pares)}", 26, E.PETROLEO, (255, 255, 255), fonte_titulo=True)
    img.alpha_composite(pl, (W - pl.width - 40, 46))
    # letreiro com o pôster à esquerda, "se você ama" à direita
    ph = 420
    mq, (mx, my) = marquise(ph)
    x0, y0 = 70, 170
    img.alpha_composite(mq, (x0, y0))
    img.alpha_composite(poster(pst, ph), (x0 + mx, y0 + my))
    cx = x0 + mq.width + (W - x0 - mq.width) // 2 - 6
    sv = E.texto("SE VOCÊ AMA", 38, cor=E.MARROM, peso=900)
    t = E.titulo(filme.upper().replace(" O SEU ", " O SEU\n").replace(" NO PAÍS", "\nNO PAÍS"), 56, cor=(255, 255, 255),
                 larg_max=W - x0 - mq.width - 70)
    vc = E.pilula("VAI CURTIR...", 34, E.LARANJA, (255, 255, 255), fonte_titulo=True)
    bh = sv.height + t.height + vc.height + 30
    yb = y0 + (mq.height - bh) // 2
    cola_centro(img, sv, cx, yb)
    cola_centro(img, t, cx, yb + sv.height)
    cola_centro(img, vc, cx, yb + sv.height + t.height + 24)
    # balde de pipoca com a caixa saltando
    bw, bh2 = 760, 520
    by = 960
    cx_img = E.jogo(caixa, 300, larg=400)
    d = ImageDraw.Draw(img)
    rnd = random.Random(k)
    for _ in range(16):  # pipocas transbordando atrás da caixa
        pipoca(d, W // 2 + rnd.randint(-bw // 2 + 40, bw // 2 - 40), by + rnd.randint(-40, 14), rnd.randint(20, 30), rnd)
    cola_centro(img, cx_img, W // 2, by - cx_img.height + 60)
    for _ in range(8):  # pipocas na frente da caixa, na boca do balde
        pipoca(d, W // 2 + rnd.randint(-bw // 2 + 30, bw // 2 - 30), by + rnd.randint(-6, 22), rnd.randint(18, 26), rnd)
    bd = balde(bw, bh2)
    img.alpha_composite(bd, ((W - bw) // 2, by + 24))
    # rótulo do balde
    lw, lh = 640, 290
    rot = E.bloco(lw, lh, CREME, raio=30, ow=6, sombra=8)
    img.alpha_composite(rot, ((W - lw) // 2, by + 60))
    y = by + 74
    tn = E.titulo(nome, 52, cor=E.LARANJA, larg_max=lw - 40)
    cola_centro(img, tn, W // 2, y)
    y += tn.height
    fi = E.texto(ficha(site), 24, cor=E.PETROLEO, peso=800, larg_max=lw - 40)
    cola_centro(img, fi, W // 2, y)
    y += fi.height + 2
    fr = E.texto(frase, 26, cor=E.MARROM, peso=600, larg_max=lw - 50, entre=1.25)
    cola_centro(img, fr, W // 2, y)
    return img


def capa_animacao(pares):
    img = _fundo_pipoca(H, 1).copy()
    logo_topo(img, 26, 180)
    t = E.titulo("SE VOCÊ AMA\nANIMAÇÃO...", 104, cor=(255, 255, 255), larg_max=980)
    cola_centro(img, t, W // 2, 200)
    # fileira de 4 pôsteres em letreiros pequenos
    ims = [poster(p[1], 250) for p in pares[:4]]
    x = (W - (4 * 167 + 3 * 22)) // 2
    for im in ims:
        im2 = E.bloco(im.width + 16, im.height + 16, E.MARROM, raio=16, ow=0, sombra=8)
        im2.alpha_composite(im, (8, 8))
        img.alpha_composite(im2, (x - 8, 200 + t.height + 10))
        x += 167 + 22
    t2 = E.titulo("...VAI CURTIR ESSES\nJOGOS DE TABULEIRO!", 74, cor=E.LARANJA, larg_max=980)
    cola_centro(img, t2, W // 2, 200 + t.height + 300)
    by = 1150
    bw = 640
    lq = E.leque([p[4] for p in pares[:5]], 170)
    if lq.width > W - 120:
        lq = lq.resize((W - 120, int(lq.height * (W - 120) / lq.width)), Image.LANCZOS)
    d = ImageDraw.Draw(img)
    rnd = random.Random(9)
    for _ in range(14):
        pipoca(d, W // 2 + rnd.randint(-bw // 2 + 30, bw // 2 - 30), by + rnd.randint(-30, 10), rnd.randint(20, 28), rnd)
    cola_centro(img, lq, W // 2, by - lq.height + 60)
    img.alpha_composite(balde(bw, 300), ((W - bw) // 2, by + 20))
    return img


# ----------------------------------------------------------------------------------------- FILMES: ingresso de cinema
@lru_cache(None)
def _fundo_cortina(hh):
    img = Image.new("RGBA", (W, hh), (120, 18, 26, 255))
    a = Image.new("RGB", (W, hh))
    px = []
    for x in range(W):  # pregas da cortina: seno de duas frequências
        v = 0.55 + 0.25 * math.sin(x / 34.0) + 0.12 * math.sin(x / 11.0 + 1.3)
        px.append(v)
    col = Image.new("RGB", (W, 1))
    col.putdata([(int(150 * v + 30), int(22 * v + 6), int(30 * v + 8)) for v in px])
    a = col.resize((W, hh))
    img = a.convert("RGBA")
    luz = Image.new("L", (W, hh), 0)  # holofote no meio
    ImageDraw.Draw(luz).ellipse((W * 0.08, hh * 0.08, W * 0.92, hh * 0.92), fill=150)
    luz = luz.filter(ImageFilter.GaussianBlur(160))
    img = Image.composite(Image.new("RGBA", (W, hh), (255, 214, 150, 255)), img, luz.point(lambda v: int(v * 0.45)))
    d = ImageDraw.Draw(img)
    for x in range(0, W, 2):  # franja dourada no alto
        pass
    d.rectangle((0, 0, W, 18), fill=(212, 160, 60))
    return img


def ingresso(k, pares, story=False):
    filme, pst, nome, site, caixa, frase = pares[k]
    tw = 900
    ph = 470
    th = 1040
    s = 14
    im = Image.new("RGBA", (tw + s + 2, th + s + 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    corte = 610  # altura do picote
    r = 34

    def forma(dx, dy, cor, contorno=None, w=0):
        d.rounded_rectangle((dx, dy, dx + tw, dy + th), radius=30, fill=cor, outline=contorno, width=w)

    forma(s, s, E.MARROM)
    forma(0, 0, CREME, E.MARROM, 7)
    # recortes semicirculares no picote (mostram o fundo: transparentes)
    for cx in (0, tw):
        d.ellipse((cx - r, corte - r, cx + r, corte + r), fill=(0, 0, 0, 0), outline=E.MARROM, width=7)
        d.rectangle((cx - r - 8 if cx == 0 else cx + 1, corte - r - 8, cx - 1 if cx == 0 else cx + r + 8, corte + r + 8),
                    fill=(0, 0, 0, 0))
    for x in range(r + 18, tw - r - 10, 30):  # picote
        d.line((x, corte, x + 14, corte), fill=E.MARROM, width=5)
    # faixa do alto
    d.rounded_rectangle((26, 26, tw - 26, 96), radius=20, fill=VERMELHO)
    f = E.lilita(42)
    d.text((tw // 2, 61), f"INGRESSO · SESSÃO {k + 1}/{len(pares)} · ADMITE 1", font=f, fill=(255, 255, 255), anchor="mm")
    # pôster à esquerda, texto à direita
    p = poster(pst, ph)
    im.alpha_composite(E.bloco(p.width + 10, p.height + 10, E.MARROM, raio=18, ow=0, sombra=0), (40, 118))
    im.alpha_composite(p, (45, 123))
    cx = 45 + p.width + (tw - 45 - p.width) // 2
    sv = E.texto("SE VOCÊ AMA", 36, cor=E.PETROLEO, peso=900)
    t = E.titulo(filme.upper(), 58, cor=VERMELHO, larg_max=tw - p.width - 110)
    bh = sv.height + t.height
    yb = 118 + (ph - bh) // 2
    im.alpha_composite(sv, (int(cx - sv.width / 2), yb))
    im.alpha_composite(t, (int(cx - t.width / 2), yb + sv.height))
    # canhoto: vai curtir
    vc = E.pilula("VAI CURTIR", 32, E.LARANJA, (255, 255, 255), fonte_titulo=True)
    im.alpha_composite(vc, ((tw - vc.width) // 2, corte - vc.height // 2))
    cxj = E.jogo(caixa, 250, larg=330)
    yc = corte + vc.height // 2 + 14
    im.alpha_composite(cxj, (60, yc + 10))
    xr = 60 + cxj.width + 30
    larg = tw - xr - 40
    tn = E.titulo(nome, 56, cor=E.LARANJA, larg_max=larg)
    fi = E.texto(ficha(site), 25, cor=E.PETROLEO, peso=800, larg_max=larg, alinha="lm")
    fr = E.texto(frase, 27, cor=E.MARROM, peso=600, larg_max=larg, entre=1.25, alinha="lm")
    y = yc
    im.alpha_composite(tn, (xr - 14, y))
    y += tn.height
    im.alpha_composite(fi, (xr, y))
    y += fi.height + 4
    im.alpha_composite(fr, (xr, y))
    # código de barras no pé
    rnd = random.Random(k)
    x = 60
    while x < tw - 60:
        w = rnd.choice([3, 3, 5, 8])
        d.rectangle((x, th - 70, x + w, th - 30), fill=E.MARROM)
        x += w + rnd.choice([4, 5, 7])
    return im


def tela_filmes(k, pares):
    img = _fundo_cortina(H).copy()
    logo_topo(img, 28, 150)
    ing = ingresso(k, pares)
    ing = ing.rotate(-1.5, expand=True, resample=Image.BICUBIC)
    cola_centro(img, ing, W // 2 + 4, 150)
    return img


def capa_filmes(pares):
    img = _fundo_cortina(H).copy()
    logo_topo(img, 28, 180)
    t = E.titulo("SE VOCÊ AMA\nCINEMA...", 110, cor=(255, 214, 102), larg_max=980)
    cola_centro(img, t, W // 2, 190)
    ims = [poster(p[1], 270) for p in pares[:3]]
    x0 = (W - (3 * 180 + 2 * 40)) // 2
    for i, im in enumerate(ims):
        im2 = E.bloco(im.width + 16, im.height + 16, CREME, raio=16, ow=5, sombra=10)
        im2.alpha_composite(im, (8, 8))
        im2 = im2.rotate([4, -2, -5][i], expand=True, resample=Image.BICUBIC)
        img.alpha_composite(im2, (x0 + i * 220 - 10, 190 + t.height + 10))
    t2 = E.titulo("...VAI CURTIR ESSES\nJOGOS DE TABULEIRO!", 74, cor=(255, 255, 255), larg_max=980)
    cola_centro(img, t2, W // 2, 190 + t.height + 330)
    lq = E.leque([p[4] for p in pares], 200)
    if lq.width > W - 120:
        lq = lq.resize((W - 120, int(lq.height * (W - 120) / lq.width)), Image.LANCZOS)
    cola_centro(img, lq, W // 2, H - lq.height - 40)
    return img


# ----------------------------------------------------------------------------------------- final + stories
def tela_final(modo, pares, story=False):
    hh = 1920 if story else H
    img = (_fundo_pipoca(hh, 50) if modo == "animacao" else _fundo_cortina(hh)).copy()
    y = logo_topo(img, 40 if story else 30, 200) + 30
    t = E.titulo("FIM... OU SÓ O\nCOMEÇO DA SESSÃO?", 78, cor=(255, 255, 255) if modo == "animacao" else (255, 214, 102),
                 larg_max=980)
    cola_centro(img, t, W // 2, y)
    y += t.height + 10
    cw, ch = 900, 470
    img.alpha_composite(E.bloco(cw, ch, CREME, raio=40, ow=8, sombra=14), ((W - cw) // 2, y))
    lq = E.leque([p[4] for p in pares], 200, passo=0.5)
    if lq.width > cw - 60:
        lq = lq.resize((cw - 60, int(lq.height * (cw - 60) / lq.width)), Image.LANCZOS)
    cola_centro(img, lq, W // 2, y + 24)
    yy = y + 24 + lq.height - 6
    for txt, s, cor in [("Aluga na Sua Vez: retire em Mauá ou receba em casa", 31, E.MARROM),
                        ("3 jogos = 7 dias pelo mesmo preço!", 31, E.PETROLEO)]:
        tt = E.texto(txt, s, cor=cor, peso=800, larg_max=820)
        cola_centro(img, tt, W // 2, yy)
        yy += tt.height
    pl = E.pilula("LINK NA BIO · @SUAVEZ_BG", 32, E.AMARELO, E.MARROM, fonte_titulo=True)
    cola_centro(img, pl, W // 2, yy + 8)
    y += ch + 40
    c = E.titulo("COMENTA: QUAL " + ("ANIMAÇÃO" if modo == "animacao" else "FILME") + "\nFICOU FALTANDO?", 56,
                 cor=E.LARANJA if modo == "animacao" else (255, 255, 255), larg_max=980)
    cola_centro(img, c, W // 2, y)
    if story:
        y += c.height + 40
        tt = E.texto("aluga aqui:", 42, cor=E.MARROM if modo == "animacao" else (255, 255, 255), peso=900)
        cola_centro(img, tt, W // 2, y)
        d = ImageDraw.Draw(img)
        cx, yy = W // 2, y + tt.height + 10
        d.polygon([(cx - 34, yy), (cx + 34, yy), (cx, yy + 46)], fill=E.LARANJA, outline=E.MARROM, width=5)
    return img


def story_de(modo, tela):
    st = (_fundo_pipoca(1920, 77) if modo == "animacao" else _fundo_cortina(1920)).copy()
    st.alpha_composite(tela, (0, 285))
    return st


def main():
    modo = sys.argv[1]
    pares = LISTAS[modo]
    out = os.path.join(ROOT, "out", modo)
    os.makedirs(os.path.join(out, "stories"), exist_ok=True)
    capa = capa_animacao if modo == "animacao" else capa_filmes
    tela = tela_animacao if modo == "animacao" else tela_filmes
    if "--teste" in sys.argv:
        a, b = capa(pares), tela(0, pares)
        f = Image.new("RGB", (W * 2 + 40, H), (255, 255, 255))
        f.paste(a.convert("RGB"), (0, 0))
        f.paste(b.convert("RGB"), (W + 40, 0))
        f.save(os.path.join(out, "teste.jpg"), quality=90)
        print("ok teste")
        return
    telas = [capa(pares)] + [tela(k, pares) for k in range(len(pares))] + [tela_final(modo, pares)]
    for i, t in enumerate(telas, 1):
        t.convert("RGB").save(os.path.join(out, f"{i:02d}.png"))
        st = tela_final(modo, pares, story=True) if i == len(telas) else story_de(modo, t)
        st.convert("RGB").save(os.path.join(out, "stories", f"story_{i:02d}.png"))
    folha = Image.new("RGB", (5 * 370 + 10, 2 * 460 + 10), (255, 255, 255))
    for i, t in enumerate(telas):
        folha.paste(t.convert("RGB").resize((360, 450)), (10 + (i % 5) * 370, 10 + (i // 5) * 460))
    folha.save(os.path.join(out, "previa.jpg"), quality=88)
    print("ok", len(telas))


if __name__ == "__main__":
    main()
