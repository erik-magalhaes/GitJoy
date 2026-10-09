#!/usr/bin/env python3
"""Reels "jogos para crianças", com o material GRAVADO PELO DONO (pasta brutos/, fora do git):

- v0.mp4 (Drive, 1:10): ele falando na frente da estante (várias tentativas; uso só as boas);
- v1–v3 Go Cuckoo, v4–v5 Scooby-Doo, v6–v7 Gravity Superstar, v8 Draftosaurus (cenas dos jogos).

Montagem curta (~33 s): gancho em cima da cena do Go Cuckoo; em cada jogo, ele aparece falando (com a boca
sincronizada) e corta para as cenas do jogo enquanto a fala continua; legenda pelas palavras; "comenta"; CTA.

    python3 criancas.py --frame 1 5 12      # quadros de teste em out/frames.jpg
    python3 criancas2.py                    # out/criancas2_com_legenda.mp4 e out/criancas2_sem_legenda.mp4

2ª GRAVAÇÃO (brutos/novos/, ele refez com o microfone mais baixo): gancho novo (20261009_182144) e todas as falas numa
tomada só (20261009_182216), uso a ÚLTIMA tentativa boa de cada uma. Edição "adulta" com efeitos do jogo por cima das
cenas da mesa (ovos caindo no Go Cuckoo, estrelas no Gravity, pegadas no Draftosaurus, névoa e fantasma no Scooby).
"""
import argparse
import json
import math
import os
import subprocess
import sys

import numpy as np
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "..", "comum"))
from motor import (W, H, FPS, WHITE, seg, ease, lerp, pop, quica, font, emoji, logo_card, cola, sombra, letreiro, pilula,  # noqa
                   folha, ffmpeg)
import som  # noqa: E402

BR = os.path.join(ROOT, "brutos")
OUT = os.path.join(ROOT, "out")
INK = (20, 16, 30)
AMARELO = (255, 214, 70)
# voz: o celular grava "embolado" (+8 dB em 120-500 Hz e -14 dB acima de 4 kHz, medido) e com eco da sala.
# Tira o grave embolado, devolve presença e ar, segura o eco entre as palavras (gate suave) e comprime.
# 2ª versão (a 1ª ficou "horrível": EQ/realce/gate exagerados na voz e cor estourada nos jogos).
# Agora é mão leve: a voz do celular quase não é mexida, só limpa o grave e nivela; a imagem só corrige um pouco.
# 3ª versão do som (ele: "o áudio tá esquisito, eu usei microfone"). Medido: o microfone vem muito grave/abafado
# (+8 a +13 dB em 100–500 Hz e −18 dB acima de 4 kHz, em relação a 500–2000 Hz) e o loudnorm dinâmico "bombeava" o volume.
# Agora: tira o embolado com mão moderada, devolve um pouco de clareza, SEM compressor/loudnorm dinâmico; o nível de cada
# fala é ajustado com ganho fixo (nivela()) e a mixagem não satura mais a voz (som.build(..., satura=False)).
VOZ_CADEIA = ("volume=-9dB,highpass=f=90,equalizer=f=140:t=q:w=1:g=-2,equalizer=f=320:t=q:w=1.3:g=-4,"
              "equalizer=f=3200:t=q:w=1.4:g=2,highshelf=f=6000:g=2")
# acabamento "HD" (pedido dele, sem estourar cor): denoise forte para o ruído do celular, curva que segura os brancos
# (estouro caiu de ~5% para ~0,3%), nitidez só na luz (sem halo de cor), vinheta bem leve e saturação no lugar.
GRADE = ("hqdn3d=2.5:2:5:5,curves=all='0/0.012 0.25/0.245 0.5/0.52 0.75/0.775 1/0.98',"
         "eq=contrast=1.02:saturation=0.97:gamma=1.04,unsharp=5:5:0.55:5:5:0.0,vignette=angle=PI/14")
GRADE_ROSTO = ("hqdn3d=2.5:2:5:5,curves=all='0/0.012 0.25/0.245 0.5/0.52 0.75/0.775 1/0.98',"
               "eq=contrast=1.02:saturation=0.95:gamma=1.05,unsharp=5:5:0.45:5:5:0.0,vignette=angle=PI/14")
