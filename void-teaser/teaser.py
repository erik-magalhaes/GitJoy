"""Teaser VOID (livros) — vertical 1080x1920, ~69 s, narração em português (voz sintetizada) e legendas em PT-BR.

Uso:
  python3 teaser.py --frame 3 20 40     -> out/frames.jpg (quadros de teste)
  python3 teaser.py                     -> out/void_teaser.mp4
Sem rostos, sem logos, sem texto além das legendas.
"""
import functools
import json
import math
import os
import subprocess
import sys
from multiprocessing import Pool

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from motor_void import (FPS, H, W, Galpao, acabamento, bloom, camera, cola_silhueta, gradua_foto,  # noqa: E402
                        nevoa, para_u8, ruido)
from falas import FALAS  # noqa: E402

OUT = os.path.join(HERE, "out")
A = os.path.join(HERE, "assets")
C = os.path.join(HERE, "cand")


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def lerp(a, b, x):
    return a + (b - a) * x


# ------------------------------------------------------------------ linha do tempo
VOZ_DIR = os.environ.get("VOZ_DIR", "voz")  # voz (grave), voz_h (homem, voz normal), voz_m (mulher)
DUR_FALA = []
for i in range(1, 9):
    p = os.path.join(HERE, VOZ_DIR, f"c_{i:02d}.wav")
    DUR_FALA.append(float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                                          "csv=p=0", p], capture_output=True, text=True).stdout or 1))
INICIO = [1.2, 4.1, 14.3, 26.8, 37.2, 46.4, 59.2, 63.3]
# tempos fixos (as imagens são as mesmas em todas as versões)
APAGA = 66.857  # todas as luzes apagam na última batida
DUR = APAGA + 2.3
TIRO = 25.48  # "Ele nunca erra." -> tiro
if VOZ_DIR != "voz":
    # a fala 3 termina colada no tiro e a fala 8 termina pouco antes do apagão
    INICIO[2] = TIRO - 0.12 - DUR_FALA[2]
    INICIO[7] = APAGA - 0.55 - DUR_FALA[7]

# cenas: (nome, início, fim)
CENAS = [
    ("vegas", 0.0, 4.4),
    ("aerea", 4.4, 8.2),
    ("fachada", 8.2, 14.2),
    ("pistola", 14.2, 19.6),
    ("estande", 19.6, 26.7),
    ("teclado", 26.7, 31.2),
    ("telas", 31.2, 37.0),
    ("adaga", 37.0, 41.0),
    ("estrategista", 41.0, 44.6),
    ("arremesso", 44.6, 46.3),
    ("lider", 46.3, 50.8),
    ("bancada", 50.8, 54.9),
    ("luvas", 54.9, 59.1),
    ("final", 59.1, DUR),
]


# ------------------------------------------------------------------ recursos
@functools.lru_cache(maxsize=None)
def foto(nome, des=0.5, gamma=1.2, frio=True):
    return gradua_foto(np.asarray(Image.open(os.path.join(C, nome)).convert("RGB")), des, gamma, frio)


@functools.lru_cache(maxsize=None)
def sil(nome, h, flip=False, largura=1.0):
    """Silhueta recortada (assets/sil_<nome>.png) com altura h px (do topo da cabeça à base da imagem)."""
    m = np.asarray(Image.open(os.path.join(A, f"sil_{nome}.png")).convert("L"), np.float32) / 255.0
    ys, xs = np.where(m > 0.5)
    m = m[ys.min():ys.max() + 1, max(0, xs.min() - 4):xs.max() + 5]
    if flip:
        m = m[:, ::-1]
    s = h / m.shape[0]
    m = cv2.resize(m, (max(2, int(m.shape[1] * s * largura)), int(h)), interpolation=cv2.INTER_AREA)
    m = np.clip((m - 0.5) * 2.5 + 0.5, 0, 1)
    return m


@functools.lru_cache(maxsize=None)
def galpao(chave):
    if chave == "central":
        return Galpao(cam=(0.0, 1.5, 0.0), horizonte=0.47)
    if chave == "final":
        return Galpao(cam=(0.0, 1.7, -2.0), horizonte=0.47, seed=5,
                      lampadas=[(sx * 4.5, 6.8, z, (k + (sx > 0)) % 3) for k, z in enumerate(range(4, 44, 6))
                                for sx in (-1, 1)] + [(0.0, 6.6, 8.5, 2)])
    if chave == "estande":
        return Galpao(cam=(0.0, 1.55, 0.0), largura=2.4, altura=3.2, fundo=24.0, horizonte=0.47, seed=8,
                      pilares=[(sx * 2.0, z) for z in range(4, 22, 3) for sx in (-1, 1)],
                      lampadas=[(0.0, 3.0, 22.5, 0), (0.0, 3.0, 9.0, 1), (0.0, 3.0, 15.0, 1)],
                      porta_fundo=False, cor_luz=(1.0, 0.93, 0.82))
    if chave == "escuro":
        return Galpao(cam=(0.0, 1.6, 0.0), horizonte=0.5, seed=11,
                      lampadas=[(0.0, 6.5, 20.0, 0), (-6, 6.8, 30, 1), (6, 6.8, 30, 1)])
    raise KeyError(chave)


def cor(r, g, b):
    return np.array([r, g, b], np.float32)


CARMIM = cor(0.55, 0.06, 0.07)


# ------------------------------------------------------------------ cenas
def c_vegas(t, d):
    img = foto("vegas_04.jpg", des=0.25, gamma=1.15, frio=False)
    k = t / d
    out = camera(img, zoom=lerp(1.08, 1.22, ease(k)), cx=0.60, cy=lerp(0.55, 0.62, k))
    out = cv2.GaussianBlur(out, (0, 0), 2.6)
    out = bloom(out * 1.15, 0.45, 45, 0.9)
    return out * min(1, t / 0.8)


def c_aerea(t, d):
    img = foto("vegas_08.jpg", des=0.35, gamma=1.2, frio=False)
    k = ease(t / d)
    out = camera(img, zoom=lerp(1.35, 1.0, k), cx=lerp(0.45, 0.25, k), cy=lerp(0.55, 0.75, k))
    out = cv2.GaussianBlur(out, (0, 0), 2.4 + 2.5 * k)
    out = bloom(out, 0.45, 41, 0.8) * lerp(1.0, 0.35, k)
    if t < 0.5:  # entra a partir do strip com mistura
        out = out * (t / 0.5) + c_vegas(4.4, 4.4) * (1 - t / 0.5)
    return out


