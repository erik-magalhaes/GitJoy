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

# Elenco: só duas vozes, na velocidade e no tom naturais (acelerar ou mudar o tom deixa com cara de robô).
MULHER = ("pt-BR-ThalitaMultilingualNeural", "+0%", "+0Hz")
HOMEM = ("pt-BR-AntonioNeural", "+0%", "+0Hz")
ELENCO = {
    "narrador": HOMEM, "camila": MULHER, "neide": MULHER, "rafael": HOMEM, "bia": MULHER,
    "rosana": MULHER, "diego": HOMEM, "lucas": HOMEM, "jessica": MULHER, "celia": MULHER, "consultor": HOMEM,
}

# Palavras que a voz pronuncia errado: a tela mostra a grafia certa, a voz lê a outra.
PRONUNCIA = {
    r"\blouça\b": "lôssa",
    r"\bLouça\b": "Lôssa",
    r"\bPIX\b": "píquis",
    r"\benquete\b": "enquête",
}

EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿⬀-⯿️‍]")


def limpa(txt):
    """Texto que a voz lê: sem emoji, sem 'kkkk' repetido demais."""
    t = EMOJI.sub("", txt).replace("@", "")   # menção (@Fulano) a voz lê só o nome
    t = re.sub(r"\b[kK]{3,}\b", "", t)   # risada escrita a voz lê "ká-ká-ká": não lê
    # dinheiro: "R$ 2.300" -> "dois mil e trezentos reais"
    from num2words import num2words
    t = re.sub(r"R\$\s?([\d.]+)(?:,(\d\d))?",
               lambda m: num2words(int(m.group(1).replace(".", "")), lang="pt_BR") + " reais", t)
    # palavra em CAIXA ALTA (grito no zap) a voz às vezes soletra: lê em minúsculas
    siglas = {"CPF", "PIX", "MED", "DJ", "BO"}
    t = re.sub(r"\b[A-ZÀ-Ý]{2,}\b", lambda m: m.group(0) if m.group(0) in siglas else m.group(0).lower(), t)
    for a, b in PRONUNCIA.items():
        t = re.sub(a, b, t)
    return re.sub(r"\s+", " ", t).strip()


# Vozes multilíngues adivinham o idioma pela frase; em frase curta erram (leem "Neide" como "Night").
# Então a fala é gerada com uma frase em português antes, que depois é cortada pelo tempo das palavras.
PREFIXO = "Então, a mensagem que chegou diz assim:"


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
    pre = (PREFIXO + "|v2") if "Multilingual" in voz else ""
    h = hashlib.md5(f"{voz}|{rate}|{pitch}|{pre}|{texto}".encode()).hexdigest()[:16]
    wav, js = os.path.join(CACHE, h + ".f32"), os.path.join(CACHE, h + ".json")
    if not os.path.exists(js):
        mp3 = os.path.join(CACHE, h + ".mp3")
        multi = "Multilingual" in voz
        palavras = _gera(voz, rate, pitch, (PREFIXO + " " + texto) if multi else texto, mp3)
        pcm = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", mp3, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                             capture_output=True, check=True).stdout
        a = np.frombuffer(pcm, np.float32)
        if multi:
            n_pre = len(PREFIXO.split())
            fim_pre = palavras[n_pre - 1][1]
            ini_txt = palavras[n_pre][0] if len(palavras) > n_pre else fim_pre
            # corta logo depois do prefixo (o tempo da palavra seguinte vem um pouco atrasado e comia a consoante inicial)
            corte = fim_pre + 0.25 * (ini_txt - fim_pre) if ini_txt - fim_pre > 0.05 else max(fim_pre, ini_txt - 0.08)
            a = a[int(corte * SR):]
            palavras = [(s - corte, e - corte, w) for s, e, w in palavras[n_pre:]]
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
