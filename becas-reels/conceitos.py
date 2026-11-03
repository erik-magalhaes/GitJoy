#!/usr/bin/env python3
"""3 conceitos NOVOS para o Reels da tarde no Becas (3/nov/2026). Pedido dele: "os vídeos estão ficando todos iguais,
mesma pegada, mesmos sons; seja imaginativo, use trechos de vídeos que a gente já tem, com a mesma estética da loja".

  1 PARA DE ROLAR   o vídeo começa fingindo ser o próprio feed (posts cinza rolando, som de rolagem); a tela TRINCA
                    e estoura em cor: cenas reais deles jogando, os guarda-chuvinhas caem. Quebra de padrão.
  2 JOGO DAS XÍCARAS  o vídeo É um jogo: 3 xícaras do café embaralham, "onde está o dado? comenta 1, 2 ou 3"; a
                    resposta abre o convite. Dá replay e comentário.
  3 6 HORAS EM 30 S   as cenas REAIS deles (Sky Team, top 10, mesa) em cortes no ritmo, com um relógio gigante
                    correndo 13:00 → 19:00 e etiquetas escritas ("14h: já tá todo mundo rindo", "18h59: só mais uma?").

    /usr/bin/python3 conceitos.py    # out/conceitos.jpg
"""
import math
import os
import random
import subprocess
import sys

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
for p in ("assinatura-reels", "promo", "comum"):
    sys.path.insert(0, os.path.join(REPO, p))
import estilo as E  # noqa: E402
import tarde_becas as TB  # noqa: E402
from motor import ffmpeg  # noqa: E402

W, H = 1080, 1920
OUT = os.path.join(ROOT, "out")
MAR, PET, LAR, AMA, BR, ROSA = E.MARROM, E.PETROLEO, E.LARANJA, E.AMARELO, E.BRANCO, TB.ROSA
BRUTOS = os.path.join(REPO, "gravados-reels", "brutos")


def quadro_video(arq, t):
    tmp = os.path.join(OUT, "_q.jpg")
    subprocess.run([ffmpeg(), "-v", "error", "-ss", str(t), "-i", arq, "-frames:v", "1", "-y", tmp], check=True)
    return Image.open(tmp).convert("RGB")


def cheio(im):
    return ImageOps.fit(im, (W, H), Image.LANCZOS).convert("RGBA")


def logo(img):
    lg = E.logo(150)
    img.alpha_composite(lg, (W - 180, 40))


# ---------------------------------------------------------------- 1 PARA DE ROLAR
def feed_cinza():
    img = Image.new("RGBA", (W, H), (236, 236, 236, 255))
    d = ImageDraw.Draw(img)
    rnd = random.Random(2)
    y = -260
    while y < H:
        d.ellipse((40, y + 20, 110, y + 90), fill=(200, 200, 200))
        d.rounded_rectangle((130, y + 35, 130 + rnd.randint(180, 320), y + 60), 10, fill=(205, 205, 205))
        d.rectangle((0, y + 110, W, y + 110 + 760), fill=tuple([rnd.randint(185, 210)] * 3))
        for k in range(3):
            d.ellipse((40 + k * 80, y + 900, 90 + k * 80, y + 950), outline=(170, 170, 170), width=5)
        y += 1010
    return img.filter(ImageFilter.GaussianBlur(1.2))


def rolar_a():
    img = feed_cinza()
    E.cola(img, E.titulo("SÁBADO\nROLANDO\nO FEED\nDE NOVO?", 150, BR), W / 2, 820, -2)
    E.cola(img, E.pilula("👆 continua rolando...".replace("👆 ", ""), 40, (120, 120, 120), BR), W / 2, 1330, 0)
    return img


def trinca(img, cx, cy, seed=4):
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    for k in range(14):
        a = k * 2 * math.pi / 14 + rnd.uniform(-0.2, 0.2)
        x, y = cx, cy
        for _ in range(5):
            r = rnd.uniform(70, 190)
            a += rnd.uniform(-0.35, 0.35)
            x2, y2 = x + r * math.cos(a), y + r * math.sin(a)
            d.line((x, y, x2, y2), fill=(255, 255, 255, 230), width=5)
            d.line((x + 3, y + 3, x2 + 3, y2 + 3), fill=(40, 40, 40, 120), width=2)
            x, y = x2, y2


