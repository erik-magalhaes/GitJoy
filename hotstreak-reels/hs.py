#!/usr/bin/env python3
"""Reels do Hot Streak – visual "Arquibancada" com a arte oficial do jogo (vetor do manual).

    python3 hs.py --teste            # teste curto do gancho (out/hs_teste.mp4)
    python3 hs.py --frame 1 3 6      # quadros de teste (out/frames.jpg)
"""
import argparse
import math
import os
import subprocess
import sys
from functools import lru_cache
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "..", "nekojima-reels"))
import som_neko as som  # noqa: E402

P = os.path.join(ROOT, "assets", "pecas")
FN = os.path.join(ROOT, "assets", "fonts")
OUT = os.path.join(ROOT, "out")
W, H, FPS = 1080, 1920, 30
POSE = 12

RED = (230, 40, 40)
DRED = (150, 20, 20)
YEL = (255, 214, 60)
CREAM = (250, 236, 200)
GREEN = (60, 120, 60)
WHITE = (255, 255, 255)
INK = (30, 20, 30)
MASC = ["p_hurley.png", "p_gobbler.png", "p_dangle.png", "p_mum.png"]


def seg(t, a, b):
    return min(1.0, max(0.0, (t - a) / (b - a)))


def ease(u):
    return u * u * (3 - 2 * u)


def out_back(u, s=1.7):
    u -= 1
    return u * u * ((s + 1) * u + s) + 1


def lerp(a, b, u):
    return a + (b - a) * u


def pose(t):
    return int(t * POSE) / POSE


@lru_cache(None)
def font(n, s):
    return ImageFont.truetype(os.path.join(FN, n), s)


@lru_cache(None)
def peca(n, h):
    im = Image.open(os.path.join(P, n)).convert("RGBA")
    return im.resize((max(2, int(im.width * h / im.height)), int(h)), Image.LANCZOS)


@lru_cache(None)
def com_sombra(n, h):
    im = peca(n, h)
    pad = 40
    out = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    a = Image.new("L", out.size, 0)
    a.paste(im.getchannel("A").point(lambda v: int(v * 0.4)), (pad + 12, pad + 18))
    sh = Image.new("RGBA", out.size, (20, 30, 20, 255))
    sh.putalpha(a.filter(ImageFilter.GaussianBlur(12)))
    out.alpha_composite(sh)
    out.alpha_composite(im, (pad, pad))
    return out


def cola(img, im, x, y, rot=0.0, sc=1.0, sx=1.0, sy=1.0, alpha=1.0):
    if sc <= 0.02 or alpha <= 0.01:
        return
    if abs(sc * sx - 1) > 0.003 or abs(sc * sy - 1) > 0.003:
        im = im.resize((max(2, int(im.width * sc * sx)), max(2, int(im.height * sc * sy))), Image.BICUBIC)
    if abs(rot) > 0.1:
        im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    if alpha < 1:
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    img.paste(im, (int(x - im.width / 2), int(y - im.height / 2)), im)


def pop(t, t0, d=0.35):
    u = seg(t, t0, t0 + d)
    return max(0.0, out_back(u)) if u < 1 else 1.0


# ---------------------------------------------------------------- cenário: arquibancada + pista
CROWD_H = 1300


@lru_cache(None)
def torcida():
    im = Image.open(os.path.join(P, "v_torcida_limpa.png")).convert("RGBA")
    s = CROWD_H / im.height
    return im.resize((int(im.width * s), CROWD_H), Image.LANCZOS)


