#!/usr/bin/env python3
"""Vídeos BookTok/Reels com trechos de "Três Segredos e um CEO" (1080x1920, 30 fps, ~22 s, sem narração).

Visual da capa: a foto das costas em zoom lento, escurecida, brasas subindo; gancho em cima nos primeiros
segundos; as falas entram uma a uma no meio (a anterior apaga um pouco); fecha com o livro e "em breve".
Trilha: piano + pad em lá menor e um coração batendo baixinho, sintetizados (sem direitos autorais).

    python3 trechos.py            → out/trechos/<nome>_{com_trilha,para_musica}.mp4
    python3 trechos.py --frame 1 5 12 [--so reencontro]   → out/trechos/frames.jpg
"""
import argparse
import os
import subprocess
import sys
import wave
from multiprocessing import Pool

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from divulgacao import CREME, VERMELHO, _mascara, filete, fonte, livro, texto, texto_ouro  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(AQUI, "out", "trechos")
W, H, FPS = 1080, 1920, 30
SR = 44100
GANCHO, LINHA, FINAL = 3.0, 3.2, 4.2

VIDEOS = {
    "reencontro": {
        "gancho": "POV: o homem que sumiu\ndepois de uma noite\nvirou o seu chefe",
        "zoom": (1.0, 1.12), "foco": (0.5, 0.55), "tom": (1.0, 0.95, 1.0), "espelho": False, "anim": "bokeh",
        "linhas": [
            "— Helena. A gente\njá se conhece?",
            "O coração dela batia\ntão forte que doía.",
            "— Não, senhor —\nmentiu Helena.",
            "— Engraçado. Tenho a sensação\nde que já vi esse cabelo antes.",
            "— Não é nada comum,\nsenhorita Duarte.",
        ],
    },
    "conselho": {
        "gancho": "Quando os seus trigêmeos\ninvadem a reunião do chefe…\nque é o pai deles",
        "zoom": (1.0, 1.15), "foco": (0.5, 0.6), "tom": (0.62, 0.7, 0.85), "espelho": False, "contraste": 1.25, "brilho": -0.18, "anim": "poeira",
        "linhas": [
            "Bento parou na frente\nde Rafael Montenegro.",
            "— Você é o chefe exigente?",
            "Os dois franziram a testa\nao mesmo tempo.",
            "— Mamãe.\nEle tem o meu olho.",
            "— Minha sala. Agora.",
        ],
    },
    "dois_segundos": {
        "gancho": "Era pra ser um beijo\nde mentira.\nSó pra foto.",
        "zoom": (1.0, 1.2), "foco": (0.3, 0.5), "tom": (1.05, 0.9, 0.85), "espelho": False, "anim": "bokeh",
        "linhas": [
            "— É só encostar.\nDois segundos.",
            "Um.\nDois.",
            "E no três,\nela não se afastou.",
            "No quatro, os dedos dele\nestavam no cabelo dela.",
            "— Se você me beijar assim de novo,\neu esqueço o contrato inteiro.",
            "— Esquece.",
        ],
    },
    "bilhete": {
        "gancho": "Ele deixou um bilhete.\nEla nunca viu.\nCinco anos depois…",
        "zoom": (1.05, 1.3), "foco": (0.62, 0.5), "tom": (1.05, 0.95, 0.8), "espelho": False, "anim": "poeira",
        "linhas": [
            "— Eu deixei um bilhete.",
            "— Eu não vi\nbilhete nenhum.",
            "— Eu chutei a máscara\ne saí pelo elevador de serviço\ncom o sapato na mão.",
            "Cinco anos.\nTrês Natais.",
            "Tudo por causa\nde um chute.",
        ],
    },
    "elevador": {
        "gancho": "Presa no elevador\ncom o chefe…\nque é o pai dos seus filhos",
        "zoom": (1.0, 1.15), "foco": (0.55, 0.5), "tom": (0.9, 1.0, 1.05), "espelho": False, "anim": "andar",
        "linhas": [
            "Ela sentia a respiração dele\nno pescoço.",
            "— Se você der mais um passo,\neu não respondo por mim.",
            "— Então não responde.",
            "— Cinco anos. E eu ainda\nlembro do gosto da sua boca.",
            "— Aperta o botão.\nAntes que eu esqueça\nquem eu sou.",
        ],
    },
    "cozinha": {
        "gancho": "1h30 da manhã.\nEle, sem camisa,\natrás de mim no fogão.",
        "zoom": (1.0, 1.1), "foco": (0.5, 0.5), "tom": (1.05, 0.9, 0.95), "espelho": False, "anim": "chuva",
        "linhas": [
            "O calor do corpo dele\nchegou antes da mão.",
            "A mão dele parou na cintura dela.\nSó parou.",
            "E foi pior do que\nse tivesse continuado.",
            "— Me pede pra sair, Helena.\nUma palavra só.",
            "Ela não pediu.",
        ],
    },
    "regra_quebrada": {
        "gancho": "Regra número um:\nnada de beijos\nfora das fotos.",
        "zoom": (1.0, 1.15), "foco": (0.40, 0.62), "tom": (1.25, 0.6, 0.55), "espelho": False, "cinza": 0.55, "contraste": 1.25, "brilho": -0.1, "anim": "brasas",
        "linhas": [
            "— Então eu estou quebrando\na regra número um.\nDe propósito.",
            "— Tira — disse ela,\npuxando a gravata dele.",
            "— Você tem certeza?\n— Eu tô sem ar\ndesde o primeiro café.",
            "O vestido vermelho escorregou\nde um ombro.",
            "— Devagar. Dessa vez eu quero\nlembrar de tudo.",
            "A chave girou duas vezes.",
        ],
    },
    "provar": {
        "gancho": "Ela é confeiteira.\nEle, o chefe que ela\njurou odiar.",
        "zoom": (1.0, 1.2), "foco": (0.72, 0.6), "tom": (1.05, 0.88, 0.85), "espelho": False, "anim": "bokeh",
        "linhas": [
            "— Me deixa provar.",
            "— O bolo é da vitrine.\nNinguém prova o bolo da vitrine.",
            "— Eu não falei do bolo.",
            "Ela passou a ponta do dedo\nno chantilly.",
            "Ele segurou o pulso dela.\nProvou. Sem pressa nenhuma.",
            "— Eu ainda não provei\no que eu vim provar.",
        ],
    },
    "encharcado": {
        "gancho": "Ele chegou encharcado.\nE ela pediu pra ele\ntirar a camisa.",
        "zoom": (1.0, 1.15), "foco": (0.5, 0.5), "tom": (1.1, 0.85, 1.0), "espelho": False, "anim": "chuva",
        "linhas": [
            "— Você está encharcado.",
            "— Tira isso.\nVai pegar um resfriado.",
            "— Isso é preocupação\nou é uma desculpa?\n— É um pedido.",
            "Ele desabotoou a camisa devagar,\nsem tirar os olhos dela.",
            "— Você está me molhando inteira.\n— Quer que eu pare?",
            "— Apaga a luz da frente.",
        ],
    },
}


