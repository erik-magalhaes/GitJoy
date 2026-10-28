#!/usr/bin/env python3
"""Carrossel 1080x1350 "DINÂMICAS COM JOGOS NA SUA EMPRESA" (28/out/2026, ideia dele: levar a monitoria de eventos para
DENTRO das empresas; foco em comunicação, confiança, planejamento e resolução de problemas, NÃO em quebra-gelo).
Conceito próprio: CONVITE DE REUNIÃO DA AGENDA CORPORATIVA. O fundo é a grade de uma agenda (horários e reuniões chatas
desbotadas); cada tela é um convite com título, duração, participantes, pauta e os botões "Vai participar? Sim / Talvez /
Não", mas a reunião é um jogo. Identidade da Jéssica (Lilita + Figtree, marrom, sombra sólida).
Jogos (ele aprovou a lista; tirou o Sheriff of Nottingham): Código Secreto: Imagens, The Mind, Take Time, Unlock! e
Passaporte Mundo. Fichas do site (comum/dados/acervo_site.json). Sem "empresas atendidas" nem depoimento (ainda não
fizeram evento). WhatsApp do rodapé do site.

    python3 empresas.py      # out/empresas/01..07.png (+ out/empresas_folha.jpg)
"""
import json
import os
import sys

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
from estilo import (MARROM, PETROLEO, LARANJA, AMARELO, BRANCO, titulo, texto, bloco, pilula, logo, jogo, cola,  # noqa
                    lilita, fig)

OUT = os.path.join(ROOT, "out", "empresas")
W, H = 1080, 1350
GRADE, LINHA, CINZA = (244, 247, 250), (222, 228, 236), (130, 140, 152)
VERDE, ROXO, VERMELHO = (40, 150, 90), (108, 63, 160), (214, 64, 64)
_R = lambda *p: os.path.join(REPO, *p)  # noqa: E731
SITE = json.load(open(_R("comum", "dados", "acervo_site.json"), encoding="utf-8"))
REUNIOES = [  # (título, cor, jogo no site, caixa, nome curto, pauta)
    ("Comunicação clara", LARANJA, "Código secreto: imagens", _R("hobby-reels/assets/caixas/c_digo_secreto_imagens.png"),
     "Código Secreto: Imagens",
     ["Dar UMA dica que o time inteiro entende", "Entender como o colega pensa", "Decidir juntos o próximo passo"]),
    ("Sincronia e confiança", PETROLEO, "The Mind", _R("hobby-reels/assets/acervo/the_mind.png"), "The Mind",
     ["Jogar as cartas em ordem crescente...", "...sem ninguém falar nada", "Confiar no ritmo do outro"]),
    ("Planejamento em equipe", ROXO, "Take Time", _R("hobby-reels/assets/acervo/take_time.png"), "Take Time",
     ["Cooperativo: ganha ou perde o time todo", "Cada um planeja sem mostrar as próprias cartas",
      "Organizar o todo com informação parcial"]),
    ("Resolver problemas sob pressão", VERMELHO, "Unlock!: Timeless Adventures",
     _R("hobby-reels/assets/acervo/unlock_timeless_adventures.png"), "Unlock!",
     ["Escape room em cartas, com tempo contado", "Juntar as pistas que estão com cada um", "Dividir tarefas e destravar"]),
    ("Decisão em grupo", VERDE, "Passaporte Mundo", _R("hobby-reels/assets/acervo/passaporte_mundo.png"), "Passaporte Mundo",
     ["Quiz COOPERATIVO de países do mundo", "Ouvir todo mundo antes de responder", "Chegar num consenso"]),
]


def ficha(nome):
    v = SITE[nome]
    a, b = v["jogadores"].split("–")
    return (f"{a} a {b} pessoas" if a != b else f"{a} pessoas"), v["tempo"].replace("min", " min")


