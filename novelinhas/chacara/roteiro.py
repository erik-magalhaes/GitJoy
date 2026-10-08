"""A Chácara: novela de terror (estilo Pânico) em 7 partes do Compartilhado, no WhatsApp escuro.

Seis amigos marcam um fim de semana na chácara da família do Theo, com milharal, represa e sinal ruim. A Mel, prima do
Theo, sobe na sexta para arrumar tudo e é a primeira vítima (a "garota da abertura"). Depois disso, o assassino usa o
celular dela: as mensagens dele aparecem como "Mel". No sábado o grupo chega, e um por um vai sumindo, em tempo real:
o Breno no carro, a Isa trancada no banheiro, o Theo no milharal. Suspeitos: o caseiro, Seu Dito, e o Kauã, ex da Isa,
que não foi convidado. O motivo só aparece aos poucos: um ano antes, numa festa ali, a Lara (16) foi desafiada a nadar
na represa de madrugada e morreu; o grupo disse à polícia que ela foi sozinha. A assassina é a Bel, "amiga da facul" da
Isa que ninguém conhecia direito: irmã da Lara por parte de pai. Ela sempre sabia onde cada um estava escondido,
porque era ela que mandava cada um para lá. A violência fica só implícita.
"""
import functools
import os
import random

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

import zap

FOTOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fotos")
TITULO = "A Chácara"
TEMA = "escuro"
TRILHA = "terror"

THALITA = ("pt-BR-ThalitaMultilingualNeural", "+0%", "+0Hz")
ANTONIO = ("pt-BR-AntonioNeural", "+0%", "+0Hz")
FRANCISCA = ("pt-BR-FranciscaNeural", "+0%", "+0Hz")
VOZES = {"malu": THALITA, "bel": THALITA, "mel": FRANCISCA, "isa": FRANCISCA,
         "theo": ANTONIO, "breno": ANTONIO, "kaua": ANTONIO, "dito": ANTONIO, "assassino": ANTONIO}
EFEITO_VOZ = {"assassino": "mascara"}   # quem escreve do celular da Mel (a voz do Número Desconhecido, que ele aprovou)
PRONUNCIA = {r"\bKauã\b": "Cauã", r"\bIsa\b": "Iza", r"\bTheo\b": "Téo"}

PERSONAGENS = {
    "malu": dict(nome="Malu", cor=(126, 87, 194)),
    "mel": dict(nome="Mel", cor=(255, 179, 0)),
    "assassino": dict(nome="Mel", cor=(255, 179, 0)),
    "theo": dict(nome="Theo", cor=(30, 136, 229)),
    "breno": dict(nome="Breno", cor=(255, 112, 67)),
    "isa": dict(nome="Isa", cor=(0, 172, 193)),
    "bel": dict(nome="Bel", cor=(236, 64, 122)),
    "kaua": dict(nome="Kauã", cor=(67, 160, 71)),
    "dito": dict(nome="Seu Dito", cor=(141, 110, 99)),
}

NOMES = {"mel": "Mel 🌻", "assassino": "Mel 🌻", "theo": "Theo", "breno": "Breno", "isa": "Isa", "bel": "Bel", "malu": "Malu"}
CHATS = {
    "grupo": dict(dono="malu", titulo="Chácara 🌽🔥", grupo=True, sub="Mel, Theo, Breno, Isa, Bel, Você", nomes=NOMES),
    "mel": dict(dono="malu", titulo="Mel 🌻", com="mel", sub="online"),
    # Parte 1: o celular da Mel (ela é a "dona" da tela)
    "grupo_mel": dict(dono="mel", titulo="Chácara 🌽🔥", grupo=True, sub="Malu, Theo, Breno, Isa, Bel, Você", nomes=NOMES),
    "malu_mel": dict(dono="mel", titulo="Malu 💜", com="malu", sub="online"),
    "theo": dict(dono="malu", titulo="Theo", com="theo", sub="online"),
    "isa": dict(dono="malu", titulo="Isa", com="isa", sub="online"),
    "bel": dict(dono="malu", titulo="Bel (amiga da Isa)", com="bel", sub="online"),
    "kaua": dict(dono="malu", titulo="Kauã", com="kaua", sub="online"),
    "dito": dict(dono="malu", titulo="Seu Dito (caseiro)", com="dito", sub="visto por último ontem"),
}


