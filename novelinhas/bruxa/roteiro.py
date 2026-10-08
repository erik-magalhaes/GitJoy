"""A Quarta: novela sobrenatural (adolescente, estilo Jovens Bruxas) em 5 partes do Compartilhado, no WhatsApp escuro.

A Raíssa (17), expulsa da escola antiga, mora com a Tia Glória desde que a mãe, a Helena, morreu, sete anos atrás. No
primeiro dia na escola nova, a Paula humilha ela e os refletores da quadra estouram. A Íris, a Cami e a Dandara chamam
a Raíssa para "O Círculo". Os feitiços começam de brincadeira e terminam com a Paula no hospital. A tia mostra o diário
da Helena: ela e a Marta (mãe da Íris) eram de um coven que precisava de uma "quarta", e a quarta entrega todo o poder no
ritual da lua cheia. A Helena recusou e morreu. Na lua cheia, a Cami troca as velas, o feitiço volta para a Íris, a
Paula acorda e a Raíssa e a Cami começam um círculo novo. A magia aparece no celular: mensagem que chega antes de a
Raíssa digitar, relógio travado em 00:00, áudio sussurrado, o diário que escreve sozinho.
"""
import functools
import os

from PIL import Image, ImageDraw, ImageEnhance

import zap

FOTOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fotos")
TITULO = "A Quarta"
TEMA = "escuro"
TRILHA = "terror"

THALITA = ("pt-BR-ThalitaMultilingualNeural", "+0%", "+0Hz")
ANTONIO = ("pt-BR-AntonioNeural", "+0%", "+0Hz")
FRANCISCA = ("pt-BR-FranciscaNeural", "+0%", "+0Hz")
VOZES = {"raissa": THALITA, "cami": THALITA, "paula": THALITA, "iris": FRANCISCA, "dandara": FRANCISCA,
         "gloria": FRANCISCA, "nico": ANTONIO}
PRONUNCIA = {r"\bRaíssa\b": "Raíça", r"\bÍris\b": "Íris"}

PERSONAGENS = {
    "raissa": dict(nome="Raíssa", cor=(126, 87, 194)),
    "iris": dict(nome="Íris", cor=(171, 71, 188)),
    "cami": dict(nome="Cami", cor=(240, 98, 146)),
    "dandara": dict(nome="Dandara", cor=(255, 167, 38)),
    "gloria": dict(nome="Tia Glória", cor=(102, 187, 106)),
    "paula": dict(nome="Paula", cor=(239, 83, 80)),
    "nico": dict(nome="Nico", cor=(66, 165, 245)),
}

NOMES_TURMA = {"paula": "Paula", "nico": "Nico", "cami": "Cami"}
NOMES_CIRC = {"iris": "Íris", "cami": "Cami", "dandara": "Dandara"}
CHATS = {
    "turma": dict(dono="raissa", titulo="2ºB 🏫", grupo=True, sub="Paula, Nico, Cami e mais 31", nomes=NOMES_TURMA),
    "tia": dict(dono="raissa", titulo="Tia Glória", com="gloria", sub="online"),
    "numero": dict(dono="raissa", titulo="+55 11 96613-1313", com="iris", sub="online"),
    "circulo": dict(dono="raissa", titulo="O Círculo 🌙", grupo=True, sub="Íris, Cami, Dandara, Você", nomes=NOMES_CIRC),
    "iris": dict(dono="raissa", titulo="Íris 🌙", com="iris", sub="online"),
    "cami": dict(dono="raissa", titulo="Cami", com="cami", sub="online"),
    "novo": dict(dono="raissa", titulo="Círculo Novo 🌒", grupo=True, sub="Cami, Você", nomes={"cami": "Cami"}),
}


def _foto(nome):
    return Image.open(os.path.join(FOTOS, nome)).convert("RGB")


@functools.lru_cache(None)
def vela_nome():
    """As velas, mais escuras, com o nome da Raíssa riscado na cera."""
    im = ImageEnhance.Brightness(_foto("velas_ritual.jpg")).enhance(0.8)
    w = 720
    im = im.resize((w, round(w * im.height / im.width)))
    d = ImageDraw.Draw(im)
    f = zap.fonte("Pacifico-Regular.ttf", 46)
    # o nome riscado na vela grande (texto vertical, cor de cera queimada)
    txt = Image.new("RGBA", (420, 90), (0, 0, 0, 0))
    ImageDraw.Draw(txt).text((10, 10), "Raíssa", font=f, fill=(120, 70, 30, 230))
    txt = txt.rotate(90, expand=True)
    im.paste(txt, (round(w * 0.30), round(im.height * 0.45)), txt)
    return im