def dur(v):
    return GANCHO + LINHA * len(v["linhas"]) + FINAL


def seg(t, a, b):
    return min(1.0, max(0.0, (t - a) / (b - a)))


def ease(u):
    return u * u * (3 - 2 * u)


# ---------------------------------------------------------------- camadas pré-renderizadas
_cache = {}


def foto_base(nome):
    k = "foto_" + nome
    if k not in _cache:
        v = VIDEOS[nome]
        im = Image.open(os.path.join(AQUI, "assets", "videos", nome + ".jpg")).convert("RGB")
        _cache[k] = grade(im, v)
    return _cache[k]


def grade(im, v):
    """Cor de cada vídeo: tom multiplicado, contraste, opcionalmente dessatura; mantém a foto reconhecível."""
    a = np.asarray(im).astype(np.float32) / 255
    if v.get("cinza"):
        g = a.mean(2, keepdims=True)
        a = a * (1 - v["cinza"]) + g * v["cinza"]
    a = np.clip((a - 0.5) * v.get("contraste", 1.1) + 0.5 + v.get("brilho", -0.05), 0, 1)
    a = a * np.array(v["tom"])
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    if v["espelho"]:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return im


def _velho_foto_base(nome):
    k = "velho_" + nome
    if k not in _cache:
        v = VIDEOS[nome]
        im = Image.open(os.path.join(AQUI, "assets", "foto_costas.jpg")).convert("RGB")
        a = np.asarray(im).astype(np.float32) / 255
        lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
        jan = np.clip((lum - 0.55) / 0.35, 0, 1)
        lum = lum * (1 - 0.5 * jan)
        pts = np.array([0, 0.08, 0.25, 0.5, 1.0])
        cores = np.array([[4, 2, 3], [34, 6, 10], [120, 34, 26], [214, 120, 72], [255, 222, 170]], np.float32) / 255
        l = np.clip(lum * 1.2, 0, 1)
        out = np.stack([np.interp(l, pts, cores[:, c]) for c in range(3)], -1)
        if v.get("cinza"):
            g = out.mean(2, keepdims=True)
            out = out * (1 - v["cinza"]) + g * v["cinza"]
        out = out * np.array(v["tom"])
        im = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))
        if v["espelho"]:
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
        _cache[k] = im
    return _cache[k]


