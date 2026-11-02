"""Teaser VOID — versão com FILMAGENS REAIS (Mixkit, licença livre) no lugar das cenas desenhadas.

Mesma narração, legendas e trilha do teaser.py. O final (os quatro de costas, luzes piscando, apagão) continua o
do teaser.py, com fumaça real por cima.

python3 real.py --frame 3 20 40   -> out/frames_real.jpg
python3 real.py                   -> out/void_real.mp4 e out/void_real_sem_legenda.mp4 (sem áudio; finalize com finaliza.py)
"""
import os
import subprocess
import sys
from multiprocessing import Pool

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import teaser as T  # noqa: E402
import tipografia  # noqa: E402

VERSAO = os.environ.get("VERSAO", "homem")  # homem | mulher | texto
from motor_void import FPS, H, W, acabamento, bloom, para_u8  # noqa: E402

M = os.path.join(HERE, "mix")

# (início, fim, clipe, segundo de origem, centro x do recorte vertical, velocidade, zoom início, zoom fim, ajustes)
PLANOS = [
    (0.0, 4.4, "WA0029", 0.3, 0.50, 1.0, 1.00, 1.06, {}),
    (4.4, 5.9, "4163", 3.0, 0.50, 1.0, 1.05, 1.12, {"desfoca": 1.2}),
    (5.9, 7.3, "47512", 2.0, 0.62, 1.0, 1.00, 1.05, {"desfoca": 1.0}),
    (7.3, 9.4, "42041", 1.0, 0.50, 1.0, 1.15, 1.00, {"luz": 0.8}),
    (9.4, 10.4, "23658", 0.1, 0.30, 1.0, 1.00, 1.04, {"luz": 0.9}),
    (10.4, 12.7, "WA0028", 0.5, 0.50, 1.0, 1.00, 1.06, {}),
    (12.7, 14.2, "31380", 0.3, 0.42, 1.0, 1.00, 1.10, {"branco_fim": 0.5}),
    # Joseph West
    (14.2, 16.2, "WA0020", 0.0, 0.50, 0.565, 1.00, 1.05, {"branco_ini": 0.4}),
    (16.2, 19.6, "33605", 0.0, 0.58, 0.55, 1.25, 1.40, {"pistola": True}),
    (19.6, 22.2, "1038", 0.4, 0.50, 1.0, 1.00, 1.08, {}),
    (22.2, 25.3, "WA0025", 0.5, 0.50, 1.0, 1.00, 1.06, {}),
    (25.3, 26.7, "33605", 1.87, 0.66, 1.0, 1.00, 1.00, {"pistola": True, "tiro": True}),
    # Sebastián Ortiz
    (26.7, 29.0, "41640", 0.8, 0.58, 1.0, 1.00, 1.08, {}),
    (29.0, 32.2, "WA0024", 0.0, 0.50, 1.0, 1.00, 1.05, {}),
    (32.2, 34.0, "31378", 2.0, 0.60, 1.0, 1.00, 1.05, {"luz": 1.15}),
    (34.0, 37.0, "WA0026", 1.2, 0.50, 1.0, 1.00, 1.06, {"luz": 1.2}),
    # Hailey Zhang
    (37.0, 41.2, "3918", 3.0, 0.44, 1.0, 1.00, 1.07, {"luz": 1.1}),
    (41.2, 43.6, "36383", 0.0, 0.40, 1.0, 1.00, 1.05, {}),
    (43.6, 44.5, "WA0023", 0.0, 0.50, 1.0, 1.00, 1.04, {}),
    (44.5, 46.3, "36383", 3.0, 0.40, 1.0, 1.05, 1.10, {}),
    # Hunter Ward
    (46.3, 48.7, "WA0021", 0.0, 0.45, 1.0, 1.00, 1.05, {"luz": 1.2}),
    (48.7, 50.8, "41807", 1.5, 0.52, 1.0, 1.00, 1.05, {"luz": 1.1}),
    (50.8, 53.2, "WA0022", 0.0, 0.50, 1.0, 1.00, 1.06, {}),
    (53.2, 55.0, "13163", 2.0, 0.55, 1.0, 1.00, 1.06, {}),
    (55.0, 57.3, "44", 3.0, 0.45, 1.0, 1.10, 1.16, {}),
    (57.3, 59.1, "WA0027", 2.55, 0.50, 1.0, 1.00, 1.08, {}),
]


