#!/usr/bin/env python3
"""Wonderland's War em 1ª PESSOA com o vídeo DELES (8/nov, brutos/mesa.mp4, 32 s, câmera rente ao tabuleiro): "apaga o
fundo" → a sala (parede, cadeiras, sacola) vira o céu do País das Maravilhas (`mascara_mesa.py` separa tabuleiro + peças
em pé). Óculos de VR (lente, HUD, alvos), textos das regras na hora de cada peça, e no fim DESCONECTA: abre o olho e é a
mesma cena com a sala de verdade ("...ESSE JOGO É MUITO BOM!"), comenta e tela final (de `vr.py`).

    /usr/bin/python3 mascara_mesa.py                       (uma vez: out/mask_mesa)
    /usr/bin/python3 pov_mesa.py --frame 2 5 9 13 17 21 26 31 34 38
    /usr/bin/python3 pov_mesa.py            → out/alice_pov_{com_som,para_musica}_final.mp4
"""
import argparse
import json
import math
import os
import random
import subprocess
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import vr as V
from vr import W, H, FPS, CIANO, OURO, VERM, ease, texto, fnt, F_VT, cin, hud_font, painel, lente, glitch, marca
from motor import encode, folha, ffmpeg  # noqa: E402
from base import final_loudness  # noqa: E402
import sons as S  # noqa: E402

ROOT = V.ROOT
OUT = V.OUT
HD = os.path.join(OUT, "hd_mesa")
MK = os.path.join(OUT, "mask_mesa")
NQ = len(os.listdir(HD)) if os.path.isdir(HD) else 966
PAN = json.load(open(os.path.join(OUT, "pan_mesa.json"))) if os.path.exists(os.path.join(OUT, "pan_mesa.json")) else None
ROSA = (255, 150, 230)

# trechos do bruto (início, fim, velocidade) e o texto do HUD de cada um
TRECHOS = [
    (0.0, 4.6, 1.0, "apoiadores"),
    (4.6, 8.3, 1.0, "castelo"),
    (8.3, 13.4, 1.0, "alice"),
    (13.4, 16.4, 1.0, "gato"),
    (16.4, 19.2, 2.6, "voo"),
    (19.2, 22.3, 1.0, "trilha"),
    (22.3, 28.5, 1.35, "cha"),
    (28.5, 31.4, 1.0, "volta"),
]
T0 = 3.0                       # gancho
SEG = []
_t = T0
for a, b, v, k in TRECHOS:
    d = (b - a) / v
    SEG.append((_t, _t + d, a, v, k))
    _t += d
T_SAI = _t                     # desconectando
T_OLHO = T_SAI + 1.3           # abre o olho: a sala de verdade
REAL = (28.9, 32.1)            # trecho do bruto que vira o "mundo real"
T_COM = T_OLHO + (REAL[1] - REAL[0]) + 0.6
T_CTA = T_COM + 3.6
DUR = T_CTA + 5.0


def src_de(t):
    for t0, t1, a, v, k in SEG:
        if t < t1:
            return a + (t - t0) * v, k, t - t0
    t0, t1, a, v, k = SEG[-1]
    return a + (t1 - t0) * v - 0.01, k, t1 - t0


# ---------------------------------------------------------------- quadros do bruto
def quadro_hd(s):
    n = min(NQ, max(1, int(round(s * 30)) + 1))
    return Image.open(os.path.join(HD, "%04d.jpg" % n)).convert("RGB"), n


