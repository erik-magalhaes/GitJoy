"""Base dos 3 Reels "chama a Sua Vez pro seu evento de fim de ano" (5/nov/2026, pedido dele: "seja criativo, não use a
mesma coisa de sempre"; ele pediu os TRÊS e liberou narração por voz de IA "se precisar").

  previsao.py  — paródia de previsão do tempo da confraternização (narrada por voz de IA, tom de apresentador)
  grilos.py    — o silêncio da festa (CRI CRI) que explode nas cenas reais de jogo (sem narração)
  lista.py     — checklist da festa riscada à mão, último item resolvido com o carimbo da Sua Vez (sem narração)

Cenas de jogo = brutos REAIS deles (kit.CLIPES do becas-reels). Fatos de eventos: levam os jogos e ficam o evento TODO
ensinando; ABC Paulista e São Paulo capital; orçamento no WhatsApp (11) 97793-3910. Ainda NÃO fizeram evento: nada de
"já atendemos" nem foto de evento.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "becas-reels"))
import kit  # noqa: E402
from kit import W, H, FPS, E, ffmpeg, encode, folha, final_loudness  # noqa: E402,F401

OUT = os.path.join(ROOT, "out")
WHATS = "(11) 97793-3910"
F = os.path.join(REPO, "comum", "fontes")


def clip(nome, t0, d, u, vel=1.0):
    """Quadro u (s) de um trecho de cena real (o cache fica no becas-reels/out/_cache)."""
    return kit.quadro_clip(nome, t0, d, vel, u)


def prepara(trechos):
    kit.prepara([(n, t0, d, 1.0) for n, t0, d in trechos])


def entrega(nome, dur, render, wav_com, wav_sem):
    os.makedirs(OUT, exist_ok=True)
    n = int(round(dur * FPS))
    base = os.path.join(OUT, f"{nome}_com_som.mp4")
    encode(base, render, list(range(n)), wav_com)
    sem = os.path.join(OUT, f"{nome}_para_musica.mp4")
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", base, "-i", wav_sem, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", sem], check=True)
    for arq in (base, sem):
        final_loudness(arq, arq.replace(".mp4", "_final.mp4"))


def chat(arq, kbps=4200):
    """Cópia em 2 passadas para caber no chat (< 30 MB)."""
    out = arq.replace("_final.mp4", "_chat.mp4")
    log = os.path.join(OUT, "ffpass")
    for p in (1, 2):
        cmd = [ffmpeg(), "-y", "-loglevel", "error", "-i", arq, "-c:v", "libx264", "-b:v", f"{kbps}k", "-preset", "slow",
               "-pass", str(p), "-passlogfile", log]
        cmd += (["-an", "-f", "null", "/dev/null"] if p == 1 else ["-c:a", "copy", "-movflags", "+faststart", out])
        subprocess.run(cmd, check=True)
    return out
