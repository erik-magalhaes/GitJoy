#!/usr/bin/env python3
"""Reels NARRADOS da tarde de jogos no Becas (3/nov/2026). Ele não gostou dos 3 só com texto e pediu algo para NARRAR;
quer o vídeo pronto ANTES ("primeiro cria o vídeo e depois eu narro"). Os três usam só as cenas de jogo que eles já
gravaram (gravados-reels/brutos/mesa e nov01) e o roteiro dos gravadores em gravador/:

  doc  DOCUMENTÁRIO DE NATUREZA: faixas de cinema, legenda de documentário ("Jogador de tabuleiro · Ludens tabulae"),
       zoom lento nas cenas, cordas e piano calmos.               gravador Documentario → becasdoc_narracao_NN
  gol  NARRADOR DE FUTEBOL: placar de TV "AO VIVO", relógio de jogo, GOOOL com replay em câmera lenta, checagem do VAR,
       torcida e apito.                                            gravador Futebol → becasgol_narracao_NN
  zap  ÁUDIO DE ZAP PRO AMIGO: cenas de jogo com uma bolha de mensagem de voz tocando (onda, tempo), "MARCA O AMIGO
       QUE NUNCA TOPA NADA".                                       gravador Zap → becaszap_narracao_NN

Prévia SEM voz: cada fala tem o tempo estimado pelo nº de letras; quando a narração chegar, os tempos passam a ser os
da fala real (mesmo esquema do narracao.py dos outros vídeos).

    /usr/bin/python3 narrados.py doc --frame 2 8 20 30 40 50     # out/frames_doc.jpg
    /usr/bin/python3 narrados.py doc                              # out/doc_previa.mp4 (720p para o chat)
"""
import math
import os
import random
import sys
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont

import kit as K
import sons as S
from kit import W, H, FPS, E, TB, MAR, PET, LAR, AMA, BR, ROSA, ease

sys.path.insert(0, K.ROOT)
import tarde  # noqa: E402

FONTES = os.path.join(K.REPO, "halloween-reels", "assets", "fonts")
# trechos inteiros dos brutos (nome → início, duração útil)
FULL = {"critter": (0.0, 7.1), "sushi": (0.0, 6.9), "canvas": (0.4, 7.6), "art": (0.0, 6.7), "passaporte": (0.3, 7.5),
        "unlock": (0.3, 7.4), "taketime": (16.0, 26.0), "taketime2": (0.5, 16.0), "sky_dados": (0.5, 18.0),
        "sky_painel": (0.5, 12.0), "sky_caixa": (0.5, 10.4), "sky_trilha": (0.3, 9.6)}

# ---------------------------------------------------------------- roteiros (iguais aos gravadores)
# cada fala: (texto, cenas, efeito) — cenas = [(clipe, segundo de início no trecho)] ou "becas" / "info" / "cta"
DOC = [("Aqui, em seu habitat natural... observamos uma espécie rara: o jogador de tabuleiro.",
        [("critter", 0.0), ("sky_trilha", 1.0)], "especie"),
       ("Repare como ele protege suas cartas. Ninguém se aproxima. Nem a própria família.",
        [("canvas", 1.0), ("sushi", 0.5)], None),
       ("Quando se sente ameaçado... ele bate na mesa. É um sinal de dominância.",
        [("sky_dados", 3.0), ("art", 0.5)], None),
       ("Os mais experientes ensinam os novatos. Em cinco minutos, o novato já está ganhando. "
        "E o experiente... finge que deixou.", [("taketime", 2.0), ("passaporte", 0.8)], None),
       ("Mas essa espécie tem um ritual. De tempos em tempos, ela migra em bando para um lugar muito especial...",
        [("unlock", 0.5), ("sky_painel", 2.0)], None),
       ("O Becas Café. Lá, a Sua Vez leva os jogos... e ensina todo mundo, mesa por mesa.", "becas", None),
       ("O ingresso é trinta reais. E quinze voltam em consumação no café. Um raro caso de equilíbrio na natureza.",
        "info", None),
       ("A data sai em breve. Garanta sua mesa pelo WhatsApp. E comenta aqui: que espécie de jogador é você?",
        "cta", None)]

