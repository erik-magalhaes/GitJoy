#!/usr/bin/env python3
"""2ª versão dos carrosséis do feed (1080 x 1080). Ele gostou, mas: (1) os três tinham o MESMO layout e (2) repetiam
jogos (Hitster, Ticket to Ride... já usados em outros posts). Agora cada um tem cara própria e NENHUM jogo se repete entre
eles nem com os posts anteriores (nem com os 10 do vídeo do tarô):

    rolê       → PRINT DE CONVERSA DE WHATSAPP (amigo pergunta, a Sua Vez responde com a caixa)
    clássicos  → ANTES × DEPOIS (papel envelhecido com o clássico em cima, moderno colorido embaixo)
    top 5      → RANKING DE REVISTA (número gigante, faixa diagonal, cor por posição)

    python3 carrosseis2.py      # out/v2_<role|classicos|top5>/01.png ... e todas.jpg
"""
import json
import math
import os
import random
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "comum"))
from motor import WHITE, font, emoji, logo_card, cola, sombra, letreiro, pilula  # noqa: E402

S = 1080
OUT = os.path.join(ROOT, "out")
AS = os.path.join(ROOT, "assets")
NAVY = (22, 33, 62)
ORANGE = (249, 115, 22)
VERDE = (22, 163, 74)
SITE = {k.strip(): v for k, v in json.load(open(os.path.join(REPO, "comum", "dados", "acervo_site.json"), encoding="utf-8")).items()}
NOME_SITE = {"patchwork": "Patchwork", "monkey_palace": "Monkey Palace", "say_my_name": "Say my Name",
             "survive": "Survive The Island", "santa_kaos": "Santa Kaos", "dinosaur_world": "Dinosaur World",
             "flip7_vinganca": "Flip 7: A Vingança", "micromacro": "MicroMacro: Crime City - full house",
             "mind_mgmt": "Mind MGMT: The Psychic Espionage “Game.”", "wonderland": "Wonderland's War",
             "jungo": "Jungo", "bandido": "Bandido", "next_station": "Next Station: London", "dungeon_fighter": "Dungeon Fighter",
             "take_time": "Take Time"}


@lru_cache(None)
def caixa(n, h, larg=None):
    im = Image.open(os.path.join(AS, n + ".png")).convert("RGBA")
    im = im.crop(im.getbbox())
    s = h / im.height
    if larg and im.width * s > larg:
        s = larg / im.width
    return im.resize((max(2, int(im.width * s)), max(2, int(im.height * s))), Image.LANCZOS)


def info(n):
    d = SITE[NOME_SITE[n]]
    a, b = d["jogadores"].split("–")
    jog = f"{a} JOGADOR" if a == b == "1" else (f"{a} JOGADORES" if a == b else f"{a} A {b} JOGADORES")
    if n == "flip7_vinganca":
        jog = "3+ JOGADORES"
    return f"{jog} · {d['tempo'].replace('min', ' MIN')}"


def e_emoji(tok):
    import unicodedata
    return any(unicodedata.category(c) == "So" or ord(c) > 0x1F000 for c in tok)


def larg_tok(tok, f):
    return f.size * 1.1 if e_emoji(tok) else f.getlength(tok)


def quebra_e(txt, f, larg):
    linhas, cur, cw = [], [], 0
    esp = f.getlength(" ")
    for w in txt.split():
        lw = larg_tok(w, f)
        if cur and cw + esp + lw > larg:
            linhas.append(cur)
            cur, cw = [], 0
        cw += (esp if cur else 0) + lw
        cur.append(w)
    return linhas + [cur]


def escreve(img, x, y, toks, f, cor):
    """Escreve uma linha (lista de palavras) com emoji colorido no lugar dos símbolos (a fonte não tem emoji)."""
    d = ImageDraw.Draw(img)
    esp = f.getlength(" ")
    for w in toks:
        if e_emoji(w):
            e = emoji(w, int(f.size * 1.05))
            img.alpha_composite(e, (int(x), int(y - e.height / 2)))
            x += f.size * 1.1 + esp
        else:
            d.text((x, y), w, font=f, fill=cor, anchor="lm")
            x += f.getlength(w) + esp


