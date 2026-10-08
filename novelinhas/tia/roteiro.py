"""15 Anos: novela em 5 partes do Compartilhado. Baseada numa história real da família do dono (nomes trocados).

A Tia Sandra está casada há 15 anos com o Valmir (mecânico, que ama o carro vermelho dele). O Jean, marido da Kelly
(sobrinha da Sandra, filha da irmã dela, a Lúcia, e mãe do pequeno Arthur), descobre que o Valmir e a Kelly têm um caso.
Tudo explode no grupo da família, a Sandra fica paranoica perguntando "você sabia?" para todo mundo, o Valmir vai morar
com a Kelly, e meses depois a tia aparece bonitona, viajando sozinha.
"""
import functools
import os

from PIL import Image, ImageDraw

import zap

FOTOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fotos")
TITULO = "15 Anos"

THALITA = ("pt-BR-ThalitaMultilingualNeural", "+0%", "+0Hz")
ANTONIO = ("pt-BR-AntonioNeural", "+0%", "+0Hz")
FRANCISCA = ("pt-BR-FranciscaNeural", "+0%", "+0Hz")
PRONUNCIA = {r"\bKelly\b": "Quéli"}
VOZES = {"sandra": THALITA, "marcia": THALITA, "tati": THALITA, "kelly": FRANCISCA, "lucia": FRANCISCA,
         "valmir": ANTONIO, "jean": ANTONIO, "igor": ANTONIO}

PERSONAGENS = {
    "sandra": dict(nome="Sandra", cor=(194, 24, 91)),
    "valmir": dict(nome="Valmir", cor=(93, 64, 55)),
    "kelly": dict(nome="Kelly", cor=(142, 36, 170)),
    "jean": dict(nome="Jean", cor=(21, 101, 192)),
    "lucia": dict(nome="Lúcia", cor=(0, 137, 123)),
    "igor": dict(nome="Igor", cor=(230, 81, 0)),
    "marcia": dict(nome="Márcia", cor=(46, 125, 50)),
    "tati": dict(nome="Tati", cor=(233, 30, 99)),
}

NOMES = {"valmir": "Valmir", "kelly": "Kelly", "jean": "Jean", "lucia": "Lúcia", "igor": "Igor", "marcia": "Márcia"}
CHATS = {
    "familia": dict(dono="sandra", titulo="Família Souza 💛", grupo=True,
                    sub="Lúcia, Kelly, Jean, Valmir, Igor, Márcia, Você", nomes=NOMES),
    "jean": dict(dono="sandra", titulo="Jean (marido da Kelly)", com="jean", sub="online"),
    "valmir": dict(dono="sandra", titulo="Valmir ❤️", com="valmir", sub="online"),
    "kelly": dict(dono="sandra", titulo="Kelly (sobrinha)", com="kelly", sub="online"),
    "lucia": dict(dono="sandra", titulo="Lúcia (mana)", com="lucia", sub="online"),
    "igor": dict(dono="sandra", titulo="Igor (sobrinho)", com="igor", sub="online"),
    "marcia": dict(dono="sandra", titulo="Márcia (cunhada)", com="marcia", sub="online"),
    "tati": dict(dono="sandra", titulo="Tati Manicure 💅", com="tati", sub="online"),
}


def _foto(nome):
    return Image.open(os.path.join(FOTOS, nome)).convert("RGB")


