#!/usr/bin/env python3
"""DOMINGO DE JOGOS DE NATAL (13/12) — material FOCADO NO PRÓXIMO EVENTO (27/nov/2026).

Ele achou o material anterior "muito focado no que já aconteceu" (abria com "lembra da nossa tarde?") e as
informações do evento só apareciam no fim. Regra desta leva: a DATA e o aviso EVENTO FECHADO / SÓ COM RESERVA vêm na
1ª tela e no 1º segundo, e continuam à vista o tempo todo (rodapé fixo no carrossel e faixa fixa no vídeo).
Material: as fotos novas que eles mandaram (pátio das guarda-chuvinhas, lanches do Beca’s, jogos novos) em
`assets/natal/`. Nada do evento de 20/11. O mínimo de 15 pessoas é INTERNO e não aparece em nenhuma peça.

    /usr/bin/python3 natal_fechado.py --fotos       # out/natal_fechado/01..07.png + stories/ + previa.jpg
    /usr/bin/python3 natal_fechado.py --frame 0.1 2 5 9 12 16 [--stories]
    /usr/bin/python3 natal_fechado.py               # out/fechado_{reels,stories}_{com_som,para_musica}_final.mp4
"""
import math
import os
import sys
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter, ImageOps

import kit as K
import sons as S
import domingo as D
import domingo_carrossel as DC
from tarde import E, TB, W, H, MAR, PET, LAR, AMA, BR, ROSA
from motor import FPS

ROOT = os.path.dirname(os.path.abspath(__file__))
FOTOS = os.path.join(ROOT, "assets", "natal")
PASTA = os.path.join(D.OUT, "natal_fechado")
CW, CH = 1080, 1350
VERDE = (24, 110, 66)
NOITE = (40, 14, 10)


@lru_cache(None)
def foto(nome):
    return Image.open(os.path.join(FOTOS, nome + ".jpg")).convert("RGB")


def pol(nome, w, h, leg, ay=0.5):
    return DC.polaroide(foto(nome), w, h, leg, ay)


# ---------------------------------------------------------------- peças
@lru_cache(None)
def rodape(w=CW):
    """Faixa fixa do pé de cada tela: quem não rodar o carrossel inteiro já sabe do evento."""
    h = 92
    im = Image.new("RGBA", (w, h), VERDE + (255,))
    d = ImageDraw.Draw(im)
    d.line((0, 3, w, 3), fill=MAR, width=6)
    for x in range(-40, w + 40, 46):   # listrinha dourada
        d.line((x, 10, x + 14, 10), fill=AMA, width=3)
    txt = "DOMINGO 13/12 · 30 VAGAS · RESERVE PELO LINK NA BIO"
    d.text((w / 2, 54), txt, font=D.cabe(txt, w - 60, 44), fill=BR, anchor="mm")
    return im


