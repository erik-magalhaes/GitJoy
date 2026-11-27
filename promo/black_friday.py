#!/usr/bin/env python3
"""BLACK FRIDAY da Sua Vez (27 a 29/nov/2026): "ALUGUE 3 JOGOS, O MAIS BARATO É POR NOSSA CONTA" (promoção do site:
Item Mais Barato, mínimo 3 itens, não combina com cupom; válida até domingo 29/11, 23:59). Sem preço na arte (o site
novo tem 5 ou 7 dias com preços diferentes). Visual: preto com brilho dourado e confete, identidade da Jéssica (Lilita/
Figtree, contorno marrom, sombra sólida), 3 caixas com a menor ganhando o carimbo "GRÁTIS".

    /usr/bin/python3 black_friday.py            # out/black_friday/: stories + post + carrossel
    /usr/bin/python3 black_friday.py --reels    # out/black_friday/bf_{com_som,para_musica}_final.mp4 (+ --stories)
"""
import math
import os
import random
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
import estilo as E  # noqa: E402

AC = os.path.join(REPO, "hobby-reels", "assets", "acervo")
OUT = os.path.join(ROOT, "out", "black_friday")
W = 1080
PRETO = (16, 14, 18)
OURO = (255, 199, 31)
VERMELHO = (226, 52, 52)
BRANCO = (255, 255, 255)
CAIXAS = [os.path.join(AC, f) for f in ("wingspan.png", "hitster.png", "sea_salt_paper.png")]  # a última = a "grátis"
LINK = "suavez.acervodejogos.com.br"


