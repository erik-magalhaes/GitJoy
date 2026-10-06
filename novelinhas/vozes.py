"""Vozes neurais (edge-tts) com cache em out/cache: devolve o áudio (float32, 44,1 kHz) e o tempo de cada palavra.

O proxy do ambiente usa um certificado próprio, por isso o certifi aponta para /root/.ccr/ca-bundle.crt.
"""
import asyncio
import hashlib
import json
import os
import re
import subprocess

import numpy as np

SR = 44100
AQUI = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(AQUI, "out", "cache")
CA = "/root/.ccr/ca-bundle.crt"

# Elenco: voz, velocidade e tom de cada personagem.
ELENCO = {
    "narrador": ("pt-BR-AntonioNeural", "+12%", "-12Hz"),
    "camila": ("pt-BR-ThalitaMultilingualNeural", "+22%", "+0Hz"),
    "neide": ("pt-BR-FranciscaNeural", "+12%", "-10Hz"),
    "rafael": ("pt-BR-AntonioNeural", "+20%", "+4Hz"),
    "bia": ("pt-BR-FranciscaNeural", "+26%", "+14Hz"),
    "rosana": ("pt-BR-FranciscaNeural", "+8%", "-22Hz"),
    "diego": ("pt-BR-AntonioNeural", "+24%", "+16Hz"),
    "lucas": ("pt-BR-AntonioNeural", "+20%", "+10Hz"),
    "jessica": ("pt-BR-ThalitaMultilingualNeural", "+14%", "+12Hz"),
}

EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿⬀-⯿️‍]")


def limpa(txt):
    """Texto que a voz lê: sem emoji, sem 'kkkk' repetido demais."""
    t = EMOJI.sub("", txt)
    t = re.sub(r"\b[kK]{4,}\b", "kkkk", t)
    return re.sub(r"\s+", " ", t).strip()


def _gera(voz, rate, pitch, texto, mp3):
    import certifi
    certifi.where = lambda: CA
    import edge_tts

    async def run():
        com = edge_tts.Communicate(texto, voz, rate=rate, pitch=pitch, boundary="WordBoundary")
        palavras = []
        with open(mp3, "wb") as f:
            async for ch in com.stream():
                if ch["type"] == "audio":
                    f.write(ch["data"])
                elif ch["type"] == "WordBoundary":
                    palavras.append((ch["offset"] / 1e7, (ch["offset"] + ch["duration"]) / 1e7, ch["text"]))
        return palavras

    for tentativa in range(4):
        try:
            return asyncio.run(run())
        except Exception:
            if tentativa == 3:
                raise
            import time
            time.sleep(2 ** tentativa)


def fala(quem, texto):
    """-> (audio float32 mono a 44,1 kHz, [(ini, fim, palavra), ...])"""
    voz, rate, pitch = ELENCO[quem]
    texto = limpa(texto)
    os.makedirs(CACHE, exist_ok=True)
    h = hashlib.md5(f"{voz}|{rate}|{pitch}|{texto}".encode()).hexdigest()[:16]
    wav, js = os.path.join(CACHE, h + ".f32"), os.path.join(CACHE, h + ".json")
    if not os.path.exists(js):
        mp3 = os.path.join(CACHE, h + ".mp3")
        palavras = _gera(voz, rate, pitch, texto, mp3)
        pcm = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", mp3, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                             capture_output=True, check=True).stdout
        a = np.frombuffer(pcm, np.float32)
        # corta o silêncio do começo e do fim (o TTS deixa ~100 ms)
        env = np.abs(a) > 0.01
        ini = max(0, int(np.argmax(env)) - int(0.02 * SR)) if env.any() else 0
        fim = min(len(a), len(a) - int(np.argmax(env[::-1])) + int(0.06 * SR)) if env.any() else len(a)
        a = a[ini:fim]
        desl = ini / SR
        palavras = [(max(0, s - desl), max(0, e - desl), w) for s, e, w in palavras]
        a.astype(np.float32).tofile(wav)
        json.dump(palavras, open(js, "w"), ensure_ascii=False)
        os.remove(mp3)
    return np.fromfile(wav, np.float32), [tuple(p) for p in json.load(open(js))]


if __name__ == "__main__":
    import sys
    a, p = fala(sys.argv[1], sys.argv[2])
    print(len(a) / SR, p)
