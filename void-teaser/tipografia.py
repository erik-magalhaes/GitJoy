"""Textos animados da versão SEM NARRAÇÃO: o roteiro inteiro escrito na tela, com fontes e posições variadas.

Cada item: (início, fim, texto, fonte, tamanho, cor, x, y, âncora, efeito, extra)
efeitos: fade, espaco (letras se juntando), digita (máquina de escrever), desliza, impacto, corte (lâmina), sobe
"""
import functools
import math
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, "assets", "fonts")
W, H = 1080, 1920

F = {
    "bebas": "BebasNeue-Regular.ttf",
    "cinzel": "Cinzel-VF.ttf",
    "corm": "Cormorant-Italic.ttf",
    "italiana": "Italiana.ttf",
    "josefin": "JosefinSans.ttf",
    "maquina": "SpecialElite-Regular.ttf",
    "orbitron": "Orbitron.ttf",
    "oswald": "Oswald-VF.ttf",
    "mono": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
}
BRANCO = (0.95, 0.94, 0.92)
VERMELHO = (0.85, 0.08, 0.08)
VERDE = (0.45, 0.95, 0.75)
CINZA = (0.75, 0.76, 0.78)

TIRO = 25.48
APAGA = 66.857

ITENS = [
    # abertura
    (0.8, 4.3, "Bem-vindo a", "corm", 76, BRANCO, 540, 300, "mm", "fade", {}),
    (1.1, 4.3, "LAS VEGAS", "bebas", 220, BRANCO, 540, 440, "mm", "espaco", {"de": 60}),
    (4.5, 7.4, "Além das luzes brilhantes", "josefin", 56, BRANCO, 80, 300, "lm", "desliza", {}),
    (5.2, 7.4, "e dos cassinos lotados,", "josefin", 56, CINZA, 80, 372, "lm", "desliza", {}),
    (7.5, 10.4, "um galpão abandonado", "maquina", 70, BRANCO, 540, 1260, "mm", "digita", {"cps": 14}),
    (10.5, 13.0, "esconde as operações\nde uma organização\nconhecida como", "maquina", 52, BRANCO, 80, 1180, "la", "digita", {"cps": 28}),
    (12.2, 14.2, "VOID", "cinzel", 320, (1.0, 1.0, 1.0), 540, 760, "mm", "espaco", {"de": 140, "pisca": True}),
    # Joseph West
    (14.4, 18.4, "JOSEPH WEST", "bebas", 200, BRANCO, 70, 1240, "lm", "desliza", {}),
    (15.0, 18.4, "o atirador mais letal da organização", "corm", 54, CINZA, 74, 1350, "lm", "fade", {}),
    (18.7, 22.0, "Uma vez que você entra em sua mira,", "corm", 58, BRANCO, 540, 300, "mm", "fade", {}),
    (20.0, 23.6, "não existe segunda chance.", "corm", 74, BRANCO, 540, 380, "mm", "sobe", {}),
    (23.8, 26.7, "ELE NUNCA", "bebas", 160, BRANCO, 540, 1140, "mm", "fade", {}),
    (TIRO, 26.7, "ERRA.", "bebas", 260, VERMELHO, 540, 1320, "mm", "impacto", {}),
    # Sebastián Ortiz
    (26.9, 30.0, "SEBASTIÁN ORTIZ", "orbitron", 76, VERDE, 70, 330, "lm", "digita", {"cps": 16, "cursor": True}),
    (27.9, 30.0, "> o hacker da equipe", "mono", 40, VERDE, 72, 410, "lm", "digita", {"cps": 22}),
    (30.3, 33.4, "Por trás de suas telas,", "mono", 50, BRANCO, 70, 1250, "lm", "digita", {"cps": 18, "cursor": True}),
    (33.5, 37.0, "nenhum sistema está seguro\ne nenhum segredo\npermanece escondido.", "mono", 50, BRANCO, 70, 1180, "la", "digita", {"cps": 26, "cursor": True, "falha": True}),
    # Hailey Zhang
    (37.3, 41.0, "Hailey Zhang", "italiana", 130, BRANCO, 540, 330, "mm", "espaco", {"de": 30}),
    (38.0, 41.0, "a estrategista", "corm", 66, CINZA, 540, 450, "mm", "fade", {}),
    (41.3, 43.6, "Com uma adaga nas mãos,", "corm", 70, BRANCO, 540, 300, "mm", "fade", {}),
    (42.1, 43.6, "cada movimento é calculado", "corm", 56, BRANCO, 540, 390, "mm", "fade", {}),
    (43.7, 46.3, "E CADA GOLPE", "bebas", 140, BRANCO, 540, 1180, "mm", "corte", {}),
    (44.2, 46.3, "É PRECISO.", "bebas", 140, VERMELHO, 540, 1320, "mm", "corte", {}),
    # Hunter Ward
    (46.5, 50.6, "E HUNTER WARD?", "cinzel", 96, BRANCO, 540, 340, "mm", "fade", {"lento": True}),
    (48.6, 50.6, "Ele é o líder.", "corm", 72, CINZA, 540, 450, "mm", "sobe", {}),
    (50.9, 53.2, "O homem que comanda\ndas sombras.", "corm", 72, BRANCO, 80, 1220, "la", "fade", {"lento": True}),
    (53.3, 56.0, "Mas, quando entra em cena,", "corm", 70, BRANCO, 540, 330, "mm", "fade", {}),
    (55.2, 59.1, "QUALQUER COISA", "bebas", 150, BRANCO, 540, 1200, "mm", "fade", {}),
    (56.2, 59.1, "PODE SE TORNAR UMA ARMA.", "bebas", 104, VERMELHO, 540, 1330, "mm", "impacto", {}),
    # final
    (59.4, 63.0, "QUATRO ASSASSINOS.", "cinzel", 78, BRANCO, 540, 1420, "mm", "espaco", {"de": 24, "luz": True}),
    (60.9, 63.0, "UMA ORGANIZAÇÃO.", "cinzel", 58, BRANCO, 540, 1510, "mm", "fade", {"luz": True}),
    (63.3, APAGA, "E quatro histórias", "corm", 84, BRANCO, 540, 1400, "mm", "fade", {"luz": True, "corte_fim": True}),
    (64.0, APAGA, "esperando para serem contadas.", "corm", 64, BRANCO, 540, 1495, "mm", "fade", {"luz": True, "corte_fim": True}),
]