def _pagina(linhas, cor_tinta=(40, 30, 90), titulo=None):
    """Página do diário da Helena: papel amarelado, letra à mão."""
    w, h = 820, 170 + 66 * len(linhas) + 40
    im = Image.new("RGBA", (w, h), (238, 226, 196, 255))
    d = ImageDraw.Draw(im)
    for y in range(170, h - 20, 66):
        d.line([(30, y), (w - 30, y)], fill=(205, 190, 160), width=2)
    f = zap.fonte("Pacifico-Regular.ttf", 36)
    y = 170
    if titulo:
        d.text((40, 40), titulo, font=zap.inter(28, 600), fill=(120, 100, 70))
    for ln in linhas:
        zap.texto_rico(im, 40, y - 56, ln, f, cor_tinta)
        y += 66
    return im.convert("RGB")


@functools.lru_cache(None)
def diario():
    return _pagina(["A Marta diz que o círculo só fecha", "com quatro. Na lua cheia, a quarta",
                    "entrega tudo o que tem pras outras.", "Eu sou a quarta. E eu não vou entregar.",
                    "Glória, se acontecer alguma coisa", "comigo, esconde a Raíssa delas.",
                    "O feitiço volta pra quem acende", "a primeira vela. — Helena"], titulo="Diário · 12 de abril")


@functools.lru_cache(None)
def diario_final():
    return _pagina(["Agora você está pronta, filha."], cor_tinta=(120, 40, 140), titulo="Diário · hoje")


