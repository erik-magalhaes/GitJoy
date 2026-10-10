#!/usr/bin/env python3
"""Capa do Reels "jogos para crianças" (1080x1920): raios coloridos com confete, as 4 caixas OFICIAIS em destaque (ele pediu
para tirar a foto dele e deixar só os jogos), "INDICAÇÃO PRO DIA DAS CRIANÇAS / 4 JOGOS PRA JOGAR COM AS CRIANÇAS!" em letras coloridas, logo da
Sua Vez e as 4 caixas OFICIAIS. Título e logo ficam dentro da área 4:5 do meio (y 285–1635), que é o que aparece na
grade do perfil.

    python3 capa_criancas.py      # out/capa_criancas.jpg (+ out/capa_criancas_grade.jpg, prévia do corte 4:5)
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "..", "comum"))
from motor import W, H, WHITE, font, logo_card, cola, sombra, letreiro, pilula  # noqa: E402

OUT = os.path.join(ROOT, "out")
OF = os.path.join(ROOT, "assets", "oficial")
INK = (30, 20, 60)
CORES = [(255, 72, 120), (255, 160, 0), (255, 214, 0), (60, 200, 90), (0, 170, 255), (140, 90, 255)]


def fundo():
    img = Image.new("RGBA", (W, H), (255, 214, 0, 255))
    d = ImageDraw.Draw(img)
    cx, cy, r, n = 540, 980, 2400, 24
    for j in range(n):
        a0, a1 = j * math.tau / n, (j + 1) * math.tau / n
        c = CORES[j % len(CORES)]
        d.polygon([(cx, cy), (cx + r * math.cos(a0), cy + r * math.sin(a0)), (cx + r * math.cos(a1), cy + r * math.sin(a1))],
                  fill=c)
    # clarão no meio para ele destacar e degradê leve nas bordas
    luz = Image.new("L", (W, H), 0)
    ImageDraw.Draw(luz).ellipse((cx - 520, cy - 560, cx + 520, cy + 560), fill=200)
    luz = luz.filter(ImageFilter.GaussianBlur(160))
    img = Image.composite(Image.new("RGBA", (W, H), (255, 250, 235, 255)), img, luz)
    rnd = random.Random(7)
    d = ImageDraw.Draw(img)
    for _ in range(140):  # confete
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        if 200 < x < 880 and 700 < y < 1500:
            continue
        c = rnd.choice(CORES + [WHITE])
        s = rnd.uniform(10, 26)
        if rnd.random() < 0.5:
            d.ellipse((x - s / 2, y - s / 2, x + s / 2, y + s / 2), fill=c)
        else:
            a = rnd.uniform(0, math.pi)
            pts = [(x + s * math.cos(a + k * math.pi / 2) * (1 if k % 2 == 0 else 0.4),
                    y + s * math.sin(a + k * math.pi / 2) * (1 if k % 2 == 0 else 0.4)) for k in range(4)]
            d.polygon(pts, fill=c)
    return img


def estrela(s, cor):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    pts = []
    for k in range(10):
        r = s / 2 if k % 2 == 0 else s / 4.6
        a = -math.pi / 2 + k * math.pi / 5
        pts.append((s / 2 + r * math.cos(a), s / 2 + r * math.sin(a)))
    d = ImageDraw.Draw(im)
    d.polygon(pts, fill=cor, outline=WHITE, width=max(3, s // 14))
    return im


def adesivo(im, borda=16):
    """Contorno branco grosso em volta do recorte (efeito adesivo) + sombra."""
    a = im.getchannel("A")
    grande = a.filter(ImageFilter.MaxFilter(borda * 2 + 1)).filter(ImageFilter.GaussianBlur(1.5))
    out = Image.new("RGBA", im.size, (255, 255, 255, 0))
    out.putalpha(grande)
    out.alpha_composite(im)
    return sombra(out, 20, (0, 18), 0.35)


def titulo_colorido(txt, size):
    """Cada letra de uma cor, com contorno escuro e leve sobe-desce."""
    ims = [letreiro(ch, size, CORES[k % len(CORES)], INK, 14, sombra_px=8, cor_sombra=INK) if ch != " " else None
           for k, ch in enumerate(txt)]
    f = font("Bungee-Regular.ttf", size)
    larg = [f.getlength(ch) for ch in txt]
    tot = sum(larg) + 4 * (len(txt) - 1)
    out = Image.new("RGBA", (int(tot + 120), int(size * 1.9)), (0, 0, 0, 0))
    x = 60
    for k, (im, w) in enumerate(zip(ims, larg)):
        if im is not None:
            dy = 10 * math.sin(k * 1.3)
            r = im.rotate(6 * math.sin(k * 2.1), expand=True, resample=Image.BICUBIC)
            out.alpha_composite(r, (int(x + w / 2 - r.width / 2), int(out.height / 2 - r.height / 2 + dy)))
        x += w + 4
    return out


def caixa(nome, h):
    im = Image.open(os.path.join(OF, nome)).convert("RGBA")
    im = im.crop(im.getbbox())
    im = im.resize((int(im.width * h / im.height), int(h)), Image.LANCZOS)
    if nome == "scooby_doo.png":  # capa reta: cantinho arredondado
        m = Image.new("L", im.size, 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=im.width // 30, fill=255)
        im.putalpha(m)
    return adesivo(im, 7)


def main():
    os.makedirs(OUT, exist_ok=True)
    img = fundo()
    for x, y, s_, c in ((95, 1000, 90, CORES[0]), (990, 980, 80, CORES[4]), (90, 1700, 100, CORES[3]),
                        (990, 1690, 110, CORES[5]), (540, 1290, 70, CORES[2])):
        cola(img, estrela(s_, c), x, y, 0)
    # título e logo (área segura 4:5)
    cola(img, logo_card(250), 540, 368, -2)
    cola(img, pilula("INDICAÇÃO PRO DIA DAS CRIANÇAS", 40, (255, 72, 120), WHITE, WHITE, bw=6), 540, 500, -2)
    cola(img, titulo_colorido("4 JOGOS", 180), 540, 630, -3)
    cola(img, letreiro("PRA JOGAR COM\nAS CRIANÇAS!", 78, WHITE, INK, 13, sombra_px=7, cor_sombra=INK), 540, 808, 2)
    # as 4 caixas oficiais em destaque (2 x 2), tudo dentro da área que aparece na grade
    caixas = [("go_cuckoo.png", 350, -6, 300, 1100), ("draftosaurus.png", 315, 5, 765, 1100),
              ("gravity_superstar.png", 315, -4, 300, 1450), ("scooby_doo.png", 315, 6, 770, 1450)]
    for n, h, rot, x, y in caixas:
        cola(img, caixa(n, h), x, y, rot)
    cola(img, pilula("@SUAVEZ_BG", 38, INK, WHITE, WHITE), 540, 1840, 0)
    rgb = img.convert("RGB")
    rgb.save(os.path.join(OUT, "capa_criancas.jpg"), quality=95)
    rgb.crop((0, 285, 1080, 1635)).save(os.path.join(OUT, "capa_criancas_grade.jpg"), quality=90)
    print("ok")


if __name__ == "__main__":
    main()