def escurece():
    """Véu: o meio da tela (onde ficam as falas) mais escuro."""
    if "veu" not in _cache:
        y = np.linspace(0, 1, H)[:, None]
        x = np.linspace(-1, 1, W)[None, :]
        meio = np.exp(-((y - 0.55) / 0.22) ** 2) * 0.55
        base = np.clip((y - 0.45) / 0.35, 0, 1) * 0.6
        vin = np.clip(np.sqrt(x ** 2 * 0.5 + (y - 0.4) ** 2) - 0.45, 0, 1) * 0.8
        a = np.clip(meio + base + vin, 0, 0.92)
        _cache["veu"] = Image.fromarray((np.repeat(a[..., None], 1, 2)[..., 0] * 255).astype(np.uint8), "L")
    return _cache["veu"]


def camada(xy, txt, f, cor, entrelinha=18, espaco=0, sombra=12, faixa=0):
    """Texto em RGBA com sombra suave (e, se faixa>0, um véu escuro largo atrás pra ler sobre a janela clara)."""
    m = _mascara((W, H), xy, txt, f, "mm", espaco, "center", entrelinha)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if faixa:
        bb = m.getbbox()
        veu = Image.new("L", (W, H))
        ImageDraw.Draw(veu).rectangle((0, bb[1] - faixa, W, bb[3] + faixa), fill=170)
        out.putalpha(veu.filter(ImageFilter.GaussianBlur(faixa * 0.8)))
    if sombra:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sh.putalpha(m.filter(ImageFilter.GaussianBlur(sombra)).point(lambda v: min(255, v * 2)))
        out.alpha_composite(sh)
    tx = Image.new("RGBA", (W, H), tuple(cor) + (0,))
    tx.putalpha(m)
    out.alpha_composite(tx)
    return out


def camadas(nome):
    if nome in _cache:
        return _cache[nome]
    v = VIDEOS[nome]
    c = {}
    fg = fonte("PlayfairDisplay.ttf", 76, 900)
    c["gancho"] = camada((W / 2, 360), v["gancho"], fg, CREME, entrelinha=14, faixa=90)
    fl = fonte("PlayfairDisplay-Italic.ttf", 70, 600)
    c["linhas"] = []
    for i, s in enumerate(v["linhas"]):
        cor = VERMELHO if i == len(v["linhas"]) - 1 else CREME
        c["linhas"].append(camada((W / 2, 1050), s, fl, cor, entrelinha=26))
    c["assina"] = camada((W / 2, 1560), "TRÊS SEGREDOS E UM CEO · ESTELA MANCINI",
                         fonte("Cinzel.ttf", 30, 700), (240, 200, 120), espaco=4, sombra=6)
    # tela final
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
    c["fim"] = fim
    _cache[nome] = c
    return c


