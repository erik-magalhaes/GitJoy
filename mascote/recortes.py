#!/usr/bin/env python3
"""Recorta os mascotes (capivara = Jéssica, coruja = Erik) das folhas 3D do Gemini (12/nov/2026).
Folhas em assets/folhas/*.jpg (1024 px) → ampliadas 4x com Real-ESRGAN (*_x4.png, wonderland-reels/ampliar_tab.py).
Cada folha é cortada em linhas/colunas pelas faixas vazias de fundo creme e cada quadro passa pelo rembg
(isnet-general-use). Saída: assets/poses/<nome>.png (fundo transparente) + out/poses_verde.jpg (conferência).

    /usr/bin/python3 recortes.py
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
FOL = os.path.join(ROOT, "assets", "folhas")
POS = os.path.join(ROOT, "assets", "poses")
OUT = os.path.join(ROOT, "out")

FOLHAS = {  # folha: (linhas de nomes, da esquerda pra direita)
    "capivara_1": [["capivara_acenando", "capivara_apontando", "capivara_aponta_baixo"],
                   ["capivara_comemorando", "capivara_entregando", "capivara_joinha"]],
    "capivara_2": [["capivara_patinete", "capivara_rindo", "capivara_surpresa"],
                   ["capivara_pufe", "capivara_chorando", "capivara_pilha"]],
    "coruja_1": [["coruja_acenando", "coruja_apontando", "coruja_aponta_baixo"],
                 ["coruja_explicando", "coruja_ideia", "coruja_joinha"]],
    "coruja_2": [["coruja_pensando", "coruja_lupa", "coruja_comemorando"],
                 ["coruja_chocada", "coruja_facepalm", "coruja_chorando"]],
    "dupla_ref": [["dupla_referencia"]],
    "dupla_cenas": [["dupla_acenando", "dupla_explicando", "dupla_vitoria"],
                    ["dupla_highfive", "dupla_aponta_baixo", "dupla_abraco"]],
    # 13/nov: a capivara virou uma SALSICHA (dachshund) de cachecol rosa = a Jéssica
    "salsicha_ref": [["dupla2_referencia"]],
    "salsicha_1": [["salsicha_acenando", "salsicha_apontando", "salsicha_aponta_baixo"],
                   ["salsicha_comemorando", "salsicha_entregando", "salsicha_joinha"]],
    "salsicha_2": [["salsicha_patinete", "salsicha_rindo", "salsicha_surpresa"],
                   ["salsicha_pufe", "salsicha_chorando", "salsicha_pilha"]],
    "dupla_natal": [["natal_acenando", "natal_presente", "natal_pisca_pisca"],
                    ["natal_amigo_secreto", "natal_brinde", "natal_dormindo"]],
}


def cortes(ocup, n):
    """Divide em n faixas cortando no meio das n-1 maiores faixas vazias (ocup = bool por linha/coluna)."""
    vaz, i, L = [], 0, len(ocup)
    while i < L:
        if not ocup[i]:
            j = i
            while j < L and not ocup[j]:
                j += 1
            if i > 0 and j < L:
                vaz.append((j - i, (i + j) // 2))
            i = j
        else:
            i += 1
    meios = sorted(m for _, m in sorted(vaz, reverse=True)[:n - 1])
    return [0] + meios + [L]


def main():
    from rembg import new_session, remove
    ses = new_session("isnet-general-use")
    os.makedirs(POS, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    feitos = []
    import sys
    so = sys.argv[1:]
    for folha, linhas in FOLHAS.items():
        if (so and folha not in so) or not os.path.exists(os.path.join(FOL, folha + "_x4.png")):
            continue
        im = Image.open(os.path.join(FOL, folha + "_x4.png")).convert("RGB")
        a = np.asarray(im).astype(float)
        fundo = np.median(np.r_[a[:20].reshape(-1, 3), a[-20:].reshape(-1, 3)], 0)
        ocupado = np.sqrt(((a - fundo) ** 2).sum(-1)) > 40
        ys = cortes(ocupado.sum(1) > 6, len(linhas))
        for r, nomes in enumerate(linhas):
            faixa = ocupado[ys[r]:ys[r + 1]]
            xs = cortes(faixa.sum(0) > 6, len(nomes))
            for c, nome in enumerate(nomes):
                cel = im.crop((xs[c], ys[r], xs[c + 1], ys[r + 1]))
                out = remove(cel, session=ses)
                al = np.asarray(out.getchannel("A"))
                out = out.crop(Image.fromarray(np.where(al > 40, 255, 0).astype(np.uint8)).getbbox())
                out.save(os.path.join(POS, nome + ".png"))
                feitos.append((nome, out))
                print(nome, out.size, flush=True)
    # folha de conferência no verde
    cols, tw, th = 6, 300, 340
    rows = (len(feitos) + cols - 1) // cols
    sh = Image.new("RGB", (cols * tw, rows * th), (40, 200, 60))
    d = ImageDraw.Draw(sh)
    f = ImageFont.load_default()
    for k, (nome, im) in enumerate(feitos):
        t = im.copy()
        t.thumbnail((tw - 20, th - 40))
        x, y = (k % cols) * tw, (k // cols) * th
        sh.paste(t, (x + (tw - t.width) // 2, y + 5), t)
        d.text((x + 6, y + th - 22), nome, fill=(0, 0, 0), font=f)
    sh.save(os.path.join(OUT, "poses_verde.jpg"), quality=88)


if __name__ == "__main__":
    main()
