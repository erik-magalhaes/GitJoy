"""A Festa Surpresa: novela em 5 partes do Compartilhado.

As coisas da Carol começam a sumir de casa: o fone com adesivo de margarida, o perfume e o relógio de bolso do avô.
O namorado, Bruno, joga a desconfiança no melhor amigo dela, o Vini, que tem a chave reserva (cuidou do gato Pipoca).
Para entrar no apê do Vini, ela organiza uma festa surpresa com a Dani, que divide o apê com ele, e acha uma caixa
com tudo. A reviravolta: o Vini viu as coisas dela à venda num site de usados, o vendedor era o Bruno, e ele comprou
tudo de volta para devolver e ter prova. O story do fone foi para ver a reação do Bruno, que caiu e culpou o Vini.
"""
import functools
import os

from PIL import Image, ImageDraw, ImageFilter

import zap

FOTOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fotos")
FONTES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fonts")
TITULO = "A Festa Surpresa"

THALITA = ("pt-BR-ThalitaMultilingualNeural", "+0%", "+0Hz")
ANTONIO = ("pt-BR-AntonioNeural", "+0%", "+0Hz")
PRONUNCIA = {r"\bsurpresaaa\b": "surpresa!"}
VOZES = {"carol": THALITA, "dani": THALITA, "thais": THALITA,
         "bruno": ANTONIO, "vini": ANTONIO, "gui": ANTONIO}

PERSONAGENS = {
    "carol": dict(nome="Carol", cor=(194, 24, 91)),
    "bruno": dict(nome="Bruno", cor=(21, 101, 192)),
    "vini": dict(nome="Vini", cor=(46, 125, 50)),
    "dani": dict(nome="Dani", cor=(230, 81, 0)),
    "gui": dict(nome="Gui", cor=(69, 39, 160)),
    "thais": dict(nome="Thaís", cor=(0, 131, 143)),
}

NOMES = {"dani": "Dani", "gui": "Gui", "thais": "Thaís"}
CHATS = {
    "bruno": dict(dono="carol", titulo="Bruno 🤍", com="bruno", sub="online"),
    "vini": dict(dono="carol", titulo="Vini 🌼", com="vini", sub="online"),
    "dani": dict(dono="carol", titulo="Dani (apê do Vini)", com="dani", sub="online"),
    "grupo": dict(dono="carol", titulo="Surpresa do Vini 🤫🎉", grupo=True, sub="Dani, Gui, Thaís, Você", nomes=NOMES),
}


def _foto(nome):
    return Image.open(os.path.join(FOTOS, nome)).convert("RGB")


def _cobre(im, w, h):
    """Redimensiona e recorta para preencher w x h."""
    esc = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * esc), round(im.height * esc)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


@functools.lru_cache(None)
def fone_margarida():
    """O fone da Carol: a foto com o adesivo de margarida colado na concha."""
    im = _foto("fone.jpg").convert("RGBA")
    flor = zap.emoji_img("🌼", 150).rotate(-18, expand=True, resample=Image.BICUBIC)
    sombra = Image.new("RGBA", flor.size, (0, 0, 0, 0))
    sombra.putalpha(flor.getchannel("A").point(lambda a: a * 0.35))
    sombra = sombra.filter(ImageFilter.GaussianBlur(5))
    x, y = 585, 455
    im.alpha_composite(sombra, (x + 5, y + 7))
    im.alpha_composite(flor, (x, y))
    return im.convert("RGB")


