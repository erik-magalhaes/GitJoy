#!/usr/bin/env python3
"""Carrosséis do feed (1080 x 1080, pedido dele: quadrado), ideias 8, 9 e 11 da lista que ele aprovou:

    8  "O jogo certo pra cada rolê"           (rolê → jogo)
    9  "Curte esse clássico? Experimente…"    (clássico → moderno parecido)
    11 "Top 5 queridinhos da Sua Vez"         (ele pediu "mais alugados do mês", mas a loja ainda não tem aluguéis:
                                               virou os que eles MAIS INDICAM, com as frases dele do vídeo 5-4-3-2-1)

Visual próprio (cores do site, laranja/azul-marinho, fundo creme, círculo colorido atrás da caixa), diferente do
carrossel de madeira. Só caixas OFICIAIS de jogos que estão no acervo; jogadores/tempo do site (comum/dados/acervo_site.json).

    python3 carrosseis.py      # out/<role|classicos|top5>/01.png ... e todas.jpg de cada
"""
import json
import math
import os
import sys
from functools import lru_cache

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "comum"))
from motor import WHITE, font, emoji, logo_card, cola, sombra, letreiro, pilula  # noqa: E402

S = 1080
OUT = os.path.join(ROOT, "out")
CREME = (255, 247, 236)
NAVY = (22, 33, 62)
ORANGE = (249, 115, 22)
CORES = [(249, 115, 22), (37, 99, 235), (22, 163, 74), (147, 51, 234), (236, 72, 153), (13, 148, 136)]
SITE = {k.strip(): v for k, v in json.load(open(os.path.join(REPO, "comum", "dados", "acervo_site.json"), encoding="utf-8")).items()}
CX = {
    "azul_duel": "gravados-reels/assets/lista/azul_duel.png", "gravity": "gravados-reels/assets/oficial/gravity_superstar.png",
    "hitster": "gravados-reels/assets/lista/hitster.png", "finalgirl": "finalgirl-reels/assets/recortes/caixa_base.png",
    "ticket": "gravados-reels/assets/lista/ticket_to_ride.png", "arquitetos": "architects-reels/assets/oficial/caixa3d.png",
    "flip7": "feed-posts/assets/flip7_vinganca.png", "banana": "gravados-reels/assets/perguntas/bananagrams.png",
    "dixit": "gravados-reels/assets/lista/dixit.png", "micromacro": "feed-posts/assets/micromacro.png",
    "boop": "gravados-reels/assets/lista/boop.png", "harmonies": "gravados-reels/assets/lista/harmonies.png",
    "king": "gravados-reels/assets/lista/king_of_tokyo.png", "splendor": "gravados-reels/assets/lista/splendor_duel.png",
}
NOME_SITE = {"azul_duel": "Azul Duel", "gravity": "Gravity Superstar", "hitster": "Hitster", "finalgirl": "Final Girl",
             "ticket": "Ticket to Ride", "arquitetos": "7 Wonders: Architects", "flip7": "Flip 7: A Vingança",
             "banana": "Bananagrams", "dixit": "Dixit", "micromacro": "MicroMacro: Crime City - full house", "boop": "boop.",
             "harmonies": "Harmonies", "king": "King of Tokyo", "splendor": "Splendor Duel"}


@lru_cache(None)
def caixa(n, h):
    im = Image.open(os.path.join(REPO, CX[n])).convert("RGBA")
    im = im.crop(im.getbbox())
    if im.width / im.height > 1.6:  # caixas muito largas (banana) não podem ficar enormes
        h = int(h * 0.62)
    im = im.resize((max(2, int(im.width * h / im.height)), int(h)), Image.LANCZOS)
    return sombra(im, 16, (8, 16), 0.4)


def info(n):
    d = SITE[NOME_SITE[n]]
    a, b = d["jogadores"].split("–")
    jog = f"{a} JOGADOR" if a == b == "1" else (f"{a} JOGADORES" if a == b else f"{a} A {b} JOGADORES")
    if n == "flip7":
        jog = "3+ JOGADORES"
    return f"{jog} · {d['tempo'].replace('min', ' MIN')}"


def quebra(txt, f, larg):
    linhas, cur = [], ""
    for w in txt.split():
        t = (cur + " " + w).strip()
        if f.getlength(t) > larg and cur:
            linhas.append(cur)
            cur = w
        else:
            cur = t
    return linhas + [cur]


def base(cor):
    img = Image.new("RGBA", (S, S), CREME + (255,))
    d = ImageDraw.Draw(img)
    for k in range(-S, S, 90):  # listras bem leves
        d.line((k, 0, k + S, S), fill=(255, 255, 255, 120), width=34)
    d.ellipse((540 - 290, 450 - 290, 540 + 290, 450 + 290), fill=cor + (255,))
    d.ellipse((540 - 262, 450 - 262, 540 + 262, 450 + 262), outline=(255, 255, 255, 160), width=6)
    return img


