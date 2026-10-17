#!/usr/bin/env python3
"""Reels do TRIAL BY TROLLEY feito com os STORIES dele de 14/out/2026 (mandados pelo chat em 17/out; brutos fora do git
em brutos/stories1014/, 720x1280 já comprimidos pelo Instagram). Ele mostra a caixa na estante e explica a dinâmica na
mesa (dois inocentes e um culpado em cada trilho, modificadores, alguém decide por onde o bondinho passa).
O que era só de story saiu: "ele vai entrar no nosso site essa semana" (já entrou) e "no próximo story / posto uma
votação" (a votação vira "Comenta: de cima ou de baixo?"). Legenda palavra a palavra com o texto das cartas conferido
nos quadros (o Whisper errou "freiras se divertindo", "abelhas", "terças-feiras"...).

    python3 trolley.py --frame 1 10 40     # out/frames_trolley.jpg
    python3 trolley.py                     # out/trolley.mp4
"""
import argparse
import json
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

BR = os.path.join(ROOT, "brutos", "stories1014")
OUT = os.path.join(ROOT, "out")
ARQ = {"a": "VID_20261014_154316_033", "b": "VID_20261014_154320_767", "c": "VID_20261014_154325_705"}
WAV = {"a": "154316", "b": "154320", "c": "154325"}
INK, AMARELO, VERMELHO, VERDE = (20, 16, 30), (255, 214, 70), (214, 46, 52), (40, 160, 90)
# 720p do Instagram → 1080p: lanczos + nitidez leve; cor quase intocada (lição: em gravado, mexer pouco)
GRADE = "scale=1080:1920:flags=lanczos,hqdn3d=1.5:1.5:3:3,unsharp=5:5:0.45:5:5:0.0,eq=contrast=1.02:saturation=1.02"
VOZ = "highpass=f=80,afftdn=nr=8:nf=-48,equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1.4:g=1.5"
# (fonte, início, fim, tipo) — tempos no bruto de cada story
TRECHOS = [
    ("a", 0.00, 2.45, "gancho"),   # "Eu acabei de lembrar que eu quero mostrar um jogo pra vocês."
    ("a", 3.70, 5.70, "caixa"),    # "Ele tá aqui."
    ("a", 8.00, 9.75, "caixa"),    # "O Trial by Trolley."  (o "vai entrar no site essa semana" saiu: já entrou)
    ("a", 14.70, 17.20, "caixa"),  # "Mas eu quero mostrar pra vocês a dinâmica dele."
    ("b", 0.00, 43.05, "mesa"),    # a regra e o trilho de cima (sem o "no próximo mostro o de baixo")
    ("c", 0.00, 27.15, "mesa"),    # o trilho de baixo e "ainda falta os modificadores"
    ("c", 28.60, 49.10, "mesa"),   # (sem "que é aquele montinho ali") os modificadores e "vou deixar vocês decidirem"
]
CORRIGE = {("b", 14.2): "Trolley,", ("b", 16.3): "o", ("b", 29.7): "freiras", ("b", 30.5): "se", ("b", 30.7): None,
           ("b", 30.8): "divertindo,", ("b", 40.7): "abelhas", ("c", 3.6): "inocentes,", ("c", 36.3): "terças-feiras,",
           ("c", 37.0): "ensina", ("a", 8.4): "Trial", ("a", 8.9): "by", ("a", 9.1): "Trolley.", ("c", 44.6): None,
           ("c", 44.5): "pré-escola,"}
GAP, PAD = 0.32, 0.1
VEL = 1.1  # fala e mão 10% mais rápidas (os 3 stories somavam ~1:30)
COMENTA, FIM = 3.4, 3.8


# ---------------------------------------------------------------- cortes pela energia
@lru_cache(None)
def energia(src):
    w = wave.open(os.path.join(BR, WAV[src] + ".wav"))
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
    q = int(0.02 * w.getframerate())
    n = len(x) // q
    return 20 * np.log10(np.sqrt((x[:n * q].reshape(n, q) ** 2).mean(1)) + 1e-9)


@lru_cache(None)
def palavras(src):
    return json.load(open(os.path.join(BR, WAV[src] + "_palavras.json"), encoding="utf-8"))


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
    for j, (src, a, b, tipo) in enumerate(TRECHOS):
        marcas.setdefault(tipo, t)
        for ta, tb in pedacos(src, a, b):
            n = nq(t, (tb - ta) / VEL)
            tl.append(dict(t0=t, n=n, src=src, a=ta, j=j, tipo=tipo))
            t += n / FPS
    marcas["comenta"] = t
    marcas["fim"] = t + COMENTA
    return tl, marcas, t + COMENTA + FIM


