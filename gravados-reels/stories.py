#!/usr/bin/env python3
"""Stories gravados por ele em 14/out/2026 (brutos/stories/, fora do git): edição BÁSICA, como ele pediu
("só uma editada básica e colocar a legenda"): corta o silêncio do começo, gira e enquadra em 1080x1920, cor bem leve
(a mesma GRADE_ROSTO dos outros vídeos gravados), voz só limpa e nivelada, legenda palavra a palavra (1–3 palavras,
a falada em amarelo) e loudness −15,5 LUFS. Sem trilha, sem logo e sem tela final (é story).

    1  20261014_095354 — separando os jogos do dia (Wandering Towers), cupom JOGAABC5, 3/5/7 jogos = 7/10/15 dias
    2  20261014_095443 — a "nova novidade": planos de assinatura no site (ele põe o adesivo de link no Instagram)

    python3 stories.py --frame 1 5 12   # quadros de teste do story 1 em out/frames.jpg
    python3 stories.py                  # out/story{1,2}_legendado.mp4 (+ _sem_legenda)
"""
import argparse
import json
import os
import subprocess
import sys
from functools import lru_cache

from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "..", "comum"))
from motor import W, H, WHITE, ease, cola, letreiro, folha  # noqa: E402

BR = os.path.join(ROOT, "brutos", "stories")
OUT = os.path.join(ROOT, "out")
FPS = 30
INK = (20, 16, 30)
AMARELO = (255, 214, 70)
GRADE = ("hqdn3d=2.5:2:5:5,curves=all='0/0.012 0.25/0.245 0.5/0.52 0.75/0.775 1/0.98',"
         "eq=contrast=1.02:saturation=0.96:gamma=1.04,unsharp=5:5:0.45:5:5:0.0")
# microfone de lapela Kaidi (aparece no peito): a mesma EQ moderada que deu certo no criancas2 (sem compressor)
VOZ = ("highpass=f=90,equalizer=f=140:t=q:w=1:g=-2,equalizer=f=320:t=q:w=1.3:g=-4,"
       "equalizer=f=3200:t=q:w=1.4:g=2,highshelf=f=6000:g=2")
# (arquivo, início, fim, correções do Whisper por índice de palavra: texto novo ou None para juntar com a anterior)
STORIES = [
    ("20261014_095354", 0.45, 37.2, {16: "Wandering", 21: "pra", 23: "locação", 28: "site", 34: "JOGAABC5,", 35: None,
                                     37: "5%", 38: None, 39: "de", 42: "locação,", 88: "pra", 100: "locação",
                                     101: "pra,", 114: "story."}),
    ("20261014_095443", 0.45, 37.15, {}),
]


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def subs(k):
    """Grupos de 1–3 palavras com os tempos reais (já no tempo do vídeo cortado)."""
    nome, ini, fim, cor = STORIES[k]
    ws = json.load(open(os.path.join(BR, nome + "_palavras.json"), encoding="utf-8"))
    pal = []
    for i, w in enumerate(ws):
        txt = cor.get(i, w["w"])
        if txt is None:
            continue
        pal.append((txt, max(0.0, w["a"] - ini), w["b"] - ini))
    grupos, cur = [], []
    for w in pal:
        cur.append(w)
        if len(cur) == 3 or len(" ".join(x[0] for x in cur)) > 14 or w[0][-1] in ",.!?":
            grupos.append(cur)
            cur = []
    if cur:
        grupos.append(cur)
    out = []
    for j, g in enumerate(grupos):
        prox = grupos[j + 1][0][1] if j + 1 < len(grupos) else g[-1][2] + 0.4
        out.append((g[0][1], min(prox, g[-1][2] + 0.6), g))
    return out


@lru_cache(None)
def palavra_img(txt, amarela):
    return letreiro(txt.upper(), 84, AMARELO if amarela else WHITE, INK, 11, "Poppins-Black.ttf")


