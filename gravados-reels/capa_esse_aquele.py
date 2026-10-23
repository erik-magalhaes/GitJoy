#!/usr/bin/env python3
"""Capa do Reels "ESSE OU AQUELE? versão Jéssica" (esse_aquele.py), pedido de 23/out/2026: 1080x1920 com a foto dela e o
título; tudo na área que aparece na grade do perfil (y 285–1635).
Fundo nas cores do logo (laranja × azul-petróleo na diagonal, como a capa C do casal, que ela aprovou). Foto: quadro com
ela SORRINDO e OLHANDO PARA A CÂMERA, achado pela busca automática do FaceMesh (ver capa_casal.py; folha J1–J8 em
out/capa_ea_opcoes.jpg). Ela escolheu a J8 = 55,17 s (antes era a J4, 44,67 s, com o dedinho levantado). Nos cantos, as fotos do site de 2 jogos da
1ª rodada (Luxor × Wonderland's War), sem entregar o campeão.

    python3 capa_esse_aquele.py      # out/capa_esse_aquele.png
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
from capa_casal import titulo, pilula, raios, W, H, MARROM, BRANCO, LARANJA, PETROLEO  # noqa: E402

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


def capa():
    img = raios(LARANJA, (540, 960), 22, 0.14)
    azul = raios(PETROLEO, (540, 960), 22, 0.14)
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([(760, 0), (W, 0), (W, H), (320, H)], fill=255)
    img.paste(azul, (0, 0), m)
    cola(img, titulo("ESSE OU\nAQUELE?", 160, entre=0.95), W / 2, 450, rot=-3)
    cola(img, cartao_foto(600, 700), W / 2, 1060, rot=2)
    cola(img, foto_site("luxor", 250, borda=8, raio=22, sombra_a=0.45), 150, 1330, rot=-10)
    cola(img, foto_site("wonderland_s_war", 250, borda=8, raio=22, sombra_a=0.45), 930, 1330, rot=10)
    cola(img, pilula("VERSÃO JÉSSICA", 84, BRANCO, MARROM), W / 2, 1490, rot=-2)
    cola(img, logo_card(170), W - 130, 120)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    capa().convert("RGB").save(os.path.join(OUT, "capa_esse_aquele.png"))
    print("ok")


if __name__ == "__main__":
    main()
