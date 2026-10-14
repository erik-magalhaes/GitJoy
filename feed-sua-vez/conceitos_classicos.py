#!/usr/bin/env python3
"""3 visuais para o NOVO comparativo antigo × moderno (14/out/2026), com o mesmo par de exemplo (Ludo → Camel Up):
1 "EVOLUIU!" (tela de evolução de videogame), 2 "DEU MATCH" (tela de app de namoro), 3 TV antiga × HD.
Os comparativos anteriores (feed-posts/carrosseis*.py: creme+círculo e antes×depois em papel envelhecido) não se repetem.
Clássicos: fotos da Ri Happy (VTEX, fundo branco); modernos: fotos do site da Sua Vez (fundo laranja).

    python3 conceitos_classicos.py    # out/conceitos_classicos.jpg
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
sys.path.insert(0, ROOT)
from estilo import MARROM, PETROLEO, LARANJA, AMARELO, BRANCO, titulo, texto, bloco, pilula, logo, cola, lilita  # noqa
from semana import produto  # noqa: E402
from como_alugar import ficha_foto  # noqa: E402

W, H = 1080, 1350
CL = os.path.join(ROOT, "assets", "classicos", "orig")
SITE = os.path.join(REPO, "hobby-reels", "assets", "acervo_foto")
ANTIGO, MODERNO = "LUDO", "CAMEL UP"
FOTO_ANT = os.path.join(CL, "ludo2.jpg")
FOTO_MOD = os.path.join(SITE, "camel_up_second_edition.jpg")
FRASE = "Corrida com dados, mas os camelos se EMPILHAM e você aposta em quem vai ganhar."


def caixa_antiga(larg, velha=False):
    obj, _ = produto(FOTO_ANT)
    obj = obj.crop(obj.getchannel("A").getbbox())
    s = larg / obj.width
    obj = obj.resize((round(obj.width * s), round(obj.height * s)), Image.LANCZOS)
    if velha:
        a = obj.getchannel("A")
        rgb = ImageEnhance.Color(obj.convert("RGB")).enhance(0.25)
        rgb = Image.blend(rgb, Image.new("RGB", rgb.size, (180, 140, 90)), 0.25)
        obj = rgb.convert("RGBA")
        obj.putalpha(a)
    return obj


def raios(img, cx, cy, cor, n=18, alpha=70):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for k in range(n):
        a0 = k * 2 * math.pi / n
        a1 = a0 + math.pi / n
        d.polygon([(cx, cy), (cx + 2000 * math.cos(a0), cy + 2000 * math.sin(a0)),
                   (cx + 2000 * math.cos(a1), cy + 2000 * math.sin(a1))], fill=cor + (alpha,))
    img.alpha_composite(lay)


def silhueta(im, cor=(255, 255, 255)):
    s = Image.new("RGBA", im.size, cor + (255,))
    s.putalpha(im.getchannel("A"))
    return s


def opcao_1():
    """EVOLUIU!: fundo azul com raios, clássico vira silhueta branca e 'evolui' para o moderno."""
    img = Image.new("RGBA", (W, H), (24, 70, 128, 255))
    raios(img, W / 2, 760, (255, 255, 255), 20, 40)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((W / 2 - 420, 760 - 420, W / 2 + 420, 760 + 420), fill=(255, 255, 220, 120))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(90)))
    cola(img, titulo("O QUÊ?!", 90, AMARELO), W / 2, 95, -3)
    cola(img, texto(f"Seu {ANTIGO} está evoluindo!", 46, BRANCO, 900), W / 2, 185)
    ant = caixa_antiga(300)
    cola(img, ant, 190, 470, -8)
    cola(img, silhueta(ant), 190 + 30, 470 + 18, -8, 1, 0.35)
    for k, x in enumerate((360, 420, 480)):
        cola(img, titulo("›", 120, BRANCO, sw=6, sombra=6), x, 470, 0, 1, 0.5 + 0.25 * k)
    cola(img, ficha_foto(FOTO_MOD, 560), W / 2 + 120, 760, 4)
    cola(img, pilula("EVOLUIU!", 64, AMARELO, MARROM, pad=(40, 14), fonte_titulo=True), W / 2 + 120, 1080, -3)
    cola(img, texto(f"{ANTIGO} evoluiu para {MODERNO}!", 44, BRANCO, 900), W / 2, 1175)
    cola(img, texto(FRASE, 32, (210, 230, 250), 700, larg_max=900), W / 2, 1255)
    return img


def opcao_2():
    """DEU MATCH: tela de app de namoro, as duas caixas em círculos se encontrando."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    yy = np.linspace(0, 1, H)[:, None, None]
    grad = (np.array([253, 89, 120]) * (1 - yy) + np.array([255, 160, 70]) * yy) * np.ones((1, W, 1))
    img = Image.fromarray(grad.astype(np.uint8), "RGB").convert("RGBA")
    cola(img, texto(f"Você curtia {ANTIGO}?", 50, BRANCO, 900), W / 2, 110)
    cola(img, titulo("DEU MATCH!", 140, BRANCO, contorno=(150, 20, 60)), W / 2, 260, -4)

    def circulo(foto_img, lado):
        m = Image.new("L", (lado, lado), 0)
        ImageDraw.Draw(m).ellipse((0, 0, lado - 1, lado - 1), fill=255)
        c = Image.new("RGBA", (lado + 24, lado + 24), (0, 0, 0, 0))
        ImageDraw.Draw(c).ellipse((0, 0, lado + 23, lado + 23), fill=BRANCO)
        fi = ImageOps.fit(foto_img.convert("RGBA"), (lado, lado), Image.LANCZOS)
        fi.putalpha(m)
        c.alpha_composite(fi, (12, 12))
        return c
    fundo_branco = Image.new("RGBA", (900, 900), (250, 250, 250, 255))
    ant = caixa_antiga(700)
    fundo_branco.alpha_composite(ant, ((900 - ant.width) // 2, (900 - ant.height) // 2))
    cola(img, circulo(fundo_branco, 380), 330, 620, -6)
    cola(img, circulo(Image.open(FOTO_MOD), 420), 740, 650, 6)
    cora = Image.new("RGBA", (170, 160), (0, 0, 0, 0))
    d = ImageDraw.Draw(cora)
    d.ellipse((5, 5, 85, 85), fill=(255, 255, 255))
    d.ellipse((85, 5, 165, 85), fill=(255, 255, 255))
    d.polygon([(10, 60), (160, 60), (85, 155)], fill=(255, 255, 255))
    cola(img, cora, W / 2, 870, 0)
    cola(img, texto(f"Vai amar {MODERNO.title()}", 56, BRANCO, 900), W / 2, 1010)
    cola(img, texto(FRASE, 36, BRANCO, 700, larg_max=880), W / 2, 1120)
    cola(img, pilula("MANDAR MENSAGEM", 40, BRANCO, (230, 70, 110), pad=(40, 16)), W / 2, 1255)
    return img


def opcao_3():
    """TV antiga × HD: em cima, TV de tubo com o clássico desbotado; embaixo, o moderno nítido."""
    img = Image.new("RGBA", (W, H), (34, 28, 26, 255))
    tv = bloco(600, 470, (120, 86, 56), raio=40, ow=8, sombra=12)
    d = ImageDraw.Draw(tv)
    d.rounded_rectangle((36, 36, 470, 434), radius=60, fill=(40, 44, 40), outline=MARROM, width=6)
    tela = Image.new("RGBA", (420, 380), (200, 190, 170, 255))
    ant = caixa_antiga(330, velha=True)
    tela.alpha_composite(ant, ((420 - ant.width) // 2, (380 - ant.height) // 2))
    dt = ImageDraw.Draw(tela)
    for y in range(0, 380, 6):
        dt.line((0, y, 420, y), fill=(0, 0, 0, 40), width=2)
    m = Image.new("L", tela.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, 419, 379), radius=55, fill=255)
    tv.paste(tela, (43, 45), m)
    for k in range(2):
        d.ellipse((500, 90 + k * 110, 570, 160 + k * 110), fill=(60, 44, 30), outline=MARROM, width=5)
    for k in range(5):
        d.line((495, 340 + k * 16, 575, 340 + k * 16), fill=MARROM, width=5)
    cola(img, tv, 400, 330, -3)
    cola(img, pilula("ANTES", 40, (190, 180, 160), MARROM, pad=(26, 10), fonte_titulo=True), 870, 190, 5)
    cola(img, texto(ANTIGO, 54, (220, 205, 180), 900), 870, 290)
    cola(img, pilula("AGORA EM HD", 48, AMARELO, MARROM, pad=(30, 12), fonte_titulo=True), 300, 700, -3)
    cola(img, ficha_foto(FOTO_MOD, 470), 700, 880, 3)
    cola(img, titulo(MODERNO, 80, LARANJA), 250, 860, -3)
    cola(img, texto(FRASE, 38, BRANCO, 700, larg_max=900), W / 2, 1210)
    return img


def main():
    ops = [opcao_1(), opcao_2(), opcao_3()]
    folha = Image.new("RGB", (3 * 540 + 40, 675 + 90), (255, 255, 255))
    d = ImageDraw.Draw(folha)
    for k, im in enumerate(ops):
        folha.paste(im.convert("RGB").resize((540, 675), Image.LANCZOS), (10 + k * 550, 80))
        d.text((10 + k * 550 + 270, 40), ("1 · EVOLUIU!", "2 · DEU MATCH", "3 · TV ANTIGA × HD")[k], font=lilita(40),
               fill=MARROM, anchor="mm")
    folha.save(os.path.join(ROOT, "out", "conceitos_classicos.jpg"), quality=90)
    print("ok")


if __name__ == "__main__":
    main()
