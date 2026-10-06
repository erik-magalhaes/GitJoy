"""A Sogra Tem a Chave: novela em 5 partes do Print Vazado.

Eventos (lidos por novela.py):
  ("gancho", titulo_notif, texto_notif, hora, fala_do_narrador)
  ("titulo",)
  ("narr", texto)
  ("chat", id, hora, chip=None, historico=())
  ("msg", quem, texto, {opções})      opções: dig, ler, pausa, enc
  ("audio", quem, texto, {opções})    opções: voz, enc, tocar, transcricao
  ("foto", quem, imagem, legenda, {opções})
  ("digitando", quem, segundos) / ("apagar", quem) / ("status", texto) / ("sistema", texto) / ("pausa", s)
  ("fim", linha1, linha2, pergunta)
"""
import functools
import os

from PIL import Image, ImageDraw, ImageFilter

import zap

FOTOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fotos")

TITULO = "A Sogra Tem a Chave"
CHAMADA = "Segue e manda pra quem tem sogra 👀"

PERSONAGENS = {
    "camila": dict(nome="Camila", cor=(216, 27, 96)),
    "neide": dict(nome="Dona Neide", cor=(142, 36, 170)),
    "rafael": dict(nome="Rafa", cor=(6, 147, 227)),
    "bia": dict(nome="Bia", cor=(245, 124, 0)),
    "rosana": dict(nome="Tia Rosana", cor=(0, 137, 123)),
    "diego": dict(nome="Diego", cor=(57, 73, 171)),
    "lucas": dict(nome="Lucas", cor=(0, 150, 136)),
    "jessica": dict(nome="Jéssica", cor=(194, 24, 91)),
    "narrador": dict(nome="Narrador", cor=(0, 0, 0)),
}

MEMBROS = "Dona Neide, Tia Rosana, Diego, Rafa, Você"
CHATS = {
    "neide": dict(dono="camila", titulo="Dona Neide 🌻", com="neide", sub="online"),
    "bia": dict(dono="camila", titulo="Bia 💅", com="bia", sub="online"),
    "familia": dict(dono="camila", titulo="Família Souza 🙏", grupo=True, sub=MEMBROS),
    "familia_r": dict(dono="rafael", titulo="Família Souza 🙏", grupo=True,
                      sub="Mãe, Tia Rosana, Diego, Camila, Você", nomes={"neide": "Mãe"}),
    "rafa": dict(dono="camila", titulo="Amor ❤️", com="rafael", sub="online"),
    "mae": dict(dono="rafael", titulo="Mãe", com="neide", sub="online"),
    "lucas": dict(dono="camila", titulo="Lucas Festas 🎉", com="lucas", sub="online"),
    "rosana": dict(dono="neide", titulo="Rosana irmã 🙏", com="rosana", sub="online"),
    "jessica": dict(dono="camila", titulo="+55 11 98472-3310", com="jessica", sub="online"),
}


# ------------------------------------------------------------------ imagens que aparecem nas conversas
@functools.lru_cache(None)
def print_lucas():
    """O print que a sogra tira da conversa da Camila com o Lucas."""
    im = zap.papel_parede().copy().convert("RGBA")
    zap.barra_status(im, "09:27")
    zap.cabecalho(im, "Lucas 💙", "online", PERSONAGENS["lucas"]["cor"])
    y = zap.CHAT_Y0 + 24
    for quem, txt, hora in (("lucas", "Nosso segredo, hein? Ele NÃO pode saber 🤫", "09:12"),
                            ("camila", "Pode deixar. Sábado que vem, 20h. Mal posso esperar ❤️", "09:14")):
        saida = quem == "camila"
        b, pad = zap.balao_texto(txt, hora, saida, True)
        x = zap.DIR - (b.width - pad) if saida else zap.ESQ - pad
        im.alpha_composite(b, (x, y - pad))
        y += b.height - 2 * pad + 20
    return im.crop((0, zap.STATUS_Y, zap.W, y + 30)).convert("RGB")


