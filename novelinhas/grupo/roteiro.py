"""Grupo Errado: novela em 5 partes do Compartilhado.

A Bruna (74) manda sem querer no grupo do condomínio uma mensagem picante para o amante, o Marcelo (casado).
Ela não sabe que a esposa dele é a própria síndica, a Vera (que na verdade se chama Verônica).
Tom picante só na insinuação; nada explícito (o TikTok derruba).
"""
import functools
import random

from PIL import Image, ImageDraw, ImageFilter

import zap
from sogra.roteiro import print_conversa

TITULO = "Grupo Errado"

AVA = ("en-US-AvaMultilingualNeural", "+0%", "+0Hz")      # voz 2 da amostra (mulheres)
BRIAN = ("en-US-BrianMultilingualNeural", "+0%", "+0Hz")  # voz 7 da amostra (homens)
VOZES = {"bruna": AVA, "vera": AVA, "sueli": AVA, "tati": AVA,
         "marcelo": BRIAN, "osvaldo": BRIAN, "novo": BRIAN}

PERSONAGENS = {
    "bruna": dict(nome="Bruna", cor=(233, 30, 99)),
    "marcelo": dict(nome="Marcelo", cor=(55, 71, 79)),
    "vera": dict(nome="Vera", cor=(94, 53, 177)),
    "sueli": dict(nome="Sueli", cor=(255, 143, 0)),
    "osvaldo": dict(nome="Osvaldo", cor=(0, 121, 107)),
    "tati": dict(nome="Tati", cor=(216, 27, 96)),
    "novo": dict(nome="Novo", cor=(30, 136, 229)),
}

GRUPO_NOMES = {"vera": "Vera Síndica", "sueli": "Sueli 32", "osvaldo": "Osvaldo 51", "marcelo": "Marcelo 11"}
CHATS = {
    "cond": dict(dono="bruna", titulo="Condomínio Jardim Primavera 🏢", grupo=True,
                 sub="Vera Síndica, Sueli 32, Osvaldo 51, Marcelo 11 e mais 38", nomes=GRUPO_NOMES),
    "m": dict(dono="bruna", titulo="M 🔥", com="marcelo", sub="online"),
    "tati": dict(dono="bruna", titulo="Tati 💋", com="tati", sub="online"),
    "sueli_b": dict(dono="bruna", titulo="Sueli 32", com="sueli", sub="online"),
    "vera_b": dict(dono="bruna", titulo="Vera Síndica", com="vera", sub="online"),
    "veronica": dict(dono="marcelo", titulo="Verônica 💍", com="vera", sub="online"),
    "novo": dict(dono="bruna", titulo="+55 11 98820-4471", com="novo", sub="online"),
}


# ------------------------------------------------------------------ imagens
@functools.lru_cache(None)
def enquete():
    """Enquete da Sueli no grupo (cartão no estilo do WhatsApp)."""
    w, h = 760, 640
    im = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(im)
    zap.texto_rico(im, 36, 30, "ENQUETE: Quem é o perfumado do prédio? 👀", zap.inter(38, 750), (17, 27, 33), maxw=690)
    d.text((36, 150), "Selecione uma opção", font=zap.inter(26, 450), fill=(120, 130, 136))
    ops = [("Alguém do bloco B", 9), ("O personal do 63", 7), ("Seu Osvaldo", 4), ("Prefiro não saber", 12)]
    total = max(v for _, v in ops)
    y = 210
    for txt, v in ops:
        d.ellipse((36, y, 76, y + 40), outline=(160, 170, 175), width=4)
        d.text((100, y + 2), txt, font=zap.inter(34, 450), fill=(17, 27, 33))
        d.text((w - 36, y + 2), str(v), font=zap.inter(32, 600), fill=(84, 101, 111), anchor="ra")
        d.rounded_rectangle((100, y + 56, w - 36, y + 66), 5, fill=(230, 233, 235))
        d.rounded_rectangle((100, y + 56, 100 + (w - 136) * v / total, y + 66), 5, fill=(0, 168, 132))
        y += 100
    d.text((w / 2, h - 30), "32 votos", font=zap.inter(28, 600), fill=(0, 150, 120), anchor="mm")
    return im


