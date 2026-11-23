#!/usr/bin/env python3
"""Carrossel "QUAL JOGO LEVAR PRO NATAL?" (23/nov/2026, pedido dela: "se sua família tem muita briga... muita fofoca...
gosta muito de festa..."). Conceito MESA DA CEIA vista de cima: toalha xadrez vermelha, pisca-pisca no alto, cartão de
lugar com o "tipo de família", PRATO com a caixa oficial do jogo servida, talheres, bolinhas de Natal; embaixo o cartão
"LEVA:" com o porquê e a ficha do site. 1080x1350 + Stories (o último com espaço pro adesivo de link).
Jogos que não estavam no carrossel da confra (Hitster, Telma, Say my Name, Dixit, Flip 7, Mascarade e Tapalavras ficaram
de fora):
  briga → Passaporte Mundo (cooperativo) · fofoca → Spyfall · festa → Happy Salmon · criançada → Uga Buga ·
  quem rouba no jogo → Coup · só pensa na ceia → Sushi Go!

    /usr/bin/python3 natal_familia.py      # out/natal_familia/01..08.png + stories/
"""
import json
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
import estilo as E  # noqa: E402

OUT = os.path.join(ROOT, "out", "natal_familia")
W, H = 1080, 1350
MAR, PET, LAR, AMA, BR = E.MARROM, E.PETROLEO, E.LARANJA, E.AMARELO, E.BRANCO
VERM = (200, 36, 44)
VERDE = (34, 120, 70)
DOURADO = (232, 180, 60)
CREME = (255, 249, 236)
SITE = json.load(open(os.path.join(REPO, "comum", "dados", "acervo_site.json")))
AC = os.path.join(REPO, "hobby-reels", "assets", "acervo")

# (linha 1, linha 2 em destaque, jogo, nome no site, caixa, frase)
FAMILIAS = [
    ("SE SUA FAMÍLIA", "TEM MUITA BRIGA...", "PASSAPORTE MUNDO", "Passaporte Mundo",
     os.path.join(AC, "passaporte_mundo.png"),
     "É cooperativo: todo mundo no MESMO time, viajando pelo mundo. Hoje ninguém briga com ninguém."),
    ("SE SUA FAMÍLIA", "AMA UMA FOFOCA...", "SPYFALL", "Spyfall", os.path.join(AC, "spyfall.png"),
     "Um é o espião e ninguém sabe quem. Pergunta daqui, desconfia dali... fofoqueiro nasceu pra isso."),
    ("SE SUA FAMÍLIA", "É PURA FESTA...", "HAPPY SALMON", "Happy Salmon",
     os.path.join(REPO, "roleta-reels", "assets", "happy_salmon.png"),
     "Grita, bate a mão, troca de lugar: 2 minutos de barulho e risada. Vão pedir bis a noite toda."),
    ("SE SUA FAMÍLIA", "TEM MUITA CRIANÇA...", "UGA BUGA", "Uga Buga", os.path.join(AC, "uga_buga.png"),
     "Cada homem das cavernas ganha um nome maluco. Lembrou? Grita! A criançada ganha dos adultos fácil."),
    ("SE NA SUA FAMÍLIA", "TEM QUEM ROUBA NO JOGO...", "COUP", "Coup: Inquisition",
     os.path.join(AC, "coup_inquisition.png"),
     "Aqui mentir é a regra! Finalmente aquele tio do blefe vai jogar do jeito dele."),
    ("SE SUA FAMÍLIA", "SÓ PENSA NA CEIA...", "SUSHI GO!", "Sushi Go!",
     os.path.join(ROOT, "assets", "seu_perde", "sushi_go.png"),
     "Monte o melhor prato passando as cartas. Dá fome, mas é rapidinho: cabe antes da sobremesa."),
]