def mascara(n):
    """Média de 3 quadros (tira a cintilação do isnet), ampliada e com borda suave."""
    ms = []
    for k in (n - 1, n, n + 1):
        k = min(NQ, max(1, k))
        p = os.path.join(MK, "%04d.png" % k)
        if os.path.exists(p):
            ms.append(np.asarray(Image.open(p), np.float32))
    m = np.mean(ms, 0) if ms else np.full((640, 360), 255, np.float32)
    im = Image.fromarray(m.astype(np.uint8)).resize((W, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(3))
    return im


# ---------------------------------------------------------------- céu do País das Maravilhas
@lru_cache(None)
def ceu_base():
    y = np.linspace(0, 1, H)[:, None]
    top = np.array([22, 8, 48.0])
    meio = np.array([86, 32, 120.0])
    hor = np.array([210, 110, 190.0])
    c = np.where(y < 0.55, top + (meio - top) * (y / 0.55), meio + (hor - meio) * ((y - 0.55) / 0.45))
    a = np.broadcast_to(c[:, None, :], (H, W, 3)).astype(np.uint8)
    img = Image.fromarray(a).convert("RGBA")
    # o sorriso do Gato (capa oficial) bem grande e apagado no céu, como uma lua
    g = Image.open(os.path.join(V.ART, "gato.png")).convert("RGB")
    g = g.resize((1500, int(1500 * g.height / g.width)), Image.LANCZOS).filter(ImageFilter.GaussianBlur(5))
    m = Image.new("L", g.size, 0)
    ImageDraw.Draw(m).ellipse((120, 80, g.width - 120, g.height - 160), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(120)).point(lambda v: int(v * 0.42))
    g = g.convert("RGBA")
    g.putalpha(m)
    img.alpha_composite(g, ((W - g.width) // 2, -260))
    return img


@lru_cache(None)
def estrelas():
    rnd = random.Random(3)
    return [(rnd.uniform(0, 2 * W), rnd.uniform(0, H * 0.75), rnd.uniform(1.5, 4.5), rnd.uniform(0, 6.28),
             rnd.uniform(0.15, 0.6)) for _ in range(150)]


@lru_cache(None)
def carta_voa(n, alt):
    return V.carta(n, alt).filter(ImageFilter.GaussianBlur(2))


def ceu(t, pan):
    img = ceu_base().copy()
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for x, y, r, ph, prof in estrelas():
        xx = (x + pan * prof * 0.12) % (2 * W) - W / 2
        if not -10 < xx < W + 10:
            continue
        a = 0.5 + 0.5 * math.sin(t * 2.2 + ph)
        d.ellipse((xx - r, y - r, xx + r, y + r), fill=(255, 240, 255, int(90 + 160 * a)))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(0.8)))
    # cartas oficiais flutuando ao longe (Torre Vermelha, Morsa)
    for k, (n, alt, y0, prof) in enumerate((("torre", 260, 420, 0.25), ("morsa", 220, 700, 0.18),
                                           ("torre", 180, 250, 0.1))):
        c = carta_voa(n, alt).rotate(12 * math.sin(t * 0.6 + k * 2), expand=True, resample=Image.BICUBIC)
        x = (k * 620 + 180 + pan * prof * 0.12 + t * 25) % (W + 600) - 300
        y = y0 + 30 * math.sin(t * 0.8 + k)
        c.putalpha(c.getchannel("A").point(lambda v: int(v * 0.7)))
        img.alpha_composite(c, (int(x - c.width / 2), int(y - c.height / 2)))
    return img


def brilho_borda(m):
    """Luz rosa na linha do horizonte (onde o tabuleiro encontra o céu) e em volta das peças."""
    a = np.asarray(m, np.float32) / 255
    b = np.asarray(m.filter(ImageFilter.MinFilter(9)), np.float32) / 255
    borda = np.clip(a - b, 0, 1)
    g = Image.fromarray((borda * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(14))
    lay = Image.new("RGBA", (W, H), ROSA + (0,))
    lay.putalpha(g.point(lambda v: min(255, int(v * 1.6))))
    return lay


def grade(im):
    a = np.asarray(im, np.float32)
    lum = a.mean(2, keepdims=True)
    a = lum + (a - lum) * 1.12
    a = (a - 128) * 1.06 + 128
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def mundo(t, real=False, s=None):
    if s is None:
        s, _, _ = src_de(t)
    q, n = quadro_hd(s)
    if real:
        return q.convert("RGBA"), n
    q = grade(q)
    m = mascara(n)
    pan = PAN["dx"][min(len(PAN["dx"]) - 1, n - 1)] if PAN else 0
    img = ceu(t, pan)
    fg = q.convert("RGBA")
    fg.putalpha(m)
    img.alpha_composite(fg)
    img.alpha_composite(brilho_borda(m))
    return img, n


# ---------------------------------------------------------------- HUD de cada trecho
def alvo(img, cx, cy, w, h, u, cor=CIANO, nome=None):
    """Colchetes que travam no alvo (fecham de fora para dentro)."""
    k = 1.6 - 0.6 * ease(u / 0.35)
    w, h = w * k, h * k
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    c = cor + (230,)
    L = 60
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = cx + sx * w / 2, cy + sy * h / 2
            d.line((x, y, x - sx * L, y), fill=c, width=6)
            d.line((x, y, x, y - sy * L), fill=c, width=6)
    if nome and u > 0.35:
        f = fnt(F_VT, 50)
        tw = d.textlength(nome, font=f)
        y = max(360, cy - h / 2 - 50)
        d.rounded_rectangle((cx - tw / 2 - 18, y - 30, cx + tw / 2 + 18, y + 30), 10, fill=(10, 6, 24, 200),
                            outline=c, width=3)
        d.text((cx, y), nome, font=f, fill=c, anchor="mm")
    img.alpha_composite(lay)


OBJ = os.path.join(OUT, "obj_mesa")
LOWRES = os.path.join(OUT, "frames_mesa")


@lru_cache(None)
def pecas_q(n):
    """Peças em pé no quadro n (isnet, 360x640): [(área, x0, y0, x1, y1, cor)] da maior para a menor, em 1080x1920."""
    from scipy import ndimage
    p = os.path.join(OBJ, "%04d.png" % min(NQ, max(1, n)))
    if not os.path.exists(p):
        return []
    m = np.asarray(Image.open(p)) > 127
    f = np.asarray(Image.open(os.path.join(LOWRES, "%04d.jpg" % min(NQ, max(1, n)))).convert("RGB"), np.float32)
    lab, k = ndimage.label(m)
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        a = (lab[sl] == i).sum()
        if a < 60:
            continue
        r, g, b = [f[sl][..., j][lab[sl] == i].mean() for j in range(3)]
        cor = ROSA if r > b + 20 else CIANO
        out.append((a, sl[1].start * 3, sl[0].start * 3, sl[1].stop * 3, sl[0].stop * 3, cor))
    return sorted(out, reverse=True)


def pecas(n, quantas=1, cmin=0, cmax=W):
    """Caixas suavizadas (mediana de ±4 quadros) das maiores peças, da esquerda para a direita."""
    res = []
    for j in range(quantas):
        bs = []
        for q in range(n - 4, n + 5):
            ps = [p for p in pecas_q(q) if cmin <= (p[1] + p[3]) / 2 <= cmax]
            ps = sorted(ps[:quantas], key=lambda p: p[1])
            if len(ps) > j:
                bs.append(ps[j])
        if len(bs) >= 3:
            b = np.median(np.array([x[1:5] for x in bs]), 0)
            res.append((b, bs[len(bs) // 2][5]))
    return res


def mira(img, n, u, quantas, nome, cor=None, folga=1.15):
    for b, c in pecas(n, quantas):
        x0, y0, x1, y1 = b
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        alvo(img, cx, cy, (x1 - x0) * folga + 40, (y1 - y0) * folga + 40, u, cor or c, nome)


def hud_trecho(img, t, k, u, n):
    if k == "apoiadores":
        if u > 0.4:
            mira(img, n, u - 0.4, 2, "APOIADOR")
        painel(img, ["EU TÔ DENTRO DO TABULEIRO!", "cada meeple é um apoiador", "numa das 5 regiões"], 1250,
               alpha=ease((u - 0.8) / 0.3))
    elif k == "castelo":
        if u > 1.2:
            mira(img, n, u - 1.2, 1, "CASTELO", OURO)
        painel(img, ["GANHOU A GUERRA NA REGIÃO?", "constrói um castelo e faz pontos"], 1250,
               alpha=ease((u - 1.5) / 0.3), cor=OURO)
    elif k == "alice":
        if u > 1.0:
            mira(img, n, u - 1.0, 1, "LÍDER: ALICE", CIANO, 1.05)
        painel(img, ["VOCÊ É UM LÍDER", "e anda pela Festa do Chá", "juntando aliados"], 1300,
               alpha=ease((u - 1.8) / 0.3))
    elif k == "gato":
        mira(img, n, u, 1, "RIVAL: GATO", VERM, 1.05)
        if int(t * 4) % 2 == 0:
            texto(img, "INIMIGO À VISTA", fnt(F_VT, 64), (W / 2, 1330), VERM, stroke=3, scor=(20, 0, 0))
    elif k == "voo":
        texto(img, "> VOANDO PELO TABULEIRO...", fnt(F_VT, 60), (W / 2, 1300), CIANO, stroke=3, scor=(10, 0, 20))
    elif k == "trilha":
        if u > 0.6:
            mira(img, n, u - 0.6, 2, None)
        painel(img, ["A CORRIDA PELOS PONTOS", "3 rodadas: mais pontos vence"], 1300, alpha=ease((u - 1.0) / 0.3),
               cor=ROSA)
    elif k == "cha":
        painel(img, ["VISÃO DO ALTO", "a mesa da Festa do Chá:", "cada cadeira, uma carta"], 1300,
               alpha=ease((u - 0.4) / 0.3))
    elif k == "volta":
        if u > 1.0:
            mira(img, n, u - 1.0, 1, "ALICE", CIANO, 1.05)


def hud_vr(img, t, titulo):
    V.hud(img, t, titulo)


def vinheta(img):
    lay = vinheta_cache()
    img.alpha_composite(lay)


@lru_cache(None)
def vinheta_cache():
    y, x = np.mgrid[:H, :W]
    r = np.sqrt(((x - W / 2) / (W * 0.62)) ** 2 + ((y - H / 2) / (H * 0.6)) ** 2)
    a = np.clip((r - 0.7) / 0.5, 0, 1) * 150
    lay = np.zeros((H, W, 4), np.uint8)
    lay[..., 0:3] = (10, 4, 20)
    lay[..., 3] = a.astype(np.uint8)
    return Image.fromarray(lay)


TITULOS = {"apoiadores": "WONDERLAND'S WAR", "castelo": "REGIÃO CONQUISTADA", "alice": "LÍDER DETECTADO",
           "gato": "ALERTA", "voo": "MODO VOO", "trilha": "PLACAR", "cha": "MAPA", "volta": "WONDERLAND'S WAR"}


# ---------------------------------------------------------------- cenas
def cena_gancho(t):
    img, _ = mundo(T0, s=0.0)
    img = img.filter(ImageFilter.GaussianBlur(18 * (1 - ease((t - 1.6) / 1.4))))
    img.alpha_composite(Image.new("RGBA", (W, H), (5, 2, 10, int(170 * (1 - ease((t - 1.8) / 1.2))))))
    lente(img, ease(t / 0.9))
    hud_vr(img, t, "INICIANDO REALIDADE VIRTUAL")
    a = 1 - ease((t - 2.4) / 0.5)
    texto(img, "E SE VOCÊ\nENTRASSE\nDENTRO\nDO JOGO?", cin(112), (W / 2, 820), OURO, stroke=4, scor=(30, 10, 40),
          brilho=16, alpha=a)
    texto(img, V.digita("> carregando: WONDERLAND'S WAR...", t - 0.5, 30), fnt(F_VT, 50), (W / 2, 1330), CIANO,
          alpha=a)
    barra = ease((t - 0.5) / 2.0)
    if a > 0.05:
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((240, 1390, 840, 1416), 12, outline=CIANO + (int(200 * a),), width=3)
        d.rounded_rectangle((246, 1396, 246 + 588 * barra, 1410), 8, fill=CIANO + (int(230 * a),))
    marca(img)
    return img


def cena_mundo(t):
    s, k, u = src_de(t)
    img, n = mundo(t, s=s)
    if k == "voo":  # borrão de velocidade
        img = img.filter(ImageFilter.BoxBlur(3))
    # entrada de cada trecho: um "piscar" de interface
    if u < 0.12 and t > T0 + 0.1:
        img = glitch(img, 0.5 * (1 - u / 0.12), int(t * FPS))
    vinheta(img)
    hud_trecho(img, t, k, u, n)
    hud_vr(img, t, TITULOS[k])
    if t < T0 + 0.5:
        img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(200 * (1 - (t - T0) / 0.5)))))
    marca(img)
    return img


def cena_sai(t):
    if t < T_OLHO:
        u = (t - T_SAI) / (T_OLHO - T_SAI)
        s = TRECHOS[-1][1] - 0.01
        img, _ = mundo(t, s=min(s, src_de(t)[0]))
        img = glitch(img, 0.3 + 0.7 * u, int(t * FPS))
        lente(img, 1 - ease(u))
        texto(img, V.digita("> DESCONECTANDO...", t - T_SAI, 22), fnt(F_VT, 64), (W / 2, H / 2), CIANO)
        return img
    # abre o olho: a MESMA mesa, agora com a sala de verdade
    u = t - T_OLHO
    img, _ = mundo(t, real=True, s=REAL[0] + min(u, REAL[1] - REAL[0] - 0.02))
    foco = 1 - ease((u - 0.3) / 1.0)
    if foco > 0.02:
        img = img.filter(ImageFilter.GaussianBlur(18 * foco))
    abre = ease(u / 0.6) if u < 0.8 else (1 - math.sin(min(1, (u - 0.8) / 0.3) * math.pi) * 0.85)
    if u > 1.1:
        abre = 1
    hh = H * 0.62 * abre
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse((-W * 0.35, H / 2 - hh, W * 1.35, H / 2 + hh), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(60))
    preto = Image.new("RGBA", (W, H), (8, 4, 4, 255))
    preto.putalpha(Image.eval(m, lambda v: 255 - v))
    img.alpha_composite(preto)
    if u > 1.3:
        k = ease((u - 1.3) / 0.35)
        img.alpha_composite(Image.new("RGBA", (W, H), (20, 8, 4, int(70 * k))))
        texto(img, "“...ESSE JOGO É\nMUITO BOM!”", cin(100), (W / 2, 1380), (255, 240, 210), stroke=6,
              scor=(40, 20, 10), brilho=10, alpha=k)
    marca(img)
    return img


def frame(fi):
    t = fi / FPS
    if t < T0:
        img = cena_gancho(t)
    elif t < T_SAI:
        img = cena_mundo(t)
    elif t < T_COM:
        img = cena_sai(t)
    elif t < T_CTA:
        img = V.cena_comenta(V.T_COM + (t - T_COM))
    else:
        img = V.cena_cta(V.T_CTA + (t - T_CTA))
    return img.convert("RGB")


def render(fi):
    return frame(fi).tobytes()


# ---------------------------------------------------------------- som
def eventos():
    ev = [(0.05, V.boot(), 0.5), (0.6, S.estatica(0.4), 0.15), (T0 - 0.6, V.whoosh(1.0), 0.7), (T0, S.sino(), 0.4)]
    for t0, t1, a, v, k in SEG[1:]:
        ev.append((t0, S.estatica(0.15), 0.25))
    alvos = {"apoiadores": [0.4, 0.6], "castelo": [1.2], "alice": [1.2], "gato": [0.0], "trilha": [0.6], "volta": [1.0]}
    for t0, t1, a, v, k in SEG:
        for d in alvos.get(k, []):
            ev.append((t0 + d, S.bip(1760, 0.06), 0.35))
            ev.append((t0 + d + 0.3, S.bip(2200, 0.05), 0.3))
        if k == "voo":
            ev.append((t0, V.whoosh(t1 - t0 + 0.3), 0.8))
        if k == "gato":
            for j in range(4):
                ev.append((t0 + 0.25 * j, S.bip(660, 0.1), 0.3))
        if k == "trilha":
            ev.append((t0 + 1.0, S.plim(), 0.3))
    ev += [(T_SAI + 0.1, S.estatica(1.0), 0.4), (T_SAI + 0.3, V.desliga(), 0.8),
           (T_OLHO + 1.3, S.plim(), 0.4), (T_COM + 0.1, S.sopro(0.5), 0.3), (T_CTA, S.sino(), 0.4)]
    return ev


def audio():
    os.makedirs(OUT, exist_ok=True)
    SR = S.SR
    m = V.valsa(DUR)
    n = int(DUR * SR)
    tt = np.arange(n) / SR
    env = np.ones(n)
    env[(tt >= T_SAI) & (tt < T_OLHO + 1.0)] = 0.15
    env = np.convolve(env, np.ones(int(0.25 * SR)) / int(0.25 * SR), "same")
    m = m * env
    com, sem = os.path.join(OUT, "alice_com.wav"), os.path.join(OUT, "alice_sem.wav")
    S.grava(com, DUR, eventos(), m, musica_ganho=0.42, fx_ganho=0.8)
    S.grava(sem, DUR, eventos(), None, fx_ganho=0.8)
    return com, sem


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", nargs="*", type=float)
    a = ap.parse_args()
    if a.frame:
        folha([frame(int(t * FPS)) for t in a.frame], os.path.join(OUT, "frames_alice.jpg"))
        print("DUR", round(DUR, 2), "T_SAI", round(T_SAI, 2))
        return
    com, sem = audio()
    n = int(round(DUR * FPS))
    base = os.path.join(OUT, "alice_pov_com_som.mp4")
    encode(base, render, list(range(n)), com)
    semv = os.path.join(OUT, "alice_pov_para_musica.mp4")
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", base, "-i", sem, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", semv], check=True)
    for arq in (base, semv):
        final_loudness(arq, arq.replace(".mp4", "_final.mp4"))
    print("ok", DUR)


if __name__ == "__main__":
    main()
