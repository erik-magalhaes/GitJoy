#!/usr/bin/env python3
"""Carrossel "COMO VOCÊ REAGE QUANDO PERDE?" (13/nov/2026), 4º da série dos bichinhos (mesmo visual do seu_mes):
6 bichinhos que ELES fizeram no Gemini (folha 3x2; a lhama da 1ª folha saiu porque a pata ficou estranha → hamster;
ampliada 4x com Real-ESRGAN → assets/seu_perde/gemini_perde_x4.jpg), tipo de perdedor, frase e caixa do jogo.

    /usr/bin/python3 seu_perde.py   # out/seu_perde/01..08.png + stories/ + out/seu_perde_previa.jpg
"""
import inspect
import os
import random

from PIL import Image

import seu_mes as SM
import seu_signo as SS
from seu_mes import W, H, E, letra, caixa, selo, papel

ROOT = os.path.dirname(os.path.abspath(__file__))
SM.GEMINI = os.path.join(ROOT, "assets", "seu_perde", "gemini_perde_x4.jpg")
CAIXAS = "../../../"
# o creme desta folha é diferente do da folha do seu_mes: mede na borda da própria folha
import numpy as _np
_f = _np.asarray(Image.open(SM.GEMINI).convert("RGB")).astype(float)
SM.FUNDO_GEMINI = _np.median(_np.concatenate([_f[:8].reshape(-1, 3), _f[-8:].reshape(-1, 3),
                                              _f[:, :8].reshape(-1, 3), _f[:, -8:].reshape(-1, 3)]), 0)  # relativo a hobby-reels/assets/acervo

TIPOS = [  # (tipo, frase, jogo, recorte, fundo pastel)
    ("O QUE VIRA\nA MESA", "FOI DESMASCARADO NO BLEFE\nE QUEM PAGOU FOI A MESA", "Coup", "coup_inquisition",
     (250, 214, 206)),
    ("O QUE PEDE\nREVANCHE", "NEM GUARDOU AS CARTAS\nE JÁ QUER A VINGANÇA", "Flip 7: A Vingança",
     CAIXAS + "gravados-reels/assets/top10/flip_7_a_vinganca", (252, 230, 196)),
    ("O QUE \"DEIXOU\"\nVOCÊ GANHAR", "PERDEU POR UM SASHIMI,\nMAS JURA QUE FOI DE PROPÓSITO", "Sushi Go!",
     CAIXAS + "feed-sua-vez/assets/seu_perde/sushi_go", (246, 222, 210)),
    ("O QUE CULPA\nO DADO", "PERDEU? A CULPA É DO DADO.\nCERTEZA QUE TÁ VICIADO.", "Dice Colony", "dice_colony",
     (220, 236, 214)),
    ("O QUE NEM\nPERCEBEU", "TAVA TÃO FELIZ NA PARTIDA\nQUE NEM VIU QUE PERDEU", "Wandering Towers",
     "wandering_towers", (226, 222, 236)),
    ("O DRAMÁTICO", "PERDEU UMA RODADA\nE JÁ CAIU DURO NO CHÃO", "Por favor, não corte minha cabeça!",
     "por_favor_n_o_corte_minha_cabe_a", (214, 230, 236)),
]

# a folha é 3x2 (a do seu_mes é 4x3): mesma função de recorte, com a grade trocada
_src = inspect.getsource(SM.bicho.__wrapped__)
_src = _src[_src.index("def "):].replace("def bicho(", "def _b(").replace("im.shape[0] / 3", "im.shape[0] / 2") \
    .replace("im.shape[1] / 4", "im.shape[1] / 3").replace("divmod(k, 4)", "divmod(k, 3)")
_ns = dict(SM.__dict__)
exec(_src, _ns)
_cache = {}