# ---------------------------------------------------------------- mesa
def toalha(w, h):
    """Toalha xadrez escocês VERMELHO E VERDE (pedido dela: "nos tons vermelho e verde")."""
    img = Image.new("RGBA", (w, h), (196, 32, 42, 255))
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    q = 200
    for x in range(-40, w + q, q):  # faixas verdes largas (verde puro; o cruzamento fica verde-escuro)
        d.rectangle((x, 0, x + 96, h), fill=(26, 120, 64, 255))
    for y in range(-40, h + q, q):
        d.rectangle((0, y, w, y + 96), fill=(26, 120, 64, 255))
    for x in range(-40, w + q, q):
        for y in range(-40, h + q, q):
            d.rectangle((x, y, x + 96, y + 96), fill=(14, 78, 42, 255))
    for x in range(-40, w + q, q):  # fios finos: escuro no meio do verde, dourado entre as faixas
        d.rectangle((x + 44, 0, x + 52, h), fill=(10, 50, 30, 150))
        d.rectangle((x + 146, 0, x + 150, h), fill=(240, 200, 90, 120))
    for y in range(-40, h + q, q):
        d.rectangle((0, y + 44, w, y + 52), fill=(10, 50, 30, 150))
        d.rectangle((0, y + 146, w, y + 150), fill=(240, 200, 90, 120))
    img.alpha_composite(lay)
    rnd = random.Random(3)
    d = ImageDraw.Draw(img)
    for _ in range(1400):  # trama do tecido
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        d.line((x, y, x + rnd.uniform(4, 10), y), fill=(255, 255, 255, 14), width=1)
    vin = Image.new("L", (w, h), 0)
    ImageDraw.Draw(vin).ellipse((-w * 0.3, -h * 0.2, w * 1.3, h * 1.2), fill=255)
    vin = vin.filter(ImageFilter.GaussianBlur(140))
    esc = Image.new("RGBA", (w, h), (40, 10, 12, 255))
    return Image.composite(img, esc, vin)


def luzes(img):
    """Pisca-pisca no alto (fio com 3 barrigas e lâmpadas acesas)."""
    w = img.width
    cores = [(226, 52, 52), (46, 160, 80), (255, 196, 40), (40, 140, 220), (240, 120, 200)]
    glow = Image.new("RGBA", (w, 170), (0, 0, 0, 0))
    lay = Image.new("RGBA", (w, 170), (0, 0, 0, 0))
    g, d = ImageDraw.Draw(glow), ImageDraw.Draw(lay)

    def fy(x):
        return 20 + 72 * math.sin(math.pi * ((x % 360) / 360))
    d.line([(x, fy(x)) for x in range(-10, w + 12, 6)], fill=(50, 70, 40, 255), width=4)
    for i, x in enumerate(range(22, w, 46)):
        y = fy(x) + 6
        c = cores[i % len(cores)]
        g.ellipse((x - 26, y - 6, x + 26, y + 46), fill=c + (160,))
        d.rectangle((x - 5, y - 4, x + 5, y + 6), fill=(70, 70, 60, 255))
        d.ellipse((x - 9, y + 4, x + 9, y + 30), fill=c + (255,), outline=MAR, width=2)
        d.ellipse((x - 4, y + 9, x + 1, y + 16), fill=(255, 255, 255, 200))
    glow = glow.filter(ImageFilter.GaussianBlur(10))
    glow.alpha_composite(lay)
    img.alpha_composite(glow)


