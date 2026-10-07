#!/usr/bin/env python3
"""Três conceitos visuais para o Reels "o que são os jogos modernos" (quadros parados para ele escolher).

    python3 conceitos.py    # out/conceito_1..3.png e out/conceitos_hobby.jpg
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
C = os.path.join(ROOT, "assets", "caixas")
FN = os.path.join(ROOT, "assets", "fonts")
OUT = os.path.join(ROOT, "out")
W, H = 1080, 1920
ORANGE, NAVY, WHITE, CREAM = (249, 115, 22), (15, 23, 42), (255, 255, 255), (255, 247, 237)


def font(n, s):
    return ImageFont.truetype(os.path.join(FN, n), s)


def caixa(n, h):
    im = Image.open(os.path.join(C, n + ".png")).convert("RGBA")
    return im.resize((int(im.width * h / im.height), h), Image.LANCZOS)


def sombra(im, blur=14, off=(10, 18), op=0.45):
    pad = blur * 3
    out = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    a = Image.new("L", out.size, 0)
    a.paste(im.getchannel("A").point(lambda v: int(v * op)), (pad + off[0], pad + off[1]))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 255))
    sh.putalpha(a.filter(ImageFilter.GaussianBlur(blur)))
    out.alpha_composite(sh)
    out.alpha_composite(im, (pad, pad))
    return out


def cola(img, im, x, y, rot=0):
    if rot:
        im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))


def logo(img, w=170):
    lg = Image.open(os.path.join(ROOT, "assets", "logo_suavez.png")).convert("RGBA")
    lg = lg.resize((w, int(lg.height * w / lg.width)), Image.LANCZOS)
    card = Image.new("RGBA", (lg.width + 24, lg.height + 20), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=16, fill=WHITE)
    card.alpha_composite(lg, (12, 10))
    img.alpha_composite(card, (W - card.width - 30, 40))


def etiqueta(txt1, txt2, cor, w=330, riscado=False):
    """Etiqueta de preço de papel com furinho e barbante."""
    h = int(w * 0.62)
    im = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = [(20, 20 + h * 0.5), (20 + h * 0.35, 20), (w + 20, 20), (w + 20, h + 20), (20 + h * 0.35, h + 20)]
    d.polygon(pts, fill=cor)
    d.ellipse((20 + h * 0.2 - 12, 20 + h * 0.5 - 12, 20 + h * 0.2 + 12, 20 + h * 0.5 + 12), fill=(0, 0, 0, 0))
    cx = 20 + h * 0.35 + (w - h * 0.35) / 2
    d.text((cx, 20 + h * 0.3), txt1, font=font("Poppins-ExtraBold.ttf", int(h * 0.17)), fill=WHITE, anchor="mm")
    d.text((cx, 20 + h * 0.66), txt2, font=font("Poppins-Black.ttf", int(h * 0.32)), fill=WHITE, anchor="mm")
    if riscado:
        d.line((cx - w * 0.33, 20 + h * 0.8, cx + w * 0.33, 20 + h * 0.5), fill=(255, 230, 0), width=12)
    return sombra(im, 8, (6, 10), 0.4)


# ---------------------------------------------------------------- 1. estante da ludoteca
def conceito_estante():
    img = Image.new("RGBA", (W, H), (58, 36, 24, 255))
    d = ImageDraw.Draw(img)
    for k in range(0, W, 6):  # veio da madeira do fundo
        d.line((k, 0, k + 40 * math.sin(k * 0.05), H), fill=(66 + (k * 7) % 14, 42, 28), width=4)
    rows = [("7_wonders_duel", "azul_duel", "camel_up_second_edition", "cartographers"),
            ("king_of_tokyo", "harmonies", "everdell_duo", "nekojima"),
            ("root", "santorini", "flamecraft", "mlem_space_agency")]
    for r, nomes in enumerate(rows):
        y = 640 + r * 400
        x = 60
        for n in nomes:
            if r == 1 and n == "everdell_duo":
                x += 230  # o espaço de onde a caixa "saiu"
                continue
            b = caixa(n, 300)
            img.alpha_composite(b, (int(x), int(y - b.height)))
            x += b.width - 20
        d.rectangle((0, y, W, y + 40), fill=(150, 98, 58))
        d.rectangle((0, y + 40, W, y + 56), fill=(96, 60, 36))
    # luz quente de cima
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ov).ellipse((-300, -600, W + 300, 900), fill=(255, 200, 120, 40))
    img.alpha_composite(ov.filter(ImageFilter.GaussianBlur(80)))
    cola(img, sombra(caixa("wingspan", 640), 22, (14, 26), 0.6), 540, 1180, -6)
    cola(img, etiqueta("NA LOJA", "R$ 377", (120, 120, 130), riscado=True), 260, 1520, 8)
    cola(img, etiqueta("5 DIAS", "R$ 45", ORANGE), 790, 1500, -6)
    f = font("LuckiestGuy-Regular.ttf", 84)
    for k, l in enumerate(("JOGO DE TABULEIRO", "NÃO É SÓ BANCO", "IMOBILIÁRIO!")):
        d.text((540, 230 + k * 104), l, font=f, fill=WHITE, anchor="mm", stroke_width=8, stroke_fill=NAVY)
    logo(img)
    return img


# ---------------------------------------------------------------- 2. programa de auditório
def conceito_auditorio():
    img = Image.new("RGBA", (W, H), (30, 8, 40, 255))
    d = ImageDraw.Draw(img)
    for k in range(-10, 30):  # cortina
        x = k * 60
        d.rectangle((x, 0, x + 60, H), fill=(150 + 30 * (k % 2), 20, 40))
    d.rectangle((0, 0, W, 120), fill=(110, 10, 30))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    o = ImageDraw.Draw(ov)
    o.polygon([(440, 0), (640, 0), (900, 1500), (180, 1500)], fill=(255, 240, 200, 70))  # holofote
    o.ellipse((150, 1380, 930, 1560), fill=(255, 240, 200, 90))
    img.alpha_composite(ov.filter(ImageFilter.GaussianBlur(20)))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((260, 1250, 820, 1480), radius=20, fill=(240, 190, 40))  # pódio
    d.rounded_rectangle((280, 1270, 800, 1460), radius=14, fill=(200, 40, 60))
    d.text((540, 1365), "SUA VEZ", font=font("Bungee-Regular.ttf", 90), fill=(255, 230, 120), anchor="mm")
    cola(img, sombra(caixa("clank_catacombs", 560)), 540, 980, 0)
    # placar de preço
    d.rounded_rectangle((90, 320, 990, 580), radius=30, fill=(20, 20, 30), outline=(240, 190, 40), width=10)
    for i in range(22):
        x = 120 + i * 40
        d.ellipse((x - 7, 312, x + 7, 326), fill=(255, 220, 120) if i % 2 else (180, 120, 40))
        d.ellipse((x - 7, 534, x + 7, 548), fill=(255, 220, 120) if i % 2 == 0 else (180, 120, 40))
    d.text((540, 380), "QUANTO CUSTA?", font=font("Bungee-Regular.ttf", 64), fill=WHITE, anchor="mm")
    for k, ch in enumerate("R$ 422"):
        x = 250 + k * 110
        d.rounded_rectangle((x - 48, 430, x + 48, 530), radius=10, fill=(50, 50, 60))
        d.line((x - 48, 480, x + 48, 480), fill=(20, 20, 30), width=4)
        d.text((x, 482), ch, font=font("Bungee-Regular.ttf", 70), fill=(255, 210, 60), anchor="mm")
    lb = font("Bungee-Regular.ttf", 58)
    d.rounded_rectangle((150, 1600 - 120, 930, 1600 - 20), radius=20, fill=(255, 210, 60))
    d.text((540, 1530), "ALUGUEL: R$ 45", font=lb, fill=(150, 20, 40), anchor="mm")
    d.text((540, 230), "JOGOS MODERNOS", font=font("LuckiestGuy-Regular.ttf", 88), fill=WHITE, anchor="mm",
           stroke_width=8, stroke_fill=(110, 10, 30))
    logo(img)
    return img


# ---------------------------------------------------------------- 3. conversa no celular
def balao(img, txt, x, y, w, minha, size=40):
    f = font("Poppins-SemiBold.ttf", size)
    words, lines, cur = txt.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if f.getlength(t) > w - 60 and cur:
            lines.append(cur)
            cur = wd
        else:
            cur = t
    lines.append(cur)
    bw = int(max(f.getlength(l) for l in lines)) + 60
    bh = int(len(lines) * size * 1.3 + 40)
    x0 = x if not minha else x + w - bw
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x0, y, x0 + bw, y + bh), radius=30, fill=(220, 248, 198) if minha else WHITE)
    for k, l in enumerate(lines):
        d.text((x0 + 30, y + 20 + k * size * 1.3), l, font=f, fill=(20, 20, 20))
    return y + bh + 24


def conceito_chat():
    img = Image.new("RGBA", (W, H), (236, 229, 221, 255))
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(3)
    for _ in range(140):  # padrão de rabiscos do fundo do chat
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        d.ellipse((x, y, x + 18, y + 18), outline=(222, 214, 205), width=3)
    d.rectangle((0, 0, W, 190), fill=(7, 94, 84))
    d.ellipse((40, 60, 130, 150), fill=ORANGE)
    d.text((85, 105), "SV", font=font("Poppins-Black.ttf", 40), fill=WHITE, anchor="mm")
    d.text((160, 80), "Sua Vez - Jogos", font=font("Poppins-ExtraBold.ttf", 44), fill=WHITE)
    d.text((160, 132), "digitando...", font=font("Poppins-SemiBold.ttf", 30), fill=(200, 240, 230))
    y = 240
    y = balao(img, "Jogo de tabuleiro? Tipo Banco Imobiliário? kkkk", 40, y, 760, False)
    y = balao(img, "Nada disso! Jogo moderno é rápido, bonito e todo mundo joga até o fim", 40, y, 1000, True)
    # mensagem com foto das caixas
    d = ImageDraw.Draw(img)
    x0 = W - 40 - 640
    d.rounded_rectangle((x0, y, W - 40, y + 520), radius=30, fill=(220, 248, 198))
    for k, (n, dx) in enumerate((("camel_up_second_edition", -170), ("ticket_to_ride", 0), ("dixit", 170))):
        cola(img, sombra(caixa(n, 300), 10, (6, 10), 0.35), x0 + 320 + dx, y + 240 + abs(dx) * 0.1, -dx / 30)
    d.text((x0 + 30, y + 440), "Festa, cooperativo, estratégia...", font=font("Poppins-SemiBold.ttf", 36),
           fill=(20, 20, 20))
    y += 560
    y = balao(img, "Mas deve ser caro né?", 40, y, 700, False)
    y = balao(img, "Na loja uns R$ 400. Aqui você aluga por R$ 45 e joga 5 dias!", 40, y, 1000, True)
    d = ImageDraw.Draw(img)
    d.rectangle((0, H - 150, W, H), fill=(240, 240, 240))
    d.rounded_rectangle((30, H - 125, W - 150, H - 35), radius=45, fill=WHITE)
    d.text((80, H - 80), "Mensagem", font=font("Poppins-SemiBold.ttf", 38), fill=(150, 150, 150), anchor="lm")
    d.ellipse((W - 125, H - 125, W - 35, H - 35), fill=(7, 94, 84))
    logo(img)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    ims = [conceito_estante(), conceito_auditorio(), conceito_chat()]
    nomes = ["1 · ESTANTE DA LUDOTECA", "2 · PROGRAMA DE AUDITÓRIO", "3 · CONVERSA NO CELULAR"]
    sheet = Image.new("RGB", (3 * 540 + 80, 960 + 140), (245, 240, 235))
    d = ImageDraw.Draw(sheet)
    for k, im in enumerate(ims):
        im.convert("RGB").save(os.path.join(OUT, f"conceito_{k + 1}.png"))
        sheet.paste(im.convert("RGB").resize((540, 960), Image.LANCZOS), (20 + k * 560, 110))
        d.text((20 + k * 560 + 270, 55), nomes[k], font=font("Poppins-ExtraBold.ttf", 34), fill=NAVY, anchor="mm")
    sheet.save(os.path.join(OUT, "conceitos_hobby.jpg"), quality=90)
    print("ok")


if __name__ == "__main__":
    main()