@functools.lru_cache(None)
def camera():
    """Imagem da câmera do corredor: um homem entrando no 74 às 23h."""
    w, h = 800, 600
    rnd = random.Random(3)
    im = Image.new("L", (w, h), 40)
    d = ImageDraw.Draw(im)
    # corredor em perspectiva
    d.polygon([(0, h), (w, h), (520, 300), (280, 300)], fill=70)            # chão
    d.polygon([(0, 0), (280, 120), (280, 300), (0, h)], fill=55)            # parede esq.
    d.polygon([(w, 0), (520, 120), (520, 300), (w, h)], fill=60)            # parede dir.
    d.rectangle((280, 120, 520, 300), fill=35)                               # fundo
    # porta do 74 (parede direita) entreaberta, com luz saindo
    d.polygon([(640, 140), (720, 90), (720, 520), (640, 430)], fill=95)
    d.polygon([(640, 140), (660, 128), (660, 418), (640, 430)], fill=170)
    d.text((675, 70), "74", font=zap.inter(30, 700), fill=150)
    # silhueta entrando
    d.ellipse((560, 205, 600, 250), fill=18)
    d.rounded_rectangle((548, 248, 614, 380), 22, fill=18)
    d.rectangle((556, 370, 578, 460), fill=18)
    d.rectangle((586, 370, 606, 455), fill=18)
    # luminária
    d.ellipse((370, 40, 430, 60), fill=200)
    im = im.filter(ImageFilter.GaussianBlur(1.4))
    px = im.load()
    for _ in range(26000):  # granulado de câmera de segurança
        x, y = rnd.randrange(w), rnd.randrange(h)
        px[x, y] = max(0, min(255, px[x, y] + rnd.randint(-40, 40)))
    im = im.convert("RGB")
    d = ImageDraw.Draw(im)
    d.text((20, 18), "CAM 03 · 7º ANDAR", font=zap.inter(30, 700), fill=(235, 235, 235))
    d.text((w - 20, 18), "SEX 23:04:17", font=zap.inter(30, 700), fill=(235, 235, 235), anchor="ra")
    d.ellipse((24, h - 46, 46, h - 24), fill=(220, 30, 30))
    d.text((56, h - 50), "REC", font=zap.inter(28, 700), fill=(235, 235, 235))
    return im


@functools.lru_cache(None)
def print_grupo():
    """O print que a Sueli tirou antes de a Bruna apagar."""
    return print_conversa("Condomínio Jardim Primavera 🏢", (90, 110, 120), (
        ("bruna", "Ainda tô sentindo o seu perfume... Amanhã a porta fica destrancada de novo 😏🔥", "23:47"),
        ("sueli", "EITA 👀", "23:47"),
    ), hora="23:48", dono="sueli")


