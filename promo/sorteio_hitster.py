#!/usr/bin/env python3
"""Sorteio do HITSTER (31/out/2026, ideia dele) + bônus para quem alugar.
Formato escolhido por ele: sorteio ABERTO (sem precisar alugar: sorteio que depende de compra precisa de autorização
do governo, Lei 5.768/71) para ganhar alcance/seguidores, e um bônus GARANTIDO separado para quem alugar no período:
+2 dias de jogo. Datas dele: participa até 15/11, resultado 16/11.
Visual: noite de festa do Hitster (fundo preto com ondas de som e círculos de "disco" em rosa/ciano/amarelo, como as
cores do jogo), identidade da Jéssica (Lilita + Figtree, contorno, selos em pílula), caixa OFICIAL da Galápagos.

    python3 sorteio_hitster.py   # out/sorteio/post_1_sorteio.png, post_2_bonus.png, story_sorteio.png, story_bonus.png
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
import estilo as E  # noqa: E402

OUT = os.path.join(ROOT, "out", "sorteio")
CAIXA = os.path.join(REPO, "gravados-reels", "assets", "lista", "hitster.png")
ROSA, CIANO, AMAR, PRETO = (255, 64, 160), (40, 220, 235), (255, 214, 40), (14, 12, 22)
FIM, RESULTADO = "15/11", "16/11"


def fundo(W, H, semente=1):
    """Preto com discos de vinil coloridos desfocados e ondas de som."""
    img = Image.new("RGBA", (W, H), PRETO + (255,))
    luz = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(luz)
    rnd = random.Random(semente)
    for cor, (x, y, r) in zip((ROSA, CIANO, AMAR, ROSA, CIANO),
                              ((0.1, 0.12, 0.38), (0.95, 0.3, 0.4), (0.15, 0.85, 0.3), (0.9, 0.95, 0.35),
                               (0.5, 0.55, 0.22))):
        R = r * W
        d.ellipse((x * W - R, y * H - R, x * W + R, y * H + R), fill=cor + (70,))
    img.alpha_composite(luz.filter(ImageFilter.GaussianBlur(W * 0.12)))
    d = ImageDraw.Draw(img)
    for k in range(60):  # barras de equalizador no pé
        x = k * W / 60
        h = (0.25 + 0.75 * abs(math.sin(k * 0.55 + rnd.random()))) * min(H * 0.07, 60)
        cor = (ROSA, CIANO, AMAR)[k % 3]
        d.rounded_rectangle((x + 3, H - h - 10, x + W / 60 - 3, H - 10), radius=4, fill=cor + (150,))
    return img


def disco(r):
    """Disco de vinil com o selo no meio (cara de música, tema do Hitster)."""
    im = Image.new("RGBA", (2 * r + 10, 2 * r + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = r + 5
    d.ellipse((5, 5, 2 * r + 5, 2 * r + 5), fill=(22, 20, 28), outline=E.MARROM, width=6)
    for k in range(6, r - r // 3, 9):
        d.ellipse((c - r + k, c - r + k, c + r - k, c + r - k), outline=(40, 38, 50), width=2)
    rs = r // 3
    d.ellipse((c - rs, c - rs, c + rs, c + rs), fill=ROSA)
    d.ellipse((c - 8, c - 8, c + 8, c + 8), fill=PRETO)
    return im


def passo(n, txt, w, cor):
    im = E.bloco(w, 120, E.BRANCO, raio=30, ow=6, sombra=9).copy()
    d = ImageDraw.Draw(im)
    d.ellipse((18, 18, 102, 102), fill=cor, outline=E.MARROM, width=5)
    d.text((60, 62), str(n), font=E.lilita(56), fill=E.BRANCO, anchor="mm")
    d.text((128, 62), txt, font=E.fig(40, 800), fill=E.MARROM, anchor="lm")
    return im


def peca_sorteio(W, H):
    img = fundo(W, H)
    alto = H > 1500
    # (pílula, título, caixa, 1º passo, data) — o post 4:5 é mais apertado que o story
    y = dict(pil=200, tit=410, cx=920, ps=1300, dt=1730, fs=1810) if alto else \
        dict(pil=60, tit=230, cx=565, ps=830, dt=1195, fs=1255)
    E.cola(img, E.pilula("SORTEIO", 52, AMAR, E.MARROM, fonte_titulo=True), W / 2, y["pil"], -3)
    E.cola(img, E.titulo("VALENDO UM\nHITSTER!", 128 if alto else 112, E.BRANCO), W / 2, y["tit"], -2)
    E.cola(img, disco(250 if alto else 190), W / 2 + 140, y["cx"] - 20, 0)
    E.cola(img, E.jogo(CAIXA, 520 if alto else 380), W / 2 - 80, y["cx"], -6)
    for k, (t, c) in enumerate((("Siga a @suavez_bg", ROSA), ("Curta este post", CIANO),
                                ("Marque 2 amigos nos comentários", AMAR))):
        E.cola(img, passo(k + 1, t, 860, c), W / 2, y["ps"] + k * (140 if alto else 120), (k - 1) * 0.8)
    E.cola(img, E.pilula(f"PARTICIPE ATÉ {FIM} · RESULTADO DIA {RESULTADO}", 34, ROSA, E.BRANCO), W / 2, y["dt"], 1)
    E.cola(img, E.texto("Esta promoção não é patrocinada nem administrada pelo Instagram.", 24, (230, 230, 240), 600),
           W / 2, y["fs"])
    img.alpha_composite(E.logo(190), (W - 228, 30))
    return img


def peca_bonus(W, H):
    img = fundo(W, H, 2)
    alto = H > 1500
    y0 = 230 if alto else 120
    E.cola(img, E.pilula("E TEM MAIS!", 50, CIANO, E.MARROM, fonte_titulo=True), W / 2, y0, 3)
    E.cola(img, E.titulo("ALUGOU ATÉ\n" + FIM + "?", 130, E.BRANCO), W / 2, y0 + 220, -2)
    yc = y0 + (640 if alto else 600)
    E.cola(img, E.titulo("+2", 330, AMAR), W / 2, yc, -4)
    E.cola(img, E.titulo("DIAS DE JOGO", 110, ROSA), W / 2, yc + 230, 2)
    E.cola(img, E.texto("de presente, em qualquer jogo do acervo.", 40, E.BRANCO, 700), W / 2, yc + 360)
    E.cola(img, E.pilula("RESERVE PELO LINK NA BIO", 44, AMAR, E.MARROM), W / 2, yc + (520 if alto else 480), -1)
    img.alpha_composite(E.logo(190), (W - 228, 30))
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    peca_sorteio(1080, 1350).convert("RGB").save(os.path.join(OUT, "post_1_sorteio.png"))
    peca_bonus(1080, 1350).convert("RGB").save(os.path.join(OUT, "post_2_bonus.png"))
    peca_sorteio(1080, 1920).convert("RGB").save(os.path.join(OUT, "story_sorteio.png"))
    peca_bonus(1080, 1920).convert("RGB").save(os.path.join(OUT, "story_bonus.png"))
    ims = [Image.open(os.path.join(OUT, n)) for n in ("post_1_sorteio.png", "post_2_bonus.png", "story_sorteio.png",
                                                      "story_bonus.png")]
    sh = Image.new("RGB", (4 * 420 + 10, 760), (255, 255, 255))
    for k, im in enumerate(ims):
        im = im.copy()
        im.thumbnail((410, 740))
        sh.paste(im, (10 + k * 420, 10))
    sh.save(os.path.join(ROOT, "out", "sorteio_previa.jpg"), quality=90)
    print("ok")


if __name__ == "__main__":
    main()
