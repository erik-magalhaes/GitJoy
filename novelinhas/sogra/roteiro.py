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
    "golpe": dict(nome="Recupera Já", cor=(46, 125, 50)),
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
    "rosana_c": dict(dono="camila", titulo="Tia Rosana", com="rosana", sub="online"),
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
    d.text((w - 50, 740), "R$ 4.850,00", font=zap.inter(40, 800), fill=(20, 20, 20), anchor="ra")
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


def print_conversa(titulo, cor, msgs, hora="10:29", dono="neide"):
    """Print de uma conversa (lista de (quem, texto, hora)); quem == dono fica do lado direito."""
    im = zap.papel_parede().copy().convert("RGBA")
    zap.barra_status(im, hora)
    zap.cabecalho(im, titulo, "online", cor)
    y = zap.CHAT_Y0 + 24
    ant = None
    for quem, txt, hh in msgs:
        saida = quem == dono
        b, pad = zap.balao_texto(txt, hh, saida, quem != ant)
        x = zap.DIR - (b.width - pad) if saida else zap.ESQ - pad
        im.alpha_composite(b, (x, y - pad))
        y += b.height - 2 * pad + (20 if quem != ant else 6)
        ant = quem
    return im.crop((0, zap.STATUS_Y, zap.W, y + 30)).convert("RGB")


@functools.lru_cache(None)
def print_golpe():
    return print_conversa("Recupera Já 💰", (46, 125, 50), (
        ("golpe", "Sra. Neide, ÓTIMA NOTÍCIA! Conseguimos recuperar o seu investimento 💰", "10:21"),
        ("golpe", "Para liberar o valor, pague a taxa de R$ 3.000,00 via PIX até as 12h. Depois disso o valor é perdido.", "10:21"),
        ("neide", "Graças a Deus!! Vou fazer agora", "10:28"),
    ))


@functools.lru_cache(None)
def escritura():
    """Escritura do apartamento no nome da sogra."""
    w, h = 860, 1060
    im = Image.new("RGB", (w, h), (250, 246, 234))
    d = ImageDraw.Draw(im)
    d.rectangle((20, 20, w - 20, h - 20), outline=(150, 130, 90), width=4)
    d.text((w / 2, 90), "ESCRITURA DE COMPRA E VENDA", font=zap.inter(40, 800), fill=(60, 50, 30), anchor="mm")
    d.text((w / 2, 140), "2º Tabelionato de Notas", font=zap.inter(28, 450), fill=(110, 95, 70), anchor="mm")
    linhas = [("Imóvel:", "Apartamento 52, Bloco B"), ("", "Residencial Jardim das Flores"),
              ("Valor:", "R$ 280.000,00"), ("Data:", "15 de março de 2024")]
    y = 230
    for a, b in linhas:
        d.text((70, y), a, font=zap.inter(32, 700), fill=(60, 50, 30))
        d.text((230, y), b, font=zap.inter(32, 450), fill=(40, 40, 40))
        y += 60
    d.text((70, y + 30), "COMPRADORA:", font=zap.inter(34, 800), fill=(60, 50, 30))
    d.rounded_rectangle((60, y + 80, w - 60, y + 160), 10, fill=(255, 241, 118))
    d.text((80, y + 98), "NEIDE APARECIDA SOUZA", font=zap.inter(40, 800), fill=(20, 20, 20))
    for i in range(5):
        d.line([(70, y + 220 + i * 44), (w - 70, y + 220 + i * 44)], fill=(200, 190, 165), width=3)
    # carimbo
    cx, cy = w - 190, h - 170
    d.ellipse((cx - 110, cy - 110, cx + 110, cy + 110), outline=(170, 40, 40), width=8)
    d.text((cx, cy - 16), "REGISTRADO", font=zap.inter(30, 800), fill=(170, 40, 40), anchor="mm")
    d.text((cx, cy + 24), "CARTÓRIO", font=zap.inter(24, 600), fill=(170, 40, 40), anchor="mm")
    return im


