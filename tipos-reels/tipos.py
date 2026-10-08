#!/usr/bin/env python3
"""Reels "Os 7 tipos de jogador que todo grupo tem": cada tipo é uma CARTA COLECIONÁVEL (estilo figurinha rara)
que sai de um pacotinho, vira e brilha (holográfico), com status, habilidade especial e o jogo do acervo "dele".

    python3 tipos.py --frame 3 10      # quadros de teste em out/frames.jpg
    python3 tipos.py --teste           # out/teste_cartas.jpg (as 7 cartas lado a lado)
"""
import argparse
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
HOBBY = os.path.join(REPO, "hobby-reels", "assets")
FN = os.path.join(HOBBY, "fonts")
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
LOGO = os.path.join(HOBBY, "logo_suavez.png")
W, H = 1080, 1920
WHITE = (255, 255, 255)
INK = (24, 20, 40)
CREME = (255, 248, 232)

# raridade → cor da moldura (degradê) e rótulo
RAR = {"COMUM": ((120, 200, 255), (40, 110, 220)), "RARO": ((150, 255, 170), (20, 150, 80)),
       "ÉPICO": ((230, 160, 255), (120, 40, 200)), "LENDÁRIO": ((255, 230, 120), (230, 120, 10))}

TIPOS = [
    dict(nome="O PROFESSOR", emoji="🤓", rar="ÉPICO", frase="Lê o manual INTEIRO em voz alta",
         stats=[("Paciência exigida", 10), ("Diversão nos 1ºs 40 min", 1), ("Conhecimento", 10)],
         hab="5 minutos de regra viram 1 hora de aula.", jogo="root", jogo_nome="Root"),
    dict(nome="O ANALISTA", emoji="🐢", rar="RARO", frase="Pensa 10 minutos por jogada",
         stats=[("Velocidade", 1), ("Estratégia", 10), ("Bocejos causados", 9)],
         hab="Até a ampulheta fica impaciente.", jogo="hive", jogo_nome="Hive"),
    dict(nome="O MAU PERDEDOR", emoji="😡", rar="ÉPICO", frase="Perdeu? O jogo é que tá roubado",
         stats=[("Espírito esportivo", 0), ("Pedidos de revanche", 10), ("Drama", 9)],
         hab="Joga de novo até ganhar.", jogo="flip_7_a_vingan_a", jogo_nome="Flip 7"),
    dict(nome="O TRAÍRA", emoji="🐍", rar="LENDÁRIO", frase="Jura aliança... e te apunhala",
         stats=[("Confiança", 0), ("Cara de inocente", 10), ("Amizades perdidas", 8)],
         hab="Muda de lado na rodada seguinte.", jogo="the_resistance", jogo_nome="The Resistance"),
    dict(nome="O SÓ MAIS UMA", emoji="🌙", rar="RARO", frase="Começou às 20h. São 3h da manhã",
         stats=[("Sono", 0), ("Energia", 10), ("Partidas por noite", 10)],
         hab="'Última, juro!' (não é a última).", jogo="king_of_tokyo", jogo_nome="King of Tokyo"),
    dict(nome="O SORTUDO", emoji="🍀", rar="LENDÁRIO", frase="Não entendeu a regra e ganhou",
         stats=[("Entendimento das regras", 2), ("Sorte", 10), ("Raiva que causa", 10)],
         hab="Ganha sem saber como.", jogo="camel_up_second_edition", jogo_nome="Camel Up"),
    dict(nome="O 'É MINHA VEZ?'", emoji="📱", rar="COMUM", frase="Tava no celular e perdeu a vez",
         stats=[("Atenção", 1), ("Tempo de tela", 10), ("'De quem é a vez?'", 10)],
         hab="Pergunta de quem é a vez. De novo.", jogo="dixit", jogo_nome="Dixit"),
]


def font(n, s):
    return ImageFont.truetype(os.path.join(FN, n), int(s))


