#!/usr/bin/env python3
"""Story de FELICITAÇÃO do Dia das Crianças (12/out) da Sua Vez, 1080x1920, no visual da loja (o das artes de promoção:
creme com listras laranja, cartão branco do logo, Poppins azul-marinho, laranja da marca).
Histórico: v1 céu azul + meeples desenhados (REJEITADA: "nada a ver com a loja, meeples mal feitos"); v2 com 4 caixas
de jogo em cartões (REJEITADA: "você fez uma imagem promocional, eu quero só o Feliz Dia das Crianças").
Agora: só a mensagem, balões e confete nas cores da marca, dados geométricos limpos e um convite discreto para o site.

    python3 story_criancas.py      # out/story_criancas.png
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter

from promo_3jogos import ORANGE, ORANGE_D, NAVY, GREEN, BLUE, WHITE, BLACK, XB, SB, LOGO, OUT, f, fundo, paste_c, \
    shadowed, text_c

W, H = 1080, 1920
AMARELO = (250, 190, 30)
CORES = [ORANGE, BLUE, GREEN, AMARELO]


def balao(r, cor):
    """Balão liso com brilho, nó e cordinha."""
    w, h = int(r * 2), int(r * 2.4)
    im = Image.new("RGBA", (w + 20, h + 330), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = (w + 20) / 2
    d.ellipse((10, 0, 10 + w, h), fill=cor)
    d.polygon([(cx - 14, h - 6), (cx + 14, h - 6), (cx, h + 16)], fill=cor)
    br = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(br).ellipse((10 + w * 0.2, h * 0.12, 10 + w * 0.42, h * 0.38), fill=(255, 255, 255, 110))
    im.alpha_composite(br.filter(ImageFilter.GaussianBlur(r * 0.05)))
    pts = [(cx + 14 * math.sin(k / 6), h + 16 + k * 5) for k in range(62)]
    d.line(pts, fill=(120, 130, 150), width=3)
    return im


def dado(s, cor, n):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, s - 1, s - 1), radius=s // 5, fill=cor)
    p = {2: [(0.28, 0.28), (0.72, 0.72)], 3: [(0.26, 0.26), (0.5, 0.5), (0.74, 0.74)],
         5: [(0.26, 0.26), (0.74, 0.26), (0.5, 0.5), (0.26, 0.74), (0.74, 0.74)],
         6: [(0.28, 0.22), (0.72, 0.22), (0.28, 0.5), (0.72, 0.5), (0.28, 0.78), (0.72, 0.78)]}[n]
    r = s * 0.085
    for x, y in p:
        d.ellipse((x * s - r, y * s - r, x * s + r, y * s + r), fill=WHITE)
    return im


def confete(img):
    d = ImageDraw.Draw(img)
    rnd = random.Random(12)
    for _ in range(110):
        x, y = rnd.uniform(30, W - 30), rnd.uniform(40, H - 40)
        if 60 < x < 1020 and 560 < y < 1450:  # deixa a mensagem limpa
            continue
        c = rnd.choice(CORES)
        s = rnd.uniform(9, 20)
        if rnd.random() < 0.55:
            d.ellipse((x - s / 2, y - s / 2, x + s / 2, y + s / 2), fill=c)
        else:
            a = rnd.uniform(0, math.pi)
            d.line((x, y, x + s * 1.5 * math.cos(a), y + s * 1.5 * math.sin(a)), fill=c, width=7)


def main():
    img = fundo(W, H)
    confete(img)
    # balões nos cantos de cima (fora da área que o Instagram cobre no topo)
    for x, y, r, c, rot in ((150, 570, 95, BLUE, 8), (285, 500, 80, ORANGE, -4), (800, 500, 80, GREEN, 5),
                            (935, 570, 95, AMARELO, -8)):
        paste_c(img, shadowed(balao(r, c), 10, (4, 10), 0.15), x, y, rot)
    d = ImageDraw.Draw(img)
    lg = Image.open(LOGO).convert("RGBA")
    lw = 300
    lg = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS)
    card = Image.new("RGBA", (lg.width + 40, lg.height + 30), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=26, fill=WHITE)
    card.alpha_composite(lg, (20, 15))
    paste_c(img, shadowed(card, 12, (4, 8), 0.2), W / 2, 330)
    text_c(d, (W / 2, 720), "FELIZ DIA", f(BLACK, 128), NAVY)
    text_c(d, (W / 2, 860), "DAS", f(BLACK, 128), NAVY)
    d.rounded_rectangle((80, 940, W - 80, 1120), radius=48, fill=ORANGE)
    text_c(d, (W / 2, 1035), "CRIANÇAS!", f(BLACK, 136), WHITE)
    text_c(d, (W / 2, 1215), "Pra criança que tem em casa", f(SB, 44), NAVY)
    text_c(d, (W / 2, 1272), "e pra que mora dentro da gente.", f(SB, 44), NAVY)
    text_c(d, (W / 2, 1362), "Hoje o dia é de brincar junto!", f(XB, 50), ORANGE_D)
    for x, y, s, c, n, r in ((250, 1500, 110, BLUE, 5, 14), (430, 1530, 92, GREEN, 3, -10),
                             (650, 1525, 96, AMARELO, 6, 8), (835, 1495, 108, ORANGE, 2, -16)):
        paste_c(img, shadowed(dado(s, c, n), 8, (4, 8), 0.2), x, y, r)
    d = ImageDraw.Draw(img)
    pill = (150, 1620, W - 150, 1700)
    d.rounded_rectangle(pill, radius=40, fill=NAVY)
    text_c(d, (W / 2, 1660), "suavez.acervodejogos.com.br", f(XB, 36), WHITE)
    os.makedirs(OUT, exist_ok=True)
    img.convert("RGB").save(os.path.join(OUT, "story_criancas.png"))
    print("ok")


if __name__ == "__main__":
    main()