TL, M, DUR = linha()


# ---------------------------------------------------------------- legenda palavra a palavra
def subs():
    pal = []
    for p in TL:
        a, b = p["a"], p["a"] + p["n"] / FPS * VEL
        for w in palavras(p["src"]):
            if a <= (w["s"] + w["e"]) / 2 < b:
                txt = CORRIGE.get((p["src"], round(w["s"], 1)), w["w"])
                if txt:
                    pal.append((txt, p["t0"] + max(0.0, w["s"] - a) / VEL, p["t0"] + (min(b, w["e"]) - a) / VEL))
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


# ---------------------------------------------------------------- textos
@lru_cache(None)
def pilula(txt, s, cor, fg=WHITE):
    tx = texto(txt, "lilita", s, fg)
    im = Image.new("RGBA", (tx.width + 40, tx.height + 8), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=im.height // 2, fill=cor,
                                          outline=INK, width=6)
    im.alpha_composite(tx, (20, 4))
    return im


@lru_cache(None)
def gancho_img():
    return texto("VOCÊ DESVIARIA\nO BONDINHO?", "lilita", 104, WHITE, INK, 9, 8, INK, entre=1.05)


def overlay(t):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if t >= M["fim"]:
        tela_final(img, t - M["fim"])
        return img
    img.alpha_composite(logo_card(150), (W - 186, 46))
    if t < M["caixa"]:
        cola(img, gancho_img(), W / 2, 1180, rot=-2, sc=out_back(seg(t, 0.0, 0.4)))
    elif t < M["mesa"]:
        u = out_back(seg(t, M["caixa"], M["caixa"] + 0.4))
        cola(img, pilula("JÁ NO SITE DA SUA VEZ!", 54, VERDE), W / 2, 250, rot=-2, sc=u)
    elif t < M["comenta"]:
        u = out_back(seg(t, M["mesa"], M["mesa"] + 0.4))
        cola(img, pilula("TRIAL BY TROLLEY · 3 A 13 JOGADORES", 42, VERMELHO), W / 2, 230, sc=u)
    else:
        lt = t - M["comenta"]
        cola(img, texto("POR ONDE O\nBONDINHO PASSA?", "lilita", 104, WHITE, INK, 9, 8, INK, entre=1.05), W / 2, 760,
             rot=-2, sc=out_back(seg(lt, 0.0, 0.4)))
        cola(img, pilula("DE CIMA", 64, (28, 124, 150)), W / 2 - 200, 1010, rot=-3, sc=out_back(seg(lt, 0.4, 0.7)))
        cola(img, pilula("DE BAIXO", 64, (219, 39, 119)), W / 2 + 200, 1010, rot=3, sc=out_back(seg(lt, 0.55, 0.85)))
        cola(img, texto("Comenta aqui!", "lilita", 80, AMARELO, INK, 7, 6, INK), W / 2, 1200, sc=out_back(seg(lt, 0.9, 1.2)))
        return img
    legenda(img, t)
    return img


def tela_final(img, lt):
    cola(img, logo_card(420), W / 2, 300, sc=out_back(seg(lt, 0.0, 0.4)))
    cola(img, foto("trial_by_trolley", 600, borda=12, raio=26, sombra_a=0.5), W / 2, 790, rot=-2,
         sc=out_back(seg(lt, 0.15, 0.5)))
    v = ease(seg(lt, 0.5, 0.9))
    linhas = [("ALUGUE O TRIAL BY TROLLEY", "lilita", 70, AMARELO), ("3 a 13 jogadores · 5 dias de jogo", "figtree", 46, WHITE),
              ("RESERVE ONLINE · RETIRE EM MAUÁ\nOU RECEBA EM CASA", "figtree", 44, WHITE),
              ("LINK NA BIO · @SUAVEZ_BG", "lilita", 58, WHITE)]
    for j, (txt, f, s, cor) in enumerate(linhas):
        cola(img, texto(txt, f, s, cor, INK, 6 if f == "lilita" else 0, 5 if f == "lilita" else 3, INK, entre=1.2),
             W / 2, 1170 + j * 135 + (30 if j >= 2 else 0), alpha=v)


