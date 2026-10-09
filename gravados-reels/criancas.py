#!/usr/bin/env python3
"""Reels "jogos para crianças", com o material GRAVADO PELO DONO (pasta brutos/, fora do git):

- v0.mp4 (Drive, 1:10): ele falando na frente da estante (várias tentativas; uso só as boas);
- v1–v3 Go Cuckoo, v4–v5 Scooby-Doo, v6–v7 Gravity Superstar, v8 Draftosaurus (cenas dos jogos).

Montagem curta (~33 s): gancho em cima da cena do Go Cuckoo; em cada jogo, ele aparece falando (com a boca
sincronizada) e corta para as cenas do jogo enquanto a fala continua; legenda pelas palavras; "comenta"; CTA.

    python3 criancas.py --frame 1 5 12      # quadros de teste em out/frames.jpg
    python3 criancas.py                     # out/criancas_com_legenda.mp4 e out/criancas_sem_legenda.mp4
"""
import argparse
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "..", "comum"))
from motor import (W, H, FPS, WHITE, seg, ease, lerp, pop, font, emoji, logo_card, cola, letreiro, pilula,  # noqa
                   legenda, folha, ffmpeg)
import som  # noqa: E402

BR = os.path.join(ROOT, "brutos")
OUT = os.path.join(ROOT, "out")
INK = (20, 16, 30)
AMARELO = (255, 214, 70)
VOZ_CADEIA = ("highpass=f=90,afftdn=nr=14:nf=-42:tn=1,equalizer=f=250:t=q:w=1:g=-3,equalizer=f=3200:t=q:w=1:g=3,"
              "highshelf=f=9000:g=1.5,deesser=i=0.35,acompressor=threshold=-20dB:ratio=3:attack=6:release=140:makeup=3,"
              "loudnorm=I=-16:TP=-1.5:LRA=6")
GRADE = ("hqdn3d=2:1.5:4:4,normalize=blackpt=black:whitept=white:smoothing=20:independence=0.4:strength=0.8,"
         "curves=all='0/0 0.25/0.26 0.5/0.56 0.75/0.82 1/1',vibrance=intensity=0.3,eq=saturation=1.08,"
         "colorbalance=rm=-0.03:bm=0.03:rh=0.02,unsharp=5:5:0.7")

# falas boas da gravação v0 (início, fim) e o texto que ele falou
FALAS = [
    ("Go Cuckoo!", (4.60, 10.95), "E o primeiro da lista é o Go Cuckoo, um jogo onde a gente precisa montar um ninho perfeito "
                                  "pra que a Kiki possa botar os seus ovos."),
    ("Gravity Superstar", (18.55, 24.85), "E o segundo é o Gravity Stars, um jogo onde viramos astronautas em busca de "
                                          "pequenas estrelas coloridas."),
    ("Draftosaurus", (51.55, 57.75), "Também separamos o Draftosaurus, o jogo onde a gente monta o nosso próprio parque "
                                     "de dinossauros. Ótimo para os pequeninos!"),
    ("Scooby-Doo!", (60.50, 66.40), "E por último, o jogo Scooby-Doo Board Game, onde a família se une pra derrotar o "
                                    "monstro da semana."),
]
FALA_ROSTO = 1.7  # segundos com ele falando antes de cortar para as cenas do jogo
# cenas de cada jogo: (arquivo, início) — encaixadas em sequência até o fim da fala
CENAS = [[("v2.mp4", 1.6), ("v3.mp4", 8.0)], [("v7.mp4", 1.0), ("v6.mp4", 3.5)],
         [("v8.mp4", 2.2), ("v8.mp4", 8.5)], [("v4.mp4", 1.6), ("v5.mp4", 1.8)]]
GANCHO = 4.3  # ele entrando no quadro e se ajeitando na frente da câmera (pedido dele: é o gancho)
GANCHO_INI = 0.3
COMENTA = 2.6
CTA = 3.6


