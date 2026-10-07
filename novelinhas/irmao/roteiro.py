"""O Irmão do Meio: novela (drama pesado) em 5 partes do Compartilhado.

A família Andrade despreza o Tiago, o irmão do meio, que acham que ainda é motoboy. Na verdade ele é programador e
paga em silêncio o plano de saúde do pai, a faculdade da Mari e o sinal do buffet das bodas de ouro, enquanto o
Gustavo (o mais velho, médico) fica com o crédito. Excluído das bodas e humilhado pela mãe, o Tiago avisa que
"cada um paga as próprias contas". O pai sempre soube.
"""
import functools
import os

from PIL import Image, ImageDraw

import zap

FOTOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fotos")
TITULO = "O Irmão do Meio"

THALITA = ("pt-BR-ThalitaMultilingualNeural", "+0%", "+0Hz")
ANTONIO = ("pt-BR-AntonioNeural", "+0%", "+0Hz")
PRONUNCIA = {r"\bbuffet\b": "bufê", r"\bBuffet\b": "Bufê"}
VOZES = {"sonia": THALITA, "mariana": THALITA, "lia": THALITA,
         "tiago": ANTONIO, "gustavo": ANTONIO, "raul": ANTONIO}

PERSONAGENS = {
    "tiago": dict(nome="Tiago", cor=(55, 71, 79)),
    "gustavo": dict(nome="Gustavo", cor=(21, 101, 192)),
    "mariana": dict(nome="Mari", cor=(216, 27, 96)),
    "sonia": dict(nome="Mãe", cor=(142, 36, 170)),
    "raul": dict(nome="Pai", cor=(93, 64, 55)),
    "lia": dict(nome="Lia", cor=(0, 137, 123)),
}

NOMES = {"sonia": "Mãe", "raul": "Pai", "gustavo": "Gustavo", "mariana": "Mari"}
CHATS = {
    "familia": dict(dono="tiago", titulo="Família Andrade ❤️", grupo=True, sub="Mãe, Pai, Gustavo, Mari, Você", nomes=NOMES),
    "bodas": dict(dono="tiago", titulo="Bodas 50 anos 💍 (NÃO ADD O TIAGO)", grupo=True, sub="Mãe, Gustavo, Mari, Você", nomes=NOMES),
    "lia": dict(dono="tiago", titulo="Lia ❤️", com="lia", sub="online"),
    "mae": dict(dono="tiago", titulo="Mãe", com="sonia", sub="online"),
    "gustavo": dict(dono="tiago", titulo="Gustavo", com="gustavo", sub="online"),
    "pai": dict(dono="tiago", titulo="Pai", com="raul", sub="online"),
}


def _doc(titulo, cor, linhas, destaque=None, rodape=None, w=820):
    """Documento simples (comprovante, contrato, planilha)."""
    h = 200 + len(linhas) * 74 + (120 if rodape else 40)
    im = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, 120), fill=cor)
    d.text((40, 60), titulo, font=zap.inter(40, 800), fill=(255, 255, 255), anchor="lm")
    y = 160
    for i, (a, b) in enumerate(linhas):
        if destaque is not None and i == destaque:
            d.rounded_rectangle((26, y - 12, w - 26, y + 56), 10, fill=(255, 241, 118))
        d.text((40, y), a, font=zap.inter(32, 500), fill=(90, 90, 90))
        d.text((w - 40, y), b, font=zap.inter(32, 750), fill=(25, 25, 25), anchor="ra")
        y += 74
    if rodape:
        d.line([(40, y + 10), (w - 40, y + 10)], fill=(220, 220, 220), width=3)
        d.text((40, y + 40), rodape, font=zap.inter(34, 800), fill=(25, 25, 25))
    return im


@functools.lru_cache(None)
def comprovante_plano():
    return _doc("Vida Plena Saúde · Comprovante", (0, 121, 107), [
        ("Beneficiário", "Raul Andrade"), ("Plano", "Sênior Plus"), ("Referência", "março"),
        ("Pagador", "Tiago Andrade"), ("Valor", "R$ 1.480,00")], destaque=3, rodape="Pago · débito automático")


