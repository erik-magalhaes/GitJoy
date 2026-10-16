#!/usr/bin/env python3
"""Reels "Quanto a gente se conhece?" (16/out/2026): Erik e Jéssica responderam as MESMAS 6 perguntas separados, sem
ouvir o outro ("o meu é X, e eu acho que o dela é Y"). Brutos do Drive (fora do git) em brutos/casal/:

    erik.mp4  20261016_153506 (3:11, ele lê cada pergunta em voz alta e responde)
    jess.mp4  20261016_171307 (1:19, a 2ª gravação dela; a 1ª, 154151, ficou de fora)

Os dois seguram o UNO Stacko como "microfone". Montagem: teaser (o tapa na cara do The Resistance) → para cada pergunta,
pergunta escrita → Erik → Jéssica → carimbo BATEU / NÃO BATEU → placar → "comenta" → tela final.
Pausas longas viram cortes secos (medidos pela energia), alternando enquadramento aberto / punch-in leve.
Pedidos: ZOOM na cara dela no "ele fica mais competitivo em todos... todos." e correção LEVE de luz e áudio.

    python3 casal.py --frame 1 8 30      # quadros de teste em out/frames.jpg
    python3 casal.py                     # out/casal_com_legenda.mp4 e out/casal_sem_legenda.mp4
"""
import argparse
import json
import os
import subprocess
import sys
import wave
from functools import lru_cache

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "comum"))
from motor import W, H, FPS, WHITE, ease, pop, logo_card, cola, sombra, letreiro, pilula, emoji, folha, ffmpeg  # noqa
import som  # noqa: E402
from audio import fx_buzz  # noqa: E402

som.FX["buzz"] = fx_buzz
BR = os.path.join(ROOT, "brutos", "casal")
OUT = os.path.join(ROOT, "out")
CAIXAS = os.path.join(REPO, "hobby-reels", "assets", "acervo")
INK = (20, 16, 30)
AMARELO = (255, 214, 70)
VERDE, VERMELHO = (22, 163, 74), (220, 38, 38)
COR = {"erik": (37, 99, 235), "jess": (219, 39, 119)}
NOME = {"erik": "ERIK", "jess": "JÉSSICA"}
# luz: só o necessário. Ele está claro (segura os brancos), ela um pouco escura (sobe os médios).
GRADE = {
    "erik": "hqdn3d=2:1.5:4:4,curves=all='0/0.01 0.25/0.245 0.5/0.5 0.75/0.75 1/0.965',"
            "eq=contrast=1.02:saturation=0.98,unsharp=5:5:0.35:5:5:0.0",
    "jess": "hqdn3d=2:1.5:4:4,curves=all='0/0.012 0.25/0.28 0.5/0.56 0.75/0.8 1/0.985',"
            "eq=contrast=1.02:saturation=0.98,unsharp=5:5:0.35:5:5:0.0",
}
VOZ = "highpass=f=80,afftdn=nr=8:nf=-48,equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1.4:g=1.5"