GOL = [("Boa tarde, torcedor! Começa agora a grande final da tarde de jogos!",
        [("sky_caixa", 3.5), ("sky_trilha", 1.0)], "apito"),
       ("Embaralha... distribui... e os jogadores se encaram. Que tensão no estádio!",
        [("sushi", 0.3), ("passaporte", 1.0)], None),
       ("Lá vem a carta... olha a carta... OLHA A CARTA!", [("canvas", 1.2)], "lento"),
       ("Bateu na mesa! Bateu! É GOOOOOOOL! É GOL DA RODADA!", [("art", 0.6)], "gol"),
       ("E o adversário reclama com o juiz! Não adianta, meu amigo: jogo de tabuleiro não tem VAR!",
        [("unlock", 0.5), ("sky_painel", 2.5)], "var"),
       ("Quer ver esse clássico ao vivo? A tarde de jogos é no Becas Café, com data em breve. "
        "A Sua Vez leva os jogos e ensina todo mundo.", [("critter", 0.2), ("taketime", 6.0)], "faixa"),
       ("Garanta sua mesa pelo WhatsApp! E comenta aqui: na mesa, você é craque ou perna de pau?", "cta", None)]

ZAP = [("Ô! Escuta, rapidinho. Vai ter uma tarde de jogos de tabuleiro num café, e eu quero te levar.",
        [("sky_trilha", 1.0), ("taketime2", 2.0)], None),
       ("Não, não é Banco Imobiliário! Calma! É jogo moderno, rapidinho, e a galera te ensina na mesa.",
        [("sushi", 0.3), ("passaporte", 0.8)], None),
       ("Tem um que você monta quadros com cartas transparentes... outro que é um escape room na mesa... "
        "e um de cozinha que vira uma bagunça. É muito bom!", [("canvas", 1.0), ("unlock", 0.5), ("critter", 0.2)],
        None),
       ("Trinta reais, e quinze já voltam em café e comida lá no Becas. Ou seja: é quase de graça.",
        [("art", 0.5)], "preco"),
       ("Não precisa saber jogar nada. Sério. Confirma aí, que eu já vou reservar a nossa mesa no WhatsApp.",
        [("taketime", 2.0), ("sky_dados", 3.0)], None),
       ("E se você não for... eu vou te marcar em todo vídeo de jogo até você ir.", "cta", "marca")]

ESTILO = {"doc": (DOC, 13.0), "gol": (GOL, 15.0), "zap": (ZAP, 14.5)}  # letras por segundo (estimativa da fala)
LEAD, GAP, FIM = 0.5, 0.55, 2.6

MODO = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in ESTILO else "doc"
FALAS, LPS = ESTILO[MODO]


def tempos():
    """[(início da cena, início da fala, fim da fala, fim da cena)] com a fala estimada pelas letras."""
    out, t = [], 0.0
    for k, (txt, _, _) in enumerate(FALAS):
        d = len(txt) / LPS
        a = t + LEAD
        b = a + d
        fim = b + (FIM if k == len(FALAS) - 1 else GAP)
        out.append((t, a, b, fim))
        t = fim
    return out


T = tempos()
DUR = T[-1][3]


# ---------------------------------------------------------------- comum
def trechos():
    return [(n, t0, d, 1.0) for n, (t0, d) in FULL.items()]


