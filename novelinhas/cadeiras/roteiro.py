"""As Cadeiras: novela (comédia) em 5 partes do Compartilhado. Baseada num causo real contado pelo dono.

O Léo se mudou com a Bia e comprou 4 cadeiras num site de usados. O vendedor, Seu Valdir, entregou tudo certinho e, ao
mostrar "outros móveis" no celular, passou uma foto dele pelado. O Léo conta tudo no grupo dos amigos (Rafa e Teco),
que insistem para ele aceitar as fotos que o Valdir oferece no WhatsApp. No meio dos móveis: o Valdir de calcinha.
A Bia pega o celular, se apresenta como esposa, e o Valdir apaga todas as fotos dos móveis... menos a de calcinha.
Continuação: a Sônia, esposa do Valdir, acha a conversa (a calcinha é dela), descobre que ele faz isso com todo
comprador (o Teco comprou a mesa e também recebeu) e vende tudo dele.
As fotos "proibidas" nunca aparecem: ficam borradas com um 🙈.
"""
import functools
import os

from PIL import Image, ImageDraw, ImageFilter

import zap

FOTOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fotos")
TITULO = "As Cadeiras"

THALITA = ("pt-BR-ThalitaMultilingualNeural", "+0%", "+0Hz")
ANTONIO = ("pt-BR-AntonioNeural", "+0%", "+0Hz")
FRANCISCA = ("pt-BR-FranciscaNeural", "+0%", "+0Hz")
VOZES = {"bia": THALITA, "sonia": FRANCISCA,
         "leo": ANTONIO, "rafa": ANTONIO, "teco": ANTONIO, "valdir": ANTONIO}

PERSONAGENS = {
    "leo": dict(nome="Léo", cor=(21, 101, 192)),
    "bia": dict(nome="Bia", cor=(194, 24, 91)),
    "rafa": dict(nome="Rafa", cor=(230, 81, 0)),
    "teco": dict(nome="Teco", cor=(46, 125, 50)),
    "valdir": dict(nome="Valdir", cor=(121, 85, 72)),
    "sonia": dict(nome="Sônia", cor=(142, 36, 170)),
}

NOMES = {"rafa": "Rafa", "teco": "Teco"}
CHATS = {
    "bia": dict(dono="leo", titulo="Bia ❤️", com="bia", sub="online"),
    "grupo": dict(dono="leo", titulo="Os Parça 🍻", grupo=True, sub="Rafa, Teco, Você", nomes=NOMES),
    "valdir": dict(dono="leo", titulo="Valdir Cadeiras 🪑", com="valdir", sub="online"),
    "sonia": dict(dono="leo", titulo="+55 11 98734-2210", com="sonia", sub="online"),
}


def _foto(nome):
    return Image.open(os.path.join(FOTOS, nome)).convert("RGB")


def _cobre(im, w, h):
    esc = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * esc), round(im.height * esc)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