@functools.lru_cache(maxsize=64)
def fonte(nome, tam):
    p = F[nome] if F[nome].startswith("/") else os.path.join(FD, F[nome])
    f = ImageFont.truetype(p, tam)
    if nome in ("cinzel", "oswald"):
        try:
            f.set_variation_by_axes([600 if nome == "cinzel" else 500])
        except Exception:
            pass
    return f


@functools.lru_cache(maxsize=512)
def render_texto(texto, nome, tam, espaco=0):
    """Texto branco em máscara (float 0..1) + sombra; suporta várias linhas e espaçamento extra entre letras."""
    f = fonte(nome, tam)
    linhas = texto.split("\n")
    alt = int(tam * 1.18)
    larg = 0
    for l in linhas:
        w = sum(f.getlength(c) for c in l) + espaco * max(0, len(l) - 1)
        larg = max(larg, w)
    pad = int(tam * 0.5)
    im = Image.new("L", (int(larg) + 2 * pad, alt * len(linhas) + 2 * pad), 0)
    d = ImageDraw.Draw(im)
    for k, l in enumerate(linhas):
        x = pad
        for c in l:
            d.text((x, pad + k * alt), c, font=f, fill=255)
            x += f.getlength(c) + espaco
    a = np.asarray(im, np.float32) / 255
    return a, pad


