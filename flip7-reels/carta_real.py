#!/usr/bin/env python3
"""Cartas do FLIP 7: A VINGANÇA no desenho REAL do jogo (28/out/2026; a 1ª tentativa, cartas.py, ficou "bem diferente
das cartas do jogo"). Referência: fotos oficiais da The Op (assets/orig/op/, fora do git): carta creme com moldura de
FITA amarela (linha dupla, pontas dobradas nos cantos), arco "FORCE SUA SORTE" no alto, LEQUE de faixas coloridas na
lateral, número VAZADO em contorno duplo (art déco) e o nome do número numa faixa embaixo.
A carta sai em CAMADAS (máscaras + cor), para cada estilo (papel recortado, giz, neon...) desenhar cada camada do seu jeito.

    python3 carta_real.py      # out/carta_real_teste.png
"""
import math
import os
from functools import lru_cache

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
FT = os.path.join(ROOT, "assets", "fonts")
CW, CH = 600, 840  # resolução de trabalho (2x) das camadas
CREME, MARINHO, FITA = (246, 238, 216), (40, 52, 120), (242, 194, 48)
NOMES = ["ZERO", "UM", "DOIS", "TRÊS", "QUATRO", "CINCO", "SEIS", "SETE", "OITO", "NOVE", "DEZ", "ONZE", "DOZE", "TREZE"]
COR = {0: (230, 84, 70), 1: (120, 98, 84), 2: (214, 166, 40), 3: (232, 116, 60), 4: (40, 160, 170), 5: (84, 170, 80),
       6: (220, 70, 120), 7: (240, 140, 30), 8: (90, 140, 220), 9: (190, 90, 180), 10: (220, 60, 60),
       11: (130, 120, 210), 12: (100, 120, 170), 13: (40, 90, 180)}
LEQUE = [(232, 70, 60), (246, 150, 50), (250, 210, 60), (90, 180, 110), (70, 160, 220), (150, 110, 210)]


@lru_cache(None)
def fonte(nome, s):
    return ImageFont.truetype(os.path.join(FT, nome), int(s))


def _mask(desenho):
    m = Image.new("L", (CW, CH), 0)
    desenho(ImageDraw.Draw(m))
    return np.asarray(m) > 127


def numero_vazado(txt, cx, cy, s, fonte_nome="Bungee-Regular.ttf", larg=0.62):
    """Máscaras do número vazado: contorno de fora, contorno de dentro e o miolo entre eles."""
    f = fonte(fonte_nome, s)
    big = Image.new("L", (CW * 2, CH), 0)
    ImageDraw.Draw(big).text((CW, cy), txt, font=f, fill=255, anchor="mm")
    a = np.asarray(big)
    ys, xs = np.nonzero(a > 127)
    w = xs.max() - xs.min()
    alvo = CW * larg if len(txt) == 1 else CW * 0.82
    esc = min(1.0, alvo / w)
    # estreita o número na horizontal (o do jogo é alto e fino)
    m = cv2.resize(a, (int(a.shape[1] * esc * 0.78), a.shape[0]), interpolation=cv2.INTER_AREA)
    out = np.zeros((CH, CW), np.uint8)
    x0 = int(cx - m.shape[1] / 2)
    sx0, dx0 = max(0, -x0), max(0, x0)
    larg_ = min(m.shape[1] - sx0, CW - dx0)
    out[:, dx0:dx0 + larg_] = m[:, sx0:sx0 + larg_]
    cheio = out > 127
    k = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))  # noqa: E731
    e1 = cv2.erode(cheio.astype(np.uint8), k(9)).astype(bool)
    e2 = cv2.erode(cheio.astype(np.uint8), k(17)).astype(bool)
    e3 = cv2.erode(cheio.astype(np.uint8), k(24)).astype(bool)
    return {"fora": cheio & ~e1, "miolo": e1 & ~e2, "dentro": e2 & ~e3, "cheio": cheio}


