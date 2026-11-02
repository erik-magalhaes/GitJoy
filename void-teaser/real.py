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
    # Joseph West: de costas -> tira a arma do coldre -> mira e atira (sem faca)
    (14.2, 17.4, "1038", 0.4, 0.50, 1.0, 1.00, 1.08, {"branco_ini": 0.4}),
    (17.4, 21.4, "WA0021", 0.0, 0.45, 0.6, 1.00, 1.06, {"luz": 1.2}),
    (21.4, 26.7, "WA0025", 0.0, 0.50, 0.8, 1.00, 1.06, {"tiro": (0.63, 0.445)}),
    # Sebastián Ortiz
    (26.7, 29.0, "41640", 0.8, 0.58, 1.0, 1.00, 1.08, {}),
    (29.0, 32.2, "WA0024", 0.0, 0.50, 1.0, 1.00, 1.05, {}),
    (32.2, 34.0, "31378", 2.0, 0.60, 1.0, 1.00, 1.05, {"luz": 1.15}),
    (34.0, 37.0, "WA0026", 1.2, 0.50, 1.0, 1.00, 1.06, {"luz": 1.2}),
    # Hailey Zhang: silhueta de mulher de cabelo preto longo, de costas; adaga; golpe
    (37.0, 41.6, "924", 3.0, 0.56, 1.0, 1.00, 1.08, {"luz": 1.1}),
    (41.6, 43.6, "33106", 3.5, 0.45, 1.0, 1.10, 1.16, {"luz": 1.1}),
    (43.6, 44.5, "WA0023", 0.0, 0.50, 1.0, 1.00, 1.04, {}),
    (44.5, 46.3, "924", 9.0, 0.58, 1.0, 1.05, 1.12, {"luz": 1.1}),
    # Hunter Ward: entra no escuro, passa a mão na faca, faca na forja, bancada, luvas, sangue
    (46.3, 48.4, "41807", 1.5, 0.52, 1.0, 1.00, 1.05, {"luz": 1.1}),
    (48.4, 50.4, "WA0020", 0.0, 0.50, 0.565, 1.00, 1.05, {}),
    (50.4, 52.4, "36383", 0.0, 0.40, 1.0, 1.00, 1.05, {}),
    (52.4, 54.4, "WA0022", 0.0, 0.50, 1.0, 1.00, 1.06, {}),
    (54.4, 57.3, "44", 2.5, 0.45, 1.0, 1.10, 1.16, {}),
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
            bx, by = W * aj["tiro"][0], H * aj["tiro"][1]  # boca do cano
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


# ---------------------------------------------------------------- final realista
# fundo: galpão real (WA0028) em câmera lenta; silhuetas recortadas de pessoas reais filmadas de costas
FIGS = [  # (máscara, largura dos ombros em px, deslocamento x, altura dos ombros y, espelha, fase)
    ("homem1", 300, -360, 845, False, 0.0),      # Joseph
    ("r_mulher", 205, -122, 905, False, 1.3),    # Hailey (cabelo preto longo)
    ("homem2", 290, 118, 860, True, 2.1),        # Sebastián
    ("r_casaco", 330, 362, 820, True, 0.7),      # Hunter (sobretudo)
]
VEL_FUNDO = 0.55
_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
_HALO = (0.55 * np.exp(-(((_xx - W / 2) / 420) ** 2 + ((_yy - 760) / 480) ** 2))
         + 0.25 * np.exp(-(((_xx - W / 2) / 900) ** 2 + ((_yy - 900) / 800) ** 2))).astype(np.float32)
del _yy, _xx


@__import__("functools").lru_cache(maxsize=None)
def mascara(nome, ombro_px, espelha):
    """Máscara recortada, escalada pela largura dos ombros; devolve (máscara, y dos ombros dentro dela)."""
    m = np.asarray(Image.open(os.path.join(HERE, "assets", f"sil_{nome}.png")).convert("L"), np.float32) / 255
    ys, xs = np.where(m > 0.5)
    m = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    if espelha:
        m = m[:, ::-1]
    larg = (m > 0.5).sum(axis=1)
    h = m.shape[0]
    # ombros: primeira linha (depois da cabeça) com largura >= 85% da largura máxima do terço de cima
    topo = larg[: int(h * 0.45)]
    lim = topo.max() * 0.85
    yo = int(np.argmax(topo >= lim))
    s = ombro_px / max(1, topo.max())
    m = cv2.resize(m, (max(2, int(m.shape[1] * s)), max(2, int(h * s))), interpolation=cv2.INTER_AREA)
    m = cv2.GaussianBlur(m, (0, 0), 1.1)
    return m, int(yo * s)