# falas boas (arquivo, início, fim) e o texto que ele falou; o início é a 1ª palavra (sem a puxada de ar antes)
ROSTO = "novos/20261009_182216.mp4"  # tomada com as falas
HOOK = "novos/20261009_182144.mp4"   # gancho: ele pertinho da câmera e depois a abertura
ROSTOS = (ROSTO, HOOK)
INTRO = (HOOK, (3.64, 8.35), "Hoje eu vim te indicar 4 ótimos jogos pra brincar com os piticos no Dia das Crianças!")
FALAS = [
    ("Go Cuckoo!", (ROSTO, 1.48, 7.60), "E o primeiro desses jogos é o Go Cuckoo, um jogo onde a gente precisa criar um "
                                         "ninho pra Kiki conseguir colocar os ovos dela."),
    ("Gravity Superstar", (ROSTO, 14.56, 21.55), "Já o segundo é o Gravity Superstars, um jogo onde viramos aventureiros "
                                                  "espaciais precisando capturar algumas estrelas."),
    ("Draftosaurus", (ROSTO, 48.43, 53.50), "Já o terceiro é o Draftosaurus, um jogo onde montamos o nosso próprio parque "
                                             "dos dinossauros."),
    ("Scooby-Doo!", (ROSTO, 74.84, 81.45), "E por último, mas não menos importante, separamos o Scooby-Doo, um jogo que une "
                                            "toda a família pra derrotar o monstro da semana."),
]
FINAL = (ROSTO, (85.24, 89.75), "Todos esses jogos já estão disponíveis lá na Sua Vez. Corre que o link tá na bio!")
FALA_ROSTO = 1.3  # ele falando (a capa aparece pequena no canto quando ele diz o nome) → o jogo na mesa com as
# fichas → volta pra ele, ainda com a capa no canto (sem tampar o rosto)
NOMES = [("cuckoo", "go"), ("gravity",), ("draftosaurus",), ("scooby", "scooby-doo")]
# cada trecho de cena é usado UMA vez só (ele reclamou de cenas repetidas): (arquivo, início)
CENAS = [[("v2.mp4", 1.6), ("v3.mp4", 9.0)], [("v7.mp4", 1.0), ("v6.mp4", 3.5)],  # 2 cenas do jogo por fala,
         [("v8.mp4", 2.2), ("v8.mp4", 7.0)], [("v4.mp4", 1.6), ("v5.mp4", 3.0)]]  # cada trecho usado uma vez
RESPIRO = 0.7  # o jogo fica um pouco na tela depois da fala, antes do próximo
OLHA = {}  # ex.: {3: (0.5, "v4.mp4", 0.2)} cobre o giro dele no Scooby; ele pediu para DEIXAR o giro
# fichas de cada jogo (edições atuais: Go Cuckoo da Devir 2023, Sit Down!, MeepleBR, CMON)
INFO = [("2 a 5 jogadores", "a partir de 5 anos", "15 min", "DESTREZA", (236, 72, 153)),
        ("2 a 6 jogadores", "a partir de 7 anos", "20 min", "CORRIDA ESPACIAL", (99, 102, 241)),
        ("2 a 5 jogadores", "a partir de 8 anos", "15 min", "MONTE SEU PARQUE", (22, 163, 74)),
        ("1 a 5 jogadores", "a partir de 10 anos", "30 min", "COOPERATIVO", (14, 165, 233))]
# gancho (pedido dele): a ÚLTIMA vez que ele chega pertinho da câmera ajeitando, com um movimento de câmera de efeito
GANCHO_ARQ, GANCHO_INI, GANCHO = HOOK, 1.85, 1.79  # começa ele JÁ mexendo na câmera
INTRO_ROSTO = 1.9  # na fala de abertura, depois disso entra uma montagem rápida dos 4 jogos
MONTAGEM = [("v1.mp4", 1.0), ("v6.mp4", 0.5), ("v8.mp4", 11.5), ("v4.mp4", 6.0)]
COMENTA = 2.6
CTA = 3.6