# blocos: (rótulo, pergunta, [(fonte, início, fim), ...], veredito). Tempos = trechos das falas no bruto.
TEASER = [("erik", 107.0, 110.75)]  # o tapa na cara em P&B ("bastidores"); repete em cores na pergunta 3 para dar o contexto (pedido dele)
BLOCOS = [  # a pergunta aparece escrita; a leitura dele em voz alta ficou de fora (vídeo mais curto)
    ("1", "QUAL É O JOGO FAVORITO DO OUTRO?",
     [("erik", 50.3, 52.9), ("erik", 55.45, 57.5), ("jess", 16.75, 22.25)], "nao"),
    ("2", "QUAL JOGO O OUTRO JOGA MELHOR QUE VOCÊ?",
     [("erik", 81.4, 86.45), ("erik", 87.35, 92.2), ("erik", 93.5, 96.55), ("jess", 25.4, 31.2)], "nao"),
    ("3", "QUAL JOGO JÁ DEU BRIGA ENTRE VOCÊS?",
     [("erik", 100.9, 104.65), ("erik", 107.0, 110.75), ("erik", 112.45, 113.5), ("jess", 34.45, 39.05)], "sim"),
    ("4", "QUAL A PIOR DESCULPA DO OUTRO QUANDO PERDE?",
     [("erik", 125.8, 128.4), ("erik", 134.3, 136.9), ("erik", 140.75, 141.7), ("erik", 143.55, 147.85),
      ("jess", 43.8, 50.45)], "nao"),
    ("5", "EM QUAL JOGO O OUTRO FICA MAIS COMPETITIVO?",
     [("erik", 160.25, 170.75), ("jess", 55.3, 60.95), ("jess", 61.1, 65.6, "inteiro")], "nao"),
    ("6", "QUAL FOI O PRIMEIRO JOGO QUE VOCÊS JOGARAM JUNTOS?",
     [("erik", 175.75, 184.85), ("jess", 70.15, 73.15)], "quase"),
]
ZOOM_JESS = (63.30, 0.22, 1.42)  # (tempo no bruto, duração, escala): o "todos... todos."
VEREDITO = 0.9                   # segundos do quadro congelado com o carimbo
PLACAR, COMENTA, FIM = 2.3, 2.6, 3.6
# correções do Whisper, por (fonte, índice da palavra): texto novo ou None para apagar
CORRIGE = {("erik", 244): "Patinhas!", ("erik", 242): "É", ("erik", 243): "Tio", ("erik", 296): "Cat",
           ("erik", 331): "Scotland", ("erik", 332): "Yard.", ("jess", 63): "roubou."}
GAP, PAD = 0.3, 0.1  # silêncio maior que GAP vira corte; PAD de folga em cada lado


# ---------------------------------------------------------------- cortes pela energia
@lru_cache(None)
def energia(src):
    w = wave.open(os.path.join(BR, src + "16.wav"))
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
    q = 320  # 20 ms
    n = len(x) // q
    e = 20 * np.log10(np.sqrt((x[:n * q].reshape(n, q) ** 2).mean(1)) + 1e-9)
    return e


def pedacos(src, a, b):
    """Divide [a, b] nos trechos com voz, cortando os silêncios longos."""
    e = energia(src)
    i0, i1 = int(a / 0.02), int(b / 0.02)
    seg = e[i0:i1]
    piso = np.percentile(e[e > -90], 15)
    voz = seg > max(piso + 15, -38)
    idx = np.where(voz)[0]
    if not len(idx):
        return []
    out, ini, ant = [], idx[0], idx[0]
    for k in idx[1:]:
        if (k - ant) * 0.02 > GAP:
            out.append((ini, ant))
            ini = k
        ant = k
    out.append((ini, ant))
    res = []
    for s, f in out:
        ta, tb = a + s * 0.02 - PAD, a + (f + 1) * 0.02 + PAD + 0.14  # rabo das palavras é fraco ("Ride" ficava cortado)
        ta, tb = max(a, ta), min(b, tb)
        if tb - ta > 0.15:
            res.append((ta, tb))
    return res


@lru_cache(None)
def palavras(src):
    return json.load(open(os.path.join(BR, src + "_palavras.json"), encoding="utf-8"))


def nq(t0, d):
    return round((t0 + d) * FPS) - round(t0 * FPS)


def linha():
    """Lista de planos (t0, nquadros, fonte, início, tipo, bloco, punch)."""
    tl, t, k = [], 0.0, 0
    marcas = {}

    def poe(src, a, b, tipo, blk, inteiro=False):
        nonlocal t, k
        for ta, tb in ([(a, b)] if inteiro else pedacos(src, a, b)):
            if not inteiro and tb - ta < 0.9 and not any(ta <= (w["a"] + min(w["b"], w["a"] + 0.6)) / 2 < tb
                                                         for w in palavras(src)):
                continue  # pedacinho sem palavra (respiro, barulho do microfone)
            n = nq(t, tb - ta)
            tl.append(dict(t0=t, n=n, src=src, a=ta, tipo=tipo, blk=blk, punch=k % 2))
            t += n / FPS
            k += 1

    for src, a, b in TEASER:
        poe(src, a, b, "teaser", None)
    marcas["teaser_fim"] = t
    for j, (rot, perg, partes, ver) in enumerate(BLOCOS):
        marcas[f"b{j}"] = t
        for parte in partes:
            poe(*parte[:3], "fala", j, len(parte) > 3)
        n = nq(t, VEREDITO)
        tl.append(dict(t0=t, n=n, src=None, a=0, tipo="veredito", blk=j, punch=0))
        marcas[f"v{j}"] = t
        t += n / FPS
    marcas["placar"] = t
    t += PLACAR
    marcas["comenta"] = t
    t += COMENTA
    marcas["fim"] = t
    return tl, marcas, t + FIM


