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
    """Pausas internas longas (vírgula/ponto da voz sintetizada) viram no máximo maxp segundos."""
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


def corta_respiro(a, sr, voz_db=-20, antes=0.06):
    """Nunca começar na puxada de ar: a fala começa na 1ª palavra (salto de energia acima de voz_db)."""
    win = int(0.01 * sr)
    e = 20 * np.log10(np.sqrt(np.convolve(a ** 2, np.ones(win) / win, "same")) + 1e-9)
    on = np.where(e > voz_db)[0]
    if not len(on):
        return a
    i0 = max(0, on[0] - int(antes * sr))
    if i0 < 0.2 * sr:  # nada a cortar
        return a
    a = a[i0:].copy()
    f = int(0.01 * sr)
    a[:f] *= np.linspace(0, 1, f)
    return a


def periodico(x):
    ac = np.correlate(x, x, "full")[len(x) - 1:]
    ac /= ac[0] + 1e-12
    return ac[100:600].max()


def corta_resto_respiro(a, sr, ate=0.8):
    """Resto de respiro: chiado SEM tom (não periódico) + silêncio curto (< -40 dB por 30 ms) + voz. Corta no silêncio.
    Palavra que começa com S/T não tem esse silêncio antes da vogal, então não é cortada."""
    win = int(0.01 * sr)
    e = 20 * np.log10(np.sqrt(np.convolve(a ** 2, np.ones(win) / win, "same")) + 1e-9)
    n = int(ate * sr)
    quieto = e[:n] < -40
    i = int(0.03 * sr)
    while i < n:
        if quieto[i]:
            j = i
            while j < n and quieto[j]:
                j += 1
            if j - i >= 0.03 * sr and i > 0.05 * sr:
                antes = a[:i]
                # depois do silêncio: tem tom em até 0,25 s (palavra com S/T no começo chia antes da vogal)
                tom = max((periodico(a[k:k + int(0.05 * sr)]) for k in range(j, j + int(0.25 * sr), int(0.025 * sr))
                           if k + int(0.05 * sr) <= len(a)), default=0)
                if periodico(antes[-int(0.1 * sr):]) < 0.3 and tom > 0.45:
                    a = a[max(0, j - int(0.02 * sr)):].copy()
                    f = int(0.01 * sr)
                    a[:f] *= np.linspace(0, 1, f)
                return a
            i = j
        i += 1
    return a


def main():
    from faster_whisper import WhisperModel
    model = WhisperModel("small", compute_type="int8")
    palavras = {}
    for n in range(1, 9):
        with wave.open(os.path.join(NAR, f"tmp_{n:02d}.wav")) as w:
            a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
        a = encurta_pausas(corta_resto_respiro(corta_respiro(trim(resample_poly(a, 147, 160), 44100), 44100), 44100), 44100, maxp=0.3)
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