# ------------------------------------------------------------------ episódios
EPISODIOS = [
    # ---------------------------------------------------------------------------------------------- 1
    dict(parte=1, nome="Grupo errado", eventos=[
        ("chat", "m", "23:40", "HOJE", (("chip", "ONTEM"), ("marcelo", "Saudade de ontem 🔥", "22:10"),
                                        ("bruna", "Para que eu não consigo dormir 😏", "22:12"))),
        ("msg", "marcelo", "Hoje ela dormiu cedo.", dict(dig=0.5)),
        ("msg", "bruna", "Então sobe 😏"),
        ("msg", "marcelo", "Você é perigosa 🔥", dict(dig=0.4)),
        ("chat", "cond", "23:47", "HOJE", (("chip", "HOJE"),
                                           ("vera", "Lembrando: a manutenção do elevador é amanhã às 8h.", "19:00"),
                                           ("osvaldo", "Obrigado, síndica. Boa noite a todos 🌹", "19:30"))),
        ("msg", "bruna", "Ainda tô sentindo o seu perfume... Amanhã a porta fica destrancada de novo 😏🔥"),
        ("digitando", "sueli", 1.0),
        ("msg", "sueli", "EITA 👀", dict(dig=0.2)),
        ("apagar", "bruna"),
        ("msg", "sueli", "Apagou não adianta, eu li 👀👀", dict(dig=0.4)),
        ("msg", "osvaldo", "Boa noite. Que porta?"),
        ("msg", "marcelo", "Gente, alguém sabe se o elevador volta a funcionar amanhã?"),
        ("msg", "sueli", "Marcelo, ninguém quer saber de elevador agora kkkk"),
        ("msg", "sueli", "Quem é o perfumado do prédio??"),
        ("msg", "marcelo", "Deve ter sido engano, Sueli. Vamos dormir, pessoal 😅"),
        ("msg", "vera", "Lembrando que o grupo é para assuntos do condomínio. Boa noite."),
        ("chat", "tati", "23:52", "HOJE"),
        ("msg", "bruna", "TATI. Eu mandei a mensagem do M no grupo do PRÉDIO"),
        ("msg", "tati", "MENTIRA. A do perfume??", dict(dig=0.3)),
        ("msg", "bruna", "A do perfume. E da porta destrancada 😭"),
        ("msg", "tati", "Amiga... ele é casado. E se a mulher dele tá nesse grupo?"),
        ("msg", "bruna", "Eu sei que ele é casado, Tati, não começa. Eu nem sei quem é a mulher dele."),
        ("chat", "m", "23:55"),
        ("msg", "marcelo", "Você mandou no grupo do PRÉDIO??", dict(dig=0.4)),
        ("msg", "marcelo", "Não responde ninguém. Fica quieta que passa."),
        ("msg", "bruna", "Já apaguei! Mas a Sueli viu..."),
        ("msg", "marcelo", "A Sueli vê tudo.", dict(dig=0.3)),
        ("msg", "marcelo", "Minha mulher acordou. Depois a gente fala.", dict(dig=0.7)),
        ("status", "visto por último hoje às 23:56"),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 2
    dict(parte=2, nome="Quem é o perfumado?", eventos=[
        ("chat", "cond", "09:10", "HOJE", (("chip", "ONTEM"), ("marcelo", "Deve ter sido engano, Sueli. Vamos dormir, pessoal 😅", "23:49"),
                                           ("vera", "Lembrando que o grupo é para assuntos do condomínio. Boa noite.", "23:50"))),
        ("msg", "sueli", "Bom dia, vizinhos! Fiz uma enquete 😇"),
        ("foto", "sueli", enquete, None, dict(pausa=3.4, h_max=600, zoom=True)),
        ("msg", "osvaldo", "Por que eu tô na enquete? Eu uso Avanço desde 1978."),
        ("msg", "sueli", "Exatamente, Seu Osvaldo 👀"),
        ("msg", "marcelo", "Sueli, isso é perda de tempo. Bom dia a todos."),
        ("msg", "vera", "Sueli, por favor, apague essa enquete."),
        ("msg", "sueli", "Apago quando a pessoa que mandou a mensagem se apresentar 😇"),
        ("chat", "sueli_b", "09:30", "HOJE"),
        ("msg", "sueli", "Bom dia, vizinha do 74 😘"),
        ("msg", "sueli", "Eu vi a mensagem antes de você apagar. O número era o seu."),
        ("msg", "bruna", "Sueli, por favor, não fala nada pra ninguém."),
        ("msg", "sueli", "Calma, eu sou um túmulo 🤐"),
        ("msg", "sueli", "Só me conta uma coisinha: ele é do prédio?"),
        ("rascunho", "É sim, ele mora no", 0.8),
        ("msg", "bruna", "Não é da sua conta, Sueli."),
        ("msg", "sueli", "Hmm... demorou pra responder 👀"),
        ("chat", "veronica", "10:05", "HOJE", (("chip", "ONTEM"), ("vera", "Compra pão quando voltar? 🥖", "18:20"))),
        ("msg", "vera", "Marcelo, onde você foi ontem às onze da noite? Acordei e você não tava na cama."),
        ("msg", "marcelo", "Desci pra pegar uma encomenda na portaria, amor."),
        ("msg", "vera", "Às onze da noite?"),
        ("msg", "marcelo", "Coisa do trabalho. Volta a dormir 😘"),
        ("msg", "vera", "São dez da manhã, Marcelo."),
        ("chat", "vera_b", "19:00"),
        ("msg", "vera", "Boa noite, Bruna. Aqui é a Vera, a síndica."),
        ("msg", "vera", "Preciso falar com você sobre a mensagem de ontem. Em particular.", dict(dig=0.8)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 3
    dict(parte=3, nome="A síndica", eventos=[
        ("chat", "vera_b", "19:01", None, (("chip", "HOJE"), ("vera", "Boa noite, Bruna. Aqui é a Vera, a síndica.", "19:00"),
                                           ("vera", "Preciso falar com você sobre a mensagem de ontem. Em particular.", "19:00"))),
        ("msg", "bruna", "Boa noite, Dona Vera. Que mensagem?"),
        ("msg", "vera", "Não se faça de boba. A Sueli me mandou o print."),
        ("foto", "vera", print_grupo, None, dict(pausa=3.0, h_max=560, w=700, zoom=True)),
        ("msg", "bruna", "Dona Vera, isso é a minha vida pessoal. Não tem nada a ver com o condomínio."),
        ("msg", "vera", "Teria, se não fosse no MEU prédio."),
        ("msg", "vera", "E tem mais uma coisa."),
        ("foto", "vera", camera, None, dict(pausa=3.4, h_max=600, zoom=True)),
        ("msg", "vera", "A câmera do corredor mostra um homem entrando no 74 às onze da noite."),
        ("digitando", "vera", 1.6),
        ("msg", "vera", "Esse homem é o MEU marido.", dict(dig=0.3)),
        ("rascunho", "Dona Vera, eu", 1.0),
        ("msg", "bruna", "O Marcelo... é casado com a senhora?"),
        ("msg", "vera", "Ele te disse que a mulher dele se chamava Verônica, não disse?"),
        ("msg", "vera", "Pois é. Verônica sou eu. Vera é apelido.", dict(dig=0.8)),
        ("chat", "tati", "19:20", "HOJE"),
        ("msg", "bruna", "Tati. A mulher do M é a SÍNDICA do meu prédio."),
        ("msg", "tati", "A VERA?? A que manda multa por vaso na varanda??", dict(dig=0.3)),
        ("msg", "bruna", "Essa mesma. E ela tem o vídeo da câmera."),
        ("msg", "tati", "Amiga, eu avisei que isso ia dar ruim 😬"),
        ("msg", "bruna", "O pior é que eu sabia que ele era casado. Só não sabia com QUEM."),
        ("msg", "tati", "E agora?"),
        ("msg", "bruna", "Agora eu tô com medo de sair no corredor 😭"),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 4
    dict(parte=4, nome="A esposa", eventos=[
        ("chat", "m", "19:25", "HOJE"),
        ("msg", "bruna", "MARCELO. A sua mulher é a SÍNDICA??"),
        ("msg", "marcelo", "Calma. Quem te falou isso?", dict(dig=0.4)),
        ("msg", "bruna", "ELA. Ela tem o vídeo da câmera, Marcelo!"),
        ("digitando", "marcelo", 1.6),
        ("msg", "marcelo", "Nega tudo. Diz que eu fui consertar o seu chuveiro.", dict(dig=0.3)),
        ("msg", "bruna", "Às onze da noite?? De perfume??"),
        ("msg", "marcelo", "Eu vou dar um jeito. Confia em mim 🙏"),
        ("msg", "bruna", "Confiar? Você nunca me disse que a sua mulher era a síndica!"),
        ("msg", "marcelo", "Você nunca perguntou 😅"),
        ("msg", "bruna", "MARCELO."),
        ("chat", "vera_b", "21:00", "HOJE"),
        ("msg", "vera", "Bruna. Eu não vou fazer escândalo."),
        ("audio", "vera", "Eu sou casada com o Marcelo há doze anos. Eu já desconfiava faz tempo. Você não é a primeira, viu? "
                          "Só foi a primeira a mandar no grupo do prédio."),
        ("msg", "bruna", "Dona Vera... me desculpa. Eu sabia que ele era casado. Eu não devia."),
        ("msg", "vera", "Não devia mesmo. Mas agora eu preciso de você."),
        ("msg", "vera", "Me ajuda a pegar ele no flagra. Na frente de todo mundo."),
        ("msg", "bruna", "Como?"),
        ("msg", "vera", "Hoje ele vai te mandar mensagem. Responde normal. Eu cuido do resto 😌"),
        ("chat", "m", "22:58"),
        ("msg", "marcelo", "Ela foi dormir.", dict(dig=0.4)),
        ("msg", "marcelo", "Posso subir? 😏", dict(dig=0.6)),
        ("rascunho", "Não sobe, ela sabe", 1.2),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 5
    dict(parte=5, nome="Assembleia extraordinária", fim_texto="Fim", eventos=[
        ("chat", "m", "23:00", None, (("chip", "HOJE"), ("marcelo", "Ela foi dormir.", "22:58"), ("marcelo", "Posso subir? 😏", "22:58"))),
        ("msg", "bruna", "Pode. Porta destrancada 😏"),
        ("msg", "marcelo", "Tô subindo 🔥", dict(dig=0.3)),
        ("chat", "vera_b", "23:01"),
        ("msg", "bruna", "Ele tá subindo."),
        ("msg", "vera", "Ótimo. Eu e o porteiro estamos no corredor 😌", dict(dig=0.4)),
        ("chat", "cond", "08:00", "HOJE"),
        ("msg", "vera", "📢 ASSEMBLEIA EXTRAORDINÁRIA hoje, às 19h, no salão de festas."),
        ("msg", "vera", "Pauta: troca da fechadura do apartamento 11 e a saída de um morador."),
        ("msg", "sueli", "QUEM VAI SAIR?? 👀", dict(dig=0.3)),
        ("msg", "osvaldo", "Vai ter bolo?"),
        ("msg", "vera", "O Marcelo, Sueli. Meu marido. Ex-marido, a partir de hoje."),
        ("msg", "vera", "As malas dele estão na portaria."),
        ("msg", "sueli", "EU SABIA!! O PERFUMADO 😱", dict(dig=0.3)),
        ("msg", "marcelo", "Vera, a gente pode conversar em casa?"),
        ("msg", "vera", "Que casa?"),
        ("sistema", "Vera Síndica removeu Marcelo 11"),
        ("msg", "osvaldo", "Então não vai ter bolo?"),
        ("chat", "vera_b", "19:40", "HOJE"),
        ("msg", "vera", "Obrigada, Bruna. Doeu, mas foi libertador."),
        ("msg", "bruna", "Desculpa por tudo, Dona Vera."),
        ("msg", "vera", "Pode me chamar de Vera. E da próxima vez, confere o grupo antes de mandar 😉"),
        ("chat", "novo", "22:30", "HOJE"),
        ("msg", "novo", "Oi, vizinha 😏", dict(dig=0.6)),
        ("msg", "novo", "Sou o novo morador do 52. Me disseram que a porta do 74 tem fama de ficar destrancada...", dict(dig=0.9)),
        ("rascunho", "Quem te disse isso", 1.2),
        ("pausa", 2.4),
    ]),
]