TL, M, DUR = linha()


def plano_em(t):
    for p in TL:
        if p["t0"] <= t < p["t0"] + p["n"] / FPS:
            return p
    return None


# ---------------------------------------------------------------- legendas palavra a palavra
def subs():
    pal = []
    for p in TL:
        if p["src"] is None:
            continue
        a, b = p["a"], p["a"] + p["n"] / FPS
        for i, w in enumerate(palavras(p["src"])):
            meio = (w["a"] + min(w["b"], w["a"] + 0.6)) / 2
            if a <= meio < b:
                txt = CORRIGE.get((p["src"], i), w["w"])
                if txt:
                    pal.append((txt, p["t0"] + max(0.0, w["a"] - a), p["t0"] + min(b, w["b"]) - a))
    grupos, cur = [], []
    for w in pal:
        if cur and w[1] - cur[-1][2] > 0.5:
            grupos.append(cur)
            cur = []
        cur.append(w)
        if len(cur) == 3 or len(" ".join(x[0] for x in cur)) > 14 or w[0][-1] in ",.!?":
            grupos.append(cur)
            cur = []
    if cur:
        grupos.append(cur)
    out = []
    for j, g in enumerate(grupos):
        prox = grupos[j + 1][0][1] if j + 1 < len(grupos) else g[-1][2] + 0.4
        out.append((g[0][1], min(prox, g[-1][2] + 0.5), [(x[0], x[1]) for x in g]))
    return out


SUBS = subs()

# jogo citado → caixa na tela (índice da palavra no palavras.json de cada um)
CITA = {"erik": {30: "wingspan", 44: "harmonies", 87: "clank_catacombs", 113: "ticket_to_ride", 174: "the_resistance",
                 286: "dracula_vs_van_helsing", 296: "cat_in_the_box", 319: "dixit", 331: "scotland_yard"},
        "jess": {5: "clank_a_deck_building_adventure", 13: "ticket_to_ride", 21: "sea_salt_paper", 31: "wingspan",
                 45: "the_resistance", 72: "ticket_to_ride", 101: "dixit"}}
CASAL = os.path.join(ROOT, "assets", "casal")


def mencoes():
    out = []
    for p in TL:
        if p["src"] is None:
            continue
        a, b = p["a"], p["a"] + p["n"] / FPS
        for i, nome in CITA[p["src"]].items():
            w = palavras(p["src"])[i]
            if a <= w["a"] < b:
                out.append((p["t0"] + w["a"] - a, nome, p["blk"]))
    return sorted(out)


MENCOES = mencoes()


@lru_cache(None)
def caixa_cit(nome):
    pasta = CASAL if os.path.exists(os.path.join(CASAL, nome + ".png")) else CAIXAS
    im = Image.open(os.path.join(pasta, nome + ".png")).convert("RGBA")
    im = im.crop(im.getchannel("A").getbbox())
    h = 270
    w = int(im.width * h / im.height)
    if w > 330:
        w, h = 330, int(im.height * 330 / im.width)
    return sombra(im.resize((w, h), Image.LANCZOS), 16, (0, 14), 0.55)


def caixa_citada(img, t):
    """A caixa aparece quando o nome é dito e fica até 2,6 s (ou até o próximo jogo do mesmo bloco)."""
    for k, (t0, nome, blk) in enumerate(MENCOES):
        fim = t0 + 2.6
        if k + 1 < len(MENCOES) and MENCOES[k + 1][2] == blk:
            fim = min(fim, MENCOES[k + 1][0])
        if t0 - 0.1 <= t < fim:
            sc = pop(t, t0 - 0.1, 0.3)
            if fim - t < 0.15:
                sc *= max(0.0, (fim - t) / 0.15)
            cola(img, caixa_cit(nome), 905, 760, 5 if k % 2 else -5, sc)
            return


