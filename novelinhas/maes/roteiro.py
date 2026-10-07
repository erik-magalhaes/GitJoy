"""Grupo das Mães: novela em 5 partes do Compartilhado.

No grupo do 3º ano B, a Cris (mãe representante) organiza a vaquinha da festa junina e a Jaqueline cuida do
dinheiro. O envelope some, a Jaqueline acusa a Cris e vaza um áudio dela falando mal da Renata (mãe nova).
A Renata descobre que a Cris está desempregada (o filho é bolsista) e que a Jaqueline mentiu: o dinheiro virou
a decoração do aniversário do filho dela, como o Marcos (o único pai do grupo) deixa escapar.
"""
import functools
import os

from PIL import Image, ImageDraw

import zap
from sogra.roteiro import print_conversa

FOTOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fotos")
TITULO = "Grupo das Mães"

FRANCISCA = ("pt-BR-FranciscaNeural", "+0%", "+0Hz")
ANTONIO = ("pt-BR-AntonioNeural", "+0%", "+0Hz")
VOZES = {"renata": FRANCISCA, "cris": FRANCISCA, "jaque": FRANCISCA, "paula": FRANCISCA, "ana": FRANCISCA,
         "marcos": ANTONIO}

PERSONAGENS = {
    "renata": dict(nome="Renata", cor=(0, 137, 123)),
    "cris": dict(nome="Cris", cor=(194, 24, 91)),
    "jaque": dict(nome="Jaqueline", cor=(239, 108, 0)),
    "paula": dict(nome="Paula", cor=(94, 53, 177)),
    "ana": dict(nome="Professora Ana", cor=(46, 125, 50)),
    "marcos": dict(nome="Marcos", cor=(21, 101, 192)),
}

CHATS = {
    "grupo": dict(dono="renata", titulo="3º ano B 🍎 Mães (e pai)", grupo=True,
                  sub="Cris, Jaqueline, Paula, Marcos, Prof. Ana, Você e mais 19",
                  nomes={"cris": "Cris (representante)", "jaque": "Jaqueline (mãe do Enzo)", "paula": "Paula (mãe da Lívia)",
                         "ana": "Prof. Ana", "marcos": "Marcos (pai do Pedro)"}),
    "paula": dict(dono="renata", titulo="Paula (mãe da Lívia)", com="paula", sub="online"),
    "cris": dict(dono="renata", titulo="Cris (representante)", com="cris", sub="online"),
}


def _foto(nome, w, h):
    im = Image.open(os.path.join(FOTOS, nome)).convert("RGB")
    esc = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * esc), round(im.height * esc)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


@functools.lru_cache(None)
def decoracao():
    """Orçamento da decoração que a Jaqueline mostra no dia da vaquinha."""
    w, h = 900, 760
    im = Image.new("RGBA", (w, h), (255, 248, 225, 255))
    d = ImageDraw.Draw(im)
    im.paste(_foto("bandeirinhas.jpg", 560, 520), (20, 120))
    im.paste(_foto("lanterna_chita.jpg", 300, 520), (580, 120))
    zap.texto_rico(im, 24, 24, "Decoração do Arraiá 3º B 🌽", zap.inter(48, 900), (183, 28, 28))
    d.rectangle((0, 660, w, h), fill=(183, 28, 28))
    d.text((24, 690), "Bandeirinhas e balões de chita · R$ 1.150", font=zap.inter(36, 700), fill=(255, 255, 255))
    return im.convert("RGB")


@functools.lru_cache(None)
def aniversario():
    """Foto do aniversário do Enzo, com a mesma decoração."""
    w, h = 900, 900
    im = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    fundo = _foto("bandeirinhas.jpg", w, h)
    im.paste(fundo, (0, 0))
    im.paste(_foto("lanterna_chita.jpg", 300, 460), (560, 300))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((60, 640, 520, 820), 24, fill=(255, 255, 255))
    zap.texto_rico(im, 90, 660, "Arraiá do Enzo 🤠", zap.inter(48, 900), (183, 28, 28))
    zap.texto_rico(im, 90, 740, "7 aninhos 🎂", zap.inter(40, 700), (60, 60, 60))
    d.text((24, 20), "@jaque.mae.do.enzo", font=zap.inter(30, 700), fill=(255, 255, 255))
    return im.convert("RGB")


