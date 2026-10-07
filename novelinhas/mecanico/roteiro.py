"""Carlos Mecânico: novela em 5 partes do Compartilhado.

A Pati vê no celular do marido (Ricardo) um "Carlos Mecânico 🔧" mandando coração. A temporada inteira as provas
apontam para a melhor amiga, a Juli (brinco no carro, encontro no café, story "dia de oficina"). Na verdade a Juli
descobriu tudo por acaso e cobrava do Ricardo que contasse. O Carlos é mecânico de verdade, e o Ricardo se
apaixonou por ele. O erro do Ricardo é mentir e trair, não gostar de um homem.
"""
import functools
import os

from PIL import Image, ImageDraw, ImageFilter

import zap

FOTOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fotos")
TITULO = "Carlos Mecânico"

AVA = ("en-US-AvaMultilingualNeural", "+0%", "+0Hz")
BRIAN = ("en-US-BrianMultilingualNeural", "+0%", "+0Hz")
PRONUNCIA = {r"Acácias, 120": "Acácias, número cento e vinte"}
VOZES = {"pati": AVA, "ju": AVA, "debora": AVA, "ricardo": BRIAN, "carlos": BRIAN}

PERSONAGENS = {
    "pati": dict(nome="Pati", cor=(194, 24, 91)),
    "ricardo": dict(nome="Ricardo", cor=(21, 101, 192)),
    "ju": dict(nome="Juli", cor=(251, 140, 0)),
    "debora": dict(nome="Débora", cor=(123, 31, 162)),
    "carlos": dict(nome="Carlos", cor=(84, 110, 122)),
}

CHATS = {
    "ju": dict(dono="pati", titulo="Juli 💛", com="ju", sub="online"),
    "rico": dict(dono="pati", titulo="Rico ❤️", com="ricardo", sub="online"),
    "de": dict(dono="pati", titulo="Dé (irmã) 💜", com="debora", sub="online"),
    "carlos_p": dict(dono="pati", titulo="+55 11 97310-5582", com="carlos", sub="online"),
    "carlos_r": dict(dono="ricardo", titulo="Carlos Mecânico 🔧", com="carlos", sub="visto por último hoje às 13:12"),
}


