#!/usr/bin/env python3
"""Reels 1: PREVISÃO DO TEMPO DA CONFRATERNIZAÇÃO (paródia de jornal de TV), narrado por voz de IA (liberada por ele).

Estúdio azul de telejornal, faixa "AO VIVO", mapa do SALÃO DA FESTA (mesa do amigo secreto, buffet, pista, cantinho do
celular) com ícones de tempo desenhados (nuvem, neve, vento, sol). Frente fria de silêncio no amigo secreto → rajadas de
celular → ALERTA: frente quente "SUA VEZ" atravessa o mapa → "imagens do satélite" = cenas REAIS deles jogando →
previsão em cartões (jogos, monitoria, região) → mapa todo de sol "100% DE RISADA" → cartão final com WhatsApp e comenta.
Legenda estilo closed caption da TV (pedaços da fala, tempo proporcional às letras).

    python3 previsao.py --voz          # gera as falas (voz/prev_NN.wav)
    python3 previsao.py --frame 1 5 10 15 20 25 30
    python3 previsao.py                # vídeo (com som / para música) + cópia do chat
"""
import argparse
import math
import os
import random
import subprocess
import sys
import wave
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import comum_festa as C  # noqa: E402
from comum_festa import W, H, FPS, E  # noqa: E402
sys.path.insert(0, os.path.join(C.REPO, "comum"))
from motor import emoji, out_back  # noqa: E402
import sons as S  # noqa: E402  (becas-reels/sons.py)

VOZ = os.path.join(ROOT, "voz")
FALAS = [
    "Boa noite! Agora, a previsão do tempo para a confraternização de fim de ano.",
    "Na mesa do amigo secreto, frente fria de silêncio, com noventa por cento de chance de climão.",
    "No fundo do salão, rajadas fortes de gente olhando o celular.",
    "Mas atenção: uma frente quente está chegando! É a Sua Vez, com jogos de tabuleiro pra todo mundo.",
    "Imagens do satélite mostram risada, gente sentando junto... e ninguém mais no celular.",
    "A gente leva os jogos e fica o evento todo ensinando. No ABC Paulista e em São Paulo capital.",
    "Previsão atualizada: cem por cento de risada. Chama a gente no WhatsApp!",
]
LEGENDA = [
    "Boa noite! Agora, a previsão do tempo para a confraternização de fim de ano.",
    "Na mesa do amigo secreto, frente fria de silêncio, com 90% de chance de climão.",
    "No fundo do salão, rajadas fortes de gente olhando o celular.",
    "Mas atenção: uma frente quente está chegando! É a Sua Vez, com jogos de tabuleiro pra todo mundo.",
    "Imagens do satélite mostram risada, gente sentando junto... e ninguém mais no celular.",
    "A gente leva os jogos e fica o evento todo ensinando. No ABC Paulista e em São Paulo capital.",
    "Previsão atualizada: 100% de risada. Chama a gente no WhatsApp!",
]
LEAD, GAP, TAIL = 0.45, 0.35, 3.4
SR = 44100
AZUL1, AZUL2 = (10, 34, 88), (30, 98, 184)
VERM = (214, 38, 48)
AMA = (255, 205, 40)
BR = (255, 255, 255)
TINTA = (24, 32, 52)


def gera_voz():
    os.makedirs(VOZ, exist_ok=True)
    tts = os.path.join(C.REPO, "hobby-reels", "tts.py")
    for k, f in enumerate(FALAS, 1):
        mp3 = os.path.join(VOZ, f"prev_{k:02d}.mp3")
        subprocess.run([sys.executable, tts, "pt-BR-AntonioNeural", f, mp3, "+10%", "+2Hz"], check=True)
        # voz de TV: corta silêncio das pontas, EQ de presença, compressão e 44,1 kHz mono
        subprocess.run([C.ffmpeg(), "-y", "-loglevel", "error", "-i", mp3, "-af",
                        "silenceremove=start_periods=1:start_threshold=-45dB:stop_periods=-1:stop_threshold=-45dB:"
                        "stop_duration=0.25,highpass=f=90,equalizer=f=3000:t=q:w=1:g=2.5,"
                        "acompressor=threshold=-18dB:ratio=3:attack=5:release=120:makeup=2dB",
                        "-ar", str(SR), "-ac", "1", os.path.join(VOZ, f"prev_{k:02d}.wav")], check=True)
        print("voz", k, flush=True)


