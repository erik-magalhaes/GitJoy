#!/usr/bin/env python3
"""Carrossel 1080x1350 "Avaliando os jogos que jogamos essa semana" (14/out/2026). Pedido do Erik: "só o jogo na mesa
e a escrita" (rejeitou caderno, trilha de pontos e medidor de conceitos_semana.py). Eles não têm fotos das partidas,
então cada tela é uma MONTAGEM: mesa de madeira gerada em numpy + fotos OFICIAIS dos componentes (Galápagos: Splendor
Duel, Hitster Lado B, Ticket to Ride Legacy; PaperGames: Trio) pousadas com sombra; por cima, só o texto (nome, nota e
a frase dele). Notas e frases são as que o Erik mandou; nada inventado.
Fotos de produto em fundo branco: o branco ligado à borda vira transparente e as sombras do estúdio entram em
"multiplicar" sobre a madeira (escurecem a mesa como sombra de verdade).

    python3 semana.py      # out/semana/01..06.png (+ out/semana_folha.jpg)
"""
import os
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
from estilo import MARROM, AMARELO, BRANCO, titulo, texto, pilula, logo, cola, lilita, fig  # noqa: E402

A = os.path.join(ROOT, "assets", "semana", "orig")
OUT = os.path.join(ROOT, "out", "semana")
W, H = 1080, 1350
TTR_ABERTO = os.path.join(REPO, "byebye-reels", "assets", "ttr_lendas_do_oeste_aberto.png")

JOGOS = [  # (nome na tela, nota, frase do Erik, no acervo?)
    ("TICKET TO RIDE LEGACY", 10, "Melhora muito o Ticket original. E depois que a campanha acaba, ainda dá pra "
                                  "continuar jogando!", False),
    ("SPLENDOR DUEL", 8, "Ótimo pra duas pessoas e ótimo pra ter briga. Minha esposa ficou bem brava ontem... mas eu "
                         "ganhei!", True),
    ("HITSTER LADO B", 10, "Muito divertido, ótimo pra galera. Todo mundo gosta, ninguém se arrepende de jogar.", True),
    ("TRIO", 9, "Ótimo jogo, mas depende de quem tá jogando: se a galera não pega rápido, fica mais longo e "
                "chatinho.", False),
]


