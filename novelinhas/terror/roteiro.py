"""3:33: novela de terror em 5 partes do Compartilhado (WhatsApp no modo escuro).

A Júlia mora sozinha na casa da avó, a Vó Cida, que morreu há 10 dias e foi enterrada com o celular.
Toda noite, às 3h33, chegam mensagens do número dela avisando sobre "o homem no sótão". Um homem vivia
escondido lá em cima, e foi preso. Mas a polícia nunca achou o celular da avó. E alguém ainda não terminou.
"""
import functools
import os
import random

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

FOTOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fotos")
TITULO = "3:33"
TEMA = "escuro"
TRILHA = "terror"

FRANCISCA = ("pt-BR-FranciscaNeural", "+0%", "+0Hz")
BRIAN = ("en-US-BrianMultilingualNeural", "+0%", "+0Hz")
VOZES = {"julia": FRANCISCA, "cida": FRANCISCA, "davi": BRIAN, "estranho": BRIAN}

PERSONAGENS = {
    "julia": dict(nome="Júlia", cor=(126, 87, 194)),
    "cida": dict(nome="Vó Cida", cor=(255, 179, 0)),
    "davi": dict(nome="Davi", cor=(38, 166, 154)),
    "estranho": dict(nome="?", cor=(80, 80, 80)),
}

CHATS = {
    "cida": dict(dono="julia", titulo="Vó Cida 🌻", com="cida", sub="visto por último há 10 dias"),
    "davi": dict(dono="julia", titulo="Davi (primo)", com="davi", sub="online"),
    "estranho": dict(dono="julia", titulo="+55 11 90000-0333", com="estranho", sub=""),
}