def brasas(img, t, semente):
    rng = np.random.default_rng(semente)
    n = 70
    px = rng.uniform(0, W, n)
    vel = rng.uniform(30, 90, n)
    fase = rng.uniform(0, H, n)
    r = rng.uniform(1.5, 4.5, n)
    osc = rng.uniform(0, 6.28, n)
    lay = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(lay)
    for i in range(n):
        y = (H + 60) - ((fase[i] + vel[i] * t) % (H + 120))
        x = px[i] + 18 * np.sin(t * 0.9 + osc[i])
        brilho = 0.55 + 0.45 * np.sin(t * 3 + osc[i])
        cor = (255, int(110 + 50 * brilho), 60)
        d.ellipse((x - r[i], y - r[i], x + r[i], y + r[i]), fill=tuple(int(c * brilho) for c in cor))
    lay = Image.blend(lay.filter(ImageFilter.GaussianBlur(3)), lay, 0.5)
    return Image.fromarray(np.clip(np.asarray(img, np.int16) + np.asarray(lay, np.int16) * 0.8, 0, 255).astype(np.uint8))


def fundo(nome, t):
    v = VIDEOS[nome]
    D = dur(v)
    u = ease(seg(t, 0, D - FINAL))
    z = v["zoom"][0] + (v["zoom"][1] - v["zoom"][0]) * u
    f = foto_base(nome)
    # quadro 9:16 dentro da foto (que é ~2:3), com zoom em torno do foco
    ch = f.height / z
    cw = ch * W / H
    cx = v["foco"][0] * f.width
    cy = v["foco"][1] * f.height + (u - 0.5) * 0.06 * f.height
    x0 = min(max(0, cx - cw / 2), f.width - cw)
    y0 = min(max(0, cy - ch / 2), f.height - ch)
    img = f.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
    img = Image.composite(Image.new("RGB", (W, H)), img, escurece())
    anim = v.get("anim", "brasas")
    if anim == "bokeh":
        return bokeh(img, t, 3)
    if anim == "chuva":
        return chuva(img, t)
    if anim == "poeira":
        return poeira(img, t)
    if anim == "andar":
        return andar(poeira(img, t, n=30), t)
    return brasas(img, t, 5)


def soma(img, lay, k=0.8):
    return Image.fromarray(np.clip(np.asarray(img, np.int16) + np.asarray(lay, np.int16) * k, 0, 255).astype(np.uint8))


def bokeh(img, t, semente):
    """Luzes da cidade fora de foco, flutuando devagar."""
    rng = np.random.default_rng(semente)
    lay = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(lay)
    for _ in range(26):
        x0, y0 = rng.uniform(0, W), rng.uniform(0, H)
        r = rng.uniform(25, 85)
        vx, vy = rng.uniform(-12, 12), rng.uniform(-20, -6)
        cor = [(255, 170, 90), (255, 120, 120), (255, 210, 150), (200, 160, 255)][rng.integers(0, 4)]
        br = 0.25 + 0.2 * np.sin(t * rng.uniform(0.6, 1.4) + rng.uniform(0, 6))
        x, y = x0 + vx * t, (y0 + vy * t) % (H + 200) - 100
        d.ellipse((x - r, y - r, x + r, y + r), fill=tuple(int(c * br) for c in cor))
    return soma(img, lay.filter(ImageFilter.GaussianBlur(10)), 0.9)


def chuva(img, t):
    """Gotas escorrendo no vidro + riscos de chuva."""
    rng = np.random.default_rng(9)
    lay = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(lay)
    for _ in range(140):
        x, v, f = rng.uniform(0, W), rng.uniform(900, 1500), rng.uniform(0, H)
        y = (f + v * t) % (H + 100) - 50
        d.line((x, y, x - 6, y - 45), fill=(120, 120, 140), width=2)
    for _ in range(18):
        x, v, f = rng.uniform(0, W), rng.uniform(25, 70), rng.uniform(0, H)
        y = (f + v * t) % (H + 80) - 40
        r = rng.uniform(5, 10)
        d.ellipse((x - r, y - r * 1.3, x + r, y + r * 1.3), fill=(150, 140, 150))
        d.line((x, y - r, x, y - r - rng.uniform(40, 120)), fill=(70, 65, 75), width=3)
    return soma(img, lay.filter(ImageFilter.GaussianBlur(1.2)), 0.6)


