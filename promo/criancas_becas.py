#!/usr/bin/env python3
"""Carrossel "VAI LEVAR AS CRIANÇAS?" da TARDE DE JOGOS NO BECA’S (10/nov/2026, ideia dele: uma moça perguntou a idade
mínima). Mostra jogos que vão estar na mesa, com o básico: idade, jogadores, tempo e uma frase do que é.

Visual da linha das guarda-chuvinhas (`becas_chuva.py`), com um elemento novo: cada guarda-chuvinha segura a CAIXA e
outro segura uma ETIQUETA DE IDADE redonda grande ("A PARTIR DE 5 ANOS"), a informação que a moça perguntou.

Idades CONFERIDAS na editora (o site da Sua Vez às vezes diverge, ex.: Coffee Rush aparece 8+ no site e é 14+ na
Galápagos): Go Cuckoo 5+ (Devir), Taco Gato 6+ (PaperGames), Gravity Superstar, Bananagrams e Dixit 8+
(API da Galápagos, x_faixaEtaria), Draftosaurus 8+ (MeepleBR), King of Tokyo 8+ (Devir/IELLO), UNO Stacko 7+ e 2 a 10 (Mattel; ele pediu no lugar do The Mind:
"pode ser jogado por criança mais jovem").

    /usr/bin/python3 criancas_becas.py
      → out/becas/criancas/01..11.png (1080x1350) + stories/story_01..11.png (1080x1920) + previa*.jpg
"""
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

import becas_chuva as BC
import tarde_becas as TB
from tarde_becas import E, MAR, PET, LAR, AMA, BR, ROSA, CREME, WHATS

REPO = TB.REPO
OUT = os.path.join(TB.OUT, "criancas")
VERDE = BC.VERDE
W, H = 1080, 1350

# (nome, arquivo da caixa, idade, jogadores, tempo, frase, cor)
JOGOS = [
    ("Taco Gato Cabra\nQueijo Pizza", "promo/assets/criancas/taco_gato.png", 6, "2 a 8", "10 min",
     "Vira a carta falando a palavra. Carta e palavra iguais? Todo mundo bate na pilha: o último leva!", AMA),
    ("UNO Stacko", "promo/assets/criancas/uno_stacko.png", 7, "2 a 10", "partida rápida",
     "Tire da torre um bloco da cor ou do número pedido e ponha no topo. Derrubou, perdeu!", ROSA),
    ("Dixit", "hobby-reels/assets/caixas/dixit.png", 8, "3 a 6", "30 min",
     "Dê uma pista sobre uma carta ilustrada e veja quem adivinha qual é!", LAR),
    ("King of Tokyo", "hobby-reels/assets/caixas/king_of_tokyo.png", 8, "2 a 6", "30 min",
     "Monstros gigantes rolam dados e brigam pra ser o rei de Tóquio!", VERDE),
    ("Splendor Duel", "gravados-reels/assets/lista/splendor_duel.png", 10, "2", "30 min",
     "Duelo pra dois: junte pedras preciosas, compre cartas e chegue ao prestígio antes do outro!", PET),
    ("Take Time", "feed-posts/assets/take_time.png", 10, "2 a 4", "30 min",
     "Cooperativo e quase sem conversar: todos juntos pra completar o relógio!", ROSA),
    ("Spyfall", "promo/assets/criancas/spyfall_capa.png", 13, "3 a 8", "15 min",
     "Todo mundo sabe o lugar... menos o espião! Pergunte e descubra quem é ele.", LAR),
    ("Hitster", "gravados-reels/assets/lista/hitster.png", 14, "2 a 10", "30 min",
     "Ouça a música e encaixe na sua linha do tempo: ela saiu antes ou depois?", PET),
    ("Coffee Rush", "coffee-reels/assets/caixa.png", 14, "2 a 4", "30 min",
     "Vire barista: junte os ingredientes e entregue os pedidos antes da fila crescer!", VERDE),
]
# os outros jogos da lista da tarde (caixas recortadas do site) para a tela "e tem muito mais"
OUTROS = ["telma", "tapalavras", "say_my_name", "uga_buga", "santorini", "marrakech", "draftosaurus", "hive",
          "wandering_towers", "canvas", "dixit_disney_edition", "break_the_cube"]


