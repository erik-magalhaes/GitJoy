#!/usr/bin/env python3
"""Stories "QUAL É O PLANO PRO FIM DE SEMANA?" + RECEITA de um jogo pra cada plano (6/nov/2026, ideia dele).

Story 1: a pergunta + espaço LIVRE no meio (y≈930–1400) para a ENQUETE do Instagram (máx. 4 opções).
Stories seguintes: conceito RECEITA MÉDICA ("Dr. Sua Vez, especialista em fim de semana sem tédio"): papel de receituário
com "Rx", a caixa OFICIAL, ficha do site, "modo de usar", "efeito colateral" e carimbo. 6 planos para ele escolher 4.

    /usr/bin/python3 promo/story_plano_fds.py      # promo/out/plano_fds/*.png + previa.jpg
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
import estilo as E  # noqa: E402
from estilo import MARROM, PETROLEO, LARANJA, AMARELO, BRANCO  # noqa: E402

W, H = 1080, 1920
OUT = os.path.join(REPO, "promo", "out", "plano_fds")
R = lambda *p: os.path.join(REPO, *p)  # noqa: E731
ROSA, VERDE, ROXO = (236, 106, 140), (86, 164, 104), (108, 63, 160)
PAPEL = (255, 252, 244)

PLANOS = [  # (arquivo, plano, cor, jogo, caixa, ficha, modo de usar, efeito colateral)
    ("1_familia", "ALMOÇO EM FAMÍLIA", LARANJA, "Uga Buga", R("hobby-reels/assets/acervo/uga_buga.png"),
     "3 A 8 PESSOAS · 15 MIN",
     "Depois da sobremesa e antes do tio puxar assunto de política.",
     "A vó rindo alto e pedindo mais uma rodada."),
    ("2_date", "DATE COM O MOZÃO", ROSA, "boop.", R("gravados-reels/assets/lista/boop.png"),
     "2 PESSOAS · 30 MIN",
     "Uma partida antes do filme. Ou no lugar dele.",
     "Pedido de revanche até meia-noite."),
    ("3_galera", "ROLÊ COM A GALERA", ROXO, "Hitster", R("hobby-reels/assets/acervo/hitster.png"),
     "2 A 10 PESSOAS · 30 MIN",
     "Toca a música, todo mundo chuta o ano e monta a sua linha do tempo.",
     "A galera cantando junto e jurando que essa música é de 2005."),
    ("4_em_casa", "FICAR DE BOA EM CASA", PETROLEO, "Canvas", R("hobby-reels/assets/acervo/canvas.png"),
     "1 A 5 PESSOAS · 30 MIN",
     "Café passado, mesa limpa e quadros pintados sem sujar a mão.",
     "Vontade de emoldurar a partida."),
    ("5_empresa", "FESTA DA EMPRESA", VERDE, "Código Secreto: Imagens",
     R("hobby-reels/assets/caixas/c_digo_secreto_imagens.png"), "2 A 8 PESSOAS · 15 MIN",
     "Divide em dois times e esquece o crachá.",
     "O estagiário virando o herói da festa."),
    ("6_sogra", "VISITA NA SOGRA", AMARELO, "Take Time", R("hobby-reels/assets/acervo/take_time.png"),
     "2 A 4 PESSOAS · 30 MIN",
     "Jogo cooperativo: todo mundo no mesmo time, ninguém ganha da sogra.",
     "Convite pro almoço do próximo domingo."),
]


def escurece(c, k=0.82):
    return tuple(int(v * k) for v in c)


def fundo(cor, semente=1):
    """Cor lisa com cruzinhas de farmácia e comprimidos espalhados (receita)."""
    img = Image.new("RGBA", (W, H), cor + (255,))
    d = ImageDraw.Draw(img)
    rnd = random.Random(semente)
    clara = tuple(min(255, int(v + (255 - v) * 0.18)) for v in cor)
    for y in range(60, H, 150):
        for x in range(60 + (75 if (y // 150) % 2 else 0), W + 80, 150):
            if rnd.random() < 0.5:  # cruz
                d.rounded_rectangle((x - 22, y - 7, x + 22, y + 7), 4, fill=clara)
                d.rounded_rectangle((x - 7, y - 22, x + 7, y + 22), 4, fill=clara)
            else:  # comprimido
                a = rnd.uniform(0, math.pi)
                p = Image.new("RGBA", (70, 30), (0, 0, 0, 0))
                ImageDraw.Draw(p).rounded_rectangle((0, 0, 69, 29), 15, fill=clara)
                p = p.rotate(math.degrees(a), expand=True, resample=Image.BICUBIC)
                img.alpha_composite(p, (int(x - p.width / 2), int(y - p.height / 2)))
    return img


def seta(cor=MARROM, h=120):
    im = Image.new("RGBA", (110, h + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.line((55, 5, 55, h - 40), fill=cor, width=16)
    d.polygon([(10, h - 55), (100, h - 55), (55, h)], fill=cor)
    return im


def carimbo(txt, cor=(200, 40, 50)):
    f = E.lilita(46)
    tw = E._larg(txt, f)
    w, h = int(tw + 70), 110
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((4, 4, w - 4, h - 4), 22, outline=cor + (220,), width=7)
    d.rounded_rectangle((16, 16, w - 16, h - 16), 14, outline=cor + (150,), width=3)
    d.text((w / 2, h / 2 + 2), txt, font=f, fill=cor + (225,), anchor="mm")
    return im.rotate(-9, expand=True, resample=Image.BICUBIC)


def pergunta():
    img = fundo(PETROLEO, 7)
    E.cola(img, E.logo(300), W / 2, 250, -2)
    E.cola(img, E.titulo("E AÍ, QUAL É O\nPLANO PRO FIM\nDE SEMANA?", 116, BRANCO, larg_max=W - 110), W / 2, 590, -2)
    E.cola(img, E.pilula("VOTA AQUI EMBAIXO", 46, AMARELO, MARROM, fonte_titulo=True), W / 2 - 50, 845, 2)
    E.cola(img, seta(AMARELO), W / 2 + 270, 850)
    # y≈930–1400 fica LIVRE para a enquete
    card = E.bloco(900, 230, PAPEL, raio=34, ow=7, sombra=12)
    d = ImageDraw.Draw(card)
    d.text((95, 115), "Rx", font=E.lilita(110), fill=PETROLEO, anchor="mm")
    tx = E.texto("No próximo story, a gente RECEITA um jogo pra cada plano!", 42, MARROM, 800, larg_max=640, entre=1.3)
    card.alpha_composite(tx, (int(535 - tx.width / 2), int(115 - tx.height / 2)))
    E.cola(img, card, W / 2, 1510, 1.5)
    return img


def receita(plano, cor, nome, caixa, ficha, modo, efeito, semente):
    img = fundo(cor, semente)
    claro = cor in (AMARELO,)
    E.cola(img, E.logo(230), W / 2, 210, -2)
    E.cola(img, E.titulo("O SEU PLANO PEDE...", 70, BRANCO if not claro else PETROLEO, larg_max=W - 120), W / 2, 345, -1)
    pw, ph, x0, y0 = 920, 1170, 80, 420
    papel = E.bloco(pw, ph, PAPEL, raio=30, ow=7, sombra=14)
    d = ImageDraw.Draw(papel)
    for y in range(330, ph - 40, 58):  # pauta clarinha
        d.line((40, y, pw - 40, y), fill=(238, 232, 220), width=2)
    d.text((50, 70), "RECEITA", font=E.lilita(64), fill=PETROLEO, anchor="lm")
    d.text((pw - 50, 58), "Dr. Sua Vez", font=E.fig(34, 900), fill=MARROM, anchor="rm")
    d.text((pw - 50, 98), "especialista em fim de semana sem tédio", font=E.fig(24, 600), fill=MARROM, anchor="rm")
    d.line((40, 140, pw - 40, 140), fill=MARROM, width=5)
    d.text((50, 200), "Para quem vai:", font=E.fig(32, 700), fill=MARROM, anchor="lm")
    pl = E.pilula(plano, 40, cor, BRANCO if not claro else MARROM, fonte_titulo=True)
    papel.alpha_composite(pl, (int(pw - 45 - pl.width), int(200 - pl.height / 2)))
    # Rx + caixa
    d.text((140, 400), "Rx", font=E.lilita(150), fill=escurece(cor, 0.9) if not claro else LARANJA, anchor="mm")
    cx = E.jogo(caixa, 290, larg=400)
    papel.alpha_composite(cx, (int(560 - cx.width / 2), int(405 - cx.height / 2)))
    nm = E.titulo(nome, 78, cor if not claro else LARANJA, larg_max=pw - 100)
    papel.alpha_composite(nm, (int(pw / 2 - nm.width / 2), int(615 - nm.height / 2)))
    fc = E.pilula(ficha, 32, AMARELO if cor != AMARELO else PETROLEO, MARROM if cor != AMARELO else BRANCO)
    papel.alpha_composite(fc, (int(pw / 2 - fc.width / 2), int(700 - fc.height / 2)))
    y = 765
    for rot, txt in (("Modo de usar:", modo), ("Efeito colateral:", efeito)):
        d.text((50, y), rot, font=E.fig(36, 900), fill=PETROLEO, anchor="lm")
        t = E.texto(txt, 36, MARROM, 600, larg_max=pw - 110, alinha="lm", entre=1.25)
        papel.alpha_composite(t, (45, int(y + 26)))
        y += 30 + t.height + 18
    d.text((50, ph - 60), "assinado: Dr. Sua Vez", font=E.fig(26, 600), fill=MARROM, anchor="lm")
    img.alpha_composite(papel, (x0, y0))
    E.cola(img, carimbo("RECEITADO!"), x0 + pw - 190, y0 + ph - 80)
    E.cola(img, E.pilula("ALUGA NO LINK DA BIO · @SUAVEZ_BG", 36, BRANCO, MARROM, fonte_titulo=True), W / 2, 1680, -1)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    telas = [("0_pergunta", pergunta())]
    for k, (arq, plano, cor, nome, caixa, ficha, modo, efeito) in enumerate(PLANOS):
        telas.append((arq, receita(plano, cor, nome, caixa, ficha, modo, efeito, k + 2)))
    for arq, im in telas:
        im.convert("RGB").save(os.path.join(OUT, f"story_{arq}.png"))
    w = 360
    h = int(w * H / W)
    sh = Image.new("RGB", (4 * w + 50, 2 * h + 30), (240, 236, 228))
    for k, (_, im) in enumerate(telas):
        sh.paste(im.convert("RGB").resize((w, h), Image.LANCZOS), (10 + (k % 4) * (w + 10), 10 + (k // 4) * (h + 10)))
    sh.save(os.path.join(OUT, "previa.jpg"), quality=88)
    print("ok", OUT)


if __name__ == "__main__":
    main()
