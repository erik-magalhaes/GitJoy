#!/usr/bin/env python3
"""AZUL MINI EM 1 MINUTO OU MENOS — GRAVADO pelo Erik (26/nov, 7 vídeos VID_20261126_07xxxx no Drive de brutos →
brutos/nov26/<hhmmss>.mp4, fora do git; só a mesa, sem rosto). Edição com a CARA DO AZUL (`tema.py`; ele recusou os adesivos fofos aqui): relógio = mostruário
contando, placas creme com moldura azul, azulejos portugueses e as 5 peças nos cantos, legenda palavra a palavra.
Abertura: a Jéssica (075617, espelhada) "Vem comigo aprender Azul Mini em 1 minuto ou menos".
Pedido dele: na parte dos azulejos QUEBRADOS (o chão / pontos negativos) um ASTERISCO explicando que o azulejo quebra
quando não cabe na linha da esquerda (pegou mais do que cabe).
A fala (~100 s) foi enxugada por frases (CORTES, tempos do bruto) + pausas ≤ GAP + fala a VEL para caber em 1 minuto.

    /usr/bin/python3 azul1min.py --info          # texto de cada pedaço e duração
    /usr/bin/python3 azul1min.py --frame 1 10 20 30 40 50 60
    /usr/bin/python3 azul1min.py                 # out/azul1min_{legendado,sem_legenda}_final.mp4
"""
import json
import math
import os
import subprocess
import sys
import wave
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

import azul as A
import tema as T
from azul import K, S, W, H, FPS, BR, TINTA, ROSA, AMAR, MENTA, CEU, PESS, LILAS

ROOT = os.path.dirname(os.path.abspath(__file__))
BRUTO = os.path.join(ROOT, "brutos", "nov26")
OUT = os.path.join(ROOT, "out")
VEL = 1.2
ESPELHADO = {"075617"}      # câmera da frente: a bolsa com "AZUL" saía ao contrário
VEL_ARQ = {"075617": 1.0}   # a abertura vai na velocidade normal


def vel(f):
    return VEL_ARQ.get(f, VEL)
GAP = 0.15            # pausa máxima entre palavras
SR = 44100
VOZ = ("highpass=f=80,afftdn=nr=10:nf=-45,equalizer=f=300:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1.4:g=1.5,"
       "acompressor=threshold=-20dB:ratio=2:attack=8:release=150")
GRADE = "hqdn3d=2:1.5:3:3,eq=contrast=1.03:saturation=1.04:gamma=1.02,unsharp=5:5:0.35"
# (arquivo, início, fim no bruto, título da parte ou None, asterisco?)
CORTES = [
    ("075617", 0.0, 2.75, None, False),          # abertura da Jéssica (26/nov): "Vem comigo aprender..."
    ("070944", 0.0, 4.3, "O TABULEIRO", False),
    ("071048", 0.0, 3.6, "NA SUA VEZ", False),
    ("071048", 4.9, 6.45, None, False),
    ("071048", 8.75, 10.95, None, False),
    ("071048", 13.2, 18.0, None, False),
    ("071252", 0.0, 13.75, "OU PEGA DO MEIO", False),
    ("071604", 0.0, 3.95, "FIM DA RODADA", False),
    ("071604", 4.3, 6.35, None, False),
    ("072121", 1.85, 6.1, "PONTUAÇÃO", False),
    ("072121", 6.75, 13.20, None, False),
    ("072121", 14.0, 15.0, None, False),         # ele fala "pedras", para e repete "em outra pedra": só a 2ª
    ("072121", 28.6, 33.3, None, True),
    ("072121", 39.6, 41.6, None, False),
    ("072308", 0.0, 2.46, "FIM DO JOGO", False),
    ("072308", 7.3, 10.95, None, False),
    ("072308", 11.45, 12.7, None, False),
    ("072308", 15.6, 16.9, None, False),
    ("072308", 17.1, 20.2, None, False),
    ("072441", 0.0, 3.0, None, False),
]
# asterisco: do "quebrou" até o fim do 071252, e no "quebrei" do 072121
AST_071252 = 6.6
CORRIGE = {"Azumini": "Azul Mini", "a menos.": "ou menos.", "mostruário": "mostruário", "tabuleirinho.": "tabuleirinho."}
# adesivos de ponto/marcos que entram NA PALAVRA (arquivo, palavra, texto, cor, x, y)
MARCAS = [
    ("070944", "parede", "A PAREDE", CEU, 760, 1250),
    ("071048", "azuis", "TODOS DA MESMA COR!", AMAR, 540, 760),
    ("071048", "centro.", "O RESTO VAI PRO MEIO", PESS, 540, 760),
    ("071048", "esquerdo", "LINHAS DA ESQUERDA", MENTA, 540, 760),
    ("071252", "daqui", "QUEM PEGA O 1 COMEÇA A PRÓXIMA RODADA", CEU, 540, 510),
    ("071252", "negativos", "PONTOS NEGATIVOS!", (255, 120, 140), 540, 510),
    ("071604", "completas.", "SÓ LINHA COMPLETA", MENTA, 540, 760),
    ("072121", "pontinho", "+1", AMAR, 540, 800),
    ("072121", "mais", "+2", AMAR, 540, 800),
    ("072121", "menos", "-1", (255, 120, 140), 880, 1390),
    ("072121", "quatro", "4 PONTOS!", AMAR, 830, 1390),
    ("072308", "dois", "LINHA +2", CEU, 540, 800),
    ("072308", "dez", "5 DA MESMA COR +10", ROSA, 540, 800),
    ("072308", "sete", "COLUNA +7", MENTA, 540, 800),
]


