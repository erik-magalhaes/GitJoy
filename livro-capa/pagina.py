#!/usr/bin/env python3
"""Vídeos no estilo "página do livro" do BookTok/Reels (referência que o Erik mandou):
foto de casal se beijando no fundo, EM MOVIMENTO (paralaxe 2,5D com mapa de profundidade), gancho "POV" grande em
cima e uma página creme com o trecho do livro, frases grifadas em rosa, corações e setinhas desenhados à mão,
"Capítulo N" e a porcentagem no rodapé. Fecha com o livro e "EM BREVE".

    python3 pagina.py [--so nome ...]            → out/pagina/<nome>_{com_trilha,para_musica}.mp4
    python3 pagina.py --frame 2 9 15 [--so ...]  → out/pagina/frames.jpg

Profundidade: Depth Anything small (ONNX, huggingface Xenova/depth-anything-small-hf, model_quantized.onnx),
caminho em DEPTH (fora do git). Sem o modelo, o fundo só faz zoom e pan.
"""
import argparse
import os
import subprocess
import sys
from multiprocessing import Pool

import cv2
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from divulgacao import _mascara, fonte, livro, texto, texto_ouro, filete, CREME  # noqa: E402
import trechos  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(AQUI, "out", "pagina")
DEPTH = os.environ.get("DEPTH_ONNX", "/tmp/claude-0/-home-user-GitJoy/63292039-f7c8-5ca8-813a-78035237103f/scratchpad/depth.onnx")
W, H, FPS = 1080, 1920, 30
ENTRA, PASSO, FINAL = 1.2, 2.6, 3.4

PAPEL = (248, 241, 230)
TINTA = (40, 32, 30)
ROSA = (238, 150, 170)
VINHO = (196, 64, 92)
# cada vídeo com uma "página" diferente: (papel, tinta, grifo, rabisco, rodapé)
TEMAS = {
    "creme": ((248, 241, 230), (40, 32, 30), (238, 150, 170), (196, 64, 92), (140, 130, 125)),
    "noturno": ((24, 22, 26), (226, 220, 214), (150, 40, 70), (240, 120, 150), (120, 115, 120)),
    "branco": ((253, 253, 251), (30, 30, 34), (255, 210, 120), (210, 80, 40), (150, 150, 150)),
    "sepia": ((236, 222, 196), (60, 42, 28), (214, 120, 100), (150, 50, 40), (130, 110, 90)),
    "rosa": ((252, 232, 236), (60, 30, 40), (240, 120, 150), (180, 30, 70), (160, 120, 130)),
}

