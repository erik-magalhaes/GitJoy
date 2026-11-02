"""Gera assets/sil_mulher.png a partir da silhueta masculina: ombros mais estreitos, cintura marcada e cabelo longo."""
import cv2
import numpy as np
from PIL import Image, ImageDraw

m = np.asarray(Image.open("assets/sil_homem1.png").convert("L"), np.float32) / 255
ys, xs = np.where(m > 0.5)
m = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
h, w = m.shape
cx = w / 2
out = np.zeros((h, int(w * 1.0)), np.float32)
PAD = int(h * 0.04)
# fator de largura por altura (fração da altura da imagem; a foto vai até a coxa)
def fator(fy):
    pts = [(0.0, 0.92), (0.18, 0.92), (0.24, 0.74), (0.45, 0.70), (0.62, 0.64), (0.80, 0.78), (1.0, 0.82)]
    return np.interp(fy, [p[0] for p in pts], [p[1] for p in pts])
for y in range(h):
    f = fator(y / h)
    row = m[y]
    xs_ = (np.arange(w) - cx) / f + cx
    out[y] = np.interp(xs_, np.arange(w), row, left=0, right=0)
# cabelo longo
ys2, xs2 = np.where(out[: int(h * 0.2)] > 0.5)
topo = ys2.min()
cab_w = (xs2[ys2 < topo + h * 0.08].max() - xs2[ys2 < topo + h * 0.08].min())
out = np.vstack([np.zeros((PAD, out.shape[1]), np.float32), out])
topo += PAD
h2 = h
im = Image.fromarray((out * 255).astype(np.uint8))
d = ImageDraw.Draw(im)
hw = cab_w * 0.50
# limpa a cabeça masculina (cabelo curto) e desenha cabeça + cabelo longo e solto
d.rectangle([0, 0, im.width, topo + h * 0.13], fill=0)
d.ellipse([cx - hw, topo, cx + hw, topo + h * 0.17], fill=255)
d.rectangle([cx - hw * 0.35, topo + h * 0.12, cx + hw * 0.35, topo + h * 0.2], fill=255)
import math
pts = []
for k in range(41):
    s_ = k / 40
    yy = topo + h * (0.07 + 0.25 * s_)
    larg = hw * (1.0 + 0.25 * math.sin(s_ * math.pi * 0.8)) * (1 - 0.45 * s_ ** 3)
    pts.append((cx + larg, yy))
pts += [(cx - x_ + cx - cx, y_) for (x_, y_) in []]
esq = [(2 * cx - x_, y_) for (x_, y_) in reversed(pts)]
d.polygon(pts + esq, fill=255)
d.ellipse([cx - hw * 0.62, topo + h * 0.27, cx + hw * 0.62, topo + h * 0.335], fill=255)
a = np.asarray(im, np.float32) / 255
a = cv2.GaussianBlur(a, (0, 0), 5)
a = np.clip((a - 0.5) * 4 + 0.5, 0, 1)
Image.fromarray((a * 255).astype(np.uint8)).save("assets/sil_mulher.png")
