#!/usr/bin/env python3
"""Carrossel "O JOGO CERTO PRA CADA FESTA" (11/nov/2026, ideia dele: um jogo do acervo para cada tipo de evento).

Conceito novo: CALENDÁRIO DE PAREDE. Cada tela é a folha do mês pendurada num prego (espiral de arame no alto): em cima,
a "foto do mês" com o nome do evento, a caixa do jogo e a ficha; embaixo, a grade do mês com o dia circulado à caneta
vermelha. Eventos sem data fixa (aniversário, churrasco, pijama, chá revelação) circulam um dia com "o seu dia!".
Identidade da Jéssica (Lilita + Figtree, marrom, contorno e sombra), letra de mão Caveat na caneta.

Ele escolheu 10 dos 12 da folha de opções (tirou Go Cuckoo, "a gente está usando muito", e Perfil Express).
Fichas (jogadores/tempo) do site (`comum/dados/acervo_site.json`); caixas = recortes da foto do site/oficiais.

    /usr/bin/python3 calendario_festas.py
      → out/calendario_festas/01..12.png (1080x1350) + stories/story_01..12.png (1080x1920) + previa*.jpg
"""
import calendar
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
import estilo as E  # noqa: E402

OUT = os.path.join(ROOT, "out", "calendario_festas")
MAR, PET, LAR, AMA, BR = E.MARROM, E.PETROLEO, E.LARANJA, E.AMARELO, E.BRANCO
ROSA, VERDE, ROXO, VERM = (219, 39, 119), (88, 160, 60), (108, 63, 160), (200, 32, 40)
CANETA = os.path.join(REPO, "tikal-reels", "assets", "fonts", "Caveat.ttf")
W, H = 1080, 1350
MESES = ["JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO", "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO",
         "NOVEMBRO", "DEZEMBRO"]
WHATS = "(11) 97793-3910"

# (evento, (ano, mês, dia) ou None, nota da caneta, jogo, caixa, jogadores, tempo, frase, cor da foto do mês)
EVENTOS = [
    ("ANIVERSÁRIO", None, "o seu dia!", "Flip 7: A Vingança", "hobby-reels/assets/acervo/flip_7_a_vingan_a.png",
     "3 a 28", "20 min", "Vira mais uma carta ou para? Dá pra jogar com até 28 pessoas!", LAR),
    ("AMIGO SECRETO", (2026, 12, None), "dia da confra!", "Mascarade",
     "hobby-reels/assets/acervo/mascarade_second_edition.png", "4 a 12", "30 min",
     "Cada um tem um personagem... e ninguém tem certeza de quem é quem!", ROXO),
    ("RÉVEILLON", (2026, 12, 31), "virada!", "Telestrations na Madruga",
     "gravados-reels/assets/top10/telestrations_madruga.png", "4 a 8", "30 min",
     "Desenha, passa, adivinha... e ri até a virada. Versão +18!", MAR),
    ("CARNAVAL", (2027, 2, 9), "bloquinho!", "Happy Salmon", "roleta-reels/assets/happy_salmon.png", "3 a 8",
     "2 min", "Todo mundo grita, troca cartas e bate a mão ao mesmo tempo. É bagunça boa!", VERDE),
    ("DIA DOS NAMORADOS", (2027, 6, 12), "date!", "Allumbra: O Duelo",
     "hobby-reels/assets/acervo/allumbra_o_duelo.png", "2", "10 min",
     "Um duelo rapidinho a dois: 10 minutos e já sai pedido de revanche.", ROSA),
    ("FESTA JUNINA", (2027, 6, 24), "arraiá!", "Bohnanza", "hobby-reels/assets/acervo/bohnanza.png", "2 a 7",
     "45 min", "Plante, negocie e venda feijão como numa barraca de quermesse!", AMA),
    ("HALLOWEEN", (2027, 10, 31), "buuu!", "Paranormal Detectives",
     "hobby-reels/assets/acervo/paranormal_detectives.png", "2 a 6", "50 min",
     "Um jogador é o fantasma e o resto tenta descobrir o que aconteceu com ele.", ROXO),
    ("CHURRASCO", None, "domingão!", "Throw Throw Burrito", "hobby-reels/assets/acervo/throw_throw_burrito.png",
     "2 a 6", "15 min", "Junte cartas iguais e... arremesse burrito de pelúcia na galera!", LAR),
    ("FESTA DO PIJAMA", None, "noite toda!", "Scooby-Doo!", "gravados-reels/assets/oficial/scooby_doo.png",
     "1 a 5", "30 min", "Junte pistas com a turma do Scooby e desmascare o monstro!", PET),
    ("CHÁ REVELAÇÃO", None, "é menina ou menino?", "Código Secreto: Imagens",
     "hobby-reels/assets/caixas/c_digo_secreto_imagens.png", "2 a 8", "15 min",
     "Time \"é menina\" × time \"é menino\": o chefe dá uma dica e o time acha as imagens!", ROSA),
]


