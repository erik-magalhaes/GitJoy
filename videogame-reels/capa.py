#!/usr/bin/env python3
"""Capa do Reels "5 jogos que te fazem sentir dentro do videogame" (27/nov/2026). 1080x1920, o que importa dentro de
y 285–1635 (área que aparece na grade do perfil). Duas opções:

  A  ELE em tela cheia (quadro sorrindo e olhando pra câmera, boné limpo, luz de rosto do edita.py), "TÁ ESPERANDO O
     GTA 6?" no alto e, embaixo, "5 JOGOS DE TABULEIRO QUE PARECEM VIDEOGAME" com o leque das 5 caixas.
  B  Só gráfico, tela de videogame: as 5 capas digitais à esquerda → as 5 caixas à direita, título no alto.

    /usr/bin/python3 capa.py      # out/capa_A.png, out/capa_B.png, out/capa_opcoes.jpg
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import edita as V  # noqa: E402

E = V.E
W, H = 1080, 1920
OUT = V.OUT
NOITE = (18, 34, 58)


def quadro_dele(nome="144733", t=10.5):
    raw = subprocess.run([V.FF, "-v", "error", "-ss", str(t), "-i", os.path.join(V.BR, nome + ".mp4"), "-frames:v", "1",
                          "-vf", "scale=1080:1920,hqdn3d=3:3:4:4,smartblur=lr=1.2:ls=0.3:lt=-4,eq=contrast=1.05:"
                                 "saturation=1.06,colorbalance=rs=0.02:bs=-0.02:rm=0.025:bm=-0.025,unsharp=5:5:0.45",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    im = Image.frombytes("RGB", (W, H), raw)
    import json
    d = json.load(open(os.path.join(OUT, f"rosto_{nome}.json")))
    v = [xy for ts, xy in d.items() if abs(float(ts) - t) < 1.0]
    fx, fy = np.median(np.array(v), 0)
    im = V.limpa_bone(im, fx, fy)
    im = V.limpa_blusa(im, fx, fy)
    # rosto centralizado e mais perto (z 1,25), um pouco acima do meio
    z = 1.18
    w, h = W / z, H / z
    x0 = min(max(fx - 540 / z, 0), W - w)
    y0 = min(max(fy - 880 / z, 0), H - h)
    im = im.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h))
    return im.convert("RGBA")


def degrade(img, y0, y1, cor, a0=0, a1=235):
    g = Image.new("L", (1, H), 0)
    for y in range(H):
        k = min(max((y - y0) / max(1, y1 - y0), 0), 1)
        g.putpixel((0, y), int(a0 + (a1 - a0) * k))
    m = g.resize((W, H))
    img.alpha_composite(Image.composite(Image.new("RGBA", (W, H), cor + (255,)), Image.new("RGBA", (W, H), (0, 0, 0, 0)), m))


def capa_a(nome="144733", t=10.5):
    img = quadro_dele(nome, t)
    # escurece o alto (título) e o pé (caixas)
    top = Image.new("L", (1, H))
    for y in range(H):
        a = 0
        if y < 620:
            a = int(215 * (1 - y / 620) ** 1.2)
        if y > 1180:
            a = int(240 * min((y - 1180) / 300, 1))
        top.putpixel((0, y), a)
    img.alpha_composite(Image.composite(Image.new("RGBA", (W, H), NOITE + (255,)), Image.new("RGBA", (W, H), (0, 0, 0, 0)),
                                        top.resize((W, H))))
    t1 = E.titulo("TÁ ESPERANDO\nO GTA 6?", 120, cor=E.AMARELO, larg_max=980)
    img.alpha_composite(t1, ((W - t1.width) // 2, 300))
    lq = E.leque([V.JOGOS[k][0] for k in ("bad", "res", "ww", "heat", "dbd")], 250, passo=0.56)
    if lq.width > W - 60:
        lq = lq.resize((W - 60, int(lq.height * (W - 60) / lq.width)), Image.LANCZOS)
    t2 = E.titulo("5 JOGOS DE TABULEIRO\nQUE PARECEM VIDEOGAME", 70, cor=(255, 255, 255), larg_max=1000)
    yb = 1635 - t2.height
    img.alpha_composite(t2, ((W - t2.width) // 2, yb))
    img.alpha_composite(lq, ((W - lq.width) // 2, yb - lq.height + 5))
    cg = V.capa("gta", 230)
    img.alpha_composite(cg, (W - cg.width - 40, 300 + t1.height - 40))
    lg = E.logo(170)
    img.alpha_composite(lg, (W - lg.width - 30, 60))
    return img


def capa_b():
    img = Image.new("RGBA", (W, H), NOITE + (255,))
    d = ImageDraw.Draw(img)
    for x in range(0, W, 30):
        d.line((x, 0, x, H), fill=(28, 50, 80))
    for y in range(0, H, 30):
        d.line((0, y, W, y), fill=(28, 50, 80))
    t1 = E.titulo("SE VOCÊ JOGA...", 92, cor=(110, 226, 240), larg_max=980)
    img.alpha_composite(t1, ((W - t1.width) // 2, 300))
    pares = [("gta", "bad"), ("among", "res"), ("aoe", "ww"), ("forza", "heat"), ("dbd", "dbd")]
    y = 300 + t1.height - 4
    passo = 196
    for i, (dg, tb) in enumerate(pares):
        cy = y + i * passo + passo // 2
        c = V.capa(dg, 186).rotate(-6 if i % 2 else 6, expand=True, resample=Image.BICUBIC)
        img.alpha_composite(c, (170 - c.width // 2, int(cy - c.height / 2)))
        cx = E.jogo(V.JOGOS[tb][0], 182, larg=215)
        img.alpha_composite(cx, (W - 200 - cx.width // 2, int(cy - cx.height / 2)))
        # seta de pixel
        p = 9
        mapa = ["000010000", "000011000", "111111100", "111111110", "111111100", "000011000", "000010000"]
        x0, y0 = W // 2 - 4 * p, cy - 3 * p
        for j, l in enumerate(mapa):
            for k, ch in enumerate(l):
                if ch == "1":
                    d.rectangle((x0 + k * p + 4, y0 + j * p + 4, x0 + (k + 1) * p + 3, y0 + (j + 1) * p + 3), fill=(0, 0, 0))
                    d.rectangle((x0 + k * p, y0 + j * p, x0 + (k + 1) * p - 1, y0 + (j + 1) * p - 1), fill=E.AMARELO)
    t2 = E.titulo("...VAI CURTIR ESSES\nJOGOS DE TABULEIRO!", 74, cor=E.AMARELO, larg_max=1000)
    img.alpha_composite(t2, ((W - t2.width) // 2, 1635 - t2.height))
    lg = E.logo(170)
    img.alpha_composite(lg, (W - lg.width - 30, 60))
    return img


OPCOES = [("144818", 233.0), ("144733", 13.3), ("144818", 245.0), ("144818", 203.5)]


def main():
    if "--frames" in sys.argv:
        ims = [capa_a(n, t) for n, t in OPCOES]
        f = Image.new("RGB", (4 * 540 + 90, 960 + 70), (255, 255, 255))
        dd = ImageDraw.Draw(f)
        for i, im in enumerate(ims):
            im.convert("RGB").save(os.path.join(OUT, f"capa_A{i + 1}.png"))
            f.paste(im.convert("RGB").resize((540, 960)), (i * 570, 70))
            dd.text((i * 570 + 250, 15), str(i + 1), fill=(0, 0, 0), font=E.lilita(44))
        f.save(os.path.join(OUT, "capa_A_opcoes.jpg"), quality=90)
        print("ok")
        return
    a, b = capa_a(), capa_b()
    a.convert("RGB").save(os.path.join(OUT, "capa_A.png"))
    b.convert("RGB").save(os.path.join(OUT, "capa_B.png"))
    f = Image.new("RGB", (2 * 540 + 30, 960 + 60), (255, 255, 255))
    dd = ImageDraw.Draw(f)
    for i, im in enumerate((a, b)):
        f.paste(im.convert("RGB").resize((540, 960)), (i * 570, 60))
        dd.rectangle((i * 570, 60 + 142, i * 570 + 539, 60 + 817), outline=(255, 0, 0), width=2)  # área da grade
        dd.text((i * 570 + 250, 20), "AB"[i], fill=(0, 0, 0), font=E.lilita(36))
    f.save(os.path.join(OUT, "capa_opcoes.jpg"), quality=90)
    print("ok")


if __name__ == "__main__":
    main()