def le_wav(p):
    with wave.open(p) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return a


def linha_tempo():
    """Começo e fim de cada fala no vídeo; cenas = fala + folga."""
    t, marcas = LEAD, []
    for k in range(len(FALAS)):
        d = len(le_wav(os.path.join(VOZ, f"prev_{k + 1:02d}.wav"))) / SR
        marcas.append((t, t + d))
        t += d + GAP
    return marcas, t - GAP + TAIL


MARCAS, DUR = (linha_tempo() if os.path.exists(os.path.join(VOZ, "prev_07.wav")) else ([(i * 4.0, i * 4.0 + 3.5)
                                                                                          for i in range(7)], 31.0))


def cena(t):
    """Índice da fala/cena e tempo desde o começo dela."""
    k = 0
    for i, (a, b) in enumerate(MARCAS):
        if t >= a - 0.15:
            k = i
    return k, t - MARCAS[k][0]


def ease(u):
    u = min(1, max(0, u))
    return u * u * (3 - 2 * u)


# ---------------------------------------------------------------- fontes
@lru_cache(None)
def fonte(nome, s, peso=None):
    f = ImageFont.truetype(os.path.join(C.F, nome), s)
    if peso is not None:
        try:
            f.set_variation_by_axes([peso])
        except Exception:
            pass
    return f


def gro(s, peso=700):
    return fonte("SpaceGrotesk.ttf", s, peso)


def anton(s):
    return fonte("Anton-Regular.ttf", s)


# ---------------------------------------------------------------- estúdio de TV
@lru_cache(None)
def estudio():
    y = np.linspace(0, 1, H)[:, None, None]
    x = np.linspace(-1, 1, W)[None, :, None]
    base = np.array(AZUL1, float) * (1 - y) + np.array(AZUL2, float) * y
    luz = np.exp(-((x * 1.2) ** 2 + ((y - 0.35) * 2.2) ** 2)) * 60
    a = np.clip(base + luz, 0, 255)
    img = Image.fromarray(np.broadcast_to(a, (H, W, 3)).astype(np.uint8)).convert("RGBA")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for k in range(-12, 20):  # faixas diagonais largas e bem suaves (cenário de estúdio)
        x0 = k * 160
        d.polygon([(x0, 0), (x0 + 60, 0), (x0 + 760, H), (x0 + 700, H)], fill=(255, 255, 255, 9))
    img.alpha_composite(lay)
    return img


def faixa_tv(img, t, titulo="PREVISÃO DO TEMPO", sub="CONFRATERNIZAÇÃO DE FIM DE ANO"):
    """Tarja da TV no alto: AO VIVO + relógio + título."""
    d = ImageDraw.Draw(img)
    d.rectangle((0, 150, 640, 228), fill=VERM)
    d.text((40, 189), titulo, font=anton(54), fill=BR, anchor="lm")
    d.rectangle((0, 228, 820, 282), fill=BR)
    d.text((40, 255), sub, font=gro(34, 700), fill=TINTA, anchor="lm")
    vivo = int(t * 2) % 2 == 0
    d.rounded_rectangle((40, 92, 230, 136), 8, fill=(0, 0, 0, 140))
    d.ellipse((56, 104, 76, 124), fill=VERM if vivo else (110, 20, 26))
    d.text((88, 114), "AO VIVO", font=gro(30, 800), fill=BR, anchor="lm")
    d.text((250, 114), "21:47", font=gro(30, 700), fill=BR, anchor="lm")
    lg = C.kit.logo(140)
    img.alpha_composite(lg, (W - lg.width - 36, 60))