# ---------------------------------------------------------------- peças
def caneta(s):
    return E.fonte(CANETA, s) if os.path.isabs(CANETA) else E.fonte(CANETA, s)


def fonte_caneta(s):
    from PIL import ImageFont
    f = ImageFont.truetype(CANETA, s)
    try:
        f.set_variation_by_axes([700])
    except Exception:
        pass
    return f


def parede(w, h, seed=1):
    """Parede pintada (azul-claro da marca) com papel de parede de losangos bem suaves e luz de cima."""
    rnd = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    base = np.array(E.FUNDO, np.float32)
    los = ((np.abs(((xx + yy) % 90) - 45) < 2) | (np.abs(((xx - yy) % 90) - 45) < 2)).astype(np.float32)
    a = base[None, None] * (1 - 0.035 * los[..., None])
    a *= (1.02 - 0.08 * (yy / h))[..., None]
    a += rnd.normal(0, 2.2, (h, w, 1))
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


def caixa(path, hmax, wmax):
    im = Image.open(os.path.join(REPO, path)).convert("RGBA")
    im = im.crop(im.getbbox())
    esc = min(hmax / im.height, wmax / im.width)
    im = im.resize((int(im.width * esc), int(im.height * esc)), Image.LANCZOS)
    sh = Image.new("RGBA", (im.width + 30, im.height + 30), (0, 0, 0, 0))
    sh.paste((0, 0, 0, 110), (16, 20), im.getchannel("A"))
    sh = sh.filter(ImageFilter.GaussianBlur(7))
    sh.alpha_composite(im, (2, 2))
    return sh


def chip(txt, s=34, cor=BR, cor_txt=MAR):
    return E.pilula(txt, s, cor, cor_txt, pad=(24, 10), ow=4, sombra=5)


def circulo(d, cx, cy, rx, ry, cor=VERM, seed=0):
    """Círculo de caneta: 2 voltas tremidas que não fecham certinho."""
    rnd = random.Random(seed)
    for volta in range(2):
        pts = []
        a0 = rnd.uniform(-1.2, -0.6)
        for k in range(46):
            a = a0 + 2 * math.pi * 1.08 * k / 45
            r = 1 + 0.05 * math.sin(3 * a + volta) + rnd.uniform(-0.012, 0.012)
            pts.append((cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)))
        d.line(pts, fill=cor, width=7, joint="curve")


def mes_grade(img, x0, y0, w, h, ano, mes, dia, nota, seed=0, rotulo=None):
    """Grade do mês (D S T Q Q S S) com o dia circulado e a nota à caneta."""
    d = ImageDraw.Draw(img)
    titulo = rotulo or f"{MESES[mes - 1]} {ano}"
    d.text((x0 + 14, y0 + 34), titulo, font=E.lilita(54), fill=MAR, anchor="lm")
    d.text((x0 + w - 14, y0 + 30), nota, font=fonte_caneta(52), fill=VERM, anchor="rm")
    cols = ["D", "S", "T", "Q", "Q", "S", "S"]
    cw = w / 7
    for k, c in enumerate(cols):
        d.text((x0 + cw * (k + 0.5), y0 + 92), c, font=E.fig(28, 900), fill=VERM if k == 0 else PET, anchor="mm")
    cal = calendar.Calendar(firstweekday=6).monthdayscalendar(ano, mes)
    ch = (h - 120) / max(5, len(cal))
    alvo = None
    for r, sem in enumerate(cal):
        for c, n in enumerate(sem):
            cx, cy = x0 + cw * (c + 0.5), y0 + 120 + ch * (r + 0.5)
            d.line((x0 + cw * c + 6, y0 + 120 + ch * r, x0 + cw * (c + 1) - 6, y0 + 120 + ch * r), fill=(225, 225, 225), width=2)
            if n:
                d.text((cx, cy), str(n), font=E.fig(34, 800), fill=VERM if c == 0 else MAR, anchor="mm")
                if n == dia:
                    alvo = (cx, cy, r, c)
    if alvo:
        cx, cy, r, c = alvo
        circulo(d, cx, cy, cw * 0.46, ch * 0.5, seed=seed)
    return alvo


