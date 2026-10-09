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
from motor import (W, H, FPS, WHITE, seg, ease, lerp, pop, font, emoji, logo_card, cola, letreiro, pilula,  # noqa
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
VOZ_CADEIA = ("highpass=f=75,equalizer=f=300:t=q:w=1:g=-2,"
              "acompressor=threshold=-24dB:ratio=2:attack=10:release=200:makeup=1.5,"
              "loudnorm=I=-16:TP=-1.5:LRA=7")
GRADE = "hqdn3d=1.5:1.5:3:3,eq=contrast=1.03:saturation=1.05:gamma=1.02,colorbalance=rm=-0.02:bm=0.02,unsharp=3:3:0.3"
GRADE_ROSTO = "hqdn3d=1.5:1.5:3:3,eq=contrast=1.02:saturation=0.98:gamma=1.04,colorbalance=rm=-0.03:bm=0.02,unsharp=3:3:0.25"
# falas boas (arquivo, início, fim) e o texto que ele falou
INTRO = ("vg.mp4", (11.15, 16.35), "A gente separou quatro ótimos jogos pra jogar com os pequenos no Dia das Crianças!")
FALAS = [
    ("Go Cuckoo!", ("v0.mp4", 4.60, 10.95), "E o primeiro da lista é o Go Cuckoo, um jogo onde a gente precisa montar um "
                                             "ninho perfeito pra que a Kiki possa botar os seus ovos."),
    ("Gravity Superstar", ("v0.mp4", 18.55, 24.85), "E o segundo é o Gravity Stars, um jogo onde viramos astronautas em "
                                                     "busca de pequenas estrelas coloridas."),
    ("Draftosaurus", ("v0.mp4", 51.55, 57.75), "Também separamos o Draftosaurus, o jogo onde a gente monta o nosso "
                                                "próprio parque de dinossauros. Ótimo para os pequeninos!"),
    ("Scooby-Doo!", ("v0.mp4", 60.50, 66.40), "E por último, o jogo Scooby-Doo Board Game, onde a família se une pra "
                                               "derrotar o monstro da semana."),
]
FALA_ROSTO = 1.7  # segundos com ele falando antes de cortar para as cenas do jogo
# cenas de cada jogo: (arquivo, início) — encaixadas em sequência até o fim da fala
CENAS = [[("v2.mp4", 1.6), ("v3.mp4", 8.0)], [("v7.mp4", 1.0), ("v6.mp4", 3.5)],
         [("v8.mp4", 2.2), ("v8.mp4", 8.5)], [("v4.mp4", 1.6), ("v5.mp4", 1.8)]]
# gancho (pedido dele): a ÚLTIMA vez que ele chega pertinho da câmera ajeitando, com um movimento de câmera de efeito
GANCHO_ARQ, GANCHO_INI, GANCHO = "vg.mp4", 8.45, 2.70
INTRO_ROSTO = 1.9  # na fala de abertura, depois disso entra uma montagem rápida dos 4 jogos
MONTAGEM = [("v3.mp4", 2.2), ("v7.mp4", 0.6), ("v8.mp4", 4.0), ("v5.mp4", 2.4)]
COMENTA = 2.6
CTA = 3.6


def linha_do_tempo():
    """Planos [(t0, dur, arquivo, início no arquivo)] e falas [(índice, t0, dur)] (índice -1 = abertura)."""
    planos, voz = [], []
    a, b = INTRO[1]
    planos.append((0.0, GANCHO + INTRO_ROSTO, GANCHO_ARQ, GANCHO_INI))  # gancho e abertura: mesma tomada
    voz.append((-1, GANCHO, b - a))
    resto = (b - a) - INTRO_ROSTO
    for j, (arq, ini) in enumerate(MONTAGEM):
        dd = resto / len(MONTAGEM)
        planos.append((GANCHO + INTRO_ROSTO + j * dd, dd, arq, ini))
    t = GANCHO + (b - a) + 0.2
    for k, (_, (arq0, a, b), _) in enumerate(FALAS):
        d = b - a
        voz.append((k, t, d))
        planos.append((t, FALA_ROSTO, arq0, a))
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


def fala(k):
    """(arquivo, início, fim, texto) da fala k (-1 = abertura)."""
    if k < 0:
        return INTRO[0], INTRO[1][0], INTRO[1][1], INTRO[2]
    nome, (arq, a, b), txt = FALAS[k]
    return arq, a, b, txt


PLANOS, VOZ, DUR = linha_do_tempo()


# palavras com os tempos reais (faster-whisper medium, revisadas): palavras.json, uma lista por fala de VOZ
CORRIGE = {"kiki": "Kiki", "Scooby": "Scooby-Doo", "-Doo": None, "para": "pra"}


def subs():
    """Legenda estilo Reels: 1 a 3 palavras por vez, palavra falada em amarelo (tempos reais da voz)."""
    pals = json.load(open(os.path.join(ROOT, "palavras.json"), encoding="utf-8"))
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
        g = GRADE_ROSTO if arq in ("v0.mp4", "vg.mp4") else GRADE
        vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},{g}"
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
    for i, (k, t0, d) in enumerate(VOZ):
        arq, a, b, _ = fala(k)
        p = os.path.join(OUT, f"voz_{i}.wav")
        subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i",
                        os.path.join(BR, arq), "-vn", "-ac", "1", "-ar", "44100", "-af",
                        VOZ_CADEIA + ",afade=t=in:d=0.05,afade=t=out:st=%.2f:d=0.12" % (b - a - 0.12),
                        p], check=True)
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
    if arq == "v0.mp4":  # rosto: cada fala num enquadramento (aberto / fechado), com empurrão leve
        z = (1.06 if i % 2 else 1.16) + 0.03 * u
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
    y0 = (H - h) * (0.42 if PLANOS[i][2] == "v0.mp4" else 0.5)  # no rosto, sobe um pouco para não cortar a cabeça
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
            gap = 22
            tot = sum(x.width for x in ims) + gap * (len(ims) - 1) - 24 * len(ims)
            linhas = [ims] if tot <= 980 else [ims[:2], ims[2:]]
            sc = 0.85 + 0.15 * ease(min(1.0, (t - a) / 0.12))
            y = 1300 - (len(linhas) - 1) * 55
            for ln in linhas:
                lw = sum(x.width - 24 for x in ln) + gap * (len(ln) - 1)
                x = 540 - lw / 2
                for im in ln:
                    cola(img, im, x + (im.width - 24) / 2, y, 0, sc)
                    x += im.width - 24 + gap
                y += 115
            return


