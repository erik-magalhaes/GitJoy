#!/usr/bin/env python3
"""Reels "TAKE TIME EM 1 MINUTO OU MENOS" (18/out/2026). Ele gravou 5 vídeos de story (brutos fora do git em
brutos/out18/; os arquivos 153426 e 153528 são cópias de 153358 e 153455): o gancho no espelho, a caixa, as cartas e as
capas, a regra na mesa com o relógio e o fecho ("a gente joga em casal... já está no site").
Conceito: CONTRA O RELÓGIO. Um relógio no estilo do jogo (mostrador lilás, aro dourado, 6 seções) conta 60 s enquanto
ele explica; as regras pipocam em selos na hora em que ele fala; no fim o relógio para e carimba "EXPLICADO!".
Cortes secos pela energia, alternando aberto / punch-in, legenda palavra a palavra.

    python3 taketime.py --info             # linha do tempo
    python3 taketime.py --frame 1 10 40    # out/frames_taketime.jpg
    python3 taketime.py                    # out/taketime.mp4
"""
import argparse
import json
import math
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
from base import texto, foto  # noqa: E402

BR = os.path.join(ROOT, "brutos", "out18")
OUT = os.path.join(ROOT, "out")
ARQ = {"h": "153134", "i": "153358", "c": "153455", "r": "153721", "f": "153841"}
INK, AMARELO, VERMELHO, VERDE = (20, 16, 30), (255, 214, 70), (214, 46, 52), (40, 160, 90)
LILAS, ROXO, OURO = (186, 160, 236), (92, 62, 160), (232, 184, 74)
# gravado em 1080p no celular: mexer pouco (denoise e nitidez fracos, cor quase intocada)
GRADE = "hqdn3d=1.5:1.5:3:3,unsharp=5:5:0.35:5:5:0.0,eq=contrast=1.02:saturation=1.02"
VOZ = "highpass=f=80,afftdn=nr=8:nf=-48,equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1.4:g=1.5"
VEL_EXP = 1.2  # a explicação a 1,2x para caber no "1 minuto ou menos"
# (fonte, início, fim, tipo, velocidade) — tempos no bruto
TRECHOS = [
    ("h", 0.00, 2.95, "gancho", 1.0),    # "Eu vou explicar o Take Time em 1 minuto ou menos." (no espelho)
    ("i", 0.00, 5.40, "exp", VEL_EXP),   # "Take Time é um jogo cooperativo... Vou te mostrar."
    ("c", 0.00, 15.40, "exp", VEL_EXP),  # baralho do sol e da lua, 12 níveis
    ("r", 0.00, 56.50, "exp", VEL_EXP),  # a regra na mesa, até "...a gente segue para o próximo." (fim da explicação)
    ("r", 56.50, 60.05, "casal", VEL_EXP),  # "Dentro de cada capa tem 4 relógios e no total são 12 capas." (já é o fecho)
    ("f", 0.00, 10.70, "casal", VEL_EXP),   # "a gente gosta de jogar muito em casal... um nível que estava difícil."
    ("f", 13.30, 16.70, "casal", VEL_EXP),  # (sem o "E... claro," hesitado) "ele já está disponível no nosso site... corre lá!"
]
CORRIGE = {("h", 1.1): "Take", ("h", 1.2): "Time", ("r", 12.7): "seções.", ("r", 14.2): "seções."}
# selos das regras: (fonte, início da palavra no bruto, texto, cor)
SELOS = [
    ("i", 1.28, "JOGO COOPERATIVO", VERDE),
    ("c", 2.46, "CARTAS DO SOL E DA LUA", ROXO),
    ("c", 9.68, "12 NÍVEIS", (28, 124, 150)),
    ("r", 8.16, "ORDEM CRESCENTE", ROXO),
    ("r", 11.50, "NO MÁXIMO 24 POR SEÇÃO", VERMELHO),
    ("r", 13.90, "6 SEÇÕES", (28, 124, 150)),
    ("r", 20.58, "SEM COMUNICAÇÃO!", VERMELHO),
    ("r", 37.42, "CARTA VIRADA PRA BAIXO", ROXO),
    ("r", 43.52, "EXATAMENTE 3 CARTAS", (28, 124, 150)),
    ("r", 55.26, "PRÓXIMO RELÓGIO!", VERDE),
    ("r", 57.78, "4 RELÓGIOS EM CADA CAPA", ROXO),
    ("f", 2.42, "PERFEITO PRA CASAL", (219, 39, 119)),
    ("f", 14.38, "JÁ NO SITE · LINK NA BIO", VERDE),
]
GAP, PAD = 0.32, 0.1
FRASE_FINAL = 56.5  # "Dentro de cada capa...": o bruto acaba colado no "capas" (limite do story)
RESPIRO, CARIMBO = 0.9, 0.15  # pausa depois do "próximo" (o relógio para) e o carimbo entra 0,15 s depois
# o story parou de gravar (60 s) no "capa", antes do "s" (medido: nada agudo depois de 59,92 s). O "s" que falta é o do
# "cartas." dele mesmo (44,74–44,98 s do mesmo arquivo), emendado logo depois do "capa".
FIM_CAPA, S_DE_CARTAS = 59.92, (44.76, 44.92)
COMENTA, FIM = 3.6, 3.8


