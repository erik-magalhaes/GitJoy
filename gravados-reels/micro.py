#!/usr/bin/env python3
"""Reels "LINHA MICRO DA PAPERGAMES: 3 JOGOS POR R$ 15" (27/out/2026). Ele gravou 3 stories apresentando as 3 caixinhas
(brutos fora do git em brutos/out27/): 1·2·3 (O Que O Quê, Duo Regna, Qui-Quitanda), 4·5·6 (ProcuRatos, Glifos,
Glitches) e 7·8·9 (Lemur, Córdoba, Lux Nova). Pedido: "legenda, bem dinâmico e bem legal".
Edição: um Reels só com os 3 stories. Saem o que era de story ("no próximo Stories", "vou colocar o link") e os
tropeços ("Opa! Lado errado", "faz tenkano joguem, galera. Foi mal", "de fazer... de ferrar"). A câmera da frente grava ESPELHADO: a imagem é
desespelhada (as caixas ficam legíveis). Cortes secos pela energia alternando aberto / punch-in, fala a 1,1x, legenda
palavra a palavra; quando ele fala o nome de um jogo, a caixa OFICIAL (PaperGames, assets/micro/recorte/) pula na tela
com a etiqueta do que ele disse; "comenta" e tela final com as 3 caixinhas.

    python3 micro.py --info            # linha do tempo
    python3 micro.py --frame 2 20 40   # out/frames_micro.jpg
    python3 micro.py                   # out/micro.mp4 + out/micro_chat.mp4
"""
import argparse
import json
import os
import subprocess
import sys
import wave
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "comum"))
sys.path.insert(0, os.path.join(REPO, "listas-reels"))
from motor import W, H, FPS, WHITE, ease, seg, out_back, logo_card, cola, letreiro, folha, ffmpeg  # noqa: E402
import som  # noqa: E402
from base import texto  # noqa: E402

BR = os.path.join(ROOT, "brutos", "out27")
OUT = os.path.join(ROOT, "out")
CX = os.path.join(ROOT, "assets", "micro", "recorte")
ARQ = {"1": "VID_20261027_100508_573", "2": "VID_20261027_100708_386", "3": "VID_20261027_101152_072"}
INK, AMARELO = (63, 36, 18), (255, 199, 31)
LARANJA, PETROLEO, VERDE, ROSA, ROXO = (244, 136, 37), (28, 124, 150), (40, 160, 90), (219, 39, 119), (108, 63, 160)
GRADE = "hflip,hqdn3d=1.5:1.5:3:3,unsharp=5:5:0.35:5:5:0.0,eq=contrast=1.02:saturation=1.02"
VOZ = "highpass=f=80,afftdn=nr=8:nf=-48,equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1.4:g=1.5"
VEL = 1.1
# (fonte, início, fim, tipo) — tempos no bruto
TRECHOS = [
    ("1", 0.00, 4.65, "gancho"),   # "Você sabia que você consegue alugar três jogos por apenas R$ 15 no nosso site?"
    ("1", 4.65, 24.45, "fala"),    # linha Micro, caixinha 1·2·3 ... "um pouquinho mais estratégico." (sem o "próximo Stories")
    ("2", 0.30, 3.62, "fala"),     # "E continuando aqui, a gente tem o jogo 4, 5 e 6," (sem "que é o... Opa! Lado errado.")
    ("2", 5.85, 17.28, "fala"),    # "É o ProcuRatos, o Glifos e o Glitches. ProcuRatos é... Glifos,"
    ("2", 20.55, 34.70, "fala"),   # (sem "se eu não me engano... faz tenkano joguem, galera. Foi mal. Mas") "se eu não me engano, também..."
    ("3", 0.00, 14.08, "fala"),    # caixinha 7·8·9 ... "essa pegada de jogo de carta"
    ("3", 15.35, 36.20, "fala"),   # (sem o "de fazer..." tropeçado) "de ferrar o amiguinho" ... "então aproveita!"
]
# o Whisper erra os nomes; palavra vazia = some da legenda
CORRIGE = {"QQ,": "O Que O Quê,", "Kiki": "Qui-Quitanda", "Tanda.": "", "Tanda": "", "Procuratus,": "ProcuRatos,",
           "Procuratus": "ProcuRatos", "Glyphos": "Glifos", "Glyphos,": "Glifos,", "R": "R$ 15", "$15": "", ",00": "",
           "Uno,": "UNO,", "Micro": "Micro"}