def overlay(t, com_legenda):
    """Camada transparente com textos, nomes dos jogos, legenda, logo e CTA."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if t < GANCHO + 0.4:
        sai = seg(t, GANCHO, GANCHO + 0.4)
        cola(img, letreiro("JOGOS PRO DIA\nDAS CRIANÇAS", 112, AMARELO, INK, 14), 540, 1380, -3, pop(t, -0.3), 1 - sai)
        cola(img, emoji("🎈", 120), 900, 1170, 12 * math.sin(t * 4), pop(t, 0.15), 1 - sai)
    for k, t0, d in VOZ:
        if k >= 0 and t0 <= t < t0 + d:
            nome = FALAS[k][0]
            cola(img, pilula(f"JOGO {k + 1}/4", 38, INK), 540, 230, 0, pop(t, t0))
            cola(img, pilula(nome.upper(), 60, (249, 115, 22)), 540, 340, -2, pop(t, t0 + 0.1))
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
    if com_legenda and GANCHO + 0.3 <= t < tc:
        legenda_viva(img, t)
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
            fr = camera(Image.frombytes("RGB", (W, H), r.stdout[:W * H * 3]), x).convert("RGBA")
            fr.alpha_composite(overlay(x, True))
            ims.append(fr.convert("RGB"))
        folha(ims, os.path.join(OUT, "frames.jpg"))
        return
    wav = os.path.join(OUT, "trilha.wav")
    som.build(wav, DUR, cues(), musica="travessa", voz=vozes(), fx_ganho=0.35, duck=0.8, musica_ganho=0.2)
    compor(base, os.path.join(OUT, "criancas_com_legenda.mp4"), wav, True)
    compor(base, os.path.join(OUT, "criancas_sem_legenda.mp4"), wav, False)


if __name__ == "__main__":
    main()
