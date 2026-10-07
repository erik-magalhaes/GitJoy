"""Grupo Errado: novela em 5 partes do Compartilhado.

A Bruna (74) manda sem querer no grupo do condomínio uma mensagem picante para o amante, o Marcelo (casado).
Ela sabe que ele é casado, mas não sabe que a esposa é a própria síndica, a Vera (Verônica).
Quem conta é um chantagista anônimo: o Seu Osvaldo (51), ex-síndico que ainda tem a senha das câmeras e deve
R$ 15 mil de condomínio (a Vera quer leiloar o apartamento dele). A pista é a rosa 🌹 que ele usa em tudo.
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
         "marcelo": BRIAN, "osvaldo": BRIAN, "novo": BRIAN, "anon": BRIAN}

PERSONAGENS = {
    "bruna": dict(nome="Bruna", cor=(233, 30, 99)),
    "marcelo": dict(nome="Marcelo", cor=(55, 71, 79)),
    "vera": dict(nome="Vera", cor=(94, 53, 177)),
    "sueli": dict(nome="Sueli", cor=(255, 143, 0)),
    "osvaldo": dict(nome="Osvaldo", cor=(0, 121, 107)),
    "tati": dict(nome="Tati", cor=(216, 27, 96)),
    "novo": dict(nome="Novo", cor=(30, 136, 229)),
    "anon": dict(nome="?", cor=(120, 120, 120)),
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
    "anon": dict(dono="bruna", titulo="+55 11 99104-2207", com="anon", sub="online"),
}


# ------------------------------------------------------------------ imagens
@functools.lru_cache(None)
def enquete():
    """Enquete da Sueli no grupo (cartão no estilo do WhatsApp)."""
    w, h = 760, 640
    im = Image.new("RGBA", (w, h), (255, 255, 255, 255))
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
    return im.convert("RGB")


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


@functools.lru_cache(None)
def inadimplentes():
    """Lista de inadimplentes que a síndica colou no elevador."""
    w, h = 760, 820
    im = Image.new("RGB", (w, h), (252, 250, 240))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, 120), fill=(94, 53, 177))
    d.text((w / 2, 60), "CONDOMÍNIO JARDIM PRIMAVERA", font=zap.inter(36, 800), fill=(255, 255, 255), anchor="mm")
    d.text((w / 2, 180), "UNIDADES EM ATRASO", font=zap.inter(44, 800), fill=(30, 30, 30), anchor="mm")
    y = 260
    for apto, valor, alerta in (("Apto 22", "R$ 640,00", False), ("Apto 51", "R$ 15.320,00", True),
                                ("Apto 93", "R$ 1.280,00", False), ("Apto 104", "R$ 410,00", False)):
        if alerta:
            d.rounded_rectangle((40, y - 14, w - 40, y + 66), 10, fill=(255, 241, 118))
        d.text((70, y), apto, font=zap.inter(40, 700), fill=(30, 30, 30))
        d.text((w - 70, y), valor, font=zap.inter(40, 700 if alerta else 450), fill=(198, 40, 40) if alerta else (30, 30, 30), anchor="ra")
        y += 110
    d.text((70, h - 150), "Apto 51: em processo de leilão.", font=zap.inter(32, 700), fill=(198, 40, 40))
    d.text((70, h - 90), "A Administração (Vera, síndica)", font=zap.inter(30, 450), fill=(90, 90, 90))
    return im


# ------------------------------------------------------------------ episódios
EPISODIOS = [
    # ---------------------------------------------------------------------------------------------- 1
    dict(parte=1, nome="Grupo errado", eventos=[
        ("chat", "m", "23:40", "HOJE", (("chip", "ONTEM"), ("marcelo", "Saudade de ontem 🔥", "22:10"),
                                        ("bruna", "Para que eu não consigo dormir 😏", "22:12"))),
        ("msg", "marcelo", "Hoje ela dormiu cedo.", dict(dig=0.5)),
        ("msg", "bruna", "Então sobe 😏"),
        ("msg", "marcelo", "Você é perigosa 🔥", dict(dig=0.4)),
        ("chat", "cond", "23:47", None, (("chip", "HOJE"),
                                           ("vera", "Lembrando: a manutenção do elevador é amanhã às 8h.", "19:00"),
                                           ("osvaldo", "Obrigado, síndica. Boa noite a todos 🌹", "19:30"))),
        ("msg", "bruna", "Ainda tô sentindo o seu perfume... Amanhã a porta fica destrancada de novo 😏🔥"),
        ("digitando", "sueli", 1.0),
        ("msg", "sueli", "EITA 👀", dict(dig=0.2)),
        ("apagar", "bruna"),
        ("msg", "sueli", "Apagou não adianta, eu li 👀👀", dict(dig=0.4)),
        ("msg", "osvaldo", "Boa noite. Que porta?"),
        ("msg", "marcelo", "@Vera Síndica deu tudo certo com o técnico do elevador?"),
        ("msg", "vera", "Deu sim. Amanhã às 8h volta a funcionar."),
        ("msg", "sueli", "Ninguém quer saber de elevador agora kkkk"),
        ("msg", "sueli", "Quem é o perfumado do prédio??"),
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
        ("chat", "cond", "09:10", "HOJE", (("chip", "ONTEM"), ("sueli", "Quem é o perfumado do prédio??", "23:49"),
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
        ("chat", "anon", "19:00"),
        ("msg", "anon", "Boa noite, perfumada 🌹", dict(dig=0.8)),
        ("msg", "anon", "Gostei da sua mensagem de ontem no grupo."),
        ("msg", "anon", "Amanhã a gente conversa 🌹", dict(dig=0.8)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 3
    dict(parte=3, nome="O número desconhecido", eventos=[
        ("chat", "anon", "19:02", None, (("chip", "ONTEM"), ("anon", "Boa noite, perfumada 🌹", "19:00"),
                                         ("anon", "Gostei da sua mensagem de ontem no grupo.", "19:00"),
                                         ("anon", "Amanhã a gente conversa 🌹", "19:01"), ("chip", "HOJE"))),
        ("msg", "bruna", "Quem é você?"),
        ("msg", "anon", "Alguém que tem acesso às câmeras do prédio 🌹", dict(dig=0.8)),
        ("foto", "anon", camera, None, dict(pausa=3.4, h_max=600, zoom=True)),
        ("msg", "anon", "Bonito esse perfumado entrando no 74 às onze da noite, né?"),
        ("msg", "bruna", "Isso não é da sua conta."),
        ("msg", "anon", "Sabe quem é a esposa dele?"),
        ("digitando", "anon", 1.6),
        ("msg", "anon", "A síndica. A Dona Vera 😉", dict(dig=0.3)),
        ("rascunho", "Mentira, ele disse que", 1.0),
        ("msg", "anon", "Cinco mil reais até sexta. Ou o grupo inteiro vê esse vídeo. Inclusive ela 🌹"),
        ("chat", "m", "19:15", "HOJE"),
        ("msg", "bruna", "Marcelo. A sua mulher é a SÍNDICA??"),
        ("msg", "marcelo", "Calma. Quem te falou isso?", dict(dig=0.4)),
        ("msg", "bruna", "Alguém tá me chantageando. Tem o vídeo da câmera. Quer cinco mil."),
        ("digitando", "marcelo", 1.6),
        ("msg", "marcelo", "Paga. Pelo amor de Deus, paga. Depois eu te devolvo.", dict(dig=0.3)),
        ("msg", "bruna", "Você nunca me disse que ela era a síndica!"),
        ("msg", "marcelo", "Você nunca perguntou 😅"),
        ("msg", "bruna", "MARCELO."),
        ("msg", "marcelo", "Se ela descobrir, eu tô ferrado. Paga, por favor."),
        ("msg", "bruna", "E se eu não pagar?"),
        ("digitando", "marcelo", 1.4),
        ("status", "visto por último hoje às 19:17"),
        ("chat", "anon", "19:30"),
        ("msg", "anon", "Tic tac, perfumada 🌹", dict(dig=0.8)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 4
    dict(parte=4, nome="A rosa", eventos=[
        ("chat", "tati", "20:00", "HOJE"),
        ("msg", "bruna", "Tati, tô sendo chantageada. Cinco mil. A pessoa tem o vídeo da câmera do corredor."),
        ("msg", "tati", "QUÊ?? Quem tem acesso às câmeras do seu prédio?", dict(dig=0.3)),
        ("msg", "bruna", "A síndica, o porteiro... sei lá."),
        ("msg", "tati", "Se fosse a síndica, ela não ia querer dinheiro. Ia querer o seu pescoço."),
        ("msg", "tati", "Presta atenção no jeito que essa pessoa escreve."),
        ("msg", "bruna", "Ele termina tudo com uma rosa. 🌹"),
        ("msg", "tati", "E quem do seu grupo manda rosa?"),
        ("chat", "cond", "20:20", None, (("chip", "ONTEM"), ("osvaldo", "Obrigado, síndica. Boa noite a todos 🌹", "19:30"),
                                         ("chip", "HOJE"))),
        ("msg", "osvaldo", "Boa noite a todos 🌹", dict(pausa=1.4)),
        ("msg", "vera", "Lembrando: amanhã vence o boleto do condomínio."),
        ("chat", "sueli_b", "20:30", "HOJE"),
        ("msg", "bruna", "Sueli, me tira uma dúvida. Quem tem a senha das câmeras do prédio?"),
        ("msg", "sueli", "Oficialmente, é a Vera e o porteiro."),
        ("msg", "sueli", "Mas o Seu Osvaldo foi síndico por vinte anos e nunca devolveu a senha 👀"),
        ("msg", "bruna", "O Seu Osvaldo??"),
        ("msg", "sueli", "E ele tá devendo quinze mil de condomínio. Olha a lista que a Vera colou no elevador:"),
        ("foto", "sueli", inadimplentes, None, dict(pausa=3.2, h_max=640, zoom=True)),
        ("msg", "bruna", "Então ele precisa de dinheiro..."),
        ("msg", "sueli", "Por que a pergunta, vizinha? 👀"),
        ("chat", "anon", "22:00"),
        ("msg", "anon", "O prazo acaba amanhã, perfumada 🌹", dict(dig=0.8)),
        ("msg", "bruna", "Boa noite, Seu Osvaldo."),
        ("digitando", "anon", 2.2),
        ("status", "visto por último hoje às 22:01"),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 5
    dict(parte=5, nome="Assembleia extraordinária", fim_texto="Fim", eventos=[
        ("chat", "vera_b", "22:10", "HOJE"),
        ("msg", "bruna", "Dona Vera, boa noite. É a Bruna, do 74. Eu preciso te contar uma coisa. E vai doer."),
        ("msg", "vera", "Pode falar.", dict(dig=0.4)),
        ("msg", "bruna", "A mensagem do perfume no grupo fui eu que mandei. Era pro seu marido."),
        ("digitando", "vera", 2.0),
        ("msg", "bruna", "E tem alguém me chantageando com o vídeo da câmera. É o Seu Osvaldo."),
        ("audio", "vera", "Eu já desconfiava do Marcelo faz tempo. E o Osvaldo nunca aceitou ter perdido a eleição. "
                          "Amanhã eu resolvo os dois de uma vez."),
        ("chat", "cond", "08:00", "HOJE"),
        ("msg", "vera", "📢 ASSEMBLEIA EXTRAORDINÁRIA hoje, às 19h, no salão de festas."),
        ("msg", "vera", "Primeira pauta: troca da senha das câmeras. Alguém andou usando pra chantagear uma moradora. Né, Seu Osvaldo?"),
        ("msg", "sueli", "EU SABIA QUE ERA ELE 😱", dict(dig=0.3)),
        ("msg", "osvaldo", "Eu só queria salvar o meu apartamento..."),
        ("msg", "vera", "Segunda pauta: a saída do Marcelo. Meu ex-marido. As malas estão na portaria."),
        ("msg", "marcelo", "Vera, a gente pode conversar em casa?"),
        ("msg", "vera", "Que casa?"),
        ("sistema", "Vera Síndica removeu Marcelo 11"),
        ("msg", "osvaldo", "Então não vai ter bolo?"),
        ("chat", "vera_b", "19:40", "HOJE"),
        ("msg", "vera", "Obrigada, Bruna. O Osvaldo vai parcelar a dívida e eu tô livre."),
        ("msg", "vera", "E da próxima vez, confere o grupo antes de mandar 😉"),
        ("chat", "novo", "22:30", "HOJE"),
        ("msg", "novo", "Oi, vizinha 😏", dict(dig=0.6)),
        ("msg", "novo", "Sou o novo morador do 52. Me disseram que a porta do 74 tem fama de ficar destrancada...", dict(dig=0.9)),
        ("rascunho", "Quem te disse isso", 1.2),
        ("pausa", 2.4),
    ]),
]