# ---------------------------------------------------------------- cortes pela energia
@lru_cache(None)
def energia(src):
    w = wave.open(os.path.join(BR, ARQ[src] + ".wav"))
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
    q = int(0.02 * w.getframerate())
    n = len(x) // q
    return 20 * np.log10(np.sqrt((x[:n * q].reshape(n, q) ** 2).mean(1)) + 1e-9)


@lru_cache(None)
def todas_palavras():
    return json.load(open(os.path.join(BR, "palavras.json"), encoding="utf-8"))


def palavras(src):
    return [w for w in todas_palavras()[ARQ[src] + ".mp4"] if src != "h" or w["s"] < 10]


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
    for j, (src, a, b, tipo, vel) in enumerate(TRECHOS):
        marcas.setdefault(tipo, t)
        for ta, tb in pedacos(src, a, b):
            n = nq(t, (tb - ta) / vel)
            tl.append(dict(t0=t, n=n, nv=n, src=src, a=ta, j=j, tipo=tipo, vel=vel))  # nv = quadros com voz
            t += n / FPS
        if tipo == "exp" and j == 3:
            marcas["fim_exp"] = t
            tl[-1]["n"] += nq(t, RESPIRO)  # a mesa continua (o vídeo segue rodando) enquanto o carimbo entra
            t += nq(t, RESPIRO) / FPS
    marcas["comenta"] = t
    marcas["fim"] = t + COMENTA
    return tl, marcas, t + COMENTA + FIM


TL, M, DUR = linha()


def no_video(src, ts):
    """Tempo no vídeo de um instante ts do bruto (None se caiu num corte)."""
    for p in TL:
        if p["src"] == src and p["a"] <= ts < p["a"] + p["nv"] / FPS * p["vel"]:
            return p["t0"] + (ts - p["a"]) / p["vel"]
    return None


# ---------------------------------------------------------------- legenda palavra a palavra
def subs():
    pal = []
    for p in TL:
        a, b = p["a"], p["a"] + p["nv"] / FPS * p["vel"]
        for w in palavras(p["src"]):
            if a <= (w["s"] + w["e"]) / 2 < b:
                txt = CORRIGE.get((p["src"], round(w["s"], 1)), w["w"].strip())
                if txt:
                    pal.append((txt, p["t0"] + max(0.0, w["s"] - a) / p["vel"], p["t0"] + (min(b, w["e"]) - a) / p["vel"]))
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
    return letreiro(txt.upper(), 76, AMARELO if amarela else WHITE, INK, 11, "Poppins-Black.ttf")


def legenda(img, t, y0=1470):
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
            y = y0 - (len(linhas) - 1) * 95
            for ln in linhas:
                lw = sum(x.width - 22 for x in ln) + gap * (len(ln) - 1)
                x = 540 - lw / 2
                for im in ln:
                    cola(img, im, x + (im.width - 22) / 2, y, 0, sc)
                    x += im.width - 22 + gap
                y += 95
            return


# ---------------------------------------------------------------- relógio (no estilo do mostrador do jogo)
RAIO = 120


@lru_cache(None)
def mostrador():
    s = 2 * RAIO + 40
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = s / 2
    d.ellipse((c - RAIO - 10, c - RAIO - 4, c + RAIO + 10, c + RAIO + 16), fill=(0, 0, 0, 90))  # sombra
    d.ellipse((c - RAIO, c - RAIO, c + RAIO, c + RAIO), fill=(236, 240, 250), outline=INK, width=7)  # aro claro
    r2 = RAIO - 20
    face = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    fd = ImageDraw.Draw(face)
    for k in range(r2, 0, -2):  # degradê lilás → roxo, como o relógio do jogo
        u = k / r2
        cor = tuple(int(ROXO[i] + (LILAS[i] - ROXO[i]) * (1 - u) ** 0.8) for i in range(3))
        fd.ellipse((c - k, c - k, c + k, c + k), fill=cor + (255,))
    im.alpha_composite(face)
    d.ellipse((c - r2, c - r2, c + r2, c + r2), outline=OURO, width=6)
    for k in range(6):  # as 6 seções
        a = math.radians(k * 60 - 90)
        d.line((c + math.cos(a) * (r2 - 2), c + math.sin(a) * (r2 - 2), c + math.cos(a) * (RAIO - 3),
                c + math.sin(a) * (RAIO - 3)), fill=OURO, width=6)
    return im


