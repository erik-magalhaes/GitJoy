#!/usr/bin/env python3
"""Stories NOVOS das assinaturas (27/nov/2026, junto com a Black Friday). Conceito novo: O CICLO SEM FIM — as caixas do
acervo girando numa roda com setas (devolve → escolhe outro → joga), em fundo petróleo com bolinhas; identidade da
Jéssica. Sem citar taxa. Espaço LIVRE para o adesivo de link logo abaixo da seta, no meio da tela (ele não quer o link baixo).

  1  gancho: "E SE VOCÊ PUDESSE TROCAR DE JOGO QUANTAS VEZES QUISER?" + roda de caixas
  2  como funciona (3 passos) + "trocas sem limite no mês"
  3  os 3 planos lado a lado (Silver / Gold / Platinum) + "assine pelo link"

    /usr/bin/python3 stories_nov.py    # out/stories_nov/story_{1,2,3}.png + post_{1,2,3}.png (1080x1350)
"""
import math
import os
import random

from PIL import Image, ImageDraw

from estilo import (MARROM, PETROLEO, LARANJA, AMARELO, BRANCO, PRATA, PLANOS, titulo, texto, bloco, pilula, logo, cola,
                    jogo)

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
AC = os.path.join(REPO, "hobby-reels", "assets", "acervo")
OUT = os.path.join(ROOT, "out", "stories_nov")
W = 1080
RODA = ["wingspan.png", "harmonies.png", "sea_salt_paper.png", "draftosaurus.png", "hitster.png", "ticket_to_ride.png",
        "king_of_tokyo.png", "clank_catacombs.png"]