def clipe(nome, t_ini, u, dur_plano, zoom=0.08, lento=1.0):
    """Quadro do clipe com zoom lento (Ken Burns). Se o plano for mais longo que o trecho, desacelera."""
    t0, L = FULL[nome]
    resto = max(0.5, L - t_ini)
    vel = min(1.0, resto / max(dur_plano, 0.1)) * lento
    img = K.quadro_clip(nome, t0, L, 1.0, t_ini + u * vel)
    z = 1 + zoom * (u / max(dur_plano, 0.1))
    if z > 1.001:
        w2, h2 = int(W * z), int(H * z)
        img = img.resize((w2, h2), Image.BILINEAR).crop(((w2 - W) // 2, (h2 - H) // 2, (w2 - W) // 2 + W,
                                                         (h2 - H) // 2 + H))
    return img


def cena_clipes(k, t):
    ini, _, _, fim = T[k]
    cenas = FALAS[k][1]
    n = len(cenas)
    d = (fim - ini) / n
    j = min(n - 1, int((t - ini) / d))
    nome, t_ini = cenas[j]
    lento = 0.45 if FALAS[k][2] == "lento" else 1.0
    return clipe(nome, t_ini, t - ini - j * d, d, lento=lento), j


def pedacos(txt, maxc=38):
    out, cur = [], []
    for w in txt.split():
        cur.append(w)
        if len(" ".join(cur)) >= maxc or w[-1] in ".?!:":
            out.append(" ".join(cur))
            cur = []
    if cur:
        out.append(" ".join(cur))
    return out


def legenda_atual(t):
    for k, (_, a, b, _) in enumerate(T):
        if a <= t < b:
            ps = pedacos(FALAS[k][0], 38 if MODO == "doc" else 30)
            tot = sum(len(p) for p in ps)
            acc = a
            for p in ps:
                dd = (b - a) * len(p) / tot
                if t < acc + dd:
                    return p
                acc += dd
    return None


@lru_cache(None)
def fonte(arq, s):
    return ImageFont.truetype(os.path.join(FONTES, arq), s)


@lru_cache(None)
def leg_img(txt, estilo):
    if estilo == "doc":
        f = E.fig(48, 600)
        cor, contorno = (255, 255, 255), (0, 0, 0)
    else:
        f = E.fig(48, 900)
        cor, contorno = BR, MAR
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    w = int(tmp.textlength(txt, font=f)) + 40
    im = Image.new("RGBA", (w, 90), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if estilo == "doc":
        for dx, dy in ((2, 2), (3, 3)):
            d.text((w / 2 + dx, 45 + dy), txt, font=f, fill=(0, 0, 0, 160), anchor="mm")
        d.text((w / 2, 45), txt, font=f, fill=cor, anchor="mm")
    else:
        d.text((w / 2, 45), txt, font=f, fill=cor, anchor="mm", stroke_width=6, stroke_fill=contorno)
    return im


def legenda(img, t, y, estilo):
    p = legenda_atual(t)
    if p:
        li = leg_img(p, estilo)
        img.alpha_composite(li, ((W - li.width) // 2, int(y - li.height / 2)))


def cena_info(img, u):
    K.poe(img, TB.card_info(920), W / 2, 960, u, 0.3)


def cena_cta(img, u, comenta):
    K.poe(img, K.logo(230), W / 2, 470, u, 0.2)
    K.poe(img, K.card_cta(), W / 2, 900, u, 0.4, -1.5, d=0.35)
    if comenta:
        K.poe(img, comenta, W / 2, 1290, u, 1.2, 1.5)


def fundo_desfocado(t, nome="taketime2", t_ini=6.0):
    img = K.desfoca(clipe(nome, t_ini, t * 0.3, 30, zoom=0), 16)
    img.alpha_composite(Image.new("RGBA", (W, H), (30, 18, 10, 130)))
    return img


# ---------------------------------------------------------------- DOCUMENTÁRIO
FAIXA = 150


@lru_cache(None)
def terco_especie():
    """Legenda de documentário: nome da espécie + nome 'científico'."""
    im = Image.new("RGBA", (760, 170), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.line((0, 20, 0, 150), fill=(255, 255, 255, 230), width=5)
    d.text((28, 58), "JOGADOR DE TABULEIRO", font=fonte("Cinzel.ttf", 50), fill=(255, 255, 255), anchor="lm")
    d.text((30, 118), "Ludens tabulae  ·  espécie rara", font=fonte("Cormorant-Italic.ttf", 46),
           fill=(235, 225, 205), anchor="lm")
    return im


@lru_cache(None)
def terco(txt1, txt2, cor=(255, 255, 255), cor2=(235, 225, 205)):
    im = Image.new("RGBA", (860, 170), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.line((0, 20, 0, 150), fill=cor, width=5)
    d.text((28, 58), txt1, font=fonte("Cinzel.ttf", 48), fill=cor, anchor="lm")
    d.text((30, 118), txt2, font=fonte("Cormorant-Italic.ttf", 44), fill=cor2, anchor="lm")
    return im


def doc_quadro(t):
    k = max(i for i in range(len(T)) if T[i][0] <= t)
    ini, a, b, fim = T[k]
    u = t - ini
    cenas = FALAS[k][1]
    if cenas == "becas":
        img = Image.new("RGBA", (W, H), TB.CREME + (255,))
        tarde.guarda_chuvas(img, u)
        K.poe(img, K.titulo("BECAS CAFÉ", 150, LAR), W / 2, 820, u, 0.3, -2)
        K.poe(img, K.etiqueta("TARDE DE JOGOS COM A SUA VEZ", 42, PET, BR), W / 2, 1010, u, 0.8, 1.5)
        K.poe(img, terco("HABITAT TEMPORÁRIO", "uma tarde de jogos, com café", MAR, PET), 120 + 430, 1300, u, 1.4, 0)
    elif cenas == "info":
        img = fundo_desfocado(u)
        cena_info(img, u)
    elif cenas == "cta":
        img = fundo_desfocado(u + 5)
        cena_cta(img, u, K.etiqueta("QUE ESPÉCIE É VOCÊ? COMENTA!", 44, AMA, MAR))
    else:
        img, _ = cena_clipes(k, t)
        # leve "filme de natureza": um pouco mais quente e menos saturado
        img = Image.blend(img.convert("RGB"), Image.new("RGB", (W, H), (60, 40, 20)), 0.06).convert("RGBA")
        if FALAS[k][2] == "especie" and u > 1.2:
            a_ = min(1.0, (u - 1.2) / 0.5)
            te = terco_especie().copy()
            te.putalpha(te.getchannel("A").point(lambda v: int(v * a_)))
            K.escurece(img, 1080, 1420, int(150 * a_))
            img.alpha_composite(te, (70, 1180))
    d = ImageDraw.Draw(img)  # faixas de cinema
    d.rectangle((0, 0, W, FAIXA), fill=(0, 0, 0))
    d.rectangle((0, H - FAIXA, W, H), fill=(0, 0, 0))
    if cenas != "cta":
        img.alpha_composite(K.logo(130), (W - 165, FAIXA + 25))
    if cenas == "becas":
        legenda(img, t, 1560, "gol")
    else:
        K.escurece(img, 1460, H - FAIXA + 40, 120)
        legenda(img, t, 1560, "doc")
    if k == 0 and u < 0.6:  # abre do preto
        img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - u / 0.6)))))
    return img


# ---------------------------------------------------------------- FUTEBOL
def k_de(t):
    return max(i for i in range(len(T)) if T[i][0] <= t)


def gol_t():
    k = [i for i, f in enumerate(FALAS) if f[2] == "gol"][0]
    return T[k][1] + 1.6  # o grito do GOOOL (ajusta com a fala real)


@lru_cache(None)
def placar_tv(a, b):
    w, h = 520, 92
    im = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 8, w + 8, h + 8), 18, fill=(0, 0, 0, 120))
    d.rounded_rectangle((0, 0, w, h), 18, fill=(250, 248, 240), outline=MAR, width=5)
    d.rectangle((150, 5, 370, h - 5), fill=MAR)
    d.text((80, h / 2), "MESA A", font=E.lilita(34), fill=PET, anchor="mm")
    d.text((440, h / 2), "MESA B", font=E.lilita(34), fill=LAR, anchor="mm")
    d.text((260, h / 2), f"{a}  x  {b}", font=E.lilita(56), fill=AMA, anchor="mm")
    return im


