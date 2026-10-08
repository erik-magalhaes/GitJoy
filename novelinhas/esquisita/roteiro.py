"""A Esquisita do 3ºA: novela teen (estilo filme adolescente americano) em 5 partes do Compartilhado.

A Lorena (óculos, aparelho, a melhor em física) vira meme no grupo da turma pela Valentina, a abelha-rainha. O Lucca,
capitão do vôlei, pede ajuda em física e os dois se apaixonam. A Valentina mostra um print: os meninos apostaram R$ 500
em quem levasse "a esquisita" pro baile, e o Lucca respondeu "fechado". O Cadu (melhor amigo) e a irmã dele, a Nanda
(cabeleireira), fazem a transformação "pra ela, não pra ele". O Lucca já tinha cancelado a aposta. No baile, a Lorena
arrasa, o plano da Valentina dá errado e o Lucca chama a Lorena pra dançar.
"""
import functools
import os

from PIL import Image, ImageDraw

import zap

FOTOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fotos")
TITULO = "A Esquisita do 3ºA"

THALITA = ("pt-BR-ThalitaMultilingualNeural", "+0%", "+0Hz")
ANTONIO = ("pt-BR-AntonioNeural", "+0%", "+0Hz")
FRANCISCA = ("pt-BR-FranciscaNeural", "+0%", "+0Hz")
VOZES = {"lorena": THALITA, "nanda": THALITA, "valentina": FRANCISCA, "manu": FRANCISCA,
         "lucca": ANTONIO, "cadu": ANTONIO, "pietro": ANTONIO}
PRONUNCIA = {r"\bLucca\b": "Luca", r"\bCadu\b": "Cadú"}

PERSONAGENS = {
    "lorena": dict(nome="Lorena", cor=(126, 87, 194)),
    "lucca": dict(nome="Lucca", cor=(30, 136, 229)),
    "valentina": dict(nome="Valentina", cor=(216, 27, 96)),
    "cadu": dict(nome="Cadu", cor=(46, 125, 50)),
    "nanda": dict(nome="Nanda", cor=(255, 112, 67)),
    "pietro": dict(nome="Pietro", cor=(0, 137, 123)),
    "manu": dict(nome="Manu", cor=(156, 39, 176)),
}

NOMES = {"valentina": "Valentina", "lucca": "Lucca", "cadu": "Cadu", "pietro": "Pietro", "manu": "Manu"}
CHATS = {
    "turma": dict(dono="lorena", titulo="3ºA Oficial 📚", grupo=True, sub="Valentina, Lucca, Cadu, Pietro, Manu e mais 29",
                  nomes=NOMES),
    "lucca": dict(dono="lorena", titulo="Lucca", com="lucca", sub="online"),
    "cadu": dict(dono="lorena", titulo="Cadu 💚", com="cadu", sub="online"),
    "valentina": dict(dono="lorena", titulo="Valentina", com="valentina", sub="online"),
    "operacao": dict(dono="lorena", titulo="Operação Baile 💄", grupo=True, sub="Cadu, Nanda, Você",
                     nomes={"cadu": "Cadu", "nanda": "Nanda"}),
}


def _foto(nome):
    return Image.open(os.path.join(FOTOS, nome)).convert("RGB")


