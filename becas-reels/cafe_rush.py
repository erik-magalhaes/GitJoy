#!/usr/bin/env python3
""""UM CAFÉ... NUM CAFÉ" (7/nov/2026, ideia dele): a capa do Coffee Rush ANIMADA pelo Gemini (Veo, prompt meu) com a
imagem `coffee-reels/out/coffee_rush_9x16.png`... ele usou a foto quadrada com fundo transparente, então os 4 primeiros
segundos têm bordas PRETAS → `tira_preto()` troca o preto ligado à borda por creme. O fim do clipe (7–10 s) já é a
caixa numa mesa de madeira com café e guarda-chuvinhas coloridas no teto (cara do Beca’s).

    0–10 s   clipe do Gemini (`coffee-reels/brutos/gemini1.mp4`, 720x1280, 24 fps → 1080x1920) + gancho + data
    10–15,6  convite da Tarde de Jogos (fundo = último quadro desfocado + guarda-chuvinhas), Reels ou Stories

    /usr/bin/python3 cafe_rush.py [--stories] [--frame 0.5 3 6 8.5 12]
"""
import os
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

import no_becas as NB
from no_becas import K, S, W, H, FPS, MAR, PET, LAR, AMA, BR, Plano, etq, tit

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = K.OUT
GEMINI = os.path.join(AQUI, "..", "coffee-reels", "brutos", "gemini1.mp4")
K.CLIPES["rush"] = (os.path.abspath(GEMINI), "COFFEE RUSH")
CLIPE = Plano("rush", 0.0, 10.0, 1.0)
VID = CLIPE.d
DUR = VID + 5.6
FMT = "reels"
T_DATA = 7.4  # a caixa já está na mesa do café


def creme():
    y = np.linspace(0, 1, H)[:, None]
    top, bot = np.array([246, 236, 218]), np.array([226, 206, 178])
    return np.broadcast_to((top * (1 - y) + bot * y)[:, None, :], (H, W, 3)).astype(np.float32)


CREME = creme()


def tira_preto(im):
    """O preto que encosta na borda do quadro (fundo transparente da foto quadrada) vira creme, com borda suave."""
    a = np.asarray(im.convert("RGB")).astype(np.float32)
    escuro = a.max(2) < 28
    if escuro.mean() < 0.002:
        return im
    lab, n = ndimage.label(escuro)
    borda = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    m = np.isin(lab, borda[borda > 0])
    m = ndimage.binary_dilation(m, iterations=2).astype(np.float32)
    m = ndimage.gaussian_filter(m, 3)[:, :, None]
    out = a * (1 - m) + CREME * m
    return Image.fromarray(out.astype(np.uint8)).convert("RGBA")


def quadro(t):
    if t < VID:
        img = tira_preto(CLIPE.quadro(t))
        if t < 3.8:
            K.escurece(img, 120, 520, 110)
            K.poe(img, tit("JÁ PENSOU EM JOGAR\nUM CAFÉ... NUM CAFÉ?", 78, BR), W / 2, 320, t, 0.2, -1.5)
        if t >= T_DATA:
            K.poe(img, etq("O COFFEE RUSH VAI ESTAR NA MESA!", 46, BR, MAR), W / 2, 1380, t, T_DATA, -1.5)
            K.poe(img, etq("SEXTA, 20/11 · TARDE DE JOGOS NO BECA’S", 40, AMA, MAR), W / 2, 1490, t, T_DATA + 0.35, 1)
        K.marca(img)
        return img.convert("RGB")
    img = CLIPE.quadro(VID - 0.01).filter(ImageFilter.GaussianBlur(12))
    u = t - VID
    NB.escuro(img, min(140, u * 400))
    NB.balanco(img, t)
    if FMT == "stories":
        K.poe(img, tit("VOCÊ VEM?", 130, AMA), W / 2, 400, t, VID + 0.1, -2)
        K.poe(img, NB.card_convite(), W / 2, 880, t, VID + 0.35, 1)
        NB.linha_link(img, t, VID + 0.9, 1200)
        K.poe(img, etq("MANDA PRA QUEM VAI COM VOCÊ!", 40, BR, MAR), W / 2, 1660, t, VID + 1.1, -1.5)
    else:
        K.poe(img, tit("VOCÊ VEM?", 130, AMA), W / 2, 520, t, VID + 0.1, -2)
        K.poe(img, NB.card_convite(), W / 2, 1020, t, VID + 0.35, 1)
        K.poe(img, etq("COMENTA: CAFÉ PRETINHO OU COM LEITE?", 38, BR, MAR), W / 2, 1440, t, VID + 1.0, -1.5)
    return img.convert("RGB")


def render(fi):
    return quadro(fi / FPS).tobytes()


def ambiente():
    """Som do próprio clipe do Gemini (café, xícaras) a 44,1 kHz, mono, com fade no fim."""
    wav = os.path.join(OUT, "cafe_rush_amb.wav")
    subprocess.run([K.ffmpeg(), "-y", "-v", "error", "-i", GEMINI, "-ac", "1", "-ar", "44100", wav], check=True)
    with wave.open(wav) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
    f = int(0.6 * S.SR)
    a[-f:] *= np.linspace(1, 0, f)
    return a / (np.abs(a).max() + 1e-9)


def audio():
    ev = [(0.0, ambiente(), 0.5), (0.2, S.cartao(), 0.35), (T_DATA, S.cartao(), 0.3), (T_DATA + 0.35, S.plim(), 0.35),
          (VID, S.sino(), 0.45), (VID + 0.35, S.cartao(), 0.4), (VID + 1.0, S.cartao(), 0.3)]
    return ev, S.musica_cafe(DUR + 0.5), 0.38


def main():
    global FMT
    FMT = "stories" if "--stories" in sys.argv else "reels"
    nome = "cafe_rush" + ("_stories" if FMT == "stories" else "")
    K.prepara([CLIPE.trecho()])
    os.makedirs(OUT, exist_ok=True)
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:] if not x.startswith("--")]
        K.folha([quadro(x) for x in ts], os.path.join(OUT, f"frames_{nome}.jpg"))
        print("ok", DUR)
        return
    ev, mus, mg = audio()
    com, sem = os.path.join(OUT, f"{nome}_com.wav"), os.path.join(OUT, f"{nome}_sem.wav")
    S.grava(com, DUR, ev, mus, musica_ganho=mg, fx_ganho=0.8)
    S.grava(sem, DUR, ev, None, fx_ganho=0.8)
    K.entrega(nome, DUR, render, com, sem)
    print("ok", nome, DUR)


if __name__ == "__main__":
    main()