def quebra(txt, f, larg):
    linhas, cur = [], ""
    for w in txt.split():
        t = (cur + " " + w).strip()
        if f.getlength(t) > larg and cur:
            linhas.append(cur)
            cur = w
        else:
            cur = t
    return linhas + [cur]


def num_slide(img, n, tot, cor=NAVY, fg=WHITE):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((34, 34, 150, 92), radius=29, fill=cor)
    d.text((92, 63), f"{n}/{tot}", font=font("Bungee-Regular.ttf", 30), fill=fg, anchor="mm")


def arrasta(img, cor=NAVY, y=None):
    k = pilula("ARRASTA     ", 30, cor)
    dk = ImageDraw.Draw(k)
    cy, x1 = k.height / 2 + 1, k.width - 52
    dk.polygon([(x1, cy - 11), (x1 + 20, cy), (x1, cy + 11)], fill=WHITE)
    dk.line((x1 - 24, cy, x1 + 3, cy), fill=WHITE, width=5)
    cola(img, k, S - k.width / 2 - 30, y or S - 50)


# ================================================================ 1. WHATSAPP
ZAP_BG = (236, 229, 221)
ZAP_TOPO = (7, 94, 84)
ZAP_EU = (217, 253, 211)
ROLE = [("primeiro encontro 💕", "patchwork", "Patchwork! Lindo, só pra dois e dá pra jogar conversando 😍"),
        ("almoço de família 👵👶", "monkey_palace", "Monkey Palace! Todo mundo monta o palácio junto, com peças LEGO 🐒"),
        ("galera grande, uns 10 🎉", "say_my_name", "Say my Name! Jogo de festa de 4 a 12 pessoas, risada garantida 😂"),
        ("quero ver treta 😈", "survive", "Survive: The Island! Fuja da ilha… e mande o tubarão pro barco do amigo 🦈"),
        ("ceia de Natal 🎄", "santa_kaos", "Santa Kaos! Caos natalino pra animar a ceia 🎅"),
        ("quero fritar a cuca 🧠", "dinosaur_world", "Dinosaur World! Monte seu parque sem deixar ninguém virar lanche 🦖")]


@lru_cache(None)
def zap_fundo():
    img = Image.new("RGBA", (S, S), ZAP_BG + (255,))
    d = ImageDraw.Draw(img)
    rnd = random.Random(5)
    for _ in range(70):  # rabiscos claros do papel de parede
        x, y, r = rnd.uniform(0, S), rnd.uniform(0, S), rnd.uniform(10, 22)
        tipo = rnd.randint(0, 2)
        c = (222, 214, 204)
        if tipo == 0:
            d.ellipse((x - r, y - r, x + r, y + r), outline=c, width=3)
        elif tipo == 1:
            d.rectangle((x - r, y - r, x + r, y + r), outline=c, width=3)
        else:
            d.polygon([(x, y - r), (x + r, y + r), (x - r, y + r)], outline=c)
    d.rectangle((0, 0, S, 120), fill=ZAP_TOPO)
    d.ellipse((95, 25, 165, 95), fill=(240, 240, 240))
    img.alpha_composite(emoji("🎲", 44), (108, 38))
    d.text((190, 45), "Galera do Rolê", font=font("Poppins-Black.ttf", 36), fill=WHITE, anchor="lm")
    d.text((190, 85), "você, Sua Vez e mais 6", font=font("Poppins-SemiBold.ttf", 24), fill=(200, 230, 225), anchor="lm")
    d.polygon([(40, 60), (62, 40), (62, 80)], fill=WHITE)  # seta voltar
    d.rectangle((0, S - 100, S, S), fill=(240, 240, 240))
    d.rounded_rectangle((30, S - 82, S - 130, S - 22), radius=30, fill=WHITE)
    d.text((70, S - 52), "Mensagem", font=font("Poppins-SemiBold.ttf", 28), fill=(160, 160, 160), anchor="lm")
    d.ellipse((S - 110, S - 90, S - 30, S - 10), fill=ZAP_TOPO)
    return img


