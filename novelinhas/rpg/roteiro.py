"""A Guilda do Dragão: aventura medieval em 5 partes do Compartilhado que, no final, é uma partida de RPG pelo WhatsApp.

O grupo "A Guilda ⚔️" fala como se estivesse num reino de verdade: Valdora em chamas, o dragão Ignarok, a taverna, a floresta
sombria, a traição do ladino Kael, a montanha. O "Mestre" narra e manda "visões" (imagens), e o "Dado Mágico" decide tudo.
Pistas que só fazem sentido no fim: o dado, o Sir Breno sumindo "pra resolver uma coisa", a bateria dele, o Kael "morto" que
ainda manda emoji. Na Parte 5, depois do 20 crítico contra o dragão, chega a mãe da Lia chamando para jantar e o Mestre muda
o nome do grupo para "RPG da 8ª série 🎲": eram quatro amigos de 14 anos jogando RPG pelo celular.
"""
import functools
import os

from PIL import Image, ImageDraw

import zap

FOTOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fotos")
TITULO = "A Guilda do Dragão"

THALITA = ("pt-BR-ThalitaMultilingualNeural", "+0%", "+0Hz")
ANTONIO = ("pt-BR-AntonioNeural", "+0%", "+0Hz")
FRANCISCA = ("pt-BR-FranciscaNeural", "+0%", "+0Hz")
VOZES = {"lia": THALITA, "mae": FRANCISCA, "dado": FRANCISCA,
         "mestre": ANTONIO, "breno": ANTONIO, "kael": ANTONIO}
PRONUNCIA = {r"\bKael\b": "Kaél", r"\bIgnarok\b": "Iguinárok", r"\bd20\b": "dê vinte"}

PERSONAGENS = {
    "lia": dict(nome="Lia", cor=(126, 87, 194)),
    "mestre": dict(nome="Mestre", cor=(255, 179, 0)),
    "breno": dict(nome="Sir Breno", cor=(30, 136, 229)),
    "kael": dict(nome="Kael", cor=(67, 160, 71)),
    "dado": dict(nome="Dado Mágico", cor=(229, 57, 53)),
    "mae": dict(nome="Mãe", cor=(216, 27, 96)),
}

NOMES = {"mestre": "Mestre", "breno": "Sir Breno", "kael": "Kael, o Ladino", "dado": "Dado Mágico"}
CHATS = {
    "guilda": dict(dono="lia", titulo="A Guilda ⚔️", grupo=True, sub="Mestre, Sir Breno, Kael, Dado Mágico, Você", nomes=NOMES),
    "kael": dict(dono="lia", titulo="Kael", com="kael", sub="online"),
    "breno": dict(dono="lia", titulo="Sir Breno", com="breno", sub="online"),
    "mae": dict(dono="lia", titulo="Mãe 💜", com="mae", sub="online"),
}


@functools.lru_cache(None)
def dado(n):
    """Um d20 desenhado (icosaedro visto de frente) com o número no centro."""
    w = 520
    im = Image.new("RGB", (w, w), (24, 20, 40))
    d = ImageDraw.Draw(im)
    import math
    cx, cy, r = w / 2, w / 2, 210
    hexa = [(cx + r * math.cos(math.radians(90 + 60 * k)), cy - r * math.sin(math.radians(90 + 60 * k))) for k in range(6)]
    cor = (255, 196, 0) if n == 20 else ((198, 40, 40) if n <= 5 else (94, 53, 177))
    d.polygon(hexa, fill=cor)
    tri = [hexa[0], hexa[2], hexa[4]]
    claro = tuple(min(255, c + 45) for c in cor)
    d.polygon(tri, fill=claro)
    for p in hexa:
        for q in tri:
            d.line([p, q], fill=(30, 20, 50), width=4)
    d.polygon(hexa, outline=(30, 20, 50), width=6)
    d.text((cx, cy + 30), str(n), font=zap.inter(120, 900), fill=(255, 255, 255), anchor="mm", stroke_width=6,
           stroke_fill=(30, 20, 50))
    if n == 20:
        d.text((cx, w - 30), "CRÍTICO!", font=zap.inter(44, 900), fill=(255, 214, 0), anchor="mm")
    return im