VIDEOS = {
    "elevador": {
        "pov": "POV: Ele sumiu depois de uma noite. Cinco anos depois, você fica presa no elevador com ele… e ele ainda não sabe dos trigêmeos.",
        "cap": 4, "pct": 22, "foco": (0.42, 0.45), "vfoco": 0.45, "vy": 0.62, "tema": "noturno",
        "par": [
            "Rafael apoiou a mão no espelho do fundo, do lado do rosto dela.",
            "— Se você der mais um passo — disse ela, baixinho —, eu não respondo por mim.",
            "— Então não responde.",
            "— Cinco anos. E eu ainda lembro do gosto da sua boca.",
            "— Aperta o botão. Antes que eu esqueça quem eu sou.",
        ],
        "grifo": ["não respondo por mim", "lembro do gosto da sua boca", "Antes que eu esqueça quem eu sou"],
    },
    "cozinha": {
        "pov": "POV: Vocês moram juntos por contrato. Regra número um: nada de beijos. E ele está sem camisa na cozinha à 1h30.",
        "cap": 7, "pct": 38, "foco": (0.5, 0.12), "vfoco": 0.5, "vy": 0.5, "vzoom": 1.0, "tema": "creme",
        "par": [
            "O calor do corpo dele chegou antes da mão.",
            "— Regra número um — disse Helena, para o fogão.",
            "A mão dele parou na cintura dela, por cima da camiseta velha. Só parou.",
            "— Me pede pra sair, Helena. Uma palavra só. Eu saio.",
            "Ela não pediu.",
        ],
        "grifo": ["chegou antes da mão", "Só parou.", "Ela não pediu."],
    },
    "escritorio": {
        "pov": "POV: Ele é seu chefe, o pai dos seus filhos e o homem que você jurou odiar. São 9 da noite e o andar está vazio.",
        "cap": 8, "pct": 44, "foco": (0.5, 0.3), "vfoco": 0.5, "vy": 0.3, "tema": "branco",
        "par": [
            "— Você sempre se debruça assim na mesa dos seus chefes?",
            "— Só dos que ficam olhando.",
            "O polegar dele subiu pelo pulso dela, até a dobra do cotovelo. Helena esqueceu como se respirava.",
            "— Você vai me deixar sem ar no meio do expediente.",
            "— O expediente acabou às seis.",
        ],
        "grifo": ["Só dos que ficam olhando.", "esqueceu como se respirava", "acabou às seis"],
    },
    "provar": {
        "pov": "POV: Ele é CEO. Você é confeiteira. E ele não veio provar o bolo.",
        "cap": 18, "pct": 96, "foco": (0.5, 0.2), "vfoco": 0.56, "vy": 0.5, "vzoom": 1.0, "tema": "sepia",
        "par": [
            "— Me deixa provar.",
            "— O bolo é da vitrine. Ninguém prova o bolo da vitrine.",
            "— Eu não falei do bolo.",
            "Ele segurou o pulso dela. Provou. Sem pressa nenhuma, olhando para ela o tempo inteiro.",
            "— Eu ainda não provei o que eu vim provar.",
        ],
        "grifo": ["Eu não falei do bolo.", "Sem pressa nenhuma", "o que eu vim provar"],
    },
    "regra_quebrada": {
        "pov": "POV: O noivado era de mentira. A regra era clara: nada de beijos fora das fotos. Até essa noite.",
        "cap": 10, "pct": 55, "foco": (0.6, 0.3), "vfoco": 0.5, "vy": 0.15, "tema": "rosa",
        "par": [
            "— Então eu estou quebrando a regra número um — disse Helena. — De propósito. Pra constar.",
            "— Tira — disse ela, puxando a gravata dele até o nó se desfazer.",
            "— Você tem certeza?",
            "— Eu tô sem ar desde o primeiro café, Rafael. Tenho.",
            "A chave girou duas vezes.",
        ],
        "grifo": ["De propósito.", "puxando a gravata dele", "A chave girou duas vezes."],
    },
    "manha": {
        "pov": "POV: Ele tentou sair da cama às 6h30 sem te acordar. Péssima ideia.",
        "cap": 12, "pct": 63, "foco": (0.5, 0.4), "vfoco": 0.6, "vy": 0.5, "vzoom": 1.0, "tema": "branco",
        "par": [
            "— Você ia sair sem me acordar? — disse Helena, de olhos fechados, a voz rouca de sono.",
            "— Ia correr.",
            "Ela abriu um olho só. Depois puxou a camiseta dele com as duas mãos, até tirar pela cabeça, e jogou no chão.",
            "— Cinco minutos — disse. — Depois você corre.",
            "Os cinco minutos viraram quarenta.",
        ],
        "grifo": ["sem me acordar", "jogou no chão", "viraram quarenta"],
    },
}


def dur(v):
    return ENTRA + PASSO * len(v["par"]) + 1.6 + FINAL


def seg(t, a, b):
    return min(1.0, max(0.0, (t - a) / (b - a)))


def ease(u):
    return u * u * (3 - 2 * u)


_cache = {}


# ---------------------------------------------------------------- fundo em movimento (paralaxe com profundidade)
def profundidade(rgb):
    if not os.path.exists(DEPTH):
        return np.zeros(rgb.shape[:2], np.float32)
    import onnxruntime as ort
    sess = ort.InferenceSession(DEPTH, providers=["CPUExecutionProvider"])
    x = cv2.resize(rgb, (518, 518)).astype(np.float32) / 255
    x = (x - np.array([0.485, 0.456, 0.406])) / np.array([0.229, 0.224, 0.225])
    out = sess.run(None, {sess.get_inputs()[0].name: x.transpose(2, 0, 1)[None].astype(np.float32)})[0]
    d = out.reshape(out.shape[-2:])
    d = cv2.resize(d, (rgb.shape[1], rgb.shape[0]))
    d = (d - d.min()) / max(1e-6, d.max() - d.min())
    return cv2.GaussianBlur(d.astype(np.float32), (0, 0), 6)