def marca(img, n, tot):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((34, 34, 150, 92), radius=29, fill=NAVY)
    d.text((92, 63), f"{n}/{tot}", font=font("Bungee-Regular.ttf", 30), fill=WHITE, anchor="mm")
    lg = logo_card(140)
    img.alpha_composite(lg, (S - lg.width - 30, 30))
    if n < tot:
        k = pilula("ARRASTA     ", 30, NAVY)
        dk = ImageDraw.Draw(k)
        cy, x1 = k.height / 2 + 1, k.width - 52
        dk.polygon([(x1, cy - 11), (x1 + 20, cy), (x1, cy + 11)], fill=WHITE)
        dk.line((x1 - 24, cy, x1 + 3, cy), fill=WHITE, width=5)
        cola(img, k, S - k.width / 2 - 30, S - 60)


def texto_jogo(img, n, nome, motivo, y0=770):
    d = ImageDraw.Draw(img)
    d.text((540, y0), nome, font=font("Poppins-Black.ttf", 54), fill=NAVY, anchor="mm")
    f = font("Poppins-SemiBold.ttf", 34)
    for k, l in enumerate(quebra(motivo, f, 900)):
        d.text((540, y0 + 66 + k * 44), l, font=f, fill=(70, 70, 85), anchor="mm")
    cola(img, pilula(info(n), 30, ORANGE), 540, 965)


def capa(titulo, sub, caixas, cor):
    img = base(cor)
    for j, n in enumerate(caixas):
        ang = (j - (len(caixas) - 1) / 2) * 9
        x = 540 + (j - (len(caixas) - 1) / 2) * 150
        cola(img, caixa(n, 300), x, 520 + abs(j - (len(caixas) - 1) / 2) * 25, -ang)
    tam = 74 if max(len(l) for l in titulo.split("\n")) <= 14 else 60
    cola(img, letreiro(titulo, tam, WHITE, NAVY, 12, sombra_px=7, cor_sombra=NAVY), 540, 185, -2)
    cola(img, pilula(sub, 34, NAVY), 540, 870, 1)
    return img


def cta(pergunta, cor):
    img = Image.new("RGBA", (S, S), NAVY + (255,))
    d = ImageDraw.Draw(img)
    d.ellipse((540 - 520, 160 - 520, 540 + 520, 160 + 520), fill=cor + (255,))
    cola(img, logo_card(330), 540, 190)
    cola(img, letreiro("ALUGUE NA SUA VEZ!", 70, (255, 214, 70), NAVY, 12), 540, 400, -2)
    itens = [("5 DIAS DE JOGO · 3 JOGOS = 7 DIAS", WHITE), ("RESERVE ONLINE · RETIRE EM MAUÁ E ABC", WHITE),
             ("OU RECEBA EM CASA", (134, 239, 172)), ("LINK NA BIO · @SUAVEZ_BG", (255, 190, 120))]
    for k, (t, c) in enumerate(itens):
        d.text((540, 520 + k * 66), t, font=font("Bungee-Regular.ttf", 40), fill=c, anchor="mm")
    cola(img, pilula(pergunta, 34, ORANGE), 540, 880, -1)
    return img


# ---------------------------------------------------------------- 8: o jogo certo pra cada rolê
ROLE = [("💕", "PRIMEIRO ENCONTRO", "azul_duel", "AZUL DUEL", "Bonito, só pra dois e dá pra conversar enquanto joga."),
        ("🧸", "FAMÍLIA COM CRIANÇAS", "gravity", "GRAVITY SUPERSTAR", "Fácil de aprender e diverte do pequeno ao avô."),
        ("🎉", "GALERA GRANDE", "hitster", "HITSTER", "Monte a linha do tempo das músicas. Até 10 pessoas!"),
        ("🔦", "NOITE SOZINHO", "finalgirl", "FINAL GIRL", "Você contra o assassino de um filme de terror."),
        ("🌱", "QUEM TÁ COMEÇANDO", "ticket", "TICKET TO RIDE", "Ligue cidades com trens. Regra simples, vicia rápido."),
        ("🧠", "QUEM CURTE ESTRATÉGIA", "arquitetos", "7 WONDERS ARQUITETOS", "Construa sua maravilha: rápido, mas cheio de decisões.")]


def slide_role(k):
    em, rol, n, nome, mot = ROLE[k]
    img = base(CORES[k % len(CORES)])
    cola(img, caixa(n, 400), 540, 455, (-3, 3)[k % 2])
    cola(img, emoji(em, 74), 150, 175)
    cola(img, letreiro(rol, 56 if len(rol) < 18 else 48, WHITE, NAVY, 10), 590, 175, -1)
    texto_jogo(img, n, nome, mot)
    return img