def relogio(img, t, x, y, sc=1.0):
    """Conta de 60 s a 0 durante a explicação; para no fim dela."""
    t0, t1 = M["exp"], M["fim_exp"]
    usado = min(max(0.0, t - t0), t1 - t0)
    resta = max(0.0, 60 - usado)
    im = mostrador().copy()
    d = ImageDraw.Draw(im)
    c = im.width / 2
    r2 = RAIO - 26
    if usado > 0:  # o tempo que já passou escurece o mostrador (sombra que gira)
        sb = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sb).pieslice((c - r2, c - r2, c + r2, c + r2), -90, -90 + 360 * usado / 60, fill=(16, 10, 40, 165))
        im.alpha_composite(sb)
    a = math.radians(-90 + 360 * usado / 60)
    d.line((c, c, c + math.cos(a) * (r2 - 6), c + math.sin(a) * (r2 - 6)), fill=(255, 236, 170), width=9)
    d.ellipse((c - 14, c - 14, c + 14, c + 14), fill=OURO, outline=INK, width=4)
    urgente = resta < 10.5 and t < t1
    pulso = 1.0 + (0.06 * max(0.0, math.cos((t - t0) * 2 * math.pi)) if urgente else 0.0)
    cola(img, im, x, y, sc=sc * pulso)
    cor = (255, 110, 110) if urgente else WHITE
    s_ = int(math.ceil(resta - 1e-6)) if t < t1 else int(round(resta))
    cola(img, digital(f"0:{s_:02d}" if s_ < 60 else "1:00", cor), x, y + (RAIO + 44) * sc, sc=sc)


@lru_cache(None)
def digital(txt, cor):
    return texto(txt, "lilita", 66, cor, INK, 6, 5, INK)


# ---------------------------------------------------------------- textos
@lru_cache(None)
def pilula(txt, s, cor, fg=WHITE):
    tx = texto(txt, "lilita", s, fg)
    im = Image.new("RGBA", (tx.width + 44, tx.height + 10), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=im.height // 2, fill=cor,
                                          outline=INK, width=6)
    im.alpha_composite(tx, (22, 5))
    return im


def selos_tempos():
    out = []
    for src, ts, txt, cor in SELOS:
        tv = no_video(src, ts)
        if tv is None:  # palavra caiu na borda de um corte: usa o próximo pedaço
            tv = min(p["t0"] for p in TL if p["src"] == src and p["a"] >= ts)
        out.append((tv, txt, cor))
    return out


SELOS_T = selos_tempos()


@lru_cache(None)
def gancho_img():
    return texto("TAKE TIME\nEM 1 MINUTO", "lilita", 112, WHITE, INK, 9, 8, INK, entre=1.02)


@lru_cache(None)
def carimbo(seg_):
    tx = texto(f"EXPLICADO\nEM {seg_} SEGUNDOS!", "lilita", 88, WHITE, INK, 8, 7, INK, entre=1.05)
    im = Image.new("RGBA", (tx.width + 70, tx.height + 50), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=34, fill=VERDE, outline=INK, width=9)
    im.alpha_composite(tx, (35, 25))
    return im


