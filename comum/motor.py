"""Peças comuns dos Reels novos (tipos-reels, quiz-reels, byebye-reels): animação, textos, legendas,
linha do tempo da narração e render (PIL → ffmpeg)."""
import json
import math
import os
import subprocess
from functools import lru_cache
from multiprocessing import Pool

from PIL import Image, ImageDraw, ImageFilter, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOBBY = os.path.join(REPO, "hobby-reels", "assets")
FN = os.path.join(HOBBY, "fonts")
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
LOGO = os.path.join(HOBBY, "logo_suavez.png")
W, H, FPS = 1080, 1920, 30
WHITE = (255, 255, 255)


# ---------------------------------------------------------------- tempo
def seg(t, a, b):
    return min(1.0, max(0.0, (t - a) / (b - a)))


def ease(u):
    return u * u * (3 - 2 * u)


def out_back(u, s=1.6):
    u -= 1
    return u * u * ((s + 1) * u + s) + 1


def lerp(a, b, u):
    return a + (b - a) * u


def pop(t, t0, d=0.35):
    u = seg(t, t0, t0 + d)
    return max(0.0, out_back(u)) if u < 1 else 1.0


def quica(t, t0, d=0.6):
    """Queda com quique (0 → 1)."""
    u = seg(t, t0, t0 + d)
    if u >= 1:
        return 1.0
    if u < 0.6:
        return (u / 0.6) ** 2
    v = (u - 0.6) / 0.4
    return 1 - 0.12 * math.sin(v * math.pi)


# ---------------------------------------------------------------- imagens e textos
@lru_cache(None)
def font(n, s):
    return ImageFont.truetype(os.path.join(FN, n), int(s))


@lru_cache(None)
def emoji(ch, size):
    f = ImageFont.truetype(EMOJI, 109)
    im = Image.new("RGBA", (180, 180), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    return im.resize((int(size), max(2, int(im.height * size / im.width))), Image.LANCZOS)


@lru_cache(None)
def caixa_original(nome):
    """Caixa recortada do acervo (hobby-reels), sem os bloquinhos de JPEG e com um leve realce."""
    import cv2
    import numpy as np
    p = os.path.join(HOBBY, "caixas", nome + ".png")
    if not os.path.exists(p):
        p = os.path.join(HOBBY, "acervo", nome + ".png")
    im = Image.open(p).convert("RGBA")
    rgb = cv2.fastNlMeansDenoisingColored(np.ascontiguousarray(np.asarray(im)[..., :3]), None, 4, 4, 5, 15)
    out = Image.fromarray(rgb).filter(ImageFilter.UnsharpMask(radius=1.4, percent=60, threshold=2)).convert("RGBA")
    out.putalpha(im.getchannel("A"))
    return out


@lru_cache(None)
def caixa(nome, h):
    im = caixa_original(nome)
    return im.resize((max(2, int(im.width * h / im.height)), int(h)), Image.LANCZOS)


@lru_cache(None)
def logo_card(w=170):
    lg = Image.open(LOGO).convert("RGBA")
    lg = lg.resize((int(w), int(lg.height * w / lg.width)), Image.LANCZOS)
    pad = max(10, int(w * 0.07))
    card = Image.new("RGBA", (lg.width + pad * 2, lg.height + pad * 2 - 4), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=int(pad * 1.4), fill=WHITE)
    card.alpha_composite(lg, (pad, pad - 2))
    return card


def cola(img, im, x, y, rot=0.0, sc=1.0, alpha=1.0):
    if sc <= 0.02 or alpha <= 0.01:
        return
    if abs(sc - 1) > 0.003:
        im = im.resize((max(2, int(im.width * sc)), max(2, int(im.height * sc))), Image.BICUBIC)
    if abs(rot) > 0.1:
        im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    if alpha < 1:
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    img.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))


def sombra(im, blur=22, off=(0, 24), a=0.45, cor=(0, 0, 0)):
    s = Image.new("RGBA", (im.width + blur * 4, im.height + blur * 4), (0, 0, 0, 0))
    sa = Image.new("RGBA", im.size, cor + (255,))
    sa.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    s.alpha_composite(sa, (blur * 2 + off[0], blur * 2 + off[1]))
    s = s.filter(ImageFilter.GaussianBlur(blur))
    s.alpha_composite(im, (blur * 2, blur * 2))
    return s


