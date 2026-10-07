"""Amigo Secreto: novela em 5 partes do Compartilhado.

No amigo secreto da agência Pulso, um número "🎅" entra no grupo e começa a revelar os segredos de cada um,
sempre às 17:59. A Larissa desconfia da Kátia (RH), mas o Papai Noel é a Bianca, a estagiária que ninguém
lembra o nome: o Fernando (gerente) apresentou como dele a campanha que ela criou.
"""
import functools

from PIL import Image, ImageDraw

import zap

TITULO = "Amigo Secreto"

THALITA = ("pt-BR-ThalitaMultilingualNeural", "+0%", "+0Hz")
ANTONIO = ("pt-BR-AntonioNeural", "+0%", "+0Hz")
# o 🎅 fala com voz de homem (disfarce); quando a Bianca se revela, a voz dela é a de mulher
VOZES = {"larissa": THALITA, "katia": THALITA, "bianca": THALITA,
         "fernando": ANTONIO, "rodrigo": ANTONIO, "paulo": ANTONIO, "noel": ANTONIO}

PERSONAGENS = {
    "larissa": dict(nome="Lari", cor=(0, 137, 123)),
    "katia": dict(nome="Kátia", cor=(194, 24, 91)),
    "fernando": dict(nome="Fernando", cor=(69, 90, 100)),
    "rodrigo": dict(nome="Rodrigo", cor=(245, 124, 0)),
    "bianca": dict(nome="Bianca", cor=(123, 31, 162)),
    "paulo": dict(nome="Paulo", cor=(21, 101, 192)),
    "noel": dict(nome="Noel", cor=(198, 40, 40)),
}

NUM_NOEL = "+55 11 95501-1212"
CHATS = {
    "grupo": dict(dono="larissa", titulo="Pulso 💼 Amigo Secreto 🎁", grupo=True,
                  sub="Kátia RH, Fernando, Rodrigo, Bianca Estágio, Paulo Diretor, Você",
                  nomes={"katia": "Kátia RH", "bianca": "Bianca Estágio", "paulo": "Paulo Diretor", "noel": NUM_NOEL + " 🎅"}),
    "rodrigo": dict(dono="larissa", titulo="Rodrigo 😂", com="rodrigo", sub="online"),
    "katia": dict(dono="larissa", titulo="Kátia RH", com="katia", sub="online"),
    "noel": dict(dono="larissa", titulo=NUM_NOEL, com="noel", sub="online"),
}


# ------------------------------------------------------------------ imagens
@functools.lru_cache(None)
def sorteio():
    w, h = 760, 560
    im = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, 150), fill=(198, 40, 40))
    zap.texto_rico(im, 40, 40, "🎁 Amigo Secreto Pulso", zap.inter(52, 900), (255, 255, 255))
    d.text((40, 200), "Sorteio realizado!", font=zap.inter(44, 800), fill=(30, 30, 30))
    d.text((40, 270), "15 participantes · valor: R$ 80", font=zap.inter(34, 450), fill=(90, 90, 90))
    d.text((40, 330), "Confraternização: sexta, dia 20, 19h", font=zap.inter(34, 450), fill=(90, 90, 90))
    d.rounded_rectangle((40, 420, w - 40, 510), 18, fill=(255, 235, 238))
    zap.texto_rico(im, 70, 440, "🤫 Cada um já recebeu o seu no app", zap.inter(34, 700), (198, 40, 40))
    return im.convert("RGB")


def _slide(autor, data, cor):
    w, h = 520, 360
    im = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, h), fill=(255, 248, 225))
    d.rectangle((0, 0, w, 70), fill=(255, 160, 0))
    zap.texto_rico(im, 24, 14, "☀️ Campanha de Verão", zap.inter(34, 900), (255, 255, 255))
    d.text((24, 100), "Conceito: \"O verão é seu\"", font=zap.inter(26, 700), fill=(40, 40, 40))
    for i, t in enumerate(("• Influencers de bairro", "• Cupom na praia", "• Vídeo com os clientes")):
        d.text((24, 145 + i * 38), t, font=zap.inter(24, 450), fill=(60, 60, 60))
    d.rounded_rectangle((16, 280, w - 16, 344), 10, fill=cor)
    d.text((30, 290), autor, font=zap.inter(24, 800), fill=(255, 255, 255))
    d.text((30, 318), data, font=zap.inter(20, 500), fill=(255, 255, 255))
    return im


