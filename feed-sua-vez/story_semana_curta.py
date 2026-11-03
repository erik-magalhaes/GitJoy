#!/usr/bin/env python3
"""Stories "SEMANA CURTA" (2/nov/2026, feriado de Finados; pedido dele: algo pro Stories que leve gente pro site, sem
falar de Finados). A semana deles começa na terça. 3 telas 1080x1920, identidade da Jéssica, conceito AGENDA DA SEMANA
(folha de agenda creme com espiral no alto, linhas pautadas e margem), fundo novo:

  1 gancho "SÉRIE OU JOGO?" + espaço para a ENQUETE do Instagram (a 1ª, "quanto tempo sobra pra jogar depois do
    trabalho?", ele achou ruim)
  2 a agenda: TER/QUA/QUI com um jogo Pocket rápido por noite (R$ 15, ficha do site) e SEX "o jogão: você escolhe";
    faixa "3 JOGOS POCKET = R$ 45 E FICAM 7 DIAS" (prazo progressivo: 3 jogos = 7 dias, mesmo preço)
  3 chamada: bônus do sorteio do Hitster (quem alugar até 15/11 ganha +2 dias) + espaço para o adesivo de LINK

Tudo dentro de y 250–1650 (o Instagram cobre o alto e o pé do story).

    /usr/bin/python3 story_semana_curta.py   # out/story_semana/1_enquete.png, 2_agenda.png, 3_link.png
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
import estilo as E  # noqa: E402

W, H = 1080, 1920
OUT = os.path.join(ROOT, "out", "story_semana")
CX = os.path.join(REPO, "hobby-reels", "assets", "acervo")
MAR, PET, LAR, AMA, BR = E.MARROM, E.PETROLEO, E.LARANJA, E.AMARELO, E.BRANCO
PAPEL = (252, 246, 232)
LINHA = (214, 228, 236)
# (dia, arquivo, nome, ficha do site)
NOITES = [("TER", "bad_signs", "Bad Signs", "2 a 6 jogadores · 15 min"),
          ("QUA", "flash_10", "Flash 10", "2 a 5 jogadores · 20 min"),
          ("QUI", "loser", "Loser", "3 a 6 jogadores · 20 min")]


def fundo():
    """Mesa laranja com a folha de agenda creme por cima (espiral no alto, pautado azul, margem vermelha)."""
    img = Image.new("RGBA", (W, H), LAR + (255,))
    d = ImageDraw.Draw(img)
    for y in range(0, H, 60):  # listras finas da mesa
        d.rectangle((0, y, W, y + 26), fill=(236, 124, 28))
    folha = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    df = ImageDraw.Draw(folha)
    x0, y0, x1, y1 = 56, 150, W - 56, H - 110
    df.rounded_rectangle((x0 + 14, y0 + 16, x1 + 14, y1 + 16), 30, fill=MAR)  # sombra sólida
    df.rounded_rectangle((x0, y0, x1, y1), 30, fill=PAPEL, outline=MAR, width=7)
    for y in range(y0 + 150, y1 - 30, 64):
        df.line((x0 + 10, y, x1 - 10, y), fill=LINHA, width=3)
    df.line((x0 + 110, y0 + 8, x0 + 110, y1 - 8), fill=(238, 160, 160), width=4)
    for x in range(x0 + 60, x1 - 30, 74):  # espiral
        df.ellipse((x - 16, y0 + 28, x + 16, y0 + 60), fill=(90, 70, 60))
        df.rounded_rectangle((x - 7, y0 - 34, x + 7, y0 + 48), 7, fill=(170, 170, 178), outline=MAR, width=3)
    img.alpha_composite(folha)
    return img


def caixa(nome, h, larg):
    im = Image.open(os.path.join(CX, nome + ".png")).convert("RGBA")
    im = im.crop(im.getbbox())
    s = min(h / im.height, larg / im.width)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    sh = Image.new("RGBA", (im.width + 16, im.height + 16), (0, 0, 0, 0))
    sh.paste(MAR + (150,), (10, 12), im.getchannel("A"))
    sh = sh.filter(ImageFilter.GaussianBlur(4))
    sh.alpha_composite(im, (0, 0))
    return sh


def logo(img):
    lg = E.logo(190)
    img.alpha_composite(lg, (W - lg.width - 70, 205))


def tela1():
    img = fundo()
    logo(img)
    E.cola(img, E.pilula("A PERGUNTA DE HOJE", 40, PET, BR), W / 2 - 40, 430, -2)
    E.cola(img, E.titulo("SÉRIE\nOU JOGO?", 150, AMA), W / 2, 650, -2)
    E.cola(img, E.texto("Hoje à noite, você vai de quê?", 52, MAR, 800), W / 2, 905)
    # y 1000–1380 fica LIVRE para o adesivo de enquete do Instagram (SÉRIE / JOGO)
    t = E.texto("Deu JOGO? O próximo story é pra você.", 42, MAR, 800)
    E.cola(img, t, W / 2, 1500)
    return img


def tela2():
    img = fundo()
    logo(img)
    E.cola(img, E.titulo("SEMANA CURTA,\nJOGO RÁPIDO!", 104, AMA), W / 2, 460, -2)
    E.cola(img, E.texto("um por noite, depois do trabalho:", 44, MAR, 800), W / 2, 620)
    y = 720
    for k, (dia, arq, nome, ficha) in enumerate(NOITES):
        E.cola(img, E.pilula(dia, 46, (PET, LAR, PET)[k], BR, fonte_titulo=True), 225, y + 70, (-4, 3, -3)[k])
        cx = caixa(arq, 170, 200)
        img.alpha_composite(cx, (350 - 0, int(y + 70 - cx.height / 2)))
        E.cola(img, E.texto(nome, 54, MAR, 900, alinha="lm"), 590 + E.texto(nome, 54, MAR, 900, alinha="lm").width / 2,
               y + 40)
        f = E.texto(ficha, 34, (110, 80, 60), 700, alinha="lm")
        E.cola(img, f, 590 + f.width / 2, y + 100)
        y += 196
    E.cola(img, E.pilula("SEX", 46, LAR, BR, fonte_titulo=True), 225, y + 60, 4)
    t = E.texto("o jogão: você escolhe\nentre 160+ do acervo!", 44, MAR, 900, alinha="lm")
    E.cola(img, t, 380 + t.width / 2, y + 60)
    faixa = E.bloco(900, 170, AMA, raio=30, ow=7, sombra=11).copy()
    d = ImageDraw.Draw(faixa)
    d.text((450, 58), "3 JOGOS POCKET = R$ 45", font=E.lilita(62), fill=MAR, anchor="mm")
    d.text((450, 122), "e os 3 ficam 7 dias com você", font=E.fig(40, 800), fill=MAR, anchor="mm")
    E.cola(img, faixa, W / 2, 1570, -1.5)
    return img


def tela3():
    img = fundo()
    logo(img)
    E.cola(img, E.titulo("BÔNUS DA\nSEMANA!", 140, AMA), W / 2, 520, -2)
    selo = E.bloco(760, 300, PET, raio=40, ow=8, sombra=12).copy()
    d = ImageDraw.Draw(selo)
    d.text((380, 70), "ALUGOU ATÉ 15/11?", font=E.lilita(58), fill=BR, anchor="mm")
    d.text((380, 175), "+2 DIAS", font=E.lilita(130), fill=AMA, anchor="mm", stroke_width=7, stroke_fill=MAR)
    d.text((380, 262), "de jogo de presente", font=E.fig(40, 800), fill=BR, anchor="mm")
    E.cola(img, selo, W / 2, 920, 2)
    E.cola(img, E.texto("Reserve no site e retire em Mauá\nou receba em casa.", 46, MAR, 800), W / 2, 1185)
    E.cola(img, E.pilula("RESERVE PELO LINK 👇".replace(" 👇", ""), 52, LAR, BR, fonte_titulo=True), W / 2, 1335, -2)
    d = ImageDraw.Draw(img)  # seta para o adesivo de link
    d.polygon([(W / 2 - 40, 1400), (W / 2 + 40, 1400), (W / 2, 1450)], fill=MAR)
    # y 1475–1610 fica LIVRE para o adesivo de link
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    telas = [("1_enquete", tela1()), ("2_agenda", tela2()), ("3_link", tela3())]
    for n, im in telas:
        im.convert("RGB").save(os.path.join(OUT, n + ".png"))
    sh = Image.new("RGB", (3 * 360 + 40, 640), (255, 255, 255))
    for k, (_, im) in enumerate(telas):
        sh.paste(im.convert("RGB").resize((360, 640), Image.LANCZOS), (k * 380, 0))
    sh.save(os.path.join(OUT, "folha.jpg"), quality=90)
    print("ok")


if __name__ == "__main__":
    main()
