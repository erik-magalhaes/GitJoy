#!/usr/bin/env python3
"""Reels "PILOTAR UM AVIÃO EM 1 MINUTO OU MENOS" — Sky Team (1/nov/2026). Ele gravou 7 vídeos (brutos fora do git em
brutos/nov01/): o gancho com a caixa na câmera da frente (ESPELHADO → hflip), o jogo na mesa e o fecho ("ótimo jogo
para casal"). Base: taketime.py (mesma edição contra o relógio), com cara de AVIAÇÃO: um PAINEL DE APROXIMAÇÃO no alto
(o avião ✈️ vai até a pista enquanto o cronômetro desce de 1:00), selos das regras na hora da fala e, no pouso, o
carimbo "POUSOU EM XX SEGUNDOS!" com palmas (as palmas de quando o avião pousa). No site: "Sky Team (em inglês)",
Família R$ 30, 2 jogadores, 20 min. Caixa = foto do site recortada (assets/sky/sky_team.png).

    python3 skyteam.py --info
    python3 skyteam.py --frame 1 10 40
    python3 skyteam.py                    # out/skyteam.mp4
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
from motor import W, H, FPS, WHITE, ease, seg, out_back, logo_card, cola, letreiro, folha, ffmpeg, emoji, sombra  # noqa: E402
import som  # noqa: E402
from base import texto, foto  # noqa: E402

BR = os.path.join(ROOT, "brutos", "nov01")
OUT = os.path.join(ROOT, "out")
ARQ = {"h": "084557", "a": "084743", "b": "085035", "c": "085111", "d": "085317", "e": "085359", "f": "085509"}
INK, AMARELO, VERMELHO, VERDE = (20, 16, 30), (255, 214, 70), (214, 46, 52), (40, 160, 90)
LILAS, ROXO, OURO = (186, 160, 236), (92, 62, 160), (232, 184, 74)
CEU, NAVY, LARANJA = (28, 124, 190), (16, 30, 58), (244, 136, 37)
# gravado em 1080p no celular: mexer pouco (denoise e nitidez fracos, cor quase intocada)
GRADE = "hqdn3d=1.5:1.5:3:3,unsharp=5:5:0.35:5:5:0.0,eq=contrast=1.02:saturation=1.02"
VOZ = "highpass=f=80,afftdn=nr=8:nf=-48,equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1.4:g=1.5"
VEL_EXP = 1.1  # a explicação a 1,1x (já cabe folgado no "1 minuto ou menos")
# (fonte, início, fim, tipo, velocidade) — tempos no bruto
TRECHOS = [
    ("h", 0.00, 3.25, "gancho", 1.0),     # "...em um minuto ou menos." (o bruto acaba a 3,0 s, no começo do "s": 0,25 s de quadro parado)
    ("a", 0.00, 10.90, "exp", VEL_EXP),   # "Esse aqui é o Sky Team, um jogo cooperativo... antes que as rodadas acabem."
    ("b", 0.00, 5.04, "exp", VEL_EXP),    # dados → ações no tabuleiro
    ("c", 0.40, 19.16, "exp", VEL_EXP),   # eixo + motor obrigatórios; a soma dos dados anda 0, 1 ou 2
    ("d", 0.00, 5.10, "exp", VEL_EXP),    # tirar os aviões do caminho
    ("d", 5.10, 9.70, "exp", VEL_EXP),    # INTEIRO: "taca o dedo na buzina! Biii! / Ué, avião tem buzina? (a voz de fora) / Não."
    ("e", 0.00, 12.61, "exp", VEL_EXP),   # pouso: trem de pouso, flaps, freio e o cafezinho (fim da explicação)
    ("f", 0.00, 16.10, "casal", VEL_EXP), # "Essa aqui é só a fase do tutorial... ótimo jogo para casal ou... sempre quis voar."
]
FIM_EXP_J = 6
INTEIRO = {("d", 5.10)}  # trechos sem corte interno (a pergunta de quem está fora da câmera é baixa e o corte por energia comia)
# o celular parou de gravar no começo do "s" de "menos" (medido: o chiado agudo só começa a 2,97 s, no último quadro).
# O "s" que falta vem do "pessoas" dele mesmo (3,61–3,78 s do 084743), emendado ali, com o ganho daquele arquivo.
FIM_MENOS, S_DE_PESSOAS = 2.965, ("a", 3.61, 3.78)
REFORCO = [("d", 7.55, 9.05, 9.0)]  # (fonte, de, até, dB): a voz de fora da câmera ~12 dB mais baixa  # o pouso (fim da explicação) é depois do trecho "e"
# Whisper (small e medium) ouviu "flares": no Sky Team são os FLAPS
CORRIGE = {("a", 1.1): "Sky Team,", ("a", 5.6): "copiloto", ("a", 5.7): "", ("d", 6.7): "BIII,", ("d", 7.1): "BIII!", ("e", 5.2): "flaps",
           ("e", 5.5): "precisam estar", ("e", 11.8): "necessário."}
# selos das regras: (fonte, início da palavra no bruto, texto, cor)
SELOS = [
    ("a", 2.04, "COOPERATIVO · 2 JOGADORES", VERDE),
    ("a", 4.50, "PILOTO × COPILOTO", CEU),
    ("a", 8.64, "CHEGUE AO AEROPORTO!", LARANJA),
    ("b", 1.90, "CADA DADO = UMA AÇÃO", ROXO),
    ("c", 2.36, "OBRIGATÓRIO: EIXO + MOTOR", VERMELHO),
    ("c", 6.18, "EIXO: O AVIÃO PODE VIRAR", CEU),
    ("c", 12.82, "SOMA DOS DADOS = VELOCIDADE", LARANJA),
    ("d", 1.16, "TIRE OS AVIÕES DO CAMINHO", VERMELHO),
    ("d", 6.14, "(NO JOGO É O RÁDIO!)", ROXO),
    ("e", 2.78, "TREM DE POUSO", CEU),
    ("e", 5.18, "FLAPS", VERDE),
    ("e", 9.18, "FREIOS", VERMELHO),
    ("e", 11.12, "CAFÉ = AJUSTA O DADO", LARANJA),
    ("f", 1.62, "ISSO É SÓ O TUTORIAL!", ROXO),
    ("f", 8.36, "+ COMBUSTÍVEL E MUITO MAIS", LARANJA),
    ("f", 13.22, "PERFEITO PRA CASAL", (219, 39, 119)),
]
GAP, PAD = 0.32, 0.1
RESPIRO, CARIMBO = 0.9, 0.15  # pausa depois do pouso (o cronômetro para) e o carimbo entra 0,15 s depois
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
    return todas_palavras()[ARQ[src] + ".mp4"]


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
        for ta, tb in ([(a, b)] if tipo == "gancho" or (src, a) in INTEIRO else pedacos(src, a, b)):  # o gancho vai inteiro
            n = nq(t, (tb - ta) / vel)
            tl.append(dict(t0=t, n=n, nv=n, src=src, a=ta, j=j, tipo=tipo, vel=vel))  # nv = quadros com voz
            t += n / FPS
        if tipo == "exp" and j == FIM_EXP_J:
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


# ---------------------------------------------------------------- painel de aproximação (o "relógio" deste vídeo)
PW, PH = 500, 190


@lru_cache(None)
def painel_base():
    im = Image.new("RGBA", (PW + 20, PH + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 12, PW + 8, PH + 12), radius=30, fill=(0, 0, 0, 110))  # sombra
    d.rounded_rectangle((0, 0, PW, PH), radius=30, fill=NAVY, outline=INK, width=7)
    d.rounded_rectangle((12, 12, PW - 12, PH - 12), radius=20, outline=(60, 110, 160), width=3)
    d.text((34, 44), "POUSO EM", font=__import__("base").fonte("lilita", 34), fill=(150, 200, 240), anchor="lm")
    # pista no fim da trilha
    x0, y0 = PW - 120, 132
    d.rounded_rectangle((x0, y0 - 16, x0 + 96, y0 + 16), radius=5, fill=(70, 76, 88), outline=(200, 210, 220), width=2)
    for k in range(4):
        d.rectangle((x0 + 10 + k * 22, y0 - 2, x0 + 22 + k * 22, y0 + 2), fill=WHITE)
    for k in range(9):  # trilha tracejada até a pista
        x = 40 + k * 36
        d.rounded_rectangle((x, y0 - 3, x + 18, y0 + 3), radius=3, fill=(90, 140, 190))
    return im


@lru_cache(None)
def aviao():
    return emoji("\u2708\ufe0f", 64).rotate(-45, expand=True, resample=Image.BICUBIC)  # aponta para a direita


def relogio(img, t, x, y, sc=1.0):
    """Cronômetro de 60 s a 0 durante a explicação; o avião chega na pista exatamente no fim dela (o pouso)."""
    t0, t1 = M["exp"], M["fim_exp"]
    usado = min(max(0.0, t - t0), t1 - t0)
    resta = max(0.0, 60 - usado)
    im = painel_base().copy()
    u = usado / (t1 - t0)
    av = aviao()
    ax = 40 + (PW - 120 + 30 - 40) * ease(u) if u < 1 else PW - 90
    im.alpha_composite(av, (int(ax - av.width / 2), int(132 - av.height / 2 - 2)))
    urgente = resta < 10.5 and t < t1
    cor = (255, 110, 110) if urgente else WHITE
    s_ = int(math.ceil(resta - 1e-6)) if t < t1 else int(round(resta))
    dg = digital(f"0:{s_:02d}" if s_ < 60 else "1:00", cor)
    im.alpha_composite(dg, (int(PW - 34 - dg.width), int(48 - dg.height / 2)))
    cola(img, im, x, y, sc=sc)


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
    return texto("PILOTAR UM AVIÃO\nEM 1 MINUTO", "lilita", 104, WHITE, INK, 9, 8, INK, entre=1.02)


@lru_cache(None)
def carimbo(seg_):
    tx = texto(f"POUSOU EM\n{seg_} SEGUNDOS!", "lilita", 88, WHITE, INK, 8, 7, INK, entre=1.05)
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
        relogio(img, t, 290, 150, sc=out_back(seg(t, 0.2, 0.6)))
        return img  # sem legenda no gancho: o letreiro já diz a frase
    elif t < M["comenta"]:
        fim = M["fim_exp"]
        # o relógio fica até o fim da explicação + o carimbo, depois sai voando para cima
        sai = ease(seg(t, fim + CARIMBO + 2.2, fim + CARIMBO + 2.6))
        if sai < 1:
            relogio(img, t, 290, 150 - 420 * sai)
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
        cola(img, texto("VOCÊ CONFIARIA\nNO SEU PAR PRA\nPOUSAR ESSE AVIÃO?", "lilita", 92, WHITE, INK, 9, 8, INK, entre=1.05),
             W / 2, 820, rot=-2, sc=out_back(seg(lt, 0.0, 0.4)))
        cola(img, pilula("Comenta aqui!", 70, (219, 39, 119)), W / 2, 1150, rot=3, sc=out_back(seg(lt, 0.4, 0.75)))
        return img
    legenda(img, t)
    return img


@lru_cache(None)
def caixa_final():
    im = Image.open(os.path.join(ROOT, "assets", "sky", "sky_team.png")).convert("RGBA")
    im = im.crop(im.getbbox())
    s_ = 600 / im.height
    im = im.resize((int(im.width * s_), 600), Image.LANCZOS)
    sh = sombra(im, 18, (0, 20), 0.5)
    sh.alpha_composite(im, (36, 36))
    return sh


def tela_final(img, lt):
    cola(img, logo_card(420), W / 2, 300, sc=out_back(seg(lt, 0.0, 0.4)))
    cola(img, caixa_final(), W / 2, 800, rot=-3, sc=out_back(seg(lt, 0.15, 0.5)))
    v = ease(seg(lt, 0.5, 0.9))
    linhas = [("ALUGUE O SKY TEAM", "lilita", 76, AMARELO), ("2 jogadores · 20 min · 5 dias de jogo", "figtree", 46, WHITE),
              ("RESERVE ONLINE · RETIRE EM MAUÁ\nOU RECEBA EM CASA", "figtree", 44, WHITE),
              ("LINK NA BIO · @SUAVEZ_BG", "lilita", 58, WHITE)]
    for j, (txt, f, s, cor) in enumerate(linhas):
        cola(img, texto(txt, f, s, cor, INK, 6 if f == "lilita" else 0, 5 if f == "lilita" else 3, INK, entre=1.2),
             W / 2, 1170 + j * 135 + (30 if j >= 2 else 0), alpha=v)


# ---------------------------------------------------------------- vídeo
def ler(src, a, n, vel):
    p = subprocess.Popen([ffmpeg(), "-loglevel", "error", "-ss", f"{a:.3f}", "-i", os.path.join(BR, ARQ[src] + ".mp4"),
                          "-frames:v", str(n), "-vf", f"setpts=PTS/{vel},fps={FPS},scale={W}:{H},{GRADE}" + (",hflip" if src == "h" else ""), "-f", "rawvideo",
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
    c = [(0.0, "pop", 0.4), (0.3, "whoosh", 0.3), (M["exp"], "whoosh", 0.4)]
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
    G = {}
    for src in ARQ:  # ganho fixo por arquivo (mesmo nível de fala em todos)
        xs = [x for p, x in pecas if p["src"] == src]
        if xs:
            tudo = np.concatenate(xs)
            e = np.sqrt(np.convolve(tudo ** 2, np.ones(q) / q, "same"))
            G[src] = 10 ** (-20 / 20) / (np.sqrt((tudo[e > e.max() * 0.12] ** 2).mean()) + 1e-9)
    for src, g in G.items():
        for p, x in pecas:
            if p["src"] != src:
                continue
            x = x * g
            for rs, r0, r1, db in REFORCO:  # trecho de outra voz mais baixa
                if rs == p["src"]:
                    k0 = int(round(max(0.0, (r0 - p["a"]) / p["vel"]) * sr))
                    k1 = int(round(max(0.0, (r1 - p["a"]) / p["vel"]) * sr))
                    x[k0:k1] *= 10 ** (db / 20)
            if p["src"] == "h":  # "meno" + o "s" do "pessoas."
                k = int(round(FIM_MENOS * sr))
                fd = int(0.012 * sr)
                x[k:k + fd] *= np.linspace(1, 0, fd)
                x[k + fd:] = 0
                fs, a0, a1 = S_DE_PESSOAS
                ss = ler_audio(fs, a0, a1 - a0, 1.0) * G[fs]
                ss[:int(0.01 * sr)] *= np.linspace(0, 1, int(0.01 * sr))
                ss[-int(0.06 * sr):] *= np.linspace(1, 0, int(0.06 * sr))
                x[k:k + len(ss)] += ss[:len(x) - k]
            f = int(0.015 * sr)
            x[:f] *= np.linspace(0, 1, f)
            x[-f:] *= np.linspace(1, 0, f)
            i = int(round(p["t0"] * sr))
            voz[i:i + len(x)] += x
    vp = os.path.join(OUT, "skyteam_voz.wav")
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
        folha([ims[k] for k in sorted(ims)], os.path.join(OUT, "frames_skyteam.jpg"))
        return
    wav = os.path.join(OUT, "skyteam.wav")
    audio(wav)
    render(os.path.join(OUT, "skyteam.mp4"), wav)


if __name__ == "__main__":
    main()
