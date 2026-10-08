"""O Portão: novela (drama) em 5 partes do Compartilhado, sobre um pai que abandonou o filho.

O Gabriel acabou de ser pai do Miguel. O Roberto, pai dele, sumiu quando ele tinha 7 anos (no aniversário de 8, o
Gabriel ficou no portão esperando até dormir) e reaparece 18 anos depois querendo conhecer o neto. Ele tem outra filha,
a Manu (16), que conta que o pai está com leucemia e precisa de transplante de medula. O Gabriel acha que foi procurado
só por isso, mas a Manu mostra as mensagens que o pai escreveu por anos e nunca teve coragem de mandar. O Gabriel faz o
exame, é compatível e doa, não por ele, mas pela Manu e pelo Miguel. A Dona Rose, mãe do Gabriel, resiste e depois apoia.
Fim: "Domingo tem almoço aqui. O portão vai estar aberto."
"""
import functools
import os

from PIL import Image, ImageDraw, ImageEnhance, ImageOps

import zap

FOTOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fotos")
TITULO = "O Portão"

THALITA = ("pt-BR-ThalitaMultilingualNeural", "+0%", "+0Hz")
ANTONIO = ("pt-BR-AntonioNeural", "+0%", "+0Hz")
FRANCISCA = ("pt-BR-FranciscaNeural", "+0%", "+0Hz")
VOZES = {"livia": THALITA, "manu": THALITA, "rose": FRANCISCA,
         "gabriel": ANTONIO, "roberto": ANTONIO}

PERSONAGENS = {
    "gabriel": dict(nome="Gabriel", cor=(30, 136, 229)),
    "livia": dict(nome="Lívia", cor=(216, 27, 96)),
    "rose": dict(nome="Mãe", cor=(142, 36, 170)),
    "roberto": dict(nome="Roberto", cor=(93, 64, 55)),
    "manu": dict(nome="Manu", cor=(0, 137, 123)),
}

CHATS = {
    "livia": dict(dono="gabriel", titulo="Lívia ❤️", com="livia", sub="online"),
    "rose": dict(dono="gabriel", titulo="Mãe 💜", com="rose", sub="online"),
    "roberto": dict(dono="gabriel", titulo="+55 11 99412-5530", com="roberto", sub="online"),
    "manu": dict(dono="gabriel", titulo="+55 11 98120-7744", com="manu", sub="online"),
}


@functools.lru_cache(None)
def foto_aniversario():
    """A foto do aniversário de 8 anos: o bolo, com cara de foto antiga (amarelada, com borda branca)."""
    im = Image.open(os.path.join(FOTOS, "bolo_infantil.jpg")).convert("RGB")
    im.thumbnail((760, 760))
    im = ImageEnhance.Color(im).enhance(0.55)
    sepia = ImageOps.colorize(ImageOps.grayscale(im), (60, 40, 20), (255, 236, 200))
    im = Image.blend(im, sepia, 0.55)
    im = ImageEnhance.Contrast(im).enhance(0.85)
    moldura = Image.new("RGB", (im.width + 60, im.height + 150), (246, 242, 232))
    moldura.paste(im, (30, 30))
    d = ImageDraw.Draw(moldura)
    d.text((moldura.width // 2, im.height + 92), "Gabriel, 8 anos", font=zap.fonte("Pacifico-Regular.ttf", 44),
           fill=(70, 70, 120), anchor="mm")
    return moldura


@functools.lru_cache(None)
def notas_roberto():
    """Print do bloco de notas do pai: mensagens que ele escreveu e nunca mandou."""
    w = 820
    notas = [("12/03/2016", "Gabriel, hoje você faz 15 anos. Eu vi você de longe na escola. Não tive coragem."),
             ("12/03/2019", "18 anos, filho. Escrevi e apaguei umas dez vezes."),
             ("20/11/2022", "Soube que você se formou. Eu chorei sozinho no carro."),
             ("07/10/2026", "Hoje eu nasci de novo: vi a foto do seu filho. Vou te mandar mensagem. Dessa vez eu vou.")]
    h = 150 + len(notas) * 210
    im = Image.new("RGB", (w, h), (255, 251, 230))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, 110), fill=(255, 202, 40))
    d.text((34, 55), "Notas · Pro Gabriel (não enviar)", font=zap.inter(36, 800), fill=(40, 30, 0), anchor="lm")
    y = 140
    for data, txt in notas:
        d.text((34, y), data, font=zap.inter(26, 700), fill=(150, 120, 40))
        zap.texto_rico(im, 34, y + 34, txt, zap.inter(32, 500), (40, 40, 40), maxw=w - 70)
        y += 210
        d.line([(34, y - 26), (w - 34, y - 26)], fill=(230, 220, 180), width=2)
    return im