def _noite(nome, brilho=0.4, seed=1, azul=True):
    """Escurece, tira a cor, puxa para o azul e põe granulado: foto de celular à noite."""
    im = Image.open(os.path.join(FOTOS, nome)).convert("RGB")
    im.thumbnail((900, 900))
    im = ImageEnhance.Brightness(im).enhance(brilho)
    im = ImageEnhance.Color(im).enhance(0.25)
    if azul:
        r, g, b = im.split()
        im = Image.merge("RGB", (r.point(lambda v: int(v * 0.8)), g.point(lambda v: int(v * 0.9)), b))
    px = im.load()
    rnd = random.Random(seed)
    for _ in range(im.width * im.height // 5):
        x, y = rnd.randrange(im.width), rnd.randrange(im.height)
        r, g, b = px[x, y]
        k = rnd.randint(-24, 24)
        px[x, y] = (max(0, min(255, r + k)), max(0, min(255, g + k)), max(0, min(255, b + k)))
    return im.filter(ImageFilter.GaussianBlur(0.7))


@functools.lru_cache(None)
def casa_noite():
    return _noite("casa_chacara.jpg", 0.42, 2)


@functools.lru_cache(None)
def milharal_noite():
    return _noite("milharal_dentro.jpg", 0.75, 4)


@functools.lru_cache(None)
def celeiro_noite():
    return _noite("celeiro.jpg", 0.35, 6)


@functools.lru_cache(None)
def localizacao():
    """Card de localização em tempo real do Theo, parado no meio do milharal."""
    w, h = 720, 620
    im = Image.new("RGB", (w, h), (36, 52, 40))
    d = ImageDraw.Draw(im)
    rnd = random.Random(9)
    for x in range(0, w, 14):   # fileiras do milharal vistas de cima
        d.line([(x, 0), (x + rnd.randint(-6, 6), h - 150)], fill=(48, 72, 50), width=6)
    d.line([(0, 330), (w, 300)], fill=(150, 120, 80), width=18)   # estradinha de terra
    cx, cy = 430, 210
    d.ellipse((cx - 70, cy - 70, cx + 70, cy + 70), fill=(30, 136, 229, 60), outline=(90, 170, 240), width=3)
    d.ellipse((cx - 26, cy - 26, cx + 26, cy + 26), fill=(30, 136, 229), outline=(255, 255, 255), width=5)
    d.rectangle((0, h - 150, w, h), fill=(32, 44, 52))
    d.text((30, h - 110), "Localização em tempo real · Theo", font=zap.inter(32, 750), fill=(235, 235, 235))
    d.text((30, h - 62), "Parado há 6 min · bateria 4%", font=zap.inter(28, 500), fill=(255, 138, 128))
    return im


@functools.lru_cache(None)
def noticia():
    """Print de uma notícia antiga sobre a morte da Lara na represa."""
    w = 820
    im = Image.new("RGB", (w, 760), (250, 250, 250))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, 100), fill=(183, 28, 28))
    d.text((30, 50), "Notícias da Região", font=zap.inter(40, 800), fill=(255, 255, 255), anchor="lm")
    zap.texto_rico(im, 30, 130, "Adolescente de 16 anos morre afogada em represa de chácara durante festa",
                   zap.inter(44, 800), (25, 25, 25), maxw=w - 60)
    d.text((30, 330), "Publicado há 1 ano", font=zap.inter(26, 500), fill=(130, 130, 130))
    texto = ("Lara S., 16 anos, foi encontrada na represa na manhã de domingo. Segundo os amigos ouvidos pela polícia, "
             "a jovem teria entrado na água sozinha, de madrugada, enquanto todos dormiam. O caso foi tratado como acidente.")
    zap.texto_rico(im, 30, 380, texto, zap.inter(32, 450), (40, 40, 40), maxw=w - 60)
    return im