def folha(ev, k):
    """Uma folha do calendário pendurada (900 x 1210) com a foto do mês e a grade."""
    nome, data, nota, jogo, path, jog, tempo, frase, cor = ev
    fw, fh = 900, 1200
    f = Image.new("RGBA", (fw, fh), (252, 252, 250, 255))
    d = ImageDraw.Draw(f)
    # "foto do mês"
    fy0, fy1 = 70, 650
    clara = tuple(int(v + (255 - v) * 0.25) for v in cor)
    d.rectangle((24, fy0, fw - 24, fy1), fill=cor)
    rnd = random.Random(k)
    for _ in range(70):  # confete clarinho na foto
        x, y, r = rnd.uniform(30, fw - 30), rnd.uniform(fy0 + 6, fy1 - 6), rnd.uniform(4, 8)
        d.ellipse((x - r, y - r, x + r, y + r), fill=clara)
    txt_cor = MAR if cor == AMA else BR
    t = E.titulo(nome, 92 if len(nome) < 14 else 74, AMA if cor not in (AMA, LAR) else BR, larg_max=fw - 90)
    f.alpha_composite(t, (int(fw / 2 - t.width / 2), fy0 + 18))
    ytop = fy0 + 26 + t.height
    cb = caixa(path, fy1 - ytop - 24, 360)
    f.alpha_composite(cb, (60, int(ytop + (fy1 - ytop - cb.height) / 2)))
    # ficha à direita
    xr0 = 60 + cb.width + 20
    wr = fw - 40 - xr0
    tj = E.titulo(jogo, 56, BR if cor != AMA else PET, larg_max=wr)
    yy = ytop + 10
    f.alpha_composite(tj, (int(xr0 + wr / 2 - tj.width / 2), int(yy)))
    yy += tj.height + 12
    a = chip(f"{jog} jogadores" if jog != "2" else "2 jogadores")
    b = chip(tempo)
    if a.width + b.width + 14 <= wr:
        f.alpha_composite(a, (int(xr0 + wr / 2 - (a.width + b.width + 14) / 2), int(yy)))
        f.alpha_composite(b, (int(xr0 + wr / 2 - (a.width + b.width + 14) / 2 + a.width + 14), int(yy)))
        yy += a.height + 14
    else:
        f.alpha_composite(a, (int(xr0 + wr / 2 - a.width / 2), int(yy)))
        yy += a.height + 8
        f.alpha_composite(b, (int(xr0 + wr / 2 - b.width / 2), int(yy)))
        yy += b.height + 14
    for tam in range(38, 25, -2):  # a frase diminui até caber na foto do mês
        tf = E.texto(frase, tam, txt_cor, 800, larg_max=wr - 10, entre=1.15)
        if yy + tf.height <= fy1 - 16:
            break
    f.alpha_composite(tf, (int(xr0 + wr / 2 - tf.width / 2), int(yy)))
    # grade do mês
    if data and data[2]:
        mes_grade(f, 40, 680, fw - 80, fh - 700, data[0], data[1], data[2], nota, seed=k)
    elif data:  # mês certo, dia que você escolhe
        mes_grade(f, 40, 680, fw - 80, fh - 700, data[0], data[1], 18, nota, seed=k)
    else:
        mes_grade(f, 40, 680, fw - 80, fh - 700, 2026, 11, 14, nota, seed=k, rotulo="QUALQUER MÊS")
    # furos da espiral
    for x in range(60, fw - 40, 44):
        d.ellipse((x - 7, 26, x + 7, 40), fill=(205, 210, 214))
    return f


def pendura(img, f, cx, top, rot=0.0):
    """Prego + espiral de arame + a folha com sombra suave na parede."""
    d = ImageDraw.Draw(img)
    fr = f.rotate(rot, expand=True, resample=Image.BICUBIC) if rot else f
    sh = Image.new("RGBA", fr.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 80), (0, 0), fr.getchannel("A"))
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    x0 = int(cx - fr.width / 2)
    img.alpha_composite(sh, (x0 + 12, top + 18))
    img.alpha_composite(fr, (x0, top))
    # espiral (argolas de arame passando pelos furos)
    for x in range(int(cx - f.width / 2) + 60, int(cx + f.width / 2) - 40, 44):
        d.arc((x - 9, top + 6, x + 9, top + 44), 180, 360, fill=(120, 124, 130), width=5)
    # cordinha e prego
    d.line((cx - 140, top + 14, cx, top - 50, cx + 140, top + 14), fill=(120, 124, 130), width=4)
    d.ellipse((cx - 13, top - 63, cx + 13, top - 37), fill=(150, 150, 155), outline=(90, 90, 95), width=3)


