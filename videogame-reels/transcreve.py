#!/usr/bin/env python3
"""Transcreve os brutos (faster-whisper small, pt, tempos por palavra) → out/transcricao/<nome>.json + .txt.
O áudio é extraído a 16 kHz e passado como array (o av.open de caminho falha nesta máquina)."""
import json, os, subprocess, sys
import numpy as np
import imageio_ffmpeg
from faster_whisper import WhisperModel

ROOT = os.path.dirname(os.path.abspath(__file__))
FF = imageio_ffmpeg.get_ffmpeg_exe()
OUT = os.path.join(ROOT, "out", "transcricao")
os.makedirs(OUT, exist_ok=True)
modelo = WhisperModel(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].endswith(".mp4") else "small",
                      device="cpu", compute_type="int8")
arqs = [a for a in sys.argv[1:] if a.endswith(".mp4")] or sorted(
    os.path.join(ROOT, "brutos", f) for f in os.listdir(os.path.join(ROOT, "brutos")) if f.endswith(".mp4"))
for a in arqs:
    nome = os.path.basename(a)[:-4]
    raw = subprocess.run([FF, "-v", "error", "-i", a, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True).stdout
    audio = np.frombuffer(raw, np.float32)
    segs, _ = modelo.transcribe(audio, language="pt", word_timestamps=True, vad_filter=False, beam_size=5)
    palavras, linhas = [], []
    for s in segs:
        linhas.append(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text.strip()}")
        for w in s.words:
            palavras.append({"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)})
    json.dump(palavras, open(os.path.join(OUT, nome + ".json"), "w"), ensure_ascii=False)
    open(os.path.join(OUT, nome + ".txt"), "w").write("\n".join(linhas))
    print("==", nome, f"{len(audio)/16000:.1f}s")
    print("\n".join(linhas))
