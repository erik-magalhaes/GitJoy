#!/usr/bin/env python3
"""Carrossel "SEU MÊS, SEU JOGO" (31/out/2026), na trend "Seu mês, seu bichinho" que ele mandou (@hippieartesanatos):
capa com os 12 jogos em volta do título, uma tela por mês (papel pastel, letra de mão em caixa alta, a caixa do jogo no
meio e uma frase com o "personagem" do jogo no clima do mês) e uma tela final pra comentar.
Caixas recortadas do site (hobby-reels/assets/acervo/); letra = Patrick Hand engrossada (como em taco-reels).
1080x1350.

    python3 seu_mes.py            # out/seu_mes/01..14.png + out/seu_mes_previa.jpg + out/carrossel_seu_mes.zip
    python3 seu_mes.py --previa   # só capa + 3 meses na folha de prévia
"""
import os
import random
import sys
import zipfile
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
import estilo as E  # noqa: E402

W, H = 1080, 1350
OUT = os.path.join(ROOT, "out")
ACERVO = os.path.join(REPO, "hobby-reels", "assets", "acervo")
MAO = os.path.join(REPO, "taco-reels", "assets", "fonts", "PatrickHand-Regular.ttf")
TINTA = (34, 30, 30)
MESES = [  # (mês, frase, jogo, recorte, fundo pastel)
    ("JANEIRO", "GATO ASTRONAUTA\nDE FÉRIAS NA LUA", "MLEM: Agência Espacial", "mlem_space_agency", (198, 214, 240)),
    ("FEVEREIRO", "UNICÓRNIO QUE SÓ\nPENSA EM CARNAVAL", "Unicorn Fever", "unicorn_fever", (246, 204, 222)),
    ("MARÇO", "BICHINHO DA FLORESTA\nFAZENDO PLANILHA DO ANO", "Everdell Duo", "everdell_duo", (214, 234, 200)),
    ("ABRIL", "XERIFE QUE FINGE\nQUE ACREDITA", "Sheriff of Nottingham", "sheriff_of_nottingham_2nd_edition",
     (250, 226, 190)),
    ("MAIO", "CHEF ESTRESSADO\nNO DIA DAS MÃES", "Critter Kitchen", "critter_kitchen", (228, 214, 244)),
    ("JUNHO", "FAZENDEIRO\nDE QUADRILHA", "La Granja", "la_granja", (252, 214, 196)),
    ("JULHO", "TURISTA PERDIDO\nNO METRÔ DE LONDRES", "Next Station London", "next_station_london",
     (204, 230, 236)),
    ("AGOSTO", "CHEFÃO DE MASMORRA\nNO MÊS DO DESGOSTO", "Boss Monster", "boss_monster_the_dungeon_building_card_game",
     (236, 220, 206)),
    ("SETEMBRO", "PASSARINHO\nESPERANDO A PRIMAVERA", "Wingspan", "wingspan", (220, 238, 214)),
    ("OUTUBRO", "SUPER-HERÓI ZUMBI\nBATENDO PONTO", "DCeased", "dceased_gotham_city_outbreak", (214, 206, 232)),
    ("NOVEMBRO", "BANDIDO\nDE BLACK FRIDAY", "Bad Company", "bad_company", (244, 232, 204)),
    ("DEZEMBRO", "DRAGÃO CONFEITEIRO\nNO TURNO DO NATAL", "Flamecraft", "flamecraft", (250, 210, 210)),
]


@lru_cache(None)
def mao(s):
    return ImageFont.truetype(MAO, int(s))