@functools.lru_cache(None)
def story_vini():
    """Story do Vini com o fone (barra de progresso, nome, legenda)."""
    w, h = 720, 1100
    im = Image.new("RGB", (w, h), (18, 18, 18))
    f = _cobre(fone_margarida(), w, 760)
    im.paste(f, (0, 170))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((20, 22, w - 20, 28), 3, fill=(120, 120, 120))
    d.rounded_rectangle((20, 22, 420, 28), 3, fill=(255, 255, 255))
    av = zap.avatar("Vini", PERSONAGENS["vini"]["cor"], 64)
    im.paste(av, (24, 50), av if av.mode == "RGBA" else None)
    d.text((104, 82), "vini.santos", font=zap.inter(30, 700), fill=(255, 255, 255), anchor="lm")
    d.text((282, 82), "2 h", font=zap.inter(28, 450), fill=(200, 200, 200), anchor="lm")
    tj = zap.tarja("olha o que eu achei 👀🎧", 44, maxw=620, ang=-3)
    im.paste(tj, ((w - tj.width) // 2, 960 - tj.height // 2), tj)
    return im


@functools.lru_cache(None)
def bilhete():
    """Bilhete escrito à mão, no envelope da caixa."""
    w, h = 820, 640
    im = Image.new("RGBA", (w, h), (252, 247, 222, 255))
    d = ImageDraw.Draw(im)
    for y in range(150, h - 40, 66):
        d.line([(30, y), (w - 30, y)], fill=(170, 200, 230), width=2)
    d.line([(100, 0), (100, h)], fill=(235, 150, 150), width=3)
    f = zap.fonte("Pacifico-Regular.ttf", 40)
    linhas = ["Carol,", "comprei tudo de volta.", "Tava à venda na internet.", "Os prints tão no envelope.",
              "Eu não sabia como", "te contar. Me perdoa.", "Vini 🌼"]
    y = 150
    for k, ln in enumerate(linhas):
        x = 470 if k == len(linhas) - 1 else 120
        zap.texto_rico(im, x, y - 62, ln, f, (30, 50, 120))
        y += 66
    return im.convert("RGB")


def _card_anuncio(foto, titulo, preco, w=800):
    h = 300
    im = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    im.paste(_cobre(foto, 260, 260), (20, 20))
    zap.texto_rico(im, 300, 26, titulo, zap.inter(32, 650), (30, 30, 30), maxw=w - 320)
    d.text((300, 190), preco, font=zap.inter(44, 800), fill=(106, 27, 154))
    d.text((300, 252), "Vila Mariana, São Paulo", font=zap.inter(26, 450), fill=(120, 120, 120))
    return im.convert("RGB")


@functools.lru_cache(None)
def anuncios():
    """Print do site de usados: dois anúncios com as coisas da Carol e o vendedor Bruno R."""
    w = 840
    topo = 120
    cards = [
        _card_anuncio(_foto("relogio_bolso.jpg"), "Relógio de bolso antigo, banhado a ouro. Herança de família", "R$ 900"),
        _card_anuncio(fone_margarida(), "Fone on-ear seminovo, com adesivo de brinde 🌼", "R$ 350"),
    ]
    h = topo + sum(c.height + 24 for c in cards) + 150
    im = Image.new("RGB", (w, h), (240, 240, 244))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, topo - 20), fill=(106, 27, 154))
    d.text((30, (topo - 20) // 2), "Desapega Já", font=zap.inter(44, 800), fill=(255, 255, 255), anchor="lm")
    d.text((w - 30, (topo - 20) // 2), "anúncios do vendedor", font=zap.inter(26, 500), fill=(230, 210, 240), anchor="rm")
    y = topo
    for c in cards:
        im.paste(c, (20, y))
        y += c.height + 24
    d.rounded_rectangle((20, y, w - 20, y + 120), 14, fill=(255, 255, 255))
    av = zap.avatar("Bruno", PERSONAGENS["bruno"]["cor"], 80)
    im.paste(av, (40, y + 20), av if av.mode == "RGBA" else None)
    d.text((140, y + 40), "Vendedor: Bruno R.", font=zap.inter(34, 750), fill=(30, 30, 30), anchor="lm")
    d.text((140, y + 84), "Na plataforma desde março · 6 anúncios", font=zap.inter(26, 450), fill=(110, 110, 110), anchor="lm")
    return im


@functools.lru_cache(None)
def comprovantes():
    """Os três PIX do Vini para o Bruno (compra de volta)."""
    w = 820
    linhas = [("Relógio de bolso", "R$ 900,00"), ("Fone com margarida", "R$ 350,00"), ("Perfume importado", "R$ 280,00")]
    h = 200 + len(linhas) * 80 + 150
    im = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, 120), fill=(0, 121, 107))
    d.text((40, 60), "Comprovantes PIX", font=zap.inter(42, 800), fill=(255, 255, 255), anchor="lm")
    d.text((40, 160), "De: Vinícius Santos   Para: Bruno Rocha", font=zap.inter(30, 600), fill=(70, 70, 70), anchor="lm")
    y = 220
    for a, b in linhas:
        d.text((40, y), a, font=zap.inter(32, 500), fill=(90, 90, 90))
        d.text((w - 40, y), b, font=zap.inter(32, 750), fill=(25, 25, 25), anchor="ra")
        y += 80
    d.line([(40, y + 10), (w - 40, y + 10)], fill=(220, 220, 220), width=3)
    d.rounded_rectangle((26, y + 34, w - 26, y + 110), 10, fill=(255, 241, 118))
    d.text((40, y + 72), "TOTAL", font=zap.inter(36, 800), fill=(25, 25, 25), anchor="lm")
    d.text((w - 40, y + 72), "R$ 1.530,00", font=zap.inter(36, 800), fill=(25, 25, 25), anchor="rm")
    return im


EPISODIOS = [
    # ---------------------------------------------------------------------------------------------- 1
    dict(parte=1, nome="Sumiu", eventos=[
        ("chat", "bruno", "08:10", "HOJE", (("chip", "ONTEM"), ("bruno", "Boa noite, amor 🤍", "23:40"),
                                            ("carol", "Boa noite 🤍", "23:41"))),
        ("msg", "carol", "Amor, você viu o meu fone? Aquele com o adesivo de margarida 🌼"),
        ("msg", "bruno", "Não vi, amor. Você deve ter esquecido na academia.", dict(dig=0.4)),
        ("msg", "carol", "Semana passada foi o perfume. Agora o fone. Tá sumindo tudo aqui de casa."),
        ("msg", "bruno", "Você é muito desligada, Carol 😂"),
        ("msg", "carol", "Não sou, não. E hoje eu fui ver o relógio de bolso do meu avô na gaveta... também sumiu."),
        ("digitando", "bruno", 1.6),
        ("msg", "bruno", "Calma. Quem mais entra aí?"),
        ("msg", "carol", "Só eu, você... e o Vini. Ele ainda tem a chave reserva, de quando cuidou do Pipoca."),
        ("msg", "bruno", "Hmm. Sei não, hein.", dict(dig=0.4)),
        ("msg", "bruno", "Eu nunca fui com a cara desse seu amigo."),
        ("msg", "carol", "Para, Bruno. O Vini é o meu melhor amigo desde a escola."),
        ("chat", "vini", "12:30", "HOJE", (("chip", "SEGUNDA"), ("vini", "E o Pipoca, sobreviveu sem mim? 🐱", "19:02"),
                                           ("carol", "Tá mimado até hoje kkkk", "19:05"))),
        ("msg", "vini", "Carol! Pergunta aleatória.", dict(dig=0.4)),
        ("msg", "vini", "Você ainda tem aquele relógio de bolso do seu avô?"),
        ("rascunho", "Como você sabe que ele sumiu", 1.2),
        ("msg", "carol", "Por que você quer saber?"),
        ("msg", "vini", "Nada não. Depois eu te conto 😅", dict(dig=0.6)),
        ("status", "visto por último hoje às 12:31"),
        ("chat", "bruno", "21:00", "HOJE"),
        ("msg", "bruno", "Amor, olha o story do teu amigo.", dict(dig=0.4)),
        ("foto", "bruno", story_vini, "Esse fone não é o teu?", dict(zoom=True, pausa=0.8, h_max=640)),
        ("msg", "carol", "É o MEU fone. Com o MEU adesivo."),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 2
    dict(parte=2, nome="O plano", eventos=[
        ("chat", "vini", "21:05", "HOJE", (("chip", "HOJE"), ("vini", "Carol! Pergunta aleatória.", "12:30"),
                                           ("vini", "Você ainda tem aquele relógio de bolso do seu avô?", "12:30"))),
        ("msg", "carol", "Vini, esse fone do seu story é de onde?"),
        ("digitando", "vini", 1.8),
        ("msg", "vini", "Comprei de segunda mão 😄 Bonito, né?"),
        ("msg", "carol", "Comprou de quem?"),
        ("msg", "vini", "Depois eu te conto, tô saindo do trabalho.", dict(dig=0.6)),
        ("chat", "bruno", "21:20", "HOJE"),
        ("msg", "bruno", "Segunda mão... sei. Com um adesivo igualzinho ao teu? 🙄"),
        ("msg", "bruno", "Pega essa chave de volta, Carol."),
        ("msg", "carol", "Se eu pedir a chave, ele vai saber que eu desconfio."),
        ("msg", "carol", "Eu preciso ver com os meus olhos. Entrar no apê dele."),
        ("msg", "bruno", "E como você vai entrar lá?", dict(dig=0.4)),
        ("msg", "carol", "O aniversário dele é sábado. Vou fazer uma festa surpresa. No apê dele 🎉"),
        ("msg", "bruno", "Boa. Mas sábado eu tenho futebol, não vou poder ir.", dict(dig=0.6)),
        ("chat", "dani", "21:40", "HOJE"),
        ("msg", "carol", "Oi, Dani! Aqui é a Carol, a amiga do Vini 😊"),
        ("msg", "dani", "Oi, Carol! Tudo bem?", dict(dig=0.3)),
        ("msg", "carol", "Quero fazer uma festa surpresa pro aniversário dele. Sábado, aí no apê de vocês. Me ajuda?"),
        ("msg", "dani", "AMEI! Ele vai chorar 😭", dict(dig=0.3)),
        ("msg", "carol", "Só uma coisa: eu preciso entrar umas duas horas antes. Pra arrumar tudo."),
        ("msg", "dani", "Fechado! Deixo a chave na portaria."),
        ("chat", "grupo", "22:00", "HOJE"),
        ("sistema", "Você criou o grupo \"Surpresa do Vini 🤫🎉\""),
        ("sistema", "Você adicionou Dani, Gui e Thaís"),
        ("msg", "dani", "Gente, NINGUÉM conta pro Vini! 🤫", dict(dig=0.3)),
        ("msg", "thais", "Eu levo o bolo! 🎂", dict(dig=0.3)),
        ("msg", "gui", "Falando nele... o Vini tá estranho essa semana. Disse que tá juntando provas de alguma coisa.", dict(dig=0.6)),
        ("msg", "gui", "E que no sábado ele precisa resolver um assunto sério com a Carol.", dict(dig=0.6)),
        ("rascunho", "Provas de quê??", 1.4),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 3
    dict(parte=3, nome="A caixa", eventos=[
        ("chat", "vini", "10:00", "SÁBADO", (("chip", "QUINTA"), ("vini", "Depois eu te conto, tô saindo do trabalho.", "21:06"))),
        ("msg", "vini", "Carol, hoje à noite você tá livre? Preciso te mostrar uma coisa. É sério."),
        ("rascunho", "Mostrar o quê? As provas?", 1.2),
        ("msg", "carol", "Hoje não dá 😬"),
        ("msg", "vini", "É importante, Carol.", dict(dig=0.4)),
        ("msg", "carol", "Amanhã?"),
        ("msg", "vini", "Tá. Amanhã.", dict(dig=0.8)),
        ("chat", "dani", "17:00", "SÁBADO"),
        ("msg", "dani", "A chave tá na portaria! O Vini só volta às oito 🤫", dict(dig=0.3)),
        ("msg", "carol", "Chegando 🏃‍♀️"),
        ("chat", "bruno", "17:30", "SÁBADO"),
        ("msg", "carol", "Tô no apê dele."),
        ("msg", "bruno", "Procura no quarto. Armário, gaveta, debaixo da cama.", dict(dig=0.3)),
        ("msg", "carol", "Por que você tá tão interessado, Bruno?"),
        ("msg", "bruno", "Porque eu me preocupo contigo, amor 🤍", dict(dig=0.6)),
        ("chat", "grupo", "18:10", "SÁBADO"),
        ("foto", "thais", "bolo.jpg", "Bolo chegando! 🎂"),
        ("msg", "dani", "Carol, cadê você? Tá no quarto do Vini faz meia hora 😂", dict(dig=0.3)),
        ("chat", "bruno", "18:15", "SÁBADO"),
        ("foto", "carol", "armario.jpg", "Tem uma caixa no armário dele. Com o meu nome.", dict(zoom=True, pausa=0.6, h_max=640)),
        ("digitando", "bruno", 1.4),
        ("msg", "bruno", "Abre."),
        ("msg", "carol", "Tá tudo aqui, Bruno. O fone. O perfume. O relógio do meu avô."),
        ("msg", "bruno", "EU SABIA! Ladrão! Chama a polícia!", dict(dig=0.3)),
        ("msg", "carol", "Calma. Tem um envelope aqui embaixo."),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 4
    dict(parte=4, nome="O envelope", eventos=[
        ("chat", "bruno", "18:17", None, (("chip", "SÁBADO"), ("bruno", "EU SABIA! Ladrão! Chama a polícia!", "18:16"),
                                          ("carol", "Calma. Tem um envelope aqui embaixo.", "18:16"))),
        ("foto", "carol", bilhete, None, dict(zoom=True, pausa=4.6, h_max=640)),
        ("msg", "bruno", "Deixa eu ver os prints.", dict(dig=0.3)),
        ("foto", "carol", anuncios, "O vendedor é você, Bruno.", dict(zoom=True, pausa=1.0, h_max=700)),
        ("msg", "bruno", "Isso é montagem dele!", dict(dig=0.3)),
        ("msg", "carol", "Tem a sua foto. E o seu bairro."),
        ("digitando", "bruno", 1.6),
        ("apagar", "bruno"),
        ("chat", "grupo", "20:02", "SÁBADO"),
        ("msg", "dani", "ELE CHEGOU! Apaga a luz! 🤫", dict(dig=0.2)),
        ("msg", "gui", "SURPRESAAA 🎉🎉", dict(dig=0.2)),
        ("chat", "vini", "20:30", "SÁBADO"),
        ("msg", "vini", "Você achou a caixa, né?"),
        ("msg", "carol", "Por que você não me contou?"),
        ("audio", "vini", "Eu vi o relógio do seu avô à venda num site de usados. Reconheci na hora, por isso eu te perguntei dele. "
                          "O vendedor era o Bruno. Aí eu comprei tudo de volta, pra você ter as suas coisas e ter prova."),
        ("msg", "carol", "E aquele story com o fone?"),
        ("msg", "vini", "Postei pra ver a reação do Bruno. Quem te mostrou o story?"),
        ("msg", "carol", "Foi ele. E ainda colocou a culpa em você."),
        ("msg", "vini", "Eu sei que você ama ele, Carol. Eu só não queria te ver sendo enganada.", dict(dig=0.6)),
        ("chat", "bruno", "20:45", "SÁBADO"),
        ("msg", "bruno", "Amor, a gente precisa conversar. Esse cara tá armando contra mim.", dict(dig=0.4)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 5
    dict(parte=5, nome="A festa era sua", fim_texto="Fim", eventos=[
        ("chat", "bruno", "20:46", None, (("chip", "SÁBADO"), ("bruno", "Amor, a gente precisa conversar. Esse cara tá armando contra mim.", "20:45"))),
        ("msg", "carol", "Armando? Então me explica esses PIX."),
        ("foto", "carol", comprovantes, "Do Vini. Pra você. Pelas MINHAS coisas.", dict(zoom=True, pausa=0.8, h_max=600)),
        ("digitando", "bruno", 2.0),
        ("audio", "bruno", "Carol, eu tava devendo, tá? Eu tava desesperado. Eu ia comprar tudo de volta antes de você perceber, eu juro."),
        ("msg", "carol", "Você vendeu o relógio do meu avô."),
        ("msg", "carol", "E jogou a culpa no meu melhor amigo."),
        ("msg", "carol", "As suas coisas vão estar na portaria amanhã. E o chaveiro já troca a fechadura de manhã."),
        ("msg", "bruno", "Carol, por favor 🥺", dict(dig=0.4)),
        ("sistema", "Você bloqueou este contato"),
        ("chat", "vini", "21:10", "SÁBADO"),
        ("msg", "carol", "Vini, eu desconfiei de você. Me perdoa."),
        ("msg", "carol", "Eu te devo mil quinhentos e trinta reais e um pedido de desculpas."),
        ("msg", "vini", "Você me deve é um pedaço de bolo. Hoje é o MEU aniversário, lembra? 😂", dict(dig=0.4)),
        ("msg", "carol", "Parabéns, Vini. Obrigada por cuidar de mim até quando eu desconfiei de você 🌼"),
        ("msg", "vini", "Pra que serve melhor amigo? 🌼", dict(dig=0.6)),
        ("chat", "grupo", "21:20", "SÁBADO"),
        ("msg", "dani", "Vocês dois vão voltar pra sala ou não?? O bolo tá acabando! 🎂", dict(dig=0.3)),
        ("foto", "thais", "brinde.jpg", "Um brinde ao aniversariante! 🥂"),
        ("msg", "carol", "Tô indo! E a próxima festa surpresa é pra você, Dani 😂"),
        ("pausa", 2.4),
    ]),
]