@lru_cache(None)
def camadas(n=None, tipo="numero", rotulo=None):
    """Lista de (nome, máscara bool CHxCW, cor) de baixo para cima."""
    L = []
    base = _mask(lambda d: d.rounded_rectangle((0, 0, CW - 1, CH - 1), radius=44, fill=255))
    cor_fundo = CREME if tipo != "azarado" else (214, 218, 224)
    L.append(("fundo", base, cor_fundo))
    # moldura de fita: linha dupla com recortes nos cantos e pontas dobradas
    def moldura(d, w):
        m = 46
        pts = [(m + 40, m), (CW - m - 40, m), (CW - m, m + 40), (CW - m, CH - m - 40), (CW - m - 40, CH - m),
               (m + 40, CH - m), (m, CH - m - 40), (m, m + 40)]
        d.line(pts + [pts[0]], fill=255, width=w, joint="curve")
    fora = _mask(lambda d: moldura(d, 22))
    vao = _mask(lambda d: moldura(d, 8))
    L.append(("fita", fora & ~vao, FITA))
    for (x, y, a) in ((46 + 20, 46 + 20, 45), (CW - 66, 66, -45), (66, CH - 66, -45), (CW - 66, CH - 66, 45)):
        dob = _mask(lambda d, x=x, y=y, a=a: d.polygon(
            [(x + 26 * math.cos(math.radians(a + t)), y + 26 * math.sin(math.radians(a + t))) for t in (0, 120, 240)],
            fill=255))
        L.append(("dobra", dob, (226, 168, 30)))
    # arco "FORCE SUA SORTE" no alto
    arco = Image.new("L", (CW, CH), 0)
    da = ImageDraw.Draw(arco)
    da.arc((CW / 2 - 150, 40, CW / 2 + 150, 220), 200, 340, fill=255, width=40)
    L.append(("arco", np.asarray(arco) > 127, FITA))
    txt = Image.new("L", (CW, CH), 0)
    frase = "FORCE SUA SORTE"
    for k, ch in enumerate(frase):  # letras seguindo o arco
        t = (k - (len(frase) - 1) / 2) / len(frase) * 2.1
        x, y = CW / 2 + 150 * math.sin(t), 130 - 90 * math.cos(t)
        g = Image.new("L", (40, 40), 0)
        ImageDraw.Draw(g).text((20, 20), ch, font=fonte("Bungee-Regular.ttf", 20), fill=255, anchor="mm")
        g = g.rotate(-math.degrees(t), resample=Image.BICUBIC)
        txt.paste(255, (int(x - 20), int(y - 20)), g)
    L.append(("arco_txt", np.asarray(txt) > 127, MARINHO))
    # leque de faixas coloridas na lateral direita (e à esquerda no 7 azarado, como no jogo)
    lados = (1, -1) if tipo == "azarado" else (1,)
    for lado in lados:
        cx = CW - 48 if lado > 0 else 48
        for k, c in enumerate(LEQUE):
            ang = 100 + k * 27  # abre para DENTRO da carta, saindo da moldura
            a0, a1 = (ang, ang + 25) if lado > 0 else (180 - ang - 25, 180 - ang)
            fa = _mask(lambda d, a0=a0, a1=a1, cx=cx: d.pieslice((cx - 95, 245, cx + 95, 435), a0, a1, fill=255))
            if tipo == "azarado":
                c = tuple(int(v * 0.4 + 140) for v in c[:1] * 3)
            dentro = _mask(lambda d: d.rectangle((60, 60, CW - 60, CH - 60), fill=255))  # o leque não sai da carta
            L.append(("leque", fa & dentro & ~_mask(lambda d, cx=cx: d.ellipse((cx - 40, 300, cx + 40, 380), fill=255)), c))
    # número vazado
    if n is not None:
        nv = numero_vazado(str(n), CW / 2 - 30, 410, 520)
        cor = COR[n] if tipo == "numero" else MARINHO
        L.append(("num_miolo", nv["miolo"], CREME if tipo == "numero" else (250, 250, 250)))
        L.append(("num_fora", nv["fora"], cor))
        L.append(("num_dentro", nv["dentro"], cor))
        if tipo in ("sortudo", "zero"):  # o 13 sortudo e o zero têm o miolo listrado de cores
            yy, xx = np.mgrid[0:CH, 0:CW]
            faixas = ((xx + yy) // 60) % len(LEQUE)
            for k, c in enumerate(LEQUE):
                L.append(("num_listra", nv["miolo"] & (faixas == k), c))
    # faixa com o nome
    nome = rotulo or (NOMES[n] if n is not None else "")
    fx = _mask(lambda d: d.rectangle((90, 650, CW - 90, 740), fill=255))
    fxi = _mask(lambda d: d.rectangle((100, 660, CW - 100, 730), fill=255))
    L.append(("faixa", fx & ~fxi, FITA))
    L.append(("faixa_fundo", fxi, CREME))
    nm = _mask(lambda d: d.text((CW / 2, 696), nome, font=fonte("Bungee-Regular.ttf", 52 if len(nome) < 8 else 40),
                                fill=255, anchor="mm"))
    L.append(("nome", nm, MARINHO))
    return L


def plana(camadas_, esc=0.5):
    """A carta 'normal' (sem estilo), só para conferir o desenho."""
    a = np.zeros((CH, CW, 4), np.uint8)
    for _nome, m, cor in camadas_:
        a[m] = cor + (255,)
    im = Image.fromarray(a)
    return im.resize((int(CW * esc), int(CH * esc)), Image.LANCZOS)


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    cs = [camadas(12), camadas(5), camadas(10), camadas(13, "sortudo", "SORTUDO"), camadas(7, "azarado", "AZARADO"),
          camadas(0, "zero", "O ZERO")]
    sh = Image.new("RGBA", (6 * 320, 440), (60, 60, 70, 255))
    for k, c in enumerate(cs):
        sh.alpha_composite(plana(c), (10 + k * 320, 10))
    sh.convert("RGB").save(os.path.join(ROOT, "out", "carta_real_teste.png"))
    print("ok")
