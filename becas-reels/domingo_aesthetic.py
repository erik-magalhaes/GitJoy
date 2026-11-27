#!/usr/bin/env python3
"""Domingo de Jogos 13/12 — versão AESTHETIC (24/nov, ela: "não gostei dos takes, as pessoas olhando pra câmera fica
esquisito; deixa mais aesthetic"). Só DETALHES, sem ninguém olhando pra câmera: guarda-chuvinhas vistas de baixo, a
parede do Beca’s, bolo nuvem, vitrine e MÃOS nos jogos (Canvas, Sushi Go, Art Society, Critter Kitchen). Câmera lenta,
cor quente e suave (preto levantado, pouca saturação), bokeh de pisca-pisca dourado/vermelho/verde passando, letra
serifada fina (DM Serif Display + Cormorant itálico), fusões suaves, trilha lounge calma.

    /usr/bin/python3 domingo_aesthetic.py --frame 1 10 22 [--stories]
    /usr/bin/python3 domingo_aesthetic.py      # out/aesthetic_{reels,stories}_{com_som,para_musica}_final.mp4
"""
import math
import os
import random
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import kit as K
import sons as S
import domingo as D
from kit import W, H, FPS, OUT, TB

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOV06 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brutos", "nov06")
MESA = os.path.join(K.BR_, "mesa")
DIA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brutos", "nov20", "180822.mp4")
F_SERIF = os.path.join(REPO, "comum", "fontes", "DMSerifDisplay-Regular.ttf")
F_ITAL = os.path.join(REPO, "halloween-reels", "assets", "fonts", "Cormorant-Italic.ttf")
F_REG = os.path.join(REPO, "halloween-reels", "assets", "fonts", "Cormorant.ttf")

K.GRADE = ("scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,hqdn3d=4:4:5:5,"
           "eq=contrast=0.94:saturation=0.86:gamma=1.04,"
           "colorbalance=rs=0.05:gs=0.01:bs=-0.05:rm=0.03:bm=-0.03:rh=0.02:bh=-0.04,"
           "curves=all='0/0.07 0.5/0.52 1/0.96',unsharp=5:5:0.25")

# (nome, arquivo, início no bruto, segundos na tela, velocidade, texto grande, texto pequeno)
PLANOS = [
    ("a_chuva", os.path.join(NOV06, "20261106_150333.mp4"), 5.6, 3.2, 0.6, "Domingo de Jogos", "edição de fim de ano"),
    ("a_parede", os.path.join(NOV06, "20261106_150726.mp4"), 1.6, 2.6, 0.6, "um domingo diferente", "no Beca’s Café"),
    ("a_bolo", os.path.join(NOV06, "20261106_151311.mp4"), 0.0, 2.5, 0.65, "café, doce...", ""),
    ("a_canvas", os.path.join(MESA, "canvas.mp4"), 3.4, 2.5, 0.7, "...e um jogo novo na mesa", ""),
    ("a_mesona", DIA, 2.2, 2.8, 0.9, "pra rir com quem", "você gosta"),
    ("a_art", os.path.join(MESA, "art_society.mp4"), 0.4, 2.4, 0.7, "e fechar o ano", "jogando"),
    ("a_balcao", DIA, 37.3, 2.6, 0.6, "mais de 30 jogos", "esperando por você"),
    ("a_vitrine", os.path.join(NOV06, "20261106_150657.mp4"), 7.6, 2.4, 0.7, "só 30 lugares", ""),
    ("a_critter", os.path.join(MESA, "critter.mp4"), 1.0, 2.5, 0.7, "13 de dezembro", "das 13h às 19h"),
]
FUSAO = 0.5
FUNDO_FIM = ("a_fim", os.path.join(NOV06, "20261106_150333.mp4"), 5.9, 7.0, 0.35)
for p in PLANOS + [FUNDO_FIM]:
    K.CLIPES[p[0]] = (p[1], "")

INI = []
_t = 0.0
for p in PLANOS:
    INI.append(_t)
    _t += p[3] - FUSAO
T_FIM = _t
DUR = T_FIM + 6.6
DOURADO = (246, 214, 150)
CREME = (252, 246, 234)