# ------------------------------------------------------------------ imagens
@functools.lru_cache(None)
def notificacao():
    """Foto (print) da tela de bloqueio do Ricardo com a notificação do Carlos."""
    w, h = 720, 900
    im = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    px = im.load()
    for y in range(h):  # fundo azul-escuro em degradê
        for x in range(0, w, 4):
            c = (20 + y // 30, 30 + y // 25, 70 + y // 12, 255)
            for k in range(4):
                if x + k < w:
                    px[x + k, y] = c
    d = ImageDraw.Draw(im)
    d.text((w / 2, 120), "sexta-feira, 13 de junho", font=zap.inter(30, 500), fill=(230, 230, 240), anchor="mm")
    d.text((w / 2, 240), "23:41", font=zap.inter(150, 300), fill=(255, 255, 255), anchor="mm")
    card = Image.new("RGBA", (w - 60, 190), (0, 0, 0, 0))
    dc = ImageDraw.Draw(card)
    dc.rounded_rectangle((0, 0, card.width - 1, card.height - 1), 30, fill=(245, 245, 247, 235))
    dc.rounded_rectangle((22, 24, 82, 84), 16, fill=(37, 211, 102))
    dc.text((100, 40), "WHATSAPP", font=zap.inter(24, 600), fill=(120, 120, 125))
    dc.text((card.width - 26, 40), "agora", font=zap.inter(24, 450), fill=(120, 120, 125), anchor="ra")
    zap.desenha_linha(card, 100, 108, zap.tokens("Carlos Mecânico 🔧"), zap.inter(32, 700), (20, 20, 20))
    zap.desenha_linha(card, 100, 156, zap.tokens("Saudade de você ❤️"), zap.inter(34, 450), (40, 40, 40))
    im.alpha_composite(card, (30, 420))
    return im.convert("RGB")


@functools.lru_cache(None)
def mapa():
    """Localização em tempo real do Ricardo: o ponto azul no Café Grão Fino."""
    w, h = 760, 760
    im = Image.new("RGBA", (w, h), (236, 232, 222, 255))
    d = ImageDraw.Draw(im)
    d.polygon([(0, 520), (260, 470), (300, 760), (0, 760)], fill=(200, 230, 190))       # praça
    d.ellipse((520, 40, 760, 230), fill=(170, 210, 240))                                 # lago
    for x in (120, 330, 560):
        d.line([(x, 0), (x + 40, h)], fill=(255, 255, 255), width=26)
    for y in (160, 400, 640):
        d.line([(0, y), (w, y - 30)], fill=(255, 255, 255), width=26)
    d.line([(0, 300), (w, 260)], fill=(255, 214, 102), width=34)                         # avenida
    d.text((20, 230), "Av. das Acácias", font=zap.inter(24, 600), fill=(120, 110, 90))
    cx, cy = 380, 330
    d.ellipse((cx - 70, cy - 70, cx + 70, cy + 70), fill=(66, 133, 244, 60))
    d.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), fill=(255, 255, 255))
    d.ellipse((cx - 16, cy - 16, cx + 16, cy + 16), fill=(66, 133, 244))
    d.rounded_rectangle((cx - 150, cy - 150, cx + 150, cy - 86), 16, fill=(255, 255, 255))
    zap.desenha_linha(im, cx - 132, cy - 104, zap.tokens("☕ Café Grão Fino"), zap.inter(30, 700), (30, 30, 30))
    d.rectangle((0, h - 110, w, h), fill=(255, 255, 255))
    av = zap.avatar("Ricardo", PERSONAGENS["ricardo"]["cor"], 64)
    im.paste(av, (24, h - 88), av)
    d.text((104, h - 84), "Ricardo", font=zap.inter(32, 700), fill=(30, 30, 30))
    d.text((104, h - 44), "Localização em tempo real · agora", font=zap.inter(26, 450), fill=(110, 110, 110))
    return im.convert("RGB")