def logo_canto(img):
    lg = E.logo(150)
    img.alpha_composite(lg, (W - lg.width - 20, 18))


# ---------------------------------------------------------------- telas
def tela_evento(k):
    img = parede(W, H, 10 + k)
    pendura(img, folha(EVENTOS[k], k), W / 2, 120, rot=(-1.2, 0.9, -0.6, 1.1)[k % 4])
    logo_canto(img)
    return img


def tela_capa():
    img = parede(W, H, 3)
    rnd = random.Random(5)
    # folhas empilhadas atrás (mês que vira), a de cima com a capa
    for k, rot in enumerate((5, -4)):
        f = Image.new("RGBA", (860, 1120), (240, 240, 236, 255))
        ImageDraw.Draw(f).rectangle((24, 60, 836, 560), fill=(LAR, PET)[k])
        pendura(img, f, W / 2 + (k * 2 - 1) * 26, 150, rot=rot)
    f = Image.new("RGBA", (860, 1120), (252, 252, 250, 255))
    d = ImageDraw.Draw(f)
    d.rectangle((24, 60, 836, 600), fill=PET)
    for _ in range(80):
        x, y, r = rnd.uniform(30, 830), rnd.uniform(66, 594), rnd.uniform(4, 8)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(80, 160, 182))
    # mini caixas na foto
    sel = [EVENTOS[i][4] for i in (0, 3, 5, 7)]
    for j, p in enumerate(sel):
        cb = caixa(p, 200, 180)
        f.alpha_composite(cb.rotate((-8, 6, -5, 8)[j], expand=True, resample=Image.BICUBIC),
                          (70 + j * 185, 350 - (j % 2) * 30))
    t = E.titulo("O JOGO CERTO\nPRA CADA FESTA", 96, AMA, larg_max=780)
    f.alpha_composite(t, (int(430 - t.width / 2), 90))
    d.text((430, 680), "CALENDÁRIO DE FESTAS", font=E.lilita(56), fill=MAR, anchor="mm")
    d.text((430, 740), "DA SUA VEZ", font=E.lilita(56), fill=LAR, anchor="mm")
    fc = fonte_caneta(54)
    d.text((430, 850), "aniversário, carnaval, amigo secreto...", font=fc, fill=VERM, anchor="mm")
    d.text((430, 915), "tem jogo pra todo evento do ano!", font=fc, fill=PET, anchor="mm")
    for x in range(60, 820, 44):
        d.ellipse((x - 7, 26, x + 7, 40), fill=(205, 210, 214))
    pendura(img, f, W / 2, 150, rot=-1)
    logo_canto(img)
    E.cola(img, E.pilula("arrasta pro lado  →", 32, AMA, MAR), W / 2, 1300, 0)
    return img


def tela_final():
    img = parede(W, H, 99)
    f = Image.new("RGBA", (880, 1080), (252, 252, 250, 255))
    d = ImageDraw.Draw(f)
    d.rectangle((24, 60, 856, 470), fill=LAR)
    t = E.titulo("QUAL É O SEU\nPRÓXIMO EVENTO?", 82, AMA, larg_max=800)
    f.alpha_composite(t, (int(440 - t.width / 2), 110))
    fc = fonte_caneta(58)
    d.text((440, 400), "comenta aqui que a gente indica o jogo!", font=fc, fill=BR, anchor="mm")
    y = 520
    for txt, cor in (("Aluga pelo link na bio", PET), ("3 jogos = 7 dias pelo mesmo preço", MAR),
                     ("Retire em Mauá ou receba em casa", MAR)):
        d.text((440, y), txt, font=E.fig(42, 900), fill=cor, anchor="mm")
        y += 64
    d.line((80, y + 6, 800, y + 6), fill=(225, 225, 225), width=3)
    d.text((440, y + 62), "Quer monitoria no seu evento?", font=E.lilita(46), fill=LAR, anchor="mm")
    d.text((440, y + 118), "A gente leva os jogos e ensina todo mundo:", font=E.fig(34, 800), fill=MAR, anchor="mm")
    d.text((440, y + 166), f"WhatsApp {WHATS}", font=E.fig(40, 900), fill=PET, anchor="mm")
    d.text((440, y + 214), "ABC Paulista e São Paulo capital", font=E.fig(32, 700), fill=MAR, anchor="mm")
    for x in range(60, 840, 44):
        d.ellipse((x - 7, 26, x + 7, 40), fill=(205, 210, 214))
    pendura(img, f, W / 2, 150, rot=0.8)
    lg = E.logo(260)
    img.alpha_composite(lg, (int(W / 2 - lg.width / 2), H - lg.height - 22))
    return img