@functools.lru_cache(None)
def orcamento():
    """Orçamento da festa surpresa (papel timbrado do Lucas)."""
    w, h = 900, 1020
    im = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, 150), fill=(0, 150, 136))
    zap.texto_rico(im, 50, 36, "LUCAS FESTAS 🎉", zap.inter(64, 900), (255, 255, 255))
    d.text((50, 210), "ORÇAMENTO Nº 0347", font=zap.inter(34, 700), fill=(120, 120, 120))
    d.text((50, 280), "Festa surpresa: 35 anos do Rafael", font=zap.inter(44, 800), fill=(20, 20, 20))
    linhas = ["Sábado · 20h · Salão Villa Jardim", "80 convidados", "Bolo de 3 andares", "DJ + decoração",
              "Contratante: Camila Souza"]
    for i, l in enumerate(linhas):
        d.text((70, 370 + i * 64), "•  " + l, font=zap.inter(38, 450), fill=(40, 40, 40))
    d.line([(50, 715), (w - 50, 715)], fill=(220, 220, 220), width=3)
    d.text((50, 740), "TOTAL", font=zap.inter(40, 700), fill=(20, 20, 20))
    d.text((w - 50, 740), "R$ 4.850,00", font=zap.inter(40, 800), fill=(20, 20, 20), anchor="ra")
    d.rounded_rectangle((50, 840, w - 50, 960), 18, fill=(255, 235, 238))
    zap.texto_rico(im, 80, 868, "🤫 SURPRESA: não contar pro aniversariante!", zap.inter(36, 750), (198, 40, 40))
    return im.convert("RGB")