@functools.lru_cache(None)
def story_ju():
    """Story da Juli: 'Dia de oficina 🔧'."""
    w, h = 720, 1280
    ft = Image.open(os.path.join(FOTOS, "oficina.jpg")).convert("RGB")
    fundo = ft.resize((round(ft.width * h / ft.height), h), Image.LANCZOS)
    x0 = (fundo.width - w) // 2
    im = fundo.crop((x0, 0, x0 + w, h)).filter(ImageFilter.GaussianBlur(26)).convert("RGBA")
    meio = ft.resize((w, round(ft.height * w / ft.width)), Image.LANCZOS)
    im.paste(meio, (0, (h - meio.height) // 2))
    d = ImageDraw.Draw(im)
    for i in range(2):
        x = 16 + i * (w - 32) / 2
        d.rounded_rectangle((x + 3, 20, x + (w - 32) / 2 - 3, 26), 3, fill=(255, 255, 255, 255 if i == 0 else 110))
    av = zap.avatar("Juli", PERSONAGENS["ju"]["cor"], 64)
    im.paste(av, (20, 44), av)
    d.text((98, 86), "juli.martins", font=zap.inter(30, 700), fill=(255, 255, 255), anchor="ls")
    d.text((262, 86), "5 h", font=zap.inter(28, 450), fill=(230, 230, 230), anchor="ls")
    txt = "Dia de oficina 🔧"
    f = zap.inter(50, 800)
    tw = zap.larg_linha(zap.tokens(txt), f)
    d.rounded_rectangle(((w - tw) / 2 - 20, 1000, (w + tw) / 2 + 20, 1076), 14, fill=(255, 255, 255))
    zap.desenha_linha(im, (w - tw) / 2, 1056, zap.tokens(txt), f, (20, 20, 20))
    return im.convert("RGB")


# ------------------------------------------------------------------ episódios
EPISODIOS = [
    # ---------------------------------------------------------------------------------------------- 1
    dict(parte=1, nome="O Carlos", eventos=[
        ("chat", "ju", "23:42", None, (("chip", "ONTEM"), ("ju", "Amanhã academia? 💪", "19:00"), ("pati", "Bora! 7h", "19:05"),
                                       ("chip", "HOJE"))),
        ("msg", "pati", "Juli, tá acordada?"),
        ("msg", "ju", "Tô sim. Que foi?", dict(dig=0.4)),
        ("foto", "pati", notificacao, "Olha o que apareceu no celular do Rico agora 😳", dict(zoom=True, pausa=1.0, h_max=700, w=520)),
        ("digitando", "ju", 2.0),
        ("msg", "ju", "Carlos Mecânico?", dict(dig=0.3)),
        ("msg", "ju", "Deve ser brincadeira de homem, amiga kkkk"),
        ("msg", "pati", "Brincadeira com coração?"),
        ("msg", "pati", "Ele saiu do banho, pegou o celular correndo e apagou a notificação na minha frente."),
        ("msg", "ju", "Amiga... conversa com ele amanhã. Com calma.", dict(dig=0.8)),
        ("msg", "pati", "Você tá estranha, Juli."),
        ("msg", "ju", "Tô com sono, só isso. Relaxa, que o Rico te ama. Vou dormir, beijo!"),
        ("status", "visto por último hoje às 23:44"),
        ("chat", "rico", "08:10", "HOJE", (("chip", "ONTEM"), ("ricardo", "Chego tarde hoje, amor. Muito trabalho 😓", "18:20"))),
        ("msg", "pati", "Amor, quem é Carlos Mecânico?"),
        ("digitando", "ricardo", 1.4),
        ("msg", "ricardo", "O cara que tá arrumando o meu carro, ué.", dict(dig=0.3)),
        ("msg", "pati", "E ele te manda coração?"),
        ("msg", "ricardo", "Ele é brincalhão, manda pra todo cliente 😂"),
        ("msg", "pati", "Hum.", dict(ler=False, pausa=0.8)),
        ("msg", "ricardo", "Tá desconfiando de mim, Pati? Dez anos de casamento..."),
        ("msg", "pati", "Só perguntei, Ricardo."),
        ("chat", "carlos_p", "08:30"),
        ("msg", "pati", "Oi, Carlos! Aqui é a Patrícia, esposa do Ricardo."),
        ("msg", "pati", "Ele disse que o carro tá aí com você. Fica pronto quando?"),
        ("digitando", "carlos", 2.2),
        ("msg", "carlos", "Que carro? 😂", dict(dig=0.3)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 2
    dict(parte=2, nome="Que carro?", eventos=[
        ("chat", "carlos_p", "08:31", None, (("chip", "HOJE"), ("pati", "Ele disse que o carro tá aí com você. Fica pronto quando?", "08:30"),
                                             ("carlos", "Que carro? 😂", "08:31"))),
        ("digitando", "carlos", 1.4),
        ("msg", "carlos", "Ah, desculpa! Número errado 🙏", dict(dig=0.3)),
        ("status", "visto por último hoje às 08:32"),
        ("msg", "pati", "Número errado?"),
        ("chat", "de", "09:00", "HOJE", (("chip", "ONTEM"), ("debora", "Pati, almoço domingo na mãe?", "12:00"),
                                         ("pati", "Vou sim 😘", "12:10"))),
        ("msg", "pati", "Dé, preciso falar com a minha irmã preferida."),
        ("msg", "debora", "Sou a sua única irmã kkk fala", dict(dig=0.4)),
        ("msg", "pati", "Acho que o Rico tá me traindo."),
        ("msg", "debora", "O RICO?? Com quem?", dict(dig=0.3)),
        ("msg", "pati", "Tem um tal de Carlos Mecânico no celular dele, mandando coração. E o carro dele tá na garagem. Nunca foi pra oficina."),
        ("msg", "debora", "Pati... Carlos Mecânico é nome de contato pra esconder mulher. Clássico."),
        ("chat", "carlos_r", "13:20", "HOJE", (("chip", "HOJE"), ("carlos", "Bom dia ❤️", "07:50"), ("ricardo", "Bom dia 😊", "07:52"))),
        ("msg", "carlos", "Ela desconfiou? 😬"),
        ("msg", "ricardo", "Acho que sim. Ela te mandou mensagem?"),
        ("msg", "carlos", "Mandou. Eu disse que era número errado 😅"),
        ("msg", "ricardo", "Apaga tudo hoje, por favor."),
        ("msg", "carlos", "Te vejo sábado? ❤️"),
        ("msg", "ricardo", "Sábado, no café de sempre ❤️"),
        ("chat", "de", "13:30"),
        ("msg", "pati", "Dé. Peguei o celular dele. \"Sábado, no café de sempre\" com coração."),
        ("msg", "pati", "E achei um brinco no banco do carro. Não é meu."),
        ("msg", "debora", "Sábado é amanhã. Liga a localização dele.", dict(dig=0.4)),
        ("chat", "ju", "14:05"),
        ("msg", "ju", "Amiga, por acaso você achou um brinco meu no carro do Rico?", dict(dig=0.6)),
        ("msg", "ju", "Ele me deu carona semana passada 😅", dict(dig=0.6)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 3
    dict(parte=3, nome="O encontro", eventos=[
        ("chat", "ju", "14:07", None, (("chip", "HOJE"), ("ju", "Amiga, por acaso você achou um brinco meu no carro do Rico?", "14:05"),
                                       ("ju", "Ele me deu carona semana passada 😅", "14:05"))),
        ("msg", "pati", "Achei sim. Que carona foi essa?"),
        ("msg", "ju", "Ah, ele me levou na oficina, o meu carro tava ruim 😅"),
        ("msg", "pati", "Na oficina do CARLOS?"),
        ("digitando", "ju", 2.0),
        ("msg", "ju", "Que Carlos? Amiga, tô atrasada, depois a gente fala!", dict(dig=0.3)),
        ("msg", "pati", "Juli??"),
        ("status", "visto por último hoje às 14:09"),
        ("chat", "de", "15:10", "SÁBADO"),
        ("foto", "pati", mapa, "Localização dele agora: Café Grão Fino.", dict(zoom=True, pausa=1.0, h_max=640)),
        ("msg", "debora", "Tô a duas quadras. Vou lá.", dict(dig=0.4)),
        ("digitando", "debora", 2.4),
        ("foto", "debora", "cafe.jpg", "Tirei pela janela...", dict(zoom=True, pausa=1.0)),
        ("msg", "debora", "Pati. Ele tá com a JULI.", dict(dig=0.6)),
        ("msg", "pati", "A JULI?? Não pode ser. Olha direito, Dé!"),
        ("msg", "debora", "Sentados juntos. Ela segurando a mão dele."),
        ("msg", "pati", "Fica aí, Dé. Vê se mais alguém chega."),
        ("msg", "debora", "Não dá, o meu Uber chegou. Mas Pati... ele tava nervoso. E ela falando sem parar."),
        ("msg", "debora", "E olha o story que ela postou hoje cedo:"),
        ("foto", "debora", story_ju, None, dict(zoom=True, pausa=3.0, w=430, h_max=760)),
        ("msg", "pati", "Dia de oficina. Carlos MECÂNICO."),
        ("msg", "pati", "Dé... a Juli é o Carlos. Ela tem outro número."),
        ("msg", "debora", "Meu Deus, Pati. A sua madrinha de casamento.", dict(dig=0.4)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 4
    dict(parte=4, nome="A madrinha", eventos=[
        ("chat", "ju", "21:00", "HOJE"),
        ("msg", "pati", "Juli. Para de mentir. Você é o Carlos Mecânico."),
        ("digitando", "ju", 2.2),
        ("msg", "ju", "O QUÊ?? Tá doida, Pati?", dict(dig=0.2)),
        ("msg", "pati", "O brinco no carro. O café. O story da oficina. A mão dele na sua."),
        ("msg", "ju", "Pati, eu não sou o Carlos."),
        ("msg", "ju", "Mas eu sei quem é.", dict(dig=0.8)),
        ("msg", "pati", "Então fala! Quem é, Juli??"),
        ("audio", "ju", "Amiga, eu descobri isso sem querer, faz um mês. Eu juro que pedi pra ele te contar. Hoje no café eu fui "
                        "justamente cobrar isso dele. Mas não sou eu que tenho que te contar, Pati. Tem que ser ele."),
        ("msg", "pati", "Você é a minha madrinha de casamento, Juli!"),
        ("msg", "ju", "Por isso mesmo. Vai até a oficina. Rua das Acácias, 120."),
        ("chat", "rico", "21:30", "HOJE"),
        ("msg", "pati", "Ricardo, eu sei que você se encontrou com a Juli hoje."),
        ("msg", "ricardo", "Pati, não é nada disso que você tá pensando.", dict(dig=0.5)),
        ("msg", "pati", "Então o que é??"),
        ("digitando", "ricardo", 2.0),
        ("msg", "ricardo", "Amanhã a gente conversa. Eu prometo.", dict(dig=0.3)),
        ("chat", "carlos_p", "09:00", "DOMINGO"),
        ("msg", "pati", "Bom dia, Carlos. Tô aqui na frente da oficina."),
        ("digitando", "carlos", 2.4),
        ("msg", "carlos", "Patrícia?? 😳", dict(dig=0.3)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 5
    dict(parte=5, nome="O mecânico", fim_texto="Fim", eventos=[
        ("chat", "carlos_p", "09:01", None, (("chip", "HOJE"), ("pati", "Bom dia, Carlos. Tô aqui na frente da oficina.", "09:00"),
                                             ("carlos", "Patrícia?? 😳", "09:00"))),
        ("msg", "carlos", "Espera, eu vou sair aí.", dict(dig=0.5)),
        ("msg", "pati", "Então você existe."),
        ("msg", "carlos", "Existo. Eu sou o Carlos. Mecânico de verdade."),
        ("msg", "carlos", "E eu gosto do Ricardo. Muito. Me desculpa.", dict(dig=1.0)),
        ("rascunho", "Você e o meu", 1.2),
        ("chat", "rico", "10:00", "HOJE"),
        ("msg", "pati", "Eu tô na oficina. Com o Carlos."),
        ("digitando", "ricardo", 2.4),
        ("audio", "ricardo", "Pati, eu me apaixonei por ele. Eu demorei muito pra entender quem eu sou, e fui covarde. "
                             "Te enganar foi o meu erro. Você não merecia isso."),
        ("msg", "pati", "Dez anos, Ricardo. Eu só queria a verdade."),
        ("msg", "ricardo", "Eu sei. Eu vou sair de casa hoje."),
        ("msg", "pati", "E a Juli?"),
        ("msg", "ricardo", "A Juli só tentou me fazer te contar. Ela nunca fez nada de errado."),
        ("chat", "ju", "20:00", "HOJE"),
        ("msg", "pati", "Juli... me desculpa. Eu achei que era você."),
        ("msg", "ju", "Eu entendo, amiga. Eu também teria achado.", dict(dig=0.5)),
        ("msg", "ju", "Como você tá?"),
        ("msg", "pati", "Destruída. Mas pelo menos agora eu sei a verdade."),
        ("msg", "ju", "Bora tomar um vinho hoje? 🍷", dict(dig=0.4)),
        ("msg", "pati", "Duas garrafas."),
        ("sistema", "Você alterou o nome do contato \"Rico ❤️\" para \"Ricardo\""),
        ("pausa", 2.4),
    ]),
]