def poeira(img, t, n=60):
    """Partículas douradas finas, quase paradas."""
    rng = np.random.default_rng(4)
    lay = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(lay)
    for _ in range(n):
        x0, y0 = rng.uniform(0, W), rng.uniform(0, H)
        x = x0 + 25 * np.sin(t * 0.4 + rng.uniform(0, 6))
        y = (y0 - 12 * t) % H
        r = rng.uniform(1, 3)
        br = 0.5 + 0.5 * np.sin(t * 2 + rng.uniform(0, 6))
        d.ellipse((x - r, y - r, x + r, y + r), fill=(int(255 * br), int(210 * br), int(140 * br)))
    return soma(img, lay.filter(ImageFilter.GaussianBlur(1.5)), 0.9)


def andar(img, t):
    """Painel de elevador: o andar desce de 40 até 35 e trava entre 35 e 34, piscando PARADO."""
    if t < GANCHO - 0.2:
        return img
    a = ease(seg(t, GANCHO - 0.2, GANCHO + 0.4))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx, cy = W / 2, 330
    d.rounded_rectangle((cx - 170, cy - 110, cx + 170, cy + 110), 18, fill=(10, 10, 12, int(230 * a)),
                        outline=(120, 110, 100, int(255 * a)), width=4)
    andar_n = max(35, 40 - int((t - GANCHO) / 0.6))
    parado = t > GANCHO + 3.2
    txt = "35" if parado else str(andar_n)
    cor = (255, 70, 60) if parado else (255, 180, 80)
    f = fonte("PlayfairDisplay.ttf", 130, 900)
    d.text((cx + 25, cy - 5), txt, font=f, fill=cor + (int(255 * a),), anchor="mm")
    d.polygon([(cx - 120, cy - 25), (cx - 80, cy - 25), (cx - 100, cy + 15)], fill=cor + (int(255 * a),))
    if parado and int(t * 2) % 2 == 0:
        d.text((cx, cy + 150), "PARADO", font=fonte("Cinzel.ttf", 44, 900), fill=(255, 70, 60, int(255 * a)), anchor="mm")
    base = img.convert("RGBA")
    base.alpha_composite(lay)
    return base.convert("RGB")


def frame(args):
    nome, i = args
    t = i / FPS
    v = VIDEOS[nome]
    c = camadas(nome)
    D = dur(v)
    t_fim = D - FINAL
    if t >= t_fim:
        img = c["fim"].copy()
        img = brasas(img, t, 7)
        a = ease(seg(t, t_fim, t_fim + 0.6))
        if a < 1:
            base = fundo(nome, t)
            img = Image.blend(base, img, a)
        if t > D - 0.4:
            img = Image.blend(img, Image.new("RGB", (W, H)), seg(t, D - 0.4, D))
        return np.asarray(img).tobytes()
    img = fundo(nome, t).convert("RGBA")
    # entrada geral
    if t < 0.4:
        pass
    # gancho: nos primeiros segundos, depois sobe e some
    ag = ease(seg(t, 0.0, 0.25)) * (1 - ease(seg(t, GANCHO - 0.4, GANCHO + 0.2)))
    if ag > 0:
        img.alpha_composite(alfa(c["gancho"], ag))
    for k, lay in enumerate(c["linhas"]):
        t0 = GANCHO + k * LINHA
        if t < t0:
            break
        a = ease(seg(t, t0, t0 + 0.5))
        a *= 1 - ease(seg(t, t0 + LINHA - 0.35, t0 + LINHA))  if k < len(c["linhas"]) - 1 else 1
        dy = int(30 * (1 - ease(seg(t, t0, t0 + 0.6))))
        if a > 0:
            img.alpha_composite(alfa(lay, a), (0, dy))
    aa = ease(seg(t, GANCHO, GANCHO + 0.8))
    img.alpha_composite(alfa(c["assina"], aa * 0.9))
    img = img.convert("RGB")
    if t < 0.3:
        img = Image.blend(Image.new("RGB", (W, H)), img, seg(t, 0, 0.3))
    return np.asarray(img).tobytes()


def alfa(lay, a):
    if a >= 0.999:
        return lay
    out = lay.copy()
    out.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    return out


