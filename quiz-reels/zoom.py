#!/usr/bin/env python3
"""Reels "Adivinha o jogo pelo zoom": SEM narração, só texto na tela, para o dono pôr a MÚSICA EM ALTA no Instagram.
Uma lupa mostra um detalhe da caixa e vai se afastando devagar, com contagem 3-2-1; depois a caixa aparece inteira
com o nome. Seis rodadas, do FÁCIL ao IMPOSSÍVEL, e no fim "Quantos você acertou? Comenta!" + CTA.

    python3 zoom.py --teste            # out/teste_zoom.jpg
"""
import argparse
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
WHITE = (255, 255, 255)
ORANGE = (249, 115, 22)
ORANGE_D = (214, 84, 6)
NAVY = (15, 23, 42)
DIF = {"FÁCIL": (22, 163, 74), "MÉDIO": (44, 120, 200), "DIFÍCIL": (200, 40, 60), "IMPOSSÍVEL": (20, 20, 20)}

# (caixa, nome na tela, dificuldade, centro do zoom em fração da caixa, zoom inicial)
QUIZ = [
    ("ticket_to_ride", "Ticket to Ride", "FÁCIL", (0.52, 0.55), 2.6),
    ("king_of_tokyo", "King of Tokyo", "FÁCIL", (0.70, 0.30), 2.8),
    ("dixit", "Dixit", "MÉDIO", (0.36, 0.62), 2.8),
    ("camel_up_second_edition", "Camel Up", "MÉDIO", (0.70, 0.30), 3.0),
    ("santorini", "Santorini", "DIFÍCIL", (0.30, 0.40), 3.2),
    ("wingspan", "Wingspan", "IMPOSSÍVEL", (0.80, 0.24), 3.4),
]


def font(n, s):
    return ImageFont.truetype(os.path.join(FN, n), int(s))


