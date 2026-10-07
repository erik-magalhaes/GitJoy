"""Match: novela em 5 partes do Compartilhado.

A Carol dá match com o Léo (foto de costas na praia, voz grave, áudios às 23h). Ele desmarca, foge de chamada
de vídeo e some quando ela conta que começa num emprego novo. Na segunda-feira, o novo chefe manda um áudio
no grupo da equipe: é a mesma voz. O Léo é o Leonardo Prado, gerente dela. Picante só na insinuação.
"""
import functools
import os

from PIL import Image, ImageDraw

import zap

FOTOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fotos")
TITULO = "Match"

AVA = ("en-US-AvaMultilingualNeural", "+0%", "+0Hz")
BRIAN = ("en-US-BrianMultilingualNeural", "+0%", "+0Hz")
VOZES = {"carol": AVA, "nanda": AVA, "simone": AVA, "leo": BRIAN, "bruno": BRIAN}

PERSONAGENS = {
    "carol": dict(nome="Carol", cor=(216, 27, 96)),
    "nanda": dict(nome="Nanda", cor=(142, 36, 170)),
    "leo": dict(nome="Léo", cor=(2, 136, 209)),
    "simone": dict(nome="Simone", cor=(0, 121, 107)),
    "bruno": dict(nome="Bruno", cor=(245, 124, 0)),
}

CHATS = {
    "nanda": dict(dono="carol", titulo="Nanda 💜", com="nanda", sub="online"),
    "leo": dict(dono="carol", titulo="Léo 🌊", com="leo", sub="online"),
    "equipe": dict(dono="carol", titulo="Equipe Comercial 📈", grupo=True,
                   sub="Leonardo Prado, Simone RH, Bruno, Você e mais 6",
                   nomes={"leo": "Leonardo Prado (gerente)", "simone": "Simone RH", "bruno": "Bruno"}),
    "simone": dict(dono="carol", titulo="Simone RH", com="simone", sub="online"),
}


