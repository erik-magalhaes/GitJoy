#!/usr/bin/env python3
"""Stories "QUAL É O PLANO PRO FIM DE SEMANA?" + um jogo indicado para cada plano (6/nov/2026, ideia dele).

Story 1: a pergunta + espaço LIVRE no meio (y≈930–1400) para a ENQUETE do Instagram (4 opções).
Stories seguintes (um por plano): fundo de cor com confete, "SEU PLANO:" + o plano, cartão branco com a caixa OFICIAL,
nome, ficha do site e UMA frase; embaixo "RESERVA ESSE JOGO AQUI:" + seta e espaço LIVRE y≈1255–1490 para o adesivo de
LINK do jogo no site. 2ª rodada (pedido dele): a 1ª versão era uma "receita médica" (ele não gostou e achou informação
demais), o link ficava baixo demais (y≈1650–1790), saiu o "ficar de boa em casa" (Canvas) e o jogo da família trocou
(Uga Buga → Dixit → Dixit: Disney Edition, pedido dele). Ficaram 4 planos (a "visita na sogra" com Take Time também saiu).

    /usr/bin/python3 promo/story_plano_fds.py      # promo/out/plano_fds/*.png + previa.jpg
"""
import os
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
LIVRE = (0, 1255, W, 1490)  # adesivo de link

PLANOS = [  # (arquivo, plano, cor, jogo, caixa, ficha, frase)
    ("1_familia", "ALMOÇO EM FAMÍLIA", LARANJA, "Dixit Disney", R("hobby-reels/assets/acervo/dixit_disney_edition.png"),
     "3 A 6 PESSOAS · 30 MIN", "Uma imagem, uma dica e a família inteira tentando adivinhar."),
    ("2_date", "DATE COM O MOZÃO", ROSA, "boop.", R("gravados-reels/assets/lista/boop.png"),
     "2 PESSOAS · 30 MIN", "Uma partida antes do filme. Ou no lugar dele."),
    ("3_galera", "ROLÊ COM A GALERA", ROXO, "Hitster", R("hobby-reels/assets/acervo/hitster.png"),
     "2 A 10 PESSOAS · 30 MIN", "Toca a música e todo mundo chuta o ano."),
    ("4_empresa", "FESTA DA EMPRESA", VERDE, "Código Secreto: Imagens",
     R("hobby-reels/assets/caixas/c_digo_secreto_imagens.png"), "2 A 8 PESSOAS · 15 MIN",
     "Dois times, uma dica por vez e o estagiário virando o herói da festa."),
]


def fundo(cor, semente, livre=None):
    cores = tuple(c for c in (AMARELO, BRANCO, PETROLEO, LARANJA, ROSA) if c != cor)
    return E.fundo_confete(W, H, base=cor, cores=cores, semente=semente, n=70, livre=livre)


def seta(cor=MARROM, h=120):
    im = Image.new("RGBA", (110, h + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.line((55, 5, 55, h - 40), fill=cor, width=16)
    d.polygon([(10, h - 55), (100, h - 55), (55, h)], fill=cor)
    return im


def pergunta():
    img = fundo(PETROLEO, 7, livre=(0, 920, W, 1410))
    E.cola(img, E.logo(300), W / 2, 250, -2)
    E.cola(img, E.titulo("E AÍ, QUAL É O\nPLANO PRO FIM\nDE SEMANA?", 116, BRANCO, larg_max=W - 110), W / 2, 590, -2)
    E.cola(img, E.pilula("VOTA AQUI EMBAIXO", 46, AMARELO, MARROM, fonte_titulo=True), W / 2 - 50, 845, 2)
    E.cola(img, seta(AMARELO), W / 2 + 270, 850)
    # y≈930–1400 fica LIVRE para a enquete
    card = E.bloco(860, 190, BRANCO, raio=34, ow=7, sombra=12)
    tx = E.texto("No próximo story, a gente indica\num jogo pra cada plano!", 44, MARROM, 800, entre=1.3)
    card.alpha_composite(tx, (int(430 - tx.width / 2), int(95 - tx.height / 2)))
    E.cola(img, card, W / 2, 1520, 1.5)
    return img


def plano_story(plano, cor, nome, caixa, ficha, frase, semente):
    img = fundo(cor, semente, livre=LIVRE)
    E.cola(img, E.logo(210), W / 2, 200, -2)
    E.cola(img, E.pilula("SEU PLANO:", 40, AMARELO, MARROM, fonte_titulo=True), W / 2, 335, -2)
    E.cola(img, E.titulo(plano, 96, BRANCO, larg_max=W - 100), W / 2, 445, -1)
    cw, ch = 860, 600
    card = E.bloco(cw, ch, BRANCO, raio=40, ow=7, sombra=14)
    cx = E.jogo(caixa, 290, larg=500)
    card.alpha_composite(cx, (int(cw / 2 - cx.width / 2), int(175 - cx.height / 2)))
    nm = E.titulo(nome, 74, cor, larg_max=cw - 80)
    card.alpha_composite(nm, (int(cw / 2 - nm.width / 2), int(375 - nm.height / 2)))
    fc = E.pilula(ficha, 32, AMARELO, MARROM)
    card.alpha_composite(fc, (int(cw / 2 - fc.width / 2), int(450 - fc.height / 2)))
    tx = E.texto(frase, 36, MARROM, 700, larg_max=cw - 110, entre=1.25)
    card.alpha_composite(tx, (int(cw / 2 - tx.width / 2), int(530 - tx.height / 2)))
    E.cola(img, card, W / 2, 835, 1)
    E.cola(img, E.pilula("RESERVA ESSE JOGO AQUI:", 42, BRANCO, MARROM, fonte_titulo=True), W / 2 - 50, 1200, -1)
    E.cola(img, seta(BRANCO, 100), W / 2 + 265, 1210)
    # y≈1255–1490 fica LIVRE para o adesivo de link do jogo no site
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):  # tira as telas da versão anterior (receita)
        if f.startswith("story_"):
            os.remove(os.path.join(OUT, f))
    telas = [("0_pergunta", pergunta())]
    for k, (arq, plano, cor, nome, caixa, ficha, frase) in enumerate(PLANOS):
        telas.append((arq, plano_story(plano, cor, nome, caixa, ficha, frase, k + 2)))
    for arq, im in telas:
        im.convert("RGB").save(os.path.join(OUT, f"story_{arq}.png"))
    w = 300
    h = int(w * H / W)
    sh = Image.new("RGB", (len(telas) * (w + 10) + 10, h + 20), (240, 236, 228))
    for k, (_, im) in enumerate(telas):
        sh.paste(im.convert("RGB").resize((w, h), Image.LANCZOS), (10 + k * (w + 10), 10))
    sh.save(os.path.join(OUT, "previa.jpg"), quality=88)
    print("ok", OUT)


if __name__ == "__main__":
    main()