def fundo_final(i0, n):
    t0 = PLANOS[-1][1]
    ini = max(0.0, (i0 / FPS - t0) * VEL_FUNDO)
    src = os.path.join(HERE, "lise", "WA0028.mp4")
    vf = (f"setpts=PTS/{VEL_FUNDO},fps={FPS},scale={W}:{H}:flags=lanczos,hqdn3d=2:2:3:3,unsharp=7:7:0.6")
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{ini:.3f}", "-i", src, "-vf", vf, "-frames:v", str(n),
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    q = np.frombuffer(p, np.uint8)
    k = len(q) // (W * H * 3)
    fr = q[: k * W * H * 3].reshape(k, H, W, 3)
    if k < n:
        fr = np.concatenate([fr, np.repeat(fr[-1:], n - k, 0)]) if k else np.zeros((n, H, W, 3), np.uint8)
    return fr


def compoe_final(bg_u8, t, luz, flash, fum):
    """Galpão real + 4 silhuetas de costas, luz de recorte vinda do próprio fundo, névoa e fumaça reais."""
    bg = bg_u8.astype(np.float32) / 255.0
    bg = bg ** 1.15
    lum = bg.mean(axis=2, keepdims=True)
    bg = lum * np.array([0.88, 0.95, 1.06], np.float32)  # preto e branco frio
    fundo = bg * (0.10 + 0.95 * luz)
    # contraluz: névoa iluminada atrás do grupo (luz do fundo do galpão), modulada pela fumaça real
    f0 = cv2.resize(fum, (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32).mean(axis=2) / 255.0
    halo = _HALO * (0.75 + 0.6 * f0)
    fundo = fundo + halo[..., None] * np.array([0.78, 0.82, 0.88], np.float32) * (0.05 + 0.95 * luz)
    img = fundo.copy()
    borrado = cv2.GaussianBlur(fundo, (0, 0), 22)
    corte = 1520  # abaixo disso, tudo some na névoa
    for k, (nome, ombro, dx, yo_alvo, esp, fase) in enumerate(FIGS):
        m, yo = mascara(nome, ombro, esp)
        resp = 1 + 0.004 * np.sin(2 * np.pi * t / 3.7 + fase)  # respiração
        bal = 2.0 * np.sin(2 * np.pi * t / 5.3 + fase)        # leve balanço
        if abs(resp - 1) > 1e-4:
            m = cv2.resize(m, (m.shape[1], int(m.shape[0] * resp)))
        mh, mw = m.shape
        x0 = int(W / 2 + dx - mw / 2 + bal)
        y0 = int(yo_alvo - yo * resp)
        sx0, sy0, sx1, sy1 = max(0, x0), max(0, y0), min(W, x0 + mw), min(H, y0 + mh)
        mm = m[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0].copy()
        yy = np.arange(sy0, sy1, dtype=np.float32)[:, None]
        fim = min(y0 + mh - 6, 1330)  # cada corpo some na névoa antes de acabar o recorte
        mm *= np.clip((fim - yy) / 260, 0, 1) ** 1.3
        borda = np.clip(mm - cv2.GaussianBlur(mm, (0, 0), 5), 0, 1) * 1.6
        reg = img[sy0:sy1, sx0:sx1]
        corpo = reg * 0.06 + 0.008  # não é preto chapado: pega um pouco do ambiente
        reg[:] = reg * (1 - mm[..., None]) + corpo * mm[..., None]
        # luz que "vaza" do fundo pelas bordas (light wrap), mais forte em cima
        topo = np.clip(1.25 - (yy - sy0) / max(1, (sy1 - sy0)), 0, 1)
        reg += borrado[sy0:sy1, sx0:sx1] * (borda * topo)[..., None] * 1.1
    # névoa no chão + fumaça real
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    chao = np.clip((yy - 0.56) / 0.18, 0, 1) ** 1.2
    f = cv2.resize(fum, (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32) / 255.0
    img += f * (0.20 + 0.35 * chao[..., None]) * (0.25 + 0.75 * luz)
    img += chao[..., None] * np.array([0.10, 0.105, 0.11], np.float32) * (0.2 + 0.8 * luz)
    if flash:
        img += 0.18
    return bloom(img, 0.55, 51, 0.6)


def render_final(args):
    i0, i1, com = args
    t_fin = PLANOS[-1][1]
    fum = fumaca_clipe()
    bgs = fundo_final(i0, i1 - i0)
    out = []
    for j, i in enumerate(range(i0, i1)):
        ta = i / FPS
        t = ta - t_fin
        if ta >= T.APAGA:
            img = np.zeros((H, W, 3), np.float32)
            luz = 0.0
        else:
            nv, flash = T.piscar(ta - T.CENAS[-1][1])
            luz = max(nv)
            img = compoe_final(bgs[j], t, luz, flash, fum[i % len(fum)])
            k = min(1.0, t / max(0.1, T.APAGA - t_fin))
            z = 1.30 + (1.0 - 1.30) * T.ease(k)  # câmera se afastando devagar
            M2 = cv2.getRotationMatrix2D((W / 2, H * 0.47), 0, z)
            img = cv2.warpAffine(img, M2, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            if t < 0.3:
                img *= t / 0.3
        img = acabamento(img, 0.6)
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
