#!/usr/bin/env python3
"""3 visuais NOVOS para o carrossel de séries (12/nov/2026; ele não gostou do app de streaming). Tela de teste com a
Wandinha → Paranormal Detectives em cada conceito:

  1 DEU MATCH: app de namoro. Perfil do personagem (emoji, idade, bio "gosta de...") e "É UM MATCH!" com o jogo.
  2 RG DO JOGADOR: carteira de identidade verde em cima da mesa de madeira, com foto (emoji), campos preenchidos à
    mão, "JOGO FAVORITO" e carimbo "APROVADO"; a caixa do jogo presa com clipe.
  3 PERFIL DO INSTAGRAM: o perfil do personagem (@), bio e o último post = foto do jogo, curtido por outro personagem,
    com legenda e comentários.

    /usr/bin/python3 series_conceitos.py   # out/series_conceitos.jpg
"""
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import personagens as P  # noqa: E402

E = P.E
W, H = P.W, P.H
CAIXA = os.path.join(P.AC, "paranormal_detectives.png")
FONTE_MAO = os.path.join(P.REPO, "taco-reels", "assets", "fonts")


def centro(img, im, cx, y):
    img.alpha_composite(im, (int(cx - im.width / 2), int(y)))


def match():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    for y in range(H):  # degradê rosa → laranja
        t = y / H
        d.line((0, y, W, y), fill=(int(240 - 10 * t), int(80 + 60 * t), int(120 - 60 * t)))
    lg = E.logo(150)
    img.alpha_composite(lg, (40, 36))
    d.text((W - 50, 36 + lg.height // 2), "MATCH", font=E.lilita(44), fill=(255, 255, 255), anchor="rm")
    # cartão do perfil
    cw, ch = 900, 520
    c = E.bloco(cw, ch, (255, 255, 255), raio=40, ow=0, sombra=0)
    dc = ImageDraw.Draw(c)
    dc.rounded_rectangle((24, 24, cw - 24, 330), radius=28, fill=(40, 30, 46))
    e = P.emoji("🖤", 200)
    c.alpha_composite(e, ((cw - e.width) // 2, 60))
    dc.text((44, 360), "Wandinha, 16", font=E.lilita(62), fill=(30, 30, 30))
    dc.text((44, 440), "Nunca Mais · gosta de: fantasmas,", font=E.fig(30, 600), fill=(90, 90, 100))
    dc.text((44, 478), "mistério e silêncio absoluto", font=E.fig(30, 600), fill=(90, 90, 100))
    img.alpha_composite(c, ((W - cw) // 2, 190))
    t = E.titulo("É UM MATCH!", 110, cor=(255, 255, 255), contorno=(200, 40, 90))
    centro(img, t, W / 2, 740)
    cx = E.jogo(CAIXA, 250, larg=300)
    centro(img, cx, W / 2, 880)
    tn = E.texto("Paranormal Detectives  ·  2 a 6 jogadores  ·  R$ 30", 32, cor=(255, 255, 255), peso=800)
    centro(img, tn, W / 2, 1150)
    for x, em in [(W // 2 - 140, "❌"), (W // 2 + 140, "❤️")]:
        d.ellipse((x - 56, 1215, x + 56, 1327), fill=(255, 255, 255))
        e2 = P.emoji(em, 60)
        img.alpha_composite(e2, (x - e2.width // 2, 1271 - e2.height // 2))
    return img


def rg():
    img = Image.new("RGBA", (W, H), (150, 100, 62, 255))
    d = ImageDraw.Draw(img)
    rnd = random.Random(2)
    for y in range(0, H, 3):  # mesa de madeira
        v = int(10 * rnd.random())
        d.line((0, y, W, y), fill=(150 - v, 100 - v, 62 - v // 2))
    cw, ch = 940, 640
    c = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    dc = ImageDraw.Draw(c)
    dc.rounded_rectangle((0, 0, cw - 1, ch - 1), radius=26, fill=(196, 222, 186), outline=(90, 130, 90), width=4)
    for y in range(20, ch, 14):  # guilhoché
        dc.line((20, y, cw - 20, y + 6), fill=(184, 212, 174), width=2)
    dc.text((cw // 2, 40), "REPÚBLICA DOS JOGOS DE TABULEIRO", font=E.fig(28, 900), fill=(40, 80, 50), anchor="mm")
    dc.text((cw // 2, 76), "CARTEIRA DE IDENTIDADE DE JOGADOR", font=E.fig(24, 700), fill=(40, 80, 50), anchor="mm")
    dc.rectangle((40, 120, 300, 440), fill=(236, 236, 230), outline=(90, 130, 90), width=3)
    e = P.emoji("🖤", 170)
    c.alpha_composite(e, (170 - e.width // 2, 200))
    mao = E.ImageFont.truetype(os.path.join(FONTE_MAO, "Kalam-Bold.ttf"), 44) if hasattr(E, "ImageFont") else None
    from PIL import ImageFont
    mao = ImageFont.truetype(os.path.join(FONTE_MAO, "Kalam-Bold.ttf"), 46)
    campos = [("NOME", "Wandinha Addams"), ("SÉRIE", "Wandinha"), ("ESTILO DE JOGO", "não sorri nem quando ganha"),
              ("JOGO FAVORITO", "Paranormal Detectives")]
    y = 120
    for k, v in campos:
        dc.text((330, y), k, font=E.fig(22, 900), fill=(60, 100, 70))
        dc.text((330, y + 22), v, font=mao, fill=(30, 40, 90) if k != "JOGO FAVORITO" else (190, 40, 40))
        y += 86
    dc.line((60, 560, 420, 545), fill=(30, 40, 90), width=3)  # assinatura
    dc.text((60, 570), "ASSINATURA DO TITULAR", font=E.fig(18, 800), fill=(60, 100, 70))
    c = c.rotate(-3, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(E.bloco(c.width - 20, c.height - 20, (0, 0, 0, 0), raio=26, ow=0, sombra=0), (0, 0))
    sh = Image.new("RGBA", c.size, (0, 0, 0, 0))
    sh.putalpha(c.getchannel("A").point(lambda v: int(v * 0.4)))
    sh = sh.filter(ImageFilter.GaussianBlur(12))
    img.alpha_composite(sh, (78, 228))
    img.alpha_composite(c, (60, 210))
    # carimbo
    ca = Image.new("RGBA", (360, 140), (0, 0, 0, 0))
    dca = ImageDraw.Draw(ca)
    dca.rounded_rectangle((4, 4, 356, 136), radius=16, outline=(200, 40, 40, 220), width=8)
    dca.text((180, 70), "APROVADO", font=E.lilita(70), fill=(200, 40, 40, 220), anchor="mm")
    ca = ca.rotate(14, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(ca, (640, 640))
    cx = E.jogo(CAIXA, 360, larg=420).rotate(6, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(cx, (90, 900))
    t = E.titulo("RG DA\nWANDINHA", 86, cor=(255, 255, 255), larg_max=520)
    img.alpha_composite(t, (560, 960))
    lg = E.logo(150)
    img.alpha_composite(lg, (W - lg.width - 40, 40))
    t0 = E.titulo("QUE JOGO ELA JOGARIA?", 64, cor=E.AMARELO, larg_max=W - 260)
    img.alpha_composite(t0, (40, 60))
    return img


def perfil():
    img = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    d = ImageDraw.Draw(img)
    f = E.fig
    d.text((50, 50), "wandinha.addams", font=f(42, 900), fill=(20, 20, 20))
    # avatar com anel
    cx, cy, r = 150, 230, 96
    for k, cor in enumerate([(250, 160, 60), (230, 60, 120), (150, 60, 200)]):
        pass
    d.ellipse((cx - r - 10, cy - r - 10, cx + r + 10, cy + r + 10), fill=(230, 70, 130))
    d.ellipse((cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3), fill=(255, 255, 255))
    d.ellipse((cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4), fill=(40, 30, 46))
    e = P.emoji("🖤", 110)
    img.alpha_composite(e, (cx - e.width // 2, cy - e.height // 2))
    for i, (n, l) in enumerate([("1", "post"), ("13", "seguidores"), ("0", "seguindo")]):
        x = 420 + i * 220
        d.text((x, 200), n, font=f(44, 900), fill=(20, 20, 20), anchor="mm")
        d.text((x, 248), l, font=f(28, 600), fill=(20, 20, 20), anchor="mm")
    d.text((50, 350), "Wandinha", font=f(32, 900), fill=(20, 20, 20))
    d.text((50, 392), "não sorrio. jogo. · Nunca Mais", font=f(30, 500), fill=(20, 20, 20))
    d.line((0, 450, W, 450), fill=(220, 220, 220), width=2)
    # post
    py, ph = 470, 560
    bg = Image.open(CAIXA).convert("RGBA").resize((W, ph)).filter(ImageFilter.GaussianBlur(30))
    img.alpha_composite(bg, (0, py))
    cxx = E.jogo(CAIXA, 470, larg=560)
    centro(img, cxx, W / 2, py + (ph - cxx.height) // 2)
    y = py + ph + 20
    for i, em in enumerate(["🤍", "💬", "✈️"]):
        e3 = P.emoji(em, 48)
        img.alpha_composite(e3, (50 + i * 80, y + 4))
    y += 70
    d.text((50, y), "Curtido por eleven e outras pessoas", font=f(30, 700), fill=(20, 20, 20))
    y += 46
    d.text((50, y), "wandinha.addams", font=f(30, 900), fill=(20, 20, 20))
    w0 = d.textlength("wandinha.addams ", font=f(30, 900))
    d.text((50 + w0, y), "sexta à noite: Paranormal Detectives.", font=f(30, 500), fill=(20, 20, 20))
    y += 42
    d.text((50, y), "Os fantasmas falam comigo. Vocês não.", font=f(30, 500), fill=(20, 20, 20))
    y += 52
    d.text((50, y), "suavez_bg  aluga na Sua Vez, link na bio!", font=f(28, 600), fill=(120, 120, 120))
    lg = E.logo(130)
    img.alpha_composite(lg, (W - lg.width - 40, 330))
    return img


def main():
    ims = [match(), rg(), perfil()]
    f = Image.new("RGB", (3 * W + 80, H + 120), (255, 255, 255))
    d = ImageDraw.Draw(f)
    for i, (im, nome) in enumerate(zip(ims, ["1  DEU MATCH", "2  RG DO JOGADOR", "3  PERFIL DO INSTAGRAM"])):
        f.paste(im.convert("RGB"), (i * (W + 40), 120))
        d.text((i * (W + 40) + W // 2, 60), nome, font=E.lilita(70), fill=E.MARROM, anchor="mm")
    f.resize((f.width // 2, f.height // 2), Image.LANCZOS).save(os.path.join(ROOT, "out", "series_conceitos.jpg"),
                                                                 quality=90)
    print("ok")


if __name__ == "__main__":
    main()
