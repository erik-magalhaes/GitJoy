#!/usr/bin/env python3
"""Capa do Reels "TOP 10 ÀS CEGAS — versão Erik" (2/nov/2026, pedido dele: "uma capa legal, no tamanho de Reels").
1080x1920, com tudo o que importa na área da grade do perfil (y 285–1635). Gancho de curiosidade: as caixas do 2º ao
10º à mostra, numeradas, e o Nº 1 escondido ("QUAL FOI O Nº 1 DELE?"), pra pessoa abrir o vídeo. Fundo NOVO (regra:
variar o fundo entre capas): azul-noite com holofote e confete, nada da diagonal com raios das outras capas.

    python3 capa_top10_erik.py   # out/capa_top10_erik.png + out/capa_top10_erik_grade.jpg (recorte 3:4 de conferência)
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

W, H = 1080, 1920
OUT = os.path.join(ROOT, "out")
AS = os.path.join(ROOT, "assets", "top10")
INK = (63, 36, 18)
NOITE = (18, 26, 54)
# o top 10 do Erik (do 2 ao 10; o 1, Flip 7, fica escondido)
TOP = {2: "mlem_space_agency", 3: "marvel_deadpool", 4: "ticket_to_ride", 5: "coup_inquisition",
       6: "zombicide_season_3_rue_morgue", 7: "metro", 8: "paranormal_detectives", 9: "taco_gato", 10: "draftosaurus"}


def fundo():
    img = Image.new("RGBA", (W, H), NOITE + (255,))
    luz = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(luz)
    d.ellipse((90, 120, 990, 1000), fill=(70, 110, 200, 120))     # holofote atrás do título
    d.ellipse((150, 1180, 930, 1900), fill=(244, 136, 37, 70))     # brilho quente atrás do Nº 1
    img.alpha_composite(luz.filter(ImageFilter.GaussianBlur(150)))
    d = ImageDraw.Draw(img)
    rnd = random.Random(11)
    cores = [(255, 199, 31), (244, 136, 37), (28, 124, 150), (250, 250, 250), (219, 39, 119)]
    for _ in range(90):  # confete
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        a, s = rnd.uniform(0, math.pi), rnd.uniform(7, 15)
        c = cores[rnd.randrange(len(cores))]
        pts = [(x + s * math.cos(a + k * math.pi / 2) * (1 if k % 2 else 0.45),
                y + s * math.sin(a + k * math.pi / 2) * (1 if k % 2 else 0.45)) for k in range(4)]
        d.polygon(pts, fill=c + (int(rnd.uniform(110, 210)),))
    return img


def caixa(n, h, larg):
    im = Image.open(os.path.join(AS, n + ".png")).convert("RGBA")
    im = im.crop(im.getbbox())
    s = min(h / im.height, larg / im.width)
    return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)


def numero(n, s=78, cor=(255, 199, 31)):
    im = Image.new("RGBA", (s + 12, s + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((8, 10, s + 8, s + 10), fill=INK)
    d.ellipse((2, 2, s, s), fill=cor, outline=INK, width=6)
    f = E.lilita(int(s * (0.55 if n < 10 else 0.46)))
    d.text((s / 2 + 1, s / 2 + 2), str(n), font=f, fill=INK, anchor="mm")
    return im


def cartao(n):
    cw, ch = 300, 228
    c = E.bloco(cw, ch, (250, 246, 238), raio=26, ow=6, sombra=9).copy()
    bx = caixa(TOP[n], ch - 46, cw - 70)
    c.alpha_composite(bx, (int(cw / 2 - bx.width / 2 + 18), int((ch - 9) / 2 - bx.height / 2)))
    c.alpha_composite(numero(n, 70), (-4, -4))
    return c


def foto_erik(d):
    """Rosto do Erik sorrindo e olhando pra câmera (quadro de 16,0 s do 152424), num círculo com contorno marrom.
    O recorte fica do peito pra cima: a caixa do Flip 7 (o Nº 1) que ele segura NÃO aparece."""
    im = Image.open(os.path.join(ROOT, "assets", "capa", "erik_top10.jpg")).convert("RGB")
    im = im.crop((0, 250, 780, 1030)).resize((d, d), Image.LANCZOS)
    ow, sh = 9, 12
    out = Image.new("RGBA", (d + 2 * ow + sh, d + 2 * ow + sh), (0, 0, 0, 0))
    dr = ImageDraw.Draw(out)
    dr.ellipse((sh, sh, d + 2 * ow + sh, d + 2 * ow + sh), fill=INK)
    dr.ellipse((0, 0, d + 2 * ow, d + 2 * ow), fill=(250, 250, 250))
    m = Image.new("L", (d, d), 0)
    ImageDraw.Draw(m).ellipse((0, 0, d - 1, d - 1), fill=255)
    out.paste(im, (ow, ow), m)
    dr.ellipse((0, 0, d + 2 * ow, d + 2 * ow), outline=INK, width=ow - 2)
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    img = fundo()
    # título
    E.cola(img, E.pilula("SEM SABER O PRÓXIMO JOGO!", 38, (219, 39, 119), (250, 250, 250)), W / 2, 300, -2)
    E.cola(img, foto_erik(360), 225, 528, -4)
    E.cola(img, E.titulo("TOP 10\nÀS CEGAS", 122, (255, 199, 31)), 712, 500, -2)
    E.cola(img, E.pilula("VERSÃO ERIK", 44, (28, 124, 150), (250, 250, 250), fonte_titulo=True), 712, 690, 2)
    # do 2 ao 10, em 3 colunas
    for k, n in enumerate(range(2, 11)):
        col, lin = k % 3, k // 3
        x, y = 195 + col * 345, 855 + lin * 232
        E.cola(img, cartao(n), x, y, (-3, 2, -2)[(col + lin) % 3])
    # o nº 1 escondido
    c1 = E.bloco(760, 180, (255, 199, 31), raio=34, ow=8, sombra=12).copy()
    d = ImageDraw.Draw(c1)
    c1.alpha_composite(numero(1, 116, (250, 250, 250)), (22, 22))
    d.text((165, 68), "QUAL FOI O", font=E.lilita(52), fill=INK, anchor="lm")
    d.text((165, 122), "Nº 1 DELE?", font=E.lilita(70), fill=INK, anchor="lm")
    d.text((675, 86), "?", font=E.lilita(150), fill=(219, 39, 119), anchor="mm", stroke_width=6, stroke_fill=INK)
    E.cola(img, c1, W / 2, 1540, -2)
    lg = E.logo(170)
    img.alpha_composite(lg, (W - lg.width - 36, 46))
    img.convert("RGB").save(os.path.join(OUT, "capa_top10_erik.png"))
    # conferência: o que aparece na grade (3:4 do meio) e em miniatura
    g = img.convert("RGB").crop((0, 240, W, 1680)).resize((360, 480), Image.LANCZOS)
    sh = Image.new("RGB", (540 + 380, 960), (255, 255, 255))
    sh.paste(img.convert("RGB").resize((540, 960), Image.LANCZOS), (0, 0))
    sh.paste(g, (560, 20))
    sh.save(os.path.join(OUT, "capa_top10_erik_grade.jpg"), quality=90)
    print("ok")


if __name__ == "__main__":
    main()