# ---------------------------------------------------------------- som
def nota(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def trilha(nome):
    v = VIDEOS[nome]
    D = dur(v)
    N = int(D * SR)
    t = np.arange(N) / SR
    out = np.zeros(N)
    # pad: Am - F - C - G, 4 s por acorde
    acordes = [[57, 60, 64], [53, 57, 60], [48, 55, 64], [55, 59, 62]]
    for k in range(int(D // 4) + 1):
        a = acordes[k % 4]
        s0 = int(k * 4 * SR)
        L = min(int(4.6 * SR), N - s0)
        if L <= 0:
            break
        tt = np.arange(L) / SR
        envl = np.minimum(1, tt / 1.2) * np.minimum(1, (4.6 - tt) / 1.0)
        for n in a:
            f = nota(n)
            out[s0:s0 + L] += 0.05 * envl * (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * f * 2.003 * tt))
    # piano: arpejo lento, uma nota a cada 0,8 s
    mel = [69, 72, 76, 72, 65, 69, 72, 69, 64, 67, 72, 67, 67, 71, 74, 71]
    for k in range(int(D / 0.8)):
        n = mel[k % len(mel)] + (12 if (k // 16) % 2 else 0) * 0
        s0 = int(k * 0.8 * SR)
        L = min(int(2.4 * SR), N - s0)
        tt = np.arange(L) / SR
        f = nota(n)
        tom = np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * 2 * f * tt) * np.exp(-tt * 3) + 0.15 * np.sin(2 * np.pi * 3 * f * tt) * np.exp(-tt * 5)
        out[s0:s0 + L] += 0.12 * tom * np.exp(-tt * 1.8) * np.minimum(1, tt / 0.005)
    # coração: tum-tum a cada 1,1 s, mais forte no fim das falas
    for k in range(int((D - FINAL) / 1.1)):
        for dt, g in ((0, 1.0), (0.18, 0.7)):
            s0 = int((k * 1.1 + dt) * SR)
            L = min(int(0.25 * SR), N - s0)
            tt = np.arange(L) / SR
            out[s0:s0 + L] += 0.22 * g * np.sin(2 * np.pi * (55 - 20 * tt) * tt) * np.exp(-tt * 18)
    # "boom" grave na tela final
    s0 = int((D - FINAL) * SR)
    L = min(int(2.5 * SR), N - s0)
    tt = np.arange(L) / SR
    out[s0:s0 + L] += 0.5 * np.sin(2 * np.pi * (48 - 12 * tt) * tt) * np.exp(-tt * 2.2)
    # fade
    out *= np.minimum(1, t / 0.5) * np.minimum(1, (D - t) / 1.2)
    return out / max(1e-9, np.abs(out).max()) * 0.8


def grava_wav(path, x):
    x = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(np.repeat(x[:, None], 2, 1).reshape(-1).tobytes() if False else x.tobytes())


# ---------------------------------------------------------------- render
def render(nome):
    v = VIDEOS[nome]
    n = int(round(dur(v) * FPS))
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    mudo = os.path.join(OUT, f"{nome}_mudo.mp4")
    p = subprocess.Popen([ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                          "-tune", "film", "-pix_fmt", "yuv420p", mudo], stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for b in pool.imap(frame, [(nome, i) for i in range(n)], chunksize=8):
            p.stdin.write(b)
    p.stdin.close()
    p.wait()
    wav = os.path.join(OUT, f"{nome}.wav")
    grava_wav(wav, trilha(nome))
    for sufixo, audio in (("com_trilha", ["-i", wav]), ("para_musica", ["-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=stereo"])):
        dst = os.path.join(OUT, f"{nome}_{sufixo}.mp4")
        filtro = ["-af", "loudnorm=I=-15.5:TP=-1.5:LRA=7"] if sufixo == "com_trilha" else []
        subprocess.run([ff, "-y", "-loglevel", "error", "-i", mudo, *audio, *filtro, "-map", "0:v", "-map", "1:a",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-shortest",
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
    nomes = a.so if a.so else list(VIDEOS)
    if a.frame:
        fs = []
        for nome in nomes:
            for t in a.frame:
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