def bola(r, cor):
    """Bolinha de Natal com brilho e o pino dourado."""
    s = int(r * 2 + 40)
    im = Image.new("RGBA", (s, s + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = s / 2, s / 2 + 26
    d.ellipse((cx - r + 8, cy - r + 10, cx + r + 8, cy + r + 10), fill=(60, 10, 12, 110))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=cor, outline=MAR, width=4)
    clara = tuple(min(255, int(c + (255 - c) * 0.55)) for c in cor)
    d.ellipse((cx - r * 0.55, cy - r * 0.6, cx - r * 0.1, cy - r * 0.2), fill=clara)
    d.rectangle((cx - r * 0.22, cy - r - 18, cx + r * 0.22, cy - r + 4), fill=DOURADO, outline=MAR, width=3)
    d.arc((cx - 10, cy - r - 36, cx + 10, cy - r - 14), 180, 360, fill=MAR, width=4)
    return im


def prato(r):
    s = int(r * 2 + 50)
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    sh = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((25 + 10, 25 + 16, 25 + 2 * r + 10, 25 + 2 * r + 16), fill=(70, 20, 20, 120))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    d = ImageDraw.Draw(im)
    c = s / 2
    d.ellipse((c - r, c - r, c + r, c + r), fill=(252, 252, 250), outline=(205, 200, 195), width=4)
    d.ellipse((c - r * 0.74, c - r * 0.74, c + r * 0.74, c + r * 0.74), fill=(244, 243, 240), outline=(220, 215, 210),
              width=3)
    d.arc((c - r * 0.88, c - r * 0.88, c + r * 0.88, c + r * 0.88), 200, 320, fill=DOURADO, width=5)
    d.arc((c - r * 0.88, c - r * 0.88, c + r * 0.88, c + r * 0.88), 20, 140, fill=DOURADO, width=5)
    return im


def talher(tipo, h):
    w = 70
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    prata, borda = (214, 218, 222), (120, 124, 130)
    cx = w / 2
    d.rounded_rectangle((cx - 10, h * 0.42, cx + 10, h - 6), 10, fill=prata, outline=borda, width=3)
    if tipo == "garfo":
        d.rounded_rectangle((cx - 22, h * 0.2, cx + 22, h * 0.46), 14, fill=prata, outline=borda, width=3)
        for k in (-15, -5, 5, 15):
            d.rounded_rectangle((cx + k - 3, 4, cx + k + 3, h * 0.3), 3, fill=prata, outline=borda, width=2)
    else:
        d.rounded_rectangle((cx - 16, 4, cx + 16, h * 0.46), 16, fill=prata, outline=borda, width=3)
    return im


def caixa(path, h, wmax=None):
    im = Image.open(path).convert("RGBA")
    im = im.crop(im.getbbox())
    s = h / im.height
    if wmax and im.width * s > wmax:
        s = wmax / im.width
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    sh = Image.new("RGBA", (im.width + 40, im.height + 40), (0, 0, 0, 0))
    sh.paste((60, 30, 20, 150), (14, 22), im.getchannel("A"))
    sh = sh.filter(ImageFilter.GaussianBlur(8))
    sh.alpha_composite(im, (6, 6))
    return sh


def cartao_lugar(l1, l2, w=900):
    """Cartão de lugar da ceia (dobrado, com raminho)."""
    h = 230
    c = E.bloco(w, h, CREME, raio=22, ow=6, sombra=12).copy()
    d = ImageDraw.Draw(c)
    d.line((40, 70, w - 40, 70), fill=(230, 210, 190), width=3)
    d.text((w / 2, 46), l1, font=E.lilita(44), fill=VERDE, anchor="mm")
    f = E.lilita(84)
    while d.textlength(l2, font=f) > w - 70:
        f = E.lilita(f.size - 4)
    d.text((w / 2, 150), l2, font=f, fill=VERM, anchor="mm", stroke_width=3, stroke_fill=MAR)
    for x in (34, w - 34):  # raminhos de azevinho
        for a in (-0.6, 0.6):
            d.ellipse((x - 18 + 14 * a, 14, x + 18 + 14 * a, 34), fill=VERDE)
        d.ellipse((x - 7, 22, x + 7, 36), fill=VERM)
    return c


def cartao_leva(jogo, site, frase, w=960):
    ficha = SITE[site]
    h = 330
    c = E.bloco(w, h, BR, raio=30, ow=7, sombra=12).copy()
    d = ImageDraw.Draw(c)
    d.text((40, 58), "LEVA:", font=E.lilita(54), fill=VERDE, anchor="lm")
    f = E.lilita(70)
    d.text((200, 58), jogo, font=f, fill=LAR, anchor="lm", stroke_width=4, stroke_fill=MAR)
    # frase quebrada em até 2 linhas
    fz = E.fig(34, 800)
    palavras, linhas, at = frase.split(), [], ""
    for p in palavras:
        t = (at + " " + p).strip()
        if d.textlength(t, font=fz) > w - 80:
            linhas.append(at)
            at = p
        else:
            at = t
    linhas.append(at)
    for k, l in enumerate(linhas[:3]):
        d.text((40, 116 + k * 44), l, font=fz, fill=MAR, anchor="lm")
    x = 40
    for txt, cor, fg in ((f"{ficha['jogadores'].replace('–', ' a ')} jogadores", PET, BR),
                         (ficha["tempo"].replace("min", " min"), AMA, MAR),
                         (f"R$ {ficha['preco']} · 5 dias", VERM, BR)):
        p = E.pilula(txt, 28, cor, fg, fonte_titulo=True)
        c.alpha_composite(p, (x, h - 74))
        x += p.width + 14
    return c


def base(seed=0):
    img = toalha(W, H).convert("RGBA")
    luzes(img)
    rnd = random.Random(seed)
    for (x, y) in ((70, 1230), (1010, 1180)):
        b = bola(rnd.randint(40, 52), rnd.choice([VERM, VERDE, DOURADO, (40, 110, 190)]))
        img.alpha_composite(b, (int(x - b.width / 2), int(y - b.height / 2)))
    return img


def tela_familia(k):
    l1, l2, jogo, site, path, frase = FAMILIAS[k]
    img = base(k)
    E.cola(img, cartao_lugar(l1, l2), W / 2, 280, (-1.5, 1.5)[k % 2], 1, 1)
    p = prato(300)
    img.alpha_composite(p, (int(W / 2 - p.width / 2), int(700 - p.height / 2)))
    E.cola(img, talher("garfo", 340), W / 2 - 400, 700, -4, 1, 1)
    E.cola(img, talher("faca", 340), W / 2 + 400, 700, 4, 1, 1)
    E.cola(img, caixa(path, 380, 400), W / 2, 690, (-4, 4)[k % 2], 1, 1)
    E.cola(img, cartao_leva(jogo, site, frase), W / 2, 1150, 0, 1, 1)
    return img.convert("RGB")


def tela_capa():
    img = base(9)
    E.cola(img, E.titulo("QUAL JOGO\nLEVAR PRO\nNATAL?", 128, BR, larg_max=980), W / 2, 420, -2, 1, 1)
    E.cola(img, E.pilula("depende da sua família...", 46, CREME, MAR, fonte_titulo=True), W / 2, 680, 1, 1, 1)
    for k, (x, y, r) in enumerate(((240, 990, -8), (540, 1020, 3), (840, 990, 8))):
        p = prato(170)
        img.alpha_composite(p, (int(x - p.width / 2), int(y - p.height / 2)))
        E.cola(img, caixa(FAMILIAS[[0, 2, 1][k]][4], 220, 230), x, y - 8, r, 1, 1)
    E.cola(img, E.pilula("ARRASTA E ACHA A SUA!", 38, VERDE, BR, fonte_titulo=True), W / 2, 1250, -1, 1, 1)
    return img.convert("RGB")


def tela_final():
    img = base(11)
    E.cola(img, E.logo(240), W / 2, 330, 0, 1, 1)
    E.cola(img, E.titulo("ALUGA E LEVA\nPRA CEIA!", 120, BR, larg_max=980), W / 2, 590, -2, 1, 1)
    c = E.bloco(900, 330, CREME, raio=34, ow=7, sombra=12).copy()
    d = ImageDraw.Draw(c)
    for k, t in enumerate(("Retire em Mauá ou receba em casa", "5 dias de jogo pra curtir o feriado",
                           "Reserve pelo link na bio")):
        y = 70 + k * 95
        d.ellipse((40, y - 26, 92, y + 26), fill=(VERM, VERDE, LAR)[k], outline=MAR, width=4)
        d.text((66, y + 1), str(k + 1), font=E.lilita(36), fill=BR, anchor="mm")
        d.text((120, y), t, font=E.fig(38, 900), fill=MAR, anchor="lm")
    E.cola(img, c, W / 2, 930, 1, 1, 1)
    E.cola(img, E.pilula("Marca aqui a sua família!", 42, AMA, MAR, fonte_titulo=True), W / 2, 1170, -1, 1, 1)
    E.cola(img, E.pilula("@suavez_bg", 34, BR, MAR, fonte_titulo=True), W / 2, 1255, 0, 1, 1)
    return img.convert("RGB")


def story_de(tela, ultima=False):
    st = toalha(W, 1920).convert("RGBA")
    luzes(st)
    st.alpha_composite(tela.convert("RGBA"), (0, 285 if not ultima else 170))
    if ultima:
        d = ImageDraw.Draw(st)
        E.cola(st, E.pilula("aluga aqui:", 42, CREME, MAR, fonte_titulo=True), W / 2, 1570, 0, 1, 1)
        seta = Image.new("RGBA", (120, 140), (0, 0, 0, 0))
        sd = ImageDraw.Draw(seta)
        pts = [(42, 0), (78, 0), (78, 70), (112, 70), (60, 136), (8, 70), (42, 70)]
        sd.polygon(pts, fill=AMA)
        sd.line(pts + [pts[0]], fill=MAR, width=6)
        E.cola(st, seta, W / 2, 1670, 0, 0.5, 1)
        del d
    return st.convert("RGB")


def main():
    os.makedirs(os.path.join(OUT, "stories"), exist_ok=True)
    telas = [tela_capa()] + [tela_familia(k) for k in range(len(FAMILIAS))] + [tela_final()]
    for k, im in enumerate(telas):
        im.save(os.path.join(OUT, f"{k + 1:02d}.png"))
        story_de(im, k == len(telas) - 1).save(os.path.join(OUT, "stories", f"story_{k + 1:02d}.png"))
    sh = Image.new("RGB", (len(telas) * 300, 375), "white")
    for k, im in enumerate(telas):
        sh.paste(im.resize((300, 375)), (k * 300, 0))
    sh.save(os.path.join(OUT, "previa.jpg"), quality=88)
    print("ok", OUT)


if __name__ == "__main__":
    main()