def linha_do_tempo():
    """Planos [(t0, dur, arquivo, início no arquivo)] e falas [(índice, t0, dur)] (índice -1 = abertura)."""
    planos, voz = [], []
    a, b = INTRO[1]
    planos.append((0.0, GANCHO + INTRO_ROSTO, GANCHO_ARQ, GANCHO_INI))  # gancho e abertura: mesma tomada
    voz.append((-1, GANCHO, b - a))
    resto = (b - a) - INTRO_ROSTO + 0.2  # cobre também a pausa de 0,2 s antes da 1ª fala (sem buraco na imagem)
    for j, (arq, ini) in enumerate(MONTAGEM):
        dd = resto / len(MONTAGEM)
        planos.append((GANCHO + INTRO_ROSTO + j * dd, dd, arq, ini))
    t = GANCHO + (b - a) + 0.2
    fichas, caixas = [], []
    pals = json.load(open(os.path.join(ROOT, "palavras2.json"), encoding="utf-8"))
    for k, (_, (arq0, a, b), _) in enumerate(FALAS):
        d = b - a
        voz.append((k, t, d))
        # a capa pequena aparece quando ele FALA o nome do jogo e fica até o fim da fala (só nos planos dele)
        tn = next(w0 for w, w0, _ in pals[k + 1] if w.strip(",.!").lower() in NOMES[k])
        ta = min(max(FALA_ROSTO, tn + 0.9), d - 3.2)
        if k in OLHA:  # ele ainda está virado no começo da fala: cobre com o jogo até ele olhar pra câmera
            off, c0, i0 = OLHA[k]
            planos.append((t, off, c0, i0))
            planos.append((t + off, ta - off, arq0, a + off))
        else:
            planos.append((t, ta, arq0, a))                 # ele apresenta o jogo (rosto livre, capa no canto)
        caixas.append((t + min(tn, ta - 0.6), t + ta, k))
        resto = d - ta + RESPIRO                           # daqui até o próximo jogo: SÓ o jogo na mesa
        (c1, i1), (c2, i2) = CENAS[k]
        d1 = resto * 0.48
        planos.append((t + ta, d1, c1, i1))
        fichas.append((t + ta, resto, k))  # nome e fichas nas duas cenas do jogo
        planos.append((t + ta + d1, resto - d1, c2, i2))
        t += d + RESPIRO
    planos.append((t, COMENTA, "v5.mp4", 5.6))
    t += COMENTA
    a, b = FINAL[1]
    voz.append((4, t, b - a))
    planos.append((t, b - a + 0.25, ROSTO, a))  # ele chamando para o link da bio
    t += b - a + 0.25
    planos.append((t, CTA, "mosaico", 0.0))
    t += CTA
    return planos, voz, t, fichas, caixas


def fala(k):
    """(arquivo, início, fim, texto) da fala k (-1 = abertura)."""
    if k < 0:
        return INTRO[0], INTRO[1][0], INTRO[1][1], INTRO[2]
    if k == 4:
        return FINAL[0], FINAL[1][0], FINAL[1][1], FINAL[2]
    nome, (arq, a, b), txt = FALAS[k]
    return arq, a, b, txt


PLANOS, VOZ, DUR, FICHAS, CAIXAS_T = linha_do_tempo()
TC = VOZ[4][1] + VOZ[4][2] + RESPIRO  # começo do "comenta" (depois do último jogo)
TF = TC + COMENTA                     # ele fala o CTA
TA = VOZ[5][1] + VOZ[5][2] + 0.25     # tela final


# palavras com os tempos reais (faster-whisper medium, revisadas): palavras2.json, uma lista por fala de VOZ
CORRIGE = {"kiki": "Kiki", "Scooby": "Scooby-Doo", "-Doo": None, "para": "pra"}


def subs():
    """Legenda estilo Reels: 1 a 3 palavras por vez, palavra falada em amarelo (tempos reais da voz)."""
    pals = json.load(open(os.path.join(ROOT, "palavras2.json"), encoding="utf-8"))
    out = []
    for (k, t0, d), ws in zip(VOZ, pals):
        ws = [(CORRIGE.get(w, w), a, b) for w, a, b in ws]
        ws = [(w, t0 + a, t0 + b) for w, a, b in ws if w]
        grupos, cur = [], []
        for w in ws:
            cur.append(w)
            if len(cur) == 3 or len(" ".join(x[0] for x in cur)) > 14 or w[0][-1] in ",.!?":
                grupos.append(cur)
                cur = []
        if cur:
            grupos.append(cur)
        for j, g in enumerate(grupos):
            fim = grupos[j + 1][0][1] if j + 1 < len(grupos) else min(g[-1][2] + 0.3, t0 + d)
            out.append((g[0][1], fim, g))
    return out


SUBS = subs()


def nq(t0, d):
    """Quadros exatos do plano (sem acumular arredondamento: a imagem fica presa à voz)."""
    return round((t0 + d) * FPS) - round(t0 * FPS)


def base_video(path):
    """Corta, gira, enquadra em 1080x1920 e trata a cor de cada plano; junta tudo sem áudio."""
    tmp = os.path.join(OUT, "planos2")
    os.makedirs(tmp, exist_ok=True)
    lst = []
    for i, (t0, d, arq, ini) in enumerate(PLANOS):
        p = os.path.join(tmp, f"p{i:02d}.mp4")
        if arq == "mosaico":
            mosaico(p, nq(t0, d) / FPS)
            lst.append(p)
            continue
        g = GRADE_ROSTO if arq in ROSTOS else GRADE
        vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},{g}"
        subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-ss", f"{ini:.3f}", "-i", os.path.join(BR, arq), "-frames:v",
                        str(nq(t0, d)), "-an", "-vf", vf, "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-pix_fmt",
                        "yuv420p", p], check=True)
        lst.append(p)
    with open(os.path.join(tmp, "lista.txt"), "w") as f:
        f.writelines(f"file '{p}'\n" for p in lst)
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i",
                    os.path.join(tmp, "lista.txt"), "-c", "copy", path], check=True)