def legenda(img, t):
    """Closed caption da TV: pedaço da fala atual (tempo proporcional às letras)."""
    for k, (a, b) in enumerate(MARCAS):
        if a - 0.05 <= t <= b + 0.25:
            txt = LEGENDA[k]
            partes = pedacos(txt)
            tot = sum(len(p) for p in partes)
            u = (t - a) / max(0.1, b - a) * tot
            acc = 0
            for p in partes:
                acc += len(p)
                if u <= acc:
                    break
            f = gro(44, 700)
            d = ImageDraw.Draw(img)
            linhas = quebra(p, f, 900)
            hh = 60 * len(linhas) + 24
            y0 = 1600 - hh
            for i, ln in enumerate(linhas):
                tw = d.textlength(ln, font=f)
                d.rectangle((W / 2 - tw / 2 - 16, y0 + i * 60, W / 2 + tw / 2 + 16, y0 + i * 60 + 60), fill=(0, 0, 0, 205))
                d.text((W / 2, y0 + i * 60 + 30), ln, font=f, fill=BR, anchor="mm")
            return


def pedacos(txt, n=34):
    ws, out, cur = txt.split(), [], ""
    for w in ws:
        if len(cur) + len(w) + 1 > n and cur:
            out.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    out.append(cur)
    return out


def quebra(txt, f, larg):
    d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    ws, linhas, cur = txt.split(), [], ""
    for w in ws:
        tst = (cur + " " + w).strip()
        if d.textlength(tst, font=f) > larg and cur:
            linhas.append(cur)
            cur = w
        else:
            cur = tst
    linhas.append(cur)
    return linhas


# ---------------------------------------------------------------- ícones de tempo (desenhados)
@lru_cache(None)
def nuvem(w=260, cor=(240, 244, 250), escura=False):
    h = int(w * 0.62)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = (150, 160, 178) if escura else cor
    for (cx, cy, r) in ((0.30, 0.62, 0.22), (0.52, 0.45, 0.28), (0.74, 0.62, 0.21), (0.5, 0.7, 0.24)):
        d.ellipse((w * (cx - r), h * cy - w * r, w * (cx + r), h * cy + w * r), fill=c + (255,))
    d.rectangle((w * 0.12, h * 0.62, w * 0.88, h * 0.92), fill=c + (255,))
    sh = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    m = im.getchannel("A").point(lambda v: int(v * 0.35))
    sh.paste((0, 0, 0, 255), (14, 18), m)
    sh = sh.filter(ImageFilter.GaussianBlur(8))
    sh.alpha_composite(im, (0, 0))
    return sh


def floco(d, x, y, r, cor=(210, 235, 255)):
    for k in range(6):
        a = k * math.pi / 3
        d.line((x, y, x + r * math.cos(a), y + r * math.sin(a)), fill=cor, width=6)
        bx, by = x + r * 0.6 * math.cos(a), y + r * 0.6 * math.sin(a)
        for s in (-1, 1):
            d.line((bx, by, bx + r * 0.28 * math.cos(a + s * 0.8), by + r * 0.28 * math.sin(a + s * 0.8)), fill=cor,
                   width=5)


