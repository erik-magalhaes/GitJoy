#!/usr/bin/env python3
"""Mais material da TARDE DE JOGOS NO BECAS com os GUARDA-CHUVINHAS (5/nov/2026). Ele: "o primeiro é o que eu mais
gosto por causa dos guarda-chuvinhas, combina com a estética do lugar; cria outros materiais baseado nisso".

Mesma identidade de `tarde_becas.py` (creme, confete claro, guarda-chuvinhas nas cores da Sua Vez, Lilita + Figtree,
contorno marrom e sombra sólida). A ideia nova: os guarda-chuvinhas SEGURAM as coisas pelo cabo (placas, caixas,
números), como um móbile pendurado no teto do Becas.

    /usr/bin/python3 becas_chuva.py
      → out/becas/contagem/story_{7,3,2,1,hoje}.png   stories de contagem regressiva (com espaço p/ adesivo de link)
      → out/becas/carrossel/01..05.png                carrossel "PREVISÃO PRA 20/11: CHUVA DE JOGOS" (1080x1350)
      → out/becas/plaquinhas_mesa.pdf                 plaquinha de mesa A4 dobrada (MESA 1–8), uma cor por mesa
"""
import math
import os
import random

from PIL import Image, ImageDraw

import tarde_becas as TB
from tarde_becas import E, MAR, PET, LAR, AMA, BR, ROSA, CREME, WHATS

VERDE = (118, 176, 65)
CORES = [LAR, PET, AMA, ROSA, VERDE]
OUT = TB.OUT
FIO = (150, 120, 100)


# ---------------------------------------------------------------- peças
def segura(img, x, y, w, cor, obj=None, gap=40, rot=0.0, seed=0):
    """Guarda-chuvinha pendurado do teto (fio até y) segurando `obj` pelo cabo, com um fio de `gap` px.
    Devolve o centro do objeto."""
    d = ImageDraw.Draw(img)
    d.line([(x, 0), (x, y)], fill=FIO, width=3)
    g = TB.guarda_chuva(w, cor, seed)
    img.alpha_composite(g, (int(x - g.width / 2), int(y - 6)))
    hx, hy = x - 0.055 * w, y - 6 + 14 + 0.75 * w + 2  # ponto mais baixo do gancho do cabo
    if obj is None:
        return None
    o = obj.rotate(rot, expand=True, resample=Image.BICUBIC) if abs(rot) > 0.05 else obj
    top = hy + gap
    # argola + fio
    d.line([(hx, hy - 4), (hx, top + 14)], fill=MAR, width=4)
    img.alpha_composite(o, (int(hx - o.width / 2), int(top)))
    d.ellipse((hx - 9, top + 4, hx + 9, top + 22), fill=BR, outline=MAR, width=4)
    return hx, top + o.height / 2


def fundo_leve(W, H, seed=7):
    """Creme + confete claro, sem a fileira de guarda-chuvas (cada tela põe os seus)."""
    img = Image.new("RGBA", (W, H), CREME + (255,))
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    for _ in range(int(160 * W * H / (1080 * 1350))):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(3, 6)
        c = CORES[rnd.randrange(4)]
        c = tuple(int(v + (255 - v) * 0.7) for v in c)
        d.ellipse((x - r, y - r, x + r, y + r), fill=c)
    return img


def placa(w, h, cor, linhas, cor_txt=MAR):
    """Placa (bloco com contorno e sombra) com linhas [(texto, fonte, cor)] centralizadas."""
    p = E.bloco(w, h, cor, raio=28, ow=6, sombra=9).copy()
    d = ImageDraw.Draw(p)
    tot = sum(f.size * 1.18 for _, f, _ in linhas)
    y = h / 2 - tot / 2
    for txt, f, c in linhas:
        d.text((w / 2, y + f.size * 0.59), txt, font=f, fill=c or cor_txt, anchor="mm")
        y += f.size * 1.18
    return p