def overlay(t):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if t >= M["fim"]:
        tela_final(img, t - M["fim"])
        return img
    img.alpha_composite(logo_card(150), (W - 186, 46))
    if t < M["exp"]:  # gancho: o relógio já aparece parado em 1:00 (o rosto dele fica livre, em cima)
        cola(img, gancho_img(), W / 2, 1120, rot=-2, sc=out_back(seg(t, 0.05, 0.45)))
        cola(img, pilula("(OU MENOS!)", 58, VERMELHO), W / 2 + 130, 1290, rot=4, sc=out_back(seg(t, 1.9, 2.3)))
        relogio(img, t, 175, 205, sc=out_back(seg(t, 0.2, 0.6)))
        return img  # sem legenda no gancho: o letreiro já diz a frase
    elif t < M["comenta"]:
        fim = M["fim_exp"]
        # o relógio fica até o fim da explicação + o carimbo, depois sai voando para cima
        sai = ease(seg(t, fim + CARIMBO + 2.2, fim + CARIMBO + 2.6))
        if sai < 1:
            relogio(img, t, 175, 205 - 420 * sai)
        if fim <= t < fim + CARIMBO + 2.6:
            lt = t - fim - CARIMBO
            seg_ = int(fim - M["exp"])
            cola(img, carimbo(seg_), W / 2, 760, rot=-4, sc=out_back(seg(lt, 0.0, 0.35)) * (1 - ease(seg(lt, 2.2, 2.6))))
        ativos = [s for s in SELOS_T if s[0] <= t]
        if ativos:
            t0, txt, cor = ativos[-1]
            prox = [s[0] for s in SELOS_T if s[0] > t0]
            dura = min(2.8, (prox[0] - t0) if prox else 2.8)
            lt = t - t0
            if lt < dura and not (fim <= t < fim + CARIMBO + 2.6):
                u = out_back(seg(lt, 0.0, 0.3)) * (1 - ease(seg(lt, dura - 0.2, dura)))
                cola(img, pilula(txt, 60, cor), W / 2 + 60, 470, rot=-3 if len(prox) % 2 else 3, sc=u)
    else:
        lt = t - M["comenta"]
        cola(img, texto("JOGO COOPERATIVO:\nUNE OU SEPARA\nO CASAL?", "lilita", 96, WHITE, INK, 9, 8, INK, entre=1.05),
             W / 2, 820, rot=-2, sc=out_back(seg(lt, 0.0, 0.4)))
        cola(img, pilula("Comenta aqui!", 70, (219, 39, 119)), W / 2, 1150, rot=3, sc=out_back(seg(lt, 0.4, 0.75)))
        return img
    legenda(img, t)
    return img


def tela_final(img, lt):
    cola(img, logo_card(420), W / 2, 300, sc=out_back(seg(lt, 0.0, 0.4)))
    cola(img, foto("take_time", 600, borda=12, raio=26, sombra_a=0.5), W / 2, 790, rot=-2,
         sc=out_back(seg(lt, 0.15, 0.5)))
    v = ease(seg(lt, 0.5, 0.9))
    linhas = [("ALUGUE O TAKE TIME", "lilita", 76, AMARELO), ("2 a 4 jogadores · 30 min · 5 dias de jogo", "figtree", 46, WHITE),
              ("RESERVE ONLINE · RETIRE EM MAUÁ\nOU RECEBA EM CASA", "figtree", 44, WHITE),
              ("LINK NA BIO · @SUAVEZ_BG", "lilita", 58, WHITE)]
    for j, (txt, f, s, cor) in enumerate(linhas):
        cola(img, texto(txt, f, s, cor, INK, 6 if f == "lilita" else 0, 5 if f == "lilita" else 3, INK, entre=1.2),
             W / 2, 1170 + j * 135 + (30 if j >= 2 else 0), alpha=v)


