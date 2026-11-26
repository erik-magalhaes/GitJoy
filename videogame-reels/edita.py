#!/usr/bin/env python3
"""Reels GRAVADO pelo Erik (26/nov/2026): "5 jogos que te fazem sentir dentro do videogame".
Brutos no Drive de brutos → brutos/ (fora do git): 144733 (gancho) e 144818 (4 min, várias tentativas).
Pedido: bem dinâmico, NÃO cortar palavras, melhores tomadas, imagem dos jogos citados (tabuleiro E digital) e
pedacinhos de gameplay dos videogames (trailers OFICIAIS: Steam e o site do GTA VI → brutos/gameplay/).

Montagem: rosto dele em tela cheia (corte seco entre tomadas, alternando aberto / punch-in), um PAINEL de "tela de
videogame" no alto (sobre a estante) com o gameplay do jogo digital, a caixa oficial do jogo de tabuleiro saltando
ao lado quando ele fala o nome, "FASE n" entre os jogos, legenda palavra a palavra no peito e tela final.

    /usr/bin/python3 edita.py --frame 3 10 20 30     # out/frames.jpg
    /usr/bin/python3 edita.py                        # out/videogame_final.mp4 (+ _chat.mp4 < 30 MB)
"""
import json
import math
import os
import subprocess
import sys
import wave
from functools import lru_cache

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
sys.path.insert(0, os.path.join(REPO, "becas-reels"))
import estilo as E  # noqa: E402
import sons as S  # noqa: E402

FF = imageio_ffmpeg.get_ffmpeg_exe()
BR = os.path.join(ROOT, "brutos")
GP = os.path.join(BR, "gameplay")
OUT = os.path.join(ROOT, "out")
CX = os.path.join(ROOT, "assets", "caixas")
CP = os.path.join(ROOT, "assets", "capas")
AC = os.path.join(REPO, "hobby-reels", "assets", "acervo")
W, H, FPS, SR = 1080, 1920, 30, 44100
TRANS = os.path.join(OUT, "transcricao")

JOGOS = {  # caixa, nome na tela
    "bad": (f"{AC}/bad_company.png", "BAD COMPANY"),
    "res": (f"{AC}/the_resistance.png", "THE RESISTANCE"),
    "ww": (f"{AC}/world_wonders.png", "WORLD WONDERS"),
    "heat": (f"{CX}/heat.png", "HEAT: PEDAL TO THE METAL"),
    "dbd": (f"{CX}/dbd.png", "DEAD BY DAYLIGHT: O JOGO DE TABULEIRO"),
}
# clipes de gameplay: (arquivo, início, duração); vários trechos encadeados em loop
CLIPES = {
    # GTA VI: o trailer só existe no YouTube → imagens OFICIAIS do site (rockstargames.com/VI) com zoom (Ken Burns)
    "gta": [(f"{GP}/gta6img/{i}.jpg", "img", 0.9) for i in (11, 5, 26, 8, 21, 12, 20, 4, 39, 44)],
    "among": [(f"{GP}/among_us.mp4", 21.5, 9.0)],
    "aoe": [(f"{GP}/aoe2.mp4", 34.5, 5.0), (f"{GP}/aoe4.mp4", 0.5, 4.0)],
    "forza": [(f"{GP}/forza.mp4", 15.0, 18.0)],
    "dbd": [(f"{GP}/dbd.mp4", 30.5, 4.0), (f"{GP}/dbd.mp4", 4.5, 3.0), (f"{GP}/dbd.mp4", 46.0, 6.0)],
}
CAPAS = {"gta": "gta6.jpg", "among": "among_us.jpg", "aoe": "aoe2.jpg", "forza": "forza.jpg", "nfs": "nfs.jpg",
         "dbd": "dbd.jpg"}
NOME_DIG = {"gta": "GTA 6", "among": "AMONG US", "aoe": "AGE OF EMPIRES", "forza": "FORZA HORIZON",
            "nfs": "NEED FOR SPEED", "dbd": "DEAD BY DAYLIGHT"}

