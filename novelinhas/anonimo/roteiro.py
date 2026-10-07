"""Número Desconhecido: novela de terror (estilo Pânico) em 5 partes do Compartilhado, no WhatsApp escuro.

Um ano depois da formatura, a turma do 3ºB marca uma reunião. Na festa de formatura, a Nina filmou o Enzo (irmão da
Lari) passando vergonha, o Caio postou e a Duda compartilhou; o vídeo viralizou e o Enzo nunca mais saiu do quarto
(hoje está internado numa clínica em outra cidade). Um número desconhecido começa a perguntar "qual é o seu filme de
terror favorito?" e a turma vai sumindo. Os assassinos são dois: a Lari (que finge ser a primeira vítima) e o Pedro,
namorado da Nina e melhor amigo de infância do Enzo. A Nina se tranca no armário e grava tudo; a mãe chama a polícia.
Seis meses depois, o número desconhecido manda mensagem de novo. A violência fica só implícita.
"""
import functools
import os
import random

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

import zap

FOTOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fotos")
TITULO = "Número Desconhecido"
TEMA = "escuro"
TRILHA = "terror"

THALITA = ("pt-BR-ThalitaMultilingualNeural", "+0%", "+0Hz")
ANTONIO = ("pt-BR-AntonioNeural", "+0%", "+0Hz")
FRANCISCA = ("pt-BR-FranciscaNeural", "+0%", "+0Hz")
VOZES = {"nina": THALITA, "lari": THALITA, "duda": FRANCISCA, "mae": FRANCISCA,
         "pedro": ANTONIO, "caio": ANTONIO, "anonimo": ANTONIO}
EFEITO_VOZ = {"anonimo": "mascara"}   # a voz do número desconhecido é distorcida (grave e áspera)

PERSONAGENS = {
    "nina": dict(nome="Nina", cor=(126, 87, 194)),
    "lari": dict(nome="Lari", cor=(236, 64, 122)),
    "pedro": dict(nome="Pedro", cor=(30, 136, 229)),
    "caio": dict(nome="Caio", cor=(255, 143, 0)),
    "duda": dict(nome="Duda", cor=(0, 172, 193)),
    "mae": dict(nome="Mãe", cor=(124, 179, 66)),
    "anonimo": dict(nome="?", cor=(70, 70, 70)),
}

NOMES = {"lari": "Lari", "pedro": "Pedro", "caio": "Caio", "duda": "Duda", "anonimo": "+55 11 97666-0013"}
CHATS = {
    "mae": dict(dono="nina", titulo="Mãe 💚", com="mae", sub="online"),
    "turma": dict(dono="nina", titulo="3ºB pra sempre 🎓", grupo=True, sub="Lari, Pedro, Caio, Duda, Você", nomes=NOMES),
    "anonimo": dict(dono="nina", titulo="+55 11 97666-0013", com="anonimo", sub=""),
    "pedro": dict(dono="nina", titulo="Pedro ❤️", com="pedro", sub="online"),
    "lari": dict(dono="nina", titulo="Lari 🌙", com="lari", sub="online"),
}