def agenda(semente=0, eventos=True):
    """Fundo: grade de agenda (coluna de horários, linhas e reuniões chatas desbotadas)."""
    img = Image.new("RGBA", (W, H), GRADE + (255,))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 120), fill=BRANCO)
    d.line((0, 120, W, 120), fill=LINHA, width=3)
    for k, dia in enumerate(["SEG", "TER", "QUA", "QUI", "SEX"]):
        x = 150 + k * 186 + 93
        d.text((x, 60), dia, font=fig(30, 800), fill=CINZA, anchor="mm")
    for k, hora in enumerate(range(8, 19)):
        y = 170 + k * 110
        d.text((70, y), f"{hora:02d}:00", font=fig(26, 700), fill=CINZA, anchor="mm")
        d.line((140, y, W, y), fill=LINHA, width=2)
    for k in range(6):
        d.line((150 + k * 186, 120, 150 + k * 186, H), fill=LINHA, width=2)
    if eventos:
        chatas = ["Alinhamento", "Status semanal", "Reunião da reunião", "Follow-up", "Report", "Sync rápido",
                  "Alinhamento 2", "Revisão do status"]
        import random
        rnd = random.Random(semente)
        for k, txt in enumerate(chatas):
            col, y = rnd.randrange(5), 180 + rnd.randrange(10) * 110
            x0 = 156 + col * 186
            d.rounded_rectangle((x0, y, x0 + 174, y + 96), radius=14, fill=(214, 222, 232))
            d.text((x0 + 12, y + 14), txt, font=fig(22, 700), fill=(150, 160, 172))
    return img


def icone_relogio(d, x, y, r=17, cor=CINZA):
    d.ellipse((x - r, y - r, x + r, y + r), outline=cor, width=4)
    d.line((x, y, x, y - r * 0.6), fill=cor, width=4)
    d.line((x, y, x + r * 0.5, y), fill=cor, width=4)


def icone_pessoas(d, x, y, cor=CINZA):
    for dx in (-10, 10):
        d.ellipse((x + dx - 8, y - 18, x + dx + 8, y - 2), fill=cor)
        d.pieslice((x + dx - 15, y, x + dx + 15, y + 30), 180, 360, fill=cor)


def botoes(c, y, w):
    """'Vai participar?' com SIM marcado."""
    d = ImageDraw.Draw(c)
    d.text((60, y), "Vai participar?", font=fig(34, 800), fill=MARROM, anchor="lm")
    x = w - 60
    for txt, ativo in (("Não", False), ("Talvez", False), ("Sim ✓", True)):
        f = fig(32, 900)
        tw = d.textlength(txt, font=f)
        bw = int(tw + 50)
        x0 = x - bw
        if ativo:
            d.rounded_rectangle((x0, y - 32, x, y + 32), radius=32, fill=VERDE, outline=MARROM, width=4)
            d.text(((x0 + x) / 2, y), txt.replace(" ✓", ""), font=f, fill=BRANCO, anchor="mm")
            cx = x0 + 22  # o "visto" desenhado (a fonte não tem ✓)
        else:
            d.rounded_rectangle((x0, y - 32, x, y + 32), radius=32, fill=BRANCO, outline=(190, 196, 204), width=4)
            d.text(((x0 + x) / 2, y), txt, font=f, fill=CINZA, anchor="mm")
        x = x0 - 16


def convite(tit, cor, nome_site, caixa, curto, pauta, n, total):
    w, h = 940, 1010
    c = bloco(w, h, BRANCO, raio=30, ow=6, sombra=14)
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((0, 0, 34, h), radius=30, fill=cor)
    d.rectangle((18, 0, 34, h), fill=cor)
    d.rounded_rectangle((0, 0, w, h), radius=30, outline=MARROM, width=6)
    cola(c, pilula("CONVITE DE REUNIÃO", 28, cor, BRANCO, pad=(20, 8), ow=4, sombra=5), 250, 70)
    cola(c, texto(f"{n} de {total}", 26, CINZA, 700), w - 90, 70)
    tt = titulo(tit, 74, MARROM, MARROM, sw=0, sombra=0, larg_max=w - 120)
    c.alpha_composite(tt, (54, 120))
    pessoas, tempo = ficha(nome_site)
    y = 140 + tt.height + 30
    icone_relogio(d, 82, y)
    d.text((112, y), tempo, font=fig(34, 800), fill=MARROM, anchor="lm")
    icone_pessoas(d, 330, y - 4)
    d.text((362, y), pessoas, font=fig(34, 800), fill=MARROM, anchor="lm")
    d.text((60, y + 70), "Local: sala de reunião (a gente leva o jogo)", font=fig(28, 600), fill=CINZA, anchor="lm")
    d.line((54, y + 115, w - 54, y + 115), fill=LINHA, width=3)
    d.text((60, y + 160), "PAUTA", font=fig(30, 900), fill=cor, anchor="lm")
    yy = y + 205
    for p in pauta:  # cada item embaixo do anterior (item de 2 linhas empurra o próximo)
        tx = texto(p, 33, MARROM, 700, larg_max=470, entre=1.15, alinha="lm")
        d.ellipse((60, yy + 12, 78, yy + 30), fill=cor)
        c.alpha_composite(tx, (96, int(yy)))
        yy += tx.height + 22
    cola(c, jogo(caixa, 360, 300), w - 190, y + 290, 4)
    cola(c, pilula(curto, 32, AMARELO, MARROM, pad=(22, 8), fonte_titulo=True), w - 190, y + 500, -3)
    d.line((54, h - 130, w - 54, h - 130), fill=LINHA, width=3)
    botoes(c, h - 66, w)
    return c


