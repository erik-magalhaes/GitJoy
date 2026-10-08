#!/usr/bin/env python3
"""Reels "BYE BYE..." para a trend com a música American Pie ("bye, bye, Miss American Pie").
Visual retrô anos 70 (a música é de 1971): raios de sol laranja/mostarda/marrom, letras com sombra 3D e
polaroides que dão tchau e voam para fora. Cada "BYE BYE" é uma coisa chata de que a pessoa se despede;
no fim, "OI, SUA VEZ!". SEM narração e SEM a música (o dono põe o áudio da trend no Instagram).

    python3 byebye.py --teste      # out/teste_byebye.jpg
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
HOBBY = os.path.join(REPO, "hobby-reels", "assets")
FN = os.path.join(HOBBY, "fonts")
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
LOGO = os.path.join(HOBBY, "logo_suavez.png")
W, H = 1080, 1920
CREME = (250, 238, 212)
MARROM = (92, 46, 26)
LARANJA = (228, 112, 38)
MOSTARDA = (236, 172, 52)
VERMELHO = (196, 66, 46)

# (texto do adeus, emoji ou caixa do acervo para a polaroide)
ADEUS = [
    ("domingo rolando\no celular", "📱"),
    ("pagar R$ 400 num jogo\nque você jogou 1 vez", "💸"),
    ("aquele jogo que\nnunca acaba", "⏳"),
    ("estante cheia de\ncaixa parada", "📦"),
    ("\"não tem nada\npra fazer hoje\"", "🥱"),
    ("rolê caro no\nshopping", "🛍️"),
]


def font(n, s):
    return ImageFont.truetype(os.path.join(FN, n), int(s))


def emoji(ch, size):
    f = ImageFont.truetype(EMOJI, 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    return im.resize((size, int(im.height * size / im.width)), Image.LANCZOS)


def caixa(nome, h):
    p = os.path.join(HOBBY, "caixas", nome + ".png")
    if not os.path.exists(p):
        p = os.path.join(HOBBY, "acervo", nome + ".png")
    im = Image.open(p).convert("RGBA")
    return im.resize((int(im.width * h / im.height), int(h)), Image.LANCZOS)


def fundo(t=0.0):
    """Raios de sol retrô saindo de baixo, girando bem devagar."""
    img = Image.new("RGBA", (W, H), CREME + (255,))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    cx, cy, n = 540, 2050, 24
    cores = [LARANJA, MOSTARDA, VERMELHO, MOSTARDA]
    for i in range(n):
        a0 = math.pi + i * math.pi / n + math.sin(t * 0.3) * 0.02
        a1 = a0 + math.pi / n * 0.5
        d.polygon([(cx, cy), (cx + 3000 * math.cos(a0), cy + 3000 * math.sin(a0)),
                   (cx + 3000 * math.cos(a1), cy + 3000 * math.sin(a1))], fill=cores[i % 4] + (60,))
    img.alpha_composite(ov)
    d = ImageDraw.Draw(img)
    # sol de listras no rodapé (metade escondida embaixo da tela)
    for k, c in enumerate((MOSTARDA, LARANJA, VERMELHO, MARROM)):
        r = 460 - k * 95
        d.ellipse((cx - r, cy - r - 60, cx + r, cy + r - 60), fill=c)
    return img


def retro(txt, size, cor=CREME, sombra=MARROM, prof=12, fonte="AlfaSlabOne-Regular.ttf", contorno=MARROM):
    """Letreiro anos 70: texto com sombra 3D em degraus e contorno."""
    f = font(fonte, size)
    linhas = txt.split("\n")
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    lw = max(tmp.textlength(l, font=f) for l in linhas)
    lh = size * 1.12
    im = Image.new("RGBA", (int(lw + prof * 2 + 40), int(lh * len(linhas) + prof * 2 + 40)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k, l in enumerate(linhas):
        x, y = im.width / 2 - prof / 2, 20 + k * lh + size * 0.55
        for s in range(prof, 0, -1):
            d.text((x + s, y + s), l, font=f, fill=sombra, anchor="mm", stroke_width=4, stroke_fill=sombra)
        d.text((x, y), l, font=f, fill=cor, anchor="mm", stroke_width=4, stroke_fill=contorno)
    return im


def polaroide(conteudo, rot=0.0, w=620):
    """Polaroide com a 'foto' (fundo colorido + emoji ou caixa) e sombra."""
    hh = int(w * 1.18)
    p = Image.new("RGBA", (w, hh), (255, 253, 247, 255))
    foto_w = w - 60
    cor = [(110, 170, 200), (240, 190, 120), (170, 120, 190), (130, 180, 120)][hash(conteudo) % 4]
    foto = Image.new("RGBA", (foto_w, foto_w), cor + (255,))
    if conteudo.startswith("caixa:"):
        cx = caixa(conteudo[6:], int(foto_w * 0.78))
    else:
        cx = emoji(conteudo, int(foto_w * 0.6))
    foto.alpha_composite(cx, (foto_w // 2 - cx.width // 2, foto_w // 2 - cx.height // 2))
    p.alpha_composite(foto, (30, 30))
    pad = 40
    out = Image.new("RGBA", (w + pad * 2, hh + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", (w, hh), (60, 30, 10, 120))
    out.alpha_composite(sh, (pad + 10, pad + 18))
    out = out.filter(ImageFilter.GaussianBlur(14))
    out.alpha_composite(p, (pad, pad))
    return out.rotate(rot, expand=True, resample=Image.BICUBIC)


def logo(img, w=170):
    lg = Image.open(LOGO).convert("RGBA")
    lg = lg.resize((w, int(lg.height * w / lg.width)), Image.LANCZOS)
    card = Image.new("RGBA", (lg.width + 24, lg.height + 20), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=16, fill=(255, 255, 255))
    card.alpha_composite(lg, (12, 10))
    img.alpha_composite(card, (W - card.width - 30, 40))


def cola(img, im, x, y):
    img.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))


def quadro_adeus(k):
    txt, cont = ADEUS[k]
    img = fundo(k)
    cola(img, retro("BYE BYE,", 150, CREME, MARROM, 14), 540, 300)
    cola(img, polaroide(cont, -5 if k % 2 else 5), 540, 860)
    cola(img, emoji("👋", 170), 850, 560)
    d = ImageDraw.Draw(img)
    f = font("Poppins-Black.ttf", 64)
    d.rounded_rectangle((90, 1300, 990, 1510), radius=36, fill=CREME, outline=MARROM, width=6)
    for i, l in enumerate(txt.split("\n")):
        d.text((540, 1362 + i * 84), l, font=f, fill=MARROM, anchor="mm")
    logo(img)
    return img


def quadro_oi():
    img = fundo(9)
    cola(img, retro("OI,", 170, MOSTARDA, MARROM, 14), 540, 280)
    cola(img, retro("SUA VEZ!", 160, CREME, MARROM, 14), 540, 460)
    nomes = ["dixit", "king_of_tokyo", "ticket_to_ride", "camel_up_second_edition", "wingspan", "root", "santorini"]
    for i, n in enumerate(nomes):
        cx = caixa(n, 300).rotate((i - 3) * 7, expand=True, resample=Image.BICUBIC)
        x = 540 + (i - 3) * 120
        y = 930 + abs(i - 3) * 30
        cola(img, cx, x, y)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((110, 1210, 970, 1390), radius=40, fill=MARROM)
    d.text((540, 1262), "+160 JOGOS PRA ALUGAR", font=font("Poppins-Black.ttf", 54), fill=CREME, anchor="mm")
    d.text((540, 1340), "5 dias a partir de R$ 15", font=font("Poppins-ExtraBold.ttf", 50), fill=MOSTARDA, anchor="mm")
    return img


if __name__ == "__main__":
    ims = [quadro_adeus(0), quadro_adeus(1), quadro_oi()]
    sheet = Image.new("RGB", (3 * 540 + 40, 980), (20, 20, 20))
    for k, im in enumerate(ims):
        sheet.paste(im.convert("RGB").resize((540, 960), Image.LANCZOS), (10 + k * 550, 10))
    sheet.save(os.path.join(ROOT, "out", "teste_byebye.jpg"), quality=90)
    print("ok")