@lru_cache(None)
def fonte(path, s):
    return ImageFont.truetype(path, s)


def espacado(txt, f, track):
    """Texto em caixa alta espaçada (largura, desenhador)."""
    ws = [f.getlength(c) for c in txt]
    return sum(ws) + track * (len(txt) - 1), ws


def escreve(img, xy, txt, f, cor, a=1.0, track=0, sombra=True):
    """Texto centrado em xy com sombra difusa; a = opacidade."""
    if a <= 0:
        return
    larg, ws = espacado(txt, f, track)
    asc, desc = f.getmetrics()
    pad = 60
    camada = Image.new("RGBA", (int(larg) + 2 * pad, asc + desc + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(camada)
    x = pad
    for c, w_ in zip(txt, ws):
        d.text((x, pad), c, font=f, fill=cor + (255,))
        x += w_ + track
    if sombra:
        sh = Image.new("RGBA", camada.size, (0, 0, 0, 0))
        sh.putalpha(camada.getchannel("A").filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.55)))
        camada = Image.alpha_composite(sh, camada)
    if a < 1:
        camada.putalpha(camada.getchannel("A").point(lambda v: int(v * a)))
    img.alpha_composite(camada, (int(xy[0] - camada.width / 2), int(xy[1] - camada.height / 2)))


# ---------------------------------------------------------------- bokeh de pisca-pisca
RND = random.Random(7)
BOKEH = []
for _ in range(26):
    cor = RND.choice([(255, 196, 110)] * 7 + [(255, 110, 90), (130, 210, 120), (255, 232, 185)] * 1)
    BOKEH.append((RND.uniform(-0.1, 1.1), RND.uniform(0, 1), RND.uniform(14, 46), RND.uniform(0.008, 0.03),
                  RND.uniform(0, 6.28), cor, RND.uniform(0.25, 0.6)))


def bokeh(t, forca=1.0):
    sw, shh = W // 4, H // 4
    cam = np.zeros((shh, sw, 3), np.float32)
    im = Image.new("RGB", (sw, shh))
    d = ImageDraw.Draw(im)
    for x0, y0, r, vel, fase, cor, a in BOKEH:
        x = (x0 + 0.02 * math.sin(t * 0.4 + fase)) * sw
        y = ((y0 - vel * t) % 1.15 - 0.075) * shh
        pis = 0.65 + 0.35 * math.sin(t * 1.3 + fase * 3)
        k = a * pis * forca
        rr = r / 4
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=tuple(int(c * k) for c in cor))
    im = im.filter(ImageFilter.GaussianBlur(2.2)).resize((W, H), Image.BILINEAR)
    cam = np.asarray(im, np.float32)
    return cam


def tela(img_rgb, t, forca=1.0):
    arr = np.asarray(img_rgb.convert("RGB"), np.float32)
    b = bokeh(t, forca)
    arr = 255 - (255 - arr) * (255 - b) / 255  # screen
    # vinheta suave
    return Image.fromarray(np.clip(arr * VINHETA[..., None], 0, 255).astype(np.uint8)).convert("RGBA")


yy, xx = np.mgrid[0:H, 0:W]
_r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
VINHETA = (1 - 0.32 * np.clip(_r - 0.35, 0, 1) ** 1.4).astype(np.float32)
del yy, xx, _r


# ---------------------------------------------------------------- planos
def quadro_plano(k, t):
    nome, _, t0, d, vel, _, _ = PLANOS[k]
    u = t - INI[k]
    im = K.quadro_clip(nome, t0, d, vel, u).convert("RGB")
    z = 1.04 + 0.05 * (u / d)  # aproximação lenta
    cw, ch = W / z, H / z
    return im.crop((int((W - cw) / 2), int((H - ch) / 2), int((W + cw) / 2), int((H + ch) / 2))).resize((W, H),
                                                                                                    Image.BICUBIC)


def alfa_txt(u, d):
    return min(1, max(0, (u - 0.35) / 0.5)) * min(1, max(0, (d - FUSAO - u) / 0.4))