@functools.lru_cache(None)
def notificacao():
    """Foto (tirada pelo Jean) da tela de bloqueio da Kelly com a notificação do 'Val 🔧'."""
    w, h = 720, 760
    im = Image.new("RGB", (w, h), (20, 20, 30))
    d0 = ImageDraw.Draw(im)
    for y in range(h):   # papel de parede em degradê (roxo para azul)
        k = y / h
        d0.line([(0, y), (w, y)], fill=(int(70 - 40 * k), int(40 + 10 * k), int(110 + 30 * k)))
    im = im.convert("RGBA")
    d = ImageDraw.Draw(im)
    d.text((w // 2, 120), "21:12", font=zap.inter(110, 300), fill=(255, 255, 255), anchor="mm")
    d.text((w // 2, 200), "domingo, 17 de agosto", font=zap.inter(30, 500), fill=(235, 235, 235), anchor="mm")
    y = 330
    d.rounded_rectangle((30, y, w - 30, y + 170), 34, fill=(245, 245, 245, 235))
    ic = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    ImageDraw.Draw(ic).rounded_rectangle((0, 0, 63, 63), 16, fill=(37, 211, 102))
    im.alpha_composite(ic, (56, y + 26))
    d.text((140, y + 40), "WhatsApp", font=zap.inter(26, 600), fill=(90, 90, 90), anchor="lm")
    d.text((w - 60, y + 40), "agora", font=zap.inter(24, 500), fill=(120, 120, 120), anchor="rm")
    zap.texto_rico(im, 140, y + 62, "Val 🔧", zap.inter(32, 750), (20, 20, 20))
    zap.texto_rico(im, 140, y + 106, "saudade de ontem 🔥", zap.inter(32, 450), (30, 30, 30))
    return im.convert("RGB")


@functools.lru_cache(None)
def tabela_datas():
    """As datas que o Jean e a Sandra cruzaram: 'hora extra' dele = 'academia' dela."""
    w = 820
    linhas = [("Ter 15/07", "hora extra", "academia"), ("Qui 24/07", "hora extra", "academia"),
              ("Ter 05/08", "hora extra", "academia"), ("Qui 07/08", "hora extra", "academia"),
              ("Ter 12/08", "hora extra", "academia"), ("Dom 17/08", "hora extra", "academia")]
    h = 240 + len(linhas) * 80
    im = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, 110), fill=(55, 71, 79))
    d.text((34, 55), "Agenda do Jean", font=zap.inter(40, 800), fill=(255, 255, 255), anchor="lm")
    d.text((34, 150), "Dia", font=zap.inter(30, 800), fill=(90, 90, 90), anchor="lm")
    d.text((330, 150), "Valmir", font=zap.inter(30, 800), fill=(93, 64, 55), anchor="lm")
    d.text((590, 150), "Kelly", font=zap.inter(30, 800), fill=(142, 36, 170), anchor="lm")
    y = 200
    for dia, a, b in linhas:
        d.rounded_rectangle((20, y - 4, w - 20, y + 64), 10, fill=(255, 241, 118) if dia.startswith("Dom 17") else (246, 246, 246))
        d.text((34, y + 30), dia, font=zap.inter(30, 600), fill=(40, 40, 40), anchor="lm")
        d.text((330, y + 30), a, font=zap.inter(30, 500), fill=(40, 40, 40), anchor="lm")
        d.text((590, y + 30), b, font=zap.inter(30, 500), fill=(40, 40, 40), anchor="lm")
        y += 80
    return im


EPISODIOS = [
    # ---------------------------------------------------------------------------------------------- 1
    dict(parte=1, nome="15 anos", eventos=[
        ("chat", "familia", "08:00", "HOJE"),
        ("foto", "sandra", "rosas.jpg", "15 anos com o amor da minha vida 💛"),
        ("msg", "lucia", "Parabéns, mana! Casal abençoado 🥰", dict(dig=0.3)),
        ("msg", "kelly", "Que lindos 🥹 O tio Val é tudo", dict(dig=0.3)),
        ("msg", "igor", "Parabéns, tia e tio! 🎉", dict(dig=0.3)),
        ("msg", "marcia", "Casal vinte! 😍", dict(dig=0.3)),
        ("msg", "valmir", "Te amo, nega 💛", dict(dig=0.4)),
        ("msg", "sandra", "Obrigada, família! Hoje tem churrasco aqui em casa 🍖"),
        ("msg", "kelly", "Eu levo o vinagrete, tia 😘", dict(dig=0.3)),
        ("chat", "jean", "21:30", "HOJE"),
        ("msg", "jean", "Tia, desculpa te chamar essa hora.", dict(dig=0.4)),
        ("msg", "jean", "Posso te perguntar uma coisa?", dict(dig=0.4)),
        ("msg", "sandra", "Claro, Jean. Aconteceu alguma coisa com o Arthur?"),
        ("msg", "jean", "Não, o Arthur tá dormindo.", dict(dig=0.4)),
        ("msg", "jean", "O tio Valmir tem dado carona pra Kelly todo dia?", dict(dig=0.6)),
        ("msg", "sandra", "Carona? Ele sai cedo pra oficina naquele carro vermelho dele..."),
        ("msg", "jean", "A Kelly disse que é ele que leva ela pra academia.", dict(dig=0.4)),
        ("msg", "sandra", "Ele nunca me falou isso."),
        ("msg", "jean", "Ela também não me contava. Eu só soube porque o vizinho comentou.", dict(dig=0.4)),
        ("digitando", "jean", 2.2),
        ("msg", "jean", "Tia... eu vi isso no celular dela agora há pouco.", dict(dig=0.4)),
        ("foto", "jean", notificacao, None, dict(zoom=True, pausa=3.2, h_max=620)),
        ("msg", "jean", "Val. Com chave de mecânico. 🔧"),
        ("rascunho", "Deve ser outro Val", 1.4),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 2
    dict(parte=2, nome="Hora extra", eventos=[
        ("chat", "valmir", "21:45", "HOJE", (("chip", "HOJE"), ("valmir", "Hoje vou fazer hora extra, nega. Não me espera pra jantar", "17:10"))),
        ("msg", "sandra", "Valmir, você tá dando carona pra Kelly?"),
        ("msg", "valmir", "Dei umas vezes, ué. É caminho.", dict(dig=0.4)),
        ("msg", "sandra", "E esse \"saudade de ontem\" com foguinho que você mandou pra ela?"),
        ("digitando", "valmir", 3.0),
        ("msg", "valmir", "Que isso, Sandra? Isso é coisa da cabeça do Jean. Ele é ciumento.", dict(dig=0.2)),
        ("msg", "valmir", "Tô chegando, a gente conversa em casa.", dict(dig=0.3)),
        ("chat", "jean", "23:10", "HOJE"),
        ("msg", "sandra", "Jean, ele disse que você é ciumento."),
        ("msg", "jean", "Tia, eu anotei tudo. Olha isso.", dict(dig=0.4)),
        ("foto", "jean", tabela_datas, None, dict(zoom=True, pausa=3.4, h_max=640)),
        ("msg", "jean", "Toda vez que ele faz hora extra, ela vai pra academia.", dict(dig=0.4)),
        ("msg", "jean", "E ela nunca volta suada.", dict(dig=0.6)),
        ("msg", "sandra", "Hoje ele fez hora extra de novo. No dia do nosso aniversário de casamento."),
        ("msg", "jean", "E hoje a Kelly foi pra academia.", dict(dig=0.6)),
        ("chat", "jean", "14:05", "QUINTA"),
        ("msg", "jean", "Tia, eu saí mais cedo do trabalho e passei na frente de casa agora.", dict(dig=0.4)),
        ("foto", "jean", "carro_vermelho.jpg", "O carro do tio tá parado na minha porta. Duas da tarde.",
         dict(zoom=True, pausa=0.8, h_max=520)),
        ("msg", "jean", "Era pra Kelly tá na academia.", dict(dig=0.4)),
        ("rascunho", "Eu tô indo", 1.2),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 3
    dict(parte=3, nome="O grupo da família", eventos=[
        ("chat", "familia", "14:20", "QUINTA", (("chip", "DOMINGO"), ("sandra", "15 anos com o amor da minha vida 💛", "08:00"),
                                                ("valmir", "Te amo, nega 💛", "08:05"))),
        ("msg", "sandra", "Valmir, por que o seu carro tá na porta da Kelly às duas da tarde?"),
        ("pausa", 1.4),
        ("msg", "lucia", "Mana?? Que pergunta é essa no grupo da família?", dict(dig=0.3)),
        ("msg", "igor", "Eita 😳", dict(dig=0.2)),
        ("msg", "marcia", "Gente...", dict(dig=0.4)),
        ("msg", "kelly", "Tia, o tio veio consertar o chuveiro aqui.", dict(dig=0.8)),
        ("msg", "sandra", "Consertar chuveiro no horário da academia, Kelly?"),
        ("msg", "jean", "Kelly, o chuveiro tá ótimo. Eu tomei banho hoje de manhã.", dict(dig=0.3)),
        ("msg", "lucia", "Sandra, você tá acusando a minha filha?", dict(dig=0.3)),
        ("msg", "sandra", "Não, Lúcia. Eu tô perguntando pro meu marido."),
        ("digitando", "valmir", 2.0),
        ("msg", "valmir", "Sandra, a gente conversa em casa."),
        ("msg", "jean", "Fala aqui, tio. Na frente de todo mundo.", dict(dig=0.3)),
        ("msg", "kelly", "Jean, para.", dict(dig=0.3)),
        ("digitando", "valmir", 3.0),
        ("msg", "valmir", "É verdade. A gente tá junto faz oito meses.", dict(dig=0.2)),
        ("sistema", "Jean saiu"),
        ("msg", "lucia", "Meu Deus do céu.", dict(dig=0.4)),
        ("msg", "marcia", "Eu não acredito nisso.", dict(dig=0.4)),
        ("msg", "igor", "Tia, se precisar de alguma coisa, eu tô aqui.", dict(dig=0.4)),
        ("chat", "kelly", "14:40", "QUINTA"),
        ("msg", "kelly", "Tia, eu nunca quis te machucar.", dict(dig=0.6)),
        ("msg", "sandra", "Oito meses, Kelly. Eu troquei a sua fralda."),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 4
    dict(parte=4, nome="Você sabia?", eventos=[
        ("chat", "lucia", "15:00", "QUINTA"),
        ("msg", "sandra", "Lúcia. Você sabia?"),
        ("msg", "lucia", "Mana, eu juro que não!", dict(dig=0.3)),
        ("msg", "sandra", "Você é a mãe dela. Você SABIA?"),
        ("msg", "lucia", "Eu achava estranho tanta carona... mas nunca imaginei.", dict(dig=0.6)),
        ("msg", "sandra", "ACHAVA ESTRANHO?"),
        ("msg", "sandra", "Ela dormia na minha casa quando era pequena, Lúcia."),
        ("msg", "lucia", "Eu sei, mana. Eu tô morrendo de vergonha.", dict(dig=0.6)),
        ("chat", "igor", "15:10", "QUINTA"),
        ("msg", "sandra", "Igor, você sabia?"),
        ("msg", "igor", "Tia, eu juro que não sabia de nada 😭", dict(dig=0.4)),
        ("msg", "sandra", "Então por que você demorou pra responder?"),
        ("msg", "igor", "Eu tava no banho, tia!!", dict(dig=0.2)),
        ("chat", "marcia", "15:20", "QUINTA"),
        ("msg", "sandra", "Márcia, você sabia?"),
        ("digitando", "marcia", 2.0),
        ("msg", "marcia", "Ai, Sandra... no Natal eu vi o Valmir dando presente pra ela antes de dar o seu."),
        ("msg", "sandra", "E NÃO ME CONTOU??"),
        ("msg", "marcia", "Achei que era amigo secreto 😬", dict(dig=0.4)),
        ("chat", "tati", "15:30", "QUINTA"),
        ("msg", "sandra", "Tati, você sabia?"),
        ("msg", "tati", "Sabia o quê, Dona Sandra? 😳", dict(dig=0.3)),
        ("msg", "sandra", "Nada não. Quinta às dez tá confirmado."),
        ("chat", "jean", "16:00", "QUINTA"),
        ("msg", "sandra", "Jean, você sabia antes de me contar?"),
        ("msg", "jean", "Tia, eu te contei no mesmo dia que eu vi.", dict(dig=0.4)),
        ("msg", "sandra", "Desculpa, Jean. Eu tô desconfiando até da minha sombra."),
        ("chat", "valmir", "21:00", "QUINTA"),
        ("msg", "valmir", "Sandra, amanhã eu pego as minhas coisas.", dict(dig=0.6)),
        ("msg", "valmir", "Vou ficar na casa da Kelly.", dict(dig=0.8)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 5
    dict(parte=5, nome="A tia ficou bonitona", fim_texto="Fim", eventos=[
        ("chat", "familia", "16:00", "UM ANO DEPOIS"),
        ("foto", "sandra", "drink_praia.jpg", "Primeira viagem sozinha. Nunca me senti tão bem 🏖️"),
        ("msg", "lucia", "Mana, que linda!! 😍", dict(dig=0.3)),
        ("msg", "marcia", "Tá maravilhosa, Sandra! 🔥", dict(dig=0.3)),
        ("msg", "igor", "A tia tá voando 😍", dict(dig=0.3)),
        ("msg", "sandra", "Perdi dezoito quilos na academia. E noventa de marido 😂"),
        ("msg", "igor", "KKKKKKKK A TIA NÃO PERDOA", dict(dig=0.2)),
        ("msg", "kelly", "Tá bonita, tia.", dict(dig=1.0)),
        ("pausa", 1.2),
        ("chat", "valmir", "16:30", "UM ANO DEPOIS"),
        ("msg", "valmir", "Sandra, vi a sua foto. Você tá linda.", dict(dig=0.6)),
        ("msg", "valmir", "Eu errei feio.", dict(dig=0.8)),
        ("msg", "sandra", "Você errou por quinze anos, Valmir. O meu erro acabou."),
        ("msg", "valmir", "A gente podia tomar um café qualquer dia...", dict(dig=0.6)),
        ("msg", "sandra", "Café eu tomo aqui, de frente pro mar. Tchau."),
        ("sistema", "Você bloqueou este contato"),
        ("chat", "jean", "17:00", "UM ANO DEPOIS"),
        ("msg", "jean", "Tia, vi as fotos. Você tá incrível!", dict(dig=0.4)),
        ("msg", "sandra", "Obrigada, Jean! E o Arthur?"),
        ("msg", "jean", "Tá enorme. E eu tô namorando de novo 😊", dict(dig=0.4)),
        ("msg", "sandra", "Isso! A gente merece ser feliz 💛"),
        ("msg", "jean", "E o Arthur perguntou da senhora. Quer ir na praia com a tia-avó 😂", dict(dig=0.4)),
        ("msg", "sandra", "Traz ele no domingo! A tia-avó paga o sorvete 🍦"),
        ("pausa", 2.4),
    ]),
]