def gol_quadro(t):
    k = k_de(t)
    ini, a, b, fim = T[k]
    u = t - ini
    cenas, ef = FALAS[k][1], FALAS[k][2]
    tg = gol_t()
    if cenas == "cta":
        img = fundo_desfocado(u + 3, "critter", 2.0)
        cena_cta(img, u, K.etiqueta("CRAQUE OU PERNA DE PAU? COMENTA!", 42, AMA, MAR))
        legenda(img, t, 1500, "gol")
        return img
    if ef == "gol" and t > tg + 1.2:  # REPLAY em câmera lenta
        img = clipe("art", 0.6, (t - tg - 1.2) * 0.35, 3, zoom=0.15)
        K.poe(img, K.etiqueta("REPLAY", 46, (220, 40, 40), BR), 200, 400, t, tg + 1.25, -3)
    else:
        img, _ = cena_clipes(k, t)
    # grafismo de TV
    gols = 1 if t >= tg else 0
    img.alpha_composite(placar_tv(gols, 0), (40, 150))
    pis = int(t * 2) % 2 == 0
    E.cola(img, E.pilula("AO VIVO", 30, (220, 40, 40) if pis else (180, 30, 30), BR, fonte_titulo=True), 670, 196)
    seg = 23 * 60 + int(t * 7)  # relógio de jogo correndo
    E.cola(img, E.pilula(f"1ºT {seg // 60:02d}:{seg % 60:02d}", 28, MAR, BR), 670, 260)
    K.marca(img)
    if ef == "gol" and tg <= t < tg + 1.2:
        q = t - tg
        img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(200 * max(0, 1 - q / 0.25)))))
        dx = 14 * math.sin(q * 60) * max(0, 1 - q)
        rnd = random.Random(int(q * 30))
        dd = ImageDraw.Draw(img)
        for _ in range(60):
            x, y = rnd.uniform(0, W), rnd.uniform(300, 1500)
            dd.rectangle((x, y, x + 16, y + 9), fill=(LAR, PET, AMA, ROSA, BR)[rnd.randrange(5)])
        E.cola(img, K.titulo("GOOOOOL!", 190, AMA), W / 2 + dx, 860, -4, 0.6 + 0.4 * min(1, q / 0.15))
    if ef == "var":
        q = u
        if 1.0 < q and t <= b - 1.4:
            caixa = E.bloco(560, 170, (20, 20, 20), raio=20, ow=6, sombra=10).copy()
            dd = ImageDraw.Draw(caixa)
            dd.text((280, 60), "VAR", font=E.lilita(70), fill=BR, anchor="mm")
            dd.text((280, 128), "checando o lance" + "." * (1 + int(q * 3) % 3), font=E.fig(36, 700), fill=AMA,
                    anchor="mm")
            E.cola(img, caixa, W / 2, 760, 0)
        if t > b - 1.4:
            K.poe(img, K.titulo("SEM VAR!", 160, (235, 70, 60)), W / 2, 860, t, b - 1.4, -8)
    if ef == "faixa":
        K.poe(img, K.card_cta(820), W / 2, 1080, u, max(0.5, (a - ini) + 2.2), 0, d=0.35)
    legenda(img, t, 1500, "gol")
    return img