@lru_cache(None)
def ingresso(w=960, h=640):
    """O convite em forma de INGRESSO: foto do pátio no canhoto + todas as informações."""
    c = E.bloco(w, h, D.CREME, raio=36, ow=8, sombra=16).copy()
    d = ImageDraw.Draw(c)
    fw = 330
    f = ImageOps.fit(foto("patio"), (fw - 40, h - 60), Image.LANCZOS, centering=(0.5, 0.35)).convert("RGBA")
    m = Image.new("L", f.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, f.width - 1, f.height - 1), 22, fill=255)
    c.paste(f, (24, 30), m)
    d.rounded_rectangle((24, 30, 24 + f.width - 1, 30 + f.height - 1), 22, outline=MAR, width=4)
    for y in range(26, h - 20, 26):   # picote
        d.line((fw + 8, y, fw + 8, y + 13), fill=MAR, width=5)
    for y in (0, h):                  # meias-luas do picote
        d.ellipse((fw + 8 - 22, y - 22, fw + 8 + 22, y + 22), fill=(0, 0, 0, 0), outline=MAR, width=6)
    cx = fw + 8 + (w - fw - 8) / 2
    lx = w - fw - 70
    sel = E.pilula("ESPECIAL DE NATAL", 34, VERDE, BR, fonte_titulo=True)
    c.alpha_composite(sel, (int(cx - sel.width / 2), 38))
    d.text((cx, 162), "DOMINGO\nDE JOGOS", font=E.lilita(84), fill=LAR, anchor="mm", align="center",
           stroke_width=5, stroke_fill=MAR, spacing=-6)
    dt = E.pilula("DOMINGO, 13/12 · 13H ÀS 19H", 34, AMA, MAR, fonte_titulo=True)
    c.alpha_composite(dt, (int(cx - dt.width / 2), 262))
    d.text((cx, 360), "Beca’s Café", font=E.fig(36, 900), fill=MAR, anchor="mm")
    d.text((cx, 404), "Rua Sorocaba, 35 · Mauá", font=E.fig(30, 700), fill=MAR, anchor="mm")
    d.text((cx, 470), "R$ 40", font=E.lilita(70), fill=PET, anchor="mm", stroke_width=4, stroke_fill=MAR)
    d.text((cx, 528), "R$ 25 viram consumação no café", font=E.fig(28, 800), fill=MAR, anchor="mm")
    d.rounded_rectangle((fw + 40, 560, w - 30, 616), 26, fill=D.VERM)
    d.text((cx, 588), "SÓ 30 VAGAS", font=E.lilita(36), fill=BR, anchor="mm")
    return c


@lru_cache(None)
def carimbo(txt="EVENTO FECHADO", sub="SÓ ENTRA QUEM TEM RESERVA", s=78):
    f, f2 = E.lilita(s), E.lilita(int(s * 0.42))
    dd = ImageDraw.Draw(Image.new("L", (1, 1)))
    w = int(max(dd.textlength(txt, font=f), dd.textlength(sub, font=f2)) + 80)
    h = int(s * 1.9)
    im = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((14, 16, w + 14, h + 16), 22, fill=MAR)
    d.rounded_rectangle((4, 4, w, h), 22, fill=BR, outline=MAR, width=6)
    d.rounded_rectangle((16, 16, w - 12, h - 12), 16, outline=D.VERM, width=5)
    d.text((w / 2 + 2, h * 0.40), txt, font=f, fill=D.VERM, anchor="mm")
    d.text((w / 2 + 2, h * 0.78), sub, font=f2, fill=MAR, anchor="mm")
    return im


