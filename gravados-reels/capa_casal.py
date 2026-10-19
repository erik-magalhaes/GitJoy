#!/usr/bin/env python3
"""Capa do Reels "Quanto a gente se conhece?" (casal.py), pedido da Jéssica em 19/out/2026: 1080x1920 com os dois.
Tudo que importa fica na área do meio que aparece na grade do perfil (y 285–1635).
  A "frente a frente": tela dividida na diagonal com os quadros inteiros, ela à esquerda e ele olhando de lado,
    desconfiado, PARA ela; VS no meio. (O recorte com rembg ficou com bordas retas onde o cabelo encosta na borda do quadro.)
  B "fotos": dois quadros do vídeo como fotos inclinadas, com o título entre elas.
Quadros escolhidos (mais nítidos pela variância do Laplaciano): jess 36,4 s (sorrisinho) e 49,8 s; erik 155,8 s (olhar de
lado) e 112,9 s (sorrisão).

    python3 capa_casal.py            # out/capa_casal_{A,B}.png + out/capa_casal_opcoes.jpg
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "comum"))
sys.path.insert(0, os.path.join(REPO, "listas-reels"))
from motor import logo_card, cola, ffmpeg  # noqa: E402
from base import texto  # noqa: E402

W, H = 1080, 1920
BR = os.path.join(ROOT, "brutos", "casal")
OUT = os.path.join(ROOT, "out")
MARROM, AMARELO, BRANCO = (63, 36, 18), (255, 199, 31), (250, 250, 250)
ROSA, AZUL = (219, 39, 119), (37, 99, 235)


def quadro(src, t):
    r = subprocess.run([ffmpeg(), "-v", "error", "-ss", f"{t:.2f}", "-i", os.path.join(BR, src + ".mp4"), "-frames:v", "1",
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True)
    return Image.fromarray(np.frombuffer(r.stdout, np.uint8).reshape(1920, 1080, 3).copy())


def titulo(txt, s, cor=BRANCO, entre=1.0):
    return texto(txt, "lilita", s, cor, MARROM, max(7, s // 10), max(6, s // 12), MARROM, entre=entre)


def pilula(txt, s, cor, fg=BRANCO):
    tx = texto(txt, "lilita", s, fg)
    im = Image.new("RGBA", (tx.width + 50, tx.height + 14), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((9, 9, im.width - 1, im.height - 1), radius=im.height // 2, fill=MARROM)
    d.rounded_rectangle((0, 0, im.width - 10, im.height - 10), radius=im.height // 2, fill=cor, outline=MARROM, width=7)
    im.alpha_composite(tx, (20, 0))
    return im


def metade(src, t, cx_face, sc=1.0, dy=0):
    """Quadro inteiro do vídeo deslocado para o rosto ficar em x = cx_face (as sobras: o próprio quadro desfocado)."""
    im = quadro(src, t)
    if sc != 1.0:
        im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    fundo = im.resize((W, H)).filter(ImageFilter.GaussianBlur(30)).convert("RGBA")
    face = {"jess": 470, "erik": 520}[src] * sc  # x do rosto no quadro
    m = Image.new("L", im.size, 255)  # emenda suave em cima com o fundo desfocado
    ImageDraw.Draw(m).rectangle((0, 0, im.width, 0), fill=0)
    m = Image.fromarray(np.minimum(np.asarray(m), np.clip(np.arange(im.height)[:, None] / 120 * 255, 0, 255)
                                   .astype(np.uint8).repeat(im.width, 1)))
    fundo.paste(im, (int(cx_face - face), int(dy)), m)
    return fundo


def opcao_a():
    """Tela dividida na diagonal: ela à esquerda (sorrisinho), ele à direita olhando de lado PARA ela."""
    img = metade("jess", 36.4, 245, 1.0, 560)
    ele = metade("erik", 155.8, 835, 1.0, 520)
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([(700, 0), (W, 0), (W, H), (420, H)], fill=255)
    img.paste(ele, (0, 0), m)
    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))  # faixa escura no alto para o título
    ImageDraw.Draw(sombra).rectangle((0, 0, W, 700), fill=(20, 10, 5, 255))
    sombra.putalpha(Image.linear_gradient("L").resize((W, H)).point(lambda v: int(200 * max(0, 1 - v / 255 * 2.7))))
    img.alpha_composite(sombra)
    d = ImageDraw.Draw(img)
    d.line([(700, 0), (420, H)], fill=BRANCO, width=30)
    d.line([(700, 0), (420, H)], fill=MARROM, width=10)
    cola(img, titulo("QUANTO A GENTE\nSE CONHECE?", 122), W / 2, 430, rot=-3)
    cola(img, pilula("ELA", 64, ROSA), 170, 1340, rot=-6)
    cola(img, pilula("ELE", 64, AZUL), 930, 1340, rot=6)
    cola(img, titulo("VS", 150, AMARELO), 560, 1250, rot=-8)
    cola(img, pilula("SERÁ QUE A GENTE ACERTA?", 66, AMARELO, MARROM), W / 2, 1530, rot=-2)
    cola(img, logo_card(170), W - 130, 120)
    return img


def foto(src, t, w, h, cy=0.42):
    im = quadro(src, t)
    s = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    y0 = int(min(max(0, cy * im.height - h / 2), im.height - h))
    x0 = (im.width - w) // 2
    im = im.crop((x0, y0, x0 + w, y0 + h)).convert("RGBA")
    b = 22
    card = Image.new("RGBA", (w + 2 * b + 18, h + 2 * b + 18), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((18, 18, w + 2 * b + 17, h + 2 * b + 17), radius=34, fill=MARROM)
    d.rounded_rectangle((0, 0, w + 2 * b - 1, h + 2 * b - 1), radius=34, fill=BRANCO, outline=MARROM, width=8)
    mk = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mk).rounded_rectangle((0, 0, w - 1, h - 1), radius=18, fill=255)
    card.paste(im, (b, b), mk)
    return card


def opcao_b():
    img = Image.new("RGBA", (W, H), (227, 243, 246, 255))
    d = ImageDraw.Draw(img)
    for k in range(-H, W + H, 90):  # listras diagonais suaves (identidade da Jéssica: azul-claro)
        d.polygon([(k, 0), (k + 40, 0), (k + 40 - H, H), (k - H, H)], fill=(212, 236, 241))
    cola(img, foto("jess", 49.8, 600, 600, 0.30), 345, 600, rot=-6)
    cola(img, pilula("ELA", 60, ROSA), 150, 330, rot=-10)
    cola(img, foto("erik", 112.9, 600, 600, 0.27), 735, 1330, rot=5)
    cola(img, pilula("ELE", 60, AZUL), 960, 1060, rot=8)
    cola(img, titulo("QUANTO A GENTE\nSE CONHECE?", 112), W / 2, 975, rot=-2)
    cola(img, pilula("ACERTAMOS SÓ 1 DE 6?!", 58, AMARELO, MARROM), 330, 1580, rot=-3)
    cola(img, logo_card(170), W - 130, 120)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    ims = {"A": opcao_a(), "B": opcao_b()}
    for k, im in ims.items():
        im.convert("RGB").save(os.path.join(OUT, f"capa_casal_{k}.png"))
    sh = Image.new("RGB", (2 * 540 + 30, 960), (40, 40, 40))
    for i, k in enumerate("AB"):
        p = ims[k].convert("RGB").resize((540, 960), Image.LANCZOS)
        d = ImageDraw.Draw(p)
        d.rectangle((0, 142, 539, 817), outline=(255, 255, 255), width=2)  # área que aparece na grade do perfil
        sh.paste(p, (i * 570, 0))
    sh.save(os.path.join(OUT, "capa_casal_opcoes.jpg"), quality=92)
    print("ok")


if __name__ == "__main__":
    main()