# Planos: (bruto, primeira palavra, última palavra (tempos do Whisper, para achar o corte pela energia), fase, eventos)
# eventos em tempo do BRUTO: ("dig", t, clipe) mostra o gameplay; ("cx", t, jogo) faz a caixa saltar;
# ("capa", t, chave) troca a capa do canto; ("chips", t, [...]); ("lista", t) leque das 5 caixas; ("missao", t)
PLANOS = [
    ("144733", 7.42, 13.90, 0, [("dig", 7.3, "gta"), ("lista", 11.5)]),
    ("144818", 12.56, 21.04, 1, [("dig", 12.4, "gta"), ("cx", 16.4, "bad")]),
    ("144818", 33.84, 43.80, 2, [("cx", 35.6, "res"), ("dig", 37.5, "among")]),
    ("144818", 98.74, 104.20, 3, [("cx", 101.5, "ww"), ("dig", 103.7, "aoe")]),
    ("144818", 114.32, 118.24, 4, [("cx", 116.9, "heat")]),
    ("144818", 125.24, 129.26, 4, [("dig", 126.1, "forza"), ("capa", 127.4, "nfs")]),
    ("144818", 149.40, 156.12, 5, [("dig", 152.3, "dbd"), ("cx", 155.9, "dbd")]),
    ("144818", 140.08, 142.60, 5, [("chips", 140.1, ["5 JOGADORES", "4 SOBREVIVENTES", "1 ASSASSINO"])]),
    ("144818", 190.26, 195.78, 6, [("missao", 190.2)]),
    ("144818", 239.46, 244.86, 7, [("lista", 239.4)]),
]
# o que ele falou (legenda), corrigindo o Whisper
CORRIGE = {"Dead": "Dead", "the": "by", "Light.": "Daylight.", "Light,": "Daylight,", "Hit": "Heat:",
           "Petal,": "Pedal,", "Petal.": "Pedal.", "biu.": "bio.", "pensarei": "pensando,", "trouxe": "eu trouxe o",
           "sua": "Sua", "vez.": "Vez."}
FIM = 2.6  # tela final