# ---------------------------------------------------------------- vídeo
def ler(src, a, n, vel):
    p = subprocess.Popen([ffmpeg(), "-loglevel", "error", "-ss", f"{a:.3f}", "-i", os.path.join(BR, ARQ[src] + ".mp4"),
                          "-frames:v", str(n), "-vf", f"setpts=PTS/{vel},fps={FPS},scale={W}:{H},{GRADE}", "-f", "rawvideo",
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


def escala(fr, s, cy=0.45):
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
        punch = 1.08 if i % 2 else 1.0  # corte seco alternando aberto / fechado
        cy = 0.3 if p["src"] == "h" else 0.45  # no espelho, o punch-in ancora no rosto
        for fr in ler(p["src"], p["a"], p["n"], p["vel"]):
            ultimo = fr
            yield escala(fr, punch, cy)
    # "comenta" e tela final: a última cena desfocada, aproximando devagar
    base = Image.fromarray(ultimo).filter(ImageFilter.GaussianBlur(20))
    escuro = np.asarray(Image.blend(base, Image.new("RGB", (W, H), (34, 20, 60)), 0.55))
    n = round(COMENTA * FPS)
    for k in range(n):
        yield escala(escuro, 1.0 + 0.05 * k / n)
    fundo = np.asarray(Image.blend(base, Image.new("RGB", (W, H), (34, 20, 60)), 0.7))
    for _ in range(round(FIM * FPS) + 2):
        yield fundo


# ---------------------------------------------------------------- áudio
def ler_audio(src, a, d, vel):
    """d = duração na SAÍDA; lê d·vel do bruto e acelera com atempo (tom preservado)."""
    af = VOZ + (f",atempo={vel}" if abs(vel - 1) > 1e-3 else "")
    r = subprocess.run([ffmpeg(), "-loglevel", "error", "-ss", f"{a:.3f}", "-t", f"{d * vel + 0.05:.4f}", "-i",
                        os.path.join(BR, ARQ[src] + ".mp4"), "-vn", "-ac", "1", "-ar", "44100", "-af", af, "-f", "s16le",
                        "-"], capture_output=True)
    x = np.frombuffer(r.stdout, np.int16).astype(np.float64) / 32768
    n = int(round(d * 44100))
    return np.pad(x, (0, max(0, n - len(x))))[:n]


def cues():
    c = [(0.0, "pop", 0.4), (0.3, "whoosh", 0.3), (M["exp"], "relogio", 0.5)]
    for k in range(1, int(M["fim_exp"] - M["exp"]) + 1):  # tique-taque baixinho a cada segundo; mais forte no fim
        tk = M["exp"] + k
        if tk < M["fim_exp"]:
            c.append((tk, "tick", 0.16 if 60 - k > 10 else 0.32))
    for tv, _txt, _c in SELOS_T:
        c.append((tv, "pop", 0.35))
    c += [(M["fim_exp"] + CARIMBO, "ding", 0.6), (M["fim_exp"] + CARIMBO + 0.05, "carimbo", 0.5),
          (M["fim_exp"] + CARIMBO + 0.3, "plateia", 0.35),
          (M["comenta"], "whoosh", 0.4), (M["comenta"] + 0.4, "pop", 0.5), (M["fim"], "whoosh", 0.4),
          (M["fim"] + 0.5, "chime", 0.5)]
    return c


def audio(path):
    sr = 44100
    def voz_peca(p):  # na pausa (n > nv) a imagem segue e a voz fica em silêncio
        x = ler_audio(p["src"], p["a"], p["nv"] / FPS, p["vel"])
        f = int(0.015 * sr)
        x[-f:] *= np.linspace(1, 0, f)
        return np.pad(x, (0, int(round(p["n"] / FPS * sr)) - len(x)))
    pecas = [(p, voz_peca(p)) for p in TL]
    tudo = np.concatenate([x for _, x in pecas])
    q = int(0.03 * sr)
    voz = np.zeros(int(DUR * sr) + sr)
    for src in ARQ:  # ganho fixo por arquivo (mesmo nível de fala em todos)
        xs = [x for p, x in pecas if p["src"] == src]
        if not xs:
            continue
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
            if p["src"] == "r" and p["a"] >= FRASE_FINAL:  # "capa" + o "s" do "cartas."
                k = int(round((FIM_CAPA - p["a"]) / p["vel"] * sr))
                fd = int(0.03 * sr)
                x[k:k + fd] *= np.linspace(1, 0, fd)
                x[k + fd:] = 0
                ss = ler_audio("r", S_DE_CARTAS[0], S_DE_CARTAS[1] - S_DE_CARTAS[0], 1.0) * g * 10 ** (-8 / 20)  # ganho do arquivo, −8 dB (discreto)
                ss[:int(0.02 * sr)] *= np.linspace(0, 1, int(0.02 * sr))
                ss[-int(0.05 * sr):] *= np.linspace(1, 0, int(0.05 * sr))
                x[k:k + len(ss)] += ss[:len(x) - k]
            i = int(round(p["t0"] * sr))
            voz[i:i + len(x)] += x
    vp = os.path.join(OUT, "taketime_voz.wav")
    with wave.open(vp, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.clip(voz, -1, 1) * 32767).astype(np.int16).tobytes())
    som.build(path, DUR, cues(), musica="gameshow", voz=[(vp, 0.0)], fx_ganho=0.35, duck=0.55, musica_ganho=0.22,
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
    print("ok", saida, os.path.getsize(saida) // 1024 ** 2, "MB", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    ap.add_argument("--info", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    print(f"duração {DUR:.1f} s", {k: round(v, 1) for k, v in M.items()},
          f"explicação {M['fim_exp'] - M['exp']:.1f} s")
    if a.info:
        for p in TL:
            print(f"{p['t0']:6.2f} {p['n'] / FPS:5.2f} {p['src']} {p['a']:.2f}")
        for s in SELOS_T:
            print(f"selo {s[0]:6.2f} {s[1]}")
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
        folha([ims[k] for k in sorted(ims)], os.path.join(OUT, "frames_taketime.jpg"))
        return
    wav = os.path.join(OUT, "taketime.wav")
    audio(wav)
    render(os.path.join(OUT, "taketime.mp4"), wav)


if __name__ == "__main__":
    main()