# ---------------------------------------------------------------- ZAP
@lru_cache(None)
def onda(n=46, seed=5):
    rnd = random.Random(seed)
    return [0.25 + 0.75 * abs(math.sin(i * 0.7)) * rnd.uniform(0.4, 1) for i in range(n)]


def bolha_audio(prog, tempo_txt, tocando):
    w, h = 900, 190
    im = E.bloco(w, h, BR, raio=48, ow=6, sombra=10).copy()
    d = ImageDraw.Draw(im)
    lg = K.logo(110)
    im.alpha_composite(lg, (24, int(h / 2 - lg.height / 2) - 4))
    # botão
    cx, cy = 200, h / 2 - 4
    d.ellipse((cx - 38, cy - 38, cx + 38, cy + 38), fill=PET)
    if tocando:
        d.rectangle((cx - 14, cy - 18, cx - 4, cy + 18), fill=BR)
        d.rectangle((cx + 4, cy - 18, cx + 14, cy + 18), fill=BR)
    else:
        d.polygon([(cx - 10, cy - 20), (cx - 10, cy + 20), (cx + 20, cy)], fill=BR)
    xs, xe = 270, w - 120
    ns = onda()
    for i, v in enumerate(ns):
        x = xs + (xe - xs) * i / (len(ns) - 1)
        hh = 60 * v
        cor = PET if i / len(ns) <= prog else (190, 200, 205)
        d.rounded_rectangle((x - 4, cy - hh / 2, x + 4, cy + hh / 2), 4, fill=cor)
    px = xs + (xe - xs) * prog
    d.ellipse((px - 14, cy - 14, px + 14, cy + 14), fill=LAR, outline=MAR, width=3)
    d.text((w - 64, cy - 22), tempo_txt, font=E.fig(30, 800), fill=MAR, anchor="mm")
    d.text((w - 64, cy + 22), "1,5x" if tocando else "", font=E.fig(24, 800), fill=(150, 150, 150), anchor="mm")
    return im