def posiciona(img, mask, cor, x, y, ancora, pad, alpha, escala=1.0, dx=0.0, dy=0.0):
    if alpha <= 0.003:
        return img
    if escala != 1.0:
        mask = cv2.resize(mask, (max(1, int(mask.shape[1] * escala)), max(1, int(mask.shape[0] * escala))))
        pad = int(pad * escala)
    h, w = mask.shape
    tw, th = w - 2 * pad, h - 2 * pad
    if ancora[0] == "l":
        x0 = x - pad
    elif ancora[0] == "m":
        x0 = x - w / 2
    else:
        x0 = x - w + pad
    if ancora[1] == "a":
        y0 = y - pad
    else:
        y0 = y - h / 2
    x0, y0 = int(x0 + dx), int(y0 + dy)
    sx0, sy0 = max(0, x0), max(0, y0)
    sx1, sy1 = min(W, x0 + w), min(H, y0 + h)
    if sx1 <= sx0 or sy1 <= sy0:
        return img
    m = mask[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] * alpha
    sombra = cv2.GaussianBlur(mask, (0, 0), max(3, h / 18))[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] * alpha
    reg = img[sy0:sy1, sx0:sx1]
    reg *= (1 - 0.7 * np.clip(sombra * 1.6, 0, 1))[..., None]
    reg[:] = reg * (1 - m[..., None]) + m[..., None] * np.array(cor, np.float32)
    return img


def env(t, t0, t1, ent=0.35, sai=0.35):
    return max(0.0, min(1.0, (t - t0) / ent, (t1 - t) / sai))


def aplica(img, t, luz=1.0):
    for (t0, t1, txt, fn, tam, cor, x, y, anc, ef, ex) in ITENS:
        if not (t0 <= t < t1):
            continue
        k = (t - t0) / (t1 - t0)
        lento = ex.get("lento")
        a = env(t, t0, t1, 0.9 if lento else 0.3, 0.3)
        if ex.get("corte_fim"):
            a = min(1.0, (t - t0) / 0.5)
        if ex.get("luz"):
            a *= 0.35 + 0.65 * luz
        esc, dx, dy, esp = 1.0, 0.0, 0.0, 0
        texto = txt
        if ef == "espaco":
            de = ex.get("de", 40)
            esp = int(de * (1 - (1 - (1 - min(1, k * 1.4)) ** 3)))
            if ex.get("pisca"):
                a *= 1.0 if (int(t * 24) % 7) not in (2, 5) else 0.55
        elif ef == "digita":
            cps = ex.get("cps", 20)
            n = int((t - t0) * cps)
            texto = txt[:n]
            if ex.get("cursor") and (int(t * 3) % 2 == 0 or n < len(txt)):
                texto += "_"
            if not texto:
                continue
            a = min(1.0, (t1 - t) / 0.25)
            if ex.get("falha") and n >= len(txt) and int(t * 20) % 9 == 0:
                dx = 14
        elif ef == "desliza":
            dx = -160 * (1 - min(1, (t - t0) / 0.45)) ** 3
        elif ef == "sobe":
            dy = 40 * (1 - min(1, (t - t0) / 0.6)) ** 2
        elif ef == "impacto":
            u = (t - t0) / 0.14
            esc = 1.0 + 0.6 * max(0, 1 - u) ** 2
            a = min(1.0, u + 0.3, (t1 - t) / 0.25)
            if 0 < t - t0 < 0.35:
                s = (1 - (t - t0) / 0.35) * 12
                dx, dy = s * math.sin(t * 90), s * math.cos(t * 70)
        mask, pad = render_texto(texto, fn, tam, esp)
        if ef == "corte":  # revela da esquerda para a direita, em diagonal, com um risco vermelho
            u = min(1.0, (t - t0) / 0.28)
            hh, ww = mask.shape
            yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
            frente = u * (ww + hh * 0.4)
            mask = mask * np.clip((frente - (xx + (hh - yy) * 0.4)) / 12, 0, 1)
            if u < 1:
                risco = np.exp(-((xx + (hh - yy) * 0.4 - frente) / 3) ** 2) * (yy > hh * 0.15) * (yy < hh * 0.85)
                img = posiciona(img, risco.astype(np.float32), (1, 0.25, 0.2), x, y, anc, pad, a * 1.0)
        img = posiciona(img, mask, cor, x, y, anc, pad, a, esc, dx, dy)
    return img
