#!/usr/bin/env python3
"""Reels "Os 7 tipos de jogador que todo grupo tem": cada tipo é uma CARTA COLECIONÁVEL (estilo figurinha rara)
que sai de um pacotinho, vira e brilha (holográfico), com status, habilidade especial e o jogo do acervo "dele".
Narração do dono (9 falas); prévia sem voz com as legendas do roteiro.

    python3 tipos.py --frame 1 8 12      # quadros de teste em out/frames.jpg
    python3 tipos.py --only preview      # só a versão com legenda
    python3 tipos.py                     # com e sem legenda
"""
import argparse
import math
import os
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "..", "comum"))
from motor import (W, H, FPS, WHITE, seg, ease, lerp, pop, quica, font, emoji, caixa, logo_card, cola, sombra,  # noqa
                   letreiro, pilula, default_subs, legenda, Linha, encode, previa_720p, folha)
import som  # noqa: E402

OUT = os.path.join(ROOT, "out")
INK = (24, 20, 40)
CREME = (255, 248, 232)
AMARELO = (255, 220, 90)

# raridade → cor da moldura (degradê)
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

ROTEIRO = [
    "Todo grupo de jogo tem esses sete tipos de jogador. Marca o amigo que é cada um!",
    "O Professor: lê o manual inteiro em voz alta, e cinco minutos de regra viram uma hora de aula.",
    "O Analista: pensa dez minutos em cada jogada. Até a ampulheta fica impaciente.",
    "O Mau Perdedor: se ele perdeu, o jogo tá roubado. E já pede revanche.",
    "O Traíra: jura aliança com você... e te apunhala na rodada seguinte.",
    "O Só Mais Uma: começou às oito da noite, e às três da manhã ainda tá pedindo só mais uma.",
    "O Sortudo: não entendeu nenhuma regra e mesmo assim ganhou de todo mundo.",
    "E o É Minha Vez?: tava no celular, perdeu a vez e pergunta de quem é a vez. De novo.",
    "E você, qual desses é? Comenta aqui e marca o amigo! E pra juntar a galera, aluga na Sua Vez: o link tá na bio.",
]
SCENES = [(0.0, 6.5)] + [(6.5 + 7 * k, 13.5 + 7 * k) for k in range(7)] + [(55.5, 66.5)]
CTA = 8
COMENTA = 5.0  # dentro da última cena: até aqui é o "comenta", depois a tela da Sua Vez
TL = Linha(os.path.join(ROOT, "narracao", "timeline.json"))
DUR = TL.tl["duracao"] if TL.tl else SCENES[-1][1]
SUBS = [tuple(x) for x in TL.tl["legendas"]] if TL.tl else default_subs(SCENES, ROTEIRO)
CW, CH = 800, 1140  # carta


def scene_of(t):
    for i, (a, b) in enumerate(SCENES):
        if t < b:
            return i
    return len(SCENES) - 1


# ---------------------------------------------------------------- carta
def degrade(w, h, c1, c2):
    tt = np.linspace(0, 1, h)[:, None, None]
    a = np.array(c1)[None, None] * (1 - tt) + np.array(c2)[None, None] * tt
    return Image.fromarray(np.broadcast_to(a, (h, w, 3)).astype(np.uint8), "RGB")


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


@lru_cache(None)
def mascara_carta():
    m = Image.new("L", (CW, CH), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, CW - 1, CH - 1), radius=46, fill=255)
    return m