@lru_cache(None)
def sol(r=110):
    im = Image.new("RGBA", (r * 4, r * 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = r * 2
    for k in range(12):
        a = k * math.tau / 12
        d.polygon([(c + r * 1.25 * math.cos(a - 0.12), c + r * 1.25 * math.sin(a - 0.12)),
                   (c + r * 1.75 * math.cos(a), c + r * 1.75 * math.sin(a)),
                   (c + r * 1.25 * math.cos(a + 0.12), c + r * 1.25 * math.sin(a + 0.12))], fill=(255, 196, 40, 255))
    g = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse((c - r * 1.3, c - r * 1.3, c + r * 1.3, c + r * 1.3), fill=(255, 220, 90, 130))
    im = Image.alpha_composite(g.filter(ImageFilter.GaussianBlur(18)), im)
    d = ImageDraw.Draw(im)
    d.ellipse((c - r, c - r, c + r, c + r), fill=(255, 210, 50, 255), outline=(240, 150, 20, 255), width=6)
    return im


def badge(txt, sub, cor):
    f1, f2 = anton(84), gro(30, 800)
    d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    w = int(max(d0.textlength(txt, font=f1), d0.textlength(sub, font=f2)) + 70)
    im = Image.new("RGBA", (w + 20, 170), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((6, 10, w + 14, 166), 24, fill=(0, 0, 0, 90))
    d.rounded_rectangle((0, 0, w, 156), 24, fill=cor + (255,), outline=BR + (255,), width=5)
    d.text((w / 2, 62), txt, font=f1, fill=BR, anchor="mm")
    d.text((w / 2, 124), sub, font=f2, fill=BR, anchor="mm")
    return im


# ---------------------------------------------------------------- mapa do salão
MX, MY, MW, MH = 70, 360, 940, 960  # painel do mapa


@lru_cache(None)
def mapa_base(ensolarado=False):
    im = Image.new("RGBA", (MW, MH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, MW - 1, MH - 1), 34, fill=(18, 60, 120, 255), outline=(170, 210, 255, 255), width=5)
    terra = (140, 196, 120) if not ensolarado else (156, 210, 110)
    terra2 = (120, 176, 104) if not ensolarado else (140, 196, 96)
    # "continente" = piso do salão com contorno irregular
    rnd = random.Random(5)
    pts = []
    for k in range(60):
        a = k * math.tau / 60
        r = 1 + 0.05 * math.sin(3 * a) + 0.03 * rnd.uniform(-1, 1)
        pts.append((MW / 2 + 400 * r * math.cos(a), MH / 2 + 420 * r * math.sin(a)))
    d.polygon(pts, fill=terra + (255,), outline=(60, 110, 70, 255))
    regioes = {  # nome: (caixa)
        "MESA DO AMIGO SECRETO": (150, 170, 560, 420),
        "BUFFET": (600, 190, 800, 360),
        "PISTA": (170, 500, 430, 760),
        "CANTINHO DO CELULAR": (480, 520, 800, 760),
    }
    for nome, (a, b, c, e) in regioes.items():
        d.rounded_rectangle((a, b, c, e), 26, fill=terra2 + (255,), outline=(60, 110, 70, 255), width=3)
        d.text(((a + c) / 2, e - 26), nome, font=gro(26, 800), fill=(30, 60, 40), anchor="mm")
    # mesa do amigo secreto com cadeirinhas
    d.rounded_rectangle((250, 250, 460, 320), 18, fill=(196, 150, 100, 255), outline=(110, 70, 40, 255), width=3)
    for k in range(5):
        for yy in (228, 342):
            d.ellipse((258 + k * 44, yy - 12, 282 + k * 44, yy + 12), fill=(110, 70, 40, 255))
    d.text((MW / 2, MH - 44), "SALÃO DA FESTA", font=anton(48), fill=BR, anchor="mm")
    return im


REG = {"amigo": (355, 285), "buffet": (700, 270), "pista": (300, 620), "celular": (640, 630)}


def no_mapa(x, y):
    return MX + x, MY + y


def cena_mapa(img, t, k, u):
    ens = k >= 6
    mp = mapa_base(ens).copy()
    dm = ImageDraw.Draw(mp)
    if k <= 2 or (k == 3 and u < 0.6):
        # frente fria no amigo secreto (cena 2 em diante)
        if k >= 1:
            a = ease((t - MARCAS[1][0]) / 0.5)
            cx, cy = REG["amigo"]
            n = nuvem(300, escura=True)
            mp.alpha_composite(n, (int(cx - 150), int(cy - 230 - 20 * (1 - a))))
            for i in range(5):  # neve caindo
                fx = cx - 120 + i * 60
                fy = cy - 40 + ((t * 70 + i * 37) % 120)
                floco(dm, fx, fy, 16)
            # linha de frente fria (azul com triângulos)
            for i in range(9):
                x0 = 120 + i * 50
                dm.line((x0, 450, x0 + 50, 450 + 10 * math.sin(i)), fill=(40, 110, 230), width=7)
                dm.polygon([(x0 + 12, 448), (x0 + 38, 448), (x0 + 25, 424)], fill=(40, 110, 230))
        if k >= 2:  # vento no cantinho do celular
            cx, cy = REG["celular"]
            for i in range(4):
                off = (t * 260 + i * 90) % 360
                y = cy - 80 + i * 40
                pts = [(cx - 160 + off * 0.3 + j * 20, y + 10 * math.sin(j * 0.7 + t * 4)) for j in range(12)]
                dm.line(pts, fill=(235, 245, 255), width=6)
            # celularzinho
            dm.rounded_rectangle((cx + 60, cy - 120, cx + 120, cy - 20), 10, fill=(30, 30, 40), outline=BR, width=3)
            dm.rectangle((cx + 68, cy - 108, cx + 112, cy - 34), fill=(120, 200, 255))
    if k == 3 and u > 0.6:  # frente quente Sua Vez atravessando
        v = ease((u - 0.6) / 2.4)
        xf = -60 + v * (MW + 260)
        pts = [(xf + 30 * math.sin(yy / 90), yy) for yy in range(80, MH - 60, 20)]
        dm.line(pts, fill=(230, 50, 40), width=9)
        for yy in range(100, MH - 80, 70):
            x = xf + 30 * math.sin(yy / 90)
            dm.pieslice((x - 4, yy - 22, x + 40, yy + 22), -90, 90, fill=(230, 50, 40))
        lg = C.kit.logo(170)
        mp.alpha_composite(lg, (int(xf - lg.width / 2), int(MH / 2 - lg.height / 2)))
    if k == 3 and u > 0.6:  # sóis nascendo onde a frente já passou
        xf = -60 + ease((u - 0.6) / 2.4) * (MW + 260)
        for i, (nm, (cx, cy)) in enumerate(REG.items()):
            if cx < xf - 60:
                s = sol(60)
                mp.alpha_composite(s, (int(cx - s.width / 2), int(cy - 60 - s.height / 2)))
    if ens:
        for i, (nm, (cx, cy)) in enumerate(REG.items()):
            a = 1.0 if u > 0 else 0
            s = sol(70)
            if a > 0:
                s2 = s.resize((int(s.width * a), int(s.height * a)))
                mp.alpha_composite(s2, (int(cx - s2.width / 2), int(cy - 60 - s2.height / 2)))
    img.alpha_composite(mp, (MX, MY))
    if k == 1:
        a = ease((u - 0.9) / 0.3)
        if a > 0:
            E.cola(img, badge("90%", "DE CHANCE DE CLIMÃO", (40, 110, 230)), 700, 1400, 3, out_back(a), 1)
            E.cola(img, badge("8°", "NA MESA", (60, 80, 120)), 230, 1405, -4, out_back(ease((u - 1.5) / 0.3)), 1)
    if k == 2:
        a = ease((u - 0.6) / 0.3)
        if a > 0:
            E.cola(img, badge("120 km/h", "RAJADAS DE CELULAR", (90, 100, 130)), 640, 1400, 3, out_back(a), 1)
    if ens:
        a = ease((u - 0.8) / 0.35)
        if a > 0:
            E.cola(img, badge("100%", "DE RISADA", (240, 140, 20)), W // 2, 1400, -3, out_back(a), 1)


def alerta(img, t, u):
    """Faixa de ALERTA (cena 4, começo)."""
    if u > 2.6:
        return
    pisca = int(u * 6) % 2 == 0
    fx = Image.new("RGBA", (W, 150), (0, 0, 0, 0))
    d = ImageDraw.Draw(fx)
    for i in range(-2, 30):
        d.polygon([(i * 60, 0), (i * 60 + 30, 0), (i * 60 - 30, 150), (i * 60 - 60, 150)], fill=(20, 20, 20, 255))
    d.rectangle((0, 0, W, 150), outline=(20, 20, 20, 255), width=6)
    base = Image.new("RGBA", (W, 150), AMA + (255,))
    base.alpha_composite(fx)
    d = ImageDraw.Draw(base)
    d.rectangle((110, 26, W - 110, 124), fill=AMA if pisca else (255, 240, 160))
    d.text((W / 2, 76), "ALERTA: FRENTE QUENTE!", font=anton(70), fill=(20, 20, 20), anchor="mm")
    a = ease(u / 0.25)
    img.alpha_composite(base, (0, int(1340 - 40 * (1 - a))))


@lru_cache(None)
def moldura_sat(w=900, h=1060):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 28, outline=(170, 230, 255, 255), width=6)
    for (x, y, sx, sy) in ((30, 30, 1, 1), (w - 30, 30, -1, 1), (30, h - 30, 1, -1), (w - 30, h - 30, -1, -1)):
        d.line((x, y, x + 60 * sx, y), fill=AMA + (255,), width=6)
        d.line((x, y, x, y + 60 * sy), fill=AMA + (255,), width=6)
    return im


SAT = [("critter", 1.0, 2.1, "COZINHA AGITADA"), ("art", 0.6, 2.1, "LEILÃO DISPUTADO"), ("passaporte", 1.0, 2.1,
                                                                                         "TODO MUNDO JUNTO")]


def cena_satelite(img, t, u):
    d0 = max(1.0, (MARCAS[4][1] - MARCAS[4][0] + GAP) / len(SAT))
    i = min(len(SAT) - 1, int(u / d0))
    nome, t0, dd, rot = SAT[i]
    uu = min(dd - 0.05, (u - i * d0) * (dd / d0))
    q = C.clip(nome, t0, dd, uu)
    w, h = 900, 1060
    z = 1.0 + 0.04 * (uu / dd)
    q = q.resize((int(W * z), int(H * z)))
    cx, cy = q.width // 2, int(q.height * 0.52)
    q = q.crop((cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2))
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 28, fill=255)
    x0, y0 = (W - w) // 2, 330
    img.paste(q, (x0, y0), m)
    img.alpha_composite(moldura_sat(w, h), (x0, y0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x0 + 30, y0 + 100, x0 + 470, y0 + 160), 12, fill=(0, 0, 0, 160))
    d.text((x0 + 50, y0 + 130), "SATÉLITE SUA VEZ-1", font=gro(32, 800), fill=(170, 230, 255), anchor="lm")
    d.rounded_rectangle((x0 + 30, y0 + h - 170, x0 + 30 + d.textlength(rot, font=anton(52)) + 40, y0 + h - 100), 12,
                        fill=VERM)
    d.text((x0 + 50, y0 + h - 135), rot, font=anton(52), fill=BR, anchor="lm")
    if (u - i * d0) < 0.12:  # flash de troca
        img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(200 * (1 - (u - i * d0) / 0.12)))))


