#!/usr/bin/env python3
"""Reels "Quando tem novata na loja:" (trend da referência brutos/perguntas/ref/referencia.mp4, fora do git):
a novata (com a Lila no colo) pergunta "Eric, quem mandou a novata...?" e, num chicote de câmera, corta pro Eric rindo
(o culpado). 4 perguntas × 4 risadas, intercaladas. Brutos (Drive, 11/out/2026) em brutos/perguntas/:

    perguntas: 090602 Bananagrams · 090724 Uno (2ª tentativa, com chicote no fim) · 091548 tapetes de Marrakech
               (2ª tentativa) · 091719 Coffee Rush
    Eric:      090022 na prateleira · 090102 em pé na mesa · 090212 andando no corredor com as caixas · 090311 sentado

Transição: chicote (borrão horizontal + deslocamento para a esquerda) na saída de um plano e na entrada do próximo.
Onde eles gravaram o movimento de câmera de verdade, o corte cai no meio do borrão real e o digital só completa.

    python3 novata.py --frame 1 4 8      # quadros de teste em out/frames.jpg
    python3 novata.py                    # out/novata_com_legenda.mp4 e out/novata_sem_legenda.mp4
"""
import argparse
import math
import os
import subprocess
import sys
import wave
from functools import lru_cache

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "..", "comum"))
from motor import W, H, FPS, WHITE, ease, pop, font, logo_card, cola, sombra, letreiro, pilula, folha, ffmpeg  # noqa
import som  # noqa: E402

BR = os.path.join(ROOT, "brutos", "perguntas")
OUT = os.path.join(ROOT, "out")
CX = os.path.join(ROOT, "assets", "perguntas")
INK = (20, 16, 30)
AMARELO = (255, 214, 70)
GRADE = ("hqdn3d=2.5:2:5:5,curves=all='0/0.012 0.25/0.245 0.5/0.52 0.75/0.775 1/0.98',"
         "eq=contrast=1.02:saturation=1.0:gamma=1.03,unsharp=5:5:0.45:5:5:0.0")
# (arquivo, início, fim, tipo, texto, fim da fala) — início = 1ª palavra (medido pela energia)
PLANOS = [
    ("20261011_090602", 3.47, 6.55, "Q", "Eric, quem mandou a novata descascar o Bananagrams?", 6.00),
    ("20261011_090022", 0.75, 3.83, "E", None, None),
    ("20261011_090724", 23.84, 27.40, "Q", "Eric, quem mandou a novata procurar o tabuleiro do Uno?", 26.97),
    ("20261011_090102", 0.85, 3.10, "E", None, None),
    ("20261011_091548", 22.36, 25.30, "Q", "Eric, quem mandou a novata varrer os tapetes de Marrakech?", 25.00),
    ("20261011_090212", 0.75, 3.45, "E", None, None),
    ("20261011_091719", 1.77, 4.95, "Q", "Eric, quem mandou a novata moer os grãos do Coffee Rush?", 4.62),
    ("20261011_090311", 0.85, 3.90, "E", None, None),
]
FIM = 3.2  # tela final
WHIP = 6   # quadros de borrão em cada lado do corte
CAIXAS = ["bananagrams", "uno", "marrakech", "coffee_rush"]


def nq(t0, d):
    return round((t0 + d) * FPS) - round(t0 * FPS)


def linha():
    out, t = [], 0.0
    for arq, a, b, tipo, txt, fala_fim in PLANOS:
        n = nq(t, b - a)
        out.append((t, n, arq, a, tipo, txt, fala_fim))
        t += n / FPS
    return out, t


TL, T_FIM = linha()
DUR = T_FIM + FIM


# ---------------------------------------------------------------- legenda (só nas perguntas)
def subs():
    """Palavras distribuídas pela fala (proporcional ao tamanho), em grupos de até 3, a falada em amarelo."""
    out = []
    for t0, n, arq, a, tipo, txt, fala_fim in TL:
        if tipo != "Q":
            continue
        ws = txt.split()
        dur = fala_fim - a
        peso = np.array([len(w) + 2 for w in ws], float)
        ini = np.concatenate([[0], np.cumsum(peso)[:-1]]) / peso.sum() * dur
        tw = [(w, t0 + s) for w, s in zip(ws, ini)]
        grupos, cur = [], []
        for w in tw:
            cur.append(w)
            if len(cur) == 3 or len(" ".join(x[0] for x in cur)) > 14 or w[0][-1] in ",?":
                grupos.append(cur)
                cur = []
        if cur:
            grupos.append(cur)
        for j, g in enumerate(grupos):
            fim = grupos[j + 1][0][1] if j + 1 < len(grupos) else t0 + dur + 0.35
            out.append((g[0][1], fim, g))
    return out


SUBS = subs()


