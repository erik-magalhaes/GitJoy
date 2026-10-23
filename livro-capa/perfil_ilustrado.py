#!/usr/bin/env python3
"""Foto de perfil ilustrada da autora E.M. Valentine (Instagram/TikTok), 1080x1080, tudo dentro do círculo.

Arte: "Girl with long brown hair, red dress", pintura de Carle J. Blenner (domínio público, Library of Congress,
via rawpixel), recortada no busto e ampliada 4x com Real-ESRGAN → assets/perfil/ruiva.png.
É uma pintura, não uma foto: funciona como a "cara" da marca sem fingir ser uma pessoa real.

    python3 perfil_ilustrado.py   → out/perfil/perfil_{a,b,c}.png + out/perfil/opcoes.jpg (com a máscara redonda)
        a = pintura no noir da capa (vinho → cobre), moldura dourada
        b = desenho a lápis de cor em papel creme
        c = ilustração pintada (pinceladas chapadas e contorno)
"""
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from divulgacao import CREME, brasas, fonte, fundo, texto, texto_ouro

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(AQUI, "out", "perfil")
W = H = 1080
# moldura do retrato: círculo no alto, nome embaixo (tudo dentro do círculo de 540 do perfil)
CX, CY, R = W // 2, 430, 330
ROSTO = (1108, 960)  # centro do rosto em assets/perfil/ruiva.png


def retrato(lado):
    """Quadrado lado x lado centrado um pouco abaixo do rosto (pega rosto, ombro e cabelo)."""
    im = Image.open(os.path.join(AQUI, "assets", "perfil", "ruiva.png")).convert("RGB")
    meia = 820
    cx, cy = ROSTO[0] + 90, ROSTO[1] + 360
    return im.crop((cx - meia, cy - meia, cx + meia, cy + meia)).resize((lado, lado), Image.LANCZOS)


def noir(im):
    """Mesmo gradiente da capa: preto → vinho → cobre → creme, com um pouco da cor original."""
    a = np.asarray(im).astype(np.float32) / 255
    lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
    pts = np.array([0, 0.12, 0.3, 0.55, 1.0])
    cores = np.array([[6, 2, 3], [40, 8, 12], [128, 36, 28], [222, 132, 84], [255, 228, 190]], np.float32) / 255
    l = np.clip((lum - 0.12) * 1.35, 0, 1)
    out = np.stack([np.interp(l, pts, cores[:, c]) for c in range(3)], -1)
    out = out * 0.7 + a * 0.3
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))


def traco(im):
    """Lápis de cor em papel creme (cv2.pencilSketch colorido), traço puxado para o vinho."""
    _, cor = cv2.pencilSketch(np.asarray(im), sigma_s=40, sigma_r=0.08, shade_factor=0.04)
    c = cor.astype(np.float32) / 255
    papel = np.array([246, 234, 216], np.float32) / 255
    # traço escuro vira vinho, papel branco vira creme
    tinta = 1 - c.mean(-1, keepdims=True)
    out = papel * c + np.array([0.35, 0.02, 0.08]) * tinta * 0.4
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))


def poster(im):
    """Ilustração pintada: cv2.stylization (pinceladas chapadas e contorno) com um pouco do noir da capa."""
    s = cv2.stylization(np.asarray(im), sigma_s=60, sigma_r=0.35).astype(np.float32)
    n = np.asarray(noir(im)).astype(np.float32)
    return Image.fromarray(np.clip(s * 0.7 + n * 0.3, 0, 255).astype(np.uint8))


def anel(img, cor_brilho=(230, 120, 60)):
    d = ImageDraw.Draw(img)
    for r, w, c in ((R + 22, 3, (164, 110, 44)), (R + 10, 7, (226, 176, 92)), (R + 3, 2, (255, 236, 178))):
        d.ellipse((CX - r, CY - r, CX + r, CY + r), outline=c, width=w)
    # 4 pontinhos vermelhos nos pontos cardeais do anel externo
    for ang in (0, 90, 180, 270):
        x = CX + (R + 22) * np.cos(np.radians(ang))
        y = CY + (R + 22) * np.sin(np.radians(ang))
        d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=(196, 30, 42))


def monta(arte, semente):
    img = fundo(W, H, semente=semente, luz=(0.5, 0.4))
    lado = 2 * R
    m = Image.new("L", (lado, lado))
    ImageDraw.Draw(m).ellipse((0, 0, lado - 1, lado - 1), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(1.2))
    # sombra do medalhão
    sh = Image.new("L", (W, H))
    ImageDraw.Draw(sh).ellipse((CX - R, CY - R + 14, CX + R, CY + R + 14), fill=220)
    img.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(26)))
    img.paste(arte, (CX - R, CY - R), m)
    anel(img)
    # nome: dentro do círculo do perfil (meia largura em y=860 ≈ 440 px)
    texto_ouro(img, (W / 2, 862), "E.M. VALENTINE", fonte("Cinzel.ttf", 74, 900), espaco=8)
    texto(img, (W / 2, 942), "ROMANCES QUE QUEIMAM", fonte("Cinzel.ttf", 26, 700), CREME, espaco=9, sombra=6)
    return img


def circulo(img):
    """Prévia como a rede mostra: recorte redondo sobre fundo cinza."""
    m = Image.new("L", img.size)
    ImageDraw.Draw(m).ellipse((0, 0, W - 1, H - 1), fill=255)
    out = Image.new("RGB", img.size, (238, 238, 238))
    out.paste(img, (0, 0), m)
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    base = retrato(2 * R)
    artes = {"a": noir(base), "b": traco(base), "c": poster(base)}
    prev = []
    for i, (k, arte) in enumerate(artes.items()):
        img = monta(arte, semente=21 + i)
        img.save(os.path.join(OUT, f"perfil_{k}.png"))
        prev.append(circulo(img).resize((520, 520), Image.LANCZOS))
    folha = Image.new("RGB", (3 * 520 + 4 * 30, 520 + 2 * 30 + 60), (238, 238, 238))
    d = ImageDraw.Draw(folha)
    for i, p in enumerate(prev):
        x = 30 + i * 550
        folha.paste(p, (x, 30))
        d.text((x + 260, 580), "ABC"[i], font=fonte("Cinzel.ttf", 44, 900), fill=(60, 20, 20), anchor="mm")
    folha.save(os.path.join(OUT, "opcoes.jpg"), quality=92)
    print("ok", OUT)


if __name__ == "__main__":
    main()