@lru_cache(None)
def _faixa(h):
    y = np.linspace(-1, 1, h)
    al = (np.clip(1 - np.abs(y), 0, 1) ** 0.8 * 150).astype(np.uint8)
    im = Image.new("RGBA", (W, h), (20, 12, 8, 0))
    im.putalpha(Image.fromarray(np.repeat(al[:, None], W, 1)))
    return im


def faixa(img, yc, h, a):
    f = _faixa(h)
    if a < 1:
        f = f.copy()
        f.putalpha(f.getchannel("A").point(lambda v: int(v * a)))
    img.alpha_composite(f, (0, int(yc - h / 2)))


def textos(img, k, t):
    _, _, _, d, _, grande, peq = PLANOS[k]
    u = t - INI[k]
    a = alfa_txt(u, d)
    if a <= 0:
        return
    faixa(img, 950 if k == 0 else (1290 if peq else 1290), 560 if k == 0 else 440, a)
    sobe = (1 - min(1, max(0, (u - 0.35) / 0.8))) * 18
    if k == 0:
        escreve(img, (W / 2, 820 + sobe), "SUA VEZ  ×  BECA’S CAFÉ", fonte(F_REG, 34), CREME, a, track=6)
        escreve(img, (W / 2, 930 + sobe), grande, fonte(F_SERIF, 122), CREME, a)
        escreve(img, (W / 2, 1060 + sobe), peq, fonte(F_ITAL, 72), DOURADO, a)
        return
    y = 1240 if peq else 1290
    escreve(img, (W / 2, y + sobe), grande, fonte(F_SERIF, 84), CREME, a)
    if peq:
        escreve(img, (W / 2, y + 100 + sobe), peq, fonte(F_ITAL, 70), DOURADO, a)


@lru_cache(None)
def linha_fina(w):
    im = Image.new("RGBA", (w, 3), DOURADO + (200,))
    return im


def fim(img, t, modo):
    u = t - T_FIM
    def fa(t0, d=0.6):
        return min(1, max(0, (u - t0) / d))
    y = 450
    escreve(img, (W / 2, y), "SUA VEZ  ×  BECA’S CAFÉ", fonte(F_REG, 34), CREME, fa(0.2), track=6)
    escreve(img, (W / 2, y + 115), "Domingo de Jogos", fonte(F_SERIF, 118), CREME, fa(0.3))
    escreve(img, (W / 2, y + 235), "edição de fim de ano", fonte(F_ITAL, 70), DOURADO, fa(0.5))
    if fa(0.8) > 0:
        lw = int(360 * fa(0.8, 0.8))
        if lw > 2:
            img.alpha_composite(linha_fina(lw), (int(W / 2 - lw / 2), y + 320))
    linhas = [("domingo, 13 de dezembro", F_SERIF, 64, CREME),
              ("das 13h às 19h", F_ITAL, 60, CREME),
              ("Beca’s Café · Rua Sorocaba, 35 · Mauá", F_SERIF, 44, CREME),
              ("R$ 40 · R$ 25 viram consumação no café", F_SERIF, 44, CREME)]
    yy = y + 410
    for k, (txt, f, s, cor) in enumerate(linhas):
        escreve(img, (W / 2, yy), txt, fonte(f, s), cor, fa(1.0 + 0.25 * k))
        yy += s + 34
    escreve(img, (W / 2, yy + 30), "APENAS 30 VAGAS", fonte(F_SERIF, 54), DOURADO, fa(2.2), track=6)
    escreve(img, (W / 2, yy + 95), "vaga só com pagamento antecipado", fonte(F_ITAL, 52), CREME, fa(2.4))
    if modo == "stories":
        escreve(img, (W / 2, 1395), "garanta sua vaga aqui", fonte(F_ITAL, 62), DOURADO, fa(2.8))
        a = fa(3.0)
        if a > 0:
            d = ImageDraw.Draw(img)
            c = DOURADO + (int(255 * a),)
            yb = 1435 + 8 * math.sin(u * 4)
            d.line((W / 2, yb, W / 2, yb + 40), fill=c, width=4)
            d.line((W / 2 - 16, yb + 24, W / 2, yb + 42, W / 2 + 16, yb + 24), fill=c, width=4, joint="curve")
        escreve(img, (W / 2, 1720), f"ou pelo WhatsApp {TB.WHATS}", fonte(F_REG, 40), CREME, fa(3.0))
    else:
        escreve(img, (W / 2, 1400), f"reserve pelo WhatsApp {TB.WHATS}", fonte(F_SERIF, 52), CREME, fa(2.8))
        escreve(img, (W / 2, 1490), "comenta: com quem você viria?", fonte(F_ITAL, 54), DOURADO, fa(3.2))


