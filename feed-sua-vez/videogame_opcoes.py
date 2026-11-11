#!/usr/bin/env python3
"""Folha de OPÇÕES do carrossel "Se você joga ___ (videogame), vai gostar de ___ (tabuleiro)" (11/nov/2026, ideia dele).
Só jogos do acervo (caixa recortada do site). Ele escolhe os pares antes de eu montar o carrossel.

    /usr/bin/python3 videogame_opcoes.py   # out/opcoes_videogame.jpg
"""
import os
import sys

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
import estilo as E  # noqa: E402

AC = os.path.join(REPO, "hobby-reels", "assets", "acervo")
CX = os.path.join(REPO, "hobby-reels", "assets", "caixas")
GR = os.path.join(REPO, "gravados-reels", "assets")

PARES = [  # (videogame, jogo de tabuleiro, por quê, caixa)
    ("Among Us", "The Resistance", "tem traidor na mesa e ninguém confia em ninguém", f"{AC}/the_resistance.png"),
    ("Mini Metro", "Next Station: London", "você desenha as linhas do metrô", f"{AC}/next_station_london.png"),
    ("Tetris", "Patchwork", "encaixar peças sem sobrar buraco", f"{REPO}/roleta-reels/assets/patchwork.png"),
    ("Street Fighter / Smash", "Unmatched", "duelo de personagens, cada um com seu golpe",
     f"{AC}/unmatched_robin_hood_vs_bigfoot.png"),
    ("Jurassic World Evolution", "Dinosaur Island", "monte o seu parque de dinossauros", f"{AC}/dinosaur_island.png"),
    ("Stardew Valley", "La Granja", "plantar, colher e cuidar da fazenda", f"{AC}/la_granja.png"),
    ("Animal Crossing", "Everdell Duo", "uma vila fofa de bichinhos", f"{AC}/everdell_duo.png"),
    ("Overcooked", "Critter Kitchen", "cozinha caótica, pedido atrás de pedido", f"{AC}/critter_kitchen.png"),
    ("Hades / Slay the Spire", "Clank! Catacombs", "masmorra, monte o baralho e fuja vivo", f"{AC}/clank_catacombs.png"),
    ("Mario Kart", "Camel Up", "corrida caótica que vira na última volta", f"{AC}/camel_up_second_edition.png"),
    ("Civilization", "7 Wonders Duel", "construa sua civilização e vença o rival", f"{AC}/7_wonders_duel.png"),
    ("GTA", "Bad Company", "monte a gangue e planeje os assaltos", f"{AC}/bad_company.png"),
    ("The Last of Us", "Tiny Epic Zombies", "sobreviver aos zumbis em equipe", f"{AC}/tiny_epic_zombies.png"),
    ("Gartic Phone", "Telestrations na Madruga (+18)", "o telefone sem fio desenhado", f"{GR}/top10/telestrations_madruga.png"),
    ("Termo / Wordle", "Bananagrams", "formar palavras contra o tempo", f"{GR}/perguntas/bananagrams.png"),
    ("L.A. Noire", "Detective", "investigar um crime de verdade", f"{AC}/detective_a_modern_crime_board_game.png"),
]

CW, CH = 460, 560


def cartao(i, vg, tab, porque, caixa):
    c = E.bloco(CW, CH, E.BRANCO, raio=28, ow=5, sombra=8)
    d = ImageDraw.Draw(c)
    d.text((26, 18), str(i), font=E.lilita(46), fill=E.LARANJA)
    t1 = E.texto("se você joga", 24, cor=E.PETROLEO, peso=700)
    c.alpha_composite(t1, ((CW - t1.width) // 2, 24))
    t2 = E.texto(vg.upper(), 34, cor=E.MARROM, peso=900, larg_max=CW - 70)
    c.alpha_composite(t2, ((CW - t2.width) // 2, 58))
    cx = E.jogo(caixa, 250, larg=300)
    c.alpha_composite(cx, ((CW - cx.width) // 2, 60 + t2.height + 12))
    y = 60 + t2.height + 12 + cx.height + 10
    t3 = E.texto("vai gostar de", 22, cor=E.PETROLEO, peso=700)
    c.alpha_composite(t3, ((CW - t3.width) // 2, y))
    t4 = E.texto(tab, 28, cor=E.LARANJA, peso=900, larg_max=CW - 50)
    c.alpha_composite(t4, ((CW - t4.width) // 2, y + 30))
    t5 = E.texto(porque, 19, cor=E.MARROM, peso=500, larg_max=CW - 60)
    c.alpha_composite(t5, ((CW - t5.width) // 2, y + 34 + t4.height))
    return c


def main():
    cols = 4
    lins = (len(PARES) + cols - 1) // cols
    W, H = cols * (CW + 30) + 50, lins * (CH + 30) + 170
    img = Image.new("RGBA", (W, H), E.FUNDO + (255,))
    t = E.titulo("VIDEOGAME x TABULEIRO: QUAIS PARES ENTRAM?", 64, cor=E.AMARELO)
    img.alpha_composite(t, ((W - t.width) // 2, 30))
    for i, p in enumerate(PARES):
        c = cartao(i + 1, *p)
        img.alpha_composite(c, (40 + (i % cols) * (CW + 30), 150 + (i // cols) * (CH + 30)))
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    img.convert("RGB").save(os.path.join(ROOT, "out", "opcoes_videogame.jpg"), quality=90)
    print("ok")


if __name__ == "__main__":
    main()
