#!/usr/bin/env python3
"""Capa do Reels "ESSE OU AQUELE? versão Jéssica" (esse_aquele.py), pedido de 23/out/2026: 1080x1920 com a foto dela e o
título; tudo na área que aparece na grade do perfil (y 285–1635).
Fundo nas cores do logo (laranja × azul-petróleo). Ela pediu um fundo DIFERENTE dos outros (todas as capas estavam com a
diagonal com raios): 3 opções, xadrez de tabuleiro, bolinhas pop e trilha de casas. Foto: quadro com
ela SORRINDO e OLHANDO PARA A CÂMERA, achado pela busca automática do FaceMesh (ver capa_casal.py; folha J1–J8 em
out/capa_ea_opcoes.jpg). Ela escolheu a J8 = 55,17 s (antes era a J4, 44,67 s, com o dedinho levantado). Nos cantos, as fotos do site de 2 jogos da
1ª rodada (Luxor × Wonderland's War), sem entregar o campeão.

    python3 capa_esse_aquele.py      # out/capa_esse_aquele_{1_xadrez,2_bolinhas,3_trilha}.png + _fundos.jpg
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "comum"))
sys.path.insert(0, os.path.join(REPO, "listas-reels"))
from motor import logo_card, cola, ffmpeg  # noqa: E402
from base import foto as foto_site  # noqa: E402
from capa_casal import titulo, pilula, W, H, MARROM, BRANCO, LARANJA, PETROLEO  # noqa: E402

BRUTO = os.path.join(ROOT, "brutos", "out17", "20261017_133042.mp4")
OUT = os.path.join(ROOT, "out")
T_FOTO, NARIZ_Y = 55.17, 0.30  # nariz a ~30% da altura do quadro (o rosto fica no alto)


def quadro(t):
    r = subprocess.run([ffmpeg(), "-v", "error", "-ss", f"{t:.2f}", "-i", BRUTO, "-frames:v", "1", "-f", "rawvideo",
                        "-pix_fmt", "rgb24", "-"], capture_output=True)
    return Image.fromarray(np.frombuffer(r.stdout, np.uint8).reshape(1920, 1080, 3).copy())


def cartao_foto(w, h):
    im = quadro(T_FOTO)
    s = w / im.width * 1.15  # zoom leve no rosto
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    y0 = int(min(max(0, NARIZ_Y * im.height - h * 0.36), im.height - h))
    x0 = int((im.width - w) * 0.52)
    im = im.crop((x0, y0, x0 + w, y0 + h)).convert("RGBA")
    b = 22
    card = Image.new("RGBA", (w + 2 * b + 18, h + 2 * b + 18), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((18, 18, w + 2 * b + 17, h + 2 * b + 17), radius=36, fill=MARROM)
    d.rounded_rectangle((0, 0, w + 2 * b - 1, h + 2 * b - 1), radius=36, fill=BRANCO, outline=MARROM, width=8)
    mk = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mk).rounded_rectangle((0, 0, w - 1, h - 1), radius=20, fill=255)
    card.paste(im, (b, b), mk)
    return card


def mistura(a, b, u):
    return tuple(int(x + (y - x) * u) for x, y in zip(a, b))


def fundo_xadrez():
    """Tabuleiro: quadrados grandes laranja × petróleo girados, com as linhas mais claras."""
    lado = 240
    big = Image.new("RGBA", (2 * W, 2 * H), LARANJA + (255,))
    d = ImageDraw.Draw(big)
    for i in range(0, 2 * W // lado + 2):
        for j in range(0, 2 * H // lado + 2):
            if (i + j) % 2:
                d.rectangle((i * lado, j * lado, (i + 1) * lado - 1, (j + 1) * lado - 1), fill=PETROLEO)
    for i in range(0, 2 * W // lado + 2):  # fio claro entre as casas (cara de tabuleiro impresso)
        d.line((i * lado, 0, i * lado, 2 * H), fill=(255, 255, 255, 60), width=6)
    for j in range(0, 2 * H // lado + 2):
        d.line((0, j * lado, 2 * W, j * lado), fill=(255, 255, 255, 60), width=6)
    big = big.rotate(12, resample=Image.BICUBIC)
    return big.crop((W // 2, H // 2, W // 2 + W, H // 2 + H))


def fundo_bolinhas():
    """Pop: laranja com bolinhas petróleo que crescem para baixo e para os cantos (meio-tom)."""
    img = Image.new("RGBA", (W, H), LARANJA + (255,))
    d = ImageDraw.Draw(img)
    passo = 64
    for j in range(-1, H // passo + 2):
        for i in range(-1, W // passo + 2):
            x, y = i * passo + (passo / 2 if j % 2 else 0), j * passo
            u = min(1.0, (abs(x - W / 2) / (W / 2)) ** 1.5 * 0.55 + (max(0, y) / H) ** 1.6 * 0.75)
            r = 3 + 27 * u
            d.ellipse((x - r, y - r, x + r, y + r), fill=PETROLEO)
    return img


def fundo_trilha():
    """Trilha de tabuleiro: fundo petróleo e uma trilha de casas redondas laranja serpenteando atrás de tudo."""
    import math
    img = Image.new("RGBA", (W, H), PETROLEO + (255,))
    d = ImageDraw.Draw(img)
    for k in range(0, 40):  # listras finas mais escuras
        d.line((0, k * 60, W, k * 60 - 300), fill=mistura(PETROLEO, (10, 40, 60), 0.18), width=22)
    pts = []
    for k in range(150):
        t = k / 149
        pts.append((540 + 400 * math.sin(t * math.pi * 3.2 + 0.4), -80 + t * (H + 160)))
    casas, acc, ult = [], 0.0, pts[0]
    for p in pts[1:]:
        acc += math.dist(p, ult)
        ult = p
        if acc >= 150:
            casas.append(p)
            acc = 0
    for k, (x, y) in enumerate(casas):
        r = 58
        d.ellipse((x - r + 10, y - r + 12, x + r + 10, y + r + 12), fill=(14, 52, 64))
        cor = LARANJA if k % 3 else AMARELO_C
        d.ellipse((x - r, y - r, x + r, y + r), fill=cor, outline=MARROM, width=8)
    return img


AMARELO_C = (255, 199, 31)
FUNDOS = {"xadrez": fundo_xadrez, "bolinhas": fundo_bolinhas, "trilha": fundo_trilha}


def capa(fundo="xadrez"):
    img = FUNDOS[fundo]()
    cola(img, titulo("ESSE OU\nAQUELE?", 160, entre=0.95), W / 2, 450, rot=-3)
    cola(img, cartao_foto(600, 700), W / 2, 1060, rot=2)
    cola(img, foto_site("luxor", 250, borda=8, raio=22, sombra_a=0.45), 150, 1330, rot=-10)
    cola(img, foto_site("wonderland_s_war", 250, borda=8, raio=22, sombra_a=0.45), 930, 1330, rot=10)
    cola(img, pilula("VERSÃO JÉSSICA", 84, BRANCO, MARROM), W / 2, 1490, rot=-2)
    cola(img, logo_card(170), W - 130, 120)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    ims = []
    for k, nome in enumerate(FUNDOS, 1):
        im = capa(nome).convert("RGB")
        im.save(os.path.join(OUT, f"capa_esse_aquele_{k}_{nome}.png"))
        ims.append(im.resize((540, 960), Image.LANCZOS))
    sh = Image.new("RGB", (3 * 540 + 60, 960), (40, 40, 40))
    for k, im in enumerate(ims):
        sh.paste(im, (k * 570, 0))
    sh.save(os.path.join(OUT, "capa_esse_aquele_fundos.jpg"), quality=90)
    print("ok")


if __name__ == "__main__":
    main()