# ------------------------------------------------------------------ episódios
# Só as conversas: sem narrador, título ou tela final. O que antes o narrador explicava agora aparece nas mensagens.
RAFA_MAE_PRINT = (("chip", "ONTEM"), ("neide", "Filho, levou o casaco?", "18:02"), ("rafael", "Levei mãe", "18:30"),
                  ("chip", "HOJE"), ("neide", "Filho", "09:30"), ("neide", "Você tá sentado?", "09:30"),
                  ("neide", "Achei uma coisa no celular da sua mulher.", "09:31"), ("rafael", "Que coisa, mãe?", "09:31"),
                  ("foto", "neide", print_lucas, "09:32", 640, 700), ("neide", "Quem é esse Lucas, filho?", "09:32"))

EPISODIOS = [
    # ---------------------------------------------------------------------------------------------- 1
    dict(parte=1, nome="Bom dia, nora", eventos=[
        ("chat", "neide", "06:12", "HOJE", (("chip", "ONTEM"),
                                            ("neide", "Rafa disse que o almoço de domingo é aí né", "21:40"),
                                            ("camila", "Isso, Dona Neide! Vou fazer frango com arroz 😊", "21:52"))),
        ("msg", "neide", "Bom dia nora 🌻🙏", dict(dig=0.3)),
        ("audio", "neide", "Camila, bom dia! O arroz de domingo tava empapado, viu? O Rafa gosta soltinho. Depois eu te ensino. Beijo!"),
        ("msg", "camila", "Bom dia, Dona Neide... são seis da manhã 😅"),
        ("chat", "bia", "08:40", "HOJE"),
        ("msg", "camila", "BIA. Ela entrou aqui de novo."),
        ("msg", "bia", "QUEM?? A sua sogra??", dict(dig=0.4)),
        ("msg", "camila", "Fui na padaria e quando voltei a porta tava destrancada."),
        ("msg", "camila", "Ela entrou com a chave que o Rafa deu \"só pra emergência\" 🙃"),
        ("msg", "bia", "E qual foi a emergência?"),
        ("msg", "camila", "A louça."),
        ("msg", "bia", "KKKKKKKK mentira", dict(dig=0.3, ler=False, pausa=0.8)),
        ("chat", "familia", "09:05", "HOJE"),
        ("foto", "neide", "pia.jpg", "Olha como o meu filho está vivendo 😢"),
        ("msg", "rosana", "Meu Deus do céu 😱", dict(dig=0.4)),
        ("msg", "diego", "kkkkkkkkkkk", dict(dig=0.3, ler=False, pausa=0.7)),
        ("msg", "camila", "Dona Neide, a senhora entrou na minha casa sem avisar e postou foto da minha pia no grupo??"),
        ("msg", "neide", "Só quis ajudar, minha filha. Não precisa ser grossa 🙏"),
        ("msg", "rosana", "Respeita a sua sogra, Camila."),
        ("chat", "bia", "09:12"),
        ("msg", "camila", "Vou tomar um banho antes que eu fale besteira. Ela ainda tá aqui 🙄"),
        ("msg", "bia", "Esconde esse celular, hein!"),
        ("msg", "camila", "Relaxa, ela nem sabe mexer em celular 😂"),
        ("chat", "mae", "09:31", "HOJE", (("chip", "ONTEM"), ("neide", "Filho, levou o casaco?", "18:02"),
                                          ("rafael", "Levei mãe", "18:30"))),
        ("msg", "neide", "Filho", dict(dig=0.4)),
        ("msg", "neide", "Você tá sentado?", dict(dig=0.5)),
        ("msg", "neide", "Achei uma coisa no celular da sua mulher.", dict(dig=0.8)),
        ("msg", "rafael", "Que coisa, mãe?"),
        ("foto", "neide", print_lucas, None, dict(pausa=3.6, h_max=640, w=700, zoom=True, hora="09:32")),
        ("msg", "neide", "Quem é esse Lucas, filho?", dict(dig=0.6, hora="09:32")),
        ("rascunho", "Mãe, isso deve ter", 1.0),
        ("pausa", 2.6),
    ]),
    # ---------------------------------------------------------------------------------------------- 2
    dict(parte=2, nome="Quem é Lucas?", eventos=[
        ("chat", "mae", "09:33", None, RAFA_MAE_PRINT),
        ("msg", "rafael", "Mãe, a senhora mexeu no celular dela??"),
        ("msg", "neide", "Tava desbloqueado em cima da mesa. Deus quis que eu visse 🙏"),
        ("msg", "rafael", "Isso deve ter uma explicação."),
        ("msg", "neide", "\"Ele NÃO pode saber\"? Filho, abre o olho."),
        ("chat", "familia_r", "09:40", "HOJE"),
        ("msg", "neide", "Gente, orem pelo casamento do meu filho 🙏😢"),
        ("msg", "rosana", "O que aconteceu, Neide???", dict(dig=0.3)),
        ("msg", "neide", "Não posso falar aqui. Mas tem um tal de LUCAS."),
        ("msg", "diego", "eita 👀🍿", dict(dig=0.3, ler=False, pausa=0.7)),
        ("msg", "rosana", "Eu sempre falei. Nunca gostei dessa menina."),
        ("msg", "diego", "Tia, quem é Lucas?"),
        ("chat", "bia", "09:52", "HOJE"),
        ("msg", "camila", "Bia, saí do banho e tem 47 mensagens no grupo da família 😰"),
        ("msg", "camila", "A minha sogra mexeu no meu celular. Ela viu as mensagens do Lucas."),
        ("msg", "bia", "NÃO. Ela vai estragar TUDO.", dict(dig=0.4)),
        ("msg", "camila", "Eu não posso contar pro Rafa. Não agora."),
        ("msg", "bia", "Amiga, se você não contar, ela vai contar a versão dela."),
        ("chat", "rafa", "09:55", "HOJE", (("chip", "ONTEM"), ("rafael", "Te amo, boa noite ❤️", "23:10"),
                                           ("camila", "Te amo mais 😘", "23:11"))),
        ("msg", "rafael", "Camila.", dict(dig=0.5)),
        ("msg", "rafael", "Quem é Lucas?", dict(dig=0.8)),
        ("digitando", "rafael", 1.8),
        ("pausa", 0.5),
        ("digitando", "rafael", 1.2),
        ("status", "visto por último hoje às 09:56"),
        ("rascunho", "Amor, eu posso explicar", 1.2),
        ("pausa", 3.2),
    ]),
    # ---------------------------------------------------------------------------------------------- 3
    dict(parte=3, nome="A surpresa", eventos=[
        ("chat", "rafa", "10:02", None, (("chip", "HOJE"), ("rafael", "Camila.", "09:55"), ("rafael", "Quem é Lucas?", "09:55"))),
        ("msg", "camila", "Amor, me liga. Não é nada do que a sua mãe tá falando."),
        ("foto", "camila", orcamento, None, dict(pausa=3.2, h_max=680, zoom=True)),
        ("msg", "camila", "O Lucas é o organizador de festas. É o seu aniversário surpresa de 35 anos!"),
        ("msg", "camila", "Eu tô preparando isso há três meses 😭"),
        ("digitando", "rafael", 1.4),
        ("msg", "rafael", "Meu Deus, Camila. Me desculpa.", dict(dig=0.3)),
        ("msg", "rafael", "Vou falar com a minha mãe agora."),
        ("chat", "neide", "10:15", "HOJE", (("chip", "HOJE"), ("neide", "Quem cedo madruga Deus ajuda 🙏", "06:14"))),
        ("msg", "camila", "Dona Neide, o Lucas é o organizador da festa surpresa do Rafa. A senhora estragou a surpresa que eu preparava há três meses."),
        ("msg", "neide", "E como eu ia saber? Mensagem escondida é coisa de quem deve."),
        ("msg", "camila", "A senhora mexeu no meu celular!"),
        ("audio", "neide", "Camila, a minha pressão subiu, viu? Tô aqui deitada, passando mal. Mas tudo bem. Eu sou a vilã, né? Sempre sou."),
        ("msg", "neide", "Tudo bem. Deus tá vendo 🙏"),
        ("chat", "rosana", "22:47", "HOJE"),
        ("msg", "neide", "Rosana. A festa do Rafa é sábado que vem."),
        ("msg", "rosana", "Então o tal do Lucas era da festa? Que bom, Neide!"),
        ("msg", "neide", "Bom pra quem?"),
        ("msg", "neide", "Eu vou levar uma convidada especial."),
        ("msg", "rosana", "Quem??", dict(dig=0.3)),
        ("msg", "neide", "Essa festa vai ser o fim desse casamento."),
        ("msg", "rosana", "Neide... o que você vai fazer?"),
        ("apagar", "neide"),
        ("digitando", "neide", 1.2),
        ("msg", "neide", "Nada não. Boa noite 🙏", dict(dig=0)),
        ("pausa", 2.6),
    ]),
    # ---------------------------------------------------------------------------------------------- 4
    dict(parte=4, nome="Sabotagem", eventos=[
        ("chat", "lucas", "14:10", "HOJE", (("chip", "QUARTA"), ("camila", "Tudo certo pro sábado, Lucas? 🙏", "11:20"),
                                            ("lucas", "Tudo certinho! Bolo, DJ e decoração ✅", "11:31"))),
        ("msg", "lucas", "Camila, tudo bem? Uma dúvida: por que você cancelou o bolo?"),
        ("msg", "camila", "Eu não cancelei nada!"),
        ("msg", "lucas", "Uma senhora ligou aqui ontem. Disse que era a sogra e que falava em seu nome 😬"),
        ("msg", "camila", "Refaz o pedido, Lucas. Pelo amor de Deus."),
        ("chat", "familia", "14:30", "HOJE"),
        ("msg", "neide", "Atenção família! Mudou o endereço da festa do Rafa 🎉 Agora é lá em casa, 19h. Lá é mais aconchegante 🙏"),
        ("msg", "rosana", "Anotado, Neide ❤️", dict(dig=0.3)),
        ("msg", "diego", "blz tia", dict(dig=0.3, ler=False, pausa=0.7)),
        ("msg", "camila", "Gente, NÃO mudou nada! A festa é no salão, 20h, como tá no convite!"),
        ("msg", "neide", "Ih, a Camila tá nervosa de novo 😔"),
        ("chat", "bia", "16:05", "HOJE"),
        ("msg", "bia", "AMIGA. Senta.", dict(dig=0.4)),
        ("foto", "bia", story_jessica, None, dict(pausa=3.4, w=430, h_max=760, zoom=True)),
        ("msg", "bia", "Essa é a Jéssica. A EX do Rafa."),
        ("msg", "camila", "A minha sogra convidou a EX do meu marido pra festa que EU organizei??"),
        ("msg", "bia", "E ainda marcou ela no story 😳"),
        ("chat", "jessica", "16:20", "HOJE"),
        ("msg", "jessica", "Oi Camila. Aqui é a Jéssica."),
        ("msg", "jessica", "Eu não vou na festa. Não quero confusão."),
        ("msg", "jessica", "Mas a sua sogra me mandou um áudio... e você PRECISA ouvir isso."),
        ("audio", "jessica", "Jéssica, minha filha, é a Neide.", dict(voz="neide", enc=True, tocar=False, pausa=1.2)),
        ("rascunho", "Meu Deus, o que ela", 0.8),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 5
    dict(parte=5, nome="O áudio", fim_texto="Fim da 1ª temporada", eventos=[
        ("chat", "jessica", "16:22", None, (("chip", "HOJE"), ("jessica", "Oi Camila. Aqui é a Jéssica.", "16:20"),
                                            ("jessica", "Mas a sua sogra me mandou um áudio... e você PRECISA ouvir isso.", "16:20"))),
        ("audio", "jessica", "Jéssica, minha filha, é a Neide. Vem bonita no sábado, viu? Essa Camila não é mulher pro meu filho. "
                             "Eu já dei um jeito no bolo e no endereço. Só falta você.", dict(voz="neide", enc=True, hora="16:20")),
        ("msg", "camila", "Eu não acredito."),
        ("msg", "camila", "Obrigada, Jéssica. De verdade."),
        ("msg", "jessica", "Mulher apoia mulher 💅"),
        ("chat", "familia", "16:40", "HOJE"),
        ("audio", "camila", "Jéssica, minha filha, é a Neide.", dict(voz="neide", enc=True, tocar=False, pausa=1.0)),
        ("msg", "camila", "Pra ninguém mais ter dúvida de quem tá mentindo nessa família."),
        ("msg", "neide", "Isso é montagem!!", dict(dig=0.4)),
        ("apagar", "neide"),
        ("msg", "rosana", "Neide... é a sua voz.", dict(dig=0.6)),
        ("msg", "diego", "😳😳😳", dict(dig=0.3, ler=False, pausa=0.8)),
        ("msg", "rafael", "Mãe. Eu ouvi tudo."),
        ("chat", "mae", "17:05", "HOJE"),
        ("msg", "rafael", "Mãe, a senhora passou de todos os limites."),
        ("msg", "rafael", "Tô indo aí agora pegar a chave do meu apartamento."),
        ("msg", "neide", "Filho, eu só queria o seu bem 😢"),
        ("msg", "rafael", "O meu bem é a Camila. A senhora vai ter que aceitar."),
        ("chat", "bia", "23:58", "SÁBADO"),
        ("msg", "bia", "E aí??? Como foi a festa???", dict(dig=0.3)),
        ("foto", "camila", "bolo.jpg", "Foi PERFEITA. O Rafa chorou no parabéns 🥹"),
        ("msg", "bia", "E a jararaca?", dict(dig=0.4)),
        ("msg", "camila", "Nem apareceu 😌"),
        ("chat", "neide", "00:00", "HOJE"),
        ("msg", "neide", "Camila.", dict(dig=0.6)),
        ("msg", "neide", "Já que é assim...", dict(dig=0.8)),
        ("msg", "neide", "Tem uma coisa sobre o Rafael que ninguém te contou.", dict(dig=1.2)),
        ("digitando", "neide", 2.0),
        ("pausa", 2.4),
    ]),
]


# ------------------------------------------------------------------ 2ª temporada: o segredo do apartamento
EPISODIOS += [
    # ---------------------------------------------------------------------------------------------- 6
    dict(parte=6, nome="O segredo", eventos=[
        ("chat", "neide", "00:01", None, (("chip", "HOJE"), ("neide", "Camila.", "00:00"), ("neide", "Já que é assim...", "00:00"),
                                          ("neide", "Tem uma coisa sobre o Rafael que ninguém te contou.", "00:00"))),
        ("msg", "neide", "Esse apartamento que vocês moram...", dict(dig=0.8)),
        ("msg", "neide", "É MEU.", dict(dig=0.6)),
        ("foto", "neide", escritura, None, dict(pausa=3.4, h_max=700, zoom=True)),
        ("msg", "neide", "Tá no meu nome. Por isso eu tenho a chave."),
        ("msg", "camila", "A senhora tá mentindo."),
        ("msg", "neide", "Pergunta pra ele. Boa noite, nora 🌻"),
        ("status", "visto por último hoje às 00:03"),
        ("chat", "bia", "00:06", "HOJE"),
        ("msg", "camila", "Bia, tá acordada?"),
        ("msg", "bia", "Tô sim. Que foi??", dict(dig=0.3)),
        ("msg", "camila", "A Dona Neide disse que o apartamento é dela. Mandou até a escritura."),
        ("msg", "bia", "COMO ASSIM?? O Rafa não disse que tinha comprado?"),
        ("msg", "camila", "Disse! Há dois anos!"),
        ("msg", "camila", "Ele tá dormindo do meu lado 😶"),
        ("chat", "rafa", "07:40", "HOJE", (("chip", "ONTEM"), ("rafael", "Melhor aniversário da minha vida ❤️", "23:30"))),
        ("msg", "camila", "Rafa, o apartamento tá no nome da sua mãe?"),
        ("digitando", "rafael", 1.6),
        ("msg", "rafael", "Quem te contou isso?", dict(dig=0.3)),
        ("msg", "camila", "Então é verdade."),
        ("msg", "rafael", "Amor, eu ia te contar."),
        ("msg", "rafael", "Quando a gente comprou, eu tava com o nome sujo. A minha mãe deu a entrada e colocou no nome dela."),
        ("msg", "rafael", "Mas quem paga as parcelas sou eu! Todo mês!"),
        ("msg", "camila", "Dois anos, Rafael. E você nunca falou nada."),
        ("msg", "camila", "Agora eu entendi por que ela entra aqui quando quer."),
        ("msg", "rafael", "Me perdoa. Eu fiquei com vergonha."),
        ("chat", "familia", "09:15", "HOJE"),
        ("msg", "neide", "Aviso importante: a partir do mês que vem eu vou precisar do MEU apartamento de volta."),
        ("msg", "rosana", "Que apartamento, Neide?", dict(dig=0.3)),
        ("msg", "neide", "O que o Rafa mora. Que é meu 🙏"),
        ("msg", "diego", "😳", dict(dig=0.3, ler=False, pausa=0.8)),
        ("pausa", 2.6),
    ]),
    # ---------------------------------------------------------------------------------------------- 7
    dict(parte=7, nome="Despejo", eventos=[
        ("chat", "mae", "09:20", None, (("chip", "HOJE"), ("neide", "Bom dia filho 🌻", "06:10"))),
        ("msg", "rafael", "Mãe, que história é essa no grupo?"),
        ("msg", "neide", "O apartamento é meu, filho. Eu que decido."),
        ("msg", "rafael", "Eu pago as parcelas há dois anos!"),
        ("audio", "neide", "Filho, é simples. Ou ela sai, ou vocês dois saem. Vocês têm trinta dias."),
        ("msg", "rafael", "Então a gente sai."),
        ("msg", "neide", "Você vai largar a sua mãe por causa dessa menina?"),
        ("msg", "rafael", "Eu não tô largando ninguém. Eu tô escolhendo a minha casa."),
        ("chat", "bia", "12:30", "HOJE"),
        ("msg", "camila", "Bia, a gente vai ter que se mudar em 30 dias 😭"),
        ("msg", "bia", "Já tô procurando! Olha esse:", dict(dig=0.4)),
        ("foto", "bia", "ape1.jpg", "2 quartos, perto do metrô. R$ 2.300"),
        ("msg", "camila", "Bonito! Mas é mais caro que a parcela..."),
        ("msg", "bia", "E esse aqui?"),
        ("foto", "bia", "ape2.jpg", "Esse tem até lareira kkkk R$ 9.800"),
        ("msg", "camila", "Bia, eu tô falando sério 😑"),
        ("msg", "bia", "Brincadeira! Amanhã a gente visita o primeiro."),
        ("chat", "rafa", "18:05", "HOJE"),
        ("msg", "rafael", "Amor, liguei pro dono do apartamento. Dá pra visitar sábado."),
        ("msg", "rafael", "Tenho. Lá nunca foi nosso de verdade."),
        ("msg", "rafael", "Onde você estiver, é a minha casa."),
        ("msg", "camila", "❤️", dict(ler=False, pausa=0.8)),
        ("chat", "rosana_c", "21:40"),
        ("msg", "rosana", "Camila, boa noite. É a Tia Rosana."),
        ("msg", "rosana", "Mas eu preciso te contar uma coisa sobre a sua sogra."),
        ("msg", "rosana", "Ela não pode saber que fui eu.", dict(dig=0.8)),
        ("digitando", "rosana", 2.0),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 8
    dict(parte=8, nome="A tia sabe", eventos=[
        ("chat", "rosana_c", "21:42", None, (("chip", "HOJE"), ("rosana", "Camila, boa noite. É a Tia Rosana.", "21:40"),
                                             ("rosana", "Mas eu preciso te contar uma coisa sobre a sua sogra.", "21:40"),
                                             ("rosana", "Ela não pode saber que fui eu.", "21:41"))),
        ("msg", "camila", "Pode falar, tia."),
        ("msg", "rosana", "A Neide não quer o apartamento por sua causa."),
        ("msg", "rosana", "Ela caiu num golpe. Na internet.", dict(dig=0.8)),
        ("msg", "camila", "Golpe??"),
        ("audio", "rosana", "Um rapaz falou com ela pelo celular, disse que era investimento, que o dinheiro ia dobrar. "
                            "Ela colocou tudo, Camila. As economias de uma vida inteira. E agora tá devendo pro banco."),
        ("msg", "rosana", "Ela quer vender o apartamento pra pagar a dívida. E tem vergonha de contar pro Rafa."),
        ("msg", "camila", "Meu Deus..."),
        ("msg", "camila", "Por que a senhora tá me contando isso?"),
        ("msg", "rosana", "Porque você foi a única que teve coragem de enfrentar ela. E ela vai precisar de alguém assim."),
        ("chat", "rafa", "22:05", "HOJE"),
        ("msg", "camila", "Amor, tá acordado?"),
        ("msg", "rafael", "Tô. O que foi?", dict(dig=0.3)),
        ("msg", "camila", "Eu preciso te contar uma coisa sobre a sua mãe. Mas promete que não vai brigar com ela."),
        ("msg", "rafael", "Camila, você tá me assustando."),
        ("msg", "camila", "Amanhã eu te explico tudo. Pessoalmente."),
        ("chat", "neide", "23:48", "HOJE", (("chip", "ONTEM"), ("neide", "Pergunta pra ele. Boa noite, nora 🌻", "00:02"))),
        ("audio", "neide", "Rosana, eu não aguento mais. Eles vão sair do apartamento e eu vou ter que vender mesmo assim. "
                           "O banco ligou de novo hoje. E eu não tenho coragem de contar pro meu filho."),
        ("msg", "camila", "Dona Neide..."),
        ("msg", "camila", "Esse áudio veio pra mim."),
        ("digitando", "neide", 1.4),
        ("apagar", "neide"),
        ("msg", "neide", "Ignora. Foi engano 🙏", dict(dig=0.6)),
        ("pausa", 2.6),
    ]),
    # ---------------------------------------------------------------------------------------------- 9
    dict(parte=9, nome="Áudio errado", eventos=[
        ("chat", "neide", "23:50", None, (("chip", "HOJE"), ("camila", "Dona Neide...", "23:49"), ("camila", "Esse áudio veio pra mim.", "23:49"),
                                          ("neide", "Ignora. Foi engano 🙏", "23:49"))),
        ("msg", "camila", "Eu já ouvi, Dona Neide."),
        ("msg", "camila", "E eu sei do golpe."),
        ("digitando", "neide", 2.0),
        ("msg", "neide", "Foi a Rosana, né?", dict(dig=0.3)),
        ("msg", "camila", "Não importa quem foi. Importa que a senhora não tá sozinha."),
        ("audio", "neide", "Camila, eu fui uma boba. Eu achei que ia deixar alguma coisa pro Rafa e perdi tudo. "
                           "E ainda descontei em você. Eu tenho vergonha de olhar na sua cara."),
        ("msg", "camila", "A senhora não foi boba. Esses golpistas enganam todo mundo."),
        ("msg", "camila", "Amanhã a gente vai no banco. Eu, a senhora e o Rafa."),
        ("msg", "neide", "O Rafa não pode saber!"),
        ("msg", "camila", "Ele precisa saber. Ele é seu filho."),
        ("chat", "bia", "08:10", "HOJE"),
        ("msg", "camila", "Bia, eu preciso da minha amiga advogada 🙏"),
        ("msg", "bia", "Sempre! O que houve?", dict(dig=0.3)),
        ("msg", "camila", "A minha sogra caiu num golpe de investimento. Perdeu tudo."),
        ("msg", "bia", "A JARARACA??", dict(dig=0.3)),
        ("msg", "camila", "Bia..."),
        ("msg", "bia", "Tá, desculpa. Ela fez PIX?"),
        ("msg", "camila", "Fez. E agora tá devendo pro banco."),
        ("msg", "bia", "Tem que fazer boletim de ocorrência hoje e pedir o MED no banco. Às vezes dá pra recuperar uma parte."),
        ("chat", "neide", "10:30", "HOJE"),
        ("msg", "neide", "Camila, socorro", dict(dig=0.4)),
        ("foto", "neide", print_golpe, None, dict(pausa=3.6, h_max=700, w=700, zoom=True)),
        ("msg", "neide", "Eles disseram que se eu pagar essa taxa eu recebo tudo de volta!"),
        ("msg", "neide", "Já tô no aplicativo do banco...", dict(dig=0.8)),
        ("pausa", 2.6),
    ]),
    # ---------------------------------------------------------------------------------------------- 10
    dict(parte=10, nome="A chave", fim_texto="Fim da 2ª temporada", eventos=[
        ("chat", "neide", "10:31", None, (("chip", "HOJE"), ("neide", "Camila, socorro", "10:30"),
                                          ("foto", "neide", print_golpe, "10:30", 520, 600),
                                          ("neide", "Já tô no aplicativo do banco...", "10:31"))),
        ("msg", "camila", "NÃO PAGA!!!"),
        ("msg", "camila", "Dona Neide, é golpe de novo! Ninguém cobra taxa pra devolver dinheiro!"),
        ("digitando", "neide", 1.4),
        ("msg", "neide", "Mas eles sabiam o meu nome, o meu CPF...", dict(dig=0.3)),
        ("msg", "camila", "Fecha esse aplicativo. Eu tô indo aí agora."),
        ("msg", "neide", "Tá bom. Já fechei 🙏"),
        ("chat", "familia", "15:20", "HOJE"),
        ("msg", "camila", "Família, eu e o Rafa passamos o dia com a Dona Neide."),
        ("msg", "camila", "Ela caiu num golpe. A gente fez o boletim e a contestação no banco. Uma parte do dinheiro vai voltar 🙏"),
        ("msg", "rosana", "Graças a Deus 🙏", dict(dig=0.3)),
        ("msg", "rafael", "Obrigado, amor. Você foi incrível hoje."),
        ("msg", "neide", "Eu quero falar uma coisa."),
        ("audio", "neide", "Camila, eu te devo desculpas. Eu entrei na sua casa, mexi no seu celular, falei mal de você pra família inteira. "
                           "E quando eu mais precisei, foi você que me ajudou. Me perdoa, minha filha."),
        ("msg", "camila", "Tá perdoada, Dona Neide ❤️"),
        ("chat", "neide", "18:00", "HOJE"),
        ("msg", "neide", "Camila, o apartamento continua de vocês. Semana que vem eu passo pro nome do Rafa."),
        ("msg", "neide", "Deixei a minha chave com o porteiro. Agora eu só entro se vocês me convidarem 🙏"),
        ("msg", "camila", "A senhora tá convidada pro almoço de domingo 😊"),
        ("msg", "neide", "Eu levo o arroz. Bem soltinho 🌻"),
        ("chat", "bia", "22:30", "HOJE"),
        ("msg", "bia", "E aí, como foi o dia?", dict(dig=0.3)),
        ("msg", "camila", "Bia... eu preciso te contar uma coisa."),
        ("msg", "camila", "Eu tô grávida."),
        ("msg", "bia", "QUÊ????? 😱😱", dict(dig=0.3)),
        ("msg", "bia", "A DONA NEIDE VAI SER AVÓ?? 😂", dict(dig=0.6)),
        ("pausa", 2.6),
    ]),
]
