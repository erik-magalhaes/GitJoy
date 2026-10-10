#!/usr/bin/env python3
"""Reels da trend "5, 4, 3, 2, 1" de jogos de tabuleiro, com o material GRAVADO PELO DONO (brutos/54321/, fora do git):

- 20261010_102656.mp4: ele pertinho da câmera, "Vamos gravar um 5, 4, 3, 2, 1" (gancho);
- 20261010_102715.mp4: tomada única, alguém pergunta (fora da câmera) e ele responde. Ele travou no "3 jogos pra dois"
  e no "1 jogo": uso a ÚLTIMA tentativa boa (o vídeo segue o que ele FALOU).

Visual: contagem regressiva. A cada pergunta o número entra batendo no meio e vira o selo do título; as casas vazias
aparecem e cada caixa OFICIAL (recortes_lista.py) cai na sua casa quando ele fala o nome. No "1", a caixa do Hitster
sozinha, grande, com raios dourados. Rosto livre (tudo fica do peito para baixo), legenda palavra a palavra, "comenta" e
tela final da Sua Vez.

    python3 lista54321.py --frame 1 8 30      # quadros de teste em out/frames.jpg
    python3 lista54321.py                     # out/lista54321_com_legenda.mp4 e out/lista54321_sem_legenda.mp4
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
sys.path.insert(0, os.path.join(ROOT, "..", "comum"))
from motor import (W, H, FPS, WHITE, seg, ease, lerp, pop, font, emoji, logo_card, cola, sombra, letreiro, pilula,  # noqa
                   folha, ffmpeg)
import som  # noqa: E402

BR = os.path.join(ROOT, "brutos", "54321")
OUT = os.path.join(ROOT, "out")
CX = os.path.join(ROOT, "assets", "lista")
INK = (20, 16, 30)
AMARELO = (255, 214, 70)
GANCHO_ARQ = "20261010_102656.mp4"
TOMADA = "20261010_102715.mp4"
# mesmo microfone sem fio do vídeo das crianças (grave/abafado): mesma cadeia moderada e ganho fixo por trecho
VOZ_CADEIA = ("volume=-9dB,highpass=f=90,equalizer=f=140:t=q:w=1:g=-2,equalizer=f=320:t=q:w=1.3:g=-4,"
              "equalizer=f=3200:t=q:w=1.4:g=2,highshelf=f=6000:g=2")
GRADE = ("hqdn3d=2.5:2:5:5,curves=all='0/0.012 0.25/0.245 0.5/0.52 0.75/0.775 1/0.98',"
         "eq=contrast=1.02:saturation=0.97:gamma=1.03,unsharp=5:5:0.45:5:5:0.0,vignette=angle=PI/14")

# trechos (tipo, arquivo, início, fim) em segundos do bruto; Q = pergunta (k = número), A = resposta
TRECHOS = [  # início = 1ª palavra (medido pela energia, sem a puxada de ar); fim = última palavra
    ("H", GANCHO_ARQ, 4.38, 6.64, 0),
    ("Q", TOMADA, 2.27, 5.80, 5),
    ("A", TOMADA, 6.17, 9.50, 5), ("A", TOMADA, 13.12, 14.90, 5),
    ("Q", TOMADA, 15.98, 18.40, 4),
    ("A", TOMADA, 18.86, 20.15, 4), ("A", TOMADA, 21.12, 23.40, 4),
    ("A", TOMADA, 25.27, 28.45, 4), ("A", TOMADA, 29.60, 31.62, 4),
    ("Q", TOMADA, 52.50, 54.55, 3),
    ("A", TOMADA, 55.12, 57.00, 3), ("A", TOMADA, 57.57, 58.80, 3), ("A", TOMADA, 60.92, 62.00, 3),
    ("Q", TOMADA, 63.29, 65.88, 2),
    ("A", TOMADA, 66.42, 71.98, 2),
    ("Q", TOMADA, 84.64, 89.20, 1),
    ("A", TOMADA, 89.48, 95.15, 1),
]
COMENTA = (TOMADA, 95.30, 3.0, (95.98, 96.62))  # "É isso." por baixo do "comenta"
CTA = 4.2
# caixa de cada jogo e o instante (no bruto) em que ele fala o nome
JOGOS = {5: [("ticket_to_ride", 6.18), ("dixit", 7.54), ("marvel_united", 8.32), ("trio", 13.13), ("flip_7", 14.29)],
         4: [("king_of_tokyo", 18.87), ("the_resistance", 21.13), ("coup", 22.23), ("boop", 26.86)],
         3: [("jaipur", 55.13), ("splendor_duel", 57.58), ("azul_duel", 60.93)],
         2: [("harmonies", 66.43), ("azul", 70.71)],
         1: [("hitster", 89.77)]}
TITULO = {5: "JOGOS PRA QUEM\nNUNCA JOGOU", 4: "JOGOS QUE DESTROEM\nAMIZADES", 3: "JOGOS PRA\nJOGAR A DOIS",
          2: "JOGOS QUE\nNUNCA CANSAM", 1: "JOGO QUE TODO MUNDO\nPRECISA JOGAR"}
COR = {5: (249, 115, 22), 4: (220, 38, 38), 3: (147, 51, 234), 2: (37, 99, 235), 1: (234, 179, 8)}
CASA_H = {5: 230, 4: 270, 3: 310, 2: 360}  # altura das caixas na fileira
FILA_Y = 1265


def nq(t0, d):
    return round((t0 + d) * FPS) - round(t0 * FPS)


def linha_do_tempo():
    """Planos (t0 no vídeo final, duração, arquivo, início no bruto, tipo, k) e o mapa bruto → final."""
    planos, t = [], 0.0
    for tipo, arq, a, b, k in TRECHOS:
        planos.append((t, b - a, arq, a, tipo, k))
        t += b - a
    planos.append((t, COMENTA[2], COMENTA[0], COMENTA[1], "C", 0))
    t += COMENTA[2]
    planos.append((t, CTA, "cta", 90.0, "F", 0))
    return planos, t + CTA


PLANOS, DUR = linha_do_tempo()
TC = [p[0] for p in PLANOS if p[4] == "C"][0]
TF = [p[0] for p in PLANOS if p[4] == "F"][0]
QT = {p[5]: p[0] for p in PLANOS if p[4] == "Q"}  # início de cada pergunta


def final_de(arq, x):
    """Instante no vídeo final de um instante x do bruto (None se o trecho foi cortado)."""
    for t0, d, a_, ini, tipo, k in PLANOS:
        if a_ == arq and ini <= x < ini + d and tipo in "HQA":
            return t0 + x - ini
    return None


ENTRA = {k: [(n, final_de(TOMADA, x)) for n, x in v] for k, v in JOGOS.items()}

# ---------------------------------------------------------------- legenda (só nas respostas)
CORRIGE = {"Chikichuride,": "Ticket to Ride,", "Set.": "7.", "Koop": "Coup", "Dual.": "Duel.", "HITSTER,": "Hitster,",
           "Boop,": "boop,", "azul,": "Azul,", "azul": "Azul", "para": "pra", "e...": "e…", "E...": "E…"}


def subs():
    pals = json.load(open(os.path.join(ROOT, "palavras_lista.json"), encoding="utf-8"))
    out = []
    for t0, d, arq, ini, tipo, k in PLANOS:
        if tipo not in "A":
            continue
        ws = [(CORRIGE.get(w, w), t0 + max(a, ini) - ini, t0 + b - ini) for a, b, w in pals[arq[:-4]]
              if ini - 0.1 <= a < ini + d]
        grupos, cur = [], []
        for w in ws:
            cur.append(w)
            if len(cur) == 3 or len(" ".join(x[0] for x in cur)) > 13 or w[0][-1] in ",.!?…":
                grupos.append(cur)
                cur = []
        if cur:
            grupos.append(cur)
        for j, g in enumerate(grupos):
            fim = grupos[j + 1][0][1] if j + 1 < len(grupos) else min(g[-1][2] + 0.35, t0 + d)
            out.append((g[0][1], fim, g))
    return out


SUBS = subs()


@lru_cache(None)
def palavra_img(txt, amarela):
    return letreiro(txt.upper(), 88, AMARELO if amarela else WHITE, INK, 12, "Poppins-Black.ttf")


def legenda_viva(img, t):
    for a, b, g in SUBS:
        if a <= t < b:
            agora = max(j for j, (_, w0, _) in enumerate(g) if w0 <= t or j == 0)
            ims = [palavra_img(w, j == agora) for j, (w, _, _) in enumerate(g)]
            gap, larg = 22, 960
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
            y = 1530 - (len(linhas) - 1) * 105
            for ln in linhas:
                lw = sum(x.width - 24 for x in ln) + gap * (len(ln) - 1)
                x = 540 - lw / 2
                for im in ln:
                    cola(img, im, x + (im.width - 24) / 2, y, 0, sc)
                    x += im.width - 24 + gap
                y += 110
            return


# ---------------------------------------------------------------- vídeo base
def base_video(path):
    tmp = os.path.join(OUT, "planos_lista")
    os.makedirs(tmp, exist_ok=True)
    lst = []
    for i, (t0, d, arq, ini, tipo, k) in enumerate(PLANOS):
        p = os.path.join(tmp, f"p{i:02d}.mp4")
        vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},{GRADE}"
        if tipo == "F":  # fundo da tela final: ele, desfocado e escuro
            vf += ",eq=brightness=-0.25:saturation=0.8,gblur=sigma=14"
            arq = TOMADA
        subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-ss", f"{ini:.3f}", "-i", os.path.join(BR, arq), "-frames:v",
                        str(nq(t0, d)), "-an", "-vf", vf, "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-pix_fmt",
                        "yuv420p", p], check=True)
        lst.append(p)
    with open(os.path.join(tmp, "lista.txt"), "w") as f:
        f.writelines(f"file '{p}'\n" for p in lst)
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i",
                    os.path.join(tmp, "lista.txt"), "-c", "copy", path], check=True)


def plano(t):
    for i, p in enumerate(PLANOS):
        if p[0] <= t < p[0] + p[1]:
            return i
    return len(PLANOS) - 1


def camera(fr, t):
    """Corte seco alternando aberto / punch-in de 6% (esconde os pulos de corte); a cabeça nunca é cortada (ancora no topo)."""
    i = plano(t)
    t0, d, arq, ini, tipo, k = PLANOS[i]
    if tipo in "HF":
        return fr
    z = 1.06 if i % 2 else 1.0
    z += 0.012 * (t - t0) / d
    if tipo == "Q" and t - t0 < 0.25:  # chicote de zoom quando entra a pergunta
        z += 0.10 * (1 - ease((t - t0) / 0.25))
    w, h = W / z, H / z
    x0 = min(max(0.0, 660 - w / 2), W - w)
    return fr.resize((W, H), Image.BICUBIC, box=(x0, 0, x0 + w, h))


# ---------------------------------------------------------------- vozes
def nivela(p, alvo=-19.0):
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
    itens = [(t0, arq, ini, d) for t0, d, arq, ini, tipo, k in PLANOS if tipo in "HQA"]
    a, b = COMENTA[3]
    itens.append((TC + a - COMENTA[1], COMENTA[0], a, b - a))
    for i, (t0, arq, ini, d) in enumerate(itens):
        p = os.path.join(OUT, f"voz_lista_{i:02d}.wav")
        subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-ss", f"{ini:.3f}", "-t", f"{d:.3f}", "-i",
                        os.path.join(BR, arq), "-vn", "-ac", "1", "-ar", "44100", "-af",
                        VOZ_CADEIA + ",afade=t=in:d=0.03,afade=t=out:st=%.3f:d=0.06" % (d - 0.06), p], check=True)
        nivela(p)
        arqs.append((p, t0))
    return arqs


def final_loudness(wav, alvo=-15.5, tp=-2.0):
    r = subprocess.run([ffmpeg(), "-hide_banner", "-i", wav, "-af", f"loudnorm=I={alvo}:TP={tp}:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    tmp = wav.replace(".wav", "_n.wav")
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", wav, "-af",
                    f"loudnorm=I={alvo}:TP={tp}:LRA=11:linear=true:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
                    f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}",
                    "-ar", "44100", tmp], check=True)
    os.replace(tmp, wav)


# ---------------------------------------------------------------- desenhos
@lru_cache(None)
def caixa(nome, h):
    im = Image.open(os.path.join(CX, nome + ".png")).convert("RGBA")
    im = im.resize((max(2, int(im.width * h / im.height)), int(h)), Image.LANCZOS)
    return sombra(im, 14, (0, 12), 0.5)


@lru_cache(None)
def numero(k, size):
    return letreiro(str(k), size, WHITE, COR[k], max(10, size // 14), "Bungee-Regular.ttf", sombra_px=size // 22,
                    cor_sombra=INK)


@lru_cache(None)
def titulo(k):
    return letreiro(TITULO[k], 62, WHITE, INK, 10)


@lru_cache(None)
def casa(w, h):
    im = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((2, 2, w - 3, h - 3), radius=18, fill=(20, 16, 30, 120), outline=(255, 255, 255, 170), width=4)
    d.text((w / 2, h / 2), "?", font=font("Bungee-Regular.ttf", int(h * 0.32)), fill=(255, 255, 255, 150), anchor="mm")
    return im


@lru_cache(None)
def raios(r, cor):
    im = Image.new("RGBA", (2 * r, 2 * r), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for j in range(16):
        a0, a1 = j * math.tau / 16, (j + 0.5) * math.tau / 16
        d.polygon([(r, r), (r + r * math.cos(a0), r + r * math.sin(a0)), (r + r * math.cos(a1), r + r * math.sin(a1))],
                  fill=cor + (90,))
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).ellipse((0, 0, 2 * r, 2 * r), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(r // 4))
    im.putalpha(Image.fromarray((np.asarray(im.getchannel("A"), float) * np.asarray(m, float) / 255).astype(np.uint8)))
    return im


def fim_da_secao(k):
    return QT[k - 1] if k > 1 else TC


def secao(img, t, k):
    """Número batendo no meio → vira selo ao lado do título; casas; caixas caindo nas casas quando ele fala o nome."""
    q0, q1 = QT[k], fim_da_secao(k)
    if not q0 <= t < q1:
        return
    sai = seg(t, q1 - 0.3, q1)  # tudo sai para a esquerda antes da próxima pergunta
    dx = -1200 * ease(sai)
    u = seg(t, q0 + 0.45, q0 + 0.8)  # o número vai do meio para o selo
    if t < q0 + 0.45:
        sc = lerp(2.2, 1.0, ease(seg(t, q0, q0 + 0.18)))
        cola(img, numero(k, 360), 540 + dx, 1080, -4, sc)
    else:
        cola(img, numero(k, 360), lerp(540, 150, ease(u)) + dx, lerp(1080, 985, ease(u)), -4, lerp(1.0, 0.62, ease(u)))
        cola(img, titulo(k), 640 + dx, 985, -2, pop(t, q0 + 0.6))
    if k == 1:  # o número 1: caixa grande e sozinha, com raios dourados girando
        nome, te = ENTRA[1][0]
        if t >= te:
            r = raios(380, (255, 214, 70)).rotate(-(t - te) * 25, resample=Image.BICUBIC)
            cola(img, r, 540 + dx, 1265, 0, pop(t, te, 0.5))
            cola(img, caixa(nome, 420), 540 + dx, 1262, -3, pop(t, te, 0.45))
        return
    jogos = ENTRA[k]
    h = CASA_H[k]
    ims = [caixa(n, h) for n, _ in jogos]
    larg = [im.width - 56 for im in ims]  # sem a margem da sombra
    gap = 18
    total = sum(larg) + gap * (len(larg) - 1)
    if total > 1020:
        f = 1020 / total
        ims = [caixa(n, int(h * f)) for n, _ in jogos]
        larg = [im.width - 56 for im in ims]
        total = sum(larg) + gap * (len(larg) - 1)
    x = 540 - total / 2
    for j, ((n, te), im, lw) in enumerate(zip(jogos, ims, larg)):
        cx = x + lw / 2 + dx
        rot = (-3, 2, -2, 3, -1)[j]
        if t < te:
            cola(img, casa(lw, im.height - 56), cx, FILA_Y, 0, pop(t, q0 + 0.7 + 0.08 * j))
        else:
            v = seg(t, te, te + 0.22)
            cola(img, im, cx, lerp(FILA_Y - 130, FILA_Y, ease(v)), rot * (1 - v) * 3 + rot, lerp(1.25, 1.0, ease(v)))
        x += lw + gap


def gancho(img, t):
    """Ele dizendo '5, 4, 3, 2, 1': cada número pula na hora em que ele fala; a frase já está na tela."""
    cola(img, pilula("VERSÃO JOGOS DE TABULEIRO", 46, INK, WHITE, AMARELO), 540, 1450, -2, pop(t, -0.2))
    tempos = [5.08, 5.30, 5.48, 5.86, 6.02]
    for j, k in enumerate((5, 4, 3, 2, 1)):
        te = tempos[j] - TRECHOS[0][2]
        if t >= te:
            cola(img, numero(k, 190), 140 + j * 200, 1230, (-6, 4, -3, 5, -4)[j], pop(t, te, 0.25))


def overlay(t, com_legenda):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if t < QT[5]:
        gancho(img, t)
    for k in QT:
        secao(img, t, k)
    if TC <= t < TF:
        b = 1 + 0.04 * abs(math.sin(t * 6))
        cola(img, letreiro("E O SEU\nNÚMERO 1?", 110, AMARELO, INK, 14), 540, 1060, -2, pop(t, TC))
        cola(img, letreiro("COMENTA AQUI!", 84, WHITE, INK, 12), 500, 1330, 2, pop(t, TC + 0.35) * b)
        cola(img, emoji("👇", 100), 930, 1340 + 12 * math.sin(t * 9), 0, pop(t, TC + 0.45))
    if t >= TF:
        cola(img, logo_card(400), 540, 300, 0, pop(t, TF))
        fan = ["ticket_to_ride", "king_of_tokyo", "hitster", "harmonies", "dixit"]
        for j, n in enumerate(fan):
            cola(img, caixa(n, 300 if j == 2 else 250), 540 + (j - 2) * 190, 700 + abs(j - 2) * 25, (j - 2) * 6,
                 pop(t, TF + 0.15 + 0.07 * abs(j - 2)))
        cola(img, caixa("hitster", 300), 540, 700, 0, pop(t, TF + 0.15))
        itens = [(0.4, letreiro("ALUGUE NA\nSUA VEZ!", 100, AMARELO, INK, 14), 1010),
                 (0.7, pilula("5 DIAS DE JOGO · 3 JOGOS = 7 DIAS", 38, INK), 1215),
                 (0.9, pilula("RESERVE ONLINE · RETIRE EM MAUÁ E ABC", 34, WHITE, INK, INK), 1320),
                 (1.1, pilula("OU RECEBA EM CASA!", 42, (22, 163, 74)), 1425),
                 (1.3, pilula("LINK NA BIO · @SUAVEZ_BG", 50, (249, 115, 22)), 1550)]
        for t0, im, y in itens:
            if t >= TF + t0:
                cola(img, im, 540, y, 0, pop(t, TF + t0))
    else:
        wm = logo_card(160)
        img.alpha_composite(wm, (W - wm.width - 30, 40))
    if com_legenda and QT[5] <= t < TC:
        legenda_viva(img, t)
    return img


def compor(base, saida, wav, com_legenda):
    rd = subprocess.Popen([ffmpeg(), "-loglevel", "error", "-i", base, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                          stdout=subprocess.PIPE)
    wr = subprocess.Popen([ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s",
                           f"{W}x{H}", "-framerate", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-crf", "19",
                           "-preset", "medium", "-tune", "film", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                           "-shortest", "-movflags", "+faststart", saida], stdin=subprocess.PIPE)
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
    c = [(0.0, "whoosh", 0.4)]
    c += [(x - TRECHOS[0][2], "pop", 0.4) for x in (5.08, 5.30, 5.48, 5.86, 6.02)]
    for k, q0 in QT.items():
        c += [(q0 - 0.3, "whoosh", 0.5), (q0, "carimbo", 0.55), (q0 + 0.5, "whoosh", 0.3)]
        c += [(te, "pop", 0.45) for _, te in ENTRA[k]]
    c += [(ENTRA[1][0][1], "reveal", 0.5), (ENTRA[1][0][1] + 0.1, "ding", 0.4)]
    c += [(TC, "pop", 0.4), (TC + 0.35, "boing", 0.4), (TF, "whoosh", 0.4), (TF + 1.3, "ding", 0.5)]
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    print(f"duração: {DUR:.1f} s; perguntas em", {k: round(v, 1) for k, v in QT.items()})
    base = os.path.join(OUT, "base_lista.mp4")
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
    wav = os.path.join(OUT, "trilha_lista.wav")
    som.build(wav, DUR, cues(), musica="gameshow", voz=vozes(), fx_ganho=0.3, duck=0.8, musica_ganho=0.14, satura=False)
    final_loudness(wav, -15.5, -2.0)
    compor(base, os.path.join(OUT, "lista54321_com_legenda.mp4"), wav, True)
    compor(base, os.path.join(OUT, "lista54321_sem_legenda.mp4"), wav, False)


if __name__ == "__main__":
    main()