@functools.lru_cache(None)
def resultado_exame():
    w = 820
    linhas = [("Paciente", "Roberto Almeida"), ("Doador", "Gabriel Almeida"), ("Tipo", "Haploidêntico (pai e filho)"),
              ("Resultado", "COMPATÍVEL")]
    h = 200 + len(linhas) * 80 + 60
    im = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, 120), fill=(21, 101, 192))
    d.text((40, 60), "Hemocentro · Exame HLA", font=zap.inter(40, 800), fill=(255, 255, 255), anchor="lm")
    y = 170
    for i, (a, b) in enumerate(linhas):
        if i == len(linhas) - 1:
            d.rounded_rectangle((26, y - 14, w - 26, y + 56), 10, fill=(200, 230, 201))
        d.text((40, y), a, font=zap.inter(32, 500), fill=(90, 90, 90))
        d.text((w - 40, y), b, font=zap.inter(32, 750), fill=(25, 25, 25), anchor="ra")
        y += 80
    return im


EPISODIOS = [
    # ---------------------------------------------------------------------------------------------- 1
    dict(parte=1, nome="O neto", eventos=[
        ("chat", "rose", "07:30", "HOJE"),
        ("foto", "gabriel", "pezinho.jpg", "Mãe, o Miguel nasceu! Três quilos e duzentos 😭💙"),
        ("msg", "rose", "MEU NETO!!! 😭😭 Tô indo pro hospital agora!", dict(dig=0.2)),
        ("msg", "rose", "Posso postar a foto do pezinho no Facebook?", dict(dig=0.4)),
        ("msg", "gabriel", "Pode, vovó Rose 😂"),
        ("chat", "livia", "09:00", "HOJE"),
        ("msg", "livia", "Amor, ele dormiu no meu peito. Eu não paro de olhar pra ele 🥹", dict(dig=0.4)),
        ("msg", "gabriel", "Eu prometi pra ele hoje cedo: eu nunca vou ser o pai que eu tive."),
        ("msg", "livia", "Você já não é. Vem logo pro quarto ❤️", dict(dig=0.4)),
        ("chat", "roberto", "21:40", "HOJE"),
        ("msg", "roberto", "Gabriel?", dict(dig=0.8)),
        ("msg", "roberto", "Aqui é o Roberto. O seu pai.", dict(dig=1.0)),
        ("msg", "roberto", "Vi a foto do bebê no Facebook da sua mãe. Parabéns, filho.", dict(dig=0.8)),
        ("rascunho", "Filho? Você nem sabe", 1.2),
        ("msg", "gabriel", "Você foi embora quando eu tinha sete anos."),
        ("msg", "gabriel", "Dezoito anos sem uma mensagem. E agora me chama de filho?"),
        ("digitando", "roberto", 2.2),
        ("msg", "roberto", "Eu sei que eu não tenho esse direito."),
        ("msg", "roberto", "Mas eu queria muito conhecer o meu neto.", dict(dig=0.6)),
        ("chat", "rose", "21:50", "HOJE"),
        ("msg", "gabriel", "Mãe. O Roberto me mandou mensagem. Quer conhecer o Miguel."),
        ("digitando", "rose", 2.0),
        ("msg", "rose", "Depois de dezoito anos?? Ele viu a foto, né? Eu devia ter deixado o Facebook fechado.", dict(dig=0.3)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 2
    dict(parte=2, nome="O portão", eventos=[
        ("chat", "rose", "21:52", None, (("chip", "HOJE"), ("gabriel", "Mãe. O Roberto me mandou mensagem. Quer conhecer o Miguel.", "21:50"),
                                         ("rose", "Depois de dezoito anos?? Ele viu a foto, né? Eu devia ter deixado o Facebook fechado.", "21:50"))),
        ("audio", "rose", "Filho, você lembra do seu aniversário de oito anos? Ele prometeu que vinha. Você não deixou ninguém "
                          "cortar o bolo. Ficou sentado no portão esperando até dormir. Eu te carreguei pra cama."),
        ("foto", "rose", foto_aniversario, "Achei essa foto na caixa de fotos antigas.", dict(zoom=True, pausa=0.8, h_max=600)),
        ("msg", "gabriel", "Eu lembro, mãe. Eu lembro do portão."),
        ("chat", "roberto", "22:10", "HOJE"),
        ("msg", "gabriel", "Você lembra do meu aniversário de oito anos?"),
        ("digitando", "roberto", 2.4),
        ("msg", "roberto", "Lembro. Eu tava a duas quadras. Parei o carro e não tive coragem de chegar."),
        ("msg", "roberto", "Eu tinha vinte e dois anos e fugi. Foi o maior erro da minha vida.", dict(dig=0.6)),
        ("msg", "gabriel", "E nos outros dezoito anos? Faltou coragem todos os dias?"),
        ("msg", "roberto", "Eu casei de novo. Tenho uma filha, a Manu. Ela tem dezesseis anos.", dict(dig=0.8)),
        ("msg", "gabriel", "Então você soube ser pai."),
        ("msg", "gabriel", "Só não de mim."),
        ("status", "visto por último hoje às 22:14"),
        ("chat", "manu", "23:30", "HOJE"),
        ("msg", "manu", "Oi, Gabriel. Desculpa mandar mensagem assim.", dict(dig=0.6)),
        ("msg", "manu", "Eu sou a Manu. A sua irmã. Peguei o seu número no celular do pai.", dict(dig=0.6)),
        ("msg", "manu", "Ele não ia te contar. Mas ele tá doente.", dict(dig=1.0)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 3
    dict(parte=3, nome="Não enviar", eventos=[
        ("chat", "manu", "23:31", None, (("chip", "ONTEM"), ("manu", "Eu sou a Manu. A sua irmã. Peguei o seu número no celular do pai.", "23:30"),
                                         ("manu", "Ele não ia te contar. Mas ele tá doente.", "23:30"))),
        ("msg", "gabriel", "Doente como?"),
        ("msg", "manu", "Leucemia. Ele precisa de um transplante de medula.", dict(dig=0.4)),
        ("msg", "manu", "Eu fiz o exame e não sou compatível. Os médicos querem testar a família toda.", dict(dig=0.4)),
        ("msg", "gabriel", "Então é isso. Ele não me procurou por causa do neto. Me procurou porque precisa de mim."),
        ("msg", "manu", "NÃO! Ele te procurou antes do diagnóstico. Juro.", dict(dig=0.2)),
        ("msg", "manu", "Olha o que eu achei no celular dele.", dict(dig=0.4)),
        ("foto", "manu", notas_roberto, None, dict(zoom=True, pausa=5.0, h_max=700)),
        ("msg", "manu", "Ele escreve pra você faz anos. Só nunca mandou.", dict(dig=0.4)),
        ("chat", "livia", "23:50", "ONTEM"),
        ("msg", "gabriel", "Lívia, o meu pai tá com leucemia. Precisa de medula. E ele escrevia pra mim todo ano e nunca mandava."),
        ("msg", "livia", "Meu Deus, amor. E o que você tá sentindo?", dict(dig=0.4)),
        ("msg", "gabriel", "Raiva. E uma vontade de chorar que eu não sei de onde vem."),
        ("msg", "livia", "Vem de um menino de oito anos sentado num portão ❤️", dict(dig=0.6)),
        ("chat", "rose", "08:00", "HOJE"),
        ("msg", "gabriel", "Mãe, ele tá com leucemia. Eu vou fazer o exame de compatibilidade."),
        ("msg", "rose", "Ele te abandonou e agora quer a sua medula??", dict(dig=0.2)),
        ("msg", "rose", "Filho, você acabou de ter um bebê. Você não deve nada pra esse homem.", dict(dig=0.4)),
        ("msg", "gabriel", "Eu sei que não devo, mãe."),
        ("chat", "manu", "08:10", "HOJE"),
        ("msg", "gabriel", "Manu. Onde eu faço o exame?"),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 4
    dict(parte=4, nome="Compatível", eventos=[
        ("chat", "manu", "16:00", "SEXTA", (("chip", "TERÇA"), ("gabriel", "Manu. Onde eu faço o exame?", "08:10"),
                                            ("manu", "Hemocentro da Paulista. Obrigada, irmão 🥹", "08:11"))),
        ("msg", "manu", "Gabriel... saiu o resultado.", dict(dig=0.4)),
        ("foto", "manu", resultado_exame, "Você é compatível!! 😭", dict(zoom=True, pausa=0.8, h_max=600)),
        ("chat", "roberto", "16:30", "SEXTA"),
        ("audio", "roberto", "Filho, a Manu me contou. Eu não quero que você faça isso por mim. Eu não mereço. Eu não fui no seu "
                             "aniversário, não fui na sua formatura, não fui em nada."),
        ("msg", "gabriel", "Não é por você."),
        ("msg", "gabriel", "É pela Manu, que não vai ficar sem pai. E pelo Miguel, que merece conhecer o avô."),
        ("msg", "gabriel", "Mesmo um avô atrasado dezoito anos."),
        ("msg", "roberto", "Obrigado, filho 😭", dict(dig=1.0)),
        ("chat", "rose", "17:00", "SEXTA"),
        ("msg", "gabriel", "Mãe, eu sou compatível. A doação é segunda."),
        ("digitando", "rose", 2.6),
        ("audio", "rose", "Eu fiquei com raiva a semana inteira, filho. Raiva dele, não de você. Mas eu te criei pra ser "
                          "melhor que ele. E você é. Vai. Eu fico com o Miguel."),
        ("msg", "gabriel", "Te amo, mãe 💜"),
        ("chat", "livia", "06:00", "SEGUNDA"),
        ("msg", "livia", "Amor, o Miguel e eu tamo aqui no corredor. Vai dar tudo certo ❤️", dict(dig=0.4)),
        ("msg", "gabriel", "Tô entrando. O médico disse que demora umas horas."),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 5
    dict(parte=5, nome="Dessa vez eu chego", fim_texto="Fim", eventos=[
        ("chat", "manu", "14:00", "SEGUNDA", (("chip", "SEXTA"), ("manu", "Você é compatível!! 😭", "16:00"))),
        ("msg", "manu", "Gabriel! O transplante deu certo! O médico disse que a medula pegou! 😭😭", dict(dig=0.2)),
        ("msg", "gabriel", "Graças a Deus, Manu."),
        ("msg", "manu", "Ele acordou e a primeira coisa que perguntou foi de você.", dict(dig=0.4)),
        ("msg", "gabriel", "E o que você falou?"),
        ("msg", "manu", "Que você tava no quarto do lado, dormindo. E roncando igualzinho a ele 😂", dict(dig=0.4)),
        ("msg", "gabriel", "Isso eu não precisava saber 😂"),
        ("chat", "roberto", "10:00", "UM MÊS DEPOIS"),
        ("msg", "roberto", "Filho, hoje eu tive alta.", dict(dig=0.6)),
        ("msg", "roberto", "Eu tenho a sua medula. E não tenho nem o seu perdão. Eu sei disso.", dict(dig=0.8)),
        ("msg", "gabriel", "Perdão leva tempo. Mas dá pra começar."),
        ("foto", "gabriel", "pezinho.jpg", "Esse é o Miguel."),
        ("msg", "gabriel", "Domingo tem almoço aqui em casa. Traz a Manu."),
        ("msg", "gabriel", "O portão vai estar aberto."),
        ("digitando", "roberto", 2.4),
        ("msg", "roberto", "Eu vou chegar cedo, filho. Dessa vez eu chego. 😭"),
        ("msg", "gabriel", "Eu sei, pai. Te espero."),
        ("chat", "rose", "10:20", "UM MÊS DEPOIS"),
        ("msg", "gabriel", "Mãe, chamei o Roberto e a Manu pro almoço de domingo."),
        ("digitando", "rose", 2.0),
        ("msg", "rose", "Então eu faço o bolo.", dict(dig=0.4)),
        ("msg", "rose", "Dessa vez a gente corta junto 💜", dict(dig=0.6)),
        ("pausa", 2.4),
    ]),
]
