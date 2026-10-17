#!/usr/bin/env python3
"""Reels "ESSE OU AQUELE?" com a Jéssica (17/out/2026, gravado por eles: brutos/out17/20261017_133042.mp4, fora do git).
O Erik filma e pergunta ("Luxor ou Nekojima?"), ela responde; quem ganha FICA e enfrenta o próximo (formato "o
vencedor fica"). Por cima, no pé da tela, as FOTOS DO SITE dos dois jogos da rodada com "OU" no meio: na resposta dela
o escolhido brilha e o outro leva um X e cai; o vencedor desliza para a esquerda e o próximo desafiante entra.
Fecha com o campeão (Clank! Catacombs), "E você, ficava com qual?" e a tela final.

Whisper corrigido: "Necoagima" = Nekojima, "Wonderland Noirce" = Wonderland's War, "Espírito" = Splito (CONFERIR com
eles), "Comodados Edejejados" = Convidados Indesejados, "Survive" = Survive the Island, "Flamiecraft" = Flamecraft.
O "Clank Catacombs?" / "Clank." (38,8–40,4 s) é só ele confirmando qual Clank: saiu; a rodada seguinte decide.

    python3 esse_aquele.py --frame 1 5 30     # out/frames_esse.jpg
    python3 esse_aquele.py                    # out/esse_aquele.mp4
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
from motor import W, H, FPS, WHITE, ease, seg, lerp, out_back, logo_card, cola, folha, ffmpeg  # noqa: E402
import som  # noqa: E402
from base import texto, foto  # noqa: E402

BRUTO = os.path.join(ROOT, "brutos", "out17", "20261017_133042.mp4")
OUT = os.path.join(ROOT, "out")
INK, AMARELO, VERMELHO, ROSA = (20, 16, 30), (255, 214, 70), (220, 38, 38), (219, 39, 119)
GRADE = ("hqdn3d=2:1.5:4:4,curves=all='0/0.012 0.25/0.27 0.5/0.545 0.75/0.79 1/0.985',"
         "eq=contrast=1.02:saturation=0.98,unsharp=5:5:0.35:5:5:0.0")
VOZ = "highpass=f=80,afftdn=nr=8:nf=-48,equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1.4:g=1.5"
NOMES = {"luxor": "Luxor", "nekojima": "Nekojima", "taco_gato_cabra_queso_pizza_carpincho_promo": "Taco Gato...",
         "wonderland_s_war": "Wonderland's War", "unicorn_fever": "Unicorn Fever", "splito": "Splito",
         "take_time": "Take Time", "convidados_indesejados": "Convidados Indesejados", "clank_a_deck_building_adventure":
         "Clank!", "clank_catacombs": "Clank! Catacombs", "survive_the_island": "Survive the Island",
         "flamecraft": "Flamecraft"}
# rodadas: (início da pergunta, início da resposta, fim da resposta, esquerda, direita, vencedor) — tempos no bruto
RODADAS = [
    (5.74, 8.44, 9.20, "luxor", "nekojima", "luxor"),
    (9.34, 12.72, 13.30, "luxor", "taco_gato_cabra_queso_pizza_carpincho_promo", "luxor"),
    (13.72, 16.78, 17.26, "luxor", "wonderland_s_war", "wonderland_s_war"),
    (17.94, 20.80, 21.68, "wonderland_s_war", "unicorn_fever", "unicorn_fever"),
    (22.06, 24.92, 25.70, "unicorn_fever", "splito", "unicorn_fever"),
    (26.10, 28.36, 30.10, "unicorn_fever", "take_time", "unicorn_fever"),
    (30.24, 33.60, 35.20, "unicorn_fever", "convidados_indesejados", "convidados_indesejados"),
    (35.60, 38.04, 38.64, "convidados_indesejados", "clank_a_deck_building_adventure", "clank_a_deck_building_adventure"),
    (41.05, 43.82, 45.42, "clank_a_deck_building_adventure", "clank_catacombs", "clank_catacombs"),
    (45.96, 48.62, 49.08, "clank_catacombs", "survive_the_island", "clank_catacombs"),
    (49.52, 51.58, 52.14, "clank_catacombs", "flamecraft", "clank_catacombs"),
    (52.38, 54.20, 55.50, "clank_catacombs", "nekojima", "clank_catacombs"),  # + o "Ei!" dela
]
ANTES, DEPOIS = 0.18, 0.28
CAMPEAO, COMENTA, FIM = 2.6, 2.4, 3.6


def linha():
    tl, t = [], 0.0
    for q, a, b, esq, dir_, venc in RODADAS:
        a0, b0 = q - ANTES, b + DEPOIS
        n = round((t + b0 - a0) * FPS) - round(t * FPS)
        tl.append(dict(t0=t, n=n, src=a0, q=q, a=a, esq=esq, dir=dir_, venc=venc))
        t += n / FPS
    return tl, t


TL, T_CAMP = linha()
T_COM = T_CAMP + CAMPEAO
T_FIM = T_COM + COMENTA
DUR = T_FIM + FIM


def rodada_em(t):
    for k, r in enumerate(TL):
        if r["t0"] <= t < r["t0"] + r["n"] / FPS:
            return k, r
    return None, None


def out_t(r, t_bruto):
    return r["t0"] + t_bruto - r["src"]


# ---------------------------------------------------------------- cartões
@lru_cache(None)
def cartao(nome, w, brilho=False):
    c = foto(nome, w, borda=12, cor_borda=AMARELO if brilho else WHITE, raio=26, sombra_a=0.55)
    return c


@lru_cache(None)
def nome_img(nome):
    s = 46 if len(NOMES[nome]) < 15 else 36
    return texto(NOMES[nome], "lilita", s, WHITE, INK, 6, 4, INK)


@lru_cache(None)
def ou():
    s = texto("OU", "lilita", 74, INK)
    im = Image.new("RGBA", (130, 130), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((4, 4, 126, 126), fill=AMARELO, outline=INK, width=7)
    cola(im, s, 65, 67)
    return im


@lru_cache(None)
def xis():
    im = Image.new("RGBA", (260, 260), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for a, b in [((30, 30), (230, 230)), ((230, 30), (30, 230))]:
        d.line((a, b), fill=INK, width=46)
        d.line((a, b), fill=VERMELHO, width=30)
    return im


@lru_cache(None)
def coroa(w):
    im = Image.new("RGBA", (w, int(w * 0.62)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    h = im.height
    pts = [(0.06 * w, h * 0.95), (0.06 * w, h * 0.3), (0.3 * w, h * 0.62), (0.5 * w, h * 0.08), (0.7 * w, h * 0.62),
           (0.94 * w, h * 0.3), (0.94 * w, h * 0.95)]
    d.polygon(pts, fill=AMARELO, outline=INK, width=max(4, w // 22))
    for x in (0.06, 0.5, 0.94):
        r = w * 0.06
        d.ellipse((x * w - r, (0.3 if x != 0.5 else 0.08) * h - r, x * w + r, (0.3 if x != 0.5 else 0.08) * h + r),
                  fill=(240, 80, 90), outline=INK, width=max(3, w // 40))
    return im


XE, XD, YC, CW = 285, 795, 1420, 380


def duelo(img, t, k, r):
    lt = t - r["t0"]
    ta = out_t(r, r["a"]) - r["t0"]  # resposta (tempo dentro da rodada)
    dur = r["n"] / FPS
    prev = TL[k - 1] if k else None
    # vencedor da rodada anterior vinha da direita? desliza para a esquerda
    x_esq = XE
    if prev and prev["venc"] == prev["dir"]:
        x_esq = lerp(XD, XE, ease(seg(lt, 0.0, 0.3)))
    ent = out_back(seg(lt, 0.05, 0.4)) if k else out_back(seg(lt, 0.0, 0.35))
    x_dir = lerp(W + 300, XD, min(1.0, ent))
    escolha = ease(seg(lt, ta, ta + 0.25))
    for lado, nome, x in (("esq", r["esq"], x_esq), ("dir", r["dir"], x_dir)):
        venc = nome == r["venc"]
        if lado == "esq" and not k:
            x = lerp(-300, XE, min(1.0, out_back(seg(lt, 0.0, 0.35))))
        if venc:
            sc = 1 + 0.08 * escolha
            cola(img, cartao(nome, CW, escolha > 0.5), x, YC, rot=0, sc=sc)
            cola(img, nome_img(nome), x, YC + 245)
            if escolha > 0.01:
                cola(img, coroa(150), x, YC - 225 - 12 * escolha, rot=-8, sc=escolha)
        else:
            cai = ease(seg(lt, ta + 0.25, min(dur, ta + 0.7)))
            cola(img, cartao(nome, CW), x, YC + 500 * cai, rot=10 * cai * (1 if lado == "dir" else -1),
                 alpha=1 - 0.6 * cai)
            if cai < 0.5:
                cola(img, nome_img(nome), x, YC + 245, alpha=1 - 2 * cai)
            if escolha > 0.01:
                cola(img, xis(), x, YC + 500 * cai, sc=out_back(seg(lt, ta, ta + 0.25)), alpha=1 - cai)
    if escolha < 1:
        cola(img, ou(), W / 2, YC, sc=out_back(seg(lt, 0.15, 0.45)) * (1 - escolha))


@lru_cache(None)
def titulo():
    return texto("ESSE OU AQUELE?", "lilita", 96, WHITE, INK, 9, 8, INK)


@lru_cache(None)
def selo_jess():
    s = texto("VERSÃO JÉSSICA", "lilita", 44, WHITE)
    im = Image.new("RGBA", (s.width + 30, s.height + 6), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=im.height // 2, fill=ROSA,
                                          outline=INK, width=5)
    im.alpha_composite(s, (15, 3))
    return im


def overlay(t):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if t < T_CAMP:
        img.alpha_composite(logo_card(150), (W - 186, 46))
        k, r = rodada_em(t)
        if r:
            duelo(img, t, k, r)
        u = out_back(seg(t, 0.0, 0.4))
        if t < 2.6:
            cola(img, titulo(), W / 2, 1080, rot=-3, sc=u * (1 - ease(seg(t, 2.3, 2.6))))
            cola(img, selo_jess(), W / 2, 1170, rot=2, sc=u * (1 - ease(seg(t, 2.3, 2.6))))
        else:
            cola(img, selo_jess(), W / 2, 1100, sc=out_back(seg(t, 2.6, 2.9)))
    elif t < T_COM:
        lt = t - T_CAMP
        u = out_back(seg(lt, 0.0, 0.45))
        cola(img, texto("CAMPEÃO!", "lilita", 120, AMARELO, INK, 10, 9, INK), W / 2, 330, rot=-3, sc=u)
        c = out_back(seg(lt, 0.15, 0.6))
        cola(img, coroa(220), W / 2, 560, rot=-6, sc=c)
        cola(img, cartao("clank_catacombs", 620, True), W / 2, 980, sc=c)
        cola(img, texto("Clank! Catacombs", "lilita", 80, WHITE, INK, 8, 6, INK), W / 2, 1380, alpha=ease(seg(lt, 0.5, 0.8)))
        cola(img, texto("o favorito da Jéssica", "figtree", 46, WHITE, None, 0, 3, INK), W / 2, 1470,
             alpha=ease(seg(lt, 0.7, 1.0)))
    elif t < T_FIM:
        lt = t - T_COM
        u = out_back(seg(lt, 0.0, 0.4))
        cola(img, texto("E VOCÊ?\nFICAVA COM QUAL?", "lilita", 100, WHITE, INK, 9, 8, INK, entre=1.05), W / 2, 820,
             rot=-2, sc=u)
        cola(img, texto("Comenta aqui!", "lilita", 80, AMARELO, INK, 7, 6, INK), W / 2, 1120, sc=out_back(seg(lt, 0.4, 0.8)))
    else:
        lt = t - T_FIM
        cola(img, logo_card(430), W / 2, 330, sc=out_back(seg(lt, 0.0, 0.4)))
        jogos = list(NOMES)
        for i, n in enumerate(jogos):
            x, y = 165 + (i % 4) * 250, 640 + (i // 4) * 260
            cola(img, foto(n, 225, borda=7, raio=16, sombra_a=0.4), x, y, sc=out_back(seg(lt, 0.1 + 0.03 * i, 0.4 + 0.03 * i)))
        v = ease(seg(lt, 0.5, 0.9))
        for j, (txt, f, s, cor) in enumerate([("TODOS NA SUA VEZ", "lilita", 80, AMARELO),
                                               ("RESERVE ONLINE · RETIRE EM MAUÁ\nOU RECEBA EM CASA", "figtree", 44, WHITE),
                                               ("LINK NA BIO · @SUAVEZ_BG", "lilita", 58, WHITE)]):
            cola(img, texto(txt, f, s, cor, INK, 6 if f == "lilita" else 0, 5 if f == "lilita" else 3, INK, entre=1.2),
                 W / 2, 1440 + j * 140, alpha=v)
    return img


# ---------------------------------------------------------------- vídeo
def ler(a, n):
    vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},{GRADE}"
    p = subprocess.Popen([ffmpeg(), "-loglevel", "error", "-ss", f"{a:.3f}", "-i", BRUTO, "-frames:v", str(n), "-vf", vf,
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


def quadros():
    ultimo = None
    for r in TL:
        for fr in ler(r["src"], r["n"]):
            ultimo = fr
            yield fr
    fundo = Image.fromarray(ultimo).filter(ImageFilter.GaussianBlur(22))
    fundo = np.asarray(Image.blend(fundo, Image.new("RGB", (W, H), (60, 14, 40)), 0.62))
    for _ in range(round((DUR - T_CAMP) * FPS) + 1):
        yield fundo


# ---------------------------------------------------------------- áudio
def ler_audio(a, d):
    r = subprocess.run([ffmpeg(), "-loglevel", "error", "-ss", f"{a:.3f}", "-t", f"{d:.4f}", "-i", BRUTO, "-vn", "-ac",
                        "1", "-ar", "44100", "-af", VOZ, "-f", "s16le", "-"], capture_output=True)
    x = np.frombuffer(r.stdout, np.int16).astype(np.float64) / 32768
    n = int(round(d * 44100))
    return np.pad(x, (0, max(0, n - len(x))))[:n]


def rms_voz(x):
    q = int(0.03 * 44100)
    e = np.sqrt(np.convolve(x ** 2, np.ones(q) / q, "same"))
    v = e > e.max() * 0.12
    return np.sqrt((x[v] ** 2).mean()) + 1e-9


def audio(path):
    """Ganho FIXO por pessoa: a pergunta (Erik, atrás do celular) e a resposta (Jéssica) chegam com volumes diferentes."""
    sr = 44100
    pedacos = []
    for r in TL:
        d = r["n"] / FPS
        x = ler_audio(r["src"], d)
        corte = int((r["a"] - 0.12 - r["src"]) * sr)
        pedacos.append((r, x, corte))
    g_q = 10 ** (-21 / 20) / rms_voz(np.concatenate([x[:c] for _, x, c in pedacos]))
    g_a = 10 ** (-20 / 20) / rms_voz(np.concatenate([x[c:] for _, x, c in pedacos]))
    voz = np.zeros(int(DUR * sr) + sr)
    cues = [(0.0, "pop", 0.5)]
    for r, x, c in pedacos:
        ganho = np.ones(len(x)) * g_a
        f = int(0.04 * sr)
        ganho[:c] = g_q
        ganho[c:c + f] = np.linspace(g_q, g_a, len(ganho[c:c + f]))
        x = x * ganho
        e = int(0.015 * sr)
        x[:e] *= np.linspace(0, 1, e)
        x[-e:] *= np.linspace(1, 0, e)
        i = int(round(r["t0"] * sr))
        voz[i:i + len(x)] += x
        cues += [(r["t0"] + 0.05, "whoosh", 0.3), (out_t(r, r["a"]), "ding", 0.45), (out_t(r, r["a"]) + 0.3, "boing", 0.25)]
    cues += [(T_CAMP, "reveal", 0.6), (T_CAMP + 0.2, "plateia", 0.4), (T_COM, "whoosh", 0.4), (T_FIM, "chime", 0.5)]
    vp = os.path.join(OUT, "esse_voz.wav")
    with wave.open(vp, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.clip(voz, -1, 1) * 32767).astype(np.int16).tobytes())
    som.build(path, DUR, cues, musica="gameshow", voz=[(vp, 0.0)], fx_ganho=0.35, duck=0.55, musica_ganho=0.24,
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
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    print(f"duração {DUR:.1f} s (campeão em {T_CAMP:.1f} s)")
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
        folha([ims[k] for k in sorted(ims)], os.path.join(OUT, "frames_esse.jpg"))
        return
    wav = os.path.join(OUT, "esse_aquele.wav")
    audio(wav)
    render(os.path.join(OUT, "esse_aquele.mp4"), wav)


if __name__ == "__main__":
    main()
