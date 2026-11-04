#!/usr/bin/env python3
"""Amplia uma imagem RGB grande 4x com Real-ESRGAN (ONNX, CPU) em blocos com sobreposição.
    python3 ampliar_tab.py <modelo.onnx> <entrada> <saida> [--reduz LARGURA]"""
import argparse
import numpy as np
import onnxruntime as ort
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("modelo"); ap.add_argument("ent"); ap.add_argument("sai")
ap.add_argument("--reduz", type=int, default=0)
a = ap.parse_args()
im = Image.open(a.ent).convert("RGB")
if a.reduz:
    im = im.resize((a.reduz, round(im.height * a.reduz / im.width)), Image.LANCZOS)
x = np.asarray(im).astype(np.float32) / 255
s = ort.InferenceSession(a.modelo, providers=["CPUExecutionProvider"])
nome = s.get_inputs()[0].name
T, O = 192, 16
h, w, _ = x.shape
out = np.zeros((h * 4, w * 4, 3), np.float32)
for y0 in range(0, h, T):
    for x0 in range(0, w, T):
        ya, xa = max(0, y0 - O), max(0, x0 - O)
        yb, xb = min(h, y0 + T + O), min(w, x0 + T + O)
        bl = x[ya:yb, xa:xb].transpose(2, 0, 1)[None]
        r = s.run(None, {nome: bl})[0][0].transpose(1, 2, 0)
        cy, cx = (y0 - ya) * 4, (x0 - xa) * 4
        hh, ww = (min(h, y0 + T) - y0) * 4, (min(w, x0 + T) - x0) * 4
        out[y0 * 4:y0 * 4 + hh, x0 * 4:x0 * 4 + ww] = r[cy:cy + hh, cx:cx + ww]
    print(y0, h, flush=True)
Image.fromarray((out.clip(0, 1) * 255).astype(np.uint8)).save(a.sai, quality=95)