def emoji(ch, size):
    f = ImageFont.truetype(EMOJI, 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    return im.resize((size, int(im.height * size / im.width)), Image.LANCZOS)


def caixa(nome):
    return Image.open(os.path.join(HOBBY, "caixas", nome + ".png")).convert("RGBA")


def fundo(t=0.0):
    """Palco de game show nas cores da Sua Vez: degradê laranja com raios girando devagar."""
    yy = np.linspace(0, 1, H)[:, None, None]
    a = (np.array(ORANGE) * (1 - yy) + np.array(ORANGE_D) * 0.75 * yy) * np.ones((1, W, 1))
    img = Image.fromarray(a.astype(np.uint8), "RGB").convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    cx, cy, n = 540, 880, 20
    for i in range(n):
        a0 = i * 2 * math.pi / n + t * 0.08
        d.polygon([(cx, cy), (cx + 2400 * math.cos(a0), cy + 2400 * math.sin(a0)),
                   (cx + 2400 * math.cos(a0 + 0.16), cy + 2400 * math.sin(a0 + 0.16))], fill=(255, 255, 255, 22))
    img.alpha_composite(ov)
    return img


def lupa(img, detalhe, cx, cy, r):
    """Lupa: círculo com o detalhe ampliado, aro grosso branco e cabo."""
    d = ImageDraw.Draw(img)
    # cabo
    ang = math.radians(50)
    x0, y0 = cx + r * math.cos(ang), cy + r * math.sin(ang)
    x1, y1 = cx + (r + 330) * math.cos(ang), cy + (r + 330) * math.sin(ang)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse((cx - r - 30 + 14, cy - r - 30 + 24, cx + r + 30 + 14, cy + r + 30 + 24), fill=(60, 20, 0, 110))
    sd.line((x0 + 14, y0 + 24, x1 + 14, y1 + 24), fill=(60, 20, 0, 110), width=86)
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
    d.line((x0, y0, x1, y1), fill=NAVY, width=86)
    d.ellipse((x1 - 43, y1 - 43, x1 + 43, y1 + 43), fill=NAVY)
    d.line((x0, y0, x0 + 90 * math.cos(ang), y0 + 90 * math.sin(ang)), fill=(200, 205, 215), width=96)
    # vidro com o detalhe
    m = Image.new("L", (2 * r, 2 * r), 0)
    ImageDraw.Draw(m).ellipse((0, 0, 2 * r - 1, 2 * r - 1), fill=255)
    img.paste(detalhe.resize((2 * r, 2 * r), Image.LANCZOS), (cx - r, cy - r), m)
    # reflexo do vidro
    rf = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(rf).arc((cx - r * 0.8, cy - r * 0.8, cx + r * 0.8, cy + r * 0.8), 200, 250, fill=(255, 255, 255, 110),
                           width=22)
    img.alpha_composite(rf.filter(ImageFilter.GaussianBlur(3)))
    d.ellipse((cx - r - 30, cy - r - 30, cx + r + 30, cy + r + 30), outline=WHITE, width=34)
    d.ellipse((cx - r - 32, cy - r - 32, cx + r + 32, cy + r + 32), outline=NAVY, width=6)


def recorte_zoom(nome, centro, z, lado=860):
    """Pedaço quadrado da caixa ampliado z vezes (z=1: a caixa inteira cabe no círculo)."""
    cx_im = caixa(nome)
    bw, bh = cx_im.size
    base = max(bw, bh) * 1.05  # z=1 mostra a caixa toda
    s = base / z
    cx, cy = centro[0] * bw, centro[1] * bh
    # nunca sai da caixa (o fundo transparente entregaria o formato)
    if z > 1.6:
        cx = min(max(cx, s / 2), bw - s / 2)
        cy = min(max(cy, s / 2), bh - s / 2)
    fundo_l = Image.new("RGBA", cx_im.size, (255, 244, 230, 255))
    fundo_l.alpha_composite(cx_im)
    box = (cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2)
    pedaco = Image.new("RGBA", (int(s), int(s)), (255, 244, 230, 255))
    ix0, iy0 = max(0, int(box[0])), max(0, int(box[1]))
    ix1, iy1 = min(bw, int(box[2])), min(bh, int(box[3]))
    pedaco.alpha_composite(fundo_l.crop((ix0, iy0, ix1, iy1)), (ix0 - int(box[0]), iy0 - int(box[1])))
    return pedaco.resize((lado, lado), Image.LANCZOS)


def pilula(img, txt, x, y, cor, size=44, fg=WHITE):
    d = ImageDraw.Draw(img)
    f = font("Bungee-Regular.ttf", size)
    tw = d.textlength(txt, font=f)
    d.rounded_rectangle((x - tw / 2 - 34, y - size * 0.85, x + tw / 2 + 34, y + size * 0.85), radius=size, fill=cor,
                        outline=WHITE, width=5)
    d.text((x, y + 2), txt, font=f, fill=fg, anchor="mm")


def placar(img, k):
    d = ImageDraw.Draw(img)
    for i in range(len(QUIZ)):
        x = 540 + (i - 2.5) * 80
        cor = WHITE if i <= k else (255, 255, 255, 90)
        d.ellipse((x - 22, 350 - 22, x + 22, 350 + 22), fill=cor if i <= k else None, outline=WHITE, width=5)


def logo(img, w=170):
    lg = Image.open(LOGO).convert("RGBA")
    lg = lg.resize((w, int(lg.height * w / lg.width)), Image.LANCZOS)
    card = Image.new("RGBA", (lg.width + 24, lg.height + 20), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=16, fill=WHITE)
    card.alpha_composite(lg, (12, 10))
    img.alpha_composite(card, (W - card.width - 30, 40))


def contorno(d, xy, txt, f, fill, sw=10, stroke=NAVY):
    d.text(xy, txt, font=f, fill=fill, anchor="mm", stroke_width=sw, stroke_fill=stroke)


def quadro_teste(k, fase):
    nome, titulo, dif, centro, z0 = QUIZ[k]
    img = fundo(k)
    d = ImageDraw.Draw(img)
    contorno(d, (500, 250), "QUE JOGO É ESSE?", font("Bungee-Regular.ttf", 70), WHITE)
    img.alpha_composite(emoji("🔍", 80), (870, 210))
    placar(img, k)
    if fase == "gancho":
        contorno(d, (540, 560), "SÓ 1% ACERTA", font("Bungee-Regular.ttf", 120), (255, 230, 90), 14)
        contorno(d, (540, 720), "OS 6!", font("Bungee-Regular.ttf", 190), WHITE, 16)
        lupa(img, recorte_zoom(nome, centro, z0, 600), 540, 1180, 290)
    elif fase == "zoom":
        pilula(img, f"RODADA {k + 1} · {dif}", 540, 450, DIF[dif])
        lupa(img, recorte_zoom(nome, centro, z0), 540, 960, 390)
        contorno(d, (540, 1520), "2", font("Bungee-Regular.ttf", 200), WHITE, 16)
    else:  # revelação
        pilula(img, f"RODADA {k + 1} · {dif}", 540, 450, DIF[dif])
        cx = caixa(nome)
        cx = cx.resize((int(cx.width * 820 / cx.height), 820), Image.LANCZOS)
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sa = Image.new("RGBA", cx.size, (60, 20, 0, 255))
        sa.putalpha(cx.getchannel("A").point(lambda v: int(v * 0.5)))
        sh.alpha_composite(sa, (540 - cx.width // 2 + 16, 530 + 30))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(22)))
        img.alpha_composite(cx, (540 - cx.width // 2, 530))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((90, 1370, 990, 1510), radius=30, fill=NAVY, outline=WHITE, width=6)
        d.text((540, 1442), titulo.upper(), font=font("Bungee-Regular.ttf", 76), fill=WHITE, anchor="mm")
        pilula(img, "TEM NA SUA VEZ!", 540, 1580, (22, 163, 74), 40)
    logo(img)
    return img


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--teste", action="store_true")
    a = ap.parse_args()
    ims = [quadro_teste(0, "gancho"), quadro_teste(2, "zoom"), quadro_teste(2, "revela")]
    sheet = Image.new("RGB", (3 * 540 + 40, 980), (20, 20, 20))
    for k, im in enumerate(ims):
        sheet.paste(im.convert("RGB").resize((540, 960), Image.LANCZOS), (10 + k * 550, 10))
    sheet.save(os.path.join(ROOT, "out", "teste_zoom.jpg"), quality=90)
    ims[1].convert("RGB").save(os.path.join(ROOT, "out", "teste_zoom_full.jpg"), quality=92)
    print("ok")
