"""A Chácara 2: A Represa. Continuação de A Chácara, em 7 partes (terror, WhatsApp escuro). Final fechado, sem gancho.

Dois meses depois. A Bel está presa e só manda um recado: "ainda falta um". O Seu Dito, o caseiro, acha no celeiro uma
mochila escondida (máscara, luvas, um tênis 42 com barro vermelho) e é a nova "primeira vítima". A Malu, o Theo e o Kauã
(os sobreviventes) desconfiam um do outro; o Kauã empurra a suspeita para o Theo. O pai da Lara conta que ela tinha um
namorado escondido, "um tal de K". A delegada rastreia o celular da Mel até a rua do Kauã, e a Malu percebe a pista da
primeira temporada: ele disse que estava em São Paulo e chegou à chácara em cinco minutos. O Kauã era o namorado da Lara
e planejou tudo com a Bel. A Malu o atrai para o cais da represa com a polícia escondida. Fim: a verdade sobre a Lara
contada à polícia e flores na represa.
"""
import functools
import os

from PIL import Image, ImageDraw

import zap
from chacara.roteiro import _noite

FOTOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fotos")
TITULO = "A Chácara 2"
TEMA = "escuro"
TRILHA = "terror"

THALITA = ("pt-BR-ThalitaMultilingualNeural", "+0%", "+0Hz")
ANTONIO = ("pt-BR-AntonioNeural", "+0%", "+0Hz")
FRANCISCA = ("pt-BR-FranciscaNeural", "+0%", "+0Hz")
VOZES = {"malu": THALITA, "ro": FRANCISCA, "ana": FRANCISCA,
         "theo": ANTONIO, "kaua": ANTONIO, "dito": ANTONIO, "rubens": ANTONIO, "assassino": ANTONIO}
EFEITO_VOZ = {"assassino": "mascara"}
PRONUNCIA = {r"\bKauã\b": "Cauã", r"\bTheo\b": "Téo", r"\bRô\b": "Rô"}

PERSONAGENS = {
    "malu": dict(nome="Malu", cor=(126, 87, 194)),
    "theo": dict(nome="Theo", cor=(30, 136, 229)),
    "kaua": dict(nome="Kauã", cor=(67, 160, 71)),
    "dito": dict(nome="Seu Dito", cor=(141, 110, 99)),
    "ro": dict(nome="Rô", cor=(255, 167, 38)),
    "ana": dict(nome="Delegada Ana", cor=(0, 137, 123)),
    "rubens": dict(nome="Rubens", cor=(120, 144, 156)),
    "assassino": dict(nome="Mel", cor=(255, 179, 0)),
}

NOMES = {"theo": "Theo", "kaua": "Kauã"}
CHATS = {
    # Parte 1: o celular do Seu Dito
    "ro": dict(dono="dito", titulo="Rô 💛 (filha)", com="ro", sub="online"),
    # Partes 2 a 7: o celular da Malu
    "sobrev": dict(dono="malu", titulo="Nós três", grupo=True, sub="Theo, Kauã, Você", nomes=NOMES),
    "mel": dict(dono="malu", titulo="Mel 🌻", com="assassino", sub="online"),
    "theo": dict(dono="malu", titulo="Theo", com="theo", sub="online"),
    "kaua": dict(dono="malu", titulo="Kauã", com="kaua", sub="online"),
    "ana": dict(dono="malu", titulo="Delegada Ana", com="ana", sub="online"),
    "rubens": dict(dono="malu", titulo="+55 11 97321-0450", com="rubens", sub="online"),
}


def _foto(nome):
    return Image.open(os.path.join(FOTOS, nome)).convert("RGB")