EPISODIOS = [
    # ---------------------------------------------------------------------------------------------- 1
    # A Parte 1 é vista pelo celular da Mel. O wifi cai e os pedidos de socorro dela ficam "não entregue".
    # No fim, o assassino apaga o socorro do grupo e manda, como se fosse ela, que está tudo certo: por isso os amigos sobem.
    dict(parte=1, nome="A primeira", eventos=[
        ("chat", "grupo_mel", "21:00", "SEXTA"),
        ("msg", "theo", "Prima, chegou bem? Amanhã cedo a gente sobe! 🌽🔥", dict(dig=0.3)),
        ("msg", "isa", "Lembrando que a Bel, minha amiga da facul, vai com a gente 😊", dict(dig=0.3)),
        ("msg", "bel", "Oi, gente! Obrigada por me chamarem 🥰", dict(dig=0.4)),
        ("foto", "mel", casa_noite, "Cheguei! O sinal aqui é horrível, só pega no wifi 😂", dict(pausa=0.8)),
        ("msg", "mel", "O Seu Dito, o caseiro, já foi embora. Fiquei só eu e os grilos"),
        ("msg", "malu", "Tranca tudo, hein, Mel! 😂", dict(dig=0.3)),
        ("chat", "malu_mel", "22:40", "SEXTA"),
        ("msg", "mel", "Amiga, acordada?"),
        ("msg", "malu", "Tô! Que foi?", dict(dig=0.3)),
        ("msg", "mel", "Tô ouvindo um barulho no milharal. Tipo alguém andando."),
        ("msg", "malu", "Deve ser bicho, Mel. É roça 😂", dict(dig=0.3)),
        ("assobio", 4.0, 0.25),
        ("msg", "mel", "Bicho não assobia, Malu."),
        ("audio", "mel", "Malu, tem alguém andando em volta da casa. Eu apaguei todas as luzes. Escuta. Ele tá assobiando.",
         dict(assobio=True, assobio_vol=0.35)),
        ("msg", "malu", "Mel, liga pra polícia AGORA", dict(dig=0.2)),
        ("msg", "mel", "não tem sinal pra ligar. só o wifi"),
        ("pausa", 0.8),
        ("msg", "mel", "malu o wifi caiu", dict(falha=True)),
        ("msg", "mel", "ele tá batendo na janela da cozinha", dict(falha=True)),
        ("msg", "mel", "a porta dos fundos tá aberta. eu tranquei. eu TENHO CERTEZA que tranquei", dict(falha=True)),
        ("msg", "mel", "tô escondida no armário do quarto", dict(falha=True)),
        ("assobio", 3.5, 0.3),
        ("msg", "mel", "ele tá no corredor", dict(falha=True)),
        ("msg", "mel", "consigo ouvir ele respirando", dict(falha=True)),
        ("chat", "grupo_mel", "22:51"),
        ("msg", "mel", "SOCORRO", dict(falha=True)),
        ("msg", "mel", "tem alguém aqui dentro da chácara", dict(falha=True)),
        ("msg", "mel", "ele parou na porta do quarto", dict(falha=True)),
        ("pausa", 3.0),
        ("apagar", "mel"),
        ("apagar", "mel"),
        ("apagar", "mel"),
        ("pausa", 0.8),
        ("msg", "assassino", "Gente, alarme falso, era um gato 😂 Tá tudo certo por aqui! Sobe todo mundo amanhã cedo 🌻",
         dict(saida=True)),
        ("msg", "malu", "Ufa! Que susto, amiga 😂 Amanhã às oito a gente sai daqui!", dict(dig=0.4)),
        ("msg", "theo", "Boa, prima! Deixa a cerveja gelando 🍻", dict(dig=0.3)),
        ("pausa", 1.6),
        ("msg", "assassino", "Vou estar esperando vocês 🙂", dict(saida=True)),
        ("pausa", 2.6),
    ]),
    # ---------------------------------------------------------------------------------------------- 2
    # Ninguém recebeu o socorro da Mel: o dia começa alegre. O "recado da Mel" no grupo é do assassino.
    dict(parte=2, nome="O violão", eventos=[
        ("chat", "grupo", "09:40", "SÁBADO"),
        ("foto", "theo", "estrada_terra.jpg", "Estrada de terra = quase lá! 🚗", dict(pausa=0.6)),
        ("msg", "isa", "Já tô sentindo o cheiro do churrasco 😍", dict(dig=0.3)),
        ("msg", "bel", "Primeira vez que eu vou numa chácara, tô animada! 🥰", dict(dig=0.3)),
        ("chat", "grupo", "10:30"),
        ("msg", "theo", "Chegamos! Cadê você, Mel?", dict(dig=0.3)),
        ("msg", "assassino", "Desci pra cidade comprar carvão! A chave tá debaixo do vaso da varanda 🌻", dict(dig=0.8)),
        ("msg", "theo", "Folgada 😂 Valeu, prima!", dict(dig=0.3)),
        ("chat", "theo", "10:40", "SÁBADO"),
        ("msg", "malu", "Theo, ontem a Mel me mandou um áudio de alguém assobiando em volta da casa. Achei tão estranho."),
        ("msg", "theo", "Ela mesma disse no grupo que era um gato, Malu. E hoje já foi pra cidade. Relaxa e curte 😄", dict(dig=0.4)),
        ("msg", "malu", "Tá bom. Vou tentar 😅"),
        ("chat", "grupo", "13:00"),
        ("foto", "isa", "milharal_dia.jpg", "Gente, que lindo esse milharal 😍", dict(pausa=0.6)),
        ("msg", "malu", "O Theo queimou a primeira carne 😂"),
        ("msg", "theo", "Culpa do carvão, que a Mel ainda não trouxe 😂", dict(dig=0.3)),
        ("msg", "bel", "Gente, vocês são muito divertidos 😂🥰", dict(dig=0.3)),
        ("msg", "breno", "Primeira vez que a gente volta aqui desde aquilo, né.", dict(dig=0.6)),
        ("msg", "theo", "Hoje não, Breno.", dict(dig=0.3)),
        ("msg", "bel", "Desde aquilo o quê? 😅", dict(dig=0.4)),
        ("msg", "isa", "Nada, amiga. História velha. Bora curtir 🍻", dict(dig=0.4)),
        ("msg", "breno", "Pelo menos o Kauã não veio.", dict(dig=0.4)),
        ("msg", "isa", "Ninguém chamou o meu ex depois do que ele falou da gente. Graças a Deus.", dict(dig=0.4)),
        ("chat", "grupo", "21:00"),
        ("msg", "theo", "A Mel não voltou da cidade até agora?", dict(dig=0.3)),
        ("msg", "malu", "Ela não me responde desde ontem, Theo."),
        ("msg", "breno", "Vou buscar o violão no carro. Hoje tem roda de música 🎸", dict(dig=0.3)),
        ("msg", "breno", "Gente.", dict(dig=0.2)),
        ("msg", "breno", "Tem alguém parado na beira do milharal olhando pra cá.", dict(dig=0.3)),
        ("msg", "malu", "Volta pra casa, Breno!"),
        ("audio", "breno", "Eu tô voltando... ele tá assobiando. Ele começou a andar na minha direção. Ele tá vindo rápido. Ele tá...",
         dict(assobio=True, assobio_vol=0.35)),
        ("pausa", 2.4),
        ("msg", "isa", "Breno??", dict(dig=0.2)),
        ("msg", "theo", "BRENO", dict(dig=0.2)),
        ("digitando", "assassino", 2.6),
        ("foto", "assassino", milharal_noite, "O Breno não vai mais tocar violão 🙂", dict(zoom=True, pausa=0.8, h_max=560)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 3
    dict(parte=3, nome="O banheiro", eventos=[
        ("chat", "grupo", "21:20", None, (("chip", "SÁBADO"), ("assassino", "O Breno não vai mais tocar violão 🙂", "21:16"))),
        ("msg", "theo", "Todo mundo pra sala. AGORA. Ninguém fica sozinho.", dict(dig=0.2)),
        ("msg", "malu", "Tô na sala com o Theo. Cadê a Isa e a Bel?"),
        ("msg", "isa", "tô no banheiro lá de cima", dict(dig=0.2)),
        ("msg", "bel", "Tô na cozinha, já tô indo!", dict(dig=0.3)),
        ("chat", "isa", "21:24", "SÁBADO"),
        ("msg", "isa", "malu", dict(dig=0.1)),
        ("msg", "isa", "tem alguém subindo a escada", dict(dig=0.2)),
        ("msg", "malu", "Tranca a porta! A gente tá subindo!"),
        ("msg", "isa", "tranquei", dict(dig=0.1)),
        ("msg", "isa", "ele tá na porta", dict(dig=0.2)),
        ("msg", "isa", "tá girando a maçaneta devagar", dict(dig=0.3)),
        ("msg", "isa", "não me liga. o celular vibra. ele vai ouvir", dict(dig=0.2)),
        ("msg", "malu", "O Theo tá subindo com a lanterna"),
        ("pausa", 1.2),
        ("msg", "isa", "ele parou", dict(dig=0.2)),
        ("msg", "isa", "tá sem barulho nenhum", dict(dig=0.4)),
        ("chat", "grupo", "21:27", "SÁBADO"),
        ("msg", "bel", "Isa, pula a janela do banheiro! Dá direto pro milharal. Eu tô aqui fora te esperando!", dict(dig=0.2)),
        ("msg", "isa", "tá bom. vou pular", dict(dig=0.2)),
        ("msg", "theo", "Cheguei no banheiro. A porta tá arrombada. A janela tá aberta.", dict(dig=0.2)),
        ("chat", "isa", "21:30", "SÁBADO"),
        ("msg", "isa", "pulei. tô no milharal", dict(dig=0.2)),
        ("msg", "isa", "bel cadê você", dict(dig=0.2)),
        ("msg", "isa", "tô vendo uma lanterna vindo", dict(dig=0.3)),
        ("msg", "isa", "bel é você?", dict(dig=0.4)),
        ("pausa", 2.4),
        ("msg", "malu", "ISA?"),
        ("chat", "grupo", "21:33", "SÁBADO"),
        ("msg", "bel", "Gente, ele pegou a Isa. EU VI. Tô correndo pro outro lado!!", dict(dig=0.2)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 4
    dict(parte=4, nome="O milharal", eventos=[
        ("chat", "theo", "21:40", "SÁBADO"),
        ("msg", "theo", "Malu, eu fui atrás da Isa. Fica dentro de casa.", dict(dig=0.2)),
        ("msg", "malu", "Theo, não! Volta!"),
        ("msg", "theo", "tô no milharal. tá escuro demais", dict(dig=0.2)),
        ("msg", "theo", "tem alguém andando do meu lado. na outra fileira", dict(dig=0.2)),
        ("msg", "theo", "tô correndo", dict(dig=0.1)),
        ("msg", "theo", "não sei pra que lado é a casa", dict(dig=0.2)),
        ("msg", "theo", "deitei no chão. ele passou do meu lado. vi a bota dele", dict(dig=0.3)),
        ("msg", "malu", "Fica parado, Theo. Me manda a sua localização."),
        ("foto", "theo", localizacao, None, dict(zoom=True, pausa=3.0, h_max=560)),
        ("msg", "malu", "Theo, ela parou de mexer faz seis minutos. Theo?"),
        ("status", "visto por último hoje às 21:46"),
        ("chat", "bel", "21:55", "SÁBADO"),
        ("msg", "bel", "Malu! Eu tô na casinha do caseiro, no fundo da chácara. Tô trancada aqui.", dict(dig=0.3)),
        ("msg", "bel", "Vem pra cá, aqui é seguro. Vem pelo milharal, é mais rápido.", dict(dig=0.3)),
        ("rascunho", "Tô indo", 1.2),
        ("chat", "dito", "21:58", "SÁBADO"),
        ("msg", "malu", "Seu Dito, aqui é a Malu, amiga do Theo. Tem alguém atacando a gente na chácara. Sua casa tá aberta?"),
        ("digitando", "dito", 2.4),
        ("msg", "dito", "Moça, eu tô na cidade desde ontem de manhã. A Dona Mel me dispensou.", dict(dig=0.4)),
        ("msg", "dito", "A minha casinha tá trancada. A chave tá aqui comigo.", dict(dig=0.4)),
        ("msg", "dito", "Não tem ninguém lá dentro.", dict(dig=0.6)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 5
    dict(parte=5, nome="Um ano atrás", eventos=[
        ("chat", "bel", "22:00", "SÁBADO", (("chip", "SÁBADO"),
                                             ("bel", "Vem pra cá, aqui é seguro. Vem pelo milharal, é mais rápido.", "21:55"))),
        ("msg", "bel", "Malu? Você vem?", dict(dig=0.4)),
        ("msg", "malu", "Tô indo, Bel. Me espera.", dict(pausa=0.6)),
        ("chat", "kaua", "22:03", "SÁBADO"),
        ("msg", "malu", "Kauã, é você? É você que tá fazendo isso com a gente?"),
        ("msg", "kaua", "Eu?? Malu, eu tô em casa, em São Paulo! Que história é essa?", dict(dig=0.3)),
        ("msg", "malu", "A Mel, o Breno, a Isa, o Theo. Sumiram todos."),
        ("msg", "malu", "Eu menti pra Bel que tava indo. Tô escondida no celeiro."),
        ("msg", "kaua", "Na chácara... onde a Lara morreu.", dict(dig=0.6)),
        ("msg", "malu", "Ninguém fala o nome dela faz um ano."),
        ("msg", "kaua", "Porque vocês mentiram, Malu.", dict(dig=0.4)),
        ("audio", "kaua", "O Breno e o Theo desafiaram a Lara a atravessar a represa de madrugada. A Isa filmou. A Mel ria. "
                          "E vocês disseram pra polícia que ela entrou na água sozinha. Por isso eu saí do grupo."),
        ("foto", "kaua", noticia, None, dict(zoom=True, pausa=4.2, h_max=620)),
        ("msg", "malu", "Eu tava dormindo, Kauã. Eu só soube de manhã. E fiquei quieta."),
        ("msg", "kaua", "A Lara tinha uma irmã por parte de pai. Na missa, ela jurou que ia descobrir a verdade.", dict(dig=0.4)),
        ("msg", "malu", "Que irmã? Qual o nome dela?"),
        ("msg", "kaua", "Nunca soube. Mas ela era da mesma idade que vocês.", dict(dig=0.4)),
        ("chat", "isa", "22:10", "SÁBADO"),
        ("msg", "malu", "Isa, se você tiver viva, me responde: onde você conheceu a Bel?"),
        ("pausa", 1.6),
        ("chat", "grupo", "22:11", "SÁBADO"),
        ("msg", "malu", "Bel. Qual é o seu sobrenome?"),
        ("digitando", "bel", 2.6),
        ("msg", "bel", "Por que a pergunta, Malu? 🙂", dict(dig=0.2)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 6
    dict(parte=6, nome="A irmã", eventos=[
        ("chat", "bel", "22:13", "SÁBADO"),
        ("msg", "bel", "Você demorou, Malu.", dict(dig=0.4)),
        ("msg", "bel", "Siqueira. Isabel Siqueira. O mesmo sobrenome da Lara.", dict(dig=0.6)),
        ("audio", "bel", "A Lara era a minha irmã. A gente tinha o mesmo pai e a mesma risada. Vocês desafiaram ela, filmaram ela "
                         "se afogando e mentiram pra polícia. Eu passei um ano estudando cada um de vocês."),
        ("msg", "malu", "Eu nem tava acordada, Bel!"),
        ("msg", "bel", "Mas você sabia. E ficou quieta. Igual a todo mundo.", dict(dig=0.4)),
        ("msg", "bel", "Foi tão fácil. Cada um corria exatamente pra onde eu mandava 🙂", dict(dig=0.6)),
        ("chat", "kaua", "22:16", "SÁBADO"),
        ("msg", "malu", "Kauã, é a Bel. Ela é a irmã da Lara. Chama a polícia. Eu tô no celeiro, lá em cima, no feno."),
        ("msg", "kaua", "Já liguei. Tô indo pra aí de carro também. Aguenta!", dict(dig=0.2)),
        ("chat", "mel", "22:18", "SÁBADO"),
        ("digitando", "assassino", 2.0),
        ("foto", "assassino", celeiro_noite, "Feno dá alergia, Malu 🙂", dict(zoom=True, pausa=0.8, h_max=560)),
        ("audio", "assassino", "Eu tô ouvindo o seu celular vibrar. Desliga ele. Ou não. Eu já sei onde você tá.",
         dict(assobio=True, assobio_vol=0.25)),
        ("chat", "kaua", "22:20", "SÁBADO"),
        ("msg", "malu", "ela tá aqui dentro do celeiro", dict(dig=0.1)),
        ("msg", "malu", "tá subindo a escada", dict(dig=0.1)),
        ("msg", "kaua", "Tô a cinco minutos! A polícia tá logo atrás de mim!", dict(dig=0.2)),
        ("msg", "malu", "não vai dar tempo", dict(dig=0.1)),
        ("pausa", 2.6),
    ]),
    # ---------------------------------------------------------------------------------------------- 7
    dict(parte=7, nome="Amanhecer", fim_texto="Fim?", eventos=[
        ("chat", "kaua", "22:24", "SÁBADO", (("chip", "SÁBADO"), ("malu", "não vai dar tempo", "22:20"))),
        ("msg", "kaua", "Malu? Cheguei na porteira! Tô vendo a sirene vindo!", dict(dig=0.2)),
        ("pausa", 1.6),
        ("msg", "malu", "empurrei a escada", dict(dig=0.1)),
        ("msg", "malu", "ela caiu lá embaixo. tá se mexendo. tá procurando a faca no escuro", dict(dig=0.1)),
        ("msg", "kaua", "A polícia tá entrando no celeiro! Fica aí em cima!", dict(dig=0.2)),
        ("pausa", 2.0),
        ("msg", "malu", "pegaram ela", dict(dig=0.3)),
        ("msg", "malu", "pegaram a Bel, Kauã 😭", dict(dig=0.3)),
        ("msg", "kaua", "Acabou, Malu. Pode descer devagar. Eu tô aqui embaixo.", dict(dig=0.4)),
        ("chat", "theo", "06:10", "DOMINGO"),
        ("msg", "theo", "Malu.", dict(dig=0.8)),
        ("msg", "theo", "tô no hospital. me acharam no milharal de madrugada. vou ficar bem", dict(dig=0.6)),
        ("msg", "malu", "THEO 😭 Graças a Deus!"),
        ("msg", "malu", "A Mel, o Breno e a Isa não tiveram a mesma sorte."),
        ("msg", "theo", "Eu sei. A polícia me contou.", dict(dig=0.8)),
        ("msg", "theo", "E eu vou contar a verdade sobre a Lara. Chega de mentira.", dict(dig=0.6)),
        ("msg", "malu", "Eu também, Theo. Eu vou junto."),
        ("chat", "mel", "03:33", "UM MÊS DEPOIS", (("chip", "SÁBADO"), ("assassino", "Feno dá alergia, Malu 🙂", "22:18"))),
        ("digitando", "assassino", 2.4),
        ("msg", "assassino", "Oi, Malu 🙂", dict(dig=0.6)),
        ("msg", "assassino", "A Bel não tava sozinha.", dict(dig=0.8)),
        ("pausa", 2.6),
    ]),
]