@lru_cache(None)
def pista(w=1400, h=880):
    """Pista no estilo do tapete do jogo: faixas verdes, tracejado branco e estrelas claras."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lanes = 4
    lh = h / lanes
    for k in range(lanes):
        d.rectangle((0, k * lh, w, (k + 1) * lh), fill=(52, 160, 76) if k % 2 else (62, 178, 86))
        d.rectangle((0, k * lh, w, k * lh + 10), fill=(44, 140, 66))
    return im


def estrela(d, cx, cy, r, cor):
    pts = [(cx + (r if i % 2 == 0 else r * 0.45) * math.cos(-math.pi / 2 + i * math.pi / 5),
            cy + (r if i % 2 == 0 else r * 0.45) * math.sin(-math.pi / 2 + i * math.pi / 5)) for i in range(10)]
    d.polygon(pts, fill=cor)


def desenha_pista(img, y0, scroll):
    """Pista com marcas andando (scroll em px) para dar a sensação de velocidade."""
    base = pista().copy()
    d = ImageDraw.Draw(base)
    lh = base.height / 4
    for k in range(4):
        off = (scroll * (1 + 0.1 * k)) % 160
        for x in np.arange(-160, base.width + 160, 160) - off:
            d.rounded_rectangle((x, (k + 1) * lh - 26, x + 70, (k + 1) * lh - 12), radius=6, fill=WHITE)
        off2 = (scroll * 0.9) % 330
        for x in np.arange(-330, base.width + 330, 330) - off2:
            estrela(d, x + (k % 2) * 160, k * lh + lh * 0.42, 26, (176, 232, 176))
    img.paste(base, (int((W - base.width) / 2), int(y0)), base)
    d2 = ImageDraw.Draw(img)  # gramado e linha lateral embaixo da pista
    yb = int(y0 + base.height)
    if yb < H:
        d2.rectangle((0, yb, W, H), fill=(36, 110, 54))
        d2.rectangle((0, yb, W, min(H, yb + 14)), fill=WHITE)


def confete(img, t, n=120, seed=3, top=0, bottom=H):
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(seed)
    cols = [(255, 210, 60), (240, 60, 70), (60, 160, 240), (255, 255, 255), (250, 120, 40), (120, 200, 90)]
    for _ in range(n):
        x0, sp, ph = rng.uniform(0, W), rng.uniform(140, 320), rng.uniform(0, 6.28)
        y = top + (rng.uniform(0, bottom - top) + t * sp) % (bottom - top)
        x = x0 + 30 * math.sin(t * 2 + ph)
        a = t * 4 + ph
        col = cols[rng.integers(len(cols))]
        L = 20 * abs(math.cos(a)) + 6
        d.line((x - L * math.cos(a), y - L * math.sin(a) * 0.4, x + L * math.cos(a), y + L * math.sin(a) * 0.4),
               fill=col, width=9)


@lru_cache(None)
def placa(txt, size=96, fundo=RED, letra=YEL, w=None):
    """Placa de torcida no estilo do jogo (retângulo de papel com letras grossas)."""
    f = font("LuckiestGuy-Regular.ttf", size)
    lines = txt.split("\n")
    tw = max(f.getlength(l) for l in lines)
    bw = int(w or tw + size * 0.9)
    bh = int(size * 1.25 * len(lines) + size * 0.6)
    im = Image.new("RGBA", (bw + 30, bh + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((16, 18, bw + 16, bh + 18), fill=(0, 0, 0, 90))
    d.rectangle((0, 0, bw, bh), fill=fundo)
    for k, l in enumerate(lines):
        d.text((bw / 2, size * 0.35 + size * 1.25 * k + size * 0.62), l, font=f, fill=letra, anchor="mm",
               stroke_width=max(4, size // 16), stroke_fill=DRED if fundo == RED else INK)
    return im


def corredor(img, nome, x, y, h, t, fase=0.0, vel=1.0, rot0=0.0):
    """Mascote correndo: pulinho, balanço e esticadinha a cada passo (12 poses/s)."""
    tp = pose(t) * vel * 2 * math.pi * 1.6 + fase
    hop = abs(math.sin(tp)) * h * 0.06
    rot = rot0 + 7 * math.sin(tp)
    sq = 1 + 0.05 * math.cos(2 * tp)
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse((x - h * 0.28, y - 14, x + h * 0.28, y + 14), fill=(20, 60, 25, 110))
    cola(img, com_sombra(nome, h), x, y - h * 0.5 - hop, rot, 1.0, 1 / sq, sq)
    if vel > 0.2:  # poeirinha atrás
        rng = np.random.default_rng(int(t * POSE) + int(fase * 10))
        for k in range(3):
            r = rng.uniform(12, 26)
            px = x - h * 0.35 - k * 30 - rng.uniform(0, 20)
            d.ellipse((px - r, y - 20 - r, px + r, y - 20 + r), fill=(230, 245, 220, 150 - k * 40))


# ---------------------------------------------------------------- cenas do teste
def cena_gancho(img, t):
    tc = torcida()
    bob = 10 * abs(math.sin(pose(t) * 9))  # a torcida pula
    z = 1 + 0.04 * seg(t, 0, 4.5)
    im = tc.resize((int(tc.width * z), int(tc.height * z)), Image.BICUBIC)
    img.paste(im, (int((W - im.width) / 2), int(-80 - bob)), im)
    confete(img, t, 90, 1, 0, 1300)
    # chão da pista embaixo
    desenha_pista(img, 1180, t * 40)
    u = seg(t, 0.25, 0.75)
    x = lerp(-400, 540, ease(u))
    cola(img, com_sombra("p_hurley.png", 900), x, 1180 + 30 * (1 - ease(u)), lerp(-25, -4, ease(u)) +
         3 * math.sin(pose(t) * 5))
    cola(img, placa("APOSTOU NUM\nCACHORRO-QUENTE?!", 84), 540, 430, -4 + 1.5 * math.sin(pose(t) * 6), pop(t, 0.4))


def cena_largada(img, t):
    t0 = 4.5
    u = ease(seg(t, t0, t0 + 1.6))  # câmera desce da torcida até a pista
    cam = lerp(0, 450, u)
    tc = torcida()
    bob = 8 * abs(math.sin(pose(t) * 9))
    img.paste(tc, (int((W - tc.width) / 2), int(-60 - cam - bob)), tc)
    py = 1180 - cam
    desenha_pista(img, py, max(0.0, t - (t0 + 1.8)) * 900)
    confete(img, t, 60, 2, 0, int(1300 - cam))
    lanes_y = [py + 220 * (k + 1) - 26 for k in range(4)]
    largada = t0 + 1.9
    for k, nome in enumerate(MASC):
        v = seg(t, largada + k * 0.05, largada + 0.9)
        x = lerp(160, 360 + [180, 40, 120, -20][k], ease(v)) + (35 * math.sin(t * 1.3 + k) if v >= 1 else 0)
        corredor(img, nome, x, lanes_y[k], 300, t, fase=k * 1.3, vel=1.0 if t >= largada else 0.0)
    if t >= largada - 0.6 and t < largada + 0.3:
        cola(img, placa("JÁ!" if t >= largada else "3, 2, 1...", 120, YEL, RED), 540, 300, 0, pop(t, largada - 0.6, 0.2))
    if t >= largada + 1.0:
        cola(img, placa("QUEM VAI VENCER?", 92), 540, 260, -3, pop(t, largada + 1.0))


@lru_cache(None)
def logo_card(width):
    lg = Image.open(os.path.join(ROOT, "assets", "logo_suavez.png")).convert("RGBA")
    pad = int(lg.width * 0.06)
    card = Image.new("RGBA", (lg.width + pad * 2, lg.height + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=pad * 2,
                                           fill=(255, 255, 255, 255))
    card.alpha_composite(lg, (pad, pad))
    return card.resize((int(width), int(card.height * width / card.width)), Image.LANCZOS)


def frame_teste(t):
    img = Image.new("RGBA", (W, H), (40, 110, 60, 255))
    if t < 4.5:
        cena_gancho(img, t)
    else:
        cena_largada(img, t)
    if 4.4 <= t < 4.6:
        img = Image.blend(img, Image.new("RGBA", img.size, WHITE + (255,)), 0.7 * (1 - abs(t - 4.5) / 0.1))
    wm = logo_card(180)
    img.paste(wm, (W - wm.width - 30, 40), wm)
    return img.convert("RGB")


def render_teste(path, dur=10.0):
    wav = os.path.join(OUT, "hs_teste.wav")
    cues = [(0.25, "swoosh", 0.6), (0.4, "pop", 0.5), (0.0, "crowd", 0.7), (4.5, "stinger", 0.6),
            (5.8, "beat", 0.6), (6.4, "whistle", 0.8), (6.4, "crowd", 0.8), (7.4, "pop", 0.5), (9.2, "crowd", 0.6)]
    som.build(wav, dur, cues=cues)
    n = int(dur * FPS)
    cmd = [ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-framerate", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "19",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for fr in pool.imap(_rt, range(n), chunksize=4):
            p.stdin.write(fr)
    p.stdin.close()
    p.wait()
    print("ok:", path)


def _rt(k):
    return frame_teste(k / FPS).tobytes()


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    ap.add_argument("--teste", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.frame:
        ims = [frame_teste(x) for x in a.frame]
        sheet = Image.new("RGB", (360 * len(ims), 640))
        for k, im in enumerate(ims):
            sheet.paste(im.resize((360, 640), Image.LANCZOS), (360 * k, 0))
        sheet.save(os.path.join(OUT, "frames.jpg"), quality=90)
    if a.teste:
        render_teste(os.path.join(OUT, "hs_teste.mp4"))


if __name__ == "__main__":
    main()