JOGOS = {  # ficha da PaperGames (todos 10 min)
    "o-que-o-que": ("O QUE O QUÊ", "2 a 5 jogadores"), "duo-regna": ("DUO REGNA", "2 jogadores"),
    "qui-quitanda": ("QUI-QUITANDA", "1 a 4 jogadores"), "procuratos": ("PROCURATOS", "2 a 6 jogadores"),
    "glifos": ("GLIFOS", "1 a 5 jogadores"), "glitches": ("GLITCHES", "2 jogadores"),
    "lemur": ("LEMUR", "2 a 4 jogadores"), "cordoba": ("CÓRDOBA", "2 jogadores"), "lux-nova": ("LUX NOVA", "1 a 4 jogadores"),
}
CAIXAS = [("1 · 2 · 3", ["o-que-o-que", "duo-regna", "qui-quitanda"]), ("4 · 5 · 6", ["procuratos", "glifos", "glitches"]),
          ("7 · 8 · 9", ["lemur", "cordoba", "lux-nova"])]
# a caixinha aparece com os 3 jogos em fileira; cada um acende quando ele fala o nome (ou o tipo, na 3ª)
FILEIRAS = [("1", 11.80, 17.15, 0, [13.9, 14.7, 15.7]), ("2", 1.90, 9.40, 1, [6.4, 7.5, 8.2]),
            ("3", 1.90, 9.50, 2, [6.2, 7.4, 8.6])]
# quando ele DESCREVE o jogo: a caixa grande com a etiqueta do que ele falou
CARTOES = [("1", 19.70, "o-que-o-que", "MAIS GALERA", LARANJA), ("1", 20.50, "duo-regna", "PRA DUAS PESSOAS", ROSA),
           ("1", 22.40, "qui-quitanda", "MAIS ESTRATÉGICO", ROXO), ("2", 9.50, "procuratos", "JOGO DE MEMÓRIA", LARANJA),
           ("2", 16.90, "glifos", "MEMÓRIA + COLEÇÃO", PETROLEO), ("2", 25.50, "glitches", "HACKER · PRA DUPLA", VERDE),
           ("3", 9.60, "lemur", "O DA GALERA", LARANJA), ("3", 17.30, "cordoba", "PRA DOIS", ROSA),
           ("3", 27.10, "lux-nova", "O MAIS ESTRATÉGICO", ROXO)]
SELOS = [("1", 6.40, "LINHA MICRO · PAPERGAMES", PETROLEO), ("1", 9.70, "3 JOGOS EM CADA CAIXINHA", VERDE),
         ("2", 33.40, "NOSSO FAVORITO DA CAIXA!", ROSA), ("3", 30.40, "3 JOGOS POR R$ 15!", VERDE),
         ("3", 35.40, "APROVEITA!", LARANJA)]
GAP, PAD = 0.32, 0.1
COMENTA, FIM = 3.4, 4.2


# ---------------------------------------------------------------- cortes pela energia
@lru_cache(None)
def energia(src):
    w = wave.open(os.path.join(BR, ARQ[src] + ".wav"))
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
    q = int(0.02 * w.getframerate())
    n = len(x) // q
    return 20 * np.log10(np.sqrt((x[:n * q].reshape(n, q) ** 2).mean(1)) + 1e-9)


@lru_cache(None)
def palavras(src):
    d = json.load(open(os.path.join(BR, "palavras.json"), encoding="utf-8"))
    return [dict(s=s, e=e, w=w) for s, e, w in d[ARQ[src] + ".wav"]]


def pedacos(src, a, b):
    e = energia(src)
    i0, i1 = int(a / 0.02), min(len(e), int(b / 0.02))
    piso = np.percentile(e[e > -90], 15)
    voz = e[i0:i1] > max(piso + 14, -40)
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
        ta, tb = max(a, a + s * 0.02 - PAD), min(b, a + (f + 1) * 0.02 + PAD + 0.14)
        tem = any(ta <= (w["s"] + w["e"]) / 2 < tb for w in palavras(src))
        if tb - ta > 0.2 and tem:
            res.append((ta, tb))
    return res