def rolar_b():
    # metade de cima ainda o feed cinza; a tela trinca e por baixo aparece a cena real colorida
    real = cheio(Image.open(os.path.join(REPO, "gravados-reels", "assets", "capa", "erik_rindo.jpg")))
    real = ImageEnhance.Color(real).enhance(1.08)
    cinza = feed_cinza()
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([(0, 0), (W, 0), (W, 520), (640, 690), (380, 600), (0, 760)], fill=255)
    img = real.copy()
    img.paste(cinza, (0, 0), m)
    trinca(img, 170, 700)
    TB.guarda_chuvas(img, [140, 230, 110, 210, 130], 150)
    E.cola(img, E.titulo("OU JOGANDO\nNO BECAS?", 140, AMA), W / 2, 1360, -2)
    E.cola(img, E.pilula("TARDE DE JOGOS · DATA EM BREVE", 38, LAR, BR, fonte_titulo=True), W / 2, 1560, 1.5)
    logo(img)
    return img


# ---------------------------------------------------------------- 2 JOGO DAS XÍCARAS
def xicara(w, cor):
    h = int(w * 0.8)
    im = Image.new("RGBA", (w + 80, h + 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # xícara virada de boca para baixo (como no jogo dos copinhos): corpo trapézio + pires
    corpo = [(w * 0.18 + 20, 10), (w * 0.82 + 20, 10), (w + 20, h - 20), (20, h - 20)]
    d.polygon([(x + 8, y + 10) for x, y in corpo], fill=MAR)
    d.polygon(corpo, fill=cor, outline=MAR)
    d.line(corpo + [corpo[0]], fill=MAR, width=7)
    d.arc((w + 2, h * 0.25, w + 75, h * 0.7), -100, 100, fill=MAR, width=14)  # asa
    d.arc((w + 2, h * 0.25, w + 75, h * 0.7), -100, 100, fill=cor, width=6)
    d.rounded_rectangle((0, h - 30, w + 40, h - 2), 14, fill=BR, outline=MAR, width=6)  # pires
    d.ellipse((w * 0.35, h * 0.4, w * 0.65, h * 0.55), fill=BR)  # bolinha branca da estampa
    return im


def mesa():
    img = Image.new("RGBA", (W, H), (246, 236, 220, 255))
    d = ImageDraw.Draw(img)
    for y in range(1050, H, 70):  # toalha xadrez da mesa
        for x in range(0, W, 70):
            if (x // 70 + y // 70) % 2:
                d.rectangle((x, y, x + 70, y + 70), fill=(232, 120, 60))
    d.rectangle((0, 1040, W, 1050), fill=MAR)
    return img


def xic_a():
    img = mesa()
    TB.guarda_chuvas(img, [90, 170, 70, 150, 90], 130)
    E.cola(img, E.titulo("ONDE ESTÁ\nO DADO?", 150, LAR), W / 2, 620, -2)
    cores = (PET, AMA, ROSA)
    for k, x in enumerate((230, 540, 850)):
        x2 = x + (60 if k == 0 else -60 if k == 2 else 0)
        for j in range(3, 0, -1):  # rastro de movimento
            g = xicara(220, cores[k])
            g.putalpha(g.getchannel("A").point(lambda v, j=j: int(v * 0.18)))
            E.cola(img, g, x2 + j * 40 * (1 if k == 0 else -1), 1090)
        E.cola(img, xicara(220, cores[k]), x2, 1090, (k - 1) * 4)
        E.cola(img, E.pilula(str(k + 1), 56, BR, MAR, fonte_titulo=True), x, 1300)
    E.cola(img, E.texto("Comenta 1, 2 ou 3!", 52, MAR, 900), W / 2, 1470)
    logo(img)
    return img


def xic_b():
    img = mesa()
    TB.guarda_chuvas(img, [90, 170, 70, 150, 90], 130)
    cores = (PET, AMA, ROSA)
    for k, x in enumerate((230, 540, 850)):
        y = 1090 - (300 if k == 1 else 0)
        E.cola(img, xicara(220, cores[k]), x, y, (k - 1) * 4 + (12 if k == 1 else 0))
    # debaixo da xícara 2: o "dado" é o convite
    conv = E.bloco(620, 300, BR, raio=30, ow=7, sombra=12).copy()
    d = ImageDraw.Draw(conv)
    d.text((310, 70), "ACERTOU? ENTÃO VEM:", font=E.fig(36, 900), fill=PET, anchor="mm")
    d.text((310, 150), "TARDE DE JOGOS", font=E.lilita(72), fill=LAR, anchor="mm", stroke_width=3, stroke_fill=MAR)
    d.text((310, 230), "no Becas Café · data em breve", font=E.fig(36, 800), fill=MAR, anchor="mm")
    E.cola(img, conv, W / 2, 1360, -2)
    E.cola(img, E.titulo("ERA A 2!", 140, AMA), W / 2, 480, 3)
    logo(img)
    return img


# ---------------------------------------------------------------- 3 6 HORAS EM 30 SEGUNDOS
def relogio(hh, mm, s=1.0):
    w = int(520 * s)
    im = E.bloco(w, int(w * 0.42), MAR, raio=int(40 * s), ow=7, sombra=12).copy()
    d = ImageDraw.Draw(im)
    d.text((w / 2, w * 0.21), f"{hh:02d}:{mm:02d}", font=E.lilita(int(170 * s)), fill=AMA, anchor="mm")
    return im


def etiqueta(txt, cor=AMA, fg=MAR):
    return E.pilula(txt, 46, cor, fg, fonte_titulo=True)


def horas_a():
    img = cheio(quadro_video(os.path.join(BRUTOS, "nov01", "085111.mp4"), 5))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle((0, 0, W, 520), fill=(0, 0, 0, 90))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(60)))
    E.cola(img, relogio(14, 7), W / 2, 330, -2)
    E.cola(img, etiqueta("14h: JÁ TEM DADO ROLANDO"), W / 2, 560, 2)
    E.cola(img, E.pilula("6 HORAS DE JOGO EM 30 SEGUNDOS", 34, BR, MAR), W / 2, 1520, -1)
    logo(img)
    return img


def horas_b():
    img = cheio(quadro_video(os.path.join(BRUTOS, "nov01b", "20261101_151657.mp4"), 20))
    E.cola(img, relogio(18, 59, 0.8), 280, 1000, 2)  # no peito, longe do rosto
    E.cola(img, etiqueta("18h59: \"SÓ MAIS UMA?\"", ROSA, BR), 330, 1160, -2)
    E.cola(img, E.titulo("TARDE DE JOGOS\nNO BECAS CAFÉ", 100, AMA), W / 2, 1480, -2)
    logo(img)
    return img


# ---------------------------------------------------------------- folha de comparação
def main():
    os.makedirs(OUT, exist_ok=True)
    cols = [("1  PARA DE ROLAR", [rolar_a(), rolar_b()]), ("2  JOGO DAS XÍCARAS", [xic_a(), xic_b()]),
            ("3  6 HORAS EM 30 S", [horas_a(), horas_b()])]
    tw, th = 360, 640
    sh = Image.new("RGB", (3 * (2 * tw + 20) + 40, th + 110), (255, 255, 255))
    d = ImageDraw.Draw(sh)
    for c, (nome, ims) in enumerate(cols):
        x0 = 20 + c * (2 * tw + 20)
        d.text((x0 + tw, 45), nome, font=E.lilita(52), fill=MAR, anchor="mm")
        for k, im in enumerate(ims):
            sh.paste(im.convert("RGB").resize((tw - 10, th - 18), Image.LANCZOS), (x0 + k * tw, 90))
    sh.save(os.path.join(OUT, "conceitos.jpg"), quality=90)
    os.remove(os.path.join(OUT, "_q.jpg"))
    print("ok")


if __name__ == "__main__":
    main()
