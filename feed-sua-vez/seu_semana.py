#!/usr/bin/env python3
"""Carrossel "SEU DIA DA SEMANA, SEU JOGO" (14/nov/2026), 5º da série, mas com cara NOVA (pedido dele: "tá tudo
ficando meio igual, bichinho; algo mais viajado, ET, monstros"): monstrinhos e ETs que ELES fizeram no Gemini (folha 4x2,
ampliada 4x → assets/seu_semana/gemini_semana_x4.jpg) como ADESIVOS (borda branca grossa + sombra) num fundo de
ESPAÇO (roxo profundo, estrelas, planetinhas), títulos em Dela Gothic One com sombra 3D colorida e texto em Bricolage.

    /usr/bin/python3 seu_semana.py   # out/seu_semana/01..10.png + stories/ + out/seu_semana_previa.jpg
"""
import inspect
import math
import os
import random
from functools import lru_cache

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import seu_mes as SM
import seu_signo as SS
from seu_mes import E

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
FT = os.path.join(REPO, "comum", "fontes")
W, H = 1080, 1350
SM.GEMINI = os.path.join(ROOT, "assets", "seu_semana", "gemini_semana_x4.jpg")
_f = np.asarray(Image.open(SM.GEMINI).convert("RGB")).astype(float)
SM.FUNDO_GEMINI = np.median(np.concatenate([_f[:8].reshape(-1, 3), _f[-8:].reshape(-1, 3)]), 0)
del _f
ACERVO = os.path.join(REPO, "hobby-reels", "assets", "acervo")

ROXO, LIMA, ROSA, TURQ, LAR, AMA = (124, 77, 255), (196, 244, 70), (255, 92, 168), (40, 214, 214), (255, 140, 40), (255, 214, 60)
DIAS = [  # (dia, frase, jogo, caixa, cor de destaque)
    ("SEGUNDA", "NINGUÉM QUER CONVERSAR:\nJOGO EM SILÊNCIO TOTAL", "The Mind", "the_mind", TURQ),
    ("TERÇA", "AINDA SEM ENERGIA:\nSÓ UMA PARTIDA RAPIDINHA", "Flash 10", "flash_10", LIMA),
    ("QUARTA", "METADE DA SEMANA:\nSUBINDO O MORRO ANDAR POR ANDAR", "Santorini", "santorini", ROXO),
    ("QUINTA", "QUASE SEXTA, OLHO NO RELÓGIO:\nCADA SEGUNDO CONTA", "Take Time", "take_time", ROSA),
    ("SEXTA", "SEXTOU! BAGUNÇA LIBERADA\n(E BURRITO VOANDO)", "Throw Throw Burrito", "throw_throw_burrito", LAR),
    ("SÁBADO", "DIA DE JOGÃO:\nA MASMORRA TE ESPERA", "Clank! Catacombs", "clank_catacombs", TURQ),
    ("DOMINGO", "SOFÁ, PIPOCA E\nHISTÓRIA COM A FAMÍLIA", "Dixit: Disney Edition", "dixit_disney_edition", ROSA),
    ("FERIADO", "FOLGA EXTRA? HORA DE\nPILOTAR JUNTO ATÉ O POUSO", "Sky Team", "../../../gravados-reels/assets/sky/sky_team",
     LIMA),
]

_src = inspect.getsource(SM.bicho.__wrapped__)
_src = _src[_src.index("def "):].replace("def bicho(", "def _b(").replace("im.shape[0] / 3", "im.shape[0] / 2")
_ns = dict(SM.__dict__)
exec(_src, _ns)


def fonte(nome, s, peso=None):
    f = ImageFont.truetype(os.path.join(FT, nome), int(s))
    if peso:
        try:
            f.set_variation_by_axes([peso])
        except Exception:
            pass
    return f


def dela(s):
    return fonte("DelaGothicOne-Regular.ttf", s)


def brico(s, peso=800):
    return fonte("BricolageGrotesque.ttf", s, peso)


