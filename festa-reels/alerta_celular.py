#!/usr/bin/env python3
"""Abertura "ALERTA NO CELULAR" (18/nov/2026, pedido dele) que emenda na previsão do tempo da confraternização.

Tela de bloqueio de celular → chega uma notificação do "Grupo da firma" → o celular vibra e abre um ALERTA EXTREMO
(paródia: "Defesa Civil da DIVERSÃO", nunca o nome do órgão de verdade) com a previsão de CHUVA DE JOGOS → dedo toca
"VER BOLETIM" → zoom + flash → corta pro vídeo da previsão (previsao_*_final.mp4, que precisa existir).

    python3 alerta_celular.py --frame 0.5 1.5 3 5.4 6
    python3 alerta_celular.py           # intro + emenda → out/previsao_alerta_{com_som,para_musica}_final.mp4
"""
import argparse
import math
import os
import subprocess
import sys
import wave
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import comum_festa as C  # noqa: E402
from comum_festa import W, H, FPS, E  # noqa: E402
import previsao as P  # noqa: E402  (fontes e ease)

DUR = 6.4
T_NOTIF, T_ALERTA, T_TOQUE, T_ZOOM = 0.35, 1.0, 5.1, 5.55
SR = 44100
VERM = (214, 38, 48)
YC = 1250  # centro do cartão do alerta (a notificação do grupo fica visível acima)
gro, anton, ease = P.gro, P.anton, P.ease


@lru_cache(None)
def papel_parede():
    y = np.linspace(0, 1, H)[:, None, None]
    a = np.array([40, 30, 92], float)
    b = np.array([18, 70, 120], float)
    img = a * (1 - y) + b * y + np.zeros((H, W, 3))
    im = Image.fromarray(img.clip(0, 255).astype(np.uint8)).convert("RGBA")
    bl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(bl)
    for (x, yy, r, c) in [(200, 500, 380, (244, 136, 37, 150)), (900, 1200, 420, (28, 160, 190, 150)),
                          (300, 1650, 360, (255, 199, 31, 110))]:
        d.ellipse((x - r, yy - r, x + r, yy + r), fill=c)
    im.alpha_composite(bl.filter(ImageFilter.GaussianBlur(150)))
    return im


def tela_bloqueio(t):
    img = papel_parede().copy()
    d = ImageDraw.Draw(img)
    d.text((70, 62), "18:42", font=gro(40, 600), fill="white", anchor="lm")
    # ícones da barra: sinal + bateria
    for i in range(4):
        d.rectangle((W - 230 + i * 18, 72 - i * 7, W - 218 + i * 18, 78), fill="white")
    d.rounded_rectangle((W - 140, 50, W - 70, 76), 7, outline="white", width=3)
    d.rectangle((W - 135, 55, W - 95, 71), fill="white")
    d.text((W / 2, 300), "sexta-feira, 11 de dezembro", font=gro(44, 500), fill=(235, 238, 255), anchor="mm")
    d.text((W / 2, 470), "18:42", font=gro(250, 300), fill="white", anchor="mm")
    # notificação do grupo
    if t > T_NOTIF:
        a = ease((t - T_NOTIF) / 0.3)
        y = 615 - (1 - a) * 60
        n = Image.new("RGBA", (960, 190), (0, 0, 0, 0))
        dn = ImageDraw.Draw(n)
        dn.rounded_rectangle((0, 0, 959, 189), 40, fill=(255, 255, 255, 215))
        dn.rounded_rectangle((32, 38, 112, 118), 22, fill=(37, 211, 102))
        dn.ellipse((52, 58, 92, 98), outline="white", width=6)
        dn.text((140, 52), "Grupo da firma", font=gro(38, 700), fill=(20, 20, 30), anchor="lm")
        dn.text((928, 52), "agora", font=gro(30, 500), fill=(90, 90, 100), anchor="rm")
        dn.text((140, 104), "Jorge: quem vai animar a festa esse ano?", font=gro(34, 500), fill=(40, 40, 50),
                anchor="lm")
        dn.text((140, 148), "Ana: ninguém, né...", font=gro(34, 500),
                fill=(40, 40, 50), anchor="lm")
        n.putalpha(n.getchannel("A").point(lambda v: int(v * a)))
        img.alpha_composite(n, (60, int(y)))
    return img


def triangulo(d, cx, cy, s, cor):
    d.polygon([(cx, cy - s), (cx + s * 1.1, cy + s * 0.8), (cx - s * 1.1, cy + s * 0.8)], fill=cor)
    d.rounded_rectangle((cx - 6, cy - s * 0.45, cx + 6, cy + s * 0.25), 4, fill="white")
    d.ellipse((cx - 8, cy + s * 0.42, cx + 8, cy + s * 0.58), fill="white")


@lru_cache(None)
def cartao(apertado=False):
    w, h = 940, 800
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 46, fill=(250, 250, 252))
    d.rounded_rectangle((0, 0, w - 1, 200), 46, fill=VERM)
    d.rectangle((0, 150, w - 1, 200), fill=VERM)
    triangulo(d, 110, 100, 52, (255, 210, 40))
    d.text((200, 72), "ALERTA EXTREMO", font=anton(76), fill="white", anchor="lm")
    d.text((202, 145), "Defesa Civil da Diversão", font=gro(36, 600), fill=(255, 225, 225), anchor="lm")
    corpo = [("PREVISÃO DE CHUVA DE JOGOS", anton(64), VERM),
             ("na sua confraternização de fim de ano.", gro(40, 600), (30, 30, 40)),
             ("", None, None),
             ("Risco ALTO de climão, rajadas de", gro(38, 500), (50, 50, 60)),
             ("celular e silêncio constrangedor.", gro(38, 500), (50, 50, 60)),
             ("", None, None),
             ("Acompanhe o boletim a seguir.", gro(38, 700), (30, 30, 40))]
    y = 260
    for txt, f, cor in corpo:
        if f is None:
            y += 18
            continue
        d.text((w / 2, y), txt, font=f, fill=cor, anchor="mm")
        y += 66 if f.size > 50 else 52
    bx = (90, h - 170, w - 90, h - 60)
    d.rounded_rectangle(bx, 55, fill=(170, 25, 35) if apertado else VERM)
    d.text((w / 2, (bx[1] + bx[3]) / 2), "VER BOLETIM", font=anton(56), fill="white", anchor="mm")
    return im