def balao(texto, eu, nome=None, hora="19:42", larg=640, img_caixa=None, extra=None):
    f = font("Poppins-SemiBold.ttf", 32)
    linhas = quebra_e(texto, f, larg - 60)
    alt_img = img_caixa.height + 20 if img_caixa else 0
    alt = (46 if nome else 0) + alt_img + len(linhas) * 44 + (40 if extra else 0) + 60
    if img_caixa or len(linhas) > 1 or extra:
        w = larg
    else:
        w = int(sum(larg_tok(t, f) for t in linhas[0]) + f.getlength(" ") * len(linhas[0]) + 150)
    im = Image.new("RGBA", (w + 20, alt + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cor = ZAP_EU if eu else WHITE
    d.rounded_rectangle((10, 0, w + 10, alt), radius=22, fill=cor)
    if eu:
        d.polygon([(w - 10, 0), (w + 22, 0), (w + 6, 24)], fill=cor)
    else:
        d.polygon([(30, 0), (-2, 0), (14, 24)], fill=cor)
    y = 18
    if nome:
        d.text((34, y + 14), nome, font=font("Poppins-Black.ttf", 28), fill=(232, 90, 40), anchor="lm")
        y += 46
    if img_caixa:
        im.alpha_composite(img_caixa, (int(10 + w / 2 - img_caixa.width / 2), y))
        y += alt_img
    for l in linhas:
        escreve(im, 34, y + 20, l, f, (30, 30, 30))
        y += 44
    if extra:
        d.text((34, y + 18), extra, font=font("Bungee-Regular.ttf", 24), fill=ZAP_TOPO, anchor="lm")
    hx = w - 10
    if eu:  # tiques azuis de lida
        for dx in (0, 14):
            d.line((hx - 34 + dx, alt - 24, hx - 27 + dx, alt - 16, hx - 14 + dx, alt - 30), fill=(52, 183, 241), width=3)
        hx -= 50
    d.text((hx, alt - 22), hora, font=font("Poppins-SemiBold.ttf", 22), fill=(120, 140, 130), anchor="rm")
    return sombra(im, 4, (0, 3), 0.15)


def zap_slide(pergunta, n, resposta, quem="Ju"):
    img = zap_fundo().copy()
    b1 = balao(f"rolê de hoje: {pergunta} qual jogo eu levo??", False, quem, "19:41", 600)
    img.alpha_composite(b1, (30, 150))
    cx = sombra(caixa(n, 245, 380), 10, (0, 8), 0.3)
    b2 = balao(resposta, True, None, "19:42", 660, cx, info(n))
    img.alpha_composite(b2, (S - b2.width - 30, 160 + b1.height + 10))
    return img


def zap_capa():
    img = zap_fundo().copy()
    msgs = [(False, "Ju", "galera, qual jogo eu levo pro rolê? 🤔", "19:40"),
            (False, "Léo", "depende do rolê né kkkk", "19:40"),
            (True, None, "tem um jogo certo pra cada rolê 😎", "19:41")]
    y = 160
    for eu, nome, txt, hora in msgs:
        b = balao(txt, eu, nome, hora, 640)
        img.alpha_composite(b, (S - b.width - 30 if eu else 30, y))
        y += b.height + 14
    cola(img, letreiro("O JOGO CERTO\nPRA CADA ROLÊ", 82, WHITE, ZAP_TOPO, 12, sombra_px=6, cor_sombra=(4, 60, 54)), 540, 800, -2)
    return img


def zap_cta():
    img = zap_fundo().copy()
    b = balao("onde eu acho esses jogos?? 😱", False, "Ju", "19:45", 560)
    img.alpha_composite(b, (30, 160))
    lg = logo_card(300)
    txt = ("Aluga na Sua Vez! 5 dias de jogo, e 3 jogos = 7 dias. Reserva online e retira em Mauá e ABC ou "
           "recebe em casa. O link tá na bio: @suavez_bg 🧡")
    b2 = balao(txt, True, None, "19:46", 700, lg)
    img.alpha_composite(b2, (S - b2.width - 30, 175 + b.height))
    cola(img, pilula("QUAL É O SEU ROLÊ? COMENTA!", 34, ORANGE), 540, S - 160, -1)
    return img


# ================================================================ 2. ANTES × DEPOIS
CLASSICOS = [("UNO", "flip7_vinganca", "FLIP 7: A VINGANÇA", "Também é carta e número, mas você decide até onde arriscar."),
             ("DETETIVE", "micromacro", "MICROMACRO: FULL HOUSE", "Ache o culpado numa cidade gigante, toda desenhada."),
             ("BATALHA NAVAL", "mind_mgmt", "MIND MGMT", "Um agente se esconde no mapa e os outros tentam achar onde ele está."),
             ("WAR", "wonderland", "WONDERLAND'S WAR", "Conquista de território… no País das Maravilhas.")]


@lru_cache(None)
def papel_velho():
    rng = np.random.default_rng(3)
    a = rng.random((30, 30)).astype(np.float32)
    m = np.array(Image.fromarray((a * 255).astype(np.uint8)).resize((S, 470), Image.BICUBIC).filter(ImageFilter.GaussianBlur(40)),
                 np.float32) / 255
    base = np.array([226, 205, 165], np.float32)
    img = (base[None, None, :] * (0.88 + 0.16 * m[..., None])).clip(0, 255).astype(np.uint8)
    p = Image.fromarray(img).convert("RGBA")
    d = ImageDraw.Draw(p)
    for k in range(4):
        d.rectangle((20 + k * 4, 20 + k * 4, S - 20 - k * 4, 450 - k * 4), outline=(150, 120, 80, 60))
    return p


def corte_rasgado(img, y):
    d = ImageDraw.Draw(img)
    rnd = random.Random(int(y))
    pts = [(0, y)]
    for x in range(0, S + 30, 30):
        pts.append((x, y + rnd.uniform(-12, 12)))
    pts += [(S, y + 40), (0, y + 40)]
    d.polygon(pts, fill=(250, 248, 240))


def antes_depois(k):
    cl, n, nome, mot = CLASSICOS[k]
    cores = [(255, 90, 60), (37, 99, 235), (147, 51, 234), (13, 148, 136)]
    img = Image.new("RGBA", (S, S), cores[k] + (255,))
    d = ImageDraw.Draw(img)
    for j in range(16):  # raios no "depois"
        a0, a1 = j * math.tau / 16, (j + 0.5) * math.tau / 16
        d.polygon([(780, 800), (780 + 1600 * math.cos(a0), 800 + 1600 * math.sin(a0)),
                   (780 + 1600 * math.cos(a1), 800 + 1600 * math.sin(a1))], fill=tuple(min(255, c + 22) for c in cores[k]))
    img.alpha_composite(papel_velho(), (0, 0))
    d = ImageDraw.Draw(img)
    cola(img, pilula("ANTES", 34, (120, 90, 55), (250, 240, 220), (120, 90, 55)), 160, 120, -4)
    d.text((540, 230), f"CURTE {cl}?", font=font("AlfaSlabOne-Regular.ttf", 84 if len(cl) < 9 else 68), fill=(90, 62, 35),
           anchor="mm")
    d.text((540, 330), "o clássico que todo mundo já jogou", font=font("Poppins-SemiBold.ttf", 34), fill=(120, 90, 55),
           anchor="mm")
    corte_rasgado(img, 455)
    cola(img, pilula("DEPOIS", 34, NAVY, WHITE, WHITE), 160, 545, 3)
    cola(img, sombra(caixa(n, 400, 380), 16, (8, 14), 0.4), 800, 760, 4)
    d = ImageDraw.Draw(img)
    f = font("Poppins-Black.ttf", 44)
    linhas = quebra(nome, f, 520)
    y = 640
    for l in linhas:
        d.text((60, y), l, font=f, fill=WHITE, anchor="lm", stroke_width=3, stroke_fill=NAVY)
        y += 54
    fm = font("Poppins-SemiBold.ttf", 31)
    for l in quebra(mot, fm, 520):
        d.text((60, y + 10), l, font=fm, fill=WHITE, anchor="lm")
        y += 42
    pl = pilula(info(n), 26, NAVY)
    cola(img, pl, 60 + pl.width / 2, y + 50)
    return img


def antes_capa():
    img = Image.new("RGBA", (S, S), (255, 90, 60, 255))
    img.alpha_composite(papel_velho(), (0, 0))
    d = ImageDraw.Draw(img)
    d.text((540, 170), "OS CLÁSSICOS", font=font("AlfaSlabOne-Regular.ttf", 90), fill=(90, 62, 35), anchor="mm")
    d.text((540, 290), "UNO · DETETIVE · BATALHA NAVAL · WAR", font=font("Poppins-Black.ttf", 36), fill=(120, 90, 55), anchor="mm")
    corte_rasgado(img, 455)
    for j, n in enumerate(["flip7_vinganca", "micromacro", "mind_mgmt", "wonderland"]):
        cola(img, sombra(caixa(n, 300, 260), 12, (6, 12), 0.4), 180 + j * 240, 720, (-6, 3, -3, 6)[j])
    cola(img, letreiro("TÊM VERSÕES MODERNAS!", 62, WHITE, NAVY, 10), 540, 950, -2)
    return img


def antes_cta():
    img = Image.new("RGBA", (S, S), NAVY + (255,))
    d = ImageDraw.Draw(img)
    img.alpha_composite(papel_velho().crop((0, 0, S, 300)), (0, 0))
    d.text((540, 150), "DO ANTES PRO DEPOIS…", font=font("AlfaSlabOne-Regular.ttf", 64), fill=(90, 62, 35), anchor="mm")
    corte_rasgado(img, 285)
    cola(img, logo_card(300), 540, 450)
    cola(img, letreiro("ALUGUE NA SUA VEZ!", 66, (255, 214, 70), NAVY, 10), 540, 620, -2)
    for k, (t, c) in enumerate([("5 DIAS DE JOGO · 3 JOGOS = 7 DIAS", WHITE), ("RESERVE ONLINE · RETIRE EM MAUÁ E ABC", WHITE),
                                ("OU RECEBA EM CASA", (134, 239, 172)), ("LINK NA BIO · @SUAVEZ_BG", (255, 190, 120))]):
        d.text((540, 720 + k * 58), t, font=font("Bungee-Regular.ttf", 38), fill=c, anchor="mm")
    cola(img, pilula("QUAL CLÁSSICO VOCÊ AMA? COMENTA!", 32, ORANGE), 540, 990, -1)
    return img


# ================================================================ 3. RANKING DE REVISTA
TOP = [(5, "jungo", "JUNGO", "Descarte combinações maiores que as do vizinho. 15 minutos e já quer a revanche."),
       (4, "bandido", "BANDIDO", "Cooperativo: fechem todos os túneis antes que o bandido fuja. Dá até pra jogar sozinho."),
       (3, "next_station", "NEXT STATION LONDON", "Desenhe as linhas do metrô de Londres e ligue o máximo de estações."),
       (2, "dungeon_fighter", "DUNGEON FIGHTER", "Ataque os monstros arremessando os dados no alvo. Puro caos e risada!"),
       (1, "take_time", "TAKE TIME", "Cooperativo e em silêncio: acertem juntos as cartas nos relógios sem falar nada.")]
RANK_COR = [(236, 72, 153), (13, 148, 136), (37, 99, 235), (249, 115, 22), (234, 179, 8)]


def ranking(k):
    num, n, nome, mot = TOP[k]
    cor = RANK_COR[k]
    img = Image.new("RGBA", (S, S), cor + (255,))
    d = ImageDraw.Draw(img)
    d.polygon([(0, 0), (S, 0), (S, 90), (0, 170)], fill=NAVY)
    d.text((180, 66), "TOP 5 · SUA VEZ", font=font("Bungee-Regular.ttf", 44), fill=WHITE, anchor="lm")
    # número gigante vazado
    num_im = Image.new("RGBA", (620, 760), (0, 0, 0, 0))
    ImageDraw.Draw(num_im).text((310, 380), str(num), font=font("Bungee-Regular.ttf", 640), fill=(255, 255, 255, 70),
                                anchor="mm", stroke_width=10, stroke_fill=WHITE)
    cola(img, num_im, 280, 560, -6)
    cola(img, sombra(caixa(n, 470, 470), 18, (10, 18), 0.45), 720, 500, 5)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 820, S, S), fill=WHITE)
    d.rectangle((0, 820, 18, S), fill=NAVY)
    d.text((60, 868), f"#{num}  {nome}", font=font("Poppins-Black.ttf", 50), fill=NAVY, anchor="lm")
    fm = font("Poppins-SemiBold.ttf", 30)
    for j, l in enumerate(quebra(mot, fm, 900)):
        d.text((60, 925 + j * 40), l, font=fm, fill=(70, 70, 85), anchor="lm")
    pl = pilula(info(n), 24, cor)
    cola(img, pl, 60 + pl.width / 2, 1035)
    return img