EPISODIOS = [
    # ---------------------------------------------------------------------------------------------- 1
    dict(parte=1, nome="A quadra", eventos=[
        ("chat", "tia", "12:40", "SEGUNDA"),
        ("msg", "gloria", "Raíssa, a diretora da escola nova me ligou. Primeiro dia e você já gritou com uma menina na quadra?",
         dict(dig=0.4)),
        ("msg", "raissa", "Ela começou, tia. Me deixa."),
        ("msg", "gloria", "Você já foi expulsa de uma escola. Não tem mais pra onde ir, filha.", dict(dig=0.4)),
        ("msg", "raissa", "Eu não sou sua filha."),
        ("status", "visto por último hoje às 12:42"),
        ("chat", "turma", "13:00", "SEGUNDA"),
        ("msg", "paula", "Gente, a novata surtou na quadra 😂 Gritou comigo do nada", dict(dig=0.3)),
        ("msg", "nico", "E os refletores? Estouraram todos na hora que ela gritou. Que bizarro", dict(dig=0.4)),
        ("foto", "nico", "refletores.jpg", "Sobrou só esse", dict(pausa=0.6)),
        ("msg", "paula", "E a tela do meu celular rachou sozinha no meu bolso 😡 Bruxa!", dict(dig=0.3)),
        ("msg", "cami", "Paula, para. Foi você que jogou a garrafa nela.", dict(dig=0.4)),
        ("chat", "numero", "23:00", "SEGUNDA"),
        ("msg", "iris", "Oi, Raíssa.", dict(dig=0.6)),
        ("msg", "iris", "Você vai perguntar quem eu sou.", dict(dig=0.1)),
        ("msg", "raissa", "Quem é você?"),
        ("msg", "iris", "Viu? 🙂", dict(dig=0.4)),
        ("msg", "iris", "A gente viu o que você fez na quadra hoje. Os refletores. O celular da Paula.", dict(dig=0.4)),
        ("msg", "raissa", "Eu não fiz nada. Foi coincidência."),
        ("msg", "iris", "Não foi. Você sente um formigamento nas mãos quando fica com raiva, né?", dict(dig=0.6)),
        ("rascunho", "Como você sabe disso", 1.4),
        ("msg", "iris", "Você é uma de nós.", dict(dig=0.4)),
        ("foto", "iris", vela_nome, "Essa vela tá acesa pra você desde o dia em que você nasceu.", dict(zoom=True, pausa=0.8, h_max=620)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 2
    dict(parte=2, nome="O círculo", eventos=[
        ("chat", "circulo", "22:30", "TERÇA"),
        ("sistema", "Íris adicionou você"),
        ("msg", "iris", "Bem-vinda, Raíssa. Eu sou a Íris. Essas são a Cami e a Dandara.", dict(dig=0.4)),
        ("msg", "cami", "Oi! Eu sou da sua sala. Fui eu que mandei a Paula parar no grupo 😊", dict(dig=0.3)),
        ("msg", "dandara", "E eu sou a que vai te ensinar a fazer a Paula ficar careca 😂", dict(dig=0.3)),
        ("msg", "raissa", "Isso é sério? Vocês são... bruxas?"),
        ("msg", "iris", "A gente prefere \"círculo\". Hoje à meia-noite, no bosque atrás da escola. Traz sal.", dict(dig=0.4)),
        ("chat", "circulo", "00:00", "QUARTA"),
        ("msg", "dandara", "Tô vendo você chegando com o pacote de sal de cozinha 😂", dict(dig=0.3, hora="00:00")),
        ("msg", "raissa", "Era o que tinha em casa!", dict(hora="00:00")),
        ("audio", "iris", "Três já somos, a quarta chegou. O círculo fecha onde a vela queimou.",
         dict(efeito="fantasma", hora="00:00")),
        ("msg", "cami", "Gente... olhem o relógio do celular", dict(dig=0.4, hora="00:00")),
        ("msg", "raissa", "Tá travado em meia-noite. Faz uns dez minutos.", dict(hora="00:00")),
        ("msg", "iris", "É sempre assim quando o círculo se abre 🌙", dict(dig=0.4, hora="00:00")),
        ("chat", "turma", "08:10", "QUARTA"),
        ("msg", "nico", "Gente, alguém viu a Paula? Ela chegou de boné e não tira de jeito nenhum 😂", dict(dig=0.3)),
        ("msg", "paula", "Não tem graça. O meu cabelo caiu um tufo inteiro no banho 😭", dict(dig=0.3)),
        ("chat", "circulo", "08:12"),
        ("msg", "dandara", "Falei que ia te ensinar 😂😂", dict(dig=0.2)),
        ("msg", "raissa", "Gente, isso é errado... mas foi muito engraçado 😂"),
        ("chat", "tia", "21:00", "QUARTA"),
        ("msg", "gloria", "Raíssa, que sal é esse espalhado no seu tênis? E essas velas no seu quarto?", dict(dig=0.4)),
        ("msg", "raissa", "Não mexe nas minhas coisas, tia."),
        ("msg", "gloria", "Essas meninas. Qual é o sobrenome da tal da Íris?", dict(dig=0.6)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 3
    dict(parte=3, nome="Longe demais", eventos=[
        ("chat", "circulo", "19:00", "SEXTA"),
        ("msg", "iris", "A Paula postou que a Raíssa é bruxa e que vai chamar a polícia. Chega.", dict(dig=0.4)),
        ("msg", "iris", "Hoje a gente faz o feitiço de verdade.", dict(dig=0.6)),
        ("msg", "raissa", "Que feitiço de verdade?"),
        ("msg", "dandara", "O do sono. Ela dorme e só acorda quando a gente quiser 😈", dict(dig=0.3)),
        ("msg", "cami", "Íris, isso é perigoso. A gente combinou que era só brincadeira.", dict(dig=0.4)),
        ("msg", "iris", "Cami, quem manda no círculo?", dict(dig=0.4)),
        ("msg", "cami", "Você.", dict(dig=1.0)),
        ("chat", "turma", "10:30", "SÁBADO"),
        ("msg", "nico", "Gente, a Paula tá no hospital.", dict(dig=0.3)),
        ("msg", "nico", "Ela foi dormir ontem e não acorda. Os médicos não sabem o que é.", dict(dig=0.4)),
        ("chat", "iris", "10:40", "SÁBADO"),
        ("msg", "raissa", "Íris. A Paula tá no hospital."),
        ("msg", "iris", "Eu sei. É só um susto. Ela acorda quando a gente quiser 🙂", dict(dig=0.4)),
        ("msg", "raissa", "Então acorda ela AGORA."),
        ("msg", "iris", "Na lua cheia. Daqui a três dias. Depois do seu ritual de entrada completa.", dict(dig=0.6)),
        ("msg", "raissa", "Que ritual de entrada completa?"),
        ("msg", "iris", "Você vai gostar. Você vai sentir tudo 🌕", dict(dig=0.8)),
        ("chat", "tia", "11:00", "SÁBADO"),
        ("msg", "gloria", "Raíssa. Eu descobri o sobrenome da Íris. É filha da Marta Valente.", dict(dig=0.4)),
        ("msg", "gloria", "A sua mãe também entrou num círculo com dezessete anos. Com a Marta.", dict(dig=0.6)),
        ("msg", "gloria", "Vem pra casa. Agora.", dict(dig=0.4)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 4
    dict(parte=4, nome="A mãe", eventos=[
        ("chat", "tia", "12:00", "SÁBADO"),
        ("foto", "gloria", "livro_antigo.jpg", "Esse é o diário da sua mãe. Eu guardei por sete anos.", dict(pausa=0.8)),
        ("msg", "raissa", "Por que você nunca me mostrou?"),
        ("msg", "gloria", "Porque ela me pediu pra te esconder delas. E eu achei que tinha conseguido.", dict(dig=0.6)),
        ("foto", "gloria", diario, None, dict(zoom=True, pausa=6.0, h_max=700)),
        ("msg", "raissa", "A quarta entrega tudo..."),
        ("audio", "gloria", "A Helena recusou ser a quarta. Duas semanas depois, ela sofreu o acidente. Eu peguei você, mudei de "
                            "cidade e nunca mais falei esse nome. Mas você foi expulsa, mudou de escola... e caiu direto na escola da "
                            "filha da Marta."),
        ("msg", "raissa", "Elas não me chamaram pra fazer parte, tia."),
        ("msg", "raissa", "Elas me chamaram pra ser a oferenda."),
        ("msg", "gloria", "E a lua cheia é na segunda.", dict(dig=0.6)),
        ("chat", "iris", "13:00", "SÁBADO"),
        ("msg", "iris", "Sua tia te mostrou o diário, né? 🙂", dict(dig=0.4)),
        ("msg", "raissa", "Como você sabe?"),
        ("msg", "iris", "A gente esperou sete anos você aparecer, Raíssa. A gente sabe de tudo.", dict(dig=0.6)),
        ("msg", "iris", "E se você não for na segunda, a Paula não acorda nunca mais.", dict(dig=0.6)),
        ("chat", "cami", "13:20", "SÁBADO"),
        ("msg", "cami", "Raíssa... eu não sabia de nada disso. Juro.", dict(dig=0.6)),
        ("msg", "cami", "A Íris disse que a gente só ia te ensinar. Eu tô com medo dela também.", dict(dig=0.6)),
        ("msg", "raissa", "Você me ajuda?"),
        ("msg", "cami", "Ajudo. O que eu faço?", dict(dig=0.4)),
        ("msg", "raissa", "\"O feitiço volta pra quem acende a primeira vela.\" Na segunda, você troca as velas."),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 5
    dict(parte=5, nome="Lua cheia", fim_texto="Fim", eventos=[
        ("chat", "circulo", "23:50", "SEGUNDA"),
        ("foto", "iris", "lua_cheia.jpg", "Ela chegou 🌕", dict(pausa=0.6)),
        ("msg", "iris", "Raíssa, no centro do círculo. Cami, as velas.", dict(dig=0.3)),
        ("msg", "cami", "Velas no lugar 🕯️", dict(dig=0.4)),
        ("msg", "dandara", "Íris, acende a primeira. Como sempre.", dict(dig=0.3)),
        ("chat", "circulo", "00:00", "TERÇA"),
        ("audio", "iris", "Quarta irmã, filha de Helena, entrega o que é teu pra quem acende a chama.",
         dict(efeito="fantasma", hora="00:00")),
        ("msg", "dandara", "Íris???", dict(dig=0.2, hora="00:00")),
        ("msg", "dandara", "O fogo virou pro seu lado!", dict(dig=0.2, hora="00:00")),
        ("msg", "iris", "o que vc fez cami", dict(dig=0.2, hora="00:00")),
        ("msg", "cami", "Troquei as velas. A primeira que você acendeu era a da Raíssa.", dict(dig=0.4, hora="00:00")),
        ("msg", "iris", "eu nao sinto mais nada", dict(dig=0.4, hora="00:00")),
        ("msg", "iris", "minhas maos tao frias", dict(dig=0.4, hora="00:00")),
        ("msg", "raissa", "O feitiço voltou pra quem acendeu, Íris. Igual com a minha mãe. Só que dessa vez ao contrário.",
         dict(hora="00:01")),
        ("sistema", "Íris saiu"),
        ("chat", "turma", "07:30", "TERÇA"),
        ("msg", "nico", "GENTE, A PAULA ACORDOU!! 🙏", dict(dig=0.2)),
        ("msg", "paula", "Acordei. E Raíssa... desculpa pela garrafa. De verdade.", dict(dig=0.8)),
        ("chat", "tia", "08:00", "TERÇA"),
        ("msg", "raissa", "Tia. Acabou. A Paula acordou e a Íris não tem mais nada."),
        ("msg", "gloria", "A sua mãe teria tanto orgulho de você 💚", dict(dig=0.6)),
        ("msg", "raissa", "Obrigada por me esconder esse tempo todo. E desculpa por tudo que eu te falei."),
        ("msg", "gloria", "Volta cedo hoje. Eu faço aquele bolo de fubá 💚", dict(dig=0.4)),
        ("chat", "novo", "22:00", "TERÇA"),
        ("sistema", "Você criou o grupo \"Círculo Novo 🌒\""),
        ("msg", "cami", "Só nós duas? 🥹", dict(dig=0.3)),
        ("msg", "raissa", "Por enquanto. E aqui ninguém é oferenda de ninguém."),
        ("foto", "raissa", diario_final, "Cami... o diário da minha mãe escreveu sozinho.", dict(zoom=True, pausa=1.0, h_max=420)),
        ("pausa", 2.4),
    ]),
]
