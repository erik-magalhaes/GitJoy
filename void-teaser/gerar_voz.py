import subprocess, sys
from falas import FALAS, FONETICA
for i, f in enumerate(FALAS, 1):
    t = f
    for a, b in FONETICA.items(): t = t.replace(a, b)
    t = t.replace(". ", "... ")
    subprocess.run([sys.executable, "../hobby-reels/tts.py", "pt-BR-AntonioNeural", t, f"voz/fala_{i:02d}.mp3", "-12%", "-14Hz"], check=True)