@lru_cache(None)
def transc():
    return json.load(open(os.path.join(BRUTO, "transc.json"), encoding="utf-8"))


@lru_cache(None)
def energias(f):
    """Energia (dB) a cada 10 ms do áudio inteiro e da parte AGUDA (> 3 kHz, onde mora o "s")."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(BRUTO, f + ".mp4"), "-ac", "1", "-ar", "16000",
                          "-f", "s16le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float64) / 32768
    q = 160
    n = len(x) // q
    fr = x[:n * q].reshape(n, q)
    tot = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9)
    hp = np.diff(x, prepend=0)                    # derivada = realça os agudos
    hp = np.diff(hp, prepend=0)
    ag = 20 * np.log10(np.sqrt((hp[:n * q].reshape(n, q) ** 2).mean(1)) + 1e-9)
    return tot, ag, np.percentile(tot, 20), np.percentile(ag, 20)


def borda(f, t, sentido, limite):
    """Anda a partir de t (fim/início da palavra no Whisper) enquanto ainda há voz OU chiado de "s",
    sem passar do limite (a palavra vizinha). Assim o "s" final e a 1ª consoante não são cortados."""
    tot, ag, p_tot, p_ag = energias(f)
    i = int(t / 0.01)
    lim = int(limite / 0.01)
    quietos = 0
    while (i < lim if sentido > 0 else i > lim) and 0 <= i < len(tot):
        voz = tot[i] > p_tot + 9 or ag[i] > p_ag + 10
        quietos = 0 if voz else quietos + 1
        if quietos >= 4:            # 40 ms de silêncio de verdade
            break
        i += sentido
    return (i - sentido * quietos) * 0.01 + sentido * 0.05


def pedacos():
    """Cada corte vira pedaços de fala com pausas ≤ GAP. → [(arq, a, b, corte_idx, palavras)]
    26/nov: o fim de cada pedaço agora segue a ENERGIA (o Whisper termina a palavra antes do "s": cortava
    "azuis", "paredes"...)."""
    out = []
    for ci, (f, a, b, _tit, _ast) in enumerate(CORTES):
        todas = transc()[f]
        ws = [w for w in todas if a - 0.05 <= w["s"] < b]
        grupos, grupo = [], []
        for w in ws:
            if grupo and w["s"] - grupo[-1]["e"] > GAP + 0.1:
                grupos.append(grupo)
                grupo = []
            grupo.append(w)
        if grupo:
            grupos.append(grupo)
        for g in grupos:
            k0, k1 = todas.index(g[0]), todas.index(g[-1])
            ant = todas[k0 - 1]["e"] + 0.03 if k0 > 0 else 0.0
            prox = todas[k1 + 1]["s"] - 0.03 if k1 + 1 < len(todas) else g[-1]["e"] + 0.8
            ini = max(ant, borda(f, g[0]["s"], -1, max(ant, g[0]["s"] - 0.15)))
            fim = min(prox, borda(f, g[-1]["e"], 1, min(prox, g[-1]["e"] + 0.7)))
            fim = max(fim, g[-1]["e"] + 0.08)
            if k1 + 1 == len(todas):   # última fala do arquivo: deixa o fim respirar até o fim da gravação
                fim = max(fim, min(g[-1]["e"] + 0.4, len(energias(f)[0]) * 0.01 - 0.02))
            if out and out[-1][0] == f:
                ini = max(ini, out[-1][2])
            out.append((f, ini, fim, ci, g))
    return out


PEDACOS = pedacos()


def linha_tempo():
    tl, t = [], 0.0
    for f, a, b, ci, g in PEDACOS:
        d = (b - a) / vel(f)
        n = round((t + d) * FPS) - round(t * FPS)
        tl.append(dict(f=f, a=a, b=b, ci=ci, g=g, t0=t, n=n))
        t += n / FPS
    return tl, t


TL, T_FALA = linha_tempo()
T_FIM_EXPL = next(p["t0"] for p in TL if p["f"] == "072441")   # o "E essa foi a explicação..." já é o fecho
T_CARIMBO = T_FALA + 0.2
T_COM = T_CARIMBO + 2.6
T_CTA = T_COM + 4.0
DUR = T_CTA + 5.6
T_EXP0 = next(p["t0"] for p in TL if p["f"] == "070944")       # a explicação (e o relógio) começa aqui
SEG_EXPL = T_FIM_EXPL - T_EXP0


def saida(f, tb):
    """Tempo no bruto → tempo no vídeo (ou None se o trecho saiu)."""
    for p in TL:
        if p["f"] == f and p["a"] <= tb <= p["b"]:
            return p["t0"] + (tb - p["a"]) / vel(f)
    return None


def palavras_saida():
    res = []
    for p in TL:
        for w in p["g"]:
            s = saida(p["f"], w["s"])
            e = saida(p["f"], min(w["e"], p["b"]))
            if s is not None:
                res.append(dict(w=CORRIGE.get(w["w"], w["w"]), s=s, e=e or s + 0.2, f=p["f"], ci=p["ci"], raw=w["w"]))
    return res


PAL = palavras_saida()


def ini_corte(ci):
    return min(p["t0"] for p in TL if p["ci"] == ci)


# ---------------------------------------------------------------- vídeo base (cortes + velocidade)
def base():
    """Concatena os pedaços (imagem e voz a VEL) → out/azul1min_base.mp4 + out/azul1min_voz.wav."""
    os.makedirs(os.path.join(OUT, "_p"), exist_ok=True)
    lista = []
    for k, p in enumerate(TL):
        dst = os.path.join(OUT, "_p", f"p{k:02d}.mp4")
        d = p["n"] / FPS
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{p['a']:.3f}", "-t", f"{(p['b'] - p['a']) + 0.2:.3f}",
                        "-i", os.path.join(BRUTO, p["f"] + ".mp4"),
                        "-vf", f"setpts=PTS/{vel(p['f'])},fps={FPS},scale={W}:{H},{GRADE}" + (",hflip" if p["f"] in ESPELHADO else ""),
                        "-af", f"atempo={vel(p['f'])},{VOZ},aresample={SR}",
                        "-t", f"{d:.4f}", "-c:v", "libx264", "-crf", "15", "-preset", "fast", "-c:a", "pcm_s16le",
                        "-ar", str(SR), "-ac", "1", dst.replace(".mp4", ".mkv")], check=True)
        lista.append(dst.replace(".mp4", ".mkv"))
    with open(os.path.join(OUT, "_p", "lista.txt"), "w") as fh:
        for l in lista:
            fh.write(f"file '{l}'\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i",
                    os.path.join(OUT, "_p", "lista.txt"), "-c", "copy", os.path.join(OUT, "azul1min_base.mkv")],
                   check=True)


@lru_cache(None)
def voz():
    """Voz montada no tempo do vídeo, com 12 ms de rampa em cada emenda e ganho fixo."""
    v = np.zeros(int((DUR + 1) * SR))
    for k, p in enumerate(TL):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(OUT, "_p", f"p{k:02d}.mkv"), "-f", "s16le",
                              "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
        x = np.frombuffer(raw, np.int16).astype(np.float64) / 32768
        n = int(round(p["n"] / FPS * SR))
        x = np.pad(x, (0, max(0, n - len(x))))[:n]
        r = int(0.012 * SR)
        x[:r] *= np.linspace(0, 1, r)
        x[-r:] *= np.linspace(1, 0, r)
        i = int(round(p["t0"] * SR))
        v[i:i + n] += x
    rms = np.sqrt((v[np.abs(v) > 0.02] ** 2).mean())
    return v * (10 ** (-18 / 20) / (rms + 1e-9))


# ---------------------------------------------------------------- sobreposições (tema do Azul: tema.py)
NEG = (255, 120, 140)


def legenda(img, t):
    """Palavra a palavra (até 3), serifa branca com contorno azul; a falada em dourado."""
    ativos = [w for w in PAL if w["s"] <= t < w["e"] + 0.35]
    if not ativos or t >= T_FALA + 0.1 or t < T_EXP0:
        return
    w0 = ativos[-1]
    idx = PAL.index(w0)
    ini = idx - (idx % 3)
    grupo = [w for w in PAL[ini:ini + 3] if w["ci"] == w0["ci"]]
    f = T.serif(74)
    sw = 7
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    partes = [(w["w"], w is w0) for w in grupo]
    larg = [d0.textbbox((0, 0), p, font=f, stroke_width=sw)[2] for p, _ in partes]
    tot = sum(larg) + 20 * (len(partes) - 1)
    im = Image.new("RGBA", (int(tot) + 20, 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = 10
    for (p, on), lw in zip(partes, larg):
        d.text((x, 60), p, font=f, fill=T.OURO if on else T.BRANCO, stroke_width=sw, stroke_fill=T.AZ_ESC, anchor="lm")
        x += lw + 20
    if im.width > W - 60:
        im = im.resize((W - 60, int(im.height * (W - 60) / im.width)), Image.LANCZOS)
    A.cola(img, T.sombra(im, 6, 0, 5, 0.5), W / 2, 1520)


def marcas(img, t):
    for f, palavra, txt, cor, x, y in MARCAS:
        ws = [w for w in PAL if w["f"] == f and w["raw"].lower().strip(",.!?") == palavra.strip(",.!?").lower()]
        if not ws:
            continue
        t0 = ws[0]["s"]
        fim_corte = max(p["t0"] + p["n"] / FPS for p in TL if p["ci"] == ws[0]["ci"])
        t1 = max(t0 + 0.9, min(t0 + 2.4, fim_corte + 0.3))   # 26/nov: some quando a fala muda de assunto
        if t0 <= t < t1:
            curto = len(txt) <= 4
            tam = (64 if y > 1300 else 96) if curto else (46 if len(txt) > 24 else (48 if y > 1300 else 60))
            sp = T.placa(txt, tam, T.VERM if cor == NEG else T.AZ_ESC)
            A.pop(img, sp, x, y, t, t0, 0, wob=False)


CANTOS = [("azul", 70, 300, -12), ("amarelo", 1010, 330, 10), ("vermelho", 62, 1760, 8), ("turquesa", 1015, 1730, -9)]


def pecas_cantos(img, t):
    for k, (cor, x, y, r) in enumerate(CANTOS):
        A.cola(img, T.peca(cor, 96), x, y + 6 * math.sin(t * 1.8 + k), r + 4 * math.sin(t * 1.2 + k))


def sobre(img, t):
    # gancho: letreiro AZUL MINI + placa + caixa
    if t < T_EXP0:
        A.pop(img, T.letreiro("AZUL MINI", 150), W / 2, 1330, t, 0.9, 0, wob=False)   # no peito (rosto livre)
        A.pop(img, T.placa("em 1 minuto ou menos", 62), W / 2, 1530, t, 1.6, 0, wob=False)
    for ci, c in enumerate(CORTES):  # placa com o nome da parte
        if c[3]:
            t0 = ini_corte(ci)
            prox = [ini_corte(k) for k in range(ci + 1, len(CORTES)) if CORTES[k][3]]
            t1 = min(prox + [T_FIM_EXPL])
            ta = t0
            if ta <= t < t1:
                A.pop(img, T.placa(c[3], 58), W / 2 + 40, 300, t, ta, 0, wob=False)
    marcas(img, t)
    ta = saida("071252", AST_071252)
    tb = ini_corte(7)
    tc = ini_corte(12)
    td = ini_corte(13) + 2.0
    if ta is not None and ta <= t < tb:    # 26/nov: no zoom da pontuação (072121) o cartão tapava a trilha de pontos
        A.pop(img, T.nota_asterisco(), W / 2, 800, t, ta if t < tb else tc, 0, wob=False)
    legenda(img, t)
    pecas_cantos(img, t)
    if T_EXP0 - 0.3 < t < T_FIM_EXPL + 0.8:
        rest = min(60.0, max(0.0, 60 - (min(t, T_FIM_EXPL) - T_EXP0)))
        A.pop(img, T.mostruario(rest, 190, rest <= 10), 135, 135, t, T_EXP0 - 0.3, 0, wob=False)
    A.cola(img, K.logo(150), W - 110, 95)


@lru_cache(None)
def caixa_ok(h):
    c = A.caixa()
    return c.resize((int(c.width * h / c.height), h), Image.LANCZOS)


def fundo_tema(t):
    """Parede de azulejos clareada, deslizando devagar."""
    base_ = T.parede_azulejos(W, H + 180, 180, 0.5)
    dy = int((t * 18) % 180)
    return base_.crop((0, dy, W, dy + H)).copy()


def painel(img, y0, y1):
    p = Image.new("RGBA", (W - 100, y1 - y0), (0, 0, 0, 0))
    T._moldura(ImageDraw.Draw(p), 2, 2, p.width - 3, p.height - 3, 30)
    A.cola(img, T.sombra(p, 14, 0, 10, 0.4), W / 2, (y0 + y1) / 2)


def carimbo(img, t):
    u = t - T_CARIMBO
    s = 1.5 - 0.5 * A.out_back(min(1, u / 0.3)) if u < 0.3 else 1.0
    A.pop(img, T.letreiro("Explicado em\n%d segundos!" % round(SEG_EXPL), 118), W / 2, 880, t, T_CARIMBO, -3, s,
          wob=False)
    for k, c in enumerate(list(T.PECAS) * 2):
        a = k * 0.628 + u * 0.7
        A.pop(img, T.peca(c, 110), W / 2 + 430 * math.cos(a), 880 + 520 * math.sin(a), t, T_CARIMBO + 0.15 + k * 0.05,
              k * 17, wob=False)


def comenta(img, t):
    painel(img, 420, 1380)
    A.pop(img, T.letreiro("E aí?", 150, T.OURO), W / 2, 590, t, T_COM, 0, wob=False)
    A.pop(img, T.letreiro("Você seria quem\nquebra todos os\nazulejos?", 84), W / 2, 900, t, T_COM + 0.35, 0,
          wob=False)
    A.pop(img, T.placa("Comenta aqui!", 66, T.VERM), W / 2, 1230, t, T_COM + 0.8, 0, wob=False)
    for k, c in enumerate(["vermelho", "preto", "amarelo", "azul", "turquesa"]):
        A.pop(img, T.peca(c, 130), 180 + k * 180, 1560 + 18 * math.sin(t * 2.5 + k), t, T_COM + 1.1 + k * 0.1,
              k * 9 - 18, wob=False)


def cta(img, t):
    painel(img, 230, 1700)
    A.pop(img, K.logo(230), W / 2, 360, t, T_CTA, 0, wob=False)
    A.pop(img, T.letreiro("Alugue o\nAzul Mini", 110), W / 2, 610, t, T_CTA + 0.15, 0, wob=False)
    A.pop(img, T.sombra(caixa_ok(560), 12, 0, 10, 0.45), W / 2, 1060, t, T_CTA + 0.35, 2, wob=False)
    A.pop(img, T.placa("2 a 4 jogadores · 8+", 46), W / 2, 1400, t, T_CTA + 0.6, 0, wob=False)
    d = ImageDraw.Draw(img)
    if t > T_CTA + 0.8:
        d.text((W / 2, 1515), "RETIRE EM MAUÁ OU RECEBA EM CASA", font=T.fig(40), fill=T.AZ_ESC, anchor="mm")
        d.text((W / 2, 1590), "LINK NA BIO · @SUAVEZ_BG", font=T.serif(52), fill=T.VERM, anchor="mm")


# ---------------------------------------------------------------- quadros
def frames_base():
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", os.path.join(OUT, "azul1min_base.mkv"), "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    n = W * H * 3
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        yield Image.frombytes("RGB", (W, H), b)


SEM_LEGENDA = False


def compoe(fr, t, leg=True):
    global legenda
    if t < T_FALA:
        img = fr.convert("RGBA")
        if leg:
            sobre(img, t)
        else:
            _l = legenda
            legenda = lambda *a: None  # noqa: E731
            sobre(img, t)
            legenda = _l
    else:
        img = fundo_tema(t)
        if t < T_COM:
            carimbo(img, t)
        elif t < T_CTA:
            comenta(img, t)
        else:
            cta(img, t)
        if t < T_CTA:
            A.cola(img, K.logo(150), W - 110, 95)
    for tb in (T_FALA, T_COM, T_CTA):
        if 0 <= t - tb < 0.1:
            img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(170 * (1 - (t - tb) / 0.1)))))
    return img.convert("RGB")
def audio(path):
    ev = [(0.05, S.estouro(), 0.4), (0.35, S.estouro(), 0.4), (0.6, S.plim(), 0.3)]
    for ci, c in enumerate(CORTES):
        if c[3] and ci:
            ev.append((ini_corte(ci), S.plim(), 0.25))
    for f, palavra, *_ in MARCAS:
        ws = [w for w in PAL if w["f"] == f and w["raw"].lower().strip(",.!?") == palavra.strip(",.!?").lower()]
        if ws:
            ev.append((ws[0]["s"], S.estouro(), 0.3))
    ev += [(T_CARIMBO, S.estouro(), 0.6), (T_CARIMBO + 0.05, S.sino(), 0.5), (T_COM, S.plim(), 0.45),
           (T_CTA, S.carta_vira(), 0.5)]
    n = int(DUR * SR)
    fx = np.zeros(n)
    for t, s_, g in ev:
        S.add(fx, s_, t, g)
    mus = S.musica_marimba_pop(DUR + 0.5)[:n]
    mus = np.pad(mus, (0, n - len(mus))) / (np.abs(mus).max() + 1e-9)
    v = voz()[:n]
    env = np.convolve(np.abs(v), np.ones(int(0.25 * SR)) / int(0.25 * SR), "same")
    duck = 1 - 0.75 * np.clip(env / (env.max() * 0.25 + 1e-9), 0, 1)
    mix = v + mus * 0.16 * duck + fx * 0.35
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.89
    st = np.repeat((mix * 32767).astype(np.int16)[:, None], 2, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(st.tobytes())


def render(saida_mp4, wav, leg):
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-framerate", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-crf", "18", "-preset",
                          "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags",
                          "+faststart", saida_mp4], stdin=subprocess.PIPE)
    fb = frames_base()
    ultimo = None
    for k in range(int(round(DUR * FPS))):
        t = k / FPS
        fr = next(fb, None) if t < T_FALA else None
        ultimo = fr or ultimo or Image.new("RGB", (W, H))
        p.stdin.write(compoe(fr or ultimo, t, leg).tobytes())
    p.stdin.close()
    p.wait()


def main():
    os.makedirs(OUT, exist_ok=True)
    print(f"explicação {SEG_EXPL:.1f} s, fala {T_FALA:.1f} s, total {DUR:.1f} s")
    if "--info" in sys.argv:
        for p in TL:
            print(f"{p['t0']:6.2f} {p['f']} {p['a']:.2f}-{p['b']:.2f}", " ".join(w["w"] for w in p["g"]))
        return
    if not os.path.exists(os.path.join(OUT, "azul1min_base.mkv")) or "--base" in sys.argv:
        base()
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:]]
        alvo = {round(x * FPS): x for x in ts}
        ims = {}
        fb = frames_base()
        ult = None
        for k in range(int(round(DUR * FPS))):
            t = k / FPS
            fr = next(fb, None) if t < T_FALA else None
            ult = fr or ult
            if k in alvo:
                ims[k] = compoe(fr or ult, t)
            if len(ims) == len(alvo):
                break
        K.folha([ims[k] for k in sorted(ims)], os.path.join(OUT, "frames_azul1min.jpg"))
        return
    wav = os.path.join(OUT, "azul1min.wav")
    audio(wav)
    for leg in (True, False):
        nome = "legendado" if leg else "sem_legenda"
        bruto = os.path.join(OUT, f"azul1min_{nome}.mp4")
        render(bruto, wav, leg)
        from base import final_loudness
        final_loudness(bruto, bruto.replace(".mp4", "_final.mp4"))
        print("ok", nome)


if __name__ == "__main__":
    main()