MOSAICO = [("v2.mp4", 5.0), ("v7.mp4", 6.0), ("v3.mp4", 2.0), ("v1.mp4", 3.0)]


def mosaico(p, d):
    """Fundo do CTA: as 4 cenas que ele gravou em grade 2x2, escurecidas para os textos lerem bem."""
    ins = []
    for arq, ini in MOSAICO:
        ins += ["-ss", f"{ini:.2f}", "-t", f"{d:.3f}", "-i", os.path.join(BR, arq)]
    w2, h2 = W // 2, H // 2
    f = ";".join(f"[{i}:v]scale={w2}:{h2}:force_original_aspect_ratio=increase,crop={w2}:{h2},fps={FPS},{GRADE}[m{i}]"
                 for i in range(4))
    f += ";[m0][m1]hstack[top];[m2][m3]hstack[bot];[top][bot]vstack,eq=brightness=-0.22:saturation=0.85,gblur=sigma=6"
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error"] + ins + ["-filter_complex", f, "-frames:v", str(round(d * FPS)), "-an",
                    "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-pix_fmt", "yuv420p", p], check=True)


def nivela(p, alvo=-19.0):
    """Ganho FIXO na fala inteira (sem bombear): RMS das partes com voz no alvo e picos raros arredondados."""
    import wave
    with wave.open(p) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
    q = int(0.03 * 44100)
    e = np.sqrt(np.convolve(x ** 2, np.ones(q) / q, "same"))
    voz = e > e.max() * 0.1
    g = 10 ** (alvo / 20) / (np.sqrt((x[voz] ** 2).mean()) + 1e-9)
    y = x * g
    lim = 0.89
    y = np.where(np.abs(y) > lim * 0.8, np.sign(y) * (lim * 0.8 + (lim * 0.2) * np.tanh((np.abs(y) - lim * 0.8) / (lim * 0.2))), y)
    with wave.open(p, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(44100)
        w.writeframes((y * 32767).astype(np.int16).tobytes())


def vozes():
    arqs = []
    for i, (k, t0, d) in enumerate(VOZ):
        arq, a, b, _ = fala(k)
        p = os.path.join(OUT, f"voz2_{i}.wav")
        subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i",
                        os.path.join(BR, arq), "-vn", "-ac", "1", "-ar", "44100", "-af",
                        VOZ_CADEIA + ",afade=t=in:d=0.05,afade=t=out:st=%.2f:d=0.12" % (b - a - 0.12),
                        p], check=True)
        nivela(p)
        arqs.append((p, t0))
    return arqs


def plano(t):
    for i, (t0, d, arq, ini) in enumerate(PLANOS):
        if t0 <= t < t0 + d:
            return i, t0, d, arq
    return len(PLANOS) - 1, PLANOS[-1][0], PLANOS[-1][1], PLANOS[-1][2]


def zoom_de(t):
    """Zoom de cada momento (referência: edição de Reels falados — punch-in no rosto alternando o enquadramento,
    empurrão lento nas cenas, e um zoom rápido com desfoque nos cortes)."""
    i, t0, d, arq = plano(t)
    u = (t - t0) / d
    if i == 0:  # gancho: aproxima devagar enquanto ele ajeita a câmera e abre rápido quando ele se afasta
        z = 1.0 + 0.10 * ease(min(1.0, t / GANCHO / 0.85))
        sai = seg(t, GANCHO - 0.35, GANCHO + 0.45)
        return lerp(z, 1.0, ease(sai)), (0.05 < sai < 0.95) * math.sin(sai * math.pi)
    if arq == "mosaico":
        return 1.0, 0.0
    if arq in ROSTOS:  # rosto: aberto em A e fechado (punch-in) em C, com empurrão leve
        z = 1.0 + 0.015 * u  # rosto sem punch-in: o boné não pode cortar
    elif arq == "v5.mp4" and i == len(PLANOS) - 2:  # "comenta"
        z = 1.0 + 0.05 * u
    else:  # cenas dos jogos: empurrão lento, alternando entrar/sair
        z = 1.04 + 0.08 * (u if i % 2 else 1 - u)
    ent = t - t0
    blur = 0.0
    if ent < 0.2:  # chicote de zoom na entrada do plano
        q = ent / 0.2
        z += 0.12 * (1 - ease(q))
        blur = 1 - q
    return z, blur


def camera(fr, t):
    z, blur = zoom_de(t)
    if z <= 1.001 and blur <= 0.01:
        return fr
    i = plano(t)[0]
    dx = 14 * math.sin(t * 1.3) if i == 0 else 0.0
    w, h = W / z, H / z
    x0 = min(max(0.0, W / 2 - w / 2 + dx), W - w)
    y0 = (H - h) * (0.12 if PLANOS[i][2] in ROSTOS else 0.5)  # no rosto, sobe um pouco para não cortar a cabeça
    out = fr.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h))
    if blur > 0.05:
        out = Image.blend(out, out.filter(ImageFilter.GaussianBlur(7 * blur)), 0.65 * blur)
    return out