EPISODIOS = [
    # ---------------------------------------------------------------------------------------------- 1
    dict(parte=1, nome="A convocação", eventos=[
        ("chat", "guilda", "19:00", "SÁBADO"),
        ("msg", "mestre", "Valdora arde. Na noite passada, o dragão Ignarok queimou a ponte do norte e levou o ouro do rei.",
         dict(dig=0.6)),
        ("foto", "mestre", "torre_ruina.jpg", "Isto é o que restou da torre de vigia.", dict(pausa=0.6)),
        ("msg", "mestre", "O rei convoca a Guilda. Quem atende ao chamado?", dict(dig=0.4)),
        ("msg", "breno", "Pela honra da Ordem do Leão, eu vou! ⚔️", dict(dig=0.3)),
        ("foto", "breno", "armadura.jpg", "Armadura polida e pronta.", dict(pausa=0.6)),
        ("msg", "lia", "Eu levo as ervas de cura. Alguém vai precisar 🌿"),
        ("msg", "kael", "E eu levo... tudo que não estiver pregado no chão 😏", dict(dig=0.3)),
        ("msg", "mestre", "Vocês se encontram na Taverna do Javali Torto. O taverneiro olha desconfiado para o Kael.", dict(dig=0.4)),
        ("msg", "kael", "Eu tento pegar a bolsa de moedas do balcão sem ninguém ver.", dict(dig=0.3)),
        ("msg", "dado", "Kael rolou Furtividade: 4.", dict(dig=0.6)),
        ("msg", "mestre", "O taverneiro segura o seu pulso. A taverna inteira fica em silêncio.", dict(dig=0.4)),
        ("msg", "lia", "Kael, pelo amor dos deuses 🤦‍♀️"),
        ("msg", "breno", "Eu pago a bebida de todo mundo pra ninguém brigar 🍺", dict(dig=0.3)),
        ("msg", "mestre", "Aceito. Mas no fundo da taverna, um velho encapuzado chama a curandeira.", dict(dig=0.4)),
        ("msg", "mestre", "\"O dragão não age sozinho. Alguém desta guilda já negociou com ele.\"", dict(dig=0.6)),
        ("msg", "lia", "Quem?? Fala quem!"),
        ("msg", "mestre", "O velho some na fumaça. E uma sombra gigante cobre a lua sobre a taverna.", dict(dig=0.4)),
        ("foto", "mestre", "iluminura_dragao.jpg", "Uma visão: Ignarok vem buscar quem o desafiar.", dict(zoom=True, pausa=0.8, h_max=600)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 2
    dict(parte=2, nome="A floresta sombria", eventos=[
        ("chat", "guilda", "19:40", "SÁBADO"),
        ("foto", "mestre", "floresta_nevoa.jpg", "A Floresta Sombria. Nenhum pássaro canta aqui.", dict(pausa=0.6)),
        ("msg", "breno", "Eu vou na frente, com o escudo levantado 🛡️", dict(dig=0.3)),
        ("msg", "mestre", "Galhos estalam. Cinco goblins saltam das árvores!", dict(dig=0.4)),
        ("msg", "breno", "ATACO O MAIOR!", dict(dig=0.2)),
        ("msg", "dado", "Sir Breno rolou Ataque: 15.", dict(dig=0.6)),
        ("msg", "mestre", "Sua espada atravessa o goblin chefe. Mas uma flecha acerta o seu ombro.", dict(dig=0.4)),
        ("msg", "breno", "Lia, ajuda aqui 😵", dict(dig=0.2)),
        ("msg", "lia", "Eu uso as ervas e faço a cura no Breno!"),
        ("msg", "dado", "Lia rolou Cura: 18.", dict(dig=0.6)),
        ("msg", "mestre", "A ferida fecha com uma luz verde. Os goblins fogem para a névoa.", dict(dig=0.4)),
        ("msg", "breno", "Valeu, Lia! Te devo uma 🙏", dict(dig=0.3)),
        ("msg", "breno", "Gente, volto já. Preciso resolver uma coisa no castelo.", dict(dig=0.4)),
        ("msg", "mestre", "Sir Breno se afasta por um momento.", dict(dig=0.3)),
        ("msg", "mestre", "E onde está o Kael? E o mapa do reino, que estava com o Breno?", dict(dig=0.6)),
        ("msg", "lia", "O MAPA SUMIU."),
        ("chat", "kael", "19:55", "SÁBADO"),
        ("msg", "kael", "Lia. Só você.", dict(dig=0.4)),
        ("msg", "kael", "Eu tô com o mapa. Confia em mim. Não conta pro Breno.", dict(dig=0.6)),
        ("msg", "lia", "Kael, o velho da taverna falou que alguém da guilda negociou com o dragão."),
        ("msg", "kael", "Então você já sabe quem é 🙂", dict(dig=0.8)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 3
    dict(parte=3, nome="A traição", eventos=[
        ("chat", "guilda", "20:10", "SÁBADO"),
        ("msg", "breno", "Voltei! Perdi alguma coisa?", dict(dig=0.3)),
        ("msg", "lia", "O Kael roubou o mapa. Ele fez acordo com o dragão."),
        ("msg", "kael", "Acordo, não. Negócio. O Ignarok me paga mil moedas de ouro por cada cavaleiro 😏", dict(dig=0.4)),
        ("msg", "breno", "TRAIDOR! Eu desafio você pra um duelo! ⚔️", dict(dig=0.2)),
        ("msg", "dado", "Sir Breno rolou Ataque: 19.", dict(dig=0.6)),
        ("msg", "dado", "Kael rolou Defesa: 3.", dict(dig=0.6)),
        ("msg", "mestre", "A espada do Breno é mais rápida. Kael cai no chão da floresta. Zero pontos de vida.", dict(dig=0.6)),
        ("msg", "mestre", "Kael, o Ladino, está morto.", dict(dig=0.8)),
        ("msg", "kael", "Nãããão 😭😭😭", dict(dig=0.2)),
        ("msg", "mestre", "Mortos não mandam mensagem, Kael.", dict(dig=0.3)),
        ("msg", "kael", "Desculpa 😶", dict(dig=0.2)),
        ("msg", "mestre", "Mas antes de morrer, ele quebrou um frasco. Uma fumaça roxa envolve o Sir Breno.", dict(dig=0.6)),
        ("msg", "mestre", "Sir Breno, teste de resistência contra veneno. Precisa tirar 10.", dict(dig=0.4)),
        ("msg", "dado", "Sir Breno rolou Resistência: 2.", dict(dig=0.8)),
        ("msg", "mestre", "O cavaleiro cai, desacordado.", dict(dig=0.4)),
        ("msg", "breno", "NÃOOO", dict(dig=0.2)),
        ("msg", "breno", "Bom, minha bateria tá em 2% mesmo 😩", dict(dig=0.4)),
        ("msg", "mestre", "Muito conveniente, cavaleiro.", dict(dig=0.3)),
        ("msg", "mestre", "Lia, curandeira. Agora a montanha do dragão é só sua.", dict(dig=0.6)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 4
    dict(parte=4, nome="A montanha", eventos=[
        ("chat", "guilda", "20:30", "SÁBADO"),
        ("foto", "mestre", "montanha_neve.jpg", "A Montanha de Cinzas. O vento corta como faca.", dict(pausa=0.6)),
        ("msg", "lia", "Eu subo sozinha. Pelo Breno, e pela Valdora."),
        ("msg", "mestre", "No meio da subida, uma ponte de corda velha sobre um abismo.", dict(dig=0.4)),
        ("msg", "mestre", "Teste de agilidade. Precisa tirar 15 pra atravessar.", dict(dig=0.4)),
        ("msg", "lia", "Por favor, por favor, por favor 🙏"),
        ("digitando", "dado", 2.4),
        ("msg", "dado", "Lia rolou Agilidade: 16.", dict(dig=0.2)),
        ("msg", "lia", "EU PASSEI!!"),
        ("msg", "mestre", "As cordas arrebentam logo depois que você pisa do outro lado. Não tem mais volta.", dict(dig=0.4)),
        ("chat", "breno", "20:40", "SÁBADO"),
        ("msg", "lia", "Breno, acorda! Eu cheguei na caverna do dragão sozinha!"),
        ("msg", "breno", "Lia, segura aí! Eu tô tentando voltar, juro.", dict(dig=0.4)),
        ("msg", "breno", "É que aqui no castelo... tá difícil sair agora 😬", dict(dig=0.4)),
        ("chat", "guilda", "20:45", "SÁBADO"),
        ("msg", "mestre", "A caverna está quente. Pilhas de ouro brilham no escuro. E algo enorme respira.", dict(dig=0.6)),
        ("msg", "mestre", "Dois olhos amarelos se abrem.", dict(dig=0.8)),
        ("audio", "mestre", "Curandeira tola. Você veio sozinha até o meu ninho. Eu sou Ignarok. E esta é a sua última noite."),
        ("msg", "mestre", "Role a iniciativa.", dict(dig=0.6)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 5
    dict(parte=5, nome="O dragão", fim_texto="Fim", eventos=[
        ("chat", "guilda", "20:46", None, (("chip", "SÁBADO"), ("mestre", "Role a iniciativa.", "20:45"))),
        ("msg", "dado", "Lia rolou Iniciativa: 7.", dict(dig=0.6)),
        ("msg", "mestre", "O dragão é mais rápido. Uma rajada de fogo vem na sua direção!", dict(dig=0.4)),
        ("msg", "lia", "Eu me jogo atrás das pilhas de ouro!"),
        ("msg", "breno", "VOLTEI!! Me devolveram o carregador!! Sir Breno acorda do veneno!", dict(dig=0.2)),
        ("msg", "mestre", "Só se a curandeira usar a última erva em você. Pela distância.", dict(dig=0.4)),
        ("msg", "lia", "Eu jogo a última erva no Breno!"),
        ("msg", "dado", "Lia rolou Cura: 14.", dict(dig=0.6)),
        ("msg", "mestre", "Sir Breno entra na caverna correndo, de espada em punho!", dict(dig=0.4)),
        ("msg", "breno", "Lia, segura o dragão. Eu vou no golpe final. Tudo ou nada!", dict(dig=0.3)),
        ("digitando", "dado", 3.0),
        ("foto", "dado", lambda: dado(20), "Sir Breno rolou Ataque: 20.", dict(zoom=True, pausa=0.8, h_max=520)),
        ("msg", "mestre", "VINTE CRÍTICO. A espada atravessa as escamas. Ignarok cai. VALDORA ESTÁ SALVA!", dict(dig=0.3)),
        ("msg", "lia", "AAAAAAAAA A GENTE CONSEGUIU!! 🐉⚔️"),
        ("msg", "kael", "Parabéns, gente 😭 Até eu, que tô morto, tô feliz", dict(dig=0.3)),
        ("chat", "mae", "21:30", "SÁBADO"),
        ("msg", "mae", "Lia, já são nove e meia. Desliga esse jogo e vem jantar, que a lasanha esfriou!", dict(dig=0.3)),
        ("msg", "lia", "Já vou, mãe! A gente acabou de matar o dragão 😂"),
        ("chat", "guilda", "21:31", "SÁBADO"),
        ("msg", "breno", "Mestre, melhor sessão de RPG da vida 🙌", dict(dig=0.3)),
        ("msg", "kael", "Semana que vem eu volto com um anão. Que não seja traidor 😂", dict(dig=0.3)),
        ("msg", "mestre", "Sessão encerrada. Sábado que vem, mesmo horário. E Breno: faz a lição de matemática antes, senão sua mãe confisca o carregador de novo 😂",
         dict(dig=0.4)),
        ("sistema", "Mestre mudou o nome do grupo para \"RPG da 8ª série 🎲\""),
        ("foto", "lia", "dados_rpg.jpg", "Meus dados da sorte 🎲💜", dict(pausa=0.8)),
        ("pausa", 2.4),
    ]),
]