def linha_do_tempo():
    """Lista de planos [(t0, dur, arquivo, início no arquivo)] e posições da voz."""
    planos, voz, t = [], [], 0.0
    t = GANCHO
    for k, (_, (a, b), _) in enumerate(FALAS):
        d = b - a
        voz.append((k, t, d))
        if k == 0:  # o gancho emenda direto na 1ª fala (mesma tomada, sem corte)
            planos.append((0.0, GANCHO + FALA_ROSTO, "v0.mp4", GANCHO_INI))
        else:
            planos.append((t, FALA_ROSTO, "v0.mp4", a))
        resto = d - FALA_ROSTO
        cs = CENAS[k]
        for j, (arq, ini) in enumerate(cs):
            dd = resto / len(cs)
            planos.append((t + FALA_ROSTO + j * dd, dd, arq, ini))
        t += d + 0.15
    planos.append((t, COMENTA, "v5.mp4", 4.5))
    t += COMENTA
    planos.append((t, CTA, "mosaico", 0.0))
    t += CTA
    return planos, voz, t


PLANOS, VOZ, DUR = linha_do_tempo()


def subs():
    out = []
    for k, t0, d in VOZ:
        txt = FALAS[k][2]
        palavras = txt.split()
        partes, cur = [], []
        for w in palavras:
            cur.append(w)
            if len(" ".join(cur)) > 30:
                partes.append(" ".join(cur))
                cur = []
        if cur:
            partes.append(" ".join(cur))
        tot = sum(len(p) for p in partes)
        acc = 0
        for p in partes:
            a = t0 + 0.1 + (d - 0.2) * acc / tot
            acc += len(p)
            b = t0 + 0.1 + (d - 0.2) * acc / tot
            out.append((a, b, p))
    return out


SUBS = subs()


def base_video(path):
    """Corta, gira, enquadra em 1080x1920 e trata a cor de cada plano; junta tudo sem áudio."""
    tmp = os.path.join(OUT, "planos")
    os.makedirs(tmp, exist_ok=True)
    lst = []
    for i, (t0, d, arq, ini) in enumerate(PLANOS):
        p = os.path.join(tmp, f"p{i:02d}.mp4")
        if arq == "mosaico":
            mosaico(p, d)
            lst.append(p)
            continue
        vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},{GRADE}"
        subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-ss", f"{ini:.3f}", "-i", os.path.join(BR, arq), "-t",
                        f"{d:.3f}", "-an", "-vf", vf, "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-pix_fmt",
                        "yuv420p", p], check=True)
        lst.append(p)
    with open(os.path.join(tmp, "lista.txt"), "w") as f:
        f.writelines(f"file '{p}'\n" for p in lst)
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i",
                    os.path.join(tmp, "lista.txt"), "-c", "copy", path], check=True)


MOSAICO = [("v2.mp4", 4.0), ("v6.mp4", 6.6), ("v8.mp4", 3.0), ("v4.mp4", 3.0)]


def mosaico(p, d):
    """Fundo do CTA: as 4 cenas que ele gravou em grade 2x2, escurecidas para os textos lerem bem."""
    ins = []
    for arq, ini in MOSAICO:
        ins += ["-ss", f"{ini:.2f}", "-t", f"{d:.3f}", "-i", os.path.join(BR, arq)]
    w2, h2 = W // 2, H // 2
    f = ";".join(f"[{i}:v]scale={w2}:{h2}:force_original_aspect_ratio=increase,crop={w2}:{h2},fps={FPS},{GRADE}[m{i}]"
                 for i in range(4))
    f += ";[m0][m1]hstack[top];[m2][m3]hstack[bot];[top][bot]vstack,eq=brightness=-0.22:saturation=0.85,gblur=sigma=6"
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error"] + ins + ["-filter_complex", f, "-t", f"{d:.3f}", "-an",
                    "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-pix_fmt", "yuv420p", p], check=True)