def papel(cor, semente=1):
    """Papel pastel com grão e fibra leve."""
    rng = np.random.default_rng(semente)
    a = np.ones((H, W, 3)) * np.array(cor, float)
    g = rng.normal(0, 1, (H // 3, W // 3))
    g = np.asarray(Image.fromarray(((g + 4) * 30).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC),
                   float) / 30 - 4
    a += g[..., None] * 2.2
    a += rng.normal(0, 2.0, (H, W, 1))
    return Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert("RGBA")


def letra(img, txt, s, cx, cy, cor=TINTA, sw=None, entre=1.12, semente=0):
    """Letra de mão em caixa alta: cada letra com tamanho/altura/giro levemente diferentes, traço engrossado."""
    rnd = random.Random(semente)
    sw = max(1, int(s * 0.045)) if sw is None else sw
    f = mao(s)
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    linhas = txt.split("\n")
    lh = s * entre
    y0 = cy - lh * (len(linhas) - 1) / 2
    for k, l in enumerate(linhas):
        larg = [d0.textlength(c, font=f) * 1.04 for c in l]
        x = cx - sum(larg) / 2
        for c, lw in zip(l, larg):
            if c != " ":
                ss = s * rnd.uniform(0.95, 1.05)
                g = Image.new("RGBA", (int(ss * 1.6), int(ss * 1.6)), (0, 0, 0, 0))
                ImageDraw.Draw(g).text((g.width / 2, g.height / 2), c, font=mao(ss), fill=cor, anchor="mm",
                                       stroke_width=sw, stroke_fill=cor)
                g = g.rotate(rnd.uniform(-3.5, 3.5), resample=Image.BICUBIC)
                img.alpha_composite(g, (int(x + lw / 2 - g.width / 2), int(y0 + k * lh - g.height / 2 +
                                                                              rnd.uniform(-3, 3))))
            x += lw


@lru_cache(None)
def caixa(nome, h, larg=None):
    im = Image.open(os.path.join(ACERVO, nome + ".png")).convert("RGBA")
    im = im.crop(im.getbbox())
    s = h / im.height
    if larg and im.width * s > larg:
        s = larg / im.width
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    sh = Image.new("RGBA", (im.width + 80, im.height + 80), (0, 0, 0, 0))
    m = Image.new("RGBA", im.size, (40, 30, 30, 255))
    m.putalpha(im.getchannel("A").point(lambda v: int(v * 0.32)))
    sh.alpha_composite(m, (52, 58))
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    sh.alpha_composite(im, (40, 40))
    return sh


def selo(img, x, y, w=170):
    lg = E.logo(w)
    img.alpha_composite(lg, (int(x), int(y)))


def tela_mes(k):
    mes, frase, jogo, rec, cor = MESES[k]
    img = papel(cor, k + 3)
    letra(img, mes, 110, W / 2, 175, semente=k)
    cx = caixa(rec, 560, 600)
    img.alpha_composite(cx, (int(W / 2 - cx.width / 2), int(670 - cx.height / 2)))
    letra(img, frase, 74, W / 2, 1075, semente=k + 50)
    letra(img, "jogo: " + jogo, 40, W / 2, 1215, (80, 70, 70), sw=1, semente=k + 90)
    selo(img, 34, H - 128, 150)
    return img


def tela_capa():
    img = papel((246, 206, 196), 99)
    letra(img, "SEU MÊS,\nSEU JOGO", 128, W / 2, 610, semente=7)
    letra(img, "(qual é o seu?)", 60, W / 2, 800, (90, 70, 70), sw=2, semente=8)
    # as 12 caixas em volta do título (sentido horário, começando em janeiro no alto à esquerda)
    pos = [(170, 175), (430, 150), (690, 160), (930, 230), (950, 520), (960, 820), (900, 1120), (640, 1180),
           (380, 1190), (140, 1110), (120, 820), (130, 500)]
    for k, ((x, y), m) in enumerate(zip(pos, MESES)):
        cx = caixa(m[3], 200, 210)
        cx = cx.rotate(random.Random(k).uniform(-8, 8), expand=True, resample=Image.BICUBIC)
        img.alpha_composite(cx, (int(x - cx.width / 2), int(y - cx.height / 2)))
    selo(img, W / 2 - 85, 905, 170)
    return img


def tela_final():
    img = papel((210, 228, 240), 77)
    letra(img, "E AÍ,\nQUAL É O SEU MÊS?", 100, W / 2, 380, semente=3)
    letra(img, "comenta aqui\ne marca quem é do seu mês!", 58, W / 2, 640, (90, 70, 70), sw=2, semente=4)
    lg = E.logo(330)
    img.alpha_composite(lg, (int(W / 2 - lg.width / 2), 820))
    letra(img, "ALUGA O SEU NA SUA VEZ\nO LINK TÁ NA BIO", 56, W / 2, 1150, semente=5)
    return img


def main():
    d = os.path.join(OUT, "seu_mes")
    os.makedirs(d, exist_ok=True)
    previa = "--previa" in sys.argv
    telas = [tela_capa()] + [tela_mes(k) for k in (range(12) if not previa else (0, 3, 11))]
    if not previa:
        telas.append(tela_final())
    for k, im in enumerate(telas, 1):
        im.convert("RGB").save(os.path.join(d, f"{k:02d}.png"))
    cols = min(len(telas), 7)
    rows = (len(telas) + cols - 1) // cols
    sh = Image.new("RGB", (cols * 330 + 10, rows * 420 + 10), (255, 255, 255))
    for k, im in enumerate(telas):
        sh.paste(im.convert("RGB").resize((320, 400), Image.LANCZOS), (10 + (k % cols) * 330, 10 + (k // cols) * 420))
    sh.save(os.path.join(OUT, "seu_mes_previa.jpg"), quality=90)
    if not previa:
        with zipfile.ZipFile(os.path.join(OUT, "carrossel_seu_mes.zip"), "w") as z:
            for k in range(1, len(telas) + 1):
                z.write(os.path.join(d, f"{k:02d}.png"), f"seu_mes_{k:02d}.png")
    print("ok", len(telas))


if __name__ == "__main__":
    main()