@lru_cache(None)
def letreiro(txt, size, cor=WHITE, contorno=(20, 20, 30), sw=10, fonte="Bungee-Regular.ttf", sombra_px=0,
             cor_sombra=(0, 0, 0)):
    """Texto (várias linhas) com contorno grosso e, se pedir, sombra 3D em degraus."""
    f = font(fonte, size)
    linhas = txt.split("\n")
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    lw = max(tmp.textlength(l, font=f) for l in linhas)
    lh = size * 1.15
    m = sw + sombra_px + 16
    im = Image.new("RGBA", (int(lw + 2 * m), int(lh * len(linhas) + 2 * m)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k, l in enumerate(linhas):
        x, y = im.width / 2 - sombra_px / 2, m + k * lh + lh / 2 - sombra_px / 2
        for s in range(sombra_px, 0, -1):
            d.text((x + s, y + s), l, font=f, fill=cor_sombra, anchor="mm", stroke_width=sw, stroke_fill=cor_sombra)
        d.text((x, y), l, font=f, fill=cor, anchor="mm", stroke_width=sw, stroke_fill=contorno)
    return im


@lru_cache(None)
def pilula(txt, size, cor, fg=WHITE, borda=WHITE, fonte="Bungee-Regular.ttf", bw=5):
    f = font(fonte, size)
    tw = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textlength(txt, font=f)
    w, h = int(tw + size * 1.6), int(size * 1.75)
    im = Image.new("RGBA", (w + 4, h + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((2, 2, w + 1, h + 1), radius=h // 2, fill=cor, outline=borda, width=bw)
    d.text((w / 2 + 2, h / 2 + 4), txt, font=f, fill=fg, anchor="mm")
    return im


# ---------------------------------------------------------------- legendas e narração
def quebra(txt, maxc=34):
    chunks, cur = [], []
    for w in txt.split():
        cur.append(w)
        if len(" ".join(cur)) > maxc or w[-1] in ".?!:":
            chunks.append(" ".join(cur))
            cur = []
    if cur:
        chunks.append(" ".join(cur))
    return chunks


def default_subs(scenes, roteiro):
    """Legendas do roteiro distribuídas pela cena (prévia sem voz)."""
    out = []
    for (a, b), txt in zip(scenes, roteiro):
        if not txt:
            continue
        ch = quebra(txt)
        span = (b - a - 0.6) / len(ch)
        for k, c in enumerate(ch):
            out.append((a + 0.3 + k * span, a + 0.3 + (k + 1) * span, c))
    return out


@lru_cache(None)
def sub_img(text):
    f = font("Poppins-ExtraBold.ttf", 50)
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        tst = (cur + " " + w_).strip()
        if f.getlength(tst) > 920 and cur:
            lines.append(cur)
            cur = w_
        else:
            cur = tst
    lines.append(cur)
    lh = 62
    w = int(max(f.getlength(l) for l in lines)) + 50
    h = lh * len(lines) + 24
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=18, fill=(0, 0, 0, 205))
    for k, l in enumerate(lines):
        d.text((w / 2, 12 + lh * k + lh / 2), l, font=f, fill=WHITE, anchor="mm")
    return im


def legenda(img, subs, t, y=1740):
    for a_, b_, s in subs:
        if a_ <= t < b_:
            si = sub_img(s)
            img.alpha_composite(si, ((W - si.width) // 2, y - si.height // 2))


class Linha:
    """Linha do tempo da narração (narracao/timeline.json): converte o tempo do vídeo final ↔ tempo original."""

    def __init__(self, path):
        self.tl = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else None

    def to_orig(self, t):
        if self.tl is None:
            return t
        for o0, o1, n0, n1 in self.tl["cenas"]:
            if n0 <= t < n1:
                return o0 + (t - n0) * (o1 - o0) / (n1 - n0)
        o0, o1, n0, n1 = self.tl["cenas"][-1]
        return o0 + (t - n0) * (o1 - o0) / (n1 - n0)

    def warp(self, t_orig):
        if self.tl is None:
            return t_orig
        for o0, o1, n0, n1 in self.tl["cenas"]:
            if o0 <= t_orig < o1:
                return n0 + (t_orig - o0) * (n1 - n0) / (o1 - o0)
        return t_orig


# ---------------------------------------------------------------- render
def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def encode(out_path, render_frame, args, wav=None, workers=4):
    """render_frame(arg) → bytes RGB de um quadro. Sem wav, grava uma faixa de áudio muda."""
    audio = ["-i", wav] if wav else ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]
    cmd = [ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-framerate", str(FPS), "-i", "-"] + audio + [
        "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-tune", "animation", "-maxrate", "14M",
        "-bufsize", "28M", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
        "-movflags", "+faststart", out_path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = len(args)
    with Pool(workers) as pool:
        for k, fr in enumerate(pool.imap(render_frame, args, chunksize=6)):
            p.stdin.write(fr)
            if k % 300 == 0:
                print(f"  quadro {k}/{n}", flush=True)
    p.stdin.close()
    p.wait()
    print("ok:", out_path, flush=True)


def previa_720p(src, dst, kbps=3300):
    """Versão para o chat (limite de 30 MB): 720p em duas passadas."""
    base = [ffmpeg(), "-y", "-loglevel", "error", "-i", src, "-vf", "scale=720:1280", "-c:v", "libx264",
            "-preset", "slow", "-tune", "animation", "-b:v", f"{kbps}k"]
    log = dst + ".passlog"
    subprocess.run(base + ["-pass", "1", "-passlogfile", log, "-an", "-f", "null", "/dev/null"], check=True)
    subprocess.run(base + ["-pass", "2", "-passlogfile", log, "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
                           dst], check=True)
    for ext in ("-0.log", "-0.log.mbtree"):
        if os.path.exists(log + ext):
            os.remove(log + ext)
    print("ok:", dst, os.path.getsize(dst) // 1024 ** 2, "MB", flush=True)


def loudness(src, dst, ganho_db=1.6):
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", src, "-c:v", "copy", "-af",
                    f"volume={ganho_db}dB,alimiter=limit=0.89", "-c:a", "aac", "-b:a", "192k", dst], check=True)


def folha(frames, path):
    cols = min(6, len(frames))
    rows = math.ceil(len(frames) / cols)
    sheet = Image.new("RGB", (360 * cols, 640 * rows))
    for k, im in enumerate(frames):
        sheet.paste(im.resize((360, 640), Image.LANCZOS), (360 * (k % cols), 640 * (k // cols)))
    sheet.save(path, quality=88)
