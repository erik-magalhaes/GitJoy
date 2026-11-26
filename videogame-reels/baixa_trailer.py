#!/usr/bin/env python3
"""Baixa os primeiros N segundos de um trailer OFICIAL da Steam (HLS) → mp4.
Uso: baixa_trailer.py <appid> <indice_do_trailer> <segundos> <saida.mp4> [inicio_s]"""
import json, os, subprocess, sys, urllib.parse
import requests, imageio_ffmpeg

appid, idx, dur, out = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
ini = float(sys.argv[5]) if len(sys.argv) > 5 else 0
S = requests.Session(); S.headers["User-Agent"] = "Mozilla/5.0"
d = S.get(f"https://store.steampowered.com/api/appdetails?appids={appid}").json()[appid]["data"]
mv = d["movies"][idx]
print(d["name"], "|", mv["name"])
master = mv["hls_h264"]
txt = S.get(master).text
var = []
for i, l in enumerate(txt.splitlines()):
    if l.startswith("#EXT-X-STREAM-INF"):
        bw = int(l.split("BANDWIDTH=")[1].split(",")[0])
        res = l.split("RESOLUTION=")[1].split(",")[0] if "RESOLUTION=" in l else "?"
        var.append((bw, res, txt.splitlines()[i + 1]))
var.sort()
alvo = [v for v in var if v[1] != "?" and int(v[1].split("x")[1]) <= 1080] or var
bw, res, uri = alvo[-1]
pl_url = urllib.parse.urljoin(master, uri)
pl = S.get(pl_url).text.splitlines()
init, segs, t, mapa = None, [], 0.0, None
for i, l in enumerate(pl):
    if l.startswith("#EXT-X-MAP"):
        init = urllib.parse.urljoin(pl_url, l.split('URI="')[1].split('"')[0])
    if l.startswith("#EXTINF"):
        dd = float(l.split(":")[1].split(",")[0])
        if t + dd >= ini and t < ini + dur:
            segs.append(urllib.parse.urljoin(pl_url, pl[i + 1]))
        t += dd
tmp = out + ".ts"
with open(tmp, "wb") as f:
    if init:
        f.write(S.get(init).content)
    for s in segs:
        f.write(S.get(s).content)
# áudio também? só vídeo (o áudio do trailer não entra no Reels)
FF = imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([FF, "-v", "error", "-y", "-i", tmp, "-an", "-c:v", "libx264", "-crf", "18", "-preset", "fast", out], check=True)
os.remove(tmp)
print("ok", res, len(segs), "segmentos →", out)
