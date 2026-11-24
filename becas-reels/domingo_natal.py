#!/usr/bin/env python3
"""Carrossel de FIM DE ANO do Domingo de Jogos (22/nov/2026, ele: "é dezembro e não tem nada de Natal, Ano Novo, amigo
secreto"). Ângulo: o Domingo de Jogos (13/12) como a CONFRA de fim de ano da turma, inclusive pra fazer o amigo secreto.
Mesmo fundo de Natal do `domingo.py` (guarda-chuvinhas + pisca-pisca + estrelinhas), presentes desenhados só como
enfeite, caixas OFICIAIS do acervo e fotos REAIS da tarde de 20/11 e do Beca’s.

    /usr/bin/python3 domingo_natal.py      # out/domingo_natal/01..07.png + stories/
"""
import math
import os
import random

from PIL import Image, ImageDraw

import domingo as D
import domingo_mais as M
import domingo_carrossel as DC
from tarde import E, TB, W, MAR, PET, LAR, AMA, BR, ROSA

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
PASTA = os.path.join(D.OUT, "domingo_natal")
CW, CH = 1080, 1350
VERM, VERDE = D.VERM, (24, 110, 66)
ACERVO = os.path.join(REPO, "hobby-reels", "assets", "acervo")
CAIXAS = [os.path.join(ACERVO, f) for f in ("hitster.png", "telma.png", "say_my_name.png", "dixit.png",
                                            "mascarade_second_edition.png", "tapalavras.png")]
CAIXAS.insert(4, os.path.join(REPO, "gravados-reels", "assets", "top10", "flip_7_a_vinganca.png"))


