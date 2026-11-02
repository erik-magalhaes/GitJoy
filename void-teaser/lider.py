"""assets/sil_lider.png: tronco do homem1 (corpo largo, sem capacete) + pernas do soldado (corpo inteiro, sem fuzil)."""
import cv2, numpy as np
from PIL import Image
def crop(a):
    ys, xs = np.where(a > 127)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
sold = np.asarray(Image.open("assets/sil_soldado.png").convert("L"))
b = (sold > 127).astype(np.uint8) * 255
o = cv2.morphologyEx(b, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25)))
n, lab, st, _ = cv2.connectedComponentsWithStats(o)
o = np.where(lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA]), 255, 0).astype(np.uint8)
sold = crop(o)
cima = crop(np.asarray(Image.open("assets/sil_homem1.png").convert("L")))
# pernas: do quadril (52% da altura) para baixo
ph = sold.shape[0]
pernas = sold[int(ph * 0.52):]
# largura do quadril do soldado x largura da base do tronco
lb = (cima[-5] > 127).sum()
lp = (pernas[5] > 127).sum()
s = lb / max(1, lp) * 0.92
pernas = cv2.resize(pernas, (int(pernas.shape[1] * s), int(pernas.shape[0] * s * 1.05)))
W = max(cima.shape[1], pernas.shape[1])
out = np.zeros((cima.shape[0] + pernas.shape[0] - 30, W), np.uint8)
x0 = (W - cima.shape[1]) // 2
out[:cima.shape[0], x0:x0 + cima.shape[1]] = cima
x1 = (W - pernas.shape[1]) // 2
reg = out[cima.shape[0] - 30:, x1:x1 + pernas.shape[1]]
np.maximum(reg, pernas, out=reg)
out = cv2.GaussianBlur(out, (0, 0), 3)
out = np.where(out > 127, 255, 0).astype(np.uint8)
Image.fromarray(cv2.GaussianBlur(out, (0, 0), 1.5)).save("assets/sil_lider.png")