def fundo(h, semente):
    img = Image.new("RGBA", (W, h), PETROLEO + (255,))
    d = ImageDraw.Draw(img)
    for y in range(30, h, 60):
        for x in range(30 + (30 if (y // 60) % 2 else 0), W, 60):
            d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(40, 140, 166))
    rnd = random.Random(semente)
    for _ in range(26):
        x, y = rnd.randint(0, W), rnd.randint(0, h)
        if 160 < x < W - 160 and 300 < y < h - 300:
            continue
        cor = rnd.choice([AMARELO, LARANJA, BRANCO])
        r = rnd.randint(8, 14)
        d.ellipse((x - r, y - r, x + r, y + r), fill=cor)
    return img


def centro(img, im, cx, y):
    img.alpha_composite(im, (int(cx - im.width / 2), int(y)))


def roda(raio=300, h=170):
    """As caixas numa roda, com setas curvas entre elas: a ideia de trocar sem parar."""
    tam = raio * 2 + h + 60
    im = Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = tam / 2
    d.ellipse((c - raio, c - raio, c + raio, c + raio), outline=AMARELO, width=14)
    n = len(RODA)
    for i in range(n):  # setinhas na roda (sentido horário)
        a = (i + 0.5) / n * 2 * math.pi - math.pi / 2
        x, y = c + raio * math.cos(a), c + raio * math.sin(a)
        t = a + math.pi / 2
        p = [(x + 26 * math.cos(t), y + 26 * math.sin(t)),
             (x + 18 * math.cos(t + 2.4), y + 18 * math.sin(t + 2.4)),
             (x + 18 * math.cos(t - 2.4), y + 18 * math.sin(t - 2.4))]
        d.polygon(p, fill=AMARELO, outline=MARROM)
    for i, f in enumerate(RODA):
        a = i / n * 2 * math.pi - math.pi / 2
        cx = jogo(os.path.join(AC, f), h, int(h * 1.05))
        cola(im, cx, c + raio * math.cos(a), c + raio * math.sin(a), (-6, 5, -3, 7, -5, 4, -7, 6)[i])
    centro(im, logo(int(raio * 0.95)), c, c - logo(int(raio * 0.95)).height / 2)
    return im


def seta_link(img, y, txt):
    p = pilula(txt, 50, AMARELO, MARROM, pad=(36, 14), fonte_titulo=True)
    centro(img, p, W / 2, y)
    d = ImageDraw.Draw(img)
    cx = W / 2
    yy = y + p.height + 12
    d.rounded_rectangle((cx - 12, yy, cx + 12, yy + 30), radius=12, fill=MARROM)
    d.polygon([(cx - 36, yy + 24), (cx + 36, yy + 24), (cx, yy + 62)], fill=MARROM)


def s1(h=1920, link=True):
    img = fundo(h, 1)
    y0 = 140 if h == 1920 else 50
    t = titulo("E SE VOCÊ PUDESSE\nTROCAR DE JOGO\nQUANTAS VEZES QUISER?", 84, BRANCO, larg_max=1000)
    centro(img, t, W / 2, y0)
    r = roda(300 if h == 1920 else 270)
    centro(img, r, W / 2, y0 + t.height - 20)
    yb = y0 + t.height - 20 + r.height - 30
    pl = pilula("ASSINATURA SUA VEZ", 48, LARANJA, BRANCO, pad=(30, 12), fonte_titulo=True)
    centro(img, pl, W / 2, yb)
    if link:
        seta_link(img, 1420, "CONHEÇA OS PLANOS")
    return img


def s2(h=1920, link=True):
    img = fundo(h, 2)
    y = 150 if h == 1920 else 60
    t = titulo("COMO FUNCIONA\nA ASSINATURA?", 96, AMARELO, larg_max=980)
    centro(img, t, W / 2, y)
    y += t.height + 10
    passos = [("1", "Escolha o plano e os seus jogos", LARANJA),
              ("2", "Jogou e cansou? Devolve e pega outro", PETROLEO),
              ("3", "Troque quantas vezes quiser no mês", (120, 70, 160))]
    for n, txt, cor in passos:
        c = bloco(900, 170, (255, 248, 232), raio=34, ow=7, sombra=10)
        d = ImageDraw.Draw(c)
        d.ellipse((30, 25, 150, 145), fill=cor, outline=MARROM, width=6)
        from estilo import lilita
        d.text((90, 88), n, font=lilita(80), fill=BRANCO, anchor="mm")
        tx = texto(txt, 42, MARROM, 800, larg_max=680, alinha="lm")
        c.alpha_composite(tx, (180, (170 - tx.height) // 2))
        centro(img, c, W / 2, y)
        y += 200
    pl = pilula("TROCAS SEM LIMITE NO MÊS!", 54, AMARELO, MARROM, pad=(34, 14), fonte_titulo=True)
    centro(img, pl, W / 2, y + 10)
    tx = texto("Retire em Mauá ou receba em casa", 38, BRANCO, 800)
    centro(img, tx, W / 2, y + 10 + pl.height + 20)
    if link:
        seta_link(img, 1280, "ASSINE PELO LINK")
    return img


def mini(k):
    nome, preco, por_vez, cats, cor, cor_tit, obs = PLANOS[k]
    c = bloco(310, 560, cor, raio=30, ow=7, sombra=10)
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((18, 18, 292, 190), radius=22, fill=BRANCO, outline=MARROM, width=5)
    cola(c, titulo(nome, 56 if nome != "PLATINUM" else 46, cor if cor != PRATA else (150, 166, 175), sw=5, sombra=5),
         155, 70)
    cola(c, titulo(f"R$ {preco}", 60, MARROM, BRANCO, sw=0, sombra=0), 155, 140)
    cola(c, texto("por mês", 28, cor_tit, 800), 155, 222)
    cola(c, titulo(f"{por_vez} JOGO{'S' if por_vez > 1 else ''}\nPOR VEZ", 46, BRANCO, sw=5, sombra=4), 155, 310)
    cats_txt = {0: "Pocket e\nFamília", 1: "Pocket, Família\ne Estratégico", 2: "o acervo\ninteiro"}[k]
    cola(c, texto(cats_txt, 30, cor_tit, 800, entre=1.15), 155, 430)
    if obs:
        cola(c, texto("até 1 Deluxe por vez", 22, cor_tit, 700), 155, 520)
    return c


def s3(h=1920, link=True):
    img = fundo(h, 3)
    y = 150 if h == 1920 else 60
    t = titulo("ESCOLHA O SEU PLANO", 84, BRANCO, larg_max=1000)
    centro(img, t, W / 2, y)
    y += t.height + 30
    for k in range(3):
        m = mini(k)
        cola(img, m, W / 2 + (k - 1) * 340, y + m.height / 2, (-2, 1.5, -1.5)[k])
    y += 600
    tx = texto("Trocas sem limite no mês · retire em Mauá ou receba em casa", 34, BRANCO, 800, larg_max=900)
    centro(img, tx, W / 2, y)
    if link:
        seta_link(img, 1200, "ASSINE PELO LINK")
    else:
        pl = pilula("ASSINE PELO LINK NA BIO · @SUAVEZ_BG", 38, AMARELO, MARROM, fonte_titulo=True)
        centro(img, pl, W / 2, h - pl.height - 60)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    for i, f in enumerate((s1, s2, s3), 1):
        f().convert("RGB").save(os.path.join(OUT, f"story_{i}.png"))
        f(1350, link=False).convert("RGB").save(os.path.join(OUT, f"post_{i}.png"))
    ims = [Image.open(os.path.join(OUT, f"story_{i}.png")).resize((360, 640)) for i in (1, 2, 3)]
    ims += [Image.open(os.path.join(OUT, f"post_{i}.png")).resize((360, 450)) for i in (1, 2, 3)]
    f = Image.new("RGB", (6 * 370, 650), (255, 255, 255))
    for i, im in enumerate(ims):
        f.paste(im, (i * 370, 0))
    f.save(os.path.join(OUT, "previa.jpg"), quality=88)
    print("ok")


if __name__ == "__main__":
    main()
