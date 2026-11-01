"""Base dos vídeos curtos em LOOP (1/nov/2026): render, som em loop (imagem E som emendam) e entrega a −15,5 LUFS.
Trilha: a "brincalhona" do bichos-reels (marimba em loop perfeito)."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "comum"))
sys.path.insert(0, os.path.join(REPO, "listas-reels"))
sys.path.insert(0, os.path.join(REPO, "bichos-reels"))
from motor import FPS, encode, ffmpeg  # noqa: E402
import som  # noqa: E402
from base import final_loudness  # noqa: E402
import bichos  # noqa: E402,F401  (registra a trilha "brincalhona" e o "tique")

OUT = os.path.join(ROOT, "out")


# efeitos usados (já existem em som.FX): pop, whoosh, flip, tick, ding


def entrega(nome, dur, render_frame, cues):
    os.makedirs(OUT, exist_ok=True)
    n = int(round(dur * FPS))
    base = None
    for versao, mus in (("com_trilha", "brincalhona"), ("para_musica", None)):
        wav = os.path.join(OUT, f"{nome}_{versao}.wav")
        som.build(wav, dur + 1e-9, cues, musica=mus, fx_ganho=0.5, musica_ganho=0.28)
        mp4 = os.path.join(OUT, f"{nome}_{versao}.mp4")
        if base is None:
            encode(mp4, render_frame, list(range(n)), wav)
            base = mp4
        else:
            subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", base, "-i", wav, "-map", "0:v", "-map", "1:a",
                            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", mp4], check=True)
        final_loudness(mp4, mp4.replace(".mp4", "_final.mp4"))