@lru_cache(None)
def palavra_img(txt, amarela):
    return letreiro(txt.upper(), 92, AMARELO if amarela else WHITE, INK, 12, "Poppins-Black.ttf")


def legenda_viva(img, t):
    """Grupo de 1–3 palavras centrado, a palavra que ele está falando em amarelo e um 'pop' ao entrar."""
    for a, b, g in SUBS:
        if a <= t < b:
            fala_agora = max(j for j, (_, w0, _) in enumerate(g) if w0 <= t or j == 0)
            ims = [palavra_img(w, j == fala_agora) for j, (w, _, _) in enumerate(g)]
            gap, larg = 22, 960  # quebra por largura real: nenhuma palavra sai da tela
            ims = [im if im.width - 24 <= larg else im.resize((larg + 24, int(im.height * (larg + 24) / im.width)),
                                                               Image.LANCZOS) for im in ims]
            linhas, cur, cw = [], [], 0
            for im in ims:
                w_ = im.width - 24
                if cur and cw + gap + w_ > larg:
                    linhas.append(cur)
                    cur, cw = [], 0
                cw += (gap if cur else 0) + w_
                cur.append(im)
            linhas.append(cur)
            sc = 0.85 + 0.15 * ease(min(1.0, (t - a) / 0.12))
            y = 1525 - (len(linhas) - 1) * 110
            for ln in linhas:
                lw = sum(x.width - 24 for x in ln) + gap * (len(ln) - 1)
                x = 540 - lw / 2
                for im in ln:
                    cola(img, im, x + (im.width - 24) / 2, y, 0, sc)
                    x += im.width - 24 + gap
                y += 115
            return


CAIXAS = ["go_cuckoo.png", "gravity_superstar.png", "draftosaurus.png", "scooby_doo.png"]  # fotos OFICIAIS (recortes_oficiais.py)


def caixa_oficial(k, h):
    """Foto oficial da caixa sem os bloquinhos de JPEG (a capa reta do Scooby ganha cantos redondos)."""
    import cv2
    im = Image.open(os.path.join(ROOT, "assets", "oficial", CAIXAS[k])).convert("RGBA")
    rgb = cv2.fastNlMeansDenoisingColored(np.array(im.convert("RGB")), None, 4, 4, 7, 21)
    im = Image.merge("RGBA", (*Image.fromarray(rgb).split(), im.getchannel("A")))
    larg = min(820, int(im.width * h / im.height))
    im = im.resize((larg, int(im.height * larg / im.width)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.2, 60, 2))
    if k == 3:
        m = Image.new("L", im.size, 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=24, fill=255)
        im.putalpha(m)
    return im


@lru_cache(None)
def capa_canto(k):
    im = caixa_oficial(k, 600 if k == 0 else 400)
    if im.width > 340:
        im = im.resize((340, int(im.height * 340 / im.width)), Image.LANCZOS)
    return sombra(im, 16, (8, 18), 0.55)


def capa_pequena(img, t):
    """A capa oficial pequena no canto de baixo, à direita (sobre o ombro dele, longe do rosto), só nos planos dele."""
    if PLANOS[plano(t)[0]][2] not in ROSTOS or t >= TC:
        return
    for t0, t1, k in CAIXAS_T:
        if t0 <= t < t1:
            sai = seg(t, t1 - 0.25, t1)
            cx = capa_canto(k)
            y = 1440 - cx.height / 2 + 4 * math.sin((t - t0) * 2.0) + 600 * ease(sai)
            cola(img, cx, 1040 - cx.width / 2, y, 5, quica(t, t0, 0.5))
            return


