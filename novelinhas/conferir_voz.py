"""Confere a pronúncia: transcreve cada fala com o Whisper e lista as que não batem com o texto.

python3 conferir_voz.py sogra 1 2 3 4 5
"""
import difflib
import re
import sys
import unicodedata

from faster_whisper import WhisperModel
from scipy.signal import resample_poly

import vozes

falas = []
_orig = vozes.fala


def _espia(quem, texto):
    falas.append((quem, texto))
    return _orig(quem, texto)


vozes.fala = _espia
import novela  # noqa: E402  (importa depois do espião)


def norm(t):
    t = unicodedata.normalize("NFKD", vozes.limpa(t).lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]", " ", t).split()


serie = sys.argv[1]
for n in sys.argv[2:]:
    novela.Ep(serie, int(n))
w = WhisperModel("small", device="cpu", compute_type="int8")
vistos = set()
ruins = 0
for quem, texto in falas:
    if (quem, texto) in vistos:
        continue
    vistos.add((quem, texto))
    a, _ = _orig(quem, texto)
    a16 = resample_poly(a, 160, 441).astype("float32")
    a16 = __import__("numpy").concatenate([__import__("numpy").zeros(8000, "float32"), a16])  # sem pausa o Whisper engole a 1ª palavra
    segs, _ = w.transcribe(a16, language="pt", beam_size=5)
    ouvido = " ".join(s.text for s in segs)
    esp, ouv = norm(texto), norm(ouvido)
    r = difflib.SequenceMatcher(None, esp, ouv).ratio()
    if r < 0.8:
        ruins += 1
        print(f"[{r:.2f}] {quem}: {texto}\n        ouvido: {ouvido.strip()}")
print(f"{len(vistos)} falas conferidas, {ruins} suspeitas")
