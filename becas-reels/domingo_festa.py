#!/usr/bin/env python3
"""Domingo de Jogos 13/12 — vídeo novo (24/nov, ela: "o aesthetic perdeu um pouco; quero na dinâmica das
GUARDA-CHUVINHAS com LUZINHA DE NATAL, focado nisso", e mandou o vídeo do story do @becascafe com o pessoal se divertindo).

Fundo do kit de fim de ano (`domingo.fundo`: guarda-chuvinhas balançando + pisca-pisca + estrelinhas). Um guarda-chuva
rosa SEGURA uma POLAROIDE grande pendurada (balança como móbile) e dentro dela passam as cenas reais da tarde de 20/11
(do repost do @becascafe, recortadas sem a moldura cinza, o cabeçalho e a legenda do story). Embaixo, uma pílula por cena.
Depois: DOMINGO DE JOGOS (especial de fim de ano) → SÓ 30 VAGAS (quadro de vagas) → convite.

    /usr/bin/python3 domingo_festa.py --frame 1 5 9 14 18 23 [--stories]
    /usr/bin/python3 domingo_festa.py      # out/festa_{reels,stories}_{com_som,para_musica}_final.mp4
"""
import math
import os
import subprocess
import sys
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter

import kit as K
import sons as S
import domingo as D
from tarde import E, TB, W, H, MAR, PET, LAR, AMA, BR, ROSA
from motor import FPS, ffmpeg

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = D.OUT
BRUTO = os.path.join(ROOT, "brutos", "nov24", "festa.mp4")   # = brutos/nov20/144913.mp4 (repost do @becascafe)
CROP = "crop=576:770:72:215"                                  # só o vídeo, sem moldura/cabeçalho/legenda
FW, FH = 720, 962                                             # foto dentro da polaroide

NOV06 = os.path.join(ROOT, "brutos", "nov06")
CAFE = "scale=720:-2,crop=720:962:0:(ih-962)*{ay}"
# (arquivo, recorte, início no bruto, duração, pílula embaixo): evento (repost) intercalado com o café
CENAS = [
    (BRUTO, CROP, 12.6, 2.4, "LEMBRA DA NOSSA TARDE DE JOGOS?"),
    (os.path.join(NOV06, "20261106_150333.mp4"), CAFE.format(ay=0.2), 5.8, 2.1, "NO BECA’S CAFÉ..."),
    (BRUTO, CROP, 1.8, 2.1, "SALÃO CHEIO!"),
    (os.path.join(NOV06, "20261106_151311.mp4"), CAFE.format(ay=0.5), 0.0, 2.1, "CAFÉ, DOCINHO..."),
    (BRUTO, CROP, 30.0, 2.1, "...JOGO PRA TODA IDADE"),
    (os.path.join(NOV06, "20261106_150657.mp4"), CAFE.format(ay=0.5), 7.6, 2.1, "LANCHINHO NA MESA"),
    (BRUTO, CROP, 50.4, 2.1, "E MUITA RISADA!"),
    (BRUTO, CROP, 40.2, 2.1, "GENTE NOVA EM CADA MESA"),
    (os.path.join(NOV06, "20261106_150726.mp4"), CAFE.format(ay=0.35), 1.6, 2.4, "AGORA VEM A EDIÇÃO DE NATAL!"),
]
INI = []
_t = 0.0
for c in CENAS:
    INI.append(_t)
    _t += c[3]
T_TIT = _t
T_QUADRO = T_TIT + 3.4
T_CTA = T_QUADRO + 4.0
DUR = T_CTA + 6.4
CACHE = os.path.join(OUT, "_cache_festa")


def prepara():
    for arq, crop, s, d, _ in CENAS:
        pasta = os.path.join(CACHE, f"{os.path.basename(arq)}_{s:.2f}_{d:.2f}")
        if os.path.isdir(pasta) and os.listdir(pasta):
            continue
        os.makedirs(pasta, exist_ok=True)
        vf = (f"fps={FPS},{crop},scale={FW}:{FH}:flags=lanczos,hqdn3d=3:3:4:4,"
              "eq=contrast=1.04:saturation=1.08:gamma=1.02,colorbalance=rs=0.03:bs=-0.03,unsharp=5:5:0.4")
        subprocess.run([ffmpeg(), "-v", "error", "-ss", str(s), "-t", str(d + 0.2), "-i", arq, "-vf", vf, "-q:v", "2",
                        os.path.join(pasta, "%04d.jpg")], check=True)


@lru_cache(maxsize=32)
def _foto(caminho):
    return Image.open(caminho).convert("RGBA")


def foto(k, u):
    arq, _, s, d, _ = CENAS[k]
    pasta = os.path.join(CACHE, f"{os.path.basename(arq)}_{s:.2f}_{d:.2f}")
    n = len(os.listdir(pasta))
    return _foto(os.path.join(pasta, f"{max(0, min(n - 1, int(u * FPS))) + 1:04d}.jpg"))


# ---------------------------------------------------------------- polaroide pendurada no guarda-chuva
FIO, UMB = 90, 230
M_LAT, M_TOP, M_BAIXO = 26, 26, 104


@lru_cache(None)
def moldura():
    w, h = FW + 2 * M_LAT, FH + M_TOP + M_BAIXO
    im = Image.new("RGBA", (w + 24, h + 24), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle((14, 16, w + 14, h + 16), fill=MAR + (150,))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w - 1, h - 1), fill=D.CREME + (255,), outline=MAR, width=5)
    txt = "tarde de jogos no Beca’s"
    f = E.fig(44, 800)
    d.text((w / 2, FH + M_TOP + M_BAIXO / 2), txt, font=f, fill=MAR, anchor="mm")
    return im


