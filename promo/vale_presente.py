#!/usr/bin/env python3
"""VALE-PRESENTE da Sua Vez (27/nov/2026, novidade no site). Divulgação para o Natal: "DÊ DE PRESENTE UMA NOITE DE
JOGOS". Conceito: o próprio VALE como um cartão de presente (creme com contorno marrom, laço laranja e fita petróleo,
picote, "VALE-PRESENTE / SUA VEZ / uma noite de jogos pra quem você ama"), sobre papel de presente petróleo com
bolinhas e estrelinhas, caixas do acervo saindo de trás do cartão. Sem valores (ele ainda não passou): fica "você escolhe
o valor" só se ele confirmar. Feed 1080x1350 + quadrado 1080x1080 + story 1080x1920 (espaço do link no meio).

    /usr/bin/python3 vale_presente.py   # out/vale_presente/
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
import estilo as E  # noqa: E402

AC = os.path.join(REPO, "hobby-reels", "assets", "acervo")
OUT = os.path.join(ROOT, "out", "vale_presente")
W = 1080
FUNDO = (20, 96, 118)
CREME = (255, 246, 228)
BRANCO = (255, 255, 255)
CAIXAS = [os.path.join(AC, f) for f in ("dixit.png", "ticket_to_ride.png", "harmonies.png", "hitster.png")]


def fundo(h, semente=1):
    img = Image.new("RGBA", (W, h), FUNDO + (255,))
    d = ImageDraw.Draw(img)
    for y in range(24, h, 48):
        for x in range(24 + (24 if (y // 48) % 2 else 0), W, 48):
            d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(34, 118, 140))
    rnd = random.Random(semente)
    for _ in range(40):  # estrelinhas desenhadas (a fonte não tem ✦)
        x, y = rnd.randint(0, W), rnd.randint(0, h)
        r = rnd.randint(10, 20)
        cor = rnd.choice([E.AMARELO, BRANCO, E.LARANJA])
        pts = []
        for k in range(8):
            a = k * math.pi / 4
            rr = r if k % 2 == 0 else r * 0.35
            pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
        d.polygon(pts, fill=cor)
    return img


def centro(img, im, cx, y):
    img.alpha_composite(im, (int(cx - im.width / 2), int(y)))


def laco(s=220):
    """Laço laranja desenhado (2 alças + nó + 2 pontas)."""
    im = Image.new("RGBA", (s * 2, s * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = s
    for sinal in (-1, 1):
        p = [(c, c), (c + sinal * s * 0.95, c - s * 0.55), (c + sinal * s * 0.95, c + s * 0.35)]
        d.polygon([(x + 8, y + 8) for x, y in p], fill=E.MARROM)
        d.polygon(p, fill=E.LARANJA, outline=E.MARROM, width=8)
        q = [(c, c), (c + sinal * s * 0.55, c + s * 0.95), (c + sinal * s * 0.25, c + s * 0.95)]
        d.polygon(q, fill=(222, 110, 20), outline=E.MARROM, width=7)
    d.ellipse((c - s * 0.22, c - s * 0.22, c + s * 0.22, c + s * 0.22), fill=E.LARANJA, outline=E.MARROM, width=8)
    return im.crop(im.getbbox())


def vale(w=860, h=520):
    """O cartão do vale: creme, fita petróleo vertical à esquerda com o laço, picote, textos."""
    c = E.bloco(w, h, CREME, raio=40, ow=8, sombra=16)
    d = ImageDraw.Draw(c)
    fx = int(w * 0.2)
    d.rectangle((fx - 34, 4, fx + 34, h - 4), fill=E.PETROLEO)
    d.line((fx - 34, 4, fx - 34, h - 4), fill=E.MARROM, width=5)
    d.line((fx + 34, 4, fx + 34, h - 4), fill=E.MARROM, width=5)
    for y in range(30, h - 20, 26):  # picote
        d.line((fx + 70, y, fx + 70, y + 12), fill=E.MARROM, width=4)
    l = laco(150)
    c.alpha_composite(l, (int(fx - l.width / 2), int(h * 0.12)))
    cx = fx + 70 + (w - fx - 70) / 2
    t1 = E.pilula("VALE-PRESENTE", 46, E.LARANJA, BRANCO, fonte_titulo=True)
    c.alpha_composite(t1, (int(cx - t1.width / 2), 50))
    lg = E.logo(330)
    c.alpha_composite(lg, (int(cx - lg.width / 2), 50 + t1.height + 18))
    tx = E.texto("uma noite de jogos\npra quem você ama", 40, E.MARROM, 800, entre=1.15)
    c.alpha_composite(tx, (int(cx - tx.width / 2), 50 + t1.height + 18 + lg.height + 16))
    return c.rotate(-4, expand=True, resample=Image.BICUBIC)


def composicao(img, y_cartao, larg=860):
    k = larg / 860
    ims = [E.jogo(p, int(300 * k), int(300 * k)) for p in CAIXAS]
    xs = [W / 2 + (x - 540) * k for x in (170, 400, 680, 910)]
    rots = [-12, 6, -6, 12]
    for i, im in enumerate(ims):  # caixas saindo de trás do cartão
        r = im.rotate(rots[i], expand=True, resample=Image.BICUBIC)
        img.alpha_composite(r, (int(xs[i] - r.width / 2), int(y_cartao - r.height * 0.62)))
    v = vale(860, 516)
    if k != 1:
        v = v.resize((int(v.width * k), int(v.height * k)), Image.LANCZOS)
    centro(img, v, W / 2, y_cartao)
    return y_cartao + v.height


def post(h=1350):
    img = fundo(h, 1)
    sq = h == 1080
    y = 50 if sq else 90
    t = E.titulo("DÊ DE PRESENTE\nUMA NOITE DE JOGOS!", 88 if sq else 96, BRANCO, larg_max=1000)
    centro(img, t, W / 2, y)
    y += t.height + (170 if sq else 200)
    y = composicao(img, y, 720 if sq else 820)
    tx = E.texto("Natal, aniversário, amigo secreto...\no presente que vira diversão.", 34, BRANCO, 800,
                 larg_max=900)
    if not sq:
        centro(img, tx, W / 2, y - 6)
    pl = E.pilula("GARANTA O SEU PELO LINK NA BIO", 40, E.AMARELO, E.MARROM, fonte_titulo=True)
    centro(img, pl, W / 2, h - pl.height - 30)
    return img


def story():
    h = 1920
    img = fundo(h, 2)
    y = 170
    pl = E.pilula("NOVIDADE!", 46, E.LARANJA, BRANCO, fonte_titulo=True)
    centro(img, pl, W / 2, y)
    y += pl.height + 20
    t = E.titulo("DÊ DE PRESENTE\nUMA NOITE DE JOGOS!", 96, BRANCO, larg_max=1000)
    centro(img, t, W / 2, y)
    y += t.height + 200
    y = composicao(img, y, 860)
    tx = E.texto("Natal, aniversário, amigo secreto...\no presente que vira diversão.", 40, BRANCO, 800, larg_max=900)
    centro(img, tx, W / 2, y)
    y += tx.height + 30
    p2 = E.pilula("COMPRE SEU VALE-PRESENTE AQUI:", 42, E.AMARELO, E.MARROM, fonte_titulo=True)
    centro(img, p2, W / 2, y)
    d = ImageDraw.Draw(img)
    yy = y + p2.height + 10
    d.polygon([(W / 2 - 36, yy), (W / 2 + 36, yy), (W / 2, yy + 46)], fill=E.AMARELO, outline=E.MARROM, width=5)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    saidas = {"post_1080x1350": post(1350), "post_quadrado": post(1080), "story": story()}
    for n, im in saidas.items():
        im.convert("RGB").save(os.path.join(OUT, n + ".png"))
    f = Image.new("RGB", (400 + 432 + 432 + 40, 720), (255, 255, 255))
    f.paste(saidas["story"].convert("RGB").resize((400, 711)), (0, 0))
    f.paste(saidas["post_1080x1350"].convert("RGB").resize((432, 540)), (420, 0))
    f.paste(saidas["post_quadrado"].convert("RGB").resize((432, 432)), (872, 0))
    f.save(os.path.join(OUT, "previa.jpg"), quality=88)
    print("ok")


if __name__ == "__main__":
    main()