# ---------------------------------------------------------------- recortes (fotos de produto em fundo branco)
def recorta_branco(src, dst, limiar=242):
    im = Image.open(src).convert("RGB")
    a = np.asarray(im).astype(int)
    claro = a.min(2) >= limiar
    lab, _ = ndimage.label(claro)
    borda = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])) - {0}
    fundo = np.isin(lab, list(borda))
    obj = ndimage.binary_fill_holes(ndimage.binary_opening(~fundo, iterations=2))
    lab2, n = ndimage.label(obj)
    if n > 1:
        tam = ndimage.sum(obj, lab2, range(1, n + 1))
        obj = lab2 == (1 + int(np.argmax(tam)))
    m = Image.fromarray((obj * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
    out = im.convert("RGBA")
    out.putalpha(m)
    out = out.crop(out.getbbox())
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    out.save(dst)
    print("recorte", dst, out.size)


def prepara():
    d = os.path.join(TB.ROOT, "assets", "criancas")
    if not os.path.exists(os.path.join(d, "the_mind.png")):
        # foto 3D oficial da Galápagos (ccstore/v1/products/TMI001 → primaryFullImageURL, 1600 px)
        recorta_branco(os.path.join(d, "orig", "the_mind.png"), os.path.join(d, "the_mind.png"))
    if not os.path.exists(os.path.join(d, "uno_stacko.png")):
        # foto oficial da Mattel na Ri Happy (VTEX, 1500 px): só a caixa, sem a torre montada ao lado
        recorta_branco(os.path.join(d, "orig", "uno_stacko_caixa.png"), os.path.join(d, "uno_stacko.png"))
    if not os.path.exists(os.path.join(d, "taco_gato.png")):
        recorta_branco(os.path.join(REPO, "taco-reels", "assets", "caixa_frente.png"), os.path.join(d, "taco_gato.png"))


def caixa(path, hmax, wmax=None):
    im = Image.open(os.path.join(REPO, path)).convert("RGBA")
    im = im.crop(im.getbbox())
    esc = hmax / im.height
    if wmax and im.width * esc > wmax:
        esc = wmax / im.width
    im = im.resize((int(im.width * esc), int(im.height * esc)), Image.LANCZOS)
    if "capa" in path:  # capa plana com fundo branco: contorno para não sumir no creme
        ImageDraw.Draw(im).rectangle((0, 0, im.width - 1, im.height - 1), outline=MAR, width=5)
    sh = Image.new("RGBA", (im.width + 28, im.height + 28), (0, 0, 0, 0))
    sh.paste(MAR + (120,), (14, 18), im.getchannel("A"))
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    sh.alpha_composite(im, (2, 2))
    return sh


# ---------------------------------------------------------------- peças
def etiqueta_idade(idade, cor, diam=360):
    """Etiqueta redonda de idade, a informação principal: A PARTIR DE / 5 / ANOS."""
    linhas = [("A PARTIR DE", E.lilita(36), MAR), (str(idade), E.lilita(200), BR if cor != AMA else LAR),
              ("ANOS", E.lilita(58), MAR)]
    fundo = BR if cor == AMA else cor
    if fundo in (PET, ROSA, VERDE, LAR):
        linhas = [("A PARTIR DE", E.lilita(36), BR), (str(idade), E.lilita(200), AMA), ("ANOS", E.lilita(58), BR)]
    return BC.disco(diam, fundo, linhas)


def icone_pessoas(s, cor):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for dx, k in ((-0.2, 0.8), (0.12, 1.0)):
        cx = s * (0.5 + dx)
        r = s * 0.15 * k
        d.ellipse((cx - r, s * 0.16, cx + r, s * 0.16 + 2 * r), fill=cor)
        d.rounded_rectangle((cx - r * 1.6, s * 0.2 + 2 * r, cx + r * 1.6, s * 0.92), int(r), fill=cor)
    return im


def icone_relogio(s, cor):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    m = s * 0.08
    d.ellipse((m, m, s - m, s - m), outline=cor, width=max(4, s // 9))
    c = s / 2
    d.line((c, c, c, s * 0.27), fill=cor, width=max(4, s // 10))
    d.line((c, c, s * 0.7, c), fill=cor, width=max(4, s // 10))
    return im


def chip(icone, txt, s=40, cor=BR, cor_txt=MAR):
    f = E.fig(s, 900)
    tw = int(E._larg(txt, f))
    ic = icone(int(s * 1.25), cor_txt)
    w, h = 30 + ic.width + 14 + tw + 34, int(s * 1.9)
    p = E.bloco(w, h, cor, raio=h // 2, ow=5, sombra=7).copy()
    p.alpha_composite(ic, (26, (h - ic.height) // 2 - 2))
    ImageDraw.Draw(p).text((26 + ic.width + 14, h / 2 - 3), txt, font=f, fill=cor_txt, anchor="lm")
    return p


def ficha(nome, jog, tempo, frase, cor, w=960):
    nlin = nome.count("\n") + 1
    s = 84 if nlin == 1 else 66
    tit = E.titulo(nome.upper(), s, cor if cor != AMA else LAR, larg_max=w - 80)
    a = chip(icone_pessoas, jog + " jogadores", 40)
    b = chip(icone_relogio, tempo, 40)
    t = E.texto(frase, 44, MAR, 800, larg_max=w - 100, entre=1.2)
    y1 = 22 + tit.height + 4
    y2 = y1 + a.height + 14
    h = y2 + t.height + 36
    c = E.bloco(w, h, BR, raio=36, ow=7, sombra=12).copy()
    c.alpha_composite(tit, (int(w / 2 - tit.width / 2), 22))
    gap = 26
    x0 = int(w / 2 - (a.width + gap + b.width) / 2)
    c.alpha_composite(a, (x0, y1))
    c.alpha_composite(b, (x0 + a.width + gap, y1))
    c.alpha_composite(t, (int(w / 2 - t.width / 2), y2))
    return c


def rodape(img, txt="TARDE DE JOGOS NO BECA’S · 20/11"):
    E.cola(img, E.pilula(txt, 30, PET, BR, fonte_titulo=True), W / 2, H - 52, 0)


# ---------------------------------------------------------------- telas
def tela_capa():
    """Capa com a ESCADINHA de idade: cada degrau (6+ ... 14+) com uma caixa em cima."""
    img = BC.fundo_leve(W, H, 41)
    for k, (x, y, wg) in enumerate([(110, 50, 140), (330, 110, 120), (750, 110, 120), (970, 50, 140)]):
        BC.segura(img, x, y, wg, BC.CORES[k], seed=k)
    E.cola(img, E.pilula("TARDE DE JOGOS NO BECA’S · 20/11", 34, PET, BR, fonte_titulo=True), W / 2, 300, -1)
    E.cola(img, E.titulo("TEM JOGO PRA\nTODA IDADE!", 128, LAR), W / 2, 470, -2)
    degraus = [(0, 6), (1, 7), (2, 8), (4, 10), (6, 13), (7, 14)]
    cores = [AMA, ROSA, LAR, PET, VERDE, ROSA]
    base, larg, x0 = 1210, 168, 36
    d = ImageDraw.Draw(img)
    for k, (j, idade) in enumerate(degraus):
        x = x0 + k * larg
        h = 110 + k * 62
        d.rounded_rectangle((x + 9, base - h + 9, x + larg + 9, base + 9), 14, fill=MAR)
        d.rounded_rectangle((x, base - h, x + larg, base), 14, fill=cores[k], outline=MAR, width=6)
        d.text((x + larg / 2, base - h + 52), f"{idade}+", font=E.lilita(62), fill=BR if cores[k] != AMA else MAR,
               anchor="mm", stroke_width=4 if cores[k] != AMA else 0, stroke_fill=MAR)
        cx = caixa(JOGOS[j][1], 175, 150)
        img.alpha_composite(cx, (int(x + larg / 2 - cx.width / 2), int(base - h - cx.height + 10)))
    E.cola(img, E.pilula("idade, quantos jogam e o que é cada um  →", 32, AMA, MAR), W / 2, 1290, 0)
    return img


def tela_jogo(k):
    nome, path, idade, jog, tempo, frase, cor = JOGOS[k]
    img = BC.fundo_leve(W, H, 50 + k)
    rnd = random.Random(k)
    fi = ficha(nome, jog, tempo, frase, cor)
    topo_ficha = 1225 - fi.height
    y_gc = 36 + rnd.randint(0, 24)
    topo_caixa = y_gc - 6 + 14 + 0.75 * 190 + 2 + 20
    cb = caixa(path, min(560, int(topo_ficha - 40 - topo_caixa)), 470)
    # caixa à esquerda, etiqueta à direita, cada uma no seu guarda-chuvinha
    BC.segura(img, 300, y_gc, 190, cor, cb, gap=20, rot=rnd.choice((-3, -2, 2, 3)), seed=k)
    BC.segura(img, 805, 90 + rnd.randint(0, 40), 170, BC.CORES[(k + 2) % 5], etiqueta_idade(idade, cor),
              gap=24, rot=rnd.choice((-5, 5)), seed=k + 9)
    E.cola(img, fi, W / 2, topo_ficha + fi.height / 2, 0)
    rodape(img)
    return img


def tela_mais():
    img = BC.fundo_leve(W, H, 61)
    E.cola(img, E.titulo("E TEM MUITO\nMAIS NA MESA!", 104, LAR), W / 2, 200, -1.5)
    cxs = [n for n in OUTROS if os.path.exists(os.path.join(TB.CX, n + ".png"))][:12]
    cols, x0, y0, dx, dy = 4, 150, 420, 260, 265
    for k, n in enumerate(cxs):
        x = x0 + (k % cols) * dx + (65 if k >= 8 else 0) * (len(cxs) - 8 == 3)
        y = y0 + (k // cols) * dy
        E.cola(img, TB.caixa(n, 215), x, y, (-5, 4, -3, 5)[k % 4])
    E.cola(img, E.pilula("Mais de 30 jogos pra todas as idades", 40, PET, BR), W / 2, 1290 - 110, -1)
    E.cola(img, E.pilula("e a gente ensina todos, mesa por mesa!", 36, AMA, MAR), W / 2, 1290 - 25, 1)
    return img


def tela_final():
    img = TB.fundo(W, H, [60, 120, 40, 105, 50, 115], 140)
    E.cola(img, E.titulo("TRAZ A\nGALERA!", 140, LAR), W / 2, 450, -2)
    E.cola(img, TB.selo_data(38), W / 2, 640, 1.5)
    E.cola(img, TB.selo_endereco(28), W / 2, 712, -1)
    E.cola(img, TB.inscricao(900), W / 2, 880, 0)
    E.cola(img, E.pilula("Comenta: qual desses você quer jogar?", 38, AMA, MAR), W / 2, 1080, -1.5)
    lg = TB.parceria(130)
    img.alpha_composite(lg, (int(W / 2 - lg.width / 2), 1170))
    return img


# ---------------------------------------------------------------- stories
def story_de(tela, seed):
    """Tela no meio (y 285–1635); os fios que saem do topo da tela continuam até o alto do Story."""
    bg = BC.fundo_leve(1080, 1920, seed)
    bg.alpha_composite(tela.convert("RGBA"), (0, 285))
    a = np.asarray(tela.convert("RGB"))[2].astype(int)
    fio = np.all(np.abs(a - np.array(BC.FIO)) < 18, axis=1)
    d = ImageDraw.Draw(bg)
    xs = np.where(fio)[0]
    for grupo in np.split(xs, np.where(np.diff(xs) > 2)[0] + 1) if len(xs) else []:
        x = float(grupo.mean())
        d.line([(x, 0), (x, 287)], fill=BC.FIO, width=3)
    return bg


def seta(cor):
    im = Image.new("RGBA", (130, 140), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.line([(20, 20), (60, 70), (55, 120)], fill=cor, width=10, joint="curve")
    d.polygon([(30, 105), (80, 108), (54, 136)], fill=cor)
    return im


def story_final():
    S = Image.new("RGBA", (1080, 1920))
    img = TB.fundo(1080, 1920, [60, 120, 40, 105, 50, 115], 140)
    E.cola(img, E.titulo("TRAZ A\nGALERA!", 136, LAR), 540, 480, -2)
    E.cola(img, TB.selo_data(38), 540, 680, 1.5)
    E.cola(img, TB.selo_endereco(28), 540, 752, -1)
    E.cola(img, TB.inscricao(900), 540, 930, 0)
    lin = Image.new("RGBA", (1080, 150), (0, 0, 0, 0))
    ImageDraw.Draw(lin).text((480, 60), "garanta sua mesa aqui:", font=E.fig(46, 900), fill=MAR, anchor="mm")
    lin.alpha_composite(seta(MAR), (760, 0))
    img.alpha_composite(lin, (0, 1130))
    # y ≈ 1350–1580 LIVRE para o adesivo de link
    lg = TB.parceria(120)
    img.alpha_composite(lg, (int(540 - lg.width / 2), 1660))
    return img


def main():
    prepara()
    os.makedirs(os.path.join(OUT, "stories"), exist_ok=True)
    telas = [tela_capa()] + [tela_jogo(k) for k in range(len(JOGOS))] + [tela_mais(), tela_final()]
    stories = [story_de(t, 70 + k) for k, t in enumerate(telas[:-1])] + [story_final()]
    for k, im in enumerate(telas):
        im.convert("RGB").save(os.path.join(OUT, f"{k + 1:02d}.png"))
    for k, im in enumerate(stories):
        im.convert("RGB").save(os.path.join(OUT, "stories", f"story_{k + 1:02d}.png"))
    for lista, nome, ww, hh in ((telas, "previa.jpg", W, H), (stories, "previa_stories.jpg", 1080, 1920)):
        w = 300
        h = int(w * hh / ww)
        cols = 6
        rows = (len(lista) + cols - 1) // cols
        sh = Image.new("RGB", (cols * (w + 10) + 10, rows * (h + 10) + 10), (240, 236, 228))
        for k, im in enumerate(lista):
            sh.paste(im.convert("RGB").resize((w, h), Image.LANCZOS), (10 + (k % cols) * (w + 10), 10 + (k // cols) * (h + 10)))
        sh.save(os.path.join(OUT, nome), quality=88)
    print("ok", OUT, len(telas))


if __name__ == "__main__":
    main()
