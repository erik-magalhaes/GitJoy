"""Gera as 8 falas com uma voz: gerar_voz2.py VOZ pasta rate pitch  (corta o silêncio -> c_NN.wav)"""
import subprocess, sys, os
from falas import FALAS, FONETICA
voz, pasta, rate, pitch = sys.argv[1:5]
os.makedirs(pasta, exist_ok=True)
for i, f in enumerate(FALAS, 1):
    t = f
    for a, b in FONETICA.items():
        t = t.replace(a, b)
    mp3 = f"{pasta}/fala_{i:02d}.mp3"
    for tent in range(3):
        r = subprocess.run([sys.executable, "../hobby-reels/tts.py", voz, t, mp3, rate, pitch])
        if r.returncode == 0 and os.path.getsize(mp3) > 1000:
            break
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp3, "-af",
                    "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse",
                    "-ar", "44100", "-ac", "1", f"{pasta}/c_{i:02d}.wav"], check=True)
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{pasta}/c_{i:02d}.wav"], capture_output=True, text=True).stdout.strip()
    print(i, d)