PREV = [("🎲", "JOGOS", "a gente leva"), ("🙋", "MONITORIA", "o evento todo"), ("📍", "ONDE", "ABC + SP capital")]


def cena_cartoes(img, t, u):
    d = ImageDraw.Draw(img)
    d.text((W / 2, 420), "PREVISÃO PARA O SEU EVENTO", font=anton(64), fill=BR, anchor="mm")
    for i, (em, tit, sub) in enumerate(PREV):
        a = ease((u - 0.25 - 0.45 * i) / 0.35)
        if a <= 0:
            continue
        c = Image.new("RGBA", (290, 520), (0, 0, 0, 0))
        dc = ImageDraw.Draw(c)
        dc.rounded_rectangle((0, 0, 289, 519), 30, fill=(255, 255, 255, 235), outline=AMA + (255,), width=6)
        c.alpha_composite(emoji(em, 130), (80, 50))
        dc.text((145, 270), tit, font=anton(52), fill=TINTA, anchor="mm")
        for j, ln in enumerate(quebra(sub, gro(36, 700), 250)):
            dc.text((145, 350 + j * 46), ln, font=gro(36, 700), fill=(40, 90, 170), anchor="mm")
        E.cola(img, c, 190 + i * 350, 820, (-3, 0, 3)[i], out_back(a), 1)