def base(nome):
    if "b_" + nome in _cache:
        return _cache["b_" + nome]
    v = VIDEOS[nome]
    im = np.asarray(Image.open(os.path.join(AQUI, "assets", "pagina", nome + ".jpg")).convert("RGB"))
    # recorte 9:16 com folga de 12% para o movimento, em torno do foco
    Wb, Hb = int(W * 1.12), int(H * 1.12)
    s = max(Wb / im.shape[1], Hb / im.shape[0])
    im = cv2.resize(im, (round(im.shape[1] * s), round(im.shape[0] * s)), interpolation=cv2.INTER_AREA)
    cx, cy = v["foco"][0] * im.shape[1], v["foco"][1] * im.shape[0]
    x0 = int(min(max(0, cx - Wb / 2), im.shape[1] - Wb))
    # o foco (rosto/beijo) fica a ~33% da altura, entre o gancho e a página; se faltar foto em cima, completa
    # com a borda da própria foto bem desfocada e escura
    y0 = int(min(cy - Hb * 0.33, im.shape[0] - Hb))
    if y0 < 0:
        topo = cv2.GaussianBlur(np.repeat(im[:1], -y0, 0), (0, 0), 25)
        topo = (topo * np.linspace(0.3, 1, -y0)[:, None, None]).astype(np.uint8)
        im = np.concatenate([topo, im], 0)
        y0 = 0
    im = np.ascontiguousarray(im[y0:y0 + Hb, x0:x0 + Wb])
    d = profundidade(im)
    _cache["b_" + nome] = (im, d)
    return im, d


