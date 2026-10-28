#!/usr/bin/env python3
"""Cartas do FLIP 7: A VINGANÇA redesenhadas retas, no estilo das cartas do jogo (edição Grok, 28/out/2026).
As fotos oficiais da Grok (assets/orig/, fora do git) só mostram as cartas pequenas e em perspectiva, então as cartas são
redesenhadas: papel creme, contorno azul-marinho, número grande colorido com contorno (como nas cartas) e o nome do
número escrito embaixo (QUATRO, CINCO, ONZE...). Ações e modificadores com os nomes da caixa brasileira: VIRE QUATRO,
SÓ MAIS UMA, TROCA, ROUBO, DESCARTE, −2 a −10 e ÷2.

    python3 cartas.py      # out/cartas_teste.png
"""
import os
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
FT = os.path.join(ROOT, "assets", "fonts")
CREME, MARINHO = (246, 237, 214), (30, 42, 92)
NOMES = ["ZERO", "UM", "DOIS", "TRÊS", "QUATRO", "CINCO", "SEIS", "SETE", "OITO", "NOVE", "DEZ", "ONZE", "DOZE", "TREZE"]
COR = {0: (150, 150, 158), 1: (128, 108, 92), 2: (205, 162, 52), 3: (222, 118, 66), 4: (52, 158, 168),
       5: (104, 170, 78), 6: (222, 88, 112), 7: (236, 146, 36), 8: (112, 156, 214), 9: (196, 104, 178),
       10: (220, 76, 66), 11: (156, 128, 204), 12: (104, 126, 150), 13: (48, 86, 168)}
ACOES = {"VIRE QUATRO": (196, 214, 70), "SÓ MAIS UMA": (176, 150, 222), "TROCA": (82, 186, 190),
         "ROUBO": (250, 206, 70), "DESCARTE": (240, 140, 160)}
CW, CH = 300, 420


@lru_cache(None)
def fonte(nome, s):
    return ImageFont.truetype(os.path.join(FT, nome), int(s))


def _base(fundo=CREME, borda=MARINHO):
    im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, CW - 1, CH - 1), radius=24, fill=fundo, outline=borda, width=7)
    return im, d


def _numero(d, txt, cx, cy, s, cor, contorno=MARINHO):
    f = fonte("AlfaSlabOne-Regular.ttf", s)
    d.text((cx + 7, cy + 8), txt, font=f, fill=contorno, anchor="mm", stroke_width=max(4, s // 22), stroke_fill=contorno)
    d.text((cx, cy), txt, font=f, fill=cor, anchor="mm", stroke_width=max(4, s // 22), stroke_fill=contorno)


@lru_cache(None)
def numero(n, s=1.0):
    """Carta de número: número grande colorido, nome embaixo e o número pequeno nos cantos."""
    im, d = _base()
    cor = COR[n]
    d.rounded_rectangle((16, 16, CW - 17, CH - 17), radius=16, outline=cor, width=5)
    _numero(d, str(n), CW / 2, CH / 2 - 26, 190 if n < 10 else 150, cor)
    d.text((CW / 2, CH - 70), NOMES[n], font=fonte("Bungee-Regular.ttf", 34), fill=MARINHO, anchor="mm")
    for (x, y, r) in ((40, 44, 0), (CW - 40, CH - 44, 180)):
        t = Image.new("RGBA", (70, 50), (0, 0, 0, 0))
        ImageDraw.Draw(t).text((35, 25), str(n), font=fonte("AlfaSlabOne-Regular.ttf", 34 if n < 10 else 25), fill=cor,
                               anchor="mm",
                               stroke_width=2, stroke_fill=MARINHO)
        t = t.rotate(r)
        im.alpha_composite(t, (int(x - 35), int(y - 25)))
    return _esc(im, s)


@lru_cache(None)
def acao(nome, s=1.0):
    im, d = _base(ACOES[nome])
    d.rounded_rectangle((18, 18, CW - 19, CH - 19), radius=16, fill=CREME, outline=MARINHO, width=4)
    d.rectangle((18, 150, CW - 19, 270), fill=ACOES[nome])
    linhas = nome.split(" ") if len(nome) > 8 else [nome]
    if nome == "SÓ MAIS UMA":
        linhas = ["SÓ MAIS", "UMA"]
    tam = 50 if len(linhas) > 1 else 54
    while max(d.textlength(l, font=fonte("Bungee-Regular.ttf", tam)) for l in linhas) > CW - 50:
        tam -= 2
    f = fonte("Bungee-Regular.ttf", tam)
    for k, l in enumerate(linhas):
        d.text((CW / 2, 210 + (k - (len(linhas) - 1) / 2) * 56), l, font=f, fill=MARINHO, anchor="mm")
    d.text((CW / 2, 92), "AÇÃO", font=fonte("Bungee-Regular.ttf", 30), fill=MARINHO, anchor="mm")
    return _esc(im, s)


@lru_cache(None)
def modificador(txt, s=1.0):
    im, d = _base((228, 82, 62))
    d.rounded_rectangle((18, 18, CW - 19, CH - 19), radius=16, outline=CREME, width=4)
    _numero(d, txt, CW / 2, CH / 2 - 10, 150 if len(txt) < 3 else 124, CREME)
    return _esc(im, s)


@lru_cache(None)
def verso(s=1.0):
    """Verso: azul com o leque de cartas coloridas (como o logo da caixa) e 'FLIP 7'."""
    im, d = _base((40, 86, 168), MARINHO)
    d.rounded_rectangle((18, 18, CW - 19, CH - 19), radius=16, outline=CREME, width=4)
    import math
    cores = [(236, 104, 84), (246, 170, 60), (250, 214, 80), (104, 186, 140), (100, 176, 220), (176, 140, 214)]
    for k, c in enumerate(cores):
        a = math.radians(-60 + k * 24)
        cx, cy = CW / 2 + math.sin(a) * 60, 190 - math.cos(a) * 30
        leq = Image.new("RGBA", (80, 120), (0, 0, 0, 0))
        ImageDraw.Draw(leq).rounded_rectangle((0, 0, 79, 119), radius=10, fill=c, outline=MARINHO, width=4)
        leq = leq.rotate(-math.degrees(a), expand=True, resample=Image.BICUBIC)
        im.alpha_composite(leq, (int(cx - leq.width / 2), int(cy - leq.height / 2)))
    d.text((CW / 2, 310), "FLIP 7", font=fonte("Bungee-Regular.ttf", 66), fill=(252, 220, 80), anchor="mm",
           stroke_width=4, stroke_fill=MARINHO)
    return _esc(im, s)


def _esc(im, s):
    if abs(s - 1) < 1e-3:
        return im
    return im.resize((int(CW * s), int(CH * s)), Image.LANCZOS)


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    ims = [numero(n) for n in range(14)] + [acao(a) for a in ACOES] + [modificador(m) for m in ("-2", "-10", "÷2")] + [verso()]
    sh = Image.new("RGBA", (8 * 320, 3 * 440), (70, 70, 80, 255))
    for k, im in enumerate(ims):
        sh.alpha_composite(im, ((k % 8) * 320 + 10, (k // 8) * 440 + 10))
    sh.convert("RGB").save(os.path.join(ROOT, "out", "cartas_teste.png"))
    print("ok")