@lru_cache(None)
def palavra_img(txt, amarela):
    return letreiro(txt.upper(), 84, AMARELO if amarela else WHITE, INK, 12, "Poppins-Black.ttf")


def legenda(img, t):
    for a, b, g in SUBS:
        if a <= t < b:
            agora = max(j for j, (_, w0) in enumerate(g) if w0 <= t or j == 0)
            ims = [palavra_img(w, j == agora) for j, (w, _) in enumerate(g)]
            gap, larg = 20, 960
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
            y = 1480 - (len(linhas) - 1) * 105
            for ln in linhas:
                lw = sum(x.width - 24 for x in ln) + gap * (len(ln) - 1)
                x = 540 - lw / 2
                for im in ln:
                    cola(img, im, x + (im.width - 24) / 2, y, 0, sc)
                    x += im.width - 24 + gap
                y += 110
            return


# ---------------------------------------------------------------- textos fixos e tela final
@lru_cache(None)
def topo():
    return letreiro("Quando tem novata na loja:", 64, WHITE, INK, 8, "Poppins-ExtraBold.ttf")


@lru_cache(None)
def caixa(nome, h):
    im = Image.open(os.path.join(CX, nome + ".png")).convert("RGBA")
    im = im.resize((max(2, int(im.width * h / im.height)), int(h)), Image.LANCZOS)
    return sombra(im, 14, (0, 12), 0.5)


def tela_final(img, t):
    u = t - T_FIM
    cola(img, logo_card(380), 540, 300, 0, pop(t, T_FIM))
    pos = {"uno": (290, 690, -6, 320), "marrakech": (540, 660, 0, 320), "coffee_rush": (790, 690, 6, 320),
           "bananagrams": (540, 880, -5, 165)}  # a banana na frente
    for j, n in enumerate(["uno", "marrakech", "coffee_rush", "bananagrams"]):
        x, y, r, h = pos[n]
        cola(img, caixa(n, h), x, y, r, pop(t, T_FIM + 0.15 + 0.08 * j))
    itens = [(0.5, letreiro("QUER JOGAR DE\nVERDADE?", 92, AMARELO, INK, 13), 1030),
             (0.8, letreiro("ALUGUE NA SUA VEZ!", 70, WHITE, INK, 11), 1210),
             (1.0, pilula("RESERVE ONLINE · RETIRE EM MAUÁ E ABC", 34, WHITE, INK, INK), 1330),
             (1.15, pilula("OU RECEBA EM CASA!", 42, (22, 163, 74)), 1430),
             (1.3, pilula("LINK NA BIO · @SUAVEZ_BG", 48, (249, 115, 22)), 1550)]
    for t0, im, y in itens:
        if u >= t0:
            cola(img, im, 540, y, 0, pop(t, T_FIM + t0))


def overlay(t, com_legenda):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if t < T_FIM:
        cola(img, topo(), 540, 300)
        wm = logo_card(150)
        img.alpha_composite(wm, (W - wm.width - 30, 40))
        if com_legenda:
            legenda(img, t)
    else:
        tela_final(img, t)
    return img