def passo(n, txt, cor, w=880):
    c = E.bloco(w, 150, BR, raio=30, ow=6, sombra=10).copy()
    d = ImageDraw.Draw(c)
    d.ellipse((24, 22, 130, 128), fill=cor, outline=MAR, width=5)
    d.text((77, 76), str(n), font=E.lilita(66), fill=BR if cor != AMA else MAR, anchor="mm")
    tx = E.texto(txt, 40, MAR, 800, larg_max=w - 190, alinha="lm")
    c.alpha_composite(tx, (160, (150 - tx.height) // 2))
    return c


# ---------------------------------------------------------------- carrossel
def base(livres=()):
    img = DC.base(livres=livres)
    img.alpha_composite(rodape(), (0, CH - rodape().height))
    return img


def t_capa():
    img = DC.base()
    E.cola(img, E.titulo("VEM AÍ!", 110, AMA), 540, 320, -3, 1, 1)
    E.cola(img, ingresso(), 540, 790, 1, 1, 1)
    E.cola(img, E.titulo("RESERVE JÁ!", 96, AMA), 540, 1185, -2, 1, 1)
    E.cola(img, E.pilula("ARRASTA PRO LADO →", 30, BR, MAR, fonte_titulo=True), 540, 1290, 1, 1, 1)
    return img.convert("RGB")


def t_exclusivo():
    img = base(livres=(540,))
    DC.pendura(img, pol("patio", 600, 560, "o Beca’s só pra gente", 0.4), 540, 390, ROSA, -2, 160)
    E.cola(img, E.titulo("UM DOMINGO\nSÓ NOSSO NO\nBECA’S CAFÉ!", 92, AMA), 540, 280, -2, 1, 1)
    E.cola(img, E.pilula("O Beca’s não abre aos domingos: nesse, ele é todo nosso!", 31, BR, MAR), 540, 1180, 1, 1, 1)
    return img.convert("RGB")


def t_cafe():
    img = base(livres=(200, 540, 880))
    DC.pendura(img, pol("lanche", 270, 340, "lanche quentinho", 0.45), 200, 470, ROSA, 3, 130)
    DC.pendura(img, pol("bebidas", 270, 340, "bebidas da casa", 0.5), 540, 540, AMA, -2, 130)
    DC.pendura(img, pol("croissant", 270, 340, "croissant", 0.5), 880, 470, PET, 3, 130)
    E.cola(img, E.titulo("R$ 25 VIRAM\nCONSUMAÇÃO", 104, AMA), 540, 290, -2, 1, 1)
    E.cola(img, E.pilula("Ingresso R$ 40: o lanche já tá incluso!", 36, BR, MAR), 540, 1180, 1, 1, 1)
    return img.convert("RGB")


def t_jogos():
    img = base(livres=(160, 410, 670, 920))
    for (n, leg, ay), x, y, cor, r in zip((("boop", "boop.", 0.4), ("seasalt", "Sea Salt & Paper", 0.5),
                                           ("flamecraft", "Flamecraft", 0.5), ("monkey", "Monkey Palace", 0.4)),
                                          (160, 410, 670, 920), (520, 600, 520, 600),
                                          (ROSA, AMA, PET, LAR), (3, -2, 2, -3)):
        DC.pendura(img, pol(n, 200, 270, leg, ay), x, y, cor, r, 110)
    E.cola(img, E.titulo("E A MESA FICA\nCHEIA DE JOGO", 100, AMA), 540, 290, -2, 1, 1)
    E.cola(img, E.pilula("Mais de 30 jogos e a gente ENSINA todos!", 36, BR, MAR), 540, 1180, 1, 1, 1)
    return img.convert("RGB")


def t_como():
    img = base()
    E.cola(img, E.titulo("COMO GARANTIR\nA SUA VAGA?", 100, AMA), 540, 290, -2, 1, 1)
    for k, (txt, cor) in enumerate((("Toca no link da nossa bio", LAR),
                                    ("Faça a sua reserva antes do dia", PET),
                                    ("No domingo, é só chegar e jogar!", VERDE))):
        E.cola(img, passo(k + 1, txt, cor), 540, 560 + k * 185, (-1, 1, -1)[k], 1, 1)
    E.cola(img, E.pilula("Garanta antes: as vagas são limitadas!", 38, AMA, MAR, fonte_titulo=True), 540, 1140, 2, 1, 1)
    return img.convert("RGB")


def t_vagas():
    img = base()
    E.cola(img, E.titulo("SÓ 30 VAGAS!", 120, AMA), 540, 270, 2, 1, 1)
    E.cola(img, D.painel(0), 540, 700, 0, 0.9, 1)
    E.cola(img, E.pilula("QUANTO ANTES, MELHOR!", 46, PET, BR, fonte_titulo=True), 540, 1095, -1, 1, 1)
    E.cola(img, E.pilula("Esgotou? Só lista de espera.", 36, BR, MAR), 540, 1180, 1, 1, 1)
    return img.convert("RGB")


def t_final():
    img = base()
    E.cola(img, TB.parceria(90), 540, 230, 0, 1, 1)
    E.cola(img, E.pilula("ESPECIAL DE NATAL", 40, VERDE, BR, fonte_titulo=True), 540, 345, -1, 1, 1)
    E.cola(img, D.card(), 540, 690, 0, 0.95, 1)
    E.cola(img, E.pilula("RESERVE PELO LINK NA BIO", 44, PET, BR, fonte_titulo=True), 540, 1045, -1, 1, 1)
    E.cola(img, E.pilula("Marca aqui quem vem com você!", 36, BR, MAR), 540, 1140, 1, 1, 1)
    return img.convert("RGB")


TELAS = [t_capa, t_exclusivo, t_cafe, t_jogos, t_como, t_vagas, t_final]


def fotos():
    os.makedirs(os.path.join(PASTA, "stories"), exist_ok=True)
    ims = [f() for f in TELAS]
    for k, im in enumerate(ims):
        im.save(os.path.join(PASTA, f"{k + 1:02d}.png"))
        DC.story_de(im, k == len(ims) - 1).save(os.path.join(PASTA, "stories", f"story_{k + 1:02d}.png"))
    sh = Image.new("RGB", (len(ims) * 360, 450), "white")
    for k, im in enumerate(ims):
        sh.paste(im.resize((360, 450)), (k * 360, 0))
    sh.save(os.path.join(PASTA, "previa.jpg"), quality=88)


# ---------------------------------------------------------------- vídeo
D.BASE_FUNDO = lru_cache(None)(lambda: DC.fundo_natal("vermelho"))
D.COR_SELO, D.COR_VAGAS = VERDE, AMA

T_GANCHO = 3.4
CENAS = [("lanche", "SEUS R$ 25 VIRAM CONSUMAÇÃO", 0.45), ("bebidas", "CAFÉ E DOCINHO NA MESA", 0.5),
         ("boop", "+ DE 30 JOGOS NA MESA", 0.4), ("flamecraft", "A GENTE ENSINA TUDO", 0.5),
         ("seasalt", "JOGO RAPIDINHO...", 0.5), ("monkey", "...OU JOGÃO", 0.45)]
CORTE = 2 * 60 / 118
T_TIT = T_GANCHO + len(CENAS) * CORTE
T_QUADRO = T_TIT + 3.2
T_CTA = T_QUADRO + 3.8
DUR = T_CTA + 6.2
D.T_TIT, D.T_QUADRO, D.T_CTA = T_TIT, T_QUADRO, T_CTA


@lru_cache(None)
def tela_cheia(nome, ay):
    im = ImageOps.fit(foto(nome), (W + 120, H + 214), Image.LANCZOS, centering=(0.5, ay))
    return im.convert("RGBA")


def ken(nome, ay, u, d):
    """Aproximação lenta dentro da foto (corta da imagem maior)."""
    im = tela_cheia(nome, ay)
    k = min(1.0, u / d)
    z = 1 + 0.06 * k
    w, h = (W + 120) / z, (H + 214) / z
    x0, y0 = ((W + 120) - w) / 2, ((H + 214) - h) / 2
    return im.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h))


