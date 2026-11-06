#!/usr/bin/env python3
"""Capa do Reels "TOP 10 ÀS CEGAS" da JÉSSICA (6/nov), igual à 7ª versão do Erik (`capa_top10_erik.py --simples`):
quadro do vídeo dela em tela cheia, "TOP 10 / ÀS / CEGAS" amarelo em 3 linhas à esquerda, logo no canto de cima à direita.
Quadros tirados dos brutos (`brutos/nov01b/`), o mais nítido numa janela de ±0,4 s → `assets/capa/jess_top10_<v><t>.jpg`
(a = 151657, b = 151838). Gera as 4 opções lado a lado (`out/capa_top10_jessica_opcoes.jpg`) para eles escolherem.

    /usr/bin/python3 capa_top10_jessica.py            # opções
    /usr/bin/python3 capa_top10_jessica.py b13.20     # só a escolhida → out/capa_top10_jessica.png
"""
import os
import sys

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "assinatura-reels"))
import estilo as E  # noqa: E402

W, H = 1080, 1920
OUT = os.path.join(ROOT, "out")
CAPA = os.path.join(ROOT, "assets", "capa")
OPCOES = ["b13.20", "b14.70", "b07.00", "b16.00"]  # do 151657 (a) a carta ficava em cima do título


def capa(q):
    img = Image.open(os.path.join(CAPA, f"jess_top10_{q}.jpg")).convert("RGB").resize((W, H), Image.LANCZOS)
    img = img.convert("RGBA")
    for txt, y in (("TOP 10", 1265), ("ÀS", 1400), ("CEGAS", 1535)):
        t = E.titulo(txt, 132, (255, 199, 31))
        img.alpha_composite(t, (30, int(y - t.height / 2)))
    lg = E.logo(210)
    img.alpha_composite(lg, (W - lg.width - 34, 40))
    return img.convert("RGB")


def main():
    os.makedirs(OUT, exist_ok=True)
    if len(sys.argv) > 1:
        capa(sys.argv[1]).save(os.path.join(OUT, "capa_top10_jessica.png"))
        print("ok")
        return
    w, h = 360, 640
    sh = Image.new("RGB", (4 * w + 50, h + 70), (240, 236, 228))
    d = ImageDraw.Draw(sh)
    for k, q in enumerate(OPCOES):
        im = capa(q)
        im.save(os.path.join(OUT, f"capa_top10_jessica_{k + 1}.png"))
        x, y = 10 + k * (w + 10), 10
        d.text((x + w / 2, y + 25), f"OPÇÃO {k + 1}", font=E.lilita(40), fill=(63, 36, 18), anchor="mm")
        sh.paste(im.resize((w, h), Image.LANCZOS), (x, y + 50))
    sh.save(os.path.join(OUT, "capa_top10_jessica_opcoes.jpg"), quality=90)
    print("ok")


if __name__ == "__main__":
    main()