def disco(diam, cor, linhas):
    """Plaquinha redonda (para os números da contagem)."""
    s = 12
    im = Image.new("RGBA", (diam + s + 4, diam + s + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((s, s, s + diam, s + diam), fill=MAR)
    d.ellipse((0, 0, diam, diam), fill=cor, outline=MAR, width=8)
    tot = sum(f.size * 1.05 for _, f, _ in linhas)
    y = diam / 2 - tot / 2
    for txt, f, c in linhas:
        sw = max(3, int(f.size * 0.07)) if f.size > 120 else 0
        d.text((diam / 2, y + f.size * 0.52), txt, font=f, fill=c, anchor="mm", stroke_width=sw, stroke_fill=MAR)
        y += f.size * 1.05
    return im


# ---------------------------------------------------------------- stories de contagem
def story_contagem(n):
    W, H = 1080, 1920
    img = fundo_leve(W, H, 11 + (n if isinstance(n, int) else 0))
    # guarda-chuvinhas de enfeite nos cantos
    for k, (x, y, w) in enumerate([(110, 120, 150), (260, 230, 130), (820, 230, 130), (970, 120, 150)]):
        segura(img, x, y, w, CORES[(k + 1) % 5], seed=k)
    if n == "hoje":
        linhas = [("É", E.lilita(110), MAR), ("HOJE!", E.lilita(190), LAR)]
        cor = AMA
    elif n == 1:
        linhas = [("É", E.lilita(110), MAR), ("AMANHÃ!", E.lilita(108), LAR)]
        cor = AMA
    else:
        linhas = [("FALTAM", E.lilita(78), MAR), (str(n), E.lilita(290), LAR), ("DIAS", E.lilita(78), MAR)]
        cor = BR
    cx, cy = segura(img, W / 2, 140, 400, PET if n != "hoje" else ROSA, disco(560, cor, linhas), gap=36, rot=-3)
    y = cy + 330
    E.cola(img, E.titulo("TARDE DE JOGOS\nNO BECAS CAFÉ", 92, LAR), W / 2, y + 30, -1.5)
    E.cola(img, TB.selo_data(40), W / 2, y + 190, 1.5)
    E.cola(img, TB.selo_endereco(30), W / 2, y + 268, -1)
    txt = "Hoje das 13h às 19h: chega e joga!" if n == "hoje" else "Garanta sua mesa: " + WHATS
    E.cola(img, E.pilula(txt, 36, PET, BR), W / 2, y + 360, 0)
    # y ~1610–1760 fica livre para o adesivo de link do Instagram
    lg = E.logo(150)
    img.alpha_composite(lg, (int(W / 2 - lg.width / 2), H - lg.height - 40))
    return img


# ---------------------------------------------------------------- carrossel "chuva de jogos"
JOGOS6 = ["hitster", "dixit", "telma", "tapalavras", "say_my_name", "uga_buga"]
NOMES = {"hitster": "Hitster", "dixit": "Dixit", "telma": "Telma", "tapalavras": "Tapalavras",
         "say_my_name": "Say my Name", "uga_buga": "Uga Buga"}


def tela_capa():
    W, H = 1080, 1350
    img = fundo_leve(W, H, 21)
    # caixas "chovendo" entre os guarda-chuvas
    rnd = random.Random(4)
    pos = [(110, 1090, -16), (970, 1070, 14), (330, 1180, 10), (760, 1190, -9), (95, 640, 8), (985, 610, -12)]
    for (x, y, r), nome in zip(pos, JOGOS6):
        E.cola(img, TB.caixa(nome, 130 if y < 800 else 175), x, y, r)
    d = ImageDraw.Draw(img)
    for _ in range(26):  # pingos
        x, y = rnd.uniform(60, W - 60), rnd.uniform(420, 1300)
        d.line((x, y, x - 6, y + 26), fill=tuple(int(v + (255 - v) * 0.35) for v in PET), width=6)
    for k, (x, y, w) in enumerate([(120, 60, 160), (330, 140, 150), (540, 40, 170), (750, 130, 150), (960, 60, 160)]):
        segura(img, x, y, w, CORES[k], seed=k)
    E.cola(img, E.pilula("PREVISÃO PRA SEXTA, 20/11:", 40, BR, MAR, fonte_titulo=True), W / 2, 470, -1.5)
    E.cola(img, E.titulo("CHUVA\nDE JOGOS", 170, LAR), W / 2, 680, -2)
    E.cola(img, E.pilula("no Becas Café · 13h às 19h", 40, PET, BR), W / 2, 900, 1.5)
    E.cola(img, E.pilula("arrasta pro lado  →", 30, AMA, MAR), W / 2, 1270, 0)
    return img


def cabecalho(img, txt, y=470, cor=LAR):
    E.cola(img, E.titulo(txt, 96, cor, larg_max=960), img.width / 2, y, -1.5)


def tela_como():
    W, H = 1080, 1350
    img = fundo_leve(W, H, 22)
    passos = [("1", "Chega e", "pega uma mesa", LAR), ("2", "A gente", "ensina o jogo", PET), ("3", "Joga, pede", "um café e troca", ROSA)]
    xs = [190, 540, 890]
    ys = [40, 110, 30]
    for k, ((n, a, b, cor), x, y) in enumerate(zip(passos, xs, ys)):
        p = placa(300, 300, BR, [(n, E.lilita(120), cor), (a, E.fig(34, 900), MAR), (b, E.fig(34, 900), MAR)])
        segura(img, x, y, 190, cor, p, gap=30, rot=(-4, 3, -2)[k], seed=k)
    cabecalho(img, "COMO FUNCIONA?", 760)
    lista = placa(900, 300, BR, [("A gente leva os jogos e ensina todos", E.fig(40, 900), MAR),
                                 ("Jogos rápidos, pra quem nunca jogou", E.fig(40, 900), PET),
                                 ("Café e comidinhas do Becas", E.fig(40, 900), MAR)])
    E.cola(img, lista, W / 2, 1000, 0)
    E.cola(img, E.pilula("Venha sozinho, em dupla ou com a galera", 36, AMA, MAR), W / 2, 1230, -1)
    return img


def tela_jogos():
    W, H = 1080, 1350
    img = fundo_leve(W, H, 23)
    xs = [180, 540, 900]
    for k, nome in enumerate(JOGOS6):
        lin = k // 3
        x = xs[k % 3] + (lin * 20 - 10)
        y = (30, 110, 50)[k % 3] + lin * 470
        segura(img, x, y, 150, CORES[k % 5], TB.caixa(nome, 250), gap=24, rot=(-5, 4, -3, 5, -4, 3)[k], seed=k)
    # nomes em pílulas no pé de cada caixa? (as caixas já dizem o nome) → só o título
    cabecalho(img, "VAI TER NA MESA:", 1230, PET)
    return img


def tela_preco():
    W, H = 1080, 1350
    img = fundo_leve(W, H, 24)
    etiqueta = placa(560, 470, AMA, [("R$ 30", E.lilita(170), LAR), ("por pessoa", E.fig(44, 900), MAR),
                                      ("R$ 15 viram", E.fig(44, 900), PET), ("consumação no café", E.fig(44, 900), PET)])
    segura(img, W / 2, 30, 300, ROSA, etiqueta, gap=40, rot=-3)
    for k, (x, y, w) in enumerate([(120, 120, 150), (960, 120, 150)]):
        segura(img, x, y, w, (PET, VERDE)[k], seed=k + 4)
    cabecalho(img, "E QUANTO É?", 1000, PET)
    bonus = placa(860, 150, BR, [("E MAIS: quem joga ganha um cupom", E.fig(36, 900), MAR),
                                 ("de 10% no 1º aluguel na Sua Vez", E.fig(36, 900), PET)])
    E.cola(img, bonus, W / 2, 1180, 1)
    return img


def tela_reserva():
    W, H = 1080, 1350
    img = TB.fundo(W, H, [60, 120, 40, 105, 50, 115], 140)
    E.cola(img, E.titulo("GARANTA\nSUA MESA!", 140, LAR), W / 2, 450, -2)
    E.cola(img, TB.selo_data(38), W / 2, 640, 1.5)
    E.cola(img, TB.selo_endereco(28), W / 2, 712, -1)
    E.cola(img, TB.inscricao(900), W / 2, 880, 0)
    E.cola(img, E.pilula("Comenta: com quem você vai?", 40, AMA, MAR), W / 2, 1080, -1.5)
    lg = E.logo(190)
    img.alpha_composite(lg, (int(W / 2 - lg.width / 2), 1170))
    return img


# ---------------------------------------------------------------- plaquinhas de mesa (impresso)
def plaquinha(n):
    """Metade de uma A4 deitada (29,7 x 10,5 cm visível): MESA n segurada por um guarda-chuvinha."""
    W, H = 3508, 1240  # A4 em largura a 300 dpi, metade da altura
    img = fundo_leve(W, H, 30 + n)
    cor = CORES[(n - 1) % 5]
    E.cola(img, TB.guarda_chuva(760, cor, n), 560, 600, -6)
    E.cola(img, E.titulo(f"MESA {n}", 360, cor if cor != AMA else LAR), 1800, 460, -1.5)
    E.cola(img, E.pilula("Tarde de Jogos · Sua Vez × Becas Café", 70, BR, MAR, fonte_titulo=True), 1800, 820, 1)
    E.cola(img, E.pilula("Dúvida no jogo? Chama a gente!", 62, PET, BR), 1800, 1040, 0)
    lg = E.logo(560)
    E.cola(img, lg, 3020, 620, 3)
    return img


def folha_plaquinha(n):
    """A4 em pé, dobrada ao meio: a metade de cima de ponta-cabeça (aparece dos dois lados da mesa)."""
    W, H = 3508, 2480
    p = plaquinha(n).convert("RGB")
    f = Image.new("RGB", (W, H), (255, 255, 255))
    f.paste(p.rotate(180), (0, 0))
    f.paste(p, (0, H // 2))
    d = ImageDraw.Draw(f)
    for x in range(0, W, 60):  # linha de dobra tracejada
        d.line((x, H // 2, x + 30, H // 2), fill=(170, 170, 170), width=4)
    return f.rotate(90, expand=True)  # A4 em pé para imprimir


def main():
    os.makedirs(os.path.join(OUT, "contagem"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "carrossel"), exist_ok=True)
    for n in (7, 3, 2, 1, "hoje"):
        story_contagem(n).convert("RGB").save(os.path.join(OUT, "contagem", f"story_{n}.png"))
    for k, f in enumerate((tela_capa, tela_como, tela_jogos, tela_preco, tela_reserva), 1):
        f().convert("RGB").save(os.path.join(OUT, "carrossel", f"{k:02d}.png"))
    fs = [folha_plaquinha(n) for n in range(1, 9)]
    fs[0].save(os.path.join(OUT, "plaquinhas_mesa.pdf"), resolution=300, save_all=True, append_images=fs[1:])
    plaquinha(1).convert("RGB").resize((1169, 413)).save(os.path.join(OUT, "plaquinha_previa.jpg"), quality=88)
    print("ok")


if __name__ == "__main__":
    main()