@lru_cache(None)
def palavra_img(txt, amarela):
    return letreiro(txt.upper(), 78, AMARELO if amarela else WHITE, INK, 11, "Poppins-Black.ttf")


def legenda(img, t):
    for a, b, g in SUBS:
        if a <= t < b:
            agora = max(j for j, (_, w0) in enumerate(g) if w0 <= t or j == 0)
            ims = [palavra_img(w, j == agora) for j, (w, _) in enumerate(g)]
            gap, larg = 18, 940
            linhas, cur, cw = [], [], 0
            for im in ims:
                w_ = im.width - 22
                if cur and cw + gap + w_ > larg:
                    linhas.append(cur)
                    cur, cw = [], 0
                cw += (gap if cur else 0) + w_
                cur.append(im)
            linhas.append(cur)
            sc = 0.85 + 0.15 * ease(min(1.0, (t - a) / 0.12))
            y = 1470 - (len(linhas) - 1) * 100
            for ln in linhas:
                lw = sum(x.width - 22 for x in ln) + gap * (len(ln) - 1)
                x = 540 - lw / 2
                for im in ln:
                    cola(img, im, x + (im.width - 22) / 2, y, 0, sc)
                    x += im.width - 22 + gap
                y += 100
            return


# ---------------------------------------------------------------- textos
@lru_cache(None)
def cartao_pergunta(j):
    """Pergunta num painel escuro (legível por cima da caixa do UNO Stacko), com a etiqueta do número."""
    from motor import font
    rot, perg = BLOCOS[j][0], BLOCOS[j][1]
    f = font("Poppins-Black.ttf", 58)
    d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    linhas, cur = [], ""
    for w in perg.split():
        if cur and d0.textlength(cur + " " + w, font=f) > 880:
            linhas.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    linhas.append(cur)
    lw = max(d0.textlength(l, font=f) for l in linhas)
    pw, ph = int(lw + 80), int(len(linhas) * 70 + 70)
    im = Image.new("RGBA", (pw, ph + 34), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 34, pw - 1, ph + 33), radius=34, fill=INK + (225,), outline=WHITE, width=4)
    for k, l in enumerate(linhas):
        d.text((pw / 2, 34 + 50 + k * 70), l, font=f, fill=WHITE, anchor="mm")
    tag = pilula(f"PERGUNTA {rot}", 34, AMARELO, INK, INK)
    im.alpha_composite(tag, ((pw - tag.width) // 2, 0))
    return im


@lru_cache(None)
def nome_tag(src):
    return pilula(NOME[src], 40, COR[src])


@lru_cache(None)
def carimbo(ver):
    txt, cor = {"sim": ("BATEU!", VERDE), "nao": ("NÃO BATEU!", VERMELHO), "quase": ("QUASE!", (234, 179, 8))}[ver]
    ic = {"sim": "✅", "nao": "❌", "quase": "🤏"}[ver]
    t = letreiro(txt, 130, WHITE, cor, 16, "Poppins-Black.ttf", sombra_px=8, cor_sombra=INK)
    e = emoji(ic, 150)
    im = Image.new("RGBA", (max(t.width, e.width), t.height + e.height - 10), (0, 0, 0, 0))
    im.alpha_composite(e, ((im.width - e.width) // 2, 0))
    im.alpha_composite(t, ((im.width - t.width) // 2, e.height - 10))
    return im


@lru_cache(None)
def caixa(nome, h):
    im = Image.open(os.path.join(CAIXAS, nome + ".png")).convert("RGBA")
    im = im.crop(im.getchannel("A").getbbox())
    im = im.resize((max(2, int(im.width * h / im.height)), int(h)), Image.LANCZOS)
    return sombra(im, 14, (0, 12), 0.5)


JOGOS = ["wingspan", "harmonies", "ticket_to_ride", "clank_catacombs", "sea_salt_paper", "the_resistance",
         "dracula_vs_van_helsing", "dixit"]


def placar(img, t):
    u = t - M["placar"]
    cola(img, letreiro("PLACAR FINAL", 84, AMARELO, INK, 12, "Poppins-Black.ttf"), 540, 640, -2, pop(t, M["placar"]))
    cola(img, letreiro("1 DE 6", 210, WHITE, INK, 18, "Poppins-Black.ttf", sombra_px=10, cor_sombra=INK), 540, 860, 0,
         pop(t, M["placar"] + 0.25))
    if u > 0.7:
        cola(img, letreiro("(e um quase...)", 64, WHITE, INK, 9, "Poppins-ExtraBold.ttf"), 540, 1060, 2,
             pop(t, M["placar"] + 0.7))
    if u > 1.1:
        cola(img, emoji("😅", 170), 540, 1260, 0, pop(t, M["placar"] + 1.1))


def comenta(img, t):
    u = t - M["comenta"]
    cola(img, letreiro("E VOCÊS?", 120, AMARELO, INK, 14, "Poppins-Black.ttf"), 540, 650, -3, pop(t, M["comenta"]))
    cola(img, letreiro("QUANTAS VOCÊS\nACERTARIAM?", 86, WHITE, INK, 12, "Poppins-Black.ttf"), 540, 880, 0,
         pop(t, M["comenta"] + 0.25))
    if u > 0.8:
        cola(img, pilula("MARCA O SEU PAR E COMENTA AQUI!", 40, COR["jess"]), 540, 1110, 0, pop(t, M["comenta"] + 0.8))
    if u > 1.1:
        cola(img, emoji("💬", 130), 540, 1290, 0, pop(t, M["comenta"] + 1.1))


def tela_final(img, t):
    t0 = M["fim"]
    u = t - t0
    cola(img, logo_card(360), 540, 270, 0, pop(t, t0))
    pos = [(200, 620), (420, 600), (660, 600), (880, 620), (200, 900), (420, 880), (660, 880), (880, 900)]
    for j, (n, (x, y)) in enumerate(zip(JOGOS, pos)):
        if u > 0.12 + 0.06 * j:
            cola(img, caixa(n, 230), x, y, (-5, 3, -3, 5)[j % 4], pop(t, t0 + 0.12 + 0.06 * j))
    itens = [(0.6, letreiro("OS JOGOS DO VÍDEO\nESTÃO NA SUA VEZ!", 70, AMARELO, INK, 11, "Poppins-Black.ttf"), 1150),
             (0.85, pilula("RESERVE ONLINE · RETIRE EM MAUÁ E ABC", 34, WHITE, INK, INK), 1320),
             (1.0, pilula("OU RECEBA EM CASA!", 42, VERDE), 1420),
             (1.15, pilula("LINK NA BIO · @SUAVEZ_BG", 48, (249, 115, 22)), 1530)]
    for ti, im, y in itens:
        if u >= ti:
            cola(img, im, 540, y, 0, pop(t, t0 + ti))


@lru_cache(None)
def titulo_teaser():
    return letreiro("QUANTO A GENTE\nSE CONHECE?", 96, AMARELO, INK, 13, "Poppins-Black.ttf", sombra_px=6,
                    cor_sombra=INK)


def overlay(t, com_legenda):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if t >= M["placar"]:
        (placar if t < M["comenta"] else comenta if t < M["fim"] else tela_final)(img, t)
        return img
    wm = logo_card(150)
    img.alpha_composite(wm, (W - wm.width - 30, 40))
    p = plano_em(t)
    if t < M["teaser_fim"]:
        cola(img, titulo_teaser(), 540, 1130, -2, pop(t, 0.0))
    elif p is not None:
        j = p["blk"]
        if p["src"]:
            cola(img, cartao_pergunta(j), 540, 1130, 0, pop(t, M[f"b{j}"]))
            ini = min(q["t0"] for q in TL if q["blk"] == j and q["src"] == p["src"])
            cola(img, nome_tag(p["src"]), 540, 945, -3, pop(t, ini))
        else:
            cola(img, carimbo(BLOCOS[j][3]), 540, 1150, -6, pop(t, M[f"v{j}"], 0.3))
    if p is not None and p["src"]:
        caixa_citada(img, t)
    if com_legenda and (p is None or p["src"]):
        legenda(img, t)
    return img


# ---------------------------------------------------------------- vídeo
def ler(src, a, n):
    vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},{GRADE[src]}"
    p = subprocess.Popen([ffmpeg(), "-loglevel", "error", "-ss", f"{a:.3f}", "-i", os.path.join(BR, src + ".mp4"), "-frames:v",
                          str(n), "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    k, ultimo = 0, None
    while k < n:
        buf = p.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        ultimo = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        yield ultimo
        k += 1
    while k < n:
        yield ultimo
        k += 1
    p.wait()


def escala(fr, s, cy=0.22):
    """Punch-in ancorado perto do rosto (cy = altura do rosto na tela, de 0 a 1)."""
    if s <= 1.001:
        return fr
    w, h = W / s, H / s
    x0 = (W - w) / 2
    y0 = min(max(0.0, cy * H - h * min(cy * s, 0.4)), H - h)  # o rosto desce até ~40% no zoom forte
    M_ = np.float32([[s, 0, -x0 * s], [0, s, -y0 * s]])
    return cv2.warpAffine(fr, M_, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


def zoom_jess(p, k):
    t_src = p["a"] + k / FPS
    z0, zd, zs = ZOOM_JESS
    if p["src"] != "jess" or p["blk"] != 4 or t_src < z0:
        return None
    return 1 + (zs - 1) * ease(min(1.0, (t_src - z0) / zd))


def quadros():
    ultimo, s_ult = None, 1.0
    for p in TL:
        if p["src"] is None:  # veredito: congela o último quadro
            for k in range(p["n"]):
                yield ultimo
            continue
        for k, fr in enumerate(ler(p["src"], p["a"], p["n"])):
            if p["tipo"] == "teaser":  # flash-forward em preto e branco (pedido dele)
                g = cv2.cvtColor(fr, cv2.COLOR_RGB2GRAY)
                g = cv2.convertScaleAbs(g, alpha=1.12, beta=-12)
                fr = np.repeat(g[..., None], 3, 2)
            z = zoom_jess(p, k)
            s = z if z else (1.07 if p["punch"] else 1.0)
            fr = escala(fr, s, 0.18 if p["src"] == "jess" else 0.2)
            ultimo = fr
            yield fr
    fundo = Image.fromarray(ultimo).filter(ImageFilter.GaussianBlur(22))
    fundo = np.asarray(Image.blend(fundo, Image.new("RGB", (W, H), (14, 10, 28)), 0.6))
    for k in range(round((DUR - M["placar"]) * FPS) + 1):
        yield fundo


# ---------------------------------------------------------------- áudio
def ler_audio(src, a, d):
    r = subprocess.run([ffmpeg(), "-loglevel", "error", "-ss", f"{a:.3f}", "-t", f"{d:.4f}", "-i",
                        os.path.join(BR, src + ".mp4"), "-vn", "-ac", "1", "-ar", "44100", "-af", VOZ, "-f", "s16le", "-"],
                       capture_output=True)
    x = np.frombuffer(r.stdout, np.int16).astype(np.float64) / 32768
    n = int(round(d * 44100))
    return np.pad(x, (0, max(0, n - len(x))))[:n]


@lru_cache(None)
def ganho(src):
    """Ganho FIXO por pessoa (mesma voz em todo o vídeo, sem bombear)."""
    x = ler_audio(src, 0, 200)
    q = int(0.03 * 44100)
    e = np.sqrt(np.convolve(x ** 2, np.ones(q) / q, "same"))
    voz = e > e.max() * 0.12
    return 10 ** (-20 / 20) / (np.sqrt((x[voz] ** 2).mean()) + 1e-9)


def audio(path):
    sr = 44100
    voz = np.zeros(int(DUR * sr) + sr)
    cues = [(0.0, "pop", 0.4)]
    for p in TL:
        if p["src"] is None:
            cues.append((p["t0"] + 0.02, "ding" if BLOCOS[p["blk"]][3] == "sim" else
                         ("boing" if BLOCOS[p["blk"]][3] == "quase" else "buzz"), 0.7))
            continue
        d = p["n"] / FPS
        x = ler_audio(p["src"], p["a"], d) * ganho(p["src"])
        f = int(0.015 * sr)
        x[:f] *= np.linspace(0, 1, f)
        x[-f:] *= np.linspace(1, 0, f)
        i = int(round(p["t0"] * sr))
        voz[i:i + len(x)] += x
    for j in range(len(BLOCOS)):
        cues.append((M[f"b{j}"] - 0.05, "whoosh", 0.4))
    z0 = next(p for p in TL if p["src"] == "jess" and p["blk"] == 4 and p["a"] <= ZOOM_JESS[0] < p["a"] + p["n"] / FPS)
    cues.append((z0["t0"] + ZOOM_JESS[0] - z0["a"] - 0.05, "whoosh", 0.6))
    cues += [(M["placar"], "whoosh", 0.4), (M["placar"] + 0.25, "carimbo", 0.6), (M["comenta"], "whoosh", 0.4),
             (M["comenta"] + 0.8, "pop", 0.5), (M["fim"], "whoosh", 0.4), (M["fim"] + 0.6, "ding", 0.5)]
    vp = os.path.join(OUT, "casal_voz.wav")
    with wave.open(vp, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.clip(voz, -1, 1) * 32767).astype(np.int16).tobytes())
    som.build(path, DUR, cues, musica="gameshow", voz=[(vp, 0.0)], fx_ganho=0.35, duck=0.55, musica_ganho=0.24,
              satura=False)
    r = subprocess.run([ffmpeg(), "-hide_banner", "-i", path, "-af", "loudnorm=I=-15.5:TP=-2:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    tmp = path.replace(".wav", "_n.wav")
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", path, "-af",
                    f"loudnorm=I=-15.5:TP=-2:LRA=11:linear=true:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
                    f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}",
                    "-ar", "44100", tmp], check=True)
    os.replace(tmp, path)


def render(saidas, wav):
    ws = {}
    for saida, leg in saidas:
        ws[leg] = subprocess.Popen([ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s",
                                    f"{W}x{H}", "-framerate", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-crf",
                                    "19", "-preset", "medium", "-tune", "film", "-pix_fmt", "yuv420p", "-c:a", "aac",
                                    "-b:a", "192k", "-shortest", "-movflags", "+faststart", saida], stdin=subprocess.PIPE)
    for n, fr in enumerate(quadros()):
        t = n / FPS
        if t >= DUR:
            break
        base = Image.fromarray(fr).convert("RGBA")
        for leg, p in ws.items():
            im = base.copy()
            im.alpha_composite(overlay(t, leg))
            p.stdin.write(im.convert("RGB").tobytes())
    for p in ws.values():
        p.stdin.close()
        p.wait()
    print("ok", [s for s, _ in saidas], flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    ap.add_argument("--info", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    print(f"duração {DUR:.1f} s; marcas", {k: round(v, 1) for k, v in M.items()})
    if a.info:
        for p in TL:
            print(f"{p['t0']:6.2f} {p['n'] / FPS:5.2f} {p['src']} {p['a']:.2f}")
        return
    if a.frame:
        alvo = {round(x * FPS): x for x in a.frame}
        ims = {}
        for n, fr in enumerate(quadros()):
            if n in alvo:
                im = Image.fromarray(fr).convert("RGBA")
                im.alpha_composite(overlay(n / FPS, True))
                ims[n] = im.convert("RGB")
            if len(ims) == len(alvo):
                break
        folha([ims[k] for k in sorted(ims)], os.path.join(OUT, "frames.jpg"))
        return
    wav = os.path.join(OUT, "casal.wav")
    audio(wav)
    render([(os.path.join(OUT, "casal_com_legenda.mp4"), True)], wav)  # ele pediu só a versão com legenda


if __name__ == "__main__":
    main()