def fundo(nome, t):
    im, d = base(nome)
    D = dur(VIDEOS[nome])
    Hb, Wb = im.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    z = 1.0 + 0.05 * (t / D)
    cx, cy = Wb / 2, Hb / 2
    # câmera passeando devagar: o que está perto (casal) mexe mais que o fundo
    ang = 2 * np.pi * t / 9.0
    amp = 26.0
    sx = (xx - W / 2) / z + cx
    sy = (yy - H / 2) / z + cy
    sx, sy = sx.astype(np.float32), sy.astype(np.float32)
    dd = cv2.remap(d, sx, sy, cv2.INTER_LINEAR)
    mx = sx + amp * np.sin(ang) * (dd - 0.5)
    my = sy + amp * 0.6 * np.cos(ang * 0.8) * (dd - 0.5) - 6 * np.sin(ang * 0.5)
    out = cv2.remap(im, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    # véu: escurece em cima (gancho) e um pouco no geral
    g = np.clip(1 - 0.55 * np.exp(-((yy[:, :1] / H - 0.17) / 0.17) ** 2) - 0.12, 0, 1)
    return (out * g[..., None]).astype(np.uint8)


# ---------------------------------------------------------------- página do livro
def quebra(txt, f, larg):
    linhas, atual = [], ""
    for p in txt.split():
        cand = (atual + " " + p).strip()
        if f.getlength(cand) <= larg or not atual:
            atual = cand
        else:
            linhas.append(atual)
            atual = p
    linhas.append(atual)
    return linhas


def coracao(d, x, y, r, cor, w=4):
    pts = []
    for k in range(60):
        a = 2 * np.pi * k / 59
        px = 16 * np.sin(a) ** 3
        py = -(13 * np.cos(a) - 5 * np.cos(2 * a) - 2 * np.cos(3 * a) - np.cos(4 * a))
        pts.append((x + px * r / 16, y + py * r / 16))
    d.line(pts, fill=cor, width=w, joint="curve")


def seta(d, x0, y0, x1, y1, cor, w=4):
    mx, my = (x0 + x1) / 2 + (y1 - y0) * 0.25, (y0 + y1) / 2 - (x1 - x0) * 0.25
    pts = [((1 - u) ** 2 * x0 + 2 * (1 - u) * u * mx + u ** 2 * x1, (1 - u) ** 2 * y0 + 2 * (1 - u) * u * my + u ** 2 * y1)
           for u in np.linspace(0, 1, 20)]
    d.line(pts, fill=cor, width=w, joint="curve")
    a = np.arctan2(y1 - pts[-3][1], x1 - pts[-3][0])
    for da in (2.6, -2.6):
        d.line([(x1, y1), (x1 + 18 * np.cos(a + da), y1 + 18 * np.sin(a + da))], fill=cor, width=w)


def brilho(d, x, y, cor, w=4):
    for a in (-0.5, 0, 0.5):
        d.line([(x + 14 * np.cos(a), y + 14 * np.sin(a)), (x + 34 * np.cos(a), y + 34 * np.sin(a))], fill=cor, width=w)


def pagina(nome):
    """Camadas da página: fundo do papel + um RGBA por parágrafo (texto, grifo e rabiscos), para entrar um a um."""
    if "p_" + nome in _cache:
        return _cache["p_" + nome]
    v = VIDEOS[nome]
    PW, MARG = 880, 56
    f = fonte("Cormorant.ttf", 45, 500)
    fi = fonte("Cormorant-Italic.ttf", 45, 500)
    lh = 56
    blocos = []
    y = 70
    for i, par in enumerate(v["par"]):
        linhas = quebra(par, f, PW - 2 * MARG - 30)
        blocos.append((y, linhas))
        y += len(linhas) * lh + 26
    PH = y + 70
    PAPEL, TINTA, ROSA, VINHO, RODAPE = TEMAS[v.get("tema", "creme")]
    papel = Image.new("RGBA", (PW, PH), PAPEL + (255,))
    dp = ImageDraw.Draw(papel)
    ff = fonte("Cormorant.ttf", 30, 500)
    dp.text((MARG - 20, PH - 46), f"Capítulo {v['cap']}", font=ff, fill=RODAPE)
    dp.text((PW - MARG + 20, PH - 46), f"{v['pct']}%", font=ff, fill=RODAPE, anchor="ra")
    camadas = []
    rng = np.random.default_rng(len(nome))
    for i, (y0, linhas) in enumerate(blocos):
        lay = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lay)
        grifo = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
        dg = ImageDraw.Draw(grifo)
        par_txt = " ".join(linhas)
        marcados = set()
        for g in v["grifo"]:
            k = par_txt.find(g)
            if k >= 0:
                marcados.update(range(k, k + len(g)))
        pos = 0
        for j, ln in enumerate(linhas):
            yy = y0 + j * lh
            x = MARG + (34 if j == 0 and not ln.startswith("—") else 0)
            # grifo rosa nos trechos marcados (por palavra)
            for pal in ln.split(" "):
                k = par_txt.find(pal, pos)
                marc = k >= 0 and any(c in marcados for c in range(k, k + len(pal)))
                wpal = (fi if marc else f).getlength(pal)
                if marc:
                    dg.rounded_rectangle((x - 4, yy + 8, x + wpal + 4 + f.getlength(" "), yy + lh - 8), 8, fill=ROSA + (120,))
                    dg.line((x - 2, yy + lh - 6, x + wpal + 6, yy + lh - 8), fill=VINHO + (200,), width=3)
                dl.text((x, yy), pal, font=fi if marc else f, fill=TINTA + (255,))
                x += wpal + f.getlength(" ")
                if k >= 0:
                    pos = k + len(pal)
        # rabiscos: coração, setinha ou brilho, alternando lados
        lado = i % 2
        cy = y0 + 22
        if i % 3 == 0:
            coracao(dl, (PW - 34) if lado else 32, cy + 10, 20, VINHO + (255,))
        elif i % 3 == 1:
            brilho(dl, (PW - 70) if lado else 12, cy, VINHO + (255,))
        else:
            seta(dl, (PW - 40) if lado else 26, cy + 50, (PW - 70) if lado else 56, cy + 6, VINHO + (255,))
        if i == len(blocos) - 1:
            coracao(dl, PW / 2, y0 + len(linhas) * lh + 8, 16, VINHO + (255,))
        camadas.append((grifo, lay))
    sombra = Image.new("RGBA", (PW + 80, PH + 80), (0, 0, 0, 0))
    ImageDraw.Draw(sombra).rectangle((40, 50, PW + 40, PH + 50), fill=(0, 0, 0, 120))
    sombra = sombra.filter(ImageFilter.GaussianBlur(20))
    _cache["p_" + nome] = (papel, camadas, sombra)
    return _cache["p_" + nome]


def pov(nome):
    if "pov_" + nome in _cache:
        return _cache["pov_" + nome]
    v = VIDEOS[nome]
    f = fonte("PlayfairDisplay.ttf", 56, 800)
    linhas = quebra(v["pov"], f, W - 120)
    txt = "\n".join(linhas)
    m = _mascara((W, H), (W / 2, 80), txt, f, "ma", 0, "center", 6)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.putalpha(m.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(6)).point(lambda p: min(255, p * 2)))
    out.alpha_composite(sh)
    tx = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    tx.putalpha(m)
    out.alpha_composite(tx)
    bb = m.getbbox()
    _cache["pov_" + nome] = (out, bb[3])
    return _cache["pov_" + nome]