@functools.lru_cache(None)
def story_jessica():
    """Print do story da ex (foto de brinde + textos do Instagram)."""
    w, h = 720, 1280
    ft = Image.open(os.path.join(FOTOS, "brinde.jpg")).convert("RGB")
    fundo = ft.resize((round(ft.width * h / ft.height), h), Image.LANCZOS)
    x0 = (fundo.width - w) // 2 + 120
    fundo = fundo.crop((x0, 0, x0 + w, h)).filter(ImageFilter.GaussianBlur(28))
    im = fundo.convert("RGBA")
    im.alpha_composite(Image.new("RGBA", (w, h), (0, 0, 0, 70)))
    meio = ft.resize((w, round(ft.height * w / ft.width)), Image.LANCZOS)
    im.paste(meio, (0, (h - meio.height) // 2 - 40))
    d = ImageDraw.Draw(im)
    for i in range(3):  # barrinhas do story
        x = 16 + i * (w - 32) / 3
        d.rounded_rectangle((x + 3, 20, x + (w - 32) / 3 - 3, 26), 3,
                            fill=(255, 255, 255, 255 if i < 2 else 110))
    av = zap.avatar("Jéssica", PERSONAGENS["jessica"]["cor"], 64)
    im.paste(av, (20, 44), av)
    d.text((98, 86), "jessica.mendes", font=zap.inter(30, 700), fill=(255, 255, 255), anchor="ls")
    d.text((340, 86), "2 h", font=zap.inter(28, 450), fill=(230, 230, 230), anchor="ls")
    for txt, y, tam in (("Sábado tem reencontro 🥂", 190, 46), ("obrigada pelo convite,", 1010, 38),
                        ("@dona.neide ❤️", 1066, 40)):
        f = zap.inter(tam, 800)
        tw = zap.larg_linha(zap.tokens(txt), f)
        d.rounded_rectangle(((w - tw) / 2 - 18, y - 10, (w + tw) / 2 + 18, y + tam + 16), 12, fill=(255, 255, 255))
        zap.desenha_linha(im, (w - tw) / 2, y + tam, zap.tokens(txt), f, (20, 20, 20))
    return im.convert("RGB")


# ------------------------------------------------------------------ episódios
EPISODIOS = [
    # ---------------------------------------------------------------------------------------------- 1
    dict(parte=1, nome="Bom dia, nora", dia="sábado, 14 de outubro", eventos=[
        ("gancho", "Mãe", "Filho, achei uma coisa no celular da sua mulher.", "09:31",
         "Essa mensagem chegou pro marido às nove da manhã. Mas tudo começou bem antes."),
        ("titulo",),
        ("chat", "neide", "06:12", "HOJE", (("chip", "ONTEM"),
                                            ("neide", "Rafa disse que o almoço de domingo é aí né", "21:40"),
                                            ("camila", "Isso, Dona Neide! Vou fazer frango com arroz 😊", "21:52"))),
        ("msg", "neide", "Bom dia nora 🌻🙏"),
        ("audio", "neide", "Camila, bom dia! O arroz de domingo tava empapado, viu? O Rafa gosta soltinho. Depois eu te ensino. Beijo!"),
        ("msg", "camila", "Bom dia, Dona Neide... são seis da manhã 😅"),
        ("narr", "A Camila nem respondeu. Foi na padaria... e quando voltou, a porta estava destrancada."),
        ("chat", "bia", "08:40", "HOJE"),
        ("msg", "camila", "BIA. Ela entrou aqui de novo."),
        ("msg", "bia", "QUEM?? A sogra??", dict(dig=0.4)),
        ("msg", "camila", "Com a chave que o Rafa deu \"só pra emergência\" 🙃"),
        ("msg", "bia", "E qual foi a emergência?"),
        ("msg", "camila", "A louça."),
        ("msg", "bia", "KKKKKKKK mentira", dict(dig=0.3, ler=False, pausa=0.7)),
        ("narr", "Mas a Dona Neide não ficou só na louça."),
        ("chat", "familia", "09:05", "HOJE"),
        ("foto", "neide", "pia.jpg", "Olha como o meu filho está vivendo 😢"),
        ("msg", "rosana", "Meu Deus do céu 😱", dict(dig=0.3)),
        ("msg", "diego", "kkkkkkkkkkk", dict(dig=0.3, ler=False, pausa=0.6)),
        ("msg", "camila", "Dona Neide, a senhora entrou na minha casa sem avisar e postou foto da minha pia no grupo??"),
        ("msg", "neide", "Só quis ajudar, minha filha. Não precisa ser grossa 🙏"),
        ("msg", "rosana", "Respeita a sua sogra, Camila."),
        ("narr", "A Camila largou o celular desbloqueado na mesa e foi pro banho. A sogra ainda estava lá."),
        ("chat", "mae", "09:31", "HOJE", (("chip", "ONTEM"), ("neide", "Filho, levou o casaco?", "18:02"),
                                          ("rafael", "Levei mãe", "18:30"))),
        ("msg", "neide", "Filho", dict(dig=0.4)),
        ("msg", "neide", "Você tá sentado?", dict(dig=0.5)),
        ("msg", "neide", "Achei uma coisa no celular da sua mulher.", dict(dig=0.9)),
        ("msg", "rafael", "Que coisa, mãe?"),
        ("digitando", "neide", 2.2),
        ("status", "online"),
        ("pausa", 0.4),
        ("fim", "CONTINUA…", "Parte 2: Quem é Lucas?", "Comenta aí: você daria a chave da sua casa pra sua sogra? 🔑"),
    ]),
    # ---------------------------------------------------------------------------------------------- 2
    dict(parte=2, nome="Quem é Lucas?", dia="sábado, 14 de outubro", eventos=[
        ("gancho", "Amor ❤️", "Camila. Quem é Lucas?", "09:55",
         "Três palavras... e um casamento por um fio."),
        ("titulo",),
        ("narr", "No capítulo anterior: a sogra entrou sem avisar... e mexeu no celular da nora."),
        ("chat", "mae", "09:33", None, (("chip", "HOJE"), ("neide", "Filho", "09:30"), ("neide", "Você tá sentado?", "09:30"),
                                          ("neide", "Achei uma coisa no celular da sua mulher.", "09:31"),
                                          ("rafael", "Que coisa, mãe?", "09:31"))),
        ("foto", "neide", print_lucas, None, dict(pausa=3.2, h_max=640, w=700, zoom=True)),
        ("msg", "neide", "Tirei print. Quem é esse Lucas, filho?"),
        ("msg", "rafael", "Mãe, a senhora mexeu no celular dela??"),
        ("msg", "neide", "Tava desbloqueado em cima da mesa. Deus quis que eu visse 🙏"),
        ("narr", "E se você acha que a Dona Neide guardou isso só pro filho..."),
        ("chat", "familia_r", "09:40", "HOJE"),
        ("msg", "neide", "Gente, orem pelo casamento do meu filho 🙏😢"),
        ("msg", "rosana", "O que aconteceu, Neide???", dict(dig=0.3)),
        ("msg", "neide", "Não posso falar aqui. Mas tem um tal de LUCAS."),
        ("msg", "diego", "eita 👀🍿", dict(dig=0.3, ler=False, pausa=0.6)),
        ("msg", "rosana", "Eu sempre falei. Nunca gostei dessa menina."),
        ("narr", "A Camila saiu do banho com quarenta e sete mensagens não lidas."),
        ("chat", "bia", "09:52", "HOJE"),
        ("msg", "camila", "Bia, minha sogra mexeu no meu celular. Ela viu as mensagens do Lucas."),
        ("msg", "bia", "NÃO. Ela vai estragar TUDO.", dict(dig=0.4)),
        ("msg", "camila", "Eu não posso contar pro Rafa. Não agora."),
        ("msg", "bia", "Amiga, se você não contar, ela vai contar a versão dela."),
        ("narr", "Foi aí que chegou a mensagem que ela mais temia."),
        ("chat", "rafa", "09:55", "HOJE", (("chip", "ONTEM"), ("rafael", "Te amo, boa noite ❤️", "23:10"),
                                           ("camila", "Te amo mais 😘", "23:11"))),
        ("msg", "rafael", "Camila.", dict(dig=0.5)),
        ("msg", "rafael", "Quem é Lucas?", dict(dig=0.8)),
        ("digitando", "rafael", 1.8),
        ("pausa", 0.5),
        ("digitando", "rafael", 1.2),
        ("status", "visto por último hoje às 09:56"),
        ("narr", "Ele parou de digitar... e ficou offline."),
        ("fim", "CONTINUA…", "Parte 3: A surpresa", "Comenta aí: você acha que a Camila tá traindo? 👀"),
    ]),
    # ---------------------------------------------------------------------------------------------- 3
    dict(parte=3, nome="A surpresa", dia="sábado, 14 de outubro", eventos=[
        ("gancho", "Rosana irmã 🙏", "Neide: Essa festa vai ser o fim desse casamento.", "22:47",
         "A verdade apareceu... mas a sogra já tinha outro plano."),
        ("titulo",),
        ("narr", "No capítulo anterior: a sogra espalhou pra família que a nora tinha um tal de Lucas."),
        ("chat", "rafa", "10:02", None, (("chip", "HOJE"), ("rafael", "Camila.", "09:55"), ("rafael", "Quem é Lucas?", "09:55"))),
        ("msg", "camila", "Amor, me liga. Não é nada do que a sua mãe tá falando."),
        ("foto", "camila", orcamento, None, dict(pausa=3.0, h_max=680, zoom=True)),
        ("msg", "camila", "O Lucas é o organizador de festas. É o seu aniversário surpresa de 35 anos!"),
        ("digitando", "rafael", 1.4),
        ("msg", "rafael", "Meu Deus, Camila. Me desculpa.", dict(dig=0.3)),
        ("narr", "A surpresa acabou. Mas a Camila foi tirar satisfação."),
        ("chat", "neide", "10:15", "HOJE", (("chip", "HOJE"), ("neide", "Quem cedo madruga Deus ajuda 🙏", "06:14"))),
        ("msg", "camila", "Dona Neide, o Lucas é o organizador da festa surpresa do Rafa. A senhora estragou a surpresa que eu preparava há três meses."),
        ("msg", "neide", "E como eu ia saber? Mensagem escondida é coisa de quem deve."),
        ("msg", "camila", "A senhora mexeu no meu celular!"),
        ("audio", "neide", "Camila, a minha pressão subiu, viu? Tô aqui deitada, passando mal. Mas tudo bem. Eu sou a vilã, né? Sempre sou."),
        ("narr", "Naquela noite, a Dona Neide mandou uma mensagem pra irmã."),
        ("chat", "rosana", "22:47", "HOJE"),
        ("msg", "neide", "Rosana. A festa do Rafa é sábado que vem."),
        ("msg", "neide", "E eu vou levar uma convidada especial."),
        ("msg", "rosana", "Quem??", dict(dig=0.3)),
        ("msg", "neide", "Essa festa vai ser o fim desse casamento."),
        ("msg", "rosana", "Neide... o que você vai fazer?"),
        ("apagar", "neide"),
        ("digitando", "neide", 1.4),
        ("fim", "CONTINUA…", "Parte 4: Sabotagem", "Comenta aí: quem você acha que é a convidada especial? 🤔"),
    ]),
    # ---------------------------------------------------------------------------------------------- 4
    dict(parte=4, nome="Sabotagem", dia="sexta-feira, 20 de outubro", eventos=[
        ("gancho", "+55 11 98472-3310", "Sua sogra me mandou um áudio... você PRECISA ouvir isso.", "16:20",
         "A ex do marido... mandando mensagem pra esposa. Na véspera da festa."),
        ("titulo",),
        ("narr", "No capítulo anterior: a sogra prometeu que a festa seria o fim do casamento."),
        ("chat", "lucas", "14:10", "HOJE", (("chip", "QUARTA"), ("camila", "Tudo certo pro sábado, Lucas? 🙏", "11:20"),
                                            ("lucas", "Tudo certinho! Bolo, DJ e decoração ✅", "11:31"))),
        ("msg", "lucas", "Camila, tudo bem? Uma dúvida: por que você cancelou o bolo?"),
        ("msg", "camila", "Eu não cancelei nada!"),
        ("msg", "lucas", "Uma senhora ligou aqui ontem. Disse que era a sogra e que falava em seu nome 😬"),
        ("msg", "camila", "Refaz o pedido, Lucas. Pelo amor de Deus."),
        ("narr", "E tinha mais."),
        ("chat", "familia", "14:30", "HOJE"),
        ("msg", "neide", "Atenção família! Mudou o endereço da festa do Rafa 🎉 Agora é lá em casa, 19h. Lá é mais aconchegante 🙏"),
        ("msg", "rosana", "Anotado, Neide ❤️", dict(dig=0.3)),
        ("msg", "diego", "blz tia", dict(dig=0.3, ler=False, pausa=0.6)),
        ("msg", "camila", "Gente, NÃO mudou nada! A festa é no salão, 20h, como tá no convite!"),
        ("msg", "neide", "Ih, a Camila tá nervosa de novo 😔"),
        ("narr", "Até que a Bia mandou um print."),
        ("chat", "bia", "16:05", "HOJE"),
        ("msg", "bia", "AMIGA. Senta.", dict(dig=0.4)),
        ("foto", "bia", story_jessica, None, dict(pausa=3.0, w=430, h_max=760, zoom=True)),
        ("msg", "bia", "Essa é a Jéssica. A EX do Rafa."),
        ("msg", "camila", "A minha sogra convidou a EX do meu marido pra festa que EU organizei??"),
        ("msg", "bia", "E ainda marcou ela no story 😳"),
        ("narr", "Aí chegou mensagem de um número desconhecido."),
        ("chat", "jessica", "16:20", "HOJE"),
        ("msg", "jessica", "Oi Camila. Aqui é a Jéssica. Eu não vou na festa, não quero confusão."),
        ("msg", "jessica", "Mas a sua sogra me mandou um áudio... e você PRECISA ouvir isso."),
        ("audio", "jessica", "Jéssica, minha filha, é a Neide.", dict(voz="neide", enc=True, tocar=False, pausa=1.6)),
        ("fim", "CONTINUA…", "Parte 5: O áudio", "Comenta aí: o que você acha que tem nesse áudio? 🎧"),
    ]),
    # ---------------------------------------------------------------------------------------------- 5
    dict(parte=5, nome="O áudio", dia="sexta-feira, 20 de outubro", eventos=[
        ("gancho", "Família Souza 🙏", "Dona Neide: Esta mensagem foi apagada", "16:41",
         "Um áudio... que a família inteira ouviu."),
        ("titulo",),
        ("narr", "No capítulo anterior: a ex mandou pra Camila um áudio da sogra."),
        ("chat", "jessica", "16:22", None, (("chip", "HOJE"),
                                            ("jessica", "Mas a sua sogra me mandou um áudio... e você PRECISA ouvir isso.", "16:20"))),
        ("audio", "jessica", "Jéssica, minha filha, é a Neide. Vem bonita no sábado, viu? Essa Camila não é mulher pro meu filho. "
                             "Eu já dei um jeito no bolo e no endereço. Só falta você.",
         dict(voz="neide", enc=True)),
        ("msg", "camila", "Obrigada, Jéssica. De verdade."),
        ("msg", "jessica", "Mulher apoia mulher 💅"),
        ("narr", "A Camila pensou em brigar. Mas fez melhor."),
        ("chat", "familia", "16:40", "HOJE"),
        ("audio", "camila", "Jéssica, minha filha, é a Neide.", dict(voz="neide", enc=True, tocar=False, pausa=1.0)),
        ("msg", "camila", "Pra ninguém mais ter dúvida de quem tá mentindo nessa família."),
        ("msg", "neide", "Isso é montagem!!", dict(dig=0.4)),
        ("apagar", "neide"),
        ("msg", "rosana", "Neide... é a sua voz.", dict(dig=0.6)),
        ("msg", "diego", "😳😳😳", dict(dig=0.3, ler=False, pausa=0.8)),
        ("msg", "rafael", "Mãe. Eu ouvi tudo."),
        ("narr", "E o Rafael não parou por aí."),
        ("chat", "mae", "17:05", "HOJE"),
        ("msg", "rafael", "Mãe, a senhora passou de todos os limites."),
        ("msg", "rafael", "Tô indo aí agora pegar a chave do meu apartamento."),
        ("msg", "neide", "Filho, eu só queria o seu bem 😢"),
        ("msg", "rafael", "O meu bem é a Camila. A senhora vai ter que aceitar."),
        ("narr", "No sábado, teve festa. Com bolo... e sem a Dona Neide."),
        ("chat", "bia", "23:58", "SÁBADO"),
        ("msg", "bia", "E aí??? Como foi???", dict(dig=0.3)),
        ("foto", "camila", "bolo.jpg", "Foi PERFEITA. O Rafa chorou no parabéns 🥹"),
        ("msg", "bia", "E a jararaca?", dict(dig=0.4)),
        ("msg", "camila", "Nem apareceu 😌"),
        ("narr", "Até que, à meia-noite..."),
        ("chat", "neide", "00:00", "HOJE"),
        ("msg", "neide", "Camila.", dict(dig=0.6)),
        ("msg", "neide", "Já que é assim...", dict(dig=0.8)),
        ("msg", "neide", "Tem uma coisa sobre o Rafael que ninguém te contou.", dict(dig=1.2)),
        ("digitando", "neide", 2.0),
        ("fim", "FIM DA 1ª TEMPORADA", "Mas a Dona Neide ainda não acabou…", "Comenta PARTE 6 se você quer saber o segredo do Rafael! 👇"),
    ]),
]
