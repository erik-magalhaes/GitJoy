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

import numpy as np

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
    """Erik fazendo JOIA e olhando pra câmera (quadro de 124,6 s do 152424, pedido dele), num cartão quadrado de cantos
    redondos (no círculo o polegar ficava cortado). O recorte para em y 850: logo abaixo ele segura a caixa do Flip 7,
    que é o Nº 1 escondido da capa."""
    im = Image.open(os.path.join(ROOT, "assets", "capa", "erik_top10.jpg")).convert("RGB")
    im = im.crop((120, 0, 970, 850)).resize((d, d), Image.LANCZOS)
    ow, sh, r = 9, 12, 44
    t = d + 2 * ow
    out = Image.new("RGBA", (t + sh, t + sh), (0, 0, 0, 0))
    dr = ImageDraw.Draw(out)
    dr.rounded_rectangle((sh, sh, t + sh - 1, t + sh - 1), r, fill=INK)
    dr.rounded_rectangle((0, 0, t - 1, t - 1), r, fill=INK)
    m = Image.new("L", (d, d), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, d - 1, d - 1), r - ow, fill=255)
    out.paste(im, (ow, ow), m)
    return out

def capa_foto(arq, saida, zoom=1.12, cx=0.5):
    """Versão só com o título (pedido dele): quadro do vídeo em tela cheia, ele olhando pro lado, e "TOP 10 ÀS CEGAS"
    embaixo. A caixa do Flip 7 que ele segura (o Nº 1) some num degradê azul-noite atrás do título."""
    im = Image.open(os.path.join(ROOT, "assets", "capa", arq)).convert("RGB")
    w, h = int(W * zoom), int(H * zoom)
    im = im.resize((w, h), Image.LANCZOS)
    x0 = int(min(max(w * cx - W / 2, 0), w - W))
    img = im.crop((x0, 0, x0 + W, H)).convert("RGBA")
    # degradê de baixo: transparente até y 1020, opaco a partir de y 1330
    g = Image.new("L", (1, H), 0)
    for y in range(H):
        g.putpixel((0, y), int(255 * min(max((y - 1020) / 310, 0), 1) ** 1.2))
    cor = Image.new("RGBA", (W, H), NOITE + (255,))
    cor.putalpha(g.resize((W, H)))
    img.alpha_composite(cor)
    rnd = random.Random(5)
    d = ImageDraw.Draw(img)
    cores = [(255, 199, 31), (244, 136, 37), (28, 124, 150), (250, 250, 250), (219, 39, 119)]
    for _ in range(40):  # confete só na parte escura
        x, y = rnd.uniform(0, W), rnd.uniform(1330, H)
        a, sz = rnd.uniform(0, math.pi), rnd.uniform(7, 14)
        pts = [(x + sz * math.cos(a + k * math.pi / 2) * (1 if k % 2 else 0.45),
                y + sz * math.sin(a + k * math.pi / 2) * (1 if k % 2 else 0.45)) for k in range(4)]
        d.polygon(pts, fill=cores[rnd.randrange(5)] + (180,))
    E.cola(img, E.titulo("TOP 10\nÀS CEGAS", 175, (255, 199, 31)), W / 2, 1440, -3)
    lg = E.logo(170)
    img.alpha_composite(lg, (W - lg.width - 36, 46))
    img.convert("RGB").save(os.path.join(OUT, saida + ".png"))
    return img

def balao(w, h):
    """Balão de pensamento branco com contorno marrom e sombra sólida (cores da logo dentro)."""
    sh, ow = 12, 8
    out = Image.new("RGBA", (w + sh + 2, h + sh + 2), (0, 0, 0, 0))
    m = Image.new("L", out.size, 0)
    dm = ImageDraw.Draw(m)
    # nuvem = elipse central + bolotas na borda
    dm.ellipse((w * 0.06, h * 0.12, w * 0.94, h * 0.88), fill=255)
    for k in range(11):
        a = 2 * math.pi * k / 11
        cx, cy = w / 2 + math.cos(a) * w * 0.40, h / 2 + math.sin(a) * h * 0.36
        r = min(w, h) * 0.16
        dm.ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    borda = m.filter(ImageFilter.MaxFilter(2 * ow + 1))
    som = Image.new("L", out.size, 0)
    som.paste(borda, (sh, sh))
    out.paste(INK + (255,), (0, 0), som)
    out.paste(INK + (255,), (0, 0), borda)
    out.paste((250, 250, 250, 255), (0, 0), m)
    return out

