#!/usr/bin/env python3
"""Corta silêncios das falas tratadas (narracao/tmp_NN.wav -> frase_NN.wav, 44.1 kHz) e transcreve palavras."""
import json
import os
import wave

import numpy as np
from scipy.signal import resample_poly

NAR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "narracao")


def trim(a, sr, thr_db=-38, pad=0.08):
    win = int(0.02 * sr)
    e = np.sqrt(np.convolve(a ** 2, np.ones(win) / win, "same"))
    on = np.where(20 * np.log10(e + 1e-9) > thr_db)[0]
    if not len(on):
        return a
    i0, i1 = max(0, on[0] - int(pad * sr)), min(len(a), on[-1] + int(pad * 2 * sr))
    a = a[i0:i1].copy()
    f = int(0.01 * sr)
    a[:f] *= np.linspace(0, 1, f)
    a[-f * 3:] *= np.linspace(1, 0, f * 3)
    return a


def encurta_pausas(a, sr, thr_db=-40, maxp=0.45):
    """Pausas internas longas  viram no máximo maxp segundos."""
    win = int(0.02 * sr)
    e = np.sqrt(np.convolve(a ** 2, np.ones(win) / win, "same"))
    quiet = 20 * np.log10(e + 1e-9) < thr_db
    out, i, n = [], 0, len(a)
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]:
                j += 1
            if j - i > maxp * sr and i > 0 and j < n:
                keep = int(maxp * sr / 2)
                out.append(a[i:i + keep])
                out.append(a[j - keep:j])
            else:
                out.append(a[i:j])
            i = j
        else:
            j = i
            while j < n and not quiet[j]:
                j += 1
            out.append(a[i:j])
            i = j
    return np.concatenate(out)


def main():
    from faster_whisper import WhisperModel
    model = WhisperModel("small", compute_type="int8")
    palavras = {}
    for n in range(1, 10):
        with wave.open(os.path.join(NAR, f"tmp_{n:02d}.wav")) as w:
            a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
        a = encurta_pausas(trim(resample_poly(a, 147, 160), 44100), 44100, maxp=0.3)
        out = os.path.join(NAR, f"frase_{n:02d}.wav")
        with wave.open(out, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(44100)
            w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())
        segs, _ = model.transcribe(out, language="pt", word_timestamps=True)
        ws = [[round(x.start, 2), round(x.end, 2), x.word.strip()] for s in segs for x in s.words]
        palavras[f"{n:02d}"] = ws
        print(f"{n:02d} {len(a)/44100:5.2f}s:", " ".join(x[2] for x in ws))
    json.dump(palavras, open(os.path.join(NAR, "palavras.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