def emoji(ch, size):
    f = ImageFont.truetype(EMOJI, 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    return im.resize((size, int(im.height * size / im.width)), Image.LANCZOS)


def caixa(nome, h):
    p = os.path.join(HOBBY, "caixas", nome + ".png")
    if not os.path.exists(p):
        p = os.path.join(HOBBY, "acervo", nome + ".png")
    im = Image.open(p).convert("RGBA")
    return im.resize((int(im.width * h / im.height), int(h)), Image.LANCZOS)


def degrade(w, h, c1, c2, vertical=True):
    t = np.linspace(0, 1, h if vertical else w)
    t = t[:, None] if vertical else t[None, :]
    a = np.array(c1)[None, None] * (1 - t[..., None]) + np.array(c2)[None, None] * t[..., None]
    a = np.broadcast_to(a, (h, w, 3))
    return Image.fromarray(a.astype(np.uint8), "RGB")


def texto_quebrado(d, txt, f, largura):
    linhas, atual = [], ""
    for p in txt.split():
        t = (atual + " " + p).strip()
        if d.textlength(t, font=f) > largura and atual:
            linhas.append(atual)
            atual = p
        else:
            atual = t
    return linhas + [atual]


def carta(k, holo=0.0):
    """Carta colecionável do tipo k (800x1140, RGBA). holo = posição do brilho holográfico (0..1)."""
    tp = TIPOS[k]
    cw, ch, r = 800, 1140, 46
    c1, c2 = RAR[tp["rar"]]
    out = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    m = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, cw - 1, ch - 1), radius=r, fill=255)
    moldura = degrade(cw, ch, c1, c2).convert("RGBA")
    out.paste(moldura, (0, 0), m)
    d = ImageDraw.Draw(out)
    # miolo creme
    pad = 26
    d.rounded_rectangle((pad, pad, cw - pad, ch - pad), radius=r - 16, fill=CREME)
    # faixa do nome
    d.rounded_rectangle((pad + 14, pad + 14, cw - pad - 14, pad + 124), radius=24, fill=INK)
    fn = font("Bungee-Regular.ttf", 62)
    while d.textlength(tp["nome"], font=fn) > cw - 2 * pad - 80:
        fn = font("Bungee-Regular.ttf", fn.size - 2)
    d.text((cw / 2, pad + 70), tp["nome"], font=fn, fill=WHITE, anchor="mm")
    # janela da ilustração: degradê da raridade + raios + emoji gigante
    jx0, jy0, jx1, jy1 = pad + 14, pad + 140, cw - pad - 14, pad + 500
    jw, jh = jx1 - jx0, jy1 - jy0
    jan = degrade(jw, jh, tuple(min(255, v + 40) for v in c1), c2).convert("RGBA")
    rd = ImageDraw.Draw(jan)
    for i in range(18):  # raios de sol
        a0 = i * 2 * math.pi / 18
        rd.polygon([(jw / 2, jh / 2), (jw / 2 + 900 * math.cos(a0), jh / 2 + 900 * math.sin(a0)),
                    (jw / 2 + 900 * math.cos(a0 + 0.17), jh / 2 + 900 * math.sin(a0 + 0.17))], fill=(255, 255, 255, 40))
    em = emoji(tp["emoji"], 290)
    sh = Image.new("RGBA", em.size, (0, 0, 0, 0))
    sh.putalpha(em.getchannel("A").point(lambda v: int(v * 0.35)))
    jan.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), (jw // 2 - em.width // 2 + 10, jh // 2 - em.height // 2 + 16))
    jan.alpha_composite(em, (jw // 2 - em.width // 2, jh // 2 - em.height // 2))
    mj = Image.new("L", (jw, jh), 0)
    ImageDraw.Draw(mj).rounded_rectangle((0, 0, jw - 1, jh - 1), radius=22, fill=255)
    out.paste(jan, (jx0, jy0), mj)
    d.rounded_rectangle((jx0, jy0, jx1, jy1), radius=22, outline=INK, width=5)
    # selo de raridade
    fr = font("Bungee-Regular.ttf", 30)
    tw = d.textlength(tp["rar"], font=fr)
    d.rounded_rectangle((cw / 2 - tw / 2 - 26, jy1 - 26, cw / 2 + tw / 2 + 26, jy1 + 26), radius=26, fill=c2,
                        outline=WHITE, width=4)
    d.text((cw / 2, jy1 + 1), tp["rar"], font=fr, fill=WHITE, anchor="mm")
    # frase
    ff = font("Poppins-ExtraBold.ttf", 38)
    d.text((cw / 2, jy1 + 72), tp["frase"], font=ff, fill=INK, anchor="mm")
    # status
    fs = font("Poppins-SemiBold.ttf", 29)
    y = jy1 + 122
    for nome, v in tp["stats"]:
        d.text((pad + 40, y + 20), nome.upper(), font=fs, fill=INK, anchor="lm")
        bx0 = cw - pad - 40 - 10 * 25
        for i in range(10):
            on = i < v
            d.rounded_rectangle((bx0 + i * 25, y + 6, bx0 + i * 25 + 19, y + 34), radius=5,
                                fill=c2 if on else (225, 218, 205))
        y += 52
    # habilidade
    y += 8
    d.rounded_rectangle((pad + 30, y, cw - pad - 30, y + 140), radius=18, fill=(255, 236, 200), outline=c2, width=4)
    d.text((pad + 52, y + 26), "HABILIDADE ESPECIAL", font=font("Bungee-Regular.ttf", 24), fill=c2, anchor="lm")
    fh = font("Poppins-ExtraBold.ttf", 31)
    for i, l in enumerate(texto_quebrado(d, tp["hab"], fh, cw - 2 * pad - 110)[:2]):
        d.text((pad + 52, y + 68 + i * 38), l, font=fh, fill=INK, anchor="lm")
    # jogo dele
    y = ch - pad - 150
    d.line((pad + 30, y - 6, cw - pad - 30, y - 6), fill=(215, 205, 190), width=3)
    cx = caixa(tp["jogo"], 128)
    out.alpha_composite(cx, (cw - pad - 50 - cx.width, y + 6))
    d.text((pad + 44, y + 40), "JOGO FAVORITO:", font=font("Bungee-Regular.ttf", 26), fill=(150, 130, 110), anchor="lm")
    d.text((pad + 44, y + 92), tp["jogo_nome"], font=font("Poppins-Black.ttf", 46), fill=INK, anchor="lm")
    # brilho holográfico (faixa diagonal arco-íris que atravessa a carta)
    if holo > 0:
        hol = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        hd = ImageDraw.Draw(hol)
        x = -400 + holo * (cw + 800)
        cores = [(255, 120, 200), (255, 230, 120), (120, 255, 200), (120, 180, 255)]
        for i, c in enumerate(cores):
            hd.polygon([(x + i * 40, 0), (x + i * 40 + 40, 0), (x + i * 40 + 40 - 500, ch), (x + i * 40 - 500, ch)],
                       fill=c + (60,))
        hol = hol.filter(ImageFilter.GaussianBlur(18))
        a = np.minimum(np.asarray(hol.getchannel("A")), np.asarray(m))
        hol.putalpha(Image.fromarray(a.astype(np.uint8)))
        out.alpha_composite(hol)
    return out


def fundo(t=0.0, cor=(70, 30, 140)):
    """Fundo: degradê roxo-noite com bolinhas de luz desfocadas (bokeh) subindo devagar."""
    img = degrade(W, H, tuple(int(v * 0.55) for v in cor), (10, 8, 24)).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    rng = np.random.default_rng(7)
    for _ in range(26):
        x, y0, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(20, 90)
        y = (y0 - t * rng.uniform(15, 40)) % (H + 200) - 100
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 220, 255, int(rng.uniform(14, 40))))
    img.alpha_composite(ov.filter(ImageFilter.GaussianBlur(14)))
    return img


def sombra(im, blur=26, off=(0, 30), a=0.5):
    s = Image.new("RGBA", (im.width + blur * 4, im.height + blur * 4), (0, 0, 0, 0))
    sa = Image.new("RGBA", im.size, (0, 0, 0, 255))
    sa.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    s.alpha_composite(sa, (blur * 2 + off[0], blur * 2 + off[1]))
    s = s.filter(ImageFilter.GaussianBlur(blur))
    s.alpha_composite(im, (blur * 2, blur * 2))
    return s


def logo(img, w=170):
    lg = Image.open(LOGO).convert("RGBA")
    lg = lg.resize((w, int(lg.height * w / lg.width)), Image.LANCZOS)
    card = Image.new("RGBA", (lg.width + 24, lg.height + 20), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=16, fill=WHITE)
    card.alpha_composite(lg, (12, 10))
    img.alpha_composite(card, (W - card.width - 30, 40))


def quadro_teste(k, holo, gancho=False):
    img = fundo(k * 3.0, RAR[TIPOS[k]["rar"]][1])
    d = ImageDraw.Draw(img)
    if gancho:
        d.text((540, 300), "TODO GRUPO TEM", font=font("Bungee-Regular.ttf", 84), fill=WHITE, anchor="mm")
        d.text((540, 420), "ESSES 7 TIPOS", font=font("Bungee-Regular.ttf", 110), fill=(255, 220, 90), anchor="mm")
        d.text((500, 530), "marca quem é quem", font=font("Poppins-ExtraBold.ttf", 54), fill=WHITE, anchor="mm")
        img.alpha_composite(emoji("👇", 64), (830, 495))
        # leque de cartas
        for i, (kk, rot, x, y) in enumerate(((1, 14, 300, 1180), (5, -14, 780, 1180), (3, 0, 540, 1120))):
            c = carta(kk, 0).resize((480, 684), Image.LANCZOS).rotate(rot, expand=True, resample=Image.BICUBIC)
            c = sombra(c)
            img.alpha_composite(c, (int(x - c.width / 2), int(y - c.height / 2)))
    else:
        d.rounded_rectangle((60, 60, 330, 140), radius=40, fill=(0, 0, 0, 120))
        d.text((195, 100), f"TIPO {k + 1}/7", font=font("Bungee-Regular.ttf", 44), fill=WHITE, anchor="mm")
        c = sombra(carta(k, holo).resize((760, 1083), Image.LANCZOS))
        img.alpha_composite(c, (540 - c.width // 2, 880 - c.height // 2))
    logo(img)
    return img


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--teste", action="store_true")
    a = ap.parse_args()
    ims = [quadro_teste(3, 0, True), quadro_teste(0, 0.55), quadro_teste(3, 0.3)]
    sheet = Image.new("RGB", (3 * 540 + 40, 980), (20, 20, 20))
    for k, im in enumerate(ims):
        sheet.paste(im.convert("RGB").resize((540, 960), Image.LANCZOS), (10 + k * 550, 10))
    sheet.save(os.path.join(ROOT, "out", "teste_tipos.jpg"), quality=90)
    print("ok")