def nq(t0, d):
    return round((t0 + d) * FPS) - round(t0 * FPS)


def linha():
    tl, t, marcas = [], 0.0, {}
    for j, (src, a, b, tipo) in enumerate(TRECHOS):
        marcas.setdefault(tipo, t)
        for ta, tb in pedacos(src, a, b):
            n = nq(t, (tb - ta) / VEL)
            tl.append(dict(t0=t, n=n, src=src, a=ta, j=j, tipo=tipo))
            t += n / FPS
    marcas["comenta"] = t
    marcas["fim"] = t + COMENTA
    return tl, marcas, t + COMENTA + FIM


TL, M, DUR = linha()


def no_video(src, ts):
    """Tempo no vídeo de um instante ts do bruto (se caiu num corte, o começo do próximo pedaço)."""
    for p in TL:
        if p["src"] == src and p["a"] <= ts < p["a"] + p["n"] / FPS * VEL:
            return p["t0"] + (ts - p["a"]) / VEL
    return min(p["t0"] for p in TL if p["src"] == src and p["a"] >= ts)


# ---------------------------------------------------------------- legenda palavra a palavra
def subs():
    pal = []
    for p in TL:
        if p["tipo"] == "gancho":  # no gancho o letreiro já diz a frase
            continue
        a, b = p["a"], p["a"] + p["n"] / FPS * VEL
        for w in palavras(p["src"]):
            if a <= (w["s"] + w["e"]) / 2 < b:
                txt = CORRIGE.get(w["w"].strip(), w["w"].strip())
                if txt:
                    pal.append((txt, p["t0"] + max(0.0, w["s"] - a) / VEL, p["t0"] + (min(b, w["e"]) - a) / VEL))
    grupos, cur = [], []
    for w in pal:
        if cur and w[1] - cur[-1][2] > 0.5:
            grupos.append(cur)
            cur = []
        cur.append(w)
        if len(cur) == 3 or len(" ".join(x[0] for x in cur)) > 15 or w[0][-1] in ",.!?":
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


@lru_cache(None)
def palavra_img(txt, amarela):
    return letreiro(txt.upper(), 74, AMARELO if amarela else WHITE, (20, 16, 30), 11, "Poppins-Black.ttf")


def legenda(img, t, y0=1490):
    for a, b, g in SUBS:
        if a <= t < b:
            agora = max(j for j, (_, w0) in enumerate(g) if w0 <= t or j == 0)
            ims = [palavra_img(w, j == agora) for j, (w, _) in enumerate(g)]
            gap, larg = 16, 960
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
            y = y0 - (len(linhas) - 1) * 92
            for ln in linhas:
                lw = sum(x.width - 22 for x in ln) + gap * (len(ln) - 1)
                x = 540 - lw / 2
                for im in ln:
                    cola(img, im, x + (im.width - 22) / 2, y, 0, sc)
                    x += im.width - 22 + gap
                y += 92
            return


# ---------------------------------------------------------------- peças
@lru_cache(None)
def caixa(nome, h):
    im = Image.open(os.path.join(CX, nome + "_caixa.png")).convert("RGBA")
    im = im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
    sh = Image.new("RGBA", (im.width + 40, im.height + 40), (0, 0, 0, 0))
    a = im.getchannel("A").point(lambda v: int(v * 0.45))
    sh.paste((0, 0, 0, 255), (26, 30), a)
    sh = sh.filter(ImageFilter.GaussianBlur(9))
    sh.alpha_composite(im, (10, 8))
    return sh


