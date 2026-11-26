#!/usr/bin/env python3
"""Acha o centro do rosto no bruto a cada 0,25 s (Haar frontal + perfil, OpenCV 4) → out/rosto_<nome>.json.
Uso: rosto.py <nome> <t0> <t1>  (vários intervalos: repetir os três)."""
import json, os, subprocess, sys
import cv2, numpy as np, imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
ROOT = os.path.dirname(os.path.abspath(__file__))
fc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
fp = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")
nome = sys.argv[1]
saida = os.path.join(ROOT, "out", f"rosto_{nome}.json")
pts = json.load(open(saida)) if os.path.exists(saida) else {}
args = sys.argv[2:]
for i in range(0, len(args), 2):
    t0, t1 = float(args[i]), float(args[i + 1])
    w, h = 540, 960
    p = subprocess.Popen([FF, "-v", "error", "-ss", str(t0), "-t", str(t1 - t0), "-i", os.path.join(ROOT, "brutos", nome + ".mp4"),
                          "-vf", f"fps=4,scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
    k = 0
    while True:
        b = p.stdout.read(w * h)
        if len(b) < w * h:
            break
        g = np.frombuffer(b, np.uint8).reshape(h, w)
        fs = list(fc.detectMultiScale(g, 1.1, 5, minSize=(70, 70)))
        if not fs:
            fs = list(fp.detectMultiScale(g, 1.1, 4, minSize=(70, 70))) + \
                 [(w - x - ww, y, ww, hh) for x, y, ww, hh in fp.detectMultiScale(g[:, ::-1].copy(), 1.1, 4, minSize=(70, 70))]
        if fs:
            x, y, ww, hh = max(fs, key=lambda r: r[2])
            pts[f"{t0 + k * 0.25:.2f}"] = [(x + ww / 2) * 2, (y + hh / 2) * 2]
        k += 1
json.dump(pts, open(saida, "w"))
print(nome, len(pts))