@lru_cache(None)
def _fundo(h, semente):
    img = Image.new("RGB", (W, h), PRETO)
    a = np.zeros((h, W), np.float32)
    yy, xx = np.mgrid[0:h, 0:W].astype(np.float32)
    for cx, cy, r, k in [(W * 0.15, h * 0.12, 520, 0.35), (W * 0.9, h * 0.45, 600, 0.25), (W * 0.3, h * 0.92, 560, 0.3)]:
        a += k * np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r))
    luz = np.clip(a, 0, 1)[..., None] * np.array([95, 66, 10], np.float32)
    img = Image.fromarray(np.clip(np.asarray(img, np.float32) + luz, 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(img)
    rnd = random.Random(semente)
    for _ in range(70):  # confete dourado e laranja, mais nas bordas
        x = rnd.choice([rnd.randint(0, 170), rnd.randint(W - 170, W), rnd.randint(0, W)])
        y = rnd.randint(0, h)
        cor = rnd.choice([OURO, E.LARANJA, (255, 236, 160), BRANCO])
        s = rnd.randint(7, 15)
        ang = rnd.uniform(0, math.pi)
        pts = [(x + s * math.cos(ang + k * math.pi / 2) * (1 if k % 2 == 0 else 0.45),
                y + s * math.sin(ang + k * math.pi / 2) * (1 if k % 2 == 0 else 0.45)) for k in range(4)]
        d.polygon(pts, fill=cor)
    return img


def fundo(h, semente=1):
    return _fundo(h, semente).copy()


def centro(img, im, cx, y):
    img.alpha_composite(im, (int(cx - im.width / 2), int(y)))


def faixa_bf(w=900, s=118):
    """Faixa preta e dourada "BLACK FRIDAY" girada, cara de fita de liquidação."""
    t = E.titulo("BLACK FRIDAY", s, cor=OURO, contorno=(0, 0, 0), sw=8, sombra=0)
    b = Image.new("RGBA", (max(w, t.width + 80), t.height + 50), (0, 0, 0, 0))
    d = ImageDraw.Draw(b)
    d.rectangle((0, 0, b.width, b.height), fill=(0, 0, 0, 255))
    for x in range(-60, b.width + 60, 60):  # listras de fita nas bordas
        d.polygon([(x, 0), (x + 30, 0), (x + 10, 14), (x - 20, 14)], fill=OURO)
        d.polygon([(x, b.height - 14), (x + 30, b.height - 14), (x + 10, b.height), (x - 20, b.height)], fill=OURO)
    b.alpha_composite(t, ((b.width - t.width) // 2, 25))
    return b.rotate(-4, expand=True, resample=Image.BICUBIC)


def etiqueta(txt, s, cor, cor_txt, ang=0):
    """Etiqueta de preço pendurada embaixo da caixa (pílula com furinho), texto em 1 ou 2 linhas."""
    linhas = txt.split("\n")
    f = E.lilita(s)
    lw = max(ImageDraw.Draw(Image.new("L", (1, 1))).textlength(l, font=f) for l in linhas)
    w, h = int(lw + 70), int(s * 1.15 * len(linhas) + 30)
    im = Image.new("RGBA", (w + 14, h + 14), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 8, 8 + w, 8 + h), radius=20, fill=E.MARROM)
    d.rounded_rectangle((0, 0, w, h), radius=20, fill=cor, outline=E.MARROM, width=5)
    for k, l in enumerate(linhas):
        d.text((w / 2, 15 + s * 1.15 * (k + 0.5)), l, font=f, fill=cor_txt, anchor="mm")
    return im.rotate(ang, expand=True, resample=Image.BICUBIC) if ang else im


def tres_caixas(h=330, gratis=True, k_gratis=1.0):
    """As 3 caixas lado a lado com etiqueta EMBAIXO de cada uma: as 2 primeiras "VOCÊ PAGA" e a 3ª (a mais barata)
    "ALUGUEL POR NOSSA CONTA" em destaque, ligeiramente maior — fica claro que é o aluguel do 3º jogo."""
    ims = [E.jogo(p, h, int(h * 1.05)) for p in CAIXAS]
    ims[2] = E.jogo(CAIXAS[2], int(h * 0.82), int(h * 0.9))
    ims = [im.rotate([3, -2, -5][i], expand=True, resample=Image.BICUBIC) for i, im in enumerate(ims)]
    s = max(26, int(h * 0.13))
    pagos = [etiqueta("VOCÊ\nPAGA", s, BRANCO, E.MARROM) for _ in range(2)]
    nossa = etiqueta("ALUGUEL POR\nNOSSA CONTA!", int(s * 1.05), OURO, E.MARROM, ang=-4)
    gap = 26
    larg = [max(ims[i].width, (pagos + [nossa])[i].width) for i in range(3)]
    w = sum(larg) + 2 * gap
    alt = max(i.height for i in ims)
    et_h = max(e.height for e in pagos + [nossa])
    out = Image.new("RGBA", (w + 40, alt + et_h + 30), (0, 0, 0, 0))
    x = 20
    for i, im in enumerate(ims):
        cx = x + larg[i] / 2
        out.alpha_composite(im, (int(cx - im.width / 2), alt - im.height))
        if gratis and i == 2 and k_gratis > 0.02:  # só a etiqueta amarela (ele achou 'VOCÊ PAGA' forte)
            e = pagos[i] if i < 2 else nossa
            if i == 2 and k_gratis < 1:
                e = e.resize((max(2, int(e.width * k_gratis)), max(2, int(e.height * k_gratis))), Image.BICUBIC)
            out.alpha_composite(e, (int(cx - e.width / 2), alt + 14))
        x += larg[i] + gap
    return out


def seta_link(img, y, txt="garanta os seus aqui:"):
    t = E.texto(txt, 44, cor=BRANCO, peso=900)
    centro(img, t, W / 2, y)
    d = ImageDraw.Draw(img)
    cx, yy = W // 2, y + t.height + 8
    d.polygon([(cx - 38, yy), (cx + 38, yy), (cx, yy + 52)], fill=OURO, outline=(0, 0, 0), width=5)
    return yy + 52


def logo_topo(img, y=60, w=210):
    lg = E.logo(w)
    centro(img, lg, W / 2, y)
    return y + lg.height


# ------------------------------------------------------------------------------------------------ STORIES
def story_promo():
    H = 1920
    img = fundo(H, 1)
    y = logo_topo(img, 150, 220) + 30
    fb = faixa_bf()
    centro(img, fb, W / 2, y)
    y += fb.height - 10
    t = E.titulo("ALUGUE 3 JOGOS\nE PAGUE SÓ 2!", 92, cor=BRANCO, larg_max=1000)
    centro(img, t, W / 2, y)
    y += t.height - 10
    cx = tres_caixas(270)
    centro(img, cx, W / 2, y + 20)
    # espaço do adesivo de link: y ≈ 1350–1580 (livre)
    seta_link(img, 1370)
    pl = E.pilula("SÓ ATÉ DOMINGO, 29/11", 44, OURO, E.MARROM, fonte_titulo=True)
    centro(img, pl, W / 2, 1610)
    return img


def story_como():
    H = 1920
    img = fundo(H, 2)
    y = logo_topo(img, 150, 200) + 30
    t = E.titulo("COMO FUNCIONA?", 100, cor=OURO, larg_max=980)
    centro(img, t, W / 2, y)
    y += t.height + 10
    passos = [("1", "Escolha 3 jogos ou mais no site", E.LARANJA),
              ("2", "No carrinho, o aluguel do mais barato fica por nossa conta", E.PETROLEO),
              ("3", "Retire em Mauá ou receba em casa", (120, 70, 160))]
    for n, txt, cor in passos:
        card = E.bloco(900, 170, (255, 248, 232), raio=34, ow=7, sombra=10)
        d = ImageDraw.Draw(card)
        d.ellipse((30, 25, 150, 145), fill=cor, outline=E.MARROM, width=6)
        d.text((90, 88), n, font=E.lilita(80), fill=BRANCO, anchor="mm")
        tx = E.texto(txt, 42, cor=E.MARROM, peso=800, larg_max=680, alinha="lm")
        card.alpha_composite(tx, (180, (170 - tx.height) // 2))
        centro(img, card, W / 2, y)
        y += 200
    cx = tres_caixas(150)
    centro(img, cx, W / 2, y - 10)
    seta_link(img, 1400, "corre pro site:")
    pl = E.pilula("BLACK FRIDAY · SÓ ATÉ DOMINGO, 29/11", 36, OURO, E.MARROM, fonte_titulo=True)
    centro(img, pl, W / 2, 1610)
    return img


def story_ultimo():
    H = 1920
    img = fundo(H, 3)
    y = logo_topo(img, 150, 200) + 40
    t = E.titulo("ÚLTIMO DIA!", 150, cor=OURO, larg_max=980)
    centro(img, t, W / 2, y)
    y += t.height
    t2 = E.titulo("BLACK FRIDAY ACABA HOJE,\nÀS 23:59", 66, cor=BRANCO, larg_max=980)
    centro(img, t2, W / 2, y)
    y += t2.height + 10
    t3 = E.texto("3 jogos no carrinho: o aluguel do mais barato fica por nossa conta", 40, cor=BRANCO, peso=800, larg_max=880)
    centro(img, t3, W / 2, y)
    cx = tres_caixas(230)
    centro(img, cx, W / 2, y + t3.height + 20)
    seta_link(img, 1330)
    return img


# ------------------------------------------------------------------------------------------------ POST / CARROSSEL
def post():
    H = 1350
    img = fundo(H, 4)
    lg = E.logo(170)
    img.alpha_composite(lg, (W - lg.width - 36, 36))
    fb = faixa_bf(820, 108)
    centro(img, fb, W / 2 - 40, 60)
    t = E.titulo("ALUGUE 3 JOGOS\nE PAGUE SÓ 2!", 88, cor=BRANCO, larg_max=1000)
    centro(img, t, W / 2, 60 + fb.height - 10)
    cx = tres_caixas(270)
    centro(img, cx, W / 2, 60 + fb.height + t.height + 10)
    pl = E.pilula("SÓ ATÉ DOMINGO, 29/11 · LINK NA BIO", 38, OURO, E.MARROM, fonte_titulo=True)
    centro(img, pl, W / 2, H - pl.height - 50)
    return img


def post_como():
    H = 1350
    img = fundo(H, 6)
    lg = E.logo(170)
    img.alpha_composite(lg, (W - lg.width - 36, 36))
    t = E.titulo("COMO FUNCIONA?", 100, cor=OURO, larg_max=760)
    img.alpha_composite(t, (50, 60))
    y = 60 + t.height + 30
    passos = [("1", "Escolha 3 jogos ou mais no site", E.LARANJA),
              ("2", "No carrinho, o aluguel do mais barato fica por nossa conta", E.PETROLEO),
              ("3", "Retire em Mauá ou receba em casa", (120, 70, 160))]
    for n, txt, cor in passos:
        card = E.bloco(900, 170, (255, 248, 232), raio=34, ow=7, sombra=10)
        d = ImageDraw.Draw(card)
        d.ellipse((30, 25, 150, 145), fill=cor, outline=E.MARROM, width=6)
        d.text((90, 88), n, font=E.lilita(80), fill=BRANCO, anchor="mm")
        tx = E.texto(txt, 42, cor=E.MARROM, peso=800, larg_max=680, alinha="lm")
        card.alpha_composite(tx, (180, (170 - tx.height) // 2))
        centro(img, card, W / 2, y)
        y += 200
    cx = tres_caixas(190)
    centro(img, cx, W / 2, y - 10)
    pl = E.pilula("SÓ ATÉ DOMINGO, 29/11 · LINK NA BIO", 38, OURO, E.MARROM, fonte_titulo=True)
    centro(img, pl, W / 2, H - pl.height - 40)
    return img


def vitrine(h=380, gap=36, refl=True):
    """As 3 caixas EM PÉ, retas, numa prateleira escura com reflexo e sombra; brilho dourado atrás da 3ª (a do
    aluguel por nossa conta) e a etiqueta amarela pendurada embaixo dela."""
    ims = [E.jogo(p, h, int(h * 1.0)) for p in CAIXAS]
    w = sum(i.width for i in ims) + 2 * gap
    out = Image.new("RGBA", (w + 240, int(h * 1.95)), (0, 0, 0, 0))
    base = h + 130
    x = 120
    pos = []
    for im in ims:
        pos.append((x, base - im.height))
        x += im.width + gap
    # brilho dourado atrás da 3ª
    gx, gy = pos[2][0] + ims[2].width / 2, base - ims[2].height / 2
    glow = Image.new("L", out.size, 0)
    ImageDraw.Draw(glow).ellipse((gx - ims[2].width * 0.95, gy - ims[2].height * 0.85, gx + ims[2].width * 0.95,
                                  gy + ims[2].height * 0.75), fill=200)
    glow = glow.filter(ImageFilter.GaussianBlur(40))
    out.alpha_composite(Image.composite(Image.new("RGBA", out.size, OURO + (255,)), Image.new("RGBA", out.size, (0, 0, 0, 0)),
                                        glow.point(lambda v: int(v * 0.45))))
    d = ImageDraw.Draw(out)
    d.rounded_rectangle((70, base - 4, out.width - 70, base + 16), radius=8, fill=(60, 44, 30))  # prateleira
    d.rectangle((70, base - 4, out.width - 70, base), fill=(110, 84, 50))
    for (px, py), im in zip(pos, ims):
        if refl:  # reflexo na prateleira
            r = im.transpose(Image.FLIP_TOP_BOTTOM).crop((0, 0, im.width, int(im.height * 0.25)))
            m = Image.new("L", r.size)
            for yy in range(r.height):
                ImageDraw.Draw(m).line((0, yy, r.width, yy), fill=int(70 * (1 - yy / r.height)))
            r.putalpha(Image.composite(r.getchannel("A"), Image.new("L", r.size, 0), m).point(lambda v: min(v, 70)))
            out.alpha_composite(r, (int(px), base + 16))
        out.alpha_composite(im, (int(px), int(py)))
    e = etiqueta("ALUGUEL POR\nNOSSA CONTA!", int(h * 0.085), OURO, E.MARROM, ang=-3)
    ex = pos[2][0] + ims[2].width / 2
    out.alpha_composite(e, (int(min(out.width - e.width - 4, ex - e.width / 2)), base + 28))
    return out


def titulo_2(s=96):
    """ "ALUGUE 3 JOGOS / E PAGUE SÓ 2!" com o 2 grande em dourado."""
    l1 = E.titulo("ALUGUE 3 JOGOS", s, cor=BRANCO, larg_max=1000)
    a = E.titulo("E PAGUE SÓ", s, cor=BRANCO)
    n = E.titulo("2!", int(s * 1.55), cor=OURO)
    l2 = Image.new("RGBA", (a.width + n.width - 20, max(a.height, n.height)), (0, 0, 0, 0))
    l2.alpha_composite(a, (0, l2.height - a.height - int(s * 0.08)))
    l2.alpha_composite(n, (a.width - 20, 0))
    sob = int(s * 0.75)
    out = Image.new("RGBA", (max(l1.width, l2.width), l1.height + l2.height - sob), (0, 0, 0, 0))
    out.alpha_composite(l2, ((out.width - l2.width) // 2, l1.height - sob))
    out.alpha_composite(l1, ((out.width - l1.width) // 2, 0))
    return out


def fita_topo(img, y, s=84):
    """Fita BLACK FRIDAY reta de ponta a ponta."""
    t = E.titulo("BLACK FRIDAY", s, cor=OURO, contorno=(0, 0, 0), sw=7, sombra=0)
    h = t.height + 36
    b = Image.new("RGBA", (W + 200, h), (0, 0, 0, 255))
    d = ImageDraw.Draw(b)
    for x in range(-60, b.width + 60, 54):
        d.polygon([(x, 0), (x + 27, 0), (x + 9, 12), (x - 18, 12)], fill=OURO)
        d.polygon([(x, h - 12), (x + 27, h - 12), (x + 9, h), (x - 18, h)], fill=OURO)
    b.alpha_composite(t, ((b.width - t.width) // 2, 18))
    b = b.rotate(-2.5, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(b, (int(W / 2 - b.width / 2), int(y)))
    return y + b.height


def post_q():
    """Versão QUADRADA 1080x1080, refeita (ele achou a 1ª pobre e com os jogos tortos)."""
    H = 1080
    img = fundo(H, 7)
    y = fita_topo(img, 18)
    t = titulo_2(84)
    centro(img, t, W / 2, y - 6)
    v = vitrine(300)
    centro(img, v, W / 2, y + t.height - 120)
    pl = E.pilula("SÓ ATÉ DOMINGO, 29/11 · LINK NA BIO", 34, OURO, E.MARROM, fonte_titulo=True)
    centro(img, pl, W / 2, H - pl.height - 30)
    lg = E.logo(130)
    img.alpha_composite(lg, (24, H - lg.height - 24))
    return img


def post_como_q():
    H = 1080
    img = fundo(H, 8)
    y = fita_topo(img, 18, 70)
    t = E.titulo("COMO FUNCIONA?", 92, cor=BRANCO, larg_max=980)
    centro(img, t, W / 2, y + 6)
    y += t.height + 24
    passos = [("1", "Escolha 3 jogos ou mais no site", E.LARANJA),
              ("2", "O aluguel do mais barato\nfica por nossa conta", OURO),
              ("3", "Retire em Mauá ou receba em casa", E.PETROLEO)]
    for i, (n, txt, cor) in enumerate(passos):
        card = E.bloco(940, 168, (255, 248, 232), raio=34, ow=7, sombra=10)
        d = ImageDraw.Draw(card)
        d.rounded_rectangle((22, 22, 146, 146), radius=26, fill=cor, outline=E.MARROM, width=6)
        d.text((84, 88), n, font=E.lilita(88), fill=BRANCO if cor != OURO else E.MARROM, anchor="mm")
        tx = E.titulo(txt.upper(), 44, cor=E.MARROM, contorno=E.MARROM, sw=0, sombra=0, larg_max=730)
        card.alpha_composite(tx, (176, (168 - tx.height) // 2))
        centro(img, card, W / 2, y)
        y += 192
    pl = E.pilula("SÓ ATÉ DOMINGO, 29/11 · LINK NA BIO", 34, OURO, E.MARROM, fonte_titulo=True)
    centro(img, pl, W / 2, H - pl.height - 30)
    return img


def story_de(tela, semente):
    st = fundo(1920, semente)
    st.alpha_composite(tela, (0, 285))
    return st


# ------------------------------------------------------------------------------------------------ REELS (curto)
def ease(x):
    x = min(max(x, 0), 1)
    return 1 - (1 - x) ** 3


def back(x):
    x = min(max(x, 0), 1)
    c = 1.9
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


DUR = 12.0


def quadro_reels(t, stories=False):
    H = 1920
    img = fundo(H, 5)
    lg = E.logo(200)
    centro(img, lg, W / 2, 140)
    # 0–1,2: faixa BLACK FRIDAY bate
    k = back(t / 0.45)
    fb = faixa_bf()
    if k > 0.02:
        s = 0.4 + 0.6 * k if t < 0.45 else 1.0
        f2 = fb.resize((int(fb.width * s), int(fb.height * s)), Image.BICUBIC)
        centro(img, f2, W / 2, 330 + (fb.height - f2.height) / 2)
    # 0,8: título linha a linha
    linhas = ["ALUGUE 3 JOGOS", "E PAGUE SÓ 2!"]
    y = 330 + fb.height
    for i, l in enumerate(linhas):
        kk = ease((t - 0.8 - i * 0.35) / 0.3)
        if kk > 0:
            tt = E.titulo(l, 92, cor=OURO if i == 2 else BRANCO, larg_max=1000)
            tt2 = tt.copy()
            tt2.putalpha(tt.getchannel("A").point(lambda v: int(v * kk)))
            centro(img, tt2, W / 2, y + (1 - kk) * 40)
        y += 100
    # 2,2: caixas caem uma a uma; 4,0: carimbo GRÁTIS
    ims = [E.jogo(p, 280, 300) for p in CAIXAS]
    ims[2] = E.jogo(CAIXAS[2], 230, 250)
    xs = [W / 2 - 330, W / 2, W / 2 + 320]
    base = 1300
    for i, im in enumerate(ims):
        kk = back((t - 2.2 - i * 0.35) / 0.4)
        if kk > 0.01:
            im2 = im.rotate([3, -2, -5][i], expand=True, resample=Image.BICUBIC)
            img.alpha_composite(im2, (int(xs[i] - im2.width / 2), int(base - im2.height - (1 - kk) * 500)))
    kg = back((t - 3.8) / 0.35)
    if kg > 0.02:
        c = etiqueta("ALUGUEL POR\nNOSSA CONTA!", 28, OURO, E.MARROM, ang=-4)
        c = c.resize((max(2, int(c.width * kg)), max(2, int(c.height * kg))), Image.BICUBIC)
        centro(img, c, xs[2], base + 12)
    # 5,0: regra e prazo
    if t > 5.0:
        a = ease((t - 5.0) / 0.4)
        tx = E.texto("3 jogos ou mais no carrinho:\no aluguel do mais barato fica por nossa conta!", 44, cor=BRANCO, peso=800, larg_max=900)
        tx2 = tx.copy()
        tx2.putalpha(tx.getchannel("A").point(lambda v: int(v * a)))
        centro(img, tx2, W / 2, 1340)
    if t > 6.5:
        kk = back((t - 6.5) / 0.35)
        pl = E.pilula("SÓ ATÉ DOMINGO, 29/11", 48, OURO, E.MARROM, fonte_titulo=True)
        pl = pl.resize((max(2, int(pl.width * kk)), max(2, int(pl.height * kk))), Image.BICUBIC)
        centro(img, pl, W / 2, 1490)
    if t > 8.0:
        kk = ease((t - 8.0) / 0.4)
        if stories:
            seta = Image.new("RGBA", (W, 400), (0, 0, 0, 0))
            seta_link(seta, 0, "garanta os seus aqui:")
            seta.putalpha(seta.getchannel("A").point(lambda v: int(v * kk)))
            img.alpha_composite(seta, (0, 1580))
        else:
            pl = E.pilula("RESERVE PELO LINK NA BIO · @SUAVEZ_BG", 36, E.LARANJA, BRANCO, fonte_titulo=True)
            pl.putalpha(pl.getchannel("A").point(lambda v: int(v * kk)))
            centro(img, pl, W / 2, 1600)
            c = E.texto("Comenta: quais 3 você levaria?", 40, cor=OURO, peso=900)
            c.putalpha(c.getchannel("A").point(lambda v: int(v * kk)))
            centro(img, c, W / 2, 1700)
    return img


def reels(stories=False):
    import subprocess
    import imageio_ffmpeg
    sys.path.insert(0, os.path.join(REPO, "becas-reels"))
    import sons as S
    FF = imageio_ffmpeg.get_ffmpeg_exe()
    nome = "bf_stories" if stories else "bf"
    ev = [(0.0, S.estouro(), 0.6)] + [(2.2 + i * 0.35, S.louca(1800 - i * 200), 0.5) for i in range(3)] + \
         [(3.8, S.carimbo() if hasattr(S, "carimbo") else S.estouro(), 0.7), (6.5, S.plim(), 0.5), (8.0, S.sino(), 0.4)]
    mus = S.musica_pop(DUR + 1, 0.0)
    com, sem = os.path.join(OUT, f"_{nome}_com.wav"), os.path.join(OUT, f"_{nome}_sem.wav")
    S.grava(com, DUR, ev, mus, musica_ganho=0.45, fx_ganho=0.8)
    S.grava(sem, DUR, ev, None, fx_ganho=0.8)
    for wav, suf in ((com, "com_som"), (sem, "para_musica")):
        tmp = os.path.join(OUT, f"_{nome}_{suf}.mp4")
        wr = imageio_ffmpeg.write_frames(tmp, (W, 1920), fps=30, codec="libx264", quality=None,
                                         output_params=["-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p"],
                                         audio_path=wav, audio_codec="aac")
        wr.send(None)
        for i in range(int(DUR * 30)):
            wr.send(quadro_reels(i / 30, stories).convert("RGB").tobytes())
        wr.close()
        final = os.path.join(OUT, f"{nome}_{suf}_final.mp4")
        subprocess.run([FF, "-v", "error", "-y", "-i", tmp, "-c:v", "copy", "-af", "loudnorm=I=-15.5:TP=-2:LRA=11",
                        "-ar", "44100", "-c:a", "aac", "-b:a", "192k", final], check=True)
        print("ok", final)


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--reels" in sys.argv:
        reels("--stories" in sys.argv)
        return
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:]]
        ims = [quadro_reels(t).convert("RGB").resize((360, 640)) for t in ts]
        f = Image.new("RGB", (370 * len(ims), 640), (255, 255, 255))
        for i, im in enumerate(ims):
            f.paste(im, (i * 370, 0))
        f.save(os.path.join(OUT, "frames.jpg"), quality=88)
        return
    saidas = {"story_1_promo": story_promo(), "story_2_como_funciona": story_como(), "story_3_ultimo_dia": story_ultimo(),
              "post_1": post(), "post_2_como_funciona": post_como(),
              "quadrado_1": post_q(), "quadrado_2_como_funciona": post_como_q()}
    for n, im in saidas.items():
        im.convert("RGB").save(os.path.join(OUT, n + ".png"))
    os.makedirs(os.path.join(OUT, "stories_do_carrossel"), exist_ok=True)
    for i, n in enumerate(("post_1", "post_2_como_funciona")):
        story_de(saidas[n], 10 + i).convert("RGB").save(os.path.join(OUT, "stories_do_carrossel", f"story_{i + 1:02d}.png"))
    f = Image.new("RGB", (3 * 400 + 2 * 420 + 60, 760), (255, 255, 255))
    x = 10
    for n in ("story_1_promo", "story_2_como_funciona", "story_3_ultimo_dia"):
        f.paste(saidas[n].convert("RGB").resize((400, 711)), (x, 10))
        x += 410
    for n in ("post_1", "post_2_como_funciona"):
        f.paste(saidas[n].convert("RGB").resize((420, 525)), (x, 10))
        x += 430
    f.save(os.path.join(OUT, "previa.jpg"), quality=88)
    print("ok")


if __name__ == "__main__":
    main()
