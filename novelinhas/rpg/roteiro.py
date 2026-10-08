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
VOZES = {"lia": THALITA, "mae": FRANCISCA, "mestre": ANTONIO, "breno": ANTONIO, "kael": ANTONIO,
         "gui": ANTONIO, "breno2": ANTONIO, "juninho": ANTONIO}
PRONUNCIA = {r"\bKael\b": "Kaél", r"\bIgnarok\b": "Iguinárok", r"\bAldric\b": "Áldric"}

PERSONAGENS = {
    "lia": dict(nome="Lia", cor=(126, 87, 194)),
    "mestre": dict(nome="Aldric, o Mago", cor=(255, 179, 0)),
    "breno": dict(nome="Sir Breno", cor=(30, 136, 229)),
    "kael": dict(nome="Kael", cor=(67, 160, 71)),
    # depois da revelação: os mesmos, com os nomes de verdade
    "gui": dict(nome="Mestre (Gui)", cor=(255, 179, 0)),
    "breno2": dict(nome="Breno", cor=(30, 136, 229)),
    "juninho": dict(nome="Juninho", cor=(67, 160, 71)),
    "mae": dict(nome="Mãe", cor=(216, 27, 96)),
}

NOMES = {"mestre": "Aldric, o Mago", "breno": "Sir Breno", "kael": "Kael, o Ladino",
         "gui": "Mestre (Gui)", "breno2": "Breno", "juninho": "Juninho"}