def ranking_capa():
    img = Image.new("RGBA", (S, S), (234, 179, 8, 255))
    d = ImageDraw.Draw(img)
    d.polygon([(0, 0), (S, 0), (S, 300), (0, 420)], fill=NAVY)
    d.text((540, 150), "TOP 5", font=font("Bungee-Regular.ttf", 170), fill=(255, 214, 70), anchor="mm")
    d.text((540, 300), "JOGOS PRA CONHECER ESSA SEMANA", font=font("Poppins-Black.ttf", 40), fill=WHITE, anchor="mm")
    for j, n in enumerate(["jungo", "bandido", "next_station", "dungeon_fighter", "take_time"]):
        cola(img, sombra(caixa(n, 300, 240), 12, (6, 12), 0.4), 130 + j * 205, 680 + (j % 2) * 40, (-6, 4, -3, 5, -4)[j])
    cola(img, pilula("A SELEÇÃO DA SUA VEZ", 36, NAVY), 540, 930, -1)
    return img


def ranking_cta():
    img = Image.new("RGBA", (S, S), NAVY + (255,))
    d = ImageDraw.Draw(img)
    d.polygon([(0, 0), (S, 0), (S, 260), (0, 380)], fill=(234, 179, 8))
    cola(img, logo_card(320), 540, 180)
    cola(img, letreiro("ALUGUE NA SUA VEZ!", 70, (255, 214, 70), NAVY, 12), 540, 470, -2)
    for k, (t, c) in enumerate([("5 DIAS DE JOGO · 3 JOGOS = 7 DIAS", WHITE), ("RESERVE ONLINE · RETIRE EM MAUÁ E ABC", WHITE),
                                ("OU RECEBA EM CASA", (134, 239, 172)), ("LINK NA BIO · @SUAVEZ_BG", (255, 190, 120))]):
        d.text((540, 590 + k * 66), t, font=font("Bungee-Regular.ttf", 40), fill=c, anchor="mm")
    cola(img, pilula("QUAL VOCÊ JOGARIA PRIMEIRO? COMENTA!", 32, ORANGE), 540, 930, -1)
    return img