def cena_cta(img, t, u):
    d = ImageDraw.Draw(img)
    d.text((W / 2, 420), "PREVISÃO DO SEU EVENTO:", font=anton(66), fill=BR, anchor="mm")
    d.text((W / 2, 540), "100% DE RISADA", font=anton(120), fill=AMA, anchor="mm", stroke_width=5,
           stroke_fill=(20, 40, 90))
    c = E.bloco(900, 520, (255, 255, 255), raio=34, ow=6, sombra=12).copy()
    dc = ImageDraw.Draw(c)
    dc.text((450, 80), "EVENTOS DE FIM DE ANO", font=anton(58), fill=VERM, anchor="mm")
    dc.text((450, 160), "Amigo secreto, firma, família, aniversário:", font=gro(36, 700), fill=TINTA, anchor="mm")
    dc.text((450, 210), "a gente leva os jogos e fica o evento", font=gro(36, 700), fill=TINTA, anchor="mm")
    dc.text((450, 258), "todo ensinando.", font=gro(36, 700), fill=TINTA, anchor="mm")
    dc.text((450, 320), "ABC PAULISTA E SÃO PAULO CAPITAL", font=gro(34, 800), fill=(40, 90, 170), anchor="mm")
    dc.rounded_rectangle((60, 380, 840, 470), 26, fill=(30, 150, 80))
    dc.text((450, 425), f"ORÇAMENTO: WHATSAPP {C.WHATS}", font=gro(40, 800), fill=BR, anchor="mm")
    a = ease(u / 0.35)
    E.cola(img, c, W // 2, 940, 0, out_back(a), 1)
    b = ease((u - 0.8) / 0.3)
    if b > 0:
        p = E.pilula("COMENTA: QUAL EVENTO SEU PRECISAVA DE JOGOS?", 36, AMA, (20, 30, 60))
        E.cola(img, p, W // 2, 1300, -2, out_back(b), 1)


def frame(fi):
    t = fi / FPS
    img = estudio().copy()
    k, u = cena(t)
    if t < MARCAS[0][0] + 0.9:  # gancho: título enorme antes do mapa
        a = ease(t / 0.3)
        faixa_tv(img, t)
        d = ImageDraw.Draw(img)
        d.text((W / 2, 700), "PREVISÃO DO TEMPO", font=anton(120), fill=BR, anchor="mm")
        d.text((W / 2, 840), "PRA SUA CONFRATERNIZAÇÃO", font=anton(76), fill=AMA, anchor="mm")
        E.cola(img, nuvem(330, escura=True), 300, 1080, 0, out_back(a), 1)
        E.cola(img, sol(80), 760, 1060, 0, out_back(ease((t - 0.2) / 0.3)), 1)
    elif k <= 3:
        faixa_tv(img, t)
        cena_mapa(img, t, k, u)
        if k == 3:
            alerta(img, t, u)
    elif k == 4:
        faixa_tv(img, t, "IMAGENS DO SATÉLITE", "TEMPO REAL · SALÃO DA FESTA")
        cena_satelite(img, t, u)
    elif k == 5:
        faixa_tv(img, t)
        cena_cartoes(img, t, u)
    elif u < 2.4:
        faixa_tv(img, t, "PREVISÃO ATUALIZADA")
        cena_mapa(img, t, 6, u)
    else:
        faixa_tv(img, t, "PREVISÃO ATUALIZADA")
        cena_cta(img, t, u - 2.4)
    legenda(img, t)
    return img.convert("RGB")


def render(fi):
    return frame(fi).tobytes()


# ---------------------------------------------------------------- som
def vinheta():
    """Vinheta de telejornal: acorde de metais sintéticos + sino."""
    o = np.zeros(int(2.2 * SR))
    t = S.t_(1.8)
    for f in (392, 493.9, 587.3, 784):
        s = sum(np.sin(2 * np.pi * f * h * t) / h for h in (1, 2, 3, 4)) * np.minimum(1, t / 0.03) * np.exp(-t * 1.6)
        S.add(o, s, 0.0, 0.12)
    S.add(o, S.sino(), 0.0, 0.5)
    return o


def trilha(dur):
    """Base de 'previsão do tempo': pad leve + baixo e marimba em 104 bpm (sem direitos autorais)."""
    n = int(dur * SR)
    out = np.zeros(n + SR * 2)
    b = 60 / 104
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)  # noqa: E731
    acordes = [(55, [67, 71, 74]), (52, [64, 67, 71]), (48, [64, 67, 72]), (50, [66, 69, 74])]
    t, k = 0.0, 0
    while t < dur:
        r, ac = acordes[k % 4]
        for j in range(4):
            S.add(out, S.baixo(hz(r - 12 + (7 if j == 2 else 0)), b * 0.9), t + j * b, 0.35)
            S.add(out, S.marimba(hz(ac[(j + k) % 3] + 12), b), t + j * b + b / 2, 0.16)
        for m in ac:
            S.add(out, S.rhodes(hz(m), 4 * b), t, 0.06)
        t += 4 * b
        k += 1
    return out[:n]


def audio():
    n = int(DUR * SR)
    voz = np.zeros(n)
    for k, (a, b) in enumerate(MARCAS):
        v = le_wav(os.path.join(VOZ, f"prev_{k + 1:02d}.wav"))
        S.add(voz, v, a, 1.0)
    m = trilha(DUR)
    env = np.convolve((np.abs(voz) > 0.02).astype(float), np.ones(int(0.3 * SR)) / int(0.3 * SR), "same")
    m = m / (np.abs(m).max() + 1e-9) * (0.32 - 0.2 * np.clip(env * 3, 0, 1))
    fx = np.zeros(n)
    S.add(fx, vinheta(), 0.0, 0.7)
    S.add(fx, S.sopro(0.6), MARCAS[1][0] + 0.1, 0.4)
    S.add(fx, S.estatica(0.5), MARCAS[2][0] + 0.1, 0.15)
    for i in range(6):
        S.add(fx, S.bip(1500 if i % 2 else 1100, 0.12), MARCAS[3][0] + i * 0.36, 0.35)
    d0 = max(1.0, (MARCAS[4][1] - MARCAS[4][0] + GAP) / len(SAT))
    for i in range(len(SAT)):
        S.add(fx, S.obturador(), MARCAS[4][0] + i * d0, 0.5)
    for i in range(3):
        S.add(fx, S.plim(), MARCAS[5][0] + 0.25 + 0.45 * i, 0.4)
    S.add(fx, vinheta(), MARCAS[6][0] + 2.4, 0.5)
    os.makedirs(C.OUT, exist_ok=True)
    com, sem = os.path.join(C.OUT, "prev_com.wav"), os.path.join(C.OUT, "prev_sem.wav")
    for p, mus in ((com, m), (sem, None)):
        mix = voz * 0.9 + fx * 0.6 + (mus if mus is not None else 0)
        mix = mix / (np.abs(mix).max() + 1e-9) * 0.8
        st = np.repeat((mix * 32767).astype(np.int16)[:, None], 2, 1)
        with wave.open(p, "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(st.tobytes())
    return com, sem


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voz", action="store_true")
    ap.add_argument("--frame", nargs="*", type=float)
    a = ap.parse_args()
    if a.voz:
        gera_voz()
        return
    C.prepara([(n, t0, d) for n, t0, d, _ in SAT])
    os.makedirs(C.OUT, exist_ok=True)
    if a.frame:
        C.folha([frame(int(x * FPS)) for x in a.frame], os.path.join(C.OUT, "frames_prev.jpg"))
        print("DUR", round(DUR, 2), [tuple(round(v, 2) for v in m) for m in MARCAS])
        return
    com, sem = audio()
    C.entrega("previsao", DUR, render, com, sem)
    print(C.chat(os.path.join(C.OUT, "previsao_com_som_final.mp4")))
    print(C.chat(os.path.join(C.OUT, "previsao_para_musica_final.mp4")))


if __name__ == "__main__":
    main()