CHATS = {
    "guilda": dict(dono="lia", titulo="A Guilda ⚔️", grupo=True, sub="Aldric, Sir Breno, Kael, Você", nomes=NOMES),
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
    cx, cy, r = w / 2, w / 2 + 40, 180
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
    d.text((cx, cy + 25), str(n), font=zap.inter(110, 900), fill=(255, 255, 255), anchor="mm", stroke_width=6,
           stroke_fill=(30, 20, 50))
    if n == 20:
        d.text((cx, 50), "CRÍTICO!", font=zap.inter(48, 900), fill=(255, 214, 0), anchor="mm")
    return im


EPISODIOS = [
    # ---------------------------------------------------------------------------------------------- 1
    dict(parte=1, nome="A convocação", eventos=[
        ("chat", "guilda", "19:00", "SÁBADO"),
        ("msg", "mestre", "Guerreiros de Valdora. Aqui é Aldric, o mago do rei. Falo com vocês pela minha esfera de cristal.",
         dict(dig=0.6)),
        ("msg", "mestre", "Na noite passada, o dragão Ignarok queimou a ponte do norte e levou o ouro do reino.", dict(dig=0.6)),
        ("foto", "mestre", "torre_ruina.jpg", "Isto é o que restou da torre de vigia.", dict(pausa=0.6)),
        ("msg", "mestre", "O rei convoca a Guilda. Quem atende ao chamado?", dict(dig=0.4)),
        ("msg", "breno", "Pela honra da Ordem do Leão, eu vou! ⚔️", dict(dig=0.3)),
        ("foto", "breno", "armadura.jpg", "Armadura polida e pronta.", dict(pausa=0.6)),
        ("msg", "lia", "Eu levo as ervas de cura. Alguém vai precisar 🌿"),
        ("msg", "kael", "E eu levo... tudo que não estiver pregado no chão 😏", dict(dig=0.3)),
        ("msg", "mestre", "Encontrem-se na Taverna do Javali Torto antes da lua alta.", dict(dig=0.4)),
        ("chat", "guilda", "20:00"),
        ("msg", "lia", "Chegamos na taverna. O taverneiro tá olhando torto pro Kael."),
        ("msg", "kael", "Só peguei uma moedinha do balcão. Ninguém viu.", dict(dig=0.3)),
        ("msg", "breno", "Todo mundo viu, Kael. Ele tá vindo com um porrete 😂", dict(dig=0.3)),
        ("msg", "breno", "Eu pago a bebida de todo mundo pra ninguém brigar 🍺", dict(dig=0.3)),
        ("msg", "lia", "Gente. Um velho encapuzado tá me chamando lá no fundo."),
        ("audio", "lia", "Ele falou assim, bem baixinho: o dragão não age sozinho. Alguém desta guilda já fez um acordo com ele."),
        ("msg", "breno", "Quem?? Pergunta quem!", dict(dig=0.2)),
        ("msg", "lia", "Ele sumiu. Virou fumaça na minha frente."),
        ("msg", "mestre", "Cuidado. Uma sombra gigante acaba de cobrir a lua sobre a taverna.", dict(dig=0.6)),
        ("foto", "mestre", "iluminura_dragao.jpg", "Minha esfera mostrou isto. Ignarok está vindo.", dict(zoom=True, pausa=0.8, h_max=600)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 2
    dict(parte=2, nome="A floresta sombria", eventos=[
        ("chat", "guilda", "21:00", "SÁBADO"),
        ("foto", "lia", "floresta_nevoa.jpg", "Entramos na Floresta Sombria. Nenhum pássaro canta aqui.", dict(pausa=0.6)),
        ("msg", "breno", "Eu vou na frente, com o escudo levantado 🛡️", dict(dig=0.3)),
        ("msg", "mestre", "Os galhos estão se mexendo sem vento. Goblins. Cinco deles, nas árvores.", dict(dig=0.4)),
        ("msg", "breno", "ELES PULARAM EM CIMA DA GENTE!", dict(dig=0.2)),
        ("msg", "breno", "Derrubei o maior! Mas levei uma flechada no ombro 😵", dict(dig=0.3)),
        ("msg", "lia", "Breno, segura firme! Tô passando as ervas!"),
        ("msg", "breno", "Tá fechando... tá brilhando verde. Lia, você é incrível 🙏", dict(dig=0.4)),
        ("msg", "mestre", "Os goblins fugiram para a névoa. Mas fiquem atentos. Eles não atacaram por acaso.", dict(dig=0.4)),
        ("msg", "breno", "Gente, volto já. Me chamaram lá no castelo, não posso negar.", dict(dig=0.4)),
        ("msg", "lia", "Vai e volta rápido!"),
        ("msg", "mestre", "Lia. Onde está o Kael? E o mapa do reino, que estava com o Breno?", dict(dig=0.6)),
        ("msg", "lia", "O MAPA SUMIU."),
        ("chat", "kael", "21:20", "SÁBADO"),
        ("msg", "kael", "Lia. Só você.", dict(dig=0.4)),
        ("msg", "kael", "Eu tô com o mapa. Confia em mim. Não conta pro Breno.", dict(dig=0.6)),
        ("msg", "lia", "Kael, o velho da taverna falou que alguém da guilda fez acordo com o dragão."),
        ("msg", "kael", "Então você já sabe quem é 🙂", dict(dig=0.8)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 3
    dict(parte=3, nome="A traição", eventos=[
        ("chat", "guilda", "21:40", "SÁBADO"),
        ("msg", "breno", "Voltei! O que aconteceu?", dict(dig=0.3)),
        ("msg", "lia", "O Kael roubou o mapa. Ele fez acordo com o dragão."),
        ("msg", "kael", "Acordo, não. Negócio. O Ignarok me paga mil moedas de ouro por cada cavaleiro 😏", dict(dig=0.4)),
        ("msg", "breno", "TRAIDOR! Eu te desafio pra um duelo! ⚔️", dict(dig=0.2)),
        ("msg", "kael", "Vem, cavaleiro. Eu sou mais rápido que você.", dict(dig=0.3)),
        ("msg", "lia", "Para, vocês dois!"),
        ("pausa", 1.6),
        ("msg", "breno", "Acabou. O Kael caiu.", dict(dig=0.8)),
        ("msg", "mestre", "Kael, o Ladino, não se levanta mais. Que os deuses tenham piedade dele.", dict(dig=0.6)),
        ("msg", "breno", "Lia... ele quebrou um frasco antes de cair. Tem uma fumaça roxa em volta de mim.", dict(dig=0.4)),
        ("msg", "lia", "Não respira! Breno, sai daí!"),
        ("msg", "breno", "Tá tudo girando...", dict(dig=0.6)),
        ("msg", "mestre", "Veneno de sono de dragão. O cavaleiro caiu, desacordado.", dict(dig=0.6)),
        ("msg", "lia", "Aldric, me diz que ele vai acordar."),
        ("msg", "mestre", "Só quando o dragão morrer, curandeira. O veneno é dele.", dict(dig=0.6)),
        ("msg", "mestre", "Agora a montanha é só sua.", dict(dig=0.6)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 4
    dict(parte=4, nome="A montanha", eventos=[
        ("chat", "guilda", "22:00", "SÁBADO"),
        ("foto", "lia", "montanha_neve.jpg", "A Montanha de Cinzas. O vento corta como faca.", dict(pausa=0.6)),
        ("msg", "lia", "Eu subo sozinha. Pelo Breno, e pela Valdora."),
        ("msg", "mestre", "No meio da subida há uma ponte de corda velha sobre o abismo. Não olhe para baixo.", dict(dig=0.4)),
        ("msg", "lia", "Tô atravessando... uma tábua quebrou 😱"),
        ("pausa", 1.6),
        ("msg", "lia", "CONSEGUI PASSAR!!"),
        ("msg", "lia", "Meu coração tá saindo pela boca 😮‍💨"),
        ("msg", "mestre", "As cordas arrebentaram logo atrás de você. Não existe mais caminho de volta.", dict(dig=0.4)),
        ("chat", "breno", "22:10", "SÁBADO"),
        ("msg", "lia", "Breno, acorda! Eu tô sozinha na porta da caverna do dragão!"),
        ("pausa", 1.6),
        ("status", "visto por último hoje às 21:52"),
        ("chat", "guilda", "22:15"),
        ("msg", "mestre", "A caverna está quente. Montanhas de ouro brilham no escuro. E algo enorme respira.", dict(dig=0.6)),
        ("msg", "mestre", "Dois olhos amarelos se abrem.", dict(dig=0.8)),
        ("audio", "mestre", "Curandeira tola. Você veio sozinha até o meu ninho. Eu sou Ignarok. E esta é a sua última noite."),
        ("msg", "lia", "Aldric... o dragão falou comigo."),
        ("msg", "mestre", "Então lute, Lia. A Valdora inteira depende de você.", dict(dig=0.6)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 5
    dict(parte=5, nome="O dragão", fim_texto="Fim", eventos=[
        ("chat", "guilda", "22:16", None, (("chip", "SÁBADO"), ("mestre", "Então lute, Lia. A Valdora inteira depende de você.", "22:15"))),
        ("msg", "mestre", "Ignarok abre a boca. Uma rajada de fogo vem na sua direção!", dict(dig=0.4)),
        ("msg", "lia", "Eu me jogo atrás das pilhas de ouro!"),
        ("msg", "breno", "LIA! Acordei! Tô subindo a montanha correndo!", dict(dig=0.2)),
        ("msg", "lia", "Breno?? Como você acordou?"),
        ("msg", "breno", "Não importa! Distrai o dragão, que eu vou no golpe final. Tudo ou nada!", dict(dig=0.3)),
        ("msg", "lia", "EI, IGNAROK! AQUI!"),
        ("pausa", 1.4),
        ("msg", "mestre", "A espada de Sir Breno atravessa as escamas. Ignarok cai. VALDORA ESTÁ SALVA!", dict(dig=0.6)),
        ("msg", "lia", "AAAAAAAAA A GENTE CONSEGUIU!! 🐉⚔️"),
        ("pausa", 1.0),
        ("sistema", "Sir Breno mudou o nome para \"Breno\""),
        ("foto", "breno2", lambda: dado(20), "TIREI VINTE NO DADO, GENTE!! VINTE!!", dict(zoom=True, pausa=0.8, h_max=520)),
        ("sistema", "Aldric, o Mago mudou o nome para \"Mestre (Gui)\""),
        ("msg", "gui", "Vinte natural no último ataque, Breno. Isso é lendário 😂", dict(dig=0.3)),
        ("sistema", "Kael, o Ladino mudou o nome para \"Juninho\""),
        ("msg", "juninho", "Gui, posso voltar agora? Tô morto faz uma hora 😂", dict(dig=0.3)),
        ("msg", "gui", "Semana que vem você faz outro personagem. De preferência um que não seja traidor 😂", dict(dig=0.3)),
        ("chat", "mae", "22:30", "SÁBADO"),
        ("msg", "mae", "Lia, já são dez e meia. Desliga esse jogo e vai dormir! Amanhã tem missa!", dict(dig=0.3)),
        ("msg", "lia", "Já vou, mãe! A gente acabou de matar o dragão 😂"),
        ("chat", "guilda", "22:31"),
        ("msg", "breno2", "Gui, melhor sessão de RPG da vida 🙌", dict(dig=0.3)),
        ("msg", "gui", "Sessão encerrada! Sábado que vem, mesmo horário. E Breno: faz a lição de matemática antes 😂", dict(dig=0.4)),
        ("sistema", "Mestre (Gui) mudou o nome do grupo para \"RPG da 8ª série\""),
        ("foto", "lia", "dados_rpg.jpg", "Meus dados da sorte 🎲💜", dict(pausa=0.8)),
        ("pausa", 2.4),
    ]),
]