@lru_cache(None)
def guarda():
    return TB.guarda_chuva(UMB, ROSA, 3)


def sprite(k, u):
    mol = moldura().copy()
    mol.alpha_composite(foto(k, u), (M_LAT, M_TOP))
    d = ImageDraw.Draw(mol)
    d.rectangle((M_LAT, M_TOP, M_LAT + FW - 1, M_TOP + FH - 1), outline=MAR, width=3)
    umb = guarda()
    hook = 14 + 0.75 * UMB + 2
    gap = 30
    alt = FIO + hook + gap + mol.height
    S_ = int(2 * alt + 20)
    im = Image.new("RGBA", (S_, S_), (0, 0, 0, 0))
    cx = cy = S_ / 2
    dd = ImageDraw.Draw(im)
    dd.line([(cx, cy), (cx, cy + FIO)], fill=(150, 120, 100), width=4)
    im.alpha_composite(umb, (int(cx - umb.width / 2), int(cy + FIO - 6)))
    hx, hy = cx - 0.055 * UMB, cy + FIO - 6 + hook
    top = hy + gap
    for ox in (-0.32, 0.32):   # dois fios do gancho até os cantos de cima da polaroide
        dd.line([(hx, hy - 2), (hx + ox * mol.width, top + 10)], fill=MAR, width=4)
    im.alpha_composite(mol, (int(hx - mol.width / 2 + 12), int(top)))
    dd.ellipse((hx - 10, hy - 12, hx + 10, hy + 8), fill=BR, outline=MAR, width=4)
    return im


def balanco(t):
    amort = 1 + 1.2 * math.exp(-t * 2.0)
    return 2.2 * amort * math.sin(2 * math.pi * t / 2.6)


def polaroide(img, t):
    k = max(i for i in range(len(CENAS)) if INI[i] <= t)
    u = t - INI[k]
    sp = sprite(k, u)
    cai = max(0.0, 1 - t / 0.45) ** 2 * 900          # cai do teto no comecinho
    r = sp.rotate(balanco(t), resample=Image.BICUBIC)
    img.alpha_composite(r, (int(W / 2 - r.width / 2), int(-r.height / 2 - cai)))
    rot = (-2, 2, -1, 1.5, -2, 1)[k % 6]
    s = 58 if k in (0, len(CENAS) - 1) else 64
    K.poe(img, K.etiqueta(CENAS[k][4], s, AMA if k not in (0, len(CENAS) - 1) else VERM_ETQ, MAR if k not in (0, len(CENAS) - 1) else BR),
          W / 2, 1475, t, INI[k] + 0.05, rot, d=0.25)


VERM_ETQ = D.VERM


def quadro(t, modo="reels"):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    if t < T_TIT:
        img.alpha_composite(D.fundo(t + 3.0))
        polaroide(img, t)
    elif t < T_QUADRO:
        D.titulo(img, t)
    elif t < T_CTA:
        D.quadro_vagas(img, t)
    else:
        D.cta(img, t, modo)
    for tb in (T_TIT, T_QUADRO, T_CTA):
        dd = t - tb
        if 0 <= dd < 0.12:
            img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(200 * (1 - dd / 0.12)))))
    if t < T_TIT:
        K.marca(img)
    return img.convert("RGB")


D.T_TIT, D.T_QUADRO, D.T_CTA = T_TIT, T_QUADRO, T_CTA


def render_reels(fi):
    return quadro(fi / FPS, "reels").tobytes()


def render_stories(fi):
    return quadro(fi / FPS, "stories").tobytes()


def audio(nome):
    ev = [(0.05, S.sopro(0.4), 0.3), (0.45, S.estouro(), 0.3)]
    ev += [(INI[k], S.tic(k % 2 == 0), 0.35) for k in range(1, len(CENAS))]
    ev += [(T_TIT, S.sino(), 0.45), (T_TIT + 0.05, S.estouro(), 0.5)]
    ev += [(T_QUADRO + 0.85 + k * 0.045, S.tic(k % 2 == 0), 0.15) for k in range(D.VAGAS)]
    ev += [(T_QUADRO + 2.4, S.plim(), 0.5), (T_CTA, S.sopro(0.5, False), 0.4), (T_CTA + 0.35, S.carta_vira(), 0.5)]
    mus = S.musica_pop(DUR + 0.5, 0.0)
    com = os.path.join(OUT, f"{nome}_com.wav")
    sem = os.path.join(OUT, f"{nome}_sem.wav")
    S.grava(com, DUR, ev, mus, musica_ganho=0.45, fx_ganho=0.75)
    S.grava(sem, DUR, ev, None, fx_ganho=0.75)
    return com, sem


def main():
    args = sys.argv[1:]
    modo = "stories" if "--stories" in args else "reels"
    prepara()
    if "--frame" in args:
        ts = [float(a) for a in args[args.index("--frame") + 1:] if not a.startswith("--")]
        K.folha([quadro(t, modo) for t in ts], os.path.join(OUT, "frames_festa.jpg"))
        print("DUR", DUR)
        return
    for m in ("reels", "stories"):
        com, sem = audio(f"festa_{m}")
        K.entrega(f"festa_{m}", DUR, render_reels if m == "reels" else render_stories, com, sem)
    print("ok", DUR)


if __name__ == "__main__":
    main()