# ---------------------------------------------------------------- stories
def story_de(tela, seed):
    bg = parede(1080, 1920, seed)
    bg.alpha_composite(tela.convert("RGBA"), (0, 285))
    return bg


def seta(cor):
    im = Image.new("RGBA", (130, 140), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.line([(20, 20), (60, 70), (55, 120)], fill=cor, width=10, joint="curve")
    d.polygon([(30, 105), (80, 108), (54, 136)], fill=cor)
    return im


def story_final():
    img = parede(1080, 1920, 77)
    f = Image.new("RGBA", (880, 860), (252, 252, 250, 255))
    d = ImageDraw.Draw(f)
    d.rectangle((24, 60, 856, 440), fill=LAR)
    t = E.titulo("QUAL É O SEU\nPRÓXIMO EVENTO?", 82, AMA, larg_max=800)
    f.alpha_composite(t, (int(440 - t.width / 2), 100))
    d.text((440, 385), "a gente indica o jogo!", font=fonte_caneta(58), fill=BR, anchor="mm")
    y = 500
    for txt, cor in (("3 jogos = 7 dias pelo mesmo preço", MAR), ("Retire em Mauá ou receba em casa", MAR)):
        d.text((440, y), txt, font=E.fig(42, 900), fill=cor, anchor="mm")
        y += 64
    d.text((440, y + 40), "Monitoria no seu evento:", font=E.lilita(44), fill=LAR, anchor="mm")
    d.text((440, y + 100), f"WhatsApp {WHATS}", font=E.fig(40, 900), fill=PET, anchor="mm")
    for x in range(60, 840, 44):
        d.ellipse((x - 7, 26, x + 7, 40), fill=(205, 210, 214))
    pendura(img, f, 540, 200, rot=0.6)
    lin = Image.new("RGBA", (1080, 150), (0, 0, 0, 0))
    ImageDraw.Draw(lin).text((470, 60), "aluga aqui:", font=E.fig(50, 900), fill=MAR, anchor="mm")
    lin.alpha_composite(seta(MAR), (640, 0))
    img.alpha_composite(lin, (0, 1150))
    # y ≈ 1350–1580 LIVRE para o adesivo de link
    lg = E.logo(240)
    img.alpha_composite(lg, (int(540 - lg.width / 2), 1660))
    return img


def main():
    os.makedirs(os.path.join(OUT, "stories"), exist_ok=True)
    telas = [tela_capa()] + [tela_evento(k) for k in range(len(EVENTOS))] + [tela_final()]
    stories = [story_de(t, 50 + k) for k, t in enumerate(telas[:-1])] + [story_final()]
    for k, im in enumerate(telas):
        im.convert("RGB").save(os.path.join(OUT, f"{k + 1:02d}.png"))
    for k, im in enumerate(stories):
        im.convert("RGB").save(os.path.join(OUT, "stories", f"story_{k + 1:02d}.png"))
    for lista, nome, ww, hh in ((telas, "previa.jpg", W, H), (stories, "previa_stories.jpg", 1080, 1920)):
        w = 300
        h = int(w * hh / ww)
        cols = 6
        rows = (len(lista) + cols - 1) // cols
        sh = Image.new("RGB", (cols * (w + 10) + 10, rows * (h + 10) + 10), (240, 236, 228))
        for k, im in enumerate(lista):
            sh.paste(im.convert("RGB").resize((w, h), Image.LANCZOS),
                     (10 + (k % cols) * (w + 10), 10 + (k // cols) * (h + 10)))
        sh.save(os.path.join(OUT, nome), quality=88)
    print("ok", OUT, len(telas))


if __name__ == "__main__":
    main()