@functools.lru_cache(maxsize=1)
def fachada_base():
    """Fachada do galpão à noite (2400 px de altura para dar zoom)."""
    HW, HH = 1600, 2600
    y, x = np.mgrid[0:HH, 0:HW].astype(np.float32)
    ceu = np.stack([0.02 + 0.03 * (1 - y / HH), 0.025 + 0.02 * (1 - y / HH), 0.04 + 0.02 * (1 - y / HH)], -1)
    # brilho distante de Vegas no horizonte (laranja)
    ceu += np.exp(-((y - 1150) / 260) ** 2)[..., None] * cor(0.20, 0.09, 0.04) * (0.6 + 0.4 * np.exp(-((x - 1300) / 500) ** 2))[..., None]
    img = ceu.astype(np.float32)
    # prédio: parede corrugada
    top, base = 820, 1900
    parede = (y > top) & (y < base) & (x > 60) & (x < HW - 60)
    rib = 0.5 + 0.5 * np.sin(x * 2 * np.pi / 22)
    tex = ruido(HW, HH, 80, 4)
    ferr = ruido(HW, HH, 14, 9)
    pcol = (0.045 + 0.02 * rib + 0.03 * tex - 0.02 * ferr)[..., None] * cor(0.85, 0.9, 1.0)
    img = np.where(parede[..., None], pcol, img)
    # telhado inclinado
    tel = (y > top - 90 + 0.06 * np.abs(x - HW / 2)) & (y <= top) & (x > 40) & (x < HW - 40)
    img = np.where(tel[..., None], cor(0.03, 0.032, 0.038), img)
    # portas de metal duplas
    pl, pr, pt, pb = 520, 1080, 1180, 1900
    porta = (x > pl) & (x < pr) & (y > pt) & (y < pb)
    prib = 0.5 + 0.5 * np.sin(y * 2 * np.pi / 30)
    img = np.where(porta[..., None], (0.06 + 0.035 * prib + 0.03 * tex)[..., None] * cor(0.9, 0.93, 1.0), img)
    img = np.where((porta & (np.abs(x - (pl + pr) / 2) < 3))[..., None], 0.0, img)
    # chão molhado
    chao = y >= base
    asf = ruido(HW, HH, 10, 12)
    img = np.where(chao[..., None], (0.02 + 0.02 * asf)[..., None] * cor(0.9, 0.95, 1.0), img)
    # reflexo da parede no chão molhado
    refl = img[np.clip(2 * base - y, 0, HH - 1).astype(int), x.astype(int)] * 0.35
    img = np.where(chao[..., None], img + refl * (ruido(HW, HH, 30, 2) > 0.45)[..., None], img)
    return img.astype(np.float32), (pl, pr, pt, pb, base)


def c_fachada(t, d):
    img, (pl, pr, pt, pb, base) = fachada_base()
    img = img.copy()
    HH, HW = img.shape[:2]
    y, x = np.mgrid[0:HH, 0:HW].astype(np.float32)
    abre = ease((t - 3.4) / 1.6)
    # interior aceso aparecendo entre as portas
    if abre > 0:
        meio = (pl + pr) / 2
        larg = (pr - pl) / 2 * abre
        dentro = (np.abs(x - meio) < larg) & (y > pt) & (y < pb)
        luzin = (0.55 + 0.45 * np.exp(-((x - meio) / 200) ** 2)) * np.exp(-((y - 1500) / 600) ** 2)
        img = np.where(dentro[..., None], luzin[..., None] * cor(0.9, 0.85, 0.75) * 1.4, img)
        # luz saindo pelo chão
        img += (np.exp(-((x - meio) / (larg + 60)) ** 2) * np.exp(-((y - base) / 260) ** 2) * (y > base)
                * abre)[..., None] * cor(0.5, 0.45, 0.38)
    # lâmpada de vapor de sódio sobre a porta (pisca)
    lx, ly = (pl + pr) / 2, pt - 120
    pis = 1.0 if (int(t * 17) % 23) not in (3, 4, 11) else 0.25
    cone = np.exp(-((x - lx) / (40 + 0.55 * np.clip(y - ly, 0, None))) ** 2) * (y > ly) * np.exp(-(y - ly) / 900)
    img += (cone * 0.35 * pis)[..., None] * cor(1.0, 0.62, 0.3)
    img += (np.exp(-((x - lx) ** 2 + (y - ly) ** 2) / 900) * 3 * pis)[..., None] * cor(1, 0.7, 0.4)
    img += (np.exp(-((x - lx) ** 2 + (y - ly) ** 2) / 60000) * 0.25 * pis)[..., None] * cor(1, 0.6, 0.3)
    k = t / d
    z = lerp(1.0, 1.35, ease(k / 0.75)) * (1 + 4.0 * ease((t - 4.4) / 1.6))
    out = camera(img, zoom=z, cx=0.5, cy=lerp(0.6, 0.6, k))
    out += nevoa(t, 2, (30, -4))[..., None] * cor(0.05, 0.05, 0.06)
    out = bloom(out, 0.5, 51, 0.8)
    if t < 0.6:
        out = out * (t / 0.6)
    if t > d - 0.7:  # entra na luz
        w = ease((t - (d - 0.7)) / 0.7)
        out = out * (1 - w) + w * cor(0.75, 0.72, 0.68)
    return out


def c_pistola(t, d):
    img = foto("pistola_05.jpg", des=0.85, gamma=1.35)
    k = t / d
    out = camera(img, zoom=lerp(2.45, 2.7, ease(k)), cx=lerp(0.82, 0.84, k), cy=lerp(0.42, 0.40, k))
    out = out * 0.9
    # faixa de luz passando pelo aço
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    pos = lerp(-300, W + 300, ease((t - 0.8) / 3.2))
    faixa = np.exp(-((x - pos + 0.5 * (y - H / 2)) / 120) ** 2)
    lum = out.mean(axis=2, keepdims=True)
    out = out + faixa[..., None] * np.clip(lum - 0.08, 0, 1) * 2.2 * cor(0.95, 0.97, 1.0)
    out += nevoa(t, 3, (25, -10))[..., None] * cor(0.03, 0.03, 0.035)
    # entra da luz branca da porta
    if t < 0.5:
        w = 1 - t / 0.5
        out = out * (1 - w) + w * cor(0.75, 0.72, 0.68)
    return bloom(out, 0.6, 31, 0.5)


@functools.lru_cache(maxsize=1)
def alvo():
    """Alvo de papel (silhueta de treino + anéis), 300x460."""
    im = Image.new("RGB", (300, 460), (205, 200, 188))
    d = ImageDraw.Draw(im)
    d.ellipse([105, 40, 195, 140], fill=(25, 25, 28))
    d.polygon([(60, 150), (240, 150), (270, 460), (30, 460)], fill=(25, 25, 28))
    d.rectangle([125, 128, 175, 160], fill=(25, 25, 28))
    for r, c_ in ((44, (200, 196, 185)), (38, (25, 25, 28)), (26, (200, 196, 185)), (20, (25, 25, 28)), (8, (200, 196, 185))):
        d.ellipse([150 - r, 260 - r, 150 + r, 260 + r], outline=c_, width=3)
    for r in (36, 22):
        d.ellipse([150 - r, 90 - r * 0.6, 150 + r, 90 + r * 0.6], outline=(200, 196, 185), width=2)
    return np.asarray(im, np.float32) / 255.0


