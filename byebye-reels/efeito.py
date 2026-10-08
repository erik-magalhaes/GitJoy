#!/usr/bin/env python3
"""O efeito "jogos modernos" (trend "O efeito 'Suíça'", música American Pie).

Na referência (referencia/referencia.mp4, 22 s úteis): a primeira parte mostra o "antes" (calçada esburacada) e,
quando a música volta depois do silêncio (o "tchan", em 10,16 s), corta para o "depois" (a Suíça). O texto
'O efeito "Suíça" 🇨🇭' fica fixo na tela o tempo todo. Aqui: antes = jogo antigo, depois = jogo moderno.

Os cortes são os mesmos da referência (medidos por diferença de quadros) e o áudio é o da própria referência.

    python3 efeito.py --antigo antigo.mp4 [antigo2.mp4] --moderno moderno.mp4 [moderno2.mp4 ...]
    # out/efeito_com_musica.mp4 e out/efeito_sem_musica.mp4
"""
import argparse
import os
import subprocess
import sys

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "..", "comum"))
from motor import W, H, FPS, font, emoji, logo_card, ffmpeg  # noqa: E402

REF = os.path.join(ROOT, "referencia", "referencia.mp4")
OUT = os.path.join(ROOT, "out")
TCHAN = 10.10   # corte do "antes" para o "depois" (a música volta em 10,16 s)
FIM = 22.17     # fim do conteúdo na referência (depois vem a vinheta do TikTok)
# cortes da referência: antes [0, 4.67, 10.10]; depois [10.10, 12.47, 14.40, 16.43, 22.17]
CORTES_ANTES = [0.0, 4.67, TCHAN]
CORTES_DEPOIS = [TCHAN, 12.47, 14.40, 16.43, FIM]
TEXTO = 'O efeito "jogos modernos"'


def dur(path):
    out = subprocess.run([ffmpeg(), "-i", path], capture_output=True, text=True).stderr
    h, m, s = out.split("Duration: ")[1].split(",")[0].split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def planos(clipes, cortes):
    """Distribui os planos (entre cortes) pelos clipes: um clipe por plano, repetindo trechos diferentes
    do mesmo clipe se vierem menos clipes que planos."""
    pl = []
    n = len(cortes) - 1
    usado = {c: 0.0 for c in clipes}
    for i in range(n):
        c = clipes[i % len(clipes)]
        d = cortes[i + 1] - cortes[i]
        total = dur(c)
        vezes = sum(1 for j in range(n) if clipes[j % len(clipes)] == c)
        # cada uso do clipe pega um trecho diferente, espalhado pela gravação
        passo = max(0.0, (total - d) / max(1, vezes - 1)) if vezes > 1 else 0.0
        ini = min(usado[c], max(0.0, total - d))
        usado[c] = ini + max(d, passo)
        pl.append((c, ini, d))
    return pl


def texto_png(path):
    """Texto do jeito do TikTok: branco com contorno preto fino, e o emoji de dado no fim."""
    f = font("Poppins-ExtraBold.ttf", 56)
    im = Image.new("RGBA", (W, 200), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    tw = d.textlength(TEXTO, font=f)
    e = emoji("🎲", 58)
    x0 = (W - tw - e.width - 14) / 2
    d.text((x0, 100), TEXTO, font=f, fill=(255, 255, 255), anchor="lm", stroke_width=5, stroke_fill=(0, 0, 0))
    im.alpha_composite(e, (int(x0 + tw + 14), 100 - e.height // 2))
    lg = logo_card(150)
    full = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    full.alpha_composite(im, (0, 660 - 100))
    full.alpha_composite(lg, (W - lg.width - 30, 40))
    full.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--antigo", nargs="+", required=True)
    ap.add_argument("--moderno", nargs="+", required=True)
    ap.add_argument("--rapido", type=float, default=1.0, help="acelera os clipes (ex.: 1.3)")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    pl = planos(a.antigo, CORTES_ANTES) + planos(a.moderno, CORTES_DEPOIS)
    over = os.path.join(OUT, "efeito_texto.png")
    texto_png(over)
    args, filt = [ffmpeg(), "-y", "-loglevel", "error"], []
    for i, (c, ini, d) in enumerate(pl):
        args += ["-ss", f"{ini:.3f}", "-t", f"{d * a.rapido + 0.2:.3f}", "-i", c]
        filt.append(f"[{i}:v]setpts=(PTS-STARTPTS)/{a.rapido},fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,"
                    f"crop={W}:{H},setsar=1,trim=duration={d:.3f},setpts=PTS-STARTPTS[v{i}]")
    n = len(pl)
    args += ["-i", over, "-ss", "0", "-t", f"{FIM:.3f}", "-i", REF]
    filt.append("".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[cat]")
    filt.append(f"[cat][{n}:v]overlay=0:0[vid]")
    filt.append(f"[{n + 1}:a]afade=t=out:st={FIM - 0.4:.2f}:d=0.4[aud]")
    com = os.path.join(OUT, "efeito_com_musica.mp4")
    subprocess.run(args + ["-filter_complex", ";".join(filt), "-map", "[vid]", "-map", "[aud]", "-c:v", "libx264",
                           "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                           "-movflags", "+faststart", com], check=True)
    sem = os.path.join(OUT, "efeito_sem_musica.mp4")
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", com, "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-shortest", sem], check=True)
    print("ok:", com, sem)


if __name__ == "__main__":
    main()
