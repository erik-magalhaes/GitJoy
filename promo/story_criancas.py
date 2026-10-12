#!/usr/bin/env python3
"""Story do Dia das Crianças (12/out) da Sua Vez, 1080x1920. Visual próprio (a capa do Reels já usou raios): céu azul
com nuvens e confete, uma turma de meeples coloridos pulando (desenhados em vetor, com contorno de adesivo), dados no ar,
"FELIZ DIA DAS CRIANÇAS!" em letras coloridas. Sem caixa de jogo (é um post de felicitação). Tudo fora das áreas que o
Instagram cobre no story (topo ~250 px e base ~300 px).

    python3 story_criancas.py      # out/story_criancas.jpg
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "comum"))
sys.path.insert(0, os.path.join(REPO, "gravados-reels"))
from motor import W, H, WHITE, font, logo_card, cola, sombra, letreiro, pilula  # noqa: E402
from capa_criancas import CORES, INK, adesivo, titulo_colorido, estrela  # noqa: E402

OUT = os.path.join(ROOT, "out")


def ceu():
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    a, b = (90, 190, 255), (200, 236, 255)
    for y in range(H):
        u = y / H
        d.line((0, y, W, y), fill=tuple(int(a[i] + (b[i] - a[i]) * u) for i in range(3)))
    nuv = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dn = ImageDraw.Draw(nuv)
    for cx, cy, s in ((150, 420, 1.0), (930, 330, 0.8), (880, 1180, 0.9), (120, 1060, 0.7)):
        for dx, dy, r in ((-90, 20, 70), (-20, -20, 95), (70, 10, 75), (0, 40, 80)):
            dn.ellipse((cx + dx * s - r * s, cy + dy * s - r * s, cx + dx * s + r * s, cy + dy * s + r * s),
                       fill=(255, 255, 255, 235))
    img.alpha_composite(nuv.filter(ImageFilter.GaussianBlur(2)))
    rnd = random.Random(12)
    d = ImageDraw.Draw(img)
    for _ in range(150):  # confete e serpentina
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        if 80 < x < 1000 and 480 < y < 1130:
            continue
        c = rnd.choice(CORES + [WHITE])
        s = rnd.uniform(10, 24)
        if rnd.random() < 0.5:
            d.ellipse((x - s / 2, y - s / 2, x + s / 2, y + s / 2), fill=c)
        else:
            a0 = rnd.uniform(0, math.pi)
            d.line((x, y, x + s * 1.6 * math.cos(a0), y + s * 1.6 * math.sin(a0)), fill=c, width=7)
    return img


def meeple(h, cor):
    """Meeple clássico: cabeça redonda, braços abertos, pernas afastadas."""
    s = h / 100
    m = Image.new("L", (int(110 * s), int(104 * s)), 0)
    d = ImageDraw.Draw(m)
    ox = 5 * s
    d.ellipse((ox + 34 * s, 0, ox + 66 * s, 32 * s), fill=255)
    d.polygon([(ox + 50 * s, 22 * s), (ox + 98 * s, 40 * s), (ox + 100 * s, 54 * s), (ox + 70 * s, 56 * s),
               (ox + 92 * s, 100 * s), (ox + 58 * s, 100 * s), (ox + 50 * s, 82 * s), (ox + 42 * s, 100 * s),
               (ox + 8 * s, 100 * s), (ox + 30 * s, 56 * s), (ox + 0, 54 * s), (ox + 2 * s, 40 * s)], fill=255)
    m = m.filter(ImageFilter.MaxFilter(int(7 * s) | 1)).filter(ImageFilter.MinFilter(int(7 * s) | 1))
    m = m.filter(ImageFilter.GaussianBlur(1.2 * s)).point(lambda v: 255 if v > 128 else 0)
    im = Image.new("RGBA", m.size, cor + (255,))
    # luz de cima: um pouco mais claro no topo
    lz = Image.new("RGBA", m.size, (255, 255, 255, 0))
    ImageDraw.Draw(lz).ellipse((-m.width * 0.2, -m.height * 0.6, m.width * 1.2, m.height * 0.45), fill=(255, 255, 255, 60))
    im.alpha_composite(lz.filter(ImageFilter.GaussianBlur(10 * s)))
    # olhinhos e sorriso
    dd = ImageDraw.Draw(im)
    for ex in (44, 56):
        dd.ellipse((ox + (ex - 2.6) * s, 12 * s, ox + (ex + 2.6) * s, 19 * s), fill=INK)
    dd.arc((ox + 42 * s, 15 * s, ox + 58 * s, 27 * s), 20, 160, fill=INK, width=max(2, int(2.2 * s)))
    im.putalpha(m)
    return im


def dado(s, cor, n):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, s - 1, s - 1), radius=s // 5, fill=cor)
    p = {1: [(0.5, 0.5)], 2: [(0.27, 0.27), (0.73, 0.73)], 3: [(0.25, 0.25), (0.5, 0.5), (0.75, 0.75)],
         4: [(0.27, 0.27), (0.73, 0.27), (0.27, 0.73), (0.73, 0.73)],
         5: [(0.25, 0.25), (0.75, 0.25), (0.5, 0.5), (0.25, 0.75), (0.75, 0.75)],
         6: [(0.27, 0.22), (0.73, 0.22), (0.27, 0.5), (0.73, 0.5), (0.27, 0.78), (0.73, 0.78)]}[n]
    r = s * 0.085
    for x, y in p:
        d.ellipse((x * s - r, y * s - r, x * s + r, y * s + r), fill=WHITE)
    return im


def main():
    os.makedirs(OUT, exist_ok=True)
    img = ceu()
    cola(img, logo_card(300), 540, 330, -2)
    cola(img, titulo_colorido("FELIZ DIA", 150), 540, 600, -3)
    cola(img, titulo_colorido("DAS", 150), 540, 765, 2)
    cola(img, titulo_colorido("CRIANÇAS!", 150), 540, 930, -2)
    cola(img, letreiro("pra criança de todas as idades!", 54, WHITE, INK, 10, "Poppins-Black.ttf"), 540, 1080, 1)
    # a turma de meeples pulando (os do meio mais altos), com dados no ar
    turma = [(130, 1490, 190, 0, -10, 0), (300, 1440, 230, 4, 6, -40), (540, 1420, 270, 2, -4, -70),
             (780, 1440, 230, 3, 8, -40), (950, 1490, 190, 5, -6, 0)]
    for x, y, h, ci, rot, pulo in turma:
        cola(img, adesivo(meeple(h, CORES[ci]), 8), x, y + pulo, rot)
    for x, y, s, c, n, r in ((130, 1265, 92, CORES[0], 5, 18), (950, 1265, 84, CORES[3], 3, -20),
                             (690, 1200, 70, CORES[5], 6, 30), (390, 1205, 64, CORES[1], 2, -12)):
        cola(img, adesivo(dado(s, c, n), 6), x, y, r)
    for x, y, s, c in ((95, 560, 70, CORES[2]), (990, 600, 60, CORES[0]), (980, 870, 46, CORES[4]), (90, 900, 50, CORES[5])):
        cola(img, estrela(s, c), x, y, 10)
    cola(img, pilula("BORA JOGAR EM FAMÍLIA? · LINK NA BIO", 40, INK, WHITE, WHITE, bw=5), 540, 1650, 0)
    img.convert("RGB").save(os.path.join(OUT, "story_criancas.jpg"), quality=94)
    print("ok")


if __name__ == "__main__":
    main()