@lru_cache(None)
def fundo(semente, h=H):
    rng = np.random.default_rng(semente)
    y = np.linspace(0, 1, h)[:, None, None]
    a, b = np.array([30, 16, 66]), np.array([74, 28, 110])
    img = (a * (1 - y) + b * y) * np.ones((h, W, 1))
    # nebulosas suaves
    for _ in range(3):
        cx, cy, r = rng.uniform(0, W), rng.uniform(0, h), rng.uniform(250, 520)
        cor = np.array([(124, 77, 255), (255, 92, 168), (40, 214, 214)][rng.integers(3)])
        yy, xx = np.mgrid[0:h, 0:W]
        g = np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r))[..., None] * 0.22
        img = img * (1 - g) + cor * g
    img += rng.normal(0, 4, img.shape)  # grão
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(im)
    for _ in range(170):  # estrelas
        x, yv, s = rng.uniform(0, W), rng.uniform(0, h), rng.choice([1, 1, 2, 2, 3])
        d.ellipse((x - s, yv - s, x + s, yv + s), fill=(255, 255, 240, int(rng.uniform(120, 255))))
    for _ in range(6):  # estrelinhas de 4 pontas
        x, yv, s = rng.uniform(40, W - 40), rng.uniform(40, h - 40), rng.uniform(8, 16)
        d.polygon([(x, yv - s), (x + s * .25, yv - s * .25), (x + s, yv), (x + s * .25, yv + s * .25), (x, yv + s),
                   (x - s * .25, yv + s * .25), (x - s, yv), (x - s * .25, yv - s * .25)], fill=(255, 240, 200, 230))
    for _ in range(2):  # planetinhas com anel
        x, yv, r = rng.choice([rng.uniform(45, 85), rng.uniform(995, 1035)]), rng.uniform(330, 700) + (h - 1350) / 2, rng.uniform(18, 26)
        c = tuple(int(v) for v in [(255, 140, 40), (196, 244, 70), (40, 214, 214)][rng.integers(3)])
        d.ellipse((x - r, yv - r, x + r, yv + r), fill=c + (200,))
        d.ellipse((x - r * 1.9, yv - r * .45, x + r * 1.9, yv + r * .45), outline=(255, 240, 200, 170), width=4)
    return im


def adesivo(im, borda=18, sombra=True):
    """Borda branca grossa em volta (como adesivo recortado) + sombra escura deslocada."""
    a = np.asarray(im.getchannel("A"))
    pad = borda + 30
    A = np.pad(a, pad)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * borda + 1, 2 * borda + 1))
    fech = cv2.morphologyEx((A > 60).astype(np.uint8), cv2.MORPH_CLOSE,
                            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41)))
    m = cv2.dilate(fech, k)
    m = cv2.GaussianBlur(m.astype(float) * 255, (0, 0), 1.2).clip(0, 255).astype(np.uint8)
    base = Image.new("RGBA", (A.shape[1], A.shape[0]), (0, 0, 0, 0))
    if sombra:
        s = Image.new("RGBA", base.size, (12, 4, 30, 0))
        s.putalpha(Image.fromarray((m * 0.55).astype(np.uint8)))
        base.alpha_composite(s.filter(ImageFilter.GaussianBlur(6)), (14, 18) if False else (0, 0))
        base = base.transform(base.size, Image.AFFINE, (1, 0, -14, 0, 1, -18))
    branco = Image.new("RGBA", base.size, (255, 252, 244, 0))
    branco.putalpha(Image.fromarray(m))
    base.alpha_composite(branco)
    base.alpha_composite(im, (pad, pad))
    return base.crop(base.getbbox())


_cache = {}


def monstro(k, h):
    if (k, h) not in _cache:
        b = _ns["_b"](k, int(h))
        _cache[(k, h)] = adesivo(b, max(10, int(h * 0.03)))
    return _cache[(k, h)]


def caixa(nome, h, larg):
    im = Image.open(os.path.join(ACERVO, nome + ".png")).convert("RGBA")
    im = im.crop(im.getbbox())
    s = min(h / im.height, larg / im.width)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    return adesivo(im, 12)


def titulo(img, txt, s, cx, cy, cor, sombra=(12, 4, 30), dz=10):
    """Dela Gothic com contorno escuro e sombra 3D em degraus."""
    f = dela(s)
    d = ImageDraw.Draw(img)
    for i in range(dz, 0, -2):
        d.multiline_text((cx + i, cy + i), txt, font=f, fill=sombra, anchor="mm", align="center", spacing=s * 0.12,
                         stroke_width=int(s * .07), stroke_fill=sombra)
    d.multiline_text((cx, cy), txt, font=f, fill=cor, anchor="mm", align="center", spacing=s * 0.12,
                     stroke_width=int(s * .07), stroke_fill=sombra)


def texto(img, txt, s, cx, cy, cor=(255, 250, 240), peso=800):
    d = ImageDraw.Draw(img)
    d.multiline_text((cx, cy), txt, font=brico(s, peso), fill=cor, anchor="mm", align="center", spacing=s * 0.3,
                     stroke_width=3, stroke_fill=(20, 8, 44))


