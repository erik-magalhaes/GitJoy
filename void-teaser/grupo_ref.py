"""Máscara do grupo final a partir da referência (assets/ref_grupo.jpg): 4 silhuetas de costas.
Ajustes pedidos: a mulher de cabelo comprido e o homem de altura média com cabelo ralo.
Saída: assets/sil_grupo.png (largura 1080, corpos esticados para baixo até sair do quadro)."""
import math
import cv2
import numpy as np
from PIL import Image, ImageDraw

S = 1080 / 736
ref = np.asarray(Image.open("assets/ref_grupo.jpg").convert("L"), np.float32)
# máscara suave pelo tom (céu ~47, silhueta ~3)
m = np.clip((30 - ref) / 14, 0, 1)
m = cv2.resize(m, (1080, 1080), interpolation=cv2.INTER_CUBIC)
m = np.clip(m, 0, 1)
im = Image.fromarray((m * 255).astype(np.uint8))
d = ImageDraw.Draw(im)
P = lambda x, y: (x * S, y * S)
rng = np.random.default_rng(4)

# --- homem de altura média (2º da esquerda): cabelo ralo -> crânio natural com fios curtos
d.rectangle([P(244, 168), P(356, 232)], fill=0)
cx, cy, rx, ry = 300, 241, 42, 46  # cúpula do crânio; embaixo continua a cabeça/nuca original da foto
d.ellipse([P(cx - rx, cy - ry), P(cx + rx, cy + ry * 0.55)], fill=255)
d.polygon([P(cx - rx + 3, cy + 6), P(cx + rx - 3, cy + 6), P(cx + 27, 286), P(cx - 27, 286)], fill=255)  # nuca
for sx in (-1, 1):  # orelhas
    ex = cx + sx * (rx - 5)
    d.ellipse([P(ex - 4, 240), P(ex + 4, 260)], fill=255)
for k in range(60):  # fios ralos e curtos, só no alto e atrás
    a = math.pi * (0.12 + 0.76 * rng.random())
    x0 = cx - rx * math.cos(a)
    y0 = cy - ry * math.sin(a)
    comp = rng.uniform(0.6, 2.0)
    x1 = x0 - comp * math.cos(a) * 0.6 + rng.uniform(-0.6, 0.6)
    y1 = y0 - comp * math.sin(a)
    d.line([P(x0, y0), P(x1, y1)], fill=255, width=1)

# --- mulher (3º): cabelo comprido caindo até os ombros/costas, sem pescoço aparente
cab = [P(458, 262), P(478, 250), P(512, 248), P(538, 258), P(552, 280), P(560, 310), P(566, 345),
       P(574, 378), P(578, 405), P(566, 418), P(548, 412), P(520, 398), P(492, 380), P(470, 352),
       P(462, 318), P(456, 290)]
d.polygon(cab, fill=255)
for k in range(9):  # pontas do cabelo irregulares
    x = 528 + k * 5.5 + rng.uniform(-1.5, 1.5)
    d.line([P(x, 398 + k * 1.5), P(x + rng.uniform(-2, 3), 414 + k * 1.2 + rng.uniform(0, 7))], fill=255, width=int(2.4 * S))

m = np.asarray(im, np.float32) / 255
m = cv2.GaussianBlur(m, (0, 0), 1.2)
# corta antes das plantas do pé da foto e estica as pernas para baixo
corte = int(560 * S)
m = m[:corte]
base = m[-3:].max(axis=0)
ext = np.repeat(base[None], 1400, 0)
# as frestas entre as pernas fecham aos poucos: embaixo fica tudo escuro, como na referência
fade = np.clip(np.arange(1400) / 220.0, 0, 1)[:, None]
ext = ext * (1 - fade) + fade
m = np.vstack([m, ext])
Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8)).save("assets/sil_grupo.png")
prev = Image.fromarray((255 - np.clip(m, 0, 1) * 200).astype(np.uint8)).resize((540, int(m.shape[0] / 2)))
prev.save("out/sil_grupo_prev.png")
print(m.shape)
