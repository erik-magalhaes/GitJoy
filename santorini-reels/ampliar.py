#!/usr/bin/env python3
"""Peças OFICIAIS do manual Spin Master (renders 3D pequenos, 50–400 px) ampliadas 4x com Real-ESRGAN (ONNX, CPU).
O modelo (RealESRGAN_x4.onnx, huggingface Meeperomi/RealESRGAN_x4-onnx) fica no scratchpad, fora do git.
Cor e alfa são ampliados separadamente (o alfa também pela rede, para a borda sair limpa).

    python3 ampliar.py <modelo.onnx> <entrada.png> ... -o assets/pecas/
"""
import argparse
import os

import numpy as np
import onnxruntime as ort
from PIL import Image, ImageFilter


def roda(sess, rgb):
    x = rgb.astype(np.float32).transpose(2, 0, 1)[None] / 255
    y = sess.run(None, {sess.get_inputs()[0].name: x})[0][0]
    return (y.transpose(1, 2, 0).clip(0, 1) * 255).astype(np.uint8)


def amplia(sess, im, vezes=1):
    im = im.convert("RGBA")
    for _ in range(vezes):
        a = np.asarray(im)
        alfa = a[..., 3:4].astype(np.float32) / 255
        # cor sobre a média das bordas visíveis (evita halo branco/preto)
        cor = (a[..., :3].astype(np.float32) * alfa + 200 * (1 - alfa)).astype(np.uint8)
        rgb = roda(sess, cor)
        al = roda(sess, np.repeat(a[..., 3:4], 3, 2))[..., 0]
        im = Image.fromarray(np.dstack([rgb, al]), "RGBA")
    al = im.getchannel("A").point(lambda v: 0 if v < 12 else min(255, int((v - 12) * 1.06)))
    im.putalpha(al.filter(ImageFilter.GaussianBlur(0.6)))
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("modelo")
    ap.add_argument("imgs", nargs="+")
    ap.add_argument("-o", default="assets/pecas")
    ap.add_argument("--vezes", type=int, default=1)
    a = ap.parse_args()
    sess = ort.InferenceSession(a.modelo, providers=["CPUExecutionProvider"])
    os.makedirs(a.o, exist_ok=True)
    for f in a.imgs:
        out = amplia(sess, Image.open(f), a.vezes)
        p = os.path.join(a.o, os.path.basename(f))
        out.save(p)
        print(p, out.size, flush=True)


if __name__ == "__main__":
    main()