def tela_reuniao(k):
    tit, cor, nome_site, caixa, curto, pauta = REUNIOES[k]
    img = agenda(k + 3)
    cola(img, convite(tit, cor, nome_site, caixa, curto, pauta, k + 1, len(REUNIOES)), W / 2 + 8, 690)
    return img


def capa():
    img = agenda(1)
    d = ImageDraw.Draw(img)
    # o bloco do jogo, colorido, no meio da semana cheia de reunião
    cola(img, bloco(360, 210, AMARELO, raio=22, ow=6, sombra=10), 150 + 2 * 186 + 93, 1040, -4)
    cola(img, titulo("DINÂMICA COM\nJOGOS", 44, MARROM, MARROM, sw=0, sombra=0), 150 + 2 * 186 + 93, 1030, -4)
    del d
    cola(img, logo(250), W - 180, 230, 3)
    cola(img, titulo("SUA EQUIPE\nPRECISA DE MAIS\nUMA REUNIÃO?", 104, BRANCO), W / 2, 520, -2)
    cola(img, pilula("ou de um jogo?  →", 60, LARANJA, BRANCO, pad=(34, 14), fonte_titulo=True), W / 2, 800, 2)
    return img


def final():
    img = agenda(9, eventos=False)
    w, h = 940, 1080
    c = bloco(w, h, BRANCO, raio=30, ow=6, sombra=14)
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((0, 0, 34, h), radius=30, fill=AMARELO)
    d.rectangle((18, 0, 34, h), fill=AMARELO)
    d.rounded_rectangle((0, 0, w, h), radius=30, outline=MARROM, width=6)
    cola(c, pilula("NOVO CONVITE", 28, AMARELO, MARROM, pad=(20, 8), ow=4, sombra=5), 190, 70)
    cola(c, titulo("Jogos e dinâmicas\nna sua empresa", 70, MARROM, MARROM, sw=0, sombra=0), w / 2 - 60, 230)
    d.text((60, 330), "Organizador: Sua Vez", font=fig(30, 800), fill=PETROLEO, anchor="lm")
    itens = ["A gente leva os jogos e fica o tempo todo ensinando e conduzindo",
             "Comunicação, confiança, planejamento e resolução de problemas",
             "A quantidade de jogos vai conforme o tamanho da equipe",
             "Atendemos principalmente o ABC Paulista"]
    for k, it in enumerate(itens):
        yy = 420 + k * 105
        d.ellipse((60, yy - 9, 78, yy + 9), fill=LARANJA)
        tx = texto(it, 32, MARROM, 700, larg_max=780, entre=1.2, alinha="lm")
        c.alpha_composite(tx, (96, int(yy - tx.height / 2 + 4)))
    d.line((54, 850, w - 54, 850), fill=LINHA, width=3)
    cola(c, texto("Peça um orçamento pelo Direct\nou pelo WhatsApp (11) 97793-3910", 36, MARROM, 900, entre=1.25), w / 2,
         960)
    cola(c, logo(210), w - 150, 90, 3)
    cola(img, c, W / 2 + 8, 690)
    cola(img, pilula("@SUAVEZ_BG", 40, AMARELO, MARROM, pad=(30, 12), fonte_titulo=True), W / 2, 1290, -2)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    telas = [capa()] + [tela_reuniao(k) for k in range(len(REUNIOES))] + [final()]
    for k, im in enumerate(telas):
        im.convert("RGB").save(os.path.join(OUT, f"{k + 1:02d}.png"))
    folha = Image.new("RGB", (4 * 405 + 50, 2 * 506 + 30), (255, 255, 255))
    for k, im in enumerate(telas):
        folha.paste(im.convert("RGB").resize((405, 506), Image.LANCZOS), (10 + (k % 4) * 415, 10 + (k // 4) * 516))
    folha.save(os.path.join(ROOT, "out", "empresas_folha.jpg"), quality=90)
    print("ok", len(telas))


if __name__ == "__main__":
    main()