def presente(w, cor, fita, seed=0):
    """Presente embrulhado (enfeite): papel com bolinhas, fita cruzada e laço."""
    h = int(w * 0.82)
    im = Image.new("RGBA", (w + 40, h + 90), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x0, y0 = 20, 70
    d.rectangle((x0 + 10, y0 + 10, x0 + w + 10, y0 + h + 10), fill=MAR)
    d.rectangle((x0, y0, x0 + w, y0 + h), fill=cor, outline=MAR, width=5)
    rnd = random.Random(seed)
    clara = tuple(min(255, int(c + (255 - c) * 0.45)) for c in cor)
    for _ in range(int(w * h / 1800)):
        x, y = rnd.uniform(x0 + 10, x0 + w - 10), rnd.uniform(y0 + 10, y0 + h - 10)
        d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=clara)
    cx = x0 + w / 2
    fw = max(14, w // 9)
    d.rectangle((cx - fw / 2, y0, cx + fw / 2, y0 + h), fill=fita, outline=MAR, width=3)
    d.rectangle((x0, y0 + h * 0.42 - fw / 2, x0 + w, y0 + h * 0.42 + fw / 2), fill=fita, outline=MAR, width=3)
    r = w * 0.2
    for s in (-1, 1):
        d.ellipse((cx + s * r * 0.1 - r if s < 0 else cx + s * r * 0.1, y0 - r * 0.75, cx + s * r * 0.1 if s < 0
                   else cx + s * r * 0.1 + r, y0 + r * 0.25), fill=fita, outline=MAR, width=4)
    d.ellipse((cx - fw * 0.7, y0 - fw * 0.6, cx + fw * 0.7, y0 + fw * 0.6), fill=fita, outline=MAR, width=4)
    return im


def caixa(path, h):
    im = Image.open(path).convert("RGBA")
    im = im.crop(im.getbbox())
    return im.resize((int(im.width * h / im.height), h), Image.LANCZOS)


def base(seed=3.0):
    return DC.base()   # fundo parado vermelho natalino (o mesmo do carrossel "vai ter mais um")


def papelzinho(txt1, txt2, w=520):
    """Papelzinho do sorteio do amigo secreto."""
    h = 300
    p = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(p)
    d.rectangle((14, 14, w + 14, h + 14), fill=MAR)
    d.rectangle((0, 0, w, h), fill=(255, 252, 240), outline=MAR, width=5)
    for y in range(80, h - 20, 46):
        d.line((30, y, w - 30, y), fill=(190, 210, 230), width=2)
    d.text((w / 2, 60), txt1, font=E.fig(40, 800), fill=MAR, anchor="mm")
    d.text((w / 2, 180), txt2, font=E.lilita(110), fill=VERM, anchor="mm")
    return p


def t_capa():
    img = base(2.2)
    for x, y, w, cor, fita, rot in ((200, 1020, 260, VERDE, AMA, -8), (540, 1060, 300, AMA, VERDE, 3),
                                    (875, 1010, 250, PET, AMA, 7)):
        E.cola(img, presente(w, cor, fita, x), x, y, rot, 1, 1)
    E.cola(img, E.titulo("A CONFRA DE\nFIM DE ANO\nDA SUA TURMA", 104, LAR), 540, 530, -2, 1, 1)
    E.cola(img, E.pilula(f"É NO DOMINGO DE JOGOS · {D.DATA.split(', ')[-1]}", 40, PET, BR, fonte_titulo=True), 540,
           790, 1, 1, 1)
    E.cola(img, E.pilula("ARRASTA PRO LADO!", 34, AMA, MAR, fonte_titulo=True), 540, 1285, -1, 1, 1)
    return img.convert("RGB")


def t_amigo():
    img = base(2.6)
    E.cola(img, E.titulo("AMIGO SECRETO?\nFAZ NA MESA!", 104, LAR), 540, 440, -2, 1, 1)
    E.cola(img, papelzinho("você tirou:", "???"), 380, 800, -6, 1, 1)
    E.cola(img, presente(240, VERDE, AMA, 5), 840, 830, 8, 1, 1)
    E.cola(img, E.pilula("Sorteia no grupo e traz os presentes:", 36, BR, MAR), 540, 1105, 1, 1, 1)
    E.cola(img, E.pilula("a troca rola entre uma partida e outra!", 36, BR, MAR), 540, 1180, -1, 1, 1)
    return img.convert("RGB")


def t_jogos():
    img = base(3.1)
    E.cola(img, E.titulo("JOGO DE FESTA\nPRO GRUPO TODO", 100, LAR), 540, 440, -2, 1, 1)
    pos = [(195, 720, -5), (425, 705, 2), (655, 720, -3), (885, 705, 4), (310, 950, 3), (540, 965, -2), (770, 950, 4)]
    for (x, y, r), p in zip(pos, CAIXAS):
        E.cola(img, caixa(p, 240), x, y, r, 1, 1)
    E.cola(img, E.pilula("Hitster, Telma, Say my Name, Dixit, Flip 7, Mascarade...", 32, BR, MAR), 540, 1140, 1, 1, 1)
    E.cola(img, E.pilula("e a gente ensina tudo na hora!", 36, PET, BR, fonte_titulo=True), 540, 1215, -1, 1, 1)
    return img.convert("RGB")


def t_foto(arq, seg, leg, titulo, texto, ay=0.5, seed=3.0, rot=-3):
    img = base(seed)
    E.cola(img, E.titulo(titulo, 96, LAR), 540, 420, -2, 1, 1)
    p = M.polaroide(arq, seg, 760, 560, leg, ay)
    E.cola(img, p, 540, 870, rot, 1, 1)
    M.fita(img, 540, 870 - p.height / 2 + 8, rot + 4)
    E.cola(img, E.pilula(texto, 32, BR, MAR), 540, 1250, 1, 1, 1)
    return img.convert("RGB")


def t_turma():
    img = base(3.6)
    E.cola(img, E.titulo("VEM COM\nA TURMA TODA", 104, LAR), 540, 440, -2, 1, 1)
    E.cola(img, D.painel(0), 540, 830, 0, 0.66, 1)
    E.cola(img, E.titulo("SÓ 30 VAGAS!", 96, AMA), 540, 1140, 2, 1, 1)
    E.cola(img, E.pilula("Junta a galera e garante as vagas de todo mundo de uma vez.", 30, BR, MAR), 540, 1250, -1, 1,
           1)
    return img.convert("RGB")


def t_final():
    img = base(4.0)
    E.cola(img, TB.parceria(90), 540, 330, 0, 1, 1)
    E.cola(img, D.selo_fim_de_ano(40), 540, 450, -1, 1, 1)
    E.cola(img, D.card(), 540, 800, 0, 0.92, 1)
    E.cola(img, E.pilula("RESERVE PELO LINK NA BIO", 38, PET, BR, fonte_titulo=True), 540, 1130, -1, 1, 1)
    E.cola(img, E.pilula("Marca aqui quem tem que vir na sua confra!", 34, BR, MAR), 540, 1215, 1, 1, 1)
    return img.convert("RGB")


TELAS = [t_capa, t_amigo, t_jogos,
         lambda: t_foto(os.path.join(M.NOV06, "20261106_151311.mp4"), 1.6, "o bolo nuvem do Beca’s",
                        "O LANCHE DA CONFRA", "R$ 25 do ingresso viram consumação no café: é só escolher!", seed=2.9),
         lambda: t_foto(M.DIA, 13.5, "a tarde de 20/11", "FECHA O ANO JOGANDO",
                        "Uma tarde pra rir, competir e conhecer gente nova antes das festas.", ay=0.3, seed=3.4, rot=3),
         t_turma, t_final]


def main():
    os.makedirs(os.path.join(PASTA, "stories"), exist_ok=True)
    ims = [f() for f in TELAS]
    for k, im in enumerate(ims):
        im.save(os.path.join(PASTA, f"{k + 1:02d}.png"))
        DC.story_de(im, k == len(ims) - 1).save(os.path.join(PASTA, "stories", f"story_{k + 1:02d}.png"))
    sh = Image.new("RGB", (len(ims) * 340, 425), "white")
    for k, im in enumerate(ims):
        sh.paste(im.resize((340, 425)), (k * 340, 0))
    sh.save(os.path.join(PASTA, "previa.jpg"), quality=88)
    print("ok", PASTA)


if __name__ == "__main__":
    main()