def legenda(img, t, sb):
    for a, b, g in sb:
        if a <= t < b:
            agora = max(j for j, (_, w0, _) in enumerate(g) if w0 <= t or j == 0)
            ims = [palavra_img(w, j == agora) for j, (w, _, _) in enumerate(g)]
            gap, larg = 20, 940
            ims = [im if im.width - 22 <= larg else im.resize((larg + 22, int(im.height * (larg + 22) / im.width)),
                                                               Image.LANCZOS) for im in ims]
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
            y = 1400 - (len(linhas) - 1) * 52
            for ln in linhas:
                lw = sum(x.width - 22 for x in ln) + gap * (len(ln) - 1)
                x = W / 2 - lw / 2
                for im in ln:
                    cola(img, im, x + (im.width - 22) / 2, y, 0, sc)
                    x += im.width - 22 + gap
                y += 105
            return


def base(k):
    """Corte + rotação automática + 1080x1920 + cor leve, sem áudio."""
    nome, ini, fim, _ = STORIES[k]
    p = os.path.join(OUT, f"story{k + 1}_base.mp4")
    vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},{GRADE}"
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-ss", f"{ini}", "-to", f"{fim}", "-i",
                    os.path.join(BR, nome + ".mp4"), "-an", "-vf", vf, "-c:v", "libx264", "-crf", "16", "-preset", "fast",
                    "-pix_fmt", "yuv420p", p], check=True)
    return p


def audio(k, alvo=-15.5, tp=-2.0):
    """Voz limpa + ganho FIXO (loudnorm linear em 2 passadas)."""
    nome, ini, fim, _ = STORIES[k]
    src = os.path.join(BR, nome + ".mp4")
    af = f"{VOZ},afade=t=in:d=0.04,afade=t=out:st={fim - ini - 0.25:.2f}:d=0.25"
    r = subprocess.run([ffmpeg(), "-hide_banner", "-ss", f"{ini}", "-to", f"{fim}", "-i", src, "-vn", "-af",
                        af + f",loudnorm=I={alvo}:TP={tp}:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    m = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
    wav = os.path.join(OUT, f"story{k + 1}.wav")
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-ss", f"{ini}", "-to", f"{fim}", "-i", src, "-vn", "-ac", "2",
                    "-ar", "44100", "-af",
                    af + f",loudnorm=I={alvo}:TP={tp}:LRA=11:linear=true:measured_I={m['input_i']}:"
                    f"measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
                    f"offset={m['target_offset']}", wav], check=True)
    return wav


def compor(base_mp4, wav, saida, sb):
    rd = subprocess.Popen([ffmpeg(), "-loglevel", "error", "-i", base_mp4, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                          stdout=subprocess.PIPE)
    wr = subprocess.Popen([ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-framerate", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-crf", "20", "-preset",
                           "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags",
                           "+faststart", saida], stdin=subprocess.PIPE)
    n = 0
    while True:
        buf = rd.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        fr = Image.frombytes("RGB", (W, H), buf)
        if sb:
            fr = fr.convert("RGBA")
            legenda(fr, n / FPS, sb)
            fr = fr.convert("RGB")
        wr.stdin.write(fr.tobytes())
        n += 1
    wr.stdin.close()
    wr.wait()
    print("ok:", saida, n, "quadros", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    ap.add_argument("--story", type=int, default=1)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.frame:
        k = a.story - 1
        nome, ini, _, _ = STORIES[k]
        sb = subs(k)
        ims = []
        for t in a.frame:
            p = os.path.join(OUT, "_q.png")
            subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-ss", f"{ini + t}", "-i", os.path.join(BR, nome + ".mp4"),
                            "-frames:v", "1", "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                            f"{GRADE}", p], check=True)
            im = Image.open(p).convert("RGBA")
            legenda(im, t, sb)
            ims.append(im.convert("RGB"))
        folha(ims, os.path.join(OUT, "frames.jpg"))
        return
    for k in range(len(STORIES)):
        b = base(k)
        wav = audio(k)
        compor(b, wav, os.path.join(OUT, f"story{k + 1}_legendado.mp4"), subs(k))
        compor(b, wav, os.path.join(OUT, f"story{k + 1}_sem_legenda.mp4"), None)


if __name__ == "__main__":
    main()
