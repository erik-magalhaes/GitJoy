#!/usr/bin/env python3
"""Imagem inicial 9:16 pro Gemini (Veo): "VOCÊ ESTÁ DENTRO DO HOT STREAK" (9/nov, ideia dele: POV correndo na rua, olha
pra trás, os mascotes estão atrás e ele está dentro do jogo). Clipe 1 (rua) é só texto no Gemini; esta imagem é o
início do clipe 2: a pista verde do jogo vista de quem corre, a torcida oficial ao fundo e os 4 mascotes OFICIAIS do
manual (p_*.png) correndo na direção da câmera.

    /usr/bin/python3 foto_gemini.py   → out/gemini/hotstreak_pista_9x16.png
"""
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(ROOT, "assets", "pecas")
W, H = 1440, 2560
HOR = 1060          # linha onde a pista encontra a arquibancada
VERDE, VERDE2 = (34, 150, 70), (28, 128, 60)


def pista():
    """Pista plana (como a do jogo: faixas verdes, linhas brancas tracejadas, estrelinhas) e depois em perspectiva."""
    pw, ph = 1600, 3200
    im = Image.new("RGB", (pw, ph), VERDE)
    d = ImageDraw.Draw(im)
    for k in range(0, ph, 400):
        d.rectangle((0, k, pw, k + 200), fill=VERDE2)
    for x in (400, 800, 1200):  # 4 raias
        for y in range(0, ph, 160):
            d.rectangle((x - 9, y, x + 9, y + 80), fill=(245, 245, 235))
    rng = np.random.default_rng(3)
    for _ in range(40):
        cx, cy, r = rng.uniform(40, pw - 40), rng.uniform(40, ph - 40), rng.uniform(16, 30)
        pts = [(cx + r * (1 if i % 2 == 0 else 0.45) * np.cos(np.pi / 2 + i * np.pi / 5),
                cy - r * (1 if i % 2 == 0 else 0.45) * np.sin(np.pi / 2 + i * np.pi / 5)) for i in range(10)]
        d.polygon(pts, fill=(150, 220, 150))
    a = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR)
    src = np.float32([[0, 0], [pw, 0], [pw, ph], [0, ph]])
    dst = np.float32([[60, HOR], [W - 60, HOR], [W + 1300, H + 200], [-1300, H + 200]])
    M = cv2.getPerspectiveTransform(src, dst)
    out = cv2.warpPerspective(a, M, (W, H), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    m = cv2.warpPerspective(np.full((ph, pw), 255, np.uint8), M, (W, H))
    img = Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).convert("RGBA")
    img.putalpha(Image.fromarray(m))
    return img


def torcida():
    t = Image.open(os.path.join(P, "v_torcida_limpa.png")).convert("RGBA")
    k = (HOR + 120) / t.height
    t = t.resize((int(t.width * k), HOR + 120), Image.LANCZOS)
    x0 = (t.width - W) // 2
    return t.crop((x0, 0, x0 + W, t.height))


def mascote(nome, alt):
    im = Image.open(os.path.join(P, f"p_{nome}.png")).convert("RGBA")
    im = im.crop(im.getbbox())
    return im.resize((int(im.width * alt / im.height), alt), Image.LANCZOS)


def main():
    img = Image.new("RGBA", (W, H), (240, 230, 210, 255))
    img.alpha_composite(torcida())
    img.alpha_composite(pista())
    # mascotes correndo na direção da câmera: o de trás menor, o da frente grande
    for nome, alt, cx, base in (("mum", 480, 540, 1340), ("dangle", 470, 960, 1330),
                                ("gobbler", 720, 330, 2050), ("hurley", 860, 1050, 2200)):
        m = mascote(nome, alt)
        sh = Image.new("RGBA", (int(m.width * 0.9), int(alt * 0.12)), (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse((0, 0, sh.width - 1, sh.height - 1), fill=(0, 30, 0, 110))
        sh = sh.filter(ImageFilter.GaussianBlur(alt * 0.03))
        img.alpha_composite(sh, (cx - sh.width // 2, base - sh.height // 2))
        img.alpha_composite(m, (cx - m.width // 2, base - m.height))
    os.makedirs(os.path.join(ROOT, "out", "gemini"), exist_ok=True)
    img.convert("RGB").save(os.path.join(ROOT, "out", "gemini", "hotstreak_pista_9x16.png"))


if __name__ == "__main__":
    main()