def colagem():
    """Fundo com as 10 caixas do top 10 dele (inclusive o Flip 7, misturado), meio sobrepostas e giradas, cobrindo tudo."""
    nomes = list(TOP.values()) + ["flip_7_a_vinganca"]
    rnd = random.Random(21)
    img = Image.new("RGBA", (W, H), (14, 70, 88, 255))
    cache = {n: caixa(n, 330, 330) for n in nomes}
    k = 0
    for lin in range(8):
        for col in range(5):
            n = nomes[(col * 3 + lin * 7) % len(nomes)]
            k += 1
            x = col * 250 - 40 + (125 if lin % 2 else 0) + rnd.uniform(-30, 30)
            y = lin * 255 - 60 + rnd.uniform(-30, 30)
            bx = cache[n].rotate(rnd.uniform(-14, 14), expand=True, resample=Image.BICUBIC)
            sh = Image.new("RGBA", bx.size, (0, 0, 0, 0))
            sh.paste((0, 0, 0, 140), (0, 0), bx.getchannel("A"))
            E.cola(img, sh.filter(ImageFilter.GaussianBlur(10)), x + 10, y + 14)
            E.cola(img, bx, x, y)
    return img


def capa_criativa(arq="erik_lado3.jpg", saida="capa_top10_erik_final", caixas=False):
    """3ª versão (pedido dele: "tá muito simples, seja criativo, cores da logo, logo no canto superior direito"):
    foto dele olhando pra cima (13,5 s) + balão de pensamento "E AGORA? ONDE EU PONHO ESSE?" com 3 caixas-mistério,
    selo "ELE NÃO SABIA O PRÓXIMO JOGO!", título TOP 10 (amarelo) + ÀS CEGAS (faixa laranja) e as 10 casas com "?"
    sobre o petróleo da logo. O degradê esconde a caixa do Flip 7 (o Nº 1) que ele segura."""
    PET, PET_E = (28, 124, 150), (14, 70, 88)
    if caixas:
        img = colagem()
        tinta = Image.new("RGBA", (W, H), PET_E + (85,))  # petróleo por cima pra ele saltar na frente
        img.alpha_composite(tinta)
        pes = Image.open(os.path.join(ROOT, "assets", "capa", arq.replace(".jpg", "_recorte.png"))).convert("RGBA")
        pes = pes.resize((W, H), Image.LANCZOS)
        a = pes.getchannel("A")
        fade = Image.new("L", (1, H), 0)
        for y in range(H):  # some de y 960 a 1150 (a caixa do Flip 7 na mão dele fica escondida)
            fade.putpixel((0, y), int(255 * min(max((1150 - y) / 190, 0), 1)))
        a = Image.fromarray((np.asarray(a, np.float32) * np.asarray(fade.resize((W, H)), np.float32) / 255).astype(np.uint8))
        pes.putalpha(a)
        som = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        som.paste((8, 30, 40, 200), (16, 10), a)  # sombra atrás dele
        img.alpha_composite(som.filter(ImageFilter.GaussianBlur(14)))
        borda = a.filter(ImageFilter.MaxFilter(13))  # contorno branco de adesivo
        img.paste((250, 250, 250, 255), (0, 0), borda)
        img.alpha_composite(pes)
    else:
        img = Image.open(os.path.join(ROOT, "assets", "capa", arq)).convert("RGB").resize((W, H), Image.LANCZOS)
        img = img.convert("RGBA")
    LAR, AMA, BR = (244, 136, 37), (255, 199, 31), (250, 250, 250)
    # degradê pro petróleo escuro, opaco a partir de y 1180
    g = Image.new("L", (1, H), 0)
    for y in range(H):
        g.putpixel((0, y), int((205 if caixas else 255) * min(max((y - 930) / 250, 0), 1) ** 1.3))
    base = Image.new("RGBA", (W, H), PET_E + (255,))
    d = ImageDraw.Draw(base)
    for k in range(-20, 40):  # listras diagonais suaves (petróleo claro)
        x = k * 90
        d.polygon([(x, H), (x + 45, H), (x + 45 + 900, H - 900), (x + 900, H - 900)], fill=(20, 88, 108, 255))
    base.putalpha(g.resize((W, H)))
    img.alpha_composite(base)
    d = ImageDraw.Draw(img)
    rnd = random.Random(8)
    for _ in range(45):  # confete nas cores da logo
        x, y = rnd.uniform(0, W), rnd.uniform(1200, H)
        a, sz = rnd.uniform(0, math.pi), rnd.uniform(8, 15)
        pts = [(x + sz * math.cos(a + k * math.pi / 2) * (1 if k % 2 else 0.45),
                y + sz * math.sin(a + k * math.pi / 2) * (1 if k % 2 else 0.45)) for k in range(4)]
        d.polygon(pts, fill=(LAR, AMA, BR, PET)[rnd.randrange(4)] + (230,))
    # balão de pensamento saindo da cabeça dele
    for (x, y, r) in ((632, 770, 17), (668, 712, 27)):
        d.ellipse((x - r + 7, y - r + 7, x + r + 7, y + r + 7), fill=INK)
        d.ellipse((x - r, y - r, x + r, y + r), fill=BR, outline=INK, width=6)
    b = balao(470, 360)
    db = ImageDraw.Draw(b)
    db.text((235, 92), "E AGORA?", font=E.lilita(46), fill=INK, anchor="mm")
    db.text((235, 140), "ONDE EU PONHO?", font=E.lilita(38), fill=LAR, anchor="mm")
    for i, (c, rot) in enumerate(((PET, -8), (LAR, 4), (AMA, -3))):
        cx = E.bloco(84, 98, c, raio=12, ow=5, sombra=6).copy()
        ImageDraw.Draw(cx).text((40, 47), "?", font=E.lilita(62), fill=BR if c != AMA else INK, anchor="mm",
                                stroke_width=3, stroke_fill=INK)
        E.cola(b, cx, 140 + i * 95, 238, rot)
    E.cola(img, b, 840, 520, 3)
    # selo
    E.cola(img, E.pilula("ELE NÃO SABIA O PRÓXIMO JOGO!", 40, AMA, INK), W / 2, 1090, -3)
    # título
    E.cola(img, E.titulo("TOP 10", 200, AMA), W / 2, 1255, -2)
    E.cola(img, E.pilula("ÀS CEGAS", 104, LAR, BR, fonte_titulo=True, pad=(46, 8), ow=7, sombra=10), W / 2, 1425, 2)
    # as 10 casas
    for n in range(1, 11):
        t = E.bloco(84, 96, BR, raio=16, ow=5, sombra=6).copy()
        dt = ImageDraw.Draw(t)
        dt.text((40, 20), str(n), font=E.lilita(24), fill=PET, anchor="mm")
        dt.text((40, 56), "?", font=E.lilita(48), fill=LAR if n > 1 else (219, 39, 119), anchor="mm")
        E.cola(img, t, 76 + (n - 1) * 103, 1572, (-4, 3, -2, 4, -3)[n % 5])
    lg = E.logo(210)
    img.alpha_composite(lg, (W - lg.width - 34, 40))
    img.convert("RGB").save(os.path.join(OUT, saida + ".png"))
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    img = fundo()
    # título
    E.cola(img, E.pilula("SEM SABER O PRÓXIMO JOGO!", 38, (219, 39, 119), (250, 250, 250)), W / 2, 300, -2)
    E.cola(img, foto_erik(340), 222, 535, -4)
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
    if "--final" in sys.argv:  # versão criativa com a foto escolhida (13,5 s)
        os.makedirs(OUT, exist_ok=True)
        capa_criativa()
        capa_criativa(saida="capa_top10_erik_caixas", caixas=True)
        print("ok")
    elif "--foto" in sys.argv:  # só título + foto dele olhando pro lado
        os.makedirs(OUT, exist_ok=True)
        a = capa_foto("erik_lado.jpg", "capa_top10_erik_foto", cx=0.44)
        b = capa_foto("erik_lado2.jpg", "capa_top10_erik_foto2")
        sh = Image.new("RGB", (1100, 960), (255, 255, 255))
        for i, im in enumerate((a, b)):
            sh.paste(im.convert("RGB").resize((540, 960), Image.LANCZOS), (i * 560, 0))
        sh.save(os.path.join(OUT, "capa_top10_erik_foto_folha.jpg"), quality=90)
        print("ok")
    else:
        main()
