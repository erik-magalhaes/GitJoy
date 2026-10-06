#!/usr/bin/env python3
"""Arte da promoção "3 jogos = 7 dias para todos" (feed 1080x1350 e story 1080x1920).

    python3 promo/promo_3jogos.py    # gera promo/out/promo_3jogos_feed.png e promo_3jogos_story.png
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
OUT = os.path.join(ROOT, "out")
FONT = os.path.join(REPO, "sintonia-reels", "assets", "fonts")
LOGO = os.path.join(REPO, "voodoo-reels", "assets", "logo_suavez.png")
CAIXAS = [os.path.join(REPO, "sintonia-reels", "assets", "pieces", "box.png"),
          os.path.join(REPO, "architects-reels", "assets", "oficial", "caixa3d.png"),
          os.path.join(REPO, "voodoo-reels", "assets", "pieces", "box.png")]

# cores do site da Sua Vez
ORANGE = (249, 115, 22)
ORANGE_D = (214, 84, 6)
NAVY = (15, 23, 42)
CREAM = (255, 247, 237)
GREEN = (22, 163, 74)
GREEN_L = (220, 252, 231)
BLUE = (44, 120, 200)
GRAY = (226, 232, 240)
WHITE = (255, 255, 255)


def f(name, size):
    return ImageFont.truetype(os.path.join(FONT, name), size)


BLACK = "Poppins-Black.ttf"
XB = "Poppins-ExtraBold.ttf"
SB = "Poppins-SemiBold.ttf"


def shadowed(im, blur=18, off=(10, 18), op=0.35):
    pad = blur * 3
    out = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    a = Image.new("L", out.size, 0)
    a.paste(im.getchannel("A").point(lambda v: int(v * op)), (pad + off[0], pad + off[1]))
    sh = Image.new("RGBA", out.size, NAVY + (255,))
    sh.putalpha(a.filter(ImageFilter.GaussianBlur(blur)))
    out.alpha_composite(sh)
    out.alpha_composite(im, (pad, pad))
    return out


def paste_c(img, im, x, y, rot=0):
    if rot:
        im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))


def text_c(d, xy, txt, font, fill, **kw):
    d.text(xy, txt, font=font, fill=fill, anchor="mm", **kw)


def calendario(width):
    """7 dias: 5 normais + 2 de presente (laranja)."""
    n, gap = 7, 14
    cw = (width - gap * (n - 1)) / n
    ch = cw * 1.18
    im = Image.new("RGBA", (int(width), int(ch + 70)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k in range(n):
        x0 = k * (cw + gap)
        extra = k >= 5
        bg = ORANGE if extra else WHITE
        d.rounded_rectangle((x0, 0, x0 + cw, ch), radius=int(cw * 0.18), fill=bg,
                            outline=ORANGE_D if extra else (203, 213, 225), width=4)
        d.rounded_rectangle((x0, 0, x0 + cw, ch * 0.26), radius=int(cw * 0.18), fill=ORANGE_D if extra else BLUE)
        d.rectangle((x0, ch * 0.14, x0 + cw, ch * 0.26), fill=ORANGE_D if extra else BLUE)
        text_c(d, (x0 + cw / 2, ch * 0.62), str(k + 1), f(BLACK, int(cw * 0.5)), WHITE if extra else NAVY)
    # chaves embaixo
    d.text(((5 * cw + 4 * gap) / 2, ch + 36), "5 DIAS NORMAIS", font=f(XB, int(cw * 0.2)), fill=NAVY, anchor="mm")
    d.text((5 * (cw + gap) + (2 * cw + gap) / 2, ch + 36), "+2 GRÁTIS", font=f(XB, int(cw * 0.2)), fill=ORANGE_D,
           anchor="mm")
    return im


def caixas(height):
    ims = []
    for p in CAIXAS:
        im = Image.open(p).convert("RGBA")
        im = im.crop(im.getbbox())
        ims.append(im.resize((int(im.width * height / im.height), height), Image.LANCZOS))
    return ims


def selo(text1, text2, r):
    S = int(r * 2.3)
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = S / 2
    pts = []
    for k in range(32):
        rr = r * (1.0 if k % 2 == 0 else 0.9)
        a = k * math.pi / 16
        pts.append((c + rr * math.cos(a), c + rr * math.sin(a)))
    d.polygon(pts, fill=GREEN)
    d.ellipse((c - r * 0.8, c - r * 0.8, c + r * 0.8, c + r * 0.8), outline=WHITE, width=5)
    text_c(d, (c, c - r * 0.18), text1, f(BLACK, int(r * 0.42)), WHITE)
    text_c(d, (c, c + r * 0.28), text2, f(XB, int(r * 0.2)), WHITE)
    return im


def fundo(W, H):
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img, "RGBA")
    for k in range(-H, W + H, 90):  # listras suaves
        d.line((k, 0, k - H, H), fill=ORANGE + (16,), width=34)
    d.ellipse((W * 0.55, -W * 0.35, W * 1.35, W * 0.45), fill=ORANGE + (45,))
    d.ellipse((-W * 0.4, H - W * 0.5, W * 0.4, H + W * 0.3), fill=BLUE + (30,))
    return img.convert("RGBA")


def arte(W, H, story):
    img = fundo(W, H)
    d = ImageDraw.Draw(img)
    s = W / 1080
    y = (230 if story else 40) * s
    k = 1.0 if story else 0.8  # o feed é mais baixo: tudo um pouco menor
    lg = Image.open(LOGO).convert("RGBA")
    lw = int(300 * s * (1 if story else 0.8))
    lg = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS)
    card = Image.new("RGBA", (lg.width + 40, lg.height + 30), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=26, fill=WHITE)
    card.alpha_composite(lg, (20, 15))
    paste_c(img, shadowed(card, 12, (4, 8), 0.2), W / 2, y + card.height / 2)
    y += card.height + 40 * s * k
    text_c(d, (W / 2, y + 40 * s), "ALUGOU 3 JOGOS?", f(BLACK, int(92 * s)), NAVY)
    y += 110 * s
    # faixa principal
    band_h = 150 * s
    d.rounded_rectangle((60 * s, y, W - 60 * s, y + band_h), radius=int(36 * s), fill=ORANGE)
    text_c(d, (W / 2, y + band_h / 2 + 4), "TODOS FICAM 7 DIAS!", f(BLACK, int(84 * s)), WHITE)
    y += band_h + 24 * s
    text_c(d, (W / 2, y + 30 * s), "+2 dias de presente, pelo mesmo preço!", f(SB, int(46 * s)), NAVY)
    y += (100 if story else 80) * s
    # caixas em leque com o selo
    bh = int((430 if story else 300) * s)
    bx = caixas(bh)
    cy = y + bh * 0.62
    for k, (im, dx, rot) in enumerate(zip(bx, (-300, 0, 300), (9, 0, -9))):
        paste_c(img, shadowed(im), W / 2 + dx * s * (1.0 if story else 0.95), cy + (25 if k != 1 else 0) * s, rot)
    paste_c(img, selo("3 = 7", "DIAS PARA TODOS", int(100 * s)), W - 150 * s, y + 95 * s, 12)
    y += bh + (90 if story else 60) * s
    cal = calendario((W - 160 * s) * (1 if story else 0.82))
    paste_c(img, cal, W / 2, y + cal.height / 2)
    y += cal.height + (50 if story else 24) * s
    # rodapé
    if story:
        box = (60 * s, y, W - 60 * s, y + 120 * s)
        d.rounded_rectangle(box, radius=int(26 * s), fill=GREEN_L, outline=(134, 239, 172), width=3)
        text_c(d, (W / 2, y + 42 * s), "Monte o carrinho com 3 jogos no site:", f(SB, int(34 * s)), (21, 101, 52))
        text_c(d, (W / 2, y + 86 * s), "o prazo extra entra sozinho!", f(XB, int(38 * s)), (21, 101, 52))
        y += 150 * s
    text_c(d, (W / 2, y + 20 * s), "RETIRE EM MAUÁ OU RECEBA EM CASA", f(XB, int(36 * s)), NAVY)
    text_c(d, (W / 2, y + 75 * s), "suavez.acervodejogos.com.br  ·  @suavez_bg", f(SB, int(32 * s)), ORANGE_D)
    return img.convert("RGB")


def main():
    os.makedirs(OUT, exist_ok=True)
    arte(1080, 1350, False).save(os.path.join(OUT, "promo_3jogos_feed.png"))
    arte(1080, 1920, True).save(os.path.join(OUT, "promo_3jogos_story.png"))
    print("ok")


if __name__ == "__main__":
    main()
