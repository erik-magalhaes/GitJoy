#!/usr/bin/env python3
"""BANNERS do carrossel do topo do site novo (plataforma Rejoy, 13/nov/2026). 1920x640 (3:1); o que importa fica no
meio (x ~300–1620) pra sobreviver se a plataforma cortar as laterais. Identidade da Jéssica (estilo.py) + mascotes 3D
(capivara = Jéssica, coruja = Erik) + caixas OFICIAIS. Um fundo diferente por banner.
Sem "mais alugados" (não há dado de aluguel: nunca inventar) → "queridinhos da casa".

    /usr/bin/python3 rejoy.py   → out/banner_0N_*.png + out/banners_previa.jpg
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
import estilo as E  # noqa: E402

W, H = 1920, 640
OUT = os.path.join(ROOT, "out")
POSES = os.path.join(REPO, "mascote", "assets", "poses")
LISTA = os.path.join(REPO, "gravados-reels", "assets", "lista")
MAR, PET, LAR, AMA, BR = E.MARROM, E.PETROLEO, E.LARANJA, E.AMARELO, E.BRANCO
ROXO = (108, 63, 160)


def pose(nome, h):
    im = Image.open(os.path.join(POSES, nome + ".png")).convert("RGBA")
    return im.resize((int(im.width * h / im.height), int(h)), Image.LANCZOS)


def caixa(path, h):
    im = Image.open(path).convert("RGBA")
    im = im.crop(im.getbbox())
    im = im.resize((int(im.width * h / im.height), int(h)), Image.LANCZOS)
    sh = Image.new("RGBA", (im.width + 40, im.height + 40), (0, 0, 0, 0))
    sh.paste(MAR + (120,), (22, 26), im.getchannel("A"))
    sh = sh.filter(ImageFilter.GaussianBlur(7))
    sh.alpha_composite(im, (6, 6))
    return sh


def sombra_chao(img, cx, base, w):
    s = Image.new("RGBA", (int(w * 1.3), 70), (0, 0, 0, 0))
    ImageDraw.Draw(s).ellipse((w * 0.15, 18, w * 1.15, 52), fill=MAR + (60,))
    s = s.filter(ImageFilter.GaussianBlur(9))
    img.alpha_composite(s, (int(cx - s.width / 2), int(base - 40)))


def mascote(img, nome, h, cx, base):
    p = pose(nome, h)
    sombra_chao(img, cx, base, p.width * 0.75)
    img.alpha_composite(p, (int(cx - p.width / 2), int(base - p.height)))


def esq(img, im, x, cy):
    """cola alinhado pela ESQUERDA em x."""
    img.alpha_composite(im, (int(x), int(cy - im.height / 2)))


def logo_canto(img):
    lg = E.logo(190)
    img.alpha_composite(lg, (W - lg.width - 40, 30))


def b1_hero():
    img = E.fundo(W, H, 3).copy()
    esq(img, E.titulo("ALUGUE JOGOS\nDE TABULEIRO", 104, LAR), 330, 215)
    esq(img, E.texto("e jogue em casa com quem você gosta", 44, MAR, 800), 345, 360)
    esq(img, E.pilula("+ DE 160 JOGOS · A PARTIR DE R$ 15", 38, AMA, MAR, fonte_titulo=True), 340, 445)
    esq(img, E.pilula("RETIRE EM MAUÁ OU RECEBA EM CASA", 34, PET, BR, fonte_titulo=True), 340, 530)
    mascote(img, "capivara_pilha", 470, 1340, 610)
    mascote(img, "coruja_acenando", 430, 1640, 615)
    logo_canto(img)
    return img


def b2_queridinhos():
    img = E.fundo_confete(W, H, base=LAR, semente=5, n=70, livre=(260, 60, 1660, 600)).copy()
    E.cola(img, E.titulo("OS QUERIDINHOS DA CASA", 92, AMA), W / 2, 105, -1.5)
    nomes = ["king_of_tokyo", "ticket_to_ride", "harmonies", "hitster", "dixit"]
    xs = [460, 710, 960, 1210, 1460]
    for k, (n, x) in enumerate(zip(nomes, xs)):
        E.cola(img, caixa(os.path.join(LISTA, n + ".png"), 300), x, 395, (-1) ** k * 3)
    E.cola(img, E.pilula("os jogos que a gente mais indica pra começar", 34, BR, MAR), W / 2, 590, 0)
    mascote(img, "coruja_joinha", 330, 175, 625)
    logo_canto(img)
    return img


def degrau(w, h, cor, jogos, dias):
    b = E.bloco(w, h, cor, raio=28, ow=6, sombra=10).copy()
    d = ImageDraw.Draw(b)
    d.text((w / 2, 62), f"{jogos} JOGOS", font=E.lilita(50), fill=BR, anchor="mm", stroke_width=4, stroke_fill=MAR)
    d.text((w / 2, 128), "=", font=E.lilita(46), fill=MAR, anchor="mm")
    d.text((w / 2, 196), f"{dias} DIAS", font=E.lilita(58), fill=AMA, anchor="mm", stroke_width=5, stroke_fill=MAR)
    return b


def b3_prazo():
    img = E.fundo_xadrez(W, H).copy()
    esq(img, E.titulo("QUANTO MAIS JOGOS,\nMAIS DIAS!", 92, LAR), 300, 205)
    esq(img, E.texto("Todos os jogos do carrinho ficam\nmais tempo, pelo mesmo preço.", 40, MAR, 800, alinha="lm"),
        310, 405)
    for k, (j, dd, cor) in enumerate([(3, 7, PET), (5, 10, LAR), (7, 15, (219, 39, 119))]):
        h = 260 + k * 45
        b = degrau(270, h, cor, j, dd)
        img.alpha_composite(b, (1000 + k * 295, 600 - h))
    logo_canto(img)
    return img


def plano(w, h, cor, nome, preco, linhas):
    b = E.bloco(w, h, BR, raio=30, ow=6, sombra=10).copy()
    d = ImageDraw.Draw(b)
    d.rounded_rectangle((0, 0, w, 86), 30, fill=cor, outline=MAR, width=6)
    d.rectangle((6, 56, w - 6, 83), fill=cor)
    d.line((0, 86, w, 86), fill=MAR, width=6)
    d.text((w / 2, 46), nome, font=E.lilita(50), fill=BR, anchor="mm", stroke_width=4, stroke_fill=MAR)
    d.text((w / 2, 150), preco, font=E.lilita(62), fill=MAR, anchor="mm")
    d.text((w / 2, 196), "por mês", font=E.fig(28, 800), fill=MAR, anchor="mm")
    for k, l in enumerate(linhas):
        d.text((w / 2, 248 + k * 38), l, font=E.fig(28, 800), fill=PET, anchor="mm")
    return b


def b4_assinatura():
    img = Image.new("RGBA", (W, H), PET + (255,))
    d = ImageDraw.Draw(img)
    for y in range(30, H, 60):
        for x in range(30 + (30 if (y // 60) % 2 else 0), W, 60):
            d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(46, 142, 168))
    esq(img, E.titulo("ASSINE E\nTROQUE À\nVONTADE!", 80, AMA), 280, 250)
    esq(img, E.texto("trocas sem limite no mês", 36, BR, 800), 300, 515)
    for k, (n, p, cor, ls) in enumerate([("SILVER", "R$ 49", (150, 160, 170), ["1 jogo por vez", "Pocket e Família"]),
                                         ("GOLD", "R$ 89", (226, 168, 30), ["2 jogos por vez", "+ Estratégico"]),
                                         ("PLATINUM", "R$ 139", (120, 130, 200), ["3 jogos por vez", "acervo inteiro"])]):
        b = plano(280, 340, cor, n, p, ls)
        E.cola(img, b, 880 + k * 300, 330, (-1.5, 0, 1.5)[k])
    mascote(img, "capivara_joinha", 360, 1770, 625)
    logo_canto(img)
    return img


def b5_eventos():
    img = E.fundo_confete(W, H, base=ROXO, cores=(AMA, BR, LAR, (130, 200, 220)), semente=9, n=80,
                          livre=(240, 40, 1500, 610)).copy()
    esq(img, E.titulo("TEM EVENTO?\nA GENTE LEVA OS JOGOS!", 84, AMA), 300, 200)
    esq(img, E.texto("e fica o evento todo ensinando a jogar", 40, BR, 800), 312, 375)
    esq(img, E.pilula("ABC PAULISTA E SÃO PAULO CAPITAL", 34, BR, ROXO, fonte_titulo=True), 305, 455)
    esq(img, E.pilula("ORÇAMENTO NO WHATSAPP (11) 97793-3910", 34, AMA, MAR, fonte_titulo=True), 305, 540)
    mascote(img, "coruja_explicando", 470, 1420, 615)
    mascote(img, "capivara_entregando", 400, 1660, 615)
    logo_canto(img)
    return img


BANNERS = [("01_alugue", b1_hero), ("02_queridinhos", b2_queridinhos), ("03_prazo_progressivo", b3_prazo),
           ("04_assinaturas", b4_assinatura), ("05_eventos", b5_eventos)]


def main():
    os.makedirs(OUT, exist_ok=True)
    ims = []
    for nome, f in BANNERS:
        im = f().convert("RGB")
        im.save(os.path.join(OUT, f"banner_{nome}.png"))
        ims.append(im)
    pv = Image.new("RGB", (960, len(ims) * 330 + 10), (255, 255, 255))
    for k, im in enumerate(ims):
        pv.paste(im.resize((960, 320)), (0, 5 + k * 330))
    pv.save(os.path.join(OUT, "banners_previa.jpg"), quality=88)
    print("ok")


if __name__ == "__main__":
    main()