@functools.lru_cache(None)
def porteira_vende():
    """A porteira da chácara, com a placa de VENDE-SE pintada à mão."""
    im = _foto("porteira_campo.jpg")
    w = 760
    im = im.resize((w, round(w * im.height / im.width)))
    d = ImageDraw.Draw(im)
    x, y = 70, im.height - 230
    d.rectangle((x, y, x + 300, y + 130), fill=(245, 236, 210), outline=(90, 60, 30), width=6)
    d.text((x + 150, y + 45), "VENDE-SE", font=zap.inter(52, 900), fill=(180, 30, 30), anchor="mm")
    d.text((x + 150, y + 100), "tratar com Theo", font=zap.inter(28, 600), fill=(60, 40, 20), anchor="mm")
    d.line([(x + 60, y + 130), (x + 60, y + 220)], fill=(90, 60, 30), width=10)
    d.line([(x + 240, y + 130), (x + 240, y + 220)], fill=(90, 60, 30), width=10)
    return im


@functools.lru_cache(None)
def estrada_noite():
    return _noite("estrada_noite.jpg", 0.9, 8, azul=False)


@functools.lru_cache(None)
def cais_noite():
    return _noite("cais_represa.jpg", 0.55, 11)


@functools.lru_cache(None)
def localizacao_mel():
    """Card da delegada: o celular da Mel liga sempre na mesma rua."""
    w, h = 720, 620
    im = Image.new("RGB", (w, h), (40, 46, 56))
    d = ImageDraw.Draw(im)
    for x in range(0, w, 120):
        d.line([(x, 0), (x, h - 160)], fill=(70, 78, 92), width=14)
    for y in range(40, h - 160, 110):
        d.line([(0, y), (w, y)], fill=(70, 78, 92), width=14)
    d.text((370, 250), "R. das Palmeiras", font=zap.inter(24, 600), fill=(170, 180, 195))
    for k, (cx, cy) in enumerate(((330, 210), (352, 228), (318, 236))):
        d.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), fill=(229, 57, 53), outline=(255, 255, 255), width=4)
    d.rectangle((0, h - 160, w, h), fill=(28, 32, 40))
    d.text((30, h - 120), "Celular da Mel · 3 sinais", font=zap.inter(32, 750), fill=(235, 235, 235))
    d.text((30, h - 70), "Rua das Palmeiras, Vila Nova · 2 min cada", font=zap.inter(28, 500), fill=(255, 138, 128))
    return im


@functools.lru_cache(None)
def print_kaua():
    """Print da conversa da Malu com o Kauã na noite da chácara (primeira temporada)."""
    im = zap.papel_parede().copy().convert("RGBA")
    zap.barra_status(im, "22:20")
    zap.cabecalho(im, "Kauã", "online", (67, 160, 71))
    y = zap.CHAT_Y0 + 24
    for quem, txt, hh in (("malu", "Kauã, é você? É você que tá fazendo isso com a gente?", "22:03"),
                          ("kaua", "Eu?? Malu, eu tô em casa, em São Paulo! Que história é essa?", "22:03"),
                          ("malu", "Chama a polícia. Eu tô no celeiro.", "22:16"),
                          ("kaua", "Tô a cinco minutos! A polícia tá logo atrás de mim!", "22:20")):
        saida = quem == "malu"
        b, pad = zap.balao_texto(txt, hh, saida, True)
        x = zap.DIR - (b.width - pad) if saida else zap.ESQ - pad
        im.alpha_composite(b, (x, y - pad))
        y += b.height - 2 * pad + 20
    return im.crop((0, zap.STATUS_Y, zap.W, y + 30)).convert("RGB")