# ---------------------------------------------------------------- vídeo
def ler(arq, a, n):
    vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},{GRADE}"
    p = subprocess.Popen([ffmpeg(), "-loglevel", "error", "-ss", f"{a:.3f}", "-i", os.path.join(BR, arq + ".mp4"), "-frames:v",
                          str(n), "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    k = 0
    ultimo = None
    while k < n:
        buf = p.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        ultimo = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        yield ultimo
        k += 1
    while k < n:  # garante a contagem exata de quadros
        yield ultimo
        k += 1
    p.wait()


def chicote(fr, s):
    """s em [-1, 1]: <0 saindo (o quadro corre para a esquerda), >0 entrando (vem da direita). |s| = força."""
    f = abs(s)
    if f < 0.02:
        return fr
    pequeno = cv2.resize(fr, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    L = max(3, int(90 * f))
    k = np.ones((1, L), np.float32) / L
    b = cv2.filter2D(pequeno, -1, k, borderType=cv2.BORDER_REFLECT)
    b = cv2.resize(b, (W, H), interpolation=cv2.INTER_LINEAR)
    desl = int(-420 * f) if s < 0 else int(420 * f)
    b = cv2.warpAffine(b, np.float32([[1, 0, desl], [0, 1, 0]]), (W, H), borderMode=cv2.BORDER_REFLECT)
    return cv2.addWeighted(b, min(1.0, 0.35 + f), fr, max(0.0, 0.65 - f), 0)


def quadros():
    """Todos os quadros do vídeo, com o chicote nos cortes e a tela final."""
    ultimo = None
    for i, (t0, n, arq, a, tipo, txt, ff) in enumerate(TL):
        for k, fr in enumerate(ler(arq, a, n)):
            s = 0.0
            if i > 0 and k < WHIP:
                s = (1 - k / WHIP) ** 1.5
            if k >= n - WHIP:
                s = -(((k - (n - WHIP)) + 1) / WHIP) ** 1.5
            ultimo = fr
            yield chicote(fr, s)
    fundo = Image.fromarray(ultimo).filter(ImageFilter.GaussianBlur(18))
    fundo = Image.blend(fundo, Image.new("RGB", (W, H), (10, 8, 20)), 0.55)
    fa = np.asarray(fundo)
    for k in range(round(FIM * FPS)):
        yield chicote(fa, max(0.0, 1 - k / WHIP) ** 1.5) if k < WHIP else fa


# ---------------------------------------------------------------- áudio
def ler_audio(arq, a, d):
    r = subprocess.run([ffmpeg(), "-loglevel", "error", "-ss", f"{a:.3f}", "-t", f"{d:.4f}", "-i",
                        os.path.join(BR, arq + ".mp4"), "-vn", "-ac", "1", "-ar", "44100", "-af",
                        "highpass=f=80,afftdn=nr=10:nf=-45", "-f", "s16le", "-"], capture_output=True)
    x = np.frombuffer(r.stdout, np.int16).astype(np.float64) / 32768
    n = int(round(d * 44100))
    return np.pad(x, (0, max(0, n - len(x))))[:n]


def nivel(x, alvo):
    q = int(0.03 * 44100)
    e = np.sqrt(np.convolve(x ** 2, np.ones(q) / q, "same"))
    voz = e > e.max() * 0.1
    if not voz.any():
        return x
    return x * 10 ** (alvo / 20) / (np.sqrt((x[voz] ** 2).mean()) + 1e-9)


def audio(path):
    sr = 44100
    voz = np.zeros(int(DUR * sr) + sr)
    for t0, n, arq, a, tipo, txt, ff in TL:
        d = n / FPS
        x = nivel(ler_audio(arq, a, d), -19 if tipo == "Q" else -22)
        f = int(0.03 * sr)
        x[:f] *= np.linspace(0, 1, f)
        x[-f:] *= np.linspace(1, 0, f)
        i = int(round(t0 * sr))
        voz[i:i + len(x)] += x
    vp = os.path.join(OUT, "novata_voz.wav")
    with wave.open(vp, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.clip(voz, -1, 1) * 32767).astype(np.int16).tobytes())
    cues = [(t0 - 0.12, "whoosh", 0.55) for t0, *_ in TL[1:]] + [(T_FIM - 0.1, "whoosh", 0.55), (T_FIM + 1.3, "ding", 0.5)]
    som.build(path, DUR, cues, musica="travessa", voz=[(vp, 0.0)], fx_ganho=0.35, duck=0.85, musica_ganho=0.10,
              satura=False)
    r = subprocess.run([ffmpeg(), "-hide_banner", "-i", path, "-af", "loudnorm=I=-15.5:TP=-2:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    import json
    m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    tmp = path.replace(".wav", "_n.wav")
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", path, "-af",
                    f"loudnorm=I=-15.5:TP=-2:LRA=11:linear=true:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
                    f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}",
                    "-ar", "44100", tmp], check=True)
    os.replace(tmp, path)


def render(saidas, wav):
    ws = {}
    for saida, leg in saidas:
        ws[leg] = subprocess.Popen([ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s",
                                    f"{W}x{H}", "-framerate", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-crf",
                                    "18", "-preset", "medium", "-tune", "film", "-pix_fmt", "yuv420p", "-c:a", "aac",
                                    "-b:a", "192k", "-shortest", "-movflags", "+faststart", saida], stdin=subprocess.PIPE)
    for n, fr in enumerate(quadros()):
        t = n / FPS
        base = Image.fromarray(fr).convert("RGBA")
        for leg, p in ws.items():
            im = base.copy()
            im.alpha_composite(overlay(t, leg))
            p.stdin.write(im.convert("RGB").tobytes())
    for p in ws.values():
        p.stdin.close()
        p.wait()
    print("ok", [s for s, _ in saidas], flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    print(f"duração {DUR:.1f} s; planos em", [round(p[0], 2) for p in TL])
    if a.frame:
        alvo = {round(x * FPS): x for x in a.frame}
        ims = {}
        for n, fr in enumerate(quadros()):
            if n in alvo:
                im = Image.fromarray(fr).convert("RGBA")
                im.alpha_composite(overlay(n / FPS, True))
                ims[n] = im.convert("RGB")
            if len(ims) == len(alvo):
                break
        folha([ims[k] for k in sorted(ims)], os.path.join(OUT, "frames.jpg"))
        return
    wav = os.path.join(OUT, "novata.wav")
    audio(wav)
    render([(os.path.join(OUT, "novata_com_legenda.mp4"), True), (os.path.join(OUT, "novata_sem_legenda.mp4"), False)], wav)


if __name__ == "__main__":
    main()
