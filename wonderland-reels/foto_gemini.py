#!/usr/bin/env python3
"""Imagem inicial 9:16 pro Gemini (Veo) fazer o voo em 1ª pessoa do Wonderland's War (9/nov: eles não querem gravar).
Tudo OFICIAL da Galápagos (os originais da loja têm só 607 px: x4_02/x4_03 = ampliados 4x com ampliar_tab.py): tabuleiro retificado e ampliado (tabuleiro_x4) em perspectiva sobre uma mesa de madeira
escura + os standees da foto oficial (gal_WLW001_03 com a máscara standees_rembg) em pé no meio do tabuleiro.

    /usr/bin/python3 foto_gemini.py   → out/gemini/wonderland_9x16.png
"""
import os

import cv2
import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
O = os.path.join(ROOT, "assets", "orig")
W, H = 1440, 2560  # maior que o Reels: o Gemini recebe a imagem com mais detalhe
K = W / 1080


def mesa():
    y = np.linspace(0, 1, H)[:, None, None]
    x = np.linspace(0, 1, W)[None, :, None]
    base = np.array([58, 36, 26.0]) * (0.55 + 0.6 * y)
    rng = np.random.default_rng(2)
    veio = np.sin(x * 40 + np.sin(y * 7) * 3 + rng.normal(0, 0.02, (1, W, 1))) * 6
    a = np.clip(base + veio, 0, 255)
    # luz quente vindo de cima
    luz = np.exp(-(((x - 0.5) / 0.6) ** 2 + ((y - 0.25) / 0.5) ** 2)) * 40
    a = np.clip(a + luz * np.array([1.0, 0.75, 0.45]), 0, 255)
    return Image.fromarray(a.astype(np.uint8)).convert("RGBA")


def tabuleiro():
    t = cv2.imread(os.path.join(O, "tabuleiro_x4.jpg"))
    h, w = t.shape[:2]
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    dst = np.float32([[150, 330], [930, 330], [1240, 1980], [-160, 1980]])  # vista de quem está sentado à mesa
    M = cv2.getPerspectiveTransform(src, dst)
    rgba = cv2.cvtColor(t, cv2.COLOR_BGR2BGRA)
    out = cv2.warpPerspective(rgba, M, (W, H), flags=cv2.INTER_AREA, borderValue=(0, 0, 0, 0))
    return Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGRA2RGBA))


def standees(larg):
    im = Image.open(os.path.join(O, "x4_03.png")).convert("RGB")  # original 607 px ampliado 4x (Real-ESRGAN)
    m = Image.open(os.path.join(O, "standees_rembg.png")).convert("L").resize(im.size, Image.LANCZOS)
    im.putalpha(m)
    im = im.crop(im.getbbox())
    return im.resize((larg, int(im.height * larg / im.width)), Image.LANCZOS)


def tabuleiro_foto():
    """Foto oficial do jogo montado (render da Galápagos, fundo branco → transparente)."""
    im = Image.open(os.path.join(O, "x4_02.png")).convert("RGB")
    a = np.asarray(im).astype(np.int16)
    bran = (a.min(2) > 238).astype(np.uint8)
    n, lab = cv2.connectedComponents(bran)
    borda = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    fundo = np.isin(lab, list(borda))
    al = (~fundo).astype(np.uint8) * 255
    im = im.convert("RGBA")
    im.putalpha(Image.fromarray(al).filter(ImageFilter.GaussianBlur(1)))
    im = im.crop(im.getbbox())
    k = 1.38 * W / im.width   # maior que a tela: o tabuleiro sai pelas bordas, o miolo fica grande
    return im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)


def main():
    img = mesa()
    tf = tabuleiro_foto()
    tb = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    tb.alpha_composite(tf, (int((W - tf.width) // 2 - 40 * K), int(1040 * K - tf.height // 2)))
    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sombra.putalpha(tb.getchannel("A").point(lambda v: int(v * 0.6)).filter(ImageFilter.GaussianBlur(25 * K)))
    img.alpha_composite(sombra, (0, int(18 * K)))
    img.alpha_composite(tb)
    s = standees(int(560 * K))
    x, y = int((W - s.width) // 2 + 30 * K), int(1010 * K - s.height)
    sh = Image.new("RGBA", s.size, (0, 0, 0, 0))
    sh.putalpha(s.getchannel("A").point(lambda v: int(v * 0.45)))
    sh = sh.resize((s.width, max(1, s.height // 6))).filter(ImageFilter.GaussianBlur(12 * K))
    img.alpha_composite(sh, (x + 20, y + s.height - sh.height // 2))
    img.alpha_composite(s, (x, y))
    os.makedirs(os.path.join(ROOT, "out", "gemini"), exist_ok=True)
    img.convert("RGB").save(os.path.join(ROOT, "out", "gemini", "wonderland_9x16.png"))
    img.convert("RGB").save(os.path.join(ROOT, "out", "gemini", "wonderland_9x16.jpg"), quality=92)


def personagens():
    """Opção B: só os standees oficiais (bem nítidos depois de ampliar) grandes, de perto, na mesa de madeira."""
    img = mesa()
    s = standees(int(W * 0.96))
    x, y = (W - s.width) // 2, int(H * 0.62) - s.height
    sh = Image.new("RGBA", s.size, (0, 0, 0, 0))
    sh.putalpha(s.getchannel("A").point(lambda v: int(v * 0.5)))
    sh = sh.resize((s.width, max(1, s.height // 7))).filter(ImageFilter.GaussianBlur(16 * K))
    img.alpha_composite(sh, (x + int(25 * K), y + s.height - sh.height // 2))
    img.alpha_composite(s, (x, y))
    img.convert("RGB").save(os.path.join(ROOT, "out", "gemini", "wonderland_personagens_9x16.png"))


if __name__ == "__main__":
    main()
    personagens()