@functools.lru_cache(None)
def slides():
    """O arquivo da Bianca (antes) e a apresentação do Fernando (depois): o mesmo slide."""
    w, h = 1120, 520
    im = Image.new("RGBA", (w, h), (236, 239, 241, 255))
    d = ImageDraw.Draw(im)
    im.alpha_composite(_slide("Bianca Lima (estágio)", "arquivo criado em 03/10", (123, 31, 162)), (24, 110))
    im.alpha_composite(_slide("Fernando Alves (gerente)", "apresentado em 17/10", (69, 90, 100)), (576, 110))
    d.text((24 + 260, 60), "ORIGINAL", font=zap.inter(36, 900), fill=(123, 31, 162), anchor="mm")
    d.text((576 + 260, 60), "APRESENTADO", font=zap.inter(36, 900), fill=(69, 90, 100), anchor="mm")
    return im.convert("RGB")


# ------------------------------------------------------------------ episódios
EPISODIOS = [
    # ---------------------------------------------------------------------------------------------- 1
    dict(parte=1, nome="O sorteio", eventos=[
        ("chat", "grupo", "10:00", "HOJE"),
        ("msg", "katia", "Bom dia, Pulso! 🎁 Amigo secreto da firma: valor de oitenta reais. Confraternização sexta, dia 20!"),
        ("foto", "katia", sorteio, "Sorteio feito pelo app! Ninguém conta quem tirou, hein 🤫", dict(zoom=True, pausa=0.6, h_max=520)),
        ("msg", "rodrigo", "Se eu tirar o Fernando, vou dar um despertador ⏰"),
        ("msg", "fernando", "Rodrigo, foco no relatório."),
        ("msg", "bianca", "Oi gente, sou a Bianca, do estágio. Tô participando também 😊", dict(dig=0.6)),
        ("pausa", 0.6),
        ("hora", "17:59"),
        ("sistema", NUM_NOEL + " entrou usando o link do grupo"),
        ("msg", "noel", "Ho ho ho 🎅 Boa tarde, Pulso!", dict(dig=0.8, hora="17:59")),
        ("msg", "noel", "Primeira dica do amigo secreto: tem gente aqui que passa a tarde no Tinder em vez de trabalhar 👀 Né, Rodrigo?",
         dict(hora="17:59")),
        ("msg", "rodrigo", "QUE ISSO?? Quem é esse número??", dict(dig=0.3, hora="18:00")),
        ("msg", "katia", "Gente, quem passou o link do grupo pra esse número?", dict(hora="18:00")),
        ("msg", "noel", "Amanhã tem mais 🎅", dict(hora="18:00")),
        ("chat", "rodrigo", "18:05", "HOJE"),
        ("msg", "rodrigo", "Lari. Foi você?"),
        ("msg", "larissa", "Eu?? Eu nem sabia do Tinder, Rodrigo!"),
        ("msg", "rodrigo", "Ninguém sabia! Só quem viu a minha tela."),
        ("msg", "larissa", "E quem senta do seu lado?"),
        ("msg", "rodrigo", "Você. A estagiária. E a impressora."),
        ("msg", "larissa", "Então foi a impressora 😂"),
        ("msg", "rodrigo", "Não tem graça, Lari. Amanhã pode ser você.", dict(dig=0.8)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 2
    dict(parte=2, nome="Ho ho ho", eventos=[
        ("chat", "grupo", "17:59", "HOJE", (("chip", "ONTEM"), ("noel", "Amanhã tem mais 🎅", "18:00"))),
        ("msg", "noel", "Ho ho ho 🎅 Dica de hoje:", dict(dig=0.8)),
        ("msg", "noel", "O atestado do Fernando na sexta passada? Ele tava no estádio. Tem foto no story da cunhada 📸"),
        ("msg", "fernando", "Isso é mentira! Kátia, tira esse número AGORA.", dict(dig=0.3)),
        ("msg", "katia", "Tô tentando, Fernando! Só o Paulo é administrador."),
        ("msg", "fernando", "Eu vou descobrir quem tá por trás disso. E vai ter processo."),
        ("msg", "paulo", "Fernando, amanhã cedo, na minha sala."),
        ("msg", "rodrigo", "eita 😳", dict(dig=0.3, ler=False, pausa=0.8)),
        ("msg", "noel", "E essa foi só a segunda dica. Faltam três dias pra confraternização 🎁"),
        ("chat", "katia", "18:20", "HOJE"),
        ("msg", "larissa", "Kátia, dá pra descobrir de quem é esse número?"),
        ("msg", "katia", "Não dá. Mas Lari... ele sabe de coisa que só o RH sabe."),
        ("msg", "katia", "O atestado do Fernando tava na minha mesa."),
        ("msg", "larissa", "Então alguém mexe na sua mesa."),
        ("msg", "katia", "Ou alguém vai achar que fui eu 😟"),
        ("msg", "larissa", "Quem mais entra na sua sala?"),
        ("msg", "katia", "Todo mundo, Lari. Até a estagiária vai lá buscar papel pra impressora."),
        ("msg", "larissa", "Vou ficar de olho."),
        ("chat", "noel", "21:30"),
        ("msg", "noel", "Boa noite, Lari 🎅", dict(dig=0.8)),
        ("msg", "noel", "Você é a próxima.", dict(dig=1.0)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 3
    dict(parte=3, nome="A próxima", eventos=[
        ("chat", "noel", "21:31", None, (("chip", "HOJE"), ("noel", "Boa noite, Lari 🎅", "21:30"), ("noel", "Você é a próxima.", "21:30"))),
        ("msg", "larissa", "Quem é você?"),
        ("msg", "noel", "O seu amigo secreto 🎅", dict(dig=0.8)),
        ("msg", "larissa", "Para com isso. Você tá destruindo as pessoas."),
        ("msg", "noel", "Eu só conto verdades. Amanhã eu conto a sua."),
        ("chat", "grupo", "17:59", "HOJE"),
        ("msg", "noel", "Ho ho ho 🎅 Dica de hoje:", dict(dig=0.8)),
        ("msg", "noel", "A Larissa tá fazendo entrevista em outra agência. Terça, no horário do almoço. Boa sorte, Lari! 🍀"),
        ("msg", "fernando", "Larissa. Isso é verdade?", dict(dig=0.4)),
        ("msg", "rodrigo", "Lari?? 😳", dict(dig=0.3)),
        ("msg", "paulo", "Larissa, quero falar com você amanhã cedo."),
        ("chat", "rodrigo", "18:10", "HOJE"),
        ("msg", "rodrigo", "Lari, eu não sabia da entrevista. Juro."),
        ("msg", "larissa", "O Paulo vai me chamar amanhã. Eu vou perder o emprego antes de conseguir outro 😭"),
        ("msg", "rodrigo", "Calma. A gente vai descobrir quem é."),
        ("msg", "larissa", "Ninguém sabia. Só a Kátia, porque eu pedi uma carta de referência pro RH."),
        ("msg", "rodrigo", "A KÁTIA??", dict(dig=0.3)),
        ("msg", "larissa", "O atestado tava na mesa dela. A minha carta também."),
        ("msg", "larissa", "É ela, Rodrigo. A Kátia é o Papai Noel."),
        ("msg", "rodrigo", "E o que você vai fazer?"),
        ("msg", "larissa", "Amanhã eu provo."),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 4
    dict(parte=4, nome="Às 17:59", eventos=[
        ("chat", "katia", "09:00", "HOJE"),
        ("msg", "larissa", "Kátia, só você sabia da minha entrevista."),
        ("msg", "katia", "Lari, eu juro que não fui eu!", dict(dig=0.4)),
        ("msg", "katia", "Eu sou a mais prejudicada aqui! O Paulo acha que o vazamento é do RH."),
        ("msg", "larissa", "Então me explica como o Papai Noel sabia."),
        ("msg", "katia", "A minha mesa fica do lado da copa. Todo mundo passa por ali."),
        ("msg", "katia", "E a senha do meu computador tá num post-it. Qualquer um vê."),
        ("chat", "rodrigo", "12:30", "HOJE"),
        ("msg", "larissa", "Rodrigo, repara numa coisa. Todas as mensagens do Papai Noel chegam às 17:59."),
        ("msg", "rodrigo", "E daí?"),
        ("msg", "larissa", "A Kátia sai às seis e meia. Você e o Fernando saem às sete. Quem sai às seis em ponto?"),
        ("digitando", "rodrigo", 1.6),
        ("msg", "rodrigo", "Os estagiários.", dict(dig=0.3)),
        ("msg", "larissa", "E quem fica na copa o dia inteiro, ouvindo tudo, sem ninguém reparar?"),
        ("digitando", "rodrigo", 1.8),
        ("msg", "rodrigo", "A Bianca.", dict(dig=0.3)),
        ("msg", "larissa", "Você sabe o sobrenome dela?"),
        ("msg", "rodrigo", "Não..."),
        ("msg", "larissa", "Ninguém sabe. Esse é o ponto."),
        ("chat", "noel", "17:59", "HOJE"),
        ("msg", "larissa", "Boa tarde, Bianca."),
        ("digitando", "noel", 2.6),
        ("msg", "noel", "Amanhã, antes da confraternização. Eu te explico tudo.", dict(dig=0.4)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 5
    dict(parte=5, nome="A confraternização", fim_texto="Fim", eventos=[
        ("chat", "noel", "08:30", "HOJE"),
        ("msg", "bianca", "Oi, Lari. Sou eu. A Bianca.", dict(dig=0.8)),
        ("msg", "bianca", "Lembra da Campanha de Verão que o Fernando apresentou pro Paulo e ganhou bônus?"),
        ("foto", "bianca", slides, "Fui eu que fiz. Esse é o meu arquivo, duas semanas antes.", dict(zoom=True, pausa=1.0, h_max=420, w=700)),
        ("msg", "bianca", "Eu reclamei com ele. Ele disse que estagiário não tem ideia, tem tarefa."),
        ("msg", "larissa", "E por isso você expôs todo mundo?"),
        ("audio", "bianca", "Eu sei que eu errei, Lari. Ninguém aqui sabe nem o meu nome. "
                            "Você sempre foi a única que me dava bom dia."),
        ("msg", "larissa", "Me manda esses arquivos. Eu vou te ajudar. Do jeito certo."),
        ("chat", "grupo", "19:00", "HOJE"),
        ("msg", "larissa", "Pessoal, antes da troca de presentes: a Campanha de Verão que o Fernando apresentou foi criada pela Bianca. Os arquivos com data estão aqui."),
        ("foto", "larissa", slides, None, dict(zoom=True, pausa=1.8, h_max=420, w=700)),
        ("msg", "paulo", "Fernando. Na minha sala. Agora."),
        ("msg", "bianca", "E o Papai Noel era eu. Me desculpem."),
        ("msg", "paulo", "Bianca, você vai responder pelas mensagens. Mas a campanha é sua, e isso vai ficar registrado."),
        ("sistema", "Paulo Diretor removeu Fernando"),
        ("sistema", "Paulo Diretor removeu " + NUM_NOEL),
        ("msg", "rodrigo", "E o meu presente de amigo secreto, como fica? 😂"),
        ("chat", "noel", "22:00", "HOJE"),
        ("msg", "bianca", "Obrigada, Lari. Ah... eu tirei você no amigo secreto 🎁"),
        ("msg", "larissa", "Sério? E qual é o presente?"),
        ("msg", "bianca", "Pedi pro Paulo assinar a sua carta de referência. Boa sorte na entrevista 😉"),
        ("pausa", 2.4),
    ]),
]