# ------------------------------------------------------------------------------------------------ áudio / cortes
@lru_cache(None)
def audio_bruto(nome):
    raw = subprocess.run([FF, "-v", "error", "-i", os.path.join(BR, nome + ".mp4"), "-ac", "1", "-ar", str(SR),
                          "-af", "highpass=f=80,afftdn=nr=8:nf=-45,equalizer=f=300:t=q:w=1:g=-2,"
                                 "equalizer=f=3200:t=q:w=1.2:g=2,acompressor=threshold=-20dB:ratio=2:attack=8:release=160",
                          "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def energia(a, t0, t1):
    i0, i1 = max(0, int(t0 * SR)), int(t1 * SR)
    seg = a[i0:i1]
    n = int(0.02 * SR)
    k = max(1, len(seg) // n)
    e = np.array([np.sqrt(np.mean(seg[j * n:(j + 1) * n] ** 2) + 1e-12) for j in range(k)])
    return 20 * np.log10(e + 1e-9), n


def corte(nome, w0, w1):
    """Começo: o início da voz (energia > −30 dB) logo antes da 1ª palavra, menos 0,08 s; fim: o ÚLTIMO quadro com
    voz depois da última palavra (até a próxima palavra), mais 0,1 s. Uma consoante como o "p" faz um microssilêncio
    no meio da palavra (Age of Em-p-ires): por isso não se corta no ponto mais quieto, e sim depois da última voz."""
    a = audio_bruto(nome)
    pal = json.load(open(os.path.join(TRANS, nome + ".json")))
    ant = max([p["e"] for p in pal if p["e"] <= w0 - 0.05] or [0])
    prox = min([p["s"] for p in pal if p["s"] >= w1 + 0.15] or [len(a) / SR])
    lim = -30
    ant_real = max([p["e"] for p in pal if p["s"] < w0 - 0.05] or [0])
    if w0 - ant_real < 0.15:  # sem pausa antes (ex.: "...Pedal. Então"): corta no ponto mais quieto entre as palavras
        e, n = energia(a, ant_real - 0.08, w0 + 0.06)
        ini = ant_real - 0.08 + int(np.argmin(e)) * n / SR
        f1 = min(w1 + 0.9, prox - 0.08)
        e, n = energia(a, w1 - 0.1, f1)
        voz = [i for i, x in enumerate(e) if x > lim]
        fim = min(f1, w1 - 0.1 + (voz[-1] + 1) * n / SR + 0.1) if voz else w1 + 0.2
        return round(ini, 3), round(fim, 3)
    s0 = max(ant + 0.08, w0 - 0.18)  # mais cedo que isso costuma ser respiro
    e, n = energia(a, s0, w0 + 0.15)
    voz = [i for i, x in enumerate(e) if x > lim]
    ini = s0 + voz[0] * n / SR - 0.08 if voz else w0 - 0.15
    f1 = min(w1 + 0.9, prox - 0.08)
    e, n = energia(a, w1 - 0.1, f1)
    voz = [i for i, x in enumerate(e) if x > lim]
    fim = min(f1, w1 - 0.1 + (voz[-1] + 1) * n / SR + 0.1) if voz else w1 + 0.2
    return round(max(ini, ant + 0.03), 3), round(fim, 3)


PAUSA = 0.22  # pausa interna maior que isso vira corte seco


def pedacos(nome, a, b):
    """Divide [a, b] nas pausas internas (energia < −32 dB por mais de PAUSA), deixando 0,05 s de folga."""
    au = audio_bruto(nome)
    e, n = energia(au, a, b)
    dt = n / SR
    quieto = e < -32
    out, ini, i = [], a, 0
    while i < len(e):
        if quieto[i]:
            j = i
            while j < len(e) and quieto[j]:
                j += 1
            if (j - i) * dt > PAUSA and i > 0 and j < len(e):
                out.append((ini, a + i * dt + 0.12))  # rabo da palavra (fim de sílaba baixinho)
                ini = a + j * dt - 0.05
            i = j
        else:
            i += 1
    out.append((ini, b))
    return [(x, y) for x, y in out if y - x > 0.12]


def linha_do_tempo():
    tl, t, k = [], 0.0, 0
    for pk, (nome, w0, w1, fase, evs) in enumerate(PLANOS):
        a, b = corte(nome, w0, w1)
        pcs = pedacos(nome, a, b)
        # pedacinho curto antes da 1ª pausa SEM nenhuma palavra = respiro; se tiver palavra (o "Agora" baixinho), fica
        pal = json.load(open(os.path.join(TRANS, nome + ".json")))
        if len(pcs) > 1 and pcs[0][1] - pcs[0][0] < 0.6 and not any(
                pcs[0][0] - 0.05 <= w["s"] <= pcs[0][1] - 0.1 for w in pal):
            pcs = pcs[1:]
        for j, (x, y) in enumerate(pcs):
            nf = max(1, round((y - x) * FPS))
            tl.append(dict(k=k, pk=pk, nome=nome, a=x, b=x + nf / FPS, ini=t, dur=nf / FPS, fase=fase, evs=evs,
                           primeira=(j == 0), inicio_fase=(j == 0 and (pk == 0 or PLANOS[pk - 1][3] != fase))))
            t += nf / FPS
            k += 1
    # zoom: reenquadramento a cada ~2,4 s (referências de edição de Reels: corte ou zoom a cada 1,5–3 s), alternando
    # 100% / 112% / 106%, sempre diferente do anterior (o corte seco entre pedaços também troca o zoom)
    niveis = [1.22, 1.32, 1.26, 1.36]  # mais perto: mostra menos corpo (pedido dele)
    z = 0
    for p in tl:
        n = max(1, math.ceil(p["dur"] / 2.4))
        p["zooms"] = [(i * p["dur"] / n, niveis[(z + i) % len(niveis)]) for i in range(n)]
        z += n
    return tl, t


def src2out(pk, ts):
    """Tempo do bruto (do plano pk) → tempo de saída (cai no pedaço seguinte se estiver numa pausa cortada)."""
    ps = [p for p in TL if p["pk"] == pk]
    for p in ps:
        if ts < p["b"]:
            return p["ini"] + max(0.0, ts - p["a"])
    return ps[-1]["ini"] + ps[-1]["dur"]


TL, DUR_FALA = linha_do_tempo()
DUR = DUR_FALA + FIM


def palavras_tl():
    out = []
    for p in TL:
        pal = json.load(open(os.path.join(TRANS, p["nome"] + ".json")))
        for w in pal:
            if p["a"] - 0.08 <= w["s"] < p["b"] - 0.02:
                txt = w["w"]
                if txt == "the" and p["nome"] == "144818" and 147 < w["s"] < 153:
                    continue  # "Dead by the Light" → "Dead by Daylight"
                txt = CORRIGE.get(txt, txt)
                if txt == "Metal" and 116 < w["s"] < 125:
                    continue  # "Hit Metal to the Petal" → "Heat: Pedal to the Metal"
                if txt == "Pedal," and 116 < w["s"] < 125:
                    txt = "Pedal to the Metal,"
                if txt in ("to", "the") and 116 < w["s"] < 125:
                    continue
                out.append((p["ini"] + w["s"] - p["a"], p["ini"] + w["e"] - p["a"], txt))
    return out


PAL = palavras_tl()


# ------------------------------------------------------------------------------------------------ vídeo base
def base_video():
    """Corta os planos do bruto (cor leve, punch-in alternado) e junta num só vídeo CFR 30 fps."""
    os.makedirs(os.path.join(OUT, "_planos"), exist_ok=True)
    lst = []
    for p in TL:
        o = os.path.join(OUT, "_planos", f"p{p['k']:02d}.mp4")
        vf = ("scale=1080:1920,hqdn3d=3:3:4:4,smartblur=lr=1.2:ls=0.3:lt=-4,eq=contrast=1.05:saturation=1.06,"
              "colorbalance=rs=0.02:bs=-0.02:rm=0.025:bm=-0.025,unsharp=5:5:0.45,fps=30")
        nf = round(p["dur"] * FPS)
        subprocess.run([FF, "-v", "error", "-y", "-ss", str(p["a"]), "-i", os.path.join(BR, p["nome"] + ".mp4"),
                        "-frames:v", str(nf), "-vf", vf, "-an", "-c:v", "libx264", "-crf", "16", "-preset", "fast",
                        o], check=True)
        lst.append(o)
    txt = os.path.join(OUT, "_planos", "lista.txt")
    open(txt, "w").write("".join(f"file '{x}'\n" for x in lst))
    base = os.path.join(OUT, "_base.mp4")
    subprocess.run([FF, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", txt, "-c", "copy", base], check=True)
    return base


class Leitor:
    """Lê quadros em sequência (tempo crescente) de um vídeo, já redimensionado."""

    def __init__(self, path, size, ini=0.0, dur=None):
        self.path, self.size, self.ini, self.dur = path, size, ini, dur
        self.gen, self.idx, self.ultimo = None, -1, None

    def quadro(self, t):
        i = int(t * FPS)
        w, h = self.size
        if self.gen is None or i < self.idx:
            if self.gen is not None:
                self.gen.kill()
            vf = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps=30"
            self.gen = subprocess.Popen([FF, "-v", "error", "-ss", str(self.ini), "-i", self.path, "-vf", vf,
                                         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE,
                                        bufsize=w * h * 3 * 4)
            self.idx = -1
        while self.idx < i:
            fr = self.gen.stdout.read(w * h * 3)
            if len(fr) < w * h * 3:
                break
            self.ultimo = fr
            self.idx += 1
        if self.ultimo is None:
            return Image.new("RGB", self.size)
        return Image.frombytes("RGB", self.size, self.ultimo)


def dur_video(p):
    s = subprocess.run([FF, "-i", p], capture_output=True, text=True).stderr
    h, m, x = s.split("Duration: ")[1].split(",")[0].split(":")
    return float(h) * 3600 + float(m) * 60 + float(x)


PW, PH = 960, 540  # tela de gameplay
PX, PY = (W - PW) // 2, 150


class KenBurns:
    """Imagem oficial com aproximação lenta (alternando o lado), no tamanho da tela de gameplay."""

    def __init__(self, path, k):
        im = Image.open(path).convert("RGB")
        r = PW / PH
        if im.width / im.height > r:
            nw = int(im.height * r)
            im = im.crop(((im.width - nw) // 2, 0, (im.width - nw) // 2 + nw, im.height))
        else:
            nh = int(im.width / r)
            im = im.crop((0, (im.height - nh) // 2, im.width, (im.height - nh) // 2 + nh))
        self.im = im.resize((int(PW * 1.25), int(PH * 1.25)), Image.LANCZOS)
        self.k = k

    def quadro(self, t):
        z = 1.25 - 0.18 * min(t / 0.9, 1)
        w, h = int(PW * z), int(PH * z)
        dx = (self.im.width - w) * (0.2 if self.k % 2 else 0.8)
        dy = (self.im.height - h) / 2
        return self.im.crop((int(dx), int(dy), int(dx) + w, int(dy) + h)).resize((PW, PH), Image.BILINEAR)


class Gameplay:
    def __init__(self, chave):
        self.trechos = []
        for f, a, d in CLIPES[chave]:
            if a == "img":
                self.trechos.append((KenBurns(f, len(self.trechos)), d))
                continue
            d = d or dur_video(f) - 0.05
            self.trechos.append((Leitor(f, (PW, PH), a, d), d))
        self.total = sum(d for _, d in self.trechos)

    def quadro(self, t):
        t = t % self.total
        for l, d in self.trechos:
            if t < d:
                return l.quadro(t)
            t -= d
        return self.trechos[-1][0].quadro(0)


# ------------------------------------------------------------------------------------------------ gráficos
def ease(x):
    x = min(max(x, 0), 1)
    return 1 - (1 - x) ** 3


def back(x):
    x = min(max(x, 0), 1)
    c = 1.9
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


@lru_cache(None)
def moldura():
    m = Image.new("RGBA", (PW + 40, PH + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(m)
    d.rounded_rectangle((14, 16, PW + 34, PH + 36), radius=28, fill=(0, 0, 0, 140))
    d.rounded_rectangle((0, 0, PW + 20, PH + 20), radius=28, fill=(20, 20, 24), outline=E.MARROM, width=7)
    return m


@lru_cache(None)
def mascara_tela():
    m = Image.new("L", (PW, PH), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, PW - 1, PH - 1), radius=18, fill=255)
    return m


@lru_cache(None)
def capa(chave, h=210):
    im = Image.open(os.path.join(CP, CAPAS[chave])).convert("RGB")
    if im.width > im.height:
        w = int(im.height * 2 / 3)
        im = im.crop(((im.width - w) // 2, 0, (im.width - w) // 2 + w, im.height))
    im = im.resize((int(h * 2 / 3), h), Image.LANCZOS)
    out = E.bloco(im.width + 10, im.height + 10, (255, 255, 255), raio=12, ow=5, sombra=7)
    out.alpha_composite(im.convert("RGBA"), (5, 5))
    return out.rotate(6, expand=True, resample=Image.BICUBIC)


@lru_cache(None)
def caixa(jogo, h=360):
    return E.jogo(JOGOS[jogo][0], h, larg=int(h * 1.05))


@lru_cache(None)
def pilula(txt, s=30, cor=(20, 20, 24), cor_t=(255, 255, 255)):
    return E.pilula(txt, s, cor, cor_t, fonte_titulo=True, ow=4, sombra=6)


@lru_cache(None)
def leque():
    return E.leque([JOGOS[k][0] for k in ("bad", "res", "ww", "heat", "dbd")], 300, passo=0.55)


@lru_cache(None)
def logo_marca():
    return E.logo(150)


def tela_lista(t_ev, t, texto):
    """Painel com o leque das 5 caixas sobre fundo de videogame (azul-noite com grade)."""
    p = Image.new("RGB", (PW, PH), (18, 34, 58))
    d = ImageDraw.Draw(p)
    for x in range(0, PW, 30):
        d.line((x, 0, x, PH), fill=(28, 50, 80))
    for y in range(0, PH, 30):
        d.line((0, y, PW, y), fill=(28, 50, 80))
    lq = leque()
    k = ease((t - t_ev) / 0.5)
    lq2 = lq.resize((max(2, int(lq.width * 0.95)), max(2, int(lq.height * 0.95))))
    p.paste(lq2, ((PW - lq2.width) // 2, int(PH - lq2.height + 40 + (1 - k) * 300)), lq2)
    tt = E.titulo(texto, 52, cor=E.AMARELO, larg_max=PW - 60)
    p.paste(tt, ((PW - tt.width) // 2, 14), tt)
    return p


def tela_missao():
    p = Image.new("RGB", (PW, PH), (18, 34, 58))
    tt = E.titulo("SUA MISSÃO:", 80, cor=E.AMARELO)
    p.paste(tt, ((PW - tt.width) // 2, 60), tt)
    tx = E.texto("comenta o seu videogame favorito\ne o jogo de tabuleiro que lembra ele!", 44, cor=(255, 255, 255),
                 peso=800, larg_max=PW - 80)
    p.paste(tx, ((PW - tx.width) // 2, 220), tx)
    e = E.pilula("💬 COMENTA AQUI".replace("💬 ", ""), 44, E.LARANJA, (255, 255, 255), fonte_titulo=True)
    p.paste(e, ((PW - e.width) // 2, 400), e)
    return p


# ------------------------------------------------------------------------------------------------ quadro
GAMES = {}


def gameplay(chave):
    if chave not in GAMES:
        GAMES[chave] = Gameplay(chave)
    return GAMES[chave]


def estado(t):
    """Plano atual e os eventos já disparados (em tempo de saída)."""
    for p in TL:
        if p["ini"] <= t < p["ini"] + p["dur"]:
            evs = [(src2out(p["pk"], e[1]), e) for e in p["evs"]]
            return p, evs
    return None, []


def ultimo_ev(evs, t, tipos):
    v = [(te, e) for te, e in evs if e[0] in tipos and te <= t]
    return v[-1] if v else (None, None)


def legenda(img, t):
    # grupos de até 3 palavras (quebra na pontuação)
    grupos, g = [], []
    for w in PAL:
        g.append(w)
        if len(g) == 3 or w[2][-1] in ".,!?" or (len(g) >= 2 and len(" ".join(x[2] for x in g)) > 22):
            grupos.append(g)
            g = []
    if g:
        grupos.append(g)
    for g in grupos:
        if g[0][0] - 0.05 <= t < max(g[-1][1], g[-1][0] + 0.3) + 0.05:
            f = E.lilita(66)
            pal = [x[2] for x in g]
            d0 = ImageDraw.Draw(img)
            larg = sum(d0.textlength(p + " ", font=f) for p in pal)
            x = W / 2 - larg / 2
            y = 1500
            for (s, e, p) in g:
                cor = E.AMARELO if s - 0.03 <= t else (255, 255, 255)
                d0.text((x, y), p, font=f, fill=cor, stroke_width=7, stroke_fill=E.MARROM)
                x += d0.textlength(p + " ", font=f)
            return


FACE = (580, 1220)  # centro do rosto NO BRUTO (medido; nas duas gravações ele fica no mesmo lugar)
FACE_OUT = (540, 1220)  # onde o rosto fica na saída: centralizado


@lru_cache(None)
def mascara_luz():
    """Luz de rosto: clareia uma elipse em volta do rosto e escurece de leve as bordas (vinheta)."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - FACE_OUT[0]) / 430) ** 2 + ((yy - FACE_OUT[1] + 40) / 520) ** 2)
    luz = np.clip(1.15 - d, 0, 1) ** 1.5
    v = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.72)) ** 2)
    vin = 1 - 0.16 * np.clip(v - 0.55, 0, 1) / 0.45
    return luz[..., None], vin[..., None]


@lru_cache(None)
def rosto_no_pedaco(k):
    """Centro do rosto (mediana dos pontos do rosto.py dentro do pedaço): um valor fixo por pedaço = sem tremedeira."""
    p = TL[k]
    try:
        d = json.load(open(os.path.join(OUT, f"rosto_{p['nome']}.json")))
    except FileNotFoundError:
        return FACE
    v = [xy for ts, xy in d.items() if p["a"] - 0.1 <= float(ts) <= p["b"] + 0.1]
    if not v:
        return FACE
    return tuple(float(x) for x in np.median(np.array(v), axis=0))


def realce(img, t, p):
    """Zoom no rosto (reenquadramento por pedaço + aproximação lenta) e a luz de rosto."""
    if p is not None:
        dt = t - p["ini"]
        z0 = [z for (tz, z) in p["zooms"] if tz <= dt][-1]
        tz0 = [tz for (tz, z) in p["zooms"] if tz <= dt][-1]
        z = z0 * (1 + 0.035 * min((dt - tz0) / 3.0, 1))
        # sempre um pouco de zoom (≥ 1,08) para poder CENTRALIZAR o rosto na horizontal sem aparecer borda
        w, h = W / z, H / z
        fx, fy = rosto_no_pedaco(p["k"])
        x0 = min(max(fx - FACE_OUT[0] / z, 0), W - w)
        y0 = min(max(fy - FACE_OUT[1] / z, 0), H - h)
        img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h))
    a = np.asarray(img, np.float32)
    luz, vin = mascara_luz()
    a = a + (255 - a) * 0.13 * luz  # clareia os médios do rosto sem estourar o branco
    a = a * vin
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def quadro(base, t):
    if t >= DUR_FALA:
        return tela_final(t - DUR_FALA)
    p, evs = estado(t)
    img = realce(base, t, p).convert("RGBA")
    lg = logo_marca()
    img.alpha_composite(lg, (W - lg.width - 22, 18))
    if p is None:
        return img
    # ---------------- painel
    te_d, ev_d = ultimo_ev(evs, t, ("dig", "lista", "missao"))
    # o gameplay de um plano anterior da mesma fase continua (ex.: Forza → NFS no plano seguinte)
    if ev_d is None:
        for q in TL:
            if q["fase"] == p["fase"] and q["ini"] < p["ini"]:
                for e in q["evs"]:
                    if e[0] in ("dig",):
                        te_d, ev_d = src2out(q["pk"], e[1]), e
    if ev_d is not None:
        k = back((t - te_d) / 0.35)
        if ev_d[0] == "dig":
            tela = gameplay(ev_d[2]).quadro(t - te_d)
            nome = NOME_DIG[ev_d[2]]
        elif ev_d[0] == "lista":
            tela = tela_lista(te_d, t, "5 JOGOS PRA SE SENTIR NO VIDEOGAME" if p["pk"] == 0 else "TODOS NA SUA VEZ!")
            nome = None
        else:
            tela = tela_missao()
            nome = None
        pn = Image.new("RGBA", (PW + 40, PH + 40), (0, 0, 0, 0))
        pn.alpha_composite(moldura())
        tl = tela.convert("RGBA")
        tl.putalpha(mascara_tela())
        pn.alpha_composite(tl, (10, 10))
        if nome:
            pl = pilula("▶ " + nome if False else nome, 34)
            pn.alpha_composite(pl, (26, PH + 10 - pl.height - 14))
        if k < 0.999:
            s = max(0.05, k)
            pn = pn.resize((max(2, int(pn.width * s)), max(2, int(pn.height * s))), Image.BICUBIC)
        img.alpha_composite(pn, (int(W / 2 - pn.width / 2), int(PY + (PH + 40) / 2 - pn.height / 2)))
        # capa do videogame no canto
        if ev_d[0] == "dig":
            te_c, ev_c = ultimo_ev(evs, t, ("capa",))
            ch = ev_c[2] if ev_c else ev_d[2]
            kc = back((t - (te_c if ev_c else te_d) - 0.15) / 0.35)
            if kc > 0.05:
                c = capa(ch)
                c = c.resize((max(2, int(c.width * kc)), max(2, int(c.height * kc))), Image.BICUBIC)
                img.alpha_composite(c, (int(PX + PW - 70 - c.width / 2), int(PY - 30)))
    # ---------------- caixa do tabuleiro
    te_b, ev_b = ultimo_ev(evs, t, ("cx",))
    if ev_b is None:  # a caixa fica nos planos seguintes da mesma fase
        for q in TL:
            if q["fase"] == p["fase"] and q["ini"] < p["ini"]:
                for e in q["evs"]:
                    if e[0] == "cx":
                        te_b, ev_b = src2out(q["pk"], e[1]), e
    if ev_b is not None:
        k = back((t - te_b) / 0.4)
        cx = caixa(ev_b[2])
        flut = math.sin((t - te_b) * 2.2) * 6
        if k > 0.02:
            c2 = cx.resize((max(2, int(cx.width * k)), max(2, int(cx.height * k))), Image.BICUBIC)
            c2 = c2.rotate(-6 + 2 * math.sin((t - te_b) * 1.7), expand=True, resample=Image.BICUBIC)
            cxx, cyy = 835, 760 + flut
            img.alpha_composite(c2, (int(cxx - c2.width / 2), int(cyy - c2.height / 2)))
            if t - te_b > 0.25:
                nm = pilula(JOGOS[ev_b[2]][1], 30, E.LARANJA, (255, 255, 255))
                if nm.width > 560:
                    nm = nm.resize((560, int(nm.height * 560 / nm.width)), Image.LANCZOS)
                img.alpha_composite(nm, (int(min(W - nm.width - 20, cxx - nm.width / 2)), int(cyy + cx.height / 2 + 4)))
    # ---------------- chips do DbD
    te_h, ev_h = ultimo_ev(evs, t, ("chips",))
    if ev_h is not None:
        y = 960
        for i, tx in enumerate(ev_h[2]):
            ki = back((t - te_h - i * 0.45) / 0.3)
            if ki > 0.02:
                c = pilula(tx, 34, [E.PETROLEO, E.LARANJA, (200, 40, 40)][i], (255, 255, 255))
                c = c.resize((max(2, int(c.width * ki)), max(2, int(c.height * ki))), Image.BICUBIC)
                img.alpha_composite(c, (60, int(y + i * 90)))
    # ---------------- FASE n (flash no começo de cada jogo)
    if p["fase"] in (1, 2, 3, 4, 5) and p["inicio_fase"]:
        dt = t - p["ini"]
        if dt < 0.7:
            a = 1 - max(0, (dt - 0.45) / 0.25)
            s = 1.25 - 0.25 * ease(dt / 0.25)
            f = E.titulo(f"FASE {p['fase']}", 150, cor=E.AMARELO)
            f = f.resize((int(f.width * s), int(f.height * s)), Image.BICUBIC)
            if a < 1:
                f.putalpha(f.getchannel("A").point(lambda v: int(v * a)))
            img.alpha_composite(f, (int(W / 2 - f.width / 2), int(1330 - f.height / 2)))
    if p["fase"] in (1, 2, 3, 4, 5):
        h = pilula(f"FASE {p['fase']}/5", 28, E.AMARELO, E.MARROM)
        img.alpha_composite(h, (26, 30))
    legenda(img, t)
    return img


# ------------------------------------------------------------------------------------------------ tela final
@lru_cache(None)
def fundo_final():
    img = Image.new("RGBA", (W, H), (18, 34, 58, 255))
    d = ImageDraw.Draw(img)
    for x in range(0, W, 30):
        d.line((x, 0, x, H), fill=(28, 50, 80))
    for y in range(0, H, 30):
        d.line((0, y, W, y), fill=(28, 50, 80))
    lg = E.logo(380)
    img.alpha_composite(lg, ((W - lg.width) // 2, 230))
    t = E.titulo("ALUGUE NA SUA VEZ", 96, cor=E.AMARELO, larg_max=980)
    img.alpha_composite(t, ((W - t.width) // 2, 560))
    lq = E.leque([JOGOS[k][0] for k in ("bad", "res", "ww", "heat", "dbd")], 360, passo=0.55)
    if lq.width > W - 60:
        lq = lq.resize((W - 60, int(lq.height * (W - 60) / lq.width)), Image.LANCZOS)
    img.alpha_composite(lq, ((W - lq.width) // 2, 720))
    y = 720 + lq.height + 10
    for tx, cor in [("5 dias de jogo · 3 jogos = 7 dias", (255, 255, 255)),
                    ("RESERVE ONLINE · RETIRE EM MAUÁ OU RECEBA EM CASA", E.AMARELO)]:
        tt = E.texto(tx, 40, cor=cor, peso=900, larg_max=980)
        img.alpha_composite(tt, ((W - tt.width) // 2, y))
        y += tt.height + 6
    pl = E.pilula("LINK NA BIO · @SUAVEZ_BG", 46, E.LARANJA, (255, 255, 255), fonte_titulo=True)
    img.alpha_composite(pl, ((W - pl.width) // 2, y + 20))
    return img


def tela_final(dt):
    img = fundo_final().copy()
    a = ease(dt / 0.3)
    if a < 1:
        bl = Image.new("RGBA", (W, H), (255, 255, 255, int(255 * (1 - a))))
        img.alpha_composite(bl)
    return img


# ------------------------------------------------------------------------------------------------ som
def mixa(path):
    n = int(DUR * SR)
    voz = np.zeros(n, np.float32)
    for p in TL:
        a = audio_bruto(p["nome"])
        s = a[int(p["a"] * SR): int(p["a"] * SR) + int(p["dur"] * SR)].copy()
        f = int(0.012 * SR)
        s[:f] *= np.linspace(0, 1, f)
        s[-f:] *= np.linspace(1, 0, f)
        i0 = int(p["ini"] * SR)
        voz[i0:i0 + len(s)] += s[: n - i0]
    voz = voz / (np.percentile(np.abs(voz), 99.7) + 1e-9) * 0.6
    mus = S.musica_chip(DUR + 1)[:n]
    mus = np.pad(mus, (0, n - len(mus))) / (np.abs(mus).max() + 1e-9)
    env = np.convolve(np.abs(voz), np.ones(int(0.25 * SR)) / int(0.25 * SR), "same")
    duck = 1 - 0.65 * np.clip(env / 0.05, 0, 1)
    fx = np.zeros(n)
    for p in TL:
        if p["fase"] in (1, 2, 3, 4, 5) and p["inicio_fase"]:
            S.add(fx, S.sopro(0.4), p["ini"], 0.5)
            S.add(fx, S.bip(1320, 0.07), p["ini"] + 0.05, 0.25)
    for pk, pl in enumerate(PLANOS):
        for e in pl[4]:
            te = src2out(pk, e[1])
            if e[0] == "cx":
                S.add(fx, S.plim(), te, 0.35)
            elif e[0] == "dig":
                S.add(fx, S.estatica(0.18), te, 0.25)
            elif e[0] == "chips":
                for i in range(3):
                    S.add(fx, S.bip(990 + 220 * i, 0.06), te + i * 0.45, 0.25)
    S.add(fx, S.plim(), DUR_FALA, 0.4)
    mix = voz + mus * 0.12 * duck + fx * 0.6
    mix[int(DUR_FALA * SR):] += mus[int(DUR_FALA * SR):] * 0.12
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.89
    st = np.repeat((mix * 32767).astype(np.int16)[:, None], 2, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(st.tobytes())


def loudnorm(src, dst, alvo=-15.5):
    r = subprocess.run([FF, "-hide_banner", "-i", src, "-af", f"loudnorm=I={alvo}:TP=-2:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    i0 = r.rindex("{")
    j = json.loads(r[i0:r.index("}", i0) + 1])
    af = (f"loudnorm=I={alvo}:TP=-2:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
          f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    subprocess.run([FF, "-v", "error", "-y", "-i", src, "-c:v", "copy", "-af", af, "-ar", "44100", "-c:a", "aac",
                    "-b:a", "192k", dst], check=True)


# ------------------------------------------------------------------------------------------------ main
def main():
    os.makedirs(OUT, exist_ok=True)
    print(f"duração: {DUR:.1f} s")
    for p in TL:
        print(f"  {p['nome']} {p['a']:.2f}-{p['b']:.2f} → {p['ini']:.2f} (+{p['dur']:.2f}) fase {p['fase']}")
    base = base_video()
    lb = Leitor(base, (W, H))
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:]]
        ims = []
        for t in sorted(ts):
            b = lb.quadro(min(t, DUR_FALA - 0.04)) if t < DUR_FALA else Image.new("RGB", (W, H))
            ims.append(quadro(b, t).convert("RGB").resize((360, 640)))
        f = Image.new("RGB", (370 * len(ims), 640), (255, 255, 255))
        for i, im in enumerate(ims):
            f.paste(im, (i * 370, 0))
        f.save(os.path.join(OUT, "frames.jpg"), quality=88)
        print("ok frames")
        return
    wav = os.path.join(OUT, "_mix.wav")
    tmp = os.path.join(OUT, "_video.mp4")
    if "--so-final" in sys.argv:
        return finaliza(tmp)
    mixa(wav)
    nf = int(round(DUR * FPS))
    wr = imageio_ffmpeg.write_frames(tmp, (W, H), fps=FPS, codec="libx264", quality=None,
                                     output_params=["-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p"],
                                     audio_path=wav, audio_codec="aac")
    wr.send(None)
    preto = Image.new("RGB", (W, H))
    for i in range(nf):
        t = i / FPS
        b = lb.quadro(t) if t < DUR_FALA else preto
        wr.send(quadro(b, t).convert("RGB").tobytes())
        if i % 150 == 0:
            print(f"  {t:.1f}s")
    wr.close()
    finaliza(tmp)


def finaliza(tmp):
    final = os.path.join(OUT, "videogame_final.mp4")
    loudnorm(tmp, final)
    # versão para o chat (< 30 MB)
    chat = os.path.join(OUT, "videogame_chat.mp4")
    br = int(27 * 8 * 1024 / DUR - 192)
    for ps in (1, 2):
        subprocess.run([FF, "-v", "error", "-y", "-i", final, "-c:v", "libx264", "-b:v", f"{br}k", "-preset", "medium",
                        "-pass", str(ps), "-passlogfile", os.path.join(OUT, "_pass")]
                       + (["-an", "-f", "mp4", "/dev/null"] if ps == 1 else ["-c:a", "copy", chat]), check=True)
    print("ok", final, chat)


if __name__ == "__main__":
    main()