def logo(img, x, y, w=150):
    img.alpha_composite(E.logo(w), (int(x), int(y)))


def cola(img, im, cx, cy, rot=0):
    if rot:
        im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def tela_dia(k):
    dia, frase, jogo, rec, cor = DIAS[k]
    img = fundo(k + 11).copy()
    titulo(img, dia, 132, W / 2, 165, cor)
    m = monstro(k, 480)
    if m.width > 860:
        m = m.resize((860, int(m.height * 860 / m.width)), Image.LANCZOS)
    cola(img, m, W / 2, 545, rot=random.Random(k).uniform(-4, 4))
    texto(img, frase, 52, W / 2, 875)
    cx = caixa(rec, 290, 330)
    cola(img, cx, W - 30 - cx.width / 2, H - 30 - cx.height / 2, rot=-5)
    x0 = W - 30 - cx.width
    nome = jogo if len(jogo) < 16 else jogo.replace(": ", ":\n").replace(" Burrito", "\nBurrito")
    texto(img, "JOGO:", 38, (40 + x0) / 2, 1110, cor, 800)
    texto(img, nome, 46, (40 + x0) / 2, 1175 if "\n" in nome else 1160)
    logo(img, 36, H - 140, 140)
    return img


def tela_capa():
    img = fundo(5).copy()
    titulo(img, "SEU DIA\nDA SEMANA,", 104, W / 2, 560, (255, 250, 240))
    titulo(img, "SEU JOGO", 120, W / 2, 790, LIMA)
    texto(img, "(qual é o seu?)", 46, W / 2, 893, (255, 250, 240), 600)
    pos = [(160, 200), (420, 175), (680, 185), (930, 205), (150, 1150), (420, 1170), (680, 1160), (930, 1140)]
    for k, (x, y) in enumerate(pos):
        m = monstro(k, 230)
        if m.width > 270:
            m = m.resize((270, int(m.height * 270 / m.width)), Image.LANCZOS)
        cola(img, m, x, y, rot=random.Random(k + 3).uniform(-8, 8))
    logo(img, W / 2 - 70, 960, 140)
    return img


def tela_final():
    img = fundo(77).copy()
    titulo(img, "E AÍ, QUAL É\nO SEU DIA\nDE JOGAR?", 96, W / 2, 380, AMA)
    texto(img, "comenta aqui e marca quem\njoga com você nesse dia!", 46, W / 2, 680, (255, 250, 240), 600)
    lg = E.logo(320)
    img.alpha_composite(lg, (int(W / 2 - lg.width / 2), 820))
    texto(img, "ALUGA O SEU NA SUA VEZ\nO LINK TÁ NA BIO", 50, W / 2, 1160)
    return img


def story_de(tela, k, ultimo=False):
    st = fundo(k + 200, 1920).copy()
    if ultimo:
        st.alpha_composite(tela.crop((0, 0, W, 1090)), (0, 200))
        texto(st, "aluga aqui:", 56, W / 2, 1345, (255, 250, 240))
        d = ImageDraw.Draw(st)
        d.line([(W / 2, 1395), (W / 2, 1470)], fill=(255, 250, 240), width=10)
        d.polygon([(W / 2 - 30, 1455), (W / 2 + 30, 1455), (W / 2, 1500)], fill=(255, 250, 240))
    else:
        st.alpha_composite(tela, (0, 285))
    return st


def main():
    d = os.path.join(ROOT, "out", "seu_semana")
    os.makedirs(os.path.join(d, "stories"), exist_ok=True)
    telas = [tela_capa()] + [tela_dia(k) for k in range(8)] + [tela_final()]
    for k, im in enumerate(telas, 1):
        im.convert("RGB").save(os.path.join(d, f"{k:02d}.png"))
        story_de(im, k, k == len(telas)).convert("RGB").save(os.path.join(d, "stories", f"story_{k:02d}.png"))
    sh = Image.new("RGB", (5 * 330 + 10, 2 * 420 + 10), (255, 255, 255))
    for k, im in enumerate(telas):
        sh.paste(im.convert("RGB").resize((320, 400), Image.LANCZOS), (10 + (k % 5) * 330, 10 + (k // 5) * 420))
    sh.save(os.path.join(ROOT, "out", "seu_semana_previa.jpg"), quality=90)
    print("ok", len(telas))


if __name__ == "__main__":
    main()
