#!/usr/bin/env python3
"""Kit da dinâmica "Kaizen do Café" (Coffee Rush) para o time de melhoria contínua do Erik (28/out/2026):
kit.html (visão geral, roteiro, regras, ficha de medição, em A4 retrato) + a3.html (A3 adaptado, A4 paisagem)
→ out/kaizen_do_cafe.pdf (as 5 páginas) e out/pagina_N.png para conferir.

    python3 gerar_pdf.py
"""
import os

import pymupdf
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out")


def main():
    os.makedirs(OUT, exist_ok=True)
    partes = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        for nome, paisagem in (("kit", False), ("a3", True)):
            pg.goto("file://" + os.path.join(ROOT, nome + ".html"))
            pg.wait_for_timeout(300)
            destino = os.path.join(OUT, nome + ".pdf")
            pg.pdf(path=destino, format="A4", landscape=paisagem, print_background=True,
                   margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
            partes.append(destino)
        b.close()
    doc = pymupdf.open()
    for f in partes:
        doc.insert_pdf(pymupdf.open(f))
    final = os.path.join(OUT, "kaizen_do_cafe.pdf")
    doc.save(final)
    for k, page in enumerate(doc, 1):
        page.get_pixmap(dpi=80).save(os.path.join(OUT, f"pagina_{k}.png"))
    print(final, len(doc), "páginas")


if __name__ == "__main__":
    main()
