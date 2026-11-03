"""Base dos 3 Reels novos do Becas (3/nov/2026): cenas REAIS de jogo na mesa (brutos deles) + estética da loja.

- CLIPES: trechos dos brutos (Drive de brutos → gravados-reels/brutos/, fora do git) com a cor tratada de leve
  (denoise + contraste/saturação mínimos, lição do Dia das Crianças: em vídeo gravado, mexer pouco).
- prepara(): extrai cada trecho para JPGs 1080x1920 em out/_cache (uma vez); quadro_clip() lê o quadro do tempo u.
- entrega(): grava as duas versões (com som / para música) e normaliza para −15,5 LUFS (*_final.mp4).
"""
import os
import subprocess
import sys
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
for p in ("assinatura-reels", "promo", "comum", "listas-reels"):
    sys.path.insert(0, os.path.join(REPO, p))
import estilo as E  # noqa: E402,F401
import tarde_becas as TB  # noqa: E402,F401
from motor import ffmpeg, encode, folha, ease, out_back  # noqa: E402,F401
from base import final_loudness  # noqa: E402

W, H, FPS = 1080, 1920, 30
OUT = os.path.join(ROOT, "out")
CACHE = os.path.join(OUT, "_cache")
BR_ = os.path.join(REPO, "gravados-reels", "brutos")
MAR, PET, LAR, AMA, BR, ROSA = E.MARROM, E.PETROLEO, E.LARANJA, E.AMARELO, E.BRANCO, TB.ROSA

# nome → (arquivo, nome do jogo na tela)
CLIPES = {
    "critter": ("mesa/critter.mp4", "CRITTER KITCHEN"),
    "sushi": ("mesa/sushi.mp4", "SUSHI GO!"),
    "canvas": ("mesa/canvas.mp4", "CANVAS"),
    "art": ("mesa/art_society.mp4", "ART SOCIETY"),
    "passaporte": ("mesa/passaporte.mp4", "PASSAPORTE MUNDO"),
    "unlock": ("mesa/unlock.mp4", "UNLOCK!"),
    "taketime": ("mesa/taketime.mp4", "TAKE TIME"),
    "taketime2": ("mesa/taketime2.mp4", "TAKE TIME"),
    "sky_dados": ("nov01/085111.mp4", "SKY TEAM"),
    "sky_painel": ("nov01/085359.mp4", "SKY TEAM"),
    "sky_caixa": ("nov01/084743.mp4", "SKY TEAM"),
    "sky_trilha": ("nov01/085317.mp4", "SKY TEAM"),
}
GRADE = ("scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,hqdn3d=3:3:4:4,"
         "eq=contrast=1.03:saturation=1.05:gamma=1.02,unsharp=5:5:0.35")


def chave(nome, t0, d, vel):
    return f"{nome}_{t0:.2f}_{d:.2f}_{vel:.2f}"


def prepara(trechos):
    """trechos = [(nome, t0, dur_na_tela, vel)]. Extrai os quadros que faltam."""
    os.makedirs(CACHE, exist_ok=True)
    for nome, t0, d, vel in trechos:
        pasta = os.path.join(CACHE, chave(nome, t0, d, vel))
        if os.path.isdir(pasta) and os.listdir(pasta):
            continue
        os.makedirs(pasta, exist_ok=True)
        arq = os.path.join(BR_, CLIPES[nome][0])
        vf = f"setpts=PTS/{vel},fps={FPS},{GRADE}"
        subprocess.run([ffmpeg(), "-v", "error", "-ss", str(t0), "-t", str(d * vel + 0.2), "-i", arq, "-vf", vf,
                        "-q:v", "2", os.path.join(pasta, "%04d.jpg")], check=True)
        print("cache:", pasta, len(os.listdir(pasta)), flush=True)


@lru_cache(maxsize=48)
def _abre(caminho):
    return Image.open(caminho).convert("RGBA")


def quadro_clip(nome, t0, d, vel, u):
    """Quadro do trecho no tempo u (s, desde o começo do trecho na tela)."""
    pasta = os.path.join(CACHE, chave(nome, t0, d, vel))
    n = len(os.listdir(pasta))
    i = max(0, min(n - 1, int(u * FPS)))
    return _abre(os.path.join(pasta, f"{i + 1:04d}.jpg")).copy()


@lru_cache(None)
def logo(w=150):
    return E.logo(w)


def marca(img):
    lg = logo(150)
    img.alpha_composite(lg, (W - 180, 40))


def surge(t, t0, d=0.3):
    if t < t0:
        return 0.0, 0.0
    u = min(1.0, (t - t0) / d)
    return min(1.0, u * 2), out_back(u)


def poe(img, im, x, y, t, t0, rot=0.0, d=0.3):
    a, s = surge(t, t0, d)
    E.cola(img, im, x, y, rot, s, a)


@lru_cache(None)
def etiqueta(txt, s=46, cor=AMA, fg=MAR):
    return E.pilula(txt, s, cor, fg, fonte_titulo=True)


@lru_cache(None)
def titulo(txt, s, cor=AMA):
    return E.titulo(txt, s, cor, larg_max=980)


def escurece(img, y0, y1, a=150):
    """Degradê escuro numa faixa (para o texto ler sobre o vídeo)."""
    g = Image.new("L", (1, 256))
    for k in range(256):
        g.putpixel((0, k), int(a * (1 - abs(k - 128) / 128) ** 0.6))
    m = g.resize((W, y1 - y0))
    sh = Image.new("RGBA", (W, y1 - y0), (20, 12, 6, 255))
    sh.putalpha(m)
    img.alpha_composite(sh, (0, y0))


def desfoca(img, r=18):
    return img.filter(ImageFilter.GaussianBlur(r))


@lru_cache(None)
def card_cta(w=920):
    """Convite final (igual nos 3): título, data em breve e reserva pelo WhatsApp."""
    c = E.bloco(w, 560, TB.CREME, raio=40, ow=8, sombra=14).copy()
    d = ImageDraw.Draw(c)
    d.text((w / 2, 78), "SUA VEZ  ×  BECAS CAFÉ", font=E.lilita(42), fill=PET, anchor="mm")
    d.text((w / 2, 170), "TARDE DE JOGOS", font=E.lilita(104), fill=LAR, anchor="mm", stroke_width=5, stroke_fill=MAR)
    sel = TB.selo_data(40)
    c.alpha_composite(sel, (int(w / 2 - sel.width / 2), 230))
    d.text((w / 2, 352), "R$ 30, e R$ 15 viram consumação no café", font=E.fig(36, 800), fill=MAR, anchor="mm")
    d.text((w / 2, 402), "a gente ensina todos os jogos", font=E.fig(36, 700), fill=MAR, anchor="mm")
    d.rounded_rectangle((60, 445, w - 60, 525), 30, fill=PET)
    d.text((w / 2, 485), f"RESERVE: WHATSAPP {TB.WHATS}", font=E.lilita(42), fill=BR, anchor="mm")
    return c


def entrega(nome, dur, render, wav_com, wav_sem):
    """Gera <nome>_com_som e <nome>_para_musica e normaliza (→ *_final.mp4)."""
    os.makedirs(OUT, exist_ok=True)
    n = int(round(dur * FPS))
    base = os.path.join(OUT, f"{nome}_com_som.mp4")
    encode(base, render, list(range(n)), wav_com)
    sem = os.path.join(OUT, f"{nome}_para_musica.mp4")
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", base, "-i", wav_sem, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", sem], check=True)
    for arq in (base, sem):
        final_loudness(arq, arq.replace(".mp4", "_final.mp4"))