@lru_cache(None)
def ficha(txt, ico):
    f = font("Poppins-Black.ttf", 44)
    tw = int(f.getlength(txt))
    im = Image.new("RGBA", (tw + 130, 84), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, im.width - 1, 83), radius=42, fill=(255, 255, 255, 240), outline=INK, width=4)
    e = emoji(ico, 52)
    im.alpha_composite(e, (18, (84 - e.height) // 2))
    d.text((92, 42), txt, font=f, fill=INK, anchor="lm")
    return im


def fichas(img, t):
    """No vídeo do jogo na mesa: nome do jogo em cima e as fichas (tipo, jogadores, idade, tempo) entrando uma a uma."""
    for t0, d, k in FICHAS:
        if not (t0 <= t < t0 + d):
            continue
        cola(img, pilula(f"JOGO {k + 1}/4", 38, INK), 540, 230, 0, pop(t, t0))
        cola(img, pilula(FALAS[k][0].upper(), 60, (249, 115, 22)), 540, 340, -2, pop(t, t0 + 0.1))
        p, a, tm, tag, cor = INFO[k]
        itens = [(0.3, pilula(tag, 36, cor)), (0.5, ficha(p, "👥")), (0.7, ficha(a, "🎂")), (0.9, ficha(tm, "⏱️"))]
        for q, (dt, im) in enumerate(itens):
            if t >= t0 + dt:
                cola(img, im, 60 + im.width / 2, 1040 + q * 100, 0, pop(t, t0 + dt))
        return


# ---------------------------------------------------------------- efeitos do jogo (por cima das cenas da mesa)
@lru_cache(None)
def ovo(s=110):
    im = Image.new("RGBA", (s, int(s * 1.3)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((4, 4, s - 4, s * 1.3 - 4), fill=(250, 246, 236, 255))
    d.ellipse((s * 0.2, s * 0.15, s * 0.45, s * 0.5), fill=(255, 255, 255, 200))  # brilho
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((s * 0.35, s * 0.55, s - 6, s * 1.3 - 6), fill=(190, 170, 140, 90))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    return sombra(im, 8, (3, 8), 0.35)


@lru_cache(None)
def estrela(s, cor):
    """Estrela brilhante de 4 pontas com brilho suave (as estrelinhas do Gravity)."""
    im = Image.new("RGBA", (s * 2, s * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = s
    pts = []
    for k in range(8):
        r = s * (0.95 if k % 2 == 0 else 0.22)
        a = k * math.pi / 4
        pts.append((c + r * math.cos(a - math.pi / 2), c + r * math.sin(a - math.pi / 2)))
    d.polygon(pts, fill=cor + (255,))
    glow = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((c - s * 0.6, c - s * 0.6, c + s * 0.6, c + s * 0.6), fill=cor + (150,))
    out = glow.filter(ImageFilter.GaussianBlur(s * 0.35))
    out.alpha_composite(im)
    ImageDraw.Draw(out).ellipse((c - s * 0.12, c - s * 0.12, c + s * 0.12, c + s * 0.12), fill=(255, 255, 255, 255))
    return out


@lru_cache(None)
def pegada(s=90, rot=0):
    """Pegada de dinossauro (3 dedos) em verde escuro, como carimbo."""
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cor = (20, 110, 60, 225)
    d.ellipse((s * 0.28, s * 0.45, s * 0.72, s * 0.9), fill=cor)
    for ang in (-35, 0, 35):
        a = math.radians(ang - 90)
        x, y = s * 0.5 + math.cos(a) * s * 0.36, s * 0.52 + math.sin(a) * s * 0.36
        d.polygon([(s * 0.5 + math.cos(a + 1.6) * s * 0.09, s * 0.55 + math.sin(a + 1.6) * s * 0.09),
                   (x, y), (s * 0.5 + math.cos(a - 1.6) * s * 0.09, s * 0.55 + math.sin(a - 1.6) * s * 0.09)], fill=cor)
    return im.rotate(rot, expand=True, resample=Image.BICUBIC)


@lru_cache(None)
def fantasma(s=260):
    im = Image.new("RGBA", (s, int(s * 1.2)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, s, s), fill=(240, 248, 255, 200))
    d.rectangle((0, s / 2, s, s * 1.05), fill=(240, 248, 255, 200))
    for k in range(4):  # barra ondulada
        d.ellipse((k * s / 4, s * 0.95, (k + 1) * s / 4, s * 1.18), fill=(240, 248, 255, 200))
    for x in (0.33, 0.62):
        d.ellipse((s * x - 18, s * 0.38, s * x + 18, s * 0.38 + 46), fill=(30, 30, 50, 230))
    d.ellipse((s * 0.43, s * 0.62, s * 0.55, s * 0.78), fill=(30, 30, 50, 200))
    glow = im.filter(ImageFilter.GaussianBlur(16))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.alpha_composite(glow)
    out.alpha_composite(im)
    return out


@lru_cache(None)
def nevoa_faixa():
    rng = np.random.default_rng(3)
    a = rng.random((8, 30)).astype(np.float32)
    m = Image.fromarray((a * 255).astype(np.uint8), "L").resize((W * 2, 700), Image.BICUBIC).filter(ImageFilter.GaussianBlur(40))
    al = np.array(m, np.float32) / 255 * 0.5
    al *= np.linspace(0, 1, 700)[:, None] ** 1.5
    im = Image.new("RGBA", (W * 2, 700), (225, 235, 255, 0))
    im.putalpha(Image.fromarray((al * 255).astype(np.uint8)))
    return im


@lru_cache(None)
def balao_zoinks():
    return letreiro("ZOINKS!", 92, AMARELO, INK, 12, "Bungee-Regular.ttf")


def efeitos(img, t):
    """Um efeito de cada jogo enquanto aparece o jogo na mesa: discreto, rápido, sem tampar as fichas."""
    for t0, d, k in FICHAS:
        if not (t0 <= t < t0 + d):
            continue
        u = t - t0
        sai = 1 - seg(t, t0 + d - 0.3, t0 + d)
        if k == 0:  # Go Cuckoo: os ovos da Kiki caindo no ninho (lado direito)
            for j, (x, t1) in enumerate(((760, 0.3), (900, 0.75), (680, 1.2), (850, 1.65), (960, 2.1))):
                v = u - t1
                if v < 0:
                    continue
                q = min(1.0, v / 0.55)
                y = lerp(-120, 1330 - (j % 2) * 70, q * q)
                y -= 60 * math.sin(min(1, max(0, (v - 0.55) / 0.3)) * math.pi) * (v > 0.55)  # quique
                cola(img, ovo(110), x, y, (j - 2) * 12 + (1 - q) * 90, 1.0, sai)
        elif k == 1:  # Gravity: estrelas coloridas flutuando e piscando
            cores = [(255, 210, 60), (255, 90, 170), (80, 220, 255), (120, 255, 140), (255, 160, 60)]
            for j in range(9):
                x = 620 + (j * 137) % 400
                y = 1450 - ((u * (90 + 15 * j) + j * 160) % 1100)
                tw = 0.65 + 0.35 * math.sin(t * 6 + j)
                cola(img, estrela(44 + 8 * (j % 3), cores[j % 5]), x, y, t * 40 * (1 if j % 2 else -1), tw,
                     sai * min(1, u / 0.3))
        elif k == 2:  # Draftosaurus: pegadas de dinossauro atravessando a tela
            for j in range(8):  # sobem pela direita da cena, longe das fichas e da legenda
                tj = 0.25 + j * 0.35
                if u < tj:
                    break
                x = 700 + j * 40 + (45 if j % 2 else -45)
                y = 1330 - j * 115
                cola(img, pegada(120, 12 if j % 2 else -12), x, y, 0, pop(t, t0 + tj, 0.2),
                     sai * (1 - seg(u, tj + 1.8, tj + 2.4)))
        elif k == 3:  # Scooby-Doo: névoa no chão e o fantasma passando
            nv = nevoa_faixa()
            off = int((u * 120) % W)
            img.alpha_composite(nv.crop((off, 0, off + W, 700)).point(lambda v: v), (0, H - 700 - 160))
            x = lerp(1250, -200, ease(seg(u, 0.2, d - 0.2)))
            cola(img, fantasma(240), x, 760 + 40 * math.sin(u * 3), 6 * math.sin(u * 2), 1.0, 0.85 * sai)
        return


def overlay(t, com_legenda):
    """Camada transparente com textos, nomes dos jogos, legenda, logo e CTA."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fichas(img, t)
    capa_pequena(img, t)
    if t < GANCHO + 0.4:
        sai = seg(t, GANCHO, GANCHO + 0.4)
        cola(img, letreiro("4 JOGOS PRO DIA\nDAS CRIANÇAS", 108, AMARELO, INK, 14), 540, 1380, -2, pop(t, -0.3), 1 - sai)
    tc = TC
    efeitos(img, t)
    if tc <= t < tc + COMENTA:
        b = 1 + 0.04 * abs(math.sin(t * 6))
        cola(img, letreiro("QUAL SEU FILHO\nIA AMAR?", 104, AMARELO, INK, 14), 540, 760, -2, pop(t, tc))
        cola(img, letreiro("COMENTA AQUI!", 84, WHITE, INK, 12), 500, 1040, 2, pop(t, tc + 0.3) * b)
        cola(img, emoji("👇", 100), 920, 1050 + 12 * math.sin(t * 9), 0, pop(t, tc + 0.4))
    if TF <= t < TA:  # ele chamando para o link
        cola(img, pilula("TODOS NO ACERVO DA SUA VEZ", 42, (249, 115, 22)), 540, 1290, 0, pop(t, TF + 0.2))
        cola(img, pilula("LINK NA BIO · @SUAVEZ_BG", 44, INK, WHITE, (249, 115, 22)), 540, 1390, 0, pop(t, TF + 2.4))
    ta = TA
    if t >= ta:
        cola(img, logo_card(440), 540, 420, 0, pop(t, ta))
        itens = [(0.3, letreiro("ALUGUE NA\nSUA VEZ!", 100, AMARELO, INK, 14), 800),
                 (0.6, pilula("5 DIAS DE JOGO · 3 JOGOS = 7 DIAS", 38, INK), 1040),
                 (0.8, pilula("RESERVE ONLINE · RETIRE EM MAUÁ E ABC", 34, WHITE, INK, INK), 1150),
                 (1.0, pilula("OU RECEBA EM CASA!", 42, (22, 163, 74)), 1260),
                 (1.2, pilula("LINK NA BIO · @SUAVEZ_BG", 50, (249, 115, 22)), 1400)]
        for t0, im, y in itens:
            if t >= ta + t0:
                cola(img, im, 540, y, 0, pop(t, ta + t0))
    else:
        wm = logo_card(160)
        img.alpha_composite(wm, (W - wm.width - 30, 40))
    if com_legenda and (GANCHO + 0.3 <= t < tc or TF <= t < TA):
        legenda_viva(img, t)
    return img


def final_loudness(wav, alvo=-14.0, tp=-1.0):
    """Loudness final com ganho FIXO (loudnorm linear em 2 passadas), pico real ≤ −1 dB."""
    import json as js
    r = subprocess.run([ffmpeg(), "-hide_banner", "-i", wav, "-af", f"loudnorm=I={alvo}:TP={tp}:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    m = js.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    tmp = wav.replace(".wav", "_n.wav")
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", wav, "-af",
                    f"loudnorm=I={alvo}:TP={tp}:LRA=11:linear=true:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
                    f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}",
                    "-ar", "44100", tmp], check=True)
    os.replace(tmp, wav)


def compor(base, saida, wav, com_legenda):
    """Lê o vídeo base quadro a quadro, cola a camada de textos e grava com o áudio."""
    rd = subprocess.Popen([ffmpeg(), "-loglevel", "error", "-i", base, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                          stdout=subprocess.PIPE)
    wr = subprocess.Popen([ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s",
                           f"{W}x{H}", "-framerate", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-crf", "20",
                           "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
                           "-movflags", "+faststart", saida], stdin=subprocess.PIPE)
    n = 0
    while True:
        buf = rd.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        fr = camera(Image.frombytes("RGB", (W, H), buf), n / FPS).convert("RGBA")
        fr.alpha_composite(overlay(n / FPS, com_legenda))
        wr.stdin.write(fr.convert("RGB").tobytes())
        n += 1
    wr.stdin.close()
    wr.wait()
    print("ok:", saida, n, "quadros", flush=True)


def cues():
    c = [(0.0, "pop", 0.4), (0.15, "pop", 0.3), (GANCHO - 0.3, "whoosh", 0.6)]
    c += [(GANCHO + INTRO_ROSTO + j * 0.82, "pop", 0.3) for j in range(4)]
    c += [(t0, "whoosh", 0.28) for t0, d, arq, _ in PLANOS if t0 > GANCHO + INTRO_ROSTO + 3 and arq not in ROSTOS + ("mosaico",)]
    c += [(t0, "pop", 0.35) for t0, _, _ in CAIXAS_T]
    for t0, d, k in FICHAS:
        c += [(t0 + x, "pop", 0.22) for x in (0.1, 0.3, 0.5, 0.7, 0.9)] + [(t0 + d, "whoosh", 0.3), (t0 + d + 0.05, "ding", 0.3)]
    tc = TC
    c += [(tc, "pop", 0.4), (tc + 0.3, "boing", 0.4), (TF, "whoosh", 0.4), (TF + 2.4, "pop", 0.4), (TA, "whoosh", 0.4),
          (TA + 1.2, "ding", 0.5)]
    for t0, d, k in FICHAS:  # sons dos efeitos de cada jogo
        c += [(t0 + 0.4 + 0.45 * j, ("pop", "chime", "pop", "boing")[k], 0.18) for j in range(4)]
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    base = os.path.join(OUT, "base2.mp4")
    if not os.path.exists(base) or a.frame is None:
        base_video(base)
    if a.frame:
        ims = []
        for x in a.frame:
            r = subprocess.run([ffmpeg(), "-loglevel", "error", "-ss", f"{x:.3f}", "-i", base, "-frames:v", "1", "-f",
                                "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True)
            fr = camera(Image.frombytes("RGB", (W, H), r.stdout[:W * H * 3]), x).convert("RGBA")
            fr.alpha_composite(overlay(x, True))
            ims.append(fr.convert("RGB"))
        folha(ims, os.path.join(OUT, "frames.jpg"))
        return
    wav = os.path.join(OUT, "trilha2.wav")
    som.build(wav, DUR, cues(), musica="travessa", voz=vozes(), fx_ganho=0.3, duck=0.8, musica_ganho=0.16, satura=False)
    final_loudness(wav, -15.5, -2.0)  # um pouco mais baixo e com folga no pico (no celular a 100% ele "explodia")
    compor(base, os.path.join(OUT, "criancas2_com_legenda.mp4"), wav, True)
    compor(base, os.path.join(OUT, "criancas2_sem_legenda.mp4"), wav, False)


if __name__ == "__main__":
    main()