def quadro(t, modo="reels"):
    if t >= T_FIM - FUSAO:
        nome, _, t0, d, vel = FUNDO_FIM
        u = max(0.0, t - (T_FIM - FUSAO))
        bg = K.quadro_clip(nome, t0, d, vel, u).convert("RGB").filter(ImageFilter.GaussianBlur(14))
        bg = Image.blend(bg, Image.new("RGB", (W, H), (28, 18, 12)), 0.55)
        base = tela(bg, t, 1.4)
        if t < T_FIM:  # fusão do último plano para o fundo final
            ult = tela(quadro_plano(len(PLANOS) - 1, t), t)
            textos(ult, len(PLANOS) - 1, t)
            base = Image.blend(ult, base, (t - (T_FIM - FUSAO)) / FUSAO)
        else:
            fim(base, t, modo)
        img = base
    else:
        k = max(i for i in range(len(PLANOS)) if INI[i] <= t)
        img = tela(quadro_plano(k, t), t)
        textos(img, k, t)
        fim_k = INI[k] + PLANOS[k][3] - FUSAO
        if k + 1 < len(PLANOS) and t >= fim_k:
            nxt = tela(quadro_plano(k + 1, t), t)
            textos(nxt, k + 1, t)
            img = Image.blend(img, nxt, (t - fim_k) / FUSAO)
    if t < T_FIM + 0.3:
        lg = K.logo(130)
        img.alpha_composite(lg, (W - lg.width - 40, 50))
    else:
        lg = K.logo(200)
        img.alpha_composite(lg, (int(W / 2 - lg.width / 2), 210))
    if t < 0.5:
        img = Image.blend(Image.new("RGBA", (W, H), (0, 0, 0, 255)), img, t / 0.5)
    return img.convert("RGB")


def trechos():
    return [(p[0], p[2], p[3], p[4]) for p in PLANOS] + [FUNDO_FIM[:1] + FUNDO_FIM[2:]]


def audio(nome):
    ev = [(0.2, S.sino(), 0.25), (T_FIM, S.sino(), 0.3)]
    mus = S.musica_cafe(DUR + 0.5, bpm=80)
    n = len(mus)
    fade = int(1.6 * S.SR)
    mus[n - fade:] *= np.linspace(1, 0, fade)
    com = os.path.join(OUT, f"{nome}_com.wav")
    sem = os.path.join(OUT, f"{nome}_sem.wav")
    S.grava(com, DUR, ev, mus, musica_ganho=0.55, fx_ganho=0.5)
    S.grava(sem, DUR, ev, None, fx_ganho=0.5)
    return com, sem


def render_reels(fi):
    return quadro(fi / FPS, "reels").tobytes()


def render_stories(fi):
    return quadro(fi / FPS, "stories").tobytes()


def main():
    args = sys.argv[1:]
    modo = "stories" if "--stories" in args else "reels"
    K.prepara(trechos())
    if "--frame" in args:
        ts = [float(a) for a in args[args.index("--frame") + 1:] if not a.startswith("--")]
        ims = [quadro(t, modo) for t in ts]
        K.folha(ims, os.path.join(OUT, "frames_aesthetic.jpg"))
        print("DUR", DUR)
        return
    for m in ("reels", "stories"):
        com, sem = audio(f"aesthetic_{m}")
        K.entrega(f"aesthetic_{m}", DUR, render_reels if m == "reels" else render_stories, com, sem)
    print("ok", DUR)


if __name__ == "__main__":
    main()
