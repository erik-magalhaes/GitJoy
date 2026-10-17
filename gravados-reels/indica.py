#!/usr/bin/env python3
"""Reels "ME DIZ O QUE VOCÊ GOSTA DE FAZER QUE EU TE INDICO UM JOGO" (17/out/2026, gravado pelo Erik).
Brutos (fora do git) em brutos/out17/: 20261017_133810.mp4 (ele falando, 5 min, várias tentativas; uso a ÚLTIMA boa
de cada fala) e as cenas na mesa: Art Society (134947), Passaporte Mundo (135233), Critter Kitchen (135550), Canvas
(135716) e Unlock! (140020) e Sushi Go! (140828, ele mandou depois).
Edição (lições do criancas2): rosto livre; capa do SITE pequena no canto quando ele FALA o nome; o rosto só até ~0,9 s
depois do nome e daí a cena do jogo em tela cheia com nome + jogadores/tempo (do site); legenda palavra a palavra;
pausas longas viram corte seco; "comenta" e CTA com ele falando; tela final com os 6 jogos.

    python3 indica.py --frame 2 9 20       # out/frames_indica.jpg
    python3 indica.py                      # out/indica.mp4
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

BR = os.path.join(ROOT, "brutos", "out17")
FALA = os.path.join(BR, "20261017_133810.mp4")
OUT = os.path.join(ROOT, "out")
INK, AMARELO, PETROLEO = (20, 16, 30), (255, 214, 70), (28, 124, 150)
GRADE = ("hqdn3d=2:1.5:4:4,curves=all='0/0.01 0.25/0.245 0.5/0.5 0.75/0.75 1/0.965',"
         "eq=contrast=1.02:saturation=0.98,unsharp=5:5:0.35:5:5:0.0")
VOZ = "highpass=f=80,afftdn=nr=8:nf=-48,equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1.4:g=1.5"
# (tipo, início, fim, jogo) — tempos no bruto da fala; a última tentativa boa de cada uma
FALAS = [
    ("gancho", 31.40, 34.60, None),
    ("jogo", 35.00, 42.30, "critter"),
    ("jogo", 59.70, 67.70, "sushi"),
    ("jogo", 114.40, 121.50, "canvas"),  # a última (125–134) tem 3 s estranhos no "artística"
    ("jogo", 156.30, 164.45, "art"),
    ("jogo", 179.55, 186.35, "passaporte"),
    ("jogo", 264.75, 272.50, "unlock"),
    ("comenta", 281.40, 286.60, None),
    ("cta", 290.90, 294.85, None),
]
CANVAS_T = 116.98
JOGOS = {  # foto do site, nome, linha do site, gosto, cena na mesa (arquivo, início), tempo do nome no bruto
    "critter": ("critter_kitchen", "Critter Kitchen", "1 a 5 jogadores · 60 min", "COZINHAR", ("135550", 0.3), 37.46),
    "sushi": ("sushi_go", "Sushi Go!", "2 a 5 jogadores · 15 min", "COMER", ("140828", 0.2), 62.88),
    "canvas": ("canvas", "Canvas", "1 a 5 jogadores · 30 min", "PINTAR", ("135716", 0.3), CANVAS_T),
    "art": ("art_society", "Art Society", "2 a 4 jogadores · 60 min", "ARTE", ("134947", 0.2), 160.18),
    "passaporte": ("passaporte_mundo", "Passaporte Mundo", "1 a 6 jogadores · 45 min", "VIAJAR", ("135233", 0.2), 181.48),
    "unlock": ("unlock_timeless_adventures", "Unlock!", "1 a 6 jogadores · 90 min", "ESCAPE ROOM", ("140020", 0.2), 267.28),
}
CORRIGE = {37.86: "Kitchen,", 64.32: "passa", 64.74: "numa", 66.88: "combo", 116.98: "Canvas.", 185.08: "encaixa",
           293.00: "Sua", 293.18: "Vez."}
DEPOIS_NOME = 0.9  # rosto até 0,9 s depois de ele começar a dizer o nome; depois, a cena do jogo
GAP, PAD = 0.32, 0.1
FIM = 3.6


# ---------------------------------------------------------------- cortes pela energia
@lru_cache(None)
def energia():
    w = wave.open(os.path.join(BR, "133810.wav"))
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
    q = int(0.02 * w.getframerate())
    n = len(x) // q
    return 20 * np.log10(np.sqrt((x[:n * q].reshape(n, q) ** 2).mean(1)) + 1e-9)


@lru_cache(None)
def palavras():
    return json.load(open(os.path.join(BR, "133810_palavras.json"), encoding="utf-8"))


def pedacos(a, b):
    e = energia()
    i0, i1 = int(a / 0.02), int(b / 0.02)
    piso = np.percentile(e[e > -90], 15)
    voz = e[i0:i1] > max(piso + 15, -38)
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
        tem_palavra = any(ta <= (w["s"] + min(w["e"], w["s"] + 0.6)) / 2 < tb for w in palavras())
        if tb - ta > 0.15 and tem_palavra:
            res.append((ta, tb))
    return res


def nq(t0, d):
    return round((t0 + d) * FPS) - round(t0 * FPS)


def linha():
    """Planos: (t0, n, a no bruto da fala, fala j). Marcas: início de cada fala e onde entra a cena do jogo."""
    tl, t, marcas = [], 0.0, {}
    for j, (tipo, a, b, jogo) in enumerate(FALAS):
        marcas[f"f{j}"] = t
        for k, (ta, tb) in enumerate(pedacos(a, b)):
            n = nq(t, tb - ta)
            tl.append(dict(t0=t, n=n, a=ta, j=j, punch=(len(tl) % 2)))
            t += n / FPS
        marcas[f"f{j}_fim"] = t
    marcas["fim"] = t
    return tl, marcas, t + FIM


TL, M, DUR = linha()


def bruto_para_saida(tb):
    for p in TL:
        if p["a"] <= tb < p["a"] + p["n"] / FPS:
            return p["t0"] + tb - p["a"]
    return None


def corte_cena(j):
    """Tempo de saída em que entra a cena na mesa (rosto até o nome + DEPOIS_NOME)."""
    jogo = FALAS[j][3]
    t = bruto_para_saida(JOGOS[jogo][5])
    return (t if t is not None else M[f"f{j}"]) + DEPOIS_NOME


def plano_em(t):
    for p in TL:
        if p["t0"] <= t < p["t0"] + p["n"] / FPS:
            return p
    return None


# ---------------------------------------------------------------- legendas palavra a palavra
def subs():
    pal = []
    for p in TL:
        if FALAS[p["j"]][0] == "gancho":
            continue
        a, b = p["a"], p["a"] + p["n"] / FPS
        for w in palavras():
            if min(b, w["e"]) - max(a, w["s"]) > 0.05:  # o Whisper adianta o começo de algumas falas
                txt = CORRIGE.get(round(w["s"], 2), w["w"])
                pal.append((txt, p["t0"] + max(0.0, w["s"] - a), p["t0"] + min(b, w["e"]) - a))
    grupos, cur = [], []
    for w in pal:
        if cur and w[1] - cur[-1][2] > 0.5:
            grupos.append(cur)
            cur = []
        cur.append(w)
        if len(cur) == 3 or len(" ".join(x[0] for x in cur)) > 14 or w[0][-1] in ",.!?":
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
    return letreiro(txt.upper(), 78, AMARELO if amarela else WHITE, INK, 11, "Poppins-Black.ttf")


def legenda(img, t):
    for a, b, g in SUBS:
        if a <= t < b:
            agora = max(j for j, (_, w0) in enumerate(g) if w0 <= t or j == 0)
            ims = [palavra_img(w, j == agora) for j, (w, _) in enumerate(g)]
            gap, larg = 18, 940
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
            y = 1470 - (len(linhas) - 1) * 100
            for ln in linhas:
                lw = sum(x.width - 22 for x in ln) + gap * (len(ln) - 1)
                x = 540 - lw / 2
                for im in ln:
                    cola(img, im, x + (im.width - 22) / 2, y, 0, sc)
                    x += im.width - 22 + gap
                y += 100
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
def cartao(nome, w):
    return foto(nome, w, borda=10, raio=22, sombra_a=0.5)


def info_jogo(img, t, j):
    """Sobre a cena da mesa: 'PRA QUEM GOSTA DE …', nome e jogadores/tempo (no alto, onde a mesa não tem nada)."""
    jogo = JOGOS[FALAS[j][3]]
    t0 = corte_cena(j)
    u = out_back(seg(t, t0, t0 + 0.35))
    cola(img, pilula("PRA QUEM GOSTA DE " + jogo[3], 44, PETROLEO), W / 2, 250, rot=-2, sc=u)
    cola(img, texto(jogo[1], "lilita", 104, WHITE, INK, 9, 8, INK), W / 2, 380, sc=out_back(seg(t, t0 + 0.1, t0 + 0.45)))
    cola(img, texto(jogo[2], "figtree", 46, WHITE, INK, 4, 4, INK), W / 2, 480, alpha=ease(seg(t, t0 + 0.3, t0 + 0.6)))


def capa_canto(img, t, j):
    jogo = FALAS[j][3]
    tn = bruto_para_saida(JOGOS[jogo][5])
    if tn is None or t < tn:
        return
    w = 300 if JOGOS[jogo][4] else 430  # sem cena (Sushi Go): a foto fica grande
    x, y = (W - 200, 1180) if JOGOS[jogo][4] else (W - 260, 1150)
    cola(img, cartao(JOGOS[jogo][0], w), x, y, rot=4 if JOGOS[jogo][4] else -3, sc=out_back(seg(t, tn, tn + 0.35)))


@lru_cache(None)
def gancho_img():
    return texto("O QUE VOCÊ GOSTA\nDE FAZER?", "lilita", 104, WHITE, INK, 9, 8, INK, entre=1.05)


def overlay(t):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if t >= M["fim"]:
        tela_final(img, t - M["fim"])
        return img
    img.alpha_composite(logo_card(150), (W - 186, 46))
    p = plano_em(t)
    if p is None:
        return img
    j = p["j"]
    tipo = FALAS[j][0]
    if tipo == "gancho":
        cola(img, gancho_img(), W / 2, 1300, rot=-2, sc=out_back(seg(t, 0.0, 0.4)))
        cola(img, pilula("EU TE INDICO UM JOGO", 50, PETROLEO), W / 2, 1490, rot=2, sc=out_back(seg(t, 1.2, 1.5)))
        return img
    if tipo == "jogo":
        jogo = JOGOS[FALAS[j][3]]
        if jogo[4] and t >= corte_cena(j):
            info_jogo(img, t, j)
        else:
            capa_canto(img, t, j)
    if tipo == "comenta":
        cola(img, pilula("COMENTA AQUI!", 64, (219, 39, 119)), W / 2, 1180, rot=-3, sc=out_back(seg(t, M[f"f{j}"] + 1.2,
                                                                                                  M[f"f{j}"] + 1.5)))
    legenda(img, t)
    return img


def tela_final(img, lt):
    cola(img, logo_card(430), W / 2, 330, sc=out_back(seg(lt, 0.0, 0.4)))
    for i, k in enumerate(JOGOS):
        x, y = 205 + (i % 3) * 335, 720 + (i // 3) * 345
        cola(img, foto(JOGOS[k][0], 300, borda=8, raio=18, sombra_a=0.45), x, y,
             sc=out_back(seg(lt, 0.1 + 0.05 * i, 0.45 + 0.05 * i)))
    v = ease(seg(lt, 0.5, 0.9))
    for j, (txt, f, s, cor) in enumerate([("TODOS NA SUA VEZ", "lilita", 82, AMARELO),
                                           ("RESERVE ONLINE · RETIRE EM MAUÁ\nOU RECEBA EM CASA", "figtree", 44, WHITE),
                                           ("LINK NA BIO · @SUAVEZ_BG", "lilita", 58, WHITE)]):
        cola(img, texto(txt, f, s, cor, INK, 6 if f == "lilita" else 0, 5 if f == "lilita" else 3, INK, entre=1.2),
             W / 2, 1290 + j * 140, alpha=v)


# ---------------------------------------------------------------- vídeo
def ler(path, a, n):
    vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},{GRADE}"
    p = subprocess.Popen([ffmpeg(), "-loglevel", "error", "-ss", f"{a:.3f}", "-i", path, "-frames:v", str(n), "-vf", vf,
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
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


def escala(fr, s, cy=0.2):
    if s <= 1.001:
        return fr
    import cv2
    w, h = W / s, H / s
    x0 = (W - w) / 2
    y0 = min(max(0.0, cy * H - h * min(cy * s, 0.4)), H - h)
    M_ = np.float32([[s, 0, -x0 * s], [0, s, -y0 * s]])
    return cv2.warpAffine(fr, M_, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


def quadros():
    ultimo = None
    cena_usada = {}
    for p in TL:
        j = p["j"]
        tipo, _a, _b, jogo = FALAS[j]
        cena = JOGOS[jogo][4] if tipo == "jogo" else None
        tc = corte_cena(j) if cena else None
        rosto = list(ler(FALA, p["a"], p["n"]))
        for k in range(p["n"]):
            t = p["t0"] + k / FPS
            if cena and t >= tc:
                if j not in cena_usada:
                    n_resto = round((M[f"f{j}_fim"] - tc) * FPS) + 2
                    cena_usada[j] = list(ler(os.path.join(BR, f"20261017_{cena[0]}.mp4"), cena[1], n_resto))
                idx = min(len(cena_usada[j]) - 1, round((t - tc) * FPS))
                fr = cena_usada[j][idx]
            else:
                fr = escala(rosto[k], 1.06 if p["punch"] else 1.0)
            ultimo = fr
            yield fr
        if cena and p["t0"] + p["n"] / FPS >= M[f"f{j}_fim"] - 1e-6:
            cena_usada.pop(j, None)
    fundo = Image.fromarray(ultimo).filter(ImageFilter.GaussianBlur(22))
    fundo = np.asarray(Image.blend(fundo, Image.new("RGB", (W, H), (12, 40, 52)), 0.62))
    for _ in range(round((DUR - M["fim"]) * FPS) + 1):
        yield fundo


# ---------------------------------------------------------------- áudio
def ler_audio(a, d):
    r = subprocess.run([ffmpeg(), "-loglevel", "error", "-ss", f"{a:.3f}", "-t", f"{d:.4f}", "-i", FALA, "-vn", "-ac", "1",
                        "-ar", "44100", "-af", VOZ, "-f", "s16le", "-"], capture_output=True)
    x = np.frombuffer(r.stdout, np.int16).astype(np.float64) / 32768
    n = int(round(d * 44100))
    return np.pad(x, (0, max(0, n - len(x))))[:n]


def audio(path):
    sr = 44100
    pecas = [(p, ler_audio(p["a"], p["n"] / FPS)) for p in TL]
    tudo = np.concatenate([x for _, x in pecas])
    q = int(0.03 * sr)
    e = np.sqrt(np.convolve(tudo ** 2, np.ones(q) / q, "same"))
    ganho = 10 ** (-20 / 20) / (np.sqrt((tudo[e > e.max() * 0.12] ** 2).mean()) + 1e-9)  # ganho FIXO
    voz = np.zeros(int(DUR * sr) + sr)
    for p, x in pecas:
        x = x * ganho
        f = int(0.015 * sr)
        x[:f] *= np.linspace(0, 1, f)
        x[-f:] *= np.linspace(1, 0, f)
        i = int(round(p["t0"] * sr))
        voz[i:i + len(x)] += x
    cues = [(0.0, "pop", 0.4)]
    for j, (tipo, _a, _b, jogo) in enumerate(FALAS):
        if tipo == "jogo":
            tn = bruto_para_saida(JOGOS[jogo][5])
            cues.append((tn, "pop", 0.35))
            if JOGOS[jogo][4]:
                cues.append((corte_cena(j) - 0.05, "whoosh", 0.4))
        if tipo == "comenta":
            cues.append((M[f"f{j}"] + 1.2, "boing", 0.4))
    cues += [(M["fim"], "whoosh", 0.4), (M["fim"] + 0.5, "ding", 0.5)]
    vp = os.path.join(OUT, "indica_voz.wav")
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
            print(f"{p['t0']:6.2f} {p['n'] / FPS:5.2f} fala{p['j']} {p['a']:.2f}")
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
        folha([ims[k] for k in sorted(ims)], os.path.join(OUT, "frames_indica.jpg"))
        return
    wav = os.path.join(OUT, "indica.wav")
    audio(wav)
    render(os.path.join(OUT, "indica.mp4"), wav)


if __name__ == "__main__":
    main()