def vozes():
    arqs = []
    for k, (_, (a, b), _) in enumerate(FALAS):
        p = os.path.join(OUT, f"voz_{k + 1}.wav")
        subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i",
                        os.path.join(BR, "v0.mp4"), "-vn", "-ac", "1", "-ar", "48000", "-af",
                        VOZ_CADEIA + ",aresample=44100,afade=t=in:d=0.05,afade=t=out:st=%.2f:d=0.12" % (b - a - 0.12),
                        p], check=True)
        arqs.append((p, VOZ[k][1]))
    return arqs


def overlay(t, com_legenda):
    """Camada transparente com textos, nomes dos jogos, legenda, logo e CTA."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if t < GANCHO:
        cola(img, letreiro("4 JOGOS PRA\nCRIANÇADA", 118, AMARELO, INK, 14), 540, 560, -3, pop(t, -0.3))
        cola(img, letreiro("largar o celular", 70, WHITE, INK, 10, "Poppins-Black.ttf"), 500, 800, 2, pop(t, 0.1))
        cola(img, emoji("📵", 100), 900, 800, 0, pop(t, 0.2))
    for k, t0, d in VOZ:
        if t0 <= t < t0 + d:
            nome = FALAS[k][0]
            cola(img, pilula(f"{k + 1}/4", 40, INK), 160, 230, 0, pop(t, t0))
            cola(img, pilula(nome.upper(), 54, (249, 115, 22)), 540, 1450, -2, pop(t, t0 + 0.1))
    tc = VOZ[-1][1] + VOZ[-1][2] + 0.15
    if tc <= t < tc + COMENTA:
        b = 1 + 0.04 * abs(math.sin(t * 6))
        cola(img, letreiro("QUAL SEU FILHO\nIA AMAR?", 104, AMARELO, INK, 14), 540, 760, -2, pop(t, tc))
        cola(img, letreiro("COMENTA AQUI!", 84, WHITE, INK, 12), 500, 1040, 2, pop(t, tc + 0.3) * b)
        cola(img, emoji("👇", 100), 920, 1050 + 12 * math.sin(t * 9), 0, pop(t, tc + 0.4))
    ta = tc + COMENTA
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
    if com_legenda:
        legenda(img, SUBS, t)
    return img


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
        fr = Image.frombytes("RGB", (W, H), buf).convert("RGBA")
        fr.alpha_composite(overlay(n / FPS, com_legenda))
        wr.stdin.write(fr.convert("RGB").tobytes())
        n += 1
    wr.stdin.close()
    wr.wait()
    print("ok:", saida, n, "quadros", flush=True)


def cues():
    c = [(0.0, "whoosh", 0.4), (0.0, "pop", 0.4)]
    for k, t0, d in VOZ:
        c += [(t0, "pop", 0.3), (t0 + FALA_ROSTO, "whoosh", 0.3)]
    tc = VOZ[-1][1] + VOZ[-1][2] + 0.15
    c += [(tc, "pop", 0.4), (tc + 0.3, "boing", 0.4), (tc + COMENTA, "whoosh", 0.4), (tc + COMENTA + 1.2, "ding", 0.5)]
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    base = os.path.join(OUT, "base.mp4")
    if not os.path.exists(base) or a.frame is None:
        base_video(base)
    if a.frame:
        ims = []
        for x in a.frame:
            r = subprocess.run([ffmpeg(), "-loglevel", "error", "-ss", f"{x:.3f}", "-i", base, "-frames:v", "1", "-f",
                                "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True)
            fr = Image.frombytes("RGB", (W, H), r.stdout[:W * H * 3]).convert("RGBA")
            fr.alpha_composite(overlay(x, True))
            ims.append(fr.convert("RGB"))
        folha(ims, os.path.join(OUT, "frames.jpg"))
        return
    wav = os.path.join(OUT, "trilha.wav")
    som.build(wav, DUR, cues(), musica="travessa", voz=vozes())
    compor(base, os.path.join(OUT, "criancas_com_legenda.mp4"), wav, True)
    compor(base, os.path.join(OUT, "criancas_sem_legenda.mp4"), wav, False)


if __name__ == "__main__":
    main()