def tela_final():
    if "fim" in _cache:
        return _cache["fim"]
    fim = Image.new("RGB", (W, H), (6, 2, 3))
    y = np.linspace(0, 1, H)[:, None]
    x = np.linspace(-1, 1, W)[None, :]
    g = np.exp(-((x / 0.9) ** 2 + ((y - 0.42) / 0.45) ** 2))
    fim = Image.fromarray(np.clip(np.asarray(fim, np.float32) + g[..., None] * np.array([110, 14, 20]), 0, 255).astype(np.uint8))
    capa = Image.open(os.path.join(AQUI, "out", "capa.png")).convert("RGB")
    lv = livro(capa, 1000)
    fim.paste(lv, ((W - lv.width) // 2, 230), lv)
    texto_ouro(fim, (W / 2, 1420), "EM BREVE", fonte("PlayfairDisplay.ttf", 120, 900), espaco=10)
    filete(fim, W / 2, 1515, meia=220)
    texto(fim, (W / 2, 1580), "Segue a @ pra saber do lançamento", fonte("PlayfairDisplay-Italic.ttf", 44, 500), CREME)
    _cache["fim"] = fim
    return fim


def alfa(lay, a):
    if a >= 0.999:
        return lay
    out = lay.copy()
    out.putalpha(lay.getchannel("A").point(lambda p: int(p * a)))
    return out


def frame(args):
    nome, i = args
    t = i / FPS
    return compoe(nome, t, fundo(nome, t))


def compoe(nome, t, fundo_rgb):
    v = VIDEOS[nome]
    D = dur(v)
    t_fim = D - FINAL
    if t >= t_fim + 0.6:
        img = tela_final()
        if t > D - 0.4:
            img = Image.blend(img, Image.new("RGB", (W, H)), seg(t, D - 0.4, D))
        return np.asarray(img).tobytes()
    img = Image.fromarray(fundo_rgb).convert("RGBA")
    camada_pov, pov_baixo = pov(nome)
    img.alpha_composite(alfa(camada_pov, ease(seg(t, 0.0, 0.4))))
    papel, camadas, sombra = pagina(nome)
    PW, PH = papel.size
    a = ease(seg(t, 0.5, 1.1))
    if a > 0:
        topo = max(pov_baixo + 50, H - PH - 250)
        dy = int(80 * (1 - a))
        x0 = (W - PW) // 2
        pg = papel.copy()
        for k, (grifo, lay) in enumerate(camadas):
            t0 = ENTRA + k * PASSO
            ak = ease(seg(t, t0, t0 + 0.5))
            if ak <= 0:
                break
            # o grifo "passa" da esquerda para a direita
            ag = ease(seg(t, t0 + 0.3, t0 + 1.0))
            if ag > 0:
                gm = grifo.copy()
                corte = int(PW * ag)
                if corte < PW:
                    ImageDraw.Draw(gm).rectangle((corte, 0, PW, PH), fill=(0, 0, 0, 0))
                pg.alpha_composite(gm)
            pg.alpha_composite(alfa(lay, ak))
        img.alpha_composite(alfa(sombra, a), (x0 - 40, topo - 40 + dy))
        img.alpha_composite(alfa(pg, a), (x0, topo + dy))
    img = img.convert("RGB")
    if t > t_fim:
        img = Image.blend(img, tela_final(), ease(seg(t, t_fim, t_fim + 0.6)))
    if t < 0.25:
        img = Image.blend(Image.new("RGB", (W, H)), img, seg(t, 0, 0.25))
    return np.asarray(img).tobytes()


VEL = 0.7  # câmera lenta no vídeo de fundo


def clipe(nome):
    p = os.path.join(AQUI, "assets", "pagina", nome + ".mp4")
    return p if os.path.exists(p) else None


def fundo_video(nome, D):
    """Monta o vídeo de fundo 1080x1920: câmera lenta, recorte em volta do casal e emendas com fusão de 1 s."""
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    src = clipe(nome)
    dclip = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src],
                                 capture_output=True, text=True).stdout)
    L = dclip / VEL - 0.2
    n = max(1, int(np.ceil((D - 1) / (L - 1))))
    fx = VIDEOS[nome].get("vfoco", 0.5)
    fy = VIDEOS[nome].get("vy", 0.5)
    vz = VIDEOS[nome].get("vzoom", 1.3)
    ent, filt = [], []
    for k in range(n):
        ent += ["-i", src]
        filt.append(f"[{k}:v]setpts=(PTS-STARTPTS)/{VEL},scale=w={round(W * vz)}:h={round(H * vz)}:force_original_aspect_ratio=increase,"
                    f"crop={W}:{H}:(iw-{W})*{fx}:(ih-{H})*{fy},setsar=1,trim=0:{L:.3f},setpts=PTS-STARTPTS,"
                    f"fps={FPS},settb=AVTB[v{k}]")
    ult = "v0"
    for k in range(1, n):
        filt.append(f"[{ult}][v{k}]xfade=transition=fade:duration=1:offset={k * (L - 1):.3f}[x{k}]")
        ult = f"x{k}"
    dst = os.path.join(OUT, f"{nome}_fundo.mp4")
    subprocess.run([ff, "-y", "-loglevel", "error", *ent, "-filter_complex", ";".join(filt), "-map", f"[{ult}]",
                    "-t", f"{D:.3f}", "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p", dst],
                   check=True)
    return dst