def _assombrar(nome, brilho=0.45, seed=1):
    """Escurece, esverdeia e põe granulado: cara de foto tirada no escuro."""
    im = Image.open(os.path.join(FOTOS, nome)).convert("RGB")
    im.thumbnail((900, 900))
    im = ImageEnhance.Brightness(im).enhance(brilho)
    im = ImageEnhance.Color(im).enhance(0.35)
    px = im.load()
    rnd = random.Random(seed)
    for _ in range(im.width * im.height // 6):
        x, y = rnd.randrange(im.width), rnd.randrange(im.height)
        r, g, b = px[x, y]
        k = rnd.randint(-28, 28)
        px[x, y] = (max(0, min(255, r + k)), max(0, min(255, g + k + 6)), max(0, min(255, b + k)))
    return im.filter(ImageFilter.GaussianBlur(0.6))


@functools.lru_cache(None)
def foto_dormindo():
    """A foto da Júlia dormindo, tirada do corredor."""
    im = _assombrar("corredor.jpg", 0.55, 3)
    d = ImageDraw.Draw(im)
    # silhueta da cama e de alguém deitado, no fundo do quarto
    w, h = im.size
    d.rectangle((w * 0.55, h * 0.62, w * 0.92, h * 0.80), fill=(38, 40, 38))
    d.ellipse((w * 0.57, h * 0.56, w * 0.64, h * 0.66), fill=(60, 62, 58))
    d.rectangle((w * 0.62, h * 0.60, w * 0.90, h * 0.66), fill=(70, 72, 66))
    return im.filter(ImageFilter.GaussianBlur(1.0))


@functools.lru_cache(None)
def foto_alcapao():
    return _assombrar("alcapao.jpg", 0.5, 7)


EPISODIOS = [
    # ---------------------------------------------------------------------------------------------- 1
    dict(parte=1, nome="3:33", eventos=[
        ("chat", "davi", "23:10", "HOJE"),
        ("msg", "julia", "Primeira noite sozinha na casa da vó. Tá tudo tão quieto."),
        ("msg", "davi", "Quer que eu durma aí?", dict(dig=0.6)),
        ("msg", "julia", "Não precisa. Mas é estranho... ainda sinto o cheiro do café dela."),
        ("msg", "davi", "Ela ia gostar de saber que você ficou com a casa 🌻"),
        ("chat", "cida", "03:33", None, (("chip", "11 DIAS ATRÁS"), ("cida", "Filha, vem almoçar domingo? Fiz bolo de fubá 🌻", "10:12"),
                                         ("julia", "Vou sim, vó! Te amo ❤️", "10:40"), ("chip", "HOJE"))),
        ("pausa", 1.2),
        ("msg", "cida", "Júlia", dict(dig=2.0)),
        ("msg", "cida", "Não dorme de luz apagada.", dict(dig=1.6)),
        ("pausa", 1.0),
        ("msg", "julia", "Vó?"),
        ("msg", "julia", "Quem tá usando o número da minha avó?"),
        ("digitando", "cida", 3.0),
        ("pausa", 1.2),
        ("chat", "davi", "03:40", "HOJE"),
        ("msg", "julia", "Davi, acorda. Mandaram mensagem do número da vó."),
        ("msg", "davi", "Júlia, são quase quatro da manhã...", dict(dig=1.0)),
        ("msg", "julia", "Não dorme de luz apagada.", dict(enc=True)),
        ("msg", "davi", "Deve ser a operadora. Quando cancela a linha, o número vai pra outra pessoa."),
        ("msg", "julia", "Em dez dias? E como essa pessoa sabe o meu nome?"),
        ("msg", "davi", "Trote, prima. Gente sem noção. Tenta dormir."),
        ("msg", "julia", "Vou deixar a luz acesa."),
        ("chat", "cida", "03:52"),
        ("pausa", 1.0),
        ("msg", "cida", "Boa menina 🌻", dict(dig=2.4)),
        ("pausa", 2.6),
    ]),
    # ---------------------------------------------------------------------------------------------- 2
    dict(parte=2, nome="A cantiga", eventos=[
        ("chat", "cida", "03:33", "HOJE", (("chip", "ONTEM"), ("cida", "Júlia", "03:33"), ("cida", "Não dorme de luz apagada.", "03:33"),
                                           ("julia", "Quem tá usando o número da minha avó?", "03:34"), ("cida", "Boa menina 🌻", "03:52"))),
        ("pausa", 1.0),
        ("audio", "cida", "Nana, neném, que a Cuca vem pegar... Papai foi pra roça, mamãe foi trabalhar...", dict(efeito="fantasma")),
        ("msg", "julia", "Essa era a música que ela cantava pra eu dormir..."),
        ("msg", "julia", "Para com isso. Não tem graça nenhuma."),
        ("digitando", "cida", 2.4),
        ("foto", "cida", foto_dormindo, "Você dorme tão bonitinha.", dict(zoom=True, pausa=1.2, h_max=600)),
        ("msg", "julia", "QUEM TÁ NA MINHA CASA??"),
        ("msg", "cida", "Fica no quarto.", dict(dig=1.6)),
        ("chat", "davi", "03:40", "HOJE"),
        ("msg", "julia", "Davi. Tem uma foto minha dormindo. Tirada do corredor. HOJE."),
        ("msg", "davi", "Júlia... isso não é trote.", dict(dig=1.0)),
        ("msg", "davi", "E tem uma coisa que eu não te contei."),
        ("msg", "davi", "O celular da vó foi enterrado com ela. Ela pediu. Eu mesmo coloquei no caixão."),
        ("msg", "julia", "Então quem tá mandando essas mensagens??"),
        ("msg", "davi", "Tranca a porta do quarto. Tô indo aí agora."),
        ("msg", "davi", "Trancou a janela também?"),
        ("msg", "julia", "Tranquei tudo. Vem rápido."),
        ("msg", "davi", "Vinte minutos. Não desliga o celular."),
        ("msg", "julia", "Tô ouvindo um rangido no corredor."),
        ("msg", "davi", "Já tô no carro. Fica quietinha.", dict(dig=0.6)),
        ("pausa", 2.6),
    ]),
    # ---------------------------------------------------------------------------------------------- 3
    dict(parte=3, nome="Linha cancelada", eventos=[
        ("chat", "davi", "09:00", "HOJE", (("chip", "ONTEM"), ("davi", "Tranca a porta do quarto. Tô indo aí agora.", "03:41"))),
        ("msg", "davi", "Liguei na operadora."),
        ("msg", "davi", "A linha da vó foi cancelada no dia seguinte ao enterro. Há nove dias."),
        ("msg", "julia", "Então como chega mensagem?"),
        ("msg", "davi", "Eles disseram que é impossível."),
        ("msg", "julia", "Você dormiu aqui. Não ouviu nada?"),
        ("msg", "davi", "Nada. Mas a porta do sótão tava aberta hoje cedo. E eu tenho certeza que ontem tava fechada.", dict(dig=0.8)),
        ("msg", "julia", "A vó nunca deixava ninguém subir no sótão."),
        ("msg", "davi", "Eu subi a escada até a metade. Tinha um cheiro... de comida."),
        ("msg", "julia", "Comida??"),
        ("msg", "davi", "Sei lá. Deve ser rato. Hoje eu durmo aí de novo."),
        ("chat", "cida", "03:33", "HOJE"),
        ("pausa", 1.2),
        ("msg", "cida", "Júlia.", dict(dig=2.0)),
        ("msg", "cida", "Ele tá no sótão.", dict(dig=1.6)),
        ("msg", "julia", "Quem??"),
        ("digitando", "cida", 3.0),
        ("msg", "cida", "O homem que dorme em cima do seu quarto.", dict(dig=0.3)),
        ("audio", "cida", "Eu sempre tranquei o sótão, minha flor. Agora não tem mais ninguém pra trancar.", dict(efeito="fantasma")),
        ("msg", "julia", "Vó? Se for você... me diz o que eu faço."),
        ("msg", "cida", "Acorda o Davi.", dict(dig=2.0)),
        ("pausa", 2.6),
    ]),
    # ---------------------------------------------------------------------------------------------- 4
    dict(parte=4, nome="O sótão", eventos=[
        ("chat", "davi", "03:36", "HOJE"),
        ("msg", "julia", "Davi, você tá acordado? Tá aí na sala?"),
        ("msg", "davi", "Tô. Acordei com um barulho.", dict(dig=0.6)),
        ("msg", "julia", "DAVI. Ela disse que tem alguém no sótão."),
        ("msg", "davi", "Eu tô ouvindo.", dict(dig=0.6)),
        ("msg", "davi", "Passos. Em cima do seu quarto."),
        ("msg", "davi", "Agora parece que tão arrastando alguma coisa."),
        ("msg", "julia", "Davi, eu tô com muito medo."),
        ("msg", "julia", "Não sobe!!"),
        ("foto", "davi", foto_alcapao, "O alçapão tá trancado. Por DENTRO.", dict(zoom=True, pausa=1.0, h_max=640, w=520)),
        ("msg", "julia", "Liga pra polícia!"),
        ("msg", "davi", "Já liguei. Eu vou esperar a viatura na rua. Fica trancada no quarto."),
        ("chat", "cida", "03:47"),
        ("msg", "cida", "Não abre a porta do quarto.", dict(dig=1.4)),
        ("msg", "julia", "Tem alguém batendo na porta do meu quarto agora."),
        ("msg", "julia", "É o Davi?"),
        ("digitando", "cida", 2.6),
        ("msg", "cida", "Porque não é o Davi que tá batendo.", dict(dig=0.3)),
        ("pausa", 1.2),
        ("chat", "davi", "03:48"),
        ("msg", "julia", "Davi, você tá batendo na porta do meu quarto?"),
        ("digitando", "davi", 1.8),
        ("msg", "davi", "Não. Eu tô na rua, Júlia.", dict(dig=0.3)),
        ("msg", "julia", "Ele tá mexendo na maçaneta."),
        ("msg", "julia", "Davi, corre.", dict(pausa=0.8)),
        ("pausa", 2.6),
    ]),
    # ---------------------------------------------------------------------------------------------- 5
    dict(parte=5, nome="A última mensagem", fim_texto="Fim?", eventos=[
        ("chat", "davi", "03:50", None, (("chip", "HOJE"), ("julia", "Davi, você tá batendo na porta do meu quarto?", "03:48"),
                                         ("davi", "Não. Eu tô na rua, Júlia.", "03:48"))),
        ("msg", "davi", "A polícia chegou! Tão subindo!", dict(dig=0.4)),
        ("msg", "julia", "Ele parou de bater."),
        ("msg", "julia", "Davi, vem pra cá. Eu não quero ficar sozinha."),
        ("msg", "davi", "Tô subindo.", dict(dig=0.4)),
        ("hora", "05:10"),
        ("chip", "05:10"),
        ("msg", "davi", "Pegaram ele. Um homem. Tava morando no sótão fazia meses.", dict(hora="05:10")),
        ("msg", "davi", "Tinha colchão, comida, uma câmera. Ele entrava pelo telhado. Foi ele que tirou aquela foto sua.", dict(hora="05:10")),
        ("msg", "davi", "Ele tinha fotos suas dormindo. De várias noites.", dict(hora="05:10")),
        ("msg", "julia", "Que horror...", dict(hora="05:11")),
        ("msg", "julia", "E as mensagens? Ele tava com o celular da vó?", dict(hora="05:11")),
        ("msg", "davi", "Não. A polícia revistou tudo. Nenhum celular.", dict(hora="05:11")),
        ("audio", "davi", "Júlia... o policial perguntou como a gente soube que tinha alguém lá em cima. Eu não soube o que responder.",
         dict(hora="05:12")),
        ("chat", "cida", "03:33", "HOJE"),
        ("pausa", 1.2),
        ("msg", "cida", "Agora você tá segura.", dict(dig=2.0)),
        ("msg", "cida", "Te amo, minha flor 🌻", dict(dig=1.6)),
        ("msg", "julia", "Te amo, vó ❤️"),
        ("chat", "estranho", "03:34"),
        ("pausa", 0.8),
        ("msg", "estranho", "Ela não era a única aqui.", dict(dig=2.4)),
        ("msg", "julia", "Quem é?"),
        ("digitando", "estranho", 2.4),
        ("pausa", 2.6),
    ]),
]