@functools.lru_cache(None)
def contrato_buffet():
    return _doc("Buffet Jardim Real · Contrato", (183, 28, 28), [
        ("Evento", "Bodas de Ouro"), ("Homenageados", "Sônia e Raul"), ("Convidados", "120"),
        ("Sinal pago", "R$ 6.000,00"), ("Contratante", "Tiago Andrade")], destaque=4, rodape="Status: CANCELADO pelo contratante")


@functools.lru_cache(None)
def planilha():
    return _doc("Pagamentos do Tiago · 3 anos", (55, 71, 79), [
        ("Plano de saúde do pai", "R$ 53.280"), ("Faculdade da Mari", "R$ 86.400"), ("Sinal do buffet das bodas", "R$ 6.000"),
        ("Conserto do carro do pai", "R$ 4.200"), ("Pago pelo Gustavo", "R$ 0")], destaque=4, rodape="TOTAL: R$ 149.880")


EPISODIOS = [
    # ---------------------------------------------------------------------------------------------- 1
    dict(parte=1, nome="O do meio", eventos=[
        ("chat", "familia", "19:00", "HOJE", (("chip", "ONTEM"), ("sonia", "Bom dia, família abençoada 🙏", "07:00"))),
        ("msg", "sonia", "Família, quero agradecer o Gustavo na frente de todo mundo. Ele paga o plano de saúde do pai há três anos e nunca reclamou. Esse é o meu orgulho 🙏❤️"),
        ("msg", "gustavo", "Imagina, mãe. Família é pra isso 😊"),
        ("msg", "mariana", "Melhor irmão do mundo 😍", dict(dig=0.3)),
        ("msg", "raul", "Obrigado, filho."),
        ("rascunho", "Mãe, na verdade quem paga", 1.2),
        ("msg", "tiago", "Que bom que o senhor tá bem, pai."),
        ("msg", "sonia", "E você, Tiago? Ainda fazendo aquelas entregas de moto?"),
        ("msg", "gustavo", "Deixa ele, mãe. Cada um no seu tempo 😏"),
        ("chat", "lia", "19:15", "HOJE"),
        ("msg", "tiago", "Viu o grupo?"),
        ("msg", "lia", "Vi. Amor, o Gustavo tá levando o crédito pelo plano que VOCÊ paga.", dict(dig=0.4)),
        ("foto", "tiago", comprovante_plano, "Todo mês. Há três anos. No meu nome.", dict(zoom=True, pausa=0.6, h_max=560)),
        ("msg", "lia", "Por que você não fala nada?"),
        ("msg", "tiago", "Porque o meu pai precisa do plano. Não de briga."),
        ("msg", "lia", "E a faculdade da Mari? E o sinal do buffet das bodas? Também é você."),
        ("msg", "lia", "Eles nem sabem que você é programador. Acham que você ainda é motoboy."),
        ("msg", "tiago", "Melhor assim. Ninguém me pede mais nada."),
        ("chat", "bodas", "21:40", "HOJE"),
        ("sistema", "Mari adicionou você"),
        ("msg", "sonia", "E o salão comporta cento e vinte pessoas! 🎉"),
        ("msg", "mariana", "O buffet confirmou a data, gente! 💍", dict(dig=0.4)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 2
    dict(parte=2, nome="Sem o Tiago", eventos=[
        ("chat", "bodas", "21:41", None, (("chip", "HOJE"), ("chip", "Mari adicionou você"),
                                          ("mariana", "O buffet confirmou a data, gente! 💍", "21:40"))),
        ("msg", "sonia", "Só uma coisa: o Tiago não pode saber dessa festa."),
        ("msg", "gustavo", "Óbvio. Ele vai aparecer de bermuda e envergonhar a gente na frente dos convidados."),
        ("msg", "sonia", "Fala que é só pra casais. Ele não tem ninguém mesmo."),
        ("msg", "mariana", "Gente...", dict(dig=0.6)),
        ("msg", "mariana", "Eu adicionei o Tiago sem querer 😳", dict(dig=0.8)),
        ("apagar", "gustavo"),
        ("sistema", "Mari removeu você"),
        ("chat", "lia", "21:50", "HOJE"),
        ("msg", "tiago", "Lia. Eles tão organizando as bodas sem mim. Disseram que eu ia envergonhar eles."),
        ("msg", "lia", "Que absurdo! Você pagou o sinal do buffet!", dict(dig=0.3)),
        ("msg", "tiago", "Seis mil reais. E eu não posso nem ir."),
        ("msg", "tiago", "A minha própria mãe, Lia."),
        ("msg", "lia", "Eu sei, amor. Eu tô aqui.", dict(dig=0.4)),
        ("audio", "lia", "Amor, chega. Você não é o caixa eletrônico dessa família. Você é filho. E filho não precisa pagar pra ser amado."),
        ("chat", "mae", "22:30", "HOJE", (("chip", "DOMINGO"), ("sonia", "Bença, filho 🙏", "08:00"), ("tiago", "Deus abençoe, mãe", "08:30"))),
        ("msg", "sonia", "Filho, tudo bem? 🙏", dict(dig=0.4)),
        ("msg", "sonia", "Preciso de um favor. Me empresta nove mil? O Gustavo tá apertado esse mês."),
        ("msg", "sonia", "É pra uma festa da igreja 🙏", dict(dig=0.8)),
        ("rascunho", "Festa da igreja, mãe?", 1.4),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 3
    dict(parte=3, nome="A vergonha da família", eventos=[
        ("chat", "mae", "22:32", None, (("chip", "HOJE"), ("sonia", "Preciso de um favor. Me empresta nove mil? O Gustavo tá apertado esse mês.", "22:30"),
                                        ("sonia", "É pra uma festa da igreja 🙏", "22:30"))),
        ("msg", "tiago", "Festa da igreja, mãe? Ou as bodas que eu não posso ir?"),
        ("digitando", "sonia", 2.0),
        ("msg", "sonia", "Quem te contou?", dict(dig=0.3)),
        ("msg", "tiago", "A Mari me adicionou no grupo sem querer. Eu li tudo. \"Ele vai envergonhar a gente.\""),
        ("audio", "sonia", "Tiago, olha pra sua vida. O seu irmão é médico. A sua irmã vai ser advogada. E você? Entregando comida de moto "
                           "até hoje. Eu tenho vergonha, sim. Pronto, falei."),
        ("msg", "tiago", "Entendi, mãe.", dict(pausa=0.8)),
        ("msg", "sonia", "E o dinheiro? Não vai me responder?", dict(dig=0.6)),
        ("msg", "tiago", "Boa noite, mãe."),
        ("chat", "gustavo", "23:00", "HOJE"),
        ("msg", "gustavo", "A mãe falou que você surtou. Para de drama, Tiago."),
        ("msg", "gustavo", "Ninguém te convidou porque você não acrescenta nada."),
        ("msg", "tiago", "Gustavo, quem paga o plano do pai?"),
        ("msg", "gustavo", "Eu, ué. Todo mundo sabe.", dict(dig=0.4)),
        ("msg", "tiago", "Tá bom."),
        ("chat", "familia", "23:30", "HOJE"),
        ("msg", "tiago", "Família, um aviso."),
        ("msg", "tiago", "A partir de amanhã, cada um paga as próprias contas."),
        ("msg", "mariana", "Ué, que contas? 😂", dict(dig=0.3)),
        ("msg", "gustavo", "Ele tá bêbado, gente. Pode ignorar."),
        ("digitando", "raul", 1.8),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 4
    dict(parte=4, nome="As contas", eventos=[
        ("chat", "familia", "10:00", "HOJE", (("chip", "ONTEM"), ("tiago", "A partir de amanhã, cada um paga as próprias contas.", "23:30"),
                                              ("gustavo", "Ele tá bêbado, gente. Pode ignorar.", "23:31"))),
        ("msg", "mariana", "GENTE. A faculdade mandou e-mail. A minha matrícula foi cancelada por falta de pagamento??"),
        ("msg", "mariana", "Mãe, você não pagou o boleto?"),
        ("msg", "sonia", "Quem paga é o Gustavo, filha!", dict(dig=0.4)),
        ("msg", "gustavo", "Eu?? Eu nunca paguei faculdade nenhuma.", dict(dig=0.4)),
        ("msg", "sonia", "Como assim, Gustavo?"),
        ("msg", "gustavo", "Mãe, eu posso explicar...", dict(dig=0.6)),
        ("msg", "sonia", "Então explica!"),
        ("msg", "mariana", "Alguém vai me responder?? Quem pagava a minha faculdade??"),
        ("hora", "11:20"),
        ("msg", "sonia", "O buffet acabou de ligar. Disseram que o contratante cancelou a festa. Que contratante??", dict(hora="11:20")),
        ("foto", "tiago", contrato_buffet, "O contratante sou eu.", dict(zoom=True, pausa=0.6, h_max=600, hora="11:21")),
        ("msg", "tiago", "E o plano de saúde do pai também tá no meu nome. Fica ativo mais trinta dias. Depois, o médico da família assume.",
         dict(hora="11:21")),
        ("msg", "sonia", "Tiago, isso é chantagem!", dict(dig=0.3, hora="11:22")),
        ("msg", "tiago", "Não, mãe. É só a conta.", dict(hora="11:22")),
        ("msg", "mariana", "Então era você que pagava a minha faculdade?? 😳", dict(hora="11:22")),
        ("digitando", "raul", 2.0),
        ("chat", "gustavo", "12:00", "HOJE"),
        ("msg", "gustavo", "Irmão. Precisamos conversar.", dict(dig=0.6)),
        ("msg", "gustavo", "Não conta nada pra mãe, por favor.", dict(dig=0.8)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 5
    dict(parte=5, nome="A volta por cima", fim_texto="Fim", eventos=[
        ("chat", "gustavo", "12:01", None, (("chip", "HOJE"), ("gustavo", "Irmão. Precisamos conversar.", "12:00"),
                                            ("gustavo", "Não conta nada pra mãe, por favor.", "12:00"))),
        ("msg", "tiago", "Contar o quê, Gustavo?"),
        ("audio", "gustavo", "Que eu tô devendo até o pescoço. Cartão, empréstimo, tudo. Eu deixei a mãe achar que era eu que pagava "
                             "porque era a única coisa que eu ainda tinha: o orgulho dela."),
        ("msg", "tiago", "E pra isso você deixou ela me humilhar por três anos."),
        ("msg", "gustavo", "Eu sei. Me desculpa."),
        ("chat", "familia", "14:00", "HOJE"),
        ("msg", "tiago", "Pra ninguém mais ter dúvida."),
        ("foto", "tiago", planilha, "Três anos. Do entregador de moto.", dict(zoom=True, pausa=0.6, h_max=640)),
        ("msg", "mariana", "Tiago... me perdoa 😭", dict(dig=0.4)),
        ("digitando", "sonia", 2.4),
        ("audio", "raul", "Eu sempre soube, filho. Eu vi o seu nome no boleto do plano. E fiquei quieto, porque fui covarde. Me perdoa."),
        ("msg", "tiago", "O plano do senhor eu continuo pagando, pai. O senhor nunca me tratou diferente."),
        ("msg", "tiago", "A faculdade da Mari também. Ela é a minha irmã. O resto é com o médico da família."),
        ("msg", "sonia", "Filho... me perdoa.", dict(dig=1.0)),
        ("msg", "tiago", "Vai levar tempo, mãe."),
        ("chat", "pai", "18:00", "HOJE"),
        ("foto", "tiago", "casa_tiago.jpg", "Pai, comprei a minha casa. Paguei à vista."),
        ("msg", "raul", "Que orgulho, filho 😭", dict(dig=0.6)),
        ("msg", "tiago", "Tem um quarto pro senhor. E as bodas a gente comemora aqui, do nosso jeito."),
        ("msg", "raul", "Eu levo a sua mãe. Ela precisa ver isso de perto."),
        ("pausa", 2.4),
    ]),
]