def sem_sombra(im):
    """Tira a sombra clara do chão (cinza-bege, pouco saturada) que fica ligada ao lado de fora, só no pé da figura;
    o branco do galo/panda fica protegido pelo contorno escuro."""
    import cv2
    import numpy as np
    a = np.asarray(im).copy()
    rgb = a[..., :3].astype(int)
    claro = (rgb.min(-1) > 175) & ((rgb.max(-1) - rgb.min(-1)) < 45)
    fora = a[..., 3] < 40
    pe = np.zeros(claro.shape, bool)
    pe[int(a.shape[0] * 0.72):] = True
    cand = ((claro & pe) | fora).astype(np.uint8)
    n, lab = cv2.connectedComponents(cand, connectivity=4)
    ids = set(np.unique(lab[fora])) - {0}
    tira = np.isin(lab, list(ids)) & claro & pe
    tira = cv2.dilate(tira.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    tira &= claro | (a[..., 3] < 200)
    a[..., 3][tira] = 0
    out = Image.fromarray(a)
    return out.crop(out.getbbox())


def bichinho(k, h):
    if (k, h) not in _cache:
        b = sem_sombra(_ns["_b"](k, int(h * 1.1)))
        s = h / b.height
        _cache[(k, h)] = b.resize((int(b.width * s), h), Image.LANCZOS)
    return _cache[(k, h)]


def tela_tipo(k):
    tipo, frase, jogo, rec, cor = TIPOS[k]
    img = papel(cor, k + 81)
    duas = "\n" in tipo
    letra(img, tipo, 100 if duas else 110, W / 2, 175 if duas else 160, semente=k)
    b = bichinho(k, 520)
    if b.width > 820:
        b = b.resize((820, int(b.height * 820 / b.width)), Image.LANCZOS)
    img.alpha_composite(b, (int(W / 2 - b.width / 2), int(580 - b.height / 2)))
    letra(img, frase, 58, W / 2, 905, semente=k + 50)
    cx = caixa(rec, 350, 380)
    x0 = int(W - 5 - cx.width)
    img.alpha_composite(cx, (x0, int(H + 15 - cx.height)))
    nome = jogo if len(jogo) < 22 else jogo.replace(", ", ",\n")
    letra(img, "jogo: " + nome, 44, (200 + x0 + 40) / 2, 1205, (80, 70, 70), sw=1, semente=k + 90)
    selo(img, 34, H - 128, 150)
    return img


def tela_capa():
    img = papel((252, 226, 200), 399)
    letra(img, "COMO VOCÊ\nREAGE QUANDO\nPERDE?", 112, W / 2, 640, semente=37)
    letra(img, "(seja sincero)", 60, W / 2, 880, (90, 70, 70), sw=2, semente=38)
    pos = [(190, 220), (540, 200), (890, 220), (190, 1150), (540, 1170), (890, 1150)]
    for k, (x, y) in enumerate(pos):
        cx = bichinho(k, 290)
        if cx.width > 320:
            cx = cx.resize((320, int(cx.height * 320 / cx.width)), Image.LANCZOS)
        cx = cx.rotate(random.Random(k).uniform(-6, 6), expand=True, resample=Image.BICUBIC)
        img.alpha_composite(cx, (int(x - cx.width / 2), int(y - cx.height / 2)))
    selo(img, W / 2 - 75, 935, 150)
    return img


def tela_final():
    img = papel((250, 214, 206), 377)
    letra(img, "E VOCÊ,\nQUAL É?", 110, W / 2, 360, semente=33)
    letra(img, "comenta aqui e marca\naquele amigo que vira a mesa!", 58, W / 2, 620, (90, 70, 70), sw=2,
          semente=34)
    lg = E.logo(330)
    img.alpha_composite(lg, (int(W / 2 - lg.width / 2), 820))
    letra(img, "ALUGA O SEU NA SUA VEZ\nO LINK TÁ NA BIO", 56, W / 2, 1150, semente=35)
    return img


def main():
    d = os.path.join(ROOT, "out", "seu_perde")
    os.makedirs(os.path.join(d, "stories"), exist_ok=True)
    telas = [tela_capa()] + [tela_tipo(k) for k in range(6)] + [tela_final()]
    for k, im in enumerate(telas, 1):
        im.convert("RGB").save(os.path.join(d, f"{k:02d}.png"))
        SS.story_de(im, k == len(telas)).convert("RGB").save(os.path.join(d, "stories", f"story_{k:02d}.png"))
    sh = Image.new("RGB", (4 * 330 + 10, 2 * 420 + 10), (255, 255, 255))
    for k, im in enumerate(telas):
        sh.paste(im.convert("RGB").resize((320, 400), Image.LANCZOS), (10 + (k % 4) * 330, 10 + (k // 4) * 420))
    sh.save(os.path.join(ROOT, "out", "seu_perde_previa.jpg"), quality=90)
    print("ok", len(telas))


if __name__ == "__main__":
    main()