@functools.lru_cache(None)
def match_card():
    """Print do aplicativo: 'Deu match!' com a foto de costas na praia."""
    w, h = 720, 900
    im = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    for y in range(h):  # degradê rosa → laranja
        t = y / h
        d.line([(0, y), (w, y)], fill=(int(236 - 20 * t), int(64 + 80 * t), int(122 - 60 * t)))
    f = zap.inter(72, 900)
    tw = zap.larg_linha(zap.tokens("Deu match! 💘"), f)
    zap.desenha_linha(im, (w - tw) / 2, 150, zap.tokens("Deu match! 💘"), f, (255, 255, 255))
    d.text((w / 2, 210), "Você e o Léo curtiram um ao outro", font=zap.inter(30, 500), fill=(255, 240, 245), anchor="mm")
    # duas fotos redondas
    def redonda(im_f, tam):
        im_f = im_f.convert("RGB")
        lado = min(im_f.size)
        im_f = im_f.crop(((im_f.width - lado) // 2, (im_f.height - lado) // 2,
                          (im_f.width + lado) // 2, (im_f.height + lado) // 2)).resize((tam, tam), Image.LANCZOS).convert("RGBA")
        m = Image.new("L", (tam, tam), 0)
        ImageDraw.Draw(m).ellipse((0, 0, tam - 1, tam - 1), fill=255)
        im_f.putalpha(m)
        return im_f
    tam = 250
    praia = redonda(Image.open(os.path.join(FOTOS, "leo_praia.jpg")), tam)
    ela = zap.avatar("Carol", PERSONAGENS["carol"]["cor"], tam)
    for img, x in ((ela, 90), (praia, w - 90 - tam)):
        d.ellipse((x - 8, 300 - 8, x + tam + 8, 300 + tam + 8), fill=(255, 255, 255))
        im.alpha_composite(img, (x, 300))
    d.text((90 + tam / 2, 590), "Você", font=zap.inter(34, 700), fill=(255, 255, 255), anchor="mm")
    d.text((w - 90 - tam / 2, 590), "Léo, 34", font=zap.inter(34, 700), fill=(255, 255, 255), anchor="mm")
    d.rounded_rectangle((90, 680, w - 90, 780), 50, fill=(255, 255, 255))
    d.text((w / 2, 730), "Mandar mensagem", font=zap.inter(36, 800), fill=(236, 64, 122), anchor="mm")
    return im.convert("RGB")


EPISODIOS = [
    # ---------------------------------------------------------------------------------------------- 1
    dict(parte=1, nome="Deu match", eventos=[
        ("chat", "nanda", "22:10", "HOJE", (("chip", "ONTEM"), ("nanda", "Baixou o app que eu falei? 👀", "21:00"),
                                            ("carol", "Baixei. Só tem doido kkk", "21:30"))),
        ("foto", "carol", match_card, "NANDA. Olha só esse match 😳", dict(zoom=True, pausa=0.8, h_max=700, w=520)),
        ("msg", "nanda", "Foto de costas na praia? Clássico de quem esconde alguma coisa 🤨", dict(dig=0.4)),
        ("msg", "carol", "Ele é engraçado. E a voz dele, amiga... 🔥"),
        ("msg", "nanda", "Já tá mandando áudio?? Me conta tudo!"),
        ("chat", "leo", "23:05", "HOJE", (("chip", "HOJE"), ("leo", "Oi, Carol. Gostei do seu sorriso 😊", "20:15"),
                                          ("carol", "Gostei do seu... mar 😂", "20:17"))),
        ("audio", "leo", "Boa noite, Carol. Tava pensando em você. Me conta... o que você tá fazendo acordada a essa hora?"),
        ("msg", "carol", "Pensando em quem manda áudio às onze da noite 😏"),
        ("msg", "leo", "Então eu tô no caminho certo 🔥", dict(dig=0.4)),
        ("msg", "carol", "Você não perde tempo, hein?"),
        ("msg", "leo", "Me conta uma coisa sua que ninguém sabe."),
        ("msg", "carol", "Eu canto no chuveiro. Muito mal 😂"),
        ("msg", "leo", "Quero ouvir um dia 😏", dict(dig=0.4)),
        ("msg", "leo", "Com você, não. Sábado? Um vinho? 🍷"),
        ("msg", "carol", "Sábado. Sem desculpa."),
        ("msg", "leo", "Vou contar as horas 🔥", dict(dig=0.4)),
        ("chat", "nanda", "23:30"),
        ("msg", "carol", "Marquei com ele no sábado 🍷"),
        ("msg", "nanda", "Amiga, eu pesquisei o número dele. Não tem foto, não tem rede social, não tem NADA."),
        ("msg", "nanda", "Quem não aparece em lugar nenhum tem alguma coisa pra esconder.", dict(dig=0.6)),
        ("msg", "carol", "Ou é só um homem discreto, Nanda."),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 2
    dict(parte=2, nome="Desmarcado", eventos=[
        ("chat", "leo", "18:00", "SÁBADO", (("chip", "QUINTA"), ("leo", "Vou contar as horas 🔥", "23:08"))),
        ("msg", "leo", "Carol, surgiu um imprevisto no trabalho 😔 Remarca pra amanhã?", dict(dig=0.8)),
        ("msg", "carol", "Tudo bem... amanhã então."),
        ("hora", "17:40"),
        ("chip", "DOMINGO"),
        ("msg", "leo", "Carol, a minha mãe passou mal. Vou ter que desmarcar de novo 😞", dict(hora="17:40")),
        ("chat", "nanda", "17:50", "DOMINGO"),
        ("msg", "carol", "Desmarcou de novo."),
        ("msg", "nanda", "Amiga, isso é golpe. Daqui a pouco ele pede um PIX pra ajudar a mãe.", dict(dig=0.4)),
        ("msg", "carol", "Ele nunca pediu nada."),
        ("msg", "nanda", "E você não acha estranho ele nunca falar o sobrenome?"),
        ("msg", "carol", "Agora que você falou..."),
        ("msg", "nanda", "Então pede uma chamada de vídeo. Agora."),
        ("chat", "leo", "18:00"),
        ("msg", "carol", "Vamos fazer uma chamada de vídeo agora?"),
        ("digitando", "leo", 2.0),
        ("msg", "leo", "Tô sem câmera boa hoje... prefiro te ver pessoalmente 😏", dict(dig=0.3)),
        ("msg", "carol", "Léo, você é casado?"),
        ("msg", "leo", "Não! Juro.", dict(dig=0.3)),
        ("audio", "leo", "Eu só sou tímido com câmera, Carol. Mas eu tô gostando de você de verdade."),
        ("msg", "carol", "Tímido? Com esses áudios? 😂"),
        ("msg", "carol", "Então me fala o seu sobrenome."),
        ("digitando", "leo", 2.4),
        ("msg", "leo", "Logo, logo você vai saber tudo sobre mim 😉", dict(dig=0.3)),
        ("msg", "carol", "Tá bom. Mas eu vou descobrir, Léo."),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 3
    dict(parte=3, nome="Segunda-feira", eventos=[
        ("chat", "leo", "21:40", "HOJE", (("chip", "HOJE"), ("leo", "Logo, logo você vai saber tudo sobre mim 😉", "18:05"))),
        ("msg", "carol", "Amanhã eu começo no emprego novo! Tô muito nervosa 😬"),
        ("msg", "leo", "Que demais! Onde?", dict(dig=0.4)),
        ("msg", "carol", "Na Vértice Comercial, na Paulista."),
        ("digitando", "leo", 2.6),
        ("pausa", 0.8),
        ("msg", "leo", "Boa sorte 🙏", dict(dig=0.3)),
        ("status", "visto por último hoje às 21:43"),
        ("chat", "nanda", "21:50", "HOJE"),
        ("msg", "carol", "Ele ficou estranho quando eu falei do emprego."),
        ("msg", "nanda", "Estranho como?"),
        ("msg", "carol", "Mandou só um boa sorte. E sumiu. Será que eu falei alguma coisa errada?"),
        ("msg", "nanda", "Amiga, foca no emprego. Homem que some não merece o seu nervosismo."),
        ("msg", "carol", "Tem razão. Vou dormir. Amanhã é dia de causar boa impressão."),
        ("chat", "equipe", "08:30", "SEGUNDA"),
        ("sistema", "Simone RH adicionou você"),
        ("msg", "simone", "Bom dia, equipe! Hoje chega a Carol, nossa nova executiva de contas. Sejam gentis 😊"),
        ("msg", "bruno", "Bem-vinda, Carol! Eu sou o Bruno, da mesa do lado. Café é por minha conta ☕"),
        ("audio", "leo", "Bom dia, equipe. Seja bem-vinda, Carol. Às dez, reunião na minha sala."),
        ("rascunho", "Obrigada, Leon", 1.2),
        ("chat", "nanda", "08:34"),
        ("msg", "carol", "NANDA."),
        ("msg", "carol", "O meu chefe novo tem a MESMA voz do Léo.", dict(pausa=0.4)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 4
    dict(parte=4, nome="O chefe", eventos=[
        ("chat", "leo", "08:40", "HOJE", (("chip", "ONTEM"), ("leo", "Boa sorte 🙏", "21:43"))),
        ("msg", "carol", "Léo... ou eu devo dizer Leonardo Prado?"),
        ("digitando", "leo", 2.4),
        ("msg", "leo", "Carol, eu posso explicar.", dict(dig=0.3)),
        ("msg", "leo", "Quando você falou da Vértice, eu travei. Eu sou gerente lá. Eu sou o seu gerente."),
        ("msg", "carol", "E você me deu boas-vindas por áudio, como se nada tivesse acontecido?!"),
        ("msg", "leo", "O que eu ia fazer? Falar no grupo que a gente se conheceu num aplicativo?"),
        ("chat", "nanda", "09:00", "HOJE"),
        ("msg", "nanda", "Isso é filme!! E agora? Ele vai te mandar embora?", dict(dig=0.3)),
        ("msg", "carol", "Ou eu peço pra sair. Ou ele resolve isso."),
        ("msg", "nanda", "Pelo menos ele é bonito?"),
        ("msg", "carol", "Nanda!! ... É. Muito 😩"),
        ("msg", "nanda", "E a reunião das dez?"),
        ("msg", "carol", "Eu vou. Profissional. Como se eu nunca tivesse ouvido aquela voz às onze da noite 😶"),
        ("chat", "equipe", "11:15"),
        ("msg", "leo", "Ótima reunião, equipe. Carol, pode ficar depois do almoço? Preciso alinhar umas coisas."),
        ("msg", "bruno", "uiii, já vai ganhar bronca no primeiro dia 👀"),
        ("chat", "leo", "23:02"),
        ("msg", "leo", "Ainda tá acordada?", dict(dig=0.6)),
        ("msg", "carol", "Chefe não manda mensagem às onze da noite."),
        ("msg", "leo", "Não é o chefe. É o Léo 🔥", dict(dig=0.8)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 5
    dict(parte=5, nome="Regras", fim_texto="Fim", eventos=[
        ("chat", "leo", "23:04", None, (("chip", "HOJE"), ("leo", "Ainda tá acordada?", "23:02"),
                                        ("carol", "Chefe não manda mensagem às onze da noite.", "23:02"),
                                        ("leo", "Não é o chefe. É o Léo 🔥", "23:03"))),
        ("msg", "carol", "Léo, isso não pode continuar. Você é o meu chefe."),
        ("audio", "leo", "Eu sei. Mas eu não consigo fingir que não aconteceu nada entre a gente."),
        ("chat", "simone", "10:00", "HOJE"),
        ("msg", "simone", "Carol, bom dia. Pode passar no RH?"),
        ("msg", "simone", "Recebemos uma denúncia anônima. Alguém viu você e o Leonardo saindo juntos ontem à noite."),
        ("msg", "carol", "A gente só conversou. Não aconteceu nada aqui dentro."),
        ("msg", "simone", "Regra da empresa: relacionamento entre gestor e subordinado precisa ser comunicado. E um dos dois muda de área."),
        ("chat", "leo", "10:30", "HOJE"),
        ("msg", "carol", "O RH sabe. Alguém viu a gente."),
        ("msg", "leo", "Foi o Bruno. Ele mora no meu prédio.", dict(dig=0.6)),
        ("msg", "leo", "Eu vou pedir transferência pra outra filial. Você acabou de chegar. Esse emprego é seu."),
        ("msg", "carol", "Você faria isso?"),
        ("msg", "leo", "Já fiz. Amanhã eu não sou mais o seu chefe."),
        ("msg", "leo", "Então... sábado? Um vinho? 🍷", dict(dig=0.8)),
        ("msg", "carol", "Dessa vez, sem desmarcar."),
        ("msg", "leo", "Prometo 🔥", dict(dig=0.3)),
        ("chat", "nanda", "10:45"),
        ("msg", "carol", "Ele pediu transferência por mim."),
        ("msg", "nanda", "AMIGA. Finalmente um homem que não some 😭", dict(dig=0.3)),
        ("pausa", 2.4),
    ]),
]