EPISODIOS = [
    # ---------------------------------------------------------------------------------------------- 1
    # A nova "primeira vítima": o Seu Dito, pelo celular dele.
    dict(parte=1, nome="O caseiro", eventos=[
        ("chat", "ro", "18:30", "SEXTA"),
        ("msg", "ro", "Pai, o senhor vai mesmo dormir na chácara hoje? Depois de tudo que aconteceu lá?", dict(dig=0.4)),
        ("msg", "dito", "Vou, filha. O Theo vendeu a chácara. Amanhã os donos novos vêm buscar a chave."),
        ("foto", "dito", porteira_vende, "Até placa eu pintei.", dict(pausa=0.6)),
        ("msg", "ro", "Ficou linda, pai 😂 Mas me manda mensagem de hora em hora, tá?", dict(dig=0.4)),
        ("chat", "ro", "21:10"),
        ("msg", "dito", "Rô, fui limpar o celeiro e achei uma mochila escondida lá em cima, no meio do feno."),
        ("msg", "ro", "Mochila de quem?", dict(dig=0.3)),
        ("msg", "dito", "Tem uma máscara preta, luva e um tênis 42 sujo de barro vermelho."),
        ("msg", "dito", "Não é da moça que a polícia prendeu. Tênis de homem."),
        ("msg", "ro", "PAI. Larga isso aí e liga pra polícia!", dict(dig=0.2)),
        ("msg", "dito", "Vou ligar. Deixa eu só guardar no carro primeiro."),
        ("assobio", 4.0, 0.25),
        ("msg", "dito", "Filha. Tem alguém assobiando no milharal."),
        ("msg", "ro", "Pai, entra no carro e vai embora AGORA!", dict(dig=0.2)),
        ("pausa", 1.0),
        ("msg", "dito", "a chave do carro sumiu", dict(falha=True)),
        ("msg", "dito", "o sinal caiu rô", dict(falha=True)),
        ("assobio", 3.5, 0.32),
        ("msg", "dito", "tô no celeiro de novo. com a mochila", dict(falha=True)),
        ("msg", "dito", "ele tá na porta do celeiro. ele quer a mochila", dict(falha=True)),
        ("pausa", 2.6),
        ("msg", "ro", "Pai? Tá aí?", dict(dig=0.2)),
        ("msg", "ro", "Pai, faz uma hora. Me responde!", dict(dig=0.2, hora="22:15")),
        ("msg", "ro", "PAI, EU TÔ CHAMANDO A POLÍCIA", dict(dig=0.2, hora="22:40")),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 2
    dict(parte=2, nome="Nós três", eventos=[
        ("chat", "sobrev", "08:00", "SÁBADO"),
        ("msg", "theo", "Gente. O Seu Dito sumiu. A filha dele achou o carro aberto na chácara e ele não tava.", dict(dig=0.4)),
        ("msg", "malu", "Não. Não, não, não. Começou de novo?"),
        ("msg", "kaua", "Calma. A Bel tá presa. Pode ter sido qualquer coisa.", dict(dig=0.4)),
        ("msg", "theo", "A filha dele falou que ele achou uma mochila escondida no celeiro. Com máscara.", dict(dig=0.4)),
        ("msg", "malu", "Então a Bel não tava sozinha mesmo."),
        ("chat", "ana", "10:30", "SÁBADO"),
        ("msg", "ana", "Malu, aqui é a Delegada Ana. Eu cuido do caso da chácara desde aquela noite.", dict(dig=0.4)),
        ("msg", "ana", "A mochila que o Seu Dito achou sumiu. Ele também.", dict(dig=0.4)),
        ("msg", "ana", "E hoje cedo o advogado da Bel trouxe um recado dela pra vocês três.", dict(dig=0.6)),
        ("msg", "malu", "Que recado?"),
        ("msg", "ana", "\"Ainda falta um.\"", dict(dig=0.8)),
        ("msg", "ana", "Vocês três não ficam sozinhos em hipótese nenhuma. Entendido?", dict(dig=0.4)),
        ("chat", "sobrev", "11:00", None),
        ("msg", "malu", "A delegada mandou ninguém ficar sozinho."),
        ("msg", "kaua", "Eu fico com você, Malu. O Theo mora longe.", dict(dig=0.3)),
        ("msg", "theo", "Eu moro a dez minutos dela, Kauã.", dict(dig=0.4)),
        ("chat", "mel", "23:33", "SÁBADO"),
        ("digitando", "assassino", 2.4),
        ("msg", "assassino", "Oi, Malu 🙂 Sentiu saudade?", dict(dig=0.4)),
        ("audio", "assassino", "O caseiro achou uma coisa que era minha. Agora ele não acha mais nada. Faltam vocês três.",
         dict(assobio=True, assobio_vol=0.25)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 3
    dict(parte=3, nome="Offline", eventos=[
        ("chat", "kaua", "09:00", "DOMINGO"),
        ("msg", "kaua", "Malu, eu não queria falar no grupo. Mas presta atenção numa coisa.", dict(dig=0.4)),
        ("msg", "kaua", "Toda vez que o celular da Mel manda mensagem, o Theo tá offline.", dict(dig=0.4)),
        ("msg", "kaua", "E naquela noite, ele foi o único que sobreviveu no milharal sem ninguém ver.", dict(dig=0.4)),
        ("msg", "malu", "O Theo foi atacado, Kauã. Ele ficou internado."),
        ("msg", "kaua", "Um corte no braço. Os outros morreram.", dict(dig=0.6)),
        ("msg", "kaua", "E quem vendeu a chácara rapidinho, antes de alguém olhar o celeiro direito?", dict(dig=0.6)),
        ("chat", "theo", "09:30", "DOMINGO"),
        ("msg", "malu", "Theo, onde você tava ontem às 23:33?"),
        ("msg", "theo", "Dormindo. Por quê?", dict(dig=0.4)),
        ("msg", "malu", "O celular da Mel me mandou mensagem bem nessa hora."),
        ("digitando", "theo", 2.4),
        ("msg", "theo", "Malu, você tá desconfiando de mim?", dict(dig=0.2)),
        ("msg", "theo", "Eu perdi a minha prima lá. Eu quase morri lá.", dict(dig=0.4)),
        ("msg", "theo", "Quem tá colocando isso na sua cabeça? O Kauã?", dict(dig=0.4)),
        ("rascunho", "Ele só falou que", 1.2),
        ("msg", "malu", "Desculpa, Theo. Eu não sei mais em quem confiar."),
        ("chat", "mel", "22:10", "DOMINGO"),
        ("digitando", "assassino", 2.0),
        ("foto", "assassino", estrada_noite, "Tô indo visitar o Theo. Avisa ele 🙂", dict(zoom=True, pausa=0.8, h_max=520)),
        ("chat", "theo", "22:11"),
        ("msg", "malu", "THEO, TRANCA A PORTA. ELE TÁ INDO AÍ."),
        ("pausa", 1.6),
        ("status", "visto por último hoje às 21:58"),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 4
    dict(parte=4, nome="Um ano", eventos=[
        ("chat", "theo", "06:40", "SEGUNDA", (("chip", "DOMINGO"), ("malu", "THEO, TRANCA A PORTA. ELE TÁ INDO AÍ.", "22:11"))),
        ("msg", "theo", "Malu, desculpa. Eu tava sem bateria. Ninguém veio aqui.", dict(dig=0.4)),
        ("msg", "theo", "Hoje faz um ano da Lara. Vai ter uma homenagem na represa às seis da tarde.", dict(dig=0.4)),
        ("msg", "theo", "Eu vou. Eu devo isso a ela.", dict(dig=0.6)),
        ("chat", "rubens", "12:00", "SEGUNDA"),
        ("msg", "rubens", "Você é a Malu? Eu sou o Rubens. Pai da Lara. E da Isabel.", dict(dig=0.6)),
        ("msg", "rubens", "Uma filha no fundo da represa e a outra na cadeia. Por causa de vocês.", dict(dig=0.6)),
        ("msg", "malu", "Seu Rubens, eu sinto muito. De verdade. Eu tava dormindo naquela noite."),
        ("msg", "rubens", "Todo mundo tava dormindo. Ninguém viu nada. Nem o namorado dela.", dict(dig=0.6)),
        ("msg", "malu", "Namorado? A Lara tinha namorado?"),
        ("msg", "rubens", "Escondido. Ela só chamava ele de \"K\". Dizia que era mais velho e da turma de vocês.", dict(dig=0.6)),
        ("chat", "sobrev", "18:10", "SEGUNDA"),
        ("foto", "theo", "cais_represa.jpg", "Cheguei. Tá todo mundo aqui no cais.", dict(pausa=0.6)),
        ("foto", "malu", "flor_branca.jpg", "Trouxe uma flor branca pra ela.", dict(pausa=0.6)),
        ("msg", "kaua", "Tô estacionando. Já chego.", dict(dig=0.4)),
        ("assobio", 4.0, 0.28),
        ("msg", "malu", "Theo... você tá ouvindo esse assobio no mato?"),
        ("msg", "theo", "Tô. Vou ver o que é.", dict(dig=0.3)),
        ("msg", "malu", "Theo, não vai sozinho!"),
        ("pausa", 2.0),
        ("msg", "kaua", "Malu! Achei o Theo caído perto das árvores! Bateram na cabeça dele. Tá respirando.", dict(dig=0.3)),
        ("msg", "kaua", "Chamei a ambulância. Fica aí no cais que eu cuido dele.", dict(dig=0.4)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 5
    dict(parte=5, nome="A rua", eventos=[
        ("chat", "ana", "21:00", "SEGUNDA"),
        ("msg", "malu", "Delegada, o Theo foi atacado na represa. O Kauã achou ele."),
        ("msg", "ana", "Eu sei. Ele tá no hospital, vai ficar bem.", dict(dig=0.4)),
        ("msg", "ana", "Malu, a gente conseguiu rastrear o celular da Mel. Ele só liga dois minutos e desliga.", dict(dig=0.4)),
        ("msg", "ana", "Mas ligou três vezes no mesmo lugar.", dict(dig=0.4)),
        ("foto", "ana", localizacao_mel, None, dict(zoom=True, pausa=3.2, h_max=560)),
        ("msg", "malu", "Rua das Palmeiras..."),
        ("msg", "malu", "Delegada. É a rua do Kauã."),
        ("msg", "ana", "Você tem certeza?", dict(dig=0.3)),
        ("msg", "malu", "Tenho. E tem outra coisa. Eu tô relendo a nossa conversa daquela noite."),
        ("foto", "malu", print_kaua, None, dict(zoom=True, pausa=4.0, h_max=680)),
        ("msg", "malu", "Ele disse que tava em casa, em São Paulo. E vinte minutos depois ele chegou na chácara."),
        ("msg", "malu", "São duas horas de estrada, delegada."),
        ("msg", "ana", "Ele já tava lá. O tempo todo.", dict(dig=0.6)),
        ("msg", "malu", "Kauã... com K. O namorado escondido da Lara."),
        ("chat", "kaua", "21:30", "SEGUNDA"),
        ("msg", "kaua", "Malu, já deixei o Theo no hospital. Quer que eu durma aí com você hoje? Ninguém fica sozinho 🙂",
         dict(dig=0.4)),
        ("rascunho", "Eu sei que foi você", 1.4),
        ("msg", "malu", "Não precisa, Kauã. A minha mãe tá aqui."),
        ("status", "visto por último hoje às 21:31"),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 6
    dict(parte=6, nome="K", eventos=[
        ("chat", "mel", "23:00", "SEGUNDA"),
        ("digitando", "assassino", 2.4),
        ("msg", "assassino", "A sua mãe não tá aí, Malu 🙂", dict(dig=0.4)),
        ("msg", "assassino", "Ela tá de plantão até as sete. Eu sei de tudo.", dict(dig=0.6)),
        ("msg", "malu", "Eu sei que é você, Kauã."),
        ("pausa", 2.0),
        ("chat", "kaua", "23:02"),
        ("audio", "kaua", "Demorou, hein. Eu namorava a Lara escondido. Naquela noite eu tava lá, do outro lado da represa. "
                          "Eu vi o Breno e o Theo desafiando ela. Vi a Isa filmando. Eu pulei na água e não achei ela."),
        ("audio", "kaua", "Aí eu achei a Bel. A gente planejou tudo junto. Quem desligou o wifi na noite da Mel fui eu. "
                          "O Breno no carro, o Theo no milharal, fui eu. E o caseiro achou a minha mochila."),
        ("msg", "malu", "E por que você me ajudou no celeiro?"),
        ("msg", "kaua", "Porque você não tava lá na represa. Você era a única que eu ia deixar viver.", dict(dig=0.6)),
        ("msg", "kaua", "Até você começar a contar os minutos.", dict(dig=0.6)),
        ("msg", "malu", "Cadê o Seu Dito, Kauã?"),
        ("msg", "kaua", "Me encontra no cais da represa. Amanhã, meia-noite. Sozinha.", dict(dig=0.6)),
        ("msg", "kaua", "Se a polícia aparecer, o Theo não sai do hospital. Eu sei o quarto dele.", dict(dig=0.6)),
        ("chat", "ana", "23:10", "SEGUNDA"),
        ("msg", "malu", "Delegada. Ele confessou tudo por áudio. E me chamou pro cais da represa amanhã à meia-noite."),
        ("msg", "ana", "Você não vai.", dict(dig=0.2)),
        ("msg", "malu", "Eu vou. É o único jeito de pegar ele. Coloca polícia no quarto do Theo e me espera escondida no mato."),
        ("digitando", "ana", 2.4),
        ("msg", "ana", "Tá. Mas você vai compartilhar a localização comigo o tempo todo.", dict(dig=0.2)),
        ("pausa", 2.4),
    ]),
    # ---------------------------------------------------------------------------------------------- 7
    dict(parte=7, nome="A represa", fim_texto="Fim", eventos=[
        ("chat", "ana", "23:50", "TERÇA"),
        ("msg", "malu", "Cheguei no cais. Localização ligada."),
        ("msg", "ana", "Estamos no mato, a vinte metros de você. O quarto do Theo tem dois policiais.", dict(dig=0.3)),
        ("chat", "kaua", "00:00", "QUARTA"),
        ("foto", "malu", cais_noite, "Tô aqui, Kauã. Sozinha.", dict(pausa=0.8)),
        ("assobio", 4.0, 0.3),
        ("msg", "kaua", "Tô te vendo 🙂", dict(dig=0.6)),
        ("msg", "malu", "Onde tá o Seu Dito?"),
        ("msg", "kaua", "Trancado na casa de bomba, do outro lado da represa. Vivo. Ainda.", dict(dig=0.6)),
        ("msg", "malu", "Por que você poupou ele?"),
        ("msg", "kaua", "Porque eu queria trocar ele por você 🙂", dict(dig=0.6)),
        ("chat", "ana", "00:03"),
        ("msg", "malu", "Ele falou que o Seu Dito tá vivo na casa de bomba, do outro lado. Ele tá vindo pelo cais."),
        ("msg", "ana", "Abaixa. AGORA.", dict(dig=0.1)),
        ("pausa", 2.6),
        ("msg", "ana", "Pegamos ele. Acabou, Malu.", dict(dig=0.4)),
        ("msg", "ana", "E a outra equipe achou o Seu Dito. Machucado, com frio, mas vivo.", dict(dig=0.6)),
        ("chat", "theo", "08:00", "QUARTA"),
        ("msg", "theo", "Malu. Os policiais me contaram tudo. Você é louca 😭", dict(dig=0.4)),
        ("msg", "malu", "Acabou, Theo. De verdade dessa vez."),
        ("msg", "theo", "Hoje eu vou na delegacia contar o que aconteceu com a Lara. Tudo. Do jeito que foi.", dict(dig=0.6)),
        ("msg", "malu", "Eu vou com você. E depois a gente leva flores pra ela na represa."),
        ("chat", "rubens", "18:00", "QUARTA"),
        ("msg", "rubens", "Malu. A delegada me contou da confissão do Theo. Agora eu sei o que aconteceu com a minha filha.",
         dict(dig=0.6)),
        ("msg", "rubens", "Obrigado por não ficar quieta.", dict(dig=0.6)),
        ("foto", "malu", "flor_branca.jpg", "Deixamos essa flor no cais pra ela, Seu Rubens. A Lara agora pode descansar.",
         dict(pausa=0.8)),
        ("pausa", 2.4),
    ]),
]