@lru_cache(None)
def pilula(txt, s, cor, fg=WHITE):
    tx = texto(txt, "lilita", s, fg)
    im = Image.new("RGBA", (tx.width + 52, tx.height + 22), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 10, im.width - 1, im.height - 1), radius=(im.height - 10) // 2, fill=INK)
    d.rounded_rectangle((0, 0, im.width - 9, im.height - 11), radius=(im.height - 10) // 2, fill=cor, outline=INK, width=6)
    im.alpha_composite(tx, (22, 0))
    return im


@lru_cache(None)
def titulo(txt, s, cor=WHITE):
    return texto(txt, "lilita", s, cor, INK, max(7, s // 10), max(6, s // 12), INK, entre=1.0)


@lru_cache(None)
def ficha(txt):
    return texto(txt + " · 10 min", "figtree", 44, WHITE, INK, 0, 4, INK)


def eventos(lista, k_t=1):
    return sorted([(no_video(x[0], x[k_t]),) + tuple(x) for x in lista])


CART_T = eventos(CARTOES)
SELO_T = eventos(SELOS)
FIL_T = [(no_video(s, a), no_video(s, b), k, [no_video(s, x) for x in acende]) for s, a, b, k, acende in FILEIRAS]


def fileira(img, t):
    for t0, t1, k, acende in FIL_T:
        if t0 - 0.05 <= t < t1 + 0.3:
            lt, sai = t - t0, ease(seg(t, t1, t1 + 0.3))
            num, nomes = CAIXAS[k]
            cola(img, pilula("CAIXINHA " + num, 62, AMARELO, INK), W / 2, 1075, rot=-3,
                 sc=out_back(seg(lt, 0.0, 0.3)) * (1 - sai))
            for j, nome in enumerate(nomes):
                aceso = t >= acende[j]
                u = out_back(seg(lt, 0.15 + j * 0.1, 0.45 + j * 0.1)) * (1 - sai)
                pulo = 1.0 + 0.18 * (1 - ease(seg(t, acende[j], acende[j] + 0.25))) * (t >= acende[j])
                cola(img, caixa(nome, 270), 250 + j * 290, 1265, rot=(-6, 0, 6)[j],
                     sc=u * (1.08 if aceso else 0.9) * pulo, alpha=1.0 if aceso else 0.75)
            return True
    return False


def cartao(img, t):
    for i, (tv, _s, _ts, nome, tag, cor) in enumerate(CART_T):
        prox = CART_T[i + 1][0] if i + 1 < len(CART_T) else tv + 4
        dura = min(prox - tv, 5.0)
        lt = t - tv
        if 0 <= lt < dura:
            u = out_back(seg(lt, 0.0, 0.3)) * (1 - ease(seg(lt, dura - 0.2, dura)))
            lado = 1 if i % 2 else -1  # alterna esquerda / direita (o rosto dele fica livre)
            x = W / 2 + lado * 250
            cola(img, caixa(nome, 380), x, 1150, rot=lado * 5, sc=u)
            cola(img, pilula(tag, 48, cor), x, 1360, rot=-lado * 3, sc=u)
            cola(img, ficha(JOGOS[nome][1]), x, 1420, sc=u)
            return True
    return False


def selo(img, t):
    for i, (tv, _s, _ts, txt, cor) in enumerate(SELO_T):
        lt = t - tv
        if 0 <= lt < 2.6:
            u = out_back(seg(lt, 0.0, 0.3)) * (1 - ease(seg(lt, 2.4, 2.6)))
            cola(img, pilula(txt, 62, cor), W / 2, 330 if txt.startswith(("LINHA", "NOSSO")) else 1220,
                 rot=3 if i % 2 else -3, sc=u)


def overlay(t):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if t >= M["fim"]:
        tela_final(img, t - M["fim"])
        return img
    img.alpha_composite(logo_card(150), (W - 186, 46))
    if t < M["fala"]:  # gancho: "3 JOGOS POR R$ 15?!" do peito para baixo (o rosto fica livre)
        cola(img, titulo("3 JOGOS\nPOR R$ 15?!", 150), W / 2, 1180, rot=-3, sc=out_back(seg(t, 0.05, 0.4)))
        cola(img, pilula("NO NOSSO SITE", 64, PETROLEO), W / 2 + 90, 1430, rot=3, sc=out_back(seg(t, 2.4, 2.75)))
        return img
    if t < M["comenta"]:
        if not fileira(img, t):
            cartao(img, t)
        selo(img, t)
        legenda(img, t)
        return img
    lt = t - M["comenta"]
    cola(img, titulo("QUAL CAIXINHA\nVOCÊ LEVARIA?", 112), W / 2, 700, rot=-2, sc=out_back(seg(lt, 0.0, 0.35)))
    for j, (num, nomes) in enumerate(CAIXAS):
        u = out_back(seg(lt, 0.4 + j * 0.15, 0.7 + j * 0.15))
        cola(img, trio(tuple(nomes), 190), 185 + j * 355, 1080, sc=u)
        cola(img, pilula(num, 50, AMARELO, INK), 185 + j * 355, 1235, sc=u)
    cola(img, pilula("Comenta aqui!", 72, ROSA), W / 2, 1420, rot=3, sc=out_back(seg(lt, 1.1, 1.45)))
    return img


@lru_cache(None)
def trio(nomes, h):
    """As 3 caixas da caixinha em leque (como vêm juntas)."""
    ims = [caixa(n, h).rotate(r, expand=True, resample=Image.BICUBIC) for n, r in zip(nomes, (9, 0, -9))]
    wt = int(ims[0].width * 2.1)
    out = Image.new("RGBA", (wt, max(i.height for i in ims) + 20), (0, 0, 0, 0))
    for j in (0, 2, 1):
        im = ims[j]
        out.alpha_composite(im, (int(j * ims[0].width * 0.55), (out.height - im.height) // 2 + (0 if j == 1 else 14)))
    return out


def tela_final(img, lt):
    cola(img, logo_card(400), W / 2, 290, sc=out_back(seg(lt, 0.0, 0.4)))
    for j, (num, nomes) in enumerate(CAIXAS):
        u = out_back(seg(lt, 0.15 + j * 0.12, 0.5 + j * 0.12))
        cola(img, trio(tuple(nomes), 200), 185 + j * 355, 720, sc=u)
        cola(img, pilula(num, 46, AMARELO, INK), 185 + j * 355, 880, sc=u)
    v = ease(seg(lt, 0.6, 1.0))
    linhas = [("ALUGUE A LINHA MICRO", "lilita", 80, AMARELO), ("3 jogos em cada caixinha · R$ 15", "figtree", 50, WHITE),
              ("RESERVE ONLINE · RETIRE EM MAUÁ\nOU RECEBA EM CASA", "figtree", 44, WHITE),
              ("LINK NA BIO · @SUAVEZ_BG", "lilita", 60, WHITE)]
    for j, (txt, f, s, cor) in enumerate(linhas):
        cola(img, texto(txt, f, s, cor, INK, 6 if f == "lilita" else 0, 5 if f == "lilita" else 3, INK, entre=1.2),
             W / 2, 1060 + j * 130 + (30 if j >= 2 else 0) + (40 if j == 3 else 0), alpha=v)


# ---------------------------------------------------------------- vídeo
def ler(src, a, n):
    p = subprocess.Popen([ffmpeg(), "-loglevel", "error", "-ss", f"{a:.3f}", "-i", os.path.join(BR, ARQ[src] + ".mp4"),
                          "-frames:v", str(n), "-vf", f"setpts=PTS/{VEL},fps={FPS},scale={W}:{H},{GRADE}", "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
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


def escala(fr, s, cy=0.35):
    if s <= 1.001:
        return fr
    import cv2
    w, h = W / s, H / s
    x0, y0 = (W - w) / 2, min(max(0.0, cy * H - h / 2), H - h)
    M_ = np.float32([[s, 0, -x0 * s], [0, s, -y0 * s]])
    return cv2.warpAffine(fr, M_, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


def quadros():
    ultimo = None
    for i, p in enumerate(TL):
        punch = 1.08 if i % 2 else 1.0  # corte seco alternando aberto / fechado (ancorado no rosto)
        for fr in ler(p["src"], p["a"], p["n"]):
            ultimo = fr
            yield escala(fr, punch)
    base = Image.fromarray(ultimo).filter(ImageFilter.GaussianBlur(22))
    escuro = np.asarray(Image.blend(base, Image.new("RGB", (W, H), (20, 60, 76)), 0.6))
    n = round(COMENTA * FPS)
    for k in range(n):
        yield escala(escuro, 1.0 + 0.05 * k / n)
    fundo = np.asarray(Image.blend(base, Image.new("RGB", (W, H), (20, 60, 76)), 0.72))
    for _ in range(round(FIM * FPS) + 2):
        yield fundo


# ---------------------------------------------------------------- áudio
def ler_audio(src, a, d):
    r = subprocess.run([ffmpeg(), "-loglevel", "error", "-ss", f"{a:.3f}", "-t", f"{d * VEL + 0.05:.4f}", "-i",
                        os.path.join(BR, ARQ[src] + ".mp4"), "-vn", "-ac", "1", "-ar", "44100", "-af",
                        VOZ + f",atempo={VEL}", "-f", "s16le", "-"], capture_output=True)
    x = np.frombuffer(r.stdout, np.int16).astype(np.float64) / 32768
    n = int(round(d * 44100))
    return np.pad(x, (0, max(0, n - len(x))))[:n]


def cues():
    c = [(0.0, "pop", 0.45), (0.25, "whoosh", 0.3)]
    for t0, _t1, _k, acende in FIL_T:
        c += [(t0, "whoosh", 0.4)] + [(x, "pop", 0.35) for x in acende]
    c += [(x[0], "pop", 0.4) for x in CART_T] + [(x[0], "ding", 0.3) for x in SELO_T]
    c += [(M["comenta"], "whoosh", 0.4), (M["comenta"] + 1.1, "pop", 0.5), (M["fim"], "whoosh", 0.4),
          (M["fim"] + 0.5, "chime", 0.5)]
    return c


def audio(path):
    sr = 44100
    pecas = [(p, ler_audio(p["src"], p["a"], p["n"] / FPS)) for p in TL]
    q = int(0.03 * sr)
    voz = np.zeros(int(DUR * sr) + sr)
    for src in ARQ:  # ganho fixo por arquivo (mesmo nível de fala nos 3 stories)
        xs = [x for p, x in pecas if p["src"] == src]
        tudo = np.concatenate(xs)
        e = np.sqrt(np.convolve(tudo ** 2, np.ones(q) / q, "same"))
        g = 10 ** (-20 / 20) / (np.sqrt((tudo[e > e.max() * 0.12] ** 2).mean()) + 1e-9)
        for p, x in pecas:
            if p["src"] != src:
                continue
            x = x * g
            f = int(0.015 * sr)
            x[:f] *= np.linspace(0, 1, f)
            x[-f:] *= np.linspace(1, 0, f)
            i = int(round(p["t0"] * sr))
            voz[i:i + len(x)] += x
    vp = os.path.join(OUT, "micro_voz.wav")
    with wave.open(vp, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.clip(voz, -1, 1) * 32767).astype(np.int16).tobytes())
    som.build(path, DUR, cues(), musica="travessa", voz=[(vp, 0.0)], fx_ganho=0.35, duck=0.55, musica_ganho=0.24,
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


def render(saida, wav):
    p = subprocess.Popen([ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-framerate", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-crf", "19", "-preset", "medium",
                          "-tune", "film", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags",
                          "+faststart", saida], stdin=subprocess.PIPE)
    for n, fr in enumerate(quadros()):
        t = n / FPS
        if t >= DUR:
            break
        im = Image.fromarray(fr).convert("RGBA")
        im.alpha_composite(overlay(t))
        p.stdin.write(im.convert("RGB").tobytes())
    p.stdin.close()
    p.wait()


def chat(src, dst):
    """2 passadas para caber nos 30 MB do chat."""
    kbps = int(28 * 8 * 1024 / DUR) - 200
    base = os.path.join(OUT, "micro_2pass")
    for k in (1, 2):
        subprocess.run([ffmpeg(), "-v", "error", "-y", "-i", src, "-c:v", "libx264", "-preset", "slow", "-tune", "film",
                        "-b:v", f"{kbps}k", "-pass", str(k), "-passlogfile", base, "-pix_fmt", "yuv420p"]
                       + (["-an", "-f", "null", "/dev/null"] if k == 1 else ["-c:a", "copy", "-movflags", "+faststart", dst]),
                       check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    ap.add_argument("--info", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    print(f"duração {DUR:.1f} s", {k: round(v, 1) for k, v in M.items()})
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
                im.alpha_composite(overlay(n / FPS))
                ims[n] = im.convert("RGB")
            if len(ims) == len(alvo):
                break
        folha([ims[k] for k in sorted(ims)], os.path.join(OUT, "frames_micro.jpg"))
        return
    wav = os.path.join(OUT, "micro.wav")
    audio(wav)
    render(os.path.join(OUT, "micro.mp4"), wav)
    chat(os.path.join(OUT, "micro.mp4"), os.path.join(OUT, "micro_chat.mp4"))
    print("ok")


if __name__ == "__main__":
    main()
