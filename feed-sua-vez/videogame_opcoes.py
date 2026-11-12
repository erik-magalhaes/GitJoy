#!/usr/bin/env python3
"""Folha de OPÇÕES do carrossel "Se você joga ___ (videogame), vai gostar de ___ (tabuleiro)" (11/nov/2026, ideia dele).
Só jogos do acervo (caixa recortada do site). Ele escolhe os pares antes de eu montar o carrossel.

    /usr/bin/python3 videogame_opcoes.py [videogame|animacao|filmes]   # out/opcoes_<nome>.jpg
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

PARES_VG = [  # (videogame, jogo de tabuleiro, por quê, caixa)
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

LISTAS = {  # nome → (título da folha, "se você ..." , pares)
    "videogame": ("VIDEOGAME x TABULEIRO: QUAIS PARES ENTRAM?", "se você joga", None),
    "animacao": ("ANIMAÇÕES x TABULEIRO: QUAIS PARES ENTRAM?", "se você ama", [
        ("Ratatouille", "Critter Kitchen", "bichinhos cozinhando pra agradar os clientes", f"{AC}/critter_kitchen.png"),
        ("Clássicos da Disney", "Dixit: Disney Edition", "conte histórias com cenas dos filmes da Disney",
         f"{AC}/dixit_disney_edition.png"),
        ("Alice no País das Maravilhas", "Wonderland's War", "o Chapeleiro e a Rainha Vermelha em guerra",
         f"{AC}/wonderland_s_war.png"),
        ("Robin Hood", "Unmatched: Robin Hood vs. Bigfoot", "o próprio Robin Hood, agora num duelo",
         f"{AC}/unmatched_robin_hood_vs_bigfoot.png"),
        ("Procurando Nemo", "Sea Salt & Paper", "peixes, caranguejos e barquinhos de papel", f"{AC}/sea_salt_paper.png"),
        ("Monstros S.A.", "O Vale dos Monstros II", "monstros invadindo a cidade", f"{REPO}/halloween-reels/assets/vale_monstros.png"),
        ("Moana", "Survive the Island", "fugir da ilha num mar cheio de monstros", f"{AC}/survive_the_island.png"),
        ("Carros", "Camel Up", "corrida maluca que vira na última volta", f"{AC}/camel_up_second_edition.png"),
        ("Os Incríveis", "Marvel United", "heróis em equipe contra o vilão", f"{GR}/lista/marvel_united.png"),
        ("Como Treinar o seu Dragão", "Flamecraft", "dragõezinhos fofos ajudando a cidade", f"{AC}/flamecraft.png"),
        ("Hotel Transilvânia", "Drácula vs Van Helsing", "o Drácula de verdade, num duelo de 2", f"{AC}/dracula_vs_van_helsing.png"),
        ("Zootopia", "MicroMacro: Crime City", "investigar crimes numa cidade gigante",
         f"{AC}/micromacro_crime_city_full_house.png"),
    ]),
    "filmes": ("FILMES x TABULEIRO: QUAIS PARES ENTRAM?", "se você ama", [
        ("Indiana Jones", "Tikal", "explorar a selva e achar os templos perdidos", f"{AC}/tikal.png"),
        ("Piratas do Caribe", "Treasure Island", "um pirata esconde o tesouro, os outros caçam no mapa",
         f"{AC}/treasure_island.png"),
        ("Sherlock Holmes", "Detective", "investigar um crime de verdade, com pistas e suspeitos",
         f"{AC}/detective_a_modern_crime_board_game.png"),
        ("Jurassic Park", "Dinosaur World", "monte o parque e leve os visitantes pra ver os dinos", f"{AC}/dinosaur_world.png"),
        ("Missão Impossível", "Spyfall", "um espião infiltrado e todo mundo desconfiando", f"{AC}/spyfall.png"),
        ("O Poderoso Chefão", "Coup", "poder, blefe e traição na família", f"{AC}/coup_inquisition.png"),
        ("Pânico / Sexta-Feira 13", "Final Girl", "você é a sobrevivente contra o assassino",
         f"{REPO}/finalgirl-reels/assets/recortes/caixa_base.png"),
        ("Os Caça-Fantasmas", "Paranormal Detectives", "investigar fantasmas e descobrir como morreram",
         f"{AC}/paranormal_detectives.png"),
        ("Harry Potter", "Wandering Towers", "magos, torres que andam e poções", f"{AC}/wandering_towers.png"),
        ("O Hobbit", "Tesouro do Dragão", "o dragão em cima do tesouro, e você querendo um pouco",
         f"{AC}/tesouro_do_drag_o.png"),
        ("Truque de Mestre", "Mascarade", "ilusão e blefe: ninguém sabe quem é quem", f"{AC}/mascarade_second_edition.png"),
        ("Os Vingadores", "Marvel United", "junte os heróis e derrote o vilão", f"{GR}/lista/marvel_united.png"),
        ("O Lobo de Wall Street", "High Society", "leilão de luxo pra quem gasta sem dó",
         f"{AC}/high_society.png"),
    ]),
    "personagens": ("QUE JOGO ESSE PERSONAGEM JOGARIA?", "personagem", [
        ("Sheldon (The Big Bang Theory)", "Hive", "xadrez sem tabuleiro, com regra explicada 3 vezes", f"{AC}/hive.png"),
        ("Monica (Friends)", "Azul Duel", "tudo organizadinho, peça por peça, e ela PRECISA ganhar", f"{AC}/azul_duel.png"),
        ("Rachel (Friends)", "Canvas", "montar a pintura mais bonita, camada por camada", f"{AC}/canvas.png"),
        ("Ross (Friends)", "Draftosaurus", "dinossauros! (e ele vai dizer que estava dando um tempo)", f"{AC}/draftosaurus.png"),
        ("Joey (Friends)", "Critter Kitchen", "é sobre comida. O Joey não divide comida", f"{AC}/critter_kitchen.png"),
        ("Phoebe (Friends)", "Dixit", "a dica mais viajada da mesa é sempre dela", f"{REPO}/hobby-reels/assets/caixas/dixit.png"),
        ("Chandler (Friends)", "Ref! O jogo da referência", "a piada com referência é a língua dele",
         f"{AC}/ref_o_jogo_da_refer_ncia.png"),
        ("Dwight (The Office)", "La Granja", "fazenda, colheita e muita beterraba", f"{AC}/la_granja.png"),
        ("Jim (The Office)", "Sheriff of Nottingham", "cara de paisagem pra passar o contrabando",
         f"{AC}/sheriff_of_nottingham_2nd_edition.png"),
        ("Eleven (Stranger Things)", "The Mind", "jogo de ler a mente, sem falar nada", f"{REPO}/roleta-reels/assets/the_mind.png"),
        ("Wandinha", "Paranormal Detectives", "conversar com fantasmas e descobrir como morreram",
         f"{AC}/paranormal_detectives.png"),
        ("Sherlock Holmes (série)", "MicroMacro: Crime City", "achar o culpado numa cidade cheia de pistas",
         f"{AC}/micromacro_crime_city_full_house.png"),
        ("Seu Madruga (Chaves)", "Bohnanza", "negociar feijão pra pagar o aluguel atrasado", f"{AC}/bohnanza.png"),
        ("Bridgerton", "High Society", "leilões de luxo na alta sociedade", f"{AC}/high_society.png"),
        ("Cersei (Game of Thrones)", "Coup", "mentir e trair pra ficar com o trono",
         f"{AC}/coup_inquisition.png"),
        ("Dr. House", "Detective", "investigar o caso até o fim, sem confiar em ninguém",
         f"{AC}/detective_a_modern_crime_board_game.png"),
    ], "jogaria"),
}
CW, CH = 460, 560


def cartao(i, vg, tab, porque, caixa, se="se você joga", vai="vai gostar de"):
    c = E.bloco(CW, CH, E.BRANCO, raio=28, ow=5, sombra=8)
    d = ImageDraw.Draw(c)
    d.text((26, 18), str(i), font=E.lilita(46), fill=E.LARANJA)
    t1 = E.texto(se, 24, cor=E.PETROLEO, peso=700)
    c.alpha_composite(t1, ((CW - t1.width) // 2, 24))
    t2 = E.texto(vg.upper(), 34, cor=E.MARROM, peso=900, larg_max=CW - 70)
    c.alpha_composite(t2, ((CW - t2.width) // 2, 58))
    cx = E.jogo(caixa, 250, larg=300)
    c.alpha_composite(cx, ((CW - cx.width) // 2, 60 + t2.height + 12))
    y = 60 + t2.height + 12 + cx.height + 10
    t3 = E.texto(vai, 22, cor=E.PETROLEO, peso=700)
    c.alpha_composite(t3, ((CW - t3.width) // 2, y))
    t4 = E.texto(tab, 28, cor=E.LARANJA, peso=900, larg_max=CW - 50)
    c.alpha_composite(t4, ((CW - t4.width) // 2, y + 30))
    t5 = E.texto(porque, 19, cor=E.MARROM, peso=500, larg_max=CW - 60)
    c.alpha_composite(t5, ((CW - t5.width) // 2, y + 34 + t4.height))
    return c


def main():
    nome = sys.argv[1] if len(sys.argv) > 1 else "videogame"
    titulo, se, PARES = LISTAS[nome][:3]
    vai = LISTAS[nome][3] if len(LISTAS[nome]) > 3 else "vai gostar de"
    PARES = PARES or PARES_VG
    cols = 4
    lins = (len(PARES) + cols - 1) // cols
    W, H = cols * (CW + 30) + 50, lins * (CH + 30) + 170
    img = Image.new("RGBA", (W, H), E.FUNDO + (255,))
    t = E.titulo(titulo, 64, cor=E.AMARELO, larg_max=W - 60)
    img.alpha_composite(t, ((W - t.width) // 2, 30))
    for i, p in enumerate(PARES):
        c = cartao(i + 1, *p, se=se, vai=vai)
        img.alpha_composite(c, (40 + (i % cols) * (CW + 30), 150 + (i // cols) * (CH + 30)))
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    img.convert("RGB").save(os.path.join(ROOT, "out", f"opcoes_{nome}.jpg"), quality=90)
    print("ok")


if __name__ == "__main__":
    main()