def salva(pasta, ims, cor_num=NAVY):
    d = os.path.join(OUT, pasta)
    os.makedirs(d, exist_ok=True)
    tot = len(ims)
    for i, im in enumerate(ims, 1):
        if pasta == "v2_role":
            dd = ImageDraw.Draw(im)
            dd.rounded_rectangle((S - 150, 34, S - 34, 88), radius=27, fill=(4, 70, 62))
            dd.text((S - 92, 61), f"{i}/{tot}", font=font("Bungee-Regular.ttf", 28), fill=WHITE, anchor="mm")
        else:
            num_slide(im, i, tot, cor_num)
        lg = logo_card(130)
        if pasta != "v2_role":  # no WhatsApp o logo já está no balão / topo é da conversa
            im.alpha_composite(lg, (S - lg.width - 30, 30 if pasta != "v2_top5" else 190))
        if i < tot:
            arrasta(im, NAVY if pasta != "v2_role" else (7, 94, 84), S - 135 if pasta == "v2_role" else None)
        im.convert("RGB").save(os.path.join(d, f"{i:02d}.png"))
    cols = 4
    folha = Image.new("RGB", (cols * 400, ((tot + cols - 1) // cols) * 400), "white")
    for i, im in enumerate(ims):
        folha.paste(im.convert("RGB").resize((400, 400), Image.LANCZOS), ((i % cols) * 400, (i // cols) * 400))
    folha.save(os.path.join(d, "todas.jpg"), quality=88)
    print("ok", pasta, tot)


def main():
    salva("v2_role", [zap_capa()] + [zap_slide(*ROLE[k]) for k in range(len(ROLE))] + [zap_cta()])
    salva("v2_classicos", [antes_capa()] + [antes_depois(k) for k in range(len(CLASSICOS))] + [antes_cta()])
    salva("v2_top5", [ranking_capa()] + [ranking(k) for k in range(len(TOP))] + [ranking_cta()])


if __name__ == "__main__":
    main()