@functools.lru_cache(None)
def censurada():
    """A foto que ninguém precisa ver: borrada, cor de pele, com um 🙈 enorme por cima."""
    w, h = 720, 720
    base = _cobre(_foto("sofa.jpg"), w, h).filter(ImageFilter.GaussianBlur(40))
    pele = Image.new("RGB", (w, h), (226, 170, 140))
    im = Image.blend(base, pele, 0.6).convert("RGBA")
    m = zap.emoji_img("🙈", 380)
    im.alpha_composite(m, ((w - m.width) // 2, (h - m.height) // 2 - 60))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((170, h - 190, w - 170, h - 110), 40, fill=(0, 0, 0, 150))
    d.text((w // 2, h - 150), "CENSURADO", font=zap.inter(44, 800), fill=(255, 255, 255), anchor="mm")
    return im.convert("RGB")


@functools.lru_cache(None)
def bazar():
    """Anúncio da Sônia no site de usados."""
    w = 840
    itens = [("sofa.jpg", "Sofá de couro", "R$ 300"), ("comoda.jpg", "Cômoda preta", "R$ 150"),
             ("mesa.jpg", "Mesa de madeira", "VENDIDA")]
    h = 300 + len(itens) * 190 + 40
    im = Image.new("RGB", (w, h), (240, 240, 244))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, 100), fill=(106, 27, 154))
    d.text((30, 50), "Desapega Já", font=zap.inter(44, 800), fill=(255, 255, 255), anchor="lm")
    d.rounded_rectangle((20, 120, w - 20, 270), 14, fill=(255, 255, 255))
    d.text((44, 150), "VENDO TUDO DO MEU MARIDO", font=zap.inter(40, 800), fill=(30, 30, 30))
    d.text((44, 210), "Motivo: ele sabe. Retirar com a Sônia.", font=zap.inter(30, 500), fill=(110, 110, 110))
    y = 290
    for arq, nome, preco in itens:
        d.rounded_rectangle((20, y, w - 20, y + 170), 14, fill=(255, 255, 255))
        im.paste(_cobre(_foto(arq), 150, 150), (30, y + 10))
        d.text((210, y + 50), nome, font=zap.inter(34, 650), fill=(30, 30, 30), anchor="lm")
        d.text((210, y + 115), preco, font=zap.inter(40, 800), fill=(106, 27, 154) if preco != "VENDIDA" else (200, 40, 40),
               anchor="lm")
        y += 190
    return im


EPISODIOS = [
    # ---------------------------------------------------------------------------------------------- 1
    dict(parte=1, nome="As cadeiras", eventos=[
        ("chat", "bia", "10:00", "HOJE", (("chip", "ONTEM"),
                                          ("bia", "Amor, a casa nova tá linda, mas a gente não tem onde sentar 😂", "22:10"))),
        ("msg", "leo", "Achei quatro cadeiras num site de usados. Cento e vinte reais as quatro!"),
        ("foto", "leo", "cadeira.jpg", "Olha que linda"),
        ("msg", "bia", "Barato demais, hein. Cuidado com golpe.", dict(dig=0.4)),
        ("msg", "leo", "O vendedor vai entregar aqui hoje. É o Seu Valdir. Super educado."),
        ("msg", "bia", "Tá bom. Eu tô no trabalho até as oito ❤️"),
        ("chat", "grupo", "19:30", "HOJE"),
        ("msg", "leo", "Gente. GENTE."),
        ("audio", "leo", "Vocês não vão acreditar. O Seu Valdir, o vendedor das cadeiras, entregou tudo certinho. Aí ele falou: "
                         "tenho outros móveis, olha as fotos. E começou a passar no celular. Cadeira, mesa... e do nada, uma foto "
                         "dele pelado. Pelado, gente!"),
        ("msg", "rafa", "KKKKKKKKK MENTIRA", dict(dig=0.2)),
        ("msg", "teco", "E você fez o quê??", dict(dig=0.3)),
        ("msg", "leo", "Fingi que não vi! Falei \"que mesa bonita, hein\" 😭"),
        ("msg", "rafa", "\"Que mesa bonita\" kkkkkk eu morri", dict(dig=0.3)),
        ("msg", "teco", "E ele?"),
        ("msg", "leo", "Passou pra próxima foto como se nada tivesse acontecido."),
        ("msg", "rafa", "Você printou?"),
        ("msg", "leo", "Printar como, Rafa? O celular era DELE!"),
        ("msg", "teco", "E a Bia já sabe?", dict(dig=0.3)),
        ("msg", "leo", "Tô com vergonha de contar 😂"),
        ("chat", "valdir", "21:00", "HOJE"),
        ("msg", "valdir", "Boa noite, Léo! Aqui é o Valdir, das cadeiras 😊", dict(dig=0.5)),
        ("msg", "valdir", "Tenho outros móveis. Quer que eu mande as fotos? 📸", dict(dig=0.8)),
        ("rascunho", "Não precisa, obrig", 1.2),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 2
    dict(parte=2, nome="Pode mandar", eventos=[
        ("chat", "valdir", "21:01", None, (("chip", "HOJE"), ("valdir", "Boa noite, Léo! Aqui é o Valdir, das cadeiras 😊", "21:00"),
                                           ("valdir", "Tenho outros móveis. Quer que eu mande as fotos? 📸", "21:00"))),
        ("pausa", 1.0),
        ("chat", "grupo", "21:02", "HOJE"),
        ("msg", "leo", "Gente, o Valdir me chamou no zap. Quer me mandar FOTOS dos outros móveis."),
        ("msg", "rafa", "MANDA ELE MANDAR", dict(dig=0.2)),
        ("msg", "teco", "Pelo amor de Deus, Léo. Pela ciência.", dict(dig=0.3)),
        ("msg", "leo", "Vocês são doentes."),
        ("msg", "rafa", "Ninguém sai desse grupo até ele mandar 😂", dict(dig=0.3)),
        ("msg", "rafa", "E se vier foto, você encaminha aqui 👀", dict(dig=0.3)),
        ("msg", "leo", "NUNCA. Eu tenho família."),
        ("msg", "leo", "Tá bom. Mas eu só vou olhar os móveis."),
        ("chat", "valdir", "21:05", "HOJE"),
        ("msg", "leo", "Pode mandar, Seu Valdir."),
        ("msg", "valdir", "Opa! 😊", dict(dig=0.3)),
        ("foto", "valdir", "sofa.jpg", "Sofá de couro, trezentos reais"),
        ("foto", "valdir", "comoda.jpg", "Cômoda, cento e cinquenta"),
        ("foto", "valdir", censurada, None, dict(pausa=1.6)),
        ("foto", "valdir", "mesa.jpg", "Mesa de madeira, duzentos"),
        ("rascunho", "Seu Valdir, a terceira foto", 1.4),
        ("chat", "grupo", "21:08", "HOJE"),
        ("msg", "leo", "Gente."),
        ("msg", "leo", "No meio dos móveis, ele mandou uma foto DE CALCINHA."),
        ("msg", "leo", "Ele. De calcinha."),
        ("msg", "rafa", "EU NÃO TÔ BEM 😭😭😭", dict(dig=0.2)),
        ("msg", "teco", "Calcinha de que cor?", dict(dig=0.4)),
        ("msg", "leo", "TECO, PELO AMOR DE DEUS."),
        ("chat", "bia", "21:20", "HOJE"),
        ("msg", "bia", "Cheguei, amor! Me empresta o seu celular? O meu descarregou."),
        ("rascunho", "Agora não, amor", 1.2),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 3
    dict(parte=3, nome="A esposa", eventos=[
        ("chat", "valdir", "21:30", None, (("chip", "HOJE"), ("leo", "Pode mandar, Seu Valdir.", "21:05"),
                                           ("valdir", "Opa! 😊", "21:05"),
                                           ("foto", "valdir", "sofa.jpg", "21:05", 230, 340),
                                           ("foto", "valdir", "comoda.jpg", "21:05", 230, 340),
                                           ("foto", "valdir", censurada, "21:06", 340, 340),
                                           ("foto", "valdir", "mesa.jpg", "21:06", 230, 340))),
        ("pausa", 1.2),
        ("msg", "leo", "Boa noite, Seu Valdir. Aqui é a Bia, a ESPOSA do Léo.", dict(dig=1.0)),
        ("msg", "leo", "Eu tô vendo todas as fotos. Inclusive essa aí."),
        ("msg", "leo", "Essa de calcinha também tá à venda?"),
        ("digitando", "valdir", 1.2),
        ("apagar", "valdir"),
        ("apagar", "valdir", dict(pular=1)),
        ("apagar", "valdir", dict(pular=1)),
        ("msg", "valdir", "MEU DEUS! Me desculpa, Dona Bia!", dict(dig=0.2)),
        ("msg", "valdir", "Foi sem querer, mandei a foto errada 🙏", dict(dig=0.3)),
        ("msg", "leo", "Seu Valdir... o senhor apagou os móveis."),
        ("msg", "leo", "E deixou SÓ a calcinha."),
        ("digitando", "valdir", 2.0),
        ("msg", "valdir", "Como que apaga pra todo mundo???", dict(dig=0.2)),
        ("chat", "grupo", "21:45", "HOJE"),
        ("audio", "leo", "Gente, a Bia pegou o meu celular e escreveu pro Valdir que é a minha esposa. Ele pediu desculpa, saiu "
                         "apagando tudo... e apagou todas as fotos dos móveis. Sobrou só a foto de calcinha!"),
        ("msg", "rafa", "Isso não é vendedor, isso é artista", dict(dig=0.3)),
        ("msg", "leo", "Eu nunca mais compro nada usado."),
        ("msg", "rafa", "Fala isso pras cadeiras 😂", dict(dig=0.3)),
        ("msg", "teco", "Ele ainda vende a mesa? Tô precisando de uma", dict(dig=0.4)),
        ("chat", "sonia", "23:10", "HOJE"),
        ("msg", "sonia", "Boa noite. Quem é você e por que o meu marido tá te mandando foto?", dict(dig=0.4)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 4
    dict(parte=4, nome="A outra esposa", eventos=[
        ("chat", "sonia", "23:11", None, (("chip", "HOJE"),
                                          ("sonia", "Boa noite. Quem é você e por que o meu marido tá te mandando foto?", "23:10"))),
        ("msg", "leo", "Senhora, eu só comprei umas cadeiras!"),
        ("msg", "sonia", "Cadeiras. Sei.", dict(dig=0.4)),
        ("audio", "sonia", "Eu sou a Sônia, mulher do Valdir. Peguei o celular dele e achei a conversa com você. Tá tudo apagado, "
                           "só sobrou uma foto. E a calcinha da foto é minha!"),
        ("msg", "leo", "A calcinha é SUA??"),
        ("msg", "leo", "Dona Sônia, vou passar pra minha esposa. Ela explica melhor."),
        ("pausa", 1.2),
        ("msg", "leo", "Oi, Dona Sônia! Aqui é a Bia, esposa do Léo.", dict(dig=1.0)),
        ("msg", "leo", "Pode ficar tranquila. Ninguém aqui quer o seu marido 😂"),
        ("digitando", "sonia", 1.8),
        ("msg", "sonia", "Me desculpa, Bia. É que ele faz isso com todo mundo que compra alguma coisa dele."),
        ("msg", "sonia", "Você é o terceiro comprador que recebe foto essa semana."),
        ("msg", "leo", "TERCEIRO??"),
        ("chat", "grupo", "23:30", "HOJE"),
        ("msg", "leo", "Gente, a esposa do Valdir me chamou. A calcinha é dela."),
        ("msg", "leo", "E ele manda foto pra TODO comprador. Eu sou o terceiro da semana."),
        ("msg", "rafa", "Ele tem um catálogo 😭", dict(dig=0.3)),
        ("digitando", "teco", 2.2),
        ("msg", "teco", "Gente... eu fui buscar a mesa dele agora à noite.", dict(dig=0.2)),
        ("msg", "teco", "E ele me mostrou a foto também.", dict(dig=0.6)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 5
    dict(parte=5, nome="O bazar", fim_texto="Fim", eventos=[
        ("chat", "grupo", "23:32", None, (("chip", "ONTEM"), ("teco", "Gente... eu fui buscar a mesa dele agora à noite.", "23:31"),
                                          ("teco", "E ele me mostrou a foto também.", "23:31"))),
        ("msg", "rafa", "TECO, VOCÊ É O QUARTO", dict(dig=0.2)),
        ("audio", "teco", "Eu fui buscar a mesa e, na hora de pagar, ele falou: olha, tenho outros móveis. Eu já sabia o que "
                          "vinha. Fechei o olho, peguei a mesa e saí correndo. Mas deu tempo de ver, gente. Deu tempo."),
        ("msg", "leo", "Pelo menos a mesa é boa?"),
        ("msg", "teco", "A mesa é ótima. O resto eu quero esquecer.", dict(dig=0.4)),
        ("chat", "sonia", "09:00", "HOJE", (("chip", "ONTEM"), ("leo", "TERCEIRO??", "23:20"))),
        ("msg", "sonia", "Bom dia, Léo e Bia. Pensei a noite inteira e decidi.", dict(dig=0.4)),
        ("foto", "sonia", bazar, "Vou vender tudo dele.", dict(zoom=True, pausa=1.0, h_max=700)),
        ("msg", "sonia", "E pra vocês, a cômoda sai de graça. Pelo trauma.", dict(dig=0.4)),
        ("msg", "leo", "Dona Sônia, aqui é a Bia de novo. A senhora é das minhas 😂", dict(dig=0.8)),
        ("msg", "leo", "Mas pode ficar com a cômoda. A gente vai comprar tudo novo daqui pra frente."),
        ("msg", "sonia", "Faz bem, querida. E se for comprar usado, compra de mulher 😂", dict(dig=0.4)),
        ("chat", "grupo", "09:30", "HOJE"),
        ("msg", "leo", "Moral da história: comprem tudo novo."),
        ("msg", "teco", "Tarde demais pra mim 😭", dict(dig=0.3)),
        ("msg", "rafa", "Léo, o Valdir mandou foto nova hoje?", dict(dig=0.3)),
        ("msg", "leo", "SAI DO GRUPO, RAFA."),
        ("sistema", "Você removeu Rafa"),
        ("pausa", 2.4),
    ]),
]