@functools.lru_cache(None)
def meme_coruja():
    """O meme que a Valentina postou: a coruja com texto branco de contorno preto."""
    im = _foto("coruja.jpg")
    w = 720
    im = im.resize((w, round(w * im.height / im.width)))
    d = ImageDraw.Draw(im)
    f = zap.inter(56, 900)
    for y, txt in ((60, "QUANDO A LORENA"), (im.height - 70, "ENTENDE FÍSICA 🤓")):
        d.text((w // 2, y), txt.replace(" 🤓", ""), font=f, fill=(255, 255, 255), anchor="mm", stroke_width=5,
               stroke_fill=(0, 0, 0))
    return im


def _print_grupo(titulo, msgs, hora="22:10"):
    """Print de um grupo (lista de (nome, cor, texto, hora))."""
    im = zap.papel_parede().copy().convert("RGBA")
    zap.barra_status(im, hora)
    zap.cabecalho(im, titulo, "Pietro, Lucca, Gui, Theo...", (90, 90, 90), grupo=True)
    y = zap.CHAT_Y0 + 24
    for nome, cor, txt, hh in msgs:
        b, pad = zap.balao_texto(txt, hh, False, True, nome, cor)
        im.alpha_composite(b, (zap.ESQ - pad, y - pad))
        y += b.height - 2 * pad + 20
    return im.crop((0, zap.STATUS_Y, zap.W, y + 30)).convert("RGB")


@functools.lru_cache(None)
def print_aposta():
    return _print_grupo("Vôlei 3ºA 🏐", (
        ("Pietro", (0, 137, 123), "Aposta: quem levar a esquisita da Lorena pro baile ganha 500 reais 😂", "21:02"),
        ("Pietro", (0, 137, 123), "Lucca, você que vive pedindo ajuda em física pra ela...", "21:03"),
        ("Lucca", (30, 136, 229), "Fechado 😂", "21:05"),
    ), hora="21:05")


@functools.lru_cache(None)
def print_cancela():
    return _print_grupo("Vôlei 3ºA 🏐", (
        ("Lucca", (30, 136, 229), "Pietro, cancela essa aposta. Não tem graça nenhuma.", "19:40"),
        ("Lucca", (30, 136, 229), "Eu gosto dela de verdade. E se alguém zoar a Lorena de novo, sai do time.", "19:41"),
        ("Pietro", (0, 137, 123), "Calma, capitão 😳 Foi ideia da Valentina, não minha", "19:43"),
    ), hora="19:43")


EPISODIOS = [
    # ---------------------------------------------------------------------------------------------- 1
    dict(parte=1, nome="A coruja", eventos=[
        ("chat", "turma", "13:10", "SEGUNDA"),
        ("msg", "valentina", "Gente, a aula de física hoje foi demais 😂", dict(dig=0.3)),
        ("foto", "valentina", meme_coruja, None, dict(zoom=True, pausa=2.2, h_max=600)),
        ("msg", "pietro", "KKKKKKK MORRI", dict(dig=0.2)),
        ("msg", "manu", "A cara dela 😂😂😂", dict(dig=0.3)),
        ("msg", "valentina", "Brincadeira, Lorena! Você é muito sensível 💅", dict(dig=0.4)),
        ("msg", "cadu", "Valentina, apaga isso. Como representante da sala, tô pedindo. Não tem graça nenhuma.", dict(dig=0.4)),
        ("msg", "valentina", "Ai, chegou o advogado da coruja 🙄", dict(dig=0.3)),
        ("chat", "cadu", "13:20", "SEGUNDA"),
        ("msg", "cadu", "Amiga, ignora. Ela tem inveja porque você tirou dez e ela tirou três 😘", dict(dig=0.4)),
        ("msg", "lorena", "Eu tô cansada, Cadu. Três anos disso."),
        ("msg", "cadu", "Falta só o baile. Depois a gente nunca mais vê essa garota 💚", dict(dig=0.4)),
        ("chat", "lucca", "21:30", "SEGUNDA"),
        ("msg", "lucca", "Oi, Lorena. Aqui é o Lucca, da sua sala.", dict(dig=0.5)),
        ("msg", "lucca", "Foi mal pelo grupo hoje. A Valentina passou dos limites.", dict(dig=0.5)),
        ("rascunho", "O capitão do vôlei falando comigo?", 1.2),
        ("msg", "lorena", "Tudo bem. Já tô acostumada."),
        ("msg", "lucca", "Não devia. Mas então... posso te pedir um favor?", dict(dig=0.6)),
        ("msg", "lucca", "Se eu reprovar em física, o técnico me tira do time. Você me dá umas aulas? 🙏", dict(dig=0.6)),
        ("msg", "lorena", "Eu? Dar aula pra você?"),
        ("msg", "lucca", "Você é a única que entende aquilo lá. Amanhã, na biblioteca?", dict(dig=0.4)),
        ("msg", "lorena", "Tá. Às duas."),
        ("chat", "valentina", "14:40", "TERÇA"),
        ("foto", "valentina", "biblioteca.jpg", "Biblioteca, é? 👀 Tô de olho em você, coruja.", dict(zoom=True, pausa=0.8, h_max=520)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 2
    dict(parte=2, nome="As aulas", eventos=[
        ("chat", "lucca", "22:00", "TERÇA"),
        ("msg", "lucca", "Professora Lorena, fiz o exercício 4 sozinho 😎", dict(dig=0.4)),
        ("msg", "lorena", "Deu quanto?"),
        ("msg", "lucca", "Deu... banana? 🍌", dict(dig=0.6)),
        ("msg", "lorena", "Lucca 😂😂 A resposta era em metros por segundo"),
        ("audio", "lucca", "Tá, eu errei de novo. Mas pelo menos eu fiz você rir. Isso vale meio ponto, né, professora?"),
        ("msg", "lorena", "Vale. Meio ponto 😂"),
        ("chat", "cadu", "22:20", "TERÇA"),
        ("msg", "lorena", "Cadu. O Lucca me fez rir três vezes hoje."),
        ("msg", "cadu", "Três? Amiga, isso é casamento 😂", dict(dig=0.3)),
        ("msg", "lorena", "Para 😂 Ele só precisa passar em física."),
        ("msg", "cadu", "Sei. E por que você tá sorrindo pro celular? Eu sinto daqui 💚", dict(dig=0.4)),
        ("chat", "lucca", "23:10", "QUINTA"),
        ("msg", "lucca", "Lorena, tirei sete na prova!! SETE!! 🎉", dict(dig=0.2)),
        ("msg", "lorena", "EU SABIA!! 🎉"),
        ("msg", "lucca", "Posso te perguntar uma coisa?", dict(dig=0.6)),
        ("msg", "lucca", "Você vai no baile de formatura?", dict(dig=0.8)),
        ("msg", "lorena", "Não sei. Ninguém me chamou."),
        ("msg", "lucca", "Então deixa eu ser o primeiro. Vai comigo? 🙂", dict(dig=0.8)),
        ("msg", "lorena", "Vou 🥹"),
        ("chat", "valentina", "23:30", "QUINTA"),
        ("msg", "valentina", "Oi, coruja. Fiquei sabendo que você vai no baile com o Lucca 😂", dict(dig=0.4)),
        ("msg", "valentina", "Antes de comprar o vestido, dá uma olhadinha nisso 💅", dict(dig=0.4)),
        ("foto", "valentina", print_aposta, None, dict(zoom=True, pausa=3.6, h_max=640)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 3
    dict(parte=3, nome="A aposta", eventos=[
        ("chat", "valentina", "23:31", None, (("chip", "QUINTA"),
                                               ("valentina", "Antes de comprar o vestido, dá uma olhadinha nisso 💅", "23:30"))),
        ("msg", "valentina", "Quinhentos reais, coruja. É isso que você vale 😂", dict(dig=0.4)),
        ("chat", "cadu", "23:35", "QUINTA"),
        ("msg", "lorena", "Cadu. Era uma aposta. Tudo."),
        ("msg", "lorena", "As aulas, as risadas, o convite. Tudo era pra ganhar quinhentos reais."),
        ("msg", "cadu", "Amiga, eu tô indo aí. Não chora sozinha.", dict(dig=0.2)),
        ("chat", "lucca", "23:40", "QUINTA"),
        ("msg", "lorena", "Quinhentos reais, Lucca?"),
        ("digitando", "lucca", 2.6),
        ("msg", "lucca", "Lorena, me deixa explicar", dict(dig=0.2)),
        ("audio", "lucca", "No começo foi aposta, sim. Eu fui um idiota. Mas na segunda aula já não era mais. Eu esperava a terça "
                           "a semana inteira. Eu nunca gostei tanto de física na minha vida."),
        ("msg", "lorena", "Você me fez de piada. Igual a todo mundo."),
        ("sistema", "Você bloqueou este contato"),
        ("chat", "cadu", "00:30", "SEXTA"),
        ("msg", "cadu", "Tô aqui na sua porta com sorvete 🍦", dict(dig=0.3)),
        ("msg", "lorena", "Eu não vou no baile, Cadu."),
        ("msg", "cadu", "Vai sim. E não por causa dele.", dict(dig=0.4)),
        ("msg", "cadu", "Três anos você baixou a cabeça pra Valentina. No último dia, você vai entrar naquele baile de cabeça erguida.",
         dict(dig=0.4)),
        ("msg", "lorena", "Eu nem tenho roupa, nem sei me arrumar."),
        ("msg", "cadu", "Pra isso existe a minha irmã 😏", dict(dig=0.4)),
        ("chat", "operacao", "00:40", "SEXTA"),
        ("sistema", "Cadu criou o grupo \"Operação Baile 💄\""),
        ("sistema", "Cadu adicionou Nanda e você"),
        ("msg", "nanda", "Oi, Lorena! O Cadu me contou tudo. Amanhã às nove no meu salão. Eu cuido de você 💇‍♀️", dict(dig=0.4)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 4
    dict(parte=4, nome="A transformação", eventos=[
        ("chat", "operacao", "09:00", "SÁBADO"),
        ("foto", "nanda", "tesoura_pente.jpg", "Bom dia, cliente VIP! Hoje vai ter corte, hidratação e escova ✂️", dict(pausa=0.6)),
        ("msg", "lorena", "Nanda, só não corta muito, tá? 😬"),
        ("msg", "nanda", "Confia na tia 😂", dict(dig=0.3)),
        ("foto", "lorena", "oculos_livro.jpg", "Primeira vez de lente de contato. Óculos aposentados 🥲", dict(pausa=0.6)),
        ("msg", "cadu", "Aposentados não, de férias! A gente ama esses óculos 💚", dict(dig=0.3)),
        ("foto", "nanda", "maquiagem.jpg", "Agora a parte que eu mais amo 💄", dict(pausa=0.6)),
        ("msg", "lorena", "Gente, eu tô fazendo isso pra mim. Não é pra ele, tá?"),
        ("msg", "nanda", "Exatamente. É pra você se ver do jeito que a gente sempre te viu ✨", dict(dig=0.4)),
        ("chat", "cadu", "15:00", "SÁBADO"),
        ("msg", "cadu", "Amiga. Eu preciso te mostrar uma coisa. O Pietro me mandou isso agora.", dict(dig=0.3)),
        ("foto", "cadu", print_cancela, None, dict(zoom=True, pausa=3.8, h_max=640)),
        ("msg", "cadu", "O Lucca cancelou a aposta na terça. Antes da Valentina te mandar o print.", dict(dig=0.4)),
        ("msg", "cadu", "E a ideia da aposta foi da própria Valentina.", dict(dig=0.4)),
        ("msg", "lorena", "Então ela me mandou um print velho... de propósito."),
        ("msg", "cadu", "Claro. Ela queria que você não fosse no baile.", dict(dig=0.4)),
        ("rascunho", "Desbloquear o Lucca", 1.2),
        ("chat", "operacao", "19:30", "SÁBADO"),
        ("msg", "nanda", "Pronta, Lorena? O Cadu tá esperando no carro 🚗", dict(dig=0.3)),
        ("msg", "lorena", "Pronta. E pela primeira vez, eu gostei do que eu vi no espelho 🥹"),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 5
    dict(parte=5, nome="O baile", fim_texto="Fim", eventos=[
        ("chat", "turma", "21:00", "SÁBADO"),
        ("foto", "manu", "salao_baile.jpg", "O baile tá LINDO 😍", dict(pausa=0.6)),
        ("msg", "pietro", "GENTE. QUEM É ESSA QUE ACABOU DE ENTRAR COM O CADU??", dict(dig=0.2)),
        ("msg", "manu", "É a LORENA?? 😳😳", dict(dig=0.3)),
        ("msg", "pietro", "A Lorena da física??", dict(dig=0.3)),
        ("msg", "valentina", "Até coruja de vestido continua coruja 💅", dict(dig=0.5)),
        ("msg", "cadu", "Valentina, a gente sabe da aposta. E sabe de quem foi a ideia.", dict(dig=0.3)),
        ("msg", "cadu", "E sabe também do balde de tinta que você escondeu atrás do palco pra hora da foto 😉", dict(dig=0.4)),
        ("msg", "manu", "BALDE DE TINTA?? Valentina, que isso??", dict(dig=0.3)),
        ("msg", "pietro", "Já tiramos o balde de lá, Cadu. Tá no banheiro dos professores 😂", dict(dig=0.3)),
        ("chat", "lucca", "21:20", "SÁBADO"),
        ("sistema", "Você desbloqueou este contato"),
        ("msg", "lorena", "O Cadu me mostrou o print de terça. Por que você não me contou?"),
        ("msg", "lucca", "Porque você me bloqueou antes 😅 E porque eu achei que não merecia mais uma chance.", dict(dig=0.4)),
        ("msg", "lucca", "Lorena. Você tá linda. Mas você já era, de óculos e tudo.", dict(dig=0.6)),
        ("msg", "lucca", "Olha pro meio do salão.", dict(dig=0.4)),
        ("foto", "lucca", "globo_luz.jpg", "Me concede essa dança, professora? 🙂", dict(zoom=True, pausa=0.8, h_max=520)),
        ("msg", "lorena", "Só se você acertar a unidade da velocidade 😂"),
        ("msg", "lucca", "Metros por segundo! Tô indo te buscar 😎", dict(dig=0.3)),
        ("chat", "turma", "21:40", "SÁBADO"),
        ("msg", "manu", "O LUCCA TÁ DANÇANDO COM A LORENA 😭😭", dict(dig=0.2)),
        ("msg", "pietro", "Casal do ano, sem discussão 👏", dict(dig=0.3)),
        ("sistema", "Cadu removeu Valentina"),
        ("msg", "cadu", "Agora sim o grupo ficou bonito 💚", dict(dig=0.3)),
        ("pausa", 2.4),
    ]),
]