@lru_cache(None)
def mesa(semente=3):
    """Tampo de madeira visto de cima (tábuas na vertical, veios suaves, luz quente no meio). Limpo, sem ruído."""
    rng = np.random.default_rng(semente)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    larg = 216
    tab = (xx // larg).astype(int)
    off = rng.uniform(0, 100, 12)
    var = rng.uniform(0.9, 1.07, 12)
    veio = np.sin((yy * 0.010 + np.sin(yy * 0.0035 + off[tab]) * 3.2 + (xx % larg) * 0.07) * 2.0)
    veio2 = np.sin(yy * 0.045 + (xx % larg) * 0.27 + off[tab])
    lum = var[tab] * (0.93 + 0.055 * veio + 0.02 * veio2)
    base = np.array([168, 112, 70], np.float32)
    img = base[None, None] * lum[..., None]
    img[(xx % larg) < 3] *= 0.6
    yv = np.linspace(-1, 1, H)[:, None]
    xv = np.linspace(-1, 1, W)[None, :]
    img *= (1.06 - 0.38 * (xv ** 2 + (yv * 0.9) ** 2) ** 1.1)[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


@lru_cache(None)
def produto(nome):
    """Foto de produto → (RGBA do objeto, mapa de sombra 0–1 para multiplicar na mesa)."""
    im = Image.open(os.path.join(A, nome) if not os.path.isabs(nome) else nome)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        cantos = [im.getpixel(c) for c in ((0, 0), (im.width - 1, 0), (0, im.height - 1), (im.width - 1, im.height - 1))]
        if any(c[3] < 30 for c in cantos):  # já tem transparência oficial
            return im, None
    rgb = np.asarray(im.convert("RGB")).astype(np.float32)
    claro = (rgb.min(axis=2) > 236) & (rgb.max(axis=2) - rgb.min(axis=2) < 14)
    lab, _ = ndimage.label(claro)
    borda = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    fundo = np.isin(lab, list(borda))
    # sombra do estúdio = tudo do fundo que não é branco puro, ligado ao fundo
    cinza = rgb.mean(axis=2) / 255.0
    quase = (rgb.min(axis=2) > 150) & (rgb.max(axis=2) - rgb.min(axis=2) < 22)
    lab2, _ = ndimage.label(quase | fundo)
    ids = set(np.unique(lab2[fundo])) - {0}
    fundo2 = np.isin(lab2, list(ids))
    obj = ~fundo2
    obj = ndimage.binary_opening(obj, iterations=1)
    alfa = ndimage.gaussian_filter(obj.astype(np.float32), 0.8)
    out = np.dstack([rgb, alfa * 255]).astype(np.uint8)
    sombra = np.where(fundo2, np.clip(cinza / 0.985, 0, 1) ** 1.4, 1.0)
    return Image.fromarray(out, "RGBA"), sombra.astype(np.float32)


def pousa(img, nome, cx, cy, larg, rot=0.0, sombra_extra=True):
    """Coloca o objeto na mesa: sombra do estúdio multiplicada + sombra suave própria + o objeto."""
    obj, sh = produto(nome)
    bb = obj.getchannel("A").getbbox()
    if sh is not None:  # inclui a sombra do estúdio no recorte
        ys, xs = np.where(sh < 0.97)
        if len(xs):
            bb = (min(bb[0], xs.min()), min(bb[1], ys.min()), max(bb[2], xs.max() + 1), max(bb[3], ys.max() + 1))
    obj = obj.crop(bb)
    s = larg / obj.width
    obj = obj.resize((max(2, round(obj.width * s)), max(2, round(obj.height * s))), Image.LANCZOS)
    if sh is not None:
        shi = Image.fromarray((sh[bb[1]:bb[3], bb[0]:bb[2]] * 255).astype(np.uint8), "L").resize(obj.size,
                                                                                            Image.LANCZOS)
    if abs(rot) > 0.05:
        obj = obj.rotate(rot, expand=True, resample=Image.BICUBIC)
        if sh is not None:
            shi = shi.rotate(rot, expand=True, resample=Image.BICUBIC, fillcolor=255)
    x0, y0 = int(cx - obj.width / 2), int(cy - obj.height / 2)
    if sombra_extra:
        a = obj.getchannel("A").filter(ImageFilter.GaussianBlur(max(6, obj.width / 60)))
        a = a.point(lambda v: int(v * (0.38 if sh is None else 0.18)))
        so = Image.new("RGBA", obj.size, (25, 12, 4, 0))
        so.putalpha(a)
        img.alpha_composite(so, (x0 + int(obj.width / 70), y0 + int(obj.width / 45)))
    if sh is not None:
        reg = img.crop((x0, y0, x0 + obj.width, y0 + obj.height))
        arr = np.asarray(reg).astype(np.float32)
        m = np.asarray(shi).astype(np.float32)[..., None] / 255
        arr[..., :3] *= m
        img.paste(Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA"), (x0, y0))
    img.alpha_composite(obj, (x0, y0)) if x0 >= 0 and y0 >= 0 else img.paste(obj, (x0, y0), obj)


def escrita(img, nome, nota, frase):
    """Só a escrita: nome em cima, nota grande, frase embaixo. Branco com sombra escura (cara de post do TikTok)."""
    def sombreado(im):
        sh = Image.new("RGBA", im.size, (20, 10, 4, 0))
        sh.putalpha(im.getchannel("A").filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * 0.85)))
        out = Image.new("RGBA", (im.width + 30, im.height + 30), (0, 0, 0, 0))
        out.alpha_composite(sh, (15, 21))
        out.alpha_composite(sh, (15, 17))
        out.alpha_composite(im, (15, 15))
        return out
    cola(img, sombreado(texto(nome, 62, BRANCO, 900, larg_max=900)), W / 2, 110)
    n = Image.new("RGBA", (560, 200), (0, 0, 0, 0))
    d = ImageDraw.Draw(n)
    d.text((280, 100), f"{nota}/10", font=lilita(190), fill=AMARELO, anchor="mm")
    cola(img, sombreado(n.crop(n.getbbox())), W / 2, 245)
    cola(img, sombreado(texto(frase, 42, BRANCO, 800, larg_max=900)), W / 2, 1185)


def marca(img):
    cola(img, logo(150), W - 100, H - 62, 0)


def cena_ttr():
    img = mesa(1).copy()
    pousa(img, TTR_ABERTO, W / 2 + 10, 730, 880)
    return img


def cena_splendor():
    img = mesa(2).copy()
    pousa(img, "SPL201_02.png", W / 2 - 70, 735, 680, 0)
    pousa(img, "SPL201_OCC.png", 905, 930, 250, -6)
    return img


def cena_hitster():
    img = mesa(3).copy()
    pousa(img, "HIT003.8.png", 360, 760, 640, 8)
    pousa(img, "HIT003.9.png", 640, 620, 560, -10)
    pousa(img, "HIT003.3.png", 820, 860, 330, 6)
    return img


def cena_trio():
    img = mesa(4).copy()
    # mesa do Trio: cartas viradas no meio e um trio de 7 revelado
    for k in range(9):
        pousa(img, "trio_cartas_verso.png", 190 + (k % 3) * 150, 520 + (k // 3) * 215, 125, (-3, 2, -1, 4, -2, 1, 3, -4, 2)[k])
    for k in range(3):
        pousa(img, "trio_cartas_frente7.png", 690 + k * 70, 640 + k * 26, 175, -10 + k * 9)
    for k, c in enumerate(("1", "4", "9", "12")):
        pousa(img, f"trio_cartas_frente{c}.png", 600 + k * 80, 940, 150, -14 + k * 9)
    pousa(img, "trio_3D_frente.png", 905, 470, 230, 5)
    return img


def capa():
    img = mesa(5).copy()
    pousa(img, "SPL201_OCC.png", 300, 820, 330, -9)
    pousa(img, "HIT003.3.png", 790, 830, 330, 8)
    pousa(img, "TTR401_3D-Box-01_OCC.png", 560, 1080, 470, -3)
    pousa(img, "trio_3D_frente.png", 560, 720, 250, 2)
    return img


def tela_capa():
    img = capa()
    cola(img, titulo("AVALIANDO OS JOGOS\nQUE JOGAMOS\nESSA SEMANA", 104, BRANCO, larg_max=980), W / 2, 260, -2)
    cola(img, pilula("NOTA SINCERA DE 0 A 10", 34, AMARELO, MARROM, pad=(26, 10)), W / 2, 500, 2)
    cola(img, logo(170), 110, 1270, -4)
    return img


def tela_final():
    img = mesa(6).copy()
    cola(img, titulo("E VOCÊ,\nQUE NOTA DÁ?", 120, BRANCO, larg_max=960), W / 2, 230, -2)
    cola(img, pilula("COMENTA AQUI!", 56, AMARELO, MARROM, pad=(36, 14), fonte_titulo=True), W / 2, 450, 2)
    pousa(img, "SPL201_OCC.png", 360, 760, 320, -6)
    pousa(img, "HIT003.3.png", 720, 760, 320, 6)
    cola(img, texto("Splendor Duel e Hitster Lado B estão no acervo:", 38, BRANCO, 800, larg_max=900), W / 2, 1050)
    cola(img, pilula("ALUGUE PELO LINK NA BIO", 48, BRANCO, MARROM, pad=(34, 14), fonte_titulo=True), W / 2, 1135)
    cola(img, logo(210), W / 2, 1265)
    return img


def telas():
    cenas = [cena_ttr(), cena_splendor(), cena_hitster(), cena_trio()]
    out = [tela_capa()]
    for img, (nome, nota, frase, _) in zip(cenas, JOGOS):
        escrita(img, nome, nota, frase)
        marca(img)
        out.append(img)
    return out + [tela_final()]


def main():
    os.makedirs(OUT, exist_ok=True)
    ts = telas()
    for k, im in enumerate(ts):
        im.convert("RGB").save(os.path.join(OUT, f"{k + 1:02d}.png"))
    folha = Image.new("RGB", (3 * 405 + 40, 2 * 506 + 30), (255, 255, 255))
    for k, im in enumerate(ts):
        folha.paste(im.convert("RGB").resize((405, 506), Image.LANCZOS), (10 + (k % 3) * 415, 10 + (k // 3) * 516))
    folha.save(os.path.join(ROOT, "out", "semana_folha.jpg"), quality=90)
    print("ok", len(ts))


if __name__ == "__main__":
    main()