@lru_cache(None)
def faixa_video():
    h = 112
    im = Image.new("RGBA", (W, h), VERDE + (240,))
    d = ImageDraw.Draw(im)
    d.line((0, h - 3, W, h - 3), fill=MAR, width=6)
    txt = "DOMINGO 13/12 · 30 VAGAS · RESERVE JÁ"
    d.text((W / 2, h / 2), txt, font=D.cabe(txt, W - 70, 46), fill=BR, anchor="mm")
    return im


def gancho(img, t):
    img.alpha_composite(ken("patio", 0.4, t, T_GANCHO))
    K.escurece(img, 380, 1500, 200)
    # tudo já na tela no 1º quadro (sem esperar animação)
    E.cola(img, E.pilula("ESPECIAL DE NATAL", 56, VERDE, BR, fonte_titulo=True), W / 2, 600, -3, 1 + 0.04 * max(0, 1 - t / 0.25), 1)
    E.cola(img, E.titulo("DOMINGO DE JOGOS\nDE NATAL", 104, AMA), W / 2, 860, -1, 1, 1)
    E.cola(img, E.pilula("DOMINGO, 13/12 · 13H ÀS 19H", 52, BR, MAR, fonte_titulo=True), W / 2, 1060, 1, 1, 1)
    E.cola(img, E.pilula("NO BECA’S CAFÉ · MAUÁ", 46, PET, BR, fonte_titulo=True), W / 2, 1160, -1, 1, 1)
    K.poe(img, K.etiqueta("SÓ 30 VAGAS: RESERVE JÁ!", 56, D.VERM, BR), W / 2, 1300, t, 0.9, 2)