# ---------------------------------------------------------------- 9: clássico → moderno
CLASSICOS = [("UNO", "flip7", "FLIP 7: A VINGANÇA", "Também é carta e número, mas você decide até onde arriscar."),
             ("SCRABBLE", "banana", "BANANAGRAMS", "Palavras cruzadas sem tabuleiro, todo mundo ao mesmo tempo."),
             ("IMAGEM & AÇÃO", "dixit", "DIXIT", "Em vez de desenhar, você dá dicas sobre cartas ilustradas."),
             ("DETETIVE", "micromacro", "MICROMACRO: FULL HOUSE", "Ache o culpado numa cidade gigante toda desenhada."),
             ("JOGO DA VELHA", "boop", "BOOP.", "Três em linha… mas os gatinhos empurram uns aos outros!")]


def slide_classico(k):
    cl, n, nome, mot = CLASSICOS[k]
    img = base(CORES[(k + 1) % len(CORES)])
    cola(img, letreiro(f"CURTE {cl}?", 62 if len(cl) < 10 else 54, WHITE, NAVY, 11), 540, 150, -2)
    cola(img, pilula("ENTÃO EXPERIMENTA:", 30, NAVY), 540, 235, 1)
    cola(img, caixa(n, 360), 540, 480, (3, -3)[k % 2])
    texto_jogo(img, n, nome, mot)
    return img


# ---------------------------------------------------------------- 11: top 5 queridinhos (frases dele no vídeo 5-4-3-2-1)
TOP5 = [(5, "king", "KING OF TOKYO", "“Destrói qualquer amizade.” Monstro gigante, dado e muita treta."),
        (4, "ticket", "TICKET TO RIDE", "O que a gente indica pra quem nunca jogou um jogo moderno."),
        (3, "splendor", "SPLENDOR DUEL", "Um dos nossos favoritos pra jogar a dois."),
        (2, "harmonies", "HARMONIES", "“O nosso jogo mais jogado aqui.” Monte paisagens e atraia animais."),
        (1, "hitster", "HITSTER", "“Um jogo democrático: se você gosta de música, vai curtir.”")]


def slide_top(k):
    num, n, nome, mot = TOP5[k]
    img = base(CORES[k % len(CORES)])
    cola(img, letreiro("TOP 5 QUERIDINHOS", 44, WHITE, NAVY, 9), 540, 140, -1)
    cola(img, caixa(n, 390), 600, 460, 3)
    cola(img, letreiro(f"#{num}", 190, (255, 214, 70), NAVY, 16, sombra_px=10, cor_sombra=NAVY), 210, 470, -8)
    texto_jogo(img, n, nome, mot)
    return img


def salva(pasta, ims):
    d = os.path.join(OUT, pasta)
    os.makedirs(d, exist_ok=True)
    tot = len(ims)
    for i, im in enumerate(ims, 1):
        marca(im, i, tot)
        im.convert("RGB").save(os.path.join(d, f"{i:02d}.png"))
    cols = 4
    folha = Image.new("RGB", (cols * 400, ((tot + cols - 1) // cols) * 400), "white")
    for i, im in enumerate(ims):
        folha.paste(im.convert("RGB").resize((400, 400), Image.LANCZOS), ((i % cols) * 400, (i // cols) * 400))
    folha.save(os.path.join(d, "todas.jpg"), quality=88)
    print("ok", pasta, tot)


def main():
    salva("role", [capa("O JOGO CERTO\nPRA CADA ROLÊ", "ARRASTA E ACHA O SEU", ["azul_duel", "hitster", "ticket", "finalgirl"], CORES[1])]
          + [slide_role(k) for k in range(len(ROLE))] + [cta("QUAL É O SEU ROLÊ? COMENTA!", CORES[0])])
    salva("classicos", [capa("CURTE OS\nCLÁSSICOS?", "TEM UM MODERNO PARECIDO", ["flip7", "dixit", "boop", "micromacro"], CORES[0])]
          + [slide_classico(k) for k in range(len(CLASSICOS))] + [cta("QUAL CLÁSSICO VOCÊ AMA? COMENTA!", CORES[1])])
    salva("top5", [capa("TOP 5 QUERIDINHOS\nDA SUA VEZ", "OS QUE A GENTE MAIS INDICA", ["king", "ticket", "harmonies", "hitster"], CORES[3])]
          + [slide_top(k) for k in range(len(TOP5))] + [cta("QUAL É O SEU TOP 1? COMENTA!", CORES[3])])


if __name__ == "__main__":
    main()