def frame(fi):
    t = fi / FPS
    img = tela_bloqueio(t)
    if t > T_ALERTA:
        a = ease((t - T_ALERTA) / 0.25)
        img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(150 * a))))
        c = cartao(T_TOQUE <= t < T_TOQUE + 0.3)
        esc = 0.85 + 0.15 * P.out_back(min(1, (t - T_ALERTA) / 0.35)) if hasattr(P, "out_back") else a
        vib = 0
        if T_ALERTA < t < T_ALERTA + 1.8:  # vibrando
            vib = int(8 * math.sin(t * 2 * math.pi * 22)) * (1 if int((t - T_ALERTA) / 0.45) % 2 == 0 else 0)
        E.cola(img, c, W / 2 + vib, YC, 0, esc, a)
    if T_TOQUE - 0.35 < t < T_ZOOM + 0.2:  # dedo tocando o botão
        u = (t - T_TOQUE) / 0.35
        d = ImageDraw.Draw(img)
        cx, cy = W / 2 + 60, YC + 400 - 115
        r = 46 - 8 * max(0, min(1, 1 - abs(u)))
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255, 170))
        if u > 0:
            rr = 46 + 140 * min(1, u)
            d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=(255, 255, 255), width=5)
    if t > T_ZOOM:  # entra na tela + flash
        u = ease((t - T_ZOOM) / (DUR - T_ZOOM))
        z = 1 + 1.6 * u
        im = img.resize((int(W * z), int(H * z)), Image.BICUBIC)
        x0, y0 = (im.width - W) // 2, int((im.height - H) * YC / H)
        img = im.crop((x0, y0, x0 + W, y0 + H))
        img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * u ** 1.5))))
    return img.convert("RGB")


def render(fi):
    return frame(fi).tobytes()


# ---------------------------------------------------------------- som
def tom(f, d, forma=1.0):
    t = np.arange(int(d * SR)) / SR
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t) * forma
    return s * np.minimum(1, t / 0.01) * np.minimum(1, (d - t) / 0.02)


def audio():
    n = int(DUR * SR)
    o = np.zeros(n)

    def add(s, t0, g):
        i = int(t0 * SR)
        j = min(n, i + len(s))
        o[i:j] += s[:j - i] * g

    add(tom(1318, 0.09) + 0, T_NOTIF, 0.25)  # plim da notificação
    add(tom(1760, 0.12), T_NOTIF + 0.1, 0.22)
    for k in range(6):  # alerta: sequência de bipes (não é o tom oficial de emergência)
        t0 = T_ALERTA + k * 0.3
        add(tom(988 if k % 2 == 0 else 784, 0.22), t0, 0.32)
    t = np.arange(int(1.8 * SR)) / SR  # vibração do celular
    buzz = np.sign(np.sin(2 * np.pi * 165 * t)) * (np.sin(2 * np.pi * t / 0.9) > -0.2) * 0.5
    add(np.convolve(buzz, np.ones(30) / 30, "same"), T_ALERTA, 0.25)
    add(tom(2400, 0.03), T_TOQUE, 0.3)  # toque
    m = int((DUR - T_ZOOM) * SR)  # whoosh do zoom
    rng = np.random.default_rng(3)
    ru = np.convolve(rng.standard_normal(m), np.ones(18) / 18, "same") * np.linspace(0, 1, m) ** 2
    add(ru, T_ZOOM, 0.6)
    o = o / (np.abs(o).max() + 1e-9) * 0.7
    p = os.path.join(C.OUT, "alerta_intro.wav")
    st = np.repeat((o * 32767).astype(np.int16)[:, None], 2, 1)
    with wave.open(p, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(st.tobytes())
    return p


def emenda(intro, prev, out):
    cmd = [C.ffmpeg(), "-y", "-loglevel", "error", "-i", intro, "-i", prev, "-filter_complex",
           "[0:v]fps=30,format=yuv420p[v0];[1:v]fps=30,format=yuv420p[v1];"
           "[0:a]aresample=44100,aformat=channel_layouts=stereo[a0];[1:a]aresample=44100,aformat=channel_layouts=stereo[a1];"
           "[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]",
           "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-c:a", "aac",
           "-b:a", "192k", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", nargs="*", type=float)
    a = ap.parse_args()
    os.makedirs(C.OUT, exist_ok=True)
    if a.frame:
        C.folha([frame(int(x * FPS)) for x in a.frame], os.path.join(C.OUT, "frames_alerta.jpg"))
        return
    wav = audio()
    intro = os.path.join(C.OUT, "alerta_intro.mp4")
    C.encode(intro, render, list(range(int(DUR * FPS))), wav)
    for v in ("com_som", "para_musica"):
        tmp = os.path.join(C.OUT, f"previsao_alerta_{v}.mp4")
        emenda(intro, os.path.join(C.OUT, f"previsao_{v}_final.mp4"), tmp)
        C.final_loudness(tmp, tmp.replace(".mp4", "_final.mp4"))
        print(tmp.replace(".mp4", "_final.mp4"))


if __name__ == "__main__":
    main()