def cenas(img, t):
    k = min(len(CENAS) - 1, int((t - T_GANCHO) / CORTE))
    u = t - T_GANCHO - k * CORTE
    nome, rot, ay = CENAS[k]
    img.alpha_composite(ken(nome, ay, u, CORTE))
    K.escurece(img, 1230, 1580, 160)
    K.poe(img, K.etiqueta(rot, 62, AMA, MAR), W / 2, 1400, t, T_GANCHO + k * CORTE, -2 if k % 2 else 2, d=0.22)


def quadro(t, modo="reels"):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    if t < T_GANCHO:
        gancho(img, t)
    elif t < T_TIT:
        cenas(img, t)
    elif t < T_QUADRO:
        D.titulo(img, t)
    elif t < T_CTA:
        D.quadro_vagas(img, t)
    else:
        D.cta(img, t, modo)
    if T_GANCHO <= t < T_TIT:          # faixa fixa com a data enquanto passam as fotos
        img.alpha_composite(faixa_video(), (0, 250))
    for tb in (T_GANCHO, T_TIT, T_QUADRO, T_CTA):
        dd = t - tb
        if 0 <= dd < 0.12:
            img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(200 * (1 - dd / 0.12)))))
    if t < T_TIT:
        K.marca(img)
    return img.convert("RGB")


def render_reels(fi):
    return quadro(fi / FPS, "reels").tobytes()


def render_stories(fi):
    return quadro(fi / FPS, "stories").tobytes()


def audio(nome):
    ev = [(0.0, S.estouro(), 0.5), (0.02, S.sino(), 0.4), (0.9, S.plim(), 0.45)]
    ev += [(T_GANCHO + k * CORTE, S.sopro(0.25), 0.3) for k in range(len(CENAS))]
    ev += [(T_TIT, S.sino(), 0.45), (T_TIT + 0.35, S.estouro(), 0.4), (T_QUADRO + 0.05, S.estouro(), 0.5)]
    ev += [(T_QUADRO + 0.25 + k * 0.045, S.tic(k % 2 == 0), 0.18) for k in range(D.VAGAS)]
    ev += [(T_QUADRO + 2.4, S.plim(), 0.45), (T_CTA, S.sopro(0.5, False), 0.4), (T_CTA + 0.35, S.carta_vira(), 0.5)]
    mus = S.musica_pop(DUR + 0.5, 0.0)
    com = os.path.join(D.OUT, f"{nome}_com.wav")
    sem = os.path.join(D.OUT, f"{nome}_sem.wav")
    S.grava(com, DUR, ev, mus, musica_ganho=0.42, fx_ganho=0.75)
    S.grava(sem, DUR, ev, None, fx_ganho=0.75)
    return com, sem


def main():
    args = sys.argv[1:]
    if "--fotos" in args:
        fotos()
        print("ok fotos")
        return
    modo = "stories" if "--stories" in args else "reels"
    if "--frame" in args:
        ts = [float(a) for a in args[args.index("--frame") + 1:] if not a.startswith("--")]
        K.folha([quadro(t, modo) for t in ts], os.path.join(D.OUT, "frames_fechado.jpg"))
        print("DUR", DUR)
        return
    for m in ("reels", "stories"):
        com, sem = audio(f"fechado_{m}")
        K.entrega(f"fechado_{m}", DUR, render_reels if m == "reels" else render_stories, com, sem)
    print("ok", DUR)


if __name__ == "__main__":
    main()