@functools.lru_cache(None)
def print_jaque():
    """O print que prova que o envelope ficou com a Jaqueline."""
    return print_conversa("Jaqueline (mãe do Enzo)", PERSONAGENS["jaque"]["cor"], (
        ("cris", "Jaque, o envelope da vaquinha tá com você?", "19:02"),
        ("jaque", "Tá sim, Cris! Ficou comigo, eu compro a decoração na sexta 😘", "19:10"),
    ), hora="19:11", dono="cris")


EPISODIOS = [
    # ---------------------------------------------------------------------------------------------- 1
    dict(parte=1, nome="A vaquinha", eventos=[
        ("chat", "grupo", "08:00", "HOJE"),
        ("msg", "ana", "Bom dia, mamães e papai! Nossa festa junina vai ser dia 24 🌽"),
        ("msg", "cris", "Como representante, eu proponho uma vaquinha de cinquenta reais por família, pra decoração e comida."),
        ("msg", "jaque", "Eu cuido do dinheiro, como sempre 💰 Podem me entregar na portaria!"),
        ("foto", "jaque", decoracao, "Já até escolhi a decoração 😍", dict(zoom=True, pausa=0.6, h_max=520)),
        ("msg", "marcos", "Bom dia! Pago o meu e o de quem precisar 🤠"),
        ("msg", "paula", "O Marcos, sempre um cavalheiro 😍"),
        ("msg", "marcos", "Professora, o Pedro pode ir de caipira ou de cowboy?"),
        ("msg", "ana", "Pode ir do que quiser, Marcos 😄"),
        ("msg", "renata", "Oi, gente! Eu sou a Renata, mãe do Theo, aluno novo. Já vou entregar o meu 💛"),
        ("chat", "paula", "08:20", "HOJE"),
        ("msg", "paula", "Renata, bem-vinda ao grupo mais perigoso da escola 😂"),
        ("msg", "renata", "Perigoso?"),
        ("msg", "paula", "A Cris manda, a Jaqueline fofoca e todo mundo baba no Marcos."),
        ("msg", "renata", "E o Marcos?"),
        ("msg", "paula", "Viúvo, lindo e cozinha. O grupo inteiro suspira."),
        ("msg", "renata", "Entendi o \"baba no Marcos\" 😂"),
        ("msg", "paula", "Uma dica: nunca discorda da Cris no grupo."),
        ("msg", "renata", "Anotado 😅"),
        ("chat", "grupo", "21:00"),
        ("chip", "UMA SEMANA DEPOIS"),
        ("msg", "jaque", "Gente...", dict(dig=0.6)),
        ("msg", "jaque", "Alguém viu o envelope do dinheiro da festa? 😰", dict(dig=0.8)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 2
    dict(parte=2, nome="Cadê o dinheiro?", eventos=[
        ("chat", "grupo", "21:02", None, (("chip", "HOJE"), ("jaque", "Alguém viu o envelope do dinheiro da festa? 😰", "21:00"))),
        ("msg", "jaque", "Eu deixei o envelope com a Cris na reunião de quinta. Agora ela diz que não pegou 🤷‍♀️"),
        ("msg", "cris", "Mentira, Jaqueline! Você nunca me entregou envelope nenhum!", dict(dig=0.3)),
        ("msg", "jaque", "Mil cento e cinquenta reais, gente. Sumiram."),
        ("msg", "paula", "Meu Deus 😳 E a decoração, Jaqueline? Já foi comprada?", dict(dig=0.3)),
        ("msg", "jaque", "Claro que não, né! Sem o dinheiro!"),
        ("msg", "marcos", "Gente, calma. Vamos conversar."),
        ("msg", "jaque", "Calma nada. E tem mais: olhem o que a Cris fala da mãe nova."),
        ("audio", "jaque", "Essa Renata chegou agora e já quer palpitar em tudo. Mãe de aluno novo devia ficar quietinha.",
         dict(voz="cris", enc=True)),
        ("msg", "renata", "Cris?? Eu nem falei nada!"),
        ("msg", "cris", "Esse áudio é de outro contexto! Jaqueline, você é uma cobra!"),
        ("msg", "ana", "Mamães, por favor. Respeito no grupo."),
        ("chat", "paula", "21:15"),
        ("msg", "renata", "Paula, o que foi aquilo?"),
        ("msg", "paula", "Bem-vinda ao 3º B 😬"),
        ("msg", "renata", "E eu que já paguei os meus cinquenta 😩"),
        ("msg", "renata", "A Cris falou mal de mim mesmo?"),
        ("msg", "paula", "A voz é dela. Mas a Jaqueline guardou esse áudio por quanto tempo, né?"),
        ("chat", "cris", "21:30", "HOJE"),
        ("msg", "cris", "Renata, precisamos conversar.", dict(dig=0.6)),
        ("msg", "cris", "Não é o que parece.", dict(dig=0.6)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 3
    dict(parte=3, nome="A eleição", eventos=[
        ("chat", "cris", "21:32", None, (("chip", "HOJE"), ("cris", "Renata, precisamos conversar.", "21:30"),
                                         ("cris", "Não é o que parece.", "21:30"))),
        ("msg", "cris", "Eu falei aquilo num dia ruim, pra uma amiga. Me desculpa."),
        ("msg", "renata", "Mas você falou, Cris."),
        ("msg", "cris", "Eu sei. Eu errei com você. Mas nisso eu sou inocente. Eu juro que não peguei o dinheiro."),
        ("chat", "grupo", "08:10", "HOJE"),
        ("msg", "jaque", "Proposta: nova eleição de mãe representante! Eu indico a Renata 🙋‍♀️"),
        ("msg", "paula", "Ué, Jaqueline, desde quando você gosta da Renata?"),
        ("msg", "renata", "Gente, eu acabei de chegar. Não quero ser representante de nada."),
        ("msg", "jaque", "Mas você é perfeita pro cargo, Renata 😘"),
        ("msg", "marcos", "Eu voto em quem trouxer o bolo de milho 🌽"),
        ("msg", "jaque", "Votação até sexta, pessoal!"),
        ("msg", "cris", "Tudo bem. Façam a votação."),
        ("chat", "paula", "08:30"),
        ("msg", "renata", "Paula, por que a Jaqueline tá me usando?"),
        ("msg", "paula", "Pra tirar a Cris. A Jaqueline quer mandar nesse grupo há anos."),
        ("msg", "paula", "Repara: desde que o dinheiro sumiu, a Jaqueline tá toda boazinha com você."),
        ("msg", "renata", "E se a Cris for inocente?"),
        ("msg", "paula", "Aí alguém tá mentindo. E não é pouca coisa."),
        ("chat", "cris", "22:00"),
        ("msg", "cris", "Renata... posso te contar uma coisa?", dict(dig=0.8)),
        ("msg", "cris", "Ninguém nesse grupo sabe.", dict(dig=0.8)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 4
    dict(parte=4, nome="O segredo da Cris", eventos=[
        ("chat", "cris", "22:01", None, (("chip", "HOJE"), ("cris", "Renata... posso te contar uma coisa?", "22:00"),
                                         ("cris", "Ninguém nesse grupo sabe.", "22:00"))),
        ("msg", "renata", "Pode, Cris."),
        ("audio", "cris", "O meu filho é bolsista. Eu tô desempregada desde março. Eu jamais ia pegar o dinheiro da festa das crianças. "
                          "Eu tenho vergonha até de falar isso."),
        ("msg", "renata", "Cris... por que você não conta pras outras mães?"),
        ("msg", "cris", "Pra elas falarem de mim na portaria? Não."),
        ("msg", "renata", "Eu sinto muito, Cris. Eu não vou contar pra ninguém."),
        ("msg", "cris", "Mas eu consigo provar que não peguei o envelope. Olha o que a Jaqueline me mandou:"),
        ("foto", "cris", print_jaque, None, dict(zoom=True, pausa=3.0, h_max=560, w=700)),
        ("msg", "renata", "Ela disse que o envelope ficou com ELA?!"),
        ("msg", "cris", "Uma semana antes de me acusar."),
        ("chat", "paula", "22:20", "HOJE"),
        ("msg", "renata", "Paula. A Jaqueline mentiu. O envelope ficou com ela o tempo todo."),
        ("msg", "paula", "Eu sabia que tinha coisa! Mas cadê o dinheiro?", dict(dig=0.3)),
        ("msg", "renata", "Não sei. Ela disse que a decoração ainda não foi comprada..."),
        ("msg", "paula", "Ela disse, né? 🤔"),
        ("chat", "grupo", "09:00", "HOJE"),
        ("msg", "marcos", "Bom dia! Ontem o Pedro foi no aniversário do Enzo, filho da Jaqueline."),
        ("msg", "marcos", "Que decoração linda! Igualzinha à da festa junina 🤠🎉", dict(dig=0.8)),
        ("msg", "marcos", "A Jaqueline caprichou, hein 👏", dict(dig=0.6)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 5
    dict(parte=5, nome="O arraiá", fim_texto="Fim", eventos=[
        ("chat", "grupo", "09:02", None, (("chip", "HOJE"), ("marcos", "Bom dia! Ontem o Pedro foi no aniversário do Enzo, filho da Jaqueline.", "09:00"),
                                          ("marcos", "Que decoração linda! Igualzinha à da festa junina 🤠🎉", "09:00"))),
        ("msg", "renata", "Jaqueline, posta as fotos do aniversário? O Marcos disse que tava lindo 😊"),
        ("msg", "jaque", "Ah... depois eu posto", dict(dig=1.0)),
        ("msg", "paula", "Não precisa, eu já vi no seu Instagram 🙂"),
        ("foto", "paula", aniversario, None, dict(zoom=True, pausa=2.6, h_max=600)),
        ("foto", "renata", decoracao, "E essa é a decoração que você mostrou no dia da vaquinha. Mesma bandeirinha, mesmo balão.",
         dict(zoom=True, pausa=0.6, h_max=520)),
        ("foto", "cris", print_jaque, "E aqui você diz que o envelope ficou com você.", dict(zoom=True, pausa=0.6, h_max=520, w=700)),
        ("msg", "jaque", "Vocês tão me perseguindo!", dict(dig=0.4)),
        ("msg", "paula", "Mil cento e cinquenta reais em bandeirinha, Jaqueline?"),
        ("msg", "jaque", "Gente, eu ia devolver!!", dict(dig=0.4)),
        ("apagar", "jaque"),
        ("msg", "ana", "Jaqueline, a direção vai conversar com você hoje. E o dinheiro volta pra festa."),
        ("msg", "ana", "A festa continua dia 24, com tudo!"),
        ("sistema", "Jaqueline (mãe do Enzo) saiu"),
        ("msg", "marcos", "Então a festa junina tá cancelada? 😢"),
        ("msg", "renata", "Não tá não! E eu proponho que a Cris continue como representante."),
        ("msg", "cris", "Renata... obrigada 💛 E eu volto com muito orgulho."),
        ("msg", "renata", "E eu faço a pamonha 🌽"),
        ("msg", "paula", "E o Marcos traz o quentão 😍"),
        ("msg", "marcos", "Só se a Renata dançar a quadrilha comigo 🤠"),
        ("msg", "renata", "Combinado 😊"),
        ("pausa", 2.4),
    ]),
]