# ---------------------------------------------------------------- vídeo
def ler(src, a, n):
    p = subprocess.Popen([ffmpeg(), "-loglevel", "error", "-ss", f"{a:.3f}", "-i", os.path.join(BR, ARQ[src] + ".mp4"),
                          "-frames:v", str(n), "-vf", f"setpts=PTS/{VEL},fps={FPS},{GRADE}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         stdout=subprocess.PIPE)
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


def quadros():
    ultimo = None
    for p in TL:
        for fr in ler(p["src"], p["a"], p["n"]):
            ultimo = fr
            yield fr
    # "comenta": a mesa montada com os dois trilhos (fim do story c), escurecida
    mesa = next(iter(ler("c", 47.5, 1)))
    base = Image.blend(Image.fromarray(mesa), Image.new("RGB", (W, H), (10, 10, 20)), 0.45)
    for _ in range(round(COMENTA * FPS)):
        yield np.asarray(base)
    fundo = Image.fromarray(ultimo).filter(ImageFilter.GaussianBlur(22))
    fundo = np.asarray(Image.blend(fundo, Image.new("RGB", (W, H), (40, 14, 20)), 0.62))
    for _ in range(round(FIM * FPS) + 2):
        yield fundo


# ---------------------------------------------------------------- áudio
def ler_audio(src, a, d):
    """d = duração na SAÍDA; lê d·VEL do bruto e acelera com atempo (tom preservado)."""
    r = subprocess.run([ffmpeg(), "-loglevel", "error", "-ss", f"{a:.3f}", "-t", f"{d * VEL + 0.05:.4f}", "-i",
                        os.path.join(BR, ARQ[src] + ".mp4"), "-vn", "-ac", "1", "-ar", "44100", "-af",
                        VOZ + f",atempo={VEL}", "-f", "s16le",
                        "-"], capture_output=True)
    x = np.frombuffer(r.stdout, np.int16).astype(np.float64) / 32768
    n = int(round(d * 44100))
    return np.pad(x, (0, max(0, n - len(x))))[:n]


def audio(path):
    sr = 44100
    pecas = [(p, ler_audio(p["src"], p["a"], p["n"] / FPS)) for p in TL]
    ganhos = {}
    for src in ARQ:
        xs = [x for p, x in pecas if p["src"] == src]
        if xs:
            tudo = np.concatenate(xs)
            q = int(0.03 * sr)
            e = np.sqrt(np.convolve(tudo ** 2, np.ones(q) / q, "same"))
            ganhos[src] = 10 ** (-20 / 20) / (np.sqrt((tudo[e > e.max() * 0.12] ** 2).mean()) + 1e-9)
    voz = np.zeros(int(DUR * sr) + sr)
    for p, x in pecas:
        x = x * ganhos[p["src"]]
        f = int(0.015 * sr)
        x[:f] *= np.linspace(0, 1, f)
        x[-f:] *= np.linspace(1, 0, f)
        i = int(round(p["t0"] * sr))
        voz[i:i + len(x)] += x
    cues = [(0.0, "pop", 0.4), (M["caixa"], "whoosh", 0.35), (M["mesa"], "whoosh", 0.35), (M["comenta"], "reveal", 0.6),
            (M["comenta"] + 0.45, "pop", 0.5), (M["comenta"] + 0.6, "pop", 0.5), (M["fim"], "whoosh", 0.4),
            (M["fim"] + 0.5, "ding", 0.5)]
    vp = os.path.join(OUT, "trolley_voz.wav")
    with wave.open(vp, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.clip(voz, -1, 1) * 32767).astype(np.int16).tobytes())
    som.build(path, DUR, cues, musica="travessa", voz=[(vp, 0.0)], fx_ganho=0.35, duck=0.55, musica_ganho=0.22,
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
    print(f"duração {DUR:.1f} s", {k: round(v, 1) for k, v in M.items()})
    if a.info:
        for p in TL:
            print(f"{p['t0']:6.2f} {p['n'] / FPS:5.2f} {p['src']} {p['a']:.2f}")
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
        folha([ims[k] for k in sorted(ims)], os.path.join(OUT, "frames_trolley.jpg"))
        return
    wav = os.path.join(OUT, "trolley.wav")
    audio(wav)
    render(os.path.join(OUT, "trolley.mp4"), wav)


if __name__ == "__main__":
    main()
