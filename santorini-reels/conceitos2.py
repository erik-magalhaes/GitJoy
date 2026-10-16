#!/usr/bin/env python3
"""2ª rodada de visual (16/out/2026): ele escolheu o PÔR DO SOL, mas não gostou das peças desenhadas e pediu FOTOS do jogo.
Fotos oficiais da edição dele (Spin Master), da Zatu, em 4320 px (assets/orig/sm/, fora do git; recortes em assets/fotos/),
e o clipe que ELE gravou do jogo na mesa (byebye-reels/referencia/clipes/c3.mp4), com luz de fim de tarde por cima.

    python3 conceitos2.py      # out/conceitos2.jpg (3 quadros: gancho, regra, deuses)
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "comum"))
from motor import W, H, cola, sombra, pilula, logo_card, font, ffmpeg  # noqa: E402
from ilha import mar, ceu  # noqa: E402
from conceitos import txt  # noqa: E402

OUT = os.path.join(ROOT, "out")
FOTOS = os.path.join(ROOT, "assets", "fotos")
CLIPE = os.path.join(REPO, "byebye-reels", "referencia", "clipes", "c3.mp4")
DOURADO, VINHO = (255, 206, 90), (70, 30, 40)


def por_do_sol():
    img = ceu(W, H, ((255, 214, 150), (248, 140, 110), (120, 70, 140), (40, 30, 80)))
    d = ImageDraw.Draw(img)
    d.ellipse((W / 2 - 260, 640 - 260, W / 2 + 260, 640 + 260), fill=(255, 226, 150, 255))
    img = img.filter(ImageFilter.GaussianBlur(3))
    img.alpha_composite(mar(W, 820, (240, 150, 120), (40, 40, 100), seed=4), (0, H - 820))
    return img


def luz_quente(im, forca=0.35):
    """Banho de luz dourada de fim de tarde por cima da foto (multiplica + realce leve)."""
    rgb = im.convert("RGB")
    quente = Image.new("RGB", rgb.size, (255, 196, 140))
    a = np.asarray(rgb).astype(np.float32) * (np.asarray(quente).astype(np.float32) / 255)
    mix = np.asarray(rgb).astype(np.float32) * (1 - forca) + a * forca
    out = Image.fromarray(mix.clip(0, 255).astype(np.uint8))
    out = ImageEnhance.Contrast(out).enhance(1.05)
    if im.mode == "RGBA":
        out = out.convert("RGBA")
        out.putalpha(im.getchannel("A"))
    return out


def brilho(img, x, y, r, cor=(255, 220, 140), a=150):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).ellipse((x - r, y - r * 0.6, x + r, y + r * 0.6), fill=cor + (a,))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(r / 3)))


def quadro_1():
    """Gancho: o tabuleiro de verdade (foto oficial) boiando no mar ao pôr do sol."""
    img = por_do_sol()
    tab = Image.open(os.path.join(FOTOS, "zatu_2.png"))
    tab = tab.crop((0, 0, tab.width, int(tab.height * 0.50)))  # só a ilha (as cartas ficam para depois)
    a = np.asarray(tab.getchannel("A")).astype(np.float32)
    fade = np.clip((np.arange(tab.height) - tab.height * 0.70) / (tab.height * 0.22), 0, 1)[:, None]
    tab.putalpha(Image.fromarray((a * (1 - fade)).astype(np.uint8)))
    tab = luz_quente(tab.resize((1050, int(tab.height * 1050 / tab.width)), Image.LANCZOS))
    brilho(img, W / 2, 1060, 420, a=120)
    cola(img, sombra(tab, 30, (0, 30), 0.4), W / 2, 1040)
    cola(img, txt("CONSTRUA COMO\nUM MORTAL.", "cinzel", 86, (255, 240, 210), VINHO, 4), W / 2, 250)
    cola(img, txt("VENÇA COMO\nUM DEUS.", "cinzel", 110, DOURADO, VINHO, 5, 4), W / 2, 1570)
    img.alpha_composite(logo_card(150), (W - 180, 40))
    return img


def quadro_2():
    """Regra: o clipe que ELES gravaram, com luz dourada, e a regra escrita."""
    p = os.path.join(OUT, "_c3.png")
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-ss", "2.0", "-i", CLIPE, "-frames:v", "1", "-vf",
                    f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}", p], check=True)
    img = luz_quente(Image.open(p).convert("RGBA"), 0.45)
    v = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(v).rectangle((0, 0, W, 520), fill=(40, 20, 40, 150))
    img.alpha_composite(v.filter(ImageFilter.GaussianBlur(60)))
    cola(img, txt("SUBA NO MÁXIMO\n1 ANDAR POR VEZ", "cinzel", 84, DOURADO, VINHO, 5, 3), W / 2, 260)
    cola(img, pilula("DESCER PODE QUANTO QUISER", 40, (60, 30, 50), (255, 240, 210), (255, 240, 210)), W / 2, 1500)
    img.alpha_composite(logo_card(150), (W - 180, 40))
    return img


def quadro_3():
    """Deuses: as cartas de verdade (foto oficial) abertas em leque, iluminadas."""
    img = por_do_sol()
    tab = Image.open(os.path.join(FOTOS, "zatu_2.png"))
    cartas = tab.crop((0, int(tab.height * 0.47), tab.width, tab.height))
    al = np.asarray(cartas.getchannel("A")).astype(np.float32)
    corte = np.clip(np.arange(cartas.height) / (cartas.height * 0.16), 0, 1)[:, None]  # some o pé do penhasco
    cartas.putalpha(Image.fromarray((al * corte).astype(np.uint8)))
    cartas = luz_quente(cartas.resize((1040, int(cartas.height * 1040 / cartas.width)), Image.LANCZOS), 0.2)
    brilho(img, W / 2, 1000, 480, a=140)
    cola(img, sombra(cartas, 30, (0, 30), 0.45), W / 2, 1020)
    cola(img, txt("CADA DEUS\nQUEBRA UMA REGRA", "cinzel", 84, DOURADO, VINHO, 5, 3), W / 2, 260)
    cola(img, pilula("APOLO TROCA DE LUGAR COM O RIVAL", 38, (60, 30, 50), (255, 240, 210), (255, 240, 210)), W / 2, 1560)
    img.alpha_composite(logo_card(150), (W - 180, 40))
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    ops = [quadro_1(), quadro_2(), quadro_3()]
    nomes = ["GANCHO (foto oficial)", "REGRA (o clipe de vocês)", "DEUSES (foto oficial)"]
    folha = Image.new("RGB", (3 * 540 + 40, 960 + 90), (255, 255, 255))
    d = ImageDraw.Draw(folha)
    for k, im in enumerate(ops):
        folha.paste(im.convert("RGB").resize((540, 960), Image.LANCZOS), (10 + k * 550, 80))
        d.text((10 + k * 550 + 270, 40), nomes[k], font=font("Poppins-Black.ttf", 30), fill=(20, 20, 30), anchor="mm")
    folha.save(os.path.join(OUT, "conceitos2.jpg"), quality=90)
    print("ok")


if __name__ == "__main__":
    main()