def c_estande(t, d):
    g = galpao("estande")
    ini = INICIO[2] - CENAS[4][1]
    tiro = TIRO - CENAS[4][1]
    nv = [0.25 + 0.05 * math.sin(t * 1.3), 1.0]
    # flash do tiro ilumina o corredor
    fl = math.exp(-max(0, t - tiro) / 0.06) if t >= tiro else 0
    img = g.quadro(nv)
    # alvo no fundo, iluminado
    a = alvo()
    sx, sy = g.proj(0, 1.45, 23.6)
    hpx = g.f * 1.1 / (23.6 - g.cam[2])
    aa = cv2.resize(a, (max(2, int(hpx * 300 / 460)), max(2, int(hpx))), interpolation=cv2.INTER_AREA)
    if t >= tiro:  # furo na cabeça
        hh, ww = aa.shape[:2]
        cv2.circle(aa, (ww // 2, int(hh * 90 / 460)), max(1, int(hh * 0.012)), (0.02, 0.02, 0.02), -1)
    x0, y0 = int(sx - aa.shape[1] / 2), int(sy - aa.shape[0] / 2)
    img[y0:y0 + aa.shape[0], x0:x0 + aa.shape[1]] = aa * 0.55
    img += nevoa(t, 4, (12, -3))[..., None] * cor(0.05, 0.05, 0.055)
    # câmera: avança lento atrás dele
    k = t / d
    hfig = lerp(1500, 1650, ease(k))
    m = sil("homem1", int(hfig))
    fx = W / 2 + 40
    fy = H + hfig * 0.36
    img = cola_silhueta(img, m, fx, fy, rim_cor=(0.95, 0.9, 0.82), rim=0.55, borda=5)
    # mão/arma: clarão na boca do cano (à frente, acima do ombro)
    if t >= tiro:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        bx, by = sx + 10, sy + 40
        f = math.exp(-(t - tiro) / 0.05)
        img += (np.exp(-((x - bx) ** 2 + (y - by) ** 2) / (3000 + 20000 * f)) * 6 * f)[..., None] * cor(1, 0.75, 0.4)
        img += fl * 0.35 * cor(1, 0.8, 0.55)
    # tremor no tiro
    if 0 <= t - tiro < 0.35:
        s = (1 - (t - tiro) / 0.35) * 14
        img = cv2.warpAffine(img, np.float32([[1, 0, s * math.sin(t * 90)], [0, 1, s * math.cos(t * 70)]]), (W, H),
                             borderMode=cv2.BORDER_REFLECT)
    z = lerp(1.0, 1.06, ease(k))
    img = camera(img, zoom=z, cx=0.5, cy=0.45)
    if t < 0.35:
        img = img * (t / 0.35)
    return bloom(img, 0.6, 41, 0.6)


# --------- hacker
@functools.lru_cache(maxsize=1)
def teclado_plano():
    """Teclado visto de cima (plano), 1800x700, com mapa das teclas."""
    TW, TH = 1800, 700
    im = np.full((TH, TW, 3), 0.015, np.float32)
    teclas = []
    linhas = [16, 15, 14, 13, 9]
    y = 60
    for li, n in enumerate(linhas):
        x = 60 + li * 22
        larg = (TW - 120 - li * 44) / n
        if li == 4:
            larg = (TW - 120) / 9
            x = 60
        for k in range(n):
            w = larg * (5 if (li == 4 and k == 4) else 1) if False else larg
            teclas.append((int(x + 7), int(y + 7), int(x + w - 7), int(y + 112)))
            x += w
        y += 122
    for (x0, y0, x1, y1) in teclas:
        im[y0:y1, x0:x1] = 0.05
        im[y0:y0 + 6, x0:x1] = 0.11  # borda de cima pega luz
    return im, teclas


def mao_mask(tw, th, cx, cy, s, dedos, lado):
    """Mão vista de trás/cima sobre o teclado: dorso largo, dedos grossos e curvados para baixo."""
    im = Image.new("L", (tw, th), 0)
    d = ImageDraw.Draw(im)
    # antebraço vindo de baixo
    d.polygon([(cx - 105 * s, cy + 120 * s), (cx + 105 * s, cy + 120 * s), (cx + 150 * s, th), (cx - 150 * s, th)], fill=255)
    # dorso da mão
    d.rounded_rectangle([cx - 125 * s, cy - 60 * s, cx + 125 * s, cy + 150 * s], radius=int(80 * s), fill=255)
    for i in range(4):
        fx = cx + (-84 + 56 * i) * s * lado
        comp = (95 - abs(i - 1.3) * 14) * s * (1 - 0.25 * dedos[i])
        r = 27 * s
        d.rounded_rectangle([fx - r, cy - 60 * s - comp, fx + r, cy - 20 * s], radius=int(r), fill=255)
    px = cx + 125 * s * lado
    d.line([(cx + 70 * s * lado, cy + 80 * s), (px + 10 * s * lado, cy + 5 * s)], fill=255, width=int(56 * s))
    d.ellipse([px - 28 * s + 10 * s * lado, cy - 23 * s, px + 28 * s + 10 * s * lado, cy + 33 * s], fill=255)
    a = np.asarray(im, np.float32) / 255
    return cv2.GaussianBlur(a, (0, 0), 3)


def c_teclado(t, d):
    base, teclas = teclado_plano()
    TH, TW = base.shape[:2]
    img = base.copy()
    rng = np.random.default_rng(int(t * 14))
    # teclas acesas (luz de fundo ciano/vermelha) conforme digita
    maos = [(600, 420, -1), (1200, 420, 1)]
    dedos_all = []
    for mi, (cx, cy, lado) in enumerate(maos):
        ds = []
        for i in range(4):
            ph = math.sin(t * (11 + i * 1.7 + mi * 2.3) + i * 1.9 + mi)
            ds.append(max(0, ph) ** 4)
        dedos_all.append(ds)
        for i, v in enumerate(ds):
            if v > 0.6:
                fx = cx + (-84 + 56 * i) * 1.0 * lado
                for (x0, y0, x1, y1) in teclas:
                    if x0 <= fx <= x1 and y0 <= cy - 150 <= y1 + 60:
                        img[y0:y1, x0:x1] += cor(0.10, 0.35, 0.42)
                        break
    # brilho da tela vindo de cima
    yy = np.linspace(0, 1, TH)[:, None, None]
    img += (1 - yy) ** 2 * cor(0.05, 0.12, 0.16)
    # mãos (pretas, com recorte azul da tela)
    for (cx, cy, lado), ds in zip(maos, dedos_all):
        m = mao_mask(TW, TH, cx + 6 * math.sin(t * 2 + lado), cy, 1.25, ds, lado)
        aro = np.clip(m - cv2.GaussianBlur(m, (0, 0), 7), 0, 1) * 2.0 * np.clip(1.4 - yy[..., 0] * 1.5, 0, 1)
        img = img * (1 - m[..., None]) + 0.01 * m[..., None] + aro[..., None] * cor(0.3, 0.75, 0.9)
    # perspectiva: teclado deitado, câmera baixa
    k = t / d
    src = np.float32([[0, 0], [TW, 0], [TW, TH], [0, TH]])
    esp = lerp(240, 200, k)
    dst = np.float32([[esp, 760], [W - esp, 760], [W + 520, H + 120], [-520, H + 120]])
    M = cv2.getPerspectiveTransform(src, dst)
    out = cv2.warpPerspective(img, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0))
    # monitores desfocados no alto
    telas = cv2.GaussianBlur(cv2.resize(telas_parede(t), (W, 760)), (0, 0), 16)
    out[:760] += telas * 0.7
    out += nevoa(t, 5, (10, -4))[..., None] * cor(0.02, 0.03, 0.035)
    out = camera(out, zoom=lerp(1.05, 1.12, ease(k)), cx=0.5, cy=0.55)
    if t < 0.3:
        out *= t / 0.3
    return bloom(out, 0.5, 31, 0.5)


def tela_conteudo(i, t, w, h):
    """Conteúdo abstrato de cada monitor (nada de letras)."""
    rng = np.random.default_rng(i * 7 + 1)
    im = np.zeros((h, w, 3), np.float32)
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    tipo = i % 9
    if tipo in (0, 4):  # câmera de vigilância
        src = foto("vegas_08.jpg") if tipo == 0 else fachada_base()[0]
        g = cv2.resize(src, (w, h)).mean(axis=2, keepdims=True)
        im = np.repeat(g, 3, 2) * cor(0.7, 1.0, 0.85) * 1.3
        im *= (0.85 + 0.15 * np.sin(y * 1.2))[..., None]
        im += np.random.default_rng(int(t * 24) + i).random((h, w, 1)).astype(np.float32) * 0.06
        if int(t * 2) % 2 == 0:
            cv2.circle(im, (14, 14), 5, (0.9, 0.1, 0.1), -1)
    elif tipo in (1, 6):  # linhas de "código" (barras)
        for k in range(14):
            yy = int((k * 16 - t * 60 * (1 + tipo % 2)) % (h + 20)) - 10
            xx = int(rng.integers(8, 40))
            ww = int(rng.integers(40, w - 40))
            c = cor(0.2, 0.75, 0.9) if rng.random() < 0.8 else cor(0.9, 0.2, 0.2)
            cv2.rectangle(im, (xx, yy), (min(w - 6, xx + ww), yy + 5), c.tolist(), -1)
    elif tipo == 2:  # mapa com alvo
        im[:] = cor(0.02, 0.05, 0.06)
        for k in range(0, w, 24):
            im[:, k] += 0.05
        for k in range(0, h, 24):
            im[k, :] += 0.05
        for _ in range(9):
            p = rng.integers(0, [w, h], 2)
            q = rng.integers(0, [w, h], 2)
            cv2.line(im, tuple(int(v) for v in p), tuple(int(v) for v in q), (0.1, 0.35, 0.4), 2)
        px, py = int(w * (0.3 + 0.4 * (t % 4) / 4)), int(h * 0.55)
        r = int(10 + 8 * ((t * 2) % 1))
        cv2.circle(im, (px, py), r, (0.9, 0.15, 0.15), 2)
        cv2.circle(im, (px, py), 3, (1, 0.2, 0.2), -1)
    elif tipo == 3:  # ficha confidencial (barras cinza = texto ilegível, tarja preta)
        im[:] = cor(0.55, 0.57, 0.6)
        cv2.rectangle(im, (10, 10), (int(w * 0.3), int(h * 0.45)), (0.25, 0.27, 0.3), -1)
        for k in range(8):
            yy = int(h * 0.12 + k * h * 0.1)
            x0 = int(w * 0.36) if k < 4 else 10
            cv2.rectangle(im, (x0, yy), (int(w * (0.6 + 0.3 * rng.random())), yy + 5), (0.3, 0.3, 0.33), -1)
        cv2.rectangle(im, (int(w * 0.36), int(h * 0.62)), (int(w * 0.92), int(h * 0.72)), (0.02, 0.02, 0.02), -1)
        im *= 0.75
    elif tipo == 5:  # alerta vermelho piscando com cadeado
        pis = 0.5 + 0.5 * math.sin(t * 7)
        im[:] = cor(0.25, 0.02, 0.03) * (0.5 + pis)
        cx, cy = w // 2, h // 2
        cv2.rectangle(im, (cx - 22, cy - 4), (cx + 22, cy + 30), (0.95, 0.9, 0.9), -1)
        cv2.ellipse(im, (cx, cy - 4), (15, 18), 0, 180, 360, (0.95, 0.9, 0.9), 5)
        cv2.rectangle(im, (6, 6), (w - 6, h - 6), (1, 0.2, 0.2), 3)
    elif tipo == 7:  # onda
        for k in range(3):
            pts = np.stack([x[0], h / 2 + (h * 0.3) * np.sin(x[0] / (18 + 9 * k) + t * (3 + k)) * np.sin(x[0] / 90 + k)], 1)
            cv2.polylines(im, [pts.astype(np.int32)], False, (0.2, 0.7 + 0.1 * k, 0.9), 2)
    elif tipo == 8:  # radar
        cx, cy = w // 2, h // 2
        r = min(w, h) // 2 - 8
        for rr in (r, r * 2 // 3, r // 3):
            cv2.circle(im, (cx, cy), rr, (0.1, 0.4, 0.35), 1)
        ang = t * 2.5
        ex, ey = int(cx + r * math.cos(ang)), int(cy + r * math.sin(ang))
        cv2.line(im, (cx, cy), (ex, ey), (0.3, 1, 0.8), 2)
        ang2 = np.arctan2(y - cy, x - cx)
        dif = (ang - ang2) % (2 * math.pi)
        im += (np.exp(-dif / 0.8) * ((x - cx) ** 2 + (y - cy) ** 2 < r * r))[..., None] * cor(0.05, 0.3, 0.22)
    return im


def telas_parede(t, cols=3, rows=3, tw=320, th=200, gap=18):
    Wp = cols * tw + (cols + 1) * gap
    Hp = rows * th + (rows + 1) * gap
    im = np.full((Hp, Wp, 3), 0.008, np.float32)
    for r in range(rows):
        for c in range(cols):
            i = r * cols + c
            x0 = gap + c * (tw + gap)
            y0 = gap + r * (th + gap)
            cont = tela_conteudo(i, t + i * 0.37, tw - 12, th - 12)
            # tremulação leve
            cont *= 0.9 + 0.1 * math.sin(t * 50 + i)
            im[y0:y0 + th, x0:x0 + tw] = 0.03
            im[y0 + 6:y0 + th - 6, x0 + 6:x0 + tw - 6] = cont
    return im


def c_telas(t, d):
    g = galpao("escuro")
    img = g.quadro([0.15, 0.2]) * 0.6
    k = t / d
    p = telas_parede(t)
    ph, pw = p.shape[:2]
    s = 1.0
    # parede de telas (levemente arqueada: 3 colunas giradas)
    tela = cv2.resize(p, (int(pw * 1.02), int(ph * 1.02)))
    x0 = (W - tela.shape[1]) // 2
    y0 = 430
    img[y0:y0 + tela.shape[0], x0:x0 + tela.shape[1]] = tela + img[y0:y0 + tela.shape[0], x0:x0 + tela.shape[1]] * 0.2
    # luz das telas na sala (azulada) + brilho
    glow = cv2.GaussianBlur(cv2.resize(p, (W // 8, H // 8)), (0, 0), 6)
    glow = cv2.resize(glow, (W, H))
    img += glow * 0.25
    # mesa
    img[1360:1400] = img[1360:1400] * 0.3 + cor(0.06, 0.12, 0.14)
    img[1400:] *= 0.25
    # hacker de costas (encapuzado, sentado)
    m = sil("homem2", 1240, largura=0.95)
    img = cola_silhueta(img, m, W / 2 + 10 + 4 * math.sin(t * 0.9), 1410 + 610, rim_cor=(0.3, 0.7, 0.9), rim=0.9, borda=6)
    img += nevoa(t, 6, (8, -5))[..., None] * cor(0.02, 0.035, 0.04)
    out = camera(img, zoom=lerp(1.18, 1.0, ease(k)), cx=0.5, cy=0.45)
    if t < 0.25:
        out *= t / 0.25
    if t > d - 0.3:
        out *= max(0, (d - t) / 0.3)
    return bloom(out, 0.5, 41, 0.6)


# --------- estrategista
def lamina_img(Lpx, Wpx, luz_ang, brilho_pos):
    """Adaga de dois gumes (horizontal, ponta à direita) com aço sombreado. Devolve (rgb, alpha)."""
    gw, gh = Lpx + 40, Wpx * 3
    y, x = np.mgrid[0:gh, 0:gw].astype(np.float32)
    cy = gh / 2
    cabo_fim = Lpx * 0.27
    # lâmina
    u = (x - cabo_fim) / (Lpx - cabo_fim)
    uc = np.clip(u, 0, 1)
    meia = Wpx / 2 * np.clip(1 - uc ** 1.8, 0, 1) * (u >= 0)
    v = (y - cy) / np.maximum(meia, 1e-3)
    blade = (np.abs(y - cy) < meia) & (u >= 0) & (u <= 1)
    # normal do bisel: dois planos + fio
    nx = np.where(v > 0, -0.6, 0.6)
    luz = np.array([math.cos(luz_ang), math.sin(luz_ang)])
    dif = 0.35 + 0.65 * np.clip(nx * luz[1] + 0.5, 0, 1)
    espec = np.exp(-((u - brilho_pos) / 0.05) ** 2) * (0.5 + 0.5 * (v * np.sign(luz[1]) < 0))
    fuller = np.exp(-(v / 0.12) ** 2) * (u < 0.7) * 0.4
    aco = (0.62 * dif - fuller * 0.25 + 0.18 * np.exp(-((uc - 0.35) / 0.4) ** 2))[..., None] * cor(0.75, 0.8, 0.88) + espec[..., None] * cor(1.6, 1.55, 1.5)
    # reflexo carmim no gume
    aco += (np.abs(v) > 0.82)[..., None] * cor(0.25, 0.03, 0.03) * dif[..., None]
    alpha = blade.astype(np.float32)
    rgb = aco * alpha[..., None]
    # guarda
    gx0, gx1 = cabo_fim - Wpx * 0.25, cabo_fim
    guard = (x > gx0) & (x < gx1) & (np.abs(y - cy) < Wpx * 1.05)
    rgb = np.where(guard[..., None], (0.25 + 0.4 * np.exp(-((y - cy + Wpx * 0.6) / (Wpx * 0.3)) ** 2))[..., None] * cor(0.8, 0.78, 0.72), rgb)
    alpha = np.maximum(alpha, guard.astype(np.float32))
    # cabo enrolado
    cabo = (x > 6) & (x < gx0) & (np.abs(y - cy) < Wpx * 0.32)
    tr = 0.5 + 0.5 * np.sin((x + (y - cy) * 0.8) * 2 * np.pi / (Wpx * 0.35))
    rgb = np.where(cabo[..., None], (0.05 + 0.07 * tr)[..., None] * cor(1, 0.85, 0.75), rgb)
    alpha = np.maximum(alpha, cabo.astype(np.float32))
    pom = (x - 10) ** 2 + (y - cy) ** 2 < (Wpx * 0.42) ** 2
    rgb = np.where(pom[..., None], cor(0.3, 0.3, 0.32), rgb)
    alpha = np.maximum(alpha, pom.astype(np.float32))
    alpha = cv2.GaussianBlur(alpha, (0, 0), 0.8)
    return rgb.astype(np.float32), alpha


def cola_rgba(img, rgb, a, cx, cy, ang, escala=1.0):
    h, w = a.shape
    M = cv2.getRotationMatrix2D((w / 2, h / 2), ang, escala)
    M[0, 2] += cx - w / 2
    M[1, 2] += cy - h / 2
    r = cv2.warpAffine(rgb, M, (W, H))
    al = cv2.warpAffine(a, M, (W, H))[..., None]
    return img * (1 - al) + r


@functools.lru_cache(maxsize=1)
def bokeh_fundo():
    rng = np.random.default_rng(21)
    im = np.zeros((H, W, 3), np.float32)
    for _ in range(26):
        x, y = rng.integers(0, W), rng.integers(0, H)
        r = int(rng.integers(30, 90))
        c = CARMIM * 1.3 if rng.random() < 0.6 else cor(0.25, 0.28, 0.32)
        cv2.circle(im, (int(x), int(y)), r, (c * rng.uniform(0.15, 0.45)).tolist(), -1)
    return cv2.GaussianBlur(im, (0, 0), 5)


def c_adaga(t, d):
    k = t / d
    img = bokeh_fundo() * 0.8 + cor(0.01, 0.01, 0.012)
    img = camera(img, zoom=1.1, cx=0.5 + 0.03 * k, cy=0.5)
    img += nevoa(t, 7, (20, -6))[..., None] * cor(0.03, 0.025, 0.028)
    rgb, a = lamina_img(1500, 130, 1.0 + t * 0.4, lerp(-0.1, 1.15, ease((t - 0.5) / 2.6)))
    img = cola_rgba(img, rgb, a, W / 2 + lerp(60, -40, k), H * 0.47, lerp(-58, -66, ease(k)), 0.95)
    # brilho estrela no fio quando o reflexo passa
    if 2.4 < t < 3.2:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        e = math.sin((t - 2.4) / 0.8 * math.pi)
        px, py = W / 2 + 230, H * 0.47 - 470
        star = (np.exp(-((x - px) / 220) ** 2 - ((y - py) / 3) ** 2) + np.exp(-((x - px) / 3) ** 2 - ((y - py) / 220) ** 2)
                + np.exp(-((x - px) ** 2 + (y - py) ** 2) / 300) * 2)
        img += (star * e * 1.2)[..., None] * cor(1, 0.97, 0.95)
    if t < 0.3:
        img *= t / 0.3
    return bloom(img, 0.55, 31, 0.6)


def c_estrategista(t, d):
    g = galpao("central")
    k = t / d
    img = g.quadro([1.0, 0.35 + 0.1 * math.sin(t * 3)])
    img += nevoa(t, 8, (14, -5))[..., None] * cor(0.05, 0.045, 0.05)
    hf = lerp(1120, 1180, ease(k))
    m = sil("mulher", int(hf)) if os.path.exists(os.path.join(A, "sil_mulher.png")) else sil("homem1", int(hf), largura=0.8)
    fx, fy = W / 2, 1290
    img = cola_silhueta(img, m, fx, fy, rim_cor=(0.95, 0.88, 0.82), rim=0.7, borda=5, some_base=0.3)
    # adagas nas mãos (pontas para baixo), girando de leve
    mh, mw = m.shape
    for s, fase in ((-1, 0.0), (1, 1.3)):
        rgb, a = lamina_img(520, 52, 0.5 + t * 2 + fase, (t * 0.7 + fase) % 1.4 - 0.2)
        hx = fx + s * mw * 0.40
        hy = fy - mh * 0.24
        ang = -90 + s * 6 + 6 * math.sin(t * 1.6 + fase)
        # a adaga gira pelo cabo: centro da imagem fica ~0.37 do comprimento abaixo da mão
        rad = math.radians(-ang)
        off = 520 * 0.5 - 520 * 0.16
        img = cola_rgba(img, rgb, a, hx + off * math.cos(rad), hy + off * math.sin(rad), ang, 1.0)
    out = camera(img, zoom=lerp(1.0, 1.05, k), cx=0.5, cy=0.5)
    if t < 0.25:
        out *= t / 0.25
    return bloom(out, 0.55, 41, 0.6)


@functools.lru_cache(maxsize=1)
def poste_madeira():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    veio = ruido(W, H, 30, 31)
    an = 0.5 + 0.5 * np.sin((x + 40 * veio * 6) / 9)
    poste = (np.abs(x - W * 0.62) < 230)
    base = np.where(poste[..., None], (0.08 + 0.05 * an + 0.03 * veio)[..., None] * cor(1.0, 0.72, 0.5),
                    cor(0.01, 0.01, 0.012) + bokeh_fundo() * 0.4)
    lado = np.exp(-((x - (W * 0.62 - 230)) / 30) ** 2) * poste
    return (base + lado[..., None] * cor(0.15, 0.12, 0.1)).astype(np.float32)


def c_arremesso(t, d):
    img = poste_madeira().copy()
    crav = 0.42
    alvo_x, alvo_y = W * 0.62 - 60, H * 0.45
    if t < crav:
        k = t / crav
        cx = lerp(-500, alvo_x - 300, k)
        cy = lerp(H * 0.42, alvo_y, k)
        rot = 0
        vib = 0
    else:
        cx, cy = alvo_x - 300, alvo_y
        vib = math.exp(-(t - crav) / 0.25) * math.sin((t - crav) * 70) * 4
    rgb, a = lamina_img(900, 90, 0.8, (t * 1.3) % 1.3)
    # ponta enterrada: corta a parte que entrou na madeira (máscara em x)
    img = cola_rgba(img, rgb, a, cx, cy, vib, 1.0)
    if t >= crav:
        f = math.exp(-(t - crav) / 0.08)
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        img += (np.exp(-((x - alvo_x) ** 2 + (y - alvo_y) ** 2) / 4000) * f * 1.5)[..., None] * cor(1, 0.9, 0.8)
        s = f * 10
        img = cv2.warpAffine(img, np.float32([[1, 0, s * math.sin(t * 80)], [0, 1, 0]]), (W, H), borderMode=cv2.BORDER_REFLECT)
    if t < crav:  # borrão de movimento
        img = cv2.blur(img, (31, 1))
    return bloom(img, 0.55, 31, 0.5)


# --------- líder
def c_lider(t, d):
    g = galpao("escuro")
    k = t / d
    luz = ease(t / 1.4)
    img = g.quadro([0.9 * luz, 0.25 * luz])
    img += nevoa(t, 9, (10, -4))[..., None] * cor(0.06, 0.06, 0.065) * (0.4 + 0.6 * luz)
    # ele vem andando do fundo, na direção da câmera (de frente, só silhueta preta)
    z = lerp(11.0, 3.9, ease(k * 1.05))
    hf = g.f * 1.9 / z
    sx, sy = g.proj(0.0, 0.0, z)
    passo = math.sin(t * 5.2)
    m = sil("lider", int(hf), flip=passo > 0, largura=1.05)
    # anda: balança leve
    fy = sy + hf * 0.0 + abs(passo) * hf * 0.008
    img = cola_silhueta(img, m, sx + passo * hf * 0.01, fy + hf * 0.02, rim_cor=(0.9, 0.86, 0.82), rim=0.5 * luz,
                        preto=0.008, borda=5, some_base=0.12)
    out = camera(img, zoom=1.0, cx=0.5, cy=0.5)
    return bloom(out, 0.55, 41, 0.6)


def ferramenta(nome, s):
    """Desenho de ferramenta (silhueta de metal) -> (rgb, alpha)."""
    w, h = int(700 * s), int(700 * s)
    m = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(m)
    tipo = Image.new("L", (w, h), 0)  # 0 madeira 120 aço escuro 255 aço claro
    td = ImageDraw.Draw(tipo)

    def P(pts):
        return [(x * s, y * s) for x, y in pts]
    if nome == "machado":
        md.rectangle(P([(330, 120), (370, 690)]), fill=255)
        td.rectangle(P([(330, 120), (370, 690)]), fill=60)
        cab = P([(250, 60), (380, 70), (390, 200), (330, 210), (230, 260), (200, 160), (215, 80)])
        md.polygon(cab, fill=255)
        td.polygon(cab, fill=200)
        td.polygon(P([(200, 160), (230, 260), (250, 240), (225, 150)]), fill=255)
    elif nome == "alicate":
        for sx in (-1, 1):
            cabo = P([(350 + sx * 20, 330), (350 + sx * 95, 650), (350 + sx * 60, 660), (350 + sx * 2, 340)])
            md.polygon(cabo, fill=255)
            td.polygon(cabo, fill=40 if sx > 0 else 30)
        boca = P([(320, 80), (380, 80), (395, 330), (305, 330)])
        md.polygon(boca, fill=255)
        td.polygon(boca, fill=210)
        md.ellipse(P([(318, 300), (382, 364)]), fill=255)
        td.ellipse(P([(330, 312), (370, 352)]), fill=255)
    elif nome == "chave":
        md.rectangle(P([(330, 180), (370, 650)]), fill=255)
        td.rectangle(P([(330, 180), (370, 650)]), fill=190)
        md.ellipse(P([(280, 60), (420, 200)]), fill=255)
        td.ellipse(P([(280, 60), (420, 200)]), fill=210)
        md.rectangle(P([(330, 50), (370, 120)]), fill=0)
        md.ellipse(P([(300, 600), (400, 690)]), fill=255)
        td.ellipse(P([(300, 600), (400, 690)]), fill=200)
        md.ellipse(P([(325, 620), (375, 670)]), fill=0)
    elif nome == "martelo":
        md.rectangle(P([(332, 160), (368, 680)]), fill=255)
        td.rectangle(P([(332, 160), (368, 680)]), fill=60)
        md.rectangle(P([(230, 90), (470, 170)]), fill=255)
        td.rectangle(P([(230, 90), (470, 170)]), fill=200)
    elif nome == "corrente":
        for i in range(9):
            y0 = 60 + i * 66
            if i % 2 == 0:
                md.ellipse(P([(320, y0), (380, y0 + 90)]), fill=255)
                md.ellipse(P([(336, y0 + 18), (364, y0 + 72)]), fill=0)
            else:
                md.rectangle(P([(342, y0), (358, y0 + 90)]), fill=255)
        td.rectangle([0, 0, w, h], fill=170)
    a = np.asarray(m, np.float32) / 255
    k = np.asarray(tipo, np.float32) / 255
    a = cv2.GaussianBlur(a, (0, 0), 0.9)
    y = np.linspace(0, 1, h)[:, None]
    madeira = cor(0.20, 0.11, 0.05)
    aco = cor(0.45, 0.48, 0.52)
    base = np.where((k < 0.3)[..., None], madeira * (0.6 + 0.4 * k[..., None] / 0.3),
                    aco * (k[..., None] * 0.9))
    # gradiente (luz vem de cima)
    rgb = base * (1.15 - 0.6 * y)[..., None]
    return (rgb * a[..., None]).astype(np.float32), a


def c_bancada(t, d):
    k = t / d
    # lâmpada balançando
    lx = W / 2 + 260 * math.sin(t * 1.7)
    ly = -80
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    dist = np.sqrt((x - lx) ** 2 + (y - ly) ** 2)
    luz = np.exp(-dist / 900)[..., None]
    # painel perfurado
    painel = (0.06 + 0.02 * ruido(W, H, 40, 41))[..., None] * cor(0.8, 0.8, 0.82)
    furos = ((x % 46) - 23) ** 2 + ((y % 46) - 23) ** 2 < 30
    painel = np.where(furos[..., None], 0.005, painel)
    img = painel * (0.25 + 1.6 * luz)
    # bancada
    img[1500:] = cor(0.07, 0.05, 0.035) * (0.4 + 1.2 * luz[1500:]) * (0.8 + 0.2 * ruido(W, H, 12, 44)[1500:, :, None])
    img[1495:1510] = cor(0.16, 0.12, 0.08) * (0.4 + 1.2 * luz[1495:1510])
    # ferramentas penduradas, com sombra projetada
    pos = [("machado", 180, 260, 1.15), ("alicate", 470, 380, 0.85), ("chave", 680, 360, 0.85),
           ("martelo", 880, 330, 0.8), ("corrente", 1010, 250, 0.9)]
    for nome, px, py, s in pos:
        rgb, a = ferramenta(nome, s)
        h, w = a.shape
        x0, y0 = int(px - w / 2), int(py)
        x1, y1 = min(W, x0 + w), min(1495, y0 + h)
        if x1 <= max(0, x0):
            continue
        sx0 = max(0, x0)
        sub = (slice(y0, y1), slice(sx0, x1))
        ac = a[: y1 - y0, sx0 - x0: x1 - x0]
        rc = rgb[: y1 - y0, sx0 - x0: x1 - x0]
        # sombra deslocada para longe da lâmpada
        vx = (px - lx) / 900 * 60
        vy = (py - ly) / 900 * 40
        Ms = np.float32([[1, 0, vx], [0, 1, vy]])
        sh = cv2.GaussianBlur(cv2.warpAffine(ac, Ms, (ac.shape[1], ac.shape[0])), (0, 0), 6)
        img[sub] *= (1 - 0.75 * sh[..., None])
        lz = luz[sub]
        espec = np.exp(-((np.arange(ac.shape[1])[None, :] + sx0 - lx) / 140) ** 2)[..., None] * 0.6
        img[sub] = img[sub] * (1 - ac[..., None]) + rc * (0.3 + 2.0 * lz) + (ac[..., None] * espec * lz * 1.5 * (rc.mean(2, keepdims=True) > 0.15))
    # lâmpada visível no alto
    img += (np.exp(-((x - lx) ** 2 + (y - 40) ** 2) / 2500) * 2.5)[..., None] * cor(1, 0.85, 0.6)
    img += nevoa(t, 10, (12, -5))[..., None] * cor(0.03, 0.03, 0.03)
    out = camera(img, zoom=lerp(1.12, 1.0, ease(k)), cx=lerp(0.42, 0.55, k), cy=0.5)
    if t < 0.25:
        out *= t / 0.25
    return bloom(out, 0.55, 41, 0.5)


def luva_mask(tw, th, cx, cy, s, fecha):
    """Mão de luva preta, dorso para a câmera, dedos para cima; fecha = 0 aberta .. 1 punho."""
    im = Image.new("L", (tw, th), 0)
    d = ImageDraw.Draw(im)
    d.polygon([(cx - 150 * s, cy + 160 * s), (cx + 150 * s, cy + 160 * s), (cx + 190 * s, th), (cx - 190 * s, th)], fill=255)
    d.rounded_rectangle([cx - 185 * s, cy - 120 * s, cx + 185 * s, cy + 230 * s], radius=int(110 * s), fill=255)
    for i in range(4):
        fx = cx + (-135 + 90 * i) * s
        comp = (250 - abs(i - 1.4) * 40) * s * (1 - 0.82 * fecha)
        r = 41 * s
        d.rounded_rectangle([fx - r, cy - 120 * s - comp, fx + r, cy - 40 * s], radius=int(r), fill=255)
    # polegar (de lado)
    ang = lerp(-0.6, -0.15, fecha)
    px, py = cx - 175 * s, cy + 120 * s
    ex, ey = px - 60 * s, py - 95 * s - 40 * s * fecha
    d.line([(px, py), (ex, ey)], fill=255, width=int(86 * s))
    d.ellipse([ex - 43 * s, ey - 43 * s, ex + 43 * s, ey + 43 * s], fill=255)
    a = np.asarray(im, np.float32) / 255
    return cv2.GaussianBlur(a, (0, 0), 2.5)


def c_luvas(t, d):
    k = t / d
    img = bokeh_fundo() * 0.35 + cor(0.008, 0.008, 0.01)
    img = camera(img, zoom=1.2, cx=0.45, cy=0.55)
    puxa = ease(t / 1.5)
    fecha = ease((t - 1.9) / 1.0)
    cy = H * 0.42 + (1 - puxa) * 140
    s = 1.35
    m = luva_mask(W, H, W * 0.52, cy, s, fecha)
    bl = cv2.GaussianBlur(m, (0, 0), 12)
    # recorte de luz só do lado de cima/direita (luz direcional)
    desl = cv2.warpAffine(m, np.float32([[1, 0, -10], [0, 1, 12]]), (W, H))
    aro = cv2.GaussianBlur(np.clip(m - desl, 0, 1), (0, 0), 2.5) * 1.0
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    cour = ruido(W, H, 5, 51) * 0.5 + 0.5
    # brilho do couro: nos nós dos dedos e no dorso (luz de cima à direita)
    nos = np.exp(-((y - (cy - 110 * s - 20 * fecha)) / 30) ** 2) * np.clip(bl - 0.6, 0, 1) * 1.6
    dorso = np.exp(-(((x - W * 0.6) / 160) ** 2 + ((y - (cy + 40 * s)) / 140) ** 2)) * np.clip(bl - 0.6, 0, 1)
    real = (nos + dorso * 0.8) * cour
    img = img * (1 - m[..., None]) + m[..., None] * 0.012
    img += aro[..., None] * cor(0.6, 0.12, 0.12) + real[..., None] * cor(0.32, 0.31, 0.31)
    # punho da luva sendo puxado: borda brilhante que desce pelo pulso
    yp = lerp(cy + 120 * s, cy + 330 * s, puxa)
    faixa = np.exp(-((y - yp) / 8) ** 2) * m
    img += faixa[..., None] * cor(0.35, 0.33, 0.33) * (1 - 0.6 * fecha)
    # dedos da outra mão puxando o punho (entram por baixo e saem)
    if t < 1.9:
        vis = 1 - ease((t - 1.4) / 0.5)
        for i in range(3):
            fx = W * 0.52 + (-60 + 60 * i) * s
            o = np.exp(-(((x - fx) / 26) ** 2 + ((y - (yp + 30)) / 70) ** 2) ** 1.5)
            o = np.clip(o * 3, 0, 1) * vis
            img = img * (1 - o[..., None]) + o[..., None] * 0.015
            img += np.clip(o - cv2.GaussianBlur(o, (0, 0), 6), 0, 1)[..., None] * cor(0.5, 0.1, 0.1)
    img += nevoa(t, 12, (14, -6))[..., None] * cor(0.025, 0.02, 0.022)
    out = camera(img, zoom=lerp(1.0, 1.08, ease(k)), cx=0.5, cy=0.48)
    if t < 0.25:
        out *= t / 0.25
    return bloom(out, 0.55, 31, 0.5)


# --------- final: os quatro
def piscar(t):
    """Nível de cada grupo de luz no final: pisca cada vez mais até apagar tudo em APAGA."""
    ta = t + CENAS[-1][1]
    if ta >= APAGA:
        return [0.0, 0.0, 0.0], 0.0
    falta = APAGA - ta
    rng = np.random.default_rng(int(ta * 15))
    intens = 1 - min(1, falta / 6.5)  # 0 = estável, 1 = muito instável
    nv = []
    for g in range(3):
        on = 1.0 if rng.random() > 0.55 * intens ** 1.3 else rng.uniform(0.0, 0.15)
        nv.append(on)
    flash = 1.0 if (falta < 2.2 and rng.random() < 0.35) else 0.0
    return nv, flash


def c_final(t, d):
    g = galpao("final")
    ta = t + CENAS[-1][1]
    if ta >= APAGA:
        return np.zeros((H, W, 3), np.float32)
    nv, flash = piscar(t)
    img = g.quadro(nv)
    img += nevoa(t, 13, (12, -4))[..., None] * cor(0.05, 0.05, 0.055) * (0.4 + 0.6 * max(nv))
    # névoa no chão (esconde as pernas)
    yy = np.linspace(0, 1, H)[:, None]
    chao = np.clip((yy - 0.62) / 0.2, 0, 1) ** 1.5
    nv_chao = nevoa(t * 1.5, 14, (25, -1))
    # os quatro de costas: 3 homens e 1 mulher (2ª da esquerda)
    alt = 600
    figs = [("homem1", 1.0, False, -372), ("mulher", 0.95, False, -124), ("homem2", 0.98, True, 122),
            ("lider", 1.08, True, 372)]
    for nome, larg, fl, dx in figs:
        if nome == "mulher" and not os.path.exists(os.path.join(A, "sil_mulher.png")):
            m = sil("homem2", int(alt * 0.93), fl, 0.78)
        else:
            hfig = alt * (0.93 if nome == "mulher" else 1.0)
            if nome == "lider":  # corpo inteiro: mesma escala do tronco dos outros
                hfig = alt * 1.62 * 0.98
            m = sil(nome, int(hfig), fl, larg)
        base_y = 1180 if nome != "lider" else 1180 + alt * 1.62 * 0.98 - alt * 0.98
        img = cola_silhueta(img, m, W / 2 + dx, base_y, rim_cor=(0.95, 0.9, 0.82), rim=0.65 * max(nv), borda=5, some_base=0.35 if nome != "lider" else 0.6)
    img += (chao[..., None] * (0.5 + 0.5 * nv_chao[..., None])) * cor(0.07, 0.07, 0.075) * (0.25 + 0.75 * max(nv))
    if flash:
        img += cor(0.25, 0.24, 0.22)
    k = t / max(0.1, APAGA - CENAS[-1][1])
    out = camera(img, zoom=lerp(1.32, 1.0, ease(k)), cx=0.5, cy=lerp(0.50, 0.50, k))
    if t < 0.4:
        out *= t / 0.4
    return bloom(out, 0.5, 51, 0.7)


FUNCS = {n: globals()["c_" + n] for n, *_ in CENAS}


# ------------------------------------------------------------------ legendas
FONTE = os.path.join(HERE, "..", "assinatura-reels", "assets", "fonts", "Figtree.ttf")


def pedacos(texto, max_c=44):
    """Quebra a fala em pedaços de no máx. 2 linhas, cortando em pontuação."""
    import re
    frases = re.split(r"(?<=[.?!,])\s+", texto)
    out, atual = [], ""
    for f in frases:
        cand = (atual + " " + f).strip()
        if len(cand) <= max_c * 2 - 6 and not atual.endswith((".", "?", "!")):
            atual = cand
        else:
            if atual:
                out.append(atual)
            atual = f
    if atual:
        out.append(atual)
    return out


def legendas():
    lst = []
    for i, txt in enumerate(FALAS):
        ps = pedacos(txt)
        tot = sum(len(p) for p in ps)
        t = INICIO[i]
        for p in ps:
            d = DUR_FALA[i] * len(p) / tot
            lst.append((t, t + d + (0.25 if p == ps[-1] else 0.05), p))
            t += d
    return lst


LEG = legendas()


@functools.lru_cache(maxsize=None)
def leg_img(txt):
    f = ImageFont.truetype(FONTE, 50)
    try:
        f.set_variation_by_axes([560])
    except Exception:
        pass
    pal = txt.split()
    linhas, at = [], ""
    for p in pal:
        c = (at + " " + p).strip()
        if f.getlength(c) > 900 and at:
            linhas.append(at)
            at = p
        else:
            at = c
    linhas.append(at)
    alt = 66
    im = Image.new("L", (W, alt * len(linhas) + 40), 0)
    d = ImageDraw.Draw(im)
    for k, l in enumerate(linhas):
        d.text((W / 2, 20 + alt * k + alt / 2), l, font=f, fill=255, anchor="mm")
    a = np.asarray(im, np.float32) / 255
    sombra = cv2.GaussianBlur(a, (0, 0), 6)
    return a, sombra


def aplica_legenda(img, t):
    ativos = [x for x in LEG if x[0] <= t < x[1]]
    for (t0, t1, txt) in ativos[-1:]:
        if True:
            a, s = leg_img(txt)
            op = min(1, (t - t0) / 0.12, (t1 - t) / 0.12)
            y0 = 1560 - a.shape[0] // 2
            reg = img[y0:y0 + a.shape[0]]
            reg *= (1 - 0.65 * s[..., None] * op)
            reg[:] = reg * (1 - a[..., None] * op) + a[..., None] * op * cor(0.95, 0.94, 0.92)
    return img


# ------------------------------------------------------------------ render
def quadro(t, com_legenda=True):
    for i, (n, t0, t1) in enumerate(CENAS):
        if t0 <= t < t1 or i == len(CENAS) - 1:
            img = FUNCS[n](t - t0, t1 - t0)
            break
    img = acabamento(img, 0.6)
    if com_legenda:
        img = aplica_legenda(img, t)
    return para_u8(img)


def _render(args):
    i0, i1, com = args
    return [quadro(i / FPS, com).tobytes() for i in range(i0, i1)]


def render(caminho, com=True):
    n = int(DUR * FPS)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-tune", "film",
                          "-pix_fmt", "yuv420p", caminho], stdin=subprocess.PIPE)
    blocos = [(i, min(n, i + 15), com) for i in range(0, n, 15)]
    with Pool(4) as pool:
        for k, b in enumerate(pool.imap(_render, blocos)):
            for fr in b:
                p.stdin.write(fr)
            if k % 10 == 0:
                print(f"{k * 15}/{n}", flush=True)
    p.stdin.close()
    p.wait()


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    if "--frame" in sys.argv:
        ts = [float(v) for v in sys.argv[sys.argv.index("--frame") + 1:]]
        ims = [Image.fromarray(quadro(t)).resize((360, 640)) for t in ts]
        fol = Image.new("RGB", (360 * min(6, len(ims)), 640 * ((len(ims) + 5) // 6)))
        for k, im in enumerate(ims):
            fol.paste(im, ((k % 6) * 360, (k // 6) * 640))
        fol.save(os.path.join(OUT, "frames.jpg"), quality=88)
    elif "--info" in sys.argv:
        print("DUR", DUR, "APAGA", APAGA, "TIRO", TIRO)
        for i in range(8):
            print(i + 1, INICIO[i], round(INICIO[i] + DUR_FALA[i], 2))
    else:
        render(os.path.join(OUT, "void_video.mp4"), True)
        render(os.path.join(OUT, "void_video_sem_legenda.mp4"), False)