def le_trecho(clipe, ini, n, cx, vel):
    """Lê n quadros (30 fps de saída) do clipe a partir de ini, recorte vertical 9:16 centrado em cx, 1080x1920."""
    src = os.path.join(M, f"v_{clipe}.mp4")
    lise = clipe.startswith("WA")
    if lise:
        src = os.path.join(HERE, "lise", f"{clipe}.mp4")
    pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                         "-of", "csv=p=0", src], capture_output=True, text=True).stdout.strip().split(",")
    sw, sh = int(pr[0]), int(pr[1])
    cw = min(int(sh * 9 / 16), sw) // 2 * 2
    x = int(min(max(0, cx * sw - cw / 2), sw - cw)) // 2 * 2
    vf = f"setpts=PTS/{vel},fps={FPS},crop={cw}:{sh}:{x}:0,scale={W}:{H}:flags=lanczos"
    if lise:  # vídeos do WhatsApp (baixa resolução): limpa blocos e devolve um pouco de nitidez
        vf += ",hqdn3d=2:2:3:3,unsharp=7:7:0.7"
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(ini), "-i", src, "-vf", vf, "-frames:v", str(n),
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    q = np.frombuffer(p, np.uint8)
    k = len(q) // (W * H * 3)
    fr = q[: k * W * H * 3].reshape(k, H, W, 3)
    if k < n:  # completa congelando o último quadro
        fr = np.concatenate([fr, np.repeat(fr[-1:], n - k, 0)])
    return fr


def gradua(img, aj):
    """Cor de thriller: menos saturação, pretos frios, contraste; tudo em float 0..1."""
    x = img.astype(np.float32) / 255.0
    if aj.get("desfoca"):
        x = cv2.GaussianBlur(x, (0, 0), aj["desfoca"])
    x = x ** 1.12 * aj.get("luz", 1.0)
    lum = x.mean(axis=2, keepdims=True)
    x = lum + (x - lum) * 0.62
    if aj.get("pistola"):  # fundo cinza claro do estúdio vira névoa escura e fria
        x = np.clip((x - 0.35) * 0.55, 0, 1) * np.array([0.85, 0.95, 1.1], np.float32)
    return x


_fumaca = {}


def fumaca(t):
    """Fumaça real (clipe 8461) para somar por cima (tela)."""
    i = int(t * FPS) % (25 * FPS)
    if "fr" not in _fumaca:
        _fumaca["fr"] = None
    return None