def _escuro(nome, brilho=0.45, seed=1):
    """Escurece, tira a cor e põe granulado: cara de foto tirada no escuro, de longe."""
    im = Image.open(os.path.join(FOTOS, nome)).convert("RGB")
    im.thumbnail((900, 900))
    im = ImageEnhance.Brightness(im).enhance(brilho)
    im = ImageEnhance.Color(im).enhance(0.3)
    px = im.load()
    rnd = random.Random(seed)
    for _ in range(im.width * im.height // 6):
        x, y = rnd.randrange(im.width), rnd.randrange(im.height)
        r, g, b = px[x, y]
        k = rnd.randint(-26, 26)
        px[x, y] = (max(0, min(255, r + k)), max(0, min(255, g + k)), max(0, min(255, b + k + 4)))
    return im.filter(ImageFilter.GaussianBlur(0.6))


@functools.lru_cache(None)
def foto_casa():
    """A casa da Nina, fotografada da rua, à noite."""
    return _escuro("casas_noite.jpg", 0.75, 2)


@functools.lru_cache(None)
def foto_corredor():
    """O corredor da casa da Nina, por dentro."""
    return _escuro("corredor.jpg", 0.6, 5)


@functools.lru_cache(None)
def video_formatura():
    """Miniatura do vídeo que viralizou (borrado, com o botão de play e as visualizações)."""
    w, h = 720, 900
    base = Image.open(os.path.join(FOTOS, "brinde.jpg")).convert("RGB")
    esc = max(w / base.width, h / base.height)
    base = base.resize((round(base.width * esc), round(base.height * esc)))
    base = base.crop(((base.width - w) // 2, (base.height - h) // 2, (base.width - w) // 2 + w, (base.height - h) // 2 + h))
    im = ImageEnhance.Brightness(base.filter(ImageFilter.GaussianBlur(10))).enhance(0.6).convert("RGBA")
    d = ImageDraw.Draw(im)
    d.ellipse((w // 2 - 80, h // 2 - 80, w // 2 + 80, h // 2 + 80), fill=(0, 0, 0, 140))
    d.polygon([(w // 2 - 28, h // 2 - 45), (w // 2 - 28, h // 2 + 45), (w // 2 + 48, h // 2)], fill=(255, 255, 255))
    d.text((30, 40), "formatura_3B_KKKK.mp4", font=zap.inter(36, 700), fill=(255, 255, 255))
    d.rounded_rectangle((30, h - 120, w - 30, h - 40), 16, fill=(0, 0, 0, 160))
    d.text((w // 2, h - 80), "▶ 2,1 milhões de visualizações", font=zap.inter(36, 700), fill=(255, 255, 255), anchor="mm")
    return im.convert("RGB")


EPISODIOS = [
    # ---------------------------------------------------------------------------------------------- 1
    dict(parte=1, nome="O filme favorito", eventos=[
        ("chat", "mae", "22:40", "HOJE"),
        ("msg", "mae", "Filha, tô de plantão no hospital até as sete. Tranca a porta, tá? 💚", dict(dig=0.4)),
        ("msg", "nina", "Pode deixar, mãe. Beijo"),
        ("chat", "turma", "22:50", "HOJE"),
        ("msg", "caio", "Sábado faz um ano de formatura! Churrasco na minha casa? 🍖", dict(dig=0.3)),
        ("msg", "duda", "Eu vou! Saudade de vocês 🥹", dict(dig=0.3)),
        ("msg", "lari", "Vou sim. Mas sem o meu irmão, né.", dict(dig=0.6)),
        ("msg", "nina", "Como o Enzo tá, Lari?"),
        ("msg", "lari", "Do mesmo jeito. Desde aquele vídeo da formatura ele não sai mais do quarto.", dict(dig=0.6)),
        ("msg", "caio", "Gente, eu já pedi desculpa mil vezes. Era só uma brincadeira.", dict(dig=0.4)),
        ("msg", "pedro", "Deixa isso pra lá. Sábado eu levo o carvão 🔥", dict(dig=0.4)),
        ("chat", "anonimo", "23:10", "HOJE"),
        ("msg", "anonimo", "Oi, Nina 🙂", dict(dig=0.6)),
        ("msg", "anonimo", "Qual é o seu filme de terror favorito?", dict(dig=0.8)),
        ("msg", "nina", "Quem é?"),
        ("msg", "anonimo", "Responde. Depois eu digo quem eu sou.", dict(dig=0.6)),
        ("msg", "nina", "Pânico. Agora fala quem é."),
        ("msg", "anonimo", "Boa escolha. Sabe o que acontece com quem ri nesse filme?", dict(dig=0.8)),
        ("foto", "anonimo", foto_casa, "A sua casa é bonita à noite.", dict(zoom=True, pausa=0.8, h_max=560)),
        ("chat", "turma", "23:14", "HOJE"),
        ("msg", "nina", "Gente, um número estranho tá me mandando foto da minha casa."),
        ("msg", "duda", "Pra mim também chegou mensagem! Perguntou o meu filme de terror favorito 😳", dict(dig=0.3)),
        ("msg", "lari", "Pra mim também kkkk. Caio, é você, né?", dict(dig=0.4)),
        ("msg", "caio", "Não sou eu!! Juro!", dict(dig=0.2)),
        ("msg", "lari", "Gente, espera. Tem alguém aqui no meu quintal.", dict(dig=0.6)),
        ("msg", "nina", "Lari??"),
        ("msg", "nina", "LARI, RESPONDE"),
        ("chat", "anonimo", "23:20", "HOJE"),
        ("msg", "anonimo", "A Lari não vai no churrasco de sábado 🙂", dict(dig=1.0)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 2
    dict(parte=2, nome="Um ano atrás", eventos=[
        ("chat", "lari", "23:21", "HOJE", (("chip", "ONTEM"), ("lari", "Amiga, amanhã a gente fala do churrasco 🌙", "21:15"))),
        ("msg", "nina", "Lari, me responde, pelo amor de Deus."),
        ("sistema", "Chamada de voz não atendida"),
        ("status", "visto por último hoje às 23:16"),
        ("chat", "turma", "23:23", "HOJE"),
        ("msg", "caio", "Gente, calma. É trote. A Lari tá zoando com a gente.", dict(dig=0.3)),
        ("sistema", "+55 11 97666-0013 entrou usando o link de convite"),
        ("msg", "anonimo", "Um ano atrás, vocês riram do Enzo.", dict(dig=0.6)),
        ("msg", "anonimo", "Hoje, quem vai rir sou eu.", dict(dig=0.6)),
        ("foto", "anonimo", video_formatura, "Lembram desse vídeo?", dict(zoom=True, pausa=0.8, h_max=560)),
        ("msg", "caio", "Enzo? É você, cara? Me desculpa!", dict(dig=0.2)),
        ("msg", "duda", "Gente, eu vou chamar a polícia.", dict(dig=0.3)),
        ("msg", "caio", "Calma, Duda! Se for trote, vai dar problema pra todo mundo.", dict(dig=0.3)),
        ("chat", "pedro", "23:26", "HOJE"),
        ("msg", "nina", "Pedro, tô com medo."),
        ("msg", "nina", "Fui eu que filmei o Enzo naquela festa. Eu nunca te contei isso."),
        ("msg", "nina", "Ninguém sabe que fui eu. Só eu e a Lari."),
        ("msg", "pedro", "Eu sei. Calma, tô indo pra sua casa.", dict(dig=0.4)),
        ("chat", "turma", "23:35", "HOJE"),
        ("audio", "caio", "Gente, a luz da minha casa apagou do nada. Tem alguém mexendo na porta da cozinha. Enzo, se for você, "
                          "me escuta, eu só postei o vídeo, eu não sabia que ia viralizar..."),
        ("msg", "caio", "TÁ AQUI DENTR", dict(dig=0.2)),
        ("msg", "nina", "CAIO?"),
        ("msg", "anonimo", "Faltam três 🙂", dict(dig=1.0)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 3
    dict(parte=3, nome="Por dentro", eventos=[
        ("chat", "pedro", "23:45", "HOJE", (("chip", "HOJE"), ("pedro", "Eu sei. Calma, tô indo pra sua casa.", "23:26"))),
        ("msg", "pedro", "Cheguei. Abre a porta.", dict(dig=0.3)),
        ("msg", "nina", "Abri. Entra rápido."),
        ("msg", "pedro", "Tranca a porta de novo. Eu vou olhar a casa.", dict(dig=0.3)),
        ("chat", "turma", "23:50", "HOJE", (("chip", "HOJE"), ("anonimo", "Faltam três 🙂", "23:36"))),
        ("msg", "duda", "Gente, a polícia ligou de volta.", dict(dig=0.3)),
        ("msg", "duda", "O Enzo tá internado numa clínica em outra cidade há seis meses. Não pode ser ele.", dict(dig=0.4)),
        ("msg", "nina", "Então quem é??"),
        ("msg", "duda", "Não sei. Mas essa pessoa sabe tudo da gente. Só pode ser alguém da turma.", dict(dig=0.4)),
        ("chat", "anonimo", "23:58", "HOJE"),
        ("foto", "anonimo", foto_corredor, "A sua casa por dentro é mais bonita ainda.", dict(zoom=True, pausa=0.8, h_max=560)),
        ("chat", "pedro", "23:59", "HOJE"),
        ("msg", "nina", "Pedro, ele tá AQUI DENTRO. Mandou foto do corredor."),
        ("msg", "nina", "Você foi ver a cozinha e não voltou. Cadê você?"),
        ("msg", "pedro", "Tô aqui embaixo. Fica no quarto e não sai.", dict(dig=0.6)),
        ("chat", "mae", "00:01", "HOJE"),
        ("msg", "nina", "Mãe, tem alguém aqui em casa. Chama a polícia. Eu tô escondida no armário."),
        ("msg", "mae", "Filha??? Tô ligando agora! Não sai daí!", dict(dig=0.2)),
        ("chat", "turma", "00:03", "HOJE"),
        ("msg", "duda", "Nina, quem tá aí com você?", dict(dig=0.3)),
        ("msg", "nina", "O Pedro."),
        ("msg", "duda", "Nina... eu pedi pro meu primo da operadora puxar esse número desconhecido.", dict(dig=0.4)),
        ("msg", "duda", "O chip tá no nome de", dict(dig=0.2)),
        ("pausa", 1.6),
        ("msg", "anonimo", "Faltam dois 🙂", dict(dig=1.0)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 4
    dict(parte=4, nome="Dois", eventos=[
        ("chat", "anonimo", "00:05", "HOJE", (("chip", "HOJE"),
                                             ("anonimo", "A sua casa por dentro é mais bonita ainda.", "23:58"))),
        ("msg", "nina", "O que você quer de mim?"),
        ("digitando", "anonimo", 2.4),
        ("audio", "pedro", "Sabe o que é engraçado, Nina? Foi você mesma que abriu a porta pra mim."),
        ("msg", "nina", "Pedro???"),
        ("chat", "pedro", "00:06", "HOJE"),
        ("msg", "nina", "Por quê, Pedro?"),
        ("audio", "pedro", "O Enzo era o meu melhor amigo desde criança. Aí você filmou ele, o Caio postou, a Duda compartilhou. "
                           "E todo mundo riu. Até você. Eu comecei a namorar você só pra chegar até aqui."),
        ("msg", "nina", "Você matou o Caio."),
        ("msg", "pedro", "Eu não tava sozinho.", dict(dig=0.6)),
        ("msg", "nina", "Eu confiei em você."),
        ("chat", "lari", "00:08", "HOJE", (("chip", "HOJE"), ("nina", "Lari, me responde, pelo amor de Deus.", "23:21"))),
        ("msg", "lari", "Surpresa 🙂", dict(dig=0.4)),
        ("audio", "lari", "O meu irmão tá numa clínica há seis meses, Nina. E vocês marcando churrasco. Eu só fingi que sumi, "
                          "pra ninguém desconfiar de mim. A Duda já era. Agora falta você."),
        ("msg", "nina", "Lari, eu te pedi desculpa. Eu chorei com você no hospital."),
        ("msg", "lari", "Eu lembro. Eu tava lá. Você chorou e depois foi pra praia 🙂", dict(dig=0.6)),
        ("chat", "anonimo", "00:10", "HOJE"),
        ("msg", "anonimo", "Toc, toc 🙂", dict(dig=0.8)),
        ("msg", "anonimo", "A gente tá na porta do seu quarto.", dict(dig=0.6)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 5
    dict(parte=5, nome="Fim?", fim_texto="Fim?", eventos=[
        ("chat", "mae", "00:11", "HOJE", (("chip", "HOJE"),
                                          ("nina", "Mãe, tem alguém aqui em casa. Chama a polícia. Eu tô escondida no armário.", "00:01"),
                                          ("mae", "Filha??? Tô ligando agora! Não sai daí!", "00:01"))),
        ("msg", "mae", "A polícia tá virando a esquina, filha! Aguenta!", dict(dig=0.2)),
        ("msg", "nina", "Mãe, é o Pedro e a Lari. Eles tão na porta do meu quarto."),
        ("msg", "nina", "Eles me mandaram áudio confessando tudo. Eu salvei e te encaminhei agora."),
        ("msg", "nina", "Se eu não sair daqui, entrega pra polícia."),
        ("msg", "mae", "Recebi os áudios. Eles tão entrando aí, filha. Não abre o armário.", dict(dig=0.3)),
        ("pausa", 2.0),
        ("msg", "mae", "Filha?", dict(dig=0.2)),
        ("msg", "mae", "NINA, ME RESPONDE", dict(dig=0.2)),
        ("digitando", "nina", 2.0),
        ("msg", "nina", "Pegaram os dois, mãe. Tô viva. 💚"),
        ("msg", "mae", "Graças a Deus, filha! Tô indo pra casa agora.", dict(dig=0.3)),
        ("msg", "nina", "Mãe, o Pedro dormia aqui em casa. A gente confiava nele."),
        ("msg", "mae", "Eu sei, filha. Eu sei.", dict(dig=0.6)),
        ("chat", "turma", "01:30", "HOJE"),
        ("msg", "duda", "Gente... tô no hospital. Levei pontos, mas tô viva.", dict(dig=0.4)),
        ("msg", "nina", "Duda!!! Graças a Deus."),
        ("msg", "duda", "E o Caio?", dict(dig=0.6)),
        ("msg", "nina", "A polícia achou ele. Ele não resistiu."),
        ("msg", "duda", "Eu não acredito que era a Lari. Ela chorava pelo irmão todo dia.", dict(dig=0.4)),
        ("msg", "nina", "Ela chorava de verdade. Só que de raiva."),
        ("chat", "anonimo", "02:00", "6 MESES DEPOIS", (("chip", "HOJE"), ("anonimo", "Toc, toc 🙂", "00:10"))),
        ("msg", "anonimo", "Oi, Nina 🙂", dict(dig=1.0)),
        ("msg", "anonimo", "Qual é o seu filme de terror favorito?", dict(dig=0.8)),
        ("pausa", 2.6),
    ]),
]