def zap_quadro(t):
    k = k_de(t)
    ini, a, b, fim = T[k]
    u = t - ini
    cenas, ef = FALAS[k][1], FALAS[k][2]
    if cenas == "cta":
        img = fundo_desfocado(u + 2, "sky_dados", 4.0)
        K.poe(img, K.logo(200), W / 2, 400, u, 0.2)
        K.poe(img, K.card_cta(), W / 2, 790, u, 0.4, -1.5, d=0.35)
        K.poe(img, K.titulo("MARCA O AMIGO QUE\nNUNCA TOPA NADA!", 80, AMA), W / 2, 1200, u, 1.0, -2)
    else:
        img, _ = cena_clipes(k, t)
        if ef == "preco":
            K.poe(img, TB.card_info(900), W / 2, 820, u, 0.6, -1.5)
        K.marca(img)
    # topo: "conversa"
    if cenas != "cta":
        K.escurece(img, 0, 330, 170)
        cab = E.pilula("Erik  ·  gravando áudio...", 34, BR, MAR)
        img.alpha_composite(cab, (40, 70))
    # bolha do áudio (o tempo todo)
    fala_tot = T[-1][2] - T[0][1]
    prog = min(1.0, max(0.0, (t - T[0][1]) / fala_tot))
    seg = int(max(0.0, t - T[0][1]))
    tocando = T[0][1] <= t < T[-1][2]
    K.escurece(img, 1300, 1700, 150)
    E.cola(img, bolha_audio(prog, f"{seg // 60}:{seg % 60:02d}", tocando), W / 2 + 10, 1610 - 40, 0)
    legenda(img, t, 1390, "zap")
    return img


QUADRO = {"doc": doc_quadro, "gol": gol_quadro, "zap": zap_quadro}


def render(fi):
    return QUADRO[MODO](fi / FPS).convert("RGB").tobytes()


def audio(path):
    ev = []
    if MODO == "doc":
        mus = S.musica_doc(DUR)
        ev += [(T[5][0], S.louca(2000 + 150 * j), 0.2) for j in range(6)]
        S.grava(path, DUR, ev, mus, musica_ganho=0.45)
    elif MODO == "gol":
        tg = gol_t()
        mus = S.torcida(DUR, picos=[tg])
        ev += [(T[0][1] - 0.3, S.apito(), 0.8), (tg, S.estouro(), 0.7), (DUR - 2.0, S.apito(1.4), 0.6)]
        ev += [(T[k][0], S.sopro(0.4), 0.5) for k in range(1, len(T))]
        S.grava(path, DUR, ev, mus, musica_ganho=0.35)
    else:
        mus = S.musica_cafe(DUR)
        ev += [(0.1, S.plim(), 0.8), (T[-1][0] + 0.2, S.plim(), 0.6)]
        S.grava(path, DUR, ev, mus, musica_ganho=0.3)


def main():
    os.makedirs(K.OUT, exist_ok=True)
    K.prepara(trechos())
    print(MODO, "duração", round(DUR, 1), "s")
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:]]
        K.folha([QUADRO[MODO](x).convert("RGB") for x in ts], os.path.join(K.OUT, f"frames_{MODO}.jpg"))
        return
    wav = os.path.join(K.OUT, f"{MODO}_previa.wav")
    audio(wav)
    full = os.path.join(K.OUT, f"{MODO}_previa_1080.mp4")
    K.encode(full, render, list(range(int(round(DUR * FPS)))), wav)
    from motor import previa_720p
    previa_720p(full, os.path.join(K.OUT, f"{MODO}_previa.mp4"), kbps=4000)


if __name__ == "__main__":
    main()
