#!/usr/bin/env python3
"""3 visuais para o Reels do Santorini (16/out/2026). Ele não consegue filmar as peças, então tudo é desenhado.
Mesma jogada nas 3: o construtor azul SOBE do 2º para o 3º andar = vitória. Caixa = a do SITE (Spin Master 2024).

    1 MAQUETE AO SOL     ilha isométrica no mar azul, dia claro, letreiro arredondado branco (cara da caixa)
    2 PÔR DO SOL ÉPICO   mesma ilha com luz dourada de fim de tarde, letreiro serifado dourado ("vença como um deus")
    3 VISTA DE CIMA      tabuleiro visto de cima como um manual animado: andares em quadrados concêntricos, setas

    python3 conceitos.py      # out/conceitos.jpg
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "comum"))
from motor import W, H, cola, sombra, letreiro, pilula, logo_card, font  # noqa: E402
from ilha import ilha, mar, ceu, altura, PEOES  # noqa: E402

OUT = os.path.join(ROOT, "out")
CAIXA = os.path.join(REPO, "hobby-reels", "assets", "acervo", "santorini.png")
FN = {"lilita": os.path.join(REPO, "assinatura-reels", "assets", "fonts", "LilitaOne.ttf"),
      "cinzel": os.path.join(REPO, "halloween-reels", "assets", "fonts", "Cinzel.ttf")}
AZUL_ESC = (18, 54, 128)
EST = {(1, 1): 1, (2, 1): 2, (2, 2): 3, (3, 2): 1, (1, 3): 2, (3, 3): 3}
CUP = {(3, 3)}


def txt(texto, fonte, size, cor, contorno, sw, sombra_px=0):
    from PIL import ImageFont
    f = ImageFont.truetype(FN[fonte], size)
    linhas = texto.split("\n")
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    lw = max(tmp.textlength(l, font=f) for l in linhas)
    lh = size * 1.12
    m = sw + sombra_px + 12
    im = Image.new("RGBA", (int(lw + 2 * m), int(lh * len(linhas) + 2 * m)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k, l in enumerate(linhas):
        x, y = im.width / 2, m + k * lh + lh / 2
        for s in range(sombra_px, 0, -1):
            d.text((x + s, y + s), l, font=f, fill=contorno, anchor="mm", stroke_width=sw, stroke_fill=contorno)
        d.text((x, y), l, font=f, fill=cor, anchor="mm", stroke_width=sw, stroke_fill=contorno)
    return im


def seta_pulo(d, iso, img, cor=(255, 214, 70)):
    """Seta curva do construtor no 2º andar (2,1) para o topo do 3º (2,2)."""
    a = iso(2, 1, altura(2) + 60)
    b = iso(2, 2, altura(3) + 70)
    pts = []
    for k in range(21):
        u = k / 20
        x = a[0] + (b[0] - a[0]) * u
        y = a[1] + (b[1] - a[1]) * u - 90 * math.sin(math.pi * u)
        pts.append((x, y))
    d.line(pts, fill=(20, 20, 30), width=16, joint="curve")
    d.line(pts, fill=cor, width=9, joint="curve")
    bx, by = pts[-1]
    d.polygon([(bx - 22, by - 26), (bx + 22, by - 26), (bx, by + 6)], fill=cor, outline=(20, 20, 30))


def opcao_1():
    img = Image.new("RGBA", (W, H))
    img.alpha_composite(ceu(W, 700, ((120, 200, 250), (176, 226, 250), (210, 238, 250))), (0, 0))
    img.alpha_composite(mar(W, H - 700, (110, 196, 232), (16, 92, 170)), (0, 700))
    d = ImageDraw.Draw(img)
    for x, y, r in [(180, 260, 70), (260, 240, 90), (840, 330, 80), (920, 310, 60)]:  # nuvens
        d.ellipse((x - r, y - r * 0.6, x + r, y + r * 0.6), fill=(255, 255, 255, 230))
    il = ilha(EST, CUP, {(2, 1): "azul", (3, 2): "laranja"}, tile=200, extra=seta_pulo)
    cola(img, sombra(il, 30, (0, 40), 0.35), W / 2, 1050)
    cola(img, txt("SUBIU NO 3º\nANDAR?", "lilita", 120, (255, 255, 255), AZUL_ESC, 14, 8), W / 2, 330, -3)
    cola(img, pilula("VOCÊ VENCEU!", 58, (255, 196, 40), AZUL_ESC, AZUL_ESC, bw=6), W / 2, 1560, 2)
    img.alpha_composite(logo_card(150), (W - 180, 40))
    return img


def opcao_2():
    img = ceu(W, H, ((255, 214, 150), (248, 140, 110), (120, 70, 140), (40, 30, 80)))
    d = ImageDraw.Draw(img)
    d.ellipse((W / 2 - 230, 520 - 230, W / 2 + 230, 520 + 230), fill=(255, 226, 150, 255))  # sol
    img = img.filter(ImageFilter.GaussianBlur(2))
    m = mar(W, 900, (240, 150, 120), (40, 40, 100), seed=4)
    img.alpha_composite(m, (0, H - 900))
    il = ilha(EST, CUP, {(2, 2): "azul", (3, 2): "laranja"}, tile=200, luz="sol")
    brilho = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(brilho).ellipse((W / 2 - 120, 830, W / 2 + 120, 1000), fill=(255, 230, 150, 160))
    img.alpha_composite(brilho.filter(ImageFilter.GaussianBlur(40)))
    cola(img, sombra(il, 30, (0, 40), 0.45), W / 2, 1120)
    cola(img, txt("CONSTRUA COMO\nUM MORTAL.", "cinzel", 86, (255, 240, 210), (60, 30, 50), 4, 0), W / 2, 240)
    cola(img, txt("VENÇA COMO\nUM DEUS.", "cinzel", 110, (255, 206, 90), (70, 30, 40), 5, 4), W / 2, 1560)
    img.alpha_composite(logo_card(150), (W - 180, 40))
    return img


def opcao_3():
    img = Image.new("RGBA", (W, H), (240, 236, 226, 255))
    d = ImageDraw.Draw(img)
    for k in range(0, W, 60):  # greca nas bordas
        d.rectangle((k, 0, k + 40, 26), fill=(30, 84, 196))
        d.rectangle((k, H - 26, k + 40, H), fill=(30, 84, 196))
    cel, x0, y0 = 170, (W - 5 * 170) / 2, 520
    for x in range(5):
        for y in range(5):
            cx, cy = x0 + x * cel, y0 + y * cel
            d.rectangle((cx + 4, cy + 4, cx + cel - 4, cy + cel - 4), fill=(126, 190, 86) if (x + y) % 2 else (140, 200, 100))
            nv = EST.get((x, y), 0)
            for lv in range(1, nv + 1):  # andares = quadrados concêntricos
                m = 10 + (lv - 1) * 22
                d.rectangle((cx + m, cy + m, cx + cel - m, cy + cel - m), fill=(250, 250, 246),
                            outline=(150, 160, 170), width=4)
            if nv:
                d.text((cx + cel - 26, cy + 24), str(nv), font=font("Poppins-Black.ttf", 30), fill=(80, 90, 110), anchor="mm")
            if (x, y) in CUP:
                d.ellipse((cx + 45, cy + 45, cx + cel - 45, cy + cel - 45), fill=(30, 84, 196))
    def peao(x, y, cor):
        cx, cy = x0 + x * cel + cel / 2, y0 + y * cel + cel / 2
        esc, luz = PEOES[cor]
        d.ellipse((cx - 30, cy - 30, cx + 30, cy + 30), fill=esc, outline=(20, 20, 30), width=4)
        d.ellipse((cx - 14, cy - 18, cx + 2, cy - 2), fill=luz)
    peao(2, 1, "azul")
    peao(3, 2, "laranja")
    a = (x0 + 2.5 * cel, y0 + 1.5 * cel + 34)
    b = (x0 + 2.5 * cel, y0 + 2.5 * cel - 40)
    d.line([a, b], fill=(220, 38, 38), width=12)
    d.polygon([(b[0] - 26, b[1] - 10), (b[0] + 26, b[1] - 10), (b[0], b[1] + 26)], fill=(220, 38, 38))
    cola(img, txt("DO 2 PRO 3 = VITÓRIA!", "lilita", 92, (220, 38, 38), (255, 255, 255), 10), W / 2, 1480, -2)
    cola(img, txt("COMO SE GANHA\nNO SANTORINI?", "lilita", 104, AZUL_ESC, (255, 255, 255), 10), W / 2, 280)
    cola(img, pilula("SOBE NO MÁX. 1 ANDAR POR VEZ", 38, AZUL_ESC), W / 2, 1640)
    img.alpha_composite(logo_card(150), (W - 180, 46))
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    ops = [opcao_1(), opcao_2(), opcao_3()]
    nomes = ["1 · MAQUETE AO SOL", "2 · PÔR DO SOL ÉPICO", "3 · VISTA DE CIMA"]
    folha = Image.new("RGB", (3 * 540 + 40, 960 + 90), (255, 255, 255))
    d = ImageDraw.Draw(folha)
    for k, im in enumerate(ops):
        folha.paste(im.convert("RGB").resize((540, 960), Image.LANCZOS), (10 + k * 550, 80))
        d.text((10 + k * 550 + 270, 40), nomes[k], font=font("Poppins-Black.ttf", 34), fill=(20, 20, 30), anchor="mm")
    folha.save(os.path.join(OUT, "conceitos.jpg"), quality=90)
    print("ok")


if __name__ == "__main__":
    main()