def quadros(path):
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    p = subprocess.Popen([ff, "-loglevel", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         stdout=subprocess.PIPE)
    n = W * H * 3
    ultimo = None
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        ultimo = np.frombuffer(b, np.uint8).reshape(H, W, 3)
        yield ultimo
    while True:
        yield ultimo


def veu_video():
    if "veu" not in _cache:
        yy = np.linspace(0, 1, H)[:, None]
        g = np.clip(1 - 0.5 * np.exp(-((yy - 0.17) / 0.17) ** 2) - 0.1, 0, 1)
        _cache["veu"] = g[..., None].astype(np.float32)
    return _cache["veu"]


def render(nome):
    v = VIDEOS[nome]
    n = int(round(dur(v) * FPS))
    if not clipe(nome):
        base(nome)
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    mudo = os.path.join(OUT, f"{nome}_mudo.mp4")
    p = subprocess.Popen([ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                          "-tune", "film", "-pix_fmt", "yuv420p", mudo], stdin=subprocess.PIPE)
    if clipe(nome):
        bg = quadros(fundo_video(nome, dur(v)))
        for i in range(n):
            f = (next(bg).astype(np.float32) * veu_video()).astype(np.uint8)
            p.stdin.write(compoe(nome, i / FPS, f))
    else:
        with Pool(4) as pool:
            for b in pool.imap(frame, [(nome, i) for i in range(n)], chunksize=6):
                p.stdin.write(b)
    p.stdin.close()
    p.wait()
    # trilha: a mesma do trechos.py, com a duração deste vídeo
    trechos.VIDEOS["_tmp"] = {"linhas": [""] * 0}
    orig = trechos.dur
    trechos.dur = lambda _v: dur(v)
    try:
        wav = os.path.join(OUT, f"{nome}.wav")
        trechos.grava_wav(wav, trechos.trilha("_tmp"))
    finally:
        trechos.dur = orig
    for sufixo, audio in (("com_trilha", ["-i", wav]), ("para_musica", ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"])):
        dst = os.path.join(OUT, f"{nome}_{sufixo}.mp4")
        filtro = ["-af", "loudnorm=I=-15.5:TP=-1.5:LRA=7"] if sufixo == "com_trilha" else []
        subprocess.run([ff, "-y", "-loglevel", "error", "-i", mudo, *audio, *filtro, "-map", "0:v", "-map", "1:a",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-shortest",
                        "-movflags", "+faststart", dst], check=True)
        print(dst, flush=True)
    os.remove(mudo)
    os.remove(wav)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    ap.add_argument("--so", nargs="*")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    nomes = a.so or list(VIDEOS)
    if a.frame:
        fs = []
        for nome in nomes:
            if clipe(nome):
                bgp = fundo_video(nome, dur(VIDEOS[nome]))
                qs = list(zip(range(int(max(a.frame) * FPS) + 1), quadros(bgp)))
            for t in a.frame:
                if clipe(nome):
                    f = (qs[int(t * FPS)][1].astype(np.float32) * veu_video()).astype(np.uint8)
                    b = compoe(nome, t, f)
                else:
                    b = frame((nome, int(t * FPS)))
                fs.append(Image.frombytes("RGB", (W, H), b).resize((270, 480)))
        cols = len(a.frame)
        folha = Image.new("RGB", (270 * cols, 480 * len(nomes)))
        for k, im in enumerate(fs):
            folha.paste(im, ((k % cols) * 270, (k // cols) * 480))
        folha.save(os.path.join(OUT, "frames.jpg"), quality=88)
        print(os.path.join(OUT, "frames.jpg"))
        return
    for nome in nomes:
        render(nome)


if __name__ == "__main__":
    main()