def quadro_plano(pl, k, fr):
    t0, t1, clipe, ini, cx, vel, z0, z1, aj = pl
    n = len(fr)
    t = k / FPS
    d = t1 - t0
    img = gradua(fr[k], aj)
    z = z0 + (z1 - z0) * T.ease(k / max(1, n - 1))
    if abs(z - 1) > 1e-3:
        Mx = cv2.getRotationMatrix2D((W / 2, H / 2), 0, z)
        img = cv2.warpAffine(img, Mx, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    if aj.get("tiro"):
        ta = t0 + t
        if ta >= T.TIRO:
            f = np.exp(-(ta - T.TIRO) / 0.06)
            y, x = np.mgrid[0:H, 0:W].astype(np.float32)
            bx, by = W * 0.86, H * 0.20  # boca do cano
            img += (np.exp(-((x - bx) ** 2 + (y - by) ** 2) / (4000 + 60000 * f)) * 5 * f)[..., None] * np.array(
                [1, 0.75, 0.4], np.float32)
            img += 0.35 * f * np.array([1, 0.85, 0.6], np.float32)
            if ta - T.TIRO < 0.3:
                s = (1 - (ta - T.TIRO) / 0.3) * 16
                img = cv2.warpAffine(img, np.float32([[1, 0, s * np.sin(ta * 90)], [0, 1, s * np.cos(ta * 70)]]),
                                     (W, H), borderMode=cv2.BORDER_REFLECT)
    # transições: entra do preto rápido e sai para o preto
    if t < 0.2 and t0 > 0:
        img *= t / 0.2
    if d - t < 0.12:
        img *= max(0, (d - t) / 0.12)
    if aj.get("branco_fim") and d - t < aj["branco_fim"]:
        w = T.ease(1 - (d - t) / aj["branco_fim"])
        img = img * (1 - w) + w * np.array([0.8, 0.78, 0.74], np.float32)
    if aj.get("branco_ini") and t < aj["branco_ini"]:
        w = 1 - t / aj["branco_ini"]
        img = img * (1 - w) + w * np.array([0.8, 0.78, 0.74], np.float32)
    if t0 == 0 and t < 0.6:
        img *= t / 0.6
    return bloom(img, 0.6, 31, 0.35)


def textos(img, t, luz, com):
    if VERSAO == "texto":
        return tipografia.aplica(img, t, luz)
    return T.aplica_legenda(img, t) if com else img


def render_plano(args):
    i, com = args
    pl = PLANOS[i]
    n = int(round(pl[1] * FPS)) - int(round(pl[0] * FPS))
    fr = le_trecho(pl[2], pl[3], n, pl[4], pl[5])
    out = []
    for k in range(n):
        img = acabamento(quadro_plano(pl, k, fr), 0.5)
        img = textos(img, pl[0] + k / FPS, 1.0, com)
        out.append(para_u8(img).tobytes())
    return out


@__import__("functools").lru_cache(maxsize=1)
def fumaca_clipe():
    """Fumaça em baixa resolução (270x480, 12 s) — é desfocada mesmo; ampliada quadro a quadro."""
    n = 12 * FPS
    src = os.path.join(M, "v_8461.mp4")
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", "1", "-i", src, "-vf",
                        f"fps={FPS},crop=ih*9/16:ih,scale=270:480", "-frames:v", str(n), "-f", "rawvideo",
                        "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    return np.frombuffer(p, np.uint8).reshape(-1, 480, 270, 3)


def render_final(args):
    i0, i1, com = args
    t0 = PLANOS[-1][1]
    fum = fumaca_clipe()
    out = []
    for i in range(i0, i1):
        ta = i / FPS
        t = ta - T.CENAS[-1][1]
        img = T.c_final(t, T.DUR - T.CENAS[-1][1])
        if ta < T.APAGA:
            nv, _ = T.piscar(t)
            f = cv2.resize(fum[i % len(fum)], (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32) / 255.0
            img = img + f * 0.35 * (0.3 + 0.7 * max(nv))
        img = acabamento(img, 0.6)
        luz = max(T.piscar(t)[0]) if ta < T.APAGA else 0.0
        img = textos(img, ta, luz, com)
        out.append(para_u8(img).tobytes())
    return out


def render(caminho, com):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-tune", "film",
                          "-pix_fmt", "yuv420p", caminho], stdin=subprocess.PIPE)
    i_fim = int(round(PLANOS[-1][1] * FPS))
    n = int(T.DUR * FPS)
    blocos_fin = [(i, min(n, i + 15), com) for i in range(i_fim, n, 15)]
    with Pool(4) as pool:
        for fr in pool.imap(render_plano, [(i, com) for i in range(len(PLANOS))]):
            for b in fr:
                p.stdin.write(b)
        for fr in pool.imap(render_final, blocos_fin):
            for b in fr:
                p.stdin.write(b)
    p.stdin.close()
    p.wait()


if __name__ == "__main__":
    if "--frame" in sys.argv:
        ts = [float(v) for v in sys.argv[sys.argv.index("--frame") + 1:]]
        ims = []
        for ta in ts:
            for i, pl in enumerate(PLANOS):
                if pl[0] <= ta < pl[1]:
                    k = int(round((ta - pl[0]) * FPS))
                    n = int(round(pl[1] * FPS)) - int(round(pl[0] * FPS))
                    fr = le_trecho(pl[2], pl[3], n, pl[4], pl[5])
                    img = textos(acabamento(quadro_plano(pl, min(k, n - 1), fr), 0.5), ta, 1.0, True)
                    break
            else:
                i = int(ta * FPS)
                img = None
                b = render_final((i, i + 1, True))
                ims.append(Image.frombytes("RGB", (W, H), b[0]).resize((360, 640)))
                continue
            ims.append(Image.fromarray(para_u8(img)).resize((360, 640)))
        fol = Image.new("RGB", (360 * min(6, len(ims)), 640 * ((len(ims) + 5) // 6)))
        for k, im in enumerate(ims):
            fol.paste(im, ((k % 6) * 360, (k // 6) * 640))
        fol.save(os.path.join(T.OUT, "frames_real.jpg"), quality=88)
    else:
        render(os.path.join(T.OUT, f"void_{VERSAO}.mp4"), True)
