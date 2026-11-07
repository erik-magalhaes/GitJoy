#!/usr/bin/env python3
"""Narração do "tarde comum": narracao_tarde/raw/becastarde_narracao_NN.webm → tmp_NN.wav (cadeia de voz, 44,1 kHz,
feita no ffmpeg) → frase_NN.wav (sem silêncio/respiro, pausas ≤0,3 s) + palavras.json (faster-whisper small).

    /usr/bin/python3 tratar_tarde.py
"""
import json
import os
import sys
import wave

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "taco-reels"))
import tratar_narracao as TN  # noqa: E402

NAR = os.path.join(AQUI, "narracao_tarde")


def main():
    from faster_whisper import WhisperModel
    model = WhisperModel("small", compute_type="int8")
    palavras = {}
    for n in range(1, 8):
        src = os.path.join(NAR, f"tmp_{n:02d}.wav")
        if not os.path.exists(src):
            print(f"{n:02d} FALTA")
            continue
        with wave.open(src) as w:
            a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
        sr = 44100
        a = TN.corta_respiro(TN.trim(a, sr), sr)
        b = TN.corta_resto_respiro(a, sr)
        if len(b) > len(a) - 0.3 * sr:  # o "resto de respiro" às vezes leva uma palavra curta inteira ("Um")
            a = b
        a = TN.encurta_pausas(a, sr, maxp=0.3)
        out = os.path.join(NAR, f"frase_{n:02d}.wav")
        with wave.open(out, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
            w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())
        from scipy.signal import resample_poly
        segs, _ = model.transcribe(resample_poly(a, 160, 441).astype(np.float32), language="pt", word_timestamps=True)
        ws = [[round(x.start, 2), round(x.end, 2), x.word.strip()] for s in segs for x in s.words]
        palavras[f"{n:02d}"] = ws
        print(f"{n:02d} {len(a) / sr:5.2f}s:", " ".join(x[2] for x in ws))
    json.dump(palavras, open(os.path.join(NAR, "palavras.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