@lru_cache(None)
def carta(k, barras=(10, 10, 10), mostra_jogo=True):
    """Frente da carta do tipo k. barras = quantos quadradinhos de cada status já acenderam."""
    tp = TIPOS[k]
    c1, c2 = RAR[tp["rar"]]
    out = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    out.paste(degrade(CW, CH, c1, c2).convert("RGBA"), (0, 0), mascara_carta())
    d = ImageDraw.Draw(out)
    pad = 26
    d.rounded_rectangle((pad, pad, CW - pad, CH - pad), radius=30, fill=CREME)
    d.rounded_rectangle((pad + 14, pad + 14, CW - pad - 14, pad + 124), radius=24, fill=INK)
    fn = font("Bungee-Regular.ttf", 62)
    while d.textlength(tp["nome"], font=fn) > CW - 2 * pad - 80:
        fn = font("Bungee-Regular.ttf", fn.size - 2)
    d.text((CW / 2, pad + 70), tp["nome"], font=fn, fill=WHITE, anchor="mm")
    # janela da ilustração: degradê da raridade + raios + emoji gigante
    jx0, jy0, jx1, jy1 = pad + 14, pad + 140, CW - pad - 14, pad + 500
    jw, jh = jx1 - jx0, jy1 - jy0
    jan = degrade(jw, jh, tuple(min(255, v + 40) for v in c1), c2).convert("RGBA")
    ov = Image.new("RGBA", (jw, jh), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ov)
    for i in range(18):
        a0 = i * 2 * math.pi / 18
        rd.polygon([(jw / 2, jh / 2), (jw / 2 + 900 * math.cos(a0), jh / 2 + 900 * math.sin(a0)),
                    (jw / 2 + 900 * math.cos(a0 + 0.17), jh / 2 + 900 * math.sin(a0 + 0.17))], fill=(255, 255, 255, 40))
    jan.alpha_composite(ov)
    em = emoji(tp["emoji"], 290)
    sh = Image.new("RGBA", em.size, (0, 0, 0, 0))
    sh.putalpha(em.getchannel("A").point(lambda v: int(v * 0.35)))
    jan.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), (jw // 2 - em.width // 2 + 10, jh // 2 - em.height // 2 + 16))
    jan.alpha_composite(em, (jw // 2 - em.width // 2, jh // 2 - em.height // 2))
    mj = Image.new("L", (jw, jh), 0)
    ImageDraw.Draw(mj).rounded_rectangle((0, 0, jw - 1, jh - 1), radius=22, fill=255)
    out.paste(jan, (jx0, jy0), mj)
    d.rounded_rectangle((jx0, jy0, jx1, jy1), radius=22, outline=INK, width=5)
    fr = font("Bungee-Regular.ttf", 30)
    tw = d.textlength(tp["rar"], font=fr)
    d.rounded_rectangle((CW / 2 - tw / 2 - 26, jy1 - 26, CW / 2 + tw / 2 + 26, jy1 + 26), radius=26, fill=c2,
                        outline=WHITE, width=4)
    d.text((CW / 2, jy1 + 1), tp["rar"], font=fr, fill=WHITE, anchor="mm")
    d.text((CW / 2, jy1 + 72), tp["frase"], font=font("Poppins-ExtraBold.ttf", 38), fill=INK, anchor="mm")
    fs = font("Poppins-SemiBold.ttf", 29)
    y = jy1 + 122
    for (nome, v), acesas in zip(tp["stats"], barras):
        d.text((pad + 40, y + 20), nome.upper(), font=fs, fill=INK, anchor="lm")
        bx0 = CW - pad - 40 - 10 * 25
        for i in range(10):
            on = i < min(v, acesas)
            d.rounded_rectangle((bx0 + i * 25, y + 6, bx0 + i * 25 + 19, y + 34), radius=5,
                                fill=c2 if on else (225, 218, 205))
        y += 52
    y += 8
    d.rounded_rectangle((pad + 30, y, CW - pad - 30, y + 140), radius=18, fill=(255, 236, 200), outline=c2, width=4)
    d.text((pad + 52, y + 26), "HABILIDADE ESPECIAL", font=font("Bungee-Regular.ttf", 24), fill=c2, anchor="lm")
    fh = font("Poppins-ExtraBold.ttf", 31)
    for i, l in enumerate(texto_quebrado(d, tp["hab"], fh, CW - 2 * pad - 110)[:2]):
        d.text((pad + 52, y + 68 + i * 38), l, font=fh, fill=INK, anchor="lm")
    y = CH - pad - 150
    d.line((pad + 30, y - 6, CW - pad - 30, y - 6), fill=(215, 205, 190), width=3)
    d.text((pad + 44, y + 40), "JOGO FAVORITO:", font=font("Bungee-Regular.ttf", 26), fill=(150, 130, 110), anchor="lm")
    if mostra_jogo:
        cx = caixa(tp["jogo"], 128)
        out.alpha_composite(cx, (CW - pad - 50 - cx.width, y + 6))
        d.text((pad + 44, y + 92), tp["jogo_nome"], font=font("Poppins-Black.ttf", 46), fill=INK, anchor="lm")
    else:
        d.text((pad + 44, y + 92), "???", font=font("Poppins-Black.ttf", 46), fill=(190, 180, 165), anchor="lm")
    return out


@lru_cache(None)
def verso():
    """Verso da carta: tinta escura, padrão de losangos e o logo da Sua Vez."""
    out = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    out.paste(degrade(CW, CH, (60, 40, 120), (20, 14, 40)).convert("RGBA"), (0, 0), mascara_carta())
    ov = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for yy in range(-60, CH + 60, 90):
        for xx in range(-60, CW + 60, 90):
            o = 45 if (yy // 90) % 2 else 0
            d.polygon([(xx + o, yy - 30), (xx + o + 30, yy), (xx + o, yy + 30), (xx + o - 30, yy)], fill=(255, 255, 255, 18))
    a = np.minimum(np.asarray(ov.getchannel("A")), np.asarray(mascara_carta()))
    ov.putalpha(Image.fromarray(a.astype(np.uint8)))
    out.alpha_composite(ov)
    d = ImageDraw.Draw(out)
    d.rounded_rectangle((26, 26, CW - 26, CH - 26), radius=30, outline=AMARELO, width=8)
    lg = logo_card(420)
    out.alpha_composite(lg, (CW // 2 - lg.width // 2, CH // 2 - lg.height // 2 - 40))
    d.text((CW / 2, CH / 2 + 170), "TIPOS DE JOGADOR", font=font("Bungee-Regular.ttf", 50), fill=AMARELO, anchor="mm")
    d.text((CW / 2, CH / 2 + 235), "edição colecionável", font=font("Poppins-ExtraBold.ttf", 36), fill=WHITE, anchor="mm")
    return out


@lru_cache(None)
def faixa_holo():
    """Faixa arco-íris diagonal (desfocada) para o brilho holográfico."""
    im = Image.new("RGBA", (CW + 1600, CH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = 800
    for i, c in enumerate([(255, 120, 200), (255, 230, 120), (120, 255, 200), (120, 180, 255)]):
        d.polygon([(x + i * 40, 0), (x + i * 40 + 40, 0), (x + i * 40 + 40 - 500, CH), (x + i * 40 - 500, CH)],
                  fill=c + (70,))
    return im.filter(ImageFilter.GaussianBlur(18))


def com_holo(c, u):
    """Carta c com o brilho holográfico na posição u (0..1)."""
    if u <= 0 or u >= 1:
        return c
    off = int(lerp(1400, 0, u))
    h = faixa_holo().crop((off, 0, off + CW, CH))
    a = np.minimum(np.asarray(h.getchannel("A")), np.asarray(mascara_carta()))
    h.putalpha(Image.fromarray(a.astype(np.uint8)))
    c = c.copy()
    c.alpha_composite(h)
    return c


def vira(frente, tras, u):
    """Carta virando (giro no eixo vertical): u 0 → verso, 1 → frente."""
    ang = u * math.pi
    lado = tras if ang < math.pi / 2 else frente
    esc = abs(math.cos(ang))
    w = max(2, int(CW * esc))
    return lado.resize((w, CH), Image.BICUBIC)


@lru_cache(None)
def pacote(cor1, cor2, rasgado=False):
    """Pacotinho de figurinhas metalizado (bordas serrilhadas)."""
    pw, ph = 900, 560
    im = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    corpo = degrade(pw, ph, cor1, cor2).convert("RGBA")
    m = Image.new("L", (pw, ph), 0)
    md = ImageDraw.Draw(m)
    pts = [(0, 30)]
    for i in range(0, pw + 1, 30):
        pts.append((i, 0 if (i // 30) % 2 else 30))
    pts += [(pw, ph - 30)]
    for i in range(pw, -1, -30):
        pts.append((i, ph if (i // 30) % 2 else ph - 30))
    md.polygon(pts, fill=255)
    if rasgado:  # tira a faixa do topo
        md.rectangle((0, 0, pw, 110), fill=0)
    im.paste(corpo, (0, 0), m)
    ov = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for i in range(-ph, pw, 70):  # reflexo metálico
        d.line((i, ph, i + ph, 0), fill=(255, 255, 255, 30), width=26)
    a = np.minimum(np.asarray(ov.getchannel("A")), np.asarray(m))
    ov.putalpha(Image.fromarray(a.astype(np.uint8)))
    im.alpha_composite(ov)
    d = ImageDraw.Draw(im)
    d.text((pw / 2, 250), "PACOTE SURPRESA", font=font("Bungee-Regular.ttf", 64), fill=WHITE, anchor="mm",
           stroke_width=6, stroke_fill=INK)
    d.text((pw / 2, 345), "1 TIPO DE JOGADOR", font=font("Poppins-Black.ttf", 44), fill=AMARELO, anchor="mm",
           stroke_width=4, stroke_fill=INK)
    return im


# ---------------------------------------------------------------- fundo
@lru_cache(None)
def fundo_base(cor):
    return degrade(W, H, tuple(int(v * 0.55) for v in cor), (10, 8, 24)).convert("RGBA")


def fundo(t, cor=(70, 30, 140)):
    """Degradê noturno na cor da raridade com bolinhas de luz desfocadas (bokeh) subindo devagar."""
    img = fundo_base(cor).copy()
    ov = Image.new("RGBA", (W // 4, H // 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    rng = np.random.default_rng(7)
    for _ in range(26):
        x, y0, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(20, 90)
        y = (y0 - t * rng.uniform(15, 40)) % (H + 200) - 100
        d.ellipse(((x - r) / 4, (y - r) / 4, (x + r) / 4, (y + r) / 4), fill=(255, 220, 255, int(rng.uniform(14, 40))))
    img.alpha_composite(ov.filter(ImageFilter.GaussianBlur(3.5)).resize((W, H), Image.BILINEAR))
    return img


# ---------------------------------------------------------------- cenas
def cena_gancho(img, t):
    a, b = SCENES[0]
    cola(img, letreiro("TODO GRUPO TEM", 84, WHITE, INK, 10), 540, 300, 0, pop(t, -0.3))
    cola(img, letreiro("ESSES 7 TIPOS", 118, AMARELO, INK, 12), 540, 430, -2, pop(t, -0.15))
    # leque das 7 cartas
    for i in range(7):
        t0 = 0.3 + i * 0.12
        if t >= t0:
            ang = (i - 3) * 9
            x = 540 + (i - 3) * 105
            y = 1130 + abs(i - 3) ** 1.6 * 22
            flut = 8 * math.sin(t * 2 + i)
            c = carta(i).resize((380, 542), Image.LANCZOS)
            cola(img, sombra(c, 16, (0, 18), 0.45), x, lerp(2300, y, quica(t, t0, 0.55)) + flut, -ang)
    if t >= 1.5:
        cola(img, letreiro("marca quem é quem", 56, WHITE, INK, 8, "Poppins-Black.ttf"), 500, 580, 0, pop(t, 1.5))
        cola(img, emoji("👇", 72), 850, 585 + 8 * math.sin(t * 8))
    sai = ease(seg(t, b - 0.4, b))
    if sai > 0:
        img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(150 * sai))))


def cena_tipo(img, t, k):
    a, b = SCENES[k + 1]
    u = t - a
    tp = TIPOS[k]
    cola(img, pilula(f"TIPO {k + 1}/7", 40, (0, 0, 0), WHITE, WHITE), 200, 110, 0, pop(t, a + 0.05))
    cy = 880
    # 1) pacotinho sobe, rasga e a carta sai virada para baixo
    if u < 1.2:
        c1, c2 = RAR[tp["rar"]]
        sobe = quica(t, a, 0.45)
        rasga = u >= 0.55
        treme = 6 * math.sin(u * 50) * seg(u, 0.35, 0.55) * (1 - seg(u, 0.55, 0.6))
        some = ease(seg(u, 0.9, 1.2))
        if rasga:  # a carta já sai de dentro
            cs = ease(seg(u, 0.55, 1.1))
            cola(img, sombra(verso().resize((600, 855), Image.LANCZOS), 18, (0, 20), 0.4), 540, lerp(1550, cy, cs),
                 0, lerp(0.75, 1.0, cs))
        p = pacote(c1, c2, rasga)
        cola(img, p, 540 + treme, lerp(2300, 1500, sobe) + some * 900, 0, 1.0, 1 - some)
        if rasga and u < 0.9:  # a tira do topo voando
            v = seg(u, 0.55, 0.9)
            tira = pacote(c1, c2).crop((0, 0, 900, 110))
            cola(img, tira, 540 + 400 * v, 1500 - 225 - 600 * v, 25 * v, 1.0, 1 - v)
        return
    # 2) vira, brilha, os status enchem, o jogo favorito aparece
    sai = ease(seg(t, b - 0.45, b))
    gira = ease(seg(u, 1.2, 1.6))
    barras = tuple(int(10 * seg(u, 2.0 + j * 0.45, 2.4 + j * 0.45)) for j in range(3))
    frente = carta(k, barras, u >= 4.4)
    frente = com_holo(frente, seg(u, 1.6, 2.4))
    if gira < 1:
        c = vira(frente, verso(), gira)
    else:
        c = frente
    flut = 6 * math.sin(u * 2.2)
    rot = 1.5 * math.sin(u * 1.3)
    cola(img, sombra(c.resize((max(2, int(c.width * 0.95)), int(CH * 0.95)), Image.LANCZOS), 22, (0, 26), 0.5),
         lerp(540, -700, sai), cy + flut, rot + lerp(0, 18, sai))
    if 1.6 <= u < 2.6:  # estrelinhas do brilho
        for j in range(8):
            ang = j * math.pi / 4 + u
            rr = 380 + 140 * seg(u, 1.6, 2.6)
            cola(img, emoji("✨", 70), 540 + rr * math.cos(ang), cy + rr * 1.35 * math.sin(ang), 0, 1.0,
                 1 - seg(u, 2.2, 2.6))
    if 4.4 <= u < 5.2:  # carimbo no jogo favorito
        cola(img, pilula("TEM NA SUA VEZ!", 34, (22, 163, 74)), lerp(540, -700, sai) + 170, cy + 520, -6, pop(t, a + 4.4))
    elif u >= 5.2:
        cola(img, pilula("TEM NA SUA VEZ!", 34, (22, 163, 74)), lerp(540, -700, sai) + 170, cy + 520, -6)


def cena_final(img, t):
    a, b = SCENES[CTA]
    u = t - a
    if u < COMENTA:
        cola(img, letreiro("E VOCÊ,\nQUAL DESSES É?", 100, AMARELO, INK, 12), 540, 360, -2, pop(t, a + 0.05))
        for i in range(7):
            t0 = a + 0.5 + i * 0.1
            if t >= t0:
                col, lin = (i % 4, i // 4) if i < 4 else ((i - 4) % 3, 1)
                x = 540 + (col - 1.5) * 235 if i < 4 else 540 + (col - 1) * 235
                y = 800 + lin * 360
                c = carta(i).resize((210, 300), Image.LANCZOS)
                cola(img, sombra(c, 10, (0, 10), 0.4), x, y + 6 * math.sin(t * 3 + i), ((i * 37) % 9) - 4, pop(t, t0))
        if u >= 1.6:
            b_ = 1 + 0.05 * abs(math.sin(t * 5))
            cola(img, letreiro("COMENTA E MARCA\nO AMIGO!", 76, WHITE, INK, 10), 500, 1440, -2, pop(t, a + 1.6) * b_)
            cola(img, emoji("👇", 100), 940, 1460 + 12 * math.sin(t * 8))
        return
    a2 = a + COMENTA
    cola(img, logo_card(430), 540, 250, 0, pop(t, a2 + 0.05))
    jogos = ["root", "king_of_tokyo", "camel_up_second_edition", "dixit", "hive"]
    for i, n in enumerate(jogos):
        t0 = a2 + 0.3 + i * 0.1
        if t >= t0:
            cola(img, sombra(caixa(n, 300), 14, (6, 14), 0.4), 540 + (i - 2) * 160,
                 lerp(-400, 680 + abs(i - 2) * 24, quica(t, t0, 0.5)), (i - 2) * 6)
    itens = [(1.0, letreiro("ALUGUE O JOGO\nDO SEU GRUPO!", 76, AMARELO, INK, 12), 1030),
             (1.4, pilula("5 DIAS DE JOGO · 3 JOGOS = 7 DIAS", 38, (120, 40, 200)), 1225),
             (1.8, pilula("RESERVE ONLINE · RETIRE EM MAUÁ E ABC", 34, WHITE, INK, INK), 1335),
             (2.1, pilula("OU RECEBA EM CASA!", 42, (22, 163, 74)), 1445),
             (2.5, pilula("LINK NA BIO · @SUAVEZ_BG", 50, (230, 120, 10)), 1570)]
    for t0, im, y in itens:
        if t >= a2 + t0:
            b_ = 1 + 0.04 * abs(math.sin(t * 5)) if y == 1570 else 1
            cola(img, im, 540, y, 0, pop(t, a2 + t0) * b_)


def frame_at(t):
    i = scene_of(t)
    cor = RAR[TIPOS[i - 1]["rar"]][1] if 1 <= i <= 7 else (70, 30, 140)
    img = fundo(t, cor)
    if i == 0:
        cena_gancho(img, t)
    elif i <= 7:
        cena_tipo(img, t, i - 1)
    else:
        cena_final(img, t)
    return img


def em_cta(to):
    return to >= SCENES[CTA][0] + COMENTA


def render_frame(args):
    fi, subs = args
    t = fi / FPS
    to = TL.to_orig(t)
    img = frame_at(to)
    if not em_cta(to):
        wm = logo_card(170)
        img.alpha_composite(wm, (W - wm.width - 30, 40))
    if subs:
        legenda(img, SUBS, t)
    return img.convert("RGB").tobytes()


def cues():
    c = [(0.0, "pop", 0.5), (0.15, "pop", 0.4)] + [(0.3 + i * 0.12 + 0.3, "flip", 0.4) for i in range(7)]
    c += [(1.5, "boing", 0.4)]
    for k in range(7):
        a = SCENES[k + 1][0]
        c += [(a, "whoosh", 0.5), (a + 0.4, "rasga", 0.8), (a + 1.2, "flip", 0.7), (a + 1.6, "brilho", 0.6)]
        c += [(a + 2.0 + j * 0.45, "barra", 0.35) for j in range(3)]
        c += [(a + 4.4, "carimbo", 0.6), (a + 4.45, "ding", 0.35), (SCENES[k + 1][1] - 0.45, "whoosh", 0.4)]
    a = SCENES[CTA][0]
    c += [(a, "pop", 0.5)] + [(a + 0.5 + i * 0.1, "flip", 0.3) for i in range(7)] + [(a + 1.6, "boing", 0.5)]
    a2 = a + COMENTA
    c += [(a2, "whoosh", 0.4)] + [(a2 + x, "pop", 0.4) for x in (1.0, 1.4, 1.8, 2.1)] + [(a2 + 2.5, "ding", 0.6)]
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    ap.add_argument("--only", choices=["preview", "limpo"])
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.frame:
        folha([Image.frombytes("RGB", (W, H), render_frame((int(round(x * FPS)), True))) for x in a.frame],
              os.path.join(OUT, "frames.jpg"))
        return
    wav = os.path.join(OUT, "trilha.wav")
    voz = [(os.path.join(ROOT, v["arquivo"]), v["inicio"]) for v in TL.tl["voz"]] if TL.tl else None
    som.build(wav, DUR, cues(), musica="travessa", warp=TL.warp, voz=voz)
    n = int(DUR * FPS)
    if a.only != "limpo":
        encode(os.path.join(OUT, "tipos_preview.mp4"), render_frame, [(j, True) for j in range(n)], wav)
        previa_720p(os.path.join(OUT, "tipos_preview.mp4"), os.path.join(OUT, "tipos_preview_720p.mp4"))
    if a.only != "preview":
        encode(os.path.join(OUT, "tipos_limpo.mp4"), render_frame, [(j, False) for j in range(n)], wav)


if __name__ == "__main__":
    main()
